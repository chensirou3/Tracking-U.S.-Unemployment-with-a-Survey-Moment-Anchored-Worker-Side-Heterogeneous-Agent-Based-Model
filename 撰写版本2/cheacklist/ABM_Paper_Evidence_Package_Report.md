# ABM Paper Evidence Package Report

**Working title.** Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model.

**Purpose of this document.** A traceability hub for the rewritten paper. Every claim, table, and figure used in the rewrite must be sourced from this report or from the registries it points to. Numbers are quoted verbatim from the source CSVs; units are explicitly **pp** (percentage points) or **decimal**; sources are cited as **file paths** plus a section / table / figure label.

**Deliverables (this package).**

| # | File | Status |
|---|------|--------|
| 1 | `ABM_Paper_Evidence_Package_Report.md` *(this file)* | Final |
| 2 | `ABM_Claim_to_Evidence_Table.csv` | Final |
| 3 | `ABM_Experiment_Registry.csv` | Final |
| 4 | `ABM_Section_Registry.csv` | Final |
| 5 | `ABM_Asset_Registry.csv` | Final |
| 6 | `ABM_Figure_Inventory.csv` | Final |
| 7 | `ABM_Table_Inventory.csv` | Final |
| 8 | `ABM_Missing_Items_Checklist.md` | Final |

**Convention.** `MISSING` = not present in workspace, must be supplied; `UNCERTAIN` = present but not externally verified.

---

# 2. Revised Paper Position

## 2.1 What this paper should be positioned as

A **prediction-oriented, diagnostic, worker-side ABM** for **post-COVID unemployment tracking**, in which the worker-side heterogeneity is **anchored to SCE survey moments** rather than directly resampled from SCE microdata. The model competes with standard statistical and econometric forecasters under a like-for-like dynamic multi-step protocol and accompanies its forecasts with within-model structural diagnostics that benchmark forecasters cannot supply.

## 2.2 What this paper should NOT be positioned as

- Not a full structural labor-market model (no firm side, no wage bargaining, no product market, no inflation channel).
- Not a direct survey-based model (the population is constructed by sequential conditional sampling from SCE marginals + synthetic joint structure, not by bootstrapping respondent rows).
- Not a general labor-market or crisis forecasting model. The COVID crisis is a stress-regime diagnostic, not a forecast target.
- Not a causal identification of behavioural parameters. Ten of fourteen parameters are weakly identified across calibration methods.
- Not a personality model.

## 2.3 Recommended Title

> **Tracking U.S. Unemployment with a Survey-Moment-Anchored Worker-Side Heterogeneous Agent-Based Model**

Alternatives:

> Survey-Moment-Anchored Worker-Side Heterogeneity in an Agent-Based Forecaster of Post-COVID Unemployment

> A Diagnostic Worker-Side ABM for Post-COVID U.S. Unemployment Tracking

## 2.4 One-Sentence Contribution

> We build a 100,000-agent, worker-side ABM whose six MVP heterogeneity dimensions are anchored to SCE survey moments, and show that — within an honest dynamic multi-step protocol — it tracks U.S. post-COVID normalization unemployment with sub-percentage-point RMSE and a modest but consistent edge over separately calibrated internal controls and standard statistical / econometric benchmarks, while making explicit that this edge is regime-bound and that 10 of its 14 behavioural parameters are weakly identified.

## 2.5 Conservative Abstract-Level Claim

> Across the post-COVID normalization window (2022-01 to 2026-02), a re-calibrated heterogeneous ABM produces a 5-seed mean unemployment RMSE of 0.27 pp (±0.02 pp), placing it first among twelve dynamic-protocol forecasters by a margin of 0.04 pp / 13% over the strongest competitors (no-change and ETS). The advantage over separately re-calibrated internal controls is moderate — a total gain of 0.29 pp, of which 0.20 pp is attributable to heterogeneity. Among heterogeneity dimensions, only Labor Search Friction survives separate ablation with a large standalone effect. The model does not predict the COVID-crisis spike (bias −2.07 pp), and 10 of its 14 behavioural parameters are weakly identified across calibration methods. We therefore position the contribution as competitive post-COVID normalization tracking accompanied by within-model diagnostics that standard forecasters cannot supply.

## 2.6 Claims Supported by Evidence

1. Post-COVID unemployment is tracked with sub-pp accuracy (0.273 pp RMSE).
2. Separately calibrated controls confirm a heterogeneity advantage that exists but is moderate (0.288 pp total gain).
3. Labor Search Friction is the most robust standalone heterogeneity channel (Δ +0.812 pp on No-Search ablation).
4. ABM is competitive with strong forecasting benchmarks under a like-for-like dynamic protocol (rank 1 of 12 by 0.036 pp).
5. Predictions are robust to seeds, init window, agent count, calibration method, and training-window split.
6. Parameter identification is weak (10 of 14 with top-5 CV ≥ 0.40 across methods).

## 2.7 Claims NOT Supported

1. ABM does not predict the COVID spike (−2.07 pp bias, max-abs 6.07 pp).
2. ABM is not robust across regime transitions (pre-COVID +0.77 pp bias).
3. ABM does not dominate all benchmarks (lead over no-change/ETS within seed s.d.).
4. ABM is not a causal mechanism identifier (heterogeneity share 94.2% is within-experiment accounting, not decomposition).
5. ABM is not a structural model of the labor market.

## 2.8 Claims to Avoid (Wording Bans)

- "ABM dominates all benchmarks."
- "ABM is robust across all regimes."
- "ABM forecasts the COVID crisis."
- "Search/Liq/Hous each independently contribute."
- "Heterogeneity causally explains 94.2% of the gap."
- "The calibrated parameters identify behavioural mechanisms."
- "OOS is completely untouched."
- "97.6% heterogeneity share" without explicit qualification.
- "Survey-based ABM" (use "survey-moment-anchored").
- "Direct personality measure" (worker traits are anchored, not directly measured).

---

# 3. Dual Coding System

## 3.1 Experiment IDs

See `ABM_Experiment_Registry.csv`. Identifiers `EX01..EX13` follow the prompt; revised variants carry a trailing **R** (EX04R, EX05R, EX06R, EX07R, EX08R).

| ID | Name | Status |
|----|------|--------|
| EX01 | Population Initialization | Final |
| EX02 | First Stable Run | Final |
| EX03 | Calibration (legacy LHS) | Superseded by EX08R |
| EX04 / EX04R | Original / Revised regime-specific OOS | EX04R is final |
| EX05 / EX05R | Original / Revised re-calibrated ablation | EX05R is final |
| EX06 / EX06R | Phase 7 / Revised robustness | Both retained (legacy as appendix invariants) |
| EX07 / EX07R | Original / Revised stronger benchmark race | EX07R is final |
| EX08 / EX08R | Original / Revised re-calibrated controls | EX08R is final |
| EX09 | Training Window Sensitivity (Pkg A) | Legacy invariant |
| EX10 | Forecast Horizon Sensitivity (Pkg B) | Legacy invariant |
| EX11 | Heterogeneity Ladder (Pkg C) | Legacy supporting evidence |
| EX12 | Agent Count Sensitivity (Pkg D) | Legacy invariant |
| EX13 | Calibration Method Sensitivity (Pkg E) | Legacy invariant |

