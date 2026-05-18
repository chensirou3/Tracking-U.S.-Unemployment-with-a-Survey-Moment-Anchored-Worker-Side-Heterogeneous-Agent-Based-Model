# E1 — Source Files

| Asset | Path | Role |
|---|---|---|
| Generation script | `Phase2_Code/population_init_engine.py` | Builds population, single seed, parametric draws |
| Population file | `Phase2_Output/population_v1.npz` | Loaded by every fix6.x simulation run |
| Schema map | `Phase2_Output/matrix_schema_map.json` | Column→variable name mapping |
| Moment extractor | `Phase2_Code/extract_distributions.py` | Computes unweighted SCE moments |
| Moment file | `Phase2_Output/empirical_distributions.json` | Anchoring moments (referenced only) |
| Documentation | `撰写版本2/cheacklist/ABM_P1_Resolution_Report.md` §4 | Line-by-line audit |
| Documentation | `撰写版本2/cheacklist/SCE_Question_Wording.md` | Per-variable codebook table |

No fix6.x folder produces or modifies the population.
