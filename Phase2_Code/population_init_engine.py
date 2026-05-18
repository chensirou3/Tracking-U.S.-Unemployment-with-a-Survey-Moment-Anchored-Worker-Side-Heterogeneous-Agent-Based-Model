"""
Phase 2 - Vectorized Population Initialization Engine
Generates synthetic agent population with realistic heterogeneity.

Output: Phase2_Output/population_v1.npz
"""
import numpy as np
import json
import os

os.makedirs('Phase2_Output', exist_ok=True)

# ============================================================
# CONSTANTS (from Phase 1 Agent Schema)
# ============================================================
# static_traits columns
ST_AGE, ST_EDUCATION, ST_MARITAL, ST_HH_SIZE = 0, 1, 2, 3
# category_states columns
CS_EMPLOYMENT, CS_LIQUIDITY_TYPE, CS_HOUSING_STATUS, CS_CONSUMPTION_TYPE = 0, 1, 2, 3
# dynamic_states columns
DS_INCOME_EXP, DS_INCOME_UNC, DS_LABOR_FRAG, DS_CASH_BUFFER = 0, 1, 2, 3
DS_SEARCH_INT, DS_MOBILITY_FRIC, DS_HH_INCOME, DS_UNEMP_DUR, DS_DEBT_STRESS = 4, 5, 6, 7, 8
# behavior_params columns
BP_MPC_POS, BP_MPC_NEG, BP_ASYMMETRY, BP_RESV_WAGE, BP_FLEXIBILITY = 0, 1, 2, 3, 4
# Encodings
EMP_E, EMP_U, EMP_N = 0, 1, 2
LIQ_H2M, LIQ_BUFFER, LIQ_WEALTHY = 0, 1, 2
HSG_RENT_MOB, HSG_RENT_STB, HSG_OWN_LOW, HSG_OWN_HIGH = 0, 1, 2, 3
CON_SAVER, CON_SMOOTHER, CON_SPENDER = 0, 1, 2

K_STATIC, K_CAT, K_DYN, K_BEHAV = 4, 4, 9, 5


