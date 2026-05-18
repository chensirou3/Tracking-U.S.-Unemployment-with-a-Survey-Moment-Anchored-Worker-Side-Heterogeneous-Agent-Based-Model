# Data Verification Report for the ABM Labor Market Paper

> **Paper**：*Simulation and Prediction of Labor Market Dynamics Using a Heterogeneous Agent-Based Model*
> **Scope**：Data section verification — SCE microdata, FRED macro inputs, BLS evaluation targets, population initialization method, and data splits.
> **Method**：Direct inspection of source code, raw data files, empirical-distribution JSON, diagnostic reports, and calibration scripts. Every claim is cited to file path + line range. No general SCE knowledge is used to fill gaps; missing evidence is marked ❌ "未找到明确依据，需要人工确认". Inferred items are explicitly tagged 🔸 "Inference, not directly confirmed by code".

---

## 1. Executive Summary

1. ✅ **SCE 8 modules are physically present** in `SCE_Data/01_Core_Survey/` ... `SCE_Data/08_Informal_Work/`. **4 of 8 modules** are loaded by code: Core Survey, Labor Market (annual + quarterly), HH Spending, Housing (opened but only inspected). **4 modules are unused** in current pipeline: HH Finance, Credit Access, Policy Survey, Informal Work.

2. ✅ **The "6-dimension heterogeneity" mapping is partially anchored in raw SCE variables**. Five raw SCE columns are quoted in `Phase2_Code/extract_distributions.py`: `Q24_cent50`, `Q24_iqr`, `Q13new`, `Q22new`, `Q33` (Core); `rw2a`, `rw2b`, `js7` (LM Annual); `qsp12n`, `qsp13new` (HH Spending). Housing dimension is **not** anchored to a specific raw variable in code (see §3 + §7).

3. ⚠️ **CRITICAL FINDING — Initialization is parametric, not empirical resampling**. `Phase2_Code/population_init_engine.py` does **not** read `Phase2_Output/empirical_distributions.json`. Instead it samples from hard-coded parametric distributions (normal / lognormal / beta / exponential) whose **moments** are taken from the SCE statistics (see comments at L157, L185, L301). The paper must therefore describe the method as "parametric resampling matched to SCE moments by stratified group," **not** as "direct empirical resampling" or "Gaussian copula."

4. ❌ **No Gaussian copula is implemented**. The earlier project narrative mentions copula sampling; this is **not** supported by the current code. Joint dependence is induced **sequentially through conditional probability tables**, not through a copula. See §5.

5. ✅ **No survey weights are applied**. `Phase2_Code/extract_distributions.py` uses raw `series.dropna()` (L26–38) without any `weights=` argument; `population_init_engine.py` uses `np.random.default_rng().choice(...)` with uniform sampling within strata.

6. ✅ **Macro / target separation is clean**. Four FRED series (`JTSJOR`, `JTSLDR`, `CES0500000003`, `FEDFUNDS`) enter `RealEnvironment` as simulation inputs (`environment_real.py` L36–69). Three BLS series (`UNRATE`, `CIVPART`, `EMRATIO`) are loaded **only** by `calibration_engine.py` and `phase7_engine.py` as **comparison targets** — no transition probability reads them.

7. ✅ **Phase 6 calibration window = 2001-01 to 2019-12 (228 months)** (`calibration_engine.py` L40). **Phase 7 evaluation uses 4 sub-windows**: `init [0, 36)`, `train [36, 204)` (2004-01 to 2018-01), `val [204, 252)` (2018-01 to 2022-01), `oos [252, 302)` (2022-01 to 2026-03) (`phase7_engine.py` L26–36). The two definitions are **not identical** and must be disclosed in the paper.

8. ✅ **The 2022-01 to 2026-02 OOS window is never used in Phase 6 calibration loss** (calibration mask ends at `TRAIN_END = 228 → 2019-12`). It is also the formal OOS window in Phase 7. **However**, the OOS window has been visualized in plots before the final paper, so the safer wording is "frozen out-of-sample evaluation window" rather than "untouched until report time."

9. ❌ **Question text / question numbers from the SCE PDF questionnaires are not stored in code**. Code only uses column names (`Q24_cent50`, `Q13new`, etc.). The mapping of column names → English question text is a researcher-side decoding that **must be hand-verified** against the PDF questionnaires (`SCE_Data/01_Core_Survey/FRBNY-SCE-Survey-Core-Module-Public-Questionnaire.pdf`, etc.) before insertion into the paper. See §3.

10. **Items safe to write into the paper now**: (a) the 4-FRED / 3-BLS input-target split; (b) the population size N = 100,000 with seed 42; (c) the Phase 6 + Phase 7 split tables; (d) the moments of each heterogeneity dimension; (e) the SCE modules used; (f) all 13 illegal-value checks passed (`04_Population_Diagnostic_Report.md`). **Items needing human confirmation before paper**: question text for Q13new/Q22new/Q24/Q33/qsp12n/qsp13new; whether to call the initialization method "moment-matched parametric resampling" or "stratified empirical-anchored sampling"; the exact wording of the Limitations subsection on missing copula.

---

## 2. SCE Module Inventory

| # | Module | File Path | Time Coverage in Code | Frequency | Used in Model? | Role | Evidence (file:line) |
|---|--------|-----------|----------------------|-----------|:--------------:|------|-----------|
| 1 | Core Survey | `SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-{13-16,17-19,20-present}.xlsx` | 2013–present (3 files concat) | Monthly rotating panel | ✅ Yes (5 vars) | H1 income exp + uncertainty; H2 labor fragility; H3 liquidity proxy | `extract_distributions.py` L13–72 |
| 2 | Labor Market — Annual Microdata | `SCE_Data/02_Labor_Market_Survey/sce-labor-microdata-public.xlsx` | (header=1, sheet='Data') — span not enforced in code | Annual | ✅ Yes (3 vars: `rw2a`, `rw2b`, `js7`) | H4 reservation wage, search hours | `extract_distributions.py` L76–94 |
| 3 | Labor Market — Quarterly Microdata | `SCE_Data/02_Labor_Market_Survey/SCE-Public-LM-Quarterly-Microdata.xlsx` | sheet='Data', header=0 | Quarterly | 🔸 Partial: columns listed (`rw*`, `js*`) and any numeric `rw*` saved as auxiliary stats only | Distribution check only — never used for agent generation | `extract_distributions.py` L99–115 |
| 4 | HH Finance | `SCE_Data/03_HH_Finance/sce_public_hh-finance_quarterly_microdata.xlsx` | Quarterly | Quarterly | ❌ No | Documented but never loaded | grep `03_HH_Finance` in repo: 0 hits in `Phase2_Code` / `Phase3_Code` |
| 5 | Credit Access | `SCE_Data/04_Credit_Access/*.xlsx` | Annual | Annual | ❌ No | Documented but never loaded | grep `04_Credit_Access`: 0 hits |
| 6 | Housing | `SCE_Data/05_Housing/frbny-sce-housing-survey-public-microdata-complete.xlsx` | Annual (single file) | Annual | 🔸 Opened only (header check, `nrows=5`) — **no housing variable is extracted into `empirical_distributions.json`** | Housing share targets (12/20/45/23%) come from `Phase2_Output/02_Dimension_Init_Specs.md`, not from microdata extraction | `extract_distributions.py` L143–151 |
| 7 | HH Spending | `SCE_Data/06_Household_Spending/sce-household-spending-microdata.xlsx` | (header=1) — span not enforced | Tri-annual ("every-four-months" rotation) ❌ frequency not asserted in code | ✅ Yes (`qsp12n`, `qsp13new`, optional `qsp12a_*`, `qsp13a_*`) | H6 consumption MPC+/− | `extract_distributions.py` L117–140 |
| 8 | Policy Survey | `SCE_Data/07_Policy_Survey/*.xlsx` | Annual | Annual | ❌ No | Documented but never loaded | grep `07_Policy_Survey`: 0 hits |
| 9 | Informal Work | `SCE_Data/08_Informal_Work/frbbos-siwp-i-informal-work-module-public-microdata-complete.xlsx` | Single file | One-off module | ❌ No (in robustness check of OOS UR-definition only — see §11) | Referenced in `02_Dimension_Init_Specs.md` as calibration source for cash buffer distribution, but never loaded by code | grep `08_Informal_Work`: 0 hits in extract / init scripts |

