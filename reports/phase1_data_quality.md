# Phase 1 - data quality report

Generated 2026-09-17 00:09. Gate 1: **PASS** (0 blocking flags).

## Coverage

- Vanguard feed: 116 ETFs, **98 investable** after structural exclusions
- Brief roster (S7.2): 92 tickers, **0 unresolved**
- Return panel: 1936 trading days x 98 tickers, 2019-01-03 to 2026-09-16
- Excluded: 18 ({'target-maturity: insufficient history': 10, 'municipal: strictly dominated without taxes': 8})

## Flags

| severity | check | n |
|---|---|---|
| INFO | yield_asof_spread | 1 |
| WARN | adj_reconcile | 4 |
| WARN | insufficient_history | 16 |
| WARN | real_yield | 2 |

### Resolutions

- **adj_reconcile (4)** - Yahoo's `Adj Close` disagrees with `close + dividends` by 5-7 bp on single days (VNQI 2024-12-20, VDE 2022-09-28, VTV/MGV 2020-03-26). Each is a large ordinary distribution on a large-move day; the gap is Yahoo's adjustment-factor rounding. **Resolution: use the `close + dividends` reconstruction, not `Adj Close`.** Accepted.
- **real_yield (2)** - VTIP and VTP publish a *real* SEC yield. Flagged from the feed's footnote text, not a hardcoded list. **Resolution: excluded from any nominal expected-return vector unless an explicit inflation add-on is applied.**
- **insufficient_history (16)** - under 500 observations. Handled per ticker below.
- **yield_asof_spread (1)** - SEC yields carry three different as-of dates (['2026-08-31', '2026-09-10', '2026-09-14']). Informational.

## Funds with insufficient history

| ticker | inception | obs | disposition |
|---|---|---|---|
| BNDP | 2025-12-02 | 196 | proxy with BND |
| VBIL | 2025-02-07 | 400 | proxy with FRED 1M bill total return |
| VCHY | 2026-06-02 | 72 | exclude from covariance; overlay only |
| VDG | 2026-04-14 | 106 | exclude |
| VDIG | 2025-11-14 | 207 | proxy with VIG |
| VDV | 2026-04-14 | 106 | exclude |
| VEXC | 2025-09-30 | 240 | exclude; overlay for the pitch |
| VGHY | 2025-09-16 | 251 | proxy with VCHY/VWOB |
| VGMS | 2025-06-09 | 318 | exclude |
| VGUS | 2025-02-07 | 400 | proxy with FRED 3M bill total return |
| VGVT | 2025-07-07 | 300 | proxy with VGIT |
| VSDB | 2025-04-01 | 365 | proxy with a VCSH/VGSH blend |
| VTG | 2025-07-07 | 299 | proxy with VGIT/VGSH |
| VTP | 2025-07-07 | 299 | exclude (real yield too) |
| VUSG | 2025-11-14 | 207 | proxy with VUG |
| VUSV | 2025-11-14 | 207 | proxy with VTV |

## Distribution calendar

Days between ex-date and pay date, across the universe:

| lag (days) | funds |
|---|---|
| 2 | 52 |
| 3 | 3 |
| 4 | 18 |
| 5 | 25 |

Minimum lag is 2 days; no fund pays on its ex-date. Note the scope of this claim: it describes the **funds' real distribution calendar**, not StockTrak's accounting. A simulator is free to credit cash on the ex-date regardless of the real pay date, and some do. So this confirms the *mechanism* exists universe-wide, but whether it reaches our scored return series is still the open question, and 1 October settles it.

## Trading cost

Two estimators, reconciled in `vgdata.blended_spread` (see module docstring for the bias in each). Short-end candidates, full spread in bp:

| ticker | Corwin-Schultz | quote feed | used |
|---|---|---|---|
| VBIL | 0.28 | 0.00 | 0.28 |
| VGUS | 0.34 | 1.32 | 0.34 |
| VUSB | 1.23 | 4.04 | 1.23 |
| VGSH | 1.30 | 1.74 | 1.30 |
| VSDB | 3.33 | 10.66 | 3.33 |
| VCSH | 2.07 | 2.58 | 2.07 |
| VTIP | 2.23 | 2.03 | 2.03 |
| BSV | 2.74 | 2.61 | 2.61 |
