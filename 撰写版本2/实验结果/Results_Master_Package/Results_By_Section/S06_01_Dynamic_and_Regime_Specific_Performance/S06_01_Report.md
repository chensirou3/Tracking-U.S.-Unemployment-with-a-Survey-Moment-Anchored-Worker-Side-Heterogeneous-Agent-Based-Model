# S06_01 — Dynamic and Regime-Specific Performance

**Manuscript section:** §6.1
**Supporting experiments:** E4 (Dynamic Evaluation), E5 (Regime-Specific Evaluation)
**Source-of-evidence path:** `Results_By_Experiment/E04_Dynamic_Evaluation/` and `E05_Regime_Specific_Evaluation/`

## Headline result

Across the post-COVID normalisation window 2022-01..2026-02, the recalibrated V_Full ABM tracks the U.S. unemployment rate with a 5-seed mean RMSE of **0.273 pp** (seed SD 0.023 pp), bias close to zero (−0.04 pp), and correlation 0.79. This is the manuscript's headline tracking number and the value cited in the abstract.

The same model, run forward over the COVID crisis window 2020-03..2021-12 without refit, attains UR RMSE 2.82 pp and bias −2.07 pp. The direction of the unemployment spike is captured (correlation 0.75), but the magnitude is systematically under-predicted. Both numbers must be reported together — the post-COVID headline is not admissible in isolation.

Over the full post-2018 evaluation window (97 months), the aggregate UR RMSE is 1.42 pp, but this is dominated by the 22 COVID-crisis months and is reported as a diagnostic, not as a headline.

## Paper-ready figures

- **`paper_ready_figures/S06_01_F01A_Observed_vs_Simulated_UR_Full__E4_v01.png`** — Standalone full post-2018 window. Observed BLS UNRATE versus the 5-seed simulated V_Full UR with the three regimes shaded (early stable / 2020-2021 disruption / main recent evaluation). Source: `fix6.2/reeval_trajectories.npz V_Full_ur` averaged over 5 calibration candidates.
- **`paper_ready_figures/S06_01_F01B_Observed_vs_Simulated_UR_MainEval__E4_v01.png`** — Standalone main recent evaluation window (2022-01..2026-02) with the V_Full UR RMSE = 0.273 pp headline call-out and cross-seed SD = 0.023 pp. Same source as F01A.
- **`paper_ready_figures/S06_01_F02A_Regime_RMSE_Bar__E5_v01.png`** — UR RMSE by evaluation window (early stable / 2020-2021 disruption / main recent evaluation / full post-2018) with cross-seed error bars. The main-recent bar is the recalibrated V_Full headline; the three other bars are the legacy E5 dynamic-regime diagnostic (declared in caption).
- **`paper_ready_figures/S06_01_F02B_Regime_Bias_Bar__E5_v01.png`** — UR bias (sim minus obs) by evaluation window. Main-recent bar uses the recalibrated V_Full bias -0.167 pp.

## Paper-ready table

- **`paper_ready_tables/S06_01_T01_Dynamic_Regime_Performance__E4_E5_v01.csv`** — Five-row summary covering pre-COVID, COVID crisis (Mar and Jan variants), post-COVID, and the aggregate full post-2018 window. Columns: window label, period, months, UR RMSE pp, UR MAE pp, UR bias pp, UR correlation, LFPR RMSE pp, EPOP RMSE pp, interpretation.

## Manuscript-facing wording (drop-in)

> The recalibrated heterogeneous ABM tracks observed U.S. unemployment over the post-COVID normalisation window 2022-01 to 2026-02 with a five-seed mean RMSE of 0.27 percentage points (cross-seed SD 0.02 pp), a near-zero bias of −0.04 pp, and a correlation of 0.79 with the BLS series. The same model, simulated forward from a fixed 2018-01 initialisation without any re-fitting, captures the direction of the 2020 COVID unemployment spike (UR correlation 0.75) but under-predicts its magnitude by approximately two percentage points on average over March 2020 through December 2021. We report both numbers and treat them as complementary — the post-COVID figure as the headline tracking accuracy, the crisis-window figure as the boundary of the model's quantitative reach.

## Caveats and wording rules

- The 0.273 pp headline is a **dynamic multi-step** simulation, not a rolling one-step forecast. The model is not re-fit anywhere inside the 2018-2026 evaluation window.
- Manuscript must avoid "dominates", "structurally identifies", "causal", and "completely tracks". Use "tracks", "competitively close to", "competitive", "accounting".
- Cross-seed SD (0.023 pp) is the relevant dispersion benchmark for any claim of "within seed SD" in §6.4.
- The covid_crisis_jan variant (2020-01..2021-12, including January and February 2020) is reported for sensitivity but is not the headline crisis window.

## Status

READY — paper-ready table and two figures are produced; numbers are traceable to `fix6.1/regime_metrics.json` and `fix6.2/reeval_metrics.json`.

## Audit mirror (full evidence for the appendix)

This section folder additionally contains an `audit_mirror/` subfolder with verbatim copies of every figure and table from the source experiments **E4 (Dynamic Evaluation)** and **E5 (Regime-Specific Evaluation)**: 4 figures + 3 tables. See `audit_mirror/_INDEX.md` for per-file provenance. The paper-ready files in `paper_ready_figures/` and `paper_ready_tables/` are the manuscript-facing condensed versions; the audit-mirror files are for appendix assembly and reviewer-side traceability.
