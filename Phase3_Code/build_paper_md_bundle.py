"""
Build paper_md_bundle/: recursively scan project .md files and merge into
phase/topic bundles with full provenance. Originals are never touched.
"""
import os
import re
import csv
import datetime
from collections import defaultdict, Counter

ROOT = '.'
DEST = 'paper_md_bundle'
EXCLUDE_DIR_NAMES = {
    '.git', '__pycache__', '.ipynb_checkpoints', 'node_modules',
    '.venv', 'venv', '.mypy_cache', '.pytest_cache',
    'paper_md_bundle', 'paper_results_bundle',
}

SUBDIRS = [
    '00_manifest', '01_all_in_one', '02_by_phase',
    '03_by_topic', '04_original_md_path_index',
]

PHASE_PATTERNS = [
    (re.compile(r'(?:^|[\\/_])phase\s*1(?:[^0-9]|$)', re.I), 'phase1'),
    (re.compile(r'(?:^|[\\/_])phase\s*2(?:[^0-9]|$)', re.I), 'phase2'),
    (re.compile(r'(?:^|[\\/_])phase\s*3(?:[^0-9]|$)', re.I), 'phase3'),
    (re.compile(r'(?:^|[\\/_])phase\s*4(?:[^0-9]|$)', re.I), 'phase4'),
    (re.compile(r'(?:^|[\\/_])phase\s*5(?:[^0-9]|$)', re.I), 'phase5'),
    (re.compile(r'(?:^|[\\/_])phase\s*6(?:[^0-9]|$)', re.I), 'phase6'),
    (re.compile(r'(?:^|[\\/_])phase\s*7(?:[^0-9]|$)', re.I), 'phase7'),
    (re.compile(r'(?:^|[\\/_])phase\s*8(?:[^0-9]|$)', re.I), 'phase8'),
]

# Package folders are mapped to best-matching phase for narrative continuity.
PACKAGE_TO_PHASE = {
    'packagea': 'phase8', 'packageb': 'phase8',
    'packagec': 'phase8', 'packaged': 'phase8', 'packagee': 'phase8',
}

TOPIC_RULES = [
    ('heterogeneity', [
        'heterogeneity', 'heterogeneity_audit', 'heterogeneity_dictionary',
        'mvp_boundary', 'vectorized_agent_schema', 'survey_to_agent',
        'ladder', 'minimal_sufficient',
    ]),
    ('population_initialization', [
        'population', 'backbone', 'dimension_init', 'joint_structure',
        'population_diagnostic', 'population_sensitivity',
    ]),
    ('engine_and_mechanisms', [
        'environment_spec', 'simulation_order', 'state_transition',
        'mechanism_map', 'mechanism_registry', 'first_stable_run',
        'stage3_input',
    ]),
    ('identification_and_functional_forms', [
        'functional_form', 'identification', 'screening', 'interaction',
        'feature_ranking', 'instability', 'phase5_summary',
    ]),
    ('calibration', [
        'calibration', 'candidate_', 'packagee', 'method_set',
        'fair_comparison', 'method_metric', 'method_performance',
        'parameter_overlap', 'cost_benefit',
    ]),
    ('real_data_main_results', [
        'real_data', 'real_history', 'target_system', 'time_alignment',
        'main_run', 'phase7_summary', 'phase8_summary',
        'first_stable_run_summary',
    ]),
    ('robustness', [
        'packagea_summary', 'packageb_summary', 'packagec_summary',
        'packaged_summary', 'stability_report', 'robustness',
        'window_design', 'run_strategy', 'horizon', 'ablation',
        'agent_count', 'convergence', 'monte_carlo', 'noise',
        'ranking_by_count', 'computational_cost', 'recommendation',
        'ladder_level', 'ladder_metric', 'ladder_run_strategy',
        'heterogeneity_ladder_design', 'forecast_origin',
    ]),
    ('benchmarks_and_comparison', [
        'benchmark', 'external_benchmark', 'comparison_architecture',
        'derived_control', 'unified_evaluation', 'source_of_advantage',
        'positioning', 'claim_update',
    ]),
    ('paper_ready_materials', [
        'paper_ready', 'paper-ready', 'paper_results', 'candidate_versions',
        'evaluation_metric_spec', 'metric_spec',
    ]),
]

HIGH_VALUE_KEYWORDS = [
    'summary', 'claim_update', 'claim', 'target_system', 'time_alignment',
    'window_design', 'source_of_advantage', 'benchmark_specs',
    'external_benchmark', 'derived_control', 'paper_ready',
    'comparison_architecture', 'unified_evaluation',
]


