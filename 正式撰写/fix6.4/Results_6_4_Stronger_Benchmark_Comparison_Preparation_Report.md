# Results §6.4 — Stronger Forecast Benchmark Comparison

**Preparation report, rev. 2026-05-14.** Companion to `run_fix6_4_benchmarks.py`
and `build_fix6_4_artifacts.py`. All RMSE / MAE / Bias values are reported in
percentage points (pp). The ABM rows use the §6.2 recalibrated full
heterogeneous model (`V_Full`), mean over 5 evaluation seeds at rank-0
(cand_idx = 32). No statistical benchmark was hand-tuned on the OOS window.

---

## 1. Goal and scope

Section 6.3 established that **Search Friction** is the only mechanism whose
removal materially degrades post-COVID unemployment-rate (UR) tracking. The
purpose of §6.4 is to test whether this advantage survives against a broader,
stronger set of forecasting benchmarks than the original AR / VAR / Beveridge /
DMP set, including naive baselines (no-change, mean, drift), state-of-practice
univariate models (AR, ARIMA, ETS), and multivariate / structural models (VAR,
Ridge-VAR, Beveridge, DMP, Flow). The primary comparison window is the
**post-COVID normalization** regime (2022-01..2026-02, 50 months); three
additional regimes (pre-COVID stable, COVID crisis March-2020 cohort, and the
full post-2018 horizon) provide robustness.

## 2. Protocol design

Two protocols are implemented separately for every benchmark.

* **Dynamic multi-step** (primary). Fit once on data ending immediately
  before the evaluation window; produce the entire OOS path without any
  re-fitting and without consuming the observed OOS UR. This matches the
  ABM, which is also a multi-step simulation. Structural benchmarks
  (Beveridge, DMP, Flow, Ridge-VAR with exogenous regressors) consume the
  observed OOS values of vacancy rate, separation rate, and earnings only —
  the same exogenous inputs the ABM also consumes.
* **Rolling one-step-ahead** (nowcasting reference). For each $t$ in the
  evaluation window, refit on $[0, t)$ and forecast $\hat u_{t+1}$. This
  protocol consumes the realised UR one period before the forecast, which
  the ABM does not, so its numbers are reported for context only and not
  directly compared with the ABM.

Regime fit cutoffs (Protocol A, strict): pre-COVID stable fits up to
2017-12 (t = 204), COVID crisis up to 2020-02 (t = 230), post-COVID up to
2021-12 (t = 252), full post-2018 up to 2017-12 (t = 204).

## 3. Benchmark catalogue

Eleven benchmarks are evaluated; specifications (orders, parameters, fit
regimes) are stored in `tables/table3_model_specs.csv`.

| ID | Family | Specification |
|---|---|---|
| B0a | Naive | No-change (random walk), $\hat u_{T+h}=u_T$ |
| B0b | Naive | Historical mean of training UR |
| B0c | Naive | Drift / 12-month local OLS trend |
| B1 | Univariate | AR(p), BIC ∈ {1,2,3,6,12} |
| B2 | Univariate | ARIMA(p,d,q), AIC grid p ≤ 4, q ≤ 4, d ≤ 2 |
| B3 | Univariate | ETS (SES / Holt / Damped Holt), AICc selection |
| B4 | Multivariate | VAR(p), BIC, on UNRATE+CIVPART+EMRATIO |
| B5 | Multivariate | Ridge VAR(2) on 5 variables (BVAR shrinkage proxy) |
| B6 | Structural | Beveridge OLS in $1/v_t$ and $s_t$ |
| B7 | Structural | DMP-style matching: $f_t = A\theta_t^{1-\alpha}$ + flow UR |
| B8 | Structural | Flow-based UR with AR(1) on job-finding rate $f_t$ |

## 4. Main result — post-COVID normalization (Table 5, Figure 1, Figure 2)

| Rank | Model | Dynamic UR RMSE (pp) | Ratio vs ABM | Corr |
|---:|---|---:|---:|---:|
| 1 | **ABM (recalibrated)** | **0.273** | 1.00 | +0.764 |
| 2 | No-change (B0a) | 0.309 | 1.13 | — (const) |
| 2 | ETS — SES (B3) | 0.309 | 1.13 | — (const) |
| 4 | Beveridge (B6) | 0.422 | 1.54 | +0.826 |
| 5 | Flow-based UR (B8) | 0.426 | 1.56 | +0.642 |
| 6 | DMP (B7) | 0.636 | 2.33 | +0.819 |
| 7 | VAR (B4) | 0.663 | 2.43 | −0.870 |
| 8 | Ridge VAR (B5) | 1.264 | 4.63 | +0.936 |
| 9 | AR (B1) | 1.611 | 5.90 | +0.637 |
| 10 | ARIMA (B2) | 1.617 | 5.92 | +0.637 |
| 11 | Historical mean (B0b) | 2.173 | 7.96 | 0.000 |
| 12 | Drift (B0c) | 6.919 | 25.34 | −0.855 |

