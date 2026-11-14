# Why we trade before tomorrow's open

**For: Aahan, Dhrubojeet, Shubham · Written 17 Sep 2026**

The book is settled. This document is about **when**, and the whole decision
turns on one ambiguous sentence in StockTrak's documentation. We worked it
through and the answer is: go now.

---

## The ask

Each of us places these six orders, **all four accounts, same day**, one
sitting, market orders.

| # | Ticker | Fund | **Shares** |
|---|---|---|---|
| 1 | **VBIL** | Vanguard 0-3 Month Treasury Bill ETF | **820** |
| 2 | **VGUS** | Vanguard Ultra-Short Treasury ETF | **819** |
| 3 | **VUSB** | Vanguard Ultra-Short Bond ETF | **1,250** |
| 4 | **VGSH** | Vanguard Short-Term Treasury ETF | **328** |
| 5 | **VFMV** | Vanguard U.S. Minimum Volatility ETF | **86** |
| 6 | **VSDB** | Vanguard Short Duration Bond ETF | **165** |

$229,462 invested · $60 commission · cash 8.19% (cap 10%).
Re-check share counts against live quotes before submitting.

---

# 1 · The sentence everything hangs on

StockTrak's own documentation, last line:

> *"We also only begin calculating the Sharpe Ratio 5 trading days after your
> first trade."*

That can mean two completely different things.

**Reading A — exclusion.** The first five trading days are **dropped from the
series**. Your score is computed only from day six onward. Anything that happens
in those five days never touches your Sharpe.

**Reading B — delay.** Every day from your first trade **counts**. The number is
simply not *displayed* until there are five days of data, because a standard
deviation on three observations is meaningless.

Same sentence. Opposite mechanics. And which one is true decides whether we
trade tomorrow or wait a week.

# 2 · Why it matters: there is a trick if Reading A is true

Our bond funds all go ex-dividend on **1 October**. On that day their price
drops about 0.3% and — if the platform credits the cash two days later — our
account value dips and then recovers. Both of those days land in our volatility,
which is the thing being divided by. It is the single biggest risk we have.

Now suppose the five days really are excluded. Then the entry date lets you
**position the dip inside the warm-up**:

| enter | warm-up covers | 1 Oct dip | ~5 Oct recovery |
|---|---|---|---|
| Fri 18 Sep | 21–25 Sep | scored | scored |
| **Thu 24 Sep** | **25 Sep – 1 Oct** | **dropped** | **scored** |
| Mon 28 Sep | 29 Sep – 5 Oct | dropped | dropped |

Entering on 24 September would throw away the **−0.3% day** and keep the
**+0.3% day**. Not a wash — one-sided, in our favour. We measured it as worth up
to **+31 percentage points** on our chance of a top-7 finish in the bad scenario.

That is a big enough prize that it was worth being sure about.

# 3 · What the wording actually says

Read the two sentences together, in order, as StockTrak wrote them:

> *"...**weekends are excluded from** the Sharpe Ratio calculation. We also only
> **begin calculating** the Sharpe Ratio 5 trading days after your first trade."*

For weekends they say **excluded from the calculation**. One sentence later, for
the five days, they say **begin calculating**. They had the exclusion word right
there and chose a different one. Different words, one sentence apart, almost
certainly mean different things.

Two more things point the same way:

- Their instruction for finding your average daily return is to export **"your
  historical performance"** from Graph My Portfolio — the whole series, not one
  starting on day six.
- There is an obvious engineering reason for a display gate and no obvious
  reason to throw away data. Excluding five days would hand every team a free
  option to watch the market for a week and then position, which the platform
  has no reason to offer.

**We are going with Reading B: the five days count.**

# 4 · What we measured, both ways

We swept every entry date from 18 September to 1 October, under both readings
and both crediting outcomes — 16 historical windows per cell. Median Sharpe:

