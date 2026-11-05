# Plan: restructure Section 4.5 Estimates

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Nothing edited yet.
Third of four section-level passes (4.1 and 4.4 done; this is 4.5; then Section 4 as a whole). Inputs: Explore inventory (labels, citations, table sources, overlaps, numbers verified against `results/` and the macros), micro-theorist assessment, and a drafting pass applying the narrativize rules and the humanizer checklist. Same procedure as 4.1 to 4.4.

## Context

`\subsection{Estimates}` (`sec:results`, `sections/04-structural-draft.tex`, lines ~551-781, ~2,500 words of prose plus ~850 in table and figure notes) is still the full-attention results section. The first two subsubsections present rho-hat, c_0-hat = beta-hat_1 e*-hat (2.4 and 3.5 percent), sigma-hat_0 and the wedge lambda-hat as the results; the attention model arrives only at line ~707 as "the alternative reading". Section 4.4 now leads with the attention objects, so 4.5 contradicts the paper's arc and, in places, its own tables. It is also the headline-results section, so order and claims matter most here.

## Assessment (what is wrong)

**Arc.** Current: structural estimates for the benchmark (rho, c_0 = beta_1 e*, sigma_0, lambda) -> attention as an extension. Right arc: silence sells above the full-attention ceiling; how much attention reached silent listings; what silence pays and who earns it (ordering, c_0 = Delta-hat, hiding rates, transfer, rho-hat as the scale); fit and limits; hand-over to Section 5.

**Tables.**
- `tab:attention` should lead: its body is generated (`results/tables/table_attention_body.tex`), but caption and notes are typed; the body says "core model" and uses C^def, C*_delta, C-bar^sil where the text uses zeta; notes say "Panel B is the comparison the table is built around" and "values are provisional". Reorder panels to A, C, B.
- `tab:did_results` is typed end to end (cells, N, notes), with its numbers also hard-coded as constants in `scripts/compute_attention.py` (parity assertions) and a second copy in the `A-robustness.tex` specification table (lines ~39 and ~45). Its notes still define c_0-hat = beta-hat_1 e*-hat and lambda-hat = Delta-hat - c_0-hat, and say lambda "is not folded into c_0-hat" (the opposite of 4.4 and Prop att_identification(iv)); the Panel B row "c_0 (hiding cost)" shows the full-attention 2.4/3.5; "no longer treated as an upper bound" is retraction wording. The Std column mixes ddof = 0 (Panels A and B) and ddof = 1 (Panel C) without saying so. `table_estimates.tex` (Sept 15) is a stale unused artefact.

