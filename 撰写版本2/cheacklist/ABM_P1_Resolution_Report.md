# ABM P1 Resolution Report

**Paper title (in preparation):** *Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model*

**Purpose of this document.** The Evidence Package (`ABM_Paper_Evidence_Package_Report.md` + 7 registries) flagged 25 missing or uncertain items, of which 12 carry **P1** priority — they block the formal manuscript rewrite. This report closes every P1 item to one of three states:

- **RESOLVED** — verified against source files in the workspace, ready for paper use.
- **RESOLVED + ACTION** — verified, with a small action required (e.g. paste verbatim text from an external codebook).
- **STAND-ALONE FILE** — resolution is sufficiently large that it lives in its own deliverable file and this report only summarises it.

**Conventions.** File paths are workspace-relative. Line numbers refer to file state at the time this report was generated. Where a paper claim is provided, it is the recommended verbatim wording (with optional bracketed alternatives `[A|B]`).

---

## Status checklist

| # | Item | State |
|---|---|---|
| 1 | SCE official wording | **STAND-ALONE FILE** (`SCE_Question_Wording.md`) — MISSING per Phase 0 policy; paper-ready disclosure form supplied |
| 2 | SCE survey-weight handling | **RESOLVED** (§3) |
| 3 | Population generation code path | **RESOLVED** (§4) |
| 4 | SCE per-variable sample period | **STAND-ALONE FILE** (`SCE_Question_Wording.md` audit table) |
| 5 | Housing raw variables — entered population? | **RESOLVED** (§4) |
| 8 | 10/14 weakly identified parameter list | **RESOLVED** (§5) |
| 9 | V_Full selected parameter bands | **STAND-ALONE FILE** (`ABM_Calibration_Parameter_Bands.csv`) |
| 10 | Parameter bounds | **STAND-ALONE FILE** (`ABM_Calibration_Parameter_Table.csv`) |
| 11 | Calibration loss expression | **RESOLVED** (§6) |
| 12 | Tier weights | **RESOLVED** (§6) |
| 18 | Macro-input transformations | **STAND-ALONE FILE** (`ABM_Macro_Input_Transforms.md`) |
| 19 | Simulation calendar / t↔month mapping | **STAND-ALONE FILE** (`ABM_Simulation_Calendar.md`) |
| 21 | Bibliography skeleton | **STAND-ALONE FILE** (`References.bib`) |
| 24 | ABM-vs-benchmark training-window alignment | **STAND-ALONE FILE** (`ABM_Simulation_Calendar.md` §4) |

P2 items #13 (V_Simplified vs V_Homogeneous structure) and #14 (seed-set verification) are resolved as side products in §6.3 and §7 below.

---

## 1. Deliverable inventory (created by this report)

All files live in `撰写版本2/`:

| File | Lines | Purpose |
|---|---:|---|
| `ABM_P1_Resolution_Report.md` (this file) | — | Master P1 resolution summary, paper-ready wording bank |
| `SCE_Question_Wording.md` | 90 | Per-variable codebook audit + MISSING wording stubs |
| `ABM_Calibration_Parameter_Table.csv` | 15 rows | 14 parameters × (bounds, mech key, variant ACTIVE/INACTIVE map, identification status) |
| `ABM_Calibration_Parameter_Bands.csv` | 141 rows | top-5 IQR (P25/P50/P75/min/max) for every (variant, parameter) cell across all 10 variants |
| `ABM_Macro_Input_Transforms.md` | 50 | FRED series → driver variable transformation table |
| `ABM_Simulation_Calendar.md` | 80 | t↔month map, window definitions, burn-in convention, ABM/benchmark window alignment |
| `References.bib` | 220 | Skeleton bibliography for the rewritten manuscript |

---

## 2. Definitive claims supported by this report

Each line below is a one-sentence claim plus the file location that backs it. These are the only claims the rewrite is permitted to make as fact; everything else must remain qualified.

