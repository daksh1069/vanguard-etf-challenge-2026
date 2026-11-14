"""Re-project the competition under the OBSERVED one-business-day crediting lag."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, glob, yfinance as yf
import vgdata
from vgdata import sawtooth as sw, prices as vp
rng=np.random.default_rng(3); pd.set_option("display.width",230)
ds=vgdata.build()
HELD={"VUSB":1250,"VGSH":502,"VGUS":819,"VBIL":819,"VTES":44,"VSDM":99}
pan=vp.fetch_prices(sorted(set(HELD)|set(ds.master.index)|{"VFMV","VSDB"}),force=True)
hs=vgdata.blended_spread(vgdata.estimate_spreads(ds.panel),ds.quotes)["half_spread_bp"]
tr=vp.total_return(pan)
px=pan["close"].iloc[-1]
mv=pd.Series({t:HELD[t]*px[t] for t in HELD}); tot=mv.sum()+24118.01
W=mv/tot                                      # actual live weights
print("live weights:", (W*100).round(2).to_dict(), f"cash {24118.01/tot:.2%}\n")

teams={}; seen=set()
for f in sorted(glob.glob("data/private/competition/2026-09-17/*OpenPositions*.csv")):
    df=pd.read_csv(f); h=pd.util.hash_pandas_object(df,index=False).sum()
    if h in seen: continue
    seen.add(h); w=df.groupby("Symbol")["MarketValueDelayed"].sum()
    w=w[w.index.isin(pan["close"].columns)]
    if len(w): teams[f[-8:-4]]=w/w.sum()
eq=[t for t in ds.master.index if str(ds.master.at[t,"asset_class"]).startswith("Stock")
    and t in tr.columns and tr[t].notna().sum()>=1900]

N=36
common=pan["close"][list(W.index)].dropna()
idx=[i for i in range(len(common)-N-1)
     if int((pan["dividends"].reindex(common.index)[["VBIL"]].iloc[i:i+N]>0).any(axis=1).sum())==2][::2]
def sharpe(w,i,lag):
    w=pd.Series(w); w=w[w>0]
    c=pan["close"][list(w.index)].dropna()
    if i+N>len(c): return np.nan
    c=c.iloc[i:i+N]; d=pan["dividends"].reindex(c.index)[list(w.index)].fillna(0.0)
    cr="ex_date" if lag==0 else "pay_date"
    r=sw.simulate_account(c,d,w,capital=250_000,credit=cr,pay_lag_bdays=max(lag,1),
                          half_spread_bp=hs).returns.dropna()
    return r.mean()/r.std()*np.sqrt(252) if len(r)>5 and r.std()>0 else np.nan

print(f"=== full-window projection, {len(idx)} historical windows, 36 days, 2 ex-dates ===")
field={}
for lag in (0,1,2):
    for i in idx:
        f=[sharpe(rw,i,lag) for rw in teams.values()]
        f+=[sharpe({t:1/6 for t in rng.choice(eq,6,replace=False)},i,lag) for _ in range(66-len(teams))]
        field[(lag,i)]=np.array([x for x in f if np.isfinite(x)])
for lag,lbl in [(0,"same-day"),(1,"ONE-day lag (observed)"),(2,"two-day lag")]:
    s=[];rk=[]
    for i in idx:
        x=sharpe(W,i,lag)
        if np.isfinite(x): s.append(x); rk.append(int((field[(lag,i)]>x).sum())+1)
    s=np.array(s); rk=np.array(rk)
    riv=np.median([np.median([sharpe(w,i,lag) for i in idx]) for w in teams.values()])
    print(f"  {lbl:24s} median Sharpe {np.median(s):5.2f} [p10 {np.percentile(s,10):5.2f}] | "
          f"median rank {np.median(rk):4.1f} | P(top3) {(rk<=3).mean():5.1%} | P(top7) {(rk<=7).mean():5.1%}"
          f" | median rival {riv:.2f}")

# cash cap through the November distribution
d_nov=sum(HELD[t]*pan["dividends"][t][pan["dividends"][t]>0].iloc[-1] for t in HELD)
cash_after=24118.01+d_nov
print(f"\n=== cash cap ===")
print(f"  now: ${24118.01:,.2f} / ${tot:,.2f} = {24118.01/tot:.2%}")
print(f"  after Nov distribution (~${d_nov:,.0f}): ${cash_after:,.2f} / ${tot+d_nov:,.2f} = {cash_after/(tot+d_nov):.2%}")
print(f"  portfolio would have to fall {(1-cash_after/0.10/(tot+d_nov))*100:.2f}% for cash to breach 10%")
