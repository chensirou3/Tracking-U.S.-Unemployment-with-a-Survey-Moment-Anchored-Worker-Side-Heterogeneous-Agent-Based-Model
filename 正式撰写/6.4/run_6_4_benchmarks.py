"""
Section 6.4 — External Benchmark Comparison rerun.

Reruns the four Phase 8 benchmarks (B1 AR, B2 VAR, B3 Beveridge, B4 DMP) on the
same fitting window (36:252) and OOS window (252:302) used by Section 6.1/6.2/6.3.

Differences from Phase3_Code/phase8_benchmarks.py:
- OOS evaluation uses NaN-masking (2025-10 UNRATE is missing in FRED snapshot),
  matching the Section 6.1/6.2/6.3 convention; benchmarks are still fit on the
  forward-filled history (otherwise OLS/AR/VAR cannot be estimated).
- Reports RMSE, MAE, correlation, bias, max-abs error, min/max predicted and
  observed UR, in both decimal and percentage-point formats.

Outputs to 正式撰写/6.4/:
  benchmark_metrics.json   — per-benchmark metrics
  benchmark_series.npz     — OOS forecast paths (UR/LFPR/EPOP where applicable)
  rerun_log.txt            — console log
"""
import os, sys, json, time
import numpy as np

# Make project importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

from Phase3_Code.phase7_engine import get_targets, WINDOWS
from Phase3_Code.environment_real import RealEnvironment

OUT_DIR = os.path.join(ROOT, '正式撰写', '6.4')
os.makedirs(OUT_DIR, exist_ok=True)


def ffill(x):
    y = x.copy()
    last = y[~np.isnan(y)][0] if np.any(~np.isnan(y)) else 0.0
    for i in range(len(y)):
        if np.isnan(y[i]):
            y[i] = last
        else:
            last = y[i]
    return y


def metrics_block(pred, obs):
    """Return masked-NaN RMSE/MAE/corr/bias/max-abs/min/max. Inputs in decimal."""
    v = ~(np.isnan(pred) | np.isnan(obs))
    if v.sum() < 2:
        return {k: float('nan') for k in
                ['n_valid', 'rmse', 'mae', 'corr', 'bias',
                 'max_abs_err', 'pred_mean', 'obs_mean',
                 'pred_min', 'pred_max', 'obs_min', 'obs_max']}
    pv, ov = pred[v], obs[v]
    err = pv - ov
    return {
        'n_valid': int(v.sum()),
        'rmse': float(np.sqrt(np.mean(err ** 2))),
        'mae': float(np.mean(np.abs(err))),
        'corr': float(np.corrcoef(pv, ov)[0, 1]),
        'bias': float(np.mean(err)),
        'max_abs_err': float(np.max(np.abs(err))),
        'pred_mean': float(np.mean(pv)),
        'obs_mean': float(np.mean(ov)),
        'pred_min': float(np.min(pv)),
        'pred_max': float(np.max(pv)),
        'obs_min': float(np.min(ov)),
        'obs_max': float(np.max(ov)),
    }


def benchmark_AR(y_fit, oos_len, p=None):
    from statsmodels.tsa.ar_model import AutoReg
    if p is None:
        best_bic, p = np.inf, 1
        for tp in [1, 2, 3, 6, 12]:
            try:
                mod = AutoReg(y_fit, lags=tp, old_names=False).fit()
                if mod.bic < best_bic:
                    best_bic, p = mod.bic, tp
            except Exception:
                pass
    mod = AutoReg(y_fit, lags=p, old_names=False).fit()
    fc = mod.predict(start=len(y_fit), end=len(y_fit) + oos_len - 1)
    return np.asarray(fc), int(p)


def benchmark_VAR(Y_fit, oos_len, maxlag=6):
    from statsmodels.tsa.api import VAR
    mod = VAR(Y_fit)
    try:
        p = int(mod.select_order(maxlags=maxlag).bic)
        if p < 1:
            p = 1
    except Exception:
        p = 2
    res = mod.fit(p)
    fc = res.forecast(Y_fit[-p:], steps=oos_len)
    return np.asarray(fc), int(p)


def benchmark_Beveridge(ur_fit, v_fit, s_fit, v_oos, s_oos):
    from statsmodels.api import OLS, add_constant
    X_fit = add_constant(np.column_stack([1.0 / np.maximum(v_fit, 0.01), s_fit]))
    mod = OLS(ur_fit, X_fit).fit()
    X_oos = add_constant(np.column_stack([1.0 / np.maximum(v_oos, 0.01), s_oos]))
    fc = mod.predict(X_oos)
    return np.asarray(fc), [float(c) for c in mod.params], {
        'r2_train': float(mod.rsquared),
        'r2_train_adj': float(mod.rsquared_adj),
    }


