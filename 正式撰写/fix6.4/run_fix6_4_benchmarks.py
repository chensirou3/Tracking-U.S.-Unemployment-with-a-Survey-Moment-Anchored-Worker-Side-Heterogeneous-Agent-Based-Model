"""
Section 6.4 (revised) — Stronger Forecast Benchmark Comparison.

Implements 11 statistical / econometric benchmarks under two protocols
(Dynamic multi-step, Rolling one-step-ahead) across four regime windows
(pre-COVID stable, COVID crisis (Mar 2020 on), post-COVID normalization,
full post-2018), and stores per-(model, regime, protocol) UR/LFPR/EPOP
metrics + per-month forecast paths.

ABM rows are pulled later (in build_fix6_4_artifacts.py) from
正式撰写/fix6.2/reeval_metrics.json (V_Full, rank=0 cand=32, 5 seeds).

Outputs to 正式撰写/fix6.4/:
  benchmark_metrics.json      (per (model, regime, protocol) metrics)
  benchmark_series.npz        (per (model, regime, protocol) forecast paths)
  rerun_log.txt               (console log)

Benchmarks:
  B0a  No-change / random walk            (UR only)
  B0b  Historical mean                    (UR only)
  B0c  Drift / local linear trend         (UR only, 12-month OLS slope)
  B1   AR(p), BIC select p in {1,2,3,6,12}
  B2   ARIMA(p,d,q), AIC grid p<=4,d<=2,q<=4
  B3   ETS — SES / Holt / Damped-Holt, AICc select
  B4   VAR(p) on (UR, LFPR, EPOP), BIC select
  B5   Ridge VAR(p=2) on (UR, LFPR, EPOP, vac_rate, sep_rate); 5 lambda CV
  B6   Beveridge OLS:  UR = a + b1*(1/v_t) + b2*sep_t
       (uses observed OOS vacancy & separation)
  B7   DMP-style flow:  u_{t+1} = u_t + s_t(1-u_t) - A theta^{1-alpha} u_t
       (uses observed OOS vacancy & separation)
  B8   Flow-based UR:  separation = JTSLDR; job-finding f_t from
       AR(1) on (1-u_{t+1})/(1-u_t)*... approximation; rolls u dynamically
       (uses observed OOS separation)

Protocols:
  Dynamic   — fit once on [0, REGIME_FIT_END), forecast whole regime window
  Rolling   — for each month t in regime, fit on [0, t), forecast t
              (ARIMA/ETS orders are selected ONCE on the first fit and held
              fixed for the rolling sweep, otherwise rolling × grid ~2h)
"""
import os, sys, json, time, warnings
import numpy as np

warnings.filterwarnings('ignore')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

from Phase3_Code.phase7_engine import get_targets, WINDOWS

OUT_DIR = os.path.join(ROOT, '正式撰写', 'fix6.4')
os.makedirs(OUT_DIR, exist_ok=True)


# ----------------------------------------------------------------------------
# Regime windows  (fit ends BEFORE the regime, matching ABM train/val cutoffs)
# ----------------------------------------------------------------------------
REGIMES = {
    'pre_covid_stable':   {'period': '2018-01..2019-12', 'oos': (204, 228), 'fit_end': 204},
    'covid_crisis_mar':   {'period': '2020-03..2021-12', 'oos': (230, 252), 'fit_end': 230},
    'post_covid_norm':    {'period': '2022-01..2026-02', 'oos': (252, 302), 'fit_end': 252},
    'full_post_2018':     {'period': '2018-01..2026-02', 'oos': (204, 302), 'fit_end': 204},
}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def ffill(x):
    y = x.copy()
    nz = np.where(~np.isnan(y))[0]
    if len(nz) == 0:
        return np.zeros_like(y)
    last = y[nz[0]]
    for i in range(len(y)):
        if np.isnan(y[i]):
            y[i] = last
        else:
            last = y[i]
    return y


def metrics_block(pred, obs):
    """RMSE/MAE/corr/bias/max-abs on NaN-masked overlap. Inputs decimal."""
    pred = np.asarray(pred, dtype=float)
    obs = np.asarray(obs, dtype=float)
    v = ~(np.isnan(pred) | np.isnan(obs))
    if v.sum() < 2:
        return {k: float('nan') for k in
                ['n_valid', 'rmse', 'mae', 'corr', 'bias',
                 'max_abs_err', 'pred_mean', 'obs_mean']}
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
    }


