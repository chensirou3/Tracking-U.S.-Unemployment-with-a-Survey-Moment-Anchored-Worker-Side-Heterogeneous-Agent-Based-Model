# E5 — Regime Specific Evaluation

## Purpose

Decompose the V_Full performance into three regime windows — pre-COVID stable, COVID crisis, and post-COVID normalisation — to expose where the headline number comes from and where the model under-tracks. Pairs with E4.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Regime driver | 正式撰写/fix6.1/run_fix6_1_regime.py | Regime-decomposed metrics computation |
| Regime metrics | 正式撰写/fix6.1/regime_metrics.json | Per-window per-seed metrics |
| Regime summary table | 正式撰写/fix6.1/tables/table1_regime_summary.csv | Aggregate across 5 seeds, 5 windows |
| Seed-level regime | 正式撰写/fix6.1/tables/table2_seed_level_regime.csv | Per-seed cross-window metrics |
| Trajectories | 正式撰写/fix6.1/regime_series.npz | 5-seed UR/LFPR/EPOP for plotting |

## Protocol

1. Reuse the same 5-seed V_Full trajectories from E4.
2. Define four manuscript-facing windows: pre_covid_stable (2018-01..2019-12), covid_crisis_mar (2020-03..2021-12), post_covid_norm (2022-01..2026-02), full_post_2018 (2018-01..2026-02).
3. Compute UR/LFPR/EPOP RMSE, MAE, bias, max-abs, and correlation per window, averaged across the 5 seeds.
4. Also report the alternative covid_crisis_jan window (2020-01..2021-12) for sensitivity.

## Main Outputs

- `tables/E05_T01_Regime_Performance_v01.csv` — Aggregate metrics for the 5 windows (UR + LFPR + EPOP)
- `tables/E05_T02_Seed_Level_Regime_v01.csv` — Per-seed metrics, 5×5 = 25 rows
- `figures/E05_F01_Regime_RMSE_Bar_v01.png` — UR RMSE + bias bar by window
- `figures/E05_F02_LFPR_EPOP_Regime_Bar_v01.png` — LFPR / EPOP RMSE by window

## Key Numbers

| Quantity | Value |
|---|---|
| Pre-COVID UR RMSE / bias | 0.79 pp / +0.77 pp |
| COVID-crisis UR RMSE / bias | 2.82 pp / −2.07 pp |
| Post-COVID UR RMSE / bias | 0.273 pp / −0.04 pp |
| Full post-2018 UR RMSE | 1.42 pp (dominated by 2020 crisis months) |
| UR correlation, COVID crisis | 0.75 (direction correct, magnitude under) |

## Use in Manuscript

- §6.1 (S06_01) regime decomposition

## Caveats

- The full post-2018 RMSE of 1.42 pp is driven by COVID-crisis months; not a substitute for the post-COVID headline.
- Reporting only the post-COVID number without the crisis number is inadmissible per the wording policy.
- The COVID-crisis window's high RMSE is consistent with the survey-moment anchoring not extending to 2020 shock parameters.

## Status

READY
