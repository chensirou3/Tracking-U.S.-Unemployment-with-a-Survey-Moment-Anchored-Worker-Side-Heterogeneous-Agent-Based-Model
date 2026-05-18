"""
Phase 8 Analysis: combined comparison table, source-of-advantage decomposition,
and paper-ready figures.
"""
import sys, os, json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.phase7_engine import WINDOWS

os.makedirs('Phase3_Output/phase8', exist_ok=True)

# Load all results
with open('Phase3_Output/phase8/derived_results.json') as f:
    derived = json.load(f)
with open('Phase3_Output/phase8/benchmark_results.json') as f:
    bench = json.load(f)
series = dict(np.load('Phase3_Output/phase8/derived_series.npz', allow_pickle=True))
dates = list(series['dates'])
t_ur = series['target_ur']
t_lfpr = series['target_lfpr']
t_epop = series['target_epop']

# ================================================================
# TABLE: Combined comparison
# ================================================================
rows = []
# Derived models (convert rmse already in decimal, *100 for pp)
for mname, r in derived.items():
    m = r['metrics']['oos']
    rows.append({
        'Model': mname,
        'Category': 'Structural',
        'UR_RMSE_pp': m['ur_rmse_mean'] * 100,
        'UR_RMSE_std_pp': m['ur_rmse_std'] * 100,
        'UR_Corr': m['ur_corr_mean'],
        'LFPR_RMSE_pp': m['lfpr_rmse_mean'] * 100,
        'EPOP_RMSE_pp': m['epop_rmse_mean'] * 100,
        'Full_System': 'YES',
        'Overlap_Eligible': 'YES',
    })
# Benchmarks
for bname, b in bench.items():
    row = {
        'Model': bname, 'Category': 'Benchmark',
        'UR_RMSE_pp': b['ur_rmse'] * 100, 'UR_RMSE_std_pp': 0.0,
        'UR_Corr': b['ur_corr'],
        'LFPR_RMSE_pp': b.get('lfpr_rmse', np.nan) * 100 if not np.isnan(b.get('lfpr_rmse', np.nan)) else np.nan,
        'EPOP_RMSE_pp': b.get('epop_rmse', np.nan) * 100 if not np.isnan(b.get('epop_rmse', np.nan)) else np.nan,
        'Full_System': 'NO',
        'Overlap_Eligible': 'YES' if 'VAR' in bname else 'NO',
    }
    rows.append(row)

