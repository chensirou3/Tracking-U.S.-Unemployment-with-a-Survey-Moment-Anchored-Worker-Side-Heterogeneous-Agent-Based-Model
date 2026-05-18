"""
Build §6.4 artifacts: 5 tables + 5 figures from
  正式撰写/fix6.4/benchmark_metrics.json
  正式撰写/fix6.4/benchmark_series.npz
  正式撰写/fix6.2/reeval_metrics.json   (for ABM V_Full rows)
  正式撰写/6.1/  + 正式撰写/6.4/         (for original-baseline ABM, optional)
"""
import os, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
BENCH = json.load(open(BASE / 'benchmark_metrics.json', encoding='utf-8'))
SERIES = np.load(BASE / 'benchmark_series.npz', allow_pickle=True)

# ABM (recalibrated, §6.2) reeval json
ABM_PATH = BASE.parent / 'fix6.2' / 'reeval_metrics.json'
ABM = json.load(open(ABM_PATH, encoding='utf-8'))

# Old baseline ABM rows (from §6.1 final report or §6.4 legacy json if present)
LEGACY_BENCH = BASE.parent / '6.4' / 'benchmark_metrics.json'

TBL = BASE / 'tables'; TBL.mkdir(exist_ok=True)
FIG = BASE / 'figures'; FIG.mkdir(exist_ok=True)

REGIMES = ['pre_covid_stable', 'covid_crisis_mar', 'post_covid_norm', 'full_post_2018']
REGIME_LABEL = {
    'pre_covid_stable':  'Pre-COVID stable (2018-01..2019-12)',
    'covid_crisis_mar':  'COVID crisis (2020-03..2021-12)',
    'post_covid_norm':   'Post-COVID normalization (2022-01..2026-02)',
    'full_post_2018':    'Full post-2018 (2018-01..2026-02)',
}
BENCHMARK_LABEL = {
    'B0a_NoChange':   'No-change (random walk)',
    'B0b_HistMean':   'Historical mean',
    'B0c_Drift':      'Drift (12m local trend)',
    'B1_AR':          'AR(p), BIC',
    'B2_ARIMA':       'ARIMA(p,d,q), AIC grid',
    'B3_ETS':         'ETS (SES/Holt/Damped, AICc)',
    'B4_VAR':         'VAR(p), BIC, UR+LFPR+EPOP',
    'B5_RidgeVAR':    'Ridge VAR(2), 5 vars (BVAR approx)',
    'B6_Beveridge':   'Beveridge OLS (vac, sep)',
    'B7_DMP':         'DMP-style (theta, sep)',
    'B8_Flow':        'Flow-based UR (sep + AR(1) f)',
}
ABM_KEYS = ['ABM_Full_recalibrated', 'ABM_Full_original']
ALL_MODELS = ABM_KEYS + list(BENCHMARK_LABEL.keys())

ABM_LABEL = {
    'ABM_Full_recalibrated':  'Full heterogeneous ABM (recalibrated, §6.2)',
    'ABM_Full_original':      'Full heterogeneous ABM (original baseline, §6.1)',
}
MODEL_LABEL = {**ABM_LABEL, **BENCHMARK_LABEL}


def abm_rmse(window, key='ur', rank=0):
    """Mean UR/LFPR/EPOP RMSE across 5 seeds at rank=0 (cand_idx=32)."""
    rows = [r for r in ABM['variants']['V_Full']['rows']
            if r['rank'] == rank and r['window'] == window]
    vals = [r[key]['rmse'] for r in rows if not np.isnan(r[key]['rmse'])]
    biases = [r[key]['bias'] for r in rows if not np.isnan(r[key]['bias'])]
    corrs = [r[key]['corr'] for r in rows if not np.isnan(r[key]['corr'])]
    maes  = [r[key]['mae']  for r in rows if not np.isnan(r[key]['mae'])]
    return {'rmse': float(np.mean(vals)) if vals else float('nan'),
            'sd':   float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            'mae':  float(np.mean(maes)) if maes else float('nan'),
            'corr': float(np.mean(corrs)) if corrs else float('nan'),
            'bias': float(np.mean(biases)) if biases else float('nan'),
            'n_seeds': len(rows)}


def bench_get(regime, proto, bench, key='ur'):
    return BENCH[regime][proto][bench].get(key, {})


