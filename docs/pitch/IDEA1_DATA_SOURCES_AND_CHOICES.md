# Idea 1: data sources, data used, and data choices

**Idea 1:** a USD-hedged 1-3 year developed ex-US government bond ETF.
**Prepared:** 12 Nov 2026, from the analyst files in `reports/etf_ideas/` (Alpha, Alpha-2, Gamma, Gamma-2, Epsilon) and `reports/pitch/build_pdfs.py`.
**Purpose:** let anyone on the team (or a judge asking "where does that number come from?") trace every figure in the Idea 1 PDF to a source, and see which choices were ours.

How to read the labels: **Real** = observed data from an existing fund or market series. **Model** = a number we computed or simulated. **Sourced** = from a published page we cite, not re-measured. **Unverified** = not confirmed against a primary source; do not rely on it.

---

## 1. The one-paragraph summary

No hedged 1-3 year ex-US government ETF exists to price, so the "backtest" has two different kinds of evidence:

1. **Real fund data** about neighbours (BNDX, VGSH, BSV, BND, ISHG and others). This is what shows that short duration, not hedging, protected investors in 2022.
2. **Model C**, a simulation we built from government yield curves, FX rates and overnight rates. It is a model, not a track record. It tells us the carry and roll mechanics are plausible, not what the fund would have returned.

The yields quoted in the "no yield pickup over the US 2-year" argument are **government curve yields plus overnight rates**, not any ETF's published yield. We have **not** verified any competing fund's SEC yield or duration from the issuer.

---

## 2. Real fund data (what was actually observed)

