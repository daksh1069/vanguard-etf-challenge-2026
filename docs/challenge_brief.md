---
title: "2026 Vanguard ETF Fall Trading Challenge"
subtitle: "Team WolfPack, NC State University: Rules, Scoring Mechanics, ETF Universe and Strategy Brief"
date: "Compiled 16 September 2026"
geometry: margin=0.9in
fontsize: 10pt
colorlinks: true
toc: true
toc-depth: 2
---

\newpage

# 1. Purpose of this document

I went through the rules, the StockTrak platform settings and the Vanguard lineup so the rest of you do not have to. This is that legwork written down in one place.

Read Sections 2 through 4 and Section 10. That is the part that affects what you do. The rest is reference: Section 7 tells you where the fund data lives, Section 11 is for whoever runs the analysis, and Section 12 is the short list of what is still unknown.

Everything here is current as of 16 September 2026. Trading opened on 14 September, so the window is already running.

## 1.1 Status

| Item | Status |
|---|---|
| Competition rules and dates | Settled, Section 2 and 3 |
| StockTrak platform parameters | Settled, Section 3.2 |
| How Sharpe is calculated | Settled, Section 4.2 |
| Risk-free rate used in scoring | Settled at 0%, Section 4.3 |
| Team aggregation | Settled, Section 4.5 |
| Fund universe and data source | Settled, Section 7 |
| Execution approach | Settled, Section 10 |
| **Which ranking we are scored on** | **Work in progress. Answer expected at the 23 September workshop.** |

That last line is the only thing genuinely open, and it is the one that decides what we buy. Everything in Section 9 waits on it. Nothing else does.

## 1.2 One note on numbers

This document deliberately carries very few figures. Expense ratios, SEC yields, returns and prices go stale, and earlier drafts mixed sourced data with volatility estimates that were guesses. All live fund data now comes from the Vanguard page linked in Section 7.1. All risk figures come from the covariance run in Section 11. Where a claim here rests on a number, either the number is sourced and dated or the claim is stated directionally and flagged as not yet quantified.

# 2. Competition structure

## 2.1 What this is

The Vanguard ETF Challenge is hosted by Temple University's Fox School of Business and sponsored by The Vanguard Group. It is an annual trading simulation, open internationally, in which student teams manage a virtual portfolio built exclusively from Vanguard ETFs. It runs in two phases:

1. **Trading phase.** Teams manage simulated capital over roughly eight weeks via StockTrak. Teams are ranked on portfolio performance.
2. **Pitch phase.** The top performing teams design their own international ETF and present it to a panel of judges drawn from Vanguard and the Fox School.

Historically the pitch round has been a substantive judged event rather than a formality. In past editions a small number of finalist teams gave short presentations with a question-and-answer segment, and the judging panel selected the winners from those presentations. In at least one recent edition a team finished first in total return while placing second overall on a Sharpe ratio of 1.49, which indicates that more than one ranking is computed and reported.

The organizer's email notes that the Vanguard representatives on the judging panel are partly there to identify strong students, and that past presenters have gone on to interview at Vanguard. Recent finalists were also invited to visit the New York Stock Exchange.

## 2.2 Team and registration

Team name: **WolfPack**. Registered with Prof. Bora Ozkan (Fox School of Business, Temple University).

Members: Aahan Jain, Dhrubojeet Haldar, Shubham Khinchi and Daksh Kumar.

Each member registers an individual StockTrak account **using their university email**. Registration with a personal address cannot be matched to the team and will be removed by the organizer.

## 2.3 Key dates

| Date | Event |
|---|---|
| 14 Sep 2026, 09:30 | Trading opens |
| 23 Sep 2026, 12:00 to 13:00 | Workshop 1 with Vanguard professionals |
| **3 Oct 2026** | **First trade due. Accounts below the minimum are removed.** |
| 12 Oct 2026, 12:00 to 13:00 | Workshop 2 |
| 6 Nov 2026, 16:00 | Trading closes |
| 13 Nov 2026, 12:00 to 15:00 | Final presentations |

The trading window is 53 calendar days, 40 trading days (no NYSE holidays fall in this window).

## 2.4 The disqualification risk

This is the single highest-severity item in the competition and it is entirely avoidable. Every member must place at least five trades, with the first trade placed by 3 October. Accounts that have not met the minimum are removed after the deadline. If one member is removed, the team competes with three accounts against fields of four. The organizer notes that teams lose position this way every year.

**Mitigation: every member builds a portfolio of six or more positions in a single session, well before 3 October.** Six positions is six trades, which clears the five-trade minimum immediately with one trade of margin for a rejected or mistaken order.

# 3. Competition rules

## 3.1 Organizer rules (from the registration email)

- Vanguard ETFs only
- Long positions only
- At least five trades per person, first trade by 3 October
- Cash no higher than 10 percent of the portfolio
- Teams of four
- Each member trades an individual $250,000 account; a full team competes with $1,000,000 across four accounts
- The team result comes from all four accounts together

## 3.2 StockTrak platform parameters (from the Rules page)

| Parameter | Value |
|---|---|
| Trading start | 09/14/2026 09:30 |
| Trading end | 11/06/2026 16:00 |
| Allowed security types | Equities |
| Allowed equity types | ETFs |
| Allowed exchanges | US |
| Initial cash | $250,000.00 |
| Weekly deposit | $0.00 |
| Total trades allowed | 10,000 |
| Day trading allowed | Yes |
| Margin trading allowed | No |
| Short selling allowed | No |
| **Interest earned on cash** | **0%** |
| Portfolio currency | USD |
| Fractional trading allowed | No |
| Commission | $10.00 per trade |
| Minimum buy price | $3.00 |
| Position limit (single position) | 25% |
| Position limit (single security) | 200% |

