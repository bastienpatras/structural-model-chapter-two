"""
rho_identification.py
======================
Point-identified estimator for buyer EPC-sensitivity (rho) and hiding cost (c0),
replacing the market-by-market ratio estimator in event_study.py's
estimate_rho_c0(), which is degenerate: rho_hat = DiD_delta / (DiD_beta1 * e_star)
collapses to ~1 for any true rho_m, because rho_m cancels between numerator and
denominator under the model's own pricing equations (insensitive buyers value
quality identically whether disclosed or hidden, so BOTH the disclosed-H-vs-L gap
and the non-disclosure premium scale by the same rho_m*beta_1 product).

Full derivation: quality_reports/plans/humble-zooming-lovelace.md, Appendix D
(Propositions 1, 2, 4; Corollaries 1.1, 1.2; Lemma 3).

Key results this module implements:
  - Proposition 1: (rho_m, beta_1) are identified ONLY as the product
    b_m = rho_m*beta_1, by any price-based moment, for any number of markets.
    An external, non-price anchor on beta_1 is required -- pooling markets alone
    does not restore identification.
  - Assumption A: an ADEME-consumption-based, non-price anchor for beta_1_m
    (data_prep.compute_energy_anchor + estimate_beta1_anchor below).
  - Proposition 4: given the anchor, rho_m = B_m / beta_1_m^anchor is point
    identified, with the model's rho_m<=1 constraint becoming a TESTABLE
    inequality (B_m <= beta_1_m^anchor) rather than something silently clipped.
    rho_m depends on DiD_beta1 and beta1_anchor ONLY -- not on e_star/sigma_0.
  - Proposition 2(ii): c0_m = B_m * e_star_m(sigma_0_hat) is point identified in
    Partial Pooling WITHOUT needing rho or the anchor at all -- B_m (the
    disclosed-high-vs-low price gap) already IS the rho_m*beta_1 composite, so
    multiplying by the independently-measured e_star_m gives c0_m directly. This
    REPLACES the old c0_hat = rho_hat*DiD_beta1*e_star formula, which (because
    rho_hat = DiD_delta/(DiD_beta1*e_star) by construction) algebraically
    collapses to DiD_delta itself -- i.e. the OLD "structural" c0 estimate was
    just the raw non-disclosure premium (clipped), not a distinct inversion.
  - Corollary 1.1 / Lemma 3: DiD_delta - B_m*e_star_m is an over-identifying
    wedge (lambda_m), not noise to be clipped away -- reported as a diagnostic.

B_m throughout is DiD_beta1_m (the disclosed-high-vs-low DiD price gap) -- see
Phase 0 of the plan for why DiD, not hedonic, beta_1 is the deliberate choice
here (matches eq:c0_estimator's own stated formula; internal consistency with
the rest of the paper's DiD-based identification strategy).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from src.model import belief_function
from src.moments import compute_model_moments
from src.estimation import MSMResult

if TYPE_CHECKING:
    from src.event_study import DiDEstimates
    from src.model import ValuationParams

logger = logging.getLogger(__name__)

# Minimum |DiD_beta1| / |beta1_anchor| treated as identified rather than a
# degenerate near-zero denominator. Shared across both validity checks below.
MIN_BETA1 = 1e-6


# ---------------------------------------------------------------------------
# Assumption A — the energy-cost anchor for beta_1_m
# ---------------------------------------------------------------------------

def estimate_beta1_anchor(
    market_levels: pd.DataFrame,
    energy_anchor: pd.DataFrame,
    p_E          : float,
    r            : float,
    T            : float | None,
    kappa        : float = 1.0,
    price_col    : str = "price_per_m2_eur",
) -> pd.Series:
    """
    Assumption A: external, non-price anchor for beta_1_m -- the capitalised
    energy-cost saving a sensitive buyer attaches to a certified-high-quality vs
    certified-low-quality dwelling.

        beta_1_m = kappa * A_m / P_m
        A_m      = (Ebar_0,m - Ebar_1,m) * p_E * annuity(r, T)
        annuity  = (1 - (1+r)^-T) / r        (perpetuity, 1/r, if T is None)

    Non-price by construction: A_m comes entirely from ADEME-certified
    consumption bands (data_prep.compute_energy_anchor), independent of B_m,
    Delta_m, or rho. Calibration (p_E, r, T) is a national constant for the
    first pass -- market-level variation in beta_1_m comes through each
    market's actual letter-band mix and its price level P_m.

    CAVEAT: the DPE bands (and therefore Ebar_0,m/Ebar_1,m) are in kWh_ep
    (primary energy), not the kWh a household is billed for -- France applies a
    2.3x primary/final conversion factor for electricity specifically, ~1x for
    gas. p_E should be a blended primary-energy-equivalent price reflecting the
    national heating-vector mix, not a plain retail electricity or gas price.
    See quality_reports/plans/humble-zooming-lovelace.md Phase 1 for sourcing
    notes and the calibration sensitivity grid; T in particular is NOT yet
    locked (see native memory rho_anchor_calibration.md) -- treat any single
    point estimate from this function as provisional until T is sourced from
    actual property holding-period data.

    Parameters
    ----------
    market_levels : indexed by market_id, must carry `price_col`
                     (output of data_prep.compute_market_levels)
    energy_anchor : indexed by market_id, columns e_bar_0_kwh, e_bar_1_kwh
                     (output of data_prep.compute_energy_anchor)
    p_E           : blended primary-energy-equivalent price, EUR/kWh
    r             : discount rate; must be > 0
    T             : horizon in years; None = perpetuity (annuity = 1/r)
    kappa         : sensitivity scale, default 1.0 (baseline)
    price_col     : column in market_levels giving local price per m^2

    Returns
    -------
    pd.Series indexed by market_id: beta_1_m^anchor (NaN where the consumption
    gap is non-positive, price is missing/non-positive, or the join drops the
    market)
    """
    if r <= 0:
        raise ValueError(f"estimate_beta1_anchor: discount rate r must be > 0, got {r}")

    annuity = (1.0 / r) if T is None else (1 - (1 + r) ** (-T)) / r

    n_before = len(energy_anchor)
    joined = energy_anchor.join(market_levels[[price_col]], how="inner")
    if len(joined) < n_before:
        logger.warning(
            f"[rho_identification] energy_anchor/market_levels join dropped "
            f"{n_before - len(joined)}/{n_before} markets (index mismatch)."
        )

    gap = joined["e_bar_0_kwh"] - joined["e_bar_1_kwh"]
    n_nonpos_gap = (gap <= 0).sum()
    if n_nonpos_gap > 0:
        logger.warning(
            f"[rho_identification] {n_nonpos_gap} markets have Ebar_0<=Ebar_1 "
            "(non-positive consumption gap) -- beta1_anchor set to NaN there."
        )
    gap = gap.where(gap > 0, np.nan)

    price = joined[price_col].where(joined[price_col] > 0, np.nan)
    n_nonpos_price = (joined[price_col] <= 0).sum()
    if n_nonpos_price > 0:
        logger.warning(
            f"[rho_identification] {n_nonpos_price} markets have {price_col}<=0 "
            "-- beta1_anchor set to NaN there."
        )

    a_m = gap * p_E * annuity
    beta1_anchor = (kappa * a_m / price).rename("beta1_anchor")

    finite_or_nan = beta1_anchor.isna() | np.isfinite(beta1_anchor)
    if not finite_or_nan.all():
        n_bad = (~finite_or_nan).sum()
        logger.warning(f"[rho_identification] {n_bad} non-finite (inf) beta1_anchor values -- set to NaN.")
        beta1_anchor = beta1_anchor.where(finite_or_nan, np.nan)

    logger.info(
        f"[rho_identification] beta1_anchor: annuity={annuity:.2f}  "
        f"n={beta1_anchor.notna().sum()}/{len(beta1_anchor)}  "
        f"mean={beta1_anchor.mean():.4f}  median={beta1_anchor.median():.4f}"
    )
    return beta1_anchor


# ---------------------------------------------------------------------------
# Anchored rho_m / c0_m estimator
# ---------------------------------------------------------------------------

@dataclass
class AnchoredResult:
    """
    Attributes
    ----------
    rho_m           : pd.Series[market_id -> rho_hat_m], the ANCHORED, point-
                       identified estimate (Proposition 4) = DiD_beta1_m /
                       beta1_anchor_m. Depends on DiD_beta1 and beta1_anchor
                       ONLY (not on e_star/sigma_0_hat). NOT clipped to [0,1];
                       use n_violate_bound / the raw values to see the
                       testable-inequality violations directly.
    c0_m            : pd.Series[market_id -> c0_hat_m] = B_m * e_star_m
                       (Proposition 2(ii)) -- independent of rho_m and of the
                       anchor; identified whenever B_m > 0 and e_star_m is
                       defined (not NaN). Where a market has no informed
                       low-quality sellers (sigma_0_hat is NaN in market_stats),
                       e_star is imputed at the worst-case sigma_0=1 (max
                       hiding) -- see `sigma0_imputed` in `details` to identify
                       and, if desired, exclude these markets downstream.
    beta1_anchor    : pd.Series[market_id -> beta_1_m^anchor] used as rho's
                       denominator.
    lambda_m        : pd.Series[market_id -> DiD_delta_m - B_m*e_star_m], the
                       measured over-identification wedge (Lemma 3).
    j_stat          : simple one-sample t-statistic for H0: mean(lambda_m)=0
                       (NOT an optimal-GMM J-test; a lightweight diagnostic --
                       refine with a proper weighting matrix before reporting
                       in the paper as a formal specification test).
    concentration   : Lambda_bar' = mean(rho_m*(1-rho_m)) over markets with
                       rho_m in [0,1] only -- near zero means the sample is too
                       saturated to identify a covariate index (section 2.2 of
                       the derivation); only meaningful on that restricted set.
    n_violate_bound : count of markets with rho_m > 1 (B_m > beta1_anchor_m) --
                       the testable inequality Proposition 4 makes available;
                       report this directly rather than silently clipping.
    n_total         : total markets with a defined rho_m (B_m>0 and
                       beta1_anchor>0).
    details         : pd.DataFrame, all intermediate per-market quantities,
                       including `sigma0_imputed` (bool: True where sigma_0_hat
                       was missing and e_star used the sigma_0=1 fallback).
    """
    rho_m          : pd.Series
    c0_m           : pd.Series
    beta1_anchor   : pd.Series
    lambda_m       : pd.Series
    j_stat         : float
    concentration  : float
    n_violate_bound: int
    n_total        : int
    details        : pd.DataFrame


def _empty_anchored_result(details: pd.DataFrame) -> AnchoredResult:
    empty = pd.Series(dtype=float)
    return AnchoredResult(
        rho_m=empty.rename("rho_m"), c0_m=empty.rename("c0_m"),
        beta1_anchor=empty.rename("beta1_anchor"), lambda_m=empty.rename("lambda_m"),
        j_stat=np.nan, concentration=np.nan, n_violate_bound=0, n_total=0, details=details,
    )


def estimate_rho_c0_anchored(
    did          : "DiDEstimates",
    market_stats : pd.DataFrame,
    beta1_anchor : pd.Series,
) -> AnchoredResult:
    """
    Point-identified (rho_m, c0_m), given an external beta_1_m^anchor.

    Parameters
    ----------
    did          : output of event_study.compute_did() -- did.did carries
                   DiD_beta1, DiD_delta per market_id
    market_stats : output of data_prep.compute_market_stats(), indexed by
                   market_id, must carry pi_hat, theta_bar_hat, sigma_0_hat
    beta1_anchor : output of estimate_beta1_anchor(), indexed by market_id

    Returns
    -------
    AnchoredResult
    """
    ms = market_stats.copy()
    if ms.index.name != "market_id":
        logger.warning(
            f"[rho_identification] market_stats index name was {ms.index.name!r}; "
            "assuming it is market_id."
        )
        ms.index.name = "market_id"
    assert ms.index.is_unique, "market_stats index has duplicate market_id values"

    n_before = len(did.did)
    df = (
        did.did[["DiD_beta1", "DiD_delta"]]
        .join(ms[["pi_hat", "theta_bar_hat", "sigma_0_hat"]], how="inner")
        .join(beta1_anchor.rename("beta1_anchor"), how="inner")
    )
    if len(df) < n_before:
        logger.warning(
            f"[rho_identification] did/market_stats/beta1_anchor join dropped "
            f"{n_before - len(df)}/{n_before} markets (index mismatch)."
        )

    if df.empty:
        logger.warning("[rho_identification] no markets survived the join(s); returning empty AnchoredResult.")
        return _empty_anchored_result(df)

    # sigma_0_hat is NaN when a market has no informed low-quality sellers
    # (data_prep.compute_market_stats). Imputing sigma_0=1 (worst case, max
    # hiding) lets e_star/c0_m still be computed there, but it is an
    # assumption, not a measured value -- flag it explicitly rather than
    # letting it disappear into the arithmetic.
    df["sigma0_imputed"] = df["sigma_0_hat"].isna()
    n_sigma0_missing = int(df["sigma0_imputed"].sum())
    if n_sigma0_missing > 0:
        logger.warning(
            f"[rho_identification] {n_sigma0_missing}/{len(df)} markets have "
            "sigma_0_hat=NaN (no informed low-quality sellers) -- imputing the "
            "worst-case sigma_0=1 (max hiding) for e_star; c0_m/lambda_m for "
            "these markets rest on that assumption, not a measured value "
            "(see details['sigma0_imputed'])."
        )
    sigma_0_filled = df["sigma_0_hat"].fillna(1.0)

    df["e_star"] = [
        belief_function(float(s), float(pi), float(th))
        for s, pi, th in zip(sigma_0_filled, df["pi_hat"], df["theta_bar_hat"])
    ]

    # rho_m -- Proposition 4. Depends on DiD_beta1 and beta1_anchor ONLY; does
    # NOT require e_star to be defined (unlike the old ratio estimator this
    # replaces). NOT clipped -- report violations via n_violate_bound instead.
    rho_valid_mask = (df["DiD_beta1"] > MIN_BETA1) & (df["beta1_anchor"] > MIN_BETA1)
    n_rho_dropped = int((~rho_valid_mask).sum())
    if n_rho_dropped > 0:
        logger.warning(
            f"[rho_identification] {n_rho_dropped}/{len(df)} markets excluded from "
            "rho_m (DiD_beta1<=0 or beta1_anchor undefined/non-positive)."
        )
    df["rho_m"] = np.where(rho_valid_mask, df["DiD_beta1"] / df["beta1_anchor"], np.nan)

    # c0_m -- Proposition 2(ii). Independent of rho_m/beta1_anchor: B_m already
    # IS the rho_m*beta_1 composite, so B_m*e_star gives c0_m directly.
    c0_valid = (df["DiD_beta1"] > MIN_BETA1) & (df["e_star"] > 0)
    n_c0_dropped = int((~c0_valid).sum())
    if n_c0_dropped > 0:
        logger.warning(
            f"[rho_identification] {n_c0_dropped}/{len(df)} markets excluded from "
            "c0_m (DiD_beta1<=0 or e_star<=0)."
        )
    df["c0_m"] = np.where(c0_valid, df["DiD_beta1"] * df["e_star"], np.nan)

    # lambda_m -- the over-identifying wedge (Lemma 3 / Corollary 1.1).
    df["lambda_m"] = np.where(c0_valid, df["DiD_delta"] - df["c0_m"], np.nan)

    lam = df["lambda_m"].dropna()
    if len(lam) > 1 and lam.std(ddof=1) > 0:
        j_stat = float(lam.mean() / (lam.std(ddof=1) / np.sqrt(len(lam))))
    else:
        j_stat = np.nan

    rho_valid = df["rho_m"].dropna()
    rho_in_bounds = rho_valid[(rho_valid >= 0) & (rho_valid <= 1)]
    concentration = float((rho_in_bounds * (1 - rho_in_bounds)).mean()) if len(rho_in_bounds) > 0 else np.nan

    n_violate = int((df["rho_m"] > 1).sum())
    n_total   = int(df["rho_m"].notna().sum())

    logger.info(
        f"[rho_identification] anchored rho_m: n={n_total}  "
        f"mean={df['rho_m'].mean():.3f}  median={df['rho_m'].median():.3f}  "
        f"violate(rho>1)={n_violate}/{n_total}  concentration={concentration:.4f}  "
        f"lambda_m mean={lam.mean() if len(lam) else float('nan'):.4f} (t={j_stat:.2f})"
    )

    return AnchoredResult(
        rho_m           = df["rho_m"].rename("rho_m"),
        c0_m            = df["c0_m"].rename("c0_m"),
        beta1_anchor    = df["beta1_anchor"].rename("beta1_anchor"),
        lambda_m        = df["lambda_m"].rename("lambda_m"),
        j_stat          = j_stat,
        concentration   = concentration,
        n_violate_bound = n_violate,
        n_total         = n_total,
        details         = df,
    )


# ---------------------------------------------------------------------------
# Bridge to the existing pipeline's MSMResult
# ---------------------------------------------------------------------------

def build_msm_result_from_anchored(
    anchored     : AnchoredResult,
    market_stats : pd.DataFrame,
    market_params: dict,
) -> MSMResult:
    """
    Package an AnchoredResult as an MSMResult, so it can be passed anywhere
    the existing pipeline (compute_market_subsidies, compute_subsidy_grid,
    produce_all_outputs, ...) expects estimate_msm()'s output.

    Deliberately does NOT route through estimate_msm(fix_rho=True) -- that
    function recomputes c0_hat = rho_hat*beta1_m*e_star internally
    (estimation.py:353), which would silently reintroduce a rho-dependence
    into c0 if fed the anchored rho_m as rho_init (Proposition 2(ii) says c0_m
    should NOT depend on rho at all). Instead, rho_hat/c0_hat are taken
    directly from `anchored`, and only the regime classification
    (eq_types/model_moments, needed for Table 4/figure grouping downstream) is
    computed via the existing compute_model_moments() helper -- reusing
    market_params[m] (whose beta_1 is already DiD_beta1_m, i.e. B_m, per Phase
    0's fix) with beta_1 swapped to beta1_anchor_m and rho set to the reported
    anchored rho_m, so the internal trace is consistent with what's actually
    reported. The regime/eq_star/sigma_0_star outputs are provably invariant
    to this rho/beta1 decomposition (Corollary 1.2) as long as the product
    rho_m*beta_1 equals B_m -- which it does by construction (rho_m =
    B_m/beta1_anchor_m) -- so this is not an approximation.

    Q_star is set to 0.0, matching the existing convention for the two-step
    (non-optimised) estimator (estimation.py:373) -- this is a closed-form
    inversion, not a fitted objective, under either estimator.

    Parameters
    ----------
    anchored      : output of estimate_rho_c0_anchored()
    market_stats  : indexed by market_id, must carry pi_hat, theta_bar_hat
    market_params : {market_id: ValuationParams}, output of
                    build_valuation_params() with did_beta1 passed (Phase 0)

    Returns
    -------
    MSMResult, with rho_hat/c0_hat from `anchored` and eq_types/model_moments
    computed consistently for regime classification. rho_se/c0_se are left
    empty (populate via a bootstrap over this estimator separately, not yet
    implemented -- see plan file Phase 2 verification section).
    """
    markets = list(anchored.rho_m.dropna().index)
    missing_params = [m for m in markets if m not in market_params]
    if missing_params:
        logger.warning(
            f"[rho_identification] {len(missing_params)} markets have an anchored "
            "rho_m but no entry in market_params -- excluded from the MSMResult."
        )
        markets = [m for m in markets if m in market_params]

    rho_hat: dict = {}
    c0_hat: dict = {}
    model_moments_hat: dict = {}
    eq_types: dict = {}

    for m in markets:
        rho_m = float(anchored.rho_m[m])
        c0_m  = float(anchored.c0_m[m]) if pd.notna(anchored.c0_m.get(m, np.nan)) else np.nan
        rho_hat[m] = rho_m
        c0_hat[m]  = c0_m

        if pd.isna(c0_m):
            continue  # can't classify a regime without a defined c0_m

        pi_m = float(market_stats.loc[m, "pi_hat"])
        th_m = float(market_stats.loc[m, "theta_bar_hat"])
        params_m: "ValuationParams" = replace(market_params[m], beta_1=float(anchored.beta1_anchor[m]))
        mm = compute_model_moments(
            rho=rho_m, c0=c0_m, pi=pi_m, theta_bar=th_m, params=params_m, market_id=m,
        )
        model_moments_hat[m] = mm
        eq_types[m]          = mm.eq_type

    logger.info(
        f"[rho_identification] MSMResult (anchored): {len(rho_hat)} markets  "
        f"c0_hat mean={np.nanmean(list(c0_hat.values())):.6f}  "
        f"rho_hat mean={np.nanmean(list(rho_hat.values())):.4f}"
    )

    return MSMResult(
        rho_hat       = rho_hat,
        c0_hat        = c0_hat,
        Q_star        = 0.0,
        n_markets     = len(rho_hat),
        model_moments = model_moments_hat,
        eq_types      = eq_types,
        converged     = True,
        message       = "anchored point-identified estimator (Assumption A / Propositions 2(ii), 4)",
    )
