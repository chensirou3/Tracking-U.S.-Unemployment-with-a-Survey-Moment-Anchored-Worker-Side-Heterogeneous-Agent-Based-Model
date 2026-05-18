"""
Phase 2 - Population Diagnostics
Validates marginal distributions, joint structures, and illegal values.
"""
import numpy as np
from scipy import stats
import json
import os

os.makedirs('Phase2_Output', exist_ok=True)

# Load population
pop = np.load('Phase2_Output/population_v1.npz')
st = pop['static_traits']
cs = pop['category_states']
ds = pop['dynamic_states']
bp = pop['behavior_params']
N = st.shape[0]

# Constants
ST_AGE, ST_EDUCATION, ST_MARITAL, ST_HH_SIZE = 0, 1, 2, 3
CS_EMPLOYMENT, CS_LIQUIDITY_TYPE, CS_HOUSING_STATUS, CS_CONSUMPTION_TYPE = 0, 1, 2, 3
DS_INCOME_EXP, DS_INCOME_UNC, DS_LABOR_FRAG, DS_CASH_BUFFER = 0, 1, 2, 3
DS_SEARCH_INT, DS_MOBILITY_FRIC, DS_HH_INCOME, DS_UNEMP_DUR, DS_DEBT_STRESS = 4, 5, 6, 7, 8
BP_MPC_POS, BP_MPC_NEG, BP_ASYMMETRY, BP_RESV_WAGE, BP_FLEXIBILITY = 0, 1, 2, 3, 4

report = []
report.append("# Population Diagnostic Report\n")
report.append(f"N = {N}\n")

# ============================================================
# 1. MARGINAL DISTRIBUTIONS
# ============================================================
report.append("\n## 1. Marginal Distributions\n")

# Age
ages = st[:, ST_AGE]
age_u40 = (ages < 40).mean()
age_40_60 = ((ages >= 40) & (ages <= 60)).mean()
age_60p = (ages > 60).mean()
report.append(f"### Age: <40={age_u40:.3f}(target:0.277), 40-60={age_40_60:.3f}(0.391), >60={age_60p:.3f}(0.332)")

# Education
edus = st[:, ST_EDUCATION]
for e, lbl in [(0,'HS'),(1,'SomeCol'),(2,'College+')]:
    report.append(f"  Edu={lbl}: {(edus==e).mean():.3f}")

# Employment
emp = cs[:, CS_EMPLOYMENT]
for e, lbl, tgt in [(0,'E',0.60),(1,'U',0.04),(2,'N',0.36)]:
    actual = (emp==e).mean()
    status = "✅" if abs(actual - tgt) < 0.03 else "⚠️"
    report.append(f"  Employment {lbl}: {actual:.3f} (target:{tgt}) {status}")

# Housing
hsg = cs[:, CS_HOUSING_STATUS]
hsg_labels = {0:'Renter-Mobile',1:'Renter-Stable',2:'Owner-Low',3:'Owner-High'}
hsg_targets = {0:0.12,1:0.20,2:0.45,3:0.23}
for h in range(4):
    actual = (hsg==h).mean()
    report.append(f"  Housing {hsg_labels[h]}: {actual:.3f} (target:{hsg_targets[h]})")

owner_pct = ((hsg==2)|(hsg==3)).mean()
report.append(f"  Total Owner: {owner_pct:.3f} (target: ~0.66-0.68)")

# Liquidity
liq = cs[:, CS_LIQUIDITY_TYPE]
for l, lbl, tgt in [(0,'H2M',0.30),(1,'Buffer',0.45),(2,'Wealthy',0.25)]:
    actual = (liq==l).mean()
    report.append(f"  Liquidity {lbl}: {actual:.3f} (target:{tgt})")

# Consumption Type
con = cs[:, CS_CONSUMPTION_TYPE]
for c, lbl in [(0,'Saver'),(1,'Smoother'),(2,'Spender')]:
    report.append(f"  Consumption {lbl}: {(con==c).mean():.3f}")

# Continuous variables
report.append("\n### Continuous Variables\n")
continuous_checks = [
    ("income_expectation", ds[:, DS_INCOME_EXP], "mean~0.03, std~0.04"),
    ("income_uncertainty", ds[:, DS_INCOME_UNC], "mean~0.03"),
    ("labor_fragility", ds[:, DS_LABOR_FRAG], "mean~0.30, [0,1]"),
    ("cash_buffer_months", ds[:, DS_CASH_BUFFER], "H2M~0.5, Buffer~3, Wealthy~12"),
    ("search_intensity", ds[:, DS_SEARCH_INT], "U>0, E=0"),
    ("mobility_friction", ds[:, DS_MOBILITY_FRIC], "Renter<Owner"),
    ("household_income", ds[:, DS_HH_INCOME], "mean~50 ($k)"),
    ("reservation_wage", bp[:, BP_RESV_WAGE], "mean~1.0, [0.5,5.0]"),
    ("mpc_positive", bp[:, BP_MPC_POS], "mean~0.45"),
    ("mpc_negative", bp[:, BP_MPC_NEG], "mean~0.30"),
]
for name, arr, target in continuous_checks:
    report.append(f"  {name}: mean={arr.mean():.4f}, std={arr.std():.4f}, "
                  f"min={arr.min():.4f}, max={arr.max():.4f} | target: {target}")

