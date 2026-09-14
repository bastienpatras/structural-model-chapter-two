---
name: identification_strategy
description: Detailed notes on the DiD + MSM identification strategy and its known weaknesses, updated 2026-04-21 — LARGELY SUPERSEDED, see review_2026-09 note below before relying on this
type: project
---

**⚠ Status note (2026-09-14, see [[review_2026-09_paper_code_review]] for full detail):** several
items below are now stale relative to `paper-real-estate/sections/04-structural-draft.tex` and
`src/estimation.py` at rev `ee0e311`. Specifically: the "critical directional error" on ĉ₀_m's
upper/lower bound (line ~62 below) is confirmed fixed — the paper now correctly calls ĉ₀_m an
upper bound throughout. The "joint MSM vs. two-step narrative" tension (lines 23-28) is resolved:
`estimate_msm(fix_rho=True)` is now explicitly documented as "the primary estimator" (closed-form
two-step inversion, no joint optimisation); `fix_rho=False` joint mode is explicitly labeled
robustness-only. The σ̂₁=0 "validation" claim (line 67-68 below) is **no longer made in the
paper** — §4.1 now explicitly disclaims it as an imposed assumption, not a tested restriction. Re-
read the current section text before citing any of the pre-2026-09 findings below as live paper
claims — they were accurate readings of an earlier draft, not of the current one.

**DiD event study (first stage — ρ_m):**
- Pre-reform (≤ Jun 2021): DPE not legally opposable, ρ_m ≈ 0
- Post-reform (≥ Jul 2021): DPE legally binding, ρ_m > 0 market-specific
- Estimators: DiD_β₁_m = (p̄_ABC − p̄_EFG)_post − pre; DiD_Δ_m = (p̄_∅ − p̄_EFG)_post − pre
- Structural inversion: ρ̂_m = DiD_Δ_m / (DiD_β₁_m · ê*_m)
- ê*_m computed directly from ADEME match (no model estimation needed)
- Code: src/event_study.py:compute_did(), estimate_rho_c0()

**Bartik instrument:** Failed (F-stat 1.0–1.6). Root cause: bouclier tarifaire decoupled household from TTF wholesale gas prices Oct 2021–2023. Archived in src/instrument.py. Do not revisit.

**MSM second stage (c₀_m):**
- Only active moment: m₄ = σ̂₀_m (hiding rate among K=1, θ=0 sellers)
- DROP_MOMENTS = [0, 1, 2, 4] — drops m₁ (fit by construction), m₂ (fit by construction), m₃ (selection-contaminated), m₅ (overid test)
- φ-reparameterisation: c₀_m = φ_m · Δ(e₀; ρ_m), enforces interior equilibrium algebraically
- Code: src/estimation.py:estimate_msm(), msm_objective_pooled() with phi_mode=True

**Key identification tension (important for referee response):**
- Paper narrative: DiD identifies ρ_m first; MSM then pins c₀_m given ρ̂_m (sequential)
- Code reality: estimate_msm() jointly optimises over [ρ_1,...,ρ_M, φ_1,...,φ_M] with only m₄ active
- With 2M parameters and M active moments, the system is technically under-identified unless ρ_m is treated as known
- The DiD estimate is only a warm-start for ρ_m in the joint optimisation; ρ_m is allowed to move freely
- This tension needs to be resolved: either (a) fix ρ̂_m at DiD value and run MSM only for c₀, or (b) include m₃ (DiD_Δ) as an active moment to identify ρ jointly with c₀

