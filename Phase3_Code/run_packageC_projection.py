"""
Package C - Projection Ladder runner.
Fixed Phase 6 baseline params; flatten levels of heterogeneity.
Core 7 levels + Layer 2 new levels (G2, G3). L0/L2/L6 shared with Core.
Total 9 unique levels x 3 seeds = 27 sims.
"""
import sys, os, json, time, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.packageC_engine import (
    run_level, history_to_dict, test_window_metrics,
    CORE_LADDER, CORE_ORDER, LAYER_LADDER, LAYER_ORDER
)
from Phase3_Code.phase7_engine import load_candidates, get_targets

os.makedirs('Phase3_Output/packageC', exist_ok=True)

SEEDS = [42, 137, 2024]


def main():
    t0 = time.time()
    versions = load_candidates()
    params = versions['baseline']['params']
    env, t_ur, t_lfpr, t_epop = get_targets()

    # Build unique level list (Core first, then Layer unique ones)
    unique_levels = {}
    for lid in CORE_ORDER:
        unique_levels[lid] = {'ladder': 'core', 'active': CORE_LADDER[lid]}
    # Add Layer-only new levels; G1 == L2, G4 == L6
    unique_levels['G2'] = {'ladder': 'layer', 'active': LAYER_LADDER['G2']}
    unique_levels['G3'] = {'ladder': 'layer', 'active': LAYER_LADDER['G3']}

    print("=" * 72)
    print(f"PACKAGE C - Projection Ladder ({len(unique_levels)} levels x {len(SEEDS)} seeds)")
    print("=" * 72)

    rows = []
    all_series = {}

    for lid, spec in unique_levels.items():
        active = spec['active']
        print(f"\n{lid}  active={sorted(active)}  (dim={len(active)})")
        seed_metrics = []
        for seed in SEEDS:
            t1 = time.time()
            hist = run_level(params, active, seed=seed, env=env)
            arr = history_to_dict(hist)
            m = test_window_metrics(arr, t_ur, t_lfpr, t_epop)
            m['sim_time_s'] = time.time() - t1
            seed_metrics.append(m)
            if seed == 42:
                all_series[lid] = arr
            print(f"  seed={seed}  dt={time.time()-t1:.1f}s  "
                  f"UR_RMSE={m['ur_rmse_pp']:.3f}pp  LFPR_RMSE={m['lfpr_rmse_pp']:.3f}pp")

        # Aggregate across seeds
        agg = {}
        for k in seed_metrics[0].keys():
            vals = [sm[k] for sm in seed_metrics]
            agg[k + '_mean'] = float(np.mean(vals))
            agg[k + '_std'] = float(np.std(vals))
        agg.update({
            'level': lid, 'ladder': spec['ladder'], 'active_dims': '|'.join(sorted(active)),
            'n_active_dim': len(active),
        })
        rows.append(agg)

    # Save CSV
    fields = ['level', 'ladder', 'n_active_dim', 'active_dims',
              'ur_rmse_pp_mean', 'ur_rmse_pp_std', 'ur_mae_pp_mean',
              'ur_corr_mean', 'lfpr_rmse_pp_mean', 'epop_rmse_pp_mean',
              'eu_mean_mean', 'ue_mean_mean', 'h2m_share_mean',
              'avg_buffer_mean', 'avg_dur_mean', 'sim_time_s_mean']
    with open('Phase3_Output/packageC/projection_ladder_results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})

    # Save raw series (seed=42)
    save_dict = {}
    for lid, arr in all_series.items():
        for k, v in arr.items():
            save_dict[f'{lid}_{k}'] = v
    np.savez_compressed('Phase3_Output/packageC/projection_rawseries.npz', **save_dict)

    # Sanity prints
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for r in rows:
        print(f"  {r['level']:4s} ({r['ladder']:5s}) dim={r['n_active_dim']}  "
              f"UR_RMSE={r['ur_rmse_pp_mean']:.3f}+/-{r['ur_rmse_pp_std']:.3f}  "
              f"LFPR={r['lfpr_rmse_pp_mean']:.3f}  EPOP={r['epop_rmse_pp_mean']:.3f}  "
              f"h2m={r['h2m_share_mean']:.2f}  buf={r['avg_buffer_mean']:.2f}")

    print(f"\nTotal time: {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
