# Phase 3 - the distribution sawtooth, sized

Generated 2026-09-17 00:14.

Brief S9.1 says the volatility of a T-bill book "cannot be stated until V1 is
resolved" - V1 being an October observation of whether StockTrak credits a
distribution on the ex-date or on the pay date. It can be stated now, as a
two-branch answer, by simulating the account exactly as the platform marks it:
integer shares, cash at 0%, no reinvestment, entry across the spread.

## The mechanism

- Every bond ETF's price falls by the distribution on its ex-date. Measured on VBIL: **-21c on a $75.60 price, about -29 bp**, on each of 2026-06-01, 07-01, 08-03 and 09-01. Every other day moves +1 to +3c.
- The quote feed confirms **no fund pays on its ex-date**: the lag is 2 days for 52 of 98 funds, 3 for 3, 4 for 18 and 5 for 25.
- StockTrak charts unadjusted prices, and the sawtooth is plainly visible on its own VBIL candles, so the price leg definitely reaches the account.
- What is *not* yet known is the cash leg: a simulator may credit on the ex-date regardless of the real pay date.

## The two branches

Brief S9.1 weights, 65 rolling 40-day windows over the funds' common history (2025-04-03 to 2026-09-16), rf = 0:

|          |   median |   p10 |   p90 |   mean |   frac_below_2.0 |   windows |
|:---------|---------:|------:|------:|-------:|-----------------:|----------:|
| ex_date  |      8.2 |  3.86 | 11.54 |   7.68 |             0.02 |        65 |
| pay_date |      2.4 |  1.43 |  3.5  |   2.47 |             0.29 |        65 |

The mean return is identical under both branches - a late payment changes when
value arrives, not how much. The entire gap is volatility. Under same-day
crediting the price drop and the cash credit cancel and sigma falls to the tick
quantisation floor; under lagged crediting the account dips the full 29 bp and
recovers two days later, putting four outlier days into a series whose other
days move about 1 bp.

**Both branches clear the brief's 1.5-2.0 historical winning band** (S6.4), so
the short-end book is the right structure either way. The branch decides the
margin, not the direction.

## Per fund, most recent 40 days

|                      |   sharpe |   mean_bp |   sd_bp |   worst_day_bp |
|:---------------------|---------:|----------:|--------:|---------------:|
| ('VBIL', 'ex_date')  |    17.93 |      1.41 |    1.25 |          -1.32 |
| ('VBIL', 'pay_date') |     2.37 |      1.42 |    9.47 |         -29.04 |
| ('VGUS', 'ex_date')  |    16.74 |      1.28 |    1.21 |          -1.32 |
| ('VGUS', 'pay_date') |     2.04 |      1.28 |    9.95 |         -30.56 |
| ('VUSB', 'ex_date')  |     4.17 |      0.95 |    3.61 |         -10.01 |
| ('VUSB', 'pay_date') |     1.25 |      0.96 |   12.18 |         -40.05 |
| ('VGSH', 'ex_date')  |    -0.68 |     -0.34 |    7.99 |         -24.05 |
| ('VGSH', 'pay_date') |    -0.41 |     -0.34 |   13.1  |         -37.77 |
| ('VSDB', 'ex_date')  |    -1.42 |     -0.89 |    9.94 |         -29.57 |
| ('VSDB', 'pay_date') |    -0.83 |     -0.88 |   16.93 |         -52.48 |

VBIL and VGUS carry the result. They are the only two funds whose daily return
series is dominated by price quantisation rather than by duration: at a $75.60
price one cent is 1.32 bp, against a daily return standard deviation of 1.79 bp.
VGSH and VSDB carry real duration and print negative Sharpe over this particular
window, though across all rolling windows they are negative in only 8-9% of them.

## What this changes

1. **October is a confirmation, not a blocker.** Both branches are sized, and the portfolio structure is the same under either. Nothing waits on it.
2. **The ex-date is 1 October**, two days before the first-trade deadline. If the book is built before then, the observation is free.
3. **What to watch on 1 October:** VBIL should print about -21c. The question is whether the *account value* dips that day. If it stays flat, we are on the ex_date branch and the expected Sharpe is around 8; if it dips and recovers on 5 October, we are on the pay_date branch and it is around 2.4.