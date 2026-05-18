"""
Package E — analysis.
Produces:
  - method_aggregated.csv        per-method aggregates
  - top_k_per_method.csv         top-5 per method
  - param_stability.csv          14-param x 5-method stability
  - param_overlap.csv            pairwise method overlap on each param (14x10)
  - best_so_far.csv              convergence trajectories
  - performance_comparison_report.md
  - parameter_overlap_report.md
  - source_of_advantage_report.md
  - cost_benefit_report.md
  - packageE_claim_update.md
"""
import os, sys, json, itertools
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Phase3_Code.calibration_engine import param_names, PARAM_SPACE

OUT = 'Phase3_Output/packageE'
RAW_CSV = os.path.join(OUT, 'method_raw_results.csv')
SOA_CSV = os.path.join(OUT, 'source_of_advantage_per_method.csv')
METHODS = ['M1_RS', 'M2_LHS', 'M3_Sobol', 'M4_CtF', 'M5_DE']
TOP_K = 5


def _best_so_far(ser):
    return np.minimum.accumulate(ser.values)


def build_aggregates(df):
    rows = []
    for mid in METHODS:
        sub = df[df.method_id == mid].copy().reset_index(drop=True)
        if len(sub) == 0:
            continue
        top5 = sub.nsmallest(TOP_K, 'train_loss_mean')
        rank1 = sub.loc[sub['train_loss_mean'].idxmin()]
        rows.append({
            'method_id': mid,
            'n_evals': len(sub),
            'failed_total': int(sub['failed_seeds'].sum()),
            'best_train_loss': float(sub['train_loss_mean'].min()),
            'best_val_loss': float(rank1['val_loss_mean']),
            'best_test_ur_rmse_pp': float(rank1['test_ur_rmse_pp']),
            'best_test_lfpr_rmse_pp': float(rank1['test_lfpr_rmse_pp']),
            'best_test_epop_rmse_pp': float(rank1['test_epop_rmse_pp']),
            'top5_train_loss_mean': float(top5['train_loss_mean'].mean()),
            'top5_train_loss_std': float(top5['train_loss_mean'].std(ddof=1)),
            'top5_val_loss_mean': float(top5['val_loss_mean'].mean()),
            'top5_test_ur_mean': float(top5['test_ur_rmse_pp'].mean()),
            'top5_test_ur_std': float(top5['test_ur_rmse_pp'].std(ddof=1)),
            'mean_train_loss': float(sub['train_loss_mean'].mean()),
            'median_train_loss': float(sub['train_loss_mean'].median()),
            'total_runtime_min': float(sub['runtime_s'].sum() / 60.0),
            'mean_runtime_s': float(sub['runtime_s'].mean()),
        })
    return pd.DataFrame(rows)


def build_top_k_table(df):
    rows = []
    for mid in METHODS:
        sub = df[df.method_id == mid]
        if len(sub) == 0:
            continue
        top5 = sub.nsmallest(TOP_K, 'train_loss_mean').reset_index(drop=True)
        for r, (_, row) in enumerate(top5.iterrows()):
            out = {'method_id': mid, 'rank': r + 1,
                   'eval_idx': int(row['eval_idx']),
                   'train_loss_mean': row['train_loss_mean'],
                   'val_loss_mean': row['val_loss_mean'],
                   'test_ur_rmse_pp': row['test_ur_rmse_pp'],
                   'test_lfpr_rmse_pp': row['test_lfpr_rmse_pp'],
                   'test_epop_rmse_pp': row['test_epop_rmse_pp']}
            for n in param_names:
                out[f'p_{n}'] = row[f'p_{n}']
            rows.append(out)
    return pd.DataFrame(rows)


def build_param_stability(top_k_df):
    """Per-param x method: top-5 mean/std/cv/band."""
    rows = []
    for n in param_names:
        lo = PARAM_SPACE[n][2]; hi = PARAM_SPACE[n][3]
        for mid in METHODS:
            sub = top_k_df[top_k_df.method_id == mid][f'p_{n}']
            if len(sub) == 0:
                continue
            mu = float(sub.mean()); sd = float(sub.std(ddof=1))
            cv = abs(sd / mu) if mu != 0 else np.nan
            band = (sub.max() - sub.min()) / (hi - lo)
            rows.append({'param': n, 'method_id': mid, 'prior_low': lo, 'prior_high': hi,
                         'p_min': float(sub.min()), 'p_max': float(sub.max()),
                         'p_mean': mu, 'p_std': sd, 'cv': cv,
                         'normalized_band': float(band)})
    return pd.DataFrame(rows)


def build_param_overlap(top_k_df):
    """For each param and each pair of methods, compute band overlap."""
    rows = []
    for n in param_names:
        for a, b in itertools.combinations(METHODS, 2):
            sa = top_k_df[top_k_df.method_id == a][f'p_{n}']
            sb = top_k_df[top_k_df.method_id == b][f'p_{n}']
            if len(sa) == 0 or len(sb) == 0:
                continue
            amin, amax = sa.min(), sa.max()
            bmin, bmax = sb.min(), sb.max()
            inter = max(0.0, min(amax, bmax) - max(amin, bmin))
            denom = max(amax - amin, bmax - bmin)
            ov = float(inter / denom) if denom > 0 else 1.0
            rows.append({'param': n, 'method_a': a, 'method_b': b,
                         'a_band': float(amax - amin), 'b_band': float(bmax - bmin),
                         'overlap_frac': ov})
    return pd.DataFrame(rows)


def build_best_so_far(df):
    out = {}
    for mid in METHODS:
        sub = df[df.method_id == mid].sort_values('eval_idx')
        if len(sub) == 0:
            continue
        out[mid] = _best_so_far(sub['train_loss_mean'])
    maxlen = max(len(v) for v in out.values())
    padded = {k: np.concatenate([v, np.full(maxlen - len(v), np.nan)]) for k, v in out.items()}
    return pd.DataFrame(padded)


def main():
    df = pd.read_csv(RAW_CSV)
    print(f'Loaded {len(df)} raw evaluations')

    agg = build_aggregates(df)
    agg.to_csv(os.path.join(OUT, 'method_aggregated.csv'), index=False)
    print('Saved method_aggregated.csv')

    top_k = build_top_k_table(df)
    top_k.to_csv(os.path.join(OUT, 'top_k_per_method.csv'), index=False)
    print('Saved top_k_per_method.csv')

    stab = build_param_stability(top_k)
    stab.to_csv(os.path.join(OUT, 'param_stability.csv'), index=False)
    print('Saved param_stability.csv')

    ovl = build_param_overlap(top_k)
    ovl.to_csv(os.path.join(OUT, 'param_overlap.csv'), index=False)
    print('Saved param_overlap.csv')

    bsf = build_best_so_far(df)
    bsf.to_csv(os.path.join(OUT, 'best_so_far.csv'), index=False)
    print('Saved best_so_far.csv')

    print('\n=== SUMMARY AGGREGATES ===')
    print(agg.to_string(index=False))


if __name__ == '__main__':
    main()