# ---------------------------------------------------------------------------
# Table 1 — Main post-COVID benchmark comparison (dynamic, primary)
# ---------------------------------------------------------------------------
def table1():
    rows = []
    abm = abm_rmse('post_covid_norm', 'ur')
    rmse_abm = abm['rmse']
    rows.append(dict(
        model='ABM_Full_recalibrated',
        label=MODEL_LABEL['ABM_Full_recalibrated'],
        protocol='Dynamic (sim)', input_vars='4 macro inputs (vac, sep, earn, ffr)',
        UR_RMSE_pp=round(rmse_abm * 100, 4),
        UR_MAE_pp=round(abm['mae'] * 100, 4),
        UR_Corr=round(abm['corr'], 4),
        UR_Bias_pp=round(abm['bias'] * 100, 4),
        RMSE_ratio_vs_ABM=1.000,
        interpretation='Reference. Mean over 5 seeds at rank-0 (cand_idx=32).'
    ))
    # original-baseline ABM (from old §6.4 benchmark json, if available)
    if LEGACY_BENCH.exists():
        legacy = json.load(open(LEGACY_BENCH, encoding='utf-8'))
        # Pull ABM from legacy if recorded; else N/A
        if 'meta' in legacy and 'abm_oos_rmse_pp' in legacy['meta']:
            rmse_orig = legacy['meta']['abm_oos_rmse_pp'] / 100
        else:
            rmse_orig = float('nan')
        rows.append(dict(
            model='ABM_Full_original',
            label=MODEL_LABEL['ABM_Full_original'],
            protocol='Dynamic (sim)', input_vars='4 macro inputs',
            UR_RMSE_pp=round(rmse_orig * 100, 4) if not np.isnan(rmse_orig) else 'N/A',
            UR_MAE_pp='N/A', UR_Corr='N/A', UR_Bias_pp='N/A',
            RMSE_ratio_vs_ABM=round(rmse_orig / rmse_abm, 3) if not np.isnan(rmse_orig) else 'N/A',
            interpretation='Legacy §6.1 baseline (not separately recalibrated)'
        ))
    for b in BENCHMARK_LABEL:
        m = bench_get('post_covid_norm', 'dynamic', b)
        rows.append(dict(
            model=b, label=BENCHMARK_LABEL[b],
            protocol='Dynamic (multi-step)',
            input_vars=_inputs_of(b),
            UR_RMSE_pp=round(m['rmse'] * 100, 4),
            UR_MAE_pp=round(m['mae'] * 100, 4),
            UR_Corr=round(m['corr'], 4) if not np.isnan(m['corr']) else 'N/A',
            UR_Bias_pp=round(m['bias'] * 100, 4),
            RMSE_ratio_vs_ABM=round(m['rmse'] / rmse_abm, 3),
            interpretation=_interpret(m['rmse'], rmse_abm, m.get('corr'))
        ))
    df = pd.DataFrame(rows)
    df.to_csv(TBL / 'table1_main_postcovid_benchmark.csv', index=False)
    print("table1 saved")
    return df


def _inputs_of(b):
    if b in ('B0a_NoChange', 'B0b_HistMean', 'B0c_Drift', 'B1_AR', 'B2_ARIMA', 'B3_ETS'):
        return 'UNRATE only'
    if b == 'B4_VAR':
        return 'UNRATE, CIVPART, EMRATIO'
    if b == 'B5_RidgeVAR':
        return 'UNRATE, CIVPART, EMRATIO, vac, sep (OOS exog used)'
    if b in ('B6_Beveridge', 'B7_DMP'):
        return 'vac, sep (OOS exog used)'
    if b == 'B8_Flow':
        return 'sep (OOS exog used) + implied f from AR(1)'
    return 'N/A'


def _interpret(rmse_b, rmse_abm, corr=None):
    diff_pp = (rmse_b - rmse_abm) * 100
    if abs(diff_pp) < 0.02:
        return f'ties ABM (Δ={diff_pp:+.3f} pp)'
    if rmse_b < rmse_abm:
        return f'BEATS ABM by {-diff_pp:.3f} pp'
    return f'ABM better by {diff_pp:.3f} pp'