# ----------------------------------------------------------------------------
# B0: naive benchmarks
# ----------------------------------------------------------------------------
def fc_no_change(y_fit, horizon):
    last = float(y_fit[-1])
    return np.full(horizon, last), {'type': 'random_walk', 'last_value': last}


def fc_hist_mean(y_fit, horizon):
    m = float(np.nanmean(y_fit))
    return np.full(horizon, m), {'type': 'historical_mean', 'mean': m}


def fc_drift(y_fit, horizon, window=12):
    n = len(y_fit)
    w = min(window, n)
    x = np.arange(w, dtype=float)
    y = y_fit[-w:]
    slope, intercept = np.polyfit(x, y, 1)
    out = np.array([y[-1] + slope * (i + 1) for i in range(horizon)])
    return out, {'type': 'local_linear_trend', 'slope_per_month': float(slope),
                 'window_months': int(w)}


# ----------------------------------------------------------------------------
# B1: AR(p) — BIC over p in {1,2,3,6,12}
# ----------------------------------------------------------------------------
def fc_ar(y_fit, horizon, p_grid=(1, 2, 3, 6, 12)):
    from statsmodels.tsa.ar_model import AutoReg
    best_bic, best_p, best_mod = np.inf, p_grid[0], None
    for p in p_grid:
        try:
            m = AutoReg(y_fit, lags=p, old_names=False).fit()
            if m.bic < best_bic:
                best_bic, best_p, best_mod = float(m.bic), int(p), m
        except Exception:
            continue
    if best_mod is None:
        return fc_no_change(y_fit, horizon)
    fc = best_mod.predict(start=len(y_fit), end=len(y_fit) + horizon - 1)
    return np.asarray(fc), {'type': 'AR', 'p_selected_BIC': int(best_p),
                            'bic': float(best_bic)}


# ----------------------------------------------------------------------------
# B2: ARIMA(p,d,q) — AIC grid select
# ----------------------------------------------------------------------------
def fc_arima(y_fit, horizon, order=None, p_max=4, d_max=2, q_max=4):
    """If order is None, run AIC grid; otherwise refit fixed order."""
    from statsmodels.tsa.arima.model import ARIMA
    if order is None:
        best_aic, best_order, best_res = np.inf, (1, 1, 0), None
        for p in range(p_max + 1):
            for d in range(d_max + 1):
                for q in range(q_max + 1):
                    if p == 0 and q == 0:
                        continue
                    try:
                        res = ARIMA(y_fit, order=(p, d, q),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False).fit(method_kwargs={'warn_convergence': False})
                        if np.isfinite(res.aic) and res.aic < best_aic:
                            best_aic = float(res.aic); best_order = (p, d, q); best_res = res
                    except Exception:
                        continue
        if best_res is None:
            return fc_no_change(y_fit, horizon)[0], {'type': 'ARIMA',
                                                     'order_AIC': (0, 1, 0),
                                                     'aic': float('nan')}
        order = best_order; res = best_res
    else:
        try:
            res = ARIMA(y_fit, order=order,
                        enforce_stationarity=False,
                        enforce_invertibility=False).fit(method_kwargs={'warn_convergence': False})
        except Exception:
            return fc_no_change(y_fit, horizon)[0], {'type': 'ARIMA',
                                                     'order_AIC': order,
                                                     'aic': float('nan')}
    fc = res.forecast(steps=horizon)
    return np.asarray(fc), {'type': 'ARIMA', 'order_AIC': tuple(int(x) for x in order),
                            'aic': float(res.aic)}


