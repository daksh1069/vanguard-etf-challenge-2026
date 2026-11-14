"""Settled configuration: DELAY reading, series anchored at the entry timestamp.
Regenerates every headline figure so the document is internally consistent."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob
import vgdata
from vgdata import sawtooth as sw, prices as vp
rng=np.random.default_rng(5); pd.set_option("display.width",230)
ds=vgdata.build()
pan=vp.fetch_prices(sorted(set(["VSDM","VDE","VGT","VDC","VBIL","BNDX","EDV","VPL","VGUS",
                                "VCSH","VGSH","VUSB","VSDB","VFMV","VTI"])|set(ds.master.index)))
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
A=pd.Series({"VBIL":.248,"VGUS":.2477,"VUSB":.2479,"VGSH":.0758,"VFMV":.0498,"VSDB":.0498})
B={"VSDM":.1841,"VDE":.1730,"VGT":.1642,"VDC":.1629,"VBIL":.0556,"BNDX":.0505,"EDV":.0431,"VPL":.0346,"VGUS":.0311,"VCSH":.0293}
M={"VBIL":.20,"VUSB":.20,"VGUS":.20,"VGSH":.1149,"VDE":.0442,"VGT":.0423,"VDC":.0414,"VFMV":.0385,"VSDB":.0385}
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
N=36
common=pan["close"][sorted(set(A.index)|set(B)|set(M))].dropna()
idx=[i for i in range(len(common)-N-1)
     if int((pan["dividends"].reindex(common.index)[["VBIL"]].iloc[i:i+N]>0).any(axis=1).sum())==2][::2]
print(f"{len(idx)} windows x {N} trading days, 2 ex-dates, DELAY reading, anchored at entry\n")

def stats(w,i,credit):
    w=pd.Series(w); w=w[w>0]
    c=pan["close"][list(w.index)].dropna()
    if i+N>len(c): return None
    c=c.iloc[i:i+N]; d=pan["dividends"].reindex(c.index)[list(w.index)].fillna(0.0)
    p=sw.simulate_account(c,d,w,capital=250_000,credit=credit,half_spread_bp=hs)
    r=p.returns.dropna()          # NO .iloc[5:] - delay reading
    if len(r)<6 or r.std()==0: return None
    return (r.mean()/r.std()*np.sqrt(252), r.std()*np.sqrt(252)*100,
            ((1+r.mean())**252-1)*100)

field={}
for credit in ("ex_date","pay_date"):
    for i in idx:
        f=[stats(rw,i,credit) for rw in teams.values()]
        f=[x[0] for x in f if x]
        f+=[stats({t:1/6 for t in rng.choice(eq,6,replace=False)},i,credit)[0]
            for _ in range(66-len(teams))
            if stats({t:1/6 for t in rng.choice(eq,6,replace=False)},i,credit)]
        field[(credit,i)]=np.array([x for x in f if np.isfinite(x)])

out={}
for nm,w in [("Book A (ours)",A),("Book B",B),("Merged",M),("VTI",{"VTI":.92})]:
    for credit,cl in [("ex_date","same-day"),("pay_date","lagged")]:
        S=[];V=[];R=[];rk=[]
        for i in idx:
            r=stats(w,i,credit)
            if not r: continue
            S.append(r[0]); V.append(r[1]); R.append(r[2])
            rk.append(int((field[(credit,i)]>r[0]).sum())+1)
        rk=np.array(rk)
        out[(nm,cl)]={"Sharpe":np.median(S),"ann_vol_%":np.median(V),"ann_ret_%":np.median(R),
                      "P(neg)":(np.array(S)<0).mean(),"med_rank":np.median(rk),
                      "P(top7)":(rk<=7).mean()}
print(pd.DataFrame(out).T.round(3).to_string())
rivals=[np.median([stats(w,i,"ex_date")[0] for i in idx if stats(w,i,"ex_date")]) for w in teams.values()]
print(f"\n17 real rivals, same-day: best {max(rivals):.2f} | median {np.median(rivals):.2f} | worst {min(rivals):.2f}")
