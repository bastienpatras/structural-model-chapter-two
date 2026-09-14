# Presenting a Structural Model to a Reduced-Form Audience

The audience is empirical. They are not hostile to structure, but they will not grant it for
free: the model must be shown to buy something a reduced form cannot. Every convention below
serves that burden of proof.

**This is about presentation, not size.** None of it requires cutting model content. A full
equilibrium characterisation, complete comparative statics, and a full proof appendix are all
compatible with these conventions. What changes is the order of exposition and the framing.

## §4.1 Model Motivation — write this subsection first

It is the subsection most often missing and the one that decides whether the reader accepts
the rest. Structure:

**1. One sentence on purpose.** Before anything else:

> "To uncover some of the forces behind [the observed pattern], we use a simple structural
> model of [decision] which allows [agents] to [deviate / behave in the way at issue]."

Note "simple." The corpus describes its own model as simple even when estimation is
involved.

**2. State the permissiveness explicitly.**

> "We allow, but do not impose, [the mechanism] as a potential force behind [the pattern]."

This is the single most useful sentence pattern in the corpus. It converts the model from an
assumption you are imposing into a hypothesis you are letting the data speak to.

**3. Justify the mechanism on two independent grounds.**

- *Resemblance*: the stylized facts resemble evidence from an established literature, which
  rationalises them via this mechanism.
- *Institutional detail*: specific features of the setting make the mechanism plausible.
  Enumerated — First, Second, Lastly — and evidenced.

**4. Rule out the alternatives here, not in robustness.** Argue that the forces that would
*normally* explain the pattern have limited importance in this setting. The corpus's sharpest
version of this is a **timing argument**: competing explanations "would also have to decline
relatively rapidly — within a couple of months — to explain the convergence observed in
Figure 5." Find the analogous argument for your setting; a competing mechanism that cannot
match the observed timing is dead without needing a test.

**5. Introduce the modelling device, justified by external support**, then walk its mechanism
in **plain language with a worked ladder** — the corpus walks level 0 → 1 → 2 → ∞, showing
how the threshold moves at each step, and closes with a pointer to an illustrative figure.
Still no notation.

**6. State what the model does not take a stance on.**

> "The [model] does not take a stance on why [agents] may fail to [do X]. It may be that…
> Or it may be that… Irrespective of which of these leads to [the deviation], we expect…"

This is where a *partially identified or boundary-clipped parameter belongs.* If a parameter
is clipped at a bound in most units, or point-identified in only a subset, say so here, in
this register, and report the identified interval. In this literature that reads as command
of the design. Burying it and letting a referee find it does not.

## §4.2 Model Setup — purpose before notation, every time

Open with what the specification buys:

> "We embed [the device] into a [framework]. This model setup allows us to uncover [the
> latent objects] from [the observed decision], while controlling for [confounds]."

Only then introduce the agent, the type, and the decision. Define notation at first use, in
prose, not in a display block of symbol definitions.

## Propositions: the three-part pattern

An empirical audience skips unmotivated displayed mathematics. Every formal result gets three
parts, in this order:

1. **The proposition**, stated formally.
2. **One sentence of economic reading** — what it means in words, no symbols if avoidable.
3. **The testable implication** — what it predicts in the data, and which exhibit will show
   it.

A proposition with no part 2 and no part 3 will not be read. Proofs go to the appendix
without exception; do not interrupt the argument with a derivation.

## Comparative statics earn their place by mapping to variation

Sign a comparative static, then immediately name the observable variation that traces it out.
A comparative static with no empirical counterpart belongs in the appendix.

## The counterfactual is the model's justification

The strongest available argument for structure is an object the model produces that no
reduced form can: a minimum incentive-compatible transfer, an equilibrium response to a
policy not yet implemented, a welfare decomposition. Make this argument explicitly, early,
and in the introduction as well as §4.1.

A policy counterfactual therefore is not an appendage to a structural paper — it is the
reason the paper is structural. Frame it that way and the policy contribution and the
methodological contribution reinforce each other instead of competing.

## Defending the specification in §5

- **Nested restriction with a fit comparison.** Estimate the restricted model that shuts
  down your mechanism, compare fit accounting for parameter count, and report it. This is
  the most persuasive single robustness result a structural paper can offer.
- **Robustness to the obvious confounds**, listed compactly in one paragraph.
- **Estimation choices** — thresholds, filters, initial values — one short subsection each.

## Scope disclaimer

Include it, in the introduction and again in §4.1 or §5:

> "We do not purport to estimate the one true model. We rather propose one novel way of
> looking at the data through the lens of a workhorse model."

The corpus pairs this with an argument that the chosen model has independent support, which
"allays the concern that once one departs from equilibrium, anything is possible." If your
model has an analogous pedigree, invoke it.