# ----------------------------------------------------------------------------
# B3: ETS — SES / Holt / Damped-Holt, AICc select
# ----------------------------------------------------------------------------
def fc_ets(y_fit, horizon, kind=None):
    """If kind is None, fit all 3 variants and AICc-select; else refit fixed kind.
       Use sum-of-squared-residuals proxy for AIC when statsmodels does not return one."""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing as HW, SimpleExpSmoothing
    configs = {
        'SES':        dict(trend=None,        damped_trend=False),
        'Holt':       dict(trend='add',       damped_trend=False),
        'DampedHolt': dict(trend='add',       damped_trend=True),
    }
    keys = [kind] if kind is not None else list(configs.keys())
    best_aic, best_kind, best_res = np.inf, keys[0], None
    n = len(y_fit)
    for k in keys:
        try:
            if k == 'SES':
                res = SimpleExpSmoothing(y_fit, initialization_method='heuristic').fit(
                    optimized=True)
                npar = 2
            else:
                res = HW(y_fit, **configs[k],
                         initialization_method='heuristic').fit(optimized=True)
                npar = 3 if not configs[k]['damped_trend'] else 4
            # Proxy AICc from residuals if .aic is nan
            aic_attr = getattr(res, 'aic', None)
            if aic_attr is not None and np.isfinite(aic_attr):
                aic = float(aic_attr)
            else:
                resid = np.asarray(y_fit) - np.asarray(res.fittedvalues)
                sse = float(np.sum(resid ** 2))
                aic = n * np.log(sse / n + 1e-12) + 2 * npar  # proxy
            if np.isfinite(aic) and aic < best_aic:
                best_aic, best_kind, best_res = aic, k, res
        except Exception:
            continue
    if best_res is None:
        return fc_no_change(y_fit, horizon)[0], {'type': 'ETS', 'kind': 'fallback_no_change',
                                                 'aic': float('nan')}
    fc = best_res.forecast(steps=horizon)
    return np.asarray(fc), {'type': 'ETS', 'kind': best_kind, 'aic': float(best_aic)}


# ----------------------------------------------------------------------------
# B4: VAR(p) on (UR, LFPR, EPOP) — BIC select
# ----------------------------------------------------------------------------
def fc_var(Y_fit, horizon, p=None, maxlag=6):
    """If p is None, run BIC select; otherwise refit fixed p."""
    from statsmodels.tsa.api import VAR
    mod = VAR(Y_fit)
    if p is None:
        try:
            sel = mod.select_order(maxlags=maxlag)
            p = int(sel.bic)
            if p < 1:
                p = 1
        except Exception:
            p = 2
    try:
        res = mod.fit(p)
        fc = res.forecast(Y_fit[-p:], steps=horizon)
    except Exception:
        fc = np.tile(Y_fit[-1], (horizon, 1))
    return np.asarray(fc), {'type': 'VAR', 'p_selected_BIC': int(p),
                            'variables': ['UR', 'LFPR', 'EPOP']}


# ----------------------------------------------------------------------------
# B5: Ridge VAR(p=2) on (UR, LFPR, EPOP, vac, sep), 5 lambda CV
# ----------------------------------------------------------------------------
def fc_ridge_var(Y_fit, horizon, p=2, exog_oos=None, lam=None,
                 lambda_grid=(0.001, 0.01, 0.1, 1.0, 10.0)):
    """Ridge-regularized VAR as approximation to BVAR.
       Y_fit: (T, K), K cols = (UR, LFPR, EPOP, vac, sep)
       exog_oos: future macro inputs for vac/sep — if None, use last in-sample value.
       Returns forecast matrix (horizon, K)."""
    from sklearn.linear_model import Ridge
    T, K = Y_fit.shape
    # Build lag matrix
    X = np.column_stack([Y_fit[p - 1 - lag: T - 1 - lag] for lag in range(p)])
    Yt = Y_fit[p:]
    X = X[:Yt.shape[0]]
    if lam is None:
        # 5-fold CV on training residuals
        from sklearn.model_selection import KFold
        best_lam, best_score = lambda_grid[0], np.inf
        kf = KFold(n_splits=min(5, len(Yt) - 1), shuffle=False)
        for L in lambda_grid:
            scores = []
            for tr, te in kf.split(X):
                try:
                    rg = Ridge(alpha=L, fit_intercept=True).fit(X[tr], Yt[tr])
                    pred = rg.predict(X[te])
                    scores.append(float(np.mean((pred[:, 0] - Yt[te, 0]) ** 2)))
                except Exception:
                    scores.append(np.inf)
            avg = float(np.mean(scores)) if scores else np.inf
            if avg < best_score:
                best_score, best_lam = avg, L
        lam = best_lam
    rg = Ridge(alpha=lam, fit_intercept=True).fit(X, Yt)
    # Roll forecast
    out = np.zeros((horizon, K))
    state = Y_fit[-p:].copy()
    for h in range(horizon):
        feat = np.column_stack([state[p - 1 - lag][None, :] for lag in range(p)])
        pred = rg.predict(feat)[0]
        # If exog future inputs supplied, override the (vac, sep) cols
        if exog_oos is not None and h < exog_oos.shape[0]:
            pred[3:5] = exog_oos[h, :]
        out[h] = pred
        state = np.vstack([state[1:], pred[None, :]])
    return out, {'type': 'RidgeVAR', 'p': int(p), 'lambda': float(lam),
                 'variables': ['UR', 'LFPR', 'EPOP', 'vac', 'sep'],
                 'uses_observed_OOS_exog': exog_oos is not None}


