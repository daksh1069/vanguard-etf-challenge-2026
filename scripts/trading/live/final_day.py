"""Status at the 5 Nov close, and what one remaining day can do.

Rolls each team's running Sharpe state from the 3 Nov file through 4 and 5 Nov using
the positions exported on 4 Nov. Rivals may have traded since then, so their marks are
estimates. Friday is drawn from the same joint historical sample as final_two_days.py.
"""
import glob, warnings
import numpy as np, pandas as pd, requests, yfinance as yf
import vgdata
from vgdata.config import HEADERS
warnings.filterwarnings("ignore")
pd.set_option("display.width", 230); pd.set_option("display.max_rows", 300)
D = "data/private/competition/2026-11-04"
T = {"desy": ("Team Desy", 1032405.374532, 5.49, 3.24053745, 26), "pioneer": ("Pioneer", 1027183.23629, 5.38, 2.718323629, 32),
     "coog": ("$COOG", 1012423.4084, 5.22, 1.24234084, 24), "quackstreet": ("Quack Street", 1004284.343412, 4.53, 0.42843434, 23),
     "fig": ("FIG", 1017988.9305, 2.61, 1.79889305, 24), "wolfpack": ("WolfPack", 1004881.6672, 2.32, 0.48816672, 33),
     "IB Prospects": ("IB Prospects", 1012971.443125, 2.13, 1.29714431, 32), "drexel": ("Drexel", 1016398.695924, 1.98, 1.63986959, 33),
     "gettysburg": ("Gettysburg", 1010526.1239, 1.90, 1.05261239, 32), "arch": ("Arch", 1013352.4485, 1.81, 1.33524485, 36)}


def sharpe(state):
    N, M, SS = state
    return M / np.sqrt((SS - N * M * M) / (N - 1)) * np.sqrt(252)


def step(state, r):
    N, M, SS = state
    return (N + 1, (N * M + r) / (N + 1), SS + r * r)


W, st4, cashw = {}, {}, {}
for k, (nm, V, S, R, n) in T.items():
    p = pd.read_csv(glob.glob(f"{D}/{k}/*OpenPositions*")[0])
    p["qty"] = (p.MarketValueDelayed / p.LastPrice).round()
    mv = p.MarketValueDelayed.sum(); day = (p.qty * p.DelayedPriceChange).sum(); cash = V - (mv - day); Vn = mv + cash
    W[k] = p.groupby("Symbol").MarketValueDelayed.sum() / Vn; cashw[k] = cash / Vn
    m = np.log(1 + R / 100) / n; s = m * np.sqrt(252) / S
    st4[k] = step((n, m, (n - 1) * s * s + n * m * m), day / V)

fm = vgdata.fund_master()
tick = sorted(set(fm.index) | {s for w in W.values() for s in w.index} | {"VOO", "VTI"})
raw = yf.download(tick, start="2025-03-03", end="2026-11-06", auto_adjust=False, progress=False)
px = raw["Close"].dropna(how="all")
print("last price date:", px.index[-1].date(), "| previous:", px.index[-2].date())
today = px.pct_change().iloc[-1]
op = raw["Open"].iloc[-1]; cl = px.iloc[-1]

print("\n=== market today, close to close (open to close in brackets) ===")
for t in ["VOO", "VTI", "VGT", "VHT", "VDE", "VPU", "VDC", "VFH", "VNQ", "VWO", "VEA", "EDV", "VGLT", "BND", "VGIT", "VCSH", "VGSH", "VUSB", "VBIL", "VGUS", "VSDM", "VTES"]:
    if t in today.index and today[t] == today[t]:
        print(f"  {t:5s} {today[t]*100:+6.2f}%   ({(cl[t]/op[t]-1)*100:+6.2f}%)")

print("\n=== cross-check against Vanguard's last trade ===")
for t in ["VOO", "VDE", "VGSH", "VBIL"]:
    q = requests.get(f"https://investor.vanguard.com/vmf/api/{t}/delayedPrice", headers=HEADERS, timeout=30).json()["quotes"][0]["equity"]["pricing"]
    print(f"  {t:5s} yfinance {cl[t]:.2f} | Vanguard last {q.get('lastTradePrice')} | previous close {q.get('previousClosePrice', q.get('prevClosePrice'))}")

st5, rows = {}, []
for k, (nm, *_) in T.items():
    w = W[k]; r = float((today.reindex(w.index).fillna(0) * w).sum())
    st5[k] = step(st4[k], r)
    rows.append({"team": nm, "S_3Nov": T[k][2], "S_4Nov": sharpe(st4[k]), "today_bp": r * 1e4, "S_5Nov": sharpe(st5[k]), "cash%": cashw[k] * 100,
                 "top_holdings": ", ".join(f"{a} {b*100:.0f}" for a, b in w.sort_values(ascending=False).head(4).items())})
