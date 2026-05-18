# Results §6.3 — Recalibrated Heterogeneity Ablation and Coupled Heterogeneity
## Preparation Report

**Status.** Final. Calibration wall time 201.3 min; re-evaluation 23.1 min; all numbers
below are derived from `calibration_results.json`, `reeval_metrics.json`, and the seven
tables in `正式撰写/fix6.3/tables/`.

---

## 1. Executive Summary

This revision replaces the legacy §6.3 — in which each "ablation" variant inherited the
Full model's calibrated parameter vector and only flattened one heterogeneity dimension
— with a protocol in which **every ablation variant is re-calibrated separately on the
same training window**, under the same LHS budget and loss function as the recalibrated
controls of §6.2. The aim is to test whether the heterogeneity dimensions identified in
the legacy §6.3 (especially Labor Search Friction with its ΔUR = +0.889 pp) still appear
important once each ablated variant is given the chance to re-optimise its remaining
parameters.

**Headline result.** Of the three dimensions singled out by the legacy §6.3, **only
Labor Search Friction retains a structurally large post-COVID degradation after
re-calibration**:

| Dimension flattened | Old raw ΔUR (pp) | New recalibrated ΔUR (pp) | Closing of gap |
|---|---:|---:|---:|
| Search Friction (`V_NoSearch`)   | +0.889 | **+0.812** | −0.077 pp (≈9 %) |
| Liquidity Fragility (`V_NoLiquidity`) | +0.299 | +0.105 | −0.194 pp (≈65 %) |
| Housing Mobility (`V_NoHousing`)   | +0.162 | **−0.036** | sign flip |
| Consumption Rule (`V_NoConsumption`) | +0.040 | −0.025 | sign flip |
| Search+Liq+Housing block (`V_NoSLH`) |  n/a   | +0.429 | (new variant) |
| Search-only kept (`V_SearchOnly`)   |  n/a   | +0.037 | (new variant) |

Δ is RMSE_UR(variant) − RMSE_UR(Full) on the post-COVID normalization window
(2022-01 .. 2026-02, 49 months, mean of 5 final seeds × top-1 candidate).

Two qualitative conclusions follow:

1. **Search Friction is the only single dimension whose post-COVID degradation
   survives fair re-calibration**: 91 % of the legacy ΔUR remains.
2. **Liquidity Fragility and Housing Mobility are much weaker than the legacy §6.3
   suggested**: re-calibration of the surrounding parameters either substantially
   shrinks the gap (Liquidity: 65 % closed) or flips its sign (Housing). The legacy
   numbers were therefore partly attributable to parameter mis-match, not to the
   structural absence of the dimension.

The 4-dim variant V_SearchOnly (only Search heterogeneity preserved) recovers Full's
post-COVID UR RMSE (Δ = +0.037 pp) but pays a price on the training window and
pre-COVID stability, consistent with Liquidity/Housing/Consumption providing weakly
identified but jointly useful auxiliary structure. The 3-dim block variant V_NoSLH has a
moderate Δ = +0.429 pp post-COVID, smaller than Search alone — indicating non-additive
interactions among the three dimensions and weak identifiability under recalibration.

These findings are *experiment-internal* decompositions of forecast accuracy. **They are
not causal mechanism identifications**; survey-anchored heterogeneity in this framework
is descriptive, not behavioural.

The seven variants in scope are:

| Paper name | Code id | Flattened dims | Active dims | Mechanisms | Active params |
|---|---|---|---:|---|---:|
| Full heterogeneous ABM           | `V_Full`           | — | 6 | all 13 ON | 14 |
| No Search Friction ABM           | `V_NoSearch`       | `search` | 5 | all 13 ON | 14 |
| No Liquidity Fragility ABM       | `V_NoLiquidity`    | `liquidity` | 5 | all 13 ON | 14 |
| No Housing Mobility ABM          | `V_NoHousing`      | `housing` | 5 | all 13 ON | 14 |
| No Search-Liquidity-Housing ABM  | `V_NoSLH`          | `search`+`liquidity`+`housing` | 3 | all 13 ON | 14 |
| No Consumption Rule ABM          | `V_NoConsumption`  | `consumption_rule` | 5 | all 13 ON | 14 |
| Search-only heterogeneity ABM    | `V_SearchOnly`     | `liquidity`+`housing` | 4 | all 13 ON | 14 |

