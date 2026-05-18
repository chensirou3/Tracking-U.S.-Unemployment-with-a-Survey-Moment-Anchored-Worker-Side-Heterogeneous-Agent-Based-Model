"""
Build paper_results_bundle/ — copy all paper-relevant artefacts into one place.
COPY ONLY. Originals are never moved or modified.
"""
import os
import csv
import shutil
import datetime
import re

ROOT = '.'
DEST = 'paper_results_bundle'
SUBDIRS = [
    '00_manifest',
    '01_heterogeneity_construction',
    '02_distribution_and_mapping',
    '03_strength_identification',
    '04_main_model_and_controls',
    '05_real_data_and_oos',
    '06_package_C_heterogeneity_ladder',
    '07_package_D_agent_count_sensitivity',
    '08_package_E_calibration_method_sensitivity',
    '09_figures_tables',
    '10_logs_configs',
    '11_misc',
]

EXTS_REPORT = {'.md', '.txt', '.pdf', '.docx'}
EXTS_TABLE = {'.csv', '.xlsx', '.tsv', '.parquet'}
EXTS_IMAGE = {'.png', '.jpg', '.jpeg', '.svg'}
EXTS_CONFIG = {'.yaml', '.yml', '.json', '.toml'}
EXTS_LOG = {'.log'}
EXTS_DATA_RESULT = {'.npz'}  # npz only if filename hits result keyword

ALL_EXTS = EXTS_REPORT | EXTS_TABLE | EXTS_IMAGE | EXTS_CONFIG | EXTS_LOG | EXTS_DATA_RESULT

RESULT_KEYWORDS = [
    'results', 'metrics', 'report', 'summary', 'evaluation', 'oos',
    'validation', 'calibration', 'ladder', 'agent_count', 'heterogeneity',
    'sensitivity', 'claim', 'manifest', 'figure', 'table', 'plot',
    'comparison', 'spec', 'series', 'trajectories', 'rmse', 'metric',
    'decomp', 'positioning', 'rank', 'top', 'overlap', 'param',
    'analysis', 'derived', 'benchmark', 'soa', 'horizon', 'ablation',
    'robustness', 'split', 'main_run', 'best_so_far', 'environment',
    'mechanism', 'population', 'protocol', 'design', 'aggregated',
    'cost', 'noise', 'convergence', 'stability', 'recommendation',
    'log', 'config', 'distribution',
    'history', 'baseline', 'recession', 'real_data', 'first_stable',
    'agent_decision',
]

# Skip: code dirs, raw inputs, caches
SKIP_DIRS = {
    'paper_results_bundle', '.git', '__pycache__', '.idea', '.vscode',
    'Phase3_Code', 'Phase2_Code',  # source code, not results
    'SCE_Data', 'Phase3_Data',     # raw inputs, not results
    'fred_data', 'household', 'labor',  # subdirs under Phase3_Code
}

# Map (top_level_dir, subpath_or_pattern_or_name) -> category
# Tuples of (predicate_fn, category)
def classify(path):
    """Return target category (subdir name) for a relative path."""
    p = path.replace('\\', '/').lower()
    name = os.path.basename(p)

    # Package E (everything in Phase3_Output/packageE)
    if '/packagee/' in p or p.startswith('phase3_output/packagee'):
        return '08_package_E_calibration_method_sensitivity'
    if '/packaged/' in p or p.startswith('phase3_output/packaged'):
        return '07_package_D_agent_count_sensitivity'
    if '/packagec/' in p or p.startswith('phase3_output/packagec'):
        return '06_package_C_heterogeneity_ladder'

    # Package A (training window stability) -> main + controls comparisons
    if '/packagea/' in p or p.startswith('phase3_output/packagea'):
        return '04_main_model_and_controls'
    # Package B (forecast horizon) -> OOS / horizon / real-data
    if '/packageb/' in p or p.startswith('phase3_output/packageb'):
        return '05_real_data_and_oos'

    # Phase 1: heterogeneity construction
    if p.startswith('phase1_output'):
        return '01_heterogeneity_construction'

    # Phase 2: distributions & mapping
    if p.startswith('phase2_output'):
        return '02_distribution_and_mapping'

    # Phase 5: feature/strength identification + parameter priors
    if p.startswith('phase3_output/phase5'):
        return '03_strength_identification'

    # Phase 6: calibration candidates -> strength_identification (calibration)
    if p.startswith('phase3_output/phase6'):
        return '03_strength_identification'

    # Phase 7: main model run + ablation + robustness
    if p.startswith('phase3_output/phase7'):
        if 'real_data' in name or 'real_history' in name:
            return '05_real_data_and_oos'
        return '04_main_model_and_controls'

    # Phase 8: M0 vs D1/D2/D3 derived controls + benchmarks
    if p.startswith('phase3_output/phase8'):
        return '04_main_model_and_controls'

    # Phase3_Output root-level stable runs / first stable / real history
    if p.startswith('phase3_output/'):
        if 'real_history' in name or 'real_data' in name:
            return '05_real_data_and_oos'
        if 'first_stable' in name or 'baseline' in name or 'recession' in name:
            return '05_real_data_and_oos'
        if name.startswith('phase4_'):
            return '02_distribution_and_mapping'
        if name.startswith(('01_', '02_', '03_', '04_')) and name.endswith('.md'):
            return '02_distribution_and_mapping'
        if 'figures' in p or '/figures/' in p:
            return '09_figures_tables'
        if 'ablation' in name:
            return '04_main_model_and_controls'
        if 'schema' in name:
            return '10_logs_configs'
        if 'agent_decision' in name:
            return '11_misc'

    return '11_misc'


