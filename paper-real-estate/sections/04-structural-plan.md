# §4 A Structural Interpretation — restructure plan

Protocol step 2: structure before prose. This is the largest consolidation in the rewrite —
four current sections become one — so it gets a plan first. Nothing drafted yet.

## The consolidation

| Current | Becomes | Content |
|---|---|---|
| §4 Model 4.1 Motivating Intuition | **4.1 Motivation** | rewritten per convention — see below |
| §4 Model 4.2–4.5 (Environment and Timing · Payoffs and Hiding Costs · Buyer Valuations and Demand · Buyer Beliefs and the Non-Disclosing Pool, incl. Who Hides? and The Belief Function) | **4.2 Setup** | relocated, demoted one level |
| §5 Equilibrium Analysis 5.1–5.3 (Disclosure Incentives · Equilibrium Characterization · Comparative Statics) | **4.3 Equilibrium** | relocated, demoted one level |
| §6 Identification 6.1–6.4 (the reform as natural experiment · DiD identification of ρ · measuring beliefs · closed-form identification of c₀) | **4.4 Identification** | relocated, demoted one level |
| §7 Results 7.1–7.2 | **4.5 Estimates** | relocated; **no standalone Results section** |

Four sections → one. Section count 9 → 6; the policy section makes 7, by design.

**Nothing is cut.** All ten propositions/lemmas/corollaries stay in the main text, the proof
appendix is untouched, comparative statics stay at full length, and every figure and table
survives. This is a relocation and a re-titling, exactly as you specified.

Section titled *"A Structural Interpretation"* per the corpus: the model interprets facts already
established in §3 rather than arriving unmotivated.

## 4.1 Motivation — the one subsection genuinely rewritten

Current 4.1 is a good economic argument but not in the form this literature expects. Per
`references/model-presentation.md` it needs six moves in order:

1. **Purpose in one sentence, before any notation.** "To recover the forces behind the patterns in
   §3, we use a model of the disclosure decision that…"
2. **"We allow, but do not impose, strategic concealment."** The load-bearing phrase.
3. **Justify on two independent grounds** — that the facts resemble the Dye/Jung–Kwon structure,
   and that the institutional detail in §3.1 supports it.
4. **Rule out the alternatives here, not in robustness.** The corpus's sharpest version is a
   *timing* argument. Ours: a competing explanation must produce an abrupt shift at July 2021 in
   both β₁ and Δ simultaneously, at the same markets and the same date, while the undisclosed share
   stays flat. The material for this already exists in current §6.1 — it is currently buried in the
   identification section and belongs here too.
5. **Plain-language walkthrough** of the mechanism, with the pointer to `fig:equilibrium_outcomes`
   (now in §2.2). No notation.
6. **State what the model does not take a stance on** — and this is where the **ρ̂ clipping** goes:
   that in most markets the data are consistent with full buyer sensitivity but cannot pin down how
   close to one it lies, so ĉ₀ is an upper bound. Stated here, in this register, it reads as command
   of the design.

The *"France operates in the bottom-right cell"* paragraph stays here, now referencing §2.2's
taxonomy across sections.

## 4.4 Identification — one substantive addition

Add the **stability-of-the-undisclosed-share** argument (v2 queue item 5). For apartments the share
moves only 35.9% → 33.8% across the reform, against 24.6% → 14.4% for houses. A stable share means
the composition of the silent pool, and hence the equilibrium belief ê\*, does not shift — so the
jump in the premium cannot be a supply-side compositional artefact and is attributable to
demand-side repricing.

This is currently the paper's strongest unused identification argument. It also states precisely
why apartments carry the paper: the identification is cleanest exactly where the share is most
stable. It should sit alongside the existing joint-flatness-of-β₁-and-Δ argument, which is doing
similar work.

## 4.5 Estimates — ordering change

**Lead with σ̂₁ = 0 across all 140 markets**, framed as the specification test: a model-implied
restriction, never used in estimation, that the data could have rejected. Per your confirmation,
and it is also the answer to the corpus's nested-model-comparison convention (see `DIAGNOSIS.md`).
Currently this result is under-placed.

Then the magnitudes (ρ̂, ĉ₀), then the Δ̂-versus-ĉ₀ decomposition, which is already well written.

## Two fixes folded in

- **`cor:rho` and `prop:pi` have no economic gloss.** They sit back to back separated only by
  "Proof. See Appendix." Each needs one sentence of economic reading plus a testable implication.
  Eight of the ten theorem environments already have this; these two are the exceptions.
- **Robustness material currently inside §7** gets extracted to the new §6, rather than left mixed
  in with the estimates.

## Wiring dependencies

1. Delete four section blocks from `main.tex`, replace with one `\input`
2. Preserve `\label{sec:model}`, `\label{sec:equilibrium}`, `\label{sec:identification}`,
   `\label{sec:results}` — **all are referenced elsewhere**; each must be carried onto the
   corresponding new subsection or the references break. To verify before cutting, as with
   `sec:data` in §3.
3. Demote `\subsection` → `\subsubsection` throughout the four relocated blocks
4. Proof-appendix references (`app:proofs`) must continue to resolve

## What I need from you

Only one thing, and it is a judgement call rather than a fact:

**Does 4.2–4.5 with nested subsubsections read as acceptable to you?** The consolidation produces a
long section with three levels of nesting (4.2.1 Environment and Timing, and so on). It is the
corpus shape and it cuts nothing, but it is a visible change to how your paper is organised, and
some authors dislike three-level nesting. The alternative is keeping Equilibrium Analysis as its own
§5 — which costs one section against the target but keeps the nesting shallower.

My recommendation is the full consolidation: a single authoritative §4 presents the structural
contribution more strongly than four thin sections, which was the point of the exercise.
