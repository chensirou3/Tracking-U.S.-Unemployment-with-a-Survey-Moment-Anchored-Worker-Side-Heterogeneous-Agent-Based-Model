"""
Package D — main runner.
Loops over (mode, N, model, seed) and records RMSE + runtime + memory.
Writes results incrementally to CSV so partial runs are recoverable.
"""
import os, sys, json, time, csv, platform
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.packageD_engine import (
    run_sim, test_window_metrics, GRID, SEEDS, MODELS, MODES, HAS_PSUTIL
)
from Phase3_Code.phase7_engine import load_candidates, get_targets

OUT = 'Phase3_Output/packageD'
os.makedirs(OUT, exist_ok=True)

CSV_FIELDS = [
    'mode', 'N', 'model', 'seed',
    'ur_rmse_pp', 'ur_mae_pp', 'ur_corr',
    'lfpr_rmse_pp', 'epop_rmse_pp',
    'eu_mean', 'ue_mean', 'h2m_share', 'avg_buffer', 'avg_dur',
    'runtime_s', 'peak_mem_mb',
]


def log_env():
    info = {
        'os': platform.platform(),
        'python': sys.version.split()[0],
        'numpy': np.__version__,
        'cpu_count': os.cpu_count(),
        'omp_num_threads': os.environ.get('OMP_NUM_THREADS', ''),
        'mkl_num_threads': os.environ.get('MKL_NUM_THREADS', ''),
        'has_psutil': HAS_PSUTIL,
    }
    with open(f'{OUT}/environment_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    return info


def main():
    t_global = time.time()
    env_info = log_env()
    print("=" * 72)
    print("PACKAGE D - Agent Count Sensitivity")
    print(f"  {env_info['os']}")
    print(f"  Python {env_info['python']}, NumPy {env_info['numpy']}")
    print(f"  Grid: {GRID}")
    print(f"  Models: {MODELS}")
    print(f"  Modes: {MODES}")
    print(f"  Seeds: {SEEDS}  (n={len(SEEDS)})")
    total = len(MODES) * len(GRID) * len(MODELS) * len(SEEDS)
    print(f"  Total sims: {total}")
    print("=" * 72)

    versions = load_candidates()
    params = versions['baseline']['params']
    env, tu, tl, te = get_targets()

    # Warm-up run at small N to stabilise JIT/cache
    print("Warm-up...")
    run_sim(params, 5_000, 'M0', 42, 'subsample', env)
    print("  done")

    # Incremental CSV writer
    csv_path = f'{OUT}/agent_count_results.csv'
    series = {}   # keep seed=42 trajectories for plots
    rows = []

    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()

        counter = 0
        for mode in MODES:
            for N in GRID:
                for model in MODELS:
                    seed_metrics = []
                    for seed in SEEDS:
                        counter += 1
                        t0 = time.time()
                        try:
                            arr, dt, mem = run_sim(params, N, model, seed, mode, env)
                            m = test_window_metrics(arr, tu, tl, te)
                            row = {
                                'mode': mode, 'N': N, 'model': model, 'seed': seed,
                                'runtime_s': dt, 'peak_mem_mb': mem, **m,
                            }
                            w.writerow({k: row.get(k) for k in CSV_FIELDS})
                            f.flush()
                            rows.append(row)
                            seed_metrics.append(m)
                            if seed == 42:
                                key = f'{mode}_N{N}_{model}'
                                series[f'{key}_ur'] = arr['unemployment_rate']
                                series[f'{key}_lfpr'] = arr['lfpr']
                                series[f'{key}_epop'] = arr['epop']
                        except Exception as e:
                            print(f"  !! FAILED mode={mode} N={N} model={model} seed={seed}: {e}")
                            row = {'mode': mode, 'N': N, 'model': model, 'seed': seed,
                                   'runtime_s': float('nan'), 'peak_mem_mb': float('nan'),
                                   'ur_rmse_pp': float('nan'), 'ur_mae_pp': float('nan'),
                                   'ur_corr': float('nan'), 'lfpr_rmse_pp': float('nan'),
                                   'epop_rmse_pp': float('nan'), 'eu_mean': float('nan'),
                                   'ue_mean': float('nan'), 'h2m_share': float('nan'),
                                   'avg_buffer': float('nan'), 'avg_dur': float('nan')}
                            w.writerow(row); f.flush()
                            rows.append(row)

                    if seed_metrics:
                        urs = [x['ur_rmse_pp'] for x in seed_metrics]
                        elapsed = time.time() - t_global
                        pct = counter / total * 100
                        print(f"  [{counter:3d}/{total}  {pct:5.1f}%  {elapsed:5.0f}s]  "
                              f"mode={mode:10s} N={N:6d} {model}  "
                              f"UR_RMSE={np.mean(urs):.3f}+/-{np.std(urs, ddof=1):.3f}pp")

    np.savez_compressed(f'{OUT}/agent_count_series.npz', **series)
    print("\n" + "=" * 72)
    print(f"DONE.  Total time = {(time.time()-t_global)/60:.1f} min")
    print(f"Saved: {csv_path}")
    print(f"       {OUT}/agent_count_series.npz  ({len(series)//3} seed=42 trajectories)")
    print("=" * 72)


if __name__ == '__main__':
    main()
