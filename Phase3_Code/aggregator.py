"""
Module G: Aggregator
Computes aggregate statistics from individual agent states each month.
"""
import numpy as np
from Phase3_Code.constants import *


def compute_aggregates(cs, ds, bp, transitions):
    """
    Compute all aggregate output variables for the current period.

    Returns:
        dict of aggregate metrics
    """
    N = cs.shape[0]
    emp = cs[:, CS_EMPLOYMENT]

    n_e = (emp == EMP_E).sum()
    n_u = (emp == EMP_U).sum()
    n_n = (emp == EMP_N).sum()
    n_lf = n_e + n_u  # labor force

    # --- Core: Unemployment Rate ---
    unemployment_rate = n_u / max(n_lf, 1)

    # --- Layer 1: Labor Market Indicators ---
    lfpr = n_lf / N  # labor force participation rate
    epop = n_e / N    # employment-population ratio

    # Transition rates (as fraction of origin state)
    prev_e = n_e + transitions.get('E_to_U', 0) + transitions.get('E_to_N', 0)
    prev_u = n_u + transitions.get('U_to_E', 0) + transitions.get('U_to_N', 0) - transitions.get('E_to_U', 0)

    eu_rate = transitions.get('E_to_U', 0) / max(prev_e, 1)
    ue_rate = transitions.get('U_to_E', 0) / max(max(prev_u, 1), 1)
    en_rate = transitions.get('E_to_N', 0) / max(prev_e, 1)
    nu_rate = transitions.get('N_to_U', 0) / max(n_n + transitions.get('N_to_U', 0), 1)
    un_rate = transitions.get('U_to_N', 0) / max(max(prev_u, 1), 1)

    # --- Layer 2: Household Support Indicators ---
    income = ds[:, DS_HH_INCOME]
    cash_buf = ds[:, DS_CASH_BUFFER]
    search_int = ds[:, DS_SEARCH_INT]
    debt_stress = ds[:, DS_DEBT_STRESS]
    liq = cs[:, CS_LIQUIDITY_TYPE]
    frag = ds[:, DS_LABOR_FRAG]

    avg_income = income.mean()
    avg_cash_buffer = cash_buf.mean()
    avg_search_intensity = search_int[emp == EMP_U].mean() if n_u > 0 else 0.0
    avg_debt_stress = debt_stress.mean()
    h2m_share = (liq == LIQ_H2M).mean()
    avg_fragility = frag.mean()
    avg_mpc_pos = bp[:, BP_MPC_POS].mean()

    # Average unemployment duration
    avg_unemp_dur = ds[emp == EMP_U, DS_UNEMP_DUR].mean() if n_u > 0 else 0.0

    return {
        # Core
        'unemployment_rate': unemployment_rate,
        # Layer 1: Labor
        'lfpr': lfpr,
        'epop': epop,
        'eu_rate': eu_rate,
        'ue_rate': ue_rate,
        'en_rate': en_rate,
        'un_rate': un_rate,
        'nu_rate': nu_rate,
        # Layer 2: Household
        'avg_income': avg_income,
        'avg_cash_buffer': avg_cash_buffer,
        'avg_search_intensity': avg_search_intensity,
        'avg_debt_stress': avg_debt_stress,
        'h2m_share': h2m_share,
        'avg_fragility': avg_fragility,
        'avg_unemp_dur': avg_unemp_dur,
        # Counts
        'n_employed': int(n_e),
        'n_unemployed': int(n_u),
        'n_nilf': int(n_n),
        # Transitions
        **{f'trans_{k}': int(v) for k, v in transitions.items()},
    }
