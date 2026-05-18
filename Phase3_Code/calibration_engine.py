"""
Phase 6: Global Calibration Engine
LHS search over mechanism parameters, multi-target loss, multi-seed evaluation.
"""
import sys, os, csv, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config

os.makedirs('Phase3_Output/phase6', exist_ok=True)

# ================================================================
# TARGET DATA
# ================================================================
def load_target(fname, col=1):
    data = {}
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                data[row[0][:7]] = float(row[col])
            except (ValueError, IndexError):
                pass
    return data

print("Loading target data...")
tgt_ur = load_target('Phase3_Data/UNRATE.csv')
tgt_lfpr = load_target('Phase3_Data/CIVPART.csv')
tgt_epop = load_target('Phase3_Data/EMRATIO.csv')

# Build aligned target arrays
env_ref = RealEnvironment(data_dir='Phase3_Data')
dates = env_ref.dates
T = env_ref.T
TRAIN_END = 228  # 2001-01 to 2019-12 = 228 months
# Validation: 2020-01 to 2026-02

target_ur = np.array([tgt_ur.get(d, np.nan) for d in dates]) / 100.0
target_lfpr = np.array([tgt_lfpr.get(d, np.nan) for d in dates]) / 100.0
target_epop = np.array([tgt_epop.get(d, np.nan) for d in dates]) / 100.0

# ================================================================
# SEARCH SPACE (from Phase 5 parameter_prior_bands)
# ================================================================
PARAM_SPACE = {
    # (config_key, param_key, low, high)
    'vacancy_rate': ('matching_competition', 'vacancy_rate', 0.02, 0.08),
    'fragility_threshold': ('high_fragility_modifier', 'fragility_threshold', 0.3, 0.7),
    'acceptance_pressure': ('high_fragility_modifier', 'acceptance_pressure_factor', 0.05, 0.30),
    'h2m_resv_discount': ('liquidity_constraint_modifier', 'h2m_resv_wage_discount', 0.10, 0.35),
    'lockin_penalty': ('housing_lockin_modifier', 'lockin_search_penalty', 0.10, 0.50),
    'duration_thresh': ('discouraged_worker', 'duration_threshold_months', 3, 12),
    'exit_jump': ('discouraged_worker', 'exit_jump_factor', 1.0, 4.0),
    'reentry_penalty': ('housing_reentry_friction', 'owner_reentry_penalty', 0.05, 0.50),
    'h2m_mpc_floor': ('effective_mpc_adjustment', 'h2m_mpc_floor', 0.85, 0.99),
    'wealthy_discount': ('effective_mpc_adjustment', 'wealthy_mpc_discount', 0.15, 0.50),
    'emp_adapt_speed': ('state_dependent_expectation', 'employed_adaptation_speed', 0.02, 0.15),
    'unemp_adapt_speed': ('state_dependent_expectation', 'unemployed_adaptation_speed', 0.08, 0.35),
    'pessimism_exit': ('expectation_participation', 'pessimism_exit_boost', 0.05, 0.40),
    'optimism_entry': ('expectation_participation', 'optimism_entry_boost', 0.10, 0.50),
}
N_PARAMS = len(PARAM_SPACE)
param_names = list(PARAM_SPACE.keys())

def make_config(param_vec):
    """Convert parameter vector to mechanism config dict."""
    cfg = default_config()
    for i, name in enumerate(param_names):
        mech_key, param_key, _, _ = PARAM_SPACE[name]
        cfg[mech_key][param_key] = param_vec[i]
    return cfg


# ================================================================
# LOSS FUNCTION
# ================================================================
def compute_loss(history, period='train'):
    """Multi-target hierarchical loss."""
    if period == 'train':
        s, e = 0, TRAIN_END
    else:
        s, e = TRAIN_END, T

    h = history[s:e]
    n = len(h)
    if n == 0:
        return 999.0, {}

    m_ur = np.array([x['unemployment_rate'] for x in h])
    m_lfpr = np.array([x['lfpr'] for x in h])
    m_epop = np.array([x['epop'] for x in h])
    m_eu = np.array([x['eu_rate'] for x in h])
    m_ue = np.array([x['ue_rate'] for x in h])

    t_ur = target_ur[s:e]
    t_lfpr = target_lfpr[s:e]
    t_epop = target_epop[s:e]

    valid_ur = ~np.isnan(t_ur)
    valid_lfpr = ~np.isnan(t_lfpr)
    valid_epop = ~np.isnan(t_epop)

    # Tier 1: UR (weight 5.0)
    loss_ur = np.sqrt(np.mean((m_ur[valid_ur] - t_ur[valid_ur])**2)) if valid_ur.sum() > 0 else 0.5

    # Tier 2: LFPR, EPOP (weight 2.0 each)
    loss_lfpr = np.sqrt(np.mean((m_lfpr[valid_lfpr] - t_lfpr[valid_lfpr])**2)) if valid_lfpr.sum() > 0 else 0.5
    loss_epop = np.sqrt(np.mean((m_epop[valid_epop] - t_epop[valid_epop])**2)) if valid_epop.sum() > 0 else 0.5

    # Tier 2: transition rate targets (approximate BLS benchmarks)
    # BLS: avg EU rate ~1.5%/month, UE rate ~25%/month
    loss_eu = abs(m_eu.mean() - 0.015) * 10  # penalize deviation from ~1.5%
    loss_ue = abs(m_ue.mean() - 0.25) * 5    # penalize deviation from ~25%

    # Tier 3: H2M share target ~30% (Kaplan-Violante)
    m_h2m = np.array([x['h2m_share'] for x in h])
    loss_h2m = abs(m_h2m.mean() - 0.30) * 2

    total = (5.0 * loss_ur + 2.0 * loss_lfpr + 2.0 * loss_epop
             + 1.0 * loss_eu + 1.0 * loss_ue + 0.5 * loss_h2m)

    components = {
        'ur': float(loss_ur), 'lfpr': float(loss_lfpr), 'epop': float(loss_epop),
        'eu': float(loss_eu), 'ue': float(loss_ue), 'h2m': float(loss_h2m),
        'total': float(total),
    }
    return total, components


# ================================================================
# SINGLE EVALUATION
# ================================================================
def evaluate(param_vec, seed=42):
    """Run simulation and compute loss."""
    cfg = make_config(param_vec)
    env = RealEnvironment(data_dir='Phase3_Data')
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    history = sim.run(verbose=False)
    train_loss, train_comp = compute_loss(history, 'train')
    val_loss, val_comp = compute_loss(history, 'validation')
    return train_loss, val_loss, train_comp, val_comp, history
