"""
Section 6.2 fix — separately re-calibrate four ABM variants.

Variants (paper names):
  Full heterogeneous ABM   (V_Full)         14 params, no flatten
  Homogeneous ABM          (V_Homogeneous)  14 params, all 6 dims flattened
  Labor-only ABM           (V_LaborOnly)    11 params, 4 household mechs OFF
  Simplified ABM           (V_Simplified)   1 param (vacancy_rate), all-off + matching_competition

Protocol:
  - LHS sampling, bounds from PARAM_SPACE
  - Per-variant LHS budget: 100 / 100 / 100 / 30
  - 3 calibration seeds {42, 137, 2024}
  - Train loss = compute_loss on window [36, 204) = 2004-01..2017-12
  - Selection: top-5 by mean train loss across seeds
  - Inactive params held at default_config() baseline
"""
import os, sys, json, time, csv
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config, all_off_config
from Phase3_Code.phase7_engine import PARAM_MAP, flatten_heterogeneity
from Phase3_Code.phase8_derived import flatten_all_heterogeneity
from Phase3_Code.calibration_engine import (
    PARAM_SPACE, param_names, target_ur, target_lfpr, target_epop
)

OUT = Path('正式撰写/fix6.2')
CKPT = OUT / 'checkpoints'
CKPT.mkdir(parents=True, exist_ok=True)

# Training window: 2004-01..2017-12  (indices 36..204 exclusive)
TRAIN_S, TRAIN_E = 36, 204
SEEDS = [42, 137, 2024]

LOWS = np.array([PARAM_SPACE[n][2] for n in param_names], dtype=float)
HIGHS = np.array([PARAM_SPACE[n][3] for n in param_names], dtype=float)
N_PARAMS = len(param_names)

# Inactive params per variant — held at default_config() baseline
DEFAULT_CFG = default_config()
BASELINE = np.array([DEFAULT_CFG[PARAM_SPACE[n][0]][PARAM_SPACE[n][1]] for n in param_names], dtype=float)

LABORONLY_DISABLED_PARAMS = {'h2m_resv_discount', 'h2m_mpc_floor', 'wealthy_discount'}
LABORONLY_DISABLED_MECHS = ['effective_mpc_adjustment', 'consumption_sequencing',
                             'buffer_consumption_ordering', 'liquidity_constraint_modifier']

VARIANT_SPEC = {
    'V_Full':         dict(active=set(param_names),                                 n_draws=100),
    'V_Homogeneous':  dict(active=set(param_names),                                 n_draws=100),
    'V_LaborOnly':    dict(active=set(param_names) - LABORONLY_DISABLED_PARAMS,     n_draws=100),
    'V_Simplified':   dict(active={'vacancy_rate'},                                 n_draws=30),
}


def lhs_sample(n, dim, seed):
    rng = np.random.default_rng(seed)
    u = np.zeros((n, dim))
    for j in range(dim):
        perm = rng.permutation(n)
        for i in range(n):
            u[perm[i], j] = (i + rng.random()) / n
    return u


def make_param_vec(u_row, variant):
    """Map LHS row (in active dims) to full 14-vector with baselines on inactive dims."""
    active = VARIANT_SPEC[variant]['active']
    active_idx = [i for i, n in enumerate(param_names) if n in active]
    vec = BASELINE.copy()
    for k, i in enumerate(active_idx):
        vec[i] = LOWS[i] + u_row[k] * (HIGHS[i] - LOWS[i])
    return vec, active_idx


def build_cfg(param_vec, variant):
    if variant == 'V_Simplified':
        cfg = all_off_config()
        cfg['matching_competition']['enabled'] = True
        vr_idx = param_names.index('vacancy_rate')
        cfg['matching_competition']['vacancy_rate'] = float(param_vec[vr_idx])
        return cfg
    cfg = default_config()
    for i, n in enumerate(param_names):
        mk, pk = PARAM_SPACE[n][0], PARAM_SPACE[n][1]
        cfg[mk][pk] = float(param_vec[i])
    if variant == 'V_LaborOnly':
        for m in LABORONLY_DISABLED_MECHS:
            cfg[m]['enabled'] = False
    return cfg


def run_one(param_vec, variant, seed, env):
    cfg = build_cfg(param_vec, variant)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    if variant in ('V_Homogeneous', 'V_Simplified'):
        flatten_all_heterogeneity(sim.cs, sim.ds, sim.bp)
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
    """Return dict[cand_idx] -> dict[seed] -> (total, comp)."""
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
        dim = len(active)
        n = spec['n_draws']
        print(f"\n=== {variant}  active_dim={dim}  n_draws={n}  total_sims={n*len(SEEDS)} ===", flush=True)

        samples_file = CKPT / f'{variant}_samples.npy'
        if samples_file.exists():
            samples = np.load(samples_file)
            assert samples.shape == (n, N_PARAMS), (samples.shape, n, N_PARAMS)
            print(f"  [resume] reusing existing samples file", flush=True)
        else:
            u = lhs_sample(n, dim, seed=12345 + hash(variant) % 10000)
            samples = np.array([make_param_vec(u_row, variant)[0] for u_row in u])
            np.save(samples_file, samples)

        progress_csv = CKPT / f'{variant}_progress.csv'
        done = _load_existing_progress(progress_csv)
        if done:
            print(f"  [resume] {sum(len(v) for v in done.values())} seed-rows already computed", flush=True)
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
            per_cand.append(dict(idx=i, mean=mean, std=std, seed_losses=seed_losses,
                                 comp_mean={k: float(np.mean([c[k] for c in seed_comps])) for k in seed_comps[0]}))
            elapsed = time.perf_counter() - t_start
            print(f"  {variant} [{i+1:3d}/{n}] mean={mean:.4f} std={std:.4f}  elapsed={elapsed/60:.1f}min", flush=True)

        per_cand.sort(key=lambda d: d['mean'])
        top5 = per_cand[:5]
        summary[variant] = dict(
            n_draws=n, active_params=active,
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
