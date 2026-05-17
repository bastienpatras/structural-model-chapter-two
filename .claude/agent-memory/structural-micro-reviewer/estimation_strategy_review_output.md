---
name: estimation_strategy_review_output
description: Session record for 2026-04-21 writing of ESTIMATION_STRATEGY_REVIEW.md — key findings, framing decisions, and open issues surfaced during the write
type: project
---

On 2026-04-21, wrote `paper/ESTIMATION_STRATEGY_REVIEW.md` as a self-contained methods appendix covering model, identification, moments, estimator, results, and limitations.

**Key structural facts confirmed from code:**

- Primary estimator: `estimate_msm(fix_rho=True)` — pure closed-form inversion, no optimization. c₀_hat = rho_m * beta1_m * e_star, with e_star from belief_function(sigma_0_hat, pi_hat, theta_bar_hat).
- σ̂₁_m = 0 across all 140 markets (40 apt + 100 house) — confirmed untargeted, not imposed as restriction. This is the strongest validation result.
- Moment set: m₃ (DiD premium, identifies ρ_m in Step 1), m₄ (hiding rate σ̂₀_m, active in Step 2 for c₀), m₅ (σ̂₁_m ≈ 0, overidentifying check). m₁ and m₂ dropped because fit by construction after hedonic residualization.
- ρ̂_m clipped at [0,1]; ρ̂_m > 1 in all 40 apartment markets and 92/107 house markets before clipping.

**Key numbers (finalized in the document):**

- Apartments: 40 markets. ĉ₀_m mean 1.6% (0.016 log pts). ê*_m mean 0.252. ρ̂_m = 1 for all 40 markets.
- Houses: 100 markets. ĉ₀_m mean 1.8% (0.018 log pts). Identified interval [0.018, 0.034]. ~8 markets with interior ρ̂_m < 1.
- Pooled hedonic: β̂₁ = 0.063 (houses), 0.036 (apartments). DiD mean: 0.058 (houses), 0.017 (apartments) — attenuation confirmed for apartments.

**Framing decisions made:**

- ρ̂_m = 1 should be presented as a maintained assumption (set-identified at boundary), not an interior estimate.
- ĉ₀_m should be presented as a lower bound (apartments) or identified interval (houses).
- The paper-code tension (joint MSM vs. two-step) is resolved: fix_rho=True is the primary estimator; joint mode is robustness only.
- c₀_hat = DiD_delta in event_study.py:estimate_rho_c0() is correctly labeled as an upper bound / warm-start, not the structural estimate.

**Why:** Chapter 2 dissertation document requested by Bastien as methods appendix suitable for top-5 journal submission.
**How to apply:** Use the document's framing (lower bound / identified interval) whenever discussing ĉ₀_m results. The σ̂₁_m = 0 result should be foregrounded in any draft section on model validation.
