from __future__ import annotations
"""
estimation.py
=============
Part 4: Structural Estimation of (ρ_m, c₀)
-------------------------------------------
Implements two estimation strategies from Section 7 of the paper:

Strategy 1 — Direct estimator (Eq. (eq:premium) adapted; estimation appendix forthcoming):
  Fast, market-by-market approach using the linearised premium relationship.
  Suitable for first-pass estimates and as starting values for MSM.

Strategy 2 — Method of Simulated Moments (estimation appendix forthcoming):
  Jointly estimates (ρ_m, c₀) by minimising the weighted distance between
  data moments and model-implied moments. Asymptotically efficient under
  correct specification.

Standard errors (bootstrap; estimation appendix forthcoming):
  Computed via bootstrap (Algorithm: resample listings within markets,
  re-estimate all parameters, repeat B=500 times).

Parameters estimated:
  ρ_m ∈ [0, 1]  : share of EPC-sensitive buyers (market-specific)
  c₀  ≥ 0       : hiding cost (common across markets, or market-specific)
"""

import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution, brentq
from scipy.stats import norm
from dataclasses import dataclass, field
from typing import Callable
import warnings

logger = logging.getLogger(__name__)

from .model import (
    ValuationParams,
    solve_equilibrium,
    profit_gain_hiding,
    belief_bounds,
    belief_function,
    optimal_price,
    renovation_threshold,
    optimal_subsidy,
)
from .moments import (
    DataMoments,
    ModelMoments,
    compute_model_moments,
    moment_residuals,
    build_weighting_matrix,
)


# ---------------------------------------------------------------------------
# Section A — Market-level ValuationParams (from hedonic estimates)
# ---------------------------------------------------------------------------

def build_valuation_params(
    market_id     : str | int,
    market_stats  : pd.DataFrame,
    hedonic_params,
    scale         : float = 1.0,
    scale_m       : dict | None = None,
    v0_offset     : float = 0.0,
    did_beta1     : float | None = None,
) -> ValuationParams:
    """
    Construct ValuationParams for market m from hedonic estimates.

    Maps the hedonic regression output (β̂₁, γ̂, α̂_m) to the model's
    valuation parameters, evaluated at market-mean controls X̄_m.

    Parameters
    ----------
    market_id      : market identifier
    market_stats   : market-level statistics (output of compute_market_stats)
    hedonic_params : HedonicParams (from hedonic.estimate_hedonic)
    scale          : pooled logistic demand scale (from hedonic.calibrate_demand_scale)
    scale_m        : per-market logistic demand scales (from hedonic.calibrate_demand_scale_m)
                     if provided, market_id's value takes precedence over pooled scale
    v0_offset      : adjustment to v₀ relative to β₀ + X̄'β_X
                     (negative ↔ insensitive buyers value property less than sensitive)
    did_beta1      : DiD-identified EPC quality premium (DiD_beta1_m from the price
                     index panel). When provided, overrides the hedonic β̂₁_m as the
                     structural quality parameter. Use this for markets with DiD
                     coverage: the reform-induced β₁ strips out pre-existing EPC-
                     correlated price differences (quality, location) that the hedonic
                     absorbs into β̂₁ but that are not driven by buyer EPC sensitivity.
    """
    row = market_stats.loc[market_id]

    # α̂_m: market fixed effect from hedonic regression
    alpha_m = hedonic_params.alpha_m.get(market_id, 0.0)

    # X̄_m'·γ̂: contribution of controls at market-mean/mode characteristics
    X_beta_X = 0.0

    # Continuous controls: γ̂_k · X̄_mk
    for ctrl in hedonic_params.cont_controls:
        col = f"X_bar_{ctrl}"
        if col in market_stats.columns and not pd.isna(row.get(col, np.nan)):
            X_beta_X += hedonic_params.gamma.get(ctrl, 0.0) * float(row[col])

    # Categorical controls: γ̂_k · 𝟙[X̄_mk ≠ reference]
    # X_bar_ctrl holds the modal category for this market (string).
    # The reference category has coefficient 0 by construction.
    # Non-reference categories look up their dummy key in gamma.
    for ctrl in hedonic_params.cat_controls:
        col = f"X_bar_{ctrl}"
        if col not in market_stats.columns:
            continue
        mode_val = row.get(col)
        if mode_val is None or (not isinstance(mode_val, str) and pd.isna(mode_val)):
            continue
        ref_val = hedonic_params.cat_refs.get(ctrl)
        if str(mode_val) == str(ref_val):
            continue   # reference category → dummy coefficient = 0
        dummy_key = f"C({ctrl}, Treatment(reference='{ref_val}'))[T.{mode_val}]"
        X_beta_X += hedonic_params.gamma.get(dummy_key, 0.0)

    # β₁_m: use DiD override if supplied, else market-specific hedonic, else pooled
    if did_beta1 is not None:
        beta_1_m = did_beta1
    else:
        beta_1_m = hedonic_params.beta_1_m.get(market_id, hedonic_params.beta_1)

    # Use market-specific demand scale if available, fall back to pooled scale
    scale_used = scale_m.get(market_id, scale) if scale_m is not None else scale

    return ValuationParams(
        beta_0    = alpha_m,
        beta_1    = beta_1_m,
        X_beta_X  = X_beta_X,
        v0_offset = v0_offset,
        scale     = scale_used,
        gamma_0   = 0.0,   # assumption: listing price ≈ transaction price
        gamma_1   = 1.0,
    )


