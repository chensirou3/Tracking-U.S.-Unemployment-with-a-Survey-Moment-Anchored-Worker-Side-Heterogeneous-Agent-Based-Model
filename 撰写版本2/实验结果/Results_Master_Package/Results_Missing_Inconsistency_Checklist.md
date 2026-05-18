# Results Missing / Inconsistency Checklist

Each row is one issue. Severity legend:

- **BLOCKS RESULTS WRITING** — must be fixed before §6 can be drafted.
- **NEEDS CHECK BEFORE FINAL DRAFT** — main text can be drafted but the item must be reconciled before submission.
- **APPENDIX ONLY** — does not affect main text; resolve when assembling the appendix.
- **OPTIONAL IMPROVEMENT** — quality enhancement only.

| Item | Location | Problem | Severity | Needed action |
|---|---|---|---|---|
| 1 | E1 — Population marginals figure | ~~`E01_F01_Population_Marginals_v01.png` is a placeholder~~ **RESOLVED 2026-05-16**: six-panel marginals figure (age / education / employment / liquidity / housing / consumption) generated from `Phase2_Output/population_v1.npz` by `_scripts/build_audit_figures.py`. | APPENDIX ONLY (closed) | — |
| 2 | E2 — Stability summary table | `E02_T01_Stability_Summary_v01.csv` is currently inferred from `fix6.2/checkpoints/V_Full_progress.csv`; no dedicated stability-check run exists. | APPENDIX ONLY | Optional: re-run 5 seeds × 14 years with no calibration to obtain a clean stability table. Existing checkpoint evidence is sufficient for the appendix. |
| 3 | SCE question wording | `撰写版本2/SCE_Question_Wording.md` flagged MISSING per Phase 0 policy. | NEEDS CHECK BEFORE FINAL DRAFT | Paste verbatim FRBNY codebook text into the file before the Data section is finalised. |
| 4 | E10 — Training-window asymmetry | ABM trains on 2004-01..2017-12; benchmarks train on 2001-01..2022-01. Documented but not equalised. | NEEDS CHECK BEFORE FINAL DRAFT | Either run an ABM variant trained on 2001-2022 for symmetry, or write a transparent disclosure paragraph in §6.4. |
| 5 | E11/E12 use legacy M0 family | Robustness panels use the pre-fix6.x M0 family, not the recalibrated V_Full. | NEEDS CHECK BEFORE FINAL DRAFT | Report at ranking level only; manuscript wording in S06_05 already reflects this. Document explicitly in §6.5 prose. |
| 6 | RMSE numbers 0.221 vs 0.273 | The legacy headline (0.221 pp) and the recalibrated headline (0.273 pp) both circulate in older summaries. | NEEDS CHECK BEFORE FINAL DRAFT | Use **0.273 pp** as the manuscript's single headline. The 0.221 figure appears only in pre-recalibration appendix tables (E07_T02, E08_T02). |
| 7 | E13 best-test band 0.21–0.24 vs headline 0.273 | The E13 best-test UR RMSE band is centred on the legacy 0.22 pp value, below the recalibrated 0.27 pp headline. | NEEDS CHECK BEFORE FINAL DRAFT | Clarify in §6.5 that the E13 lens varies *calibration method* on the legacy population; ranking and CV are the transferable claims, not absolute level. |
| 8 | V_Simplified is not zero-mechanism | V_Simplified retains the matching mechanism; despite the name, it is not a fully de-mechanised baseline. | NEEDS CHECK BEFORE FINAL DRAFT | Wording in S06_02 explicit; ensure the Section 5 model description states this. |
| 9 | V_NoHousing < V_Full after recalibration | V_NoHousing UR RMSE (0.237 pp) is below V_Full (0.273 pp) — an accounting artefact of recalibration. | NEEDS CHECK BEFORE FINAL DRAFT | Report transparently; do **not** claim housing heterogeneity is harmful. Wording in S06_03 already correct. |
| 10 | 94% / 6% decomposition is accounting, not causal | Manuscript must avoid causal language. | BLOCKS RESULTS WRITING | Wording rule enforced in S06_02; cross-checked against `Results_Wording_Bank.md`. |
| 11 | Weak identification: 10 of 14 parameters | Must be reported as bands, not point estimates. | BLOCKS RESULTS WRITING | Wording rule enforced in S06_05; final values appear in `ABM_Calibration_Parameter_Bands.csv`. |
| 12 | Benchmark margin (0.036 pp) vs seed SD (0.023 pp) | Margin is the same order as seed SD; cannot claim "dominates". | BLOCKS RESULTS WRITING | Wording rule enforced in S06_04 (use "competitive", "modestly better"). |
| 13 | COVID-crisis window must be reported with headline | Crisis-window error 2.82 pp is the boundary of model reach. | BLOCKS RESULTS WRITING | Always report alongside the 0.273 pp headline in §6.1; do not isolate. |
| 14 | Internal-workflow language in audit folders | `E##_Report.md` files contain phrases like "pre-recalibration" and "old vs new" that must not surface in §6 prose. | NEEDS CHECK BEFORE FINAL DRAFT | Manuscript-facing language lives in `Results_By_Section/`; audit-folder language is internal and is not copied into §6. |
| 15 | Rolling-origin protocol reporting | Mentioned in E10_T02 but not in headline table. | APPENDIX ONLY | Add a one-paragraph footnote in §6.4 referring readers to the rolling-origin appendix table. |
| 16 | Citations and references | `References.bib` skeleton is generated but several entries are `[VERIFY]`-flagged (Poledna et al. volume/pages; Barnichon-Garda working-paper number). | NEEDS CHECK BEFORE FINAL DRAFT | Verify final bibliographic details before submission. |
| 17 | Eight remaining P2 items | Population marginals figure; rolling-protocol benchmark numbers; mobility/flexibility synthetic-vs-derived flags. | OPTIONAL IMPROVEMENT | Track separately in the P2 backlog; not required for §6 main text. |
| 18 | Wording rules audit (per §0 of the prompt) | Files in this package must not use "dominates", "causal", "structurally identified", "completely untouched", "survey-sampled", or over-emphasise COVID. | BLOCKS RESULTS WRITING | Final wording pass against `Results_Wording_Bank.md` before §6 is sent for review. |
| 19 | Units consistency (pp vs percent vs decimal) | UR/LFPR/EPOP errors **must** be reported in **pp**; correlations as **decimal**; shares with explicit decimal/percent label. | BLOCKS RESULTS WRITING | Already enforced in all `S06_*_T01_*.csv`. Spot-check during §6 drafting. |
| 20 | E2 (Baseline Stability) and parts of E3 are READY WITH CAVEAT, not READY | Recorded in each folder's `status.md`. | APPENDIX ONLY | If the user wishes to upgrade to READY, run the stability check explicitly. Not blocking for main text. |
| 21 | Audit-layer figures: E02/E03/E07/E09 had only one figure each (or none) | Each experiment's audit folder previously contained at most one figure, leaving the evidence chain visually sparse. | APPENDIX ONLY (closed) | **RESOLVED 2026-05-16**: `_scripts/build_audit_figures.py` generated E01_F01, E02_F02, E03_F01, E03_F02, E03_F03, E07_F02, E09_F02; registered in `Results_Figure_Registry.csv`. |
| 22 | Paper-ready layer: S06_02 and S06_04 had only one figure each | Section folders had a single figure even though the underlying experiment supports a second view (decomposition bar, dynamic-path overlay). | APPENDIX ONLY (closed) | **RESOLVED 2026-05-16**: `S06_02_F02_Source_of_Advantage__E7_v01.png` and `S06_04_F02_Paths_Dynamic__E10_v01.png` generated, mirrored to `Results_PaperReady_Figures/`, and added to the registry. Reports updated. |
| 23 | S06_01_F01 figure body invisible (no lines drawn) | `build_figures.py` treated `regime_series.npz` series as already in pp, but they are stored as decimals (0.04 = 4%). Combined with `set_ylim(2, 16)`, this pushed every data line below the visible y-axis, leaving only the regime-shading background. The user reported the figure looked like "axes/labels without content". | APPENDIX ONLY (closed) | **RESOLVED 2026-05-17**: `fig_s06_01_f01()` patched to multiply `target_ur` and `ur` by 100.0 before plotting; both mirror copies regenerated. Post-fix pixel variance 1517 → 1977 and non-white fraction 6.4% → 7.7%. |
| 24 | Section layer figure/table count below experiment layer | Manuscript layer originally contained only condensed paper-ready files (9 figs / 7 tabs), while audit layer had 31 figs / 29 tabs. Per user request 2026-05-17, the design is changed so each §6.x folder is **self-contained**: paper-ready files (unchanged) plus a verbatim `audit_mirror/figures/` and `audit_mirror/tables/` copy of every source-experiment artefact. The user will assemble an appendix from the mirror layer. | APPENDIX ONLY (closed) | **RESOLVED 2026-05-17**: `_scripts/mirror_audit_to_sections.py` added; produces 25 figures + 21 tables of mirror content across S06_01..S06_05. Each section's `_INDEX.md` documents per-file provenance. `audit_package.py` updated to skip `audit_mirror/` to avoid double-counting. Reports updated. |

