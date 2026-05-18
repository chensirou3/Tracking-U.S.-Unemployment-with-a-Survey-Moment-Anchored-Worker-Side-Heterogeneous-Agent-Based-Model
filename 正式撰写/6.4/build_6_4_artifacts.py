"""
Build Section 6.4 tables and figures from benchmark_metrics.json and
benchmark_series.npz, plus the Full heterogeneous ABM 5-seed baseline trajectories
stored in 正式撰写/6.1/baseline_seed_trajectories.npz.
"""
import os, json, csv
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DIR_64 = os.path.join(ROOT, '正式撰写', '6.4')
TBL = os.path.join(DIR_64, 'tables')
FIG = os.path.join(DIR_64, 'figures')
os.makedirs(TBL, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# ---- Load 6.4 benchmark data ----
with open(os.path.join(DIR_64, 'benchmark_metrics.json'), 'r') as f:
    BM = json.load(f)
S = np.load(os.path.join(DIR_64, 'benchmark_series.npz'))

# ---- Load 6.1 Full ABM seed-mean OOS path (5 seeds) ----
B61 = np.load(os.path.join(ROOT, '正式撰写', '6.1', 'baseline_seed_trajectories.npz'))
SEEDS = [42, 137, 2024, 888, 1234]
ur_seeds = np.array([B61[f'ur_{s}'] for s in SEEDS])           # (5, 302) decimal
lfpr_seeds = np.array([B61[f'lfpr_{s}'] for s in SEEDS])
epop_seeds = np.array([B61[f'epop_{s}'] for s in SEEDS])
dates = list(B61['dates'])
VAL_END, OOS_END = 252, 302
oos_idx = np.arange(VAL_END, OOS_END)
oos_dates = dates[VAL_END:OOS_END]

ur_full_mean = ur_seeds[:, VAL_END:OOS_END].mean(axis=0)        # seed-mean over OOS
ur_full_per_seed = ur_seeds[:, VAL_END:OOS_END]

obs_ur = S['obs_ur']                                            # (50,) decimal, with NaN at 2025-10
obs_lfpr = S['obs_lfpr']
obs_epop = S['obs_epop']
valid = ~np.isnan(obs_ur)

def metrics_against_obs(pred, obs):
    v = ~(np.isnan(pred) | np.isnan(obs))
    if v.sum() < 2:
        return {k: float('nan') for k in ['rmse','mae','corr','bias','max_abs_err',
                                            'pred_mean','obs_mean']}
    pv, ov = pred[v], obs[v]
    err = pv - ov
    return {
        'rmse': float(np.sqrt(np.mean(err**2))),
        'mae':  float(np.mean(np.abs(err))),
        'corr': float(np.corrcoef(pv, ov)[0,1]),
        'bias': float(np.mean(err)),
        'max_abs_err': float(np.max(np.abs(err))),
        'pred_mean': float(np.mean(pv)),
        'obs_mean':  float(np.mean(ov)),
    }

# ---- Full ABM per-seed metrics + seed-mean metrics ----
abm_per_seed = []
for i, s in enumerate(SEEDS):
    abm_per_seed.append(metrics_against_obs(ur_full_per_seed[i], obs_ur))
abm_metrics_meanseed = {
    'rmse_mean': float(np.mean([m['rmse'] for m in abm_per_seed])),
    'rmse_std':  float(np.std([m['rmse'] for m in abm_per_seed], ddof=0)),
    'mae_mean':  float(np.mean([m['mae'] for m in abm_per_seed])),
    'corr_mean': float(np.mean([m['corr'] for m in abm_per_seed])),
    'bias_mean': float(np.mean([m['bias'] for m in abm_per_seed])),
    'max_abs_err_mean': float(np.mean([m['max_abs_err'] for m in abm_per_seed])),
}
# Also compute metrics of the seed-mean path
abm_metrics_meanpath = metrics_against_obs(ur_full_mean, obs_ur)

# Pull from 6.2 derived series for LFPR/EPOP RMSE of full ABM (matches 6.2 numbers)
ABM_LFPR_RMSE = 2.2743 / 100  # decimal; from 6.2 table3
ABM_EPOP_RMSE = 2.2141 / 100  # decimal
ABM_LFPR_BIAS = 2.2537 / 100
ABM_EPOP_BIAS = 2.1941 / 100

B_UR = abm_metrics_meanseed['rmse_mean'] * 100  # pp
B_UR_SD = abm_metrics_meanseed['rmse_std'] * 100
B_UR_CORR = abm_metrics_meanseed['corr_mean']
B_UR_BIAS = abm_metrics_meanseed['bias_mean'] * 100

print(f"Full ABM (5-seed): UR RMSE = {B_UR:.4f} pp ± {B_UR_SD:.4f}, "
      f"Corr = {B_UR_CORR:.4f}, bias = {B_UR_BIAS:+.4f} pp")

# Map of benchmark display names
NAMES = {
    'B1_AR':       'AR(1) benchmark',
    'B2_VAR':      'VAR(2) benchmark',
    'B3_Beveridge':'Beveridge benchmark',
    'B4_DMP':      'DMP-style benchmark',
}
TYPES = {
    'B1_AR':       'Univariate AR',
    'B2_VAR':      'Multivariate AR',
    'B3_Beveridge':'Reduced-form OLS',
    'B4_DMP':      'Structural search-matching',
}
OOS_EXOG = {
    'B1_AR':       False,
    'B2_VAR':      False,
    'B3_Beveridge':True,
    'B4_DMP':      True,
}

def write_csv(path, rows):
    if not rows: return
    keys = list(rows[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

# ============================================================
# Table 1 — OOS comparison (paper-leaning, full metric set)
# ============================================================
def pp(x): return x * 100
rows1 = [{
    'model': 'Full heterogeneous ABM',
    'model_type': 'Heterogeneous ABM (5 seeds)',
    'OOS_UR_RMSE_pp': round(B_UR, 4),
    'OOS_UR_RMSE_seed_sd_pp': round(B_UR_SD, 4),
    'OOS_UR_MAE_pp':  round(abm_metrics_meanseed['mae_mean']*100, 4),
    'OOS_UR_corr':    round(B_UR_CORR, 4),
    'OOS_UR_bias_pp': round(B_UR_BIAS, 4),
    'OOS_UR_max_abs_err_pp': round(abm_metrics_meanseed['max_abs_err_mean']*100, 4),
    'RMSE_ratio_vs_full': 1.0,
    'improvement_vs_full_pp': 0.0,
    'interpretation': 'reference (lowest OOS UR RMSE among all models)',
}]
for bk in ['B3_Beveridge', 'B4_DMP', 'B2_VAR', 'B1_AR']:
    m = BM[bk]['ur']
    ratio = m['rmse'] / (B_UR / 100)
    improv = pp(m['rmse']) - B_UR
    rows1.append({
        'model': NAMES[bk],
        'model_type': TYPES[bk],
        'OOS_UR_RMSE_pp': round(pp(m['rmse']), 4),
        'OOS_UR_RMSE_seed_sd_pp': '—',  # deterministic
        'OOS_UR_MAE_pp':  round(pp(m['mae']), 4),
        'OOS_UR_corr':    round(m['corr'], 4),
        'OOS_UR_bias_pp': round(pp(m['bias']), 4),
        'OOS_UR_max_abs_err_pp': round(pp(m['max_abs_err']), 4),
        'RMSE_ratio_vs_full': round(ratio, 3),
        'improvement_vs_full_pp': round(improv, 4),
        'interpretation': '',
    })

# Add interpretation strings post-hoc (we know the ranking now)
def interp(bk, rmse_pp, corr, bias_pp):
    if bk == 'B3_Beveridge':
        return ('strongest external benchmark; tracks co-movement (Corr ' +
                f'{corr:+.2f}) but level RMSE ' + f'{rmse_pp/B_UR:.1f}x worse than full ABM')
    if bk == 'B4_DMP':
        return ('captures matching structure; underpredicts post-COVID UR ' +
                f'(bias {bias_pp:+.2f} pp)')
    if bk == 'B2_VAR':
        return ('negative OOS Corr: multivariate AR extrapolates wrong direction ' +
                'after COVID training-window structural break')
    if bk == 'B1_AR':
        return ('univariate baseline; reverts toward training mean while ' +
                f'observed UR rose (bias {bias_pp:+.2f} pp)')
    return ''
for r in rows1[1:]:
    bk_lookup = {v: k for k, v in NAMES.items()}[r['model']]
    r['interpretation'] = interp(bk_lookup, r['OOS_UR_RMSE_pp'], r['OOS_UR_corr'], r['OOS_UR_bias_pp'])
write_csv(os.path.join(TBL, 'table1_oos_comparison.csv'), rows1)

# ============================================================
# Table 2 — Multi-target results (UR + LFPR + EPOP where applicable)
# ============================================================
rows2 = [{
    'model': 'Full heterogeneous ABM',
    'window': 'OOS 2022-01..2026-02 (49 valid months)',
    'UR_RMSE_pp':  round(B_UR, 4),
    'UR_MAE_pp':   round(abm_metrics_meanseed['mae_mean']*100, 4),
    'UR_corr':     round(B_UR_CORR, 4),
    'UR_bias_pp':  round(B_UR_BIAS, 4),
    'LFPR_RMSE_pp': round(ABM_LFPR_RMSE*100, 4),
    'LFPR_bias_pp': round(ABM_LFPR_BIAS*100, 4),
    'EPOP_RMSE_pp': round(ABM_EPOP_RMSE*100, 4),
    'EPOP_bias_pp': round(ABM_EPOP_BIAS*100, 4),
    'notes': '5-seed mean; LFPR/EPOP from Section 6.2 derived series',
}]
for bk in ['B3_Beveridge', 'B4_DMP', 'B2_VAR', 'B1_AR']:
    bb = BM[bk]
    m = bb['ur']
    row = {
        'model': NAMES[bk],
        'window': 'OOS 2022-01..2026-02 (49 valid months)',
        'UR_RMSE_pp': round(pp(m['rmse']), 4),
        'UR_MAE_pp':  round(pp(m['mae']), 4),
        'UR_corr':    round(m['corr'], 4),
        'UR_bias_pp': round(pp(m['bias']), 4),
        'LFPR_RMSE_pp': '—', 'LFPR_bias_pp': '—',
        'EPOP_RMSE_pp': '—', 'EPOP_bias_pp': '—',
        'notes': '',
    }
    if 'lfpr' in bb:
        row['LFPR_RMSE_pp'] = round(pp(bb['lfpr']['rmse']), 4)
        row['LFPR_bias_pp'] = round(pp(bb['lfpr']['bias']), 4)
        row['EPOP_RMSE_pp'] = round(pp(bb['epop']['rmse']), 4)
        row['EPOP_bias_pp'] = round(pp(bb['epop']['bias']), 4)
        row['notes'] = 'VAR jointly forecasts UR/LFPR/EPOP'
    else:
        row['notes'] = 'UR-only benchmark (LFPR/EPOP not applicable)'
    rows2.append(row)
write_csv(os.path.join(TBL, 'table2_full_window_results.csv'), rows2)
print("Table 2 saved.")

# ============================================================
# Table 3 — Benchmark model specifications
# ============================================================
rows3 = [
    {'model': 'B1 AR',
     'paper_name': 'AR(1) benchmark',
     'formula_method': 'y_t = c + phi*y_{t-1} + eps_t (BIC over {1,2,3,6,12} -> p=1)',
     'input_variables': 'UR only',
     'training_period': '2001-01..2022-01 (252 months, ffilled)',
     'OOS_exog_used': 'No',
     'estimated_parameters': 'c, phi (2)',
     'code_location': 'Phase3_Code/phase8_benchmarks.py:51 ; 6.4/run_6_4_benchmarks.py:71'},
    {'model': 'B2 VAR',
     'paper_name': 'VAR(2) benchmark',
     'formula_method': 'Y_t = c + A1 Y_{t-1} + A2 Y_{t-2} + e_t (BIC over [1..6] -> p=2); Y=(UR,LFPR,EPOP)',
     'input_variables': 'UR, LFPR, EPOP',
     'training_period': '2001-01..2022-01 (252 months, ffilled)',
     'OOS_exog_used': 'No',
     'estimated_parameters': 'c (3) + A1 (9) + A2 (9) = 21',
     'code_location': 'Phase3_Code/phase8_benchmarks.py:73 ; 6.4/run_6_4_benchmarks.py:87'},
    {'model': 'B3 Beveridge',
     'paper_name': 'Beveridge benchmark',
     'formula_method': 'UR_t = a + b1*(1/theta_t) + b2*s_t (OLS, static regression)',
     'input_variables': 'theta=JTSJOR/3 (market tightness), s=JTSLDR/100 (separation rate)',
     'training_period': '2001-01..2022-01 (252 months)',
     'OOS_exog_used': 'Yes (observed JTSJOR and JTSLDR over 2022-01..2026-02)',
     'estimated_parameters': 'a, b1, b2 (3)',
     'code_location': 'Phase3_Code/phase8_benchmarks.py:92 ; 6.4/run_6_4_benchmarks.py:99'},
    {'model': 'B4 DMP',
     'paper_name': 'DMP-style benchmark',
     'formula_method': ('u_{t+1} = u_t + s_t*(1-u_t) - f_t*u_t,  '
                        'f_t = A*theta_t^(1-alpha);  A, alpha fit by Nelder-Mead SSE'),
     'input_variables': 'theta (market tightness), s (separation rate)',
     'training_period': '2001-01..2022-01 (252 months)',
     'OOS_exog_used': 'Yes (observed JTSJOR and JTSLDR over OOS window)',
     'estimated_parameters': 'A, alpha (2)',
     'code_location': 'Phase3_Code/phase8_benchmarks.py:109 ; 6.4/run_6_4_benchmarks.py:108'},
    {'model': 'Full heterogeneous ABM',
     'paper_name': 'Full heterogeneous ABM',
     'formula_method': '100k-agent micro-founded ABM, see Section 6.1',
     'input_variables': 'JTSJOR, JTSLDR, CES, FEDFUNDS + 6 heterogeneity dimensions',
     'training_period': 'calibrated on Train 2004-01..2018-01; Val 2018-01..2022-01',
     'OOS_exog_used': 'Yes (observed JTSJOR/JTSLDR/CES/FEDFUNDS only)',
     'estimated_parameters': '14 baseline parameters (Phase 6 candidate_baseline.json)',
     'code_location': 'Phase3_Code/phase7_engine.py + scheduler.py'},
]
write_csv(os.path.join(TBL, 'table3_benchmark_specs.csv'), rows3)
print("Table 3 saved.")

# ============================================================
# Table 4 — Ranking by OOS UR RMSE
# ============================================================
rank_items = [(NAMES[bk], pp(BM[bk]['ur']['rmse']), BM[bk]['ur']['corr'],
               pp(BM[bk]['ur']['bias']), bk) for bk in BM if bk != 'meta']
rank_items.append(('Full heterogeneous ABM', B_UR, B_UR_CORR, B_UR_BIAS, 'FullABM'))
rank_items.sort(key=lambda r: r[1])
rows4 = []
for i, (n, r, c, bi, _) in enumerate(rank_items, 1):
    if n == 'Full heterogeneous ABM':
        interp_s = 'lowest OOS UR RMSE; structural ABM'
    elif n == 'Beveridge benchmark':
        interp_s = 'strongest external benchmark; uses OOS vacancy/separation'
    elif n == 'DMP-style benchmark':
        interp_s = 'structural matching; under-predicts post-COVID UR'
    elif n == 'VAR(2) benchmark':
        interp_s = 'high Corr magnitude but negative sign; pure-history extrapolation fails'
    else:
        interp_s = 'reversion to training mean; large bias'
    rows4.append({'rank': i, 'model': n,
                  'OOS_UR_RMSE_pp': round(r, 4),
                  'OOS_UR_corr': round(c, 4),
                  'OOS_UR_bias_pp': round(bi, 4),
                  'main_interpretation': interp_s})
write_csv(os.path.join(TBL, 'table4_ranking.csv'), rows4)
print("Table 4 saved.")

# ============================================================
# Table 5 — Paper-ready compact
# ============================================================
order5 = ['Full heterogeneous ABM', 'Beveridge benchmark', 'DMP-style benchmark',
          'VAR(2) benchmark', 'AR(1) benchmark']
def lookup(name):
    if name == 'Full heterogeneous ABM':
        return B_UR, B_UR_CORR
    for bk, n in NAMES.items():
        if n == name:
            return pp(BM[bk]['ur']['rmse']), BM[bk]['ur']['corr']
    raise KeyError(name)
rows5 = []
for n in order5:
    r, c = lookup(n)
    ratio = r / B_UR if n != 'Full heterogeneous ABM' else 1.0
    if n == 'Full heterogeneous ABM':
        interp_s = 'reference'
    elif n == 'Beveridge benchmark':
        interp_s = f'strongest external benchmark; {ratio:.2f}x ABM RMSE'
    elif n == 'DMP-style benchmark':
        interp_s = f'structural matching; {ratio:.2f}x ABM RMSE; high Corr'
    elif n == 'VAR(2) benchmark':
        interp_s = f'multivariate AR; {ratio:.2f}x ABM RMSE; OOS Corr {c:+.2f}'
    else:
        interp_s = f'univariate AR; {ratio:.2f}x ABM RMSE; reverts to mean'
    rows5.append({
        'Model': n,
        'OOS_UR_RMSE_pp': f'{r:.3f}',
        'OOS_UR_Corr':    f'{c:+.3f}',
        'RMSE_ratio_vs_full': f'{ratio:.2f}',
        'Interpretation': interp_s,
    })
write_csv(os.path.join(TBL, 'table5_paper_ready_compact.csv'), rows5)
print("Table 5 saved.")


# ============================================================
# Figures
# ============================================================
plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 200, 'font.size': 10})

# Build OOS arrays
B1 = S['B1_AR_ur']
B2 = S['B2_VAR_ur']
B3 = S['B3_Beveridge_ur']
B4 = S['B4_DMP_ur']
ABM = ur_full_mean  # decimal
OBS = obs_ur

x_idx = np.arange(len(OBS))
xticks_idx = [0, 12, 24, 36, 48]
xticks_labels = [oos_dates[i] if i < len(oos_dates) else '' for i in xticks_idx]

# ---- Figure 1: OOS UR paths overlay ----
fig, ax = plt.subplots(figsize=(8.5, 4.8))
ax.plot(x_idx, OBS * 100, color='black', lw=2.2, label='Observed UNRATE', zorder=10)
ax.plot(x_idx, ABM * 100, color='#1f77b4', lw=2.0, label=f'Full heterogeneous ABM (RMSE {B_UR:.3f} pp)')
ax.plot(x_idx, B3 * 100, color='#2ca02c', lw=1.4, ls='--',
        label=f"Beveridge (RMSE {pp(BM['B3_Beveridge']['ur']['rmse']):.3f} pp)")
ax.plot(x_idx, B4 * 100, color='#ff7f0e', lw=1.4, ls='--',
        label=f"DMP-style (RMSE {pp(BM['B4_DMP']['ur']['rmse']):.3f} pp)")
ax.plot(x_idx, B2 * 100, color='#9467bd', lw=1.2, ls=':',
        label=f"VAR(2) (RMSE {pp(BM['B2_VAR']['ur']['rmse']):.3f} pp)")
ax.plot(x_idx, B1 * 100, color='#8c564b', lw=1.2, ls=':',
        label=f"AR(1) (RMSE {pp(BM['B1_AR']['ur']['rmse']):.3f} pp)")
ax.set_xticks(xticks_idx); ax.set_xticklabels(xticks_labels)
ax.set_ylabel('Unemployment rate (%)'); ax.set_xlabel('OOS month')
ax.set_title('Figure 1 — OOS UR trajectories: full ABM vs four external benchmarks')
ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig1_oos_paths.png')); plt.close()
print("Figure 1 saved.")

# ---- Figure 2: RMSE bar chart (log y) ----
fig, ax = plt.subplots(figsize=(7, 4.5))
labels = ['Full\nABM', 'Beveridge', 'DMP-style', 'VAR(2)', 'AR(1)']
vals = [B_UR,
        pp(BM['B3_Beveridge']['ur']['rmse']),
        pp(BM['B4_DMP']['ur']['rmse']),
        pp(BM['B2_VAR']['ur']['rmse']),
        pp(BM['B1_AR']['ur']['rmse'])]
colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b']
bars = ax.bar(labels, vals, color=colors, edgecolor='black', lw=0.7)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v * 1.04, f'{v:.3f}',
            ha='center', va='bottom', fontsize=9)