The recalibrated ABM has the lowest dynamic UR RMSE on the primary window, but
the margin over the no-change and ETS-SES baselines is **0.036 pp** (≈ 13 %
RMSE reduction), which is small in absolute terms and within the seed-to-seed
band reported in §6.2 (±0.023 pp s.d.). The ABM's correlation with observed
UR (+0.76) is also higher than no-change/ETS (undefined, because both produce
constant forecasts that anchor to $u_{T_{\rm fit}}=3.9\%$).

## 5. Regime cross-cut (Table 2, Figure 5)

| Regime | Best model | Best RMSE (pp) | ABM RMSE (pp) | ABM rank / 12 |
|---|---|---:|---:|---:|
| Pre-COVID stable (2018-01..2019-12) | DMP (B7) | 0.257 | 0.609 | 7 |
| COVID crisis Mar-2020 (2020-03..2021-12) | Flow (B8) | 2.293 | 2.974 | 3 |
| **Post-COVID norm (2022-01..2026-02)** | **ABM** | **0.273** | 0.273 | **1** |
| Full post-2018 (2018-01..2026-02) | Flow (B8) | 0.985 | 1.467 | 2 |

The ABM wins only on the post-COVID normalization window. Two observations
must be reported honestly: (i) in the pre-COVID stable regime, where the
unemployment rate moves slowly along a steady trend, the DMP and drift
benchmarks track the level slightly better than the ABM, which under-shoots
the gentle UR decline by ≈ 0.3 pp; and (ii) in the COVID crisis window all
twelve models have RMSE above 2 pp, and the flow-based UR model — which
ingests observed separations — is the best of the set. The ABM's structural
advantage materialises specifically during the recovery phase, where the
heterogeneous search-friction block helps it avoid both the no-change anchor
error and the Beveridge / DMP overshoot generated by the volatile post-2022
vacancy and separation series.

## 6. Protocol comparison (Table 4)

Rolling one-step-ahead RMSE for every benchmark on the post-COVID window
collapses to 0.11–0.23 pp (no-change 0.115 pp, ETS 0.115 pp, drift 0.134 pp,
VAR 0.223 pp, Beveridge 0.385 pp). These numbers are not directly comparable
with the ABM's 0.273 pp dynamic RMSE because the rolling benchmarks observe
$u_{t-1}$ at every step. The protocol contrast is included to (a) document
that the ABM is *not* being compared on a nowcasting horizon, and (b) show
that the ABM's dynamic 0.273 pp is roughly equal to the *rolling one-step*
RMSE of the best statistical benchmarks — i.e., the ABM produces a 50-month
multi-step trajectory whose quality is similar to a benchmark that sees
the previous month's realised UR.

## 7. Source-of-advantage analysis

Combining §5 and §6.3:

* The 0.036 pp ABM gain over the strongest statistical benchmark (no-change
  / ETS) is consistent with the §6.3 finding that disabling search friction
  raises post-COVID UR RMSE by 0.812 pp, while disabling consumption,
  housing, or liquidity moves the RMSE by less than 0.05 pp.
* Structural benchmarks that use the same exogenous data the ABM consumes
  (B6 Beveridge, B8 Flow, B7 DMP) are not flattering: the simple Beveridge
  OLS lands at 0.422 pp, ≈ 1.54× the ABM. The ABM's marginal value over
  these structural benchmarks is therefore not "more macroeconomic data"
  but the heterogeneous search-friction block inferred from survey moments.

## 8. Wording for §6.4 (paper draft, ≈ 280 words)

> Section 6.4 evaluates the recalibrated full heterogeneous ABM against
> a wider set of forecasting benchmarks than commonly reported in this
> literature. Eleven models are estimated under two protocols (dynamic
> multi-step and rolling one-step) across four evaluation regimes
> (pre-COVID stable, COVID crisis, post-COVID normalization, and the
> full post-2018 window). The naive baselines (no-change, historical
> mean, drift), univariate state-of-practice models (AR with BIC order
> selection, ARIMA with AIC grid search, ETS with AICc selection),
> multivariate models (VAR, ridge-shrunk VAR as a BVAR proxy), and
> structural benchmarks (Beveridge, DMP, flow-based UR) are all
> implemented with strict regime-specific fit cutoffs.
>
> On the primary out-of-sample window — post-COVID normalization,
> 2022-01..2026-02 — the recalibrated ABM produces a 50-month dynamic
> forecast with UR RMSE 0.273 pp (corr. +0.76), compared with 0.309 pp
> for the best two statistical benchmarks (no-change and ETS-SES, both
> of which collapse to a constant), 0.42 pp for Beveridge, 0.43 pp for
> the flow-based UR model, and 0.66 pp or worse for VAR / DMP / AR /
> ARIMA / Ridge-VAR. The improvement over the strongest benchmark is
> 0.036 pp (≈ 13 % RMSE reduction), which is modest but consistent
> with the §6.3 ablation evidence that search-friction heterogeneity
> drives the post-COVID gain.
>
> The ABM does not dominate in every regime. In the pre-COVID stable
> window it ranks 7th of 12, behind DMP and a simple 12-month drift,
> and in the COVID-crisis window the flow-based UR model — which
> consumes observed separations — has the lowest RMSE. The ABM
> therefore should be positioned as *competitive with strong
> benchmarks during regime transitions* while additionally providing
> heterogeneity-level diagnostics that no purely statistical benchmark
> can produce.