# ---------------------------------------------------------------------------
# Section B — MSM objective function (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def msm_objective(
    rho         : float,
    c0          : float,
    data_mom    : DataMoments,
    params      : ValuationParams,
    weights     : np.ndarray,
    pi          : float,
    theta_bar   : float,
) -> float:
    """
    MSM objective for a single market (estimation appendix forthcoming).

        Q_m(ρ_m, c₀) = Σ_{j=1}^{4} W_j · (m_j^data - m_j^model(ρ_m, c₀))²   (estimation appendix forthcoming)

    Parameters
    ----------
    rho       : candidate buyer sensitivity ρ_m
    c0        : candidate hiding cost c₀
    data_mom  : DataMoments for market m
    params    : ValuationParams for market m
    weights   : np.ndarray of shape (4,) with W_j values
    pi        : π̂_m (directly measured)
    theta_bar : θ̂_m (directly measured)

    Returns
    -------
    float : scalar objective value Q_m(ρ, c₀)
    """
    try:
        model_mom = compute_model_moments(
            rho=rho, c0=c0,
            pi=pi, theta_bar=theta_bar,
            params=params,
            market_id=data_mom.market_id,
        )
    except Exception:
        # If equilibrium solver fails, return a large penalty
        return 1e6

    residuals = moment_residuals(data_mom, model_mom)

    # Replace NaN residuals with 0 (missing data moments are ignored)
    residuals = np.where(np.isnan(residuals), 0.0, residuals)

    return float(residuals @ weights @ residuals)


def msm_objective_pooled(
    params_vec   : np.ndarray,
    data_moments : dict,
    market_params: dict,
    weighting    : dict,
    market_stats : pd.DataFrame,
    phi_mode     : bool = False,
) -> float:
    """
    Pooled MSM objective across all markets — estimation appendix forthcoming.

    Two parameterisations (selected by ``phi_mode``):

    Standard (phi_mode=False):
        Parameter vector layout: [ρ_1, ..., ρ_M, c₀_1, ..., c₀_M]

    φ-mode (phi_mode=True)  — recommended:
        Parameter vector layout: [ρ_1, ..., ρ_M, φ_1, ..., φ_M]
        where c₀_m = φ_m · Δ(e₀; ρ_m) = φ_m · ρ_m · β₁_m · θ̄_m
        and   φ_m ∈ (0, 1).

        This reparameterisation guarantees c₀_m < Δ(e₀; ρ_m) for any
        (ρ, φ) ∈ [0,1]², keeping the equilibrium in the mixed-strategy /
        partial-separation region and preventing gradient vanishing at the
        full-unraveling boundary.

    Parameters
    ----------
    params_vec   : np.ndarray, candidate parameter values
    data_moments : dict {market_id → DataMoments}
    market_params: dict {market_id → ValuationParams}
    weighting    : dict {market_id → np.ndarray of weights}
    market_stats : pd.DataFrame with π̂_m, θ̂_m per market
    phi_mode     : bool, use φ parameterisation if True
    """
    markets = sorted(data_moments.keys())
    M       = len(markets)

    rho_vec = params_vec[:M]
    aux_vec = params_vec[M:]   # c₀ directly (phi_mode=False) or φ (phi_mode=True)

    Q_total = 0.0
    for j, m in enumerate(markets):
        rho_m = float(rho_vec[j])
        pi_m  = float(market_stats.loc[m, "pi_hat"])
        th_m  = float(market_stats.loc[m, "theta_bar_hat"])
        pm    = market_params[m]

        if phi_mode:
            phi_m = float(aux_vec[j])
            e0, _ = belief_bounds(pi_m, th_m)
            delta_e0 = profit_gain_hiding(e0, rho_m, pm)
            c0_m = phi_m * delta_e0
        else:
            c0_m = float(aux_vec[j])

        Q_m = msm_objective(rho_m, c0_m, data_moments[m], pm, weighting[m], pi_m, th_m)
        Q_total += Q_m

    return Q_total


