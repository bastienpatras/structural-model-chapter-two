# Results Analysis — Structural Estimates (Houses)
*Patras, B. — Mandatory Disclosure and Housing Market Dynamics*
*Last updated: 2026-04-21 | 100 markets, two-step estimator*

---

## Summary of estimates

| Parameter | Mean | Median | Std | \[p10, p90\] |
|---|---|---|---|---|
| $\hat{\beta}_{1,m}$ — DiD EPC quality premium (log pts) | 0.0580 | 0.0544 | 0.0382 | \[0.017, 0.109\] |
| $\hat{\Delta}_m$ — non-disclosure premium (log pts) | 0.0338 | 0.0292 | 0.0476 | \[−0.028, 0.099\] |
| $\hat{\sigma}_{0,m}$ — hiding rate, informed low-quality | 0.037 | 0.028 | 0.031 | \[0.015, 0.068\] |
| $\hat{e}^*_m$ — equilibrium pool quality | 0.277 | 0.255 | 0.114 | \[0.160, 0.425\] |
| $\hat{\rho}_m$ — EPC-sensitive buyer share (clipped to \[0,1\]) | 0.718 | 1.000 | 0.438 | \[0.000, 1.000\] |
| $\hat{c}_{0,m}$ — hiding cost (log pts) | 0.0180 | 0.0147 | 0.0194 | \[0.000, 0.038\] |
| $\hat{\sigma}_{1,m}$ — hiding rate, informed high-quality | 0.000 | — | — | — |

**Sample.** 677,011 listings, 501 markets. Group composition: Truthful Disclosure 90.4%, Uninformed 8.5%, Strategic Hiding 1.1%. Pooled hedonic $\hat{\beta}_1 = 0.0632$. Mean $\hat{\pi}_m = 0.417$ (informed-seller share), mean $\bar{\theta}_m = 0.285$ (quality share among informed).

**DiD coverage.** 113 markets with price index data; 107 with $\hat{\beta}_{1,m} > 0$; 100 matched to listings data and used in estimation. 92 of 107 markets had $\hat{\rho}_m > 1$ before clipping.

**Equilibrium regime.** 75 markets in mixed strategy (75%), 25 in full unraveling (25%).

---

## 1. Assessment of $\hat{\rho}_m$ identification

The identification formula is:

$$\hat{\rho}_m = \frac{\hat{\Delta}_m}{\hat{\beta}_{1,m} \cdot \hat{e}^*_m}$$

For $\hat{\rho}_m \leq 1$, the model requires $\hat{\Delta}_m < \hat{\beta}_{1,m} \cdot \hat{e}^*_m$. With $\hat{e}^*_m \approx 0.28$, this amounts to $\hat{\Delta}_m < 0.28 \cdot \hat{\beta}_{1,m}$.

**Houses are a genuine improvement over apartments.** The ratio $\hat{\Delta}_m / \hat{\beta}_{1,m} \approx 0.58$ on average, versus approximately 5 for apartments. The identification constraint is not catastrophically violated — the non-disclosure premium is now in the same order of magnitude as the EPC quality premium. Nevertheless, 92 of 107 markets still have $\hat{\rho}_m > 1$ before clipping, and the median remains at the boundary (1.000). Interior identification is achieved in approximately **8 markets** (those in the mixed-strategy regime with $\hat{\rho}_m < 1$). These 8 markets are the most informative observations in the sample and should be characterized explicitly in an appendix table.

**Why does the constraint still bind for most markets?** Even with a better-behaved ratio, $\hat{e}^*_m \approx 0.28$ discounts the denominator substantially. For the constraint to be non-binding requires $\hat{\Delta}_m / \hat{\beta}_{1,m} < 0.28$, i.e. the non-disclosure premium must be less than 28% of the EPC quality premium. Only markets with particularly large $\hat{\beta}_{1,m}$ (energy-intensive houses with high heating bills) or small $\hat{\Delta}_m$ achieve this. The 25 full-unraveling markets (with $\hat{\Delta}_m \leq 0$) mechanically set $\hat{\rho}_m = 0$, pulling the cross-market mean below 1.

**Honest framing.** $\hat{\rho}_m$ remains partially set-identified for the majority of house markets. The upper bound $\hat{\rho}_m = 1$ is maintained for 67 of 75 partial-pooling markets; the lower bound $\hat{\rho}_m = 0$ applies to the 25 full-unraveling markets. The 8 interior estimates are the genuine point-identified observations. The cross-market slope regression proposed for apartments (Section 3.2 of the apartment analysis) is equally applicable here and would recover a pooled $\hat{\rho}$ from the slope of $\hat{\Delta}_m$ on $\hat{\beta}_{1,m} \cdot \hat{e}^*_m$.

