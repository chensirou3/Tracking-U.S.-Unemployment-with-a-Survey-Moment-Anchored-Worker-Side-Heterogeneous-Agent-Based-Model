"""Package D: five plots."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT = 'Phase3_Output/packageD'
plt.rcParams['figure.dpi'] = 110

df = pd.read_csv(f'{OUT}/agent_count_results.csv')
agg = df.groupby(['mode', 'N', 'model']).agg(
    ur_mean=('ur_rmse_pp', 'mean'), ur_std=('ur_rmse_pp', 'std'),
    lfpr_mean=('lfpr_rmse_pp', 'mean'), lfpr_std=('lfpr_rmse_pp', 'std'),
    epop_mean=('epop_rmse_pp', 'mean'), epop_std=('epop_rmse_pp', 'std'),
    runtime=('runtime_s', 'mean'), mem=('peak_mem_mb', 'mean'),
).reset_index()

MODELS = ['M0', 'D1', 'D2', 'D3']
COLORS = {'M0': '#c73e1d', 'D1': '#2e86ab', 'D2': '#7a9e9f', 'D3': '#e1a96b'}
MODE_LS = {'regenerate': '-', 'subsample': '--'}


def _plot_by_model(metric_mean, metric_std, title, ylabel, fname, legend_loc='upper right'):
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for mode in ['regenerate', 'subsample']:
        for m in MODELS:
            sub = agg[(agg['mode'] == mode) & (agg['model'] == m)].sort_values('N')
            ax.errorbar(sub['N'], sub[metric_mean], yerr=sub[metric_std],
                        fmt='o' + MODE_LS[mode], color=COLORS[m],
                        label=f'{m} ({mode})' if mode == 'regenerate' else None,
                        capsize=3, lw=2 if mode == 'regenerate' else 1.2, alpha=0.95 if mode == 'regenerate' else 0.55)
    ax.set_xscale('log')
    ax.set_xlabel('Agent count N (log scale)')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc=legend_loc, ncol=2)
    plt.tight_layout()
    plt.savefig(f'{OUT}/{fname}', dpi=150)
    plt.close()


# fig1: UR RMSE
_plot_by_model('ur_mean', 'ur_std',
               'Test UR RMSE vs Agent Count (2022-2026)',
               'UR RMSE (pp)', 'fig1_count_ur_rmse.png')

# fig2: Aux (LFPR + EPOP)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5), sharex=True)
for ax, mean_k, std_k, title in [(ax1, 'lfpr_mean', 'lfpr_std', 'LFPR RMSE'),
                                  (ax2, 'epop_mean', 'epop_std', 'EPOP RMSE')]:
    for mode in ['regenerate', 'subsample']:
        for m in MODELS:
            sub = agg[(agg['mode']==mode) & (agg['model']==m)].sort_values('N')
            ax.errorbar(sub['N'], sub[mean_k], yerr=sub[std_k],
                        fmt='o' + MODE_LS[mode], color=COLORS[m],
                        label=f'{m} ({mode})' if mode=='regenerate' else None,
                        capsize=3, lw=2 if mode=='regenerate' else 1.2,
                        alpha=0.95 if mode=='regenerate' else 0.55)
    ax.set_xscale('log')
    ax.set_xlabel('Agent count N')
    ax.set_ylabel(f'{title} (pp)')
    ax.set_title(title)
    ax.grid(alpha=0.3)
ax1.legend(loc='upper right', fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(f'{OUT}/fig2_count_aux_rmse.png', dpi=150)
plt.close()

# fig3: Seed std (log-log)
fig, ax = plt.subplots(figsize=(8.5, 5))
for mode in ['regenerate', 'subsample']:
    for m in MODELS:
        sub = agg[(agg['mode']==mode) & (agg['model']==m)].sort_values('N')
        if mode == 'subsample':
            sub = sub[sub['N'] <= 100000]   # subsample caps at 100k source
        ax.loglog(sub['N'], sub['ur_std'], 'o' + MODE_LS[mode], color=COLORS[m],
                  label=f'{m} ({mode})' if mode=='regenerate' else None,
                  lw=2 if mode=='regenerate' else 1.2,
                  alpha=0.95 if mode=='regenerate' else 0.55)
Ns = np.array([5000, 300000])
ref_vals = 0.06 * (Ns / 5000) ** (-0.5)
ax.loglog(Ns, ref_vals, 'k:', alpha=0.6, label='√N reference (α=-0.5)')
ax.set_xlabel('Agent count N (log)')
ax.set_ylabel('UR RMSE seed std (pp, log)')
ax.set_title('Monte Carlo Noise Scaling')
ax.grid(alpha=0.3, which='both')
ax.legend(loc='upper right', fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(f'{OUT}/fig3_count_seed_std.png', dpi=150)
plt.close()

# fig4: Runtime + Memory
fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()
for m in MODELS:
    sub = agg[(agg['mode']=='regenerate') & (agg['model']==m)].sort_values('N')
    ax1.loglog(sub['N'], sub['runtime'], 'o-', color=COLORS[m], label=f'{m} runtime', lw=2)
    ax2.loglog(sub['N'], sub['mem'], 's--', color=COLORS[m], alpha=0.5,
               label=f'{m} mem' if m == 'M0' else None)
Ns = np.array([5000, 300000])
ax1.loglog(Ns, 0.4 * Ns / 5000, 'k:', alpha=0.5, label='O(N) reference')
ax1.set_xlabel('Agent count N')
ax1.set_ylabel('Runtime per sim (s)', color='black')
ax2.set_ylabel('Peak memory delta (MB)', color='gray')
ax1.set_title('Computational Cost Scaling')
ax1.grid(alpha=0.3, which='both')
ax1.legend(loc='upper left', fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(f'{OUT}/fig4_count_runtime_memory.png', dpi=150)
plt.close()

# fig5: Pareto (runtime vs UR RMSE)
fig, ax = plt.subplots(figsize=(8.5, 5.5))
for m in MODELS:
    sub = agg[(agg['mode']=='regenerate') & (agg['model']==m)].sort_values('N')
    ax.errorbar(sub['runtime'], sub['ur_mean'], yerr=sub['ur_std'],
                fmt='o-', color=COLORS[m], label=m, capsize=3, lw=2)
    for _, r in sub.iterrows():
        ax.annotate(f'{int(r["N"]/1000)}k', (r['runtime'], r['ur_mean']),
                    textcoords='offset points', xytext=(6, 4), fontsize=7, color=COLORS[m])
ax.set_xscale('log')
ax.set_xlabel('Runtime per sim (s, log)')
ax.set_ylabel('UR RMSE (pp)')
ax.set_title('Performance-Cost Pareto (Regenerate mode)')
ax.grid(alpha=0.3, which='both')
ax.legend(loc='upper right')
# shade recommended region
ax.axvspan(3.5, 11, color='green', alpha=0.08, label='_nolegend_')
ax.text(6, ax.get_ylim()[1]*0.95, 'recommended\n50k–100k',
        ha='center', fontsize=9, color='darkgreen')
plt.tight_layout()
plt.savefig(f'{OUT}/fig5_pareto_tradeoff.png', dpi=150)
plt.close()

print("Saved 5 figures to", OUT)
