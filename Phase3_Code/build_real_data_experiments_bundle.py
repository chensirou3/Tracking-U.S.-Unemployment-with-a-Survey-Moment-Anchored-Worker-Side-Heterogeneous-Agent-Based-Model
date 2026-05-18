"""Build real_data_experiments/ bundle.

For each of the 13 real-data experiments, create a sub-folder containing
(a) every raw result file (md/csv/png/json/npz/...) copied verbatim via
shutil.copy2 (timestamps preserved) and (b) one merged `_merged.md`
collecting all markdown content in reading order with source headers.

Originals are NOT modified, moved or renamed. Only read + copy.
"""
from __future__ import annotations
import csv
import datetime as dt
import os
import shutil
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'real_data_experiments')

# Shared spec files that accompany several sub-experiments.
PHASE7_SHARED = [
    'Phase3_Output/phase7/real_data_input_registry.md',
    'Phase3_Output/phase7/time_alignment_spec.md',
    'Phase3_Output/phase7/target_system.md',
    'Phase3_Output/phase7/candidate_versions.md',
    'Phase3_Output/phase7/Phase7_Summary.md',
]
PHASE8_SHARED_FULL = [
    'Phase3_Output/phase8/comparison_architecture.md',
    'Phase3_Output/phase8/derived_control_specs.md',
    'Phase3_Output/phase8/external_benchmark_specs.md',
    'Phase3_Output/phase8/unified_evaluation_framework.md',
    'Phase3_Output/phase8/Phase8_Summary.md',
]
PHASE8_SHARED_CORE = [
    'Phase3_Output/phase8/comparison_architecture.md',
    'Phase3_Output/phase8/unified_evaluation_framework.md',
    'Phase3_Output/phase8/Phase8_Summary.md',
]

EXPERIMENTS: List[Tuple[str, str, List[str]]] = [
    ('01_phase2_population_init',
     'Phase 2 — SCE-based population initialization (100k agents, 6 MVP dims)',
     ['Phase2_Output/' + n for n in [
         '01_Population_Backbone_Spec.md', '02_Dimension_Init_Specs.md',
         '03_Joint_Structure_Spec.md', '04_Population_Diagnostic_Report.md',
         '05_Population_Sensitivity_Report.md', '06_Stage3_Input_Spec.md',
         'core_distributions.json', 'empirical_distributions.json',
         'lm_distributions.json', 'matrix_schema_map.json',
         'spending_distributions.json', 'population_v1.npz']]),
    ('02_phase3_first_stable_run',
     'Phase 3 — First stable run driven by FRED real environment paths',
     ['Phase3_Output/' + n for n in [
         '01_Environment_Spec.md', '02_Simulation_Order_Spec.md',
         '03_State_Transition_Map.md', '04_First_Stable_Run_Summary.md',
         'output_schema.json', 'run_baseline.npz', 'run_recession.npz',
         'run_real_history.npz', 'agent_decision_data.npz',
         'ablation_results.json',
         'figures/first_stable_run.png',
         'figures/household_indicators.png',
         'figures/prediction_evaluation.png',
         'figures/real_history_run.png']]),
    ('03_phase6_calibration',
     'Phase 6 — 14-param LHS calibration against FRED/BLS targets',
     ['Phase3_Output/phase6/' + n for n in [
         'calibration_comparison.png', 'calibration_results.json',
         'candidate_aggressive.json', 'candidate_baseline.json',
         'candidate_conservative.json']]),
    ('04_phase7_main_run',
     'Phase 7 — Main Run: 3 versions × 5 seeds on 50-month real OOS',
     PHASE7_SHARED + ['Phase3_Output/phase7/' + n for n in [
         'main_run_metrics.json', 'main_run_series.npz',
         'fig1_ur_comparison.png', 'fig2_auxiliary_targets.png',
         'claim_update.md']]),
    ('05_phase7_ablation',
     'Phase 7 — Heterogeneity-flattening ablation (7 dims × 3 seeds)',
     PHASE7_SHARED + ['Phase3_Output/phase7/' + n for n in [
         'ablation_results.json', 'fig3_ablation.png']]),
    ('06_phase7_robustness',
     'Phase 7 — Robustness checks R1-R4 (seeds / init / weights / informal)',
     PHASE7_SHARED + ['Phase3_Output/phase7/' + n for n in [
         'robustness_results.json', 'fig4_robustness.png']]),
    ('07_phase8_benchmark_comparison',
     'Phase 8 — 8-model unified comparison (M0 + D1/D2/D3 + B1/B2/B3/B4)',
     PHASE8_SHARED_FULL + ['Phase3_Output/phase8/' + n for n in [
         'benchmark_results.json', 'derived_results.json',
         'derived_series.npz', 'comparison_results.csv',
         'fig1_unified_comparison.png', 'fig2_rmse_bars.png',
         'paper_ready_comparison_package.md']]),
    ('08_phase8_source_of_advantage',
     'Phase 8 — Source-of-Advantage decomposition (heterogeneity=96%)',
     PHASE8_SHARED_CORE + ['Phase3_Output/phase8/' + n for n in [
         'source_of_advantage.json', 'source_of_advantage_report.md',
         'incremental_contribution.json', 'fig3_source_of_advantage.png',
         'fig4_positioning_map.png', 'model_positioning_update.md']]),
    ('09_packageA_training_window',
     'Package A — Training-window sensitivity (10 splits × 8 models × 3 seeds)',
     None),  # sentinel: copy all of Phase3_Output/packageA/
    ('10_packageB_forecast_horizon',
     'Package B — Forecast-horizon degradation (6 horizons × 8 models × 49 origins)',
     None),
    ('11_packageC_heterogeneity_ladder',
     'Package C — Heterogeneity ladder L0-L6 (244 sims, projection + refit)',
     None),
    ('12_packageD_agent_count',
     'Package D — Agent-count sensitivity (7 sizes × 4 models × 10 seeds × 2 modes = 560 sims)',
     None),
    ('13_packageE_calibration_method',
     'Package E — Calibration-method sensitivity (5 methods × 3030 sims total)',
     None),
]

