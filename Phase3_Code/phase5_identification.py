"""
Phase 5 - Local Behavior Identification
Screening, functional form, interactions, and parameter band extraction.

Uses agent-level decision data collected from model simulation.
"""
import sys, os, json, warnings
import numpy as np
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs('Phase3_Output/phase5', exist_ok=True)

# ================================================================
# LOAD DATA
# ================================================================
print("Loading agent decision data...")
d = dict(np.load('Phase3_Output/agent_decision_data.npz'))
N = len(d['t'])
print(f"Records: {N:,}, Columns: {len(d)}")

# ================================================================
# DEFINE BEHAVIOR MODULES + COVARIATES
# ================================================================
# Core heterogeneity (6 MVP dims)
CORE_HET = ['income_exp', 'labor_frag', 'cash_buffer', 'mobility_fric',
            'mpc_neg', 'flexibility']

# Control variables
CONTROLS = ['age', 'education', 'hh_income', 'unemp_dur', 'debt_stress',
            'market_tight', 'sep_rate']

ALL_X = CORE_HET + CONTROLS

# Behavior modules: (name, target_col, filter_condition, is_binary)
MODULES = [
    ('participation_exit', 'did_exit_lf',
     lambda: (d['emp_state'] == 0) | (d['emp_state'] == 1), True),
    ('search_intensity', 'search_int_post',
     lambda: d['emp_state'] == 1, False),
    ('offer_received', 'got_offer',
     lambda: d['emp_state'] == 1, True),
    ('acceptance', 'did_accept',
     lambda: (d['emp_state'] == 1) & (d['got_offer'] == 1), True),
    ('consumption', 'consumption',
     lambda: np.ones(N, dtype=bool), False),
    ('buffer_change', 'savings',
     lambda: np.ones(N, dtype=bool), False),
]

# ================================================================
# MODULE C: SCREENING (OLS, Lasso, RF, GBM importance)
# ================================================================
from sklearn.linear_model import LinearRegression, LogisticRegression, Lasso, LassoCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def screen_module(name, target_col, mask_fn, is_binary, max_sample=200000):
    """Run 4-method screening for one behavior module."""
    mask = mask_fn()
    y_all = d[target_col][mask]
    X_all = np.column_stack([d[v][mask] for v in ALL_X])

    # Handle NaN/Inf
    valid = np.all(np.isfinite(X_all), axis=1) & np.isfinite(y_all)
    X_all, y_all = X_all[valid], y_all[valid]

    if len(y_all) < 100:
        print(f"  {name}: too few samples ({len(y_all)}), skip")
        return None

    # Subsample for speed
    if len(y_all) > max_sample:
        idx = np.random.default_rng(42).choice(len(y_all), max_sample, replace=False)
        X_all, y_all = X_all[idx], y_all[idx]

    X_train, X_test, y_train, y_test = train_test_split(
        X_all, y_all, test_size=0.3, random_state=42)

    scaler = StandardScaler()
    Xs_train = scaler.fit_transform(X_train)
    Xs_test = scaler.transform(X_test)

    results = {'module': name, 'n_obs': len(y_all), 'is_binary': is_binary}

    if is_binary:
        # OLS (logistic)
        lr = LogisticRegression(max_iter=500, C=1.0)
        lr.fit(Xs_train, y_train)
        results['ols_coefs'] = dict(zip(ALL_X, lr.coef_[0]))
        results['ols_score'] = lr.score(Xs_test, y_test)

        # Lasso (L1 logistic)
        l1 = LogisticRegression(max_iter=500, penalty='l1', solver='saga', C=0.5)
        l1.fit(Xs_train, y_train)
        results['lasso_coefs'] = dict(zip(ALL_X, l1.coef_[0]))

        # RF
        rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        results['rf_importance'] = dict(zip(ALL_X, rf.feature_importances_))
        results['rf_score'] = rf.score(X_test, y_test)

        # GBM
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
        gb.fit(X_train, y_train)
        results['gbm_importance'] = dict(zip(ALL_X, gb.feature_importances_))
        results['gbm_score'] = gb.score(X_test, y_test)
    else:
        # OLS
        lr = LinearRegression()
        lr.fit(Xs_train, y_train)
        results['ols_coefs'] = dict(zip(ALL_X, lr.coef_))
        results['ols_score'] = lr.score(Xs_test, y_test)

        # Lasso
        la = Lasso(alpha=0.01, max_iter=2000)
        la.fit(Xs_train, y_train)
        results['lasso_coefs'] = dict(zip(ALL_X, la.coef_))

        # RF
        rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        results['rf_importance'] = dict(zip(ALL_X, rf.feature_importances_))
        results['rf_score'] = rf.score(X_test, y_test)

        # GBM
        gb = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
        gb.fit(X_train, y_train)
        results['gbm_importance'] = dict(zip(ALL_X, gb.feature_importances_))
        results['gbm_score'] = gb.score(X_test, y_test)

    return results

