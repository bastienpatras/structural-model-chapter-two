# Plan: restructure Section 4.1 Motivation (and 4.1.1)

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Nothing edited yet.
First of four section-level passes (4.1, 4.4, 4.5, then Section 4 as a whole). Inputs: Explore inventory (labels, citations, paragraph map, overlaps, stale claims), micro-theorist assessment, and a drafting pass applying the narrativize rules and the humanizer checklist. Same procedure as 4.2 and 4.3.

## Context

`\section{A Structural Interpretation}` (`sec:model`) opens with `\subsection{Motivation}` (`ss:model_motivation`, ~680 words) and `\subsubsection{Silence Priced Above a Verified Efficient Rating}` (`ss:att_motivation`, ~850 words), in `paper-real-estate/sections/04-structural-draft.tex` (lines ~10-88). The text still motivates the full-attention model: it says the facts line up with Dye-Jung-Kwon, and the puzzle that justifies attention only arrives in 4.1.1. The two heading levels are inverted, much of 4.1 repeats the Introduction, Section 2 and Section 3, and several claims are stale or wrong. Goal: the reader is led from the puzzle left by Sections 2-3, through why beliefs cannot solve it, to why attention can, into 4.2 The Model.

## Assessment (what is wrong)

**Order and role.** Motivation should state the puzzle, show beliefs cannot solve it, argue attention can, and hand over. Current order: positioning of Dye-Jung-Kwon (L16-26), scope (L28-30), "facts line up with DJK" (L32-38), timing test (L40-47), Figure 1 cell (L49-56), caveats (L58-69), then, in 4.1.1, the puzzle (L75), the answer as a one-sentence stub (L77), rival amendments (L79), literature (L82), French features (L84-85), three-step mechanism (L87).

**Stale or wrong statements.**
1. L62-65: sigma_1* = 0 is called "maintained... an assumption and not a result"; it is a result outside Complete Adverse Selection (Cor att_hq).
2. L65-68: "we maintain rho-hat = 1 and treat c_0-hat as an upper bound" predates the anchored estimator (rho-hat identified, mean about 49.5 percent) and the paper now takes c_0-hat = Delta-hat.
3. L54-55: "EPC-sensitive share approaches one" contradicts the estimates.
4. L55-56: "incomplete coverage alone sustains the premium; France satisfies only one condition" is false in the current model: coverage alone gives 0 < Delta* < b, and most of the apartment premium comes from inattention.
5. L40-47: the timing test says a supply-side shift "would move the two gaps by different amounts... neither is observed", but the two gaps did move by different amounts (8.5 vs 4.1); that is the wedge. "Identification is sharpest in apartments" is unsupported.
6. L30: "estimation determines whether concealment occurs" (sigma_0 is measured from the registry) and "admits full unravelling" (false for pi < 1).
7. L75-94: change vs level. The DiD shows the silent price rose more than the A-to-D price; reading it as silence selling above A-to-D needs assum:no_pre_pricing. "In most markets" is a count of changes (37 of 45), not levels.
8. L79: the cursedness numbers (0.1 of 6.1) mix lambda-hat (6.1) with 8.5 - 4.1 = 4.4; two different "unexplained" numbers. The structural bound (a cursed belief is thetabar < 1, so Delta <= rho*beta_1*thetabar < b) makes the numbers unnecessary.
9. L82: "the amendments share the premise" overstates (over-reaction and composition are not buyer-belief amendments).
10. L26: "K... to recover c_0" is no longer how c_0 is read (Delta-hat).
11. File-header comment (L2-3) says the benchmark is of 4.4; it is Appendix E.

**Redundancy.** DJK positioning duplicates Intro 8-9 and Section 2; the rental-ban threshold duplicates Section 3; the Figure 1 cell duplicates Section 2; the "model leaves unsettled" paragraph duplicates the Intro and 4.2/4.3; the attention literature duplicates Section 2 and Intro; the 2022 euro-bill rule duplicates Section 3 L51; the apartment wedge is restated at Intro 9, 3 (fifth requirement), 4.2 opening, 4.3 (twice) and 4.5.

**Use before definition.** rho, psi, pi, theta, K, c_0, sigma_1*, rho-hat, c_0-hat, "silent", "EPC-sensitive" are used before 4.2 (acceptable in a motivation except sigma_1*, rho-hat, c_0-hat). Five forward pointers: Prop att_seller_types, Cor att_hq, `sec:results`, `tab:did_results`, `app:robustness`. Circular chain today: Section 3's fifth requirement -> `ss:att_motivation` -> 4.5.

## Proposed structure

One flat `\subsection{Motivation}` (labels `ss:model_motivation` and `ss:att_motivation` both kept on it; the 4.1.1 heading is dropped; `sec:model` stays on the section). Four paragraphs:

| # | Paragraph | Question it answers |
|---|---|---|
| a | Puzzle | Which fact can the classical game not deliver? Unraveling breaks through uninformed sellers and buyer heterogeneity, but with full attention Delta* cannot exceed b whatever belief in [0,1]. The reform fact is referred back to Section 3 (new Fact 5). Level-vs-change caveat stated. |
| b | Beliefs cannot do it | Why not cursedness, distrust, over-reaction, composition? Structural bound instead of the cursedness numbers; composition left open and pointed to 4.4. |
| c | Attention can | Why is attention plausible here? One sentence of evidence (Chetty, Finkelstein, Brown, Allcott, Sallee, Gabaix) plus three French features (label and euro bill only on displayed listings from January 2022, collective heating, missing rating common). |
| d | Three steps | What would buyers have to do? Full, half, no attention on a silent listing; ends by saying the model formalises it: classical seller side, buyers attend with omega_1 to a rating and omega_0 <= omega_1 to silence. |

