# Section Architecture

## The template

| § | Title pattern | Contents |
|---|---|---|
| 1 | Introduction | See `introduction.md` |
| 2 | *"The [Theory] Prediction"* / *"Conceptual Underpinnings"* | The economic problem; the theory in prose; its assumptions enumerated; closing declaration that its descriptiveness is an empirical question |
| 3 | *"The [Industry/Market]"* / *"Setting and Data"* | 3.1 Institutional Background · 3.2 Data · 3.3 Stylized Facts |
| 4 | *"A Structural Interpretation"* (or *"Research Design and Results"* if reduced-form) | 4.1 Motivation · 4.2 Setup · 4.3 Estimation · 4.4 Findings |
| 5 | *"Alternatives and Robustness"* | 5.1 Alternative models (incl. nested restrictions) · 5.2 Sample and estimation choices |
| 6 | Conclusion | |

Appendix: proofs, derivations, variable definitions, supplementary exhibits.

## §2 is conceptual, not bibliographic

The most frequent misreading of this template is to treat §2 as a literature review. It is
not. It is a *verbal derivation* of the theory whose descriptiveness the paper tests:

1. Open on the economic problem, from first principles and with the canonical citation
   (information asymmetry → adverse selection → Akerlof).
2. Walk the theoretical logic through in prose. **No equations.** The corpus spends a full
   paragraph narrating an unravelling argument step by step in words — best type discloses,
   next-best anticipates and follows, and so on.
3. Enumerate the assumptions the result rests on.
4. Close: *"its descriptiveness … is an empirical question."*

Related-literature citations go in the introduction's contribution paragraphs, not here.

## Data goes in §3, before the model

Institutional background, then data, then stylized facts — all before any model appears. A
Data section placed after the model is the clearest structural tell that a paper was written
for a different field.

The stylized-facts subsection ends with a verdict paragraph: *"Collectively, these stylized
facts suggest [theory] is not immediately descriptive… Yet [qualified partial verdict]."*

## Consolidating a many-sectioned draft

Papers written for economics or accounting audiences commonly arrive with 9–10 sections.
The mapping is a relocation, not a cut. A worked example:

| Original | Destination |
|---|---|
| Introduction | §1 |
| Setting and Stylized Facts | §3.1 + §3.3 |
| Model | §4.2 |
| Equilibrium Analysis | §4.3 |
| Data | §3.2 — **moves up**, ahead of the model |
| Identification | §4.4 |
| Results | §4.5 — **no standalone Results section**; findings sit inside the model section |
| Policy Extension / Counterfactual | §5 if it is the model's justification; else §4.6 |
| Robustness (if scattered) | gather into its own section |
| Conclusion | final |
| Proofs | appendix |

Nothing is deleted. Section count falls; content does not.

## Where a policy or counterfactual section goes

Two defensible placements, and the choice is strategic:

- **As a numbered section of its own** — appropriate when the counterfactual is the reason
  the paper is structural, and when the author wants the policy contribution visible to
  readers who skim the table of contents. Costs one section against the six-section norm.
- **As a final subsection of §4** — tighter, more conventional, but the policy contribution
  becomes less visible.

Prefer the standalone section when the counterfactual delivers an object no reduced-form
design could produce. That is precisely the argument that justifies the structure, so it
should not be buried.

## §5: Alternatives and Robustness

Two subsections, in this order:

1. **Alternative models** — including at least one *nested* restriction of your model, with
   a formal fit comparison (log-likelihood, penalised for parameter count). This is the
   strongest available defence of a structural specification: it shows the added structure
   earns its degrees of freedom rather than merely fitting better.
2. **Sample and estimation choices** — thresholds, exclusions, initial values, filters. One
   short subsection per choice that a referee could otherwise suspect was chosen to
   flatter the result.