def is_excluded(path):
    parts = set(p.lower() for p in path.replace('\\', '/').split('/'))
    return bool(parts & {e.lower() for e in EXCLUDE_DIR_NAMES})


def scan_md_files(root):
    out = []
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in EXCLUDE_DIR_NAMES
                 and not d.startswith('.')]
        if is_excluded(r):
            continue
        for f in fs:
            if f.lower().endswith('.md'):
                p = os.path.normpath(os.path.join(r, f))
                out.append(p)
    return sorted(out, key=lambda x: x.lower())


def guess_phase(path):
    pl = path.lower().replace('\\', '/')
    parts = [p for p in pl.split('/') if p]
    # Top-level container directories (e.g. "Phase3_Output") describe the
    # storage location, not the originating phase. Ignore them so inner
    # package/phase tokens take priority.
    inner_parts = [p for i, p in enumerate(parts)
                   if not (i == 0 and p.endswith('_output'))]
    # Package mapping wins over the outer phase3_output container.
    for k, v in PACKAGE_TO_PHASE.items():
        if any(k in p for p in inner_parts):
            return v
    # Otherwise prefer the deepest (rightmost) phase token in the remaining
    # inner components.
    best = None
    for i, comp in enumerate(inner_parts):
        for pat, name in PHASE_PATTERNS:
            if pat.search(comp):
                best = (i, name)
    if best is not None:
        return best[1]
    # Last-chance fallback: scan the full path (covers edge cases like
    # `Phase1_Output/*` where the phase lives in the top component).
    for pat, name in PHASE_PATTERNS:
        if pat.search(pl):
            return name
    return 'unclassified'


def guess_topic(path):
    pl = os.path.basename(path).lower()
    fullp = path.lower().replace('\\', '/')
    for topic, keys in TOPIC_RULES:
        for k in keys:
            if k in pl or k in fullp:
                return topic
    return 'misc'


def is_high_value(path):
    pl = os.path.basename(path).lower()
    return [k for k in HIGH_VALUE_KEYWORDS if k in pl]


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


def make_header(rec):
    return (
        '\n\n---\n\n'
        '# Source File\n'
        f'- Original path: `{rec["original_path"]}`\n'
        f'- Filename: `{rec["filename"]}`\n'
        f'- Phase guess: `{rec["phase_guess"]}`\n'
        f'- Topic guess: `{rec["topic_guess"]}`\n'
        f'- Last modified: {rec["last_modified"]}\n'
        '\n---\n\n'
    )


def sibling_info(path):
    d = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    try:
        sibs = os.listdir(d)
    except OSError:
        return False, False
    png = any(s.lower().endswith('.png') and os.path.splitext(s)[0] == stem
              for s in sibs)
    csv_ = any(s.lower().endswith('.csv') and os.path.splitext(s)[0] == stem
               for s in sibs)
    return png, csv_


def write_merged(out_path, records, title, descr):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'# {title}\n\n')
        f.write(f'{descr}\n\n')
        f.write(f'Files included: **{len(records)}**\n\n')
        f.write('Table of contents\n\n')
        for i, r in enumerate(records, 1):
            f.write(f'{i}. `{r["original_path"]}` '
                    f'(phase={r["phase_guess"]}, topic={r["topic_guess"]})\n')
        for r in records:
            f.write(make_header(r))
            f.write(clean_blank_lines(r['content']))


def detect_duplicates(records):
    by_name = defaultdict(list)
    for r in records:
        by_name[r['filename'].lower()].append(r['original_path'])
    dup_name = {k: v for k, v in by_name.items() if len(v) > 1}

    by_hash = defaultdict(list)
    for r in records:
        h = hash(re.sub(r'\s+', ' ', r['content']).strip())
        by_hash[h].append(r['original_path'])
    dup_hash = [v for v in by_hash.values() if len(v) > 1]

    version_stems = defaultdict(list)
    suffix_re = re.compile(
        r'(_v\d+|_latest|_clean|_paper[_-]?ready|_final|_update(d)?'
        r'|_report|_old|_new|_fixed|_draft)$')
    for r in records:
        stem = os.path.splitext(r['filename'].lower())[0]
        prev = None
        base = stem
        while prev != base:
            prev = base
            base = suffix_re.sub('', base)
        version_stems[base].append(r['filename'])
    version_groups = {k: sorted(set(v)) for k, v in version_stems.items()
                      if len(set(v)) > 1}

    return dup_name, dup_hash, version_groups


