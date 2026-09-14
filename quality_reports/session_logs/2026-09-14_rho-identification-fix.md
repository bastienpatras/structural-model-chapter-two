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

### Phase 0 — done (commit `f354e94`)

User chose DiD β1 (not hedonic) for ĉ0/R̄/S* after seeing both options quantified. Fixed
`run.py:126-130` (missing `did_beta1` kwarg to `build_valuation_params`). Real, substantive
effect, not bookkeeping: ĉ0 apartments 3.42%→2.27%, houses ~4.5%→2.53%; apartment markets needing
subsidy @€250/m² 77.5%→100%; aggregate budget €15.5bn/€38.7bn→€11.6bn/€34.8bn. Table 4/§5 paper
text not yet updated (Phase 3).

### Phase 1 — energy-cost anchor for β1 (commit `c972538`)

Raw ADEME consumption data unavailable locally (lives on GCS, confidential geocoded address
data, current match pipeline only keeps the letter grade) — pivoted to a public, standardized
DPE-band-midpoint anchor instead (no new data acquisition). User caught a real selection-bias
risk before implementation: Ē0,m/Ē1,m must pool BOTH disclosed and hidden K=1 listings, not
disclosed-only. `compute_energy_anchor()` in `src/data_prep.py`, validated on real data — zero
wrong-sign markets, ~143 kWh/m²/yr mean gap.

Calibration: p_E≈€0.21/kWh (CRE/Eurostat), r≈3.75% (French mortgage rate) — both reasonably
settled. **T (horizon) is NOT locked** — user is sourcing actual French property holding-period
data (pushed back on my "long horizon/perpetuity" default; connects to the energy-efficiency-gap
literature). Sensitivity grid run T∈{10,20,25,perpetuity}: apartment mean ρ̂ ranges 0.50→0.15,
violations of ρ≤1 drop 22%→0%, highly sensitive. Saved to native memory
`rho_anchor_calibration.md` — **do not lock T without checking there first.**

### Phase 2 — core estimator (commit `c972538`, same as Phase 1)

`src/rho_identification.py`: `estimate_beta1_anchor` + `estimate_rho_c0_anchored`
(Propositions 2(ii), 4). `python-reviewer` found 2 critical bugs (both copy-pasted from the old
estimator without re-deriving for the new formulas) — fixed before commit. Validated end-to-end,
T=10 placeholder: apartments n=49 mean ρ̂=0.50 (1 violation), houses n=104 mean ρ̂=0.45
(6 violations) — genuine cross-market variation, not the old estimator's ~100%-clipped-at-1
degeneracy.

**Deliberately NOT wired into `run.py` yet** — found a real integration subtlety (naively
feeding the anchored ρ̂ into `estimate_msm`'s existing machinery would silently reintroduce a
ρ-dependence into ĉ0 that Proposition 2(ii) says shouldn't be there). Design is resolved (bypass
`estimate_msm`, build a compatible `MSMResult` directly, populate `eq_types` via
`model.solve_equilibrium`) but not executed — holding until T is locked, to avoid validating
throwaway plumbing against a provisional calibration.

### Next

Waiting on user's tenure/holding-period number to finalize T, then: wire the estimator into
`run.py` (Phase 2 step 4-5), re-run both property types, then Phase 3 (paper rewrite — Table 4,
identification section, robustness appendix, abstract/conclusion, §5 prose).
