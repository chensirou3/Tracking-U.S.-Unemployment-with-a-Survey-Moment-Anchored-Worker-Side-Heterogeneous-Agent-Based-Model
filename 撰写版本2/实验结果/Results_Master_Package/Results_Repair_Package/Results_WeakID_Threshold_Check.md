# Weak-Identification Threshold Check

**Goal:** Resolve the inconsistency between manuscript-facing documents about the weak-identification threshold (0.40 vs 0.50) and lock a single definition.

**Verdict:** The threshold is **CV ≥ 0.40 across the top-5 calibration candidates within a method**. Three independent sources agree; one downstream document was wrong and is patched in this repair package.

---

## 1. Cross-source threshold audit

| Source file | Statement / evidence | Threshold stated | Correct? |
|---|---|---|---|
| `Results_By_Experiment/E13_Calibration_Method_and_Parameter_ID_Sensitivity/E13_Report.md` line 5 | "10 of 14 parameters have CV ≥ 0.40 across top-5 candidates — weakly identified" | **0.40** | YES — primary source |
| `Results_By_Experiment/E13_.../E13_Report.md` line 23 | "Flag parameters as weakly identified if CV ≥ 0.40 in any method." | **0.40** | YES — protocol statement |
| `Results_By_Experiment/E13_.../E13_Report.md` line 38 | Key Numbers: "Weakly identified parameters (CV ≥ 0.40) | 10 of 14" | **0.40** | YES — Key Numbers |
| `Results_By_Experiment/E13_.../tables/E13_T02_Parameter_Identification_v01.csv` | 14 parameter rows with `cv_across_top5` and `status ∈ {WEAK, STABLE}`. The 10 WEAK rows have CV in [0.4230, 0.6426]; the 4 STABLE rows have CV in [0.0640, 0.3636]. The decision boundary sits between 0.3636 (STABLE: wealthy_discount) and 0.4230 (WEAK: h2m_resv_discount). | **0.40** | YES — implied by row-level status flag |
| `Results_PaperReady_Tables/S06_05_T01_Robustness_Summary__E11_E12_E13_v01.csv` row 7 | "10/14 parameters CV ≥ 0.40 across top-5 candidates" | **0.40** | YES — paper-ready table |
| `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226 | "10 of 14 parameters have CV ≥ 0.40 across top-5 candidates; 4 of 14 are stable (CV < 0.20)" | **0.40** for weak; **<0.20** for stable | PARTIAL — the weak threshold 0.40 is correct, but the "<0.20 stable count of 4" is wrong (see §2 below) |
| `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 230 | "ten of fourteen free parameters are weakly identified (cross-candidate CV ≥ 0.40 in at least one calibration method)" | **0.40** | YES |
| `Consistency_Resolution/Results_Final_Wording_Guide.md` line 118 | "10 are weakly identified in the sense that within the top-5 calibration candidates the coefficient of variation exceeds 0.5" | **0.50** | **WRONG** — must be patched to 0.40 |

**Conclusion.** All primary evidence sources (E13_Report, E13_T02, S06_05_T01) use 0.40. Only `Results_Final_Wording_Guide.md` says 0.50, and it is the lone outlier; it must be patched.

---

## 2. Stable-parameter count correction