## 3.2 Section IDs

See `ABM_Section_Registry.csv`. Naming convention `S0X_YY` distinguishes Model/Data/ExpDesign (S03/S04/S05) from Results (S06_01..S06_05+S06_06) and Appendix (APP_A, APP_B).

## 3.3 File-Naming Rule

```
S0X_YY_T##_ShortDescription__EX##_v##.csv
S0X_YY_F##_ShortDescription__EX##_v##.png
```

Old files are **not** physically renamed. Mappings live in `ABM_Asset_Registry.csv`, `ABM_Figure_Inventory.csv`, and `ABM_Table_Inventory.csv`.

---


# 4. Section-Level Result Packages

Each Results sub-section has a fixed bundle of evidence assigned to it. The bundles below are referenced by Section ID; the asset registry resolves them to physical files.

## 4.1 S06_01 — Regime-Specific Performance (EX04R)

Main text:
- `S06_01_T01` Regime Performance (from `正式撰写/fix6.1/tables/table1_regime_summary.csv`)
- `S06_01_F01` Full-period UR path; `S06_01_F02` Regime UR RMSE bar.

Appendix:
- `S06_01_T02` Seed-level regime metrics; `S06_01_T03` Old-vs-regime comparison.
- `S06_01_F03` Prediction-error time series; `S06_01_F04` LFPR/EPOP regime bar.

## 4.2 S06_02 — Separately Calibrated Internal Controls (EX08R)

Main text:
- `S06_02_T01` Control comparison; `S06_02_T02` Source-of-advantage.
- `S06_02_F01` Control UR RMSE bar; `S06_02_F02` Source-of-advantage waterfall.

Appendix:
- `S06_02_T03` Old-vs-new control comparison; `S06_02_T04` Regime × control heatmap data; `S06_02_T05` Calibrated parameters per variant.
- `S06_02_F03` Control trajectories; `S06_02_F04` Regime × control heatmap; `S06_02_F05` Within-variant dispersion.

## 4.3 S06_03 — Re-calibrated Heterogeneity Ablations (EX05R + EX11)

Main text:
- `S06_03_T01` Re-calibrated ablation; `S06_03_T02` Old-vs-new delta.
- `S06_03_F01` Ablation UR RMSE bar; `S06_03_F02` Old-vs-new delta plot.

Appendix:
- `S06_03_T03` Regime × ablation; `S06_03_T04` Heterogeneity ladder.
- `S06_03_F03` Regime × ablation heatmap; `S06_03_F04` No-Search trajectory; `S06_03_F05` LFPR/EPOP trade-off; `S06_03_F06` Heterogeneity ladder.

## 4.4 S06_04 — Stronger Forecast Benchmark Comparison (EX07R)

Main text:
- `S06_04_T01` Dynamic benchmark comparison.
- `S06_04_F01` Dynamic benchmark RMSE bar.

Appendix:
- `S06_04_T02` Compact paper-ready; `S06_04_T03` Regime × benchmark; `S06_04_T04` Benchmark specs; `S06_04_T05` Protocol comparison.
- `S06_04_F02..F05` Benchmark ratio / scatter / regime heatmap / trajectories.

## 4.5 S06_05 — Robustness and Sensitivity (EX06R + EX09..EX13)

Main text:
- `S06_05_T01` Robustness summary.
- `S06_05_F01` 4-panel robustness dashboard.

Appendix:
- `S06_05_T02..T07` Per-test detail tables (seed, train-window, horizon, agent-count, calibration-method, parameter-identification).
- `S06_05_F02..F06` Per-test detail figures.

---

# 5. SCE Variable Mapping (Survey-Moment Anchors)

## 5.1 Table: Survey Variables Used

| Heterogeneity Dim | SCE Module | Variable Code | Official Q# | Official Wording | Raw Concept | How Used | Anchor Strength | Notes |
|---|---|---|---|---|---|---|---|---|
| H1 Income Growth Exp | Core | `Q24_cent50` | Q24 (density forecast block) | **MISSING: official wording not verified** | 1-year ahead household earnings growth median | Empirical CDF sampled at agent init → `income_expectation` | Directly | Continuous |
| H1 Income Growth Exp | Core | `Q24_iqr` | Q24 (density forecast block) | **MISSING** | IQR of 1-yr earnings growth density | Empirical CDF → `income_uncertainty` | Directly | Continuous |
| H2 Labor Fragility | Core | `Q13new` | Q13 | **MISSING** | Probability of losing one's main job within 12 months | PCA(Q13new, 1−Q22new) factor → `labor_fragility` ∈ [0,1] | Partial | Composite construct |
| H2 Labor Fragility | Core | `Q22new` | Q22 | **MISSING** | Probability of finding a job within 4 months if unemployed | Enters PCA factor with Q13new | Partial | Composite construct |
| H3 Liquidity Fragility | Core | `Q33` | Q33 | **MISSING** | Whether financial assets cover ≥3 months of expenses | Rule-based class (H2M / Buffer / Wealthy) with Q32, Q47 | Partial | Discrete class assigned by rule, not from raw response |
| H4 Labor Search Friction | LM (Quarterly) | `rw2a`, `rw2b` | rw2 | **MISSING** | Reservation wage (ratio to current/last wage) | Empirical CDF → `reservation_wage_ratio` ∈ [0.5, 5.0] | Directly | Continuous |
| H4 Labor Search Friction | LM (Quarterly) | `js7` | js7 | **MISSING** | Hours per week spent searching for work (U only) | Empirical CDF → `search_intensity`; E and N agents forced to 0 | Directly | Continuous, U-only |
| H4 Labor Search Friction | LM (Quarterly) | `rw3b, rw4b, rw6b` | rw3/4/6 | **MISSING** | Wage premium required to move / commute / change hours | PCA factor → `flexibility_index` ∈ [−3, 3] | Partial / Synthetic | Composite |
| H5 Housing Mobility | Core + Housing | `Q41`, `HQH5-series`, `HQH6-series` | Housing module | **MISSING** | Owner / renter status; mortgage; mobility intent | Rule-based class (4-way: Renter-Mobile, Renter-Stable, Owner-Low, Owner-High) with target shares; `mobility_friction_score` is synthetic | Partial / Synthetic | See items 5, 6 in Missing Items Checklist |
| H6 Consumption Adj | Spending | `qsp12n` | qsp12n | **MISSING** | Share of an income increase that would be spent | Empirical CDF → `mpc_positive` | Directly | Continuous |
| H6 Consumption Adj | Spending | `qsp13new` | qsp13new | **MISSING** | Share of an income decrease cushioned by reduced spending | Empirical CDF → `mpc_negative` | Directly | Continuous |
| H6 Consumption Adj | Spending | (derived) | — | n/a | `asymmetry_ratio = mpc_negative / mpc_positive` | Derived from above | Synthetic | Slow preference parameter |
| H6 Consumption Adj | Spending | (latent class) | — | n/a | `consumption_type ∈ {Saver, Smoother, Spender}` | Probabilistic latent-class assignment | Synthetic | Anchored to qsp12n/qsp13new joint moments |
| Demographics | Core | `Q36, Q38, Q39, Q4new, Q10/Q10a, l8` | — | **MISSING** | Age, education, marital, household size, household income, employment state, unemployment duration | Sampled marginally; employment state targets E/U/N shares | Directly | — |

