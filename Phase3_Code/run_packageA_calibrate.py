"""
Package A Step 1: Shared-Pool Mini-Calibration across 10 splits.

Strategy: generate 60 LHS parameter sets (+ 1 center = 61 total) once.
Each parameter vector produces a fixed 302-month history.
For each split, pick the parameter vector that minimizes train-window loss.

Output: split_best_params.json  (per-split best params + train/val/test losses)
        lhs_pool.npz            (all 61 series arrays for later reuse)
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.packageA_engine import (
    SPLITS, lhs_samples, compute_loss_on_window, get_env_targets
)
from Phase3_Code.calibration_engine import param_names, make_config
from Phase3_Code.scheduler import Simulation

os.makedirs('Phase3_Output/packageA', exist_ok=True)

N_LHS = 60
SEED = 42

# Series we cache per sim so evaluate_loss can re-use them across splits.
SERIES_KEYS = ['unemployment_rate', 'lfpr', 'epop',
               'eu_rate', 'ue_rate', 'h2m_share',
               'avg_cash_buffer', 'avg_unemp_dur']


def history_to_array(history):
    return {k: np.array([h[k] for h in history]) for k in SERIES_KEYS}


def loss_from_arrays(arr, s, e, target_ur, target_lfpr, target_epop, w_ur=5.0):
    """Same formula as compute_loss_on_window but operating on cached arrays."""
    m_ur = arr['unemployment_rate'][s:e]
    m_lfpr = arr['lfpr'][s:e]
    m_epop = arr['epop'][s:e]
    m_eu = arr['eu_rate'][s:e]
    m_ue = arr['ue_rate'][s:e]
    m_h2m = arr['h2m_share'][s:e]
    tu, tl, te = target_ur[s:e], target_lfpr[s:e], target_epop[s:e]
    vu, vl, ve = ~np.isnan(tu), ~np.isnan(tl), ~np.isnan(te)

    def r(a, b, v):
        return float(np.sqrt(np.mean((a[v] - b[v])**2))) if v.sum() > 0 else 0.5
    lu = r(m_ur, tu, vu); ll = r(m_lfpr, tl, vl); le = r(m_epop, te, ve)
    leu = abs(m_eu.mean() - 0.015) * 10
    lue = abs(m_ue.mean() - 0.25) * 5
    lh = abs(m_h2m.mean() - 0.30) * 2
    total = w_ur * lu + 2 * ll + 2 * le + 1 * leu + 1 * lue + 0.5 * lh
    return float(total), {'ur': float(lu), 'lfpr': float(ll), 'epop': float(le),
                          'eu': float(leu), 'ue': float(lue), 'h2m': float(lh)}


def main():
    t0 = time.time()
    print("=" * 72)
    print(f"PACKAGE A - Calibration: {N_LHS} LHS samples x {len(SPLITS)} splits")
    print("=" * 72)

    # --- Sample LHS pool ---
    samples = lhs_samples(N_LHS, seed=SEED)  # shape (N_LHS+1, 14); row 0 is center
    N_TOTAL = samples.shape[0]
    print(f"Generated {N_TOTAL} parameter vectors")

    env, (t_ur, t_lfpr, t_epop) = get_env_targets()

    # --- Run every param vector once, cache series ---
    all_series = []
    for i in range(N_TOTAL):
        t1 = time.time()
        cfg = make_config(samples[i])
        sim = Simulation(config=cfg, seed=SEED, env_override=env)
        hist = sim.run(verbose=False)
        arr = history_to_array(hist)
        all_series.append(arr)
        dt = time.time() - t1
        ur_full = arr['unemployment_rate']
        if i % 5 == 0 or i == N_TOTAL - 1:
            print(f"  [{i+1}/{N_TOTAL}] dt={dt:.1f}s  UR mean={ur_full.mean():.3f}  "
                  f"elapsed={time.time()-t0:.0f}s")

    # --- Compute losses per split ---
    split_results = {}
    for sid, spec in SPLITS.items():
        tr_s, tr_e = spec['train']
        va_s, va_e = spec['val']
        te_s, te_e = spec['test']
        losses = []
        for i, arr in enumerate(all_series):
            tr_loss, tr_comp = loss_from_arrays(arr, tr_s, tr_e, t_ur, t_lfpr, t_epop)
            va_loss, va_comp = (loss_from_arrays(arr, va_s, va_e, t_ur, t_lfpr, t_epop)
                                if va_e > va_s else (0.0, {}))
            te_loss, te_comp = loss_from_arrays(arr, te_s, te_e, t_ur, t_lfpr, t_epop)
            losses.append({
                'idx': i,
                'train_loss': tr_loss, 'val_loss': va_loss, 'test_loss': te_loss,
                'train_ur_rmse': tr_comp['ur'],
                'val_ur_rmse': va_comp.get('ur', np.nan) if va_comp else np.nan,
                'test_ur_rmse': te_comp['ur'],
            })
        best = min(losses, key=lambda x: x['train_loss'])
        best_params = {param_names[j]: float(samples[best['idx'], j])
                       for j in range(len(param_names))}
        split_results[sid] = {
            'type': spec['type'], 'train': spec['train'], 'val': spec['val'], 'test': spec['test'],
            'best_idx': best['idx'], 'best_params': best_params,
            'train_loss': best['train_loss'], 'val_loss': best['val_loss'],
            'test_loss': best['test_loss'],
            'train_ur_rmse': best['train_ur_rmse'], 'val_ur_rmse': best['val_ur_rmse'],
            'test_ur_rmse': best['test_ur_rmse'],
            'all_losses': losses,
        }
        print(f"  {sid}: best_idx={best['idx']}  train_L={best['train_loss']:.3f}  "
              f"test_UR_RMSE={best['test_ur_rmse']:.4f}")

    # --- Save ---
    out_json = {'n_lhs': N_TOTAL, 'seed': SEED, 'param_names': param_names,
                'splits': split_results}
    with open('Phase3_Output/packageA/split_best_params.json', 'w') as f:
        json.dump(out_json, f, indent=2, default=float)

    save_dict = {'samples': samples}
    for i, arr in enumerate(all_series):
        for k in SERIES_KEYS:
            save_dict[f'sim{i}_{k}'] = arr[k]
    save_dict['target_ur'] = t_ur
    save_dict['target_lfpr'] = t_lfpr
    save_dict['target_epop'] = t_epop
    np.savez_compressed('Phase3_Output/packageA/lhs_pool.npz', **save_dict)

    print(f"\nTotal time: {time.time()-t0:.0f}s")
    print("Saved split_best_params.json + lhs_pool.npz")


if __name__ == '__main__':
    main()
