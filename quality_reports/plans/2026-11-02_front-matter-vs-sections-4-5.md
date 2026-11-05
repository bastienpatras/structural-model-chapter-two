# Plan: align abstract, Introduction and Conclusion with the revised Sections 4-5

Status: APPROVED by the user ("yes please", 2026-11-02). Branch `sections-4-5`. No commit.

## Scope
`main.tex` abstract (L44) and Conclusion (L339-354); `sections/01-introduction-draft.tex` (whole, in particular L113-131, L134-153, L166-197).
Section 5 is not re-edited here except where front matter and Section 5 disagree and Section 5 is the one that is wrong.

## Known stale items (from the status check)
1. Intro L116-117: "6.9\% ... 3.4\%" in percent; abstract and conclusion use log points.
2. Intro L141: "it nests the classical benchmark" / "intermediate values ... partial pooling" vs Section 4 (regime imposed by the calibration, in-band shares 0% / 11%).
3. Intro L186-197 and Conclusion L349-351: "light benchmark", programme cost and percent of MaPrimeRenov' budget, "audit investment scales how many sellers are reached"; Section 5 now treats the subsidies as lower bounds with selection biasing them down, the programme-cost share as a bill and not a budget, and the salience bound as a bound.
4. Conclusion repeats the three findings already in the abstract, Introduction and the Section 4 closer.
5. Conclusion L348 "strategic hiding is uncommon" uses the hiding-rate pair that is still an open decision (baseline vs registry vs macros).
6. `[AUTHOR REWRITE]` paragraphs: Intro L148, L179, L190; Conclusion L344, L347, L350, L353 are suggestions only, except sentences already edited at the user's yes.

## Procedure
1. Micro-theorist read, fenced: neutral copy of the sources outside the checkout, no plan or prior reviews. Own reading first, then the checklist above.
2. Apply mechanical and numerical fixes (macros, units, labels), compile after each batch.
3. Wording fixes from the findings; marked paragraphs get suggestions only.
4. /narrativize on Introduction and Conclusion, then humanizer in advisory mode; suggestions listed, applied only on the user's yes.
5. `latexmk` twice; zero undefined and multiply defined labels; page count; session log updated.

## Open decisions not settled here
Canonical hiding-rate pair; M9; M10; D1-D6; notary-fee and MaPrimeRenov budget sources.
