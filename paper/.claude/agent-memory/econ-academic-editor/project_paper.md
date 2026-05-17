---
name: project-paper
description: Core paper identity, notation conventions, and empirical numbers for "Mandatory Disclosure and Housing Market Dynamics"
metadata:
  type: project
---

Paper: "Mandatory Disclosure and Housing Market Dynamics" (chapter 2, Sciences Po PhD thesis, Bastien Patras).

**Core argument:** A model of disclosure failure with two empirical departures from the classical framework: uninformed sellers and heterogeneous buyers. These sustain non-disclosure premia in equilibrium. The paper estimates the model on French housing transaction data around the July 2021 DPE reform using a DiD event study.

**Key parameters:** π (share of informed sellers), ρ (share of EPC-sensitive buyers), β₁ (verified-quality premium in log-points), c₀ (hiding cost).

**Equilibrium regimes:** Partial Pooling (PP, empirically dominant) and Cost-Deterred Hiding (CDH, minority). In PP, the renovation threshold R̄ collapses to the verified-quality premium; c₀ and π cancel.

**Renovation threshold and subsidy:** S*_m = max{R̂ − R̄_m, 0}. Two benchmarks used: R̂ = 250 €/m² (light) and R̂ = 500 €/m² (medium). The R̂ = 1000 benchmark is dropped from policy discussion.

**Key empirical numbers:**
- Apartments (40 markets): 38 PP + 2 CDH. Mean R̄_m ≈ €165/m², median €151/m². Median price/m² €2,814.
- Houses (100 markets): 75 PP + 25 CDH. Mean R̄_m ≈ €128/m², median €134/m². Median price/m² €2,196.
- At R̂=250: 77.5% apt / 91% hse markets need subsidy. Median S*|S*>0: €99/m² (apt), €116/m² (hse).
- At R̂=500: 100% apt / 98% hse need subsidy. Median S*: €349/m² (apt), €366/m² (hse).
- Aggregate upper bound: €15.5 bn (R̂=250) and €38.7 bn (R̂=500). MaPrimeRénov' annual budget ≈ €4–5 bn → implied 3–8× multiplier for medium intervention.

**Figure names (policy section):**
- fig_subsidy_threshold_distribution.pdf → fig:subsidy_threshold_dist
- fig_subsidy_grid.pdf → fig:subsidy_grid (2-column, R̂=250 and R̂=500 only)
- fig_subsidy_regime_breakdown.pdf → fig:subsidy_regime_breakdown (2 bars per panel)
- fig_subsidy_map_R250.pdf (top) + fig_subsidy_map_R500.pdf (bottom) → combined fig:subsidy_maps

**Why:** Reference for consistent empirical numbers and figure labelling across all editing sessions.

**How to apply:** Verify numbers and figure filenames against this record before accepting or writing any edits to the policy section (§7.5, sec:policy_empirical).
