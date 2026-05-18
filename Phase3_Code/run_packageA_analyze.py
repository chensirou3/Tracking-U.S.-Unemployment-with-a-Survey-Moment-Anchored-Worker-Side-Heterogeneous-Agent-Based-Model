"""
Package A Step 3: Analysis.
- Ranking stability across splits
- Parameter drift across splits
- Source-of-advantage decomposition per split
- Hard-window identification
Output: stability_report.json + comparison_table.csv + parameter_drift.csv
"""
import sys, os, json, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs('Phase3_Output/packageA', exist_ok=True)

with open('Phase3_Output/packageA/packageA_all_results.json') as f:
    results = json.load(f)
with open('Phase3_Output/packageA/split_best_params.json') as f:
    cal = json.load(f)

MODELS = ['M0_Main', 'D1_Homogeneous', 'D2_Simplified', 'D3_LaborOnly',
          'B1_AR', 'B2_VAR', 'B3_Beveridge', 'B4_DMP']
SPLITS = list(results.keys())
PARAM_NAMES = cal['param_names']


def get_rmse(sid, m):
    r = results[sid]['models'][m].get('ur_rmse_mean', np.nan)
    try:
        return float(r)
    except (TypeError, ValueError):
        return np.nan


# ============================================================
# 1. Comparison table: rows=splits, cols=models, value=UR RMSE pp
# ============================================================
table_rows = []
for sid in SPLITS:
    row = {'split': sid, 'type': results[sid]['type']}
    for m in MODELS:
        row[m] = get_rmse(sid, m) * 100  # convert to pp
    table_rows.append(row)

