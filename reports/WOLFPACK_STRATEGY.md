# WolfPack — Final Strategy & Decision Record

**2026 Vanguard ETF Challenge · Temple Fox × Vanguard**
Written 2026-09-17. This is the single authoritative document.
Supporting detail in `reports/`; nothing there overrides this file.

**Scoring: Sharpe ratio** (confirmed by Prof. Ozkan, 17 Sep 2026).
**Risk-free rate: 0%** (session cash-interest setting).
**Warm-up: delay, not exclusion.** StockTrak's *"we only begin calculating the
Sharpe Ratio 5 trading days after your first trade"* is read as a display gate —
every day from the first trade counts. The return series is anchored at the
entry timestamp, so purchase costs sit in the opening level rather than showing
up as a return. Every figure in this document uses that configuration.
**Decision: Book A — short-duration carry, 5% minimum-volatility sleeve, no rebalancing.**

---

# 1 · The order

Six trades. One session. All four accounts identical.

| # | Ticker | Fund | **Shares** | ≈ Cost | Weight |
|---|---|---|---|---|---|
| 1 | **VBIL** | Vanguard 0-3 Month Treasury Bill ETF | **820** | $61,992 | 24.80% |
| 2 | **VGUS** | Vanguard Ultra-Short Treasury ETF | **819** | $61,859 | 24.74% |
| 3 | **VUSB** | Vanguard Ultra-Short Bond ETF | **1,250** | $61,950 | 24.78% |
| 4 | **VGSH** | Vanguard Short-Term Treasury ETF | **328** | $18,916 | 7.57% |
| 5 | **VFMV** | Vanguard U.S. Minimum Volatility ETF | **86** | $12,341 | 4.94% |
| 6 | **VSDB** | Vanguard Short Duration Bond ETF | **165** | $12,405 | 4.96% |

$229,462 invested · commissions $60 · **cash $20,478 = 8.19%** (cap 10%)
Six trades clears the five-trade minimum with one spare.
Portfolio duration ~0.25 years · **annualised volatility 0.63%** (same-day
crediting) or **1.68%** (lagged). See the note on volatility figures in §2.

> **Share counts priced 17 Sep. Re-check against live quotes before submitting.
> The weights are the decision, not the share counts.**

### Checklist

- [ ] All six are Vanguard funds — the platform will fill SPY without complaint
- [ ] Market orders, all six together, one sitting
- [ ] Identical in **every** account
- [ ] **Do not rebalance** (§6)
- [ ] Do not reinvest distributions
- [ ] Turn off the Book B rebalance script before **Thu 24 Sep**

### One thing to settle before placing

**Position cap: 24.80% or 20%?** The platform allows 25%. Book B sets a 20%
house rule, which is not a competition constraint. Measured:

| | same-day | lagged |
|---|---|---|
| cap 24.8% (platform) | **7.194** | 2.514 |
| cap 20.0% (house rule) | **6.250** | 2.513 |

**Costs 0.94 Sharpe on the same-day branch, nothing on the lagged one.**
Recommendation: the 25% cap. VBIL is a T-bill fund at 0.28% volatility — the
blow-up risk a concentration limit guards against is not present here. Decide it
explicitly rather than by default.

---

# 2 · Why this works

StockTrak computes `(mean daily return − rf) / sd(daily return) × √252`, with
`rf` taken from the session's cash-interest setting — **0%**. The numerator is
therefore not excess return. It is *all* return.

Under a normal rf of ~3.6%, a T-bill fund earns roughly the risk-free rate, its
excess return is ~zero, and its Sharpe is ~zero — the most useless asset you can
own. Remove the subtraction and the same fund keeps 3.64% while moving 0.28% a
year. **The lowest-volatility assets become the highest-scoring assets.**

For a bond fund:

```
return      ≈ carry − duration × Δyield
volatility  ≈ duration × σ(Δyield)
⟹ Sharpe@rf0 ≈ carry / (duration × σ(Δyield))
```

The denominator scales **linearly** with duration; the numerator only with the
slope of the yield curve, which flattens. The ratio is maximised as duration → 0.

| ticker | SEC yield | duration | ann vol | **Sharpe @ rf=0** |
|---|---|---|---|---|
| **VBIL** | 3.64% | ~0.0 | 0.28% | **12.6** |
| **VGUS** | 3.77% | 0.1 | 0.32% | **11.4** |
| **VUSB** | 4.50% | 0.5 | 0.74% | **5.9** |
| VGSH | 4.37% | 1.6 | 1.42% | 3.1 |
| VSDB | 4.98% | 1.8 | 1.85% | 2.6 |
| VCIT | 5.62% | 4.0 | 4.78% | 1.2 |
| VCLT | 6.31% | 5.5 | 9.68% | 0.7 |
| EDV | 5.64% | 10.3 | 17.09% | 0.3 |

