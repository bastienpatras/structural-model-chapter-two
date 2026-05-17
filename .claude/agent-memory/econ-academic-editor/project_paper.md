---
name: project_paper
description: Core argument, identification strategy, estimates, and notation conventions for "Mandatory Disclosure and Housing Market Dynamics"
type: project
---

**Paper:** "Mandatory Disclosure and Housing Market Dynamics" — Bastien Patras, Sciences Po Paris.

**Core puzzle:** After France's July 2021 mandatory EPC disclosure reform, non-disclosing properties trade at a ~6 pp premium over energy-efficient disclosers — the opposite of classical unraveling theory.

**Key notation (maintain across sessions):**
- π_m: share of informed sellers (ADEME match rate) in market m
- ρ_m: share of EPC-sensitive buyers — first-stage DiD parameter
- c₀_m: hiding cost per market — second-stage MSM parameter
- β₁_m: EPC quality premium (hedonic, from truthful disclosers)
- Δ_m: non-disclosure premium (DiD, upper bound on c₀_m, NOT point estimate)
- σ₀_m: equilibrium hiding rate of informed low-quality sellers (K=1, θ=0, d=0)
- ê*_m: equilibrium belief — directly observed from ADEME frequencies (no estimation needed)
- θ ∈ {0,1}: high/low energy efficiency; θ=1 iff EPC ≤ D (A–D)
- K_i: seller's information status (1 = certified audit exists in ADEME)

**Identification strategy (two-stage, closed-form — NOT MSM optimization):**
1. DiD around July 2021 reform: pre-reform ρ_m ≈ 0 (DPE not legally opposable); post-reform ρ_m > 0. ρ̂_m = Δ̂_m / (β̂₁_m · ê*_m).
   - CRITICAL: ρ̂_m > 1 in ALL 40 apartment markets and 92/107 house markets before clipping. ρ_m is set-identified, not point-identified, in most markets. ρ_m = 1 is a working assumption for clipped markets.
   - Point identification of ρ_m: 8 house markets only (interior solution).
2. Closed-form inversion (NOT MSM): ĉ₀_m = ρ̂_m · β̂₁_m · ê*_m(σ̂₀_m). Exact one-moment, one-parameter inversion. No L-BFGS-B, no reparametrization, no rescue pass.
   - ĉ₀_m is a lower bound when ρ_m = 1 is the working assumption (true ρ_m ≤ 1 implies true c₀_m ≥ ĉ₀_m).
   - Houses: partially identified interval ĉ₀_m ∈ [ρ̂_m · β̂₁_m · ê*_m(σ̂₀_m), Δ̂_m] = [0.018, 0.034] on average.
   - φ_m reparametrization: belongs to joint robustness mode only (fix_rho=False); do NOT describe in primary estimator.
- Bartik instrument FAILED (F=1.0–1.6) due to bouclier tarifaire. Correctly relegated to footnote. Do not revisit.
- DiD Δ̂_m is an upper bound for c₀_m — contaminated by uninformed sellers (~85% of non-disclosers for apts, ~75% for houses).
- Exclusion restriction (§4.1): ONLY two pieces of evidence — (1) ADEME match rate continuity at reform date; (2) flat pre-trends for β₁_m,t and Δ_m,t. The fabricated "third piece" (Chapter 1 near-zero EPC predictive power in transaction prices) has been permanently removed. Do not reintroduce it.
- c₀_m threat to exclusion restriction: acknowledged in a footnote at end of §4.1 exclusion restriction paragraph. The reform made the DPE legally opposable, potentially raising sellers' legal exposure from non-disclosure (shifting c₀_m upward at the reform date). If so, ρ̂_m is biased upward — reinforces upper-bound interpretation. This is the established and complete treatment; do not expand it into a separate paragraph.
- ê*_m measured directly from ADEME frequencies — no model estimation needed.

**Main estimates (pooled 2022–2024, current configuration):**
- Apartments: 40 markets (DiD volume filter); ρ̂_m = 1 in all 40 (clipped); mean ratio Δ̂/(β̂₁·ê*) ≈ 7.7
- Houses: 100 markets; 8 interior-identified; 67 clipped to ρ̂=1; 25 Cost-Deterred Hiding (Δ̂<0 → ρ̂=0)
- ĉ₀_m lower bound: ~1.6% for apts, ~1.8% for houses (log pts); house identified interval [0.018, 0.034]
- NOTE: Stored estimates of 57 apt / 91 house markets and mean ρ̂ = 0.700/0.500 correspond to an OLDER model configuration. Current run uses stricter volume filter and closed-form inversion. Do not cite old numbers.

**Data:**
- SeLoger listings (2021Q3–2024Q4): 843,621 apts, 687,878 houses
- ADEME registry: matched at listing level using address+area+floor
- Four-group classification: truthful disclosers, strategic hiders (3.5% apt / 1.1% house), genuinely uninformed, non-certifiable disclosers
- Strategic hiders among K=1: 6.9% apts, 2.7% houses

