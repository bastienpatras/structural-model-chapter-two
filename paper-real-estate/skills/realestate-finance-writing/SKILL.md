---
name: realestate-finance-writing
description: "Structure, tone, and writing conventions for empirical real-estate and finance papers, with a specialty in disclosure/information-economics settings and in presenting structural models to reduced-form audiences. Use when drafting, restructuring, or diagnosing a paper (or section of one) aimed at top real-estate or finance journals (Real Estate Economics, JREFE, JUE, JF, JFE, RFS, Management Science) or at a real-estate/finance department audience such as a job-market paper. Triggers: reframing a paper for a new audience, 'does this read like a finance paper', restructuring sections, writing or fixing an introduction funnel, motivating a structural model, presenting propositions to an empirical audience, converting a policy extension into a counterfactual that justifies the model."
---

# Real-Estate & Finance Paper Conventions

Codified from a corpus of disclosure and information-economics papers (see
`references/corpus.md` for provenance and confidence levels). Purpose: make a paper read
as *native* to top real-estate/finance outlets rather than translated into them.

## The two rules that matter most

**1. Six sections.** The corpus is strikingly uniform:

| § | Function |
|---|---|
| 1 | Introduction |
| 2 | Conceptual framing — theory in prose, assumptions enumerated, ends on the empirical question |
| 3 | Setting: institutional background → data → stylized facts |
| 4 | The core analysis (for structural papers: *"A Structural Interpretation"*) |
| 5 | Alternatives and robustness |
| 6 | Conclusion |

A paper with nine or ten sections is signalling that it was written for a different field.
Consolidate — but see rule 2 about *how*.

**2. Consolidate, never cut.** Restructuring to this architecture is a *relocation*
exercise. Model, equilibrium, identification, and results sections merge under one roof;
data moves up into the setting section; proofs go to the appendix. Nothing is deleted. A
structural contribution presented in four thin sections reads weaker than the same content
presented as one authoritative section.

## Core conventions

**Data belongs with the institutional setting, before the model.** The corpus order is
institutional background → data → stylized facts → model. A Data section appearing *after*
the model is a field tell.

**The model is an interpretation of facts already on the table.** Establish the puzzle
descriptively in §3, then open §4 by explaining why description is insufficient. The
canonical section title is "A Structural Interpretation."

**Every model subsection opens purpose-first, math-later.** One sentence on what the model
buys you before any notation. See `references/model-presentation.md`.

**"We allow for, but do not impose."** The load-bearing phrase for introducing a
mechanism. It frames the model as permissive rather than assumed, and it is also the
honest, literature-sanctioned way to present a partially identified or boundary-clipped
parameter. Pair it with an explicit statement of what the model does *not* take a stance
on.

**Rule out alternative explanations inside the model motivation**, not only in robustness.
The corpus argues, before the model is even specified, that competing forces cannot
generate the observed pattern — often on timing grounds.

**No standalone literature review.** §2 is *conceptual*: the economic problem, the theory
walked through in prose with no math, its assumptions enumerated, and a closing declaration
that its descriptiveness is an empirical question. Related-literature citations are
distributed into the introduction's contribution paragraphs instead.

**No roadmap paragraph.** Do not write "the remainder of the paper proceeds as follows."
The introduction's final paragraph pre-empts the generalizability objection instead:
concede the limits of the setting, then argue the mechanism travels.

**State scope limits explicitly and early.** "We do not purport to estimate the one true
model." Read as confidence in this literature, not weakness — it demonstrates you know
what your design can and cannot deliver.

## Reference files

- `references/structure.md` — section architecture, consolidation mappings, what goes where
- `references/introduction.md` — the introduction funnel, paragraph by paragraph
- `references/model-presentation.md` — motivating, specifying, and defending a structural model
- `references/prose.md` — sentence-level conventions, phrasing, what to avoid
- `references/diagnostic-protocol.md` — how to run a section-by-section diagnosis and rewrite
- `references/corpus.md` — provenance, and which rules are verified vs. provisional

## Using this skill

For a **diagnosis**, follow `references/diagnostic-protocol.md`: read the section, score it
against the relevant conventions, and report specific violations with the convention each
one breaches. Never rewrite before diagnosing.

For a **rewrite**, propose structure before prose. Show the author what moves where and why
before producing paragraphs, and flag every substantive change rather than burying it.

Do not quote corpus prose into a draft. These are structural and functional conventions;
the author's own voice fills them.
