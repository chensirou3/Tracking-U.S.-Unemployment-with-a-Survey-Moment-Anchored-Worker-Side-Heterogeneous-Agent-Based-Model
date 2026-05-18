# E6 — Internal Control Comparison

## Purpose

Compare V_Full against three internal controls — V_Homogeneous (no heterogeneity, all mechanisms on), V_LaborOnly (labour-side dimensions only), and V_Simplified (no heterogeneity, single mechanism) — each separately calibrated under the same LHS budget and loss function. The four-row ladder is the foundation of the source-of-advantage accounting in E7.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Calibration driver | 正式撰写/fix6.2/run_fix6_2_calibrate.py | 100/100/100/30 LHS budget across 4 variants × 3 cal-seeds |
| Re-evaluation driver | 正式撰写/fix6.2/run_fix6_2_reeval.py | Top-5 of each variant re-evaluated on 5 final seeds |
| Variant summary | 正式撰写/fix6.2/tables/table1_variant_summary.csv | Per-variant aggregate |
| Regime × variant | 正式撰写/fix6.2/tables/table7_regime_x_variant.csv | Per-window per-variant metrics |
| Seed-level metrics | 正式撰写/fix6.2/tables/table3_seed_level_metrics.csv | Per-seed per-variant rows |
| Trajectories | 正式撰写/fix6.2/reeval_trajectories.npz | 5×5×302 UR/LFPR/EPOP per variant |

## Protocol

1. Define four variant configurations: V_Full (reference), V_Homogeneous, V_LaborOnly, V_Simplified.
2. Calibrate each variant separately with identical LHS budget (100/100/100/30 draws across 3 cal-seeds) and identical loss function.
3. Take the top-5 candidates of each variant by mean train loss; re-evaluate on the 5 final seeds.
4. Report 5-seed mean UR RMSE for the headline window (post-COVID normalisation 2022-01..2026-02).
5. Decompose by regime in the regime_x_variant cross-tab.

## Main Outputs

- `tables/E06_T01_Control_Comparison_v01.csv` — Per-variant aggregate (UR/LFPR/EPOP RMSE, train loss)
- `tables/E06_T02_Regime_by_Variant_v01.csv` — Regime × variant cross-tab
- `tables/E06_T03_Seed_Level_Variant_v01.csv` — Per-seed per-variant rows
- `figures/E06_F01_Control_RMSE_Bar_v01.png` — UR RMSE bar across 4 variants
- `figures/E06_F02_Variant_UR_Lines_v01.png` — Mean UR trajectory by variant
- `figures/E06_F03_Regime_by_Variant_Heatmap_v01.png` — Regime × variant heatmap
- `figures/E06_F04_Within_Variant_Dispersion_v01.png` — Top-5 within-variant dispersion

## Key Numbers

| Quantity | Value |
|---|---|
| UR RMSE V_Full | 0.273 pp |
| UR RMSE V_Homogeneous | 0.545 pp |
| UR RMSE V_LaborOnly | 0.363 pp |
| UR RMSE V_Simplified | 0.562 pp |
| Variants separately calibrated? | Yes |
| Final evaluation seeds | {42, 137, 2024, 888, 1234} |

## Use in Manuscript

- §6.2 (S06_02) internal controls

## Caveats

- The differences feed the within-experiment source-of-advantage accounting (E7); they are not causal decompositions.
- V_Simplified retains the matching_competition mechanism; it is not literally a zero-mechanism baseline.
- Each variant is re-calibrated under the same LHS budget, so differences are not driven by calibration effort asymmetry.

## Status

READY
