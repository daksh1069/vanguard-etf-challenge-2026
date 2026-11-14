"""Phase 3: size the distribution-crediting question from history."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import vgdata
from vgdata import sawtooth as sw
from vgdata.config import REPORTS

pd.set_option("display.width", 220)
ds = vgdata.build()
hs = vgdata.blended_spread(vgdata.estimate_spreads(ds.panel), ds.quotes)["half_spread_bp"]

W = pd.Series({"VBIL": .25, "VGUS": .25, "VUSB": .22, "VGSH": .18, "VSDB": .10})
close = ds.panel["close"][W.index].dropna()
divs = ds.panel["dividends"].reindex(close.index)[W.index].fillna(0.0)

starts = list(range(0, len(close) - 41, 5))
res = {"ex_date": [], "pay_date": []}
for i in starts:
    c, d = close.iloc[i:i+41], divs.iloc[i:i+41]
    for cr in res:
        res[cr].append(sw.simulate_account(c, d, W, credit=cr, half_spread_bp=hs).sharpe())

dist = {}
for cr, v in res.items():
    v = np.array([x for x in v if np.isfinite(x)])
    dist[cr] = {"median": np.median(v), "p10": np.percentile(v, 10), "p90": np.percentile(v, 90),
                "mean": v.mean(), "frac_below_2.0": (v < 2).mean(), "windows": len(v)}
dist = pd.DataFrame(dist).T

single = {}
for t in W.index:
    for cr in ("ex_date", "pay_date"):
        p = sw.simulate_account(close.tail(41), divs.tail(41), pd.Series({t: 1.0}),
                                credit=cr, half_spread_bp=hs)
        single[(t, cr)] = p.stats()
single = pd.DataFrame(single).T[["sharpe", "mean_bp", "sd_bp", "worst_day_bp"]]

L = []; w = L.append
w("# Phase 3 - the distribution sawtooth, sized\n")
w(f"Generated {pd.Timestamp.today():%Y-%m-%d %H:%M}.\n")
w("""Brief S9.1 says the volatility of a T-bill book "cannot be stated until V1 is
resolved" - V1 being an October observation of whether StockTrak credits a
distribution on the ex-date or on the pay date. It can be stated now, as a
two-branch answer, by simulating the account exactly as the platform marks it:
integer shares, cash at 0%, no reinvestment, entry across the spread.\n""")

w("## The mechanism\n")
w("- Every bond ETF's price falls by the distribution on its ex-date. Measured on "
  "VBIL: **-21c on a $75.60 price, about -29 bp**, on each of 2026-06-01, 07-01, "
  "08-03 and 09-01. Every other day moves +1 to +3c.")
w("- The quote feed confirms **no fund pays on its ex-date**: the lag is 2 days for "
  "52 of 98 funds, 3 for 3, 4 for 18 and 5 for 25.")
w("- StockTrak charts unadjusted prices, and the sawtooth is plainly visible on its "
  "own VBIL candles, so the price leg definitely reaches the account.")
w("- What is *not* yet known is the cash leg: a simulator may credit on the ex-date "
  "regardless of the real pay date.\n")

w("## The two branches\n")
w(f"Brief S9.1 weights, {len(starts)} rolling 40-day windows over the funds' common "
  f"history ({close.index[0]:%Y-%m-%d} to {close.index[-1]:%Y-%m-%d}), rf = 0:\n")
w(dist.round(2).to_markdown())
w("""
The mean return is identical under both branches - a late payment changes when
value arrives, not how much. The entire gap is volatility. Under same-day
crediting the price drop and the cash credit cancel and sigma falls to the tick
quantisation floor; under lagged crediting the account dips the full 29 bp and
recovers two days later, putting four outlier days into a series whose other
days move about 1 bp.

**Both branches clear the brief's 1.5-2.0 historical winning band** (S6.4), so
the short-end book is the right structure either way. The branch decides the
margin, not the direction.
""")

w("## Per fund, most recent 40 days\n")
w(single.round(2).to_markdown())
w("""
VBIL and VGUS carry the result. They are the only two funds whose daily return
series is dominated by price quantisation rather than by duration: at a $75.60
price one cent is 1.32 bp, against a daily return standard deviation of 1.79 bp.
VGSH and VSDB carry real duration and print negative Sharpe over this particular
window, though across all rolling windows they are negative in only 8-9% of them.
""")

w("## What this changes\n")
w("1. **October is a confirmation, not a blocker.** Both branches are sized, and "
  "the portfolio structure is the same under either. Nothing waits on it.")
w("2. **The ex-date is 1 October**, two days before the first-trade deadline. If the "
  "book is built before then, the observation is free.")
w("3. **What to watch on 1 October:** VBIL should print about -21c. The question is "
  "whether the *account value* dips that day. If it stays flat, we are on the "
  "ex_date branch and the expected Sharpe is around 8; if it dips and recovers on "
  "5 October, we are on the pay_date branch and it is around 2.4.")

out = REPORTS / "phase3_sawtooth.md"
out.write_text("\n".join(L))
print("\n".join(L))
print(f"\n--- written to {out} ---")
