# Editorial Decision: *When Silence Pays: Mandatory Disclosure and Strategic Concealment in Housing Markets*

**Calibrated to:** Top Finance Journal — composite (TOPFIN)
**Manuscript:** `paper-real-estate/main.tex` (+ `sections/01`–`04`, `sections/A-robustness.tex`)
**Date:** 2026-09-14
**Decision:** **REJECT** — with an explicit invitation to resubmit a reduced-form + measurement paper (see "Editor's note to the author")

---

## One-paragraph editor's assessment

This paper has a genuinely rare data asset and a puzzle worth a top journal, and both referees say so independently and at length. It does not have a working structural layer. I verified the methods referee's two most consequential claims directly against the manuscript rather than accepting them, and both hold: under the paper's own Appendix derivation of the premium equation, the empirically-defined β̂₁ₘ = p̄^H − p̄^L already equals ρₘβ₁ₘ, so ρ cancels out of ρ̂ₘ = Δ̂ₘ/(β̂₁ₘê*ₘ) and the estimator returns 1 by construction; and §5.4's counterfactual is implemented as β̂₁ₘ × local price/m², containing no estimated structural parameter. I then found a second, logically independent failure that survives any rebuttal of the first: with the paper's own Table 4 values (β̂₁ = 1.7%, θ̄ = 62.5%), the largest non-disclosure premium the model can generate *in any of its three regimes* is ρβ₁θ̄ ≤ 1.06%, against an observed Δ̂ = 6.9% — the headline fact of the paper sits 6.5× outside the model's entire feasible range, in the segment the paper calls its sharpest. Two fatal concerns is a reject under my decision rule, and I am not overriding it, because these are not a grumpy referee's taste: they are arithmetic on the manuscript's own equations and its own table, reached by two separately-fenced referees of different dispositions and then re-derived independently by me. The reduced-form premium, the ADEME match, and §3 are strong enough to carry a different paper, and I say so below.

---

## Referee summary

- **Referee A (domain, SKEPTIC):** 68/100, Major Revision. The headline premium is a DiD *change* in a gap between two groups never shown comparable, one of which is hit by a rental ban from the same statute on the same date; the structural layer reports a boundary-saturated parameter and a rejected corollary as results.
- **Referee B (methods, STRUCTURAL):** 26/100, Reject. The structural layer identifies nothing the reduced form does not already deliver; ρ cancels from its own estimator and ĉ₀ is Δ̂ truncated. Four of four structural sanity checks FAIL. Explicitly states the project is excellent and the reject is driven entirely by the §4.3–4.4 algebra.

The 42-point spread is not a disagreement about quality. It is a disagreement about *scope*: Referee A graded the paper's causal claim and found it wanting but repairable; Referee B graded the identification algebra and found it broken. Both diagnoses are correct, and they compound rather than offset.

---

## Editor's verification of the two load-bearing claims

Per the post-judge hallucination-gate discipline, I did not let confident-sounding referee algebra into this decision unchecked.

### Methods Concern 1 — **CONFIRMED, and stronger than stated**

The Appendix proof of eq. (premium) (`main.tex:559`) states the pricing rule explicitly:

> "Under the benchmark αₖ=βₖ, the equilibrium price of a listing equals its expected buyer valuation."

and applies it to exactly two listing types — disclosed-low (p*_L = β₀) and non-disclosed (p*_0 = β₀ + ρβ₁e*). It never applies it to the third. Applying the **identical rule** to a disclosed-high listing, using the model's own EPC-insensitive valuation v₀(X) = δ₀ + Σδₙ Xₙ (`04-structural-draft.tex:119`), which is independent of θ and d by construction, gives sensitive value β₀+β₁, insensitive value β₀, hence p*_H = β₀ + **ρ**β₁. The empirical definition at `04-structural-draft.tex:385` is β₁,ₘ,ₜ = p̄^H − p̄^L. Therefore the observed object is ρₘβ₁ₘ, and

