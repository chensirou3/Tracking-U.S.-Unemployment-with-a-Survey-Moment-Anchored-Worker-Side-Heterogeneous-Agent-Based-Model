# E10 — Forecast Benchmark Comparison

## Purpose

Place the recalibrated V_Full against eleven external forecast benchmarks under the same dynamic multi-step protocol. The headline finding is that V_Full is rank 1 across all four regime windows, but the margin against the strongest benchmarks (B0a No-change, B3 ETS, B6 Beveridge) is within the seed SD of V_Full itself. Competitive, not dominant.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Benchmark runner | 正式撰写/fix6.4/run_fix6_4_benchmarks.py | 11 benchmarks × 2 protocols × 4 regime windows |
| Benchmark metrics | 正式撰写/fix6.4/benchmark_metrics.json | Per-window per-benchmark UR metrics |
| Main post-COVID table | 正式撰写/fix6.4/tables/table1_main_postcovid_benchmark.csv | Headline window comparison |
| Regime-specific | 正式撰写/fix6.4/tables/table2_regime_specific.csv | Per-regime per-benchmark |
| Model specs | 正式撰写/fix6.4/tables/table3_model_specs.csv | Specification + inputs + training window |
| Protocol comparison | 正式撰写/fix6.4/tables/table4_protocol_comparison.csv | Dynamic vs Rolling |
| Paper-ready compact | 正式撰写/fix6.4/tables/table5_paper_ready.csv | Ratio vs ABM column |
| Trajectories | 正式撰写/fix6.4/benchmark_series.npz | Per-window per-benchmark paths |

## Protocol

1. Define 11 benchmarks: B0a NoChange, B0b HistMean, B0c Drift, B1 AR(p), B2 ARIMA, B3 ETS, B4 VAR, B5 RidgeVAR, B6 Beveridge OLS, B7 DMP, B8 Flow.
2. Fit each benchmark on 2001-01..2022-01 (or rolling origin for the rolling protocol).
3. Run dynamic multi-step forecast from 2022-01 over the post-COVID window; reuse fitted parameters without refit.
4. Compare to ABM_Full_recalibrated on the same window (post-COVID 2022-01..2026-02).
5. Report UR RMSE / MAE / Bias / Correlation per regime window; compute Ratio_vs_ABM.

## Main Outputs

- `tables/E10_T01_Dynamic_Benchmark_Comparison_v01.csv` — Main post-COVID comparison
- `tables/E10_T02_Rolling_Benchmark_Comparison_v01.csv` — Rolling-origin variant
- `tables/E10_T03_Regime_by_Benchmark_v01.csv` — Regime × benchmark cross-tab
- `tables/E10_T04_Benchmark_Specs_v01.csv` — Specification, inputs, training window
- `figures/E10_F01_Benchmark_RMSE_Bar_v01.png` — Horizontal RMSE bar
- `figures/E10_F02_Ratio_vs_ABM_v01.png` — Ratio of benchmark RMSE to ABM
- `figures/E10_F03_Paths_Dynamic_v01.png` — Forecast path overlay
- `figures/E10_F04_Regime_by_Benchmark_Heatmap_v01.png` — Regime × benchmark heatmap

## Key Numbers

| Quantity | Value |
|---|---|
| V_Full UR RMSE (post-COVID) | 0.273 pp |
| Strongest benchmark (B0a No-change) UR RMSE | 0.309 pp (ratio 1.13×) |
| Next-best (B3 ETS Damped) UR RMSE | 0.309 pp (ratio 1.13×) |
| Worst benchmark (B0c Drift) UR RMSE | 6.92 pp (ratio 25×) |
| ABM advantage over B0a | +0.036 pp (≈ V_Full seed SD) |
| V_Full rank across the 4 regime windows | 1 of 12 in 3 of 4 windows |

## Use in Manuscript

- §6.4 (S06_04) external benchmark comparison

## Caveats

- ABM training window is 2004-01..2017-12 (168 months); benchmarks train on 2001-01..2022-01 (~252 months). The window difference is documented but not equalised.
- ABM advantage over B0a No-change (0.036 pp) is the same order as the V_Full seed SD (0.023 pp). Manuscript must say 'competitive', not 'dominant'.
- Structural benchmarks (Beveridge, DMP, Flow) use observed JTSJOR/JTSLDR over the OOS window; ABM uses the same exogenous drivers, so the comparison is on equal footing for OOS exogenous information.

## Status

READY