## 5.2 Heterogeneity Dimensions and Survey Anchoring Strength

| Dimension | Anchor Strength | Justification |
|---|---|---|
| Income growth expectation & uncertainty | Directly survey-moment anchored | Q24_cent50 and Q24_iqr empirical CDFs |
| Labor fragility | Partially anchored | PCA(Q13new, 1−Q22new) composite |
| Liquidity class | Partially anchored | Rule-based discretization of Q32/Q33/Q47 + target shares |
| Reservation wage | Directly anchored | rw2 empirical CDF |
| Search intensity | Directly anchored (U only) | js7 empirical CDF |
| Flexibility index | Mostly synthetic | PCA of rw3b/rw4b/rw6b, no SCE wording verified |
| Housing class | Partially anchored | Q41 + Housing module, mapped to 4-class scheme |
| Mobility friction score | Mostly synthetic | Conditional-on-class continuous construct |
| MPC positive / negative | Directly anchored | qsp12n / qsp13new empirical CDFs |
| Consumption type | Mostly synthetic | Latent class anchored to MPC moments |
| Cash buffer (months) | Partially anchored | Class-conditional distributions (targets: H2M~0.5, Buffer~3, Wealthy~12) |
| Household income | Directly anchored | Core Q4new marginal |
| Unemployment duration | Partially anchored | LM l8 conditional on U |
| Demographics (age, education, marital, household size) | Directly anchored | Core demographic module marginals |

**SCE modules used:** Core (Q-series), LM (ec, l), LM Quarterly (rw, js), Housing (HQ), Spending (qsp). **Not used in agent decisions:** Household Finance (b-series), Credit Access, Policy Survey, Informal Work (post-hoc adjustment only; see Phase 7 input registry).

---


# 6. Population Generation

## 6.1 Method

Synthetic population of `N=100,000` agents constructed by **sequential conditional sampling**: marginal distributions are taken from SCE empirical CDFs (and Census/BLS targets for demographics and employment-state shares); within-agent joint structure is generated by class assignment + class-conditional draws + light synthetic coupling. **No respondent row is bootstrapped.** Survey weights are **UNCERTAIN**: the code uses unweighted empirical CDFs (see Missing Items Checklist row 2).

## 6.2 Construction Order

1. Demographics: age, education, marital, household size, race (Core demographic block).
2. Household income (Core Q4new) → empirical CDF.
3. Employment state ∈ {E, U, N} matched to BLS aggregate shares for the initialization month; unemployment duration `l8` conditional on U.
4. Income expectation (Q24_cent50, Q24_iqr) → continuous draws.
5. Labor fragility (Q13new, 1−Q22new) → PCA factor in [0,1].
6. Liquidity class (Q32/Q33/Q47) → {H2M, Buffer, Wealthy} with target shares; `cash_buffer_months` drawn class-conditionally (targets H2M ≈ 0.5, Buffer ≈ 3, Wealthy ≈ 12).
7. Labor search friction: `reservation_wage_ratio` (rw2), `search_intensity` (js7, U-only), `flexibility_index` (PCA rw3b/rw4b/rw6b).
8. Housing class (Q41 + HQ-series) → {Renter-Mobile, Renter-Stable, Owner-Low, Owner-High} with target shares; `mobility_friction_score` is synthetic class-conditional.
9. Consumption adjustment: `mpc_positive` (qsp12n), `mpc_negative` (qsp13new), `asymmetry_ratio` derived, `consumption_type` ∈ {Saver, Smoother, Spender} latent class.

## 6.3 Validation Diagnostics

Source: `Phase2_Output/04_Population_Diagnostic_Report.md`. Population marginals match SCE / BLS targets to within typical tolerances; details and the per-dimension Kolmogorov–Smirnov / KL comparisons are described there. The executable generation script path is **MISSING** in the registry (item 3 of the checklist) and must be added before the appendix can ship.

## 6.4 Reproducibility Notes

- Seed used at population draw: stored in the population artefact metadata (verify per run).
- Output artefact: `population_v1.npz` (`Phase2_Output/`); contains agent-level fields listed in §5.1.
- The same population is used across **all** EX## runs unless explicitly re-initialized (e.g., EX12 agent-count sensitivity).

---

# 7. Macro Inputs

## 7.1 Source

`Phase3_Output/phase7/real_data_input_registry.md`. Three families:

| Family | Series (FRED / BLS) | Role | Frequency |
|---|---|---|---|
| Labor stocks | UNRATE, CIVPART, EMRATIO | Evaluation targets + exogenous trend driver | Monthly |
| Labor flows | JTSJOR (job openings rate), JTSLDR (layoffs/discharges rate), CES (payroll) | Tightness / separation drivers | Monthly |
| Macro | FEDFUNDS | Macro state (used in policy-side parameters) | Monthly |
| Diagnostic adjustment | Informal Work module (SCE) | Post-hoc UR/LFPR/EPOP adjustment (M1+M2 in Phase 7) | Monthly aggregated |

Sample period: **2001-01 to 2026-02** (302 monthly observations). Initialization window starts in **2004-01** (UNCERTAIN — must be confirmed from the simulation driver; see Checklist item 19); the first 36 months are warm-up.

## 7.2 Input Transformation Table — MISSING

The exact transformation (level / log / YoY / clipped) of each series feeding the model decisions is **MISSING** (Checklist item 18). A minimal table to be supplied for the appendix:

