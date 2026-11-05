# Section-by-Section Diagnosis and Rewrite

A protocol for reframing an existing paper. Work one section at a time and stop for author
feedback between sections — a reframing cascades, so an unreviewed decision in an early
section corrupts everything after it.

## Order of work — not document order

The framing decision propagates downward, so it comes first; the abstract compresses the
finished introduction, so it comes last.

1. **Framing decision + introduction skeleton.** The hook, the isolated assumption, the
   contribution claims, the audience. Everything else inherits this. Produce a paragraph
   *plan* here, not prose.
2. **Setting / institutional background.**
3. **Data and measurement** — where an empirical audience is most sceptical, especially of
   record linkage, matching, and constructed samples.
4. **Model and identification**, restructured per `model-presentation.md`.
5. **Results.**
6. **Policy / counterfactual.**
7. **Conclusion.**
8. **Abstract**, last.
9. **Introduction, final prose pass** — after the body is settled.

## Per-section loop

**Step 1 — Diagnose before writing anything.**

Read the current section in full. Then report:

- What the section is currently *doing*, in one sentence.
- Which conventions it breaches, each named explicitly, with the specific text at fault.
- What is already right — say so, and preserve it. A reframing that rewrites strong material
  wastes the author's time and erodes their voice.

  **But "preserve" applies to structure and voice, never to facts.** Judging a paragraph
  well-built is not the same as checking that its claims are true. Any paragraph carried
  forward — especially a data or measurement paragraph — must still be audited claim by
  claim against what the code and the data sections actually support. Ask specifically:
  does every listed data source actually get used the way the sentence says? Is every source
  described as *matched* genuinely matched at the unit of observation? Does the sample scope
  named in the prose match the sample the numbers come from? A well-written overclaim
  propagates silently precisely because it reads well, and the author's own draft is where
  such overclaims are most likely to have gone unexamined.
- The single highest-leverage change.

Never rewrite before diagnosing. A rewrite the author cannot audit against a stated
diagnosis is not reviewable.

**Step 2 — Propose structure, not prose.**

An outline: subsection headings, one line on each subsection's job, and an explicit map of
what moves where from the current draft. Flag anything that leaves the section, and say where
it lands — the author must be able to confirm nothing was silently dropped.

**Step 3 — Draft, with changes flagged.**

Write the section. Then list, separately, the substantive changes and why each was made.
Distinguish:

- *Relocations* — content moved, unchanged
- *Reframings* — same content, different framing or emphasis
- *Additions* — new material, which the author must verify for factual accuracy
- *Cuts* — always call these out individually and justify each; default to not cutting

Any number, estimate, or citation you did not find in the source is an addition, and must be
marked as needing verification. Do not invent magnitudes to fill a template slot.

**Step 4 — Pause.** Hand back and wait. Do not proceed to the next section.

**Step 5 — Iterate**, then commit the accepted section before moving on.

## Diagnosing structure across the whole paper

Before starting on sections, run these checks:

- [ ] Section count — more than seven suggests consolidation (see `structure.md`)
- [ ] Is there a Data section positioned *after* the model?
- [ ] Is there a standalone Results section?
- [ ] Is there a standalone literature review?
- [ ] Is there a roadmap paragraph?
- [ ] Does §2 contain equations?
- [ ] Does the introduction contain notation?
- [ ] Are the theory's assumptions enumerated anywhere?
- [ ] Is there a nested-model fit comparison?
- [ ] Does any proposition lack an economic gloss and a testable implication?
- [ ] Is a partially identified or bound-clipped parameter presented as if point-identified?

## On known weaknesses

When the author already knows a design weakness — a parameter clipped at a bound, a coverage
gap, an untested parallel-trends assumption — the conventions in this literature give a
principled home for it rather than a reason to hide it. See the "allows for, but does not
impose" and "does not take a stance on" patterns in `model-presentation.md`. Surface the
weakness in the author's own voice, in the register the literature uses, and report the
identified interval. A referee who discovers an unstated limitation discounts the whole
paper; an author who states it first is read as being in command of the design.