ρ̂ₘ = Δ̂ₘ/(β̂₁ₘ·ê*ₘ) = (ρβ₁e*)/(ρβ₁·ê*) = **1**.

The referee did not check whether the DiD-differencing saves it. It does not, and this is worth stating because it closes the author's most natural line of defense (`04-structural-draft.tex:367`: "the hat quantities are DiD estimates"). In change form, β̂₁ = β₁(ρ_post − ρ_pre) and Δ̂ = β₁(ρ_post e*_post − ρ_pre e*_pre), so ρ̂ = (ρ_post e*_post − ρ_pre e*_pre)/((ρ_post−ρ_pre)ê*), which equals 1 when e* is stable and is otherwise a ratio of belief-weighted objects that is not ρ in any regime. Worse, this delivers a *deterministic* explanation for ρ̂ ≫ 1 that the paper does not consider: when ρ_post ≈ ρ_pre the denominator collapses while the numerator does not, so the ratio explodes with no noise required at all. "Composition bias and thin-cell attenuation" (`:409`) are substantive stories offered for an algebraic artefact.

**Independent corroboration from the paper's own Table 4.** Panel B reports ρ̂ₘ mean 90.9%, SD 28.6pp, N=45 (apartments). For a variable confined to [0,1], a Bernoulli with p=0.909 has SD √(0.909×0.091) = **28.7pp**. The match to the reported 28.6 is essentially exact. ρ̂ₘ takes only the values 0 and 1 in the apartment sample — there are no interior estimates. The abstract, introduction, results and conclusion all narrate ρ̂ = 90.9% as "nearly all buyers in the average market price energy performance" (`04-structural-draft.tex:496`). Arithmetically, that sentence reports **the share of apartment markets that hit the upper clip**. It is not a measurement of buyer sensitivity. (Houses: mean 0.681, SD 42.0 vs Bernoulli 46.6 — some interior mass, consistent with the paper's own claim of a handful of point-identified house markets.)

Domain Referee Concern 5 reached the same suspicion from an entirely different route — reading the regime table and asking whether the disclosed-high/disclosed-low gap should carry the same ρ weighting as the premium does. Two differently-fenced referees converging on the same algebraic defect, plus my own re-derivation, is as strong as this kind of signal gets.

**The one escape route, and why it does not save the paper today.** The "expected buyer valuation" shortcut is itself inconsistent with the paper's *actual* pricing model — the Lemma A.1 FOC (`main.tex:426`) yields ∂p*/∂v₁ ∈ (0,1), i.e. p* ≠ E[v]. Under the FOC, p̄^H − p̄^L is not exactly ρβ₁ and the cancellation is not exact. That is precisely methods Concern 11, and it is a real escape hatch — but it is an escape from an unidentified estimator into a *underived* one, since the author would then need to show what the three observed indices equal under the FOC and that the residual ρ-dependence is a usable identifying wedge rather than a second-order nonlinearity. With the Bartik first stage failed (F between 1.0 and 1.6, `:371`) there is no second source of variation shifting ρₘ independently of β₁ₘ. The route exists; nobody has walked it.

### Methods Concern 7 — **CONFIRMED**

`main.tex:237`: "Because β₁ measures the quality premium in log-point terms against a local price-per-m² base, the nominal threshold R̄ₘ scales with the local price level." R̄ₘ = β̂₁ₘ × p̄ₘ; S*ₘ = max{R̂ − R̄ₘ, 0} with R̂ ∈ {250, 500} taken from programme documentation (`:250`). Neither ĉ₀ₘ, π̂ₘ, σ̂₀ₘ nor ê*ₘ appears; ρ̂ₘ is numerically inert where it is clipped to 1, which is every apartment market. The €15.5bn/€38.7bn aggregates, the 3–8× MaPrimeRénov' multiplier, the maps and the abstract's cost-share range are a function of one reduced-form DiD coefficient, a price level, and two assumed costs. Confirmed as stated.

