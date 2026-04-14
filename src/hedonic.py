from __future__ import annotations
"""
hedonic.py
==========
Part 2 (continued): Hedonic Price Regression and Hiding Premium
---------------------------------------------------------------
Implements the hedonic steps of the estimation (estimation appendix forthcoming).

Step 1: Estimate hedonic regression on truthful disclosers (estimation appendix forthcoming)
Step 2: Compute counterfactual prices for strategic hiders (estimation appendix forthcoming)
Step 3: Compute individual hiding premiums (estimation appendix forthcoming)
Step 4: Aggregate market-level hiding premium Δ̄_m (estimation appendix forthcoming)
Step 5: Back out ρ_m using the direct estimator (estimation appendix forthcoming)

Key identification argument (estimation appendix forthcoming):
  For strategic hiders (d=0, K=1), we observe:
    - Their actual listing price (with hiding premium)
    - Their true (verified) quality θ_i (from ADEME)
  This lets us compute the counterfactual price they would have obtained
  under disclosure, and hence the premium from hiding.

Assumption (benchmark α_k = β_k, Sec. "Buyer Valuations and Demand"):
  Buyers value quality the same whether verified or inferred. Under this
  benchmark, the hedonic coefficient β̂_1 from disclosed transactions directly
  measures the causal price premium of quality, applicable to inferred quality
  as well.
"""

