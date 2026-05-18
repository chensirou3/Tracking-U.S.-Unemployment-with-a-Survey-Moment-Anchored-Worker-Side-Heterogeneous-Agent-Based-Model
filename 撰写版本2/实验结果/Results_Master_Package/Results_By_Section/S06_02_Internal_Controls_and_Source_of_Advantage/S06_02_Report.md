# S06_02 — Internal Controls and Source of Advantage

**Manuscript section:** §6.2
**Supporting experiments:** E6 (Internal Control Comparison), E7 (Source-of-Advantage Decomposition)
**Source-of-evidence path:** `Results_By_Experiment/E06_Internal_Control_Comparison/` and `E07_Source_of_Advantage_Decomposition/`

## Headline result

When V_Full is held against three separately-calibrated internal controls on the same post-COVID window, the four-row ladder is:

| Variant | Active heterogeneity | Active mechanisms | UR RMSE (pp) |
|---|---|---:|---:|
| V_Full | All 6 dimensions | All 14 mechanisms | **0.273** |
| V_Homogeneous | None (flattened) | All 14 mechanisms | 0.545 |
| V_LaborOnly | 4 labour-side dimensions | 11 of 14 (3 household-side OFF) | 0.363 |
| V_Simplified | None (flattened) | 1 of 14 (matching only) | 0.562 |

Total RMSE gain of V_Full over V_Simplified is **0.289 pp**. Decomposed within the experiment:
- Heterogeneity-associated gain (RMSE V_Homogeneous − RMSE V_Full) = **0.272 pp** ≈ **94.2%** of total
- Mechanism-associated gain (RMSE V_Simplified − RMSE V_Homogeneous) = 0.017 pp ≈ 5.8% of total
- Household-block gain (RMSE V_LaborOnly − RMSE V_Full) = 0.090 pp

Read literally: under the same LHS calibration budget and the same loss function, removing all six worker-side heterogeneity dimensions causes a 0.27 pp RMSE loss that recalibration cannot recover; switching the mechanism set from fourteen down to one causes an additional 0.02 pp loss. The household block (consumption / liquidity / housing) contributes the smaller but visible 0.09 pp share.

## Paper-ready figures

- **`paper_ready_figures/S06_02_F01_Control_RMSE_Bar__E6_v01.png`** — Single-panel bar chart of UR RMSE for the four variants with 5-seed error bars and the total gain annotation.
- **`paper_ready_figures/S06_02_F02_Source_of_Advantage__E7_v01.png`** — Three-bar accounting decomposition of the V_Full advantage. Bars: heterogeneity gain (V_Homogeneous − V_Full), mechanism gain (V_Simplified − V_Homogeneous), and household-block gain (V_LaborOnly − V_Full); each bar annotated with magnitude in pp and percentage share of the total gain; horizontal dashed reference line at the total gain.

## Paper-ready tables

- **`paper_ready_tables/S06_02_T01_Internal_Control_Comparison__E6_v01.csv`** — Four-row summary: variant, active heterogeneity, active mechanisms, separately calibrated (yes/yes/yes/yes), UR RMSE pp, UR RMSE seed SD, LFPR RMSE pp, EPOP RMSE pp, train loss.
- **`paper_ready_tables/S06_02_T02_Source_of_Advantage__E7_v01.csv`** — Four-row accounting decomposition: component, definition (RMSE arithmetic), gain in pp, share in %, interpretation.

## Manuscript-facing wording (drop-in)

> Three internal controls, each separately calibrated under the same LHS budget and loss function, identify where the V_Full advantage on the post-COVID window comes from. A homogeneous-population variant with all fourteen mechanisms active attains UR RMSE 0.55 pp; a labour-side-only heterogeneous variant attains 0.36 pp; and a fully flattened variant with a single mechanism attains 0.56 pp. The total RMSE gain of V_Full over the flattened reference is 0.29 pp; within this within-experiment accounting decomposition, 94 percent is associated with restoring the worker-side heterogeneity dimensions, and 6 percent with restoring the additional mechanisms. We refer to this throughout as a within-experiment accounting decomposition rather than a causal partition: each variant is recalibrated, so part of the difference is absorbed by parameter substitution and the shares are not identified separately from the calibration protocol.

## Caveats and wording rules

- The 94/6 split is an **additive accounting identity**, not a causal partition. Manuscript must say "within-experiment accounting", "accounting decomposition", or "decomposition of the RMSE difference"; never "causal decomposition".
- V_Simplified retains the matching_competition mechanism — it is not a zero-mechanism baseline.
- Each variant is independently recalibrated; the difference between V_Full and V_Simplified is what recalibration *cannot* close.
- The 5.8% mechanism share is small because V_Homogeneous already has all 14 mechanisms ON; this share captures only the marginal contribution under a flat population.

## Status

READY — paper-ready tables (T01 + T02) and two figures (F01 control RMSE bar, F02 source-of-advantage decomposition) are produced; numbers are traceable to `fix6.2/reeval_metrics.json` and `fix6.2/table4_source_of_advantage.csv`.

## Audit mirror (full evidence for the appendix)

This section folder additionally contains an `audit_mirror/` subfolder with verbatim copies of every figure and table from the source experiments **E6 (Internal Control Comparison)** and **E7 (Source-of-Advantage Decomposition)**: 6 figures + 5 tables. See `audit_mirror/_INDEX.md` for per-file provenance. The paper-ready files are the manuscript-facing condensed versions; the audit-mirror files are for appendix assembly and reviewer-side traceability.
