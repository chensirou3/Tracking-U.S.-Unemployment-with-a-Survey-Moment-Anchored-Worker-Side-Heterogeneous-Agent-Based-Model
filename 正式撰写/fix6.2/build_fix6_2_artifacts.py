"""
Build all tables and figures for Section 6.2 (revised, re-calibrated controls).

Inputs:
  正式撰写/fix6.2/calibration_results.json
  正式撰写/fix6.2/reeval_trajectories.npz
  正式撰写/fix6.2/reeval_metrics.json
  (and legacy 正式撰写/6.2/Results_6_2_Source_of_Advantage_Preparation_Report.md
   for the old vs new comparison row of Table 6)
"""
import os, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path('正式撰写/fix6.2')
TBL  = BASE / 'tables'; TBL.mkdir(exist_ok=True)
FIG  = BASE / 'figures'; FIG.mkdir(exist_ok=True)

with open(BASE / 'calibration_results.json', encoding='utf-8') as f:
    CAL = json.load(f)
with open(BASE / 'reeval_metrics.json', encoding='utf-8') as f:
    RE = json.load(f)
S = np.load(BASE / 'reeval_trajectories.npz', allow_pickle=True)
dates = list(S['dates']); seeds = list(S['seeds'])

# Param-name list (must match calibration script)
from run_fix6_2_calibrate import param_names  # noqa: E402

VARIANTS = ['V_Simplified', 'V_LaborOnly', 'V_Homogeneous', 'V_Full']
LABELS = {
    'V_Full':         'Full heterogeneous ABM',
    'V_Homogeneous':  'Homogeneous ABM',
    'V_LaborOnly':    'Labor-only ABM',
    'V_Simplified':   'Simplified ABM',
}
COLORS = {'V_Simplified': '#CD5C5C', 'V_LaborOnly': '#DAA520',
          'V_Homogeneous': '#4682B4', 'V_Full': '#2E8B57'}


def _rows_by(variant, window, rank=0):
    """Return list of seed-level dicts for given variant/window/rank."""
    return [r for r in RE['variants'][variant]['rows']
            if r['window'] == window and r['rank'] == rank]


def _agg_rmse(variant, window, key='ur', rank=0):
    vals = [r[key]['rmse'] for r in _rows_by(variant, window, rank)
            if not np.isnan(r[key]['rmse'])]
    if not vals:
        return float('nan'), float('nan'), float('nan')
    m = float(np.mean(vals)); s = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    cv = float(s / m * 100) if m else float('nan')
    return m, s, cv


# ------------- Table 1: variant summary on post-COVID normalization ----------
def table1():
    rows = []
    for v in VARIANTS:
        ur_m, ur_sd, ur_cv = _agg_rmse(v, 'post_covid_norm', 'ur')
        lf_m, *_ = _agg_rmse(v, 'post_covid_norm', 'lfpr')
        ep_m, *_ = _agg_rmse(v, 'post_covid_norm', 'epop')
        full_ur, *_ = _agg_rmse(v, 'full_post_2018', 'ur')
        train_loss_mean = CAL[v]['top5_mean'][0]
        rows.append(dict(
            variant=v, label=LABELS[v],
            train_loss_mean_top1=round(train_loss_mean, 4),
            UR_RMSE_post_covid_pp=round(ur_m * 100, 4),
            UR_RMSE_sd_pp=round(ur_sd * 100, 4),
            UR_CV_pct=round(ur_cv, 3),
            LFPR_RMSE_pp=round(lf_m * 100, 4),
            EPOP_RMSE_pp=round(ep_m * 100, 4),
            UR_RMSE_full_post2018_pp=round(full_ur * 100, 4),
        ))
    df = pd.DataFrame(rows)
    df.to_csv(TBL / 'table1_variant_summary.csv', index=False)
    print(df.to_string(index=False))