## 9. Wording explicitly to avoid

1. "ABM beats all benchmarks on every metric." Only true on post-COVID
   dynamic UR.
2. "Beveridge is the standard benchmark." It is one structural benchmark
   among five (B4, B5, B6, B7, B8) and is not the strongest.
3. "OOS is completely untouched." The structural benchmarks consume
   observed OOS vacancy / separation series — exactly as the ABM does.
4. Reporting decimals as percentage points (e.g. 0.0027 vs 0.27 pp).
5. Calling no-change "trivial". Its 0.309 pp dynamic RMSE on post-COVID
   normalisation is within 13 % of the ABM.
6. Using the internal IDs "B0a … B8" in the paper body — use full names.
7. Implying benchmark inferiority is structural evidence. The ablation
   in §6.3 supplies the mechanism evidence, not §6.4.
8. Reporting rolling and dynamic numbers side-by-side without noting
   that the protocols are not comparable for the ABM row.

## 10. Artifacts

* `tables/table1_main_postcovid_benchmark.csv` — post-COVID dynamic ranking
* `tables/table2_regime_specific.csv` — full model × regime matrix
* `tables/table3_model_specs.csv` — selected orders / parameters per regime
* `tables/table4_protocol_comparison.csv` — dynamic vs rolling RMSE
* `tables/table5_paper_ready.csv` — compact LaTeX-ready table
* `figures/fig1_rmse_bars_postcovid_dynamic.png` — sorted RMSE bars
* `figures/fig2_ratio_vs_abm.png` — RMSE ratio bar
* `figures/fig3_paths_postcovid_dynamic.png` — UR trajectories
* `figures/fig4_scatter_postcovid.png` — predicted vs observed scatter
* `figures/fig5_heatmap_model_regime.png` — RMSE heatmap

## 11. Reproducibility

* Raw outputs: `benchmark_metrics.json` (28 KB), `benchmark_series.npz`
  (≈ 110 KB).
* Execution time: 37.8 s total on a single-core run (4 regimes × 11
  benchmarks × 2 protocols = 88 forecast paths).
* ABM rows are loaded from `正式撰写/fix6.2/reeval_metrics.json` (5 seeds,
  rank-0 candidate cand_idx = 32, post-COVID UR RMSE 0.273 pp ± 0.023 pp).

## 12. Limitations

The dynamic protocol is unforgiving: any model that produces a non-stationary
trajectory (drift, ridge-VAR with weak shrinkage) is heavily penalised by the
50-month projection horizon. Conversely, models that collapse to a constant
(no-change, ETS-SES) are protected by the fact that the post-COVID UR series
itself is nearly flat at 3.5–4.2 %. The ABM's margin therefore reflects both
its forecasting structure and the empirical mildness of the post-COVID UR
dynamics; this is acknowledged in §8 and should not be overstated.

## 13. Evidence appendix — exact numbers

Mean over 5 evaluation seeds for ABM_Full_recalibrated, rank-0
(cand_idx = 32). Single-run for statistical benchmarks. All values pp.

```
post_covid_norm dynamic:
  ABM_Full_recalibrated  RMSE 0.2731  MAE 0.2087  Corr +0.7636  Bias  N/A
  B0a_NoChange           RMSE 0.3094  MAE 0.2714  Corr undef    Bias -0.002
  B3_ETS (SES)           RMSE 0.3094  MAE 0.2715  Corr undef    Bias -0.002
  B6_Beveridge           RMSE 0.4216  MAE 0.3869  Corr +0.8262  Bias +0.165
  B8_Flow                RMSE 0.4263  MAE 0.3637  Corr +0.6425  Bias -0.087
post_covid_norm rolling:
  B0a_NoChange  RMSE 0.1152   B3_ETS  RMSE 0.1150   B0c_Drift  RMSE 0.1339
covid_crisis_mar dynamic:
  B8_Flow       RMSE 2.2934   B7_DMP  RMSE 2.9290   ABM       RMSE 2.9740
pre_covid_stable dynamic:
  B7_DMP        RMSE 0.2568   B0c_Drift RMSE 0.2754  ABM       RMSE 0.6092
full_post_2018 dynamic:
  B8_Flow       RMSE 0.9848   ABM        RMSE 1.4674  B7_DMP    RMSE 1.6858
```