The `V_Full` reference is reused verbatim from §6.2 (identical specification: 14 params,
no flattening, all 13 mechanisms ON, 100 LHS × 3 seeds, top-5 reeval × 5 seeds). The six
ablation variants are calibrated independently with the same protocol.

---

## 2. Why this revision was needed

The legacy §6.3 reported ΔUR RMSE = +0.889 pp for flattening Search Friction, +0.299 pp
for Liquidity, +0.162 pp for Housing — but these deltas were measured with **the Full
model's calibrated parameter vector**, so a fraction of the ΔUR may have reflected
parameter mis-match rather than the structural absence of the dimension. The §6.2
recalibration exercise showed precisely this effect for full-block controls
(Homogeneous and Simplified RMSEs dropped 4× after fair recalibration). For §6.3, the
question is now: *under separately optimised parameters, does removing each individual
dimension still produce a measurable degradation in post-COVID UR tracking?*

This conflates two questions a fair decomposition should keep separate:
"how much does each dimension contribute *after each variant is given its best shot*?"
vs. "how much does the Full model gain by being allowed to tune to its own structure?"

The revision answers the first question.

---

## 3. Methodology

### 3.1 Calibration protocol (identical to §6.2)
- Sampler: Latin Hypercube, bounds from `Phase3_Code/calibration_engine.PARAM_SPACE`.
- LHS budget: **100 draws × 3 seeds** per ablation variant.
- All variants have all 14 parameters active (mechanisms are all ON; only the agent state
  is modified by `flatten_heterogeneity` post `Simulation()` init).
- Training window: 2004-01..2017-12 (indices 36..204 of the 302-month history).
- Loss formula (same as §6.2):
  `L = 5·UR_RMSE + 2·LFPR_RMSE + 2·EPOP_RMSE + |EU−0.015|·10 + |UE−0.25|·5 + 0.5·|H2M−0.30|·2`.
- Selection criterion: lowest mean train loss across the 3 seeds.

### 3.2 Re-evaluation protocol
- Top-5 candidates per variant re-evaluated on 5 final seeds {42, 137, 2024, 888, 1234}.
- Rank-1 of top-5 = "best model" per variant.
- Eight reporting windows match those defined in §6.1/§6.2: pre-COVID stable
  (2018-01..2019-12), COVID crisis Mar/Jan starts, post-COVID normalization
  (2022-01..2026-02), full post-2018, train, validation, original OOS.

### 3.3 Single-dimension flattening
`flatten_heterogeneity(cs, ds, bp, dim)` in `Phase3_Code/phase7_engine.py:126-154`
replaces a single dimension's continuous columns with the population median and forces
the categorical column to the dim's middle category (e.g. `LIQ_BUFFER` for liquidity,
`HSG_RENT_STB` for housing). This preserves the mechanism's engagement but removes the
behavioural dispersion across agents.

For `V_NoSLH` and `V_SearchOnly` the same function is invoked once per dimension on the
same `(cs, ds, bp)` arrays after `Simulation()` init.

### 3.4 Delta and interpretation rules
Let `R(v) = RMSE_UR(v, post_covid_norm)` after recalibration. For each ablation,
`Δ(v) = R(v) − R(Full)` in pp. Rules:
- Δ > 0.15 pp: dimension is structurally hard to replace within this framework.
- 0 < Δ ≤ 0.15 pp: mild loss; recalibration partly compensates.
- Δ ≤ 0 pp: removing the dimension does not hurt (and may help) once parameters
  are re-tuned — suggests the dimension's role is substitutable.
- All-bad in crisis: crisis tracking is dominated by other forces.

This is an *experiment-internal* decomposition, **not** a causal mechanism
identification.

---

## 4. Calibration results (Table 1)

Top-1 mean training loss across 3 LHS seeds, per variant:

