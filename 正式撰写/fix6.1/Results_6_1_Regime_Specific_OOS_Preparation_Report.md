﻿# Results 6.1 (Revised) — Regime-Specific Out-of-Sample Performance

**Scope.** This revision replaces the single-window OOS framing of the original §6.1
with a regime-decomposed evaluation. No new simulations are run. The 5-seed
trajectories of the *baseline candidate of the heterogeneous ABM* (the same
parameter vector reported in the original §6.1 and reused throughout §6.2–§6.5) are
read from `正式撰写/6.2/derived_series.npz` (verified bit-identical to
`正式撰写/6.1/baseline_seed_trajectories.npz`). Eight named windows are scored,
including four regime windows and four legacy windows.

- Source script: `正式撰写/fix6.1/run_fix6_1_regime.py` (consolidation only; 0.01 s).
- Artefact builder: `正式撰写/fix6.1/build_fix6_1_artifacts.py`.
- Outputs: `regime_metrics.json`, `regime_series.npz`, `tables/table1..3.csv`,
  `figures/fig1..4.png`.
- All error metrics are reported in **percentage points (pp)** in the body
  (= decimal × 100); the JSON keeps decimal units for downstream re-use.

---

## 1. Executive Summary

1. **Post-COVID normalization (2022-01..2026-02, 49 valid months).** UR RMSE
   **0.221 ± 0.007 pp**, MAE 0.163 pp, corr 0.790, bias −0.043 pp, seed CV 3.08 %.
   This is the same headline number reported throughout §6.1–§6.5; the heterogeneous
   ABM tracks the post-COVID U-3 plateau (3.4 – 4.3 %) closely.
2. **COVID crisis (2020-03..2021-12, 22 months).** UR RMSE **2.820 ± 0.020 pp**,
   bias **−2.069 pp** (severe under-prediction), max abs error 6.069 pp, corr 0.755.
   The model captures the *direction* of the COVID shock — UR rises, then falls —
   but never approaches the 14.7 % observed peak. **The heterogeneous ABM cannot
   replicate extreme labor-market discontinuities of the COVID type.**
3. **Pre-COVID stable (2018-01..2019-12, 24 months).** UR RMSE 0.786 ± 0.050 pp,
   but this is **bias-dominated**: bias = +0.765 pp (model UR mean 4.55 % vs.
   observed 3.78 %). Correlation is low (0.21) because the observed series is
   essentially flat (range 3.5 – 4.1 %), so any month-to-month noise dilutes the
   correlation ratio. Importantly, **LFPR (0.54 pp) and EPOP (0.19 pp) are excellent
   here**.
4. **Full post-2018 (97 months).** UR RMSE 1.417 pp; ~85 % of the squared error is
   contributed by the 22 COVID-crisis months even though they are only 23 % of the
   sample. Headline RMSE on this composite window is the wrong summary statistic;
   the regime decomposition is the correct one.
5. **Legacy validation window (2018-01..2021-12) UR RMSE 2.00 pp is COVID-driven.**
   On the 24 non-COVID months of validation (the pre-COVID-stable subset), UR RMSE
   is 0.79 pp; on the 24 COVID-window months (Jan 2020 on), it is 2.72 pp. The
   2.00 pp aggregate is a weighted average of these two regimes — its size says
   nothing about model performance in normal conditions.
6. **LFPR / EPOP pattern is regime-structured, not uniformly weak.** RMSE values
   (pp): pre-COVID stable {LFPR 0.54, EPOP 0.19}; COVID crisis {2.23, 3.68};
   post-COVID norm {2.27, 2.21}. The labor-stock errors reported in the original
   §6.1 are a **post-COVID structural-break artefact** — the pre-COVID LFPR/EPOP
   are close to observed. The post-COVID divergence reflects a permanent
   compositional shift (older-cohort retirements, COVID NILF flows) that the
   Phase 6 baseline parameterization does not absorb.
