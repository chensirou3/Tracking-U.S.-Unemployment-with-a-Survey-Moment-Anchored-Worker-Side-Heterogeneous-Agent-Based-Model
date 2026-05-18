# S06_05 — Source Experiments

Manuscript section §6.5 draws on the following experiments. Full audit trails live in `Results_By_Experiment/`.

| Paper ID | Experiment | Source | Role in this section |
|---|---|---|---|
| E11 | Training-Window Sensitivity | `包A_训练窗口敏感性/run_packageA.py (archived in 6.5 pipeline) + 6.5/tables/table2_training_window.csv` | 10 splits; mean 0.245 ± 0.011 pp |
| E12 | Forecast-Horizon and Agent-Count Sensitivity | `包B/包D (archived in 6.5 pipeline) + 6.5/tables/table3_horizon.csv, table4_agent_count.csv` | Slope −0.09; plateau at N ≥ 50k |
| E13 | Calibration-Method and Parameter-ID Sensitivity | `包E_校准方法敏感性/run_packageE.py + 6.5/robustness_metrics.json` | Best-test band 0.214–0.243 pp; CV 5.55%; 10/14 params weakly identified |

See each experiment's `E##_Report.md` for the full protocol, key numbers, and caveats.