# ------------- Table 2: top-5 train-loss dispersion within variant ----------
def table2():
    rows = []
    for v in VARIANTS:
        top5 = CAL[v]['top5_mean']
        spread = max(top5) - min(top5)
        cv = float(np.std(top5, ddof=1) / np.mean(top5) * 100) if len(top5) > 1 else 0.0
        for rank, val in enumerate(top5):
            rows.append(dict(variant=v, label=LABELS[v], rank=rank,
                             cand_idx=CAL[v]['top5_idx'][rank],
                             mean_train_loss=round(val, 4),
                             std_train_loss=round(CAL[v]['top5_std'][rank], 4)))
        rows.append(dict(variant=v, label=LABELS[v], rank='spread',
                         cand_idx=None,
                         mean_train_loss=round(spread, 4),
                         std_train_loss=round(cv, 4)))
    pd.DataFrame(rows).to_csv(TBL / 'table2_top5_within_variant.csv', index=False)


# ------------- Table 3: seed-level metrics on post-COVID norm ---------------
def table3():
    rows = []
    for v in VARIANTS:
        for r in _rows_by(v, 'post_covid_norm'):
            rows.append(dict(
                variant=v, label=LABELS[v], seed=r['seed'],
                UR_RMSE_pp=round(r['ur']['rmse'] * 100, 4),
                UR_MAE_pp=round(r['ur']['mae'] * 100, 4),
                UR_corr=round(r['ur']['corr'], 4),
                UR_bias_pp=round(r['ur']['bias'] * 100, 4),
                UR_max_abs_pp=round(r['ur']['max_abs_err'] * 100, 4),
                LFPR_RMSE_pp=round(r['lfpr']['rmse'] * 100, 4),
                EPOP_RMSE_pp=round(r['epop']['rmse'] * 100, 4),
            ))
    pd.DataFrame(rows).to_csv(TBL / 'table3_seed_level_metrics.csv', index=False)


# ------------- Table 4: source-of-advantage decomposition (post-COVID norm) -
def table4():
    rmse = {v: _agg_rmse(v, 'post_covid_norm', 'ur')[0] for v in VARIANTS}
    total = rmse['V_Simplified'] - rmse['V_Full']
    het = rmse['V_Homogeneous'] - rmse['V_Full']
    mech = rmse['V_Simplified'] - rmse['V_Homogeneous']
    hh = rmse['V_LaborOnly'] - rmse['V_Full']
    rows = [
        dict(metric='RMSE_Simplified_pp',  value=round(rmse['V_Simplified']*100, 4)),
        dict(metric='RMSE_LaborOnly_pp',   value=round(rmse['V_LaborOnly']*100, 4)),
        dict(metric='RMSE_Homogeneous_pp', value=round(rmse['V_Homogeneous']*100, 4)),
        dict(metric='RMSE_Full_pp',        value=round(rmse['V_Full']*100, 4)),
        dict(metric='Total_gain_Simplified_minus_Full_pp', value=round(total*100, 4)),
        dict(metric='Mechanism_gain_Simplified_minus_Homogeneous_pp', value=round(mech*100, 4)),
        dict(metric='Heterogeneity_gain_Homogeneous_minus_Full_pp',  value=round(het*100, 4)),
        dict(metric='Household_block_gain_LaborOnly_minus_Full_pp',  value=round(hh*100, 4)),
        dict(metric='Heterogeneity_share_pct',
             value=round(het / total * 100, 2) if total > 0 else float('nan')),
        dict(metric='Mechanism_share_pct',
             value=round(mech / total * 100, 2) if total > 0 else float('nan')),
    ]
    pd.DataFrame(rows).to_csv(TBL / 'table4_source_of_advantage.csv', index=False)


# ------------- Table 5: calibrated parameter vectors per variant -----------
def table5():
    rows = []
    for i, p in enumerate(param_names):
        row = dict(param=p)
        for v in VARIANTS:
            vec = CAL[v]['best_param_vec']
            active = set(CAL[v]['active_params'])
            row[v] = round(vec[i], 4) if p in active else f'(inactive={round(vec[i], 4)})'
        rows.append(row)
    pd.DataFrame(rows).to_csv(TBL / 'table5_calibrated_params.csv', index=False)


