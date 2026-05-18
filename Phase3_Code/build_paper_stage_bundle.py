"""
Build paper_stage_bundle/: per-phase copy of every result file plus a merged
markdown per phase. Originals are never modified.
"""
import os
import re
import csv
import shutil
import datetime
from collections import defaultdict, Counter

ROOT = '.'
DEST = 'paper_stage_bundle'
EXCLUDE_DIR_NAMES = {
    '.git', '__pycache__', '.ipynb_checkpoints', 'node_modules',
    '.venv', 'venv', '.mypy_cache', '.pytest_cache',
    'paper_stage_bundle', 'paper_md_bundle', 'paper_results_bundle',
    'fred_data',
}
INCLUDE_EXT = {
    '.md', '.csv', '.png',
    '.json', '.npz', '.xlsx', '.pdf', '.jpg', '.jpeg', '.svg',
    '.parquet', '.txt', '.yaml', '.yml',
}

PHASE_DIR_NAMES = [
    '01_phase1', '02_phase2', '03_phase3', '04_phase4', '05_phase5',
    '06_phase6', '07_phase7', '08_phase8', '09_cross_stage_or_unclassified',
]

PHASE_PATTERNS = [
    (re.compile(r'(?:^|[\\/_])phase[\s_]*1(?:[^0-9]|$)', re.I), 'phase1'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*2(?:[^0-9]|$)', re.I), 'phase2'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*3(?:[^0-9]|$)', re.I), 'phase3'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*4(?:[^0-9]|$)', re.I), 'phase4'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*5(?:[^0-9]|$)', re.I), 'phase5'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*6(?:[^0-9]|$)', re.I), 'phase6'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*7(?:[^0-9]|$)', re.I), 'phase7'),
    (re.compile(r'(?:^|[\\/_])phase[\s_]*8(?:[^0-9]|$)', re.I), 'phase8'),
]

# Package-folder → phase assignment. Packages A-E were executed on top of
# Phase 8's comparison architecture.
PACKAGE_TO_PHASE = {
    'packagea': 'phase8', 'packageb': 'phase8',
    'packagec': 'phase8', 'packaged': 'phase8', 'packagee': 'phase8',
}

# Path-hint routing for input-data directories and other non-phase
# containers. These are checked only when no phase or package token matches.
PATH_HINT_TO_PHASE = [
    ('sce_data', 'phase2'),      # NY Fed SCE survey microdata → pop init
    ('phase3_data', 'phase7'),   # FRED macro series → real-data target system
]

# Topic keyword → phase fallback (applied when path tokens are silent).
TOPIC_KEYWORDS = [
    ('phase1', [
        'heterogeneity', 'audit', 'dictionary', 'dimension_init',
        'mvp_boundary', 'survey_to_agent', 'survey-to-agent',
        'trait_definition', 'agent_schema',
    ]),
    ('phase2', [
        'population', 'initialization', 'joint_distribution',
        'joint_structure', 'distribution_fitting', 'population_v1',
        'synthetic_population', 'diagnostic', 'backbone',
        'core_distributions', 'lm_distributions', 'spending_distributions',
        'empirical_distributions',
    ]),
    ('phase3', [
        'engine', 'scheduler', 'transition', 'environment_spec',
        'state_map', 'state_transition', 'monthly_loop',
        'mechanism_interface', 'simulation_order', 'first_stable_run',
    ]),
    ('phase4', [
        'mechanism_registry', 'mechanism_map', 'mechanism_toggle',
        'mechanism_ablation',
    ]),
    ('phase5', [
        'screening', 'functional_form', 'partial_dependence', 'interaction',
        'identification', 'feature_importance', 'feature_ranking',
        'parameter_prior', 'instability',
    ]),
    ('phase6', [
        'calibration', 'candidate_baseline', 'candidate_aggressive',
        'candidate_conservative', 'calibration_comparison', 'prior_bands',
        'selected_params',
    ]),
    ('phase7', [
        'real_data', 'target_system', 'time_alignment', 'claim_update',
        'robustness', 'oos', 'main_run', 'main_experiment', 'ablation',
    ]),
    ('phase8', [
        'benchmark', 'derived_control', 'comparison_architecture',
        'unified_evaluation', 'source_of_advantage', 'positioning',
        'paper_ready', 'packagea', 'packageb', 'packagec', 'packaged',
        'packagee', 'ladder', 'agent_count', 'horizon',
    ]),
]

# Phase → output dir mapping
PHASE_TO_DIR = {f'phase{i}': n for i, n in enumerate(PHASE_DIR_NAMES[:8], 1)}
PHASE_TO_DIR['unclassified'] = '09_cross_stage_or_unclassified'


