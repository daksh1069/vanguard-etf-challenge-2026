"""Entry-date sweep: 2 (warm-up reading) x 2 (crediting) x 2 (off-by-one) x entry date.

Historical analogues are built by aligning on real ex-dates: for each past
ex-date E, a window is started `offset` trading days before it, with the same
length as the 2026 window from that entry date to 6 Nov.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import vgdata
from vgdata import sawtooth as sw
pd.set_option("display.width",240)
ds=vgdata.build()
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
W=pd.Series({"VBIL":.248,"VGUS":.2477,"VUSB":.2479,"VGSH":.0758,"VFMV":.0498,"VSDB":.0498})
close=ds.panel["close"][list(W.index)].dropna()
divs=ds.panel["dividends"].reindex(close.index)[list(W.index)].fillna(0.0)
exmask=(divs[["VBIL"]]>0).any(axis=1).to_numpy()
expos=[k for k,v in enumerate(exmask) if v]

td=pd.bdate_range("2026-09-18","2026-11-06")
entries=[]
EX1=pd.Timestamp("2026-10-01")
for d in td[:11]:
    w=list(td[td>=d]); n=len(w)
    if EX1 not in w: continue          # entered after the dip; nothing to position around
    entries.append((d,n,w.index(EX1)))

def score(i, n, warm, credit):
    """Simulate n days from index i; drop `warm` leading return observations."""
    if i<0 or i+n>len(close): return np.nan
    c=close.iloc[i:i+n]; d=divs.iloc[i:i+n]
    p=sw.simulate_account(c,d,W,capital=250_000,credit=credit,half_spread_bp=hs)
    r=p.returns.dropna()
    if warm: r=r.iloc[warm:]
    return r.mean()/r.std()*np.sqrt(252) if len(r)>5 and r.std()>0 else np.nan

rows={}
for d,n,o1 in entries:
    # historical windows whose first ex-date sits o1 trading days after the start
    starts=[p-o1 for p in expos if p-o1>=0 and p-o1+n<=len(close)]
    if len(starts)<8: continue
    rec={}
    for credit in ("ex_date","pay_date"):
        for wl,warm in [("excl@5",5),("excl@6",6),("delay",0)]:
            v=np.array([x for x in (score(s,n,warm,credit) for s in starts) if np.isfinite(x)])
            rec[f"{wl}/{'same' if credit=='ex_date' else 'lag'}"]=np.median(v) if len(v) else np.nan
    rec["n_days"]=n; rec["off_ex1"]=o1; rec["n_win"]=len(starts)
    rows[d.strftime("%a %d %b")]=rec
R=pd.DataFrame(rows).T
cols=["n_days","off_ex1","n_win",
      "excl@5/same","excl@6/same","delay/same",
      "excl@5/lag","excl@6/lag","delay/lag"]
print("=== median Sharpe by entry date, warm-up reading and crediting branch ===\n")
print(R[cols].round(2).to_string())
print("\n  excl@5 = scoring starts ON the 5th trading day after entry")
print("  excl@6 = scoring starts AFTER the 5th (the reading the note implies)")
print("  delay  = all days counted, nothing dropped")
b=R.loc["Fri 18 Sep"]
print("\n=== gain vs trading 18 Sep ===")
for k in ["Thu 24 Sep","Fri 25 Sep","Mon 28 Sep"]:
    if k in R.index:
        r=R.loc[k]
        print(f"  {k}: "+"  ".join(f"{c} {r[c]-b[c]:+.2f}" for c in cols[3:]))