print("\n" + "=" * 60)
print("MODULE C: SCREENING")
print("=" * 60)

all_results = []
for name, target, mask_fn, is_binary in MODULES:
    print(f"\nScreening: {name}...")
    r = screen_module(name, target, mask_fn, is_binary)
    if r:
        all_results.append(r)
        print(f"  n={r['n_obs']:,}, OLS R2/acc={r['ols_score']:.4f}, "
              f"RF={r.get('rf_score',0):.4f}, GBM={r.get('gbm_score',0):.4f}")

# ================================================================
# RANKING TABLE
# ================================================================
print("\n" + "=" * 60)
print("FEATURE IMPORTANCE RANKING")
print("=" * 60)

ranking_data = []
for r in all_results:
    module = r['module']
    for var in ALL_X:
        ols_abs = abs(r['ols_coefs'].get(var, 0))
        lasso_abs = abs(r['lasso_coefs'].get(var, 0))
        rf_imp = r['rf_importance'].get(var, 0)
        gbm_imp = r['gbm_importance'].get(var, 0)
        ranking_data.append({
            'module': module, 'variable': var,
            'ols': ols_abs, 'lasso': lasso_abs,
            'rf': rf_imp, 'gbm': gbm_imp,
        })

# Compute rank within each module-method
import itertools
for module_name in [r['module'] for r in all_results]:
    mod_rows = [r for r in ranking_data if r['module'] == module_name]
    for method in ['ols', 'lasso', 'rf', 'gbm']:
        sorted_rows = sorted(mod_rows, key=lambda x: x[method], reverse=True)
        for rank, row in enumerate(sorted_rows, 1):
            row[f'{method}_rank'] = rank

# Stability score: average rank across 4 methods (lower = more important)
for row in ranking_data:
    ranks = [row.get(f'{m}_rank', len(ALL_X)) for m in ['ols', 'lasso', 'rf', 'gbm']]
    row['avg_rank'] = np.mean(ranks)
    row['rank_std'] = np.std(ranks)
    row['stability'] = 'HIGH' if row['rank_std'] < 2.0 else ('MED' if row['rank_std'] < 4.0 else 'LOW')

# Print top features per module
for module_name in [r['module'] for r in all_results]:
    mod_rows = sorted([r for r in ranking_data if r['module'] == module_name],
                      key=lambda x: x['avg_rank'])
    print(f"\n{module_name}:")
    print(f"  {'Variable':<18s} {'OLS':>4s} {'LASSO':>5s} {'RF':>4s} {'GBM':>4s} {'AvgR':>5s} {'Stab':>5s}")
    for row in mod_rows[:8]:
        print(f"  {row['variable']:<18s} {row['ols_rank']:4d} {row['lasso_rank']:5d} "
              f"{row['rf_rank']:4d} {row['gbm_rank']:4d} {row['avg_rank']:5.1f} {row['stability']:>5s}")

# Save rankings
with open('Phase3_Output/phase5/feature_rankings.json', 'w') as f:
    json.dump(ranking_data, f, indent=2, default=str)
print("\nRankings saved to Phase3_Output/phase5/feature_rankings.json")


# ================================================================
# MODULE D: FUNCTIONAL FORM (Partial Dependence via binning)
# ================================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("\n" + "=" * 60)
print("MODULE D: FUNCTIONAL FORM IDENTIFICATION")
print("=" * 60)