PACKAGE_DIRS = {
    '09_packageA_training_window': 'Phase3_Output/packageA',
    '10_packageB_forecast_horizon': 'Phase3_Output/packageB',
    '11_packageC_heterogeneity_ladder': 'Phase3_Output/packageC',
    '12_packageD_agent_count': 'Phase3_Output/packageD',
    '13_packageE_calibration_method': 'Phase3_Output/packageE',
}


def gather_package_files(pkg_rel_dir: str) -> List[str]:
    abs_dir = os.path.join(ROOT, pkg_rel_dir)
    out: List[str] = []
    for dirpath, _, filenames in os.walk(abs_dir):
        for fn in sorted(filenames):
            abs_fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_fp, ROOT).replace('\\', '/')
            out.append(rel)
    return out


def flatten_dest(rel_src: str, pkg_root):
    if pkg_root and rel_src.startswith(pkg_root + '/'):
        return rel_src[len(pkg_root) + 1:]
    return os.path.basename(rel_src)


def copy_files(files, dest_dir, pkg_root=None):
    os.makedirs(dest_dir, exist_ok=True)
    rows = []
    for rel in files:
        abs_src = os.path.join(ROOT, rel)
        if not os.path.exists(abs_src):
            print(f'  [MISSING] {rel}')
            continue
        rel_dest = flatten_dest(rel, pkg_root)
        abs_dest = os.path.join(dest_dir, rel_dest)
        os.makedirs(os.path.dirname(abs_dest) or dest_dir, exist_ok=True)
        shutil.copy2(abs_src, abs_dest)
        rows.append((rel, rel_dest, os.path.getsize(abs_src)))
    return rows


def merge_markdowns(rows, dest_dir, exp_id, exp_title):
    md_rows = [r for r in rows if r[0].lower().endswith('.md')]
    if not md_rows:
        return None
    out_path = os.path.join(dest_dir, f'{exp_id}_merged.md')
    ts = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(out_path, 'w', encoding='utf-8') as w:
        w.write(f'# {exp_id} - merged markdown\n\n')
        w.write(f'> {exp_title}\n>\n')
        w.write(f'> Built {ts}. {len(md_rows)} source .md file(s) merged '
                'verbatim in reading order. Originals untouched.\n\n')
        w.write('## Contents\n\n')
        for i, (src, _, _) in enumerate(md_rows, 1):
            w.write(f'{i}. `{src}`\n')
        w.write('\n---\n')
        for src, _, size in md_rows:
            abs_src = os.path.join(ROOT, src)
            mtime = dt.datetime.fromtimestamp(os.path.getmtime(abs_src))
            w.write('\n\n<!-- =================================================== -->\n')
            w.write(f'# Source: `{src}`\n')
            w.write(f'> size: {size:,} bytes | mtime: {mtime:%Y-%m-%d %H:%M}\n\n')
            with open(abs_src, 'r', encoding='utf-8', errors='replace') as r:
                w.write(r.read().rstrip())
            w.write('\n')
    return out_path


