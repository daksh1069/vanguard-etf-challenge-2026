"""Hedged 1-3y international government bond returns from real prices, all of ISHG's currencies hedged. No new Bloomberg pulls.

Bond returns  : ISHG total return (Yahoo), the real unhedged 1-3y fund.
Major FX      : EUR, JPY, GBP, CAD, AUD spot and 1-month forwards from the team's Bloomberg file (2015 onward, NY close).
Small FX      : KRW, ILS, SGD, NZD, NOK, DKK, SEK spot from Yahoo; hedge carry from the 3-month rate gap (FRED / OECD),
                i.e. covered interest parity without the cross-currency basis. Checked against real forwards on the majors.
Hedged return = ISHG return - sum_c w_c * spot return_c + sum_c w_c * carry_c, then +0.25%/yr to move ISHG's 0.35% fee to 0.10%.
Weights       : ISHG's 5 Nov 2026 currency mix (team's docs). KRW only recently entered the index, so the main case leaves it out.
"""
import io, contextlib, runpy, warnings
import numpy as np, pandas as pd, yfinance as yf
warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("scripts/pitch/validate_etf_test_data.py", run_name="v")
B = g["blocks"]
mk = lambda s: s.groupby(s.index.to_period("M")).last()

W = {"EUR": 55.53, "JPY": 9.12, "GBP": 7.27, "CAD": 4.57, "AUD": 4.54, "KRW": 4.52, "ILS": 4.40, "SGD": 3.32, "NZD": 2.05, "NOK": 1.59, "DKK": 1.51, "SEK": 1.28}
MAJ = {"EUR": ("EURUSD Curncy", "EUR1M Curncy", 1, 1e4), "JPY": ("USDJPY Curncy", "JPY1M Curncy", 0, 100), "GBP": ("GBPUSD Curncy", "GBP1M Curncy", 1, 1e4),
       "CAD": ("USDCAD Curncy", "CAD1M Curncy", 0, 1e4), "AUD": ("AUDUSD Curncy", "AUD1M Curncy", 1, 1e4)}
YFX = {"EUR": ("EURUSD=X", 1), "JPY": ("JPY=X", 0), "GBP": ("GBPUSD=X", 1), "CAD": ("CAD=X", 0), "AUD": ("AUDUSD=X", 1), "KRW": ("KRW=X", 0),
       "ILS": ("ILS=X", 0), "SGD": ("SGD=X", 0), "NZD": ("NZDUSD=X", 1), "NOK": ("NOK=X", 0), "DKK": ("DKK=X", 0), "SEK": ("SEK=X", 0)}
OECD = {"US": "US", "EUR": "EZ", "JPY": "JP", "GBP": "GB", "CAD": "CA", "AUD": "AU", "KRW": "KR", "ILS": "IL", "SGD": "SG", "NZD": "NZ", "NOK": "NO", "DKK": "DK", "SEK": "SE"}