7. **Seed stability is regime-dependent but always small.** Five-seed UR RMSE CV:
   pre-COVID 6.4 %, COVID crisis **0.70 %**, post-COVID norm 3.1 %, full post-2018
   0.51 %. The crisis CV is small because the under-prediction is *structural* —
   every seed produces nearly the same UR path; the dispersion at the bottom of
   the plateau is what dominates seed CV in the normal regime.
8. **Reframed paper claim.** The heterogeneous ABM is *not* a broad
   crisis-forecasting tool. It is a **normal-regime monthly unemployment tracker**:
   accurate on post-COVID U-3 (0.221 pp), directionally correct but
   level-incomplete during extreme discontinuities, and biased-but-stable in
   pre-COVID UR while excellent in pre-COVID LFPR/EPOP. The Section 6.1 wording
   in §10 below makes this scope explicit.

---

## 2. Experiment Setup

| item | value |
|---|---|
| Reported model | **the heterogeneous ABM**, Phase 6 baseline candidate (no recalibration) |
| Population | `Phase2_Output/population_v1.npz` (100,000 synthetic agents, NY-Fed-SCE-anchored moments) |
| Seeds | [42, 137, 2024, 888, 1234] |
| Simulation period | 2001-01..2026-02 (302 months) — the full simulation horizon, same for every regime |
| Macro inputs | FRED **JTSJOR, JTSLDR, CES0500000003, FEDFUNDS** via `Phase3_Code/environment_real.py` |
| Targets | BLS **UNRATE, CIVPART, EMRATIO** (observed UR / LFPR / EPOP), divided by 100 to decimal |
| NaN handling | UNRATE missing 2025-10 only; metric functions mask NaN (n_valid = 49 in the post-COVID norm window) |
| Trajectory source | `正式撰写/6.2/derived_series.npz` (M0_Full × 5 seeds × 302 months — verified identical to `正式撰写/6.1/baseline_seed_trajectories.npz`) |
| Re-evaluation script | `正式撰写/fix6.1/run_fix6_1_regime.py` (no simulation; metric recomputation only) |

The simulation does **not** use observed UR / LFPR / EPOP as transition inputs —
agents' E↔U↔N decisions are driven by macro inputs and individual state only;
the BLS series are read solely by metric code (`compute_window_metrics` in the
original `Phase3_Code/phase7_engine.py:68–119` and the regime variant here).

**OOS-window honesty.** The post-COVID normalization window (= original OOS
window) is held out from the calibration loss but was monitored during later
development and robustness analysis. Do not claim the OOS was completely
untouched.

---

## 3. Regime Definitions

Eight windows, half-open index intervals on the 302-month calendar
(2001-01 = index 0):

| key | label | calendar period | index range | months in range | n_valid (UR) | rationale |
|---|---|---|---|---:|---:|---|
| `pre_covid_stable`  | Pre-COVID stable           | 2018-01..2019-12 | [204, 228) | 24 | 24 | last two years of the late-2010s plateau |
| `covid_crisis_mar`  | COVID crisis (Mar 2020 on) | 2020-03..2021-12 | [230, 252) | 22 | 22 | shock + recovery, starting from the BLS UR pop |
| `covid_crisis_jan`  | COVID crisis (Jan 2020 on) | 2020-01..2021-12 | [228, 252) | 24 | 24 | optional alternative that includes the two pre-shock months |
| `post_covid_norm`   | Post-COVID normalization   | 2022-01..2026-02 | [252, 302) | 50 | 49 (Oct-25 NaN) | the original headline OOS window |
| `full_post_2018`    | Full post-2018             | 2018-01..2026-02 | [204, 302) | 98 | 97 | super-window covering all of validation + OOS |
| `train`             | Train                      | 2004-01..2017-12 | [36, 204)  | 168 | 168 | legacy Phase 7 training window (calibration weight 1.0) |
| `validation`        | Validation                 | 2018-01..2021-12 | [204, 252) | 48 | 48 | legacy Phase 7 validation window (candidate selection only) |
| `original_oos`      | Original OOS               | 2022-01..2026-02 | [252, 302) | 50 | 49 | legacy headline OOS — identical to post_covid_norm by construction |

