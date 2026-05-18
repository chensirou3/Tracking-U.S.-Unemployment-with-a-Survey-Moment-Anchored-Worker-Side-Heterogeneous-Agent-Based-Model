"""
Build Tables (CSV) and Figures (PNG) for paper Section 6.2 from the
freshly-regenerated Phase 8 derived-control outputs.
"""
import os, sys, json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

OUT = '正式撰写/6.2'
TBL = os.path.join(OUT, 'tables')
FIG = os.path.join(OUT, 'figures')
os.makedirs(TBL, exist_ok=True); os.makedirs(FIG, exist_ok=True)

with open(os.path.join(OUT, 'derived_metrics.json'), encoding='utf-8') as f:
    D = json.load(f)
series = dict(np.load(os.path.join(OUT, 'derived_series.npz'), allow_pickle=True))
dates = list(series['dates'])
t_ur = series['target_ur']; t_lfpr = series['target_lfpr']; t_epop = series['target_epop']

SEEDS = D['seeds']
VARIANTS = D['variants']  # M0_Full, D1_Homogeneous, D2_Simplified, D3_LaborOnly
WINDOWS = ['train', 'val', 'oos']
INIT_E, TRAIN_E, VAL_E, OOS_E = 36, 204, 252, 302
WIN_IDX = {'train': (INIT_E, TRAIN_E), 'val': (TRAIN_E, VAL_E), 'oos': (VAL_E, OOS_E)}

PAPER_NAMES = {
    'M0_Full':        'Full heterogeneous ABM',
    'D1_Homogeneous': 'Homogeneous ABM',
    'D2_Simplified':  'Simplified ABM',
    'D3_LaborOnly':   'Labor-only ABM',
}
COLORS = {'M0_Full': '#1f77b4', 'D1_Homogeneous': '#ff7f0e',
          'D2_Simplified': '#7f7f7f', 'D3_LaborOnly': '#2ca02c'}

def pp(x):
    if x is None or (isinstance(x, float) and np.isnan(x)): return float('nan')
    return x * 100

def bias(sim, obs, s, e):
    v = ~np.isnan(obs[s:e])
    return float(np.mean((sim[s:e] - obs[s:e])[v]))

def max_abs(sim, obs, s, e):
    v = ~np.isnan(obs[s:e])
    return float(np.max(np.abs(sim[s:e] - obs[s:e])[v]))

def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

# ---------- TABLE 1: per variant × window summary ----------
rows1 = []
for v in VARIANTS:
    for w in WINDOWS:
        s = D['summary'][v][w]
        rows1.append({
            'model_variant': PAPER_NAMES[v], 'code': v, 'window': w,
            'UR_RMSE_pp_mean': round(pp(s['ur_rmse_mean']), 4),
            'UR_RMSE_pp_sd':   round(pp(s['ur_rmse_std']),  4),
            'UR_MAE_pp_mean':  round(pp(s['ur_mae_mean']),  4),
            'UR_corr_mean':    round(s['ur_corr_mean'], 4),
            'UR_corr_sd':      round(s['ur_corr_std'],  4),
            'LFPR_RMSE_pp_mean': round(pp(s['lfpr_rmse_mean']), 4),
            'EPOP_RMSE_pp_mean': round(pp(s['epop_rmse_mean']), 4),
            'n_seeds': len(SEEDS),
        })
write_csv(os.path.join(TBL, 'table1_summary_by_window.csv'), rows1)

# ---------- TABLE 2: per seed, full breakdown ----------
rows2 = []
for v in VARIANTS:
    ur_mat = series[f'{v}_ur']; lfpr_mat = series[f'{v}_lfpr']; epop_mat = series[f'{v}_epop']
    for i, sd in enumerate(SEEDS):
        for w in WINDOWS:
            m = D['all_metrics'][v][str(sd)][w]
            s_i, e_i = WIN_IDX[w]
            ur_b   = bias(ur_mat[i],   t_ur,   s_i, e_i)
            lfpr_b = bias(lfpr_mat[i], t_lfpr, s_i, e_i)
            epop_b = bias(epop_mat[i], t_epop, s_i, e_i)
            ur_max = max_abs(ur_mat[i], t_ur, s_i, e_i)
            rows2.append({
                'model_variant': PAPER_NAMES[v], 'code': v, 'seed': sd, 'window': w,
                'UR_RMSE_pp':  round(pp(m['ur_rmse']), 4),
                'UR_MAE_pp':   round(pp(m['ur_mae']), 4),
                'UR_corr':     round(m['ur_corr'], 4),
                'UR_bias_pp':  round(pp(ur_b), 4),
                'UR_maxabs_pp':round(pp(ur_max), 4),
                'UR_sim_mean_pp': round(pp(m['ur_mean']), 4),
                'LFPR_RMSE_pp':round(pp(m['lfpr_rmse']), 4),
                'LFPR_bias_pp':round(pp(lfpr_b), 4),
                'EPOP_RMSE_pp':round(pp(m['epop_rmse']), 4),
                'EPOP_bias_pp':round(pp(epop_b), 4),
                'EU_mean': round(m['eu_mean'], 5),
                'UE_mean': round(m['ue_mean'], 5),
                'H2M_mean':round(m['h2m_mean'], 4),
                'buf_mean':round(m['buf_mean'], 3),
            })