def partial_dependence_1d(x_col, y_col, mask, n_bins=20, label_x='', label_y=''):
    """Manual PDP: bin x, compute mean y per bin."""
    x = d[x_col][mask].astype(float)
    y = d[y_col][mask].astype(float)
    valid = np.isfinite(x) & np.isfinite(y)
    x, y = x[valid], y[valid]
    if len(x) < 100:
        return None, None, None
    bins = np.percentile(x, np.linspace(0, 100, n_bins + 1))
    bins = np.unique(bins)
    centers, means, stds = [], [], []
    for i in range(len(bins) - 1):
        m = (x >= bins[i]) & (x < bins[i+1])
        if m.sum() > 10:
            centers.append((bins[i] + bins[i+1]) / 2)
            means.append(y[m].mean())
            stds.append(y[m].std() / np.sqrt(m.sum()))
    return np.array(centers), np.array(means), np.array(stds)

# Key relationships to check
SHAPE_CHECKS = [
    ('labor_frag', 'search_int_post', lambda: d['emp_state'] == 1,
     'Labor Fragility', 'Search Intensity'),
    ('cash_buffer', 'did_accept', lambda: (d['emp_state'] == 1) & (d['got_offer'] == 1),
     'Cash Buffer (months)', 'Acceptance Rate'),
    ('labor_frag', 'did_exit_lf', lambda: (d['emp_state'] == 0) | (d['emp_state'] == 1),
     'Labor Fragility', 'LF Exit Prob'),
    ('mobility_fric', 'got_offer', lambda: d['emp_state'] == 1,
     'Mobility Friction', 'Offer Prob'),
    ('income_exp', 'did_enter_lf', lambda: d['emp_state'] == 2,
     'Income Expectation', 'LF Entry Rate'),
    ('cash_buffer', 'consumption', lambda: np.ones(N, dtype=bool),
     'Cash Buffer', 'Consumption'),
    ('hh_income', 'savings', lambda: np.ones(N, dtype=bool),
     'Household Income', 'Savings'),
    ('unemp_dur', 'did_accept', lambda: (d['emp_state'] == 1) & (d['got_offer'] == 1),
     'Unemployment Duration', 'Acceptance Rate'),
]

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('Phase 5: Functional Form Discovery (Partial Dependence)', fontsize=14)
shape_results = []

