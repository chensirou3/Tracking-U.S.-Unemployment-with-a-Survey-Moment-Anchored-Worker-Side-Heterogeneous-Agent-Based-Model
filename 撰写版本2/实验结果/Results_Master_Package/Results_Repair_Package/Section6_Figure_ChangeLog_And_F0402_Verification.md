# Section 6 — Figure Change Log + S06_04_F02 Unit-Bug Verification

Scope: the round of repairs covering the nine paper-ready figures in `Results_PaperReady_Figures/`
that were flagged in the user's "Fix Main-Text Figures in Section 6" prompt.
This file is the single deliverable for §Deliverables of that prompt.

---

## 1. Per-figure change log

Classification key:
- **SPLIT** = composite figure split into two or more standalone figures (axes/data unchanged per panel).
- **LAYOUT** = layout / readability / label / caption changes only; underlying data identical.
- **DATA-FIX** = the rendered values themselves changed because the wrong array (or wrong units) was being plotted before.

| Figure | Class | Before → After | Notes |
|---|---|---|---|
| **S06_01_F01** → **F01A + F01B** | SPLIT | 1 composite (full + main-eval panels stacked) → 2 standalone PNGs | F01A: full post-2018 window with three regimes shaded. F01B: main-recent window (2022-01 .. 2026-02) with 0.273 pp headline call-out. Both pull from a shared helper `_load_v_full_trajectory()` so the same recalibrated `V_Full_ur` (fix6.2/reeval_trajectories.npz, averaged across 5 cal × 5 seed, decimal→percent) is plotted in both panels. |
| **S06_01_F02** → **F02A + F02B** | SPLIT | 1 two-panel composite (RMSE bar + bias bar) → 2 standalone PNGs | Axis labels normalised to: Early stable / 2020-2021 disruption / Main recent evaluation / Full post-2018. Main-recent bar continues to use the recalibrated V_Full RMSE (0.273 pp) and bias (-0.167 pp); the other three windows remain the legacy E5 dynamic-regime diagnostic and are declared in caption. Values come from `fix6.1/table1_regime_summary.csv`. |
| **S06_02_F01** (Control RMSE bar, 6.21) | LAYOUT | label crowding | Figure widened; value-label offsets adjusted so the V_Full headline annotation no longer collides with bar tops. No data change (still reads `fix6.2/tables/table1_variant_summary.csv`). |
| **S06_02_F02** (Source of Advantage, 6.22) | LAYOUT | layout polish | Vertical spacing of three-bar component-contribution chart cleaned up; "within-experiment accounting, not causal decomposition" caption tightened. No data change. |
| **S06_03_F01** (Ablation RMSE bar, 6.31) | LAYOUT | top margin | Top margin enlarged so the V_Full headline reference line + label do not collide with the title. Bar values, ordering, and Δ-vs-Full annotations unchanged. |
| **S06_03_F02** (Heterogeneity ladder, 6.32) | LAYOUT | annotations + sidecar caption | Long mechanism strings (labor_frag / search / income_exp / liquidity / housing / consumption_rule) removed from the plot area to prevent overlap. L0..L6 step labels kept; full mechanism composition moved to a sidecar file `S06_03_F02_caption.txt` for paste-in to the manuscript caption. Step values (e.g. L4→L5 = −0.2487 pp) unchanged. |
| **S06_04_F01** (Benchmark RMSE bar, 6.41) | LAYOUT | (no changes this round) | Already conformed to spec in the prior pass; verified during regeneration. |
| **S06_04_F02** (Forecast paths, 6.42) | **DATA-FIX** | ABM trajectory replaced | See §2 below. The previous version plotted `benchmark_series.npz['v_full']`, which is **not** a UR series (it is a calibration scalar replicated per month; median ≈ 1.1). The new version plots `V_Full_ur` from `fix6.2/reeval_trajectories.npz`, averaged across 5 calibration candidates × 5 evaluation seeds, decimal→percent. Benchmark set locked to the approved 6-line composition (ABM, Observed, No-change, ETS, Beveridge, Flow-based UR); auto-top-N selection removed. |
| **S06_05_F01** → **F01A + F01B + F01C + F01D** | SPLIT | 1 four-panel dashboard → 4 standalone PNGs | F01A: per-split UR RMSE (E11). F01B: log-log horizon decay (E12). F01C: agent-count plateau (E12). F01D: per-parameter CV across top-5 V_Full candidates with the CV ≥ 0.40 weak-ID threshold line and "10 of 14" annotation (E13). Package A/B/D/E labels removed; "Full ABM" replaces M0_Main. Underlying data per panel unchanged. |

Legacy composite PNGs removed from `Results_PaperReady_Figures/` and from each section's `paper_ready_figures/` mirror in `_cleanup_legacy_composites()`:
- `S06_01_F01_Observed_vs_Simulated_UR__E4_v01.png`
- `S06_01_F02_Regime_RMSE_Bar__E5_v01.png`
- `S06_05_F01_Robustness_Dashboard__E11_E12_E13_v01.png`

