"""
Package A Step 4: 5 figures.
fig1_per_split_rmse.png     - UR RMSE heatmap (splits x models)
fig2_ranking_distribution.png - ranking boxplot per model
fig3_source_of_advantage.png  - stacked bars per split (het/mech/hh)
fig4_parameter_drift.png      - CV bar chart + trajectories
fig5_test_ur_trajectory.png   - M0 vs best benchmark on each split test window
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('Phase3_Output/packageA', exist_ok=True)

with open('Phase3_Output/packageA/stability_report.json') as f:
    rep = json.load(f)
with open('Phase3_Output/packageA/split_best_params.json') as f:
    cal = json.load(f)

SPLITS = rep['splits']
MODELS = rep['models']
PARAMS = cal['param_names']

# Build RMSE matrix (splits x models)
rmse_mat = np.full((len(SPLITS), len(MODELS)), np.nan)
for i, sid in enumerate(SPLITS):
    row = next(r for r in rep['comparison_table_pp'] if r['split'] == sid)
    for j, m in enumerate(MODELS):
        rmse_mat[i, j] = row[m]

# --------- FIG 1: heatmap ---------
fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(rmse_mat, aspect='auto', cmap='RdYlGn_r',
               vmin=0, vmax=min(3.0, np.nanmax(rmse_mat)))
ax.set_xticks(range(len(MODELS))); ax.set_xticklabels(MODELS, rotation=35, ha='right')
ax.set_yticks(range(len(SPLITS))); ax.set_yticklabels(SPLITS)
for i in range(len(SPLITS)):
    for j in range(len(MODELS)):
        v = rmse_mat[i, j]
        if not np.isnan(v):
            ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                    color='white' if v > 1.5 else 'black', fontsize=8)
plt.colorbar(im, label='UR RMSE (pp)')
ax.set_title('Per-Split Test UR RMSE (pp) across 10 splits x 8 models')
plt.tight_layout()
plt.savefig('Phase3_Output/packageA/fig1_per_split_rmse.png', dpi=120)
plt.close()

# --------- FIG 2: ranking distribution ---------
rank_data = {m: [rep['ranking'][m]['per_split'][s] for s in SPLITS] for m in MODELS}
fig, ax = plt.subplots(figsize=(11, 5))
positions = np.arange(len(MODELS))
bp = ax.boxplot([rank_data[m] for m in MODELS], positions=positions, widths=0.6,
                patch_artist=True, showmeans=True)
for patch, m in zip(bp['boxes'], MODELS):
    if m.startswith('M0'): patch.set_facecolor('#2E7D32'); patch.set_alpha(0.75)
    elif m.startswith('D'): patch.set_facecolor('#1976D2'); patch.set_alpha(0.6)
    else: patch.set_facecolor('#9E9E9E'); patch.set_alpha(0.6)
# Overlay mean rank as scatter
for j, m in enumerate(MODELS):
    mr = rep['ranking'][m]['mean_rank']
    ax.plot(j, mr, 'ro', markersize=7)
    ax.text(j, 9, f"#1={rep['ranking'][m]['n_rank1']}", ha='center', fontsize=8)
ax.set_xticks(positions); ax.set_xticklabels(MODELS, rotation=35, ha='right')
ax.set_ylim(0.5, 9.5); ax.invert_yaxis()
ax.set_ylabel('Rank across splits (1 = best)')
ax.set_title('Ranking Distribution across 10 Splits')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('Phase3_Output/packageA/fig2_ranking_distribution.png', dpi=120)
plt.close()

# --------- FIG 3: source-of-advantage per split ---------
soa = rep['source_of_advantage']
het_vals = []; mech_vals = []; split_ids = []
for sid in SPLITS:
    if soa[sid] is None: continue
    het_vals.append(soa[sid]['delta_het_pp'])
    mech_vals.append(soa[sid]['delta_mech_pp'])
    split_ids.append(sid)
x = np.arange(len(split_ids))
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(x, het_vals, label='Δ Heterogeneity (D1-M0)', color='#2E7D32', alpha=0.8)
ax.bar(x, mech_vals, bottom=het_vals, label='Δ Mechanism (D2-D1)', color='#F9A825', alpha=0.8)
ax.axhline(0, color='k', lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(split_ids)
ax.set_ylabel('UR RMSE reduction (pp)')
ax.set_title('Source-of-Advantage Decomposition: Heterogeneity vs Mechanism, per Split')
ax.legend()
ax.grid(axis='y', alpha=0.3)
for xi, (h, m) in enumerate(zip(het_vals, mech_vals)):
    ax.text(xi, max(h+m, 0.05), f'{h+m:.2f}', ha='center', fontsize=8)
plt.tight_layout()
plt.savefig('Phase3_Output/packageA/fig3_source_of_advantage.png', dpi=120)
plt.close()

# --------- FIG 4: parameter drift ---------
drift = rep['parameter_drift']
cvs = np.array([drift[p]['cv'] for p in PARAMS])
order = np.argsort(cvs)
names_sorted = [PARAMS[i] for i in order]
cvs_sorted = cvs[order]
colors = ['#2E7D32' if c < 0.1 else ('#F9A825' if c < 0.3 else '#C62828') for c in cvs_sorted]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(np.arange(len(names_sorted)), cvs_sorted, color=colors)
ax.axvline(0.1, color='k', ls='--', lw=0.7, label='stable threshold (0.10)')
ax.axvline(0.3, color='r', ls='--', lw=0.7, label='significant drift (0.30)')
ax.set_yticks(np.arange(len(names_sorted))); ax.set_yticklabels(names_sorted)
ax.set_xlabel('Coefficient of Variation across splits')
ax.set_title('Parameter Drift across 10 Splits (lower = more stable)')
ax.legend()
plt.tight_layout()
plt.savefig('Phase3_Output/packageA/fig4_parameter_drift.png', dpi=120)
plt.close()

# --------- FIG 5: M0 vs best benchmark trajectories ---------
data = np.load('Phase3_Output/packageA/packageA_test_series.npz')
dates_all = np.arange(302)
fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharey=False)
for ax, sid in zip(axes.flat, SPLITS):
    test = cal['splits'][sid]['test']
    months = np.arange(test[0], test[1])
    years = 2001 + months / 12
    tgt = data[f'{sid}_ur_target']
    m0 = data[f'{sid}_M0_Main']
    d1 = data[f'{sid}_D1_Homogeneous']
    bev = data[f'{sid}_B3_Beveridge']
    ax.plot(years, tgt * 100, 'k-', lw=1.8, label='BLS UR')
    ax.plot(years, m0 * 100, 'g-', lw=1.2, label='M0')
    ax.plot(years, d1 * 100, 'b--', lw=1, label='D1 Homog')
    ax.plot(years, bev * 100, 'r:', lw=1, label='Beveridge')
    ax.set_title(f"{sid} ({cal['splits'][sid]['type']})", fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_ylabel('UR (%)', fontsize=9)
axes[0,0].legend(fontsize=8, loc='upper right')
plt.suptitle('Test-window UR trajectories: M0 vs D1 vs Beveridge (across 10 splits)')
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('Phase3_Output/packageA/fig5_test_ur_trajectories.png', dpi=120)
plt.close()

print("Saved 5 figures to Phase3_Output/packageA/")