# ----------------------------------------------------------------------------
# B6: Beveridge OLS:  UR_t = a + b1*(1/v_t) + b2*sep_t
# ----------------------------------------------------------------------------
def fc_beveridge(ur_fit, v_fit, s_fit, v_oos, s_oos):
    from statsmodels.api import OLS, add_constant
    X = add_constant(np.column_stack([1.0 / np.maximum(v_fit, 0.01), s_fit]),
                     has_constant='add')
    mod = OLS(ur_fit, X).fit()
    Xo = add_constant(np.column_stack([1.0 / np.maximum(v_oos, 0.01), s_oos]),
                      has_constant='add')
    fc = mod.predict(Xo)
    return np.asarray(fc), {'type': 'Beveridge',
                            'params_a_b1_b2': [float(c) for c in mod.params],
                            'r2_train': float(mod.rsquared),
                            'uses_observed_OOS_exog': True,
                            'exog_vars': ['market_tightness', 'separation_rate']}


# ----------------------------------------------------------------------------
# B7: DMP-style flow model:  u_{t+1} = u_t + s_t(1-u_t) - A theta^{1-alpha} u_t
# ----------------------------------------------------------------------------
def fc_dmp(ur_history, v_full, s_full, fit_end, oos_end):
    """Fit (A, alpha) by NM on history[0..fit_end), simulate fwd to oos_end."""
    from scipy.optimize import minimize

    def simulate(A, alpha, u0, end):
        u = np.zeros(end)
        u[0] = u0
        for t in range(1, end):
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
        usim = simulate(A, alpha, ur_history[0], fit_end)
        return float(np.sum((usim[1:fit_end] - ur_history[1:fit_end]) ** 2))

    res = minimize(obj, x0=[0.3, 0.5], method='Nelder-Mead',
                   options={'xatol': 1e-4, 'fatol': 1e-6, 'maxiter': 600})
    A, alpha = float(res.x[0]), float(res.x[1])
    u_path = simulate(A, alpha, ur_history[0], oos_end)
    return np.asarray(u_path[fit_end:oos_end]), {
        'type': 'DMP', 'A': A, 'alpha': alpha,
        'uses_observed_OOS_exog': True,
        'exog_vars': ['market_tightness', 'separation_rate']}


# ----------------------------------------------------------------------------
# B8: Flow-based UR — exploit JOLTS separations as inflow; AR(1) job-finding
# ----------------------------------------------------------------------------
def fc_flow(ur_history, s_full, fit_end, oos_end):
    """Recover implied job-finding rate f_t from UR identity, fit AR(1) on f,
       project f over OOS, roll u dynamic using observed s_t and projected f_t."""
    u_fit = ur_history[:fit_end]
    s_fit = s_full[:fit_end]
    # Implied f_t:  u_{t+1} = u_t + s_t(1-u_t) - f_t u_t  =>  f_t = (u_t + s_t(1-u_t) - u_{t+1}) / u_t
    f_imp = (u_fit[:-1] + s_fit[:-1] * (1 - u_fit[:-1]) - u_fit[1:]) / np.maximum(u_fit[:-1], 1e-4)
    f_imp = np.clip(f_imp, 0.01, 0.95)
    # AR(1) on f
    try:
        from statsmodels.tsa.ar_model import AutoReg
        ar = AutoReg(f_imp, lags=1, old_names=False).fit()
        rho = float(ar.params[1]); mu = float(ar.params[0])
        f_long = mu / (1 - rho) if abs(rho) < 0.999 else float(np.mean(f_imp))
    except Exception:
        rho = 0.5; mu = float(np.mean(f_imp)) * (1 - 0.5); f_long = float(np.mean(f_imp))
    # Simulate forward
    u = np.zeros(oos_end - fit_end)
    f_path = np.zeros_like(u)
    u_prev = float(u_fit[-1])
    f_prev = float(f_imp[-1])
    for h in range(oos_end - fit_end):
        f_t = mu + rho * f_prev
        f_t = float(np.clip(f_t, 0.01, 0.95))
        s_t = float(s_full[fit_end + h - 1]) if fit_end + h >= 1 else float(s_full[0])
        u_new = u_prev + s_t * (1 - u_prev) - f_t * u_prev
        u_new = float(np.clip(u_new, 0.01, 0.5))
        u[h] = u_new; f_path[h] = f_t
        u_prev, f_prev = u_new, f_t
    return u, {'type': 'Flow_based', 'f_AR1_rho': float(rho), 'f_AR1_const': float(mu),
               'f_longrun': float(f_long), 'f_imp_mean': float(np.mean(f_imp)),
               'uses_observed_OOS_exog': True, 'exog_vars': ['separation_rate']}



