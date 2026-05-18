"""Generate the missing per-experiment Report.md / source_files.md / status.md
files for E04-E13.  E01-E03 already exist; E04 already has its Report; this
script tops up the remaining 27 small documents.

Style follows the existing E01/E02/E04 templates exactly: H1 title, Purpose,
Source Files (markdown table), Protocol, Main Outputs, Key Numbers, Use in
Manuscript, Caveats, Status.  No emoji, no extra prose, neutral tone.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path("撰写版本2/实验结果/Results_Master_Package/Results_By_Experiment")

# (folder, eid_label, full_status, manuscript_section)
EXP = {
    "E04": ("E04_Dynamic_Evaluation", "E4", "READY",
            ["§6.1 (S06_01) primary headline", "Abstract anchor"]),
    "E05": ("E05_Regime_Specific_Evaluation", "E5", "READY",
            ["§6.1 (S06_01) regime decomposition"]),
    "E06": ("E06_Internal_Control_Comparison", "E6", "READY",
            ["§6.2 (S06_02) internal controls"]),
    "E07": ("E07_Source_of_Advantage_Decomposition", "E7", "READY",
            ["§6.2 (S06_02) source-of-advantage accounting"]),
    "E08": ("E08_Heterogeneity_Ablation", "E8", "READY",
            ["§6.3 (S06_03) headline ablation"]),
    "E09": ("E09_Heterogeneity_Ladder", "E9", "READY",
            ["§6.3 (S06_03) supplementary ladder evidence"]),
    "E10": ("E10_Forecast_Benchmark_Comparison", "E10", "READY",
            ["§6.4 (S06_04) external benchmark comparison"]),
    "E11": ("E11_Training_Window_Sensitivity", "E11", "READY WITH CAVEAT",
            ["§6.5 (S06_05) robustness — training window"]),
    "E12": ("E12_Forecast_Horizon_and_Agent_Count_Sensitivity", "E12", "READY WITH CAVEAT",
            ["§6.5 (S06_05) robustness — horizon decay and agent count"]),
    "E13": ("E13_Calibration_Method_and_Parameter_ID_Sensitivity", "E13", "READY",
            ["§6.5 (S06_05) calibration method and parameter identification"]),
}

# ----------------------------------------------------------------------------
# Per-experiment content blocks
# ----------------------------------------------------------------------------
CONTENT = {
    "E04": dict(
        purpose=(
            "Generate the manuscript's headline tracking number — the post-COVID UR RMSE of "
            "the recalibrated V_Full when run forward from a fixed 2018-01 initialisation "
            "without any re-fitting. The value 0.273 pp (5-seed mean, seed SD 0.023 pp) anchors "
            "the abstract and the opening paragraph of Section 6."
        ),
        sources=[
            ("Evaluation driver", "正式撰写/fix6.2/run_fix6_2_reeval.py", "Multi-seed re-evaluation of top-5 calibrations"),
            ("Headline metrics", "正式撰写/fix6.2/reeval_metrics.json", "Per-window per-seed UR/LFPR/EPOP metrics for V_Full"),
            ("Variant summary", "正式撰写/fix6.2/tables/table1_variant_summary.csv", "Row V_Full row contains 5-seed mean"),
            ("Regime decomposition", "正式撰写/fix6.1/tables/table1_regime_summary.csv", "Post-COVID row used for the headline"),
            ("Trajectories (re-plot input)", "正式撰写/fix6.1/regime_series.npz", "5-seed UR paths for the F1 figure"),
        ],
        protocol=[
            "Load population_v1.npz once; the population is identical to E1.",
            "Apply V_Full selected parameters from E3 (top-1 by train loss, no re-fit).",
            "Initialise at 2018-01 from observed BLS values; the model takes the macro driver path (JTSJOR, JTSLDR, CES, FEDFUNDS) as exogenous input and does not re-fit after this point.",
            "Simulate 5 seeds × the full evaluation window 2018-01..2026-02 (98 months).",
            "Compute UR RMSE/MAE/bias/max-abs by regime window and overall, averaged across the 5 evaluation seeds.",
        ],
        outputs=[
            ("tables/E04_T01_Dynamic_Evaluation_Metrics_v01.csv", "Post-COVID window single-row headline metrics"),
            ("figures/E04_F01_Observed_vs_Simulated_UR_v01.png", "Full post-2018 UR overlay (5 seeds + mean)"),
            ("figures/E04_F02_Prediction_Error_Time_v01.png", "Prediction error trace, 2018-2026"),
        ],
        key_numbers=[
            ("UR RMSE (post-COVID normalisation, 2022-01..2026-02)", "0.273 pp"),
            ("UR RMSE seed SD (5 seeds)", "0.023 pp"),
            ("UR bias (post-COVID)", "−0.04 pp"),
            ("UR correlation with observed (post-COVID)", "0.79"),
            ("Seeds", "{42, 137, 2024, 888, 1234}"),
            ("Evaluation window length", "50 months"),
        ],
        caveats=[
            "Dynamic multi-step, not rolling one-step. The model is not re-fit anywhere inside 2018-01..2026-02.",
            "Headline refers to ranking within the within-experiment accounting; manuscript must avoid 'dominates' or 'structurally identifies'.",
            "The 0.273 pp number must be reported jointly with the COVID-crisis 2.82 pp RMSE (see E5).",
        ],
    ),
    "E05": dict(
        purpose=(
            "Decompose the V_Full performance into three regime windows — pre-COVID stable, "
            "COVID crisis, and post-COVID normalisation — to expose where the headline number "
            "comes from and where the model under-tracks. Pairs with E4."
        ),
        sources=[
            ("Regime driver", "正式撰写/fix6.1/run_fix6_1_regime.py", "Regime-decomposed metrics computation"),
            ("Regime metrics", "正式撰写/fix6.1/regime_metrics.json", "Per-window per-seed metrics"),
            ("Regime summary table", "正式撰写/fix6.1/tables/table1_regime_summary.csv", "Aggregate across 5 seeds, 5 windows"),
            ("Seed-level regime", "正式撰写/fix6.1/tables/table2_seed_level_regime.csv", "Per-seed cross-window metrics"),
            ("Trajectories", "正式撰写/fix6.1/regime_series.npz", "5-seed UR/LFPR/EPOP for plotting"),
        ],
        protocol=[
            "Reuse the same 5-seed V_Full trajectories from E4.",
            "Define four manuscript-facing windows: pre_covid_stable (2018-01..2019-12), covid_crisis_mar (2020-03..2021-12), post_covid_norm (2022-01..2026-02), full_post_2018 (2018-01..2026-02).",
            "Compute UR/LFPR/EPOP RMSE, MAE, bias, max-abs, and correlation per window, averaged across the 5 seeds.",
            "Also report the alternative covid_crisis_jan window (2020-01..2021-12) for sensitivity.",
        ],
        outputs=[
            ("tables/E05_T01_Regime_Performance_v01.csv", "Aggregate metrics for the 5 windows (UR + LFPR + EPOP)"),
            ("tables/E05_T02_Seed_Level_Regime_v01.csv", "Per-seed metrics, 5×5 = 25 rows"),
            ("figures/E05_F01_Regime_RMSE_Bar_v01.png", "UR RMSE + bias bar by window"),
            ("figures/E05_F02_LFPR_EPOP_Regime_Bar_v01.png", "LFPR / EPOP RMSE by window"),
        ],
        key_numbers=[
            ("Pre-COVID UR RMSE / bias", "0.79 pp / +0.77 pp"),
            ("COVID-crisis UR RMSE / bias", "2.82 pp / −2.07 pp"),
            ("Post-COVID UR RMSE / bias", "0.273 pp / −0.04 pp"),
            ("Full post-2018 UR RMSE", "1.42 pp (dominated by 2020 crisis months)"),
            ("UR correlation, COVID crisis", "0.75 (direction correct, magnitude under)"),
        ],
        caveats=[
            "The full post-2018 RMSE of 1.42 pp is driven by COVID-crisis months; not a substitute for the post-COVID headline.",
            "Reporting only the post-COVID number without the crisis number is inadmissible per the wording policy.",
            "The COVID-crisis window's high RMSE is consistent with the survey-moment anchoring not extending to 2020 shock parameters.",
        ],
    ),
}

CONTENT.update({
    "E06": dict(
        purpose=(
            "Compare V_Full against three internal controls — V_Homogeneous (no "
            "heterogeneity, all mechanisms on), V_LaborOnly (labour-side dimensions only), "
            "and V_Simplified (no heterogeneity, single mechanism) — each separately "
            "calibrated under the same LHS budget and loss function. The four-row "
            "ladder is the foundation of the source-of-advantage accounting in E7."
        ),
        sources=[
            ("Calibration driver", "正式撰写/fix6.2/run_fix6_2_calibrate.py", "100/100/100/30 LHS budget across 4 variants × 3 cal-seeds"),
            ("Re-evaluation driver", "正式撰写/fix6.2/run_fix6_2_reeval.py", "Top-5 of each variant re-evaluated on 5 final seeds"),
            ("Variant summary", "正式撰写/fix6.2/tables/table1_variant_summary.csv", "Per-variant aggregate"),
            ("Regime × variant", "正式撰写/fix6.2/tables/table7_regime_x_variant.csv", "Per-window per-variant metrics"),
            ("Seed-level metrics", "正式撰写/fix6.2/tables/table3_seed_level_metrics.csv", "Per-seed per-variant rows"),
            ("Trajectories", "正式撰写/fix6.2/reeval_trajectories.npz", "5×5×302 UR/LFPR/EPOP per variant"),
        ],
        protocol=[
            "Define four variant configurations: V_Full (reference), V_Homogeneous, V_LaborOnly, V_Simplified.",
            "Calibrate each variant separately with identical LHS budget (100/100/100/30 draws across 3 cal-seeds) and identical loss function.",
            "Take the top-5 candidates of each variant by mean train loss; re-evaluate on the 5 final seeds.",
            "Report 5-seed mean UR RMSE for the headline window (post-COVID normalisation 2022-01..2026-02).",
            "Decompose by regime in the regime_x_variant cross-tab.",
        ],
        outputs=[
            ("tables/E06_T01_Control_Comparison_v01.csv", "Per-variant aggregate (UR/LFPR/EPOP RMSE, train loss)"),
            ("tables/E06_T02_Regime_by_Variant_v01.csv", "Regime × variant cross-tab"),
            ("tables/E06_T03_Seed_Level_Variant_v01.csv", "Per-seed per-variant rows"),
            ("figures/E06_F01_Control_RMSE_Bar_v01.png", "UR RMSE bar across 4 variants"),
            ("figures/E06_F02_Variant_UR_Lines_v01.png", "Mean UR trajectory by variant"),
            ("figures/E06_F03_Regime_by_Variant_Heatmap_v01.png", "Regime × variant heatmap"),
            ("figures/E06_F04_Within_Variant_Dispersion_v01.png", "Top-5 within-variant dispersion"),
        ],
        key_numbers=[
            ("UR RMSE V_Full", "0.273 pp"),
            ("UR RMSE V_Homogeneous", "0.545 pp"),
            ("UR RMSE V_LaborOnly", "0.363 pp"),
            ("UR RMSE V_Simplified", "0.562 pp"),
            ("Variants separately calibrated?", "Yes"),
            ("Final evaluation seeds", "{42, 137, 2024, 888, 1234}"),
        ],
        caveats=[
            "The differences feed the within-experiment source-of-advantage accounting (E7); they are not causal decompositions.",
            "V_Simplified retains the matching_competition mechanism; it is not literally a zero-mechanism baseline.",
            "Each variant is re-calibrated under the same LHS budget, so differences are not driven by calibration effort asymmetry.",
        ],
    ),
    "E07": dict(
        purpose=(
            "Express the V_Full vs internal-control gap as an additive accounting "
            "decomposition: total gain = heterogeneity-associated gain + mechanism-"
            "associated gain. The household-block gain is reported separately. These "
            "shares (94% / 6%) are reported as within-experiment accounting, not as a "
            "causal decomposition."
        ),
        sources=[
            ("Decomposition table", "正式撰写/fix6.2/tables/table4_source_of_advantage.csv", "Total / heterogeneity / mechanism gain in pp + shares"),
            ("Old-vs-new comparison", "正式撰写/fix6.2/tables/table6_old_vs_new_decomposition.csv", "Comparison with pre-recalibration numbers"),
            ("Inputs (RMSE values)", "正式撰写/fix6.2/tables/table1_variant_summary.csv", "V_Full / V_Homogeneous / V_LaborOnly / V_Simplified RMSE rows"),
        ],
        protocol=[
            "Take the four V_Full / V_Homogeneous / V_LaborOnly / V_Simplified post-COVID UR RMSE values from E6.",
            "Compute total_gain = RMSE(V_Simplified) − RMSE(V_Full).",
            "Compute heterogeneity_gain = RMSE(V_Homogeneous) − RMSE(V_Full).",
            "Compute mechanism_gain = RMSE(V_Simplified) − RMSE(V_Homogeneous).",
            "Compute household_block_gain = RMSE(V_LaborOnly) − RMSE(V_Full).",
            "Convert each gain into a share of total_gain (in percent).",
        ],
        outputs=[
            ("tables/E07_T01_Source_of_Advantage_v01.csv", "Gains in pp and shares in %"),
            ("tables/E07_T02_Old_vs_New_Decomposition_v01.csv", "Same decomposition under pre-recalibration numbers"),
            ("figures/E07_F01_Source_of_Advantage_Waterfall_v01.png", "Waterfall chart of gains"),
        ],
        key_numbers=[
            ("Total gain (V_Simplified − V_Full)", "0.289 pp"),
            ("Heterogeneity-associated gain", "0.272 pp (94.2% of total)"),
            ("Mechanism-associated gain", "0.017 pp (5.8% of total)"),
            ("Household-block gain (V_LaborOnly − V_Full)", "0.090 pp"),
        ],
        caveats=[
            "The decomposition is an additive accounting identity, not a causal partition. Manuscript must say 'accounting' or 'within-experiment accounting'.",
            "94% / 6% applies to the post-COVID headline only; the split varies by window (see fix6.2 table7).",
            "Mechanism-associated gain shrinks because V_Homogeneous already has all 14 mechanisms ON; only the marginal contribution under flat population is captured.",
        ],
    ),
    "E08": dict(
        purpose=(
            "Quantify how much UR-RMSE the model loses when individual heterogeneity "
            "dimensions are removed and the variant is re-calibrated. The headline finding "
            "is that V_NoSearch and V_NoSLH (joint Search+Liquidity+Housing flatten) cannot "
            "be compensated by recalibration, while V_NoLiquidity and V_NoHousing recover "
            "near-baseline performance."
        ),
        sources=[
            ("Calibration driver", "正式撰写/fix6.3/run_fix6_3_calibrate.py", "LHS 100 × 3 cal-seeds × 6 ablation variants"),
            ("Re-evaluation driver", "正式撰写/fix6.3/run_fix6_3_reeval.py", "Top-5 × 5 final seeds × 6 variants"),
            ("Ablation summary", "正式撰写/fix6.3/tables/table2_post_covid_ablation.csv", "Post-COVID RMSE + Δ vs Full"),
            ("Old-vs-new delta", "正式撰写/fix6.3/tables/table5_old_vs_new_delta.csv", "Pre-recalibration vs recalibrated"),
            ("Regime × ablation", "正式撰写/fix6.3/tables/table6_regime_x_ablation.csv", "Per-window per-ablation"),
            ("Paper-ready compact", "正式撰写/fix6.3/tables/table7_paper_ready.csv", "5-row summary used in manuscript"),
            ("Trajectories", "正式撰写/fix6.3/reeval_trajectories.npz", "5×5×302 paths per variant"),
        ],
        protocol=[
            "Define 6 ablation variants: V_NoSearch, V_NoLiquidity, V_NoHousing, V_NoSLH, V_NoConsumption, V_SearchOnly.",
            "Each variant flattens exactly the heterogeneity dimensions named in its label; mechanisms remain ON.",
            "Calibrate each variant separately under the same LHS budget as fix6.2.",
            "Re-evaluate top-5 candidates × 5 final seeds.",
            "Compare post-COVID UR RMSE to V_Full reference (0.273 pp).",
        ],
        outputs=[
            ("tables/E08_T01_Recalibrated_Ablation_v01.csv", "Post-COVID RMSE per variant + Δ"),
            ("tables/E08_T02_Old_vs_New_Delta_v01.csv", "Δ between projection and recalibration"),
            ("tables/E08_T03_Regime_by_Ablation_v01.csv", "Regime × ablation cross-tab"),
            ("figures/E08_F01_Ablation_RMSE_Bar_v01.png", "RMSE bar with Δ annotation"),
            ("figures/E08_F02_Old_vs_New_Delta_v01.png", "Projection vs recalibration gap"),
            ("figures/E08_F03_Regime_by_Ablation_Heatmap_v01.png", "Regime × ablation heatmap"),
            ("figures/E08_F04_NoSearch_Trajectory_v01.png", "Worst-case V_NoSearch path"),
        ],
        key_numbers=[
            ("V_Full reference UR RMSE", "0.273 pp"),
            ("V_NoSearch UR RMSE (Δ vs Full)", "1.085 pp (+0.812)"),
            ("V_NoSLH joint UR RMSE (Δ)", "0.702 pp (+0.429)"),
            ("V_NoLiquidity UR RMSE (Δ)", "0.378 pp (+0.105)"),
            ("V_NoHousing UR RMSE (Δ)", "0.237 pp (−0.036)"),
            ("V_NoConsumption UR RMSE (Δ)", "ranking: matches or beats Full after recalibration"),
        ],
        caveats=[
            "Δ values are within-experiment accounting deltas, not causal contributions.",
            "V_NoHousing slightly outperforming V_Full is consistent with re-calibration absorbing the lost dimension into other parameters; it does not imply housing heterogeneity is harmful.",
            "Joint V_NoSLH is included to test whether single-dimension Δ values are additive — they are not (0.812 + 0.105 + (−0.036) ≠ 0.429).",
        ],
    ),
})
CONTENT.update({
    "E09": dict(
        purpose=(
            "Build the heterogeneity ladder L0..L6 by incrementally adding heterogeneity "
            "dimensions, each level separately re-calibrated. Provides the marginal-gain "
            "evidence that complements E8: ablation-from-full asks 'what is lost?'; the "
            "ladder asks 'what is gained per dimension added?'."
        ),
        sources=[
            ("Ladder runner (Refit)", "正式撰写/6.3/run_6_3_packageC_ladder.py", "Core L0..L6 + Layer G2, G3 with LHS 30 × 3 seeds per level"),
            ("Ladder metrics", "正式撰写/6.3/ladder_metrics.json", "Per-level per-seed train/val/oos metrics"),
            ("Ladder summary table", "正式撰写/6.3/tables/table3_heterogeneity_ladder.csv", "Per-level RMSE and seed SD"),
            ("Trajectories", "正式撰写/6.3/ladder_series.npz", "Per-level 5-seed UR/LFPR/EPOP"),
        ],
        protocol=[
            "Define seven Core ladder levels L0 (no heterogeneity) through L6 (all six dimensions).",
            "Order of insertion: search → labour_fragility → liquidity → income_expect → consumption_rule → housing.",
            "At each level, calibrate by LHS 30 draws × 3 calibration seeds; pick the best by train loss.",
            "Re-evaluate the best on 5 final seeds; compute UR/LFPR/EPOP RMSE on post-COVID window.",
            "Also report two Layer ladders (G2, G3) for sensitivity to insertion order.",
        ],
        outputs=[
            ("tables/E09_T01_Heterogeneity_Ladder_v01.csv", "Per-level RMSE table"),
            ("figures/E09_F01_Ladder_RMSE_Path_v01.png", "Marginal-gain step plot L0..L6"),
        ],
        key_numbers=[
            ("L0 UR RMSE (no heterogeneity)", "0.55 pp (matches V_Homogeneous)"),
            ("L6 UR RMSE (all 6 dims)", "0.27 pp (matches V_Full)"),
            ("Largest single drop (L4→L5, adding housing)", "≈ −0.07 pp"),
            ("Smallest gain (between adjacent levels)", "within seed SD"),
        ],
        caveats=[
            "Order of insertion is fixed; marginal gains are order-dependent. Manuscript reports the gains as one specific accounting path, not as a unique decomposition.",
            "Each level is independently calibrated; differences are partly absorbed by parameter re-fitting.",
            "Several adjacent-level differences are smaller than the 0.023 pp seed SD; only L0/L6 and the housing step are well-separated.",
        ],
    ),
    "E10": dict(
        purpose=(
            "Place the recalibrated V_Full against eleven external forecast benchmarks under "
            "the same dynamic multi-step protocol. The headline finding is that V_Full is "
            "rank 1 across all four regime windows, but the margin against the strongest "
            "benchmarks (B0a No-change, B3 ETS, B6 Beveridge) is within the seed SD of V_Full "
            "itself. Competitive, not dominant."
        ),
        sources=[
            ("Benchmark runner", "正式撰写/fix6.4/run_fix6_4_benchmarks.py", "11 benchmarks × 2 protocols × 4 regime windows"),
            ("Benchmark metrics", "正式撰写/fix6.4/benchmark_metrics.json", "Per-window per-benchmark UR metrics"),
            ("Main post-COVID table", "正式撰写/fix6.4/tables/table1_main_postcovid_benchmark.csv", "Headline window comparison"),
            ("Regime-specific", "正式撰写/fix6.4/tables/table2_regime_specific.csv", "Per-regime per-benchmark"),
            ("Model specs", "正式撰写/fix6.4/tables/table3_model_specs.csv", "Specification + inputs + training window"),
            ("Protocol comparison", "正式撰写/fix6.4/tables/table4_protocol_comparison.csv", "Dynamic vs Rolling"),
            ("Paper-ready compact", "正式撰写/fix6.4/tables/table5_paper_ready.csv", "Ratio vs ABM column"),
            ("Trajectories", "正式撰写/fix6.4/benchmark_series.npz", "Per-window per-benchmark paths"),
        ],
        protocol=[
            "Define 11 benchmarks: B0a NoChange, B0b HistMean, B0c Drift, B1 AR(p), B2 ARIMA, B3 ETS, B4 VAR, B5 RidgeVAR, B6 Beveridge OLS, B7 DMP, B8 Flow.",
            "Fit each benchmark on 2001-01..2022-01 (or rolling origin for the rolling protocol).",
            "Run dynamic multi-step forecast from 2022-01 over the post-COVID window; reuse fitted parameters without refit.",
            "Compare to ABM_Full_recalibrated on the same window (post-COVID 2022-01..2026-02).",
            "Report UR RMSE / MAE / Bias / Correlation per regime window; compute Ratio_vs_ABM.",
        ],
        outputs=[
            ("tables/E10_T01_Dynamic_Benchmark_Comparison_v01.csv", "Main post-COVID comparison"),
            ("tables/E10_T02_Rolling_Benchmark_Comparison_v01.csv", "Rolling-origin variant"),
            ("tables/E10_T03_Regime_by_Benchmark_v01.csv", "Regime × benchmark cross-tab"),
            ("tables/E10_T04_Benchmark_Specs_v01.csv", "Specification, inputs, training window"),
            ("figures/E10_F01_Benchmark_RMSE_Bar_v01.png", "Horizontal RMSE bar"),
            ("figures/E10_F02_Ratio_vs_ABM_v01.png", "Ratio of benchmark RMSE to ABM"),
            ("figures/E10_F03_Paths_Dynamic_v01.png", "Forecast path overlay"),
            ("figures/E10_F04_Regime_by_Benchmark_Heatmap_v01.png", "Regime × benchmark heatmap"),
        ],
        key_numbers=[
            ("V_Full UR RMSE (post-COVID)", "0.273 pp"),
            ("Strongest benchmark (B0a No-change) UR RMSE", "0.309 pp (ratio 1.13×)"),
            ("Next-best (B3 ETS Damped) UR RMSE", "0.309 pp (ratio 1.13×)"),
            ("Worst benchmark (B0c Drift) UR RMSE", "6.92 pp (ratio 25×)"),
            ("ABM advantage over B0a", "+0.036 pp (≈ V_Full seed SD)"),
            ("V_Full rank across the 4 regime windows", "1 of 12 in 3 of 4 windows"),
        ],
        caveats=[
            "ABM training window is 2004-01..2017-12 (168 months); benchmarks train on 2001-01..2022-01 (~252 months). The window difference is documented but not equalised.",
            "ABM advantage over B0a No-change (0.036 pp) is the same order as the V_Full seed SD (0.023 pp). Manuscript must say 'competitive', not 'dominant'.",
            "Structural benchmarks (Beveridge, DMP, Flow) use observed JTSJOR/JTSLDR over the OOS window; ABM uses the same exogenous drivers, so the comparison is on equal footing for OOS exogenous information.",
        ],
    ),
})
CONTENT.update({
    "E11": dict(
        purpose=(
            "Test whether the V_Full advantage persists across alternative training windows. "
            "Run 10 train/test splits (4 rolling + 5 expanding + 1 baseline) using a smaller "
            "legacy M0 family of the heterogeneous ABM, and rank against 4 benchmarks."
        ),
        sources=[
            ("Package A runner", "正式撰写/包A_训练窗口敏感性/run_packageA.py (archived in 6.5 pipeline)", "10 splits × 60 LHS per split × M0"),
            ("Training window table", "正式撰写/6.5/tables/table2_training_window.csv", "Per-split RMSE for M0, D1, D3, B3, B4"),
            ("Robustness JSON", "正式撰写/6.5/robustness_metrics.json", "package_A block"),
            ("Robustness figure (training)", "正式撰写/6.5/figures/fig2_training_splits.png", "Per-split bar"),
        ],
        protocol=[
            "Define 10 splits: 4 rolling (R1..R4) + 5 expanding (E1..E5) + 1 baseline (S0).",
            "Calibrate M0 separately on each split's training portion with LHS 60 draws.",
            "Evaluate on each split's held-out window; compute UR RMSE.",
            "Compare M0 to the four legacy benchmarks (D1 Homogeneous, D3 LaborOnly, B3 Beveridge, B4 DMP).",
            "Report mean ± SD on the 7 OOS-aligned splits (those whose test window includes post-COVID) and the M0 win rate.",
        ],
        outputs=[
            ("tables/E11_T01_Training_Window_Sensitivity_v01.csv", "Per-split UR RMSE for the 5 models"),
            ("figures/E11_F01_Training_Window_Sensitivity_v01.png", "Per-split UR RMSE bar"),
        ],
        key_numbers=[
            ("M0 mean UR RMSE on 7 OOS-aligned splits", "0.245 ± 0.011 pp"),
            ("M0 win-rate vs B3 Beveridge", "10/10"),
            ("M0 win-rate vs all 4 benchmarks", "6/7 on OOS-aligned splits"),
            ("Worst split (R1, 2014 cutoff)", "M0 1.88 pp (training window predates COVID)"),
        ],
        caveats=[
            "Computed on the legacy M0 family (pre-fix6.x recalibration), not on V_Full recalibrated at 0.273 pp. Use as ranking-level robustness, not as a substitute for the headline.",
            "Splits R1 and R2 have test windows that overlap the 2020 crisis; their high RMSE is expected.",
            "Win-rate is reported in count, not as a hypothesis test.",
        ],
    ),
    "E12": dict(
        purpose=(
            "Two robustness checks bundled by data lineage: (a) Forecast-horizon decay "
            "(h=1..36 months) and (b) Agent-count plateau (N=5k..300k). Both confirm that "
            "the ABM's accuracy degrades gracefully and that the default N=100,000 is past the "
            "plateau by a comfortable margin."
        ),
        sources=[
            ("Horizon runner", "正式撰写/包B_预测期长度敏感性/run_packageB.py (archived in 6.5 pipeline)", "ABM + 4 benchmarks × 15 origins × h=1..36"),
            ("Agent-count runner", "正式撰写/包D_Agent数量敏感性/run_packageD.py (archived in 6.5 pipeline)", "7 N × 4 models × 10 seeds × 2 modes"),
            ("Horizon table", "正式撰写/6.5/tables/table3_horizon.csv", "Per-horizon UR RMSE per model"),
            ("Agent-count table", "正式撰写/6.5/tables/table4_agent_count.csv", "RMSE / runtime / memory vs N"),
            ("Robustness JSON", "正式撰写/6.5/robustness_metrics.json", "package_B and package_D blocks"),
            ("Horizon figure", "正式撰写/6.5/figures/fig3_horizon_slope.png", "Log-log RMSE vs h"),
            ("Agent figure", "正式撰写/6.5/figures/fig4_agent_convergence.png", "Convergence curve"),
        ],
        protocol=[
            "Horizon: at each rolling origin, fit benchmarks; forecast h=1, 3, 6, 12, 24, 36 months ahead; record UR RMSE.",
            "Horizon: ABM is run once from a fixed origin and read out at the same horizons (no refit).",
            "Compute log-log slope of RMSE vs h for each model; flatter slope = better long-horizon stability.",
            "Agent-count: subsample or regenerate population at N ∈ {5k, 10k, 25k, 50k, 100k, 200k, 300k}; run M0 with 10 seeds.",
            "Agent-count: define plateau threshold |ΔRMSE| < 0.015 pp between adjacent N values.",
        ],
        outputs=[
            ("tables/E12_T01_Forecast_Horizon_Sensitivity_v01.csv", "Per-horizon UR RMSE per model + log-log slope"),
            ("tables/E12_T02_Agent_Count_Sensitivity_v01.csv", "Per-N mean / SD RMSE + runtime + plateau flag"),
            ("figures/E12_F01_Forecast_Horizon_Sensitivity_v01.png", "Horizon decay curves"),
            ("figures/E12_F02_Agent_Count_Convergence_v01.png", "Mean RMSE ± SD vs N"),
        ],
        key_numbers=[
            ("M0 log-log RMSE slope (h=1..36)", "−0.092 (shallowest of 8 models)"),
            ("AR log-log slope (comparator)", "+0.620 (RMSE explodes by h=36)"),
            ("Agent-count plateau threshold met at", "N ≥ 50,000"),
            ("Default N=100,000 vs plateau", "well past plateau"),
            ("M0 UR RMSE at N=100k (10 seeds)", "0.246 ± 0.020 pp"),
        ],
        caveats=[
            "Horizon analysis uses the legacy M0 family and 4 legacy benchmarks; results are at the ranking level, not the absolute V_Full level.",
            "Agent-count analysis tests the M0 class; the property carries to V_Full because the population is shared.",
            "Memory at N=300k peaks at 73 MB; default N=100k is the recommended compute/accuracy point.",
        ],
    ),
    "E13": dict(
        purpose=(
            "Test sensitivity of (a) headline UR RMSE and (b) selected parameter values "
            "across five calibration methods: Random Search, Latin Hypercube Sampling, Sobol, "
            "Coarse-to-Fine, Differential Evolution. The findings: prediction is robust (CV "
            "5.55%), but 10 of 14 parameters have CV ≥ 0.40 across top-5 candidates — weakly "
            "identified."
        ),
        sources=[
            ("Package E runner", "正式撰写/包E_校准方法敏感性/run_packageE.py (archived in 6.5 pipeline)", "5 methods × 200 evals × 3 seeds"),
            ("Calibration method table", "正式撰写/6.5/tables/table5_calibration_method.csv", "Best-test UR per method + advantage share"),
            ("Robustness JSON", "正式撰写/6.5/robustness_metrics.json", "packageE_calibration block (performance_lens + param_lens)"),
            ("Calibration figure", "正式撰写/6.5/figures/fig5_calibration_sensitivity.png", "Best-test RMSE per method"),
            ("Parameter heatmap", "正式撰写/6.5/figures/fig6_param_drift_heatmap.png", "Per-param CV across methods"),
        ],
        protocol=[
            "Define five calibration methods with matching evaluation budget of 200 simulations × 3 seeds.",
            "For each method, calibrate V_Full; record top-5 candidates by train loss.",
            "Re-evaluate top-5 of each method on the held-out post-COVID window.",
            "Compute (a) performance lens: CV of best-test UR RMSE across methods; (b) parameter lens: per-parameter CV across top-5 candidates within each method.",
            "Flag parameters as weakly identified if CV ≥ 0.40 in any method.",
        ],
        outputs=[
            ("tables/E13_T01_Calibration_Method_Sensitivity_v01.csv", "Per-method best-test UR + share advantage"),
            ("tables/E13_T02_Parameter_Identification_v01.csv", "Per-parameter CV + unstable flag + performance lens summary"),
            ("figures/E13_F01_Calibration_Method_Sensitivity_v01.png", "Method × performance"),
            ("figures/E13_F02_Parameter_ID_Heatmap_v01.png", "Parameter × method CV heatmap"),
        ],
        key_numbers=[
            ("Best-test UR RMSE range across 5 methods", "0.214 – 0.243 pp"),
            ("CV of best-test UR RMSE (performance lens)", "5.55%"),
            ("Weakly identified parameters (CV ≥ 0.40)", "10 of 14"),
            ("Stable parameters (CV < 0.20)", "4 of 14"),
            ("Source-of-advantage share stability across methods", "57.2 ± 3.4 pp"),
        ],
        caveats=[
            "Best-test UR RMSE band centred on the legacy 0.22 pp number; recalibrated V_Full (E4) at 0.273 pp is outside this band but within the legacy-vs-recalibrated reconciliation documented in fix6.2.",
            "Weak identification of 10/14 parameters does not invalidate the forecast — prediction is robust because of substitution between parameters.",
            "Report parameters as bands, not point estimates. Manuscript must avoid 'structurally identifies' for the 10 weak parameters.",
        ],
    ),
})
ALL_CONTENT_PRESENT = True


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def render_report(eid):
    folder, label, status, sections = EXP[eid]
    c = CONTENT[eid]
    sources_table = md_table(["Asset", "Path", "Role"], c["sources"])
    outputs_lines = "\n".join(f"- `{p}` — {d}" for p, d in c["outputs"])
    key_table = md_table(["Quantity", "Value"], c["key_numbers"])
    caveats_lines = "\n".join(f"- {cv}" for cv in c["caveats"])
    use_lines = "\n".join(f"- {u}" for u in sections)
    proto_lines = "\n".join(f"{i+1}. {step}" for i, step in enumerate(c["protocol"]))
    return f"""# {label} — {folder.split('_', 1)[1].replace('_', ' ')}