def fred(sid):
    try:
        d = pd.read_csv(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
        d.columns = ["date", "v"]
        s = pd.to_numeric(d.v, errors="coerce")
        s.index = pd.to_datetime(d.date)
        return mk(s.dropna())
    except Exception:
        return None


rates = {}
for c, cc in OECD.items():
    s = fred(f"IR3TIB01{cc}M156N")
    rates[c] = s
    print(f"  3M rate {c}: " + (f"{s.index[0]} to {s.index[-1]}" if s is not None and len(s) else "NOT AVAILABLE"))
R3 = pd.DataFrame({c: s for c, s in rates.items() if s is not None}).ffill(limit=3)

# spot: Bloomberg (majors, 2015+) and Yahoo (all, 2013+); both as USD per unit of foreign currency
yfx = yf.download([t for t, _ in YFX.values()], start="2013-07-01", end="2026-11-01", auto_adjust=False, progress=False)["Close"]
SY = pd.DataFrame({c: (mk(yfx[t]) if d else 1 / mk(yfx[t])) for c, (t, d) in YFX.items()})
SB, FB = {}, {}
for c, (sp, fp, d, sc) in MAJ.items():
    m = mk((B[sp].PX_BID + B[sp].PX_ASK) / 2)
    f = m + mk((B[fp].PX_BID + B[fp].PX_ASK) / 2) / sc
    SB[c], FB[c] = (m, f) if d else (1 / m, 1 / f)
SB, FB = pd.DataFrame(SB), pd.DataFrame(FB)

px = yf.download(["ISHG", "VGSH", "BSV", "BNDX", "BIL", "0P00011WU8"], start="2013-07-01", end="2026-11-01", auto_adjust=True, progress=False)["Close"]
RF = mk(px).pct_change()
tb = (mk(B["USGG3M Index"].PX_ASK).shift(1) / 1200)
dtb3 = fred("DTB3")
tb = tb.combine_first(dtb3.shift(1) / 1200) if dtb3 is not None else tb

# carry: real forwards where we have them, CIP from 3M rates elsewhere
cip = pd.DataFrame({c: (R3["US"] - R3[c]) / 1200 for c in W if c in R3}).shift(1)
if "SGD" not in cip:            # no Singapore 3M rate on FRED: hedge SGD's FX moves but credit zero carry (slightly understates the return)
    cip["SGD"] = 0.0
real = (FB / SB - 1).shift(1)
carry = cip.copy()
for c in real:
    carry[c] = real[c].combine_first(cip.get(c))
spot = SY.copy()
for c in SB:
    spot[c] = SB[c].combine_first(SY[c])          # Bloomberg NY close where available
s_ret = spot.pct_change()

# check: rate-gap carry vs real forwards on the majors (difference = basis effect + rate-definition noise)
print("\nRate-gap estimate vs real 1M forwards, majors, 2015-2026 (annualised % a year; positive = real hedge paid more):")
for c in real:
    d = (real[c] - cip[c]).dropna() * 1200
    print(f"  {c}: mean {d.mean():+.2f}, monthly sd {d.std():.2f}")

idx = RF.index[(RF.index >= pd.Period("2013-10", "M")) & (RF.index <= pd.Period("2026-10", "M"))]


def hedged(ccys, idx=idx):
    w = pd.Series({c: W[c] for c in ccys}) / 100
    sr, ca = s_ret.reindex(idx)[w.index], carry.reindex(idx)[w.index]
    return RF["ISHG"].reindex(idx) - (sr * w).sum(axis=1, min_count=len(w)) + (ca * w).sum(axis=1, min_count=len(w)) + 0.0025 / 12


ALL = list(W)
EXK = [c for c in W if c != "KRW"]
series = {"Hedged ISHG, 11 currencies (ex KRW), fee 0.10%": hedged(EXK), "Hedged ISHG, all 12 currencies, fee 0.10%": hedged(ALL),
          "ISHG unhedged (0.35% fee)": RF["ISHG"].reindex(idx), "VGSH": RF["VGSH"].reindex(idx), "BSV": RF["BSV"].reindex(idx),
          "BNDX": RF["BNDX"].reindex(idx), "BIL": RF["BIL"].reindex(idx), "3M T-bills": tb.reindex(idx)}


def stats(x, lab, vg):
    x = x.dropna(); n = len(x)
    gg = pd.concat([pd.Series([1.0]), (1 + x).cumprod()])
    y22 = x[(x.index >= pd.Period("2022-01", "M")) & (x.index <= pd.Period("2022-12", "M"))]
    ex = (x - tb).dropna()
    return {"series": lab, "from": str(x.index[0]), "months": n, "return %/yr": ((1 + x).prod() ** (12 / n) - 1) * 100, "vol %": x.std() * np.sqrt(12) * 100,
            "max DD %": (gg / gg.cummax() - 1).min() * 100, "2022 %": ((1 + y22).prod() - 1) * 100 if len(y22) == 12 else np.nan,
            "corr VGSH": x.corr(vg), "excess vs bills %/yr": ex.mean() * 1200}


for lab, start in [("FULL WINDOW (2013-10 to 2026-10; majors use rate-gap carry before 2015)", "2013-10"), ("REAL-FORWARD WINDOW (2015-02 onward)", "2015-02"),
                   ("IRISH FUND WINDOW (2019-02 onward)", "2019-02")]:
    m = [p for p in idx if p >= pd.Period(start, "M")]
    rows = [stats(s.reindex(m), k, RF["VGSH"]) for k, s in series.items()]
    if start == "2019-02":
        rows.insert(2, stats(RF["0P00011WU8"].reindex(m), "Vanguard Irish hedged short-term fund (real NAV)", RF["VGSH"]))
    print(f"\n{lab}")
    print(pd.DataFrame(rows).set_index("series").round(2).to_string())

h = series["Hedged ISHG, 11 currencies (ex KRW), fee 0.10%"]
yr = pd.DataFrame({"hedged (11 ccy)": h, "VGSH": RF["VGSH"].reindex(idx), "BNDX": RF["BNDX"].reindex(idx), "T-bills": tb.reindex(idx)})
print("\nCalendar-year returns, %:")
print(((1 + yr).groupby(yr.index.year).prod() - 1).mul(100).round(2).T.to_string())
out = pd.DataFrame(series)
out.index = out.index.astype(str)
out.to_csv("data/processed/real_hedged_ishg_monthly.csv")
print("\nSaved data/processed/real_hedged_ishg_monthly.csv")
