# Results Master Report

**Project:** Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model
**Package:** `Results_Master_Package/`
**Purpose:** Single entry point to all evidence supporting §6 of the manuscript. Two layers — Audit (`Results_By_Experiment/`) and Manuscript (`Results_By_Section/`) — plus a shared paper-ready figure/table pool and seven top-level registries.

---

## 1. Package layout

```text
Results_Master_Package/
├── Results_Master_Report.md                        (this file)
├── README.md
├── Results_Asset_Registry.csv
├── Results_Table_Registry.csv
├── Results_Figure_Registry.csv
├── Results_Experiment_to_Section_Crosswalk.csv
├── Results_Claim_to_Evidence_Table.csv
├── Results_Missing_Inconsistency_Checklist.md
├── Results_Wording_Bank.md
├── Results_PaperReady_Figures/        (7 PNGs, 300 dpi)
├── Results_PaperReady_Tables/         (7 CSVs)
├── Results_By_Experiment/             (E01..E13 audit folders)
└── Results_By_Section/                (S06_01..S06_05 manuscript folders)
```

## 2. Headline numbers (manuscript-ready)

| Statistic | Value | Window | Source |
|---|---|---|---|
| UR RMSE (5-seed mean) | **0.273 pp** | 2022-01..2026-02 (post-COVID) | E4/E5 |
| UR RMSE seed SD | 0.023 pp | same | E4 |
| UR bias | −0.04 pp | same | E5 |
| UR correlation | 0.79 | same | E5 |
| COVID-crisis UR RMSE | 2.82 pp | 2020-03..2021-12 | E5 |
| V_Full vs V_Homogeneous gap (heterogeneity) | 0.272 pp (94.2% of total) | post-COVID | E7 |
| V_Full vs V_Simplified gap (total) | 0.289 pp | post-COVID | E7 |
| Worst ablation (V_NoSearch) | +0.81 pp vs V_Full | post-COVID | E8 |
| Benchmark rank of V_Full | **1 of 12** | post-COVID | E10 |
| Margin over best benchmark (B0a / B3) | 0.036 pp | post-COVID | E10 |
| Robustness: CV across calibration methods | 5.55% | post-COVID | E13 |
| Weakly-identified parameters | 10 of 14 (CV ≥ 0.40) | top-5 candidates per method | E13 |

## 3. Audit layer — Results_By_Experiment

Thirteen folders, one per experiment. Each contains `E##_Report.md` (purpose, sources, protocol, outputs, key numbers, caveats), `source_files.md` (provenance map), `status.md` (READY / READY WITH CAVEAT / MISSING), plus `tables/` and `figures/` subfolders.

| Paper ID | Folder | Status |
|---|---|---|
| E1 | `E01_Synthetic_Population_Construction/` | READY |
| E2 | `E02_Baseline_Stability_Check/` | READY WITH CAVEAT |
| E3 | `E03_Calibration_Setup/` | READY |
| E4 | `E04_Dynamic_Evaluation/` | READY |
| E5 | `E05_Regime_Specific_Evaluation/` | READY |
| E6 | `E06_Internal_Control_Comparison/` | READY |
| E7 | `E07_Source_of_Advantage_Decomposition/` | READY |
| E8 | `E08_Heterogeneity_Ablation/` | READY |
| E9 | `E09_Heterogeneity_Ladder/` | READY |
| E10 | `E10_Forecast_Benchmark_Comparison/` | READY |
| E11 | `E11_Training_Window_Sensitivity/` | READY |
| E12 | `E12_Forecast_Horizon_and_Agent_Count_Sensitivity/` | READY |
| E13 | `E13_Calibration_Method_and_Parameter_ID_Sensitivity/` | READY |

## 4. Manuscript layer — Results_By_Section

Five folders, one per §6 subsection. Each contains `S06_0x_Report.md` with the headline result, paper-ready figure and table references, drop-in manuscript-facing wording, and the per-section caveats and wording rules.

| Section | Folder | Source experiments | Status |
|---|---|---|---|
| §6.1 Dynamic and Regime-Specific Performance | `S06_01_Dynamic_and_Regime_Specific_Performance/` | E4, E5 | READY |
| §6.2 Internal Controls and Source of Advantage | `S06_02_Internal_Controls_and_Source_of_Advantage/` | E6, E7 | READY |
| §6.3 Recalibrated Heterogeneity Ablations | `S06_03_Recalibrated_Heterogeneity_Ablations/` | E8, E9 | READY |
| §6.4 Forecast Benchmark Comparison | `S06_04_Forecast_Benchmark_Comparison/` | E10 | READY |
| §6.5 Robustness and Sensitivity | `S06_05_Robustness_and_Sensitivity/` | E11, E12, E13 | READY |

## 5. Paper-ready figures and tables

Seven figures + seven tables under `Results_PaperReady_Figures/` and `Results_PaperReady_Tables/`. All figures are 300-dpi PNGs in a neutral palette. Naming pattern: `S06_XX_F##_Description__E##_v01.png` and `S06_XX_T##_Description__E##_v01.csv`.

## 6. Wording rules (summary; full text in `Results_Wording_Bank.md`)

- Headline UR RMSE: **0.273 pp** (not 0.221 pp).
- Decompositions: **"within-experiment accounting"**, never "causal".
- Benchmark margin: **"competitive at the top"**, never "dominates".
- Parameter values: **bands**, not point estimates; **"weakly identified"**, not "structurally identified" for the 10 weak parameters.
- Crisis-window error: always reported alongside the post-COVID headline.
- Units: errors in **pp**, correlations in **decimal**, shares with explicit decimal/percent label.

## 7. Reproduction map

| Asset | Source script | Source data |
|---|---|---|
| S06_01_T01 / S06_01_F01 | `_scripts/build_tables.py`, `_scripts/build_figures.py` | `正式撰写/fix6.2/reeval_metrics.json`, `reeval_trajectories.npz` |
| S06_01_F02 | `_scripts/build_figures.py` | `正式撰写/fix6.1/regime_metrics.json` |
| S06_02_T01 / S06_02_F01 | `_scripts/build_*.py` | `正式撰写/fix6.2/tables/table1_variant_summary.csv` |
| S06_02_T02 | `_scripts/build_tables.py` | `正式撰写/fix6.2/tables/table4_source_of_advantage.csv` |
| S06_03_T01 / S06_03_F01 | `_scripts/build_*.py` | `正式撰写/fix6.3/tables/table2_post_covid_ablation.csv` |
| S06_03_T02 / S06_03_F02 | `_scripts/build_*.py` | `正式撰写/6.3/ladder_metrics.json`, `ladder_series.npz` |
| S06_04_T01 / S06_04_F01 | `_scripts/build_*.py` | `正式撰写/fix6.4/benchmark_metrics.json`, `tables/table1_main_postcovid_benchmark.csv` |
| S06_05_T01 / S06_05_F01 | `_scripts/build_*.py` | `正式撰写/6.5/robustness_metrics.json`, `tables/table2_..table5_*.csv` |

## 8. Ready-for-Section-6 verdict

**READY.** The six BLOCKS-RESULTS-WRITING items in the checklist are wording / reporting rules (not missing evidence); they are enforced in `Results_Wording_Bank.md` and observed in every `S06_0x_Report.md`. Eight NEEDS-CHECK items are disclosure paragraphs to be added during drafting and do not block the headline numbers. Four APPENDIX-ONLY items do not affect §6.

§6 can be drafted directly from `Results_By_Section/` using the wording bank and the seven paper-ready assets.
