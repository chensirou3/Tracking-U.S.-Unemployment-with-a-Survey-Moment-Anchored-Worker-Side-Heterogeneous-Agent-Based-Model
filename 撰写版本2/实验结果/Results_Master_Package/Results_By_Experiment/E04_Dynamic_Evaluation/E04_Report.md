# E4 — Dynamic Evaluation

## Purpose

Generate the manuscript's headline tracking number — the post-COVID UR RMSE of the recalibrated V_Full when run forward from a fixed 2018-01 initialisation without any re-fitting. The value 0.273 pp (5-seed mean, seed SD 0.023 pp) anchors the abstract and the opening paragraph of Section 6.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Evaluation driver | 正式撰写/fix6.2/run_fix6_2_reeval.py | Multi-seed re-evaluation of top-5 calibrations |
| Headline metrics | 正式撰写/fix6.2/reeval_metrics.json | Per-window per-seed UR/LFPR/EPOP metrics for V_Full |
| Variant summary | 正式撰写/fix6.2/tables/table1_variant_summary.csv | Row V_Full row contains 5-seed mean |
| Regime decomposition | 正式撰写/fix6.1/tables/table1_regime_summary.csv | Post-COVID row used for the headline |
| Trajectories (re-plot input) | 正式撰写/fix6.1/regime_series.npz | 5-seed UR paths for the F1 figure |

## Protocol

1. Load population_v1.npz once; the population is identical to E1.
2. Apply V_Full selected parameters from E3 (top-1 by train loss, no re-fit).
3. Initialise at 2018-01 from observed BLS values; the model takes the macro driver path (JTSJOR, JTSLDR, CES, FEDFUNDS) as exogenous input and does not re-fit after this point.
4. Simulate 5 seeds × the full evaluation window 2018-01..2026-02 (98 months).
5. Compute UR RMSE/MAE/bias/max-abs by regime window and overall, averaged across the 5 evaluation seeds.

## Main Outputs

- `tables/E04_T01_Dynamic_Evaluation_Metrics_v01.csv` — Post-COVID window single-row headline metrics
- `figures/E04_F01_Observed_vs_Simulated_UR_v01.png` — Full post-2018 UR overlay (5 seeds + mean)
- `figures/E04_F02_Prediction_Error_Time_v01.png` — Prediction error trace, 2018-2026

## Key Numbers

| Quantity | Value |
|---|---|
| UR RMSE (post-COVID normalisation, 2022-01..2026-02) | 0.273 pp |
| UR RMSE seed SD (5 seeds) | 0.023 pp |
| UR bias (post-COVID) | −0.04 pp |
| UR correlation with observed (post-COVID) | 0.79 |
| Seeds | {42, 137, 2024, 888, 1234} |
| Evaluation window length | 50 months |

## Use in Manuscript

- §6.1 (S06_01) primary headline
- Abstract anchor

## Caveats

- Dynamic multi-step, not rolling one-step. The model is not re-fit anywhere inside 2018-01..2026-02.
- Headline refers to ranking within the within-experiment accounting; manuscript must avoid 'dominates' or 'structurally identifies'.
- The 0.273 pp number must be reported jointly with the COVID-crisis 2.82 pp RMSE (see E5).

## Status

READY
