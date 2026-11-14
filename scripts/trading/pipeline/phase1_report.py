"""Phase 1 deliverable: build the datasets and write the data-quality report."""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
import vgdata
from vgdata.config import REPORTS, today_stamp

pd.set_option("display.width", 200)

ds = vgdata.build()
sp = vgdata.estimate_spreads(ds.panel)
bl = vgdata.blended_spread(sp, ds.quotes)
bl.to_parquet(vgdata.PROCESSED / f"spreads_{today_stamp()}.parquet")

L = []
w = L.append
w("# Phase 1 - data quality report\n")
w(f"Generated {pd.Timestamp.today():%Y-%m-%d %H:%M}. Gate 1: "
  f"**{'BLOCKED' if len(ds.blocking) else 'PASS'}** ({len(ds.blocking)} blocking flags).\n")

w("## Coverage\n")
w(f"- Vanguard feed: {len(ds.master) + len(ds.dropped)} ETFs, "
  f"**{len(ds.master)} investable** after structural exclusions")
w(f"- Brief roster (S7.2): {len(vgdata.BRIEF_ROSTER)} tickers, "
  f"**{sum(t not in ds.master.index and t not in ds.dropped.index for t in vgdata.BRIEF_ROSTER)} unresolved**")
w(f"- Return panel: {ds.tr.shape[0]} trading days x {ds.tr.shape[1]} tickers, "
  f"{ds.tr.index.min():%Y-%m-%d} to {ds.tr.index.max():%Y-%m-%d}")
w(f"- Excluded: {len(ds.dropped)} "
  f"({ds.dropped['drop_reason'].value_counts().to_dict()})\n")

w("## Flags\n")
w("| severity | check | n |\n|---|---|---|")
for (sev, chk), n in ds.flags.groupby(["severity", "check"]).size().items():
    w(f"| {sev} | {chk} | {n} |")
w("")

w("### Resolutions\n")
w("- **adj_reconcile (4)** - Yahoo's `Adj Close` disagrees with `close + dividends` "
  "by 5-7 bp on single days (VNQI 2024-12-20, VDE 2022-09-28, VTV/MGV 2020-03-26). "
  "Each is a large ordinary distribution on a large-move day; the gap is Yahoo's "
  "adjustment-factor rounding. **Resolution: use the `close + dividends` "
  "reconstruction, not `Adj Close`.** Accepted.")
w("- **real_yield (2)** - VTIP and VTP publish a *real* SEC yield. Flagged from the "
  "feed's footnote text, not a hardcoded list. **Resolution: excluded from any "
  "nominal expected-return vector unless an explicit inflation add-on is applied.**")
w("- **insufficient_history (16)** - under 500 observations. Handled per ticker below.")
w("- **yield_asof_spread (1)** - SEC yields carry three different as-of dates "
  f"({sorted(ds.master['sec_yield_asof'].dropna().unique())}). Informational.\n")

young = ds.flags[ds.flags["check"] == "insufficient_history"]["ticker"].tolist()
w("## Funds with insufficient history\n")
w("| ticker | inception | obs | disposition |\n|---|---|---|---|")
DISPOSITION = {
    "VBIL": "proxy with FRED 1M bill total return", "VGUS": "proxy with FRED 3M bill total return",
    "VSDB": "proxy with a VCSH/VGSH blend", "VCHY": "exclude from covariance; overlay only",
    "VDG": "exclude", "VDV": "exclude", "VEXC": "exclude; overlay for the pitch",
    "VGHY": "proxy with VCHY/VWOB", "VGMS": "exclude", "VGVT": "proxy with VGIT",
    "VTG": "proxy with VGIT/VGSH", "VTP": "exclude (real yield too)",
    "BNDP": "proxy with BND", "VDIG": "proxy with VIG", "VUSG": "proxy with VUG",
    "VUSV": "proxy with VTV",
}
for t in young:
    n = int(ds.panel["close"][t].notna().sum())
    w(f"| {t} | {ds.master.at[t,'inception']:%Y-%m-%d} | {n} | {DISPOSITION.get(t,'TBD')} |")
w("")

w("## Distribution calendar\n")
lag = ds.quotes["pay_lag_days"].dropna()
w("Days between ex-date and pay date, across the universe:\n")
w("| lag (days) | funds |\n|---|---|")
for k, v in lag.value_counts().sort_index().items():
    w(f"| {int(k)} | {v} |")
w(f"\nMinimum lag is {int(lag.min())} days; no fund pays on its ex-date. Note the "
  "scope of this claim: it describes the **funds' real distribution calendar**, "
  "not StockTrak's accounting. A simulator is free to credit cash on the ex-date "
  "regardless of the real pay date, and some do. So this confirms the *mechanism* "
  "exists universe-wide, but whether it reaches our scored return series is still "
  "the open question, and 1 October settles it.\n")

w("## Trading cost\n")
w("Two estimators, reconciled in `vgdata.blended_spread` (see module docstring "
  "for the bias in each). Short-end candidates, full spread in bp:\n")
w("| ticker | Corwin-Schultz | quote feed | used |\n|---|---|---|---|")
for t in ["VBIL", "VGUS", "VUSB", "VGSH", "VSDB", "VCSH", "VTIP", "BSV"]:
    if t in bl.index:
        r = bl.loc[t]
        w(f"| {t} | {r['cs_spread_bp']:.2f} | {r['quote_spread_bp']:.2f} | {r['spread_bp']:.2f} |")
w("")

out = REPORTS / "phase1_data_quality.md"
out.write_text("\n".join(L))
print("\n".join(L))
print(f"\n--- written to {out} ---")
