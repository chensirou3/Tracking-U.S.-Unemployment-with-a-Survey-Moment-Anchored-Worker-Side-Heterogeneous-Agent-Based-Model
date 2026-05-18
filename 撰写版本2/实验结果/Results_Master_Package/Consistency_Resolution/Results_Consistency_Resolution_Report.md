# Results Consistency Resolution Report

**Project:** Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model
**Scope:** Section 6 (Results) + Appendix evidence package.
**Generated:** 2026-05-17
**Purpose:** Lock the final manuscript-facing wording, identify every inconsistency that must be resolved before §6 drafting begins, and decide for every asset whether it belongs in main text or appendix.

---

## 0. Executive verdict

**Can Section 6 writing start? — YES WITH CAVEATS.**

Three numeric inconsistencies must be reconciled **before** main-text prose is finalised:
1. `S06_01_T01` paper-ready table reports the post-COVID row as 0.2211 pp (legacy M0 family). The headline and every downstream §6.2/§6.3/§6.4 reference uses 0.273 pp (recalibrated V_Full family). The table must be rewritten or annotated.
2. `E09_Report.md` "Key Numbers" section claims L6 matches V_Full and that the L4→L5 step is ≈ −0.07 pp. Both are wrong against the actual ladder CSV.
3. Legacy report `正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md` still cites "ABM 0.221 pp" as the comparison reference. It must be marked LEGACY-DO-NOT-CITE in §6.4 prose.

All other issues are paper-ready figure redraws (regime labels) and wording-bank reinforcements that do not block writing.

**Final headline RMSE for the manuscript:** 0.273 pp (5-seed mean, recalibrated V_Full, dynamic protocol, 49 valid months in the 2022-01..2026-02 window).
**Final benchmark claim:** ABM is competitive at rank 1, modestly better than the two best benchmarks (No-change, ETS) by 0.036 pp. Margin is within seed SD (0.023 pp). Use "competitive" or "modestly better"; do not use "dominates".
**Final robustness claim:** Supports the tracking result under expanding-window, horizon, agent-count, and calibration-method checks; conditional on weak identification of 10 of 14 parameters and on the fact that two rolling-window splits perform poorly. Do not write "universally robust" or "structurally identified".

---

## 1. Number-tracking ground truth

| Number | Source | Variant | Window | Seeds | Valid months | Role in manuscript |
|---|---|---|---|---|---:|---|
| **0.2211 pp** | `正式撰写/fix6.1/tables/table1_regime_summary.csv` row `post_covid_norm`; `regime_series.npz` | Legacy M0 baseline (NOT separately recalibrated) | 2022-01..2026-02 | 5 ({42,137,2024,888,1234}) | 49 | **APPENDIX ONLY** — baseline dynamic-regime diagnostic |
| **0.2731 pp** | `正式撰写/fix6.2/tables/table1_variant_summary.csv` row `V_Full`; `reeval_trajectories.npz` | V_Full separately recalibrated under fix6.2 LHS protocol | 2022-01..2026-02 | 5 (same set) | 49 | **MAIN-TEXT HEADLINE** — used by §6.2 controls, §6.3 ablations, §6.4 benchmarks |
| 0.214 pp | Legacy 6.2 default-config baseline | V_Full at default-config params (NOT separately calibrated) | 2022-01..2026-02 | 5 | 49 | DO NOT CITE — appears only in old-vs-new comparison tables (E07 T02, E08 T02) |
| 0.245 ± 0.011 pp | `正式撰写/6.5/robustness_metrics.json` packageA block | Legacy M0 family on Package A 10-split protocol | 7 OOS-aligned splits | 60 LHS × 1 seed per split | varies | APPENDIX — training-window sensitivity band |

**Resolution for Issue 1:** Use **0.273 pp** as the headline. 0.221 pp is a baseline diagnostic from a pre-recalibration family; it should not appear in §6.1 prose. If retained anywhere in §6.1, it must be labelled "legacy M0 baseline (not separately recalibrated)" and pushed to appendix.

---

## 2. Critical inconsistencies (must fix before §6 prose is final)

### 2.1 `S06_01_T01_Dynamic_Regime_Performance__E4_E5_v01.csv` — post-COVID row

