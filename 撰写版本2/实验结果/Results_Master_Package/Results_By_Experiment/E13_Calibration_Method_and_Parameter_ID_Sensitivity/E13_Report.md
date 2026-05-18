# E13 — Calibration Method and Parameter ID Sensitivity

## Purpose

Test sensitivity of (a) headline UR RMSE and (b) selected parameter values across five calibration methods: Random Search, Latin Hypercube Sampling, Sobol, Coarse-to-Fine, Differential Evolution. The findings: prediction is robust (CV 5.55%), but 10 of 14 parameters have CV ≥ 0.40 across top-5 candidates — weakly identified.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Package E runner | 正式撰写/包E_校准方法敏感性/run_packageE.py (archived in 6.5 pipeline) | 5 methods × 200 evals × 3 seeds |
| Calibration method table | 正式撰写/6.5/tables/table5_calibration_method.csv | Best-test UR per method + advantage share |
| Robustness JSON | 正式撰写/6.5/robustness_metrics.json | packageE_calibration block (performance_lens + param_lens) |
| Calibration figure | 正式撰写/6.5/figures/fig5_calibration_sensitivity.png | Best-test RMSE per method |
| Parameter heatmap | 正式撰写/6.5/figures/fig6_param_drift_heatmap.png | Per-param CV across methods |

## Protocol

1. Define five calibration methods with matching evaluation budget of 200 simulations × 3 seeds.
2. For each method, calibrate V_Full; record top-5 candidates by train loss.
3. Re-evaluate top-5 of each method on the held-out post-COVID window.
4. Compute (a) performance lens: CV of best-test UR RMSE across methods; (b) parameter lens: per-parameter CV across top-5 candidates within each method.
5. Flag parameters as weakly identified if CV ≥ 0.40 in any method.

## Main Outputs

- `tables/E13_T01_Calibration_Method_Sensitivity_v01.csv` — Per-method best-test UR + share advantage
- `tables/E13_T02_Parameter_Identification_v01.csv` — Per-parameter CV + unstable flag + performance lens summary
- `figures/E13_F01_Calibration_Method_Sensitivity_v01.png` — Method × performance
- `figures/E13_F02_Parameter_ID_Heatmap_v01.png` — Parameter × method CV heatmap

## Key Numbers

| Quantity | Value |
|---|---|
| Best-test UR RMSE range across 5 methods | 0.214 – 0.243 pp |
| CV of best-test UR RMSE (performance lens) | 5.55% |
| Weakly identified parameters (CV ≥ 0.40) | 10 of 14 |
| Stable parameters (CV < 0.40; complement of weak) | 4 of 14 |
| Strictly stable parameters (CV < 0.20) | 1 of 14 (`h2m_mpc_floor` only) |
| Source-of-advantage share stability across methods | 57.2 ± 3.4 pp |

## Use in Manuscript

- §6.5 (S06_05) calibration method and parameter identification

## Caveats

- Best-test UR RMSE band centred on the legacy 0.22 pp number; recalibrated V_Full (E4) at 0.273 pp is outside this band but within the legacy-vs-recalibrated reconciliation documented in fix6.2.
- Weak identification of 10/14 parameters does not invalidate the forecast — prediction is robust because of substitution between parameters.
- Report parameters as bands, not point estimates. Manuscript must avoid 'structurally identifies' for the 10 weak parameters.

## Status

READY