write_csv(os.path.join(TBL, 'table2_seed_level.csv'), rows2)

# ---------- TABLE 3: OOS comparison (mean across seeds) ----------
rows3 = []
for v in VARIANTS:
    s = D['summary'][v]['oos']
    ur_mat = series[f'{v}_ur']
    lfpr_mat = series[f'{v}_lfpr']
    epop_mat = series[f'{v}_epop']
    biases_ur   = [bias(ur_mat[i],   t_ur,   VAL_E, OOS_E) for i in range(len(SEEDS))]
    biases_lfpr = [bias(lfpr_mat[i], t_lfpr, VAL_E, OOS_E) for i in range(len(SEEDS))]
    biases_epop = [bias(epop_mat[i], t_epop, VAL_E, OOS_E) for i in range(len(SEEDS))]
    rows3.append({
        'model_variant': PAPER_NAMES[v], 'code': v,
        'UR_RMSE_pp_mean': round(pp(s['ur_rmse_mean']), 4),
        'UR_RMSE_pp_sd':   round(pp(s['ur_rmse_std']),  4),
        'UR_MAE_pp_mean':  round(pp(s['ur_mae_mean']),  4),
        'UR_corr_mean':    round(s['ur_corr_mean'], 4),
        'UR_bias_pp_mean': round(pp(float(np.mean(biases_ur))), 4),
        'LFPR_RMSE_pp_mean': round(pp(s['lfpr_rmse_mean']), 4),
        'LFPR_bias_pp_mean': round(pp(float(np.mean(biases_lfpr))), 4),
        'EPOP_RMSE_pp_mean': round(pp(s['epop_rmse_mean']), 4),
        'EPOP_bias_pp_mean': round(pp(float(np.mean(biases_epop))), 4),
        'UR_seed_CV_pct':  round(100 * s['ur_rmse_std'] / s['ur_rmse_mean'], 2) if s['ur_rmse_mean'] else float('nan'),
    })
write_csv(os.path.join(TBL, 'table3_oos_comparison.csv'), rows3)

# ---------- TABLE 4: Source-of-Advantage decomposition ----------
m0 = pp(D['summary']['M0_Full']['oos']['ur_rmse_mean'])
d1 = pp(D['summary']['D1_Homogeneous']['oos']['ur_rmse_mean'])
d2 = pp(D['summary']['D2_Simplified']['oos']['ur_rmse_mean'])
d3 = pp(D['summary']['D3_LaborOnly']['oos']['ur_rmse_mean'])
total_gain = d2 - m0
mech_gain  = d2 - d1
het_gain   = d1 - m0
hh_gain    = d3 - m0
het_share = 100 * het_gain / total_gain if total_gain > 0 else float('nan')
mech_share = 100 * mech_gain / total_gain if total_gain > 0 else float('nan')

rows4 = [
    {'row': 'Full heterogeneous ABM',  'definition': 'M0 baseline: full heterogeneity + full mechanism layer + household block',
     'value_pp': round(m0, 4), 'share_percent': '', 'interpretation': 'lowest OOS UR RMSE, reference point'},
    {'row': 'Homogeneous ABM',         'definition': 'D1: heterogeneity flattened, mechanisms + household block kept',
     'value_pp': round(d1, 4), 'share_percent': '', 'interpretation': 'isolates the contribution of heterogeneity'},
    {'row': 'Simplified ABM',          'definition': 'D2: heterogeneity flattened AND advanced mechanisms disabled; matching kept',
     'value_pp': round(d2, 4), 'share_percent': '', 'interpretation': 'minimal internal baseline'},
    {'row': 'Labor-only ABM',          'definition': 'D3: full heterogeneity, household block disabled',
     'value_pp': round(d3, 4), 'share_percent': '', 'interpretation': 'isolates the contribution of the household block on UR'},
    {'row': 'Total Gain',              'definition': 'Simplified - Full (OOS UR RMSE, pp)',
     'value_pp': round(total_gain, 4), 'share_percent': 100.0, 'interpretation': 'gain delivered by going from minimal to full model'},
    {'row': 'Mechanism Gain',          'definition': 'Simplified - Homogeneous (pp)',
     'value_pp': round(mech_gain, 4), 'share_percent': round(mech_share, 1), 'interpretation': 'gain from adding mechanism layer alone (no heterogeneity)'},
    {'row': 'Heterogeneity Gain',      'definition': 'Homogeneous - Full (pp)',
     'value_pp': round(het_gain, 4), 'share_percent': round(het_share, 1), 'interpretation': 'gain from adding 6-dim heterogeneity on top of full mechanisms'},
    {'row': 'Household Gain (on UR)',  'definition': 'LaborOnly - Full (pp)',
     'value_pp': round(hh_gain, 4), 'share_percent': '', 'interpretation': 'effect of household block on UR; +ve means household block helps UR'},
]
write_csv(os.path.join(TBL, 'table4_source_of_advantage.csv'), rows4)