def generate_population(N=100_000, seed=42):
    """Generate N synthetic agents with realistic heterogeneity."""
    rng = np.random.default_rng(seed)

    static_traits = np.zeros((N, K_STATIC), dtype=np.int16)
    category_states = np.zeros((N, K_CAT), dtype=np.int8)
    dynamic_states = np.zeros((N, K_DYN), dtype=np.float64)
    behavior_params = np.zeros((N, K_BEHAV), dtype=np.float64)

    # ========================================================
    # STEP 1: Static Traits (Population Backbone)
    # ========================================================
    # Age: 3 groups → uniform within group
    age_probs = [0.277, 0.391, 0.332]  # <40, 40-60, >60
    age_groups = rng.choice(3, size=N, p=age_probs)
    age_ranges = [(18, 39), (40, 60), (61, 85)]
    for g in range(3):
        mask = age_groups == g
        lo, hi = age_ranges[g]
        static_traits[mask, ST_AGE] = rng.integers(lo, hi + 1, size=mask.sum())

    # Education: 3 groups, weakly conditional on age
    edu_probs = [0.114, 0.332, 0.554]  # HS, SomeCol, College+
    static_traits[:, ST_EDUCATION] = rng.choice(3, size=N, p=edu_probs).astype(np.int16)

    # Marital status: ~50% married (approximate)
    static_traits[:, ST_MARITAL] = rng.binomial(1, 0.50, size=N).astype(np.int16)

    # Household size: 1-6, right-skewed
    hh_probs = [0.28, 0.34, 0.15, 0.13, 0.06, 0.04]
    static_traits[:, ST_HH_SIZE] = (rng.choice(6, size=N, p=hh_probs) + 1).astype(np.int16)

    ages = static_traits[:, ST_AGE]
    edus = static_traits[:, ST_EDUCATION]

    # ========================================================
    # STEP 2: Employment State (conditional on age × education)
    # ========================================================
    # BLS-calibrated: overall E=60%, U=4%, N=36%
    # Young: higher U, lower N | Old: lower U, higher N
    emp = np.full(N, EMP_E, dtype=np.int8)
    for ag in range(3):
        age_mask = age_groups == ag
        if ag == 0:    # <40: E=68%, U=6%, N=26%
            probs = [0.68, 0.06, 0.26]
        elif ag == 1:  # 40-60: E=72%, U=4%, N=24%
            probs = [0.72, 0.04, 0.24]
        else:          # >60: E=35%, U=2%, N=63%
            probs = [0.35, 0.02, 0.63]
        emp[age_mask] = rng.choice(3, size=age_mask.sum(), p=probs).astype(np.int8)
    category_states[:, CS_EMPLOYMENT] = emp

    # ========================================================
    # STEP 3: Housing Status (conditional on age)
    # ========================================================
    hsg = np.zeros(N, dtype=np.int8)
    for ag in range(3):
        mask = age_groups == ag
        if ag == 0:    # Young: more renters
            probs = [0.20, 0.30, 0.30, 0.20]
        elif ag == 1:  # Middle: more owners
            probs = [0.08, 0.15, 0.50, 0.27]
        else:          # Old: owners, low LTV
            probs = [0.08, 0.15, 0.55, 0.22]
        hsg[mask] = rng.choice(4, size=mask.sum(), p=probs).astype(np.int8)
    category_states[:, CS_HOUSING_STATUS] = hsg

    # ========================================================
    # STEP 4: Liquidity Type (conditional on employment × housing)
    # ========================================================
    # Joint relation 4: housing × liquidity
    liq_table = {
        # (employment, housing) → [H2M, Buffer, Wealthy]
    }
    # Simplified: condition mainly on employment and housing
    liq = np.zeros(N, dtype=np.int8)
    for e_state in [EMP_E, EMP_U, EMP_N]:
        for h_state in range(4):
            mask = (emp == e_state) & (hsg == h_state)
            if mask.sum() == 0:
                continue
            # Base probabilities
            if e_state == EMP_U:
                base = [0.50, 0.40, 0.10]
            elif e_state == EMP_N:
                base = [0.35, 0.40, 0.25]
            else:  # Employed
                base = [0.20, 0.45, 0.35]
            # Housing adjustment
            if h_state in [HSG_OWN_LOW]:
                # Owners tend wealthier
                adj = [-0.10, 0.0, 0.10]
            elif h_state in [HSG_OWN_HIGH]:
                # High-LTV owners: asset-rich but possibly liquidity-poor
                adj = [0.10, 0.0, -0.10]
            elif h_state == HSG_RENT_MOB:
                adj = [0.10, 0.0, -0.10]
            else:
                adj = [0.0, 0.0, 0.0]
            probs = np.clip(np.array(base) + np.array(adj), 0.01, 1.0)
            probs /= probs.sum()
            liq[mask] = rng.choice(3, size=mask.sum(), p=probs).astype(np.int8)
    category_states[:, CS_LIQUIDITY_TYPE] = liq

    # ========================================================
    # STEP 5: Consumption Type (conditional on liquidity_type)
    # ========================================================
    # Joint relation 2: liquidity × consumption
    con_type = np.zeros(N, dtype=np.int8)
    con_table = {
        LIQ_H2M:     [0.10, 0.30, 0.60],  # H2M → mostly Spender
        LIQ_BUFFER:  [0.25, 0.50, 0.25],  # Buffer → mostly Smoother
        LIQ_WEALTHY: [0.55, 0.35, 0.10],  # Wealthy → mostly Saver
    }
    for lt, probs in con_table.items():
        mask = liq == lt
        con_type[mask] = rng.choice(3, size=mask.sum(), p=probs).astype(np.int8)
    category_states[:, CS_CONSUMPTION_TYPE] = con_type

    # ========================================================
    # STEP 6: Labor Fragility (conditional on employment × age)
    # ========================================================
    # Dynamic state: fragility_index ∈ [0, 1]
    # From data: Q13new mean=14.8%, Q22new mean=54.6%
    # fragility = (Q13new/100 + (100-Q22new)/100) / 2
    # Overall mean ≈ 0.30, median ≈ 0.26
    frag = np.zeros(N, dtype=np.float64)
    for e_state in [EMP_E, EMP_U, EMP_N]:
        for ag in range(3):
            mask = (emp == e_state) & (age_groups == ag)
            n_mask = mask.sum()
            if n_mask == 0:
                continue
            # Set mean/std by group
            if e_state == EMP_E:
                mu = 0.18 if ag == 0 else (0.22 if ag == 1 else 0.30)
                sigma = 0.12
            elif e_state == EMP_U:
                mu = 0.50 if ag == 0 else (0.55 if ag == 1 else 0.65)
                sigma = 0.15
            else:  # N
                mu = 0.40 if ag == 0 else (0.45 if ag == 1 else 0.50)
                sigma = 0.15
            vals = rng.normal(mu, sigma, size=n_mask)
            frag[mask] = np.clip(vals, 0.0, 1.0)
    dynamic_states[:, DS_LABOR_FRAG] = frag

    # ========================================================
    # STEP 7: Income Growth Expectation (conditional on fragility)
    # ========================================================
    # Joint relation 1: higher fragility → lower income expectation
    # From data: Q24_cent50 mean=3.05%, std=4.91%, median=2.3%
    # Store as fraction (not percentage)
    inc_exp = np.zeros(N, dtype=np.float64)
    # Map fragility to income expectation: negative correlation
    # fragility 0 → income_exp ~ N(0.04, 0.03)
    # fragility 1 → income_exp ~ N(-0.02, 0.05)
    base_mu = 0.04 - 0.06 * frag  # linear mapping
    base_sigma = 0.03 + 0.02 * frag  # higher uncertainty for fragile
    inc_exp = rng.normal(base_mu, base_sigma)
    inc_exp = np.clip(inc_exp, -0.30, 0.50)
    dynamic_states[:, DS_INCOME_EXP] = inc_exp

    # Income uncertainty
    inc_unc = 0.02 + 0.03 * frag + rng.exponential(0.01, size=N)
    inc_unc = np.clip(inc_unc, 0.0, 0.50)
    dynamic_states[:, DS_INCOME_UNC] = inc_unc

    # ========================================================
    # STEP 8: Labor Search Friction (conditional on employment × housing)
    # ========================================================
    # Joint relation 3 & 5

    # 8a: Reservation wage ratio
    # From data: rw2h median=$21.6/hr → ratio ≈ 1.0
    resv_wage = np.ones(N, dtype=np.float64)
    # Employed: from distribution centered on 1.0
    mask_e = emp == EMP_E
    resv_wage[mask_e] = rng.lognormal(np.log(1.05), 0.25, size=mask_e.sum())
    # Unemployed: starts at 1.0, decreases with duration (set initial)
    mask_u = emp == EMP_U
    resv_wage[mask_u] = rng.lognormal(np.log(0.95), 0.30, size=mask_u.sum())
    # NILF: very high (not searching)
    mask_n = emp == EMP_N
    resv_wage[mask_n] = rng.lognormal(np.log(2.0), 0.3, size=mask_n.sum())
    resv_wage = np.clip(resv_wage, 0.5, 5.0)
    behavior_params[:, BP_RESV_WAGE] = resv_wage

    # 8b: Search intensity (hours/week)
    search_int = np.zeros(N, dtype=np.float64)
    # Only unemployed search
    search_int[mask_u] = rng.exponential(10.0, size=mask_u.sum())
    search_int = np.clip(search_int, 0.0, 40.0)
    dynamic_states[:, DS_SEARCH_INT] = search_int

    # 8c: Flexibility index (higher = more flexible)
    flex = np.zeros(N, dtype=np.float64)
    # Condition on housing: owners less flexible
    for h_state in range(4):
        mask = hsg == h_state
        if h_state == HSG_RENT_MOB:
            mu, sigma = 1.0, 0.8
        elif h_state == HSG_RENT_STB:
            mu, sigma = 0.3, 0.7
        elif h_state == HSG_OWN_LOW:
            mu, sigma = -0.3, 0.7
        else:  # OWN_HIGH
            mu, sigma = -1.0, 0.6
        flex[mask] = rng.normal(mu, sigma, size=mask.sum())
    flex = np.clip(flex, -3.0, 3.0)
    behavior_params[:, BP_FLEXIBILITY] = flex

    # ========================================================
    # STEP 9: Remaining Dynamic States
    # ========================================================

    # 9a: Cash buffer months (conditional on liquidity_type)
    cash_buf = np.zeros(N, dtype=np.float64)
    buf_params = {
        LIQ_H2M:     (0.5, 0.3, 0.0, 1.5),    # mean, std, min, max
        LIQ_BUFFER:  (3.0, 1.5, 1.0, 8.0),
        LIQ_WEALTHY: (12.0, 4.0, 5.0, 36.0),
    }
    for lt, (mu, sigma, lo, hi) in buf_params.items():
        mask = liq == lt
        vals = rng.normal(mu, sigma, size=mask.sum())
        cash_buf[mask] = np.clip(vals, lo, hi)
    dynamic_states[:, DS_CASH_BUFFER] = cash_buf

    # 9b: Mobility friction score (conditional on housing_status)
    mob_fric = np.zeros(N, dtype=np.float64)
    mob_params = {
        HSG_RENT_MOB:  (0.15, 0.10),
        HSG_RENT_STB:  (0.35, 0.15),
        HSG_OWN_LOW:   (0.60, 0.15),
        HSG_OWN_HIGH:  (0.80, 0.10),
    }
    for hs, (mu, sigma) in mob_params.items():
        mask = hsg == hs
        mob_fric[mask] = np.clip(rng.normal(mu, sigma, size=mask.sum()), 0.0, 1.0)
    dynamic_states[:, DS_MOBILITY_FRIC] = mob_fric

    # 9c: Household income (conditional on employment × education × age)
    hh_income = np.zeros(N, dtype=np.float64)
    # Approximate annual income in $1000s
    base_income = 30.0 + 15.0 * edus + 0.3 * ages - 0.004 * ages**2
    emp_factor = np.where(emp == EMP_E, 1.0, np.where(emp == EMP_U, 0.3, 0.5))
    hh_income = base_income * emp_factor * rng.lognormal(0, 0.3, size=N)
    hh_income = np.clip(hh_income, 5.0, 500.0)
    dynamic_states[:, DS_HH_INCOME] = hh_income

    # 9d: Unemployment duration (only for U state)
    unemp_dur = np.zeros(N, dtype=np.float64)
    unemp_dur[mask_u] = rng.exponential(4.0, size=mask_u.sum())  # mean 4 months
    unemp_dur = np.clip(unemp_dur, 0.0, 60.0)
    dynamic_states[:, DS_UNEMP_DUR] = unemp_dur

    # 9e: Debt stress (derived from liquidity type)
    debt_stress = np.zeros(N, dtype=np.float64)
    debt_stress[liq == LIQ_H2M] = rng.beta(3, 2, size=(liq == LIQ_H2M).sum())  # mean ~0.6
    debt_stress[liq == LIQ_BUFFER] = rng.beta(2, 5, size=(liq == LIQ_BUFFER).sum())  # mean ~0.28
    debt_stress[liq == LIQ_WEALTHY] = rng.beta(1, 8, size=(liq == LIQ_WEALTHY).sum())  # mean ~0.11
    dynamic_states[:, DS_DEBT_STRESS] = debt_stress

    # ========================================================
    # STEP 10: MPC Parameters (conditional on consumption_type)
    # ========================================================
    # From data: qsp12n 1-7 scale → mpc_pos = (val-1)/6
    # qsp12n distribution: 1=22%, 2=2%, 3=15%, 4=28%, 5=7%, 6=11%, 7=14%
    mpc_params = {
        CON_SAVER:    (0.15, 0.10, 0.10, 0.08),  # (mpc_pos_mu, mpc_pos_std, mpc_neg_mu, mpc_neg_std)
        CON_SMOOTHER: (0.45, 0.15, 0.30, 0.12),
        CON_SPENDER:  (0.75, 0.12, 0.55, 0.15),
    }
    for ct, (pos_mu, pos_std, neg_mu, neg_std) in mpc_params.items():
        mask = con_type == ct
        n_m = mask.sum()
        mpc_pos = np.clip(rng.normal(pos_mu, pos_std, size=n_m), 0.01, 0.99)
        mpc_neg = np.clip(rng.normal(neg_mu, neg_std, size=n_m), 0.01, 0.99)
        behavior_params[mask, BP_MPC_POS] = mpc_pos
        behavior_params[mask, BP_MPC_NEG] = mpc_neg
        behavior_params[mask, BP_ASYMMETRY] = mpc_neg / np.maximum(mpc_pos, 0.01)

    # ========================================================
    # DONE: Return population
    # ========================================================
    return {
        'static_traits': static_traits,
        'category_states': category_states,
        'dynamic_states': dynamic_states,
        'behavior_params': behavior_params,
    }