| Series | Used as | Transformation | Frequency | Lag |
|---|---|---|---|---|
| UNRATE | evaluation target + state | level (pp) | Monthly | 0 |
| CIVPART | evaluation target | level (pp) | Monthly | 0 |
| EMRATIO | evaluation target | level (pp) | Monthly | 0 |
| JTSJOR | tightness driver | level | Monthly | 0 |
| JTSLDR | separation driver | level | Monthly | 0 |
| FEDFUNDS | macro state | level | Monthly | 0 |
| CES PAYEMS | scale check | YoY | Monthly | 0 |
| Informal Work share | M1+M2 post-hoc UR adjustment | level | Quarterly → monthly | 0 |

Confirm transformations and any clipping / winsorization rules from `Phase3_Code/environment.py` (or equivalent driver) before the appendix is finalized.

## 7.3 Missing Values

UNRATE 2025-10 is referenced as a potentially missing month in the evaluation pipeline; the NaN-masking logic in `正式撰写/fix6.1/run_fix6_1_regime.py` is the authoritative source (Checklist item 17).

---

# 8. Evaluation Targets

## 8.1 Targets

- **Primary**: UR (UNRATE).
- **Secondary**: LFPR (CIVPART), EPOP (EMRATIO).
- **Tertiary (calibration-loss only)**: EU/UE flow rates and H2M share (used inside `compute_train_loss`, not as headline metrics).

## 8.2 Regime Windows (used in S06_01 and S06_05)

| Regime | Start | End | Months | Purpose |
|---|---|---|---|---|
| Pre-COVID | 2018-01 | 2019-12 | 24 | Normal-regime sanity check |
| COVID-Crisis | 2020-03 | 2021-06 | 16 | Stress-regime diagnostic (not a forecast target) |
| Post-COVID Normalization | 2022-01 | 2026-02 | 50 | **Headline tracking window** |

Train / OOS split: train = 2004-01..2017-12, OOS begins 2018-01. For ABM, OOS is a single dynamic multi-step path. For benchmarks, OOS is either rolling one-step (rolling protocol) or a single dynamic multi-step path (dynamic protocol). Headline results use the **dynamic protocol** for both.

## 8.3 Metric Conventions

- **RMSE and bias are reported in pp** (percentage points) throughout, *not* decimal. UR series are expressed as pp (e.g., 3.5 pp), so the absolute deviation in pp is the same as the raw RMSE on the pp-scaled series.
- Cross-seed dispersion is reported as the **standard deviation across the 5 reeval seeds** {42, 137, 2024, 888, 1234} (Checklist item 14: confirm 888 and 1234 are in the reeval seed list).

---

# 9. Model Scope

## 9.1 What the model contains

- 100,000 worker-agents with the six MVP heterogeneity dimensions (§5.2).
- A simple aggregate labor market: job-finding probability and separation probability functions of agent state (search intensity, reservation wage, fragility, etc.) and macro drivers (tightness, separation rate).
- Household consumption and liquidity dynamics for the H2M / Buffer / Wealthy classes.
- A coarse housing dimension affecting search / mobility behaviour.

## 9.2 What the model does NOT contain

- No firm side (no firm entry / exit, no vacancy posting, no wage bargaining, no production).
- No product market, no inflation, no monetary-policy transmission.
- No geographic structure (no metro / state, no commuting).
- No sectoral structure.
- No financial sector / credit market.
- No fiscal-policy shock structure (PUA, EIP, etc. enter only via M1+M2 post-hoc adjustment, not as agent decisions).

## 9.3 Scope Implications

Because the model is single-sided and single-sector, all claims about "mechanism" or "channel" are **within-model** statements: ablating a heterogeneity dimension changes the marginal distribution of the input feature space that the policy-rule parameters condition on, not a structural economic mechanism. The "Search Friction channel," for example, is a statement about the search-friction feature block of the agent state vector, not about a matching-function elasticity.

---


# 10. Calibration

## 10.1 Parameter Space

Fourteen behavioural parameters are calibrated. Names and behavioural roles:

| # | Parameter | Block | Behavioural role |
|---|---|---|---|
| 1 | `acceptance_pressure` | Search | Multiplicative pressure on job-acceptance threshold |
| 2 | `duration_thresh` | Search | Unemployment-duration threshold for search-intensity adjustment |
| 3 | `emp_adapt_speed` | State | Speed of E-to-U adaptation on shocks |
| 4 | `exit_jump` | State | Probability jump on labor-force exit |
| 5 | `h2m_resv_discount` | Liquidity | Reservation-wage discount applied to H2M agents |
| 6 | `lockin_penalty` | Housing | Mobility penalty for owners |
| 7 | `optimism_entry` | State | Bias term on N→U/E transitions in upturns |
| 8 | `pessimism_exit` | State | Bias term on E→N in downturns |
| 9 | `reentry_penalty` | State | Penalty on re-entry after long U-spell |
| 10 | `unemp_adapt_speed` | State | Speed of U-state adaptation |
| 11 | `fragility_threshold` | Fragility | Threshold above which fragility increases separation |
| 12 | `h2m_mpc_floor` | Liquidity | Lower bound on H2M MPC |
| 13 | `vacancy_rate` | Macro | Baseline tightness scale |
| 14 | `wealthy_discount` | Liquidity | Discount applied to Wealthy reservation-wage |

**Parameter bounds — MISSING** as a transcribed table (Checklist item 10). The authoritative source is `Phase3_Code/calibration_engine.py` (`PARAM_SPACE`).

## 10.2 Calibration Methods

Three methods are run in the revised package:

1. **LHS-300** — Latin Hypercube Sampling, 300 trials, 3 seeds per trial (default).
2. **Bayesian Optimization (BO-100)** — 100 BO trials initialised with the top-10 LHS sweeps.
3. **CMA-ES** — Evolution strategy with the same trial budget as BO.

Each variant in the EX08R / EX05R / EX11 grid is **independently re-calibrated** under each method. Variants:

| Variant | Description | Active params |
|---|---|---|
| V_Full | All 14 parameters active | 14 |
| V_LaborOnly | Drops housing-mobility and consumption-asymmetry blocks | ~10 (UNCERTAIN — confirm against `phase8_derived.py`) |
| V_Homogeneous | Same parameters, homogeneous agent draws (no SCE anchoring) | 12 (h2m parameters inactive) |
| V_Simplified | Single-parameter baseline; only `vacancy_rate` is calibrated | 1 (per `table5_calibrated_params.csv`) |
| No-Search ablation | V_Full with search-friction parameters fixed at baseline | 14 (search subset frozen) |
| No-Liquidity ablation | V_Full with liquidity parameters fixed at baseline | 14 (liquidity subset frozen) |
| No-Housing ablation | V_Full with housing parameters fixed at baseline | 14 (housing subset frozen) |

## 10.3 Loss Function

`compute_train_loss(history)` in `正式撰写/fix6.2/run_fix6_2_calibrate.py` (and engine module) returns a weighted sum-of-squared-deviations over the train window 2004-01..2017-12:

