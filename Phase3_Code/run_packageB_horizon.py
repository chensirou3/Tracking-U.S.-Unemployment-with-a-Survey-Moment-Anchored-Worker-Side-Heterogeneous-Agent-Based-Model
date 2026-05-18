"""
Package B Step 2: run rolling-origin benchmarks + aggregate horizon metrics
for all 8 models (4 ABM cached + 4 benchmarks refit per origin).

Output:
    horizon_results.csv       (one row per model x horizon; aggregated across origins & seeds)
    horizon_raw.npz           (raw (model, origin, h) -> forecast_ur for later inspection)
"""
import sys, os, csv, time, warnings
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')

from Phase3_Code.phase7_engine import get_targets
from Phase3_Code.phase8_benchmarks import (
    load_env_arrays, benchmark_AR, benchmark_VAR,
    benchmark_Beveridge, benchmark_DMP,
)

os.makedirs('Phase3_Output/packageB', exist_ok=True)

HORIZONS = [1, 3, 6, 12, 24, 36]
INIT_END = 36        # 2004-01
OOS_START = 252      # 2022-01
OOS_END = 302        # 2026-02
SEEDS = [42, 137, 2024]
ABM_MODELS = ['M0_Main', 'D1_Homogeneous', 'D2_Simplified', 'D3_LaborOnly']
BENCHMARKS = ['B1_AR', 'B2_VAR', 'B3_Beveridge', 'B4_DMP']


def ffill(x):
    y = x.copy(); last = y[0]
    for i in range(len(y)):
        if np.isnan(y[i]): y[i] = last
        else: last = y[i]
    return y


