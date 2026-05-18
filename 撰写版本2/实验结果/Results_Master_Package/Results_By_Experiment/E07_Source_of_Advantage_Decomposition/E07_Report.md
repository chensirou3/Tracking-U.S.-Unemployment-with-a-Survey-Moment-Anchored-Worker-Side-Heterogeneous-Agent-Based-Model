# E7 — Source of Advantage Decomposition

## Purpose

Express the V_Full vs internal-control gap as an additive accounting decomposition: total gain = heterogeneity-associated gain + mechanism-associated gain. The household-block gain is reported separately. These shares (94% / 6%) are reported as within-experiment accounting, not as a causal decomposition.

## Source Files

| Asset | Path | Role |
|---|---|---|
| Decomposition table | 正式撰写/fix6.2/tables/table4_source_of_advantage.csv | Total / heterogeneity / mechanism gain in pp + shares |
| Old-vs-new comparison | 正式撰写/fix6.2/tables/table6_old_vs_new_decomposition.csv | Comparison with pre-recalibration numbers |
| Inputs (RMSE values) | 正式撰写/fix6.2/tables/table1_variant_summary.csv | V_Full / V_Homogeneous / V_LaborOnly / V_Simplified RMSE rows |

## Protocol

1. Take the four V_Full / V_Homogeneous / V_LaborOnly / V_Simplified post-COVID UR RMSE values from E6.
2. Compute total_gain = RMSE(V_Simplified) − RMSE(V_Full).
3. Compute heterogeneity_gain = RMSE(V_Homogeneous) − RMSE(V_Full).
4. Compute mechanism_gain = RMSE(V_Simplified) − RMSE(V_Homogeneous).
5. Compute household_block_gain = RMSE(V_LaborOnly) − RMSE(V_Full).
6. Convert each gain into a share of total_gain (in percent).

## Main Outputs

- `tables/E07_T01_Source_of_Advantage_v01.csv` — Gains in pp and shares in %
- `tables/E07_T02_Old_vs_New_Decomposition_v01.csv` — Same decomposition under pre-recalibration numbers
- `figures/E07_F01_Source_of_Advantage_Waterfall_v01.png` — Waterfall chart of gains
- `figures/E07_F02_Component_Contribution_Bar_v01.png` — Side-by-side bar chart of heterogeneity-associated vs mechanism-associated gain (pp and % of total) on the post-COVID window

## Key Numbers

| Quantity | Value |
|---|---|
| Total gain (V_Simplified − V_Full) | 0.289 pp |
| Heterogeneity-associated gain | 0.272 pp (94.2% of total) |
| Mechanism-associated gain | 0.017 pp (5.8% of total) |
| Household-block gain (V_LaborOnly − V_Full) | 0.090 pp |

## Use in Manuscript

- §6.2 (S06_02) source-of-advantage accounting

## Caveats

- The decomposition is an additive accounting identity, not a causal partition. Manuscript must say 'accounting' or 'within-experiment accounting'.
- 94% / 6% applies to the post-COVID headline only; the split varies by window (see fix6.2 table7).
- Mechanism-associated gain shrinks because V_Homogeneous already has all 14 mechanisms ON; only the marginal contribution under flat population is captured.

## Status

READY
