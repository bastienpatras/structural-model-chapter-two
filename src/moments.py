from __future__ import annotations

"""
moments.py
==========
Part 3: Data Moments and Model-Implied Moments
----------------------------------------------
Three moments per market m:
  m₃^data : DiD non-disclosure premium Δ̂_m  (or cross-sectional residual if no DiD)
  m₄^data : hiding rate among informed low-quality sellers  σ̂_{0,m}
  m₅^data : hiding rate among informed high-quality sellers σ̂_{1,m}

m₁ (mean price, disclosed high-quality) and m₂ (mean price, disclosed low-quality)
are dropped: they are fit by construction after residualisation and carry no
information about (ρ_m, c₀).

Identification logic:
  - m₃ (DiD Δ̂_m = ρ_m·β₁_m·ê*): identifies ρ_m given β₁_m from the hedonic.
    Handled upstream in the DiD first stage; here stored for diagnostics.
  - m₄ (σ̂₀_m): identifies c₀ via the equilibrium condition Δ(e*(σ₀*); ρ) = c₀.
    The active moment in the two-step estimator.
  - m₅ (σ̂₁_m ≈ 0): overidentifying restriction (Corollary cor:hq_disclose).
    Stored for model validation; not used in estimation.

Diagnostic (not a moment):
  Δ̄_m = p̄(d=0) − p̄(d=1,θ=0): raw non-disclosure premium, lower bound on c₀.
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
# Section A — Data moments
# ---------------------------------------------------------------------------


@dataclass
class DataMoments:
    """
    Three active data moments for market m.

    m3 : DiD non-disclosure premium Δ̂_m (NaN when DiD coverage absent)
    m4 : σ̂_{0,m} — hiding rate, informed low-quality sellers
    m5 : σ̂_{1,m} — hiding rate, informed high-quality sellers (model: = 0)

    delta_bar : Δ̄_m = p̄(d=0) − p̄(d=1,θ=0), raw non-disclosure premium.
                Diagnostic only — lower bound on c₀ in mixed-strategy markets.
    """

    market_id : str | int
    m3        : float  # DiD Δ̂_m or cross-sectional non-disclosure premium
    m4        : float  # σ̂_{0,m}
    m5        : float  # σ̂_{1,m}  (overid check)
    delta_bar : float = np.nan  # Δ̄_m diagnostic
    var_m3    : float = np.nan
    var_m4    : float = np.nan
    var_m5    : float = np.nan
    n3        : int   = 0
    n4_informed : int = 0
    n5_informed : int = 0


def extract_data_moments(
    df         : pd.DataFrame,
    market_col : str = "market_id",
    hedonic_params = None,
    did_delta  : dict[str | int, float] | None = None,
) -> dict[str | int, DataMoments]:
    """
    Compute data moments from listing-level data for each market.

    Parameters
    ----------
    df             : listing-level DataFrame (log_price, d, K, theta, market_id, group)
    market_col     : market identifier column
    hedonic_params : HedonicParams (optional). When provided, cross-sectional m₃
                     is computed on the residual scale to remove market FE and
                     control variation. Ignored when did_delta is supplied.
    did_delta      : dict {market_id → DiD_Δ_m}. When provided, m₃ is the
                     DiD non-disclosure premium (preferred — removes selection bias).
                     Markets without DiD coverage get m₃ = NaN.

    Returns
    -------
    dict mapping market_id → DataMoments
    """
    df_clean = df[df["group"] != "unverified_disclosers"].copy()

    # Residualize prices for cross-sectional m₃ if hedonic_params supplied
    price_col = "log_price"
    if hedonic_params is not None and did_delta is None:
        hp = hedonic_params
        baseline = df_clean[market_col].map(hp.alpha_m).astype(float)
        for col in hp.cont_controls:
            coef = hp.gamma.get(col, 0.0)
            if coef != 0.0 and col in df_clean.columns:
                baseline += coef * df_clean[col].fillna(0.0)
        for col in hp.cat_controls:
            if col not in df_clean.columns:
                continue
            levels   = df_clean[col].dropna().unique()
            coef_map = {lv: hp.gamma.get(f"C({col})[T.{lv}]", 0.0) for lv in levels}
            baseline += df_clean[col].map(coef_map).fillna(0.0)
        df_clean = df_clean.copy()
        df_clean["_price_resid"] = df_clean["log_price"] - baseline
        price_col = "_price_resid"

    moments = {}

    for m, grp in df_clean.groupby(market_col):
        # Moment 3: non-disclosure premium (DiD preferred, else cross-sectional)
        mask3 = grp["d"] == 0
        n3    = int(mask3.sum())
        if did_delta is not None:
            m3   = did_delta.get(m, np.nan)
            var3 = np.nan
        else:
            m3   = grp.loc[mask3, price_col].mean()
            var3 = grp.loc[mask3, price_col].var() / max(n3, 1)

        # delta_bar: Δ̄_m = p̄(d=0) − p̄(d=1,θ=0)  (raw, diagnostic only)
        mask2     = (grp["d"] == 1) & (grp["K"] == 1) & (grp["theta"] == 0)
        p_bar_low = grp.loc[mask2, price_col].mean()
        p_bar_nd  = grp.loc[mask3, price_col].mean()
        delta_bar = float(p_bar_nd - p_bar_low)

        # Moment 4: hiding rate, informed low-quality sellers
        mask_inf_low  = (grp["K"] == 1) & (grp["theta"] == 0)
        mask_inf_low_h = mask_inf_low & (grp["d"] == 0)
        n_inf_low  = mask_inf_low.sum()
        m4   = mask_inf_low_h.sum() / n_inf_low if n_inf_low > 0 else np.nan
        var4 = (m4 * (1 - m4)) / max(n_inf_low, 1) if not np.isnan(m4) else np.nan

        # Moment 5: hiding rate, informed high-quality sellers (overid: should ≈ 0)
        mask_inf_high  = (grp["K"] == 1) & (grp["theta"] == 1)
        mask_inf_high_h = mask_inf_high & (grp["d"] == 0)
        n_inf_high = mask_inf_high.sum()
        m5   = mask_inf_high_h.sum() / n_inf_high if n_inf_high > 0 else np.nan
        var5 = (m5 * (1 - m5)) / max(n_inf_high, 1) if not np.isnan(m5) else np.nan

        moments[m] = DataMoments(
            market_id   = m,
            m3          = float(m3),
            m4          = float(m4),
            m5          = float(m5),
            delta_bar   = delta_bar,
            var_m3      = float(var3) if not np.isnan(var3) else np.nan,
            var_m4      = float(var4),
            var_m5      = float(var5),
            n3          = n3,
            n4_informed = int(n_inf_low),
            n5_informed = int(n_inf_high),
        )

    return moments


# ---------------------------------------------------------------------------
# Section B — Model-implied moments
# ---------------------------------------------------------------------------


@dataclass
class ModelMoments:
    """
    Three model-implied moments for market m given parameters (ρ_m, c₀).

    m3_model : ρ_m · β₁_m · e*   (structural non-disclosure premium)
    m4_model : σ₀*(ρ_m, c₀)      (equilibrium hiding rate)
    m5_model : 0                  (σ₁* = 0, Corollary cor:hq_disclose)
    """

    market_id    : str | int
    m3_model     : float
    m4_model     : float
    m5_model     : float
    e_star       : float
    sigma_0_star : float
    eq_type      : str


def compute_model_moments(
    rho       : float,
    c0        : float,
    pi        : float,
    theta_bar : float,
    params    : ValuationParams,
    market_id : str | int = "unknown",
) -> ModelMoments:
    """
    Compute model-implied moments for market m given (ρ_m, c₀).

    Algorithm:
    1. Solve equilibrium → (σ₀*, e*).
    2. m₃^model = ρ_m · β₁_m · e*   (structural non-disclosure premium)
    3. m₄^model = σ₀*                (equilibrium hiding rate)
    4. m₅^model = 0                  (high-quality always disclose)
    """
    eq           = solve_equilibrium(rho, c0, pi, theta_bar, params)
    sigma_0_star = eq.sigma_0_star

    return ModelMoments(
        market_id    = market_id,
        m3_model     = float(rho * params.beta_1 * eq.e_star),
        m4_model     = float(sigma_0_star),
        m5_model     = 0.0,
        e_star       = float(eq.e_star),
        sigma_0_star = float(sigma_0_star),
        eq_type      = eq.eq_type,
    )


# ---------------------------------------------------------------------------
# Section C — Moment residuals and weighting matrix (joint MSM mode)
# ---------------------------------------------------------------------------


def moment_residuals(
    data_mom  : DataMoments,
    model_mom : ModelMoments,
) -> np.ndarray:
    """
    Residuals m^data − m^model(ρ, c₀) for the three active moments.

    Returns np.ndarray of shape (3,): [r₃, r₄, r₅]
    """
    r3 = data_mom.m3 - model_mom.m3_model
    r4 = data_mom.m4 - model_mom.m4_model
    r5 = data_mom.m5 - model_mom.m5_model
    return np.array([r3, r4, r5])


def build_weighting_matrix(
    data_moments    : dict[str | int, DataMoments],
    scheme          : str = "inverse_variance",
    df              : pd.DataFrame | None = None,
    market_col      : str = "market_id",
    drop_moments    : list[int] | None = None,
) -> dict[str | int, np.ndarray]:
    """
    Construct the 3×3 GMM weighting matrix W for each market.

    Moment index mapping (0-based within the 3-vector):
      0 → m₃ (non-disclosure premium)
      1 → m₄ (hiding rate)
      2 → m₅ (high-quality hiding rate, overid)

    Schemes:
      "equal" / "identity" : W = I₃
      "inverse_variance"   : W = diag(1/Var(m_j))
      "optimal_gmm"        : W = Ω̂⁻¹  (requires df)

    drop_moments : 0-based indices within the 3-vector to zero out.
    """
    if scheme == "optimal_gmm" and df is None:
        raise ValueError("scheme='optimal_gmm' requires df.")

    df_clean = df[df["group"] != "unverified_disclosers"].copy() if df is not None else None
    drop = list(drop_moments) if drop_moments else []

    weights = {}
    for m, dm in data_moments.items():
        if scheme in ("equal", "identity"):
            W = np.eye(3)

        elif scheme == "inverse_variance":
            vars_ = np.array([dm.var_m3, dm.var_m4, dm.var_m5])
            vars_ = np.where((vars_ <= 0) | np.isnan(vars_), 1e-6, vars_)
            W = np.diag(1.0 / vars_)

        elif scheme == "optimal_gmm":
            grp = df_clean[df_clean[market_col] == m]
            W = _optimal_gmm_weights(grp, dm)

        else:
            raise ValueError(f"Unknown weighting scheme: {scheme!r}")

        for j in drop:
            W[j, :] = 0.0
            W[:, j] = 0.0

        nan_mask = np.isnan([dm.m3, dm.m4, dm.m5])
        for j in np.where(nan_mask)[0]:
            W[j, :] = 0.0
            W[:, j] = 0.0

        weights[m] = W

    return weights


def _optimal_gmm_weights(
    grp  : pd.DataFrame,
    dm   : DataMoments,
    ridge: float = 1e-8,
) -> np.ndarray:
    """
    Compute W_m = Ω̂_m⁻¹ for a single market using the sandwich estimator.

    3×3 influence-function matrix over moments [m₃, m₄, m₅].
    Falls back to diagonal inverse-variance if Ω̂ is singular.
    """
    N = len(grp)
    if N < 6:
        vars_ = np.array([dm.var_m3, dm.var_m4, dm.var_m5])
        vars_ = np.where((vars_ <= 0) | np.isnan(vars_), 1e-6, vars_)
        return np.diag(1.0 / vars_)

    log_price  = grp["log_price"].values
    d_vals     = grp["d"].values
    K_vals     = grp["K"].values
    th_vals    = grp["theta"].values

    mask3         = (d_vals == 0)
    mask_inf_low  = (K_vals == 1) & (th_vals == 0)
    mask_inf_high = (K_vals == 1) & (th_vals == 1)

    n3         = mask3.sum()
    n_inf_low  = mask_inf_low.sum()
    n_inf_high = mask_inf_high.sum()

    G = np.zeros((N, 3))

    if n3 > 0 and not np.isnan(dm.m3):
        G[mask3, 0] = (log_price[mask3] - dm.m3) / n3

    if n_inf_low > 0 and not np.isnan(dm.m4):
        G[mask_inf_low, 1] = (
            (d_vals[mask_inf_low] == 0).astype(float) - dm.m4
        ) / n_inf_low

    if n_inf_high > 0 and not np.isnan(dm.m5):
        G[mask_inf_high, 2] = (
            (d_vals[mask_inf_high] == 0).astype(float) - dm.m5
        ) / n_inf_high

    Omega_hat = G.T @ G

    missing = np.isnan([dm.m3, dm.m4, dm.m5])
    for j in np.where(missing)[0]:
        Omega_hat[j, :] = 0.0
        Omega_hat[:, j] = 0.0
        Omega_hat[j, j] = 1e12

    Omega_hat += ridge * np.eye(3)

    try:
        W = np.linalg.inv(Omega_hat)
        np.fill_diagonal(W, np.maximum(np.diag(W), 0.0))
        return W
    except np.linalg.LinAlgError:
        diag = np.diag(Omega_hat)
        diag = np.where((diag <= 0) | np.isnan(diag), 1e-6, diag)
        return np.diag(1.0 / diag)


# ---------------------------------------------------------------------------
# Section D — Moment summary table (Table 6)
# ---------------------------------------------------------------------------


def moment_summary_table(
    data_moments  : dict,
    model_moments : dict,
) -> pd.DataFrame:
    """
    Produce a summary table of moments — Table 6.

    Columns: m3_data, m3_model, m4_data, m4_model, m5_data, delta_bar, eq_type
    """
    rows = []
    for m in data_moments:
        dm = data_moments[m]
        mm = model_moments.get(m)
        rows.append({
            "market_id" : m,
            "m3_data"   : dm.m3,
            "m3_model"  : mm.m3_model if mm else np.nan,
            "m4_data"   : dm.m4,
            "m4_model"  : mm.m4_model if mm else np.nan,
            "m5_data"   : dm.m5,
            "delta_bar" : dm.delta_bar,
            "eq_type"   : mm.eq_type if mm else "—",
        })
    return pd.DataFrame(rows).set_index("market_id")