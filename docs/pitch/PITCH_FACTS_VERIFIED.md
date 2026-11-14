# Pitch facts, verified (12 Nov 2026)

Files under `data/private/` are kept out of the public repo (licensed or third-party material); see `data/private/README.md`.

Every number for the Idea 1 deck (USD-hedged 1-3 year non-US government bond ETF), with where it came from. **Real** = observed. **Built from real prices** = our calculation using only market prices. **Model** = simulation (Model C), don't headline it.

## 1. The gap

| Fact | Value | Source |
|---|---|---|
| US-listed "International Government Bonds" ETFs | 6 funds: GGOV, BWX, IGOV, ISHG, FLIA, BWZ | etfdb.com category export, 12 Nov (`data/private/web_sources/etfdb_international_government_bonds_20261112.csv`) |
| Short-term ones | ISHG ($835M, 0.35%) and BWZ ($298M, 0.35%), both **unhedged** | same |
| Hedged ones | GGOV ($4.39B, 0.39%, active, all maturities) and FLIA (0.25%, aggregate) | same |
| Short-term **and** hedged | **None found** in that category, the team's Bloomberg screen, or our searches | etfdb, `data/private/bloomberg/etf_test_data.xlsx` (Test D) |

## 2. Real performance evidence

**Hedged 1-3y non-US government, built from real prices** (ISHG's actual returns, every currency hedged with real 1M forwards for EUR/JPY/GBP/CAD/AUD and rate-gap carry for the rest, fee moved to 0.10%). Script: `scripts/pitch/real_hedged_full.py`.

| Feb 2015 to Oct 2026 | Return a year | Volatility | 2022 | Max drawdown | Corr. with VGSH |
|---|---|---|---|---|---|
| Hedged 1-3y (built from real prices) | 1.8-1.9% | 1.7% | -2.6% to -2.8% | -4.2% to -4.9% | 0.65-0.69 |
| VGSH | 1.6% | 1.6% | -3.9% | -5.3% | 1.00 |
| BSV | 1.9% | 2.2% | -5.5% | -7.8% | 0.94 |
| BNDX | 1.7% | 4.2% | -12.8% | -14.9% | 0.62 |
| 3-month T-bills | 2.2% | 0.6% | +1.8% | 0 | 0.33 |

**Calendar years 2016-2025, annualised:** hedged 1-3y 1.94%, VGSH 1.78%, BSV 2.11%, BNDX 2.08%, T-bills 2.17%. Vanguard's Irish hedged fund 2.29%.

**Vanguard already runs a version abroad (real):** Vanguard Global Short-Term Bond Index Fund, Institutional Plus USD Hedged Acc (IE00BH65QS77). Fund $7.72B, OCF 0.10%, launched 10 Mar 2015. 10-yr 2.06% a year, 5-yr 1.98%, since launch 2.05% (to 30 Sep 2026). Duration 2.7y, 5,550 bonds, 57.6% government, average quality AA-. Tracks a 1-5y global aggregate including the US and corporates, so it is close but not identical. 2022: -5.07%. Source: [Vanguard factsheet, 30 Sep 2026](https://fund-docs.vanguard.com/Global_Short-Term_Bond_Index_Fund_9376_USD_GE_SW_RETAIL.pdf).

**The hedge itself (real):** 2015-2026, real 1M forwards paid a US investor more than the simple rate gap: EUR +0.27, JPY +0.52, GBP +0.21, CAD +0.06, AUD +0.07 points a year. The basis helps a dollar hedger. The Idea 1 PDF's sign is backwards.

## 3. Comparable funds

| Fund | Facts | Source |
|---|---|---|
| BNDX | 0.07% fee; 30-day SEC yield 3.86% (10 Nov); **average duration 6.4y** (not 6.9); 6,837 bonds; fund $124.2B, **ETF share class $84.9B**; median bid/ask 0.021%; 10-yr NAV return 1.58% a year (to 31 Oct) | Vanguard BNDX page (`data/private/web_sources/vanguard_bndx_page_20261110.txt`) |
| ISHG | 0.35% fee, $835M, 183 holdings | etfdb export |
| SCIN | Schwab International Bond ETF, hedged aggregate, 0.06%, launched 21 Oct 2026 | Yahoo Finance |
| VBIL | Vanguard 0-3 month T-bill ETF, 0.06%, $14.3B since Feb 2025 | Yahoo Finance |

## 4. The index (what the fund would track)

FTSE WGBI Developed Markets 1-3 Years Capped Select (non-US; ISHG's index): 192 bonds, **$823B** market value, yield 3.30% (local currencies), effective duration 1.89y. Country cap 21%; countries above 4.6% together capped at 47%. Bills excluded; entry rating A-/A3. Published returns are **unhedged only** (5-yr -0.22% a year). A $10B fund would be about 1.2% of the market. Source: FTSE Russell factsheet, 31 Oct 2026 (`data/private/web_sources/ftse_wgbi_dm_1-3y_capped_select_factsheet_20261031.pdf`).

Korea joined the WGBI in eight monthly steps from April to November 2026 ([FTSE Russell](https://www.lseg.com/en/media-centre/press-releases/ftse-russell/2025/ftse-russell-country-classification-september-2025)), so KRW's 4.5% weight is new.

## 5. Rates today

| Rate | Value | Source |
|---|---|---|
| Fed funds | 3.75-4.00% (effective 3.88%) | FRED, per team docs |
| Bank of England | **4.00%** (raised from 3.75% on 5 Nov) | [BoE November 2026 report](https://www.bankofengland.co.uk/monetary-policy-report/2026/November-2026) |
| Bank of Japan | **1.25%** (raised June and September, held 30 Oct; next meeting 18 Dec) | Trading Economics / BoJ (`data/private/web_sources/boj_policy_rate_notes.txt`) |
| ECB deposit | 2.50% | ECB, per team docs (not re-checked) |
| US 2-year / 3-month bill | 4.46% / about 4.05% (5 Nov) | FRED, per team docs |
| Hedged euro 2-year | 4.57% on the all-issuers curve (4.40% on AAA) | team docs; equals US 2y within about 0.1 |

## 6. Vanguard's own view

Vanguard research: about 30% of a bond allocation in hedged international bonds reduces volatility; hedging helped US investors when US short rates were higher. Sources: [Vanguard advisors](https://advisors.vanguard.com/strategies/fixed-income/bond-funds/international-bond-funds), [Going global with bonds](https://vanguard.co.uk/professional/research/going-global-with-bonds).

## 7. Corrections to the Idea 1 PDF

- BNDX duration **6.4y**, not 6.9y. BNDX assets: $124.2B fund, $84.9B ETF class.
- Bank of England **4.00%**; Bank of Japan **1.25%**.
- Euro hedged 2y **4.57%** on the curve Model C uses.
- Basis sign: it **helps** a USD hedger. In stress it widened in the investor's favour; what worsens is bid-ask and settlement cash.
- "Hedge economics reverse if the Fed cuts": wrong. Against US 2y the product wins or loses by the difference in curve slopes, not the rate gap.
- Fee: 0.10% has a Vanguard precedent (Irish fund); 0.07% matches BNDX.
- Volatility: real prices give about 1.7% (same as VGSH), not Model C's 0.85-1.05%.
- Drop the Sharpe tables (they use a 0% risk-free rate) and the agent names (Alpha-2, Gamma-2, Epsilon).

## 8. Claims to avoid

- That it beats T-bills (2.17% vs 1.94% a year, 2016-2025).
- That it is lower-risk than VGSH (real-price volatility is about the same).
- Any Sharpe ratio, or a track record for a fund that doesn't exist yet.
