"""Print human-readable summary of Section 6.2 derived-control rerun."""
import json
import numpy as np

with open('正式撰写/6.2/derived_metrics.json', encoding='utf-8') as f:
    D = json.load(f)

summary = D['summary']
seeds = D['seeds']

print('=' * 78)
print(f"Variants: {D['variants']}")
print(f"Seeds (n={len(seeds)}): {seeds}")
print(f"Param source: {D['parameter_source']}")
print('=' * 78)

for vname in D['variants']:
    print(f"\n--- {vname} ---")
    for w in ['train', 'val', 'oos']:
        s = summary[vname][w]
        print(f"  {w:>5}: "
              f"UR_RMSE={s['ur_rmse_mean']*100:.3f}\u00b1{s['ur_rmse_std']*100:.3f} pp  "
              f"UR_MAE={s['ur_mae_mean']*100:.3f} pp  "
              f"UR_Corr={s['ur_corr_mean']:.3f}\u00b1{s['ur_corr_std']:.3f}  "
              f"LFPR_RMSE={s['lfpr_rmse_mean']*100:.3f} pp  "
              f"EPOP_RMSE={s['epop_rmse_mean']*100:.3f} pp  "
              f"UR_sim_mean={s['ur_mean_mean']*100:.3f} pp")

print('\n' + '=' * 78)
print("SOURCE-OF-ADVANTAGE DECOMPOSITION (OOS UR RMSE, pp)")
print('=' * 78)
m0  = summary['M0_Full']['oos']['ur_rmse_mean'] * 100
d1  = summary['D1_Homogeneous']['oos']['ur_rmse_mean'] * 100
d2  = summary['D2_Simplified']['oos']['ur_rmse_mean'] * 100
d3  = summary['D3_LaborOnly']['oos']['ur_rmse_mean'] * 100
m0_sd = summary['M0_Full']['oos']['ur_rmse_std'] * 100
d1_sd = summary['D1_Homogeneous']['oos']['ur_rmse_std'] * 100
d2_sd = summary['D2_Simplified']['oos']['ur_rmse_std'] * 100
d3_sd = summary['D3_LaborOnly']['oos']['ur_rmse_std'] * 100
print(f"  M0_Full           : {m0:.4f} \u00b1 {m0_sd:.4f} pp")
print(f"  D1_Homogeneous    : {d1:.4f} \u00b1 {d1_sd:.4f} pp")
print(f"  D2_Simplified     : {d2:.4f} \u00b1 {d2_sd:.4f} pp")
print(f"  D3_LaborOnly      : {d3:.4f} \u00b1 {d3_sd:.4f} pp")

total = d2 - m0
mech  = d2 - d1
het   = d1 - m0
hh    = d3 - m0
print(f"\n  Total Gain         (D2 -> M0): {total:.4f} pp")
print(f"  Mechanism Gain     (D2 -> D1): {mech:.4f} pp")
print(f"  Heterogeneity Gain (D1 -> M0): {het:.4f} pp")
print(f"  Household Gain     (D3 -> M0): {hh:.4f} pp")
if total > 0:
    print(f"\n  Heterogeneity Share: {100*het/total:.1f}%")
    print(f"  Mechanism Share    : {100*mech/total:.1f}%")
else:
    print("  Total Gain <= 0; share decomposition undefined.")

# Seed CV
print('\n' + '=' * 78)
print("SEED STABILITY (CV = std/mean, OOS UR RMSE)")
print('=' * 78)
for vname in D['variants']:
    s = summary[vname]['oos']
    cv = 100 * s['ur_rmse_std'] / s['ur_rmse_mean'] if s['ur_rmse_mean'] else float('nan')
    print(f"  {vname:<18}: mean={s['ur_rmse_mean']*100:.3f} pp  sd={s['ur_rmse_std']*100:.4f} pp  CV={cv:.1f}%")

# Compare with previous source_of_advantage.json
print('\n' + '=' * 78)
print("COMPARISON WITH PREVIOUS PHASE 8 RESULTS")
print('=' * 78)
try:
    with open('Phase3_Output/phase8/source_of_advantage.json', encoding='utf-8') as f:
        old = json.load(f)
    old_map = {r['config'].split(' ')[0].replace('M0_Main', 'M0_Full'): r['ur_rmse_pp']
               for r in old}
    new_map = {'M0_Full': m0, 'D1_Homogeneous': d1,
               'D2_Simplified': d2, 'D3_LaborOnly': d3}
    print(f"  {'variant':<18} {'old (3 seeds)':>14} {'new (5 seeds)':>14} {'delta':>10}")
    for k in ['M0_Full', 'D3_LaborOnly', 'D1_Homogeneous', 'D2_Simplified']:
        ov = old_map.get(k, float('nan'))
        nv = new_map[k]
        print(f"  {k:<18} {ov:>14.4f} {nv:>14.4f} {nv-ov:>+10.4f}")
except Exception as e:
    print(f"  Could not compare: {e}")