I part company with the referee on the *interpretation*, and say so under TASTE below: Lemma 1 is a selection theorem, and proving which object governs the renovation margin is a contribution. But Concern 7(a) — that the abstract's "zero to the full renovation cost" range is generated by markets where ρ̂ₘ was clipped to **zero** because a noisy DiD returned Δ̂ₘ ≤ 0 — is confirmed and is not defensible.

### Editor-added FATAL — the model cannot generate its own headline fact

This is not a new lens; it is methods Concern 3 with the inputs verified, and I am promoting it because it is **logically independent of Concern 1** and therefore survives any successful rebuttal of it.

From Table 3 (`04-structural-draft.tex:251–253`), the maximum non-disclosure premium across all three regimes is ρβ₁θ̄, attained in Cost-Deterred Hiding, and ρ ≤ 1 by assumption. From Table 4: β̂₁ = 1.7% (Panel A), θ̄ = 62.5% (Panel C, `:476`). So the model's ceiling is **1.06%**. Observed Δ̂ = **6.9%** (Panel A). Houses: ceiling 0.051 × 0.605 = 3.09% against Δ̂ = 3.4% — violated too, if narrowly.

Note that this holds *whichever* way Concern 1 resolves. If the referee is right that β̂₁ observed = ρβ₁, then the ceiling is β̂₁θ̄ = 1.06% exactly. If the author is right that β̂₁ observed = β₁, the ceiling is ρβ₁θ̄ ≤ 1.06%. The bound is the same either way. **The paper's central empirical fact is outside the range its model can produce, in the segment where it says identification is sharpest, and the manuscript nowhere reports this.** A structural paper whose only overidentifying restriction is rejected by an order of magnitude, and which responds by clipping the parameter to its bound and narrating the clip as an estimate, has not been validated.

The same arithmetic surfaces as a visible contradiction inside Table 4, which both the methods referee and I flag: the table's own note states ĉ₀ₘ = ρₘ·β̂₁ₘ·ê*ₘ with ρ̂ₘ, ê*ₘ ∈ [0,1], which forces ĉ₀ₘ ≤ β̂₁ₘ market by market and hence in the cross-market mean. The table reports 3.4% > 1.7%. Either Panels A and B use different β̂₁ and the table must say so, or a reported number is wrong.

---

## Concern classification

### FATAL

| # | Concern | From | Why fatal |
|---|---|---|---|
| **F1** | ρₘ is not identified — it cancels from its own estimator, and ρ̂ₘ is a 0/1 clip indicator in the apartment sample | Methods C1; independently Domain C5; **verified by editor** against `main.tex:559` and `04-structural-draft.tex:385`, corroborated by the Bernoulli-SD check on Table 4 | ρ̂ is one of two headline structural magnitudes, is narrated as a finding in abstract/intro/results/conclusion, and enters ĉ₀ multiplicatively. The paper's stated contribution — measuring the buyer heterogeneity the literature has had to assume — does not exist. Repairing it requires either a new source of variation (the only candidate failed) or withdrawing the parameter and rewriting the paper's claim. |
| **F2** | The observed Δ̂ = 6.9% is 6.5× outside the maximum premium the model can generate at the paper's own β̂₁ and θ̄ | Methods C3; **verified by editor** against Tables 3 and 4 | The model is rejected as a quantitative description of the lead segment, by its own reported primitives, and the rejection is not reported. This is not repairable by robustness checks — it requires a model that can produce the fact, or an honest statement that the structural interpretation is restricted to the segment where it is not rejected. Independent of F1. |

**Two FATALs → Reject.**

### ADDRESSABLE

Ranked by how much of the paper each one carries. Items marked **[convergent]** were raised independently by both separately-fenced referees.