def save_population(pop, path='Phase2_Output/population_v1.npz'):
    """Save population to compressed npz file."""
    np.savez_compressed(path, **pop)
    # Size info
    total_bytes = sum(v.nbytes for v in pop.values())
    print(f"Population saved to {path}")
    print(f"  Total memory: {total_bytes / 1024 / 1024:.2f} MB")
    for name, arr in pop.items():
        print(f"  {name}: shape={arr.shape}, dtype={arr.dtype}, "
              f"size={arr.nbytes / 1024:.1f} KB")


def save_schema(path='Phase2_Output/matrix_schema_map.json'):
    """Save schema mapping as JSON."""
    schema = {
        'static_traits': {
            'columns': {'age': ST_AGE, 'education': ST_EDUCATION,
                        'marital_status': ST_MARITAL, 'household_size': ST_HH_SIZE},
            'dtype': 'int16', 'K': K_STATIC,
        },
        'category_states': {
            'columns': {'employment_state': CS_EMPLOYMENT, 'liquidity_type': CS_LIQUIDITY_TYPE,
                        'housing_status': CS_HOUSING_STATUS, 'consumption_type': CS_CONSUMPTION_TYPE},
            'dtype': 'int8', 'K': K_CAT,
            'encodings': {
                'employment': {'E': EMP_E, 'U': EMP_U, 'N': EMP_N},
                'liquidity': {'H2M': LIQ_H2M, 'Buffer': LIQ_BUFFER, 'Wealthy': LIQ_WEALTHY},
                'housing': {'Renter-Mobile': HSG_RENT_MOB, 'Renter-Stable': HSG_RENT_STB,
                            'Owner-Low-LTV': HSG_OWN_LOW, 'Owner-High-LTV': HSG_OWN_HIGH},
                'consumption': {'Saver': CON_SAVER, 'Smoother': CON_SMOOTHER, 'Spender': CON_SPENDER},
            },
        },
        'dynamic_states': {
            'columns': {'income_expectation': DS_INCOME_EXP, 'income_uncertainty': DS_INCOME_UNC,
                        'labor_fragility': DS_LABOR_FRAG, 'cash_buffer_months': DS_CASH_BUFFER,
                        'search_intensity': DS_SEARCH_INT, 'mobility_friction_score': DS_MOBILITY_FRIC,
                        'household_income': DS_HH_INCOME, 'unemployment_duration': DS_UNEMP_DUR,
                        'debt_stress': DS_DEBT_STRESS},
            'dtype': 'float64', 'K': K_DYN,
        },
        'behavior_params': {
            'columns': {'mpc_positive': BP_MPC_POS, 'mpc_negative': BP_MPC_NEG,
                        'asymmetry_ratio': BP_ASYMMETRY, 'reservation_wage_ratio': BP_RESV_WAGE,
                        'flexibility_index': BP_FLEXIBILITY},
            'dtype': 'float64', 'K': K_BEHAV,
        },
    }
    with open(path, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"Schema saved to {path}")


if __name__ == '__main__':
    print("Generating population (N=100,000)...")
    pop = generate_population(N=100_000, seed=42)
    save_population(pop)
    save_schema()
    print("\nPopulation generation complete.")
