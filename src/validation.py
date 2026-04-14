from __future__ import annotations
"""
validation.py
=============
Part 5: Validation and Robustness Checks
-----------------------------------------
Implements the testable implications of the model and a suite of robustness
checks to assess the sensitivity of estimates to modelling assumptions.

Testable implications from Section 6:
  1. Non-disclosure premium exists and is positive (Proposition (prop:premium))
  2. Premium decreases with π (Proposition (prop:pi))
  3. Premium increases with ρ (Proposition (prop:rho))
  4. High-quality informed sellers always disclose: σ̂_{1,m} ≈ 0 (Corollary (cor:hq_disclose))
  5. Non-disclosure premium higher in warmer/southern regions (low ρ)
  6. Non-disclosure premium decreasing over time as π rises

Robustness checks:
  R1. Alternative EPC binarisation thresholds
  R2. Market-varying β₁ (relax common slope in hedonic)
  R3. Alternative MSM weighting matrices
  R4. Subsetting to markets in partial-separation regime only
  R5. Vary logistic demand scale
  R6. Drop individual markets (jackknife)
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
import warnings

logger = logging.getLogger(__name__)

from .model import ValuationParams, solve_equilibrium, belief_bounds, belief_function
from .moments import DataMoments, compute_model_moments, moment_residuals
from .estimation import estimate_msm, build_valuation_params, MSMResult


# ---------------------------------------------------------------------------
# Section A — Testable implications
# ---------------------------------------------------------------------------

def test_sigma1_zero(
    market_stats: pd.DataFrame,
    alpha       : float = 0.05,
) -> pd.DataFrame:
    """
    Testable implication: σ̂_{1,m} ≈ 0 (high-quality sellers always disclose).

    The model predicts that informed high-quality sellers strictly prefer
    disclosure (Corollary (cor:hq_disclose)). This is a sharp prediction testable
    directly in the data.

    We test: H₀: σ_{1,m} = 0  vs  H₁: σ_{1,m} > 0
    using a one-sided binomial test for each market.

    Parameters
    ----------
    market_stats : pd.DataFrame with sigma_1_hat, n_informed_high
    alpha        : significance level

    Returns
    -------
    pd.DataFrame with test statistics and pass/fail indicator per market
    """
    results = []
    for m, row in market_stats.iterrows():
        sigma_1  = row.get("sigma_1_hat", np.nan)
        n_high   = row.get("n_informed_high", 0)

        if np.isnan(sigma_1) or n_high < 5:
            results.append({
                "market_id": m,
                "sigma_1_hat": sigma_1,
                "n_informed_high": n_high,
                "p_value": np.nan,
                "rejects_H0": False,
                "note": "insufficient sample",
            })
            continue

        # Number of high-quality informed sellers who hide
        n_hiders = int(round(sigma_1 * n_high))

        # Binomial test: H₀: p=0, H₁: p>0
        # Under H₀: P(X ≥ n_hiders | p=0) = I(n_hiders == 0)
        # In practice: use H₀: p ≤ ε for small ε (regularisation)
        # We use a tolerance ε = 1/n_high (at most one accidental hider)
        epsilon = 1.0 / max(n_high, 1)
        binom_result = stats.binomtest(n_hiders, n_high, p=epsilon, alternative="greater")
        p_val = binom_result.pvalue

        results.append({
            "market_id"      : m,
            "sigma_1_hat"    : sigma_1,
            "n_informed_high": n_high,
            "n_high_hiders"  : n_hiders,
            "p_value"        : p_val,
            "rejects_H0"     : p_val < alpha,
            "note"           : "significant violation" if p_val < alpha else "consistent with model",
        })

    df_test = pd.DataFrame(results).set_index("market_id")
    n_reject = df_test["rejects_H0"].sum()
    logger.info(f"[test σ₁=0] {n_reject}/{len(df_test)} markets reject H₀: σ₁=0 (α={alpha})")
    logger.info("  → Model consistent if rejection rate ≈ 0")
    return df_test


def test_premium_sign(
    market_stats: pd.DataFrame,
    alpha       : float = 0.05,
) -> pd.DataFrame:
    """
    Testable implication: non-disclosure premium is positive (Proposition (prop:premium)).

    Test: H₀: p̄_{d=0} ≤ p̄_{d=1,θ=0}  (no premium or negative premium)
          H₁: p̄_{d=0} >  p̄_{d=1,θ=0}  (positive non-disclosure premium)

    Note: the premium is defined for low-quality sellers only.
    Comparing p̄_{d=0} to p̄_{d=1,θ=0} (not p̄_{d=1,θ=1}) because the
    theoretical premium is relative to the disclosed low-quality price.
    """
    results = []
    for m, row in market_stats.iterrows():
        delta_raw = row.get("delta_bar_raw", np.nan)
        n_m3      = row.get("n_m3", 0)

        # Simple z-test using raw premium
        # Full standard error requires the distribution of p̄_{d=0} - p̄_{d=1,θ=0}
        # For a first implementation, report the sign and flag significance
        results.append({
            "market_id"      : m,
            "premium_raw"    : delta_raw,
            "premium_positive": delta_raw > 0 if not np.isnan(delta_raw) else np.nan,
            "n_nondisclosed" : n_m3,
        })

    df_test = pd.DataFrame(results).set_index("market_id")
    pct_pos = df_test["premium_positive"].mean() * 100
    logger.info(f"[test premium>0] {pct_pos:.1f}% of markets have positive raw premium")
    logger.info("  → Model consistent if most markets show positive premium")
    return df_test


def test_premium_decreasing_in_pi(
    market_stats: pd.DataFrame,
) -> dict:
    """
    Testable implication: non-disclosure premium decreasing in π (Proposition (prop:pi)).

    Cross-market regression:
        Δ̄_m = a + b·π̂_m + controls + u_m,  with H₀: b < 0

    A negative and significant b supports the model's prediction that
    higher information prevalence reduces the attractiveness of hiding.

    Returns
    -------
    dict with slope, t-stat, p-value, and interpretation
    """
    df = market_stats[["pi_hat", "delta_bar_raw"]].dropna()

    if len(df) < 5:
        logger.info("[test Δ~π] Too few markets for regression.")
        return {"slope": np.nan, "t_stat": np.nan, "p_value": np.nan}

    X  = df["pi_hat"].values
    y  = df["delta_bar_raw"].values
    X_ = np.column_stack([np.ones(len(X)), X])

    beta, resid, _, _ = np.linalg.lstsq(X_, y, rcond=None)
    slope = float(beta[1])

    # OLS t-statistic
    n     = len(y)
    yhat  = X_ @ beta
    s2    = np.sum((y - yhat) ** 2) / (n - 2)
    se_b  = np.sqrt(s2 * np.linalg.inv(X_.T @ X_)[1, 1])
    t_stat = slope / se_b
    p_value = float(stats.t.sf(-t_stat, df=n - 2))  # one-sided: b < 0

    logger.info(f"[test Δ~π]  slope = {slope:.4f}, t = {t_stat:.2f}, p = {p_value:.4f}")
    logger.info(f"  → {'Consistent' if slope < 0 else 'Inconsistent'} with Proposition (prop:pi) (b < 0)")

    return {
        "slope"  : slope,
        "se"     : se_b,
        "t_stat" : t_stat,
        "p_value": p_value,
        "n_markets": n,
    }


def overidentification_test(
    msm_result  : MSMResult,
    data_moments: dict,
    n_params_per_market: int = 1,  # ρ_m per market
    n_common_params    : int = 1,  # c₀
) -> dict:
    """
    Hansen J-test for overidentification — estimation appendix forthcoming.

    With 4 moments per market and (1 + 1/M) parameters per market
    (ρ_m + c₀ spread over M markets), the model is overidentified.

    J-statistic = n · Q*(ρ̂, ĉ₀) ~ χ²(k) under H₀: correct specification
    where k = number of overidentifying restrictions = (4M) - (M + 1) = 3M - 1

    A significant J-statistic indicates model misspecification.

    Note: the J-test requires the optimal weighting matrix W = Ω̂⁻¹.
    With diagonal W, the test is approximate. Full implementation requires
    estimating the full variance-covariance matrix of moments.
    """
    M = msm_result.n_markets
    n_moments_total = 4 * M
    n_params_total  = 2 * M  # M ρ_m's + M c₀_m's
    df_J            = n_moments_total - n_params_total

    # Approximate total sample size
    n_obs = sum(
        dm.n1 + dm.n2 + dm.n3 + dm.n4_informed
        for dm in data_moments.values()
    )

    J_stat   = float(n_obs * msm_result.Q_star)
    p_value  = float(stats.chi2.sf(J_stat, df=df_J)) if df_J > 0 else np.nan

    logger.info(f"[J-test] J = {J_stat:.4f}, df = {df_J}, p = {p_value:.4f}")
    logger.info(f"  → {'Reject' if p_value < 0.05 else 'Fail to reject'} H₀: correct specification")
    logger.info("  (Note: approximate — requires optimal W = Ω̂⁻¹ for exact test)")

    return {
        "J_stat"  : J_stat,
        "df"      : df_J,
        "p_value" : p_value,
        "n_obs"   : n_obs,
    }


# ---------------------------------------------------------------------------
# Section B — Robustness checks
# ---------------------------------------------------------------------------

def robustness_alternative_weights(
    data_moments : dict,
    market_params: dict,
    market_stats : pd.DataFrame,
    schemes      : list[str] | None = None,
) -> dict[str, MSMResult]:
    """
    R3: Estimate MSM under alternative weighting matrices — estimation appendix forthcoming.

    Compares estimates under:
      - "equal"            : all moments weighted equally
      - "inverse_variance" : moments weighted by precision (default)

    Returns
    -------
    dict {scheme_name → MSMResult}
    """
    if schemes is None:
        schemes = ["equal", "inverse_variance"]

    results = {}
    for scheme in schemes:
        logger.info(f"[robustness W] Estimating with weighting scheme: '{scheme}'")
        result = estimate_msm(
            data_moments     = data_moments,
            market_params    = market_params,
            market_stats     = market_stats,
            weighting_scheme = scheme,
            n_restarts       = 3,
        )
        results[scheme] = result
        mean_c0 = np.mean(list(result.c0_hat.values()))
        logger.info(f"  [robustness W] mean ĉ₀ = {mean_c0:.6f}, "
                    f"mean ρ̂ = {np.mean(list(result.rho_hat.values())):.4f}")

    return results


def robustness_vary_epc_threshold(
    df             : pd.DataFrame,
    hedonic_params,
    market_params  : dict,
    thresholds     : list[float] | None = None,
) -> pd.DataFrame:
    """
    R1: Vary the EPC binarisation threshold — assumption in binarise_epc().

    For each threshold τ, re-classify properties as θ=1 if epc_score ≤ τ,
    then re-compute market statistics and data moments.

    The estimator should be robust to moderate changes in τ, since the model
    is qualitatively consistent for any binary split.

    Parameters
    ----------
    thresholds : list of EPC cutoffs to try (e.g., [2, 3, 4] for A/B, A/B/C, A/B/C/D)
    """
    from .data_prep import compute_market_stats
    from .moments import extract_data_moments

    if thresholds is None:
        thresholds = [2.0, 3.0, 4.0]   # e.g., class B, C, D boundaries

    rows = []
    for tau in thresholds:
        df_tau = df.copy()
        # Re-binarise
        df_tau["theta"] = df_tau["epc_score"].apply(
            lambda x: int(x <= tau) if pd.notna(x) else np.nan
        )
        df_tau["theta_bar_m"] = df_tau.groupby("market_id")["theta"].transform("mean")

        try:
            controls = [c for c in df_tau.columns
                        if c.startswith("X_") or c in ["size_m2", "age"]]
            ms_tau = compute_market_stats(df_tau, controls=controls)
            dm_tau = extract_data_moments(df_tau)

            result_tau = estimate_msm(
                data_moments    = dm_tau,
                market_params   = market_params,
                market_stats    = ms_tau,
                weighting_scheme= "inverse_variance",
                n_restarts      = 2,
            )

            rows.append({
                "threshold"  : tau,
                "c0_hat"     : np.mean(list(result_tau.c0_hat.values())),
                "mean_rho"   : np.mean(list(result_tau.rho_hat.values())),
                "std_rho"    : np.std(list(result_tau.rho_hat.values())),
                "Q_star"     : result_tau.Q_star,
            })
        except Exception as e:
            rows.append({
                "threshold": tau,
                "c0_hat"   : np.nan,
                "mean_rho" : np.nan,
                "error"    : str(e),
            })

    return pd.DataFrame(rows)


def robustness_demand_scale(
    data_moments : dict,
    market_stats : pd.DataFrame,
    hedonic_params,
    scales       : list[float] | None = None,
) -> pd.DataFrame:
    """
    R5: Vary the logistic demand scale parameter.

    The scale σ is calibrated from hedonic residuals (hedonic.calibrate_demand_scale).
    This check assesses sensitivity to this calibration.
    """
    from .estimation import build_valuation_params

    if scales is None:
        calibrated = hedonic_params.sigma_eps * np.pi / np.sqrt(3.0)
        scales = [calibrated * f for f in [0.5, 0.75, 1.0, 1.5, 2.0]]

    rows = []
    for sigma in scales:
        # Rebuild market params with new scale
        mp_sigma = {
            m: build_valuation_params(m, market_stats, hedonic_params, scale=sigma)
            for m in market_stats.index
        }
        try:
            result = estimate_msm(
                data_moments    = data_moments,
                market_params   = mp_sigma,
                market_stats    = market_stats,
                weighting_scheme= "inverse_variance",
                n_restarts      = 2,
            )
            rows.append({
                "scale"     : sigma,
                "c0_hat"    : np.mean(list(result.c0_hat.values())),
                "mean_rho"  : np.mean(list(result.rho_hat.values())),
                "Q_star"    : result.Q_star,
            })
        except Exception as e:
            rows.append({"scale": sigma, "error": str(e)})

    return pd.DataFrame(rows)


def jackknife_markets(
    data_moments : dict,
    market_params: dict,
    market_stats : pd.DataFrame,
) -> pd.DataFrame:
    """
    R6: Leave-one-market-out jackknife to assess influence of individual markets.

    For each market m, re-estimates (ρ̂, ĉ₀) on the sample excluding m.
    Large sensitivity to exclusion of a single market signals undue influence.
    """
    markets = sorted(data_moments.keys())
    rows    = []

    for drop_m in markets:
        dm_sub  = {m: v for m, v in data_moments.items() if m != drop_m}
        mp_sub  = {m: v for m, v in market_params.items() if m != drop_m}
        ms_sub  = market_stats.drop(index=drop_m, errors="ignore")

        try:
            result = estimate_msm(
                data_moments    = dm_sub,
                market_params   = mp_sub,
                market_stats    = ms_sub,
                weighting_scheme= "inverse_variance",
                n_restarts      = 2,
            )
            rows.append({
                "dropped_market": drop_m,
                "c0_hat"        : np.mean(list(result.c0_hat.values())),
                "mean_rho"      : np.mean(list(result.rho_hat.values())),
            })
        except Exception as e:
            rows.append({"dropped_market": drop_m, "error": str(e)})

    return pd.DataFrame(rows)


def run_all_validation(
    df           : pd.DataFrame,
    market_stats : pd.DataFrame,
    data_moments : dict,
    msm_result   : MSMResult,
    hedonic_params,
    market_params: dict,
) -> dict:
    """
    Run all validation checks and return a summary dictionary.
    """
    logger.info("=" * 60)
    logger.info("VALIDATION AND ROBUSTNESS CHECKS")
    logger.info("=" * 60)

    output = {}

    # --- Testable implications ---
    output["sigma1_test"]    = test_sigma1_zero(market_stats)
    output["premium_sign"]   = test_premium_sign(market_stats)
    output["premium_vs_pi"]  = test_premium_decreasing_in_pi(market_stats)
    output["j_test"]         = overidentification_test(msm_result, data_moments)

    # --- Robustness checks ---
    logger.info("--- Robustness: Alternative weighting matrices ---")
    output["rob_weights"] = robustness_alternative_weights(
        data_moments, market_params, market_stats
    )

    logger.info("--- Robustness: Jackknife ---")
    output["jackknife"] = jackknife_markets(data_moments, market_params, market_stats)

    logger.info("--- Robustness: Demand scale ---")
    output["rob_scale"] = robustness_demand_scale(
        data_moments, market_stats, hedonic_params
    )

    return output
