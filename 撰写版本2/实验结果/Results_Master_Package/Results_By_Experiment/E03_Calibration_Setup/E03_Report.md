# E3 — Calibration Setup

## Purpose

Fit the mechanism parameters of V_Full and the comparison variants to the BLS UR / LFPR / EPOP and gross-flow targets on the training window 2004-01..2017-12, using a multi-target weighted loss.

## Source Files

- Calibration drivers: `正式撰写/fix6.2/run_fix6_2_calibrate.py`, `正式撰写/fix6.3/run_fix6_3_calibrate.py`
- Calibration progress: `正式撰写/fix6.2/checkpoints/V_*_progress.csv`, `正式撰写/fix6.3/checkpoints/V_*_progress.csv`
- Selected parameters: `正式撰写/fix6.2/tables/table5_calibrated_params.csv`
- Parameter table (P1 deliverable): `撰写版本2/cheacklist/ABM_Calibration_Parameter_Table.csv`
- Parameter top-5 bands (P1 deliverable): `撰写版本2/cheacklist/ABM_Calibration_Parameter_Bands.csv`
- Loss formula: `正式撰写/fix6.2/run_fix6_2_calibrate.py` lines 106–123

## Protocol

1. Training window = 2004-01..2017-12 (168 months; indices [36, 204) of the 302-month grid; first 36 months are warm-up).
2. Latin Hypercube Sampling with a 100/100/100/30 budget on the 14-dimensional active parameter box.
3. Loss = weighted sum:
   `L_train = 5.0 · L_ur + 2.0 · L_lfpr + 2.0 · L_epop + 1.0 · L_eu + 1.0 · L_ue + 0.5 · L_h2m`
   where L_ur, L_lfpr, L_epop are RMSEs in decimal units and the flow / structural terms are |dev| × constant.
4. Three calibration seeds {42, 137, 2024} are averaged for the loss; the top candidate by training loss is selected.
5. Each variant (V_Full / V_Homogeneous / V_LaborOnly / V_Simplified / 6 ablations) is calibrated independently.

## Main Outputs

- `tables/E03_T01_Calibration_Parameter_Table_v01.csv` — 14 parameters with bounds and per-variant ACTIVE/INACTIVE map
- `tables/E03_T02_Parameter_Bands_v01.csv` — top-5 IQR / P25 / P50 / P75 / min / max for every (variant, parameter) cell across all 10 variants
- `tables/E03_T03_Loss_Function_Weights_v01.csv` — closed-form weights with anchor sources
- `tables/E03_T04_Calibration_Setup_Meta_v01.csv` — window, seeds, method, weak-ID preview
- `figures/E03_F01_Parameter_Top5_IQR_v01.png` — per-parameter Top-5 IQR position within search bounds for V_Full ([P25, P75] error bar by parameter)
- `figures/E03_F02_Loss_Tier_Weights_v01.png` — horizontal bar chart of six target-moment weights grouped by tier (1 = UR, 2 = secondary, 3 = auxiliary)
- `figures/E03_F03_Calibration_Convergence_v01.png` — two-panel: (a) running-minimum train loss per seed across the 100 LHS candidates; (b) per-seed boxplot of all candidate losses

## Key Numbers

- Training window: 2004-01..2017-12 (168 months)
- Calibrated parameters (V_Full): 14
- Loss weights: 5.0 / 2.0 / 2.0 / 1.0 / 1.0 / 0.5 (UR / LFPR / EPOP / EU / UE / H2M)
- Calibration seeds: 3 ({42, 137, 2024}); evaluation seeds: 5 (strict superset)
- Train loss (V_Full top-1): 0.1672; train loss (V_Simplified top-1): 0.7606
- Weakly identified parameters (preview from E13): 10 of 14 (CV ≥ 0.40 across top-5 candidates)

## Use in Manuscript

- §5 (Experimental Design) — calibration window, seeds, method, loss formula
- §6 introduction — one-line summary of training window and conservative comparison vs benchmarks
- Appendix B — parameter table with bounds and bands

## Caveats

- Parameter values are **fitted simulation quantities**, not structural estimates. Bands (not point estimates) are the appropriate manuscript representation.
- Three of fourteen parameters are inactive in V_LaborOnly and twelve are inactive in V_Simplified (see Parameter Table for per-variant map).
- The benchmark comparison window (E10) uses the full 2001-01..2022-01 history for the benchmarks. This is intentional and is documented as a conservative comparison for the ABM (see E10 / S06_04 / `撰写版本2/cheacklist/ABM_Simulation_Calendar.md` §4).

## Status

READY
