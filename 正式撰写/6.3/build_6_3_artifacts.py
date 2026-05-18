"""Build tables (CSV) and figures (PNG) for Results Section 6.3."""
import os, json, csv
import numpy as np
import matplotlib.pyplot as plt

ROOT = '正式撰写/6.3'
TBL  = os.path.join(ROOT, 'tables')
FIG  = os.path.join(ROOT, 'figures')
os.makedirs(TBL, exist_ok=True); os.makedirs(FIG, exist_ok=True)

with open(os.path.join(ROOT, 'ablation_metrics.json'), encoding='utf-8') as f:
    A = json.load(f)
with open(os.path.join(ROOT, 'ladder_metrics.json'), encoding='utf-8') as f:
    L = json.load(f)
ser_abl = np.load(os.path.join(ROOT, 'ablation_series.npz'), allow_pickle=True)
ser_lad = np.load(os.path.join(ROOT, 'ladder_series.npz'), allow_pickle=True)
dates = ser_abl['dates']
t_ur, t_lfpr, t_epop = ser_abl['target_ur'], ser_abl['target_lfpr'], ser_abl['target_epop']

DIMS = ['income_exp', 'labor_frag', 'liquidity', 'search', 'housing', 'consumption_rule']
DIM_PAPER = {
    'income_exp':       'Income Growth Expectation',
    'labor_frag':       'Labor Fragility',
    'liquidity':        'Liquidity Fragility',
    'search':           'Labor Search Friction',
    'housing':          'Housing Mobility Friction',
    'consumption_rule': 'Consumption Adjustment Rule',
}
MECHS = ['high_fragility_modifier', 'liquidity_constraint_modifier',
         'housing_lockin_modifier', 'fragility_x_liquidity_interaction',
         'matching_competition', 'discouraged_worker',
         'housing_reentry_friction', 'expectation_participation',
         'effective_mpc_adjustment', 'consumption_sequencing',
         'buffer_consumption_ordering', 'state_dependent_expectation',
         'experience_dependent_expectation']
MECH_BLOCK = {
    'high_fragility_modifier': 'type-specific',
    'liquidity_constraint_modifier': 'type-specific',
    'housing_lockin_modifier': 'type-specific',
    'fragility_x_liquidity_interaction': 'type-specific',
    'matching_competition': 'labor/search',
    'discouraged_worker': 'participation',
    'housing_reentry_friction': 'participation',
    'expectation_participation': 'participation',
    'effective_mpc_adjustment': 'household',
    'consumption_sequencing': 'household',
    'buffer_consumption_ordering': 'household',
    'state_dependent_expectation': 'expectations',
    'experience_dependent_expectation': 'expectations',
}
LADDER_ORDER = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'G2', 'G3']

base = A['summary']['baseline']['oos']
B_UR   = base['ur_rmse_mean']   * 100
B_LFPR = base['lfpr_rmse_mean'] * 100
B_EPOP = base['epop_rmse_mean'] * 100
B_CORR = base['ur_corr_mean']
B_SD   = base['ur_rmse_std']    * 100


def pp(x): return x * 100
def stable_flag(sd_pp, delta_pp):
    if abs(delta_pp) < 0.01: return 'n/a'
    return 'stable' if abs(delta_pp) > 3 * sd_pp else 'fragile'


def write_csv(path, rows):
    if not rows: return
    fields = list(rows[0].keys())
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); [w.writerow(r) for r in rows]


def interp_dim(d, ur, sd):
    delta = ur - B_UR
    if delta > 0.5: return 'critical — flattening sharply degrades UR; dominant standalone driver'
    if delta > 0.1: return 'important — clear standalone contribution to UR fit'
    if delta > 0.03: return 'marginal — small standalone effect; check ladder for interaction'
    if abs(delta) < 3 * sd:  return 'negligible — within seed noise standalone'
    return 'mild deterioration when flattened'


def interp_mech(m, ur, sd, lfpr, epop):
    delta = ur - B_UR
    if delta > 1.0:  return 'CORE — disabling collapses UR dynamics'
    if delta > 0.1:  return 'important — disabling produces visible UR loss'
    if delta > 0.03: return 'marginal UR effect; may matter for LFPR/EPOP'
    if abs(delta) < 3 * sd: return 'standalone effect within seed noise'
    return 'mild deterioration'


