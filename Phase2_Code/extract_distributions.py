"""
Phase 2 - Extract all empirical distributions needed for population initialization.
Outputs: Phase2_Output/empirical_distributions.json
"""
import pandas as pd
import numpy as np
import json, os

os.makedirs('Phase2_Output', exist_ok=True)
dist = {}

# ============================================================
# 1. CORE SURVEY
# ============================================================
print("Loading Core Survey (3 files)...")
core_dfs = []
for f in [
    'SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-13-16.xlsx',
    'SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-17-19.xlsx',
    'SCE_Data/01_Core_Survey/FRBNY-SCE-Public-Microdata-Complete-20-present.xlsx',
]:
    core_dfs.append(pd.read_excel(f, header=1))
core = pd.concat(core_dfs, ignore_index=True)
print(f"  Core combined: {core.shape}")

def continuous_stats(series, name):
    s = series.dropna()
    return {
        'n': int(len(s)), 'mean': float(s.mean()), 'std': float(s.std()),
        'min': float(s.min()), 'max': float(s.max()),
        'percentiles': {str(p): float(s.quantile(p))
                        for p in [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]},
    }

def categorical_stats(series, name):
    s = series.dropna()
    vc = s.value_counts(normalize=True).sort_index()
    return {'n': int(len(s)), 'proportions': {str(k): float(v) for k, v in vc.items()}}

# --- Demographics ---
dist['age_cat'] = categorical_stats(core['_AGE_CAT'], 'age_cat')
dist['edu_cat'] = categorical_stats(core['_EDU_CAT'], 'edu_cat')
dist['income_cat'] = categorical_stats(core['_HH_INC_CAT'], 'income_cat')

# --- H1: Income Growth Expectation ---
dist['Q24_cent50'] = continuous_stats(core['Q24_cent50'], 'Q24_cent50')
dist['Q24_iqr'] = continuous_stats(core['Q24_iqr'], 'Q24_iqr')

# Conditional: Q24_cent50 by income category
for cat in core['_HH_INC_CAT'].dropna().unique():
    mask = core['_HH_INC_CAT'] == cat
    key = f'Q24_cent50|income={cat}'
    dist[key] = continuous_stats(core.loc[mask, 'Q24_cent50'], key)

# --- H2: Labor Fragility ---
dist['Q13new'] = continuous_stats(core['Q13new'], 'Q13new')
dist['Q22new'] = continuous_stats(core['Q22new'], 'Q22new')

# Fragility index: Q13new + (100-Q22new), both 0-100
frag_data = core[['Q13new', 'Q22new']].dropna()
frag_index = (frag_data['Q13new'] / 100 + (100 - frag_data['Q22new']) / 100) / 2
dist['labor_fragility_index'] = continuous_stats(frag_index, 'labor_fragility')

# --- H3: Liquidity Fragility ---
# Q33: 1=yes can cover 3mo, 2=no
dist['Q33'] = categorical_stats(core['Q33'], 'Q33')

# --- H5: Housing ---
# Check Q41 encoding
dist['Q41'] = categorical_stats(core['Q41'] if 'Q41' in core.columns else pd.Series(), 'Q41')

print("Core extraction done.")

# ============================================================
# 2. LM SURVEY (Annual Microdata)
# ============================================================
print("\nLoading LM Survey...")
lm = pd.read_excel('SCE_Data/02_Labor_Market_Survey/sce-labor-microdata-public.xlsx',
                    sheet_name='Data', header=1)
print(f"  LM shape: {lm.shape}")

# rw2a: reservation wage (dollar amount), rw2b: frequency (1=hourly,2=weekly,3=biweekly,4=monthly,5=annual)
# Normalize all to annual
rw = lm[['rw2a', 'rw2b']].dropna()
multipliers = {1: 2080, 2: 52, 3: 26, 4: 12, 5: 1}
rw['rw2_annual'] = rw.apply(lambda r: r['rw2a'] * multipliers.get(r['rw2b'], 1), axis=1)
# Filter reasonable range (5k-500k annual)
rw_clean = rw[(rw['rw2_annual'] >= 5000) & (rw['rw2_annual'] <= 500000)]
dist['reservation_wage_annual'] = continuous_stats(rw_clean['rw2_annual'], 'rw_annual')

# js7: search hours per week
dist['js7_search_hours'] = continuous_stats(lm['js7'], 'js7')

print("LM extraction done.")

# ============================================================
# 3. LM QUARTERLY (reservation wage detail)
# ============================================================
print("\nLoading LM Quarterly...")
lmq = pd.read_excel('SCE_Data/02_Labor_Market_Survey/SCE-Public-LM-Quarterly-Microdata.xlsx',
                     sheet_name='Data', header=0)
print(f"  LMQ shape: {lmq.shape}")
print(f"  LMQ columns (first 30): {list(lmq.columns[:30])}")

# Check for rw and js columns
rw_cols = [c for c in lmq.columns if isinstance(c, str) and 'rw' in c.lower()]
js_cols = [c for c in lmq.columns if isinstance(c, str) and 'js' in c.lower()]
print(f"  RW cols: {rw_cols[:10]}")
print(f"  JS cols: {js_cols[:10]}")

for v in rw_cols[:5]:
    s = lmq[v].dropna()
    if len(s) > 0 and np.issubdtype(s.dtype, np.number):
        dist[f'lmq_{v}'] = continuous_stats(s, v)

print("LMQ extraction done.")

# ============================================================
# 4. HOUSEHOLD SPENDING
# ============================================================
print("\nLoading Spending Survey...")
sp = pd.read_excel('SCE_Data/06_Household_Spending/sce-household-spending-microdata.xlsx', header=1)
print(f"  Spending shape: {sp.shape}")

# qsp12n: 1-7 scale for positive income shock MPC
# qsp13new: 1-7 scale for negative income shock MPC
dist['qsp12n'] = categorical_stats(sp['qsp12n'], 'qsp12n')
dist['qsp13new'] = categorical_stats(sp['qsp13new'], 'qsp13new')

# qsp12a (allocation of extra spending): percentages
for v in ['qsp12a_1', 'qsp12a_2', 'qsp12a_3']:
    if v in sp.columns:
        dist[v] = continuous_stats(sp[v], v)

# qsp13a (allocation of cut spending): percentages
for v in ['qsp13a_1', 'qsp13a_2', 'qsp13a_3']:
    if v in sp.columns:
        dist[v] = continuous_stats(sp[v], v)

print("Spending extraction done.")

# ============================================================
# 5. HOUSING SURVEY
# ============================================================
print("\nLoading Housing Survey...")
hfiles = [f for f in os.listdir('SCE_Data/05_Housing') if 'microdata' in f.lower() and f.endswith('.xlsx')]
print(f"  Housing files: {hfiles}")
if hfiles:
    h = pd.read_excel(f'SCE_Data/05_Housing/{hfiles[0]}', header=1, nrows=5)
    hcols = [c for c in h.columns if isinstance(c, str) and ('hq' in c.lower() or 'own' in c.lower() or 'rent' in c.lower())]
    print(f"  Housing columns (HQ related): {hcols[:20]}")

print("\n=== ALL EXTRACTIONS COMPLETE ===")
# Save
with open('Phase2_Output/empirical_distributions.json', 'w') as f:
    json.dump(dist, f, indent=2, default=str)
print(f"Saved {len(dist)} distribution entries to Phase2_Output/empirical_distributions.json")