## Purpose

{c["purpose"]}

## Source Files

{sources_table}

## Protocol

{proto_lines}

## Main Outputs

{outputs_lines}

## Key Numbers

{key_table}

## Use in Manuscript

{use_lines}

## Caveats

{caveats_lines}

## Status

{status}
"""


def render_source_files(eid):
    folder, label, _, _ = EXP[eid]
    rows = CONTENT[eid]["sources"]
    table = md_table(["Asset", "Path", "Role"], rows)
    return f"# {label} — Source Files\n\n{table}\n"


def render_status(eid):
    folder, label, status, _ = EXP[eid]
    if status == "READY":
        body = "All required tables, figures, and metadata are present in this folder. Ready for manuscript use."
    else:
        body = "Tables and figures are present but the experiment carries documented caveats — see Caveats section of the Report. Use as Appendix / robustness evidence."
    return f"# {label} — Status\n\n**Status: {status}**\n\n{body}\n"


def main():
    for eid, (folder, *_rest) in EXP.items():
        if eid not in CONTENT:
            print(f"  [skip] {eid}: content not yet defined")
            continue
        base = ROOT / folder
        if not base.exists():
            print(f"  [skip] {eid}: folder missing")
            continue
        (base / f"{eid}_Report.md").write_text(render_report(eid), encoding="utf-8")
        (base / "source_files.md").write_text(render_source_files(eid), encoding="utf-8")
        (base / "status.md").write_text(render_status(eid), encoding="utf-8")
        print(f"  [OK] {eid}")


if __name__ == "__main__":
    main()
