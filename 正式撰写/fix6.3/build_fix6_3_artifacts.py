"""
Build tables and figures for Section 6.3 (recalibrated single-dimension ablation).

Inputs:
  正式撰写/fix6.3/calibration_results.json   (6 new ablation variants)
  正式撰写/fix6.3/reeval_metrics.json
  正式撰写/fix6.3/reeval_trajectories.npz
  正式撰写/fix6.2/calibration_results.json   (V_Full reused)
  正式撰写/fix6.2/reeval_metrics.json
  正式撰写/fix6.2/reeval_trajectories.npz
"""
import os, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE63 = Path('正式撰写/fix6.3')
BASE62 = Path('正式撰写/fix6.2')
TBL = BASE63 / 'tables'; TBL.mkdir(exist_ok=True)
FIG = BASE63 / 'figures'; FIG.mkdir(exist_ok=True)

with open(BASE63 / 'calibration_results.json', encoding='utf-8') as f:
    CAL63 = json.load(f)
with open(BASE63 / 'reeval_metrics.json', encoding='utf-8') as f:
    RE63 = json.load(f)
with open(BASE62 / 'calibration_results.json', encoding='utf-8') as f:
    CAL62 = json.load(f)
with open(BASE62 / 'reeval_metrics.json', encoding='utf-8') as f:
    RE62 = json.load(f)
S63 = np.load(BASE63 / 'reeval_trajectories.npz', allow_pickle=True)
S62 = np.load(BASE62 / 'reeval_trajectories.npz', allow_pickle=True)

# Variant order for display and reference. V_Full first (reference), then ablations.
VARIANTS = ['V_Full', 'V_NoSearch', 'V_NoLiquidity', 'V_NoHousing',
            'V_NoSLH', 'V_NoConsumption', 'V_SearchOnly']
LABELS = {
    'V_Full':          'Full heterogeneous ABM',
    'V_NoSearch':      'No Search Friction ABM',
    'V_NoLiquidity':   'No Liquidity Fragility ABM',
    'V_NoHousing':     'No Housing Mobility ABM',
    'V_NoSLH':         'No Search-Liquidity-Housing ABM',
    'V_NoConsumption': 'No Consumption Rule ABM',
    'V_SearchOnly':    'Search-only heterogeneity ABM',
}
FLATTEN = {
    'V_Full':          [],
    'V_NoSearch':      ['search'],
    'V_NoLiquidity':   ['liquidity'],
    'V_NoHousing':     ['housing'],
    'V_NoSLH':         ['search', 'liquidity', 'housing'],
    'V_NoConsumption': ['consumption_rule'],
    'V_SearchOnly':    ['liquidity', 'housing'],
}
COLORS = {
    'V_Full':          '#2E8B57',
    'V_NoSearch':      '#CD5C5C',
    'V_NoLiquidity':   '#4682B4',
    'V_NoHousing':     '#DAA520',
    'V_NoSLH':         '#8B0000',
    'V_NoConsumption': '#9370DB',
    'V_SearchOnly':    '#FF8C00',
}


def _re(variant):
    return RE62 if variant == 'V_Full' else RE63

def _cal(variant):
    return CAL62 if variant == 'V_Full' else CAL63

def _traj(variant, key):
    src = S62 if variant == 'V_Full' else S63
    return src[f'{variant}_{key}']


def _rows_by(variant, window, rank=0):
    return [r for r in _re(variant)['variants'][variant]['rows']
            if r['window'] == window and r['rank'] == rank]


def _agg_rmse(variant, window, key='ur', rank=0):
    vals = [r[key]['rmse'] for r in _rows_by(variant, window, rank)
            if not np.isnan(r[key]['rmse'])]
    if not vals:
        return float('nan'), float('nan'), float('nan')
    m = float(np.mean(vals))
    s = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    cv = float(s / m * 100) if m else float('nan')
    return m, s, cv


def _agg_metric(variant, window, key='ur', stat='corr', rank=0):
    vals = [r[key][stat] for r in _rows_by(variant, window, rank)
            if not (isinstance(r[key][stat], float) and np.isnan(r[key][stat]))]
    if not vals:
        return float('nan')
    return float(np.mean(vals))


def _delta_pp(variant, window='post_covid_norm'):
    full, *_ = _agg_rmse('V_Full', window, 'ur')
    v, *_ = _agg_rmse(variant, window, 'ur')
    return (v - full) * 100


