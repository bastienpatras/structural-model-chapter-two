# §2 Unraveling with Possibly Uninformed Sellers — diagnosis and change log

Draft: `02-unraveling-draft.tex`. New section; ~950 words, two subsections.

## Diagnosis

**The section does not exist.** The paper currently runs Introduction → Setting and Stylized
Facts, with the theoretical benchmark compressed into the introduction and the departures from it
introduced inside §3 Model. Three consequences:

1. **The unraveling argument is never actually made.** It is asserted (silence should be read as
   bad news) but never walked through, so a reader who does not already know Grossman–Milgrom
   cannot see *why* the result obtains, and therefore cannot see which step of it fails here. The
   corpus convention is a full prose derivation with no equations.
2. **An orphaned reference.** §3.1 Motivating Intuition opens *"The two failures interact and
   reinforce each other"* — with no antecedent anywhere in §3. The two failures lived in the old
   introduction's ¶3–¶4. This was already fragile and the reframed introduction makes it worse.
3. **The theory's assumptions are never enumerated**, so the paper's contribution is not visibly
   located against a specific assumption. This was the headline finding of the whole-paper
   diagnosis.

## Structure

| Subsection | Job |
|---|---|
| 2.1 The Unraveling Benchmark | The economic problem from first principles → the unraveling argument narrated in prose → the four assumptions enumerated (a)–(d) → the fourth is the under-examined one |
| 2.2 Two Departures and Why They Compound | Departure from (a): sellers who cannot disclose · Departure from (d): buyers who do not price · **why they compound** · the conceptual map · closes on the empirical question |

No equations, per convention. No data, per convention — the section stays conceptual and hands off
to §3 for measurement.

## Relocations

| What | From | To |
|---|---|---|
| "The two failures interact and reinforce each other…" mechanism | §3.1 Motivating Intuition | §2.2, third paragraph — **now with a proper antecedent**, since 2.2's first two paragraphs establish the two departures explicitly |
| "the two parameters are independently movable by policy" | §3.1 | §2.2 closing paragraph |
| `fig:equilibrium_outcomes` (the 2×2 taxonomy) | §3.1 | §2.2 — it is a conceptual taxonomy, not an empirical result, so it belongs with the theory |
| Dye / Jung–Kwon discussion | old intro ¶3 | §2.2 ¶1, expanded from one sentence to a full paragraph |
| Buyer-heterogeneity argument | old intro ¶4 | §2.2 ¶2 |

**Deliberately left in place:** the *"France operates in the bottom-right cell"* paragraph stays in
what becomes §4.1 Model Motivation. It is a data claim (48.8% audit coverage), and §2 must stay
conceptual. §2 gives the map; §3 supplies the coordinates; §4.1 places France on it.

## ⚠ Wiring dependency

`02-unraveling-draft.tex` contains `fig:equilibrium_outcomes`. **The float must be deleted from
§3.1 in the same commit that inputs this file**, or the label collides and the reference resolves
to the wrong figure. Flagged at the top of the draft too.

## Additions needing verification

1. **§2.1 ¶1 has no citation.** The adverse-selection setup is standard, but the canonical cite —
   **Akerlof (1970)** — is *not in `DPE_library.bib`*. The corpus opens exactly this paragraph with
   it. Recommend adding; I did not insert a key that would break the build.
2. **Assumption (c), credibility, has no citation** for the same reason: the standard cites
   (Crawford–Sobel 1982, Stocken 2000) are absent from the bibliography. Currently asserted
   without support. Recommend adding at least one.
3. `verrecchia_1983` and `jovanovic_1982` are used for assumption (b), disclosure costs. Both were
   already in the bibliography but previously uncited in the main text — check the attribution
   reads correctly to you.

## Consistency notes

- §2.1's enumeration of (a)–(d) deliberately repeats the introduction's ¶4. This is the corpus
  pattern, not redundancy: the introduction states the audit compactly, §2 derives it properly.
  The wording is kept parallel so a reader can map one to the other.
- The framing steer is respected — this section is segment-agnostic, since the theory applies to
  both. Apartment-first weighting begins to matter in §3.

## Not yet incorporated

The **stability-of-the-undisclosed-share** identification argument (v2 queue item 5) is *not* in
this section, deliberately: it is an identification argument resting on data, so it belongs in
§4.4 with a preview in the introduction. Noted here so it does not get lost — for apartments the
share moves only from 35.9% to 33.8% across the reform, against 24.6% → 14.4% for houses, which is
both the cleanest identification argument in the paper and the sharpest statement of why this is
an apartment story.