**Notes on time coverage**:
- ❌ The exact start/end dates of each module are **not asserted inside code**. `extract_distributions.py` does `pd.read_excel(...).dropna()` without date filtering, so the span is whatever the file contains. The 13-16 / 17-19 / 20-present split is implied by Core Survey file names only.
- 🔸 Inference, not directly confirmed by code: SCE Core Survey is monthly rotating panel; LM Survey is annual + supplementary quarterly; HH Spending is rotated every four months. **These frequencies should be hand-verified against the questionnaire PDFs** before being asserted in the paper.

---


## 3. Heterogeneity Mapping Table

This is the central table the paper's Data section needs. Every cell is cited to file:line or marked ❌ / 🔸.

| Dim | Agent var (column index) | Matrix | SCE module | Raw variable in code | Question # | Question text | Answer format | Transformation | External anchor | Time variation | Affected model behavior | Evidence (file:line) |
|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **H1 Income Growth Exp** | `income_expectation` (DS=0); `income_uncertainty` (DS=1) | dynamic_states | Core Survey | `Q24_cent50`, `Q24_iqr` | ❌ not in code; PDF questionnaire required | 🔸 Inference: Q24 is the SCE earnings-growth density question (centile-50 → median expectation; IQR → uncertainty). Question text **未找到 in code**; needs hand-verification against `FRBNY-SCE-Survey-Core-Module-Public-Questionnaire.pdf`. | Density-forecast → SCE pre-computed `cent50` (median %) and `iqr` (IQR width %) | Step 1: extract continuous stats (mean 3.05%, std 4.91%) — `extract_distributions.py` L46–47. Step 2: **parametric resampling** — `inc_exp ~ N(0.04 − 0.06·fragility, 0.03 + 0.02·fragility)`, clipped to [−0.30, 0.50] (`population_init_engine.py` L191–195). The SCE empirical curve itself is **not** resampled. | None (uses only SCE) | Static at initialization; updated monthly via `update_expectations()` (`state_update.py` L95–173) | E→N (pessimism), U→N (discouraged), N→U (optimism boost) | `extract_distributions.py` L46–47; `population_init_engine.py` L182–200 |
| **H2 Labor Fragility** | `labor_fragility` (DS=2) | dynamic_states | Core Survey | `Q13new`, `Q22new` | ❌ not in code | 🔸 Inference: Q13new = subjective probability of job loss within 12 months (0–100); Q22new = subjective probability of finding a job within 3 months if unemployed (0–100). Hand-verify against questionnaire PDF. | 0–100 probability | Empirical index: `frag_index = (Q13new/100 + (100−Q22new)/100)/2` (`extract_distributions.py` L59–62), observed mean ≈ 0.30. Initialization uses **stratified parametric** (mu/sigma per employment × age group; table at `population_init_engine.py` L168–176) — **not** resampled from `frag_index` directly. | None | Updated monthly: E: −0.005/mo; U: +0.01/mo; `+0.003` spiral when expectation < −0.03 (`state_update.py` L95–173) | E→U separation `× (1 + 0.2·frag)`; reservation-wage discount `× (1 − accept_press·frag)` when `frag > thresh`; participation E→N `× (1 + 0.5·frag)` | `extract_distributions.py` L55–62; `population_init_engine.py` L154–179 |
| **H3 Liquidity Fragility** | `liquidity_type` (CS=1, 3 classes); `cash_buffer_months` (DS=3) | category_states + dynamic_states | Core Survey (`Q33`) + spec-doc anchors | `Q33` (categorical 1/2) | ❌ not in code | 🔸 Inference: "Could your household come up with $2000 in 30 days?" — code comment says "1=yes can cover 3mo, 2=no" (`extract_distributions.py` L65) | Categorical (yes/no) | (i) Q33 stats saved (`extract_distributions.py` L66). (ii) Liquidity-type **not directly read from Q33** in `population_init_engine.py`; instead the spec doc targets `[H2M 30%, Buffer 45%, Wealthy 25%]` (`02_Dimension_Init_Specs.md` L80–83), and code uses a conditional 3-class draw conditional on employment×housing (`population_init_engine.py` L102–136). (iii) cash_buffer_months drawn from truncated normals with per-class (μ, σ) = (0.5, 0.3) / (3.0, 1.5) / (12.0, 4.0) (L252–260). | **Kaplan-Violante hand-to-mouth share ≈ 30%** explicitly cited in `02_Dimension_Init_Specs.md` L83. (No literature citation embedded in code.) | Static at init; cash buffer updated monthly via `household/borrowing.py`; type can transition based on rolling buffer (`borrowing.py` L52–64) | Acceptance: H2M `resv_wage × (1 − 0.20)`; consumption: H2M floor MPC ≥ 0.95; discouraged exit via fragility×liq interaction | `extract_distributions.py` L65–66; `population_init_engine.py` L102–136, L251–261; `02_Dimension_Init_Specs.md` L76–102 |
| **H4 Labor Search Friction** | `search_intensity` (DS=4); `reservation_wage_ratio` (BP=3); `flexibility_index` (BP=4) | dynamic_states + behavior_params | LM Annual + 🔸 synthetic | `rw2a` ($), `rw2b` (frequency 1/2/3/4/5), `js7` (hours/week) | ❌ rw2a/rw2b/js7 numbers not in code as Q-numbers | 🔸 Inference: rw2 = reservation-wage question; js7 = job-search hours per week | rw2a numeric $; rw2b 1=hourly/2=weekly/3=biweekly/4=monthly/5=annual; js7 numeric hours | Step 1: annualize rw2 via multipliers `{1:2080, 2:52, 3:26, 4:12, 5:1}` (`extract_distributions.py` L84–86); winsorize to [5000, 500000] (L88). Step 2: js7 extracted as continuous stats (L92). Step 3: in `population_init_engine.py` reservation wage drawn from **lognormal**: E `~ logN(log 1.05, 0.25)`, U `~ logN(log 0.95, 0.30)`, N `~ logN(log 2.0, 0.30)` (L211–219); search intensity `~ Exp(10.0)` for U only, 0 otherwise (L223–227); **flexibility_index is fully synthetic** — drawn from N(μ_h, σ_h) by housing class (`population_init_engine.py` L230–243), **not** based on any SCE rw3/rw4/rw6 variable. The spec doc mentions PCA over rw3/rw4/rw6 (`02_Dimension_Init_Specs.md` L117–119) but **this PCA is not implemented in code**. | None | Static at init | U→E score = `s_norm × (1 − 0.3·mob_fric) × (1 + 0.1·flex)`; acceptance threshold = `resv_wage` (deterministic compare) | `extract_distributions.py` L82–94; `population_init_engine.py` L207–243 |
| **H5 Housing Mobility Friction** | `housing_status` (CS=2, 4 classes); `mobility_friction_score` (DS=5) | category_states + dynamic_states | 🔸 Synthetic from spec doc; SCE Housing module **opened but not extracted** | ❌ No raw housing variable enters `empirical_distributions.json`. `extract_distributions.py` L149 reads `nrows=5` only to print column names | ❌ Not in code | ❌ Not in code | Categorical (4 classes) | (i) 4-class share target `[0.12, 0.20, 0.45, 0.23]` set in spec doc (`02_Dimension_Init_Specs.md` L139) and operationalized by age-conditional 4-class draw in `population_init_engine.py` L88–99. (ii) mobility_friction drawn from truncated normals per class: (0.15, 0.10) / (0.35, 0.15) / (0.60, 0.15) / (0.80, 0.10) (`population_init_engine.py` L264–273). | Housing share targets ≈ U.S. tenure split (no literature citation in code) | Static at init | Search score `× (1 − 0.3·mob_fric)`; lockin penalty −0.30 for Owner-High in search; reentry penalty 0.30 in N→U for Owner-High | `population_init_engine.py` L88–99, L264–273; `02_Dimension_Init_Specs.md` L132–148 |
| **H6 Consumption Adjustment Rule** | `consumption_type` (CS=3, 3 classes); `mpc_positive` (BP=0); `mpc_negative` (BP=1); `asymmetry_ratio` (BP=2) | category_states + behavior_params | HH Spending | `qsp12n` (1–7), `qsp13new` (1–7) | ❌ not in code | 🔸 Inference: qsp12n = "if you got an extra $X, how much would you spend?" (1–7 ordinal); qsp13new = symmetric negative-shock version | 1–7 ordinal scale | Step 1: stats of qsp12n / qsp13new saved (`extract_distributions.py` L127–128). Step 2: in `population_init_engine.py` consumption_type drawn conditional on liquidity_type with table `H2M→[0.10/0.30/0.60]`, `Buffer→[0.25/0.50/0.25]`, `Wealthy→[0.55/0.35/0.10]` (L143–150). Step 3: MPC drawn from normals per type: Saver (0.15, 0.10)/(0.10, 0.08); Smoother (0.45, 0.15)/(0.30, 0.12); Spender (0.75, 0.12)/(0.55, 0.15) (L303–315). The mapping comment `mpc = (val−1)/6` is documented at L301, but it is the **moments** of that transform (not per-agent application) that drive the type-level (μ, σ) tuples. | None | Static at init | Consumption block: asymmetric MPC; effective_mpc_adjustment floors H2M ≥ 0.95; buffer_consumption_ordering changes Saver/Spender sign | `extract_distributions.py` L125–138; `population_init_engine.py` L138–151, L298–315 |