# ---------------------------------------------------------------------------
# Table 2 — Regime-specific results (dynamic protocol), one row per model x regime
# ---------------------------------------------------------------------------
def table2():
    rows = []
    for reg in REGIMES:
        abm = abm_rmse(reg, 'ur')
        rows.append(dict(
            regime=reg, regime_label=REGIME_LABEL[reg],
            model='ABM_Full_recalibrated', label=MODEL_LABEL['ABM_Full_recalibrated'],
            UR_RMSE_pp=round(abm['rmse'] * 100, 4),
            UR_MAE_pp=round(abm['mae'] * 100, 4),
            UR_Corr=round(abm['corr'], 4) if not np.isnan(abm['corr']) else 'N/A',
            UR_Bias_pp=round(abm['bias'] * 100, 4),
            n_seeds=abm['n_seeds'],
        ))
        for b in BENCHMARK_LABEL:
            m = bench_get(reg, 'dynamic', b)
            rows.append(dict(
                regime=reg, regime_label=REGIME_LABEL[reg],
                model=b, label=BENCHMARK_LABEL[b],
                UR_RMSE_pp=round(m['rmse'] * 100, 4),
                UR_MAE_pp=round(m['mae'] * 100, 4),
                UR_Corr=round(m['corr'], 4) if not np.isnan(m['corr']) else 'N/A',
                UR_Bias_pp=round(m['bias'] * 100, 4),
                n_seeds='—',
            ))
    df = pd.DataFrame(rows)
    df.to_csv(TBL / 'table2_regime_specific.csv', index=False)
    print("table2 saved")
    return df


# ---------------------------------------------------------------------------
# Table 3 — Model specs (orders / parameters chosen per regime)
# ---------------------------------------------------------------------------
def table3():
    rows = []
    for reg in REGIMES:
        for b in BENCHMARK_LABEL:
            spec = BENCH[reg]['dynamic'][b].get('spec', {})
            rows.append(dict(
                regime=reg, regime_label=REGIME_LABEL[reg],
                model=b, label=BENCHMARK_LABEL[b],
                spec=json.dumps(spec, default=str),
            ))
    df = pd.DataFrame(rows)
    df.to_csv(TBL / 'table3_model_specs.csv', index=False)
    print("table3 saved")
    return df


# ---------------------------------------------------------------------------
# Table 4 — Protocol comparison: dynamic vs rolling RMSE per model (post-COVID)
# ---------------------------------------------------------------------------
def table4():
    rows = []
    abm = abm_rmse('post_covid_norm', 'ur')
    rows.append(dict(
        model='ABM_Full_recalibrated', label=MODEL_LABEL['ABM_Full_recalibrated'],
        dynamic_RMSE_pp=round(abm['rmse'] * 100, 4),
        rolling_RMSE_pp='N/A (sim only)',
        delta_pp='N/A',
        note='ABM does not consume observed OOS UR for nowcasting',
    ))
    for b in BENCHMARK_LABEL:
        md = bench_get('post_covid_norm', 'dynamic', b)
        mr = bench_get('post_covid_norm', 'rolling', b)
        d = round(md['rmse'] * 100, 4)
        r = round(mr['rmse'] * 100, 4)
        rows.append(dict(
            model=b, label=BENCHMARK_LABEL[b],
            dynamic_RMSE_pp=d, rolling_RMSE_pp=r,
            delta_pp=round(d - r, 4),
            note=('rolling sees lagged UR each step' if d > r + 0.01
                  else 'multi-step degradation small'),
        ))
    df = pd.DataFrame(rows)
    df.to_csv(TBL / 'table4_protocol_comparison.csv', index=False)
    print("table4 saved")
    return df


