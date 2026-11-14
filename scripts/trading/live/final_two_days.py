"""Cut = exactly top 5. Which position for 5-6 Nov maximises P(top 5)?

Running Sharpe state per team is taken at the 4 Nov close. Two remaining days are
drawn as consecutive historical pairs, jointly across all funds, so rivals move with
us. Candidates comply with the rules: Vanguard only, long only, <=25% per fund, cash<=10%.
"""
import glob, warnings
import numpy as np, pandas as pd, yfinance as yf
import vgdata
warnings.filterwarnings("ignore")
pd.set_option("display.width",230); pd.set_option("display.max_rows",300)
D="data/private/competition/2026-11-04"
T={"desy":("Team Desy",1032405.374532,5.49,3.24053745,26),"pioneer":("Pioneer",1027183.23629,5.38,2.718323629,32),
   "coog":("$COOG",1012423.4084,5.22,1.24234084,24),"quackstreet":("Quack Street",1004284.343412,4.53,0.42843434,23),
   "fig":("FIG",1017988.9305,2.61,1.79889305,24),"wolfpack":("WolfPack",1004881.6672,2.32,0.48816672,33),
   "IB Prospects":("IB Prospects",1012971.443125,2.13,1.29714431,32),"drexel":("Drexel",1016398.695924,1.98,1.63986959,33),
   "gettysburg":("Gettysburg",1010526.1239,1.90,1.05261239,32),"arch":("Arch",1013352.4485,1.81,1.33524485,36)}
W={};st={};cashw={}
for k,(nm,V,S,R,n) in T.items():
    p=pd.read_csv(glob.glob(f"{D}/{k}/*OpenPositions*")[0]); p["qty"]=(p.MarketValueDelayed/p.LastPrice).round()
    mv=p.MarketValueDelayed.sum(); day=(p.qty*p.DelayedPriceChange).sum(); cash=V-(mv-day); Vn=mv+cash
    W[k]=p.groupby("Symbol").MarketValueDelayed.sum()/Vn; cashw[k]=cash/Vn
    m=np.log(1+R/100)/n; s=m*np.sqrt(252)/S; r=day/V
    SS=(n-1)*s*s+n*m*m+r*r; N=n+1; M=(n*m+r)/N
    st[k]=(N,M,SS)
fm=vgdata.fund_master()
tick=sorted(set(fm.index)|{s for w in W.values() for s in w.index})
px=yf.download(tick,start="2025-03-03",end="2026-11-05",auto_adjust=False,progress=False)["Close"].dropna(how="all")
ret=px.pct_change().iloc[1:]
ret=ret[~(ret["VBIL"]<-0.0015)]
hist=ret.notna().sum()
ok=[c for c in ret.columns if hist[c]>=300]
ret=ret.fillna(0.0)
BOND=set(fm.index[fm.asset_class.fillna("").str.startswith("Bond")])
EQ=[c for c in ret.columns if c not in BOND]
dm=ret.copy(); dm[EQ]=ret[EQ]-ret[EQ].mean()
print(f"sample {ret.index[0].date()} -> {ret.index[-1].date()}, {len(ret)} days; {len(ok)} funds with 300+ obs; dropped bond ex-dates")
rng=np.random.default_rng(5); NS=40000
def final(state,r2):
    N,M,SS=state; n2=N+r2.shape[1]; M2=(N*M+r2.sum(1))/n2; SS2=SS+(r2**2).sum(1)
    return M2/np.sqrt(np.maximum(SS2-n2*M2**2,1e-16)/(n2-1))*np.sqrt(252)
base=W["wolfpack"]; V=1005343.0
def tilt(buy):
    w=base.copy(); need=sum(buy.values()); trades=len(buy)
    c=cashw["wolfpack"]-0.01; use=min(max(c,0),need); need-=use
    for src in ["VGSH","VTES","VSDM","VUSB","VGUS","VBIL"]:
        if need<=1e-9: break
        t=min(w[src],need); w[src]-=t; need-=t; trades+=1
    for a,b in buy.items(): w[a]=w.get(a,0)+b
    return w[w>1e-6],trades*4*10/V
