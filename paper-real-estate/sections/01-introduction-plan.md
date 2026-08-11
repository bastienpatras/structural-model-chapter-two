# §1 Introduction — paragraph plan

Protocol step 2: structure before prose. Nothing here is drafted yet. Review, correct, then
I draft.

Current draft is 9 paragraphs; target is 14. The count rises because paragraphs currently
doing three or four jobs get split, and six missing conventions get their own paragraph.

## The central framing proposal

Unraveling requires four assumptions. Enumerate them, then note that **this paper's data
converts one of them from an assumption into a measurement**, and isolate a different one as
the contribution:

| | Assumption | Status in our setting |
|---|---|---|
| (a) | Buyers know sellers possess private information about quality | **We do not assume this — we measure it.** The ADEME match observes which sellers hold an audit. 48.8% of apartment sellers genuinely do not |
| (b) | Disclosure is costless | Plausibly near-satisfied — a DPE is a bounded, one-off outlay *(figure needed, see gaps)* |
| (c) | Disclosure is credible | Strongly satisfied — DPE certification is third-party and legally opposable post-2021 |
| (d) | **Buyers are homogeneous in how much they value the disclosed signal** | **The assumption at stake.** ρ_m, the share of EPC-sensitive buyers, is the object we estimate |

This is a stronger position than the current draft, which argues for departures from *both*
(a) and (d) in adjacent paragraphs, diluting each. Recasting (a) as a measured feature of the
setting and (d) as the theoretical contribution gives one clean target, and it foregrounds
the data contribution — the vantage point becomes the reason (a) needs no defence.

## Paragraph plan

| ¶ | Job | Source | Status |
|---|---|---|---|
| 1 | Unraveling's prediction; the French market contradicts it. No first-person claims, no own findings yet | current ¶1, trimmed | Rework — move own numbers to ¶7 |
| 2 | *"To learn about X, we examine Y"* — France's 2021 *loi Climat et Résilience*, what changed legally, why it is a testbed | §3.1/§5.1 material, currently buried | **New in intro** |
| 3 | What unraveling predicts *in this market*; why France can adjudicate it | partly current ¶1 | New |
| 4 | **The assumption audit** (a)–(d) per the table above | current ¶3 + ¶4, restructured | Rework — enumerate |
| 5 | Isolate (d): buyer heterogeneity in EPC sensitivity is the under-examined joint | current ¶4 tail; Loewenstein, Ben-Shahar, Fishman cites | Rework |
| 6 | Data and vantage point: three sources, ADEME match, four groups | current ¶6 | **Keep nearly as-is** — strongest paragraph. Remove the `$K$` notation |
| 7 | Descriptive findings, enumerated: *First… Second… Third… Fourth…* | §2's four stylized facts | **New in intro** |
| 8 | Model motivation: *"a model that allows for, but does not impose, strategic concealment"*; mechanism in plain language | current ¶5, first half | Split from ¶5 |
| 9 | What the model finds: ρ̂, ĉ₀, σ̂₁ = 0 across all markets, and the invariance result | current ¶5, second half | Split from ¶5 |
| 10 | Robustness previewed + nested-model fit comparison | — | **New — see gaps** |
| 11 | *"Our paper contributes to the disclosure literature by…"* | implicit now | New |
| 12 | *"Our paper provides a new information-based account of the energy-efficiency gap…"* + scope disclaimer | current ¶7–¶8 | Rework |
| 13 | *"Related to and borrows from several strands"* — three strands | scattered | New |
| 14 | Generalizability conceded, then defended | — | **New**; replaces the roadmap |
| — | Roadmap | current ¶9 | **Delete** |

### Three strands for ¶13

1. Structural estimation of disclosure models
2. Energy-label capitalisation in housing — Brounen & Kok, Hyland & Lyons, Fuerst, Frondel,
   Myers, all already cited
3. Information asymmetry in real-estate markets — Levitt & Syverson, Lizzeri, already cited

## Gaps needing your input before I draft

1. **¶4(b), disclosure cost.** To argue disclosure is near-costless I need the DPE cost to a
   French seller — typical fee range and whether it is legally the seller's obligation. I will
   not invent a figure. What is the right number and source?

2. **¶10, the nested-model comparison.** The corpus treats this as the strongest defence of a
   structural specification: estimate the restricted model that shuts down your mechanism, and
   compare fit penalised for parameters. The natural restriction here is **ρ_m = 1 for all
   markets** — full EPC sensitivity, i.e. the classical homogeneous-buyer benchmark — against
   your estimated heterogeneous-ρ model. I have not yet checked whether anything like this
   exists in `src/estimation.py`. Three options:
   - implement it (new estimation work, strongest outcome)
   - substitute the existing pooled-hedonic comparison already in the paper
   - omit and accept the weaker position

   This is the one item that could add real work. Worth deciding early.

3. **¶9, which findings lead.** Your own review document argues σ̂₁ = 0 across all 140 markets
   is the paper's strongest result and is currently under-placed. I agree — it is a clean
   model-validation result of the kind this literature rewards. Should ¶9 lead with it?

4. **¶1 headline number.** Blocked on the `DIAGNOSIS.md` item: the abstract/intro/conclusion
   headline 7/3 log points cited to Chapter 1, while §2.1 reports 4.4/3.7. I need to know which
   number belongs in ¶1 and whether they are the same estimand.

## What I will not change without asking

The data/vantage-point paragraph, the four-group classification, and the Grossman/Milgrom
anchor. All three are already correctly pitched for this audience.