**Current state.** Row 5 reads `Post-COVID normalisation, 2022-01..2026-02, 49, 0.2211, 0.1629, -0.0425, 0.7896, 2.2743, 2.2141, ...`. This row was generated from `fix6.1/regime_metrics.json` (legacy M0 baseline), not from `fix6.2/reeval_metrics.json` (recalibrated V_Full).

**Why it conflicts.** Every downstream paper-ready asset (`S06_02_T01`, `S06_03_T01`, `S06_04_T01`, the wording bank §1) reports the post-COVID headline as 0.27 pp. The §6.1 table currently shows 0.22 pp on the same row label. A reader comparing §6.1 and §6.2 will see two different "headline" RMSEs for the same window.

**Resolution options.**
- **(A) Preferred.** Rebuild `S06_01_T01` so the post-COVID row uses recalibrated V_Full (0.2731 pp, seed SD 0.0233 pp, bias −0.1669 pp, corr 0.7636). Keep the three other window rows from fix6.1 since those windows are not redone in fix6.2. Add a footnote: "Pre-COVID stable, 2020–2021 disruption, and full post-2018 rows use the dynamic-regime evaluation from E5 (legacy M0). The main recent evaluation row uses the separately recalibrated V_Full (E6) and is the headline figure throughout §6."
- **(B) Alternative.** Add a second row labelled "Main recent evaluation window (recalibrated V_Full)" with the 0.2731 numbers and leave the 0.2211 row as "Main recent evaluation window (legacy M0 baseline, appendix-only)".

**Decision:** A. Rebuild the table.

### 2.2 `E09_Report.md` Key Numbers

**Current state.** "L6 UR RMSE (all 6 dims) | 0.27 pp (matches V_Full)". L6 in `E09_T01_Heterogeneity_Ladder_v01.csv` is **0.2211 pp**, not 0.27. V_Full in fix6.2 is 0.2731 pp. The L6 reference of the ladder uses the **legacy M0 baseline family**, not the recalibrated V_Full.

**Current state (line 2).** "Largest single drop (L4→L5, adding housing) | ≈ −0.07 pp". Real values: L4 = 0.5172, L5 = 0.2685. Drop = **−0.2487 pp**, not −0.07 pp.

**Why it matters.** §6.3 of the manuscript references this ladder. Quoting "−0.07 pp" understates the magnitude by a factor of 3.5 and undermines the very claim the ladder is meant to support.

**Resolution.** Patch `E09_Report.md` Key Numbers to:
| Quantity | Value |
|---|---|
| L0 UR RMSE (no heterogeneity) | 0.5527 pp (legacy M0 baseline family) |
| L6 UR RMSE (all 6 dims) | 0.2211 pp (legacy M0 baseline family; comparable to E5 0.2211 pp but **not** to the recalibrated V_Full 0.2731 pp) |
| Largest single drop, L4→L5 (adding housing) | −0.2487 pp |
| Smallest gain, L0→L1 (adding labor_fragility) | −0.0024 pp (within seed SD) |
| Ladder is **not monotonic**: L2 (1.0545) and L3 (1.0579) are worse than L0/L1 | — |

Add a caveat: "The ladder is computed on the legacy M0 baseline family, not on the recalibrated V_Full of fix6.2. L6 (0.2211 pp) does not equal V_Full (0.2731 pp); the two are different calibration protocols. The ladder is therefore a within-family marginal-gain diagnostic, not a recalibration of the source-of-advantage decomposition."

### 2.3 Legacy `正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md`

**Current state.** Line 320 cites "ABM OOS UR RMSE = 0.221 pp (5 seeds)".

**Why it matters.** This file is a legacy preparation report. It is **not** in the manuscript-ready package, but its content may leak into §6.4 prose if drafted from the wrong source.

**Resolution.** Do not cite this file in §6.4. Cite `正式撰写/fix6.4/benchmark_metrics.json` and `fix6.4/tables/table1_main_postcovid_benchmark.csv`, both of which report ABM = 0.2731 pp. Flag the legacy file as **LEGACY-DO-NOT-CITE** in §6.4's source list.

