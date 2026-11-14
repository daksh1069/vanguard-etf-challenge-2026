"""Friday odds from the official 5 Nov standings. Positions for rivals are the 4 Nov exports."""
import glob, warnings
import numpy as np, pandas as pd, yfinance as yf
import vgdata
warnings.filterwarnings("ignore")
pd.set_option("display.width",220)
r=pd.read_csv("data/private/competition/rankings/TeamRankings_11_05_2026.csv")
old=pd.read_csv("data/private/competition/rankings/TeamRankings_11_03_2026.csv").set_index("Username")
r=r.sort_values("SharpeRatio",ascending=False).reset_index(drop=True); r.index+=1
r["S_3Nov"]=r.Username.map(old.SharpeRatio); r["ret_3Nov"]=r.Username.map(old.Return)
print(r[["Username","Value","SharpeRatio","S_3Nov","Return","ret_3Nov"]].head(16).round(3).to_string())
wp=r[r.Username=="WolfPack"].iloc[0]
print(f"\nWolfPack value {wp.Value:,.2f}. Model at 5 Nov close: no trades about 1,005,997; three 9-VBIL buys about 1,005,967")

MAP={"desy":"Team Desy","pioneer":"Pioneer","coog":"$COOG","quackstreet":"Quack Street","fig":"Ferda Investment Group - FIG","wolfpack":"WolfPack",
     "IB Prospects":"IB Prospects","drexel":"Drexel Diversifiers","gettysburg":"Gettysburg Student Investment Society","arch":"Arch's Angels"}
N3={"desy":26,"pioneer":32,"coog":24,"quackstreet":23,"fig":24,"wolfpack":33,"IB Prospects":32,"drexel":33,"gettysburg":32,"arch":36}
W={};st={}
off=r.set_index("Username")
for k,nm in MAP.items():
    p=pd.read_csv(glob.glob(f"data/private/competition/2026-11-04/{k}/*OpenPositions*")[0])
    V=off.loc[nm,"Value"]; W[k]=p.groupby("Symbol").MarketValueDelayed.sum()/V
    n=N3[k]+2; S=off.loc[nm,"SharpeRatio"]; R=off.loc[nm,"Return"]
    m=np.log(1+R/100)/n; s=abs(m)*np.sqrt(252)/max(abs(S),1e-6)
    st[k]=(n,m,(n-1)*s*s+n*m*m,S)
def final1(state,x):
    N,M,SS,_=state; n2=N+1; M2=(N*M+x)/n2; SS2=SS+x*x
    return M2/np.sqrt(np.maximum(SS2-n2*M2**2,1e-16)/(n2-1))*np.sqrt(252)
tick=sorted({s for w in W.values() for s in w.index})
px=yf.download(tick,start="2025-03-03",end="2026-11-06",auto_adjust=False,progress=False)["Close"].dropna(how="all")
ret=px.pct_change().iloc[1:]; ret=ret[~(ret["VBIL"]<-0.0015)].fillna(0.0)
print(f"sample {len(ret)} days")
rng=np.random.default_rng(8); NS=60000
idx=rng.integers(0,len(ret),NS); A=ret.to_numpy()[idx]; cols={c:i for i,c in enumerate(ret.columns)}
fr=lambda w:A[:,[cols[c] for c in w.index]]@w.to_numpy()
riv={k:final1(st[k],fr(W[k])) for k in MAP if k!="wolfpack"}
me=final1(st["wolfpack"],fr(W["wolfpack"]))
print("median final: "+"  ".join(f"{MAP[k][:12]} {np.median(v):.2f}" for k,v in sorted(riv.items(),key=lambda x:-np.median(x[1]))),f"| WolfPack {np.median(me):.2f}")
print(f"P(top 5 among tracked ten, rivals frozen) = {(sum((riv[k]>me).astype(int) for k in riv)<=4).mean()*100:.2f}%")
print("WolfPack final by Friday return: "+"  ".join(f"{x:+d}bp {final1(st['wolfpack'],x/1e4):.2f}" for x in (-30,-20,-10,-5,0,5,10,20)))
print("\nWhat a rival needs on Friday to finish above us, if we earn +3 bp (final %.2f):"%final1(st["wolfpack"],3e-4))
tgt=final1(st["wolfpack"],3e-4); xs=np.arange(-300,1500,1)/1e4
others=r[~r.Username.isin(MAP.values())].head(6)
for _,x in pd.concat([r[r.Username.isin(MAP.values())&(r.Username!="WolfPack")],others]).sort_values("SharpeRatio",ascending=False).iterrows():
    n=max(N3.get({v:k for k,v in MAP.items()}.get(x.Username,""),31)+2,5) if x.Username in MAP.values() else 35
    m=np.log(1+x.Return/100)/n; s=abs(m)*np.sqrt(252)/max(abs(x.SharpeRatio),1e-6); stt=(n,m,(n-1)*s*s+n*m*m,x.SharpeRatio)
    f=np.array([final1(stt,y) for y in xs]); hit=xs[f>tgt]
    print(f"  {x.Username[:28]:28s} {x.SharpeRatio:5.2f} sd/day {s*1e4:6.1f}bp | best {f.max():5.2f} | "+(f"needs {hit.min()*1e4:+.0f}bp" if len(hit) else "cannot reach us"))
