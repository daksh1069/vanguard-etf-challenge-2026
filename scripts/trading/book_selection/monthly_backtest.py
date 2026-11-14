"""Rigorous monthly-cohort backtest of the Sharpe book, both crediting conventions.

Each cohort buys on the first trading day of a month and holds 40 trading days -
the competition's window length. Fully realistic: integer shares only, $10
commission per position, entry across the half-spread, cash earns 0%,
distributions never reinvested.

The same windows are run for the seven real competitor portfolios exported from
StockTrak on 17 Sep 2026, so each cohort is a head-to-head.
"""
import warnings; warnings.filterwarnings("ignore")
import glob, os
import numpy as np, pandas as pd
import vgdata
from vgdata import sawtooth as sw

pd.set_option("display.width", 240)
CAPITAL, HOLD = 250_000, 40

ds = vgdata.build()
hs = vgdata.blended_spread(vgdata.estimate_spreads(ds.panel), ds.quotes)["half_spread_bp"]
BOOK = pd.Series({"VBIL": .25, "VGUS": .25, "VUSB": .25, "VGSH": .19, "VSDB": .04, "VTIP": .02})

rivals = {}
seen = set()
for f in sorted(glob.glob("data/private/competition/2026-09-17/*OpenPositions*.csv")):
    df = pd.read_csv(f)
    h = pd.util.hash_pandas_object(df, index=False).sum()
    if h in seen:
        continue
    seen.add(h)
    w = df.groupby("Symbol")["MarketValueDelayed"].sum()
    w = w[w.index.isin(ds.panel["close"].columns)]
    if len(w):
        rivals[os.path.basename(f)[-9:-4] or "base"] = w / w.sum()


def run(weights, start, credit):
    """One cohort: buy at `start`, hold HOLD trading days, mark daily."""
    cols = [t for t in weights.index if t in ds.panel["close"].columns]
    w = weights[cols] / weights[cols].sum()
    close = ds.panel["close"][cols].dropna()
    close = close.loc[close.index >= start]
    if len(close) < HOLD + 1:
        return None
    close = close.iloc[: HOLD + 1]
    div = ds.panel["dividends"].reindex(close.index)[cols].fillna(0.0)
    path = sw.simulate_account(close, div, w, capital=CAPITAL, credit=credit,
                               half_spread_bp=hs, commission=10.0)
    st = path.stats()
    st["n_ex_dates"] = int((div > 0).any(axis=1).sum())
    st["start"] = close.index[0].date()
    st["end"] = close.index[-1].date()
    return st


# monthly cohorts: every month whose full 40-day window fits in the sample
common = ds.panel["close"][list(BOOK.index)].dropna()
months = pd.date_range(common.index[0], common.index[-1], freq="MS")
cohorts = []
for m in months:
    nxt = common.index[common.index >= m]
    if len(nxt) and len(common.loc[nxt[0]:]) >= HOLD + 1:
        cohorts.append(nxt[0])

rows = []
for s in cohorts:
    rec = {"cohort": s.strftime("%Y-%m")}
    for credit in ("ex_date", "pay_date"):
        r = run(BOOK, s, credit)
        if r is None:
            continue
        tag = "ex" if credit == "ex_date" else "pay"
        rec[f"sharpe_{tag}"] = r["sharpe"]
        rec[f"vol_{tag}_%"] = r["ann_vol_pct"]
        if tag == "ex":
            rec["ret_%"] = r["total_return_pct"]
            rec["n_ex"] = r["n_ex_dates"]
            rec["window"] = f"{r['start']}->{r['end']}"
    # best rival over the identical window
    for credit, tag in (("ex_date", "ex"), ("pay_date", "pay")):
        best = -99
        for nm, rw in rivals.items():
            rr = run(rw, s, credit)
            if rr and np.isfinite(rr["sharpe"]):
                best = max(best, rr["sharpe"])
        rec[f"best_rival_{tag}"] = best if best > -99 else np.nan
    rows.append(rec)

d = pd.DataFrame(rows)
d["beat_ex"] = d["sharpe_ex"] > d["best_rival_ex"]
d["beat_pay"] = d["sharpe_pay"] > d["best_rival_pay"]

cols = ["cohort", "window", "n_ex", "ret_%", "sharpe_ex", "best_rival_ex", "beat_ex",
        "sharpe_pay", "best_rival_pay", "beat_pay"]
print("=== MONTHLY COHORTS: buy first trading day, hold 40 trading days ===")
print(d[cols].round(2).to_string(index=False))

print(f"\n=== SUMMARY over {len(d)} monthly cohorts ===")
for tag, lbl in (("ex", "same-day crediting"), ("pay", "2-day lag crediting")):
    s = d[f"sharpe_{tag}"]
    print(f"\n  [{lbl}]")
    print(f"    our Sharpe    min {s.min():6.2f} | median {s.median():6.2f} | max {s.max():6.2f}")
    print(f"    negative      {(s < 0).sum()} of {len(s)}")
    print(f"    beat best rival in {int(d['beat_'+tag].sum())}/{len(d)} cohorts "
          f"({d['beat_'+tag].mean():.0%})")
print(f"\n  return: min {d['ret_%'].min():+.2f}% | median {d['ret_%'].median():+.2f}% | "
      f"max {d['ret_%'].max():+.2f}% | negative in {(d['ret_%']<0).sum()}/{len(d)}")
d.to_csv(vgdata.PROCESSED / "monthly_backtest.csv", index=False)
