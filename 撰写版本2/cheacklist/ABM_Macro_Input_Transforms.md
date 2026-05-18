# ABM Macro Input Transformations

**Resolves P1 item #18 (macro-input transformation table).**

Source of truth: `Phase3_Code/environment_real.py` (class `RealEnvironment`), commit on disk at the time of this report. All transformations are applied once at simulation start; no rolling or in-loop transformations are used.

## Driver inputs (enter the simulation each month)

The simulation reads these four scalars at every step via `RealEnvironment.get(t)`:

| Driver name (in model) | Source FRED series | Raw units | Transformation | Clip range | Default if missing |
|---|---|---|---|---|---|
| `market_tightness` | JTSJOR (Job Openings Rate) | percent | divide by 3.0 (centres on 1.0 at JOR≈3) | [0.30, 3.00] | 3.0 (i.e. transformed = 1.0) |
| `separation_rate` | JTSLDR (Layoffs/Discharges Rate) | percent | divide by 100 (to decimal) | [0.005, 0.050] | 1.2 (i.e. transformed = 0.012) |
| `income_growth_bg` | CES0500000003_PC1 (Avg Hourly Earnings, YoY % change) | percent | divide by 100, then divide by 12 (monthly rate) | [-0.01, 0.02] | 3.0 (i.e. transformed ≈ 0.0025) |
| `borrowing_rate` | FEDFUNDS (Effective Fed Funds Rate) | percent | add fixed spread 2.0, then divide by 100 | [0.02, 0.15] | 2.0 (i.e. transformed = 0.04) |

The lookup is by exact `YYYY-MM` calendar key; values for months where the series did not yet exist (e.g. JTSJOR before 2000-12) fall back to the default rather than the previous observation. No interpolation or smoothing is applied.

## Calibration targets (loss targets only — not simulation inputs)

These are loaded by `Phase3_Code/calibration_engine.py` and used to form the multi-target loss; they do **not** feed the agents' decisions.

| Target | FRED series | Raw units | Transformation | Notes |
|---|---|---|---|---|
| `target_ur` | UNRATE | percent | divide by 100 (to decimal) | Used in Tier-1 weighted RMSE term |
| `target_lfpr` | CIVPART | percent | divide by 100 (to decimal) | Used in Tier-2 weighted RMSE term |
| `target_epop` | EMRATIO | percent | divide by 100 (to decimal) | Used in Tier-2 weighted RMSE term |

NaN months (missing observations within the published range) are masked out of the RMSE sum at evaluation time; the mask is recomputed per window in `fix6.1/run_fix6_1_regime.py` (`_metric_block`).

## What is NOT transformed

- No lagged inputs. Every driver is contemporaneous (month-`t` raw observation → month-`t` decision).
- No HP/Hamilton filtering, no demeaning, no z-scoring.
- The fixed 2.0 percentage-point spread on FEDFUNDS is the only ad-hoc shift; it represents an approximate prime/lending premium over the policy rate. This is documented in the comment header of `environment_real.py`.

## Reproducibility note

The clip ranges above are **enforced after** lookup, so calibration runs that hit the clip boundary register the clip value rather than the raw observation. This is most relevant during 2020-04 (JTSJOR raw value brought down sharply) and 2022 (borrowing_rate before clipping would briefly exceed the upper bound when FEDFUNDS rises rapidly).

## Cross-reference

- Section using this table: **S04_01** (Data) and **S05_01** (Model — Environment).
- Experiment IDs depending on this: **EX01–EX13** (every simulation run uses this driver set).
