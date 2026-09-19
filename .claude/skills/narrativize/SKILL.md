---
name: narrativize
description: Rewrite one or more sections of the active paper (paper-real-estate) — or the whole paper — into a narrative-first exposition. Focuses on the most important concept, argument, mechanics, and equations; converts dense mathematical exposition into readable prose, citing (not reproducing) complicated equations, proofs, and derivations that live in the appendix. Runs /humanize (detect-only) on the result and reports findings before finishing. Use when user says "narrativize this section", "make section X more readable", "turn this into a narrative", "this reads like a proof, not a paper", "too many equations, too much notation", "reduce the equation density", "rewrite this section in prose", or "clean up the prose in [section]". NOT for correcting math, adding content, or changing findings/numbers — it changes exposition only.
argument-hint: "<section|file|'all'> [, <section2>, ...] [--no-humanize]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Agent"]
effort: high
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /narrativize — Narrative Rewrite of a Technical Section

Turn a dense, equation-heavy passage into an interesting, readable narrative that still respects the paper's own rigor — by citing the appendix's formal propositions, lemmas, and proofs instead of re-deriving them in the main text. Built from a manual pass on `sections/04-structural-draft.tex`'s identification narrative (2026-09-15): cut display-equation count from 7 to 1, retitled three subsections from formula-names to descriptive ones, and moved every formal statement to an appendix citation — while preserving every number and finding verbatim.

**Core principle:** the main text carries the *story* — why an approach fails, what the fix buys, what it means economically. The appendix carries the *proof*. A reader should be able to follow the argument in the main text without needing the appendix open, and verify it precisely by turning there.

## When to use

- A section reads as a wall of equations and notation rather than an argument a reader can follow.
- You've just finished a technical/identification-heavy rewrite (by hand or by another skill/agent) and it needs a narrative pass before it's presentable.
- You want the whole paper, or several sections, brought to a consistent narrative register.

## When NOT to use

- To fix incorrect math or add new analysis — this skill only re-expresses content that is already correct; if the underlying derivation is wrong, fix that first (see `theory-proving.md`).
- To polish AI-voice tells in isolation — that's `/humanize` directly; this skill calls it as a final step, not a substitute for it.
- To rewrite the appendix's own formal propositions/proofs — those stay as rigorous statements; this skill only touches what cites them from the main text.

## Phases

### Phase 0 — Resolve the target scope

Parse the argument into a concrete file list:

1. A single section — resolve by file path (`sections/04-structural-draft.tex`) or by title/label the user names ("the identification section", "§4.3") — `Grep` for `\subsection{`/`\subsubsection{` titles to find it.
2. A comma-separated list of sections — resolve each the same way.
3. `all` / "the whole paper" — every file `\input{}`-ed from `main.tex`, in document order.

Echo back the resolved file(s) and, where the target is a subset of a file (e.g. three subsubsections, not the whole file), the exact subsection titles in scope — so a partial-file target doesn't silently expand to the whole file.

### Phase 1 — Read the target and the exemplar

For each target file:

1. Read the full target section(s) in context (the surrounding subsections too, not just the one being touched — tone should match its neighbors).
2. Identify a **style exemplar**: a nearby subsection in the *same* paper that is already prose-first and reads well (e.g. an institutional/motivation subsection, not a derivation-heavy one). Point the rewrite at it explicitly rather than an abstract style description.
3. Check whether the target already has a companion formal appendix (`sections/A-robustness.tex` or similar, `\label{app:...}`) it can cite. If dense derivations in the target have **no** appendix home yet, flag this — moving content requires a place to move it to; do not invent an appendix section as a side effect without saying so first.

### Phase 2 — Dispatch the rewrite