**Policy extension:**
- Renovation threshold R̄(π,ρ,X) = market premium for verified high quality + c₀
- Optimal subsidy S*(π,ρ,X) = max{R̂(X) − R̄, 0}
- Key result: ∂S*/∂c₀ = −1: enforcement and subsidies are perfect substitutes at the margin (CAS corner only; = 0 in PP)
- Uniform national subsidies (e.g., MaPrimeRénov') are generically inefficient
- §7.5 (label: sec:policy_empirical) inserted 2026-05-15: "Renovation Subsidies in French Housing Markets: Empirical Magnitudes and Spatial Heterogeneity"
  - Figures: fig_subsidy_threshold_distribution.pdf (label fig:subsidy_threshold_dist), fig_subsidy_grid.pdf (fig:subsidy_grid), fig_subsidy_regime_breakdown.pdf (fig:subsidy_regime_breakdown), fig_subsidy_map_R500+R1000 combined (fig:subsidy_maps)
  - Empirical: apts mean R̄=€165/m², median €151; houses mean €128, median €134
  - At R̂=250: 31/40 apt mkts need subsidy; 91/100 house mkts
  - Aggregate UB fiscal cost: apts €6.4/15.7/34.7 bn; houses €9.1/23.0/51.4 bn at R̂=250/500/1000
  - R250 map and threshold-vs-β₁ diagnostic relegated to appendix

**Equilibrium regime labels (finalized 2026-04-20 — do not revert):**
- σ₀*=0: "Cost-Deterred Hiding" (NOT "Full Unraveling" — this is not Milgrom/Grossman unraveling; pool is uninformed, silence is uninformative)
- σ₀*=1: "Complete Adverse Selection" (NOT "Partial Separation" — all informed low-quality sellers hide, pool maximally contaminated)
- σ₀*∈(0,1): "Partial Pooling" (NOT "Mixed Strategy" — interior mixing in adverse selection literature)
- Exact premium formula: p₀*−p₁* = ρ·β₁·(1−π)θ̄/(1−πθ̄) — the ∝ notation was corrected to this closed form
- (1−π)θ̄/(1−πθ̄) is e* = equilibrium pool quality = fraction of high-quality among non-disclosers when σ₀*=1
- IFT signs in Partial Pooling: dσ₀*/dc₀ < 0 (Φ'<0); dσ₀*/dρ > 0
- π and c₀ are policy substitutes (both reduce hiding, distinct channels); stated as such in \prop{comparative_statics}
- Comparative statics now consolidated into one proposition (\label{prop:comparative_statics}); old \label{prop:pi}, \label{prop:rho}, \label{prop:c0} are removed — do not reference them

**Model subsection conventions (established 2026-04-17):**
- bp-template.cls defines \begin{assumption}[name] environment (numbered, section-scoped) — use this, not \noindent\textbf{Assumption...}
- No Falsification Assumption: d=1 requires K_i=1; self-enforcing under registry deterrence; Extension 2 is the formal treatment (ensure label exists)
- π is measured from ADEME registry match rate — if treated as directly observed, do not say "structurally estimated"
- Simultaneous d + p^list reflects Article L271-4 CCH institutional constraint (not just a modelling choice)
- c₀ maps to loi ALUR legal liability (Loi no. 2014-366, consider Article 54 footnote)
- Rental ban timeline: new G+ rentals banned Jan 2025; all G Jan 2028; F Jan 2034 — specify which date when referencing investor incentives
- α_k = β_k benchmark: conservative; under α_k < β_k, ρ̂ is a lower bound — always state directional implication
- ρ_m identified from DiD cross-market variation in price response to July 2021 reform — mention this when introducing ρ in model sections
- Buyer type partition: EPC-sensitive = primary-residence owner-occupiers + investors facing rental ban; EPC-insensitive = vacation buyers, cash investors in liquid markets

**Style rules confirmed for this paper:**
- No em-dashes anywhere (replace with comma, semicolon, colon, or parentheses)
- No bullet lists in running prose (convert to flowing text)
- No informal phrasing (no "looks at", "check if", "Note that", "Recall that", "We now turn to", "In what follows", etc.)
- No telegraphic transitions ("Figure X shows that Y" → "Y (Figure X)"; "Turning to X" → just state content; "The clean statement is..." → just state it)
- No bold paragraph headers acting as bullet labels (convert to continuous narrative paragraphs)
- Bold blocks to PRESERVE: \noindent\textbf{Assumption...}, \noindent\textbf{Partial Pooling Closed Form...}, \medskip\noindent\textbf{Remark (...)} — these are definitional/structural
- AER/QJE register throughout
- §7.5 (sec:policy_empirical) was already rewritten — do not touch it in style sweeps
- Appendix proofs (everything after \appendix) are out of scope for style sweeps

**Why:** This is a chapter 2 of Bastien's thesis, targeting top-5 journals. Consistent framing across editing sessions is essential to avoid drift in notation or claims.
**How to apply:** Always use the notation above. Never describe Δ_m as a point estimate of c₀_m. Always treat the ADEME data advantage as the paper's key empirical contribution. Always check that forward-references (Extension 2, section labels) are consistent with what exists in main_concise.tex before recommending them.