| Data | Source | Used for | Notes |
|---|---|---|---|
| Daily returns for Vanguard funds (VGSH, VBIL, BSV, BND, BNDX, VEA and others) | `data/processed/returns_spliced.csv`: CRSP through 2024-12-31 (WRDS), yfinance after | 2022 comparison, hiking-regime results, Model C benchmarks | File ends **2026-09-17**. CRSP and yfinance agree to a median 0.003 bp daily over 5,285 overlapping days, with differences concentrated in illiquid small-cap ETFs. Market-price basis. |
| ISHG (iShares 1-3 Year International Treasury Bond, unhedged), BWX, BWZ, IBTE, IBGS, IGLH and others | yfinance adjusted close | Competitor comparison, Model C validation | Not matched to CRSP (CRSP only covers the repo's Vanguard universe). yfinance is an unofficial scraper; a re-pull can differ slightly. |
| ISHG holdings (country and currency weights, duration, yield to maturity) | iShares `latest-holdings.csv`, as of **5 Nov 2026** | Model C weights | Single date. Historical weights are **not available**. Fund-weighted duration 1.90y, YTM 3.24%. |
| Fees and assets for competitors | Yahoo Finance, the iShares product page, and web search snippets | Fee comparison (ISHG 0.35%, BWZ 0.35%, IBTE 0.10% EUR class, BNDX 0.07%) | Sourced, not read from fund documents. **BNDX's fee, duration and SEC yield are unverified**: Epsilon could not read Vanguard's page. |

### What the real data shows (used in the PDF)
- 2022: BNDX **-12.8%** (hedged, duration about 6.9y per the research memo, unverified), BND -13.1%, BSV -5.5%, VGSH -3.9% (CRSP total return) or -3.1% (yfinance price-adjusted). Short duration, not hedging, protected investors.
- Hiking-regime windows (3m yield up more than 0.25pp over 126 trading days; 1,026 days): VGSH +0.56% annualised, BNDX +0.10%, BND -2.06%.

---

## 3. Model C: inputs, by purpose

Model C (built by Alpha-2, stress-tested by Gamma-2, sources checked by Epsilon) reprices a 1-3 year zero-coupon bucket per currency, adds a monthly-locked hedge carry, and subtracts a fee. All inputs were retrieved on 6 Nov 2026 with public, unauthenticated requests and cached in `reports/etf_ideas/alpha2/raw/` (not committed to git). The full URL list is `reports/etf_ideas/alpha2/source_log.csv`.

### 3.1 Government yield curves (the "local" return)
| Currency | Source | Series | Status |
|---|---|---|---|
| EUR | ECB Data Portal, spot curves | `YC/B.U2.EUR.4F.G_N_C.SV_C_YM.SR_*` (all euro-area issuers), 3M-10Y | OK. **Main curve.** |
| EUR (sensitivity) | ECB | `G_N_A` (AAA issuers only) | OK. Sensitivity only. |
| JPY | Ministry of Finance, `jgbcme_all.csv` | JGB par yields 1-10Y | OK to 2026-10-30. This is the date that ends the backtest window. |
| CAD | Bank of Canada Valet | `bond_yields_benchmark` (2-10Y) | OK. No 1Y node; 1Y interpolated. |
| AUD | RBA tables F2 | Government par yields 2-10Y | OK. No 1Y node; interpolated. |
| GBP | **None used in the main case** | Flat at SONIA | **Assumption, not data.** A verified 1-3y gilt curve was not available (see section 5). |
| USD | FRED `DGS1`...`DGS10`, `DFF` | US Treasury curve | Used for the US-curve proxy check and the VGSH comparison. |

### 3.2 Overnight rates (the hedge carry)
Hedge pickup each month is the US overnight rate minus the foreign overnight rate (covered interest parity).

| Currency | Series | Notes |
|---|---|---|
| USD | FRED `DFF` (effective fed funds) | OK |
| EUR | EONIA to 2019-09-30, then €STR (`EST/B.EU000A2X2A25.WT`) | OK. EONIA = €STR + 8.5bp exactly in the overlap, so no adjustment was needed. |
| GBP | SONIA (FRED `IUDSOIA`) | OK |
| CAD | CORRA (BoC `AVG.INTWO`); BoC target rate before CORRA existed | OK |
| AUD | RBA cash rate (F1) | OK |
| JPY | OECD monthly call rate (FRED `IRSTCI01JPM156N`), held flat between months, last print Sept 2026 | **Weakest series.** TONA (BoJ daily) was unreachable. |

### 3.3 FX
ECB euro reference rates for 12 currencies (`EXR/D.{CCY}.EUR.SP00.A`), converted to USD per local unit. The ECB fix is at **14:10 CET** and is published about 16:00 CET (Alpha-2 wrote 14:15, which Epsilon corrected). The NYSE closes at 22:00 CET in November, so the FX and fund prices are about 8 hours apart. This is the main reason daily correlation to ISHG is only 0.45-0.53.

### 3.4 Weights
ISHG's 5 Nov 2026 holdings: EUR 55.53%, JPY 9.12%, GBP 7.27%, CAD 4.57%, AUD 4.54%, KRW 4.52%, ILS 4.40%, SGD 3.32%, NZD 2.05%, NOK 1.59%, DKK 1.51%, SEK 1.28%. The main model uses the five currencies with curve data, renormalised: **EUR 68.5%, JPY 11.3%, GBP 9.0%, CAD 5.6%, AUD 5.6%**. The other seven (18.7% of ISHG) are dropped. Weights are held constant over 2013-2026.

### 3.5 Fee
0.07% a year (main case) and 0.10% (sensitivity). **0.07% is below every comparable we found** (ISHG 0.35%, IBTE 0.10%); at 0.35% the model's mean return falls by about 0.28pp a year.

---

## 4. Data choices, why we made them, and what they cost

| Choice | Why | Effect if we had chosen otherwise |
|---|---|---|
| **ECB all-issuers curve, not AAA, for the euro leg** | ISHG holds France, Italy, Spain, Portugal and others, not just AAA names. AAA sits about 29bp below the all-issuers curve on average. | AAA lowers CAGR from 1.70% to 1.37% and costs 0.32 Sharpe. |
| **Zero-coupon repricing of a 1-3y bucket, rebalanced daily** | Simple, transparent, reproducible from public curves. Self-tests are exact. | Real bonds carry liquidity and new-issue effects that curves do not capture. |
| **Par yields treated as zero rates** (JPY, CAD, AUD) | Zero curves were not available. | Approximation; may understate yield moves (hypothesis, untested). |
| **GBP flat at SONIA** | The BoE 1-3y spot curve was not verified. | Using the 5y zero instead changes CAGR by +0.02pp and Sharpe by -0.13. |
| **Drop the 7 currencies with no daily yield source** | No free daily 1-3y government yield exists for KRW, ILS, SGD, NZD, NOK, DKK or SEK. | Proxying them with EUR or US curves changes the result by under 0.1 Sharpe. |
| **Constant 5 Nov 2026 weights over 13 years** | No historical holdings available. | Unknown. Duration is about right (model 2.11y vs ISHG 1.90y). |
| **Monthly hedge reset** | Matches how a real fund rolls forwards. | Intra-month FX residual is small (about 0.05% a year in 2022-2026). |
| **Cross-currency basis not modelled (sensitivity -30/0/+30bp)** | No sourced 2013-2026 series. | **Largest single uncertainty**: Sharpe moves from 1.59 to 2.28. Gamma-2 thinks the sign convention in the sensitivity is probably reversed. |
| **VGSH 2022 from CRSP total return, with yfinance shown as an alternative** | CRSP is the better source for Vanguard funds. | 2022 VGSH is -3.9% (CRSP) or -3.1% (yfinance). The Model C "edge" over VGSH is +0.91pp or +0.16pp depending on the series. |
| **Return window 4 Sep 2013 to 30 Oct 2026 (Model C); table in the PDF to 17 Sep 2026** | Model C ends at the last JGB print; the CRSP-spliced file ends 17 Sep. | CAGR reads 1.70% on the longer window and 1.58% on the PDF's. The PDF says "about 1.6-1.7%". |
| **Volatility band 0.85-1.05%, not 0.87%** | Gamma-2 tested the euro leg against the real euro 1-3y ETF (IBGS): daily correlation 0.73, monthly 0.96. | At 1.05% volatility the Sharpe is about 1.60, and the 2022 edge over VGSH vanishes. |

---

## 5. Gaps and unverified items

- **GBP:** no 1/2/3y gilt tenors confirmed. Alpha-2 downloaded the 39 MB BoE ZIP files without approval; they sit in `reports/etf_ideas/alpha2/raw/` (git-ignored) and were not used. Decision pending whether to delete them.
- **JPY overnight:** monthly OECD only, with a stale last print. BoJ TONA unreached.
- **KRW, ILS, SGD, NZD, DKK:** no daily yield source reachable. SEK and NOK have policy rates only.
- **Cross-currency basis:** no sourced series; sign unresolved.
- **BNDX duration, fee, SEC yield and hedging method:** unverified against Vanguard's page.
- **Historical ISHG weights and the FTSE index's rebalance and cap rules:** unverified.
- **Hedging frictions** beyond the basis (forward bid-offer, collateral, rolls): not modelled.
- **BoE Nov 2026 Bank Rate decision:** unverified. Bank Rate was 3.75% as of 31 Oct 2026.
- **Spliced CRSP file ends 17 Sep 2026:** after that date Vanguard fund returns are not in the project file.

---

## 6. The yields in the "no pickup over the US 2-year" argument

The hedged yield for a currency is: **foreign 2-year yield + (US overnight rate - foreign overnight rate)**. Inputs on 5 Nov 2026:

| Market | Foreign 2y | Pickup (US 3.88% minus foreign overnight) | Hedged 2y | Sources |
|---|---|---|---|---|
| Euro, AAA curve | 2.96% | +1.44 (€STR 2.44%) | **4.40%** | ECB, FRED DFF |
| Euro, all-issuers curve | 3.13% | +1.44 | **4.57%** | ECB, FRED DFF |
| Canada | 3.17% | +1.36 (CORRA 2.52%) | **4.53%** | BoC |
| US Treasury 2y | 4.46% | n/a | 4.46% | FRED DGS2 |
| US 3-month bill | about 4.05% | n/a | about 4.05% | As quoted in the research; not re-read here |

**Correction to what I said earlier in chat:** I used the euro AAA curve (4.40%). Model C's main case uses the all-issuers curve, which gives about 4.57% for the euro leg. Both sit within about 0.1 points of the US 2-year, so the conclusion (no yield pickup over comparable US duration) is unchanged. Note this is a **curve-yield calculation**, not any fund's SEC yield. ISHG's own file shows a weighted yield to maturity of 3.24% in local-currency terms, unhedged.

---

## 7. What we can and cannot claim from this data

**Can claim (real or well-supported):**
- Short-duration funds held up in 2022 (VGSH about -3.9%, BSV -5.5%); BNDX, which is hedged but long, did not (-12.8%).
- The hedge carry mechanics work: a real EUR-hedged USD Treasury fund (IBTE) lagged its unhedged twin by 1.775% a year against 1.654% implied by the rate gap, a residual of about 0.12 points.
- A model of a hedged 1-3y basket returned roughly 1.4-2.0% a year across data choices from 2013, with volatility of about 0.85-1.05%.

**Cannot claim:**
- A Sharpe ratio (the range 1.5-2.3 depends on unvalidated volatility and an unknown basis).
- That it beats T-bills (about 1.9% a year, FRED `DTB3`, over the same period).
- Any outperformance of VGSH in 2022 as a result.
- That a fund like this has a track record, or that the 5 Nov 2026 weights describe 2013-2026.

---

## 8. Reproducing the numbers

- Model C: `venv/bin/python reports/etf_ideas/alpha2/build.py` (needs cached inputs in `alpha2/raw/`; re-download is possible from `source_log.csv` URLs).
- Source checks: `venv/bin/python reports/etf_ideas/epsilon/model_c_verify.py` writes `epsilon/model_c/model_c_source_tests.csv` (56 rows).
- Stress test: `reports/etf_ideas/gamma2/` (CSV files named in `CRITIQUE.md`).
- PDF figures: `reports/pitch/build_pdfs.py`, run from the project root with the PDF virtual environment.

Key files: `alpha2/RESULTS.md`, `alpha2/model_c_daily.csv`, `alpha2/source_log.csv`, `epsilon/VERIFICATION_MODEL_SOURCES.md`, `gamma2/CRITIQUE.md`.

## 9. Fast checks to close before Friday 13 Nov
1. Read BNDX duration, fee and SEC yield from Vanguard's page, and ISHG's from iShares.
2. Source a cross-currency basis series (BIS or a Bloomberg pull) and settle the sign.
3. Confirm one clean figure for the hedged 2-year comparison (AAA vs all-issuers, and the exact US 3-month bill yield).
4. Decide whether to delete the unused BoE ZIP files.