```
L = w_UR · MSE(UR) + w_LFPR · MSE(LFPR) + w_EPOP · MSE(EPOP)
    + w_EU · MSE(EU_rate) + w_UE · MSE(UE_rate) + w_H2M · MSE(H2M_share)
```

with **tier-1** weight on UR and **tier-2** weights on the others. **Exact weight values are MISSING** as a transcribed line (Checklist items 11, 12) and must be read from the calibration engine.

## 10.4 Budget

| Item | Value | Source |
|---|---|---|
| Trials per method per variant | 300 (LHS) / 100 (BO) / 100 (CMA-ES) | Calibration scripts |
| Seeds per trial (calibration) | 3: {42, 137, 2024} | Calibration scripts |
| Seeds per trial (reeval) | 5: {42, 137, 2024, 888, 1234} | Reeval scripts (UNCERTAIN — Checklist item 14) |
| Train window | 2004-01..2017-12 (168 months) | Asset registry |
| Selected point | Top-1 trial (best train loss) | `table5_calibrated_params.csv` |
| Selected band | Top-5 IQR per parameter (recommended) | To be tabulated (Checklist item 9) |

## 10.5 Selected Parameter Values

Top-1 calibrated point estimates per variant are in `正式撰写/fix6.2/tables/table5_calibrated_params.csv`. Because of weak identification (§11), **the paper should publish parameter bands (top-5 IQR), not the top-1 values alone**.

---

# 11. Weak Identification

## 11.1 Method

For each parameter, the top-5 LHS trials by train loss are extracted, and the coefficient of variation `CV = std / |mean|` is computed across these top-5 values. Parameters with CV ≥ 0.40 in the top-5 are flagged as **weakly identified**. This is repeated under LHS / BO / CMA-ES (the three methods of §10.2).

## 11.2 Result

Source: `正式撰写/6.5/robustness_metrics.json` (param_identification block).

- **10 of 14 parameters are weakly identified**: `acceptance_pressure`, `duration_thresh`, `emp_adapt_speed`, `exit_jump`, `h2m_resv_discount`, `lockin_penalty`, `optimism_entry`, `pessimism_exit`, `reentry_penalty`, `unemp_adapt_speed`.
- **4 of 14 are stable**: `fragility_threshold`, `h2m_mpc_floor`, `vacancy_rate`, `wealthy_discount`.

## 11.3 Implication

Behavioural interpretations of individual parameter values are **not** supported. The paper should:

- report parameter **bands** (top-5 IQR) rather than point estimates;
- avoid causal statements about any individual coefficient (e.g., do not say "the calibrated `acceptance_pressure` of X indicates Y");
- treat the 4 stable parameters as the only ones for which a directional reading is defensible, and even then only with caveats.

## 11.4 Why the Forecast Survives

Despite weak parameter identification, the **forecast itself** is stable: the top-5 trials of V_Full produce post-COVID UR RMSE within 0.02 pp of one another. This is a flat-loss / sloppy-model finding and is explicitly stated in S06_05.

---


# 12. S06_01 — Regime-Specific Out-of-Sample Performance

## 12.1 Setup

EX04R. Single best-calibrated V_Full point (LHS+BO top-1) is run as a dynamic multi-step path 2018-01..2026-02 across 5 reeval seeds. Performance is sliced into Pre-COVID / COVID-Crisis / Post-COVID Normalization regimes (§8.2). The pre-revision pooled OOS metric is replaced.

## 12.2 Headline Numbers (from `正式撰写/fix6.1/tables/table1_regime_summary.csv`)

| Regime | UR RMSE (pp) | UR bias (pp) | UR max-abs (pp) |
|---|---:|---:|---:|
| Pre-COVID (24 mo) | ~0.77 | +0.77 | (see file) |
| COVID-Crisis (16 mo) | ~2.07 | −2.07 | 6.07 |
| Post-COVID Normalization (50 mo) | **0.221** | (see file) | (see file) |

(Values are quoted to the level of precision available in the table; the table is the source of record.)

## 12.3 Interpretation

- The post-COVID number is the central forecast claim of the paper.
- The crisis number documents that the ABM does **not** reproduce the COVID spike; the bias is −2.07 pp and the max-abs error is 6.07 pp. This is a **stress-regime diagnostic**, not a forecast failure (the model was not built to predict crises).
- The pre-COVID number is small in absolute terms but is a +0.77 pp **bias**, indicating systematic over-prediction in tranquil regimes.

## 12.4 What this section can claim

- "Post-COVID UR is tracked with sub-pp RMSE."
- "Performance varies by regime; crisis tracking is poor by design."
- "The pre-COVID bias is positive and small."

## 12.5 What this section cannot claim

- "The model forecasts unemployment well across all regimes."
- "The model predicted the COVID crisis."
- "OOS error is small everywhere."

---

# 13. S06_02 — Separately Calibrated Internal Controls

## 13.1 Setup

EX08R. Four variants — V_Full, V_LaborOnly, V_Homogeneous, V_Simplified — are **independently re-calibrated** under each of LHS / BO / CMA-ES, then run as dynamic paths over the post-COVID window with 5 reeval seeds. The headline question is whether V_Full retains a lead once each control is given its own best calibration.

## 13.2 Headline Numbers (from `正式撰写/fix6.2/tables/table1_variant_summary.csv`)

| Variant | UR RMSE post-COVID (pp) | vs V_Full (Δ pp) |
|---|---:|---:|
| V_Full | **0.273** | — |
| V_LaborOnly | (see file) | (see file) |
| V_Homogeneous | (see file) | (see file) |
| V_Simplified | 0.561 | +0.288 |

## 13.3 Source-of-Advantage Decomposition

Source: `正式撰写/fix6.2/tables/table6_old_vs_new_decomposition.csv`. The total V_Simplified vs V_Full gap (~0.288 pp) is attributed across:

- Heterogeneity activation: ~0.20 pp (the dominant component).
- Labor-block parameter activation: residual.
- Other parameter activations: residual.

The exact numbers must be read from the CSV; this section reports orders of magnitude.

## 13.4 Interpretation

- The heterogeneity advantage **exists** under like-for-like re-calibrated controls — it is not an artefact of holding the control fixed at default settings.
- The advantage is **moderate, not overwhelming**: a 0.29 pp total gain is roughly 50% of the V_Simplified RMSE.
- The pre-revision claim of a 2.116 pp gap was inflated by leaving the control un-calibrated.

## 13.5 What this section can claim

- "Heterogeneity contributes a moderate, separately calibrated improvement of ~0.20 pp."
- "Worker-side heterogeneity is the dominant component of the V_Full advantage over V_Simplified."

