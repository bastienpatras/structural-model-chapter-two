# `/humanize` Detection Report

**File:** `paper-real-estate/main.tex`
**Scope:** lines 268–288 — `\section{Conclusion}`
**Date:** 2026-09-21
**Mode:** detect-only (per `.claude/rules/writing-with-ai.md` — no edits made)

Five prose paragraphs (271, 273, 275, 277, 279). Lines 268–270 are the section header/comment
rule; 280–288 are the appendix transition (`\clearpage`, `\appendix`, `\input{...}`) — no prose.

## Headline finding

Categories 1, 2, 6, 7, 10 are fully clean: no boilerplate transitions, cliché lexicon, hedging
stacks, "not only/but also," or sycophancy. **Zero em-dashes** anywhere in the section
(grep-confirmed against both Unicode U+2014 and the `---` LaTeX convention) — nothing to remove
on that axis this time. The colon-elaboration tic is again the dominant pattern: **10 instances
across all 5 paragraphs**, roughly 2 per paragraph. A structural-level tell also surfaced for the
first time in this paper: all 5 paragraphs share the same build → punchy-closing-line shape.

## Per-category counts

| Category | HIGH | MED | LOW |
|---|---|---|---|
| 1. Boilerplate transitions | 0 | 0 | 0 |
| 2. AI-cliché lexicon | 0 | 0 | 0 |
| 3. Em-dash overuse | 0 | 0 | 0 |
| 3b. Colon-elaboration tic (tracked separately) | 10 | — | — |
| 4. Symmetric paragraph shapes | 1 (whole section) | 0 | 0 |
| 5. Tricolon abuse | 0 | 0 | 1 |
| 6. Hedging stacking | 0 | 0 | 0 |
| 7. "Not only X, but also Y" | 0 | 0 | 0 |
| 8. Formulaic openers/closers | 0 | 1 | 1 |
| 9. Hyphenation excess | 2 | 1 | 0 |
| 10. Sycophancy/self-importance | 0 | 0 | 1 |

## Findings

### Colon-elaboration tic (all HIGH, 10 instances — every paragraph, ~2 each)

| Line | Current text | Suggested rewrite |
|---|---|---|
| 271 | "...silence is still rewarded: properties listed without an EPC score trade at a premium of 6.9 percent..." | "...silence is still rewarded. Properties listed without an EPC score trade at a premium..." |
| 273 | "First, not all sellers are informed: at listing time, only 51.8% of apartment sellers..." | "First, not all sellers are informed. At listing time, only 51.8%..." |
| 273 | "...they face genuine ambiguity: the non-disclosing seller may be concealing an unfavorable rating..." | "...they face genuine ambiguity. The non-disclosing seller may be concealing..." |
| 273 | "Neither departure alone is sufficient: uninformed sellers keep silence ambiguous, but buyer heterogeneity..." | "Neither departure alone is sufficient. Uninformed sellers keep silence ambiguous, but buyer heterogeneity..." |
| 275 | "...delivers the paper's central theoretical result: the non-disclosure premium equals exactly the concealment cost..." | "...delivers the paper's central theoretical result. The non-disclosure premium equals exactly..." |
| 275 | "The two segments concur less than an earlier reading of these facts suggested: concealment costs are 2.4%..." | "...suggested. Concealment costs are 2.4%..." |
| 275 | "Strategic hiding is itself uncommon: 15.2% of informed apartment sellers with unfavorable ratings withhold them..." | "Strategic hiding is itself uncommon. 15.2% of informed apartment sellers..." |
| 277 | "...causes that cost to cancel exactly in partial pooling: the renovation incentive reduces to the verified-quality premium..." | "...cancel exactly in partial pooling. The renovation incentive reduces to..." |
| 277 | "A uniform national subsidy exploits none of this structure: the minimum cost-sharing requirement ranges from zero..." | "A uniform national subsidy exploits none of this structure. The minimum cost-sharing requirement ranges..." |
| 279 | "...the mandate produces ambiguity rather than transparency: involuntary non-disclosers shelter strategic hiders..." | "...produces ambiguity rather than transparency. Involuntary non-disclosers shelter strategic hiders..." |

One additional colon (line 277, "The regulator faces three distinct instruments:") is a
legitimate list-introduction colon, excluded from the count above.

### Symmetric paragraph shapes (HIGH — spans the whole section)

All 5 paragraphs follow a build → punchy-closing-line shape: P271 closes "This paper resolves
the puzzle."; P273 closes with the "Neither departure alone is sufficient..." colon-tic
sentence; P275 closes "...the informed hider, in the segment where the model fits, merely
breaks even."; P277 has a mid-paragraph closer ("These are complements, not substitutes.") plus
a final one; P279 closes with the toolkit metaphor. Rated HIGH because the pattern spans all 5
consecutive paragraphs, not just a 3-paragraph window.

### Formulaic openers/closers

| Line | Severity | Text | Note |
|---|---|---|---|
| 279 | MED | "The broader lesson extends beyond energy labels." | Classic conclusion "zoom-out" opener — generic broadening move with no specific content of its own; consider naming the class of markets it generalizes to instead |
| 271 | LOW | "This paper resolves the puzzle." | Could fold into a more specific claim naming the resolution directly |

The section's actual opening sentence (line 271, "Four years after France mandated...") is
concrete, not formulaic — a good sign.

### Hyphenation excess

| Line | Severity | Note |
|---|---|---|
| 275 | HIGH | ~10 compound modifiers (partial-pooling, disclosed-price, registry-measured, energy-sensitivity ×2, energy-cost, non-disclosure ×2, ...) |
| 277 | HIGH | ~10 compounds (verified-quality ×2, high/low-quality, non-disclosure, audit-infrastructure ×2, cost-sharing); "audit-infrastructure investment" appears twice in two sentences |
| 279 | MED | 1 instance (non-disclosure) — flagged only for sitting at the tail of two HIGH paragraphs, not a problem in isolation |

### Categories with no findings

Boilerplate transitions, AI-cliché lexicon, hedging stacking, "not only/but also" (two milder
"not X but Y" antitheses at lines 275/279 don't meet this pattern's bar), and sycophancy (one
neutral descriptor at line 275, "the paper's central theoretical result," flagged LOW only
because conclusions get extra scrutiny on this category, not because it reads as a tell) are all
clean. Tricolon abuse: one legitimate tricolon at line 277, well under threshold.

## Top 3 most concentrated paragraphs

1. **Line 275** — 3 colon-tics, 2 semicolons (legitimate), HIGH hyphenation (~10 compounds), a
   contributing punchline close. Densest paragraph in the section.
2. **Line 277** — 2 colon-tics (+1 legitimate list colon), 1 tricolon, HIGH hyphenation
   (~10 compounds), mid-paragraph and final punchline closers.
3. **Line 273** — 3 colon-tics, the clearest instance of the topic→two-points→summary symmetric
   shape.

## Action recommendation

The colon-elaboration tic is again the single most fixable target: 10 instances, every
paragraph, each splitting cleanly into two sentences with no content loss (table above gives a
ready rewrite for each). No em-dashes to remove this time. The hyphenation density in
lines 275/277 is mostly the paper's own necessary vocabulary and lower priority; the one
genuinely worth touching is "audit-infrastructure investment" repeating twice in two adjacent
sentences at line 277.

This is a detect-only report per `.claude/rules/writing-with-ai.md`; no edits were made to the
audited file.
