# Plan — Run the humanizer plugin on every prose section of the paper, with a full audit trail and a micro-theorist cross-check

**Status:** DRAFT · 2026-10-30 · branch `review`. Supersedes the earlier plan under this name (new proposition + proof rewrite, COMPLETED). Nothing is executed yet.

## Context

The project's own `/humanize` skill and `humanize-auditor` agent were removed on 2026-10-30; the `humanizer` plugin (blader/humanizer v3.1.0, 26 patterns, answers to `/humanizer:humanizer`) is installed but is only loaded in a new session. Bastien wants it run on every section of the paper, wants every change tracked so he can check whether the content changed, and wants a final cross-check with the micro-theorist.

Constraints that shape the design:
- **The plugin rewrites.** In its "file mode" it overwrites the file. That conflicts with `writing-with-ai.md` and `proofreading-protocol.md` (propose, then approve, then apply). Decision: **propose-then-approve**; the manuscript never changes without Bastien's sign-off.
- **It is built for plain text, not LaTeX.** It keeps code blocks, paths and link targets, but says nothing about math, `\cite`/`\ref`, `\att…` macros, labels, or `% [AUTHOR REWRITE]` markers, and it may merge, split or shorten paragraphs and drop hedges (its pattern 9 "stacked qualifiers"). Hedges and quantifiers here are claims (e.g. "at most", "only if", "may", "set-identified"), so each change must be checked for meaning.
- **It does not defeat AI detectors** (its README says so). The provenance caveat in `writing-with-ai.md` stands, and `/submission-disclosures` still applies.
- The working tree has ~120 uncommitted changes, so "before" must be a snapshot, not `git diff HEAD`.

## Decisions (Bastien, 2026-10-30)

- **Apply mode:** propose, approve, then apply (per paragraph).
- **Baseline:** archive snapshot with SHA-256 manifest (no commit).
- **Scope:** all prose; skip equations, theorem/lemma/definition/corollary statements, proofs, tables, and passages marked `% [AUTHOR REWRITE]`.
- **Execution:** one fresh-context subagent per section, in parallel.
- **Final cross-check:** micro-theorist, after everything is applied.

## What is in scope (inventory from the repo)

| Unit group | File | Notes |
|---|---|---|
| Abstract | `main.tex` (`\abs{…}`) | contains inline `% [AUTHOR REWRITE]` markers |
| §1 Introduction | `sections/01-introduction-draft.tex` (251 lines) | |
| §2 Unraveling | `sections/02-unraveling-draft.tex` (114) | shortest, used as the pilot |
| §3 Setting and data | `sections/03-setting-draft.tex` (248) | |
| §4 Core model | `sections/04-structural-draft.tex` (596) | many equations and propositions |
| §4.6 Attention | `sections/04-attention-draft.tex` (470) | prose between propositions only |
| §5 Policy + Conclusion | `main.tex` lines ~64–385 | tables and propositions excluded |
| Appendices | `sections/A-robustness.tex` (264); `sections/A-attention.tex` non-proof prose (715 lines); `main.tex` appendices (Data/Model objects, figure notes) | proofs excluded |
| Footnotes, figure/table notes and captions | everywhere | extracted as their own units |

Protected (never sent to the plugin, never changed): math and equation environments; `proposition|lemma|corollary|definition|assumption|remark` statements; `proof` bodies; `tabular` bodies; `\cite*`, `\ref`, `\eqref`, `\label`, `\att…` macros; `\input`/`\includegraphics` paths; `% [AUTHOR REWRITE]` markers with the paragraph they introduce (through the next blank line); `% [CHECK]` comments.

## Phases

**Phase 0 — Prepare (no manuscript edits).**
1. *Baseline snapshot:* copy `paper-real-estate/main.tex`, `sections/*.tex`, `results/tables/attention_macros.tex` and `attention_mc_macros.tex` to `quality_reports/humanizer/baseline_2026-10-30/` with `MANIFEST.sha256`, a README (what it is, why, what replaced it, per `repo-hygiene.md`), `baseline_text/` (pdftotext of the compiled paper) and `baseline_stats.json` (page count, words per file, macro-use counts, label/cite/ref sets). The 14 MB PDF itself is not stored (hygiene).
2. *Inventory:* `units.csv` — one row per prose unit (file, section, baseline line range, word count, protected spans) built by a parser.
3. *Tooling:* one script, `scripts/humanizer_tools.py` (flagged as new tooling, requested by "keep track of everything"; no external deps): `mask` (replace protected spans by stable placeholders ⟦M1⟧, extract footnote bodies as separate units), `unmask`, `verify` (the gates below), `ledger`, `diffs`. **Gate before anything runs:** mask → unmask is byte-identical for every unit of the baseline.
4. *Load the plugin:* start a new session (or `claude --plugin-dir`), smoke-test `/humanizer:humanizer` on one masked paragraph. If it can't load, fall back to a subagent that applies the plugin's `SKILL.md` patterns by hand (flagged in the ledger).

**Phase 1 — Pilot on §2 (shortest file).** Run the full pipeline on `02-unraveling-draft.tex` only, show Bastien the ledger, the diffs and the approval sheet, and adjust masking and instructions (technical-text mode: no added opinions or examples, keep hedges unless he approves) before the fan-out.