with open('Phase3_Output/packageA/comparison_table.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['split', 'type'] + MODELS)
    w.writeheader()
    for r in table_rows:
        w.writerow(r)

# ============================================================
# 2. Ranking across splits
# ============================================================
rankings = {m: [] for m in MODELS}
for sid in SPLITS:
    vals = [(m, get_rmse(sid, m)) for m in MODELS]
    vals_sorted = sorted(vals, key=lambda x: (np.inf if np.isnan(x[1]) else x[1]))
    for rk, (m, _) in enumerate(vals_sorted, 1):
        rankings[m].append(rk)

ranking_summary = {}
for m in MODELS:
    rks = np.array(rankings[m])
    ranking_summary[m] = {
        'per_split': dict(zip(SPLITS, [int(x) for x in rks])),
        'mean_rank': float(rks.mean()),
        'median_rank': float(np.median(rks)),
        'worst_rank': int(rks.max()),
        'best_rank': int(rks.min()),
        'n_rank1': int((rks == 1).sum()),
        'n_top3': int((rks <= 3).sum()),
    }

# ============================================================
# 3. Win-rate (model vs baseline) on UR RMSE
# ============================================================
def winrate(model_a, model_b):
    wins = 0; total = 0
    for sid in SPLITS:
        a, b = get_rmse(sid, model_a), get_rmse(sid, model_b)
        if np.isnan(a) or np.isnan(b): continue
        total += 1
        if a < b: wins += 1
    return wins, total

winrate_matrix = {}
for a in ['M0_Main']:
    winrate_matrix[a] = {}
    for b in MODELS:
        if a == b: continue
        w, t = winrate(a, b)
        winrate_matrix[a][b] = {'wins': w, 'total': t, 'rate': w / t if t else 0}

# ============================================================
# 4. Source-of-advantage decomposition per split
# ============================================================
def soa_for_split(sid):
    ur_M0 = get_rmse(sid, 'M0_Main')
    ur_D1 = get_rmse(sid, 'D1_Homogeneous')
    ur_D2 = get_rmse(sid, 'D2_Simplified')
    ur_D3 = get_rmse(sid, 'D3_LaborOnly')
    if any(np.isnan([ur_M0, ur_D1, ur_D2, ur_D3])):
        return None
    total = ur_D2 - ur_M0
    delta_het = ur_D1 - ur_M0
    delta_mech = ur_D2 - ur_D1
    delta_hh = ur_D3 - ur_M0
    return {
        'ur_M0_pp': ur_M0 * 100, 'ur_D1_pp': ur_D1 * 100,
        'ur_D2_pp': ur_D2 * 100, 'ur_D3_pp': ur_D3 * 100,
        'delta_het_pp': delta_het * 100, 'delta_mech_pp': delta_mech * 100,
        'delta_hh_pp': delta_hh * 100, 'total_pp': total * 100,
        'het_share': delta_het / total if abs(total) > 1e-9 else 0,
        'mech_share': delta_mech / total if abs(total) > 1e-9 else 0,
        'het_helps': bool(delta_het > 0),
    }

soa = {sid: soa_for_split(sid) for sid in SPLITS}

# ============================================================
# 5. Parameter drift across splits
# ============================================================
param_matrix = np.zeros((len(SPLITS), len(PARAM_NAMES)))
for i, sid in enumerate(SPLITS):
    p = cal['splits'][sid]['best_params']
    for j, pn in enumerate(PARAM_NAMES):
        param_matrix[i, j] = p[pn]

drift_summary = {}
with open('Phase3_Output/packageA/parameter_drift.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['param'] + SPLITS + ['mean', 'std', 'cv', 'stability'])
    for j, pn in enumerate(PARAM_NAMES):
        vals = param_matrix[:, j]
        mean = float(vals.mean()); std = float(vals.std())
        cv = std / abs(mean) if abs(mean) > 1e-9 else np.inf
        stab = 'STABLE' if cv < 0.1 else ('MILD' if cv < 0.3 else 'SIGNIFICANT')
        drift_summary[pn] = {'mean': mean, 'std': std, 'cv': cv, 'stability': stab,
                             'per_split': dict(zip(SPLITS, [float(v) for v in vals]))}
        w.writerow([pn] + [f'{v:.4f}' for v in vals] + [f'{mean:.4f}', f'{std:.4f}', f'{cv:.3f}', stab])

# ============================================================
# 6. Summary stats
# ============================================================
het_shares = [soa[sid]['het_share'] for sid in SPLITS if soa[sid]]
het_helps = [soa[sid]['het_helps'] for sid in SPLITS if soa[sid]]

output = {
    'n_splits': len(SPLITS), 'splits': SPLITS, 'models': MODELS,
    'comparison_table_pp': table_rows,
    'ranking': ranking_summary,
    'winrate_vs_baselines': winrate_matrix,
    'source_of_advantage': soa,
    'parameter_drift': drift_summary,
    'global_summary': {
        'M0_rank1_splits': ranking_summary['M0_Main']['n_rank1'],
        'M0_top3_splits': ranking_summary['M0_Main']['n_top3'],
        'M0_mean_rank': ranking_summary['M0_Main']['mean_rank'],
        'het_share_mean': float(np.mean(het_shares)),
        'het_share_std': float(np.std(het_shares)),
        'het_helps_in_splits': int(sum(het_helps)),
        'stable_params': sum(1 for k, v in drift_summary.items() if v['stability'] == 'STABLE'),
        'mild_drift_params': sum(1 for k, v in drift_summary.items() if v['stability'] == 'MILD'),
        'sig_drift_params': sum(1 for k, v in drift_summary.items() if v['stability'] == 'SIGNIFICANT'),
    }
}
with open('Phase3_Output/packageA/stability_report.json', 'w') as f:
    json.dump(output, f, indent=2, default=float)

# Print summary
print("=" * 72)
print(f"PACKAGE A - Stability Summary")
print("=" * 72)
print(f"\nM0 ranks across {len(SPLITS)} splits:")
for m in MODELS:
    rs = ranking_summary[m]
    print(f"  {m:20s} mean_rk={rs['mean_rank']:.2f} #1={rs['n_rank1']} top3={rs['n_top3']}")
print(f"\nM0 win-rate:")
for b, w in winrate_matrix['M0_Main'].items():
    print(f"  vs {b:20s}: {w['wins']}/{w['total']} = {w['rate']*100:.0f}%")
print(f"\nHeterogeneity helps in {sum(het_helps)}/{len(het_helps)} splits")
print(f"Mean het_share = {np.mean(het_shares):.2f}")
print(f"\nParameter drift:")
for pn, d in drift_summary.items():
    print(f"  {pn:20s} cv={d['cv']:.3f}  {d['stability']}")
print(f"\nSaved stability_report.json + comparison_table.csv + parameter_drift.csv")
