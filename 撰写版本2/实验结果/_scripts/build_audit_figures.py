"""Build 9 additional figures to close the coverage gaps.

Audit-layer (7):
  E01_F01 Population Marginals (6-panel)
  E02_F02 Multi-seed UR Trajectory
  E03_F01 Parameter Top-5 IQR Bands
  E03_F02 Loss Function Tier Weights
  E03_F03 Calibration Convergence (V_Full progress)
  E07_F02 Component Contribution Bar
  E09_F02 Per-level UR Trajectory Overlay

Section paper-ready (2):
  S06_02_F02 Source of Advantage Decomposition
  S06_04_F02 Forecast Paths Overlay (post-COVID dynamic)
"""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("撰写版本2/实验结果/Results_Master_Package")
SRC = Path("正式撰写")
PHASE2 = Path("Phase2_Output")

plt.rcParams.update({
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "legend.frameon": False,
    "lines.linewidth": 1.8,
})

C_ABM = "#1f4e79"
C_OBS = "#404040"
C_TGT = "#c0392b"
C_BENCH = "#9bb7d4"
C_SEED = "#a6c8e0"
C_BAR = "#5b8db5"

SEC = {
    "S06_01": "S06_01_Dynamic_and_Regime_Specific_Performance",
    "S06_02": "S06_02_Internal_Controls_and_Source_of_Advantage",
    "S06_03": "S06_03_Recalibrated_Heterogeneity_Ablations",
    "S06_04": "S06_04_Forecast_Benchmark_Comparison",
    "S06_05": "S06_05_Robustness_and_Sensitivity",
}

EXP = {
    "E01": "E01_Synthetic_Population_Construction",
    "E02": "E02_Baseline_Stability_Check",
    "E03": "E03_Calibration_Setup",
    "E04": "E04_Dynamic_Evaluation",
    "E05": "E05_Regime_Specific_Evaluation",
    "E06": "E06_Internal_Control_Comparison",
    "E07": "E07_Source_of_Advantage_Decomposition",
    "E08": "E08_Heterogeneity_Ablation",
    "E09": "E09_Heterogeneity_Ladder",
    "E10": "E10_Forecast_Benchmark_Comparison",
    "E11": "E11_Training_Window_Sensitivity",
    "E12": "E12_Forecast_Horizon_and_Agent_Count_Sensitivity",
    "E13": "E13_Calibration_Method_and_Parameter_ID_Sensitivity",
}


def exp_fig_dir(eid: str) -> Path:
    return ROOT / "Results_By_Experiment" / EXP[eid] / "figures"


def sec_fig_dir(sid: str) -> Path:
    return ROOT / "Results_By_Section" / SEC[sid] / "paper_ready_figures"


def save_exp(fig, eid: str, fname: str) -> None:
    out = exp_fig_dir(eid) / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out.relative_to(ROOT)}")


def save_sec(fig, sid: str, fname: str) -> None:
    out = sec_fig_dir(sid) / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    mirror = ROOT / "Results_PaperReady_Figures" / fname
    mirror.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out, mirror)
    plt.close(fig)
    print(f"  [OK] {out.relative_to(ROOT)} (+mirror)")


def read_csv_rows(p: Path) -> list[list[str]]:
    with open(p, encoding="utf-8-sig") as fh:
        return list(csv.reader(fh))


def _dates_to_dt(dates_arr: np.ndarray) -> np.ndarray:
    """Convert array of 'YYYY-MM' strings to numpy datetime64[M]."""
    return np.array([np.datetime64(d, "M") for d in dates_arr])


