"""
Package E — calibration method sensitivity main runner.
Runs 5 methods × 200 evals × 3 seeds (= 3,000 sims) on the same search space.
Incremental CSV writing allows resume on crash.
"""
import os, sys, time, json, argparse
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.packageE_engine import (
    eval_candidate, rs_sample, lhs_sample, sobol_sample,
    ctf_stage1, ctf_stage2_bounds, ctf_stage2_sample,
    LOWS, HIGHS, BOUNDS, N_PARAMS, param_names,
)

OUT = 'Phase3_Output/packageE'
os.makedirs(OUT, exist_ok=True)
RAW_CSV = os.path.join(OUT, 'method_raw_results.csv')
TRAJ_NPZ = os.path.join(OUT, 'method_trajectories.npz')

BUDGET = 200
METHOD_SEEDS = {'M1_RS': 100, 'M2_LHS': 200, 'M3_Sobol': 300, 'M4_CtF': 400, 'M5_DE': 500}
TOP_K = 5


def _make_row(method_id, eval_idx, stage, param_vec, r):
    row = {
        'method_id': method_id, 'eval_idx': eval_idx, 'stage': stage,
        'runtime_s': r['runtime_s'], 'failed_seeds': r['failed_seeds'],
        'train_loss_mean': r['train_loss_mean'], 'train_loss_std': r['train_loss_std'],
        'val_loss_mean': r['val_loss_mean'], 'val_loss_std': r['val_loss_std'],
        'test_ur_rmse_pp': r.get('test_ur_rmse_pp', np.nan),
        'test_ur_rmse_pp_std': r.get('test_ur_rmse_pp_std', np.nan),
        'test_lfpr_rmse_pp': r.get('test_lfpr_rmse_pp', np.nan),
        'test_epop_rmse_pp': r.get('test_epop_rmse_pp', np.nan),
        'h2m_share_mean': r.get('h2m_share_mean', np.nan),
        'avg_buffer_mean': r.get('avg_buffer_mean', np.nan),
        'avg_dur_mean': r.get('avg_dur_mean', np.nan),
        'eu_mean': r.get('eu_mean', np.nan),
        'ue_mean': r.get('ue_mean', np.nan),
    }
    for i, n in enumerate(param_names):
        row[f'p_{n}'] = float(param_vec[i])
    return row


def _append_csv(row):
    df = pd.DataFrame([row])
    hdr = not os.path.exists(RAW_CSV)
    df.to_csv(RAW_CSV, mode='a', header=hdr, index=False)


def _already_done(method_id):
    """Return count of evals already recorded for this method_id (for resume)."""
    if not os.path.exists(RAW_CSV):
        return 0
    df = pd.read_csv(RAW_CSV)
    return int((df['method_id'] == method_id).sum())


class _TopKeeper:
    def __init__(self, k=TOP_K):
        self.k = k; self.items = []  # list of (train_loss, eval_idx, param_vec, histories)
    def offer(self, tl, idx, x, hists):
        if np.isnan(tl):
            return
        self.items.append((tl, idx, np.array(x), [np.asarray([[h['unemployment_rate'], h['lfpr'], h['epop']] for h in hist]) for hist in hists]))
        self.items.sort(key=lambda z: z[0])
        self.items = self.items[:self.k]


def _do_eval(method_id, eval_idx, stage, x, env, keeper):
    r = eval_candidate(x, env=env)
    row = _make_row(method_id, eval_idx, stage, x, r)
    _append_csv(row)
    keeper.offer(r['train_loss_mean'], eval_idx, x, r['histories'])
    return r


def run_fixed_design(method_id, samples, env, resume=0):
    keeper = _TopKeeper()
    for i in range(resume, samples.shape[0]):
        t0 = time.perf_counter()
        _do_eval(method_id, i, 'main', samples[i], env, keeper)
        print(f'[{method_id}] {i+1}/{samples.shape[0]} | {time.perf_counter()-t0:.1f}s')
    return keeper


def run_method_RS(env, resume=0):
    return run_fixed_design('M1_RS', rs_sample(BUDGET, METHOD_SEEDS['M1_RS']), env, resume)


def run_method_LHS(env, resume=0):
    return run_fixed_design('M2_LHS', lhs_sample(BUDGET, METHOD_SEEDS['M2_LHS']), env, resume)


def run_method_Sobol(env, resume=0):
    return run_fixed_design('M3_Sobol', sobol_sample(BUDGET, METHOD_SEEDS['M3_Sobol']), env, resume)


