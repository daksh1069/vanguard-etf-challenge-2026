"""Merged 75/25 book: weights, compliance, cleaning, and the rebalance test."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import vgdata
from vgdata import sawtooth as sw, prices as vp
pd.set_option("display.width",235)
ds=vgdata.build()
EXTRA=["VSDM","VDE","VGT","VDC","VBIL","BNDX","EDV","VPL","VGUS","VCSH","VGSH","VUSB","VSDB","VFMV","VTI"]
pan=vp.fetch_prices(sorted(set(EXTRA)|set(ds.master.index)))
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
OURS={"VBIL":.25,"VGUS":.25,"VUSB":.25,"VFMV":.05,"VGSH":.07,"VSDB":.05}
FIX={"VGSH":.1841,"VDE":.1730,"VGT":.1642,"VDC":.1629,"VBIL":.0556,
     "BNDX":.0505,"VUSB":.0431,"VPL":.0346,"VGUS":.0311,"VCSH":.0293}
raw={t:0.75*OURS.get(t,0)+0.25*FIX.get(t,0) for t in set(OURS)|set(FIX)}
raw={t:v for t,v in raw.items() if v>1e-4}
print("=== raw 75/25 blend ===")
print(pd.Series(raw).sort_values(ascending=False).round(4).to_string())
print(f"  invested {sum(raw.values()):.2%}  cash {1-sum(raw.values()):.2%}  positions {len(raw)}")

# clean: drop sub-2% names, redistribute proportionally inside the same total
keep={t:v for t,v in raw.items() if v>=0.02}
scale=sum(raw.values())/sum(keep.values())
clean={t:round(v*scale,4) for t,v in keep.items()}
print("\n=== cleaned (sub-2% names dropped, total invested preserved) ===")
print(pd.Series(clean).sort_values(ascending=False).round(4).to_string())
print(f"  invested {sum(clean.values()):.2%}  cash {1-sum(clean.values()):.2%}  positions {len(clean)}")

SCORED,TOT=31,36
common=pan["close"][sorted(set(raw)|set(clean))].dropna()
idx=[i for i in range(len(common)-TOT-2)
     if int((pan["dividends"].reindex(common.index)[["VBIL"]].iloc[i+6:i+TOT]>0).any(axis=1).sum())==2][::2]
def sharpe(w,i,credit,rebal=None):
    w=pd.Series(w); w=w[w>0]
    c=pan["close"][list(w.index)].dropna()
    if i+TOT+1>len(c): return np.nan
    c=c.iloc[i:i+TOT+1]; d=pan["dividends"].reindex(c.index)[list(w.index)].fillna(0.0)
    if rebal is None:
        r=sw.simulate_account(c,d,w,capital=250_000,credit=credit,half_spread_bp=hs).returns.dropna().iloc[5:]
    else:  # rebalance every `rebal` days back to target, 50% smoothing, costs charged
        vals=[]; cap=250_000; start=0
        while start < len(c)-1:
            seg=c.iloc[start:start+rebal+1]; dseg=d.iloc[start:start+rebal+1]
            if len(seg)<2: break
            p=sw.simulate_account(seg,dseg,w,capital=cap,credit=credit,
                                  half_spread_bp=hs*0.5,commission=10.0)
            vals.append(p.value if not vals else p.value.iloc[1:]*0+p.value.iloc[1:])
            cap=float(p.value.iloc[-1]); start+=rebal
        v=pd.concat(vals); r=v.pct_change().dropna().iloc[5:]
    return r.mean()/r.std()*np.sqrt(252) if len(r)>3 and r.std()>0 else np.nan
print("\n=== does weekly rebalancing help or hurt? (5-day, costs charged) ===")
for nm,w in [("raw blend",raw),("cleaned blend",clean)]:
    for credit in ("ex_date","pay_date"):
        st=np.nanmedian([sharpe(w,i,credit) for i in idx])
        rb=np.nanmedian([sharpe(w,i,credit,rebal=5) for i in idx])
        print(f"  {nm:14s} {credit:9s} static {st:6.3f} | weekly rebal {rb:6.3f} | delta {rb-st:+.3f}")

px=pan["close"].iloc[-1]
W=pd.Series(clean)
ask=px[W.index]*(1+hs.reindex(W.index).fillna(3.0)/1e4)
sh=np.floor(W*250_000/ask); spend=sh*ask
cash=250_000-spend.sum()-10*len(W)
ex=pd.DataFrame({"weight":W.round(4),"price":px[W.index].round(2),"SHARES":sh.astype(int),
                 "cost":spend.round(0),"actual_w":(spend/250_000).round(4)})
print("\n=== MERGED BOOK — per $250,000 account ===")
print(ex.sort_values("weight",ascending=False).to_string())
print(f"\ninvested ${spend.sum():,.0f} | commissions ${10*len(W)} | CASH ${cash:,.0f} = {cash/250_000:.2%}")
print(f"largest position {ex.actual_w.max():.2%} (their 20% rule, platform 25%)")
ex.to_csv("data/processed/merged_book.csv")
