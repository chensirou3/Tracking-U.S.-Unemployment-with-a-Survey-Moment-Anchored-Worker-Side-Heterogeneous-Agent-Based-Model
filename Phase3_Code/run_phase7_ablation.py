"""
Phase 7 Real-Data Ablation: heterogeneity flattening.
Uses baseline version. Tests each of 6 MVP heterogeneities.
Reports OOS performance degradation.
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.phase7_engine import (
    run_version, compute_window_metrics, load_candidates, get_targets
)

os.makedirs('Phase3_Output/phase7', exist_ok=True)

ABLATIONS = [
    'none',              # baseline (no ablation)
    'income_exp',        # flatten income expectation
    'labor_frag',        # flatten labor fragility
    'liquidity',         # flatten liquidity (all Buffer)
    'search',            # flatten search friction
    'housing',           # flatten housing mobility (all Renter)
    'consumption_rule',  # flatten consumption type (all Smoother)
]

SEEDS = [42, 137, 2024]  # 3 seeds for speed

print("=" * 60)
print("PHASE 7 REAL-DATA ABLATION (heterogeneity flattening)")
print("=" * 60)

versions = load_candidates()
baseline_params = versions['baseline']['params']
env, tgt_ur, tgt_lfpr, tgt_epop = get_targets()

results = {}
t0 = time.time()

for abl in ABLATIONS:
    print(f"\nAblation: {abl}")
    metrics_by_seed = []
    for seed in SEEDS:
        hist = run_version(baseline_params, seed=seed, flatten_dim=abl, env=env)
        m = compute_window_metrics(hist, tgt_ur, tgt_lfpr, tgt_epop, window='oos')
        # Also train window for comparison
        m_train = compute_window_metrics(hist, tgt_ur, tgt_lfpr, tgt_epop, window='train')
        metrics_by_seed.append({'oos': m, 'train': m_train})

    # Aggregate
    agg = {}
    for window in ['train', 'oos']:
        agg[window] = {}
        for k in ['ur_rmse', 'ur_mae', 'ur_corr', 'lfpr_rmse', 'epop_rmse',
                  'eu_mean', 'ue_mean', 'ur_mean', 'total_loss']:
            vals = [mb[window].get(k, np.nan) for mb in metrics_by_seed]
            vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
            agg[window][k + '_mean'] = float(np.mean(vals)) if vals else np.nan
            agg[window][k + '_std'] = float(np.std(vals)) if vals else np.nan
    results[abl] = agg
    oos_ur = agg['oos']['ur_rmse_mean']
    print(f"  OOS UR RMSE: {oos_ur:.4f} ({oos_ur*100:.2f} pp)")

elapsed = time.time() - t0
print(f"\nTotal time: {elapsed:.1f}s")

# Compute degradation
print("\n" + "=" * 80)
print("ABLATION SUMMARY (OOS window, baseline version)")
print("=" * 80)
print(f"{'Dim Removed':<20s} {'UR RMSE':>10s} {'ΔUR RMSE':>10s} {'UR Corr':>8s} {'LFPR RMSE':>10s} {'UE mean':>8s} {'Importance':>12s}")
print("-" * 90)

baseline_ur = results['none']['oos']['ur_rmse_mean']
baseline_lfpr = results['none']['oos']['lfpr_rmse_mean']

summary_rows = []
for abl in ABLATIONS:
    ur = results[abl]['oos']['ur_rmse_mean']
    lfpr = results[abl]['oos']['lfpr_rmse_mean']
    ue = results[abl]['oos']['ue_mean_mean']
    corr = results[abl]['oos']['ur_corr_mean']
    delta_ur = ur - baseline_ur

    # Classify importance
    delta_pp = delta_ur * 100  # in percentage points
    if abl == 'none':
        imp = '(baseline)'
    elif delta_pp > 2.0:
        imp = 'CORE'
    elif delta_pp > 0.5:
        imp = 'IMPORTANT'
    elif delta_pp > 0.1:
        imp = 'MINOR'
    else:
        imp = 'NEGLIGIBLE'

    print(f"{abl:<20s} {ur:>10.4f} {delta_ur:>+10.4f} {corr:>8.3f} "
          f"{lfpr:>10.4f} {ue:>8.4f} {imp:>12s}")
    summary_rows.append({
        'ablation': abl, 'ur_rmse': ur, 'delta_ur': delta_ur,
        'delta_pp': delta_pp, 'ur_corr': corr, 'lfpr_rmse': lfpr,
        'ue_mean': ue, 'importance': imp,
    })

# Save
with open('Phase3_Output/phase7/ablation_results.json', 'w') as f:
    json.dump({'baseline_ur_rmse': baseline_ur,
               'results': results, 'summary': summary_rows}, f, indent=2)
print("\nSaved to Phase3_Output/phase7/ablation_results.json")
