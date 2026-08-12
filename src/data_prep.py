from __future__ import annotations
"""
data_prep.py
============
Part 1: Data Preparation
------------------------
Loads, merges, and classifies listing-level data following Section 7.1 of the paper.

Key objects produced:
  - df          : listing-level DataFrame with group classification (Table 5)
  - market_stats: market-level DataFrame with directly-measured parameters
                  π̂_m, θ̂_m, σ̂_{0,m}, σ̂_{1,m}, and mean log prices (directly measured market statistics, estimation appendix forthcoming)

Data requirements (not yet available; placeholders provided):
  Listings data  : one row per listing i in market m
    - listing_id, market_id
    - log_price_i          : log listing price (or transaction price if available)
    - d_i                  : 1 if EPC score displayed in listing, 0 otherwise
    - X_i                  : vector of property controls (size, age, floor, type, ...)
  ADEME registry : one row per certified energy audit
    - audit_id, listing_id (matched key)
    - K_i                  : 1 if verified EPC existed at listing time, 0 otherwise
    - theta_i              : true (verified) EPC quality; binarised here at threshold
"""

import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Section A — Placeholder data loading
# ---------------------------------------------------------------------------

def load_listings(path: str | Path, recode_market_id: bool = True) -> pd.DataFrame:
    """
    Load the listings dataset produced by data/collect_listings.py.

    Expected columns (minimum):
      listing_id  (str/int)   : unique listing identifier
      market_id   (str/int)   : local market identifier (e.g., IRIS or city code)
      log_price   (float)     : log price per m² (log(price/area))
      d           (int, 0/1)  : 1 if EPC score displayed in listing, 0 otherwise
      epc_score   (float)     : numeric EPC score 1–7 (A=1…G=7); NaN when d=0
      size_m2     (float)     : listing area in m²
      age         (float)     : property age in years at time of listing

    Parameters
    ----------
    recode_market_id : bool, default True
        The raw market_id encodes {cateaav2020_prefix}{city_center_COG}, where
        the first 2 characters are the cateaav2020 urban-area category and the
        last 5 characters are the COG of the attraction city-centre that defines
        the market.  When True (default), market_id is replaced by the last 5
        characters so that all municipalities in the same attraction zone share
        the same market_id regardless of their individual urban category.
        Set to False to keep the raw 7-character identifier.

    To generate this file from the database, run:
      from data.collect_data import collect_and_save_listings
      collect_and_save_listings(geo_id=..., geo_label='iris_id', ...)

    Returns
    -------
    pd.DataFrame
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Listings data not found at {path}. "
            "Run data/collect_listings.py::collect_and_save_listings() first to "
            "collect from the database and save to this path."
        )
    df = pd.read_parquet(path) if path.suffix == '.parquet' else pd.read_csv(path)

    if recode_market_id and "market_id" in df.columns:
        raw = df["market_id"].astype(str)
        # Only strip when the raw id is longer than 5 chars (i.e. has the prefix)
        df["market_id"] = raw.where(raw.str.len() <= 5, raw.str[-5:])

    return df


def load_ademe(path: str | Path) -> pd.DataFrame:
    """
    Load the ADEME certified-audit registry and return matched audit records.

    Expected columns:
      listing_id  (str/int)   : key to match with listings
      K           (int, 0/1)  : 1 if verified EPC existed at listing time
      epc_score   (float)     : raw EPC score 1–7 (A=1…G=7, matching collect_data encoding)

    If the ADEME registry is not yet available, K defaults to 0 for all listings
    (treated as uninformed sellers) — see merge_datasets().

    Returns
    -------
    pd.DataFrame
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"ADEME data not found at {path}. "
            "Please supply the ADEME audit registry at this path. "
            "If unavailable, pass ademe=None to merge_datasets() to treat all "
            "sellers as uninformed (K=0)."
        )
    if path.suffix == '.parquet':
        return pd.read_parquet(path)
    return pd.read_csv(path)


