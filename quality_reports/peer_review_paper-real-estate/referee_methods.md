# Methods Referee Report — `/review-paper --peer TOPFIN`

**Calibrated to:** Top Finance Journal — composite (TOPFIN)
**Disposition:** STRUCTURAL
**Paper type:** Structural (reduced-form DiD first stage feeding a closed-form structural inversion; the DiD is treated here as a load-bearing input, not a separable exercise)
**Critical peeve:** Structural estimation — parameter plausibility check required (compare to prior literature)
**Constructive peeve:** Values raw-data figures before any model (scatter plots, histograms, time series) to build intuition
**Date:** 2026-09-14

---

## Executive verdict

**Score:** 26 / 100
**Recommendation:** Reject
**Headline:** The structural layer does not identify anything the reduced form does not already deliver — under the paper's own pricing derivation the buyer-sensitivity parameter ρ cancels out of its own estimator, and the "structural" concealment cost ĉ₀ₘ is the reduced-form premium Δ̂ₘ truncated at β̂₁ₘ·ê*ₘ, not an estimate.

I want to be clear at the outset that I think the *project* is excellent. The listing↔ADEME match is a genuinely rare vantage point, §3 is exactly the kind of raw-data-first section I want to see, and the puzzle is real and worth a top journal. My recommendation is driven entirely by the identification algebra in §4.3–4.4, which I believe is broken in a way that cannot be repaired by robustness checks.

---

## Pre-scoring sanity checks (structural)

| Check | PASS/FAIL | Evidence |
|---|---|---|
| **Identification argument stated formally** | **FAIL** | §4.3 gives ρ̂ₘ = Δ̂ₘ/(β̂₁ₘ·ê*ₘ) and ĉ₀ₘ = ρ̂ₘ·β̂₁ₘ·ê*ₘ. Composing these gives ĉ₀ₘ ≡ Δ̂ₘ whenever ρ̂ₘ is interior — the paper concedes this ("equality exactly in the interior markets", §4.4.2). Worse, under the Appendix derivation of eq. (premium), the *observed* β̂₁ₘ = p̄^H − p̄^L already equals ρₘβ₁ₘ, so ρ cancels from its own estimator (Concern 1). |
| **Parameter plausibility vs. prior literature** | **FAIL** | β̂₁ = 1.7% (apartments) for A–D vs E/F/G is 3–6× below the EPC-capitalisation estimates the paper itself cites in ¶13 (Brounen–Kok 2011; Fuerst et al. 2016; Frondel et al. 2018). ĉ₀ = 3.4–4.5% of value (≈ €10–20k) is the asserted cost of omitting a €100–250 document. Neither is benchmarked against any prior estimate anywhere in the paper. |
| **Fit on moments not calibrated to** | **FAIL** | No untargeted moment is reported. §4.2.3 explicitly promises two cross-market specification tests (Δ̂ₘ ⊥ ρ̂ₘ with σ̂₀ₘ increasing in ρ̂ₘ; higher π̂ₘ ⇒ lower σ̂₀ₘ and more corner markets); neither appears in §4.4. The one genuine test that *is* run — σ₁* = 0 — is rejected (Appendix Table A1: σ̂₁ = 5.1% vs σ̂₀ = 5.5% for apartments). |
| **Counterfactual within support / driven by estimated parameters** | **FAIL** | By Lemma 1, c₀, π and σ₀ all cancel from R̄^PP. The implementation (§5.4) computes R̄ₘ as β̂₁ₘ × local price/m². The entire §5 counterfactual — €15.5–38.7bn, the 3–8× MaPrimeRénov' multiplier, the maps, the abstract's cost-share claim — is a function of one reduced-form DiD coefficient, a price level, and two assumed renovation costs. No estimated structural parameter enters. |

**Four FAILs. Composite is capped at 70 by protocol; I score well below that because the first FAIL is an identification cancellation, not a reporting gap.**

---

## Dimension scores (TOPFIN methods-referee weights, applied as given)

| # | Dimension | Weight | Score | Weighted |
|---|---|---|---|---|
| 1 | Model specification | 20% | 45 | 9.0 |
| 2 | Parameter identification | 35% | 15 | 5.25 |
| 3 | Estimation | 15% | 20 | 3.0 |
| 4 | Fit / validation | 10% | 25 | 2.5 |
| 5 | Counterfactuals | 20% | 30 | 6.0 |
| | **Composite** | 100% | | **25.75 ≈ 26** |

