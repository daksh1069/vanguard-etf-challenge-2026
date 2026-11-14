"""Data-quality gates.

Every check returns rows describing what is wrong and how bad it is. build()
refuses to declare success while any BLOCK-severity flag is outstanding; WARN
flags must be explicitly accepted in writing (PLAN Gate 1 / Gate 2).
"""
from __future__ import annotations

import pandas as pd

from .config import load

BLOCK, WARN, INFO = "BLOCK", "WARN", "INFO"


def _flag(rows, sev, check, ticker, detail):
    rows.append({"severity": sev, "check": check, "ticker": ticker, "detail": detail})


def check_master(master: pd.DataFrame, roster: list[str] | None = None) -> list[dict]:
    rows: list[dict] = []
    for t in roster or []:
        if t not in master.index:
            _flag(rows, BLOCK, "roster_resolves", t, "in brief roster but absent from Vanguard feed")

    bonds = master[master["asset_class"].fillna("").str.contains("Bond", case=False)]
    for t, r in bonds.iterrows():
        if pd.isna(r["sec_yield"]):
            _flag(rows, BLOCK, "sec_yield_present", t, "bond fund with no SEC yield")

    for t, r in master[master["yield_is_real"]].iterrows():
        _flag(rows, WARN, "real_yield", t,
              f"publishes a REAL yield ({r['sec_yield']:.2%}); needs an inflation "
              "add-on before entering a nominal expected-return vector")

    stale = master["sec_yield_asof"].dropna()
    if not stale.empty and stale.nunique() > 1:
        _flag(rows, INFO, "yield_asof_spread", "-", f"SEC yield as-of dates: {sorted(stale.unique())}")
    return rows


def check_history(panel: dict[str, pd.DataFrame], master: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    cfg = load()["data"]
    min_obs = cfg["min_obs_for_covariance"]
    close = panel["close"]

    for t in master.index:
        if t not in close.columns:
            _flag(rows, BLOCK, "price_present", t, "no price series returned")
            continue
        s = close[t].dropna()
        if s.empty:
            _flag(rows, BLOCK, "price_present", t, "price series is entirely empty")
            continue
        n = len(s)
        if n < min_obs:
            inc = master.at[t, "inception"]
            _flag(rows, WARN, "insufficient_history", t,
                  f"{n} obs (< {min_obs}); inception {pd.Timestamp(inc).date()} "
                  "- proxy or exclude from covariance")
        if (s <= 0).any():
            _flag(rows, BLOCK, "positive_prices", t, "zero or negative close present")

    if not close.index.is_monotonic_increasing:
        _flag(rows, BLOCK, "index_monotone", "-", "price index is not sorted")
    if close.index.has_duplicates:
        _flag(rows, BLOCK, "index_unique", "-", "duplicate dates in price index")
    return rows


def check_adjustment(panel: dict[str, pd.DataFrame], tol_bp: float = 5.0) -> list[dict]:
    """Reconcile Yahoo's Adj Close against close + dividends.

    This is the failure mode a second close-price vendor would not catch, and
    it is why Stooq's loss as a cross-check costs us nothing.
    """
    rows: list[dict] = []
    if "adj_close" not in panel:
        _flag(rows, WARN, "adj_reconcile", "-", "no Adj Close returned; skipped")
        return rows

    close, adj, div = panel["close"], panel["adj_close"], panel["dividends"].fillna(0.0)
    for t in close.columns:
        if t not in adj.columns:
            continue
        c, a = close[t].dropna(), adj[t].dropna()
        idx = c.index.intersection(a.index)
        if len(idx) < 30:
            continue
        # Total return implied by each representation must agree.
        tr_adj = (a[idx] / a[idx].shift(1) - 1).dropna()
        d = div[t].reindex(idx).fillna(0.0) if t in div.columns else pd.Series(0.0, index=idx)
        tr_raw = ((c[idx] + d) / c[idx].shift(1) - 1).dropna()
        common = tr_adj.index.intersection(tr_raw.index)
        if common.empty:
            continue
        diff_bp = (tr_adj[common] - tr_raw[common]).abs() * 1e4
        worst = diff_bp.max()
        if worst > tol_bp:
            when = diff_bp.idxmax().date()
            _flag(rows, WARN, "adj_reconcile", t,
                  f"adj-vs-raw total return differs by {worst:.1f} bp on {when}")
    return rows


def check_vendor_agreement(panel: dict[str, pd.DataFrame], master: pd.DataFrame,
                           tol_bp: float = 20.0) -> list[dict]:
    """Yahoo's last close vs Vanguard's own market price for the same day."""
    rows: list[dict] = []
    close = panel["close"]
    for t in master.index:
        if t not in close.columns:
            continue
        s = close[t].dropna()
        vg = master.at[t, "market_price"]
        if s.empty or pd.isna(vg) or vg <= 0:
            continue
        last_date = pd.Timestamp(master.at[t, "price_asof"]) if master.at[t, "price_asof"] else None
        if last_date is None or last_date not in s.index:
            continue
        diff_bp = abs(s.loc[last_date] / vg - 1) * 1e4
        if diff_bp > tol_bp:
            _flag(rows, WARN, "vendor_agreement", t,
                  f"Yahoo {s.loc[last_date]:.2f} vs Vanguard {vg:.2f} on "
                  f"{last_date.date()} ({diff_bp:.0f} bp)")
    return rows


def report(flags: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(flags, columns=["severity", "check", "ticker", "detail"])
    if df.empty:
        return df
    order = {BLOCK: 0, WARN: 1, INFO: 2}
    return df.sort_values(["severity", "check", "ticker"], key=lambda s: s.map(order).fillna(9)
                          if s.name == "severity" else s).reset_index(drop=True)
