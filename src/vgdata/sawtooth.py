"""Portfolio-value simulation under the two distribution-crediting conventions.

This is the pivotal uncertainty in brief S9.1. StockTrak computes volatility on
*portfolio value*, and a bond ETF's price drops on its ex-date by the amount of
the distribution. What happens next decides the Sharpe:

  credit='ex_date'   cash lands the same day the price drops. The two cancel,
                     account value is smooth, sigma stays near the quantisation
                     floor and the Sharpe is enormous.
  credit='pay_date'  cash lands 2+ business days later. Account value dips by
                     the full distribution and recovers. Over a 40-day window
                     with two cycles, four outlier days enter a series whose
                     other days move ~1 bp.

The brief could not size this gap without waiting for an October observation.
It can be sized now, from history, as a two-branch answer.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS = 252


@dataclass
class AccountPath:
    value: pd.Series
    returns: pd.Series
    shares: pd.Series
    residual_cash: float
    credit: str

    def sharpe(self, rf_annual: float = 0.0) -> float:
        r = self.returns.dropna()
        if r.empty or r.std() == 0:
            return np.nan
        return (r.mean() - rf_annual / TRADING_DAYS) / r.std() * np.sqrt(TRADING_DAYS)

    def stats(self, rf_annual: float = 0.0) -> dict:
        r = self.returns.dropna()
        return {
            "sharpe": self.sharpe(rf_annual),
            "mean_bp": r.mean() * 1e4,
            "sd_bp": r.std() * 1e4,
            "ann_vol_pct": r.std() * np.sqrt(TRADING_DAYS) * 100,
            "total_return_pct": (self.value.iloc[-1] / self.value.iloc[0] - 1) * 100,
            "worst_day_bp": r.min() * 1e4,
            "n_days": len(r),
        }


def simulate_account(
    close: pd.DataFrame,
    dividends: pd.DataFrame,
    weights: pd.Series,
    capital: float = 250_000.0,
    credit: str = "pay_date",
    pay_lag_bdays: int = 2,
    commission: float = 10.0,
    half_spread_bp: pd.Series | None = None,
    fractional: bool = False,
) -> AccountPath:
    """Walk an account forward day by day, exactly as the platform would mark it.

    Integer shares by default (StockTrak forbids fractional), cash earns 0%,
    and distributions are never reinvested (brief S10).
    """
    w = weights[weights > 0]
    px = close[w.index].dropna(how="all")
    div = dividends.reindex(columns=w.index, fill_value=0.0).reindex(px.index, fill_value=0.0).fillna(0.0)

    p0 = px.iloc[0]
    # Buying crosses the spread; StockTrak fills at real-time bid/ask.
    if half_spread_bp is not None:
        p0 = p0 * (1 + half_spread_bp.reindex(w.index).fillna(0.0) / 1e4)

    target = w * capital
    shares = target / p0 if fractional else np.floor(target / p0)
    cash = capital - float((shares * p0).sum()) - commission * len(w)

    # Map each ex-date to the day the cash actually arrives.
    if credit == "ex_date":
        credit_on = {d: d for d in px.index}
    elif credit == "pay_date":
        credit_on = {}
        for d in px.index:
            pay = d + pd.tseries.offsets.BDay(pay_lag_bdays)
            later = px.index[px.index >= pay]
            credit_on[d] = later[0] if len(later) else px.index[-1]
    else:
        raise ValueError("credit must be 'ex_date' or 'pay_date'")

    pending: dict[pd.Timestamp, float] = {}
    for d in px.index:
        amt = float((div.loc[d] * shares).sum())
        if amt:
            tgt = credit_on[d]
            pending[tgt] = pending.get(tgt, 0.0) + amt

    values, cash_t = [], cash
    for d in px.index:
        cash_t += pending.get(d, 0.0)
        values.append(float((shares * px.loc[d]).sum()) + cash_t)

    value = pd.Series(values, index=px.index, name="account_value")
    return AccountPath(value, value.pct_change(), shares, cash, credit)


def compare_branches(close, dividends, weights, **kw) -> pd.DataFrame:
    """Both crediting conventions side by side. The gap is what October settles."""
    rows = {}
    for credit in ("ex_date", "pay_date"):
        rows[credit] = simulate_account(close, dividends, weights, credit=credit, **kw).stats()
    df = pd.DataFrame(rows).T
    df.index.name = "credit_convention"
    return df


def window(panel: dict, start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Slice the close and dividend frames to a date window."""
    c = panel["close"].loc[start:end]
    d = panel["dividends"].reindex(c.index).fillna(0.0)
    return c, d