**VBIL → EDV: yield ×1.55, volatility ×60.** Arithmetic on published yields and
measured volatility — not a forecast.

Scanning **all 116 Vanguard ETFs**, only three are under 1% volatility, and all
three go to the cap. Cash ranks next: it earns 0% and moves 0%, so it beats the
duration-bearing alternatives for the marginal dollar.

> **VBIL (12.6) → VGUS (11.4) → VUSB (5.9) → cash → VGSH (3.1) → VSDB (2.6)**

**VFMV is deliberately not in that ordering.** On carry over volatility it scores
**0.15** (1.48% SEC yield, 8.76% volatility) and would rank last in the universe.
It is held for a different job: it is equity and pays **quarterly**, so it dilutes
the monthly ex-date sawtooth (§5) without adding a monthly dip of its own. 5% is
the largest size whose benefit survives stripping out the equity premium — beyond
that it becomes a directional bet.

*(An earlier draft listed "VFMV (2.0)" in the ordering. That figure was VTIP's
realised Sharpe, carried over when VTIP was replaced, and it was a realised
return — precisely the kind of estimate this document claims never to make.)*

### A note on volatility figures

Three different numbers are derivable for this book and they measure different
things. **The book's volatility is 0.63% annualised** — the simulated account's
realised volatility under same-day crediting over the matched windows, which is
the figure consistent with the headline Sharpe of 7.11 (4.57% return / 0.63%).
Under lagged crediting it is **1.68%** (4.58% / 1.68% = 2.72). The **2.62bp
clean-day figure in §5 is a decomposition**, not the book's volatility — it is
what volatility would be with ex-date days removed, and exists only to show how
much of the lagged-branch variance the sawtooth accounts for.

---

# 3 · Why not a high-return sleeve

The instinct to "add growth for upside" is correct in a *return* contest and
backwards in a *Sharpe* one. Volatility is the denominator: adding risk does not
buy a fatter right tail, it divides your score.

To match our 7.11, a rival would need:

| | volatility | required annualised | over the 31-day window |
|---|---|---|---|
| lowest-vol rival | 10.4% | **77%** | 9.4% |
| median rival | 13.1% | **96%** | 11.9% |
| highest-vol rival | 15.6% | **115%** | 14.1% |
| **us** | **0.63%** | 4.6% | **0.56%** |

A 14%-vol equity book needs a **12% melt-up in six weeks** to draw level. That
occurred in 1 of 15 historical cohorts. We need 0.55%, which is contractual
carry and has landed in 15 of 15.

This also inverts the usual tournament logic. In a return contest you take
variance because mid-pack pays the same as last. Under Sharpe the gamble hits
the denominator before it ever reaches your rank.

---

# 4 · Book A vs Book B — and what decided it

Two books were built independently.

| | whose | what |
|---|---|---|
| **Book A** | ours | VBIL/VGUS/VUSB at the cap + VGSH, VSDB, VFMV |
| **Book B** | teammate's | "The Covariance Budget" — 10 holdings, max-diversification on semi-covariance + HRP |
| Merged | 75/25 | A's six funds + B's three sectors. Equity sleeve 5% → 16.6% |
| Conditional | deferral | Hold A; upgrade on 2 Oct only if 1 Oct shows a lag |

**The merge was not a synthesis of philosophies.** It drops VSDM, EDV, BNDX, VPL
and VCSH — five of B's ten — and keeps only the three sectors. It is Book A with
one dial turned, and framing it otherwise obscured the real question.

## 4.1 The catch: B's 1.358 figure

Book B page 4: *"a pure cash-like book scores Sharpe 1.358 — worse than our core
(1.668) and worse than just buying VTI (1.499)."* That sentence justified
rejecting the entire short-duration approach.

It is a **regime artefact.** B's backtest spans 2004–2026:

| era | mean 3-month bill |
|---|---|
| 2004–2007 | 3.40% |
| **2009–2015 (ZIRP)** | **0.08%** |
| 2016–2019 | 1.31% |
| **2020–2021 (ZIRP-2)** | **0.09%** |
| 2022–2026 | 3.98% |
| **today** | **3.97%** |

**40.1% of that sample had bills below 0.25%. 49.9% below 1.00%.**

A bill fund's Sharpe at rf = 0 is yield ÷ volatility: **0.2 at ZIRP, 13.2 at
today's 3.97%.** Averaging that ratio across an era two-fifths zero-rate produces
1.358 — a number describing the 2010s, not Sept–Nov 2026. Re-run on the current
regime, Book A scores **7.19**.