Downstream documents already patched (in the same round):
- `Results_Asset_Registry.csv` and `Results_Figure_Registry.csv` — old IDs replaced with the A/B(/C/D) IDs.
- `Consistency_Resolution/Results_Figure_Revision_Checklist.csv` — three composite rows marked FIXED.
- `Results_Repair_Package/Results_PaperReady_Figure_Redraw_Specs.md` — three composite rows replaced with split-FIXED rows.
- `Results_By_Section/S06_01_.../S06_01_Report.md` and `Results_By_Section/S06_05_.../S06_05_Report.md` — bullet lists updated to the new IDs.

---

## 2. S06_04_F02 unit-bug verification note

### 2.1 Symptom

The previous build of `S06_04_F02_Paths_Dynamic__E10_v01.png` produced ABM UR values in the
~140–250 % range, completely off-scale relative to the observed BLS UR (~3–5 %) and the
four benchmark trajectories (~3–5 %).

### 2.2 Hypothesis

Either (a) a benchmark series was stored as percent and being multiplied by 100 a second time,
or (b) the wrong key was being read for the ABM trajectory.

### 2.3 Inspector evidence

Two read-only diagnostic scripts were used to discriminate the two hypotheses (no writes):

**`_inspect_bench_npz.py`** on `正式撰写/fix6.4/benchmark_series.npz`:

- `tgt_ur_full`: median ≈ 0.04 → stored as **decimal**, needs `* 100` to plot as percent.
- `post_covid_norm__dynamic__B0a_NoChange_ur`, `..._B3_ETS_ur`, `..._B6_Beveridge_ur`, `..._B8_Flow_ur`: medians all in the 0.03..0.06 range → stored as **decimal**, also need `* 100`.
- `v_full`: median ≈ 1.1, range far outside any plausible UR series → **not a UR trajectory**; this key is a calibration scalar that was replicated to a length-302 array.

Conclusion: hypothesis (a) is rejected (units of the benchmark arrays are consistent with the
target series). Hypothesis (b) is confirmed: the consumer was reading the wrong key for the
ABM line.

**`_inspect_abm_trajectory.py`** on candidate locations for the actual recalibrated V_Full UR series:

- `正式撰写/fix6.2/reeval_trajectories.npz` exposes `V_Full_ur` with shape (5, 5, 302), values in the 0.03..0.06 decimal range. Averaging over the (cal, seed) axes and slicing to the 2022-01..2026-02 window yields per-month means in 3.17..4.29 %, consistent with the observed UR.
- `正式撰写/fix6.3/reeval_trajectories.npz` and `正式撰写/6.2/derived_series.npz` were inspected for completeness; neither contains the recalibrated V_Full UR. `正式撰写/6.1/baseline_seed_trajectories.npz` is the legacy M0 baseline (different family).

Conclusion: the correct source is `fix6.2/reeval_trajectories.npz['V_Full_ur']`, averaged across both the 5-candidate calibration axis and the 5-seed evaluation axis, multiplied by 100 to convert decimal → percent.

### 2.4 Fix applied (file + lines)

`撰写版本2/实验结果/_scripts/build_audit_figures.py`, function `fig_s06_04_f02`:

- The ABM trajectory is now loaded from `SRC / "fix6.2" / "reeval_trajectories.npz"`, key `V_Full_ur`, averaged over axes (0, 1), `* 100.0`.
- The benchmark set is hard-coded to the 6-line composition (ABM, Observed, No-change B0a, ETS B3, Beveridge B6, Flow-based UR B8); the previous RMSE-based auto-top-N selection (which itself depended on the corrupted arithmetic) was removed.
- The y-axis is auto-fit to the union of all six rendered series with a small symmetric pad, so the plot is now scale-correct (~3..5 %) instead of dominated by an off-scale ABM line.
- A foot-of-figure note documents the training-window asymmetry (ABM 2004-01..2017-12 vs benchmarks 2001-01..2021-12; both forecast 2022-01..2026-02 dynamically).

### 2.5 Post-fix sanity check

After running `python 撰写版本2/实验结果/_scripts/build_audit_figures.py`:

- The regenerated `S06_04_F02_Paths_Dynamic__E10_v01.png` shows ABM V_Full and Observed both in the 3..5 % band on the main recent evaluation window; the four benchmark lines (No-change, ETS, Beveridge, Flow-based UR) are also in the 3..5 % band, with relative ordering consistent with the RMSE rankings in `S06_04_T01_Benchmark_Comparison__E10_v01.csv`.
- The ABM line is visibly the closest to Observed for most of the window, consistent with the 0.273 pp headline RMSE and the locked finding that ABM beats No-change / ETS by ≈ 0.036 pp (within cross-seed SD 0.023 pp).
- No legend, label, or unit annotation in the figure references the obsolete `v_full` key.

The S06_04_F02 unit bug is closed.
