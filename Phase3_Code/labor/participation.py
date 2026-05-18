"""
Labor Block 1: Participation
Determines whether agents enter/exit the labor force.
Transitions: E->N, U->N, N->U, N->E

Structural mechanisms (Phase 4):
- discouraged_worker: duration-dependent discouragement
- fragility_x_liquidity_interaction: high frag + H2M → exit boost
- housing_reentry_friction: housing lock-in affects re-entry
- expectation_participation: income expectation affects entry/exit
"""
import numpy as np
from Phase3_Code.constants import *


def participation_block(cs, ds, st, env, rng, cfg=None):
    N = cs.shape[0]
    emp = cs[:, CS_EMPLOYMENT]
    ages = st[:, ST_AGE]
    frag = ds[:, DS_LABOR_FRAG]
    inc_exp = ds[:, DS_INCOME_EXP]
    cash_buf = ds[:, DS_CASH_BUFFER]
    liq_type = cs[:, CS_LIQUIDITY_TYPE]
    hsg = cs[:, CS_HOUSING_STATUS]

    exit_to_n = np.zeros(N, dtype=bool)
    enter_from_n = np.zeros(N, dtype=bool)

    # ============================================================
    # E -> N transitions
    # ============================================================
    mask_e = emp == EMP_E
    base_exit_e = np.where(ages >= 62, 0.005,
                  np.where(ages >= 55, 0.002, 0.0005))
    p_exit_e = base_exit_e * (1.0 + 0.5 * frag)

    # [MECHANISM] expectation_participation: pessimism → more likely to exit E
    if cfg and cfg['expectation_participation']['enabled']:
        pessimism_boost = cfg['expectation_participation']['pessimism_exit_boost']
        p_exit_e *= np.where(inc_exp < -0.05, 1.0 + pessimism_boost, 1.0)

    p_exit_e = np.clip(p_exit_e, 0, 0.05)
    exit_to_n |= mask_e & (rng.random(N) < p_exit_e)

    # ============================================================
    # U -> N transitions
    # ============================================================
    mask_u = emp == EMP_U
    unemp_dur = ds[:, DS_UNEMP_DUR]
    base_exit_u = 0.015 + 0.003 * np.minimum(unemp_dur, 24) / 24

    exp_factor = np.where(inc_exp < -0.05, 1.5,
                 np.where(inc_exp < 0, 1.2, 1.0))
    buf_factor = np.where(cash_buf < 0.5, 1.3, 1.0)
    p_exit_u = base_exit_u * exp_factor * buf_factor

    # [MECHANISM] discouraged_worker: duration > threshold → exit jump
    if cfg and cfg['discouraged_worker']['enabled']:
        dur_thresh = cfg['discouraged_worker']['duration_threshold_months']
        jump = cfg['discouraged_worker']['exit_jump_factor']
        long_term_u = unemp_dur > dur_thresh
        p_exit_u = np.where(long_term_u, p_exit_u * jump, p_exit_u)

    # [MECHANISM] fragility_x_liquidity_interaction: high frag + H2M → exit boost
    if cfg and cfg['fragility_x_liquidity_interaction']['enabled']:
        boost = cfg['fragility_x_liquidity_interaction']['discouraged_exit_boost']
        frag_liq_mask = (frag > 0.5) & (liq_type == LIQ_H2M)
        p_exit_u = np.where(frag_liq_mask, p_exit_u + boost, p_exit_u)

    # [MECHANISM] expectation_participation: pessimism → exit
    if cfg and cfg['expectation_participation']['enabled']:
        pessimism_boost = cfg['expectation_participation']['pessimism_exit_boost']
        p_exit_u *= np.where(inc_exp < -0.05, 1.0 + pessimism_boost, 1.0)

    p_exit_u = np.clip(p_exit_u, 0, 0.15)
    exit_to_n |= mask_u & (rng.random(N) < p_exit_u)

    # ============================================================
    # N -> U transitions (entering labor force)
    # ============================================================
    mask_n = emp == EMP_N
    base_enter = np.where(ages < 25, 0.03,
                 np.where(ages < 55, 0.015, 0.005))
    exp_enter_factor = np.where(inc_exp > 0.03, 1.3,
                       np.where(inc_exp > 0, 1.1, 0.8))
    buf_enter_factor = np.where(cash_buf < 1.0, 1.5, 1.0)
    p_enter = base_enter * exp_enter_factor * buf_enter_factor

    # [MECHANISM] expectation_participation: optimism → more entry
    if cfg and cfg['expectation_participation']['enabled']:
        opt_boost = cfg['expectation_participation']['optimism_entry_boost']
        p_enter *= np.where(inc_exp > 0.02, 1.0 + opt_boost, 1.0)

    # [MECHANISM] housing_reentry_friction: owners face re-entry penalty
    if cfg and cfg['housing_reentry_friction']['enabled']:
        penalty = cfg['housing_reentry_friction']['owner_reentry_penalty']
        is_owner = (hsg == HSG_OWN_LOW) | (hsg == HSG_OWN_HIGH)
        p_enter = np.where(is_owner, p_enter * (1.0 - penalty), p_enter)

    p_enter = np.clip(p_enter, 0, 0.10)
    enter_from_n = mask_n & (rng.random(N) < p_enter)

    return exit_to_n, enter_from_n
