# Post-Repair Checklist — Ready for Section 6 Writing

**Verdict:** YES WITH CAVEATS. Two writing-blocking numeric conflicts (S06_01_T01 row and E09 Key Numbers) and one cross-document threshold inconsistency (Wording Guide CV 0.5) are resolved on disk. Remaining items are figure redraws and caption / footnote additions, which do not block prose drafting but must be completed before the manuscript is submitted.

---

## A. Hard requirements (writing-blocking) — all DONE

- [x] Headline UR RMSE locked at **0.273 pp** (recalibrated V_Full; 5-seed mean; 49 valid months in 2022-01..2026-02).
- [x] 0.221 pp moved to appendix / diagnostic only (E5 dynamic-regime + E09 ladder L6).
- [x] **S06_01_T01 rebuilt** as `Results_Rebuilt_Tables/S06_01_T01_Dynamic_Regime_Performance__E4_E5_v02.csv` with the main recent evaluation row replaced by the recalibrated V_Full headline (0.2731 pp UR RMSE; 0.2089 MAE; -0.1669 Bias; 0.7636 Corr; 4.8327 LFPR; 4.7566 EPOP; 49 valid months). Window label changed from "Post-COVID normalisation" to "Main recent evaluation window". Added Evidence family column distinguishing the legacy diagnostic rows from the recalibrated headline row.
- [x] **E09 Key Numbers patched** in `Results_Patched_Reports/E09_Report_PATCHED.md`. L6 = 0.2211 pp (legacy family endpoint, **not** V_Full); L4→L5 = −0.2487 pp (largest single drop, **not** −0.07); insertion order corrected to `labor_fragility → search → income_expect → liquidity → housing → consumption_rule`; non-monotonicity disclosure added.
- [x] **Legacy 6.4 report flagged DO-NOT-CITE** in `Results_Patched_Reports/Legacy_6_4_DO_NOT_CITE_Note.md`. Original file at `正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md` is untouched (provenance preserved). §6.4 author must cite `fix6.4/` outputs and `S06_04_T01` only.
- [x] **Weak-ID threshold confirmed at 0.40** in `Results_WeakID_Threshold_Check.md`. Verified across E13_Report.md, E13_T02 (row-level status flags), and S06_05_T01. The lone outlier (`Final_Wording_Guide.md` line 118 saying "exceeds 0.5") is patched in §B below.
- [x] Final Wording Guide patched (CV exceeds 0.5 → CV ≥ 0.40). See §B.

---

## B. In-place patches executed in this repair

