# Decision record — why Book A, and everything that moved us

Written 2026-09-17. Audience: the team, including the author of Book B.
Supersedes `superseded/MERGED_STRATEGY.md`. Every figure here is reproducible from
`scripts/trading/`; where a claim rests on a test, the test is named.

**Decision: Book A, 5% VFMV sleeve, no rebalancing.**

---

## 0. Naming

| | whose | what |
|---|---|---|
| **Book A** | ours | VBIL/VGUS/VUSB at the cap + VGSH, VSDB, VFMV. Short-duration carry engine. |
| **Book B** | teammate's | "The Covariance Budget" — 10 holdings, max-diversification on semi-covariance + HRP. |
| **Merged** | 75/25 | A's six funds + B's three sectors (VDE/VGT/VDC). Equity sleeve 5% → 16.6%. |
| **Conditional** | deferral | Hold A; upgrade to Merged on 2 Oct only if 1 Oct shows a lag. |

**Correction accepted:** calling the merge "75% A + 25% B" was wrong. It drops
VSDM, EDV, BNDX, VPL and VCSH — five of B's ten — and keeps only the three
sectors. It is not a synthesis of philosophies. It is **Book A with one dial
turned**, and framing it otherwise obscured the real question, which is where on
that dial to sit.

---

## 1. The order

Six trades, every account identical, place in one session.

| Ticker | Shares | ≈ Cost | Weight |
|---|---|---|---|
| **VBIL** | **820** | $61,992 | 24.80% |
| **VGUS** | **819** | $61,859 | 24.74% |
| **VUSB** | **1,250** | $61,950 | 24.78% |
| **VGSH** | **328** | $18,916 | 7.57% |
| **VFMV** | **86** | $12,341 | 4.94% |
| **VSDB** | **165** | $12,405 | 4.96% |

$229,462 invested · $60 commission · **cash 8.19%** · max position 24.80%.

Re-check share counts against live quotes before submitting.

**The one open disagreement: 24.80% vs B's 20% house rule.** It is not a
competition constraint — the platform cap is 25%. Measured cost of enforcing it:

| | same-day | lagged |
|---|---|---|
| cap at 24.8% (platform) | **7.194** | 2.514 |
| cap at 20.0% (house rule) | **6.250** | 2.513 |

**It costs 0.94 Sharpe on the same-day branch and nothing on the lagged one**
(under lag the sawtooth dominates, so the weight distribution barely matters).
An earlier estimate of "roughly 0.4" was unmeasured and too low.

So the question is exactly: *is a 20% concentration limit worth 0.94 Sharpe in
the branch we think is more likely?* The house rule exists to prevent
single-name blowups, and VBIL is a 0-3 month T-bill fund with 0.28% volatility —
the risk it guards against is not present here. **Recommend the 25% cap, but
settle it explicitly rather than letting the order table decide by default.**

---

## 2. The mechanism

StockTrak computes `(mean daily return − rf) / sd(daily return) × √252`, with
`rf` set to the session's cash interest — **0%**. The numerator is therefore not
excess return. It is all return.

For a bond fund, `Sharpe ≈ carry / (duration × σ_yield)`. The denominator scales
linearly with duration; the numerator only with the slope of the curve, which
flattens. The ratio is maximised as duration → 0.

Measured across the whole lineup:

| ticker | SEC yield | duration | ann vol | **Sharpe @ rf=0** |
|---|---|---|---|---|
| VBIL | 3.64% | ~0.0 | 0.28% | **12.6** |
| VGUS | 3.77% | 0.1 | 0.32% | **11.4** |
| VUSB | 4.50% | 0.5 | 0.74% | **5.9** |
| VGSH | 4.37% | 1.6 | 1.42% | 3.1 |
| VCIT | 5.62% | 4.0 | 4.78% | 1.2 |
| EDV | 5.64% | 10.3 | 17.09% | 0.3 |

**VBIL → EDV: yield ×1.55, volatility ×60.** Scanning all 116 Vanguard ETFs,
only three are under 1% volatility, and all three go to the cap.

---

## 3. The catch that moved us: B's 1.358 figure

Book B page 4: *"We also checked whether a pure Sharpe ranking is gameable by
parking everything in T-bill ETFs. It is not: a pure cash-like book scores Sharpe
1.358."* That single sentence justified rejecting the entire approach.

