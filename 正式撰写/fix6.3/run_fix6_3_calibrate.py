"""
Section 6.3 fix — separately re-calibrate single-dimension-flattened ABM variants.

Variants (paper names):
  Full heterogeneous ABM        (V_Full)             reused from fix6.2
  No Search Friction ABM        (V_NoSearch)         flatten 'search'
  No Liquidity Fragility ABM    (V_NoLiquidity)      flatten 'liquidity'
  No Housing Mobility ABM       (V_NoHousing)        flatten 'housing'
  No Search-Liquidity-Housing   (V_NoSLH)            flatten 3 dims jointly
  No Consumption Rule ABM       (V_NoConsumption)    flatten 'consumption_rule'
  Search-only heterogeneity     (V_SearchOnly)       flatten liquidity + housing

All variants: 14 PARAM_SPACE params active, all 13 mechanisms ON.
Protocol:
  - LHS sampling, bounds from PARAM_SPACE
  - 100 draws per variant x 3 calibration seeds {42, 137, 2024}
  - Train loss = Phase 6 formula on 2004-01..2017-12 (indices 36..204)
  - Selection: top-5 by mean train loss across seeds
"""
import os, sys, json, time, csv
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config
from Phase3_Code.phase7_engine import PARAM_MAP, flatten_heterogeneity
from Phase3_Code.calibration_engine import (
    PARAM_SPACE, param_names, target_ur, target_lfpr, target_epop
)

OUT = Path('正式撰写/fix6.3')
CKPT = OUT / 'checkpoints'
CKPT.mkdir(parents=True, exist_ok=True)

TRAIN_S, TRAIN_E = 36, 204
SEEDS = [42, 137, 2024]
N_DRAWS = 100

LOWS = np.array([PARAM_SPACE[n][2] for n in param_names], dtype=float)
HIGHS = np.array([PARAM_SPACE[n][3] for n in param_names], dtype=float)
N_PARAMS = len(param_names)

# Which heterogeneity dimensions are flattened for each variant. Empty = none.
VARIANT_FLATTEN = {
    'V_NoSearch':       ['search'],
    'V_NoLiquidity':    ['liquidity'],
    'V_NoHousing':      ['housing'],
    'V_NoSLH':          ['search', 'liquidity', 'housing'],
    'V_NoConsumption':  ['consumption_rule'],
    'V_SearchOnly':     ['liquidity', 'housing'],
}

# All variants calibrate all 14 params (mechanisms are all ON).
VARIANT_SPEC = {v: dict(active=set(param_names), n_draws=N_DRAWS, flatten=dims)
                for v, dims in VARIANT_FLATTEN.items()}


def lhs_sample(n, dim, seed):
    rng = np.random.default_rng(seed)
    u = np.zeros((n, dim))
    for j in range(dim):
        perm = rng.permutation(n)
        for i in range(n):
            u[perm[i], j] = (i + rng.random()) / n
    return u


def make_param_vec(u_row):
    return LOWS + u_row * (HIGHS - LOWS)


def build_cfg(param_vec):
    cfg = default_config()
    for i, n in enumerate(param_names):
        mk, pk = PARAM_SPACE[n][0], PARAM_SPACE[n][1]
        cfg[mk][pk] = float(param_vec[i])
    return cfg


def run_one(param_vec, variant, seed, env):
    cfg = build_cfg(param_vec)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    for dim in VARIANT_SPEC[variant]['flatten']:
        flatten_heterogeneity(sim.cs, sim.ds, sim.bp, dim)
    return sim.run(verbose=False)


def compute_train_loss(history):
    h = history[TRAIN_S:TRAIN_E]
    m_ur = np.array([x['unemployment_rate'] for x in h])
    m_lf = np.array([x['lfpr'] for x in h])
    m_ep = np.array([x['epop'] for x in h])
    m_eu = np.array([x['eu_rate'] for x in h])
    m_ue = np.array([x['ue_rate'] for x in h])
    m_h2m = np.array([x['h2m_share'] for x in h])
    t_ur, t_lf, t_ep = target_ur[TRAIN_S:TRAIN_E], target_lfpr[TRAIN_S:TRAIN_E], target_epop[TRAIN_S:TRAIN_E]
    vu, vl, ve = ~np.isnan(t_ur), ~np.isnan(t_lf), ~np.isnan(t_ep)
    l_ur = float(np.sqrt(np.mean((m_ur[vu] - t_ur[vu])**2)))
    l_lf = float(np.sqrt(np.mean((m_lf[vl] - t_lf[vl])**2)))
    l_ep = float(np.sqrt(np.mean((m_ep[ve] - t_ep[ve])**2)))
    l_eu = float(abs(m_eu.mean() - 0.015) * 10)
    l_ue = float(abs(m_ue.mean() - 0.25) * 5)
    l_h2m = float(abs(m_h2m.mean() - 0.30) * 2)
    total = 5.0*l_ur + 2.0*l_lf + 2.0*l_ep + 1.0*l_eu + 1.0*l_ue + 0.5*l_h2m
    return float(total), dict(ur=l_ur, lfpr=l_lf, epop=l_ep, eu=l_eu, ue=l_ue, h2m=l_h2m, total=float(total))