# ---------------------------------------------------------------------------
# Table 5 — Paper-ready compact table for §6.4 (single LaTeX-friendly view)
# ---------------------------------------------------------------------------
def table5():
    """Compact: post-COVID dynamic RMSE/MAE/Corr for ABM + 11 benchmarks,
       plus full_post_2018 dynamic RMSE for robustness column."""
    rows = []
    abm_pc = abm_rmse('post_covid_norm', 'ur')
    abm_full = abm_rmse('full_post_2018', 'ur')
    rmse_abm = abm_pc['rmse']
    rows.append(dict(
        Model='Full heterogeneous ABM (recalibrated)',
        Protocol='Dynamic (sim)',
        Inputs='vac, sep, earn, ffr',
        PostCOVID_RMSE_pp=round(abm_pc['rmse'] * 100, 3),
        PostCOVID_MAE_pp=round(abm_pc['mae'] * 100, 3),
        PostCOVID_Corr=round(abm_pc['corr'], 3) if not np.isnan(abm_pc['corr']) else '—',
        Full2018_RMSE_pp=round(abm_full['rmse'] * 100, 3),
        Ratio_vs_ABM=1.000,
    ))
    for b in BENCHMARK_LABEL:
        m_pc = bench_get('post_covid_norm', 'dynamic', b)
        m_f  = bench_get('full_post_2018', 'dynamic', b)
        rows.append(dict(
            Model=BENCHMARK_LABEL[b],
            Protocol='Dynamic (multi-step)',
            Inputs=_inputs_of(b),
            PostCOVID_RMSE_pp=round(m_pc['rmse'] * 100, 3),
            PostCOVID_MAE_pp=round(m_pc['mae'] * 100, 3),
            PostCOVID_Corr=(round(m_pc['corr'], 3)
                            if not np.isnan(m_pc['corr']) else '—'),
            Full2018_RMSE_pp=round(m_f['rmse'] * 100, 3),
            Ratio_vs_ABM=round(m_pc['rmse'] / rmse_abm, 3),
        ))
    df = pd.DataFrame(rows)
    df.to_csv(TBL / 'table5_paper_ready.csv', index=False)
    print("table5 saved")
    return df


# ---------------------------------------------------------------------------
# ABM trajectory loader (from fix6.2/reeval_trajectories.npz)
# ---------------------------------------------------------------------------
ABM_TRAJ = np.load(BASE.parent / 'fix6.2' / 'reeval_trajectories.npz',
                   allow_pickle=True)
DATES_FULL = ABM_TRAJ['dates']
ABM_FULL_UR = ABM_TRAJ['V_Full_ur'][0].mean(axis=0)  # rank-0, mean over 5 seeds

REGIME_OOS = {
    'pre_covid_stable':  (204, 228),
    'covid_crisis_mar':  (230, 252),
    'post_covid_norm':   (252, 302),
    'full_post_2018':    (204, 302),
}

PLOT_COLORS = {
    'ABM':            '#1f77b4',
    'B0a_NoChange':   '#7f7f7f',
    'B0b_HistMean':   '#bcbd22',
    'B0c_Drift':      '#8c564b',
    'B1_AR':          '#ff7f0e',
    'B2_ARIMA':       '#d62728',
    'B3_ETS':         '#9467bd',
    'B4_VAR':         '#2ca02c',
    'B5_RidgeVAR':    '#17becf',
    'B6_Beveridge':   '#e377c2',
    'B7_DMP':         '#aec7e8',
    'B8_Flow':        '#ffbb78',
}


def _short(b):
    return BENCHMARK_LABEL[b].split(',')[0].split('(')[0].strip()


# ---------------------------------------------------------------------------
# Figure 1 — RMSE bar chart (post-COVID dynamic)
# ---------------------------------------------------------------------------
def fig1():
    abm = abm_rmse('post_covid_norm', 'ur')
    names = ['ABM\n(recalibrated)'] + [_short(b) for b in BENCHMARK_LABEL]
    rmses = [abm['rmse'] * 100] + [
        bench_get('post_covid_norm', 'dynamic', b)['rmse'] * 100
        for b in BENCHMARK_LABEL]
    colors = ['#1f77b4'] + [PLOT_COLORS[b] for b in BENCHMARK_LABEL]

    order = np.argsort(rmses)
    names_s = [names[i] for i in order]
    rmses_s = [rmses[i] for i in order]
    colors_s = [colors[i] for i in order]

    fig, ax = plt.subplots(figsize=(9, 5.4))
    bars = ax.bar(range(len(names_s)), rmses_s, color=colors_s,
                  edgecolor='black', linewidth=0.5)
    ax.set_xticks(range(len(names_s)))
    ax.set_xticklabels(names_s, rotation=45, ha='right', fontsize=8.5)
    ax.set_ylabel('Unemployment Rate RMSE (pp)')
    ax.set_title('Figure 1. Post-COVID normalization dynamic forecast RMSE\n'
                 '(2022-01..2026-02, sorted ascending)', fontsize=10.5)
    abm_idx = names_s.index('ABM\n(recalibrated)')
    bars[abm_idx].set_edgecolor('#d62728')
    bars[abm_idx].set_linewidth(2.0)
    for i, v in enumerate(rmses_s):
        ax.text(i, v + 0.05, f'{v:.2f}', ha='center', fontsize=7.5)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, max(rmses_s) * 1.15)
    plt.tight_layout()
    plt.savefig(FIG / 'fig1_rmse_bars_postcovid_dynamic.png', dpi=160)
    plt.close()
    print("fig1 saved")