---

## Major concerns

### Concern 1: ρ is not identified — it cancels out of its own estimator

**Dimension:** 2 (Parameter identification) · **Severity:** MAJOR (fatal)

This is the concern the editor asked me to adjudicate, and the answer is worse than "ĉ₀ is an identity."

Take the Appendix derivation of eq. (premium) at face value. It sets δ₀ = β₀, δₙ = βₙ and weights the two buyer types:

- Disclosed low (d=1, θ=0): sensitive value β₀, insensitive value β₀ ⇒ p*_L = β₀.
- Non-disclosed: sensitive value β₀ + β₁e*, insensitive β₀ ⇒ p*_0 = β₀ + ρβ₁e*.

Apply the *identical* weighting to a disclosed high listing (d=1, θ=1): sensitive value β₀ + β₁, insensitive β₀, so p*_H = β₀ + **ρ**β₁. Therefore the observed price gap defined in §4.3.2,

> β₁,ₘ,ₜ = p̄^H_{m,t} − p̄^L_{m,t},

does **not** estimate the structural β₁ₘ. It estimates **ρₘβ₁ₘ**. The ρ-weighting is already inside the empirical β̂₁.

Substituting into the estimator:

ρ̂ₘ = Δ̂ₘ / (β̂₁ₘ · ê*ₘ) = (ρₘβ₁ₘe*ₘ) / (ρₘβ₁ₘ · e*ₘ) = **1**, identically, for every market and every true ρₘ.

ρ is not a parameter this design recovers; it is a quantity whose population value under the estimator is one by construction. What §4.4.2 calls "boundary saturation" — 40 of 42 partial-pooling apartment markets clipping at ρ̂ₘ = 1 — is not composition bias and not thin-cell attenuation. It is the estimator having no identifying content, with sampling noise in a small-denominator ratio throwing the realisations above and below unity. That also explains the segment pattern: houses have a three-fold larger (hence relatively less noisy) β̂₁, so more of their ratios land interior, and the 21 markets at ρ̂ₘ = 0 are simply markets where a noisy DiD returned Δ̂ₘ ≤ 0.

The knock-on is complete. ĉ₀ₘ = ρ̂ₘβ̂₁ₘê*ₘ collapses to β̂₁ₘê*ₘ = Δ̂ₘ in population. **ĉ₀ is Δ̂ₘ truncated at β̂₁ₘê*ₘ** — i.e. ĉ₀ₘ = min{Δ̂ₘ, β̂₁ₘê*ₘ}. The factor-of-two wedge between Δ̂ and ĉ₀ that §4.4.2 presents as "precisely the compositional mechanism the model is designed to capture" is arithmetically the part of Δ̂ₘ that was discarded by the clip. It is a truncation artefact, not a decomposition.

There is one escape route, and the paper should take it or rule it out explicitly: if β₁ₘ in the structural equation is meant to be the *sensitive-buyer valuation* gap rather than the *observed price* gap, then §4.3.2's empirical definition is the wrong object and the paper must say how the valuation gap is recovered from observed prices. But then ρ enters both numerator and denominator of that recovery too, and the identification problem reappears one layer down.

**What would change my mind:** A formal identification proposition — stated as a proposition, with a proof — that writes the observed objects (p̄^H, p̄^L, p̄^∅, ê*) as explicit functions of (ρ, β₁, e*, c₀) under the model's own pricing rule, and shows the Jacobian of that map has full rank at the estimated parameter. If the Jacobian is rank-deficient in ρ, as I believe, the honest resolution is to drop ρ from the paper, report the reduced-form premium, and re-motivate the model around something the data *can* pin down. Alternatively, exhibit a *second* source of variation that shifts ρₘ without shifting β₁ₘ (the reform shifts both, by the paper's own §4.3.1 argument), and show it is not the failed Bartik.

---

### Concern 2: the "composition bias" story contradicts the model's own pooling structure

**Dimension:** 1 (Model specification) / 2 · **Severity:** MAJOR

§4.3.4 and §4.4.2 argue that Δ̂ₘ is an upper bound on c₀ₘ "because the undisclosed category pools strategic hiders with genuinely uninformed sellers," with the uninformed "inflating the undisclosed category's average price."

