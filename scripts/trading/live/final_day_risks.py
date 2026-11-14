"""Stress the 5 Nov standing: other teams on the 3 Nov file, rivals that traded Thursday, and Friday risk."""
import sys, glob, runpy, io, contextlib, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    g=runpy.run_path("scripts/trading/live/final_day.py")
T,W,st4,st5,base,step,sharpe,final1,ret,dm,fm,today,cashw=[g[k] for k in "T W st4 st5 base step sharpe final1 ret dm fm today cashw".split()]
V=1005343.0
s4=st4["wolfpack"]; me=step(s4,g["hold_r"]); me_s=sharpe(me)
print(f"WolfPack now (cash-fixed, no VDE): {me_s:.2f}")

files=glob.glob("**/*TeamRankings*",recursive=True)
files=[f for f in files if ".venv" not in f]
if files:
    r=pd.read_csv(sorted(files)[-1]); print("\nfile:",sorted(files)[-1],"| columns:",list(r.columns))
    print(r.sort_values([c for c in r.columns if "harpe" in c][0],ascending=False).head(25).to_string(index=False))

print("\n=== book's own Friday risk, same sample ===")
w0=base.copy(); w0["VBIL"]+=0.00495
b=(ret[w0.index]*w0).sum(axis=1)*1e4
print(f"daily bp: mean {b.mean():.2f} sd {b.std():.2f} min {b.min():.1f} 1% {b.quantile(.01):.1f} 5% {b.quantile(.05):.1f} max {b.max():.1f}; last 60d sd {b.tail(60).std():.2f}")
ib=(ret[W['IB Prospects'].index]*W['IB Prospects']).sum(axis=1)*1e4
print(f"IB book daily bp: sd {ib.std():.2f}, min {ib.min():.1f}, corr with ours {b.corr(ib):.2f}")
print("Final Sharpe by Friday book return: "+"  ".join(f"{x:+d}bp {final1(me,(x-0.3)/1e4):.2f}" for x in (-30,-20,-15,-10,-5,0,5,10)))

print("\n=== what each rival needs Friday to pass us, if we earn +3 bp (final %.2f) ==="%final1(me,2.7/1e4))
tgt=final1(me,2.7/1e4)
xs=np.arange(-300,1500,1)/1e4
for k in T:
    if k=="wolfpack": continue
    f=np.array([final1(st5[k],x) for x in xs]); hit=xs[f>tgt]
    print(f"  {T[k][0]:13s} now {sharpe(st5[k]):5.2f} | best attainable {f.max():5.2f} at {xs[f.argmax()]*1e4:+.0f}bp | needs "+(f"{hit.min()*1e4:+.0f}bp or better" if len(hit) else "cannot reach us"))

print("\n=== if rivals moved to bills before Thursday's open, so 5 Nov loss did not happen ===")
locks={"nobody":[], "Drexel":["drexel"], "FIG":["fig"], "FIG+Drexel":["fig","drexel"], "Pioneer+Desy (already above us)":["pioneer","desy"]}
rng=np.random.default_rng(7); NS=40000
BOND=set(fm.index[fm.asset_class.fillna("").str.startswith("Bond")])
ok=[c for c in ret.columns if ret[c].ne(0).sum()>=300]
for lbl,tb in [("drift removed",dm),("with drift",ret)]:
    A=tb.to_numpy(); cols={c:i for i,c in enumerate(tb.columns)}; idx=rng.integers(0,len(tb),NS)
    fr=lambda w:A[idx][:,[cols[c] for c in w.index]]@w.to_numpy()
    print(" ",lbl)
    for name,L in locks.items():
        riv={}
        for k in T:
            if k=="wolfpack": continue
            if k in L:
                bills=pd.Series({"VBIL":.5,"VUSB":.5}); riv[k]=final1(step(st4[k],1.5/1e4),fr(bills))
            else: riv[k]=final1(st5[k],fr(W[k]))
        res={"hold":(sum((riv[k]>final1(me,fr(w0)-.3/1e4)).astype(int) for k in riv)<=4).mean()}
        for f in ok:
            if f in BOND and f not in ["EDV","VGLT","BLV","VCLT"]: continue
            for sz in (.05,.10,.15,.20,.25):
                w=base.copy(); need=sz
                for src in ["VGSH","VTES","VSDM","VUSB","VGUS","VBIL"]:
                    t=min(w[src],need); w[src]-=t; need-=t
                    if need<=1e-9: break
                w[f]=w.get(f,0)+sz
                res[f"{f} {int(sz*100)}%"]=(sum((riv[k]>final1(me,fr(w)-80/V)).astype(int) for k in riv)<=4).mean()
        s=pd.Series(res).sort_values(ascending=False)
        print(f"    {name:32s} hold {res['hold']*100:5.1f}% | best "+", ".join(f"{a} {v*100:.1f}%" for a,v in s.head(3).items()))

print("\n=== cash, by account, at today's close ===")
px=g["cl"]
for nm,sh,c in [("Accounts 1,2,4",{"VBIL":819,"VGUS":819,"VUSB":1250,"VGSH":502,"VSDM":95,"VTES":42},None),("Daksh",{"VBIL":819,"VGUS":819,"VUSB":1250,"VGSH":502,"VSDM":99,"VTES":44},None)]:
    mv=sum(q*px[t] for t,q in sh.items())
    print(f"  {nm}: holdings ${mv:,.0f}")
