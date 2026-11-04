# Plan: restructure Section 4.4 Identification

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Nothing edited yet.
Second of four section-level passes (4.1 done; this is 4.4; then 4.5; then Section 4 as a whole). Inputs: Explore inventory (labels, citations, pointers, paragraph map, overlaps, numbers verified against `results/`), micro-theorist assessment, and a drafting pass applying the narrativize rules and the humanizer checklist. Same procedure as 4.1 to 4.3.

## Context

`\subsection{Identification}` (`sec:identification`, `sections/04-structural-draft.tex`, ~lines 452-570, ~3,500-3,900 words) still builds the full-attention benchmark first: the first four subsubsections set up the anchored rho estimator, c_0 = beta_1 e*, and lambda as a specification test, and the attention model arrives only in the last subsubsection (`ss:att_identification`). Section 4.3 now hands over with "what the estimated premia and the registry allow us to recover", and the section does not answer that. The fact it never states, and that should set its order: everything except the scale rho*omega_1 is identified without the energy anchor.

## Assessment (what is wrong)

**The missing fact.** psi_delta (eq:att_lambda) and the perceived cost of silence zeta*_delta use only beta-hat_1, Delta-hat, e*-hat and eta, which needs certified consumption only; c_0 = Delta-hat in Partial Pooling is anchor-free too. The anchor fixes the scale rho*omega_1 and nothing else.

**Order and seams.** Current order: reform -> gaps -> registry belief -> anchor and rho -> over-identifying test -> attention (last). Problems:
- The gaps are used in 4.4.1 before they are defined in 4.4.2.
- 4.4.3 -> 4.4.4 opens with the benchmark question ("the premium equation appears to deliver rho"); the right question is now psi.
- 4.3's handover promises psi and the mark-up; the section opens on "two objects, rho and c_0".
- Exit to 4.5 ends on a footnote.