Not a methodology failure. B's process was more rigorous than ours. One missed
regime check, sitting under the conclusion that decided everything above it.

### Two consequences inside B's own book

- **VSDM at 18.41%, B's largest position.** A municipal fund yielding 3.48%
  against VGSH's 4.37% at similar duration. Municipal yields are lower *because*
  the income is tax-exempt, and **there are no taxes in a simulation** — 89bp
  given away for nothing, 16.4bp of portfolio carry.
- **EDV at 4.31% in a hiking cycle.** B's own regime work found the bond sleeve
  averages −3.1% annualised with only short duration positive. EDV: 10.3 years
  duration, 17.1% volatility, realised Sharpe **−0.61**.

Both follow from *"never forecast returns"* applied to SEC yield. But SEC yield
is **not a forecast** — it is a published yield-to-maturity that realises with
high fidelity over eight weeks. B's own DGU reading says the critique is about
the mean vector; contractual carry is not a mean estimate.

> **The merged principle, better than either document alone:
> never estimate expected returns — except contractual carry, which is not an estimate.**

## 4.2 The tests

All on **73 matched windows**: 31 scored days (36 trading days minus the 5-day
warm-up) containing exactly 2 ex-dates — the shape of 18 Sep → 6 Nov. Integer
shares, $10 commissions, measured half-spreads, cash at 0%. Rank against **17
real competitor portfolios** exported 17 Sep plus 49 simulated books, 67 teams.

**Head-to-head, real returns**

| book | branch | median Sharpe | ann vol | P(neg) | median rank | P(top 7) |
|---|---|---|---|---|---|---|
| **A** | same-day | **7.11** | 0.63% | **0%** | **1st** | **88%** |
| | lagged | 2.72 | 1.68% | 0% | 4th | 54% |
| **B** | same-day | 2.85 | 6.05% | **20%** | 8.5th | 49% |
| | lagged | 2.75 | 6.16% | 20% | 10th | 49% |
| Merged | same-day | 5.08 | 1.56% | 0% | 2nd | 81% |
| | lagged | **3.55** | 2.13% | 0% | **3rd** | **75%** |
| VTI | same-day | 2.25 | 11.2% | 28% | 18th | 7% |

114 windows of 36 trading days, delay reading, anchored at entry.

**The demeaning test — this is what decided it.** Equity returns re-centred so
no fund gets credit for having won in-sample, vol and correlation preserved:

| book | returns | same-day | lagged |
|---|---|---|---|
| **A (5% sleeve)** | real | 7.19 | 2.51 |
| | **demeaned** | **6.67** | **2.31** |
| Merged (16.6%) | real | 4.97 | 3.41 |
| | **demeaned** | **3.47** | **2.26** |

**A loses 7% to demeaning. The merge loses 30%.** Demeaned, A beats the merge on
both branches. The merge's lag protection was VDE (+46% in sample) and VGT
(+39%) — a directional bet, not diversification. This is the test Book A already
used to cap VFMV at 5%, and which we failed to apply to our own merge.

**The conditional upgrade — tested, fails**

| strategy | lagged: median rank | lagged: P(top 7) |
|---|---|---|
| Book A | **7th** | **50.7%** |
| Conditional | 9th | 49.3% |
| Merged | 3rd | 69.9% |

Worse than simply holding A — and the reason is **not** timing.

An earlier draft argued the conditional fails because the information arrives too
late: you can only observe on 1 October, by which point that sawtooth is already
in the series. **That argument is falsified by our own dates table (§8).** VFMV
pays quarterly and its recent ex-dates are 24 Sep 25, 26 Sep 24, 21 Sep 23 — so a
late-September 2026 ex-date is likely, inside the warm-up and *before* both bond
ex-dates. Crediting behaviour would be observable around 24 September, ahead of
any damage.

**The robust reason is the demeaning result.** Merged scores **2.26** on the
lagged branch demeaned, against Book A's **2.31**. You would be switching into
something with no real advantage — paying a transition day and $120 to move
sideways. The conditional fails because its destination is not better, not
because the signal is slow.

**Cut size** — tested across {4, 6, 7, 10, 15}. The ordering of candidates is
stable at every cut. No value of N flips the winner.

**Entry date — closed.** A timing idea was examined: enter on 24 September so
the 1 October ex-date falls inside the warm-up, dropping the dip while keeping
the recovery. **It only works under the exclusion reading.** Under delay, which
is the reading we adopt, waiting to the 24th costs **−6.2% of P(top 7) on both
branches** with no offsetting gain. Swept across every entry date from 18 Sep to
1 Oct and both readings; under delay, earlier is better at every date.
**Trade now.**

