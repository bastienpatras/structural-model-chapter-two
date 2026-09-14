# Session log — ρ identification fix

**Branch:** `fix/rho-identification-gmm` (off `paper-real-estate`)
**Plan:** `quality_reports/plans/humble-zooming-lovelace.md`

## Goal

Fix the market-level ρ (buyer EPC-sensitivity) identification failure surfaced by a simulated
`--peer` referee report's Concern 1 (`quality_reports/peer_review_paper-real-estate/referee_methods.md`).

## Key context

- `micro-theorist` derivation (this session) proves (ρ_m, β1) identified only as the product
  b_m=ρ_mβ1, by any model-implied moment, for any number of markets (Proposition 1) — the
  originally-planned "pooled cross-market GMM" cannot work without an external, non-price anchor
  on β1. Fix design: an ADEME-consumption-based energy-cost anchor (Assumption A / Proposition 4).
- Independent, previously-unflagged bug found while verifying the derivation against code:
  `run.py:126-130` omits the `did_beta1` kwarg to `build_valuation_params`, so ĉ0_m/R̄_m silently
  use hedonic (level) β1_m rather than the DiD β1_m Table 4 reports alongside them. Derivation's
  own level-vs-change argument says hedonic is actually the *correct* choice — Phase 0 makes this
  deliberate/documented rather than accidental.
- Policy section (§5) numbers proven unaffected by the ρ fix (R̄^PP_m = b_m = the observed
  disclosed-H-vs-L price gap directly; no ρ decomposition needed) — only its ρ-attribution prose
  needs rewriting.
- Prior work already committed and pushed to `paper-real-estate` this session (workflow-port +
  review reports, commit `3ee5572`) before this branch was created.

## Status

Plan approved. Starting Phase 0 (correctness baseline: make the hedonic-vs-DiD β1 choice explicit
in `run.py`/`04-structural-draft.tex`, regression-check outputs unchanged).