def run_method_CtF(env, resume=0):
    mid = 'M4_CtF'
    n_coarse = BUDGET // 2
    coarse = ctf_stage1(n_coarse, METHOD_SEEDS[mid])
    keeper = _TopKeeper()
    # stage 1
    for i in range(resume if resume < n_coarse else n_coarse, n_coarse):
        t0 = time.perf_counter()
        _do_eval(mid, i, 'coarse', coarse[i], env, keeper)
        print(f'[{mid}] coarse {i+1}/{n_coarse} | {time.perf_counter()-t0:.1f}s')
    # build refined bounds from coarse top-10
    df = pd.read_csv(RAW_CSV); cdf = df[(df.method_id == mid) & (df.stage == 'coarse')].copy()
    cdf = cdf.sort_values('train_loss_mean').head(10)
    top_params = cdf[[f'p_{n}' for n in param_names]].values
    lows_r, highs_r = ctf_stage2_bounds(top_params, padding_frac=0.10)
    np.savez(os.path.join(OUT, 'ctf_refined_bounds.npz'),
             lows=lows_r, highs=highs_r, param_names=np.array(param_names))
    # stage 2
    n_fine = BUDGET - n_coarse
    fine = ctf_stage2_sample(n_fine, METHOD_SEEDS[mid] + 1, lows_r, highs_r)
    start_fine = max(0, resume - n_coarse)
    for i in range(start_fine, n_fine):
        t0 = time.perf_counter()
        _do_eval(mid, n_coarse + i, 'fine', fine[i], env, keeper)
        print(f'[{mid}] fine {i+1}/{n_fine} | {time.perf_counter()-t0:.1f}s')
    return keeper


def run_method_DE(env, resume=0):
    """Budget-enforced DE via exception-on-budget."""
    from scipy.optimize import differential_evolution
    mid = 'M5_DE'; keeper = _TopKeeper(); counter = {'n': resume}

    class _BudgetExhausted(Exception):
        pass

    def objective(x):
        if counter['n'] >= BUDGET:
            raise _BudgetExhausted()
        t0 = time.perf_counter()
        r = _do_eval(mid, counter['n'], 'de', x, env, keeper)
        print(f'[{mid}] {counter["n"]+1}/{BUDGET} | {time.perf_counter()-t0:.1f}s | tl={r["train_loss_mean"]:.4f}')
        counter['n'] += 1
        return r['train_loss_mean'] if np.isfinite(r['train_loss_mean']) else 1e6

    try:
        differential_evolution(
            objective, BOUNDS, popsize=14, mutation=(0.5, 1.0), recombination=0.7,
            seed=METHOD_SEEDS[mid], polish=False, tol=1e-6, maxiter=10000,
            init='sobol', updating='deferred', workers=1,
        )
    except _BudgetExhausted:
        print(f'[{mid}] budget exhausted at {counter["n"]} evals')
    return keeper


def save_trajectories(keepers):
    payload = {}
    for mid, keeper in keepers.items():
        for rank, (tl, idx, x, traj) in enumerate(keeper.items):
            payload[f'{mid}_top{rank+1}_params'] = x
            payload[f'{mid}_top{rank+1}_info'] = np.array([tl, idx], dtype=float)
            for si, tr in enumerate(traj):
                payload[f'{mid}_top{rank+1}_seed{si}_series'] = tr
    np.savez_compressed(TRAJ_NPZ, **payload)
    print(f'Saved {len(payload)} traj arrays to {TRAJ_NPZ}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--methods', type=str, default='M1_RS,M2_LHS,M3_Sobol,M4_CtF,M5_DE')
    ap.add_argument('--only', type=str, default=None, help='run only this method id')
    args = ap.parse_args()

    env = RealEnvironment(data_dir='Phase3_Data')
    runners = {'M1_RS': run_method_RS, 'M2_LHS': run_method_LHS, 'M3_Sobol': run_method_Sobol,
               'M4_CtF': run_method_CtF, 'M5_DE': run_method_DE}

    chosen = [args.only] if args.only else args.methods.split(',')
    keepers = {}
    t_all = time.perf_counter()
    for mid in chosen:
        n_done = _already_done(mid)
        print(f'\n=== {mid} (resume from {n_done}) ===')
        t0 = time.perf_counter()
        keepers[mid] = runners[mid](env, resume=n_done)
        print(f'{mid} finished in {(time.perf_counter()-t0)/60:.1f} min')
    save_trajectories(keepers)
    print(f'\nAll methods done in {(time.perf_counter()-t_all)/60:.1f} min')
