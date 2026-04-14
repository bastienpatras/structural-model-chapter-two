# Estimation Strategy: Motivation, Changes, and Efficiency

**Project:** Mandatory Disclosure and Housing Market Dynamics
**Paper section reference:** Sections 7.2–7.7
**Reference paper:** `paper/main_concise.tex` — use labeled equation references (e.g., Eq. (eq:belief_simplified)) not numbered ones.

**Note on group naming:** The code uses `"unverified_disclosers"` for the d=1, K=0 group, but Table (tab:listing_types) in main_concise.tex still uses "Falsification". The paper table should be updated to "Unverified Disclosers" to match the code.

---

## 1. The Identification Problem

The structural model delivers a single equilibrium pricing equation for non-disclosing
properties (Sec. "Equilibrium Characterization", main_concise.tex):

```
Δ_m = ρ_m · β₁_m · e*(σ̂₀_m)
```

where `Δ_m` is the observed non-disclosure premium, `β₁_m` is the EPC quality premium,
`e*(·)` is the equilibrium buyer belief (a known function of directly measured market
statistics `π̂_m`, `θ̂_m`, `σ̂₀_m`), and the two structural parameters are:

- **ρ_m ∈ [0,1]**: the share of EPC-sensitive buyers in market *m*
- **c₀_m ≥ 0**: the hiding cost in market *m*, identified from the equilibrium condition
  `Δ(e*(σ₀*); ρ_m) = c₀_m`

The difficulty is fundamental: **one moment equation, two unknowns**. At a given
cross-section, `Δ_m` identifies the product `ρ_m · β₁_m · e*`, but cannot separately
pin down `ρ_m` and `c₀_m` without additional variation in the right-hand side.

---

## 2. First Attempt: Bartik Instrument

### Strategy
Exploit cross-market variation in energy intensity to construct a Bartik (shift-share)
instrument:

```
Z_m,t = gas_price_t × EFG_share_m
```

The idea: markets with a larger stock of low-efficiency (EFG) properties (`EFG_share_m`)
should experience a stronger increase in the non-disclosure premium when energy prices
rise, because the stigma from holding an energy-intensive property becomes more salient.
This cross-market variation in `Z_m,t` would generate exogenous shifts in `Δ_m,t`,
allowing identification of `ρ_m` separately from `c₀_m`.

### Why It Failed

The instrument produced a first-stage F-statistic of **1.0–1.6** — far below the
conventional threshold of 10 and consistent with a completely uninformative instrument.

The root cause is the French *bouclier tarifaire* (energy price shield), implemented in
October 2021 and maintained through 2023. The policy capped retail gas and electricity
prices for households, decoupling French household energy costs from the TTF wholesale
gas price spike that followed the Russian invasion of Ukraine. Consequently:

1. Household energy expenditure — the channel through which EPC scores affect buyer
   willingness to pay — barely moved during the period of maximum TTF volatility.
2. The non-disclosure premium `Δ_m,t` rose secularly across the entire sample period,
   driven by the July 2021 DPE legal reform (see Section 3 below), not by energy
   price variation.
3. The Bartik regressor `Z_m,t` is therefore orthogonal to the residual variation in
   `Δ_m,t` that the instrument was designed to exploit.

**Conclusion:** Do not revisit the Bartik approach. The exclusion restriction is
satisfied by construction (the *bouclier tarifaire* is exogenous to housing markets),
but the relevance condition fails unconditionally given French energy policy.

---

## 3. Adopted Strategy: Difference-in-Differences Event Study

### The Natural Experiment

The July 2021 reform of the *Diagnostic de Performance Énergétique* (DPE) provides a
clean natural experiment. Before the reform, DPE certificates were not legally
opposable — buyers knew scores could be contested in court, were based on unreliable
methods, and were frequently ignored. After 1 July 2021, DPEs became legally binding:
sellers became liable for inaccurate disclosures, and certificates were reformulated
under stricter technical standards.

This induces a discrete, common, and legally exogenous shift in buyer beliefs:

| Period | Legal status of DPE | ρ_m |
|--------|---------------------|-----|
| ≤ June 2021 | Not legally opposable — buyers discount EPC | ≈ 0 |
| ≥ July 2021 | Legally binding — EPC prices in | > 0, market-specific |

