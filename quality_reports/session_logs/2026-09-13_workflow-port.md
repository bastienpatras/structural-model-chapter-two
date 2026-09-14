# Session log — 2026-09-13: workflow port from rental-disclosure-claude

## Goal

Port the Claude Code academic workflow (`.claude/`, `CLAUDE.md`, `templates/`, `scripts/`,
`MEMORY.md`) from `rental-disclosure-claude` into this repo, curated for a solo Python + LaTeX
JMP paper project (no Beamer/Quarto/lecture materials). Full rationale in
`rental-disclosure-claude`'s `quality_reports/plans/floating-bouncing-otter.md`.

## What changed

- New `CLAUDE.md`, `MEMORY.md` (seeded), `.claude/settings.json` (hook wiring only — no
  `bypassPermissions`, per user's explicit choice), `.githooks/pre-commit` (quality-score step
  removed, deferred).
- Curated port of `.claude/{rules,references,agents,hooks,output-styles,skills}`, `templates/`,
  `scripts/` — see the plan for the keep/drop table.
- `scripts/check-repo-hygiene.py`: `ROOT_ALLOW`/`ROOT_ALLOW_DIRS`/`ARCHIVE_DIRS` adapted to this
  repo's actual root listing.
- `scripts/check-surface-sync.py`: `SURFACES` trimmed — the upstream `guide/`/`docs/` GH-Pages
  files don't exist here.
- Mid-session addition (user request): `python-reviewer` and `python-package-reviewer` agents,
  `.claude/rules/python-{code,package}-conventions.md`, and `/review-python` +
  `/python-package-check` skills — Python analogues of the template's R reviewer agents/rules/
  skills, since this repo's own code is Python. `CLAUDE.md` updated to reference them.
- Restored (initially dropped, restored once link-checking showed how heavily cross-referenced
  they are): `r-code-conventions.md`, `r-package-conventions.md`, `stata-code-conventions.md`,
  `simulation-conventions.md`, `pdf-processing.md` (path scope adapted to
  `paper-real-estate/corpus/**`), `stata-replication/` and `simulation-study/` skills. Kept as
  reference/cross-language material, not because this repo uses R/Stata.
- Fixed ~40 dangling relative links left by the curated drop (mostly `meta-governance.md`,
  `qa-quarto`, `domain-reviewer.md` mentions) by editing the referencing text — see diff.
- `quality_reports/qualification/LEDGER.md` seeded with a "Not yet qualified" debt table (the
  ledger-coverage gate requires this heading to run at all).

## Decisions made (asked, not assumed)

- Institution: Sciences Po.
- Curated port (not full/verbatim) — confirmed via `AskUserQuestion`.
- Quality gates (80/90/95 numeric rubric) deferred, not adapted — confirmed.
- Permission mode: kept default (prompted), did **not** adopt `rental-disclosure-claude`'s
  `bypassPermissions` — confirmed via `AskUserQuestion`.

## What was tried and abandoned

- Initially dropped all R/Stata/simulation-study conventions/skills per the "curated, Python-only
  project" plan. `check-links.py` showed 42 broken references — most pointed at these files from
  otherwise-generic reference docs. Rather than hand-editing a dozen substantive skill files to
  strip live methodology sections, restored the five cheap, harmless files instead (see above).
  `meta-governance.md`, `domain-reviewer.md`, and `qa-quarto/SKILL.md` were **not** restored
  (genuinely inapplicable — public-template framing, lecture-specific, Quarto-specific
  respectively) — their ~10 referencing mentions were edited instead.

## Verification

- `./scripts/backtest.sh`: surface-sync, skill-integrity, model-versions, spec-conformance,
  staleness all clean. `links`: 1 broken reference remains, in a **pre-existing** file
  (`.claude/agent-memory/structural-micro-reviewer/MEMORY.md`, predates this port) — not fixed,
  out of scope. `repo-hygiene`: 12 violations, all **pre-existing** tracked build artifacts under
  `paper/` and `out/` — flagged in `CLAUDE.md`, not fixed (would touch the user's tracked paper
  files without being asked). `ledger-coverage`: 9 failures, all "not tracked by git yet" — will
  resolve once these new files are committed (not done automatically). `hook-battery`: 17/234
  self-test failures — re-ran the identical suite in the original `rental-disclosure-claude`
  checkout and got the same 17 failures, confirming pre-existing environment flakiness, not a
  porting defect.
- `git status`: confirmed only additive new files under the ported directories; the 22 pre-existing
  modified files (regenerated data/figures/results, `.DS_Store`) are untouched, and
  `.claude/settings.local.json`'s three original permission entries are intact.

## What remains / next step

Phase B (review + humanize `paper-real-estate/`) gets its own plan-mode pass, per the approved
plan — not started this session.