| Variant | Flattened | Top-1 train loss | Top-1 train UR RMSE (pp) | LHS cand. idx |
|---|---|---:|---:|---:|
| `V_Full`           | (none)                       | 0.1672 | 1.258 | 32 (reused from §6.2) |
| `V_NoSearch`       | search                       | 0.2621 | 1.969 | 48 |
| `V_NoLiquidity`    | liquidity                    | 0.3736 | 1.265 | 77 |
| `V_NoHousing`      | housing                      | 0.2031 | 1.591 | 79 |
| `V_NoSLH`          | search+liquidity+housing     | 0.4667 | 1.206 | 14 |
| `V_NoConsumption`  | consumption_rule             | 0.1841 | 1.295 | 60 |
| `V_SearchOnly`     | liquidity+housing            | 0.4299 | 1.484 | 61 |

The training-window total-loss ordering already foreshadows the test-window picture:
`V_NoSearch` and the multi-dim variants (`V_NoSLH`, `V_SearchOnly`) cannot match Full's
0.167 even with 100 fresh LHS draws, while `V_NoConsumption` and `V_NoHousing` reach
loss values within 10–22 % of Full. `V_NoLiquidity` is intermediate.

The total wall time across the six new variants was **201.3 min**.

---

## 5. Post-COVID normalization ablation results (Table 2, Figure 1)

Best-candidate (rank-1) mean UR RMSE on 2022-01 .. 2026-02 (49 months), averaged over
the 5 final seeds:

| Variant | UR RMSE (pp) | seed sd (pp) | Δ vs Full (pp) | Corr | Bias (pp) |
|---|---:|---:|---:|---:|---:|
| Full heterogeneous ABM           | **0.273** | 0.023 | 0.000  | 0.764 | −0.167 |
| No Search Friction ABM           | 1.085 | 0.011 | **+0.812** | 0.780 | −1.052 |
| No Liquidity Fragility ABM       | 0.378 | 0.045 | +0.105 | 0.750 | +0.266 |
| No Housing Mobility ABM          | 0.237 | 0.016 | −0.036 | 0.735 | +0.064 |
| No Search-Liquidity-Housing ABM  | 0.703 | 0.015 | +0.429 | 0.796 | −0.629 |
| No Consumption Rule ABM          | 0.248 | 0.025 | −0.025 | 0.794 | +0.100 |
| Search-only heterogeneity ABM    | 0.310 | 0.024 | +0.037 | 0.728 | +0.168 |

Three patterns emerge:

1. **Search Friction is the only single dimension whose removal produces a structurally
   large loss** (+0.812 pp, ≈ 4× Full's RMSE). After re-calibration the remaining
   parameters cannot reroute through other dimensions to recover Full's tracking quality
   — the bias of −1.052 pp shows that the model now systematically under-predicts UR.

2. **Housing and Consumption removal produces no measurable degradation** (Δ ≤ 0). The
   recalibrated `V_NoHousing` and `V_NoConsumption` actually match Full to within seed
   noise. This is the strongest evidence that the legacy ΔUR numbers for these
   dimensions were largely parameter-fit artefacts.

3. **Liquidity removal produces a small but positive Δ = +0.105 pp**. Roughly two
   thirds of the legacy +0.299 pp gap is closed by re-calibration, but a residual
   ≈ 0.1 pp survives.

Figure 1 (`fig1_recalibrated_ablation_ur.png`) renders the five paper-facing variants
as a bar chart with seed-sd error bars. Figure 4 plots Full vs No-Search UR
trajectories across 2018-01..2026-02.

---

## 6. COVID crisis ablation results (Table 3)

Best-candidate mean UR RMSE on 2020-03 .. 2021-12 (22 months):

| Variant | UR RMSE (pp) | seed sd | Δ vs Full (pp) | Corr |
|---|---:|---:|---:|---:|
| Full heterogeneous ABM           | 2.974 | 0.024 | 0.000  | 0.759 |
| No Search Friction ABM           | 3.446 | 0.020 | +0.472 | 0.826 |
| No Liquidity Fragility ABM       | 2.640 | 0.033 | −0.334 | 0.766 |
| No Housing Mobility ABM          | 2.922 | 0.022 | −0.052 | 0.728 |
| No Search-Liquidity-Housing ABM  | 2.892 | 0.034 | −0.082 | 0.848 |
| No Consumption Rule ABM          | 2.795 | 0.034 | −0.180 | 0.752 |
| Search-only heterogeneity ABM    | 2.806 | 0.026 | −0.169 | 0.752 |

Crisis-window RMSEs are 5–13× larger than the post-COVID window for every variant;
**the absolute level of crisis tracking error is essentially insensitive to which
heterogeneity dimension is flattened**. The only positive Δ on this window is again
Search (+0.472 pp); all other variants tie or slightly improve, suggesting their roles
in COVID are absorbed by the LFPR/EPOP balance rather than by behavioural dispersion.

This corroborates the §6.2 finding that crisis-window predictability is structurally
limited under all recalibrated specifications.

---

## 7. Pre-COVID stable ablation results (Table 4)

Best-candidate mean UR RMSE on 2018-01 .. 2019-12 (24 months):

| Variant | UR RMSE (pp) | seed sd | Δ vs Full (pp) |
|---|---:|---:|---:|
| Full heterogeneous ABM           | 0.609 | 0.050 | 0.000  |
| No Search Friction ABM           | 0.284 | 0.015 | **−0.325** |
| No Liquidity Fragility ABM       | 1.036 | 0.065 | +0.427 |
| No Housing Mobility ABM          | 0.818 | 0.041 | +0.209 |
| No Search-Liquidity-Housing ABM  | 0.476 | 0.050 | −0.133 |
| No Consumption Rule ABM          | 0.883 | 0.044 | +0.274 |
| Search-only heterogeneity ABM    | 0.867 | 0.030 | +0.258 |

The pre-COVID ranking **inverts** the post-COVID ranking: in the stable 2018-19 window
`V_NoSearch` *beats* `V_Full` by 0.325 pp, while `V_NoLiquidity`, `V_NoHousing`,
`V_NoConsumption`, and `V_SearchOnly` all degrade by +0.2 to +0.4 pp. Interpretation:
the Full model's search-friction-driven mechanism is mildly mis-fit to the 2018-19
disinflationary-tightening regime, where the labour market was essentially at full
employment; flattening search lets the re-calibrated model find a better stable-state
attractor. Removing the household-side dimensions (liquidity, housing, consumption)
hurts stable-window tracking, presumably because participation persistence is encoded
in those dispersions.

This pre-/post-COVID inversion is itself a substantive finding for the paper: **no
single dimension is universally important — Search Friction matters most in the
post-COVID adjustment, household-block dispersion matters most in the pre-COVID stable
regime**.

---

## 8. Old raw ablation vs new recalibrated ablation (Table 5, Figure 2)

| Dimension | Old raw ΔUR (pp) | New recalibrated ΔUR (pp) | Gap reduction |
|---|---:|---:|---:|
| Search Friction    | +0.889 | **+0.812** | −0.077 pp (≈9 %)  |
| Liquidity Fragility | +0.299 | +0.105 | −0.194 pp (≈65 %) |
| Housing Mobility   | +0.162 | −0.036 | sign flip       |
| Consumption Rule   | +0.040 | −0.025 | sign flip       |

Figure 2 (`fig2_old_vs_new_delta.png`) renders the three legacy-comparable rows as
grouped bars. The **Search Friction column is the only one where re-calibration does
not eliminate the original gap**. This is the cleanest evidence the new protocol can
produce that the legacy §6.3 Search finding is robust to fair re-calibration; the
Liquidity and Housing legacy findings, by contrast, are not.

The reduction interpretation: re-calibration of the remaining 14 parameters lets the
ablated model recover most of the legacy gap *for Liquidity and Housing*, but recovers
< 10 % of it *for Search*. Search-friction dispersion is therefore the dimension whose
behavioural content is least substitutable by other parameters in this framework.

---

## 9. Search–Liquidity–Housing block interpretation

Two block-level variants probe how the three dimensions interact:

- `V_NoSLH` (flatten all three): post-COVID Δ = +0.429 pp.
- `V_SearchOnly` (flatten Liquidity and Housing, keep Search): post-COVID Δ = +0.037 pp.

Two non-additive observations:

1. **Removing Search alone (+0.812) is worse than removing the whole SLH block
   (+0.429).** This counter-intuitive ordering implies that once Liquidity and Housing
   dispersion are also flattened, the calibration finds a different parameter region
   that partly compensates for the loss of Search dispersion. The three dimensions are
   **jointly under-identified** — removing more lets the calibrator escape the
   constraint that Search dispersion would otherwise impose.

2. **Keeping only Search dispersion (V_SearchOnly) matches Full to within 0.04 pp on
   post-COVID.** Combined with point 1, this says Search is the *necessary but
   together-with-others under-determined* dimension for post-COVID UR tracking.

These results should not be over-interpreted: in this 14-parameter LHS regime, the
loss surface is flat enough that 0.1–0.4 pp differences in OOS RMSE can sit inside the
calibration's identifiability slack. The §6.2 weak-identifiability caveat applies here
as well.

---

## 10. LFPR / EPOP trade-offs (Figure 5)

`V_NoLiquidity`, `V_NoConsumption`, and `V_NoHousing` achieve their similar UR scores
in part by sacrificing LFPR/EPOP fit:

| Variant | UR RMSE (pp) | LFPR RMSE (pp) | EPOP RMSE (pp) |
|---|---:|---:|---:|
| Full heterogeneous ABM           | 0.273 | 4.83 | 4.76 |
| No Search Friction ABM           | 1.085 | 5.67 | 6.16 |
| No Liquidity Fragility ABM       | 0.378 | **2.89** | **2.61** |
| No Housing Mobility ABM          | 0.237 | 4.44 | 4.23 |
| No Search-Liquidity-Housing ABM  | 0.703 | 8.17 | 8.29 |
| No Consumption Rule ABM          | 0.248 | 3.54 | 3.34 |
| Search-only heterogeneity ABM    | 0.310 | 3.89 | 3.63 |

Two opposing trade-offs:

- Flattening **household-block dispersions** (Liquidity, Consumption, partly Housing)
  *improves* LFPR/EPOP tracking by 1–2 pp while modestly degrading UR. The
  re-calibrated UR weight (5×) in the loss function dominates these solutions, but the
  LFPR/EPOP improvement is consistent across all three.
- Flattening **labour-block dispersions** (Search alone, or SLH block) *degrades*
  LFPR/EPOP tracking. The all-3-block V_NoSLH has the worst LFPR (8.17) and EPOP (8.29).

This is the joint-fit version of the §6.2 conclusion: **Search Friction is the only
dimension that simultaneously matters for UR, LFPR, and EPOP** in the post-COVID
window.

---

## 11. Figures and tables generated

```
正式撰写/fix6.3/
  tables/
    table1_calibration_summary.csv
    table2_post_covid_ablation.csv
    table3_crisis_ablation.csv
    table4_precovid_ablation.csv
    table5_old_vs_new_delta.csv
    table6_regime_x_ablation.csv
    table7_paper_ready.csv
  figures/
    fig1_recalibrated_ablation_ur.png
    fig2_old_vs_new_delta.png
    fig3_regime_x_ablation_heatmap.png
    fig4_no_search_trajectory.png
    fig5_lfpr_epop_tradeoff.png
```

---

## 12. Recommended wording for revised §6.3

The following is a paper-ready draft, ≈ 750 words, suitable for direct insertion as
§6.3 of the Results chapter. Numbers and table/figure references all resolve to the
artefacts in `正式撰写/fix6.3/`.

> **6.3 Recalibrated Heterogeneity Ablation and Coupled Heterogeneity**
>
> The recalibrated controls of §6.2 established that survey-anchored heterogeneity, as
> a block, contributes the majority of the Full ABM's post-COVID unemployment-rate
> tracking advantage. §6.3 isolates the contribution of individual heterogeneity
> dimensions — Labor Search Friction, Liquidity Fragility, and Housing Mobility — under
> the same fair-recalibration protocol. The legacy ablation results, in which each
> ablated variant inherited the Full model's calibrated parameter vector and only
> flattened one dimension, attributed unemployment-rate degradations of +0.889 pp,
> +0.299 pp, and +0.162 pp respectively to these three dimensions. Because the ablated
> variants were not given the chance to re-optimise their remaining parameters, those
> degradations may have reflected parameter mis-match rather than the irreplaceable
> behavioural content of each dimension.
>
> To address this, six new variants were calibrated independently (100 LHS draws × 3
> seeds each; same loss function and training window as §6.2). Each variant flattens
> one or more agent-state dimensions to the population median/mode while keeping all
> 13 mechanism switches active and all 14 calibration parameters free. The variants are
> *No Search Friction* (flattens search), *No Liquidity Fragility* (flattens liquidity),
> *No Housing Mobility* (flattens housing), *No Search-Liquidity-Housing* (flattens all
> three), *No Consumption Rule* (flattens consumption), and *Search-only* (flattens
> liquidity and housing, keeps search). The Full reference is the same calibration used
> in §6.2 (top-5 reeval × 5 seeds; identical seed set).
>
> Table 7 summarises the post-COVID UR RMSE on the normalization window
> (2022-01..2026-02, 49 months, mean of 5 final seeds). Three results stand out. First,
> removing search-friction heterogeneity raises the post-COVID UR RMSE from 0.273 pp to
> 1.085 pp (Δ = +0.812 pp), with a systematic under-prediction bias of −1.05 pp; the
> remaining 13 parameters cannot reproduce Full's tracking quality. Second, removing
> liquidity heterogeneity raises the RMSE to 0.378 pp (Δ = +0.105 pp), about two-thirds
> smaller than the legacy +0.299 pp gap. Third, removing housing or consumption
> heterogeneity produces a small negative Δ (−0.036 pp and −0.025 pp, both within the
> seed-noise band), so re-calibration fully compensates for these dimensions.
> Comparing legacy and recalibrated deltas (Table 5, Figure 2), only the search-friction
> gap survives the fair protocol with negligible reduction; the liquidity gap shrinks by
> ~65 % and the housing gap flips sign.
>
> The cross-regime view (Table 6) qualifies this story. In the pre-COVID stable window
> (2018-01..2019-12, Table 4), the variant that flattens search actually outperforms
> Full by 0.325 pp, while flattening any of the three household-block dimensions
> degrades stable-window tracking by +0.21 to +0.43 pp. The two regimes therefore
> attribute predictive value to different dimensions: search-friction dispersion drives
> post-COVID adjustment dynamics, household-block dispersion drives stable-state
> participation persistence. In the COVID crisis window (2020-03..2021-12, Table 3),
> all variants score between 2.64 and 3.45 pp RMSE, with the search-flattened variant
> the only positive Δ (+0.47 pp); crisis-window tracking is broadly insensitive to
> heterogeneity composition, consistent with the §6.2 conclusion that recalibration
> alone cannot recover crisis predictability under any specification.
>
> Two block-level variants probe interactions. Flattening all three dimensions at once
> (No Search-Liquidity-Housing) produces a post-COVID Δ = +0.429 pp — smaller, not
> larger, than flattening search alone. Symmetrically, keeping only search dispersion
> while flattening liquidity and housing (Search-only) produces Δ = +0.037 pp, almost
> matching Full. These non-additive observations indicate weak joint identifiability:
> once two of the three dimensions are flattened, the recalibrator finds parameter
> regions that recover most of the lost tracking quality. Within the framework's
> identifiability slack, search-friction dispersion is necessary but jointly
> under-determined with the other two. Joint-fit LFPR/EPOP results (Table 2 columns,
> Figure 5) reinforce the same hierarchy: only the search-flattened and three-block
> variants worsen LFPR/EPOP, while flattening household-block dimensions improves
> LFPR/EPOP tracking at the cost of mild UR degradation.
>
> Taken together, the recalibrated ablations refine but do not overturn the legacy §6.3
> story. Labor-search-friction heterogeneity remains the single irreplaceable
> behavioural dimension for post-COVID UR forecasting; liquidity and housing
> heterogeneity have predictive value that is largely substitutable by other parameters
> after fair recalibration; and the three-dimension block is identifiable only in the
> aggregate, not individually. We emphasise that the ablation deltas are
> experiment-internal accuracy decompositions of forecast error and should not be
> interpreted as causal-mechanism identifications.

---

## 13. Wording to avoid

1. Do not quote the legacy ΔUR = +0.889 pp for Search Friction as a stable estimate
   — the recalibrated number is +0.812 pp.
2. Do not mix raw and recalibrated ablation deltas in the same column without label.
3. Do not interpret the new deltas as causal mechanism identification.
4. Do not report only the post-COVID window — pre-COVID and crisis numbers reveal
   regime-specific dimension roles and the non-recoverability of crisis predictability.
5. Do not describe survey-anchored heterogeneity as "personality traits".
6. Do not use M0 / D1 / D2 / D3 / Model C as paper-facing names; use the long names
   in §1 of this report.
7. Do not confuse decimals with percentage points (target_ur is stored in [0, 1];
   RMSE is multiplied by 100 to obtain pp).
8. Do not claim Liquidity Fragility is a robust dimension on the basis of the legacy
   +0.299 pp delta — under fair recalibration only +0.105 pp survives.
9. Do not claim that the three-dimension block is an additive sum of single-dimension
   deltas; the recalibration interactions are clearly non-additive
   (single-Search = +0.812 pp, all-3 block = +0.429 pp).

---

## 14. Evidence appendix

### A. Output artefacts

| File | Bytes | Purpose |
|---|---:|---|
| `calibration_results.json` | 154 694 | Top-5 indices, train losses, best params for all 6 new variants |
| `reeval_metrics.json`      | 1 528 396 | 8-window metrics, 6 variants × top-5 × 5 seeds |
| `reeval_trajectories.npz`  | 682 725 | UR/LFPR/EPOP trajectories (n_cand=5, n_seed=5, n_month=302) |
| `tables/*.csv`             | — | 7 tables (calibration summary, 3 regime tables, old-vs-new delta, regime × variant grid, paper-ready) |
| `figures/*.png`            | — | 5 figures (post-COVID bar, old/new comparison, regime × variant heatmap, Full vs No-Search trajectory, LFPR/EPOP trade-off) |

### B. Reproducibility

- Calibration: `python 正式撰写/fix6.3/run_fix6_3_calibrate.py` (resume-capable via
  `checkpoints/*_progress.csv`; 201.3 min wall on dev workstation).
- Re-evaluation: `python 正式撰写/fix6.3/run_fix6_3_reeval.py` (23.1 min wall).
- Artefacts: `python 正式撰写/fix6.3/build_fix6_3_artifacts.py` (< 1 min).
- All scripts read `Phase3_Code/calibration_engine.PARAM_SPACE` for parameter bounds and
  the same `compute_total_loss` / `compute_param_targets` functions as §6.2.
- The `V_Full` row is the §6.2 calibrated Full reference, reused verbatim
  (same seed set, same loss, same training window).

### C. Wall-time summary

| Stage | Wall time |
|---|---:|
| 6-variant calibration (1 700 simulations after resume) | 201.3 min |
| Re-evaluation (150 simulations) | 23.1 min |
| Artefact build | < 1 min |
| **Total** | **≈ 3.7 h** |

### D. Known caveats

1. The 14-parameter LHS calibration is weakly identifying (cf. §6.2): differences in
   total train loss of 0.05–0.30 between top-5 candidates within a variant are common.
2. The `flatten_heterogeneity` operation preserves agent count, mechanism activation
   and parameter dimension; it removes only the dispersion of the targeted
   columns. It is therefore conservative — a more aggressive ablation that also
   disabled mechanism switches would likely show larger deltas, but at the cost of
   conflating dimension and mechanism.
3. The crisis-window numbers (Table 3) are dominated by the BLS 2020-04 spike, which
   no parameter configuration can match exactly given the 302-month monthly grid.
