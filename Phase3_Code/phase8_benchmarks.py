"""
Phase 8 External Benchmarks:
- B1 AR(p) on UR alone
- B2 VAR(p) on UR + LFPR + EPOP (+ env vars)
- B3 Beveridge reduced-form: UR ~ 1/v_rate + sep_rate
- B4 Simplified DMP: canonical search-matching, u_{t+1} = u_t + s(1-u_t) - f*u_t

All benchmarks fit on Train+Val (36:252), predict OOS (252:302).
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.phase7_engine import get_targets, WINDOWS
from Phase3_Code.environment_real import RealEnvironment

os.makedirs('Phase3_Output/phase8', exist_ok=True)


def load_env_arrays():
    """Load environment paths (FRED series) as arrays aligned to model dates."""
    env = RealEnvironment(data_dir='Phase3_Data')
    T = env.T
    v_rate = np.zeros(T)
    sep_rate = np.zeros(T)
    for t in range(T):
        e = env.get(t)
        v_rate[t] = e['market_tightness']
        sep_rate[t] = e['separation_rate']
    return v_rate, sep_rate


def rmse(a, b):
    v = ~(np.isnan(a) | np.isnan(b))
    if v.sum() < 2: return np.nan
    return float(np.sqrt(np.mean((a[v] - b[v])**2)))


def corr(a, b):
    v = ~(np.isnan(a) | np.isnan(b))
    if v.sum() < 2: return np.nan
    return float(np.corrcoef(a[v], b[v])[0, 1])


def mae(a, b):
    v = ~(np.isnan(a) | np.isnan(b))
    if v.sum() < 2: return np.nan
    return float(np.mean(np.abs(a[v] - b[v])))


def benchmark_AR(y, train_end, oos_end, p=None):
    """Fit AR(p) on y[:train_end], forecast y[train_end:oos_end].
    Uses BIC to select lag if p=None."""
    from statsmodels.tsa.ar_model import AutoReg
    y_train = y[:train_end]

    # Select lag by BIC
    if p is None:
        best_bic = np.inf; p = 1
        for test_p in [1, 2, 3, 6, 12]:
            try:
                mod = AutoReg(y_train, lags=test_p, old_names=False).fit()
                if mod.bic < best_bic:
                    best_bic = mod.bic; p = test_p
            except:
                pass

    mod = AutoReg(y_train, lags=p, old_names=False).fit()
    fc = mod.predict(start=train_end, end=oos_end - 1)
    return fc, p


def benchmark_VAR(Y, train_end, oos_end, maxlag=6):
    """Multivariate VAR on Y (T x k)."""
    from statsmodels.tsa.api import VAR
    Y_train = Y[:train_end]
    mod = VAR(Y_train)
    # Select by BIC
    try:
        sel = mod.select_order(maxlags=maxlag)
        p = sel.bic
        if p < 1: p = 1
    except:
        p = 2
    res = mod.fit(p)

    # Recursive forecasting
    fc = res.forecast(Y_train[-p:], steps=oos_end - train_end)
    return fc, p


def benchmark_Beveridge(ur, v_rate, sep_rate, train_end, oos_end):
    """OLS: UR_t = a + b1*(1/v_rate_t) + b2*sep_rate_t."""
    from statsmodels.api import OLS, add_constant
    X_train = np.column_stack([1.0 / np.maximum(v_rate[:train_end], 0.01),
                                sep_rate[:train_end]])
    X_train = add_constant(X_train)
    y_train = ur[:train_end]

    mod = OLS(y_train, X_train).fit()

    X_oos = np.column_stack([1.0 / np.maximum(v_rate[train_end:oos_end], 0.01),
                              sep_rate[train_end:oos_end]])
    X_oos = add_constant(X_oos)
    fc = mod.predict(X_oos)
    return fc, mod.params


def benchmark_DMP(ur, v_rate, sep_rate, train_end, oos_end):
    """Discrete-time DMP: u_{t+1} = u_t + s_t*(1-u_t) - f_t*u_t
    Matching function: M = A * U^alpha * V^(1-alpha)
    Job finding rate: f = M/U = A * theta^(1-alpha), theta = v_rate
    Fit A, alpha on training data."""
    from scipy.optimize import minimize

    def simulate(A, alpha, u0):
        u = np.zeros(oos_end)
        u[0] = u0
        for t in range(1, oos_end):
            theta = max(v_rate[t-1], 0.001)
            f = A * theta ** (1 - alpha)
            f = min(f, 0.95)
            s = sep_rate[t-1]
            u[t] = u[t-1] + s * (1 - u[t-1]) - f * u[t-1]
            u[t] = np.clip(u[t], 0.01, 0.5)
        return u

    def obj(params):
        A, alpha = params
        if A <= 0 or alpha <= 0 or alpha >= 1: return 1e6
        u_sim = simulate(A, alpha, ur[0])
        return np.sum((u_sim[1:train_end] - ur[1:train_end])**2)

    res = minimize(obj, x0=[0.3, 0.5], method='Nelder-Mead',
                   options={'xatol': 1e-4, 'fatol': 1e-6})
    A, alpha = res.x
    u_full = simulate(A, alpha, ur[0])
    return u_full[train_end:oos_end], {'A': float(A), 'alpha': float(alpha)}


# ============================================================
# MAIN
# ============================================================
def main():
    env, tgt_ur, tgt_lfpr, tgt_epop = get_targets()
    v_rate, sep_rate = load_env_arrays()
    T = len(tgt_ur)

    # Fill NaNs in BLS data for training (forward fill)
    def ffill(x):
        y = x.copy()
        last = y[0]
        for i in range(len(y)):
            if np.isnan(y[i]): y[i] = last
            else: last = y[i]
        return y

    ur = ffill(tgt_ur)
    lfpr = ffill(tgt_lfpr)
    epop = ffill(tgt_epop)

    INIT_END = WINDOWS['init'][1]        # 36
    VAL_END = WINDOWS['val'][1]          # 252 (= OOS start)
    OOS_END = WINDOWS['oos'][1]          # 302

    # Fit on [INIT_END, VAL_END), predict OOS [VAL_END, OOS_END)
    print("=" * 70)
    print("PHASE 8: EXTERNAL BENCHMARKS")
    print("=" * 70)

    results = {}

    # ----- B1: AR -----
    print("\nB1 AR(p) on UR...")
    fc_ar, p_ar = benchmark_AR(ur, VAL_END, OOS_END, p=None)
    ur_oos = ur[VAL_END:OOS_END]
    results['B1_AR'] = {
        'lags': int(p_ar),
        'ur_rmse': rmse(fc_ar, ur_oos), 'ur_mae': mae(fc_ar, ur_oos),
        'ur_corr': corr(fc_ar, ur_oos),
        'forecast': fc_ar.tolist(),
    }
    print(f"  Lags={p_ar}, OOS UR RMSE={results['B1_AR']['ur_rmse']:.4f}, "
          f"Corr={results['B1_AR']['ur_corr']:.3f}")

    # ----- B2: VAR on UR/LFPR/EPOP -----
    print("\nB2 VAR(p) on UR + LFPR + EPOP...")
    Y = np.column_stack([ur, lfpr, epop])
    fc_var, p_var = benchmark_VAR(Y, VAL_END, OOS_END, maxlag=6)
    results['B2_VAR'] = {
        'lags': int(p_var),
        'ur_rmse': rmse(fc_var[:, 0], ur[VAL_END:OOS_END]),
        'ur_mae': mae(fc_var[:, 0], ur[VAL_END:OOS_END]),
        'ur_corr': corr(fc_var[:, 0], ur[VAL_END:OOS_END]),
        'lfpr_rmse': rmse(fc_var[:, 1], lfpr[VAL_END:OOS_END]),
        'epop_rmse': rmse(fc_var[:, 2], epop[VAL_END:OOS_END]),
        'forecast_ur': fc_var[:, 0].tolist(),
        'forecast_lfpr': fc_var[:, 1].tolist(),
        'forecast_epop': fc_var[:, 2].tolist(),
    }
    print(f"  Lags={p_var}, OOS UR RMSE={results['B2_VAR']['ur_rmse']:.4f}, "
          f"LFPR={results['B2_VAR']['lfpr_rmse']:.4f}, "
          f"EPOP={results['B2_VAR']['epop_rmse']:.4f}")

    # ----- B3: Beveridge -----
    print("\nB3 Beveridge reduced-form...")
    fc_bv, bv_params = benchmark_Beveridge(ur, v_rate, sep_rate, VAL_END, OOS_END)
    results['B3_Beveridge'] = {
        'params': bv_params.tolist() if hasattr(bv_params, 'tolist') else list(bv_params),
        'ur_rmse': rmse(fc_bv, ur[VAL_END:OOS_END]),
        'ur_mae': mae(fc_bv, ur[VAL_END:OOS_END]),
        'ur_corr': corr(fc_bv, ur[VAL_END:OOS_END]),
        'forecast': fc_bv.tolist(),
    }
    print(f"  OOS UR RMSE={results['B3_Beveridge']['ur_rmse']:.4f}, "
          f"Corr={results['B3_Beveridge']['ur_corr']:.3f}")

    # ----- B4: DMP -----
    print("\nB4 Simplified DMP...")
    fc_dmp, dmp_params = benchmark_DMP(ur, v_rate, sep_rate, VAL_END, OOS_END)
    results['B4_DMP'] = {
        'params': dmp_params,
        'ur_rmse': rmse(fc_dmp, ur[VAL_END:OOS_END]),
        'ur_mae': mae(fc_dmp, ur[VAL_END:OOS_END]),
        'ur_corr': corr(fc_dmp, ur[VAL_END:OOS_END]),
        'forecast': fc_dmp.tolist(),
    }
    print(f"  A={dmp_params['A']:.3f}, alpha={dmp_params['alpha']:.3f}, "
          f"OOS UR RMSE={results['B4_DMP']['ur_rmse']:.4f}, "
          f"Corr={results['B4_DMP']['ur_corr']:.3f}")

    # Save
    with open('Phase3_Output/phase8/benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to Phase3_Output/phase8/benchmark_results.json")

    # Print summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY (OOS 2022-2026)")
    print("=" * 70)
    print(f"{'Model':<18s} {'UR RMSE':>10s} {'UR MAE':>10s} {'UR Corr':>10s}")
    print("-" * 55)
    for bname, r in results.items():
        print(f"{bname:<18s} {r['ur_rmse']:>10.4f} {r['ur_mae']:>10.4f} "
              f"{r['ur_corr']:>10.3f}")


if __name__ == '__main__':
    main()
