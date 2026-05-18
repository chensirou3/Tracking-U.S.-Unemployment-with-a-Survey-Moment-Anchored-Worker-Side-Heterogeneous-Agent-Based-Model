"""
Phase 7: Real-Data Main Experiment Engine
- Formal 4-window evaluation (Init/Train/Val/OOS)
- Tier 1/2/3 target system
- Heterogeneity flattening for ablation
- Multi-seed support
"""
import sys, os, json, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config
from Phase3_Code.constants import (
    CS_EMPLOYMENT, CS_LIQUIDITY_TYPE, CS_HOUSING_STATUS, CS_CONSUMPTION_TYPE,
    DS_INCOME_EXP, DS_INCOME_UNC, DS_LABOR_FRAG, DS_CASH_BUFFER,
    DS_SEARCH_INT, DS_MOBILITY_FRIC, BP_MPC_POS, BP_MPC_NEG,
    BP_RESV_WAGE, BP_FLEXIBILITY, LIQ_BUFFER, HSG_RENT_STB,
    CON_SMOOTHER,
)

# ============================================================
# TIME WINDOWS
# ============================================================
INIT_END = 36    # 2004-01
TRAIN_END = 204  # 2018-01
VAL_END = 252    # 2022-01
OOS_END = 302    # 2026-03

WINDOWS = {
    'init':  (0, INIT_END),
    'train': (INIT_END, TRAIN_END),
    'val':   (TRAIN_END, VAL_END),
    'oos':   (VAL_END, OOS_END),
}

# ============================================================
# TARGET DATA
# ============================================================
def _load_fred(fname):
    data = {}
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                data[row[0][:7]] = float(row[1])
            except (ValueError, IndexError):
                pass
    return data

def get_targets():
    env = RealEnvironment(data_dir='Phase3_Data')
    ur = _load_fred('Phase3_Data/UNRATE.csv')
    lfpr = _load_fred('Phase3_Data/CIVPART.csv')
    epop = _load_fred('Phase3_Data/EMRATIO.csv')
    T = env.T
    target_ur = np.array([ur.get(d, np.nan) for d in env.dates]) / 100
    target_lfpr = np.array([lfpr.get(d, np.nan) for d in env.dates]) / 100
    target_epop = np.array([epop.get(d, np.nan) for d in env.dates]) / 100
    return env, target_ur, target_lfpr, target_epop


# ============================================================
# LOSS FUNCTION (3-tier)
# ============================================================
def compute_window_metrics(history, target_ur, target_lfpr, target_epop, window='oos'):
    s, e = WINDOWS[window]
    h = history[s:e]
    n = len(h)
    if n == 0:
        return {}

    m_ur = np.array([x['unemployment_rate'] for x in h])
    m_lfpr = np.array([x['lfpr'] for x in h])
    m_epop = np.array([x['epop'] for x in h])
    m_eu = np.array([x['eu_rate'] for x in h])
    m_ue = np.array([x['ue_rate'] for x in h])
    m_h2m = np.array([x['h2m_share'] for x in h])
    m_buf = np.array([x['avg_cash_buffer'] for x in h])
    m_dur = np.array([x['avg_unemp_dur'] for x in h])

    t_ur = target_ur[s:e]
    t_lfpr = target_lfpr[s:e]
    t_epop = target_epop[s:e]

    def rmse(a, b):
        v = ~np.isnan(b)
        if v.sum() < 2: return np.nan
        return float(np.sqrt(np.mean((a[v] - b[v])**2)))

    def corr(a, b):
        v = ~np.isnan(b)
        if v.sum() < 2: return np.nan
        return float(np.corrcoef(a[v], b[v])[0,1])

    metrics = {
        'window': window, 'n_months': n,
        'ur_rmse': rmse(m_ur, t_ur),
        'ur_mae': float(np.mean(np.abs(m_ur - t_ur)[~np.isnan(t_ur)])) if (~np.isnan(t_ur)).sum() > 0 else np.nan,
        'ur_corr': corr(m_ur, t_ur),
        'lfpr_rmse': rmse(m_lfpr, t_lfpr),
        'epop_rmse': rmse(m_epop, t_epop),
        'eu_mean': float(m_eu.mean()), 'eu_target': 0.015,
        'ue_mean': float(m_ue.mean()), 'ue_target': 0.25,
        'h2m_mean': float(m_h2m.mean()), 'h2m_target': 0.30,
        'buf_mean': float(m_buf.mean()), 'buf_target': 3.5,
        'dur_mean': float(m_dur.mean()), 'dur_target': 5.0,
        'ur_mean': float(m_ur.mean()), 'lfpr_mean': float(m_lfpr.mean()),
    }
    # Composite tier 1+2 loss
    metrics['tier1_loss'] = 5.0 * (metrics['ur_rmse'] if not np.isnan(metrics['ur_rmse']) else 0.5)
    metrics['tier2_loss'] = (2.0 * (metrics['lfpr_rmse'] if not np.isnan(metrics['lfpr_rmse']) else 0.5)
                            + 2.0 * (metrics['epop_rmse'] if not np.isnan(metrics['epop_rmse']) else 0.5)
                            + 1.0 * abs(metrics['eu_mean'] - 0.015) * 10
                            + 1.0 * abs(metrics['ue_mean'] - 0.25) * 5)
    metrics['total_loss'] = metrics['tier1_loss'] + metrics['tier2_loss']
    return metrics



