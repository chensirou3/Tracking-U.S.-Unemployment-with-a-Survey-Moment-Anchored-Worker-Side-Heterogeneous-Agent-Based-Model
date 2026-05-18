"""
Section 6.5 — build CSV tables and PNG figures from robustness_metrics.json.

Output:
  tables/table1_phase7_robustness.csv
  tables/table2_training_window.csv
  tables/table3_horizon.csv
  tables/table4_agent_count.csv
  tables/table5_calibration_method.csv
  tables/table6_paper_ready_compact.csv
  figures/fig1_robustness_overview.png
  figures/fig2_training_splits.png
  figures/fig3_horizon_slope.png
  figures/fig4_agent_convergence.png
  figures/fig5_calibration_sensitivity.png
  figures/fig6_param_drift_heatmap.png
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({"figure.dpi": 110, "savefig.dpi": 160,
                     "axes.grid": True, "grid.alpha": 0.3,
                     "font.size": 10, "axes.titlesize": 11})

ROOT = Path(__file__).resolve().parent
TBL = ROOT / "tables"; TBL.mkdir(exist_ok=True)
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
M = json.loads((ROOT / "robustness_metrics.json").read_text(encoding="utf-8"))


# ---------------- Table 1: Phase 7 R1..R4 ----------------
def table1() -> None:
    rows = []
    r1 = M["phase7_robustness"]["R1_multi_seed"]
    for k, v in r1.items():
        rows.append({"block": "R1_multi_seed", "variant": k,
                     "ur_rmse_mean_pp": round(v["ur_rmse_mean_pp"], 4),
                     "ur_rmse_std_pp":  round(v["ur_rmse_std_pp"], 4),
                     "cv":              round(v["cv"], 4),
                     "note": "5 seeds {42,137,2024,888,1234}"})
    for k, v in M["phase7_robustness"]["R2_init_window"].items():
        rows.append({"block": "R2_init_window", "variant": k,
                     "ur_rmse_mean_pp": round(v["ur_rmse_pp"], 4),
                     "ur_rmse_std_pp":  np.nan, "cv": 0.0,
                     "note": f"lfpr_rmse_pp={v['lfpr_rmse_pp']:.3f}, ur_corr={v['ur_corr']:.3f}"})
    for k, v in M["phase7_robustness"]["R3_weight_perturb"].items():
        rows.append({"block": "R3_weight_perturb", "variant": k,
                     "ur_rmse_mean_pp": np.nan, "ur_rmse_std_pp": np.nan, "cv": np.nan,
                     "note": f"composite={v['composite_loss']:.4f}, ur_comp={v['ur_component']:.4f}, "
                             f"tier2={v['tier2_component']:.4f}"})
    for k, v in M["phase7_robustness"]["R4_informal_work"].items():
        if not k.startswith("beta_"):
            continue
        rows.append({"block": "R4_informal_work", "variant": k,
                     "ur_rmse_mean_pp": round(v["rmse_vs_adjusted_target_pp"], 4),
                     "ur_rmse_std_pp": np.nan, "cv": np.nan,
                     "note": v["interpretation"]})
    pd.DataFrame(rows).to_csv(TBL / "table1_phase7_robustness.csv", index=False)


# ---------------- Table 2: training window (Package A) ----------------
def table2() -> None:
    cmp = pd.DataFrame(M["packageA_training_window"]["comparison_table"])
    reg = pd.DataFrame(M["packageA_training_window"]["registry"])
    out = cmp.merge(reg[["split_id", "train_date_start", "train_date_end",
                         "test_date_start", "test_date_end", "train_len"]],
                    left_on="split", right_on="split_id", how="left")
    out["M0_rank"] = out[["M0_Main", "D1_Homogeneous", "D2_Simplified",
                          "D3_LaborOnly", "B1_AR", "B2_VAR",
                          "B3_Beveridge", "B4_DMP"]].rank(axis=1).iloc[:, 0]
    keep = ["split", "type", "train_date_start", "train_date_end", "train_len",
            "test_date_start", "test_date_end",
            "M0_Main", "D1_Homogeneous", "D3_LaborOnly",
            "B3_Beveridge", "B4_DMP", "M0_rank"]
    out[keep].to_csv(TBL / "table2_training_window.csv", index=False, float_format="%.4f")


# ---------------- Table 3: horizon degradation (Package B) ----------------
def table3() -> None:
    pivot = pd.DataFrame(M["packageB_horizon"]["horizon_rmse_pivot_pp"])
    deg   = pd.DataFrame(M["packageB_horizon"]["degradation_table"])
    out   = pivot.merge(deg[["model", "log_log_slope", "abs_change_pp"]],
                        on="model", how="left")
    out.to_csv(TBL / "table3_horizon.csv", index=False, float_format="%.4f")


# ---------------- Table 4: agent count (Package D) ----------------
def table4() -> None:
    per = pd.DataFrame(M["packageD_agent_count"]["per_cell"])
    m0 = per[(per["model"] == "M0") & (per["mode"] == "regenerate")][
        ["N", "ur_rmse_pp_mean", "ur_rmse_pp_std", "runtime_s_mean", "peak_mem_mb_mean"]
    ].rename(columns={"ur_rmse_pp_mean": "M0_rmse_mean_pp",
                      "ur_rmse_pp_std":  "M0_rmse_std_pp",
                      "runtime_s_mean":  "runtime_s",
                      "peak_mem_mb_mean": "peak_mem_mb"})
    m0 = m0.sort_values("N")
    base = m0.iloc[0]["M0_rmse_mean_pp"]
    m0["delta_vs_prev_pp"] = m0["M0_rmse_mean_pp"].diff()
    m0["plateau_flag"] = m0["delta_vs_prev_pp"].abs() < 0.015
    m0.to_csv(TBL / "table4_agent_count.csv", index=False, float_format="%.4f")


# ---------------- Table 5: calibration method (Package E) ----------------
def table5() -> None:
    per = pd.DataFrame(M["packageE_calibration"]["per_method"])
    soa = pd.DataFrame(M["packageE_calibration"]["soa_per_method"])
    out = per.merge(soa[["method_id", "share_heterogeneity_pct", "share_household_pct"]],
                    on="method_id", how="left")
    keep = ["method_id", "n_evals", "best_train_loss", "best_test_ur_rmse_pp",
            "top5_test_ur_mean", "top5_test_ur_std",
            "share_heterogeneity_pct", "share_household_pct",
            "total_runtime_min"]
    out[keep].to_csv(TBL / "table5_calibration_method.csv", index=False, float_format="%.4f")


# ---------------- Table 6: compact paper-ready summary ----------------
def table6() -> None:
    rows = [
        {"dimension": "Multi-seed",
         "metric": "OOS UR RMSE CV across 5 seeds",
         "value":  f"{M['phase7_robustness']['R1_multi_seed']['baseline']['cv']*100:.2f}%",
         "verdict": "ROBUST"},
        {"dimension": "Initialisation window",
         "metric": "UR RMSE range across init={24,36,48}",
         "value":  "0.000 pp (identical)",
         "verdict": "ROBUST"},
        {"dimension": "UR-loss weight (3, 5, 7)",
         "metric": "Δ tier-2 component", "value": "0.000",
         "verdict": "ROBUST (tier-2 unchanged)"},
        {"dimension": "Informal-work β (0, 0.5, 1)",
         "metric": "RMSE vs adjusted target (raw → β=1)",
         "value": "0.232 → 0.482 pp",
         "verdict": "TARGET-DEFINITION SENSITIVE (post-hoc adjustment)"},
        {"dimension": "Training window (10 splits)",
         "metric": "M0 win-rate vs B3 Beveridge; mean RMSE on 7 OOS-window splits",
         "value": "10/10 wins; 0.245 ± 0.011 pp",
         "verdict": "ROBUST"},
        {"dimension": "Parameter drift",
         "metric": "# params with CV ≥ 0.30 across 10 splits",
         "value": "0 of 14 (8 stable, 6 mild)",
         "verdict": "ROBUST"},
        {"dimension": "Forecast horizon h=1..36",
         "metric": "M0 log-log RMSE slope",
         "value": "-0.092 (shallowest of 8 models)",
         "verdict": "ROBUST"},
        {"dimension": "Agent count N=5k..300k",
         "metric": "Plateau threshold |ΔRMSE|<0.015 pp",
         "value": "satisfied at N ≥ 50k",
         "verdict": "ROBUST (default 100k well past plateau)"},
        {"dimension": "Calibration method (5 methods)",
         "metric": "CV of best-test UR RMSE",
         "value": "5.55% (range 0.214–0.243 pp)",
         "verdict": "PREDICTION ROBUST"},
        {"dimension": "Calibration method — parameters",
         "metric": "# params with top-5 CV ≥ 0.40 in any method",
         "value": "10 of 14",
         "verdict": "PARAMETERS WEAKLY IDENTIFIED"},
        {"dimension": "Calibration method — advantage",
         "metric": "share_heterogeneity mean ± SD across methods",
         "value": "57.2 ± 3.35 pp",
         "verdict": "ROBUST"},
    ]
    pd.DataFrame(rows).to_csv(TBL / "table6_paper_ready_compact.csv", index=False)


# ---------------- Figure 1: robustness overview (R1..R4) ----------------
def fig1() -> None:
    fig, axs = plt.subplots(1, 4, figsize=(15, 3.6))

    # R1: 5-seed mean+/-1sd for the three loss-weight variants
    r1 = M["phase7_robustness"]["R1_multi_seed"]
    labels = list(r1.keys())
    means  = [r1[k]["ur_rmse_mean_pp"] for k in labels]
    sds    = [r1[k]["ur_rmse_std_pp"]  for k in labels]
    axs[0].bar(labels, means, yerr=sds, capsize=5,
               color=["#4c72b0", "#dd8452", "#55a467"])
    axs[0].axhline(0.221, color="grey", ls="--", lw=0.8, label="Sec 6.1 baseline")
    axs[0].set_title("R1 multi-seed (5 seeds)\nUR RMSE mean ± 1σ")
    axs[0].set_ylabel("OOS UR RMSE (pp)")
    axs[0].legend(fontsize=8); axs[0].set_ylim(0, 0.32)

    # R2: init window
    r2 = M["phase7_robustness"]["R2_init_window"]
    xs = list(r2.keys()); vals = [r2[k]["ur_rmse_pp"] for k in xs]
    axs[1].bar(xs, vals, color="#4c72b0")
    axs[1].set_title("R2 init window\n(identical across {24,36,48})")
    axs[1].set_ylabel("OOS UR RMSE (pp)")
    axs[1].set_ylim(0, 0.32)

    # R3: weight perturb -- show composite vs ur component
    r3 = M["phase7_robustness"]["R3_weight_perturb"]
    ks = list(r3.keys())
    ur  = [r3[k]["ur_component"]  for k in ks]
    tr2 = [r3[k]["tier2_component"] for k in ks]
    width = 0.35
    x = np.arange(len(ks))
    axs[2].bar(x - width / 2, ur,  width, label="UR component",      color="#4c72b0")
    axs[2].bar(x + width / 2, tr2, width, label="Tier-2 component",  color="#dd8452")
    axs[2].set_xticks(x); axs[2].set_xticklabels(ks, fontsize=8)
    axs[2].set_title("R3 UR-loss weight perturbation\n(tier-2 invariant)")
    axs[2].legend(fontsize=8)

    # R4: informal-work beta
    r4 = M["phase7_robustness"]["R4_informal_work"]
    betas = [k for k in r4 if k.startswith("beta_")]
    vals  = [r4[k]["rmse_vs_adjusted_target_pp"] for k in betas]
    axs[3].plot(betas, vals, "o-", color="#c44e52")
    axs[3].set_title("R4 informal-work β\n(RMSE vs adjusted target)")
    axs[3].set_ylabel("RMSE (pp)")
    axs[3].set_ylim(0, max(vals) * 1.15)

    plt.tight_layout(); plt.savefig(FIG / "fig1_robustness_overview.png")
    plt.close(fig)


# ---------------- Figure 2: training splits (Package A) ----------------
def fig2() -> None:
    cmp = pd.DataFrame(M["packageA_training_window"]["comparison_table"])
    splits = cmp["split"].tolist()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(len(splits))
    models = [("M0_Main", "#4c72b0", "M0 Main"),
              ("D1_Homogeneous", "#dd8452", "D1 Homogeneous"),
              ("D3_LaborOnly",   "#55a467", "D3 Labor-only"),
              ("B3_Beveridge",   "#c44e52", "B3 Beveridge")]
    width = 0.20
    for i, (col, c, lab) in enumerate(models):
        ax.bar(x + (i - 1.5) * width, cmp[col], width, color=c, label=lab)
    ax.set_xticks(x); ax.set_xticklabels(splits, rotation=0, fontsize=9)
    ax.set_ylabel("Per-split test UR RMSE (pp)")
    ax.set_title("Package A — training-window sensitivity (10 splits)")
    ax.axhline(0.221, color="grey", ls="--", lw=0.8, label="Sec 6.1 baseline (0.221 pp)")
    ax.legend(fontsize=8, ncol=5)
    plt.tight_layout(); plt.savefig(FIG / "fig2_training_splits.png"); plt.close(fig)


# ---------------- Figure 3: horizon slope (Package B) ----------------
def fig3() -> None:
    piv = pd.DataFrame(M["packageB_horizon"]["horizon_rmse_pivot_pp"])
    horizons = [int(c) for c in piv.columns if c != "model"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = {"M0_Main": "#4c72b0", "D1_Homogeneous": "#dd8452",
              "D3_LaborOnly": "#55a467", "B1_AR": "#c44e52",
              "B2_VAR": "#8172b2", "B3_Beveridge": "#937860",
              "B4_DMP": "#da8bc3"}
    for _, row in piv.iterrows():
        ys = [row[str(h)] for h in horizons]
        ax.plot(horizons, ys, "o-", label=row["model"],
                color=colors.get(row["model"], "grey"),
                lw=(2.0 if row["model"] == "M0_Main" else 1.0))
    ax.set_xscale("log"); ax.set_xticks(horizons)
    ax.set_xticklabels([str(h) for h in horizons])
    ax.set_xlabel("Forecast horizon h (months, log scale)")
    ax.set_ylabel("OOS UR RMSE (pp)")
    ax.set_title("Package B — horizon degradation (M0 slope = -0.09)")
    ax.legend(fontsize=8, ncol=2)
    plt.tight_layout(); plt.savefig(FIG / "fig3_horizon_slope.png"); plt.close(fig)


# ---------------- Figure 4: agent-count convergence (Package D) ----------------
def fig4() -> None:
    curve = M["packageD_agent_count"]["M0_regen_curve_pp"]
    Ns = [r["N"] for r in curve]
    means = [r["rmse_mean"] for r in curve]
    sds   = [r["rmse_std"]  for r in curve]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.errorbar(Ns, means, yerr=sds, fmt="o-", capsize=4,
                color="#4c72b0", lw=1.6, label="M0 mean ± 1σ (10 seeds)")
    ax.axhspan(min(means) - 0.015, min(means) + 0.015, color="grey", alpha=0.15,
               label="±0.015 pp plateau band")
    ax.set_xscale("log"); ax.set_xticks(Ns)
    ax.set_xticklabels([f"{n//1000}k" for n in Ns], fontsize=9)
    ax.set_xlabel("Synthetic-population size N (log)")
    ax.set_ylabel("OOS UR RMSE (pp)")
    ax.set_title("Package D — population-size convergence (plateau ≈ N=50k)")
    ax.legend(fontsize=9); plt.tight_layout()
    plt.savefig(FIG / "fig4_agent_convergence.png"); plt.close(fig)


# ---------------- Figure 5: calibration sensitivity (Package E) ----------------
def fig5() -> None:
    per = pd.DataFrame(M["packageE_calibration"]["per_method"])
    soa = pd.DataFrame(M["packageE_calibration"]["soa_per_method"])
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))

    axs[0].bar(per["method_id"], per["best_test_ur_rmse_pp"], color="#4c72b0", alpha=0.8)
    axs[0].errorbar(per["method_id"], per["top5_test_ur_mean"],
                    yerr=per["top5_test_ur_std"], fmt="o", color="#c44e52",
                    capsize=5, label="top-5 mean ± SD")
    axs[0].axhline(0.221, color="grey", ls="--", lw=0.8, label="Sec 6.1 baseline")
    axs[0].set_ylabel("Test UR RMSE (pp)")
    axs[0].set_title("E1 — test UR by calibration method")
    axs[0].legend(fontsize=8)

    axs[1].bar(soa["method_id"], soa["share_heterogeneity_pct"], color="#55a467", alpha=0.85)
    mean = soa["share_heterogeneity_pct"].mean()
    sd   = soa["share_heterogeneity_pct"].std(ddof=1)
    axs[1].axhline(mean, color="black", ls="-",  lw=1.0,
                   label=f"mean {mean:.1f} %")
    axs[1].axhspan(mean - sd, mean + sd, color="grey", alpha=0.2,
                   label=f"±1σ = {sd:.2f} pp")
    axs[1].set_ylabel("share_heterogeneity (%)")
    axs[1].set_title("E2 — heterogeneity-advantage share")
    axs[1].legend(fontsize=8)

    plt.tight_layout(); plt.savefig(FIG / "fig5_calibration_sensitivity.png"); plt.close(fig)



# ---------------- Figure 6: parameter drift / stability heatmap ----------------
def fig6() -> None:
    """Two-panel heatmap:
       (a) Package A parameter CV across 10 splits (one column per param);
       (b) Package E top-5 parameter CV across 5 methods.
    """
    pkgA = pd.DataFrame(M["packageA_training_window"]["param_drift_summary"]["params"])
    pkgE = pd.DataFrame(M["packageE_calibration"]["param_stability"])

    params = pkgA["param"].tolist()
    methods = sorted(pkgE["method_id"].unique().tolist())
    Z = np.full((len(methods), len(params)), np.nan)
    for i, m in enumerate(methods):
        sub = pkgE[pkgE["method_id"] == m].set_index("param")["cv"]
        for j, p in enumerate(params):
            if p in sub.index:
                Z[i, j] = sub.loc[p]

    fig, axs = plt.subplots(2, 1, figsize=(11, 5.2),
                            gridspec_kw={"height_ratios": [1, 1.6]})

    cvA = pkgA["cv"].to_numpy().reshape(1, -1)
    im0 = axs[0].imshow(cvA, aspect="auto", cmap="YlOrRd", vmin=0, vmax=0.30)
    axs[0].set_yticks([0]); axs[0].set_yticklabels(["Package A — 10 splits"])
    axs[0].set_xticks(range(len(params)))
    axs[0].set_xticklabels(params, rotation=30, ha="right", fontsize=8)
    axs[0].set_title("Parameter CV across training windows (cap 0.30; "
                     "0 of 14 above threshold)")
    fig.colorbar(im0, ax=axs[0], fraction=0.05, pad=0.02).set_label("CV")

    im1 = axs[1].imshow(Z, aspect="auto", cmap="YlOrRd", vmin=0, vmax=0.7)
    axs[1].set_yticks(range(len(methods))); axs[1].set_yticklabels(methods)
    axs[1].set_xticks(range(len(params)))
    axs[1].set_xticklabels(params, rotation=30, ha="right", fontsize=8)
    axs[1].set_title("Package E — top-5 CV by calibration method "
                     "(red = weakly identified)")
    fig.colorbar(im1, ax=axs[1], fraction=0.05, pad=0.02).set_label("top-5 CV")

    plt.tight_layout(); plt.savefig(FIG / "fig6_param_drift_heatmap.png")
    plt.close(fig)


def main() -> None:
    for fn in (table1, table2, table3, table4, table5, table6,
               fig1,   fig2,   fig3,   fig4,   fig5,   fig6):
        print(f"[6.5] running {fn.__name__}")
        fn()
    print("[6.5] all artefacts written under", ROOT)


if __name__ == "__main__":
    main()