# Table 1 — Dimension ablation
rows1 = [{
    'model_or_ablation': 'Full heterogeneous ABM (baseline)',
    'oos_ur_rmse_pp': round(B_UR, 4),
    'delta_ur_rmse_pp': 0.0,
    'seed_sd_ur_pp': round(B_SD, 4),
    'ur_corr': round(B_CORR, 4),
    'lfpr_rmse_pp': round(B_LFPR, 4),
    'epop_rmse_pp': round(B_EPOP, 4),
    'interpretation': 'reference',
}]
for d in DIMS:
    s = A['summary'][f'dim_{d}']['oos']
    ur = pp(s['ur_rmse_mean']); sd = pp(s['ur_rmse_std'])
    rows1.append({
        'model_or_ablation': f'Flatten {DIM_PAPER[d]}',
        'oos_ur_rmse_pp': round(ur, 4),
        'delta_ur_rmse_pp': round(ur - B_UR, 4),
        'seed_sd_ur_pp': round(sd, 4),
        'ur_corr': round(s['ur_corr_mean'], 4),
        'lfpr_rmse_pp': round(pp(s['lfpr_rmse_mean']), 4),
        'epop_rmse_pp': round(pp(s['epop_rmse_mean']), 4),
        'interpretation': interp_dim(d, ur, sd),
    })
write_csv(os.path.join(TBL, 'table1_dimension_ablation.csv'), rows1)

# Table 2 — Mechanism ablation
rows2 = [{
    'mechanism_disabled': 'NONE (baseline)',
    'affected_block': '—',
    'oos_ur_rmse_pp': round(B_UR, 4),
    'delta_ur_rmse_pp': 0.0,
    'seed_sd_ur_pp': round(B_SD, 4),
    'lfpr_rmse_pp': round(B_LFPR, 4),
    'epop_rmse_pp': round(B_EPOP, 4),
    'interpretation': 'reference',
}]
for m in MECHS:
    s = A['summary'][f'mech_{m}']['oos']
    ur = pp(s['ur_rmse_mean']); sd = pp(s['ur_rmse_std'])
    rows2.append({
        'mechanism_disabled': m,
        'affected_block': MECH_BLOCK[m],
        'oos_ur_rmse_pp': round(ur, 4),
        'delta_ur_rmse_pp': round(ur - B_UR, 4),
        'seed_sd_ur_pp': round(sd, 4),
        'lfpr_rmse_pp': round(pp(s['lfpr_rmse_mean']), 4),
        'epop_rmse_pp': round(pp(s['epop_rmse_mean']), 4),
        'interpretation': interp_mech(m, ur, sd, pp(s['lfpr_rmse_mean']), pp(s['epop_rmse_mean'])),
    })
write_csv(os.path.join(TBL, 'table2_mechanism_ablation.csv'), rows2)

# Table 3 — Heterogeneity ladder
rows3 = []
for lid in LADDER_ORDER:
    s = L['summary'][lid]; o = s['oos']
    ur = pp(o['ur_rmse_mean']); sd = pp(o['ur_rmse_std'])
    note = 'reference' if lid == 'L6' else ''
    rows3.append({
        'level': lid,
        'ladder': s['ladder'],
        'n_active_dim': s['n_active_dim'],
        'active_dims': s['active_dims'],
        'oos_ur_rmse_pp': round(ur, 4),
        'delta_vs_L6_pp': round(ur - B_UR, 4),
        'seed_sd_ur_pp': round(sd, 4),
        'ur_corr': round(o['ur_corr_mean'], 4),
        'lfpr_rmse_pp': round(pp(o['lfpr_rmse_mean']), 4),
        'epop_rmse_pp': round(pp(o['epop_rmse_mean']), 4),
        'note': note,
    })
write_csv(os.path.join(TBL, 'table3_heterogeneity_ladder.csv'), rows3)

