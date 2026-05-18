# E11 — Training Window Sensitivity

## Purpose

Test whether the V_Full advantage persists across alternative training windows. Run 10 train/test splits (4 rolling + 5 expanding + 1 baseline) using a smaller legacy M0 family of the heterogeneous ABM, and rank against 4 benchmarks.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Package A runner | 正式撰写/包A_训练窗口敏感性/run_packageA.py (archived in 6.5 pipeline) | 10 splits × 60 LHS per split × M0 |
| Training window table | 正式撰写/6.5/tables/table2_training_window.csv | Per-split RMSE for M0, D1, D3, B3, B4 |
| Robustness JSON | 正式撰写/6.5/robustness_metrics.json | package_A block |
| Robustness figure (training) | 正式撰写/6.5/figures/fig2_training_splits.png | Per-split bar |

## Protocol

1. Define 10 splits: 4 rolling (R1..R4) + 5 expanding (E1..E5) + 1 baseline (S0).
2. Calibrate M0 separately on each split's training portion with LHS 60 draws.
3. Evaluate on each split's held-out window; compute UR RMSE.
4. Compare M0 to the four legacy benchmarks (D1 Homogeneous, D3 LaborOnly, B3 Beveridge, B4 DMP).
5. Report mean ± SD on the 7 OOS-aligned splits (those whose test window includes post-COVID) and the M0 win rate.

## Main Outputs

- `tables/E11_T01_Training_Window_Sensitivity_v01.csv` — Per-split UR RMSE for the 5 models
- `figures/E11_F01_Training_Window_Sensitivity_v01.png` — Per-split UR RMSE bar

## Key Numbers

| Quantity | Value |
|---|---|
| M0 mean UR RMSE on 7 OOS-aligned splits | 0.245 ± 0.011 pp |
| M0 win-rate vs B3 Beveridge | 10/10 |
| M0 win-rate vs all 4 benchmarks | 6/7 on OOS-aligned splits |
| Worst split (R1, 2014 cutoff) | M0 1.88 pp (training window predates COVID) |

## Use in Manuscript

- §6.5 (S06_05) robustness — training window

## Caveats

- Computed on the legacy M0 family (pre-fix6.x recalibration), not on V_Full recalibrated at 0.273 pp. Use as ranking-level robustness, not as a substitute for the headline.
- Splits R1 and R2 have test windows that overlap the 2020 crisis; their high RMSE is expected.
- Win-rate is reported in count, not as a hypothesis test.

## Status

READY WITH CAVEAT