| enter | A: excluded, same-day | A: excluded, lagged | B: counted, same-day | B: counted, lagged |
|---|---|---|---|---|
| **Fri 18 Sep** | 7.05 | 2.36 | **6.79** | **2.64** |
| Wed 23 Sep | 6.83 | 2.01 | 7.00 | 2.52 |
| **Thu 24 Sep** | 7.22 | **4.21** | 6.66 | 2.43 |
| Fri 25 Sep | 6.77 | 4.18 | 7.05 | 2.36 |
| Mon 28 Sep | 6.94 | 2.83 | 7.59 | 2.37 |

And translated into what we actually care about — chance of finishing top 7 of 67:

| | trade tomorrow | wait to 24 Sep | |
|---|---|---|---|
| **A: excluded**, same-day | 87.5% | 93.8% | +6.2% |
| **A: excluded**, lagged | 43.8% | **75.0%** | **+31.2%** |
| **B: counted**, same-day | 93.8% | 87.5% | −6.2% |
| **B: counted**, lagged | 56.2% | 50.0% | −6.2% |

**Under Reading A, waiting is a big win. Under Reading B, waiting costs us 6.2%
on both branches with no upside at all.**

Since the wording points at Reading B, waiting is a loss. And note the shape of
the bet even if you disagree: the gain is concentrated in one cell out of four,
and it only pays if the reading goes our way *and* the crediting goes against us.

# 5 · Two more reasons, smaller but pointing the same way

**The window only shrinks.** Scoring runs from your first trade to 6 November
and does not extend.

| | scored days | error on our Sharpe |
|---|---|---|
| **trade tomorrow** | **36** | **0.85** |
| wait to 24 Sep | 32 | 0.91 |
| wait to 2 Oct | 26 | 1.01 |

We expect to be near the top, so noise can only drag us back toward the field.

**We have to be holding the book on 1 October to learn anything.** The crediting
question resolves that day and it is the biggest open variable we have. Waiting
does not buy information — it forfeits it.

---

# 6 · What to do on Thursday 1 October

The bond funds go ex-dividend. VBIL will print about **−21¢**. That is normal
and it is not a loss — the value moves from price into cash owed to you.

**Just look at your total account value that day.**

- **Holds flat** → cash credited same-day. We score ~7.11 and sit **1st of 67**.
- **Dips ~0.3%, recovers around 5 Oct** → lagged. We score ~2.72 and sit ~4th.

Either way, do nothing. Tell Daksh what you saw.

This also settles Reading A vs B for us permanently: about a week after trading,
export from Graph My Portfolio and compute the Sharpe two ways — over every day
since the first trade, and from day six onward. Whichever matches the rankings
page is the answer.

---

# 7 · Quick reminder of why this book

With the risk-free rate set to **0%**, the Sharpe formula loses its subtraction
and collapses to `return ÷ volatility`. There is no hurdle, so the
lowest-volatility assets become the highest-scoring ones. VBIL earns 3.64% and
moves 0.28% a year: score 13. Going out to long bonds multiplies your yield by
1.55 and your volatility by **60**.

Against the 17 competitor portfolios we pulled: they score **0.50 to 2.61**, we
score **7.11**. Every one of them earns four to eight times as much money as us
over the window and still loses, because their denominator is twenty times
bigger.

# 8 · What we are not claiming

- **This is a scoring quirk, not investing skill.** We are not paid for bearing
  risk; we are paid because the rule forgot to charge us for the risk-free rate.
  That is the honest answer to give a judge in November.
- **The edge is regime-dependent.** It works because T-bills yield 3.97% today.
- **Reading B is a judgement about wording, not a fact.** If we are wrong, we
  gave up about 6% of our top-7 chance in one of four scenarios. We sized the
  decision so being wrong is cheap.

---

## After you trade

- **Do not rebalance.** ~0.54 Sharpe. On a book whose return is 55bp, $360 of
  commissions is 26% of what we earn.
- **Do not reinvest distributions.**
- **Check every ticker is Vanguard before submitting.**
- Confirm TeamRankings shows WolfPack at **$1,000,000** once the fourth account
  is live.

Full reasoning and every backtest: `reports/WOLFPACK_STRATEGY.md`.
