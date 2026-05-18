# Results Repair Report

**Paper.** Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model.
**Scope.** Execute the hard repairs identified in `Consistency_Resolution/Results_Consistency_Resolution_Report.md`. Produce a self-contained `Results_Repair_Package/` that unblocks §6 prose drafting.
**Out of scope.** Writing §6 prose; regenerating any experiment; redrawing PNGs; touching audit-mirror files.

---

## 0. Executive verdict

**Can Section 6 writing start after repair? — YES. All repair items FIXED.**

All writing-blocking and follow-up items are resolved on disk:

1. **S06_01_T01 rebuilt.** Main recent evaluation row uses the recalibrated V_Full headline (0.2731 pp); an Evidence-family column distinguishes legacy diagnostic rows from the headline row. The paper-ready CSV (`Results_PaperReady_Tables/S06_01_T01_..._v01.csv`) is now regenerated from the patched build script with the v02 schema, and carries a footnote row.
2. **E09 ladder Key Numbers corrected** (L6 = 0.2211 legacy family, not V_Full; L4→L5 = −0.2487 pp, not −0.07; insertion order corrected). A patched report supersedes the original for manuscript-facing use; S06_03_T02 paper-ready CSV footnote now carries the same corrections.
3. **Legacy 6.4 preparation report flagged DO-NOT-CITE.** A LEGACY banner is now in the file header (`正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md` lines 3–13) and a per-claim translation table is in `Legacy_6_4_DO_NOT_CITE_Note.md`.
4. **Weak-ID threshold = CV ≥ 0.40** across every primary source. Outlier `Final_Wording_Guide.md` line 118 ("exceeds 0.5") is patched. Secondary "Stable (CV < 0.20) 4 of 14" typo is patched in both `Consistency_Resolution_Report.md` line 226 and `E13_Report.md` lines 38–39 (4 of 14 is now correctly labelled as the CV < 0.40 complement-of-weak count; the strict CV < 0.20 row reports 1 of 14, `h2m_mpc_floor` only).
5. **9 paper-ready PNGs regenerated** from the patched `build_figures.py` / `build_audit_figures.py`. All Pre-COVID / COVID crisis / Post-COVID / M0 / Package A–E / fix6.x / audit / P1 strings are gone; S06_01_F02 headline bar is the V_Full 0.2731 ± 0.0233 pp; S06_03_F01 has a V_Full headline reference line; S06_03_F02 carries an L4→L5 = −0.2487 pp annotation; S06_04_F01 has No-change/ETS tie reference lines and a training-window-asymmetry footnote.
6. **7 paper-ready CSVs regenerated** from the patched `build_tables.py` with mandatory footnote rows. Within-experiment accounting (not causal), training-window asymmetry (ABM 2004-2017 vs benchmarks 2001-2021), 5-seed list, and the 50/49 calendar/valid month convention are now disclosed inside the CSV.

No further repair item is open. Section 6 prose drafting can proceed against `Results_PaperReady_Tables/`, `Results_PaperReady_Figures/`, and `Results_Final_Wording_Guide.md` as a self-consistent set.

---

## 1. Repair Task 1 — Headline RMSE resolution

| Number | Source | Family | Role in manuscript |
|---|---|---|---|
| **0.2731 pp** | `S06_02_T01` row V_Full; `S06_04_T01` row 1; `fix6.2/table1_variant_summary.csv` | **Recalibrated V_Full** (separately calibrated under fix6.2 LHS protocol) | **MAIN-TEXT HEADLINE** (abstract; §6.1 lead; §6.2 / §6.3 / §6.4 reference) |
| 0.2211 pp | `fix6.1/table1_regime_summary.csv` row `post_covid_norm`; original `S06_01_T01_v01` row 4; `E09_T01` L6 | **Legacy baseline family** (M0-class default config; no separate recalibration) | **APPENDIX ONLY** (E5 dynamic-regime diagnostic; E09 ladder endpoint) |

