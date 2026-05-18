# Results §6.5 — Revised Robustness Synthesis (Preparation Report)

**Scope.** §6.5 consolidates the robustness evidence accumulated across the
revised §6.1 (regime-decomposed OOS), §6.2 (recalibrated controls), §6.3
(recalibrated ablation), §6.4 (stronger benchmarks), and the legacy Phase 7 /
Package A–E tests. No new simulations are run here; all numbers are pulled
verbatim from the upstream artefacts listed in the appendix.

---

## 1. Purpose and audit position

§6.1–§6.4 successively forced the model through four independent stress tests
(regime decomposition, separately-recalibrated controls, separately-recalibrated
ablation, stronger statistical/econometric benchmarks). §6.5 asks a single
question:

> Which of the robustness statements that the Phase 6 / Phase 7 version of the
> paper made about the heterogeneous ABM still hold once each downstream
> section has been re-run with the revised, more demanding protocol — and
> which have to be softened or retracted?

The synthesis is therefore explicitly an *honesty audit*. It declares which
claims survive (and with what caveats), which need softer wording, and which
should be moved to a "limitations" sub-section.

## 2. Headline answer

The model is **robust within the post-COVID normalization regime**, **not**
robust across regime transitions, and its **parameter-level identification is
weak even though its predictive output is method-invariant**.

| Layer | Verdict |
| --- | --- |
| Post-COVID UR tracking (the headline number) | **Survives** — 0.221 pp baseline, 0.273 pp recalibrated |
| Heterogeneity advantage as *fact* | **Survives** — Full beats Simplified after both are recalibrated |
| Heterogeneity advantage as *magnitude* | **Softened** — gap 2.116 → 0.288 pp |
| Three-mechanism (Search / Liq / Hous) story | **Reduced** — only Search Friction survives recalibrated ablation |
| Benchmark superiority | **Competitive** — rank 1 of 12 by 0.036 pp; tied within seed s.d. |
| Cross-regime robustness | **Retract** — crisis −2.07 pp bias, pre-COVID +0.77 pp bias |
| Structural read of individual parameters | **Retract** — 10/14 weakly identified |

## 3. Ten robustness dimensions (Table 1)

