# `/humanize` Detection Report

**File:** `paper-real-estate/sections/04-structural-draft.tex`
**Scope:** lines 188–323 — `\subsubsection{Disclosure Incentives}`, `\subsubsection{Equilibrium Characterization}`, and the `Corollary~\ref{cor:rho}` block inside `\subsubsection{Comparative Statics}`
**Date:** 2026-09-19
**Mode:** detect-only (per `.claude/rules/writing-with-ai.md` — no edits made)

Five formal environments in this span were excluded from the audit per explicit author
instruction (kept verbatim, not narrativized): `Proposition~\ref{prop:premium}` (192–199),
`Corollary~\ref{cor:hq_disclose}` (205–208), `Proposition~\ref{prop:equilibrium}` (230–238),
`Proposition~\ref{prop:comparative_statics}` (290–297), `Corollary~\ref{cor:rho}` (306–312).
Everything else — connective prose, exposition, and `Table~\ref{tab:equilibria}`'s surrounding
text — was audited against all 10 canonical categories.

## Headline finding

Categories 1, 2, 6, 7, 9, 10 are clean: no boilerplate transitions, cliché lexicon, hedging
stacks, "not only/but also" frames, hyphenation pile-ups, or self-important framing anywhere in
this span. The one real, mechanical tell is a **"statement: elaboration" colon construction**
used as the default connective — 17 instances in ~135 lines of prose — plus one paragraph that
stacks two em-dash asides past the per-paragraph threshold.

## Per-category counts

| Category | HIGH | MED | LOW |
|---|---|---|---|
| 1. Boilerplate transitions | 0 | 0 | 0 |
| 2. AI-cliché lexicon | 0 | 0 | 0 |
| 3. Em-dash/punctuation (colon-as-hinge tic + em-dash overuse) | 1 | 6 | 11 |
| 4. Symmetric paragraph shapes | 0 | 2 | 0 |
| 5. Tricolon abuse | 0 | 1 | 1 |
| 6. Hedging stacking | 0 | 0 | 0 |
| 7. "Not only X, but also Y" | 0 | 0 | 0 |
| 8. Formulaic openers | 0 | 0 | 1 |
| 9. Hyphenation excess | 0 | 0 | 0 |
| 10. Sycophancy/self-importance | 0 | 0 | 0 |
| **Total** | **1** | **9** | **13** |

Total words in scope: roughly 1,350. On the skill's rough thresholds (>8 HIGH/1000 words =
rewrite; 5–8 = strip before submission; <5 = light cleanup), this span sits well under 5
HIGH/1000 words — **light cleanup**, concentrated almost entirely in one repeating pattern
rather than spread across many categories.

## Findings