**Stale or wrong statements.**
1. L600-601, 603-621, 655-659: 2.4/3.5 called "the identified hiding cost" and "within about a percentage point, set by the legal regime"; under c_0 = Delta-hat the figures are 8.5 and 3.9 (ratio 3.5 against the 2.4 benchmark). L771 says the opposite, so the section contradicts itself. Units: L656 says 0.024 log points where the table unit is percent; L687 and L700 mix units.
2. L645-653: "every market is Partial Pooling by construction". True only for the full-attention c_0. Under c_0 = Delta-hat the counts are apartments 25 cost-deterred / 20 complete adverse selection / 0 partial pooling, houses 45 / 11 / 41 (macros `attRaw*`; `attShareInBandApt` = 0).
3. L750 "the evidence is the contrast between segments": wrong. The apartment rejection is within-segment (zeta*_delta about 31 vs the rational pool cost about 244 kWh/m2/yr); what does not depend on the normalisation of psi's level is the perceived cost of silence, and it needs only zeta^def < zeta-bar^sil.
4. L750 "accounts for both the rejection in apartments and the fit in houses": overclaims. psi is just-identified from the aggregate; apartment slack is 0.90 with t about 1.0; 21 of 45 apartment markets exceed their own ceiling; in houses the identified interval is [0, 0.95] and silence sells above a verified efficient rating in 33 of 97 markets.
5. L627-629, 696-705: the hiding-rate ordering across segments is presented as a prediction. It is not: c_0 is higher in apartments and d sigma_0/d c_0 < 0; rating premium raises hiding (Prop att_cs). The `[AUTHOR]` flag at L702 is right (a thinner pool of hiders raises the premium).
6. L668-672: "truncating the post-reform window leaves both results standing (Appendix robustness)". The appendix has no such exhibit. The only evidence is a diagnostic (`quality_reports/diagnostics/rho-anchor-dynamics/OVERVIEW.md`, Sept 15, T = 10): the house wedge is 1.06 at one year (t = 2.82) and 0.63 at two years (t = 1.78), 0.43 only at the full window. "Both stand" is false for houses at one year. Drop the claim.
7. Three t-statistics for one null (lambda = 0 <=> psi = 1): 6.78 (L586), 6.8 and 6.9 (table panels). Report one (macro `attLamTApt`).
8. Window statements: price panel Oct 2018 - Jul 2024; structural moments pooled 2022-2024; Section 3 sample 2021Q3-2024Q4; `compute_attention.py` `SAMPLE_YEARS = 3.5` (comment "2021-07-01 to 2024-12-31") vs listings 2022-2024. State once in the table notes; flag the 3.5 constant (affects per-year counts in the policy section).
9. Hard-coded numbers that have macros: rho mean 49.5/45.8, "1 of 45 / 5 of 97", lambda 6.1/0.4 with t = 6.78/1.10, Delta/beta 8.5/4.1 and 3.9/5.8, sigma 15.2/6.8; no macros yet for pi, thetabar means, the table SDs, the all-market 81/114 means, or the 5.9/2.8 registry hiding rates.
10. Wrong pointers: L771 cites `sec:identification` for the 2.4 (it is only in the table) and `sec:results` for "transaction-cost benchmarks" (its own parent); L680 and L705 point at `ss:attention` (now The Model) where the estimates are meant; L663, L676 cite `lem:model_bounds` (a benchmark result) as "the model's over-identifying restriction"; the `tab:attention` note points the "attention ceiling" at the wrong section; `A-benchmark.tex:147` promises a regime-classification check in 4.5 that does not exist; `main.tex:71` and `:370` point at `ss:attention`.
11. "baseline" (L598 pre-period; L621, 653, 679 full-attention case), "core" (L762; table body; `scripts/make_attention_figures.py` legends and docstring; `compute_attention.py` row labels), "extension" (L680, 705, 710).
12. L771 "the paper's measure" is stronger than the Introduction ("not as a measured sanction"); the apartment value (8.5 log points) exceeds the whole notary bill the Introduction compares c_0 to.
13. Also: `A-robustness.tex` L190 and L258 still call beta-hat_1 e*-hat "the primary estimator" and say lambda is "not absorbed into c_0" (4.4 pass fixed two of these; check the rest).

**Overlaps.** rho mean, rho > 1 counts, c_0, lambda and Delta/beta numbers are repeated 3-4 times within 4.5 and again in 4.4 and the Introduction; the notary-fee comparison appears in 4.5 and the Introduction; selection-bias and Monte Carlo sentences repeat 4.4; the window-and-sample story repeats 4.4 and Section 3.

## Proposed structure

`\subsection{Estimates}` (`sec:results`) with four `\subsubsection`s; `tab:attention` leads.