# Write CSV
with open('Phase3_Output/phase8/comparison_results.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)

# Print
print("=" * 95)
print("UNIFIED COMPARISON RESULTS (OOS 2022-01 to 2026-02, 50 months)")
print("=" * 95)
print(f"{'Model':<18s} {'Cat':<11s} {'UR_RMSE(pp)':>12s} {'UR_Corr':>9s} "
      f"{'LFPR_RMSE':>11s} {'EPOP_RMSE':>11s} {'FullSys':>8s}")
print("-" * 95)
rows_sorted = sorted(rows, key=lambda x: x['UR_RMSE_pp'])
for r in rows_sorted:
    lfpr = f"{r['LFPR_RMSE_pp']:>11.4f}" if not np.isnan(r['LFPR_RMSE_pp']) else f"{'N/A':>11s}"
    epop = f"{r['EPOP_RMSE_pp']:>11.4f}" if not np.isnan(r['EPOP_RMSE_pp']) else f"{'N/A':>11s}"
    print(f"{r['Model']:<18s} {r['Category']:<11s} {r['UR_RMSE_pp']:>11.4f}  "
          f"{r['UR_Corr']:>9.3f}  {lfpr} {epop} {r['Full_System']:>8s}")

# ================================================================
# SOURCE OF ADVANTAGE
# ================================================================
main_ur = derived['M0_Main']['metrics']['oos']['ur_rmse_mean'] * 100
print(f"\n{'='*70}")
print("SOURCE-OF-ADVANTAGE DECOMPOSITION (vs Main Model)")
print("=" * 70)

soa = [
    ('M0_Main (full)', main_ur, 0.0, 'Baseline: full heterogeneity + full mechanisms'),
    ('D3_LaborOnly', derived['D3_LaborOnly']['metrics']['oos']['ur_rmse_mean'] * 100,
     derived['D3_LaborOnly']['metrics']['oos']['ur_rmse_mean']*100 - main_ur,
     'Remove household outer ring (consumption/borrowing mechanisms)'),
    ('D1_Homogeneous', derived['D1_Homogeneous']['metrics']['oos']['ur_rmse_mean'] * 100,
     derived['D1_Homogeneous']['metrics']['oos']['ur_rmse_mean']*100 - main_ur,
     'Remove all 6-dim heterogeneity'),
    ('D2_Simplified', derived['D2_Simplified']['metrics']['oos']['ur_rmse_mean'] * 100,
     derived['D2_Simplified']['metrics']['oos']['ur_rmse_mean']*100 - main_ur,
     'Remove heterogeneity + advanced mechanisms (minimal baseline)'),
]
print(f"{'Configuration':<22s} {'UR RMSE':>9s} {'Δ vs Main':>10s}  Interpretation")
print("-" * 95)
for name, ur, delta, note in soa:
    print(f"{name:<22s} {ur:>8.4f}  {delta:>+9.4f}  {note}")

# Save source-of-advantage
with open('Phase3_Output/phase8/source_of_advantage.json', 'w') as f:
    json.dump([{'config': n, 'ur_rmse_pp': u, 'delta_pp': d, 'note': note}
               for n, u, d, note in soa], f, indent=2)

# ================================================================
# INCREMENTAL CONTRIBUTION (what each layer adds)
# ================================================================
print("\n" + "=" * 70)
print("INCREMENTAL CONTRIBUTION")
print("=" * 70)
simplified_ur = derived['D2_Simplified']['metrics']['oos']['ur_rmse_mean'] * 100
homog_ur = derived['D1_Homogeneous']['metrics']['oos']['ur_rmse_mean'] * 100
labor_only_ur = derived['D3_LaborOnly']['metrics']['oos']['ur_rmse_mean'] * 100

# Incremental gains
# Simplified → Homogeneous: adding advanced labor mechanisms (to homog baseline)
# Homogeneous → Main: adding heterogeneity
# Main (via Labor-Only): household outer ring
gain_mech = simplified_ur - homog_ur  # advanced mechs on homog
gain_het = homog_ur - main_ur          # heterogeneity on top of mechs
gain_hh = labor_only_ur - main_ur      # household outer ring

total = simplified_ur - main_ur

print(f"From D2_Simplified to M0_Main: {total:.4f} pp total improvement")
print(f"  Advanced mechanisms (D2→D1): {gain_mech:+.4f} pp ({gain_mech/max(total,0.01)*100:.0f}% of total)")
print(f"  Heterogeneity (D1→M0):       {gain_het:+.4f} pp ({gain_het/max(total,0.01)*100:.0f}% of total)")
print(f"  Household outer ring (from D3→M0): {gain_hh:+.4f} pp "
      f"({gain_hh/max(total,0.01)*100:.0f}% of total)")

inc_data = {
    'D2_Simplified_ur': simplified_ur,
    'D1_Homogeneous_ur': homog_ur,
    'D3_LaborOnly_ur': labor_only_ur,
    'M0_Main_ur': main_ur,
    'gain_advanced_mechanisms': gain_mech,
    'gain_heterogeneity': gain_het,
    'gain_household_outer': gain_hh,
    'total_gain_simplified_to_main': total,
}
with open('Phase3_Output/phase8/incremental_contribution.json', 'w') as f:
    json.dump(inc_data, f, indent=2)


# ================================================================
# FIGURES
# ================================================================
T = len(dates)
VAL_END = WINDOWS['val'][1]
months = np.arange(T)
tick_pos = [i for i, d in enumerate(dates) if d.endswith('-01') and int(d[:4]) % 3 == 0]
tick_lab = [dates[i][:4] for i in tick_pos]

# --- FIG 1: UR comparison (structural + best benchmarks) ---
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
ax.plot(months, t_ur * 100, 'k-', lw=2.5, label='BLS Actual', zorder=10)
color_map = {'M0_Main': 'blue', 'D1_Homogeneous': 'orange',
             'D2_Simplified': 'brown', 'D3_LaborOnly': 'green'}
for mname in ['M0_Main', 'D1_Homogeneous', 'D2_Simplified', 'D3_LaborOnly']:
    ur = series[f'{mname}_ur'] * 100
    ax.plot(months, ur, '-', color=color_map[mname], lw=1.3, label=mname, alpha=0.85)

oos_x = np.arange(VAL_END, T)
ax.plot(oos_x, np.array(bench['B3_Beveridge']['forecast']) * 100, '--',
        color='purple', lw=1.2, label='B3 Beveridge (OOS)', alpha=0.8)
ax.plot(oos_x, np.array(bench['B1_AR']['forecast']) * 100, '--',
        color='red', lw=1.2, label='B1 AR(1) (OOS)', alpha=0.8)

ax.axvspan(VAL_END, T, alpha=0.12, color='orange', label='OOS window')
ax.axvline(VAL_END, color='red', ls='--', lw=1.2)
ax.set_ylabel('Unemployment Rate (%)'); ax.set_xlabel('Year')
ax.set_title('Phase 8 - Unified UR Comparison')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab)
ax.legend(loc='upper left', fontsize=9, ncol=2)
ax.grid(True, alpha=0.3); ax.set_ylim(0, 17)
plt.tight_layout()
plt.savefig('Phase3_Output/phase8/fig1_unified_comparison.png', dpi=150, bbox_inches='tight')
print("\nFig 1 saved")

