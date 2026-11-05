# Reframing the JMP for Real Estate & Finance Audiences

Working plan for `paper-real-estate/`. Branch: `paper-real-estate`.
Started 2026-08-11.

## Objective

Rewrite *"When Silence Pays: Mandatory Disclosure and Strategic Concealment in
Housing Markets"* (currently `paper/main_concise.tex`) to the structure, tone, and
conventions of top real-estate and finance journals, following advice from Thomas
Bourveau (Oxford Saïd / formerly Columbia).

Secondary objective: the rewrite should signal policy-note capability, leaning on the
retrofitting/subsidy results already in §7.

## Decisions locked

1. **Target: top real-estate and finance journals**, with the caveat that this is a
   JMP. Resolution rule: **the strictest constraint wins the front matter.** Write
   title/abstract/intro/contribution to finance top-3 convention (*JF*, *JFE*, *RFS*) —
   an intro that satisfies *JFE* satisfies *REE*; the reverse is false. Let the body
   carry the RE-friendly depth, which the JMP needs anyway. One document, not two.

2. **The structural work stays in full.** No cutting, no compressing. Restructure only:
   reorganise so the model is presented the way this literature presents models.
   Corollary for the skill: it must encode rules for *presenting* a model section
   (proposition → one-sentence economic reading → testable implication), not for
   shrinking one.

3. **The model earns its keep via the counterfactual.** Framing is not "demote the
   model" but: the reduced-form fact motivates, and the model delivers an object no
   reduced form can — the minimum incentive-compatible retrofit subsidy (§7). This
   simultaneously justifies the structure and protects the policy angle. The
   retrofitting result stops being an add-on and becomes the reason the paper is
   structural.

4. **Fork with shared exhibits.** Copy the `.tex` into `paper-real-estate/`, but point
   `\graphicspath` back at `paper/fig/` and reference `results/tables/` so exhibits stay
   single-sourced and numbers cannot drift between versions.

5. **Skill installed globally** at `~/.claude/skills/`, not scoped to this repo.

6. **Agent deferred.** Build the skill first. A skill loads conventions into the working
   conversation and keeps the author in the loop, which is what section-by-section
   collaboration needs. Add a global reviewer agent later only for adversarial
   "would this land at *JF*/*REE*?" passes, which benefit from a separate context.

7. **Policy note is a separate deliverable**, in `policy-note/`. Trying to make the
   paper itself *sound* policy-oriented fights the finance framing; a standalone 3–4
   page retrofitting brief that the paper's tightened §7 cites gives both signals
   cleanly.

## Key finding from the corpus (2026-08-11)

Bourveau's corpus is 18/19 accounting journals (JAR ×4, TAR ×4, RAST ×4, JAE, CAR ×2,
Management Science ×2, JEEA) with **exactly one top-finance placement**:

> Bourveau, Breuer & Stoumbos, "Learning to Disclose: Disclosure Dynamics in the 1890s
> Streetcar Industry," *Review of Financial Studies* 38(9), 2025.

This is the single most valuable template in the corpus. It is a **structural disclosure
paper that placed in a top finance journal**, and it opens on the *same theoretical
anchor as our paper*: Grossman (1981), Milgrom (1981), and the question of whether the
unravelling result is descriptive.

Two consequences:

- **His corpus alone cannot teach top RE/finance conventions.** It teaches how to make a
  disclosure-regulation research design credible — that is the layer to take from him.
  The Tier-2 RE/finance exemplars are load-bearing, not garnish.
- **Its section structure maps onto ours without cutting anything.**

### Structure comparison

| Bourveau et al. (RFS) | Current draft |
|---|---|
| 1 Introduction | 1 Introduction |
| 2 Unravelling + related literature, closing on "is an empirical question" | — |
| 3 The Streetcar Industry: 3.1 Institutional Background, 3.2 Historical Data, 3.3 Stylized Facts | 2 Setting and Stylized Facts; **5 Data** (far later) |
| 4 A Structural Interpretation: 4.1 Model *Motivation*, 4.2 Setup, 4.3 Estimation, 4.4 Findings | 3 Model; 4 Equilibrium Analysis; 6 Identification; 7 Results |
| 5 Robustness: alternative models, estimation/sample choices | scattered |
| 6 Conclusion | 9 Conclusion |

Conventions implied:

- **Data belongs with the institutional setting, before the model.** Ours sits at §5.
- **The model is "a structural interpretation"** of facts already established, and gets
  an explicit *Motivation* subsection arguing why a model is needed at all.
- **No standalone Results section** — model findings live inside the model section.
- **Robustness is its own section**, organised as alternative models + estimation choices.

### Intro funnel (from the RFS paper)

- ¶1 — the institutional puzzle in three sentences, then the theoretical benchmark
  (unravelling), then why its descriptiveness is unclear. No "in this paper we" yet.
- ¶2 — "To learn about X, we examine Y": the setting, with rich institutional detail.
- ¶3 — what the theory predicts *in this setting*, and why the setting is a suitable
  testbed.

## Phases

- [x] **Step 0** — commit pending work, fast-forward `main`, branch `paper-real-estate`,
      create working folder.
- [~] **Phase 1** — corpus. Tier 1 (Bourveau) partially acquired; Tier 2 (RE/finance
      exemplars) pending the venue calibration. See `corpus/INDEX.md`.
- [ ] **Phase 2** — distil conventions into a global skill. Patterns and abstracted rules,
      not quoted prose.
- [ ] **Phase 3** — reviewer agent (conditional).
- [ ] **Phase 4** — fork the `.tex`, then section-by-section: diagnose → propose
      restructure → draft → author feedback → iterate → commit. **Not in document
      order**; the framing decision cascades:
      1. Framing decision + intro skeleton
      2. Setting / institutional background (+ data moved up)
      3. Data & measurement (the ADEME match is where an RE/finance reader is most sceptical)
      4. Model & identification, restructured as "a structural interpretation"
      5. Results
      6. Policy / retrofitting
      7. Conclusion
      8. **Abstract last** — it compresses the finished intro.
      Literature is a *decision*, not a section: RE/finance typically folds it into the
      intro's contribution paragraph, accounting keeps it standalone. Note that the RFS
      paper *does* keep a standalone §2. Decide at step 1.
- [ ] **Phase 5** — standalone retrofitting policy note.

## Open questions

- **Realistic primary venue?** *Real Estate Economics* or *JUE* as the honest primary,
  with *RFS*/*JFE*/*Management Science* as the stretch — vs. calibrating to the stretch
  directly. This gates Tier-2 exemplar selection and the aggressiveness of the front
  matter.
- **Citation gap:** is Bourveau, Garel & Petit-Romec, "Mandatory Carbon Disclosure:
  Evidence from France" in our bibliography? Mandatory environmental disclosure in a
  French setting is a near-neighbour of this paper and should be cited regardless.