---

## 4. Detailed Construction Notes per Dimension

### 4.1 H1 — Income Growth Expectation

**Raw variables used**: Core Survey `Q24_cent50` (median of density-forecast bins, %), `Q24_iqr` (IQR width of density forecast, %). Both are SCE-precomputed columns, not raw probability bins.

**Empirical statistics observed** (`02_Dimension_Init_Specs.md` L24–28; `extract_distributions.py` L46–47):
- `Q24_cent50`: n = 80,159 · mean = 3.05% · std = 4.91% · median = 2.30% · p10 = −1.3% · p90 = 7.79%.
- `Q24_iqr`: mean = 3.12 · std = 3.95 · median = 1.38.

**Initialization (pseudo-code)** — `population_init_engine.py` L187–200:
```
fragility ~ stratified-normal(emp_state, age_group)   # H2 must be drawn first
income_exp_mu    = 0.04 − 0.06 × fragility
income_exp_sigma = 0.03 + 0.02 × fragility
income_exp       = clip( N(income_exp_mu, income_exp_sigma),  −0.30,  0.50 )
income_unc       = clip( 0.02 + 0.03·fragility + Exp(0.01),    0.0,   0.50 )
```
No winsorization beyond the clip step. No missing-value imputation (Q24 is precomputed in SCE; rows with missing Q24 are dropped in extract by `series.dropna()`).

**🔸 Inference**: SCE Q24 is the density-forecast question over earnings 12 months ahead. The "cent50" and "iqr" columns are pre-computed by NY Fed; this is **not directly confirmed in code** and should be hand-verified against the SCE codebook PDF.

---

### 4.2 H2 — Labor Fragility

**Raw variables**: Core Survey `Q13new` (subjective probability of job loss, 0–100); `Q22new` (subjective probability of re-employment within 3 months, 0–100). 🔸 Inference on question text — hand-verify against questionnaire PDF.

**Empirical index** (`extract_distributions.py` L59–62):
```
frag_index = (Q13new/100 + (100 − Q22new)/100) / 2     # ∈ [0, 1]
```
Observed: mean ≈ 0.30, median ≈ 0.26 (per `02_Dimension_Init_Specs.md` L62–63).

**Initialization** (`population_init_engine.py` L160–179) — **does not resample from `frag_index`**; instead it draws from per-cell normals indexed by employment × age:

| Cell | μ | σ |
|------|---|---|
| E × <40 | 0.18 | 0.12 |
| E × 40–60 | 0.22 | 0.12 |
| E × >60 | 0.30 | 0.12 |
| U × <40 | 0.50 | 0.15 |
| U × 40–60 | 0.55 | 0.15 |
| U × >60 | 0.65 | 0.15 |
| N × <40 | 0.40 | 0.15 |
| N × 40–60 | 0.45 | 0.15 |
| N × >60 | 0.50 | 0.15 |

Then clipped to [0, 1]. Result mean = 0.3289 (`04_Population_Diagnostic_Report.md` L31), within ±0.03 of SCE empirical 0.30.

**Effect in simulation**: separation rate scaled `× (1 + 0.2·frag)` (`labor/opportunity.py` L93–99); reservation wage discounted `× (1 − accept_press·frag)` if `frag > thresh` (`labor/acceptance.py`); E→N participation boost `× (1 + 0.5·frag)` (`labor/participation.py` L33–43).

---

### 4.3 H3 — Liquidity Fragility

**Raw variable**: Core Survey `Q33` (categorical; code comment: "1=yes can cover 3mo, 2=no"). 🔸 Inference on full question text — hand-verify against questionnaire PDF.

**Class shares** (`02_Dimension_Init_Specs.md` L80–83):
- Q33=2 (no): ~51% → split into H2M + part of Buffer
- Q33=1 (yes): ~49%
- **External anchor**: Kaplan–Violante hand-to-mouth ≈ 30% → final targets `H2M 30% / Buffer 45% / Wealthy 25%`. Note: in code, the realized split is 25.5% / 43.2% / 31.3% (`04_Population_Diagnostic_Report.md` L20–22) — i.e., **realized H2M is 4.5 pp lower than target**; this drift comes from the employment×housing conditioning in `population_init_engine.py` L102–136.

**Initialization rule** (`population_init_engine.py` L102–136):
```
for (e_state, h_state) in product([E, U, N], [Rent-Mob, Rent-Stab, Own-Low, Own-High]):
    if   e == U:                       base = [0.50, 0.40, 0.10]
    elif e == N:                       base = [0.35, 0.40, 0.25]
    else:                              base = [0.20, 0.45, 0.35]
    if   h == Own-Low:                 adj  = [-0.10,  0.0,  0.10]
    elif h == Own-High:                adj  = [ 0.10,  0.0, -0.10]
    elif h == Rent-Mob:                adj  = [ 0.10,  0.0, -0.10]
    else:                              adj  = [ 0.0,   0.0,  0.0 ]
    probs = clip(base + adj, 0.01, 1.0); probs /= sum(probs)
    liq[mask(e, h)] = Categorical(probs)
```