## 3.3 Where the platform and the organizer differ

Several rules exist only in the organizer's email and are **not enforced by the platform**:

- **Vanguard-only.** The platform allows any US-listed ETF. It will happily fill an order for SPY or QQQ. Compliance is manual and checked by the organizer. Do not mistype a ticker.
- **The 10 percent cash cap.** Not enforced by the platform. As of 16 September several competitor accounts are sitting at over 95 percent cash, which confirms the platform is not blocking it. Assume the organizer checks it, most plausibly from the 3 October deadline onward.
- **The five-trade minimum.** The platform allows 10,000 trades and does not enforce a floor.

Because these are manually checked, the safe posture is to be conservatively compliant rather than to test edges. Nothing in the analysis below depends on violating any of them.

## 3.4 Constraints this creates

Long only, no shorting, no margin, no leverage, at most 10 percent cash, 25 percent maximum in any single position, Vanguard products only. There is no gold ETF, no broad commodity ETF, no managed futures, no currency product and no inverse or volatility product in the Vanguard lineup.

The entire risk-management budget therefore consists of: duration, credit quality, geography, sector, and equity style. That is the full toolkit. Stating this constraint explicitly is worth doing in the final presentation, because it frames every portfolio decision that follows.

# 4. Scoring mechanics

## 4.1 The three ranking views

StockTrak computes and displays three separate rankings, selectable from a dropdown on the Rankings page:

1. **Overall Rankings**, sorted on percentage return
2. **Sharpe Ratio Rankings**
3. **Weekly Rankings**

There is also a **Team Rankings** view showing pooled team portfolio value alongside a Sharpe column and a return column. As of 16 September the team leaderboard is sorted on percentage return, with the leading team at 0.040 percent. Team sizes vary; at least one team is running five accounts ($1.25M) rather than four.

**Which view determines advancement to the November pitch has not been stated by the organizer.** This is the single most important open question. See Section 12.

## 4.2 The Sharpe ratio formula, as StockTrak computes it

From StockTrak's own documentation:

$$\text{Sharpe} = \frac{\bar{r}_{\text{daily}} - r_f}{\sigma(r_{\text{daily}})} \times \sqrt{252}$$

with the following specifics:

- Average **daily** portfolio return, **weekends excluded**
- The risk-free rate is the session's "interest earned on cash" setting
- Standard deviation of daily portfolio returns, weekends excluded
- Annualized on 252 trading days
- **Calculation begins 5 trading days after the account's first trade**

## 4.3 The critical consequence: the risk-free rate is zero

The session's "interest earned on cash" parameter is **0%**. StockTrak's documentation states the risk-free rate defaults to that parameter. Therefore:

$$\text{Sharpe} = \frac{\bar{r}_{\text{daily}}}{\sigma(r_{\text{daily}})} \times 15.87$$

The metric is simply mean daily return divided by daily volatility. There is no hurdle to clear. Any positive return at low volatility scores extremely well.

This inverts the normal intuition about a Sharpe-ranked contest. Under a real-world risk-free rate of roughly 3.6 percent, a Treasury bill fund has approximately zero excess return and therefore approximately zero Sharpe, making it worthless. With $r_f = 0$, a Treasury bill fund earning 3.64 percent at near-zero volatility has an extremely high Sharpe ratio. **The lowest-volatility assets become the highest-scoring assets.**

*Caveat: the "interest earned on cash" parameter is the simulator's cash-sweep setting. StockTrak's documentation says the Sharpe risk-free rate defaults to it, but the two are nominally separate parameters. This can be verified empirically once competitor accounts hold positions for a week or more, by pulling a competitor's holdings via the eye icon on the Team Rankings page, computing their return and realized volatility independently, and comparing against their displayed Sharpe.*

## 4.4 The warm-up window

The Sharpe calculation begins 5 trading days after the first trade. It is ambiguous whether those 5 days are excluded from the return series or whether the figure is merely not displayed until then.

**Working assumption: delayed, not excluded.** This is the conservative reading and it is the more natural interpretation of needing a minimum sample before a standard deviation is meaningful. It is also the reading that makes strategic sense: an exclusion window would hand every team a free option to observe the market for a week and then position, which the platform has no reason to offer.

Under this assumption the day on which the portfolio is built carries the full move from 100 percent cash to fully invested. That day's return enters the standard deviation and is unrepresentative of how the portfolio behaves once constructed. Two execution rules follow, in Section 10.

## 4.5 Team aggregation

The organizer states the team result comes from all four accounts together, and the Team Rankings page displays a pooled portfolio value with a single percentage return. With four accounts each starting at $250,000, summed dollar profit divided by $1M is algebraically identical to the average of the four account returns, so those two candidate schemes are the same thing.

The one scheme that genuinely differs is an average of four individually computed Sharpe ratios, which would differ from the Sharpe of the pooled return series because pooling captures cross-account diversification.

**Resolution: all four members hold identical weights.** Under identical accounts every aggregation scheme produces the same answer, which makes the team invariant to a rule we do not know. This supersedes any plan to split sleeves across members.

\newpage
# 5. Market conditions as of 16 September 2026