def _load_existing_progress(progress_csv):
    done = {}
    if not progress_csv.exists():
        return done
    with open(progress_csv, encoding='utf-8') as f:
        reader = csv.reader(f); next(reader, None)
        for row in reader:
            if len(row) < 10:
                continue
            ci = int(row[0]); sd = int(row[1])
            total = float(row[2])
            comp = dict(ur=float(row[3]), lfpr=float(row[4]), epop=float(row[5]),
                        eu=float(row[6]), ue=float(row[7]), h2m=float(row[8]),
                        total=total)
            done.setdefault(ci, {})[sd] = (total, comp)
    return done


def main():
    env = RealEnvironment(data_dir='Phase3_Data')
    t_start = time.perf_counter()
    summary = {}
    for variant, spec in VARIANT_SPEC.items():
        active = sorted(spec['active'], key=lambda n: param_names.index(n))
        n = spec['n_draws']
        print(f"\n=== {variant}  flatten={spec['flatten']}  n_draws={n}  total_sims={n*len(SEEDS)} ===", flush=True)
        samples_file = CKPT / f'{variant}_samples.npy'
        if samples_file.exists():
            samples = np.load(samples_file)
            print(f"  [resume] reusing existing samples", flush=True)
        else:
            u = lhs_sample(n, N_PARAMS, seed=12345 + hash(variant) % 10000)
            samples = np.array([make_param_vec(u_row) for u_row in u])
            np.save(samples_file, samples)
        progress_csv = CKPT / f'{variant}_progress.csv'
        done = _load_existing_progress(progress_csv)
        if done:
            print(f"  [resume] {sum(len(v) for v in done.values())} seed-rows done", flush=True)
        else:
            with open(progress_csv, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(['cand_idx', 'seed', 'train_loss', 'ur', 'lfpr',
                                        'epop', 'eu', 'ue', 'h2m', 'runtime_s'])
        per_cand = []
        for i in range(n):
            seed_losses = []; seed_comps = []
            for s in SEEDS:
                if i in done and s in done[i]:
                    total, comp = done[i][s]
                else:
                    t0 = time.perf_counter()
                    hist = run_one(samples[i], variant, s, env)
                    total, comp = compute_train_loss(hist)
                    rt = time.perf_counter() - t0
                    with open(progress_csv, 'a', newline='', encoding='utf-8') as f:
                        csv.writer(f).writerow([i, s, total, comp['ur'], comp['lfpr'],
                                                comp['epop'], comp['eu'], comp['ue'],
                                                comp['h2m'], rt])
                        f.flush()
                seed_losses.append(total); seed_comps.append(comp)
            mean = float(np.mean(seed_losses))
            std = float(np.std(seed_losses, ddof=1)) if len(seed_losses) > 1 else 0.0
            per_cand.append(dict(idx=i, mean=mean, std=std, seed_losses=seed_losses))
            elapsed = time.perf_counter() - t_start
            print(f"  {variant} [{i+1:3d}/{n}] mean={mean:.4f} std={std:.4f}  elapsed={elapsed/60:.1f}min", flush=True)
        per_cand.sort(key=lambda d: d['mean'])
        top5 = per_cand[:5]
        summary[variant] = dict(
            n_draws=n, active_params=active, flatten=spec['flatten'],
            samples_file=str(CKPT / f'{variant}_samples.npy'),
            top5_idx=[int(d['idx']) for d in top5],
            top5_mean=[d['mean'] for d in top5],
            top5_std=[d['std'] for d in top5],
            best_param_vec=samples[top5[0]['idx']].tolist(),
            all_candidates=per_cand,
        )
        with open(OUT / 'calibration_results.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"  -> top1 mean train loss = {top5[0]['mean']:.4f}", flush=True)
    print(f"\nTotal elapsed: {(time.perf_counter() - t_start)/60:.1f} min")


if __name__ == '__main__':
    main()
