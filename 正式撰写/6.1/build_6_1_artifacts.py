"""
Build all Tables (CSV + MD) and Figures (PNG) for paper Section 6.1
from the freshly-regenerated Phase 7 outputs.
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

OUT = '正式撰写/6.1'
TBL = os.path.join(OUT, 'tables')
FIG = os.path.join(OUT, 'figures')
os.makedirs(TBL, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

VERSIONS = ['conservative', 'baseline', 'aggressive']
SEEDS = [42, 137, 2024, 888, 1234]
WINDOWS = ['train', 'val', 'oos']
COLORS = {'conservative': '#2E8B57', 'baseline': '#1f77b4', 'aggressive': '#CD5C5C'}

with open('Phase3_Output/phase7/main_run_metrics.json') as f:
    M = json.load(f)
series = dict(np.load('Phase3_Output/phase7/main_run_series.npz', allow_pickle=True))
dates = list(series['dates'])
T = len(dates)
t_ur, t_lfpr, t_epop = series['target_ur'], series['target_lfpr'], series['target_epop']

INIT_E, TRAIN_E, VAL_E, OOS_E = 36, 204, 252, 302

def pp(x):  # decimal -> percentage points
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else x * 100

def bias(sim, obs, s, e):
    v = ~np.isnan(obs[s:e])
    return float(np.mean((sim[s:e] - obs[s:e])[v]))

def max_abs(sim, obs, s, e):
    v = ~np.isnan(obs[s:e])
    return float(np.max(np.abs(sim[s:e] - obs[s:e])[v]))

# ---------- TABLE 2: full seed-level results ----------
import csv
rows2 = []
for v in VERSIONS:
    for s in SEEDS:
        for w in WINDOWS:
            m = M['all_metrics'][v][str(s)][w]
            s_idx, e_idx = {'train': (INIT_E, TRAIN_E), 'val': (TRAIN_E, VAL_E), 'oos': (VAL_E, OOS_E)}[w]
            sim_ur = series[f'{v}_ur'] if s == 42 else None  # series only stores seed-42 trajectory
            rows2.append({
                'candidate': v, 'seed': s, 'window': w,
                'UR_RMSE_pp': pp(m['ur_rmse']),
                'UR_MAE_pp': pp(m['ur_mae']),
                'UR_corr': m['ur_corr'],
                'UR_mean_sim_pp': pp(m['ur_mean']),
                'LFPR_RMSE_pp': pp(m['lfpr_rmse']),
                'EPOP_RMSE_pp': pp(m['epop_rmse']),
                'EU_mean': m['eu_mean'], 'UE_mean': m['ue_mean'],
                'H2M_mean': m['h2m_mean'], 'cash_buf_mean': m['buf_mean'],
                'unemp_dur_mean': m['dur_mean'],
            })

with open(os.path.join(TBL, 'table2_seed_level.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows2[0].keys()); w.writeheader(); w.writerows(rows2)

# ---------- TABLE 1: candidate × window summary (mean/sd across seeds) ----------
rows1 = []
for v in VERSIONS:
    for w in WINDOWS:
        s = M['summary'][v][w]
        rows1.append({
            'candidate': v, 'window': w,
            'UR_RMSE_pp_mean': pp(s['ur_rmse_mean']),
            'UR_RMSE_pp_sd':   pp(s['ur_rmse_std']),
            'UR_MAE_pp_mean':  pp(s['ur_mae_mean']),
            'UR_corr_mean':    s['ur_corr_mean'],
            'UR_corr_sd':      s['ur_corr_std'],
            'LFPR_RMSE_pp_mean': pp(s['lfpr_rmse_mean']),
            'EPOP_RMSE_pp_mean': pp(s['epop_rmse_mean']),
            'n_seeds': len(SEEDS),
        })
with open(os.path.join(TBL, 'table1_candidate_window_summary.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows1[0].keys()); w.writeheader(); w.writerows(rows1)

# ---------- TABLE 3: OOS detailed per seed ----------
rows3 = []
for v in VERSIONS:
    for s in SEEDS:
        m = M['all_metrics'][v][str(s)]['oos']
        # observed OOS UR mean (BLS)
        obs_mean = float(np.nanmean(t_ur[VAL_E:OOS_E]))
        rows3.append({
            'candidate': v, 'seed': s,
            'UR_mean_sim_pp': pp(m['ur_mean']),
            'UR_mean_obs_pp': pp(obs_mean),
            'UR_bias_pp':     pp(m['ur_mean'] - obs_mean),
            'UR_RMSE_pp':     pp(m['ur_rmse']),
            'UR_MAE_pp':      pp(m['ur_mae']),
            'UR_corr':        m['ur_corr'],
            'LFPR_RMSE_pp':   pp(m['lfpr_rmse']),
            'EPOP_RMSE_pp':   pp(m['epop_rmse']),
        })
with open(os.path.join(TBL, 'table3_oos_detailed.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows3[0].keys()); w.writeheader(); w.writerows(rows3)

# ---------- TABLE 4: baseline 3-window summary ----------
rows4 = []
for w in WINDOWS:
    s = M['summary']['baseline'][w]
    rows4.append({
        'window': w,
        'UR_RMSE_pp_mean': pp(s['ur_rmse_mean']),
        'UR_RMSE_pp_sd':   pp(s['ur_rmse_std']),
        'UR_MAE_pp_mean':  pp(s['ur_mae_mean']),
        'UR_corr_mean':    s['ur_corr_mean'],
        'LFPR_RMSE_pp_mean': pp(s['lfpr_rmse_mean']),
        'EPOP_RMSE_pp_mean': pp(s['epop_rmse_mean']),
    })
with open(os.path.join(TBL, 'table4_baseline_3windows.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows4[0].keys()); w.writeheader(); w.writerows(rows4)

# ---------- TABLE 5: candidate ranking ----------
rank_rows = []
for v in VERSIONS:
    oos = M['summary'][v]['oos']; val = M['summary'][v]['val']
    rank_rows.append({
        'candidate': v,
        'OOS_UR_RMSE_pp': pp(oos['ur_rmse_mean']),
        'OOS_UR_RMSE_sd_pp': pp(oos['ur_rmse_std']),
        'OOS_UR_corr': oos['ur_corr_mean'],
        'VAL_UR_RMSE_pp': pp(val['ur_rmse_mean']),
        'OOS_LFPR_RMSE_pp': pp(oos['lfpr_rmse_mean']),
        'OOS_EPOP_RMSE_pp': pp(oos['epop_rmse_mean']),
        'OOS_UR_CV_pct': 100.0 * oos['ur_rmse_std'] / oos['ur_rmse_mean'] if oos['ur_rmse_mean'] else float('nan'),
    })
with open(os.path.join(TBL, 'table5_candidate_ranking.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rank_rows[0].keys()); w.writeheader(); w.writerows(rank_rows)

print("Tables saved to", TBL)
print("Now generating figures...")

# ---------- Figures ----------
# Need baseline UR trajectory per seed for seed-band figures. Rerun fast.
from Phase3_Code.phase7_engine import run_version, get_targets, load_candidates
env, _, _, _ = get_targets()
versions = load_candidates()
seed_ur = {}        # seed_ur[seed] = baseline_ur trajectory
seed_lfpr = {}
seed_epop = {}
print("Capturing per-seed baseline trajectories (5 seeds)...")
for s in SEEDS:
    h = run_version(versions['baseline']['params'], seed=s, env=env)
    seed_ur[s]   = np.array([x['unemployment_rate'] for x in h])
    seed_lfpr[s] = np.array([x['lfpr'] for x in h])
    seed_epop[s] = np.array([x['epop'] for x in h])
np.savez_compressed(os.path.join(OUT, 'baseline_seed_trajectories.npz'),
                    dates=np.array(dates),
                    **{f'ur_{s}': seed_ur[s] for s in SEEDS},
                    **{f'lfpr_{s}': seed_lfpr[s] for s in SEEDS},
                    **{f'epop_{s}': seed_epop[s] for s in SEEDS})

base_ur_mat   = np.array([seed_ur[s]   for s in SEEDS]) * 100  # pp
base_lfpr_mat = np.array([seed_lfpr[s] for s in SEEDS]) * 100
base_epop_mat = np.array([seed_epop[s] for s in SEEDS]) * 100
base_ur_mean  = base_ur_mat.mean(axis=0)
base_ur_sd    = base_ur_mat.std(axis=0)

months = np.arange(T)
tick_pos = [i for i, d in enumerate(dates) if d.endswith('-01') and int(d[:4]) % 3 == 0]
tick_lab = [dates[i][:4] for i in tick_pos]
obs_ur_pp = t_ur * 100; obs_lfpr_pp = t_lfpr * 100; obs_epop_pp = t_epop * 100

# Fig 1 — OOS UR, baseline vs BLS (with ±1sd seed band)
fig, ax = plt.subplots(figsize=(10, 5))
oos_x = months[VAL_E:OOS_E]
ax.plot(oos_x, obs_ur_pp[VAL_E:OOS_E], 'k-', lw=2.0, label='BLS Actual')
ax.fill_between(oos_x, (base_ur_mean - base_ur_sd)[VAL_E:OOS_E],
                       (base_ur_mean + base_ur_sd)[VAL_E:OOS_E],
                alpha=0.25, color=COLORS['baseline'], label='Baseline ±1sd (5 seeds)')
ax.plot(oos_x, base_ur_mean[VAL_E:OOS_E], '-', color=COLORS['baseline'], lw=1.6, label='Baseline seed mean')
ax.set_xticks([i for i in tick_pos if i >= VAL_E])
ax.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])
ax.set_xlabel('Year'); ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Figure 1 — OOS Unemployment Rate (2022-01 to 2026-02)\nBaseline heterogeneous ABM vs BLS UNRATE')
ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig1_oos_ur_baseline.png'), dpi=150); plt.close()

# Fig 2 — Full period UR with window shading
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(months, obs_ur_pp, 'k-', lw=1.8, label='BLS Actual', zorder=5)
ax.fill_between(months, base_ur_mean - base_ur_sd, base_ur_mean + base_ur_sd,
                alpha=0.20, color=COLORS['baseline'])
ax.plot(months, base_ur_mean, '-', color=COLORS['baseline'], lw=1.3, label='Baseline ABM (seed mean)')
ax.axvspan(0, INIT_E, alpha=0.10, color='gray')
ax.axvspan(TRAIN_E, VAL_E, alpha=0.10, color='gold')
ax.axvspan(VAL_E, OOS_E, alpha=0.15, color='orange')
ax.axvline(INIT_E, color='gray', ls='--', lw=0.7)
ax.axvline(TRAIN_E, color='gray', ls='--', lw=0.7)
ax.axvline(VAL_E,  color='red',  ls='--', lw=1.0)
for xpos, lab in [(INIT_E//2, 'burn-in'), ((INIT_E+TRAIN_E)//2, 'train'),
                  ((TRAIN_E+VAL_E)//2, 'val (COVID)'), ((VAL_E+OOS_E)//2, 'OOS')]:
    ax.text(xpos, ax.get_ylim()[1]*0.92 if False else 14.5, lab, ha='center', fontsize=9, color='dimgray')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab)
ax.set_xlabel('Year'); ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Figure 2 — Full-Period UR: Baseline ABM vs BLS (2001-01 to 2026-02)')
ax.set_ylim(0, 16); ax.legend(loc='upper left'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig2_full_period_ur.png'), dpi=150); plt.close()

# Fig 3 — OOS error over time (sim - obs)
err = base_ur_mean - obs_ur_pp
err_sd = base_ur_sd
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.axhline(0, color='k', lw=0.8)
ax.fill_between(oos_x, (err - err_sd)[VAL_E:OOS_E], (err + err_sd)[VAL_E:OOS_E],
                alpha=0.25, color=COLORS['baseline'])
ax.plot(oos_x, err[VAL_E:OOS_E], '-', color=COLORS['baseline'], lw=1.6, label='Sim - Obs (pp)')
ax.set_xticks([i for i in tick_pos if i >= VAL_E])
ax.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])
ax.set_xlabel('Year'); ax.set_ylabel('UR error (pp): simulated - observed')
ax.set_title('Figure 3 — OOS UR Prediction Error Over Time (baseline, 5 seeds)')
ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig3_oos_error.png'), dpi=150); plt.close()

# Fig 4 — Candidate comparison: OOS UR RMSE bar with seed sd
cand_means = [pp(M['summary'][v]['oos']['ur_rmse_mean']) for v in VERSIONS]
cand_sds   = [pp(M['summary'][v]['oos']['ur_rmse_std'])  for v in VERSIONS]
fig, ax = plt.subplots(figsize=(7, 5))
xp = np.arange(len(VERSIONS))
bars = ax.bar(xp, cand_means, yerr=cand_sds, capsize=5,
              color=[COLORS[v] for v in VERSIONS], edgecolor='black', alpha=0.85)
for i, (m, s) in enumerate(zip(cand_means, cand_sds)):
    ax.text(i, m + s + 0.005, f'{m:.3f}', ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(xp); ax.set_xticklabels(VERSIONS)
ax.set_ylabel('OOS UR RMSE (pp)')
ax.set_title('Figure 4 — Candidate Comparison: OOS UR RMSE (mean ± seed sd, n=5)')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig4_candidate_bar.png'), dpi=150); plt.close()

# Fig 5 — LFPR & EPOP OOS comparison (baseline)
fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
ax = axes[0]
ax.plot(oos_x, obs_lfpr_pp[VAL_E:OOS_E], 'k-', lw=2, label='BLS CIVPART')
ax.fill_between(oos_x, (base_lfpr_mat.mean(0) - base_lfpr_mat.std(0))[VAL_E:OOS_E],
                       (base_lfpr_mat.mean(0) + base_lfpr_mat.std(0))[VAL_E:OOS_E],
                alpha=0.25, color=COLORS['baseline'])
ax.plot(oos_x, base_lfpr_mat.mean(0)[VAL_E:OOS_E], '-', color=COLORS['baseline'], lw=1.5, label='Baseline ABM')
ax.set_title('LFPR (CIVPART)'); ax.set_ylabel('%'); ax.legend(); ax.grid(True, alpha=0.3)
ax.set_xticks([i for i in tick_pos if i >= VAL_E])
ax.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])

ax = axes[1]
ax.plot(oos_x, obs_epop_pp[VAL_E:OOS_E], 'k-', lw=2, label='BLS EMRATIO')
ax.fill_between(oos_x, (base_epop_mat.mean(0) - base_epop_mat.std(0))[VAL_E:OOS_E],
                       (base_epop_mat.mean(0) + base_epop_mat.std(0))[VAL_E:OOS_E],
                alpha=0.25, color=COLORS['baseline'])
ax.plot(oos_x, base_epop_mat.mean(0)[VAL_E:OOS_E], '-', color=COLORS['baseline'], lw=1.5, label='Baseline ABM')
ax.set_title('EPOP (EMRATIO)'); ax.set_ylabel('%'); ax.legend(); ax.grid(True, alpha=0.3)
ax.set_xticks([i for i in tick_pos if i >= VAL_E])
ax.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])
plt.suptitle('Figure 5 — LFPR and EPOP, OOS Window (Baseline ABM vs BLS)')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig5_lfpr_epop_oos.png'), dpi=150); plt.close()

# Fig 6 — Seed stability: per-seed OOS UR paths
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(oos_x, obs_ur_pp[VAL_E:OOS_E], 'k-', lw=2.2, label='BLS Actual', zorder=5)
for s in SEEDS:
    ax.plot(oos_x, (seed_ur[s]*100)[VAL_E:OOS_E], '-', lw=1.0, alpha=0.85, label=f'seed={s}')
ax.set_xticks([i for i in tick_pos if i >= VAL_E])
ax.set_xticklabels([dates[i][:4] for i in tick_pos if i >= VAL_E])
ax.set_xlabel('Year'); ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Figure 6 — Seed Stability: Baseline ABM OOS UR paths (5 seeds)')
ax.legend(loc='upper right', ncol=2, fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig6_seed_stability.png'), dpi=150); plt.close()

print("All figures saved to", FIG)

