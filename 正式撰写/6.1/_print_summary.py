import json, numpy as np
M = json.load(open('Phase3_Output/phase7/main_run_metrics.json'))
d = np.load('Phase3_Output/phase7/main_run_series.npz', allow_pickle=True)
t_ur, t_lfpr, t_epop = d['target_ur'], d['target_lfpr'], d['target_epop']
obs_ur_oos = float(np.nanmean(t_ur[252:302])) * 100
obs_lfpr_oos = float(np.nanmean(t_lfpr[252:302])) * 100
obs_epop_oos = float(np.nanmean(t_epop[252:302])) * 100
print(f"OOS observed mean UR={obs_ur_oos:.4f} pp  LFPR={obs_lfpr_oos:.4f} pp  EPOP={obs_epop_oos:.4f} pp")
for v in ['conservative', 'baseline', 'aggressive']:
    for w in ['train', 'val', 'oos']:
        s = M['summary'][v][w]
        print(f"{v:13s} {w:5s}  UR_RMSE={s['ur_rmse_mean']*100:.4f}+/-{s['ur_rmse_std']*100:.4f} pp  "
              f"Corr={s['ur_corr_mean']:.4f}  LFPR_RMSE={s['lfpr_rmse_mean']*100:.4f} pp  "
              f"EPOP_RMSE={s['epop_rmse_mean']*100:.4f} pp  UR_sim_mean={s['ur_mean_mean']*100:.3f} pp  "
              f"LFPR_sim_mean={s['lfpr_mean_mean']*100:.3f} pp")
print("\n--- Baseline OOS per-seed UR RMSE ---")
for s in [42, 137, 2024, 888, 1234]:
    m = M['all_metrics']['baseline'][str(s)]['oos']
    print(f"  seed={s:5d}: UR_RMSE={m['ur_rmse']*100:.4f} pp  MAE={m['ur_mae']*100:.4f} pp  Corr={m['ur_corr']:.4f}")
import statistics as st
rmses = [M['all_metrics']['baseline'][str(s)]['oos']['ur_rmse']*100 for s in [42,137,2024,888,1234]]
print(f"  mean={st.mean(rmses):.4f}  sd={st.pstdev(rmses):.5f}  CV={100*st.pstdev(rmses)/st.mean(rmses):.2f}%")