Note that `post_covid_norm` and `original_oos` cover the same months; their
metrics are identical and reported in two rows of Table 3 so the reader can see
the equivalence. `validation` overlaps with `pre_covid_stable` and the COVID
windows; this is intentional — it lets us show what fraction of the legacy 2.00 pp
validation RMSE comes from each regime.

---

## 4. Main Regime-Specific Results (Table 1)

Reproduced from `tables/table1_regime_summary.csv` (mean across 5 seeds; pp units):

| window | period | n_valid | UR RMSE pp (mean ± sd) | UR MAE pp | UR corr | UR bias pp | UR max abs pp | sim mean pp | obs mean pp | LFPR RMSE pp | EPOP RMSE pp | seed CV % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pre-COVID stable           | 2018-01..2019-12 | 24 | 0.786 ± 0.050 | 0.765 | +0.211 | +0.765 | 1.14 | 4.55 | 3.78 | **0.54** | **0.19** | 6.40 |
| COVID crisis (Mar 2020 on) | 2020-03..2021-12 | 22 | **2.820 ± 0.020** | 2.426 | +0.755 | **−2.069** | 6.07 | 4.94 | 7.01 | 2.23 | 3.68 | 0.70 |
| COVID crisis (Jan 2020 on) | 2020-01..2021-12 | 24 | 2.719 ± 0.019 | 2.315 | +0.728 | −1.805 | 6.07 | 4.92 | 6.73 | 2.14 | 3.52 | 0.68 |
| **Post-COVID normalization** | **2022-01..2026-02** | **49** | **0.221 ± 0.007** | **0.163** | **+0.790** | **−0.043** | 0.66 | 3.86 | 3.90 | 2.27 | 2.21 | 3.08 |
| Full post-2018             | 2018-01..2026-02 | 97 | 1.417 ± 0.007 | 0.844 | +0.719 | −0.279 | 6.07 | 4.29 | 4.57 | 1.96 | 2.36 | 0.51 |

Reading.

- The four regime rows partition the 2018-01..2026-02 horizon: the model achieves
  **0.221 pp** in the regime that dominates 49/97 months (post-COVID norm), and
  **2.82 pp** in the regime that dominates 22/97 months (COVID crisis). The
  full-period 1.42 pp is therefore not a uniform error — it is a length-weighted
  mix of two very different regimes.
- Pre-COVID UR RMSE (0.79 pp) is unusually structured: bias accounts for
  **0.765 / 0.786 = 97 %** of the RMSE squared budget. The model's pre-COVID
  baseline simulates ~4.5 % UR while observed UR sits at ~3.8 %. This is a
  **level-offset issue, not a dynamics issue.**
- COVID-crisis correlation 0.755 means the simulation rises and falls when the
  data rise and fall, even though it under-predicts the level — a directionally
  useful but quantitatively incomplete tracker.

---

## 5. COVID Crisis Performance (Figures 1, 2, 3)

(Source: `regime_metrics.json -> windows.covid_crisis_mar`,
`figures/fig1_full_period_ur.png`, `figures/fig3_prediction_error_time.png`.)

### 5.1 Headline numbers (2020-03..2021-12, 22 months)

- **UR RMSE = 2.82 ± 0.02 pp** (mean of 5 seeds).
- **UR MAE = 2.43 pp**.
- **UR bias = −2.07 pp** (mean simulated 4.94 % vs. observed 7.01 %).
- **Max absolute monthly error = 6.07 pp** (April–May 2020 spike, when observed
  UR hit 14.7 % and the simulated path peaked near 5.7 %).
- **UR correlation = 0.755** — high enough to confirm the simulation does follow
  the shock-and-recovery arc, just with a much smaller amplitude.
- Seed CV is **0.70 %** — the under-prediction is structural; all five seeds
  produce nearly the same trajectory.

### 5.2 Why the model misses the COVID magnitude

