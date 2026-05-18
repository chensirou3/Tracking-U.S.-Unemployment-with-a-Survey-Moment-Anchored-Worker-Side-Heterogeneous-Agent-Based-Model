"""
Evaluate model prediction vs BLS actual unemployment rate.
"""
import sys, os, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load model results
model = dict(np.load('Phase3_Output/run_real_history.npz', allow_pickle=True))
model_ur = model['unemployment_rate'] * 100  # to %
model_dates = list(model['dates'])
T = len(model_ur)

# Load BLS actual UR
bls = {}
with open('Phase3_Data/UNRATE.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        d = row[0][:7]
        try:
            bls[d] = float(row[1])
        except (ValueError, IndexError):
            pass

# Align
actual_ur = np.array([bls.get(d, np.nan) for d in model_dates])
valid = ~np.isnan(actual_ur)

# ========== STATISTICS ==========
diff = model_ur[valid] - actual_ur[valid]
abs_diff = np.abs(diff)

print("=" * 65)
print("MODEL vs BLS ACTUAL UNEMPLOYMENT RATE")
print("=" * 65)
print(f"Period: {model_dates[0]} to {model_dates[-1]} ({T} months)")
print(f"\nFull Period:")
print(f"  MAE  = {abs_diff.mean():.2f} pp")
print(f"  RMSE = {np.sqrt((diff**2).mean()):.2f} pp")
print(f"  Bias = {diff.mean():+.2f} pp (model {'higher' if diff.mean()>0 else 'lower'})")
print(f"  Corr = {np.corrcoef(model_ur[valid], actual_ur[valid])[0,1]:.4f}")

# By era
eras = [
    ('2001-2006 (early)', '2001-01', '2006-12'),
    ('2007-2009 (GFC)', '2007-01', '2009-12'),
    ('2010-2014 (recovery)', '2010-01', '2014-12'),
    ('2015-2019 (expansion)', '2015-01', '2019-12'),
    ('2020-2021 (COVID)', '2020-01', '2021-12'),
    ('2022-2026 (post-COVID)', '2022-01', '2026-02'),
]

print(f"\n{'Era':<28s} {'MAE':>6s} {'RMSE':>6s} {'Bias':>7s} {'Corr':>6s}")
print("-" * 60)
for name, s, e in eras:
    idx = [(i, model_dates[i]) for i in range(T) if s <= model_dates[i] <= e]
    if not idx:
        continue
    ii = [i for i, d in idx]
    m = model_ur[ii]
    a = np.array([bls.get(model_dates[i], np.nan) for i in ii])
    v = ~np.isnan(a)
    if v.sum() < 2:
        continue
    d = m[v] - a[v]
    mae = np.abs(d).mean()
    rmse = np.sqrt((d**2).mean())
    bias = d.mean()
    corr = np.corrcoef(m[v], a[v])[0,1] if v.sum() > 2 else 0
    print(f"{name:<28s} {mae:6.2f} {rmse:6.2f} {bias:+7.2f} {corr:6.3f}")

# ========== PLOT ==========
months = np.arange(T)
tick_pos = [i for i, d in enumerate(model_dates) if d.endswith('-01') and int(d[:4]) % 2 == 1]
tick_lab = [model_dates[i][:4] for i in tick_pos]

fig, axes = plt.subplots(3, 1, figsize=(16, 12))
fig.suptitle('Model Unemployment Rate vs BLS Actual (2001-2026)', fontsize=14)

# Panel 1: UR overlay
ax = axes[0]
ax.plot(months, actual_ur, 'k-', lw=2, label='BLS Actual', alpha=0.8)
ax.plot(months, model_ur, 'b-', lw=1.5, label='Model', alpha=0.8)
ax.fill_between(months, actual_ur, model_ur,
                where=valid, alpha=0.15, color='red', label='Gap')
ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Unemployment Rate: Model vs Actual')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab, fontsize=9)
ax.legend(fontsize=10); ax.grid(True, alpha=0.3)
ax.set_ylim(0, 20)

# Shade recessions
for s, e in [(0,35), (84,107), (230,231)]:
    s, e = max(0,s), min(T-1,e)
    ax.axvspan(s, e, alpha=0.08, color='gray')

# Panel 2: Prediction error
ax = axes[1]
ax.bar(months[valid], diff, width=1, color=np.where(diff > 0, 'red', 'blue'), alpha=0.5)
ax.axhline(0, color='k', lw=0.5)
ax.set_ylabel('Error (pp): Model - Actual')
ax.set_title('Prediction Error Over Time')
ax.set_xticks(tick_pos); ax.set_xticklabels(tick_lab, fontsize=9)
ax.grid(True, alpha=0.3)

# Panel 3: Scatter
ax = axes[2]
ax.scatter(actual_ur[valid], model_ur[valid], s=8, alpha=0.4, c='blue')
mn, mx = 0, max(actual_ur[valid].max(), model_ur[valid].max()) + 1
ax.plot([mn, mx], [mn, mx], 'r--', lw=1, label='Perfect fit')
ax.set_xlabel('BLS Actual UR (%)'); ax.set_ylabel('Model UR (%)')
ax.set_title(f'Scatter (corr = {np.corrcoef(model_ur[valid], actual_ur[valid])[0,1]:.3f})')
ax.legend(); ax.grid(True, alpha=0.3)
ax.set_xlim(mn, mx); ax.set_ylim(mn, mx)
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('Phase3_Output/figures/prediction_evaluation.png', dpi=150, bbox_inches='tight')
print(f"\nFigure saved to Phase3_Output/figures/prediction_evaluation.png")