Observed from the Vanguard product list (prices as of 09/16/2026, returns as of 08/31/2026) and the StockTrak market ticker.

## 5.1 The yield curve is steeply positive

| Fund | SEC yield |
|---|---|
| VBIL (0-3 month T-bills) | 3.64% |
| VGUS (ultra-short Treasury) | 3.77% |
| VGSH (1-3 year Treasury) | 4.37% |
| VUSB (ultra-short bond, active) | 4.50% |
| BSV (short-term bond) | 4.57% |
| VGIT (intermediate Treasury) | 4.62% |
| VCSH (short-term corporate) | 4.99% |
| VSDB (short duration bond) | 4.98% |
| BIV (intermediate-term bond) | 5.12% |
| VCIT (intermediate corporate) | 5.62% |
| VCLT (long-term corporate) | 6.31% |
| VWOB (EM government) | 6.22% |
| VCHY (US high yield) | 7.25% |

The shape of this curve matters. The yield pickup from T-bills to short corporates is large relative to the additional duration taken. The pickup from short corporates to intermediate corporates is much smaller relative to the additional duration. **The efficient point on the credit curve appears to be the short end**, and past VCIT the incremental carry looks unlikely to pay for the incremental duration. Confirm this against measured volatilities once the covariance run is done; the claim is directional, not yet quantified.

## 5.2 Bonds are down across the entire curve year to date

| Fund | YTD |
|---|---|
| BSV | -0.12% |
| BND | -1.39% |
| VGIT | -2.10% |
| BIV | -2.36% |
| BLV | -3.55% |
| VGLT | -4.09% |
| EDV | -6.42% |

Rates have risen through 2026. The monotonic relationship between duration and year-to-date loss is a clean signature of a parallel upward shift. **Every carry position is therefore implicitly a bet that this stops.** A carry-heavy portfolio looks diversified across ten line items but carries essentially one risk factor.

Note the exception at the very short end: BSV is only -0.12 percent and VGSH, VCSH, VSDB, VUSB and VBIL are all positive year to date, because their carry outran their duration loss. This is the quantitative case for the short end over the intermediate.

## 5.3 Value is beating growth, decisively

| Fund | YTD | 1-year |
|---|---|---|
| VONV (Russell 1000 Value) | 20.78% | 29.67% |
| VFVA (US Value Factor) | 20.10% | 28.57% |
| VTV (Morningstar Value) | 16.74% | 25.29% |
| VOOV (S&P 500 Value) | 10.44% | 18.07% |
| VOOG (S&P 500 Growth) | 11.79% | 22.25% |
| VUG (Morningstar Growth) | 7.31% | 15.94% |
| VONG (Russell 1000 Growth) | 2.30% | 10.76% |

Note the 9.5 point year-to-date gap between VONG and VOOG, two large-cap growth funds. That is index construction, not a market signal, and it is a warning about treating same-style funds as interchangeable.

## 5.4 International is beating the US

| Fund | YTD | 1-year |
|---|---|---|
| VPL (Pacific) | 27.15% | 38.80% |
| VEXC (EM ex-China) | 20.85% | n/a |
| VYMI (Intl high dividend) | 17.96% | 30.06% |
| VEA (developed markets) | 14.87% | 27.79% |
| VEU (all-world ex-US) | 14.22% | 26.43% |
| VXUS (total international) | 13.84% | 25.89% |
| VWO (emerging markets) | 10.21% | 20.49% |
| VGK (Europe) | 7.96% | 20.36% |
| **VTI (US total market)** | **11.41%** | **20.23%** |

This is directly relevant to the November pitch, which must be an **international** ETF concept. The regions currently working are Pacific and emerging markets ex-China.

## 5.5 Sector dispersion

| Fund | Sector | YTD | 1-year |
|---|---|---|---|
| VDE | Energy | 44.86% | 46.09% |
| VGT | Information Technology | 26.50% | 38.91% |
| VHT | Health Care | 10.09% | 27.61% |
| VIS | Industrials | 9.04% | 16.40% |
| VAW | Materials | 9.04% | 15.14% |
| VDC | Consumer Staples | 7.72% | 7.08% |
| VNQ | Real Estate | 7.72% | 8.61% |
| VFH | Financials | 3.20% | 8.74% |
| VOX | Communication Services | -0.10% | 4.61% |
| **VPU** | **Utilities** | **-2.01%** | **2.83%** |
| VCR | Consumer Discretionary | -5.65% | 2.19% |

Two observations. Energy is the standout but it is also the highest-volatility sector on the board and it fell 2.96 percent on 16 September alone. Chasing a sector up 45 percent into a 40-day window is the highest-variance decision available.

More importantly, **utilities have not worked as a defensive sleeve in this regime**. VPU is negative year to date. The usual low-beta equity hedge is not functioning, likely because utilities are rate-sensitive and rates have risen. Consumer staples (VDC) have held up better and are the more reliable defensive equity position here.

# 6. Strategic analysis

## 6.1 The two regimes are nearly disjoint

With $r_f = 0$, the Sharpe ranking and the return ranking want opposite portfolios. Approximate figures over the remaining window:

The ordering is unambiguous even without measured figures. An ultra-short bond book has a small positive expected return at very low volatility, so it scores high on Sharpe and finishes near the bottom on return. An equity portfolio has a larger expected return at roughly fifteen to twenty times the volatility, so it competes on return and scores poorly on Sharpe. There is no portfolio that wins both, and a 50/50 compromise places mid-pack on each, which loses to whichever team guessed correctly.