### 2.4 `V_Full` is **not** best on `full_post_2018`

**Current state.** `fix6.2/tables/table1_variant_summary.csv`:
| Variant | UR_RMSE_post_covid_pp | UR_RMSE_full_post2018_pp |
|---|---:|---:|
| V_Simplified | 0.5616 | **1.3426** |
| V_LaborOnly | 0.3626 | 1.3837 |
| V_Homogeneous | 0.5448 | 1.4144 |
| V_Full | **0.2731** | 1.4674 |

V_Full ranks first on the post-COVID window (0.273 pp), but **last on the full-post-2018 window** (1.467 pp). The full-post-2018 window is dominated by the 2020 crisis where all variants under-predict; V_Full's heterogeneous calibration over-fits to the recent calm period.

**Why it matters.** §6.2 must say "V_Full is best **on the main recent evaluation window**", not "V_Full is the best heterogeneous configuration". The window-specific qualifier is mandatory.

**Resolution.** §6.2 prose must use "on the main recent evaluation window" or "on the 2022-01..2026-02 window" every time V_Full's ranking is asserted. The appendix must show the full-post-2018 row with V_Full last.

### 2.5 `E13` 57.2 ± 3.4 pp source-of-advantage stability ≠ `E07` 94.2%

**Current state.** E13's Key Numbers row says "Source-of-advantage share stability across methods: 57.2 ± 3.4 pp". E07's headline source-of-advantage share is 94.19% (heterogeneity) / 5.81% (mechanism).

**Why it does not actually conflict (but reads as a conflict).** E13 uses the **legacy M0 family** for its cross-method robustness check (`正式撰写/6.5/robustness_metrics.json` packageE_calibration block). E07's 94% number uses the **recalibrated V_Full family** (`fix6.2/tables/table4_source_of_advantage.csv`). They are two different statistics computed on two different calibration protocols, applied to different baselines.

**Resolution.** Add a clarifying note to `E13_Report.md` and to the wording bank: "The 94.2% heterogeneity share reported in §6.2 is the within-experiment accounting decomposition computed on the recalibrated V_Full family (E7). The 57.2 ± 3.4 pp band reported in E13 is a cross-calibration-method robustness check computed on the legacy M0 family and is not numerically comparable. Both are reported; main text cites only 94.2%; appendix cites both with explicit family labels."

---

## 3. Regime-label policy (Issue 2)

| Current label / window key | Final manuscript label | Use case |
|---|---|---|
| `pre_covid_stable` (2018-01..2019-12) | early stable window (2018-01..2019-12) | Main text + appendix |
| `covid_crisis_mar` (2020-03..2021-12) | 2020–2021 disruption window (March 2020 onward) | Main text |
| `covid_crisis_jan` (2020-01..2021-12) | 2020–2021 disruption window (January 2020 onward) | Appendix only |
| `post_covid_norm` (2022-01..2026-02) | main recent evaluation window (2022-01..2026-02) | Main text headline |
| `full_post_2018` (2018-01..2026-02) | full post-2018 evaluation (2018-01..2026-02) | Main text |
| `train` (2004-01..2017-12) | training window (2004-01..2017-12) | Methods / §6 intro |
| `validation` (2018-01..2021-12) | validation window (2018-01..2021-12) | Appendix only |

**Policy decisions:**
- **Window keys** in CSV / JSON / Python code are file-locked: do **not** rename `post_covid_norm` to `main_recent` in code. Keep the keys; rename only the human-readable labels in figure captions, axis tick labels, and report prose.
- **Audit-mirror figures** (`audit_mirror/figures/*.png`) are appendix-only and need not be redrawn; their captions in `_INDEX.md` can simply note "regime labels in the figure are file-locked window keys; see manuscript regime-label table for the camera-ready translations".
- **Paper-ready figures** (`paper_ready_figures/*.png` and `Results_PaperReady_Figures/*.png`) must be redrawn with the final labels for §6 main text — see Section 5 (Figure Revision Checklist).
- **Section 6.1 framing:** Regime decomposition is presented as a **diagnostic, not a forecast target**. The 2020-21 disruption window is a scope check, not a claim about the model's crisis-prediction ability.
- **Captions:** Do not put "Post-COVID RMSE" in any main-text caption or title; use "Main recent evaluation window RMSE" or "Post-2022 UR tracking RMSE".