| # | Concern | From | Suggested path |
|---|---|---|---|
| A1 | The control group (disclosed E/F/G) is directly treated by the rental-ban provision of the *same* statute on the *same* date. Nowhere addressed — the manuscript uses the ban at `03-setting:47` and `04-structural:38` as institutional motivation for the A–D/E–G cut and at `01-intro:71` as a reason investors are EPC-sensitive, never as a confound. | Domain C2 | Re-estimate against a control not subject to the letting ban — disclosed D-rated listings, or the full disclosed distribution reweighted to the non-disclosers' hedonic profile. Alternatively exploit the ban's own phasing (G 2025, F 2028) against the July 2021 opposability date. |
| A2 | No standard error, CI, or bootstrap anywhere, on any structural or policy object. "Std" is cross-market dispersion and is occasionally read as precision. Compounded by generated regressors, two-step estimation, and a ratio with a near-zero denominator. **[convergent]** (methods C5; domain C1/C6; desk table-format review) | Both + desk | Market-level block bootstrap resampling from listing data through *both* steps (index → DiD → inversion); Fieller intervals on ρ̂ₘ specifically; clustering statement in every table note; uncertainty on every §5 aggregate. |
| A3 | σ₁* = 0 is stated as holding "in any equilibrium," licenses the simplified belief function that produces both ρ̂ and ĉ₀, and is rejected by the paper's own Appendix Table A.1 (σ̂₁ = 5.1% vs σ̂₀ = 5.5%; 2.1% vs 2.2%) — with the reversal under the alternative cut read as *support* for the baseline cut. **[convergent]** (domain C6; methods C6) | Both | Test H₀: σ₁ₘ = 0 with SEs; state whether the σ₁-from-registry rows use the general or simplified belief function and redo with the general one if not; demote the corollary to a testable prediction and report in the main text that it fails; keep the institutional argument for the D–E cut and drop the claim that it is corroborated by passing the test. |
| A4 | The two compared groups are never shown comparable, and §3.3.1 concedes apartment non-disclosers occupy the highest price tier from 2019. | Domain C1 | Pre-period listing-level balance table on the full hedonic vector plus market covariates, with normalized differences; event-study coefficients with market-clustered SEs and a joint pre-trend F-test in the text. |
| A5 | Group membership is re-sorted by the treatment (verified disclosers 7.4% → ~50%; non-disclosure share 35.9% → 28.9% / 24.6% → 9.7%), and the sign of the resulting bias is not established. | Domain C3 | Cohort-stable estimate on a fixed market panel and fixed reference property; DFL/Oaxaca reweighting to the pre-period non-discloser distribution to split compositional shift from within-composition repricing. |
| A6 | First stage selects on the sign of its own denominator — 25 of 68 apartment markets dropped for β̂₁ₘ ≤ 0, then ρ̂ₘ formed by dividing by β̂₁ₘ (mean 1.7%, cross-market SD 3.5pp). That 37% of apartment markets show a *negative* energy-efficiency premium is itself unreported in the text. | Methods C4 | Do not drop — report the full β̂₁ₘ distribution with SEs and the share distinguishable from zero; use a bounded/regularised estimator; show conclusions survive inverse-variance weighting rather than sign selection. |
| A7 | The abstract's headline number is a DiD *change* presented as a *level* premium, and §3.3.1 says house non-disclosers start near the bottom of the price distribution — so the 3.4% "premium over disclosed E/F/G" may be false in levels. | Domain C4 | Report the post-reform hedonic-adjusted *level* gap for both segments with its SE; state the abstract's claim in whichever object is actually true; if the house level premium is negative, say so. |
| A8 | K = 0 measures registry coverage, not seller ignorance; π̂ trends mechanically from 7.4% to ~50% and is then pooled into one "primitive." The no-falsification assumption classifies 32.2% of apartment and **51.2% of house** listings as truthful disclosers, untested — and the direct test is cheap and absent. | Methods C9 | Re-estimate on 2024 alone and report stability of the four-group decomposition, π̂ₘ, σ̂₀ₘ, ĉ₀ₘ; report shares by year; **report the displayed-vs-registry grade mismatch rate among matched disclosers** as a direct test of no-falsification. |
| A9 | K ⊥ θ rests on a narrative about forced sales with no number, no citation, no test, and θ̄ₘ enters ĉ₀ₘ directly — with Table A.1 showing the quality cut moves ĉ₀ from 3.42% to 1.62%. | Methods C10 | Benchmark the K=1 grade distribution against ADEME's published national/départemental stock distribution to sign and bound the violation; or use audit-supply shifters (assessor density, waiting times) as a K-shifter plausibly orthogonal to θ. |
| A10 | The pricing layer is internally inconsistent: the FOC proof gives ∂p*/∂v₁ < 1 while the premium proof asserts p* = E[v]. The identifying equation comes from the asserted version. Also: the Disclosure Incentives proposition omits c₀ and is as written false for c₀ > 0; and Lemma 1's cancellation is executed in revenue units but implemented in price-gap units. | Methods C11 | Derive p*(d,θ;e) from the stated FOC, characterise pass-through κ, and either show κ cancels from Δ/(β₁e*) or carry it through and estimate it from the transaction data already used for γ₀, γ₁. **This is also the only venue in which F1 can be rebutted.** |
| A11 | Internal numeric contradictions across the whole manuscript: six irreconcilable market-count statements (40/100, 45/97, 49/104, 43/107, 42+3/76+21, 40/100); two values of ĉ₀ for houses (1.8% vs 4.5%, with the text saying the smaller feeds §5); two values of σ̂₀ (7.7%/3.7% vs 14.0%/5.7%); ĉ₀ = 3.4% > β̂₁ = 1.7%, impossible under the table's own estimator; €15.5bn (§5.4) vs €14.6bn (Conclusion); three values of audit coverage; "full-unravelling" used for a regime the model does not define; and a corrupted sentence in the Conclusion ("5.7% of house sellers do.7% of house sellers do so"). **[convergent]** (domain minors; methods C8; desk) | Both + desk | One reconciliation table defining the estimation sample once — base markets, each filter, markets dropped by each, final N by type — referenced everywhere; a stated regime-classification rule; corrections with a note on which value is used where. Per the desk review: **generate these, do not type them.** `main.tex` currently `\input{}`s no generated table and every number is hand-typed while the upstream artifacts in `results/tables/` sit uncommitted-modified. Wire the exhibits and run `/audit-reproducibility` before resubmitting anywhere. |
| A12 | `lu_energy_2023` ("Energy Labels, House Prices, and Efficiency Misreporting") sits in the author's own `DPE_library.bib:828` and is cited nowhere. It documents deliberate DPE misreporting in French administrative data — the most direct available challenge to No Falsification. Same for `dranove_jin`, `jin_leslie`, `shin_burden`, `eichholtz_kok_quigley_2010`, `cassidy_how`. | Desk | Verify the entry (bib says 2023, the probe suggests a 2025 *Real Estate Economics* article — the entry may be stale), then engage it in §4.2 where No Falsification is maintained. Pairs naturally with A8's mismatch-rate test. |
| A13 | §4.2.3 promises two cross-market specification tests; neither appears in §4.4. One of them (Δ̂ₘ ⊥ ρ̂ₘ) is untestable with this estimator because ρ̂ₘ is constructed from Δ̂ₘ — which is itself worth saying. | Methods C5 (checks), minor 3 | Run them or remove the promise, and state why the first is untestable. |

