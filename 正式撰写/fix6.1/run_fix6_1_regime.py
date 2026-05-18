"""
Section 6.1 (revised) — Regime-specific OOS evaluation.

No resimulation. Uses the 5-seed M0_Full baseline trajectories that
正式撰写/6.2/run_6_2_derived.py already produced and re-checks them against
the BLS targets across eight named windows. All metrics output in BOTH
decimal and percentage-point units.

Output: 正式撰写/fix6.1/regime_metrics.json + regime_series.npz
"""
import os, sys, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

SEEDS = [42, 137, 2024, 888, 1234]
SERIES_SRC = '正式撰写/6.2/derived_series.npz'
OUT_DIR = '正式撰写/fix6.1'
os.makedirs(OUT_DIR, exist_ok=True)

# Each window: human-readable label, calendar period, half-open index range [s, e)
WINDOWS = {
    'pre_covid_stable':    ('Pre-COVID stable',           '2018-01..2019-12', 204, 228),
    'covid_crisis_mar':    ('COVID crisis (Mar 2020 on)', '2020-03..2021-12', 230, 252),
    'covid_crisis_jan':    ('COVID crisis (Jan 2020 on)', '2020-01..2021-12', 228, 252),
    'post_covid_norm':     ('Post-COVID normalization',   '2022-01..2026-02', 252, 302),
    'full_post_2018':      ('Full post-2018',             '2018-01..2026-02', 204, 302),
    'train':               ('Train',                      '2004-01..2017-12',  36, 204),
    'validation':          ('Validation',                 '2018-01..2021-12', 204, 252),
    'original_oos':        ('Original OOS',               '2022-01..2026-02', 252, 302),
}


def _metric_block(sim, obs):
    """All UR-style metrics. NaN-masked. Returns decimal units; pp conversion done downstream."""
    v = ~np.isnan(obs)
    n_valid = int(v.sum())
    if n_valid < 2:
        return {k: float('nan') for k in
                ['rmse', 'mae', 'corr', 'bias', 'max_abs_err', 'sim_mean', 'obs_mean', 'n_valid']} | {'n_valid': n_valid}
    diff = sim[v] - obs[v]
    return {
        'rmse':        float(np.sqrt(np.mean(diff ** 2))),
        'mae':         float(np.mean(np.abs(diff))),
        'corr':        float(np.corrcoef(sim[v], obs[v])[0, 1]),
        'bias':        float(diff.mean()),
        'max_abs_err': float(np.max(np.abs(diff))),
        'sim_mean':    float(sim[v].mean()),
        'obs_mean':    float(obs[v].mean()),
        'n_valid':     n_valid,
    }


def _aggregate(seed_dicts, key):
    vals = [d[key] for d in seed_dicts if not np.isnan(d[key])]
    if not vals:
        return float('nan'), float('nan'), float('nan')
    m = float(np.mean(vals)); s = float(np.std(vals))
    cv = float(s / m * 100) if m != 0 else float('nan')
    return m, s, cv


def main():
    t0 = time.time()
    data = np.load(SERIES_SRC)
    dates = list(data['dates'])
    target_ur = data['target_ur']      # decimal
    target_lfpr = data['target_lfpr']
    target_epop = data['target_epop']
    ur = data['M0_Full_ur']            # (5 seeds, 302)
    lfpr = data['M0_Full_lfpr']
    epop = data['M0_Full_epop']
    assert ur.shape == (len(SEEDS), len(dates)), (ur.shape, len(SEEDS), len(dates))

    # Per-window, per-seed, per-series metrics
    by_window = {}
    for win, (label, period, s, e) in WINDOWS.items():
        by_window[win] = {'label': label, 'period': period, 'idx_start': s, 'idx_end': e,
                          'n_months_total': e - s, 'seeds': {}}
        # Seed level
        per_seed_ur, per_seed_lfpr, per_seed_epop = [], [], []
        for i, seed in enumerate(SEEDS):
            m_ur   = _metric_block(ur[i][s:e],   target_ur[s:e])
            m_lfpr = _metric_block(lfpr[i][s:e], target_lfpr[s:e])
            m_epop = _metric_block(epop[i][s:e], target_epop[s:e])
            by_window[win]['seeds'][seed] = {'ur': m_ur, 'lfpr': m_lfpr, 'epop': m_epop}
            per_seed_ur.append(m_ur); per_seed_lfpr.append(m_lfpr); per_seed_epop.append(m_epop)
        # Across-seed aggregates (decimal units; pp = decimal*100)
        agg = {}
        for sname, lst in [('ur', per_seed_ur), ('lfpr', per_seed_lfpr), ('epop', per_seed_epop)]:
            agg[sname] = {}
            for key in ['rmse', 'mae', 'corr', 'bias', 'max_abs_err', 'sim_mean', 'obs_mean']:
                mean, sd, cv = _aggregate(lst, key)
                agg[sname][key + '_mean'] = mean
                agg[sname][key + '_sd']   = sd
                agg[sname][key + '_cv']   = cv
            agg[sname]['n_valid'] = int(lst[0]['n_valid'])  # same for every seed
        by_window[win]['aggregate'] = agg

    summary = {
        'seeds': SEEDS,
        'series_source': SERIES_SRC,
        'units': 'all error metrics in DECIMAL; multiply by 100 to obtain percentage points',
        'windows': by_window,
        'wall_time_s': time.time() - t0,
    }

    out_json = os.path.join(OUT_DIR, 'regime_metrics.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)

    np.savez_compressed(os.path.join(OUT_DIR, 'regime_series.npz'),
                        dates=np.array(dates),
                        target_ur=target_ur, target_lfpr=target_lfpr, target_epop=target_epop,
                        ur=ur, lfpr=lfpr, epop=epop, seeds=np.array(SEEDS))

    # Console summary
    print('=' * 78)
    print('Section 6.1 (revised) — Regime-specific OOS')
    print(f"Source: {SERIES_SRC}  ({len(SEEDS)} seeds x {len(dates)} months)")
    print('=' * 78)
    fmt = '{:<24s} {:>16s} {:>8s} {:>10s} {:>10s} {:>9s} {:>10s} {:>11s}'
    print(fmt.format('window', 'period', 'n_obs', 'UR RMSE pp', 'UR MAE pp', 'UR corr',
                     'LFPR RMSEpp', 'EPOP RMSEpp'))
    print('-' * 110)
    for win, (label, period, s, e) in WINDOWS.items():
        a = by_window[win]['aggregate']
        n = a['ur']['n_valid']
        print(fmt.format(label, period, str(n),
                         f"{a['ur']['rmse_mean']*100:.4f}",
                         f"{a['ur']['mae_mean']*100:.4f}",
                         f"{a['ur']['corr_mean']:.3f}",
                         f"{a['lfpr']['rmse_mean']*100:.4f}",
                         f"{a['epop']['rmse_mean']*100:.4f}"))
    print('-' * 110)
    print(f"Wrote: {out_json}")
    print(f"Total wall time: {summary['wall_time_s']:.2f} s")


if __name__ == '__main__':
    main()
