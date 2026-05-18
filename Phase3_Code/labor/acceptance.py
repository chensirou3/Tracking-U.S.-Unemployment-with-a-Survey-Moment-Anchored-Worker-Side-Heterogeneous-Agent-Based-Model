"""
Labor Block 4: Acceptance / Job Choice
Determines whether agents with offers accept them.

Structural mechanisms (Phase 4):
- high_fragility_modifier: fragility increases acceptance pressure
- liquidity_constraint_modifier: H2M agents discount reservation wage
"""
import numpy as np
from Phase3_Code.constants import *


def acceptance_block(cs, ds, bp, has_offer, offered_wage_ratio, rng, cfg=None):
    N = cs.shape[0]
    accepts = np.zeros(N, dtype=bool)

    mask_offered = has_offer & (cs[:, CS_EMPLOYMENT] == EMP_U)
    if mask_offered.sum() == 0:
        return accepts

    resv_wage = bp[mask_offered, BP_RESV_WAGE].copy()

    # Duration adjustment
    dur = ds[mask_offered, DS_UNEMP_DUR]
    resv_wage *= np.exp(-0.04 * dur)

    # Buffer pressure
    cash_buf = ds[mask_offered, DS_CASH_BUFFER]
    buffer_adj = np.where(cash_buf < 0.5, 0.7,
                 np.where(cash_buf < 1.0, 0.85,
                 np.where(cash_buf < 2.0, 0.95, 1.0)))
    resv_wage *= buffer_adj

    # Fragility pressure
    frag = ds[mask_offered, DS_LABOR_FRAG]
    frag_adj = 1.0 - 0.2 * frag
    resv_wage *= frag_adj

    # [MECHANISM] high_fragility_modifier: additional acceptance pressure
    if cfg and cfg['high_fragility_modifier']['enabled']:
        frag_thresh = cfg['high_fragility_modifier']['fragility_threshold']
        pressure = cfg['high_fragility_modifier']['acceptance_pressure_factor']
        high_frag = frag > frag_thresh
        resv_wage[high_frag] *= (1.0 - pressure)

    # [MECHANISM] liquidity_constraint_modifier: H2M discount
    if cfg and cfg['liquidity_constraint_modifier']['enabled']:
        liq = cs[mask_offered, CS_LIQUIDITY_TYPE]
        h2m_discount = cfg['liquidity_constraint_modifier']['h2m_resv_wage_discount']
        h2m_mask = liq == LIQ_H2M
        resv_wage[h2m_mask] *= (1.0 - h2m_discount)

    resv_wage = np.maximum(resv_wage, 0.3)
    offered = offered_wage_ratio[mask_offered]
    accepts[mask_offered] = offered >= resv_wage

    return accepts
