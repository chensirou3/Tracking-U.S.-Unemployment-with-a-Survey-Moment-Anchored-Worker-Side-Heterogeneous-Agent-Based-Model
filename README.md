# Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model

Replication code and paper-ready results for the working paper of the same title.

The model is a **monthly, worker-side, heterogeneous agent-based model (ABM)** of the U.S. labor market.
A synthetic population of 100,000 agents is initialised from the Federal Reserve Bank of New York
**Survey of Consumer Expectations (SCE)** moments; macroeconomic inputs come from **FRED**
(UNRATE, CIVPART, EMRATIO, JTSJOR, JTSLDR, CES, FEDFUNDS). Calibration is anchored to the
SCE-derived survey moments rather than to aggregate time-series alone.

## Headline result

| Quantity | Value |
|---|---|
| Manuscript headline UR RMSE (recalibrated V_Full, main recent evaluation window) | **0.273 pp** |
| Cross-seed standard deviation (5 seeds) | 0.023 pp |
| Main recent evaluation window | 2022-01 .. 2026-02 (49 valid months / 50 calendar) |
| ABM training window | 2004-01 .. 2017-12 (168 months) |
| Best comparable benchmarks | No-change / ETS (tie at 0.309 pp) |
| Weak-ID parameters (CV ≥ 0.40 across top-5 candidates) | 10 of 14 |

The headline RMSE, evaluation window, and weak-ID disclosure are locked across all paper-ready
figures and tables; see `撰写版本2/实验结果/Results_Master_Package/Consistency_Resolution/`.

## Repository layout

| Path | Contents |
|---|---|
| `Phase1_Output/` | Heterogeneity audit, MVP boundary, vectorised agent schema (specs only). |
| `Phase2_Code/` | Synthetic-population generator and diagnostics (SCE moments → 100k agents). |
| `Phase2_Output/` | Population specs + empirical-distribution JSON files (NPZ excluded). |
| `Phase3_Code/` | **Core ABM engine**: environment, scheduler, labor / household blocks, calibration engine, all package runners (A–E), Phase-7 main runner, Phase-8 derived + benchmark runners. |
| `Phase3_Data/` | FRED macroeconomic inputs (CSV). |
| `正式撰写/6.1/ .. /6.5/` | Original Phase-7 / Phase-8 run scripts, artifact builders, and per-section preparation reports. |
| `正式撰写/fix6.1/ .. /fix6.5/` | Recalibrated runs and revised preparation reports used for the manuscript headline. |
| `撰写版本2/实验结果/Results_Master_Package/` | **Paper-ready baseline.** PNG figures, CSV tables, per-section reports, claim-to-evidence registries, repair package, consistency resolution. |
| `撰写版本2/实验结果/_scripts/` | Figure and table builders for Section 6 (`build_figures.py`, `build_audit_figures.py`, `build_tables.py`). |

The canonical paper-ready figures and tables for Section 6 are under
`撰写版本2/实验结果/Results_Master_Package/Results_PaperReady_Figures/` and
`Results_PaperReady_Tables/`. They are mirrored into each section folder under
`Results_By_Section/S06_xx/`.

## Reproducing the experiments

All reproduction is driven by a single orchestrator, `reproduce.py`, which encodes the full
dependency chain (synthetic population → calibration → re-evaluation → benchmarks → artifact
builders → paper-ready figures and tables). It must be invoked from the repository root.

Inspect the chain and the status of every stage (`READY`, `BLOCKED`, `DONE`):

```bash
python reproduce.py --list
```

Common entry points:

```bash
# Tier 1: just rebuild paper-ready Section 6 figures and tables from the included
# CSV / JSON artifacts plus any NPZ files already on disk (runs in <2 min).
python reproduce.py --stage paper

# Tier 2: full reproduction from a clean clone (≈10–15 h, single CPU).
python reproduce.py --stage all

# Resume from a specific stage after a crash:
python reproduce.py --from-stage fix6.2-reeval

# Skip stages whose declared outputs already exist:
python reproduce.py --stage all --skip-existing

# Print the plan without executing anything:
python reproduce.py --dry-run --stage all
```

