"""
Package B Step 4: 4 figures.
fig1_horizon_rmse_curve.png
fig2_lfpr_epop_horizon.png
fig3_relative_advantage.png
fig4_horizon_source_decomp.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('Phase3_Output/packageB', exist_ok=True)
HORIZONS = [1, 3, 6, 12, 24, 36]
MODELS = ['M0_Main', 'D1_Homogeneous', 'D2_Simplified', 'D3_LaborOnly',
          'B1_AR', 'B2_VAR', 'B3_Beveridge', 'B4_DMP']

df = pd.read_csv('Phase3_Output/packageB/horizon_results.csv')
piv = df.pivot(index='model', columns='horizon', values='ur_rmse_pp').reindex(MODELS).reindex(columns=HORIZONS)
piv_l = df.pivot(index='model', columns='horizon', values='lfpr_rmse_pp').reindex(MODELS).reindex(columns=HORIZONS)
piv_e = df.pivot(index='model', columns='horizon', values='epop_rmse_pp').reindex(MODELS).reindex(columns=HORIZONS)
soa = pd.read_csv('Phase3_Output/packageB/horizon_source_of_advantage.csv')

COLORS = {
    'M0_Main': '#2E7D32',
    'D1_Homogeneous': '#1565C0', 'D2_Simplified': '#1E88E5',
    'D3_LaborOnly': '#42A5F5',
    'B1_AR': '#B71C1C', 'B2_VAR': '#E53935',
    'B3_Beveridge': '#FF8F00', 'B4_DMP': '#F9A825',
}
STYLE = {m: ('-' if m.startswith(('M', 'D')) else '--') for m in MODELS}
LW = {m: (2.5 if m == 'M0_Main' else 1.5) for m in MODELS}

# ============ FIG 1: UR RMSE by horizon ============
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
for ax, ylog in [(ax1, False), (ax2, True)]:
    for m in MODELS:
        vals = piv.loc[m]
        ax.plot(vals.index, vals.values, STYLE[m], color=COLORS[m],
                lw=LW[m], marker='o', markersize=6, label=m)
    ax.set_xlabel('Forecast horizon (months)')
    ax.set_ylabel('UR RMSE (pp)')
    ax.set_xscale('log'); ax.set_xticks(HORIZONS); ax.set_xticklabels(HORIZONS)
    ax.grid(alpha=0.3, which='both')
    if ylog:
        ax.set_yscale('log')
        ax.set_title('(b) log-log scale')
    else:
        ax.set_title('(a) linear scale')
ax1.legend(fontsize=8, loc='upper right', ncol=2)
plt.suptitle('Fig 1 — UR RMSE vs Forecast Horizon', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('Phase3_Output/packageB/fig1_horizon_rmse_curve.png', dpi=120)
plt.close()

# ============ FIG 2: LFPR + EPOP horizons ============
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
for ax, piv_x, title in [(ax1, piv_l, 'LFPR RMSE'), (ax2, piv_e, 'EPOP RMSE')]:
    for m in MODELS:
        vals = piv_x.loc[m].dropna()
        if len(vals) == 0: continue
        ax.plot(vals.index, vals.values, STYLE[m], color=COLORS[m],
                lw=LW[m], marker='o', markersize=6, label=m)
    ax.set_xlabel('Forecast horizon (months)')
    ax.set_ylabel(f'{title} (pp)')
    ax.set_xscale('log'); ax.set_xticks(HORIZONS); ax.set_xticklabels(HORIZONS)
    ax.grid(alpha=0.3, which='both')
    ax.set_title(title)
    ax.legend(fontsize=8, loc='upper left')
plt.suptitle('Fig 2 — LFPR & EPOP Horizon Degradation', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('Phase3_Output/packageB/fig2_lfpr_epop_horizon.png', dpi=120)
plt.close()

# ============ FIG 3: relative advantage of M0 ============
fig, ax = plt.subplots(figsize=(10, 5.5))
m0 = piv.loc['M0_Main']
for b in MODELS:
    if b == 'M0_Main': continue
    bv = piv.loc[b]
    rel = (bv - m0) / bv * 100  # % advantage (positive = M0 better)
    ax.plot(HORIZONS, rel, STYLE[b], color=COLORS[b], lw=LW[b], marker='o',
            markersize=6, label=f'M0 vs {b}')
ax.axhline(0, color='k', lw=0.8)
ax.set_xlabel('Forecast horizon (months)')
ax.set_ylabel('M0 relative advantage (%)  →  positive = M0 better')
ax.set_xscale('log'); ax.set_xticks(HORIZONS); ax.set_xticklabels(HORIZONS)
ax.grid(alpha=0.3, which='both')
ax.legend(fontsize=9, loc='lower left', ncol=2)
ax.set_title('Fig 3 — M0 Relative Advantage by Horizon  (positive = M0 lower RMSE than baseline)')
plt.tight_layout()
plt.savefig('Phase3_Output/packageB/fig3_relative_advantage.png', dpi=120)
plt.close()

# ============ FIG 4: source-of-advantage by horizon ============
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
hs = soa.horizon.values
# Panel (a): absolute contributions
ax1.plot(hs, soa.delta_het_pp, '-o', color='#2E7D32', lw=2, label='Δ Heterogeneity (D1-M0)')
ax1.plot(hs, soa.delta_mech_pp, '-o', color='#F9A825', lw=2, label='Δ Mechanism (D2-D1)')
ax1.plot(hs, soa.delta_hh_pp, '-o', color='#1976D2', lw=2, label='Δ Household outer (D3-M0)')
ax1.plot(hs, soa.total_pp, '-s', color='k', lw=2, label='Total (D2-M0)')
ax1.axhline(0, color='gray', lw=0.7)
ax1.set_xlabel('Forecast horizon (months)')
ax1.set_ylabel('RMSE reduction (pp)')
ax1.set_xscale('log'); ax1.set_xticks(HORIZONS); ax1.set_xticklabels(HORIZONS)
ax1.grid(alpha=0.3, which='both')
ax1.legend(fontsize=9)
ax1.set_title('(a) Absolute contribution by horizon')

# Panel (b): share
ax2.plot(hs, soa.het_share, '-o', color='#2E7D32', lw=2, label='Heterogeneity share')
ax2.plot(hs, soa.mech_share, '-o', color='#F9A825', lw=2, label='Mechanism share')
ax2.axhline(1.0, color='gray', ls='--', lw=0.7)
ax2.axhline(0, color='gray', lw=0.7)
ax2.set_xlabel('Forecast horizon (months)')
ax2.set_ylabel('Share of total advantage')
ax2.set_xscale('log'); ax2.set_xticks(HORIZONS); ax2.set_xticklabels(HORIZONS)
ax2.grid(alpha=0.3, which='both')
ax2.legend(fontsize=9)
ax2.set_title('(b) Share of M0 advantage by horizon')

plt.suptitle('Fig 4 — Source-of-Advantage Decomposition by Horizon', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('Phase3_Output/packageB/fig4_horizon_source_decomp.png', dpi=120)
plt.close()

print("Saved 4 figures to Phase3_Output/packageB/")
