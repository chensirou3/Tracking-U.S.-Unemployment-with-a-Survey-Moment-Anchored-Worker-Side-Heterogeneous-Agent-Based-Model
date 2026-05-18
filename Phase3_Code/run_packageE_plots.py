"""
Package E — 4 figures.
  fig1_method_performance.png   train/val/test loss box+scatter per method
  fig2_convergence_trajectory.png best-so-far curves per method (log y)
  fig3_param_overlap.png        14-param x 5-method heatmap of top-5 cv
  fig4_soa_stability.png        share_heterogeneity per method
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Phase3_Code.calibration_engine import param_names

OUT = 'Phase3_Output/packageE'
METHODS = ['M1_RS', 'M2_LHS', 'M3_Sobol', 'M4_CtF', 'M5_DE']
COLORS = {'M1_RS': '#1f77b4', 'M2_LHS': '#ff7f0e', 'M3_Sobol': '#2ca02c',
          'M4_CtF': '#d62728', 'M5_DE': '#9467bd'}
PHASE6_TEST_UR = 0.246


def fig1_performance(df, agg):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, col, ylabel in zip(
        axes,
        ['train_loss_mean', 'val_loss_mean', 'test_ur_rmse_pp'],
        ['Train loss', 'Validation loss', 'Test UR RMSE (pp)']
    ):
        data = [df[df.method_id == m][col].values for m in METHODS]
        bp = ax.boxplot(data, labels=METHODS, showfliers=False, widths=0.55,
                        patch_artist=True)
        for patch, m in zip(bp['boxes'], METHODS):
            patch.set_facecolor(COLORS[m]); patch.set_alpha(0.35)
        # rank-1 as red dots
        for i, m in enumerate(METHODS):
            sub = df[df.method_id == m]
            rank1 = sub.loc[sub['train_loss_mean'].idxmin()]
            ax.plot(i + 1, rank1[col], 'rX', ms=11, mew=2, label='rank-1' if i == 0 else None)
        if col == 'test_ur_rmse_pp':
            ax.axhline(PHASE6_TEST_UR, ls='--', c='k', lw=1, alpha=0.6,
                       label=f'Phase 6 baseline ({PHASE6_TEST_UR}pp)')
            ax.legend(fontsize=8, loc='upper right')
        ax.set_ylabel(ylabel); ax.set_title(col)
        ax.grid(alpha=0.3)
    fig.suptitle('Package E — Performance by calibration method (200 evals each, 3 seeds)')
    fig.tight_layout()
    path = os.path.join(OUT, 'fig1_method_performance.png')
    fig.savefig(path, dpi=120, bbox_inches='tight'); plt.close(fig)
    print('Saved', path)


def fig2_convergence(bsf):
    fig, ax = plt.subplots(figsize=(10, 5))
    for m in METHODS:
        if m not in bsf.columns:
            continue
        y = bsf[m].dropna().values
        ax.plot(np.arange(1, len(y) + 1), y, c=COLORS[m], lw=2, label=m)
    ax.set_xlabel('Evaluation number')
    ax.set_ylabel('Best-so-far train_loss')
    ax.set_title('Package E — Convergence trajectory (best-so-far)')
    ax.set_yscale('log')
    ax.grid(alpha=0.3, which='both')
    ax.legend()
    fig.tight_layout()
    path = os.path.join(OUT, 'fig2_convergence_trajectory.png')
    fig.savefig(path, dpi=120, bbox_inches='tight'); plt.close(fig)
    print('Saved', path)


def fig3_param_stability(stab):
    mat = stab.pivot_table(index='param', columns='method_id', values='cv').reindex(param_names)
    mat = mat[METHODS]
    fig, ax = plt.subplots(figsize=(7.5, 8))
    im = ax.imshow(mat.values, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=0.6)
    ax.set_xticks(range(len(METHODS))); ax.set_xticklabels(METHODS, rotation=30)
    ax.set_yticks(range(len(param_names))); ax.set_yticklabels(param_names)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=8,
                        color='white' if v > 0.35 else 'black')
    cb = fig.colorbar(im, ax=ax); cb.set_label('Top-5 CV (std/|mean|)')
    ax.set_title('Package E — Top-5 parameter dispersion per method\n(lower = more stable)')
    fig.tight_layout()
    path = os.path.join(OUT, 'fig3_param_overlap.png')
    fig.savefig(path, dpi=120, bbox_inches='tight'); plt.close(fig)
    print('Saved', path)


def fig4_soa(soa):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    x = np.arange(len(METHODS))

    ax = axes[0]
    ax.bar(x - 0.2, soa['M0_test_ur_rmse_pp'], width=0.2, label='M0 (main)', color='#2ca02c')
    ax.bar(x, soa['D1_test_ur_rmse_pp'], yerr=soa['D1_std'], width=0.2,
           label='D1 (homogeneous)', color='#d62728', capsize=3)
    ax.bar(x + 0.2, soa['D3_test_ur_rmse_pp'], yerr=soa['D3_std'], width=0.2,
           label='D3 (no household)', color='#ff7f0e', capsize=3)
    ax.set_xticks(x); ax.set_xticklabels(METHODS, rotation=20)
    ax.set_ylabel('Test UR RMSE (pp)')
    ax.set_title('Test UR by model variant (rank-1 candidate)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax2 = axes[1]
    ax2.bar(x - 0.2, soa['share_heterogeneity_pct'], width=0.35,
            label='share_heterogeneity', color='#1f77b4')
    ax2.bar(x + 0.2, soa['share_household_pct'], width=0.35,
            label='share_household', color='#9467bd')
    ax2.set_xticks(x); ax2.set_xticklabels(METHODS, rotation=20)
    ax2.set_ylabel('Advantage share (%)')
    ax2.set_title('Source of advantage across methods')
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

    fig.suptitle('Package E — Source-of-Advantage stability')
    fig.tight_layout()
    path = os.path.join(OUT, 'fig4_soa_stability.png')
    fig.savefig(path, dpi=120, bbox_inches='tight'); plt.close(fig)
    print('Saved', path)


def main():
    df = pd.read_csv(os.path.join(OUT, 'method_raw_results.csv'))
    agg = pd.read_csv(os.path.join(OUT, 'method_aggregated.csv'))
    bsf = pd.read_csv(os.path.join(OUT, 'best_so_far.csv'))
    stab = pd.read_csv(os.path.join(OUT, 'param_stability.csv'))
    soa = pd.read_csv(os.path.join(OUT, 'source_of_advantage_per_method.csv'))
    fig1_performance(df, agg)
    fig2_convergence(bsf)
    fig3_param_stability(stab)
    fig4_soa(soa)


if __name__ == '__main__':
    main()
