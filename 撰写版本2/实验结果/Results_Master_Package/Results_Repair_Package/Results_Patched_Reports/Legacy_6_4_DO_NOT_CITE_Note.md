# Legacy Section 6.4 Report — DO NOT CITE

**Flagged file:** `正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md`
**Status:** LEGACY PREPARATION REPORT. Not citable in manuscript-facing §6.4 prose.
**Reason:** Headline numbers in the legacy report use the **legacy baseline family** (ABM OOS UR RMSE = 0.221 pp). The final benchmark comparison uses the **separately recalibrated V_Full** (ABM OOS UR RMSE = 0.2731 pp). Citing the legacy report in the main text would import the 0.221 number into a section whose headline must be 0.273.

---

## Required disclosure text (paste-ready)

> This legacy benchmark preparation report cites the 0.221 pp legacy baseline diagnostic and must not be used for manuscript-facing Section 6.4 prose. The final benchmark comparison uses the recalibrated V_Full result of 0.2731 pp.

---

## Specific numbers in the legacy report that must NOT enter the main text

The legacy report (`正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md`) contains the following obsolete claims. Each one must be replaced by the recalibrated counterpart before any §6.4 prose is written.

| Legacy report claim | Status | Required replacement |
|---|---|---|
| "ABM OOS UR RMSE = 0.221 pp" | OBSOLETE | Use **0.2731 pp** (recalibrated V_Full, 5-seed mean, 49 valid months). Source: `S06_04_T01` row 1. |
| "Full ABM 0.221 < Beveridge 0.422 < DMP 0.636 < VAR(2) 0.663 < AR(1) 1.611" | OBSOLETE ranking | Use the full 12-row ranking in `S06_04_T01_Dynamic_Benchmark_Comparison__E10_v01.csv`. ABM is rank 1 at 0.2731 pp; No-change and ETS tie at 0.3094 pp; Beveridge OLS 0.4216 pp; Flow-based UR 0.4263 pp; DMP-style 0.6361 pp; VAR(p) 0.6633 pp; Ridge-VAR 1.2643 pp; AR(p) 1.6106 pp; ARIMA 1.6175 pp; Historical mean 2.1729 pp; Drift 6.9191 pp. |
| "gap to the strongest external benchmark (Beveridge) is 0.201 pp — about a 1.91× RMSE ratio" | OBSOLETE | Use the **No-change and ETS** as the strongest external benchmarks (tied at 0.3094 pp). Gap is **0.0363 pp** (ratio 1.13×). Beveridge is rank 4, not the closest competitor. |
| "Safe paper claim: ... the heterogeneous ABM achieves the lowest OOS UR RMSE, 1.91× lower than the strongest external benchmark. The advantage is structural ..." | OBSOLETE wording | Use the locked benchmark claim: **"ABM ranks first on the main recent evaluation window with a modest 0.036 pp improvement over No-change and ETS; the margin is within the cross-seed SD of 0.023 pp."** Do not use "structural" or "dominates". |
| "AR reverts to the training mean, VAR extrapolates the wrong direction through the COVID structural break, DMP under-predicts the post-COVID level" | LANGUAGE OBSOLETE | The diagnostic content (AR mean reversion, VAR sign flip, DMP under-prediction) is correct but must be reworded to remove "COVID structural break" framing and rephrased without "structural" claims for the ABM. Use "the 2020-21 disruption window" instead of "COVID structural break". |
| "benchmarks B1..B4" labelling | OBSOLETE labels | Use the named-model labelling from `S06_04_T01` (No-change, ETS, Beveridge OLS, Flow-based UR, DMP-style, VAR(p), Ridge-VAR, AR(p), ARIMA, Historical mean, Drift). The legacy B1..B4 set is a strict subset that omits No-change, ETS, Flow-based UR, Ridge-VAR, ARIMA, Historical mean, and Drift. |

---

## What §6.4 prose MUST cite instead

| Source | Path | Role |
|---|---|---|
| Final benchmark table | `Results_PaperReady_Tables/S06_04_T01_Dynamic_Benchmark_Comparison__E10_v01.csv` | Canonical 12-row dynamic benchmark ranking |
| Final benchmark metrics JSON | `正式撰写/fix6.4/benchmark_metrics.json` | Source-of-truth metrics behind S06_04_T01 |
| Final benchmark main table | `正式撰写/fix6.4/tables/table1_main_postcovid_benchmark.csv` | Recalibrated comparison table |
| E10 dynamic benchmark package | `Results_By_Experiment/E10_External_Benchmark_Comparison/` | Audit-layer evidence (full figures, regime split, model specs) |

---

## Locked benchmark claim wording for §6.4

> On the main recent evaluation window (2022-01..2026-02; 49 valid months), the survey-moment-anchored worker-side heterogeneous ABM ranks first among twelve forecasting models under a dynamic multi-step protocol, with UR RMSE 0.273 pp. The two best external benchmarks (No-change and ETS) tie at 0.309 pp, a gap of 0.036 pp that is within the ABM's cross-seed standard deviation (0.023 pp). The advantage is therefore modest and window-specific; we do not claim dominance. ABM training spans 2004-01..2017-12 (168 months); benchmarks are fitted on 2001-01..2021-12 (252 months, including the 2020-21 disruption window that the ABM did not see). Two structural benchmarks (Beveridge OLS, Flow-based UR) receive the observed OOS vacancy / separation series, matching the ABM's exogenous-input set.

---

## Cross-references

- `Results_Master_Package/Consistency_Resolution/Results_Consistency_Resolution_Report.md` — Issue 7 (training-window asymmetry), Issue 12 (legacy 6.4 report citation discipline).
- `Results_Master_Package/Consistency_Resolution/Results_Final_Wording_Guide.md` — locked phrasings for §6.4.
- `Results_Master_Package/Results_Repair_Package/Results_Repair_Decision_Table.csv` — repair scope for §6.4.

**Action for §6.4 author:** when writing §6.4 prose, treat the legacy preparation report as a source-of-history reference only (i.e., to understand how the benchmark set evolved). Do not lift any number, ranking, or claim from it into the manuscript text.
