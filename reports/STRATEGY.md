# Strategy — WolfPack

**Scoring: Sharpe ratio** (Prof. Ozkan, 17 Sep 2026). **Risk-free rate: 0%.**

## The book

| # | Ticker         | Fund                                 | **Shares** | ≈ Cost |
| - | -------------- | ------------------------------------ | ---------------- | ------- |
| 1 | **VBIL** | Vanguard 0-3 Month Treasury Bill ETF | **826**    | $62,446 |
| 2 | **VGUS** | Vanguard Ultra-Short Treasury ETF    | **827**    | $62,463 |
| 3 | **VUSB** | Vanguard Ultra-Short Bond ETF        | **1,261**  | $62,495 |
| 4 | **VFMV** | Vanguard U.S. Minimum Volatility ETF | **87**     | $12,484 |
| 5 | **VGSH** | Vanguard Short-Term Treasury ETF     | **303**    | $17,474 |
| 6 | **VSDB** | Vanguard Short Duration Bond ETF     | **166**    | $12,480 |

8% cash · $60 commission · portfolio duration ~0.25 yrs · six positions.

## The core idea

With rf = 0, StockTrak's Sharpe is just `return ÷ volatility` — no hurdle. A
T-bill fund normally scores ~zero because its return *is* the risk-free rate and
the subtraction cancels it. Remove the subtraction and it keeps 3.6% while moving
0.28% a year. **The lowest-volatility assets become the highest-scoring assets.**

For a bond fund, `Sharpe ≈ carry / (duration × σ_yield)`. The denominator scales
linearly with duration; the numerator only with the slope of the curve, which
flattens. So the ratio maximises as duration → 0. Measured: **VBIL → EDV
multiplies yield ×1.55 and volatility ×60.**

Only three of the 116 Vanguard ETFs have volatility under 1% (VBIL 0.28%, VGUS
0.32%, VUSB 0.74%). All three go to the 25% cap. Cash ranks next — it earns 0%
and moves 0%, so it beats the duration-bearing alternatives. The allocation rule:

> VBIL (12.6) → VGUS (11.4) → VUSB (5.9) → **cash** → VGSH (3.1) → VSDB (2.6)

VFMV is the calibration described below.

## Methodology

Everything is measured, not assumed. Reproducible via `scripts/`.

**Data.** All 116 ETFs pulled from Vanguard's public JSON endpoint
(`investment-products/list/funddetail/all`) — SEC yields, expense ratios,
inception dates. Prices and dividends from yfinance; rates from FRED. Gated by
`vgdata.build()`, which refuses to proceed on unresolved data-quality flags.

**Account simulation, not return math.** `vgdata.sawtooth` walks the account
forward day by day exactly as the platform marks it: integer shares only, $10
commission per trade, entry across the measured half-spread, cash at 0%,
distributions never reinvested.

**Backtest design.** Monthly cohorts and matched windows — 31 scored days
(36 trading days minus the 5-day warmup) containing exactly 2 ex-dates, which is
what 18 Sep → 6 Nov gives us. Every candidate is run over the same windows.

**Competitive benchmark.** 17 real competitor portfolios exported from StockTrak
on 17 Sep, scored on the same metric over the same windows, plus 49 simulated
equity books to fill the 67-team field. We measure *rank*, not absolute Sharpe.

**Guarding against our own bias.** Where a result could come from hindsight, we
re-ran it with returns demeaned so no fund gets credit for having won in-sample.
That is how we caught that most of the apparent benefit of a large equity sleeve
was just the equity premium.

**Things this process caught that would otherwise have shipped:**

- Ledoit-Wolf shrinkage inflates VBIL's volatility **13×** in a mixed universe,
  hiding the entire trade from the optimiser. Fixed by shrinking the correlation
  matrix and preserving sample variances.
- A `Muni` substring filter silently dropped VOX ("Com-**muni**-cation").
- A break-detection scan that just rediscovered March 2020 until normalised by
  volatility.
