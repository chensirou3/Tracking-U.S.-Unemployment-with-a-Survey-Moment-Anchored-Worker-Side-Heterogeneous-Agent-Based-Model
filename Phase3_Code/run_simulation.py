"""
Phase 3 - First Stable Run
Runs the main model engine and outputs key series.
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation

os.makedirs('Phase3_Output', exist_ok=True)


def run_and_save(scenario='baseline', T=120):
    """Run simulation and save results."""
    print(f"=" * 60)
    print(f"Running {scenario} scenario, T={T} months, N=100,000")
    print(f"=" * 60)

    sim = Simulation(
        population_path='Phase2_Output/population_v1.npz',
        T=T, scenario=scenario, seed=42
    )
    history = sim.run(verbose=True)

    # Convert to arrays for saving
    keys = list(history[0].keys())
    result = {k: np.array([h[k] for h in history]) for k in keys}

    # Save
    np.savez_compressed(f'Phase3_Output/run_{scenario}.npz', **result)
    print(f"\nResults saved to Phase3_Output/run_{scenario}.npz")

    # Print summary statistics
    ur = result['unemployment_rate']
    print(f"\nSummary ({scenario}):")
    print(f"  Unemployment rate: mean={ur.mean():.4f}, "
          f"min={ur.min():.4f}, max={ur.max():.4f}")
    print(f"  LFPR: mean={result['lfpr'].mean():.4f}")
    print(f"  EPOP: mean={result['epop'].mean():.4f}")
    print(f"  Avg E->U rate: {result['eu_rate'].mean():.5f}")
    print(f"  Avg U->E rate: {result['ue_rate'].mean():.4f}")
    print(f"  Avg H2M share: {result['h2m_share'].mean():.4f}")
    print(f"  Avg fragility: {result['avg_fragility'].mean():.4f}")

    return result


if __name__ == '__main__':
    # Run baseline
    baseline = run_and_save('baseline', T=120)

    print("\n")

    # Run recession
    recession = run_and_save('recession', T=120)

    # Save combined output schema
    schema = {
        'variables': {
            'unemployment_rate': {'definition': 'U/(E+U)', 'type': 'core'},
            'lfpr': {'definition': '(E+U)/N_total', 'type': 'layer1'},
            'epop': {'definition': 'E/N_total', 'type': 'layer1'},
            'eu_rate': {'definition': 'E->U transitions / E_prev', 'type': 'layer1'},
            'ue_rate': {'definition': 'U->E transitions / U_prev', 'type': 'layer1'},
            'en_rate': {'definition': 'E->N transitions / E_prev', 'type': 'layer1'},
            'un_rate': {'definition': 'U->N transitions / U_prev', 'type': 'layer1'},
            'nu_rate': {'definition': 'N->U transitions / N_prev', 'type': 'layer1'},
            'avg_income': {'definition': 'mean household income ($k/yr)', 'type': 'layer2'},
            'avg_cash_buffer': {'definition': 'mean buffer (months)', 'type': 'layer2'},
            'avg_search_intensity': {'definition': 'mean search hrs/wk (U only)', 'type': 'layer2'},
            'avg_debt_stress': {'definition': 'mean debt stress [0,1]', 'type': 'layer2'},
            'h2m_share': {'definition': 'fraction Hand-to-Mouth', 'type': 'layer2'},
            'avg_fragility': {'definition': 'mean labor fragility [0,1]', 'type': 'layer2'},
            'avg_unemp_dur': {'definition': 'mean unemployment duration (months)', 'type': 'layer2'},
        },
        'scenarios': ['baseline', 'recession'],
        'T': 120,
        'N': 100000,
    }
    with open('Phase3_Output/output_schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    print("\nOutput schema saved to Phase3_Output/output_schema.json")
    print("\n=== PHASE 3 FIRST STABLE RUN COMPLETE ===")
