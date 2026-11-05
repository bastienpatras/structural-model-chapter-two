# Plan: rework the abstract (policy result and originality of the design, shorter)

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Copy to `quality_reports/plans/2026-11-03_abstract-rework.md` on approval. No commit.
Supersedes the 2026-11-02 table-6/Section-5 plan (done). The open items (hiding-rate pair, 4.4 vs 6.9 wording, D1-D6, [CHECK] sources) stay open at the user's request.

## Context
The abstract (`main.tex` L44-45) is about 330 words and leads with the unraveling puzzle and the attention estimates. The user wants it shorter (target 150-180 words), centred on the policy result and on what is original about the design (private listings matched to the certified-audit registry, which shows each seller's information status).

## Micro-theorist assessment (done, read-only, repo copy, no prior reviews read)
- Overstatements in the current text: "the puzzle resolves because non-disclosure pools ..." (Section 4.1 says pooling explains only part and cannot produce the apartment inversion); the closed-form "premium = hiding cost whatever the composition" reads as a tested result though c0 is calibrated to make it hold; "contrast holds for any non-negative default common to the two segments" is derivable but not stated in the body; "raising attention to silence leaves the minimum subsidy unchanged" conflicts with Section 5.7 ("follows from the single hiding cost, not a finding"); "2021 enforcement of disclosure" mislabels the reform (the certificate became legally opposable).
- Cut: psi levels and their hedges, the closed form, the "buyers treat silence as ambiguous" line, the salience sentence, the bill figures (a one-platform scale comparison needing 25 words of hedging; they stay in the Introduction).
- Carried hedges (load-bearing only): one hiding cost per market; the regime is imposed by the calibration so the subsidy is a lower bound.

## Recommended text (A', policy first, design in sentence 2; 180 words)
> What must a subsidy pay a seller to renovate rather than hide a poor energy rating? We answer it in France, where private SeLoger listings matched to the ADEME certified-audit registry reveal each seller's information status, normally unobservable: whether the seller holds a certificate and whether she shows it. After the 2021 reform made certificates legally binding, listings with no rating gained 6.9 log points (apartments) and 3.4 (houses) on disclosed inefficient ones, contrary to unraveling; most silent sellers hold no certificate on record, and apartment buyers price silence at a small fraction of its registry energy cost. In a structurally estimated disclosure game with one hiding cost per market, the minimum incentive-compatible subsidy is the renovation cost less the premium for a verified efficient rating, invariant to enforcement against hiding and to audit coverage, which changes only how many sellers it reaches. Our calibration imposes this regime; in any regime the subsidy is a lower bound. Required cost shares average about half of a light retrofit and vary widely across markets, so a uniform national programme is poorly targeted.

Alternatives held in reserve (micro-theorist drafts): B opens on the design ("Disclosure studies rarely observe what sellers know"), C opens on the unraveling puzzle. I recommend A' because the user asked for the policy result first; B is the better choice if you want the design to carry the opening.

Numbers and sources: 6.9/3.4 (`tab:attention` notes, all-market averages); "about half" = `\attBaseCostShareTwoFiftyApt` 53 and `...House` 56 at the light benchmark (Section 5.5); "most silent sellers hold no certificate on record" = `\attShareUninfApt` 95 (Section 4.1; houses about 89%); "small fraction" = perceived 31 kWh [-31, 89] vs registry 244 (Section 4.5), deliberately not tightened because of the CI.

## Execution
1. Backup `main.tex` to the scratchpad; replace the abstract paragraph (L44-45) only. The `% [AUTHOR REWRITE]` marker is kept on the paragraph.
2. Compile twice (`latexmk`); abstract fits on the title page; zero undefined/duplicate labels; word count reported.
3. Fresh micro-theorist check of the new abstract against Sections 4-5, fenced (neutral copy outside the checkout, no plan or prior verdicts); apply findings.
4. Narrativize and advisory humanizer on the new abstract; suggestions listed, applied only on your yes.
5. Align the other front matter only where it now contradicts the abstract (the Introduction ¶9/¶12.5 and Conclusion already say the same; no edits expected). Session log updated.

## Verification
- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex` twice, clean.
- Every number in the abstract traces to a macro or a table note above; none typed except 6.9/3.4, which the Introduction and Conclusion already state.
- Word count 150-185.

## Decisions for the author
- A' (recommended) vs B or C as the opening.
- Whether the bill (EUR 0.44-1.72 bn) belongs in the abstract (recommended: no).
- Whether to drop the attention estimate entirely from the abstract (recommended: keep only the apartment-pricing clause; psi levels move to the Introduction).
