"""Final-week position analysis from open positions + prices (4 Nov 2026).

Uses TeamRankings_11_03 for each team's displayed Sharpe/return, the 11_4 open
positions for current holdings, and the scoring rule verified on 4 Nov:
rf=0, all days count, entry day scored from the starting capital.
"""
import glob, warnings
import numpy as np, pandas as pd, yfinance as yf
warnings.filterwarnings("ignore")
pd.set_option("display.width",230); pd.set_option("display.max_rows",300)
D="data/private/competition/2026-11-04"
#        folder        name        value_3Nov      sharpe return% n_days(first trade -> 3 Nov, entry scored)
T={"desy":("Team Desy",1032405.374532,5.49,3.24053745,26),
   "pioneer":("Pioneer",1027183.23629,5.38,2.718323629,32),
   "coog":("$COOG",1012423.4084,5.22,1.24234084,24),
   "quackstreet":("Quack Street",1004284.343412,4.53,0.42843434,23),
   "fig":("FIG",1017988.9305,2.61,1.79889305,24),
   "wolfpack":("WolfPack",1004881.6672,2.32,0.48816672,33),
   "IB Prospects":("IB Prospects",1012971.443125,2.13,1.29714431,32),
   "drexel":("Drexel Div.",1016398.695924,1.98,1.63986959,33),
   "gettysburg":("Gettysburg",1010526.1239,1.90,1.05261239,32),
   "arch":("Arch's Angels",1013352.4485,1.81,1.33524485,36)}
pos={}
for k in T:
    p=pd.read_csv(glob.glob(f"{D}/{k}/*OpenPositions*")[0])
    p["qty"]=(p.MarketValueDelayed/p.LastPrice).round()
    p["acct"]=(p.Symbol<p.Symbol.shift(1)).cumsum()+1     # rows restart alphabetically per account
    pos[k]=p
print("=== A. cash and current book, aligned to the 3 Nov close, then 4 Nov return ===")
rows=[];W={}
for k,(nm,V,S,R,n) in T.items():
    p=pos[k]; mv_now=p.MarketValueDelayed.sum(); day=(p.qty*p.DelayedPriceChange).sum()
    cash=V-(mv_now-day); Vn=mv_now+cash
    a=p.groupby("acct").MarketValueDelayed.sum()
    acct_cash=[(Vn/len(a)-x)/(Vn/len(a))*100 for x in a]
    W[k]=(p.groupby("Symbol").MarketValueDelayed.sum()/Vn)
    bond=sum(W[k].get(s,0) for s in ["VBIL","VGUS","VUSB","VGSH","VSDM","VTES","BSV","VCSH","VTIP","VBCA","VGIT"])
    rows.append({"team":nm,"Sharpe":S,"ret_%":R,"cash_%":cash/Vn*100,"max_acct_cash_%":max(acct_cash),"accts":len(a),
                 "short_bonds_%":bond*100,"4Nov_bp":day/V*1e4})
A=pd.DataFrame(rows).set_index("team"); print(A.round(2).to_string())

tick=sorted({s for w in W.values() for s in w.index}|{"VOO","VTI"})
px=yf.download(tick,start="2026-03-25",end="2026-11-05",auto_adjust=False,progress=False)["Close"].dropna(how="all")
ret=px.pct_change().iloc[1:]
isex=ret["VBIL"]<-0.0015
print(f"\nreturn sample {ret.index[0].date()} -> {ret.index[-1].date()}, {len(ret)} days, dropping {int(isex.sum())} bond ex-dates: {[str(d.date()) for d in ret.index[isex]]}")
ret=ret[~isex].fillna(0.0)
EQ=[c for c in ret.columns if c not in ["VBIL","VGUS","VUSB","VGSH","VSDM","VTES","BSV","VCSH","VTIP","VBCA","VGIT","BNDX","BND","VCIT","VGLT","VTG"]]
dm=ret.copy(); dm[EQ]=ret[EQ]-ret[EQ].mean()

print("\n=== B. forward daily vol of each current book (bp/day) vs what the Sharpe implies so far ===")
state={}
for k,(nm,V,S,R,n) in T.items():
    m=np.log(1+R/100)/n; s=m*np.sqrt(252)/S
    fw=(ret[W[k].index]*W[k]).sum(axis=1).std()
    state[k]=(n,m,s)
    print(f"  {nm:14s} n={n:2d} mean {m*1e4:5.2f}bp sd {s*1e4:6.2f}bp | current book vol {fw*1e4:6.2f}bp/day ({fw*np.sqrt(252)*100:5.2f}%/yr)")

def upd(n,m,s,rs):
    """roll running mean/sd forward by the returns in rs (array, last axis days)."""
    SS=(n-1)*s**2+n*m**2
    N=n+rs.shape[-1]; M=(n*m+rs.sum(-1))/N; SS2=SS+(rs**2).sum(-1)
    var=(SS2-N*M**2)/(N-1)
    return M/np.sqrt(var)*np.sqrt(252)
rng=np.random.default_rng(11)
nd=len(ret); starts=rng.integers(0,nd-1,20000)
def sim(table,books,extra_cost=None):
    """two more days drawn as consecutive historical pairs, jointly across teams."""
    fin={}
    for k in T:
        w=books[k]; r=(table[w.index].to_numpy()*w.to_numpy()).sum(1)
        pair=np.stack([r[starts],r[starts+1]],1)
        d4=np.full((len(starts),1),A.loc[T[k][0],"4Nov_bp"]/1e4)
        cost=np.zeros_like(pair)
        if extra_cost and k in extra_cost: cost[:,0]=-extra_cost[k]/T[k][1]
        n,m,s=state[k]
        fin[k]=upd(n,m,s,np.concatenate([d4,pair+cost],1))
    F=pd.DataFrame(fin)
    return F