# ----- Table 1: calibration summary per variant -----
def table1():
    rows = []
    for v in VARIANTS:
        cal = _cal(v)
        active = cal[v]['active_params']
        n_draws = cal[v].get('n_draws', '?')
        best_train = cal[v]['top5_mean'][0]
        ur_train_pp = _agg_rmse(v, 'train', 'ur')[0] * 100
        ur_val_pp = _agg_rmse(v, 'pre_covid_stable', 'ur')[0] * 100
        rows.append(dict(
            variant=v, label=LABELS[v],
            flattened='+'.join(FLATTEN[v]) if FLATTEN[v] else '(none)',
            n_active_dims=6 - len(FLATTEN[v]),
            n_parameters=len(active),
            calibration_budget=f'{n_draws} LHS x 3 seeds',
            best_train_loss_top1=round(best_train, 4),
            train_UR_RMSE_pp=round(ur_train_pp, 4),
            preCOVID_UR_RMSE_pp=round(ur_val_pp, 4),
            selected_cand_idx=cal[v]['top5_idx'][0],
        ))
    pd.DataFrame(rows).to_csv(TBL / 'table1_calibration_summary.csv', index=False)


# ----- Table 2 / 3 / 4: regime-specific ablation tables -----
def _regime_table(window, fname):
    full_rmse, *_ = _agg_rmse('V_Full', window, 'ur')
    rows = []
    for v in VARIANTS:
        m, sd, _ = _agg_rmse(v, window, 'ur')
        lf, *_ = _agg_rmse(v, window, 'lfpr')
        ep, *_ = _agg_rmse(v, window, 'epop')
        corr = _agg_metric(v, window, 'ur', 'corr')
        bias = _agg_metric(v, window, 'ur', 'bias')
        delta = (m - full_rmse) * 100
        if v == 'V_Full':
            interp = '(reference)'
        elif delta < -0.02:
            interp = 'improves on Full'
        elif delta < 0.05:
            interp = 'comparable to Full'
        elif delta < 0.2:
            interp = 'mild degradation'
        else:
            interp = 'substantial degradation'
        rows.append(dict(
            variant=v, label=LABELS[v],
            UR_RMSE_pp=round(m * 100, 4),
            UR_sd_pp=round(sd * 100, 4),
            Delta_vs_Full_pp=round(delta, 4),
            UR_Corr=round(corr, 3),
            UR_Bias_pp=round(bias * 100, 4),
            LFPR_RMSE_pp=round(lf * 100, 4),
            EPOP_RMSE_pp=round(ep * 100, 4),
            interpretation=interp,
        ))
    pd.DataFrame(rows).to_csv(TBL / fname, index=False)


def table2(): _regime_table('post_covid_norm', 'table2_post_covid_ablation.csv')
def table3(): _regime_table('covid_crisis_mar', 'table3_crisis_ablation.csv')
def table4(): _regime_table('pre_covid_stable', 'table4_precovid_ablation.csv')


# ----- Table 5: old raw vs new recalibrated delta -----
def table5():
    # Old raw deltas from phase7 ablation_results.json (baseline params, single-dim flatten).
    # Baseline full: 0.0022100 (OOS UR RMSE), so deltas in pp.
    OLD = {
        'V_NoSearch':      0.889,   # ablation 'search'
        'V_NoLiquidity':   0.299,   # ablation 'liquidity'
        'V_NoHousing':     0.162,   # ablation 'housing' (paper used 0.162; phase7 raw = 0.19)
        'V_NoConsumption': 0.040,   # ablation 'consumption_rule'
    }
    full_new, *_ = _agg_rmse('V_Full', 'post_covid_norm', 'ur')
    rows = []
    for v in VARIANTS:
        if v == 'V_Full':
            continue
        new_m, *_ = _agg_rmse(v, 'post_covid_norm', 'ur')
        new_delta = (new_m - full_new) * 100
        old_delta = OLD.get(v, float('nan'))
        if np.isnan(old_delta):
            reduction = 'N/A (new variant)'
            interp = 'no legacy counterpart'
        else:
            reduction = round(old_delta - new_delta, 3)
            if old_delta > 0.1 and new_delta < old_delta * 0.4:
                interp = 'recalibration largely closes the gap'
            elif new_delta > 0.1 and new_delta > old_delta * 0.6:
                interp = 'gap survives recalibration'
            elif new_delta < 0:
                interp = 'sign flip after recalibration'
            else:
                interp = 'moderate reduction'
        rows.append(dict(
            variant=v, label=LABELS[v],
            old_raw_delta_pp=old_delta if not np.isnan(old_delta) else None,
            new_recalibrated_delta_pp=round(new_delta, 4),
            delta_reduction_pp=reduction,
            interpretation=interp,
        ))
    pd.DataFrame(rows).to_csv(TBL / 'table5_old_vs_new_delta.csv', index=False)


