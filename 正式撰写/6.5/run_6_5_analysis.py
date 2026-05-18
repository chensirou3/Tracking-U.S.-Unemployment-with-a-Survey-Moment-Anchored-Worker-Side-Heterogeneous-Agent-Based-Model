"""
Section 6.5 — Robustness & Sensitivity: analysis driver.

Reads previously computed Phase 7 / Package A / Package B / Package D / Package E
outputs, re-verifies the key summary statistics on the fly (no new simulations),
normalises everything to percentage-points (pp) on the unemployment-rate target,
and emits one consolidated JSON used by build_6_5_artifacts.py.

All RMSE numbers in the emitted file are in pp.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT  = Path(__file__).resolve().parent
PHASE3 = REPO / "Phase3_Output"


def _load_phase7_robustness() -> dict:
    raw = json.loads((PHASE3 / "phase7" / "robustness_results.json").read_text())

    # R1 stored in fraction units -> convert to pp
    r1 = {}
    for k, v in raw["R1_multi_seed"].items():
        r1[k] = {
            "ur_rmse_mean_pp": v["ur_rmse_mean"] * 100.0,
            "ur_rmse_std_pp":  v["ur_rmse_std"]  * 100.0,
            "cv":              v["cv"],
        }

    r2 = {k: {"ur_rmse_pp": v["ur_rmse"] * 100.0,
              "lfpr_rmse_pp": v["lfpr_rmse"] * 100.0,
              "ur_corr": v["ur_corr"]}
          for k, v in raw["R2_init_window"].items()}

    r3 = {k: dict(v) for k, v in raw["R3_weight_perturb"].items()}

    r4 = {k: {"rmse_vs_adjusted_target_pp": v["rmse_vs_adjusted_target"] * 100.0,
              "interpretation": v["interpretation"]}
          for k, v in raw["R4_informal_work"].items()
          if k.startswith("beta_")}
    r4["meta"] = {"p_side_U": raw["R4_informal_work"]["p_side_U"],
                   "notes":    raw["R4_informal_work"]["notes"]}

    return {"R1_multi_seed": r1, "R2_init_window": r2,
            "R3_weight_perturb": r3, "R4_informal_work": r4}


def _load_packageA() -> dict:
    cmp_t = pd.read_csv(PHASE3 / "packageA" / "comparison_table.csv")
    pdrift = pd.read_csv(PHASE3 / "packageA" / "parameter_drift.csv")
    reg = pd.read_csv(PHASE3 / "packageA" / "split_registry.csv")

    # 7 splits cover the Section 6.1 OOS window (S0, R4, E1..E5)
    canonical = ["S0", "R4", "E1", "E2", "E3", "E4", "E5"]
    canon_mask = cmp_t["split"].isin(canonical)
    canon = cmp_t.loc[canon_mask].set_index("split")

    summary = {
        "canonical_splits": canonical,
        "M0_main_OOS_window_rmse_pp": {
            "mean": float(canon["M0_Main"].mean()),
            "std":  float(canon["M0_Main"].std(ddof=1)),
            "min":  float(canon["M0_Main"].min()),
            "max":  float(canon["M0_Main"].max()),
        },
        "M0_full_10splits_rmse_pp": {
            "mean": float(cmp_t["M0_Main"].mean()),
            "std":  float(cmp_t["M0_Main"].std(ddof=1)),
        },
        "win_rates_vs_M0": {},
        "param_drift_summary": {
            "n_stable_cv_lt_0_10":   int((pdrift["cv"] < 0.10).sum()),
            "n_mild_0_10_to_0_30":   int(((pdrift["cv"] >= 0.10) & (pdrift["cv"] < 0.30)).sum()),
            "n_significant_cv_ge_0_30": int((pdrift["cv"] >= 0.30).sum()),
            "max_cv": float(pdrift["cv"].max()),
            "params": pdrift.to_dict(orient="records"),
        },
    }

    for col in ["D1_Homogeneous", "D2_Simplified", "D3_LaborOnly",
                "B1_AR", "B2_VAR", "B3_Beveridge", "B4_DMP"]:
        wins = int((cmp_t["M0_Main"] < cmp_t[col]).sum())
        summary["win_rates_vs_M0"][col] = {"wins": wins, "n_splits": int(len(cmp_t))}

    summary["comparison_table"] = cmp_t.to_dict(orient="records")
    summary["registry"] = reg.to_dict(orient="records")
    return summary


def _load_packageB() -> dict:
    pivot = pd.read_csv(PHASE3 / "packageB" / "horizon_rmse_pivot.csv")
    deg   = pd.read_csv(PHASE3 / "packageB" / "horizon_degradation_table.csv")
    return {"horizon_rmse_pivot_pp": pivot.to_dict(orient="records"),
            "degradation_table":     deg.to_dict(orient="records"),
            "horizons":              [int(c) for c in pivot.columns[1:]]}


def _load_packageD() -> dict:
    agg = pd.read_csv(PHASE3 / "packageD" / "agent_count_aggregated.csv")
    mc  = pd.read_csv(PHASE3 / "packageD" / "mc_noise_scaling.csv")
    cost = pd.read_csv(PHASE3 / "packageD" / "cost_scaling.csv")
    m0 = agg[(agg["model"] == "M0") & (agg["mode"] == "regenerate")]
    return {"per_cell": agg.to_dict(orient="records"),
            "M0_regen_curve_pp": [
                {"N": int(r["N"]),
                 "rmse_mean": float(r["ur_rmse_pp_mean"]),
                 "rmse_std":  float(r["ur_rmse_pp_std"]),
                 "runtime_s": float(r["runtime_s_mean"])}
                for _, r in m0.iterrows()],
            "mc_noise_scaling": mc.to_dict(orient="records"),
            "cost_scaling": cost.to_dict(orient="records")}


def _load_packageE() -> dict:
    agg = pd.read_csv(PHASE3 / "packageE" / "method_aggregated.csv")
    stab = pd.read_csv(PHASE3 / "packageE" / "param_stability.csv")
    soa = pd.read_csv(PHASE3 / "packageE" / "source_of_advantage_per_method.csv")

    test_rmse = agg["best_test_ur_rmse_pp"].to_numpy()
    train     = agg["best_train_loss"].to_numpy()
    share_h   = soa["share_heterogeneity_pct"].to_numpy()

    method_max_cv = stab.groupby("param")["cv"].max().reset_index()
    method_max_cv["unstable_top5"] = method_max_cv["cv"] >= 0.4

    return {"per_method": agg.to_dict(orient="records"),
            "performance_lens": {
                "cv_best_train_loss": float(train.std(ddof=1) / train.mean()),
                "cv_best_test_ur":    float(test_rmse.std(ddof=1) / test_rmse.mean()),
                "best_test_min_pp":   float(test_rmse.min()),
                "best_test_max_pp":   float(test_rmse.max()),
            },
            "advantage_lens": {
                "share_het_mean_pct": float(share_h.mean()),
                "share_het_std_pct":  float(share_h.std(ddof=1)),
            },
            "param_lens": {
                "n_unstable_params": int(method_max_cv["unstable_top5"].sum()),
                "n_total_params":    int(len(method_max_cv)),
                "by_param":          method_max_cv.to_dict(orient="records"),
            },
            "soa_per_method":   soa.to_dict(orient="records"),
            "param_stability":  stab.to_dict(orient="records")}


def main() -> None:
    metrics = {
        "meta": {
            "oos_window": "2022-01..2026-02 (49 valid months for UR)",
            "baseline_ur_rmse_pp": 0.2211,
            "seeds":        [42, 137, 2024, 888, 1234],
            "sources": {
                "phase7": "Phase3_Output/phase7/robustness_results.json",
                "packageA": "Phase3_Output/packageA/{comparison_table,parameter_drift,split_registry}.csv",
                "packageB": "Phase3_Output/packageB/{horizon_rmse_pivot,horizon_degradation_table}.csv",
                "packageD": "Phase3_Output/packageD/{agent_count_aggregated,mc_noise_scaling,cost_scaling}.csv",
                "packageE": "Phase3_Output/packageE/{method_aggregated,param_stability,source_of_advantage_per_method}.csv",
            },
        },
        "phase7_robustness": _load_phase7_robustness(),
        "packageA_training_window": _load_packageA(),
        "packageB_horizon":         _load_packageB(),
        "packageD_agent_count":     _load_packageD(),
        "packageE_calibration":     _load_packageE(),
    }
    out_path = OUT / "robustness_metrics.json"
    out_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"[6.5] wrote {out_path}")
    print(f"[6.5] keys: {list(metrics.keys())}")


if __name__ == "__main__":
    main()
