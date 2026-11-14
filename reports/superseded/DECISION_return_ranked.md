# Decision memo — return-ranked portfolio

> **Superseded in part:** international IS permitted (US-listed is the only
> requirement). Final book is in `ORDER_TICKET.md`.

**Resolved 17 Sep 2026: teams advance on percentage return, not Sharpe.**
This supersedes brief §9.1 and the entire short-end analysis in Phases 3–5.

## The short-end book is dead

| book | median 40d | p90 | P(>5%) | P(>8%) |
|---|---|---|---|---|
| §9.1 short-end (VBIL/VGUS/VUSB/VGSH) | 0.57% | 0.82% | **0.0%** | **0.0%** |
| any sensible equity book | ~3.2% | ~11–14% | ~40% | 21–28% |

Its ex-ante Sharpe of 7.4 is irrelevant. Under a return ranking it finishes last
with near-certainty. Do not build it.

## There is no edge to find

Cross-sectional rank IC of trailing return against forward 40-day return, 61 US
equity ETFs, 329 sample dates:

| signal | mean IC | t-stat | hit rate |
|---|---|---|---|
| 1-month | −0.017 | −0.79 | 49% |
| 3-month | −0.035 | −1.60 | 48% |
| 6-month | −0.005 | −0.22 | 48% |
| 12-month | +0.030 | +1.35 | 52% |
| 12−1 month | +0.031 | +1.41 | 51% |

Nothing is significant, and the t-stats are inflated by overlapping windows, so
the truth is weaker still. **Brief §9.2 is correct: this leaderboard is a
lottery.** Tested, not assumed.

## What the rules allow

With no predictive edge, expected return is identical across equity books
(~3.2% median for all of them). The only lever is variance, and the rules cap it
hard: 25% per position forces at least four holdings, long-only forbids
leverage, and Vanguard lists no leveraged, inverse or commodity product.

Maximum achievable volatility, enumerated over all 4-fund combinations of the 20
highest-volatility US equity ETFs, is stable across 1-, 2- and 3-year covariance
windows and always selects the same four funds:

**VGT, VFMO, VTWG, VBK — 22.9% annualised, 9.1% over 40 days**, against 6.6% for
simply holding VTI. Concentration buys 1.4× the market's volatility, not 3×.

## The book

| | VGT | VFMO | VTWG | VBK | VTWO | VXF |
|---|---|---|---|---|---|---|
| weight | 24% | 24% | 24% | 24% | 2% | 2% |
| shares | 504 | 267 | 226 | 178 | 43 | 21 |

Commission $60 · residual cash $737 (0.29%, cap 10%) · spread ≈ $237 · six
positions clears the five-trade minimum with one to spare · identical across all
four accounts.

Outcome distribution, 6,000 stationary-bootstrap draws:

| median | p10 | p90 | p99 | P(>8%) | P(>12%) | P(<−5%) |
|---|---|---|---|---|---|---|
| +3.20% | −8.01% | +13.71% | +25.22% | 28.4% | 14.4% | 17.2% |

## Be clear about what this is

The median outcome is +3.20%. Holding VTI gives +3.14%. **The concentration buys
almost nothing in expectation** — it raises P(top-decile outcome) from ~21% to
~28% and raises P(−5% or worse) from ~12% to ~17%. That is the correct trade
when only the top 5–10% advance, because finishing 40th and finishing 90th pay
the same. It is not a strategy, and it should not be presented as one.

## Two things to check

1. **International.** VPL, VEA and VXUS are US-listed on NYSE Arca and hold
   non-US equities. If the "US only" constraint was read from the rules rather
   than tested on the trade screen, it is worth typing VPL in — VPL carried the
   highest volatility of any Vanguard equity ETF and would improve the book.
2. **Team versus individual ranking.** If advancement is scored on the *team*
   pooled return, identical accounts are correct: pooling four identical books
   preserves the full 22.9% volatility, and that is what a tight cut rewards. But
   if any individual member advancing counts, four *different* concentrated books
   would give four independent lottery tickets instead of one. Worth asking.

> **SUPERSEDED 17 Sep 2026.** The organizer confirmed advancement is on
> **Sharpe ratio**, not return. This memo is kept only for the momentum and
> field-crowding analysis. The live book is in `ORDER_TICKET.md`.