# ----- Table 6: regime x ablation heatmap data -----
def table6():
    REGS = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm',
            'full_post_2018', 'train']
    rows = []
    for w in REGS:
        row = dict(window=w, period=_re(VARIANTS[0])['windows'][w]['period'])
        for v in VARIANTS:
            m, sd, _ = _agg_rmse(v, w, 'ur')
            row[f'{v}_RMSE_pp'] = round(m * 100, 4)
            row[f'{v}_sd_pp'] = round(sd * 100, 4)
        rows.append(row)
    pd.DataFrame(rows).to_csv(TBL / 'table6_regime_x_ablation.csv', index=False)


# ----- Table 7: paper-ready compact -----
def table7():
    full_rmse, *_ = _agg_rmse('V_Full', 'post_covid_norm', 'ur')
    PAPER_ORDER = ['V_Full', 'V_NoSearch', 'V_NoLiquidity', 'V_NoHousing', 'V_NoSLH']
    rows = []
    for v in PAPER_ORDER:
        m, sd, _ = _agg_rmse(v, 'post_covid_norm', 'ur')
        delta = (m - full_rmse) * 100
        if v == 'V_Full':
            note = 'reference'
        elif delta < 0:
            note = 'matches or beats Full after recalibration'
        elif delta < 0.05:
            note = 'within seed noise of Full'
        elif delta < 0.15:
            note = 'mild loss from removing this dimension'
        else:
            note = 'dimension is structurally hard to replace'
        rows.append(dict(
            model=LABELS[v],
            OOS_UR_RMSE_pp=round(m * 100, 4),
            seed_sd_pp=round(sd * 100, 4),
            Delta_vs_Full_pp=round(delta, 4),
            interpretation=note,
        ))
    pd.DataFrame(rows).to_csv(TBL / 'table7_paper_ready.csv', index=False)