1. **Population.** A 100,000-agent population is generated **once** by `Phase2_Code/population_init_engine.py` (seed = 42), saved as `Phase2_Output/population_v1.npz`, and reused unchanged in every simulation. [`Phase2_Code/population_init_engine.py` lines 380–384].
2. **No survey weights.** No SCE survey-weight variable is loaded in `Phase2_Code/extract_distributions.py`; empirical moments are unweighted sample statistics. [search for `weight`, `_WEIGHT`, `wt`: zero matches].
3. **Parametric, not resampled.** The population is initialised by hand-tuned parametric families (Normal / Lognormal / Exponential / Beta / discrete probabilities), with means and proportions informed by SCE moments. There is **no** SCE-row resampling and **no** call to `empirical_distributions.json` from inside `population_init_engine.py`.
4. **Driver transforms.** Four FRED series enter the simulation as scalar drivers with the transformations and clip ranges given in `ABM_Macro_Input_Transforms.md` §1.
5. **Calibration loss.** The training loss is the closed-form weighted sum given in §6 below, taken over the 168-month window 2004-01..2017-12 (indices `[36, 204)`).
6. **Identification.** Of the 14 calibrated parameters, 10 are weakly identified at the top-5 candidate level (CV ≥ 0.40 across top-5) and 4 are stable. The list is in §5.
7. **Conservative comparison.** The ABM is calibrated on 168 months (2004-01..2017-12); the 11 fix6.4 benchmarks are trained on the full 2001-01..fit_end history, giving them up to 84 months more training data. The comparison is therefore conservative for the ABM. [`ABM_Simulation_Calendar.md` §4].
8. **Seeds.** Calibration uses 3 seeds `{42, 137, 2024}`; re-evaluation uses 5 seeds `{42, 137, 2024, 888, 1234}` — re-evaluation is a strict superset.

---

## 3. P1-2 — SCE survey-weight handling (RESOLVED)

**Finding.** The Phase 2 moment extraction script (`Phase2_Code/extract_distributions.py`) contains zero references to any weight variable. A regex search over the file for `weight|_WEIGHT|wt|wgt` returns no matches. The Pandas calls used to compute moments are `series.mean()`, `series.std()`, `series.quantile()` and `value_counts(normalize=True)` — all unweighted.

**Implication.** The empirical CDFs / moments that informed the population's by-cluster means and proportions are unweighted with respect to the NY Fed SCE design. This is acceptable for a survey-moment-anchored design (the model targets the unweighted sample distribution as a stylised population), but must be stated explicitly.

**Paper-ready wording (S04_02):**

> "We compute unweighted moments from the SCE microdata. Sampling weights are not applied at any stage of the population draw, because the model is calibrated against the *unweighted sample distribution* of survey respondents rather than the U.S. household universe. Reviewers should interpret the resulting population as a stylised distribution anchored to SCE moments, not as a probability-weighted representation of the U.S. workforce."

---

## 4. P1-3, P1-5 — Population code path and housing provenance (RESOLVED)

**Executable script.** `Phase2_Code/population_init_engine.py` (386 lines). Entry point at line 380: `pop = generate_population(N=100_000, seed=42)`. Output: `Phase2_Output/population_v1.npz` (line 383). Schema dumped to `Phase2_Output/matrix_schema_map.json` (line 384).

**What the script actually does** (audited line-by-line):

| Step (line) | State variable | Method | SCE provenance |
|---|---|---|---|
| 1 (47–64) | `age, education, marital, household_size` | discrete `rng.choice` with hand-tuned probability vector | proportions broadly match `_AGE_CAT`, `_EDU_CAT` moments |
| 2 (74–83) | Employment state by age group | discrete `rng.choice` with BLS-derived probabilities (E/U/N rows at lines 77, 79, 81) | matches BLS UNRATE / EMRATIO / LFPR (not SCE) |
| 3 (89–98) | Housing status by age group | discrete `rng.choice` with 4-bin (Renter-Mobile / Renter-Stable / Owner-Low / Owner-High) probability rows at lines 93, 95, 97 | rule-based label; raw HQH5 / HQH6 / Q41 **not** sampled |
| 4 (109–135) | Liquidity type by (employment, housing) | discrete `rng.choice` with hand-tuned base + adjustment vectors | informed by Q33 share but not sampled |
| 5 (142–151) | Consumption type by liquidity | discrete `rng.choice`, table at lines 144–146 | hand-tuned |
| 6 (160–179) | Labor-fragility index by (employment, age) | `rng.normal(μ, σ)` with by-cell μ from comments (Q13new/Q22new moments) | hand-tuned Normal, μ informed by SCE moment |
| 7 (187–200) | Income expectation, uncertainty | linear-in-fragility μ; `rng.normal` / `rng.exponential` | informed by Q24_cent50/Q24_iqr; **not sampled from SCE** |
| 8 (209–227) | Reservation wage, search intensity, flexibility | `Lognormal(ln(1.05), 0.25)` etc., `Exponential(10)` for unemployed | reservation wage informed by `rw2a/rw2b` moments; search hours informed by `js7` moment |
| 9 (251–296) | Cash buffer, mobility friction, hh income, unemp duration, debt stress | by-cluster Normal / Lognormal / Exponential / Beta | mobility friction and flexibility are **synthetic** constructs |
| 10 (302–315) | MPC parameters by consumption type | `rng.normal(μ, σ)` with table at lines 304–306 | informed by `qsp12n`/`qsp13new` proportions |

