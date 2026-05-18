# ABM Simulation Calendar and Window Mapping

**Resolves P1 item #19 (initialisation-vs-evaluation window split, t-index ↔ calendar mapping) and P1 item #24 (ABM-vs-benchmark training-window alignment).**

Source of truth:
- `Phase3_Code/environment_real.py` (lines 16–52) — defines the date sequence and `T`.
- `Phase3_Code/calibration_engine.py` (lines 37–45) — defines `TRAIN_END`.
- `Phase3_Code/scheduler.py` — runs `for t in range(self.T)` with no separate burn-in flag.
- `正式撰写/fix6.1/run_fix6_1_regime.py` and `正式撰写/fix6.2/run_fix6_2_reeval.py` — define the eight evaluation windows.

## 1. Index ↔ calendar mapping

The full simulation spans **T = 302 months** with `start = 2001-01`, `end = 2026-02`. Index 0 corresponds to 2001-01; index `t` corresponds to month `2001-01 + t`. The mapping is constructed deterministically in `RealEnvironment.__init__` and is used identically by every variant and every benchmark.

| Anchor date | Index `t` | Role |
|---|---:|---|
| 2001-01 | 0 | Simulation start |
| 2004-01 | 36 | **Train start** (= calibration burn-in cutoff) |
| 2018-01 | 204 | Train end / Validation start / Pre-COVID-stable window start |
| 2020-01 | 228 | COVID-Crisis (Jan) window start (also `TRAIN_END` in `calibration_engine.py`) |
| 2020-03 | 230 | COVID-Crisis (Mar) window start |
| 2022-01 | 252 | COVID-Crisis end / Post-COVID-normalization window start |
| 2026-02 | 301 | Simulation end |

## 2. Burn-in convention

The simulation does **not** maintain a separate burn-in / warm-up flag. The scheduler runs from `t = 0` to `t = T-1` and the population is initialised once at `t = 0` using the SCE-anchored synthetic-population draw (see `Phase2_Code/population_init_engine.py`, fixed seed = 42).

What is conventionally called the "burn-in" is the **first 36 months** (`t = 0..35`, i.e. 2001-01..2003-12) which are excluded from the training loss via the lower bound `TRAIN_S = 36` in both `calibration_engine.compute_loss` and `fix6.2/run_fix6_2_calibrate.compute_train_loss`. The simulator still steps through these months — only the loss aggregation skips them.

A consequence: the **population is initialised to a snapshot calibrated against SCE moments collected primarily over 2013–2020**, but the simulation begins replaying the macro environment in **2001-01**. This is a known limitation; the 36-month burn-in is the model's only mechanism for absorbing the discrepancy. The paper should disclose this explicitly.

## 3. Window definitions

All windows are half-open intervals `[start_idx, end_idx)`. Identical definitions appear in `fix6.1/run_fix6_1_regime.py` (lines 22–31) and `fix6.2/run_fix6_2_reeval.py` (lines 24–33).

| Window key | Label | Calendar period | `[start_idx, end_idx)` | Months |
|---|---|---|---|---:|
| `train` | Train | 2004-01..2017-12 | [36, 204) | 168 |
| `validation` | Validation | 2018-01..2021-12 | [204, 252) | 48 |
| `original_oos` | Original OOS | 2022-01..2026-02 | [252, 302) | 50 |
| `pre_covid_stable` | Pre-COVID stable | 2018-01..2019-12 | [204, 228) | 24 |
| `covid_crisis_mar` | COVID crisis (Mar 2020 on) | 2020-03..2021-12 | [230, 252) | 22 |
| `covid_crisis_jan` | COVID crisis (Jan 2020 on) | 2020-01..2021-12 | [228, 252) | 24 |
| `post_covid_norm` | Post-COVID normalization | 2022-01..2026-02 | [252, 302) | 50 |
| `full_post_2018` | Full post-2018 | 2018-01..2026-02 | [204, 302) | 98 |

The COVID-crisis window appears in two variants because December reports for UNRATE are revised retroactively; using `2020-03` rather than `2020-01` excludes the two months of pre-pandemic levels but the headline results are reported on the `_mar` variant.

## 4. ABM vs benchmark training window — alignment resolution (P1-24)

| Source | Training window | Calibration target |
|---|---|---|
| ABM (V_Full and all fix6.2/fix6.3 variants) | 2004-01..2017-12 (`[36, 204)`, 168 months) | Tier-1/2/3 weighted RMSE on UR/LFPR/EPOP + transition-rate targets |
| Benchmarks B0a–B8 (fix6.4 dynamic protocol) | 2001-01..fit_end (regime-dependent) | OLS / AR / ARIMA / ETS / VAR / Ridge / Beveridge / DMP — each with their own native objective |

The benchmark `fit_end` is regime-dependent and listed in `fix6.4/run_fix6_4_benchmarks.py` lines 58–63: for `post_covid_norm` it is **index 252 (= 2022-01)**, so each benchmark sees the **full 2001-01..2021-12 history (252 months)**, whereas the ABM sees only **2004-01..2017-12 (168 months)** for its likelihood-style loss.

**Recommended paper wording** (use verbatim in S05_01 and S06_04):

> "Benchmark models are fit on 2001-01 through the month immediately preceding each evaluation window. The ABM is calibrated only on the 2004-01..2017-12 sub-window because the first 36 months are needed as a burn-in for the agent state to align with the SCE-anchored initial distribution. The ABM therefore has access to **84 fewer months of training data** and is **never refit during the validation or out-of-sample periods**. This makes the comparison conservative for the ABM."

No code-level change is recommended: extending the ABM training start to 2001-01 would require removing the burn-in, which currently absorbs the initialisation/observation timing gap (Section 2 above).

## 5. Re-evaluation seeds (P2 item #14)

Confirmed by reading `正式撰写/fix6.2/run_fix6_2_reeval.py` line 21 and the `seeds` field in `reeval_metrics.json` lines 2–8:

- **Calibration**: 3 seeds — `{42, 137, 2024}` (declared in `run_fix6_2_calibrate.py` line 39).
- **Re-evaluation of top-5 candidates**: 5 seeds — `{42, 137, 2024, 888, 1234}` (declared in `run_fix6_2_reeval.py` line 21 and `fix6.1/run_fix6_1_regime.py` line 16).

The first three seeds are shared so that re-evaluation is a strict superset of calibration. Seeds 888 and 1234 are evaluation-only.

## Cross-reference

- Sections using this calendar: **S04_02**, **S05_01**, **S06_01**, **S06_02**, **S06_04**, **S06_05**.
- Every Experiment ID (EX01–EX13) is anchored to the same 302-month grid.
