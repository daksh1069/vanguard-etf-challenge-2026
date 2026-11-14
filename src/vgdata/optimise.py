"""Covariance estimation and constrained maximum-Sharpe optimisation.

Two departures from the script in brief S11.2, both deliberate:

1. **The optimisation is solved exactly.** The brief calls `scipy.minimize` on
   the Sharpe ratio from a single equal-weight start. That objective is not
   concave, so the result is a local optimum with no certificate. Maximising a
   ratio subject to linear constraints is a classic Schaible transform: it
   becomes a convex QP in y = w/(w'mu), solved to global optimality by cvxpy.

2. **The covariance is built from simulated account returns, not fund total
   returns.** A fund's total return credits its distribution on the ex-date. If
   StockTrak credits on the pay date instead, the account's variance is several
   times larger (Phase 3). Estimating the covariance from per-fund simulated
   account paths carries that structure into the optimiser rather than leaving
   it as a caveat.
"""
from __future__ import annotations

import cvxpy as cp
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

from .sawtooth import TRADING_DAYS, simulate_account


def branch_returns(panel: dict, tickers, credit: str = "pay_date",
                   start: str | None = None) -> pd.DataFrame:
    """Per-fund account return series under a crediting convention.

    Each column is the daily return of an account holding only that fund, marked
    the way the platform would mark it. Under 'ex_date' this is the ordinary
    total return; under 'pay_date' it carries the distribution whipsaw.
    """
    close = panel["close"][list(tickers)]
    if start:
        close = close.loc[start:]
    close = close.dropna()
    div = panel["dividends"].reindex(close.index)[list(tickers)].fillna(0.0)

    out = {}
    for t in close.columns:
        path = simulate_account(close[[t]], div[[t]], pd.Series({t: 1.0}),
                                capital=1_000_000, credit=credit, commission=0.0)
        out[t] = path.returns
    return pd.DataFrame(out).dropna()


def common_window(returns: pd.DataFrame, tickers) -> pd.DataFrame:
    """Largest rectangular sample covering every requested ticker."""
    sub = returns[[t for t in tickers if t in returns.columns]]
    return sub.dropna()


def covariance(returns: pd.DataFrame, method: str = "corr_shrink") -> pd.DataFrame:
    """Annualised covariance.

    `corr_shrink` (default) shrinks the *correlation* matrix toward a constant-
    correlation target and keeps the sample variances on the diagonal.

    **Do not use `ledoit_wolf` on a universe with heterogeneous volatility.**
    Ledoit-Wolf shrinks the covariance toward mu*I, where mu is the average
    variance across all assets. In a universe holding both T-bill funds and
    equity sector funds that average is set by the equities, so the shrinkage
    inflates the very assets this competition rewards: measured on our 85-asset
    panel it raises VBIL's annualised volatility from 0.285% to 3.69%, a factor
    of 13, and VGUS by 11.5. A max-Sharpe solve on that matrix cannot see the
    short end at all. The brief's script (S11.2) has this bug.

    Shrinking the correlation instead leaves each asset's own variance intact
    and only stabilises the off-diagonal structure, which is the part that is
    actually poorly estimated.
    """
    X = returns.to_numpy()
    if method == "sample":
        S = np.cov(X, rowvar=False)
    elif method == "ledoit_wolf":
        S = LedoitWolf().fit(X).covariance_
    elif method == "corr_shrink":
        sd = X.std(axis=0, ddof=1)
        sd_safe = np.where(sd > 0, sd, 1.0)
        Z = (X - X.mean(axis=0)) / sd_safe
        C = np.corrcoef(Z, rowvar=False)
        C = np.nan_to_num(C, nan=0.0)
        np.fill_diagonal(C, 1.0)
        # Data-driven intensity: Ledoit-Wolf on standardised returns, where every
        # variance is 1 by construction so the scale problem cannot arise.
        delta = float(LedoitWolf().fit(Z).shrinkage_)
        n = C.shape[0]
        off = (C.sum() - n) / (n * (n - 1)) if n > 1 else 0.0
        target = np.full_like(C, off)
        np.fill_diagonal(target, 1.0)
        C_s = (1 - delta) * C + delta * target
        S = np.outer(sd, sd) * C_s
    else:
        raise ValueError(f"unknown covariance method {method!r}")
    return pd.DataFrame(S * TRADING_DAYS, index=returns.columns, columns=returns.columns)


def expected_returns(master: pd.DataFrame, tickers, erp: float = 0.045,
                     inflation: float = 0.023) -> pd.Series:
    """Annual expected return per fund, net of expense ratio.

    Bonds carry their SEC yield, which assumes rates follow a random walk: over a
    40-day window the expected price change from a rate move is zero, though its
    variance is not, and the covariance handles that. TIPS funds publish a REAL
    yield, so expected inflation is added back to make them comparable.
    Equities get the ERP assumption, which is an input, not a measurement.
    """
    mu = {}
    for t in tickers:
        row = master.loc[t]
        is_bond = str(row["asset_class"]).startswith("Bond")
        if is_bond and pd.notna(row["sec_yield"]):
            r = row["sec_yield"] + (inflation if row["yield_is_real"] else 0.0)
        else:
            r = erp
        mu[t] = r - (row["expense_ratio"] if pd.notna(row["expense_ratio"]) else 0.0)
    return pd.Series(mu)


