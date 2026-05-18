"""
Household Block 2: Borrowing / Liquidity Adjustment

Structural mechanisms (Phase 4):
- buffer_consumption_ordering: type-dependent buffer usage sequence
- consumption_sequencing: interacts with consumption adjustment path
"""
import numpy as np
from Phase3_Code.constants import *


def borrowing_block(cs, ds, savings, env, rng, cfg=None):
    N = cs.shape[0]
    cash_buf = ds[:, DS_CASH_BUFFER].copy()
    liq_type = cs[:, CS_LIQUIDITY_TYPE].copy()
    debt_stress = ds[:, DS_DEBT_STRESS].copy()
    income = ds[:, DS_HH_INCOME]
    con_type = cs[:, CS_CONSUMPTION_TYPE]

    monthly_expense = np.maximum(income / 12.0 * 0.80, 0.5)
    buffer_change = savings / monthly_expense

    # [MECHANISM] buffer_consumption_ordering: type-dependent sequence
    if cfg and cfg['buffer_consumption_ordering']['enabled']:
        mc = cfg['buffer_consumption_ordering']
        max_neg = mc['max_negative_buffer']

        # Saver: protects buffer → negative savings translate to LESS buffer drain
        # (they already cut consumption more in consumption block)
        saver_mask = con_type == CON_SAVER
        # Savers' buffer change already reflects their lower MPC → less drain

        # Spender: drains buffer first → allow negative buffer (borrowing)
        spender_neg = (con_type == CON_SPENDER) & (savings < 0)
        # Spender can go into negative buffer (=borrowing)
        cash_buf += buffer_change
        cash_buf = np.maximum(cash_buf, max_neg)  # allow negative for spenders

        # Non-spenders cannot go negative
        non_spender = ~(con_type == CON_SPENDER)
        cash_buf[non_spender] = np.maximum(cash_buf[non_spender], 0.0)

        # Stress feedback: negative buffer → high stress increment
        stress_rate = mc['stress_feedback_rate']
        neg_buf_mask = cash_buf < 0
        debt_stress[neg_buf_mask] += stress_rate
    else:
        cash_buf += buffer_change
        cash_buf = np.maximum(cash_buf, 0.0)

    # --- Liquidity type transitions ---
    downgrade_mask = (liq_type == LIQ_BUFFER) & (cash_buf < 1.0)
    liq_type[downgrade_mask] = LIQ_H2M

    downgrade_w = (liq_type == LIQ_WEALTHY) & (cash_buf < 4.0)
    liq_type[downgrade_w] = LIQ_BUFFER

    upgrade_h2m = (liq_type == LIQ_H2M) & (cash_buf > 2.0)
    upgrade_h2m &= rng.random(N) < 0.1
    liq_type[upgrade_h2m] = LIQ_BUFFER

    upgrade_buf = (liq_type == LIQ_BUFFER) & (cash_buf > 8.0)
    upgrade_buf &= rng.random(N) < 0.05
    liq_type[upgrade_buf] = LIQ_WEALTHY

    # --- Debt stress update ---
    stress_increase = (savings < 0) & (cash_buf < 2.0)
    stress_decrease = (savings > 0) & (cash_buf > 3.0)
    debt_stress[stress_increase] = np.minimum(debt_stress[stress_increase] + 0.05, 1.0)
    debt_stress[stress_decrease] = np.maximum(debt_stress[stress_decrease] - 0.03, 0.0)
    debt_stress = np.clip(debt_stress, 0.0, 1.0)

    return cash_buf, liq_type.astype(np.int8), debt_stress
