"""Build paper-ready PNG figures + experiment-level figures.

Style: unified, no chartjunk, no emojis, neutral palette, 300 dpi.

Paper-ready main-text figure set (post-split):
  S06_01_F01A Observed vs Simulated UR — full post-2018 window standalone
  S06_01_F01B Observed vs Simulated UR — main recent evaluation window standalone
  S06_01_F02A Regime UR RMSE bar standalone
  S06_01_F02B Regime UR bias bar standalone
  S06_02_F01  Control RMSE Bar (4 variants)
  S06_03_F01  Ablation RMSE Bar (6 ablations + Full reference line)
  S06_03_F02  Ladder RMSE Path (L0..L6)
  S06_04_F01  Benchmark RMSE Bar (12 models, horizontal)
  S06_05_F01A Training-window sensitivity standalone
  S06_05_F01B Forecast horizon decay standalone
  S06_05_F01C Agent-count plateau standalone
  S06_05_F01D Parameter identification standalone
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

# Unified style ---------------------------------------------------------------
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

C_ABM = "#1f4e79"   # deep blue
C_OBS = "#404040"   # dark gray
C_BENCH = "#9bb7d4"  # light blue
C_HIGHLIGHT = "#c0392b"  # red for caveat
C_SEED = "#a6c8e0"  # light blue tint

# Locked headline reference (recalibrated V_Full on main recent evaluation window).
# Source: 正式撰写/fix6.2/tables/table1_variant_summary.csv, V_Full row.
HEADLINE_RMSE_PP = 0.2731
HEADLINE_SD_PP = 0.0233
HEADLINE_BENCH_TIE_PP = 0.3094  # No-change / ETS tie

SEC = {
    "S06_01": "S06_01_Dynamic_and_Regime_Specific_Performance",
    "S06_02": "S06_02_Internal_Controls_and_Source_of_Advantage",
    "S06_03": "S06_03_Recalibrated_Heterogeneity_Ablations",
    "S06_04": "S06_04_Forecast_Benchmark_Comparison",
    "S06_05": "S06_05_Robustness_and_Sensitivity",
}


def sec_fig_dir(sid: str) -> Path:
    return ROOT / "Results_By_Section" / SEC[sid] / "paper_ready_figures"


def read_csv(p: Path) -> list[list[str]]:
    with open(p, encoding="utf-8-sig") as fh:
        return list(csv.reader(fh))


def savefig(fig, sid: str, fname: str) -> None:
    out = sec_fig_dir(sid) / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    # Mirror to aggregate folder
    mirror = ROOT / "Results_PaperReady_Figures" / fname
    mirror.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out, mirror)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Shared loader: recalibrated V_Full trajectory (fix6.2 reeval_trajectories)
# ---------------------------------------------------------------------------
def _load_v_full_trajectory():
    """Return (dates_str, target_pct, per_seed_pct, mean_pct) for V_Full.

    Source: fix6.2/reeval_trajectories.npz V_Full_ur (5_cal, 5_seed, 302),
    averaged over the 5 calibration candidates so the 5 seed-level trajectories
    correspond to the headline 5-seed set {42, 137, 888, 1234, 2024}. Values are
    converted from decimal to percent.
    """
    z = np.load(SRC / "fix6.2" / "reeval_trajectories.npz", allow_pickle=True)
    dates = np.array([str(x) for x in z["dates"]])
    target_pct = np.asarray(z["target_ur"], dtype=float) * 100.0
    raw = np.asarray(z["V_Full_ur"], dtype=float)  # (5_cal, 5_seed, 302)
    per_seed_pct = raw.mean(axis=0) * 100.0  # (5_seed, 302)
    mean_pct = per_seed_pct.mean(axis=0)  # (302,)
    return dates, target_pct, per_seed_pct, mean_pct


# ---------------------------------------------------------------------------
# S06_01 F01A — Observed vs Simulated UR, full post-2018 window (standalone)
# ---------------------------------------------------------------------------
def fig_s06_01_f01a():
    dates, target_pct, per_seed_pct, mean_pct = _load_v_full_trajectory()
    idx = np.where(dates >= "2018-01")[0]

    fig, ax = plt.subplots(figsize=(10, 4.6))
    pre_idx = np.where((dates >= "2018-01") & (dates <= "2019-12"))[0]
    pc_idx = np.where((dates >= "2020-03") & (dates <= "2021-12"))[0]
    pcn_idx = np.where((dates >= "2022-01") & (dates <= "2026-02"))[0]
    ax.axvspan(pre_idx.min(), pre_idx.max(), color="#dddddd", alpha=0.35, zorder=0)
    ax.axvspan(pc_idx.min(), pc_idx.max(), color="#f0d0d0", alpha=0.35, zorder=0)
    ax.axvspan(pcn_idx.min(), pcn_idx.max(), color="#d0e0d0", alpha=0.35, zorder=0)

    for s in range(per_seed_pct.shape[0]):
        ax.plot(idx, per_seed_pct[s, idx], color=C_SEED, alpha=0.45, lw=0.8)
    ax.plot(idx, mean_pct[idx], color=C_ABM, lw=1.8, label="ABM V_Full (5-seed mean)")
    ax.plot(idx, target_pct[idx], color=C_OBS, lw=1.6, label="Observed (BLS UNRATE)")

    year_ticks = [i for i in idx if dates[i].endswith("-01")]
    ax.set_xticks(year_ticks)
    ax.set_xticklabels([dates[i][:4] for i in year_ticks])
    ax.set_xlim(idx.min() - 1, idx.max() + 1)
    ax.set_ylim(2, 16)
    ax.set_xlabel("Year")
    ax.set_ylabel("Unemployment rate (%)")
    ax.set_title("Observed vs simulated U.S. unemployment rate — full post-2018 window")
    # Regime labels just above the axis baseline to avoid 2020 peak (~14.7%).
    ax.text(pre_idx.mean(), 2.6, "Early stable window", ha="center", fontsize=8.5, color="#555")
    ax.text(pc_idx.mean(), 2.6, "2020-2021 disruption", ha="center", fontsize=8.5, color="#a04040")
    ax.text(pcn_idx.mean(), 2.6, "Main recent evaluation", ha="center", fontsize=8.5, color="#406040")
    ax.legend(loc="upper right", fontsize=9)
    savefig(fig, "S06_01", "S06_01_F01A_Observed_vs_Simulated_UR_Full__E4_v01.png")


# ---------------------------------------------------------------------------
# S06_01 F01B — Observed vs Simulated UR, main recent evaluation window
# ---------------------------------------------------------------------------
def fig_s06_01_f01b():
    dates, target_pct, per_seed_pct, mean_pct = _load_v_full_trajectory()
    win = np.where((dates >= "2022-01") & (dates <= "2026-02"))[0]

    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    for s in range(per_seed_pct.shape[0]):
        ax.plot(win, per_seed_pct[s, win], color=C_SEED, alpha=0.45, lw=0.8)
    ax.plot(win, mean_pct[win], color=C_ABM, lw=2.0, label="ABM V_Full (5-seed mean)")
    ax.plot(win, target_pct[win], color=C_OBS, lw=1.7, label="Observed (BLS UNRATE)")

    yr = [i for i in win if dates[i].endswith("-01")]
    ax.set_xticks(yr)
    ax.set_xticklabels([dates[i][:4] for i in yr])
    ax.set_xlim(win.min() - 0.5, win.max() + 0.5)
    ax.set_ylim(3.1, 4.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("Unemployment rate (%)")
    ax.set_title("Main recent evaluation window — observed vs simulated UR")
    ax.legend(loc="upper left", fontsize=9)
    # Headline call-out in clean text box at lower-right.
    ax.text(0.985, 0.04,
            f"V_Full UR RMSE = {HEADLINE_RMSE_PP:.3f} pp  (SD {HEADLINE_SD_PP:.3f})",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color=C_ABM,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=C_ABM, lw=0.6))
    savefig(fig, "S06_01", "S06_01_F01B_Observed_vs_Simulated_UR_MainEval__E4_v01.png")


# ---------------------------------------------------------------------------
# Shared regime-bar values: 3 legacy E5 windows + 1 recalibrated V_Full headline
# ---------------------------------------------------------------------------
def _regime_bar_values():
    reg = read_csv(SRC / "fix6.1" / "tables" / "table1_regime_summary.csv")
    by_w = {r[0]: r for r in reg[1:]}
    order = ["pre_covid_stable", "covid_crisis_mar", "post_covid_norm", "full_post_2018"]
    labels = ["Early stable\n2018-01–2019-12",
              "2020-2021 disruption\n2020-03–2021-12",
              "Main recent eval.\n2022-01–2026-02",
              "Full post-2018\n2018-01–2026-02"]
    ur = [float(by_w[w][4]) for w in order]
    sd = [float(by_w[w][5]) for w in order]
    bias = [float(by_w[w][8]) for w in order]
    # Replace the headline window with the recalibrated V_Full numbers.
    ur[2] = HEADLINE_RMSE_PP
    sd[2] = HEADLINE_SD_PP
    bias[2] = -0.1669
    colors = [C_BENCH, C_HIGHLIGHT, C_ABM, "#777"]
    return labels, ur, sd, bias, colors


# ---------------------------------------------------------------------------
# S06_01 F02A — Regime UR RMSE bar standalone
# ---------------------------------------------------------------------------
def fig_s06_01_f02a():
    labels, ur, sd, bias, colors = _regime_bar_values()
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    bars = ax.bar(range(4), ur, yerr=sd, color=colors, capsize=4, edgecolor="white", width=0.62)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("UR RMSE (pp)")
    ax.set_title("UR RMSE by evaluation window")
    for bar, v, s in zip(bars, ur, sd):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + s + max(ur) * 0.025,
                f"{v:.3f}", ha="center", fontsize=9.5)
    ax.set_ylim(0, max(ur) * 1.32)
    # Headline call-out on the third bar (recalibrated V_Full).
    ax.annotate(f"headline {HEADLINE_RMSE_PP:.3f} pp",
                xy=(2, ur[2] + sd[2]),
                xytext=(2, max(ur) * 0.45),
                ha="center", fontsize=9, color=C_ABM,
                arrowprops=dict(arrowstyle="->", color=C_ABM, lw=0.7))
    savefig(fig, "S06_01", "S06_01_F02A_Regime_RMSE_Bar__E5_v01.png")


# ---------------------------------------------------------------------------
# S06_01 F02B — Regime UR bias bar standalone
# ---------------------------------------------------------------------------
def fig_s06_01_f02b():
    labels, ur, sd, bias, colors = _regime_bar_values()
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    bars = ax.bar(range(4), bias, color=colors, edgecolor="white", width=0.62)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("UR bias (pp; sim − obs)")
    ax.set_title("UR bias by evaluation window")
    yrange = max(bias) - min(bias)
    for bar, v in zip(bars, bias):
        offset = yrange * 0.04 if v >= 0 else -yrange * 0.06
        va = "bottom" if v >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + offset,
                f"{v:+.3f}", ha="center", va=va, fontsize=9.5)
    pad = yrange * 0.15
    ax.set_ylim(min(bias) - pad, max(bias) + pad)
    savefig(fig, "S06_01", "S06_01_F02B_Regime_Bias_Bar__E5_v01.png")


# ---------------------------------------------------------------------------
# S06_02 F01 — Control RMSE Bar
# ---------------------------------------------------------------------------
def fig_s06_02_f01():
    var = read_csv(SRC / "fix6.2" / "tables" / "table1_variant_summary.csv")
    by = {r[0]: r for r in var[1:]}
    order = ["V_Simplified", "V_Homogeneous", "V_LaborOnly", "V_Full"]
    labels = ["V_Simplified\n(no het, 1 mech)", "V_Homogeneous\n(no het, all mech)",
              "V_LaborOnly\n(labour-side only)", "V_Full\n(reference)"]
    ur = [float(by[v][3]) for v in order]
    sd = [float(by[v][4]) for v in order]
    colors = [C_BENCH, C_BENCH, "#7a9cc6", C_ABM]

    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    bars = ax.bar(range(4), ur, yerr=sd, color=colors, capsize=4, edgecolor="white", width=0.62)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("UR RMSE (pp) — main recent evaluation window")
    ax.set_title("Main recent evaluation window UR RMSE by separately calibrated variant\n"
                 "(2022-01..2026-02, 5-seed mean)")
    ax.set_ylim(0, max(ur) * 1.35)
    # Per-bar value label, sitting just above the error-bar cap.
    for bar, v, s in zip(bars, ur, sd):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + s + max(ur) * 0.022,
                f"{v:.3f}", ha="center", fontsize=10)
    # V_Full headline call-out sits well above the bar to avoid the value label.
    full_bar = bars[3]
    ax.annotate(f"headline {HEADLINE_RMSE_PP:.3f} pp",
                xy=(full_bar.get_x() + full_bar.get_width()/2, ur[3] + sd[3]),
                xytext=(full_bar.get_x() + full_bar.get_width()/2, max(ur) * 1.22),
                ha="center", fontsize=9, color=C_ABM,
                arrowprops=dict(arrowstyle="->", color=C_ABM, lw=0.7))
    # Total gain span — placed above all bar labels.
    y_total = max(ur) * 1.10
    ax.annotate("", xy=(3, y_total), xytext=(0, y_total),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=0.8))
    ax.text(1.5, y_total + max(ur) * 0.02,
            f"Total gain = {ur[0] - ur[3]:.3f} pp",
            ha="center", fontsize=9.5, color="#333")
    savefig(fig, "S06_02", "S06_02_F01_Control_RMSE_Bar__E6_v01.png")


# ---------------------------------------------------------------------------
# S06_03 F01 — Recalibrated Ablation Bar
# ---------------------------------------------------------------------------
def fig_s06_03_f01():
    ab = read_csv(SRC / "fix6.3" / "tables" / "table2_post_covid_ablation.csv")
    rows = [r for r in ab[1:] if r[0] != "V_Full"]
    full_rmse = float([r for r in ab[1:] if r[0] == "V_Full"][0][2])

    order = ["V_NoSearch", "V_NoSLH", "V_NoLiquidity", "V_SearchOnly", "V_NoConsumption", "V_NoHousing"]
    rows_d = {r[0]: r for r in rows}
    labels = ["NoSearch\n(search off)", "NoSLH\n(joint)", "NoLiquidity\n(fragility off)",
              "SearchOnly\n(others off)", "NoConsumption\n(rule off)", "NoHousing\n(mobility off)"]
    rmse = [float(rows_d[v][2]) for v in order]
    delta = [float(rows_d[v][4]) for v in order]
    sd = [float(rows_d[v][3]) for v in order]
    colors = [C_HIGHLIGHT if d > 0.2 else "#d89a8a" if d > 0.05 else "#a8c5e0" if d > 0 else C_ABM
              for d in delta]

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    bars = ax.bar(range(len(order)), rmse, yerr=sd, color=colors, capsize=4, edgecolor="white", width=0.66)
    ax.axhline(full_rmse, color=C_ABM, ls="--", lw=1.2,
               label=f"V_Full headline ({full_rmse:.3f} pp)")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("UR RMSE (pp) — main recent evaluation window")
    ax.set_title("Main recent evaluation window UR RMSE by re-calibrated ablation\n"
                 "(every variant separately calibrated; diagnostic, not structural)")
    ax.set_ylim(0, max(rmse) * 1.38)
    for bar, v, s, dv in zip(bars, rmse, sd, delta):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + s + max(rmse) * 0.025,
                f"{v:.3f}\nΔ{dv:+.3f}", ha="center", fontsize=8.5)
    ax.legend(loc="upper right", fontsize=9)
    savefig(fig, "S06_03", "S06_03_F01_Ablation_RMSE_Bar__E8_v01.png")


# ---------------------------------------------------------------------------
# S06_03 F02 — Ladder
# ---------------------------------------------------------------------------
def fig_s06_03_f02():
    ld = read_csv(SRC / "6.3" / "tables" / "table3_heterogeneity_ladder.csv")
    core = [r for r in ld[1:] if r[1] == "core"]
    levels = [int(r[2]) for r in core]
    rmse = [float(r[4]) for r in core]
    sd = [float(r[6]) for r in core]
    names = [r[3].replace("|", " + ") if r[3] else "(no heterogeneity)" for r in core]

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.errorbar(levels, rmse, yerr=sd, color=C_ABM, marker="o", lw=1.8, capsize=4,
                markerfacecolor="white", markersize=8)
    # Only L0..L6 on the X axis; mechanism composition is documented in the caption.
    ax.set_xticks(levels)
    ax.set_xticklabels([f"L{l}" for l in levels])
    ax.set_xlabel("Heterogeneity ladder level")
    ax.set_ylabel("UR RMSE (pp) — main recent evaluation window")
    ax.set_title("Heterogeneity ladder: incremental addition of dimensions\n"
                 "(legacy baseline family; not directly comparable to V_Full headline)")
    ax.set_ylim(0, max(rmse) * 1.22)
    # Per-point value labels above each marker (no mechanism strings in plot area).
    for x, y, s in zip(levels, rmse, sd):
        ax.text(x, y + s + max(rmse) * 0.025, f"{y:.3f}",
                ha="center", fontsize=8.5, color="#333")
    drop_l4_l5 = rmse[5] - rmse[4]
    ax.annotate(f"largest single drop\nL4 → L5 = {drop_l4_l5:+.4f} pp",
                xy=(5, rmse[5]),
                xytext=(2.8, max(rmse) * 0.75),
                arrowprops=dict(arrowstyle="->", color="#555", lw=0.7),
                fontsize=8.5, color="#555", ha="center")
    ax.axhline(HEADLINE_RMSE_PP, color=C_HIGHLIGHT, ls=":", lw=1.0,
               label=f"V_Full recalibrated headline = {HEADLINE_RMSE_PP:.3f} pp (different family)")
    ax.legend(loc="upper right", fontsize=8.5)
    savefig(fig, "S06_03", "S06_03_F02_Ladder_RMSE_Path__E9_v01.png")
    # Write mechanism composition as a caption sidecar so manuscript text can paste it.
    cap = ["Caption text for S06_03_F02 — heterogeneity ladder composition (paste into manuscript caption):"]
    for lv, n in zip(levels, names):
        cap.append(f"  L{lv}: {n}")
    cap_path = sec_fig_dir("S06_03") / "S06_03_F02_caption.txt"
    cap_path.write_text("\n".join(cap) + "\n", encoding="utf-8")
    (ROOT / "Results_PaperReady_Figures" / "S06_03_F02_caption.txt").write_text(
        "\n".join(cap) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# S06_04 F01 — Benchmark RMSE (horizontal bar)
# ---------------------------------------------------------------------------
def fig_s06_04_f01():
    bm = read_csv(SRC / "fix6.4" / "tables" / "table1_main_postcovid_benchmark.csv")
    rows = [r for r in bm[1:] if r[0] != "ABM_Full_original" and r[4] not in {"N/A", ""}]
    rows.sort(key=lambda r: float(r[4]), reverse=True)
    labels = ["Full heterogeneous ABM (recalibrated)" if r[0] == "ABM_Full_recalibrated" else r[1]
              for r in rows]
    rmse = [float(r[4]) for r in rows]
    colors = [C_ABM if r[0] == "ABM_Full_recalibrated" else C_BENCH for r in rows]

    fig, ax = plt.subplots(figsize=(9.4, 6.0))
    bars = ax.barh(range(len(rows)), rmse, color=colors, edgecolor="white", height=0.66)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("UR RMSE (pp) — main recent evaluation window (2022-01..2026-02)")
    ax.set_title("ABM vs forecasting benchmarks (dynamic protocol)")
    ax.set_xlim(0, max(rmse) * 1.18)
    for bar, v in zip(bars, rmse):
        ax.text(bar.get_width() + max(rmse) * 0.012,
                bar.get_y() + bar.get_height()/2,
                f"{v:.3f}", va="center", fontsize=8.5)
    abm_v = next(v for r, v in zip(rows, rmse) if r[0] == "ABM_Full_recalibrated")
    ax.axvline(abm_v, color=C_ABM, ls="--", lw=1, alpha=0.7,
               label=f"Full heterogeneous ABM (recalibrated) = {abm_v:.3f} pp")
    ax.axvline(HEADLINE_BENCH_TIE_PP, color="#888", ls=":", lw=1, alpha=0.7,
               label=f"No-change / ETS tie = {HEADLINE_BENCH_TIE_PP:.3f} pp")
    ax.legend(loc="lower right", fontsize=8.5)
    fig.text(0.01, -0.015,
             "Note: ABM trained 2004-01..2017-12 (168 m); benchmarks fit 2001-01..2021-12 "
             "(252 m, includes 2020-2021 disruption window).",
             fontsize=7.5, color="#555")
    savefig(fig, "S06_04", "S06_04_F01_Benchmark_RMSE_Bar__E10_v01.png")


# ---------------------------------------------------------------------------
# S06_05 F01A — Training-window sensitivity standalone
# ---------------------------------------------------------------------------
def fig_s06_05_f01a():
    tw = read_csv(SRC / "6.5" / "tables" / "table2_training_window.csv")
    splits = [r[0] for r in tw[1:]]
    m0 = [float(r[7]) for r in tw[1:]]
    colors = [C_HIGHLIGHT if v > 1.0 else C_ABM for v in m0]

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    bars = ax.bar(range(len(splits)), m0, color=colors, edgecolor="white", width=0.62)
    ax.set_xticks(range(len(splits)))
    ax.set_xticklabels(splits, fontsize=9)
    ax.set_ylabel("UR RMSE (pp)")
    ax.set_title("Training-window sensitivity (Full ABM class)")
    eval_mean = float(np.mean([v for v in m0 if v < 1.0]))
    ax.axhline(eval_mean, color="#555", ls="--", lw=0.8,
               label=f"Evaluation-split mean ≈ {eval_mean:.3f} pp")
    ax.set_ylim(0, max(m0) * 1.18)
    for bar, v in zip(bars, m0):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + max(m0) * 0.02,
                f"{v:.2f}", ha="center", fontsize=8.5)
    ax.legend(loc="upper right", fontsize=9)
    savefig(fig, "S06_05", "S06_05_F01A_Training_Window__E11_v01.png")


# ---------------------------------------------------------------------------
# S06_05 F01B — Forecast horizon decay standalone
# ---------------------------------------------------------------------------
def fig_s06_05_f01b():
    hz = read_csv(SRC / "6.5" / "tables" / "table3_horizon.csv")
    horizons = [1, 3, 6, 12, 24, 36]
    model_lines = {
        "M0_Main": ("Full ABM", C_ABM, "-"),
        "B1_AR": ("AR", "#a04040", "--"),
        "B2_VAR": ("VAR", "#608060", "--"),
        "B4_DMP": ("DMP", "#806040", ":"),
    }
    by = {r[0]: r for r in hz[1:]}
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for m, (lab, c, ls) in model_lines.items():
        vals = []
        for i in range(1, 7):
            try:
                vals.append(float(by[m][i]))
            except ValueError:
                vals.append(np.nan)
        ax.plot(horizons, vals, color=c, linestyle=ls, marker="o", markersize=5, label=lab)
    ax.set_xlabel("Forecast horizon (months, log scale)")
    ax.set_ylabel("UR RMSE (pp, log scale)")
    ax.set_title("Horizon decay — ABM is shallowest (log-log slope −0.09)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="upper left", fontsize=9)
    savefig(fig, "S06_05", "S06_05_F01B_Horizon_Decay__E12_v01.png")


# ---------------------------------------------------------------------------
# S06_05 F01C — Agent-count plateau standalone
# ---------------------------------------------------------------------------
def fig_s06_05_f01c():
    ac = read_csv(SRC / "6.5" / "tables" / "table4_agent_count.csv")
    N = [int(r[0]) for r in ac[1:]]
    mean_rmse = [float(r[1]) for r in ac[1:]]
    sd_rmse = [float(r[2]) for r in ac[1:]]

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.errorbar(N, mean_rmse, yerr=sd_rmse, marker="o", color=C_ABM, capsize=4,
                markerfacecolor="white", markersize=7, lw=1.6)
    ax.set_xscale("log")
    ax.set_xlabel("Agent count N (log scale)")
    ax.set_ylabel("UR RMSE (pp)")
    ax.set_title("Agent-count plateau (|ΔRMSE| < 0.015 pp at N ≥ 50,000)")
    ax.axvline(100000, color=C_HIGHLIGHT, ls="--", lw=1, alpha=0.7,
               label="Default N = 100,000")
    ax.legend(loc="upper right", fontsize=9)
    for n, m in zip(N, mean_rmse):
        ax.annotate(f"{m:.3f}", xy=(n, m), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=8.5)
    savefig(fig, "S06_05", "S06_05_F01C_Agent_Count_Plateau__E12_v01.png")


# ---------------------------------------------------------------------------
# S06_05 F01D — Parameter identification standalone
# ---------------------------------------------------------------------------
def fig_s06_05_f01d():
    with open(SRC / "6.5" / "robustness_metrics.json", encoding="utf-8") as fh:
        rob = json.load(fh)
    pl = rob["packageE_calibration"]["param_lens"]["by_param"]
    pl_sorted = sorted(pl, key=lambda r: r["cv"])
    names = [r["param"] for r in pl_sorted]
    cvs = [r["cv"] for r in pl_sorted]
    colors2 = [C_ABM if not r["unstable_top5"] else C_HIGHLIGHT for r in pl_sorted]

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bars = ax.barh(range(len(names)), cvs, color=colors2, edgecolor="white", height=0.66)
    ax.axvline(0.40, color="#555", ls="--", lw=0.9, label="Weak-ID threshold (CV = 0.40)")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("CV across top-5 calibration candidates")
    ax.set_title("Parameter identification — weak-ID threshold CV ≥ 0.40 (10/14 above)")
    ax.set_xlim(0, max(cvs) * 1.18)
    for bar, v in zip(bars, cvs):
        ax.text(bar.get_width() + max(cvs) * 0.012,
                bar.get_y() + bar.get_height()/2,
                f"{v:.2f}", va="center", fontsize=8.5)
    ax.legend(loc="lower right", fontsize=9)
    savefig(fig, "S06_05", "S06_05_F01D_Parameter_ID__E13_v01.png")


# ---------------------------------------------------------------------------
# Experiment-folder figures — copy existing PNGs from fix6.*/figures with new names
# ---------------------------------------------------------------------------
def copy_experiment_figures():
    """Copy existing PNG files to each experiment's figures/ folder with E## naming.
    The S06 paper-ready figures are regenerated above; here we re-use existing fix6.*
    figures for the experiment-folder traceability layer.
    """
    mapping = [
        # (src_path, dst_relative)
        ("fix6.1/figures/fig1_full_period_ur.png", "E04_F01_Observed_vs_Simulated_UR_v01.png"),
        ("fix6.1/figures/fig2_regime_ur_rmse_bar.png", "E05_F01_Regime_RMSE_Bar_v01.png"),
        ("fix6.1/figures/fig3_prediction_error_time.png", "E04_F02_Prediction_Error_Time_v01.png"),
        ("fix6.1/figures/fig4_lfpr_epop_regime_bar.png", "E05_F02_LFPR_EPOP_Regime_Bar_v01.png"),
        ("fix6.2/figures/fig1_variant_ur_rmse_bar.png", "E06_F01_Control_RMSE_Bar_v01.png"),
        ("fix6.2/figures/fig2_source_of_advantage_waterfall.png", "E07_F01_Source_of_Advantage_Waterfall_v01.png"),
        ("fix6.2/figures/fig3_variant_ur_lines.png", "E06_F02_Variant_UR_Lines_v01.png"),
        ("fix6.2/figures/fig4_regime_x_variant_heatmap.png", "E06_F03_Regime_by_Variant_Heatmap_v01.png"),
        ("fix6.2/figures/fig5_within_variant_dispersion.png", "E06_F04_Within_Variant_Dispersion_v01.png"),
        ("fix6.3/figures/fig1_recalibrated_ablation_ur.png", "E08_F01_Ablation_RMSE_Bar_v01.png"),
        ("fix6.3/figures/fig2_old_vs_new_delta.png", "E08_F02_Old_vs_New_Delta_v01.png"),
        ("fix6.3/figures/fig3_regime_x_ablation_heatmap.png", "E08_F03_Regime_by_Ablation_Heatmap_v01.png"),
        ("fix6.3/figures/fig4_no_search_trajectory.png", "E08_F04_NoSearch_Trajectory_v01.png"),
        ("6.3/figures/fig3_heterogeneity_ladder.png", "E09_F01_Ladder_RMSE_Path_v01.png"),
        ("fix6.4/figures/fig1_rmse_bars_postcovid_dynamic.png", "E10_F01_Benchmark_RMSE_Bar_v01.png"),
        ("fix6.4/figures/fig2_ratio_vs_abm.png", "E10_F02_Ratio_vs_ABM_v01.png"),
        ("fix6.4/figures/fig3_paths_postcovid_dynamic.png", "E10_F03_Paths_Dynamic_v01.png"),
        ("fix6.4/figures/fig5_heatmap_model_regime.png", "E10_F04_Regime_by_Benchmark_Heatmap_v01.png"),
        ("6.5/figures/fig2_training_splits.png", "E11_F01_Training_Window_Sensitivity_v01.png"),
        ("6.5/figures/fig3_horizon_slope.png", "E12_F01_Forecast_Horizon_Sensitivity_v01.png"),
        ("6.5/figures/fig4_agent_convergence.png", "E12_F02_Agent_Count_Convergence_v01.png"),
        ("6.5/figures/fig5_calibration_sensitivity.png", "E13_F01_Calibration_Method_Sensitivity_v01.png"),
        ("6.5/figures/fig6_param_drift_heatmap.png", "E13_F02_Parameter_ID_Heatmap_v01.png"),
        ("6.1/figures/fig6_seed_stability.png", "E02_F01_Seed_Stability_v01.png"),
    ]
    exp_root = ROOT / "Results_By_Experiment"
    exp_dirs = {f.name.split("_")[0]: f for f in exp_root.iterdir() if f.is_dir()}
    for src_rel, dst_name in mapping:
        src = SRC / src_rel
        eid = dst_name.split("_")[0]
        if not src.exists():
            print(f"  [skip] {src_rel}: not found")
            continue
        if eid not in exp_dirs:
            print(f"  [skip] {dst_name}: no folder for {eid}")
            continue
        dst = exp_dirs[eid] / "figures" / dst_name
        shutil.copyfile(src, dst)


def _cleanup_legacy_composites():
    """Remove now-superseded composite PNGs in mirror + per-section folders."""
    legacy = [
        ("S06_01", "S06_01_F01_Observed_vs_Simulated_UR__E4_v01.png"),
        ("S06_01", "S06_01_F02_Regime_RMSE_Bar__E5_v01.png"),
        ("S06_05", "S06_05_F01_Robustness_Dashboard__E11_E12_E13_v01.png"),
    ]
    for sid, fname in legacy:
        for p in (sec_fig_dir(sid) / fname,
                  ROOT / "Results_PaperReady_Figures" / fname):
            if p.exists():
                p.unlink()
                print(f"  [removed legacy] {p.name}")


def main():
    builders = [
        fig_s06_01_f01a, fig_s06_01_f01b,
        fig_s06_01_f02a, fig_s06_01_f02b,
        fig_s06_02_f01,
        fig_s06_03_f01, fig_s06_03_f02,
        fig_s06_04_f01,
        fig_s06_05_f01a, fig_s06_05_f01b, fig_s06_05_f01c, fig_s06_05_f01d,
    ]
    for fn in builders:
        try:
            fn()
            print(f"[OK] {fn.__name__}")
        except Exception as exc:
            print(f"[FAIL] {fn.__name__}: {exc}")
            raise
    print("[cleanup_legacy_composites]")
    _cleanup_legacy_composites()
    print("[copy_experiment_figures]")
    copy_experiment_figures()
    print("Done.")


if __name__ == "__main__":
    main()
