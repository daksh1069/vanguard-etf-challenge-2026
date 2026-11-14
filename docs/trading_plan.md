# Plan of action — WolfPack / Vanguard ETF Challenge

> **Historical document (16 Sep 2026), kept as the build log.** Open item 1 below was later reversed: the organizer
> confirmed on 17 Sep that teams are scored on **Sharpe ratio**, not total return. The final strategy is in
> `reports/WOLFPACK_STRATEGY.md`.

Written 16 Sep 2026. Phases are gated: **no phase starts until the previous
phase's gate passes.** Every number in the brief is treated as stale and
re-derived from a dated, sourced pull.

Deadline pressure: first trade due **3 Oct**, trading closes **6 Nov**. Every
day of delay costs a scored observation (brief §10).

---

## Phase 0 — Environment *(DONE)*

- `.venv` on Python 3.11.0, deps in `requirements.txt`, Chromium for Playwright.
- `config.yaml` holds every constant. Nothing numeric is hardcoded in scripts.
- Data sources probed and resolved (below).

### Source resolution — what actually works

| Source | Status | Role |
|---|---|---|
| `investor.vanguard.com/.../list/funddetail/all` | **Works, plain HTTP, no auth** | SEC yield, expense ratio, inception, asset class, risk, NAV/market price, YTD, trailing returns. 383 entities → **116 ETFs**. |
| `investor.vanguard.com/vmf/api/{TICKER}/delayedPrice` | **Works, plain HTTP** | **bid/ask** + **ex-dividend and pay dates**. |
| yfinance | Works | OHLCV + dividend history. Primary price source. |
| FRED (`DTB4WK`, `DTB3`) | Works | Bill-yield proxies for VBIL/VGUS pre-inception. |
| Stooq | **Dead** — JS bot challenge | Dropped as cross-check. |
| Playwright | Installed | Only needed to *re-discover* endpoints if they move. Not in the hot path. |

The brief (§7.1) assumed the Vanguard list needed a rendered scrape. It does
not — the JSON is public. Playwright was used once to find the endpoint and is
no longer required for routine pulls.

Because Stooq is gone, price integrity is validated **internally** instead of
against a second vendor — see Gate 2. That is the stronger test anyway: it
catches yfinance's actual failure mode (bad dividend adjustment), which a
second close-price vendor would not.

---

## Phase 1 — Data acquisition → `src/vgdata/` *(DONE — Gate 1 PASS)*

Build the module the brief refers to as `vgdata.py` but which does not exist yet.

1. `fetch_funddetail()` — pull + cache the Vanguard JSON to
   `data/raw/vanguard_funddetail_{date}.json`. Never overwrite; every pull is dated.
2. `fund_master()` — flatten to one row per ETF: ticker, name, expense ratio,
   SEC yield, **`yield_is_real`** (detected from the `yieldNote` footnote text
   `"DOES NOT INCLUDE ANY INCOME ADJUSTMENT..."`, *not* a hardcoded TIPS list),
   inception date, asset class, duration bucket, index-vs-active, NAV, market price.
3. `fetch_quotes()` — bid/ask and ex-div/pay dates per ticker.
4. `fetch_prices()` — yfinance OHLCV + dividends, both `auto_adjust=True` and
   `False`, cached to parquet.
5. `fetch_tbill()` / `bill_total_return()` — FRED bill series → synthetic total
   return, to proxy VBIL and VGUS before their Feb-2025 inception.
6. `build()` — runs all of the above and emits a **data-quality report**.

Universe filter: 116 ETFs → drop municipals (8) and target-maturity VBCA–VBCJ
(10, all inception 2026-03-24) → ~98 investable. Exclusions are structural
(brief §7.3/§7.4), not judgment calls.

**Gate 1 — no modelling until all of these pass:**
- every brief-roster ticker resolves (already verified: 92/92, zero missing);
- SEC yield present and real-vs-nominal flagged for all bond funds;
- prices non-empty, monotone index, no zero/negative closes;
- each ticker's observation count and inception date reported.

---

## Phase 2 — EDA and cleaning *(DONE — Gate 2 PASS)*

1. **History audit.** Observations per ticker vs the 500-obs threshold. Already
   known to fail: VCHY (inception 2026-06-02, ~70 obs), VDG/VDV (2026-04-14),
   BNDP (2025-12-02), VUSG/VUSV (2025-11-14), VBIL/VGUS (2025-02-07), VSDB
   (2025-04-01). Each gets proxied or dropped — **decided and documented per
   ticker**, not silently.
2. **Dividend-adjustment reconciliation.** Verify `adj_close` reconstructs from
   `close` + dividends for every ticker. This is the yfinance failure mode that
   would silently corrupt every downstream return.
3. **Cross-check today's NAV/market price** from the Vanguard feed against
   yfinance's last close, all ~98 tickers at once. Flag anything off by >20bp.