def max_sharpe(mu: pd.Series, S: pd.DataFrame, cap: float = 0.25,
               rf: float = 0.0) -> pd.Series:
    """Globally optimal long-only max-Sharpe weights under a position cap.

    Schaible transform: with y = w/(w'(mu-rf)) and kappa = 1/(w'(mu-rf)),
    maximising the ratio is equivalent to minimising y'Sy subject to
    (mu-rf)'y = 1, sum(y) = kappa, 0 <= y <= cap*kappa.
    """
    ex = (mu - rf).reindex(S.index).to_numpy()
    if not (ex > 0).any():
        raise ValueError("no asset has positive excess return; Sharpe is undefined")
    n = len(ex)
    y, k = cp.Variable(n, nonneg=True), cp.Variable(nonneg=True)
    Sig = cp.psd_wrap(S.to_numpy())
    prob = cp.Problem(
        cp.Minimize(cp.quad_form(y, Sig)),
        [ex @ y == 1, cp.sum(y) == k, y <= cap * k, k >= 1e-8],
    )
    prob.solve(solver=cp.CLARABEL)
    if y.value is None:
        raise RuntimeError(f"solver failed: {prob.status}")
    w = pd.Series(y.value / k.value, index=S.index)
    return w.clip(lower=0) / w.clip(lower=0).sum()


def min_variance(S: pd.DataFrame, cap: float = 0.25) -> pd.Series:
    w = cp.Variable(len(S), nonneg=True)
    cp.Problem(cp.Minimize(cp.quad_form(w, cp.psd_wrap(S.to_numpy()))),
               [cp.sum(w) == 1, w <= cap]).solve(solver=cp.CLARABEL)
    return pd.Series(w.value, index=S.index).clip(lower=0)


def enforce_min_positions(w: pd.Series, mu: pd.Series, S: pd.DataFrame,
                          min_positions: int = 6, token_weight: float = 0.02,
                          tol: float = 1e-3) -> pd.Series:
    """Pad the book up to `min_positions` with small positions in the next-best assets.

    The organiser requires five trades per member and the brief wants six
    positions so a rejected or fat-fingered order still leaves the account
    compliant (S10). That is a constraint on the *number of holdings*, not on
    their size.

    Tightening the position cap to 1/k would also force k holdings, but it does
    so by diluting the best assets: on our panel it drops VBIL and VGUS from 25%
    to 16.7% and costs about 2.2 points of realised Sharpe. Padding with small
    positions in the next-best-Sharpe assets costs roughly 0.2 instead, so that
    is what this does.
    """
    held = w[w > tol]
    if len(held) >= min_positions:
        return w

    standalone = (mu.reindex(S.index) / np.sqrt(np.diag(S.to_numpy()))).sort_values(ascending=False)
    need = min_positions - len(held)
    extra = [t for t in standalone.index if t not in held.index][:need]

    out = held.copy() * (1.0 - token_weight * len(extra))
    for t in extra:
        out[t] = token_weight
    return (out / out.sum()).reindex(S.index).fillna(0.0)


def clean_book(w: pd.Series, mu: pd.Series, S: pd.DataFrame,
               min_weight: float = 0.02, min_positions: int = 6) -> pd.Series:
    """Drop positions too small to be worth a commission, then re-pad.

    A convex solve happily returns a 0.4% position if it buys a sliver of
    diversification. On a $250k account that is ~$900 of exposure paying a $10
    commission - 1.1% on the position - and a line item nobody can justify in a
    presentation. Anything below `min_weight` is removed and the book is re-padded
    from the best remaining Sharpe candidates.
    """
    keep = w[w >= min_weight]
    if keep.empty:
        keep = w.nlargest(min_positions)
    keep = keep / keep.sum()
    if len(keep) >= min_positions:
        return keep.reindex(S.index).fillna(0.0)

    standalone = (mu.reindex(S.index) / np.sqrt(np.diag(S.to_numpy()))).sort_values(ascending=False)
    need = min_positions - len(keep)
    extra = [t for t in standalone.index if t not in keep.index][:need]
    out = keep * (1.0 - min_weight * len(extra))
    for t in extra:
        out[t] = min_weight
    return (out / out.sum()).reindex(S.index).fillna(0.0)


def portfolio_stats(w: pd.Series, mu: pd.Series, S: pd.DataFrame,
                    horizon_days: int = 40) -> dict:
    w = w.reindex(S.index).fillna(0.0)
    ret = float(w @ mu.reindex(S.index))
    vol = float(np.sqrt(w @ S.to_numpy() @ w))
    return {
        "ex_ante_sharpe": ret / vol if vol else np.nan,
        "ann_return_%": ret * 100,
        "ann_vol_%": vol * 100,
        "window_return_%": ret * horizon_days / TRADING_DAYS * 100,
        "n_positions": int((w > 1e-4).sum()),
        "max_weight": float(w.max()),
    }
