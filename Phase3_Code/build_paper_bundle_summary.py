"""
Generate folder_summary.md and missing_items.md for paper_results_bundle.
Reads manifest.csv produced by build_paper_bundle.py.
"""
import os
import csv
from collections import defaultdict

DEST = 'paper_results_bundle'
MAN = os.path.join(DEST, '00_manifest', 'manifest.csv')
SUM_MD = os.path.join(DEST, '00_manifest', 'folder_summary.md')
MISS_MD = os.path.join(DEST, '00_manifest', 'missing_items.md')

# What we expect to find for each Package / topic
REQUIRED_CHECKS = [
    ('12 core heterogeneity definition tables',
     ['01_Heterogeneity_Audit_Report', '03_Heterogeneity_Dictionary', '04_Survey_to_Agent_Mapping'],
     '01_heterogeneity_construction'),
    ('M0 vs D1/D2/D3 main controls (Phase 8)',
     ['comparison_results', 'derived_results', 'fig1_unified_comparison', 'paper_ready_comparison'],
     '04_main_model_and_controls'),
    ('Real-data run (full history)',
     ['run_real_history', 'real_history_run', 'main_run_metrics'],
     '05_real_data_and_oos'),
    ('OOS / horizon evaluation (Package B)',
     ['horizon_results', 'horizon_degradation_table', 'horizon_source_of_advantage', 'PackageB_Summary'],
     '05_real_data_and_oos'),
    ('Training-window stability (Package A)',
     ['stability_report', 'comparison_table', 'PackageA_Summary'],
     '04_main_model_and_controls'),
    ('Package C heterogeneity ladder final results & claim',
     ['PackageC_Summary', 'projection_ladder_results', 'refit_ladder_results',
      'minimal_sufficient_set', 'layer_ladder_results'],
     '06_package_C_heterogeneity_ladder'),
    ('Package D agent count sensitivity final results & claim',
     ['PackageD_Summary', 'agent_count_results', 'convergence_report',
      'monte_carlo_noise_report', 'computational_cost_report', 'packageD_claim'],
     '07_package_D_agent_count_sensitivity'),
    ('Package E calibration method sensitivity final results & claim',
     ['PackageE_Summary', 'method_raw_results', 'method_aggregated',
      'source_of_advantage_per_method', 'packageE_claim'],
     '08_package_E_calibration_method_sensitivity'),
    ('Phase 5 strength identification & parameter priors',
     ['parameter_prior_bands', 'screening_results', 'feature_rankings'],
     '03_strength_identification'),
    ('Phase 6 calibration candidates',
     ['candidate_baseline', 'candidate_aggressive', 'candidate_conservative', 'calibration_results'],
     '03_strength_identification'),
    ('Phase 7 main run + ablation + robustness',
     ['main_run_metrics', 'ablation_results', 'robustness_results', 'Phase7_Summary'],
     '04_main_model_and_controls'),
]


def load_manifest():
    rows = []
    with open(MAN, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def folder_summary(rows):
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r['category']].append(r)

    lines = ['# Paper Results Bundle — Folder Summary', '',
             f'Total files copied: **{len(rows)}**', '',
             '## Counts per subfolder', '',
             '| Subfolder | File count |',
             '|-----------|-----------:|']
    for s in sorted(by_cat.keys()):
        lines.append(f'| {s} | {len(by_cat[s])} |')
    lines.append('')

    # Per-subfolder file listing + likely-final / possibly-old flags
    for s in sorted(by_cat.keys()):
        lines += [f'## {s}', '']
        flags_count = {'likely_final': 0, 'possibly_old': 0}
        for r in sorted(by_cat[s], key=lambda x: x['filename']):
            tag_parts = []
            if 'likely final' in r['notes']:
                tag_parts.append('[FINAL?]')
                flags_count['likely_final'] += 1
            if 'possibly old' in r['notes']:
                tag_parts.append('[OLD?]')
                flags_count['possibly_old'] += 1
            tag = ' '.join(tag_parts)
            lines.append(f'- `{r["filename"]}` ({r["last_modified"]}) {tag}'.rstrip())
        lines += ['',
                  f'_Subfolder summary: {flags_count["likely_final"]} files look final, '
                  f'{flags_count["possibly_old"]} files look possibly older versions_', '']

    # Possible duplicates by filename across subfolders
    name_locations = defaultdict(list)
    for r in rows:
        name_locations[r['filename']].append(r['category'])
    dup = {n: cats for n, cats in name_locations.items() if len(cats) > 1}
    lines += ['## Possible duplicates (same filename in multiple subfolders)', '']
    if dup:
        for n, cats in sorted(dup.items()):
            lines.append(f'- `{n}` -> {", ".join(cats)}')
    else:
        lines.append('_None detected._')
    lines.append('')

    with open(SUM_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {SUM_MD}')


def missing_check(rows):
    lines = ['# Paper Results Bundle — Missing Items Audit', '',
             'For each required content area, we check whether key files (any keyword '
             'match in filename) are present in the expected subfolder. Files in other '
             'subfolders are reported as a fallback hit.', '']

    # Build index: category -> list of filenames
    by_cat = defaultdict(list)
    by_name = defaultdict(list)
    for r in rows:
        by_cat[r['category']].append(r['filename'])
        by_name[r['filename'].lower()].append(r['category'])

    missing = []
    for label, keywords, expected_cat in REQUIRED_CHECKS:
        hits_in_cat = []
        hits_elsewhere = []
        for kw in keywords:
            kwl = kw.lower()
            for fn in by_cat.get(expected_cat, []):
                if kwl in fn.lower() and fn not in hits_in_cat:
                    hits_in_cat.append(fn)
            for fn, cats in by_name.items():
                if kwl in fn:
                    for c in cats:
                        if c != expected_cat:
                            tag = f'{fn} (in {c})'
                            if tag not in hits_elsewhere:
                                hits_elsewhere.append(tag)
        status = 'OK' if hits_in_cat else ('PARTIAL' if hits_elsewhere else 'MISSING')
        if status != 'OK':
            missing.append(label)
        lines += [f'## {label}', f'- Expected subfolder: `{expected_cat}`',
                  f'- Status: **{status}**']
        if hits_in_cat:
            lines.append(f'- Hits in expected folder ({len(hits_in_cat)}):')
            for h in hits_in_cat[:8]:
                lines.append(f'  - `{h}`')
        if hits_elsewhere and not hits_in_cat:
            lines.append(f'- Fallback hits elsewhere ({len(hits_elsewhere)}):')
            for h in hits_elsewhere[:8]:
                lines.append(f'  - `{h}`')
        lines.append('')

    lines += ['## Summary', '']
    if missing:
        lines.append('**Items NOT cleanly satisfied:**')
        for m in missing:
            lines.append(f'- {m}')
    else:
        lines.append('**All required items satisfied** in their expected subfolders.')
    lines.append('')

    with open(MISS_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {MISS_MD}')
    return missing


if __name__ == '__main__':
    rows = load_manifest()
    folder_summary(rows)
    missing = missing_check(rows)
    print(f'\nMissing/partial items: {len(missing)}')
    for m in missing:
        print(f'  - {m}')