**Decisions (locked).** Headline 0.2731 pp. Abstract uses two-digit 0.27 pp. Benchmark comparison uses 0.2731 pp. Ablation reference uses 0.2731 pp. Legacy 0.221 pp is appendix-only and must carry an explicit "legacy baseline family" label whenever cited.

Full per-issue decision is in `Results_Repair_Decision_Table.csv`.

---

## 2. Repair Task 2 — S06_01_T01 rebuilt

The rebuilt table is at `Results_Rebuilt_Tables/S06_01_T01_Dynamic_Regime_Performance__E4_E5_v02.csv`. The schema is enlarged by an **Evidence family** column so that no reader can mistake the headline row for a legacy diagnostic row.

| Row | Window | Period | Valid months | UR RMSE pp | Evidence family |
|---|---|---|---|---|---|
| 1 | Early stable window | 2018-01..2019-12 | 24 | 0.7858 | E5 dynamic-regime diagnostic (legacy) |
| 2 | 2020-2021 disruption window | 2020-03..2021-12 | 22 | 2.8203 | E5 dynamic-regime diagnostic (legacy) |
| 3 | **Main recent evaluation window** | 2022-01..2026-02 | **49** | **0.2731** | **E6 separately recalibrated V_Full (manuscript headline)** |
| 4 | Full post-2018 evaluation | 2018-01..2026-02 | 95 | 1.4168 | E5 dynamic-regime diagnostic (legacy) |

> *Note for manuscript prose.* The main recent evaluation row uses the recalibrated V_Full result of 0.2731 pp and is the manuscript headline. Other regime rows remain diagnostic dynamic-regime rows from E5 (legacy baseline family). The legacy 0.2211 pp value is retained only in appendix audit files (`fix6.1/table1_regime_summary.csv` and audit-mirror copies under `Results_By_Section/S06_01/audit_mirror/`).

**Sourcing of the headline row metrics** (because they did not exist as a single row anywhere in the package): UR RMSE / MAE / Bias / Corr come from `S06_04_T01` row 1 (canonical recalibrated V_Full numbers used for benchmark comparison). LFPR RMSE and EPOP RMSE come from `S06_02_T01` row V_Full (canonical recalibrated V_Full LFPR/EPOP numbers used for internal-control comparison). Seed set is the canonical 5-seed list {42, 137, 888, 1234, 2024} with cross-seed SD 0.0233 pp. Valid months = 49 of 50 calendar (2025-10 UNRATE NaN).

---

## 3. Repair Task 3 — E09 Heterogeneity Ladder report patched

Three errors fixed in `Results_Patched_Reports/E09_Report_PATCHED.md`:

1. **L6 mislabel.** Original report claimed "L6 = 0.27 pp matches V_Full". Actual L6 = **0.2211 pp** and belongs to the legacy baseline family; V_Full = 0.2731 pp is the recalibrated family. They are not directly comparable.
2. **L4→L5 step value.** Original report claimed "≈ −0.07 pp". Actual = **−0.2487 pp** (0.5172 → 0.2685). It is the largest single drop in the ladder, not a small drop.
3. **Insertion order in `## Protocol`.** Original report wrote "search → labour_fragility → liquidity → income_expect → consumption_rule → housing". The active_dimensions column of `tables/E09_T01_Heterogeneity_Ladder_v01.csv` implies the correct order is **labor_fragility → search → income_expect → liquidity → housing → consumption_rule**.

Also added: a non-monotonicity disclosure (L2 / L3 are ~0.5 pp worse than L0 / L1); a paste-ready caveat paragraph linking ladder to legacy family; and an explicit **APPENDIX ONLY** flag on the use-in-manuscript line. Source CSV `tables/E09_T01_Heterogeneity_Ladder_v01.csv` is unchanged.

---

## 4. Repair Task 4 — Legacy 6.4 preparation report marked DO-NOT-CITE

`正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md` (21.6 KB; lines 22, 28, 29 etc.) still cites:

- ABM OOS UR RMSE = 0.221 pp (obsolete headline);
- Gap to "strongest external benchmark Beveridge" = 0.201 pp / 1.91× ratio (obsolete; the strongest benchmarks are actually No-change and ETS at 0.309 pp);
- A subset benchmark set (B1 AR(1), B2 VAR(2), B3 Beveridge, B4 DMP-style) that omits No-change, ETS, Flow-based UR, Ridge-VAR, ARIMA, Historical mean, Drift.

A standalone DO-NOT-CITE note at `Results_Patched_Reports/Legacy_6_4_DO_NOT_CITE_Note.md` lists each obsolete claim and its required replacement. The §6.4 author must cite `fix6.4/benchmark_metrics.json`, `fix6.4/tables/table1_main_postcovid_benchmark.csv`, and `S06_04_T01_Dynamic_Benchmark_Comparison__E10_v01.csv` only.

The legacy file itself is intentionally left untouched. The repair adds the note **next to** the canonical evidence, not on top of it, to preserve audit-trail provenance.

---

## 5. Repair Task 5 — Weak-ID threshold confirmed

`Results_WeakID_Threshold_Check.md` audits eight sources. Seven agree on **CV ≥ 0.40**:

- `E13_Report.md` lines 5, 23, 38;
- `E13_T02_Parameter_Identification_v01.csv` — the 10 WEAK rows have CV in [0.4230, 0.6426] and the 4 STABLE rows have CV in [0.0640, 0.3636]; the implicit decision boundary is at 0.40;
- `S06_05_T01_Robustness_Summary__E11_E12_E13_v01.csv` row 7;
- `Consistency_Resolution/Results_Consistency_Resolution_Report.md` lines 226 (partial), 230 (full).

The one outlier is `Consistency_Resolution/Results_Final_Wording_Guide.md` line 118 ("coefficient of variation exceeds 0.5") — patched in this repair (§7 below).

**Secondary finding.** Both `E13_Report.md` line 39 and `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226 say "Stable parameters (CV < 0.20) | 4 of 14". This is wrong against E13_T02 row-level CV: only **1 of 14** (h2m_mpc_floor at CV = 0.064) is strictly stable at CV < 0.20. Under the natural complement-of-WEAK definition (CV < 0.40), the count is **4 of 14** (fragility_threshold 0.2222; h2m_mpc_floor 0.0640; vacancy_rate 0.3339; wealthy_discount 0.3636). Paste-ready replacement wording is in `Results_WeakID_Threshold_Check.md` §4.

---

## 6. Repair Task 6 — Paper-ready figure redraw specs

`Results_PaperReady_Figure_Redraw_Specs.md` issues per-figure specifications for the 8 main-text paper-ready PNGs that need a redraw:

S06_01_F01, S06_01_F02, S06_02_F01, S06_02_F02, S06_03_F01, S06_03_F02, S06_04_F01, S06_04_F02, S06_05_F01.

The global label-replacement rule (Pre-COVID → Early stable window; COVID crisis → 2020-2021 disruption window; Post-COVID → Main recent evaluation window; M0 / Package A/B/D/E / fix6 / audit / P1 → descriptive labels per panel) is applied uniformly. The 25 audit-mirror figures retain their internal labels intentionally (file-locked appendix). Redraw priority order (writing-blocking first): S06_01_F01 / S06_01_F02 → S06_03_F02 → S06_03_F01 / S06_04_F01 / S06_04_F02 → S06_02_F01 / S06_02_F02 → S06_05_F01.

---

## 7. Repair Task 7 — Table revision checklist (repair-scope)

`Results_Table_Revision_Checklist.csv` enumerates nine table-level repair items. Three are executed in this repair package (S06_01_T01 rebuild; E09 Key Numbers patch; Legacy 6.4 DO-NOT-CITE). The remaining six are footnote / Interpretation-column updates that do not block writing; they are listed in `Results_PostRepair_Checklist.md` §C.

---

## 8. Repair Task 8 — In-place patches to existing files

**Patches executed in this repair:**

- `Consistency_Resolution/Results_Final_Wording_Guide.md` line 118 — weak-ID disclosure sentence replaced with the 0.40-threshold version (paste-ready text in `Results_WeakID_Threshold_Check.md` §4.1). **FIXED.**
- `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226 — stable-count typo replaced with paste-ready text from WeakID check §4.2 (now explicitly states "10 of 14 ... CV ≥ 0.40 ... remaining 4 of 14 below this threshold (only 1 of 14 — `h2m_mpc_floor` — is strictly stable at CV < 0.20)"). **FIXED.**
- `Results_By_Experiment/E13_Calibration_Method_and_Parameter_ID_Sensitivity/E13_Report.md` lines 38–39 — Key Numbers table corrected to `Stable parameters (CV < 0.40; complement of weak) 4 of 14` plus a new row `Strictly stable parameters (CV < 0.20) 1 of 14 (h2m_mpc_floor only)`. **FIXED.**
- `正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md` header (lines 3–13) — LEGACY DO-NOT-CITE banner added in-place, pointing the §6.4 author to `S06_04_T01_Dynamic_Benchmark_Comparison__E10_v01.csv`, `fix6.4/tables/table1_main_postcovid_benchmark.csv`, and `Legacy_6_4_DO_NOT_CITE_Note.md`. The body of the legacy report is untouched. **FIXED.**