def main():
    t_start = time.time()
    traj = np.load('Phase3_Output/packageB/abm_trajectories.npz', allow_pickle=True)
    env, t_ur, t_lfpr, t_epop = get_targets()
    v_rate, sep_rate = load_env_arrays()
    ur_ff, lfpr_ff, epop_ff = ffill(t_ur), ffill(t_lfpr), ffill(t_epop)

    # --- raw forecast storage: dict[(model, h)] -> list of (origin, forecast, bls) ---
    raw = {}

    # --- 1. ABM horizon extraction (no origin-dependent fit; continuous trajectory) ---
    for m in ABM_MODELS:
        # seed-mean trajectory (per calendar time)
        ur_seeds = np.stack([traj[f'{m}_seed{s}_unemployment_rate'] for s in SEEDS])
        lfpr_seeds = np.stack([traj[f'{m}_seed{s}_lfpr'] for s in SEEDS])
        epop_seeds = np.stack([traj[f'{m}_seed{s}_epop'] for s in SEEDS])
        # For a given (t0, h), we use the ABM's value at t0+h.
        # Seed variance is kept so we can report std later.
        for h in HORIZONS:
            n_origins = OOS_END - h - OOS_START
            if n_origins < 1: continue
            origins = np.arange(OOS_START, OOS_START + n_origins)
            # shape (n_seeds, n_origins): sim_ur at t0+h
            sim_ur = ur_seeds[:, origins + h]
            sim_lfpr = lfpr_seeds[:, origins + h]
            sim_epop = epop_seeds[:, origins + h]
            # Origin-time ABM drift for anchored error: err(t0) = sim(t0) - bls(t0)
            err0_ur = ur_seeds[:, origins] - t_ur[origins][None, :]
            err_h_ur = sim_ur - t_ur[origins + h][None, :]
            raw[(m, h)] = {
                'origins': origins,
                'sim_ur_seeds': sim_ur, 'bls_ur': t_ur[origins + h],
                'sim_lfpr_seeds': sim_lfpr, 'bls_lfpr': t_lfpr[origins + h],
                'sim_epop_seeds': sim_epop, 'bls_epop': t_epop[origins + h],
                'err_h_ur_seeds': err_h_ur, 'err0_ur_seeds': err0_ur,
            }
        print(f"[ABM] {m} cached  h in {HORIZONS}")

    # --- 2. Benchmarks: rolling origin re-fit per t0; extract at each h ---
    n_origins_max = OOS_END - min(HORIZONS) - OOS_START
    Y_full = np.column_stack([ur_ff, lfpr_ff, epop_ff])
    for b in BENCHMARKS:
        for h in HORIZONS:
            n_origins = OOS_END - h - OOS_START
            if n_origins < 1: continue
            origins = np.arange(OOS_START, OOS_START + n_origins)
            fc_ur = np.zeros(n_origins)
            fc_lfpr = np.full(n_origins, np.nan)
            fc_epop = np.full(n_origins, np.nan)
            for i, t0 in enumerate(origins):
                try:
                    end_idx = t0 + h
                    if b == 'B1_AR':
                        fc, _ = benchmark_AR(ur_ff, t0, end_idx, p=None)
                        fc_ur[i] = fc[-1]
                    elif b == 'B2_VAR':
                        fc, _ = benchmark_VAR(Y_full, t0, end_idx, maxlag=6)
                        fc_ur[i] = fc[-1, 0]; fc_lfpr[i] = fc[-1, 1]; fc_epop[i] = fc[-1, 2]
                    elif b == 'B3_Beveridge':
                        fc, _ = benchmark_Beveridge(ur_ff, v_rate, sep_rate, t0, end_idx)
                        fc_ur[i] = fc[-1]
                    elif b == 'B4_DMP':
                        fc, _ = benchmark_DMP(ur_ff, v_rate, sep_rate, t0, end_idx)
                        fc_ur[i] = fc[-1]
                except Exception as e:
                    fc_ur[i] = np.nan
            err_h = fc_ur - t_ur[origins + h]
            err0 = fc_ur * 0  # benchmark refit => err(t0) ~ 0 by construction
            raw[(b, h)] = {
                'origins': origins,
                'sim_ur_seeds': fc_ur[None, :], 'bls_ur': t_ur[origins + h],
                'sim_lfpr_seeds': fc_lfpr[None, :], 'bls_lfpr': t_lfpr[origins + h],
                'sim_epop_seeds': fc_epop[None, :], 'bls_epop': t_epop[origins + h],
                'err_h_ur_seeds': err_h[None, :], 'err0_ur_seeds': err0[None, :],
            }
        print(f"[BEN] {b} done  (elapsed {time.time()-t_start:.0f}s)")

    # --- 3. Aggregate per (model, h) ---
    rows = []
    for model in ABM_MODELS + BENCHMARKS:
        for h in HORIZONS:
            if (model, h) not in raw: continue
            d = raw[(model, h)]
            sim = d['sim_ur_seeds']         # (nseed_or_1, n_origins)
            bls = d['bls_ur']               # (n_origins,)
            valid = ~np.isnan(bls) & ~np.isnan(sim).any(axis=0)
            if valid.sum() < 2: continue
            # RMSE: average across seeds first (ABM), then RMSE across origins
            sim_mean = np.nanmean(sim[:, valid], axis=0)
            err = sim_mean - bls[valid]
            ur_rmse = float(np.sqrt(np.mean(err**2)))
            ur_mae = float(np.mean(np.abs(err)))
            ur_corr = float(np.corrcoef(sim_mean, bls[valid])[0, 1]) if valid.sum() > 2 else np.nan
            # Anchored: err_h - err0 per seed, then RMSE
            err_h = d['err_h_ur_seeds'][:, valid]
            err0 = d['err0_ur_seeds'][:, valid]
            anchored = np.nanmean(err_h - err0, axis=0)
            anch_rmse = float(np.sqrt(np.mean(anchored**2)))
            # Seed std for ABM
            seed_std = float(np.std(sim[:, valid], axis=0).mean()) if sim.shape[0] > 1 else 0.0
            # LFPR / EPOP (when available)
            lfpr_sim = d['sim_lfpr_seeds']; epop_sim = d['sim_epop_seeds']
            lfpr_rmse = epop_rmse = np.nan
            if not np.isnan(lfpr_sim).all():
                l_mean = np.nanmean(lfpr_sim[:, valid], axis=0)
                vl = ~np.isnan(d['bls_lfpr'][valid])
                if vl.sum() > 1:
                    lfpr_rmse = float(np.sqrt(np.mean((l_mean[vl] - d['bls_lfpr'][valid][vl])**2)))
            if not np.isnan(epop_sim).all():
                e_mean = np.nanmean(epop_sim[:, valid], axis=0)
                ve = ~np.isnan(d['bls_epop'][valid])
                if ve.sum() > 1:
                    epop_rmse = float(np.sqrt(np.mean((e_mean[ve] - d['bls_epop'][valid][ve])**2)))
            rows.append({
                'model': model, 'horizon': h, 'n_origins': int(valid.sum()),
                'ur_rmse_pp': ur_rmse * 100, 'ur_mae_pp': ur_mae * 100, 'ur_corr': ur_corr,
                'ur_rmse_anchored_pp': anch_rmse * 100,
                'seed_std_pp': seed_std * 100,
                'lfpr_rmse_pp': lfpr_rmse * 100 if not np.isnan(lfpr_rmse) else np.nan,
                'epop_rmse_pp': epop_rmse * 100 if not np.isnan(epop_rmse) else np.nan,
            })

    with open('Phase3_Output/packageB/horizon_results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # Save raw
    save_dict = {}
    for (m, h), d in raw.items():
        save_dict[f'{m}_h{h}_sim_ur'] = d['sim_ur_seeds']
        save_dict[f'{m}_h{h}_bls_ur'] = d['bls_ur']
        save_dict[f'{m}_h{h}_origins'] = d['origins']
    np.savez_compressed('Phase3_Output/packageB/horizon_raw.npz', **save_dict)

    print(f"\nTotal time: {time.time()-t_start:.0f}s")
    print(f"Saved horizon_results.csv ({len(rows)} rows) + horizon_raw.npz")


if __name__ == '__main__':
    main()