- Weights that summed to 89%, leaving 10.8% cash — over the organiser's cap.

## What we tested and rejected

| approach                                | result                                                                                                                                   |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **1/N** (DeMiguel-Garlappi-Uppal) | **Ties us** on the right 4 funds (8.64 vs 8.84). Over all 6 funds: 6.01. Weighting barely matters; universe selection is the edge. |
| **HRP** (López de Prado)         | A wash (9.27 vs 8.84, lower hit rate). Its advantage needs an ill-conditioned covariance; we have 6 assets and 365 observations.         |
| Return-maximising book                  | Momentum rank IC is null at 40 days (best t-stat 1.41). That leaderboard is a lottery.                                                   |
| Higher carry / longer duration          | Volatility rises faster than yield. Monotone loss.                                                                                       |
| Municipals, target-maturity             | Every one pays on the 1st too. No escape from the ex-date.                                                                               |

## The calibration: why VFMV

StockTrak marks *portfolio value*. A bond ETF's price drops by its distribution
on the ex-date. If cash is credited same-day the two cancel; if it lands on the
pay date 2 days later, the account dips and recovers — and **92% of our
lagged-branch variance is that sawtooth**.

All 29 Vanguard bond ETFs pay on the 1st, so it cannot be diversified or timed
away. VFMV can dilute it: it is equity (8.8% vol, low for equity) and pays
**quarterly**, so it adds no monthly dip.