The magnitudes require the covariance run. The direction does not.

## 6.2 The asymmetry in winnability

These two leaderboards are not equally winnable.

**The Sharpe leaderboard is close to deterministic.** Carry is known in advance from published SEC yields. The volatility of ultra-short instruments is stable and low. A portfolio built from the short end of the curve will produce a high Sharpe with high probability, because there is very little that can go wrong over 40 days in instruments with under one year of duration.

**The return leaderboard is a lottery.** Over 40 trading days, the dispersion of outcomes across sensible equity portfolios is dominated by noise. Whoever wins it will be a team that concentrated in one sector and was lucky. That is not a plan, and it is not reproducible.

## 6.3 Why concentration does not help under a Sharpe metric

The standard error of an estimated Sharpe ratio is approximately

$$SE(\hat{S}) \approx \sqrt{\frac{1 + \hat{S}^2/2}{n}}$$

Over 40 daily observations, annualized, the standard error on the reported figure is roughly 2.6 Sharpe points.

The important property is that **Sharpe is scale-invariant**. Multiplying every position by a constant leaves the ratio unchanged. So unlike a total-return contest, you cannot buy a fatter right tail by levering up. The usual tournament logic of "take a wild swing because only the top matters" does not apply cleanly.

*Qualification: this argument is exactly right about leverage and only partly right about concentration. A concentrated portfolio still has a wider distribution of realized Sharpe outcomes than a diversified one with the same ex-ante Sharpe, because idiosyncratic risk inflates the variance of the estimate. If only a small number of teams advance from a large field, some concentration is rationally correct. The effect is real but much weaker than in a return-ranked contest.*

## 6.4 Achievable Sharpe, calibrated against history

A recent finalist team posted a 1.49 Sharpe on a 2.58 percent eight-week return, which back-solves to roughly 9 to 11 percent portfolio volatility. If Sharpe were annualized from daily data with a 2.6 standard error, the top of a 100-team field would print 3 or higher. It printed 1.49.

That suggests that edition either did not annualize or computed on weekly data. Under the current documented formula (daily, $\sqrt{252}$) the printed numbers will be larger. **Treat 1.5 to 2.0 as the historical winning band and adjust upward for the annualization.**

## 6.5 The T-bill question is a strategic choice, not a technical one

Under a Sharpe ranking with $r_f = 0$, the highest-scoring compliant portfolio is roughly:

| Ticker | Weight | SEC yield |
|---|---|---|
| VBIL | 25% | 3.64% |
| VGUS | 25% | 3.77% |
| VUSB | 22% | 4.50% |
| VGSH | 18% | 4.37% |
| VSDB | 10% | 4.98% |

Blended yield approximately 4.1 percent, window return approximately 0.59 percent, at very low volatility. The 25 percent position limit is the only thing preventing a single-fund portfolio, and it barely binds.

This is legal under every stated rule. It is also scoring-artifact harvesting rather than portfolio management, and it produces nothing to present in November. **The team should decide this deliberately rather than drift into it.** See Section 11.

\newpage

# 7. The Vanguard ETF universe

## 7.1 Where the data comes from

**No expense ratios, SEC yields, returns, volatilities or prices are reproduced in this document.** Those figures go stale, and several of the volatility estimates used during earlier analysis were analyst priors rather than measurements. Reproducing them here would make guesses look like data.

The authoritative source for the full lineup, including expense ratios, SEC yields, YTD and trailing returns, inception dates and current prices, is Vanguard's own product list:

> **https://investor.vanguard.com/investment-products/list/etfs?filters=open**

The page is JavaScript-rendered, so a plain HTTP fetch returns an empty shell. It has an *Export to Excel* control, and a scraper against the underlying data endpoint is the intended path for keeping this current.

SEC yield in particular is a fund-level disclosure, not a market price, and is not available from any price API. It has to come from this page.

Companion module: `vgdata.py` handles price and dividend history, source cross-checking and StockTrak export parsing. See Section 11.

## 7.2 The investable roster

What follows is the ticker list only, grouped by the role each fund plays in the portfolio. Tickers, names and asset-class assignments are stable; everything numeric belongs in the scraper output.

**Ultra-short duration**

VBIL (0-3 Month Treasury Bill), VGUS (Ultra-Short Treasury), VUSB (Ultra-Short Bond, active), VSDB (Short Duration Bond)

**Short duration**

VGSH (Short-Term Treasury), VCSH (Short-Term Corporate), BSV (Short-Term Bond), VTIP (Short-Term TIPS)

**Intermediate and core fixed income**

BND (Total Bond Market), BIV (Intermediate-Term Bond), VGIT (Intermediate Treasury), VCIT (Intermediate Corporate), VMBS (Mortgage-Backed), VTC (Total Corporate), VTG (Total Treasury), VCRB (Core Bond, active), VPLS (Core-Plus Bond, active), BNDP (Core-Plus Bond Index), VGVT (Government Securities, active), VTP (Total TIPS), BNDX (Total International Bond, hedged), BNDW (Total World Bond)

**Long duration**

BLV (Long-Term Bond), VCLT (Long-Term Corporate), VGLT (Long-Term Treasury), EDV (Extended Duration Treasury)

**Credit and high yield**

VCHY (US High-Yield Corporate Index), VGHY (High-Yield, active), VWOB (EM Government Bond), VGMS (Multi-Sector Income), VCEB (ESG US Corporate Bond)