---

# 5 · The one live uncertainty: distribution crediting

StockTrak marks *portfolio value*. A bond ETF's price drops by its distribution
on the ex-date. If cash is credited same-day the two cancel. If it lands on the
pay date two days later, the account dips and recovers.

**Under lag, 92% of our variance is that sawtooth** — excluding days near an
ex-date our daily volatility is 2.62bp; including them, 9.48bp.

**It cannot be engineered away.** All 29 Vanguard bond ETFs — including the
municipals and target-maturity funds — go ex on the 1st with a 2-day lag. There
is no off-cycle fund to stagger into.

| branch | median Sharpe | median rank | P(top 7) |
|---|---|---|---|
| same-day (value does not dip 1 Oct) | **7.11** | **1st of 67** | 88% |
| 2-day lag (dips, recovers ~5 Oct) | 2.72 | 4th of 67 | 54% |

### How to observe it — two tests, two different places to look

**Around 24 September — VFMV's ex-date. Check the CASH line, not portfolio value.**
VFMV's distribution is ~$0.41/share, about **$35 on 86 shares = 1.4bp** of the
account. That is invisible in total portfolio value. The test is whether $35
appears in cash on the ex-date or two business days later.

**Thursday 1 October — the bond ex-date. Check portfolio VALUE.** VBIL prints
about −21¢ and the whole bond sleeve goes ex together, roughly **30bp** of the
account. Either total value dips that day or it holds flat. This is the
definitive test, and it is visible without inspecting the cash line.

---

# 6 · Rebalancing: none — and a correction to our own argument

**We previously claimed rebalancing hurts because each rebalance injects a
transition day into the volatility denominator. That was wrong.** Tested by
running weekly rebalancing at zero cost:

| book | branch | static | full cost | 50% smooth | **ZERO cost** |
|---|---|---|---|---|---|
| Book A | same-day | 7.194 | 6.342 | 6.659 | **7.251** |
| Book A | lagged | 2.514 | 2.255 | 2.324 | **2.526** |

**Zero-cost rebalancing is neutral to slightly positive.** There is no transition
variance penalty — a rebalance between two similar portfolios produces no
anomalous return, so there is nothing for the denominator to pick up. Book B's
framing, that this is a turnover question, was right and ours was wrong.

**But the cost is not immaterial for this book, and that is the reconciliation:**

| | commissions | % of gross window return |
|---|---|---|
| weekly (6 cycles × 6 trades) | $360 | **26.2%** |
| fortnightly | $180 | 13.1% |
| **once** | **$60** | **4.4%** |

Our window return is 0.55% — **$1,375 on $250,000.** $360 of commissions is a
quarter of it, straight off the numerator. The same $360 against a 3% equity
return is 4.8%.

**B's "~12bp, immaterial" was correct for B's book and wrong for ours. Same
dollars, different denominator.** Weekly rebalancing costs 0.54 Sharpe even with
50% smoothing.

**Place once, hold to 6 November.** If the cadence is kept, the burden of proof
is a test showing rebalancing beats static hold on Sharpe *net of costs on this
book's return profile*.

---

# 7 · The field

17 real competitor portfolios, scored on the same metric over the same windows.

| | best | median | worst |
|---|---|---|---|
| rival Sharpe | **2.61** | 2.12 | 0.50 |
| rival volatility | 10.4% | 13.1% | 15.6% |

Aggregate positioning: **VGT 12.9%, VUG 12.0%, VOO 11.8%, VDE 11.6%.
Short-duration bonds: 3.4%.** No rival holds more than 22.6%; we hold ~87%.

Every rival earns 2–4% over the window against our 0.55% — four to eight times
our money — and still loses, because their denominator is 20× larger.

Their trade notes are unanimously about return: *"high torque for a simulation
this short"*, *"the extra edge we need to climb the leaderboard"*, *"to the
moon"*. Two teams run real quant processes; one holds VBIL as a small
*"liquid, low-volatility reserve"* — our entire thesis, stated correctly, sized
as a rounding error.

They are not wrong about the market. They are graded on a ratio whose
denominator they are all maximising.

---

# 8 · Dates