print("\n=== C. Where everyone lands by Friday's close if nobody trades (20k joint draws) ===")
for lbl,tb in [("real",ret),("equity drift removed",dm)]:
    F=sim(tb,W); rk=F.rank(axis=1,ascending=False)
    out=pd.DataFrame({"median_final":F.median(),"p10":F.quantile(.1),"p90":F.quantile(.9)}).rename(index={k:T[k][0] for k in T})
    print(f"\n[{lbl}]"); print(out.round(2).to_string())
    wr=rk["wolfpack"]; print("  our final rank within these 10: "+"  ".join(f"#{i}:{(wr==i).mean():.1%}" for i in range(3,10)))
    print(f"  P(we beat FIG) {(F.wolfpack>F.fig).mean():.1%} | P(IB passes us) {(F['IB Prospects']>F.wolfpack).mean():.1%} | P(Drexel passes) {(F.drexel>F.wolfpack).mean():.1%} | P(Gettysburg passes) {(F.gettysburg>F.wolfpack).mean():.1%}")
print("\n  IB start-date sensitivity (n=24/28/32/36):",[round(float(upd(x,np.log(1.0129714)/x,np.log(1.0129714)/x*np.sqrt(252)/2.13,np.zeros((1,3)))[0]),2) for x in (24,28,32,36)])

print("\n=== D. Our options for the last two days (decided before Thursday's open) ===")
base=W["wolfpack"].copy()
def alt(mv):
    w=base.copy()
    for a,b in mv.items(): w[a]=w.get(a,0)+b
    return w
fix=alt({"VBIL":0.0066*3/4})   # 9 VBIL in each of the 3 over-cap accounts ~ $680 x3 of team value
opts={"hold, no fix":(base,0),"cash fix only (9 VBIL in 3 accts)":(fix,30),
      "fix + 5% VGSH->VOO":(alt({"VBIL":0.0050,"VGSH":-.05,"VOO":.05}),110),
      "fix + 11.5% VGSH->VOO":(alt({"VBIL":0.0050,"VGSH":-.1149,"VOO":.1149}),110),
      "fix + 5% cash->VOO":(alt({"VOO":.0545}),40),
      "fix + 5% VGSH->VDE":(alt({"VBIL":0.0050,"VGSH":-.05,"VDE":.05}),110)}
res={}
for nm,(w,c) in opts.items():
    for lbl,tb in [("real",ret),("no drift",dm)]:
        b=dict(W); b["wolfpack"]=w
        F=sim(tb,b,{"wolfpack":c}); r=F.rank(axis=1,ascending=False).wolfpack
        res[(nm,lbl)]={"median":F.wolfpack.median(),"P(top5)":(r<=5).mean(),"P(top6)":(r<=6).mean(),"P(top7)":(r<=7).mean(),"P(top10)":(r<=10).mean()}
print(pd.DataFrame(res).T.round(3).to_string())

print("\n=== E. Hindsight: the same book entered on different days, scored by the verified rule ===")
HELD={"VUSB":5000,"VGSH":2008,"VGUS":3276,"VBIL":3276,"VTES":170,"VSDM":384}
OCT={"VUSB":.181,"VGSH":.183,"VGUS":.226,"VBIL":.218,"VTES":.194,"VSDM":.188}
NOV={"VBIL":.2391,"VGSH":.1889,"VGUS":.2442,"VSDM":.1904,"VTES":.2319,"VUSB":.1826}
cl=yf.download(list(HELD),start="2026-09-18",end="2026-11-04",auto_adjust=False,progress=False)["Close"].dropna(how="all")
idx=list(cl.index)
def run(entry,cap=1_000_000.0,comm=240):
    e=idx.index(pd.Timestamp(entry))
    w={t:HELD[t]*cl[t].iloc[0]/1_000_000 for t in HELD}
    q={t:np.floor(w[t]*cap/cl[t].iloc[e]) for t in HELD}
    cash=cap-comm-sum(q[t]*cl[t].iloc[e] for t in HELD)
    v=[]
    for k in range(e,len(idx)):
        d=idx[k]; c=cash
        if d>=pd.Timestamp("2026-10-02") and e<idx.index(pd.Timestamp("2026-10-01")): c+=sum(q[t]*OCT[t] for t in q)
        if d>=pd.Timestamp("2026-11-03"): c+=sum(q[t]*NOV[t] for t in q)
        v.append(sum(q[t]*cl[t].iloc[k] for t in q)+c)
    v=pd.Series(v,index=idx[e:]); r=np.r_[v.iloc[0]/cap-1,v.pct_change().dropna().to_numpy()]
    return r.mean()/r.std()*np.sqrt(252),(v.iloc[-1]/cap-1)*100,len(r)
for e in ["2026-09-18","2026-09-23","2026-09-29","2026-09-30","2026-10-01","2026-10-02","2026-10-05"]:
    s,rr,nn=run(e); print(f"  enter {e}: Sharpe at 3 Nov {s:5.2f} | return {rr:+.3f}% | n={nn}")
