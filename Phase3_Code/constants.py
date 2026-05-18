"""
Shared constants for Phase 3 model engine.
Column indices, encodings, and default parameters.
"""

# === Matrix dimensions ===
K_STATIC, K_CAT, K_DYN, K_BEHAV = 4, 4, 9, 5

# === static_traits columns ===
ST_AGE, ST_EDUCATION, ST_MARITAL, ST_HH_SIZE = 0, 1, 2, 3

# === category_states columns ===
CS_EMPLOYMENT = 0
CS_LIQUIDITY_TYPE = 1
CS_HOUSING_STATUS = 2
CS_CONSUMPTION_TYPE = 3

# === dynamic_states columns ===
DS_INCOME_EXP = 0
DS_INCOME_UNC = 1
DS_LABOR_FRAG = 2
DS_CASH_BUFFER = 3
DS_SEARCH_INT = 4
DS_MOBILITY_FRIC = 5
DS_HH_INCOME = 6
DS_UNEMP_DUR = 7
DS_DEBT_STRESS = 8

# === behavior_params columns ===
BP_MPC_POS = 0
BP_MPC_NEG = 1
BP_ASYMMETRY = 2
BP_RESV_WAGE = 3
BP_FLEXIBILITY = 4

# === Employment state encodings ===
EMP_E, EMP_U, EMP_N = 0, 1, 2

# === Liquidity type encodings ===
LIQ_H2M, LIQ_BUFFER, LIQ_WEALTHY = 0, 1, 2

# === Housing status encodings ===
HSG_RENT_MOB, HSG_RENT_STB, HSG_OWN_LOW, HSG_OWN_HIGH = 0, 1, 2, 3

# === Consumption type encodings ===
CON_SAVER, CON_SMOOTHER, CON_SPENDER = 0, 1, 2
