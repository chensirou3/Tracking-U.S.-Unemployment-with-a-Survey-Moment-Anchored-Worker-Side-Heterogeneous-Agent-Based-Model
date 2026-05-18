# S06_05 — Robustness and Sensitivity

**Manuscript section:** §6.5
**Supporting experiments:** E11 (Training-Window Sensitivity), E12 (Forecast-Horizon and Agent-Count Sensitivity), E13 (Calibration-Method Sensitivity and Parameter Identification)
**Source-of-evidence path:** `Results_By_Experiment/E11_Training_Window_Sensitivity/`, `E12_Forecast_Horizon_and_Agent_Count_Sensitivity/`, `E13_Calibration_Method_and_Parameter_ID_Sensitivity/`

## Headline result

Four robustness lenses, each implemented as a separately calibrated experiment, jointly indicate that the V_Full headline tracking and ranking are stable under the choices a referee is likely to question, while several individual structural parameters are weakly identified:

| Lens | Object varied | Headline | Status |
|---|---|---|---|
| **Training window (E11)** | 10 train/test splits (4 rolling + 5 expanding + 1 baseline) | M0 mean UR RMSE 0.245 ± 0.011 pp on 7 OOS-aligned splits; wins vs all 4 benchmarks on 6 of 7 | Stable at ranking level |
| **Forecast horizon (E12)** | h ∈ {1, 3, 6, 12, 24, 36} months | M0 log-log RMSE slope −0.092 — the shallowest among 8 models compared (AR slope +0.62) | Graceful long-horizon decay |
| **Agent count (E12)** | N ∈ {5k, 10k, 25k, 50k, 100k, 200k, 300k} | Plateau threshold (|ΔRMSE| < 0.015 pp) met at N ≥ 50k; default N=100k well past plateau | Default size justified |
| **Calibration method (E13)** | RandomSearch, LHS, Sobol, Coarse-to-Fine, DE — matched at 200 evals × 3 seeds | Best-test UR RMSE band 0.214–0.243 pp across methods; performance CV 5.55% | Prediction robust |
| **Parameter identification (E13)** | Per-parameter CV across top-5 candidates within each method | **10 of 14** parameters have CV ≥ 0.40 in at least one method; only 4 of 14 are CV < 0.20 stable | Weak identification documented |

The first three lenses (E11, E12) are computed on the **legacy M0 family** rather than the recalibrated V_Full; they are reported at the **ranking and shape level**, not as substitutes for the 0.273 pp headline. The fourth lens (E13) confirms that the prediction is robust across calibration methods (5.55% CV) but explicitly identifies the parameter-identification problem: 10 of 14 free parameters change materially across the top-5 candidates within a single calibration method. The manuscript must report parameters as bands, not point estimates.

## Paper-ready figures

- **`paper_ready_figures/S06_05_F01A_Training_Window__E11_v01.png`** — Standalone per-split UR RMSE bar (E11); OOS-aligned mean reference line; two rolling-window splits highlighted in red.
- **`paper_ready_figures/S06_05_F01B_Horizon_Decay__E12_v01.png`** — Standalone log-log forecast-horizon decay curve from E12: Full ABM (slope -0.09) versus AR / VAR / DMP.
- **`paper_ready_figures/S06_05_F01C_Agent_Count_Plateau__E12_v01.png`** — Standalone mean +/- SD UR RMSE versus agent count N on a log scale; default N = 100,000 line; plateau (|deltaRMSE| < 0.015 pp at N >= 50,000) on title.
- **`paper_ready_figures/S06_05_F01D_Parameter_ID__E13_v01.png`** — Standalone per-parameter coefficient of variation across the top-5 V_Full candidates; weak-ID threshold line at CV = 0.40; title states 10/14 above threshold.

## Paper-ready table

- **`paper_ready_tables/S06_05_T01_Robustness_Summary__E11_E12_E13_v01.csv`** — Twelve-row summary: lens, object varied, n_configurations, headline metric, value, dispersion, manuscript-facing claim, source experiment ID.

## Manuscript-facing wording (drop-in)

> Four robustness lenses test whether the tracking accuracy and benchmark ranking reported in §6.1 and §6.4 are stable under choices a referee might question. First, ten alternative train/test splits — four rolling, five expanding, and one baseline — produce a mean post-COVID UR RMSE of 0.245 ± 0.011 pp on the seven splits whose test window includes the post-COVID period; the ABM wins against all four legacy benchmarks on six of those seven splits. Second, the ABM's log-log RMSE slope against forecast horizon h = 1..36 months is −0.09, the shallowest among the eight models compared; classical time-series models such as AR(p) attain slopes above +0.6 over the same horizon range. Third, a population-size sweep over N from 5,000 to 300,000 agents identifies a plateau in mean UR RMSE at N ≥ 50,000; the default N = 100,000 used throughout the paper is therefore well past the threshold at which the simulation becomes insensitive to agent count. Fourth, holding the simulator fixed and varying the calibration method across Random Search, Latin Hypercube Sampling, Sobol, Coarse-to-Fine, and Differential Evolution under a matched budget of 200 evaluations × 3 seeds produces best-test UR RMSE in the band 0.21–0.24 pp, with a coefficient of variation of 5.55 percent across methods. The prediction is therefore robust to calibration method. The same experiment reveals the limit of structural identification: ten of the fourteen free parameters exhibit a coefficient of variation greater than 0.40 across the top-five candidates within a single calibration method. We accordingly report parameter values as bands rather than point estimates and refrain from describing the parameters as structurally identified.

## Caveats and wording rules

- E11/E12 are on legacy M0; report as ranking-level robustness, not as restatements of the 0.273 pp headline.
- The 10/14 weakly-identified parameter count is the central methodological caveat of the paper. The manuscript must use "weakly identified", "report bands", "robust prediction with non-unique parameterisation", and **never** "structurally identifies" for those ten parameters.
- The 5.55% CV across methods is a measure of *prediction* robustness, not parameter robustness. These are distinct claims and must remain so in the text.
- Plateau analysis: N=100k is the default; N=300k is the maximum tested; runtime/memory cost at N=300k is documented in E12 but not in this manuscript table.

## Status

READY — paper-ready table and four-panel figure are produced; numbers are traceable to `6.5/robustness_metrics.json` and `6.5/tables/`.

## Audit mirror (full evidence for the appendix)

This section folder additionally contains an `audit_mirror/` subfolder with verbatim copies of every figure and table from the source experiments **E11 (Training-Window Sensitivity)**, **E12 (Forecast-Horizon and Agent-Count Sensitivity)**, and **E13 (Calibration-Method and Parameter-ID Sensitivity)**: 5 figures + 5 tables. See `audit_mirror/_INDEX.md` for per-file provenance. The paper-ready four-panel dashboard in `paper_ready_figures/` summarises the four lenses; the audit-mirror files provide the underlying per-experiment detail for appendix assembly and reviewer-side traceability.