4. **Index methodology break** (brief §11.1): flag the CRSP→Morningstar
   transition date for VTI, VV, VO, VB, VTV, VUG, MGC, MGK, MGV. Test whether
   pre/post volatility differs materially; if it does, truncate rather than splice.
5. **Return-distribution EDA.** Per-ticker annualised vol, skew, kurtosis, max
   drawdown, and a correlation heatmap. **Replaces every asterisked volatility
   guess in the brief with a measurement** (brief §11.3 item 1).
6. **Regime check.** Rolling 60-day stock-bond correlation. Confirm or refute
   the brief's claim that it is currently positive, and decide the estimation
   window deliberately (brief §11.1).

**Gate 2:** a written data-quality report with every flag either resolved or
explicitly accepted. Nothing proceeds on an unexplained anomaly.

---

## Phase 3 — The distribution sawtooth *(DONE — both branches sized)*

This is the single highest-leverage piece of analysis and the brief leaves it
open (§9.1, §12.2). It decides whether the T-bill book's Sharpe is ~15 or ~3.

Already established from the quote feed: for every bond ETF checked, **ex-date
2026-09-01, pay date 2026-09-03 — a 2-day lag.** The drop and the credit are
*not* same-day.

1. Measure the actual ex-date price drop from history (VBIL ≈ 0.22 on 75.60 ≈ 29bp).
2. Simulate the 40-day portfolio-value series under both readings:
   - **(a) same-day** — NAV drop offset by cash credit, sawtooth cancels, σ ≈ 0;
   - **(b) 2-day lag** — value dips then recovers, two whipsaws enter σ.
3. Report the Sharpe for the §9.1 portfolio under each. The gap between (a) and
   (b) *is* the value of the October empirical test.
4. If (b) craters the Sharpe, test whether staggering across funds with
   different ex-dates diversifies the sawtooth away.

This converts the brief's "cannot be stated until V1 is resolved" into a
two-branch answer available **now**, with the October observation demoted to a
confirmation rather than a blocker.

---

## Phase 4 — Covariance and optimisation

1. Ledoit-Wolf shrunk covariance on the cleaned panel, window chosen in Phase 2.6.
2. Expected returns: SEC yield for bonds (nominal only — TIPS need an inflation
   add-on), ERP assumption for equities, carried as a **range, not a point**.
3. Constrained max-Sharpe at the 25% cap, rf = 0, long-only, fully invested.
   Solved with **cvxpy via the Schaible transform** — an exact convex solve,
   not `scipy.minimize` from a single start (the brief's script can land on a
   local optimum and gives no certificate).
4. Duration-aware expected returns for anything past the short end: carry alone
   is not expected return (brief §11.1).
5. Produce three portfolios: max-Sharpe, max-return, and a blend — so the
   decision is ready the moment the §12.1 ranking question is answered.

## Phase 5 — Validation

1. **Stationary bootstrap** (`arch`) of realised 40-day Sharpe — fixes the
   overlapping-draw bias the brief admits to (§12.4).
2. ERP sensitivity across 3–6%; report weights as a range.
3. Rate shocks: ±25/50/100bp parallel, repricing the bond sleeve by duration.
4. **Transaction costs modelled properly:** $10 commission **plus measured
   half-spread** from the quote feed. Already measured: VBIL 1.3bp, VGSH 1.7bp,
   VCSH 2.6bp, VUSB 4.0bp, VCHY 4.1bp, **VSDB 10.7bp**. The brief lists spread
   as an unmodelled gap (§12.4); it no longer is.
5. Round-lot integerisation under the no-fractional-shares rule, with residual
   cash checked against the 10% cap.

## Phase 6 — Execution package

Per-account order tickets: ticker, share count, limit price, expected residual
cash. Identical across all four accounts (brief §4.5). ≥6 positions. A
pre-submit checklist that verifies every ticker is Vanguard and every symbol
is spelled correctly.

## Phase 7 — November pitch *(start October, run parallel)*

International ETF concept. Grounded in Phase 2's measured correlations and the
structural gaps in brief §8, not assembled the week before.

---

## Open items

| # | Item | Blocks | Owner |
|---|---|---|---|
| 1 | ~~Which ranking are we scored on~~ | **RESOLVED 17 Sep: total return.** See `reports/superseded/DECISION_return_ranked.md`. Phases 3–5 superseded. | Done |
| 2 | ~~Do VBIL/VGUS/VSDB/VCHY trade on StockTrak~~ | **CONFIRMED tradable, 17 Sep** | Done |
| 3 | Does StockTrak credit distributions same-day or lagged | ~~Sharpe magnitude~~ **Sized: median 8.2 vs 2.4.** Structure unchanged either way | Observe 1 Oct |

Item 1 does not block anything before Phase 6. Item 2 is a two-minute platform
check and should be done immediately.
