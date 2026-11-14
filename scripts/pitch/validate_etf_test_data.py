"""Independent validation of data/private/bloomberg/etf_test_data.xlsx (friend's Bloomberg Test A/B/D workbook)."""
import sys, warnings, datetime as dt
import numpy as np, pandas as pd
from openpyxl import load_workbook
warnings.filterwarnings("ignore")
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40)
p = sys.argv[1] if len(sys.argv) > 1 else "data/private/bloomberg/etf_test_data.xlsx"
wb = load_workbook(p, data_only=True)

# ---------- 1. raw monthly blocks
ws = wb["TestA_raw_values"]
blocks = {}
for c in range(1, ws.max_column + 1):
    if ws.cell(3, c).value == "Date":
        name = ws.cell(2, c).value
        hdr = []
        k = c + 1
        while ws.cell(3, k).value not in (None, "Date"):
            hdr.append(ws.cell(3, k).value); k += 1
        rows = []
        for r in range(4, 146):
            d = ws.cell(r, c).value
            if not isinstance(d, (dt.date, dt.datetime)):
                continue
            rows.append([pd.Timestamp(d)] + [ws.cell(r, c + 1 + j).value for j in range(len(hdr))])
        df = pd.DataFrame(rows, columns=["date"] + hdr).set_index("date")
        blocks[name] = df.apply(pd.to_numeric, errors="coerce")
dates = {k: tuple(v.index) for k, v in blocks.items()}
ref = dates["USGG3M Index"]
print("1. RAW DATA INTEGRITY")
print(f"   blocks: {len(blocks)}; months in US block: {len(ref)} ({ref[0].date()} to {ref[-1].date()})")
mis = [k for k, v in dates.items() if v != ref]
print("   blocks whose dates differ from the US block:", mis if mis else "none")
for k, v in blocks.items():
    nn = v.notna().sum().min()
    msg = []
    if "PX_BID" in v and "PX_ASK" in v:
        if "Index" in k or "Govt" in k:
            pass
        elif "Curncy" in k and len(k.split()[0]) == 6:   # spot pairs
            inv = (v.PX_BID > v.PX_ASK).sum(); msg.append(f"bid>ask {inv}")
    if "YLD_YTM_BID" in v:
        inv = (v.YLD_YTM_BID < v.YLD_YTM_ASK).sum(); msg.append(f"bid yld<ask yld {inv}")
        sp = (v.YLD_YTM_BID - v.YLD_YTM_ASK) * 100; msg.append(f"spread bp median {sp.median():.1f} max {sp.max():.1f}")
    stale = (v.iloc[:, 0].diff() == 0).sum()
    msg.append(f"unchanged vs prior month {stale}")
    print(f"   {k:16s} numeric rows {nn:3d} | " + "; ".join(msg))

# ---------- 2. cross-check against Yahoo
print("\n2. CROSS-CHECK AGAINST YAHOO (month-end)")
try:
    import yfinance as yf
    yt = {"EURUSD Curncy": "EURUSD=X", "GBPUSD Curncy": "GBPUSD=X", "USDJPY Curncy": "JPY=X", "USDCAD Curncy": "CAD=X", "USGG3M Index": "^IRX"}
    px = yf.download(list(yt.values()), start="2014-12-01", end="2026-11-10", auto_adjust=False, progress=False)["Close"]
    for k, t in yt.items():
        b = blocks[k]
        mid = (b.PX_BID + b.PX_ASK) / 2
        y = px[t].reindex(mid.index, method="ffill")
        rel = (mid / y - 1) * (1e4 if "Curncy" in k else 0) if "Curncy" in k else (mid - y) * 100
        unit = "bp of price" if "Curncy" in k else "bp of yield (BEY vs Yahoo discount yield)"
        print(f"   {k:14s} vs {t:9s}: median diff {rel.median():+.1f} {unit}, 95% within {rel.abs().quantile(.95):.1f}, max {rel.abs().max():.1f} on {rel.abs().idxmax().date()}")
except Exception as e:
    print("   Yahoo check failed:", e)

# ---------- 3. independent recomputation of Test A
print("\n3. INDEPENDENT RECOMPUTATION OF TEST A (3M, per country, bp/yr net of fee - 0.06%)")
FEE = (0.001 - 0.0006) * 1e4
C = {"DE": ("GTDEM3M Govt", "EURUSD Curncy", "EUR3M Curncy", 1, 1e4, 360), "FR": ("GTFRF3M Govt", "EURUSD Curncy", "EUR3M Curncy", 1, 1e4, 360),
     "UK": ("GTGBP3M Govt", "GBPUSD Curncy", "GBP3M Curncy", 1, 1e4, 365), "JP": ("GTJPY3M Govt", "USDJPY Curncy", "JPY3M Curncy", 0, 100, 365),
     "CA": ("GTCAD3M Govt", "USDCAD Curncy", "CAD3M Curncy", 0, 1e4, 365)}
OVR = {("DE", "2016-12"): -1.03, ("JP", "2026-08"): 1.0493}
us = blocks["USGG3M Index"]
usmm = us.PX_ASK * 360 / 365


