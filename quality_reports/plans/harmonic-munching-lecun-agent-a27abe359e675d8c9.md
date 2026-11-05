# Integration design: limited attention to silence (notes Part IV) into `paper-real-estate/`

**Status:** DRAFT (read-only design; nothing in the repo edited). **Date:** 2026-10-08.
**Written to the plan file** because plan mode allows no other write. The requested scratchpad copy (`…/scratchpad/integration_design.md`) does not exist yet. Copy this file there once plan mode ends.
**Sources read:** `playground/notes.md` Part III (1694–2823), Part IV (2824–3405), Exploratory check (3409–3495), Open questions (3497–3567); `paper-real-estate/main.tex`; `sections/01,02,03,04,A-robustness.tex`; `paper/bp-template-concise.cls`; `paper/DPE_library.bib`; `src/model.py`; `results/*/anchored_diagnostics.csv`; scratchpad `*.py`.
**Uncommitted work to protect:** `sections/03-setting-draft.tex` (fig-note sample line) and `sections/04-structural-draft.tex` (Panel A of `tab:did_results` moved to 45/97, log-point units, 04:373, 04:474–510, 04:591–594). Every anchor below is quoted from the **working tree**, so the edits go on top of that work. The two new files avoid most of the overlap.

---

## 0. Headline findings (read first)

