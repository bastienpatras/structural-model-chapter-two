---
paths:
  - "pyproject.toml"
  - "setup.py"
  - "setup.cfg"
  - "src/**/__init__.py"
  - "tests/**/*.py"
---

# Python Package Development Standards

**Standard:** a well-structured, installable internal research package — `pip install -e .`
succeeds on a fresh clone, `pytest` passes, and the public API is deliberate, not accidental.

> **Scope:** This rule covers **packaged Python source** — a `pyproject.toml` + `src/<pkg>/`
> layout meant to be `pip install`-ed (by you, a co-author, or a replicator), as opposed to
> one-off analysis/estimation scripts run directly with `python script.py`. For those, see
> [`python-code-conventions.md`](python-code-conventions.md) — different rules apply (a
> top-level seeded RNG passed explicitly, relative output paths, no packaging concerns).
>
> **Current state (2026-09-13):** `src/` in this repo is a plain module tree (`__init__.py`
> present, no `pyproject.toml`/`setup.py`) — imported directly, not installed. This rule is
> written for **if/when** that changes (e.g. to make the estimation code `pip install`-able
> for a replication package or a co-author). Until then, treat it as the target state, not a
> current violation — don't manufacture a `pyproject.toml` unless asked.

---

## 1. Package anatomy

```
pkg/
├── pyproject.toml       # metadata, dependencies, build backend (hand-edited)
├── src/<pkg>/           # package code (the "src layout" — prevents accidental
│                        #   imports of the uninstalled package from the repo root)
│   ├── __init__.py      # defines the public API via __all__
│   └── ...
├── tests/               # pytest tests, mirroring src/<pkg>/ structure
├── docs/                # long-form docs (optional — Sphinx/mkdocs)
└── CHANGELOG.md          # user-facing changelog
```

**Use the `src/` layout, not a flat `<pkg>/` at repo root.** A flat layout lets `import <pkg>`
silently succeed from the repo root even when the package isn't installed, masking missing
dependencies and packaging bugs that only surface for someone who `pip install`s it fresh.

## 2. Dependencies & `pyproject.toml`

- **`[project.dependencies]`** for packages imported anywhere in `src/<pkg>/`. **Optional
  extras** (`[project.optional-dependencies]`, e.g. `test`, `viz`, `geo`) for anything used only
  in tests, docs, or an optional code path — guard the import (`try/except ImportError` with a
  clear message) rather than crashing on missing extras.
- **Pin floors, not exact versions**, unless reproducing a specific published result demands it
  (`numpy>=2.0` — this project's own floor, for cluster-pickle compatibility — is the right
  shape; `numpy==2.1.3` is not, unless `capture-environment` has locked a replication snapshot).
- `[project]` metadata: `name`, `version`, `authors`, `license`, `description` (one real
  sentence, not "A package for…"), `requires-python`.
- No dependency imported in `src/<pkg>/` that is missing from `[project.dependencies]`; no
  declared dependency that nothing actually imports.

## 3. Public API & Imports

- `__all__` in `src/<pkg>/__init__.py` (and in any submodule meant to be imported directly)
  states the intentional public surface. Internal helpers are not re-exported by accident.
- No circular imports between submodules — if `estimation.py` and `data_prep.py` need each
  other's types, factor the shared piece out rather than importing across the cycle.
- No `import *` anywhere in package source.
- Absolute imports within the package (`from pkg.estimation import ...`), not fragile relative
  `from ..` chains more than one level deep.

## 4. Docstring Documentation