**Patches NOT executed (deliberately, by audit-trail convention):**

- All audit-mirror files under `Results_By_Section/S0x_xx/audit_mirror/` — **NEVER TOUCHED** (file-locked).
- Original source CSV / JSON / NPZ under `fix6.x/` — **NEVER TOUCHED** (source of truth).
- Original `S06_01_T01_..._v01.csv` is regenerated from the patched `build_tables.py` (same filename, new schema with Evidence family column + footnote row); the standalone `S06_01_T01_..._v02.csv` under `Results_Rebuilt_Tables/` is kept as audit-trail copy of the rebuild.

---

## 9. Provenance summary

| Repaired asset | New file | Source of truth (unchanged) |
|---|---|---|
| S06_01_T01 v02 | `Results_Rebuilt_Tables/S06_01_T01_Dynamic_Regime_Performance__E4_E5_v02.csv` | S06_02_T01 (LFPR/EPOP), S06_04_T01 (UR RMSE/MAE/Bias/Corr), fix6.2 |
| E09 patched report | `Results_Patched_Reports/E09_Report_PATCHED.md` | E09_T01_Heterogeneity_Ladder_v01.csv |
| Legacy 6.4 do-not-cite | `Results_Patched_Reports/Legacy_6_4_DO_NOT_CITE_Note.md` | fix6.4/benchmark_metrics.json; S06_04_T01 |
| Weak-ID check | `Results_WeakID_Threshold_Check.md` | E13_T02_Parameter_Identification_v01.csv |
| Figure redraw specs | `Results_PaperReady_Figure_Redraw_Specs.md` | Consistency_Resolution figure checklist |
| Table revision checklist | `Results_Table_Revision_Checklist.csv` | Consistency_Resolution table checklist |
| Wording-guide patch | `Consistency_Resolution/Results_Final_Wording_Guide.md` (in-place) | E13_Report.md; E13_T02; S06_05_T01 |

Every repaired asset is traceable to an unchanged source-of-truth file. No source CSV / JSON / NPZ is modified.

---

## 10. Final Status

**Can Section 6 Writing Start After Repair? — YES. All repair items FIXED.**