## Structural CSV blanks — by design, not missing data

The audit script flags ten CSVs as containing empty cells. All ten are **intentional** — the empty cells communicate structural inapplicability rather than missing values. They are listed here for transparency.

| CSV | Empty-cell pattern | Why it is empty by design |
|---|---|---|
| `E02_T02_Seed_Dispersion_v01.csv` | `window` column empty on the MEAN / SD / CV summary rows | Aggregate statistics span all windows; no single `window` value applies. |
| `E03_T02_Parameter_Bands_v01.csv` | `band` columns empty for INACTIVE parameters of V_Simplified / V_LaborOnly | Parameter is not active in that variant; an empty band is the canonical encoding (P1 spec). |
| `E04_T01_Dynamic_Evaluation_Metrics_v01.csv` | `source` only filled on the first row of each block | Block-header convention; downstream rows inherit the source. Cosmetic only. |
| `E08_T02_Old_vs_New_Delta_v01.csv` | Legacy columns empty for V_NoSLH and V_SearchOnly | These two variants are new in fix6.x and have no legacy comparator; cells carry the literal `N/A (new variant)` label. |
| `E09_T01_Heterogeneity_Ladder_v01.csv` | `active_dims` empty for L0; `note` only filled on the reference row | L0 has zero active heterogeneity dimensions; non-reference rows share the same note. |
| `E12_T01_Forecast_Horizon_Sensitivity_v01.csv` | `h=1` cells empty for B3_Beveridge | The Beveridge OLS benchmark requires ≥1 lag; h=1 is structurally undefined. |
| `E12_T02_Agent_Count_Sensitivity_v01.csv` | Same Beveridge structural-blank pattern | Same reason as T01. |
| `E13_T02_Parameter_Identification_v01.csv` | Separator blank row + `[performance_lens]` summary block with single populated column | Layout convention: separator + summary-block-with-tag. |
| `S06_03_T02_Heterogeneity_Ladder__E9_v01.csv` and its mirror in `Results_PaperReady_Tables/` | Same as `E09_T01` | Direct copy of the audit-layer table. |