| # | Part | Question it answers |
|---|---|---|
| 0 | Opening | What do the data say about attention, the hiding cost and the transfer? Takes over from 4.4's hand-over; states the window once (price panel Oct 2018 - Jul 2024, structural moments pooled 2022-2024). No table inventory opening. |
| 1 | Silence above the full-attention ceiling | Can full attention price silence? beta-hat_1 and Delta-hat, the ratio, 37 of 45 markets above the ceiling, `fig:att_belief`. |
| 2 | Attention to silence (`ss:att_estimates`) | How far below full attention is the apartment market? zeta*-hat_delta first (needs no normalisation, within-segment comparison with the rational pool cost), psi-hat as an upper bound under zeta^def = 0 with the identified set and selection bias in a clause, the test of psi = 1 through lambda-hat (macros), `fig:att_contrast`, one-sentence caveats (apartment slack not distinguishable from zero; houses fit only on average). |
| 3 | What silence pays | Where does each segment fall in Cor att_ordering, and what hiding cost does the premium imply? Ordering reading; c_0 = Delta-hat as the cost Partial Pooling implies for the marginal hider, the full-attention 2.4/3.5 in one clause with a pointer to `app:c0_fullattention`; sigma-hat_0 with the 5.9/2.8 registry-reading in a clause; the uninformed sellers' rent; the behavioural transfer lambda-hat; rho-hat as the scale (mean and count above one via macros); the cost is large against transaction-cost benchmarks and is read as what the premium implies, not as a measured sanction. |
| 4 | Fit and limits | How well does it fit market by market? `fig:att_fit`, the dispersion admission, appendix pointers; hand-over to Section 5 naming its three inputs (b = rho-hat beta-hat_1, c_0-hat = Delta-hat, psi-hat). |

## What moves, what is cut, and tables

| Item | Action |
|---|---|
| rho-hat dispersion; "every market Partial Pooling by construction" (L631-653) | One core sentence; text moves to `app:c0_fullattention` (it describes the full-attention reading) |
| Wedge and `lem:model_bounds` paragraphs (L661-683) | Delete from core; already in `app:c0_fullattention` |
| Speculative explanation of why houses carry a larger premium (L685-694) | One clause ("we do not test why") |
| Estimator properties and selection-bias numbers (L710) | One clause; detail stays in `app:att_estimator` |
| Three qualifications and year-split (L775-778) | New A-attention subsection `app:att_qualifications` (estimator dependence, G-band valuation, year-by-year 1 - psi-hat, "too imprecise to interpret"); one sentence in the core |
| Market-count sentences (L766-767), seller-payoff sentences | To the `fig:att_belief` note, `app:att_band_fit`, `app:att_payoffs` |
| Window-truncation sentences (L668-672) | Cut (unsourced; diagnostic contradicts it for houses) |
| Comparative-statics causal clause (L700-702) | Cut; state that cross-segment hiding rates are not a prediction of the model |
| `tab:did_results` | Cut to inputs: pi-hat, thetabar-hat, sigma-hat_0, rho-hat, count rho-hat > 1; remove the c_0-hat = beta-hat_1 e*-hat and lambda rows (reported in `app:c0_fullattention`); rewrite the notes (window, filters and N, population-vs-sample SD convention, rho not clipped). Make every cell a macro (add the missing macros in `compute_attention.py`; diff must show only new macro lines; the `A-robustness.tex` typed copy then points to the same macros) |
| `tab:attention` | Reorder panels A, C, B; rename "core" to "full-attention benchmark" and C -> zeta in the generated body (`compute_attention.py`); drop "Panel B is the comparison the table is built around" and "provisional"; fix the section pointer in the notes |
| Figure legends and docstring ("core") in `scripts/make_attention_figures.py` | Rename "core" to "full-attention benchmark" and regenerate (routed through the `pyplot-specialist` agent per the visual-polish rule); no data change |

## Cross-references