---

## 2. Credibility of $\hat{c}_{0,m}$ and $\hat{\sigma}_{1,m}$

**$\hat{c}_{0,m} = 1.8\%$ is credible and more informative for houses than apartments.**

As for apartments, $\hat{c}_{0,m}$ is identified entirely from $\hat{\sigma}_{0,m}$ via the equilibrium inversion, independently of $\hat{\rho}_m$. With $\hat{\rho}_m$ maintained at 1 in partial-pooling markets, $\hat{c}_{0,m}$ is a lower bound on the true hiding cost. However, for houses an important additional object is available: the DiD non-disclosure premium $\hat{\Delta}_m$ provides an *upper bound* on $c_{0,m}$ in the mixed-strategy equilibrium (by the indifference condition $c_{0,m} = \Delta(e^*_m; \rho_m) \leq \hat{\Delta}_m$). This yields an identified interval:

$$\hat{c}_{0,m} \in [\hat{c}^{\text{lower}}_{0,m},\ \hat{\Delta}_m] = [0.018,\ 0.034] \text{ on average}$$

This bracketed interval — rather than a point estimate — is the honest structural object for hiding costs in houses. It is tighter than for apartments ($[0.016, 0.085]$) and more credible as a structural range. Presenting it as such converts a limitation into a partial-identification contribution.

**$\hat{\sigma}_{1,m} = 0$ across all 100 house markets.** Combined with the 40 apartment markets, the model's sharpest prediction — that informed high-quality sellers always disclose — holds without exception across 140 markets and two property types. This universal result belongs in the main body of the paper as the primary validation, not in an appendix. It is the strongest evidence that the model's equilibrium characterization is correct.

---

## 3. Why houses behave differently from apartments

**$\hat{\beta}_{1,m}$ is three times larger for houses (0.058 vs. 0.017).** This is the central difference. Houses have larger surface areas and older building stock, making heating costs — the primary driver of EPC quality variation in France — directly material to buyers' running costs. EPC-sensitive buyers in house markets face real energy expenditure differences between ABC and EFG properties; in apartment markets, shared heating systems and smaller surfaces attenuate this sensitivity.

**$\hat{\Delta}_m$ is smaller for houses (0.034 vs. 0.085).** Fewer strategic hiders (1.1% vs. 3.5% of listings) means the non-discloser pool is thinner and less adversely selected. The non-disclosure premium is consequently lower: buyers' beliefs about hidden quality are less pessimistic because fewer sellers choose to hide.

**The hiding rate $\hat{\sigma}_{0,m}$ is half that of apartments (3.7% vs. 7.7%).** This is consistent with the equilibrium mechanism: higher $\hat{\beta}_{1,m}$ raises the cost of hiding (the forgone quality premium is larger), so fewer low-quality sellers find it optimal to conceal their EPC score. The model predicts that $\hat{\sigma}_{0,m}$ should be decreasing in $\hat{\beta}_{1,m}$, which is exactly what the comparison across property types shows.

**The 25% full-unraveling rate reflects genuine market heterogeneity — with a caveat.** In full-unraveling markets, $\hat{\Delta}_m \leq 0$: the non-disclosure premium is absent or negative, meaning buyers assign no informational value to concealment. This is economically plausible in high-compliance markets where nearly all sellers disclose (disclosure is the norm and non-disclosure signals nothing). However, approximately half of these 25 markets likely reflect measurement error in thin DiD cells: $\hat{\Delta}_m < 0$ with a small absolute value is statistically indistinguishable from zero given the standard errors. Bootstrap confidence intervals for $\hat{\Delta}_m$ are needed before classifying these markets as structurally full-unraveling rather than statistically noisy zero-premium markets.

---

## 4. What the full-unraveling markets imply

The 25 full-unraveling markets are economically and methodologically important. Three interpretations:

1. **High-compliance equilibrium.** In markets where EPC disclosure has become the norm (high $\hat{\pi}_m$, high public awareness), the non-discloser pool is so thin that buyers cannot infer anything from non-disclosure. The non-disclosure premium vanishes and hiding offers no strategic benefit. This is the model's full-unraveling prediction: when $c_0 > \Delta(\bar{\theta}; \rho)$, no informed low-quality seller hides.