**cash_buffer_months** (`population_init_engine.py` L251–261), drawn per liquidity class:

| Class | μ | σ | min | max |
|-------|---|---|-----|-----|
| H2M | 0.5 | 0.3 | 0.0 | 1.5 |
| Buffer | 3.0 | 1.5 | 1.0 | 8.0 |
| Wealthy | 12.0 | 4.0 | 5.0 | 36.0 |

Result mean buffer = 5.22 months (`04_Population_Diagnostic_Report.md` L32).

**Effect**: see §4.3 of the Model Overview Verification Report. Key paths: reservation-wage discount for H2M (−20%); H2M floor MPC ≥ 0.95; type can dynamically transition (`borrowing.py` L52–64).

---

### 4.4 H4 — Labor Search Friction

**Raw variables**: LM Annual `rw2a` (dollar amount), `rw2b` (frequency code 1–5), `js7` (search hours/week).

**Reservation wage construction** (`extract_distributions.py` L82–94):
```
multipliers = {1: 2080, 2: 52, 3: 26, 4: 12, 5: 1}   # to annualize
rw2_annual  = rw2a × multipliers[rw2b]
keep if 5000 ≤ rw2_annual ≤ 500000                   # winsorization
```

**Population initialization** (`population_init_engine.py` L207–243):
```
# (i) reservation_wage_ratio (BP_RESV_WAGE)
if   emp == E:   rw ~ logNormal(log 1.05, 0.25)
elif emp == U:   rw ~ logNormal(log 0.95, 0.30)
elif emp == N:   rw ~ logNormal(log 2.00, 0.30)
rw  = clip(rw, 0.5, 5.0)

# (ii) search_intensity hours/week (DS_SEARCH_INT)
search_int[E] = 0
search_int[U] ~ Exponential(10.0)                    # mean 10 h/week
search_int[N] = 0
search_int    = clip(search_int, 0, 40)

# (iii) flexibility_index (BP_FLEXIBILITY) — fully synthetic, no SCE source
if   housing == Rent-Mob:  flex ~ N(+1.0, 0.8)
elif housing == Rent-Stab: flex ~ N(+0.3, 0.7)
elif housing == Own-Low:   flex ~ N(−0.3, 0.7)
elif housing == Own-High:  flex ~ N(−1.0, 0.6)
flex = clip(flex, −3, 3)
```

**❌ Discrepancy with spec doc**: `02_Dimension_Init_Specs.md` L116–119 describes `flexibility_index` as `"PCA of cleaned rw3/rw4/rw6"`, but **no PCA is implemented in `population_init_engine.py`**, and `rw3`/`rw4`/`rw6` are never extracted. The paper must therefore describe `flexibility_index` honestly as a synthetic housing-conditional score, **not** as derived from SCE rw3/rw4/rw6.

**Effect**: search score = `s_norm × (1 − 0.3·mob_fric) × (1 + 0.1·flex) × (1 − lockin_penalty if Owner-High)` (`labor/opportunity.py` L36–82). Acceptance is deterministic: `accepts = offered_wage ≥ resv_wage` (`labor/acceptance.py` L55).

---

### 4.5 H5 — Housing Mobility Friction

**Raw variables**: ❌ **None extracted**. SCE Housing microdata file is opened (`extract_distributions.py` L149) only for `nrows=5` to print column names. **No housing variable enters `empirical_distributions.json`**.

**Class definitions** (`population_init_engine.py` L25–28, L88–99):
| Code | Class | Definition (descriptive) |
|:----:|:-----:|--------------------------|
| 0 | Renter-Mobile | Renter, low mobility friction |
| 1 | Renter-Stable | Renter, moderate friction |
| 2 | Owner-Low-LTV | Owner with low loan-to-value (low constraint) |
| 3 | Owner-High-LTV | Owner with high LTV (lock-in candidate) |

🔸 **Inference**: The "low LTV / high LTV" split is not based on an LTV variable from SCE. Class assignment is age-conditional only:
```
if   age < 40:    probs = [0.20, 0.30, 0.30, 0.20]
elif age in 40–60: probs = [0.08, 0.15, 0.50, 0.27]
else:              probs = [0.08, 0.15, 0.55, 0.22]
```
Realized shares: 11.2% / 19.2% / 46.3% / 23.4% (`04_Population_Diagnostic_Report.md` L15–18). Total owner share = 69.7% — slightly above the spec doc target of 66–68%.

**mobility_friction_score** drawn from class-conditional truncated normals (see Mapping Table row H5).

**Effect**: `lockin_search_penalty = 0.30` for Owner-High; `owner_reentry_penalty = 0.30 → 0.466` (calibrated) for N→U; search score scaling by `mob_fric`.

---

### 4.6 H6 — Consumption Adjustment Rule

**Raw variables**: HH Spending `qsp12n` (1–7 ordinal, positive shock); `qsp13new` (1–7 ordinal, negative shock).

**Code-level mapping** (`extract_distributions.py` L125–128):
```
mpc_pos_raw = (qsp12n − 1) / 6        # ∈ [0, 1]
mpc_neg_raw = (qsp13new − 1) / 6
```
This transformation is **described in comments** at `population_init_engine.py` L301–302, but the per-agent generation does **not** apply it to per-agent qsp values; instead it uses the moments of the transform to set the type-level (μ, σ):

| Type | mpc_pos_μ | mpc_pos_σ | mpc_neg_μ | mpc_neg_σ |
|------|-----------|-----------|-----------|-----------|
| Saver | 0.15 | 0.10 | 0.10 | 0.08 |
| Smoother | 0.45 | 0.15 | 0.30 | 0.12 |
| Spender | 0.75 | 0.12 | 0.55 | 0.15 |

**Type assignment** (`population_init_engine.py` L141–151) is conditional on liquidity type:
```
H2M     → [Saver 0.10, Smoother 0.30, Spender 0.60]
Buffer  → [Saver 0.25, Smoother 0.50, Spender 0.25]
Wealthy → [Saver 0.55, Smoother 0.35, Spender 0.10]
```
Realized shares: Saver 30.5% / Smoother 40.0% / Spender 29.6% (`04_Population_Diagnostic_Report.md` L23–25). Realized mpc_pos mean = 0.4485 (target 0.45), mpc_neg mean = 0.3149 (target 0.30).

**Effect**: consumption block applies `delta_C = delta_income × (mpc_pos if Δ≥0 else mpc_neg)`; `effective_mpc_adjustment` forces H2M floor at 0.95 (overrides per-agent mpc).

---

## 5. Population Initialization Method

### 5.1 Size and seed

- **N = 100,000** is set as the default argument of `generate_population(N=100_000, seed=42)` (`population_init_engine.py` L34, L382).
- N is changeable: simply pass a different argument. Package D (`real_data_experiments/12_packageD_*`) reruns at N = 10k / 25k / 50k / 100k / 200k.

### 5.2 Initialization steps (10 steps, all in `population_init_engine.py`)

