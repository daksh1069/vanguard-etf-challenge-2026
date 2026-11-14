"""Head-to-head: our short-duration book vs the covariance-budget book vs blends."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob
import vgdata
from vgdata import sawtooth as sw, prices as vp
rng=np.random.default_rng(7); pd.set_option("display.width",235)
ds=vgdata.build()
EXTRA=["VSDM","VDE","VGT","VDC","VBIL","BNDX","EDV","VPL","VGUS","VCSH","VGSH","VUSB","VSDB","VFMV","VTI"]
pan=vp.fetch_prices(sorted(set(EXTRA)|set(ds.master.index)))
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
SCORED,TOT=31,36
teams={}; seen=set()
for f in sorted(glob.glob("data/private/competition/2026-09-17/*OpenPositions*.csv")):
    df=pd.read_csv(f); h=pd.util.hash_pandas_object(df,index=False).sum()
    if h in seen: continue
    seen.add(h); w=df.groupby("Symbol")["MarketValueDelayed"].sum()
    w=w[w.index.isin(pan["close"].columns)]
    if len(w): teams[f[-8:-4]]=w/w.sum()
tr=vp.total_return(pan)
eq=[t for t in ds.master.index if str(ds.master.at[t,"asset_class"]).startswith("Stock")
    and t in tr.columns and tr[t].notna().sum()>=1900]

THEIRS={"VSDM":.1841,"VDE":.1730,"VGT":.1642,"VDC":.1629,"VBIL":.0556,
        "BNDX":.0505,"EDV":.0431,"VPL":.0346,"VGUS":.0311,"VCSH":.0293}
FIX={"VGSH":.1841,"VDE":.1730,"VGT":.1642,"VDC":.1629,"VBIL":.0556,
     "BNDX":.0505,"VUSB":.0431,"VPL":.0346,"VGUS":.0311,"VCSH":.0293}
OURS={"VBIL":.25,"VGUS":.25,"VUSB":.25,"VFMV":.05,"VGSH":.07,"VSDB":.05}
def bl(a,b,x):
    k=set(a)|set(b)
    return {t:v for t,v in ((t,a.get(t,0)*(1-x)+b.get(t,0)*x) for t in k) if v>1e-4}
BOOKS={"OURS":OURS,"THEIRS (as written)":THEIRS,"THEIRS (leaks patched)":FIX,
       "blend 75/25":bl(OURS,FIX,.25),"blend 60/40":bl(OURS,FIX,.40),
       "blend 50/50":bl(OURS,FIX,.50),"VTI benchmark":{"VTI":.92}}

need=sorted({t for b in BOOKS.values() for t in b})
common=pan["close"][need].dropna()
idx=[i for i in range(len(common)-TOT-2)
     if int((pan["dividends"].reindex(common.index)[["VBIL"]].iloc[i+6:i+TOT]>0).any(axis=1).sum())==2][::2]
print(f"matched windows {len(idx)} | {common.index[0].date()} -> {common.index[-1].date()}")

def sharpe(w,i,credit):
    w=pd.Series(w); w=w[w>0]
    c=pan["close"][list(w.index)].dropna()
    if i+TOT+1>len(c): return np.nan
    c=c.iloc[i:i+TOT+1]; d=pan["dividends"].reindex(c.index)[list(w.index)].fillna(0.0)
    r=sw.simulate_account(c,d,w,capital=250_000,credit=credit,
                          half_spread_bp=hs).returns.dropna().iloc[5:]
    return r.mean()/r.std()*np.sqrt(252) if r.std()>0 else np.nan

# field computed ONCE per (window, branch) and reused for every book
field={}
for credit in ("ex_date","pay_date"):
    for i in idx:
        f=[sharpe(rw,i,credit) for rw in teams.values()]
        f+=[sharpe({t:1/6 for t in rng.choice(eq,6,replace=False)},i,credit)
            for _ in range(66-len(teams))]
        field[(credit,i)]=np.array([x for x in f if np.isfinite(x)])
print("field precomputed")

out={}
for nm,w in BOOKS.items():
    for credit in ("ex_date","pay_date"):
        sh=[];rk=[]
        for i in idx:
            s=sharpe(w,i,credit)
            if not np.isfinite(s): continue
            sh.append(s); rk.append(int((field[(credit,i)]>s).sum())+1)
        sh=np.array(sh); rk=np.array(rk)
        out[(nm,credit)]={"med_Sharpe":np.median(sh),"p10":np.percentile(sh,10),
                          "P(neg)":(sh<0).mean(),"med_rank":np.median(rk),"P(top7)":(rk<=7).mean()}
print("\n"+pd.DataFrame(out).T.round(3).to_string())
print("\n=== blended P(top 7) by assumed P(same-day crediting) ===")
for nm in BOOKS:
    e=out[(nm,"ex_date")]["P(top7)"]; p=out[(nm,"pay_date")]["P(top7)"]
    print(f"  {nm:24s} "+"  ".join(f"{q:.0%}:{q*e+(1-q)*p:5.1%}" for q in (0.5,0.7,0.85)))
