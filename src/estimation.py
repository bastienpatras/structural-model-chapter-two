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
from typing import Callable, Sequence
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
    fix_rho      : bool = False,
) -> MSMResult:
    """
    MSM estimation of (ρ_m, c₀_m).

    Two modes, selected by ``fix_rho``:

    fix_rho=False (robustness / joint mode):
        Jointly optimises over [ρ_1,...,ρ_M, φ_1,...,φ_M]. Use only when
        multiple moments are active; with a single active moment the system
        is under-identified and estimates depend on the warm-start.

    fix_rho=True  (two-step mode, primary estimator):
        Fixes ρ̂_m from ``rho_init`` (the DiD first stage) and analytically
        inverts the equilibrium indifference condition for c₀_m:

            ĉ₀_m = ρ̂_m · β₁_m · e(σ̂₀_m)   [eq:pp_sigma inverted]

        No optimisation is performed. The system is exactly identified:
        one free parameter (c₀_m), one moment (σ̂₀_m).

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

    # -------------------------------------------------------------------------
    # Two-step mode: fix ρ̂_m from rho_init, invert eq:pp_sigma analytically
    # -------------------------------------------------------------------------
    if fix_rho:
        if rho_init is None:
            raise ValueError("fix_rho=True requires rho_init to be provided.")

        rho_hat: dict = {}
        c0_hat:  dict = {}
        for m in markets:
            pi_m    = float(market_stats.loc[m, "pi_hat"])
            th_m    = float(market_stats.loc[m, "theta_bar_hat"])
            sig_m   = float(market_stats.loc[m, "sigma_0_hat"])
            rho_m   = float(rho_init.get(m, np.nan))
            beta1_m = market_params[m].beta_1
            e_star  = belief_function(sig_m, pi_m, th_m)
            rho_hat[m] = rho_m
            c0_hat[m]  = float(np.clip(rho_m * beta1_m * e_star, 0.0, None))

        model_moments_hat: dict = {}
        eq_types:          dict = {}
        for m in markets:
            pi_m = float(market_stats.loc[m, "pi_hat"])
            th_m = float(market_stats.loc[m, "theta_bar_hat"])
            mm   = compute_model_moments(
                rho=rho_hat[m], c0=c0_hat[m],
                pi=pi_m, theta_bar=th_m,
                params=market_params[m],
                market_id=m,
            )
            model_moments_hat[m] = mm
            eq_types[m]          = mm.eq_type

        logger.info(
            f"[MSM two-step] ĉ₀ mean={np.nanmean(list(c0_hat.values())):.6f} "
            f"std={np.nanstd(list(c0_hat.values())):.6f} | "
            f"ρ̂ mean={np.nanmean(list(rho_hat.values())):.4f} (fixed from DiD)"
        )
        return MSMResult(
            rho_hat        = rho_hat,
            c0_hat         = c0_hat,
            Q_star         = 0.0,
            n_markets      = M,
            model_moments  = model_moments_hat,
            eq_types       = eq_types,
            converged      = True,
            message        = "two-step closed-form inversion (fix_rho=True)",
        )

    # -------------------------------------------------------------------------
    # Joint optimisation mode (robustness / fix_rho=False)
    # -------------------------------------------------------------------------

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
    rho_hat_fixed : dict | None = None,
) -> dict:
    """
    Compute bootstrap standard errors for (ρ̂_m, ĉ₀).

    Two modes depending on whether ``rho_hat_fixed`` is provided:

    Two-step mode (rho_hat_fixed is not None):
        ρ_m is held fixed at the point estimate in each bootstrap draw.
        Only σ̂_{0,m} is resampled, propagating its uncertainty to ĉ₀_m via
        the closed-form inversion ĉ₀_m = ρ̂_m · β₁_m · e(σ̂_{0,m}^b).
        Bootstrap SEs for ρ̂_m from the DiD first stage must be computed
        separately (e.g., by bootstrapping compute_did()).

    Joint mode (rho_hat_fixed is None):
        Re-runs the full joint MSM in each bootstrap draw. Requires multiple
        active moments to be identified; otherwise SEs reflect warm-start
        sensitivity rather than genuine sampling uncertainty.

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

        try:
            if rho_hat_fixed is not None:
                # Two-step bootstrap: fix ρ̂_m at point estimate, only resample σ̂₀_m
                # ĉ₀_m^b = ρ̂_m · β₁_m · e(σ̂_{0,m}^b)
                result_boot = estimate_msm(
                    data_moments    = dm_boot,
                    market_params   = market_params,
                    market_stats    = market_stats,
                    weighting_scheme= weighting_scheme,
                    df              = df_boot,
                    rho_init        = rho_hat_fixed,
                    c0_init         = 0.03,
                    n_restarts      = 1,
                    seed            = b,
                    fix_rho         = True,
                )
            else:
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