ax.set_yscale('log')
ax.set_ylabel('OOS UR RMSE (pp, log)')
ax.set_title('Figure 2 — OOS UR RMSE: full ABM vs external benchmarks')
ax.grid(True, alpha=0.3, axis='y', which='both')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig2_rmse_bar.png')); plt.close()
print("Figure 2 saved.")

# ---- Figure 3: scatter predicted vs observed ----
fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.6), sharey=True)
data_list = [
    (B3, NAMES['B3_Beveridge'], '#2ca02c'),
    (B4, NAMES['B4_DMP'],       '#ff7f0e'),
    (B2, NAMES['B2_VAR'],       '#9467bd'),
    (B1, NAMES['B1_AR'],        '#8c564b'),
]
for ax, (pred, name, col) in zip(axes, data_list):
    v = ~(np.isnan(pred) | np.isnan(OBS))
    p, o = pred[v]*100, OBS[v]*100
    ax.scatter(o, p, s=18, color=col, edgecolor='black', lw=0.4, label='benchmark')
    # ABM scatter (lighter)
    av = ABM[v]*100
    ax.scatter(o, av, s=14, color='#1f77b4', alpha=0.45, marker='x', label='Full ABM')
    lo = min(o.min(), p.min(), av.min()) - 0.3
    hi = max(o.max(), p.max(), av.max()) + 0.3
    ax.plot([lo, hi], [lo, hi], 'k--', lw=0.7, alpha=0.5)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel('Observed UR (%)'); ax.set_title(name)
    ax.grid(True, alpha=0.3)
    if ax is axes[0]:
        ax.set_ylabel('Predicted UR (%)')
        ax.legend(fontsize=7, loc='lower right')