import logging
from typing import Any
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Section A — Hedonic regression (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

@dataclass
class HedonicParams:
    """
    Output of the hedonic regression on truthful disclosers.

    Estimated equation (estimation appendix forthcoming):
        log(p_i) = α_m + β₁·θ_i + X_i'·γ + ε_i

    Estimated on: d_i = 1 AND K_i = 1 (truthful disclosers only)

    Parameters
    ----------
    beta_1       : EPC quality premium (percentage log-price gain for θ=1 vs θ=0)
    alpha_m      : dict {market_id → market fixed effect α̂_m}
    gamma        : dict {param_name → coefficient} — all OLS params including dummies
    sigma_eps    : residual standard deviation (used to calibrate demand scale)
    n_obs        : number of observations used in regression
    r_squared    : R² of hedonic regression
    controls     : list of control variable names (as supplied by caller)
    cat_controls : categorical controls (wrapped in C() in the formula)
    cont_controls: continuous controls (entered linearly)
    cat_refs     : {col → reference category used} for categorical controls
    fitted_model : statsmodels RegressionResultsWrapper (used for prediction)
    beta_1_m     : {market_id → float} market-specific β₁_m
    sigma_eps_m  : {market_id → float} market-specific σ̂_ε_m
    """
    beta_1       : float
    alpha_m      : dict
    gamma        : dict
    sigma_eps    : float
    n_obs        : int
    r_squared    : float
    controls     : list[str]
    cat_controls : list[str]
    cont_controls: list[str]
    cat_refs     : dict
    fitted_model : Any           = field(default=None, repr=False)
    beta_1_m     : dict          = field(default_factory=dict)
    sigma_eps_m  : dict          = field(default_factory=dict)


def estimate_hedonic(
    df       : pd.DataFrame,
    controls : list[str],
    market_col: str = "market_id",
) -> HedonicParams:
    """
    Estimate the hedonic price function on truthful disclosers — estimation appendix forthcoming.

    Specification:
        log(p_i) = α_m + β₁·θ_i + Σ_n γ_n·X_{in} + ε_i

    Sample restriction: d_i = 1 AND K_i = 1 (informed sellers who disclosed).
    These are "clean" observations where the buyer and researcher observe the
    same verified quality θ_i.

    Market fixed effects α_m allow level differences in prices across markets
    while imposing common slopes β₁, γ (pooled identification of EPC premium).
    An alternative with market-varying β₁ is implemented in robustness checks.

    Parameters
    ----------
    df        : listing-level DataFrame (from classify_listings)
    controls  : list of property characteristic column names
    market_col: name of market identifier column

    Returns
    -------
    HedonicParams with estimated β̂₁, γ̂, α̂_m, σ̂_ε
    """
    # ── Sample: truthful disclosers only ─────────────────────────────────────
    mask   = (df["d"] == 1) & (df["K"] == 1)
    df_reg = df[mask].copy()

    if len(df_reg) < 50:
        raise ValueError(
            f"Too few truthful disclosers for hedonic regression: {len(df_reg)}. "
            "Expand sample or aggregate markets."
        )

    # ── Classify controls: categorical (object/category dtype) vs continuous ─
    def _mode(s: pd.Series):
        """Modal value; first mode if tied."""
        return s.mode().iloc[0]

    def _is_cat(col: str) -> bool:
        if col not in df_reg.columns:
            return False
        # Use is_numeric_dtype so pandas 3.0 str dtype (and CategoricalDtype,
        # object, ArrowDtype for strings, etc.) are all treated as categorical.
        return not pd.api.types.is_numeric_dtype(df_reg[col])

    cat_controls  = [c for c in controls if _is_cat(c)]
    cont_controls = [c for c in controls if c in df_reg.columns and not _is_cat(c)]

    # ── Reference categories: mode over the regression sample ────────────────
    # Using the most frequent category minimises dummy collinearity risk and
    # gives the intercept a sensible interpretation (typical dwelling).
    cat_refs = {c: _mode(df_reg[c]) for c in cat_controls}

    def _c_term(col: str, ref) -> str:
        """Patsy C() with Treatment reference; quotes only string levels."""
        if isinstance(ref, str):
            return f"C({col}, Treatment(reference='{ref}'))"
        return f"C({col}, Treatment(reference={ref}))"

    # ── Build formula terms ───────────────────────────────────────────────────
    ctrl_terms = list(cont_controls)   # continuous: enter linearly
    for c in cat_controls:
        ctrl_terms.append(_c_term(c, cat_refs[c]))

    # city_id is NOT added: every market (IRIS) belongs to exactly one city,
    # so city FEs are a linear combination of market FEs → always collinear.
    # Including both causes numerically unstable coefficient estimates.

    market_ref = _mode(df_reg[market_col])
    ctrl_str   = " + ".join(ctrl_terms) if ctrl_terms else "1"
    formula    = (f"log_price ~ {_c_term(market_col, market_ref)} "
                  f"+ theta + {ctrl_str}")

    result = smf.ols(formula=formula, data=df_reg).fit(cov_type="HC3")

    # ── Extract β̂₁ ───────────────────────────────────────────────────────────
    beta_1_hat = float(result.params.get("theta", np.nan))

    # ── Extract market fixed effects α̂_m ─────────────────────────────────────
    # Reference market is absorbed in the intercept.
    intercept    = float(result.params.get("Intercept", 0.0))
    market_c_str = _c_term(market_col, market_ref)   # e.g. "C(market_id, Treatment(reference=5))"
    alpha_m      = {}
    for market in df[market_col].unique():
        key = f"{market_c_str}[T.{market}]"
        fe  = float(result.params.get(key, 0.0))
        alpha_m[market] = intercept + fe

    # ── Store all estimated coefficients in gamma ─────────────────────────────
    gamma = {k: float(v) for k, v in result.params.items()}

    sigma_eps = float(np.sqrt(result.mse_resid))

    logger.info(f"[hedonic] β̂₁ = {beta_1_hat:.4f}  (pooled EPC premium, log-price)")
    logger.info(f"[hedonic] σ̂_ε = {sigma_eps:.4f}  (residual std dev → demand scale)")
    logger.info(f"[hedonic] n = {len(df_reg)}, R² = {result.rsquared:.3f}")

    # ── Per-market β₁_m and σ̂_ε_m ────────────────────────────────────────────
    # Categorical controls use per-market modes as references.
    # city_id is excluded (constant within a single market).
    beta_1_m    = {}
    sigma_eps_m = {}
    n_fallback  = 0
    for m, grp_m in df_reg.groupby(market_col):
        if len(grp_m) < 20 or grp_m["theta"].nunique() < 2:
            beta_1_m[m]    = beta_1_hat
            sigma_eps_m[m] = sigma_eps
            n_fallback     += 1
            continue

        pm_terms = list(cont_controls)
        for c in cat_controls:
            if c in grp_m.columns and grp_m[c].nunique() > 1:
                pm_terms.append(_c_term(c, _mode(grp_m[c])))
        pm_ctrl_str = " + ".join(pm_terms) if pm_terms else "1"

        res_m = smf.ols(f"log_price ~ theta + {pm_ctrl_str}", data=grp_m).fit()
        pval_theta = float(res_m.pvalues.get("theta", 1.0))
        if pval_theta > 0.10:
            beta_1_m[m] = beta_1_hat
            n_fallback  += 1
        else:
            beta_1_m[m] = float(res_m.params["theta"])
        sigma_eps_m[m] = float(np.sqrt(res_m.mse_resid))

    logger.info(
        f"[hedonic] β̂₁_m (market-specific): "
        f"mean={np.mean(list(beta_1_m.values())):.4f}  "
        f"std={np.std(list(beta_1_m.values())):.4f}  "
        f"[{min(beta_1_m.values()):.4f}, {max(beta_1_m.values()):.4f}]  "
        f"({n_fallback} markets used pooled fallback: too few obs / no EPC variation / p>0.10)"
    )

    return HedonicParams(
        beta_1        = beta_1_hat,
        alpha_m       = alpha_m,
        gamma         = gamma,
        sigma_eps     = sigma_eps,
        n_obs         = len(df_reg),
        r_squared     = float(result.rsquared),
        controls      = controls,
        cat_controls  = cat_controls,
        cont_controls = cont_controls,
        cat_refs      = cat_refs,
        fitted_model  = result,
        beta_1_m      = beta_1_m,
        sigma_eps_m   = sigma_eps_m,
    )


def predict_log_price(
    row           : pd.Series,
    hedonic_params: HedonicParams,
    theta_override: float | None = None,
    market_col    : str = "market_id",
) -> float:
    """
    Predict log price from the hedonic regression — estimation appendix forthcoming.

        log(p̂_i) = α̂_m + β̂₁·θ_i + X_i'·γ̂

    Uses the stored fitted model (hedonic_params.fitted_model) — estimation appendix forthcoming — so that
    categorical dummy encoding is handled automatically and consistently
    with the estimation formula.

    Parameters
    ----------
    row            : single listing row (pd.Series)
    hedonic_params : estimated hedonic parameters (must have fitted_model set)
    theta_override : if given, substitute this θ value before predicting
                     (used to compute counterfactual disclosure prices)
    market_col     : column name for market identifier
    """
    # pd.DataFrame([row]) preserves per-column dtypes; .to_frame().T does not.
    row_df = pd.DataFrame([row])
    if theta_override is not None:
        row_df["theta"] = float(theta_override)
    return float(hedonic_params.fitted_model.predict(row_df).iloc[0])


# ---------------------------------------------------------------------------
# Section B — Counterfactual prices and hiding premiums (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def compute_hiding_premium(
    df            : pd.DataFrame,
    hedonic_params: HedonicParams,
    market_col    : str = "market_id",
) -> pd.DataFrame:
    """
    Compute individual and market-level hiding premiums — estimation appendix forthcoming.

    For each strategic hider i (d=0, K=1, θ=0):

    Step 1 — Counterfactual log price (estimation appendix forthcoming):
        log(p̂_i^cf) = α̂_m + β̂₁·θ_i + X_i'·γ̂
        (predicted price the seller would have obtained under disclosure)

    Step 2 — Individual hiding premium (estimation appendix forthcoming):
        Δ_i = log(p_i) - log(p̂_i^cf)

    Step 3 — Market-level premium (estimation appendix forthcoming):
        Δ̄_m = (1/N) · Σ_{i: K=1, θ=0, d=0} Δ_i

    Identification note (estimation appendix forthcoming):
      We focus on informed LOW-quality hiders (K=1, θ=0, d=0) because:
        - For high-quality hiders (θ=1): theory predicts they ALWAYS disclose
          (σ₁* = 0, Corollary (cor:hq_disclose)). Their presence is a testable violation.
        - For uninformed sellers (K=0): no θ_i observed, no counterfactual.
      By restricting to θ=0 strategic hiders, Δ̄_m measures the pure
      concealment premium: the price gain from pooling with uninformed sellers.

    Returns
    -------
    df with columns [log_price_cf, delta_i] for strategic hiders;
    plus market_premium DataFrame with Δ̄_m per market.
    """
    # ---- Individual hiding premiums (strategic hiders only) ----
    mask_hiders = (df["d"] == 0) & (df["K"] == 1) & (df["theta"] == 0)
    df_hiders   = df[mask_hiders].copy()

    if len(df_hiders) == 0:
        raise ValueError("No strategic hiders found. Check group classification.")

    # Counterfactual: predicted price under truthful disclosure of θ_i=0.
    # Strategic hiders already have theta=0, so predict directly on df_hiders.
    # This is vectorized (no apply), avoids dtype issues, and is much faster.
    df_hiders["log_price_cf"] = hedonic_params.fitted_model.predict(df_hiders)

    # Individual hiding premium Δ_i (estimation appendix forthcoming)
    df_hiders["delta_i"] = df_hiders["log_price"] - df_hiders["log_price_cf"]

    # ---- Market-level hiding premium Δ̄_m (estimation appendix forthcoming) ----
    market_premium = (
        df_hiders
        .groupby(market_col)
        .agg(
            delta_bar   = ("delta_i", "mean"),
            delta_std   = ("delta_i", "std"),
            n_hiders    = ("delta_i", "count"),
        )
        .reset_index()
    )

    # Variance of Δ̄_m (for inverse-variance weighting in MSM)
    market_premium["delta_var"] = (
        market_premium["delta_std"] ** 2 / market_premium["n_hiders"]
    )

    logger.info(f"[hiding premium] {len(df_hiders)} strategic hiders across "
               f"{len(market_premium)} markets")
    logger.info(f"[hiding premium] Mean Δ̄ = {market_premium['delta_bar'].mean():.4f}")
    logger.info(f"[hiding premium] Std  Δ̄ = {market_premium['delta_bar'].std():.4f}")

    return df_hiders, market_premium


