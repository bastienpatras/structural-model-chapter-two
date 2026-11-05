**Status:** DRAFT

# DiD diagnostic: make the event-study visible and check the 6.9%/3.4% numbers

## Context

The TOPFIN peer-review pipeline (previous plan, now complete — see
`quality_reports/peer_review_paper-real-estate/editorial_decision.md`) flagged the DiD
event-study as the load-bearing, unverified core of the paper: the headline non-disclosure
premium (6.9% apartments / 3.4% houses) and the structural parameter ρ̂ₘ both come from it, no
figure in the compiled paper actually traces to this repo's own DiD computation, and no
standard errors exist anywhere. The user wants to **see** the DiD before deciding anything about
the review findings — plots via `pyplot-specialist`, plus a plain overview of what is actually
being computed, because "6% seems a lot."

**What I found on reconnaissance** (all reproducible from files already in the repo):

- The DiD is real code, not vaporware: `src/event_study.py` — `load_price_indices()` reads a
  raw hedonic index panel, `compute_did()` produces market-level β̂₁ₘ (EPC quality premium,
  ABC/D vs EFG) and Δ̂ₘ (non-disclosure premium, undisclosed vs EFG) via simple pre/post mean
  differencing, with a `min_volume` thinness filter (default 20).
- Its input is `data/index_APARTMENT.csv` / `data/index_HOUSE.csv` (30,780 / 33,601 rows;
  columns `date, EPC, cluster_id, prices, volume, ...`) — a hedonic price-index panel built in
  the user's own prior chapter (`patras_mandatory_2024`), Oct 2018–Jul 2024, monthly, by EPC
  category × market (`cluster_id`).
- `main.py`/`run.py` both wire this in directly (`main.py:296-297`): `did_estimates =
  compute_did(index_df, min_volume=CONFIG["did_min_volume"])` → `estimate_rho_c0(...)`, with
  `did_min_volume=20` in both `config_apartment.json` and `config_house.json`. This is the real,
  currently-running pipeline — not a stale or orphaned script.
- **The live output already contradicts the manuscript's own market counts.**
  `results/comparison.txt` (regenerated 2026-08-17, same run as the currently-tracked
  `results/tables/*.tex`) reports **302 apartment markets, 564 house markets** — nothing close
  to the 40–107 range the manuscript's various sections quote (the referee-flagged
  irreconcilable-market-count cluster). β̂₁ = 0.016 (apt) / 0.073 (house); ĉ₀ mean = **0.0342**
  (apt) — which is *already, in the live output*, greater than β̂₁ = 0.016, the exact
  "arithmetic impossibility" the methods referee flagged as a hypothesis. `main.py:284`'s own
  comment states the estimator directly: `ĉ₀_m = Δ̂_m — equilibrium indifference` — i.e. the
  code's own comment confirms ĉ₀ is Δ̂ (not an independent estimate), which is what the
  editorial decision's F1 finding derived from the paper's equations.
- The event-study PNGs the manuscript actually displays (`main.tex:322-356`,
  `fig/event-study/{apartment,house}/index/event-study-{efficient,intensive,missing}.png`,
  which exist on disk via the `paper/fig` symlink) are attributed entirely to
  `patras_mandatory_2024`'s "two-step hedonic procedure" — a pipeline that is **not in this
  repo**. They cannot be used to verify `compute_did()`'s numbers because they are not
  necessarily the same computation. This is the actual sense in which "the DiDs are absent" —
  nothing in this repo currently plots what `compute_did()` itself is computing.
