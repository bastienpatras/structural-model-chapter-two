# Diagnosis: `paper/main_concise.tex` against RE/finance conventions

Run 2026-08-11 against the conventions in
`skills/realestate-finance-writing/`. Whole-paper structural pass plus a
paragraph-level pass on the introduction. Section-level passes come later, one at a time.

## Verdict in one line

The paper is intellectually well positioned for this audience — it is *already* a
Grossman/Milgrom-anchored disclosure paper with a hand-built information-status measure,
which is exactly what the corpus rewards. What reads as foreign is the **architecture and
the front matter**, not the content.

## Whole-paper structural checklist

| Check | Result |
|---|---|
| Section count ≤ 7 | ✗ **9 sections** + appendix |
| Data positioned before the analysis | ✗ **§5 Data** sits after §3 Model and §4 Equilibrium Analysis |
| No standalone Results section | ✗ **§7 Results** exists |
| No standalone literature review | ✓ none — related work is in the introduction |
| A conceptual §2 exists | ✗ **missing** — §2 is Setting and Stylized Facts |
| No roadmap paragraph | ✗ present, and long (`main_concise.tex` ~line 68) |
| No notation in the introduction | ✗ one instance — `$K$` |
| Theory's assumptions enumerated | ✗ discussed in prose across two paragraphs, never enumerated |
| Scope disclaimer present | ✗ **absent** — and see the ρ̂ note below |
| Introduction closes on generalizability | ✗ closes on the roadmap |
| Descriptive findings enumerated in the introduction | ✗ the four stylized facts are deferred to §2 |
| Nested-model fit comparison | ⚠ **not yet checked** in the body |
| Every proposition has an economic gloss + testable implication | ⚠ **not yet checked** — 9 propositions/corollaries in the appendix |

## Two factual issues found en route

Neither is about style. Both need your judgement, not mine.

**1. Unit inconsistency, abstract vs. body.** The abstract says the premium is *"7
percentage points"*; the introduction and conclusion both say *"7 log points"* for what
appears to be the same statistic. Same number, two different units. One of them is wrong.

**2. The headline number may not be the paper's own number.** The abstract, introduction, and
conclusion all headline **7 log points (apartments) / 3 (houses)**, attributed in the
introduction to `patras_mandatory_2024` — i.e. Chapter 1. But §2.1 reports this paper's own
hedonic-controlled gap stabilising at **+0.044 (apartments) / +0.037 (houses)** — 4.4 and 3.7
log points. For apartments the headline is ~60% larger than the paper's own estimate; for
houses it is smaller.

These may well be different estimands (Chapter 1's nationwide DiD vs. this paper's
composition-adjusted gap), in which case nothing is wrong — but they are currently presented
with identical wording, and a referee comparing the abstract to §2.1 will stop there. Either
reconcile them or label them distinctly and say which is which.

## Introduction: paragraph-by-paragraph

Current structure is 9 paragraphs against the corpus template's 12–14. Mapping:

| Current | Does | Verdict |
|---|---|---|
| ¶1 | Unraveling prediction → French challenge → own headline facts → "the market rewards opacity" | **Strong opener**, right instinct. But it front-loads *your own findings*; the corpus keeps ¶1 about the world and the literature, saving own descriptives for later |
| ¶2 | The EPC literature (Brounen & Kok, Hyland & Lyons, Fuerst, Frondel, Myers) → "none can explain why silence commands a premium" | Good content, wrong slot — template ¶2 is *"to learn about X, we examine Y"*, the setting |
| ¶3 | The gap: non-disclosure is not always a choice (Dye; Jung & Kwon) | This is assumption-audit material, unenumerated |
| ¶4 | Dye models are corporate; housing has heterogeneous buyer attention | Second assumption, also unenumerated |
| ¶5 | Model + extension + identification logic + the invariance result | ✗ **~500 words doing four jobs.** Split into model-motivation and findings paragraphs |
| ¶6 | The three-source data and the vantage point; four-group classification | ✓ **Strongest paragraph in the paper.** Matches the template's data paragraph closely. Preserve nearly as-is |
| ¶7–¶8 | Policy extension: efficiency gap, then the complementarity result | Good; needs an explicit contribution performative |
| ¶9 | Roadmap | ✗ delete |