### TASTE (author may push back)

| Concern | From | Editor's view |
|---|---|---|
| "Lemma 1 is the result that vacates the section's need for the model" (methods C7, framing) | Methods | **Push back — I do not accept this framing.** Proving *which* object governs the renovation margin, and that c₀ and π do not, is a selection theorem and a genuine contribution; a reduced-form paper would not know which coefficient to multiply by the price level, or that enforcement is inert on this margin. The author should say so explicitly in §5.1 rather than leaving the referee to draw the opposite inference. What is **not** pushable is C7(a): the abstract's "zero to the full renovation cost" range is generated by markets where ρ̂ₘ was clipped to zero because a noisy DiD returned Δ̂ₘ ≤ 0. Re-report §5 excluding those markets and state the range where the first stage is informative. Also fix the R̄ arithmetic — β̂₁ = 1.7% with mean R̄ = €165/m² implies ~€8,900/m² average across 40 *zones d'emploi*, which is not credible; the house figures reconcile fine. |
| "The composition-bias story contradicts the model's own pooling structure" (methods C2) | Methods | Correct as a matter of the model *as written* — if buyers cannot distinguish the pool, there is no within-pool price dispersion for composition to act on. But the author's answer is an extension (noisy signal of K, or agent sorting), not a defense, and it is downstream of F1/F2. **Should address**, but it is not where the paper lives or dies. |
| β̂₁ = 1.7% is 3–6× below cited EPC-capitalisation estimates | Methods (sanity check) | Partly pushable — β̂₁ here is a DiD *change* at a specific quality cut, not a level capitalisation, so the comparison is not apples-to-apples. But the paper must run the benchmarking exercise and explain the gap; "no prior estimate is referenced anywhere" is the actual defect, and it is the referee's declared critical peeve. Same for ĉ₀ ≈ €10–20k as the cost of omitting a €100–250 document — that needs an explanation regardless. |
| Remark (welfare) belongs before the maps | Domain | Preference. Both referees praised the remark's substance; placement is the author's call. |
| Panel A/B unit mixing; "Std" relabelling; volume filter says transactions but is applied to listings | Methods minors | Fix them — they are cheap — but none is a decision item. |