---

## 4. Audit-layer vs paper-ready (Issue 3)

| Section | Paper-ready figures (main text candidates) | Audit-mirror figures (appendix-only) | Action |
|---|---|---|---|
| S06_01 | F01 Observed vs Simulated UR, F02 Regime RMSE Bar | E4 F01–F02 (2) + E5 F01–F02 (2) | Redraw F01, F02 with new regime labels; audit mirror untouched |
| S06_02 | F01 Control RMSE Bar, F02 Source of Advantage | E6 F01–F04 (4) + E7 F01–F02 (2) | Redraw F01, F02 with new labels; audit mirror untouched |
| S06_03 | F01 Ablation RMSE Bar, F02 Ladder RMSE Path | E8 F01–F04 (4) + E9 F01–F02 (2) | Redraw F01 (regime labels); F02 may stay (no COVID label in step plot) but **must add non-monotonic caveat to caption** |
| S06_04 | F01 Benchmark RMSE Bar, F02 Paths Dynamic | E10 F01–F04 (4) | Redraw F01, F02 with new labels |
| S06_05 | F01 Robustness Dashboard (4-panel) | E11 F01 + E12 F01–F02 + E13 F01–F02 (5) | Redraw F01 dashboard with new labels |

**Audit-mirror figures stay as appendix-only.** They contain `Post-COVID norm.`, `COVID crisis (Mar 2020 on)`, `Pre-COVID stable` in axis labels because they are direct copies from `正式撰写/fix6.x/figures/`. They are correct as appendix artefacts and do not need redrawing.

---

## 5. Issue-by-issue summary (the Final Decision Table is in the CSV)

| Issue ID | Title | Verdict | Blocks §6 writing? |
|---|---|---|---|
| 1 | 0.221 pp vs 0.273 pp headline | 0.273 pp is the headline; 0.221 pp is appendix legacy diagnostic | **YES** (must rebuild S06_01_T01) |
| 2 | COVID / post-COVID regime labels | New mapping table; redraw paper-ready figures; audit-mirror untouched | NO (cosmetic) |
| 3 | Audit-layer vs paper-ready | Audit-mirror appendix-only by construction; only 9 paper-ready figures need attention | NO |
| 4 | S06_01 main-table reconciliation | Rebuild T01 row; co-report 0.273 not 0.221 | **YES** |
| 5 | S06_02 window-specific advantage | Always qualify V_Full ranking with "on the main recent evaluation window"; document V_Full last on full-post-2018 in appendix | **YES** (wording must be added) |
| 6 | S06_03 ablation vs ladder reconciliation | Search is least substitutable; other channels weak/substitutable; ladder is appendix; fix E09 Key Numbers | **YES** (E09 numbers wrong) |
| 7 | S06_04 training-window asymmetry | ABM 2004-01..2017-12 vs benchmarks 2001-01..2021-12; disclose; benchmarks have longer window incl. COVID; ABM still wins by 0.036 pp | NO (disclosure paragraph only) |
| 8 | S06_05 robustness over-interpretation | Use "supports the tracking claim, conditional on weak identification and rolling-split variability" | NO (wording only) |
| 9 | Main text vs appendix decisions | See `Results_MainText_vs_Appendix_Decision.csv` | NO |
| 10 | Forbidden / required wording | See `Results_Final_Wording_Guide.md` | NO |

---

## 6. Per-issue resolution detail

### Issue 4 — S06_01 final disposition

| Asset | Use | Required note |
|---|---|---|
| S06_01 main table (rebuilt T01) | Main text | Row 4 must be recalibrated V_Full = 0.273 pp; rows 1–3 retain dynamic-regime evaluation labels |
| S06_01_F01 observed vs simulated UR | Main text | Redraw with "main recent evaluation window" panel title |
| S06_01_F02 regime RMSE bar | Main text | Redraw x-axis tick labels per Section 3 mapping |
| E04 / E05 audit figures | Appendix | File-locked regime labels; document in `audit_mirror/_INDEX.md` |
| E02_F02 multi-seed UR trajectory | Appendix | Seed dispersion diagnostic |

