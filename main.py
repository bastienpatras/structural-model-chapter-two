from __future__ import annotations
"""
main.py
=======
Structural Estimation Pipeline
--------------------------------
Replication entry point for:

  Patras, B. (2024). "Mandatory Disclosure and Housing Market Dynamics."

This script orchestrates the five-step estimation workflow:
  1. Data preparation
  2. Hedonic regression and market statistics
  3. MSM estimation of (ρ_m, c₀)
  4. Validation and robustness
  5. Tables and figures

Usage
-----
  # With real data (supply paths in CONFIG below):
  python main.py

  # With synthetic data (for pipeline testing):
  python main.py --synthetic

  # Skip bootstrap (faster run):
  python main.py --synthetic --no-bootstrap

Configuration
-------------
  Edit the CONFIG dict below to point to actual data files.
  All other settings (weighting scheme, n_boot, etc.) are also set there.

Output
------
  results/tables/  — LaTeX tables
  results/figures/ — PDF figures

Dependencies
------------
  numpy, pandas, scipy, statsmodels, matplotlib
  Install: pip install -r requirements.txt
"""

import argparse
import logging
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with timestamp, level, and module name."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )

# ── Project modules ──────────────────────────────────────────────────────────
from src.data_prep   import (load_listings, load_ademe, merge_datasets,
                              classify_listings, compute_market_stats,
                              make_synthetic_data)
from src.hedonic     import (estimate_hedonic, compute_hiding_premium,
                              estimate_rho_direct, calibrate_demand_scale,
                              calibrate_demand_scale_m)
from src.moments     import extract_data_moments, moment_summary_table
from src.estimation  import (build_valuation_params, estimate_msm,
                              estimate_c0_bounds, compute_market_subsidies,
                              bootstrap_se)
from src.event_study import load_price_indices, compute_did, estimate_rho_c0
from src.validation  import run_all_validation
from src.outputs     import produce_all_outputs


# ---------------------------------------------------------------------------
# CONFIG — edit this section to point to actual data files
# ---------------------------------------------------------------------------

CONFIG = {
    # ── Data paths ──────────────────────────────────────────────────────────
    "listings_path"     : "data/listings_APARTMENT.parquet",      # listing-level data
    "ademe_path"        : "data/ademe_registry.parquet",          # ADEME audit registry
    # GCS path to the urban-area cluster pickle used to enrich listings with
    # cateaav2020_label (urbanicity) and distance controls.  Set to None to skip.
    "clusters_path"     : "These/Bastien/DIFFINDISC/geo-culsters.plk",

    # ── DiD event study (price index panel) ─────────────────────────────────
    # Hedonic price indices by EPC category × market × month.
    # Set to None to skip the DiD stage (falls back to hedonic direct estimator).
    "index_apartment_path" : "data/index_APARTMENT.csv",
    "index_house_path"     : "data/index_HOUSE.csv",   # set to None until house indices ready
    "did_min_volume"       : 20,   # minimum avg monthly transactions per EPC cell

    # ── Property controls to include in hedonic regression ──────────────────
    # These must be column names in the listings DataFrame.
    # built_year       : construction period bins (e.g. '1946_1974') → auto-dummified
    # cateaav2020_label: urban-area classification (categorical → auto-dummified)
    # distance         : distance to urban centre in km (continuous)
    "controls"          : ["size_m2", "built_year", "cateaav2020_label", "distance"],

    # ── EPC binarisation threshold ──────────────────────────────────────────
    # θ = 1 (high quality) if epc_score ≤ threshold.
    # Assumption: EPC letters encoded as integers A=1, B=2, ..., G=7.
    # Set threshold=3 → θ=1 for A/B/C (classes meeting minimum performance).
    "epc_threshold"     : 3.0,

    # ── MSM settings ────────────────────────────────────────────────────────
    "weighting_scheme"  : "optimal_gmm",         # "equal", "inverse_variance", or "optimal_gmm"
    "n_restarts"        : 5,                    # MSM restarts (robustness to local minima)
    "c0_init"           : 0.005,                # initial value for c₀ (hiding cost, in euros at mean price)

    # ── Bootstrap settings ───────────────────────────────────────────────────
    "n_boot"            : 500,                  # bootstrap replications (set to 0 to skip)

    # ── Renovation cost data (optional) ─────────────────────────────────────
    # If available, supply market-level average renovation costs (in log-price units).
    # Used to compute optimal subsidies S*_m (Sec. 7.6).
    # Example: actual_reno_costs = pd.read_csv("data/reno_costs.csv").set_index("market_id")["cost"]
    "actual_reno_costs" : None,

    # ── Synthetic data settings (for testing) ────────────────────────────────
    "synthetic_n"       : 100_000,
    "synthetic_markets" : 20,
    "synthetic_pi"      : 0.60,
    "synthetic_theta_bar": 0.40,
    "synthetic_rho"     : 0.35,
    "synthetic_c0"      : 0.03,
    "synthetic_beta_1"  : 0.2,
    "synthetic_seed"    : 42,
    # Target equilibrium regime: 1.0 = pooling, 0.7 = mixed strategy, 0.0 = full unraveling
    "synthetic_sigma_0_target": 0.7,
}