| Line | Category | Severity | Current text | Suggested rewrite |
|---|---|---|---|---|
| 203 | 3 (colon-as-hinge tic) | MED | "A high-quality seller has nothing to gain from ambiguity: disclosure reveals her type exactly, while non-disclosure pools her with low-quality hiders" | "A high-quality seller has nothing to gain from ambiguity. Disclosure reveals her type exactly; non-disclosure pools her with low-quality hiders" |
| 203 | 3 (colon-as-hinge tic) | MED | "A low-quality seller faces the opposite incentive: concealment lets her price off $e(\sigma_0^*)$" | "A low-quality seller faces the opposite incentive — concealment lets her price off $e(\sigma_0^*)$" (or split into two sentences; avoid repeating the colon pattern from the sentence above) |
| 212 | 3 (colon-as-hinge tic) | LOW | "This is a partial-unraveling result: the top of the quality distribution fully separates." | "This is a partial-unraveling result. The top of the quality distribution fully separates." |
| 219 | 3 (colon-as-hinge tic) | LOW | "$e(\sigma_0)$ falls monotonically in $\sigma_0$: every additional hider adds weight..." | "$e(\sigma_0)$ falls monotonically in $\sigma_0$, because every additional hider adds weight..." |
| 258 | 3 (colon-as-hinge tic) | MED | "Neither corner fits what we observe: universal concealment would need..." | "Neither corner fits what we observe. Universal concealment would need..." |
| 263 | 8 (formulaic opener) | LOW | "We derive the non-disclosure premium as follows:" | Cut the lead-in; let the equation follow the prior paragraph directly, or write "The non-disclosure premium follows directly:" |
| 278 | 3 (em-dash overuse — 4 dashes/2 pairs in one paragraph) | HIGH | "...come from the same comparison --- the hiding gain $\Delta(e)=\rho\beta_1 e$ evaluated at the two extremes of pool contamination, set against the hiding cost $c_0$." ... "The premium inherits a strict ordering across the three regimes, ... --- Cost-Deterred Hiding above, Complete Adverse Selection below, Partial Pooling pinned at $c_0$ in between --- and the interior value depends on neither $\pi$ nor $\rho$." | Convert the second dash-pair to a parenthetical: "...three regimes (Cost-Deterred Hiding above, Complete Adverse Selection below, Partial Pooling pinned at $c_0$ in between), and the interior value depends on neither $\pi$ nor $\rho$." |
| 278 | 5 (tricolon stacking) | MED | "no one hides; ...everyone hides; in between, an interior share hides..." stacked with "Cost-Deterred Hiding above, Complete Adverse Selection below, Partial Pooling pinned at $c_0$ in between" — two triadic constructions in one paragraph | Keep one triad, recast the other in ordinary prose rather than a parallel list |
| 280 | 3 (colon-as-hinge tic) | LOW | "so $\sigma_0^*=0$ and the pool stays uncontaminated: $e^*=\bar{\theta}$" | "so $\sigma_0^*=0$ and the pool stays uncontaminated at $e^*=\bar\theta$" |
| 280 | 3 (colon-as-hinge tic) | LOW | "but the mechanism differs: their unraveling runs through a belief penalty" | "but the mechanism differs, since their unraveling runs through a belief penalty" |
| 282 | 3 (colon-as-hinge tic) | LOW | "\emph{Complete Adverse Selection} is the opposite corner: the hiding gain survives even the dirtiest pool" | "\emph{Complete Adverse Selection} is the opposite corner — the hiding gain survives even the dirtiest pool" |
| 282 | 3 (colon-as-hinge tic) | LOW | "This is the \citet{dye_disclosure_1985} mechanism at work: a residual, non-strategic silent population keeps silence partially informative" | "This is the \citet{dye_disclosure_1985} mechanism: a residual, non-strategic silent population keeps silence partially informative" (or recast without colon) |
| 280, 282, 284 | 4 (symmetric paragraph shapes, 3-paragraph window) | MED | Three consecutive regime paragraphs ("\emph{Cost-Deterred Hiding} is where...", "\emph{Complete Adverse Selection} is the opposite corner...", "Between the two corners sits \emph{Partial Pooling}...") each follow: italicized regime name + copula + colon-elaboration opener → a "mechanism" sentence → a closing generalizing clause | Vary at least one paragraph's opening syntax — e.g., lead Partial Pooling with the indifference condition, $\Delta(e(\sigma_0^*))=c_0$, rather than restating "sits between the two corners"; drop the repeated "mechanism...:" phrasing in at least one instance |
| 284 | 3 (colon-as-hinge tic) | LOW | "Between the two corners sits \emph{Partial Pooling}: $\Phi$ is positive at $\sigma_0=0$..." | "Partial Pooling sits between the two corners. $\Phi$ is positive at $\sigma_0=0$..." |
| 286 | 3 (colon-as-hinge tic, 3 in one paragraph) | HIGH (cluster); MED individually | "That invariance is just the indifference condition doing its job: the price gap..." / "Take a rise in $\pi$: holding $\sigma_0^*$ fixed it would mechanically dirty the pool..." / "...rather than a free function of market composition: the observable price gap..." | Break the pattern for at least two of the three: "Take a rise in $\pi$. Holding $\sigma_0^*$ fixed, it would mechanically dirty the pool..."; "...rather than a free function of market composition — the observable price gap between non-disclosing and disclosed-low sellers identifies $c_0$ directly." |
| 286 | 5 (tricolon, minor) | LOW | "fewer hiders, a cleaner pool, $e$ rebounds" | fine as-is in isolation; flagged only because it compounds the paragraph's density |
| 302–303 | 4 (symmetric template repetition) + 3 (colon-as-hinge tic ×4) | MED | "The effect of $\pi$ operates through the \textit{belief channel}: as the share of informed sellers rises..." / "The effect of $\rho$ operates through the \textit{revenue channel}: a larger share of EPC-sensitive buyers..." immediately followed by "The effect of $\pi$ operates through the belief function: a higher $\pi$ increases the contamination weight..." — near-identical clause repeated 3x across two consecutive bullets | Vary the third repetition: "$\pi$'s effect runs through the same belief channel as in part (i): a higher $\pi$ increases the contamination weight..." |
| 303 | 3 (colon-as-hinge tic) | LOW | "The parameters $\pi$ and $c_0$ are therefore \textit{policy substitutes}: each reduces strategic hiding through a distinct channel" | "...are therefore \textit{policy substitutes} — each reduces strategic hiding through a distinct channel" |

## Top 3 most concentrated paragraphs

1. **Line 286** ("What makes this regime useful is that the equilibrium premium equals $c_0$
   exactly...") — three separate "statement: elaboration" colon constructions in one paragraph,
   the single densest instance of category 3 in the span.
2. **Lines 302–303** (comparative-statics bullets, Part (i) and Part (ii) of the itemize block)
   — four colon-elaborations plus a near-verbatim template sentence ("The effect of X operates
   through the Y channel/function:") repeated three times across two consecutive bullets — the
   only place category 3 and category 4 overlap directly.
3. **Line 278** ("All three equilibria in Proposition~\ref{prop:equilibrium} come from the same
   comparison...") — the only paragraph exceeding the em-dash threshold outright (2 pairs/4
   dashes), compounded with two stacked tricolon constructions.

Honorable mention: the three-paragraph regime-description block (lines 280, 282, 284 —
Cost-Deterred Hiding / Complete Adverse Selection / Partial Pooling) is the only true
symmetric-paragraph-shape finding in the span and, taken together, carries 5 of the 17
colon-tic instances.

## Action recommendation

**Light cleanup, not a rewrite.** Nothing here rises to the "reads as AI-drafted" threshold —
the AI-cliché lexicon, boilerplate transitions, hedging stacks, and self-important framing
categories are all fully clean. The one real pattern (colon-as-hinge, 17 instances) is
mechanical enough to fix quickly: break roughly half of the 17 instances into two sentences or
a different connective, prioritizing the three-instance cluster at line 286 and the
near-duplicate "effect of X operates through Y" sentences at lines 302–303, which is also the
span's only genuine symmetric-paragraph-shape finding.

This is a detect-only report per `.claude/rules/writing-with-ai.md`; no edits were made to the
audited file. Even after this cleanup, note that a clean `/humanize` report means the prose
reads well — it does not mean it reads as human-written to a neural detector (see that rule for
why, and the measurement-based alternative if provenance matters for this section).
