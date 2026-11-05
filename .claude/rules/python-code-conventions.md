---
paths:
  - "src/**/*.py"
  - "scripts/**/*.py"
  - "explorations/**/*.py"
  - "main.py"
  - "run.py"
---

# Python Code Standards

**Standard:** Senior Principal Data Engineer + PhD researcher quality — the same bar as
[`r-code-conventions.md`](r-code-conventions.md), adapted to this project's actual stack
(numpy>=2.0, pandas, scipy, statsmodels, matplotlib, plotly, geopandas).

> **Scope:** These standards apply to **analysis/estimation code** — `src/` (the structural
> model: `data_prep.py`, `estimation.py`, `model.py`, `moments.py`, `hedonic.py`,
> `event_study.py`, `outputs.py`, `validation.py`, `viz/`), `scripts/` (figure/table
> generators), and notebooks. If this codebase ever grows a proper installable package
> (`pyproject.toml`, `src/<pkg>/`, published `__all__`), see
> [`python-package-conventions.md`](python-package-conventions.md) instead — different rules
> apply (no bare module-level side effects, namespaced public API, packaging hygiene). The
> numerical discipline in §8 applies to both.

---

## 1. Reproducibility

- Seed via `numpy.random.default_rng(seed)` **once**, passed explicitly through function
  arguments — never a bare module-level `np.random.seed()` call buried in a function, and
  never re-seeded inside a loop.
- All imports at the top of the file (no `import` inside functions except to break a genuine
  circular-import or to guard an optional/heavy dependency).
- All paths relative to the repository root or built from `pathlib.Path(__file__).parent`
  — no hardcoded absolute paths (`/Users/...`) in committed code, including scratch/config paths.
- Output directories created with `Path(out_dir).mkdir(parents=True, exist_ok=True)`.
- Config passed explicitly (this project's `config_apartment.json` / `config_house.json`
  pattern) rather than hardcoded market-specific constants scattered through `src/`.

## 2. Function Design