# ---------------------------------------------------------------------------
# Parameter summary
# ---------------------------------------------------------------------------

def log_config_summary(use_synthetic: bool) -> None:
    """Log all configuration parameters before estimation begins."""
    logger.info("─" * 70)
    logger.info("CONFIGURATION PARAMETERS")
    logger.info("─" * 70)

    logger.info("── Hedonic regression ──────────────────────────────────────────────")
    logger.info(f"  controls        : {CONFIG['controls']}")
    logger.info(f"  epc_threshold   : {CONFIG['epc_threshold']}  "
                f"(θ=1 if EPC letter ≤ {CONFIG['epc_threshold']}; A=1…G=7)")

    logger.info("── MSM estimation ──────────────────────────────────────────────────")
    logger.info(f"  weighting_scheme: {CONFIG['weighting_scheme']!r}")
    logger.info(f"  c0_init         : {CONFIG['c0_init']}  (initial hiding cost)")
    logger.info(f"  n_restarts      : {CONFIG['n_restarts']}  (optimiser random restarts)")
    logger.info(f"  n_boot          : {CONFIG['n_boot']}  (bootstrap replications; 0 = skip)")

    if use_synthetic:
        sigma_tgt = CONFIG["synthetic_sigma_0_target"]
        regime = ("mixed strategy" if 0 < sigma_tgt < 1
                  else "full unraveling" if sigma_tgt <= 0
                  else "pooling / partial separation")
        logger.info("── Synthetic DGP ───────────────────────────────────────────────────")
        logger.info(f"  n_listings      : {CONFIG['synthetic_n']}")
        logger.info(f"  n_markets       : {CONFIG['synthetic_markets']}")
        logger.info(f"  π  (informed share)  : {CONFIG['synthetic_pi']}")
        logger.info(f"  θ̄  (quality share)   : {CONFIG['synthetic_theta_bar']}")
        logger.info(f"  ρ  (sensitive buyers): {CONFIG['synthetic_rho']}  ← target to recover")
        logger.info(f"  β₁ (quality premium) : {CONFIG['synthetic_beta_1']}  ← target to recover")
        logger.info(f"  σ₀* target           : {sigma_tgt}  → {regime}")
        logger.info(f"  c₀  (hiding cost)    : endogenous — set from equilibrium condition Δ(e(σ₀*))=c₀")
        logger.info(f"  seed                 : {CONFIG['synthetic_seed']}")
    else:
        logger.info("── Data paths ──────────────────────────────────────────────────────")
        logger.info(f"  listings_path   : {CONFIG['listings_path']}")
        logger.info(f"  ademe_path      : {CONFIG['ademe_path']}")

    logger.info("─" * 70)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(use_synthetic: bool = False, run_bootstrap: bool = True) -> dict:
    """
    Full estimation pipeline. Returns a dict of all output objects.

    Parameters
    ----------
    use_synthetic : if True, generate synthetic data and run the full pipeline.
                    Useful to verify the estimator recovers true parameters.
    run_bootstrap : if True, compute bootstrap standard errors.
                    Set to False for quick testing (estimates only).
    """
    logger.info("=" * 70)
    logger.info("MANDATORY DISCLOSURE AND HOUSING MARKET DYNAMICS")
    logger.info("Structural Estimation — Patras (2024)")
    logger.info("=" * 70)

    log_config_summary(use_synthetic)

    # =========================================================================
    # PART 1: Data Preparation
    # =========================================================================
    logger.info("─" * 50)
    logger.info("PART 1: Data Preparation")
    logger.info("─" * 50)

    true_params = None

    controls = CONFIG["controls"]

    if use_synthetic:
        logger.info("[synthetic] Generating synthetic data from model DGP...")
        df, market_stats, true_params = make_synthetic_data(
            n_listings      = CONFIG["synthetic_n"],
            n_markets       = CONFIG["synthetic_markets"],
            pi              = CONFIG["synthetic_pi"],
            theta_bar       = CONFIG["synthetic_theta_bar"],
            rho_true        = CONFIG["synthetic_rho"],
            beta_1          = CONFIG["synthetic_beta_1"],
            seed            = CONFIG["synthetic_seed"],
            target_sigma_0  = CONFIG.get("synthetic_sigma_0_target", 0.7),
            controls        = controls,
        )
        logger.info(f"[synthetic] {len(df)} listings, {len(market_stats)} markets")
        logger.info(f"[synthetic] True parameters: {true_params}")

    else:
        # Load and prepare real data
        listings = load_listings(CONFIG["listings_path"])
        ademe    = load_ademe(CONFIG["ademe_path"])
        df       = merge_datasets(listings, ademe)
        df       = classify_listings(df)
        market_stats = compute_market_stats(df, controls=controls)

    logger.info("[data] Group distribution:\n" + df["group"].value_counts().to_string())
    logger.info(f"[data] Estimable markets: "
                f"{market_stats['estimable'].sum()} / {len(market_stats)}")

    # Restrict to estimable markets
    market_stats = market_stats[market_stats["estimable"]].copy()
    df_est = df[df["market_id"].isin(market_stats.index)].copy()

    # =========================================================================
    # PART 2: Hedonic Regression and Market Statistics
    # =========================================================================
    logger.info("─" * 50)
    logger.info("PART 2: Hedonic Regression")
    logger.info("─" * 50)

    # Step 2a: Hedonic regression on truthful disclosers (Eq. 110)
    hedonic_params = estimate_hedonic(df_est, controls=controls)

    # Step 2b: Calibrate logistic demand scale from residual variance (pooled + per-market)
    scale   = calibrate_demand_scale(hedonic_params)
    scale_m = calibrate_demand_scale_m(hedonic_params)

    # Step 2c: Compute hiding premiums for strategic hiders (Eqs. 112–113)
    df_hiders, market_premium = compute_hiding_premium(df_est, hedonic_params)

    # Step 2d: Direct estimator for ρ_m (Eq. 116)
    rho_direct_df = estimate_rho_direct(market_stats, market_premium, hedonic_params)

    logger.info(f"[hedonic] β̂₁ = {hedonic_params.beta_1:.4f}  "
               f"(EPC quality premium, benchmark α_k = β_k)")

    # =========================================================================
    # PART 2b: DiD Event Study — Primary Identification of ρ_m and c₀_m
    # =========================================================================
    # Strategy: DiD around July 2021 DPE reform.
    #   Pre-reform (≤ 2021-06): ρ_m ≈ 0 (DPE not legally opposable).
    #   Post-reform (≥ 2021-07): ρ_m > 0, market-specific.
    #
    #   β̂₁_m = DiD[(ABC − EFG) log price gap]    — EPC quality premium
    #   Δ̂_m  = DiD[(Ø − EFG) log price gap]      — non-disclosure premium
    #   ρ̂_m  = Δ̂_m / (β̂₁_m · ê*_m)             — Eq. (eq:premium) adapted
    #   ĉ₀_m = Δ̂_m                              — equilibrium indifference
    # =========================================================================
    logger.info("─" * 50)
    logger.info("PART 2b: DiD Event Study Identification")
    logger.info("─" * 50)

    did_params   = None   # EventStudyParams (ρ̂_m, ĉ₀_m from DiD)
    did_estimates = None  # DiDEstimates (β̂₁_m, Δ̂_m per market)

    index_path = CONFIG.get("index_apartment_path") if not use_synthetic else None
    if index_path and Path(index_path).exists():
        logger.info(f"[DiD] Loading price indices from {index_path}")
        index_df      = load_price_indices(index_path)
        did_estimates = compute_did(index_df, min_volume=CONFIG["did_min_volume"])
        did_params    = estimate_rho_c0(did_estimates, market_stats)

        logger.info(
            f"[DiD] ρ̂_m : mean={did_params.rho_m.mean():.3f}  "
            f"std={did_params.rho_m.std():.3f}  "
            f"[{did_params.rho_m.min():.3f}, {did_params.rho_m.max():.3f}]"
        )
        logger.info(
            f"[DiD] ĉ₀_m: mean={did_params.c0_m.mean():.4f}  "
            f"std={did_params.c0_m.std():.4f}"
        )
    else:
        if not use_synthetic:
            logger.warning(
                f"[DiD] Price index file not found ({index_path}). "
                "Skipping DiD stage — MSM will use hedonic direct estimator as starting values."
            )

    # =========================================================================
    # PART 3: Moments and MSM Estimation (second stage / overidentification)
    # =========================================================================
    # With DiD estimates available: MSM uses ρ̂_m and ĉ₀_m from the DiD as
    # starting values and serves as an overidentification check + counterfactual
    # engine (subsidies, renovation thresholds).
    # Without DiD: MSM is the primary estimator (fallback).
    # =========================================================================
    logger.info("─" * 50)
    logger.info("PART 3: Method of Simulated Moments (second stage)")
    logger.info("─" * 50)

    # Step 3a: Extract data moments
    data_moments = extract_data_moments(df_est)

    # Restrict to markets present in all data sources
    estimable_markets = set(market_stats.index) & set(data_moments.keys())
    data_moments      = {m: data_moments[m] for m in estimable_markets}
    market_stats      = market_stats.loc[list(estimable_markets)]

    # Step 3b: Build ValuationParams per market from hedonic estimates
    market_params = {
        m: build_valuation_params(
            m, market_stats, hedonic_params, scale=scale, scale_m=scale_m
        )
        for m in estimable_markets
    }

    # Step 3c: Starting values — DiD estimates preferred; fall back to hedonic direct estimator
    rho_init = {}
    c0_init_dict = {}
    for m in estimable_markets:
        # ρ̂_m starting value
        if did_params is not None and m in did_params.rho_m.index and not np.isnan(did_params.rho_m[m]):
            rho_init[m] = float(did_params.rho_m[m])
        elif m in rho_direct_df.index and not np.isnan(rho_direct_df.loc[m, "rho_hat_clipped"]):
            rho_init[m] = float(rho_direct_df.loc[m, "rho_hat_clipped"])
        else:
            rho_init[m] = 0.3

        # ĉ₀_m starting value
        if did_params is not None and m in did_params.c0_m.index and not np.isnan(did_params.c0_m[m]):
            c0_init_dict[m] = float(did_params.c0_m[m])
        else:
            c0_init_dict[m] = CONFIG["c0_init"]

    logger.info(
        f"[MSM] Starting values: "
        f"{'DiD' if did_params is not None else 'hedonic direct estimator'} → "
        f"ρ̄_init={np.mean(list(rho_init.values())):.3f}  "
        f"ĉ₀_init={np.mean(list(c0_init_dict.values())):.4f}"
    )

    # Step 3d: MSM estimation
    msm_result = estimate_msm(
        data_moments     = data_moments,
        market_params    = market_params,
        market_stats     = market_stats,
        weighting_scheme = CONFIG["weighting_scheme"],
        df               = df_est,
        rho_init         = rho_init,
        c0_init          = c0_init_dict,
        n_restarts       = CONFIG["n_restarts"],
    )

    # Step 3e: Direct estimator for c₀ bounds (Eq. 129)
    c0_bounds = estimate_c0_bounds(market_stats, market_params, msm_result.rho_hat)

    c0_vals = list(msm_result.c0_hat.values())
    logger.info("[MSM summary]")
    logger.info(f"  ĉ₀ mean={np.mean(c0_vals):.6f}  "
                f"std={np.std(c0_vals):.6f}  "
                f"[{min(c0_vals):.6f}, {max(c0_vals):.6f}]")
    if true_params:
        c0_err = {m: abs(v - true_params["c0"]) for m, v in msm_result.c0_hat.items()}
        logger.info(f"  c₀ (true)   = {true_params['c0']:.6f}  "
                    f"mean |error| = {np.mean(list(c0_err.values())):.6f}")
        rho_err = {
            m: abs(msm_result.rho_hat[m] - true_params["rho"])
            for m in msm_result.rho_hat
        }
        logger.info(f"  ρ  (true)   = {true_params['rho']:.4f}, "
                    f"mean |error| = {np.mean(list(rho_err.values())):.4f}")

    # =========================================================================
    # PART 4: Validation and Robustness
    # =========================================================================
    logger.info("─" * 50)
    logger.info("PART 4: Validation and Robustness Checks")
    logger.info("─" * 50)

    validation_results = run_all_validation(
        df            = df_est,
        market_stats  = market_stats,
        data_moments  = data_moments,
        msm_result    = msm_result,
        hedonic_params= hedonic_params,
        market_params = market_params,
    )

    # =========================================================================
    # PART 5: Outputs — Tables and Figures
    # =========================================================================
    logger.info("─" * 50)
    logger.info("PART 5: Tables and Figures")
    logger.info("─" * 50)

    # Bootstrap standard errors (optional, slow)
    se_dict = None
    if run_bootstrap and CONFIG["n_boot"] > 0:
        boot_result = bootstrap_se(
            df             = df_est,
            market_stats   = market_stats,
            hedonic_params = hedonic_params,
            market_params  = market_params,
            n_boot         = CONFIG["n_boot"],
        )
        se_dict = {
            "rho_se"     : boot_result["rho_se"],
            "rho_se_mean": float(np.nanmean(list(boot_result["rho_se"].values()))),
            "c0_se"      : boot_result["c0_se"],   # dict {market_id → float}
        }

    # Compute renovation subsidies (Sec. 7.6)
    subsidy_df = compute_market_subsidies(
        market_stats     = market_stats,
        market_params    = market_params,
        rho_hat          = msm_result.rho_hat,
        c0_hat           = msm_result.c0_hat,
        actual_reno_costs= CONFIG["actual_reno_costs"],
    )

    produce_all_outputs(
        df             = df_est,
        market_stats   = market_stats,
        data_moments   = data_moments,
        msm_result     = msm_result,
        hedonic_params = hedonic_params,
        subsidy_df     = subsidy_df,
        se_dict        = se_dict,
        did_params     = did_params,
        did_estimates  = did_estimates,
    )

    # =========================================================================
    # Collect all outputs
    # =========================================================================
    results = {
        "df"                 : df_est,
        "market_stats"       : market_stats,
        "hedonic_params"     : hedonic_params,
        "data_moments"       : data_moments,
        "market_params"      : market_params,
        # DiD first stage (primary identification)
        "did_estimates"      : did_estimates,   # DiDEstimates (β̂₁_m, Δ̂_m); None if index unavailable
        "did_params"         : did_params,      # EventStudyParams (ρ̂_m, ĉ₀_m); None if index unavailable
        # MSM second stage (overidentification + counterfactuals)
        "msm_result"         : msm_result,
        "c0_bounds"          : c0_bounds,
        "subsidy_df"         : subsidy_df,
        "validation_results" : validation_results,
        "se_dict"            : se_dict,
        "true_params"        : true_params,     # None if real data
    }

    logger.info("=" * 70)
    logger.info("ESTIMATION COMPLETE")
    logger.info("=" * 70)
    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Structural estimation: Mandatory Disclosure and Housing Markets"
    )
    parser.add_argument(
        "--synthetic",
        action  = "store_true",
        help    = "Use synthetic data (for pipeline testing and validation)",
    )
    parser.add_argument(
        "--no-bootstrap",
        action  = "store_true",
        help    = "Skip bootstrap standard errors (faster)",
    )
    parser.add_argument(
        "--log-level",
        default = "INFO",
        choices = ["DEBUG", "INFO", "WARNING", "ERROR"],
        help    = "Logging verbosity (DEBUG shows per-restart MSM details)",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)

    results = run_pipeline(
        use_synthetic  = args.synthetic,
        run_bootstrap  = not args.no_bootstrap,
    )