But the entire mechanism of the paper is that buyers **cannot distinguish** the two groups. In the model every d=0 listing faces the same posterior e*(σ₀*) and therefore the same price p*_0 = β₀ + ρβ₁e*. There is no within-pool price dispersion to average over. The hedonic indices condition on X, so observable heterogeneity is already purged; true θ is unobserved to buyers and so cannot enter price. Under the model as written, Δ̂ₘ **is** ρβ₁e*ₘ, and in partial pooling it equals c₀ₘ exactly, with no wedge.

You cannot simultaneously claim (i) pooling is the mechanism that defeats unraveling and (ii) the pooled premium overstates the marginal hider's premium. If Δ̂ₘ systematically exceeds β̂₁ₘê*ₘ (which the paper reports it does, by ~7× for apartments), the model-consistent reading is that the model's premium equation is rejected by the data — not that Δ̂ₘ needs a compositional haircut the model does not generate.

**What would change my mind:** Either (a) an extension in which non-disclosers are priced differentially — e.g. buyers observe a noisy signal of K, or listing agents sort — with the premium re-derived under that extension; or (b) acceptance that Δ̂ₘ is the model's Δ, and a re-framing of the ρ̂ₘ > 1 finding as a rejected overidentifying restriction (Concern 3) rather than as a bias to be clipped away.

---

### Concern 3: ρ̂ₘ > 1 is a failed specification test, not a nuisance to be clipped

**Dimension:** 2 / 4 · **Severity:** MAJOR

The editor asked specifically whether the unconstrained ρ̂ₘ > 1 should be read as composition bias / thin-cell attenuation or as a specification test the model fails. It is the latter, and the magnitude is not marginal.

The model's premium is ρβ₁e*, and its **maximum across all three regimes** is ρβ₁θ̄ ≤ β₁θ̄ (Cost-Deterred Hiding, Table 3). For apartments, using the paper's own Panel A and Panel C means:

- β̂₁ · θ̄ = 0.017 × 0.625 = **1.06%** — the largest non-disclosure premium the model can produce.
- Observed Δ̂ = **6.9%**.

The headline fact of the paper sits **6.5× outside the model's entire feasible range**, in the segment §3 describes as the one "where identification is sharpest." For houses the violation is milder but still present at the mean (β̂₁θ̄ = 3.09% vs Δ̂ = 3.4%).

Reporting the unconstrained cross-market *mean* ratio of "approximately 7.7" compounds the problem: this is the mean of a ratio whose denominator has substantial mass near zero (25 of 68 apartment markets are dropped for β̂₁ₘ ≤ 0, per the Table 4 note). Such a mean is not a meaningful summary — it is dominated by the markets just above the truncation point, and it is not stable in sample. The two explanations offered (composition bias, thin-cell attenuation) are both substantive stories for what is, first, a statistical artefact and, second, a rejected restriction.

**What would change my mind:** (i) Report the *median* and the full distribution of the unconstrained ratio, with a market-level Fieller interval on each (delta-method is not adequate for a ratio with a denominator whose sign is uncertain). (ii) Report the fraction of markets for which the model's feasibility bound Δ̂ₘ ≤ β̂₁ₘθ̄ₘ can be rejected at conventional levels. If that fraction is large — and I expect it is close to one for apartments — state in the abstract and §4 that the model is rejected as a quantitative description of the apartment segment, and restrict the structural claims to the segment where it is not.

---

### Concern 4: the first stage selects on the sign of its own denominator

**Dimension:** 3 (Estimation) · **Severity:** MAJOR

§4.3.2: "markets with β̂₁ₘ ≤ 0 are excluded from structural inversion," and the Table 4 note puts this at 25 of 68 apartment markets (37%) and 6 house markets. The paper then forms ρ̂ₘ = Δ̂ₘ/(β̂₁ₘê*ₘ) on the survivors.

Conditioning a sample on β̂₁ₘ > 0 when β₁ₘ is small (mean 1.7%) and noisy (cross-market SD 3.5pp — twice the mean) and then dividing by β̂₁ₘ is the textbook recipe for an explosive, non-robust ratio. It also makes the estimation sample endogenous to the outcome: markets are retained precisely when the first-stage noise happened to land positive.

Separately, that 37% of apartment markets have a *negative* estimated energy-efficiency premium is itself a sanity-check failure worth stating plainly in the text. The model requires β₁ > 0 everywhere.