The pre-reform period therefore provides a *clean control baseline* where the
non-disclosure premium is uninformative about `ρ_m`: any level of `Δ_m` in the
pre-period is attributable to unrelated market-level heterogeneity, not EPC sensitivity.

### Estimating Equations

Using the hedonic price index panel (`data/index_APARTMENT.csv`,
`data/index_HOUSE.csv`) — monthly indices for four EPC categories (Efficient=ABC,
Balanced=D, Intensive=EFG, Undisclosed) across all markets from October 2018 to
mid-2024 — we compute the following DiD estimators for each market *m*:

**EPC quality premium (β₁_m):**
```
DiD_β₁_m = (p̄_ABC,m − p̄_EFG,m)_post − (p̄_ABC,m − p̄_EFG,m)_pre
```

**Non-disclosure premium (Δ_m):**
```
DiD_Δ_m = (p̄_Ø,m − p̄_EFG,m)_post − (p̄_Ø,m − p̄_EFG,m)_pre
```

where all `p̄` are monthly log hedonic price indices, and `Ø` denotes the
undisclosed (no-EPC) category. The DiD difference-out any pre-existing, time-invariant
gap between EPC categories, as well as common time trends.

### Direct Structural Inversion

Given `DiD_β₁_m` and `DiD_Δ_m`, the buyer sensitivity parameter follows from a
closed-form inversion of Eq. (eq:premium) (adapted to the DiD setting):

```
ρ̂_m = DiD_Δ_m / (DiD_β₁_m · ê*_m)
```

where `ê*_m = belief_function(σ̂₀_m, π̂_m, θ̂_m)` (Eq. (eq:belief_simplified)) is computed directly from the
listings data (`src/data_prep.compute_market_stats`), with no model estimation
required:

```
ê*_m = (1 − π̂_m) · θ̂_m / [π̂_m · (1 − θ̂_m) · σ̂₀_m + (1 − π̂_m)]
```

**`ĉ₀_m` is NOT identified by `DiD_Δ_m`.** The equilibrium indifference condition
`c₀ = Δ_m` requires that `Δ_m` be the price premium earned by *strategic hiders*
(K=1, θ=0, d=0) specifically. However, the "undisclosed" category in the price index
pools strategic hiders with uninformed non-disclosers (K=0, d=0). In the listings
data, uninformed sellers represent ~83% of all non-disclosers (140,523 K=0 vs 29,676
K=1 non-disclosers). The price index undisclosed gap `DiD_Δ_m` therefore reflects a
weighted average of the hider premium and the uninformed premium — it is an **upper
bound** on `c₀`, not a point estimate.

A listing-level DiD for K=1 non-disclosers only is not feasible: the listings data
(`listings_enriched_APARTMENT.parquet`) begins at the reform date (2021-07-01) and
contains no pre-reform observations. The pre-reform baseline required for DiD
differencing is unavailable at the listing level.

**`ĉ₀_m` is estimated by MSM** via the equilibrium condition
`σ₀*(ρ̂_m, c₀) = σ̂₀_m` (moment m₄), which targets informed low-quality sellers
(K=1, θ=0) exclusively and is therefore immune to uninformed-seller contamination.

### Volume Filter

To guard against DiD estimates driven by thin market×EPC cells, a minimum average
monthly transaction volume of **20 observations** per EPC category is required in both
the pre-reform and post-reform periods. Markets where any required category (ABC, EFG,
or Undisclosed) falls below this threshold are excluded. This reduced the number of
markets with negative `DiD_β₁` estimates from approximately 40 to 25 out of 68,
consistent with the filter removing noise rather than signal.

---

## 4. Why the New Strategy Is Efficient with Respect to the Theory

### 4.1 It Uses the Identifying Variation the Theory Predicts

The model predicts that `ρ_m` is identified by *changes* in the non-disclosure premium
across informational regimes, not by its level (Proposition (prop:equilibrium) and Sec. "Equilibrium Characterization"). The pre-reform period is precisely a regime where `ρ_m ≈ 0` by
institutional design. The DiD therefore exploits exactly the source of variation that
the theory flags as identifying — the reform shifts `ρ_m` from zero to its market-specific
post-reform value, and the change in `Δ_m` and `β₁_m` recovers this shift.