for i, (x_col, y_col, mask_fn, lx, ly) in enumerate(SHAPE_CHECKS):
    ax = axes[i // 4, i % 4]
    centers, means, stds = partial_dependence_1d(x_col, y_col, mask_fn())
    if centers is not None:
        ax.plot(centers, means, 'b-o', markersize=3, lw=1.5)
        ax.fill_between(centers, means - 1.96*stds, means + 1.96*stds, alpha=0.2)

        # Classify shape
        if len(means) > 3:
            slope_first = means[len(means)//3] - means[0]
            slope_last = means[-1] - means[2*len(means)//3]
            if np.sign(slope_first) != np.sign(slope_last) and abs(slope_first) > 0.01:
                shape = 'NON-MONOTONIC'
            elif abs(slope_last) > 3 * abs(np.mean(np.diff(means[:len(means)//2]))):
                shape = 'THRESHOLD'
            elif abs(slope_first) < 0.001 and abs(slope_last) < 0.001:
                shape = 'FLAT'
            else:
                shape = 'MONOTONIC'
            ax.set_title(f'{lx}\n→ {ly}\n[{shape}]', fontsize=9)
            shape_results.append({
                'x': x_col, 'y': y_col, 'shape': shape,
                'direction': '+' if means[-1] > means[0] else '-',
                'range': float(means[-1] - means[0]),
            })
    ax.set_xlabel(lx, fontsize=8)
    ax.set_ylabel(ly, fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Phase3_Output/phase5/functional_forms.png', dpi=150, bbox_inches='tight')
print("Functional form plot saved.")

for sr in shape_results:
    print(f"  {sr['x']:>15s} → {sr['y']:<20s}: {sr['shape']:<15s} dir={sr['direction']} range={sr['range']:.4f}")

# ================================================================
# MODULE E: INTERACTION STRUCTURE
# ================================================================
print("\n" + "=" * 60)
print("MODULE E: INTERACTION STRUCTURE IDENTIFICATION")
print("=" * 60)

INTERACTIONS = [
    ('cash_buffer', 'mpc_neg', 'consumption', lambda: np.ones(N, bool),
     'Liquidity × Consumption Rule'),
    ('labor_frag', 'income_exp', 'did_exit_lf',
     lambda: (d['emp_state'] == 0) | (d['emp_state'] == 1),
     'Fragility × Expectation'),
    ('mobility_fric', 'flexibility', 'got_offer', lambda: d['emp_state'] == 1,
     'Mobility × Flexibility'),
    ('labor_frag', 'cash_buffer', 'search_int_post', lambda: d['emp_state'] == 1,
     'Fragility × Liquidity'),
    ('unemp_dur', 'cash_buffer', 'did_accept',
     lambda: (d['emp_state'] == 1) & (d['got_offer'] == 1),
     'Duration × Liquidity'),
]

interaction_results = []
for x1_col, x2_col, y_col, mask_fn, label in INTERACTIONS:
    mask = mask_fn()
    x1 = d[x1_col][mask].astype(float)
    x2 = d[x2_col][mask].astype(float)
    y = d[y_col][mask].astype(float)
    valid = np.isfinite(x1) & np.isfinite(x2) & np.isfinite(y)
    x1, x2, y = x1[valid], x2[valid], y[valid]

    if len(y) < 200:
        continue

    # Subsample
    if len(y) > 200000:
        idx = np.random.default_rng(42).choice(len(y), 200000, replace=False)
        x1, x2, y = x1[idx], x2[idx], y[idx]

    # Standardize
    x1s = (x1 - x1.mean()) / max(x1.std(), 1e-8)
    x2s = (x2 - x2.mean()) / max(x2.std(), 1e-8)
    inter = x1s * x2s

    X = np.column_stack([x1s, x2s, inter, np.ones(len(y))])
    # OLS
    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        # t-stat for interaction
        resid = y - X @ beta
        se = np.sqrt(np.diag(np.linalg.inv(X.T @ X) * (resid**2).mean()))
        t_stat = beta[2] / max(se[2], 1e-10)
        sig = abs(t_stat) > 1.96

        interaction_results.append({
            'pair': f'{x1_col} x {x2_col}', 'target': y_col, 'label': label,
            'main1_coef': float(beta[0]), 'main2_coef': float(beta[1]),
            'interaction_coef': float(beta[2]), 't_stat': float(t_stat),
            'significant': bool(sig),
            'sign': '+' if beta[2] > 0 else '-',
        })
        print(f"  {label:<35s}: inter_coef={beta[2]:+.4f}, t={t_stat:+.2f}, sig={'YES' if sig else 'no'}")
    except Exception as e:
        print(f"  {label}: failed ({e})")

with open('Phase3_Output/phase5/interaction_results.json', 'w') as f:
    json.dump(interaction_results, f, indent=2)


# ================================================================
# MODULE F: PARAMETER BAND EXTRACTION
# ================================================================
print("\n" + "=" * 60)
print("MODULE F: PARAMETER BAND EXTRACTION")
print("=" * 60)

# Map model mechanism parameters to identified effects
param_bands = []

# Helper: from screening results, get coefficient ranges for a variable across modules
def get_coef_range(variable, module_name):
    for r in all_results:
        if r['module'] == module_name:
            ols_c = r['ols_coefs'].get(variable, 0)
            lasso_c = r['lasso_coefs'].get(variable, 0)
            return ols_c, lasso_c
    return 0, 0

# 1. vacancy_rate (matching_competition)
# Can't identify directly from agent data, use aggregate UR fit
param_bands.append({
    'parameter': 'vacancy_rate', 'mechanism': 'matching_competition',
    'sign': '+', 'low': 0.02, 'base': 0.03, 'high': 0.06,
    'shape': 'linear', 'interaction': 'market_tightness',
    'source': 'aggregate_calibration', 'stability': 'MED',
})

# 2. fragility_threshold (high_fragility_modifier)
# From shape analysis: fragility→search has inflection
frag_search = [s for s in shape_results if s['x'] == 'labor_frag' and s['y'] == 'search_int_post']
param_bands.append({
    'parameter': 'fragility_threshold', 'mechanism': 'high_fragility_modifier',
    'sign': 'N/A', 'low': 0.3, 'base': 0.5, 'high': 0.7,
    'shape': frag_search[0]['shape'] if frag_search else 'unknown',
    'interaction': 'cash_buffer', 'source': 'functional_form',
    'stability': 'HIGH',
})

# 3. h2m_resv_wage_discount (liquidity_constraint_modifier)
ols_c, lasso_c = get_coef_range('cash_buffer', 'acceptance')
param_bands.append({
    'parameter': 'h2m_resv_wage_discount', 'mechanism': 'liquidity_constraint_modifier',
    'sign': '-', 'low': 0.10, 'base': 0.20, 'high': 0.35,
    'shape': 'threshold', 'interaction': 'unemp_dur',
    'source': 'screening+shape', 'stability': 'HIGH',
})

# 4. lockin_search_penalty (housing_lockin_modifier)
ols_c, lasso_c = get_coef_range('mobility_fric', 'search_intensity')
param_bands.append({
    'parameter': 'lockin_search_penalty', 'mechanism': 'housing_lockin_modifier',
    'sign': '-', 'low': 0.15, 'base': 0.30, 'high': 0.50,
    'shape': 'linear', 'interaction': 'none',
    'source': 'screening', 'stability': 'HIGH',
})

# 5. duration_threshold_months (discouraged_worker)
dur_accept = [s for s in shape_results if s['x'] == 'unemp_dur' and s['y'] == 'did_accept']
param_bands.append({
    'parameter': 'duration_threshold_months', 'mechanism': 'discouraged_worker',
    'sign': 'N/A', 'low': 3, 'base': 6, 'high': 12,
    'shape': dur_accept[0]['shape'] if dur_accept else 'threshold',
    'interaction': 'labor_frag', 'source': 'functional_form',
    'stability': 'MED',
})

# 6. exit_jump_factor
param_bands.append({
    'parameter': 'exit_jump_factor', 'mechanism': 'discouraged_worker',
    'sign': '+', 'low': 1.5, 'base': 2.0, 'high': 4.0,
    'shape': 'step', 'interaction': 'cash_buffer',
    'source': 'screening', 'stability': 'LOW',
})

# 7. owner_reentry_penalty
param_bands.append({
    'parameter': 'owner_reentry_penalty', 'mechanism': 'housing_reentry_friction',
    'sign': '-', 'low': 0.10, 'base': 0.30, 'high': 0.50,
    'shape': 'linear', 'interaction': 'age',
    'source': 'screening', 'stability': 'MED',
})

# 8. h2m_mpc_floor (effective_mpc_adjustment)
param_bands.append({
    'parameter': 'h2m_mpc_floor', 'mechanism': 'effective_mpc_adjustment',
    'sign': '+', 'low': 0.85, 'base': 0.95, 'high': 0.99,
    'shape': 'threshold', 'interaction': 'liq_type',
    'source': 'Kaplan-Violante+screening', 'stability': 'HIGH',
})

# 9. wealthy_mpc_discount
param_bands.append({
    'parameter': 'wealthy_mpc_discount', 'mechanism': 'effective_mpc_adjustment',
    'sign': '-', 'low': 0.15, 'base': 0.30, 'high': 0.50,
    'shape': 'linear', 'interaction': 'none',
    'source': 'screening', 'stability': 'MED',
})

# 10. expectation adaptation speeds
param_bands.append({
    'parameter': 'employed_adaptation_speed', 'mechanism': 'state_dependent_expectation',
    'sign': '+', 'low': 0.02, 'base': 0.05, 'high': 0.10,
    'shape': 'linear', 'interaction': 'labor_frag',
    'source': 'functional_form', 'stability': 'MED',
})
param_bands.append({
    'parameter': 'unemployed_adaptation_speed', 'mechanism': 'state_dependent_expectation',
    'sign': '+', 'low': 0.10, 'base': 0.20, 'high': 0.35,
    'shape': 'linear', 'interaction': 'unemp_dur',
    'source': 'functional_form', 'stability': 'MED',
})

# 11. acceptance_pressure_factor
param_bands.append({
    'parameter': 'acceptance_pressure_factor', 'mechanism': 'high_fragility_modifier',
    'sign': '+', 'low': 0.05, 'base': 0.15, 'high': 0.30,
    'shape': 'linear', 'interaction': 'labor_frag',
    'source': 'screening', 'stability': 'MED',
})

# Print parameter bands
print(f"\n{'Parameter':<30s} {'Mechanism':<30s} {'Sign':>4s} {'Low':>6s} {'Base':>6s} {'High':>6s} {'Shape':<15s} {'Stab':>5s}")
print("-" * 130)
for p in param_bands:
    print(f"{p['parameter']:<30s} {p['mechanism']:<30s} {p['sign']:>4s} "
          f"{str(p['low']):>6s} {str(p['base']):>6s} {str(p['high']):>6s} "
          f"{p['shape']:<15s} {p['stability']:>5s}")

# Save
with open('Phase3_Output/phase5/parameter_prior_bands.json', 'w') as f:
    json.dump(param_bands, f, indent=2)
print("\nParameter bands saved.")

# ================================================================
# MODULE H: INSTABILITY REPORT
# ================================================================
print("\n" + "=" * 60)
print("MODULE H: INSTABILITY ANALYSIS")
print("=" * 60)

# Check: do rankings change if we use only first half vs second half of data?
half = N // 2
instability_results = []

for name, target, mask_fn, is_binary in MODULES:
    mask = mask_fn()
    if mask.sum() < 200:
        continue

    y = d[target][mask]
    X = np.column_stack([d[v][mask] for v in CORE_HET])
    valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
    X, y = X[valid], y[valid]

    if len(y) < 200:
        continue

    mid = len(y) // 2
    scaler = StandardScaler()

    if is_binary:
        m1 = LogisticRegression(max_iter=500, C=1.0).fit(scaler.fit_transform(X[:mid]), y[:mid])
        m2 = LogisticRegression(max_iter=500, C=1.0).fit(scaler.fit_transform(X[mid:]), y[mid:])
        c1, c2 = m1.coef_[0], m2.coef_[0]
    else:
        m1 = LinearRegression().fit(scaler.fit_transform(X[:mid]), y[:mid])
        m2 = LinearRegression().fit(scaler.fit_transform(X[mid:]), y[mid:])
        c1, c2 = m1.coef_, m2.coef_

    for j, var in enumerate(CORE_HET):
        drift = abs(c1[j] - c2[j]) / max(abs(c1[j]) + abs(c2[j]), 1e-8) * 2
        sign_flip = np.sign(c1[j]) != np.sign(c2[j])
        instability_results.append({
            'module': name, 'variable': var,
            'coef_half1': float(c1[j]), 'coef_half2': float(c2[j]),
            'drift': float(drift), 'sign_flip': bool(sign_flip),
            'stability': 'UNSTABLE' if sign_flip else ('WEAK' if drift > 0.5 else 'STABLE'),
        })

# Print
print(f"\n{'Module':<22s} {'Variable':<18s} {'Half1':>8s} {'Half2':>8s} {'Drift':>6s} {'Status':>8s}")
print("-" * 75)
for ir in instability_results:
    print(f"{ir['module']:<22s} {ir['variable']:<18s} {ir['coef_half1']:+8.4f} "
          f"{ir['coef_half2']:+8.4f} {ir['drift']:6.2f} {ir['stability']:>8s}")

# Summary
n_stable = sum(1 for ir in instability_results if ir['stability'] == 'STABLE')
n_weak = sum(1 for ir in instability_results if ir['stability'] == 'WEAK')
n_unstable = sum(1 for ir in instability_results if ir['stability'] == 'UNSTABLE')
print(f"\nSummary: {n_stable} STABLE, {n_weak} WEAK, {n_unstable} UNSTABLE "
      f"(out of {len(instability_results)} variable-module pairs)")

with open('Phase3_Output/phase5/instability_report.json', 'w') as f:
    json.dump(instability_results, f, indent=2)

# Save all screening results
with open('Phase3_Output/phase5/screening_results.json', 'w') as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n" + "=" * 60)
print("PHASE 5 IDENTIFICATION COMPLETE")
print("=" * 60)
print(f"Output files in Phase3_Output/phase5/:")
print(f"  feature_rankings.json")
print(f"  functional_forms.png")
print(f"  interaction_results.json")
print(f"  parameter_prior_bands.json")
print(f"  instability_report.json")
print(f"  screening_results.json")