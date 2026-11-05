# Plan: abstract v3, puzzle first, then the policy question, then the two-component resolution

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Copy to `quality_reports/plans/2026-11-03_abstract-v3-puzzle-first.md` on approval. No commit.
Supersedes the 2026-11-03 abstract-rework plan (executed; that version had the empirical result first, then the policy result). Open items stay open at the user's request (hiding-rate pair, 4.4 vs 6.9 wording, D1-D6, [CHECK] sources).

## Request
Rework the abstract (`main.tex`, the `\abs{...}` block, about 190 words now) in this order: (1) the puzzle; (2) the policy question; (3) how the puzzle is resolved, with two theoretical components, limited attention to silence, and uninformed sellers with heterogeneous buyers; (4) the design, and that we formally build a model to study the relative efficiency of the renovation scheme in France; then the policy result with its hedges. Then the same procedure as before: fenced micro-theorist check, narrativize, advisory humanizer (suggestions only, applied on the user's yes).

## Micro-theorist assessment (done, read-only, repo copy, no earlier reviews read)
- **Two-component split.** The body supports this split: (i) the classical departures, uninformed sellers who shelter hiders plus heterogeneous buyers (only a share price a displayed rating), explain why silence sells above a poor rating; (ii) limited attention explains why, in apartments, silence also sells above a good one. Houses need no attention component (full attention not rejected, t=1.10). This is the user's reading, "limited attention to silence" as one component and "uninformed sellers with heterogeneous buyers" as the other, and it is the one recommended. The alternative (pairing uninformed sellers with attention as "how silence is read") is defensible but hides that houses need no attention component.
- **"Relative efficiency of the renovation scheme" is the one phrase the paper cannot carry.** S* is an incentive-compatibility object, a lower bound outside the regime the calibration imposes, and not a welfare optimum (Section 5.2 remark: no social value or cost of funds is valued). The paper never models MaPrimeRenov's actual eligibility or rate schedule and has no take-up data; the bill figures are a one-platform scale comparison. What it supports: "what subsidy sellers need to renovate rather than hide, and how closely a subsidy uniform across markets fits that need". The abstract will use this wording, and the Introduction (L195) and Conclusion (L351) phrase "Efficient targeting requires/must condition" should become "matching subsidies to need requires" for consistency (decision below).
- **Keep out of the abstract:** psi levels, the closed-form premium, the bill, the 8.5/3.9 and 4.4/3.7 figures, the law name for opposability.
- **Body inconsistencies found (not caused by the abstract):** Section 3 L131 credits opposability to the loi Climat et Resilience, the Introduction footnote credits the ELAN law; silent-uninformed share 83%/89% (Section 3 L219) vs 95%/98% (Section 4 L27); the Conclusion's "None of the three suffices alone" (main.tex L343) contradicts Section 4 L415 (uninformed cover alone puts silence between the bad-news price and the good-rating price).

## Recommended text (B, about 215 words after the plain-language opening; the cheapest cuts are 'averaged across markets' and the last clause 'so no flat grant fits every market')
> Disclosure theory predicts that buyers read silence as bad news, so listings with no rating should sell below disclosed poor ones. Yet after July 2021, when disclosed energy ratings became legally opposable in France, listings with no rating gained 6.9 log points (apartments) and 3.4 (houses) on disclosed inefficient ones, averaged across markets. What subsidy makes a seller renovate rather than hide, and how closely does a uniform grant fit it? Two components resolve the puzzle. Uninformed sellers, most of the silent, shelter hiders and lift silence above a poor rating; only a share of buyers price a displayed rating, shrinking the reward to disclosure. Limited attention lifts it above a good one in apartments, where, unlike houses, full attention is rejected and buyers price silence well below its registry energy cost. Matching SeLoger listings to the ADEME certified-audit registry reveals each seller's information status, normally unobservable; we build a disclosure game to study renovation subsidies. With one hiding cost per market, the subsidy needed is at least the renovation cost less the verified-efficiency premium, equal in the regime our calibration imposes, which the data do not confirm. At an illustrative EUR 250 per square metre this bound averages about half the cost and varies with local prices, so no flat grant fits every market.

Wording rule (user, 2026-11-03): the word 'unraveling' does not appear in the abstract; the prediction is stated in plain words. 'Contrary to unraveling' style phrases elsewhere in the abstract are removed.

Edits I would make while placing it: write the euro sign as `\euro{}250`; "Two components resolve the puzzle" -> keep; "the subsidy needed" -> "the minimum subsidy" only if the lower-bound reading stays clear; keep the `% [AUTHOR REWRITE]` marker. Candidates A (policy question as "need vs uniform", attention paired with uninformed sellers) and C ("how buyers read silence / how they value a rating") are the alternatives.

Claims it relies on (body lines): 6.9/3.4 all-market averages (Intro L116-117, Table 6 notes); opposability (Section 3 L37, Intro footnote L24-33); uninformed sellers shelter hiders (Section 3 L219, Section 4 L415); share of buyers pricing a displayed rating = rho*omega_1 (Intro L151); attention needed only for the apartment inversion (Section 4 L19-29); apartments reject full attention, houses do not (Section 4.5); well below registry cost (31 vs 244 kWh, Section 4 L590, CI wide); one hiding cost per market (main.tex L74); lower bound, equality only in the imposed regime (main.tex L147-169); about half at EUR 250 (main.tex L217); varies with local prices (L221).

## Execution
1. Backup `main.tex` to the scratchpad; replace the abstract block only.
2. Compile twice; zero undefined/duplicate labels; word count 170-215; abstract on the title page.
3. Fresh micro-theorist check of the new abstract, fenced (neutral copy outside the checkout, no plan or prior verdicts); apply findings.
4. Narrativize and advisory humanizer on the new abstract; suggestions listed to the user, applied only on yes.
5. If approved below: fix the three body inconsistencies and the "Efficient targeting" phrase in the Introduction and Conclusion; compile; session log.

## Verification
`cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex` twice, clean; every number in the abstract traces to a body line above; the abstract makes no efficiency or welfare claim.

## Decisions for the author
- Opening B (recommended), A, or C.
- Fix the three body inconsistencies and the "Efficient targeting" wording now (recommended: yes, small wording edits) or leave them with the other open items.
- Keep "relative efficiency" out of the abstract in favour of "how closely a uniform grant fits what sellers need" (recommended), or keep the word and accept the referee risk.
