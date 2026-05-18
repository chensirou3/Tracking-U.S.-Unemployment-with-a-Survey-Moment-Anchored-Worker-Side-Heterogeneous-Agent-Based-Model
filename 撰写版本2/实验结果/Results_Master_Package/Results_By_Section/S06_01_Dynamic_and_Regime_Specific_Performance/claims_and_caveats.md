# S06_01 — Claims and Caveats

Claims contributed to §6.1 (numbering follows the central `Results_Claim_to_Evidence_Table.csv`).

- **C01** — Full model tracks recent monthly unemployment with sub-pp RMSE on the post-COVID window.
- **C02** — Model performance varies materially across evaluation windows.
- **C03** — The post-COVID window is the headline tracking window of the paper.
- **C13** — Results are stable across evaluation seeds.
- **C20** — The model does not claim universal accuracy across regimes.

## Caveats

See the *Caveats and wording rules* block of `S06_01_Report.md` for the full list. Key reminders:

- All decompositions and deltas in this section are within-experiment accounting, not causal partitions.
- Errors are reported in percentage points (pp); correlations in decimal; shares with explicit unit labels.
- Parameter values are fitted simulation quantities reported as bands.
- Manuscript must use the approved phrasings from `Results_Wording_Bank.md` and avoid the banned ones.