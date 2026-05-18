"""
Package B Step 3: analysis.
- Horizon x Model RMSE pivot table
- Ranking per horizon
- Degradation slope (log-log)
- Advantage half-life of M0 vs each baseline
- Horizon source-of-advantage (het/mech/hh)
- Relative advantage curves
Outputs CSVs + stability_report.json + summary prints.
"""
import os, csv, json
import numpy as np
import pandas as pd

os.makedirs('Phase3_Output/packageB', exist_ok=True)

HORIZONS = [1, 3, 6, 12, 24, 36]
MODELS = ['M0_Main', 'D1_Homogeneous', 'D2_Simplified', 'D3_LaborOnly',
          'B1_AR', 'B2_VAR', 'B3_Beveridge', 'B4_DMP']

df = pd.read_csv('Phase3_Output/packageB/horizon_results.csv')

# =====================================================
# 1. UR RMSE pivot
# =====================================================
piv = df.pivot(index='model', columns='horizon', values='ur_rmse_pp')
piv = piv.reindex(MODELS).reindex(columns=HORIZONS)
piv.to_csv('Phase3_Output/packageB/horizon_rmse_pivot.csv', float_format='%.4f')
print("\n=== UR RMSE (pp) by horizon ===")
print(piv.to_string(float_format='%.3f'))

# =====================================================
# 2. Rankings per horizon
# =====================================================
ranks_rows = []
for h in HORIZONS:
    col = piv[h].dropna()
    order = col.sort_values().index.tolist()
    for rk, m in enumerate(order, 1):
        ranks_rows.append({'horizon': h, 'rank': rk, 'model': m, 'ur_rmse_pp': col[m]})
ranks_df = pd.DataFrame(ranks_rows)
ranks_df.to_csv('Phase3_Output/packageB/horizon_ranking_table.csv', index=False,
                float_format='%.4f')
print("\n=== Top-3 per horizon ===")
for h in HORIZONS:
    sub = ranks_df[(ranks_df.horizon == h) & (ranks_df['rank'] <= 3)]
    s = ', '.join(f"{r['rank']}.{r['model']}({r['ur_rmse_pp']:.2f})" for _, r in sub.iterrows())
    print(f"  h={h:>2d}: {s}")

# =====================================================
# 3. Degradation slope (OLS log-log)
# =====================================================
slopes = {}
for m in MODELS:
    vals = piv.loc[m].dropna()
    if len(vals) < 3:
        slopes[m] = np.nan; continue
    x = np.log(vals.index.values.astype(float))
    y = np.log(vals.values)
    b = np.polyfit(x, y, 1)[0]
    slopes[m] = float(b)
slopes_df = pd.DataFrame([{'model': m, 'log_log_slope': slopes[m],
                           'rmse_h1': piv.loc[m].get(1, np.nan),
                           'rmse_h36': piv.loc[m].get(36, np.nan),
                           'abs_change_pp': (piv.loc[m].get(36, np.nan) -
                                             piv.loc[m].get(1, np.nan))}
                          for m in MODELS])
slopes_df.to_csv('Phase3_Output/packageB/horizon_degradation_table.csv', index=False,
                 float_format='%.4f')
print("\n=== Degradation slope (log-log) ===")
for m in MODELS:
    print(f"  {m:20s}  slope={slopes[m]:>+.3f}  "
          f"h1->h36: {piv.loc[m].get(1, np.nan):.2f} -> {piv.loc[m].get(36, np.nan):.2f} pp")

# =====================================================
# 4. Advantage half-life of M0 vs each baseline
# =====================================================
hl = {}
m0 = piv.loc['M0_Main']
for b in MODELS:
    if b == 'M0_Main': continue
    bv = piv.loc[b]
    # find largest h where M0 < baseline
    good_hs = [h for h in HORIZONS if (not np.isnan(m0[h])) and (not np.isnan(bv[h]))
               and (m0[h] < bv[h])]
    # find smallest h where M0 >= baseline (loss horizon)
    bad_hs = [h for h in HORIZONS if (not np.isnan(m0[h])) and (not np.isnan(bv[h]))
              and (m0[h] >= bv[h])]
    hl[b] = {
        'half_life_h': max(good_hs) if good_hs else 0,
        'first_loss_h': min(bad_hs) if bad_hs else None,
        'wins': len(good_hs), 'total': len(good_hs) + len(bad_hs),
    }