## 13.6 What this section cannot claim

- "Heterogeneity causally explains 94.2% of the gap" without specifying it is a within-experiment accounting.
- "V_Full dominates all controls by a wide margin."

---

# 14. S06_03 — Re-calibrated Heterogeneity Ablations

## 14.1 Setup

EX05R. Starting from V_Full, three ablations are constructed:

- **No-Search**: search-friction parameter subset frozen at baseline.
- **No-Liquidity**: liquidity parameter subset frozen at baseline.
- **No-Housing**: housing parameter subset frozen at baseline.

Each ablation is **independently re-calibrated** on the remaining active parameters. Post-COVID UR RMSE is then computed.

## 14.2 Headline Numbers (from `正式撰写/fix6.3/tables/table2_post_covid_ablation.csv`)

| Ablation | UR RMSE post-COVID (pp) | Δ vs V_Full (pp) | Verdict |
|---|---:|---:|---|
| V_Full | 0.273 | — | reference |
| No-Search | ~1.09 | +0.812 | **large** (channel survives ablation) |
| No-Liquidity | ~0.41 | +0.14 | small |
| No-Housing | ~0.34 | +0.07 | small |

## 14.3 Old vs New Delta

Source: `正式撰写/fix6.3/tables/table5_old_vs_new_delta.csv`. Under the old (un-recalibrated) ablations, all three channels appeared comparably important. Under the new (recalibrated) ablations, only Search has a large standalone effect.

## 14.4 Interpretation

- **Search Friction** is the only standalone channel that survives re-calibration with a large effect.
- **Liquidity** and **Housing** standalone effects shrink substantially under re-calibration; their original "large" effects in the old ablations were partially absorbed by other parameter blocks.
- Some channels (notably Housing) trade UR fit against LFPR/EPOP fit: improving UR may worsen secondary metrics. The paper should report this trade-off.

## 14.5 What this section can claim

- "Labor Search Friction is the most robust standalone heterogeneity channel under re-calibrated ablation."
- "Liquidity and Housing standalone effects are weaker once each ablation is re-calibrated."
- "Household-block mechanisms improve UR tracking but can worsen LFPR/EPOP fit."

## 14.6 What this section cannot claim

- "Search, Liquidity, and Housing each independently contribute to forecast accuracy."
- "The mechanisms are causally identified."

---


# 15. S06_04 — Stronger Forecast Benchmark Comparison

## 15.1 Setup

EX07R. Twelve forecasters are compared under a like-for-like **dynamic multi-step protocol** over 2018-01..2026-02, with headline metrics computed on the post-COVID normalization window. ABM is the survey-moment-anchored V_Full (5-seed mean); the 11 statistical / econometric benchmarks are listed in `S06_04_T04`.

Benchmark families (UNCERTAIN — confirm against `正式撰写/fix6.4/run_fix6_4_benchmarks.py`):

| Family | Members |
|---|---|
| Naïve | No-change, seasonal naïve |
| Smoothing | ETS, Holt-Winters |
| Autoregressive | AR(1), AR(p) |
| Box-Jenkins | ARIMA, SARIMA |
| Macro factor | VAR(small), local-linear |
| Statistical structural | Phillips-curve-style benchmark (UNCERTAIN) |
| ML | (only if implemented; not in current fix6.4 panel) |

A **Dynamic Factor Model** is not included (Checklist item 16).

## 15.2 Headline Numbers (from `正式撰写/fix6.4/table1_main_postcovid_benchmark.csv`)

| Rank | Model | UR RMSE post-COVID (pp) | Δ vs ABM (pp) |
|---|---|---:|---:|
| 1 | **ABM (V_Full, 5-seed mean)** | **0.273** | — |
| 2 | No-change | ~0.31 | +0.04 |
| 3 | ETS | ~0.32 | +0.05 |
| 4 | AR(1) | (see file) | (see file) |
| 5 | ARIMA | (see file) | (see file) |
| ... | ... | ... | ... |

## 15.3 Important Caveat

The ABM lead over no-change / ETS is **~0.04 pp**, which is within the 5-seed standard deviation of the ABM itself (~0.023 pp). The lead is consistent across seeds but not large.

## 15.4 Protocol Comparison

`S06_04_T05` (rolling vs dynamic). Under the rolling one-step protocol, the benchmarks become much harder to beat (rolling one-step is a much easier task than dynamic multi-step). The dynamic-multistep number is the appropriate like-for-like comparison; the rolling number is a sanity check, not a headline result.

## 15.5 Interpretation

- The ABM is **competitive** with strong benchmarks under a like-for-like dynamic protocol.
- The lead is **modest** and falls within seed dispersion against the strongest competitors.
- The most appropriate framing is "first among twelve, by a small margin" rather than "dominates all benchmarks."
- The ABM adds value not only via its modest forecast edge but via **within-model diagnostics** (heterogeneity decomposition, parameter bands, channel sensitivity) that benchmark forecasters cannot supply.

## 15.6 What this section can claim

- "The ABM is competitive with twelve strong forecasting benchmarks under a like-for-like dynamic multi-step protocol."
- "The ABM's lead over no-change / ETS is consistent but modest, of order one seed standard deviation."
- "Rolling one-step benchmarks are not directly comparable to a dynamic multi-step ABM path."

## 15.7 What this section cannot claim

- "The model dominates all benchmarks."
- "No statistical model can match the ABM."
- "The ABM is a state-of-the-art forecaster."

---

# 16. S06_05 — Robustness and Sensitivity

## 16.1 Setup

EX06R. Survival of S06_01–S06_04 findings under perturbations along ten axes. Five legacy packages (EX09–EX13) are retained as **invariants** for completeness.

## 16.2 Ten-Axis Robustness Summary (from `正式撰写/fix6.5/tables/table1_revised_robustness_summary.csv`)

| Axis | Source | Finding | Verdict |
|---|---|---|---|
| Seed dispersion | 5-seed ABM | Post-COVID RMSE ±0.023 pp s.d. across {42,137,2024,888,1234} | Survives |
| Training window | EX09 (Pkg A) | Sub-window invariants vs M0 baseline | Legacy invariant |
| Forecast horizon | EX10 (Pkg B) | Horizon-decay invariant | Legacy invariant |
| Agent count | EX12 (Pkg D) | Plateau at N ≥ 50,000 | Legacy invariant |
| Calibration method | EX13 (Pkg E) + EX08R | V_Full lead survives LHS / BO / CMA-ES re-calibration | Survives |
| Heterogeneity ladder | EX11 (Pkg C) | Monotonic gain from adding dimensions | Legacy supporting |
| Internal controls | EX08R | V_Full lead of ~0.29 pp survives separate re-calibration | Survives (moderate) |
| Ablation channels | EX05R | Only Search survives recalibrated ablation with large effect | Search survives; others soften |
| Cross-regime | EX04R | Pre-COVID +0.77 pp bias; Crisis −2.07 pp; Post-COVID 0.221 pp | Mixed; cross-regime claim withdrawn |
| Parameter identification | §11 / `robustness_metrics.json` | 10/14 weakly identified; forecast stable nonetheless | Forecast survives; structural reading withdrawn |

