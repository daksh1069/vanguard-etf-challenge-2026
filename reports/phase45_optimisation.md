# Phase 4 + 5 - optimisation, validation, execution

Generated 2026-09-17 09:33. Universe 85 funds, sample 2025-04-04 to 2026-09-16 (364d).

## The covariance bug in the brief's script

Brief S11.2 runs `LedoitWolf().fit(r.values).covariance_`. Ledoit-Wolf shrinks
toward `mu * I`, where `mu` is the **average variance across the whole universe**.
With T-bill funds and equity sector funds in the same matrix, that average is set
by the equities. Measured on our panel, the shrinkage raises annualised volatility:

| fund | sample vol | after Ledoit-Wolf | inflation |
|---|---|---|---|
| VBIL | 0.285% | 3.69% | **13.0x** |
| VGUS | 0.320% | 3.69% | **11.5x** |
| VUSB | 0.718% | 3.74% | 5.2x |
| VTI | 16.73% | 16.65% | 1.0x |

The equities are untouched and the short end is destroyed - precisely inverted
from what this competition rewards. A max-Sharpe solve on that matrix cannot see
the T-bill trade at all.

**Fix:** shrink the *correlation* matrix toward a constant-correlation target and
keep the sample variances on the diagonal (`vgdata.optimise.covariance`, method
`corr_shrink`). Variances are then preserved exactly, and only the badly
estimated off-diagonal structure is stabilised.

## Recommended book

|      |   weight |
|:-----|---------:|
| VBIL |   0.2411 |
| VGUS |   0.2411 |
| VUSB |   0.2411 |
| VGSH |   0.2369 |
| VTIP |   0.02   |
| VSDB |   0.0197 |

Ex-ante: {'ex_ante_sharpe': 7.366404860062098, 'ann_return_%': 4.029312251637256, 'ann_vol_%': 0.5469849035155107, 'window_return_%': 0.6395733732757549, 'n_positions': 6, 'max_weight': 0.24114442182576326}

Solved globally with cvxpy via the Schaible transform, long-only, fully invested, 25% position cap. Padded to six holdings with small positions rather than by tightening the cap - tightening to 1/6 would dilute VBIL and VGUS to 16.7% and cost about 2.2 points of realised Sharpe.

## Robustness to the crediting branch

|          |   median |   p10 |
|:---------|---------:|------:|
| ex_date  |     7.81 |  4.04 |
| pay_date |     2.32 |  1.5  |

**The optimal book is nearly identical under both branches** (pay-date optimum is VBIL 25 / VGUS 25 / VUSB 24 / VGSH 21 / VTIP 3). So the portfolio does not depend on resolving the October question - only its expected score does.

## Stationary bootstrap, 40-day realised Sharpe

|          |   median |   p05 |   p95 |   P(Sharpe>2) |
|:---------|---------:|------:|------:|--------------:|
| ex_date  |     6.83 |  1.8  | 11.95 |          0.94 |
| pay_date |     2.28 | -0.02 |  4.98 |          0.58 |

2,000 stationary-bootstrap draws (expected block 10 days), which is the estimator the brief asks for in S12.4 in place of overlapping blocks.

## ERP sensitivity

|      |   n_pos |   equity_weight | top                                             |
|:-----|--------:|----------------:|:------------------------------------------------|
| 3.0% |       6 |               0 | VBIL 24%, VGUS 24%, VUSB 24%, VGSH 24%, VSDB 2% |
| 4.5% |       6 |               0 | VBIL 24%, VGUS 24%, VUSB 24%, VGSH 24%, VTIP 2% |
| 6.0% |       6 |               0 | VBIL 24%, VGUS 24%, VUSB 24%, VGSH 24%, VTIP 2% |

The book is **insensitive to the equity risk premium across 3-6%**. With rf = 0 the short end dominates on risk-adjusted terms at any plausible ERP, so the assumption the brief flags as its largest modelling risk (S11.1) turns out not to matter for this portfolio.

## Rate shock

Empirical duration from regressing each fund's daily return on the daily change in the 2-year Treasury yield:

|      |   emp_duration_yrs |
|:-----|-------------------:|
| VBIL |              -0.02 |
| VGUS |               0.08 |
| VUSB |               0.53 |
| VGSH |               1.58 |
| VTIP |               1.32 |
| VSDB |               1.71 |

Parallel shift applied to the book, against 40 days of carry:

|        |   price_% |   carry_% |   total_% |
|:-------|----------:|----------:|----------:|
| -100bp |     0.577 |      0.64 |     1.217 |
| -50bp  |     0.289 |      0.64 |     0.928 |
| -25bp  |     0.144 |      0.64 |     0.784 |
| +25bp  |    -0.144 |      0.64 |     0.495 |
| +50bp  |    -0.289 |      0.64 |     0.351 |
| +100bp |    -0.577 |      0.64 |     0.063 |

## Execution package - per account, identical across all four

|      |    weight |   last_px |   est_fill |   shares |   notional |   actual_weight |
|:-----|----------:|----------:|-----------:|---------:|-----------:|----------------:|
| VBIL | 0.241144  |     75.6  |      75.6  |      797 |      60254 |          0.241  |
| VGUS | 0.241144  |     75.52 |      75.52 |      798 |      60266 |          0.2411 |
| VUSB | 0.241144  |     49.54 |      49.54 |     1216 |      60244 |          0.241  |
| VGSH | 0.236881  |     57.62 |      57.62 |     1027 |      59180 |          0.2367 |
| VTIP | 0.02      |     49.35 |      49.35 |      101 |       4985 |          0.0199 |
| VSDB | 0.0196853 |     75.11 |      75.12 |       65 |       4883 |          0.0195 |

- Commission: $60 (6 trades, clears the five-trade minimum)
- Residual cash: **$128 = 0.05%** (cap is 10%)
- Estimated spread cost: $11
- No fractional shares. All four accounts hold identical weights (brief S4.5).
