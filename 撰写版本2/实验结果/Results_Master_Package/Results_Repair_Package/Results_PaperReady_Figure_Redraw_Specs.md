# Paper-Ready Figure Redraw Specifications

**Scope.** All paper-ready PNGs that require a redraw before any §6 main-text prose is finalised. Audit-mirror figures under `Results_By_Section/S06_0x/audit_mirror/figures/` are **not** in scope; they are appendix-only by construction and remain file-locked.

**No figure is redrawn in this repair package itself.** This file is a specification; redraw work is a separate step (likely by editing `build_figures.py` label dictionaries and re-running for each affected figure).

---

## 1. Global label-replacement rules

The following replacements apply to every main-text figure title, axis label, legend entry, and bar / tick annotation:

| Old label (any occurrence) | New label |
|---|---|
| Pre-COVID stable | Early stable window |
| COVID crisis | 2020-2021 disruption window |
| COVID crisis (Mar 2020+) | 2020-2021 disruption window |
| Post-COVID normalisation | Main recent evaluation window |
| Post-COVID norm. | Main recent evaluation window |
| Post-COVID | Main recent evaluation window |
| Full post-2018 | Full post-2018 evaluation |
| M0 / M0_Main | (remove; replace with "Full ABM" or "ABM" if a label is needed) |
| Package A | Training-window sensitivity |
| Package B | Forecast-horizon sensitivity |
| Package D | Agent-count sensitivity |
| Package E | Calibration-method / parameter-ID sensitivity |
| Sec 6.1 baseline / sec6.1 baseline | (remove) |
| fix6.1 / fix6.2 / fix6.4 | (never appears in main-text labels) |
| audit | (never appears in main-text labels) |
| P1 report | (never appears in main-text labels) |
| pre-recalibration vs recalibrated | default-config baseline vs separately calibrated |
| R / revised | (never appears in main-text labels) |
| old failed | (never appears in main-text labels) |

---

## 2. Per-figure redraw spec