# ----- Figure 1: post-COVID UR RMSE bar -----
def fig1():
    PAPER_ORDER = ['V_Full', 'V_NoSearch', 'V_NoLiquidity', 'V_NoHousing', 'V_NoSLH']
    means = []; sds = []
    for v in PAPER_ORDER:
        m, sd, _ = _agg_rmse(v, 'post_covid_norm', 'ur')
        means.append(m * 100); sds.append(sd * 100)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x = np.arange(len(PAPER_ORDER))
    ax.bar(x, means, yerr=sds, capsize=6,
           color=[COLORS[v] for v in PAPER_ORDER],
           edgecolor='black', linewidth=0.8)
    for i, (m, sd) in enumerate(zip(means, sds)):
        ax.text(i, m + sd + 0.02, f'{m:.3f}', ha='center', fontsize=10, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels([LABELS[v] for v in PAPER_ORDER], rotation=15, ha='right')
    ax.set_ylabel('UR RMSE (pp), 2022-01..2026-02')
    ax.set_title('Figure 1. Post-COVID normalization UR RMSE — recalibrated ablations')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig1_recalibrated_ablation_ur.png', dpi=150); plt.close(fig)


# ----- Figure 2: old raw delta vs new recalibrated delta -----
def fig2():
    DIMS = ['V_NoSearch', 'V_NoLiquidity', 'V_NoHousing']
    OLD = {'V_NoSearch': 0.889, 'V_NoLiquidity': 0.299, 'V_NoHousing': 0.162}
    full_new, *_ = _agg_rmse('V_Full', 'post_covid_norm', 'ur')
    new_deltas = [(_agg_rmse(v, 'post_covid_norm', 'ur')[0] - full_new) * 100 for v in DIMS]
    old_deltas = [OLD[v] for v in DIMS]
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    x = np.arange(len(DIMS)); w = 0.38
    b1 = ax.bar(x - w/2, old_deltas, w, label='Old (raw ablation, no recal.)',
                color='#999999', edgecolor='black')
    b2 = ax.bar(x + w/2, new_deltas, w, label='New (recalibrated)',
                color='#2E8B57', edgecolor='black')
    for bars in (b1, b2):
        for r in bars:
            h = r.get_height()
            ax.text(r.get_x() + r.get_width()/2, h + 0.02,
                    f'{h:+.3f}', ha='center', fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(['Search', 'Liquidity', 'Housing'])
    ax.set_ylabel('Δ UR RMSE vs Full (pp)')
    ax.set_title('Figure 2. Old raw ablation vs new recalibrated ablation (post-COVID norm.)')
    ax.legend(loc='upper right'); ax.grid(axis='y', alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig2_old_vs_new_delta.png', dpi=150); plt.close(fig)


# ----- Figure 3: regime x ablation heatmap -----
def fig3():
    REGS = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm',
            'full_post_2018', 'train']
    mat = np.zeros((len(REGS), len(VARIANTS)))
    for i, w in enumerate(REGS):
        for j, v in enumerate(VARIANTS):
            m, *_ = _agg_rmse(v, w, 'ur')
            mat[i, j] = m * 100
    fig, ax = plt.subplots(figsize=(10.0, 5.0))
    im = ax.imshow(mat, aspect='auto', cmap='RdYlGn_r')
    for i in range(len(REGS)):
        for j in range(len(VARIANTS)):
            ax.text(j, i, f'{mat[i,j]:.2f}', ha='center', va='center', fontsize=9,
                    color='white' if mat[i,j] > mat.max() * 0.6 else 'black')
    ax.set_xticks(range(len(VARIANTS))); ax.set_xticklabels([LABELS[v] for v in VARIANTS],
                                                            rotation=20, ha='right', fontsize=8)
    ax.set_yticks(range(len(REGS)))
    ax.set_yticklabels([_re(VARIANTS[0])['windows'][w]['period'] for w in REGS])
    ax.set_title('Figure 3. UR RMSE (pp): regime × recalibrated ablation')
    fig.colorbar(im, ax=ax, label='UR RMSE (pp)')
    plt.tight_layout(); fig.savefig(FIG / 'fig3_regime_x_ablation_heatmap.png', dpi=150); plt.close(fig)


# ----- Figure 4: Full vs No-Search trajectory across 2018-2026 -----
def fig4():
    dates62 = list(S62['dates']); dates63 = list(S63['dates'])
    assert dates62 == dates63
    s, e = 204, 302
    xs = dates62[s:e]
    obs = S62['target_ur'][s:e] * 100
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.plot(range(len(xs)), obs, 'k-', lw=1.7, label='Observed UNRATE')
    for v in ['V_Full', 'V_NoSearch']:
        ur = _traj(v, 'ur')[0]
        mean = ur[:, s:e].mean(axis=0) * 100
        sd_band = ur[:, s:e].std(axis=0) * 100
        ax.plot(range(len(xs)), mean, '-', lw=1.4, color=COLORS[v], label=LABELS[v])
        ax.fill_between(range(len(xs)), mean - sd_band, mean + sd_band,
                        color=COLORS[v], alpha=0.18)
    tick_pos = [i for i, d in enumerate(xs) if d.endswith('-01')]
    ax.set_xticks(tick_pos); ax.set_xticklabels([xs[i] for i in tick_pos],
                                                rotation=45, ha='right')
    ax.set_xlabel('Date'); ax.set_ylabel('Unemployment rate (%)')
    ax.set_title('Figure 4. Full vs No-Search trajectories, 2018-01..2026-02 (5-seed mean ± sd)')
    ax.axvspan(xs.index('2020-03'), xs.index('2021-12'), color='red', alpha=0.07,
               label='COVID crisis')
    ax.axvspan(xs.index('2022-01'), len(xs) - 1, color='green', alpha=0.07,
               label='Post-COVID norm.')
    ax.legend(loc='upper right', framealpha=0.95); ax.grid(alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig4_no_search_trajectory.png', dpi=150); plt.close(fig)


# ----- Figure 5: LFPR / EPOP / UR tradeoff per variant -----
def fig5():
    metrics = ['ur', 'lfpr', 'epop']
    titles = ['UR RMSE (pp)', 'LFPR RMSE (pp)', 'EPOP RMSE (pp)']
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.5))
    for ax, key, title in zip(axes, metrics, titles):
        vals = []; sds = []
        for v in VARIANTS:
            m, sd, _ = _agg_rmse(v, 'post_covid_norm', key)
            vals.append(m * 100); sds.append(sd * 100)
        x = np.arange(len(VARIANTS))
        ax.bar(x, vals, yerr=sds, capsize=4,
               color=[COLORS[v] for v in VARIANTS], edgecolor='black', linewidth=0.6)
        ax.set_xticks(x); ax.set_xticklabels([LABELS[v].replace(' ABM', '') for v in VARIANTS],
                                             rotation=30, ha='right', fontsize=7)
        ax.set_ylabel(title); ax.grid(axis='y', alpha=0.3)
        ax.set_title(title)
    fig.suptitle('Figure 5. UR / LFPR / EPOP trade-off across recalibrated ablations (post-COVID)')
    plt.tight_layout(); fig.savefig(FIG / 'fig5_lfpr_epop_tradeoff.png', dpi=150); plt.close(fig)


if __name__ == '__main__':
    table1(); table2(); table3(); table4(); table5(); table6(); table7()
    fig1(); fig2(); fig3(); fig4(); fig5()
    print('Tables and figures written.')