The full chain (declaration order in `reproduce.py`):

| # | Stage | Script | Runtime |
|---|---|---|---|
| 1 | `population` | `Phase2_Code/population_init_engine.py` | ~5 min |
| 2 | `legacy-derived` | `正式撰写/6.2/run_6_2_derived.py` | ~30 min |
| 3 | `legacy-ladder` | `正式撰写/6.3/run_6_3_packageC_ladder.py` | ~30 min |
| 4 | `legacy-ablation` | `正式撰写/6.3/run_6_3_phase7_ablation.py` | ~1 h |
| 5 | `fix6.1` | `正式撰写/fix6.1/run_fix6_1_regime.py` | ~1 min |
| 6 | `fix6.2-calibrate` | `正式撰写/fix6.2/run_fix6_2_calibrate.py` | ~2.5 h |
| 7 | `fix6.2-reeval` | `正式撰写/fix6.2/run_fix6_2_reeval.py` | ~30 min |
| 8 | `fix6.3-calibrate` | `正式撰写/fix6.3/run_fix6_3_calibrate.py` | ~3 h |
| 9 | `fix6.3-reeval` | `正式撰写/fix6.3/run_fix6_3_reeval.py` | ~30 min |
| 10 | `fix6.4` | `正式撰写/fix6.4/run_fix6_4_benchmarks.py` | ~30 min |
| 11–15 | `build-fix6.{1..5}` | `正式撰写/fix6.{1..5}/build_*_artifacts.py` | <1 min each |
| 16 | `build-paper-tables` | `撰写版本2/实验结果/_scripts/build_tables.py` | <1 min |
| 17 | `build-paper-figures` | `撰写版本2/实验结果/_scripts/build_figures.py` | <1 min |
| 18 | `build-paper-audit` | `撰写版本2/实验结果/_scripts/build_audit_figures.py` | <1 min |

The headline RMSE (0.273 pp) comes out of the `fix6.2-reeval` stage; everything after that is
either dependent post-processing or non-overlapping evidence (regime decomposition, ablations,
benchmarks). All intermediate NPZ files (~1.5 GB across the chain) are deliberately excluded from
this repository and must be regenerated by the run stages above.

## Data inputs

- **FRED macroeconomic series** (small; included under `Phase3_Data/`).
- **NY Fed Survey of Consumer Expectations (SCE)** raw microdata (large; **not included** in this
  repository due to FRBNY redistribution terms). Download from
  <https://www.newyorkfed.org/microeconomics/sce> and place under `SCE_Data/{01..08}/`.
  The empirical distributions extracted from the SCE are stored in
  `Phase2_Output/empirical_distributions.json` (and the four `*_distributions.json` siblings),
  so most downstream code can be re-run without re-downloading the SCE microdata.

## Dependencies

Python 3.10+ with the standard scientific stack (`numpy`, `scipy`, `pandas`, `matplotlib`).
No exotic dependencies; a fresh `pip install numpy scipy pandas matplotlib` in a clean venv should
be sufficient for the build scripts. The model runners use only the standard library plus those
four packages.

## Caveats explicitly disclosed in the manuscript

- The 0.273 pp headline is on a 49-month main recent evaluation window. The full post-2018
  aggregate UR RMSE is 1.42 pp and is reported as a diagnostic, not as the headline.
- ABM training (2004-01..2017-12) and benchmark fitting (2001-01..2021-12) windows are
  asymmetric; benchmarks see the 2020-2021 disruption window that the ABM does not.
- 10 of 14 free parameters are weakly identified across the top-5 calibration candidates
  (coefficient of variation ≥ 0.40); the manuscript reports parameters as bands, not point
  estimates.
- The heterogeneity-vs-mechanism source-of-advantage decomposition is a within-experiment
  accounting partition, not a causal decomposition.
- The legacy §6.4 preparation report (`正式撰写/6.4/Results_6_4_Benchmark_Comparison_Preparation_Report.md`)
  is appendix-only and is not citable from main-text §6.

## Citation

To be added once the working paper is publicly released.
