"""Effective bid-ask spread estimation.

The brief lists bid-ask spread as an unmodelled cost (S12.4). Vanguard's quote
feed publishes bid/ask but its end-of-day pair is often a stale wide quote left
at the bell, so it cannot be trusted for the thinner funds - exactly the ones
where the spread matters.

Corwin & Schultz (2012) recover the effective spread from the daily high-low
range, which we have for every ticker over the full sample. The intuition: the
high-low ratio over one day reflects both volatility and the spread, while the
ratio over two days reflects roughly twice the volatility but the same spread,
so the two can be separated.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

_K = 3 - 2 * np.sqrt(2)


def corwin_schultz(high: pd.Series, low: pd.Series, window: int | None = None) -> pd.Series:
    """Daily effective-spread estimates as a fraction of price.

    Negative estimates are set to zero, which is the convention in the original
    paper: they arise when the two-day range happens to be small relative to the
    one-day ranges, and are noise rather than information.
    """
    h, l = high.astype(float), low.astype(float)
    ok = (h > 0) & (l > 0)
    h, l = h.where(ok), l.where(ok)

    hl = np.log(h / l) ** 2
    beta = hl + hl.shift(-1)

    h2 = pd.concat([h, h.shift(-1)], axis=1).max(axis=1)
    l2 = pd.concat([l, l.shift(-1)], axis=1).min(axis=1)
    gamma = np.log(h2 / l2) ** 2

    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / _K - np.sqrt(gamma / _K)
    spread = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    spread = spread.where(spread > 0, 0.0)

    if window:
        spread = spread.rolling(window, min_periods=max(5, window // 4)).mean()
    return spread


def estimate_spreads(panel: dict[str, pd.DataFrame], lookback: int = 120) -> pd.DataFrame:
    """Per-ticker effective spread in bp, over the most recent `lookback` days."""
    high, low = panel["high"], panel["low"]
    rows = {}
    for t in high.columns:
        s = corwin_schultz(high[t], low[t]).dropna()
        if s.empty:
            continue
        recent = s.tail(lookback)
        rows[t] = {
            "cs_spread_bp": recent.mean() * 1e4,
            "cs_spread_bp_median": recent.median() * 1e4,
            "cs_half_spread_bp": recent.mean() / 2 * 1e4,
            "n_obs": len(recent),
        }
    return pd.DataFrame(rows).T.sort_values("cs_spread_bp")


def blended_spread(cs: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    """Reconcile the two spread estimators into one usable number.

    Both are biased upward, in opposite regimes:

      Corwin-Schultz  attributes part of intraday volatility to the spread, so
                      it overstates for high-volatility equity ETFs (it puts
                      VGT at 34 bp; the real figure is low single digits)
      quote feed      can be a stale wide quote left at the bell, so it
                      overstates for thinly traded funds

    Taking the minimum is therefore the tighter upper bound on the true spread,
    and the disagreement between them is itself reported so a large gap gets
    looked at rather than silently averaged away.
    """
    df = cs[["cs_spread_bp"]].join(quotes[["spread_bp", "quote_stale"]], how="outer")
    df = df.rename(columns={"spread_bp": "quote_spread_bp"})
    # A zero quoted spread is a locked market at the bell, not a free trade,
    # so it is discarded rather than taken as the tighter estimate.
    usable_quote = df["quote_spread_bp"].where(
        ~df["quote_stale"].fillna(False) & (df["quote_spread_bp"] > 0)
    )
    df["spread_bp"] = df[["cs_spread_bp"]].join(usable_quote.rename("q")).min(axis=1)
    df["half_spread_bp"] = df["spread_bp"] / 2
    df["estimator_gap_bp"] = (df["cs_spread_bp"] - usable_quote).abs()
    return df.sort_values("spread_bp")


def cost_of_entry(weights: pd.Series, spreads_bp: pd.Series, notional: float,
                  commission: float = 10.0) -> pd.DataFrame:
    """One-off cost of building a portfolio: half-spread paid plus commission.

    Buying crosses the spread - StockTrak fills at real-time bid/ask - so entry
    costs the half-spread on the traded notional, once.
    """
    w = weights[weights > 0]
    hs = spreads_bp.reindex(w.index).fillna(spreads_bp.median()) / 2
    df = pd.DataFrame({
        "weight": w,
        "notional": w * notional,
        "half_spread_bp": hs,
        "spread_cost": w * notional * hs / 1e4,
        "commission": commission,
    })
    df["total_cost"] = df["spread_cost"] + df["commission"]
    df["cost_bp_of_portfolio"] = df["total_cost"] / notional * 1e4
    return df.sort_values("total_cost", ascending=False)