# Table 4 — Ablation ranking
rank_rows = []
for d in DIMS:
    s = A['summary'][f'dim_{d}']['oos']
    ur = pp(s['ur_rmse_mean']); sd = pp(s['ur_rmse_std'])
    rank_rows.append({
        'ablation': f'dimension: {DIM_PAPER[d]}',
        'kind': 'dimension',
        'delta_ur_rmse_pp': round(ur - B_UR, 4),
        'seed_sd_ur_pp': round(sd, 4),
        'stable_across_seeds': stable_flag(sd, ur - B_UR),
        'interpretation': interp_dim(d, ur, sd),
    })
for m in MECHS:
    s = A['summary'][f'mech_{m}']['oos']
    ur = pp(s['ur_rmse_mean']); sd = pp(s['ur_rmse_std'])
    rank_rows.append({
        'ablation': f'mechanism: {m}',
        'kind': 'mechanism',
        'delta_ur_rmse_pp': round(ur - B_UR, 4),
        'seed_sd_ur_pp': round(sd, 4),
        'stable_across_seeds': stable_flag(sd, ur - B_UR),
        'interpretation': interp_mech(m, ur, sd, None, None),
    })
rank_rows.sort(key=lambda r: -r['delta_ur_rmse_pp'])
for i, r in enumerate(rank_rows, 1):
    r['rank'] = i
rank_rows = [{'rank': r['rank'], **{k: v for k, v in r.items() if k != 'rank'}} for r in rank_rows]
write_csv(os.path.join(TBL, 'table4_ablation_ranking.csv'), rank_rows)

# Table 5 — Paper-ready compact dimension table
order_compact = ['search', 'liquidity', 'housing', 'consumption_rule',
                 'labor_frag', 'income_exp']
rows5 = [{
    'ablation': 'Full heterogeneous ABM',
    'oos_ur_rmse_pp': f'{B_UR:.3f}',
    'delta_ur_rmse_pp': '—',
    'main_interpretation': 'reference; LFPR/EPOP overshoot remains (see Section 6.2)',
}]
for d in order_compact:
    s = A['summary'][f'dim_{d}']['oos']
    ur = pp(s['ur_rmse_mean']); delta = ur - B_UR
    rows5.append({
        'ablation': f'Flatten {DIM_PAPER[d]}',
        'oos_ur_rmse_pp': f'{ur:.3f}',
        'delta_ur_rmse_pp': f'+{delta:.3f}',
        'main_interpretation': interp_dim(d, ur, pp(s['ur_rmse_std'])),
    })
write_csv(os.path.join(TBL, 'table5_paper_ready_compact.csv'), rows5)

print("Tables 1–5 saved to", TBL)

# ============================================================
# FIGURES
# ============================================================
VAL_E, OOS_E = 252, 302
oos_x = np.arange(VAL_E, OOS_E)
obs_ur_pp = t_ur * 100; obs_lfpr_pp = t_lfpr * 100; obs_epop_pp = t_epop * 100

# --- Figure 1: Dimension ablation bar (sorted) ---
dim_data = []
for d in DIMS:
    s = A['summary'][f'dim_{d}']['oos']
    dim_data.append((DIM_PAPER[d], pp(s['ur_rmse_mean']) - B_UR, pp(s['ur_rmse_std'])))
dim_data.sort(key=lambda x: -x[1])
labels = [d[0] for d in dim_data]
deltas = [d[1] for d in dim_data]
sds    = [d[2] for d in dim_data]
fig, ax = plt.subplots(figsize=(10, 5.2))
colors = ['#c0392b' if d > 0.5 else '#e67e22' if d > 0.1 else '#7f8c8d' for d in deltas]
bars = ax.bar(range(len(labels)), deltas, yerr=sds, capsize=5,
              color=colors, edgecolor='black', alpha=0.85)
for i, (d, s) in enumerate(zip(deltas, sds)):
    ax.text(i, d + s + 0.025, f'+{d:.3f}', ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=18, ha='right', fontsize=9)
ax.set_ylabel('Δ OOS UR RMSE vs Full model (pp)')
ax.set_title('Figure 1 — Dimension ablation: ΔOOS UR RMSE when each heterogeneity dimension is flattened\n(5 seeds, baseline ABM, OOS = 2022-01..2026-02)')
ax.axhline(0, color='black', lw=0.5)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig1_dimension_ablation_bar.png'), dpi=150); plt.close()