def _compute_threshold_row(
    m              : str | int,
    market_stats   : pd.DataFrame,
    market_params  : dict,
    rho_hat        : dict,
    c0_hat         : dict,
) -> dict | None:
    """
    Solve the equilibrium once for market m and return the renovation threshold
    and the calibrated parameters used to compute it. Returns None if any input
    is missing or the equilibrium solver fails.

    Shared by `compute_market_subsidies` (single R̂) and `compute_subsidy_grid`
    (R̂ grid) — guarantees the threshold is identical in both code paths and
    avoids re-solving the equilibrium per grid value.
    """
    pi_m  = float(market_stats.loc[m, "pi_hat"])
    th_m  = float(market_stats.loc[m, "theta_bar_hat"])
    rho_m = rho_hat.get(m, np.nan)
    c0_m  = c0_hat.get(m, np.nan)
    pm    = market_params.get(m)

    if pm is None or np.isnan(rho_m) or np.isnan(c0_m):
        return None

    try:
        eq      = solve_equilibrium(rho_m, c0_m, pi_m, th_m, pm)
        R_bar_m = renovation_threshold(rho_m, pi_m, th_m, c0_m, pm)
    except Exception as exc:
        logger.warning(f"_compute_threshold_row({m}): equilibrium failed ({exc})")
        return None

    return {
        "market_id"   : m,
        "R_bar_m"     : float(R_bar_m),
        "regime"      : eq.eq_type,
        "sigma_0_m"   : float(eq.sigma_0_star),
        "e_star_m"    : float(eq.e_star),
        "rho_m"       : float(rho_m),
        "c0_m"        : float(c0_m),
        "pi_m"        : pi_m,
        "theta_bar_m" : th_m,
        "beta_1_m"    : float(pm.beta_1),
    }


def compute_market_subsidies(
    market_stats       : pd.DataFrame,
    market_params      : dict,
    rho_hat            : dict,
    c0_hat             : dict,
    actual_reno_costs  : pd.Series | None = None,
) -> pd.DataFrame:
    """
    Compute market-specific renovation thresholds and optimal subsidies for a
    single value of R̂ per market — Eqs. (eq:threshold) and (eq:subsidy).

    For sensitivity over a grid of R̂ values, use `compute_subsidy_grid` instead.

    Steps:
    1. Renovation threshold R̄_m = Π*(d=1,θ=1) - Π*(d=0) + c₀_m  (eq:threshold)
    2. Subsidy S*_m = max{R̂_m - R̄_m, 0}                         (eq:subsidy)

    Parameters
    ----------
    market_stats      : market-level statistics
    market_params     : dict {market_id → ValuationParams}
    rho_hat           : dict {market_id → float} estimated ρ̂_m
    c0_hat            : dict {market_id → float} estimated ĉ₀_m
    actual_reno_costs : pd.Series {market_id → float}; NaN if missing.
    """
    rows = []
    for m in market_stats.index:
        base = _compute_threshold_row(m, market_stats, market_params, rho_hat, c0_hat)
        if base is None:
            rows.append({"market_id": m, "R_bar_m": np.nan,
                         "R_hat_m": np.nan, "S_star_m": np.nan})
            continue

        if actual_reno_costs is not None and m in actual_reno_costs.index:
            R_hat_m = float(actual_reno_costs.loc[m])
        else:
            R_hat_m = np.nan

        if not np.isnan(R_hat_m):
            S_star_m = optimal_subsidy(R_hat_m, base["R_bar_m"])
        else:
            S_star_m = np.nan

        rows.append({**base, "R_hat_m": R_hat_m, "S_star_m": S_star_m})

    return pd.DataFrame(rows).set_index("market_id")


