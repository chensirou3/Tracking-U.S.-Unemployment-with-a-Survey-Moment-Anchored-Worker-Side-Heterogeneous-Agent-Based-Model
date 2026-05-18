# Results 6.3 — Heterogeneity Mechanism and Ablation (Preparation Report)

**Scope.** Two experiments rerun fresh, 5 seeds, OOS = 2022-01..2026-02 (49/50 valid months).

- **Experiment 5 — Phase 7 Heterogeneity / Mechanism Ablation** (20 configurations × 5 seeds = 100 sims):
  1 baseline + 6 dimension flattenings + 13 mechanism on/off disables.
- **Experiment 11 — Package C Heterogeneity Ladder** (9 levels × 5 seeds = 45 sims):
  Core L0..L6 (nested) + Layer G2/G3 (block additions; G1==L2, G4==L6).

All numbers in this report are produced fresh from `ablation_metrics.json`,
`ladder_metrics.json` and their per-seed `.npz` trajectories. Baseline parameters
come from `Phase3_Output/phase6/candidate_baseline.json` (the same 14-parameter
vector used in Sections 6.1 and 6.2). Macro inputs are the real FRED/BLS series
described in `Data_Verification_Report.md`; the OOS window contains 49 of 50
months because UNRATE for 2025-10 is missing in the FRED snapshot (handled by
NaN-masking).

---

## 1. Executive Summary

1. **Headline (baseline = full heterogeneous ABM):** OOS UR RMSE = **0.221 ± 0.007 pp**, Corr = 0.790, LFPR RMSE = 2.27 pp, EPOP RMSE = 2.21 pp (5 seeds). This matches the 6.1/6.2 numbers bit-identically (same code, same seeds).
2. **Dominant single dimension — Labor Search Friction.** Flattening it raises OOS UR RMSE from 0.221 → **1.110 pp** (Δ = +0.889 pp, 5× the next-largest dimension). The +0.88 pp figure quoted in earlier internal notes is confirmed.
3. **Top-3 dimensions by ΔUR RMSE:** Search Friction (+0.889 pp) ≫ Liquidity Fragility (+0.299 pp) > Housing Mobility Friction (+0.162 pp). Labor Fragility, Income Expectation, and Consumption Rule each move OOS UR by ≤ 0.05 pp — within or near the 5-seed noise band of the baseline.
4. **Top mechanism is Matching Competition** (the finite-vacancy / competitive allocation rule): disabling it raises OOS UR RMSE to **2.146 pp** (Δ = +1.925 pp), nearly an order of magnitude larger than the second-ranked mechanism. This is the single largest single-toggle effect in the entire ablation grid.
5. **Heterogeneity ladder is strongly non-monotonic.** L0=0.553, L1=0.550, then L2 **jumps to 1.054 pp** when Search is added on top of Labor Fragility, and L3=1.058 pp stays bad when Income Expectation is added. L4=0.517 pp (Liquidity added) recovers part of the loss; L5=0.268 (Housing added) and L6=0.221 (Consumption Rule added) finish below L0.
6. **The Layer ladder confirms a coupled-block structure.** Adding the constraint layer (Liquidity + Housing) as a block — G2 — already gives 0.267 pp, only 0.046 pp above the full L6 model. G3 (G2 + Consumption Rule) gives 0.241 pp. The 6-dim system is therefore well approximated by a 4-dim labor+constraint block once those dimensions are activated *jointly*, not sequentially.
7. **LFPR/EPOP trade-offs are sharp.** Flattening Liquidity collapses LFPR RMSE from 2.27 → 0.47 pp and EPOP from 2.21 → 0.32 pp, while UR worsens to 0.52 pp. Disabling Matching Competition cuts LFPR RMSE to 0.77 pp while wrecking UR. UR-only or joint-only optimization gives very different "best" specifications — this is the household-block trade-off identified in Section 6.2.
8. **Match against old reports:** every dimension ablation moves by < 0.025 pp vs the older 3-seed Phase 7 output (`Phase3_Output/phase7/ablation_results.json`); the rank order and the "Search dominates" conclusion are unchanged. The Package C ladder reproduces the L2/L3 spike and the L5/L6 convergence reported in `PackageC_Summary.md` (the older 3-seed L2 was 1.071 vs new 1.054 pp).
9. **Safe paper claim:** *The model's predictive value comes from a coupled labor-search + constraint heterogeneity system. Search Friction is the strongest standalone driver, but adding it alone is destabilizing without the liquidity and housing constraint dimensions.* (Wording-to-avoid list in §13.)

