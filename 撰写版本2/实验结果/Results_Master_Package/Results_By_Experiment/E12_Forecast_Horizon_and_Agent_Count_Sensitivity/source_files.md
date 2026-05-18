# E12 — Source Files

| Asset | Path | Role |
|---|---|---|
| Horizon runner | 正式撰写/包B_预测期长度敏感性/run_packageB.py (archived in 6.5 pipeline) | ABM + 4 benchmarks × 15 origins × h=1..36 |
| Agent-count runner | 正式撰写/包D_Agent数量敏感性/run_packageD.py (archived in 6.5 pipeline) | 7 N × 4 models × 10 seeds × 2 modes |
| Horizon table | 正式撰写/6.5/tables/table3_horizon.csv | Per-horizon UR RMSE per model |
| Agent-count table | 正式撰写/6.5/tables/table4_agent_count.csv | RMSE / runtime / memory vs N |
| Robustness JSON | 正式撰写/6.5/robustness_metrics.json | package_B and package_D blocks |
| Horizon figure | 正式撰写/6.5/figures/fig3_horizon_slope.png | Log-log RMSE vs h |
| Agent figure | 正式撰写/6.5/figures/fig4_agent_convergence.png | Convergence curve |