plt.suptitle('Figure 3 — Predicted vs observed OOS UR (benchmark vs full ABM)',
             fontsize=11, y=1.02)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig3_scatter.png'), bbox_inches='tight')
plt.close()
print("Figure 3 saved.")

# ---- Figure 4: residual time series ----
fig, ax = plt.subplots(figsize=(8.5, 4.5))
def res(p): return (p - OBS) * 100
ax.axhline(0, color='black', lw=0.8)
ax.plot(x_idx, res(ABM), color='#1f77b4', lw=2.0, label=f'Full ABM (bias {B_UR_BIAS:+.3f} pp)')
ax.plot(x_idx, res(B3), color='#2ca02c', lw=1.3, ls='--',
        label=f"Beveridge (bias {pp(BM['B3_Beveridge']['ur']['bias']):+.3f} pp)")
ax.plot(x_idx, res(B4), color='#ff7f0e', lw=1.3, ls='--',
        label=f"DMP-style (bias {pp(BM['B4_DMP']['ur']['bias']):+.3f} pp)")
ax.plot(x_idx, res(B2), color='#9467bd', lw=1.1, ls=':',
        label=f"VAR(2) (bias {pp(BM['B2_VAR']['ur']['bias']):+.3f} pp)")
ax.plot(x_idx, res(B1), color='#8c564b', lw=1.1, ls=':',
        label=f"AR(1) (bias {pp(BM['B1_AR']['ur']['bias']):+.3f} pp)")
