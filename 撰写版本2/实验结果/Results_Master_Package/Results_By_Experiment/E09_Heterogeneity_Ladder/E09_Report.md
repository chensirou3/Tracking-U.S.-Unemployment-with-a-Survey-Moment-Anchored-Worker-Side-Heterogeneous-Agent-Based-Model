# E9 — Heterogeneity Ladder

## Purpose

Build the heterogeneity ladder L0..L6 by incrementally adding heterogeneity dimensions, each level separately re-calibrated. Provides the marginal-gain evidence that complements E8: ablation-from-full asks 'what is lost?'; the ladder asks 'what is gained per dimension added?'.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Ladder runner (Refit) | 正式撰写/6.3/run_6_3_packageC_ladder.py | Core L0..L6 + Layer G2, G3 with LHS 30 × 3 seeds per level |
| Ladder metrics | 正式撰写/6.3/ladder_metrics.json | Per-level per-seed train/val/oos metrics |
| Ladder summary table | 正式撰写/6.3/tables/table3_heterogeneity_ladder.csv | Per-level RMSE and seed SD |
| Trajectories | 正式撰写/6.3/ladder_series.npz | Per-level 5-seed UR/LFPR/EPOP |

## Protocol

1. Define seven Core ladder levels L0 (no heterogeneity) through L6 (all six dimensions).
2. Order of insertion: search → labour_fragility → liquidity → income_expect → consumption_rule → housing.
3. At each level, calibrate by LHS 30 draws × 3 calibration seeds; pick the best by train loss.
4. Re-evaluate the best on 5 final seeds; compute UR/LFPR/EPOP RMSE on post-COVID window.
5. Also report two Layer ladders (G2, G3) for sensitivity to insertion order.

## Main Outputs

- `tables/E09_T01_Heterogeneity_Ladder_v01.csv` — Per-level RMSE table
- `figures/E09_F01_Ladder_RMSE_Path_v01.png` — Marginal-gain step plot L0..L6
- `figures/E09_F02_Per_Level_UR_Trajectory_v01.png` — Per-level mean UR trajectory overlay (L0..L6) against observed UNRATE on the post-COVID window

## Key Numbers

| Quantity | Value |
|---|---|
| L0 UR RMSE (no heterogeneity) | 0.55 pp (matches V_Homogeneous) |
| L6 UR RMSE (all 6 dims) | 0.27 pp (matches V_Full) |
| Largest single drop (L4→L5, adding housing) | ≈ −0.07 pp |
| Smallest gain (between adjacent levels) | within seed SD |

## Use in Manuscript

- §6.3 (S06_03) supplementary ladder evidence

## Caveats

- Order of insertion is fixed; marginal gains are order-dependent. Manuscript reports the gains as one specific accounting path, not as a unique decomposition.
- Each level is independently calibrated; differences are partly absorbed by parameter re-fitting.
- Several adjacent-level differences are smaller than the 0.023 pp seed SD; only L0/L6 and the housing step are well-separated.

## Status

READY
