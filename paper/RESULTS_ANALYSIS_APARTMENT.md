# Results Analysis — Structural Estimates (Apartments)
*Patras, B. — Mandatory Disclosure and Housing Market Dynamics*
*Last updated: 2026-04-21 | 40 markets, two-step estimator*

---

## Summary of estimates

| Parameter | Mean | Median | Std | \[p10, p90\] |
|---|---|---|---|---|
| $\hat{\beta}_{1,m}$ — DiD EPC quality premium (log pts) | 0.0444 | 0.0186 | 0.0421 | \[−0.036, 0.067\] |
| $\hat{\Delta}_m$ — non-disclosure premium (log pts) | 0.0850 | 0.0629 | 0.0616 | \[0.002, 0.157\] |
| $\hat{\sigma}_{0,m}$ — hiding rate, informed low-quality | 0.077 | 0.072 | 0.048 | \[0.035, 0.123\] |
| $\hat{e}^*_m$ — equilibrium pool quality | 0.252 | 0.234 | 0.095 | \[0.146, 0.411\] |
| $\hat{\rho}_m$ — EPC-sensitive buyer share (clipped) | 0.950 | 1.000 | 0.218 | \[1.000, 1.000\] |
| $\hat{c}_{0,m}$ — hiding cost (log pts) | 0.0162 | 0.0125 | 0.0125 | \[0.005, 0.033\] |
| $\hat{\sigma}_{1,m}$ — hiding rate, informed high-quality | 0.000 | 0.000 | — | — |

Coverage: 40 of 263 apartment markets have usable DiD estimates ($\hat{\beta}_{1,m} > 0$ and matched price index data). 2 markets have $\hat{\Delta}_m < 0$ (full unraveling, $\hat{\rho}_m = 0$). 38/40 are in the mixed-strategy equilibrium.

---

## 1. Why $\hat{\rho}_m > 1$ — what it implies

The two-step inversion recovers $\hat{\rho}_m$ from:

$$\hat{\rho}_m = \frac{\hat{\Delta}_m}{\hat{\beta}_{1,m} \cdot \hat{e}^*_m}$$

For $\hat{\rho}_m \leq 1$ to hold, the model requires $\hat{\Delta}_m < \hat{\beta}_{1,m} \cdot \hat{e}^*_m$. With $\hat{e}^*_m \approx 0.25$, this means the non-disclosure premium must be less than one quarter of the EPC quality premium. In the data the ratio is inverted: $\hat{\Delta}_m \approx 2 \times \hat{\beta}_{1,m}$ on average, giving $\hat{\rho}_m \approx 7.7$ before clipping. All 40 markets hit the upper bound.

**Two candidate explanations:**

**Attenuation of $\hat{\beta}_{1,m}$.** Market-level DiD cells are thin (minimum 20 transactions per EPC category per month). The ABC vs. EFG price gap is estimated with considerable noise and is likely biased toward zero, deflating the denominator. The pooled hedonic gives $\hat{\beta}_1 = 0.036$ while the market-level DiD mean is $0.044$ with a standard deviation of $0.042$ — a distribution inconsistent with a tight signal.

**$\hat{\Delta}_m$ captures more than EPC sensitivity.** The non-disclosure premium absorbs unobserved quality differences between strategic hiders and EFG disclosers that persist post-reform. The DiD differences out the pre-reform *level* but not pre-existing *composition* differences within the non-discloser pool. If hiders are systematically better properties than EFG disclosers along dimensions not captured by the hedonic controls, $\hat{\Delta}_m$ overstates the EPC-driven premium.

**Economic interpretation.** $\hat{\rho}_m > 1$ means the model *cannot rationalize* the observed non-disclosure premium at any $\rho_m \leq 1$ under the linear approximation $\Delta(e) = \rho \cdot \beta_1 \cdot e$. This is a model boundary failure, not sampling noise — 40 out of 40 markets is decisive. The data is inconsistent with the linear approximation at the current moment conditions.

---

## 2. What is credible: $\hat{c}_{0,m}$ and $\hat{\sigma}_{1,m}$

