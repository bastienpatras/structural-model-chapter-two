from __future__ import annotations

"""
moments.py
==========
Part 3: Data Moments and Model-Implied Moments
----------------------------------------------
Implements the MSM moment construction (Table, Sec. "Data and Model Objects", Appendix; estimation appendix forthcoming).

Five moments per market m — all price moments on the *residual* scale:
  m₁^data : mean hedonic residual, disclosed high-quality  (d=1, K=1, θ=1) ≈ β̂₁_m
  m₂^data : mean hedonic residual, disclosed low-quality   (d=1, K=1, θ=0) ≈ 0
  m₃^data : mean hedonic residual, non-disclosed           (d=0)
  m₄^data : hiding rate among informed low-quality         σ̂_{0,m}
  m₅^data : hiding rate among informed high-quality        σ̂_{1,m}

Residual = log_price − (α̂_m + X_i'γ̂): subtracts the market FE and all control
contributions from the pooled hedonic, retaining only the EPC signal β₁·θ and ε.
This removes selection on observables from m₃ and makes model moments interpretable
as pure EPC effects. Requires `hedonic_params` to be passed to extract_data_moments.
If omitted, falls back to raw log-price moments (legacy behaviour).

Model-implied counterparts (Sec. 7.4.2):
  m₁^model : β₁_m              — EPC premium for θ=1 disclosers
  m₂^model : 0                 — reference (θ=0 disclosers)
  m₃^model : β₁_m · e*(σ₀*)   — belief-weighted EPC signal for hiders
  m₄^model : σ₀*(ρ_m, c₀)     — equilibrium hiding rate (low-quality)
  m₅^model : 0                 — σ₁* = 0 always (Corollary (cor:hq_disclose))

Identification logic:
  - m₁, m₂ fit by construction (≈ 0 residual after residualisation). No information
    on ρ, c₀ — dropped from the MSM objective via DROP_MOMENTS=[0,1].
  - m₃ (DiD): DiD_Δ_m = β₁_m·e*(σ₀*;ρ,c₀) identifies ρ_m once β₁_m is known.
    The DiD version differences out pre-reform selection bias. For markets without
    DiD coverage m₃ is NaN and automatically zeroed in the weighting matrix.
  - m₄ identifies c₀ via the equilibrium condition Δ(e*(σ₀*); ρ) = c₀.
  - m₅ is an overidentifying restriction: σ₁* = 0 (Corollary (cor:hq_disclose)).
    Excluded from the MSM objective (DROP_MOMENTS=[0,1,4]) — kept as a test.

Diagnostic (not a moment):
  Δ̄_m = m₃ − m₂ (residual hiding premium). Under the model Δ̄_m = β₁_m·e*,
  which is a lower bound on c₀ in the mixed-strategy equilibrium.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .model import (
    ValuationParams,
    belief_bounds,
    belief_function,
    optimal_price,
    solve_equilibrium,
)

# ---------------------------------------------------------------------------
# Section A — Data moments (Table 6, column "Data")
# ---------------------------------------------------------------------------


@dataclass
class DataMoments:
    """
    Five data moments for market m — Table 6, column 2.

    All prices are in log units (m1–m3). Moments 4–5 are probabilities.
    m5 is an overidentifying restriction: σ̂_1_m should equal 0 under the model.

    delta_bar is stored as a diagnostic (not used in MSM objective):
      Δ̄_m = p̄(d=0) − p̄(d=1,θ=0). Since σ̂_0 ≈ 0, this gives a lower bound
      on ĉ₀ — sellers forgo Δ̄_m by not hiding, so c₀ ≥ Δ̄_m.
    """

    market_id: str | int
    m1: float  # p̄_{m,d=1,θ=1}  — mean log price, disclosed high
    m2: float  # p̄_{m,d=1,θ=0}  — mean log price, disclosed low
    m3: float  # p̄_{m,d=0}      — mean log price, non-disclosed
    m4: float  # σ̂_{0,m}         — hiding rate, informed low-quality
    m5: float  # σ̂_{1,m}         — hiding rate, informed high-quality (model: = 0)
    # Diagnostic — not a moment
    delta_bar: float = np.nan  # Δ̄_m = m3 − m2 (hiding premium, lower bound on c₀)
    # Variances of data moments (for inverse-variance weighting)
    var_m1: float = np.nan
    var_m2: float = np.nan
    var_m3: float = np.nan
    var_m4: float = np.nan
    var_m5: float = np.nan
    # Sample sizes (for diagnostics)
    n1: int = 0
    n2: int = 0
    n3: int = 0
    n4_informed: int = 0   # denominator of σ̂_{0,m}
    n5_informed: int = 0   # denominator of σ̂_{1,m}


def extract_data_moments(
    df: pd.DataFrame,
    market_col: str = "market_id",
    hedonic_params=None,
    did_delta: dict[str | int, float] | None = None,
) -> dict[str | int, DataMoments]:
    """
    Compute data moments from listing-level data for each market.

    Parameters
    ----------
    df             : listing-level DataFrame with columns:
                     log_price, d, K, theta, market_id, group
    market_col     : market identifier column name
    hedonic_params : HedonicParams (optional). If provided, price moments m₁–m₃
                     are computed on the *residual* scale:
                       residual_i = log_price_i − (α̂_m + X_i'γ̂)
                     This removes market FE and control variation, so moments
                     reflect the pure EPC signal. m₁ ≈ β̂₁_m, m₂ ≈ 0, and
                     m₃ = residualized hiding premium (≈ β₁·e* + selection bias).
                     Falls back to raw log-price if hedonic_params is None.
    did_delta      : dict mapping market_id → DiD_Δ_m (optional). When provided,
                     m₃ is replaced by the DiD-estimated non-disclosure premium
                     for markets where it is available. This removes the selection
                     contamination in the cross-sectional m₃ by differencing out
                     the pre-reform baseline. Markets without DiD coverage have
                     m₃ set to NaN, which causes build_weighting_matrix to
                     automatically zero out that moment for those markets.

    Returns
    -------
    dict mapping market_id → DataMoments
    """
    df_clean = df[df["group"] != "unverified_disclosers"].copy()

    # ── Residualize prices if hedonic_params supplied ─────────────────────────
    price_col = "log_price"
    if hedonic_params is not None:
        hp = hedonic_params
        # Baseline: α̂_m + X_i'γ̂  (excludes the θ·β̂₁ term)
        baseline = df_clean[market_col].map(hp.alpha_m).astype(float)
        # Continuous controls
        for col in hp.cont_controls:
            coef = hp.gamma.get(col, 0.0)
            if coef != 0.0 and col in df_clean.columns:
                baseline += coef * df_clean[col].fillna(0.0)
        # Categorical controls
        for col in hp.cat_controls:
            if col not in df_clean.columns:
                continue
            levels = df_clean[col].dropna().unique()
            coef_map = {lv: hp.gamma.get(f"C({col})[T.{lv}]", 0.0) for lv in levels}
            baseline += df_clean[col].map(coef_map).fillna(0.0)

        df_clean = df_clean.copy()
        df_clean["_price_resid"] = df_clean["log_price"] - baseline
        price_col = "_price_resid"

    moments = {}

    for m, grp in df_clean.groupby(market_col):
        # Moment 1: mean price (or residual), disclosed high-quality (d=1, K=1, θ=1)
        mask1 = (grp["d"] == 1) & (grp["K"] == 1) & (grp["theta"] == 1)
        m1 = grp.loc[mask1, price_col].mean()
        var1 = grp.loc[mask1, price_col].var() / max(mask1.sum(), 1)
        n1 = int(mask1.sum())

        # Moment 2: mean price (or residual), disclosed low-quality (d=1, K=1, θ=0)
        mask2 = (grp["d"] == 1) & (grp["K"] == 1) & (grp["theta"] == 0)
        m2 = grp.loc[mask2, price_col].mean()
        var2 = grp.loc[mask2, price_col].var() / max(mask2.sum(), 1)
        n2 = int(mask2.sum())

        # Moment 3: DiD non-disclosure premium if available, else cross-sectional residual
        mask3 = grp["d"] == 0
        n3 = int(mask3.sum())
        if did_delta is not None:
            # Use DiD_Δ_m: clean identification, differences out pre-reform selection.
            # Markets without DiD coverage get NaN → zeroed out in weighting matrix.
            m3   = did_delta.get(m, np.nan)
            var3 = np.nan  # no sampling variance for DiD moment (treated as fixed)
        else:
            m3   = grp.loc[mask3, price_col].mean()
            var3 = grp.loc[mask3, price_col].var() / max(n3, 1)

        # Moment 4: hiding rate among informed low-quality sellers
        # σ̂_{0,m} = #{K=1, θ=0, d=0} / #{K=1, θ=0}  (Eq. 107)
        mask_informed_low = (grp["K"] == 1) & (grp["theta"] == 0)
        mask_informed_low_h = mask_informed_low & (grp["d"] == 0)
        n_inf_low = mask_informed_low.sum()
        n_inf_low_h = mask_informed_low_h.sum()
        m4 = n_inf_low_h / n_inf_low if n_inf_low > 0 else np.nan
        # Variance of binomial proportion: p(1-p)/n
        var4 = (m4 * (1 - m4)) / max(n_inf_low, 1) if not np.isnan(m4) else np.nan

        # Moment 5: hiding rate among informed HIGH-quality sellers  (Corollary (cor:hq_disclose) test)
        # σ̂_{1,m} = #{K=1, θ=1, d=0} / #{K=1, θ=1}  — model predicts 0
        mask_inf_high   = (grp["K"] == 1) & (grp["theta"] == 1)
        mask_inf_high_h = mask_inf_high & (grp["d"] == 0)
        n_inf_high  = mask_inf_high.sum()
        n_inf_high_h = mask_inf_high_h.sum()
        m5    = n_inf_high_h / n_inf_high if n_inf_high > 0 else np.nan
        var5  = (m5 * (1 - m5)) / max(n_inf_high, 1) if not np.isnan(m5) else np.nan

        # Diagnostic: hiding premium (lower bound on c₀, not a moment)
        delta_bar = m3 - m2

        moments[m] = DataMoments(
            market_id=m,
            m1=float(m1),
            m2=float(m2),
            m3=float(m3),
            m4=float(m4),
            m5=float(m5),
            delta_bar=float(delta_bar),
            var_m1=float(var1),
            var_m2=float(var2),
            var_m3=float(var3),
            var_m4=float(var4),
            var_m5=float(var5),
            n1=n1,
            n2=n2,
            n3=n3,
            n4_informed=int(n_inf_low),
            n5_informed=int(n_inf_high),
        )

    return moments


# ---------------------------------------------------------------------------
# Section B — Model-implied moments (Table 6, column "Model")
# ---------------------------------------------------------------------------


@dataclass
class ModelMoments:
    """
    Five model-implied moments for market m, given parameters (ρ_m, c₀).

    These correspond exactly to the data moments in DataMoments.
    """

    market_id: str | int
    m1_model: float  # p*(d=1, θ=1; ρ_m)
    m2_model: float  # p*(d=1, θ=0; ρ_m)
    m3_model: float  # p*(d=0, e*_m; ρ_m)
    m4_model: float  # σ₀*(ρ_m, c₀)
    m5_model: float  # σ₁* = 0  always (Corollary (cor:hq_disclose) — high-quality always disclose)
    e_star: float  # equilibrium belief
    sigma_0_star: float  # equilibrium hiding rate (= m4_model)
    eq_type: str  # "full_unraveling" / "partial_separation" / "mixed_strategy"


def compute_model_moments(
    rho: float,
    c0: float,
    pi: float,
    theta_bar: float,
    params: ValuationParams,
    market_id: str | int = "unknown",
) -> ModelMoments:
    """
    Compute model-implied moments for market m given parameters (ρ_m, c₀).

    Algorithm (Section 7.4.2):
    1. Compute valuations v₁(d,θ) and v₀ from hedonic estimates.
    2. Solve equilibrium → (σ₀*, e*).
    3. Compute optimal prices p*(d, θ; ρ) and p*(d=0, e*; ρ) from the FOC.
    4. Assemble moments as (p*(d=1,θ=1), p*(d=1,θ=0), p*(d=0,e*), σ₀*).

    Parameters
    ----------
    rho       : share of EPC-sensitive buyers (parameter to estimate)
    c0        : hiding cost (parameter to estimate)
    pi        : share of informed sellers (directly measured, Eq. 105)
    theta_bar : population mean quality (directly measured, Eq. 106)
    params    : ValuationParams with hedonic coefficients for market m
    market_id : market identifier (for output labelling)

    Returns
    -------
    ModelMoments
    """
    # Step 1: Solve for equilibrium (σ₀*, e*) — Proposition (prop:equilibrium)
    eq = solve_equilibrium(rho, c0, pi, theta_bar, params)

    # Step 2: Model-implied moments on the *residual* scale.
    #
    # Data moments m₁–m₃ are residuals: log_price − (α̂_m + X_i'γ̂).
    # Model counterparts are the EPC signal alone (market FE and controls cancel):
    #
    #   m₁^model = β₁_m · 1   = β₁_m              (disclosers, θ=1)
    #   m₂^model = β₁_m · 0   = 0                  (disclosers, θ=0 — reference)
    #   m₃^model = ρ_m · β₁_m · e*                 (hiders; structural Eq. Δ_m = ρ_m·β₁_m·e*)
    #
    # Identification (ESTIMATION_STRATEGY.md, Sec. 1):
    #   m₁, m₂: fit by construction (≈ 0 residual). No information on ρ, c₀.
    #   m₃:     ρ_m·β₁_m·e* = Δ_m  →  identifies ρ_m directly (closed-form inversion)
    #           NOTE: m₃ is excluded from the MSM objective (drop_moments includes 2)
    #           because Δ_m from cross-sectional listing prices is contaminated by
    #           unobservable selection. The DiD first stage handles this via price
    #           index differencing. m₃ is computed here for diagnostics only.
    #   m₄:     σ₀*(ρ, c₀) = σ̂₀   →  identifies c₀ via Δ(e*(σ₀*); ρ) = c₀

    beta1 = params.beta_1
    sigma_0_star = eq.sigma_0_star

    return ModelMoments(
        market_id=market_id,
        m1_model=float(beta1),                        # β₁_m  (residual: θ=1 disclosers)
        m2_model=0.0,                                  # 0     (residual: θ=0 disclosers)
        m3_model=float(rho * beta1 * eq.e_star),      # ρ_m·β₁_m·e*  (structural eq.; diagnostic only)
        m4_model=float(sigma_0_star),
        m5_model=0.0,  # σ₁* = 0 is a sharp prediction (Corollary (cor:hq_disclose))
        e_star=float(eq.e_star),
        sigma_0_star=float(sigma_0_star),
        eq_type=eq.eq_type,
    )


# ---------------------------------------------------------------------------
# Section C — Moment comparison and residual vector
# ---------------------------------------------------------------------------


def moment_residuals(
    data_mom: DataMoments,
    model_mom: ModelMoments,
) -> np.ndarray:
    """
    Residuals m^data - m^model(ρ, c₀) — the objective of MSM (Eq. 123).

    Returns
    -------
    np.ndarray of shape (4,): [r₁, r₂, r₃, r₄]
    """
    r1 = data_mom.m1 - model_mom.m1_model
    r2 = data_mom.m2 - model_mom.m2_model
    r3 = data_mom.m3 - model_mom.m3_model
    r4 = data_mom.m4 - model_mom.m4_model
    r5 = data_mom.m5 - model_mom.m5_model
    return np.array([r1, r2, r3, r4, r5])


def build_weighting_matrix(
    data_moments : dict[str | int, DataMoments],
    scheme       : str = "inverse_variance",
    df           : pd.DataFrame | None = None,
    market_col   : str = "market_id",
    drop_moments : list[int] | None = None,
) -> dict[str | int, np.ndarray]:
    """
    Construct the GMM weighting matrix W for each market — Eq. 123.

    Schemes (Sec. 7.4.3):
      "equal" / "identity" : W = I₅
      "inverse_variance"   : W = diag(1/Var(m_j))  — diagonal
      "optimal_gmm"        : W = Ω̂⁻¹  — full 5×5 inverse covariance matrix.
                             Requires `df` (listing-level DataFrame).

    Parameters
    ----------
    drop_moments : list of moment indices (0-based) to exclude from the
                   objective by zeroing out their row/column in W.
                   E.g. drop_moments=[2] drops m₃ (residual hiding premium),
                   which is recommended when m₃ is contaminated by selection
                   on unobservables. Identification then rests on m₄ alone.

    Returns
    -------
    dict mapping market_id → np.ndarray of shape (5, 5)
    """
    if scheme == "optimal_gmm" and df is None:
        raise ValueError("scheme='optimal_gmm' requires df (listing-level DataFrame).")

    df_clean = df[df["group"] != "unverified_disclosers"].copy() if df is not None else None
    drop = list(drop_moments) if drop_moments else []

    weights = {}
    for m, dm in data_moments.items():
        if scheme in ("equal", "identity"):
            W = np.eye(5)

        elif scheme == "inverse_variance":
            vars_ = np.array([dm.var_m1, dm.var_m2, dm.var_m3, dm.var_m4, dm.var_m5])
            vars_ = np.where((vars_ <= 0) | np.isnan(vars_), 1e-6, vars_)
            W = np.diag(1.0 / vars_)

        elif scheme == "optimal_gmm":
            grp = df_clean[df_clean[market_col] == m]
            W = _optimal_gmm_weights(grp, dm)

        else:
            raise ValueError(f"Unknown weighting scheme: {scheme!r}")

        # Zero out dropped moments (row and column → no contribution to Q*)
        for j in drop:
            W[j, :] = 0.0
            W[:, j] = 0.0

        # Zero out NaN data moments (e.g. m₃ when DiD coverage is missing)
        nan_mask = np.isnan([dm.m1, dm.m2, dm.m3, dm.m4, dm.m5])
        for j in np.where(nan_mask)[0]:
            W[j, :] = 0.0
            W[:, j] = 0.0

        weights[m] = W

    return weights


def _optimal_gmm_weights(
    grp  : pd.DataFrame,
    dm   : "DataMoments",
    ridge: float = 1e-8,
) -> np.ndarray:
    """
    Compute W_m = Ω̂_m⁻¹ for a single market using the sandwich estimator.

    Individual influence-function contributions (centred):
      g_{i,1} = 1(mask1_i) · (log_price_i − m1) / n1
      g_{i,2} = 1(mask2_i) · (log_price_i − m2) / n2
      g_{i,3} = 1(mask3_i) · (log_price_i − m3) / n3
      g_{i,4} = 1(K=1,θ=0)_i · (1{d_i=0} − m4) / n_inf_low

    Ω̂ = G'G  where G is the N×4 matrix of contributions.

    The diagonal of Ω̂ equals the sampling variance of each moment (s_j²/n_j).
    The only non-zero off-diagonal term is Ω̂_{34}: non-disclosers (mask3) overlap
    with informed-low-quality sellers (mask_inf_low), so m₃ and m₄ are correlated.

    Falls back to diagonal inverse-variance if Ω̂ is singular or too small.
    """
    N = len(grp)
    if N < 8:
        vars_ = np.array([dm.var_m1, dm.var_m2, dm.var_m3, dm.var_m4, dm.var_m5])
        vars_ = np.where((vars_ <= 0) | np.isnan(vars_), 1e-6, vars_)
        return np.diag(1.0 / vars_)

    log_price = grp["log_price"].values
    d_vals    = grp["d"].values
    K_vals    = grp["K"].values
    th_vals   = grp["theta"].values

    mask1         = (d_vals == 1) & (K_vals == 1) & (th_vals == 1)
    mask2         = (d_vals == 1) & (K_vals == 1) & (th_vals == 0)
    mask3         = (d_vals == 0)
    mask_inf_low  = (K_vals == 1) & (th_vals == 0)
    mask_inf_high = (K_vals == 1) & (th_vals == 1)

    n1         = mask1.sum()
    n2         = mask2.sum()
    n3         = mask3.sum()
    n_inf_low  = mask_inf_low.sum()
    n_inf_high = mask_inf_high.sum()

    G = np.zeros((N, 5))

    if n1 > 0 and not np.isnan(dm.m1):
        G[mask1, 0] = (log_price[mask1] - dm.m1) / n1

    if n2 > 0 and not np.isnan(dm.m2):
        G[mask2, 1] = (log_price[mask2] - dm.m2) / n2

    if n3 > 0 and not np.isnan(dm.m3):
        G[mask3, 2] = (log_price[mask3] - dm.m3) / n3

    if n_inf_low > 0 and not np.isnan(dm.m4):
        G[mask_inf_low, 3] = (
            (d_vals[mask_inf_low] == 0).astype(float) - dm.m4
        ) / n_inf_low

    # m5 = σ̂_{1,m}: influence function for #{K=1,θ=1,d=0} / #{K=1,θ=1}
    if n_inf_high > 0 and not np.isnan(dm.m5):
        G[mask_inf_high, 4] = (
            (d_vals[mask_inf_high] == 0).astype(float) - dm.m5
        ) / n_inf_high

    Omega_hat = G.T @ G

    # Zero out rows/cols for NaN moments → near-zero weight in objective
    missing = np.isnan([dm.m1, dm.m2, dm.m3, dm.m4, dm.m5])
    for j in np.where(missing)[0]:
        Omega_hat[j, :] = 0.0
        Omega_hat[:, j] = 0.0
        Omega_hat[j, j] = 1e12

    Omega_hat += ridge * np.eye(5)

    try:
        W = np.linalg.inv(Omega_hat)
        np.fill_diagonal(W, np.maximum(np.diag(W), 0.0))
        return W
    except np.linalg.LinAlgError:
        diag = np.diag(Omega_hat)
        diag = np.where((diag <= 0) | np.isnan(diag), 1e-6, diag)
        return np.diag(1.0 / diag)


def moment_summary_table(
    data_moments: dict,
    model_moments: dict,
) -> pd.DataFrame:
    """
    Produce a summary table of the active MSM moments — Table 6.

    m₁ and m₂ are excluded (fit by construction). m₃ is the DiD non-disclosure
    premium (NaN for markets without price index coverage). m₅ is shown as an
    overidentifying restriction check.

    Returns
    -------
    pd.DataFrame with columns:
      m3_did_data, m3_did_model, m4_data, m4_model,
      m5_data (overid), m5_model, delta_bar, eq_type
    """
    rows = []
    for m in data_moments:
        dm = data_moments[m]
        mm = model_moments.get(m)
        row = {
            "market_id":    m,
            "m3_did_data":  dm.m3,
            "m3_did_model": mm.m3_model if mm else np.nan,
            "m4_data":      dm.m4,
            "m4_model":     mm.m4_model if mm else np.nan,
            "m5_data":      dm.m5,
            "m5_model":     mm.m5_model if mm else np.nan,
            "delta_bar":    dm.delta_bar,
            "eq_type":      mm.eq_type if mm else "—",
        }
        rows.append(row)
    return pd.DataFrame(rows).set_index("market_id")
