"""Package D analysis - aggregate CSV, write 6 markdown reports + summary."""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT = 'Phase3_Output/packageD'
df = pd.read_csv(f'{OUT}/agent_count_results.csv')

GRID = [5000, 10000, 25000, 50000, 100000, 200000, 300000]
MODELS = ['M0', 'D1', 'D2', 'D3']
MODES = ['subsample', 'regenerate']

# Aggregate
agg_cols = ['ur_rmse_pp', 'lfpr_rmse_pp', 'epop_rmse_pp',
            'eu_mean', 'ue_mean', 'h2m_share', 'avg_buffer',
            'runtime_s', 'peak_mem_mb']
agg = (df.groupby(['mode', 'N', 'model'])[agg_cols]
         .agg(['mean', 'std', 'min', 'max'])
         .reset_index())
agg.columns = ['_'.join([c for c in col if c]).rstrip('_') for col in agg.columns]
agg.to_csv(f'{OUT}/agent_count_aggregated.csv', index=False)

# ---------- Convergence ----------
def conv_table(mode):
    rows = []
    for model in MODELS:
        sub = agg[(agg['mode'] == mode) & (agg['model'] == model)].sort_values('N')
        prev = None
        for _, r in sub.iterrows():
            d_ur = (prev - r['ur_rmse_pp_mean']) if prev is not None else np.nan
            rows.append({
                'mode': mode, 'model': model, 'N': int(r['N']),
                'ur_mean': r['ur_rmse_pp_mean'], 'ur_std': r['ur_rmse_pp_std'],
                'lfpr_mean': r['lfpr_rmse_pp_mean'],
                'epop_mean': r['epop_rmse_pp_mean'],
                'delta_ur_vs_prev': d_ur,
                'plateau': (not np.isnan(d_ur)) and abs(d_ur) < 0.015,
            })
            prev = r['ur_rmse_pp_mean']
    return pd.DataFrame(rows)

conv_sub = conv_table('subsample')
conv_reg = conv_table('regenerate')
conv_all = pd.concat([conv_sub, conv_reg], ignore_index=True)
conv_all.to_csv(f'{OUT}/convergence_table.csv', index=False)

# ---------- MC noise scaling (log-log regression of std vs N) ----------
mc = []
for mode in MODES:
    for model in MODELS:
        sub = agg[(agg['mode'] == mode) & (agg['model'] == model)].sort_values('N')
        # Only include distinct-N region (subsample at 100/200/300k is the same data, drop dupes)
        if mode == 'subsample':
            sub = sub[sub['N'] <= 100000]
        Ns = sub['N'].values
        stds = sub['ur_rmse_pp_std'].values
        mask = (stds > 1e-4) & np.isfinite(stds)
        if mask.sum() >= 3:
            logN = np.log(Ns[mask])
            logS = np.log(stds[mask])
            alpha, beta = np.polyfit(logN, logS, 1)
        else:
            alpha, beta = np.nan, np.nan
        mc.append({
            'mode': mode, 'model': model,
            'std_5k': sub.iloc[0]['ur_rmse_pp_std'],
            'std_100k': sub[sub['N'] == 100000]['ur_rmse_pp_std'].iloc[0] if (sub['N'] == 100000).any() else np.nan,
            'alpha_std_vs_N': alpha,
            'intercept': beta,
        })
mc_df = pd.DataFrame(mc)
mc_df.to_csv(f'{OUT}/mc_noise_scaling.csv', index=False)