---

## 2. Experiment Setup

| item | value |
|---|---|
| experiments | Phase 7 ablation (Exp 5) + Package C ladder (Exp 11) |
| seeds | [42, 137, 2024, 888, 1234] (5 seeds) |
| simulation period | 2001-01..2026-02, T = 302 months |
| evaluation windows | init (0–35), train (36–203), val (204–251), oos (252–301) |
| candidate parameterization | `candidate_baseline.json` (14 parameters, Phase 6 final) |
| macro inputs | FRED JTSJOR, JTSLDR, CES0500000003, FEDFUNDS (via `RealEnvironment`) |
| evaluation targets | FRED UNRATE, CIVPART, EMRATIO; OOS month 2025-10 NaN |
| agent population | 100,000 synthetic agents anchored to NY Fed SCE micro moments |

Total sims executed: **145** (100 ablation + 45 ladder); wall time 1066.9 s + 493.6 s = **26.0 min** total.

---

## 3. Method

### 3.1 Dimension-mapping table

| dimension | code variable / matrix column | flattening method (`flatten_heterogeneity` in `phase7_engine.py`) | affected behaviour |
|---|---|---|---|
| Income Growth Expectation | `ds[:, DS_INCOME_EXP]`, `ds[:, DS_INCOME_UNC]` | replace by population median (mean for uncertainty) | expectation updating; participation gating |
| Labor Fragility | `ds[:, DS_LABOR_FRAG]` | replace by population median | search desperation; acceptance pressure; discouraged-exit triggers |
| Liquidity Fragility | `cs[:, CS_LIQUIDITY_TYPE]`, `ds[:, DS_CASH_BUFFER]` | force LIQ_BUFFER class for all; median cash buffer | reservation wage discount; forced MPC; borrowing path |
| Labor Search Friction | `ds[:, DS_SEARCH_INT]`, `bp[:, BP_RESV_WAGE]`, `bp[:, BP_FLEXIBILITY]` | replace by population mean | search intensity; reservation wage; matching score |
| Housing Mobility Friction | `cs[:, CS_HOUSING_STATUS]`, `ds[:, DS_MOBILITY_FRIC]` | force HSG_RENT_STB class; median mobility friction | search radius / lock-in; reentry friction |
| Consumption Adjustment Rule | `cs[:, CS_CONSUMPTION_TYPE]`, `bp[:, BP_MPC_POS]`, `bp[:, BP_MPC_NEG]` | force CON_SMOOTHER class; mean MPC up/down | type-specific consumption sequencing; buffer ordering |

Code evidence: `Phase3_Code/phase7_engine.py:126-154`.

### 3.2 Mechanism on/off

The 13 mechanisms live in `Phase3_Code/mechanism_config.py:8-113`. Each ablation
flips a single `cfg[mechanism_name]['enabled']` from `True` to `False`; all other
parameters are unchanged. The default config is **all-on** ⇒ baseline.

### 3.3 Ladder construction

`Phase3_Code/packageC_engine.py:22-44` defines:
- Core (nested) `L0..L6`: each level adds one dimension on top of the previous, in the fixed order labor_frag → search → income_exp → liquidity → housing → consumption_rule.
- Layer (block) `G1..G4`: G1 = {labor_frag, search}, G2 = G1 ∪ {liquidity, housing} (constraint layer), G3 = G2 ∪ {consumption_rule}, G4 = full. Only G2 and G3 are new — G1 ≡ L2 and G4 ≡ L6.

