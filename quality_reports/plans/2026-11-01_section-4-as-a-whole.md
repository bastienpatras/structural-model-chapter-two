# Plan: Section 4 as a whole (frame, consistency, front-matter alignment)

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Copy of this plan to `quality_reports/plans/2026-11-01_section-4-as-a-whole.md` on approval.
Inputs: Explore structural inventory; micro-theorist whole-section assessment (read-only, first read). The five subsections (4.1 to 4.5) have each been restructured and checked. This pass adds the frame, aligns names and numbers across sections, and updates the front matter that still describes the old full-attention test.

## Context

The five subsections chain correctly (each closes into the next). Three things break the whole: no section-level opening, a closing bridge buried inside 4.5, and front matter (abstract, Introduction paragraph 9, conclusion) that still reports a test the section no longer runs. Numbers also conflict across sections (informed hiding rate, hiding cost).

## A. Section frame (new text, drafted by the micro-theorist; yours to rewrite)

1. **Opening** before `\subsection{Motivation}` (`04:13`): one paragraph with the question, the model's two jobs (decompose two price gaps into attention and hiding cost; supply Section 5's counterfactual structure) and a one-sentence roadmap; Appendix E as the full-attention special case, not a rival model.
2. **Closing bridge** as a separate last paragraph (replacing `04:652`): three results carried to Section 5 (full attention to silence rejected in apartments and not in houses; average hiding cost 8.5 and 3.9 log points, calibrated, not a measured sanction; the efficiency premium identified from prices, only its split needing the anchor), then the policy question. Drop "equivalently rho-hat beta-hat^anchor" (true by construction).
3. Trim `04:19` to one sentence pointing to Fact 5 (`03:246-249` already says it); keep the "no belief above b" bound at `04:17`, `04:246` and Corollary att_ordering, turn the other ~5 statements into cross-references.

## B. Front matter and cross-section numbers

4. **Abstract** (`main.tex:44`): replace the full-attention test sentences. Say what is rejected (full attention to silence, psi_delta=1, t=6.9 apartments), keep "6.9/3.4" labelled as log points on the full sample, drop "does not depend on the normalisation" unless restricted to a default common to both segments (house identified interval is [0, 0.95]).
5. **Introduction paragraph 9** (`01:147-170`) and **`main.tex:370`** (conclusion): rewrite as one specification test plus three magnitudes (attention to silence, hiding cost, scale of attention), the benchmark 2.4/3.5 appearing only as the "had silent listings been read as carefully as rated ones" counterfactual. Fix the stale "sensitivity and concealment cost identified only as a product" (the non-identified pair is rho and beta_1), "8.5% of property value" (8.5 log points is about 8.9%), and the "essentially unchanged under registry sigma_1" claim (that table reports rho-hat and the full-attention cost, not psi-hat).
6. **Broken sentence** `01:199`: the `% [AUTHOR REWRITE]` marker comments out the start of a sentence; move the marker to its own line.
7. **Informed hiding rate**: Section 3 (`03:98`) quotes 6.9/2.7 pooled and 7.7/3.7; `tab:did_results` 15.2/6.8; `tab:robustness` and 4.5 5.9/2.8 (macros `attSigmaRegMean` give 5.8/2.7); `A-attention:264` 8.0/2.9. Make Section 3 quote the baseline macros, state weighting (pooled vs market mean) in each place, and align `A-attention:264`, `tab:robustness` and 4.5's typed 5.9/2.8 with the macros or relabel them. Needs your call on which pair is canonical.
8. `03:118` says the cost "does not use sigma-hat": correct (it uses sigma-hat through the registry belief). One sample-window rationale for 2H2021 (`04:461` vs `03:118-119`).

## C. Notation and wording

