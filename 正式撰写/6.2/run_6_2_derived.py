"""
Section 6.2 rerun: Phase 8 Derived Controls + Source of Advantage.
4 variants (M0 full / D1 homogeneous / D2 simplified / D3 labor-only),
5 seeds (42, 137, 2024, 888, 1234), 3 evaluation windows (train, val, oos).
Saves per-seed metrics and per-seed UR/LFPR/EPOP trajectories for all variants.
"""
import os, sys, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Phase3_Code.phase7_engine import (
    run_version, compute_window_metrics, load_candidates, get_targets,
    flatten_heterogeneity, PARAM_MAP, WINDOWS,
)
from Phase3_Code.scheduler import Simulation
from Phase3_Code.mechanism_config import default_config, all_off_config

SEEDS = [42, 137, 2024, 888, 1234]
EVAL_WINDOWS = ['train', 'val', 'oos']
OUT_DIR = '正式撰写/6.2'
os.makedirs(OUT_DIR, exist_ok=True)


def flatten_all(cs, ds, bp):
    for dim in ['income_exp', 'labor_frag', 'liquidity', 'search',
                'housing', 'consumption_rule']:
        flatten_heterogeneity(cs, ds, bp, dim)


def _apply_params(cfg, params):
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val
    return cfg


def run_full(params, seed, env):
    return run_version(params, seed=seed, env=env)


def run_homogeneous(params, seed, env):
    cfg = _apply_params(default_config(), params)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    flatten_all(sim.cs, sim.ds, sim.bp)
    return sim.run(verbose=False)


def run_simplified(params, seed, env):
    cfg = all_off_config()
    cfg['matching_competition']['enabled'] = True
    if 'vacancy_rate' in params:
        cfg['matching_competition']['vacancy_rate'] = params['vacancy_rate']
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    flatten_all(sim.cs, sim.ds, sim.bp)
    return sim.run(verbose=False)


def run_labor_only(params, seed, env):
    cfg = _apply_params(default_config(), params)
    for m in ['effective_mpc_adjustment', 'consumption_sequencing',
              'buffer_consumption_ordering', 'liquidity_constraint_modifier']:
        cfg[m]['enabled'] = False
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    return sim.run(verbose=False)


VARIANTS = [
    ('M0_Full',        run_full),
    ('D1_Homogeneous', run_homogeneous),
    ('D2_Simplified',  run_simplified),
    ('D3_LaborOnly',   run_labor_only),
]


def main():
    versions = load_candidates()
    params = versions['baseline']['params']
    env, t_ur, t_lfpr, t_epop = get_targets()

    print("=" * 72)
    print("PHASE 8 RERUN — Source of Advantage / Derived Controls (6.2)")
    print(f"  variants: {[v[0] for v in VARIANTS]}")
    print(f"  seeds: {SEEDS}")
    print(f"  windows: {EVAL_WINDOWS}")
    print(f"  full period: 2001-01..2026-02 ({env.T} months)")
    print(f"  parameters from candidate_baseline.json")
    print("=" * 72)

    all_metrics = {}
    series = {}
    t0 = time.time()

    for vname, runner in VARIANTS:
        print(f"\n[{vname}]")
        all_metrics[vname] = {}
        seed_ur_mat = np.zeros((len(SEEDS), env.T))
        seed_lfpr_mat = np.zeros((len(SEEDS), env.T))
        seed_epop_mat = np.zeros((len(SEEDS), env.T))
        for i, sd in enumerate(SEEDS):
            ts0 = time.time()
            hist = runner(params, sd, env)
            ur_arr = np.array([x['unemployment_rate'] for x in hist])
            lfpr_arr = np.array([x['lfpr'] for x in hist])
            epop_arr = np.array([x['epop'] for x in hist])
            seed_ur_mat[i] = ur_arr
            seed_lfpr_mat[i] = lfpr_arr
            seed_epop_mat[i] = epop_arr
            all_metrics[vname][str(sd)] = {}
            for w in EVAL_WINDOWS:
                all_metrics[vname][str(sd)][w] = compute_window_metrics(
                    hist, t_ur, t_lfpr, t_epop, w)
            m_oos = all_metrics[vname][str(sd)]['oos']
            print(f"  seed={sd}: OOS UR_RMSE={m_oos['ur_rmse']*100:.3f} pp  "
                  f"Corr={m_oos['ur_corr']:.3f}  LFPR_RMSE={m_oos['lfpr_rmse']*100:.3f} pp  "
                  f"EPOP_RMSE={m_oos['epop_rmse']*100:.3f} pp  ({time.time()-ts0:.1f}s)")
        series[vname] = {'ur': seed_ur_mat, 'lfpr': seed_lfpr_mat, 'epop': seed_epop_mat}

    # Aggregate across seeds
    summary = {}
    keys = ['ur_rmse', 'ur_mae', 'ur_corr', 'lfpr_rmse', 'epop_rmse',
            'ue_mean', 'eu_mean', 'h2m_mean', 'buf_mean', 'dur_mean',
            'ur_mean', 'lfpr_mean', 'total_loss']
    for vname in all_metrics:
        summary[vname] = {}
        for w in EVAL_WINDOWS:
            summary[vname][w] = {}
            for k in keys:
                vals = [all_metrics[vname][str(s)][w].get(k, np.nan) for s in SEEDS]
                vals = [v for v in vals if isinstance(v, (int, float)) and not np.isnan(v)]
                summary[vname][w][k + '_mean'] = float(np.mean(vals)) if vals else float('nan')
                summary[vname][w][k + '_std']  = float(np.std(vals)) if vals else float('nan')

    with open(os.path.join(OUT_DIR, 'derived_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump({'all_metrics': all_metrics, 'summary': summary,
                   'seeds': SEEDS, 'windows': EVAL_WINDOWS,
                   'variants': [v[0] for v in VARIANTS],
                   'parameter_source': 'candidate_baseline'}, f, indent=2, default=str)

    npz = {'dates': np.array(env.dates),
           'target_ur': t_ur, 'target_lfpr': t_lfpr, 'target_epop': t_epop}
    for vname, s in series.items():
        npz[f'{vname}_ur']   = s['ur']
        npz[f'{vname}_lfpr'] = s['lfpr']
        npz[f'{vname}_epop'] = s['epop']
    np.savez_compressed(os.path.join(OUT_DIR, 'derived_series.npz'), **npz)

    print(f"\nTotal wall time: {time.time()-t0:.1f}s")
    print(f"Saved: {OUT_DIR}/derived_metrics.json")
    print(f"Saved: {OUT_DIR}/derived_series.npz")


if __name__ == '__main__':
    main()