**What would change my mind:** (i) Do not drop; report the full distribution of β̂₁ₘ with its standard errors, and show how many markets have β̂₁ₘ statistically distinguishable from zero. (ii) Re-estimate with a bounded or regularised estimator that does not require inverting a near-zero denominator. (iii) Show the structural conclusions are unchanged when the retention rule is randomised or when markets are weighted by 1/Var(β̂₁ₘ) rather than sign-selected.

---

### Concern 5: no inference anywhere on any structural object

**Dimension:** 3 · **Severity:** MAJOR

There is not a single standard error, confidence interval, or bootstrap in the paper for ρ̂ₘ, ĉ₀ₘ, ê*ₘ, R̄ₘ, S*ₘ, or any aggregate in §5. The "Std" columns in Table 4 and Table A1 are cross-market dispersion, and the surrounding text occasionally reads them as precision.

Three compounding reasons this is not survivable at a top finance journal:

1. **Generated regressors.** β̂₁ₘ and Δ̂ₘ come from hedonic price indices estimated in a prior paper. Their sampling error is nowhere propagated.
2. **Two-step estimation.** ĉ₀ₘ depends on ρ̂ₘ, which depends on β̂₁ₘ and Δ̂ₘ. First-stage error enters the second stage multiplicatively.
3. **Ratio with a near-zero denominator** (Concern 4) — precisely the case where asymptotic normality fails and Fieller is required.

There is also no statement anywhere of the level at which anything is clustered, and no discussion of serial correlation in the monthly index panel underlying the period-mean DiD.

**What would change my mind:** A market-level block bootstrap that resamples from the underlying listing data through *both* steps — index construction, DiD, inversion — reporting CIs on ρ̂ₘ, ĉ₀ₘ, and the §5 aggregates; plus Fieller intervals on ρ̂ₘ specifically. Table 4 and every number in §5 and the Conclusion need uncertainty attached.

---

### Concern 6: σ₁* = 0 is load-bearing and the paper's own appendix rejects it

**Dimension:** 1 / 4 · **Severity:** MAJOR

Corollary (high-quality sellers always disclose) states σ₁* = 0 **in any equilibrium**. It is not an ordering claim; it is a knife-edge prediction. It is also the restriction that licenses eq. (belief, simplified), which defines ê*ₘ, which produces both ρ̂ₘ and ĉ₀ₘ. The entire identification chain rests on it.

Appendix Table A1, with quality read from the registry: σ̂₁ = 5.1% against σ̂₀ = 5.5% (apartments), 2.1% against 2.2% (houses). Informed high-quality sellers withhold at *essentially the same rate* as informed low-quality sellers. With no standard errors, these gaps (0.4pp and 0.1pp) are indistinguishable from zero difference. The prediction is not "narrowly satisfied"; it is rejected, and the sorting mechanism the model relies on is absent from the data.

The appendix's framing compounds this. Under the C–D cut the ordering *reverses* in both segments, and the paper reads the fact that the institutionally-motivated cut is also the cut under which the restriction survives as "support for the baseline cut." That is selecting a specification on whether it confirms the model. The institutional argument for the D–E cut is good and stands on its own; do not also claim credit for the confirmation.

I also cannot tell from Table A1's note whether the "σ₁ from registry" rows recompute ê*ₘ using the *general* belief function (which has the πθ̄σ₁ term in both numerator and denominator) or merely reassign θ while still using the σ₁ = 0 simplification. If the latter, the robustness row does not do what it claims.

**What would change my mind:** (i) State explicitly whether eq. (belief, general) is used in the σ₁-from-registry rows, and if not, redo them with it. (ii) Report a test of H₀: σ₁ₘ = 0 with standard errors, market by market and pooled. (iii) If σ₁ > 0 — which the numbers say — re-derive the identification under the general belief function and report how much of the ĉ₀ estimate survives. (iv) Demote the Corollary from "in any equilibrium" to a testable prediction, and report in the main text that it fails.

---

### Concern 7: the counterfactual contains no structural parameter, and its headline dispersion is a boundary artefact

**Dimension:** 5 (Counterfactuals, 20% at TOPFIN) · **Severity:** MAJOR