The Phase 6 baseline parameter vector is calibrated against U-3 + LFPR + EPOP
moments over 2004-01..2017-12, a period in which the *maximum* observed UR is
the 10.0 % of October 2009. The agent-level separation hazards and search
intensities the calibration converges on are tuned to the macroeconomic regimes
visible in training; a 2020-style mass-layoff event with monthly separation
rates 4–5× any pre-existing observation is outside the calibration support set.
The macro inputs (JTSJOR, JTSLDR) *do* show the 2020 shock, but the agent-level
response surface that maps them into UR is bounded by training-window
experience, so the simulated UR rises only modestly.

### 5.3 What the model *does* get right during the COVID window

- **Direction.** Correlation 0.755 confirms the U-shape is reproduced.
- **Recovery slope.** From late-2020 onward the simulated and observed paths
  re-converge as macro inputs normalise (see Figure 1).
- **Seed-coherent behaviour.** Five seeds bracket the simulated path within
  ±0.02 pp RMSE — the under-prediction is *not* random; it is a property of the
  agent decision rules under shocked macro inputs.

---

## 6. Post-COVID Normalization Performance (Figures 1, 2)

(Source: `regime_metrics.json -> windows.post_covid_norm`,
`tables/table2_seed_level_regime.csv`, `figures/fig1_full_period_ur.png`.)

### 6.1 Headline numbers (2022-01..2026-02, 49 valid months)

| seed | UR RMSE pp | UR MAE pp | UR corr | UR bias pp | UR max abs pp |
|---:|---:|---:|---:|---:|---:|
| 42   | 0.2322 | 0.1661 | 0.7798 | −0.0429 | 0.76 |
| 137  | 0.2199 | 0.1639 | 0.7584 | −0.0604 | 0.66 |
| 2024 | 0.2109 | 0.1514 | 0.8245 | −0.0444 | 0.64 |
| 888  | 0.2223 | 0.1669 | 0.8004 | −0.0433 | 0.63 |
| 1234 | 0.2202 | 0.1663 | 0.7847 | −0.0213 | 0.63 |
| **mean** | **0.2211** | **0.1629** | **0.7896** | **−0.0425** | 0.66 |
| sd | 0.0068 | — | 0.022 | — | — |

### 6.2 Interpretation

- The post-COVID U-3 trajectory (3.4 – 4.3 % in BLS) is the regime the
  heterogeneous ABM is best at: the headline 0.221 pp = ~5.4 % of the observed
  mean (3.90 %). This is the result reproduced across §6.1–§6.5.
- The error is dominantly **monthly noise**: bias is only −0.04 pp, and the
  largest single-month miss is ~0.66 pp, concentrated in early 2022 immediately
  after the COVID recovery (visible in Figure 3).
- All five seeds remain in a 0.211 – 0.232 pp band — CV 3.08 %, dispersion small
  relative to the mean.

---

## 7. LFPR / EPOP Regime Results (Figure 4)

(Source: `tables/table1_regime_summary.csv`,
`figures/fig4_lfpr_epop_regime_bar.png`.)

| regime | LFPR RMSE pp | LFPR bias pp | EPOP RMSE pp | EPOP bias pp |
|---|---:|---:|---:|---:|
| Pre-COVID stable           | **0.54** | +0.53 | **0.19** | +0.02 |
| COVID crisis (Mar 2020 on) | 2.23     | +2.19 | 3.68     | +3.37 |
| Post-COVID normalization   | 2.27     | +2.25 | 2.21     | +2.19 |
| Full post-2018             | 1.96     | +1.78 | 2.36     | +1.87 |

Reading.

- **The LFPR/EPOP errors are not a uniform model weakness.** In the pre-COVID
  stable regime, LFPR RMSE 0.54 pp and EPOP RMSE 0.19 pp are *comparable to or
  better than* the UR RMSE in the same regime — the model's labor-stock predictions
  are excellent in 2018-19.
- **The post-COVID divergence is the source of the LFPR/EPOP gap.** After 2020,
  observed BLS LFPR drops permanently from ~63.3 % (2018-19) to ~62.5 %
  (2022-26) because of accelerated retirements and persistent COVID-induced NILF
  flows. The Phase 6 parameter vector, calibrated on 2004-2017, does not
  reproduce this permanent shift; the model retains a ~64.7 % LFPR in the
  normalization window.