# ============================================================
# HETEROGENEITY FLATTENING (for real-data ablation)
# ============================================================
def flatten_heterogeneity(cs, ds, bp, dim):
    """Replace a heterogeneity dimension with population median/mode."""
    if dim == 'none':
        return

    if dim == 'income_exp':
        ds[:, DS_INCOME_EXP] = np.median(ds[:, DS_INCOME_EXP])
        ds[:, DS_INCOME_UNC] = np.median(ds[:, DS_INCOME_UNC])

    elif dim == 'labor_frag':
        ds[:, DS_LABOR_FRAG] = np.median(ds[:, DS_LABOR_FRAG])

    elif dim == 'liquidity':
        cs[:, CS_LIQUIDITY_TYPE] = LIQ_BUFFER
        ds[:, DS_CASH_BUFFER] = np.median(ds[:, DS_CASH_BUFFER])

    elif dim == 'search':
        ds[:, DS_SEARCH_INT] = np.mean(ds[:, DS_SEARCH_INT])
        bp[:, BP_RESV_WAGE] = np.mean(bp[:, BP_RESV_WAGE])
        bp[:, BP_FLEXIBILITY] = np.mean(bp[:, BP_FLEXIBILITY])

    elif dim == 'housing':
        cs[:, CS_HOUSING_STATUS] = HSG_RENT_STB
        ds[:, DS_MOBILITY_FRIC] = np.median(ds[:, DS_MOBILITY_FRIC])

    elif dim == 'consumption_rule':
        cs[:, CS_CONSUMPTION_TYPE] = CON_SMOOTHER
        bp[:, BP_MPC_POS] = np.mean(bp[:, BP_MPC_POS])
        bp[:, BP_MPC_NEG] = np.mean(bp[:, BP_MPC_NEG])


# ============================================================
# PARAM SPACE MAP
# ============================================================
PARAM_MAP = {
    'vacancy_rate': ('matching_competition', 'vacancy_rate'),
    'fragility_threshold': ('high_fragility_modifier', 'fragility_threshold'),
    'acceptance_pressure': ('high_fragility_modifier', 'acceptance_pressure_factor'),
    'h2m_resv_discount': ('liquidity_constraint_modifier', 'h2m_resv_wage_discount'),
    'lockin_penalty': ('housing_lockin_modifier', 'lockin_search_penalty'),
    'duration_thresh': ('discouraged_worker', 'duration_threshold_months'),
    'exit_jump': ('discouraged_worker', 'exit_jump_factor'),
    'reentry_penalty': ('housing_reentry_friction', 'owner_reentry_penalty'),
    'h2m_mpc_floor': ('effective_mpc_adjustment', 'h2m_mpc_floor'),
    'wealthy_discount': ('effective_mpc_adjustment', 'wealthy_mpc_discount'),
    'emp_adapt_speed': ('state_dependent_expectation', 'employed_adaptation_speed'),
    'unemp_adapt_speed': ('state_dependent_expectation', 'unemployed_adaptation_speed'),
    'pessimism_exit': ('expectation_participation', 'pessimism_exit_boost'),
    'optimism_entry': ('expectation_participation', 'optimism_entry_boost'),
}


# ============================================================
# RUN SINGLE VERSION
# ============================================================
def run_version(params, seed=42, flatten_dim='none', env=None):
    """Run simulation with params and optional heterogeneity flattening."""
    if env is None:
        env = RealEnvironment(data_dir='Phase3_Data')

    cfg = default_config()
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val

    sim = Simulation(config=cfg, seed=seed, env_override=env)
    if flatten_dim != 'none':
        flatten_heterogeneity(sim.cs, sim.ds, sim.bp, flatten_dim)
    return sim.run(verbose=False)


# ============================================================
# LOAD CANDIDATES
# ============================================================
def load_candidates():
    """Load 3 candidate versions from Phase 6."""
    versions = {}
    for name in ['conservative', 'baseline', 'aggressive']:
        with open(f'Phase3_Output/phase6/candidate_{name}.json', 'r') as f:
            versions[name] = json.load(f)
    return versions
