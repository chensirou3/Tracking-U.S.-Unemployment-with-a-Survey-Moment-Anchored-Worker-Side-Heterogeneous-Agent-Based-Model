"""
Package A Engine: Training Window Sensitivity

Key optimization: a given parameter vector produces the same 302-month history
regardless of which window we evaluate on. So for LHS calibration, we simulate
ONCE per param vector, then compute loss on any split's train/val/test window.

This makes 10 splits × 60 LHS = 600 calibration runs, not 6000.
"""
import sys, os, json, time, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config, all_off_config
from Phase3_Code.calibration_engine import PARAM_SPACE, N_PARAMS, param_names, make_config
from Phase3_Code.phase7_engine import (
    flatten_heterogeneity, compute_window_metrics, load_candidates
)

os.makedirs('Phase3_Output/packageA', exist_ok=True)


# ============================================================
# SPLIT REGISTRY
# ============================================================
SPLITS = {
    'S0': {'train': (36, 204),  'val': (204, 252), 'test': (252, 302), 'type': 'baseline'},
    'R1': {'train': (36, 156),  'val': (156, 192), 'test': (192, 242), 'type': 'rolling'},
    'R2': {'train': (60, 180),  'val': (180, 216), 'test': (216, 266), 'type': 'rolling'},
    'R3': {'train': (84, 204),  'val': (204, 240), 'test': (240, 290), 'type': 'rolling'},
    'R4': {'train': (108, 228), 'val': (228, 252), 'test': (252, 302), 'type': 'rolling'},
    'E1': {'train': (36, 156),  'val': (216, 252), 'test': (252, 302), 'type': 'expanding'},
    'E2': {'train': (36, 180),  'val': (216, 252), 'test': (252, 302), 'type': 'expanding'},
    'E3': {'train': (36, 204),  'val': (216, 252), 'test': (252, 302), 'type': 'expanding'},
    'E4': {'train': (36, 228),  'val': (228, 252), 'test': (252, 302), 'type': 'expanding'},
    'E5': {'train': (36, 252),  'val': (252, 252), 'test': (252, 302), 'type': 'expanding'},
}


# ============================================================
# TARGET DATA (shared)
# ============================================================
def load_target(fname):
    data = {}
    with open(fname, 'r') as f:
        reader = csv.reader(f); next(reader)
        for row in reader:
            try:
                data[row[0][:7]] = float(row[1])
            except (ValueError, IndexError):
                pass
    return data


_env_cache = None
_targets_cache = None

def get_env_targets():
    global _env_cache, _targets_cache
    if _env_cache is None:
        _env_cache = RealEnvironment(data_dir='Phase3_Data')
        ur = load_target('Phase3_Data/UNRATE.csv')
        lfpr = load_target('Phase3_Data/CIVPART.csv')
        epop = load_target('Phase3_Data/EMRATIO.csv')
        T = _env_cache.T
        t_ur = np.array([ur.get(d, np.nan) for d in _env_cache.dates]) / 100
        t_lfpr = np.array([lfpr.get(d, np.nan) for d in _env_cache.dates]) / 100
        t_epop = np.array([epop.get(d, np.nan) for d in _env_cache.dates]) / 100
        _targets_cache = (t_ur, t_lfpr, t_epop)
    return _env_cache, _targets_cache


# ============================================================
# LOSS ON ARBITRARY WINDOW
# ============================================================
def compute_loss_on_window(history, s, e, w_ur=5.0):
    """Compute Phase 7-style loss on arbitrary window [s, e)."""
    _, (t_ur, t_lfpr, t_epop) = get_env_targets()
    h = history[s:e]
    if len(h) == 0: return 999.0, {}

    m_ur = np.array([x['unemployment_rate'] for x in h])
    m_lfpr = np.array([x['lfpr'] for x in h])
    m_epop = np.array([x['epop'] for x in h])
    m_eu = np.array([x['eu_rate'] for x in h])
    m_ue = np.array([x['ue_rate'] for x in h])
    m_h2m = np.array([x['h2m_share'] for x in h])

    tu, tl, te = t_ur[s:e], t_lfpr[s:e], t_epop[s:e]
    vu, vl, ve = ~np.isnan(tu), ~np.isnan(tl), ~np.isnan(te)

    def r(a, b, v): return np.sqrt(np.mean((a[v]-b[v])**2)) if v.sum() > 0 else 0.5
    lu = r(m_ur, tu, vu); ll = r(m_lfpr, tl, vl); le = r(m_epop, te, ve)
    leu = abs(m_eu.mean() - 0.015) * 10
    lue = abs(m_ue.mean() - 0.25) * 5
    lh = abs(m_h2m.mean() - 0.30) * 2

    total = w_ur*lu + 2*ll + 2*le + 1*leu + 1*lue + 0.5*lh
    return float(total), {'ur': float(lu), 'lfpr': float(ll), 'epop': float(le),
                          'eu': float(leu), 'ue': float(lue), 'h2m': float(lh)}


# ============================================================
# LHS SAMPLING (around Phase 6 baseline with ±20% perturbation)
# ============================================================
def lhs_samples(n, seed=42, perturb=0.20):
    """Latin Hypercube around Phase 6 baseline point."""
    versions = load_candidates()
    p6 = versions['baseline']['params']
    rng = np.random.default_rng(seed)

    center = np.array([p6[name] for name in param_names])
    lows_abs = np.array([PARAM_SPACE[n][2] for n in param_names])
    highs_abs = np.array([PARAM_SPACE[n][3] for n in param_names])

    # perturb range = max(perturb * center, 0.01) but clipped to prior
    span = np.maximum(perturb * center, 0.02)
    lows = np.maximum(center - span, lows_abs)
    highs = np.minimum(center + span, highs_abs)

    # LHS in unit cube
    cuts = np.linspace(0, 1, n + 1)
    u = rng.uniform(cuts[:-1], cuts[1:], size=(N_PARAMS, n)).T
    for j in range(N_PARAMS):
        rng.shuffle(u[:, j])

    # Scale to [lows, highs]
    samples = lows + u * (highs - lows)
    # Prepend center as sample 0
    samples = np.vstack([center.reshape(1, -1), samples])
    return samples
