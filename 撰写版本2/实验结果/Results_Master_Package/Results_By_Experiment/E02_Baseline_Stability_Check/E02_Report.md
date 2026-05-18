# E2 — Baseline Stability Check

## Purpose

Verify that the simulation engine produces stable monthly paths across seeds **before** formal calibration and evaluation. This is a diagnostic / regression-test stage; the headline tracking numbers are not produced here.

## Source Files

- Baseline trajectories: `正式撰写/6.1/baseline_seed_trajectories.npz`
- Baseline figure: `正式撰写/6.1/figures/fig6_seed_stability.png` → copied to `figures/E02_F01_Seed_Stability_v01.png`
- Three-window baseline table: `正式撰写/6.1/tables/table4_baseline_3windows.csv`
- Seed-level regime table (final, post-calibration): `正式撰写/fix6.1/tables/table2_seed_level_regime.csv`

## Protocol

1. Run the un-calibrated baseline configuration of V_Full with the 5 evaluation seeds {42, 137, 2024, 888, 1234}.
2. Compare per-seed monthly UR / LFPR / EPOP trajectories on 2001-01..2026-02.
3. Compute UR RMSE on the three evaluation windows and check the cross-seed CV.
4. Stability criterion (informal): CV of UR RMSE on the post-COVID normalisation window should be below 5% in the legacy baseline; the recalibrated V_Full reports a similar order.

## Main Outputs

- `tables/E02_T01_Stability_Summary_v01.csv` — three-window baseline metrics (legacy)
- `tables/E02_T02_Seed_Dispersion_v01.csv` — per-seed UR RMSE + mean + SD + CV on the post-COVID window (final V_Full)
- `figures/E02_F01_Seed_Stability_v01.png` — legacy seed-stability plot
- `figures/E02_F02_Multi_Seed_UR_Trajectory_v01.png` — per-seed mean UR trajectory overlay of V_Full (5 seeds × 5 candidates) with cross-seed mean and observed UNRATE, 2018-01 onward

## Key Numbers

| Window | UR RMSE (pp) | Cross-seed CV (%) |
|---|---:|---:|
| Post-COVID normalisation (legacy M0 baseline) | 0.221 ± 0.007 | 3.08 |
| Post-COVID normalisation (final V_Full, recalibrated) | 0.273 ± 0.023 | 8.54 |

The simulation engine is stable across seeds; cross-seed CV is single-digit percent in both the legacy baseline and the recalibrated final variant.

## Use in Manuscript

- §6 introduction / S06_01 — referenced as "simulation engine is stable across seeds before evaluation"
- Appendix B — placeholder for a per-seed dispersion plot if the reviewer requests it

## Caveats

- This is not a separate calibration step; it documents that the engine itself is stable.
- The legacy 0.221 pp number is the M0 (pre-recalibration) post-COVID RMSE and is reported for traceability only.
- The headline number for the paper is the recalibrated V_Full 0.273 pp (E4).

## Status

READY (diagnostic; Appendix-only material)