def is_excluded(path):
    parts = [p.lower() for p in path.replace('\\', '/').split('/')]
    return bool({p for p in parts} & {e.lower() for e in EXCLUDE_DIR_NAMES})


def scan_files(root):
    out = []
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in EXCLUDE_DIR_NAMES
                 and not d.startswith('.')]
        if is_excluded(r):
            continue
        for f in fs:
            if os.path.splitext(f)[1].lower() in INCLUDE_EXT:
                out.append(os.path.normpath(os.path.join(r, f)))
    return sorted(out, key=lambda x: x.lower())


def classify(path):
    """Return (phase_name, reason)."""
    pl = path.lower().replace('\\', '/')
    parts = [p for p in pl.split('/') if p]
    inner_parts = [p for i, p in enumerate(parts)
                   if not (i == 0 and p.endswith('_output'))]

    # 1) Package-folder token (Packages A-E live under Phase3_Output)
    for k, v in PACKAGE_TO_PHASE.items():
        if any(k in p for p in inner_parts):
            return v, f'package-token:{k}'

    # 2) Deepest phase token in inner components
    best = None
    for i, comp in enumerate(inner_parts):
        for pat, name in PHASE_PATTERNS:
            if pat.search(comp):
                best = (i, name, comp)
    if best is not None:
        return best[1], f'path-token:{best[2]}'

    # 3) Fallback to full-path phase scan (catches `Phase1_Output/*` stripped
    #    into only `Phase1_Output` at position 0)
    for pat, name in PHASE_PATTERNS:
        if pat.search(pl):
            return name, 'path-token:fullpath'

    # 4) Path hints for non-phase container directories
    for hint, phase in PATH_HINT_TO_PHASE:
        if hint in pl:
            return phase, f'path-hint:{hint}'

    # 5) Topic-keyword fallback
    fname = os.path.basename(pl)
    for phase, kws in TOPIC_KEYWORDS:
        for kw in kws:
            if kw in fname or kw in pl:
                return phase, f'keyword:{kw}'

    return 'unclassified', 'no-match'


def sibling_presence(path, all_paths_set):
    d = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    try:
        sibs = os.listdir(d)
    except OSError:
        return False, False, False
    md = any(s.lower().endswith('.md') and
             os.path.splitext(s)[0] == stem for s in sibs)
    cv = any(s.lower().endswith('.csv') and
             os.path.splitext(s)[0] == stem for s in sibs)
    pn = any(s.lower().endswith('.png') and
             os.path.splitext(s)[0] == stem for s in sibs)
    return md, cv, pn


