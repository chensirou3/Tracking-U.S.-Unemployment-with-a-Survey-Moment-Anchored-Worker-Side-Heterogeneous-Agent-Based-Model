# Results Final Wording Guide

**Scope:** §6.1–§6.5 of the manuscript "Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model".
**Status:** This guide is the **single source of truth** for §6 phrasing. It supersedes any earlier prose drafts in `正式撰写/6.x/` if they conflict.
**Companion files:** `Results_Consistency_Resolution_Report.md`, the four CSV checklists in this folder, and `Results_Wording_Bank.md` (parent folder).

---

## 1. Locked numerical phrasings (use verbatim or close paraphrase)

| Phrasing | Where to use | Notes |
|---|---|---|
| "headline UR RMSE of 0.273 pp" | abstract, §6.1, §6.2, §6.4 lead sentences | always cite: recalibrated V_Full, dynamic protocol, 5 seeds, 49 valid months in 2022-01..2026-02 |
| "5-seed mean across {42, 137, 888, 1234, 2024}" | first reference per section | seed set is identical across V_Full, V_LaborOnly, V_Homogeneous, V_Simplified, and all ablations |
| "cross-seed standard deviation of 0.023 pp" | wherever 0.273 is cited as a point estimate | uncertainty disclosure |
| "main recent evaluation window (2022-01 to 2026-02; 50 calendar months, 49 valid observations)" | §6.1 setup, every regime-table footnote | the missing month is Oct-2025 (BLS NaN) |
| "modestly better than the best benchmarks (No-change, ETS) by 0.036 pp" | §6.4 | the margin is within the seed SD; do not call it dominance |
| "94.2% heterogeneity-associated share / 5.8% mechanism-associated share" | §6.2 source-of-advantage | always followed by "of the within-experiment accounting gain" |
| "10 of 14 calibrated parameters are weakly identified" | §6.5, anywhere parameter values are referenced | co-report whenever you cite a calibrated value |
| "ABM training window 2004-01..2017-12 (168 months); benchmark fit 2001-01..2021-12 (252 months)" | §6.4 footnote / disclosure paragraph | the asymmetry must be disclosed once |

---

## 2. Required wording (use these phrases)

### Regime-window labels
- **Early stable window** — replaces "pre-COVID stable".
- **2020–2021 disruption window** — replaces "COVID crisis" or "COVID-heavy".
- **Main recent evaluation window** — replaces "Post-COVID normalisation" wherever it is the headline window.
- **Full post-2018 evaluation** — replaces "Full post-2018" (label is fine; just remove the implicit COVID framing).

### Identity / framing
- "survey-moment-anchored" — the model's identity word; use in title, abstract, §6 lead.
- "worker-side heterogeneous agent-based model" — full noun form on first mention; "the ABM" thereafter.
- "dynamic multi-step protocol" — the forecast protocol; never call it "out-of-sample" without further qualification.
- "separately calibrated controls" — for V_LaborOnly / V_Homogeneous / V_Simplified.
- "re-calibrated ablations" — for E08 ablations; always paired with this adjective to distinguish from default-config ablations.
- "fitted simulation parameters" — what calibration produces. Never "estimated primitives" or "structural estimates".
- "within-experiment accounting" — for the source-of-advantage decomposition.
- "weakly identified parameters" — for the 10/14 finding.

### Claim-strength words
- "competitive" or "modestly better" — for the benchmark comparison.
- "least substitutable channel" — for the labor search friction ablation result (NoSearch ΔRMSE ≈ +0.81 pp).
- "predictive and diagnostic" — the model's role; never "predictive and structural".
- "supports the tracking claim" — the bar for what robustness checks demonstrate.
- "conditional on …" — every robustness sentence must include a conditioning clause.

### Source-of-advantage specifically
- "an additive accounting partition computed on the main recent evaluation window".
- "94.2% of the gap is associated with worker-side heterogeneity; 5.8% with the bundle of mechanism-side recalibrations".
- "association" / "associated with" — never "due to", "caused by", "explained by".

---

## 3. Avoid wording (do not use)

### Banned: COVID-as-narrative
- ❌ "COVID prediction paper"
- ❌ "post-COVID model"
- ❌ "the model predicts COVID-era unemployment"
- ❌ "Post-COVID RMSE" as a figure or table title (use "Main recent evaluation window UR RMSE")
- ❌ "Pre-COVID" / "Post-COVID" / "Crisis-COVID" in any main-text label

### Banned: causal / structural overclaim
- ❌ "ABM dominates [benchmarks / variants / ablations]"
- ❌ "causal decomposition" — say "within-experiment accounting partition"
- ❌ "structural identification" — say "calibration"
- ❌ "structural estimates" / "structural parameters" / "primitives" — say "fitted simulation parameters"
- ❌ "mechanism identification" — say "internal-control comparison" or "ablation diagnostic"
- ❌ "the true mechanism is …"
- ❌ "heterogeneity causes X% of the gap" — say "the heterogeneity-associated accounting share is X%"
- ❌ "Search Friction is the structural channel"
- ❌ "predictive paper but structural model" — incompatible with the paper's identity

### Banned: scope / population overclaim
- ❌ "fully survey-based"
- ❌ "fully representative population" / "truly representative"
- ❌ "completely untouched OOS" — the 2022+ window was held out from ABM calibration but benchmarks used 2020–2021; disclose, do not flatten
- ❌ "the population is the U.S. labor force" — say "synthetic worker population anchored to ACS/CPS moments"

