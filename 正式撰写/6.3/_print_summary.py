"""Human-readable summary of 6.3 ablation + ladder reruns."""
import json
import numpy as np

with open('正式撰写/6.3/ablation_metrics.json', encoding='utf-8') as f:
    A = json.load(f)
with open('正式撰写/6.3/ladder_metrics.json', encoding='utf-8') as f:
    L = json.load(f)

print('=' * 90)
print(f"Phase 7 ablation: {len(A['variants'])} variants × {len(A['seeds'])} seeds")
print(f"Package C ladder: {len(L['levels'])} levels × {len(L['seeds'])} seeds")
print('=' * 90)

baseline_oos = A['summary']['baseline']['oos']
base_ur = baseline_oos['ur_rmse_mean'] * 100
base_lfpr = baseline_oos['lfpr_rmse_mean'] * 100
base_epop = baseline_oos['epop_rmse_mean'] * 100
print(f"\nBASELINE (full heterogeneous ABM, OOS):")
print(f"  UR_RMSE   = {base_ur:.4f} ± {baseline_oos['ur_rmse_std']*100:.4f} pp")
print(f"  LFPR_RMSE = {base_lfpr:.4f} pp")
print(f"  EPOP_RMSE = {base_epop:.4f} pp")
print(f"  UR_Corr   = {baseline_oos['ur_corr_mean']:.4f}")

print('\n' + '=' * 90)
print("DIMENSION ABLATION RANKING (by ΔUR_RMSE, OOS)")
print('=' * 90)
dims = ['income_exp', 'labor_frag', 'liquidity', 'search', 'housing', 'consumption_rule']
dim_rows = []
for d in dims:
    s = A['summary'][f'dim_{d}']['oos']
    ur = s['ur_rmse_mean'] * 100; sd = s['ur_rmse_std'] * 100
    lfpr = s['lfpr_rmse_mean'] * 100; epop = s['epop_rmse_mean'] * 100
    dim_rows.append((d, ur, ur - base_ur, sd, s['ur_corr_mean'], lfpr, epop))
dim_rows.sort(key=lambda r: -r[2])
for d, ur, delt, sd, corr, lfpr, epop in dim_rows:
    print(f"  {d:<22}  UR={ur:.3f} pp  ΔUR={delt:+.3f}  sd={sd:.3f}  "
          f"Corr={corr:.3f}  LFPR={lfpr:.3f}  EPOP={epop:.3f}")

print('\n' + '=' * 90)
print("MECHANISM ABLATION RANKING (by ΔUR_RMSE, OOS)")
print('=' * 90)
mechs = ['high_fragility_modifier', 'liquidity_constraint_modifier',
         'housing_lockin_modifier', 'fragility_x_liquidity_interaction',
         'matching_competition', 'discouraged_worker',
         'housing_reentry_friction', 'expectation_participation',
         'effective_mpc_adjustment', 'consumption_sequencing',
         'buffer_consumption_ordering', 'state_dependent_expectation',
         'experience_dependent_expectation']
mech_rows = []
for m in mechs:
    s = A['summary'][f'mech_{m}']['oos']
    ur = s['ur_rmse_mean'] * 100; sd = s['ur_rmse_std'] * 100
    lfpr = s['lfpr_rmse_mean'] * 100; epop = s['epop_rmse_mean'] * 100
    mech_rows.append((m, ur, ur - base_ur, sd, s['ur_corr_mean'], lfpr, epop))
mech_rows.sort(key=lambda r: -r[2])
for m, ur, delt, sd, corr, lfpr, epop in mech_rows:
    print(f"  {m:<38}  UR={ur:.3f}  ΔUR={delt:+.3f}  sd={sd:.3f}  "
          f"Corr={corr:.3f}  LFPR={lfpr:.3f}  EPOP={epop:.3f}")

print('\n' + '=' * 90)
print("PACKAGE C LADDER (OOS)")
print('=' * 90)
order = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'G2', 'G3']
for lid in order:
    s = L['summary'][lid]
    o = s['oos']
    ur = o['ur_rmse_mean'] * 100; sd = o['ur_rmse_std'] * 100
    lfpr = o['lfpr_rmse_mean'] * 100; epop = o['epop_rmse_mean'] * 100
    print(f"  {lid}  ({s['ladder']:5s})  n={s['n_active_dim']}  "
          f"UR={ur:.3f}±{sd:.3f}  ΔvsL6={ur-base_ur:+.3f}  "
          f"LFPR={lfpr:.3f}  EPOP={epop:.3f}  active=[{s['active_dims']}]")

print('\n' + '=' * 90)
print("COMPARISON WITH PREVIOUS PHASE 7 ABLATION (3 seeds)")
print('=' * 90)
with open('Phase3_Output/phase7/ablation_results.json', encoding='utf-8') as f:
    OLD = json.load(f)
old_map = {r['ablation']: r['ur_rmse'] * 100 for r in OLD['summary']}
print(f"  {'config':<22} {'old(3 seeds)':>13} {'new(5 seeds)':>13} {'Δ':>8}")
print(f"  {'none/baseline':<22} {old_map.get('none', float('nan')):>13.4f} "
      f"{base_ur:>13.4f} {base_ur - old_map.get('none', np.nan):>+8.4f}")
for d in dims:
    ov = old_map.get(d, float('nan'))
    nv = A['summary'][f'dim_{d}']['oos']['ur_rmse_mean'] * 100
    print(f"  {d:<22} {ov:>13.4f} {nv:>13.4f} {nv - ov:>+8.4f}")
