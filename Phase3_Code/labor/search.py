"""
Labor Block 2: Search
Determines search intensity for unemployed agents.

Structural mechanisms (Phase 4):
- high_fragility_modifier: fragility changes search behavior direction based on buffer
- housing_lockin_modifier: Owner-High-LTV face search penalty
"""
import numpy as np
from Phase3_Code.constants import *


def search_block(cs, ds, bp, env, rng, cfg=None):
    N = cs.shape[0]
    emp = cs[:, CS_EMPLOYMENT]
    frag = ds[:, DS_LABOR_FRAG]
    mob_fric = ds[:, DS_MOBILITY_FRIC]
    unemp_dur = ds[:, DS_UNEMP_DUR]
    cash_buf = ds[:, DS_CASH_BUFFER]
    flex = bp[:, BP_FLEXIBILITY]
    hsg = cs[:, CS_HOUSING_STATUS]
    liq_type = cs[:, CS_LIQUIDITY_TYPE]

    search_int = np.zeros(N, dtype=np.float64)
    mask_u = emp == EMP_U
    if mask_u.sum() == 0:
        return search_int

    n_u = mask_u.sum()
    base_search = 10.0 * np.ones(n_u)
    dur = unemp_dur[mask_u]
    duration_factor = np.exp(-0.015 * dur)

    # [MECHANISM] high_fragility_modifier: direction depends on buffer
    if cfg and cfg['high_fragility_modifier']['enabled']:
        frag_u = frag[mask_u]
        buf_u = cash_buf[mask_u]
        buf_thresh = cfg['high_fragility_modifier']['search_desperation_buffer_threshold']
        frag_thresh = cfg['high_fragility_modifier']['fragility_threshold']
        # High fragility + low buffer → desperate, search MORE
        desperate = (frag_u > frag_thresh) & (buf_u < buf_thresh)
        # High fragility + adequate buffer → discouraged, search LESS
        discouraged = (frag_u > frag_thresh) & (buf_u >= buf_thresh)
        frag_factor = np.ones(n_u)
        frag_factor[desperate] = 1.0 + 0.5 * frag_u[desperate]
        frag_factor[discouraged] = 1.0 - 0.3 * frag_u[discouraged]
    else:
        frag_factor = 1.0 + 0.3 * frag[mask_u]

    buf = cash_buf[mask_u]
    buffer_factor = np.where(buf < 1.0, 1.4,
                    np.where(buf < 3.0, 1.1, 1.0))
    mob_factor = 1.0 - 0.3 * mob_fric[mask_u]
    flex_factor = 1.0 + 0.1 * flex[mask_u]
    market_factor = 1.0 / max(env['market_tightness'], 0.3)

    # [MECHANISM] housing_lockin_modifier: Owner-High-LTV penalty
    lockin_factor = np.ones(n_u)
    if cfg and cfg['housing_lockin_modifier']['enabled']:
        hsg_u = hsg[mask_u]
        penalty = cfg['housing_lockin_modifier']['lockin_search_penalty']
        lockin_factor[hsg_u == HSG_OWN_HIGH] = 1.0 - penalty

    search = (base_search * duration_factor * frag_factor * buffer_factor
              * mob_factor * flex_factor * market_factor * lockin_factor)
    search *= rng.lognormal(0, 0.15, size=n_u)
    search_int[mask_u] = np.clip(search, 0.5, 40.0)
    return search_int