**Stale or wrong statements (L455-569).**
1. "Two objects, rho and c_0"; "c_0 follows from the disclosed-price gap and the hiding rate" (c_0 = Delta-hat under attention).
2. "Reform shifts rho"; "DiD of the premium identifies rho" (it shifts rho*omega_1 and rho*omega_0; the premium DiD identifies zeta*_delta).
3. lambda as a "specification test of the model" (it is the moment that identifies psi; lambda = 0 tests psi = 1).
4. "The ratio returns approximately one / the restriction fails / decisively rejected" (under attention the probability limit is e-tilde/e*; Delta-hat > beta-hat_1 e*-hat is the model's prediction).
5. "We do not simply set c_0-hat = Delta-hat" (that is now the paper's measure, Prop att_identification(iv)).
6. Pointers: two `Section~\ref{ss:attention}` now land on 4.2 The Model, not the estimates (L541); `eq:belief_simplified` and `eq:premium` are in the benchmark appendix (use `eq:belief_general`, `eq:b_att`, `eq:premium_att`); `cor:ratio_specification_test` and `lem:model_bounds` are benchmark-only.
7. The footnote "Delta = rho beta_1 e* unreliable" uses the benchmark equation; "Chapter 1" conflicts with the published citation for the indices; "36 months after" (post-period Jul 2021 to Jul 2024 is 37); the DiD post-window includes H2 2021, which a footnote calls unreliable for beta-hat_1, never reconciled; certified consumption (anchor) vs band midpoints (eta, provisional) in the notes.
8. beta_{1,m,t} (observed gap), beta_{1,m} (structural quality premium) and beta-hat_{1,m} (estimate of b = rho omega_1 beta_1) share a symbol; the data object and the model object are never separated.

**Soundness items.**
1. Prop att_identification(i) needs the anchor assumption (`assum:energy_anchor`); say so, and say that (ii)-(iv) do not depend on it.
2. The c_0-fixed assumption with no_pre_pricing implies pre-reform sigma_0 = 0 (no energy gain from hiding, so any c_0 > 0 deters it); untestable here (no pre-reform registry match). State it.
3. "Selection on beta-hat_1 > 0" is justified as "required to invert", a benchmark rationale; the ratio-of-sums estimator does not need it, and A-attention Step 4 says selection biases psi-hat toward one. State it as a choice and give its cost.
4. The common-psi-per-segment assumption and zeta^def = 0 normalisation appear only in 4.5; bring them into 4.4. "lambda = 0 tests psi = 1" requires eta_m > e*_m (eq:att_lambda is undefined at equality); state the condition.
5. psi_delta is point-identified only under zeta^def = 0 (otherwise bounded); the opening should say "given zeta^def = 0" and not call zeta^def an estimand.

**Repeated material.** The reform-demand-not-c_0 argument is stated three times (L461, L476 footnote, L476 text); parallel trends twice; the ratio cancellation three times (L457, L515, A-robustness); sample counts in L484, L543, table notes and 4.5; lambda numbers and the "1 of 45 / 5 of 97" counts in 4.4 and 4.5.

**Hard-coded numbers (all checked against `results/` and correct).** 40/45, 54/97 (rho at the boundary), 1/45, 5/97 (rho-hat above one), 81/114/49/104/45/97 (sample), lambda 6.1 (t=6.78) and 0.4 (t=1.10), EUR 0.21/kWh, 3.75%, ten years.

## Proposed structure

Five parts, descriptive titles, each opening on the question the previous one leaves:

| # | Part | Question it answers |
|---|---|---|
| 0 | Opening | Which objects are recovered and what does each need? States the anchor-free fact; hands over from 4.3. |
| 1 | The reform and the two price gaps (merges 4.4.1 and 4.4.2) | What did the reform change in prices, and is it a demand response? Gaps defined first, then DiD, parallel trends, `assum:no_pre_pricing` (both clauses), ONE supply-side paragraph with the open unobserved-composition case, `fig:ATT`. |
| 2 | What the registry measures (`sec:beliefs`) | What should a buyer infer from silence? e*-hat from pi, thetabar, sigma_0; eta; Partial Pooling classification from sigma-hat_0 in (0,1); sigma_1 treated as imposed. |
| 3 | Attention to silence and the cost of hiding (`ss:att_identification`) | How much of the reform's new attention reached silent listings? Leads with `eq:att_lambda`; lambda = 0 as the test of full attention (with the eta > e* condition); Prop att_identification (i)-(iv) with the anchor assumption in (i); common psi per segment and the normalisation; the three testable implications. |
| 4 | The scale of attention | How many buyers price ratings at all? The anchor and rho-hat = rho*omega_1, unclipped; one sentence that psi does not depend on price, rate or horizon. |
| 5 | Close | Hands to Table `tab:attention` and `tab:did_results` in 4.5. |

## What moves, where, and what is cut

| Item | Action |
|---|---|
| Naive-ratio degeneracy argument (L515, L457 in part) and `fig:rho_saturation` with its 40/45, 54/97 counts | One core sentence; argument and figure move to A-robustness `app:rho_identification`, which already holds the formal version (`prop:scale_nonid`, `cor:ratio_specification_test`). Update A-attention:411 which points at 4.4 for c_0 |
| Anchor calibration (EUR 0.21/kWh, 3.75%, T = 10), L527-531 | One core sentence; details to `app:energy_costs` (main.tex), alongside the existing anchor formula |
| `eq:anchored_estimator_main` | rho-hat half stays in part 4; the c_0 = beta-hat_1 e*-hat half goes with the benchmark estimates to `app:rho_identification` |
| L537-541 (c_0 = beta_1 e*, "not simply Delta-hat", "restriction rejected") | Rewritten as the attention reading (stale items 3-5); numbers (t-statistics, counts) go to 4.5 and are replaced by macros `\attLamApt` etc. where they exist |
| Bartik footnote (L461) and long simultaneity argument (L474) | New A-robustness subsection `app:supply_stability`; one core sentence |
| Sample-filter cascade (81/114 -> 49/104 -> 45/97) and the repeated sample size (L543) | Table notes of `tab:did_results` |
| Footnotes at L567 and L569 (levels vs differences, estimation sensitivity with macros) | Move to 4.5 or to A-attention near the proof of Prop att_identification |
| `eq:estar` (orphan label) | Kept (cited from nowhere; harmless) |

## Cross-references

- Labels that must survive: `sec:identification` (main.tex:73, A-attention:411, A-robustness, 4.2/4.3), `sec:beliefs`, `ss:att_identification`, `assum:no_pre_pricing` (Section 3, A-attention proofs), `eq:estar`, `eq:att_lambda` (main.tex:311), `prop:att_identification` (A-attention proof, A-robustness:117), `fig:ATT`, `eq:anchored_estimator_main`, `fig:rho_saturation` (moves with its text; label kept).
- New labels: `app:supply_stability` (A-robustness), subsubsection labels.
- Hard-coded part numbers: Prop att_identification (iii) and (iv) cited at L110 and L443; keep the proposition's order.
- Fix `ss:attention` pointers at L541 and the benchmark-only pointers (L502, L515, L523, L541).
- Header comment at L3 calls the benchmark "Appendix E": verify against the compiled lettering and correct if wrong.
- Numbers to macros where derivable from `results/*/anchored_diagnostics.csv` (40/45, 54/97, 1/45, 5/97): add macros in `scripts/compute_attention.py` (regenerate; diff must show only new macro lines); sample-filter counts stay typed in the table notes (flag).

## Transition logic (drafted wording; author owns load-bearing passages)

- Handover from 4.3: "Neither the mark-up nor the attention parameters behind it are observed directly. Section 4.4 sets out which of them the reform and the registry recover, and which need a benchmark from outside the price system."
- Opening: "Four objects are recovered market by market: the effective attention to displayed ratings rho*omega_1, the spillover psi of that attention to silent listings, the perceived cost of silence it enters, and the hiding cost c_0. Only the first needs information from outside the price system... The energy-cost anchor fixes the scale rho*omega_1 and nothing else." (wording to be corrected to "given zeta^def = 0" for psi.)
- Part openers: "The first question is what the reform changed in prices..."; "Prices alone do not say what a buyer should infer from silence, so the next question is what the registry reveals about the silent pool."; "With the two gaps and the registry belief in hand, the question is how much of the reform's new attention reached listings that show no rating."; "What remains is the scale of attention itself, which the price gaps cannot supply..."
Style rules: no signposts that announce what follows, at most one em-dash per paragraph, no "not X but Y".

## Execution (after approval; compile after every step)

1. Back up files. Add new appendix homes (`app:supply_stability`; benchmark-estimates text and `fig:rho_saturation` into `app:rho_identification`; calibration into `app:energy_costs`); compile.
2. Add macros for the derivable counts and regenerate (`compute_attention.py`); verify only new macro lines differ; compile.
3. Rebuild 4.4 in the new order with the corrected statements; fix pointers; compile.
4. Fresh micro-theorist check of 4.4 and the appendix homes; apply findings.
5. `/narrativize` on 4.4, then the humanizer in advisory mode; apply what you approve.
6. Grep all moved/renamed labels and part numbers; `latexmk` twice; zero undefined and zero multiply defined labels.
7. Update the session log. No commit until asked.

## Verification

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex`: no undefined references or duplicate labels; page count noted.
- All numbers unchanged (only placement, macros and the stated corrections change); new macros equal the previously hard-coded values.
- Reader test: every symbol in 4.4 defined or glossed at first use; beta_{1,m,t} / beta_{1,m} / beta-hat_{1,m} distinguished.
- Independent fenced read of 4.4 (neutral copy) per `review-fencing.md`.

## Decisions and flags for the author

- Confirm the five-part arc and moving the naive-ratio argument and `fig:rho_saturation` to A-robustness (not Appendix E, because A-robustness already holds the formal version).
- Confirm that the c_0 = beta-hat_1 e*-hat estimate (full-attention value) is demoted to the appendix, while the main text states only c_0 = Delta-hat.
- The sign claim "psi < 1 implies lambda > 0" needs eta_m > e*_m; confirm it holds in the data (it does at the segment level; market by market not checked).
- Does Prop att_identification (ii)-(iv) really need no euro valuation of energy (drafted claim; the proof is in `app:attention`)? I will check it in step 4.
- The H2 2021 window: the difference-in-differences post-period includes it while a footnote says beta-hat_1 is near zero there. Keep as is (state it once) or exclude it? This changes no numbers if only stated.
- The drafted transitions are a starting point; the paragraphs tagged `[AUTHOR REWRITE]` in this section are yours.
