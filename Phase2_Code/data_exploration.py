"""
Phase 2 - Step 0: Data Exploration
Extract empirical distributions from SCE survey data for MVP 6 dimensions.
"""
import pandas as pd
import numpy as np
import json
import os

os.makedirs('Phase2_Output', exist_ok=True)

# ============================================================
# 1. CORE SURVEY (all 3 microdata files combined)
# ============================================================
print("Loading Core Survey data...")
core_files = [
    'SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-13-16.xlsx',
    'SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-17-19.xlsx',
    'SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-20-present.xlsx',
]
core_dfs = []
for f in core_files:
    print(f"  Reading {f}...")
    df = pd.read_excel(f, header=1)
    core_dfs.append(df)
    print(f"    Shape: {df.shape}")
core = pd.concat(core_dfs, ignore_index=True)
print(f"Combined Core shape: {core.shape}")

# Key variables summary
result = {}

# --- H1: Income Growth Expectation ---
for v in ['Q24_cent50', 'Q24_iqr']:
    s = core[v].dropna()
    result[v] = {
        'n': len(s), 'mean': float(s.mean()), 'std': float(s.std()),
        'min': float(s.min()), 'max': float(s.max()),
        'q10': float(s.quantile(0.1)), 'q25': float(s.quantile(0.25)),
        'q50': float(s.quantile(0.5)), 'q75': float(s.quantile(0.75)),
        'q90': float(s.quantile(0.9)),
    }
    print(f"\n{v}: n={result[v]['n']}, mean={result[v]['mean']:.3f}, "
          f"std={result[v]['std']:.3f}, median={result[v]['q50']:.3f}")

# --- H2: Labor Fragility ---
for v in ['Q13new', 'Q22new']:
    s = core[v].dropna()
    result[v] = {
        'n': len(s), 'mean': float(s.mean()), 'std': float(s.std()),
        'min': float(s.min()), 'max': float(s.max()),
        'q10': float(s.quantile(0.1)), 'q25': float(s.quantile(0.25)),
        'q50': float(s.quantile(0.5)), 'q75': float(s.quantile(0.75)),
        'q90': float(s.quantile(0.9)),
    }
    print(f"\n{v}: n={result[v]['n']}, mean={result[v]['mean']:.3f}, "
          f"std={result[v]['std']:.3f}, median={result[v]['q50']:.3f}")

# --- Demographics ---
for v in ['_AGE_CAT', '_EDU_CAT', '_HH_INC_CAT']:
    vc = core[v].dropna().value_counts(normalize=True)
    result[v] = {k: float(v_) for k, v_ in vc.items()}
    print(f"\n{v} proportions: {result[v]}")

# --- H3: Liquidity (Q33 = 1/2 binary, Q47 is scale) ---
for v in ['Q33']:
    s = core[v].dropna()
    vc = s.value_counts(normalize=True)
    result[v] = {str(k): float(v_) for k, v_ in vc.items()}
    print(f"\n{v} proportions: {result[v]}")

# --- H5: Housing (Q41 looks like continuous - need to understand encoding) ---
# Use _HH_INC_CAT and other categoricals for now

# Save core distributions
with open('Phase2_Output/core_distributions.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
print("\nCore distributions saved.")

# ============================================================
# 2. LABOR MARKET SURVEY
# ============================================================
print("\n\nLoading LM Survey data...")
lm = pd.read_excel('SCE_Data/02_Labor_Market_Survey/sce-labor-microdata-public.xlsx',
                    sheet_name='Data', header=1)
print(f"LM shape: {lm.shape}")
print(f"LM columns (first 30): {list(lm.columns[:30])}")

lm_result = {}
# Check for reservation wage and search variables
rw_cols = [c for c in lm.columns if 'rw' in c.lower() or 'reserv' in c.lower()]
js_cols = [c for c in lm.columns if 'js' in c.lower() or 'search' in c.lower()]
print(f"\nReservation wage columns: {rw_cols[:20]}")
print(f"Job search columns: {js_cols[:20]}")

for v in rw_cols[:5] + js_cols[:5]:
    s = lm[v].dropna()
    if len(s) > 0 and s.dtype in ['float64', 'int64']:
        lm_result[v] = {
            'n': len(s), 'mean': float(s.mean()), 'std': float(s.std()),
            'q50': float(s.quantile(0.5)),
        }
        print(f"  {v}: n={len(s)}, mean={s.mean():.3f}")

with open('Phase2_Output/lm_distributions.json', 'w') as f:
    json.dump(lm_result, f, indent=2, default=str)

# ============================================================
# 3. HOUSEHOLD SPENDING SURVEY
# ============================================================
print("\n\nLoading Spending Survey data...")
sp = pd.read_excel('SCE_Data/06_Household_Spending/sce-household-spending-microdata.xlsx',
                    header=1)
print(f"Spending shape: {sp.shape}")

sp_cols_mpc = [c for c in sp.columns if 'qsp12' in c.lower() or 'qsp13' in c.lower()]
print(f"MPC columns: {sp_cols_mpc}")

sp_result = {}
for v in sp_cols_mpc:
    s = sp[v].dropna()
    if len(s) > 0 and s.dtype in ['float64', 'int64']:
        sp_result[v] = {
            'n': len(s), 'mean': float(s.mean()), 'std': float(s.std()),
            'min': float(s.min()), 'max': float(s.max()),
            'q50': float(s.quantile(0.5)),
        }
        print(f"  {v}: n={len(s)}, mean={s.mean():.3f}")

with open('Phase2_Output/spending_distributions.json', 'w') as f:
    json.dump(sp_result, f, indent=2, default=str)

# ============================================================
# 4. LM QUARTERLY (reservation wage, search hours)
# ============================================================
print("\n\nLoading LM Quarterly data...")
lmq = pd.read_excel('SCE_Data/02_Labor_Market_Survey/SCE-Public-LM-Quarterly-Microdata.xlsx',
                     sheet_name='Data', header=1)
print(f"LM Quarterly shape: {lmq.shape}")
print(f"LM Quarterly columns: {list(lmq.columns[:30])}")

lmq_rw = [c for c in lmq.columns if 'rw' in c.lower()]
lmq_js = [c for c in lmq.columns if 'js' in c.lower()]
print(f"RW cols: {lmq_rw[:15]}")
print(f"JS cols: {lmq_js[:15]}")

lmq_result = {}
for v in lmq_rw[:10] + lmq_js[:10]:
    s = lmq[v].dropna()
    if len(s) > 0 and s.dtype in ['float64', 'int64']:
        lmq_result[v] = {
            'n': len(s), 'mean': float(s.mean()), 'std': float(s.std()),
            'q50': float(s.quantile(0.5)),
        }
        print(f"  {v}: n={len(s)}, mean={s.mean():.3f}")

with open('Phase2_Output/lmq_distributions.json', 'w') as f:
    json.dump(lmq_result, f, indent=2, default=str)

print("\n\n=== DATA EXPLORATION COMPLETE ===")
