---
name: project_overview
description: Full overview of the structural estimation repo for "Mandatory Disclosure and Housing Market Dynamics" (updated 2026-04-21 after deep estimation-strategy review)
type: project
---

This repo is the replication codebase for Chapter 2 of Bastien's dissertation (Sciences Po Paris).

**Paper topic:** Non-disclosing apartment listings trade at a ~6pp premium over energy-efficient disclosers in France after the July 2021 mandatory EPC reform — the opposite of what classical unraveling theory predicts. The paper builds a structural Dye-type disclosure model with (i) seller information heterogeneity (share π of informed sellers) and (ii) buyer preference heterogeneity (share ρ of EPC-sensitive buyers) to explain this.

**Key structural parameters:**
- π_m: share of informed sellers — directly measured from ADEME registry match (no estimation)
- θ̄_m: mean quality of informed sellers — directly measured
- σ̂₀_m: observed hiding rate among K=1, θ=0 sellers — directly measured
- ρ_m: share of EPC-sensitive buyers — identified via DiD event study around July 2021 reform (closed-form inversion: ρ̂_m = DiD_Δ_m / (DiD_β₁_m · ê*_m))
- c₀_m: hiding cost — identified in 2nd stage via MSM matching moment m₄ (equilibrium hiding rate), given ρ̂_m

Both ρ_m and c₀_m are now estimated MARKET-SPECIFICALLY (prior concern about common c₀ is resolved — paper and code now both market-specific).

**Two-stage identification:**
1. DiD event study: reform shifts ρ_m from ≈0 to ρ_m^post; closed-form ρ̂_m from structural inversion
2. MSM: single active moment m₄ (σ̂₀_m); DROP_MOMENTS=[0,1,2,4]; only m₄ active

**Critical tension (open as of 2026-04-21):**
- Paper says "MSM minimises Q_m(ρ_m, c₀_m)" — both ρ and c₀ are free parameters in the objective.
- But the MSM has only ONE active moment (m₄ = hiding rate). With 2 unknowns and 1 moment, the system is under-identified.
- The resolution: ρ_m enters the MSM as a FREE parameter jointly optimised with c₀_m — it is NOT fixed at the DiD estimate before MSM runs. The code optimises over [ρ_1,...,ρ_M, φ_1,...,φ_M] jointly. The DiD estimate is only used as a warm-start.
- This means ρ_m is ONLY identified by m₄ in the MSM (no active price moments), making identification of ρ_m from the hiding rate alone potentially fragile and subject to flat likelihood regions.
- The paper presents a two-step narrative (DiD for ρ, then MSM for c₀ given ρ) but the actual code runs a joint optimisation over both parameters with only one active moment.

**Known discrepancy between paper and code (open as of 2026-04-21):**
- Paper (Section 4, last paragraph) says: "Given the first-stage estimate ρ̂_m, equation (eq:indifference) has a unique solution in c₀_m..."  — this description implies ρ_m is plugged in as fixed.
- Code: ρ_m is a free variable in estimate_msm(); warm-started from DiD but jointly optimised.
- ESTIMATION_STRATEGY.md (Section 12) lists this as an "open issue" (DiD β₁ ≤ 0 for ~24% of apartment markets).
- Documentation note: the docstring in estimate_msm() says "4 moments, 2 unknowns" but only 1 moment is active.

**event_study.py bug (open):**
- In estimate_rho_c0(), c0_hat is set to DiD_delta directly (line 359), not via the MSM equilibrium condition. This is documented as an "upper bound" for warm-starting but the EventStudyParams dataclass stores it as c0_m, which could be confused with the structural estimate if used downstream.

**c₁ parameter:**
- Paper introduces c₁ (extra hiding cost for high-quality hiders) in Section 2.3 but never estimates it.
- Corollary (cor:hq_disclose) shows high-quality sellers always disclose under α_k=β_k — making c₁ irrelevant. This is internally consistent but the parameter is introduced and then silently normalized out.

**Bootstrap SEs:** Framework exists in src/estimation.py:bootstrap_se(); described in paper as B=500 resamples with percentile CI. Status: pending execution (slow).

**Data:** Real data is in data/ (listings_enriched_APARTMENT/HOUSE.parquet, index files). ADEME registry integrated via ADEME/ directory.

**Pipeline:** src/ contains model.py, moments.py, estimation.py, event_study.py, hedonic.py, data_prep.py, validation.py, outputs.py, viz/. Main orchestration via analysis.ipynb.

**Results already in repo:** results/figures/ (HTML, 4 figures), results/tables/ (various outputs).

**Why:** Chapter 2 of Bastien's dissertation. Paper in active draft stage, being prepared for circulation.