---

## Where the referees disagreed, and what I make of it

**1. Scope of the fatal problem.** Referee B holds that the identification algebra cannot be repaired by revision; Referee A treats the same suspicion (its Concern 5) as one of six major concerns in a Major Revision. *Editor's view:* B is right, and A's own Concern 5 is the tell — A raised the possibility that "Δ̂/(β̂₁·ê*) ≡ 1 by construction… the estimator is uninformative about ρ by algebra rather than by data limitation," then did not follow it to its conclusion, precisely as A criticises the paper for doing elsewhere. I verified it; it is true. A's verdict is the right one for the paper A thought it was reading.

**2. The causal-inference threat.** Referee A's primary concern — that the E/F/G control group is directly treated by the rental-ban provision of the same law on the same date — is not weighed by Referee B at all, whose lens stopped at the structural layer. *Editor's view: this stands entirely on its own and must not be absorbed into the structural discussion.* It is the one concern that threatens the reduced-form result the author will be left with after the structural layer is withdrawn. Note that the rental-ban story predicts exactly the joint pattern the paper reads as corroborating in `04-structural-draft.tex:375` — β̂₁ and Δ̂ moving together, at the same markets, on the same date — because both share a newly-penalised denominator group. The paper's strongest stated defense of parallel trends is therefore also consistent with the leading alternative. **A1 is the first thing to fix in any resubmission anywhere.**

**3. What the §5 counterfactual means.** B reads Lemma 1 as vacating the model's necessity; A treats the same Lemma as "a genuinely non-obvious policy implication… worth defending properly." *Editor's view: A is closer to right on the theory, B is right on the implementation.* Both can hold: the Lemma is a real result, and §5 as executed is a reduced-form exercise whose headline dispersion is a clipping artefact.

**4. What converged.** Four defects were flagged independently by both referees under different dispositions and different fencing: the corrupted Conclusion sentence, the market-count drift, the total absence of inference, and σ₁ = 0 being contradicted by the paper's own Appendix Table A.1 and then framed as support. Convergence from differently-fenced referees is the strongest signal this process produces, and all four are mechanically checkable — the editor confirmed the last one's arithmetic independently. **None of these is arguable. They are simply to be fixed.**

---

## Response-planning block

**MUST address before this manuscript is sent anywhere** (in this order — the ranking is by how much of the paper each one carries):