def fixonly():
    w=base.copy(); w["VBIL"]+=0.00495; return w,30/V
def build(tb,idx):
    A=tb.to_numpy(); cols={c:i for i,c in enumerate(tb.columns)}
    def team(w):
        r=A[:,[cols[c] for c in w.index]]@w.to_numpy(); return np.stack([r[idx],r[idx+1]],1)
    riv={k:final(st[k],team(W[k])) for k in T if k!="wolfpack"}
    return team,riv
S1=["quackstreet"]; S2=["quackstreet","desy","fig","drexel"]
def probs(wp,riv):
    above=lambda drop:sum((riv[k]>wp).astype(int) for k in riv if k not in drop)
    return {"P5_none_out":(above([])<=4).mean(),"P5_Quack_out":(above(S1)<=4).mean(),"P5_4_out":(above(S2)<=4).mean(),"medS":np.median(wp)}
out={}
for lbl,tb in [("noDrift",dm),("real",ret)]:
    idx=rng.integers(0,len(tb)-1,NS); team,riv=build(tb,idx)
    w0,c0=fixonly(); r=team(w0); r[:,0]-=c0; out[(lbl,"HOLD (cash fix)")]=probs(final(st["wolfpack"],r),riv)
    if lbl=="noDrift":
        print("\nrivals' final Sharpe (no drift): "+"  ".join(f"{T[k][0]} {np.median(v):.2f}" for k,v in riv.items()))
    for f in ok:
        if f in BOND and f not in ["EDV","VGLT","BLV","VCLT","VGIT"]: continue
        for sz in (.05,.10,.15,.20,.25):
            w,c=tilt({f:sz}); r=team(w); r[:,0]-=c
            out[(lbl,f"{f} {int(sz*100)}%")]=probs(final(st["wolfpack"],r),riv)
R=pd.DataFrame(out).T
nd=R.loc["noDrift"].sort_values("P5_none_out",ascending=False); rl=R.loc["real"]
print("\n=== single-fund tilts, ranked by P(top 5) with nobody removed, equity drift removed ===")
show=nd.head(16).join(rl[["P5_none_out"]].rename(columns={"P5_none_out":"P5_real"}))
print(show.round(3).to_string())
print("\nHOLD:",R.loc[("noDrift","HOLD (cash fix)")].round(3).to_dict(),"| real:",R.loc[("real","HOLD (cash fix)")].round(3).to_dict())
tops=[c for c in nd.index if c!="HOLD (cash fix)"][:5]
print("\n=== stability: same candidates on two separate halves of the sample (no drift) ===")
mid=len(dm)//2
for name,tb in [("first half",dm.iloc[:mid]),("second half",dm.iloc[mid:])]:
    idx=rng.integers(0,len(tb)-1,NS); team,riv=build(tb,idx); row={}
    w0,c0=fixonly(); r=team(w0); r[:,0]-=c0; row["HOLD"]=probs(final(st["wolfpack"],r),riv)["P5_none_out"]
    for cand in tops:
        f,sz=cand.split(); w,c=tilt({f:int(sz[:-1])/100}); r=team(w); r[:,0]-=c; row[cand]=probs(final(st["wolfpack"],r),riv)["P5_none_out"]
    print(f"  {name}: "+"  ".join(f"{k} {v:.3f}" for k,v in row.items()))
nd.to_csv("data/processed/final_two_days_tilts.csv")

print("\n=== combinations and timing (no drift | real) ===")
BASK={"VDE 20%":{"VDE":.20},"VDE 15 + EDV 10":{"VDE":.15,"EDV":.10},"VDE 20 + VPU 10":{"VDE":.20,"VPU":.10},
      "VDE 20 + VHT 10":{"VDE":.20,"VHT":.10},"VDE 25 + VDC 10":{"VDE":.25,"VDC":.10},"VDE 25 + VPU 15":{"VDE":.25,"VPU":.15},
      "VDE 25 + VGT 25":{"VDE":.25,"VGT":.25},"VDE 25 + VWO 25":{"VDE":.25,"VWO":.25}}
