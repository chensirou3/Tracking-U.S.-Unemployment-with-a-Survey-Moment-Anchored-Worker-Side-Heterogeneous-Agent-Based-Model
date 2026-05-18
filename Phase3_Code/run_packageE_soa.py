"""
Package E — Source-of-Advantage.

For each method's rank-1 candidate, re-run D1 (homogeneous) and D3 (no household
outer ring) with the same 3 seeds, then compute share_heterogeneity and
share_household. This tests whether the heterogeneity advantage is stable
across calibration methods.

Total: 5 methods x 2 derived x 3 seeds = 30 simulations (~15 minutes).
"""
import os, sys, time
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config
from Phase3_Code.calibration_engine import param_names, make_config
from Phase3_Code.phase8_derived import flatten_all_heterogeneity
from Phase3_Code.packageE_engine import SEEDS

RAW_CSV = 'Phase3_Output/packageE/method_raw_results.csv'
OUT_CSV = 'Phase3_Output/packageE/source_of_advantage_per_method.csv'
TEST_S, TEST_E = 252, 302


def _build_cfg_d1_d3(param_vec, model):
    """M0 = make_config; D1 = M0 cfg + flatten all (done later); D3 = M0 cfg with 4 mechs off."""
    cfg = make_config(param_vec)
    if model == 'D3':
        for m in ['effective_mpc_adjustment', 'consumption_sequencing',
                  'buffer_consumption_ordering', 'liquidity_constraint_modifier']:
            if m in cfg:
                cfg[m]['enabled'] = False
    return cfg


def _test_ur_rmse(history, target_ur):
    arr = np.array([h['unemployment_rate'] for h in history])
    tu = target_ur[TEST_S:TEST_E]
    vu = ~np.isnan(tu)
    return float(np.sqrt(np.mean((arr[TEST_S:TEST_E][vu] - tu[vu]) ** 2)) * 100)


def run_one(param_vec, model, seed, env, target_ur):
    cfg = _build_cfg_d1_d3(param_vec, model)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    if model == 'D1':
        flatten_all_heterogeneity(sim.cs, sim.ds, sim.bp)
    t0 = time.perf_counter()
    hist = sim.run(verbose=False)
    return _test_ur_rmse(hist, target_ur), time.perf_counter() - t0


def get_method_rank1(df, method_id):
    sub = df[df.method_id == method_id]
    best = sub.loc[sub['train_loss_mean'].idxmin()]
    pvec = np.array([best[f'p_{n}'] for n in param_names], dtype=float)
    return pvec, best['test_ur_rmse_pp'], int(best['eval_idx'])


def main():
    env = RealEnvironment(data_dir='Phase3_Data')
    from Phase3_Code.calibration_engine import target_ur

    df = pd.read_csv(RAW_CSV)
    rows = []
    t_total = time.perf_counter()
    for mid in ['M1_RS', 'M2_LHS', 'M3_Sobol', 'M4_CtF', 'M5_DE']:
        pvec, m0_ur, idx = get_method_rank1(df, mid)
        d1_urs, d3_urs = [], []
        for s in SEEDS:
            t0 = time.perf_counter()
            d1_ur, dt_d1 = run_one(pvec, 'D1', s, env, target_ur)
            d3_ur, dt_d3 = run_one(pvec, 'D3', s, env, target_ur)
            d1_urs.append(d1_ur); d3_urs.append(d3_ur)
            print(f'[{mid}] seed={s} D1={d1_ur:.3f}pp ({dt_d1:.1f}s)  '
                  f'D3={d3_ur:.3f}pp ({dt_d3:.1f}s)')

        d1_mean = float(np.mean(d1_urs)); d3_mean = float(np.mean(d3_urs))
        d1_std = float(np.std(d1_urs, ddof=1)); d3_std = float(np.std(d3_urs, ddof=1))
        share_het = 100.0 * (d1_mean - m0_ur) / d1_mean if d1_mean > 0 else np.nan
        share_hh = 100.0 * (d3_mean - m0_ur) / d3_mean if d3_mean > 0 else np.nan
        rows.append({
            'method_id': mid, 'rank1_eval_idx': idx,
            'M0_test_ur_rmse_pp': m0_ur,
            'D1_test_ur_rmse_pp': d1_mean, 'D1_std': d1_std,
            'D3_test_ur_rmse_pp': d3_mean, 'D3_std': d3_std,
            'share_heterogeneity_pct': share_het,
            'share_household_pct': share_hh,
        })
        print(f'[{mid}] M0={m0_ur:.3f}  D1={d1_mean:.3f}  D3={d3_mean:.3f}  '
              f'share_het={share_het:.1f}%  share_hh={share_hh:.1f}%')

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False)
    print(f'\nSaved {OUT_CSV}')
    print(out.to_string(index=False))
    print(f'\nTotal time: {(time.perf_counter()-t_total)/60:.1f} min')


if __name__ == '__main__':
    main()