def compute_subsidy_grid(
    market_stats     : pd.DataFrame,
    market_params    : dict,
    rho_hat          : dict,
    c0_hat           : dict,
    cost_per_m2_grid : Sequence[float],
    market_levels    : pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute the renovation threshold R̄_m and the minimum incentive-compatible
    subsidy S*_m(c) = max{c - R̄_m^{€/m²}, 0} for each market and each cost
    scheme c (€/m²) in `cost_per_m2_grid` — Eqs. (eq:threshold), (eq:subsidy),
    Lemma `lem:threshold_regimes`.

    The structural model is in log-price units; this function translates a
    nominal renovation-cost grid (€/m²) into the model's scale market-by-market
    using each market's listing price per m² (from `market_levels`). Since the
    listings parquet uses `log_price = log(price / area)`, the price per m² is
    `exp(median log_price)` per market.

    Conversion identity (per market m, per cost scheme c):
        r_hat_log_pts   = c / price_per_m2_m                  (dimensionless)
        S_star_log_pts  = max(r_hat_log_pts - R̄_m, 0)
        S_star_eur_m2   = S_star_log_pts × price_per_m2_m     (€/m²)
        S_star_eur_unit = S_star_eur_m2  × median_area_m2_m   (€ per dwelling)

    Parameters
    ----------
    market_levels : pd.DataFrame indexed by market_id, with columns
                    `price_per_m2_eur`, `median_area_m2`, `n_listings`
                    (output of `data_prep.compute_market_levels`).

    Returns
    -------
    Long-format pd.DataFrame, one row per (market_id, cost_per_m2). Columns:
        market_id, cost_per_m2, r_hat_log_pts,
        R_bar_log_pts, R_bar_eur_per_m2,
        S_star_log_pts, S_star_eur_per_m2, S_star_eur_per_unit,
        price_per_m2_eur, median_area_m2, n_listings,
        regime, rho_m, c0_m, pi_m, theta_bar_m,
        sigma_0_m, e_star_m, beta_1_m
    """
    base_rows = []
    for m in market_stats.index:
        base = _compute_threshold_row(m, market_stats, market_params, rho_hat, c0_hat)
        if base is None or m not in market_levels.index:
            continue
        lvl = market_levels.loc[m]
        base["price_per_m2_eur"] = float(lvl["price_per_m2_eur"])
        base["median_area_m2"]   = float(lvl["median_area_m2"])
        base["n_listings"]       = int(lvl["n_listings"])
        base["R_bar_log_pts"]    = base.pop("R_bar_m")
        base["R_bar_eur_per_m2"] = base["R_bar_log_pts"] * base["price_per_m2_eur"]
        base_rows.append(base)

    cols = [
        "market_id", "cost_per_m2", "r_hat_log_pts",
        "R_bar_log_pts", "R_bar_eur_per_m2",
        "S_star_log_pts", "S_star_eur_per_m2", "S_star_eur_per_unit",
        "price_per_m2_eur", "median_area_m2", "n_listings",
        "regime", "rho_m", "c0_m", "pi_m", "theta_bar_m",
        "sigma_0_m", "e_star_m", "beta_1_m",
    ]
    if not base_rows:
        return pd.DataFrame(columns=cols)

    base_df = pd.DataFrame(base_rows)
    grid    = pd.DataFrame({"cost_per_m2": [float(c) for c in cost_per_m2_grid]})
    out     = base_df.merge(grid, how="cross")
    out["r_hat_log_pts"]       = out["cost_per_m2"] / out["price_per_m2_eur"]
    out["S_star_log_pts"]      = (out["r_hat_log_pts"] - out["R_bar_log_pts"]).clip(lower=0.0)
    out["S_star_eur_per_m2"]   = out["S_star_log_pts"]   * out["price_per_m2_eur"]
    out["S_star_eur_per_unit"] = out["S_star_eur_per_m2"] * out["median_area_m2"]
    return out[cols].reset_index(drop=True)


def aggregate_subsidy_summary(grid_df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-cost-scheme summary statistics over markets. Returns a long-format
    DataFrame with columns:
        cost_per_m2, regime, N_total, N_positive, share_positive,
        mean_S_per_m2_positive, median_S_per_m2, p75_S_per_m2,
        mean_S_per_unit_positive, median_S_per_unit
    `regime == "all"` aggregates across regimes; the others give the per-regime
    breakdown. Conditional means use only markets with S* > 0 to avoid the
    zero-mass at the kink.
    """
    cols = [
        "cost_per_m2", "regime", "N_total", "N_positive", "share_positive",
        "mean_S_per_m2_positive", "median_S_per_m2", "p75_S_per_m2",
        "mean_S_per_unit_positive", "median_S_per_unit",
    ]
    if grid_df.empty:
        return pd.DataFrame(columns=cols)

    def _stats(group):
        s_m2   = group["S_star_eur_per_m2"].dropna()
        s_unit = group["S_star_eur_per_unit"].dropna()
        pos_m2   = s_m2[s_m2 > 0]
        pos_unit = s_unit[s_unit > 0]
        n = len(s_m2)
        return pd.Series({
            "N_total"                  : int(n),
            "N_positive"               : int((s_m2 > 0).sum()),
            "share_positive"           : float((s_m2 > 0).mean()) if n else np.nan,
            "mean_S_per_m2_positive"   : float(pos_m2.mean())   if len(pos_m2)   else 0.0,
            "median_S_per_m2"          : float(s_m2.median())   if n             else np.nan,
            "p75_S_per_m2"             : float(s_m2.quantile(0.75)) if n         else np.nan,
            "mean_S_per_unit_positive" : float(pos_unit.mean()) if len(pos_unit) else 0.0,
            "median_S_per_unit"        : float(s_unit.median()) if n             else np.nan,
        })

    overall = (
        grid_df.groupby("cost_per_m2", group_keys=False)
        .apply(_stats, include_groups=False)
        .reset_index()
    )
    overall.insert(1, "regime", "all")

    by_regime = (
        grid_df.groupby(["cost_per_m2", "regime"], group_keys=False)
        .apply(_stats, include_groups=False)
        .reset_index()
    )

    return pd.concat([overall, by_regime], ignore_index=True)[cols]


def aggregate_budget(
    grid_df : pd.DataFrame,
    weights : pd.Series,
) -> pd.DataFrame:
    """
    Total fiscal cost of the subsidy programme at each cost scheme:
        B(c) = Σ_m w_m · S*_m^{€/unit}(c)
    where the weight `w_m` is the number of dwellings the regulator would
    subsidise per market (defaults to listings count). One row per `cost_per_m2`.
    """
    cols = ["cost_per_m2", "total_subsidy_eur", "weight_sum",
            "mean_subsidy_per_unit_eur"]
    if grid_df.empty:
        return pd.DataFrame(columns=cols)

    w = weights.reindex(grid_df["market_id"]).fillna(0.0).to_numpy()
    work = grid_df.copy()
    work["weighted_S"] = work["S_star_eur_per_unit"].to_numpy() * w

    out = (
        work.groupby("cost_per_m2", group_keys=False)
        .agg(total_subsidy_eur=("weighted_S", "sum"))
        .reset_index()
    )
    weight_total = float(weights.sum())
    out["weight_sum"]                = weight_total
    out["mean_subsidy_per_unit_eur"] = np.where(
        weight_total > 0,
        out["total_subsidy_eur"] / weight_total,
        np.nan,
    )
    return out[cols]