def net(code, case="base", tau=0.25, pip=0.0):
    yt, st, ft, direct, scale, basis = C[code]
    y = blocks[yt].YLD_YTM_ASK.copy()
    for (cc, m), v in OVR.items():
        if cc == code:
            y[y.index.to_period("M") == pd.Period(m)] = v
    s, f = blocks[st], blocks[ft]
    if direct:
        smid = (s.PX_BID + s.PX_ASK) / 2
        if case == "base":
            S, F = smid + pip / scale, smid - pip / scale + f.PX_BID / scale
        else:  # conservative
            S, F = s.PX_ASK, s.PX_BID + f.PX_BID / scale
    else:
        umid = (s.PX_BID + s.PX_ASK) / 2
        if case == "base":
            S, F = 1 / (umid - pip / scale), 1 / (umid + pip / scale + f.PX_ASK / scale)
        else:
            S, F = 1 / s.PX_BID, 1 / (s.PX_ASK + f.PX_ASK / scale)
    yy = y / 100 * 360 / basis
    hedged = ((1 + yy * tau) * F / S - 1) / tau * 100
    return (hedged - usmm) * 100 - FEE


ca = wb["TestA_calc"]
col = {"DE": "Y", "FR": "AP", "UK": "BG", "JP": "BX", "CA": "CO"}
colc = {"DE": "W", "FR": "AN", "UK": "BE", "JP": "BV", "CA": "CM"}
idx = [pd.Timestamp(ca[f"A{r}"].value) for r in range(60, 202)]
res = {}
for code in C:
    mine = net(code).reindex(idx)
    theirs = pd.Series([ca[f"{col[code]}{r}"].value for r in range(60, 202)], idx, dtype=float)
    mine_c = net(code, "cons").reindex(idx)
    theirs_c = pd.Series([ca[f"{colc[code]}{r}"].value for r in range(60, 202)], idx, dtype=float)
    d, dc = (mine - theirs).abs().max(), (mine_c - theirs_c).abs().max()
    res[code] = mine
    print(f"   {code}: base max |mine - theirs| = {d:.2e} bp over {theirs.notna().sum()} months; conservative {dc:.2e} bp")
W = {"core": {"DE": 0.20086393088552915, "UK": 0.39913606911447086, "CA": 0.4},
     "ext": {"DE": 0.07685950413223142, "FR": 0.19553719008264464, "UK": 0.15272727272727274, "JP": 0.4, "CA": 0.17487603305785127}}
last5 = [d for d in idx if d > pd.Timestamp("2021-10-31")]


def fund(wts, **kw):
    return sum(w * net(c, **kw).reindex(idx) for c, w in wts.items())


print("\n   Fund 5-year mean net pick-up (bp/yr):            Core     Extended")
for lab, kw in [("their BASE (t = 0.25)", {}), ("their MIDDLE (1 pip)", {"pip": 1.0}),
                ("BASE, exact 3M day count (t = 91.25/360)", {"tau": 91.25 / 360}),
                ("MIDDLE, exact day count", {"pip": 1.0, "tau": 91.25 / 360}),
                ("their CONSERVATIVE", {"case": "cons"})]:
    print(f"   {lab:46s} {fund(W['core'], **kw)[last5].mean():7.2f}  {fund(W['ext'], **kw)[last5].mean():8.2f}")
print("   (their summary sheet: BASE 4.09 / 16.16, MIDDLE 0.90 / 13.03, CONSERVATIVE -38.32 / -20.84)")
print("\n   Per-country 5-year mean, BASE, t = 0.25 vs exact day count:")
for code in C:
    print(f"   {code}: {net(code)[last5].mean():7.2f}  ->  {net(code, tau=91.25/360)[last5].mean():7.2f}")
ex = fund(W["ext"])
print(f"\n   Extended without Japan (weights renormalised): "
      f"{fund({k: v / (1 - 0.4) for k, v in W['ext'].items() if k != 'JP'})[last5].mean():.2f} bp")
yr = ex.groupby(ex.index.year).mean()
print("   Extended BASE by year:", " ".join(f"{y}:{v:+.0f}" for y, v in yr.items()))
cr = fund(W["core"]); yr = cr.groupby(cr.index.year).mean()
print("   Core BASE by year:    ", " ".join(f"{y}:{v:+.0f}" for y, v in yr.items()))

# ---------- 4. the five country sheets
print("\n4. COUNTRY SHEETS (Germany, France, UK, Japan, Canada)")
frames = {}
for s in ["Germany", "France", "UK", "Japan", "Canada"]:
    w = wb[s]
    frames[s] = pd.DataFrame([[c.value for c in row] for row in w.iter_rows(min_row=2, values_only=False)],
                             columns=[c.value for c in w[1]])
same = all(frames[s].equals(frames["Germany"]) for s in frames)
g = frames["Germany"]
print(f"   identical across all five sheets: {same}; rows {len(g)}")
print("   country of incorporation:", g.CNTRY_OF_INCORPORATION.value_counts().head(8).to_dict())
print("   currency:", g.CRNCY.value_counts().head(8).to_dict())
mt = pd.to_datetime(g.MATURITY, errors="coerce")
print(f"   maturities {mt.min().date()} to {mt.max().date()}; zero-amount rows {(pd.to_numeric(g.AMT_OUTSTANDING, errors='coerce') == 0).sum()}")
print("   sample issuers:", g.LONG_COMP_NAME.dropna().astype(str).str[:24].value_counts().head(6).to_dict())

# ---------- 5. Test D field results
print("\n5. TEST D FIELD TEST ON BNDX (values sheet)")
td = wb["TestD_values"]
for r in range(5, 60):
    a, b, c, d = (td.cell(r, k).value for k in range(1, 5))
    if b and d in ("Yes", "No", "Blank"):
        print(f"   {str(a)[:22]:22s} {str(b):32s} {d:5s} {str(c)[:40]}")