**US broad equity**

VTI (Total Stock Market), VOO (S&P 500), VV (Large-Cap), MGC (Mega Cap), VONE (Russell 1000), VTHR (Russell 3000), VO (Mid-Cap), IVOO (S&P Mid-Cap 400), VXF (Extended Market), VB (Small-Cap), VTWO (Russell 2000), VIOO (S&P Small-Cap 600)

**Style**

VTV (Value), VUG (Growth), MGV (Mega Cap Value), MGK (Mega Cap Growth), VONV (Russell 1000 Value), VONG (Russell 1000 Growth), VOOV (S&P 500 Value), VOOG (S&P 500 Growth), VOE (Mid-Cap Value), VOT (Mid-Cap Growth), VBR (Small-Cap Value), VBK (Small-Cap Growth)

**Factor**

VFMV (Minimum Volatility), VFMO (Momentum), VFMF (Multifactor), VFQY (Quality), VFVA (Value Factor)

**Dividend**

VIG (Dividend Appreciation), VYM (High Dividend Yield), VIGI (Intl Dividend Appreciation), VYMI (Intl High Dividend Yield)

**Sector**

VDC (Consumer Staples), VPU (Utilities), VHT (Health Care), VIS (Industrials), VAW (Materials), VFH (Financials), VOX (Communication Services), VCR (Consumer Discretionary), VGT (Information Technology), VDE (Energy), VNQ (Real Estate), VNQI (Global ex-US Real Estate)

**International equity**

VXUS (Total International), VEU (All-World ex-US), VEA (FTSE Developed Markets), VWO (FTSE Emerging Markets), VEXC (EM ex-China), VGK (FTSE Europe), VPL (FTSE Pacific), VSS (All-World ex-US Small-Cap), VT (Total World), VDG (Developed ex-US Growth), VDV (Developed ex-US Value)

**ESG**

ESGV (ESG US Stock), VSGX (ESG International Stock)

**Active equity (Wellington)**

VDIG (Dividend Growth), VUSG (US Growth), VUSV (US Value)

## 7.3 Municipal bonds are excluded

Vanguard's municipal lineup (VTEB, VCRM, VTEI, VTEL, VTES, VSDM, VTEC, MUNY) is deliberately excluded from the investable universe.

Municipal yields are lower than comparable taxable yields precisely because the income is exempt from federal tax. **There are no taxes in a simulation.** The entire benefit is unavailable while the yield giveaway is paid in full. Every municipal fund is therefore strictly dominated by a taxable fund of similar duration. This reasoning is structural and does not depend on any particular yield figure.

## 7.4 Target-maturity funds

Vanguard's target maturity corporate bond series (VBCA through VBCJ, maturities 2027 through 2036) all launched 24 March 2026. They have insufficient history for covariance estimation and are excluded from the optimizer. They remain available as discretionary overlays if a specific duration point is wanted.

## 7.5 What the scraper should capture

For each fund: ticker, name, asset class, risk level, expense ratio, SEC yield (flagging real versus nominal for TIPS funds), YTD, 1-year, 5-year, 10-year and since-inception returns, inception date, and current price.

Two fields need explicit handling:

- **TIPS funds (VTIP, VTP)** publish a *real* SEC yield. It is not comparable to the nominal yields on every other bond fund, and it must not be dropped into an expected-return vector without adding expected inflation.
- **Inception date** determines whether a fund can enter a covariance estimate at all. See Section 11.1.


\newpage

# 8. Structural gaps in the lineup

Worth stating explicitly because it constrains every portfolio decision and is a good framing point for the November presentation.

Vanguard's US-listed lineup contains **no gold ETF, no broad commodity ETF, no managed futures product, no currency product, and no inverse or volatility product**. Combined with long-only, no margin and a 10 percent cash cap, the available diversification axes reduce to five:

1. Duration (VBIL through EDV)
2. Credit quality (Treasury through VCHY)
3. Geography (US, developed ex-US, emerging, Pacific, Europe)
4. Sector (eleven GICS sectors)
5. Equity style and factor (value, growth, size, quality, momentum, minimum volatility)

There is no way to construct a genuinely uncorrelated return stream. In a stress event, every equity sleeve moves together and, given 2026's positive stock-bond correlation, the bond sleeve may move with them.

# 9. Candidate portfolios

**All three depend on the answer to the ranking question in Section 12.1, which is still open. These are sketches to react to, not recommendations. Nothing here should be executed before we know which leaderboard we are on.**

Expected returns are priors. Volatility and correlation figures require the covariance computation in Section 11 before weights should be treated as final.

## 9.1 If the ranking is Sharpe

| Ticker | Weight | SEC yield |
|---|---|---|
| VBIL | 25% | 3.64% |
| VGUS | 25% | 3.77% |
| VUSB | 22% | 4.50% |
| VGSH | 18% | 4.37% |
| VSDB | 10% | 4.98% |

Five positions, $50 in commissions. Blended yield and window return follow directly from the published SEC yields; compute them from current scraper output rather than from any figure written here.

**Important correction on the volatility of this portfolio.** A naive reading gives near-zero volatility and an absurd Sharpe. That is wrong. StockTrak measures the volatility of *portfolio value*, and for a Treasury bill fund essentially all return arrives as a monthly distribution rather than as price drift. The daily series looks like: flat, flat, flat, price drops roughly 0.3 percent on the ex-date, cash credited on the pay date, flat, flat.