def main():
    for sd in SUBDIRS:
        os.makedirs(os.path.join(DEST, sd), exist_ok=True)

    md_paths = scan_md_files(ROOT)
    print(f'Scanned {len(md_paths)} .md files (excluding paper_results_bundle/)')

    records = []
    for p in md_paths:
        st = os.stat(p)
        rec = {
            'original_path': p.replace('\\', '/'),
            'filename': os.path.basename(p),
            'phase_guess': guess_phase(p),
            'topic_guess': guess_topic(p),
            'last_modified': datetime.datetime.fromtimestamp(
                st.st_mtime).isoformat(timespec='seconds'),
            'size_bytes': st.st_size,
            'content': read_text(p),
            'merged_into': [],
        }
        rec['sibling_png_exists'], rec['sibling_csv_exists'] = sibling_info(p)
        rec['high_value_tags'] = is_high_value(p)
        records.append(rec)

    # Stable ordering: phase number > topic > filename
    phase_order = {f'phase{i}': i for i in range(1, 9)}
    phase_order['unclassified'] = 99
    records.sort(key=lambda r: (phase_order.get(r['phase_guess'], 99),
                                r['topic_guess'], r['filename'].lower()))

    # A) All-in-one
    all_path = os.path.join(DEST, '01_all_in_one', 'all_markdown_merged.md')
    write_merged(all_path, records, 'All Markdown Merged',
                 'Complete recursive merge of every `.md` file in the project '
                 '(excluding `paper_results_bundle/` copies). Originals are '
                 'unchanged.')
    for r in records:
        r['merged_into'].append('01_all_in_one/all_markdown_merged.md')

    # B) By phase
    by_phase = defaultdict(list)
    for r in records:
        by_phase[r['phase_guess']].append(r)
    for phase, recs in by_phase.items():
        out = f'02_by_phase/{phase}_merged.md' if phase != 'unclassified' \
            else '02_by_phase/unclassified_merged.md'
        write_merged(os.path.join(DEST, out), recs,
                     f'Phase Merge: {phase}',
                     f'All markdown files grouped under `{phase}`.')
        for r in recs:
            r['merged_into'].append(out)

    # C) By topic
    by_topic = defaultdict(list)
    for r in records:
        by_topic[r['topic_guess']].append(r)
    topic_order = [t for t, _ in TOPIC_RULES] + ['misc']
    for topic in topic_order:
        recs = by_topic.get(topic, [])
        if not recs:
            continue
        out = f'03_by_topic/{topic}_merged.md'
        write_merged(os.path.join(DEST, out), recs,
                     f'Topic Merge: {topic}',
                     f'All markdown files grouped under topic `{topic}`.')
        for r in recs:
            r['merged_into'].append(out)

    write_manifest(records)
    write_inventory(records, by_phase, by_topic)
    write_merge_map(records)
    write_duplicate_check(records)
    write_path_index(records)
    return records



def write_manifest(records):
    p = os.path.join(DEST, '00_manifest', 'manifest.csv')
    fields = ['original_path', 'filename', 'phase_guess', 'topic_guess',
              'merged_into', 'last_modified', 'size_bytes',
              'sibling_png_exists', 'sibling_csv_exists', 'high_value_tags']
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow({
                'original_path': r['original_path'],
                'filename': r['filename'],
                'phase_guess': r['phase_guess'],
                'topic_guess': r['topic_guess'],
                'merged_into': '; '.join(r['merged_into']),
                'last_modified': r['last_modified'],
                'size_bytes': r['size_bytes'],
                'sibling_png_exists': 'yes' if r['sibling_png_exists'] else 'no',
                'sibling_csv_exists': 'yes' if r['sibling_csv_exists'] else 'no',
                'high_value_tags': ','.join(r['high_value_tags']),
            })
    print(f'Wrote {p}')


