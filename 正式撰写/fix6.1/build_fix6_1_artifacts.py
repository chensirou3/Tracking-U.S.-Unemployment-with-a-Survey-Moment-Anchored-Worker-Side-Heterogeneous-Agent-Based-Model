"""
Build tables and figures for Section 6.1 (revised, regime-specific).

Inputs:
  正式撰写/fix6.1/regime_metrics.json   (per-seed and per-window metrics)
  正式撰写/fix6.1/regime_series.npz     (5-seed M0_Full trajectories + targets)

Outputs:
  正式撰写/fix6.1/tables/table1_regime_summary.csv
  正式撰写/fix6.1/tables/table2_seed_level_regime.csv
  正式撰写/fix6.1/tables/table3_old_vs_regime_comparison.csv
  正式撰写/fix6.1/figures/fig1_full_period_ur.png
  正式撰写/fix6.1/figures/fig2_regime_ur_rmse_bar.png
  正式撰写/fix6.1/figures/fig3_prediction_error_time.png
  正式撰写/fix6.1/figures/fig4_lfpr_epop_regime_bar.png
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = '正式撰写/fix6.1'
TBL  = os.path.join(BASE, 'tables')
FIG  = os.path.join(BASE, 'figures')
os.makedirs(TBL, exist_ok=True); os.makedirs(FIG, exist_ok=True)

with open(os.path.join(BASE, 'regime_metrics.json'), encoding='utf-8') as f:
    M = json.load(f)
S = np.load(os.path.join(BASE, 'regime_series.npz'))
dates = list(S['dates']); ur = S['ur']; lfpr = S['lfpr']; epop = S['epop']
t_ur = S['target_ur']; t_lfpr = S['target_lfpr']; t_epop = S['target_epop']
seeds = list(S['seeds']); WINS = M['windows']

# Table 1: regime summary (one row per regime; pp units; seed sd / cv)
REGIME_ORDER = ['pre_covid_stable', 'covid_crisis_mar', 'covid_crisis_jan',
                'post_covid_norm', 'full_post_2018']
t1_rows = []
for w in REGIME_ORDER:
    a = WINS[w]['aggregate']
    t1_rows.append({
        'window':         w,
        'label':          WINS[w]['label'],
        'period':         WINS[w]['period'],
        'n_valid':        a['ur']['n_valid'],
        'UR_RMSE_pp':     round(a['ur']['rmse_mean'] * 100, 4),
        'UR_RMSE_sd_pp':  round(a['ur']['rmse_sd']   * 100, 4),
        'UR_MAE_pp':      round(a['ur']['mae_mean']  * 100, 4),
        'UR_corr':        round(a['ur']['corr_mean'], 4),
        'UR_bias_pp':     round(a['ur']['bias_mean'] * 100, 4),
        'UR_max_abs_pp':  round(a['ur']['max_abs_err_mean'] * 100, 4),
        'UR_sim_mean_pp': round(a['ur']['sim_mean_mean'] * 100, 4),
        'UR_obs_mean_pp': round(a['ur']['obs_mean_mean'] * 100, 4),
        'LFPR_RMSE_pp':   round(a['lfpr']['rmse_mean'] * 100, 4),
        'LFPR_bias_pp':   round(a['lfpr']['bias_mean'] * 100, 4),
        'EPOP_RMSE_pp':   round(a['epop']['rmse_mean'] * 100, 4),
        'EPOP_bias_pp':   round(a['epop']['bias_mean'] * 100, 4),
        'seed_CV_pct':    round(a['ur']['rmse_cv'], 3) if not np.isnan(a['ur']['rmse_cv']) else float('nan'),
    })
pd.DataFrame(t1_rows).to_csv(os.path.join(TBL, 'table1_regime_summary.csv'), index=False, encoding='utf-8')

# Table 2: per seed × per regime
t2_rows = []
for w in REGIME_ORDER:
    for seed in seeds:
        b = WINS[w]['seeds'][str(seed)]
        t2_rows.append({
            'window':       w,
            'period':       WINS[w]['period'],
            'seed':         int(seed),
            'UR_RMSE_pp':   round(b['ur']['rmse']        * 100, 4),
            'UR_MAE_pp':    round(b['ur']['mae']         * 100, 4),
            'UR_corr':      round(b['ur']['corr'], 4),
            'UR_bias_pp':   round(b['ur']['bias']        * 100, 4),
            'UR_max_abs_pp':round(b['ur']['max_abs_err'] * 100, 4),
            'LFPR_RMSE_pp': round(b['lfpr']['rmse']      * 100, 4),
            'LFPR_bias_pp': round(b['lfpr']['bias']      * 100, 4),
            'EPOP_RMSE_pp': round(b['epop']['rmse']      * 100, 4),
            'EPOP_bias_pp': round(b['epop']['bias']      * 100, 4),
        })
pd.DataFrame(t2_rows).to_csv(os.path.join(TBL, 'table2_seed_level_regime.csv'), index=False, encoding='utf-8')

# Table 3: old vs regime comparison
INTERP = {
    'train':              'Includes 2008-09 Great Recession; model misses level of crisis',
    'validation':         'Dominated by 2020 COVID shock; large RMSE driven by crisis months',
    'original_oos':       'Post-COVID normalization regime; headline 0.221 pp result',
    'covid_crisis_mar':   'Extreme discontinuity; model cannot replicate 14.7% spike',
    'post_covid_norm':    'Same calendar period as original_oos; the regime the model is built for',
}
t3_rows = []
for w in ['train', 'validation', 'original_oos', 'covid_crisis_mar', 'post_covid_norm']:
    a = WINS[w]['aggregate']
    t3_rows.append({
        'window':        w,
        'period':        WINS[w]['period'],
        'n_valid':       a['ur']['n_valid'],
        'UR_RMSE_pp':    round(a['ur']['rmse_mean'] * 100, 4),
        'UR_corr':       round(a['ur']['corr_mean'], 4),
        'interpretation':INTERP[w],
    })
pd.DataFrame(t3_rows).to_csv(os.path.join(TBL, 'table3_old_vs_regime_comparison.csv'), index=False, encoding='utf-8')

# Figure 1: full-period observed vs simulated UR (2018-01..2026-02 zoom)
def date_idx(d): return dates.index(d) if d in dates else None
s2018 = date_idx('2018-01'); e2026 = date_idx('2026-02') + 1
xs = np.arange(s2018, e2026); xlabels = [dates[i] for i in xs]
sim_mean = ur.mean(axis=0)[s2018:e2026]; sim_sd = ur.std(axis=0)[s2018:e2026]
obs = t_ur[s2018:e2026]
fig, ax = plt.subplots(figsize=(11, 4.5))
# shaded regions
covid_a = date_idx('2020-03') - s2018; covid_b = date_idx('2021-12') - s2018 + 1
norm_a  = date_idx('2022-01') - s2018; norm_b  = date_idx('2026-02') - s2018 + 1
ax.axvspan(covid_a, covid_b, color='#fde2e2', alpha=0.7, label='COVID crisis (2020-03..2021-12)')
ax.axvspan(norm_a,  norm_b,  color='#e2efff', alpha=0.7, label='Post-COVID normalization (2022-01..2026-02)')
ax.plot(np.arange(len(xs)), obs * 100, 'k-', lw=1.5, label='Observed UNRATE')
ax.plot(np.arange(len(xs)), sim_mean * 100, 'C0-', lw=1.3, label='Simulated (mean of 5 seeds)')
ax.fill_between(np.arange(len(xs)), (sim_mean - sim_sd) * 100, (sim_mean + sim_sd) * 100,
                color='C0', alpha=0.20, label='±1 seed sd')
tick_pos = [i for i, d in enumerate(xlabels) if d.endswith('-01')]
ax.set_xticks(tick_pos); ax.set_xticklabels([xlabels[i] for i in tick_pos], rotation=45, ha='right')
ax.set_xlabel('Date'); ax.set_ylabel('Unemployment rate (%)')
ax.set_title('Figure 1. Observed vs simulated UR — heterogeneous ABM, 2018-01..2026-02')
ax.grid(True, alpha=0.3); ax.legend(loc='upper right', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig1_full_period_ur.png'), dpi=160); plt.close(fig)

# Figure 2: regime UR RMSE bar
labels = ['Pre-COVID\nstable', 'COVID crisis\n(Mar 2020 on)', 'Post-COVID\nnormalization', 'Full post-2018']
keys   = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm', 'full_post_2018']
means  = [WINS[k]['aggregate']['ur']['rmse_mean'] * 100 for k in keys]
sds    = [WINS[k]['aggregate']['ur']['rmse_sd']   * 100 for k in keys]
fig, ax = plt.subplots(figsize=(8, 4.5))
colors = ['#7aa6c2', '#d96a6a', '#4f9d69', '#a37fb8']
bars = ax.bar(labels, means, yerr=sds, color=colors, capsize=4, edgecolor='black', linewidth=0.6)
for b, m in zip(bars, means):
    ax.text(b.get_x() + b.get_width() / 2, m + 0.05, f"{m:.3f}", ha='center', va='bottom', fontsize=9)
ax.set_ylabel('UR RMSE (pp)'); ax.set_title('Figure 2. UR RMSE by regime (error bars = seed sd, n=5)')
ax.grid(True, axis='y', alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig2_regime_ur_rmse_bar.png'), dpi=160); plt.close(fig)

# Figure 3: prediction error over time (sim - obs, pp)
err = (ur.mean(axis=0) - t_ur)[s2018:e2026] * 100
err_sd = ur.std(axis=0)[s2018:e2026] * 100
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.axvspan(covid_a, covid_b, color='#fde2e2', alpha=0.7, label='COVID crisis')
ax.axvspan(norm_a,  norm_b,  color='#e2efff', alpha=0.7, label='Post-COVID normalization')
ax.axhline(0, color='black', lw=0.8)
ax.plot(np.arange(len(xs)), err, 'C3-', lw=1.4, label='Mean error (sim − obs)')
ax.fill_between(np.arange(len(xs)), err - err_sd, err + err_sd, color='C3', alpha=0.25, label='±1 seed sd')
ax.set_xticks(tick_pos); ax.set_xticklabels([xlabels[i] for i in tick_pos], rotation=45, ha='right')
ax.set_ylabel('Prediction error UR (pp)'); ax.set_title('Figure 3. Prediction error over time — heterogeneous ABM')
ax.grid(True, alpha=0.3); ax.legend(loc='upper right', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig3_prediction_error_time.png'), dpi=160); plt.close(fig)

# Figure 4: LFPR / EPOP RMSE by regime
lfpr_v = [WINS[k]['aggregate']['lfpr']['rmse_mean'] * 100 for k in keys]
epop_v = [WINS[k]['aggregate']['epop']['rmse_mean'] * 100 for k in keys]
x = np.arange(len(keys)); w = 0.36
fig, ax = plt.subplots(figsize=(8.5, 4.5))
ax.bar(x - w/2, lfpr_v, w, label='LFPR RMSE', color='#7aa6c2', edgecolor='black', linewidth=0.6)
ax.bar(x + w/2, epop_v, w, label='EPOP RMSE', color='#d96a6a', edgecolor='black', linewidth=0.6)
for i, v in enumerate(lfpr_v): ax.text(i - w/2, v + 0.05, f"{v:.2f}", ha='center', va='bottom', fontsize=8)
for i, v in enumerate(epop_v): ax.text(i + w/2, v + 0.05, f"{v:.2f}", ha='center', va='bottom', fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel('RMSE (pp)'); ax.set_title('Figure 4. LFPR / EPOP RMSE by regime')
ax.grid(True, axis='y', alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig4_lfpr_epop_regime_bar.png'), dpi=160); plt.close(fig)

print('Tables and figures written to', BASE)