tab = pd.DataFrame(rows).sort_values("S_5Nov", ascending=False)
print("\n=== standings, positions frozen at the 4 Nov export ===")
print(tab.round(2).to_string(index=False))

# Which position did WolfPack actually hold today?
base = W["wolfpack"]; V = 1005343.0
vde = base.copy(); vde["VGSH"] = vde["VGSH"] - (0.15 - (cashw["wolfpack"] - 0.01)); vde["VDE"] = 0.15
s4 = st4["wolfpack"]
hold_r = float((today.reindex(base.index) * base).sum()) - 30 / V
vde_cc = float((today.reindex(vde.index) * vde).sum()) - 80 / V
vde_oc = float((today.reindex(base.index) * base).sum()) + 0.15 * (cl["VDE"] / op["VDE"] - 1) - float(today["VGSH"]) * (0.15 - (cashw["wolfpack"] - 0.01)) - 80 / V
print("\n=== WolfPack today by what was done Thursday ===")
print(f"  no trade            {float((today.reindex(base.index)*base).sum())*1e4:+6.1f} bp -> Sharpe {sharpe(step(s4,float((today.reindex(base.index)*base).sum()))):.2f}")
print(f"  9 VBIL cash fix     {hold_r*1e4:+6.1f} bp -> Sharpe {sharpe(step(s4,hold_r)):.2f}")
print(f"  VDE 15% from open   {vde_oc*1e4:+6.1f} bp -> Sharpe {sharpe(step(s4,vde_oc)):.2f}")
print(f"  VDE 15% from close  {vde_cc*1e4:+6.1f} bp -> Sharpe {sharpe(step(s4,vde_cc)):.2f}")

# One remaining day
ret = px.pct_change().iloc[1:]; ret = ret[~(ret["VBIL"] < -0.0015)]
hist = ret.notna().sum(); ok = [c for c in ret.columns if hist[c] >= 300]; ret = ret.fillna(0.0)
BOND = set(fm.index[fm.asset_class.fillna("").str.startswith("Bond")]); EQ = [c for c in ret.columns if c not in BOND]
dm = ret.copy(); dm[EQ] = ret[EQ] - ret[EQ].mean()
rng = np.random.default_rng(6); NS = 40000


def final1(state, r):
    N, M, SS = state; n2 = N + 1; M2 = (N * M + r) / n2; SS2 = SS + r * r
    return M2 / np.sqrt(np.maximum(SS2 - n2 * M2 ** 2, 1e-16) / (n2 - 1)) * np.sqrt(252)


wp_states = {"cash-fixed book, no VDE": step(s4, hold_r), "VDE 15% bought at Thursday's open": step(s4, vde_oc)}
for lbl, tb in [("drift removed", dm), ("with historical drift", ret)]:
    A = tb.to_numpy(); cols = {c: i for i, c in enumerate(tb.columns)}; idx = rng.integers(0, len(tb), NS)
    fr = lambda w: A[idx][:, [cols[c] for c in w.index]] @ w.to_numpy()
    riv = {k: final1(st5[k], fr(W[k])) for k in T if k != "wolfpack"}
    print(f"\n=== Friday, {lbl}: rivals' median final Sharpe ===")
    print("  " + "  ".join(f"{T[k][0]} {np.median(v):.2f}" for k, v in sorted(riv.items(), key=lambda x: -np.median(x[1]))))
    for name, state in wp_states.items():
        res = {}
        w0 = base.copy(); w0["VBIL"] += 0.00495
        res["hold"] = (sum((riv[k] > final1(state, fr(w0))).astype(int) for k in riv) <= 4).mean()
        for f in ok:
            if f in BOND and f not in ["EDV", "VGLT", "BLV", "VCLT"]:
                continue
            for sz in (.10, .15, .20, .25):
                w = base.copy(); need = sz
                for src in ["VGSH", "VTES", "VSDM", "VUSB", "VGUS", "VBIL"]:
                    t = min(w[src], need); w[src] -= t; need -= t
                    if need <= 1e-9:
                        break
                w[f] = w.get(f, 0) + sz
                res[f"{f} {int(sz*100)}%"] = (sum((riv[k] > final1(state, fr(w) - 80 / V)).astype(int) for k in riv) <= 4).mean()
        s = pd.Series(res).sort_values(ascending=False)
        print(f"  {name}: hold {res['hold']*100:.1f}% | best " + ", ".join(f"{a} {b*100:.1f}%" for a, b in s.head(5).items()))

print("\n=== what WolfPack needs Friday (book return, bp) to reach each Sharpe ===")
for name, state in wp_states.items():
    print(f"  from {name} (now {sharpe(state):.2f}): " + "  ".join(f"{x:+d}bp->{final1(state,x/1e4):.2f}" for x in (-50, -20, 0, 10, 20, 30, 50, 75, 100, 150)))