**Missing entirely**, each of which the corpus treats as standard:

- Enumerated descriptive findings — *"First… Second… Third…"* — before the model appears
- The *"we allow for, but do not impose"* framing of the model
- A robustness-preview paragraph
- A nested-model fit comparison
- Explicit contribution performatives (*"Our paper contributes to… by…"*)
- A scope disclaimer
- A generalizability close

### The ρ̂ clipping problem has a home now

Your own `ESTIMATION_STRATEGY_REVIEW.md` flags as critical that ρ̂ = 1 is a *maintained
assumption* in 132 of 140 markets, not an interior estimate. The corpus supplies the exact
register for this: *"allows for, but does not impose"*, *"does not take a stance on why"*, and
*"we do not purport to estimate the one true model."* Stated that way, in §4.1 and previewed
in the introduction, the clipping reads as command of the design rather than as a hole a
referee found. This is the clearest case in the paper where a convention and a known weakness
solve each other.

## Proposed target architecture

Seven sections, one over the corpus norm — deliberately, because the counterfactual carries
the policy signal and should not be buried in §4.

| New | Title | Absorbs from current draft |
|---|---|---|
| §1 | Introduction | §1, rebuilt on the funnel |
| §2 | Unraveling with Possibly Uninformed Sellers | **New** — assembled from intro ¶2–¶4: Akerlof → Grossman/Milgrom in prose → Dye/Jung–Kwon → assumptions (a)–(d) → "an empirical question" |
| §3 | The French EPC Market | 3.1 institutional background + the 2021 reform (from §5.1 + §6.1); 3.2 data, ADEME match, four-group classification (**§5 moves up**); 3.3 the four stylized facts (§2) |
| §4 | A Structural Interpretation | 4.1 Motivation (**new**, from §3.1) · 4.2 Setup (§3.2–3.5) · 4.3 Equilibrium (§4) · 4.4 Identification (§6) · 4.5 Estimates (§7) |
| §5 | Renovation Subsidies | §8 — reframed as *the counterfactual that justifies the structure* |
| §6 | Alternatives and Robustness | gathered from §7's robustness material; add the nested restriction |
| §7 | Conclusion | §9 |
| App. | Proofs, derivations, variable definitions | unchanged |

**Nine sections become seven; nothing is deleted.** Every current section survives as a
section or subsection. The proof appendix is untouched. The equilibrium characterisation,
comparative statics, and policy derivations all persist at full length.

## What is already strong — preserve

- The Grossman/Milgrom framing. The corpus's own top-finance paper opens on the same anchor.
- The data/vantage-point paragraph. Genuinely distinctive and correctly pitched.
- The four-group classification. This is the paper's measurement contribution and the corpus
  rewards exactly this kind of hand-built information measure.
- The stylized-facts section, which already pairs each fact with a structural requirement —
  that is the corpus's "what the facts demand of the theory" move, already present.
- The bibliography's overlap with the RE/finance literature: Brounen & Kok, Myers, Levitt &
  Syverson, and Lizzeri are already cited, so the Tier-2 exemplar list is largely confirming
  choices already made rather than adding new ones.

## Where the policy-note angle strengthens

- **§5 as its own numbered section** makes the retrofitting contribution visible in the table
  of contents.
- **The minimum incentive-compatible subsidy is the single most policy-legible object in the
  paper** and should be named in the abstract.
- **The cost-share heterogeneity result** (zero to nearly 80% across markets) is the natural
  headline of the standalone policy note: it says uniform national programmes are generically
  misallocated, which is a directly actionable claim.
- **The free-riding result** on France's renovation tax credits connects to an existing
  French policy debate (`nauleau_2014`) and gives the note an institutional hook.

## Next step

Fork the `.tex` into `paper-real-estate/`, then begin the section loop at step 1 — the
framing decision and introduction skeleton. Per protocol, that produces a paragraph *plan*
for your approval, not prose.
