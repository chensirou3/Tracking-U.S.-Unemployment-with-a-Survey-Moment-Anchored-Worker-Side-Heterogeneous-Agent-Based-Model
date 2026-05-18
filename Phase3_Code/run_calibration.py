"""
Phase 6: Run global calibration search.
Round 1: Latin Hypercube Sampling (150 points)
Round 2: Local refinement around top candidates
Round 3: Multi-seed stability check on finalists
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.calibration_engine import (
    PARAM_SPACE, param_names, N_PARAMS, evaluate, make_config,
    compute_loss, RealEnvironment, Simulation, TRAIN_END, T
)

os.makedirs('Phase3_Output/phase6', exist_ok=True)

def latin_hypercube(n_samples, n_dims, rng):
    """Generate LHS samples in [0,1]^n_dims."""
    result = np.zeros((n_samples, n_dims))
    for j in range(n_dims):
        perm = rng.permutation(n_samples)
        for i in range(n_samples):
            result[perm[i], j] = (i + rng.random()) / n_samples
    return result

def scale_params(unit_vec):
    """Scale [0,1] vector to parameter space."""
    scaled = np.zeros(N_PARAMS)
    for i, name in enumerate(param_names):
        _, _, lo, hi = PARAM_SPACE[name]
        scaled[i] = lo + unit_vec[i] * (hi - lo)
    return scaled

# ================================================================
# ROUND 1: LHS SEARCH
# ================================================================
N_LHS = 150
rng = np.random.default_rng(123)

print("=" * 60)
print(f"ROUND 1: Latin Hypercube Search ({N_LHS} samples)")
print("=" * 60)

lhs_samples = latin_hypercube(N_LHS, N_PARAMS, rng)
results = []

t0 = time.time()
for i in range(N_LHS):
    pvec = scale_params(lhs_samples[i])
    try:
        train_loss, val_loss, tc, vc, _ = evaluate(pvec, seed=42)
        results.append({
            'idx': i, 'params': pvec.tolist(),
            'train_loss': train_loss, 'val_loss': val_loss,
            'train_comp': tc, 'val_comp': vc,
        })
        if (i+1) % 10 == 0:
            elapsed = time.time() - t0
            best_so_far = min(r['train_loss'] for r in results)
            print(f"  [{i+1}/{N_LHS}] {elapsed:.0f}s, best_train={best_so_far:.4f}, "
                  f"last_train={train_loss:.4f}")
    except Exception as e:
        print(f"  [{i+1}] FAILED: {e}")

results.sort(key=lambda x: x['train_loss'])
print(f"\nRound 1 complete: {len(results)} successful, best train_loss={results[0]['train_loss']:.4f}")

# ================================================================
# ROUND 2: LOCAL REFINEMENT around top 15
# ================================================================
print("\n" + "=" * 60)
print("ROUND 2: Local Refinement (top 15 x 10 perturbations)")
print("=" * 60)

top_n = min(15, len(results))
n_perturb = 10
round2_results = list(results[:top_n])  # keep originals

for rank, base in enumerate(results[:top_n]):
    base_vec = np.array(base['params'])
    for j in range(n_perturb):
        # Small gaussian perturbation (5% of range)
        noise = np.zeros(N_PARAMS)
        for k, name in enumerate(param_names):
            _, _, lo, hi = PARAM_SPACE[name]
            noise[k] = rng.normal(0, 0.05 * (hi - lo))
        pvec = np.clip(base_vec + noise,
                       [PARAM_SPACE[n][2] for n in param_names],
                       [PARAM_SPACE[n][3] for n in param_names])
        try:
            tl, vl, tc, vc, _ = evaluate(pvec, seed=42)
            round2_results.append({
                'idx': f'R2_{rank}_{j}', 'params': pvec.tolist(),
                'train_loss': tl, 'val_loss': vl,
                'train_comp': tc, 'val_comp': vc,
            })
        except:
            pass

round2_results.sort(key=lambda x: x['train_loss'])
print(f"Round 2 complete: {len(round2_results)} total, best={round2_results[0]['train_loss']:.4f}")

# ================================================================
# ROUND 3: MULTI-SEED STABILITY (top 20 x 3 seeds)
# ================================================================
print("\n" + "=" * 60)
print("ROUND 3: Multi-Seed Stability (top 20 x 3 seeds)")
print("=" * 60)

seeds = [42, 137, 2024]
top_20 = round2_results[:20]
final_results = []

for rank, cand in enumerate(top_20):
    pvec = np.array(cand['params'])
    train_losses, val_losses = [], []
    all_tc, all_vc = [], []
    for seed in seeds:
        try:
            tl, vl, tc, vc, _ = evaluate(pvec, seed=seed)
            train_losses.append(tl)
            val_losses.append(vl)
            all_tc.append(tc)
            all_vc.append(vc)
        except:
            train_losses.append(999)
            val_losses.append(999)

    final_results.append({
        'rank': rank,
        'params': {n: pvec[i] for i, n in enumerate(param_names)},
        'train_mean': np.mean(train_losses), 'train_std': np.std(train_losses),
        'val_mean': np.mean(val_losses), 'val_std': np.std(val_losses),
        'train_comp_avg': {k: np.mean([tc[k] for tc in all_tc]) for k in all_tc[0]} if all_tc else {},
        'val_comp_avg': {k: np.mean([vc[k] for vc in all_vc]) for k in all_vc[0]} if all_vc else {},
        'stable': np.std(train_losses) < 0.3 * np.mean(train_losses),
    })
    print(f"  Rank {rank}: train={np.mean(train_losses):.4f}+/-{np.std(train_losses):.4f}, "
          f"val={np.mean(val_losses):.4f}+/-{np.std(val_losses):.4f}, "
          f"stable={'YES' if final_results[-1]['stable'] else 'NO'}")

# Save all results
with open('Phase3_Output/phase6/calibration_results.json', 'w') as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved. Top 3:")
for r in final_results[:3]:
    print(f"  Rank {r['rank']}: train={r['train_mean']:.4f}, val={r['val_mean']:.4f}")
