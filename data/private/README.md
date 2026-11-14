# data/private/ — local-only inputs

Everything in this folder except this README is gitignored. These files are either licensed (Bloomberg), belong to
other people (the organizer's exports of every team's account), or are copies of third-party web pages. The derived
results that matter are committed elsewhere (for example `data/processed/real_hedged_ishg_monthly.csv`), so the
reports, charts and PDFs can be read and rebuilt without them. Only the scripts listed below need these files.

| path | what it is | needed by |
|---|---|---|
| `bloomberg/etf_test_data.xlsx` | The team's Bloomberg workbook (9 Nov 2026): Test A (hedged 3-month bills vs T-bills), Test B (forward-point spreads in calm and stress), Test D (fund screen), plus spot and 1M forward series for EUR, JPY, GBP, CAD and AUD | `scripts/pitch/validate_etf_test_data.py`, `scripts/pitch/real_hedged_full.py` |
| `competition/2026-09-17/` | Organizer exports at the start of trading: every team's open positions, trade notes and the team rankings | `scripts/trading/book_selection/*` and `scripts/trading/live/one_day_lag.py`, `reoptimise_lag.py` |
| `competition/2026-11-04/<team>/` | Organizer exports in the final week, one folder per team (open positions, trade notes, transactions) | `scripts/trading/live/final_week.py`, `final_two_days.py`, `final_day*.py` |
| `competition/rankings/TeamRankings_11_0{3,5}_2026.csv` | Official StockTrak team standings on 3 and 5 Nov | `scripts/trading/live/final_day_official.py` |
| `web_sources/ftse_wgbi_dm_1-3y_capped_select_factsheet_20261031.pdf` | FTSE Russell factsheet for the index the proposed fund tracks | facts in `docs/pitch/PITCH_FACTS_VERIFIED.md` |
| `web_sources/etfdb_international_government_bonds_20261112.csv` | etfdb.com export of the "International Government Bonds" ETF category | the gap analysis |
| `web_sources/vanguard_bndx_page_20261110.*` | Saved copy of Vanguard's BNDX fund page | BNDX facts |
| `web_sources/boj_policy_rate_notes.txt` | Notes on Bank of Japan policy-rate decisions (Trading Economics / BoJ) | the rates slide |

The public sources are cited with links in `docs/pitch/PITCH_FACTS_VERIFIED.md`.