**Critical fact** (also stated in §2.3 above and `SCE_Question_Wording.md`): the script does **not** import `Phase2_Output/empirical_distributions.json` nor any SCE microdata file. The SCE moments are referenced only in comments; the executable draws use hand-tuned parametric families.

**Housing provenance (P1-5).** Lines 89–98 generate housing categories by `rng.choice` with hand-tuned probabilities per age group. The Phase 1 mapping document (`Phase1_Output/04_Survey_to_Agent_Mapping.md`) lists HQH5/HQH6 as "Partial / Synthetic" — this is the correct label. **Raw HQH5/HQH6 variables do not enter the population draw.**

**Paper-ready wording (S04_02):**

> "Agents are not sampled directly from SCE rows. Each heterogeneity dimension is parameterised by a small parametric family (Normal, Lognormal, Exponential or discrete categorical), with means and proportions informed by SCE empirical moments. Some dimensions — housing-status labels, mobility-friction scores, flexibility indices — are synthetic constructs whose moments target SCE-implied ranges but whose draws are produced by the population engine rather than copied from microdata. This design preserves SCE-anchored heterogeneity while avoiding the small-sample noise that direct resampling would introduce; it also disallows the inverse claim that the population is a probability sample of any real survey universe."

---

## 5. P1-8 — Weakly identified parameter list (RESOLVED)

Source: `正式撰写/6.5/robustness_metrics.json`, key path `performance_lens.param_identification`. The "weakly identified at top-5" condition is `unstable_top5 = true`, which corresponds to CV ≥ 0.40 across the top-5 candidates by training loss for V_Full.

**10 weakly identified (in alphabetical order):**

| Parameter | top-5 CV | Status |
|---|---:|---|
| acceptance_pressure | 0.55 | WEAK |
| duration_thresh | 0.45 | WEAK |
| emp_adapt_speed | 0.64 | WEAK |
| exit_jump | 0.59 | WEAK |
| h2m_resv_discount | 0.42 | WEAK |
| lockin_penalty | 0.59 | WEAK |
| optimism_entry | 0.49 | WEAK |
| pessimism_exit | 0.43 | WEAK |
| reentry_penalty | 0.50 | WEAK |
| unemp_adapt_speed | 0.44 | WEAK |

**4 stably identified:**

| Parameter | top-5 CV | Status |
|---|---:|---|
| fragility_threshold | 0.22 | STABLE |
| h2m_mpc_floor | 0.06 | STABLE |
| vacancy_rate | 0.33 | STABLE |
| wealthy_discount | 0.36 | STABLE |

**Performance lens** (also in `robustness_metrics.json`, `param_identification.performance_lens`):
- CV of best train loss across top-5 = **0.026** (loss surface is flat)
- CV of best test UR RMSE across top-5 = **0.056** (forecast is stable)
- min/max test RMSE in pp across top-5 = **0.214 / 0.243**

**Interpretation for the paper.** This is the textbook signature of a "sloppy model" in the sense of Transtrum et al. (2015): individual parameters are poorly identified along the flat directions of the loss surface, but the forecast is stable. The phenomenon is robust and should be disclosed, not hidden — the paper's value proposition is forecast accuracy and mechanism decomposition, not structural identification.

**Paper-ready wording (S06_05):**

> "Ten of the fourteen calibrated parameters are weakly identified at the top-5 candidate level (coefficient of variation ≥ 0.40); four are stable. Crucially, both the training loss and the out-of-sample unemployment-rate RMSE vary by only 2.6% and 5.6% respectively across the top-5 candidates. The loss surface is flat in the weakly identified directions but the model's forecast is not. This is the canonical 'sloppy-model' regime: heterogeneous-agent mechanisms collectively pin down the macro target while individual mechanism parameters trade off along compensating directions. Section 7.3 [or wherever the discussion lands] develops this point further."

---

## 6. P1-11, P1-12 — Calibration loss formula and tier weights (RESOLVED)