See `tables/table1_revised_robustness_summary.csv`. Each row gives the
dimension, the headline number, what it supports, and the caveat that must
travel with it. The first four rows are *revised* (this paper's new evidence);
rows 5–10 are *legacy* invariants that we re-state because they describe
properties of the model class (seed noise, agent-count convergence, horizon
behaviour, calibration-method invariance) and are unaffected by the §6.2/§6.3
recalibration protocol.

## 4. Old claim vs revised claim (Table 2)

`tables/table2_old_vs_revised_claims.csv` enumerates six claim families and
matches each old claim to the revised evidence and the revised, defensible
claim. The deltas in plain prose:

1. **Broad OOS prediction → post-COVID-only.** The 0.21 pp number was an
   average over a window that masked a +0.77 pp pre-COVID bias and a −2.07 pp
   crisis bias.
2. **Heterogeneity 97.6% → 94.2%, magnitude 2.116 → 0.288 pp.** The
   97.6 / 2.116 figures over-stated the gap because the original controls were
   evaluated at the heterogeneous-ABM's calibrated parameters, putting them
   off their own best fit.
3. **Three mechanisms → one mechanism.** Recalibrated ablation collapses Liq
   and Hous near zero (+0.105 and −0.036 pp); only Search Friction retains a
   large standalone ablation effect (+0.812 pp).
4. **"Beats all benchmarks" → "competitive with no-change / ETS".** ABM is
   rank 1 of 12 in the post-COVID dynamic protocol by 0.036 pp, within the
   ±0.023 pp seed s.d. of V_Full.
5. **Cross-regime robust → post-COVID-regime robust.** Crisis and pre-COVID
   windows are not predicted at acceptable accuracy.
6. **14 parameters identified → 10/14 weakly identified.** Predictions are
   method-invariant (CV 5.55%) but parameters are not.

## 5. Paper-ready compact table (Table 3)

`tables/table3_paper_ready_compact.csv` collapses §6.5 to six lines, each with
a number and an interpretation, suitable for direct inclusion in the main
text. This is what the reader sees if §6.5 has to fit on a single page.

## 6. The legacy Phase 7 / Package A–E layer

Multi-seed (3.08% CV), init-window {24,36,48} (0 pp range), tier-2 loss-weight
sweep (Δ=0), Package A 10-split train-window (0.245 ± 0.011 pp; 0/14 drifting
parameters), Package B horizon slope (−0.092, shallowest of 8 models),
Package D agent-count plateau (|ΔRMSE| < 0.015 pp at N ≥ 50k), Package E
calibration-method CV (5.55%, range 0.214–0.243 pp). These are properties of
the model *class* (M0 / V_Full architecture); they were computed once and do
not need re-running per recalibrated variant. We re-state them for
completeness and note explicitly that they refer to the Phase 6 baseline, not
to the recalibrated variants of §6.2/§6.3.

## 7. The new parameter-identification caveat

The most consequential addition is the *weak identification* row:
**10 of 14 parameters have top-5 CV ≥ 0.40 across calibration methods**
while predictions are method-invariant (CV 5.55%, range 0.214–0.243 pp). This
is the formal justification for reporting all behavioural parameters as bands
in §5 and for refusing structural interpretation of individual coefficients in
the discussion.

## 8. What is *not* covered by §6.5

(a) Stronger benchmarks (§6.4) were run only at the post-COVID dynamic
protocol with the §6.2 V_Full ABM. Multi-seed dispersion for the benchmark
panel itself was not re-computed (benchmarks are deterministic conditional on
data, so this is not an issue for them; the ABM s.d. is inherited from §6.2).
(b) Crisis-window benchmark race was tabulated but not re-run with multiple
ABM seeds because the §6.2 reeval set already covers crisis windows.
(c) The legacy Pkg A/B/D/E numbers refer to M0 (Phase 6 baseline). Re-running
the package on each of the six §6.3 variants is left as future work; the
§6.2 recalibrated dispersion (seed s.d. 0.023 pp across V_Full) is the closest
analogue available.

## 9. Wording to avoid

1. Do **not** write "ABM is robust across all regimes" — write "robust within
   the post-COVID normalization regime; not robust across regime
   transitions".
2. Do **not** write "ABM predicts the COVID crisis" — write "ABM tracks the
   direction of the COVID-19 unemployment shock (correlation 0.76) but
   under-predicts its magnitude by 2.07 pp on average".
3. Do **not** write "the three structural mechanisms each contribute" — write
   "search friction is the only standalone dimension that survives
   recalibrated ablation; liquidity and housing effects are largely absorbed
   by parameter recalibration in their absence".
4. Do **not** write "the calibrated parameters identify behavioural
   mechanisms" — write "predictions are method-invariant, but 10 of 14
   parameters are weakly identified; structural reads should be reported as
   bands".
5. Do **not** report the 97.6% heterogeneity share without qualifying — use
   94.2% (recalibrated) and note that the absolute gap is 0.288 pp, not
   2.116 pp.
6. Do **not** state "ABM beats all benchmarks" — state "ABM is rank 1 of 12
   in the post-COVID dynamic protocol with a 0.036 pp / 13% RMSE margin over
   no-change / ETS that falls within the seed dispersion of V_Full
   (±0.023 pp)".
7. Do **not** claim OOS data are "completely untouched" — write "evaluation
   used independent LHS calibration draws and independent reeval seed sets
   per variant; observed OOS unemployment was never used as a step input to
   any model".

## 10. Paper-ready §6.5 draft

> **§6.5 Robustness and sensitivity.** We synthesize the evidence from
> §§6.1–6.4 and the legacy Phase 7 / Package A–E robustness battery to assess
> which properties of the heterogeneous ABM are robust to alternative
> specifications and which are regime-bound. The model's post-COVID
> normalization tracking is robust along every dimension we examine: it is
> stable across five evaluation seeds (CV 3.08%; 0.221 ± 0.007 pp on the
> baseline calibration and 0.273 ± 0.023 pp under the §6.2 separate
> recalibration), invariant to the initialization window choice in
> {24, 36, 48} months (zero pp range), invariant to the tier-2 loss-weight
> sweep, and invariant across the five calibration methods of Package E
> (range 0.214–0.243 pp, CV 5.55%). It also degrades gracefully along the
> forecast horizon (M0 log-log RMSE slope −0.092, the shallowest among the
> eight models we tested) and is past its agent-count plateau at the default
> N = 100k (|ΔRMSE| < 0.015 pp for N ≥ 50k). The training-window battery of
> Package A confirms that the OOS-aligned RMSE band 0.245 ± 0.011 pp and the
> 10/10 win-rate against the Beveridge curve are not split-specific.
>
> Three caveats accompany this robustness profile and we report them
> explicitly. First, robustness is *within-regime*: the same model
> under-predicts the magnitude of the COVID-19 unemployment shock by
> 2.07 pp on average (RMSE 2.82 pp; correlation 0.76 with the observed
> path) and over-predicts pre-COVID unemployment by 0.77 pp on average.
> Both errors are washed out of a single full-window RMSE; §6.1 separates
> them. Second, the recalibrated controls of §6.2 and the recalibrated
> ablation of §6.3 show that the *magnitude* of the heterogeneity
> advantage shrinks by one order of magnitude (from 2.116 pp to 0.288 pp)
> once each control is evaluated at its own best fit, and that only
> search friction survives as a standalone ablation dimension with a
> large gap (+0.812 pp); liquidity-fragility and housing-mobility gaps
> drop to +0.105 pp and −0.036 pp respectively and sign-flip in the
> consumption-rule case. Third, parameter identification is weak: 10 of
> 14 behavioural parameters have top-5 CV ≥ 0.40 across the Package E
> calibration methods, while predictive output remains method-invariant
> (CV 5.55%). We therefore report all behavioural parameters as bands
> in §5 and confine structural interpretation to the within-method
> ordering rather than to the absolute level of individual coefficients.
>
> The stronger benchmark comparison of §6.4 reinforces this picture: the
> recalibrated ABM is rank 1 of 12 in the post-COVID dynamic protocol
> at 0.273 pp UR RMSE, ahead of no-change (0.309 pp) and Exponential
> Smoothing (0.309 pp) by 0.036 pp — a 13% relative margin that lies
> within the ±0.023 pp seed dispersion of V_Full. It is not the best
> performer in the other three regime windows (rank 3 in the COVID
> crisis, rank 7 pre-COVID, rank 2 full post-2018). We conclude that
> the contribution of the model is best framed as competitive
> regime-specific forecasting accompanied by the structural diagnostics
> that none of the benchmarks can supply, rather than as universal
> forecast dominance.

## 11. Risks of over-claiming if §6.5 is not adopted

If the original §6.5 wording is retained, three reviewer attack vectors remain
unaddressed: (i) the 0.21 pp headline is regime-conditioned; (ii) the
heterogeneity gap was constructed by holding controls off their own best fit;
(iii) the three-mechanism story does not survive recalibrated ablation. The
new §6.5 acknowledges (i)–(iii) preemptively and earns the right to keep the
post-COVID tracking and Search-Friction findings as headline claims.

## 12. Evidence appendix (file pointers)

* Revised §6.1 — `正式撰写/fix6.1/tables/table1_regime_summary.csv`
* Revised §6.2 — `正式撰写/fix6.2/tables/{table1_variant_summary, table6_old_vs_new_decomposition, table7_regime_x_variant}.csv`
* Revised §6.3 — `正式撰写/fix6.3/tables/{table2_post_covid_ablation, table5_old_vs_new_delta, table6_regime_x_ablation, table7_paper_ready}.csv`
* Revised §6.4 — `正式撰写/fix6.4/tables/{table1_main_postcovid_benchmark, table2_regime_specific}.csv`
* Legacy Phase 7 / Pkgs A–E — `正式撰写/6.5/robustness_metrics.json` and `正式撰写/6.5/tables/table6_paper_ready_compact.csv`
* This synthesis — `正式撰写/fix6.5/tables/table{1,2,3}*.csv`, `正式撰写/fix6.5/figures/fig1_revised_dashboard.png`
