"""
Package C plots:
  fig1_ladder_rmse_curve.png        both projection + refit RMSE vs dim
  fig2_marginal_gain.png            bar of marginal gain per level
  fig3_cumulative_share.png         cumulative share curve + 80/90% lines
  fig4_complexity_efficiency.png    RMSE vs dim with Pareto tracking
  fig5_refit_benefit.png            projection - refit bars (heterogeneity irreplaceability)
"""
import os, csv, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT = 'Phase3_Output/packageC'
plt.rcParams['figure.dpi'] = 110


def read_csv(path):
    rows = []
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            for k, v in row.items():
                if v in ('', None): row[k] = None
                else:
                    try: row[k] = float(v)
                    except: pass
            rows.append(row)
    return rows


def main():
    A = read_csv(f'{OUT}/packageC_ladder_analysis.csv')
    levels = [r['level'] for r in A]
    dims = [int(r['n_active_dim']) for r in A]
    proj = [r['proj_ur_rmse_pp'] for r in A]
    proj_std = [r['proj_ur_rmse_std'] for r in A]
    refit = [r['refit_ur_rmse_pp'] for r in A]
    refit_std = [r['refit_ur_rmse_std'] for r in A]
    marg = [r['refit_marginal_pp'] for r in A]
    cum = [r['refit_cum_share'] for r in A]
    ce = [r['complexity_eff'] for r in A]
    benefit = [r['refit_benefit_pp'] for r in A]

    # === fig1: RMSE curve (projection vs refit) ===
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(dims, proj, yerr=proj_std, fmt='o-', color='#c73e1d',
                label='Projection (fixed params)', capsize=4, lw=2)
    ax.errorbar(dims, refit, yerr=refit_std, fmt='s-', color='#2e86ab',
                label='Refit (re-calibrated)', capsize=4, lw=2)
    for i, lv in enumerate(levels):
        ax.annotate(lv, (dims[i], min(proj[i], refit[i])),
                    textcoords='offset points', xytext=(0, -14),
                    ha='center', fontsize=8, color='#555')
    ax.set_xlabel('Number of active heterogeneity dimensions')
    ax.set_ylabel('Test UR RMSE (pp)')
    ax.set_title('Heterogeneity Ladder — UR RMSE vs Dimensionality')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig1_ladder_rmse_curve.png', dpi=150)
    plt.close()

    # === fig2: marginal gain bars ===
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#2e8b57' if m > 0 else '#b22222' for m in marg[1:]]
    ax.bar(levels[1:], marg[1:], color=colors, edgecolor='black')
    ax.axhline(0, color='black', lw=0.8)
    ax.axhline(0.02, color='gray', ls='--', alpha=0.6, label='noise band (+0.02)')
    ax.axhline(-0.02, color='gray', ls='--', alpha=0.6)
    ax.set_xlabel('Level (added dimension)')
    ax.set_ylabel('Marginal UR RMSE reduction (pp)')
    ax.set_title('Per-Level Marginal Gain (Refit track)')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig2_marginal_gain.png', dpi=150)
    plt.close()

    # === fig3: cumulative share ===
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(dims, cum, 'o-', color='#2e86ab', lw=2)
    ax.axhline(0.80, color='#c73e1d', ls='--', alpha=0.7, label='80% threshold')
    ax.axhline(0.90, color='#b22222', ls='--', alpha=0.7, label='90% threshold')
    for i, lv in enumerate(levels):
        ax.annotate(f"{lv}\n{cum[i]:.2f}", (dims[i], cum[i]),
                    textcoords='offset points', xytext=(5, 5), fontsize=8)
    ax.set_xlabel('Active heterogeneity dimensions')
    ax.set_ylabel('Cumulative share of total gain (Refit)')
    ax.set_ylim(-0.05, 1.15)
    ax.set_title('Cumulative Performance Share')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig3_cumulative_share.png', dpi=150)
    plt.close()

    # === fig4: complexity efficiency (pareto-like) ===
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(dims, refit, 'o-', color='#2e86ab', lw=2, label='Refit RMSE')
    ax2 = ax.twinx()
    ax2.bar(dims, ce, alpha=0.3, color='#e1a96b',
            label='Complexity efficiency (pp/dim)')
    ax.set_xlabel('Active dimensions')
    ax.set_ylabel('UR RMSE (pp)', color='#2e86ab')
    ax2.set_ylabel('Gain per dim (pp)', color='#e1a96b')
    ax.set_title('Complexity Efficiency Tracking')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig4_complexity_efficiency.png', dpi=150)
    plt.close()

    # === fig5: refit benefit per level ===
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#7a9e9f' if b >= 0 else '#d96941' for b in benefit]
    ax.bar(levels, benefit, color=colors, edgecolor='black')
    ax.axhline(0, color='black', lw=0.8)
    ax.set_xlabel('Level')
    ax.set_ylabel('Projection RMSE − Refit RMSE (pp)')
    ax.set_title('Re-calibration Benefit per Level\n'
                 '(high = fixed-param projection over-penalizes low-dim setups)')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig5_refit_benefit.png', dpi=150)
    plt.close()

    print("Saved 5 figures to", OUT)


if __name__ == '__main__':
    main()