# --- Figure 2: Mechanism ablation bar grouped by block ---
mech_data = []
for m in MECHS:
    s = A['summary'][f'mech_{m}']['oos']
    mech_data.append((m, MECH_BLOCK[m],
                      pp(s['ur_rmse_mean']) - B_UR, pp(s['ur_rmse_std'])))
mech_data.sort(key=lambda x: -x[2])
BLOCK_COLORS = {'labor/search': '#c0392b', 'type-specific': '#2980b9',
                'participation': '#27ae60', 'household': '#8e44ad',
                'expectations': '#d35400'}
fig, ax = plt.subplots(figsize=(11, 5.5))
colors2 = [BLOCK_COLORS[b] for _, b, _, _ in mech_data]
labels2 = [m for m, _, _, _ in mech_data]
deltas2 = [d for _, _, d, _ in mech_data]
sds2 = [s for _, _, _, s in mech_data]
ax.bar(range(len(labels2)), deltas2, yerr=sds2, capsize=4,
       color=colors2, edgecolor='black', alpha=0.85)
for i, d in enumerate(deltas2):
    if d > 0.04:
        ax.text(i, d + sds2[i] + 0.04, f'+{d:.3f}', ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(range(len(labels2)))
ax.set_xticklabels(labels2, rotation=35, ha='right', fontsize=8)
ax.set_ylabel('Δ OOS UR RMSE vs Full model (pp)')
ax.set_title('Figure 2 — Mechanism ablation: ΔOOS UR RMSE when each of 13 mechanisms is disabled\n(colour = affected block; 5 seeds)')
ax.axhline(0, color='black', lw=0.5)
ax.grid(True, alpha=0.3, axis='y')
handles = [plt.Rectangle((0,0),1,1, color=c, ec='black') for c in BLOCK_COLORS.values()]
ax.legend(handles, BLOCK_COLORS.keys(), loc='upper right', fontsize=8, title='block')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig2_mechanism_ablation_bar.png'), dpi=150); plt.close()

# --- Figure 3: Heterogeneity ladder curve ---
core_order = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']
layer_order = ['G2', 'G3']
xs = list(range(len(core_order)))
ur_core = [pp(L['summary'][lid]['oos']['ur_rmse_mean']) for lid in core_order]
sd_core = [pp(L['summary'][lid]['oos']['ur_rmse_std']) for lid in core_order]
ur_layer = [pp(L['summary'][lid]['oos']['ur_rmse_mean']) for lid in layer_order]
sd_layer = [pp(L['summary'][lid]['oos']['ur_rmse_std']) for lid in layer_order]

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.errorbar(xs, ur_core, yerr=sd_core, marker='o', ms=10, lw=2,
            color='#2c3e50', capsize=5, label='Core ladder (nested)')
for x, lid, u in zip(xs, core_order, ur_core):
    ax.annotate(f'{lid}\n{u:.3f}', (x, u), xytext=(0, 12),
                textcoords='offset points', ha='center', fontsize=9, fontweight='bold')
ax.scatter([3.9, 4.9], ur_layer, marker='D', s=120, color='#e67e22',
           edgecolor='black', zorder=10, label='Layer ladder (G2/G3)')
for xpos, lid, u in zip([3.9, 4.9], layer_order, ur_layer):
    ax.annotate(f'{lid}\n{u:.3f}', (xpos, u), xytext=(8, -4),
                textcoords='offset points', ha='left', fontsize=9, color='#a0522d')
ax.axhline(B_UR, color='#27ae60', ls='--', lw=1.5, label=f'Full model = L6 ({B_UR:.3f} pp)')
ax.set_xticks(xs)
ax.set_xticklabels([f'{c}\nn={L["summary"][c]["n_active_dim"]}' for c in core_order])
ax.set_xlabel('Heterogeneity ladder level (Core: nested addition order)')
ax.set_ylabel('OOS UR RMSE (pp)')
ax.set_title('Figure 3 — Heterogeneity ladder: OOS UR RMSE as dimensions are added\n(Core L0→L6 nested; Layer G2/G3 are conceptual block additions)')
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig3_heterogeneity_ladder.png'), dpi=150); plt.close()

print("Figures 1–3 saved.")

# --- Figure 4: UR vs LFPR/EPOP trade-off (grouped bars for top ablations) ---
selected = [('Full', B_UR, B_LFPR, B_EPOP, '#27ae60')]
for d in ['search', 'liquidity', 'housing', 'consumption_rule']:
    s = A['summary'][f'dim_{d}']['oos']
    selected.append((f'flatten\n{DIM_PAPER[d].split()[0]}',
                     pp(s['ur_rmse_mean']), pp(s['lfpr_rmse_mean']),
                     pp(s['epop_rmse_mean']), '#c0392b'))
selected.append(('disable\nmatching_comp.',
                 pp(A['summary']['mech_matching_competition']['oos']['ur_rmse_mean']),
                 pp(A['summary']['mech_matching_competition']['oos']['lfpr_rmse_mean']),
                 pp(A['summary']['mech_matching_competition']['oos']['epop_rmse_mean']),
                 '#34495e'))
labels4 = [s[0] for s in selected]
ur_arr  = np.array([s[1] for s in selected])
lf_arr  = np.array([s[2] for s in selected])
ep_arr  = np.array([s[3] for s in selected])
x4 = np.arange(len(labels4))
bw = 0.27
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.bar(x4 - bw, ur_arr, bw, color='#3498db', edgecolor='black', label='UR RMSE')
ax.bar(x4,        lf_arr, bw, color='#9b59b6', edgecolor='black', label='LFPR RMSE')
ax.bar(x4 + bw,   ep_arr, bw, color='#16a085', edgecolor='black', label='EPOP RMSE')
for i in range(len(labels4)):
    ax.text(x4[i]-bw, ur_arr[i]+0.05, f'{ur_arr[i]:.2f}', ha='center', fontsize=8)
    ax.text(x4[i],    lf_arr[i]+0.05, f'{lf_arr[i]:.2f}', ha='center', fontsize=8)
    ax.text(x4[i]+bw, ep_arr[i]+0.05, f'{ep_arr[i]:.2f}', ha='center', fontsize=8)
ax.set_xticks(x4); ax.set_xticklabels(labels4, fontsize=9)
ax.set_ylabel('OOS RMSE (pp)'); ax.set_yscale('log')
ax.set_title('Figure 4 — Cross-metric trade-off: UR vs LFPR/EPOP RMSE for selected ablations\n(5 seeds; log-y to show full dynamic range)')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3, which='both', axis='y')
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig4_ur_lfpr_epop_tradeoff.png'), dpi=150); plt.close()