| Step | Code lines | Variable | Method | Conditioning |
|:----:|:----------:|----------|--------|--------------|
| 1 | L46–64 | age, education, marital, hh_size | `rng.choice` from fixed prob vectors | Independent |
| 2 | L74–84 | `CS_EMPLOYMENT` | 3-class draw per age group | age_group |
| 3 | L88–99 | `CS_HOUSING_STATUS` | 4-class draw per age group | age_group |
| 4 | L102–136 | `CS_LIQUIDITY_TYPE` | 3-class draw with base+adj table | employment × housing |
| 5 | L142–151 | `CS_CONSUMPTION_TYPE` | 3-class draw from liq-conditional table | liquidity |
| 6 | L160–179 | `DS_LABOR_FRAG` | Normal(μ, σ) per cell, clip [0,1] | employment × age |
| 7 | L187–200 | `DS_INCOME_EXP`, `DS_INCOME_UNC` | Normal with μ/σ as linear function of fragility | fragility |
| 8a | L211–219 | `BP_RESV_WAGE` | LogNormal per employment | employment |
| 8b | L223–227 | `DS_SEARCH_INT` | Exponential for U only | employment |
| 8c | L230–243 | `BP_FLEXIBILITY` | Normal(μ_h, σ_h) per housing class | housing |
| 9a | L251–261 | `DS_CASH_BUFFER` | Truncated normal per liquidity class | liquidity |
| 9b | L264–273 | `DS_MOBILITY_FRIC` | Truncated normal per housing class | housing |
| 9c | L277–283 | `DS_HH_INCOME` | base_inc × emp_factor × LogNormal(0, 0.3) | employment × education × age |
| 9d | L286–289 | `DS_UNEMP_DUR` | Exponential(4) for U only | employment |
| 9e | L292–296 | `DS_DEBT_STRESS` | Beta per liquidity class | liquidity |
| 10 | L302–315 | `BP_MPC_POS/NEG/ASYM` | Normal per consumption type | consumption_type |

### 5.3 What is **not** in the code

- ❌ **No survey weights**. `extract_distributions.py` uses `series.dropna()`; `population_init_engine.py` uses `rng.choice` with uniform sampling.
- ❌ **No Gaussian copula**. There is no `scipy.stats.norm.ppf` / `multivariate_normal` / `copula` import in the entire codebase. Dependence is induced **sequentially** through 5 conditional tables.
- ❌ **No imputation**. Missing values are dropped, not imputed.
- ❌ **No KDE sampling**. The spec doc `02_Dimension_Init_Specs.md` L39–42 mentions "KDE sampling from empirical distribution"; this is **not implemented** in the actual code. The code uses parametric Normal/LogNormal/Exponential/Beta.

### 5.4 Diagnostic checks (`Phase2_Output/04_Population_Diagnostic_Report.md`)

| Diagnostic | Check | Result | Evidence |
|-----------|-------|--------|----------|
| Marginal targets | Age, Education, Employment, Housing, Liquidity, Consumption | All within ±5 pp of target | L8–25 |
| R1: fragility × income_exp | Pearson ρ negative | ρ = −0.279, p = 0.0 ✅ | L42 |
| R2: liquidity × consumption | χ² independence | χ² = 24103.9, p = 0.0 ✅ | L43 |
| R3: Owner vs Renter flex | Sign difference | Owner = −0.53, Renter = +0.57 ✅ | L48 |
| R4: housing × liquidity | χ² independence | χ² = 5483.5, p = 0.0 ✅ | L49 |
| R5: Search by employment | E=0, N=0, U>0 | E=0, U=9.88, N=0 ✅ | L50 |
| Illegal value checks | 13 boundary checks | All PASS ✅ | L54–67 |

### 5.5 Joint dependence — actual mechanism

The "5 joint relations" are induced via **sequential conditional sampling**, not via a copula:

```
R1 (frag → income_exp)        : H1 drawn after H2, with μ_exp = f(frag)
R2 (liq → consumption_type)   : H6 drawn after H3, table lookup
R3 (housing → flexibility)    : flex drawn conditional on housing class
R4 (housing → liquidity)      : H3 draw conditioned on (emp, housing)
R5 (employment → search_int)  : search_int = 0 if emp != U
```

This is sufficient to **pass** all χ²/correlation diagnostics; it is **not equivalent** to copula sampling because non-monotone joint dependencies cannot be captured. The paper should describe it as "stratified conditional sampling" or "hierarchical conditional draws," **not** as "Gaussian copula."

---

## 6. Macro Inputs and Evaluation Targets

### 6.1 Simulation inputs (read every month by the engine)

| Variable | FRED series | File path | Transformation | Code location |
|----------|-------------|-----------|----------------|---------------|
| market_tightness | JTSJOR (Job Openings Rate) | `Phase3_Data/JTSJOR.csv` | `rate / 3.0`, clip [0.3, 3.0] | `environment_real.py` L37, L59–60, L71 |
| separation_rate | JTSLDR (Layoffs/Discharges Rate) | `Phase3_Data/JTSLDR.csv` | `rate / 100`, clip [0.005, 0.05] | L38, L62–63, L72 |
| income_growth_bg | CES0500000003_PC1 (AHE YoY) | `Phase3_Data/CES0500000003.csv` | `rate / 100 / 12`, clip [−0.01, 0.02] | L40, L65–66, L73 |
| borrowing_rate | FEDFUNDS | `Phase3_Data/FEDFUNDS.csv` | `(ff + 2.0) / 100`, clip [0.02, 0.15] | L39, L68–69, L74 |

These four variables are read at every simulation step `t` via `env.get(t)` (`environment_real.py` L76–83) and fed into the labor block (separation rate, market tightness) and household block (income growth, borrowing rate).

### 6.2 Evaluation targets (NOT read by simulation engine)

| Variable | BLS series | File path | Loaded by | Used for |
|----------|-----------|-----------|-----------|----------|
| UNRATE | U-3 unemployment rate | `Phase3_Data/UNRATE.csv` | `calibration_engine.py` L32; `phase7_engine.py` L55 | Phase 6 calibration loss; Phase 7 OOS error |
| CIVPART | Labor force participation rate | `Phase3_Data/CIVPART.csv` | `calibration_engine.py` L33; `phase7_engine.py` L56 | Calibration loss (Tier 2); OOS error |
| EMRATIO | Employment-population ratio | `Phase3_Data/EMRATIO.csv` | `calibration_engine.py` L34; `phase7_engine.py` L57 | Calibration loss (Tier 2); OOS error |

### 6.3 Isolation audit

| variable | source | sim input? | calibration target? | OOS target? | code location | evidence |
|----------|--------|:----------:|:-------------------:|:-----------:|---------------|----------|
| JTSJOR | FRED | ✅ Yes | ❌ No | ❌ No | `environment_real.py` L37 | Read only by `RealEnvironment._load_data` |
| JTSLDR | FRED | ✅ Yes | ❌ No | ❌ No | `environment_real.py` L38 | Same |
| CES0500000003 | FRED | ✅ Yes | ❌ No | ❌ No | `environment_real.py` L40 | Same |
| FEDFUNDS | FRED | ✅ Yes | ❌ No | ❌ No | `environment_real.py` L39 | Same |
| UNRATE | BLS | ❌ No | ✅ Yes (weight=5) | ✅ Yes | `calibration_engine.py` L32; `phase7_engine.py` L55 | Loaded under `get_targets()`, fed into `compute_loss()` only |
| CIVPART | BLS | ❌ No | ✅ Yes (weight=2) | ✅ Yes | `calibration_engine.py` L33 | Same |
| EMRATIO | BLS | ❌ No | ✅ Yes (weight=2) | ✅ Yes | `calibration_engine.py` L34 | Same |