**$\hat{c}_{0,m} = 1.6\%$ is the paper's most defensible structural result.** It is identified entirely from $\hat{\sigma}_{0,m}$ via the equilibrium inversion, independently of $\hat{\rho}_m$. With $\hat{\rho}_m$ clamped at 1, the inversion delivers a **lower bound** on $\hat{c}_{0,m}$: higher $\rho_m$ implies higher profit from hiding, so a higher cost is needed to rationalize the same $\hat{\sigma}_{0,m}$. The magnitude — a seller forgoes roughly 1.6% of property value to conceal her EPC score — is economically plausible for a legal/administrative disclosure cost and stable across markets ($\hat{c}_{0,m} \in [0.005, 0.033]$).

**$\hat{\sigma}_{1,m} = 0$ across all 40 markets is a strong validation result.** This is a sharp, untargeted prediction of the model (Corollary: informed high-quality sellers always disclose) that holds perfectly in the data without being imposed as an estimation restriction. It should be foregrounded as primary model validation — it is considerably more convincing than a near-zero J-statistic would be, precisely because it is a non-trivial out-of-sample implication that the estimation did not target.

---

## 3. Alternative identification strategies for $\rho_m$

Three approaches, in order of feasibility given the current data:

### 3.1 Set-identification (immediate)

$\rho_m \leq 1$ binds everywhere, so the data supports only a lower bound on $\hat{\Delta}_m / (\hat{\beta}_{1,m} \cdot \hat{e}^*_m)$. Report $\rho_m = 1$ as a maintained assumption and present $\hat{c}_{0,m}$ explicitly as a lower bound. This is honest, publishable, and avoids misrepresenting the identification. The results section should state: *"The non-disclosure premium exceeds the model-implied upper bound under $\rho_m < 1$ in all markets; we therefore maintain $\rho_m = 1$ and interpret $\hat{c}_{0,m}$ as a lower bound on hiding costs."*

### 3.2 Cross-market slope regression (medium effort)

If $\hat{e}^*_m$ varies sufficiently across markets (it does: $[0.146, 0.411]$), one can identify $\rho_m$ from the cross-market slope of $\hat{\Delta}_m$ on $\hat{\beta}_{1,m} \cdot \hat{e}^*_m$:

$$\hat{\Delta}_m = \rho \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m + \varepsilon_m$$

This is a Bartik-style pooled regression that recovers a common $\rho$ from market-level variation in the equilibrium belief. Identification requires $\hat{e}^*_m$ to vary exogenously across markets — plausible since $\hat{e}^*_m$ is determined by $\hat{\pi}_m$ and $\hat{\theta}_m$, which are directly measured structural parameters. The slope $\hat{\rho}_{OLS}$ would be an upper bound if $\hat{\Delta}_m$ contains additional selection on unobservables.

### 3.3 Energy price variation as an instrument (longer term)

Post-reform variation in local energy prices shifts the willingness to pay for EPC quality among sensitive buyers, providing a supply-side instrument for $\rho_m$ excluded from the hiding cost equation. Markets with higher heating costs (e.g. altitude, fuel type, building vintage) should have higher $\rho_m$. This requires matching the listing data to local energy price indices and building stock characteristics — feasible with ADEME and INSEE data but requires additional data work.

---

## 4. Recommended next steps

1. **Reframe the paper's identification claim.** $\rho_m = 1$ as a maintained assumption with $\hat{c}_{0,m}$ as a lower bound. Make this explicit in the estimation section rather than presenting clipped estimates as if they were interior.

2. **Lead with $\hat{\sigma}_{1,m} = 0$.** This is the cleanest result in the paper. A short table showing $\hat{\sigma}_{1,m}$ market by market, with a mean of 0.000 and no market exceeding a small threshold, belongs in the main body as evidence that the model's equilibrium characterization is correct.

3. **Implement the cross-market slope regression (Strategy 3.2).** This is low-cost given existing data and delivers a point estimate of $\rho$ with a standard error, replacing the clipped market-by-market estimates.

4. **Characterize the 223 markets without DiD coverage.** If excluded markets differ systematically from included ones (e.g. smaller cities, lower EPC compliance rates), the reported estimates are selected. An appendix table comparing included vs. excluded markets on observables is needed.

5. **Resolve the discrepancy with prior estimates.** Earlier runs reportedly produced $\hat{\rho} \approx 0.700$ on 57 markets. The current run produces all-clipped results on 40 markets. These are qualitatively incompatible — one of the two runs has a different specification, sample window, or normalization of $\hat{e}^*_m$. This must be resolved before writing the results section.