Over 40 trading days with two distribution cycles, if ex-date and pay-date are separated, the distribution days dominate the volatility estimate and the resulting Sharpe is far lower than a naive calculation suggests, though still well above any equity portfolio. **The magnitude cannot be stated until V1 is resolved and the covariance run is done.** Do not size this portfolio off an assumed volatility.

**This must be tested empirically.** Hold a position through the early-October ex-date and observe whether StockTrak credits the distribution on the same day the price drops. If same-day, the sawtooth cancels and volatility stays near zero. If lagged, the whipsaw enters the volatility estimate. This single observation is worth more than any modeling.

## 9.2 If the ranking is total return

No defensible systematic portfolio wins a 40-day return contest. The honest position is that this leaderboard is won by concentration plus luck. If the team chooses to compete on it, the regime-consistent tilts are value over growth, international over US, and the sectors currently working. The highest-momentum exposures available are VDE, VFMF, VFMO, VPL and VONV. This is a gamble, and it should be labeled as one.

## 9.3 A blended portfolio, if we want to hedge the uncertainty

| Ticker | Weight | Rationale |
|---|---|---|
| VCSH | 20% | 4.99% carry at ~2% vol, best return-per-unit-risk on the board |
| VYMI | 15% | International high dividend, +30% 1-year |
| VTV | 15% | Value, +25% 1-year, the regime that is working |
| VEA | 12% | Developed international, +27.8% 1-year |
| VHT | 10% | Health care, +27.6% 1-year at roughly 0.7 beta |
| VUSB | 10% | 4.50% carry at ~0.7% vol, volatility ballast |
| VDC | 8% | Staples, the defensive sleeve that is actually working |
| VDE | 5% | Energy, low correlation diversifier, deliberately small |
| VFMV | 5% | Minimum volatility, the only explicit low-vol equity tool |

Approximately 30 percent fixed income and 70 percent equity, tilted to value and international. **Portfolio volatility, expected return and Sharpe are not stated here because they have not been measured.** Run Section 11.2 against live data before treating these weights as final; they are a starting structure, not an optimizer output.

This does not win either leaderboard outright. It beats a plain VOO portfolio on both metrics, which is the most a dual-mandate portfolio can deliver. Nine positions clears the trade minimum with margin and costs $90 in commissions, roughly 0.036 percent.

Note that VPU is deliberately excluded despite being the conventional low-beta choice, because it is negative year to date (Section 5.5). VDC replaces it.

# 10. Execution rules

These follow from the scoring mechanics and hold regardless of which ranking is used.

**Build the entire portfolio in a single session.** Under the working assumption that the 5-day warm-up delays display rather than excluding data, the day of construction carries the full transition from cash to invested and enters the volatility estimate. One anomalous day is better than five. Staging entry across a week creates five days of shifting exposure, none of which reflects the steady-state portfolio.

**Trade as early as possible.** The measurement window runs from first trade to 6 November. Trading now gives roughly 35 scored days; waiting until 3 October gives roughly 18. Since the standard error on a Sharpe estimate scales with $1/\sqrt{n}$, a longer window means the ranking reflects true portfolio quality rather than noise. If the team holds the best ex-ante portfolio, noise can only pull it back toward the field. Trading early is correct under either reading of the warm-up rule, so it does not depend on resolving that question.

**Do not rebalance.** Each rebalance adds a transition day to the return series and costs $10 per trade. At $250,000 with an expected mean daily return around 0.0158 percent under a carry-heavy book, a single $10 trade is 0.004 percent, roughly a quarter of a day's return. Ten trades erases roughly two and a half days. A rebalance must earn back both costs, and over 40 days it almost never does.

**Six positions minimum.** Five clears the rule with zero margin. A rejected order, a fat-fingered ticker or a minimum-price rejection leaves no room. Six costs $10 more.

**All four accounts hold identical weights.** This makes the team score invariant to the unknown aggregation rule (Section 4.5).

**No fractional shares.** Weights will be approximate. VOO trades near $693 and VTI near $371, so round lots leave residual cash. Budget 1 to 2 percent residual, which is comfortably inside the 10 percent cap.

**Distributions arrive as cash and are not automatically reinvested.** They will accumulate against the cash cap and cost $10 each to reinvest. With a 30 percent bond sleeve yielding roughly 5 percent, monthly distributions are roughly 0.12 percent of the account, so this is not material over two cycles. Do not reinvest.

**Verify tickers before submitting.** The platform allows any US-listed ETF. The Vanguard-only rule is enforced manually by the organizer.

# 11. Analysis and modeling notes

## 11.1 Data hygiene

**Insufficient history for covariance estimation.** Several funds launched too recently to support a reliable covariance estimate and should either be proxied by their underlying index or dropped from the optimization and added back as discretionary overlays. The current list, with inception dates, is maintained in `vgdata.YOUNG`, and `vgdata.build()` reports any ticker with under 500 observations at fetch time rather than relying on a hardcoded list that will drift.

As a rule of thumb: anything launched in 2025 or 2026 needs proxying. VBIL and VGUS proxy cleanly with 1-month and 3-month Treasury bill yields from FRED (`vgdata.fetch_tbill`, `vgdata.bill_total_return`). VSDB proxies reasonably with a blend of VCSH and VGSH.