Lemma 1 shows c₀ and π cancel from R̄^PP. §5.4 implements R̄ₘ as "β₁ measures the quality premium in log-point terms against a local price-per-m² base," so R̄ₘ = β̂₁ₘ × p̄ₘ. S*ₘ = max{R̂ − R̄ₘ, 0} with R̂ ∈ {250, 500} assumed from programme documentation. Neither ĉ₀ₘ, π̂ₘ, σ̂₀ₘ, nor ê*ₘ appears. Whether ρ̂ₘ appears is unclear — §5.3 says R̄^PP "depends on ρ and X alone" and the Prop 3 proof derives ∂R̄/∂ρ > 0, but §5.4's implementation describes only β₁ and the price level.

So the paper's answer to the TOPFIN question "why does this need the structural model rather than the reduced form?" is, on its own terms: it does not. The model's empirical contribution to the counterfactual is a *proof that the estimated structural parameters are irrelevant to it*. Lemma 1 is presented as "the central technical result of this section"; read as a referee, it is the result that vacates the section's need for the model.

Two further problems inside §5:

**(a) The abstract's headline dispersion is a clipping artefact.** The abstract promises "required cost-shares ranging from zero to the full renovation cost." S*ₘ/R̂ = 1 requires R̄ₘ = 0, which requires ρ̂ₘ = 0 or β̂₁ₘ ≈ 0 — i.e. exactly the 21 house markets where the noisy DiD returned Δ̂ₘ ≤ 0 and ρ̂ₘ was clipped to zero. The upper end of the distribution the abstract sells is first-stage estimation noise at a boundary, relabelled as a market where the renovation incentive is absent.

**(b) The magnitudes do not reconcile with the reported primitives.** R̄ₘ = β̂₁ₘ × p̄ₘ with β̂₁ = 1.7% and a reported apartment mean R̄ = €165/m² (median €151) implies a mean local price of ~€8,900/m² — implausible as an average over 40 French *zones d'emploi*. For houses (0.051 × p̄ = 128 ⇒ p̄ ≈ €2,500/m²) the arithmetic is fine. The apartment figure appears ~2.5–3× too large given the reported β̂₁.

**What would change my mind:** (i) A counterfactual that a reduced-form paper could not produce — e.g. the equilibrium response of σ₀*ₘ and hence of the non-disclosure premium to a subsidy or to an enforcement change, solved through the fixed point, rather than a threshold comparison at fixed beliefs. Definition 2 explicitly holds equilibrium beliefs fixed; that is where the model's value would show up if it were used. (ii) A worked table showing R̄ₘ for three named markets from their reported β̂₁ₘ, p̄ₘ and (if used) ρ̂ₘ, so the mapping can be checked. (iii) Re-report §5 excluding the ρ̂ₘ = 0 markets, and state in the abstract what the cost-share range is on the markets where the first stage is actually informative.

---

### Concern 8: internal numeric contradictions across sections — the estimation sample and two headline parameters are not well-defined

**Dimension:** 3 · **Severity:** MAJOR

These are individually small and jointly disqualifying, because a structural paper whose every number is a cross-market mean must have an unambiguous set of markets and an unambiguous value for each parameter.

**Market counts.** Six mutually irreconcilable statements:

| Location | Apartments | Houses |
|---|---|---|
| §4.3.2 (volume filter) | 40 | 100 |
| §4.3.4 (estimation sample) | 45 | 97 |
| Table 4 Panel A header (N) | 49 | 104 |
| Table 4 note | 43 (after excluding 25) | 107 (after excluding 6) |
| §4.4.2 regime counts | 42 PP + 3 = 45 | 76 PP + 21 = 97 |
| §5.4 | 40 estimable; 2 CDH | 100; 25 CDH |

43 + 25 = 68 ≠ 49; 107 + 6 = 113 ≠ 104 ≠ 110 (the base panel in §3.2.1). And §4.4.2's "3 full-unraveling" apartment markets versus §5.4's "2 Cost-Deterred Hiding apartment markets" suggests either a count error or two different labels for the same regime — which brings me to the next point.

**Regime classification rule is never stated.** Proposition 2's conditions are stated in terms of c₀ versus Δ(θ̄) and Δ(e(1)), but ĉ₀ is itself obtained by *assuming* partial pooling and inverting the PP indifference condition. The operational classification rule must therefore be something else (presumably σ̂₀ₘ ∈ (0,1) vs = 0, and ρ̂ₘ = 0 for "full unravelling"). It is nowhere written down. Note also that no market is classified as Complete Adverse Selection despite that regime carrying its own row in Table 3, and that "full unravelling" and "Cost-Deterred Hiding" are used interchangeably without being equated.