1. **F1 + F2 together, as one decision.** Either (a) produce the formal identification proposition Referee B asked for — the three observed indices written as explicit functions of (ρ, β₁, e*, c₀) under the *FOC* pricing rule, with a full-rank Jacobian at the estimates — or (b) withdraw ρ̂ from the paper, present ĉ₀ under a maintained ρ = 1 throughout, and state in the abstract and §4 that the model's feasibility bound Δ̂ₘ ≤ β̂₁ₘθ̄ₘ is violated in the apartment segment. Route (a) is legitimate and narrow; route (b) is honest and available today. **What is not available is the status quo**, in which a clipped indicator is narrated as "nearly all buyers price energy performance."
2. **A1 — rebuild the DiD against a control group not hit by the rental ban.** This is prior to everything else, because it determines whether there is a premium to explain.
3. **A2 — inference on everything**, via a two-step market-level block bootstrap plus Fieller on any ratio.
4. **A3 — test σ₁ = 0 and report that it fails**, and stop reading the cut that passes as evidence for the cut.
5. **A11 — reconcile every number, from generated exhibits.** A referee who catches four contradictions stops checking and starts doubting; Referee A said so in those words, and it is why the methods referee called an individually-small cluster "jointly disqualifying."
6. **A4–A10, A12–A13** — the balance table, the re-sorting decomposition, the level-vs-change restatement, the sign-selection fix, the coverage-vs-ignorance tests, the K ⊥ θ benchmark, the pricing-layer derivation, the Lu citation.

**SHOULD address:** methods C2's pooling inconsistency; the parameter-plausibility benchmarking against the EPC-capitalisation literature; the §5 magnitude reconciliation and the re-reported cost-share range; the promised §4.2.3 tests; the table-convention and unit fixes.

**MAY push back:** the claim that Lemma 1 vacates the model's role in §5 — with the selection-theorem argument made explicitly in the text rather than left implicit; the direct comparability of β̂₁ to level capitalisation estimates; the placement of the welfare remark.

---

## Editor's note to the author

Both referees, independently, went out of their way to say the project is excellent, and the editor agrees with them. Referee B's closing paragraph is the right advice and is endorsed here as the editorial position: **the listing↔ADEME match, §3's four stylized facts, and the documented non-disclosure premium are strong enough to carry a paper at this journal on their own.** Direct observation of seller information status at listing time is the object the Dye/Jung–Kwon literature has always had to treat as latent, and that measurement contribution is untouched by anything above.

What is being rejected is the structural layer, and the rejection is not a matter of taste or of insufficient robustness checks — it is two pieces of arithmetic on the paper's own equations and its own Table 4, re-derived independently rather than taken on referee authority. A resubmission that leads with the measurement contribution and the reduced-form premium, defends that premium against the rental-ban alternative, attaches inference to it, and uses the model as a *disciplining device* — to say which object governs the renovation margin, and to state honestly which of its restrictions the data reject — would be a paper worth sending out again. A resubmission that repairs the ρ identification with a genuine second source of variation would be a larger paper still, but the Bartik failure means that instrument does not currently exist, and the smaller paper soon is preferable to the larger one never.

One process recommendation, from the desk review and endorsed by Referee B: `main.tex` currently `\input{}`s no generated table, every number is hand-typed, and the upstream artifacts under `results/tables/` are modified-uncommitted as of this review. That configuration *is* the mechanism that produces the A11 cluster. Wire the exhibits to `results/` and run `/audit-reproducibility` before the next submission. The single-source-of-truth rule in the project's own `CLAUDE.md` would have caught most of A11 mechanically.

---

**Files read for this synthesis:**
- `quality_reports/peer_review_paper-real-estate/desk_review.md`
- `quality_reports/peer_review_paper-real-estate/referee_domain.md`
- `quality_reports/peer_review_paper-real-estate/referee_methods.md`
- `paper-real-estate/main.tex` (Appendix pricing proofs `:426–466`, `:556–588`; §5.3–5.4 `:237–291`; Conclusion `:297–305`)
- `paper-real-estate/sections/04-structural-draft.tex` (buyer valuations `:108–124`; Table 3 `:251–253`; identification `:362–409`; Table 4 `:455–484`)
- `paper-real-estate/sections/03-setting-draft.tex` (`:47`, rental-ban treatment of the control group)
- `paper-real-estate/sections/01-introduction-draft.tex` (`:71`)