**Index methodology break.** VTI, VV, VO, VB, VTV, VUG, MGC, MGK and MGV have moved from CRSP to Morningstar indices. Any spliced long history contains a methodology discontinuity at the transition date. Returns before and after are not strictly comparable.

**Regime contamination.** A 2021 to 2026 estimation window covers a rate-hiking cycle throughout which stock-bond correlation was positive. That is not the long-run relationship, and a covariance matrix estimated on that window will encode it. This is arguably the correct prior for the next 38 days, but it should be a conscious choice rather than an accident.

**SEC yield is not expected return.** For anything with duration, realized return is carry plus price change. Over a 40-day window, a modest parallel rate move is worth several times the carry earned on an intermediate bond fund, so duration risk swamps yield differences. The carry ranking in Section 5.1 is therefore only trustworthy at the short end, where duration is small enough that carry dominates. Quantify this with the rate-shock scenario in Section 11.3 before relying on any intermediate or long position.

**The equity risk premium is an assumption, not data.** Any expected-return figure for an equity sleeve rests on a forward ERP that nobody can observe. The optimizer output is highly sensitive to it. Run the sensitivity in Section 11.3 across a 3 to 6 percent range and report the weights as a range rather than a point.

## 11.2 Optimization script

Depends on `vgdata.py` for price history, dividend history, source cross-checking and SEC yields. Run `vgdata.build()` first and resolve every data-quality flag it reports before trusting any output below.

```python
import numpy as np, pandas as pd, yfinance as yf
from sklearn.covariance import LedoitWolf
from scipy.optimize import minimize

TIX = ["VUSB","VCSH","VGSH","BSV","VCIT","VWOB","BND",
       "VFMV","VTV","VDC","VYMI","VDE","VTI","VXUS","VPL",
       "VFMF","VPU","VHT","VEA","VONV","VIG","VYM"]
# VTIP deliberately omitted: real yield, not comparable. Add it back
# only with an explicit inflation adjustment.

# SEC yields: load from the scraper, do not hardcode. See vgdata.SEC_YIELD.
# TIPS funds (VTIP, VTP) publish a REAL yield and must not be mixed into
# a nominal expected-return vector without adding expected inflation.
from vgdata import SEC_YIELD as SEC          # nominal only

RF   = 0.0      # StockTrak session: interest earned on cash = 0%
ERP  = 4.5      # assumption, see 11.1
CAP  = 0.25     # StockTrak single-position limit
H    = 53/365   # 14 Sep to 6 Nov

px = yf.download(TIX, start="2021-01-01", auto_adjust=True)["Close"].dropna()
r  = np.log(px).diff().dropna()

S  = LedoitWolf().fit(r.values).covariance_ * 252
mu = np.array([SEC.get(t, ERP)/100 for t in px.columns])   # rf = 0

neg = lambda w: -(w @ mu) / np.sqrt(w @ S @ w)
res = minimize(neg, np.ones(len(mu))/len(mu),
               bounds=[(0, CAP)]*len(mu),
               constraints={"type":"eq","fun": lambda w: w.sum()-1})
w   = res.x
vol = np.sqrt(w @ S @ w)

print(pd.Series(w, index=px.columns).round(4).sort_values(ascending=False))
print(f"ex-ante Sharpe {(w@mu)/vol:.2f} | ann vol {vol:.2%} | "
      f"window return {(w@mu)*H:.2%}")

# Block bootstrap of realized 40-day Sharpe.
# NOTE: overlapping draws understate true dispersion. Treat the
# tails as optimistic. A stationary bootstrap is the better estimator.
pr = r.values @ w
idx = np.random.randint(0, len(pr)-40, 5000)
sh  = np.array([( (d:=pr[i:i+40]).mean() - RF/252 ) / d.std() * np.sqrt(252)
                for i in idx])
print(f"realized Sharpe: median {np.median(sh):.2f}, "
      f"10th {np.percentile(sh,10):.2f}, 90th {np.percentile(sh,90):.2f}")
```

## 11.3 What to compute next

1. Replace every asterisked volatility figure in Section 7 with a measured value.
2. Ledoit-Wolf shrunk covariance across the cleaned universe.
3. Constrained maximum-Sharpe weights at the 25 percent cap, for $r_f = 0$.
4. Block bootstrap of realized 40-day Sharpe to get a distribution rather than a point estimate.
5. Sensitivity of the recommended weights to the ERP assumption across 3 to 6 percent.
6. A rate-shock scenario: reprice the bond sleeve under parallel shifts of plus or minus 25, 50 and 100 basis points.

# 12. What is still open

## 12.1 The one real unknown

**Which ranking are we scored on: Overall (percentage return), Sharpe Ratio, or Weekly?**

StockTrak computes all three and the organizer picks. He has not said which. This is the only question that changes what we build, because a return ranking and a Sharpe ranking want close to opposite portfolios (Section 6.1). Everything in Section 9 is conditional on the answer.

Status: asked. Expected at the 23 September workshop or by email before it. **This section gets updated the moment we know.**

Nothing else is blocking. The rules, the platform settings, the scoring formula and the risk-free rate are all settled and documented above.

## 12.2 Quick checks to run on the platform

None of these block anything. They sharpen the analysis and each takes a few minutes.

**Are the newer funds tradable?** VBIL, VGUS, VSDB, VCHY, VTG and VGMS all launched in 2025 or 2026 and simulator universes often lag new listings. Type the tickers into the trade screen and see. Matters only if the answer to 12.1 is Sharpe.

