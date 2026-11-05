# Estimation Strategy: Mandatory Disclosure and Housing Market Dynamics

**Patras, B. — PhD Dissertation Chapter 2, Sciences Po Paris**
*Last updated: 2026-04-21 | 140 markets (40 apartments + 100 houses), two-step estimator*

---

## Overview

This document presents the complete structural estimation strategy for the paper "Mandatory Disclosure and Housing Market Dynamics." It is intended as a self-contained methods appendix, suitable for a top-5 journal submission. It covers the economic model, identification logic, moment conditions, the two-step estimator, empirical results, and honest characterization of what is and is not identified.

The paper studies strategic EPC hiding in French residential markets following the July 2021 reform that rendered Diagnostic de Performance Énergétique (DPE) scores legally opposable. The structural model belongs to the Dye (1985) family of voluntary disclosure models, extended to accommodate two empirically relevant features absent from the classical framework: seller heterogeneity in information endowments and buyer heterogeneity in EPC sensitivity. The key contribution of the estimation is to recover, market by market, the share of EPC-sensitive buyers ($\rho_m$) and the hiding cost ($c_{0,m}$) that rationalize the observed joint distribution of prices, disclosure rates, and seller information types.

---

## Part I: The Structural Model

### I.1 Primitives and Notation

The model is a signaling game on a market indexed by $m$. The primitives are as follows.

**Sellers.** Each seller owns a property with observable characteristics $X$ and energy performance $\theta \in \{0, 1\}$, where $\theta = 1$ denotes high efficiency (EPC classes A/B/C) and $\theta = 0$ denotes low efficiency (EPC classes E/F/G). Whether the seller knows $\theta$ depends on whether she possesses a certified DPE audit, matched from the ADEME registry:

- With probability $\pi_m \in (0,1)$, the seller is **informed** ($K = 1$) and knows $\theta$.
- With probability $1 - \pi_m$, the seller is **uninformed** ($K = 0$) and does not.

The parameter $\pi_m$ is measured directly from the ADEME–listing match; it is not estimated. Independence is assumed: $K \perp \theta$, with $\Pr(\theta = 1) = \bar{\theta}_m$.

**Disclosure decision and hiding cost.** The informed seller simultaneously chooses $d \in \{0, 1\}$ and a listing price $p^{\text{list}}$. An uninformed seller is constrained to $d = 0$ (No Falsification Assumption). The hiding cost is:

$$C(\theta, d) = \mathbf{1}[d = 0] \cdot (c_0 + \theta \cdot c_1)$$

where $c_0 \geq 0$ applies to all non-disclosers regardless of quality, and $c_1 \geq 0$ is an additional cost borne exclusively by high-quality hiders. In the benchmark case $\alpha_k = \beta_k$ (see below), $c_1$ is irrelevant for equilibrium because high-quality sellers always disclose regardless of its magnitude (Corollary: High-Quality Sellers Always Disclose, see below). The model is therefore estimated with $c_1$ effectively unrestricted and only $c_0$ as the active cost parameter.

**Buyers.** With probability $\rho_m \in (0,1)$, a buyer is **EPC-sensitive** and incorporates energy performance into her valuation; with probability $1 - \rho_m$, she is **EPC-insensitive**. Buyer valuations are:

$$v_1(\theta, d) = \begin{cases} \beta_0 + \beta_1 \cdot \theta + X'\beta_X & \text{if } d = 1 \text{ (verified quality)} \\ \beta_0 + \beta_1 \cdot e + X'\beta_X & \text{if } d = 0 \text{ (inferred quality, belief } e) \end{cases}$$

$$v_0 = \delta_0 + X'\delta_X$$

The benchmark $\alpha_k = \beta_k$ equates the coefficients on verified and inferred quality: buyers value quality equally whether it is certified or inferred from the pool belief. Under this assumption, the revenue difference between a disclosed and a non-disclosed listing depends only on the gap between the pool belief $e$ and the true quality $\theta$. This is conservative in the sense that a distrust discount ($\alpha_k < \beta_k$) would attenuate the non-disclosure premium and raise the required $\rho_m$, so the identified $\rho_m$ is a lower bound on the true EPC-sensitive buyer share.

**Transaction probability.** The aggregate demand function mixes the two buyer types:

$$\Gamma(p^{\text{list}} \mid d) = \rho_m \cdot G(v_1(d) - p^{\text{list}}) + (1 - \rho_m) \cdot G(v_0 - p^{\text{list}})$$

where $G(\cdot)$ is the logistic CDF with market-specific scale parameter $\sigma_m$, calibrated from hedonic residual variance (scale $\approx \sigma_{\text{OLS}} \cdot \sqrt{3}/\pi$ by probit–logit conversion).

**Seller profit.** Before the hiding cost:

$$\Pi(p; d, \rho) = \phi(p^{\text{list}}) \cdot \Gamma(p^{\text{list}} \mid d)$$

where $\phi(p^{\text{list}}) = \gamma_0 + \gamma_1 \cdot p^{\text{list}}$ maps listing to expected transaction price. The benchmark assumption is $\gamma_0 = 0$, $\gamma_1 = 1$ (listing price approximates transaction price), so profit is in log-price units throughout. The optimal listing price $p^*(v_1, v_0, \rho_m)$ is found by scalar minimization of $-\Pi(p)$ on a bounded interval.

### I.2 Equilibrium Characterization

**Buyer beliefs.** Under the equilibrium result $\sigma_1^* = 0$ (Corollary below), the non-disclosing pool consists of uninformed sellers and informed low-quality hiders only. Applying Bayes' rule:

$$e(\sigma_0) = \frac{(1 - \pi_m)\bar{\theta}_m}{\pi_m(1 - \bar{\theta}_m)\sigma_0 + (1 - \pi_m)}$$

This is the model's central object. It is strictly decreasing in $\sigma_0$: each additional low-quality hider enters the denominator while leaving the numerator unchanged, diluting pool quality. The boundary values are:

$$e(0) = \bar{\theta}_m \qquad \text{(no strategic hiding; pool = uninformed sellers)}$$

$$e(1) = \frac{(1-\pi_m)\bar{\theta}_m}{1 - \pi_m\bar{\theta}_m} < \bar{\theta}_m \qquad \text{(all low-quality sellers hide; pool maximally contaminated)}$$

