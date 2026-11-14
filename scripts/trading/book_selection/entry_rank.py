"""P(top 7) for an 18 Sep vs 24 Sep entry, across both ambiguities."""
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
base=close[list(W.index)].dropna()
exmask=(divs.reindex(base.index)[["VBIL"]]>0).any(axis=1).to_numpy()
expos=[k for k,v in enumerate(exmask) if v]

def sh(w,i,n,warm,credit):
    w=pd.Series(w); w=w[w>0]
    c=close[list(w.index)].dropna()
    if i<0 or i+n>len(c): return np.nan
    c=c.iloc[i:i+n]; d=divs.reindex(c.index)[list(w.index)].fillna(0.0)
    r=sw.simulate_account(c,d,w,capital=250_000,credit=credit,half_spread_bp=hs).returns.dropna()
    if warm: r=r.iloc[warm:]
    return r.mean()/r.std()*np.sqrt(252) if len(r)>5 and r.std()>0 else np.nan

SC={"18 Sep":(36,9),"24 Sep":(32,5)}
out={}
for lbl,(n,o1) in SC.items():
    starts=[p-o1 for p in expos if p-o1>=0 and p-o1+n<=len(base)]
    for warm,wl in [(5,"exclusion"),(0,"delay")]:
        for credit,cl in [("ex_date","same-day"),("pay_date","lagged")]:
            rk=[]
            for s in starts:
                ours=sh(W,s,n,warm,credit)
                if not np.isfinite(ours): continue
                fld=[sh(rw,s,n,warm,credit) for rw in teams.values()]
                fld+=[sh({t:1/6 for t in rng.choice(eq,6,replace=False)},s,n,warm,credit)
                      for _ in range(66-len(teams))]
                fld=np.array([x for x in fld if np.isfinite(x)])
                rk.append(int((fld>ours).sum())+1)
            rk=np.array(rk)
            out[(lbl,wl,cl)]={"med_rank":np.median(rk),"P(top7)":(rk<=7).mean(),"n":len(rk)}
R=pd.DataFrame(out).T
print(R.round(3).to_string())
print("\n=== change in P(top 7) from waiting to 24 Sep ===")
for wl in ("exclusion","delay"):
    for cl in ("same-day","lagged"):
        d=out[("24 Sep",wl,cl)]["P(top7)"]-out[("18 Sep",wl,cl)]["P(top7)"]
        print(f"  {wl:10s} {cl:9s} {out[('18 Sep',wl,cl)]['P(top7)']:.1%} -> {out[('24 Sep',wl,cl)]['P(top7)']:.1%}   {d:+.1%}")
print("\n=== expected change in P(top 7), by belief ===")
print(f"{'P(excl)':>8s}{'P(same)=50%':>14s}{'70%':>10s}{'85%':>10s}")
for pe in (0.5,0.3,0.2):
    row=f"{pe:8.0%}"
    for ps in (0.5,0.7,0.85):
        ev=sum(pw*pc*(out[("24 Sep",wl,cl)]["P(top7)"]-out[("18 Sep",wl,cl)]["P(top7)"])
               for wl,pw in (("exclusion",pe),("delay",1-pe))
               for cl,pc in (("same-day",ps),("lagged",1-ps)))
        row+=f"{ev:+10.1%}"
    print(row)