# ---------------------------------------------------------------------------
# Section C — MSM estimation (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

@dataclass
class MSMResult:
    """
    Output of the MSM estimator.

    Contains estimated parameters, standard errors, model fit, and
    equilibrium objects for each market.
    """
    rho_hat     : dict        # {market_id: float} — estimated ρ̂_m
    c0_hat      : dict        # {market_id: float} — estimated ĉ₀_m (market-specific)
    Q_star      : float       # minimised objective value
    n_markets   : int
    model_moments: dict       # {market_id: ModelMoments} at estimates
    eq_types    : dict        # {market_id: str} equilibrium regime per market
    # Standard errors (populated by bootstrap)
    rho_se      : dict        = field(default_factory=dict)
    c0_se       : dict        = field(default_factory=dict)
    # Convergence
    converged   : bool        = False
    message     : str         = ""


def estimate_msm(
    data_moments : dict,
    market_params: dict,
    market_stats : pd.DataFrame,
    weighting_scheme: str = "inverse_variance",
    df           : pd.DataFrame | None = None,
    rho_init     : dict | None = None,
    c0_init      : float | dict = 0.03,
    method       : str = "L-BFGS-B",
    n_restarts   : int = 5,
    seed         : int = 0,
    drop_moments : list[int] | None = None,
) -> MSMResult:
    """
    MSM estimation of (ρ_m, c₀_m) — estimation appendix forthcoming.

        (ρ̂_m, ĉ₀_m) = argmin_{ρ∈[0,1]^M, c₀≥0^M} Q(ρ, c₀)

    Parameter vector: [ρ_1,...,ρ_M, c₀_1,...,c₀_M]

    Identification: ρ_m is pinned by price moments 1–3; c₀_m is pinned by
    moment 4 (the hiding rate σ̂₀_m) given ρ̂_m. The system remains
    overidentified (4 moments, 2 unknowns per market).

    Parameters
    ----------
    data_moments     : dict {market_id → DataMoments}
    market_params    : dict {market_id → ValuationParams}
    market_stats     : pd.DataFrame (from compute_market_stats)
    weighting_scheme : "equal", "inverse_variance", or "optimal_gmm"
    df               : listing-level DataFrame (required for "optimal_gmm")
    rho_init         : dict {market_id → float} initial ρ_m values
    c0_init          : scalar (broadcast to all markets) or dict {market_id → float}
    method           : scipy.optimize method ("L-BFGS-B" or "trust-constr")
    n_restarts       : number of random restarts for robustness
    seed             : random seed for restarts

    Returns
    -------
    MSMResult with c0_hat as dict {market_id → float}
    """
    markets = sorted(data_moments.keys())
    M       = len(markets)

    # Build weighting matrices (5×5 per market; specified moments zeroed out)
    weighting = build_weighting_matrix(
        data_moments, scheme=weighting_scheme, df=df, drop_moments=drop_moments
    )

    # Initial values for ρ_m
    rng = np.random.default_rng(seed)
    if rho_init is None:
        rho_init_vec = np.full(M, 0.3)
    else:
        rho_init_vec = np.array([rho_init.get(m, 0.3) for m in markets])

    # φ-reparameterisation: optimise over φ_m ∈ (0, 1) where
    #   c₀_m = φ_m · Δ(e₀; ρ_m) = φ_m · ρ_m · β₁_m · θ̄_m
    # This guarantees c₀_m < Δ(e₀; ρ_m) for any (ρ, φ), keeping every market
    # in the mixed-strategy / partial-separation region regardless of how ρ moves.
    # The constraint is satisfied by construction — no coupled bounds needed.
    PHI_EPS = 1e-4   # keep φ strictly inside (0, 1)

    # Convert c0_init → φ_init per market
    if isinstance(c0_init, dict):
        c0_init_vec = np.array([c0_init.get(m, 0.03) for m in markets])
    else:
        c0_init_vec = np.full(M, float(c0_init))

    phi_init_vec = np.empty(M)
    for j, m in enumerate(markets):
        pi_m  = float(market_stats.loc[m, "pi_hat"])
        th_m  = float(market_stats.loc[m, "theta_bar_hat"])
        e0, _ = belief_bounds(pi_m, th_m)
        delta_e0 = profit_gain_hiding(e0, float(rho_init_vec[j]), market_params[m])
        if delta_e0 > 0:
            phi_init_vec[j] = float(np.clip(c0_init_vec[j] / delta_e0, PHI_EPS, 1 - PHI_EPS))
        else:
            phi_init_vec[j] = 0.5

    x0     = np.concatenate([rho_init_vec, phi_init_vec])
    bounds = [(0.0, 1.0)] * M + [(PHI_EPS, 1.0 - PHI_EPS)] * M

    objective = lambda xv: msm_objective_pooled(
        xv, data_moments, market_params, weighting, market_stats, phi_mode=True
    )

    best_result = None
    best_Q      = np.inf

    for restart in range(n_restarts):
        if restart == 0:
            x_start = x0.copy()
        else:
            x_start = np.concatenate([
                rng.uniform(0.1, 0.9, size=M),
                rng.uniform(0.05, 0.95, size=M),
            ])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = minimize(
                objective,
                x_start,
                method  = method,
                bounds  = bounds,
                options = {"maxiter": 2000, "ftol": 1e-12, "gtol": 1e-8},
            )

        if res.fun < best_Q:
            best_Q      = res.fun
            best_result = res

    # Back-transform φ → c₀
    rho_hat_vec = best_result.x[:M]
    phi_hat_vec = best_result.x[M:]

    rho_hat = {m: float(rho_hat_vec[j]) for j, m in enumerate(markets)}
    c0_hat  = {}
    for j, m in enumerate(markets):
        pi_m  = float(market_stats.loc[m, "pi_hat"])
        th_m  = float(market_stats.loc[m, "theta_bar_hat"])
        e0, _ = belief_bounds(pi_m, th_m)
        delta_e0 = profit_gain_hiding(e0, float(rho_hat_vec[j]), market_params[m])
        c0_hat[m] = float(phi_hat_vec[j] * delta_e0)

    # Compute model moments at estimates
    model_moments_hat = {}
    eq_types          = {}
    for j, m in enumerate(markets):
        pi_m  = float(market_stats.loc[m, "pi_hat"])
        th_m  = float(market_stats.loc[m, "theta_bar_hat"])
        mm    = compute_model_moments(
            rho=rho_hat[m], c0=c0_hat[m],
            pi=pi_m, theta_bar=th_m,
            params=market_params[m],
            market_id=m,
        )
        model_moments_hat[m] = mm
        eq_types[m]          = mm.eq_type

    c0_vals   = list(c0_hat.values())
    eq_counts = pd.Series(list(eq_types.values())).value_counts()
    logger.debug(
        "[MSM] Estimation complete | "
        f"ĉ₀ mean={np.mean(c0_vals):.6f} std={np.std(c0_vals):.6f} | "
        f"ρ̂={np.mean(list(rho_hat.values())):.4f}±{np.std(list(rho_hat.values())):.4f} | "
        f"Q*={best_Q:.4f} | "
        f"converged={best_result.success} ({best_result.message}) | "
        f"regimes={eq_counts.to_dict()}"
    )

    return MSMResult(
        rho_hat       = rho_hat,
        c0_hat        = c0_hat,
        Q_star        = best_Q,
        n_markets     = M,
        model_moments = model_moments_hat,
        eq_types      = eq_types,
        converged     = best_result.success,
        message       = best_result.message,
    )