def benchmark_DMP(ur_full, v_full, s_full, train_end, oos_end):
    from scipy.optimize import minimize

    def simulate(A, alpha, u0):
        u = np.zeros(oos_end)
        u[0] = u0
        for t in range(1, oos_end):
            theta = max(v_full[t - 1], 0.001)
            f = min(A * theta ** (1 - alpha), 0.95)
            s = s_full[t - 1]
            u[t] = u[t - 1] + s * (1 - u[t - 1]) - f * u[t - 1]
            u[t] = float(np.clip(u[t], 0.01, 0.5))
        return u

    def obj(p):
        A, alpha = p
        if A <= 0 or not (0 < alpha < 1):
            return 1e6
        usim = simulate(A, alpha, ur_full[0])
        return float(np.sum((usim[1:train_end] - ur_full[1:train_end]) ** 2))

    res = minimize(obj, x0=[0.3, 0.5], method='Nelder-Mead',
                   options={'xatol': 1e-4, 'fatol': 1e-6, 'maxiter': 600})
    A, alpha = float(res.x[0]), float(res.x[1])
    u_path = simulate(A, alpha, ur_full[0])
    return np.asarray(u_path[train_end:oos_end]), {'A': A, 'alpha': alpha,
                                                    'obj_value': float(res.fun)}


