"""
Reproducibility orchestrator for the ABM paper Section 6 results.

All paths are relative to the repository root; this script must be invoked
from the repository root (i.e. the directory that contains this file).

Stages (declared in STAGES below) are executed in declaration order. Each
stage names a script (run via `python <script>`), declares the input files
it expects to find, and the output files it is expected to produce. Before
running, the orchestrator checks that all declared inputs exist; after
running, it verifies all declared outputs exist.

Usage examples:
  python reproduce.py --list                       # show all stages with status
  python reproduce.py --dry-run --stage all        # plan, no execution
  python reproduce.py --stage paper                # just the paper-ready builders
  python reproduce.py --stage population fix6.2-calibrate fix6.2-reeval build-paper
  python reproduce.py --from-stage fix6.2-calibrate --to-stage build-paper
  python reproduce.py --stage all --skip-existing  # skip stages whose outputs all exist

Runtime budget (single CPU, no GPU): full chain ~10-15 h.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# Some paths in this repository contain CJK characters; force UTF-8 on stdout
# so they survive Windows pipes (the cp1252 default would crash on them).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

ROOT = Path(__file__).resolve().parent


@dataclass
class Stage:
    key: str
    label: str
    script: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    runtime_hint: str = ""


STAGES: list[Stage] = [
    Stage("population", "Phase 2 synthetic population", "Phase2_Code/population_init_engine.py",
          inputs=["Phase2_Output/empirical_distributions.json"],
          outputs=["Phase2_Output/population_v1.npz"],
          runtime_hint="~5 min"),
    Stage("legacy-derived", "Legacy 6.2 derived run (feeds fix6.1)", "正式撰写/6.2/run_6_2_derived.py",
          inputs=["Phase2_Output/population_v1.npz", "Phase3_Output/phase6/candidate_baseline.json"],
          outputs=["正式撰写/6.2/derived_series.npz", "正式撰写/6.2/derived_metrics.json"],
          runtime_hint="~30 min"),
    Stage("legacy-ladder", "Legacy 6.3 Package C heterogeneity ladder", "正式撰写/6.3/run_6_3_packageC_ladder.py",
          inputs=["Phase2_Output/population_v1.npz", "Phase3_Output/phase6/candidate_baseline.json"],
          outputs=["正式撰写/6.3/ladder_series.npz", "正式撰写/6.3/ladder_metrics.json"],
          runtime_hint="~30 min"),
    Stage("legacy-ablation", "Legacy 6.3 Phase 7 mechanism ablation", "正式撰写/6.3/run_6_3_phase7_ablation.py",
          inputs=["Phase2_Output/population_v1.npz", "Phase3_Output/phase6/candidate_baseline.json"],
          outputs=["正式撰写/6.3/ablation_series.npz", "正式撰写/6.3/ablation_metrics.json"],
          runtime_hint="~1 h"),
    Stage("fix6.1", "Regime-specific OOS decomposition (no resim)", "正式撰写/fix6.1/run_fix6_1_regime.py",
          inputs=["正式撰写/6.2/derived_series.npz"],
          outputs=["正式撰写/fix6.1/regime_series.npz", "正式撰写/fix6.1/regime_metrics.json"],
          runtime_hint="~1 min"),
    Stage("fix6.2-calibrate", "fix6.2 recalibration LHS (4 variants)", "正式撰写/fix6.2/run_fix6_2_calibrate.py",
          inputs=["Phase2_Output/population_v1.npz"],
          outputs=["正式撰写/fix6.2/calibration_results.json"],
          runtime_hint="~2.5 h"),
    Stage("fix6.2-reeval", "fix6.2 top-5 x 5-seed re-evaluation", "正式撰写/fix6.2/run_fix6_2_reeval.py",
          inputs=["正式撰写/fix6.2/calibration_results.json"],
          outputs=["正式撰写/fix6.2/reeval_trajectories.npz", "正式撰写/fix6.2/reeval_metrics.json"],
          runtime_hint="~30 min"),
    Stage("fix6.3-calibrate", "fix6.3 recalibration LHS (7 ablation variants)", "正式撰写/fix6.3/run_fix6_3_calibrate.py",
          inputs=["Phase2_Output/population_v1.npz"],
          outputs=["正式撰写/fix6.3/calibration_results.json"],
          runtime_hint="~3 h"),
    Stage("fix6.3-reeval", "fix6.3 top-5 x 5-seed re-evaluation", "正式撰写/fix6.3/run_fix6_3_reeval.py",
          inputs=["正式撰写/fix6.3/calibration_results.json"],
          outputs=["正式撰写/fix6.3/reeval_trajectories.npz", "正式撰写/fix6.3/reeval_metrics.json"],
          runtime_hint="~30 min"),
    Stage("fix6.4", "fix6.4 11 statistical benchmarks", "正式撰写/fix6.4/run_fix6_4_benchmarks.py",
          inputs=[],
          outputs=["正式撰写/fix6.4/benchmark_series.npz", "正式撰写/fix6.4/benchmark_metrics.json"],
          runtime_hint="~30 min"),
    Stage("build-fix6.1", "Build fix6.1 tables & figures", "正式撰写/fix6.1/build_fix6_1_artifacts.py",
          inputs=["正式撰写/fix6.1/regime_metrics.json"], outputs=[], runtime_hint="<1 min"),
    Stage("build-fix6.2", "Build fix6.2 tables & figures", "正式撰写/fix6.2/build_fix6_2_artifacts.py",
          inputs=["正式撰写/fix6.2/reeval_metrics.json"], outputs=[], runtime_hint="<1 min"),
    Stage("build-fix6.3", "Build fix6.3 tables & figures", "正式撰写/fix6.3/build_fix6_3_artifacts.py",
          inputs=["正式撰写/fix6.3/reeval_metrics.json"], outputs=[], runtime_hint="<1 min"),
    Stage("build-fix6.4", "Build fix6.4 tables & figures", "正式撰写/fix6.4/build_fix6_4_artifacts.py",
          inputs=["正式撰写/fix6.4/benchmark_metrics.json", "正式撰写/fix6.2/reeval_metrics.json"],
          outputs=[], runtime_hint="<1 min"),
    Stage("build-fix6.5", "Synthesize fix6.5 robustness tables", "正式撰写/fix6.5/build_fix6_5_artifacts.py",
          inputs=["正式撰写/fix6.1/tables/table1_regime_summary.csv"], outputs=[], runtime_hint="<1 min"),
    Stage("build-paper-tables", "Paper-ready Section 6 tables", "撰写版本2/实验结果/_scripts/build_tables.py",
          inputs=["正式撰写/fix6.2/reeval_metrics.json", "正式撰写/6.5/robustness_metrics.json"],
          outputs=[], runtime_hint="<1 min"),
    Stage("build-paper-figures", "Paper-ready Section 6 main-text figures", "撰写版本2/实验结果/_scripts/build_figures.py",
          inputs=["正式撰写/fix6.2/reeval_trajectories.npz", "正式撰写/6.5/robustness_metrics.json"],
          outputs=[], runtime_hint="<1 min"),
    Stage("build-paper-audit", "Paper-ready audit figures", "撰写版本2/实验结果/_scripts/build_audit_figures.py",
          inputs=["Phase2_Output/population_v1.npz", "正式撰写/fix6.2/reeval_trajectories.npz",
                  "正式撰写/6.3/ladder_series.npz", "正式撰写/fix6.4/benchmark_series.npz"],
          outputs=[], runtime_hint="<1 min"),
]

# Convenience group aliases
GROUPS = {
    "all":     [s.key for s in STAGES],
    "paper":   ["build-paper-tables", "build-paper-figures", "build-paper-audit"],
    "build":   [s.key for s in STAGES if s.key.startswith("build-")],
    "fix6.2":  ["fix6.2-calibrate", "fix6.2-reeval"],
    "fix6.3":  ["fix6.3-calibrate", "fix6.3-reeval"],
    "legacy":  ["legacy-derived", "legacy-ladder", "legacy-ablation"],
}



def stage_status(s: Stage) -> str:
    missing_in = [p for p in s.inputs if not (ROOT / p).exists()]
    have_out = [p for p in s.outputs if (ROOT / p).exists()]
    if s.outputs and len(have_out) == len(s.outputs):
        return "DONE"
    if missing_in:
        return "BLOCKED"
    return "READY"


def list_stages() -> None:
    print(f"{'KEY':<22} {'STATUS':<8} {'RUNTIME':<10} {'LABEL'}")
    print("-" * 88)
    for s in STAGES:
        print(f"{s.key:<22} {stage_status(s):<8} {s.runtime_hint:<10} {s.label}")


def resolve_selection(args: argparse.Namespace) -> list[Stage]:
    keys = list(args.stage or [])
    expanded: list[str] = []
    for k in keys:
        if k in GROUPS:
            expanded.extend(GROUPS[k])
        else:
            expanded.append(k)
    if args.from_stage or args.to_stage:
        all_keys = [s.key for s in STAGES]
        i0 = all_keys.index(args.from_stage) if args.from_stage else 0
        i1 = all_keys.index(args.to_stage) + 1 if args.to_stage else len(all_keys)
        expanded.extend(all_keys[i0:i1])
    if not expanded:
        return []
    by_key = {s.key: s for s in STAGES}
    unknown = [k for k in expanded if k not in by_key]
    if unknown:
        sys.exit(f"Unknown stage(s): {unknown}. Use --list to see valid keys.")
    seen, ordered = set(), []
    for s in STAGES:
        if s.key in expanded and s.key not in seen:
            ordered.append(s); seen.add(s.key)
    return ordered


def run_stage(s: Stage, dry_run: bool, skip_existing: bool) -> bool:
    print(f"\n[{s.key}] {s.label}  ({s.runtime_hint})")
    if skip_existing and stage_status(s) == "DONE":
        print(f"  -> SKIP (all outputs present)")
        return True
    missing = [p for p in s.inputs if not (ROOT / p).exists()]
    if missing:
        print(f"  -> BLOCKED. Missing inputs:")
        for p in missing:
            print(f"       {p}")
        return False
    cmd = [sys.executable, s.script]
    print(f"  $ {' '.join(cmd)}")
    if dry_run:
        return True
    t0 = time.time()
    rc = subprocess.run(cmd, cwd=str(ROOT)).returncode
    dt = time.time() - t0
    if rc != 0:
        print(f"  -> FAILED (exit {rc}) after {dt/60:.1f} min")
        return False
    missing_out = [p for p in s.outputs if not (ROOT / p).exists()]
    if missing_out:
        print(f"  -> WARN: stage exited cleanly but expected outputs missing:")
        for p in missing_out:
            print(f"       {p}")
    print(f"  -> OK in {dt/60:.1f} min")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true", help="list all stages and exit")
    ap.add_argument("--dry-run", action="store_true", help="print plan, do not execute")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip stages whose declared outputs all already exist")
    ap.add_argument("--from-stage", help="start at this stage (inclusive)")
    ap.add_argument("--to-stage", help="end at this stage (inclusive)")
    ap.add_argument("--stage", nargs="+", help=f"stage key(s) or group name(s): {sorted(GROUPS)}")
    args = ap.parse_args()
    if args.list:
        list_stages(); return 0
    selection = resolve_selection(args)
    if not selection:
        ap.print_help(); return 1
    print(f"Plan: {len(selection)} stage(s)")
    for s in selection:
        print(f"  - {s.key}  ({s.runtime_hint})  status={stage_status(s)}")
    ok = True
    for s in selection:
        if not run_stage(s, args.dry_run, args.skip_existing):
            ok = False
            print(f"\nStopping at {s.key}. Fix the cause and re-run with --from-stage {s.key}.")
            break
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