# ---------------------------------------------------------------------------
# E01_F01 — Population Marginals (6-panel grid)
# ---------------------------------------------------------------------------
def fig_e01_f01():
    z = np.load(PHASE2 / "population_v1.npz", allow_pickle=True)
    age = z["static_traits"][:, 0].astype(float)
    edu = z["static_traits"][:, 1].astype(int)
    emp = z["category_states"][:, 0].astype(int)
    liq = z["category_states"][:, 1].astype(int)
    hou = z["category_states"][:, 2].astype(int)
    con = z["category_states"][:, 3].astype(int)

    age_bin = np.where(age < 40, 0, np.where(age <= 60, 1, 2))

    panels = [
        ("Age", ["Under 40", "40-60", "Over 60"], age_bin, [0.277, 0.391, 0.332]),
        ("Education", ["High school", "Some college", "College+"], edu, [0.114, 0.332, 0.554]),
        ("Employment state", ["Employed", "Unemployed", "Not in LF"], emp, [0.60, 0.04, 0.36]),
        ("Liquidity type", ["H2M", "Adequate", "Wealthy"], liq, [0.30, 0.45, 0.25]),
        ("Housing status", ["Rent-mob.", "Rent-stab.", "Own-low LTV", "Own-high LTV"], hou, [0.12, 0.20, 0.45, 0.23]),
        ("Consumption type", ["Saver", "Smoother", "Spender"], con, [0.30, 0.40, 0.30]),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    for ax, (title, labels, data, target) in zip(axes.ravel(), panels):
        n = len(labels)
        sim = np.array([(data == i).mean() for i in range(n)])
        x = np.arange(n)
        w = 0.38
        ax.bar(x - w/2, sim, w, color=C_ABM, label="Simulated", edgecolor="white")
        ax.bar(x + w/2, target, w, color=C_BENCH, label="Target", edgecolor="white")
        for xi, (s, t) in enumerate(zip(sim, target)):
            ax.text(xi - w/2, s + 0.012, f"{s*100:.1f}%", ha="center", fontsize=8, color=C_ABM)
            ax.text(xi + w/2, t + 0.012, f"{t*100:.1f}%", ha="center", fontsize=8, color="#4a6a87")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, rotation=15 if n > 3 else 0)
        ax.set_title(title)
        ax.set_ylim(0, max(max(sim), max(target)) * 1.25)
        ax.set_ylabel("Share (decimal)")
        ax.grid(axis="y", alpha=0.25)
    axes[0, 0].legend(loc="upper right", fontsize=9)
    fig.suptitle("E01: Synthetic population marginals vs anchoring targets (N=100,000)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save_exp(fig, "E01", "E01_F01_Population_Marginals_v01.png")


# ---------------------------------------------------------------------------
# E02_F02 — Multi-seed UR trajectory (V_Full)
# ---------------------------------------------------------------------------
def fig_e02_f02():
    z = np.load(SRC / "fix6.2" / "reeval_trajectories.npz", allow_pickle=True)
    dates = _dates_to_dt(z["dates"])
    tgt = z["target_ur"] * 100
    ur = z["V_Full_ur"]  # (5 cand, 5 seed, 302)
    seed_means = ur.mean(axis=0) * 100  # mean over candidates → (5 seed, 302)

    mask = dates >= np.datetime64("2018-01", "M")
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for i in range(seed_means.shape[0]):
        ax.plot(dates[mask], seed_means[i][mask], color=C_SEED, lw=0.9, alpha=0.85,
                label="Per-seed (5)" if i == 0 else None)
    grand = seed_means.mean(axis=0)
    ax.plot(dates[mask], grand[mask], color=C_ABM, lw=2.2, label="5-seed mean")
    ax.plot(dates[mask], tgt[mask], color=C_OBS, lw=1.5, label="Observed (BLS UNRATE)")
    ax.axvspan(np.datetime64("2020-03", "M"), np.datetime64("2021-12", "M"),
               color="#dddddd", alpha=0.4, zorder=0)
    ax.set_ylabel("Unemployment rate (%)")
    ax.set_title("E02: Cross-seed dispersion of V_Full UR trajectory (2018-01 onward)")
    ax.legend(loc="upper right", ncol=3, fontsize=9)
    save_exp(fig, "E02", "E02_F02_Multi_Seed_UR_Trajectory_v01.png")


# ---------------------------------------------------------------------------
# E03_F01 — Parameter Top-5 IQR Bands (V_Full)
# ---------------------------------------------------------------------------
def fig_e03_f01():
    rows = read_csv_rows(ROOT / "Results_By_Experiment" / EXP["E03"] / "tables" /
                         "E03_T02_Parameter_Bands_v01.csv")[1:]
    vfull = [r for r in rows if r[0] == "V_Full" and r[2] == "ACTIVE"]
    names = [r[1] for r in vfull]
    p25 = np.array([float(r[3]) for r in vfull])
    p50 = np.array([float(r[4]) for r in vfull])
    p75 = np.array([float(r[5]) for r in vfull])
    pmn = np.array([float(r[6]) for r in vfull])
    pmx = np.array([float(r[7]) for r in vfull])

    # Normalise each parameter to its own [min, max] for visual comparability
    rng = (pmx - pmn)
    rng_safe = np.where(rng > 0, rng, 1.0)
    n_p25 = (p25 - pmn) / rng_safe
    n_p50 = (p50 - pmn) / rng_safe
    n_p75 = (p75 - pmn) / rng_safe

    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hlines(y, 0, 1, color="#dddddd", lw=2)
    ax.errorbar(n_p50, y, xerr=[n_p50 - n_p25, n_p75 - n_p50],
                fmt="o", color=C_ABM, ecolor=C_ABM, capsize=4, markersize=7,
                markerfacecolor="white", lw=1.8, label="Top-5 P50 with [P25, P75]")
    ax.plot(np.zeros_like(y), y, "|", color="#999", markersize=10)
    ax.plot(np.ones_like(y), y, "|", color="#999", markersize=10)
    for i, (mn, mx) in enumerate(zip(pmn, pmx)):
        ax.text(-0.04, i, f"{mn:.3g}", ha="right", va="center", fontsize=7.5, color="#666")
        ax.text(1.04, i, f"{mx:.3g}", ha="left", va="center", fontsize=7.5, color="#666")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(-0.18, 1.18)
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels(["lower bound", "mid-range", "upper bound"])
    ax.set_title("E03: V_Full Top-5 parameter selection within search bounds (P25/P50/P75)")
    ax.grid(axis="x", alpha=0.2)
    ax.invert_yaxis()
    save_exp(fig, "E03", "E03_F01_Parameter_Top5_IQR_v01.png")


# ---------------------------------------------------------------------------
# E03_F02 — Loss Function Tier Weights
# ---------------------------------------------------------------------------
def fig_e03_f02():
    rows = read_csv_rows(ROOT / "Results_By_Experiment" / EXP["E03"] / "tables" /
                         "E03_T03_Loss_Function_Weights_v01.csv")[1:]
    targets = [r[1] for r in rows]
    weights = [float(r[3]) for r in rows]
    tiers = [int(r[0]) for r in rows]
    metrics = [r[2] for r in rows]

    tier_colors = {1: C_ABM, 2: C_BAR, 3: C_BENCH}
    colors = [tier_colors[t] for t in tiers]

    fig, ax = plt.subplots(figsize=(11, 4.6))
    y = np.arange(len(targets))
    ax.barh(y, weights, color=colors, edgecolor="white")
    for i, (w, m) in enumerate(zip(weights, metrics)):
        ax.text(w + 0.08, i, f"w={w:.1f}  ({m})", va="center", fontsize=9, color="#333")
    ax.set_yticks(y)
    ax.set_yticklabels(targets, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Tier weight")
    ax.set_xlim(0, max(weights) * 1.55)
    ax.set_title("E03: Calibration loss function — tier weights by target moment")
    # Tier legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=tier_colors[t], label=f"Tier {t}") for t in sorted(tier_colors)]
    ax.legend(handles=handles, loc="lower right", fontsize=9)
    ax.grid(axis="x", alpha=0.25)
    save_exp(fig, "E03", "E03_F02_Loss_Tier_Weights_v01.png")


# ---------------------------------------------------------------------------
# E03_F03 — Calibration Convergence (V_Full progress)
# ---------------------------------------------------------------------------
def fig_e03_f03():
    rows = read_csv_rows(SRC / "fix6.2" / "checkpoints" / "V_Full_progress.csv")[1:]
    cand = np.array([int(r[0]) for r in rows])
    seed = np.array([int(r[1]) for r in rows])
    loss = np.array([float(r[2]) for r in rows])

    unique_seeds = sorted(set(seed.tolist()))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [3, 2]})
    ax0 = axes[0]
    seed_palette = plt.cm.Blues(np.linspace(0.4, 0.9, len(unique_seeds)))
    for color, s in zip(seed_palette, unique_seeds):
        m = seed == s
        # running minimum per seed
        order = np.argsort(cand[m])
        running_min = np.minimum.accumulate(loss[m][order])
        ax0.plot(cand[m][order], running_min, color=color, lw=1.6, label=f"seed={s}")
    ax0.set_xlabel("Candidate index (sorted)")
    ax0.set_ylabel("Train loss (running min)")
    ax0.set_title("E03: Running minimum train-loss per seed across 100 LHS candidates")
    ax0.legend(fontsize=8, loc="upper right", ncol=2)

    ax1 = axes[1]
    # distribution of all loss values per seed
    data = [loss[seed == s] for s in unique_seeds]
    bp = ax1.boxplot(data, labels=[str(s) for s in unique_seeds], widths=0.55,
                     patch_artist=True, medianprops=dict(color="#222"))
    for patch, c in zip(bp["boxes"], seed_palette):
        patch.set_facecolor(c)
        patch.set_edgecolor("white")
    ax1.set_xlabel("Seed")
    ax1.set_ylabel("Train loss")
    ax1.set_title("Per-seed distribution of all candidate losses")
    ax1.grid(axis="y", alpha=0.25)
    save_exp(fig, "E03", "E03_F03_Calibration_Convergence_v01.png")


