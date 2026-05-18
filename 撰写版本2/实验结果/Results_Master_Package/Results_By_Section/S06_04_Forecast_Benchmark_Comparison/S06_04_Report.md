# S06_04 — Forecast Benchmark Comparison

**Manuscript section:** §6.4
**Supporting experiments:** E10 (Dynamic Benchmark Comparison)
**Source-of-evidence path:** `Results_By_Experiment/E10_Forecast_Benchmark_Comparison/`

## Headline result

Under a common dynamic multi-step protocol on the post-COVID window 2022-01..2026-02, the recalibrated V_Full ABM attains UR RMSE **0.273 pp** and ranks **first of twelve** models. The two strongest external benchmarks are essentially tied at second place:

| Rank | Model | UR RMSE (pp) | Ratio vs ABM |
|---:|---|---:|---:|
| 1 | **ABM V_Full (recalibrated)** | **0.273** | 1.00 |
| 2 | B0a No-change | 0.309 | 1.13× |
| 2 | B3 ETS (damped) | 0.309 | 1.13× |
| 4 | B6 Beveridge OLS | 0.34 | 1.25× |
| 5 | B1 AR(p) | 0.39 | 1.43× |
| 6 | B2 ARIMA | 0.42 | 1.54× |
| 7 | B4 VAR / B5 RidgeVAR | 0.45–0.55 | 1.6–2.0× |
| 8 | B7 DMP, B8 Flow | 0.7–1.1 | 2.5–4.0× |
| 12 | B0c Drift | 6.92 | 25× |

The ABM advantage over B0a No-change is **+0.036 pp** — the same order of magnitude as the V_Full cross-seed SD (0.023 pp). The advantage is reproducible across all four regime windows (V_Full ranks 1 in three of four, joint-1 in the fourth) but is **not large** in any single window. The honest manuscript-facing description is "competitive at the top of the comparison set", not "dominant".

## Paper-ready figures

- **`paper_ready_figures/S06_04_F01_Benchmark_RMSE_Bar__E10_v01.png`** — Horizontal bar chart of UR RMSE for ABM + 11 benchmarks on the post-COVID window. Bars sorted by RMSE; ABM bar highlighted; reference line at ABM RMSE shown.
- **`paper_ready_figures/S06_04_F02_Paths_Dynamic__E10_v01.png`** — Forecast path overlay on the post-COVID window (2022-01..2026-02) under the dynamic multi-step protocol: observed BLS UNRATE, ABM V_Full (5-seed mean), and the four benchmarks with the lowest UR RMSE on this window. Used to visualise how tracking quality differs across the top of the comparison set.

## Paper-ready table

- **`paper_ready_tables/S06_04_T01_Dynamic_Benchmark_Comparison__E10_v01.csv`** — Twelve-row comparison: model ID, family (naive / univariate / multivariate / structural / ABM), training window, UR RMSE, MAE, bias, correlation, ratio vs ABM, post-COVID rank, full-window rank, notes.

## Manuscript-facing wording (drop-in)

> We compare the recalibrated V_Full ABM against eleven external forecasting benchmarks spanning four families: naive (No-change, Historical Mean, Drift), univariate time-series (AR, ARIMA, ETS), multivariate time-series (VAR, Ridge-VAR), and structural labour-market models (Beveridge OLS, search-and-matching DMP, flow-rate). All twelve models are evaluated under the same dynamic multi-step protocol on the post-COVID window 2022-01..2026-02, with each benchmark fitted on 2001-01..2022-01 and forecast forward without re-fitting. The ABM attains UR RMSE 0.273 pp, ranking first across the twelve models. The two closest benchmarks — the No-change naive and an exponential-smoothing model with damped trend — both attain 0.309 pp, a margin of 0.036 pp over the ABM. This margin is the same order of magnitude as the ABM's own cross-seed standard deviation of 0.023 pp. We therefore describe the ABM as competitive at the top of the comparison set on this window, rather than as dominating it, and we report the rankings on the three earlier regime windows as a robustness check rather than as additional headline results.

## Caveats and wording rules

- **Window asymmetry is documented but not equalised**: ABM trains on 2004-01..2017-12 (168 months); benchmarks train on 2001-01..2022-01 (~252 months). Both forecast the same 2022-01..2026-02 window without refit. The asymmetry is in the *training* horizon, not in the *test* horizon.
- ABM advantage of 0.036 pp is comparable to the seed SD (0.023 pp). Manuscript must say "competitive", "modestly better", "narrow margin"; never "dominates", "substantially better".
- Structural benchmarks (B6 Beveridge, B7 DMP, B8 Flow) use **observed** JTSJOR and JTSLDR over the test window — the ABM uses the same exogenous drivers, so the comparison is fair on OOS exogenous information.
- Rolling-origin protocol comparison is reported in E10's T02, not in the headline table.
- Twelve-model count includes both ABM and the eleven benchmarks; "rank 1 of 12" is the canonical phrasing.

## Status

READY — paper-ready table and two figures (F01 RMSE bar, F02 dynamic-protocol forecast paths) are produced; numbers are traceable to `fix6.4/benchmark_metrics.json`, `fix6.4/benchmark_series.npz`, and `fix6.4/tables/table1_main_postcovid_benchmark.csv`.

## Audit mirror (full evidence for the appendix)

This section folder additionally contains an `audit_mirror/` subfolder with verbatim copies of every figure and table from the source experiment **E10 (Forecast Benchmark Comparison)**: 4 figures + 4 tables. See `audit_mirror/_INDEX.md` for per-file provenance. The paper-ready files are the manuscript-facing condensed versions; the audit-mirror files are for appendix assembly and reviewer-side traceability.