**How are distributions timed?** Bond ETFs pay monthly. Hold one through the early-October ex-date and watch whether StockTrak credits the cash on the same day the price drops or with a lag. Same-day means a bond-heavy portfolio shows very low measured volatility; a lag means the whipsaw enters the volatility estimate. Affects how attractive Section 9.1 actually is.

**Does the displayed Sharpe match the documented formula?** Once teams have held positions for a week, pull a competitor's holdings from the Team Rankings page (the eye icon), compute their return and volatility independently, and compare to their displayed Sharpe. Confirms the risk-free rate is genuinely zero rather than assumed to be.

## 12.3 Assumptions written down

| Assumption | Basis | If wrong |
|---|---|---|
| Risk-free rate is 0% for scoring | StockTrak docs, session cash interest set to 0% | Section 9.1 collapses |
| Sharpe warm-up delays display rather than excluding data | Conservative reading | Nothing, execution is the same either way |
| Cash cap enforced from 3 October | Inference, not the organizer's words | Nothing, cash pays 0% so full investment is right regardless |
| Team score is pooled across the four accounts | Organizer's email and the Team Rankings display | Neutralized by all four holding identical weights |
| Forward equity risk premium | Assumption, unobservable | Large effect on any equity sizing |

## 12.4 Known limits of the analysis

- No volatility or correlation figure in this document is measured. Nothing is real until Section 11.2 runs against live data.
- The estimation window covers a rate-hiking cycle with positive stock-bond correlation, which is not the long-run relationship (Section 11.1).
- The block bootstrap uses overlapping draws and will understate true dispersion.
- The carry argument in Section 5.1 holds only at the short end, because duration risk dominates yield differences over 40 days.
- Transaction costs are modeled as flat commission only. Bid-ask spread on the thinner new listings is not modeled.

# 13. The November pitch

The finalist deliverable is specifically an **international** ETF concept, presented to a panel of Vanguard and Fox judges. Three points worth recording now.

**Start in October, not November.** The concept benefits from being grounded in positioning actually held during the trading phase rather than assembled the week before. If the portfolio carries meaningful international exposure, the pitch can be built on a real view developed over eight weeks.

**The regions currently working are Pacific and emerging markets ex-China.** VPL is up 27.15 percent year to date and 38.80 percent over one year. VEXC is up 20.85 percent since its September 2025 inception. Whatever concept the team develops, these are the live stories in the data.

**The structural gaps in Section 8 are pitch material.** A concept that fills a genuine hole in Vanguard's international lineup is a stronger proposal than a repackaging of existing exposure. The absence of any commodity, currency or alternatives product, and the relatively thin coverage of emerging market sub-regions, are the obvious gaps to examine.

One strategic note for the team. If the trading phase functions primarily as a filter, then effort spent marginally improving the portfolio past the point of reliably clearing the cut has lower expected value than effort spent on the pitch. That trade-off should be made deliberately.

\newpage

# Appendix A: Change log of corrections

Recorded so that future analysis does not re-derive errors already found.

1. **Risk-free rate.** Early analysis treated VBIL's 3.64 percent SEC yield as the risk-free hurdle, which made Treasury bill funds worthless (zero excess return). The StockTrak session sets cash interest to 0 percent, so the hurdle is zero and the conclusion inverts entirely: ultra-short instruments become the highest-Sharpe assets available.

2. **VBIL volatility.** An initial estimate of near-zero volatility ignored the distribution sawtooth in fund NAV. Corrected in Section 9.1, pending empirical verification (V1).

3. **Sleeve splitting across accounts.** An earlier plan split different sleeves across the four accounts. This was wrong. Identical accounts make the team score invariant to the unknown aggregation rule.

4. **Factor ETF availability.** VFMV, VFMO, VFMF, VFQY and VFVA were incorrectly flagged as possibly delisted. All five are live and VFMV is strategically important.

5. **Expense ratios.** Several were stale. Current: VIG 0.04%, VUG/VV/VTI/VOO/VO/VB/VTV 0.03%, VYM 0.04%, VEA 0.03%, VBIL 0.06%, VWOB 0.15%, VNQ 0.13%.

6. **Concentration under Sharpe.** An earlier claim that scale-invariance eliminates the value of concentration was too strong. It eliminates the value of *leverage*. Concentration still widens the distribution of the realized estimate. Qualified in Section 6.3.

7. **Team aggregation schemes.** Summed dollar profit and average account return were initially presented as distinct options. With equal starting capital they are algebraically identical.

8. **Municipal bonds.** Initially included in the universe. They are strictly dominated in a tax-free simulation and have been removed.

9. **Trading-day count.** Earlier drafts used 38 trading days for the 14 September to 6 November window. The correct figure is 40; no NYSE holiday falls in that span (Columbus Day is not an equity market holiday). This propagated into the standard-error arithmetic without changing any conclusion.

10. **TIPS yields.** VTIP and VTP publish *real* SEC yields, not nominal. An earlier version of the optimization script placed VTIP's real yield into a nominal expected-return vector, which systematically understated it and would have caused the optimizer to under-weight it. Fixed in Section 11.2.

11. **Reproduced market data removed.** Earlier versions of this document contained full per-fund tables of expense ratios, SEC yields, returns and volatility estimates. The volatility and beta figures were analyst priors presented alongside sourced data, which made estimates look like measurements. All such tables have been removed in favour of a pointer to the Vanguard product list and the scraper. Section 7.