def write_inventory(records, by_phase, by_topic):
    p = os.path.join(DEST, '00_manifest', 'md_inventory.md')
    lines = ['# Markdown Inventory', '',
             f'Total markdown files discovered: **{len(records)}**',
             '',
             'Scan excludes: `paper_results_bundle/`, `.git/`, `__pycache__/`, '
             '`.ipynb_checkpoints/`, `node_modules/`, venv dirs, and the '
             'output dir `paper_md_bundle/` itself.',
             '', '## Counts by phase', '',
             '| Phase | File count |', '|-------|-----------:|']
    for ph in ['phase1', 'phase2', 'phase3', 'phase4', 'phase5',
               'phase6', 'phase7', 'phase8', 'unclassified']:
        if ph in by_phase:
            lines.append(f'| {ph} | {len(by_phase[ph])} |')
    lines += ['', '## Counts by topic', '',
              '| Topic | File count |', '|-------|-----------:|']
    for topic, _ in TOPIC_RULES:
        if topic in by_topic:
            lines.append(f'| {topic} | {len(by_topic[topic])} |')
    if 'misc' in by_topic:
        lines.append(f'| misc | {len(by_topic["misc"])} |')

    # High-value
    hv = [r for r in records if r['high_value_tags']]
    lines += ['', '## High-value markdown files',
              '',
              'Files whose filename contains any of: '
              f'`{", ".join(HIGH_VALUE_KEYWORDS)}`.',
              '',
              f'Total: **{len(hv)}**', '']
    for r in sorted(hv, key=lambda x: x['original_path']):
        tags = ','.join(r['high_value_tags'])
        lines.append(f'- `{r["original_path"]}` [tags: {tags}] '
                     f'(phase={r["phase_guess"]}, topic={r["topic_guess"]})')

    # Possibly repeated by filename
    name_count = Counter(r['filename'].lower() for r in records)
    rep = [n for n, c in name_count.items() if c > 1]
    lines += ['', '## Filenames appearing in multiple locations', '']
    if rep:
        for n in sorted(rep):
            paths = [r['original_path'] for r in records
                     if r['filename'].lower() == n]
            lines.append(f'- `{n}`:')
            for pp in paths:
                lines.append(f'  - `{pp}`')
    else:
        lines.append('_None._')

    # Summary/spec/claim/report/paper-ready catalogue
    lines += ['', '## Files whose names are summary / spec / claim / report '
              '/ paper-ready', '']
    markers = ['summary', 'spec', 'claim', 'report', 'paper_ready',
               'paper-ready']
    for m in markers:
        hits = sorted(r['original_path'] for r in records
                      if m in r['filename'].lower())
        lines.append(f'### `{m}` ({len(hits)})')
        for h in hits:
            lines.append(f'- `{h}`')
        lines.append('')

    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {p}')


def write_merge_map(records):
    p = os.path.join(DEST, '00_manifest', 'merge_map.md')
    lines = ['# Merge Map', '',
             'For each original markdown file, lists every merged document '
             'it was copied into.', '']
    for r in sorted(records, key=lambda x: x['original_path']):
        lines.append(f'## `{r["original_path"]}`')
        lines.append(f'- phase: `{r["phase_guess"]}`  |  topic: '
                     f'`{r["topic_guess"]}`')
        lines.append('- merged into:')
        for m in r['merged_into']:
            lines.append(f'  - `paper_md_bundle/{m}`')
        lines.append('')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {p}')


def write_duplicate_check(records):
    p = os.path.join(DEST, '00_manifest', 'duplicate_check.md')
    dup_name, dup_hash, version_groups = detect_duplicates(records)
    lines = ['# Duplicate Check', '',
             'This report lists filename collisions, exact-content '
             'duplicates, and likely version families. Originals are NOT '
             'deleted or modified.', '']
    lines += ['## Filename collisions across directories', '']
    if dup_name:
        for name, paths in sorted(dup_name.items()):
            lines.append(f'- `{name}`')
            for pp in paths:
                lines.append(f'  - `{pp}`')
    else:
        lines.append('_None._')
    lines += ['', '## Exact-content duplicates', '']
    if dup_hash:
        for g in dup_hash:
            lines.append('- Group:')
            for pp in g:
                lines.append(f'  - `{pp}`')
    else:
        lines.append('_None._')
    lines += ['', '## Possible version families (same stem, different '
              'suffixes such as `_v2`, `_latest`, `_clean`, `_paper_ready`, '
              '`_final`, `_update`)', '']
    if version_groups:
        for stem, fns in sorted(version_groups.items()):
            lines.append(f'- stem `{stem}`: {", ".join(sorted(set(fns)))}')
    else:
        lines.append('_None._')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {p}')


def write_path_index(records):
    p = os.path.join(DEST, '04_original_md_path_index',
                     'original_paths.md')
    lines = ['# Original Markdown Path Index', '',
             'Every scanned markdown file with its original path. Sorted by '
             'path.', '']
    for r in sorted(records, key=lambda x: x['original_path']):
        lines.append(f'- `{r["original_path"]}` '
                     f'(phase={r["phase_guess"]}, topic={r["topic_guess"]}, '
                     f'{r["size_bytes"]} bytes)')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {p}')


if __name__ == '__main__':
    main()