# ---------------------------------------------------------------------------
# E07_F02 — Component Contribution Bar (audit layer)
# ---------------------------------------------------------------------------
def fig_e07_f02():
    rows = read_csv_rows(ROOT / "Results_By_Experiment" / EXP["E07"] / "tables" /
                         "E07_T01_Source_of_Advantage_v01.csv")[1:]
    d = {r[0]: float(r[1]) for r in rows}
    total = d["Total_gain_Simplified_minus_Full_pp"]
    components = [
        ("Heterogeneity\ngain",
         d["Heterogeneity_gain_Homogeneous_minus_Full_pp"],
         d["Heterogeneity_share_pct"]),
        ("Mechanism\ngain",
         d["Mechanism_gain_Simplified_minus_Homogeneous_pp"],
         d["Mechanism_share_pct"]),
        ("Household-block\ngain (overlap)",
         d["Household_block_gain_LaborOnly_minus_Full_pp"],
         100 * d["Household_block_gain_LaborOnly_minus_Full_pp"] / total),
    ]

    fig, ax = plt.subplots(figsize=(8.5, 5))
    x = np.arange(len(components))
    vals = [c[1] for c in components]
    bars = ax.bar(x, vals, color=[C_ABM, C_BAR, C_BENCH], edgecolor="white", width=0.55)
    for bar, (_, v, share) in zip(bars, components):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.008,
                f"{v:.3f} pp\n({share:.0f}%)", ha="center", va="bottom", fontsize=9)
    ax.axhline(total, color=C_TGT, lw=1.2, ls="--", alpha=0.7)
    ax.text(0.02, total + 0.005, f"Total gain {total:.3f} pp", color=C_TGT,
            fontsize=9, transform=ax.get_yaxis_transform())
    ax.set_xticks(x)
    ax.set_xticklabels([c[0] for c in components], fontsize=10)
    ax.set_ylabel("UR RMSE reduction vs V_Simplified (pp)")
    ax.set_title("E07: Within-experiment accounting decomposition of the V_Full advantage")
    ax.set_ylim(0, max(vals + [total]) * 1.25)
    ax.grid(axis="y", alpha=0.25)
    save_exp(fig, "E07", "E07_F02_Component_Contribution_Bar_v01.png")


