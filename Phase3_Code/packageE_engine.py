"""
Package E engine: calibration method sensitivity.

Shared eval_candidate() + 5 samplers.
All methods share the same PARAM_SPACE bounds, the same loss function,
the same 3-seed evaluation, the same 100k population.
"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config
from Phase3_Code.calibration_engine import (
    PARAM_SPACE, N_PARAMS, param_names, make_config, compute_loss, TRAIN_END, T
)

SEEDS = [42, 137, 2024]
SIM_SEEDS_COUNT = len(SEEDS)

LOWS = np.array([PARAM_SPACE[n][2] for n in param_names], dtype=float)
HIGHS = np.array([PARAM_SPACE[n][3] for n in param_names], dtype=float)
BOUNDS = list(zip(LOWS, HIGHS))


def _run_one_sim(param_vec, seed, env):
    cfg = make_config(param_vec)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    return sim.run(verbose=False)


def eval_candidate(param_vec, env=None, seeds=SEEDS):
    """Run 3-seed evaluation, return dict with aggregated losses and histories."""
    if env is None:
        env = RealEnvironment(data_dir='Phase3_Data')
    histories = []
    train_losses = []
    val_losses = []
    failed = 0
    t0 = time.perf_counter()
    for s in seeds:
        try:
            hist = _run_one_sim(param_vec, s, env)
            tl, _ = compute_loss(hist, 'train')
            vl, _ = compute_loss(hist, 'validation')
            histories.append(hist)
            train_losses.append(tl)
            val_losses.append(vl)
        except Exception as e:
            failed += 1
            train_losses.append(np.nan)
            val_losses.append(np.nan)
    runtime = time.perf_counter() - t0

    train_losses = np.array(train_losses)
    val_losses = np.array(val_losses)
    valid = np.isfinite(train_losses)
    result = {
        'train_loss_mean': float(np.nanmean(train_losses)) if valid.any() else np.nan,
        'train_loss_std': float(np.nanstd(train_losses, ddof=1)) if valid.sum() > 1 else 0.0,
        'val_loss_mean': float(np.nanmean(val_losses)) if valid.any() else np.nan,
        'val_loss_std': float(np.nanstd(val_losses, ddof=1)) if valid.sum() > 1 else 0.0,
        'failed_seeds': int(failed),
        'runtime_s': float(runtime),
        'histories': histories,
    }
    # Test window OOS metrics (from seed-paired histories)
    if histories:
        result.update(_test_window_from_histories(histories))
    return result


def _test_window_from_histories(histories, s=252, e=302):
    from Phase3_Code.packageA_engine import get_env_targets
    _, (t_ur, t_lfpr, t_epop) = get_env_targets()

    urs, lfs, eps = [], [], []
    h2ms, bufs, durs, eus, ues = [], [], [], [], []
    for hist in histories:
        arr_ur = np.array([x['unemployment_rate'] for x in hist])
        arr_lf = np.array([x['lfpr'] for x in hist])
        arr_ep = np.array([x['epop'] for x in hist])
        tu, tl, te = t_ur[s:e], t_lfpr[s:e], t_epop[s:e]
        vu, vl, ve = ~np.isnan(tu), ~np.isnan(tl), ~np.isnan(te)
        urs.append(np.sqrt(np.mean((arr_ur[s:e][vu] - tu[vu])**2)) * 100)
        lfs.append(np.sqrt(np.mean((arr_lf[s:e][vl] - tl[vl])**2)) * 100)
        eps.append(np.sqrt(np.mean((arr_ep[s:e][ve] - te[ve])**2)) * 100)
        h2ms.append(np.mean([x['h2m_share'] for x in hist]))
        bufs.append(np.mean([x['avg_cash_buffer'] for x in hist]))
        durs.append(np.mean([x['avg_unemp_dur'] for x in hist]))
        eus.append(np.mean([x['eu_rate'] for x in hist]))
        ues.append(np.mean([x['ue_rate'] for x in hist]))

    def mv(a): return float(np.mean(a)) if a else np.nan
    def sv(a): return float(np.std(a, ddof=1)) if len(a) > 1 else 0.0
    return {
        'test_ur_rmse_pp': mv(urs), 'test_ur_rmse_pp_std': sv(urs),
        'test_lfpr_rmse_pp': mv(lfs), 'test_epop_rmse_pp': mv(eps),
        'h2m_share_mean': mv(h2ms), 'avg_buffer_mean': mv(bufs),
        'avg_dur_mean': mv(durs), 'eu_mean': mv(eus), 'ue_mean': mv(ues),
    }


# ============================================================
# SAMPLERS
# ============================================================
def rs_sample(n, seed, lows=LOWS, highs=HIGHS):
    rng = np.random.default_rng(seed)
    return lows + rng.random((n, N_PARAMS)) * (highs - lows)


def lhs_sample(n, seed, lows=LOWS, highs=HIGHS):
    rng = np.random.default_rng(seed)
    u = np.zeros((n, N_PARAMS))
    for j in range(N_PARAMS):
        perm = rng.permutation(n)
        for i in range(n):
            u[perm[i], j] = (i + rng.random()) / n
    return lows + u * (highs - lows)


def sobol_sample(n, seed, lows=LOWS, highs=HIGHS):
    from scipy.stats import qmc
    sampler = qmc.Sobol(d=N_PARAMS, scramble=True, seed=seed)
    u = sampler.random(n=n)
    return lows + u * (highs - lows)


def ctf_stage1(n_coarse, seed):
    return lhs_sample(n_coarse, seed)


def ctf_stage2_bounds(top_params, padding_frac=0.10):
    """Build refined bounds from top-k params with padding, clipped to prior."""
    top = np.array(top_params)   # shape (k, N_PARAMS)
    mins = top.min(axis=0)
    maxs = top.max(axis=0)
    span = maxs - mins
    pad = span * padding_frac
    new_lows = np.maximum(mins - pad, LOWS)
    new_highs = np.minimum(maxs + pad, HIGHS)
    # Guard against zero-width
    zero = new_highs - new_lows < 1e-6
    if zero.any():
        new_lows[zero] = LOWS[zero]
        new_highs[zero] = HIGHS[zero]
    return new_lows, new_highs


def ctf_stage2_sample(n_fine, seed, lows_refined, highs_refined):
    return lhs_sample(n_fine, seed, lows_refined, highs_refined)