1. **Placement.** §4.6 goes in a **new file** `sections/04-attention-draft.tex`, `\input` after `main.tex:54`. Appendix A-ATT goes in **new** `sections/A-attention.tex`, `\input` after `main.tex:707` (end of `app:proofs`). This keeps edits to the uncommitted `04-structural-draft.tex` to about six local replacements.
2. **Environments.** `definition`, `assumption`, `lemma`, `proposition` and `corollary` all exist (`bp-template-concise.cls:285–290`), numbered **per section** (so Part IV's "Prop 6" renders as Prop 4.6, Lemma 6 as Lemma 4.2, Def 1 as Def 4.1, Assumption 2 as Assumption 4.2). `proof` is a numbered *theorem* there, not amsthm, and there is **no `remark`**. `\theequation` is `Eq.~N`, so `\eqref` prints "(Eq. N)" with **global** numbering. No class fix is needed.
3. **The structural reading of DiD as levels is the single largest consistency issue** (§4 below, item M1). Part IV's Table 9 row "hiding cost 2.4 → 8.5", §4.6.6 and Prop 10(iv) equate a **level** (c₀ = Δ in Partial Pooling) with the **DiD** Δ̂. The paper's own `lem:model_bounds`(ii) (A-robustness:196–200) says the DiD premium is **zero** in Partial Pooling (PP) with c₀ reform-invariant. Both the baseline λ̂ test and the extension are coherent only under an unstated assumption: **no pre-reform energy pricing (ρω^pre ≈ 0)**. That assumption must be stated once, in §4.4, before §4.6 is pasted.
4. **Three mathematical defects in Part IV** that the existing sympy checks do not catch:
   - **(M2) Prop 7(ii) / Cor 3.** In Complete Adverse Selection (CAS), high-type hiding is a *strategic complement* (∂ẽ/∂σ₁ = ψ∂e/∂σ₁ > 0). So σ₁ ∈ {0,1} can both be equilibria. A numerical example is verified below.
   - **(M3) Prop 9.** It drops c₁: σ₁ should be F(g₁ − c₁).
   - **(M4) "Exact pricing".** The claim that "every ordering holds under exact logit" is unproven. P*(v) is not well defined for a three-segment mixture, and the Part IV text still carries an `[Author: …]` stub.
5. **Interactions that break existing claims.** If ĉ₀^att = Δ̂ = 8.5 is adopted for apartments, these existing claims stop holding:
   - "concealment costs similar across segments → set by regime" (04:500–502, 536–540; intro 01:159–160);
   - the notary-fee comparison (04:489–499);
   - "every market is Partial Pooling" (04:526–534; main.tex 211, 220, 244, 248). Under the extension the PP band in apartments is about 0.09 log points wide, so interior hiding must be read through dispersed costs (Prop 9).
6. **Bibliography.** Only `allcott_is_2012` (Allcott–Greenstone 2012) exists. All 15 attention references are missing.

---

## 1. Placement map

### 1.0 Files and global wiring

| Action | File | Anchor (quote) | Insert |
|---|---|---|---|
| new file | `paper-real-estate/sections/04-attention-draft.tex` | n/a | all of §4.6 (4.6–4.6.6 + footnotes) |
| wire §4.6 | `main.tex` | line 54 `\input{sections/04-structural-draft}` | next line: `\input{sections/04-attention-draft}`. It continues §4 because there is no `\section` in between, so the subsection numbers as 4.6. |
| new file | `paper-real-estate/sections/A-attention.tex` | n/a | `\section{Limited Attention to Silence: Proofs}\label{app:attention}` + all A-ATT |
| wire appendix | `main.tex` | line 707 `\noindent\textit{Summary of policy reading.} …` (last paragraph of `app:proofs`), before line 709 `% BIBLIOGRAPHY` | `\input{sections/A-attention}` |
| macros | `main.tex` preamble | after line 21 `}` (end of `stagecard2`), before `\begin{document}` | `\input{../results/tables/attention_macros}` (generated, §5) |

Conventions to follow (from the existing files):
- Proof pointer in the main text: `\noindent\textit{Proof.} See Appendix~\ref{app:attention}. $\Box$` (as at 04:203).
- Appendix proofs: `\subsection*{Proof of Lemma~\ref{…} (Title)}` followed by `\begin{proof}…\end{proof}` (as in main.tex:426–439).
- Enumerated parts inside results: `\begin{enumerate}[label=(\roman*)]`.
- Tables: `\toprule\toprule … \bottomrule\bottomrule`, `\small\renewcommand{\arraystretch}{1.5}` (as in `tab:equilibria`, 04:244–258).
- Footnotes: `\footnote{}` inline.
- Markdown bullet lists in Part IV ("Economic reading", "What (4.25) says", "Qualifications") become prose paragraphs. Section 4 uses no `itemize`.

### 1.1 Block-by-block (all into `04-attention-draft.tex` unless noted)

| Part IV block | Env / LaTeX | Label | Notes |
|---|---|---|---|
| 4.6 heading + 2 intro paragraphs | `\subsection{Limited Attention to Silence}` | `ss:attention` | Cite `tab:did_results` for 8.5/4.1/3.9/5.8. "37 of them" → macro `\attNdeltaGtBapt`. |
| 4.6.1 Motivation | `\subsubsection{Motivation}` | `ss:att_motivation` | The ceiling argument should cite `lem:model_bounds`(i), which already gives Δ/β₁ = e ≤ θ̄ ≤ 1, rather than re-derive it. 4.5/1.6/94%/0.1 → macros. [^cap] → `\footnote` (levels 2.6→7.0 → macros). |
| "Alternatives ruled out" (3 items) | prose | — | Third item references the paper's α_k<β_k (04:121). [^comp] → `\footnote`, G2-dependent. |
| "Attention" lit paragraph | prose + `\citet/\citep` | — | Keys in §6. |
| "Why apartment buyers" (3 features) | prose | — | Feature 3 contradicts 03:39–43 (DPE mandatory before marketing). It must say "in practice, despite the mandate". The `[Author: document in Section 3]` stub needs a paragraph in `ss:institutions` after 03:51 (see §2). [^ads] carries a `[CHECK]` on the 1 Jan 2022 obligations: verify against the ANIL source before pasting. |
| "Mechanism in three steps" | prose | — | Author rewrites (writing-with-ai rule). |
| 4.6.2 Setup | `\subsubsection{Setup}` | `ss:att_setup` | |
| Environment & timing | `\paragraph{Environment and Timing}` + `enumerate` | — | Mirrors 04:77. "Assumption 1" → `Assumption~\ref{ass:independence}`. |
| Payoffs & hiding costs | `\paragraph{}` | — | **Notation clash N1** (§4): "hiding cost C(θ,d)" sits next to energy cost C_θ. |
| "Why we rewrite the valuation" (bonus vs cost form) | prose | — | Recommend keeping 1 paragraph in the main text and moving the rest to the appendix (decision D3). |
| C_{θ,m} display | `equation*` | — | Refs `assum:energy_anchor`, `eq:energy_anchor` (A-robustness:205–214) exist. |
| η (4.20) | `equation` | `eq:eta` | |
| Lemma 6 | `lemma`[Bonus and Cost Forms] | `lem:cost_form` | (4.21) inside it → `equation`, `eq:csil`. |
| Definition 1 | `definition`[Default Energy Cost] | `def:default_cost` | Three benchmarks → prose. Forward refs to Prop 6(iii), Prop 10(iii). |
| Normalisation + "why it stops being innocuous" + departure display | prose + `equation*` | — | Move to appendix with D3 if desired. Departure formula verified (sympy). |
| "Why the cost form is better" | prose | — | Appendix candidate (D3). |
| Assumption 2 | `assumption`[Display-Dependent Attention] | `assum:attention` | Label prefix follows the newer `assum:energy_anchor`. ψ and effective attention are defined right after it. |
| Table 7 | `table` | `tab:att_buyers` | Notes mention δ₀, δ_n: clash N3. |
| demand (4.22) | `equation` | `eq:demand_att` | Remove the sentence "Every ordering result below holds under the exact logit demand" (M4) or soften it (§4). |
| p^d_θ, p_H, p_L, p_sil definitions | prose | — | Trap N6: paper's p₁* = displayed **low**. Keep the explicit mapping sentence and drop p^d_θ where p_H/p_L suffice. |
| Lemma 7 | `lemma`[Prices and the Perceived Cost of Silence] | `lem:att_prices` | (4.23) `eq:b_att`, (4.24) `eq:premium_att`. |
| Beliefs paragraph | `\paragraph{Beliefs and the Effective Belief}` | — | Restate e(σ₀,σ₁) **by reference** to `eq:belief_general`, not as a new display (duplication). |
| Definition 2 | `definition`[Effective Belief] | `def:effective_belief` | |
| 4-step derivation | prose + `align*` | — | q(C) unnumbered. Replace r^def by e^def (N2). (4.25) → `equation`, `eq:etilde`. |
| Lemma 8 | `lemma`[Effective-Belief Monotonicity] | `lem:etilde_monotone` | The one-line proof stays inline (as at 04:183). |
| 4.6.3 Equilibrium | `\subsubsection{Equilibrium}` | `ss:att_equilibrium` | |
| gains (4.26) | `equation` | `eq:gains` | g_θ: clash with g(·) at main.tex:692 (N5). |
| Δ_ψ (4.27) | `equation` | `eq:Delta_psi` | |
| Prop 6 | `proposition`[Disclosure Incentives under Limited Attention] | `prop:att_incentives` | Fix (iv) (M5). [^default] → `\footnote`. |
| Testable implication (crossing point) | prose | — | Needs letter-level indices (open data question). Phrase it as a prediction, not a result. |
| Cor 3 | `corollary`[High-Quality Sellers Disclose outside CAS] | `cor:att_hq` | Fix CAS statement (M2). |
| Φ_ψ (4.28) | `equation` | `eq:Phi_psi` | |
| Prop 7 | `proposition`[Equilibrium under Limited Attention] | `prop:att_equilibrium` | (4.29) → `eq:att_pp`. Fix (ii) (M2). |
| Table 8 | `table` | `tab:att_equilibria` | Notes: "At ψ=1 the table reduces to Table~\ref{tab:equilibria}". |
| Cor 4 + empirical paragraph | `corollary`[The Partial Pooling Band] | `cor:att_band` | All band numbers → macros. Fix the aggregation issue (M6). |
| Prop 8 | `proposition`[Comparative Statics under Limited Attention] | `prop:att_cs` | Cites `prop:comparative_statics`. |
| Dispersed hiding costs + Prop 9 | `proposition`[Equilibrium with Dispersed Hiding Costs] | `prop:att_dispersed` | (4.30) `eq:att_dispersed`. Fix c₁ (M3). Use F_c, not F (N4). Statement in the main text, uniqueness bound to the appendix (D2). [^nonstrategic] → `\footnote`. |
| Welfare | `\paragraph{Welfare}` | — | (4.31) `eq:att_markup`. Correct the reference price (M7). |
| 4.6.4 Reform & identification | `\subsubsection{The Reform and Identification}` | `ss:att_identification` | Define the δx operator (N3). (4.32) → `eq:att_lambda`. |
| Prop 10 | `proposition`[Identification under Limited Attention] | `prop:att_identification` | (iv) needs the pre-reform assumption (M1). [^levels], [^ematters] → `\footnote`. |
| 4.6.5 Estimates + Table 9 | `\subsubsection{Estimates}` + `table` | `ss:att_estimates`, `tab:attention` | Body `\input{../results/tables/table_attention_body}`. [^estimator], [^gband] → `\footnote`. [^gband] is **deleted** once G3 is done. |
| 4.6.6 Policy | `\subsubsection{Policy Implications}` | `ss:att_policy` | Cross-ref `sec:policy`, `lem:threshold_regimes`, `eq:threshold_pp`. |
| A-ATT proofs (Lemmas 6–8, Props 6–10, Cor 3) | `A-attention.tex`, `\subsection*{Proof of …}` + `proof` | `app:attention` | Lemma 7 step (e): replace the re-derivation with "the special case ω₁=ω₀=1 reproduces \eqref{eq:premium_derived}". |
| A-ATT numerical illustration | `\subsection*{A Numerical Illustration}` | — | C₀=327, C₁=185, C̄^sil=243 are band-midpoint means (G3-dependent) → macros, or round illustrative values labelled as such. |
| A-ATT two caveats (pool belief moves; post-reform attention) | prose inside Prop 10 proof | — | Promote "pre-reform attention to silence zero" to the main text (M1). |
| A-ATT "Exact pricing" | `\subsection*{Exact Logit Pricing}` | `app:att_exact` | Rewrite (M4). |
| A-ATT "Estimator" + MC | `\subsection*{The Ratio-of-Means Estimator}` | `app:att_estimator` | Rename u_m, v_m → ξ^β_m, ξ^Δ_m (v clashes with valuations v₀,v₁). Use 𝔼_m for the cross-market expectation. MC numbers → macros. |

---

## 2. Existing paper text that must change

Every change below is **one or two sentences on top of the current text**. The baseline is not rewritten. G = depends on gate checks.

| # | Location | Current (short quote) | Change | G? |
|---|---|---|---|---|
| P1 | `main.tex:40` abstract | "…a divergence we trace to a measurable over-identifying wedge, reported directly rather than resolved by construction." | Append a clause: a limited-attention extension reads the apartment wedge as buyers not attending to energy when no rating is shown, and estimates it with one parameter. Give no number until G3. | no (wording); a number would be G3 |
| P2 | `01:150` | "The estimates deliver two structural magnitudes and one specification test." | Leave as is (baseline). | — |
| P3 | `01:165–171` | "Measurement noise from the registry match, … thinner buyer bargaining positions … are all candidates we examine in Section~\ref{sec:results}, and none of them move the point estimates above." | Replace with 2 sentences: the baseline cannot reach the wedge because the premium cannot exceed the efficiency premium. An extension in which buyers attend less to energy on silent listings (Section~\ref{ss:attention}) reproduces it, rejects full attention in apartments but not in houses, and leaves ρ̂ unchanged. | ψ̂ numbers: G2/G3 |
| P4 | `01:172–174` | "We maintain, rather than test, the model's prediction that informed sellers of high-quality properties never conceal; … essentially unchanged." | Keep. Add 1 clause: under limited attention this prediction holds only outside CAS (Cor~\ref{cor:att_hq}). Do **not** cite the 54–59% A–D hider share here (G2). | G2 for any number |
| P5 | `01:188–190` ¶12 | "The standard diagnosis appeals to split incentives, credit constraints, and inattention to future energy costs." | One sentence: the extension connects the paper's channel to the energy-cost-inattention literature (Allcott 2011; Sallee 2014; Allcott–Taubinsky 2015). | no |
| P6 | `01:219–233` lit strands | "Our paper draws on three strands of work." | Either a 4th strand (salience/limited attention and disclosure to inattentive receivers: Hirshleifer–Teoh; DellaVigna–Pollet; Jin–Luca–Martin; Hagenbach–Saucet) or fold it into strand 1. **D9.** | no |
| P7 | `01:205–217` ¶12.5 policy | "…invariant to enforcement against hiding…" | Keep (R̄=b survives, verified). Optionally add the salience instrument (D8). | λ̂ numbers: no |
| P8 | `04:60–66` §4.1 | "And it maintains Corollary~\ref{cor:hq_disclose}, $\sigma_1^*=0$, rather than testing it." | Keep. Append: "Section~\ref{ss:attention} relaxes the buyer side and shows where this restriction survives." | no |
| P9 | `04:363` | "The DiD does not require that buyers were entirely inattentive to EPC scores before July 2021; it requires only that…" | Keep for parallel trends. **Add a maintained assumption** in §4.4 (after 04:367): the structural mapping reads reform-induced changes as post-reform levels, i.e. no pre-reform energy pricing (ρ^pre≈0), with pre-reform level gaps attributed to non-energy components that are constant across the reform. This is what makes ρ̂ = ρ^post, ĉ₀ = β̂₁ê*, the λ̂ test, ψ̂_δ = ψ^post and Prop 10(iv) coherent at the same time (M1). **D6.** | no |
| P10 | `04:428` | "This is also why we do not simply set $\hat c_{0,m}=\hat\Delta_m$, which the indifference condition would seem to license: that shortcut imposes the restriction we want to examine." | Keep. Append: "Section~\ref{ss:attention} uses the restriction instead to measure attention to silent listings, at which point the hiding cost is read off $\hat\Delta_m$ (Proposition~\ref{prop:att_identification})." Also change "return to it in Section~\ref{sec:results} and Appendix~\ref{app:robustness}" → add "and Section~\ref{ss:attention}". | no |
| P11 | `04:526–534` | "The cost can therefore never land outside the Partial Pooling band, and every market in the sample is classified as Partial Pooling." | Add: "This classification is a property of the baseline. Under limited attention the band narrows by the factor ψ (Corollary~\ref{cor:att_band}), and interior hiding in apartments is read through dispersed costs (Proposition~\ref{prop:att_dispersed})." | band width: G3 |
| P12 | `04:536–540` and `04:497–502` | "…strikingly similar across the two segments … points to a cost set by the legal disclosure regime rather than by the property." / "…land within roughly one percentage point…" | **Conflicts with ĉ₀^att(apt)=Δ̂≈8.5.** Either qualify ("in the baseline; the extension attributes the apartment premium to attention, and the cost it implies is larger, Section~\ref{ss:att_estimates}"), or keep the baseline ĉ₀ as headline and present 8.5 only as the extension's alternative reading. **D7.** The notary-fee comparison (04:489–499) inherits the same decision. | G2/G3 for the number |
| P13 | `04:555–589` | Two paragraphs, starting "The apartment wedge deserves a closer look, because more than one channel could produce it…" and ending "…the object of study rather than a residual." | **Replace** with a ≤6-line bridge: the wedge exceeds what any pool belief can deliver (cite `lem:model_bounds`(i)), forward ref to `ss:attention`. The four candidates are dropped. Notes item 12 found that candidate 1 (registry noise attenuates β̂₁) misattributes the noise, because β̂₁ uses displayed letters, and that candidate 3 (risk premium) has the wrong sign. If kept, keep at most the "coarseness / substitute signals" candidate as one sentence (it corresponds to Task 2). | no |
| P14 | `04:602–610` | "…because a thinner pool of strategic hiders leaves buyers less pessimistic … the whole pattern is what the model's equilibrium comparative statics predict…" | Qualify the last sentence: the ordering of hiding rates fits the baseline, but the *level* of the apartment premium does not (Section~\ref{ss:attention}). The causal clause on the premium as written is internally odd: a thinner hider pool should raise e and the premium, not lower it. Flag it for an author rewrite. | no |
| P15 | `A-robustness:193–201` `lem:model_bounds`(ii) | "…the model predicts a DiD non-disclosure premium of zero…" | Under P9 it does not apply (PP did not hold pre-reform). Either restate it as conditional on PP in both periods, or delete it. Otherwise it contradicts the λ̂ test at 04:428 **and** Prop 10. **D6.** | no |
| P16 | `A-robustness:6–25, 80–90` | σ₁ robustness, "invoking Corollary~\ref{cor:hq_disclose}" | Add 1 sentence: under the extension with ẽ>1 and dispersed costs, σ₁>0 is predicted in apartments (Prop 9(iii)). The "σ₁ from registry" row is then the extension-consistent specification for apartments. The registry shows A–D at 54–59% of informed hiders in **both** segments, which points to non-strategic silence (G2). | G2 |
| P17 | `main.tex:65` + footnote at 185 | "…three different margins…" | Keep three. Optionally add salience as a 4th instrument in a footnote pointing to `ss:att_policy` (D8). | no |
| P18 | `main.tex:76, 108` | "…Corollary~\ref{cor:hq_disclose} … is exactly the result that rules it out." / "omitted as strictly dominated (Corollary~\ref{cor:hq_disclose})" | Add 1 sentence or footnote: with a single hiding cost the strategy stays dominated in PP under limited attention (Cor~\ref{cor:att_hq}). With dispersed costs a low-cost seller may renovate and then hide (Section~\ref{ss:att_policy}). | no |
| P19 | `main.tex:113` | "…positive opacity premium $\Delta(e^*) = \rho\beta_1 e^* > 0$…" | Footnote: under limited attention, read Δ_ψ(e*) (\eqref{eq:Delta_psi}). The argument is unchanged. | no |
| P20 | `main.tex:127–143` `lem:threshold_regimes` | "$\bar{R}^{\text{PP}} = \Pi(d=1,\theta=1) - \Pi(d=1,\theta=0)$" | **Stays true** (sympy E.31: R̄=b at the marginal hider, any attention). No change. §4.6.6 states the composition result. | — |
| P21 | `main.tex:177` CAS ∂R̄/∂π>0 | "$\partial \bar R/\partial \pi > 0$" | Footnote: under the extension this channel is scaled by ψ and vanishes as ψ→0 (Prop~\ref{prop:att_cs}(ii)). | no |
| P22 | `main.tex:211, 220, 244, 248` | "Every market in our estimation sample sits in the Partial Pooling regime…" | Add one sentence at 211 only: under limited attention the threshold still equals the energy-efficiency premium for the marginal seller (PP or the margin of F_c), so the euro figures are unchanged. **Do not** recompute subsidies with `src/model.py`: `solve_equilibrium`/`renovation_threshold` (model.py:390, 508) hard-code full attention. Feeding them ĉ₀=8.5 would push apartments into Cost-Deterred Hiding and change R̄. | no |
| P23 | `main.tex:275` conclusion | "…but the indifference prediction itself holds for houses and is decisively rejected for apartments, where the non-disclosure premium exceeds…" | Append 1–2 sentences: one parameter, attention to silent listings, accounts for the rejection in apartments and the fit in houses. Give the number after G2/G3. | G2/G3 |
| P24 | `main.tex:277` | "The regulator faces three distinct instruments…" | Optional salience sentence (D8). "Tightening enforcement … does not move the renovation threshold" stays true. | no |
| P25 | `03-setting` after `03:51` (end of `ss:institutions`) | (no current text) | New ≤5-line paragraph: from 1 Jan 2022, listings must show the estimated annual energy bill ([CHECK]); collective heating is paid through service charges; certificates still pending at listing despite the mandate. Part IV 4.6.1 needs this. Sits next to the uncommitted 03 edit (line ~235). Insert only; no conflict. | no ([CHECK] facts) |
| P26 | `02:38–49` assumptions (a)–(d) | "It rests on four assumptions." | **No change recommended** (keeps the baseline framing). Optional footnote noting the implicit assumption that receivers attend to and reason about silence (Jin–Luca–Martin 2021). | no |

---

## 3. Cross-reference mapping (Part IV placeholder → paper label)

| Part IV says | Paper label (existing) / new label |
|---|---|
| Section 3 | `sec:setting` / `ss:institutions` |
| Section 4.2 | `ss:model_setup` |
| Section 4.3 | `sec:equilibrium` |
| Section 4.4 | `sec:identification` (beliefs: `sec:beliefs`) |
| Section 4.5 | `sec:results` (4.5.2 has no label; refer to `sec:results`) |
| Section 4.6.x | `ss:attention`, `ss:att_motivation`, `ss:att_setup`, `ss:att_equilibrium`, `ss:att_identification`, `ss:att_estimates`, `ss:att_policy` |
| Section 5 | `sec:policy` (`sec:policy_empirical` for magnitudes) |
| Appendix A-ATT | `app:attention` (+ `app:att_exact`, `app:att_estimator`) |
| Appendix (linear pricing) | `app:proofs`, `eq:premium_derived` |
| Table 4 | `tab:did_results` |
| Table 7 / 8 / 9 | `tab:att_buyers` / `tab:att_equilibria` / `tab:attention` |
| Table "equilibria" | `tab:equilibria` |
| Assumption 1 (K⊥θ) | `ass:independence` |
| Assumption 2 | `assum:attention` |
| Assumption energy anchor | `assum:energy_anchor`, `eq:energy_anchor` |
| Definition 1 / 2 | `def:default_cost` / `def:effective_belief` |
| Lemma 6 / 7 / 8 | `lem:cost_form` / `lem:att_prices` / `lem:etilde_monotone` |
| Lemma belief monotone | `lem:belief_monotone` |
| Prop 6 / 7 / 8 / 9 / 10 | `prop:att_incentives` / `prop:att_equilibrium` / `prop:att_cs` / `prop:att_dispersed` / `prop:att_identification` |
| Prop premium / equilibrium / comparative statics | `prop:premium` / `prop:equilibrium` / `prop:comparative_statics` |
| Cor 3 / 4 | `cor:att_hq` / `cor:att_band` |
| Cor hq_disclose | `cor:hq_disclose` |
| (4.20) η | `eq:eta` |
| (4.21) C̄^sil | `eq:csil` |
| (4.22) demand | `eq:demand_att` (baseline `eq:demand`) |
| (4.23) / (4.24) | `eq:b_att` / `eq:premium_att` |
| (4.25) ẽ | `eq:etilde` |
| (4.26) gains | `eq:gains` |
| (4.27) Δ_ψ | `eq:Delta_psi` |
| (4.28) Φ_ψ | `eq:Phi_psi` (baseline `eq:Phi`) |
| (4.29) PP solution | `eq:att_pp` |
| (4.30) dispersed | `eq:att_dispersed` |
| (4.31) mark-up | `eq:att_markup` |
| (4.32) wedge | `eq:att_lambda` |
| belief_general / belief_simplified / premium / payoff / estar / anchored_estimator_main | existing labels, same names |
| λ̂ definition | 04:428 (no label). Add `\label{eq:lambda}`? It sits in prose, so refer to `sec:identification` instead. |
| Renovation threshold, R̄ = b | `lem:threshold_regimes`, `eq:threshold_pp` |

Rendered numbers are automatic: Prop 4.6–4.10, Lemma 4.2–4.4, Cor 4.3–4.4, Def 4.1–4.2, Assumption 4.2, "(Eq. N)". Part IV prose that says "Proposition 6" etc. must become `Proposition~\ref{…}` everywhere, including inside footnotes and the A-ATT proofs.

---

## 4. Notation and consistency audit

### 4.1 Symbol clashes left after Part IV's renames

| ID | Clash | Where | Proposed resolution | Who decides |
|---|---|---|---|---|
| N1 | **C(θ,d)** hiding-cost function vs **C_θ, C^def, C̄^sil, C\*, C^ins** energy costs | `eq:payoff` 04:101,104; `eq:seller_problem` main:71; `tab:strategies` notes main:105–106; Part IV "Payoffs" quotes C(θ,d) one paragraph before C_θ | Rename the paper's function to **c(θ,d)** (consistent with c₀,c₁). That is 5 occurrences, one of them in the uncommitted 04 file (an edit on top is fine). Part IV's energy notation stays final. | Bastien (D4) |
| N2 | **r^def** vs discount rate **r** in a(r,T) (A-robustness:211–212) and renovation choice **r∈{0,1}** (main:69) | Part IV (4.25),(4.27)–(4.29), Table 8, proofs | **Remove r^def.** Write everything with e^def (already defined: e^def = η − r^def). For example Δ_ψ(e) = b[ψe+(1−ψ)e^def], and e* = [c₀/b − (1−ψ)e^def]/ψ. Fewer symbols and no clash. | recommend; Bastien |
| N3 | **δ** as the reform operator (δx = x^post − x^pre, ψ_δ) vs **δ₀, δ_n** insensitive-buyer coefficients (04:121) | Table 7 notes write "δ₀=β₀" two paragraphs before δ(ρω₁) | Bastien fixed ψ_δ as final. Minimal fix: Table 7 notes say "when insensitive buyers value observables as sensitive ones do" with no δ₀. Optionally typeset the operator as `\updelta` or `\delta(\cdot)` with an explicit definition. | Bastien |
| N4 | **F** (hiding-cost CDF) vs **F_R** (renovation-cost CDF, main:193) and **dF(X)** (main:158) | Prop 9 | Use **F_c**, density f_c, bound f̄_c. | recommend |
| N5 | **g_θ** (hiding gains) vs **g(·)** logistic density | main:692 | Change main:692 `g(` → `G'(` (consistent with main:404, 408). It is a one-token edit in the proofs; g_θ stays. | recommend |
| N6 | p₀\*, p₁\* (paper: d=0 and **displayed-low**) vs p^d_θ (Part IV: p^d_1 = **displayed-high**) | `tab:equilibria`, `eq:premium`, `eq:premium_derived` | Keep Part IV's mapping sentence ("p_sil − p_L is the premium p₀\*−p₁\*"). Prefer p_H, p_L, p_sil and avoid p^d_θ except in Lemma 7's general statement. | recommend |
| N7 | **λ**: wedge λ̂_m (04:428), reparametrisation λ (A-robustness:126), shadow cost of funds λ (main:160) | pre-existing | Not introduced by Part IV. Note it for a later pass and do not add a fourth use. | — |
| N8 | **β₁**: valuation coefficient (=C₀−C₁) vs **β_{1,m}** / β̂_{1,m} price gap (04:373; A-robustness:166 "b_m=β_{1,m}") | pre-existing; Part IV makes it visible | Part IV's sentence "β̂_{1,m} estimates δb_m" is the reconciling statement. Put it once in `ss:att_identification`. **b** already exists as b_m ≡ ρ_mβ₁ (A-robustness:119). Part IV's b = ρω₁β₁ nests it at ω₁=1: say so where b is introduced (Lemma 7). | recommend |
| N9 | **v_m** (estimator noise, A-ATT) vs valuations v₀, v₁; **H, N** in the Prop 9 proof vs subscript H and market count N | A-ATT | ξ^β_m, ξ^Δ_m; S (silent mass), S₁ (its efficient part). | recommend |
| N10 | **E** (cross-market expectation in A-ATT) vs 𝔼 and Ē_θ | A-ATT estimator | Use 𝔼_m[·] or "\overline{(\cdot)}_m". | recommend |
| — | Checked, **no clash**: ψ, ω, η, ν (not used), q(·), \mathcal C_d, Φ_ψ, Γ, φ, γ, α_k, κ (same meaning as the anchor), a(r,T), A_m, B, K, G. The \eta grep only matched \theta. | | | |

### 4.2 Duplication to avoid

- **e(σ₀,σ₁)** is restated in "Beliefs" → refer to `eq:belief_general`.
- The **ceiling** Δ ≤ b (4.6.1) is weaker than the existing `lem:model_bounds`(i) (Δ/β₁ ≤ θ̄) → cite it.
- **C_{θ,m} construction** repeats `eq:energy_anchor` → one line plus a reference.
- **Lemma 7 proof step (e)** re-derives `eq:premium_derived` → one sentence.
- The **"No Falsification", payoff, demand** restatements are already handled by "Everything not stated is as in Section 4.2". Keep that sentence and delete repeats.
- **Proof of Cor 4** ("Direct from (4.27)…") mirrors `cor:rho`(ii) → cite it.

### 4.3 Mathematical consistency (Part IV vs paper)

Re-verified this session with sympy, using inline scripts that wrote no files. Lemma 7 (b and Δ), the "departure" identity, (4.32), Prop 10(iii) monotonicity (∂ψ/∂C^def<0, so the upper bound is at C^def=0), and ∂e/∂σ₁>0 at σ₀=1 are all **OK**. `full_model_sympy.py` (16) and `ext_sympy.py` (34 identities) were re-run: **all OK**, including R̄=b at the marginal hider under any attention (E.31).

| ID | Issue | Severity | Fix |
|---|---|---|---|
| **M1** | **DiD vs level.** Prop 10(iv) and Table 9's last row read ĉ₀ = Δ̂ (a DiD). Paper `lem:model_bounds`(ii) says the DiD premium is 0 in PP with invariant c₀. Prop 10 also assumes "pool composition stable across the reform", yet PP pins Δ=c₀ by moving σ₀. Footnote [^cap] reports non-zero pre-reform level gaps (2.6). Everything is coherent only if pre-reform energy pricing ≈ 0 (pre-reform regime is then Cost-Deterred with Δ^pre=0). Under that assumption ψ_δ=ψ^post, and the A-ATT bias term vanishes because ω₀^pre=0. | **Critical** | State the assumption once in §4.4 (P9). Amend `lem:model_bounds`(ii) (P15). In Prop 10, replace "silent-pool composition stable" with "no pre-reform attention to energy, or a stable composition". Relabel Table 9's last row "δΔ̂ (= c₀ under Assumption P9)". |
| **M2** | **Prop 7(ii) / Cor 3 in CAS.** Since ∂ẽ/∂σ₁ = ψ∂e/∂σ₁ > 0, g₁ rises in σ₁, so high-type hiding is self-reinforcing. Numerical check (π=.5, θ̄=.6, e^def=2.3): ψ=.5 gives g₁/b = 0.364 at σ₁=0 and 0.450 at σ₁=1; ψ=.13 gives 1.057 and 1.079. Any (c₀+c₁)/b in between makes **both** σ₁=0 and σ₁=1 equilibria. Prop 7(ii) asserts e\*=e(1) (σ₁=0), and its proof cites Cor 3, which only covers σ₀\*<1. | Major | Prop 7(ii): "σ₀\*=1. σ₁\*=0 is an equilibrium iff ẽ(1,0) ≤ 1+(c₀+c₁)/b. Otherwise the high type also hides, and equilibria with σ₁\*∈{0,1} may coexist." Existence still holds. Uniqueness is claimed only in (iii). Cor 3 wording: "σ₁\*>0 is possible only if…". |
| **M3** | **Prop 9 drops c₁.** Paper: high type pays c₀+c₁ (04:104). Prop 9 has σ₁ = F(g₁). | Major | σ₁ = F_c(g₁ − c₁). (iii) becomes "iff g₁>c₁ and F_c(g₁−c₁)>0", which requires ẽ>1. The rate gap "≈ f·b" becomes f·(b+c₁). The uniqueness bound is unchanged (∂g₁/∂x unchanged). Alternatively assume c₁=0 explicitly. |
| **M4** | **"Exact pricing" (A-ATT) + "Every ordering … holds under exact logit" (after 4.22).** With three segments, Γ is a mixture of logits, so the optimal price is not a function of the *mean* sensitive valuation. The paper's preliminary (main:346–393) treats a single-segment FOC. The text still has an `[Author: add the argument…]` stub. | Major (overclaim) | Main text: "under the linear pricing approximation of \eqref{eq:premium_derived}". Appendix: state the exact-logit orderings as numerically verified at the estimated scale (checks2.py-style global search, moved into a script) or as a conjecture. Delete the stub. |
| **M5** | **Prop 6(iv)** "(i)–(ii) reduce to Proposition~\ref{prop:premium}". prop:premium is stated **gross of c₀** ("θ=0 strictly prefers non-disclosure whenever e>0"). Prop 6(i) with ψ=1 is net of c₀ (e > c₀/b). | Minor | "(iv) If ψ=1, ẽ=e and (i)–(ii) are the net-of-cost comparisons underlying Proposition~\ref{prop:equilibrium}. With c₀=c₁=0 they reduce to Proposition~\ref{prop:premium}." |
| **M6** | **Aggregation inconsistencies in the [E] numbers.** (a) Table 9: point ψ̂_δ=0.13 but identified interval [0, 0.12]. Under C^def=0 the point must equal the interval's upper end (Prop 10(iii)). (b) The PP band [8.40, 8.49] with "mean premium 8.53 at the upper edge": 8.53 lies *outside* the band (which formally means Cost-Deterred Hiding). By construction Δ_ψ(ê\*) = mean Δ̂ < Δ_ψ(θ̄). (c) C̄^sil is identical, [243], for both segments. | Major for numbers | One aggregation rule in the script, used for all of them: either ratio of cross-market means for every object, or per-market objects with the stated weighting. Unit-test (a) and (b) as assertions. Check (c). |
| M7 | **(4.31)** reference price "V̄ − ρC̄^sil" omits −(1−ρ)C^ins. It holds only with C^ins=0. | Minor | Write V̄ − (1−ρ)C^ins − ρC̄^sil. The mark-up is unchanged. |
| M8 | **Lemma 8 / Prop 8(i)** sign of ∂σ₀\*/∂ψ requires C^def ≤ C̄^sil (stated). ∂σ₀\*/∂C^def < 0 holds at fixed c₀ (fine). Prop 8(ii)'s condition is stated for the CDH premium. For CAS the weaker condition C^def < e(1)C₁+(1−e(1))C₀ suffices, and the stated one implies it. | OK | Add "(which implies the CAS condition)". |
| M9 | **Prop 9(ii)** bound: \|Ψ'\| uses only the σ₁ term (the σ₀ term is stabilising). Re-derived by hand: correct. | OK | — |
| M10 | **ρ̂ reinterpretation.** Prop 10(i): ρ̂ identifies δ(ρω₁). The paper reads ρ̂ as "share of buyers who price energy" (01:155–157; 04:484–487, 514–524; main:275). These are consistent only under ω₁^post=1 plus P9. | Minor (wording) | One sentence in `ss:att_identification`: "With ω₁=1 and no pre-reform energy pricing, this is the ρ_m of Section~\ref{sec:identification}." Do not touch the baseline text. |
| M11 | **Cor hq_disclose** ("In any equilibrium σ₁\*=0"). It is a baseline result and stays true in the baseline. Under the extension it becomes Cor 3 (outside CAS, single cost), and Prop 9(iii) predicts σ₁\*>0 in apartments (ẽ̂≈2.1>1). Baseline estimates impose σ₁=0 (`config_*.json: "hider_theta": "impose_zero"`). ê\* enters ψ̂ with weight ψ (footnote [^ematters]), so the apartment ψ̂ is robust. **Houses** (ẽ≈0.67<1) predict σ₁=0, yet 55% of informed house hiders are A–D. The extension does **not** resolve FINDING-sigma1, which points to non-strategic silence (G2). | Interaction | P16. Say this plainly in [^nonstrategic]. |

---

## 5. Numbers pipeline

### 5.1 New code (single source of truth)

**`scripts/compute_attention.py`** (named after `compute_subsidies.py`). It is a pure function of the files below and fixed seeds.
- **Inputs:**
  - `results/{apartment,house}/anchored_diagnostics.csv` (DiD_beta1, DiD_delta, pi_hat, theta_bar_hat, sigma_0_hat, e_star, beta1_anchor, lambda_m);
  - `data/listings_enriched_{PT}.parquet` (K, ademe_epc_score, start_date; after G2/G3 also `date_reception_dpe` and certified kWh);
  - `data/index_{PT}.csv` via `src.event_study.load_price_indices` (levels, yearly windows);
  - `src.data_prep.compute_energy_anchor` (needs a `consumption="certified"` option after G3);
  - `config_{apartment,house}.json` (`epc_threshold`).
- **Outputs:**
  - `results/attention/{apartment,house}_markets.csv`: per market η_m, Ē₀, Ē₁, C̄^sil, C\*_δ, x_m, λ̂_m, bound slack, violation flag, β̂₁ tercile.
  - `results/attention/summary.csv`: one row per segment × statistic.
  - `results/attention/bootstrap_psi.csv`: 4,999 draws over markets, fixed seed.
  - `results/tables/table_attention_body.tex`: rows of Table 9 only. Caption and notes stay in the paper.
  - `results/tables/attention_macros.tex`: `\newcommand`s, letters only, for example `\attPsiApt`.
  - Assertions: M6(a) point = interval upper end at C^def=0; M6(b) fitted premium inside the PP band under the same aggregation; recomputed means of β̂₁, Δ̂, λ̂, ĉ₀ equal the values printed in `tab:did_results` (4.1/8.5/6.1/2.4; 5.8/3.9/0.4/3.5) to 0.05.

**`scripts/mc_attention_estimator.py`** (from scratchpad `ext_mc.py`, seed fixed) → `results/attention/mc_estimator.csv` and its own macros block (`\attMCols…`, `\attMCrom…`).

**Paper wiring:** `\input{../results/tables/attention_macros}` in the preamble. Before the gates run, a stub file defines every macro as `\textbf{[XX]}`, so the paper compiles and placeholders are visible.

### 5.2 Every bracketed / computed number in Part IV

Gate key:
- **now** = computable from current files.
- **G2** = changes when K is re-split by `date_reception_dpe` and pending certificates are dropped. This needs an ADEME re-pull: the enriched parquet has **no** `date_reception_dpe`. `ADEME/match_improved.py:324–339` keeps only certificates dated before publication, so pending certificates currently sit in K=0.
- **G3** = changes when η uses certified kWh. Not in the parquet: `compute_energy_anchor` maps letters to band midpoints with G=500 (`src/data_prep.py:479`).

| Number (Part IV location) | Current source | Macro | Gate |
|---|---|---|---|
| 8.5, 4.1, 3.9, 5.8, 6.1, t=6.78 (4.6, 4.6.1) | `tab:did_results` (hard-coded in 04) | text constant; asserted by script | now |
| 37 of 45 (Δ̂>β̂₁) | new | `\attNDgtBApt` | now |
| 4.5 = mean(Δ̂−β̂₁); 1.6 = mean((1−ê\*)β̂₁) | Part III §7 | `\attExcessApt`, `\attReachApt` | 4.5 now; 1.6 G2 |
| 94% uninformed in silent pool | Part III | `\attShareUninfApt` | G2 |
| 0.1 of 6.1 (full cursedness) | Part III | `\attCursedApt` | G2 |
| [^cap] 2.6 → 7.0 (silent − verified-efficient, levels) | `levels.py` | `\attLevelGapPreApt`, `\attLevelGapPostApt` | now |
| η ≈ 2.3 apartments | `attention_check.py` | `\attEtaApt` | **G3** (+G2 via K) |
| ψ̂≈0.13, "one eighth" | `ext_checks*.py` | `\attPsiApt` | G3 |
| PP band [8.40, 8.49], width 0.09, baseline width 0.71, premium 8.53; houses [3.22, 3.96], 0.74, 3.89 | Part III §7 | `\attBandLoApt` etc. | G3 + G2 (e(1), θ̄); **fix M6(b)** |
| Prop 9 "[70] times below threshold" | Part III | `\attUniqSlackApt` | G3 + G2 |
| [^nonstrategic] 2.5% house high-type hiding; "about two log points" | registry; b(1−ẽ) | `\attSigmaOneHouse`, `\attHighLossHouse` | G2 (2.5%), G3 (two) |
| Welfare ≈ 6 (= λ̂) | `tab:did_results` | text (6.1) | now (but λ̂ uses ê\*: G2) |
| Table 9: Δ̂/β̂₁ ratio of means 2.10/0.67 | `ext_checks3.py` | `\attRatioApt/House` | now |
| Table 9: η mean 2.31/2.11 | `attention_check.py` | `\attEtaApt/House` | G3 |
| Table 9: C\*_δ 28/231; C̄^sil 243/243 | `ext_checks3.py` | `\attCstar…`, `\attCsil…` | G3 (+ check M6c) |
| Table 9: ψ̂ ROM 0.13 [−0.12, 0.37] / 0.95 [0.86, 1.04]; regression 0.21 (0.11) / 0.96 (0.04); test t 6.9/1.0; interval [0, 0.12]/[0, 0.95]; slack 0.92 (1.0)/8.38 (13.0); c₀ 2.4→8.5 / 3.5→3.9 | `ext_checks*.py`, `attention_bound.py` | body file + macros | G3 (+G2 via ê\*); fix M6(a); relabel last row (M1) |
| t=6.4 (apt vs house difference) | Part III | `\attDiffT` | G3 |
| 21 of 45 violate bound; 40% in top tercile | `attention_bound.py` | `\attNViolApt`, `\attShareViolTopApt` | G3 |
| Estimator range 0.03 / 0.13 / 0.21 / 0.53, intercept 2.8 (1.9) ([^estimator]) | `ext_checks.py` | `\attPsiMedApt` … | G3 |
| [^gband] G at 420/600 → 0.24/0.17; 20/23 | `ext_checks.py` | — | **delete after G3** |
| Trajectory 1−ψ̂: 0.53/0.76/0.72 (apt), 0.11/0.01/0.03 (house) | `ext_checks.py` WINDOWS | `\attOneMinusPsiYone…` | G3 |
| [^levels] 0.09 vs 0.80 | `ext_checks2.py` | `\attPsiLevROMApt`, `\attPsiLevSlopeApt` | G3 |
| [^ematters] <0.01; "nine times" | analytic at means | `\attSensApt`, `\attSensRatio` | G3 + G2 |
| §4.6.6: 1.6 / 2.4 / −4.5 / 8.5; 6.1 / 0.4; 8.5 vs 2.4 "three and a half"; 0.03 | mixed | macros | 1.6, 2.4: G2; 4.5, 8.5, 6.1, 0.4: now; 0.03: G3 |
| A-ATT illustration C₁=185, C₀=327, C̄^sil=243, ρ=0.5 | band-midpoint means | macros, or label as "round illustrative values" | G3 |
| A-ATT Monte Carlo 0.29–0.36 / 0.14–0.15 (45 markets, ψ=0.15) | `ext_mc.py` | `mc_attention_estimator.py` macros | now (synthetic) |
| Exploratory hiding-by-letter tables | notes 3409–3495 | **not in the paper** until G2 + the market-FE version | G2 |

`[CHECK]` facts (not numbers) to settle before pasting: [^ads] advertising obligations from 1 Jan 2022, collective-heating DPEs, and certificates pending at listing (P25).

---

## 6. Bibliography (`paper/DPE_library.bib`, natbib/plainnat)

Present: `allcott_is_2012` (Allcott–Greenstone 2012, *JEP*), which is **not** Allcott (2011). None of the 15 below exist. Proposed keys follow the dominant `firstauthor_firsttitleword_year` style. Pages and DOIs for the items verified in notes §1.7 come from there. Pull exact pages and DOI from Crossref for the rest when writing each entry: notes 3565 records all of A.11 as Crossref-verified, but the pages below are from memory. Write Kőszegi as `K{\H{o}}szegi`.

| Key | Reference |
|---|---|
| `chetty_salience_2009` | Chetty, Looney, Kroft (2009) "Salience and Taxation: Theory and Evidence", *AER* 99(4):1145–77 |
| `finkelstein_eztax_2009` | Finkelstein (2009) "E-ZTax: Tax Salience and Tax Rates", *QJE* 124(3):969–1010 |
| `brown_shrouded_2010` | Brown, Hossain, Morgan (2010) "Shrouded Attributes and Information Suppression: Evidence from the Field", *QJE* 125(2):859–76 |
| `gabaix_sparsity_2014` | Gabaix (2014) "A Sparsity-Based Model of Bounded Rationality", *QJE* 129(4):1661–1710 |
| `gabaix_behavioral_2019` | Gabaix (2019) "Behavioral Inattention", *Handbook of Behavioral Economics* Vol. 2, 261–343 (`@incollection`) |
| `koszegi_model_2013` | Kőszegi, Szeidl (2013) "A Model of Focusing in Economic Choice", *QJE* 128(1):53–104 |
| `bordalo_salience_2013` | Bordalo, Gennaioli, Shleifer (2013) "Salience and Consumer Choice", *JPE* 121(5):803–43 |
| `allcott_consumers_2011` | Allcott (2011) "Consumers' Perceptions and Misperceptions of Energy Costs", *AER P&P* 101(3):98–104 |
| `sallee_rational_2014` | Sallee (2014) "Rational Inattention and Energy Efficiency", *J. Law & Econ.* 57(3):781–820 |
| `allcott_evaluating_2015` | Allcott, Taubinsky (2015) "Evaluating Behaviorally Motivated Policy: Experimental Evidence from the Lightbulb Market", *AER* 105(8):2501–38 |
| `hirshleifer_limited_2003` | Hirshleifer, Teoh (2003) "Limited Attention, Information Disclosure, and Financial Reporting", *JAE* 36(1–3):337–86 |
| `dellavigna_investor_2009` | DellaVigna, Pollet (2009) "Investor Inattention and Friday Earnings Announcements", *JF* 64(2):709–49 |
| `eyster_cursed_2005` | Eyster, Rabin (2005) "Cursed Equilibrium", *Econometrica* 73(5):1623–72 |
| `jin_is_2021` | Jin, Luca, Martin (2021) "Is No News (Perceived as) Bad News? An Experimental Investigation of Information Disclosure", *AEJ: Micro* 13(2):141–73 |
| `hagenbach_motivated_2025` | Hagenbach, Saucet (2025) "Motivated Skepticism", *REStud* 92(3):1882–1919, doi:10.1093/restud/rdae058 |

The bib is a symlink to `paper/DPE_library.bib`, which `paper/main_concise.tex` shares. Adding entries is safe. Run `/validate-bib` after.

---

## 7. Implementation sequence

| Phase | Content | Size | Verify |
|---|---|---|---|
| **0. Gates and decisions** | Bastien answers D1–D10. Run G1 internally (not in the paper), G2 and G3. These need an ADEME re-pull with `date_reception_dpe` and certified consumption: a separate data plan touching `ADEME/enrich_listings.py` and `src/data_prep.compute_energy_anchor`. Also notes Q5 (is the letter visible on some d=0 listings?) and Q6 (are new builds K=0 by construction?), which can kill the premium before attention matters. | data work, 1–2 sessions | gate results logged in `quality_reports/` |
| **1. Plumbing** | 15 bib entries. Macro stub `results/tables/attention_macros.tex` (all `[XX]`). Preamble `\input`. Notation fixes if approved: N1 rename (5 tokens), N5 `g(`→`G'(` at main:692. | ~40 lines | `latexmk -pdf`; `grep -E "undefined|multiply" main.log` clean; `/validate-bib` |
| **2. Theory §4.6.1–4.6.4** | `sections/04-attention-draft.tex` with the M2–M8 fixes and r^def removed (N2). `\input` after main:54. | ~380 lines LaTeX | compile; label audit (`grep -o '\\ref{[^}]*}'` vs `\label`); re-run `full_model_sympy.py`, `ext_sympy.py`, plus new checks for M2/M3/M5 fixes (port to `explorations/attention-sympy/` or keep in scratch) |
| **3. Appendix A-ATT** | `sections/A-attention.tex` (proofs, exact-pricing rewrite M4, estimator, MC). `\input` after main:707. | ~220 lines | compile; every `\ref` resolves; each proof cites the right label |
| **4. Numbers** | `scripts/compute_attention.py`, `scripts/mc_attention_estimator.py`; real macros and table body. Before the gates: run on the current data and check against Part IV's [E] values (pipeline parity). After the gates: final values. | ~350 lines Python | M6 assertions pass; `/audit-reproducibility`; `/review-python` |
| **5. §4.6.5–4.6.6 + edits to existing text** | Table 9 with caption/notes; P1–P25. The author writes the load-bearing sentences (abstract, intro ¶9, 4.6 opening, mechanism, interpretation of estimates) per `writing-with-ai.md`. | ~150 lines new + ~25 local edits | compile; `/humanize` (detect only); diff limited to the listed anchors (`git diff --stat`) |
| **6. Review** | `structural-micro-reviewer` on §4.4–4.6 + A-ATT + the scripts; `/verify-claims` on the attention literature paragraph. | — | findings validated (`scripts/validate-findings.py`) |

**Decisions that remain Bastien's**
- **D1** Insert now with `[XX]` placeholders, or wait for G2/G3? Recommendation: Phases 1–3 now (theory carries no numbers). Phases 4–5 only after the gates.
- **D2** Prop 9: statement in the main text (it is needed for interior hiding, renovate-then-hide and P11), uniqueness bound and proof in the appendix. Or all in the appendix.
- **D3** How much of "why we rewrite the valuation" stays in the main text. Recommendation: one paragraph plus Lemma 6; normalisation and "why cost form" go to the appendix.
- **D4** Rename the paper's C(θ,d) to c(θ,d) (N1), and the δ₀/δ_n handling (N3).
- **D5** Quality threshold. A–D is the baseline (`epc_threshold: 4.0`). Houses' C\*≈231 kWh lies between D (215.5) and E (290.5), and the A–C/D–G hider composition is flat. Discuss the threshold in the paper or not? It changes θ̄, ê\*, Ē_θ and η.
- **D6** Adopt the "no pre-reform energy pricing" maintained assumption (P9) and amend `lem:model_bounds`(ii) (P15). Required for M1.
- **D7** Headline concealment cost for apartments: the baseline 2.4 (with the extension's 8.5 as an alternative reading), or the extension's value. This determines P12, the notary comparison and the intro ¶9.
- **D8** Add salience as a policy instrument in §5/conclusion, or keep it inside §4.6.6.
- **D9** Literature placement: a new strand in the intro, or folded into strand 1.
- **D10** Keep or drop the four-candidate paragraph's "coarseness / substitute signals" sentence (P13).

---

## 8. Risks (what a referee attacks first)

1. **DiD read as levels (M1).** "Your hiding cost of 8.5 is a difference-in-differences. Your own Lemma model_bounds(ii) says the DiD premium is zero in Partial Pooling." Without P9 and P15 the extension and the baseline λ̂ test are both exposed. Highest priority.
2. **The extension sits on its own boundary.**
   - Apartment slack is about 0.9 log points (t≈1).
   - 21/45 markets violate the bound.
   - ψ̂ CI [−0.12, 0.37] includes 0 and negative values.
   - Identification needs C^def=0, so ψ is only an upper bound.
   - Expected reading: "one free parameter fits one moment exactly". The paper must lead with the bound test, the "no constant" test and the house/apartment contrast as the evidence, not with ψ̂'s level.
3. **η built from band midpoints with G=500 (G3).** The anchor text already claims certified consumption (notes item 14: the paper says certified, the code uses midpoints). Attention makes this load-bearing, because η is the bound.
4. **Composition before mechanism (notes Q1/R4, Q5, Q6).** If silent apartment listings are disproportionately new builds (K=0 by construction) or show the letter elsewhere on the page, the premium is about *what* is silent, not *how buyers attend*. This must be checked before the extension is presented as the resolution.
5. **Non-strategic silence (G2).** A–D make up 54–59% of informed hiders in both segments. The extension predicts strategic high-type hiding only in apartments, yet the composition is the same in houses. Reading informed silence as concealment is unsupported in either model until pending certificates are removed. Corollary hq_disclose / σ₁=0 imposed remains the paper's weakest maintained restriction.
6. **Institutional contradiction.** "Dwellings are routinely put on the market before their certificate is available" (4.6.1) versus 03:39–43 ("obligation to commission a DPE before marketing … predates" the reform). It needs documentation (P25) or must be dropped.
7. **Default cost has no housing evidence.** Footnote [^default] concedes that the default-cost assumption is the one the extension most depends on.
8. **CAS multiplicity (M2), the c₁ omission (M3), the exact-logit overclaim (M4).** These are easy referee wins if they are not fixed before pasting.
9. **Claims that become inconsistent if the extension is added without the gates.**
   - P12/D7: "similar concealment costs across segments → regime-determined" (04:500–502, 536–540; 01:159–160), and the notary comparison. These clash with ĉ₀^att≈8.5 vs 3.9.
   - P11/P22: "every market Partial Pooling" (04:531; main 211/220/244/248). This clashes with a 0.09-wide band.
   - P14 (04:606–610): "the whole pattern is what the model's equilibrium comparative statics predict" clashes with 4.6.1.
   - Intro 01:166 "a genuine specification tension we report rather than explain away" contradicts adding an explanation; it needs P3.
   - Abstract "reported directly rather than resolved by construction" stays true only if ψ is presented as an interpretation of λ̂, not a re-fit (P1).
   - §5 euro magnitudes stay valid (R̄=b), **provided** nobody re-runs `compute_subsidies.py` with ĉ₀=Δ̂ through the full-attention `solve_equilibrium`.
10. **Agencies.** Part IV contains no mention of agencies or delegated disclosure (checked: only the generic word "agent" in the Gabaix sentence). Keep G1 out of every paper artifact, including script names and macro names (`compute_attention.py`, no `realtor_*` outputs under `results/tables/`).
