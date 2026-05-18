"""
Household Block 1: Consumption Smoothing

Structural mechanisms (Phase 4):
- effective_mpc_adjustment: MPC dynamically adjusts with liquidity/employment
- consumption_sequencing: different types follow different adjustment paths
- liquidity_constraint_modifier: H2M forced near MPC=1
"""
import numpy as np
from Phase3_Code.constants import *


def consumption_block(cs, ds, bp, env, prev_income, rng, cfg=None):
    N = cs.shape[0]
    income = ds[:, DS_HH_INCOME]
    liq_type = cs[:, CS_LIQUIDITY_TYPE]
    con_type = cs[:, CS_CONSUMPTION_TYPE]
    emp = cs[:, CS_EMPLOYMENT]
    delta_income = income - prev_income

    mpc_pos = bp[:, BP_MPC_POS].copy()
    mpc_neg = bp[:, BP_MPC_NEG].copy()

    # [MECHANISM] effective_mpc_adjustment: state-dependent MPC
    if cfg and cfg['effective_mpc_adjustment']['enabled']:
        mc = cfg['effective_mpc_adjustment']
        # Liquidity adjustment
        h2m_floor = mc['h2m_mpc_floor']
        w_discount = mc['wealthy_mpc_discount']
        u_boost = mc['unemployed_mpc_boost']

        # H2M: floor MPC
        h2m = liq_type == LIQ_H2M
        mpc_pos[h2m] = np.maximum(mpc_pos[h2m], h2m_floor)
        mpc_neg[h2m] = np.maximum(mpc_neg[h2m], h2m_floor)

        # Wealthy: discount MPC
        wealthy = liq_type == LIQ_WEALTHY
        mpc_pos[wealthy] *= (1.0 - w_discount)
        mpc_neg[wealthy] *= (1.0 - w_discount)

        # Unemployed: boost MPC (income uncertainty → spend cautiously? No: forced to spend)
        unemp = emp == EMP_U
        mpc_neg[unemp] = np.minimum(mpc_neg[unemp] + u_boost, 0.99)
    else:
        h2m = liq_type == LIQ_H2M

    # [MECHANISM] consumption_sequencing: type-dependent adjustment paths
    if cfg and cfg['consumption_sequencing']['enabled']:
        sc = cfg['consumption_sequencing']
        buf_protect = sc['saver_buffer_protect_threshold']
        cash_buf = ds[:, DS_CASH_BUFFER]

        # Saver: when income drops, first cut consumption to protect buffer
        saver_mask = con_type == CON_SAVER
        # Saver with adequate buffer: very low MPC neg (prefer to save)
        saver_protected = saver_mask & (cash_buf > buf_protect)
        mpc_neg[saver_protected] *= 0.5  # cut consumption less = use buffer less

        # Spender: when income drops, use buffer first, only then cut consumption
        spender_mask = con_type == CON_SPENDER
        spender_has_buf = spender_mask & (cash_buf > 0.5)
        # Spender with buffer: high MPC neg → they don't cut consumption (use buffer)
        mpc_neg[spender_has_buf] *= 1.3  # more consumption maintained via buffer drain
        mpc_neg[:] = np.clip(mpc_neg, 0.01, 0.99)

    # Apply asymmetric MPC
    delta_c = np.where(delta_income >= 0,
                       delta_income * mpc_pos,
                       delta_income * mpc_neg)

    # Base consumption rate (fraction of income)
    # In steady state, savings should be near zero on average
    # Savers: save ~7%, Smoothers: save ~3%, Spenders: save ~0%
    base_rate = np.where(con_type == CON_SAVER, 0.93,
                np.where(con_type == CON_SMOOTHER, 0.97, 1.00))
    base_rate[h2m] = 1.00  # H2M: consume all income

    consumption = income * base_rate / 12.0 + delta_c
    consumption = np.maximum(consumption, 0.1)

    monthly_income = income / 12.0
    savings = monthly_income - consumption

    return consumption, savings