For each (level, seed): all six MVP dimensions are flattened by the same
`flatten_heterogeneity` routine, then dimensions in the active set are restored
to their heterogeneous values by re-running `Simulation` from the original
population matrices (the engine constructs a fresh simulation each call).

### 3.4 Metric pipeline (identical to 6.1/6.2)

For each window, `compute_window_metrics` (`phase7_engine.py:68-119`) reports
RMSE/MAE/Corr for UR, LFPR, EPOP plus mean transition rates. All decimals are
multiplied by 100 to obtain percentage points in this report. Seed aggregation:
mean and population std (`ddof=0`) across 5 seeds. Δ RMSE is computed as
`ablation - baseline` (positive = worse).

### 3.5 Deviations from prior scripts

- Old `run_phase7_ablation.py` used 3 seeds and covered 6 dimensions only.
  New `run_6_3_phase7_ablation.py` extends to 5 seeds and adds 13 mechanism toggles.
- Old `run_packageC_projection.py` used 3 seeds. New `run_6_3_packageC_ladder.py`
  uses 5 seeds; level definitions are imported from the same engine, so the
  active-set logic is bit-identical.
- No model code in `Phase3_Code/` was modified.

---

## 4. Dimension Ablation Results

OOS UR RMSE, seed-mean ± seed-sd over 5 seeds, sorted by descending Δ:

| dimension flattened | OOS UR RMSE (pp) | ΔUR RMSE (pp) | seed sd | UR Corr | LFPR (pp) | EPOP (pp) | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| — Full heterogeneous ABM | **0.221** | 0.000 | 0.007 | 0.790 | 2.27 | 2.21 | reference |
| Labor Search Friction | **1.110** | +0.889 | 0.020 | 0.784 | 3.79 | 4.35 | critical — dominant standalone driver |
| Liquidity Fragility | 0.520 | +0.299 | 0.031 | 0.798 | **0.47** | **0.32** | important; **LFPR/EPOP improve** ⇒ trade-off |
| Housing Mobility Friction | 0.383 | +0.162 | 0.032 | 0.776 | **8.95** | **8.38** | important; LFPR/EPOP catastrophic |
| Consumption Adjustment Rule | 0.268 | +0.047 | 0.011 | 0.771 | 1.93 | 1.79 | marginal standalone; check ladder |
| Labor Fragility | 0.244 | +0.023 | 0.016 | 0.754 | 2.31 | 2.25 | within seed noise |
| Income Growth Expectation | 0.241 | +0.020 | 0.015 | 0.774 | 2.22 | 2.17 | within seed noise |

**Ranking by ΔUR RMSE (largest = most important standalone):**
1. Labor Search Friction (+0.889 pp)
2. Liquidity Fragility (+0.299 pp)
3. Housing Mobility Friction (+0.162 pp)
4. Consumption Adjustment Rule (+0.047 pp)
5. Labor Fragility (+0.023 pp)
6. Income Growth Expectation (+0.020 pp)

**Interpretation.** Three of the six dimensions (Labor Fragility, Income
Expectation, Consumption Rule) have standalone Δ within or close to the seed
noise band, while Search/Liquidity/Housing each produce a clearly detectable UR
deterioration when flattened. This does **not** mean the bottom three are
unnecessary — their contribution shows up only through the ladder and through
LFPR/EPOP secondary targets. Flattening Liquidity, for example, actually
*improves* LFPR/EPOP RMSE while hurting UR; flattening Housing destroys LFPR.
See §9.

CSV: `tables/table1_dimension_ablation.csv`.

---

## 5. Mechanism Ablation Results

OOS UR RMSE for the 13 mechanisms, sorted by descending Δ vs baseline:

| rank | mechanism disabled | block | ΔUR RMSE (pp) | seed sd | stable? | LFPR (pp) | EPOP (pp) |
|---:|---|---|---:|---:|---|---:|---:|
| 1 | `matching_competition` | labor/search | **+1.925** | 0.015 | stable | 0.77 | 2.01 |
| 2 | `housing_reentry_friction` | participation | +0.175 | 0.033 | stable | 8.36 | 7.81 |
| 3 | `liquidity_constraint_modifier` | type-specific | +0.074 | 0.026 | fragile | 1.65 | 1.46 |
| 4 | `state_dependent_expectation` | expectations | +0.031 | 0.023 | fragile | 1.56 | 1.58 |
| 5 | `expectation_participation` | participation | +0.028 | 0.009 | stable | 2.56 | 2.54 |
| 6 | `effective_mpc_adjustment` | household | +0.028 | 0.011 | fragile | 2.01 | 1.91 |
| 7 | `discouraged_worker` | participation | +0.023 | 0.016 | fragile | 3.83 | 3.68 |
| 8 | `housing_lockin_modifier` | type-specific | +0.019 | 0.008 | fragile | 2.50 | 2.43 |
| 9 | `high_fragility_modifier` | type-specific | +0.012 | 0.015 | fragile | 2.28 | 2.22 |
| 10 | `fragility_x_liquidity_interaction` | type-specific | +0.011 | 0.015 | fragile | 2.32 | 2.26 |
| 11 | `experience_dependent_expectation` | expectations | +0.011 | 0.011 | fragile | 4.16 | 4.03 |
| 12 | `consumption_sequencing` | household | +0.011 | 0.010 | fragile | 2.24 | 2.17 |
| 13 | `buffer_consumption_ordering` | household | +0.006 | 0.025 | n/a | 2.09 | 2.01 |

**Interpretation.**
- `matching_competition` (finite vacancy pool with competitive allocation) is the
  single largest single-toggle effect anywhere in the ablation grid: removing it
  collapses UR dynamics to a ~2.15-pp-RMSE near-flat path. This is consistent
  with `matching_competition` being the only mechanism in the all-off "Simplified
  ABM" of Section 6.2 (D2 = 0.561 pp UR RMSE) — without it, the Simplified ABM
  would degenerate further.
- `housing_reentry_friction` (+0.175 pp UR, +6.1 pp LFPR) is a participation-side
  mechanism whose effect is similar to flattening the Housing dimension
  (+0.162 pp UR), confirming dimension-mechanism alignment for housing.
- `liquidity_constraint_modifier` and `effective_mpc_adjustment` together
  parallel the Liquidity dimension flatten; the dimension flatten effect
  (+0.299 pp) is larger than the sum of these two mechanism flips (+0.102 pp),
  because the Liquidity flatten also forces all agents to LIQ_BUFFER and equalizes
  cash buffers, which the mechanism toggles do not do.
- The five expectation/household mechanisms (ranks 9–13) all sit within 3 seed
  sd of zero; their contribution is mostly through the LFPR/EPOP channel and
  through interactions within the type-specific block, not through standalone
  UR variance.

CSV: `tables/table2_mechanism_ablation.csv`; combined ranking:
`tables/table4_ablation_ranking.csv`.

---

## 6. Heterogeneity Ladder (Package C)

### 6.1 Core ladder (nested, L0 \u2192 L6)

| level | n_active | dimensions added on this step | OOS UR RMSE (pp) | \u0394 vs L6 | seed sd | LFPR (pp) | EPOP (pp) |
|---|---:|---|---:|---:|---:|---:|---:|
| L0 | 0 | (none \u2014 fully homogeneous) | 0.553 | +0.332 | 0.007 | 8.85 | 8.78 |
| L1 | 1 | + Labor Fragility | 0.550 | +0.329 | 0.008 | 8.87 | 8.79 |
| L2 | 2 | + Labor Search Friction | **1.054** | +0.834 | 0.022 | 6.86 | 5.89 |
| L3 | 3 | + Income Growth Expectation | **1.058** | +0.837 | 0.017 | 6.92 | 5.94 |
| L4 | 4 | + Liquidity Fragility | 0.517 | +0.296 | 0.022 | 8.62 | 7.96 |
| L5 | 5 | + Housing Mobility Friction | 0.268 | +0.047 | 0.011 | 1.93 | 1.79 |
| L6 | 6 | + Consumption Adjustment Rule | **0.221** | 0.000 | 0.007 | 2.27 | 2.21 |

