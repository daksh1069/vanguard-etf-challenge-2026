# Merged Strategy — WolfPack

Two books were built independently. This merges them. Written 2026-09-17.

- **Book A — "carry engine"** (`reports/STRATEGY.md`): ultra-short bonds, exploiting
  rf = 0.
- **Book B — "covariance budget"** (`Vanguard_ETF_Strategy.pdf`): max-diversification
  on semi-covariance + HRP sleeve, 10 holdings.

**Merged book = 75% A + 25% B**, capped at 20% per position.

---

## 1. The order — per $250,000 account, identical across all four

| # | Ticker | Fund | Sleeve | **Shares** | Weight |
|---|---|---|---|---|---|
| 1 | **VBIL** | Vanguard 0-3 Month Treasury Bill ETF | cash-like | **661** | 19.99% |
| 2 | **VUSB** | Vanguard Ultra-Short Bond ETF | cash-like | **1,009** | 20.00% |
| 3 | **VGUS** | Vanguard Ultra-Short Treasury ETF | cash-like | **662** | 20.00% |
| 4 | **VGSH** | Vanguard Short-Term Treasury ETF | short bond | **498** | 11.49% |
| 5 | **VDE** | Vanguard Energy ETF | sector | **61** | 4.42% |
| 6 | **VGT** | Vanguard Information Technology ETF | sector | **87** | 4.23% |
| 7 | **VDC** | Vanguard Consumer Staples ETF | sector | **46** | 4.14% |
| 8 | **VFMV** | Vanguard U.S. Minimum Volatility ETF | low-vol eq | **67** | 3.85% |
| 9 | **VSDB** | Vanguard Short Duration Bond ETF | short bond | **128** | 3.85% |