# ============================================================
# 2. JOINT STRUCTURE VALIDATION
# ============================================================
report.append("\n## 2. Joint Structure Validation\n")

# Relation 1: fragility × income_expectation (should be negative)
rho1, p1 = stats.spearmanr(ds[:, DS_LABOR_FRAG], ds[:, DS_INCOME_EXP])
status1 = "✅" if -0.45 < rho1 < -0.15 else "⚠️"
report.append(f"  R1: fragility × income_exp: ρ={rho1:.3f}, p={p1:.2e} {status1}")

# Relation 2: liquidity × consumption (chi-square)
ct = np.zeros((3, 3), dtype=int)
for l in range(3):
    for c in range(3):
        ct[l, c] = ((liq == l) & (con == c)).sum()
chi2, p2, _, _ = stats.chi2_contingency(ct)
report.append(f"  R2: liquidity × consumption: χ²={chi2:.1f}, p={p2:.2e} {'✅' if p2<0.001 else '⚠️'}")
report.append(f"      Cross-table:\n{ct}")

# Relation 3: housing × flexibility (owners should be less flexible)
owner_flex = bp[(hsg==2)|(hsg==3), BP_FLEXIBILITY].mean()
renter_flex = bp[(hsg==0)|(hsg==1), BP_FLEXIBILITY].mean()
status3 = "✅" if renter_flex > owner_flex else "⚠️"
report.append(f"  R3: Owner flex={owner_flex:.3f}, Renter flex={renter_flex:.3f} {status3}")

# Relation 4: housing × liquidity (chi-square)
ct4 = np.zeros((4, 3), dtype=int)
for h in range(4):
    for l in range(3):
        ct4[h, l] = ((hsg == h) & (liq == l)).sum()
chi4, p4, _, _ = stats.chi2_contingency(ct4)
report.append(f"  R4: housing × liquidity: χ²={chi4:.1f}, p={p4:.2e} {'✅' if p4<0.001 else '⚠️'}")

# Relation 5: employment × search_intensity
e_search = ds[emp == 0, DS_SEARCH_INT].mean()
u_search = ds[emp == 1, DS_SEARCH_INT].mean()
n_search = ds[emp == 2, DS_SEARCH_INT].mean()
status5 = "✅" if u_search > e_search and u_search > 5.0 else "⚠️"
report.append(f"  R5: Search: E={e_search:.2f}, U={u_search:.2f}, N={n_search:.2f} {status5}")

# ============================================================
# 3. ILLEGAL VALUE CHECKS
# ============================================================
report.append("\n## 3. Illegal Value Checks\n")
checks = [
    ("ages in [18,85]", (ages>=18).all() and (ages<=85).all()),
    ("employment in {0,1,2}", np.isin(emp, [0,1,2]).all()),
    ("liquidity in {0,1,2}", np.isin(liq, [0,1,2]).all()),
    ("housing in {0,1,2,3}", np.isin(hsg, [0,1,2,3]).all()),
    ("income_exp no NaN", not np.isnan(ds[:, DS_INCOME_EXP]).any()),
    ("fragility in [0,1]", (ds[:,DS_LABOR_FRAG]>=0).all() and (ds[:,DS_LABOR_FRAG]<=1).all()),
    ("cash_buffer >= 0", (ds[:, DS_CASH_BUFFER] >= 0).all()),
    ("search_int >= 0", (ds[:, DS_SEARCH_INT] >= 0).all()),
    ("resv_wage in [0.5,5]", (bp[:,BP_RESV_WAGE]>=0.5).all() and (bp[:,BP_RESV_WAGE]<=5.0).all()),
    ("mpc_pos in (0,1)", (bp[:,BP_MPC_POS]>0).all() and (bp[:,BP_MPC_POS]<1).all()),
    ("mpc_neg in (0,1)", (bp[:,BP_MPC_NEG]>0).all() and (bp[:,BP_MPC_NEG]<1).all()),
    ("E agents: search=0", (ds[emp==0, DS_SEARCH_INT] == 0).all()),
    ("N agents: search=0", (ds[emp==2, DS_SEARCH_INT] == 0).all()),
    ("E/N agents: unemp_dur=0", (ds[emp!=1, DS_UNEMP_DUR] == 0).all()),
]
all_pass = True
for name, passed in checks:
    status = "✅ PASS" if passed else "❌ FAIL"
    report.append(f"  {name}: {status}")
    if not passed:
        all_pass = False

# ============================================================
# SUMMARY
# ============================================================
report.append(f"\n## Summary\n")
report.append(f"All illegal value checks passed: {'✅' if all_pass else '❌'}")
report.append(f"Population ready for Stage 3: {'✅' if all_pass else '❌'}")

# Write report
report_text = "\n".join(report)
print(report_text)
with open('Phase2_Output/04_Population_Diagnostic_Report.md', 'w', encoding='utf-8') as f:
    f.write(report_text)
print(f"\nReport saved to Phase2_Output/04_Population_Diagnostic_Report.md")
