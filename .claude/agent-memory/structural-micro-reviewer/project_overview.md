---
name: project_overview
description: Overview of the structural estimation repo for "Mandatory Disclosure and Housing Market Dynamics" (Patras 2024), updated after second full review 2026-03-28
type: project
---

This repo is the replication codebase for Chapter 2 of Bastien's dissertation.

**Paper topic:** Why do non-disclosing apartments (missing EPC score) trade at a 6pp premium over energy-efficient disclosers in France after 2021 mandatory EPC disclosure? Classical unraveling theory predicts disclosure should separate good from bad — but the market rewards opacity.

**Explanation:** Non-disclosure pools two distinct groups: (1) strategic hiders (informed sellers concealing bad EPC), and (2) uninformed sellers (genuinely don't have the EPC yet — costly, time-consuming audit). Buyers cannot distinguish the two, so silence is ambiguous rather than damning, supporting a premium to non-disclosure.

**Key structural parameters to estimate:**
- ρ_m ∈ [0,1]: share of EPC-sensitive buyers per market (market-specific)
- c₀ ≥ 0: hiding cost — described as COMMON across markets in the paper, but ESTIMATED MARKET-SPECIFICALLY in the code (critical mismatch, flagged 2026-03-28)
- Both identified via MSM matching 5 moments per market (code uses 5, not 4 as docstrings claim)

**Hiding cost structure:**
- Paper (Sec 3.2): C(θ,d) = c₀ + θ·c₁ (two-component: c₀ common, c₁ extra for high-quality hiders)
- Code: only c₀ is implemented; c₁ is never defined or estimated
- c₁=0 is an implicit normalization that is not declared anywhere

**Pipeline (main.py, 5 steps):**
1. `data_prep.py` — Load listings + ADEME registry, classify into 4 groups, compute market stats
2. `hedonic.py` — OLS hedonic regression on truthful disclosers → β̂₁, market FEs, demand scale
3. `moments.py` — Extract 5 data moments per market; compute model-implied counterparts
4. `estimation.py` — MSM estimation via scipy.optimize; bootstrap SEs
5. `outputs.py` + `validation.py` — LaTeX tables + HTML figures

**Model core (model.py):**
- Binary θ ∈ {0,1} EPC quality, binary K ∈ {0,1} information status
- Belief function e(σ₀) = (1-π)θ̄ / [π(1-θ̄)σ₀ + (1-π)]  (Eq. 62, simplified for σ₁*=0)
- Logistic demand G(v-p), seller profit = exp(p)·Γ(p), optimal price from numerical FOC
- 3 equilibrium regimes: full unraveling / mixed strategy / partial separation
- Two profit_gain_hiding implementations: linear approximation (ρ·β₁·e) and full structural — used inconsistently
- Policy output: optimal renovation subsidy S*_m = max{R̂_m - R̄_m, 0}

**Known bugs (as of 2026-03-28 review):**
- outputs.py line 635: passes e_star (equilibrium belief ≈ 0.2-0.5) as the `scale` argument to figure_equilibrium_phase_diagram instead of the logistic demand scale. Corrupts the figure.
- merge_datasets (data_prep.py lines 183-187): overwrites theta=0 for all informed non-disclosers, mechanically making the σ₁=0 test pass trivially — destroys a genuine empirical test
- c₀ is estimated market-specifically (c0_hat is a dict) despite paper claiming it is common
- J-test degrees of freedom: code uses 4M-2M=2M; should be 3M-1 if c₀ is common
- Moment count: docstrings say 4 moments, code uses 5 (includes σ̂₁_m as 5th moment in objective)

**Data status:** Real data not yet connected (load_listings / load_ademe raise FileNotFoundError). Pipeline runnable with `--synthetic` flag using `make_synthetic_data()`. listings.parquet and listings_enriched.parquet exist in data/ but are not used by the main pipeline (likely outputs of data/collect_listings.py). Real ADEME registry not present.

**Results already in repo:** results/tables/ (4 LaTeX tables) and results/figures/ (4 HTML figures — NOT PDFs, kaleido not in requirements.txt).

**Why:** Chapter 2 of Bastien's dissertation. Paper is in draft stage, real data integration is pending. Critical fixes needed before the paper can be circulated.