It is a **regime artefact.** B's backtest spans 2004–2026. Measured on FRED:

| era | mean 3-month bill |
|---|---|
| 2004–2007 | 3.40% |
| **2009–2015 (ZIRP)** | **0.08%** |
| 2016–2019 | 1.31% |
| **2020–2021 (ZIRP-2)** | **0.09%** |
| 2022–2026 | 3.98% |
| **today** | **3.97%** |

**40.1% of days in that sample had bills below 0.25%. 49.9% below 1.00%.**

A bill fund's Sharpe at rf = 0 is yield ÷ volatility:

| bill yield | implied Sharpe |
|---|---|
| 0.05% | **0.2** |
| 1.00% | 3.3 |
| **3.97% (today)** | **13.2** |

Averaging a ratio across an era that was two-fifths zero-rate produces 1.358 — a
number describing the 2010s, not September–November 2026. Re-run on the current
regime through B's own framing, Book A scores **7.19**, not 1.358.

This is not a methodology failure. B's process was more rigorous than ours. It is
a single missed regime check sitting underneath the conclusion that justified
everything above it.

### Two consequences inside B's own book

- **VSDM at 18.41%, B's largest position.** A municipal fund yielding **3.48%**
  against VGSH's **4.37%** at similar duration. Municipal yields are lower
  *because* the income is tax-exempt — and there are no taxes in a simulation.
  That is **89bp given away for nothing**, or 16.4bp of portfolio carry.
- **EDV at 4.31%, in a hiking cycle.** B's own regime work found the bond sleeve
  averages −3.1% annualised with only short duration positive. EDV carries 10.3
  years of duration, 17.1% volatility, realised Sharpe **−0.61** over two years.

Both follow from the same root: *"never forecast returns"* applied to SEC yield.
But SEC yield is **not a forecast** — it is a published yield-to-maturity that
realises with high fidelity over eight weeks. B's own DGU reading says the
critique is about the mean vector; a bond's contractual carry is not a mean
estimate.

**The merged principle, which is better than either document states alone:**

> Never estimate expected returns — except contractual carry, which is not an
> estimate.

---

## 4. Every test that produced the decision

All on 73 matched windows: 31 scored days (36 trading days minus the 5-day
warm-up) containing exactly 2 ex-dates — the shape of 18 Sep → 6 Nov. Integer
shares, $10 commissions, measured half-spreads, cash at 0%. Rank is against 17
real competitor portfolios exported 17 Sep plus 49 simulated books, 67 teams.

### 4.1 Head-to-head, real returns

| book | branch | median Sharpe | P(neg) | median rank | P(top 7) |
|---|---|---|---|---|---|
| **A** | same-day | **7.19** | 0% | **1st** | 88% |
| | lagged | 2.51 | 0% | 7th | 51% |
| **B** | same-day | 2.19 | **16%** | 13th | 47% |
| | lagged | 2.19 | 15% | 15th | 45% |
| **Merged** | same-day | 4.97 | 1.4% | 2nd | 85% |
| | lagged | **3.41** | 1.4% | **3rd** | **70%** |
| VTI | either | 2.4 | 27% | 18th | 3% |

On real returns the merge wins under lag. That is the case for it, and it is real.

### 4.2 The demeaning test — this is what decided it

Equity returns re-centred so no fund gets credit for having won in-sample, vol
and correlation preserved:

| book | returns | same-day | lagged |
|---|---|---|---|
| **A (5% sleeve)** | real | 7.19 | 2.51 |
| | **demeaned** | **6.67** | **2.31** |
| **Merged (16.6%)** | real | 4.97 | 3.41 |
| | **demeaned** | **3.47** | **2.26** |

**A loses 7% to demeaning. The merge loses 30%.** Demeaned, **A beats the merge
on both branches.** The merge's lag protection was VDE (+46% in sample) and VGT
(+39%) — a directional equity bet, not diversification.

This is exactly the test Book A already ran to cap VFMV at 5%, and which we
failed to apply to our own merge. It is also B's page-4 finding — adding a
return-seeking sleeve raises mean monotonically and lowers Sharpe monotonically —
applied to the merge rather than quoted at it.

### 4.3 The conditional upgrade — tested, and it fails

Hold A; if 1 Oct shows a lag, switch to Merged on 2 Oct.