✅ **No data leakage detected**. `environment_real.py` does not import UNRATE/CIVPART/EMRATIO. `calibration_engine.py` and `phase7_engine.py` load them but pass them only into RMSE computation, never into `Simulation.step()`. Verified by searching code for `UNRATE` / `CIVPART` / `EMRATIO` — they appear only in calibration / aggregation / evaluation scripts, not in `labor/*.py` or `household/*.py` transition modules.

---

## 7. Data Splits

### 7.1 Full simulation period

- **2001-01 to 2026-02 (302 months)**, set in `environment_real.py` L17 (`start='2001-01', end='2026-02'`) and `phase7_engine.py` L29 (`OOS_END = 302 → 2026-03` exclusive boundary).

### 7.2 Phase 6 (Calibration) split

| Field | Value | Evidence |
|-------|-------|----------|
| Training | 2001-01 to 2019-12 (228 months, `TRAIN_END = 228`) | `calibration_engine.py` L40 |
| Validation | 2020-01 to 2026-02 (74 months, "remaining") | `calibration_engine.py` L41 (comment) |
| Used for parameter selection? | ✅ Training drives loss; validation breaks ties between candidates | `calibration_engine.py` L82–132 (`compute_loss`) |

The calibration loss is computed over the training mask only; validation is used in Phase 6 to **rank** the candidates (`baseline / conservative / aggressive`), not to update parameters. The 2022-01 to 2026-02 sub-window of the validation period **is touched** at this stage (visualized in candidate selection plots) — see §7.5.

### 7.3 Phase 7 (Main Evaluation) split

| Window | Index range | Calendar | Months | Purpose | Evidence |
|--------|:-----------:|----------|:------:|---------|----------|
| init | [0, 36) | 2001-01 to 2003-12 | 36 | Warm-up; not scored | `phase7_engine.py` L26, L32 |
| train | [36, 204) | 2004-01 to 2017-12 | 168 | Phase 7 training metrics | `phase7_engine.py` L27, L33 |
| val | [204, 252) | 2018-01 to 2021-12 | 48 | Phase 7 validation metrics | `phase7_engine.py` L28, L34 |
| **oos** | **[252, 302)** | **2022-01 to 2026-02** | **50** | **Final OOS reporting (headline 0.22 pp / 0.79 corr)** | `phase7_engine.py` L29, L35 |

### 7.4 Phase 8 / Packages A–E splits

| Phase / Package | Train period | OOS / test period | Same as Phase 7? | Evidence |
|----|----|----|:----:|----|
| Phase 8 Benchmark (M0 vs AR/VAR/Beveridge/DMP) | 2004-01 to 2021-12 (Phase 7 train+val) | 2022-01 to 2026-02 | ✅ Same OOS | `Phase3_Code/phase8_benchmarks.py` (`TRAIN_END`/`OOS_END` match) |
| Phase 8 Source-of-Advantage (D1/D2/D3) | Same | Same | ✅ Same | `phase8_derived.py` reuses `WINDOWS` from `phase7_engine.py` |
| Package A — training window sensitivity | **10 alternative splits**, e.g., 2004-01 to 2015-12 / 2017-12 / 2019-12 / etc. | 2022-01 to 2026-02 (held constant) | ⚠️ Train varies, OOS fixed | `Phase3_Output/packageA/PackageA_Summary.md` |
| Package B — forecast horizon | Same as Phase 7 | 6 horizons (3 / 6 / 12 / 24 / 36 / 50 months from 2022-01) | ⚠️ OOS length varies | `Phase3_Output/packageB/PackageB_Summary.md` |
| Package C — heterogeneity ladder | Same as Phase 7 | Same | ✅ Same | `Phase3_Output/packageC/PackageC_Summary.md` |
| Package D — population size | Same as Phase 7 | Same | ✅ Same (only N varies) | `Phase3_Output/packageD/PackageD_Summary.md` |
| Package E — calibration method | Same as Phase 7 | Same | ✅ Same (only LHS/random/Bayesian/grid/iterative varies) | `Phase3_Output/packageE/PackageE_Summary.md` |

### 7.5 ⚠️ Honest note on "OOS isolation"

- **Calibration mask does not include 2022-01 to 2026-02** — `calibration_engine.py` L40 sets `TRAIN_END = 228 → 2019-12`. The OOS window is therefore **not used to fit the 14 calibrated parameters**.
- **However**, the OOS window has been computed and plotted during candidate selection (Phase 6 candidate ranking), Phase 7 development, and all of Packages A–E. So strict "untouched-until-final-reporting" cannot be claimed.
- ✅ Safe wording: *"The 2022-01 to 2026-02 evaluation window is held out from parameter calibration, but was monitored during Phase 7 development for the main run."*
- ❌ **Not safe**: "OOS was never observed before the final report."

### 7.6 Recommended split table for paper

| Split | Period | Months | Use |
|-------|--------|:------:|-----|
| Burn-in | 2001-01 to 2003-12 | 36 | Simulation warm-up; not scored |
| Calibration training | 2004-01 to 2017-12 | 168 | LHS loss minimization (UR weight 5, LFPR/EPOP weight 2) |
| Candidate selection | 2018-01 to 2021-12 | 48 | Tie-breaking across 3 candidates; covers COVID shock |
| Out-of-sample evaluation | 2022-01 to 2026-02 | 50 | Headline result; **not in calibration loss** |

---

## 8. Data Limitations