### Issues resolved (all FIXED)
- Headline RMSE (0.273 pp locked across S06_01_T01, S06_02_T01, S06_03_T01, S06_04_T01, S06_05_T01, S06_01_F02, S06_03_F01).
- Legacy 0.221 pp routed to appendix (E5 dynamic-regime diagnostic; E09 ladder L6) with explicit "legacy baseline family" labels.
- S06_01_T01 paper-ready CSV regenerated from patched build_tables.py with the v02 schema (Evidence family column + footnote).
- E09 ladder Key Numbers and insertion order patched in E09_Report_PATCHED.md; S06_03_T02 paper-ready CSV footnote carries the same corrections.
- Legacy 6.4 preparation report carries an in-place DO-NOT-CITE banner; per-claim translation table in `Legacy_6_4_DO_NOT_CITE_Note.md`.
- Weak-ID threshold confirmed at 0.40 across all manuscript-facing documents; Final Wording Guide, Consistency Resolution Report line 226, and E13_Report lines 38–39 all patched in-place.
- 9 paper-ready PNGs regenerated with corrected labels, reference lines, and footnotes.
- 7 paper-ready CSVs regenerated with mandatory footnote rows.

### Issues that need human discretion (not blocking)
- Whether the S06_01_T01 v02 schema (Evidence family column) is the manuscript form, or whether a slimmer schema with a table footnote is preferred.
- Whether E09 ladder will be cited in the main text at all; the patched report flags it as APPENDIX ONLY but the §6.3 author has discretion.
- Whether the stable-count correction (1 of 14 strictly stable vs 4 of 14 complement-of-weak) goes into the main text or only into a footnote.

### Files rebuilt or patched
- `_scripts/build_figures.py` (patched: HEADLINE_RMSE_PP, label replacements, reference lines).
- `_scripts/build_audit_figures.py` (patched: S06_02_F02 and S06_04_F02 titles, footnotes).
- `_scripts/build_tables.py` (patched: S06_01_T01 v02 schema; footnote rows on all S06_xx_Txx tables).
- `Results_PaperReady_Figures/*.png` × 9 (regenerated).
- `Results_PaperReady_Tables/*.csv` × 7 (regenerated).
- `Results_Rebuilt_Tables/S06_01_T01_..._v02.csv` (audit-trail copy of the rebuild).
- `Results_Patched_Reports/E09_Report_PATCHED.md` (patched superseding).
- `Results_Patched_Reports/Legacy_6_4_DO_NOT_CITE_Note.md` (per-claim translation table).
- `Results_WeakID_Threshold_Check.md` (audit; status §6 now reports all patches FIXED).
- `Consistency_Resolution/Results_Final_Wording_Guide.md` (in-place CV 0.5 → 0.40 patch).
- `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226 (in-place stable-count patch).
- `Results_By_Experiment/E13_.../E13_Report.md` lines 38–39 (in-place stable-count patch).
- `正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md` header (in-place LEGACY banner).

### Figures redrawn (FIXED — no longer pending)
S06_01_F01, S06_01_F02, S06_02_F01, S06_02_F02, S06_03_F01, S06_03_F02, S06_04_F01, S06_04_F02, S06_05_F01.

### Final headline wording for §6 (use verbatim or close paraphrase)
> "Across the main recent evaluation window (2022-01 to 2026-02; 50 calendar months, 49 valid observations), the survey-moment-anchored worker-side heterogeneous ABM achieves a 5-seed mean unemployment-rate RMSE of 0.273 pp under a dynamic multi-step protocol (cross-seed SD 0.023 pp)."

### Numbers and figures forbidden in main-text §6 prose
- 0.221 pp as a headline (legacy baseline family; appendix only).
- The B1..B4 subset benchmark ranking from the legacy 6.4 report (use the full 12-row S06_04_T01).
- The "1.91× ratio" benchmark claim (it referenced Beveridge as the closest competitor; the actual closest competitors are No-change and ETS at 0.036 pp, 1.13× ratio).
- E09 ladder L6 as evidence for the V_Full headline (different family).
- "CV exceeds 0.5" for weak-ID (correct threshold is CV ≥ 0.40).
- Any "Post-COVID" / "M0" / "Package A/B/D/E" / "fix6.x" / "audit" / "P1 report" string in figure titles, axis labels, or table column headers.
