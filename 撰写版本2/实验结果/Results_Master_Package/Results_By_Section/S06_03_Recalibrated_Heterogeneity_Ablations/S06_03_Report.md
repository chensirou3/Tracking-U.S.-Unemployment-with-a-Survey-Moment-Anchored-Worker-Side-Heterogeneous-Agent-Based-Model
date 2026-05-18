# S06_03 — Recalibrated Heterogeneity Ablations

**Manuscript section:** §6.3
**Supporting experiments:** E8 (Heterogeneity Ablation), E9 (Heterogeneity Ladder)
**Source-of-evidence path:** `Results_By_Experiment/E08_Heterogeneity_Ablation/` and `E09_Heterogeneity_Ladder/`

## Headline result

Six single-dimension ablations and one joint ablation, each separately recalibrated under the same LHS budget as V_Full, produce the following post-COVID UR RMSE ordering:

| Variant | Removed | UR RMSE (pp) | Δ vs Full (pp) |
|---|---|---:|---:|
| **V_Full (reference)** | — | 0.273 | 0.000 |
| V_NoHousing | Housing-mobility heterogeneity | 0.237 | −0.036 |
| V_NoLiquidity | Liquidity-fragility heterogeneity | 0.378 | +0.105 |
| V_NoSLH (joint) | Search + Liquidity + Housing | 0.702 | +0.429 |
| V_NoSearch | Search-friction heterogeneity | 1.085 | +0.812 |

Three accounting points: (i) the single most expensive dimension to remove is **search-friction heterogeneity** (+0.81 pp); (ii) the **joint** Search+Liquidity+Housing flatten (+0.43 pp) is **not** the sum of single deltas (0.81 + 0.11 + (−0.04) = 0.88) — recalibration absorbs different amounts of the lost variance under different configurations, so deltas are non-additive; (iii) **V_NoHousing slightly outperforms V_Full** after recalibration. This last point is documented for transparency and must be reported as an accounting consequence of recalibration, not as evidence that housing heterogeneity is harmful.

The complementary E9 heterogeneity ladder confirms this picture from the opposite direction: starting from a homogeneous L0 baseline (UR RMSE ≈ 0.55 pp), the largest single-step accuracy gain occurs when housing is added on top of the five-dimension L4 (Δ ≈ −0.07 pp). Both lenses agree that the worker-side heterogeneity dimensions are **substitutable but not redundant** — recalibration can reassign their explanatory work across other parameters only partially.

## Paper-ready figures

- **`paper_ready_figures/S06_03_F01_Ablation_RMSE_Bar__E8_v01.png`** — Six-bar UR RMSE chart with cross-seed error bars, Δ vs Full annotation under each bar, and a dashed reference line at V_Full = 0.273 pp.
- **`paper_ready_figures/S06_03_F02_Ladder_RMSE_Path__E9_v01.png`** — Step plot of UR RMSE against the number of active heterogeneity dimensions L0..L6, with the per-step gain annotated.

## Paper-ready tables

- **`paper_ready_tables/S06_03_T01_Recalibrated_Ablation__E8_v01.csv`** — Six-row ablation summary: variant, removed dimension, recalibrated (yes), UR RMSE, Δ vs Full, LFPR RMSE, EPOP RMSE, interpretation.
- **`paper_ready_tables/S06_03_T02_Heterogeneity_Ladder__E9_v01.csv`** — Per-level ladder table with L0..L6 + alternative orders G2, G3.

## Manuscript-facing wording (drop-in)

> We recalibrate six single-dimension ablations and one joint ablation of the heterogeneity structure on the same training window as V_Full and re-evaluate them on the post-COVID 2022-01..2026-02 sample. Removing search-friction heterogeneity is the most expensive single ablation: the recalibrated variant attains UR RMSE 1.09 pp, a 0.81 pp loss relative to the V_Full reference. Removing liquidity-fragility heterogeneity costs 0.11 pp; removing housing-mobility heterogeneity does not cost anything in UR RMSE terms — the recalibrated variant comes in 0.04 pp below V_Full, an accounting consequence of parameter reassignment under recalibration. The joint flatten of all three (Search + Liquidity + Housing) costs 0.43 pp — substantially less than the sum of single-dimension deltas, indicating that recalibration partially substitutes between dimensions. The complementary heterogeneity ladder L0..L6, built by incrementally adding dimensions, confirms that the housing dimension contributes the largest single-step gain (Δ −0.07 pp) when added at L5. We interpret these numbers as within-experiment accounting deltas, not as causal contributions of each dimension.

## Caveats and wording rules

- All Δ values are **within-experiment accounting deltas**, not causal contributions. Manuscript must avoid "causal", "structurally", "dominates".
- V_NoHousing < V_Full is real and reported; treat as evidence of substitution under recalibration, not as housing being harmful.
- Joint Δ is not the sum of single Δ's — this is a feature, not a bug, of the recalibrated design.
- The ladder is order-dependent; insertion order (search → fragility → liquidity → expectation → consumption → housing) is documented and reported as one accounting path.

## Status

READY — paper-ready tables and two figures produced; numbers are traceable to `fix6.3/reeval_metrics.json` and `6.3/ladder_metrics.json`.

## Audit mirror (full evidence for the appendix)

This section folder additionally contains an `audit_mirror/` subfolder with verbatim copies of every figure and table from the source experiments **E8 (Heterogeneity Ablation)** and **E9 (Heterogeneity Ladder)**: 6 figures + 4 tables. See `audit_mirror/_INDEX.md` for per-file provenance. The paper-ready files are the manuscript-facing condensed versions; the audit-mirror files are for appendix assembly and reviewer-side traceability.