Handover into 4.2: the last sentence of (d). 4.2's opening paragraph is replaced so it opens on the modelling choice (valuation written as the energy cost subtracted) with no recap of the wedge.

## What moves or is cut

| Item | Action |
|---|---|
| Reform fact (D3/B3 shifts, 37/45, house reversal) | New Section 3 `\subsubsection` "Fact 5" (`ss:fact5`) with the level caveat; update the "four features"/"five requirements" counts at 03-setting-draft.tex L19, L125, L248 |
| Timing test (L40-47) | Moves to 4.4 "The Reform and Identification", rewritten: it rules out a common seller-mix shift moving both gaps equally in the same markets on the same date; it does not rule out unobserved composition (the open case) |
| "Why informed sellers withhold" caveat (L58-61) | Moves to 4.4 (one short paragraph; a valid pre-reform certificate left undisplayed is recorded as uninformed) |
| DJK positioning, rental-ban threshold, Figure 1 cell, "leaves unsettled" paragraph (stale items 1, 2, 3, 4, 6, 10) | Deleted; covered by Intro, Section 2, Section 3, 4.2/4.3 |
| Attention literature paragraph | One sentence in (c); Hirshleifer, DellaVigna stay in Section 2 and Intro |
| 2022 dated-test footnote with the `[CHECK]` comment | Footnote kept in (c) as is; the prediction ("gap widens again at that date") is flagged for 4.5/`app:robustness` |
| `\attCursedApt`, `\attLamApt` in 4.1 | Dropped from 4.1 if the structural bound is used (check other uses before deleting; macros stay defined) |

## Cross-references

- Labels that must survive: `sec:model` (main.tex:71, :370), `ss:att_motivation` (03-setting:248, 4.2, 4.3 L447/L478), `ss:model_motivation` (uncited, kept).
- New labels: `ss:fact5` in Section 3 (check that `ss:institutions` and `sec:data` exist for the Fact 5 pointers).
- Prose references "Section 4.1.1" (if any) must become "Section 4.1" or a `\ref`; grep after the change.
- Fact 5 forward-references `tab:did_results` in Section 4 (acceptable; flagged).
- The contribution claim the old 4.1 opening carried (closed-form premium = c_0 in Partial Pooling, Prop att_seller_types) is not stated in the Introduction; add one sentence there (author to confirm).

## Transition logic (drafted wording; the paragraphs tagged `[AUTHOR REWRITE]` at L74 and L81 are yours)

Opening of (a): "Section 3 documents that silence about energy performance sells above a displayed inefficient rating. Classical disclosure theory delivers part of this." Then the bound, then the apartment result with its macros. (b): "Revising the belief cannot close the gap, because every amendment replaces the Bayesian posterior with another number in [0,1] and the bound holds for all of them." (c): "Limited attention can generate the wedge." (d): "The mechanism is easiest to see in three steps... The model below formalises this." Style: no signposts announcing what follows, at most one em-dash per paragraph, no "not X but Y".

## Execution (after approval; compile after every step)

1. Back up the three files (04-structural, 03-setting, main.tex if touched). Add Fact 5 to Section 3, update counts; compile.
2. Add the rewritten timing test and the "why withhold" paragraph to 4.4; compile.
3. Rebuild 4.1 as the flat four-paragraph Motivation; replace the 4.2 opening paragraph; fix the header comment; compile.
4. Fresh micro-theorist check of 4.1, the new Fact 5, the 4.4 additions and the 4.2 opening (ordering, soundness, level-vs-change claim, overlaps, links); apply findings.
5. `/narrativize` on 4.1, then the humanizer in advisory mode; apply what you approve.
6. Grep every `\ref` to moved/renamed labels and "4.1.1"; `latexmk` twice; zero undefined or multiply defined labels.
7. Update the session log. No commit until asked.

## Verification

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex`: no undefined references or duplicate labels; page count noted.
- All macros resolve; numbers unchanged (only the placement of the reform fact moves).
- Reader test: every symbol in 4.1 is either defined or glossed at first use.
- Independent fenced read of 4.1 and the new Fact 5 (neutral copy) per `review-fencing.md`.

## Decisions and flags for the author

- Confirm the flat structure (recommended) and moving the reform fact to Section 3 as Fact 5.
- Confirm the level-vs-change wording: the change comparison is observed; reading it as levels needs `assum:no_pre_pricing`. A referee may note that Fact 1 shows silent listings above efficient ones in raw pre-reform apartment levels, which sits uneasily with that assumption.
- Strict vs weak bound: drafted as "cannot exceed" b; check against the incentives proposition.
- The share of silent apartment listings without a certificate is 95 percent in 4.1.1 (`\attShareUninfApt`), about five-sixths in Section 3 and 83 percent in the Introduction; the paper never says how they relate (different bases or samples). Decide which to quote in (c).
- Add the closed-form-premium contribution sentence to the Introduction?
- The drafted transitions are a starting point; you rewrite the `[AUTHOR REWRITE]` paragraphs.