# --- FIG 2: Bar charts ---
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sorted_rows = sorted(rows, key=lambda x: x['UR_RMSE_pp'])
names = [r['Model'] for r in sorted_rows]
vals = [r['UR_RMSE_pp'] for r in sorted_rows]
cats = [r['Category'] for r in sorted_rows]
bar_colors = ['steelblue' if c == 'Structural' else 'coral' for c in cats]

ax = axes[0]
x_pos = np.arange(len(names))
bars = ax.bar(x_pos, vals, color=bar_colors, edgecolor='black', lw=0.5)
for bar, v in zip(bars, vals):
    h = bar.get_height()
    ax.annotate(f'{v:.3f}', xy=(bar.get_x() + bar.get_width()/2, h),
                xytext=(0, 3), textcoords='offset points', ha='center', fontsize=8)
ax.set_xticks(x_pos); ax.set_xticklabels(names, rotation=30, ha='right', fontsize=9)
ax.set_ylabel('OOS UR RMSE (pp)'); ax.set_title('UR RMSE: All 8 Models')
ax.grid(True, alpha=0.3, axis='y')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor='steelblue', label='Structural ABM'),
                   Patch(facecolor='coral', label='Benchmark')], fontsize=9)

ax = axes[1]
corr_vals = [r['UR_Corr'] for r in sorted_rows]
bars = ax.bar(x_pos, corr_vals, color=bar_colors, edgecolor='black', lw=0.5)
ax.axhline(0, color='k', lw=0.5)
for bar, v in zip(bars, corr_vals):
    h = bar.get_height()
    ax.annotate(f'{v:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                xytext=(0, 3 if h >= 0 else -12), textcoords='offset points',
                ha='center', fontsize=8)
ax.set_xticks(x_pos); ax.set_xticklabels(names, rotation=30, ha='right', fontsize=9)
ax.set_ylabel('OOS UR Correlation'); ax.set_title('UR Correlation')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('Phase3_Output/phase8/fig2_rmse_bars.png', dpi=150, bbox_inches='tight')
print("Fig 2 saved")

# --- FIG 3: Source of Advantage ---
fig, ax = plt.subplots(1, 1, figsize=(12, 6))
w_names = ['M0 Main\n(full)', 'D3 Labor-Only\n(- household)',
           'D1 Homog.\n(- heterogeneity)', 'D2 Simplified\n(- everything)']
w_vals = [main_ur, labor_only_ur, homog_ur, simplified_ur]
w_colors = ['steelblue', '#6BAED6', '#FDAE6B', '#E6550D']
x = np.arange(len(w_names))
bars = ax.bar(x, w_vals, color=w_colors, edgecolor='black', lw=0.8)
for i, (bar, v) in enumerate(zip(bars, w_vals)):
    h = bar.get_height()
    if i > 0:
        delta = v - w_vals[0]
        ax.annotate(f'{v:.3f}\n(+{delta:.3f})', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 5), textcoords='offset points', ha='center', fontsize=9)
    else:
        ax.annotate(f'{v:.3f}', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 5), textcoords='offset points', ha='center',
                    fontsize=10, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(w_names, fontsize=9)
ax.set_ylabel('OOS UR RMSE (pp)')
ax.set_title('Source-of-Advantage Decomposition')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('Phase3_Output/phase8/fig3_source_of_advantage.png', dpi=150, bbox_inches='tight')
print("Fig 3 saved")

# --- FIG 4: Positioning map ---
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
positioning = {
    'M0_Main': {'rmse': main_ur, 'struct': 5},
    'D1_Homogeneous': {'rmse': homog_ur, 'struct': 3.5},
    'D2_Simplified': {'rmse': simplified_ur, 'struct': 2},
    'D3_LaborOnly': {'rmse': labor_only_ur, 'struct': 4},
    'B1_AR': {'rmse': bench['B1_AR']['ur_rmse'] * 100, 'struct': 0.5},
    'B2_VAR': {'rmse': bench['B2_VAR']['ur_rmse'] * 100, 'struct': 1},
    'B3_Beveridge': {'rmse': bench['B3_Beveridge']['ur_rmse'] * 100, 'struct': 1.5},
    'B4_DMP': {'rmse': bench['B4_DMP']['ur_rmse'] * 100, 'struct': 3},
}
for name, p in positioning.items():
    pred_perf = 1.0 / max(p['rmse'], 0.01)
    col = 'blue' if name.startswith(('M', 'D')) else 'red'
    mk = 'o' if name.startswith('M') else ('s' if name.startswith('D') else '^')
    ax.scatter(pred_perf, p['struct'], s=200, c=col, marker=mk,
               edgecolor='black', lw=1, alpha=0.8)
    ax.annotate(name, (pred_perf, p['struct']), xytext=(5, 5),
                textcoords='offset points', fontsize=10)
ax.set_xlabel('Prediction Performance (1/UR RMSE)')
ax.set_ylabel('Structural Interpretability (subjective)')
ax.set_title('Phase 8 - Model Positioning')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Phase3_Output/phase8/fig4_positioning_map.png', dpi=150, bbox_inches='tight')
print("Fig 4 saved")
print("\nAll analyses complete.")