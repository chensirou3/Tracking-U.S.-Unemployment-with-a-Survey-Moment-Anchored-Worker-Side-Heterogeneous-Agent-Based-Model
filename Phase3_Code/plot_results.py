"""
Phase 3 - Plot first stable run results.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs('Phase3_Output/figures', exist_ok=True)

# Load results
baseline = dict(np.load('Phase3_Output/run_baseline.npz'))
recession = dict(np.load('Phase3_Output/run_recession.npz'))

T = len(baseline['unemployment_rate'])
months = np.arange(T)

fig, axes = plt.subplots(3, 2, figsize=(14, 12))
fig.suptitle('Phase 3: First Stable Run — Key Aggregate Series', fontsize=14)

# --- Panel 1: Unemployment Rate ---
ax = axes[0, 0]
ax.plot(months, baseline['unemployment_rate'] * 100, 'b-', label='Baseline')
ax.plot(months, recession['unemployment_rate'] * 100, 'r-', label='Recession')
ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Core: Unemployment Rate')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Panel 2: LFPR ---
ax = axes[0, 1]
ax.plot(months, baseline['lfpr'] * 100, 'b-', label='Baseline')
ax.plot(months, recession['lfpr'] * 100, 'r-', label='Recession')
ax.set_ylabel('LFPR (%)')
ax.set_title('Labor Force Participation Rate')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Panel 3: EPOP ---
ax = axes[1, 0]
ax.plot(months, baseline['epop'] * 100, 'b-', label='Baseline')
ax.plot(months, recession['epop'] * 100, 'r-', label='Recession')
ax.set_ylabel('EPOP (%)')
ax.set_title('Employment-Population Ratio')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Panel 4: Transition Rates ---
ax = axes[1, 1]
ax.plot(months, baseline['eu_rate'] * 100, 'b-', label='E→U (Baseline)')
ax.plot(months, recession['eu_rate'] * 100, 'r-', label='E→U (Recession)')
ax.plot(months, baseline['ue_rate'] * 100, 'b--', label='U→E (Baseline)')
ax.plot(months, recession['ue_rate'] * 100, 'r--', label='U→E (Recession)')
ax.set_ylabel('Rate (%)')
ax.set_title('Transition Rates')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Panel 5: Avg Cash Buffer ---
ax = axes[2, 0]
ax.plot(months, baseline['avg_cash_buffer'], 'b-', label='Baseline')
ax.plot(months, recession['avg_cash_buffer'], 'r-', label='Recession')
ax.set_ylabel('Months')
ax.set_title('Average Cash Buffer')
ax.set_xlabel('Month')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Panel 6: Search Intensity + H2M Share ---
ax = axes[2, 1]
ax2 = ax.twinx()
ln1 = ax.plot(months, baseline['avg_search_intensity'], 'b-', label='Search (Baseline)')
ln2 = ax.plot(months, recession['avg_search_intensity'], 'r-', label='Search (Recession)')
ln3 = ax2.plot(months, baseline['h2m_share'] * 100, 'b--', alpha=0.5, label='H2M% (Baseline)')
ln4 = ax2.plot(months, recession['h2m_share'] * 100, 'r--', alpha=0.5, label='H2M% (Recession)')
ax.set_ylabel('Search Intensity (hrs/wk)')
ax2.set_ylabel('H2M Share (%)')
ax.set_title('Search Intensity & H2M Share')
ax.set_xlabel('Month')
lns = ln1 + ln2 + ln3 + ln4
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, fontsize=7)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Phase3_Output/figures/first_stable_run.png', dpi=150, bbox_inches='tight')
print("Figure saved to Phase3_Output/figures/first_stable_run.png")
plt.close()

# Additional: Fragility and Debt Stress
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle('Phase 3: Household Support Indicators', fontsize=13)

ax = axes2[0]
ax.plot(months, baseline['avg_fragility'], 'b-', label='Baseline')
ax.plot(months, recession['avg_fragility'], 'r-', label='Recession')
ax.set_ylabel('Labor Fragility')
ax.set_title('Average Labor Fragility')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes2[1]
ax.plot(months, baseline['avg_debt_stress'], 'b-', label='Baseline')
ax.plot(months, recession['avg_debt_stress'], 'r-', label='Recession')
ax.set_ylabel('Debt Stress')
ax.set_title('Average Debt Stress')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Phase3_Output/figures/household_indicators.png', dpi=150, bbox_inches='tight')
print("Figure saved to Phase3_Output/figures/household_indicators.png")
plt.close()

print("\nAll figures generated.")