**Headline finding \u2014 strong non-monotonicity.** L1 is essentially L0; L2/L3
are *worse than L0* by ~0.5 pp; L4 partially recovers; L5/L6 finish below L0.
The bump at L2/L3 is the key signature: activating Search Friction without the
constraint layer (Liquidity + Housing) injects heterogeneous search behaviour
into a population that still has homogeneous liquidity and housing, producing a
mis-specified mixture that *amplifies* OOS UR error rather than reducing it.

### 6.2 Layer ladder (block additions, G2 / G3)

G1 \u2261 L2 = {labor_frag, search} and G4 \u2261 L6 = full, so only G2 and G3 are new
points.

| level | n_active | active set | OOS UR RMSE (pp) | \u0394 vs L6 | seed sd | LFPR (pp) | EPOP (pp) |
|---|---:|---|---:|---:|---:|---:|---:|
| G2 | 4 | labor_frag, search, **liquidity, housing** | 0.267 | +0.046 | 0.026 | 1.94 | 1.80 |
| G3 | 5 | G2 \u222a consumption_rule | 0.241 | +0.020 | 0.015 | 2.22 | 2.17 |

**Implication.** Adding the constraint layer (Liquidity + Housing) as a *block*
on top of {labor_frag, search} skips the non-monotonic bump entirely: G2 already
sits at 0.267 pp, only 0.046 pp above the full L6 model. G3 adds the household
consumption rule and gets within 0.020 pp of L6. The 6-dimensional system is
therefore approximately a "labor + constraint" 4-dim core plus a small household
adjustment.

### 6.3 Why L2/L3 are worse than L0

Diagnostic comparison (seed-mean):

| level | UR RMSE | LFPR RMSE | EPOP RMSE | UR Corr |
|---|---:|---:|---:|---:|
| L0 (homogeneous) | 0.553 | 8.85 | 8.78 | 0.805 |
| L2 (+ Search) | 1.054 | 6.86 | 5.89 | 0.786 |
| L4 (+ Liquidity) | 0.517 | 8.62 | 7.96 | 0.789 |
| G2 (Search + Liquidity + Housing) | 0.267 | 1.94 | 1.80 | 0.795 |

The L2 result is **not** noise: seed sd is 0.022 pp and all five seeds report
1.02\u20131.10 pp UR RMSE. Heterogeneous search intensity + flat liquidity & housing
produces excessive U\u2192E and E\u2192U churn during the 2022 reopening: agents with
high search intensity match too fast, agents with low search intensity exit too
slowly. The constraint dimensions in G2/L4/L5 dampen these flows.

CSV: `tables/table3_heterogeneity_ladder.csv`.

---

## 7. Cross-experiment consistency check

Phase 7 dimension ablation and Package C ladder are independent codepaths that
both touch the six MVP dimensions. They agree on the dominant ones:

| dimension | Phase 7 \u0394UR (pp) when flattened alone | Package C \u0394UR (pp) at level where dimension is first added |
|---|---:|---:|
| Labor Search Friction | +0.889 | +0.504 (L1\u2192L2 step) |
| Liquidity Fragility | +0.299 | \u22120.541 (L3\u2192L4 step \u2014 *adds*, hence negative \u0394) |
| Housing Mobility Friction | +0.162 | \u22120.249 (L4\u2192L5 step) |
| Consumption Adjustment Rule | +0.047 | \u22120.047 (L5\u2192L6 step) |
| Labor Fragility | +0.023 | \u22120.003 (L0\u2192L1 step) |
| Income Growth Expectation | +0.020 | +0.004 (L2\u2192L3 step) |

Signs and magnitudes are mutually consistent: flattening Search hurts (+0.889);
adding it on top of homogeneity also hurts (+0.504) when unbalanced. Adding
Liquidity is the largest single-step *gain* in the ladder (\u22120.541 pp at L4),
matching the +0.299 pp loss seen when Liquidity is flattened in Phase 7.

