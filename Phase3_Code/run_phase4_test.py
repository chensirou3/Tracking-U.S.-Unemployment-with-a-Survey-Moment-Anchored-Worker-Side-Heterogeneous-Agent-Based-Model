"""
Phase 4 - Full mechanism test: all ON vs all OFF + ablation
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.mechanism_config import default_config, all_off_config, ablation_config

os.makedirs('Phase3_Output', exist_ok=True)

SCENARIO = 'recession'
T = 120

def run_one(label, cfg):
    print(f"\n--- {label} ---")
    sim = Simulation(T=T, scenario=SCENARIO, config=cfg)
    h = sim.run(verbose=False)
    ur = [x['unemployment_rate'] for x in h]
    lfpr = [x['lfpr'] for x in h]
    h2m = [x['h2m_share'] for x in h]
    buf = [x['avg_cash_buffer'] for x in h]
    frag = [x['avg_fragility'] for x in h]
    print(f"  UR: mean={np.mean(ur):.4f}, peak={np.max(ur):.4f}")
    print(f"  LFPR: mean={np.mean(lfpr):.4f}")
    print(f"  H2M: mean={np.mean(h2m):.4f}")
    print(f"  Buffer: mean={np.mean(buf):.2f}")
    print(f"  Fragility: mean={np.mean(frag):.4f}")
    return {
        'ur_mean': np.mean(ur), 'ur_peak': np.max(ur), 'ur_end': np.mean(ur[-12:]),
        'lfpr_mean': np.mean(lfpr), 'h2m_mean': np.mean(h2m),
        'buf_mean': np.mean(buf), 'frag_mean': np.mean(frag),
    }

# Run all-on and all-off
results = {}
print("=" * 60)
print("PHASE 4 MECHANISM TEST")
print("=" * 60)

results['all_on'] = run_one('ALL MECHANISMS ON', default_config())
results['all_off'] = run_one('ALL MECHANISMS OFF', all_off_config())

# Ablation: disable one mechanism at a time
mechanisms = [
    'high_fragility_modifier', 'liquidity_constraint_modifier',
    'housing_lockin_modifier', 'fragility_x_liquidity_interaction',
    'matching_competition', 'discouraged_worker',
    'housing_reentry_friction', 'expectation_participation',
    'effective_mpc_adjustment', 'consumption_sequencing',
    'buffer_consumption_ordering',
    'state_dependent_expectation', 'experience_dependent_expectation',
]

print("\n" + "=" * 60)
print("ABLATION TEST (disable one mechanism at a time)")
print("=" * 60)

for mech in mechanisms:
    cfg = ablation_config(mech)
    results[f'no_{mech}'] = run_one(f'Without {mech}', cfg)

# Summary comparison table
print("\n" + "=" * 60)
print("ABLATION SUMMARY TABLE")
print("=" * 60)
base = results['all_on']
print(f"{'Config':<45s} {'UR_mean':>8s} {'UR_peak':>8s} {'LFPR':>8s} {'H2M':>8s} {'dUR':>8s}")
print("-" * 85)
for key, r in results.items():
    dur = r['ur_mean'] - base['ur_mean']
    print(f"{key:<45s} {r['ur_mean']:8.4f} {r['ur_peak']:8.4f} "
          f"{r['lfpr_mean']:8.4f} {r['h2m_mean']:8.4f} {dur:+8.4f}")

# Save results
with open('Phase3_Output/ablation_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to Phase3_Output/ablation_results.json")
print("\n=== PHASE 4 MECHANISM TEST COMPLETE ===")