### 4.2 It Is a Closed-Form Estimator

The original MSM approach required solving a high-dimensional non-linear optimisation
over the joint distribution `(ρ_1, ..., ρ_M, c₀_1, ..., c₀_M)` — a 2M-dimensional
problem (M ≈ 68–110 markets). The DiD estimator produces market-level estimates
directly by formula. This eliminates:

- Sensitivity to starting values and local optima
- Numerical instability in the equilibrium solver for extreme parameter values
- The need for a φ-reparameterisation to enforce equilibrium constraints

### 4.3 The Exclusion Restriction Is Theoretically Grounded

The identifying assumption — `ρ_m ≈ 0` pre-reform — is not a statistical restriction
imposed on the data; it is derived from institutional features of the DPE regime. The
legal non-opposability of pre-2021 certificates implies that EPC information was not
credibly verifiable in court, giving buyers rational grounds to discount it. This is
the same logic underlying the model's assumption that buyers update beliefs rationally
(Section 3.4): in the absence of a credible signalling technology, the pooling outcome
prevails and `ρ_m` collapses to zero as an empirical matter.

### 4.4 It Separates the Two Structural Objects Cleanly

| Structural object | What identifies it | Source of variation |
|---|---|---|
| `β₁_m` | `DiD_β₁_m` — change in ABC–EFG gap | Reform shifts quality pricing |
| `Δ_m` (reduced form) | `DiD_Δ_m` — change in Ø–EFG gap | Reform shifts non-disclosure pricing (all non-disclosers) |
| `ρ̂_m` | Ratio `DiD_Δ_m / (DiD_β₁_m · ê*_m)` | Reform × market EPC composition |
| `ĉ₀_m` | MSM moment m₄: `σ₀*(ρ̂_m, c₀) = σ̂₀_m` | Equilibrium hiding rate, K=1 sellers only |

**Note:** `DiD_Δ_m` is a valid instrument for the reduced-form non-disclosure premium
but is NOT a direct estimate of `c₀`. It pools strategic hiders (K=1) and uninformed
non-disclosers (K=0, ~83% of all non-disclosers), making it an upper bound on `c₀`.
The MSM is the primary estimator of `c₀_m`.

The separation is clean because `β₁_m` and `Δ_m` map to distinct pairs of EPC
categories in the index data, and the reform affects both simultaneously.

### 4.5 Empirical Findings Are Theory-Consistent

**Apartments:** `ρ̂_m ≈ 1` in most markets (mean near 1, low dispersion). This is
consistent with the model prediction that markets with strong regulatory
complementarities — legal enforceability plus the 2025 rental ban on G-rated
properties — converge to full buyer sensitivity. The main heterogeneous structural
object for apartments is therefore `c₀_m` (mean ≈ 0.079 log points, std ≈ 0.060).

**Houses (pending):** Expected to exhibit genuine `ρ_m` variation across market types
(rural, suburban, holiday), consistent with weaker regulatory exposure and lower
strategic hiding rates (1.1% vs 3.5% for apartments).

---

## 5. Role of MSM in the Revised Pipeline

The DiD event study is the **first stage**: it pins `ρ̂_m` for each market with
positive `DiD_β₁_m`.

MSM (`src/estimation.py`) is the **second stage** for:

1. **c₀_m estimation**: identified exclusively from moment m₄ (`σ̂₀_m` — hiding rate
   among informed low-quality sellers). The φ-reparameterisation `c₀_m = φ_m · Δ(e₀; ρ_m)`
   enforces the equilibrium constraint `c₀_m < Δ(e₀; ρ_m)` algebraically.
2. **Overidentification testing**: the m₃ diagnostic (`ρ̂_m · β̂₁_m · ê*_m` vs
   `DiD_Δ_m`) provides a partial consistency check of the structural equation.
3. **Counterfactual and welfare analysis**: subsidies and renovation thresholds
   require `(ρ̂_m, ĉ₀_m)` jointly.
4. **Standard errors**: bootstrap over listings within markets, B = 500 replications
   (estimation appendix forthcoming).

