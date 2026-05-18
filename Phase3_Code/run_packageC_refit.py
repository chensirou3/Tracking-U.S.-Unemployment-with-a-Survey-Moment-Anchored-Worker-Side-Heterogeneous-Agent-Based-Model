"""
Package C - Bounded Refit Ladder runner.
For each Core level L0..L6, do 30 LHS samples in Phase 5 prior bands,
pick best by train loss, then evaluate with 3 seeds on test window.
"""
import sys, os, json, time, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.packageC_engine import (
    run_level, history_to_dict, test_window_metrics, train_loss,
    CORE_LADDER, CORE_ORDER,
)
from Phase3_Code.phase7_engine import load_candidates, get_targets
from Phase3_Code.packageA_engine import lhs_samples
from Phase3_Code.calibration_engine import param_names

os.makedirs('Phase3_Output/packageC', exist_ok=True)
os.makedirs('Phase3_Output/packageC/run_logs', exist_ok=True)

N_LHS = 30
SEEDS = [42, 137, 2024]
LHS_SEED = 42


def main():
    t0 = time.time()
    env, t_ur, t_lfpr, t_epop = get_targets()
    samples = lhs_samples(N_LHS, seed=LHS_SEED)  # (N_LHS+1, 14) including center
    N_TOTAL = samples.shape[0]
    print("=" * 72)
    print(f"PACKAGE C - Refit Ladder ({len(CORE_ORDER)} levels x {N_TOTAL} LHS x 1 seed LHS)")
    print("=" * 72)

    rows = []
    best_params_per_level = {}

    for lid in CORE_ORDER:
        active = CORE_LADDER[lid]
        print(f"\n--- {lid} (dim={len(active)}) ---")
        t_level = time.time()
        # LHS loop
        lhs_log = []
        for i in range(N_TOTAL):
            pvec = samples[i]
            pdict = {param_names[j]: float(pvec[j]) for j in range(len(param_names))}
            hist = run_level(pdict, active, seed=LHS_SEED, env=env)
            arr = history_to_dict(hist)
            tl = train_loss(arr, t_ur, t_lfpr, t_epop)
            m = test_window_metrics(arr, t_ur, t_lfpr, t_epop)
            lhs_log.append({'idx': i, 'train_loss': tl, 'test_ur_rmse_pp': m['ur_rmse_pp']})
            if i % 10 == 0 or i == N_TOTAL - 1:
                print(f"  LHS {i+1}/{N_TOTAL}  train_L={tl:.3f}  test_UR={m['ur_rmse_pp']:.3f}pp  "
                      f"elapsed={time.time()-t0:.0f}s")
        best = min(lhs_log, key=lambda x: x['train_loss'])
        best_idx = best['idx']
        best_pvec = samples[best_idx]
        best_pdict = {param_names[j]: float(best_pvec[j]) for j in range(len(param_names))}
        best_params_per_level[lid] = best_pdict

        # Log LHS details
        with open(f'Phase3_Output/packageC/run_logs/{lid}_lhs.json', 'w') as f:
            json.dump({
                'level': lid, 'active': sorted(active),
                'best_idx': best_idx, 'best_train_loss': best['train_loss'],
                'best_params': best_pdict, 'lhs_log': lhs_log
            }, f, indent=2)

        # 3-seed evaluation at best point
        seed_metrics = []
        for seed in SEEDS:
            hist = run_level(best_pdict, active, seed=seed, env=env)
            arr = history_to_dict(hist)
            m = test_window_metrics(arr, t_ur, t_lfpr, t_epop)
            seed_metrics.append(m)

        agg = {'level': lid, 'n_active_dim': len(active),
               'active_dims': '|'.join(sorted(active)),
               'best_train_loss': best['train_loss']}
        for k in seed_metrics[0].keys():
            vals = [sm[k] for sm in seed_metrics]
            agg[k + '_mean'] = float(np.mean(vals))
            agg[k + '_std'] = float(np.std(vals))
        rows.append(agg)
        print(f"  >> BEST  idx={best_idx}  test_UR_RMSE={agg['ur_rmse_pp_mean']:.3f}+/-{agg['ur_rmse_pp_std']:.3f}  "
              f"level_time={time.time()-t_level:.0f}s")

    # CSV
    fields = ['level', 'n_active_dim', 'active_dims', 'best_train_loss',
              'ur_rmse_pp_mean', 'ur_rmse_pp_std', 'ur_mae_pp_mean',
              'ur_corr_mean', 'lfpr_rmse_pp_mean', 'epop_rmse_pp_mean',
              'eu_mean_mean', 'ue_mean_mean', 'h2m_share_mean',
              'avg_buffer_mean', 'avg_dur_mean']
    with open('Phase3_Output/packageC/refit_ladder_results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})

    # Save best params
    with open('Phase3_Output/packageC/refit_best_params.json', 'w') as f:
        json.dump(best_params_per_level, f, indent=2)

    print("\n" + "=" * 72)
    print("SUMMARY (Refit Ladder)")
    print("=" * 72)
    for r in rows:
        print(f"  {r['level']:4s} dim={r['n_active_dim']}  "
              f"UR_RMSE={r['ur_rmse_pp_mean']:.3f}+/-{r['ur_rmse_pp_std']:.3f}  "
              f"LFPR={r['lfpr_rmse_pp_mean']:.3f}  EPOP={r['epop_rmse_pp_mean']:.3f}")
    print(f"\nTotal time: {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