# ---------------------------------------------------------------------------
# Figure 2 — RMSE ratio vs ABM (post-COVID dynamic)
# ---------------------------------------------------------------------------
def fig2():
    abm = abm_rmse('post_covid_norm', 'ur')
    rmse_abm = abm['rmse']
    names = [_short(b) for b in BENCHMARK_LABEL]
    ratios = [bench_get('post_covid_norm', 'dynamic', b)['rmse'] / rmse_abm
              for b in BENCHMARK_LABEL]
    colors = [PLOT_COLORS[b] for b in BENCHMARK_LABEL]
    order = np.argsort(ratios)
    names_s = [names[i] for i in order]
    ratios_s = [ratios[i] for i in order]
    colors_s = [colors[i] for i in order]

    fig, ax = plt.subplots(figsize=(9, 5.4))
    bars = ax.barh(range(len(names_s)), ratios_s, color=colors_s,
                   edgecolor='black', linewidth=0.5)
    ax.axvline(1.0, color='#d62728', linestyle='--',
               label='ABM reference (ratio = 1)')
    ax.set_yticks(range(len(names_s)))
    ax.set_yticklabels(names_s, fontsize=9)
    ax.set_xlabel('RMSE ratio (benchmark / ABM)')
    ax.set_title('Figure 2. Post-COVID RMSE ratio vs recalibrated ABM\n'
                 '(values >1 → benchmark worse than ABM)', fontsize=10.5)
    for i, v in enumerate(ratios_s):
        ax.text(v + 0.05, i, f'{v:.2f}×', va='center', fontsize=8)
    ax.legend(loc='lower right', fontsize=8.5)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / 'fig2_ratio_vs_abm.png', dpi=160)
    plt.close()
    print("fig2 saved")



# ---------------------------------------------------------------------------
# Figure 3 — Predicted vs actual UR paths (top-4 benchmarks + ABM + observed)
# ---------------------------------------------------------------------------
def fig3():
    """Post-COVID dynamic. Plot observed UR + ABM + best/worst/median benchmarks."""
    s, e = REGIME_OOS['post_covid_norm']
    dates_oos = pd.to_datetime(DATES_FULL[s:e])
    obs = SERIES['tgt_ur_full'][s:e]
    abm = ABM_FULL_UR[s:e]

    # Rank benchmarks by dynamic RMSE; take best 3 + worst 2 + no-change for ref
    bench_rmse = [(b, bench_get('post_covid_norm', 'dynamic', b)['rmse'])
                  for b in BENCHMARK_LABEL]
    bench_rmse.sort(key=lambda x: x[1])
    sel = [bench_rmse[0][0], bench_rmse[1][0], bench_rmse[2][0],
           'B0a_NoChange']  # always include no-change as reference
    sel = list(dict.fromkeys(sel))  # dedupe preserve order

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(dates_oos, obs * 100, color='black', linewidth=2.2,
            label='Observed UNRATE', zorder=10)
    ax.plot(dates_oos, abm * 100, color=PLOT_COLORS['ABM'], linewidth=2.0,
            label=f'ABM (recalibrated)  RMSE={abm_rmse("post_covid_norm")["rmse"]*100:.3f}pp',
            zorder=9)
    for b in sel:
        traj = SERIES[f'post_covid_norm__dynamic__{b}_ur']
        rmse = bench_get('post_covid_norm', 'dynamic', b)['rmse'] * 100
        ax.plot(dates_oos, traj * 100, color=PLOT_COLORS[b], linewidth=1.4,
                linestyle='--', alpha=0.85,
                label=f'{_short(b)}  RMSE={rmse:.3f}pp')
    ax.set_ylabel('Unemployment rate (%)')
    ax.set_title('Figure 3. Post-COVID normalization: predicted vs observed UR paths\n'
                 '(dynamic multi-step protocol, fit ends 2021-12)', fontsize=10.5)
    ax.legend(loc='upper right', fontsize=8.5, ncol=1, framealpha=0.92)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / 'fig3_paths_postcovid_dynamic.png', dpi=160)
    plt.close()
    print("fig3 saved")