- `snake_case` naming, verb-noun pattern (`compute_moments`, `estimate_theta`, `load_registry`).
- Every non-trivial function has a docstring (NumPy or Google style — pick one project-wide,
  don't mix) documenting parameters, return value, and any non-obvious assumption.
- Type hints on public function signatures (`def estimate(df: pd.DataFrame, config: dict) ->
  EstimationResult:`), not necessarily on every internal helper.
- Default parameters for tuning values; no magic numbers inside function bodies — name them
  as module-level constants or config fields.
- Return values are named structures (`dataclass`, `NamedTuple`, or a documented `dict` with a
  fixed key set) — not bare unnamed tuples/lists that force the caller to remember positional
  order.
- **No mutable default arguments** (`def f(x, cache={})` — the classic Python footgun; use
  `None` and initialize inside the function).

## 3. Domain Correctness

- Verify estimator implementations match the formulas in `paper-real-estate/sections/04-structural-draft.tex`
  and the appendix proofs — a drift between `src/estimation.py` and the paper's stated
  equations is a **Critical** finding, not a style note (see `structural-micro-reviewer` agent).
- Check known package version pitfalls (document below in Common Pitfalls) — this project
  pins `numpy>=2.0` specifically for cluster-pickle compatibility; a regression here silently
  breaks saved estimation objects.

## 4. Visual Identity

This project uses both static (`matplotlib`) and interactive (`plotly`) figures — see the
`pyplot-specialist` and `cartopy-specialist` agents for publication-grade figure construction.
Whichever library, apply the project's palette and a single consistent style module rather than
ad hoc `plt.plot()` calls with default colors scattered across scripts.

```python
# --- project palette (keep in one place, e.g. src/viz/palette.py) ---
PRIMARY = "#012169"
ACCENT_POSITIVE = "#15803d"
ACCENT_NEGATIVE = "#b91c1c"
NEUTRAL = "#525252"
```

- Explicit figure dimensions and DPI (`fig.savefig(path, dpi=300, bbox_inches="tight")`), not
  relying on defaults that differ across machines/backends.
- Axis labels: sentence case, units included, no unexplained abbreviations.
- No default matplotlib color-cycle leaking through onto a publication figure — set it once
  via the shared style module or an `rcParams`/`mplstyle` file.

## 5. Data Caching Pattern

**Heavy computations saved to disk (parquet for tabular, pickle/joblib for model objects);
downstream scripts (paper exhibit generators, notebooks) load pre-computed data rather than
re-running estimation.** This project's analogue of the R workflow's RDS pattern.

```python
result_df.to_parquet(out_dir / "market_estimates.parquet")
joblib.dump(estimation_result, out_dir / "estimation_result.joblib")
```

- Every object referenced by `paper-real-estate/results/tables/*.tex` or a figure generator
  must have a corresponding save call — a missing one means the exhibit generator can't run
  from a fresh clone. Flag as **High** severity.
- Filenames descriptive; paths built with `pathlib`, not string concatenation.

## 6. Common Pitfalls

| Pitfall | Impact | Prevention |
|---|---|---|
| `numpy<2.0` in the environment | Cluster-pickle incompatibility (see `requirements.txt` comment) | Pin `numpy>=2.0`; check `np.__version__` in any long-running estimation job |
| Hardcoded absolute paths | Breaks on other machines / CI | `pathlib.Path(__file__).parent`-relative paths |
| Silent `pandas` dtype coercion on merge (`K=1`/`K=0` flags becoming float on a merge with NaNs) | Corrupts the informed/uninformed classification silently | Assert dtypes after every merge touching classification columns |
| `groupby(...).mean()` silently dropping NaN groups | Understates market count / biases market-level statistics | Explicit `dropna=False` where a market with all-missing values should still be counted or flagged |

## 7. Line Length & Mathematical Exceptions

**Standard:** Keep lines <= 100 characters (`ruff`/`black` default is 88 — this project's
mathematical density justifies the same exception the R convention grants).

**Exception: Mathematical Formulas** — lines may exceed 100 chars **if and only if:**

1. Breaking the line would harm readability of the math (moment conditions, likelihood
   expressions, closed-form premium formulas matching the paper's equations).
2. An inline comment explains the mathematical operation, ideally citing the paper's equation
   number:
   ```python
   # Non-disclosure premium in partial pooling, closed form (eq. 14 in 04-structural-draft.tex)
   premium = (sigma_0 * c_bar) / (sigma_0 + (1 - sigma_0) * sigma_1)
   ```
3. The line is in a numerically intensive section (estimation routines, moment computation,
   bootstrap loops).

## 8. Numerical Discipline

See [`python-reviewer.md`](../agents/python-reviewer.md) Category 11 ("Numerical Discipline")
for the full checklist. Headline rules:

- **No float equality.** Never `==` on floats/doubles. Use `np.isclose(a, b, atol=..., rtol=...)`
  or `abs(a - b) < tol`.
- **CDF/quantile clamping to an OPEN interval.** A computed probability passed to
  `scipy.stats.norm.ppf()` or similar must be clamped away from exact 0/1 — those produce
  `±inf`. Use a named epsilon:
  ```python
  EPS = 1e-12
  p_clamped = np.clip(p, EPS, 1 - EPS)
  ```
- **Explicit integer dtypes for counts.** `n_markets: int`, `df["K"].astype("Int64")` for
  nullable integer flags — don't let a merge silently promote a 0/1 indicator to float.
- **Vectorize; don't append-in-loop.** Pre-allocate (`np.empty(n)`, a list comprehension, or a
  vectorized pandas/numpy operation) instead of growing a Python list with `.append()` inside a
  hot numerical loop, and instead of repeated `pd.concat` inside a loop (quadratic).
- **Deterministic bootstrap/simulation seeding.** One `rng = np.random.default_rng(seed)`
  passed down explicitly; for parallel workers, derive independent streams via
  `rng.spawn(n_workers)` (numpy >= 1.25) rather than reusing one `rng` across processes.
- **Explicit NaN handling.** Any `.mean()`, `.sum()`, `.std()` on empirical data states its NaN
  policy explicitly (pandas defaults to `skipna=True`; make that a deliberate choice, not an
  accident, especially on the ρ̂-clipped/boundary market subsets this project already flags in
  `paper-real-estate/APPENDIX-GAPS.md`).
- **No bare `except:`.** Catch a specific exception type; a bare `except:` (or `except
  Exception:` swallowed silently) hides estimation failures as if they converged.

## 9. Code Quality Checklist

```
[ ] Imports at top; no bare module-level side effects on import
[ ] RNG seeded once via np.random.default_rng(), passed explicitly (never global np.random.seed in a function)
[ ] All paths relative / pathlib-based
[ ] Functions documented (docstrings) with type hints on public signatures
[ ] Figures: explicit dpi/dimensions, project palette, no default color-cycle leakage
[ ] Data caching: every computed object referenced downstream is saved (parquet/joblib)
[ ] Comments explain WHY not WHAT
[ ] Numerical discipline: no float ==, clamped probabilities, vectorized (not append-in-loop), explicit NaN policy, no bare except
```

## Cross-references

- [`r-code-conventions.md`](r-code-conventions.md) — the R analogue (not used in this repo's
  own code, kept for reference since the workflow template is multi-language).
- [`../agents/python-reviewer.md`](../agents/python-reviewer.md) — the agent that enforces this rule.
- [`../agents/structural-micro-reviewer.md`](../agents/structural-micro-reviewer.md) — paper-code
  consistency and identification-strategy review; domain correctness (§3) feeds that review.
