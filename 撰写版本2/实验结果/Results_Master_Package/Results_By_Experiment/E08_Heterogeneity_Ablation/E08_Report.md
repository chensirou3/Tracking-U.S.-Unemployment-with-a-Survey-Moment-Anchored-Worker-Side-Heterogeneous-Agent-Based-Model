# E8 — Heterogeneity Ablation

## Purpose

Quantify how much UR-RMSE the model loses when individual heterogeneity dimensions are removed and the variant is re-calibrated. The headline finding is that V_NoSearch and V_NoSLH (joint Search+Liquidity+Housing flatten) cannot be compensated by recalibration, while V_NoLiquidity and V_NoHousing recover near-baseline performance.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Calibration driver | 正式撰写/fix6.3/run_fix6_3_calibrate.py | LHS 100 × 3 cal-seeds × 6 ablation variants |
| Re-evaluation driver | 正式撰写/fix6.3/run_fix6_3_reeval.py | Top-5 × 5 final seeds × 6 variants |
| Ablation summary | 正式撰写/fix6.3/tables/table2_post_covid_ablation.csv | Post-COVID RMSE + Δ vs Full |
| Old-vs-new delta | 正式撰写/fix6.3/tables/table5_old_vs_new_delta.csv | Pre-recalibration vs recalibrated |
| Regime × ablation | 正式撰写/fix6.3/tables/table6_regime_x_ablation.csv | Per-window per-ablation |
| Paper-ready compact | 正式撰写/fix6.3/tables/table7_paper_ready.csv | 5-row summary used in manuscript |
| Trajectories | 正式撰写/fix6.3/reeval_trajectories.npz | 5×5×302 paths per variant |

## Protocol

1. Define 6 ablation variants: V_NoSearch, V_NoLiquidity, V_NoHousing, V_NoSLH, V_NoConsumption, V_SearchOnly.
2. Each variant flattens exactly the heterogeneity dimensions named in its label; mechanisms remain ON.
3. Calibrate each variant separately under the same LHS budget as fix6.2.
4. Re-evaluate top-5 candidates × 5 final seeds.
5. Compare post-COVID UR RMSE to V_Full reference (0.273 pp).

## Main Outputs

- `tables/E08_T01_Recalibrated_Ablation_v01.csv` — Post-COVID RMSE per variant + Δ
- `tables/E08_T02_Old_vs_New_Delta_v01.csv` — Δ between projection and recalibration
- `tables/E08_T03_Regime_by_Ablation_v01.csv` — Regime × ablation cross-tab
- `figures/E08_F01_Ablation_RMSE_Bar_v01.png` — RMSE bar with Δ annotation
- `figures/E08_F02_Old_vs_New_Delta_v01.png` — Projection vs recalibration gap
- `figures/E08_F03_Regime_by_Ablation_Heatmap_v01.png` — Regime × ablation heatmap
- `figures/E08_F04_NoSearch_Trajectory_v01.png` — Worst-case V_NoSearch path

## Key Numbers

| Quantity | Value |
|---|---|
| V_Full reference UR RMSE | 0.273 pp |
| V_NoSearch UR RMSE (Δ vs Full) | 1.085 pp (+0.812) |
| V_NoSLH joint UR RMSE (Δ) | 0.702 pp (+0.429) |
| V_NoLiquidity UR RMSE (Δ) | 0.378 pp (+0.105) |
| V_NoHousing UR RMSE (Δ) | 0.237 pp (−0.036) |
| V_NoConsumption UR RMSE (Δ) | ranking: matches or beats Full after recalibration |

## Use in Manuscript

- §6.3 (S06_03) headline ablation

## Caveats

- Δ values are within-experiment accounting deltas, not causal contributions.
- V_NoHousing slightly outperforming V_Full is consistent with re-calibration absorbing the lost dimension into other parameters; it does not imply housing heterogeneity is harmful.
- Joint V_NoSLH is included to test whether single-dimension Δ values are additive — they are not (0.812 + 0.105 + (−0.036) ≠ 0.429).

## Status

READY