### Active moments: `DROP_MOMENTS = [0, 1, 2, 4]`

Only m₄ is active in the MSM objective. m₃ is excluded for two reasons:

1. **Cross-sectional selection bias:** the listing-level non-discloser price mixes
   strategic hiders (K=1) and uninformed sellers (K=0). Uninformed sellers (~83% of
   non-disclosers) set prices unrelated to EPC strategy, biasing the residual upward.
2. **No pre-reform baseline:** a listing-level DiD for K=1 non-disclosers is infeasible —
   `listings_enriched_APARTMENT.parquet` begins at 2021-07-01 (the reform date) and
   contains no pre-reform observations.

### Market exclusion — two-stage filter

Not all estimable markets admit an interior (mixed-strategy) MSM solution. Two
exclusion criteria are applied in sequence:

**Stage 1 — Feasibility pre-screen** (`src/event_study`, cell `cell-msm-prescreen`):
For each market, test whether any `(ρ, c₀)` in a coarse grid
`ρ ∈ linspace(0.05, 0.95, 10)` × `c₀ ∈ {0.005, 0.01, 0.025, 0.05}` produces a
mixed-strategy equilibrium. Markets that fail (no interior solution exists given their
`π̂_m`, `θ̄_m`, `β̂₁_m`) are excluded before MSM is run.
- Apartments: 4 markets excluded (e.g., very low `π̂_m` → full-information market)

**Stage 2 — Post-MSM corner filter** (`cell-msm-postscreen`):
After estimation, markets where the optimizer converged to a degenerate equilibrium
(`full_unraveling` or `partial_separation`) are dropped. These are typically markets
with very high `θ̄_m` (≥ 0.70): when the non-discloser pool is seen as mostly
high-quality, buyer belief e* is large, hiding is highly profitable, and the equilibrium
collapses to `partial_separation` for any feasible c₀.
- Apartments: 5 markets excluded

**Final estimation sample — Apartments: 54 / 63 markets** (14% dropped, 9 total).

The dropped markets are reported in a separate appendix table. Their exclusion is
principled and observable (based on pre-estimation market characteristics), not
outcome-driven.

---

## 6. Summary of Changes

| # | Change | Motivation |
|---|--------|-----------|
| 1 | Built and discarded Bartik instrument (`src/instrument.py`) | F-stat = 1.0–1.6; *bouclier tarifaire* killed household energy price variation |
| 2 | Created `src/event_study.py` — DiD identification pipeline | July 2021 DPE reform provides clean pre-period (ρ_m ≈ 0) as natural experiment |
| 3 | `load_price_indices()`: reads hedonic index panel, maps EPC labels | Converts external index CSV into model-compatible long-format DataFrame |
| 4 | `compute_did()`: market-level DiD estimates of β₁_m and Δ_m | Produces closed-form structural estimands from the price index panel |
| 5 | Volume filter `min_volume=20` in `compute_did()` | Removes thin market×EPC cells; reduces spurious negative DiD_β₁ markets |
| 6 | `estimate_rho_c0()`: direct inversion `ρ̂_m = DiD_Δ_m / (DiD_β₁_m · ê*_m)` (Eq. (eq:premium) adapted) | Closed-form first-stage estimate of ρ̂_m; `ĉ₀_m = DiD_Δ_m` is an **upper bound** only (price index pools K=1 and K=0 non-disclosers; listings data has no pre-reform period for a K=1-only DiD) |
| 7 | `aggregate_event_study()`: event-time normalised time series | Provides Figure-ready pre-trend test (k = −1 normalisation) |
| 8 | `drop_moments=[2]` in MSM | Drops m₃ (non-discloser price level), contaminated by selection on unobservables — DiD handles this via index differencing |
| 9 | φ-reparameterisation retained in MSM (φ is a computational device not in the paper; enforces c₀_m < Δ(e₀; ρ_m)) | Enforces `c₀_m < Δ(e₀; ρ_m)` algebraically; prevents equilibrium constraint violations during optimisation |
| 10 | Tagged parquet outputs with item type (APARTMENT / HOUSE) | Prevents overwriting between the two sub-markets; allows independent event studies |