**ĉ₀ for houses has two values.** §4.3.4: "cross-market means are ĉ₀^inv = 0.018 log points and Δ̂ₘ = 0.034… The tighter bound ĉ₀^inv = 0.018 is the preferred estimate **and is used in the policy counterfactuals** of Section 5." Table 4 Panel B, ¶9 of the introduction, and the Conclusion all report 4.45–4.5%. These differ by 2.5×, and the text says the smaller one feeds §5.

**σ̂₀ₘ has two values.** §3.2.2: "the corresponding unweighted means across markets, reported as σ̂₀ₘ in the results, are 7.7% and 3.7%." Table 4 Panel C and Table A1 baseline: 14.0% and 5.7%. This is not a rounding difference — it is a factor of ~2 on a moment that enters ê*ₘ and therefore ĉ₀ₘ directly.

**An arithmetic impossibility in Table 4.** The estimator is ĉ₀ₘ = ρ̂ₘ·β̂₁ₘ·ê*ₘ with ρ̂ₘ ∈ [0,1] and ê*ₘ ∈ [0,1]. Hence ĉ₀ₘ ≤ β̂₁ₘ in **every** market, and since exp is monotone the same inequality survives the note's e^δ − 1 transformation and the cross-market averaging. So mean(ĉ₀ₘ) ≤ mean(β̂₁ₘ). Table 4 reports **3.42% > 1.7%** for apartments. Either Panels A and B use different β̂₁ (in which case the table must say so and report both), or one of these numbers is wrong. Houses satisfy the bound only barely (4.45% vs 5.1%).

**Aggregate totals contradict.** §5.4: €6.4bn + €9.1bn = €15.5bn at the light benchmark. Conclusion: "aggregate programme costs reach 14.6 billion euros at the light renovation benchmark."

**A garbled sentence in the Conclusion.** "5.7% of house sellers do.7% of house sellers do so."

**What would change my mind:** A single reconciliation table, in the paper, that defines the estimation sample once — base markets, each filter, markets dropped by each filter, final N by property type — and is referenced by every section; plus a stated regime-classification rule; plus correction of the ĉ₀ (houses), σ̂₀, ĉ₀ ≤ β̂₁, and aggregate-cost contradictions with a note on which value is used where. Given the project's own single-source-of-exhibits discipline, I would expect these to be generated, not typed.

---

### Concern 9: K = 0 measures registry coverage, not seller ignorance — and the paper's own data say so

**Dimension:** 1 / 3 · **Severity:** MAJOR

§3.2.2 is admirably candid that the ADEME registry contains only certificates issued from July 2021, and reports the consequence: 32.2% of apartment listings and **51.2% of house listings** display an EPC score with no registry record, falling from 62.5% (73.1%) in 2021Q3 to 18.4% (43.7%) in 2024Q4. The paper correctly infers that many of these hold valid pre-reform certificates.

Three consequences the paper does not follow through:

1. **π̂ₘ is a registry-accumulation artefact, not a structural primitive.** π̂ = 50.7% (apartments) is the K=1 match rate, which *excludes* the disclosed-unmatched group. If those sellers are informed — which is the paper's own explanation for their existence — the true informed share is closer to 83% (apartments) and 92% (houses). A parameter that trends mechanically from 7.4% to ~50% over the sample window, then gets pooled into one number for 2022–2024, is not a fixed primitive.

2. **The paper's central empirical claim is exposed.** "Non-disclosure is overwhelmingly involuntary — 16.7% genuinely uninformed vs 3.5% strategic hiders" is the resolution of the whole puzzle. But if pre-2021 valid certificates are common enough to explain a third of apartment *disclosers*, they are equally common among *non-disclosers*, and an unknown share of the "genuinely uninformed" 16.7% are in fact informed hiders. The paper notes this biases σ̂₀ downward and argues it "reinforces the upper bound" on ĉ₀ — but the upper-bound framing is a second-order consolation next to the fact that the headline decomposition itself is coverage-dependent.

3. **The no-falsification assumption is doing enormous classification work, untested.** Over half of all house listings are assigned to "truthful discloser" on the strength of an assumption, with no registry evidence. This is testable with the data in hand and the test is never reported: among listings that *do* have a registry match and display a score, what fraction of displayed grades disagree with the registry grade? That is the cheapest and most informative number the paper could produce, and it is absent.