A secondary inconsistency was found in `E13_Report.md` line 39 and `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226: both state "Stable parameters (CV < 0.20) | 4 of 14". The row-level CV values in `E13_T02_Parameter_Identification_v01.csv` show this is **wrong**.

| Definition | Count | Members (with CV) |
|---|---|---|
| WEAK (CV ≥ 0.40) | 10 | acceptance_pressure 0.5504; duration_thresh 0.4486; emp_adapt_speed 0.6426; exit_jump 0.5896; h2m_resv_discount 0.4230; lockin_penalty 0.5899; optimism_entry 0.4891; pessimism_exit 0.4325; reentry_penalty 0.4966; unemp_adapt_speed 0.4357 |
| STABLE (CV < 0.40; complement of WEAK) | 4 | fragility_threshold 0.2222; h2m_mpc_floor 0.0640; vacancy_rate 0.3339; wealthy_discount 0.3636 |
| Strictly stable (CV < 0.20) | **1** | h2m_mpc_floor 0.0640 only |
| Borderline (0.20 ≤ CV < 0.40) | 3 | fragility_threshold 0.2222; vacancy_rate 0.3339; wealthy_discount 0.3636 |

**Required wording (paste-ready).** The "4 stable" phrasing only works if it is defined as **CV < 0.40**, i.e., the complement of WEAK. If a tighter threshold is desired (CV < 0.20), only **one** parameter qualifies.

---

## 3. Locked threshold and counts

| Quantity | Locked value |
|---|---|
| Weak-ID threshold | **CV ≥ 0.40 across the top-5 calibration candidates within a method** |
| Weakly identified parameter count | **10 of 14** |
| Stable parameter count (CV < 0.40) | **4 of 14** |
| Strictly stable parameter count (CV < 0.20) | **1 of 14** (h2m_mpc_floor only) |
| Weakly identified parameters | acceptance_pressure, duration_thresh, emp_adapt_speed, exit_jump, h2m_resv_discount, lockin_penalty, optimism_entry, pessimism_exit, reentry_penalty, unemp_adapt_speed |
| Stable parameters (CV < 0.40) | fragility_threshold, h2m_mpc_floor, vacancy_rate, wealthy_discount |

---

## 4. Required wording patches

### 4.1 `Consistency_Resolution/Results_Final_Wording_Guide.md` line 118 — paste-ready replacement

> "Of the 14 calibrated parameters, 10 are weakly identified in the sense that within the top-5 calibration candidates the coefficient of variation reaches or exceeds 0.40 in at least one calibration method; the reported parameter values are fitted simulation inputs, not structural estimates."

### 4.2 `Consistency_Resolution/Results_Consistency_Resolution_Report.md` line 226 — paste-ready replacement

> "10 of 14 parameters have CV ≥ 0.40 across top-5 candidates within at least one calibration method; the remaining 4 of 14 are below this threshold (only 1 of 14 — `h2m_mpc_floor` — is strictly stable at CV < 0.20). Co-report with every parameter mention; report parameters as bands."

### 4.3 `E13_Report.md` line 39 — paste-ready replacement

> | Stable parameters (CV < 0.40) | 4 of 14 |

(Optionally add a second row for the stricter definition: `| Strictly stable parameters (CV < 0.20) | 1 of 14 |`.)

---

## 5. Required main-text wording (locked)

When parameter values are cited anywhere in §6 (most commonly in §6.5 and as a footnote in §6.2), include exactly one of the following sentences at first mention:

> "Of the 14 calibrated parameters, 10 are weakly identified across the top-5 calibration candidates (coefficient of variation ≥ 0.40 in at least one calibration method). Parameter values are reported as bands."

or, if space is tight:

> "Ten of the fourteen calibrated parameters are weakly identified under the top-candidate dispersion diagnostic (CV ≥ 0.40)."

### Banned variants

- ❌ "CV exceeds 0.5" (numerically wrong)
- ❌ "all parameters are stable except a few" (10/14 is most, not a few)
- ❌ "structurally identified" (parameter values are fitted simulation inputs)
- ❌ "weakly identified parameters but the model is structurally correct" (mixes calibration with structural claims)

---

## 6. Status

- Threshold: **CONFIRMED at 0.40**.
- Wording Guide line 118: **PATCHED** (CV exceeds 0.5 → CV ≥ 0.40).
- Consistency_Resolution_Report line 226: **PATCHED** (now matches §4.2 paste-ready text).
- E13_Report lines 38–39: **PATCHED** — Key Numbers now reports `Stable (CV < 0.40) 4 of 14` plus `Strictly stable (CV < 0.20) 1 of 14 (h2m_mpc_floor only)`.
- Stable-count inconsistency: **RESOLVED** across all manuscript-facing documents.