The two experiments measure complementary things \u2014 Phase 7 isolates one
dimension at a time against the full backdrop; Package C measures cumulative
behaviour as dimensions are stacked \u2014 and converge on the same conclusion:
**Search + Liquidity + Housing carry essentially all the UR-relevant
heterogeneity signal, with a strong coupling that prevents incremental adoption.**

---

## 8. Reconciliation with prior (3-seed) outputs

| source | dim Search \u0394 (pp) | dim Liquidity \u0394 (pp) | dim Housing \u0394 (pp) | L2 UR RMSE (pp) | L6 UR RMSE (pp) |
|---|---:|---:|---:|---:|---:|
| Old `phase7/ablation_results.json` (3 seeds) | +0.881 | +0.294 | +0.158 | 1.071 | 0.226 |
| New 5-seed (this report) | +0.889 | +0.299 | +0.162 | 1.054 | 0.221 |
| absolute delta | 0.008 | 0.005 | 0.004 | 0.017 | 0.005 |

All deltas are < 0.02 pp; the rank order is identical; the "Search dominates"
and "L2 is worse than L0" conclusions are unchanged. The differences are
explained entirely by the 3 \u2192 5 seed expansion (the model code, mechanism
config and macro data are bit-identical).

---

## 9. UR vs LFPR / EPOP trade-offs

A key finding from Section 6.2 carries through to 6.3: the model's six
heterogeneity dimensions and 13 mechanisms do *not* all push the three labor
market targets in the same direction. The table below highlights the largest
trade-offs.

| ablation | UR RMSE (pp) | LFPR RMSE (pp) | EPOP RMSE (pp) | UR vs Full | LFPR vs Full | EPOP vs Full |
|---|---:|---:|---:|---|---|---|
| Full heterogeneous ABM | 0.221 | 2.27 | 2.21 | \u2014 | \u2014 | \u2014 |
| Flatten Liquidity Fragility | 0.520 | **0.47** | **0.32** | worse | **better** | **better** |
| Flatten Labor Fragility | 0.244 | 2.31 | 2.25 | tied | tied | tied |
| Flatten Search Friction | 1.110 | 3.79 | 4.35 | worse | worse | worse |
| Flatten Housing | 0.383 | 8.95 | 8.38 | worse | catastrophic | catastrophic |
| Disable `matching_competition` | 2.146 | **0.77** | 2.01 | catastrophic | **better** | tied |
| Disable `housing_reentry_friction` | 0.396 | 8.36 | 7.81 | worse | catastrophic | catastrophic |

**Reading.** Flattening Liquidity *improves* the joint LFPR/EPOP fit by ~1.9 pp
while degrading UR by 0.30 pp. This mirrors the Section 6.2 "household block
trade-off" \u2014 the household-side dimensions over-fit UR at the cost of LFPR/EPOP.
Disabling `matching_competition` does the same thing more extremely on LFPR
(0.77 pp vs 2.27 pp), but at a UR cost so large (2.15 pp) that no paper claim
should rest on it.

Figure 4 (`figures/fig4_ur_lfpr_epop_tradeoff.png`) plots these on log-y to
keep the wide dynamic range visible.

---

## 10. Robustness and sanity checks

1. **Seed stability of the headline.** The Search-Friction \u0394 is 0.889 \u00b1 0.020 pp
   across 5 seeds \u2014 noise is ~2% of the effect. Liquidity \u0394 = 0.299 \u00b1 0.031.
   These rankings would not change under any reasonable seed reshuffle.
2. **Baseline reproducibility.** The 5-seed baseline UR RMSE (0.2211 pp) matches
   Section 6.1 and Section 6.2 to 4 decimal places; the ablation and ladder
   scripts use the same engine entrypoints (`run_phase7_ablation_v2`,
   `Simulation` via `packageC_engine`).