# ------------- Table 6: old vs new decomposition ---------------------------
def table6():
    # Read old §6.2 numbers from the legacy preparation report header (hard-coded constants).
    # These are the public claims in 正式撰写/6.2/Results_6_2_Source_of_Advantage_Preparation_Report.md.
    OLD = dict(
        rmse_full_pp=0.214,
        rmse_homog_pp=2.214,
        rmse_simple_pp=2.330,
        rmse_laboronly_pp=0.291,
        total_gain_pp=2.116,
        het_share_pct=97.6,
        mech_share_pct=2.4,
        hh_block_gain_pp=0.077,
        comment='legacy: controls run at default-config / baseline params (NOT separately calibrated)',
    )
    rmse = {v: _agg_rmse(v, 'post_covid_norm', 'ur')[0] for v in VARIANTS}
    total = rmse['V_Simplified'] - rmse['V_Full']
    het = rmse['V_Homogeneous'] - rmse['V_Full']
    mech = rmse['V_Simplified'] - rmse['V_Homogeneous']
    hh = rmse['V_LaborOnly'] - rmse['V_Full']
    NEW = dict(
        rmse_full_pp=round(rmse['V_Full']*100, 4),
        rmse_homog_pp=round(rmse['V_Homogeneous']*100, 4),
        rmse_simple_pp=round(rmse['V_Simplified']*100, 4),
        rmse_laboronly_pp=round(rmse['V_LaborOnly']*100, 4),
        total_gain_pp=round(total*100, 4),
        het_share_pct=round(het/total*100, 2) if total > 0 else float('nan'),
        mech_share_pct=round(mech/total*100, 2) if total > 0 else float('nan'),
        hh_block_gain_pp=round(hh*100, 4),
        comment='new: each variant separately re-calibrated via 100/100/100/30 LHS + 3 seeds',
    )
    rows = []
    for k in OLD:
        rows.append(dict(metric=k, old=OLD[k], new=NEW[k]))
    pd.DataFrame(rows).to_csv(TBL / 'table6_old_vs_new_decomposition.csv', index=False)


# ------------- Table 7: regime × variant UR RMSE ---------------------------
def table7():
    REGS = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm', 'full_post_2018', 'train']
    rows = []
    for w in REGS:
        row = dict(window=w, period=RE['windows'][w]['period'])
        for v in VARIANTS:
            m, sd, cv = _agg_rmse(v, w, 'ur')
            row[f'{v}_RMSE_pp'] = round(m * 100, 4)
            row[f'{v}_sd_pp']   = round(sd * 100, 4)
        rows.append(row)
    pd.DataFrame(rows).to_csv(TBL / 'table7_regime_x_variant.csv', index=False)


# ------------- Figure 1: post-COVID UR RMSE bar ----------------------------
def fig1():
    means = []; sds = []
    for v in VARIANTS:
        m, sd, _ = _agg_rmse(v, 'post_covid_norm', 'ur')
        means.append(m * 100); sds.append(sd * 100)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(len(VARIANTS))
    ax.bar(x, means, yerr=sds, capsize=6, color=[COLORS[v] for v in VARIANTS],
           edgecolor='black', linewidth=0.8)
    for i, (m, sd) in enumerate(zip(means, sds)):
        ax.text(i, m + sd + 0.05, f'{m:.3f}', ha='center', fontsize=10, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels([LABELS[v] for v in VARIANTS], rotation=15, ha='right')
    ax.set_ylabel('UR RMSE (pp), 2022-01..2026-02')
    ax.set_title('Figure 1. Post-COVID normalization UR RMSE — re-calibrated controls')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig1_variant_ur_rmse_bar.png', dpi=150); plt.close(fig)


# ------------- Figure 2: source-of-advantage waterfall ---------------------
def fig2():
    rmse = {v: _agg_rmse(v, 'post_covid_norm', 'ur')[0] * 100 for v in VARIANTS}
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    labels = ['Simplified\n(baseline)', '↓ +Labor\nblock', '↓ +Mechanism\nrichness',
              '↓ +Heterogeneity\n(=Full)']
    vals = [rmse['V_Simplified'], rmse['V_LaborOnly'], rmse['V_Homogeneous'], rmse['V_Full']]
    colors = [COLORS['V_Simplified'], COLORS['V_LaborOnly'], COLORS['V_Homogeneous'], COLORS['V_Full']]
    ax.bar(range(4), vals, color=colors, edgecolor='black')
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f'{v:.3f}', ha='center', fontweight='bold')
    ax.set_xticks(range(4)); ax.set_xticklabels(labels)
    ax.set_ylabel('Post-COVID UR RMSE (pp)')
    ax.set_title('Figure 2. Source of advantage — re-calibrated variants (post-COVID normalization)')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig2_source_of_advantage_waterfall.png', dpi=150); plt.close(fig)