def binarise_epc(epc_score, threshold: float = 3.0) -> int:
    """
    Map raw EPC score to binary quality θ ∈ {0, 1}.

    Assumption: EPC letters A–G are coded 1–7 (or kWh/m²/year thresholds).
      θ = 1 (high quality) if score ≤ threshold  (e.g., A/B/C)
      θ = 0 (low  quality) if score >  threshold  (e.g., D/E/F/G)

    The paper treats θ as binary. We binarise at the median of the distribution
    of informed sellers' scores, or at a policy-relevant cutoff (e.g., class C/D
    boundary). Adjust `threshold` accordingly.

    This binarisation is a key modelling assumption. Robustness checks in
    validation.py vary this threshold.
    """
    return int(epc_score <= threshold)


# ---------------------------------------------------------------------------
# Section B — Merge and classify listings (Table 5 of the paper)
# ---------------------------------------------------------------------------

def merge_datasets(
    listings       : pd.DataFrame,
    ademe          : pd.DataFrame | None,
    epc_threshold  : float = 3.0,
    hider_theta    : str   = "registry",
) -> pd.DataFrame:
    """
    Left-join listings to ADEME registry on listing_id.

    Unmatched listings (K = NaN) are treated as uninformed sellers (K = 0).

    If ademe is None, the listings DataFrame is expected to already contain
    K and epc_score columns (e.g., when K comes from collect_listings.py which
    uses the self-reported EPC as a proxy, or when the ADEME registry is not
    yet available).

    Parameters
    ----------
    listings : pd.DataFrame       — listing-level data (from load_listings)
    ademe    : pd.DataFrame | None — ADEME audit registry with K, epc_score;
                                     pass None to use K/epc_score already in listings
    hider_theta : {"registry", "impose_zero"}
        How to assign theta to informed non-disclosers (d=0, K=1), who display no
        score of their own. "registry" (default) binarises the certified registry
        score, leaving σ̂₁ measured and the corollary σ₁* = 0 testable.
        "impose_zero" assigns theta = 0 by revealed preference, which makes σ̂₁
        identically zero by construction; retained only to reproduce legacy runs.

    Returns
    -------
    pd.DataFrame with all listing columns plus K, theta, group
    """
    if ademe is not None:
        # ADEME columns take precedence; epc_score from listings is overwritten
        ademe_cols = ["listing_id", "K"]
        if "epc_score" in ademe.columns:
            ademe_cols.append("epc_score")
        df = listings.merge(ademe[ademe_cols], on="listing_id", how="left",
                            suffixes=("_listing", ""))
        # Drop listing-side epc_score if ADEME has its own
        if "epc_score_listing" in df.columns:
            df = df.drop(columns=["epc_score_listing"])
    else:
        df = listings.copy()

    # K = 0 for unmatched listings (genuine informational constraint)
    if "K" not in df.columns:
        df["K"] = 0
    df["K"] = df["K"].fillna(0).astype(int)

    # epc_score: keep from listings if not supplied by ADEME
    if "epc_score" not in df.columns:
        df["epc_score"] = np.nan

    # Binarise EPC quality where available
    df["theta"] = df["epc_score"].apply(
        lambda x: binarise_epc(x, threshold=epc_threshold) if pd.notna(x) else np.nan
    )

    # Quality of informed non-disclosers (d=0, K=1).
    #
    # These listings display no EPC score, so `epc_score` is missing for all of
    # them and theta cannot be binarised from the listing itself. The registry,
    # however, records their certified score: `ademe_epc_score` is populated for
    # 100% of matched listings, hiders included.
    #
    #   "registry" (default) — binarise theta from the registry score. σ̂₁ is then
    #       MEASURED, so the model's prediction σ₁* = 0 (Corollary cor:hq_disclose)
    #       becomes a testable restriction.
    #   "impose_zero" (legacy) — set theta = 0 by revealed preference, assuming the
    #       corollary holds. Reproduces results prior to 2026-08, but makes
    #       σ̂₁ identically zero by construction: `compute_market_stats` derives
    #       σ̂₁ as the d=0 share among (K=1, theta=1) listings, and this assignment
    #       empties that set. The restriction then cannot be violated, and the
    #       model's own prediction is used to build the variable that confirms it.
    mask_hiders = (df["d"] == 0) & (df["K"] == 1)
    if hider_theta == "registry":
        if "ademe_epc_score" not in df.columns:
            raise ValueError(
                "hider_theta='registry' requires an 'ademe_epc_score' column "
                "(the certified registry score). Pass hider_theta='impose_zero' "
                "to reproduce the legacy revealed-preference assignment."
            )
        df.loc[mask_hiders, "theta"] = df.loc[mask_hiders, "ademe_epc_score"].apply(
            lambda x: binarise_epc(x, threshold=epc_threshold) if pd.notna(x) else np.nan
        )
    elif hider_theta == "impose_zero":
        df.loc[mask_hiders, "theta"] = 0
    else:
        raise ValueError(
            f"hider_theta must be 'registry' or 'impose_zero', got {hider_theta!r}"
        )

    return df


