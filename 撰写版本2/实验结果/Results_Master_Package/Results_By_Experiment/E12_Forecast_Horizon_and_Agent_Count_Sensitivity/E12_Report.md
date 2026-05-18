# E12 — Forecast Horizon and Agent Count Sensitivity

## Purpose

Two robustness checks bundled by data lineage: (a) Forecast-horizon decay (h=1..36 months) and (b) Agent-count plateau (N=5k..300k). Both confirm that the ABM's accuracy degrades gracefully and that the default N=100,000 is past the plateau by a comfortable margin.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Horizon runner | 正式撰写/包B_预测期长度敏感性/run_packageB.py (archived in 6.5 pipeline) | ABM + 4 benchmarks × 15 origins × h=1..36 |
| Agent-count runner | 正式撰写/包D_Agent数量敏感性/run_packageD.py (archived in 6.5 pipeline) | 7 N × 4 models × 10 seeds × 2 modes |
| Horizon table | 正式撰写/6.5/tables/table3_horizon.csv | Per-horizon UR RMSE per model |
| Agent-count table | 正式撰写/6.5/tables/table4_agent_count.csv | RMSE / runtime / memory vs N |
| Robustness JSON | 正式撰写/6.5/robustness_metrics.json | package_B and package_D blocks |
| Horizon figure | 正式撰写/6.5/figures/fig3_horizon_slope.png | Log-log RMSE vs h |
| Agent figure | 正式撰写/6.5/figures/fig4_agent_convergence.png | Convergence curve |

## Protocol

1. Horizon: at each rolling origin, fit benchmarks; forecast h=1, 3, 6, 12, 24, 36 months ahead; record UR RMSE.
2. Horizon: ABM is run once from a fixed origin and read out at the same horizons (no refit).
3. Compute log-log slope of RMSE vs h for each model; flatter slope = better long-horizon stability.
4. Agent-count: subsample or regenerate population at N ∈ {5k, 10k, 25k, 50k, 100k, 200k, 300k}; run M0 with 10 seeds.
5. Agent-count: define plateau threshold |ΔRMSE| < 0.015 pp between adjacent N values.

## Main Outputs

- `tables/E12_T01_Forecast_Horizon_Sensitivity_v01.csv` — Per-horizon UR RMSE per model + log-log slope
- `tables/E12_T02_Agent_Count_Sensitivity_v01.csv` — Per-N mean / SD RMSE + runtime + plateau flag
- `figures/E12_F01_Forecast_Horizon_Sensitivity_v01.png` — Horizon decay curves
- `figures/E12_F02_Agent_Count_Convergence_v01.png` — Mean RMSE ± SD vs N

## Key Numbers

| Quantity | Value |
|---|---|
| M0 log-log RMSE slope (h=1..36) | −0.092 (shallowest of 8 models) |
| AR log-log slope (comparator) | +0.620 (RMSE explodes by h=36) |
| Agent-count plateau threshold met at | N ≥ 50,000 |
| Default N=100,000 vs plateau | well past plateau |
| M0 UR RMSE at N=100k (10 seeds) | 0.246 ± 0.020 pp |

## Use in Manuscript

- §6.5 (S06_05) robustness — horizon decay and agent count

## Caveats

- Horizon analysis uses the legacy M0 family and 4 legacy benchmarks; results are at the ranking level, not the absolute V_Full level.
- Agent-count analysis tests the M0 class; the property carries to V_Full because the population is shared.
- Memory at N=300k peaks at 73 MB; default N=100k is the recommended compute/accuracy point.

## Status

READY WITH CAVEAT