# ---------------------------------------------------------------------------
# Figure 4 — Scatter: predicted vs observed (ABM + top 3 benchmarks)
# ---------------------------------------------------------------------------
def fig4():
    s, e = REGIME_OOS['post_covid_norm']
    obs_raw = SERIES['tgt_ur_full'][s:e] * 100
    abm_raw = ABM_FULL_UR[s:e] * 100
    mask = np.isfinite(obs_raw) & np.isfinite(abm_raw)
    obs = obs_raw[mask]
    abm = abm_raw[mask]

    bench_rmse = [(b, bench_get('post_covid_norm', 'dynamic', b)['rmse'])
                  for b in BENCHMARK_LABEL]
    bench_rmse.sort(key=lambda x: x[1])
    top3 = [bench_rmse[i][0] for i in range(3)]

    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8), sharey=True)
    items = [('ABM (recalibrated)', abm, PLOT_COLORS['ABM'])] + [
        (_short(b),
         (SERIES[f'post_covid_norm__dynamic__{b}_ur'] * 100)[mask],
         PLOT_COLORS[b]) for b in top3]
    lo = float(min(obs.min(), min(p.min() for _, p, _ in items))) - 0.2
    hi = float(max(obs.max(), max(p.max() for _, p, _ in items))) + 0.2

    for ax, (name, pred, col) in zip(axes, items):
        rmse = np.sqrt(np.mean((pred - obs) ** 2))
        corr = np.corrcoef(pred, obs)[0, 1] if pred.std() > 1e-9 else np.nan
        ax.scatter(obs, pred, s=22, color=col, alpha=0.75, edgecolor='black',
                   linewidth=0.3)
        ax.plot([lo, hi], [lo, hi], color='gray', linestyle='--', linewidth=1)
        ax.set_xlabel('Observed UR (%)')
        ax.set_title(f'{name}\nRMSE={rmse:.3f}pp, r={corr:+.3f}'
                     if not np.isnan(corr) else f'{name}\nRMSE={rmse:.3f}pp',
                     fontsize=9.5)
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel('Predicted UR (%)')
    plt.suptitle('Figure 4. Post-COVID predicted vs observed scatter (ABM + top-3 benchmarks)',
                 fontsize=11, y=1.02)
    plt.tight_layout()
    plt.savefig(FIG / 'fig4_scatter_postcovid.png', dpi=160, bbox_inches='tight')
    plt.close()
    print("fig4 saved")


# ---------------------------------------------------------------------------
# Figure 5 — Heatmap: RMSE (pp) by model × regime, dynamic protocol
# ---------------------------------------------------------------------------
def fig5():
    rows = ['ABM_Full_recalibrated'] + list(BENCHMARK_LABEL.keys())
    cols = REGIMES
    M = np.zeros((len(rows), len(cols)))
    for j, reg in enumerate(cols):
        M[0, j] = abm_rmse(reg, 'ur')['rmse'] * 100
        for i, b in enumerate(BENCHMARK_LABEL, start=1):
            M[i, j] = bench_get(reg, 'dynamic', b)['rmse'] * 100

    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    vmax = np.nanpercentile(M, 95)
    im = ax.imshow(M, cmap='YlOrRd', aspect='auto', vmin=0, vmax=vmax)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([REGIME_LABEL[c].split(' (')[0] for c in cols],
                       rotation=15, ha='right', fontsize=9)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([MODEL_LABEL.get(r, r).split(',')[0].split('(')[0].strip()
                        for r in rows], fontsize=9)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                    fontsize=8, color='black' if v < vmax * 0.55 else 'white')
    ax.axhline(0.5, color='red', linewidth=1.6)  # separate ABM from benchmarks
    plt.colorbar(im, ax=ax, label='UR RMSE (pp)', shrink=0.85)
    ax.set_title('Figure 5. UR RMSE (pp) by model × regime — dynamic protocol\n'
                 '(ABM row highlighted; lower is better)', fontsize=10.5)
    plt.tight_layout()
    plt.savefig(FIG / 'fig5_heatmap_model_regime.png', dpi=160)
    plt.close()
    print("fig5 saved")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    table1(); table2(); table3(); table4(); table5()
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("\nAll artifacts saved to", TBL, "and", FIG)
