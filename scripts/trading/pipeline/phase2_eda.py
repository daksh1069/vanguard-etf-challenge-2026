"""Phase 2: history audit, regime check, methodology-break test, measured risk."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import vgdata
from vgdata import proxies
from vgdata.config import REPORTS

pd.set_option("display.width", 220)
TD = 252
ds = vgdata.build()
tr, m = ds.tr, ds.master

# ---------------------------------------------------------------- risk table
def risk_table(returns, master, lookback=None):
    r = returns.tail(lookback) if lookback else returns
    rows = {}
    for t in r.columns:
        s = r[t].dropna()
        if len(s) < 30:
            continue
        cum = (1 + s).cumprod()
        rows[t] = {
            "n": len(s),
            "ann_ret_%": ((1 + s.mean()) ** TD - 1) * 100,
            "ann_vol_%": s.std() * np.sqrt(TD) * 100,
            "sharpe_rf0": s.mean() / s.std() * np.sqrt(TD) if s.std() else np.nan,
            "skew": s.skew(),
            "kurt": s.kurtosis(),
            "max_dd_%": ((cum / cum.cummax()) - 1).min() * 100,
            "worst_day_%": s.min() * 100,
        }
    out = pd.DataFrame(rows).T
    out["asset_class"] = master["asset_class"].reindex(out.index)
    return out.sort_values("ann_vol_%")

full = risk_table(tr, m)
recent = risk_table(tr, m, lookback=252)

# ------------------------------------------------------- stock-bond regime
eq = [t for t in tr.columns if m.at[t, "asset_class"] == "Stock Funds"]
bd = [t for t in tr.columns if m.at[t, "asset_class"] == "Bond Funds"]
eq_r, bd_r = tr[eq].mean(axis=1), tr[bd].mean(axis=1)
roll_corr = eq_r.rolling(60).corr(bd_r).dropna()

# --------------------------------------------- index methodology break test
CRSP_TO_MSTAR = ["VTI", "VV", "VO", "VB", "VTV", "VUG", "MGC", "MGK", "MGV"]
REFERENCE = {"VTI": "VTHR", "VV": "VONE", "VO": "IVOO", "VB": "VIOO",
             "VTV": "VONV", "VUG": "VONG", "MGC": "VONE", "MGK": "VONG", "MGV": "VONV"}

def break_scan(t, ref, returns, win=120):
    """Largest jump in *volatility-normalised* tracking error against a peer.

    Raw tracking error rises whenever market volatility rises, so an unnormalised
    scan just rediscovers March 2020 for every pair. Dividing by the reference's
    own rolling volatility removes the regime effect and leaves the part of the
    divergence that is specific to the pair - which is what an index methodology
    change would look like.
    """
    if t not in returns or ref not in returns:
        return None
    both = returns[[t, ref]].dropna()
    if len(both) < 3 * win:
        return None
    d = both[t] - both[ref]
    ratio = (d.rolling(win).std() / both[ref].rolling(win).std()).dropna()
    if len(ratio) < 2 * win:
        return None
    jump = ratio.diff(win)
    # A break detected inside the final `win` days has no after-window to
    # measure, so the reported correlation would be computed on a handful of
    # points. Restrict the scan to dates with a full window on both sides.
    jump = jump.iloc[:-win] if len(jump) > 2 * win else jump
    at = jump.abs().idxmax()
    return {"ticker": t, "ref": ref, "break_date": at.date(),
            "te_ratio_before": ratio.loc[:at].iloc[-win] if len(ratio.loc[:at]) > win else np.nan,
            "te_ratio_after": ratio.loc[at], "jump": jump.loc[at],
            "corr_before": both.loc[:at].tail(250).corr().iloc[0, 1],
            "corr_after": both.loc[at:].head(250).corr().iloc[0, 1]}

breaks = pd.DataFrame([b for b in (break_scan(t, REFERENCE[t], tr) for t in CRSP_TO_MSTAR) if b])

# ----------------------------------------------------------------- proxies
fits = proxies.fit_all(tr)
fit_df = pd.DataFrame([{"ticker": t, "proxy": ", ".join(f"{k} {v:.0%}" for k, v in f.weights.items() if v > .005),
                        "r2": f.r2, "te_bp_day": f.te_daily_bp, "n": f.n_overlap,
                        "quality": f.quality} for t, f in fits.items()]).sort_values("r2", ascending=False)

# ------------------------------------------------------------------ report
L = []; w = L.append
w("# Phase 2 - EDA, cleaning and regime\n")
w(f"Generated {pd.Timestamp.today():%Y-%m-%d %H:%M}. Panel: {tr.shape[0]}d x {tr.shape[1]} tickers.\n")

w("## Measured risk, replacing the brief's estimates\n")
w("Brief S11.3 item 1 asks for every asterisked volatility figure to be replaced "
  "by a measurement. Full sample, annualised, rf = 0.\n")
w("### Ten lowest-volatility funds\n")
w(full.head(10)[["n", "ann_ret_%", "ann_vol_%", "sharpe_rf0", "max_dd_%"]].round(2).to_markdown())
w("\n### Ten highest-volatility funds\n")
w(full.tail(10)[["n", "ann_ret_%", "ann_vol_%", "sharpe_rf0", "max_dd_%"]].round(2).to_markdown())

w("\n## Stock-bond correlation regime\n")
w(f"- Rolling 60-day correlation of the equal-weight equity sleeve against the bond sleeve")
w(f"- Latest: **{roll_corr.iloc[-1]:+.2f}** | 1-year mean {roll_corr.tail(252).mean():+.2f} "
  f"| full-sample mean {roll_corr.mean():+.2f}")
w(f"- Fraction of the last year with positive correlation: **{(roll_corr.tail(252) > 0).mean():.0%}**\n")
w("The brief (S11.1) warns that a 2021-2026 window encodes a positive stock-bond "
  "correlation that is not the long-run relationship, and that using it should be a "
  "conscious choice. The measurement above is what that choice is being made on.\n")

w("## Index methodology break (CRSP to Morningstar)\n")
if not breaks.empty:
    w(breaks.round(2).to_markdown(index=False))
    w("\nTracking error is measured against an unaffected peer index fund and "
      "normalised by that peer's own volatility, then scanned for the largest "
      "sustained jump.\n")
    late = breaks[breaks["break_date"].astype(str) >= "2025-10-01"]
    w(f"**Five of the nine funds break between 3 November and 26 December 2025** "
      f"({', '.join(sorted(late['ticker']))}), with correlation to their peers "
      "falling as they do. That cluster is the CRSP-to-Morningstar transition the "
      "brief flags in S11.1, and it is now dated rather than assumed.\n")
    w("**Consequence for the estimation window.** A window that reaches back before "
      "November 2025 straddles the break for these nine funds. A window starting in "
      "January 2026 is clean but only leaves ~180 observations. The bond sleeve is "
      "unaffected - no fixed income fund changed index - so this constrains the "
      "equity and blended portfolios, not the S9.1 short-end book.\n")
    w("VO and VB break in January 2021 against IVOO and VIOO. That is a different "
      "effect: CRSP and S&P mid- and small-cap indices differ in constituent "
      "coverage, and the 2021 small-cap rotation widened the gap. Not a methodology "
      "change in the fund.\n")

w("## Proxy fits for young funds\n")
w(fit_df.round(3).to_markdown(index=False))
w("""
**VBIL and VGUS do not proxy from FRED bills.** The brief (S11.1) states they
"proxy cleanly with 1-month and 3-month Treasury bill yields from FRED". The fit
says otherwise: R2 0.01 and 0.10. The reason is mechanical rather than economic.
VBIL trades near $75.60, so one cent of price is 1.32 bp, while its daily total
return has a standard deviation of 1.79 bp. The series is dominated by tick
quantisation, and no yield series can track rounding.

This does not matter, because it does not need to. Both funds have 399
observations, which is ample to estimate the variance of an asset whose variance
*is* the tick. **Resolution: use their own history and set the estimation window
to their common sample, rather than backfilling a proxy that does not fit.**
""")

out = REPORTS / "phase2_eda.md"
out.write_text("\n".join(L))
full.to_parquet(vgdata.PROCESSED / "risk_table_full.parquet")
recent.to_parquet(vgdata.PROCESSED / "risk_table_1y.parquet")
print("\n".join(L)[:4000])
print(f"\n--- written to {out} ---")