- No standard errors or bootstrap exist for β̂₁ₘ/Δ̂ₘ anywhere (`src/estimation.py:583`'s own
  docstring: "Bootstrap SEs for ρ̂_m from the DiD first stage must be computed separately... by
  bootstrapping `compute_did()`" — flagged as a known gap, never done).

## Approach

**Goal: let the user see the actual DiD this repo computes, reconcile it against every number
currently in play (manuscript, `comparison.txt`, referee reports), without touching the paper,
`results/`, or the estimation code.** This is a read-then-visualize diagnostic pass, not a fix —
no claim in the paper is edited by this plan.

### Step 1 — new diagnostic script: `scripts/diagnose_event_study.py`

A real, reusable script (not scratch — follows the `scripts/make_*.py` naming/output
convention), read-only with respect to `data/` and `src/`. For each property type (apartment,
house):

1. Call `load_price_indices()` + `compute_did()` exactly as `main.py`/`run.py` do (same
   `min_volume=20`), so the diagnostic is provably the same computation feeding the estimates —
   not a re-implementation that could silently diverge.
2. Also build the **national aggregate monthly time series** (volume-weighted mean `log_index`
   by EPC category × month, pre/post reform) — this is the object a reader actually wants to
   *see*: three lines (ABC/D high-quality, EFG low-quality, undisclosed) around July 2021.
3. Export: (a) the aggregate time series as tidy CSV, (b) the market-level `did.did` DataFrame
   (β̂₁ₘ, Δ̂ₘ, n_pre, n_post per market) as CSV, (c) summary statistics text (N markets before/after
   the volume filter, mean/median/SD of β̂₁ₘ and Δ̂ₘ, count of markets with β̂₁ₘ ≤ 0) — reusing
   `pandas`/`numpy` only, no new estimation logic.

All outputs go to `quality_reports/diagnostics/event-study-audit/` — deliberately **not**
`results/` (that directory is the single-sourced exhibit pipeline the paper points at; this is a
verification exercise, not a new paper exhibit, so it stays out of that pipeline per
`single-source-of-truth.md` until/unless the user decides otherwise).

### Step 2 — figures via `pyplot-specialist`

Hand the exported CSVs to the `pyplot-specialist` agent (per `collaboration-mode.md`'s
visual-polish routing — no ad hoc plotting) to produce, for **both** property types:

- **Fig 1 — the event study itself.** National aggregate log-index time series by EPC category
  (ABC/D, EFG, undisclosed), monthly, Oct 2018–Jul 2024, reform date (July 2021) marked with a
  vertical line, two panels (apartment / house) or a 2×1 grid. This is the direct visual answer
  to "is 6.9%/3.4% plausible" — the reader can see the pre-trend and the post-reform gap.
- **Fig 2 — market-level distributions.** Histograms (or strip/dot plots) of β̂₁ₘ and Δ̂ₘ across
  markets, both property types, with the volume-filtered N marked and the manuscript's headline
  aggregate (6.9%/3.4%) marked as a reference line, so the reader can see where the aggregate
  sits relative to the market-level spread — including how many markets have β̂₁ₘ ≤ 0.
- **Fig 3 — the ρ̂ₘ saturation the referees flagged.** Scatter of Δ̂ₘ vs. β̂₁ₘ·ê*ₘ per market
  (the two objects whose ratio is ρ̂ₘ), with the 45° line marked — this is the single clearest
  picture of the "ρ̂ₘ clips at 1 almost everywhere" finding, and it's a direct, low-effort
  visualization of exactly the concern the user is asking about.

Saved to `quality_reports/diagnostics/event-study-audit/figures/` (PNG, 300 DPI, project
palette) — not `results/figures/`, same reasoning as Step 1.

### Step 3 — the overview memo

`quality_reports/diagnostics/event-study-audit/OVERVIEW.md` — plain-language, for the user, not
paper prose:

- What data feeds the DiD, exactly (file, columns, date range, N markets before filtering).
- The exact formulas (`β̂₁ₘ = ABC/D − EFG`, `Δ̂ₘ = undisclosed − EFG`, both as pre/post mean
  differences; `ρ̂ₘ = Δ̂ₘ/(β̂₁ₘ·ê*ₘ)`; `ĉ₀ₘ = ρ̂ₘ·β̂₁ₘ·ê*ₘ` — and the code-comment confirmation that
  this equals `Δ̂ₘ` in the interior case) — taken directly from `event_study.py`'s own docstring
  and `main.py`'s inline comments, not re-derived.
- A **reconciliation table**: what `comparison.txt` currently reports (302/564 markets,
  β̂₁=0.016/0.073, ĉ₀ mean=0.0342/0.0445) vs. what the manuscript states in each of the
  locations the referees flagged (40, 45, 49, 100, 97, 104...) — so the user can see the drift
  directly rather than take the referee reports' word for it.
- Explicit flag, not buried: the live `comparison.txt` output already shows ĉ₀ mean (0.0342) >
  β̂₁ (0.016) for apartments — the same inequality violation the methods referee predicted from
  the algebra, now confirmed against the actual current run, not just the manuscript's table.
- No claim about *why* the 6.9%/3.4% number is large or small — that's the user's judgment call
  once they can see the picture; the memo states facts and points at the figures, it doesn't
  pre-argue a verdict.

## Explicitly out of scope for this pass

- No edits to `paper-real-estate/`, `src/`, `results/`, or any exhibit the paper points at.
- No bootstrap/SE computation (that's the review's A2 item — a real follow-up, not folded in
  here silently).
- No attempt to reconcile *why* the manuscript's market counts differ from `comparison.txt`'s
  302/564 — that reconciliation is exactly what the diagnostic surfaces for the user to decide
  what to do about, not something this pass resolves unilaterally.

## Files touched

- `scripts/diagnose_event_study.py` (new)
- `quality_reports/diagnostics/event-study-audit/` (new — CSVs, figures, `OVERVIEW.md`)

## Verification

- `python3 scripts/diagnose_event_study.py` runs clean, no errors, using the same
  `load_price_indices`/`compute_did` call signature as `main.py`/`run.py` (grep-diffable against
  `main.py:296-297` to confirm no silent divergence in how the diagnostic invokes the same code).
- Spot-check: the script's own summary stats for apartment markets-after-filter should be
  checkable against `results/comparison.txt`'s "Markets: 302" — if the diagnostic's own N
  doesn't match, that's a bug in the diagnostic, not a new finding, and gets fixed before the
  figures are drawn.
- `python3 scripts/check-repo-hygiene.py` — confirm `quality_reports/diagnostics/` doesn't need
  an allowlist entry (it's under the already-allowlisted `quality_reports/` root dir, so this
  should be a no-op check, not a new gate to satisfy).