# --- Figure 5: Search Friction ablation path (OOS only) ---
ur_base_path = ser_abl['baseline_ur'].mean(axis=0) * 100
ur_search_path = ser_abl['dim_search_ur'].mean(axis=0) * 100
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(oos_x, obs_ur_pp[VAL_E:OOS_E], 'k-', lw=2.2, label='BLS Actual', zorder=10)
ax.plot(oos_x, ur_base_path[VAL_E:OOS_E], '-', lw=1.8, color='#27ae60',
        label=f'Full model (UR RMSE={B_UR:.3f} pp)')
ax.plot(oos_x, ur_search_path[VAL_E:OOS_E], '-', lw=1.8, color='#c0392b',
        label=f'Flatten Search Friction (UR RMSE={pp(A["summary"]["dim_search"]["oos"]["ur_rmse_mean"]):.3f} pp)')
tick_pos = [i for i in range(VAL_E, OOS_E) if dates[i].endswith('-01')]
ax.set_xticks(tick_pos); ax.set_xticklabels([dates[i][:4] for i in tick_pos])
ax.set_xlabel('Year'); ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Figure 5 — Search Friction ablation: full model vs Search-flattened (OOS window)\nseed-mean trajectories, 5 seeds')
ax.legend(loc='upper right', fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig5_search_friction_path.png'), dpi=150); plt.close()

print("Figures 4–5 saved to", FIG)
