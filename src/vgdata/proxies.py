"""Backfilling funds that are too young to estimate a covariance from.

Sixteen funds have under 500 observations, including VBIL and VGUS, which carry
the two largest weights in the brief's S9.1 portfolio. Dropping them is not an
option and asserting a proxy is not evidence, so each proxy is *fitted* on the
overlap period and reported with the statistics that say whether it is any good.

The fit is non-negative least squares on candidate returns, which keeps the
replication interpretable as a portfolio rather than a long/short hedge that
happens to fit in sample.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import nnls

# Candidate replicating sets. Each is chosen for economic similarity - same
# duration bucket, same credit quality, same geography - not by data mining.
CANDIDATES: dict[str, list[str]] = {
    "VBIL": ["BILL1M", "BILL3M", "VGSH"],
    "VGUS": ["BILL1M", "BILL3M", "VGSH"],
    "VSDB": ["VCSH", "VGSH", "BSV"],
    "VTG":  ["VGSH", "VGIT", "VGLT"],
    "VGVT": ["VGIT", "VGSH", "VMBS"],
    "BNDP": ["BND", "VCIT", "VGIT"],
    "VGHY": ["VWOB", "VCIT", "VCLT"],
    "VCHY": ["VWOB", "VCIT", "VCLT"],
    "VGMS": ["VCIT", "VWOB", "BND"],
    "VTP":  ["VTIP", "VGIT", "VGLT"],
    "VDIG": ["VIG", "VTV", "VOO"],
    "VUSG": ["VUG", "VONG", "VOO"],
    "VUSV": ["VTV", "VONV", "VOO"],
    "VDG":  ["VEA", "VGK", "VPL"],
    "VDV":  ["VEA", "VGK", "VPL"],
    "VEXC": ["VWO", "VPL", "VEA"],
}

MIN_OVERLAP = 60          # trading days needed before a fit is trusted
GOOD_R2 = 0.90            # below this the proxy is reported as weak
GOOD_TE_BP = 15.0         # annualised tracking error, bp of daily vol


@dataclass
class ProxyFit:
    ticker: str
    weights: pd.Series
    r2: float
    te_daily_bp: float          # daily tracking-error sd, in bp
    n_overlap: int

    @property
    def quality(self) -> str:
        if self.n_overlap < MIN_OVERLAP:
            return "UNUSABLE"
        if self.r2 >= GOOD_R2 and self.te_daily_bp <= GOOD_TE_BP:
            return "GOOD"
        if self.r2 >= 0.70:
            return "FAIR"
        return "WEAK"

    def describe(self) -> str:
        w = ", ".join(f"{k} {v:.0%}" for k, v in self.weights.items() if v > 0.005)
        return (f"{self.ticker}: {w or 'no fit'} | R2 {self.r2:.3f} | "
                f"TE {self.te_daily_bp:.1f} bp/day | n={self.n_overlap} | {self.quality}")


def fit_proxy(ticker: str, returns: pd.DataFrame, candidates: list[str] | None = None) -> ProxyFit:
    """Non-negative least squares replication of `ticker` from its candidates."""
    cands = [c for c in (candidates or CANDIDATES.get(ticker, [])) if c in returns.columns]
    if not cands or ticker not in returns.columns:
        return ProxyFit(ticker, pd.Series(dtype=float), np.nan, np.nan, 0)

    df = returns[[ticker] + cands].dropna()
    if len(df) < 10:
        return ProxyFit(ticker, pd.Series(dtype=float), np.nan, np.nan, len(df))

    y = df[ticker].to_numpy()
    X = df[cands].to_numpy()
    coef, _ = nnls(X, y)
    fitted = X @ coef
    resid = y - fitted
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (resid**2).sum() / ss_tot if ss_tot > 0 else np.nan
    return ProxyFit(ticker, pd.Series(coef, index=cands), float(r2),
                    float(resid.std() * 1e4), len(df))


def add_bill_columns(returns: pd.DataFrame) -> pd.DataFrame:
    """Append FRED bill total-return columns so they can act as candidates."""
    from .rates import proxy_series

    out = returns.copy()
    for name, key in (("BILL1M", "bill_1m"), ("BILL3M", "bill_3m")):
        out[name] = proxy_series(returns.index, key)
    return out


def fit_all(returns: pd.DataFrame, tickers: list[str] | None = None) -> dict[str, ProxyFit]:
    r = add_bill_columns(returns)
    return {t: fit_proxy(t, r) for t in (tickers or list(CANDIDATES)) if t in r.columns}


def backfill(returns: pd.DataFrame, fits: dict[str, ProxyFit],
             min_quality: tuple[str, ...] = ("GOOD", "FAIR")) -> tuple[pd.DataFrame, list[str]]:
    """Extend young funds backwards with their fitted proxy returns.

    Only GOOD and FAIR fits are used. Anything weaker is left short and must be
    excluded from the covariance rather than filled with a bad replication -
    a fabricated history is worse than a missing one.
    """
    r = add_bill_columns(returns)
    out = returns.copy()
    used: list[str] = []
    for t, fit in fits.items():
        if fit.quality not in min_quality or fit.weights.empty:
            continue
        synth = (r[fit.weights.index] * fit.weights).sum(axis=1)
        first = out[t].first_valid_index()
        if first is None:
            continue
        out[t] = out[t].where(out[t].notna(), synth.where(synth.index < first))
        used.append(t)
    return out, used