9. **psi**: after `04:510` add "Under Assumption no_pre_pricing, psi_delta = psi; we write psi-hat from here on"; drop "spillover" except at definition; remove psi_delta from `04:455`.
10. **"Wedge"** names two objects: say "apartment inversion" for silence above a verified efficient rating, keep "attention wedge lambda" for the DiD wedge.
11. **"Normalisation"**: keep it for omega_1=1; call zeta^def=0 "the zero-default assumption" everywhere (`04:455, 510, 523, 530, 532, 588, 598`).
12. **b vs beta_1**: state once at `04:223` that beta-hat_{1,m} estimates b_m (not beta_1), or rename to b-hat in tables; one hat convention.
13. **Attention ceiling**: name it where derived (`04:534`), fix the table note to eta_m beta-hat_{1,m}.
14. **Effective belief**: `04:418` promises it in 4.5 and it is never reported; add it to `tab:attention` panel A (macros `attRatioApt` 2.10, `attRatioHouse` 0.67 exist).
15. **c_0**: one definition (`04:600`); `04:455` says "Section 4.5 calibrates c_0"; `main.tex:71` uses `attCzeroFit*`, check it equals `attDthree*`.
16. Report one t-statistic for the same null (6.9 vs 6.78); put lambda-hat with its t in `tab:attention` panel B. Comment out or resolve `[CHECK: source]` at `04:600` before circulation.
17. Appendix positioning: relabel the "baseline" column of `tab:robustness` as the full-attention cost; reword `04:350` ("regimes of the benchmark reappear") and `04:310` (D/E crossing) so a reader does not need Appendix E first. A-benchmark itself stays.
18. Redundancy: merge the first two readings of lambda (`04:515`, `04:530`); say "zero residual by construction" once in the table note and once in `04:613`; keep selection-bias at `04:588`.

## D. Referee-risk points: decisions for you (I will not change content for these)

These are substantive and touch identification, so they return to the author. I will only add wording if you say how.
1. **List price vs transaction**: the DPE is appended to the sales agreement, so why does silence carry a premium at the listing stage? Needs evidence (time on market, transaction prices) or an explicit listing-stage attention argument.
2. **Selection**: on the full sample Delta/beta_1 is about 4.1, above the ceiling eta of about 2.3; selecting on beta-hat_1 > 0 brings the aggregate inside the admissible region, and 21 of 45 markets still exceed their own ceiling with psi's interval including 0. The text frames selection only as biasing psi toward one. Say it plainly.
3. **Reform-date confounds**: the March 2021 DPE methodology change, the January 2022 advertising mandate (against "c_0 unchanged"), valid pre-reform certificates counted as uninformed. The micro-theorist also believes the energy class has been mandatory in sale advertisements since 2011; that is unverified, check Legifrance.
4. **c_0 is a calibration** (0% of apartment markets inside their own band; R-squared 0.14): call it a one-parameter decomposition plus calibration, or allow within-market heterogeneity in c_0.
5. **The model's own prediction undercuts a pre-trend argument**: the flat silent share is cited against supply shifts (`04:489`), while the model predicts the reform raised it by roughly 3 pp.
6. **Announced January 2022 test** is not run; run it or drop the claim. **zeta^def=0** carries the point estimate and has no housing evidence.

## E. Execution (after approval; compile after each step)

1. Back up `04-structural-draft.tex`, `01-introduction-draft.tex`, `03-setting-draft.tex`, `main.tex`, `A-robustness.tex`, `A-attention.tex`, results tables.
2. Items 6, 9 to 16 (mechanical, one-token or one-sentence) in small batches; grep for each renamed term before and after; compile.
3. Items 1 to 5, 8, 17, 18 (new paragraphs and front-matter rewrites) from the drafted text, then fresh micro-theorist check of the whole section plus Introduction and abstract.
4. `/narrativize` then advisory humanizer on the new frame, abstract and Introduction paragraph; apply only what you approve.
5. Item 7 after you pick the canonical hiding-rate pair; regenerate tables if macros change.
6. Two `latexmk` runs, zero undefined or multiply defined labels, page count noted; session log updated. No commit.

## Verification

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex` twice: no undefined or duplicate labels.
- grep: no "spillover" outside the definition, no zeta^def "normalisation", no "benchmark" in the Section 4 frame text, `2.4`/`attCzeroBase` only as the counterfactual.
- Every number in the new frame, abstract and Introduction is a macro matching `attention_macros.tex`.
- Independent fenced read (neutral copy outside the checkout) of the section opening, closing and Introduction paragraph.

## Decisions for the author

- Apply A, B and C as drafted (recommended), starting with the mechanical items?
- Canonical informed hiding rate: baseline (15.2/6.8), registry reading (5.9/2.8 or macros 5.8/2.7), or both with labels?
- Section D: which of the six referee-risk points do you want addressed in the text now, and which stay as a to-do list?
- Extend the pass to `main.tex:370` conclusion (recommended, same stale framing)?
