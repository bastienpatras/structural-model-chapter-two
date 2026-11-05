# MEMORY.md

Generic, cross-session lessons about **how to work on this project** — workflow habits,
recurring corrections, things worth not re-learning. Committed, so it travels with the repo.

**What goes here:** `[LEARN:category] wrong → right` entries, saved when the user corrects an
approach or confirms a non-obvious one worked. Kept generic to this project's own workflow —
not a place for paper content, results, or findings (those belong in `paper-real-estate/`'s own
working notes, or in `quality_reports/`).

**What does NOT go here:** machine-specific paths, tool versions, or anything specific to one
laptop. That's native auto memory — Claude Code's built-in, machine-local memory at
`~/.claude/projects/<project>/memory/`, on by default, never committed. See
[`progress-reports.md`](.claude/rules/progress-reports.md) §3 for the promotion path from there
to here (`/promote-memory`).

**Size limit:** keep under 200 lines and 25KB — trim rather than let entries sprawl; a lesson
may be compressed but must not lose its evidence or its date (see `repo-hygiene.md`).

---

## Entries

- **[LEARN:workflow] (2026-09-14)** User wants contractor mode: once a plan is approved, execute
  autonomously and return only for genuine ambiguity or a real decision — not per-step
  confirmation. More frequent check-ins during the first few sessions while the workflow is
  being calibrated, tapering once corrections stop. All figures/maps route through
  `pyplot-specialist` / `cartopy-specialist` / `dataviz` rather than ad hoc plotting. Full policy:
  [`collaboration-mode.md`](.claude/rules/collaboration-mode.md).

- **[LEARN:review] (2026-10-30)** A prose-polishing plugin on technical text mostly finds nothing (167 of 218 units
  unchanged); the damage it can do is small and specific: it swaps a claim word ("robust" to "consistent"), narrows a
  scope phrase ("come to mind first" to "the natural"), and leaves a dangling "First," after deleting a signpost. Check
  with an independent fenced read (two copies, no ledger or rationale), then verify each finding against the source
  before acting: two of the readers' sixteen findings were overstated. Record: `quality_reports/humanizer/CROSSCHECK.md`.
- **[LEARN:tooling] (2026-10-30)** Never rewrite a CSV while iterating a `csv.DictReader` on the same path: the reader
  sees the truncated file and one row came back garbled. Read it into a list first, then write. A file lock does not
  help within one process. Also, subagents cannot write report files; have them return the report as text.