def evalall(tb):
    idx=rng.integers(0,len(tb)-1,NS); team,riv=build(tb,idx); res={}
    w0,c0=fixonly(); r0=team(w0); r0[:,0]-=c0
    res["HOLD (cash fix)"]=probs(final(st["wolfpack"],r0),riv)
    for nm,b in BASK.items():
        w,c=tilt(b); r=team(w); r[:,0]-=c; res[nm]=probs(final(st["wolfpack"],r),riv)
    # timing variants on VDE 20%
    w,c=tilt({"VDE":.20}); rt=team(w)
    r=r0.copy(); r[:,1]=rt[:,1]-c; res["VDE 20% Friday only"]=probs(final(st["wolfpack"],r),riv)
    # dynamic: VDE Thursday; at Thursday close, if already through (top 5 of the 10) cut back to bills on Friday, else keep
    riv1={k:final(st[k],team(W[k])[:,[0]]) for k in riv}
    r=rt.copy(); r[:,0]-=c
    s1=final(st["wolfpack"],r[:,[0]])
    ahead=sum((riv1[k]>s1).astype(int) for k in riv1)<=4
    r[ahead,1]=r0[ahead,1]-c      # selling back costs another round of commissions
    res["VDE 20%, cut Friday if through"]=probs(final(st["wolfpack"],r),riv)
    r=rt.copy(); r[:,0]-=c
    behind=sum((riv1[k]>s1).astype(int) for k in riv1)>4
    w2,c2=tilt({"VDE":.25,"VPU":.15}); rb=team(w2)
    r[behind,1]=rb[behind,1]-c2
    res["VDE 20%, add VPU Friday if behind"]=probs(final(st["wolfpack"],r),riv)
    return pd.DataFrame(res).T
a=evalall(dm); b=evalall(ret)
print(a.join(b[["P5_none_out","P5_Quack_out"]].rename(columns={"P5_none_out":"none_out_real","P5_Quack_out":"Quack_out_real"})).round(3).to_string())

print("\n=== if FIG and Drexel de-risk Thursday and stop moving (no drift) ===")
idx=rng.integers(0,len(dm)-1,NS); team,riv=build(dm,idx); lock=dict(riv)
for k in ["fig","drexel"]:
    N,M,SS=st[k]; lock[k]=np.full(NS,M/np.sqrt((SS-N*M*M)/(N-1))*np.sqrt(252))
print("  locked at: FIG %.2f, Drexel %.2f"%(lock["fig"][0],lock["drexel"][0]))
w0,c0=fixonly(); r=team(w0); r[:,0]-=c0; print("  HOLD      ",{k:round(v,3) for k,v in probs(final(st["wolfpack"],r),lock).items()})
w,c=tilt({"VDE":.20}); r=team(w); r[:,0]-=c; print("  VDE 20%   ",{k:round(v,3) for k,v in probs(final(st["wolfpack"],r),lock).items()})

print("\n=== what a VDE 20% book looks like, and what we need ===")
w,c=tilt({"VDE":.20}); print((w*100).round(2).to_dict(),"cash %.2f%%"%((1-w.sum())*100),"cost $%.0f"%(c*V))
vde=dm["VDE"]; print("VDE daily sd (sample) %.2f%% | corr with FIG book %.2f | Drexel book %.2f | P(VDE 2-day > +1.5%%) %.1f%%"%(vde.std()*100,
      np.corrcoef(vde,(dm[W["fig"].index]*W["fig"]).sum(axis=1))[0,1],np.corrcoef(vde,(dm[W["drexel"].index]*W["drexel"]).sum(axis=1))[0,1],
      ((vde.to_numpy()[:-1]+vde.to_numpy()[1:])>0.015).mean()*100))
for x in (10,20,30,40,60):
    N,M,SS=st["wolfpack"]; n2=N+2; M2=(N*M+x/1e4)/n2; SS2=SS+2*(x/2/1e4)**2
    print(f"  book gains {x:3d} bp over 2 days, evenly -> our Sharpe {M2/np.sqrt((SS2-n2*M2**2)/(n2-1))*np.sqrt(252):.2f}")
