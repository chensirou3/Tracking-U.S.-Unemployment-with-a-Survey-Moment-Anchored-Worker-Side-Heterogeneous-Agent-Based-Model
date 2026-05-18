"""
Labor Block 3: Opportunity / Offer Arrival
Determines which agents receive job offers this month.

Structural mechanisms (Phase 4):
- matching_competition: finite vacancy pool with competitive allocation
- housing_lockin_modifier: reduces opportunity exposure for locked-in owners
"""
import numpy as np
from Phase3_Code.constants import *


def opportunity_block(cs, ds, bp, env, rng, cfg=None):
    N = cs.shape[0]
    emp = cs[:, CS_EMPLOYMENT]
    search_int = ds[:, DS_SEARCH_INT]
    mob_fric = ds[:, DS_MOBILITY_FRIC]
    flex = bp[:, BP_FLEXIBILITY]
    frag = ds[:, DS_LABOR_FRAG]
    hsg = cs[:, CS_HOUSING_STATUS]

    has_offer = np.zeros(N, dtype=bool)
    offered_wage_ratio = np.zeros(N, dtype=np.float64)
    is_separated = np.zeros(N, dtype=bool)

    mt = env['market_tightness']
    sep_rate = env['separation_rate']

    mask_u = emp == EMP_U
    n_u = mask_u.sum()

    if n_u > 0:
        s = search_int[mask_u]
        s_norm = np.clip(s / 40.0, 0, 1)

        # [MECHANISM] matching_competition: finite vacancy pool
        use_competition = cfg and cfg['matching_competition']['enabled']

        if use_competition:
            # Number of vacancies this month
            vac_rate = cfg['matching_competition']['vacancy_rate']
            n_vacancies = max(int(N * vac_rate * mt), 1)

            # Compute competitiveness score for each U agent
            score = (s_norm
                     * (1.0 - 0.3 * mob_fric[mask_u])
                     * (1.0 + 0.1 * np.clip(flex[mask_u], -1, 3)))

            # [MECHANISM] housing_lockin_modifier: penalize locked-in owners
            if cfg['housing_lockin_modifier']['enabled']:
                hsg_u = hsg[mask_u]
                penalty = cfg['housing_lockin_modifier']['lockin_search_penalty']
                score[hsg_u == HSG_OWN_HIGH] *= (1.0 - penalty)

            # Add noise to score (prevent deterministic ordering)
            score *= rng.lognormal(0, 0.2, size=n_u)
            score = np.maximum(score, 0.001)

            # Top n_vacancies agents by score get offers
            if n_vacancies >= n_u:
                offers_u = np.ones(n_u, dtype=bool)
            else:
                threshold = np.partition(score, -n_vacancies)[-n_vacancies]
                offers_u = score >= threshold
                # If ties, randomly break
                n_selected = offers_u.sum()
                if n_selected > n_vacancies:
                    excess = n_selected - n_vacancies
                    tie_indices = np.where(offers_u & (score == threshold))[0]
                    drop = rng.choice(tie_indices, size=min(excess, len(tie_indices)),
                                      replace=False)
                    offers_u[drop] = False
        else:
            # Phase 3 fallback: independent offer probability
            alpha, beta, gamma = 0.75, 0.25, 0.25
            p_offer = alpha * (s_norm ** beta) * (mt ** gamma)
            friction_discount = 0.3 * mob_fric[mask_u]
            p_offer *= (1.0 - friction_discount)
            flex_bonus = 0.05 * np.clip(flex[mask_u], 0, 3)
            p_offer += flex_bonus
            p_offer = np.clip(p_offer, 0.05, 0.70)
            offers_u = rng.random(n_u) < p_offer

        has_offer[mask_u] = offers_u

        # Offered wage: duration penalty + market conditions
        dur = ds[mask_u, DS_UNEMP_DUR]
        wage_penalty = np.exp(-0.01 * dur)
        base_wage = rng.lognormal(np.log(1.10), 0.20, size=n_u)
        offered_wage_ratio[mask_u] = base_wage * wage_penalty * (mt ** 0.2)

    # === EXOGENOUS SEPARATIONS (E -> U) ===
    mask_e = emp == EMP_E
    if mask_e.sum() > 0:
        p_sep = sep_rate * np.ones(mask_e.sum())
        frag_bonus = 0.2 * frag[mask_e]
        p_sep *= (1.0 + frag_bonus)
        p_sep = np.clip(p_sep, 0.002, 0.05)
        is_separated[mask_e] = rng.random(mask_e.sum()) < p_sep

    return has_offer, offered_wage_ratio, is_separated