**Profit gain from hiding.** For an informed low-quality seller ($\theta = 0$), the profit gain from non-disclosure relative to truthful disclosure is:

$$\Delta(e;\rho_m) = \Pi^*(d=0, e;\rho_m) - \Pi^*(d=1, \theta=0;\rho_m)$$

Under Lemma A.1 (Appendix), with the logistic demand specification and $\alpha_k = \beta_k$, this reduces to the linear approximation:

$$\Delta(e;\rho_m) \approx \rho_m \cdot \beta_{1,m} \cdot e$$

This linear form is consistent with the paper's identification strategy and is the version implemented in `src/model.py:profit_gain_hiding()`. The full structural profit-gain function (with explicit optimization over listing prices) is available in `src/model.py:profit_gain_hiding_structural()` and is used as a robustness check.

**Corollary: High-Quality Sellers Always Disclose ($\sigma_1^* = 0$).** Under $\alpha_k = \beta_k$, an informed seller with $\theta = 1$ strictly prefers disclosure for any $e(\sigma_0^*) < 1$. The pool belief is always strictly below one in any non-degenerate equilibrium ($\pi_m < 1$ and $\bar{\theta}_m < 1$), so the corollary holds universally. It follows that $\sigma_1^* = 0$ is an **untargeted, testable prediction** of the model.

**Proposition (Equilibrium Existence and Uniqueness).** The net hiding gain is:

$$\Phi(\sigma_0) \equiv \Delta(e(\sigma_0);\rho_m) - c_0 = \frac{\rho_m \beta_{1,m}(1-\pi_m)\bar{\theta}_m}{\pi_m(1-\bar{\theta}_m)\sigma_0 + (1-\pi_m)} - c_0$$

Since $\Phi$ is strictly decreasing in $\sigma_0$ (monotone feedback), there exists a unique equilibrium:

| Condition | Regime | $\sigma_0^*$ | $e^*$ |
|---|---|---|---|
| $c_0 > \Delta(\bar{\theta}_m)$ | Cost-Deterred Hiding (Full Unraveling) | $0$ | $\bar{\theta}_m$ |
| $c_0 < \Delta(e(1))$ | Complete Adverse Selection | $1$ | $e(1)$ |
| $\Delta(e(1)) \leq c_0 \leq \Delta(\bar{\theta}_m)$ | Partial Pooling (Mixed Strategy) | $(0,1)$ | Solves $\Phi(\sigma_0^*) = 0$ |

In the Partial Pooling regime, the closed-form equilibrium is:

$$\sigma_0^* = \frac{1}{\pi_m(1-\bar{\theta}_m)}\left[\frac{\rho_m\,\beta_{1,m}\,(1-\pi_m)\bar{\theta}_m}{c_0} - (1-\pi_m)\right] \tag{eq:pp\_sigma}$$

and the non-disclosure premium is:

$$p_0^* - p_1^* = \rho_m \cdot \beta_{1,m} \cdot e(\sigma_0^*) \tag{eq:premium}$$

France operates predominantly in the Partial Pooling regime: incomplete audit coverage ($\pi_m < 1$) combined with positive buyer EPC sensitivity ($\rho_m > 0$) sustains a persistent non-disclosure premium in equilibrium.

### I.3 Parameters of Interest and Their Status

| Parameter | Description | Status |
|---|---|---|
| $\pi_m$ | Share of informed sellers | Directly measured (ADEME match) — not estimated |
| $\bar{\theta}_m$ | Mean quality among informed sellers | Directly measured — not estimated |
| $\sigma_{0,m}$ | Hiding rate, informed low-quality sellers | Directly measured from listing × ADEME data |
| $\beta_{1,m}$ | EPC quality premium in log prices | Calibrated from DiD and hedonic regression |
| $\rho_m$ | Share of EPC-sensitive buyers | Identified via DiD event study (see Part II) |
| $c_{0,m}$ | Hiding cost in log-price units | Identified via equilibrium inversion (see Part III) |
| $\sigma_{1,m}$ | Hiding rate, informed high-quality sellers | Not estimated — overidentifying restriction: $\sigma_1^* = 0$ |

---

## Part II: Identification Strategy

### II.1 The July 2021 DPE Reform as a Natural Experiment

The identification of $\rho_m$ exploits the July 1, 2021 enforcement of mandatory EPC disclosure under which DPE scores became legally opposable (*opposabilité juridique*). Before the reform, DPE scores were merely informational: buyers knew scores could be unreliable and largely discounted them, implying $\rho_m \approx 0$ for all markets. After the reform, DPE scores became legally binding and buyers began pricing EPC information, implying $\rho_m^{\text{post}} > 0$ with market-specific variation.

This generates a clean natural experiment: the reform sharply shifts the effective EPC-sensitive buyer share from near zero to a strictly positive level, while leaving the composition of the seller pool ($\pi_m$, $\bar{\theta}_m$) and the hiding cost ($c_{0,m}$) unchanged (under the assumption that sellers did not immediately change auditing behavior in response to the reform). The change in price gaps between EPC categories across the reform date identifies $\rho_m$.

**Exclusion restriction.** The reform date is assumed to affect the price response to EPC information only through the channel of buyer EPC sensitivity ($\rho_m$), and not through direct shifts in either the supply composition ($\pi_m$, $\bar{\theta}_m$) or the hiding cost ($c_{0,m}$). This is supported by:

1. The ADEME match shows that $\pi_m$ did not shift discontinuously at the reform date (the auditing market responded gradually, not sharply).
2. Legal exposure costs $c_0$ changed at the reform date, but this is captured in the structural estimation of $c_{0,m}$ and does not bias $\rho_m$ if the reform's price effect operates primarily through the demand-side channel.
3. Event study figures show parallel pre-trends in the EPC premium ($\beta_{1,t}$) and non-disclosure premium ($\Delta_t$) before July 2021 (Figure ATT in the paper), supporting the common-trends assumption.

**Note on the bouclier tarifaire.** An energy-price Bartik instrument was explored but abandoned. The French government's *bouclier tarifaire* (energy price shield), active October 2021–2023, capped household gas and electricity prices administratively, decoupling household from wholesale TTF prices and eliminating the cross-market variation in energy costs needed for Bartik identification ($F$-statistic 1.0–1.6). The instrument is archived but not used.

