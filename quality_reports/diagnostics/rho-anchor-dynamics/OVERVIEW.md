# Post-reform dynamics of the anchored ρ̂_m/ĉ₀_m estimator

Generated 2026-09-15. Data: `post_window_trajectory.csv` (this folder). Re-derivable via
`quality_reports/plans/humble-zooming-lovelace.md`'s Phase 1/2 pipeline
(`src/data_prep.py:compute_energy_anchor`, `src/rho_identification.py`), with the DiD
post-period truncated to three anniversaries of the July 2021 reform instead of the full
window to July 2024.

## What this shows

The market-level DiD (`β̂₁,m`, `Δ̂_m`) and the anchored structural estimates (`ρ̂_m`, `ĉ₀_m`,
`λ̂_m`) computed separately with the post-reform window ending July 2022 / July 2023 / July 2024
(T=10, p_E=0.21, r=0.0375 calibration held fixed throughout — only the DiD window changes).

| Property | Window end | β̂₁,m | Δ̂_m | ρ̂_m mean | ĉ₀_m mean | λ̂_m mean (t-stat) |
|---|---|---|---|---|---|---|
| Apartment | 2022-07 | 0.22% | 3.08% | 0.291 | 1.60% | 3.89% (6.87) |
| Apartment | 2023-07 | 1.06% | 5.68% | 0.375 | 1.89% | 5.50% (7.28) |
| Apartment | 2024-07 (full) | 1.66% | 6.80% | 0.488 | 2.37% | 6.00% (6.76) |
| House | 2022-07 | 3.11% | 2.92% | 0.331 | 2.54% | 1.06% (2.82) |
| House | 2023-07 | 4.03% | 3.01% | 0.380 | 2.90% | 0.63% (1.78) |
| House | 2024-07 (full) | 5.02% | 3.38% | 0.453 | 3.42% | 0.43% (1.10) |

## Three patterns

1. **β̂₁,m rises monotonically in both segments** — progressive capitalisation of the reform,
   consistent with the paper's own event-study figure.
2. **ρ̂_m grows at strikingly similar *rates* in both segments** (apartments 0.29→0.38→0.49,
   houses 0.33→0.38→0.45) despite very different ĉ₀ levels — reads like broad-based buyer
   EPC-awareness building up post-reform, not something apartment- or house-specific.
3. **The apartment/house asymmetry in λ̂_m is a diverging trend, not just an endpoint fact.**
   Apartments: the over-identifying wedge grows and stays strongly significant throughout
   (t=6.87→7.28→6.76). Houses: the wedge *shrinks* and loses significance over time
   (t=2.82→1.78→1.10) — marginally significant at 1 year post-reform, essentially zero by 3
   years. I.e. the model's Partial-Pooling prediction (Δ_m=c₀) converges toward holding for
   houses while apartments diverge further from it.

## Why this matters for Phase 3

This is a stronger, more precise version of "apartments reject the model's over-identifying
restriction, houses don't" (Concern 6/the referee's σ₁ finding is a related but separate
restriction) — it's "apartments reject increasingly over time, houses converge to fitting."
Worth citing in the robustness appendix alongside the T=5/T=15 calibration grid (not yet run,
see plan file) as a second axis of robustness for the λ̂_m finding specifically.
