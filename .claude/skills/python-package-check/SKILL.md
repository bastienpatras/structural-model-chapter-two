---
name: python-package-check
description: Run the Python package release gate — build/install check, run pytest, run ruff/mypy, and triage every finding against packaging best practice before treating a package as installable/shareable. Use when the user says "check my Python package", "is this installable", "run pytest and lint", "prepare this for a replication package", or points at a directory containing pyproject.toml. Produces a check report + release checklist in quality_reports/.
argument-hint: "[path to package root, or blank to autodetect from pyproject.toml]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Task", "Monitor"]
effort: high
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/python-package-check` — Python Package Release Gate

Run the build → test → lint/type-check → triage pipeline that decides whether a Python package
is releasable/shareable, then review the source for issues automated checks can't see. The
Python analogue of `/r-package-check`.

**Input:** `$ARGUMENTS` — the package root (a directory containing `pyproject.toml`). If blank,
autodetect by searching the working directory for `pyproject.toml`. If none exists anywhere in
the repo, say so plainly and stop — this skill checks a package, it doesn't scaffold one from
scratch unasked (see `.claude/rules/python-package-conventions.md`'s note on this repo's current
un-packaged state).

---

## Constraints

- **Follow [`.claude/rules/python-package-conventions.md`](../../rules/python-package-conventions.md)**
  — the release bar (clean install, tests pass, lint/type-check clean or justified) is the gate.
- **Run the `python-package-reviewer` agent** on the source before declaring the package
  releasable.
- **Do not bump the version or publish to PyPI/an index.** This skill *checks*; the human
  decides when to release.

---

## Workflow Phases

### Phase 0: Pre-Flight Report

```markdown
## Pre-Flight Report — Python Package Check

**Package:** [name + version from pyproject.toml]
**Root:** [path]
**Public API:** [from __all__ / package __init__.py]
**Dependencies:** [project.dependencies] · optional-dependencies [list]
**Toolchain available:** pip/build [✓/✗], pytest [✓/✗], ruff [✓/✗], mypy [✓/✗], coverage [✓/✗]
**Plan:** install → test → lint/type-check → triage → review
```

Detect the toolchain with a quick probe; if `pytest`/a build frontend is missing, stop and tell
the user what to install.

```bash
python3 -c "import importlib.util as u; print('pytest:', bool(u.find_spec('pytest')), \
'ruff:', bool(u.find_spec('ruff')), 'mypy:', bool(u.find_spec('mypy')), \
'coverage:', bool(u.find_spec('coverage')))"
```

### Phase 1: Install

Install into a clean, isolated environment (never the user's active one) and confirm it
succeeds — this is the Python analogue of `devtools::document()` + drift detection, except the
failure mode here is "doesn't install clean," not "generated docs are stale":

```bash
python3 -m venv /tmp/pkgcheck-venv && /tmp/pkgcheck-venv/bin/pip install -e "[pkg]"
```

If this fails, that's the first and most important finding — nothing downstream matters until
a clean install succeeds.

### Phase 2: Test

```bash
/tmp/pkgcheck-venv/bin/python -m pytest "[pkg]/tests" -q
```

Report failures. If `coverage` is available (Phase 4), report per-module coverage of the public
API.

### Phase 3: Lint & Type-Check

**This can be slow on a large codebase** — background-launch and stream with the **Monitor
tool** rather than blocking, the same pattern as `/r-package-check`'s `R CMD check`:

```bash
/tmp/pkgcheck-venv/bin/ruff check "[pkg]/src"
/tmp/pkgcheck-venv/bin/mypy "[pkg]/src"
```

Then **triage every result** into a table:

| Result | Tool | Severity | Action |
|---|---|---|---|
| … | ruff / mypy | error / warning | fix / justify |

- **ruff errors, mypy errors** → must fix before release.
- **Warnings/style notes** → fix if cheap; otherwise write the justification (a `# noqa: CODE —
  reason` comment, or an explicit note in the check report).

### Phase 4: Coverage (optional)

```bash
/tmp/pkgcheck-venv/bin/python -m pytest "[pkg]/tests" --cov="[pkg]/src" --cov-report=term-missing
```

Report per-module coverage; flag public functions with 0% coverage.

### Phase 5: Source Review

```
Delegate to the python-package-reviewer agent:
"Review the package source at [pkg]"
```

Address Critical (packaging/composability violations) and High (install/test-blocking) findings.

### Phase 6: Release Gate + Report

Save a report to `quality_reports/[package]_package_check.md` and present a verdict:

```markdown
## Release Gate — [package] [version]
- Install (pip install -e .): PASS/FAIL
- Tests: P passed, F failed
- ruff: E errors, W warnings · mypy: E errors
- Coverage: X% of public API
- python-package-reviewer: C critical, H high
- **Verdict:** RELEASABLE / FIX-FIRST / NOT-YET-PACKAGED

### Release checklist
[ ] Clean install in an isolated venv succeeds
[ ] pytest: 0 failures; public API covered incl. known edge cases (e.g. ρ̂ boundary markets)
[ ] ruff/mypy clean, or each remaining finding explicitly justified
[ ] Version bumped + CHANGELOG.md updated
[ ] If this is a replication-package deliverable: cross-check against /replication-package
     and /capture-environment (pinned dependency versions, not floors)
```

---

## Important

- **A clean isolated-venv install is the gate, not `pip install -e .` in your existing
  environment** — the latter can succeed while masking a missing dependency your own environment
  happens to already have installed.
- **The gate is install-clean + tests-pass + lint-clean-or-justified** — nothing less is
  "releasable," mirroring the R rule's "0 errors, 0 warnings, notes explained."
- **This skill does not publish.** Actually uploading to PyPI/an index, or finalizing a
  replication-package deposit, is the maintainer's call — see `/replication-package` for the
  latter.

## Long-running checks: use the Monitor tool

A full lint/type-check pass or a coverage run can take a while on a large codebase.
Background-launch via Bash with `run_in_background: true`, capture the `bash_id`, and use the
**Monitor tool** to stream progress instead of polling. See
[`data-analysis/SKILL.md`](../data-analysis/SKILL.md) for the pattern.
