# E9 — Heterogeneity Ladder (PATCHED)

**Status:** APPENDIX / SUPPORTING DIAGNOSTIC ONLY.
**Patch scope:** Corrects three errors in the original `E09_Report.md`:
1. Key Numbers claimed `L6 = 0.27 pp matches V_Full`; the actual L6 is 0.2211 pp and belongs to the **legacy baseline family**, not the recalibrated V_Full family (0.2731 pp).
2. Key Numbers claimed the L4→L5 (adding housing) drop is `≈ −0.07 pp`; the actual drop is **−0.2487 pp** (0.5172 → 0.2685) and is the largest single drop in the ladder.
3. Insertion order in `## Protocol` is listed incorrectly; the actual order implied by `tables/E09_T01` is **labor_fragility → search → income_expect → liquidity → housing → consumption_rule**.

This PATCHED file supersedes the corresponding sections of `Results_By_Experiment/E09_Heterogeneity_Ladder/E09_Report.md` for manuscript-facing use. Source data in `tables/E09_T01_Heterogeneity_Ladder_v01.csv` is unchanged.

---

## Purpose

Build the heterogeneity ladder L0..L6 by incrementally adding heterogeneity dimensions; each level is separately recalibrated. Provides marginal-gain evidence complementing E8 (which asks "what is lost when a dimension is removed from V_Full?"); the ladder asks "what is gained per dimension added to a zero-heterogeneity baseline?".

## Source Files

| Asset | Path | Role |
|---|---|---|
| Ladder runner | `正式撰写/6.3/run_6_3_packageC_ladder.py` | L0..L6 + Layer ladders G2, G3 (LHS 30 × 3 calibration seeds per level) |
| Ladder metrics | `正式撰写/6.3/ladder_metrics.json` | Per-level per-seed train/val/oos metrics |
| Ladder summary table | `Results_By_Experiment/E09_Heterogeneity_Ladder/tables/E09_T01_Heterogeneity_Ladder_v01.csv` | Per-level RMSE and seed SD |
| Trajectories | `正式撰写/6.3/ladder_series.npz` | Per-level 5-seed UR / LFPR / EPOP |

## Protocol (corrected)

1. Seven Core ladder levels L0 (no heterogeneity) through L6 (all six dimensions).
2. **Corrected insertion order:** `labor_fragility (L1) → search (L2) → income_expect (L3) → liquidity (L4) → housing (L5) → consumption_rule (L6)`.
3. At each level, recalibrate by LHS 30 draws × 3 calibration seeds; pick the best by train loss.
4. Re-evaluate the best candidate on 5 final seeds {42, 137, 888, 1234, 2024}; compute UR / LFPR / EPOP RMSE on the main recent evaluation window (2022-01..2026-02; 49 valid months).
5. Two Layer ladders (G2, G3) are reported as insertion-order sensitivity checks.

## Main Outputs

- `tables/E09_T01_Heterogeneity_Ladder_v01.csv` — per-level RMSE table
- `figures/E09_F01_Ladder_RMSE_Path_v01.png` — marginal-gain step plot L0..L6
- `figures/E09_F02_Per_Level_UR_Trajectory_v01.png` — per-level mean UR trajectory overlay (L0..L6) against observed UNRATE on the main recent evaluation window

## Key Numbers (CORRECTED)

| Quantity | Correct value | Required interpretation |
|---|---|---|
| L0 UR RMSE | 0.5527 pp | No heterogeneity; baseline ladder level |
| L1 UR RMSE (add labor_fragility) | 0.5503 pp | Change from L0 is −0.0024 pp, within seed SD |
| L2 UR RMSE (add search) | 1.0545 pp | Worsens substantially vs L1 |
| L3 UR RMSE (add income_expect) | 1.0579 pp | Stays worse than L0/L1 |
| L4 UR RMSE (add liquidity) | 0.5172 pp | Improves back to near-L0 level |
| L5 UR RMSE (add housing) | 0.2685 pp | **Largest single drop in the ladder** |
| L6 UR RMSE (add consumption_rule) | 0.2211 pp | Endpoint of the **legacy baseline family** |
| L4 → L5 step (adding housing) | **−0.2487 pp** | Largest single drop; not −0.07 pp |
| L0 → L1 step | −0.0024 pp | Within 0.023 pp seed SD; effectively zero |
| Ladder monotonicity | **Non-monotonic** | L2 and L3 are ~0.5 pp worse than L0 / L1 |
| Comparability of L6 to recalibrated V_Full | **Not directly comparable** | L6 belongs to the legacy baseline family (M0-class calibration); V_Full = 0.2731 pp is the separately recalibrated headline family |

## Required Caveat Text (paste verbatim into appendix prose)

> The heterogeneity ladder is computed on the legacy baseline family. Its endpoint L6 has UR RMSE 0.2211 pp and is comparable to the E5 dynamic-regime diagnostic, not to the recalibrated V_Full headline result of 0.2731 pp. The ladder is therefore a within-family marginal-gain diagnostic, not a recalibrated source-of-advantage decomposition. The ladder is also non-monotonic: adding the search and income-expectation dimensions on top of labor-fragility raises UR RMSE by approximately 0.5 pp before liquidity and housing restore tracking. The marginal gains are insertion-order-dependent and Layer ladders G2 and G3 are reported as sensitivity checks.

## Use in Manuscript

- §6.3 (S06_03) **supplementary appendix** ladder evidence only.
- **Do not** use any ladder level as a headline number in the main text.
- When the ladder is cited in prose, the caveat text above (or an equivalent paraphrase) must accompany the citation.

## Caveats (combined)

- Insertion order is fixed and marginal gains are order-dependent. Manuscript reports the gains as one specific accounting path, not as a unique decomposition.
- Each level is independently recalibrated within the legacy baseline protocol; differences are partly absorbed by parameter refitting.
- Several adjacent-level differences are smaller than the 0.023 pp seed SD; only L0/L6 and the L4→L5 (housing) step are well-separated.
- L6 is **not** the same as recalibrated V_Full. Conflating them would import the legacy 0.221 pp number into a main-text claim that requires 0.273 pp.

## Status

READY — APPENDIX ONLY.
