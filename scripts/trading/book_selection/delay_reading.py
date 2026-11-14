"""Headline numbers under the DELAY reading: all days counted, nothing dropped.

Also tests the remaining ambiguity that only exists under delay - whether the
series is anchored at the entry-day close (purchase cost invisible) or at the
prior all-cash close (entry day scored as a ~-3bp outlier).
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob
import vgdata
from vgdata import sawtooth as sw
rng=np.random.default_rng(5); pd.set_option("display.width",230)
ds=vgdata.build()
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
W=pd.Series({"VBIL":.248,"VGUS":.2477,"VUSB":.2479,"VGSH":.0758,"VFMV":.0498,"VSDB":.0498})
teams={}; seen=set()
for f in sorted(glob.glob("data/private/competition/2026-09-17/*OpenPositions*.csv")):
    df=pd.read_csv(f); h=pd.util.hash_pandas_object(df,index=False).sum()
    if h in seen: continue
    seen.add(h); w=df.groupby("Symbol")["MarketValueDelayed"].sum()
    w=w[w.index.isin(ds.panel["close"].columns)]
    if len(w): teams[f[-8:-4]]=w/w.sum()
eq=[t for t in ds.master.index if str(ds.master.at[t,"asset_class"]).startswith("Stock")
    and t in ds.tr.columns and ds.tr[t].notna().sum()>=1900]
close=ds.panel["close"]; divs=ds.panel["dividends"]
N=36
base=close[list(W.index)].dropna()
idx=[i for i in range(len(base)-N-1)
     if int((divs.reindex(base.index)[["VBIL"]].iloc[i:i+N]>0).any(axis=1).sum())==2][::2]

def path_returns(w,i,credit,anchor):
    w=pd.Series(w); w=w[w>0]
    c=close[list(w.index)].dropna()
    if i+N>len(c): return None
    c=c.iloc[i:i+N]; d=divs.reindex(c.index)[list(w.index)].fillna(0.0)
    p=sw.simulate_account(c,d,w,capital=250_000,credit=credit,half_spread_bp=hs)
    v=p.value
    if anchor=="cash":      # prepend the all-cash day before the purchase
        v=pd.concat([pd.Series([250_000.0],index=[v.index[0]-pd.Timedelta(days=1)]),v])
    return v.pct_change().dropna()

def sharpe(w,i,credit,anchor,warm):
    r=path_returns(w,i,credit,anchor)
    if r is None: return np.nan
    if warm: r=r.iloc[warm:]
    return r.mean()/r.std()*np.sqrt(252) if len(r)>5 and r.std()>0 else np.nan

print(f"{len(idx)} windows of {N} trading days, 2 ex-dates\n")
print("=== our book, all four combinations ===")
for anchor,al in [("close","anchored at entry close (cost invisible)"),
                  ("cash","anchored at prior all-cash close (entry day scored)")]:
    for credit,cl in [("ex_date","same-day"),("pay_date","lagged")]:
        s=np.array([x for x in (sharpe(W,i,credit,anchor,0) for i in idx) if np.isfinite(x)])
        print(f"  DELAY  {al:48s} {cl:9s} {np.median(s):6.2f}")
print()
old=np.array([x for x in (sharpe(W,i,"ex_date","close",5) for i in idx) if np.isfinite(x)])
oldl=np.array([x for x in (sharpe(W,i,"pay_date","close",5) for i in idx) if np.isfinite(x)])
print(f"  (for reference, EXCLUSION reading as previously published: "
      f"same-day {np.median(old):.2f}, lagged {np.median(oldl):.2f})")

print("\n=== rank under DELAY, anchored at entry close ===")
for credit,cl in [("ex_date","same-day"),("pay_date","lagged")]:
    rk=[]
    for i in idx:
        ours=sharpe(W,i,credit,"close",0)
        if not np.isfinite(ours): continue
        fld=[sharpe(rw,i,credit,"close",0) for rw in teams.values()]
        fld+=[sharpe({t:1/6 for t in rng.choice(eq,6,replace=False)},i,credit,"close",0)
              for _ in range(66-len(teams))]
        fld=np.array([x for x in fld if np.isfinite(x)])
        rk.append(int((fld>ours).sum())+1)
    rk=np.array(rk)
    print(f"  {cl:9s} median rank {np.median(rk):4.1f} | P(top3) {(rk<=3).mean():.1%} | "
          f"P(top7) {(rk<=7).mean():.1%} | P(top15) {(rk<=15).mean():.1%}")