**Window-count disclosure.** The 2022-01..2026-02 window is **50 calendar months but 49 valid observations** (Oct-2025 UNRATE is NaN in the BLS release used). Disclose this in the caption of `S06_01_T01` ("n = 49 valid months out of 50") and in `S06_01_F01`'s caption.

**Crisis window placement.** The 2020–2021 disruption window appears in §6.1 only as a scope diagnostic: model captures direction (correlation 0.75) but under-predicts magnitude (bias −2.07 pp). Do **not** present it as a forecast target.

### Issue 5 — S06_02 final disposition

| Claim | Allowed? | Final wording |
|---|---|---|
| V_Full is best in the main recent evaluation window | YES | "V_Full attains UR RMSE 0.273 pp on the main recent evaluation window 2022-01..2026-02, ranking first among the four internally-calibrated variants." |
| V_Full is best across all windows | NO | Banned. V_Full is **last** on full-post-2018 (1.467 pp vs V_Simplified 1.343 pp). |
| Heterogeneity causally explains 94% | NO | Use "94% of the 0.29 pp total accounting gain is associated with restoring worker-side heterogeneity". |
| Heterogeneity-associated accounting gain is positive | YES | "The within-experiment accounting decomposition attributes 94% of the gain to heterogeneity restoration." |
| Source-of-advantage share matches across calibration methods | NO | Banned. E13's 57.2% band uses the legacy M0 family; E07's 94.2% uses the recalibrated V_Full family. Different statistics. |
| Mechanism contribution is negligible | CAUTIOUS | Allowed only as "mechanism-associated gain is 5.8% of total in this window; it is bounded above by the experimental design which keeps all 14 mechanisms active in V_Homogeneous." |

### Issue 6 — S06_03 final disposition

| Claim | Evidence | Allowed wording | Disallowed wording |
|---|---|---|---|
| Search-friction heterogeneity is the least substitutable channel | V_NoSearch +0.81 pp, V_SearchOnly +0.04 pp | "Least substitutable accounting channel" | "Search causes 81% of the unemployment-tracking accuracy" |
| Liquidity, housing, consumption are necessary heterogeneities | V_NoLiquidity +0.10, V_NoHousing −0.04, V_NoConsumption −0.02 | "These channels are weaker and partly substitutable after recalibration; V_NoHousing and V_NoConsumption recalibrate to UR RMSE comparable to or below V_Full." | "Liquidity / housing / consumption heterogeneities are necessary" |
| Ablation is causal mechanism identification | — | — | "Causal", "structural mechanism", "identifies the mechanism" |
| Joint vs marginal deltas are additive | V_NoSLH = +0.43 ≠ V_NoSearch + V_NoLiquidity + V_NoHousing (sum = +0.88) | "Joint ablations are sub-additive in pp; recalibration partially substitutes between dimensions" | "Effects of search, liquidity, housing sum to the joint ablation effect" |
| Ladder L0..L6 is monotonic | L0=0.55, L1=0.55, L2=1.05, L3=1.06, L4=0.52, L5=0.27, L6=0.22 | Ladder shows the **overall trend** from L0 to L6 is downward but **with non-monotonic intermediate levels**; the largest single drop is L4→L5 (adding housing): −0.25 pp | "The ladder shows a monotone improvement from L0 to L6" |
| Ladder L6 matches V_Full | L6 = 0.2211, V_Full = 0.2731 | "L6 of the ladder and V_Full of fix6.2 are different calibration protocols; their RMSE values are not directly comparable" | "L6 matches V_Full" |

**Default conclusion (post-fix).** Re-calibrated ablations identify Labor Search Friction as the least substitutable accounting channel under this decomposition; the liquidity, housing, and consumption channels are weaker and partly substitutable. The ladder confirms the overall direction of the heterogeneity contribution but does not provide additional point identification.

### Issue 7 — S06_04 training-window resolution