print("\n=== M0 vs baselines: advantage structure ===")
for b, v in hl.items():
    print(f"  M0 vs {b:20s}  wins {v['wins']}/{v['total']}  "
          f"half_life={v['half_life_h']}  first_loss={v['first_loss_h']}")

# =====================================================
# 5. Source of advantage per horizon
# =====================================================
soa_rows = []
for h in HORIZONS:
    if any(np.isnan(piv.loc[m].get(h, np.nan)) for m in ['M0_Main', 'D1_Homogeneous', 'D2_Simplified', 'D3_LaborOnly']):
        continue
    ur_M0 = piv.loc['M0_Main', h]
    ur_D1 = piv.loc['D1_Homogeneous', h]
    ur_D2 = piv.loc['D2_Simplified', h]
    ur_D3 = piv.loc['D3_LaborOnly', h]
    total = ur_D2 - ur_M0
    het = ur_D1 - ur_M0
    mech = ur_D2 - ur_D1
    hh = ur_D3 - ur_M0
    soa_rows.append({
        'horizon': h,
        'ur_M0_pp': ur_M0, 'ur_D1_pp': ur_D1, 'ur_D2_pp': ur_D2, 'ur_D3_pp': ur_D3,
        'delta_het_pp': het, 'delta_mech_pp': mech, 'delta_hh_pp': hh, 'total_pp': total,
        'het_share': het / total if abs(total) > 1e-9 else np.nan,
        'mech_share': mech / total if abs(total) > 1e-9 else np.nan,
        'hh_share': hh / total if abs(total) > 1e-9 else np.nan,
    })
soa_df = pd.DataFrame(soa_rows)
soa_df.to_csv('Phase3_Output/packageB/horizon_source_of_advantage.csv',
              index=False, float_format='%.4f')
print("\n=== Horizon Source-of-Advantage ===")
for _, r in soa_df.iterrows():
    print(f"  h={int(r.horizon):>2d}  M0={r.ur_M0_pp:.2f}  total={r.total_pp:>+.2f} "
          f"het_share={r.het_share:>+.2f}  mech_share={r.mech_share:>+.2f}  "
          f"hh_share={r.hh_share:>+.2f}")

# =====================================================
# 6. LFPR / EPOP sub-table
# =====================================================
for tgt in ['lfpr_rmse_pp', 'epop_rmse_pp']:
    piv_aux = df.pivot(index='model', columns='horizon', values=tgt).reindex(MODELS).reindex(columns=HORIZONS)
    piv_aux.to_csv(f'Phase3_Output/packageB/horizon_{tgt}_pivot.csv', float_format='%.4f')

# =====================================================
# 7. Final claim JSON
# =====================================================
# M0 rank per horizon
m0_ranks = {h: int(ranks_df[(ranks_df.horizon == h) & (ranks_df.model == 'M0_Main')]['rank'].iloc[0])
            if len(ranks_df[(ranks_df.horizon == h) & (ranks_df.model == 'M0_Main')]) > 0 else None
            for h in HORIZONS}
all_rank1 = all(v == 1 for v in m0_ranks.values())
all_half36 = all(v['half_life_h'] == 36 for v in hl.values())
if all_rank1 and all_half36:
    situation = 'A_full_robust'
elif m0_ranks.get(1, 99) <= 2 and m0_ranks.get(12, 99) <= 2:
    situation = 'B_short_med_strong_long_shrink'
else:
    situation = 'C_short_only'

claim = {
    'm0_ranks_per_horizon': m0_ranks,
    'advantage_half_life': hl,
    'degradation_slopes': slopes,
    'situation': situation,
}
with open('Phase3_Output/packageB/packageB_claim.json', 'w') as f:
    json.dump(claim, f, indent=2, default=float)
print(f"\n=== Final situation: {situation} ===")
print(f"M0 ranks per horizon: {m0_ranks}")
print("Saved all tables + packageB_claim.json")