**Conclusion:** the ten CSV "issues" are **not** data-loss bugs. The audit script reports them so the structure can be sanity-checked; readers should interpret the empty cells as "structurally inapplicable" rather than "missing".

## Suspect PNGs — false positives

The audit script flags PNGs whose pixel variance falls below an empirical 1500-threshold ("BLANK? MAYBE"). All thirteen current flags are **line-plot or trajectory figures on large canvases**, where a few thin lines on white background mechanically produce low variance even when the figure is fully populated. Each flagged figure has been opened and visually confirmed non-blank. The audit threshold is conservative and is intended as a screen, not a verdict.

## Summary

- **BLOCKS RESULTS WRITING:** 6 items (#10, #11, #12, #13, #18, #19). All are wording / reporting policy items; the underlying evidence is already in place. The block is on **how** the numbers are described, not on **whether** the numbers exist.
- **NEEDS CHECK BEFORE FINAL DRAFT:** 8 items (#3, #4, #5, #6, #7, #8, #9, #14, #16). Mostly disclosure-paragraph or wording-consistency tasks; no new computation required for the main text.
- **APPENDIX ONLY:** 6 items (#2, #15, #17, #20); items #1, #21, #22 closed on 2026-05-16.
- **OPTIONAL IMPROVEMENT:** included in #17.

§6 of the manuscript can be drafted now subject to the six BLOCKS items being honoured as wording rules.