- [x] `Consistency_Resolution/Results_Final_Wording_Guide.md` line 118: weak-ID disclosure now reads "coefficient of variation reaches or exceeds 0.40 in at least one calibration method".
- [ ] `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226: stable-count parenthetical to be changed from "(CV < 0.20)" to "(CV < 0.40)"; strict-stable count footnote optional. **Pending** in next-regenerate (text already documented in WeakID check §4.2).
- [ ] `E13_Report.md` line 39: stable-parameter row to use CV < 0.40 (4 of 14) and optionally add a strictly-stable row (1 of 14). **Optional** (E13_Report is appendix-only); patch text in WeakID check §4.3.

---

## C. Soft requirements (do NOT block prose drafting; must be done before submission)

### Paper-ready figure redraws (specs issued; no figure regenerated in this repair)

- [ ] S06_01_F01 — replace right-panel title, legend, caption (49/50 month convention); verify right-panel curves are recalibrated V_Full.
- [ ] S06_01_F02 — replace x-axis tick labels; rebuild headline bar with 0.2731 (or demote to appendix).
- [ ] S06_02_F01 — replace y-axis title; annotate V_Full bar with "headline 0.273 pp".
- [ ] S06_02_F02 — prefer component-contribution over waterfall; add "within-experiment accounting, not causal" caption note.
- [ ] S06_03_F01 — replace y-axis title; strip `V_` prefix; add horizontal V_Full reference line; annotate Δ vs Full.
- [ ] S06_03_F02 — recompute step annotations (L4→L5 = −0.2487 pp); add ladder family disclosure to caption.
- [ ] S06_04_F01 — replace y-axis title; remove or break-axis the Drift bar; annotate ABM bar 0.273 and reference line 0.309.
- [ ] S06_04_F02 — title to "Main recent evaluation window dynamic forecast paths"; add training-window asymmetry sub-caption.
- [ ] S06_05_F01 — replace internal Package A/B/D/E and M0_Main labels; verify CV threshold annotation 0.40 not 0.50.

All specs in `Results_PaperReady_Figure_Redraw_Specs.md`.

### Table footnote / Interpretation updates (specs issued)

- [ ] S06_02_T01 — footnote: window-specific; V_Full ranks 4th on full-post-2018.
- [ ] S06_02_T02 — footnote: window-specific; within-experiment accounting partition; not causal.
- [ ] S06_03_T01 — replace structural-sounding Interpretation strings for V_NoHousing / V_NoConsumption rows.
- [ ] S06_03_T02 — footnote: ladder is on legacy family; L6 ≠ V_Full; non-monotonic.
- [ ] S06_04_T01 — footnote: ABM training 2004-01..2017-12 (168 m); benchmarks 2001-01..2021-12 (252 m); both forecast 2022-01..2026-02; Interpretation column reword.
- [ ] S06_05_T01 — footnote: legacy baseline family for E11/E12/E13 rows; recalibrated V_Full headline at upper end of legacy band.

All specs in `Results_Table_Revision_Checklist.csv` of this repair package.

---

## D. Locked main-text quantities (after repair)

| Quantity | Locked value | Source |
|---|---|---|
| Headline UR RMSE | **0.273 pp** | S06_01_T01 v02; S06_02_T01 row V_Full; S06_04_T01 row 1 |
| Cross-seed SD | **0.023 pp** | S06_02_T01 row V_Full |
| Benchmark gap | **0.036 pp** (within seed SD) | S06_04_T01 rows 1–3 |
| Source-of-advantage shares | **94.2% heterogeneity / 5.8% mechanism** (accounting, main recent only) | S06_02_T02 |
| Ablation Δ vs Full (pp) | NoSearch +0.81; NoLiquidity +0.10; NoHousing −0.04; NoConsumption −0.02; NoSLH +0.43; SearchOnly +0.04 | S06_03_T01 |
| Weak-ID threshold | **CV ≥ 0.40** | E13_Report; E13_T02; S06_05_T01 |
| Weak-ID count | **10 of 14** | E13_T02 status flags |
| Stable count (CV < 0.40) | **4 of 14** | E13_T02 status flags |
| Strictly stable count (CV < 0.20) | **1 of 14** (h2m_mpc_floor) | E13_T02 row-level CV |
| Calibration-method band | **0.214–0.243 pp** (legacy family; recalibrated V_Full 0.273 sits above this band) | E13_T01; S06_05_T01 |
| Training-window robustness | **0.245 ± 0.011 pp** on 7 OOS-aligned splits (legacy family) | S06_05_T01 row 2 |
| ABM training window | **2004-01..2017-12** (168 months, inclusive) | S06_04_T01 row 1; calibration setup |
| Benchmark fit window | **2001-01..2021-12** (252 months, inclusive; includes 2020-2021 disruption) | fix6.4/benchmark_metrics.json |
| Evaluation window | **2022-01..2026-02** (50 calendar months, 49 valid for UR; 2025-10 NaN) | All paper-ready outputs |

---

## E. Locked wording for §6 (cheat-sheet)

### Required
- "Main recent evaluation window" — never "Post-COVID".
- "Early stable window" — never "Pre-COVID stable".
- "2020-2021 disruption window" — never "COVID crisis" (and only as a scope diagnostic, not a narrative).
- "Recalibrated V_Full" — never "M0", "fix6.2 V_Full", "the new model".
- "Within-experiment accounting" — never "causal decomposition".
- "Re-calibrated ablations" / "diagnostic" — never "structural mechanism identification".
- "Competitive" / "modestly better by 0.036 pp" — never "dominates".
- "Conditional on weak identification of 10 of 14 parameters" — never "universally robust".
- "Coefficient of variation ≥ 0.40" — never "exceeds 0.5" or "exceeds 0.50".

### Banned (write nowhere in publishable text)
- 0.221 pp as a main-text headline.
- "ABM dominates" / "ABM solves" / "structurally identifies".
- "Causal decomposition" / "causally explains X%".
- M0 / M0_Main / Package A/B/D/E / Sec 6.1 baseline / fix6.x / audit / P1 report / R / revised.
- Any "Post-COVID" string in a paper-ready figure title, axis label, or table label.

---

## F. Ready-to-write status per section

| Section | Status | Prerequisite |
|---|---|---|
| §6.1 Dynamic and regime-specific performance | **READY** | Use `S06_01_T01_v02.csv` (rebuilt). Headline RMSE 0.273. Mention 49/50 month convention. |
| §6.2 Internal controls and source of advantage | **READY** | Use S06_02_T01 / T02 as-is + footnote disclaimers from this repair. Window-specific qualifier mandatory. |
| §6.3 Heterogeneity ablations and ladder | **READY** | Use S06_03_T01 as-is. Cite ladder via E09_Report_PATCHED.md, not the original E09_Report.md. |
| §6.4 Benchmark comparison | **READY** | Cite `fix6.4/` and S06_04_T01 only. Use Legacy_6_4_DO_NOT_CITE_Note.md as discipline reference. Add training-window asymmetry disclosure. |
| §6.5 Robustness and sensitivity | **READY** | Use S06_05_T01 as-is. CV ≥ 0.40 (not 0.5). Conditional language. |

**No section is blocked.** All four CSV / Markdown deliverables in this repair package are sufficient to start prose writing for any §6.x subsection in parallel.