### Banned: robustness overclaim
- ❌ "robust across all regimes"
- ❌ "universally robust" / "fully robust"
- ❌ "all-regime accurate"
- ❌ "ABM solves the tracking problem"
- ❌ "ABM is consistent in every robustness dimension" — two rolling-window splits perform worse; the heterogeneity-share band 0.5–0.94 across calibration families is wide

### Banned: internal-label leakage
- ❌ "M0", "M0_Main", "M0 baseline" — internal package label; replace with "legacy baseline" if a comparison is needed in the appendix
- ❌ "Package A / B / D / E" — internal robustness pipeline labels; replace with the dimension name (Training window / Forecast horizon / Agent count / Calibration method)
- ❌ "R / revised / rerun because old version had problems" — never appears in publishable prose
- ❌ "fix6.1 / fix6.2 / fix6.4" — code paths; never in prose
- ❌ "Sec 6.x baseline" / "P1 report" — internal review labels

### Banned: figure-title strings to grep for
- ❌ "Post-COVID" in any title (use "Main recent evaluation window")
- ❌ "COVID-heavy" anywhere
- ❌ "audit" anywhere in a paper-ready caption
- ❌ "recalibrated vs pre-recalibration" in source-of-advantage figures (use "separately calibrated vs default-config")

---

## 4. Required disclosure clauses (paste-ready)

Each clause appears at least once in the indicated section.

**Window-specific qualifier (§6.2):**
> "On the main recent evaluation window (2022-01..2026-02), V_Full ranks first among the four separately calibrated controls. On the full post-2018 evaluation window, V_Full ranks fourth (1.47 pp), with V_Simplified ranking first (1.34 pp). The window-specificity is reported in appendix Table A_full_post_2018."

**Accounting-not-causal disclaimer (§6.2):**
> "The source-of-advantage decomposition is an additive within-experiment accounting partition computed by holding the heterogeneous-bundle and mechanism-bundle terms fixed at recalibrated values; it does not identify a causal contribution."

**Training-window asymmetry (§6.4 footnote):**
> "The ABM is calibrated on 2004-01..2017-12 (168 months) and forecasts 2022-01..2026-02 dynamically; the benchmarks are fitted on 2001-01..2021-12 (252 months, including the 2020–2021 disruption period that the ABM did not see) and forecast the same window. The asymmetry favours the benchmarks on this comparison."

**Weak-identification disclosure (§6.5 + any §6 parameter reference):**
> "Of the 14 calibrated parameters, 10 are weakly identified in the sense that within the top-5 calibration candidates the coefficient of variation reaches or exceeds 0.40 in at least one calibration method; the reported parameter values are fitted simulation inputs, not structural estimates." (Threshold confirmed at CV ≥ 0.40; see `Results_Repair_Package/Results_WeakID_Threshold_Check.md`.)

**Ablation interpretation guard (§6.3):**
> "A negative ΔRMSE relative to V_Full (V_NoHousing, V_NoConsumption) reflects parameter reassignment under separate recalibration absorbing the removed dimension; it does not imply that the heterogeneity dimension is harmful."

**Ladder caveat (§6.3 appendix reference):**
> "The heterogeneity ladder is reported on the legacy baseline family; its endpoint L6 (0.221 pp) is not directly comparable to the recalibrated V_Full headline (0.273 pp). The ladder is non-monotonic between L1 and L3."

---

## 5. Cross-section consistency checklist

Before any §6.x prose is finalised, confirm against this list:

- [ ] Every numerical RMSE in §6.x main text is one of the locked numbers in §1 above.
- [ ] Every "best" / "first" claim is window-qualified.
- [ ] Every parameter reference is accompanied by the weak-ID disclosure (at least at first mention per section).
- [ ] No banned phrase from §3 appears in the prose.
- [ ] All four "required disclosure clauses" in §4 appear in their assigned sections.
- [ ] Regime labels in the prose match the figure / table revisions in `Results_Figure_Revision_Checklist.csv` and `Results_Table_Revision_Checklist.csv`.
- [ ] No reference to internal labels (M0, Package A..E, fix6.x, R/revised) survives in publishable text.
- [ ] Source-of-advantage uses "association" / "accounting", never "causal" / "explains".
- [ ] Ablation prose uses "least substitutable channel" for Labor Search Friction; "comparable to or marginally below Full after recalibration" for NoHousing / NoConsumption.
- [ ] Benchmark prose uses "competitive" / "modestly better"; never "dominates".

---

## 6. One-paragraph master template (for editorial reference, not for direct paste)

> Across the main recent evaluation window (2022-01 to 2026-02; 49 valid months), the survey-moment-anchored worker-side heterogeneous ABM achieves a 5-seed mean unemployment-rate RMSE of 0.273 pp (cross-seed SD 0.023 pp) under a dynamic multi-step protocol. Against separately calibrated controls, this is the lowest RMSE on the headline window, with 94.2% of the within-experiment accounting gain associated with worker-side heterogeneity and 5.8% with the bundle of mechanism-side recalibrations. Against six external benchmarks fitted on a longer training window (2001-01..2021-12), the ABM is modestly better than the best two benchmarks (No-change, ETS) by 0.036 pp — a gap within the cross-seed standard deviation. Robustness checks across training-window, forecast-horizon, agent-count, and calibration-method dimensions support this tracking result, conditional on the weak identification of 10 of the 14 calibrated parameters and on two rolling-window splits that perform less well. The ablation evidence identifies labor search friction as the least substitutable heterogeneity channel; liquidity, housing, and consumption channels are weaker or partly substitutable after separate recalibration.

---

**End of Wording Guide.** Treat this file as read-only when writing §6 prose. Any deviation must be justified in writing and reflected back into `Results_Wording_Bank.md`.
