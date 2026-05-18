"""
Section 6.3 rerun — Phase 7 Heterogeneity / Mechanism Ablation.

20 configurations × 5 seeds = 100 simulations:
  - 1 baseline (full heterogeneous ABM, no ablation)
  - 6 dimension flattenings (income_exp, labor_frag, liquidity, search,
    housing, consumption_rule)
  - 13 mechanism on/off ablations (one mechanism disabled at a time)

Output:
  - 正式撰写/6.3/ablation_metrics.json   (per-seed metrics across 3 windows)
  - 正式撰写/6.3/ablation_series.npz     (per-seed UR/LFPR/EPOP/EU/UE trajectories)
"""
import os, sys, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Phase3_Code.phase7_engine import (
    compute_window_metrics, load_candidates, get_targets,
    flatten_heterogeneity, PARAM_MAP,
)
from Phase3_Code.scheduler import Simulation
from Phase3_Code.mechanism_config import default_config

SEEDS = [42, 137, 2024, 888, 1234]
EVAL_WINDOWS = ['train', 'val', 'oos']
OUT_DIR = '正式撰写/6.3'

DIMS = ['income_exp', 'labor_frag', 'liquidity', 'search',
        'housing', 'consumption_rule']

MECHS = [
    'high_fragility_modifier',
    'liquidity_constraint_modifier',
    'housing_lockin_modifier',
    'fragility_x_liquidity_interaction',
    'matching_competition',
    'discouraged_worker',
    'housing_reentry_friction',
    'expectation_participation',
    'effective_mpc_adjustment',
    'consumption_sequencing',
    'buffer_consumption_ordering',
    'state_dependent_expectation',
    'experience_dependent_expectation',
]


def _apply_params(cfg, params):
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val
    return cfg


def run_variant(params, seed, env, variant_kind, target):
    """variant_kind in {'none','dim','mech'}, target = name."""
    cfg = _apply_params(default_config(), params)
    if variant_kind == 'mech':
        cfg[target]['enabled'] = False
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    if variant_kind == 'dim':
        flatten_heterogeneity(sim.cs, sim.ds, sim.bp, target)
    return sim.run(verbose=False)


def main():
    versions = load_candidates()
    params = versions['baseline']['params']
    env, t_ur, t_lfpr, t_epop = get_targets()

    variants = [('baseline', 'none', 'none')]
    variants += [(f'dim_{d}', 'dim', d) for d in DIMS]
    variants += [(f'mech_{m}', 'mech', m) for m in MECHS]

    print("=" * 78)
    print("PHASE 7 ABLATION RERUN (6.3) — dim flattenings + mechanism on/off")
    print(f"  configurations: {len(variants)}  seeds: {SEEDS}")
    print(f"  windows: {EVAL_WINDOWS}  period: 2001-01..2026-02 ({env.T} months)")
    print(f"  parameters from candidate_baseline.json")
    print("=" * 78)

    all_metrics = {}
    series_ur = {}
    series_lfpr = {}
    series_epop = {}
    series_eu = {}
    series_ue = {}
    t0 = time.time()

    for vname, kind, target in variants:
        print(f"\n[{vname}]  kind={kind}  target={target}")
        all_metrics[vname] = {'kind': kind, 'target': target, 'per_seed': {}}
        ur_mat = np.zeros((len(SEEDS), env.T))
        lfpr_mat = np.zeros((len(SEEDS), env.T))
        epop_mat = np.zeros((len(SEEDS), env.T))
        eu_mat = np.zeros((len(SEEDS), env.T))
        ue_mat = np.zeros((len(SEEDS), env.T))
        for i, sd in enumerate(SEEDS):
            ts = time.time()
            hist = run_variant(params, sd, env, kind, target)
            ur_mat[i]   = np.array([x['unemployment_rate'] for x in hist])
            lfpr_mat[i] = np.array([x['lfpr'] for x in hist])
            epop_mat[i] = np.array([x['epop'] for x in hist])
            eu_mat[i]   = np.array([x['eu_rate'] for x in hist])
            ue_mat[i]   = np.array([x['ue_rate'] for x in hist])
            per = {}
            for w in EVAL_WINDOWS:
                per[w] = compute_window_metrics(hist, t_ur, t_lfpr, t_epop, w)
            all_metrics[vname]['per_seed'][str(sd)] = per
            m = per['oos']
            print(f"  seed={sd}: OOS UR_RMSE={m['ur_rmse']*100:.3f} pp  "
                  f"Corr={m['ur_corr']:.3f}  LFPR={m['lfpr_rmse']*100:.3f} pp  "
                  f"EPOP={m['epop_rmse']*100:.3f} pp  ({time.time()-ts:.1f}s)")
        series_ur[vname] = ur_mat
        series_lfpr[vname] = lfpr_mat
        series_epop[vname] = epop_mat
        series_eu[vname] = eu_mat
        series_ue[vname] = ue_mat

    # Aggregate seed mean/std
    keys = ['ur_rmse', 'ur_mae', 'ur_corr', 'lfpr_rmse', 'epop_rmse',
            'eu_mean', 'ue_mean', 'h2m_mean', 'buf_mean', 'dur_mean',
            'ur_mean', 'lfpr_mean', 'total_loss']
    summary = {}
    for v in all_metrics:
        summary[v] = {'kind': all_metrics[v]['kind'], 'target': all_metrics[v]['target']}
        for w in EVAL_WINDOWS:
            summary[v][w] = {}
            for k in keys:
                vals = [all_metrics[v]['per_seed'][str(s)][w].get(k, np.nan) for s in SEEDS]
                vals = [x for x in vals if isinstance(x, (int, float)) and not np.isnan(x)]
                summary[v][w][k + '_mean'] = float(np.mean(vals)) if vals else float('nan')
                summary[v][w][k + '_std']  = float(np.std(vals)) if vals else float('nan')

    with open(os.path.join(OUT_DIR, 'ablation_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump({'all_metrics': all_metrics, 'summary': summary,
                   'seeds': SEEDS, 'windows': EVAL_WINDOWS,
                   'dims': DIMS, 'mechs': MECHS,
                   'variants': [v[0] for v in variants],
                   'parameter_source': 'candidate_baseline'},
                  f, indent=2, default=str)

    npz = {'dates': np.array(env.dates),
           'target_ur': t_ur, 'target_lfpr': t_lfpr, 'target_epop': t_epop}
    for v in series_ur:
        npz[f'{v}_ur']   = series_ur[v]
        npz[f'{v}_lfpr'] = series_lfpr[v]
        npz[f'{v}_epop'] = series_epop[v]
        npz[f'{v}_eu']   = series_eu[v]
        npz[f'{v}_ue']   = series_ue[v]
    np.savez_compressed(os.path.join(OUT_DIR, 'ablation_series.npz'), **npz)

    print(f"\nTotal wall time: {time.time()-t0:.1f}s")
    print(f"Saved: {OUT_DIR}/ablation_metrics.json")
    print(f"Saved: {OUT_DIR}/ablation_series.npz")


if __name__ == '__main__':
    main()