- **EPOP bias during COVID (+3.37 pp)** is consistent with the same mechanism:
  agents stay attached to the labor force at pre-COVID rates while observed
  workers exit en masse.
- LFPR and EPOP remain *secondary and weaker outcomes* of the model, but only
  in the *post-COVID* regime — this is a more precise statement than the
  blanket "LFPR/EPOP are weak" reading of the original §6.1.

---

## 8. Seed Stability

(Source: `regime_metrics.json -> windows.*.aggregate.ur.rmse_cv`.)

| regime | mean UR RMSE pp | seed sd UR RMSE pp | seed CV % |
|---|---:|---:|---:|
| Pre-COVID stable           | 0.786 | 0.050 | **6.40** |
| COVID crisis (Mar 2020 on) | 2.820 | 0.020 | **0.70** |
| Post-COVID normalization   | 0.221 | 0.007 | **3.08** |
| Full post-2018             | 1.417 | 0.007 | **0.51** |

The pre-COVID seed CV (6.4 %) is the largest of the four regime windows in
relative terms, but in absolute pp it is the second-smallest (0.050 pp). The
elevated CV reflects the small denominator (mean RMSE 0.79 pp) rather than wide
absolute dispersion — five seeds span 0.71 – 0.86 pp. The COVID-crisis CV is
the smallest at 0.70 % because the under-prediction is structural across
seeds. **Seed stability holds in every regime in absolute pp terms** (sd ≤
0.05 pp); we lose no Section 6.1 stability claim by switching to the regime
framing.

---

## 9. Tables and Figures Generated

```
正式撰写/fix6.1/
  Results_6_1_Regime_Specific_OOS_Preparation_Report.md   ← this file
  run_fix6_1_regime.py                                     ← metric driver (uses 6.2 trajectories)
  build_fix6_1_artifacts.py                                ← tables + figures builder
  regime_metrics.json                                      ← all per-seed metrics (decimal units)
  regime_series.npz                                        ← 5-seed M0 trajectories + BLS targets
  rerun_log.txt / build_log.txt                            ← console logs
  tables/
    table1_regime_summary.csv                              ← 5 regime rows, all UR/LFPR/EPOP metrics
    table2_seed_level_regime.csv                           ← 25 rows (5 regimes × 5 seeds)
    table3_old_vs_regime_comparison.csv                    ← legacy windows vs regime windows
  figures/
    fig1_full_period_ur.png                                ← observed + simulated UR 2018-2026 w/ shaded regimes
    fig2_regime_ur_rmse_bar.png                            ← per-regime UR RMSE bars, ±seed sd
    fig3_prediction_error_time.png                         ← (sim − obs) over time, ±seed sd
    fig4_lfpr_epop_regime_bar.png                          ← LFPR + EPOP RMSE per regime
```

---

## 10. Recommended Wording for Revised Section 6.1

### 10.1 One-paragraph version (~130 words)

> *We evaluate the heterogeneous ABM out-of-sample across four labor-market
> regimes spanning 2018-01 to 2026-02. In the **post-COVID normalization
> regime** (2022-01..2026-02, 49 months) the model achieves a five-seed mean
> unemployment-rate RMSE of **0.22 ± 0.01 percentage points** (correlation 0.79,
> bias −0.04 pp). In the **2020 COVID crisis regime** (22 months) the model
> tracks the direction of the shock (correlation 0.76) but under-predicts its
> magnitude by 2.07 pp on average and 6.07 pp at peak — the heterogeneous ABM
> does not reproduce extreme discontinuities of the COVID type. In the
> **pre-COVID stable regime** (24 months), UR error is 0.79 pp and dominantly a
> +0.77 pp level offset, while LFPR and EPOP RMSE are 0.54 and 0.19 pp
> respectively. We therefore frame the model as a normal-regime monthly
> unemployment tracker, not a broad crisis-forecasting tool.*

### 10.2 Three-paragraph version (~340 words)

