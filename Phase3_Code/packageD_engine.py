"""
Package D engine: Agent count sensitivity.

Two population modes:
    subsample : load 100k base pop, random-subsample to N with seed
    regenerate: call Phase 2 generate_population(N, seed)

Four model flavors: M0 / D1 / D2 / D3 (matches Phase 8 derived.py).

Runtime and memory are measured per run via perf_counter + psutil.
"""
import os, sys, time, gc
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config, all_off_config
from Phase3_Code.phase7_engine import flatten_heterogeneity, PARAM_MAP
from Phase3_Code.phase8_derived import flatten_all_heterogeneity
from Phase2_Code.population_init_engine import generate_population

try:
    import psutil
    PROC = psutil.Process(os.getpid())
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    PROC = None

SEEDS = [42, 137, 2024, 7, 11, 23, 58, 91, 314, 777]
GRID = [5_000, 10_000, 25_000, 50_000, 100_000, 200_000, 300_000]
MODELS = ['M0', 'D1', 'D2', 'D3']
MODES = ['subsample', 'regenerate']

_BASE_POP_CACHE = None


def load_base_pop():
    global _BASE_POP_CACHE
    if _BASE_POP_CACHE is None:
        pop = np.load('Phase2_Output/population_v1.npz')
        _BASE_POP_CACHE = {k: pop[k].copy() for k in pop.files}
    return _BASE_POP_CACHE


def make_pop_subsample(N, seed):
    base = load_base_pop()
    rng = np.random.default_rng(seed)
    total = base['static_traits'].shape[0]
    n_eff = min(N, total)
    idx = rng.choice(total, size=n_eff, replace=False)
    idx.sort()
    return {k: v[idx].copy() for k, v in base.items()}


def make_pop_regenerate(N, seed):
    return generate_population(N=N, seed=seed)


def _override_sim_pop(sim, pop):
    sim.st = pop['static_traits'].copy()
    sim.cs = pop['category_states'].copy()
    sim.ds = pop['dynamic_states'].copy()
    sim.bp = pop['behavior_params'].copy()
    sim.N = sim.st.shape[0]
    from Phase3_Code.constants import DS_HH_INCOME
    sim.prev_income = sim.ds[:, DS_HH_INCOME].copy()


def _build_cfg(params, model):
    if model == 'D2':
        cfg = all_off_config()
        cfg['matching_competition']['enabled'] = True
        if 'vacancy_rate' in params:
            cfg['matching_competition']['vacancy_rate'] = params['vacancy_rate']
        return cfg
    cfg = default_config()
    for pname, val in params.items():
        if pname in PARAM_MAP:
            mk, pk = PARAM_MAP[pname]
            cfg[mk][pk] = val
    if model == 'D3':
        for m in ['effective_mpc_adjustment', 'consumption_sequencing',
                  'buffer_consumption_ordering', 'liquidity_constraint_modifier']:
            if m in cfg:
                cfg[m]['enabled'] = False
    return cfg


def _apply_model_flatten(sim, model):
    if model in ('D1', 'D2'):
        flatten_all_heterogeneity(sim.cs, sim.ds, sim.bp)


def run_sim(params, N, model, seed, mode, env):
    """Returns (history_dict, runtime_s, peak_mem_mb)."""
    assert model in MODELS and mode in MODES
    gc.collect()
    if HAS_PSUTIL:
        rss0 = PROC.memory_info().rss

    pop = make_pop_subsample(N, seed) if mode == 'subsample' else make_pop_regenerate(N, seed)
    cfg = _build_cfg(params, model)
    sim = Simulation(config=cfg, seed=seed, env_override=env)
    _override_sim_pop(sim, pop)
    _apply_model_flatten(sim, model)

    t0 = time.perf_counter()
    hist = sim.run(verbose=False)
    runtime = time.perf_counter() - t0

    if HAS_PSUTIL:
        rss1 = PROC.memory_info().rss
        peak_mem = max((rss1 - rss0) / 1024 / 1024, 0.0)
    else:
        peak_mem = float('nan')

    arr = history_to_dict(hist)
    del sim, pop, hist
    gc.collect()
    return arr, runtime, peak_mem


def history_to_dict(hist):
    keys = ['unemployment_rate', 'lfpr', 'epop', 'eu_rate', 'ue_rate',
            'h2m_share', 'avg_cash_buffer', 'avg_unemp_dur']
    return {k: np.array([h[k] for h in hist]) for k in keys}


def test_window_metrics(arr, t_ur, t_lfpr, t_epop, s=252, e=302):
    m_ur = arr['unemployment_rate'][s:e]
    m_lfpr = arr['lfpr'][s:e]
    m_epop = arr['epop'][s:e]
    t_u, t_l, t_e = t_ur[s:e], t_lfpr[s:e], t_epop[s:e]
    vu, vl, ve = ~np.isnan(t_u), ~np.isnan(t_l), ~np.isnan(t_e)

    def rmse(a, b, v): return float(np.sqrt(np.mean((a[v]-b[v])**2))) if v.sum() > 1 else np.nan

    return {
        'ur_rmse_pp': rmse(m_ur, t_u, vu) * 100,
        'ur_mae_pp': float(np.mean(np.abs(m_ur[vu]-t_u[vu]))) * 100 if vu.sum() else np.nan,
        'ur_corr': float(np.corrcoef(m_ur[vu], t_u[vu])[0, 1]) if vu.sum() > 2 else np.nan,
        'lfpr_rmse_pp': rmse(m_lfpr, t_l, vl) * 100,
        'epop_rmse_pp': rmse(m_epop, t_e, ve) * 100,
        'eu_mean': float(arr['eu_rate'].mean()),
        'ue_mean': float(arr['ue_rate'].mean()),
        'h2m_share': float(arr['h2m_share'].mean()),
        'avg_buffer': float(arr['avg_cash_buffer'].mean()),
        'avg_dur': float(arr['avg_unemp_dur'].mean()),
    }