# ---------------------------------------------------------------------------
# Section C — Direct estimator for ρ_m (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def estimate_rho_direct(
    market_stats  : pd.DataFrame,
    market_premium: pd.DataFrame,
    hedonic_params: HedonicParams,
    market_col    : str = "market_id",
) -> pd.DataFrame:
    """
    Back out buyer sensitivity ρ_m from the observed hiding premium — estimation appendix forthcoming.

    Theoretical relationship (estimation appendix forthcoming):
        Δ̄_m ≈ ρ_m · β₁ · e*_m

    Inversion (estimation appendix forthcoming):
        ρ̂_m = Δ̄_m / (β̂₁ · ê*_m)

    where:
      - Δ̄_m is the market-level hiding premium (from compute_hiding_premium)
      - β̂₁ is the hedonic EPC premium (from estimate_hedonic)
      - ê*_m is the equilibrium belief at the observed hiding rate σ̂₀_m (estimation appendix forthcoming):
          ê*_m = (1 − π̂_m)·θ̂_m / [π̂_m·(1−θ̂_m)·σ̂₀_m + (1−π̂_m)]

    Validity conditions:
      1. Approximation (estimation appendix forthcoming) requires the profit function to be approximately
         linear in the valuation shift. This holds when the demand scale σ is
         large relative to β₁ · e*. Verify by checking the model-implied premium
         vs the linearised version.
      2. ρ̂_m must fall in [0, 1]; values outside indicate model misspecification,
         small samples, or violations of the approximation.

    Parameters
    ----------
    market_stats   : output of compute_market_stats (contains π̂_m, θ̂_m)
    market_premium : output of compute_hiding_premium (contains Δ̄_m)
    hedonic_params : estimated hedonic parameters (for β̂₁)

    Returns
    -------
    pd.DataFrame with ρ̂_m, ê*_m, and Δ̄_m per market
    """
    # Merge market stats with hiding premium
    df_rho = market_stats.reset_index().merge(
        market_premium, on=market_col, how="left"
    )

    # Equilibrium belief ê*_m evaluated at the observed hiding rate σ̂₀ (estimation appendix forthcoming):
    #   e(σ₀) = (1−π)·θ̄ / [π·(1−θ̄)·σ₀ + (1−π)]
    # Using σ₀=1 (all low-quality hide) understates e* and inflates ρ̂; we use
    # the empirical σ̂₀ from compute_market_stats instead.
    sigma_0 = df_rho["sigma_0_hat"].clip(0.0, 1.0).fillna(1.0)
    pi      = df_rho["pi_hat"]
    theta   = df_rho["theta_bar_hat"]
    df_rho["e_star_hat"] = (
        (1.0 - pi) * theta
        / (pi * (1.0 - theta) * sigma_0 + (1.0 - pi))
    )

    # Use market-specific β₁_m in the denominator (estimation appendix forthcoming)
    df_rho["beta_1_m"] = df_rho[market_col].map(
        lambda m: hedonic_params.beta_1_m.get(m, hedonic_params.beta_1)
    )

    # Denominator of direct estimator
    df_rho["denom_direct"] = df_rho["beta_1_m"] * df_rho["e_star_hat"]

    # Direct estimator of ρ_m (estimation appendix forthcoming)
    df_rho["rho_hat_direct"] = df_rho["delta_bar"] / df_rho["denom_direct"]

    # Clip to [0, 1] and flag out-of-range values (diagnostic)
    df_rho["rho_hat_clipped"] = df_rho["rho_hat_direct"].clip(0.0, 1.0)
    df_rho["rho_out_of_range"] = (
        (df_rho["rho_hat_direct"] < 0) | (df_rho["rho_hat_direct"] > 1)
    )

    n_oob = df_rho["rho_out_of_range"].sum()
    if n_oob > 0:
        logger.warning(
            f"{n_oob} markets have ρ̂_m outside [0,1]. "
            "Check sample size, hedonic specification, or approximation quality."
        )

    logger.info(f"[direct ρ] Mean ρ̂ = {df_rho['rho_hat_direct'].mean():.4f}")
    logger.info(f"[direct ρ] Std  ρ̂ = {df_rho['rho_hat_direct'].std():.4f}")

    return df_rho.set_index(market_col)


