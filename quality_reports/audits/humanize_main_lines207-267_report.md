# `/humanize` Detection Report

**File:** `paper-real-estate/main.tex`
**Scope:** lines 207–267 — `\subsection{Renovation Subsidies in French Housing Markets: Empirical Magnitudes and Spatial Heterogeneity}` (§5.5)
**Date:** 2026-09-21
**Mode:** detect-only (per `.claude/rules/writing-with-ai.md` — no edits made)

Five prose paragraphs (211, 224, 248, 250, 265) plus four figure blocks (213–222, 226–235,
237–246, 252–263) were audited against all 10 canonical categories, plus a separate check for
the "statement: elaboration" colon tic flagged in earlier passes on this paper.

## Headline finding

Categories 2, 5, 6, 7, 8, 10 are fully clean: no AI-cliché lexicon, tricolon abuse, hedging
stacks, "not only/but also" frames, formulaic openers, or sycophancy anywhere in this section.
The colon-elaboration tic is the dominant, systematic pattern: **9 instances across all 5 prose
paragraphs** — every paragraph in the section has at least one. Hyphenation density is high but
mostly load-bearing technical vocabulary (cost-sharing, verified-quality premium, cross-market,
partial-pooling), not filler.

## Per-category counts

| Category | HIGH | MED | LOW |
|---|---|---|---|
| 1. Boilerplate transitions | 0 | 0 | 1 |
| 2. AI-cliché lexicon | 0 | 0 | 0 |
| 3. Em-dash/punctuation overuse | 0 | 0 | 2 |
| 3b. Colon-elaboration tic (tracked separately) | 9 | — | — |
| 4. Symmetric paragraph shapes | 0 | 0 | 1 |
| 5. Tricolon abuse | 0 | 0 | 0 |
| 6. Hedging stacking | 0 | 0 | 0 |
| 7. "Not only X, but also Y" | 0 | 0 | 0 |
| 8. Formulaic openers | 0 | 0 | 0 |
| 9. Hyphenation excess | 1 | 4 | 0 |
| 10. Sycophancy/self-importance | 0 | 0 | 0 |

## Findings

### Colon-elaboration tic (all HIGH, 9 instances — every prose paragraph)

| Line | Current text | Suggested rewrite |
|---|---|---|
| 211 | "...scales with the local price level: high-price urban markets have the largest verified-quality premia in absolute terms" | "...scales with the local price level. High-price urban markets have the largest verified-quality premia in absolute terms" |
| 211 | "Cross-market dispersion nonetheless remains substantial: apartment thresholds range from roughly €4 to €253/m²" | "Cross-market dispersion nonetheless remains substantial. Apartment thresholds range from roughly €4 to €253/m²" |
| 224 | "...has a direct programme-design implication: a commitment to a fixed cost-sharing rate is more defensible than a commitment to a fixed euro amount" | "...has a direct programme-design implication. A commitment to a fixed cost-sharing rate is more defensible than a commitment to a fixed euro amount" |
| 224 | "...is the natural decision variable for the regulator: among markets requiring support, the mean stands at 54.0% for apartments" | "...is the natural decision variable for the regulator. Among markets requiring support, the mean stands at 54.0% for apartments" |
| 248 | "...is correspondingly uniform in structure across markets: the renovation threshold is pinned at the verified-quality premium everywhere" | "...is correspondingly uniform in structure across markets. The renovation threshold is pinned at the verified-quality premium everywhere" |
| 250 | "Both forms of misallocation are costly: the former through fiscal waste on infra-marginal markets, the latter through forgone renovations" | "Both forms of misallocation are costly, the former through fiscal waste on infra-marginal markets and the latter through forgone renovations" |
| 250 | "...also points to the co-targeting logic of §5.2: markets with small bubbles are typically markets with low verification penetration π" | "...also points to the co-targeting logic of §5.2. Markets with small bubbles typically have low verification penetration π" |
| 265 | "That multiplier is the headline fiscal fact: it implies that any credible decarbonisation programme...must either substantially expand the fiscal envelope" | "That multiplier is the headline fiscal fact. It implies that any credible decarbonisation programme...must either substantially expand the fiscal envelope" |
| 265 | "...establishes that $S^*_m$ is an incentive-compatibility object rather than a Ramsey-optimal transfer: with a shadow cost of public funds λ>1, the regulator will set the operative subsidy below $S^*_m$" | "...establishes that $S^*_m$ is an incentive-compatibility object rather than a Ramsey-optimal transfer. With a shadow cost of public funds λ>1, the regulator will set the operative subsidy below $S^*_m$" |