**What would change my mind:** (i) Re-estimate everything on 2024 alone, where the disclosed-unmatched share is down to 18.4% (apartments), and report whether the four-group decomposition, π̂ₘ, σ̂₀ₘ, and ĉ₀ₘ are stable. If the "genuinely uninformed" share collapses in 2024, the mechanism story needs rewriting. (ii) Report π̂ₘ and the four-group shares by year. (iii) Report the displayed-vs-registry grade mismatch rate among matched disclosers, as a direct test of no-falsification. (iv) Provide a bound on the true uninformed share using the observed decay rate of the disclosed-unmatched group.

---

### Concern 10: K ⊥ θ is assumed on a narrative and is first-order for ĉ₀

**Dimension:** 1 · **Severity:** MAJOR

Assumption (Independence) sets K ⊥ θ, justified by forced sales (succession, liquidation, divorce) constituting "a substantial share of the resale market" — with no number, no citation, and no test. The assumption is what allows θ̄ₘ, measured as E[θ | K=1], to be read as the unconditional E[θ], and θ̄ₘ enters ê*ₘ directly, which enters ĉ₀ₘ directly.

The economics push hard the other way. An owner who has just renovated commissions a DPE to document it; an owner who suspects an F or G rating has every reason to delay commissioning one. Both make Pr(K=1 | θ=1) > Pr(K=1 | θ=0), which inflates θ̄ₘ, inflates ê*ₘ, and inflates ĉ₀ₘ.

Appendix Table A1 shows how much this margin matters: moving the quality cut from D–E to C–D roughly halves θ̄ₘ (62.5% → 26.5%) and moves ĉ₀ₘ from 3.42% to 1.62%. The paper says so itself — "the threshold matters a great deal… this is the paper's most consequential specification choice." A parameter with that sensitivity cannot rest on an untested independence assumption.

**What would change my mind:** Benchmark the grade distribution of matched (K=1) listings against ADEME's published distribution for the national dwelling stock, by *département* where possible. If matched listings are over-represented in A–D relative to the stock, the direction and rough size of the violation are immediately visible and can be used to bound ĉ₀ₘ. Failing that, exploit within-market variation in audit-supply conditions (assessor density, appointment waiting times) as a shifter of K that is plausibly orthogonal to θ, and compare θ̄ₘ across high- and low-supply markets.

---

### Concern 11: the pricing layer is internally inconsistent, and the identification equation is asserted rather than derived

**Dimension:** 1 · **Severity:** MAJOR

§4.2.2 sets up a genuine pricing problem: max over (d, p^list) of φ(p^list)·Γ(p^list) − C(θ,d), with φ(p) = γ₀ + γ₁p and Γ a mixture of two logits. The first Appendix proof derives the FOC γ₁/(γ₀ + γ₁p*) = 1 − G(v₁ − p*) — note this is written for a single buyer type, with no ρ — and shows ∂p*/∂v₁ > 0, with the displayed expression implying ∂p*/∂v₁ **strictly less than 1**.

The proof of eq. (premium) then asserts something different and incompatible: "the equilibrium price of a listing equals its expected buyer valuation." If p* = v, then Γ(p*) = G(0) = ½ and the entire pricing/search structure is vacuous — φ, γ₀, γ₁ and the transaction records used to estimate them do no work.

This matters because Δ = ρβ₁e* — the single equation carrying all of the paper's identification — comes from the asserted version, not the derived one. Under the derived version the price gap is a pass-through fraction κ < 1 of the valuation gap, and the identification equation should read Δ = κ·ρβ₁e*.

Two smaller items in the same family:

- **Proposition (Disclosure Incentives) omits c₀.** As stated, an informed θ=0 seller "strictly prefers non-disclosure whenever e(σ₀*) > 0." That is false for c₀ > 0: the correct condition is ρβ₁e > c₀. The Corollary is unaffected (costs only reinforce it), but the proposition as written contradicts Proposition (Equilibrium), where Cost-Deterred Hiding has e = θ̄ > 0 and σ₀* = 0.
- **Price gaps and revenue gaps are used interchangeably.** Table 3 and eq. (premium) are in price-gap units (ρβ₁e); the policy section's thresholds are in revenue units Π = φ·Γ. Lemma 1's cancellation is executed in Π-units and then implemented empirically in price-gap units (β̂₁ × price/m²). The equivalence is never established.