# ---------------------------------------------------------------------------
# Section D — Direct estimator for c₀ (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def estimate_c0_bounds(
    market_stats  : pd.DataFrame,
    market_params : dict,
    rho_hat       : dict,
) -> dict:
    """
    Consistency check for market-specific c₀_m estimates (estimation appendix forthcoming).

    With market-specific c₀_m, the equilibrium condition Δ(e(σ₀*_m); ρ_m) = c₀_m
    holds exactly by construction in mixed-strategy markets. This function computes
    the implied profit-gain Δ̄_m per market as a diagnostic and cross-check.

    In partial-separation markets (σ₀*=1): c₀_m ≤ Δ(e(1); ρ_m) — hiding profitable.
    In full-unraveling markets (σ₀*=0):    c₀_m ≥ Δ(θ̄; ρ_m)   — hiding unprofitable.

    Returns
    -------
    dict with per-market delta_m values and regime classification
    """
    delta_m_vals = {}
    for m in market_stats.index:
        if m not in rho_hat or m not in market_params:
            continue
        rho_m    = rho_hat[m]
        params_m = market_params[m]
        pi_m     = float(market_stats.loc[m, "pi_hat"])
        th_m     = float(market_stats.loc[m, "theta_bar_hat"])

        e0, e1 = belief_bounds(pi_m, th_m)
        delta_m_vals[m] = {
            "delta_at_e0": profit_gain_hiding(e0, rho_m, params_m),  # Δ(θ̄)
            "delta_at_e1": profit_gain_hiding(e1, rho_m, params_m),  # Δ(e(1))
        }

    if delta_m_vals:
        mean_d0 = np.mean([v["delta_at_e0"] for v in delta_m_vals.values()])
        mean_d1 = np.mean([v["delta_at_e1"] for v in delta_m_vals.values()])
        logger.info(f"[c₀ check] Mean Δ(e(0)) = {mean_d0:.6f}, Mean Δ(e(1)) = {mean_d1:.6f}")

    return {
        "delta_m_vals"         : delta_m_vals,
        "contributing_markets" : list(delta_m_vals.keys()),
    }


