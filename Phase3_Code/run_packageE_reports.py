"""
Package E — build 4 markdown reports + claim update from analysis tables.
Must be run AFTER run_packageE_analyze.py and run_packageE_soa.py.
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Phase3_Code.calibration_engine import param_names

OUT = 'Phase3_Output/packageE'
AGG = pd.read_csv(os.path.join(OUT, 'method_aggregated.csv'))
TOP = pd.read_csv(os.path.join(OUT, 'top_k_per_method.csv'))
STAB = pd.read_csv(os.path.join(OUT, 'param_stability.csv'))
OVL = pd.read_csv(os.path.join(OUT, 'param_overlap.csv'))
SOA = pd.read_csv(os.path.join(OUT, 'source_of_advantage_per_method.csv'))
PHASE6_TEST_UR = 0.246  # Package A rank-1 / Phase 6 baseline reference


def report_performance():
    lines = ['# Performance Comparison Report', '']
    lines += ['## Method aggregates', '']
    cols = ['method_id', 'best_train_loss', 'best_val_loss', 'best_test_ur_rmse_pp',
            'top5_train_loss_mean', 'top5_train_loss_std',
            'top5_test_ur_mean', 'top5_test_ur_std', 'total_runtime_min']
    show = AGG[cols].copy().round(4)
    lines.append(show.to_markdown(index=False))
    std = AGG['best_train_loss'].std(ddof=1)
    mean = AGG['best_train_loss'].mean()
    cv_train = std / mean * 100
    std_test = AGG['best_test_ur_rmse_pp'].std(ddof=1)
    mean_test = AGG['best_test_ur_rmse_pp'].mean()
    cv_test = std_test / mean_test * 100
    lines += ['', '## Agreement metrics', '',
              f'- `best_train_loss` across 5 methods: mean={mean:.4f}, std={std:.4f}, CV={cv_train:.2f}%',
              f'- `best_test_ur_rmse_pp` across 5 methods: mean={mean_test:.3f}pp, std={std_test:.3f}pp, CV={cv_test:.2f}%',
              f'- top-5 train_loss_mean range: [{AGG["top5_train_loss_mean"].min():.4f}, {AGG["top5_train_loss_mean"].max():.4f}]',
              '']
    lines += ['## Verdict on `method_agreement_train` threshold (<10% CV -> Case A)',
              f'- CV_train = **{cv_train:.2f}%** -> ' + ('**Case A (loss landscape stable)**' if cv_train < 10 else '**Case B/C**'),
              f'- CV_test  = **{cv_test:.2f}%** -> ' + ('**OOS consistent**' if cv_test < 15 else '**OOS divergent**'),
              '',
              f'## Comparison vs Phase 6 baseline (test UR = {PHASE6_TEST_UR:.3f}pp)']
    for _, row in AGG.iterrows():
        diff = row['best_test_ur_rmse_pp'] - PHASE6_TEST_UR
        lines.append(f'- **{row["method_id"]}**: rank-1 test UR = {row["best_test_ur_rmse_pp"]:.3f}pp '
                     f'({"+%.3f" % diff if diff >= 0 else "-%.3f" % abs(diff)} vs baseline)')
    return '\n'.join(lines)


def report_overlap():
    lines = ['# Parameter Overlap Report', '']
    # Per-param method-spread stats
    lines += ['## Per-parameter cross-method stability', '',
              'Classification: Stable (CV<0.15 in ALL 5 methods), Semi (0.15<=CV<0.40 in all), Unstable (>=0.40 in any).', '']
    rows = []
    for p in param_names:
        s = STAB[STAB.param == p]
        cvmax = s['cv'].max(); cvmin = s['cv'].min()
        if s['cv'].max() < 0.15:
            cls = 'Stable'
        elif cvmax < 0.40:
            cls = 'Semi-stable'
        else:
            cls = 'Unstable'
        rows.append({'param': p, 'cv_min': round(cvmin, 3), 'cv_max': round(cvmax, 3),
                     'band_max_norm': round(s['normalized_band'].max(), 3),
                     'classification': cls})
    tbl = pd.DataFrame(rows)
    lines.append(tbl.to_markdown(index=False))
    stable_n = (tbl.classification == 'Stable').sum()
    semi_n = (tbl.classification == 'Semi-stable').sum()
    unst_n = (tbl.classification == 'Unstable').sum()
    lines += ['', '## Summary',
              f'- Stable params: {stable_n} / 14',
              f'- Semi-stable: {semi_n} / 14',
              f'- Unstable: {unst_n} / 14', '']
    # Pairwise overlap aggregate
    lines += ['## Mean pairwise band overlap (aggregated over 14 params)', '']
    pair_mean = OVL.groupby(['method_a', 'method_b'])['overlap_frac'].mean().reset_index()
    pair_mean['overlap_frac'] = pair_mean['overlap_frac'].round(3)
    lines.append(pair_mean.to_markdown(index=False))
    lines += ['', f'**Average overlap across all 10 method-pairs: {OVL["overlap_frac"].mean():.3f}**']
    return '\n'.join(lines)


def report_soa():
    lines = ['# Source-of-Advantage Report', '',
             'For each method rank-1 candidate (params optimised by that method), we re-run '
             'D1 (homogeneous flatten) and D3 (no household outer ring) on Test [252, 302) '
             'with 3 seeds {42, 137, 2024}. share_het = (D1 - M0) / D1 measures how much of '
             'the M0 advantage is attributable to heterogeneity.', '']
    lines.append(SOA.round(3).to_markdown(index=False))
    het_mean = SOA['share_heterogeneity_pct'].mean()
    het_std = SOA['share_heterogeneity_pct'].std(ddof=1)
    hh_mean = SOA['share_household_pct'].mean()
    hh_std = SOA['share_household_pct'].std(ddof=1)
    lines += ['', '## Stability across methods',
              f'- share_heterogeneity: mean={het_mean:.2f}%, std={het_std:.2f}%  '
              f'({"STABLE" if het_std < 5 else "UNSTABLE"} vs 5pp threshold)',
              f'- share_household: mean={hh_mean:.2f}%, std={hh_std:.2f}%  '
              f'({"STABLE" if hh_std < 5 else "UNSTABLE"} vs 5pp threshold)', '']
    return '\n'.join(lines)


def report_cost():
    lines = ['# Cost-Benefit Report', '']
    cb = AGG[['method_id', 'best_train_loss', 'best_test_ur_rmse_pp', 'mean_runtime_s',
              'total_runtime_min']].copy().round(3)
    lines.append(cb.to_markdown(index=False))
    best = AGG.loc[AGG['best_train_loss'].idxmin()]
    cheapest = AGG.loc[AGG['total_runtime_min'].idxmin()]
    lines += ['', '## Highlights',
              f'- Lowest train_loss: **{best["method_id"]}** at {best["best_train_loss"]:.4f} '
              f'({best["total_runtime_min"]:.1f} min)',
              f'- Cheapest wall time: **{cheapest["method_id"]}** at {cheapest["total_runtime_min"]:.1f} min',
              f'- All methods spent: {AGG["total_runtime_min"].sum():.1f} min', '']
    return '\n'.join(lines)


def claim_md():
    cv_train = AGG['best_train_loss'].std(ddof=1) / AGG['best_train_loss'].mean() * 100
    cv_test = AGG['best_test_ur_rmse_pp'].std(ddof=1) / AGG['best_test_ur_rmse_pp'].mean() * 100
    stab_tbl = STAB.pivot_table(index='param', columns='method_id', values='cv')
    unst = int((stab_tbl.max(axis=1) >= 0.40).sum())
    het_std = SOA['share_heterogeneity_pct'].std(ddof=1)
    case = 'A' if (cv_train < 10 and cv_test < 15 and unst <= 2 and het_std < 5) else ('B' if cv_train < 20 else 'C')
    return (
        '# Package E Claim Update\n\n'
        f'- 5 calibration methods x 200 evals x 3 seeds = 3,000 simulations run on identical '
        f'Phase 5 priors, identical loss and identical population.\n'
        f'- `best_train_loss` CV across methods = **{cv_train:.2f}%** ({"<10% -> method-invariant" if cv_train < 10 else ">=10%"})\n'
        f'- `best_test_ur_rmse_pp` CV across methods = **{cv_test:.2f}%**\n'
        f'- Unstable parameters (top-5 CV >= 0.40 in any method): **{unst} / 14**\n'
        f'- `share_heterogeneity` across methods: std = **{het_std:.2f}pp** '
        f'({"stable" if het_std < 5 else "unstable"})\n'
        f'- **Case verdict: {case}**\n'
    )


def main():
    with open(os.path.join(OUT, 'performance_comparison_report.md'), 'w', encoding='utf-8') as f:
        f.write(report_performance())
    with open(os.path.join(OUT, 'parameter_overlap_report.md'), 'w', encoding='utf-8') as f:
        f.write(report_overlap())
    with open(os.path.join(OUT, 'source_of_advantage_report.md'), 'w', encoding='utf-8') as f:
        f.write(report_soa())
    with open(os.path.join(OUT, 'cost_benefit_report.md'), 'w', encoding='utf-8') as f:
        f.write(report_cost())
    with open(os.path.join(OUT, 'packageE_claim_update.md'), 'w', encoding='utf-8') as f:
        f.write(claim_md())
    print('5 reports saved.')


if __name__ == '__main__':
    main()