**What would change my mind:** Derive p*(d, θ; e) from the stated FOC, characterise the pass-through κ = ∂p*/∂v, and either (a) show κ cancels from Δ/(β₁e*) — it partly does, which is worth showing explicitly — or (b) carry κ through the identification equations and report its estimated value from the transaction data you already use for γ₀, γ₁. Restate the Proposition with c₀. Add one lemma establishing that the Π-unit indifference condition reduces to the price-gap condition used empirically.

---

## Minor suggestions

1. **Table 4's "Std" columns** should be relabelled to make clear they are cross-market standard deviations, not standard errors, and the note should say so.
2. **Panel A's units footnote** says Panel A means and the ĉ₀ row are e^δ − 1 in percent, while share parameters are in percentage points. Two different units in adjacent rows of one panel invites exactly the kind of cross-panel comparison error flagged in Concern 8. Consider separate tables.
3. **§4.2.3's two announced cross-market tests** (Δ̂ₘ ⊥ ρ̂ₘ with σ̂₀ₘ rising in ρ̂ₘ; π̂ₘ negatively related to σ̂₀ₘ) should either be run and reported in §4.4 or the promise removed. Note that the first is untestable with this estimator, since ρ̂ₘ is constructed from Δ̂ₘ — that fact is itself worth stating.
4. **The volume filter** ("at least 20 average monthly transactions per disclosure group per market") is applied to listings, not transactions — the text says transactions. Worth correcting, and worth a sensitivity check at 10 and 40.
5. **Figure (model timing) and Figure (visual representation of model dynamics)** are referenced but the second is relegated to the appendix with no discussion. Either integrate or drop.
6. **The negotiation-margin footnote** cites Merlo–Ortalo-Magné for England and Friggit for France, but the claim that "the majority of properties transact at or very near list price" carries no number from the paper's own transaction data, which it has. One sentence with the estimated γ̂₁ and the mean listing-to-sale ratio would settle it.
7. **TOPFIN table convention:** coefficients to three decimals, standard errors in parentheses, clustering level in a table note. Table 4 currently reports one decimal in percent with no SEs and no clustering statement.

---

## Positive observations

These are genuine, and I want them on the record because a resubmission should keep them intact.

1. **§3 is a model of what a data section should be, and it satisfies my strongest methodological preference directly.** Four stylized facts, each with a raw-data exhibit — price-level time series by disclosure category, the event-study premium, the non-disclosure share series, the three-group decomposition, the départemental maps — all *before* any model appears. §3.4 ("What the facts demand of the theory") then states what the theory must accommodate before the theory is written. I read the whole model section already knowing what it had to explain. Very few structural papers do this, and it is why I could diagnose Concern 3 at all: the facts were laid out cleanly enough that the model's feasibility bound could be checked against them.

2. **The listing↔ADEME match is a real and rare asset.** Direct observation of K at listing time is exactly the object disclosure theory has always had to treat as latent. Whatever happens to the structural layer, this measurement contribution stands.

3. **§3.2.2's discussion of the registry-coverage gap** is unusually honest. The paper volunteers the 32.2%/51.2% disclosed-unmatched shares, traces their decay, signs the resulting bias in σ̂₀, and explains why the structural sample starts in 2022. My Concern 9 is about following that logic further, not about the paper having hidden anything.

4. **The Remark distinguishing S\* from a Ramsey optimum** is exactly right, and rarer than it should be. Writing down the welfare problem you are *not* solving, with λ ≥ 1 and the externality term, and then labelling S\* a positive object, is the correct standard.

5. **Appendix A's σ₁ table reports numbers that go against the model.** The framing needs work (Concern 6), but the numbers are there and the reader can draw the right conclusion from them. That is more than many structural appendices offer.

6. **Proposition (Equilibrium Existence and Uniqueness) is properly proved.** The monotone-Φ argument is clean, the three cases exhaust the parameter space, and uniqueness follows without refinements. The theory, as theory, is sound; my objections are to how it meets the data.

---

## Note to the editor

If the author can rebut Concern 1 — specifically, if there is a reading under which the empirical β̂₁ₘ is *not* already ρ-weighted — then Concerns 2, 3 and 7(a) change character substantially and this becomes a major-revision paper with a very good data asset. I would want to see that rebuttal as explicit algebra mapping the three observed price indices to the model's primitives, not as prose. If Concern 1 stands, the paper's structural claims cannot be repaired by revision, and the right advice is to publish the reduced-form result and the measurement contribution on their own, which are strong enough to carry a paper.
