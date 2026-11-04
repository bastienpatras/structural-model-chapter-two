# Plan: Section 4.5 Estimates without the systematic benchmark comparison

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Supersedes `2026-11-01_restructure-estimates-4-5.md` (its structure, tables and appendix moves stand; its "Silence above the full-attention ceiling" part and its benchmark-vs-attention fit are dropped).
Inputs: Explore inventory of the attention figures and remaining benchmark mentions; micro-theorist assessment of the new 4.5. The comparison has already been removed from the 4.5 text, the `tab:attention` rows and notes, and the fit paragraph (done at your request; paper compiles, 82 pages). What remains is the plan and the full procedure on the new version: figures, rebuild, check, narrativize, humanizer.

## Context

You decided that the systematic comparison with the full-attention benchmark "did not persist in the core of the paper". In 4.5 it is out: the ceiling part and its figure (moved to the appendix cost-form subsection), the benchmark prediction rows of Table `tab:attention` (panel C is now the attention model's own fit), the "full attention is rejected" framing, and the benchmark-vs-attention fit paragraph. Section 4.1 keeps the puzzle as a reduced-form fact (Fact 5), so 4.5 only has to estimate the model that resolves it, which one sentence in the opener can say.

## Assessment of the new 4.5

**Arc.** The opening has no question and no headline: it lists the window and rho-hat, and rho-hat plays no part in psi or zeta*. "Roughly half of buyers" misreads rho*omega_1 (it is the share of the energy-bill benchmark the market pays). Right arc: open on the question (how much of the reform's attention reached silent listings, and what does that imply sellers pay to hide?) with the headline (silent apartments are priced as if they cost 31 kWh instead of 244, so psi-hat = 0.13; houses 0.95), then Attention to Silence, then What Silence Pays (which absorbs the fit), then a short coda that hands Section 5 its inputs.

**What still compares to the benchmark (to drop).** `fig_att_F1_fit` (hollow benchmark markers, joining lines, "Benchmark" row in the stats box); line ~554 ("classification of markets by regime at the full-attention hiding cost"); line ~622 (raw premium and the Partial Pooling band); `main.tex:71` ("reproduces the apartment premium that the full-attention benchmark cannot reach", "2.4 and 3.5 in the full-attention benchmark", pointer to `ss:att_fit`); F5 (benchmark vs model, orphan). **Model-internal, can stay:** zeta-bar^sil as the upper end of the identified interval (rename "rational cost" to "registry cost of the silent pool" and drop "what an attentive buyer would assign"), the ceiling slack and the 21-of-45 count, and the lambda-hat mark-up as a counterfactual price inside the model.

**Stale or wrong in the new text.**
1. The ordering paragraph says "5 apartment and 43 house markets lie between the two displayed ratings" as if house markets deviated; that is the house case. The deviating house markets are the 33 above beta-hat and those below zero.
2. The c_0 sentence leans on a regime the data reject: 0 of 45 apartment markets are in their own Partial Pooling band at the raw premium. The two calibrations are one object (`c0_fit` = predicted premium = the cost that reproduces sigma-hat_0, whose mean equals Delta-hat by just-identification, `compute_attention.py` l.319-324). Lead with that; present c_0 = Delta-hat as an average identity, not as Prop att_identification(iv) applied to an average market.
3. The fit is weaker than the text says. RMSE (5.9) and the residual SD (5.9) are the same number when the mean residual is zero. The honest reference is the SD of observed Delta-hat (6.35 apartments, 4.43 houses): the model cuts RMSE by about 7 and 12 percent relative to a constant (R-squared about 0.14 and 0.22). The 0.43 correlation is partly mechanical (beta-hat enters the prediction and both gaps share the E-to-G base).
4. "5.9% and 2.8%" (registry-quality hiding rates) are typed; 15.2 vs 5.9 is a factor of 2.5 and deserves a clause.
5. Table notes: "in apartments it uses one parameter" holds in both segments; say which rows are beta-weighted. The 4.4 hand-over promises "the hiding cost" in `tab:attention`, which has no c_0 row.
6. Transaction-cost footnote: 84 of 101 departments and 6.31% need a [CHECK] and postdate the sample; 8.5 log points is about 8.9 percent of price, so the apartment cost exceeds the notary bill. Cut the footnote to one sentence.
7. Pointers: 4.3 l.418 credits `ss:att_pays` with "estimated premia and effective belief" (those are in `ss:att_estimates`); `main.tex:71` -> `ss:att_fit` is stale; A-attention l.259 and l.468 point at `ss:att_estimates` correctly.
8. "Selection on beta-hat_1 > 0 biases toward one" (l.605, l.610) is asserted; cite the Monte Carlo (`app:att_estimator`) or hedge.
9. "The evidence rests on ... Figure (appendix)" (l.635): the main text should not rest its evidence on an appendix figure.

## Proposed structure of 4.5

| # | Part | Question it answers |
|---|---|---|
| 0 | Opener (no subsection) | How much of the reform's attention reached silent listings, and what does that imply sellers pay to hide? Headline numbers; window stated once; one sentence saying the Fact 5 puzzle is a reduced-form fact that the model below resolves, so no structural test of it is needed here. |
| 1 | Attention to Silence (`ss:att_estimates`) | `tab:attention` (panels A data, B attention, C fit), perceived cost of silence vs the registry cost of the silent pool, psi with its identified interval and bound, the limits (ceiling slack, 21 of 45; houses fit only on average), why apartment buyers may not attend, pointer to `app:att_qualifications`. Figure `fig:att_contrast` (left panel only). |
| 2 | What Silence Pays (`ss:att_pays`) | Ordering via Cor att_ordering (counts fixed), the hiding cost (calibrated to the predicted premium, mean = Delta-hat; the registry-quality hiding rates 5.9/2.8 as macros; transaction costs with the units note), rent and transfer lambda-hat, and the fit (honest reference: SD of Delta-hat, RMSE, R-squared, correlation partly mechanical) with the revised `fig:att_fit`. `ss:att_fit` kept as a label on the fit paragraph. |
| 3 | Coda | Hands Section 5 its inputs: b = rho-hat beta-hat_1, c_0, psi-hat; `tab:did_results` (registry inputs and the anchored scale) placed here, with its sample-construction notes; "about half of the energy-bill benchmark" replaces "roughly half of buyers". |

## Figures (via `pyplot-specialist`, per the visual-polish rule)

| Figure | Change |
|---|---|
| `fig_att_F1_fit` (`fig:att_fit`, main text) | Rebuild attention-only: observed Delta-hat against the attention-model prediction with the 45-degree line and a horizontal line at the mean Delta-hat as the constant-prediction reference; stats box reports RMSE next to SD(Delta-hat), the correlation, and R-squared; drop hollow benchmark markers, joining lines, "Benchmark" row and legend entries. Bootstrap error bars on Delta-hat only if market-level standard errors exist in the results files (otherwise omit and say so). Keep the output filename. |
| `fig_att_F3_contrast` (`fig:att_contrast`, main text) | Keep the left panel (zeta* vs registry cost of the silent pool); move the right panel (psi by estimator and G midpoint) into a separate figure in `app:att_qualifications`; rename "rational cost" to "registry cost of the silent pool". New file name for the appendix panel. |
| `fig_att_F2a_belief`, `fig_att_F2_ceilings` (appendix) | Keep; retitle the captions around the attention ceiling; no change to data. |
| `fig_att_F5_hiding_cost` (orphan, benchmark vs model) | Stop generating it from `main()`; leave the file in place unless you say delete. |
| `fig_att_F6_salience` (orphan, attention-only) | Unchanged. |

New macros in `compute_attention.py` (diff must show only new lines): SD of observed Delta-hat per segment (`attDlSd*`), R-squared (`attRSqExt*`), and the registry-quality hiding rates if derivable from the results files (otherwise they stay typed with the pointer to `tab:robustness`).

## Other places that present the comparison as a result (decision for you)

- **Abstract** (`main.tex:44`): "With full attention the premium equals the concealment cost, and this restriction fits houses but is rejected for apartments... which full attention cannot produce."
- **Introduction** findings paragraph (`01-introduction-draft.tex` ~l.145-170): "It does not hold for apartments... Limited attention can price silence above a verified efficient rating... fits houses as before".
- **4.3** band paragraph (~l.382): reports the apartment band width against the benchmark's width (`\attBandWidthApt` vs `\attBandWidthBaseApt`).
- **4.4** (~l.530) and **Section 3** (l.118): mention the full-attention cost or value; **appendix** `app:c0_fullattention` and `A-benchmark.tex` hold the benchmark by design.
Recommended: rewrite the abstract and the Introduction paragraph so the estimates are described on their own terms (and keep the puzzle in 4.1 as a reduced-form fact), drop the numeric comparison in 4.3, and leave the appendices. I will not touch these until you confirm.

## Execution (after approval; compile after every step)

1. Back up files, scripts, results tables and figures. Add the new macros and regenerate; the macro diff shows only new lines.
2. Figures via `pyplot-specialist` (F1 rebuild, F3 split, appendix captions, F5 call removed); check each rendered figure; compile.
3. Rebuild 4.5 text to the new structure (opener, two parts, coda), fix the stale items above, rewrite the table notes, repoint `ss:att_*` references (4.3 l.418, 4.4 hand-over, `main.tex:71`), cut the notary footnote; compile twice.
4. Fresh micro-theorist check of 4.5, tables, figures and appendix homes; apply findings.
5. `/narrativize` on 4.5, then the humanizer in advisory mode; apply what you approve.
6. Grep moved/renamed labels; `latexmk` twice; zero undefined and zero multiply defined labels. Update the session log. No commit until asked.

## Verification

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex`: no undefined references or duplicate labels; page count noted.
- Every number in 4.5 is a macro equal to the previously typed value (or a stated correction); macro file differs only by new lines; the regenerated tables match the macros.
- Each regenerated figure viewed after rendering: no clipping, no benchmark wording, legends consistent with the text.
- Reader test: each symbol defined or glossed at first use; units consistent (percent vs log points); no "full attention", "benchmark", "core" or "extension" left in 4.5 or its figures except in the appendix pointers.
- Independent fenced read of the new 4.5 (neutral copy) per `review-fencing.md`.

## Decisions and flags for the author

- Extend the removal to the abstract, the Introduction findings paragraph and the 4.3 band comparison (recommended), or limit it to 4.5 and leave those as they are?
- Keep `tab:did_results` (registry inputs and rho-hat) as the coda table (recommended), or move it to the appendix?
- Add bootstrap error bars to the fit figure if market-level standard errors exist? (The assessment says it is what makes "explains the level, not the dispersion" honest.)
- Delete `fig_att_F5_hiding_cost` and its function, or only stop generating it?
- `app:c0_fullattention` and `A-benchmark.tex` keep the benchmark in the appendix; do you want those left alone?
- The transaction-cost footnote (84 of 101 departments, 6.31 percent, April 2025) is unsourced and postdates the sample; cut it or find the source?
- The drafted transitions are a starting point; the `[AUTHOR REWRITE]` paragraphs are yours.