| book              | same-day                  | lagged                     |  |  |
| ----------------- | ------------------------- | -------------------------- | - | - |
|                   | median / rank / P(top7)   | median / rank / P(top7)    |  |  |
| 0% VFMV           | 9.68 / 1st /**93%** | 2.08 / 15.5th / 45%        |  |  |
| **5% VFMV** | 7.36 / 1st /**88%** | **2.52 / 6th / 54%** |  |  |
| 10% VFMV          | 5.34 / 1st / 81%          | 2.58 / 4th /**60%**  |  |  |

**5% is the chosen size because it is the only one whose benefit survives
demeaning** (2.27 vs 2.08 with the equity premium stripped out). Beyond 5%,
roughly half the gain is an undisclosed bet on equities rising. 5% turns a miss
into a make on the bad branch for 5 points on the good one.

## Where we stand

Scored on Sharpe over matched windows, the 17 real competitor books range
**0.97 to 3.25, median 2.09**. Their trade notes are unanimous — every team is
optimising for return: *"high torque for a simulation this short"*, *"to the
moon"*, *"the extra edge we need to climb the leaderboard"*. Aggregate field
positioning is VGT 12.9%, VUG 12.0%, VOO 11.8%, VDE 11.6%. **Short-duration
bonds: 3.4%.** No team holds more than 22.6%; we hold ~92%.

**Blended P(top 7 of 67):**

| P(same-day crediting) | 0% VFMV | **5% VFMV** | 10% VFMV |
| --------------------- | ------- | ----------------- | -------- |
| 50%                   | 69.1%   | **70.8%**   | 70.5%    |
| 70%                   | 78.7%   | **77.8%**   | 74.8%    |
| 85%                   | 85.9%   | **83.0%**   | 78.0%    |

A random team is 10%.

## The competition, scored

All 17 competitor portfolios exported 17 Sep, run through the identical
simulator over the same 144 matched windows. Volatility and window return are
medians; Sharpe is on the same-day branch.

| team               | holds | top 3            | ann vol         | window ret | **Sharpe** |
| ------------------ | ----- | ---------------- | --------------- | ---------- | ---------------- |
| **WOLFPACK** | 6     | VBIL, VGUS, VUSB | **0.61%** | 0.55%      | **7.36**   |
| 10                 | 1     | VUG              | 14.7%           | 3.92%      | 3.25             |
| 3                  | 5     | VGT, VUG, VOO    | 14.4%           | 4.30%      | 2.96             |
| 5                  | 13    | MGV, VUG, VOOG   | 12.1%           | 3.30%      | 2.60             |
| 11                 | 5     | VOO, VGT, VONV   | 14.1%           | 3.97%      | 2.53             |
| 16                 | 6     | VGT, VAW, VDC    | 13.1%           | 3.29%      | 2.26             |
| 17                 | 3     | VDE, VTI, VTG    | 11.6%           | 2.74%      | 2.23             |
| 12                 | 5     | VOO, VUG, VGT    | 13.9%           | 3.40%      | 2.20             |
| 13                 | 5     | VTV, VOO, VGSH   | 10.4%           | 2.47%      | 2.12             |
| base               | 9     | VBIL, VUG, VOO   | 10.6%           | 2.45%      | 2.09             |
| 15                 | 13    | VGT, VFVA, VDE   | 11.5%           | 2.71%      | 2.06             |
| 9                  | 10    | VOO, VDE, VGT    | 13.1%           | 2.39%      | 1.74             |
| 2                  | 7     | VGT, VFMO, VFMF  | 14.3%           | 2.85%      | 1.74             |
| 1                  | 21    | VHT, VTV, VGT    | 11.7%           | 2.13%      | 1.68             |
| 8                  | 5     | VFH, VHT, VGT    | 14.0%           | 2.63%      | 1.66             |
| 6                  | 9     | VFVA, VGT, VAW   | 14.1%           | 2.10%      | 1.30             |
| 18                 | 10    | VTV, VDE, VOO    | 12.8%           | 1.96%      | 1.20             |
| 4                  | 2     | VTI, VDE         | 15.6%           | 1.69%      | 0.97             |

**Best rival 3.25 · median 2.09 · worst 0.97.** Rival volatility spans
10.4–15.6%; ours is 0.61%. On the lagged branch we fall to 2.52 — still above
the median rival, below the top four. That gap is the entire reason for the
VFMV sleeve.

Note what the table shows: **every rival earns 2–4% over the window and we earn
0.55%.** They make four to eight times our money and still lose, because the
denominator is 20× larger.

## Why a high-return, high-risk sleeve is not sensible

The instinct — "add a growth sleeve for upside" — is correct in a *return*
contest and backwards in a *Sharpe* one. Volatility is the denominator. Adding
risk does not buy a fatter right tail; it directly divides your score.

Concretely, to match our 7.36 a rival would need:

|                   | volatility      | required annualised return | over the 31-day window |
| ----------------- | --------------- | -------------------------- | ---------------------- |
| lowest-vol rival  | 10.4%           | **77%**              | 9.4%                   |
| median rival      | 13.1%           | **96%**              | 11.9%                  |
| highest-vol rival | 15.6%           | **115%**             | 14.1%                  |
| **us**      | **0.61%** | **4.5%**             | **0.55%**        |

A 14% equity book would have to return **12% in six weeks** just to draw level.
That is not a bull market, it is a melt-up — it happened in 1 of 15 historical
cohorts. Meanwhile we need 0.55%, which is contractual carry and has landed in
**15 of 15**.

This is also why the tournament logic that governs a return leaderboard is
inverted here. In a return contest, when only the top few advance, you take
variance because being mid-pack pays the same as being last. Under Sharpe,
variance is taxed directly — you cannot gamble your way up, because the gamble
shows up in the denominator before it shows up in the rank.

The one exception is the VFMV sleeve at 5%, and note *why* it qualifies: it is
not there for upside. It is there because it pays quarterly and therefore
dilutes the ex-date sawtooth. Its benefit survives stripping out the equity
premium entirely (2.27 vs 2.08). We took the smallest size where that is true.
Anything larger is an equity bet wearing a risk-management costume.

## Rebalancing: none

Every trade adds a transition day to the volatility series — directly the thing
being scored. Drift is 0.3% at worst. Distributions (~$700/mo) accumulate as
cash, taking us 8.0% → 8.6%, still inside the cap, and mildly *helping* the
ratio. Do not reinvest.

## Risks

- **Distribution crediting.** The live one. 1 October settles it: VBIL prints
  ~−21¢; watch whether account *value* dips.
- **rf ≠ 0.** The load-bearing assumption. Confirmed from session settings.
- **Imitation.** Two teams already hold a little VBIL. If several go
  short-duration before 3 October, the ranking among us becomes noise.
- **Sample.** 144 matched windows, 17 of 67 real portfolios.

## Honest framing

This is closer to scoring-artifact harvesting than portfolio management. We are
not paid for bearing risk; we are paid because the scoring rule forgot to charge
us for the risk-free rate. That is the answer to give if a judge asks — and it is
still, given the stated rules, the correct play.

---

## Appendix: the field, in their own words

Every team leaves notes on their trades. I read all 16 sets. They are, almost
without exception, a return contest being played very enthusiastically inside a
Sharpe contest.

**The vibes desk.** Team 3 holds VGT, VUG, VOO, and their complete investment
thesis, in order, is: *"could be good"*, *"Bottom is in"*, *"Going up"*, *"Going
to the moon"*, *"To the moon"*, *"to mars"*, *"to saturn"*, *"to neptune"*, *"to
pluto"*. They ran out of planets before they ran out of capital. Sharpe: 2.96.

**The self-aware one.** Team 4's notes are the most honest on the board: *"High
risk wildcard. Smaller companies are super volatile, but if the market rallies,
they can spike massively and give us the extra edge we need to climb the
leaderboard."* They also brag about using VOX to *"sneak in heavy exposure to
internet giants without violating the concentration limit."* They correctly
identified the constraint, correctly engineered around it, and pointed the
result at the wrong metric. Two holdings, 15.6% volatility, **Sharpe 0.97 —
dead last.**

**The group chat.** Team base's notes include *"One day, or Day 1?"*, *"ITS
TIME!"*, *"Jacks idea"*, and — three trades later — *"Jacks an idiot"*. Also
*"candle sticks"* and *"not feeling it yet"*. They hold VBIL, so somebody there
has an instinct. Sharpe 2.09.

**Genuinely good process, wrong objective.** Team 5 is running real quant work:
factor ETFs, limit orders, explicit position sizing, *"VFMF... I believe it is
best risk-adjusted yet high return option."* They say **risk-adjusted** out
loud. Then: *"VGT has a 1yr return of 44.9%... high torque for a simulation this
short."* Torque is exactly what you do not want. Sharpe 2.60.

**The closest anyone gets.** Team 9 runs mean-reversion scores, RSI, momentum
scores, and writes: *"BUY: Keep a liquid, low-volatility reserve that earns
short-term Treasury income."* That is our entire thesis, stated correctly, sized
as a rounding error next to VOO, VDE and VGT. Sharpe 1.74.

**Macro that is right and irrelevant.** Team 15: *"I am buying VGT as investors
shift away from fixed income investments amidst rate hikes."* Team 14: *"rally
post hike. hike is new cut."* Team 1: *"The market is currently pricing in a rate
hike this week with an 80% chance."* The macro reads are sharp. They just feed
into an objective nobody checked.

### What they are doing vs what we are doing

|                       | the field                                  | us                        |
| --------------------- | ------------------------------------------ | ------------------------- |
| optimising for        | return                                     | Sharpe                    |
| aggregate positioning | VGT 12.9%, VUG 12.0%, VOO 11.8%, VDE 11.6% | VBIL/VGUS/VUSB 75%        |
| short-duration bonds  | **3.4%** of field assets             | **~87%**            |
| volatility            | 10.4–15.6%                                | **0.61%**           |
| window return         | 1.7–4.3%                                  | 0.55%                     |
| thesis                | AI, energy, rate hikes, planets            | rf = 0 removes the hurdle |

They are not wrong about the market. Energy really is up on the Strait of
Hormuz; tech really did sell off; financials really do benefit from hikes. Every
one of those calls could be correct and it would not matter, because they are
being graded on a ratio whose denominator they are all busy maximising.

We are not smarter about the market than they are. We read the rulebook.
