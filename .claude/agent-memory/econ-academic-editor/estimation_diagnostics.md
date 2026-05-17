---
name: estimation_diagnostics
description: Structural estimation diagnostics — apartments (40 mkts, all clipped) and houses (100 mkts, partial identification)
type: project
---

## Apartments (2026-04-21, 40 markets)

**Current run result:** ρ̂_m > 1 in all 40 apartment markets before clipping. The constraint ρ_m ≤ 1 is always binding — ρ_m is not identified by the current moment condition.

**Why:** The structural inversion ρ̂_m = Δ̂_m / (β̂₁_m · ê*_m) gives ≈ 7.7 on average. Three compounding causes:
1. Δ̂_m conflates K=1 and K=0 non-disclosers — the DiD estimand inflates the numerator.
2. Levels-versus-differences mismatch: β̂₁_m is a level; Δ̂_m is a DiD. Pre-reform non-disclosure premium is non-zero and not removed.
3. Ratio estimator bias: thin cells → small β̂₁_m realizations → ρ̂_m mechanically large. β̂₁_m ranges from 0.0002 to 0.1161.

**Contrast with previous stored estimates:** The project_paper.md memory records mean ρ̂ = 0.700 for 57 apartment markets. The current run uses a different (stricter) coverage filter (40 markets) and produces a qualitatively different result. These estimates are NOT consistent — one or both corresponds to a different model/data configuration. Do not average or reconcile them without checking which run is current.

**What is credible in the current run:**
- σ̂₁_m = 0 universally: genuine overidentifying validation, model's key qualitative prediction holds exactly.
- ĉ₀_m ≈ 1.6% of value: conditionally credible as a lower bound, but biased downward if true ρ_m << 1 (since ĉ₀_m identified from indifference condition that scales with ρ_m).
- σ̂₀_m ≈ 7.7%: directly observed from data, model-independent, credible.

**Proposed fix for ρ_m:**
- Preferred: Strategy A — proxy ρ_m with observable buyer composition (primary-residence share from notarial data or SeLoger listing fractions), replace market-by-market inversion with cross-market regression of Δ̂_m on β̂₁_m · ê*_m instrumented by ρ̃_m.
- Alternative: Strategy B — exploit January 2025 rental ban on G+ as second reform for a second DiD; requires post-2025 data.
- Fallback: Strategy C — pooled GMM moment E[Δ̂_m − ρ̄ · β̂₁_m · ê*_m] = 0 to estimate a single ρ̄; disciplines ρ from aggregate variation.

**Framing for the paper:** Do not present clipped ρ̂_m = 1 as structural parameters. Frame ρ_m as set-identified (ρ_m ∈ [0,1] consistent with data), note the constraint is always binding, lead with σ̂₁_m = 0 validation and ĉ₀_m estimates. A top-5 referee will catch this immediately if not acknowledged.

**How to apply:** In any session reviewing the ρ_m identification or estimation section, flag immediately that the current run does not identify ρ_m. Do not proceed as if ρ̂_m = 1 is a structural estimate. Always distinguish σ̂₁_m = 0 (robust) from ρ̂_m and ĉ₀_m (contingent on identification).

---

## Houses (2026-04-21, 100 markets)

**Current run result:** 92 of 107 markets (with β̂₁_m > 0) have ρ̂_m > 1 before clipping. Of the 75 Partial Pooling markets (those with Δ̂_m ≥ 0), 67 are clipped to 1 and 8 admit interior identification. Mean ρ̂_m = 0.718, median = 1.000 (bimodal: 25 markets at 0, bulk at 1, 8 interior).

**Key contrast with apartments:** Ratio Δ̂_m / β̂₁_m ≈ 0.58 for houses vs. ≈5 for apartments — tenfold improvement. Larger β̂₁_m (0.058 vs. 0.017) and smaller Δ̂_m (0.034 vs. 0.085) shift many markets toward the model-coherent region but do not achieve interior identification in most. Identification is partial, not complete.

**Regime breakdown:**
- 25 markets: Cost-Deterred Hiding (Δ̂_m < 0 → ρ̂_m = 0)
- 67 markets: Partial Pooling, upper-bound binding (ρ̂_m = 1)
- 8 markets: Partial Pooling, interior identification

**What is credible in the house run:**
- σ̂₁_m = 0 for all 100 markets: strongest validation result, holds across both property types (140 total markets).
- ĉ₀_m ≈ 1.8% (lower bound under clipped ρ̂_m): plausible, slightly lower than apartments (1.6%), consistent with lower hiding rates.
- σ̂₀_m ≈ 3.7%: directly observed, model-independent. Houses hide less than apartments (7.7%) — consistent with higher buyer-side observability of energy characteristics.
- Identified set for hiding cost per market: [ĉ₀_m, Δ̂_m] = [0.018, 0.034] on average — tighter than for apartments.

**Framing for the paper:** House results are a qualified improvement over apartments. The cross-market slope regression is better-powered (100 vs. 40 markets) and should be the primary identification strategy for a common ρ̄. The 8 interior-identified markets are potentially informative about conditions favoring point identification and should be characterized on observables. Cost-Deterred Hiding regime assignment for 25 markets should be reported with bootstrap confidence intervals to account for sampling error in Δ̂_m.

**Equilibrium regime labels (FINAL — do not revert):**
- σ₀*=0: "Cost-Deterred Hiding" (not "Full Unraveling")
- σ₀*=1: "Complete Adverse Selection" (not "Partial Separation")
- σ₀*∈(0,1): "Partial Pooling" (not "Mixed Strategy")
