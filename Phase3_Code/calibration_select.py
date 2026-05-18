"""
Phase 6: Candidate selection, visualization, and handoff.
Select 3 versions: conservative / baseline / aggressive
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.calibration_engine import (
    evaluate, param_names, PARAM_SPACE, RealEnvironment,
    target_ur, target_lfpr, target_epop, T, TRAIN_END
)

os.makedirs('Phase3_Output/phase6', exist_ok=True)

# Load results
with open('Phase3_Output/phase6/calibration_results.json') as f:
    results = json.load(f)

# Strategy: pick 3 versions
# baseline = best combined (low train + acceptable val)
# conservative = best val_mean (generalizes best)
# aggressive = best train_mean (fits training best)

by_train = sorted(results, key=lambda x: x['train_mean'])
by_val = sorted(results, key=lambda x: x['val_mean'])
by_combined = sorted(results, key=lambda x: x['train_mean'] + 0.5 * x['val_mean'])

versions = {
    'aggressive': by_train[0],
    'baseline': by_combined[0],
    'conservative': by_val[0],
}

# Print selection
print("=" * 60)
print("CANDIDATE VERSION SELECTION")
print("=" * 60)
for name, v in versions.items():
    print(f"\n{name.upper()} (rank {v['rank']}):")
    print(f"  Train loss: {v['train_mean']:.4f} +/- {v['train_std']:.4f}")
    print(f"  Val loss:   {v['val_mean']:.4f} +/- {v['val_std']:.4f}")
    print(f"  Train UR RMSE:   {v['train_comp_avg']['ur']:.4f}")
    print(f"  Train LFPR RMSE: {v['train_comp_avg']['lfpr']:.4f}")
    print(f"  Params:")
    for pn, pv in v['params'].items():
        print(f"    {pn}: {pv:.4f}")

# Save candidate versions
for name, v in versions.items():
    with open(f'Phase3_Output/phase6/candidate_{name}.json', 'w') as f:
        json.dump(v, f, indent=2)

# ================================================================
# RUN ALL 3 AND PLOT AGAINST ACTUAL
# ================================================================
env = RealEnvironment(data_dir='Phase3_Data')
dates = env.dates

fig, axes = plt.subplots(3, 2, figsize=(18, 14))
fig.suptitle('Phase 6: Calibrated Model vs BLS Actual', fontsize=14)

tick_pos = [i for i, d in enumerate(dates[:T]) if d.endswith('-01') and int(d[:4]) % 3 == 0]
tick_lab = [dates[i][:4] for i in tick_pos]
months = np.arange(T)

colors = {'conservative': 'green', 'baseline': 'blue', 'aggressive': 'red'}
histories = {}

for name, v in versions.items():
    pvec = np.array([v['params'][pn] for pn in param_names])
    _, _, _, _, hist = evaluate(pvec, seed=42)
    histories[name] = hist

# Panel 1: UR
ax = axes[0, 0]
ax.plot(months, target_ur[:T] * 100, 'k-', lw=2, label='BLS Actual', alpha=0.8)
for name in ['conservative', 'baseline', 'aggressive']:
    ur = [h['unemployment_rate'] * 100 for h in histories[name]]
    ax.plot(months, ur, '-', color=colors[name], lw=1.2, label=name, alpha=0.8)
ax.axvline(TRAIN_END, color='gray', ls='--', lw=1, alpha=0.5, label='Train|Val')
ax.set_ylabel('UR (%)'); ax.set_title('Unemployment Rate')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab, fontsize=8)
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# Panel 2: LFPR
ax = axes[0, 1]
ax.plot(months, target_lfpr[:T] * 100, 'k-', lw=2, label='BLS Actual', alpha=0.8)
for name in ['conservative', 'baseline', 'aggressive']:
    lfpr = [h['lfpr'] * 100 for h in histories[name]]
    ax.plot(months, lfpr, '-', color=colors[name], lw=1.2, label=name, alpha=0.8)
ax.axvline(TRAIN_END, color='gray', ls='--', lw=1, alpha=0.5)
ax.set_ylabel('LFPR (%)'); ax.set_title('Labor Force Participation Rate')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab, fontsize=8)
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# Panel 3: EPOP
ax = axes[1, 0]
ax.plot(months, target_epop[:T] * 100, 'k-', lw=2, label='BLS Actual', alpha=0.8)
for name in ['conservative', 'baseline', 'aggressive']:
    epop = [h['epop'] * 100 for h in histories[name]]
    ax.plot(months, epop, '-', color=colors[name], lw=1.2, label=name, alpha=0.8)
ax.axvline(TRAIN_END, color='gray', ls='--', lw=1, alpha=0.5)
ax.set_ylabel('EPOP (%)'); ax.set_title('Employment-Population Ratio')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab, fontsize=8)
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# Panel 4: E→U and U→E
ax = axes[1, 1]
for name in ['baseline']:
    eu = [h['eu_rate'] * 100 for h in histories[name]]
    ue = [h['ue_rate'] * 100 for h in histories[name]]
    ax.plot(months, eu, 'r-', lw=1.2, label=f'E→U ({name})')
    ax.plot(months, ue, 'g-', lw=1.2, label=f'U→E ({name})')
ax.axhline(1.5, color='r', ls=':', alpha=0.5, label='BLS E→U target')
ax.axhline(25, color='g', ls=':', alpha=0.5, label='BLS U→E target')
ax.axvline(TRAIN_END, color='gray', ls='--', lw=1, alpha=0.5)
ax.set_ylabel('Rate (%)'); ax.set_title('Transition Rates (baseline)')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab, fontsize=8)
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# Panel 5: Loss decomposition radar
ax = axes[2, 0]
components = ['ur', 'lfpr', 'epop', 'eu', 'ue', 'h2m']
x_pos = np.arange(len(components))
width = 0.25
for i, name in enumerate(['conservative', 'baseline', 'aggressive']):
    v = versions[name]
    vals = [v['train_comp_avg'][c] for c in components]
    ax.bar(x_pos + i*width, vals, width, label=name, color=colors[name], alpha=0.7)
ax.set_xticks(x_pos + width); ax.set_xticklabels(components, fontsize=9)
ax.set_ylabel('Loss Component'); ax.set_title('Train Loss Decomposition')
ax.legend(fontsize=8)

# Panel 6: Summary table as text
ax = axes[2, 1]
ax.axis('off')
table_data = []
for name in ['conservative', 'baseline', 'aggressive']:
    v = versions[name]
    table_data.append([name, f"{v['train_mean']:.4f}", f"{v['val_mean']:.4f}",
                       f"{v['train_std']:.4f}", f"{v['val_std']:.4f}",
                       'YES' if v['stable'] == 'True' or v['stable'] == True else 'NO'])
table = ax.table(cellText=table_data,
                 colLabels=['Version', 'Train', 'Val', 'Train_std', 'Val_std', 'Stable'],
                 loc='center', cellLoc='center')
table.auto_set_font_size(False); table.set_fontsize(10)
table.scale(1, 1.5)
ax.set_title('Candidate Summary', fontsize=12, pad=20)

plt.tight_layout()
plt.savefig('Phase3_Output/phase6/calibration_comparison.png', dpi=150, bbox_inches='tight')
print("\nFigure saved to Phase3_Output/phase6/calibration_comparison.png")
print("\n=== PHASE 6 CANDIDATE SELECTION COMPLETE ===")