# ---------------------------------------------------------------------------
# E09_F02 — Per-level UR trajectory overlay (L0..L6)
# ---------------------------------------------------------------------------
def fig_e09_f02():
    z = np.load(SRC / "6.3" / "ladder_series.npz", allow_pickle=True)
    dates = _dates_to_dt(z["dates"])
    tgt = z["target_ur"] * 100
    mask = dates >= np.datetime64("2018-01", "M")

    levels = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
    palette = plt.cm.viridis(np.linspace(0.05, 0.92, len(levels)))
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for color, lv in zip(palette, levels):
        arr = z[f"{lv}_ur"] * 100  # (5 seed, 302)
        mean = arr.mean(axis=0)
        ax.plot(dates[mask], mean[mask], color=color, lw=1.4, label=lv, alpha=0.85)
    ax.plot(dates[mask], tgt[mask], color=C_OBS, lw=1.6, label="Observed", zorder=10)
    ax.axvspan(np.datetime64("2020-03", "M"), np.datetime64("2021-12", "M"),
               color="#dddddd", alpha=0.4, zorder=0)
    ax.set_ylabel("Unemployment rate (%)")
    ax.set_title("E09: Per-level UR trajectory across the heterogeneity ladder (5-seed mean)")
    ax.legend(loc="upper right", ncol=4, fontsize=8.5)
    save_exp(fig, "E09", "E09_F02_Per_Level_UR_Trajectory_v01.png")


