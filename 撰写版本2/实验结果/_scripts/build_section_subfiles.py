"""Generate the per-section sub-files required by §4.2 of the prompt:
wording_bank.md / claims_and_caveats.md / source_experiments.md.

Each is a concise excerpt; the full content lives in the central
Results_Wording_Bank.md, Results_Claim_to_Evidence_Table.csv, and the
per-experiment E##_Report.md files.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Results_Master_Package" / "Results_By_Section"

SECTIONS = {
    "S06_01": dict(
        folder="S06_01_Dynamic_and_Regime_Specific_Performance",
        title="Dynamic and Regime-Specific Performance",
        experiments=[
            ("E4", "Dynamic Evaluation", "fix6.2/run_fix6_2_reeval.py + reeval_metrics.json", "5-seed mean post-COVID UR RMSE 0.273 pp"),
            ("E5", "Regime-Specific Evaluation", "fix6.1/run_fix6_1_regime.py + regime_metrics.json", "Per-regime UR/LFPR/EPOP metrics over 4 windows"),
        ],
        claims=["C01", "C02", "C03", "C13", "C20"],
        wording_section="1. Headline tracking",
    ),
    "S06_02": dict(
        folder="S06_02_Internal_Controls_and_Source_of_Advantage",
        title="Internal Controls and Source of Advantage",
        experiments=[
            ("E6", "Internal Control Comparison", "fix6.2/run_fix6_2_calibrate.py + run_fix6_2_reeval.py", "V_Full vs V_Homogeneous / V_LaborOnly / V_Simplified — separately recalibrated"),
            ("E7", "Source-of-Advantage Decomposition", "fix6.2/tables/table4_source_of_advantage.csv", "94 / 6 split of the 0.289 pp total gain"),
        ],
        claims=["C04", "C05", "C06"],
        wording_section="2. Internal controls",
    ),
    "S06_03": dict(
        folder="S06_03_Recalibrated_Heterogeneity_Ablations",
        title="Recalibrated Heterogeneity Ablations",
        experiments=[
            ("E8", "Heterogeneity Ablation", "fix6.3/run_fix6_3_calibrate.py + reeval", "6 recalibrated ablations vs V_Full"),
            ("E9", "Heterogeneity Ladder", "6.3/run_6_3_packageC_ladder.py + ladder_metrics.json", "L0..L6 marginal-gain ladder"),
        ],
        claims=["C07", "C08", "C09"],
        wording_section="3. Heterogeneity ablations and ladder",
    ),
    "S06_04": dict(
        folder="S06_04_Forecast_Benchmark_Comparison",
        title="Forecast Benchmark Comparison",
        experiments=[
            ("E10", "Forecast Benchmark Comparison", "fix6.4/run_fix6_4_benchmarks.py + benchmark_metrics.json", "ABM rank 1 of 12 on post-COVID; margin 0.036 pp"),
        ],
        claims=["C10", "C11", "C12"],
        wording_section="4. Benchmark comparison",
    ),
    "S06_05": dict(
        folder="S06_05_Robustness_and_Sensitivity",
        title="Robustness and Sensitivity",
        experiments=[
            ("E11", "Training-Window Sensitivity", "包A_训练窗口敏感性/run_packageA.py (archived in 6.5 pipeline) + 6.5/tables/table2_training_window.csv", "10 splits; mean 0.245 ± 0.011 pp"),
            ("E12", "Forecast-Horizon and Agent-Count Sensitivity", "包B/包D (archived in 6.5 pipeline) + 6.5/tables/table3_horizon.csv, table4_agent_count.csv", "Slope −0.09; plateau at N ≥ 50k"),
            ("E13", "Calibration-Method and Parameter-ID Sensitivity", "包E_校准方法敏感性/run_packageE.py + 6.5/robustness_metrics.json", "Best-test band 0.214–0.243 pp; CV 5.55%; 10/14 params weakly identified"),
        ],
        claims=["C14", "C15", "C16", "C17", "C18"],
        wording_section="5. Robustness",
    ),
}

# Quick claim summary (mirrors Results_Claim_to_Evidence_Table.csv)
CLAIMS = {
    "C01": "Full model tracks recent monthly unemployment with sub-pp RMSE on the post-COVID window.",
    "C02": "Model performance varies materially across evaluation windows.",
    "C03": "The post-COVID window is the headline tracking window of the paper.",
    "C04": "Full model improves over separately calibrated internal controls.",
    "C05": "The heterogeneity advantage is moderate, not overwhelming.",
    "C06": "The source-of-advantage decomposition is an accounting identity, not a causal partition.",
    "C07": "Search-friction heterogeneity is the least substitutable channel.",
    "C08": "Liquidity and housing dimensions are largely substitutable after recalibration.",
    "C09": "The heterogeneity ladder confirms incremental marginal value of adding dimensions.",
    "C10": "ABM is competitive with external benchmarks under the same dynamic protocol.",
    "C11": "ABM advantage over the best simple benchmarks is modest.",
    "C12": "Rolling one-step benchmarks are reported as a diagnostic, not as the headline comparison.",
    "C13": "Results are stable across evaluation seeds.",
    "C14": "Results are not driven by one training window.",
    "C15": "Results are not driven by agent count.",
    "C16": "Results are not driven by one calibration method.",
    "C17": "Many free parameters are weakly identified.",
    "C18": "Parameter values are fitted simulation quantities, not structural estimates.",
    "C20": "The model does not claim universal accuracy across regimes.",
}


def write_source_experiments(sid: str, spec: dict) -> None:
    out = ROOT / spec["folder"] / "source_experiments.md"
    lines = [f"# {sid} — Source Experiments", "",
             f"Manuscript section §6.{sid[-1]} draws on the following experiments. Full audit trails live in `Results_By_Experiment/`.", ""]
    lines.append("| Paper ID | Experiment | Source | Role in this section |")
    lines.append("|---|---|---|---|")
    for eid, name, src, role in spec["experiments"]:
        lines.append(f"| {eid} | {name} | `{src}` | {role} |")
    lines.append("")
    lines.append("See each experiment's `E##_Report.md` for the full protocol, key numbers, and caveats.")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] {sid} source_experiments.md")


def write_claims_and_caveats(sid: str, spec: dict) -> None:
    out = ROOT / spec["folder"] / "claims_and_caveats.md"
    lines = [f"# {sid} — Claims and Caveats", "",
             f"Claims contributed to §6.{sid[-1]} (numbering follows the central `Results_Claim_to_Evidence_Table.csv`).", ""]
    for cid in spec["claims"]:
        lines.append(f"- **{cid}** — {CLAIMS[cid]}")
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append(f"See the *Caveats and wording rules* block of `{sid}_Report.md` for the full list. Key reminders:")
    lines.append("")
    lines.append("- All decompositions and deltas in this section are within-experiment accounting, not causal partitions.")
    lines.append("- Errors are reported in percentage points (pp); correlations in decimal; shares with explicit unit labels.")
    lines.append("- Parameter values are fitted simulation quantities reported as bands.")
    lines.append("- Manuscript must use the approved phrasings from `Results_Wording_Bank.md` and avoid the banned ones.")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] {sid} claims_and_caveats.md")


def write_wording_bank(sid: str, spec: dict) -> None:
    out = ROOT / spec["folder"] / "wording_bank.md"
    lines = [f"# {sid} — Wording Bank", "",
             f"Paper-ready phrasings for §6.{sid[-1]}. This file is an excerpt from the central `Results_Wording_Bank.md` (§{spec['wording_section']}); update only the central file.", "",
             f"## Drop-in wording", "",
             f"See `{sid}_Report.md` → *Manuscript-facing wording (drop-in)* block. The phrasings are reproduced from `Results_Wording_Bank.md` §{spec['wording_section']}.", "",
             "## Approved phrasings (applicable here)", "",
             "- \"Tracks observed U.S. unemployment\"",
             "- \"Survey-moment-anchored\"",
             "- \"Within-experiment accounting decomposition\"",
             "- \"Competitive at the top of the comparison set\" (S06_04 only)",
             "- \"Weakly identified\" / \"reported as bands\" (S06_05 only)",
             "- \"Diagnostic\", \"accounting delta\", \"accounting share\"",
             "",
             "## Banned phrasings (enforced)", "",
             "- \"Dominates\" / \"outperforms decisively\"",
             "- \"Causal\" / \"causal decomposition\"",
             "- \"Structurally identifies\" / \"structurally estimated\"",
             "- \"Completely tracks\" / \"completely untouched\"",
             "- Over-emphasising COVID",
             "- Internal-workflow language (\"audit\", \"P1 report\", \"revised\", \"rerun\")",
             ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] {sid} wording_bank.md")


def main() -> None:
    for sid, spec in SECTIONS.items():
        (ROOT / spec["folder"]).mkdir(parents=True, exist_ok=True)
        write_source_experiments(sid, spec)
        write_claims_and_caveats(sid, spec)
        write_wording_bank(sid, spec)


if __name__ == "__main__":
    main()