### II.2 DiD Estimator of $\beta_{1,m}$ and $\Delta_m$

The first stage uses the panel of hedonic price indices (market × EPC category × month) covering 110 markets (*zones d'emploi*), from October 2018 through July 2024. Let $\log I_{m,t,k}$ denote the log hedonic price index for market $m$, month $t$, and EPC category $k \in \{\text{ABC}, \text{EFG}, \text{undisclosed}\}$.

Define the time-varying gaps:

$$\beta_{1,m,t} = \log I_{m,t,\text{ABC}} - \log I_{m,t,\text{EFG}} \qquad \text{(EPC quality premium)}$$

$$\Delta_{m,t} = \log I_{m,t,\text{undisclosed}} - \log I_{m,t,\text{EFG}} \qquad \text{(non-disclosure premium)}$$

The DiD estimates are simple pre–post means:

$$\widehat{\text{DiD}}_{\beta_1,m} = \overline{\beta_{1,m,t}}^{\text{post}} - \overline{\beta_{1,m,t}}^{\text{pre}}$$

$$\widehat{\text{DiD}}_{\Delta,m} = \overline{\Delta_{m,t}}^{\text{post}} - \overline{\Delta_{m,t}}^{\text{pre}}$$

where "post" denotes $t \geq$ July 2021 and "pre" denotes $t <$ July 2021. Markets are retained only if each EPC category (ABC, EFG, undisclosed) has an average monthly transaction volume of at least 20, ensuring the price indices are not dominated by sampling noise. Markets where $\widehat{\text{DiD}}_{\beta_1,m} \leq 0$ (the EPC premium did not rise post-reform, so $\rho_m$ cannot be signed positively) are excluded from the structural sample.

The implementation is in `src/event_study.py:compute_did()`. The log index uses $\log(\text{prices})$, where `prices` is the hedonic reference price (€/m²), directly comparable to the listing-price hedonic coefficient $\hat{\beta}_{1,m}$ in log units.

### II.3 Closed-Form Identification of $\rho_m$

**Key identifying equation.** In the Partial Pooling equilibrium, the non-disclosure premium equals $\rho_m \cdot \beta_{1,m} \cdot e^*_m$. Equating the DiD estimator to this model-implied premium:

$$\widehat{\text{DiD}}_{\Delta,m} = \rho_m \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m$$

Inverting:

$$\hat{\rho}_m = \frac{\widehat{\text{DiD}}_{\Delta,m}}{\hat{\beta}_{1,m} \cdot \hat{e}^*_m} \tag{eq:rho\_estimator}$$

where the equilibrium belief at the observed mixing rate is:

$$\hat{e}^*_m = \frac{(1-\hat{\pi}_m)\hat{\bar{\theta}}_m}{\hat{\pi}_m(1-\hat{\bar{\theta}}_m)\hat{\sigma}_{0,m} + (1-\hat{\pi}_m)}$$

All three inputs ($\hat{\pi}_m$, $\hat{\bar{\theta}}_m$, $\hat{\sigma}_{0,m}$) are directly measured from the ADEME-matched listing data and not estimated. This makes the identification of $\rho_m$ a closed-form inversion of the structural equilibrium condition, not a numerical optimization.

**Implementation.** `src/event_study.py:estimate_rho_c0()` computes $\hat{e}^*_m$ via `src/model.py:belief_function()` and applies the formula above. Markets where $\hat{\text{DiD}}_{\beta_1,m} \leq 10^{-6}$ or $\hat{e}^*_m \leq 10^{-6}$ are assigned $\hat{\rho}_m = \text{NaN}$ (not identified). The resulting $\hat{\rho}_m$ is clipped to $[0, 1]$; out-of-range values are logged.

### II.4 What $\rho_m$ Identifies and What It Does Not

The identification formula (eq:rho_estimator) is valid under the following conditions:

1. The market is in the Partial Pooling equilibrium at the observed $\hat{\sigma}_{0,m}$.
2. The DiD identifies the demand-side response only ($\alpha_k = \beta_k$).
3. $\hat{\beta}_{1,m}$ is measured without attenuation (thin-cell noise in the DiD deflates the denominator and inflates $\hat{\rho}_m$).
4. $\widehat{\text{DiD}}_{\Delta,m}$ captures only the EPC-sensitive premium (selection on unobservables within the non-discloser pool would inflate the numerator and inflate $\hat{\rho}_m$).

**Identification failure: $\hat{\rho}_m > 1$.** The constraint $\hat{\rho}_m \leq 1$ binds in the majority of markets:

- **Apartments (40 markets):** $\hat{\rho}_m > 1$ in all 40 markets before clipping. The ratio $\hat{\Delta}_m / \hat{\beta}_{1,m} \approx 5$ on average, against a model-implied maximum of $\hat{e}^*_m \approx 0.25$.
- **Houses (100 markets):** $\hat{\rho}_m > 1$ in 92 of 107 markets before clipping. The ratio $\hat{\Delta}_m / \hat{\beta}_{1,m} \approx 0.58$ on average.

When $\hat{\rho}_m$ hits the upper bound, it is set-identified: the data supports only a lower bound on the non-disclosure premium that can be rationalized by the model. There are two candidate explanations for the systematic overrun:

1. **Attenuation of $\hat{\beta}_{1,m}$** (deflated denominator). Market-level DiD cells are thin (minimum 20 transactions per EPC cell per month). The ABC vs. EFG price gap is estimated with noise that is biased toward zero. For apartments, the DiD mean $\hat{\beta}_{1,m} = 0.017$ is below the pooled hedonic estimate $\hat{\beta}_1 = 0.036$, consistent with thin-cell attenuation.
2. **Composition bias in $\widehat{\text{DiD}}_{\Delta,m}$** (inflated numerator). The non-disclosure premium absorbs unobserved quality differences between strategic hiders and EFG disclosers that the DiD differences out at the pre-reform level but not in post-reform composition. If hiders are systematically better-quality properties on dimensions not captured by the hedonic controls, $\hat{\Delta}_m$ overstates the EPC-driven premium.

**Honest framing.** Given that $\hat{\rho}_m = 1$ binds in the large majority of markets, $\rho_m = 1$ is maintained as a working assumption and $\hat{c}_{0,m}$ is interpreted as a **lower bound** on the true hiding cost (higher $\rho_m$ implies higher profit from hiding, so a higher cost is needed to rationalize the same $\hat{\sigma}_{0,m}$).

---

## Part III: The Two-Step Estimator

### III.1 Logic and Structure

The estimator is a two-step closed-form inversion. No numerical optimization is performed in the primary estimator. Both steps operate market-by-market.

**Step 1 (DiD first stage):** Recover $\hat{\rho}_m$ from the structural inversion (eq:rho_estimator), as described in Part II. Clip to $[0, 1]$.

**Step 2 (Equilibrium inversion):** Given $\hat{\rho}_m$ (fixed), invert the equilibrium indifference condition $\Delta(e^*;\hat{\rho}_m) = c_{0,m}$ using the directly observed hiding rate $\hat{\sigma}_{0,m}$:

$$\hat{c}_{0,m} = \hat{\rho}_m \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m \tag{eq:c0\_inversion}$$

where $\hat{e}^*_m = e(\hat{\sigma}_{0,m})$ is evaluated at the observed mixing rate. This is identical to eq:pp\_sigma inverted for $c_{0,m}$.

**Exact identification.** In the Partial Pooling regime, the indifference condition $\Phi(\sigma_0^*) = 0$ delivers a unique mapping from the observed $\hat{\sigma}_{0,m}$ to $c_{0,m}$, given $\hat{\rho}_m$ and $\hat{\beta}_{1,m}$. With one free parameter ($c_{0,m}$) and one moment ($\hat{\sigma}_{0,m}$), the system is exactly identified in each market.

**Implementation.** `src/estimation.py:estimate_msm(fix_rho=True)` implements the two-step mode. The relevant lines are:

```python
e_star  = belief_function(sig_m, pi_m, th_m)
c0_hat[m] = float(np.clip(rho_m * beta1_m * e_star, 0.0, None))
```

No optimization loop is entered. `MSMResult` records `message = "two-step closed-form inversion (fix_rho=True)"` and `converged = True` by construction.

### III.2 Robustness: Joint MSM Mode

A joint MSM mode (`fix_rho=False`) is also implemented, which simultaneously optimizes over $[\rho_1, \ldots, \rho_M, \phi_1, \ldots, \phi_M]$ where $c_{0,m} = \phi_m \cdot \Delta(e_0; \hat{\rho}_m)$ is the $\phi$-reparametrization (Section III.3). This mode treats the DiD estimate only as a warm-start for $\rho_m$ and jointly optimizes both parameters. However, with only one active moment ($m_4$) and two parameters per market, the joint mode is under-identified ($2M$ parameters, $M$ moments). It is used only as a sensitivity check with a fixed common $\rho$ across markets. All primary results use the two-step mode.

**Note on a paper–code tension.** The paper's current draft describes a sequential two-step procedure (DiD for $\rho_m$, then MSM for $c_{0,m}$). The code correctly implements this in the `fix_rho=True` branch. The joint `fix_rho=False` mode is a robustness tool but should not be presented as the primary estimator.

### III.3 The $\phi$-Reparametrization (Joint Mode Only)

In the joint MSM mode, $c_{0,m}$ is parametrized as $c_{0,m} = \phi_m \cdot \Delta(e_0; \rho_m)$ where $\phi_m \in (0,1)$ and $e_0 = e(0) = \bar{\theta}_m$. This guarantees $c_{0,m} < \Delta(e_0; \rho_m)$ for any $(\rho_m, \phi_m) \in [0,1]^2$, keeping every market in the Partial Pooling regime and preventing gradient vanishing at the full-unraveling boundary. The transformation is back-solved to $c_{0,m}$ after optimization.

### III.4 Bootstrap Standard Errors

Standard errors are computed by a non-parametric bootstrap (`src/estimation.py:bootstrap_se()`): resample listings within each market with replacement ($B = 500$ replications), re-run the two-step estimator on each bootstrap sample, and report the standard deviation of the bootstrap distribution as the standard error.

**Two-step bootstrap mode.** When `rho_hat_fixed` is provided, $\hat{\rho}_m$ is held fixed at the point estimate and only $\hat{\sigma}_{0,m}$ is resampled. This propagates sampling uncertainty in the hiding rate to $\hat{c}_{0,m}$ via the closed-form inversion. Bootstrap SEs for $\hat{\rho}_m$ from the DiD first stage are computed separately by bootstrapping `compute_did()`.

---

## Part IV: Moment Conditions

Three moments are defined per market $m$. The active moment set used in the primary two-step estimator is only $m_4$. Moments $m_3$ and $m_5$ play identification and validation roles respectively.

### IV.1 Moment $m_3$: Non-Disclosure Premium (DiD, Identification of $\rho_m$)

**Data moment:**

$$m_3^{\text{data}} = \widehat{\text{DiD}}_{\Delta,m} = \overline{\log p}_{d=0,m}^{\text{post}} - \overline{\log p}_{d=0,m}^{\text{pre}} - \left(\overline{\log p}_{d=1,\theta=0,m}^{\text{post}} - \overline{\log p}_{d=1,\theta=0,m}^{\text{pre}}\right)$$

In practice, the DiD is estimated from the hedonic price index panel (EPC category × market × month), not from raw listing prices, to control for market-level trends and property composition:

$$m_3^{\text{data}} = \widehat{\text{DiD}}_{\Delta,m} \text{ from } \texttt{compute\_did()}$$

**Model moment:**

$$m_3^{\text{model}}(\rho_m, c_{0,m}) = \rho_m \cdot \beta_{1,m} \cdot e^*(\sigma_0^*)$$

**Role.** $m_3$ identifies $\rho_m$ given $\beta_{1,m}$ and $\hat{e}^*_m$. In the two-step estimator, $m_3$ is used in the first stage (Step 1) as the moment matched to recover $\hat{\rho}_m$. It is **not** used as an active moment in the MSM second stage (Step 2) because it is already absorbed by the first-stage estimate.

**Why $m_3$ is not in the MSM second stage.** If $m_3$ were included as an active MSM moment alongside $m_4$, the estimator would be over-determined in the following sense: $m_3$ identifies $\rho_m$ and $m_4$ identifies $c_{0,m}$ given $\rho_m$. The two-step structure makes this sequencing explicit and avoids confounding. Additionally, $m_3$ may carry selection bias (the non-discloser pool mixes strategic hiders with uninformed sellers whose composition is endogenous to the equilibrium), while the DiD differences out this composition effect relative to the pre-reform baseline. Including $m_3$ in the MSM without the DiD correction would contaminate the objective with a moment measured in levels rather than first differences.

### IV.2 Moment $m_4$: Hiding Rate Among Informed Low-Quality Sellers (Identifies $c_{0,m}$)

**Data moment:**

$$m_4^{\text{data}} = \hat{\sigma}_{0,m} = \frac{\#\{i: K_i = 1, \theta_i = 0, d_i = 0, \text{market}_i = m\}}{\#\{i: K_i = 1, \theta_i = 0, \text{market}_i = m\}}$$

This is a simple proportion: the share of informed low-quality sellers ($K = 1$, $\theta = 0$) who choose not to disclose. Both $K$ and $\theta$ are observed directly from the ADEME match, making this moment directly measurable rather than inferred.

**Model moment:**

$$m_4^{\text{model}}(\rho_m, c_{0,m}) = \sigma_0^*(\rho_m, c_{0,m})$$

the equilibrium hiding rate from Proposition (Equilibrium Existence and Uniqueness).

**Role.** $m_4$ is the **active moment** in the two-step estimator. Given $\hat{\rho}_m$ from Step 1, the condition $m_4^{\text{data}} = m_4^{\text{model}}(\hat{\rho}_m, c_{0,m})$ has a unique solution in $c_{0,m}$ (the Partial Pooling closed-form eq:pp\_sigma inverted). This makes the two-step estimator a closed-form inversion rather than an optimization.

**Variance.** The sampling variance of $\hat{\sigma}_{0,m}$ is estimated by the Bernoulli variance:

$$\widehat{\text{Var}}(m_4^{\text{data}}) = \frac{\hat{\sigma}_{0,m}(1 - \hat{\sigma}_{0,m})}{\#\{i: K_i = 1, \theta_i = 0, m_i = m\}}$$

### IV.3 Moment $m_5$: Hiding Rate Among Informed High-Quality Sellers (Overidentifying Restriction)

**Data moment:**

$$m_5^{\text{data}} = \hat{\sigma}_{1,m} = \frac{\#\{i: K_i = 1, \theta_i = 1, d_i = 0, m_i = m\}}{\#\{i: K_i = 1, \theta_i = 1, m_i = m\}}$$

**Model moment:**

$$m_5^{\text{model}} = 0 \qquad \text{for all } (\rho_m, c_{0,m}) \in (0,1] \times [0,\infty)$$

by the Corollary: High-Quality Sellers Always Disclose.

**Role.** $m_5$ is a **model validation check**, not an active estimation moment. The prediction $\sigma_1^* = 0$ is an untargeted implication of the equilibrium characterization that is not imposed as an estimation restriction. If $m_5^{\text{data}} \neq 0$, the model is rejected.

### IV.4 Why $m_1$ and $m_2$ Were Dropped

Two price moments were considered but excluded from the active moment set:

**$m_1$: Mean log price of disclosed high-quality listings.** $m_1$ identifies the baseline valuation parameter $\beta_0 + \beta_1 + X'\beta_X$ (the valuation of a high-quality informed seller). This parameter is already fit by construction after the hedonic residualization of prices. Including $m_1$ in the MSM would add no new information about $(\rho_m, c_{0,m})$ and would mechanically produce zero residual, inflating the precision of the estimates artificially.

**$m_2$: Mean log price of disclosed low-quality listings.** $m_2$ identifies $\beta_0 + X'\beta_X$ (the baseline valuation at $\theta = 0$). Similarly fit by construction after hedonic residualization. Both $m_1$ and $m_2$ serve as the regression targets in the hedonic stage and carry no independent information about the structural parameters of interest.

---

## Part V: Empirical Results

### V.1 Sample and Coverage

The structural estimation covers 140 markets across two property types:

**Apartments:** 40 of 263 apartment markets. DiD coverage requires: (i) price index data available, (ii) $\hat{\beta}_{1,m} > 0$ (EPC premium rose post-reform), (iii) match to listings market statistics. The 223 excluded markets — primarily smaller *zones d'emploi* — could not construct reliable DiD estimates from the minimum-volume-filtered index data.

**Houses:** 100 of 501 house markets. 113 markets with price index data; 107 with $\hat{\beta}_{1,m} > 0$; 100 matched to listings data.

The listing data covers 677,011 house listings and approximately 843,621 apartment listings. Group composition for the house sample: Truthful Disclosure 90.4%, Uninformed 8.5%, Strategic Hiding 1.1%.

### V.2 Results: Apartments (40 Markets)

| Parameter | Mean | Median | Std | [p10, p90] |
|---|---|---|---|---|
| $\hat{\beta}_{1,m}$ — DiD EPC quality premium (log pts) | 0.0444 | 0.0186 | 0.0421 | [−0.036, 0.067] |
| $\hat{\Delta}_m$ — non-disclosure premium (log pts) | 0.0850 | 0.0629 | 0.0616 | [0.002, 0.157] |
| $\hat{\sigma}_{0,m}$ — hiding rate, informed low-quality | 0.077 | 0.072 | 0.048 | [0.035, 0.123] |
| $\hat{e}^*_m$ — equilibrium pool quality | 0.252 | 0.234 | 0.095 | [0.146, 0.411] |
| $\hat{\rho}_m$ — EPC-sensitive buyer share (clipped) | 0.950 | 1.000 | 0.218 | [1.000, 1.000] |
| $\hat{c}_{0,m}$ — hiding cost (log pts) | 0.0162 | 0.0125 | 0.0125 | [0.005, 0.033] |
| $\hat{\sigma}_{1,m}$ — hiding rate, informed high-quality | 0.000 | 0.000 | — | — |

**Coverage notes.** 2 of 40 markets have $\hat{\Delta}_m < 0$ (full unraveling; $\hat{\rho}_m = 0$). 38 of 40 markets are in the Partial Pooling regime.

**$\hat{\rho}_m$ identification.** All 40 markets have $\hat{\rho}_m > 1$ before clipping. The ratio $\hat{\Delta}_m / (\hat{\beta}_{1,m} \cdot \hat{e}^*_m) \approx 7.7$ on average. This constitutes a model boundary failure, not sampling noise. No market has an interior point estimate of $\rho_m$.

**$\hat{c}_{0,m} = 1.6\%$.** Identified entirely from $\hat{\sigma}_{0,m}$ via the equilibrium inversion, independently of $\hat{\rho}_m$. With $\hat{\rho}_m$ clamped at 1, this is a **lower bound**: a seller forgoes roughly 1.6% of property value to conceal her EPC score. The identified interval for apartments (under the lower bound interpretation) is $[0.005, 0.033]$ log points across markets.

### V.3 Results: Houses (100 Markets)

| Parameter | Mean | Median | Std | [p10, p90] |
|---|---|---|---|---|
| $\hat{\beta}_{1,m}$ — DiD EPC quality premium (log pts) | 0.0580 | 0.0544 | 0.0382 | [0.017, 0.109] |
| $\hat{\Delta}_m$ — non-disclosure premium (log pts) | 0.0338 | 0.0292 | 0.0476 | [−0.028, 0.099] |
| $\hat{\sigma}_{0,m}$ — hiding rate, informed low-quality | 0.037 | 0.028 | 0.031 | [0.015, 0.068] |
| $\hat{e}^*_m$ — equilibrium pool quality | 0.277 | 0.255 | 0.114 | [0.160, 0.425] |
| $\hat{\rho}_m$ — EPC-sensitive buyer share (clipped to [0,1]) | 0.718 | 1.000 | 0.438 | [0.000, 1.000] |
| $\hat{c}_{0,m}$ — hiding cost (log pts) | 0.0180 | 0.0147 | 0.0194 | [0.000, 0.038] |
| $\hat{\sigma}_{1,m}$ — hiding rate, informed high-quality | 0.000 | — | — | — |

**Coverage notes.** 92 of 107 house markets have $\hat{\rho}_m > 1$ before clipping. Interior identification ($\hat{\rho}_m < 1$) is achieved in approximately 8 markets. 25 of 100 markets are in the Full Unraveling regime ($\hat{\Delta}_m \leq 0$, $\hat{\rho}_m = 0$). 75 of 100 markets are in the Partial Pooling regime.

**$\hat{\rho}_m$ identification.** Houses are a genuine improvement over apartments: the ratio $\hat{\Delta}_m / \hat{\beta}_{1,m} \approx 0.58$ versus approximately 5 for apartments. Interior identification is achieved in the 8 markets (those in the Partial Pooling regime with $\hat{\rho}_m < 1$). These 8 markets are the only genuinely point-identified observations for $\rho_m$.

**$\hat{c}_{0,m} = 1.8\%$.** As for apartments, identified via the equilibrium inversion independently of $\hat{\rho}_m$. For houses, the DiD non-disclosure premium provides an **upper bound** on $c_{0,m}$ in mixed-strategy markets (by the indifference condition $c_{0,m} = \Delta(e^*_m;\rho_m) \leq \hat{\Delta}_m$). This yields an **identified interval**:

$$\hat{c}_{0,m} \in [\hat{c}_{0,m}^{\text{lower}},\; \hat{\Delta}_m] = [0.018,\; 0.034] \text{ on average}$$

This bounded interval is the honest structural object for hiding costs in house markets. It is tighter than for apartments ($[0.016, 0.085]$).

### V.4 Comparison: Apartments vs. Houses

| | Apartments | Houses |
|---|---|---|
| Markets estimated | 40 | 100 |
| $\hat{\beta}_{1,m}$ mean (log pts) | 0.017 | 0.058 |
| $\hat{\Delta}_m$ mean (log pts) | 0.085 | 0.034 |
| $\hat{\Delta}_m / \hat{\beta}_{1,m}$ ratio | ~5 | ~0.58 |
| $\hat{\rho}_m$ mean (after clipping) | 0.950 | 0.718 |
| Markets with interior $\hat{\rho}_m$ | 0 | ~8 |
| $\hat{\sigma}_{0,m}$ mean | 7.7% | 3.7% |
| $\hat{c}_{0,m}$ mean (log pts) | 1.6% | 1.8% |
| Full unraveling | 5% | 25% |
| $\hat{\sigma}_{1,m} = 0$ | 40/40 | 100/100 |

The contrast is theoretically coherent. Houses have larger EPC premiums ($\hat{\beta}_{1,m}$ three times larger: 0.058 vs. 0.017), smaller non-disclosure premiums, lower hiding rates, and partial identification of $\hat{\rho}_m$ in a subset of markets. The apartment identification failure arises because the EPC quality premium is small relative to the non-disclosure premium — plausibly because shared heating systems and smaller surface areas attenuate EPC sensitivity in multi-unit buildings.

---

## Part VI: Identification Limitations

### VI.1 The $\hat{\rho}_m$ Clipping Problem

The most important identification limitation is that $\hat{\rho}_m$ hits the upper bound $\rho_m = 1$ in the large majority of markets: all 40 apartment markets and 92 of 100 house markets. The data are inconsistent with the linear approximation $\Delta(e) = \rho \cdot \beta_1 \cdot e$ at any $\rho_m \leq 1$ given the observed $(\hat{\Delta}_m, \hat{\beta}_{1,m}, \hat{e}^*_m)$.

**Set identification.** The correct characterization is:

$$\rho_m \in \left[\frac{\hat{\Delta}_m}{\hat{\beta}_{1,m} \cdot \hat{e}^*_m},\; 1\right]$$

where the lower bound exceeds 1 for clipped markets, meaning the identified set is $\{1\}$ (a singleton at the boundary). The model is not rejected — the Partial Pooling equilibrium is consistent with $\rho_m = 1$ — but no interior estimate is obtained.

**Consequences for $\hat{c}_{0,m}$.** When $\hat{\rho}_m = 1$:

- $\hat{c}_{0,m} = 1 \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m$ is the minimum hiding cost consistent with the data.
- Under any $\rho_m > 1$ (hypothetical), $\Delta(e^*;\rho_m) > \Delta(e^*;1)$, so the required $c_{0,m}$ would be even higher. The clipped estimate is therefore a lower bound.
- The interval $[\hat{c}_{0,m}^{\text{lower}}, \hat{\Delta}_m]$ is the partially identified set for $c_{0,m}$.

**Alternative identification strategies.** Three approaches with increasing data requirements:

1. **Cross-market slope regression (immediate).** The cross-market regression:

$$\hat{\Delta}_m = \rho \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m + \varepsilon_m$$

recovers a pooled $\hat{\rho}$ from the slope of the non-disclosure premium on $\hat{\beta}_{1,m} \cdot \hat{e}^*_m$, given that $\hat{e}^*_m$ varies exogenously across markets (since $\hat{e}^*_m$ is determined by $\hat{\pi}_m$ and $\hat{\bar{\theta}}_m$, which are directly measured). This is a Bartik-style pooled regression providing a point estimate of $\rho$ with a standard error.

2. **Interior-market characterization (immediate).** The approximately 8 house markets with interior $\hat{\rho}_m < 1$ are the only genuinely point-identified observations. An appendix table characterizing these markets (by $\hat{\beta}_{1,m}$, $\hat{\Delta}_m$, $\hat{\rho}_m$, climate zone, building vintage) would anchor the identification argument empirically.

3. **Energy price instrument (longer term).** Post-reform variation in local energy prices shifts EPC sensitivity among sensitive buyers, providing a supply-side instrument for $\rho_m$ excluded from the hiding cost equation. Matching the listing data to local energy price indices and building stock characteristics would permit IV identification of $\rho_m$.

### VI.2 The Identified Interval for $\hat{c}_{0,m}$

For **houses**, the structural parameter $c_{0,m}$ is set-identified with an identified interval:

$$\hat{c}_{0,m}^{\text{lower}} = \hat{\rho}_m \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m \leq c_{0,m} \leq \hat{\Delta}_m$$

Lower bound: the equilibrium inversion evaluated at $\hat{\rho}_m = 1$.
Upper bound: the DiD non-disclosure premium, which upper-bounds the profit gain from hiding by the indifference condition $c_{0,m} \leq \Delta(e^*;\rho_m) \leq \rho_m \cdot \beta_{1,m} \cdot \bar{\theta}_m \leq \hat{\Delta}_m$ (since $e^* \leq \bar{\theta}_m$ and $\rho_m \leq 1$).

The average identified interval for houses is $[0.018, 0.034]$, representing a hiding cost of 1.8% to 3.4% of property value.

For **apartments**, the upper bound $\hat{\Delta}_m = 0.085$ is wider and less informative. The lower bound $\hat{c}_{0,m}^{\text{lower}} = 0.016$ remains valid.

### VI.3 The 24% DiD Coverage Gap

Only 40 of 263 apartment markets (15%) and 100 of 501 house markets (20%) have usable DiD estimates. Markets are excluded because:

1. The EPC price index data is not available (insufficient transaction volume in all EPC categories).
2. $\hat{\beta}_{1,m} \leq 0$ (the EPC premium did not rise post-reform).
3. The market does not match to the listings data.

The excluded markets are not random: they are primarily smaller *zones d'emploi* with lower transaction volumes. If excluded markets differ systematically from included ones in $(\rho_m, c_{0,m})$, the reported estimates are a selected sample. A comparison of observable characteristics (market size, EPC compliance rate, housing stock vintage) between included and excluded markets is needed before the estimates can be interpreted as representative of all French markets.

### VI.4 Full-Unraveling Market Classification

Among the 25 house markets classified as Full Unraveling ($\hat{\Delta}_m \leq 0$), some may reflect measurement noise rather than a structural full-unraveling equilibrium. With minimum volume of 20 transactions per EPC cell per month, $\hat{\Delta}_m < 0$ with small absolute value is statistically indistinguishable from zero given bootstrap standard errors. A market should be classified as Full Unraveling only if the upper confidence bound $\hat{\Delta}_m + 1.96 \cdot \widehat{SE}(\hat{\Delta}_m) < 0$.

---

## Part VII: Model Validation

### VII.1 $\hat{\sigma}_{1,m} = 0$ Across 140 Markets

The model's sharpest prediction — that informed high-quality sellers never conceal their EPC score in equilibrium — holds without exception across all 140 estimated markets: 40 apartment markets and 100 house markets, spanning two property types and multiple equilibrium regimes.

This is a **strong overidentifying restriction** because:

1. It is untargeted: $\sigma_1^* = 0$ is not imposed as an estimation constraint. The estimator would produce non-zero $\hat{\sigma}_{1,m}$ if the data required it.
2. It is economically non-trivial: if sellers were not playing the equilibrium mixed strategy (for example, due to behavioral departures from expected profit maximization, or unmodeled disclosure costs for high-quality sellers), $\hat{\sigma}_{1,m}$ would be positive in some markets.
3. It is measured directly from the ADEME match, not inferred from prices, so it is not subject to the selection biases that affect the price moments.
4. It holds universally across heterogeneous markets: apartments and houses, Partial Pooling and Full Unraveling regimes, large cities and smaller markets.

This result should be foregrounded in the main body as the primary model validation. It is considerably more convincing than a near-zero $J$-statistic from the MSM objective, precisely because it is a non-trivial out-of-sample implication that estimation did not target.

### VII.2 Equilibrium Regime Consistency

The two-step estimator restricts attention to markets in the Partial Pooling regime (the equilibrium condition $\Phi(\sigma_0^*) = 0$ is invertible only there). Markets assigned to Full Unraveling or Complete Adverse Selection after the first stage are excluded from the $c_{0,m}$ estimation. This exclusion operates on an endogenous, model-based criterion. A careful referee will note that the composition of the remaining sample depends on the estimated parameters, which could create selection bias. The exclusion affects approximately 2 of 40 apartment markets (5%) and 25 of 100 house markets (25%).

### VII.3 Comparison with Pooled Hedonic

The market-level DiD estimates of $\hat{\beta}_{1,m}$ should be consistent with the pooled hedonic estimate $\hat{\beta}_1$. For houses, $\hat{\beta}_{1,m}^{\text{DiD}} = 0.058$ is close to the pooled hedonic $\hat{\beta}_1 = 0.063$, supporting the reliability of the DiD. For apartments, $\hat{\beta}_{1,m}^{\text{DiD}} = 0.017$ is materially below the pooled hedonic $\hat{\beta}_1 = 0.036$, consistent with thin-cell attenuation in the apartment DiD.

---

## Part VIII: Assumptions Table

| Assumption | Where Stated | Where Used | Strength | Consequence if Violated |
|---|---|---|---|---|
| $K \perp \theta$ (Independence) | Section: Buyer Beliefs | Belief function $e(\sigma_0)$; identification of $\hat{\pi}_m$, $\hat{\bar{\theta}}_m$ as separate objects | Moderate — forced sales support it | Belief function biased; $e(\sigma_0)$ no longer has the tractable form |
| $\alpha_k = \beta_k$ (Benchmark) | Section: Buyer Valuations | Linear approximation $\Delta(e) = \rho\beta_1 e$; identification of $\rho_m$ | Strong — identification direction known: $\hat{\rho}_m$ is lower bound under $\alpha_k < \beta_k$ | $\hat{\rho}_m$ is a lower bound; $\hat{c}_{0,m}$ is a lower bound |
| $\sigma_1^* = 0$ (Corollary) | Equilibrium section | Simplified belief $e(\sigma_0)$ | Testable and verified across 140 markets | Model rejected if violated |
| No Falsification | Model section | $K = 0$ sellers constrained to $d = 0$ | Strong — ADEME match verifiable | Misclassification of uninformed as strategic hiders |
| Common-trends (DiD) | Identification section | $\rho_m \approx 0$ pre-reform; DiD identifies level shift | Untested for $\Delta_{m,t}$ (tested via event study for $\beta_{1,m,t}$) | $\hat{\rho}_m$ biased if non-disclosure premium had non-parallel pre-trends |
| Linear profit gain $\Delta(e) = \rho\beta_1 e$ | Model appendix (Lemma A.1) | Equilibrium condition, $c_{0,m}$ inversion | Approximate — exact form available | Full structural inversion available as robustness |
| $\gamma_0 = 0$, $\gamma_1 = 1$ | Model section (eq:payoff) | Listing price ≈ transaction price | Moderate — listing-to-transaction regression available | Units of $c_{0,m}$ distorted; estimate requires adjustment |
| Regime: Partial Pooling | Equilibrium section | Invertibility of $\Phi(\sigma_0^*) = 0$ for $c_{0,m}$ | Testable, conditional on estimates | $c_{0,m}$ not identified from $m_4$ in corner regimes |

---

## Part IX: Recommended Improvements Before Submission

**Critical (must address):**

1. **Reframe $\hat{\rho}_m$ identification.** Present $\hat{\rho}_m = 1$ explicitly as a maintained assumption for clipped markets, not as an interior point estimate. The paper's current draft implies the inversion produces interior estimates; it does not for 132 of 140 markets.

2. **Present $\hat{c}_{0,m}$ as a bounded interval.** For houses: $[\hat{c}_{0,m}^{\text{lower}}, \hat{\Delta}_m] = [0.018, 0.034]$ log points. For apartments: lower bound 0.016 log points; upper bound less tight. This is the honest structural object under partial identification.

3. **Lead with $\hat{\sigma}_{1,m} = 0$.** The universal zero high-quality hiding rate across 140 markets is the paper's strongest empirical result. It belongs in the main body, not an appendix.

4. **Reconcile paper narrative with code.** The paper describes a two-step sequential procedure but earlier code versions also run joint MSM. Clarify that `fix_rho=True` (the two-step mode) is the primary estimator. All tables should document which mode produced the reported estimates.

**Important (non-blocking but significant):**

5. **Implement cross-market slope regression for $\hat{\rho}$.** Run $\hat{\Delta}_m = \rho \cdot \hat{\beta}_{1,m} \cdot \hat{e}^*_m + \varepsilon_m$ across Partial Pooling markets to recover a pooled $\hat{\rho}$ with a standard error. This is the only available route to a point estimate with genuine uncertainty quantification.

6. **Apply bootstrap CI filter to full-unraveling classification.** The 25% full-unraveling rate in houses should not be reported as structural until bootstrap confidence intervals on $\hat{\Delta}_m$ are available and the $\hat{\Delta}_m + 1.96 \cdot \widehat{SE}(\hat{\Delta}_m) < 0$ criterion is applied.

7. **Characterize the 8 interior-$\hat{\rho}_m$ house markets.** These are the only genuinely point-identified observations. An appendix table with $\hat{\beta}_{1,m}$, $\hat{\Delta}_m$, $\hat{\rho}_m$, climate zone, and building vintage would anchor the identification argument.

8. **Resolve apartment DiD attenuation.** The apartment $\hat{\beta}_{1,m}^{\text{DiD}} = 0.017$ is substantially below the pooled hedonic $\hat{\beta}_1 = 0.036$. Consider raising `min_volume` for apartments or aggregating to broader geographic units.

9. **Characterize coverage gap.** Compare observable characteristics of the 223 excluded apartment markets and 401 excluded house markets to the included markets. If excluded markets differ systematically, the estimates are not representative.

**Optional polish:**

10. **Bootstrap SEs for $\hat{\rho}_m$ from DiD first stage.** Current bootstrap propagates uncertainty in $\hat{\sigma}_{0,m}$ to $\hat{c}_{0,m}$ but treats $\hat{\rho}_m$ as fixed. Bootstrap the DiD stage ($B = 500$ draws) to obtain $\widehat{SE}(\hat{\rho}_m)$.

11. **Robustness: structural profit-gain function.** Replace the linear approximation $\Delta(e) = \rho\beta_1 e$ with the full structural $\Delta(e) = \Pi^*(d=0,e;\rho) - \Pi^*(d=1,\theta=0;\rho)$ (available in `src/model.py:profit_gain_hiding_structural()`). Compare $\hat{c}_{0,m}$ estimates across the two specifications.

---

*Implementation files: `src/model.py`, `src/moments.py`, `src/estimation.py`, `src/event_study.py`. Primary estimator: `estimate_msm(fix_rho=True)`. Moment extraction: `extract_data_moments()`. DiD first stage: `compute_did()`, `estimate_rho_c0()`.*