> *Section 6.1 reports out-of-sample performance of the heterogeneous ABM under
> the Phase 6 baseline parameter vector across four labor-market regimes
> spanning 2018-01 to 2026-02. Predictions are produced by simulating the
> 100,000-agent population over 2001-01..2026-02 with five seeds {42, 137,
> 2024, 888, 1234}, using FRED macro inputs (JTSJOR, JTSLDR, CES0500000003,
> FEDFUNDS) as the only exogenous drivers; observed BLS UR, LFPR, and EPOP are
> read only by metric code. The original calibration loss is computed on
> 2004-01..2017-12; the 2018-01..2026-02 horizon is held out from the
> calibration loss but was monitored during model development and robustness
> analysis.*
>
> *In the **post-COVID normalization regime** (2022-01..2026-02, 49 valid
> months), five-seed mean unemployment-rate RMSE is **0.221 ± 0.007 pp**,
> correlation 0.790, bias −0.043 pp, maximum absolute monthly error
> ≤ 0.77 pp; the heterogeneous ABM tracks the U-3 plateau (3.4 – 4.3 %)
> closely. In the **2020 COVID crisis regime** (2020-03..2021-12, 22 months),
> the same model achieves UR RMSE 2.82 ± 0.02 pp and a bias of −2.07 pp:
> the simulation captures the rise-then-fall arc of the shock (correlation
> 0.755) but under-predicts the 14.7 % April-2020 peak by ~6 pp. In the
> **pre-COVID stable regime** (2018-01..2019-12, 24 months), UR RMSE is
> 0.79 pp but is dominated by a +0.77 pp level offset; LFPR and EPOP RMSE,
> however, are 0.54 and 0.19 pp — the model's labor-stock predictions are
> in fact better in this regime than in either of the two more recent ones.*
>
> *Aggregating these regimes over 2018-01..2026-02 yields a composite UR RMSE
> of 1.42 pp, with the 22 COVID-crisis months contributing roughly 85 % of
> the squared-error budget despite being 23 % of the sample. We therefore
> position the heterogeneous ABM as a **normal-regime monthly unemployment
> tracker** rather than a broad crisis-forecasting model: it is accurate in
> post-COVID stability, directionally correct but level-incomplete during
> extreme discontinuities, and biased-but-stable in pre-COVID U-3 with
> excellent pre-COVID LFPR and EPOP. Sections 6.2 – 6.5 build on the
> post-COVID normalization RMSE as the headline number against which
> heterogeneity contributions, mechanism ablations, external benchmarks, and
> robustness perturbations are measured.*

### 10.3 Headline numbers checklist

(Every entry verifiable in `tables/table1_regime_summary.csv`.)

- *"Post-COVID normalization UR RMSE 0.221 ± 0.007 pp, corr 0.790, bias −0.043 pp."* ✅
- *"COVID-crisis UR RMSE 2.82 pp, bias −2.07 pp, max abs error 6.07 pp."* ✅
- *"COVID-crisis correlation 0.755 — direction is captured, magnitude is not."* ✅
- *"Pre-COVID UR RMSE 0.79 pp = +0.77 pp bias + 0.18 pp variance term."* ✅
- *"Pre-COVID LFPR RMSE 0.54 pp; EPOP RMSE 0.19 pp."* ✅
- *"Full 2018-2026 UR RMSE 1.42 pp = length-weighted mix; ~85 % of squared error from COVID months."* ✅
- *"Five-seed dispersion ≤ 0.05 pp in every regime; seed CV 0.7 % to 6.4 % across regimes."* ✅

---

## 11. Wording to Avoid

These claims are *not* supported by the regime-decomposed numbers and should
not appear in the revised §6.1:

1. ❌ *"The heterogeneous ABM predicts unemployment dynamics out-of-sample."*
   Too broad. State the regime: "post-COVID normalization unemployment dynamics"
   or "monthly U-3 tracking in normal regimes."
2. ❌ *"The model is accurate across 2018-2026."*
   It is accurate on the 49-month post-COVID-norm subwindow only. On the
   full 97-month horizon, RMSE is 1.42 pp; on the COVID-crisis subwindow alone,
   2.82 pp.
