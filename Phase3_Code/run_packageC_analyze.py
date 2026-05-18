"""
Package C analysis:
- Read projection + refit CSVs
- Compute marginal gains, cumulative share, complexity efficiency
- Refit benefit (projection - refit)
- Minimal sufficient set detection
- Output: packageC_ladder_analysis.csv, minimal_sufficient_set.json, packageC_report.md
"""
import sys, os, json, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT = 'Phase3_Output/packageC'

CORE_ORDER = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']
LAYER_ORDER = ['G1', 'G2', 'G3', 'G4']
LAYER_EQUIV = {'G1': 'L2', 'G4': 'L6'}   # G1 == L2 (labor only), G4 == L6 (full)


def read_csv(path):
    rows = []
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            for k, v in row.items():
                if v in ('', None):
                    row[k] = None
                else:
                    try:
                        row[k] = float(v)
                    except (ValueError, TypeError):
                        pass
            rows.append(row)
    return rows


def pick(rows, key):
    return {r['level']: r for r in rows if r['level'] == key or r.get('level') == key} if False else {r['level']: r for r in rows}


def main():
    proj = read_csv(f'{OUT}/projection_ladder_results.csv')
    refit = read_csv(f'{OUT}/refit_ladder_results.csv')
    pmap = pick(proj, 'level')
    rmap = pick(refit, 'level')

    # Metrics to track per-level
    analysis = []
    for lid in CORE_ORDER:
        p = pmap.get(lid)
        r = rmap.get(lid)
        row = {'level': lid, 'n_active_dim': int(p['n_active_dim']),
               'active_dims': p['active_dims'] or ''}
        row['proj_ur_rmse_pp'] = p['ur_rmse_pp_mean']
        row['proj_ur_rmse_std'] = p['ur_rmse_pp_std']
        row['proj_lfpr_rmse_pp'] = p['lfpr_rmse_pp_mean']
        row['proj_epop_rmse_pp'] = p['epop_rmse_pp_mean']
        row['refit_ur_rmse_pp'] = r['ur_rmse_pp_mean']
        row['refit_ur_rmse_std'] = r['ur_rmse_pp_std']
        row['refit_lfpr_rmse_pp'] = r['lfpr_rmse_pp_mean']
        row['refit_epop_rmse_pp'] = r['epop_rmse_pp_mean']
        row['refit_h2m'] = r['h2m_share_mean']
        row['refit_buffer'] = r['avg_buffer_mean']
        analysis.append(row)

    # Marginal / cumulative / efficiency (on Refit track, which is the fair one)
    base_r = analysis[0]['refit_ur_rmse_pp']
    full_r = analysis[-1]['refit_ur_rmse_pp']
    total_gain = base_r - full_r
    for i, row in enumerate(analysis):
        prev = analysis[i-1]['refit_ur_rmse_pp'] if i > 0 else row['refit_ur_rmse_pp']
        row['refit_marginal_pp'] = float(prev - row['refit_ur_rmse_pp']) if i > 0 else 0.0
        row['refit_cum_pp'] = float(base_r - row['refit_ur_rmse_pp'])
        row['refit_cum_share'] = float(row['refit_cum_pp'] / total_gain) if total_gain > 1e-6 else np.nan
        row['complexity_eff'] = float(row['refit_cum_pp'] / row['n_active_dim']) if row['n_active_dim'] > 0 else 0.0
        # Projection track marginal (secondary view)
        prev_p = analysis[i-1]['proj_ur_rmse_pp'] if i > 0 else row['proj_ur_rmse_pp']
        row['proj_marginal_pp'] = float(prev_p - row['proj_ur_rmse_pp']) if i > 0 else 0.0
        # Refit benefit
        row['refit_benefit_pp'] = float(row['proj_ur_rmse_pp'] - row['refit_ur_rmse_pp'])

    # Minimal sufficient set: smallest k such that cum_share >= 0.90 AND subsequent marginal < 0.05
    minimal_k = None
    for i, row in enumerate(analysis):
        if row['refit_cum_share'] is None or np.isnan(row['refit_cum_share']):
            continue
        if row['refit_cum_share'] >= 0.90:
            minimal_k = i
            break
    minimal_set = {
        'level': analysis[minimal_k]['level'] if minimal_k is not None else 'L6',
        'n_active_dim': analysis[minimal_k]['n_active_dim'] if minimal_k is not None else 6,
        'active_dims': analysis[minimal_k]['active_dims'] if minimal_k is not None else analysis[-1]['active_dims'],
        'cum_share': analysis[minimal_k]['refit_cum_share'] if minimal_k is not None else 1.0,
        'refit_ur_rmse_pp': analysis[minimal_k]['refit_ur_rmse_pp'] if minimal_k is not None else full_r,
        'criterion': 'smallest k such that refit_cum_share >= 0.90',
    }

    # Detect plateau / negative returns
    plateau_levels = [row['level'] for row in analysis if 0 < row['refit_marginal_pp'] < 0.02]
    negative_levels = [row['level'] for row in analysis if row['refit_marginal_pp'] < -0.03]

    # Layer ladder table
    player = read_csv(f'{OUT}/projection_ladder_results.csv')
    layer_rows = []
    for lid in LAYER_ORDER:
        src = lid if lid not in LAYER_EQUIV else LAYER_EQUIV[lid]
        r = next((x for x in player if x['level'] == src), None)
        if r:
            layer_rows.append({
                'group': lid,
                'equivalent': src if src != lid else '-',
                'n_active_dim': int(r['n_active_dim']),
                'active_dims': r['active_dims'],
                'ur_rmse_pp': r['ur_rmse_pp_mean'],
                'lfpr_rmse_pp': r['lfpr_rmse_pp_mean'],
                'epop_rmse_pp': r['epop_rmse_pp_mean'],
            })

    # Write analysis CSV
    with open(f'{OUT}/packageC_ladder_analysis.csv', 'w', newline='') as f:
        keys = list(analysis[0].keys())
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in analysis:
            w.writerow(row)

    # Minimal set JSON
    with open(f'{OUT}/minimal_sufficient_set.json', 'w') as f:
        json.dump({
            'minimal_set': minimal_set,
            'plateau_levels': plateau_levels,
            'negative_return_levels': negative_levels,
            'full_model_refit_rmse_pp': full_r,
            'homogeneous_refit_rmse_pp': base_r,
            'total_gain_pp': total_gain,
        }, f, indent=2)

    # Write layer analysis
    with open(f'{OUT}/layer_ladder_results.csv', 'w', newline='') as f:
        if layer_rows:
            w = csv.DictWriter(f, fieldnames=list(layer_rows[0].keys()))
            w.writeheader()
            for row in layer_rows:
                w.writerow(row)

    # Print summary
    print("=" * 72)
    print("PACKAGE C ANALYSIS")
    print("=" * 72)
    print(f"{'Lv':4s} {'dim':3s}  {'Proj':>7s}  {'Refit':>7s}  {'ΔRefit':>7s}  "
          f"{'CumSh':>6s}  {'CE':>6s}  {'Benefit':>7s}")
    for row in analysis:
        print(f"{row['level']:4s} {row['n_active_dim']:3d}  "
              f"{row['proj_ur_rmse_pp']:7.3f}  {row['refit_ur_rmse_pp']:7.3f}  "
              f"{row['refit_marginal_pp']:+7.3f}  "
              f"{row['refit_cum_share']:>6.2f}  {row['complexity_eff']:>6.3f}  "
              f"{row['refit_benefit_pp']:+7.3f}")
    print(f"\nMinimal sufficient set: {minimal_set['level']} "
          f"(dim={minimal_set['n_active_dim']}, cum_share={minimal_set['cum_share']:.2f})")
    print(f"Active dims: {minimal_set['active_dims']}")
    print(f"Plateau levels (0 < Δ < 0.02): {plateau_levels}")
    print(f"Negative return levels (Δ < -0.03): {negative_levels}")


if __name__ == '__main__':
    main()