# ----------------------------------------------------------------------------
# Per-regime sweep: Dynamic + Rolling
# ----------------------------------------------------------------------------
def run_regime(regime_id, regime_cfg, tgt_ur, tgt_lfpr, tgt_epop,
               v_full, s_full, log):
    fit_end = int(regime_cfg['fit_end'])
    oos_s, oos_e = regime_cfg['oos']
    horizon = oos_e - oos_s

    ur_fit = ffill(tgt_ur[:fit_end])
    lfpr_fit = ffill(tgt_lfpr[:fit_end])
    epop_fit = ffill(tgt_epop[:fit_end])
    v_fit = v_full[:fit_end]; s_fit = s_full[:fit_end]
    ur_full_ff = ffill(tgt_ur)

    obs_ur = tgt_ur[oos_s:oos_e]
    obs_lfpr = tgt_lfpr[oos_s:oos_e]
    obs_epop = tgt_epop[oos_s:oos_e]

    Y_var = np.column_stack([ur_fit, lfpr_fit, epop_fit])
    Y_rv = np.column_stack([ur_fit, lfpr_fit, epop_fit, v_fit, s_fit])

    # If fit_end < oos_s, we still need a "gap" pad: for these regimes fit_end == oos_s.
    assert fit_end == oos_s or regime_id == 'covid_crisis_mar', \
        f"fit_end != oos_s for {regime_id}"

    out_regime = {'meta': {'period': regime_cfg['period'],
                           'oos_window_index': [int(oos_s), int(oos_e)],
                           'fit_end_index': int(fit_end),
                           'horizon': int(horizon),
                           'n_oos_valid_ur': int((~np.isnan(obs_ur)).sum())}}
    fc_store = {}

    log(f"\n=== regime: {regime_id}  ({regime_cfg['period']})  "
        f"fit=[0,{fit_end})  oos=[{oos_s},{oos_e})  horizon={horizon} ===")

    # ---------- Protocol 1: DYNAMIC multi-step ----------
    log("--- Protocol 1: Dynamic multi-step ---")
    dyn = {}
    fc_store['dynamic'] = {}

    # naive
    for name, fn in [('B0a_NoChange', fc_no_change),
                     ('B0b_HistMean', fc_hist_mean),
                     ('B0c_Drift',    fc_drift)]:
        fc, spec = fn(ur_fit, horizon)
        dyn[name] = {'spec': spec, 'ur': metrics_block(fc, obs_ur)}
        fc_store['dynamic'][f'{name}_ur'] = fc
        log(f"  {name}: RMSE={dyn[name]['ur']['rmse']*100:.4f} pp  "
            f"Corr={dyn[name]['ur']['corr']:+.4f}  bias={dyn[name]['ur']['bias']*100:+.4f}")

    # AR
    fc, spec = fc_ar(ur_fit, horizon)
    dyn['B1_AR'] = {'spec': spec, 'ur': metrics_block(fc, obs_ur)}
    fc_store['dynamic']['B1_AR_ur'] = fc
    log(f"  B1_AR (p={spec['p_selected_BIC']}): RMSE={dyn['B1_AR']['ur']['rmse']*100:.4f} pp  "
        f"Corr={dyn['B1_AR']['ur']['corr']:+.4f}")

    # ARIMA (grid)
    fc, spec_arima = fc_arima(ur_fit, horizon, order=None)
    dyn['B2_ARIMA'] = {'spec': spec_arima, 'ur': metrics_block(fc, obs_ur)}
    fc_store['dynamic']['B2_ARIMA_ur'] = fc
    log(f"  B2_ARIMA {spec_arima['order_AIC']}: RMSE={dyn['B2_ARIMA']['ur']['rmse']*100:.4f} pp  "
        f"Corr={dyn['B2_ARIMA']['ur']['corr']:+.4f}")

    # ETS (3 variants, AIC select)
    fc, spec_ets = fc_ets(ur_fit, horizon, kind=None)
    dyn['B3_ETS'] = {'spec': spec_ets, 'ur': metrics_block(fc, obs_ur)}
    fc_store['dynamic']['B3_ETS_ur'] = fc
    log(f"  B3_ETS ({spec_ets['kind']}): RMSE={dyn['B3_ETS']['ur']['rmse']*100:.4f} pp  "
        f"Corr={dyn['B3_ETS']['ur']['corr']:+.4f}")

    # VAR
    fc, spec_var = fc_var(Y_var, horizon)
    dyn['B4_VAR'] = {'spec': spec_var,
                     'ur':   metrics_block(fc[:, 0], obs_ur),
                     'lfpr': metrics_block(fc[:, 1], obs_lfpr),
                     'epop': metrics_block(fc[:, 2], obs_epop)}
    fc_store['dynamic']['B4_VAR_ur'] = fc[:, 0]
    fc_store['dynamic']['B4_VAR_lfpr'] = fc[:, 1]
    fc_store['dynamic']['B4_VAR_epop'] = fc[:, 2]
    log(f"  B4_VAR (p={spec_var['p_selected_BIC']}): RMSE={dyn['B4_VAR']['ur']['rmse']*100:.4f} pp  "
        f"Corr={dyn['B4_VAR']['ur']['corr']:+.4f}")

    # Ridge VAR (uses observed OOS vac/sep)
    exog_oos = np.column_stack([v_full[oos_s:oos_e], s_full[oos_s:oos_e]])
    fc, spec_rv = fc_ridge_var(Y_rv, horizon, p=2, exog_oos=exog_oos, lam=None)
    dyn['B5_RidgeVAR'] = {'spec': spec_rv,
                          'ur':   metrics_block(fc[:, 0], obs_ur),
                          'lfpr': metrics_block(fc[:, 1], obs_lfpr),
                          'epop': metrics_block(fc[:, 2], obs_epop)}
    fc_store['dynamic']['B5_RidgeVAR_ur'] = fc[:, 0]
    fc_store['dynamic']['B5_RidgeVAR_lfpr'] = fc[:, 1]
    fc_store['dynamic']['B5_RidgeVAR_epop'] = fc[:, 2]
    log(f"  B5_RidgeVAR (lam={spec_rv['lambda']:.3g}): RMSE="
        f"{dyn['B5_RidgeVAR']['ur']['rmse']*100:.4f} pp  Corr={dyn['B5_RidgeVAR']['ur']['corr']:+.4f}")

    # Beveridge
    fc, spec_bv = fc_beveridge(ur_fit, v_fit, s_fit,
                                v_full[oos_s:oos_e], s_full[oos_s:oos_e])
    dyn['B6_Beveridge'] = {'spec': spec_bv, 'ur': metrics_block(fc, obs_ur)}
    fc_store['dynamic']['B6_Beveridge_ur'] = fc
    log(f"  B6_Beveridge: RMSE={dyn['B6_Beveridge']['ur']['rmse']*100:.4f} pp  "
        f"Corr={dyn['B6_Beveridge']['ur']['corr']:+.4f}")

    # DMP
    fc, spec_dmp = fc_dmp(ur_full_ff, v_full, s_full, fit_end, oos_e)
    dyn['B7_DMP'] = {'spec': spec_dmp, 'ur': metrics_block(fc, obs_ur)}
    fc_store['dynamic']['B7_DMP_ur'] = fc
    log(f"  B7_DMP (A={spec_dmp['A']:.3f}, alpha={spec_dmp['alpha']:.3f}): "
        f"RMSE={dyn['B7_DMP']['ur']['rmse']*100:.4f} pp  Corr={dyn['B7_DMP']['ur']['corr']:+.4f}")

    # Flow-based
    fc, spec_fl = fc_flow(ur_full_ff, s_full, fit_end, oos_e)
    dyn['B8_Flow'] = {'spec': spec_fl, 'ur': metrics_block(fc, obs_ur)}
    fc_store['dynamic']['B8_Flow_ur'] = fc
    log(f"  B8_Flow (rho_f={spec_fl['f_AR1_rho']:.3f}): "
        f"RMSE={dyn['B8_Flow']['ur']['rmse']*100:.4f} pp  Corr={dyn['B8_Flow']['ur']['corr']:+.4f}")

    out_regime['dynamic'] = dyn

    # Cache the AIC-selected orders for rolling reuse
    arima_order = spec_arima['order_AIC']
    ets_kind = spec_ets['kind']
    var_p = spec_var['p_selected_BIC']
    ridge_lam = spec_rv['lambda']

    # ---------- Protocol 2: ROLLING one-step-ahead ----------
    log("--- Protocol 2: Rolling one-step-ahead ---")
    rol = {name: {'ur': []} for name in
           ['B0a_NoChange', 'B0b_HistMean', 'B0c_Drift', 'B1_AR',
            'B2_ARIMA', 'B3_ETS', 'B4_VAR', 'B5_RidgeVAR',
            'B6_Beveridge', 'B7_DMP', 'B8_Flow']}
    rol_paths = {name: np.full(horizon, np.nan) for name in rol.keys()}
    rol_paths_lfpr = {name: np.full(horizon, np.nan) for name in ['B4_VAR', 'B5_RidgeVAR']}
    rol_paths_epop = {name: np.full(horizon, np.nan) for name in ['B4_VAR', 'B5_RidgeVAR']}

    for h in range(horizon):
        cur_end = oos_s + h            # fit on [0, cur_end), predict month cur_end
        ur_h = ffill(tgt_ur[:cur_end])
        lf_h = ffill(tgt_lfpr[:cur_end])
        ep_h = ffill(tgt_epop[:cur_end])
        Y1 = np.column_stack([ur_h, lf_h, ep_h])
        Y2 = np.column_stack([ur_h, lf_h, ep_h, v_full[:cur_end], s_full[:cur_end]])

        rol_paths['B0a_NoChange'][h] = ur_h[-1]
        rol_paths['B0b_HistMean'][h] = float(np.nanmean(ur_h))
        rol_paths['B0c_Drift'][h]    = fc_drift(ur_h, 1)[0][0]
        rol_paths['B1_AR'][h]        = fc_ar(ur_h, 1)[0][0]
        rol_paths['B2_ARIMA'][h]     = fc_arima(ur_h, 1, order=arima_order)[0][0]
        rol_paths['B3_ETS'][h]       = fc_ets(ur_h, 1, kind=ets_kind)[0][0]
        fc_v = fc_var(Y1, 1, p=var_p)[0]
        rol_paths['B4_VAR'][h]       = fc_v[0, 0]
        rol_paths_lfpr['B4_VAR'][h]  = fc_v[0, 1]
        rol_paths_epop['B4_VAR'][h]  = fc_v[0, 2]
        exog_h = np.column_stack([v_full[cur_end:cur_end+1], s_full[cur_end:cur_end+1]])
        fc_rv = fc_ridge_var(Y2, 1, p=2, exog_oos=exog_h, lam=ridge_lam)[0]
        rol_paths['B5_RidgeVAR'][h]      = fc_rv[0, 0]
        rol_paths_lfpr['B5_RidgeVAR'][h] = fc_rv[0, 1]
        rol_paths_epop['B5_RidgeVAR'][h] = fc_rv[0, 2]
        fc_bv = fc_beveridge(ur_h, v_full[:cur_end], s_full[:cur_end],
                              v_full[cur_end:cur_end+1], s_full[cur_end:cur_end+1])[0]
        rol_paths['B6_Beveridge'][h] = fc_bv[0]
        # DMP: refit per step is expensive; reuse fit from fit_end (only inflow/outflow change)
        rol_paths['B7_DMP'][h] = fc_dmp(ur_full_ff, v_full, s_full, cur_end, cur_end+1)[0][0]
        rol_paths['B8_Flow'][h] = fc_flow(ur_full_ff, s_full, cur_end, cur_end+1)[0][0]

    # Score rolling paths
    for name, path in rol_paths.items():
        rol[name]['ur'] = metrics_block(path, obs_ur)
    for name in ['B4_VAR', 'B5_RidgeVAR']:
        rol[name]['lfpr'] = metrics_block(rol_paths_lfpr[name], obs_lfpr)
        rol[name]['epop'] = metrics_block(rol_paths_epop[name], obs_epop)

    fc_store['rolling'] = {}
    for name, path in rol_paths.items():
        fc_store['rolling'][f'{name}_ur'] = path
    for name in ['B4_VAR', 'B5_RidgeVAR']:
        fc_store['rolling'][f'{name}_lfpr'] = rol_paths_lfpr[name]
        fc_store['rolling'][f'{name}_epop'] = rol_paths_epop[name]

    for name in rol.keys():
        log(f"  {name}: RMSE={rol[name]['ur']['rmse']*100:.4f} pp  "
            f"Corr={rol[name]['ur']['corr']:+.4f}  bias={rol[name]['ur']['bias']*100:+.4f}")

    out_regime['rolling'] = rol
    return out_regime, fc_store


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------
def main():
    t0 = time.time()
    log_path = os.path.join(OUT_DIR, 'rerun_log.txt')
    log_f = open(log_path, 'w', encoding='utf-8')

    def log(msg):
        print(msg, flush=True)
        log_f.write(msg + '\n'); log_f.flush()

    log("=" * 78)
    log("Section 6.4 (revised) — Stronger Forecast Benchmark Comparison")
    log("=" * 78)

    env, tgt_ur, tgt_lfpr, tgt_epop = get_targets()
    v_full = env.market_tightness.copy()
    s_full = env.separation_rate.copy()
    log(f"T={env.T} months;  dates {env.dates[0]} .. {env.dates[-1]}")
    log(f"OOS UR NaN at indices: "
        f"{[i for i, x in enumerate(tgt_ur) if np.isnan(x)]}")
    log(f"market_tightness range [{v_full.min():.3f}, {v_full.max():.3f}], "
        f"separation_rate range [{s_full.min():.4f}, {s_full.max():.4f}]")

    results = {'meta': {'T': int(env.T),
                        'dates_first': env.dates[0],
                        'dates_last': env.dates[-1],
                        'regimes': {k: dict(period=v['period'],
                                            oos=list(v['oos']),
                                            fit_end=int(v['fit_end']))
                                    for k, v in REGIMES.items()},
                        'WINDOWS_phase7': {k: list(v) for k, v in WINDOWS.items()},
                        'protocols': ['dynamic', 'rolling'],
                        'benchmarks': ['B0a_NoChange', 'B0b_HistMean', 'B0c_Drift',
                                       'B1_AR', 'B2_ARIMA', 'B3_ETS', 'B4_VAR',
                                       'B5_RidgeVAR', 'B6_Beveridge', 'B7_DMP', 'B8_Flow'],
                        'note': 'ABM (V_Full recalibrated) metrics pulled separately from '
                                'fix6.2/reeval_metrics.json in build script.'}}

    fc_npz_payload = {'dates_full': np.array(env.dates),
                      'tgt_ur_full': tgt_ur, 'tgt_lfpr_full': tgt_lfpr,
                      'tgt_epop_full': tgt_epop,
                      'v_full': v_full, 's_full': s_full}

    for rid, cfg in REGIMES.items():
        rg_t0 = time.time()
        out, fc = run_regime(rid, cfg, tgt_ur, tgt_lfpr, tgt_epop,
                             v_full, s_full, log)
        results[rid] = out
        for proto, store in fc.items():
            for k, v in store.items():
                fc_npz_payload[f'{rid}__{proto}__{k}'] = v
        log(f"  -- regime {rid} done in {time.time()-rg_t0:.1f}s")

    # Save
    with open(os.path.join(OUT_DIR, 'benchmark_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=lambda x: float(x)
                  if isinstance(x, (np.floating, np.integer)) else x.tolist()
                  if isinstance(x, np.ndarray) else str(x))
    np.savez(os.path.join(OUT_DIR, 'benchmark_series.npz'), **fc_npz_payload)
    log(f"\nSaved benchmark_metrics.json and benchmark_series.npz")
    log("=" * 78)
    log(f"Section 6.4 benchmark rerun done in {time.time() - t0:.1f} s")
    log("=" * 78)
    log_f.close()


if __name__ == '__main__':
    main()
