"""
Package A Step 2: Evaluate all 8 models across 10 splits.

ABM models (M0, D1, D2, D3): use split-specific best params from split_best_params.json
                             run with 3 seeds each, report test-window metrics.
Benchmarks (B1, B2, B3, B4): fit on train+val of each split, forecast test.

Output: packageA_all_results.json
        packageA_test_series.npz (seed=42 only, for plotting)
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.packageA_engine import SPLITS, get_env_targets
from Phase3_Code.phase8_derived import run_homogeneous, run_simplified, run_labor_only
from Phase3_Code.phase7_engine import run_version
from Phase3_Code.phase8_benchmarks import (
    load_env_arrays, benchmark_AR, benchmark_VAR,
    benchmark_Beveridge, benchmark_DMP, rmse, corr, mae
)

os.makedirs('Phase3_Output/packageA', exist_ok=True)

SEEDS = [42, 137, 2024]


def ffill(x):
    y = x.copy(); last = y[0]
    for i in range(len(y)):
        if np.isnan(y[i]): y[i] = last
        else: last = y[i]
    return y


def metrics_on_window(ur_sim, ur_tgt, lfpr_sim, lfpr_tgt, epop_sim, epop_tgt):
    return {
        'ur_rmse': rmse(ur_sim, ur_tgt), 'ur_mae': mae(ur_sim, ur_tgt),
        'ur_corr': corr(ur_sim, ur_tgt),
        'lfpr_rmse': rmse(lfpr_sim, lfpr_tgt),
        'epop_rmse': rmse(epop_sim, epop_tgt),
        'ur_mean_sim': float(np.nanmean(ur_sim)),
        'ur_mean_tgt': float(np.nanmean(ur_tgt)),
    }


def main():
    t0 = time.time()
    with open('Phase3_Output/packageA/split_best_params.json') as f:
        cal = json.load(f)

    env, (t_ur, t_lfpr, t_epop) = get_env_targets()
    v_rate, sep_rate = load_env_arrays()
    ur_ff = ffill(t_ur); lfpr_ff = ffill(t_lfpr); epop_ff = ffill(t_epop)

    abm_runners = {
        'M0_Main': lambda p, s: run_version(p, seed=s, env=env),
        'D1_Homogeneous': lambda p, s: run_homogeneous(p, s, env),
        'D2_Simplified': lambda p, s: run_simplified(p, s, env),
        'D3_LaborOnly': lambda p, s: run_labor_only(p, s, env),
    }

    all_results = {}
    test_series = {}  # for plotting

    for sid, sdata in cal['splits'].items():
        t_s = time.time()
        print(f"\n=== Split {sid} ({sdata['type']}) ===")
        tr_s, tr_e = sdata['train']
        va_s, va_e = sdata['val']
        te_s, te_e = sdata['test']
        params = sdata['best_params']

        split_out = {'type': sdata['type'], 'train': [tr_s, tr_e],
                     'val': [va_s, va_e], 'test': [te_s, te_e],
                     'best_params': params, 'models': {}}
        split_series = {}

        # ---- ABM models (3 seeds) ----
        for mname, runner in abm_runners.items():
            seed_metrics = []
            s42_ur = None
            for seed in SEEDS:
                hist = runner(params, seed)
                ur_s = np.array([h['unemployment_rate'] for h in hist])
                lfpr_s = np.array([h['lfpr'] for h in hist])
                epop_s = np.array([h['epop'] for h in hist])
                m = metrics_on_window(ur_s[te_s:te_e], t_ur[te_s:te_e],
                                      lfpr_s[te_s:te_e], t_lfpr[te_s:te_e],
                                      epop_s[te_s:te_e], t_epop[te_s:te_e])
                seed_metrics.append(m)
                if seed == 42:
                    s42_ur = ur_s[te_s:te_e].copy()
            agg = {}
            for k in seed_metrics[0].keys():
                vals = [x[k] for x in seed_metrics if not np.isnan(x[k])]
                agg[k + '_mean'] = float(np.mean(vals)) if vals else np.nan
                agg[k + '_std'] = float(np.std(vals)) if vals else np.nan
            split_out['models'][mname] = agg
            split_series[mname] = s42_ur
            print(f"  {mname}: test_UR_RMSE={agg['ur_rmse_mean']:.4f} "
                  f"(+/- {agg['ur_rmse_std']:.4f}) corr={agg['ur_corr_mean']:.3f}")

        # ---- Benchmarks (fit on train+val, forecast test) ----
        fit_end = va_e if va_e > va_s else tr_e
        try:
            fc_ar, p_ar = benchmark_AR(ur_ff, fit_end, te_e, p=None)
        except Exception as e:
            fc_ar = np.full(te_e - fit_end, np.nan); p_ar = 0
        try:
            Y = np.column_stack([ur_ff, lfpr_ff, epop_ff])
            fc_var, p_var = benchmark_VAR(Y, fit_end, te_e, maxlag=6)
            fc_var_ur = fc_var[:, 0]
        except Exception as e:
            fc_var_ur = np.full(te_e - fit_end, np.nan); p_var = 0
        fc_bev, _ = benchmark_Beveridge(ur_ff, v_rate, sep_rate, fit_end, te_e)
        fc_dmp, _ = benchmark_DMP(ur_ff, v_rate, sep_rate, fit_end, te_e)

        # Align forecasts to test window [te_s:te_e]. fit_end may be less than te_s.
        # Take the tail of the forecast that matches test indices.
        offset = te_s - fit_end
        n_test = te_e - te_s
        def slice_fc(fc): return fc[offset:offset + n_test]
        for bname, fc, extra in [
            ('B1_AR', slice_fc(fc_ar), {'lags': int(p_ar)}),
            ('B2_VAR', slice_fc(fc_var_ur), {'lags': int(p_var)}),
            ('B3_Beveridge', slice_fc(fc_bev), {}),
            ('B4_DMP', slice_fc(fc_dmp), {}),
        ]:
            m = metrics_on_window(fc, t_ur[te_s:te_e], fc, t_lfpr[te_s:te_e],
                                  fc, t_epop[te_s:te_e])
            # benchmarks only produce UR; blank out LFPR/EPOP
            m['lfpr_rmse'] = np.nan; m['epop_rmse'] = np.nan
            m.update(extra)
            split_out['models'][bname] = {k + '_mean': v if not isinstance(v, str) else v
                                          for k, v in m.items()}
            split_series[bname] = fc
            print(f"  {bname}: test_UR_RMSE={m['ur_rmse']:.4f}  corr={m['ur_corr']:.3f}")

        all_results[sid] = split_out
        test_series[sid] = {'ur_target': t_ur[te_s:te_e], **split_series}
        print(f"  [split {sid} time: {time.time()-t_s:.0f}s]")

    with open('Phase3_Output/packageA/packageA_all_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    save_dict = {}
    for sid, series_dict in test_series.items():
        for mname, arr in series_dict.items():
            save_dict[f'{sid}_{mname}'] = np.array(arr) if arr is not None else np.array([])
    np.savez_compressed('Phase3_Output/packageA/packageA_test_series.npz', **save_dict)

    print(f"\nTotal time: {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