def write_inventory(rows, dest_dir, exp_id):
    path = os.path.join(dest_dir, f'{exp_id}_inventory.csv')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['source_path', 'dest_path', 'ext', 'bytes'])
        for src, dst, size in rows:
            ext = os.path.splitext(src)[1].lower()
            wr.writerow([src, dst, ext, size])


def write_top_manifest(manifest, total_files, total_bytes):
    os.makedirs(os.path.join(DEST, '00_manifest'), exist_ok=True)
    csv_path = os.path.join(DEST, '00_manifest', 'experiment_manifest.csv')
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['exp_id', 'title', 'file_count', 'md_count',
                     'merged_md', 'ext_counts'])
        for m in manifest:
            wr.writerow([m['exp_id'], m['title'], m['file_count'],
                         m['md_count'], m['merged_md'],
                         '; '.join(f"{k}={v}" for k, v in
                                   sorted(m['ext_counts'].items()))])
    md_path = os.path.join(DEST, '00_manifest', 'README.md')
    ts = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# real_data_experiments - Index\n\n')
        f.write(f'> Built {ts}. 13 experiments that consumed real FRED/BLS '
                'and/or SCE data. Originals in the repo are NOT modified.\n\n')
        f.write(f'**Total**: {total_files} files, '
                f'{total_bytes / 1024 / 1024:.1f} MB.\n\n')
        f.write('| # | Experiment | Files | md | Merged doc |\n')
        f.write('|---|------------|------:|---:|-----------|\n')
        for i, m in enumerate(manifest, 1):
            merged = f'`{m["merged_md"]}`' if m['merged_md'] else '-'
            f.write(f'| {i} | **{m["exp_id"]}** - {m["title"]} | '
                    f'{m["file_count"]} | {m["md_count"]} | {merged} |\n')
        f.write('\n## File-type layout (per experiment)\n\n')
        f.write('| Experiment | md | csv | png | json | npz | other |\n')
        f.write('|-----------|---:|----:|----:|-----:|----:|------:|\n')
        keys = ('.md', '.csv', '.png', '.json', '.npz')
        for m in manifest:
            ec = m['ext_counts']
            other = sum(v for k, v in ec.items() if k not in keys)
            f.write('| {exp} | {md} | {csv} | {png} | {json} | {npz} | {oth} |\n'
                    .format(exp=m['exp_id'],
                            md=ec.get('.md', 0), csv=ec.get('.csv', 0),
                            png=ec.get('.png', 0), json=ec.get('.json', 0),
                            npz=ec.get('.npz', 0), oth=other))
    print(f'Wrote manifest: {csv_path}')
    print(f'Wrote README:   {md_path}')


def main():
    os.makedirs(DEST, exist_ok=True)
    manifest = []
    total_files = 0
    total_bytes = 0
    for exp_id, exp_title, files in EXPERIMENTS:
        dest_dir = os.path.join(DEST, exp_id)
        pkg_root = None
        if files is None:
            pkg_root = PACKAGE_DIRS[exp_id]
            files = gather_package_files(pkg_root)
        rows = copy_files(files, dest_dir, pkg_root)
        merged = merge_markdowns(rows, dest_dir, exp_id, exp_title)
        write_inventory(rows, dest_dir, exp_id)
        ext_counts = {}
        for src, _, size in rows:
            e = os.path.splitext(src)[1].lower() or '(none)'
            ext_counts[e] = ext_counts.get(e, 0) + 1
            total_bytes += size
        total_files += len(rows)
        manifest.append({
            'exp_id': exp_id, 'title': exp_title,
            'file_count': len(rows),
            'md_count': sum(1 for r in rows if r[0].lower().endswith('.md')),
            'merged_md': os.path.relpath(merged, DEST) if merged else '',
            'ext_counts': ext_counts,
        })
        print(f'{exp_id}: {len(rows):3d} files'
              + (f", merged={os.path.basename(merged)}" if merged else ''))
    write_top_manifest(manifest, total_files, total_bytes)
    print(f'\nTOTAL: {total_files} files, {total_bytes / 1024 / 1024:.1f} MB')
    print(f'Bundle at: {DEST}')


if __name__ == '__main__':
    main()
