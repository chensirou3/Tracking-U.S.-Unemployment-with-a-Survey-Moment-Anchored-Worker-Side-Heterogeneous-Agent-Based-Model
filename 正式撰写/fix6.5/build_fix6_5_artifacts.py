"""
Synthesize revised §6.5 robustness artefacts.

Inputs (read-only, no new simulations):
  正式撰写/fix6.1/tables/table1_regime_summary.csv         (regime decomposition)
  正式撰写/fix6.2/tables/table1_variant_summary.csv         (recalibrated controls)
  正式撰写/fix6.2/tables/table6_old_vs_new_decomposition.csv
  正式撰写/fix6.2/tables/table7_regime_x_variant.csv
  正式撰写/fix6.3/tables/table2_post_covid_ablation.csv     (recalibrated ablation)
  正式撰写/fix6.3/tables/table5_old_vs_new_delta.csv
  正式撰写/fix6.4/tables/table1_main_postcovid_benchmark.csv (stronger benchmarks)
  正式撰写/fix6.4/tables/table2_regime_specific.csv
  正式撰写/6.5/robustness_metrics.json                       (legacy Phase 7 / Pkgs A-E)

Outputs:
  tables/table1_revised_robustness_summary.csv  (10 dim × supports/caveat)
  tables/table2_old_vs_revised_claims.csv       (6 claim families)
  tables/table3_paper_ready_compact.csv         (6 findings × number × interp)
  figures/fig1_revised_dashboard.png            (4-panel summary)
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
TBL = BASE / 'tables'; TBL.mkdir(exist_ok=True)
FIG = BASE / 'figures'; FIG.mkdir(exist_ok=True)

R1 = pd.read_csv(ROOT / 'fix6.1' / 'tables' / 'table1_regime_summary.csv')
R2 = pd.read_csv(ROOT / 'fix6.2' / 'tables' / 'table1_variant_summary.csv')
R2_old_new = pd.read_csv(ROOT / 'fix6.2' / 'tables' / 'table6_old_vs_new_decomposition.csv')
R2_reg = pd.read_csv(ROOT / 'fix6.2' / 'tables' / 'table7_regime_x_variant.csv')
R3 = pd.read_csv(ROOT / 'fix6.3' / 'tables' / 'table2_post_covid_ablation.csv')
R3_delta = pd.read_csv(ROOT / 'fix6.3' / 'tables' / 'table5_old_vs_new_delta.csv')
R4 = pd.read_csv(ROOT / 'fix6.4' / 'tables' / 'table1_main_postcovid_benchmark.csv')
R4_reg = pd.read_csv(ROOT / 'fix6.4' / 'tables' / 'table2_regime_specific.csv')
LEG = json.load(open(ROOT / '6.5' / 'robustness_metrics.json', encoding='utf-8'))


def get_R1(window, key):
    return float(R1.loc[R1['window'] == window, key].iloc[0])


# ---------------------------------------------------------------------------
# Table 1 — revised robustness summary (10 rows)
# ---------------------------------------------------------------------------
rows_t1 = [
    {'dimension': 'Regime decomposition (revised §6.1)',
     'key_result': f"post-COVID 0.221 pp; COVID crisis 2.82 pp; pre-COVID 0.79 pp",
     'supports': 'post-COVID tracking only',
     'caveat': 'crisis under-prediction (-2.07 pp); pre-COVID is +0.77 pp bias'},
    {'dimension': 'Re-calibrated controls (revised §6.2)',
     'key_result': 'Full 0.273 pp; LaborOnly 0.363; Homog 0.545; Simplified 0.562',
     'supports': 'Full best on post-COVID after separate recalibration',
     'caveat': 'gap shrinks from 2.116 → 0.288 pp vs OLD shared-param controls'},
    {'dimension': 'Re-calibrated ablation (revised §6.3)',
     'key_result': 'No-Search +0.812 pp; No-Liq +0.105; No-Hous −0.036; No-SLH +0.429',
     'supports': 'Search Friction is the only robust standalone dimension',
     'caveat': 'Liq/Hous gaps largely close; sign flips on Housing/Consumption'},
    {'dimension': 'Stronger benchmarks (revised §6.4, dynamic post-COVID)',
     'key_result': 'ABM 0.273; no-change 0.309; ETS 0.309; Beveridge 0.422',
     'supports': 'ABM rank 1 in post-COVID dynamic by 0.036 pp',
     'caveat': 'margin within seed s.d. (±0.023 pp); rank 3/7 in other regimes'},
    {'dimension': 'Multi-seed dispersion (legacy R1)',
     'key_result': 'Phase 6 baseline UR RMSE CV 3.08% (0.221 ± 0.007 pp)',
     'supports': 'simulation noise is small in absolute pp',
     'caveat': '§6.2 recalibrated V_Full seed s.d. is 0.023 pp; margin vs no-change ≈ s.d.'},
    {'dimension': 'Training-window sensitivity (legacy Pkg A)',
     'key_result': 'M0 OOS RMSE 0.245 ± 0.011 pp on 7 OOS-aligned splits',
     'supports': 'ranking and OOS RMSE band stable to train-window choice',
     'caveat': 'computed on legacy M0 (not recalibrated controls); ranking re-statement only'},
    {'dimension': 'Forecast-horizon degradation (legacy Pkg B)',
     'key_result': 'M0 log-log RMSE slope −0.092 (shallowest of 8 models)',
     'supports': 'no horizon explosion up to h = 36',
     'caveat': 'used legacy benchmarks (AR/VAR/Beveridge/DMP); stronger benchmarks not re-run'},
    {'dimension': 'Agent-count plateau (legacy Pkg D)',
     'key_result': '|ΔRMSE|<0.015 pp at N≥50k; default N=100k past plateau',
     'supports': 'agent count is not a tuning lever for the headline',
     'caveat': 'invariant property of M0 class; applies to recalibrated runs as well'},
    {'dimension': 'Calibration-method sensitivity (legacy Pkg E)',
     'key_result': 'best-test UR RMSE 0.214–0.243 pp across 5 methods (CV 5.55%)',
     'supports': 'predictive performance band is method-invariant',
     'caveat': 'band centred on legacy 0.22 pp, not the recalibrated 0.273 pp'},
    {'dimension': 'Parameter weak identification (legacy Pkg A/E)',
     'key_result': '0/14 params drift across 10 splits BUT 10/14 weakly identified across methods',
     'supports': 'priors are stable within method; predictions stable across methods',
     'caveat': '*individual* structural parameters not pinned down; report as bands'},
]
pd.DataFrame(rows_t1).to_csv(TBL / 'table1_revised_robustness_summary.csv', index=False)
print('table1 saved')

# ---------------------------------------------------------------------------
# Table 2 — old claim vs revised claim (6 rows)
# ---------------------------------------------------------------------------
rows_t2 = [
    {'claim_family': 'Broad OOS prediction',
     'old_claim': 'ABM predicts U-3 OOS at 0.21 pp RMSE (2018-2026)',
     'revised_evidence': 'Regime-decomposed: post-COVID 0.221 pp; crisis 2.82 pp; pre-COVID 0.79 pp; full 1.42 pp',
     'revised_claim': 'Strong on post-COVID normalization only; not a broad forecaster'},
    {'claim_family': 'Heterogeneity advantage',
     'old_claim': 'Heterogeneity contributes 97.6% of the OOS advantage',
     'revised_evidence': 'After separate recalibration of controls, Full−Simplified = 0.288 pp; het share = 94.2%',
     'revised_claim': 'Heterogeneity advantage survives but is one order of magnitude smaller in absolute pp'},
    {'claim_family': 'Search / Liquidity / Housing as separable mechanisms',
     'old_claim': 'Three structural mechanisms each contribute identifiable post-COVID gain',
     'revised_evidence': 'Recalibrated ablation: No-Search +0.812; No-Liq +0.105; No-Hous −0.036; No-SLH +0.429',
     'revised_claim': 'Only Search Friction is a robust standalone driver; Liq/Hous absorbed by recalibration'},
    {'claim_family': 'Benchmark superiority',
     'old_claim': 'ABM decisively beats AR/VAR/Beveridge/DMP',
     'revised_evidence': '§6.4 dynamic post-COVID: ABM 0.273 vs no-change/ETS 0.309 (0.036 pp; 13%); not best in other regimes',
     'revised_claim': 'ABM is competitive with strong univariate benchmarks in the post-COVID dynamic protocol'},
    {'claim_family': 'Cross-regime robustness',
     'old_claim': 'Performance robust across windows and seeds',
     'revised_evidence': 'Robust only on post-COVID. Crisis under-predicts -2.07 pp; pre-COVID bias +0.77 pp',
     'revised_claim': 'Robust *within the post-COVID regime*; not robust across regime transitions'},
    {'claim_family': 'Structural interpretation of parameters',
     'old_claim': '14 calibrated parameters identify underlying behavioural mechanisms',
     'revised_evidence': '10/14 weakly identified across calibration methods; ablation responds non-additively',
     'revised_claim': 'Predictive output is method-invariant; individual parameters are weakly identified bands'},
]
pd.DataFrame(rows_t2).to_csv(TBL / 'table2_old_vs_revised_claims.csv', index=False)
print('table2 saved')

# ---------------------------------------------------------------------------
# Table 3 — paper-ready compact (6 findings)
# ---------------------------------------------------------------------------
rows_t3 = [
    {'finding': 'Post-COVID normalization UR tracking',
     'number': '0.221 ± 0.007 pp (legacy baseline) / 0.273 ± 0.023 pp (recalibrated V_Full)',
     'interpretation': 'Headline tracking holds under both Phase 6 baseline and §6.2 recalibration'},
    {'finding': 'COVID crisis performance',
     'number': 'UR RMSE 2.82 pp, bias −2.07 pp, max abs 6.07 pp',
     'interpretation': 'Direction correct (corr 0.76) but magnitude not captured; crisis claim NOT supported'},
    {'finding': 'Re-calibrated controls (heterogeneity gap)',
     'number': 'Full−Simplified = 0.288 pp (was 2.116 pp under shared parameters)',
     'interpretation': 'Heterogeneity advantage survives recalibration but is much smaller'},
    {'finding': 'Re-calibrated ablation (Search Friction)',
     'number': 'No-Search Δ = +0.812 pp (only ablation that survives at >0.5 pp)',
     'interpretation': 'Search Friction is the only standalone dimension with robust ablation evidence'},
    {'finding': 'Stronger benchmark comparison (dynamic post-COVID)',
     'number': 'ABM 0.273 vs no-change/ETS 0.309 (ratio 1.13×); ABM rank 1 of 12',
     'interpretation': 'Competitive lead inside seed s.d. (±0.023 pp); not overwhelming dominance'},
    {'finding': 'Parameter weak identification',
     'number': '10/14 parameters CV ≥ 0.40 across 5 calibration methods',
     'interpretation': 'Predictions/decompositions are method-invariant; structural reads require bands'},
]
pd.DataFrame(rows_t3).to_csv(TBL / 'table3_paper_ready_compact.csv', index=False)
print('table3 saved')


# ---------------------------------------------------------------------------
# Figure 1 — 4-panel dashboard
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5))

# Panel A: regime RMSE bars (revised §6.1)
ax = axes[0, 0]
order = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm', 'full_post_2018']
labels = ['Pre-COVID\nstable', 'COVID crisis\n(Mar 2020+)', 'Post-COVID\nnormalization', 'Full\npost-2018']
vals = [get_R1(w, 'UR_RMSE_pp') for w in order]
sds = [get_R1(w, 'UR_RMSE_sd_pp') for w in order]
colors = ['#7a9cc6', '#c66666', '#6cae75', '#a07ec2']
bars = ax.bar(labels, vals, yerr=sds, capsize=4, color=colors, edgecolor='black', linewidth=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.08, f'{v:.2f}', ha='center', fontsize=9)
ax.set_ylabel('UR RMSE (pp)')
ax.set_title('A. Regime-decomposed OOS performance (revised §6.1, Phase 6 baseline)')
ax.grid(axis='y', alpha=0.3)

# Panel B: recalibrated controls vs ablation post-COVID RMSE (revised §6.2 + §6.3)
ax = axes[0, 1]
ctl = R2.set_index('variant')['UR_RMSE_post_covid_pp']
abl = R3.set_index('variant')['UR_RMSE_pp']
items = [
    ('V_Full', ctl['V_Full'], '#2b7a3d'),
    ('V_LaborOnly', ctl['V_LaborOnly'], '#7a9cc6'),
    ('V_Homog.', ctl['V_Homogeneous'], '#7a9cc6'),
    ('V_Simplified', ctl['V_Simplified'], '#7a9cc6'),
    ('—No Search', abl['V_NoSearch'], '#c66666'),
    ('—No Liq', abl['V_NoLiquidity'], '#d9a566'),
    ('—No Hous', abl['V_NoHousing'], '#d9a566'),
    ('—No SLH', abl['V_NoSLH'], '#c66666'),
]
xs = [x[0] for x in items]; ys = [x[1] for x in items]; cs = [x[2] for x in items]
bars = ax.bar(xs, ys, color=cs, edgecolor='black', linewidth=0.6)
ax.axhline(ctl['V_Full'], color='#2b7a3d', linestyle='--', linewidth=0.9, alpha=0.7)
for b, v in zip(bars, ys):
    ax.text(b.get_x() + b.get_width()/2, v + 0.02, f'{v:.2f}', ha='center', fontsize=8)
ax.set_ylabel('UR RMSE (pp), post-COVID')
ax.set_title('B. Recalibrated controls (§6.2) & ablation (§6.3)')
ax.tick_params(axis='x', labelsize=8, rotation=30)
ax.grid(axis='y', alpha=0.3)

# Panel C: stronger benchmark comparison (revised §6.4 post-COVID dynamic)
ax = axes[1, 0]
sub = R4.dropna(subset=['UR_RMSE_pp']).sort_values('UR_RMSE_pp')
sub = sub[sub['UR_RMSE_pp'] < 3.0]  # drop drift outlier for legibility
names = sub['model'].str.replace('ABM_Full_recalibrated', 'ABM (recal.)').str.replace(r'^B\d[a-c]?_', '', regex=True)
colors = ['#2b7a3d' if 'ABM' in m else '#7a9cc6' for m in sub['model']]
bars = ax.barh(names, sub['UR_RMSE_pp'], color=colors, edgecolor='black', linewidth=0.6)
for b, v in zip(bars, sub['UR_RMSE_pp']):
    ax.text(v + 0.02, b.get_y() + b.get_height()/2, f'{v:.2f}', va='center', fontsize=8)
ax.invert_yaxis()
ax.set_xlabel('UR RMSE (pp)')
ax.set_title('C. Stronger benchmarks — dynamic, post-COVID (§6.4)')
ax.grid(axis='x', alpha=0.3)

# Panel D: legacy invariants summary text
ax = axes[1, 1]; ax.axis('off')
phase7 = LEG['phase7_robustness']
text_lines = [
    'D. Legacy robustness invariants (Phase 6 baseline)',
    '',
    f"  Multi-seed CV (5 seeds):           3.08% (0.221 ± 0.007 pp)",
    f"  Init-window {{24,36,48}} range:      0.000 pp (identical)",
    f"  Loss-weight tier-2 (3,5,7):        Δ = 0.000",
    '',
    f"  Pkg A train-window (10 splits):    0.245 ± 0.011 pp; 10/10 vs Beveridge",
    f"  Pkg A parameter drift:             0/14 (CV ≥ 0.30)",
    f"  Pkg B horizon slope (M0):          −0.092 (shallowest of 8 models)",
    f"  Pkg D agent count plateau:         |ΔRMSE|<0.015 pp at N ≥ 50k",
    f"  Pkg E calibration-method CV:       5.55%  (range 0.214–0.243 pp)",
    f"  Pkg E parameter weak ID:           10/14 (top-5 CV ≥ 0.40)",
    '',
    '  Status: ROBUST within the post-COVID regime;',
    '          parameter-level identification weak (predictions invariant).',
]
for i, line in enumerate(text_lines):
    weight = 'bold' if i == 0 else 'normal'
    ax.text(0.02, 0.97 - i*0.065, line, fontsize=9.5, family='monospace',
            transform=ax.transAxes, va='top', fontweight=weight)

fig.suptitle('§6.5 Revised Robustness Synthesis — dashboard', fontsize=13, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(FIG / 'fig1_revised_dashboard.png', dpi=130)
plt.close(fig)
print('fig1 saved')
print('done.')