3. **Mechanism + dimension consistency.** The mechanism-side total for the
   housing block (`housing_reentry_friction` +0.175, `housing_lockin_modifier`
   +0.019 \u2192 sum +0.194 pp) brackets the dimension-side housing flatten
   (+0.162 pp), confirming the two ablation modes measure overlapping but not
   identical objects.
4. **Macro inputs unchanged.** No edits to `Phase3_Code/` between Sections 6.1,
   6.2 and 6.3; the same `RealEnvironment` is used.
5. **Population unchanged.** The same `Phase2_Output/population_v1.npz`
   (100,000 agents, NY Fed SCE moments) is loaded by every ablation and every
   ladder level; no agent resampling.
6. **Ladder seed sd peaks at the non-monotonic bump.** L2 sd = 0.022 pp, L3
   sd = 0.017 pp; the rest are \u2264 0.011 pp (except G2 at 0.026). The bump is
   structural, not a single bad seed.

---

## 11. Connection to Sections 6.1 and 6.2

- **Section 6.1** established baseline OOS UR RMSE = 0.221 pp with high
  trajectory correlation (0.79). Section 6.3 confirms this baseline as the
  reference point for every ablation.
- **Section 6.2** decomposed the source of advantage as 97.6% heterogeneity vs
  2.4% mechanism (Simplified \u2192 Full path). Section 6.3 refines this:
  - Of the 97.6% heterogeneity share, **the Search + Liquidity + Housing
    sub-block carries the visible UR portion**; the household-side dimensions
    (Consumption Rule, Labor Fragility, Income Expectation) move UR by < 0.05 pp
    each but matter for LFPR/EPOP and for interactions inside the ladder.
  - Of the 2.4% mechanism share, **`matching_competition` is the carrier**: it
    is the single mechanism whose presence converts the homogeneous backbone
    into something that even responds to heterogeneity in the first place.
    Disabling it produces a 1.92-pp UR penalty \u2014 larger than any other single
    toggle in the model.
- **Section 6.3** therefore tells the paper's central methodology story: the
  predictive advantage is not located in any single piece, but in the
  *coupling* between (a) the matching mechanism and (b) the labor-search and
  constraint heterogeneity dimensions.

---

## 12. Paper-ready wording (safe to copy)

> Single-dimension ablations show that **Labor Search Friction** is the
> dominant heterogeneity carrier of out-of-sample UR fit: flattening it raises
> OOS UR RMSE from 0.22 pp to 1.11 pp (\u0394 = +0.89 pp, 5 seeds, std 0.02). The
> second- and third-ranked dimensions are **Liquidity Fragility** (\u0394 = +0.30 pp)
> and **Housing Mobility Friction** (\u0394 = +0.16 pp); the remaining three
> dimensions move UR RMSE by less than 0.05 pp each, but contribute to LFPR/EPOP
> and to multi-dimension interactions documented below.

> Mechanism ablations identify **matching competition** \u2014 the finite-vacancy,
> competition-based allocation rule of the labor block \u2014 as the dominant
> structural mechanism: disabling it raises OOS UR RMSE to 2.15 pp (\u0394 =
> +1.93 pp), the largest single-toggle effect across the 19 ablations tested.
> All other mechanisms move UR RMSE by less than 0.20 pp.

> A nested heterogeneity ladder (L0\u2192L6, dimensions added one at a time) reveals
> a strongly **non-monotonic** path: activating heterogeneous search on top of
> a homogeneous household population (L2) raises OOS UR RMSE *above* the
> homogeneous L0 level (1.05 pp vs 0.55 pp), and recovery only occurs once the
> liquidity and housing constraint dimensions are also activated (L4 = 0.52,
> L5 = 0.27, L6 = 0.22 pp). A complementary block-addition ladder confirms
> that adding the constraint layer simultaneously with search (G2 = 0.27 pp)
> avoids the bump entirely. The model's predictive value therefore originates
> in the *coupling* of search and constraint heterogeneity, not in any single
> dimension considered in isolation.