| Figure ID | Source file | Problem | Required changes | Main-text / appendix |
|---|---|---|---|---|
| **S06_01_F01A / F01B** (split from F01) | `S06_01_F01A_Observed_vs_Simulated_UR_Full__E4_v01.png` + `S06_01_F01B_Observed_vs_Simulated_UR_MainEval__E4_v01.png` | DONE — original composite F01 had label crowding and unclear right-panel scope. | Composite F01 has been **split into two standalone figures**: F01A is the full post-2018 window with the three regimes shaded (early stable / 2020-2021 disruption / main recent evaluation), F01B is the main recent evaluation window (2022-01..2026-02) with the 0.273 pp headline call-out. Both trajectories come from `fix6.2/reeval_trajectories.npz V_Full_ur` (averaged over 5 calibration candidates). The legacy composite `S06_01_F01_Observed_vs_Simulated_UR__E4_v01.png` has been deleted from the paper-ready folder. | Main text — FIXED |
| **S06_01_F02A / F02B** (split from F02) | `S06_01_F02A_Regime_RMSE_Bar__E5_v01.png` + `S06_01_F02B_Regime_Bias_Bar__E5_v01.png` | DONE — original composite F02 had a misleading "(headline)" tag on a legacy-family bar. | Composite F02 has been **split into two standalone figures**: F02A (RMSE bar) and F02B (bias bar). The main-recent bar in both is rebuilt from the recalibrated V_Full (0.273 pp RMSE, -0.167 pp bias); the three other bars remain the legacy E5 dynamic-regime diagnostic and are declared as such in caption. X-axis labels updated to Early stable / 2020-2021 disruption / Main recent evaluation / Full post-2018. The legacy composite has been deleted from the paper-ready folder. | Main text — FIXED |
| **S06_02_F01** | `Results_PaperReady_Figures/S06_02_F01_Control_RMSE_Bar__E6_v01.png` | Y-axis title says "Post-COVID UR RMSE (pp)"; possible overlap between bar value labels and bar tops. | (1) Replace y-axis title with **"Main recent evaluation window UR RMSE (pp)"**. (2) Title: **"Main recent evaluation window UR RMSE by separately calibrated variant."** (3) Confirm variant order V_Full / V_LaborOnly / V_Homogeneous / V_Simplified (left-to-right). (4) Annotate V_Full bar with **"headline 0.273 pp"** label; ensure no overlap between value labels and bar tops. (5) Caption: 5-seed mean ± SD; cross-seed SD per variant from `S06_02_T01`. | Main text |
| **S06_02_F02** | `Results_PaperReady_Figures/S06_02_F02_Source_of_Advantage__E7_v01.png` | If figure is a waterfall, it implies a sequential causal path; bar/tick labels likely mention "Post-COVID"; legend uses "pre-recalibration vs recalibrated". | (1) Prefer a **component-contribution bar** (heterogeneity-associated 94.2% / mechanism-associated 5.8% / total accounting gain 0.2885 pp) over a waterfall. If waterfall is retained, add an arrow-style annotation explicitly stating "accounting partition, not sequential causal path". (2) Replace any "Post-COVID" with **"main recent evaluation window"**. (3) Replace "pre-recalibration vs recalibrated" with **"default-config baseline vs separately calibrated"**. (4) Caption must say: **"within-experiment accounting, not causal decomposition; shares are window-specific (main recent evaluation window only)"**. | Main text |
| **S06_03_F01** | `Results_PaperReady_Figures/S06_03_F01_Ablation_RMSE_Bar__E8_v01.png` | Y-axis title says "Post-COVID UR RMSE (pp)"; variant labels embed `V_` prefix; no headline-reference line. | (1) Replace y-axis title with **"Main recent evaluation window UR RMSE (pp)"**. (2) Title: **"Main recent evaluation window UR RMSE by re-calibrated ablation."** (3) Strip the `V_` prefix from variant labels: Full / NoSearch / NoLiquidity / NoHousing / NoConsumption / NoSLH / SearchOnly. (4) Add a horizontal dashed line at V_Full = 0.2731 pp annotated **"V_Full headline (0.273 pp)"**. (5) Annotate each bar with Δ vs Full (NoSearch +0.81, NoLiquidity +0.10, NoHousing −0.04, NoConsumption −0.02, NoSLH +0.43, SearchOnly +0.04 pp). (6) Caption: re-calibrated ablations are diagnostic, not structural mechanism identification; a negative Δ reflects parameter reassignment absorbing the removed dimension. | Main text |
| **S06_03_F02** | `Results_PaperReady_Figures/S06_03_F02_Ladder_RMSE_Path__E9_v01.png` | Step plot displays L0..L6 but the L4→L5 annotation likely shows ≈ −0.07 pp (wrong: actual is −0.2487 pp). Reference line claims to match V_Full but L6 = 0.221 pp belongs to a different family. | (1) Recompute step annotations from `tables/E09_T01_Heterogeneity_Ladder_v01.csv`. (2) L4→L5 step must read **"−0.2487 pp"**. (3) L0→L1 step **"−0.0024 pp"**. (4) Add a clearly-labelled secondary horizontal line at **"V_Full recalibrated headline 0.273 pp (different family)"** if a comparison line is desired; otherwise remove any reference line that conflates L6 with V_Full. (5) Caption must state: ladder is non-monotonic (L2, L3 ~0.5 pp worse than L0/L1); L6 = 0.221 pp belongs to the legacy baseline family and is not directly comparable to recalibrated V_Full 0.273 pp; insertion order is labor_fragility → search → income_expect → liquidity → housing → consumption_rule. | Appendix (caption-only update; if rebuilt as main-text, recompute annotations) |
| **S06_04_F01** | `Results_PaperReady_Figures/S06_04_F01_Benchmark_RMSE_Bar__E10_v01.png` | Title or y-axis likely references "Post-COVID"; if Drift bar is plotted at 6.92 pp it compresses the top models; ABM bar may not be annotated with the 0.273 headline. | (1) Replace any "Post-COVID" with **"main recent evaluation window"**. (2) Y-axis title: **"Main recent evaluation window UR RMSE (pp)"**. (3) Either remove the Drift bar (rank 12) entirely or use a broken y-axis / log scale so the top models remain visually distinguishable; prefer a top-8 view for the main text. (4) Annotate ABM_Full_recalibrated bar at **0.273 pp** and add a horizontal reference line at **0.309 pp** labelled **"No-change / ETS tie"**. (5) Caption: ABM is modestly better than No-change and ETS by 0.036 pp; margin is within cross-seed SD 0.023 pp. | Main text |
| **S06_04_F02** | `Results_PaperReady_Figures/S06_04_F02_Paths_Dynamic__E10_v01.png` | Likely uses "Post-COVID" in axis / legend; training-window asymmetry not annotated. | (1) Title: **"Main recent evaluation window dynamic forecast paths."** (2) Legend must include ABM (recalibrated V_Full), No-change, ETS, plus one structural benchmark (Beveridge OLS) and the observed UNRATE. (3) Sub-caption: ABM training 2004-01..2017-12 (168 m); benchmarks fit 2001-01..2021-12 (252 m, includes 2020-2021 disruption window that ABM did not see); both forecast 2022-01..2026-02 dynamically. (4) Do not visually emphasise weak benchmarks (AR/ARIMA/Historical mean/Drift); the main-text path plot is about the top 3-4 models only. | Main text |
| **S06_05_F01A..F01D** (split from F01) | `S06_05_F01A_Training_Window__E11_v01.png`, `S06_05_F01B_Horizon_Decay__E12_v01.png`, `S06_05_F01C_Agent_Count_Plateau__E12_v01.png`, `S06_05_F01D_Parameter_ID__E13_v01.png` | DONE — the 4-panel composite was dense and the parameter-ID panel risked being read as structural. | Composite F01 has been **split into four standalone figures**. Package A/B/D/E labels removed; "Full ABM" replaces M0_Main. F01D explicitly labels the weak-ID threshold line at CV = 0.40 and reports 10 of 14 parameters at or above threshold. The legacy composite has been deleted from the paper-ready folder. | Main text — FIXED |

---

## 3. Out-of-scope figures (no redraw)

- All 25 audit-mirror figures under `Results_By_Section/S06_0x/audit_mirror/figures/` are file-locked. They retain the internal labels intentionally and are referenced only as appendix evidence with a translation note in each `_INDEX.md`.
- E1–E3 figures (methods cross-references) are appendix-only and unaffected.

---

## 4. Redraw priority order

1. **S06_01_F01** + **S06_01_F02** — block §6.1 main-text writing until the headline-line vs legacy bar mismatch is resolved.
2. **S06_03_F02** — caption-only fix (cheap); resolves the E09 ladder mis-annotation noted in `E09_Report_PATCHED.md`.
3. **S06_03_F01** + **S06_04_F01** + **S06_04_F02** — visual-axis cleanup, no numerical changes required.
4. **S06_02_F01** + **S06_02_F02** — label cleanup + accounting-vs-causal disclosure annotation.
5. **S06_05_F01** — threshold and label cleanup; verify panel-D heatmap uses CV ≥ 0.40.

After each figure is regenerated, re-run `_scripts/mirror_audit_to_sections.py` so that section folders pick up the updated paper-ready PNG (audit-mirror is unaffected).
