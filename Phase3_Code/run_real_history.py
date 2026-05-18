"""
Run simulation with real FRED historical data (2001-01 to 2026-02, 302 months).
Compare model-generated unemployment dynamics against actual environment.
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.scheduler import Simulation
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config

os.makedirs('Phase3_Output/figures', exist_ok=True)

# Build real environment
print("Loading real historical environment from FRED data...")
env = RealEnvironment(data_dir='Phase3_Data', start='2001-01', end='2026-02')
env.summary()

# Run simulation
print(f"\nRunning simulation: {env.T} months, 100,000 agents, all mechanisms ON")
sim = Simulation(
    population_path='Phase2_Output/population_v1.npz',
    config=default_config(),
    seed=42,
    env_override=env,
)
history = sim.run(verbose=True)

# Extract key series
T = len(history)
months = np.arange(T)
dates = env.dates
ur = np.array([h['unemployment_rate'] for h in history])
lfpr = np.array([h['lfpr'] for h in history])
epop = np.array([h['epop'] for h in history])
eu_rate = np.array([h['eu_rate'] for h in history])
ue_rate = np.array([h['ue_rate'] for h in history])
h2m_share = np.array([h['h2m_share'] for h in history])
avg_buf = np.array([h['avg_cash_buffer'] for h in history])
avg_frag = np.array([h['avg_fragility'] for h in history])
avg_search = np.array([h['avg_search_intensity'] for h in history])
avg_dur = np.array([h['avg_unemp_dur'] for h in history])

# Save data
result = {k: np.array([h[k] for h in history]) for k in history[0].keys()}
result['dates'] = np.array(dates[:T])
result['env_market_tightness'] = env.market_tightness[:T]
result['env_separation_rate'] = env.separation_rate[:T]
result['env_income_growth'] = env.income_growth_bg[:T]
np.savez_compressed('Phase3_Output/run_real_history.npz', **result)

# Print summary by era
eras = [
    ('2001-2003 Recession', 0, 36),
    ('2004-2006 Recovery', 36, 72),
    ('2007-2009 GFC', 72, 108),
    ('2010-2014 Recovery', 108, 168),
    ('2015-2019 Expansion', 168, 228),
    ('2020-2021 COVID', 228, 252),
    ('2022-2026 Post-COVID', 252, T),
]
print(f"\n{'Era':<25s} {'UR_mean':>8s} {'UR_peak':>8s} {'LFPR':>8s} {'EPOP':>8s}")
print("-" * 60)
for name, s, e in eras:
    e = min(e, T)
    if s >= T:
        continue
    print(f"{name:<25s} {ur[s:e].mean()*100:7.1f}% {ur[s:e].max()*100:7.1f}% "
          f"{lfpr[s:e].mean()*100:7.1f}% {epop[s:e].mean()*100:7.1f}%")

# ========== PLOTTING ==========
# X-axis: use year labels
tick_positions = [i for i, d in enumerate(dates[:T]) if d.endswith('-01') and int(d[:4]) % 2 == 1]
tick_labels = [dates[i][:4] for i in tick_positions]

fig, axes = plt.subplots(4, 2, figsize=(16, 16))
fig.suptitle('Real Historical Run: 2001-01 to 2026-02 (302 months)', fontsize=14)

# Panel 1: Unemployment Rate
ax = axes[0, 0]
ax.plot(months, ur * 100, 'b-', lw=1.5, label='Model UR')
ax.set_ylabel('Unemployment Rate (%)')
ax.set_title('Unemployment Rate (Model)')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.grid(True, alpha=0.3); ax.legend()

# Panel 2: Environment inputs
ax = axes[0, 1]
ax2 = ax.twinx()
ax.plot(months, env.market_tightness[:T], 'g-', lw=1, label='Market Tightness')
ax2.plot(months, env.separation_rate[:T] * 100, 'r-', lw=1, label='Sep Rate (%)')
ax.set_ylabel('Market Tightness', color='g')
ax2.set_ylabel('Separation Rate (%)', color='r')
ax.set_title('Environment Inputs (FRED)')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.legend(loc='upper left', fontsize=8); ax2.legend(loc='upper right', fontsize=8)

# Panel 3: LFPR
ax = axes[1, 0]
ax.plot(months, lfpr * 100, 'b-', lw=1.5)
ax.set_ylabel('LFPR (%)'); ax.set_title('Labor Force Participation Rate')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.grid(True, alpha=0.3)

# Panel 4: EPOP
ax = axes[1, 1]
ax.plot(months, epop * 100, 'b-', lw=1.5)
ax.set_ylabel('EPOP (%)'); ax.set_title('Employment-Population Ratio')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.grid(True, alpha=0.3)

# Panel 5: Transition rates
ax = axes[2, 0]
ax.plot(months, eu_rate * 100, 'r-', lw=1, label='E->U')
ax.plot(months, ue_rate * 100, 'g-', lw=1, label='U->E')
ax.set_ylabel('Rate (%)'); ax.set_title('Transition Rates')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.legend(); ax.grid(True, alpha=0.3)

# Panel 6: Avg unemployment duration
ax = axes[2, 1]
ax.plot(months, avg_dur, 'b-', lw=1.5)
ax.set_ylabel('Months'); ax.set_title('Avg Unemployment Duration')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.grid(True, alpha=0.3)

# Panel 7: Fragility and Search
ax = axes[3, 0]
ax.plot(months, avg_frag, 'r-', lw=1.5, label='Avg Fragility')
ax.set_ylabel('Fragility [0,1]'); ax.set_title('Average Labor Fragility')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.legend(); ax.grid(True, alpha=0.3)

# Panel 8: H2M share and buffer
ax = axes[3, 1]
ax2 = ax.twinx()
ax.plot(months, h2m_share * 100, 'r-', lw=1.5, label='H2M Share (%)')
ax2.plot(months, avg_buf, 'b-', lw=1, alpha=0.7, label='Avg Buffer (mo)')
ax.set_ylabel('H2M Share (%)', color='r')
ax2.set_ylabel('Avg Buffer (months)', color='b')
ax.set_title('Liquidity Indicators')
ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels, fontsize=8)
ax.legend(loc='upper left', fontsize=8); ax2.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('Phase3_Output/figures/real_history_run.png', dpi=150, bbox_inches='tight')
print("\nFigure saved to Phase3_Output/figures/real_history_run.png")
print("\n=== REAL HISTORICAL RUN COMPLETE ===")