**Phase 2 — Fan-out, one subagent per section** (about 8: abstract + §1; §2 if not already done; §3; §4 core; §4.6; §5 + conclusion; appendices prose; footnotes/captions). Each agent, for every unit in its range, with a fresh context: masked text → plugin → unmask → write `runs/<section>/<unit>.before.tex`, `.after.tex`, `.diff`; run `verify`; add ledger rows. **No agent edits the manuscript** and none sees another agent's output. Instruction to every agent: technical, neutral register; do not add facts, numbers, examples or reactions; preserve placeholders exactly; keep the plugin's pattern numbers it applied.

**Hard gates per unit** (a failure marks the unit REJECT-CANDIDATE, never silently dropped):
- G1 placeholder multiset identical (math, cites, refs, labels, macros);
- G2 every numeric token preserved with the same count;
- G3 sets of `\ref`/`\eqref`/`\cite*`/`\label` keys equal;
- G7 `% [AUTHOR REWRITE]` and `% [CHECK]` counts equal.

**Flag gates (human review, not auto-reject):**
- G4 claim-strength lexicon diff: modals (may, might, could, can, must), negations, quantifiers (all, every, any, some, most, only, at least, at most, exactly, if and only if), hedges (suggest, imply, consistent with, bound, set-identified, upper bound), with before/after context;
- G5 size and novelty: word/sentence delta (flag >25% shrink), new content words not in the baseline paragraph, merged or split paragraphs.

**Phase 3 — Approval (Bastien), then apply.**
1. `review/<section>.md` approval sheets, ordered by risk (gate failures and G4 flags first), each block: id, baseline lines, before, after, patterns, gate results, a one-line change type (none / cosmetic / structural / content-risk).
2. Bastien accepts, rejects or edits per unit; decisions are recorded in `ledger.csv`/`LEDGER.md`.
3. Apply only accepted units with Edit, each guarded by an exact-match check against the baseline paragraph hash (detects drift since the snapshot). After each section: `latexmk` (0 errors, 0 undefined, page count noted), macro-use counts equal, G3/G7 re-checked on the real file.
4. Ledger columns: unit, file, lines, words before/after, patterns, G1–G5, change type, decision, reviewer note, applied (y/n), applied date.

**Phase 4 — Cross-check with the micro-theorist (after all sections are applied).** Fenced per `review-fencing.md`: neutral copies of the baseline and final text outside the checkout, with no ledger, no decisions and no plugin rationale. Tasks:
1. a **programmatic** check that all non-prose regions (equations, statements, proofs, tables, macros, labels) are byte-identical between baseline and final: the diff must be empty;
2. for every changed unit, an independent classification of meaning: identical / weaker / stronger / different, quoting the exact words that differ;
3. checks of references to the changed text from elsewhere ("the first case", "as in Section 4.3", ordering words, enumerations promised then delivered);
4. a structured table; I reconcile it against the ledger. Any unit it rates weaker, stronger or different than the ledger's "cosmetic" is reverted or sent back to Bastien. Findings are treated as candidates and verified against the source before acting (adjudicate-review discipline).

**Phase 5 — Close.** `SUMMARY.md` (counts: units, accepted, rejected, edited, flagged, reverted; patterns most frequent), final snapshot `final_<date>/` with manifest, final compile, backtest unchanged versus the clean-HEAD failures, session log entry, `[LEARN]` entry if the plugin did something unexpected (for example on dashes or LaTeX quotes).

## Directory layout (all under `quality_reports/humanizer/`, README at the top)

`README.md` · `baseline_2026-10-30/` (sources, `MANIFEST.sha256`, `baseline_text/`, `baseline_stats.json`) · `units.csv` · `ledger.csv` + `LEDGER.md` · `runs/<section>/…` · `review/<section>.md` · `CROSSCHECK.md` · `SUMMARY.md` · `final_<date>/`.

## Risks and how the plan handles them

- **Hedges and quantifiers get dropped** (pattern 9, pattern 6): G4 flag plus the micro-theorist's meaning classification.
- **Plugin edits LaTeX syntax** (curly quotes, `---`, `~`, `\ `): masking plus G1; dash and quote changes are listed as their own flag.
- **Paragraphs merged or split:** G5; the apply step works on baseline paragraph hashes.
- **Drift between snapshot and live files:** exact-match guard at apply time.
- **Provenance:** the pass improves readability, not detectability; the AI-use disclosure is unaffected.
- **Plugin not loadable:** fallback documented in Phase 0.

## Critical files

New: `scripts/humanizer_tools.py`, `quality_reports/humanizer/**`. Modified only in Phase 3 and only for accepted units: `paper-real-estate/main.tex`, `sections/01-introduction-draft.tex`, `02-unraveling-draft.tex`, `03-setting-draft.tex`, `04-structural-draft.tex`, `04-attention-draft.tex`, `A-robustness.tex`, `A-attention.tex`. No change to results, macros, bib or figures.

## Verification (success criteria)

mask/unmask round-trip is the identity on the whole baseline; every applied change has a ledger row with an explicit decision; zero hard-gate failures among applied units; non-prose regions byte-identical between baseline and final; compile clean with macro-use counts unchanged; micro-theorist report has zero unresolved weaker/stronger/different items; backtest result unchanged versus clean HEAD.
