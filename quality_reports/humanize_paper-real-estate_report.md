# Humanize Audit: `paper-real-estate-humanized` (5 scoped targets)

**Targets audited:**
1. `paper-real-estate-humanized/sections/01-introduction-draft.tex` (full file)
2. `paper-real-estate-humanized/sections/02-unraveling-draft.tex` (full file)
3. `paper-real-estate-humanized/sections/03-setting-draft.tex` (full file)
4. `paper-real-estate-humanized/sections/04-structural-draft.tex` (full file)
5. `paper-real-estate-humanized/main.tex`, `\section{Policy Extension: Renovation Subsidies}` + `\section{Conclusion}` only (lines ~57–305; appendix/figures excluded)

No `voice-profile.md` exists at the repo root, so no documented-voice exemptions apply — everything below was checked against the SKILL.md's 10 categories directly.

---

## Caveat — read before acting on this report

A clean result here is a claim about **readability**, not about **provenance**. Per
[`.claude/rules/writing-with-ai.md`](/Users/bpatras/structural-model-chapter-two/.claude/rules/writing-with-ai.md):
neural AI-text detectors like Pangram classify on token-level generation statistics that persist
through *any* transformation a model applies to its own output — em-dash removal, cliché-lexicon
stripping, transition-varying, all of it. A manuscript can score zero surface tells under this
audit and still return "100% AI-written" from a real detector, because **a model cannot make its
own output stop reading as model output.** If provenance matters for a venue's AI-use policy, the
only path is (a) genuine human rewriting of the load-bearing prose, and (b) measuring against an
actual detector, not this report. Treat everything below as copy-editing signal, not a
provenance fix.

---

## Word count (approximate)

| File | Approx. words |
|---|---:|
| 01-introduction-draft.tex | ~2,100 |
| 02-unraveling-draft.tex | ~1,450 |
| 03-setting-draft.tex | ~3,300 |
| 04-structural-draft.tex | ~4,700 |
| main.tex (Policy Extension + Conclusion only) | ~3,350 |
| **Total scoped** | **~14,900** |

**Findings:** 2 (0 HIGH, 1 MED, 1 LOW)

## Per-category summary

| Category | HIGH | MED | LOW |
|---|---:|---:|---:|
| 1. Boilerplate transitions | 0 | 0 | 0 |
| 2. AI-cliché lexicon | 0 | 0 | 0 |
| 3. Em-dash / punctuation overuse | 0 | 0 | 0 |
| 4. Symmetric paragraph shapes | 0 | 1 | 0 |
| 5. Tricolon abuse | 0 | 0 | 0 |
| 6. Hedging stacking | 0 | 0 | 0 |
| 7. "Not only X but also Y" | 0 | 0 | 0 |
| 8. Formulaic openers | 0 | 0 | 1 |
| 9. Hyphenation excess | 0 | 0 | 0 |
| 10. Sycophancy / self-important framing | 0 | 0 | 0 |

Categories 1, 2, 3, 5, 6, 7, 9, 10 returned **zero** matches across all five targets on
pattern-based checks (boilerplate connectors, the AI-cliché lexicon, em-dash counts, hedge-stack
phrasing, "not only…but also", hyphenation clusters, sycophantic self-framing) plus manual
paragraph-by-paragraph reading. Tricolons in this manuscript ("renovation subsidies, enforcement
against concealment, and investment in audit coverage"; the three seller strategies in
Table~\ref{tab:strategies}) are **substantively fixed at three real objects** (the model literally
has three instruments / three strategies), not decorative padding — per the SKILL's own guidance
("Tricolons used for items that could naturally be 2 or 4"), these do not qualify as findings.

## Findings

| Line | Cat | Sev | Current text | Suggested |
|---:|---|---|---|---|
| `03-setting-draft.tex:19-20` | 8 | LOW | "This section sets out the institution, the data, and four features of the market that any candidate theory of EPC disclosure has to accommodate." | Cut the meta-announcement; let the subsection headers (§3.1 Institutional Background, §3.2 Data and Measurement, §3.3 Stylized Facts) carry the roadmap. E.g., trim to: "Four features of this market discipline any candidate theory of EPC disclosure." (single mention across ~14,900 words — flag is for awareness, not urgent) |
| `03-setting-draft.tex:126-247` (§3.3.1–§3.3.4, `ss:fact1`–`ss:fact4`) | 4 | MED | Four consecutive subsections each open with a claim sentence, present a figure as evidence, and close with an interpretive sentence tying back to classical unraveling (e.g. ¶fact1 closes "Classical unraveling predicts the opposite sign…"; ¶fact2 closes "…indicating that a substantial fraction of sellers cannot disclose…"; ¶fact4 closes "This heterogeneity rules out a national-level treatment…") | Likely domain-legitimate — a numbered "stylized facts" section with one figure per fact is standard empirical-paper architecture, not a generic LLM artifact. If variation is wanted: break the closing-sentence formula in one subsection, or vary how each subsection returns to the theory (one could open with the theoretical prediction instead of closing with it). Author's call — mark LOW-to-MED, not urgent. |

## Concentration

No meaningful concentration. The two findings above sit in different subsections of a single
file (`03-setting-draft.tex`); no 3+ finding paragraph windows exist anywhere in the scoped
corpus. This is not a "top 3 paragraphs" situation — the manuscript is close to flat.

## Out-of-scope note (flagging only, not a humanize finding)

`main.tex` line ~301 (Conclusion) contains a corrupted/duplicated sentence fragment: *"...5.7\%
of house sellers do.7\% of house sellers do so."* This reads as a text-merge artifact (likely from
an edit that didn't fully overwrite the prior sentence) and needs a proofreading fix — it is a
grammar/text-integrity defect, not a voice tell, so it is outside this agent's scope. Route it to
`/proofread` before the next compile. **Independently confirmed** by the `editor` agent's desk
review the same session (`quality_reports/peer_review_paper-real-estate/desk_review.md`,
item 1 of the internal-consistency cluster) — two independently-fenced reviewers landed on the
same defect without seeing each other's output.

## Recommendation

**~0 HIGH findings per 1000 words** across all five targets → this reads as a clean pass; no
rewrite or systematic tell-stripping is warranted. The manuscript shows essentially no trace of
the classic LLM surface patterns (boilerplate connectors, cliché lexicon, em-dash/semicolon
overuse, hedge-stacking, "not only...but also", sycophantic self-framing) — consistent with the
repo's own commit history showing a prior deliberate pass (`ee0e311 style: remove the
colon-as-hinge construction from all authored prose`). The two findings recorded here are minor
and arguably discretionary: the single formulaic section-opener in §3 (cosmetic, one instance in
~14,900 words) and the four-subsection "stylized facts" cadence (very plausibly intentional,
discipline-standard empirical-paper structure rather than an AI artifact). Neither is
load-bearing; if you fix only one thing from this pass, fix the out-of-scope Conclusion text
corruption noted above via `/proofread`, since that is an actual reading-experience defect and
the two humanize findings are not.
