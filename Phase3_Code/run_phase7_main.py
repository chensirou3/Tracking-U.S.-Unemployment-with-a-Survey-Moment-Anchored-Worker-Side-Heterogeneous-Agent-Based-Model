"""
Phase 7 Main Runs: 3 versions x 5 seeds, full window metrics.
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.phase7_engine import (
    run_version, compute_window_metrics, load_candidates, get_targets,
    WINDOWS
)

os.makedirs('Phase3_Output/phase7', exist_ok=True)

SEEDS = [42, 137, 2024, 888, 1234]
versions = load_candidates()
env, tgt_ur, tgt_lfpr, tgt_epop = get_targets()

print("=" * 60)
print("PHASE 7 MAIN RUNS")
print("=" * 60)
print(f"Versions: {list(versions.keys())}")
print(f"Seeds: {SEEDS}")
print(f"Windows: {list(WINDOWS.keys())}")

all_runs = {}  # {version: {seed: history}}
all_metrics = {}  # {version: {seed: {window: metrics}}}

t0 = time.time()
for vname, vdata in versions.items():
    params = vdata['params']
    all_runs[vname] = {}
    all_metrics[vname] = {}
    print(f"\n=== {vname.upper()} ===")
    for seed in SEEDS:
        hist = run_version(params, seed=seed, env=env)
        all_runs[vname][seed] = hist
        all_metrics[vname][seed] = {}
        for window in ['train', 'val', 'oos']:
            m = compute_window_metrics(hist, tgt_ur, tgt_lfpr, tgt_epop, window)
            all_metrics[vname][seed][window] = m

        oos = all_metrics[vname][seed]['oos']
        print(f"  seed={seed}: OOS UR_RMSE={oos['ur_rmse']:.4f}, "
              f"Corr={oos['ur_corr']:.3f}, LFPR_RMSE={oos['lfpr_rmse']:.4f}")

elapsed = time.time() - t0
print(f"\nTotal time: {elapsed:.1f}s")

# Aggregate across seeds
summary = {}
for vname in versions:
    summary[vname] = {}
    for window in ['train', 'val', 'oos']:
        keys = ['ur_rmse', 'ur_mae', 'ur_corr', 'lfpr_rmse', 'epop_rmse',
                'eu_mean', 'ue_mean', 'h2m_mean', 'ur_mean', 'lfpr_mean',
                'total_loss', 'tier1_loss', 'tier2_loss']
        summary[vname][window] = {}
        for k in keys:
            vals = [all_metrics[vname][s][window].get(k, np.nan) for s in SEEDS]
            vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
            summary[vname][window][k + '_mean'] = float(np.mean(vals)) if vals else np.nan
            summary[vname][window][k + '_std'] = float(np.std(vals)) if vals else np.nan

# Print summary
print("\n" + "=" * 80)
print("SUMMARY (mean +/- std across seeds)")
print("=" * 80)
print(f"\n{'Version':<12s} {'Window':<6s} {'UR_RMSE':>10s} {'UR_Corr':>9s} {'LFPR_RMSE':>10s} {'EPOP_RMSE':>10s} {'TotalLoss':>10s}")
print("-" * 80)
for vname in ['conservative', 'baseline', 'aggressive']:
    for window in ['train', 'val', 'oos']:
        s = summary[vname][window]
        print(f"{vname:<12s} {window:<6s} "
              f"{s['ur_rmse_mean']:.4f}+/-{s['ur_rmse_std']:.3f} "
              f"{s['ur_corr_mean']:>6.3f}  "
              f"{s['lfpr_rmse_mean']:.4f}+/-{s['lfpr_rmse_std']:.3f}  "
              f"{s['epop_rmse_mean']:.4f}  "
              f"{s['total_loss_mean']:.4f}")

# Save
with open('Phase3_Output/phase7/main_run_metrics.json', 'w') as f:
    json.dump({'summary': summary, 'all_metrics': all_metrics,
               'seeds': SEEDS, 'windows': list(WINDOWS.keys())},
              f, indent=2, default=str)

# Save selected history series for plotting
plot_data = {}
for vname in versions:
    # Use seed 42 as representative
    h = all_runs[vname][42]
    plot_data[vname] = {
        'ur': [x['unemployment_rate'] for x in h],
        'lfpr': [x['lfpr'] for x in h],
        'epop': [x['epop'] for x in h],
        'eu_rate': [x['eu_rate'] for x in h],
        'ue_rate': [x['ue_rate'] for x in h],
        'h2m_share': [x['h2m_share'] for x in h],
    }
np.savez_compressed('Phase3_Output/phase7/main_run_series.npz',
                     dates=np.array(env.dates),
                     target_ur=tgt_ur, target_lfpr=tgt_lfpr, target_epop=tgt_epop,
                     **{f'{v}_{k}': np.array(plot_data[v][k])
                        for v in plot_data for k in plot_data[v]})

print("\nSaved to Phase3_Output/phase7/main_run_metrics.json + main_run_series.npz")