| strategy | lagged: median rank | lagged: P(top 7) |
|---|---|---|
| Book A | **7th** | **50.7%** |
| Conditional | 9th | 49.3% |
| Merged | 3rd | 69.9% |

**Worse than simply holding A.** The mechanism, stated correctly: the lag is
observable **at the 1 October close** — either account value dipped that day or
it did not, and that is definitive regardless of when the cash later arrives.
The earliest possible switch is therefore 2 October, by which point the
1 October sawtooth is already inside the return series and cannot be removed.
You protect only against 2 November, and pay a transition day and $120 for it.
The information arrives after the loss, not late — the option is worthless
because the damage precedes the earliest action, not because the signal is slow.

*(An earlier draft said the lag was observable "by 5 October". That was wrong.
The test itself switched on the day after the ex-date and is unaffected; only
the explanation was mis-stated.)*

### 4.4 Cut size — does not flip the ranking

Nobody has told us the cut is seven. Tested across {4, 6, 7, 10, 15}: **the
ordering of the candidates is stable at every cut.** No value of N flips which
book wins.

(Median rank is a property of the book, not of the cut, so quoting it "at every
cut" would be trivially true rather than evidence. The claim that carries weight
is the stability of the ordering.)

Worth asking Ozkan anyway; it is not the decisive question.

### 4.5 The field, scored on the same metric

17 real competitor books: **best 3.25, median 2.09, worst 0.97.** Aggregate
positioning VGT 12.9%, VUG 12.0%, VOO 11.8%, VDE 11.6% — **short-duration bonds
3.4%.** No rival holds more than 22.6%. Every set of trade notes is about
return: *"high torque for a simulation this short"*, *"to the moon"*.

---

## 5. Rebalancing — and a correction to our own argument

**We previously claimed rebalancing hurts because each rebalance injects a
transition day into the volatility denominator. That claim is wrong.** Tested
directly by running weekly rebalancing at zero cost:

| book | branch | static | weekly, full cost | weekly, 50% smooth | **weekly, ZERO cost** |
|---|---|---|---|---|---|
| Book A | same-day | 7.194 | 6.342 | 6.659 | **7.251** |
| Book A | lagged | 2.514 | 2.255 | 2.324 | **2.526** |
| Merged | same-day | 4.969 | 4.309 | 4.576 | **5.034** |
| Merged | lagged | 3.408 | 2.929 | 2.996 | **3.479** |

**Zero-cost rebalancing is neutral to slightly positive.** There is no transition
variance penalty. B's framing — that this is a turnover question — was right and
ours was wrong.

**But the cost is not immaterial, and B's "~12bp" understates it for this book.**
Weekly rebalancing costs **0.54 Sharpe with 50% smoothing** and 0.85 at full
turnover. The reason is arithmetic:

| | commissions | as % of gross window return |
|---|---|---|
| weekly (6 cycles × 6 trades) | $360 | **26.2%** |
| fortnightly | $180 | 13.1% |
| **once** | **$60** | **4.4%** |

Our window return is 0.55% — **$1,375 on a $250,000 account.** $360 of
commissions is 26% of it, taken straight off the numerator. The same $360 against
a 3% equity return is 4.8%.

**This reconciles the disagreement completely.** B's turnover analysis concluded
"immaterial" and was correct — *for B's book*. On a book whose entire return is
55 basis points, fixed costs are proportionally five times larger. Same dollars,
different denominator.

**Recommendation: place once, hold to 6 November.** If the cadence is kept, the
burden of proof is a test showing rebalancing beats static hold on Sharpe *net of
costs on this book's return profile*, not on turnover in isolation.

**Operational:** B's page 6 schedules the first live rebalance for Thursday
24 September. A document disagreeing with it is not the same as it not firing.
Someone has to turn the script off.

---

## 6. Errors we made and corrected

Included so this can be audited rather than trusted.