**ρ̂_m clipping:**
- ~15/62 apartment markets (24%) excluded because DiD_β₁ ≤ 0 (EPC premium didn't rise post-reform)
- These are not random markets — likely low-β₁, low-ρ markets where identification is weakest
- Exclusion is hard to justify without showing these markets have similar observable characteristics to included ones

**Equilibrium regime consistency:**
- All 57 apartment and 91 house markets in final sample must be in "mixed_strategy" regime
- Markets in "full_unraveling" or "partial_separation" are excluded after the rescue pass
- This selection is on an endogenous model-based criterion — a careful referee will note this

**Key findings from 2026-04-22 targeted review of §4.1 identification text (user-requested critique):**

Directional bound confirmed resolved: paper at lines 389, 419, 469, 477 correctly labels ĉ₀_m as an upper bound. Prior "critical directional error" flag (from earlier session) is closed.

Five referee pressure points identified in §4.1:
1. Supply-side stability is unverified at the reform date — listing data begin 2021Q3, ADEME data exist independently but pre/post audit flow is not plotted
2. Flat pre-trends are jointly identified across both gaps (β₁ and Δ), but both could shift together under supply composition changes — the DiD identifies a ρ_m * e*_m compound, not ρ_m alone, unless e*_m is stable
3. "Audit stock is predetermined" claim is not documented with any lead-time data; median DPE scheduling lag is unknown
4. Reform may also have changed audit obligation thresholds (not just legal opposability), making it a demand+supply shock
5. COVID overlap in pre-period (2020–2021) creates a confound — housing market activity compressed; price gaps may have been suppressed mechanically

ADEME registry test proposed: plot monthly new-audit volume by market (from ADEME independently of listings), centered on July 2021. A structural break in audit flow at the reform would falsify the supply-stability assumption. No break strengthens it.

**Key findings from 2026-04-22 targeted review of identification and results sections:**

ρ̂_m "structural feature" framing (Q1):
- Composition-bias argument is logically flawed: ê*_m already corrects for uninformed sellers, so composition bias does not explain ρ̂_m > 1 after insertion of ê*_m. Residual excess must be measurement error in β̂₁_m or model misspecification.
- Thin-cell attenuation argument is valid but untested: no scatter of ρ̂_m vs. min-cell-volume provided.
- Cross-type test (apartment vs. house in same zone) not performed.
- Year-by-year ρ̂ (0.608–0.644 for apt) vs. pooled ρ̂ (0.950) is unexplained and contradicts "structural feature" framing.

Lower-bound framing for ĉ₀_m (Q2):
- CRITICAL DIRECTIONAL ERROR: paper says clipping ρ̂_m to 1 makes ĉ₀_m a lower bound; algebra shows the opposite (ĉ₀_m = ρ̂_m·β̂₁_m·ê*_m is increasing in ρ̂_m, so clipping up to 1 from true interior value inflates ĉ₀_m, making it an upper bound, not a lower bound). Must be corrected before circulation.

Year-by-year inconsistency (Q3):
- Pooled ρ̂ (apt: 0.950) is ~50% higher than any single-year ρ̂ (0.608–0.644). Most likely explanation: volume filter selects different (larger, higher-premium) markets for pooled vs. year-specific estimation. Year-specific note says "DiD held fixed" — this means year-by-year ρ̂ variation is only through σ̂₀_m, not ρ̂_m; the robustness table is mislabeled.

σ̂₁_m = 0 validation (Q4):
- Validation is likely a counting artifact (thin K=1,θ=1 cells), not a behavioral finding. Paper should report raw K=1,θ=1,d=0 counts per market.

Exclusion restriction (Q5):
- Critical unaddressed threat: c₀_m likely increased at the reform date (DPE became legally opposable → greater seller legal exposure). DiD conflates ∆ρ_m and ∆c₀_m.
- θ̄_m likely changed at reform (DPE 2012 → DPE 2021 methodology change reclassified many properties).
- COVID overlap in pre-period not addressed.

Full-unraveling regime (Q6):
- Δ̂_m ≤ 0 is inconsistent with the model's full-unraveling equilibrium (which predicts premium > 0, not ≤ 0). These markets should be dropped as "no identifying variation" not labeled "full unraveling."
- Including 25 full-unraveling house markets with ρ̂_m = 0 in pooled averages dilutes estimates using markets where identifying variation is absent or reversed.