def classify_listings(
    df: pd.DataFrame,
    unverified_disclosers: str = "honest",
) -> pd.DataFrame:
    """
    Assign each listing to one of three (or four) mutually exclusive groups (Table 5).

    Group                d  K   θ       Interpretation
    ──────────────────── ── ── ───      ─────────────────────────────────────
    Truthful Disclosure  1  1   *       Verified informed seller discloses θ
    Strategic Hiding     0  1   0       Informed seller conceals (θ=0 by revealed pref.)
    Uninformed           0  0   NaN     Seller lacks certified information
    (Unverified Discl.)  1  0   *       Discloses without ADEME match — see below

    Parameters
    ----------
    unverified_disclosers : {"honest", "drop"}
        How to treat listings with d=1 but no ADEME match (K=0):
        - "honest" (default): treat as truthful disclosers — K=0 most likely
          reflects a matching failure or a pre-database DPE, not fabrication.
          Their θ is binarised from the self-reported epc_score.
        - "drop": exclude them from the sample entirely (classic no-falsification
          assumption used as a robustness check).
    """
    mask_d1k1 = (df["d"] == 1) & (df["K"] == 1)
    mask_d1k0 = (df["d"] == 1) & (df["K"] == 0)
    mask_hide = (df["d"] == 0) & (df["K"] == 1)
    mask_unin = (df["d"] == 0) & (df["K"] == 0)

    conditions = [mask_d1k1, mask_d1k0, mask_hide, mask_unin]
    choices    = ["truthful_disclosure", "truthful_disclosure", "strategic_hiding", "uninformed"]
    df["group"] = np.select(conditions, choices, default="unknown")

    if unverified_disclosers == "drop":
        df = df[~mask_d1k0].copy()
    return df


# ---------------------------------------------------------------------------
# Section C — Market-level statistics (directly measured parameters, estimation appendix forthcoming)
# ---------------------------------------------------------------------------