> All numbers reported above use the same FRED/BLS macro inputs, the same
> 14-parameter baseline, and the same 100,000-agent population as Sections 6.1
> and 6.2; the out-of-sample window (2022-01\u20132026-02) is the same throughout.

---

## 13. Wording to avoid (sanity checklist)

- Do **not** describe the dimensions as "psychological personality traits" \u2014
  they are survey-anchored heterogeneity in expectations, search behaviour, and
  balance-sheet positions.
- Do **not** quote 97.6% (the Section 6.2 *heterogeneity-vs-mechanism* share)
  as the "Search Friction share". The 0.89 pp \u0394 from Search is a *standalone*
  ablation effect, not a decomposition of the 0.34 pp Simplified\u2192Full gain.
- Do **not** call Phase 7 and Package C "the same experiment"; Phase 7 is
  one-dimension-out, Package C is cumulative-dimension-in.
- Do **not** claim the OOS window is "untouched" \u2014 the OOS window is used for
  *evaluation*, not for fitting, and Section 6.3 explicitly reports OOS RMSE.
- Do **not** use model engineering names (M0, D1, D2, D3, Model C) in the
  final paper text; use "Full heterogeneous ABM" / "Simplified ABM" /
  "Homogeneous ABM" / "Labor-only ABM" as established in Section 6.2.
- Do **not** interpret the L2/L3 bump as a coding bug \u2014 the seed sd (0.022 pp)
  is small relative to the +0.5 pp effect, and Section 7 shows the result is
  consistent across both ablation experiments.
- Do **not** describe `matching_competition` as a "calibrated parameter"; it
  is a structural mechanism toggle, not a numerical fit.

---

## 14. Evidence appendix

All outputs are in `\u6b63\u5f0f\u64b0\u5199/6.3/`.

**Scripts (this section only):**
- `run_6_3_phase7_ablation.py` \u2014 5-seed Phase 7 ablation (1 + 6 + 13 = 20 configs)
- `run_6_3_packageC_ladder.py` \u2014 5-seed Package C ladder (9 levels)
- `build_6_3_artifacts.py` \u2014 generates the five CSV tables and five PNG figures

**Raw outputs:**
- `ablation_metrics.json` \u2014 per-seed metrics for all 20 ablation variants
- `ablation_series.npz` \u2014 monthly UR/LFPR/EPOP trajectories (5 seeds, all variants)
- `ladder_metrics.json` \u2014 per-seed metrics for all 9 ladder levels
- `ladder_series.npz` \u2014 monthly trajectories for ladder levels
- `rerun_log_ablation.txt`, `rerun_log_ladder.txt` \u2014 console logs with per-seed timings

**Tables (CSV):**
- `tables/table1_dimension_ablation.csv`
- `tables/table2_mechanism_ablation.csv`
- `tables/table3_heterogeneity_ladder.csv`
- `tables/table4_ablation_ranking.csv`
- `tables/table5_paper_ready_compact.csv`

**Figures (PNG):**
- `figures/fig1_dimension_ablation_bar.png` \u2014 dimension \u0394UR with seed sd bars
- `figures/fig2_mechanism_ablation_bar.png` \u2014 mechanism \u0394UR coloured by block
- `figures/fig3_heterogeneity_ladder.png` \u2014 L0\u2192L6 plus G2/G3 with non-monotonic bump
- `figures/fig4_ur_lfpr_epop_tradeoff.png` \u2014 UR/LFPR/EPOP for selected ablations (log-y)
- `figures/fig5_search_friction_path.png` \u2014 baseline vs Search-flattened OOS trajectory

**Cross-references:**
- Baseline configuration: `Phase3_Output/phase6/candidate_baseline.json`
- Mechanism definitions: `Phase3_Code/mechanism_config.py`
- Dimension flatten code: `Phase3_Code/phase7_engine.py:126-154`
- Ladder definitions: `Phase3_Code/packageC_engine.py:22-44`
- Data sources: `Data_Verification_Report.md`
- Model structure: `Model_Overview_Verification_Report.md`

End of preparation report.

