# ORDER TICKET — WolfPack

**This is the only file to trade from.** Rationale lives in `DECISION_RECORD.md`.

Scoring: **Sharpe ratio** (Ozkan, 17 Sep). Risk-free rate: **0%**.
Every member places these six orders. All four accounts identical.

## The six orders — per $250,000 account

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

**Share counts priced 17 Sep. Re-check against live quotes before submitting —
the weights are the decision, not the share counts.**

## Unresolved before you place

**Position cap: 24.80% or 20%?** The platform allows 25%. Book B's document sets
a 20% house rule, which is not a competition constraint. Measured cost of the
house rule: **0.94 Sharpe on the same-day branch, zero on the lagged branch.**
Recommendation is the 25% cap — VBIL is a T-bill fund at 0.28% volatility, so
the blow-up risk a concentration limit guards against is not present. **Settle
this explicitly.** If the house rule wins, the three large positions go to 20%
and the remainder to VGSH.

## Checklist

- [ ] All six are Vanguard funds — the platform will fill SPY without complaint
- [ ] Market orders, one session, all six together
- [ ] Identical in **every** account
- [ ] **Do not rebalance.** Weekly rebalancing costs 0.54–0.85 Sharpe, and the
      mechanism is commissions against a 55bp window return, not volatility
- [ ] Do not reinvest distributions
- [ ] Someone turn off Book B's rebalance script before **Thu 24 Sep**

## Dates

| date | event |
|---|---|
| **Fri 2 Oct** | **Effective first-trade deadline** — the email says "Friday, October 3" but 3 Oct 2026 is a **Saturday**. Confirm with Ozkan. |
| ~late Sep | VFMV quarterly ex-date likely falls in the window |
| **Thu 1 Oct** | Bond ex-date. VBIL prints ~−21¢. **Watch whether account value dips that day** — that is the whole open question, and it is answered at the close. |
| Mon 12 Oct | Workshop |
| Wed 28 Oct | FOMC, inside the window. No action. |
| Mon 2 Nov | Second bond ex-date; pay date expected Wed 4 Nov (2 business days), inside the window |
| **Fri 6 Nov** | Trading closes, 4pm |

## Expected outcome

| distribution crediting | median Sharpe | median rank of 67 |
|---|---|---|
| same-day (value does not dip 1 Oct) | **7.19** | **1st** |
| 2-day lag (value dips, recovers ~5 Oct) | 2.51 | 7th |

Measured over 73 matched windows against 17 real competitor portfolios. The 17
rivals score 0.97 to 3.25, median 2.09.