3. ❌ *"The model predicts the 2020 COVID shock."*
   It captures the *direction* (correlation 0.755), not the magnitude. State
   both numbers and call this a "directionally correct, level-incomplete"
   response.
4. ❌ *"The OOS window was completely held out."*
   Held out from the calibration loss; monitored during later development and
   robustness analysis. Wording in §10.2 reflects this.
5. ❌ *"LFPR and EPOP are weak across the board."*
   They are weak in the post-COVID regime only. Pre-COVID LFPR/EPOP RMSE
   (0.54 / 0.19 pp) are excellent. The honest framing is a regime-specific
   labor-stock divergence after 2020.
6. ❌ *"The validation window high RMSE shows the model fails on 2018-2021."*
   The 2.00 pp validation RMSE is regime-mixed: on the 24 non-COVID validation
   months it is 0.79 pp; on the 24 COVID months it is 2.72 pp. Decompose before
   interpreting.
7. ❌ *"All five seeds agree, so the model is robust."*
   Seed agreement is high in every regime. But seed agreement in the COVID
   window (CV 0.70 %) reflects *structural* under-prediction; it is not a
   robustness virtue, it is the same wrong answer five times.
8. ❌ *"The model can be used for unemployment forecasting in any regime."*
   It is a normal-regime tracker. Extreme-shock forecasting is out of scope.
9. ❌ Confusing decimal and pp. The JSON stores decimal units (0.00221), the
   tables store pp (0.221). Always write "pp" or "%" in the paper body.
10. ❌ Using internal engineering names ("M0", "M0_Main", "M0_Full") in paper
    body. Use **"the heterogeneous ABM"** or **"the baseline heterogeneous ABM"**.

---

## 12. Evidence Appendix

| claim | source file | row / key |
|---|---|---|
| Post-COVID norm UR RMSE 0.221 ± 0.007 pp     | `regime_metrics.json` | `windows.post_covid_norm.aggregate.ur.rmse_mean/sd` × 100 |
| Post-COVID norm corr 0.790, bias −0.043 pp   | same                  | `windows.post_covid_norm.aggregate.ur.{corr_mean,bias_mean}` |
| COVID crisis UR RMSE 2.82 pp, bias −2.07 pp  | same                  | `windows.covid_crisis_mar.aggregate.ur.{rmse_mean,bias_mean}` × 100 |
| COVID crisis corr 0.755                      | same                  | `windows.covid_crisis_mar.aggregate.ur.corr_mean` |
| Pre-COVID UR RMSE 0.79 pp, bias +0.77 pp     | same                  | `windows.pre_covid_stable.aggregate.ur.{rmse_mean,bias_mean}` × 100 |
| Pre-COVID LFPR 0.54 pp, EPOP 0.19 pp         | same                  | `windows.pre_covid_stable.aggregate.{lfpr,epop}.rmse_mean` × 100 |
| Full 2018-2026 UR RMSE 1.42 pp               | same                  | `windows.full_post_2018.aggregate.ur.rmse_mean` × 100 |
| Per-seed UR RMSE in post-COVID norm          | same                  | `windows.post_covid_norm.seeds.{42,137,2024,888,1234}.ur.rmse` × 100 |
| Original §6.1 train/val/oos numbers          | `tables/table3_old_vs_regime_comparison.csv` | rows `train`, `validation`, `original_oos` |
| Baseline trajectories used                   | `正式撰写/6.2/derived_series.npz` | `M0_Full_ur`, `M0_Full_lfpr`, `M0_Full_epop` (5 × 302) |
| BLS targets used                             | same                  | `target_ur`, `target_lfpr`, `target_epop` (302) |
| Identity check (6.1 vs 6.2 trajectories)     | `rerun_log.txt`        | `Max diff seed42: 0.0` (in setup section of this report) |
| Re-evaluation driver                         | `正式撰写/fix6.1/run_fix6_1_regime.py` | `main()` |
| All paper-ready summary numbers              | `正式撰写/fix6.1/tables/table1_regime_summary.csv` | per-row |

End of revised Section 6.1 preparation report.