def compute_market_stats(df: pd.DataFrame, controls: list[str] | None = None) -> pd.DataFrame:
    """
    Compute directly-measured parameters for each market m (directly measured market statistics, estimation appendix forthcoming).

    Parameters estimated here (no structural model required):
      π̂_m   : share of informed sellers (directly measured market statistics, estimation appendix forthcoming)
      θ̂_m   : average quality among informed sellers (directly measured market statistics, estimation appendix forthcoming)
      σ̂_{0,m}: hiding rate among informed low-quality sellers (directly measured market statistics, estimation appendix forthcoming)
      σ̂_{1,m}: hiding rate among informed high-quality sellers (directly measured market statistics, estimation appendix forthcoming)
                (model predicts σ̂_{1,m} ≈ 0; this is a testable implication)

    Data moments for MSM (Table 6):
      p̄_{m,d=1,θ=1}: mean log price, truthful disclosers, high quality
      p̄_{m,d=1,θ=0}: mean log price, truthful disclosers, low quality
      p̄_{m,d=0}    : mean log price, all non-disclosers
      σ̂_{0,m}       : hiding rate (moment 4)

    Parameters
    ----------
    df       : listing-level DataFrame (output of classify_listings)
    controls : list of control variable column names (for mean X̄_m computation)

    Returns
    -------
    pd.DataFrame indexed by market_id, one row per market
    """
    # Exclude unverified disclosers from all market statistics
    df_clean = df[df["group"] != "unverified_disclosers"].copy()

    markets = []
    for m, grp in df_clean.groupby("market_id"):
        n_total    = len(grp)
        n_informed = (grp["K"] == 1).sum()

        # π̂_m: share of informed sellers (directly measured market statistics, estimation appendix forthcoming)
        pi_hat = n_informed / n_total if n_total > 0 else np.nan

        # θ̂_m: mean quality among informed sellers (directly measured market statistics, estimation appendix forthcoming)
        informed = grp[grp["K"] == 1]
        theta_bar_hat = informed["theta"].mean() if len(informed) > 0 else np.nan

        # Informed low-quality sellers (K=1, θ=0)
        informed_low  = informed[informed["theta"] == 0]
        informed_high = informed[informed["theta"] == 1]

        # σ̂_{0,m}: hiding rate among informed low-quality (directly measured market statistics, estimation appendix forthcoming)
        n_inf_low_hide    = (informed_low["d"] == 0).sum()
        n_inf_low         = len(informed_low)
        sigma_0_hat = n_inf_low_hide / n_inf_low if n_inf_low > 0 else np.nan

        # σ̂_{1,m}: hiding rate among informed high-quality (directly measured market statistics, estimation appendix forthcoming)
        # Model prediction: σ̂_{1,m} ≈ 0 (testable implication, Corollary (cor:hq_disclose))
        n_inf_high_hide   = (informed_high["d"] == 0).sum()
        n_inf_high        = len(informed_high)
        sigma_1_hat = n_inf_high_hide / n_inf_high if n_inf_high > 0 else np.nan

        # --- Data moments (Table 6) ---
        # Moment 1: mean log price, truthful high-quality disclosers
        mask_m1 = (grp["d"] == 1) & (grp["K"] == 1) & (grp["theta"] == 1)
        p_bar_d1_th1 = grp.loc[mask_m1, "log_price"].mean()
        n_m1         = mask_m1.sum()

        # Moment 2: mean log price, truthful low-quality disclosers
        mask_m2 = (grp["d"] == 1) & (grp["K"] == 1) & (grp["theta"] == 0)
        p_bar_d1_th0 = grp.loc[mask_m2, "log_price"].mean()
        n_m2         = mask_m2.sum()

        # Moment 3: mean log price, all non-disclosers
        mask_m3 = grp["d"] == 0
        p_bar_d0 = grp.loc[mask_m3, "log_price"].mean()
        n_m3     = mask_m3.sum()

        # Non-disclosure premium: raw difference (estimation appendix forthcoming)
        # Deltā_m = p̄_{d=0} - p̄_{d=1,θ=0}
        delta_bar_raw = p_bar_d0 - p_bar_d1_th0

        # Mean controls X̄_m (for hedonic prediction)
        row = {
            "market_id"          : m,
            "n_total"            : n_total,
            "n_informed"         : int(n_informed),
            "n_informed_low"     : len(informed_low),
            "n_informed_high"    : len(informed_high),
            "pi_hat"             : pi_hat,
            "theta_bar_hat"      : theta_bar_hat,
            "sigma_0_hat"        : sigma_0_hat,   # m4^data
            "sigma_1_hat"        : sigma_1_hat,   # testable: should ≈ 0
            "p_bar_d1_th1"       : p_bar_d1_th1, # m1^data
            "p_bar_d1_th0"       : p_bar_d1_th0, # m2^data
            "p_bar_d0"           : p_bar_d0,      # m3^data
            "delta_bar_raw"      : delta_bar_raw, # raw non-disclosure premium
            "n_m1"               : int(n_m1),
            "n_m2"               : int(n_m2),
            "n_m3"               : int(n_m3),
        }

        # Add mean/mode controls X̄_m
        # Continuous controls: mean; categorical (object/category) controls: mode
        if controls:
            for ctrl in controls:
                if ctrl not in grp.columns:
                    continue
                if not pd.api.types.is_numeric_dtype(grp[ctrl]):
                    row[f"X_bar_{ctrl}"] = grp[ctrl].mode().iloc[0] if len(grp) > 0 else np.nan
                else:
                    row[f"X_bar_{ctrl}"] = grp[ctrl].mean()

        markets.append(row)

    market_stats = pd.DataFrame(markets).set_index("market_id")

    # Flag markets with sufficient sample size for estimation.
    # Note: n_m2 (disclosed low-quality) can be 0 in partial-separation markets
    # where all informed low-quality sellers hide (σ₀*=1). In that case moment 2
    # receives zero weight in the MSM objective. The minimum useful requirement
    # is that we observe truthful high-quality disclosers (n_m1) and non-disclosers
    # (n_m3), plus some informed sellers to measure π̂_m and θ̂_m.
    market_stats["estimable"] = (
        (market_stats["n_m1"] >= 5)
        & (market_stats["n_m3"] >= 5)
        & (market_stats["n_informed"] >= 10)
    )

    return market_stats


