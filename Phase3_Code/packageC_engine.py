"""
Package C Engine: Heterogeneity Ladder.

Core API:
    run_level(params, active_dims, seed, env) -> history
        Runs a simulation with only `active_dims` kept heterogeneous;
        all other MVP dims flattened to population median/mean.

Level registry:
    CORE_LADDER[level_id] = set of active dims
    LAYER_LADDER[layer_id] = set of active dims
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config
from Phase3_Code.phase7_engine import flatten_heterogeneity, PARAM_MAP

ALL_DIMS = ['income_exp', 'labor_frag', 'liquidity', 'search',
            'housing', 'consumption_rule']

# Nested Core Ladder: each row is the active set (superset of previous)
CORE_LADDER = {
    'L0': set(),
    'L1': {'labor_frag'},
    'L2': {'labor_frag', 'search'},
    'L3': {'labor_frag', 'search', 'income_exp'},
    'L4': {'labor_frag', 'search', 'income_exp', 'liquidity'},
    'L5': {'labor_frag', 'search', 'income_exp', 'liquidity', 'housing'},
    'L6': set(ALL_DIMS),   # = M0 Main
}
CORE_ORDER = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']

# Layer Ladder (conceptual grouping)
LAYER_LADDER = {
    'G1': {'labor_frag', 'search'},                                                   # labor
    'G2': {'labor_frag', 'search', 'liquidity', 'housing'},                           # + constraint
    'G3': {'labor_frag', 'search', 'liquidity', 'housing', 'consumption_rule'},       # + rule
    'G4': set(ALL_DIMS),                                                              # + expectations = full
}
LAYER_ORDER = ['G1', 'G2', 'G3', 'G4']


def build_config(params):
    cfg = default_config()
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val
    return cfg


def run_level(params, active_dims, seed=42, env=None):
    """Run simulation with only `active_dims` kept; rest flattened."""
    if env is None:
        env = RealEnvironment(data_dir='Phase3_Data')
    cfg = build_config(params)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    flatten_set = set(ALL_DIMS) - set(active_dims)
    for dim in flatten_set:
        flatten_heterogeneity(sim.cs, sim.ds, sim.bp, dim)
    return sim.run(verbose=False)


def history_to_dict(hist):
    """Compact numpy-friendly form."""
    keys = ['unemployment_rate', 'lfpr', 'epop', 'eu_rate', 'ue_rate',
            'h2m_share', 'avg_cash_buffer', 'avg_unemp_dur']
    return {k: np.array([h[k] for h in hist]) for k in keys}


def test_window_metrics(arr, target_ur, target_lfpr, target_epop,
                        s=252, e=302):
    """Return test-window metrics as a flat dict."""
    m_ur = arr['unemployment_rate'][s:e]
    m_lfpr = arr['lfpr'][s:e]
    m_epop = arr['epop'][s:e]
    t_ur = target_ur[s:e]; t_lfpr = target_lfpr[s:e]; t_epop = target_epop[s:e]
    vu, vl, ve = ~np.isnan(t_ur), ~np.isnan(t_lfpr), ~np.isnan(t_epop)

    def rmse(a, b, v): return float(np.sqrt(np.mean((a[v]-b[v])**2))) if v.sum() > 1 else np.nan

    return {
        'ur_rmse_pp': rmse(m_ur, t_ur, vu) * 100,
        'ur_mae_pp': float(np.mean(np.abs(m_ur[vu]-t_ur[vu]))) * 100 if vu.sum() else np.nan,
        'ur_corr': float(np.corrcoef(m_ur[vu], t_ur[vu])[0, 1]) if vu.sum() > 2 else np.nan,
        'lfpr_rmse_pp': rmse(m_lfpr, t_lfpr, vl) * 100,
        'epop_rmse_pp': rmse(m_epop, t_epop, ve) * 100,
        'eu_mean': float(arr['eu_rate'].mean()),
        'ue_mean': float(arr['ue_rate'].mean()),
        'h2m_share': float(arr['h2m_share'].mean()),
        'avg_buffer': float(arr['avg_cash_buffer'].mean()),
        'avg_dur': float(arr['avg_unemp_dur'].mean()),
    }


def train_loss(arr, target_ur, target_lfpr, target_epop,
               s=36, e=204):
    """Phase 7/A consistent training loss."""
    m_ur = arr['unemployment_rate'][s:e]
    m_lfpr = arr['lfpr'][s:e]
    m_epop = arr['epop'][s:e]
    t_ur = target_ur[s:e]; t_lfpr = target_lfpr[s:e]; t_epop = target_epop[s:e]
    vu, vl, ve = ~np.isnan(t_ur), ~np.isnan(t_lfpr), ~np.isnan(t_epop)

    def rmse(a, b, v): return float(np.sqrt(np.mean((a[v]-b[v])**2))) if v.sum() > 1 else 0.5
    lu = rmse(m_ur, t_ur, vu); ll = rmse(m_lfpr, t_lfpr, vl); le = rmse(m_epop, t_epop, ve)
    leu = abs(arr['eu_rate'].mean() - 0.015) * 10
    lue = abs(arr['ue_rate'].mean() - 0.25) * 5
    lh = abs(arr['h2m_share'].mean() - 0.30) * 2
    lb = abs(arr['avg_cash_buffer'].mean() - 3.5) * 0.3
    ld = abs(arr['avg_unemp_dur'].mean() - 5) * 0.3
    total = 5*lu + 2*ll + 2*le + 1*leu + 1*lue + 0.5*lh + lb + ld
    return float(total)