# ------------- Figure 3: UR lines across variants on 2018-2026 -------------
def fig3():
    s, e = 204, 302
    xs = dates[s:e]
    obs = S['target_ur'][s:e] * 100
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(range(len(xs)), obs, 'k-', lw=1.6, label='Observed UNRATE')
    for v in VARIANTS:
        ur = S[f'{v}_ur'][0]  # rank-0 candidate, all seeds
        mean = ur[:, s:e].mean(axis=0) * 100
        ax.plot(range(len(xs)), mean, '-', lw=1.2, color=COLORS[v], label=LABELS[v])
    tick_pos = [i for i, d in enumerate(xs) if d.endswith('-01')]
    ax.set_xticks(tick_pos); ax.set_xticklabels([xs[i] for i in tick_pos], rotation=45, ha='right')
    ax.set_xlabel('Date'); ax.set_ylabel('Unemployment rate (%)')
    ax.set_title('Figure 3. UR trajectories: 4 re-calibrated variants, 2018-01..2026-02')
    ax.legend(loc='upper right', framealpha=0.95); ax.grid(alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig3_variant_ur_lines.png', dpi=150); plt.close(fig)


# ------------- Figure 4: regime × variant UR RMSE heatmap ------------------
def fig4():
    REGS = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm', 'full_post_2018', 'train']
    mat = np.zeros((len(REGS), len(VARIANTS)))
    for i, w in enumerate(REGS):
        for j, v in enumerate(VARIANTS):
            m, *_ = _agg_rmse(v, w, 'ur')
            mat[i, j] = m * 100
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    im = ax.imshow(mat, aspect='auto', cmap='RdYlGn_r')
    for i in range(len(REGS)):
        for j in range(len(VARIANTS)):
            ax.text(j, i, f'{mat[i,j]:.2f}', ha='center', va='center', fontsize=10,
                    color='white' if mat[i,j] > mat.max() * 0.6 else 'black')
    ax.set_xticks(range(len(VARIANTS))); ax.set_xticklabels([LABELS[v] for v in VARIANTS], rotation=15, ha='right')
    ax.set_yticks(range(len(REGS))); ax.set_yticklabels([RE['windows'][w]['period'] for w in REGS])
    ax.set_title('Figure 4. UR RMSE (pp): regime × re-calibrated variant')
    fig.colorbar(im, ax=ax, label='UR RMSE (pp)')
    plt.tight_layout(); fig.savefig(FIG / 'fig4_regime_x_variant_heatmap.png', dpi=150); plt.close(fig)


# ------------- Figure 5: within-variant top-5 dispersion -------------------
def fig5():
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(VARIANTS)); width = 0.15
    for rank in range(5):
        vals = [CAL[v]['top5_mean'][rank] for v in VARIANTS]
        ax.bar(x + (rank - 2) * width, vals, width, label=f'rank {rank}')
    ax.set_xticks(x); ax.set_xticklabels([LABELS[v] for v in VARIANTS], rotation=15, ha='right')
    ax.set_ylabel('Mean train loss (3 seeds)')
    ax.set_title('Figure 5. Top-5 candidate dispersion within each variant (identifiability proxy)')
    ax.legend(loc='best', framealpha=0.95); ax.grid(axis='y', alpha=0.3)
    plt.tight_layout(); fig.savefig(FIG / 'fig5_within_variant_dispersion.png', dpi=150); plt.close(fig)


if __name__ == '__main__':
    table1(); table2(); table3(); table4(); table5(); table6(); table7()
    fig1(); fig2(); fig3(); fig4(); fig5()
    print('All tables and figures written.')
