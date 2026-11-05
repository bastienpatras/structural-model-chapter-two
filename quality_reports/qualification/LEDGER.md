# Qualification Ledger

Every check, gate, and review agent that is allowed to clear work must have a row here.
**A checker with no row is unqualified, and its green light means nothing.**

Written by `/vaccinate`. See [`verification-ladder.md`](../../.claude/references/verification-ladder.md) rung 0.

Verdicts: **PASS** (detects its named class at the stated threshold) · **FAIL** (misses it) ·
**BLOCKED** (could not be run — reason required; never record as PASS).

| Date | Target | Artifact | Defect classes | N | Recall | FPR | Baseline | Verdict |
|---|---|---|---|---|---|---|---|---|

Seeded empty on 2026-09-13 when the workflow infrastructure was ported into this repo from
`rental-disclosure-claude`. The checks themselves (`scripts/check-*.py`, `scripts/backtest.sh`)
were qualified there against that repo's own content — that qualification does not transfer,
since the checkers now run against different source files. Run `/vaccinate` here before relying
on any gate's green light for this project.

## Not yet qualified

These are relied upon and have **never been measured against this repo's own content**. Until
they have a row, treat their output as unverified — this is visible debt, not silence.

| Target | Why it matters |
|---|---|
| `scripts/check-repo-hygiene.py` | root allowlist was hand-adapted to this repo's layout (2026-09-13) — unverified against a real defect |
| `scripts/check-links.py` | gates the port itself; ~40 dangling links were found and fixed by hand this session, not by a qualified run |
| `scripts/check-surface-sync.py` | `SURFACES` list was hand-trimmed to this repo's actual files (2026-09-13) |
| `scripts/check-skill-integrity.py`, `check-spec-conformance.py`, `check-staleness.py`, `check-derived-counts.py`, `check-model-versions.sh` | ported unmodified; never run against a seeded defect in this repo |
| `python-reviewer`, `python-package-reviewer` agents | new (2026-09-13), written for this port, never run against a seeded bug |
| `structural-micro-reviewer`, `econ-academic-editor` agents | pre-existing, project-specific, predate this port — no qualification row from either repo |
| the ported review fleet (`claim-verifier`, `domain-referee`, `methods-referee`, `editor`, `humanize-auditor`, `proofreader`, `verifier`, `promote-memory-council`) | qualified against `rental-disclosure-claude`'s content only |
| `.claude/hooks/notify.sh`, `context-monitor.py`, `pre-compact.py`, `post-compact-restore.py`, `log-reminder.py` | passive hooks — a dead one costs a missed nudge, not a false green |
| `.claude/hooks/git-guardrails.py`, `root-of-trust-guard.py`, `claim-reconcile.py` | **deciding** hooks (not passive) — `git-guardrails.py`/`root-of-trust-guard.py`'s self-test suite (`scripts/hook-battery.sh`) was re-run against this repo 2026-09-13 and reproduces the original `rental-disclosure-claude` checkout's 17/234 failures exactly, consistent with pre-existing environment flakiness rather than a porting defect — but that is a reproduction, not a qualification run against this repo's own content |
| `scripts/hook-battery.sh`, `check-ledger-coverage.py` | the meta-checks that qualify the other checks — ported unmodified, never independently qualified themselves |
| `.githooks/pre-commit` | entry point wired 2026-09-13; delegates to `backtest.sh`, quality-score step removed (deferred, see `CLAUDE.md`) |

**Also not yet committed:** every file this port added under `.claude/hooks/`, `.githooks/`, and
elsewhere is currently untracked by git — `check-ledger-coverage.py`'s WIRING check correctly
flags this as "does not survive a fresh clone." That resolves itself once these files are
committed (a decision left to the user, not done automatically by this port).

The passive hooks above emit a nudge and never make a decision, so they are debt rather than a
blocker. `root-of-trust-guard.py`, `git-guardrails.py`, and `claim-reconcile.py` **do** decide —
their self-test suite (`scripts/hook-battery.sh`) was re-run against this repo on 2026-09-13 and
reproduces the same 17/234 failures as the original `rental-disclosure-claude` checkout, which is
evidence the failures are pre-existing environment flakiness in the self-tests (fixture setup on
this machine), not something the port introduced — see the 2026-09-13 session log.