ax.set_xticks(xticks_idx); ax.set_xticklabels(xticks_labels)
ax.set_xlabel('OOS month'); ax.set_ylabel('Prediction − observed (pp)')
ax.set_title('Figure 4 — OOS UR residuals over time')
ax.legend(fontsize=8, loc='upper left'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig4_residuals.png')); plt.close()
print("Figure 4 saved.")

# ---- Figure 5: RMSE ratio horizontal bar (paper highlight) ----
fig, ax = plt.subplots(figsize=(7.5, 3.8))
names = ['AR(1)', 'VAR(2)', 'DMP-style', 'Beveridge']
ratios = [pp(BM['B1_AR']['ur']['rmse']) / B_UR,
          pp(BM['B2_VAR']['ur']['rmse']) / B_UR,
          pp(BM['B4_DMP']['ur']['rmse']) / B_UR,
          pp(BM['B3_Beveridge']['ur']['rmse']) / B_UR]
cols = ['#8c564b', '#9467bd', '#ff7f0e', '#2ca02c']
bars = ax.barh(names, ratios, color=cols, edgecolor='black', lw=0.7)
ax.axvline(1.0, color='#1f77b4', lw=1.8, ls='--', label='Full ABM = 1.00x')
for b, r in zip(bars, ratios):
    ax.text(r + 0.08, b.get_y() + b.get_height()/2, f'{r:.2f}x',
            va='center', fontsize=9)
ax.set_xlabel('OOS UR RMSE relative to full heterogeneous ABM')
ax.set_title('Figure 5 — RMSE ratio of each benchmark to the full ABM (lower = closer to ABM)')
ax.set_xlim(0, max(ratios) * 1.15)
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig5_rmse_ratio.png')); plt.close()
print("Figure 5 saved.")

print("\nAll Section 6.4 tables and figures generated successfully.")