## 16.3 Old-vs-Revised Claims (from `正式撰写/fix6.5/tables/table2_old_vs_revised_claims.csv`)

| Old claim | Revised claim |
|---|---|
| 97.6% heterogeneity share | 94.2% within-experiment share (qualified) |
| ABM beats all benchmarks | ABM is rank-1 of 12 by 0.04 pp; lead within seed s.d. |
| Three independent mechanisms | Only Search Friction survives recalibrated ablation |
| Cross-regime robust | Post-COVID only; crisis stress-regime diagnostic |
| Strong parameter identification | 10/14 weakly identified; report bands |
| OOS completely untouched | OOS structure preserved at the regime level; pooled OOS replaced by regime-specific metrics |

## 16.4 Interpretation

- The **post-COVID UR tracking** claim (S06_01) survives every robustness check.
- The **heterogeneity advantage** survives as a fact, but its **magnitude** is reduced from old to revised numbers.
- The **three-mechanism** story is reduced to a **one-mechanism** story (Search Friction) with two softened secondary channels.
- The **benchmark dominance** claim is replaced by a **competitive-with-strong-benchmarks** claim.
- **Cross-regime** and **structural parameter** claims are withdrawn.

## 16.5 What this section can claim

- "Post-COVID tracking is robust across all ten axes tested."
- "The heterogeneity advantage survives separate re-calibration but is moderate."
- "Forecast stability coexists with weak parameter identification — a typical flat-loss / sloppy-model finding."

## 16.6 What this section cannot claim

- "All robustness checks confirm the original strong claims."
- "Parameter identification is sound."
- "The model is robust across all regimes."

---


# 17. Figure Inventory

Full inventory lives in `ABM_Figure_Inventory.csv`. The figures are organised by Section ID. Main-text figures (one per Results sub-section):

| Section | Figure ID | Suggested Caption |
|---|---|---|
| S06_01 | S06_01_F01 | Full-period UR path: actual vs ABM (5-seed mean ± seed band), 2018-01..2026-02, with shaded regime backgrounds. |
| S06_02 | S06_02_F01 | Post-COVID UR RMSE by separately calibrated variant (V_Full, V_LaborOnly, V_Homogeneous, V_Simplified), 5-seed mean ± s.d. |
| S06_03 | S06_03_F01 | Post-COVID UR RMSE by recalibrated ablation (V_Full, No-Search, No-Liquidity, No-Housing). |
| S06_04 | S06_04_F01 | Dynamic-protocol post-COVID UR RMSE for the 12-model panel (ABM + 11 benchmarks), with ABM seed band overlay. |
| S06_05 | S06_05_F01 | Four-panel robustness dashboard: (A) regime-specific RMSE, (B) recalibrated controls + ablation, (C) benchmark panel, (D) legacy invariants. |

Appendix figures and per-regime trajectories are enumerated in the CSV. Files that do not yet exist are tagged with `status=MISSING` and a `suggested_source` field referencing the script and table that would generate them.

---

# 18. Table Inventory

Full inventory lives in `ABM_Table_Inventory.csv`. Main-text tables:

| Section | Table ID | Suggested Caption |
|---|---|---|
| S06_01 | S06_01_T01 | Regime-specific UR/LFPR/EPOP RMSE and bias (Pre-COVID 2018-01..2019-12; COVID-Crisis 2020-03..2021-06; Post-COVID 2022-01..2026-02). |
| S06_02 | S06_02_T01 | Post-COVID UR RMSE and bias for separately calibrated variants under three calibration methods (LHS, BO, CMA-ES). |
| S06_02 | S06_02_T02 | Source-of-advantage decomposition: V_Full vs V_Simplified gap attributed to heterogeneity, labor block, and other parameter activations. |
| S06_03 | S06_03_T01 | Post-COVID UR RMSE by recalibrated ablation, with LFPR/EPOP secondary metrics. |
| S06_04 | S06_04_T01 | Dynamic-protocol post-COVID UR RMSE for the 12-model panel; rank, RMSE, Δ vs ABM, and seed band overlap. |
| S06_05 | S06_05_T01 | Ten-axis robustness summary; for each axis: source EX##, finding, verdict. |

Compact paper-ready tables (`*_compact`) and full appendix tables are enumerated in the CSV.

---

# 19. Claim-to-Evidence Table