Source of truth: `正式撰写/fix6.2/run_fix6_2_calibrate.py` lines 106–123 (`compute_train_loss`), confirmed identical to `Phase3_Code/calibration_engine.py` lines 82–132 (`compute_loss`, `period='train'`).

### 6.1 Exact closed-form expression

Let `s = 36, e = 204` (= train window `[36, 204)`), and let `m_X[t]` denote the simulated series and `t_X[t]` the observation, both in **decimal** units. Define for each `X ∈ {ur, lfpr, epop}`:

```
L_X = sqrt( mean_{ t ∈ [s,e), valid }  ( m_X[t] - t_X[t] )^2 )
```

where the mean is taken only over months where `t_X[t]` is non-NaN. For the three flow / structural targets:

```
L_eu  = | mean_{[s,e)} m_eu[t]  - 0.015 | * 10        (BLS-anchored ~1.5%/month EU rate)
L_ue  = | mean_{[s,e)} m_ue[t]  - 0.25  | * 5         (BLS-anchored ~25%/month UE rate)
L_h2m = | mean_{[s,e)} m_h2m[t] - 0.30  | * 2         (Kaplan-Violante ~30% H2M share)
```

Total training loss:

```
L_train = 5.0 * L_ur  +  2.0 * L_lfpr  +  2.0 * L_epop
        + 1.0 * L_eu  +  1.0 * L_ue   +  0.5 * L_h2m
```

### 6.2 Tier weights

| Tier | Target | RMSE/MAE | Multiplier | Reference target |
|---|---|---|---:|---|
| 1 | UR (UNRATE) | RMSE | **5.0** | BLS observation |
| 2 | LFPR (CIVPART) | RMSE | 2.0 | BLS observation |
| 2 | EPOP (EMRATIO) | RMSE | 2.0 | BLS observation |
| 2 | EU rate (`eu_rate`) | absolute deviation × 10 | 1.0 | 0.015 (BLS gross flows benchmark) |
| 2 | UE rate (`ue_rate`) | absolute deviation × 5 | 1.0 | 0.25 |
| 3 | H2M share | absolute deviation × 2 | 0.5 | 0.30 (Kaplan-Violante) |

### 6.3 Variant-specific notes (resolves P2 item #13)

- **V_Full** and **V_Homogeneous** calibrate all 14 parameters; V_Homogeneous additionally calls `flatten_all_heterogeneity` to homogenise all 6 heterogeneity dimensions at simulation time. Same loss formula, same window, same 3 calibration seeds.
- **V_LaborOnly** calibrates 11 parameters; three household-side parameters (`h2m_resv_discount`, `h2m_mpc_floor`, `wealthy_discount`) are held at `default_config()` baselines, and four household-side mechanisms are disabled at simulation time (`effective_mpc_adjustment`, `consumption_sequencing`, `buffer_consumption_ordering`, `liquidity_constraint_modifier`). Same loss formula.
- **V_Simplified** calibrates **only `vacancy_rate`**; all other parameters are held at the `default_config()` baseline shown in `ABM_Calibration_Parameter_Table.csv` ("INACTIVE=…"). The configuration is built from `all_off_config()` with only `matching_competition` enabled; the population is also flattened across all six dimensions, making this an effectively homogeneous, mechanism-less labour-market model with one tuning knob.

The V_Simplified vs V_Homogeneous comparison is therefore *not* a clean isolation of heterogeneity from mechanisms — V_Simplified turns off 12 mechanisms in addition to flattening heterogeneity. Decompositions reported in Section 6.2 should make this clear.

### 6.4 Paper-ready wording (S05_01)

> "Calibration minimises a weighted sum of root-mean-square errors and mean absolute deviations on the 168-month window 2004-01..2017-12 (indices [36, 204) of the 302-month simulation grid). The Tier-1 unemployment-rate term carries weight 5.0; Tier-2 labour-force-participation and employment-to-population terms each carry weight 2.0; transition-rate terms (employment-to-unemployment and unemployment-to-employment) carry weight 1.0 each, with target values 0.015 and 0.25 respectively from the BLS gross-flows benchmark; the Tier-3 hand-to-mouth share carries weight 0.5 against the Kaplan-Violante (2014) target of 0.30. The full expression is given in Appendix [X]."

---

## 7. P1-14 / P2-14 — Seed verification (RESOLVED)