# ---------------------------------------------------------------------------
# S06_02_F02 — Source of Advantage (paper-ready bar)
# ---------------------------------------------------------------------------
def fig_s06_02_f02():
    rows = read_csv_rows(ROOT / "Results_By_Experiment" / EXP["E07"] / "tables" /
                         "E07_T01_Source_of_Advantage_v01.csv")[1:]
    d = {r[0]: float(r[1]) for r in rows}
    total = d["Total_gain_Simplified_minus_Full_pp"]
    het = d["Heterogeneity_gain_Homogeneous_minus_Full_pp"]
    mech = d["Mechanism_gain_Simplified_minus_Homogeneous_pp"]
    hh = d["Household_block_gain_LaborOnly_minus_Full_pp"]

    labels = ["Heterogeneity", "Mechanism", "Household block\n(overlap)"]
    vals = [het, mech, hh]
    shares = [d["Heterogeneity_share_pct"], d["Mechanism_share_pct"],
              100 * hh / total]
    colors = [C_ABM, C_BAR, C_BENCH]

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    x = np.arange(len(labels))
    bars = ax.bar(x, vals, color=colors, width=0.58, edgecolor="white")
    y_top = max(vals + [total])
    ax.set_ylim(0, y_top * 1.42)
    for b, v, s in zip(bars, vals, shares):
        ax.text(b.get_x() + b.get_width()/2, v + y_top * 0.022,
                f"{v:.3f} pp\n({s:.0f}%)", ha="center", va="bottom", fontsize=10)
    ax.axhline(total, color=C_TGT, lw=1.2, ls="--", alpha=0.7)
    ax.text(0.985, total + y_top * 0.015,
            f"Total = {total:.3f} pp", color=C_TGT, fontsize=9,
            ha="right", va="bottom", transform=ax.get_yaxis_transform())
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Within-experiment accounting gain (pp)")
    ax.set_title("Source of the V_Full UR-RMSE advantage\n"
                 "(main recent evaluation window; within-experiment accounting, not causal)")
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.01, -0.015,
             "Note: components are RMSE differences against alternative variants under separate calibration; "
             "shares are window-specific (main recent evaluation window only) and not a causal decomposition.",
             fontsize=7.5, color="#555")
    save_sec(fig, "S06_02", "S06_02_F02_Source_of_Advantage__E7_v01.png")


