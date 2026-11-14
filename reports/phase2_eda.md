# Phase 2 - EDA, cleaning and regime

Generated 2026-09-17 00:14. Panel: 1936d x 98 tickers.

## Measured risk, replacing the brief's estimates

Brief S11.3 item 1 asks for every asterisked volatility figure to be replaced by a measurement. Full sample, annualised, rf = 0.

### Ten lowest-volatility funds

|      |    n |   ann_ret_% |   ann_vol_% |   sharpe_rf0 |   max_dd_% |
|:-----|-----:|------------:|------------:|-------------:|-----------:|
| VBIL |  399 |        3.99 |        0.28 |        13.79 |      -0.09 |
| VGUS |  399 |        3.92 |        0.32 |        11.9  |      -0.07 |
| VUSB | 1367 |        3.34 |        0.82 |         4.02 |      -1.79 |
| VGSH | 1936 |        2.07 |        1.73 |         1.18 |      -5.7  |
| VSDB |  364 |        3.78 |        1.85 |         2    |      -1.42 |
| BSV  | 1936 |        2.25 |        2.63 |         0.85 |      -8.54 |
| VCHY |   71 |       -0.08 |        2.82 |        -0.03 |      -1.24 |
| VTIP | 1936 |        3.76 |        3.03 |         1.22 |      -6.27 |
| VGMS |  317 |        4.95 |        3.15 |         1.53 |      -2.46 |
| VGVT |  299 |        1.74 |        3.27 |         0.53 |      -3.13 |

### Ten highest-volatility funds

|      |    n |   ann_ret_% |   ann_vol_% |   sharpe_rf0 |   max_dd_% |
|:-----|-----:|------------:|------------:|-------------:|-----------:|
| VIOG | 1936 |       14.16 |       24.57 |         0.54 |     -39.99 |
| VIOO | 1936 |       14.65 |       24.74 |         0.55 |     -42.37 |
| VBK  | 1936 |       15.16 |       24.8  |         0.57 |     -38.71 |
| VFVA | 1936 |       18.42 |       24.81 |         0.68 |     -47.94 |
| VTWO | 1936 |       15.29 |       24.93 |         0.57 |     -41.18 |
| VTWV | 1936 |       15.48 |       25.47 |         0.57 |     -44.27 |
| VIOV | 1936 |       15.13 |       25.83 |         0.55 |     -45.29 |
| VTWG | 1936 |       15.23 |       26.2  |         0.54 |     -42.07 |
| VGT  | 1936 |       31.01 |       26.78 |         1.01 |     -35.08 |
| VDE  | 1936 |       21.7  |       32.38 |         0.61 |     -64.92 |

## Stock-bond correlation regime

- Rolling 60-day correlation of the equal-weight equity sleeve against the bond sleeve
- Latest: **+0.54** | 1-year mean +0.43 | full-sample mean +0.14
- Fraction of the last year with positive correlation: **100%**

The brief (S11.1) warns that a 2021-2026 window encodes a positive stock-bond correlation that is not the long-run relationship, and that using it should be a conscious choice. The measurement above is what that choice is being made on.

## Index methodology break (CRSP to Morningstar)

| ticker   | ref   | break_date   |   te_ratio_before |   te_ratio_after |   jump |   corr_before |   corr_after |
|:---------|:------|:-------------|------------------:|-----------------:|-------:|--------------:|-------------:|
| VTI      | VTHR  | 2022-02-15   |              0.34 |             0.11 |  -0.24 |          0.98 |         1    |
| VV       | VONE  | 2025-11-03   |              0.07 |             0.14 |   0.07 |          1    |         1    |
| VO       | IVOO  | 2021-01-20   |              0.2  |             0.43 |   0.23 |          0.98 |         0.92 |
| VB       | VIOO  | 2021-01-28   |              0.22 |             0.42 |   0.19 |          0.97 |         0.94 |
| VTV      | VONV  | 2025-12-26   |              0.12 |             0.3  |   0.18 |          0.99 |         0.94 |
| VUG      | VONG  | 2025-12-11   |              0.05 |             0.18 |   0.13 |          1    |         0.98 |
| MGC      | VONE  | 2025-12-11   |              0.09 |             0.21 |   0.12 |          0.99 |         0.99 |
| MGK      | VONG  | 2022-12-15   |              0.08 |             0.17 |   0.09 |          1    |         0.99 |
| MGV      | VONV  | 2025-12-26   |              0.16 |             0.36 |   0.21 |          0.98 |         0.92 |