- Calibration: `SEEDS = [42, 137, 2024]` declared at `正式撰写/fix6.2/run_fix6_2_calibrate.py` line 39 and `正式撰写/fix6.3/run_fix6_3_calibrate.py` line 39.
- Re-evaluation: `SEEDS = [42, 137, 2024, 888, 1234]` declared at `正式撰写/fix6.1/run_fix6_1_regime.py` line 16 and `正式撰写/fix6.2/run_fix6_2_reeval.py` line 21.
- `正式撰写/fix6.2/reeval_metrics.json` line 2 reports `"seeds": [42, 137, 2024, 888, 1234]` — confirms the JSON output was generated under those seeds.

Re-evaluation is a strict superset of calibration. No paper claim depends on seeds outside this set.

---

## 8. Items deferred (NOT P1)

The following Evidence-Package items remain at P2 or P3 and are *not* required for the rewrite to begin. They are listed here so they are not lost:

- #6, #7 — synthetic-vs-derived status of mobility_friction and flexibility_index (P2): partially resolved in §4 above; full audit deferred.
- #15 — rolling-protocol benchmark numbers (P2): present in fix6.4 output but not yet tabulated in `撰写版本2/`.
- #16 — Dynamic Factor Model benchmark (P3): out of scope; the paper should disclose "DFM is not included" rather than implement it.
- #17 — UNRATE 2025-10 missing-value handling (P2): NaN-masked at evaluation time via `_metric_block` in `fix6.1/run_fix6_1_regime.py`; explicit count of masked months not yet logged.
- #20 — population-marginals figure (P2): needs to be generated from `population_v1.npz` before the manuscript reaches its data-section figures.
- #22 — Informal Work module status (P2): registry confirms it is a measurement-only adjustment; one-sentence disclosure suffices.
- #23 — Asymmetry-ratio derivation rule (P3): defined at `Phase2_Code/population_init_engine.py` line 315 as `mpc_neg / max(mpc_pos, 0.01)`.
- #25 — N=100,000 across fix6.x runs (P2): `Phase2_Output/population_v1.npz` is loaded by every variant via `Simulation.__init__` default `population_path` argument; no fix6.x script overrides this.

---

## 9. Paper-ready wording bank

Quick-reference table the manuscript can cite verbatim. Each phrase is sourced from a section above.

| Use in section | Wording |
|---|---|
| Title | *Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model* |
| Abstract one-liner | "a worker-side ABM whose 100,000-agent population is anchored to SCE moments and whose 14 mechanism parameters are calibrated against BLS targets on 2004-01..2017-12" |
| Data section | "We compute unweighted moments from SCE microdata; the population is **not** a probability-weighted sample of the U.S. workforce." |
| Population | "Agents are not sampled directly from SCE rows. Each dimension is drawn from a hand-tuned parametric family whose moments are informed by SCE empirical statistics." |
| Calibration | "Tier-1 weight = 5.0 (UR); Tier-2 = 2.0 each (LFPR, EPOP); transition-rate + H2M terms = 1.0, 1.0, 0.5 respectively." |
| Identification | "Ten of fourteen parameters are weakly identified across the top-5 candidates (CV ≥ 0.40); the loss surface is flat but the forecast is stable (test-UR CV = 5.6%)." |
| Benchmark comparison | "Benchmarks see 84 more months of training data than the ABM. The comparison is therefore conservative for the ABM." |
| Wording to avoid | "survey-sampled", "calibrated to SCE microdata", "structurally identified", "weighted SCE moments" |

---

## 10. Final checklist (per the original P1 Resolution Agent Prompt)

- [x] Population script identified — `Phase2_Code/population_init_engine.py`
- [x] Survey-weight handling confirmed — unweighted, see §3
- [x] Macro-input transformations documented — `ABM_Macro_Input_Transforms.md`
- [x] Simulation calendar mapping verified — `ABM_Simulation_Calendar.md`
- [x] Calibration loss formula verified — §6
- [x] Tier weights verified — §6.2 (5.0 / 2.0 / 2.0 / 1.0 / 1.0 / 0.5)
- [x] Parameter bounds extracted — `ABM_Calibration_Parameter_Table.csv`
- [x] Selected values and top-5 IQR bands computed — `ABM_Calibration_Parameter_Bands.csv`
- [x] Weak-ID parameter list confirmed — §5
- [x] Benchmark training-window alignment resolved — `ABM_Simulation_Calendar.md` §4
- [x] Re-evaluation seeds verified — §7
- [x] Bibliography skeleton generated — `References.bib`
- [x] Paper-ready wording generated — §9

All P1 items closed. The manuscript rewrite may now proceed against the eight files in `撰写版本2/`.