# ---------- TABLE 5: paper-ready compact ----------
rows5 = []
order = ['M0_Full', 'D3_LaborOnly', 'D1_Homogeneous', 'D2_Simplified']
interp = {
    'M0_Full': 'Best UR; moderate LFPR/EPOP miss (level bias)',
    'D3_LaborOnly': 'Worse UR; sharply better LFPR/EPOP -> trade-off',
    'D1_Homogeneous': 'UR RMSE ~2.5x; LFPR/EPOP much worse',
    'D2_Simplified': 'Minimal baseline; matches Homogeneous on UR but worst LFPR/EPOP',
}
for v in order:
    s = D['summary'][v]['oos']
    rows5.append({
        'model_variant': PAPER_NAMES[v],
        'OOS_UR_RMSE_pp':   round(pp(s['ur_rmse_mean']), 3),
        'OOS_UR_Corr':      round(s['ur_corr_mean'], 3),
        'OOS_LFPR_RMSE_pp': round(pp(s['lfpr_rmse_mean']), 2),
        'OOS_EPOP_RMSE_pp': round(pp(s['epop_rmse_mean']), 2),
        'Main_interpretation': interp[v],
    })
write_csv(os.path.join(TBL, 'table5_paper_ready_compact.csv'), rows5)

print("Tables saved to", TBL)

# ============================================================
# FIGURES
# ============================================================
months = np.arange(OOS_E)
tick_pos = [i for i, d in enumerate(dates) if d.endswith('-01') and int(d[:4]) % 3 == 0]
tick_lab = [dates[i][:4] for i in tick_pos]
obs_ur_pp   = t_ur   * 100
obs_lfpr_pp = t_lfpr * 100
obs_epop_pp = t_epop * 100

# Per-variant OOS UR RMSE mean and sd (in pp)
oos_means_pp = {v: pp(D['summary'][v]['oos']['ur_rmse_mean']) for v in VARIANTS}
oos_sds_pp   = {v: pp(D['summary'][v]['oos']['ur_rmse_std'])  for v in VARIANTS}

# ----- Figure 1: derived-control OOS UR RMSE bar -----
order_fig1 = ['M0_Full', 'D3_LaborOnly', 'D1_Homogeneous', 'D2_Simplified']
xp = np.arange(len(order_fig1))
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(xp, [oos_means_pp[v] for v in order_fig1],
              yerr=[oos_sds_pp[v] for v in order_fig1],
              capsize=5,
              color=[COLORS[v] for v in order_fig1],
              edgecolor='black', alpha=0.85)