| Model / benchmark | Training window | Training end (inclusive) | Evaluation start | Possible leakage? | Final manuscript wording |
|---|---|---|---|---|---|
| ABM V_Full (recalibrated) | 2004-01..2017-12 | 2017-12 | 2022-01 | **NO** — ABM does not see 2018-01..2021-12 at calibration time; the validation window is used only for candidate selection, not parameter fitting | "ABM training window 2004-01..2017-12 (168 months); evaluation window 2022-01..2026-02 (50 calendar months, 49 valid observations)." |
| Benchmarks B0a..B8 (dynamic protocol) | 2001-01..2021-12 | 2021-12 | 2022-01 | **NO** — fit ends strictly before evaluation start. Note this window includes the 2020-21 disruption | "Benchmarks fitted on 2001-01..2021-12 inclusive (252 monthly observations), generating multi-step paths over 2022-01..2026-02." |
| ABM_Full_original (legacy M0, §6.1) | 2004-01..2017-12 | 2017-12 | 2022-01 | No | "Legacy baseline; not separately recalibrated and not used as the comparison reference in §6.4." |

**Asymmetry note (must be in §6.4 prose):**
> The benchmark fit window (2001-01..2021-12) is longer than the ABM training window (2004-01..2017-12) and includes the 2020-21 disruption period that ABM did not see at calibration. The 0.036 pp ABM margin over the best benchmark is therefore obtained despite the benchmarks' larger and more recent fitting sample. There is no out-of-sample leakage in either direction: both fits terminate strictly before the 2022-01 evaluation start.

**Renaming / re-labelling.**
- `table1_main_postcovid_benchmark.csv` row labels: replace "Post-COVID" in interpretation column with "main recent evaluation window".
- `fig1_oos_paths.png` axis title: "Main recent evaluation window UR forecast" (currently "Post-COVID UR forecast").
- `S06_04_F01` y-axis title: keep "UR RMSE (pp)"; the regime-window subtitle should read "Main recent evaluation window, 2022-01..2026-02".

**Final benchmark wording:**
> Under a common dynamic multi-step protocol on the main recent evaluation window, the ABM attains UR RMSE 0.273 pp, ranking first across twelve models. The two closest benchmarks (a no-change naive forecast and an exponential-smoothing model with damped trend) both attain 0.309 pp, a margin of 0.036 pp over the ABM. This margin is of the same order as the ABM's own cross-seed standard deviation of 0.023 pp; we therefore describe the ABM as competitive at the top of the comparison set on this window rather than dominating it. Window-specificity is essential to this claim: the same ranking does not necessarily hold under alternative split protocols (see §6.5 robustness checks).

### Issue 8 — S06_05 robustness disposition

| Robustness dimension | Evidence (concrete number) | Supports main claim? | Caveat | Main text or appendix |
|---|---|---|---|---|
| Training-window sensitivity | M0 mean 0.245 ± 0.011 pp on 7 OOS-aligned splits; 6/7 wins vs all 4 benchmarks | **Conditionally** | R1 (2014 cutoff, training predates 2020) gives 1.88 pp; rolling-window stability is not uniform | Main text: one-line summary. Appendix: full per-split table and figure. |
| Forecast horizon (Package B) | log-log slope of UR RMSE vs h = 1..36 is −0.09 (M0 Main, shallowest among 8 models) | YES | Computed on legacy M0 family, not recalibrated V_Full | Main text: one-line summary. Appendix: full horizon table and figure. |
| Agent-count sweep (Package D) | Mean UR RMSE plateaus at N ≥ 50,000; default N = 100,000 is past plateau | YES | Computed on legacy M0 family | Main text: one-line summary. Appendix: full grid. |
| Calibration-method sensitivity (Package E performance lens) | Best-test UR RMSE 0.214–0.243 pp across 5 methods; CV 5.55% | YES | Computed on legacy M0 family; band does not include the recalibrated V_Full headline 0.273 pp (different protocol) | Main text: one-line summary. Appendix: full per-method table. |
| Parameter identification (Package E parameter lens) | 10 of 14 parameters have CV ≥ 0.40 across top-5 candidates within at least one calibration method; the remaining 4 of 14 are below this threshold (only 1 of 14 — `h2m_mpc_floor` — is strictly stable at CV < 0.20) | NO (this is a caveat, not a supporting result) | Must be co-reported with every parameter mention; report parameters as bands | Main text: weak-ID disclosure paragraph. Appendix: full heatmap. |
| Heterogeneity-share stability across methods | 57.2 ± 3.4 pp on legacy M0 family | Partial | Different statistic from §6.2's 94.2% (different baseline family) | Appendix only |

