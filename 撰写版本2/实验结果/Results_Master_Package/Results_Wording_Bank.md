# Results Wording Bank

Centralised paper-ready wording for Section 6. Use these phrasings; do not paraphrase casually.

---

## 1. Headline tracking (S06_01)

**Standard form:**

> The recalibrated heterogeneous ABM tracks observed U.S. unemployment over the post-COVID normalisation window 2022-01 to 2026-02 with a five-seed mean RMSE of 0.27 percentage points (cross-seed SD 0.02 pp), bias −0.04 pp, and correlation 0.79 with the BLS series.

**Crisis-window companion (always co-reported):**

> Simulated forward from a fixed 2018-01 initialisation without re-fitting, the model captures the direction of the 2020 COVID unemployment spike (UR correlation 0.75) but under-predicts its magnitude by approximately two percentage points on average over March 2020 through December 2021.

---

## 2. Internal controls (S06_02)

> Three internal controls, each separately calibrated under the same LHS budget and loss function, identify where the V_Full advantage on the post-COVID window comes from.

> A homogeneous-population variant with all fourteen mechanisms active attains UR RMSE 0.55 pp; a labour-side-only heterogeneous variant attains 0.36 pp; a fully flattened variant with a single mechanism attains 0.56 pp.

> Within this within-experiment accounting decomposition, 94 percent of the 0.29 pp total gain is associated with restoring worker-side heterogeneity and 6 percent with restoring the additional mechanisms.

**Mandatory qualifier on the decomposition:**

> We refer to this throughout as a within-experiment accounting decomposition rather than a causal partition: each variant is recalibrated, so part of the difference is absorbed by parameter substitution and the shares are not identified separately from the calibration protocol.

---

## 3. Heterogeneity ablations and ladder (S06_03)

> Removing search-friction heterogeneity is the most expensive single ablation: the recalibrated variant attains UR RMSE 1.09 pp, a 0.81 pp loss relative to V_Full.

> Removing liquidity-fragility heterogeneity costs 0.11 pp; removing housing-mobility heterogeneity does not cost anything in UR RMSE terms — the recalibrated variant comes in 0.04 pp below V_Full, an accounting consequence of parameter reassignment under recalibration.

> We interpret these numbers as within-experiment accounting deltas, not as causal contributions of each dimension.

**On non-additivity:**

> The joint flatten of Search, Liquidity and Housing costs 0.43 pp — substantially less than the sum of single-dimension deltas — indicating that recalibration partially substitutes between dimensions.

---

## 4. Benchmark comparison (S06_04)

> Under a common dynamic multi-step protocol on the post-COVID window 2022-01 to 2026-02, the ABM attains UR RMSE 0.273 pp, ranking first across twelve models.

> The two closest benchmarks — the No-change naive and an exponential-smoothing model with damped trend — both attain 0.309 pp, a margin of 0.036 pp over the ABM. This margin is the same order of magnitude as the ABM's own cross-seed standard deviation of 0.023 pp.

> We therefore describe the ABM as competitive at the top of the comparison set on this window, rather than as dominating it.

---

## 5. Robustness (S06_05)

> Ten alternative train/test splits produce a mean post-COVID UR RMSE of 0.245 ± 0.011 pp on the seven splits whose test window includes the post-COVID period; the ABM wins against all four legacy benchmarks on six of those seven splits.

> The ABM's log-log RMSE slope against forecast horizon h = 1..36 months is −0.09, the shallowest among the eight models compared.

> A population-size sweep over N from 5,000 to 300,000 agents identifies a plateau in mean UR RMSE at N ≥ 50,000; the default N = 100,000 is past this threshold.

> Varying the calibration method across Random Search, Latin Hypercube Sampling, Sobol, Coarse-to-Fine, and Differential Evolution under a matched budget of 200 evaluations × 3 seeds produces best-test UR RMSE in the band 0.21–0.24 pp, with a coefficient of variation of 5.55 percent across methods.

**Mandatory parameter-identification caveat:**

> Ten of the fourteen free parameters exhibit a coefficient of variation greater than 0.40 across the top-five candidates within a single calibration method. We accordingly report parameter values as bands rather than point estimates and refrain from describing the parameters as structurally identified.

---

## 6. Approved phrasings

- "Tracks observed U.S. unemployment"
- "Survey-moment-anchored"
- "Competitive at the top of the comparison set"
- "Modestly better than" / "narrow margin over"
- "Within-experiment accounting decomposition"
- "Accounting delta", "accounting share"
- "Diagnostic"
- "Predictive and diagnostic, not structural"
- "Robust prediction with non-unique parameterisation"
- "Weakly identified"
- "Reported as bands"
- "Captures the direction of the spike but under-predicts the magnitude"

## 7. Banned phrasings

- "Dominates" / "outperforms decisively" / "substantially better"
- "Causal" / "causal decomposition" / "causes"
- "Structurally identifies" / "structurally estimated" / "structural parameter values"
- "Completely untouched" / "completely tracks"
- "Survey-sampled" (use "survey-moment-anchored" instead)
- "ABM solves" / "ABM resolves"
- Over-emphasising COVID (treat as one regime among several, not as the central narrative)
- "Revised" / "audit" / "P1 report" / "rerun because old version had problems" (internal workflow language)
- "R / revised" suffixes
- Citing "0.221 pp" as the headline (use **0.273 pp** as the manuscript headline)

## 8. Numeric conventions

- UR / LFPR / EPOP errors: **percentage points (pp)**.
- Correlations: **decimal** (0.79, not 79%).
- Shares: **decimal or percent**, with explicit unit label.
- Cross-seed dispersion: **standard deviation (SD)**, not standard error.
- Sample sizes (N) and budgets: integers with thousands separator (e.g. 100,000).
- Confidence/prediction bands: reported as ranges (0.21–0.24 pp), not as ± half-widths unless the band is symmetric around the mean.

## 9. Cross-references

- Section 6.1 must reference E4 and E5; numbers come from `S06_01_T01`.
- Section 6.2 must reference E6 (controls) and E7 (decomposition); numbers come from `S06_02_T01` and `S06_02_T02`.
- Section 6.3 must reference E8 (ablation) and E9 (ladder).
- Section 6.4 must reference E10 only.
- Section 6.5 must reference E11, E12, and E13.
- E1–E3 are appendix-only and must not appear in §6 prose; they may appear in a methods cross-reference.
