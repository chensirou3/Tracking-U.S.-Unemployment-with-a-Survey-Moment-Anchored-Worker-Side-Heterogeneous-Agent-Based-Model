# Results_Master_Package — README

Single entry point to all evidence supporting Section 6 of the paper *Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model*.

## Quick start

- **Drafting §6?** Open `Results_By_Section/` and read the five `S06_0x_Report.md` files in order. Each one contains the headline result, the paper-ready figures and tables to cite, and drop-in manuscript-facing wording.
- **Need a specific number traceback?** Open the corresponding `Results_By_Experiment/E##_*/E##_Report.md`. It lists the source `正式撰写/fix6.*` files and the protocol that produced each number.
- **Need to know which assets are mainstream vs appendix?** Open `Results_Experiment_to_Section_Crosswalk.csv`.
- **Worried about wording rules?** Open `Results_Wording_Bank.md`. Approved phrasings and banned phrasings are explicit.
- **About to submit?** Check `Results_Missing_Inconsistency_Checklist.md` for the six BLOCKS-RESULTS-WRITING items (all are wording rules; no missing evidence).

## Layout

```
Results_Master_Package/
├── Results_Master_Report.md                 ← overview + headline-numbers table
├── README.md                                ← this file
├── Results_Asset_Registry.csv               ← every asset, audit + manuscript paths
├── Results_Table_Registry.csv               ← all 31 tables with status
├── Results_Figure_Registry.csv              ← all 28 figures with captions
├── Results_Experiment_to_Section_Crosswalk.csv
├── Results_Claim_to_Evidence_Table.csv      ← 20 claims with evidence trace
├── Results_Missing_Inconsistency_Checklist.md
├── Results_Wording_Bank.md                  ← approved + banned phrasings
├── Results_PaperReady_Figures/              ← 7 paper-ready PNGs (300 dpi)
├── Results_PaperReady_Tables/               ← 7 paper-ready CSVs
├── Results_By_Experiment/
│   ├── E01_Synthetic_Population_Construction/
│   ├── E02_Baseline_Stability_Check/
│   ├── E03_Calibration_Setup/
│   ├── E04_Dynamic_Evaluation/
│   ├── E05_Regime_Specific_Evaluation/
│   ├── E06_Internal_Control_Comparison/
│   ├── E07_Source_of_Advantage_Decomposition/
│   ├── E08_Heterogeneity_Ablation/
│   ├── E09_Heterogeneity_Ladder/
│   ├── E10_Forecast_Benchmark_Comparison/
│   ├── E11_Training_Window_Sensitivity/
│   ├── E12_Forecast_Horizon_and_Agent_Count_Sensitivity/
│   └── E13_Calibration_Method_and_Parameter_ID_Sensitivity/
└── Results_By_Section/
    ├── S06_01_Dynamic_and_Regime_Specific_Performance/
    ├── S06_02_Internal_Controls_and_Source_of_Advantage/
    ├── S06_03_Recalibrated_Heterogeneity_Ablations/
    ├── S06_04_Forecast_Benchmark_Comparison/
    └── S06_05_Robustness_and_Sensitivity/
```

Each `Results_By_Experiment/E##_*/` folder contains:
- `E##_Report.md` — purpose, sources, protocol, outputs, key numbers, caveats
- `source_files.md` — provenance map back to `正式撰写/fix6.*`
- `status.md` — READY / READY WITH CAVEAT / MISSING
- `tables/` — audit CSVs
- `figures/` — audit PNGs

Each `Results_By_Section/S06_0x_*/` folder contains:
- `S06_0x_Report.md` — headline result + paper-ready references + drop-in wording

## Headline numbers

| Statistic | Value | Window |
|---|---|---|
| UR RMSE (5-seed mean) | **0.273 pp** | 2022-01..2026-02 |
| UR RMSE seed SD | 0.023 pp | same |
| COVID-crisis UR RMSE | 2.82 pp | 2020-03..2021-12 |
| Benchmark rank of V_Full | **1 of 12** | post-COVID |
| Margin over best benchmark | 0.036 pp | post-COVID |
| Weakly identified parameters | 10 of 14 | top-5 per method |
| Calibration-method CV | 5.55% | post-COVID best-test |

## Wording rules (top three)

1. **Headline UR RMSE is 0.273 pp**, not 0.221 pp. The legacy figure 0.221 pp circulates only in pre-recalibration appendix tables.
2. **Decompositions are accounting, not causal**. Use "within-experiment accounting decomposition", never "causal decomposition".
3. **Benchmark comparison is competitive, not dominant**. The 0.036 pp margin over No-change/ETS is the same order as the V_Full seed SD (0.023 pp).

Full rules in `Results_Wording_Bank.md`.

## Status

**Ready for §6 drafting.** All evidence is in place; remaining items in `Results_Missing_Inconsistency_Checklist.md` are either wording rules (enforced via the wording bank) or appendix-only tasks.

## See also

- `撰写版本2/ABM_P1_Resolution_Report.md` — verified facts from the Phase-0 P1 resolution.
- `撰写版本2/ABM_Calibration_Parameter_Bands.csv` — top-5 IQR bands for all 14 parameters across all 10 variants.
- `撰写版本2/SCE_Question_Wording.md` — SCE question wording reference (paste verbatim FRBNY codebook before final submission).
- `撰写版本2/References.bib` — bibliography skeleton.