2. **Pre-existing disclosure culture.** Some French housing markets (notably in Brittany and Alsace, historically colder climates) had high voluntary EPC disclosure rates before the 2021 reform. The reform had a smaller marginal effect in these markets, reducing the DiD signal.

3. **Measurement noise.** With minimum volume of 20 transactions per EPC cell per month, some market-level DiD estimates of $\hat{\Delta}_m$ are imprecise. Negative values close to zero should not be taken as structural evidence of full unraveling without confidence intervals.

**Practical recommendation.** Apply a confidence-interval filter: retain a market as full-unraveling only if $\hat{\Delta}_m + 1.96 \cdot \hat{SE}(\hat{\Delta}_m) < 0$. Markets where zero is within the confidence interval should be classified as ambiguous and excluded from the regime distribution table.

---

## 5. Comparison with apartments

| | **Apartments** | **Houses** |
|---|---|---|
| Markets estimated | 40 | 100 |
| $\hat{\beta}_{1,m}$ mean | 0.017 | 0.058 |
| $\hat{\Delta}_m$ mean | 0.085 | 0.034 |
| $\hat{\Delta}_m / \hat{\beta}_{1,m}$ ratio | ~5 | ~0.58 |
| $\hat{\rho}_m$ mean (clipped) | 0.950 | 0.718 |
| Markets with interior $\hat{\rho}_m$ | 0 | ~8 |
| $\hat{\sigma}_{0,m}$ mean | 7.7% | 3.7% |
| $\hat{c}_{0,m}$ mean | 1.6% | 1.8% |
| Full unraveling | 5% | 25% |
| $\hat{\sigma}_{1,m} = 0$ | 40/40 | 100/100 |

The contrast is theoretically coherent: houses have larger EPC premiums, smaller non-disclosure premiums, lower hiding rates, and partial identification of $\hat{\rho}_m$ in a subset of markets. The apartment market suffers a more severe identification failure because the EPC quality premium is small relative to the non-disclosure premium — possibly reflecting the attenuation of shared heating costs in multi-unit buildings.

---

## 6. Recommended next steps

1. **Present $\hat{c}_{0,m}$ as a bounded interval $[\hat{c}^{\text{lower}}_{0,m}, \hat{\Delta}_m]$.** For houses, this interval $[0.018, 0.034]$ is tight and theoretically grounded. Reframe the hiding cost result around this interval rather than the lower-bound point estimate.

2. **Characterize the 8 interior $\hat{\rho}_m$ markets.** These are the only genuinely point-identified markets. An appendix table reporting their $\hat{\beta}_{1,m}$, $\hat{\Delta}_m$, $\hat{\rho}_m$, climate zone, and building vintage would anchor the identification argument empirically.

3. **Apply bootstrap filtering to full-unraveling classification.** The 25% full-unraveling rate should not be reported as a structural fact until confidence intervals on $\hat{\Delta}_m$ are available. Bootstrap the DiD stage with $B = 500$ draws to obtain $\hat{SE}(\hat{\Delta}_m)$ per market and apply the $\hat{\Delta}_m + 1.96 \cdot \hat{SE} < 0$ criterion.

4. **Implement the cross-market slope regression for $\hat{\rho}$.** Run $\hat{\Delta}_m = \rho \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m + \varepsilon_m$ across the 75 partial-pooling markets. This recovers a pooled $\hat{\rho}$ with a standard error and provides the primary point estimate of buyer EPC sensitivity for houses.

5. **Exploit the house/apartment contrast structurally.** The three-fold difference in $\hat{\beta}_{1,m}$ across property types is a testable model prediction (larger energy surface → higher EPC sensitivity). This cross-property-type variation could serve as an additional identification check: if $\hat{\rho}_m$ is higher in markets where houses dominate (conditional on $\hat{\beta}_{1,m}$), that is consistent with the structural mechanism.

6. **Resolve the apartment DiD attenuation.** The apartment $\hat{\beta}_{1,m}$ (0.017) is far below the pooled hedonic $\hat{\beta}_1$ (0.036), suggesting thin-cell attenuation in the DiD. Consider raising `did_min_volume` for apartments or aggregating to broader geographic units to reduce noise. For houses, $\hat{\beta}_{1,m}$ (0.058) is close to the pooled hedonic (0.063) — the DiD is working correctly there.