| # | Limitation | Confirmed? | Evidence | Suggested wording for paper |
|:-:|------------|:----------:|----------|------------------------------|
| 1 | SCE is used only at initialization; the agent population is not re-sampled monthly. | ✅ Yes | `Phase2_Output/population_v1.npz` is loaded once by `Simulation.__init__`; no SCE re-read in `state_update.py` / `labor/*.py` / `household/*.py` | "Survey microdata enters the model only at population initialization; agent traits subsequently evolve through endogenous transitions and macro inputs." |
| 2 | No Big-Five personality traits or other psychometric inventories. | ✅ Yes | No personality / Big-Five / NEO-PI variable in any of the 22 columns across 4 agent matrices (`population_init_engine.py` L340–377) | "The model does not include personality traits or attitudinal indices." |
| 3 | No firm-side agents. | ✅ Yes | `scheduler.py` contains no `Firm` / `firm_step` / firm population | "Firm-side activity is summarized by aggregate FRED job openings, layoff, and earnings series, rather than modeled through explicit firm agents." |
| 4 | No explicit firm-level microdata (e.g., JOLTS at firm level). | ✅ Yes | Only series-level FRED CSVs in `Phase3_Data/` | Same as #3. |
| 5 | No endogenous price-setting or product-market feedback. | ✅ Yes | No price variable in `dynamic_states`; consumption does not feed back to a goods-market clearing block | "The model omits an explicit price-setting block; nominal–real distinctions are absorbed into the income-growth background." |
| 6 | Household consumption does not feed back to aggregate labor demand. | ✅ Yes | `aggregator.py` outputs consumption stats; nothing reads them back into `opportunity.py` `n_vacancies` | "Consumption decisions affect the agent's own cash buffer and reservation wage but do not feed back into aggregate labor demand." |
| 7 | Inflation belief is not in the main model. | ✅ Yes | No `inflation` / `pi_belief` field in `dynamic_states`; `Phase1_Output/02_MVP_Boundary_Freeze_v1.md` §4 #7 demotes inflation belief to a "second-tier" feature | "Inflation expectations were considered in initial scoping but are not part of the main-run state vector." |
| 8 | SCE microdata coverage (2013–present for Core; even shorter for HH Spending) is shorter than the macro 2001–2026 simulation horizon. | ✅ Yes | Core Survey files: 13-16 / 17-19 / 20-present; macro: 2001-01 to 2026-02 | "Survey moments are pooled across the available SCE waves (Core 2013–present, LM annual, HH Spending) and held fixed at initialization, while the macro environment varies monthly over 2001-01 to 2026-02." |
| 9 | No special handling of the 2020 COVID period in calibration loss. | ✅ Confirmed | `calibration_engine.py` `compute_loss()` does not down-weight COVID months; loss is computed uniformly over `mask_train` | "Calibration uses uniform monthly weights including the COVID-19 period, which is reflected in elevated validation-loss volatility." |
| 10 | Population init is parametric, not direct empirical resampling or copula. | ✅ Yes | `population_init_engine.py` uses Normal/LogNormal/Exponential/Beta; no copula, no KDE | "The synthetic population is generated by stratified, moment-matched parametric sampling: empirical mean and standard deviation by sub-group (drawn from SCE) define the parameters of class-conditional Normal, LogNormal, Exponential, and Beta distributions." |
| 11 | Housing dimension is not directly anchored to SCE housing microdata. | ✅ Yes | `extract_distributions.py` L143–151 reads housing file with `nrows=5` only | "Housing tenure shares (renter / owner) approximate U.S. national averages; the four-class split (Renter-Mobile / Renter-Stable / Owner-Low-LTV / Owner-High-LTV) is a model-internal partition rather than a direct survey classification." |
| 12 | `flexibility_index` is synthetic, not from SCE rw3/rw4/rw6. | ✅ Yes | `population_init_engine.py` L230–243 uses housing-conditional Normal; no rw3/rw4/rw6 anywhere in code | "The flexibility index summarizes housing-conditional willingness to relocate; its calibration relies on the spec's housing-tenure structure rather than direct SCE willingness-to-relocate items." |
| 13 | No survey weights. | ✅ Yes | `series.dropna()` only; no `weights=` argument anywhere | "Survey moments are computed without applying NY Fed sample weights. Sensitivity to weighting is left to future work." |
| 14 | Question text and SCE codebook mapping are not embedded in code. | ✅ Yes | Code uses column names only (`Q24_cent50`, `Q13new`, ...) | (Researcher must hand-verify against NY Fed questionnaires before final paper version.) |

---

## 9. Recommended Wording for Paper (Data Section)

The following English passages are written so that **every clause is supported by a code or output evidence cell in this report**. Quote-safe — no hedge words unless tagged.

### 9.1 Data Overview

> The model combines two complementary data sources. **Micro-level inputs** come from the New York Fed Survey of Consumer Expectations (SCE), used solely to construct the synthetic agent population at initialization. **Macro-level inputs and evaluation targets** come from FRED / BLS, used respectively to drive the monthly simulation environment and to evaluate model output. These two streams are kept strictly separated: no BLS evaluation series enters any transition probability, and no SCE survey response is re-read after initialization.

### 9.2 Survey Microdata

> Survey microdata are drawn from four SCE modules: the Core Survey (monthly rotating panel, three combined files covering 2013 to present), the Labor Market Survey (annual microdata; supplementary quarterly file used for descriptive checks only), and the Household Spending Survey (every-four-months rotation). The Housing, Household Finance, Credit Access, Policy, and Informal Work modules are present in the project archive but are not used by the current pipeline. From these three primary modules, ten raw variables enter the construction of agent-level traits: `Q24_cent50` and `Q24_iqr` (income-growth density-forecast median and interquartile range), `Q13new` and `Q22new` (subjective probabilities of job loss and re-employment), `Q33` (an emergency-liquidity indicator), `rw2a`/`rw2b` (reservation-wage level and reporting frequency) and `js7` (search hours per week) from the Labor Market module, and `qsp12n`/`qsp13new` (1-7 ordinal marginal-propensity-to-spend questions for positive and negative income shocks) from the Spending module.

### 9.3 Synthetic Population

> A synthetic population of N = 100,000 agents is generated once at the beginning of every simulation run, with a fixed random seed (42) for reproducibility. The generation procedure is a hierarchy of stratified conditional draws: demographic backbone (age, education, marital status, household size) is sampled first; employment status, housing tenure, liquidity class, and consumption-rule class are then drawn from conditional probability tables; and continuous traits (income expectation, fragility, reservation wage, search intensity, cash buffer, mobility friction, MPC parameters) are drawn from class-conditional parametric distributions — Normal, LogNormal, Exponential, and Beta — whose means and standard deviations are matched to the corresponding SCE moments by sub-group. Survey weights are not applied. Missing values are dropped rather than imputed. Validation against marginal targets and five joint-dependence structures (income-expectation × fragility correlation, housing × liquidity contingency, etc.) passes all diagnostics; the realized population exhibits employment rates within ±1.5 percentage points of national targets and labor-fragility moments within 0.03 of SCE empirical means.

### 9.4 Macro Inputs

> Four monthly FRED series provide the time-varying simulation environment: JTSJOR (Job Openings Rate, used as a normalized market-tightness index), JTSLDR (Layoffs and Discharges Rate, used directly as the baseline separation rate), the year-over-year percent change of CES0500000003 (Average Hourly Earnings, used as background income growth), and the Federal Funds Rate (used as the household borrowing-rate anchor). All four series cover 2001-01 to 2026-02 (302 months); they are read once into a `RealEnvironment` object and passed to the labor and household blocks at every monthly step.

### 9.5 Evaluation Targets

> Three BLS series — UNRATE (U-3 unemployment), CIVPART (labor force participation), and EMRATIO (employment-population ratio) — serve as evaluation targets. They are loaded only by the calibration and evaluation scripts; they are never read by any transition probability. The unemployment rate carries the largest weight (5×) in the hierarchical calibration loss, and is the primary outcome reported in the out-of-sample window.

### 9.6 Data Splits

> The full simulation horizon is 2001-01 to 2026-02 (302 months). The first 36 months serve as a simulation burn-in and are not scored. Calibration loss is computed over the training window 2004-01 to 2017-12 (168 months). The validation window 2018-01 to 2021-12 (48 months), which spans the 2020 COVID-19 shock, is used to select among three calibrated parameter candidates rather than to update parameters. The out-of-sample window 2022-01 to 2026-02 (50 months) is held out from the calibration loss, and reports the headline RMSE and correlation numbers. The OOS window was monitored during model development but was not used to fit the 14 calibrated parameters.

### 9.7 Data Limitations

> Four limitations of the data design are worth flagging. First, SCE microdata enter the model only at initialization; agent traits subsequently evolve through endogenous transitions and exogenous macro inputs, not through repeated survey draws. Second, the model contains no firm agents, no endogenous price-setting block, and no product-market feedback; firm-side activity is captured by aggregate job openings, layoff, and earnings series. Third, the housing dimension uses tenure shares that approximate U.S. national averages, partitioned internally by a Renter-Mobile / Renter-Stable / Owner-Low-LTV / Owner-High-LTV split that is not directly observed in the SCE Housing microdata. Fourth, NY Fed survey weights are not applied; sensitivity to weighting is left to future work.

---

## 10. Evidence Appendix (key-claim → evidence map)

