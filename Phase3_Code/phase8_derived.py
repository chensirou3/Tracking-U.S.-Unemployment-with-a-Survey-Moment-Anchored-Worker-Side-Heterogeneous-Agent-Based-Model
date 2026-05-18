"""
Phase 8 Derived Controls:
- D1 Homogeneous ABM: flatten ALL 6 heterogeneity dims
- D2 Simplified Structural: turn off all advanced mechanisms, minimal labor
- D3 Labor-Only ABM: disable household outer ring mechanisms

All derived models use the same Phase 7 baseline parameter values where applicable,
same environment data, same population file.
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.phase7_engine import (
    run_version, compute_window_metrics, load_candidates, get_targets,
    flatten_heterogeneity, PARAM_MAP, WINDOWS
)
from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config, all_off_config

os.makedirs('Phase3_Output/phase8', exist_ok=True)


# ============================================================
# EXTENDED FLATTENING: all dims at once
# ============================================================
def flatten_all_heterogeneity(cs, ds, bp):
    """D1: Homogeneous ABM - flatten all 6 MVP dims."""
    for dim in ['income_exp', 'labor_frag', 'liquidity', 'search',
                'housing', 'consumption_rule']:
        flatten_heterogeneity(cs, ds, bp, dim)


# ============================================================
# RUN DERIVED MODELS
# ============================================================
def run_homogeneous(params, seed, env):
    """D1: Same mechanisms, no heterogeneity."""
    cfg = default_config()
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    flatten_all_heterogeneity(sim.cs, sim.ds, sim.bp)
    return sim.run(verbose=False)


def run_simplified(params, seed, env):
    """D2: Minimal structure - all advanced mechanisms off, only basic labor."""
    cfg = all_off_config()
    # Keep matching competition enabled (basic labor market needs it)
    cfg['matching_competition']['enabled'] = True
    if 'vacancy_rate' in params:
        cfg['matching_competition']['vacancy_rate'] = params['vacancy_rate']
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    flatten_all_heterogeneity(sim.cs, sim.ds, sim.bp)
    return sim.run(verbose=False)


def run_labor_only(params, seed, env):
    """D3: Full heterogeneity + labor mechanisms, household outer ring disabled."""
    cfg = default_config()
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val
    # Disable household outer ring
    for m in ['effective_mpc_adjustment', 'consumption_sequencing',
              'buffer_consumption_ordering', 'liquidity_constraint_modifier']:
        cfg[m]['enabled'] = False
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    return sim.run(verbose=False)


# ============================================================
# MAIN RUNNER
# ============================================================
def main():
    versions = load_candidates()
    params = versions['baseline']['params']
    env, tgt_ur, tgt_lfpr, tgt_epop = get_targets()

    SEEDS = [42, 137, 2024]

    models = {
        'M0_Main': lambda s: run_version(params, seed=s, env=env),
        'D1_Homogeneous': lambda s: run_homogeneous(params, s, env),
        'D2_Simplified': lambda s: run_simplified(params, s, env),
        'D3_LaborOnly': lambda s: run_labor_only(params, s, env),
    }

    print("=" * 70)
    print("PHASE 8: DERIVED CONTROL RUNS")
    print("=" * 70)

    all_results = {}
    t0 = time.time()
    for mname, run_fn in models.items():
        print(f"\n{mname}:")
        metrics_list = []
        series = {}
        for seed in SEEDS:
            hist = run_fn(seed)
            m_oos = compute_window_metrics(hist, tgt_ur, tgt_lfpr, tgt_epop, 'oos')
            m_train = compute_window_metrics(hist, tgt_ur, tgt_lfpr, tgt_epop, 'train')
            metrics_list.append({'oos': m_oos, 'train': m_train})
            if seed == 42:
                series = {
                    'ur': [x['unemployment_rate'] for x in hist],
                    'lfpr': [x['lfpr'] for x in hist],
                    'epop': [x['epop'] for x in hist],
                }
            print(f"  seed={seed}: OOS UR_RMSE={m_oos['ur_rmse']:.4f}, "
                  f"Corr={m_oos['ur_corr']:.3f}, LFPR={m_oos['lfpr_rmse']:.4f}")

        # Aggregate
        agg = {}
        for window in ['train', 'oos']:
            agg[window] = {}
            for k in ['ur_rmse', 'ur_mae', 'ur_corr', 'lfpr_rmse', 'epop_rmse',
                      'ue_mean', 'eu_mean', 'ur_mean', 'total_loss']:
                vals = [m[window].get(k, np.nan) for m in metrics_list]
                vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
                agg[window][k + '_mean'] = float(np.mean(vals)) if vals else np.nan
                agg[window][k + '_std'] = float(np.std(vals)) if vals else np.nan
        all_results[mname] = {'metrics': agg, 'series_seed42': series}

    # Save
    with open('Phase3_Output/phase8/derived_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    # Save series as npz
    save_dict = {}
    for mname, r in all_results.items():
        for k, v in r['series_seed42'].items():
            save_dict[f'{mname}_{k}'] = np.array(v)
    save_dict['target_ur'] = tgt_ur
    save_dict['target_lfpr'] = tgt_lfpr
    save_dict['target_epop'] = tgt_epop
    save_dict['dates'] = np.array(env.dates)
    np.savez_compressed('Phase3_Output/phase8/derived_series.npz', **save_dict)

    print(f"\n{'='*70}\nTotal time: {time.time()-t0:.1f}s")
    print("Saved to Phase3_Output/phase8/derived_results.json + derived_series.npz")


if __name__ == '__main__':
    main()
