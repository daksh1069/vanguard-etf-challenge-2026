"""Isolate WHY rebalancing hurts under Sharpe: costs, or transition variance?

Runs weekly rebalancing at full cost, at zero cost, and with 50% smoothing.
If zero-cost rebalancing still loses, the mechanism is variance, not turnover -
which is the objection Book B's turnover argument does not answer.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import vgdata
from vgdata import sawtooth as sw, prices as vp
pd.set_option("display.width",230)
ds=vgdata.build()
pan=vp.fetch_prices(sorted(set(["VDE","VGT","VDC","VBIL","VGUS","VGSH","VUSB","VSDB","VFMV"])|set(ds.master.index)))
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
SCORED,TOT=31,36
A={"VBIL":.248,"VGUS":.2477,"VUSB":.2479,"VGSH":.0758,"VFMV":.0498,"VSDB":.0498}
M={"VBIL":.20,"VUSB":.20,"VGUS":.20,"VGSH":.1149,"VDE":.0442,"VGT":.0423,
   "VDC":.0414,"VFMV":.0385,"VSDB":.0385}

def walk(w, c, d, credit, rebal=None, smooth=1.0, comm=10.0, spread=True):
    """Daily account walk. rebal=None -> buy and hold. Otherwise re-target every
    `rebal` days, moving `smooth` of the way to target, charging comm+spread."""
    w=pd.Series(w); w=w[w>0]; tick=list(w.index)
    hsx=(hs.reindex(tick).fillna(3.0) if spread else pd.Series(0.0,index=tick))
    px=c[tick]; dv=d[tick]
    p0=px.iloc[0]*(1+hsx/1e4)
    shares=np.floor(w*250_000/p0)
    cash=250_000-float((shares*p0).sum())-comm*len(w)
    pend={}; vals=[]
    for k,(dt,row) in enumerate(px.iterrows()):
        amt=float((dv.loc[dt]*shares).sum())
        if amt:
            tgt = dt if credit=="ex_date" else (px.index[min(k+2,len(px)-1)])
            pend[tgt]=pend.get(tgt,0.0)+amt
        cash+=pend.pop(dt,0.0)
        val=float((shares*row).sum())+cash
        if rebal and k>0 and k%rebal==0 and k<len(px)-2:
            cur=(shares*row)/val
            tgt=w*(val/ (val))            # target weights (of total value)
            new=cur+smooth*(w-cur)
            desired=np.floor(new*val/row)
            trades=int((desired!=shares).sum())
            turn=float((abs(desired-shares)*row).sum())
            cost=comm*trades + turn*float(hsx.mean())/1e4
            cash=val-float((desired*row).sum())-cost
            shares=desired
            val=float((shares*row).sum())+cash
        vals.append(val)
    v=pd.Series(vals,index=px.index)
    r=v.pct_change().dropna().iloc[5:]
    return r.mean()/r.std()*np.sqrt(252) if len(r)>3 and r.std()>0 else np.nan

common=pan["close"][sorted(set(A)|set(M))].dropna()
idx=[i for i in range(len(common)-TOT-2)
     if int((pan["dividends"].reindex(common.index)[["VBIL"]].iloc[i+6:i+TOT]>0).any(axis=1).sum())==2][::2]
print(f"matched windows {len(idx)}\n")
rows={}
for bn,bw in [("Book A",A),("Merged",M)]:
    for credit in ("ex_date","pay_date"):
        res={}
        for lbl,kw in [("static",dict(rebal=None)),
                       ("weekly, full cost",dict(rebal=5,smooth=1.0)),
                       ("weekly, 50% smooth",dict(rebal=5,smooth=0.5)),
                       ("weekly, ZERO cost",dict(rebal=5,smooth=1.0,comm=0.0,spread=False))]:
            s=[]
            for i in idx:
                c=common.iloc[i:i+TOT+1]; d=pan["dividends"].reindex(c.index).fillna(0.0)
                v=walk(bw,c,d,credit,**kw)
                if np.isfinite(v): s.append(v)
            res[lbl]=np.median(s)
        rows[(bn,credit)]=res
print(pd.DataFrame(rows).T.round(3).to_string())
print("\nIf 'weekly, ZERO cost' still trails 'static', the loss is transition")
print("variance entering the Sharpe denominator - not turnover cost.")