def has_result_keyword(name):
    n = name.lower()
    return any(k in n for k in RESULT_KEYWORDS)


def should_include(path):
    name = os.path.basename(path).lower()
    ext = os.path.splitext(name)[1]
    if ext in EXTS_REPORT or ext in EXTS_TABLE or ext in EXTS_IMAGE or ext in EXTS_CONFIG or ext in EXTS_LOG:
        return True
    if ext in EXTS_DATA_RESULT and has_result_keyword(name):
        return True
    return False


def is_likely_final(name):
    n = name.lower()
    return any(tag in n for tag in ['final', 'latest', 'paper', 'clean', 'selected', '_v2', '_v3'])


def is_possibly_old(name, all_names):
    """If there's a v2/v3/final variant of the same root, mark old."""
    n = name.lower()
    base = re.sub(r'(_v\d+|_final|_latest|_paper|_clean|_selected)\.', '.', n)
    if base == n:
        for other in all_names:
            o = other.lower()
            if o == n:
                continue
            ob = re.sub(r'(_v\d+|_final|_latest|_paper|_clean|_selected)\.', '.', o)
            if ob == n:
                return True
    return False


def walk_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # In-place prune
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            if should_include(rel):
                out.append(rel)
    return out


def main():
    os.makedirs(DEST, exist_ok=True)
    for s in SUBDIRS:
        os.makedirs(os.path.join(DEST, s), exist_ok=True)

    files = walk_files()
    print(f'Found {len(files)} candidate files')

    all_names = [os.path.basename(f) for f in files]
    rows = []
    counts = {s: 0 for s in SUBDIRS}

    for rel in files:
        cat = classify(rel)
        name = os.path.basename(rel)
        # Avoid name collisions: prefix with sanitized parent path if collision
        target_dir = os.path.join(DEST, cat)
        target = os.path.join(target_dir, name)
        if os.path.exists(target):
            parent = os.path.dirname(rel).replace('\\', '_').replace('/', '_').replace('.', '_')
            target = os.path.join(target_dir, f'{parent}__{name}')
        try:
            shutil.copy2(rel, target)
        except Exception as e:
            print(f'COPY FAIL {rel} -> {target}: {e}')
            continue
        counts[cat] += 1
        st = os.stat(rel)
        mtime = datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')
        notes = []
        if is_likely_final(name):
            notes.append('likely final')
        if is_possibly_old(name, all_names):
            notes.append('possibly old')
        rows.append({
            'original_path': rel.replace('\\', '/'),
            'new_path': os.path.relpath(target, ROOT).replace('\\', '/'),
            'category': cat,
            'filename': name,
            'last_modified': mtime,
            'notes': '; '.join(notes),
        })

    # manifest.csv
    man_path = os.path.join(DEST, '00_manifest', 'manifest.csv')
    with open(man_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['original_path', 'new_path', 'category',
                                          'filename', 'last_modified', 'notes'])
        w.writeheader()
        w.writerows(rows)
    print(f'Wrote {man_path} ({len(rows)} rows)')

    return rows, counts


if __name__ == '__main__':
    rows, counts = main()
    print('\nCounts per category:')
    for c, n in counts.items():
        print(f'  {c}: {n}')
    print(f'\nTotal copied: {sum(counts.values())}')