- Labels that must survive: `sec:results` (A-benchmark:147, 4.3 forward refs), `ss:att_estimates` (4.3, 4.4, A-attention:248, main.tex:71), `tab:did_results` (03-setting:248, 4.4, A-robustness:258), `tab:attention` (4.4, A-attention:445), `fig:att_belief`, `fig:att_contrast`, `fig:att_fit`.
- New: `app:att_qualifications` (A-attention), subsubsection labels.
- Fix pointers: `ss:attention` -> `ss:att_estimates` where estimates are meant (L680, L705); `main.tex:71` and `:370` (check context); remove `lem:model_bounds` as "the model's restriction"; the `A-benchmark.tex:147` promise (state that regimes are classified under the paper's own c_0 or drop the promise); `A-robustness.tex:258` diagnostics pointer; the retained "transaction-cost benchmarks" pointer.
- Introduction findings paragraph and abstract already quote macros; check they stay consistent with Part 3 (apartment c_0 = 8.5).

## Transition logic (drafted wording; author owns the `[AUTHOR REWRITE]` paragraphs)

- Opening: "Section 4.4 left the size of attention, of the hiding cost and of the behavioural transfer to the data. This section reports them."
- Part 1: "A fully attentive buyer values a silent listing at a belief in [0,1] times the energy-efficiency premium, so silence cannot sell above a verified efficient rating... Full attention cannot price silence in apartments. How much attention reached the silent listings is the next question."
- Part 2: "How far below full attention is the apartment market?"; Part 3: "Given that attention, where does each segment fall in Corollary 4.x, and what hiding cost does the premium imply?"; Part 4: "The model is estimated on aggregates, so the remaining question is how well it fits market by market."
- Close: "Section 5 takes three objects from these estimates: the effective benefit of a rating b, the hiding cost c_0 = Delta-hat, and the attention parameter psi-hat."
Drafted rewrites exist for the rejection paragraph, the fit paragraph and the ordering paragraph (all numbers as macros); they correct claims 3-5 above. Style: no signposts that announce what follows, at most one em-dash per paragraph, no "not X but Y".

## Execution (after approval; compile after every step)

1. Back up files, scripts and results tables. Add macros for the table inputs (pi, thetabar means, SDs, the 5.9/2.8 registry hiding rates if derivable) and regenerate; diff shows only new macro lines; compile.
2. Rename "core" to "full-attention benchmark" and C -> zeta in `compute_attention.py` row labels, regenerate the generated table body; figure legends via `pyplot-specialist`; compile.
3. Add `app:att_qualifications` and move the cut material to its appendix homes; compile.
4. Rebuild 4.5 in the new order; replace the two tables; fix pointers and the `A-benchmark`/`A-robustness` leftovers; compile twice.
5. Fresh micro-theorist check of 4.5, the tables and the appendix homes; apply findings.
6. `/narrativize` on 4.5, then the humanizer in advisory mode; apply what you approve.
7. Grep all moved/renamed labels; `latexmk` twice; zero undefined and zero multiply defined labels. Update the session log. No commit until asked.

## Verification

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex`: no undefined references or duplicate labels; page count noted.
- Every number in 4.5 is a macro that equals the previously typed value (or a stated correction); the regenerated macro file differs only by new lines; `tab:did_results` cells equal the old typed cells.
- Reader test: each symbol in 4.5 defined or glossed at first use; units consistent (percent vs log points) across table and text.
- Independent fenced read of 4.5 (neutral copy) per `review-fencing.md`.

## Decisions and flags for the author

- Confirm the four-part arc with `tab:attention` leading and `tab:did_results` cut to inputs (recommended), versus keeping the benchmark estimates as a first part.
- Confirm making `tab:did_results` macro-driven (adds macros and a script edit) versus leaving it typed.
- Confirm cutting the window-truncation claim and the comparative-statics cross-segment claim (both unsupported); the house wedge is 1.06 (t = 2.82) at one year.
- Apartment hiding cost 8.5 log points exceeds the notary bill the Introduction compares to 2.4 percent. How to phrase it in Part 3 and in the Introduction ("what the premium implies, not a measured sanction" is drafted)?
- `SAMPLE_YEARS = 3.5` in `compute_attention.py` vs listings 2022-2024 (3.0 years): leave or correct (affects per-year counts in the policy section)?
- The `A-robustness.tex` specification table repeats the typed Panel B/C values; point it at macros too?
- The drafted paragraphs guess some macro names (for instance `attNDgtBHouse`); I will check each before use.
- The `[AUTHOR REWRITE]` paragraphs and the `[AUTHOR]` G3 comments are yours; my drafts are a starting point.