def safe_copy(src, dest_path):
    """Copy src to dest_path; if dest_path exists, append __dupN suffix."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not os.path.exists(dest_path):
        shutil.copy2(src, dest_path)
        return dest_path
    stem, ext = os.path.splitext(dest_path)
    i = 1
    while True:
        cand = f'{stem}__dup{i}{ext}'
        if not os.path.exists(cand):
            shutil.copy2(src, cand)
            return cand
        i += 1


def read_text(path):
    for enc in ('utf-8', 'utf-8-sig', 'gbk', 'latin-1'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, 'rb') as f:
        return f.read().decode('utf-8', errors='replace')


def clean_blank_lines(text):
    return re.sub(r'\n{4,}', '\n\n\n', text).rstrip() + '\n'


def make_md_header(rec):
    return (
        '\n\n---\n\n'
        '# Source File\n'
        f'- Original path: `{rec["original_path"]}`\n'
        f'- Filename: `{rec["filename"]}`\n'
        f'- Stage: `{rec["phase_assigned"]}`\n'
        f'- Phase reason: `{rec["phase_reason"]}`\n'
        f'- Last modified: {rec["last_modified"]}\n'
        '\n---\n\n'
    )


def write_merged_md(phase, recs, out_path):
    md_recs = [r for r in recs if r['extension'] == '.md']
    md_recs.sort(key=lambda r: (r['original_path'].lower(),
                                r['filename'].lower()))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'# Stage Merge: {phase}\n\n')
        f.write(f'All markdown files classified to stage `{phase}`. '
                'Sorted by original path then filename.\n\n')
        f.write(f'Files included: **{len(md_recs)}**\n\n')
        f.write('## Table of contents\n\n')
        for i, r in enumerate(md_recs, 1):
            f.write(f'{i}. `{r["original_path"]}`\n')
        if not md_recs:
            f.write('\n_No markdown files were classified to this stage._\n')
            return
        for r in md_recs:
            f.write(make_md_header(r))
            f.write(clean_blank_lines(r.get('content', '')))


def write_phase_inventory(phase, recs, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fields = ['original_path', 'copied_path', 'filename', 'extension']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in sorted(recs, key=lambda x: x['original_path'].lower()):
            w.writerow({k: r[k] for k in fields})


def write_manifest(records, out_path):
    fields = ['original_path', 'copied_path', 'filename', 'extension',
              'phase_assigned', 'phase_reason', 'sibling_md_exists',
              'sibling_csv_exists', 'sibling_png_exists', 'last_modified']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow({
                'original_path': r['original_path'],
                'copied_path': r['copied_path'],
                'filename': r['filename'],
                'extension': r['extension'],
                'phase_assigned': r['phase_assigned'],
                'phase_reason': r['phase_reason'],
                'sibling_md_exists': 'yes' if r['sibling_md_exists'] else 'no',
                'sibling_csv_exists': 'yes' if r['sibling_csv_exists'] else 'no',
                'sibling_png_exists': 'yes' if r['sibling_png_exists'] else 'no',
                'last_modified': r['last_modified'],
            })


def write_phase_summary(records, out_path):
    by_phase = defaultdict(list)
    for r in records:
        by_phase[r['phase_assigned']].append(r)

    lines = ['# Stage Summary', '',
             f'Total result files copied: **{len(records)}**',
             '',
             'Scan excludes: paper_stage_bundle/, paper_md_bundle/, '
             'paper_results_bundle/, .git/, __pycache__/, .ipynb_checkpoints/, '
             'node_modules/, venv dirs, fred_data/.',
             '',
             '## File count by stage', '',
             '| Stage | Total | md | csv | png | json | npz | xlsx | pdf | other | merged_md |',
             '|-------|------:|---:|----:|----:|-----:|----:|-----:|----:|------:|-----------|']
    phase_order = [f'phase{i}' for i in range(1, 9)] + ['unclassified']
    for ph in phase_order:
        recs = by_phase.get(ph, [])
        if not recs and ph == 'unclassified':
            continue
        extc = Counter(r['extension'] for r in recs)
        known = ['.md', '.csv', '.png', '.json', '.npz', '.xlsx', '.pdf']
        other = sum(c for e, c in extc.items() if e not in known)
        dirn = PHASE_TO_DIR[ph]
        merged = f'`paper_stage_bundle/{dirn}/merged_md/{ph}_merged.md`'
        lines.append(
            f'| {ph} | {len(recs)} | {extc[".md"]} | {extc[".csv"]} | '
            f'{extc[".png"]} | {extc[".json"]} | {extc[".npz"]} | '
            f'{extc[".xlsx"]} | {extc[".pdf"]} | {other} | {merged} |'
        )

    counts = [(ph, len(by_phase.get(ph, []))) for ph in phase_order
              if by_phase.get(ph)]
    counts.sort(key=lambda x: -x[1])
    lines += ['', '## Stages ranked by file count', '']
    for ph, n in counts:
        lines.append(f'- `{ph}`: {n} files')

    empty_md = [ph for ph in phase_order if ph in by_phase
                and not any(r['extension'] == '.md' for r in by_phase[ph])]
    empty_csv = [ph for ph in phase_order if ph in by_phase
                 and not any(r['extension'] == '.csv' for r in by_phase[ph])]
    empty_png = [ph for ph in phase_order if ph in by_phase
                 and not any(r['extension'] == '.png' for r in by_phase[ph])]
    lines += ['', '## Stages missing key file types', '',
              f'- without md: {empty_md or "_none_"}',
              f'- without csv: {empty_csv or "_none_"}',
              f'- without png: {empty_png or "_none_"}']

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))



def write_duplicate_check(records, out_path):
    by_name = defaultdict(list)
    for r in records:
        by_name[r['filename'].lower()].append(r['original_path'])
    dup_name = {k: v for k, v in by_name.items() if len(set(v)) > 1}

    suffix_re = re.compile(
        r'(_v\d+|_latest|_clean|_paper[_-]?ready|_final|_update(d)?'
        r'|_report|_old|_new|_fixed|_draft)$')
    version_stems = defaultdict(list)
    for r in records:
        stem = os.path.splitext(r['filename'].lower())[0]
        prev, base = None, stem
        while prev != base:
            prev = base
            base = suffix_re.sub('', base)
        # Key by (base, extension) so version families only flag within the
        # same file type. Pairs like `foo.md` + `foo.csv` are not versions.
        version_stems[(base, r['extension'])].append(r['filename'])
    version_groups = {k: sorted(set(v)) for k, v in version_stems.items()
                      if len(set(v)) > 1}

    lines = ['# Duplicate Check', '',
             'Filenames appearing in more than one source location, plus '
             'likely version families. Originals are NOT modified.',
             '', '## Same filename in multiple source paths', '']
    if dup_name:
        for name, paths in sorted(dup_name.items()):
            lines.append(f'- `{name}`')
            for p in paths:
                lines.append(f'  - `{p}`')
    else:
        lines.append('_None._')
    lines += ['', '## Possible version families '
              '(`_v2`, `_latest`, `_clean`, `_paper_ready`, `_final`, '
              '`_update`, `_report`, `_old`, `_new`, `_fixed`, `_draft`)',
              '']
    if version_groups:
        for (stem, ext), fns in sorted(version_groups.items()):
            lines.append(f'- stem `{stem}` ({ext}): {", ".join(fns)}')
    else:
        lines.append('_None._')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def write_missing_stage_notes(records, out_path):
    by_phase = defaultdict(list)
    for r in records:
        by_phase[r['phase_assigned']].append(r)
    phase_order = [f'phase{i}' for i in range(1, 9)]

    lines = ['# Missing Stage Notes', '',
             'Stages with no files, or with only one or two files, are '
             'flagged below for a manual second look.', '']
    for ph in phase_order + ['unclassified']:
        recs = by_phase.get(ph, [])
        if not recs:
            lines.append(f'- `{ph}`: **no files at all**')
        elif len(recs) <= 2:
            files = ', '.join(f'`{r["filename"]}`' for r in recs)
            lines.append(f'- `{ph}`: only {len(recs)} file(s) -> {files}')
    if all(by_phase.get(ph) and len(by_phase[ph]) > 2 for ph in phase_order):
        lines.append('')
        lines.append('All eight phases have at least three files.')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    for sub in PHASE_DIR_NAMES:
        os.makedirs(os.path.join(DEST, sub, 'raw_files'), exist_ok=True)
        os.makedirs(os.path.join(DEST, sub, 'merged_md'), exist_ok=True)
    os.makedirs(os.path.join(DEST, '00_manifest'), exist_ok=True)

    paths = scan_files(ROOT)
    print(f'Scanned {len(paths)} candidate files')

    records = []
    for src in paths:
        st = os.stat(src)
        rel = os.path.relpath(src, ROOT)
        rel_posix = rel.replace('\\', '/')
        phase, reason = classify(src)
        ext = os.path.splitext(src)[1].lower()
        out_dir = os.path.join(DEST, PHASE_TO_DIR[phase], 'raw_files', rel)
        copied = safe_copy(src, out_dir)
        copied_norm = os.path.relpath(copied, ROOT).replace('\\', '/')
        smd, scv, spn = sibling_presence(src, set(paths))
        rec = {
            'original_path': rel_posix,
            'copied_path': copied_norm,
            'filename': os.path.basename(src),
            'extension': ext,
            'phase_assigned': phase,
            'phase_reason': reason,
            'sibling_md_exists': smd,
            'sibling_csv_exists': scv,
            'sibling_png_exists': spn,
            'last_modified': datetime.datetime.fromtimestamp(
                st.st_mtime).isoformat(timespec='seconds'),
            'size_bytes': st.st_size,
        }
        if ext == '.md':
            try:
                rec['content'] = read_text(src)
            except OSError:
                rec['content'] = ''
        records.append(rec)

    by_phase = defaultdict(list)
    for r in records:
        by_phase[r['phase_assigned']].append(r)

    for phase in list(PHASE_TO_DIR.keys()):
        recs = by_phase.get(phase, [])
        dirn = PHASE_TO_DIR[phase]
        merged_path = os.path.join(DEST, dirn, 'merged_md',
                                   f'{phase}_merged.md')
        write_merged_md(phase, recs, merged_path)
        inv_path = os.path.join(DEST, dirn, f'{phase}_inventory.csv')
        write_phase_inventory(phase, recs, inv_path)

    man_path = os.path.join(DEST, '00_manifest', 'stage_manifest.csv')
    write_manifest(records, man_path)
    print(f'Wrote {man_path}')
    sum_path = os.path.join(DEST, '00_manifest', 'phase_summary.md')
    write_phase_summary(records, sum_path)
    print(f'Wrote {sum_path}')
    dup_path = os.path.join(DEST, '00_manifest', 'duplicate_check.md')
    write_duplicate_check(records, dup_path)
    print(f'Wrote {dup_path}')
    miss_path = os.path.join(DEST, '00_manifest',
                             'missing_stage_notes.md')
    write_missing_stage_notes(records, miss_path)
    print(f'Wrote {miss_path}')

    print()
    print('Per-phase counts:')
    for ph in [f'phase{i}' for i in range(1, 9)] + ['unclassified']:
        n = len(by_phase.get(ph, []))
        if n:
            print(f'  {ph:14s} {n:4d} files')


if __name__ == '__main__':
    main()