for i, v in enumerate(order_fig1):
    ax.text(i, oos_means_pp[v] + oos_sds_pp[v] + 0.012,
            f'{oos_means_pp[v]:.3f}', ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(xp)
ax.set_xticklabels([PAPER_NAMES[v] for v in order_fig1], rotation=12, ha='right', fontsize=9)
ax.set_ylabel('OOS UR RMSE (pp)')
ax.set_title('Figure 1 — Derived-control OOS UR RMSE\n(mean ± seed sd, 5 seeds, OOS = 2022-01..2026-02)')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig1_oos_ur_rmse_bar.png'), dpi=150); plt.close()

# ----- Figure 2: Source-of-advantage waterfall -----
fig, ax = plt.subplots(figsize=(9, 5))
bar_x = [0, 1, 2]
bar_h = [d2, d1, m0]
bar_l = ['Simplified ABM\n(D2)', 'Homogeneous ABM\n(D1)', 'Full heterogeneous ABM\n(M0)']
ax.bar(bar_x, bar_h, color=[COLORS['D2_Simplified'], COLORS['D1_Homogeneous'], COLORS['M0_Full']],
       edgecolor='black', alpha=0.85, width=0.55)
for x, h in zip(bar_x, bar_h):
    ax.text(x, h + 0.012, f'{h:.3f} pp', ha='center', fontweight='bold')
# Annotate gains as arrows
ax.annotate('', xy=(1, d1), xytext=(0, d2), arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
ax.text(0.5, (d1+d2)/2, f'Mechanism Gain\n{mech_gain:+.3f} pp\nshare = {mech_share:.1f}%',
        ha='center', va='center', fontsize=9, color='black',
        bbox=dict(facecolor='white', edgecolor='black', alpha=0.85))
ax.annotate('', xy=(2, m0), xytext=(1, d1), arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
ax.text(1.5, (d1+m0)/2, f'Heterogeneity Gain\n{het_gain:+.3f} pp\nshare = {het_share:.1f}%',
        ha='center', va='center', fontsize=9, color='black',
        bbox=dict(facecolor='white', edgecolor='black', alpha=0.85))
ax.set_xticks(bar_x); ax.set_xticklabels(bar_l, fontsize=9)
ax.set_ylabel('OOS UR RMSE (pp)')
ax.set_title(f'Figure 2 — Source-of-Advantage Waterfall (OOS UR RMSE)\nTotal Gain = {total_gain:.3f} pp')
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, max(d2, d1, m0) * 1.25)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig2_source_of_advantage_waterfall.png'), dpi=150); plt.close()

# ----- Figure 3: Actual vs simulated UR, OOS, all variants (seed mean) -----
oos_x = months[VAL_E:OOS_E]
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(oos_x, obs_ur_pp[VAL_E:OOS_E], 'k-', lw=2.2, label='BLS Actual', zorder=10)
for v in order_fig1:
    sm = series[f'{v}_ur'].mean(axis=0) * 100
    ax.plot(oos_x, sm[VAL_E:OOS_E], '-', lw=1.5, color=COLORS[v], label=PAPER_NAMES[v])
ax.set_xticks([i for i in tick_pos if i >= VAL_E])
ax.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])
ax.set_xlabel('Year'); ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Figure 3 — OOS Unemployment Rate: BLS vs Derived-Control Model Variants\n(seed mean, 5 seeds, 2022-01..2026-02)')
ax.legend(loc='upper right', fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig3_oos_ur_lines.png'), dpi=150); plt.close()

# ----- Figure 4: grouped bars (UR / LFPR / EPOP RMSE), OOS -----
metrics_groups = ['UR', 'LFPR', 'EPOP']
group_means = {v: [pp(D['summary'][v]['oos']['ur_rmse_mean']),
                   pp(D['summary'][v]['oos']['lfpr_rmse_mean']),
                   pp(D['summary'][v]['oos']['epop_rmse_mean'])] for v in order_fig1}
group_sds   = {v: [pp(D['summary'][v]['oos']['ur_rmse_std']),
                   pp(D['summary'][v]['oos']['lfpr_rmse_std']),
                   pp(D['summary'][v]['oos']['epop_rmse_std'])] for v in order_fig1}
xg = np.arange(len(metrics_groups))
bw = 0.20
fig, ax = plt.subplots(figsize=(10, 5))
for i, v in enumerate(order_fig1):
    ax.bar(xg + (i - 1.5) * bw, group_means[v], width=bw,
           yerr=group_sds[v], capsize=3, color=COLORS[v],
           edgecolor='black', alpha=0.85, label=PAPER_NAMES[v])
ax.set_xticks(xg); ax.set_xticklabels(metrics_groups)
ax.set_ylabel('OOS RMSE (pp)')
ax.set_title('Figure 4 — OOS RMSE: UR vs LFPR vs EPOP across model variants\n(mean ± seed sd, 5 seeds)')
ax.set_yscale('log')
ax.legend(loc='upper left', fontsize=9); ax.grid(True, alpha=0.3, which='both', axis='y')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig4_ur_lfpr_epop_grouped.png'), dpi=150); plt.close()

# ----- Figure 5: Full vs Labor-only — UR / LFPR / EPOP series in OOS -----
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax_i, (k, t_arr, ylab) in enumerate([('ur', obs_ur_pp, 'UR (%)'),
                                          ('lfpr', obs_lfpr_pp, 'LFPR (%)'),
                                          ('epop', obs_epop_pp, 'EPOP (%)')]):
    axx = axes[ax_i]
    axx.plot(oos_x, t_arr[VAL_E:OOS_E], 'k-', lw=2, label='BLS Actual')
    for v in ['M0_Full', 'D3_LaborOnly']:
        sm = series[f'{v}_{k}'].mean(axis=0) * 100
        axx.plot(oos_x, sm[VAL_E:OOS_E], '-', lw=1.6, color=COLORS[v], label=PAPER_NAMES[v])
    axx.set_xticks([i for i in tick_pos if i >= VAL_E])
    axx.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])
    axx.set_ylabel(ylab); axx.legend(fontsize=8); axx.grid(True, alpha=0.3)
plt.suptitle('Figure 5 — Household-block trade-off: Full vs Labor-only ABM (OOS window)', y=1.02)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig5_household_tradeoff.png'), dpi=150, bbox_inches='tight'); plt.close()

print("Figures saved to", FIG)
