"""
Section 6.3 fix — re-evaluate top-5 calibrated candidates per ablation variant.

Outputs:
  正式撰写/fix6.3/reeval_trajectories.npz
  正式撰写/fix6.3/reeval_metrics.json
"""
import os, sys, json, time
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Phase3_Code.environment_real import RealEnvironment

sys.path.insert(0, str(Path('正式撰写/fix6.3').resolve()))
from run_fix6_3_calibrate import run_one, VARIANT_SPEC  # noqa: E402

OUT = Path('正式撰写/fix6.3')
SEEDS = [42, 137, 2024, 888, 1234]

WINDOWS = {
    'pre_covid_stable':   ('Pre-COVID stable',           '2018-01..2019-12', 204, 228),
    'covid_crisis_mar':   ('COVID crisis (Mar 2020 on)', '2020-03..2021-12', 230, 252),
    'covid_crisis_jan':   ('COVID crisis (Jan 2020 on)', '2020-01..2021-12', 228, 252),
    'post_covid_norm':    ('Post-COVID normalization',   '2022-01..2026-02', 252, 302),
    'full_post_2018':     ('Full post-2018',             '2018-01..2026-02', 204, 302),
    'train':              ('Train',                      '2004-01..2017-12',  36, 204),
    'validation':         ('Validation',                 '2018-01..2021-12', 204, 252),
    'original_oos':       ('Original OOS',               '2022-01..2026-02', 252, 302),
}


def _window_metrics(sim_arr, obs_arr, s, e):
    sim = sim_arr[s:e]; obs = obs_arr[s:e]
    valid = ~np.isnan(obs)
    n_valid = int(valid.sum())
    if n_valid < 2:
        return dict(rmse=float('nan'), mae=float('nan'), corr=float('nan'),
                    bias=float('nan'), max_abs_err=float('nan'),
                    sim_mean=float('nan'), obs_mean=float('nan'), n_valid=n_valid)
    d = sim[valid] - obs[valid]
    return dict(
        rmse=float(np.sqrt(np.mean(d**2))),
        mae=float(np.mean(np.abs(d))),
        corr=float(np.corrcoef(sim[valid], obs[valid])[0, 1]) if np.std(sim[valid]) > 0 else float('nan'),
        bias=float(np.mean(d)),
        max_abs_err=float(np.max(np.abs(d))),
        sim_mean=float(np.mean(sim[valid])),
        obs_mean=float(np.mean(obs[valid])),
        n_valid=n_valid,
    )


def main():
    t_start = time.perf_counter()
    with open(OUT / 'calibration_results.json', encoding='utf-8') as f:
        cal = json.load(f)

    env = RealEnvironment(data_dir='Phase3_Data')
    dates = list(env.dates)
    from Phase3_Code.calibration_engine import target_ur as t_ur, target_lfpr as t_lf, target_epop as t_ep

    traj = {}
    metrics = {}
    for variant in VARIANT_SPEC.keys():
        v_top5 = cal[variant]['top5_idx']
        v_samples = np.load(cal[variant]['samples_file'])
        n_cand = len(v_top5)
        ur_arr = np.full((n_cand, len(SEEDS), 302), np.nan)
        lf_arr = np.full((n_cand, len(SEEDS), 302), np.nan)
        ep_arr = np.full((n_cand, len(SEEDS), 302), np.nan)
        v_metrics = []
        for rank, ci in enumerate(v_top5):
            pv = v_samples[ci]
            for si, seed in enumerate(SEEDS):
                t0 = time.perf_counter()
                hist = run_one(pv, variant, seed, env)
                ur = np.array([x['unemployment_rate'] for x in hist])
                lfp = np.array([x['lfpr'] for x in hist])
                epp = np.array([x['epop'] for x in hist])
                ur_arr[rank, si] = ur; lf_arr[rank, si] = lfp; ep_arr[rank, si] = epp
                for wkey, (_, _, s, e) in WINDOWS.items():
                    v_metrics.append(dict(
                        variant=variant, rank=int(rank), cand_idx=int(ci), seed=int(seed),
                        window=wkey,
                        ur=_window_metrics(ur, t_ur, s, e),
                        lfpr=_window_metrics(lfp, t_lf, s, e),
                        epop=_window_metrics(epp, t_ep, s, e),
                    ))
                elapsed = time.perf_counter() - t_start
                print(f"  {variant} rank={rank} seed={seed} runtime={time.perf_counter()-t0:.1f}s  elapsed={elapsed/60:.1f}min", flush=True)
        traj[f'{variant}_ur'] = ur_arr
        traj[f'{variant}_lfpr'] = lf_arr
        traj[f'{variant}_epop'] = ep_arr
        metrics[variant] = dict(top5_cand_idx=v_top5, rows=v_metrics)

    np.savez_compressed(
        OUT / 'reeval_trajectories.npz',
        dates=np.array(dates),
        target_ur=t_ur, target_lfpr=t_lf, target_epop=t_ep,
        seeds=np.array(SEEDS),
        **traj,
    )
    with open(OUT / 'reeval_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(dict(
            seeds=SEEDS,
            windows={k: dict(label=v[0], period=v[1], start_idx=v[2], end_idx=v[3])
                     for k, v in WINDOWS.items()},
            variants=metrics,
            wall_time_min=(time.perf_counter() - t_start) / 60,
        ), f, indent=2)

    print(f"\nReeval done in {(time.perf_counter()-t_start)/60:.1f} min")


if __name__ == '__main__':
    main()
