"""Given the OBSERVED one-day lag and 10 realised days, which book is best for the remaining 24?

Final Sharpe = realised returns 18 Sep..2 Oct (actual book) + forward 24 days (candidate book),
forward drawn from historical windows aligned so the single remaining ex-date sits where
2 Nov does (day 21 of 24), credited one business day later. Real AND demeaned.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob
import vgdata
from vgdata import sawtooth as sw, prices as vp
rng=np.random.default_rng(9); pd.set_option("display.width",230)
ds=vgdata.build()
HELD={"VUSB":1250,"VGSH":502,"VGUS":819,"VBIL":819,"VTES":44,"VSDM":99}
CASH=24118.01
EQ=["VFMV","VDE","VGT","VDC","VYM"]
pan=vp.fetch_prices(sorted(set(HELD)|set(EQ)|set(ds.master.index)))
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
tr=vp.total_return(pan)

# ---- realised: actual account 18 Sep -> 2 Oct with 1-day lag ----
cl=pan["close"][list(HELD)].loc["2026-09-18":"2026-10-02"]
dv=pan["dividends"][list(HELD)].reindex(cl.index).fillna(0.0)
tot=sum(HELD[t]*dv[t].sum() for t in HELD)
val=pd.Series({d: sum(HELD[t]*cl.loc[d,t] for t in HELD)+23409.47+(tot if d>=pd.Timestamp("2026-10-02") else 0)
               for d in cl.index})
REAL=val.pct_change().dropna().to_numpy()
V0=float(val.iloc[-1])
print(f"realised {len(REAL)} days, Sharpe so far {REAL.mean()/REAL.std()*np.sqrt(252):+.2f}\n")

cur_w=pd.Series({t:HELD[t]*pan['close'][t].iloc[-1]/V0 for t in HELD})
def book(extra):
    """take `extra` weights out of VGSH (then VTES/VSDM) and give them to equities"""
    w=cur_w.copy(); need=sum(extra.values())
    for src in ["VGSH","VSDM","VTES"]:
        take=min(need,w[src]); w[src]-=take; need-=take
    for k,v in extra.items(): w[k]=w.get(k,0)+v
    return w[w>1e-5]
CANDS={
 "hold as is":(cur_w,0),
 "+3% VFMV":(book({"VFMV":.03}),2),
 "+5% VFMV":(book({"VFMV":.05}),2),
 "+8% VFMV":(book({"VFMV":.08}),2),
 "+3% each VDE/VGT/VDC":(book({"VDE":.03,"VGT":.03,"VDC":.03}),4),
 "+5% VYM":(book({"VYM":.05}),2),
}
# demeaned copy: equities keep vol/corr, lose drift
base_mu=tr[["VBIL","VGUS","VUSB"]].dropna().mean(axis=1).mean()
pdm={k:v.copy() for k,v in pan.items()}
for t in EQ:
    r=tr[t].dropna(); pdm["close"][t]=(100*(1+(r-r.mean()+base_mu)).cumprod()).reindex(pan["close"].index).ffill()
    pdm["dividends"][t]=0.0

ref=pan["close"][sorted(set(HELD)|set(EQ))].dropna()
ex=[k for k,v in enumerate((pan["dividends"].reindex(ref.index)[["VBIL"]]>0).any(axis=1)) if v]
starts=[p-21 for p in ex if p-21>=0 and p-21+25<=len(ref)]
print(f"{len(starts)} historical forward windows\n")

def fwd(w,s,P,ntrades):
    c=P["close"][list(w.index)].reindex(ref.index).iloc[s:s+25]
    d=P["dividends"][list(w.index)].reindex(c.index).fillna(0.0)
    p=sw.simulate_account(c,d,w/w.sum()*(1-CASH/V0),capital=V0,credit="pay_date",pay_lag_bdays=1,
                          half_spread_bp=hs,commission=0.0)
    r=p.returns.dropna().to_numpy().copy()
    r[0]-= (10*ntrades)/V0          # switching commissions land on the first forward day
    return r
def full(w,s,P,n):
    r=np.concatenate([REAL,fwd(w,s,P,n)]); return r.mean()/r.std()*np.sqrt(252)

out={}
for nm,(w,n) in CANDS.items():
    a=np.array([full(w,s,pan,n) for s in starts]); b=np.array([full(w,s,pdm,n) for s in starts])
    out[nm]={"real_median":np.median(a),"real_p10":np.percentile(a,10),"demeaned_median":np.median(b),
             "P(final>2)":(a>2).mean(),"trades":n}
print(pd.DataFrame(out).T.round(3).to_string())