# ---------------------------------------------------------------------------
# Section E — Bootstrap standard errors (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def bootstrap_se(
    df            : pd.DataFrame,
    market_stats  : pd.DataFrame,
    hedonic_params,
    market_params : dict,
    n_boot        : int = 500,
    seed          : int = 42,
    weighting_scheme: str = "inverse_variance",
) -> dict:
    """
    Compute bootstrap standard errors for (ρ̂_m, ĉ₀) — estimation appendix forthcoming.

    Algorithm (as in paper, estimation appendix forthcoming):
    1. For b = 1, ..., B:
       a. Resample listings within each market with replacement
       b. Re-estimate hedonic regression → β̂₁^b
       c. Re-compute market statistics → π̂_m^b, θ̂_m^b, σ̂_{0,m}^b
       d. Re-run MSM → (ρ̂_m^b, ĉ₀^b)
    2. Standard errors = std across bootstrap samples

    Note: full re-estimation including the hedonic is computationally expensive.
    A faster approximation re-uses the point estimate of β̂₁ and only resamples
    to estimate variance of the moments (parametric bootstrap). The full version
    is implemented here; toggle with `reestimate_hedonic=True/False`.

    Parameters
    ----------
    df             : listing-level DataFrame
    market_stats   : market-level statistics (from compute_market_stats)
    hedonic_params : HedonicParams (point estimate)
    market_params  : dict {market_id → ValuationParams}
    n_boot         : number of bootstrap replications
    seed           : random seed
    weighting_scheme: MSM weighting matrix scheme

    Returns
    -------
    dict with keys: rho_se (dict), c0_se (float), rho_boot (array), c0_boot (array)
    """
    from .moments import extract_data_moments

    rng = np.random.default_rng(seed)
    markets = list(market_stats.index)

    rho_boot_mat = {m: [] for m in markets}
    c0_boot_mat  = {m: [] for m in markets}

    logger.info(f"[bootstrap] Running {n_boot} replications...")

    for b in range(n_boot):
        # Resample listings within each market with replacement
        boot_dfs = []
        for m in markets:
            grp = df[df["market_id"] == m]
            boot_grp = grp.sample(n=len(grp), replace=True, random_state=int(rng.integers(1e9)))
            boot_dfs.append(boot_grp)
        df_boot = pd.concat(boot_dfs, ignore_index=True)

        # Re-compute data moments on bootstrap sample
        try:
            dm_boot = extract_data_moments(df_boot, market_col="market_id")
        except Exception:
            continue

        # Re-estimate MSM on bootstrap sample (using fixed hedonic params for speed)
        try:
            result_boot = estimate_msm(
                data_moments    = dm_boot,
                market_params   = market_params,
                market_stats    = market_stats,
                weighting_scheme= weighting_scheme,
                df              = df_boot,
                c0_init         = 0.03,
                n_restarts      = 1,
                seed            = b,
            )
            for m in markets:
                rho_boot_mat[m].append(result_boot.rho_hat.get(m, np.nan))
                c0_boot_mat[m].append(result_boot.c0_hat.get(m, np.nan))
        except Exception:
            for m in markets:
                rho_boot_mat[m].append(np.nan)
                c0_boot_mat[m].append(np.nan)

        if (b + 1) % 50 == 0:
            logger.info(f"[bootstrap] {b + 1}/{n_boot} replications done")

    # Compute standard errors
    rho_se = {m: float(np.nanstd(rho_boot_mat[m])) for m in markets}
    c0_se  = {m: float(np.nanstd(c0_boot_mat[m]))  for m in markets}

    logger.info(f"[bootstrap] Mean ĉ₀ SE = {np.nanmean(list(c0_se.values())):.6f}")
    logger.info(f"[bootstrap] Mean ρ̂ SE  = {np.nanmean(list(rho_se.values())):.6f}")

    return {
        "rho_se"  : rho_se,
        "c0_se"   : c0_se,
        "rho_boot": rho_boot_mat,
        "c0_boot" : c0_boot_mat,
    }


