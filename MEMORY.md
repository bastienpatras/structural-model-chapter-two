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