**Final robustness wording:**
> Robustness checks support the stability of the unemployment-tracking result under expanding-window splits, forecast-horizon variation, agent-count convergence, and calibration-method substitution. The evidence is conditional in two specific senses: first, two rolling-window splits whose training period predates the 2020-21 disruption perform substantially worse (UR RMSE up to 1.88 pp), so the ranking-level claim does not extend to arbitrary train/test splits; second, ten of fourteen free parameters are weakly identified (cross-candidate CV ≥ 0.40 in at least one calibration method) so the robustness is consistent with a predictive — rather than structural — interpretation of the parameter values.

---

## 7. Final status checklist

### Sections that can start writing immediately
- **§6.4 Benchmark comparison.** All numbers are stable and consistent. Add the training-window asymmetry disclosure paragraph. Cite `fix6.4/benchmark_metrics.json` only; flag the legacy 6.4 report as DO-NOT-CITE.
- **§6.5 Robustness.** All numbers are stable. Use the conditional language above; co-report weak-ID with every parameter reference.

### Sections that need a pre-write fix
- **§6.1 Dynamic and regime-specific performance.** Rebuild `S06_01_T01` so the post-COVID row is the recalibrated 0.273 (Issue 1 + Issue 4). Then write.
- **§6.2 Internal controls and source of advantage.** Wording must qualify "V_Full is best **on the main recent evaluation window**" (Issue 5). E07 numbers are correct; no table rebuild needed. Then write.
- **§6.3 Heterogeneity ablations and ladder.** Patch `E09_Report.md` Key Numbers (Issue 6: L6=0.2211, drop=−0.2487, non-monotonic disclosure). Patch the ladder caveat noting L6 ≠ V_Full. Then write.

### Numbers that are now locked
- Headline UR RMSE: **0.273 pp** (recalibrated V_Full, 5 seeds, 49 valid months, 2022-01..2026-02).
- Benchmark gap: **0.036 pp** modest advantage over the best benchmarks (No-change, ETS).
- Source-of-advantage shares: **94.2%** heterogeneity / **5.8%** mechanism (post-COVID, recalibrated family only).
- Ablation deltas: NoSearch **+0.81**, NoLiquidity **+0.10**, NoHousing **−0.04**, NoConsumption **−0.02**, NoSLH **+0.43**, SearchOnly **+0.04** pp.
- Weak-ID count: **10 of 14**.
- Calibration-method band: **0.214–0.243 pp** (legacy M0 family).
- Training-window robustness: **0.245 ± 0.011 pp** on 7 OOS-aligned splits (legacy M0 family).

### Figures that must be redrawn before submission
9 paper-ready PNGs (S06_01_F01, F02; S06_02_F01, F02; S06_03_F01; S06_04_F01, F02; S06_05_F01). See `Results_Figure_Revision_Checklist.csv`.

### Tables that must be revised before submission
3 tables. See `Results_Table_Revision_Checklist.csv`.

### What stays only in appendix
- All 25 audit-mirror figures (regime labels file-locked).
- `0.221 pp` (legacy M0 baseline diagnostic).
- `0.214 pp` (legacy default-config baseline).
- E13 57.2% share band (legacy family).
- Old-vs-new decomposition tables (E07 T02, E08 T02).
- LFPR/EPOP regime bar (S06_01 supplementary).
- Prediction-error time series (E04 supplementary).
- Per-seed dispersion (E02 F02).
- Heterogeneity ladder full table (E09 T01).

---

## 8. Companion files

- `Results_Consistency_Decision_Table.csv` — one row per issue.
- `Results_Figure_Revision_Checklist.csv` — one row per paper-ready figure.
- `Results_Table_Revision_Checklist.csv` — one row per paper-ready table requiring revision.
- `Results_MainText_vs_Appendix_Decision.csv` — one row per evidence asset.
- `Results_Final_Wording_Guide.md` — required and banned phrasings, organised by section.
