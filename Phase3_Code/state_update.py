"""
Module F: State Update Engine
Applies all block outputs to update agent matrices.
"""
import numpy as np
from Phase3_Code.constants import *


def update_labor_states(cs, ds, bp, exit_to_n, enter_from_n,
                        is_separated, accepts, env, rng):
    """
    Apply labor transitions and update related states.

    Transition priority:
    1. Separations: E -> U
    2. Acceptances: U -> E
    3. Exits: E/U -> N
    4. Entries: N -> U
    """
    emp = cs[:, CS_EMPLOYMENT].copy()
    N = len(emp)

    # Track transitions for aggregation
    transitions = {
        'E_to_U': 0, 'U_to_E': 0, 'E_to_N': 0,
        'U_to_N': 0, 'N_to_U': 0, 'N_to_E': 0,
    }

    # 1. Separations: E -> U
    sep_mask = is_separated & (emp == EMP_E)
    transitions['E_to_U'] = sep_mask.sum()
    emp[sep_mask] = EMP_U
    ds[sep_mask, DS_UNEMP_DUR] = 0  # reset duration

    # 2. Acceptances: U -> E (those who had offer AND accepted)
    acc_mask = accepts & (emp == EMP_U)  # emp already updated by sep
    transitions['U_to_E'] = acc_mask.sum()
    emp[acc_mask] = EMP_E
    ds[acc_mask, DS_UNEMP_DUR] = 0
    ds[acc_mask, DS_SEARCH_INT] = 0

    # 3. Exits to NILF: E/U -> N
    exit_e = exit_to_n & (emp == EMP_E)
    exit_u = exit_to_n & (emp == EMP_U)
    transitions['E_to_N'] = exit_e.sum()
    transitions['U_to_N'] = exit_u.sum()
    emp[exit_to_n & ((emp == EMP_E) | (emp == EMP_U))] = EMP_N
    ds[exit_to_n, DS_SEARCH_INT] = 0
    ds[exit_to_n, DS_UNEMP_DUR] = 0

    # 4. Entries from NILF: N -> U
    enter_mask = enter_from_n & (emp == EMP_N)
    transitions['N_to_U'] = enter_mask.sum()
    emp[enter_mask] = EMP_U
    ds[enter_mask, DS_UNEMP_DUR] = 0

    # Write back
    cs[:, CS_EMPLOYMENT] = emp

    # Update unemployment duration for remaining U
    still_u = emp == EMP_U
    ds[still_u, DS_UNEMP_DUR] += 1

    return transitions


def update_income(cs, ds, st, env, rng):
    """Update household income based on employment state."""
    emp = cs[:, CS_EMPLOYMENT]
    ages = st[:, ST_AGE].astype(np.float64)
    edus = st[:, ST_EDUCATION].astype(np.float64)
    income = ds[:, DS_HH_INCOME]

    # Background income growth
    bg = env['income_growth_bg']

    # Employed: income grows at background rate + noise
    mask_e = emp == EMP_E
    income[mask_e] *= (1.0 + bg + rng.normal(0, 0.005, size=mask_e.sum()))

    # Newly unemployed: income drops to unemployment benefit level (~40% of prior)
    newly_u = (emp == EMP_U) & (ds[:, DS_UNEMP_DUR] <= 1)
    income[newly_u] *= 0.40

    # NILF: income at ~50% level (pensions, transfers, etc.)
    mask_n = emp == EMP_N
    # Don't continuously reduce, just maintain low level
    # (initial income was already set low for N in population init)

    # Clip
    income[:] = np.clip(income, 3.0, 600.0)
    ds[:, DS_HH_INCOME] = income


def update_expectations(cs, ds, env, rng, cfg=None):
    """
    Update income expectations and labor fragility.

    Structural mechanisms (Phase 4):
    - state_dependent_expectation: update speed depends on employment/fragility
    - experience_dependent_expectation: personal experience feeds back
    """
    emp = cs[:, CS_EMPLOYMENT]
    inc_exp = ds[:, DS_INCOME_EXP]
    inc_unc = ds[:, DS_INCOME_UNC]
    frag = ds[:, DS_LABOR_FRAG]

    bg = env['income_growth_bg']
    sep = env['separation_rate']
    N = len(inc_exp)

    # [MECHANISM] state_dependent_expectation
    if cfg and cfg['state_dependent_expectation']['enabled']:
        mc = cfg['state_dependent_expectation']
        mask_e = emp == EMP_E
        mask_u = emp == EMP_U

        # State-dependent adaptation speed
        speed = np.full(N, 0.1)
        speed[mask_e] = mc['employed_adaptation_speed']      # slow
        speed[mask_u] = mc['unemployed_adaptation_speed']     # fast

        # High fragility → faster updating (more reactive)
        if cfg['state_dependent_expectation']['high_fragility_gain_boost'] > 1.0:
            high_frag = frag > 0.5
            speed[high_frag] *= mc['high_fragility_gain_boost']

        noise = rng.normal(0, 0.005, size=N)
        inc_exp[:] += speed * (bg - inc_exp) + noise
    else:
        noise = rng.normal(0, 0.005, size=N)
        inc_exp[:] += 0.1 * (bg - inc_exp) + noise

    # [MECHANISM] experience_dependent_expectation
    if cfg and cfg['experience_dependent_expectation']['enabled']:
        mc = cfg['experience_dependent_expectation']
        # Newly unemployed: sharp downward revision
        newly_u = (emp == EMP_U) & (ds[:, DS_UNEMP_DUR] <= 1)
        revision = mc['experience_weight']
        inc_exp[newly_u] -= revision  # personal job loss → pessimism

        # Recently re-employed: upward revision
        # (can't track directly here, but employed with low duration proxy)
        # Skip for now — would need a "months since last transition" field

    inc_exp[:] = np.clip(inc_exp, -0.30, 0.50)

    # Uncertainty
    if sep > 0.02:
        inc_unc[:] += 0.002
    else:
        inc_unc[:] -= 0.001
    inc_unc[:] = np.clip(inc_unc, 0.005, 0.50)

    # Labor fragility
    mask_e = emp == EMP_E
    mask_u = emp == EMP_U
    frag[mask_e] -= 0.005
    frag[mask_u] += 0.01
    env_frag = sep / 0.015
    frag[:] += 0.02 * (env_frag * 0.3 - frag)

    # [MECHANISM] experience_dependent_expectation: fragility feedback
    if cfg and cfg['experience_dependent_expectation']['enabled']:
        # Pessimistic expectations → fragility increases (spiral)
        pessimistic = inc_exp < -0.03
        frag[pessimistic] += 0.003

    frag[:] = np.clip(frag, 0.0, 1.0)

    ds[:, DS_INCOME_EXP] = inc_exp
    ds[:, DS_INCOME_UNC] = inc_unc
    ds[:, DS_LABOR_FRAG] = frag