Tracking error is measured against an unaffected peer index fund and normalised by that peer's own volatility, then scanned for the largest sustained jump.

**Five of the nine funds break between 3 November and 26 December 2025** (MGC, MGV, VTV, VUG, VV), with correlation to their peers falling as they do. That cluster is the CRSP-to-Morningstar transition the brief flags in S11.1, and it is now dated rather than assumed.

**Consequence for the estimation window.** A window that reaches back before November 2025 straddles the break for these nine funds. A window starting in January 2026 is clean but only leaves ~180 observations. The bond sleeve is unaffected - no fixed income fund changed index - so this constrains the equity and blended portfolios, not the S9.1 short-end book.

VO and VB break in January 2021 against IVOO and VIOO. That is a different effect: CRSP and S&P mid- and small-cap indices differ in constituent coverage, and the 2021 small-cap rotation widened the gap. Not a methodology change in the fund.

## Proxy fits for young funds

| ticker   | proxy                        |    r2 |   te_bp_day |   n | quality   |
|:---------|:-----------------------------|------:|------------:|----:|:----------|
| VTG      | VGSH 29%, VGIT 46%, VGLT 20% | 0.982 |       2.961 | 298 | GOOD      |
| VDG      | VEA 43%, VGK 27%, VPL 33%    | 0.973 |      21.802 | 105 | FAIR      |
| VUSG     | VUG 21%, VONG 88%            | 0.966 |      23.044 | 206 | FAIR      |
| BNDP     | BND 74%, VCIT 18%            | 0.957 |       4.751 | 195 | GOOD      |
| VDV      | VEA 81%, VGK 4%              | 0.944 |      24.026 | 105 | FAIR      |
| VEXC     | VWO 88%, VPL 11%, VEA 4%     | 0.933 |      31.569 | 239 | FAIR      |
| VTP      | VTIP 115%, VGIT 5%, VGLT 21% | 0.904 |       6.465 | 298 | GOOD      |
| VGMS     | VCIT 32%, VWOB 32%           | 0.831 |       8.102 | 317 | FAIR      |
| VDIG     | VIG 86%, VOO 7%              | 0.815 |      28.873 | 206 | FAIR      |
| VUSV     | VTV 13%, VONV 59%, VOO 19%   | 0.788 |      33.026 | 206 | FAIR      |
| VSDB     | VCSH 30%, BSV 54%            | 0.78  |       5.421 | 364 | FAIR      |
| VGVT     | VGIT 63%, VMBS 19%           | 0.76  |      10.069 | 299 | FAIR      |
| VCHY     | VWOB 40%, VCIT 11%           | 0.757 |       8.589 |  71 | FAIR      |
| VGHY     | VWOB 33%, VCIT 26%           | 0.472 |      17.86  | 250 | WEAK      |
| VGUS     | BILL1M 132%, VGSH 7%         | 0.104 |       1.925 | 399 | WEAK      |
| VBIL     | BILL1M 142%, VGSH 1%         | 0.009 |       1.775 | 399 | WEAK      |

**VBIL and VGUS do not proxy from FRED bills.** The brief (S11.1) states they
"proxy cleanly with 1-month and 3-month Treasury bill yields from FRED". The fit
says otherwise: R2 0.01 and 0.10. The reason is mechanical rather than economic.
VBIL trades near $75.60, so one cent of price is 1.32 bp, while its daily total
return has a standard deviation of 1.79 bp. The series is dominated by tick
quantisation, and no yield series can track rounding.

This does not matter, because it does not need to. Both funds have 399
observations, which is ample to estimate the variance of an asset whose variance
*is* the tick. **Resolution: use their own history and set the estimation window
to their common sample, rather than backfilling a proxy that does not fit.**
