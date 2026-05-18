"""
Package B Step 1: cache full 302-month ABM trajectories.
4 ABM models (M0/D1/D2/D3) x 3 seeds x {UR, LFPR, EPOP}.
Uses Phase 6 baseline parameters (= Phase 7/8 main version).
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.phase7_engine import run_version, load_candidates
from Phase3_Code.phase8_derived import run_homogeneous, run_simplified, run_labor_only
from Phase3_Code.environment_real import RealEnvironment

os.makedirs('Phase3_Output/packageB', exist_ok=True)

SEEDS = [42, 137, 2024]
SERIES = ['unemployment_rate', 'lfpr', 'epop']


def hist_to_arrays(hist):
    return {k: np.array([h[k] for h in hist]) for k in SERIES}


def main():
    t0 = time.time()
    versions = load_candidates()
    params = versions['baseline']['params']
    env = RealEnvironment(data_dir='Phase3_Data')

    runners = {
        'M0_Main': lambda p, s: run_version(p, seed=s, env=env),
        'D1_Homogeneous': lambda p, s: run_homogeneous(p, s, env),
        'D2_Simplified': lambda p, s: run_simplified(p, s, env),
        'D3_LaborOnly': lambda p, s: run_labor_only(p, s, env),
    }

    print("=" * 72)
    print(f"PACKAGE B - ABM trajectory cache: {len(runners)} models x {len(SEEDS)} seeds")
    print("=" * 72)

    save_dict = {}
    for mname, runner in runners.items():
        print(f"\n{mname}:")
        for seed in SEEDS:
            t1 = time.time()
            hist = runner(params, seed)
            arrs = hist_to_arrays(hist)
            for k, v in arrs.items():
                save_dict[f'{mname}_seed{seed}_{k}'] = v
            print(f"  seed={seed}  dt={time.time()-t1:.1f}s  "
                  f"UR_mean={arrs['unemployment_rate'].mean():.3f}")

    save_dict['seeds'] = np.array(SEEDS)
    save_dict['dates'] = np.array(env.dates)
    np.savez_compressed('Phase3_Output/packageB/abm_trajectories.npz', **save_dict)
    print(f"\nSaved abm_trajectories.npz  [total {time.time()-t0:.0f}s]")


if __name__ == '__main__':
    main()
