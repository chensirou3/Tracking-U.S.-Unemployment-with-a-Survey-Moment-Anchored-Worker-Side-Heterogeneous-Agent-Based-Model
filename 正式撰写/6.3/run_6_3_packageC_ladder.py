"""
Section 6.3 rerun — Package C heterogeneity ladder.

Levels: Core L0..L6 (7) + Layer G2, G3 (2 unique, since G1==L2 and G4==L6).
Seeds: 5 (42, 137, 2024, 888, 1234). Parameter source: candidate_baseline.

Output:
  - 正式撰写/6.3/ladder_metrics.json
  - 正式撰写/6.3/ladder_series.npz   (per-seed UR/LFPR/EPOP for each level)
"""
import os, sys, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Phase3_Code.packageC_engine import (
    run_level, CORE_LADDER, CORE_ORDER, LAYER_LADDER,
)
from Phase3_Code.phase7_engine import (
    load_candidates, get_targets, compute_window_metrics,
)

SEEDS = [42, 137, 2024, 888, 1234]
EVAL_WINDOWS = ['train', 'val', 'oos']
OUT_DIR = '正式撰写/6.3'


def main():
    versions = load_candidates()
    params = versions['baseline']['params']
    env, t_ur, t_lfpr, t_epop = get_targets()

    # Unique level registry: 7 Core + 2 Layer (G2, G3)
    levels = {lid: {'ladder': 'core', 'active': CORE_LADDER[lid]} for lid in CORE_ORDER}
    levels['G2'] = {'ladder': 'layer', 'active': LAYER_LADDER['G2']}
    levels['G3'] = {'ladder': 'layer', 'active': LAYER_LADDER['G3']}

    print("=" * 78)
    print(f"PACKAGE C LADDER RERUN (6.3) — {len(levels)} levels × {len(SEEDS)} seeds")
    print(f"  windows: {EVAL_WINDOWS}  period: 2001-01..2026-02 ({env.T} months)")
    print(f"  parameters from candidate_baseline.json")
    print("=" * 78)

    all_metrics = {}
    series_ur = {}
    series_lfpr = {}
    series_epop = {}
    t0 = time.time()

    for lid, spec in levels.items():
        active = sorted(spec['active'])
        print(f"\n[{lid}]  ladder={spec['ladder']}  n_active={len(active)}  active={active}")
        all_metrics[lid] = {'ladder': spec['ladder'],
                            'active_dims': '|'.join(active),
                            'n_active_dim': len(active),
                            'per_seed': {}}
        ur_mat = np.zeros((len(SEEDS), env.T))
        lfpr_mat = np.zeros((len(SEEDS), env.T))
        epop_mat = np.zeros((len(SEEDS), env.T))
        for i, sd in enumerate(SEEDS):
            ts = time.time()
            hist = run_level(params, set(active), seed=sd, env=env)
            ur_mat[i]   = np.array([x['unemployment_rate'] for x in hist])
            lfpr_mat[i] = np.array([x['lfpr'] for x in hist])
            epop_mat[i] = np.array([x['epop'] for x in hist])
            per = {}
            for w in EVAL_WINDOWS:
                per[w] = compute_window_metrics(hist, t_ur, t_lfpr, t_epop, w)
            all_metrics[lid]['per_seed'][str(sd)] = per
            m = per['oos']
            print(f"  seed={sd}: OOS UR_RMSE={m['ur_rmse']*100:.3f} pp  "
                  f"Corr={m['ur_corr']:.3f}  LFPR={m['lfpr_rmse']*100:.3f} pp  "
                  f"EPOP={m['epop_rmse']*100:.3f} pp  ({time.time()-ts:.1f}s)")
        series_ur[lid] = ur_mat
        series_lfpr[lid] = lfpr_mat
        series_epop[lid] = epop_mat

    keys = ['ur_rmse', 'ur_mae', 'ur_corr', 'lfpr_rmse', 'epop_rmse',
            'eu_mean', 'ue_mean', 'h2m_mean', 'buf_mean', 'dur_mean',
            'ur_mean', 'lfpr_mean', 'total_loss']
    summary = {}
    for lid in all_metrics:
        summary[lid] = {'ladder': all_metrics[lid]['ladder'],
                        'active_dims': all_metrics[lid]['active_dims'],
                        'n_active_dim': all_metrics[lid]['n_active_dim']}
        for w in EVAL_WINDOWS:
            summary[lid][w] = {}
            for k in keys:
                vals = [all_metrics[lid]['per_seed'][str(s)][w].get(k, np.nan) for s in SEEDS]
                vals = [x for x in vals if isinstance(x, (int, float)) and not np.isnan(x)]
                summary[lid][w][k + '_mean'] = float(np.mean(vals)) if vals else float('nan')
                summary[lid][w][k + '_std']  = float(np.std(vals)) if vals else float('nan')

    with open(os.path.join(OUT_DIR, 'ladder_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump({'all_metrics': all_metrics, 'summary': summary,
                   'seeds': SEEDS, 'windows': EVAL_WINDOWS,
                   'levels': list(levels.keys()),
                   'parameter_source': 'candidate_baseline'},
                  f, indent=2, default=str)

    npz = {'dates': np.array(env.dates),
           'target_ur': t_ur, 'target_lfpr': t_lfpr, 'target_epop': t_epop}
    for lid in series_ur:
        npz[f'{lid}_ur']   = series_ur[lid]
        npz[f'{lid}_lfpr'] = series_lfpr[lid]
        npz[f'{lid}_epop'] = series_epop[lid]
    np.savez_compressed(os.path.join(OUT_DIR, 'ladder_series.npz'), **npz)

    print(f"\nTotal wall time: {time.time()-t0:.1f}s")
    print(f"Saved: {OUT_DIR}/ladder_metrics.json")
    print(f"Saved: {OUT_DIR}/ladder_series.npz")


if __name__ == '__main__':
    main()