# ---------------------------------------------------------------------------
# Section D — Synthetic data generator (for testing the pipeline)
# ---------------------------------------------------------------------------

def make_synthetic_data(
    n_listings: int = 5_000,
    n_markets: int = 10,
    pi: float = 0.60,
    theta_bar: float = 0.40,
    rho_true: float = 0.35,
    beta_1: float = 0.06,
    seed: int = 42,
    target_sigma_0: float = 0.7,
    controls: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Generate synthetic listing-level data consistent with the model's equilibrium.

    This is the canonical test case for the estimation pipeline. The data-generating
    process follows the paper's model exactly (using the structural profit function
    to compute optimal prices), so we can verify that the estimator recovers the
    true parameters (rho_true, c0_true).

    c0_true is computed endogenously to be consistent with the target hiding rate:
      - target_sigma_0 ∈ (0, 1): mixed strategy (σ₀* = target_sigma_0)
      - target_sigma_0 = 1.0   : pooling / partial separation (all low-quality hide)
      - target_sigma_0 = 0.0   : full unraveling (no hiding)

    Parameters
    ----------
    n_listings     : total number of listings
    n_markets      : number of housing markets (IRIS-level)
    pi             : share of informed sellers (homogeneous across markets for simplicity)
    theta_bar      : population share of high-quality properties
    rho_true       : share of EPC-sensitive buyers
    beta_1         : log-price premium for disclosed high-quality property (valuation param)
    seed           : random seed
    target_sigma_0 : target equilibrium hiding rate σ₀* ∈ [0, 1].
                     0.7 → mixed strategy (default); 1.0 → pooling; 0.0 → full unraveling.
    controls       : list of control column names to pass to compute_market_stats.
                     Defaults to ["size_m2", "built_year", "cateaav2020_label", "distance"].

    Returns
    -------
    df           : listing-level DataFrame (same schema as merge_datasets output)
    market_stats : market-level statistics (from compute_market_stats)
    true_params  : dict of data-generating parameters for validation
    """
    if controls is None:
        controls = ["size_m2", "built_year", "cateaav2020_label", "distance"]

    rng = np.random.default_rng(seed)

    # ── Market / city structure ───────────────────────────────────────────────
    # Each market is an IRIS unit; multiple IRIS belong to the same city.
    # n_cities = roughly n_markets / 3 (at least 2).
    n_cities   = max(2, n_markets // 3)
    market_ids = rng.integers(0, n_markets, size=n_listings)
    # Each market is assigned to exactly one city
    market_to_city = rng.integers(0, n_cities, size=n_markets)
    city_ids       = market_to_city[market_ids]   # city_id per listing

    # ── Information status and quality ───────────────────────────────────────
    K     = rng.binomial(1, pi,        size=n_listings)
    theta = rng.binomial(1, theta_bar, size=n_listings)

    # ── Continuous controls ───────────────────────────────────────────────────
    size_m2  = rng.normal(60, 20, size=n_listings).clip(20, 200)
    distance = rng.exponential(scale=8.0, size=n_listings).clip(0.5, 50.0)

    # ── Categorical controls ──────────────────────────────────────────────────
    # built_year: French construction period bins (from process_built_year)
    _by_bins  = ['1799', '1800_1914', '1915_1945', '1946_1974',
                 '1975_1990', '1991_2003', '2004']
    _by_probs = [0.02,   0.13,        0.10,        0.30,
                 0.20,         0.13,        0.12]       # approx. French stock shares
    _by_idx   = rng.choice(len(_by_bins), size=n_listings, p=_by_probs)
    built_year = np.array(_by_bins)[_by_idx]

    # cateaav2020_label: French urban-area type (CATEAAV 2020)
    _ua_labels = ['Grand pôle urbain', 'Couronne grand pôle',
                  'Multipolarisé', 'Commune isolée']
    _ua_probs  = [0.45, 0.25, 0.20, 0.10]
    _ua_idx    = rng.choice(len(_ua_labels), size=n_listings, p=_ua_probs)
    cateaav    = np.array(_ua_labels)[_ua_idx]

    # ── Log-price DGP: market FE + city FE + control effects + noise ─────────
    # True price effects for each category (used to generate data only)
    _by_effects = {
        '1799': 0.05, '1800_1914': 0.03, '1915_1945': 0.01,
        '1946_1974': 0.00,   # reference (most common)
        '1975_1990': -0.01, '1991_2003': 0.01, '2004': 0.03,
    }
    _ua_effects = {
        'Grand pôle urbain': 0.08, 'Couronne grand pôle': 0.04,
        'Multipolarisé': 0.02,     'Commune isolée': -0.05,
    }

    market_fe = rng.normal(0, 0.15, size=n_markets)
    city_fe   = rng.normal(0, 0.05, size=n_cities)   # city-level premium

    by_contrib  = np.array([_by_effects[b] for b in built_year])
    ua_contrib  = np.array([_ua_effects[u] for u in cateaav])

    log_price_base = (
        12.0
        + market_fe[market_ids]
        + city_fe[city_ids]
        + 0.003 * size_m2
        - 0.005 * distance
        + by_contrib
        + ua_contrib
    )

    # ---- Solve the equilibrium consistently with the structural model ----
    # Import here to avoid circular imports at module level
    from src.model import ValuationParams, solve_equilibrium, optimal_price, belief_function

    # Calibrated structural parameters (market-average; market FE will shift the
    # baseline log price but do not affect the relative price structure).
    # scale: logistic demand scale in log-price units (calibrated from noise_std)
    # v0_offset: how much less insensitive buyers value the property relative to
    #   β₀ + X̄'β_X.  A small negative offset ensures v₀ < v₁(θ=0).
    noise_std  = 0.10   # idiosyncratic log-price noise
    scale      = noise_std * np.pi / np.sqrt(3.0)   # probit-logit calibration

    params = ValuationParams(
        beta_0    = 0.0,    # market FE absorbed in log_price_base
        beta_1    = beta_1,
        X_beta_X  = 0.0,    # controls absorbed in log_price_base
        v0_offset = -0.03,  # insensitive buyers value property slightly less
        scale     = scale,
        gamma_0   = 0.0,
        gamma_1   = 1.0,
    )

    # Find c0_true consistent with the target equilibrium hiding rate (Proposition (prop:equilibrium)).
    #
    # Equilibrium condition: Δ(e(σ₀*)) = c₀  (mixed strategy, Proposition (prop:equilibrium))
    # Regimes (Proposition (prop:equilibrium)):
    #   σ₀* ∈ (0,1): mixed strategy  → c₀ = Δ(e(σ₀*))
    #   σ₀* = 1    : pooling         → c₀ < Δ(e(1)), set to 50% of Δ(e(1))
    #   σ₀* = 0    : full unraveling → c₀ > Δ(e(0)), set to 150% of Δ(e(0))
    from src.model import profit_gain_hiding_structural
    e0 = belief_function(0.0, pi, theta_bar)
    e1 = belief_function(1.0, pi, theta_bar)
    if target_sigma_0 >= 1.0:
        # Pooling equilibrium: c₀ strictly below Δ(e(1))
        c0_true = profit_gain_hiding_structural(e1, rho_true, params) * 0.5
    elif target_sigma_0 <= 0.0:
        # Full unraveling: c₀ strictly above Δ(e(0))
        delta_e0 = profit_gain_hiding_structural(e0, rho_true, params)
        c0_true  = delta_e0 * 1.5 if delta_e0 > 0 else 0.01
    else:
        # Mixed strategy: c₀ = Δ(e(σ₀*))
        e_target = belief_function(target_sigma_0, pi, theta_bar)
        c0_true  = profit_gain_hiding_structural(e_target, rho_true, params)

    # Solve equilibrium at true parameters
    eq         = solve_equilibrium(rho_true, c0_true, pi, theta_bar, params)
    sigma_0_star = eq.sigma_0_star
    e_star       = eq.e_star

    # Model-implied optimal log prices (at zero market FE; shift by alpha_m below)
    p_d1_th1 = optimal_price(params.v1_disclosed(1.0), params.v0, rho_true, params)
    p_d1_th0 = optimal_price(params.v1_disclosed(0.0), params.v0, rho_true, params)
    p_d0     = optimal_price(params.v1_hidden(e_star),  params.v0, rho_true, params)

    # ---- Simulate equilibrium disclosure decisions ----
    # High-quality informed sellers always disclose (σ_1* = 0, Corollary (cor:hq_disclose))
    # Low-quality informed sellers hide with prob σ_0* (from equilibrium)
    d = np.zeros(n_listings, dtype=int)
    mask_informed_high = (K == 1) & (theta == 1)
    mask_informed_low  = (K == 1) & (theta == 0)
    d[mask_informed_high] = 1
    d[mask_informed_low]  = rng.binomial(1, 1.0 - sigma_0_star,
                                          size=mask_informed_low.sum())

    # ---- Simulate log prices from structural model's optimal prices ----
    # log_price_i = p*(d_i, θ_i; ρ_true) + α_m + control_contribution + ε_i
    # where α_m = market_fe, control_contribution = 0.003*size - 0.002*age
    # (these are absorbed in log_price_base = 12.0 + alpha_m + controls)
    #
    # The "base" shifts the absolute price level; the structural model determines
    # the *relative* prices across groups.  The reference level is p_d1_th0 (the
    # disclosed low-quality price at mean characteristics ≈ 0).
    eps = rng.normal(0, noise_std, size=n_listings)

    log_price = log_price_base.copy()
    # Add structural price contributions relative to the model baseline (=0)
    mask_high_disc = (d == 1) & (theta == 1)   # truthful high-quality
    mask_low_disc  = (d == 1) & (theta == 0)   # truthful low-quality
    mask_hide_all  = (d == 0)                  # all non-disclosers

    log_price[mask_high_disc] += p_d1_th1
    log_price[mask_low_disc]  += p_d1_th0
    log_price[mask_hide_all]  += p_d0
    log_price += eps

    df = pd.DataFrame({
        "listing_id"       : np.arange(n_listings),
        "market_id"        : market_ids,
        "city_id"          : city_ids,
        "log_price"        : log_price,
        "d"                : d,
        "K"                : K,
        "theta"            : theta.astype(float),
        "epc_score"        : np.where(K == 1, theta.astype(float), np.nan),
        "size_m2"          : size_m2,
        "built_year"       : built_year,
        "cateaav2020_label": cateaav,
        "distance"         : distance,
    })
    df["group"] = np.select(
        [
            (df["d"] == 1) & (df["K"] == 1),
            (df["d"] == 0) & (df["K"] == 1),
            (df["d"] == 0) & (df["K"] == 0),
            (df["d"] == 1) & (df["K"] == 0),
        ],
        ["truthful_disclosure", "strategic_hiding", "uninformed", "unverified_disclosers"],
        default="unknown",
    )

    market_stats = compute_market_stats(df, controls=controls)

    true_params = {
        "pi"          : pi,
        "theta_bar"   : theta_bar,
        "rho"         : rho_true,
        "c0"          : c0_true,
        "beta_1"      : beta_1,
        "e_star"      : e_star,
        "sigma_0_star": sigma_0_star,
        "scale"       : scale,
        "p_d1_th1"    : p_d1_th1,
        "p_d1_th0"    : p_d1_th0,
        "p_d0"        : p_d0,
    }

    return df, market_stats, true_params


# ---------------------------------------------------------------------------
# Section E — Market centroids for spatial visualisation
# ---------------------------------------------------------------------------

def compute_market_levels(
    df             : pd.DataFrame,
    log_price_col  : str = "log_price",
    area_col       : str = "size_m2",
    market_col     : str = "market_id",
) -> pd.DataFrame:
    """
    Per-market price and size benchmarks used to translate nominal renovation
    costs (€/m²) into the model's log-price units.

    Note: `log_price` in the listings parquet is `log(price / area)` (see
    `load_listings` docstring), so `exp(log_price)` is price per m² in €.

    Returns
    -------
    pd.DataFrame indexed by market_id with columns:
        price_per_m2_eur : exp(median log_price) per market (€/m²)
        median_area_m2   : median listing area per market (m²)
        n_listings       : number of listings per market
    """
    out = (
        df.groupby(market_col, observed=False)
        .agg(
            log_price_median=(log_price_col, "median"),
            median_area_m2  =(area_col, "median"),
            n_listings      =(log_price_col, "size"),
        )
    )
    out["price_per_m2_eur"] = np.exp(out["log_price_median"])
    return out[["price_per_m2_eur", "median_area_m2", "n_listings"]]


def _load_dept_centroids(geojson_path: str | Path) -> dict[str, tuple[float, float]]:
    """
    Load département centroids (lat, lon) keyed by dept code (string with
    leading zero, e.g. '01', '75', '2A').
    """
    try:
        from shapely.geometry import shape
    except ImportError as exc:
        raise ImportError(
            "shapely is required to compute département centroids. "
            "Install with `pip install shapely`."
        ) from exc

    with open(geojson_path) as fh:
        gj = json.load(fh)

    out: dict[str, tuple[float, float]] = {}
    for feat in gj["features"]:
        code = str(feat["properties"]["code"])
        geom = shape(feat["geometry"])
        c    = geom.centroid
        out[code] = (float(c.y), float(c.x))  # (lat, lon)
    return out


def compute_market_centroids(
    listings_df  : pd.DataFrame,
    geojson_path : str | Path = "data/geo/departements.geojson",
    market_col   : str = "market_id",
    dept_col     : str = "dept",
    cache_path   : str | Path | None = None,
) -> pd.DataFrame:
    """
    Compute one (lat, lon) coordinate per market for spatial visualisation.

    The listings parquet does not contain raw geocoordinates; we use each
    listing's département centroid and take the listings-weighted mean across
    departments per market. Resolution is sufficient for a bubble-map visual.

    Parameters
    ----------
    listings_df  : DataFrame with columns `market_id` and `dept`.
    geojson_path : path to a département-level GeoJSON (with `properties.code`).
    cache_path   : if given, write the result as CSV.

    Returns
    -------
    DataFrame indexed by market_id with columns: lat, lon, n_listings, modal_dept.
    """
    dept_centroids = _load_dept_centroids(geojson_path)

    work = listings_df[[market_col, dept_col]].copy()
    work[dept_col] = work[dept_col].astype(str).str.zfill(2)

    rows = []
    for m, g in work.groupby(market_col):
        counts  = g[dept_col].value_counts()
        n_total = int(counts.sum())

        lat_sum, lon_sum, w_sum = 0.0, 0.0, 0
        for dept_code, n in counts.items():
            coord = dept_centroids.get(dept_code)
            if coord is None:
                continue
            lat, lon = coord
            lat_sum += lat * n
            lon_sum += lon * n
            w_sum   += n

        if w_sum == 0:
            logger.warning(f"[centroids] market {m}: no dept matched, skipping")
            continue

        rows.append({
            "market_id" : m,
            "lat"       : lat_sum / w_sum,
            "lon"       : lon_sum / w_sum,
            "n_listings": n_total,
            "modal_dept": str(counts.idxmax()),
        })

    out = pd.DataFrame(rows).set_index("market_id")

    if cache_path is not None:
        cache_path = Path(cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(cache_path)
        logger.info(f"[centroids] wrote {cache_path}  (N={len(out)})")

    return out