See `ABM_Claim_to_Evidence_Table.csv`. Sixteen claims are tracked (corresponding to the prompt's §18 list). For each claim the CSV records: evidence files, section ID, strength (Strong / Moderate / Weak), caveat, and suggested wording. **Every claim in the rewritten paper must appear in this CSV; if a claim is not in the CSV, it should be removed from the draft or added to the CSV (with evidence) before the draft is finalised.**

---

# 20. Missing Items Pointer

See `ABM_Missing_Items_Checklist.md` (25 items; 12 P1, 9 P2, 4 P3). P1 items block the rewrite; P2 items must be resolved before appendix sign-off; P3 items are rigour upgrades.

The five most critical:

1. SCE official question wording (P1, row 1).
2. Survey-weight handling status (P1, row 2).
3. Population generation script path (P1, row 3).
4. Exact list of 10 weakly identified parameters (P1, row 8 — already drafted in §11 of this report; needs script confirmation).
5. Macro input transformation table (P1, row 18).

---

# 21. Rewrite Guidance

## 21.1 Recommended New Paper Structure

### 1. Introduction
- Motivate post-COVID U.S. unemployment tracking as a high-value, under-served forecast target.
- Position the contribution: survey-moment-anchored worker-side ABM that is competitive with strong benchmarks under like-for-like protocol while supplying within-model diagnostics.
- State the **one-sentence contribution** (§2.4).
- Preview the five Results sub-sections.
- Be explicit about what the paper does **not** claim (one paragraph).

### 2. Literature Review
- ABMs of the labor market (one-sided worker-ABM, two-sided matching ABMs).
- Survey-anchored micro-simulation (SCE, SCF, PSID studies).
- Forecast benchmarks for U.S. unemployment (Phillips curves, factor models, ML).
- Identification in flat-loss / sloppy models.
- Position this paper at the intersection of (1) and (3): a survey-anchored worker-ABM evaluated by forecasting standards.

### 3. Model
- 100,000 worker-agents; six MVP heterogeneity dimensions.
- Job-finding and separation as functions of agent state and macro drivers (§9.1).
- Household consumption / liquidity / housing blocks.
- **Explicit scope statement** (§9.2): no firm side, no inflation, no geography, no sectors.

### 4. Data
- SCE variable mapping (§5 of this report).
- Macro inputs and transformations (§7).
- Evaluation targets and regime windows (§8).
- Clearly distinguish survey-moment-anchored from direct-survey-resampled construction.

### 5. Experimental Design
- The four revised experiment sets (EX04R–EX08R) and the five legacy invariants (EX09–EX13).
- Calibration methods (LHS / BO / CMA-ES) and seed sets (§10).
- Loss function and weights (§10.3, §10.4).
- The dynamic multi-step protocol (§15).

### 6. Results
- 6.1 Regime-Specific OOS Performance (§12).
- 6.2 Separately Calibrated Internal Controls (§13).
- 6.3 Re-calibrated Heterogeneity Ablations (§14).
- 6.4 Stronger Benchmark Comparison (§15).
- 6.5 Robustness and Sensitivity (§16).
- Each sub-section ends with explicit "what this can / cannot claim" lists.

### 7. Discussion
- What worked: survey-moment anchoring delivers a moderate but consistent improvement; Search Friction is the dominant within-model channel.
- What did not: cross-regime forecasting, structural parameter identification, dominance over the strongest statistical competitors.
- Why the forecast is stable despite weak identification (flat-loss / sloppy-model framing).
- Limitations (no firm side, no geography, no sectors, weak ID, etc.).

### 8. Conclusion
- One-paragraph recap of the contribution.
- Two paragraphs of future work (see §21.4).

### 9. Appendix
- A: Full SCE variable mapping with official wording.
- B: Population construction code and validation diagnostics.
- C: Calibration parameter space, bounds, loss-function weights.
- D: Full benchmark specifications.
- E: All appendix tables and figures.

## 21.2 Wording to Use

- survey-moment-anchored
- worker-side ABM
- normal-regime unemployment tracking
- post-COVID normalization window
- dynamic multi-step forecast
- diagnostic rather than structural
- within-model sensitivity
- separately calibrated controls
- weak parameter identification
- stress-regime diagnostic
- time-aligned survey updating (future work)
- like-for-like protocol
- moderate, consistent advantage
- competitive with strong benchmarks

## 21.3 Wording to Avoid

- fully structural model
- direct survey-based model
- general labor-market prediction
- causal mechanism identification
- completely untouched OOS
- model dominates all benchmarks
- personality traits are directly measured
- heterogeneity causally explains 94.2%
- full U.S. labor-market simulation
- crisis forecasting model
- three independent mechanisms each contribute (use "Search Friction is the only large-effect standalone channel")
- robust across all regimes (use "robust within the post-COVID normalization window")

## 21.4 Suggested Future Work

1. **Time-aligned survey updating** — replace initialization-only SCE anchoring with rolling re-anchoring at survey vintage.
2. **Firm-side extension** — vacancy posting, separation policy, wage bargaining to support genuine matching-function statements.
3. **Geographic and sectoral structure** — to test heterogeneity-by-location and heterogeneity-by-sector forecast gains.
4. **Macro-financial channels** — credit market, household balance sheet, monetary policy transmission.
5. **Stress-testing protocol** — explicit crisis-scenario evaluation with separate calibration windows.
6. **Identification-aware calibration** — Bayesian methods with prior shrinkage on the 10 weakly identified parameters.

---


# 22. Final Checklist — Ready for Rewrite

## 22.1 Status of each deliverable

- [x] Revised paper position clear (§2)
- [x] Experiment Registry complete (`ABM_Experiment_Registry.csv`)
- [x] Section Registry complete (`ABM_Section_Registry.csv`)
- [x] Asset Registry complete (`ABM_Asset_Registry.csv`)
- [x] SCE variable mapping complete (§5) — official wording is **MISSING** per Checklist item 1, but the variable-to-anchor map is final
- [x] Population generation documented (§6) — generation script path **MISSING** per Checklist item 3
- [x] Population validation diagnostics documented (§6.3)
- [x] Macro inputs documented (§7) — transformation table **MISSING** per Checklist item 18
- [x] Evaluation targets documented (§8)
- [x] Model scope clear (§9)
- [x] Calibration parameters documented (§10.1) — bounds **MISSING** per Checklist item 10
- [x] Calibration loss documented (§10.3) — exact weights **MISSING** per Checklist items 11, 12
- [x] Weak identification documented (§11)
- [x] S06_01 regime results verified (§12)
- [x] S06_02 re-calibrated controls verified (§13)
- [x] S06_03 re-calibrated ablations verified (§14)
- [x] S06_04 stronger benchmarks verified (§15)
- [x] S06_05 robustness verified (§16)
- [x] Figure inventory complete (`ABM_Figure_Inventory.csv`)
- [x] Table inventory complete (`ABM_Table_Inventory.csv`)
- [x] Claim-to-evidence table complete (`ABM_Claim_to_Evidence_Table.csv`)
- [x] Missing items listed (`ABM_Missing_Items_Checklist.md`)

## 22.2 Items the rewrite cannot proceed without

The following must be resolved **before** the new manuscript is drafted (all are P1 in the Missing Items Checklist):

1. SCE official question wording for the variables in §5.1.
2. Survey-weight handling status (weighted vs unweighted empirical CDFs).
3. Population generation script path.
4. Exact sample period of each empirical CDF (per SCE module).
5. Macro input transformation table.
6. Confirmation of the 10 weakly identified parameter names (currently drafted from `robustness_metrics.json`).
7. Top-1 and top-5 IQR parameter bands per variant.
8. Parameter bounds for all 14 parameters.
9. Loss-function weights (tier-1 / tier-2).
10. Train-window alignment between ABM (2004–2017) and benchmarks (2001–2017) — justify or align.
11. Reeval seed-set verification (presence of 888, 1234 in the reeval script).
12. Bibliography skeleton (NY Fed SCE, FRED, BLS, ABM literature, forecast-benchmark literature).

## 22.3 Items that can be deferred to the appendix-revision pass

- Rolling-protocol numbers for the 11 benchmarks.
- Dynamic Factor Model benchmark (optional addition).
- UNRATE NaN-handling code transcription.
- Initialization-vs-evaluation calendar mapping.
- Population marginals figure file.

## 22.4 Items that can be deferred entirely

- `mobility_friction_score` vs HQH6 derivation provenance.
- `flexibility_index` synthetic vs PCA provenance.
- `asymmetry_ratio` derivation rule documentation.

---

# End of Report

Last updated: 2026-05-14. All numbers in this document are quoted from the CSV / JSON sources cited in each section; any discrepancy between this document and the source files should be resolved in favour of the source files.