# ---------- Ranking by N (regenerate mode) ----------
rank_rows = []
for mode in MODES:
    for N in GRID:
        sub = agg[(agg['mode'] == mode) & (agg['N'] == N)].sort_values('ur_rmse_pp_mean')
        rank = {r['model']: i + 1 for i, (_, r) in enumerate(sub.iterrows())}
        # per-seed ranking win rate (M0 vs D1)
        seeds = sorted(df['seed'].unique())
        m0_wins_d1 = 0; m0_wins_d2 = 0; m0_wins_d3 = 0
        for s in seeds:
            r0 = df[(df['mode']==mode)&(df['N']==N)&(df['model']=='M0')&(df['seed']==s)]['ur_rmse_pp'].iloc[0]
            r1 = df[(df['mode']==mode)&(df['N']==N)&(df['model']=='D1')&(df['seed']==s)]['ur_rmse_pp'].iloc[0]
            r2 = df[(df['mode']==mode)&(df['N']==N)&(df['model']=='D2')&(df['seed']==s)]['ur_rmse_pp'].iloc[0]
            r3 = df[(df['mode']==mode)&(df['N']==N)&(df['model']=='D3')&(df['seed']==s)]['ur_rmse_pp'].iloc[0]
            m0_wins_d1 += (r0 < r1); m0_wins_d2 += (r0 < r2); m0_wins_d3 += (r0 < r3)
        rank_rows.append({
            'mode': mode, 'N': N,
            'rank_M0': rank['M0'], 'rank_D1': rank['D1'],
            'rank_D2': rank['D2'], 'rank_D3': rank['D3'],
            'M0_win_D1': m0_wins_d1 / 10, 'M0_win_D2': m0_wins_d2 / 10,
            'M0_win_D3': m0_wins_d3 / 10,
            'advantage_vs_D1_pp':
                sub[sub['model']=='D1']['ur_rmse_pp_mean'].iloc[0] -
                sub[sub['model']=='M0']['ur_rmse_pp_mean'].iloc[0],
        })
rank_df = pd.DataFrame(rank_rows)
rank_df.to_csv(f'{OUT}/ranking_by_count.csv', index=False)

# ---------- Cost scaling ----------
cost_rows = []
for model in MODELS:
    sub = agg[(agg['mode'] == 'regenerate') & (agg['model'] == model)].sort_values('N')
    Ns = sub['N'].values
    rts = sub['runtime_s_mean'].values
    logN, logR = np.log(Ns), np.log(rts)
    alpha, beta = np.polyfit(logN, logR, 1)
    cost_rows.append({'model': model, 'alpha_runtime_vs_N': alpha,
                      'runtime_100k': sub[sub['N']==100000]['runtime_s_mean'].iloc[0],
                      'runtime_5k': sub[sub['N']==5000]['runtime_s_mean'].iloc[0],
                      'mem_100k_mb': sub[sub['N']==100000]['peak_mem_mb_mean'].iloc[0],
                      'mem_300k_mb': sub[sub['N']==300000]['peak_mem_mb_mean'].iloc[0]})
cost_df = pd.DataFrame(cost_rows)
cost_df.to_csv(f'{OUT}/cost_scaling.csv', index=False)

# ---------- Summary print ----------
print("=" * 72)
print("PACKAGE D - SUMMARY")
print("=" * 72)
print("\nConvergence (Regenerate mode, M0):")
m0_reg = conv_reg[conv_reg['model'] == 'M0']
for _, r in m0_reg.iterrows():
    tag = "  <<< plateau" if r['plateau'] else ""
    print(f"  N={r['N']:6d}  UR={r['ur_mean']:.3f}+/-{r['ur_std']:.3f}  "
          f"deltaUR={r['delta_ur_vs_prev']:+.3f}pp{tag}")

print("\nMC noise slope (alpha where seed_std ~ N^alpha, ideal = -0.5):")
for _, r in mc_df.iterrows():
    print(f"  {r['mode']:10s} {r['model']}  alpha={r['alpha_std_vs_N']:+.3f}")

print("\nRanking consistency (M0 win rate vs D1/D2/D3 across N, regenerate):")
for _, r in rank_df[rank_df['mode']=='regenerate'].iterrows():
    print(f"  N={r['N']:6d}  rank_M0={r['rank_M0']}  "
          f"M0>D1:{r['M0_win_D1']:.1f}  M0>D2:{r['M0_win_D2']:.1f}  M0>D3:{r['M0_win_D3']:.1f}  "
          f"adv={r['advantage_vs_D1_pp']:+.3f}pp")

print("\nRuntime scaling (alpha where runtime ~ N^alpha, ideal = 1.0):")
for _, r in cost_df.iterrows():
    print(f"  {r['model']}  alpha={r['alpha_runtime_vs_N']:.3f}  "
          f"runtime@100k={r['runtime_100k']:.2f}s  mem@100k={r['mem_100k_mb']:.1f}MB")

print("\nAll CSVs written to", OUT)