Invested **$229,916** · commissions **$90** · **cash $19,994 = 8.00%** ·
largest position **20.00%** (B's own rule; platform allows 25%) · 9 positions.

## 2. Why 75/25 and not either book alone

73 matched windows (31 scored days, 2 ex-dates — the shape of 18 Sep → 6 Nov),
run through one simulator: integer shares, $10 commissions, measured
half-spreads, cash at 0%. Rank is against 17 real competitor portfolios plus 49
simulated books, 67 teams.

| book | branch | median Sharpe | p10 | P(neg) | median rank | P(top 7) |
|---|---|---|---|---|---|---|
| **A alone** | same-day | **7.26** | 3.92 | 0% | **1st** | 88% |
| | lagged | 2.51 | 1.45 | 0% | 5th | 52% |
| **B alone** | same-day | 2.19 | −0.65 | 16% | 13th | 47% |
| | lagged | 2.19 | −0.64 | 15% | 15th | 45% |
| **Merged 75/25** | same-day | 4.95 | 1.23 | 1.4% | **2nd** | 81% |
| | lagged | **3.41** | 0.95 | 1.4% | **3rd** | **70%** |
| VTI | either | 2.4 | −1.68 | 27% | 18th | 3% |

**Blended P(top 7 of 67):**

| P(same-day crediting) | A alone | B alone | **Merged** |
|---|---|---|---|
| 50% | 69.9% | 45.9% | **75.3%** |
| 70% | 77.0% | 46.2% | **77.5%** |
| 85% | **82.3%** | 46.4% | 79.2% |

The merged book is **the only one that is top-3 on both branches.** A alone wins
if you are confident about same-day crediting; the merge wins otherwise and
costs little if you are right.

## 3. Book A — merits and flaws, stated plainly

**Merits**
- Identifies that rf = 0 removes the Sharpe hurdle, making `Sharpe ≈ carry /
  (duration × σ_yield)`. Maximised as duration → 0. VBIL→EDV is yield ×1.55,
  volatility ×60.
- Uses contractual carry (published SEC yields), which is estimable, rather than
  forecast returns, which are not.
- Return positive in 15 of 15 monthly cohorts and 324 of 324 windows.
- Volatility 0.76% against a field at 10.4–15.6%.

**Flaws**
- **Single point of failure.** Everything rests on whether StockTrak credits
  distributions on the ex-date or the pay date: 7.26 vs 2.51. **92% of the
  lagged-branch variance is that sawtooth**, and all 29 Vanguard bond ETFs pay on
  the 1st, so it cannot be diversified or timed away internally.
- Short estimation sample. VBIL has 399 observations; P(negative Sharpe) = 0 is
  partly an artefact of that.
- Weak presentation narrative. "We found a scoring quirk" is a harder sell in
  November than "we built a covariance budget."
- Regime-dependent by construction. At ZIRP bill yields this book scores ~0.2.

## 4. Book B — merits and flaws, stated plainly

**Merits**
- The most rigorous methodology on the team: ~40 allocators tested across 135
  out-of-sample windows, an append-only decision log, 14 recorded mistakes.
- The DGU reading is sharper than A's: *the critique is about the mean vector,
  not optimisation itself.* Correct, and it is the right framing.
- The selection-vs-weighting test (1/N on max_div's own picks scores 1.37 vs its
  own 1.77) is a clean proof the edge is in sizing. A never ran that test.
- Genuinely diversified: the three sector holdings are mutually negatively
  correlated (VGT/VDC −0.356), no company held through more than one fund, no
  single stock above 3.74%.
- **Section 07 is the most honest thing either of us wrote** — admitting
  P(Sharpe > 1.5) spans 49.6–54.1% including VTI, and that the gap between the
  optimised core and the market is inside the noise.
- **Its equity sleeve pays quarterly**, so it barely notices the monthly
  sawtooth — 2.19 on *both* branches. That is exactly the robustness A lacks,
  and it is why it earns 25%.

**Flaws**
- **The load-bearing claim is a regime artefact.** Page 4: *"a pure cash-like
  book scores Sharpe 1.358."* That is averaged over 2004–2026, of which **40.1%
  of days had 3-month bills below 0.25%** and 49.9% below 1.00%. A bill fund's
  Sharpe at rf = 0 is yield ÷ volatility: 0.2 at ZIRP, **13.2 at today's 3.97%**.
  B's own backtest, rerun on the current regime, scores A at 7.26 — not 1.358.
  The methodology was rigorous; the regime check was missed.
- **"Never forecast returns" is applied too widely.** SEC yield is not a
  forecast — it is a published yield-to-maturity that realises with high fidelity
  over eight weeks. Refusing to look at it is why **VSDM is the largest position
  at 18.41%**: a municipal fund yielding 3.48% against VGSH's 4.37% at similar
  duration. That is **89bp given away for a tax exemption worth exactly zero in a
  simulation**, costing 16bp of portfolio carry.
- **EDV at 4.31% in a hiking cycle.** B's own regime work found the bond sleeve
  averages −3.1% annualised with only short duration positive. EDV carries 10.3
  years of duration, 17.1% volatility, realised Sharpe **−0.61** over two years.
  Held for decorrelation the allocator can see, while losing money the allocator
  cannot.
- **16% chance of a negative realised Sharpe**, versus ~0% for A.
- We could not reproduce the ~6.2% volatility figure; reweighting B's book on the
  last two years gives **8.1%**. Possibly a different window — flagged, unresolved.

## 5. The merged principle

> **Never estimate expected returns — except contractual carry, which is not an
> estimate.** Use covariance machinery where returns are unknowable (equities),
> and published carry where it exists (short bonds).

This is better than either document states alone. B is right that the mean vector
is unknowable and that DGU applies to it. A is right that a bond fund's SEC yield
is a disclosure, not a projection. The merged book implements exactly that split:
~75% carry engine, ~25% covariance budget.

## 6. Rebalancing — we recommend none, and this is the one place we disagree with B

B rebalances weekly with 50% smoothing, and treats turnover as a **cost**
question (~12bp over the competition, immaterial). Under a Sharpe ranking it is
a **variance** question, which is different.

Every rebalance injects a transition day into the return series, and that day
lands in the denominator being scored. Tested directly — weekly (5-day)
rebalancing against static hold, costs charged, same windows:

| book | branch | static | weekly rebalance | delta |
|---|---|---|---|---|
| raw blend | same-day | 4.960 | 3.479 | **−1.48** |
| raw blend | lagged | 3.370 | 2.573 | **−0.80** |
| cleaned blend | same-day | 4.950 | 3.879 | **−1.07** |
| cleaned blend | lagged | 3.422 | 2.936 | **−0.49** |

Negative in all four. **Caveat, stated honestly:** our rebalance simulation is a
crude upper bound — it charges full commissions every cycle and does not
implement B's 50% smoothing, so the true cost is smaller than −1.48. The
*direction* is consistent across every configuration; the magnitude is not
precise. Worth B re-running with their own smoothing code before 24 September.

**Recommendation: build once, hold to 6 November.** If B wants to keep the
weekly cadence, the burden of proof is a test showing rebalancing beats static
hold *on Sharpe*, not on turnover cost.

## 7. What we still do not know

- **Distribution crediting.** 1 October settles it. VBIL prints ~−21¢; watch
  whether account *value* dips that day or holds flat until ~5 October. Same-day
  → the merged book sits 2nd; lagged → 3rd. Either way it is inside the cut.
- **rf = 0.** Confirmed from session settings. If it were the platform default of
  3%, A's edge narrows sharply and B's book becomes relatively stronger.
- **FOMC on 28 October, inside the window.** B flagged this and A missed it. B's
  instruction — flag it, take no discretionary action — is correct. Merged
  portfolio duration is ~0.35 years, so a surprise hike costs roughly 9bp.
- **Sample.** 73 matched windows, 17 of 67 real competitor portfolios.

## 8. What the field is doing

Aggregate positioning across 17 real competitor books: VGT 12.9%, VUG 12.0%,
VOO 11.8%, VDE 11.6%. **Short-duration bonds: 3.4%.** No rival holds more than
22.6%; the merged book holds ~63%. Scored on Sharpe, the rivals range
**0.97 to 3.25, median 2.09**. Their trade notes are unanimously about return —
*"high torque for a simulation this short"*, *"to the moon"*.

They are not wrong about the market. They are being graded on a ratio whose
denominator they are all maximising.

> **SUPERSEDED 17 Sep 2026** by `DECISION_RECORD.md`. The merge fails a
> demeaning test: it loses 30% of its score where Book A loses 7%, and
> demeaned, Book A beats it on both branches. Kept for the Book B critique.