def main():
    t0 = time.time()
    print("=" * 78)
    print("Section 6.4 \u2014 External Benchmark Comparison rerun")
    print("=" * 78)

    env, tgt_ur, tgt_lfpr, tgt_epop = get_targets()
    # Macro arrays used by Beveridge / DMP
    T = env.T
    v_full = env.market_tightness.copy()
    s_full = env.separation_rate.copy()

    INIT_END = WINDOWS['init'][1]   # 36
    TRAIN_END = WINDOWS['train'][1] # 204
    VAL_END = WINDOWS['val'][1]     # 252  (= OOS start)
    OOS_END = WINDOWS['oos'][1]     # 302
    oos_len = OOS_END - VAL_END

    print(f"T = {T} months; windows init=[0,{INIT_END}) train=[{INIT_END},{TRAIN_END}) "
          f"val=[{TRAIN_END},{VAL_END}) oos=[{VAL_END},{OOS_END})")
    print(f"Macro driver source: RealEnvironment(JTSJOR/JTSLDR/CES/FEDFUNDS)")
    print(f"  market_tightness range = [{v_full.min():.3f}, {v_full.max():.3f}]"
          f"  separation_rate range = [{s_full.min():.4f}, {s_full.max():.4f}]")

    # NaN count (UNRATE 2025-10 should be missing)
    nan_oos = int(np.isnan(tgt_ur[VAL_END:OOS_END]).sum())
    print(f"OOS UR NaN months = {nan_oos} / {oos_len}")

    # Fitting window: [0, VAL_END) = [0, 252) (= 2001-01..2022-01, 252 months).
    # This matches the original Phase 8 benchmark code (phase8_benchmarks.py)
    # so that new numbers can be cross-checked against the stored
    # comparison_results.csv with minimal methodological gap.
    # NaNs are ffilled because OLS/AR/VAR require complete history;
    # only UNRATE 2025-10 (OOS month) and CES earnings 2001-01..2007-02 contain NaNs.
    FIT_END = VAL_END
    ur_fit = ffill(tgt_ur[:FIT_END])
    lfpr_fit = ffill(tgt_lfpr[:FIT_END])
    epop_fit = ffill(tgt_epop[:FIT_END])

    # Also produce a full ffilled history for DMP simulation (it needs ur[0])
    ur_full_ff = ffill(tgt_ur)

    ur_obs_oos = tgt_ur[VAL_END:OOS_END]
    lfpr_obs_oos = tgt_lfpr[VAL_END:OOS_END]
    epop_obs_oos = tgt_epop[VAL_END:OOS_END]

    results = {
        'meta': {
            'n_oos_months': oos_len,
            'n_oos_valid_ur': int((~np.isnan(ur_obs_oos)).sum()),
            'n_oos_valid_lfpr': int((~np.isnan(lfpr_obs_oos)).sum()),
            'n_oos_valid_epop': int((~np.isnan(epop_obs_oos)).sum()),
            'fit_window_index': [0, VAL_END],
            'oos_window_index': [VAL_END, OOS_END],
            'fit_window_dates': [env.dates[0], env.dates[VAL_END - 1]],
            'oos_window_dates': [env.dates[VAL_END], env.dates[OOS_END - 1]],
        }
    }
    forecasts = {}

    # ---- B1 AR ----
    print("\n[B1] AR(p) on UR, BIC \u2208 {1,2,3,6,12}")
    fc, p_ar = benchmark_AR(ur_fit, oos_len, p=None)
    m = metrics_block(fc, ur_obs_oos)
    results['B1_AR'] = {'spec': {'lags_selected_BIC': p_ar,
                                  'fit_y_length': int(len(ur_fit))},
                        'ur': m}
    forecasts['B1_AR_ur'] = fc
    print(f"  BIC selected p={p_ar}  OOS UR RMSE = {m['rmse'] * 100:.4f} pp  "
          f"MAE={m['mae'] * 100:.4f}  Corr={m['corr']:.4f}  "
          f"bias={m['bias'] * 100:+.4f} pp  n_valid={m['n_valid']}")

    # ---- B2 VAR ----
    print("\n[B2] VAR(p) on (UR, LFPR, EPOP), BIC up to maxlag=6")
    Y_fit = np.column_stack([ur_fit, lfpr_fit, epop_fit])
    fc, p_var = benchmark_VAR(Y_fit, oos_len, maxlag=6)
    m_ur = metrics_block(fc[:, 0], ur_obs_oos)
    m_lf = metrics_block(fc[:, 1], lfpr_obs_oos)
    m_ep = metrics_block(fc[:, 2], epop_obs_oos)
    results['B2_VAR'] = {'spec': {'lags_selected_BIC': p_var,
                                   'variables': ['UR', 'LFPR', 'EPOP'],
                                   'fit_length': int(Y_fit.shape[0])},
                         'ur': m_ur, 'lfpr': m_lf, 'epop': m_ep}
    forecasts['B2_VAR_ur'] = fc[:, 0]
    forecasts['B2_VAR_lfpr'] = fc[:, 1]
    forecasts['B2_VAR_epop'] = fc[:, 2]
    print(f"  BIC selected p={p_var}  OOS UR RMSE = {m_ur['rmse'] * 100:.4f} pp  "
          f"Corr={m_ur['corr']:+.4f}  bias={m_ur['bias'] * 100:+.4f} pp")
    print(f"  LFPR RMSE = {m_lf['rmse'] * 100:.4f} pp   "
          f"EPOP RMSE = {m_ep['rmse'] * 100:.4f} pp")

    # ---- B3 Beveridge ----
    print("\n[B3] Beveridge OLS:  UR_t = a + b1*(1/v_t) + b2*sep_t")
    fc, bv_params, bv_diag = benchmark_Beveridge(
        ur_fit, v_full[:FIT_END], s_full[:FIT_END],
        v_full[VAL_END:OOS_END], s_full[VAL_END:OOS_END])
    m = metrics_block(fc, ur_obs_oos)
    results['B3_Beveridge'] = {
        'spec': {'params_a_b1_b2': bv_params, **bv_diag,
                 'uses_observed_OOS_exog': True,
                 'exog_vars': ['market_tightness (JTSJOR/3)', 'separation_rate (JTSLDR/100)']},
        'ur': m}
    forecasts['B3_Beveridge_ur'] = fc
    print(f"  params (intercept, b_invV, b_sep) = "
          f"({bv_params[0]:.5f}, {bv_params[1]:.5f}, {bv_params[2]:.5f})")
    print(f"  R^2(fit) = {bv_diag['r2_train']:.4f}    OOS UR RMSE = {m['rmse'] * 100:.4f} pp  "
          f"Corr={m['corr']:+.4f}  bias={m['bias'] * 100:+.4f} pp")

    # ---- B4 DMP ----
    print("\n[B4] Simplified DMP: u_{t+1} = u_t + s_t(1-u_t) - f_t u_t,  f = A theta^(1-alpha)")
    fc, dmp_params = benchmark_DMP(ur_full_ff, v_full, s_full, VAL_END, OOS_END)
    m = metrics_block(fc, ur_obs_oos)
    results['B4_DMP'] = {
        'spec': {'A': dmp_params['A'], 'alpha': dmp_params['alpha'],
                 'obj_value': dmp_params['obj_value'],
                 'uses_observed_OOS_exog': True,
                 'exog_vars': ['market_tightness (theta)', 'separation_rate (s)']},
        'ur': m}
    forecasts['B4_DMP_ur'] = fc
    print(f"  A={dmp_params['A']:.4f}   alpha={dmp_params['alpha']:.4f}")
    print(f"  OOS UR RMSE = {m['rmse'] * 100:.4f} pp  Corr={m['corr']:+.4f}  "
          f"bias={m['bias'] * 100:+.4f} pp")

    # Also store observed series for downstream artifact building
    forecasts['obs_ur'] = ur_obs_oos
    forecasts['obs_lfpr'] = lfpr_obs_oos
    forecasts['obs_epop'] = epop_obs_oos
    forecasts['dates_oos'] = np.array(env.dates[VAL_END:OOS_END])

    # ---- Save ----
    with open(os.path.join(OUT_DIR, 'benchmark_metrics.json'), 'w') as f:
        json.dump(results, f, indent=2)
    np.savez(os.path.join(OUT_DIR, 'benchmark_series.npz'), **forecasts)
    print(f"\nSaved benchmark_metrics.json and benchmark_series.npz")

    print("\n" + "=" * 78)
    print(f"Section 6.4 benchmark rerun done in {time.time() - t0:.1f} s")
    print("=" * 78)


if __name__ == '__main__':
    main()