| error | how it surfaced | consequence if shipped |
|---|---|---|
| Ledoit-Wolf inflated VBIL's volatility **13×** in a mixed universe | diagnosed the gap between ex-ante 2.69 and realised 8.2 | the optimiser could not see the short end at all |
| `Muni` substring filter silently dropped VOX ("Com-**muni**-cation") | universe count off by one | a sector ETF missing from the universe |
| Break-detection scan rediscovered March 2020 for every fund | every break date landed in one quarter | false methodology-break dates |
| 5% VFMV weights summed to 89.2%, leaving **10.8% cash** | compliance check after weighting | breach of the organiser's cash cap |
| Compared two books on **mismatched bootstrap samples** | reran on identical windows | reversed the conclusion |
| Claimed rebalancing costs **transition variance** | zero-cost test above | wrong mechanism, right conclusion |
| Framed the merge as "75% A + 25% B" | teammate's reframing | hid that it was one parameter |
| Said the lag was observable "by 5 October" | teammate's review | wrong mechanism beside a right conclusion (4.3) |
| Estimated the 20% house rule at "~0.4 Sharpe" | measured it | understated by more than half — it is 0.94 |

---

## 7. What remains unresolved

- **Distribution crediting.** 1 October (Thursday). VBIL prints ~−21¢; watch
  whether account *value* dips that day or holds until ~5 October. Same-day →
  A scores ~7.19 and ranks 1st. Lagged → ~2.51 and 7th. **All 29 Vanguard bond
  ETFs pay on the 1st**, so this cannot be diversified or timed away.
- **rf = 0.** Confirmed from session settings. The single load-bearing
  assumption; at rf = 3% with lagged crediting, B's book becomes the better one.
- **The cut size.** Assumed 7. Past editions reportedly used 4, 6 and 15.
- **3 October 2026 is a Saturday.** The email says "first trade by Friday,
  October 3." The effective deadline is **Friday 2 October**. Worth one line to
  Ozkan — and worth having the book placed so the question is moot.
- **FOMC, 28 October**, inside the window. B flagged it; we had missed it. B's
  instruction — flag, take no discretionary action — is correct. Portfolio
  duration is ~0.25 years, so a surprise hike costs roughly 6bp.
- **The November pay date — a check, not a risk.** The 2 November distribution
  only matters on the lagged branch *and* only if its pay date slips past
  6 November, 4pm. Verified from the live quote feed: **all six holdings run a
  2-business-day lag.** Projected:

  | lag | pay date | |
  |---|---|---|
  | 2 business days (observed) | Wed 4 Nov | inside |
  | 3 | Thu 5 Nov | inside |
  | 4 | Fri 6 Nov | inside, same day as close |
  | 5 | Mon 9 Nov | **outside** |

  It would take a slip to 5 business days, against an observed 2, *and* lagged
  crediting. A compound tail, not a live threat. If it ever did land outside we
  would lose ~0.30% off a 0.55% window return and the Sharpe roughly halves, and
  any mitigation would have to be planned against the cash cap rather than
  improvised on 5 November — so confirm the pay date when the October cycle
  prints, which costs five minutes.

- **VFMV has an ex-date inside the window.** New finding. VFMV pays quarterly
  and its recent ex-dates are 24 Sep 2025, 26 Sep 2024, 21 Sep 2023, 23 Sep 2022
  — so a late-September 2026 ex-date is likely, giving a **third** distribution
  event in the scored window alongside 1 Oct and 2 Nov. At a 4.94% weight the
  effect is small, but it was not in the model and should be watched.

- **Sample size.** 73 matched windows, 17 of 67 real competitor portfolios,
  VBIL's own history 399 observations.

---

## 8. What Book B got right and should carry forward

Stated plainly because the decision went the other way and that should not be
read as a verdict on the work.

- The methodology is the most rigorous on the team: ~40 allocators, 135
  out-of-sample windows, an append-only log with 14 recorded mistakes.
- The DGU reading — *"their critique is about the mean vector, not optimisation
  itself"* — is sharper than ours and is the correct framing.
- The selection-vs-weighting test (1/N on max_div's own picks scores 1.37 against
  its own 1.77) is a clean proof the edge is in sizing. We never ran it.
- Page 4's satellite-sleeve finding is the result that ultimately killed our own
  merge. We quoted B's flaws at length and failed to apply B's strongest finding
  to our own book until it was pointed out.
- Section 07 — admitting P(Sharpe > 1.5) spans 49.6–54.1% including VTI — is the
  most honest passage in any of these documents.
- The turnover framing on rebalancing was right where ours was wrong.

**The disagreement was never about rigour. It was one regime check, and it
happened to sit under the conclusion that decided everything else.**
