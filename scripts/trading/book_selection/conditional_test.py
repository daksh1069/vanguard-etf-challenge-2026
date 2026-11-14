"""Three tests the merged doc should have contained.

1. demeaned merged book  - does the 16.6% sleeve survive removing the equity premium?
2. P(top N) for N in {4,6,10,15} - is the ranking stable to the unknown cut size?
3. 'Book A, conditionally upgrade on 2 Oct' as a third candidate.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob
import vgdata
from vgdata import sawtooth as sw, prices as vp
rng=np.random.default_rng(11); pd.set_option("display.width",235)
ds=vgdata.build()
pan=vp.fetch_prices(sorted(set(["VSDM","VDE","VGT","VDC","VBIL","BNDX","EDV","VPL",
    "VGUS","VCSH","VGSH","VUSB","VSDB","VFMV","VTI"])|set(ds.master.index)))
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
SCORED,TOT=31,36
A={"VBIL":.248,"VGUS":.2477,"VUSB":.2479,"VGSH":.0758,"VFMV":.0498,"VSDB":.0498}
M={"VBIL":.20,"VUSB":.20,"VGUS":.20,"VGSH":.1149,"VDE":.0442,"VGT":.0423,
   "VDC":.0414,"VFMV":.0385,"VSDB":.0385}
EQ=["VDE","VGT","VDC","VFMV"]
teams={}; seen=set()
for f in sorted(glob.glob("data/private/competition/2026-09-17/*OpenPositions*.csv")):
    df=pd.read_csv(f); h=pd.util.hash_pandas_object(df,index=False).sum()
    if h in seen: continue
    seen.add(h); w=df.groupby("Symbol")["MarketValueDelayed"].sum()
    w=w[w.index.isin(pan["close"].columns)]
    if len(w): teams[f[-8:-4]]=w/w.sum()
tr=vp.total_return(pan)
eqU=[t for t in ds.master.index if str(ds.master.at[t,"asset_class"]).startswith("Stock")
     and t in tr.columns and tr[t].notna().sum()>=1900]

# ---- demeaned price panel: equities keep vol+correlation, lose their drift ----
bond_mu=(tr[["VBIL","VGUS","VUSB"]].dropna().mean(axis=1)).mean()
pan_dm={k:v.copy() for k,v in pan.items()}
for t in EQ:
    r=tr[t].dropna(); dm=r-r.mean()+bond_mu
    px=100*(1+dm).cumprod()
    pan_dm["close"][t]=px.reindex(pan["close"].index).ffill()
    pan_dm["dividends"][t]=0.0

common=pan["close"][sorted(set(A)|set(M))].dropna()
idx=[i for i in range(len(common)-TOT-2)
     if int((pan["dividends"].reindex(common.index)[["VBIL"]].iloc[i+6:i+TOT]>0).any(axis=1).sum())==2][::2]
print(f"matched windows {len(idx)}")

def path(w,i,credit,P=pan):
    w=pd.Series(w); w=w[w>0]
    c=P["close"][list(w.index)].dropna()
    if i+TOT+1>len(c): return None
    c=c.iloc[i:i+TOT+1]; d=P["dividends"].reindex(c.index)[list(w.index)].fillna(0.0)
    return sw.simulate_account(c,d,w,capital=250_000,credit=credit,half_spread_bp=hs)

def sh_of(v):
    r=v.pct_change().dropna().iloc[5:]
    return r.mean()/r.std()*np.sqrt(252) if len(r)>3 and r.std()>0 else np.nan

def conditional(i,credit):
    """Hold A. Under lag, switch to M the day after the FIRST ex-date."""
    pa=path(A,i,credit)
    if pa is None: return np.nan
    if credit=="ex_date":
        return sh_of(pa.value)
    div=pan["dividends"].reindex(pa.value.index)[["VBIL"]]
    exd=[k for k,v in enumerate((div>0).any(axis=1)) if v]
    if not exd: return sh_of(pa.value)
    sw_i=min(exd[0]+1, len(pa.value)-4)
    cap=float(pa.value.iloc[sw_i])
    w=pd.Series(M); w=w[w>0]
    c=pan["close"][list(w.index)].dropna()
    j=c.index.get_loc(pa.value.index[sw_i])
    c2=c.iloc[j:j+ (TOT+1-sw_i)]
    d2=pan["dividends"].reindex(c2.index)[list(w.index)].fillna(0.0)
    p2=sw.simulate_account(c2,d2,w,capital=cap-12*10,credit=credit,half_spread_bp=hs)
    v=pd.concat([pa.value.iloc[:sw_i], p2.value])
    return sh_of(v)

field={}
for credit in ("ex_date","pay_date"):
    for i in idx:
        f=[sh_of(path(rw,i,credit).value) for rw in teams.values() if path(rw,i,credit) is not None]
        f+=[sh_of(path({t:1/6 for t in rng.choice(eqU,6,replace=False)},i,credit).value)
            for _ in range(66-len(teams))]
        field[(credit,i)]=np.array([x for x in f if np.isfinite(x)])

print("\n=== TEST 1: does the 16.6% sleeve survive demeaning? ===")
for nm,w in [("Book A (5% sleeve)",A),("Merged (16.6% sleeve)",M)]:
    for lbl,P in [("real",pan),("demeaned",pan_dm)]:
        s=np.array([x for x in (sh_of(path(w,i,"ex_date",P).value) for i in idx if path(w,i,"ex_date",P) is not None) if np.isfinite(x)])
        s2=np.array([x for x in (sh_of(path(w,i,"pay_date",P).value) for i in idx if path(w,i,"pay_date",P) is not None) if np.isfinite(x)])
        print(f"  {nm:22s} {lbl:9s} same-day {np.median(s):6.3f} | lagged {np.median(s2):6.3f}")

print("\n=== TEST 2+3: P(top N) by cut size, incl. conditional upgrade ===")
CAND={"Book A":A,"Merged":M}
res={}
for nm,w in CAND.items():
    for credit in ("ex_date","pay_date"):
        rk=[]
        for i in idx:
            p=path(w,i,credit)
            if p is None: continue
            s=sh_of(p.value)
            if np.isfinite(s): rk.append(int((field[(credit,i)]>s).sum())+1)
        res[(nm,credit)]=np.array(rk)
for credit in ("ex_date","pay_date"):
    rk=[]
    for i in idx:
        s=conditional(i,credit)
        if np.isfinite(s): rk.append(int((field[(credit,i)]>s).sum())+1)
    res[("Conditional",credit)]=np.array(rk)
rows={}
for (nm,credit),rk in res.items():
    rows[(nm,credit)]={"med_rank":np.median(rk),**{f"P(top{n})":(rk<=n).mean() for n in (4,6,7,10,15)}}
print(pd.DataFrame(rows).T.round(3).to_string())
print("\n=== blended by P(same-day), per cut size ===")
for n in (4,6,7,10,15):
    print(f"\n  cut = top {n}")
    for nm in ("Book A","Merged","Conditional"):
        e=(res[(nm,'ex_date')]<=n).mean(); p=(res[(nm,'pay_date')]<=n).mean()
        print(f"    {nm:12s} "+"  ".join(f"{q:.0%}:{q*e+(1-q)*p:5.1%}" for q in (0.5,0.7,0.85)))