- **Every public function/class** (anything in `__all__` or otherwise imported by users outside
  the package) documents parameters, return value, and raised exceptions, in a single
  consistent style (NumPy or Google — pick one, don't mix within the package).
- Include at least one runnable example in the docstring for the main entry points (an
  estimator class, a top-level `estimate()`/`fit()` function) — a doctest or a fenced code
  block a reader can paste into a REPL.
- Document any non-obvious assumption inherited from the paper (e.g. which equilibrium regime a
  function assumes, what a config dict's required keys are).

## 5. Testing (pytest)

- Tests live in `tests/`, mirroring the `src/<pkg>/` module structure (`tests/test_estimation.py`
  for `src/<pkg>/estimation.py`).
- Every public function has at least one test covering its documented contract plus an edge
  case (empty input, boundary parameter values, the ρ̂ = 1 boundary case this project already
  knows is common — see `APPENDIX-GAPS.md` item 1).
- **No global-state leakage:** a test that monkeypatches, changes `cwd`, sets an env var, or
  seeds a global RNG must restore it (a `pytest` fixture with teardown, or `monkeypatch`, not a
  bare mutation).
- Use `pytest.mark.parametrize` for the apartment/house market-type split this project's config
  already encodes (`config_apartment.json` / `config_house.json`), rather than duplicating a
  test body per market type.
- Mark slow/data-dependent tests (`@pytest.mark.slow`) and skip them by default in CI; keep a
  fast unit-test tier that runs on every commit.

## 6. Packaging Red Flags

| Red flag | Why it fails | Do instead |
|---|---|---|
| Flat layout (`<pkg>/` at repo root, no `src/`) | Masks missing-dependency bugs; `import <pkg>` "works" uninstalled | `src/<pkg>/` layout |
| Hardcoded absolute paths in package code | Breaks for every other user/machine | `importlib.resources` for packaged data; caller-supplied paths otherwise |
| Writing outside a caller-specified directory or `tempfile` | Surprising side effects, breaks in read-only/sandboxed environments | Never write to the package's own install location; accept an explicit output path |
| Global mutable state set on import (module-level `open()`, network calls, `matplotlib` backend switches) | Import-time side effects break composability and testing | Push side effects into functions the caller invokes explicitly |
| Bare `except:` swallowing errors | Hides estimation/convergence failures as if they succeeded | Catch specific exception types; re-raise or log with context |
| Secrets or `.env` values imported into package code | Leaks into any published/shared artifact | Config injected by the caller; secrets never hardcoded |
| No `requires-python` / unpinned floor on a numpy≥2 dependency | Silent incompatibility (this project already hit this once — see `python-code-conventions.md` §6) | State the floor explicitly and check it at import time if it's load-bearing |

## 7. Versioning & Changelog

- Follow semantic versioning once there's a first tagged release: breaking API change → major,
  new capability → minor, fix → patch.
- Every user-facing change gets a `CHANGELOG.md` entry. Deprecate gracefully (raise a
  `DeprecationWarning` for at least one minor version) rather than silently removing a public
  function.

## 8. The release gate

Before treating the package as installable/shareable, run
[`/python-package-check`](../skills/python-package-check/SKILL.md): it builds the package,
runs `pytest`, runs `ruff`/`mypy`, and triages every finding. **0 build errors, 0 test failures,
lint/type-check clean or explicitly justified** is the bar — the direct analogue of the R
package rule's "0 errors, 0 warnings, notes explained."

## 9. Checklist

```
[ ] src/<pkg>/ layout; installs cleanly with pip install -e .
[ ] No library-level import-time side effects; no circular imports; __all__ defines the public API
[ ] Dependencies classified correctly in pyproject.toml; no unused or undeclared imports
[ ] Every public function: docstring with params/return/raises + a runnable example
[ ] pytest tests mirror src/ structure; public functions tested incl. edge cases; no global-state leakage
[ ] No hardcoded paths, no bare except, no writes outside a caller-specified location
[ ] Version bumped + CHANGELOG.md entry (once versioned)
[ ] ruff / mypy clean, or each remaining finding explicitly justified
```

## Cross-references

- [`r-package-conventions.md`](r-package-conventions.md) — the R/CRAN analogue this rule mirrors.
- [`python-code-conventions.md`](python-code-conventions.md) — the non-package, analysis-script
  counterpart (what most of this repo's `src/`/`scripts/` actually is today).
- [`../agents/python-package-reviewer.md`](../agents/python-package-reviewer.md) — the agent
  that enforces this rule.
- [`../agents/python-reviewer.md`](../agents/python-reviewer.md) — general numerical discipline,
  still applies inside package functions.
- [`replication-protocol.md`](replication-protocol.md) — when the package reproduces published
  results.