# ---------------------------------------------------------------------------
# Section D — Calibrate demand scale from hedonic residuals
# ---------------------------------------------------------------------------

def calibrate_demand_scale(hedonic_params: HedonicParams) -> float:
    """
    Calibrate the logistic demand scale σ from hedonic residual variance.

    The taste shock ε in the model corresponds to the idiosyncratic variation
    in willingness to pay. If ε ~ N(0, σ²_ε), then under the probit-logit
    equivalence, the logistic scale σ_G ≈ σ_ε · π / sqrt(3).

    For a unit-normal approximation: σ_G = σ_ε (simplest case).

    This is a calibration, not an estimation. The scale enters the optimal price
    computation and affects the profit level. Robustness to different scale
    values is checked in validation.py.

    Reference: Train (2009), "Discrete Choice Methods with Simulation", Ch. 3.
    """
    # Probit-logit scale equivalence: logistic scale ≈ σ_ε × π/√3
    pi_over_sqrt3 = np.pi / np.sqrt(3.0)
    scale = hedonic_params.sigma_eps * pi_over_sqrt3

    logger.info(f"[scale] σ̂_ε = {hedonic_params.sigma_eps:.4f} "
               f"→ logistic scale = {scale:.4f}")
    return float(scale)


def calibrate_demand_scale_m(hedonic_params: HedonicParams) -> dict:
    """
    Return per-market logistic demand scales from market-specific residual std devs.

    Uses the same probit-logit equivalence as calibrate_demand_scale but applied
    to each market's own σ̂_ε_m.  Markets that fell back to the pooled σ̂_ε will
    also get the pooled scale.

    Returns
    -------
    dict {market_id: float}  — logistic scale σ_m for each market
    """
    pi_over_sqrt3 = np.pi / np.sqrt(3.0)
    scales = {m: float(sig * pi_over_sqrt3)
              for m, sig in hedonic_params.sigma_eps_m.items()}
    logger.info(
        f"[scale_m] market-specific logistic scales: "
        f"mean={np.mean(list(scales.values())):.4f}  "
        f"std={np.std(list(scales.values())):.4f}  "
        f"[{min(scales.values()):.4f}, {max(scales.values()):.4f}]"
    )
    return scales