Figure-caption colons (e.g. "Top row: ... Bottom row: ...", "Benchmarks shown: ...") are
excluded — those are list/label-style caption conventions, not the sentence-level tic.

### Em-dash overuse (LOW, 2 instances)

| Line | Current text | Note |
|---|---|---|
| 248 | "$\beta_{1,m}$ and local prices --- not by any regime-composition effect" | acceptable, 1/paragraph |
| 250 | "...the energy-efficiency premium $\beta_{1,m}$ itself is large --- the latter reflecting the capitalised value of verified quality" | acceptable, 1/paragraph |

### Hyphenation excess (MED×4, HIGH×1)

| Line | Severity | Note |
|---|---|---|
| 211 | MED | ~8 instances, mostly necessary model terminology |
| 224 | MED | ~8 instances; "cost-sharing" repeats 3× in one paragraph |
| 248 | MED | 4 instances in 2 sentences, highest per-word density in the section |
| 250 | **HIGH** | ~20 instances, densest paragraph in the section; "cost-sharing" alone repeats 5× |
| 265 | MED | ~11 instances; "verified-quality-premium gap" is a genuinely awkward triple-stacked compound — consider "the gap between the verified-quality premium and..." |

Nearly all of these are the paper's own necessary technical vocabulary, not filler adjective
chains — flagged for completeness, low priority to touch except the noted "cost-sharing"
repetition and the one triple-stacked compound.

### Symmetric paragraph shapes (LOW, substantively motivated)

Lines 211/224/265 share a recurring "apartment stat → house stat → synthesizing sentence"
rhythm, but this is not a true AI tell here: the paper structurally reports two property types
× two cost benchmarks throughout the section, so the parallelism is substantively motivated by
the data structure, not templated filler.

### Boilerplate transitions (LOW, 1 instance, benign)

Line 265, "More fundamentally, Remark~\ref{rem:welfare} establishes..." — not a clichéd AI
transition (no "Moreover/Furthermore/It is important to note/In conclusion" anywhere in the
section); no action needed.

## Top 3 most concentrated paragraphs

1. **Line 250** (the "uniform national subsidy" paragraph, ~430 words) — 2 colon-elaboration
   tics, 1 em-dash, ~20 hyphenated compounds ("cost-sharing" alone repeats 5×). Highest raw
   finding count in the section.
2. **Line 265** (the aggregate fiscal-cost paragraph, ~230 words) — 2 colon-elaboration tics,
   ~11 hyphenated compounds, including the triple-stacked "verified-quality-premium gap."
3. **Line 248** (the "policy challenge is uniform" paragraph, ~85 words) — 1 colon-elaboration
   tic, 1 em-dash, 4 hyphenated compounds in two sentences — shortest paragraph, highest density
   per word.

## Action recommendation

The colon-elaboration tic is the single most fixable, highest-value target: 9 instances, one in
every prose paragraph, each a mechanical "statement: elaboration" split that becomes a plain
two-sentence structure with no loss of content (table above gives a ready rewrite for each).
Everything else in this section is either clean (6 of 10 categories) or low-priority technical
vocabulary that doesn't need touching, aside from the "cost-sharing" repetition in lines 224/250
and the one awkward triple-stacked compound at line 265.

This is a detect-only report per `.claude/rules/writing-with-ai.md`; no edits were made to the
audited file.