# ---------------------------------------------------------------------------
# S06_04_F02 — Forecast Paths Overlay (post-COVID dynamic, top-N + ABM)
# ---------------------------------------------------------------------------
def fig_s06_04_f02():
    """Forecast paths on the main recent evaluation window.

    Data sources:
      - Target UR + benchmark trajectories: fix6.4/benchmark_series.npz
        Benchmark arrays are stored as DECIMAL (median ~0.04..0.06), length 50,
        aligned to 2022-01..2026-02.
      - ABM V_Full UR: fix6.2/reeval_trajectories.npz V_Full_ur (5_cal, 5_seed, 302),
        averaged over cal+seed and converted decimal -> percent. The benchmark npz
        v_full key is not a UR series (med ~1.1) and is not used here.

    Benchmark set (locked to the approved 6-line composition): ABM, Observed,
    No-change (B0a), ETS (B3), Beveridge (B6), Flow-based UR (B8).
    """
    z = np.load(SRC / "fix6.4" / "benchmark_series.npz", allow_pickle=True)
    dates_full = _dates_to_dt(z["dates_full"])
    tgt_full = np.asarray(z["tgt_ur_full"], dtype=float) * 100.0

    # Find the 2022-01 anchor; benchmark arrays are length 50 (=> 2022-01..2026-02).
    benchmark_keys = {
        "No-change":     "post_covid_norm__dynamic__B0a_NoChange_ur",
        "ETS":           "post_covid_norm__dynamic__B3_ETS_ur",
        "Beveridge":     "post_covid_norm__dynamic__B6_Beveridge_ur",
        "Flow-based UR": "post_covid_norm__dynamic__B8_Flow_ur",
    }
    h = len(z[next(iter(benchmark_keys.values()))])
    start = int(np.where(dates_full == np.datetime64("2022-01", "M"))[0][0])
    win = slice(start, start + h)
    dates_win = dates_full[win]
    tgt_win = tgt_full[win]

    # ABM V_Full trajectory (avg over 5 cal * 5 seed); slice to same window.
    rz = np.load(SRC / "fix6.2" / "reeval_trajectories.npz", allow_pickle=True)
    rz_dates = _dates_to_dt(rz["dates"])
    abm_full_pct = np.asarray(rz["V_Full_ur"], dtype=float).mean(axis=(0, 1)) * 100.0
    rz_start = int(np.where(rz_dates == np.datetime64("2022-01", "M"))[0][0])
    abm_win = abm_full_pct[rz_start: rz_start + h]

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    palette = {"No-change": "#9bb7d4", "ETS": "#7fa1c3",
               "Beveridge": "#638ab2", "Flow-based UR": "#4a749f"}
    for label, key in benchmark_keys.items():
        series_pct = np.asarray(z[key], dtype=float) * 100.0
        ax.plot(dates_win, series_pct, color=palette[label], lw=1.5, alpha=0.9, label=label)
    ax.plot(dates_win, abm_win, color=C_ABM, lw=2.4, label="ABM V_Full", zorder=9)
    ax.plot(dates_win, tgt_win, color=C_OBS, lw=1.8, label="Observed (BLS)", zorder=10)
    ax.set_ylabel("Unemployment rate (%)")
    ax.set_title("Main recent evaluation window dynamic forecast paths: ABM vs benchmarks")
    ax.legend(loc="upper right", ncol=3, fontsize=9)
    # Auto y-limits with a small pad so all 6 lines fit cleanly (UR ~3..6%).
    all_pct = np.concatenate([tgt_win, abm_win,
                              *[np.asarray(z[k], dtype=float) * 100.0
                                for k in benchmark_keys.values()]])
    ymin = float(np.nanmin(all_pct))
    ymax = float(np.nanmax(all_pct))
    span = max(ymax - ymin, 1.0)
    ax.set_ylim(ymin - span * 0.10, ymax + span * 0.18)
    ax.grid(alpha=0.25)
    fig.text(0.01, -0.015,
             "Note: ABM trained 2004-01..2017-12 (168 m); benchmarks fit 2001-01..2021-12 "
             "(252 m, includes 2020-2021 disruption window). Both forecast 2022-01..2026-02 dynamically.",
             fontsize=7.5, color="#555")
    save_sec(fig, "S06_04", "S06_04_F02_Paths_Dynamic__E10_v01.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    funcs = [
        ("E01_F01", fig_e01_f01),
        ("E02_F02", fig_e02_f02),
        ("E03_F01", fig_e03_f01),
        ("E03_F02", fig_e03_f02),
        ("E03_F03", fig_e03_f03),
        ("E07_F02", fig_e07_f02),
        ("E09_F02", fig_e09_f02),
        ("S06_02_F02", fig_s06_02_f02),
        ("S06_04_F02", fig_s06_04_f02),
    ]
    for name, fn in funcs:
        print(f"--- {name} ---")
        try:
            fn()
        except Exception as exc:
            print(f"  [FAIL] {name}: {exc!r}")
            raise


if __name__ == "__main__":
    main()