Dispatch each target section to the `micro-theorist` agent (it needs to understand the math well enough to know what's load-bearing versus what can be cited instead of reproduced). Brief it with, at minimum:

- The exact current text (or file + line range) of the section(s) in scope.
- The style exemplar identified in Phase 1, and an instruction to match its register.
- **Every number, finding, and claim in the current text must be preserved verbatim** — this is a re-expression pass, not a re-analysis. If the agent is unsure whether a number is still accurate, it keeps what's there rather than inventing a replacement.
- Cite complicated equations/proofs to the appendix (`\ref{}`/`\eqref{}` to existing labels) rather than reproducing them; keep at most the one or two equations a reader genuinely needs to follow the argument inline.
- No self-referential commentary about earlier drafts, prior versions, or what a previous pass said — the section is written as the only, definitive version.
- **Punctuation discipline: write plain sentences, not em-dash asides or "statement: elaboration" colon constructions.** Both are legitimate in moderation, but a narrative rewrite reaches for them by default and turns them into a mechanical tic — cap em-dashes at roughly one per paragraph (not a pair per sentence), and don't use a colon to bolt on an explanatory clause more than once every few sentences. When the instinct is "X: Y" or "X --- Y ---", prefer two sentences, or join them with "because"/"since"/"so"/"which" instead. This was found recurring at scale (17 colon-elaborations and 11 em-dashes in one ~135-line pass) and is now a standing constraint, not just a `/humanize` finding to report after the fact.
- Before finishing: check whether any equation/proposition label it deletes is referenced elsewhere in the paper (`grep -rn '\\ref{<label>}\|\\eqref{<label>}' main.tex sections/*.tex` from the paper root) and repoint or preserve accordingly — this is the single most common way a narrative pass silently breaks the paper.
- Compile-check after editing: `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`, run twice if needed to resolve forward references, and confirm no undefined-reference warnings remain in the log before reporting done.

### Phase 3 — Verify independently

Do not take the dispatched agent's self-report as sufficient. After it returns:

1. Re-run the compile check yourself if the agent's own report doesn't show a clean, current log.
2. `grep -rn "earlier draft\|previous draft\|an earlier version\|prior draft"` across `main.tex` and `sections/*.tex` — this skill exists partly because that pattern recurs; confirm zero hits in the touched files (and note, don't silently fix, any hits found *outside* the touched scope for a separate pass).
3. Spot-check that the numbers/findings in the rewritten section still match what was there before (diff mentally against the pre-rewrite read from Phase 1) — the rewrite should change exposition, not substance.
4. Check the rewritten prose for the punctuation tic the Phase 2 brief constrains against: count em-dashes (`grep -o -- '---'` on the touched lines) and eyeball colon-elaboration density paragraph by paragraph. More than ~3 em-dashes in one paragraph, or a "statement: elaboration" colon in most sentences of a paragraph, repeated across several consecutive paragraphs, is this skill's own defect re-appearing, not a broader AI-voice judgment call to defer to Phase 4 — fix it directly here (plain sentences, `because`/`since`/`so`) before moving on, the same way a broken cross-reference gets fixed directly rather than reported.

### Phase 4 — Humanize pass (mandatory unless `--no-humanize`)

Run `/humanize` on the rewritten section(s). This is **detect-only** — per `.claude/rules/writing-with-ai.md`, a model cannot make its own output stop reading as model-generated to a real detector, and auto-rewriting here would just produce differently-AI prose. Report the findings back to the user for them to act on; do not apply any of `/humanize`'s findings automatically, even ones that look mechanical.

## Output / report format

A chat report, not a new file:

- The resolved target file(s)/section(s) (Phase 0).
- What changed: equation count before → after, any subsections retitled, the style exemplar used, any cross-reference repairs made (Phase 2).
- Compile status (clean / issues found and fixed).
- The `/humanize` findings for the rewritten section(s), presented as-is for the author to address — not summarized away.

## Exit behavior

- **Rewrite done, compiles clean, humanize run:** report as above.
- **Target section has dense content with no appendix home to cite:** stop after Phase 1 and ask where it should go (a new appendix subsection, an existing one, or left inline) rather than deciding unilaterally.
- **Compile breaks and can't be resolved by repointing a cross-reference:** revert the edit (the file is already at a known-good state in git; do not leave the paper in a broken state) and report what broke.
- **`--no-humanize`:** skip Phase 4, note in the report that it was skipped and why (explicit user request).

## Flags

- `--no-humanize` — Skip the `/humanize` detect pass (Phase 4). Use only when the rewrite is a quick internal draft, not heading toward the next read-through.

## Cross-references

- [`/humanize`](../humanize/SKILL.md) — the detect-only AI-voice-tell pass this skill calls at the end; never auto-rewrites.
- [`.claude/rules/writing-with-ai.md`](../../rules/writing-with-ai.md) — why humanize is detect-only, and the human-readable-prose standard this skill is aiming at.
- [`.claude/references/theory-proving.md`](../../references/theory-proving.md) — the discipline for the *appendix* content this skill cites but never rewrites; an AI-derived proof is a claim, not a theorem, and stays out of this skill's scope.
- `micro-theorist` agent (`.claude/agents/` — repo-wide agent, not paper-scoped) — does the actual rewriting; this skill is the repeatable interface around dispatching it correctly and verifying its work.
- `realestate-finance-writing` — a global skill (`~/.claude/skills/realestate-finance-writing/`, not tracked in this repo) with the house-style reference for this exact paper's target journals; consult it for register questions this skill's exemplar-matching doesn't resolve.

## What this skill does NOT do

- **Fix incorrect math.** It re-expresses correct content; if the derivation itself is wrong, that's a `theory-proving.md`-governed fix, not this skill.
- **Auto-apply `/humanize` findings.** It reports them; the author edits.
- **Invent appendix sections to move content into.** It flags when a home is needed and asks, rather than creating one silently.
- **Touch numbers, findings, or claims.** Any change to substance is out of scope — if the rewrite reveals a substantive issue (a number that looks wrong, a claim that no longer holds), it is reported, not silently corrected.
- **Commit anything.** Branch/PR/merge is [`/commit`](../commit/SKILL.md)'s job.