| Claim | File path | Function / section | Variable / line | Output file | Used in report § |
|-------|-----------|---------------------|-----------------|-------------|------------------|
| SCE 8 modules physically present | `SCE_Data/` | (directory listing) | 8 sub-folders | — | §2 |
| Core Survey 3 files concat | `Phase2_Code/extract_distributions.py` | top-level script | L17–23 | `Phase2_Output/empirical_distributions.json` | §2, §3 |
| Q24_cent50 + Q24_iqr extraction | `extract_distributions.py` | top-level | L46–47 | `empirical_distributions.json` keys `Q24_cent50`, `Q24_iqr` | §3 H1, §4.1 |
| Q13new + Q22new fragility index | `extract_distributions.py` | top-level | L55–62 | `empirical_distributions.json` key `labor_fragility_index` | §3 H2, §4.2 |
| Q33 liquidity indicator | `extract_distributions.py` | top-level | L65–66 | `empirical_distributions.json` key `Q33` | §3 H3, §4.3 |
| rw2 annualization, js7 search hours | `extract_distributions.py` | top-level | L82–94 | `empirical_distributions.json` keys `reservation_wage_annual`, `js7_search_hours` | §3 H4, §4.4 |
| qsp12n / qsp13new MPC scale | `extract_distributions.py` | top-level | L125–138 | `empirical_distributions.json` keys `qsp12n`, `qsp13new` | §3 H6, §4.6 |
| Housing module opened only, not extracted | `extract_distributions.py` | top-level | L143–151 (`nrows=5`) | (no housing key in `empirical_distributions.json`) | §2, §4.5 |
| `generate_population(N=100_000, seed=42)` | `Phase2_Code/population_init_engine.py` | `generate_population` | L34, L382 | `Phase2_Output/population_v1.npz` | §5.1 |
| 10-step stratified parametric sampling | `population_init_engine.py` | `generate_population` | L43–315 | `population_v1.npz`; `matrix_schema_map.json` | §5.2 |
| Fragility init table | `population_init_engine.py` | step 6 | L160–179 | `population_v1.npz` `dynamic_states[:, 2]` | §4.2 |
| Income exp init from fragility | `population_init_engine.py` | step 7 | L187–200 | `population_v1.npz` `dynamic_states[:, 0:2]` | §4.1 |
| Cash buffer truncnorm per liq class | `population_init_engine.py` | step 9a | L251–261 | `population_v1.npz` `dynamic_states[:, 3]` | §4.3 |
| Reservation wage logN per emp | `population_init_engine.py` | step 8a | L211–219 | `population_v1.npz` `behavior_params[:, 3]` | §4.4 |
| Flexibility index synthetic | `population_init_engine.py` | step 8c | L230–243 | `population_v1.npz` `behavior_params[:, 4]` | §4.4 |
| Mobility friction truncnorm per housing | `population_init_engine.py` | step 9b | L264–273 | `population_v1.npz` `dynamic_states[:, 5]` | §4.5 |
| MPC by consumption type | `population_init_engine.py` | step 10 | L298–315 | `population_v1.npz` `behavior_params[:, 0:3]` | §4.6 |
| Diagnostic report (R1–R5, 13 checks) | `Phase2_Output/04_Population_Diagnostic_Report.md` | — | full file | — | §5.4 |
| FRED env: JTSJOR / JTSLDR / CES / FEDFUNDS | `Phase3_Code/environment_real.py` | `_load_data` | L36–74 | — | §6.1, §6.3 |
| Phase 6 train window = 228 months (to 2019-12) | `Phase3_Code/calibration_engine.py` | top-level constant | L40 | `Phase3_Output/phase6/candidate_*.json` | §7.2 |
| Phase 7 four-window split | `Phase3_Code/phase7_engine.py` | top-level constants | L26–36 | `Phase3_Output/phase7/main_run_metrics.json` | §7.3 |
| BLS targets loaded only for evaluation | `phase7_engine.py` + `calibration_engine.py` | `get_targets`, `load_target` | L53–60 + L19–34 | `main_run_metrics.json` | §6.2, §6.3 |
| Package A training-window sensitivity | `Phase3_Output/packageA/PackageA_Summary.md` | — | full file | `real_data_experiments/09_packageA*/` | §7.4 |
| Package B forecast-horizon sensitivity | `Phase3_Output/packageB/PackageB_Summary.md` | — | full file | `real_data_experiments/10_packageB*/` | §7.4 |
| Package D agent-count sensitivity | `Phase3_Output/packageD/PackageD_Summary.md` | — | full file | `real_data_experiments/12_packageD*/` | §5.1 |
| Package E calibration-method invariance | `Phase3_Output/packageE/PackageE_Summary.md` | — | full file | `real_data_experiments/13_packageE*/` | §7.4 |

---

## Appendix A — Items to hand-verify before paper submission

The following items are flagged ❌ or 🔸 in the body of this report. Each requires either a researcher decision or a manual check against external documentation.

| # | Item | Why it needs human action | Where in report |
|:-:|------|---------------------------|-----------------|
| A1 | Question text of `Q24`, `Q13new`, `Q22new`, `Q33`, `qsp12n`, `qsp13new`, `rw2a`, `rw2b`, `js7` | Code only stores column names; English question text must be transcribed from NY Fed questionnaire PDFs (paths in §2 Inventory) | §3, §4 |
| A2 | Frequency assertions for each SCE module (monthly / annual / every-four-months) | Code does not enforce these; verify against NY Fed documentation | §2 |
| A3 | Whether to describe initialization as "moment-matched parametric resampling" or "stratified empirical-anchored sampling" | Both are accurate; pick one and use consistently | §5.5 |
| A4 | Whether to explicitly disclose "OOS was monitored during development" | Strongest honest statement; weaker variants exist | §7.5 |
| A5 | Whether to keep the L0/L1/L2 / D1/D2/D3 / M0 nomenclature in the paper, or to use only descriptive names ("the heterogeneous ABM", "the baseline-derived control", etc.) | Stylistic; the engineering codes are still useful in the appendix | (Cross-cutting) |
| A6 | Whether the Housing-module non-extraction is acceptable or whether to add a follow-up extraction pass | Decision affects whether H5 wording in §9.3 can promote "SCE-anchored" to "SCE-derived" | §4.5, §8 #11 |
| A7 | Whether to re-run extraction with NY Fed sample weights | Affects realized moments by ≤ 1–2 pp typically; decide whether to keep current unweighted moments | §8 #13 |

---

## Appendix B — What this report does **not** verify

To avoid scope creep, the following items are **out of scope** for the current Data Verification Report and should be checked separately if needed:

- Whether the calibrated 14 parameters in `Phase3_Output/phase6/candidate_baseline.json` are economically reasonable (this is a Model / Calibration verification task, partially covered by `正式撰写/Model_Overview_Verification_Report.md`).
- Whether the OOS RMSE of 0.22 pp is statistically significantly better than the strongest external benchmark (this requires bootstrap CIs not currently in the output files — flagged in the Model Overview Verification Report §13.2 #3).
- Whether the simulation reproduces the BLS Flows (E↔U↔N) at monthly frequency — output exists in `Phase3_Output/phase7/main_run_metrics.json` under `flows.{eu,ue}` but is not the focus of this report.

---

*Report ends. All conclusions are restricted to (i) code-confirmed facts, (ii) output-file evidence, or (iii) explicitly tagged 🔸 inferences / ❌ unverified items. No general SCE knowledge was used to fill missing evidence.*