| date | event |
|---|---|
| **Wed 23 Sep** | **Workshop 1 with Vanguard professionals, 12–1pm.** Six days out. |
| ~Thu 24 Sep | VFMV quarterly ex-date likely — **first read on crediting, via the cash line** |
| **Thu 1 Oct** | Bond ex-date. VBIL ~−21¢. **Watch whether account value dips.** Definitive, answered at the close. |
| **Fri 2 Oct** | **Effective first-trade deadline.** The email says "Friday, October 3" — but 3 Oct 2026 is a **Saturday**. Confirm with Ozkan. |
| ~Mon 5 Oct | October pay date — confirm the actual lag here (see the November check below) |
| Mon 12 Oct | Workshop 2, 12–1pm |
| Wed 28 Oct | FOMC, inside the window. **No action** — duration is 0.25y, a surprise hike costs ~6bp |
| Mon 2 Nov | Second bond ex-date; pay expected Wed 4 Nov |
| **Fri 6 Nov** | Trading closes, 4pm |

**November pay-date check (not a risk).** The 2 Nov distribution only matters on
the lagged branch *and* only if the pay date slips past 6 Nov. All six holdings
run a verified **2-business-day** lag → Wed 4 Nov, inside. It would take 5
business days to land outside. Confirm the actual pay date when the October
cycle prints; five minutes.

---

# 9 · Errors we made and corrected

Included so this can be audited rather than trusted.

| error | how it surfaced | consequence if shipped |
|---|---|---|
| Ledoit-Wolf inflated VBIL's volatility **13×** | gap between ex-ante 2.69 and realised 8.2 | optimiser could not see the short end at all |
| `Muni` substring dropped VOX ("Com-**muni**-cation") | universe count | a sector ETF silently missing |
| Break scan rediscovered March 2020 for every fund | all breaks in one quarter | false methodology-break dates |
| 5% VFMV weights summed to 89.2% → 10.8% cash | compliance re-check | breach of the cash cap |
| Compared two books on mismatched bootstrap samples | reran on identical windows | reversed the conclusion |
| Claimed rebalancing costs transition **variance** | zero-cost test (§6) | wrong mechanism, right conclusion |
| Framed the merge as "75% A + 25% B" | teammate's review | hid that it was one parameter |
| Said the lag was observable "by 5 October" | teammate's review | wrong mechanism beside a right conclusion |
| Estimated the 20% house rule at "~0.4 Sharpe" | measured it | understated by more than half — it is 0.94 |
| **ORDER_TICKET.md went stale** (VTIP, old share counts) | file audit | **the wrong book would have been traded** |
| Three different volatilities (0.42 / 0.61 / 0.76%) for one book | teammate's review | a reader could derive three different Sharpes |
| "VFMV (2.0)" in the allocation ordering | teammate's review | VTIP's realised figure relabelled; 0.15 on the stated method |
| Rejected the conditional on a **timing** argument | teammate's review | contradicted by our own dates table (§4.2) |
| Dates table left out of chronological order (2 Oct above 1 Oct) | re-reading after the patch | introduced *while fixing* the previous row |
| Simulator used the **exclusion** warm-up (`.iloc[5:]`) while the brief §4.4 assumed **delay**; never reconciled | entry-date analysis | headline figures computed under an unstated and probably wrong reading (moves them <0.2) |
| Quoted a confident "P(exclusion) ≈ 30%" | pressed on it | a judgment about one sentence's wording, presented as if measured |

---

# 10 · What Book B got right

The decision went the other way; that is not a verdict on the work.

- The most rigorous methodology on the team: ~40 allocators, 135 out-of-sample
  windows, an append-only log with 14 recorded mistakes.
- The DGU reading — *"their critique is about the mean vector, not optimisation
  itself"* — is sharper than ours and is the correct framing.
- The selection-vs-weighting test (1/N on max_div's own picks scores 1.37 against
  its own 1.77) is a clean proof the edge is in sizing. We never ran it.
- Page 4's satellite-sleeve finding is the result that ultimately killed our own
  merge — we quoted B's flaws at length and failed to apply B's strongest finding
  to our own book until it was pointed out.
- Section 07 — admitting P(Sharpe > 1.5) spans 49.6–54.1% *including VTI* — is
  the most honest passage in any of these documents.
- The turnover framing on rebalancing was right where ours was wrong.
- The FOMC date and the 20% concentration discipline both came from B.

**The disagreement was never about rigour. It was one regime check, and it
happened to sit under the conclusion that decided everything else.**

---

# 11 · Honest framing

This is closer to scoring-artifact harvesting than portfolio management. We are
not paid for bearing risk — we are paid because the scoring rule forgot to charge
us for the risk-free rate. If a judge asks in November, that is the answer to
give rather than dressing it as a market view.

It is also, given the stated rules and the current rate regime, the correct play.
If bills were at 0.05% it would be worthless. They are at 3.97%.

---

*Reproduce anything here from `scripts/`. Working papers and the superseded merge
analysis are in `reports/`.*