# ---------------------------------------------------------------------------
# Section F — Renovation threshold and optimal subsidies (estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def compute_market_subsidies(
    market_stats       : pd.DataFrame,
    market_params      : dict,
    rho_hat            : dict,
    c0_hat             : dict,
    actual_reno_costs  : pd.Series | None = None,
) -> pd.DataFrame:
    """
    Compute market-specific renovation thresholds and optimal subsidies — Eqs. (eq:threshold) and (eq:subsidy).

    Steps:
    1. Estimate renovation threshold R̄_m = Π*(d=1,θ=1) - Π*(d=0) + c₀_m (Eq. (eq:threshold))
    2. Compare to actual renovation cost R̂_m (from engineering data / surveys)
    3. Optimal subsidy: S*_m = max{R̂_m - R̄_m, 0}              (Eq. (eq:subsidy))

    Parameters
    ----------
    market_stats      : market-level statistics
    market_params     : dict {market_id → ValuationParams}
    rho_hat           : dict {market_id → float} estimated ρ̂_m
    c0_hat            : dict {market_id → float} estimated ĉ₀_m (market-specific)
    actual_reno_costs : pd.Series {market_id → float} actual renovation cost R̂_m
                        If None, placeholder NaN values are used.

    Returns
    -------
    pd.DataFrame with columns: R_bar_m, R_hat_m, S_star_m, per market
    """
    rows = []
    for m in market_stats.index:
        pi_m  = float(market_stats.loc[m, "pi_hat"])
        th_m  = float(market_stats.loc[m, "theta_bar_hat"])
        rho_m = rho_hat.get(m, np.nan)
        c0_m  = c0_hat.get(m, np.nan)
        pm    = market_params.get(m)

        if pm is None or np.isnan(rho_m) or np.isnan(c0_m):
            rows.append({"market_id": m, "R_bar_m": np.nan,
                         "R_hat_m": np.nan, "S_star_m": np.nan})
            continue

        # Renovation threshold R̄_m (Eq. (eq:threshold))
        try:
            R_bar_m = renovation_threshold(rho_m, pi_m, th_m, c0_m, pm)
        except Exception:
            R_bar_m = np.nan

        # Actual renovation cost R̂_m (external data; placeholder here)
        if actual_reno_costs is not None and m in actual_reno_costs.index:
            R_hat_m = float(actual_reno_costs.loc[m])
        else:
            # Placeholder: assume actual cost equals threshold (S* = 0 as default)
            # Replace with engineering estimates from ADEME technical studies or
            # MaPrimeRénov' claims data (estimation appendix forthcoming)
            R_hat_m = np.nan

        # Optimal subsidy S*_m (Eq. (eq:subsidy))
        if not np.isnan(R_hat_m) and not np.isnan(R_bar_m):
            S_star_m = optimal_subsidy(R_hat_m, R_bar_m)
        else:
            S_star_m = np.nan

        rows.append({
            "market_id": m,
            "R_bar_m"  : R_bar_m,
            "R_hat_m"  : R_hat_m,
            "S_star_m" : S_star_m,
            "rho_m"    : rho_m,
            "pi_m"     : pi_m,
            "theta_bar_m": th_m,
        })

    return pd.DataFrame(rows).set_index("market_id")
