from __future__ import annotations
"""
event_study.py
==============
Identification of ρ_m and c₀_m via a difference-in-differences event study
around the July 2021 DPE reform.

Identification argument
-----------------------
Before July 2021, the DPE (Diagnostic de Performance Énergétique) was not legally
opposable: buyers knew scores could be unreliable and largely discounted them.
After the reform, DPE became legally binding — buyers started trusting and pricing
EPC information. This creates a clean natural experiment:

  Pre-reform  (≤ 2021-06): ρ_m ≈ 0 for all markets
  Post-reform (≥ 2021-07): ρ_m > 0, varying across markets

The panel of hedonic price indices (by EPC category × market × month) provides
a direct estimate of two key structural objects via DiD:

  β₁_m  = DiD_EPC_m  = (p̄_ABC − p̄_EFG)_post − (p̄_ABC − p̄_EFG)_pre   [log pts]
  Δ_m   = DiD_Δ_m    = (p̄_Ø − p̄_EFG)_post   − (p̄_Ø − p̄_EFG)_pre     [log pts]

where p̄_Ø is the undisclosed (no-EPC) category.

Direct estimator of ρ_m (Eq. (eq:premium) adapted)
------------------------------------------
From the model equilibrium:

    Δ_m = ρ_m · β₁_m · e*(σ̂₀_m)

Inverting:

    ρ̂_m = DiD_Δ_m / (DiD_β₁_m · ê*_m)

where ê*_m = (1 − π̂_m)·θ̂_m / [π̂_m·(1 − θ̂_m)·σ̂₀_m + (1 − π̂_m)]
is computed directly from the listings data.

And from the equilibrium condition:

    ĉ₀_m = DiD_Δ_m

EPC category mapping (index file → model)
------------------------------------------
  'Efficient'  → ABC  (θ = 1, high quality)
  'Balanced'   → D    (intermediate, not used in identification)
  'Intensive'  → EFG  (θ = 0, low quality)
  'Missing'    → undisclosed (d = 0)

Reform date: 2021-07-01
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.model import belief_function

logger = logging.getLogger(__name__)

REFORM_DATE     = pd.Timestamp("2021-07-01")
EPC_LABEL_MAP   = {
    "Efficient": "ABC",
    "Balanced" : "D",
    "Intensive": "EFG",
    "Missing"  : "undisclosed",
}


# ---------------------------------------------------------------------------
# Section A — Load and preprocess price indices
# ---------------------------------------------------------------------------

def load_price_indices(
    path: str,
    market_col: str = "cluster_id",
) -> pd.DataFrame:
    """
    Load the hedonic price index file and return a clean long-format DataFrame.

    Expects columns: date, EPC, cluster_id, final_index (base 100 = Oct 2018).

    Returns a DataFrame with columns:
        market_id, date, epc_cat, log_index, post_reform, quarter
    """
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["epc_cat"] = df["EPC"].map(EPC_LABEL_MAP)
    df = df.rename(columns={market_col: "market_id"})
    df["market_id"] = df["market_id"].astype(str)

    # Use log of the hedonic reference price (€/m²) — directly comparable to the
    # listing-price hedonic β₁_m. log(prices) gives the log listing price level
    # per EPC category × market × month, so DiD gaps are in the same units as
    # the hedonic regression coefficients.
    # (final_index is a growth-rate index normalised to 100 at Oct-2018 base;
    #  log(final_index) measures differential appreciation, not the price level.)
    df["log_index"] = np.log(df["prices"])

    df["post_reform"] = (df["date"] >= REFORM_DATE).astype(int)
    df["quarter"]     = df["date"].dt.to_period("Q").astype(str)

    n_markets = df["market_id"].nunique()
    n_months  = df.groupby("market_id")["date"].nunique().median()
    logger.info(
        f"[event_study] Loaded price indices: {n_markets} markets × "
        f"~{n_months:.0f} months  ({df['date'].min().date()} → {df['date'].max().date()})"
    )
    logger.info(
        f"[event_study] Reform date: {REFORM_DATE.date()}  |  "
        f"Pre months: {(df['date'] < REFORM_DATE).sum() // (n_markets * 4):.0f}  "
        f"Post months: {(df['date'] >= REFORM_DATE).sum() // (n_markets * 4):.0f}"
    )
    return df


# ---------------------------------------------------------------------------
# Section B — Market-level DiD estimates
# ---------------------------------------------------------------------------

@dataclass
class DiDEstimates:
    """
    Market-level difference-in-differences estimates from the price index panel.

    Attributes
    ----------
    did          : pd.DataFrame indexed by market_id with columns:
                     beta1_pre, beta1_post, DiD_beta1  — EPC premium (ABC − EFG)
                     delta_pre, delta_post, DiD_delta   — non-disclosure premium (Ø − EFG)
                     n_pre, n_post                      — number of monthly obs per period
    agg_ts       : pd.DataFrame — aggregate time series (mean across markets) by quarter
    reform_date  : pd.Timestamp
    """
    did        : pd.DataFrame
    agg_ts     : pd.DataFrame
    reform_date: pd.Timestamp


def compute_did(
    index_df   : pd.DataFrame,
    pre_end    : str | pd.Timestamp | None = None,
    post_start : str | pd.Timestamp | None = None,
    min_volume : int = 20,
) -> DiDEstimates:
    """
    Compute market-level DiD estimates of β₁_m and Δ_m.

    For each market m:
        β₁_m,t       = log_index_ABC_m,t  − log_index_EFG_m,t
        Δ_m,t        = log_index_Ø_m,t   − log_index_EFG_m,t
        DiD_β₁_m     = mean(β₁_m,t | post) − mean(β₁_m,t | pre)
        DiD_Δ_m      = mean(Δ_m,t  | post) − mean(Δ_m,t  | pre)

    Parameters
    ----------
    index_df   : output of load_price_indices()
    pre_end    : last date of the pre-reform period (default: 2021-06-30)
    post_start : first date of the post-reform period (default: 2021-07-01)
    min_volume : minimum average monthly transaction volume required per EPC
                 category per market in both the pre and post periods.
                 Markets where any category falls below this threshold are
                 excluded. Default: 20.

    Returns
    -------
    DiDEstimates dataclass
    """
    pre_end    = pd.Timestamp(pre_end)    if pre_end    else REFORM_DATE - pd.DateOffset(days=1)
    post_start = pd.Timestamp(post_start) if post_start else REFORM_DATE

    # ── Volume filter: keep only markets where every EPC category has
    #    sufficient average monthly volume in both pre and post periods ────────
    if min_volume > 0 and "volume" in index_df.columns:
        cats_needed = {"ABC", "EFG", "undisclosed"}
        for period_label, mask in [("pre",  index_df["date"] <= pre_end),
                                    ("post", index_df["date"] >= post_start)]:
            avg_vol = (
                index_df.loc[mask]
                .groupby(["market_id", "epc_cat"])["volume"]
                .mean()
                .unstack("epc_cat")
            )
            # Market passes if all required categories meet the threshold
            thin_cats   = avg_vol[list(cats_needed & set(avg_vol.columns))] < min_volume
            thin_markets = thin_cats.any(axis=1)
            n_thin = thin_markets.sum()
            if n_thin > 0:
                keep = thin_markets[~thin_markets].index
                index_df = index_df[index_df["market_id"].isin(keep)]
                logger.info(
                    f"[event_study] Volume filter ({period_label}, min={min_volume}): "
                    f"dropped {n_thin} thin markets, {len(keep)} remain."
                )

    # Pivot to wide: columns = EPC category
    wide = index_df.pivot_table(
        index=["market_id", "date"],
        columns="epc_cat",
        values="log_index",
    ).reset_index()
    wide.columns.name = None

    for col in ["ABC", "EFG", "undisclosed"]:
        if col not in wide.columns:
            raise ValueError(
                f"EPC category '{col}' not found after pivot. "
                f"Available: {[c for c in wide.columns if c not in ('market_id','date')]}"
            )

    # Time-varying log price gaps
    wide["beta1_t"] = wide["ABC"]          - wide["EFG"]   # EPC premium
    wide["delta_t"] = wide["undisclosed"]  - wide["EFG"]   # non-disclosure premium

    pre  = wide[wide["date"] <= pre_end]
    post = wide[wide["date"] >= post_start]

    def _agg(df: pd.DataFrame, suffix: str) -> pd.DataFrame:
        return df.groupby("market_id").agg(
            **{f"beta1_{suffix}": ("beta1_t", "mean"),
               f"delta_{suffix}": ("delta_t", "mean"),
               f"n_{suffix}"    : ("date",     "count")},
        )

    pre_stats  = _agg(pre,  "pre")
    post_stats = _agg(post, "post")

    did = pre_stats.join(post_stats)
    did["DiD_beta1"] = did["beta1_post"] - did["beta1_pre"]
    did["DiD_delta"] = did["delta_post"] - did["delta_pre"]

    # Flag markets with negative DiD_beta1 (can't identify ρ from these)
    n_neg = (did["DiD_beta1"] <= 0).sum()
    if n_neg > 0:
        logger.warning(
            f"[event_study] {n_neg}/{len(did)} markets have DiD_beta1 ≤ 0 "
            "(ABC appreciated less than EFG post-reform). "
            "ρ_m will be set to NaN for these markets."
        )

    # Aggregate time series (mean across markets)
    agg_ts = (
        wide.groupby("date")[["beta1_t", "delta_t"]]
        .mean()
        .rename(columns={"beta1_t": "epc_premium", "delta_t": "nondiscl_premium"})
        .resample("QE").mean()
    )

    logger.info(
        f"[event_study] DiD_beta1 : mean={did['DiD_beta1'].mean():.4f}  "
        f"std={did['DiD_beta1'].std():.4f}  "
        f"[{did['DiD_beta1'].min():.4f}, {did['DiD_beta1'].max():.4f}]"
    )
    logger.info(
        f"[event_study] DiD_delta : mean={did['DiD_delta'].mean():.4f}  "
        f"std={did['DiD_delta'].std():.4f}  "
        f"[{did['DiD_delta'].min():.4f}, {did['DiD_delta'].max():.4f}]"
    )

    return DiDEstimates(did=did, agg_ts=agg_ts, reform_date=REFORM_DATE)


# ---------------------------------------------------------------------------
# Section C — Structural identification of ρ_m and c₀_m
# ---------------------------------------------------------------------------

@dataclass
class EventStudyParams:
    """
    Structural parameters identified from the event study.

    Attributes
    ----------
    rho_m  : pd.Series[market_id → ρ̂_m] — buyer EPC-sensitivity
    c0_m   : pd.Series[market_id → ĉ₀_m] — hiding cost (= DiD_delta in log points)
    beta1_m: pd.Series[market_id → β̂₁_m] — EPC quality premium (= DiD_beta1)
    e_star : pd.Series[market_id → ê*_m]  — equilibrium belief at σ̂₀_m
    details: pd.DataFrame — all intermediate quantities per market
    """
    rho_m  : pd.Series
    c0_m   : pd.Series
    beta1_m: pd.Series
    e_star : pd.Series
    details: pd.DataFrame


def estimate_rho_c0(
    did          : DiDEstimates,
    market_stats : pd.DataFrame,
    market_id_col: str = "market_id",
) -> EventStudyParams:
    """
    Identify ρ_m and c₀_m from the DiD estimates and listings market statistics.

    Estimator
    ---------
        ê*_m  = (1 − π̂_m)·θ̂_m / [π̂_m·(1 − θ̂_m)·σ̂₀_m + (1 − π̂_m)]
        ρ̂_m   = DiD_Δ_m / (DiD_β₁_m · ê*_m)
        ĉ₀_m  = DiD_Δ_m

    Parameters
    ----------
    did          : output of compute_did()
    market_stats : output of data_prep.compute_market_stats(), indexed by market_id
    market_id_col: index name in market_stats (default: "market_id")

    Returns
    -------
    EventStudyParams dataclass
    """
    # Align market_stats index name
    ms = market_stats.copy()
    if ms.index.name != "market_id":
        ms.index.name = "market_id"

    df = did.did.join(ms[["pi_hat", "theta_bar_hat", "sigma_0_hat"]], how="inner")

    n_matched = len(df)
    n_total   = len(did.did)
    if n_matched < n_total:
        logger.warning(
            f"[event_study] {n_total - n_matched} markets in index data have no "
            f"match in market_stats (listings data). "
            f"Proceeding with {n_matched} matched markets."
        )

    # ── Equilibrium belief ê*_m ──────────────────────────────────────────────
    sigma_0 = df["sigma_0_hat"].clip(0.0, 1.0).fillna(1.0)
    pi      = df["pi_hat"].clip(0.0, 1.0)
    theta   = df["theta_bar_hat"].clip(0.0, 1.0)

    df["e_star"] = df.apply(
        lambda r: belief_function(
            float(r["sigma_0_hat"]) if pd.notna(r["sigma_0_hat"]) else 1.0,
            float(r["pi_hat"]),
            float(r["theta_bar_hat"]),
        ),
        axis=1,
    )

    # ── Direct estimator ρ̂_m ─────────────────────────────────────────────────
    denom = df["DiD_beta1"] * df["e_star"]
    # Set ρ = NaN where DiD_beta1 ≤ 0 (not identified) or denominator is near zero
    valid = (df["DiD_beta1"] > 1e-6) & (df["e_star"] > 1e-6)
    df["rho_hat"] = np.where(valid, df["DiD_delta"] / denom, np.nan)

    # Clip to [0, 1] and log out-of-range
    out_of_range = ((df["rho_hat"] < 0) | (df["rho_hat"] > 1)).sum()
    if out_of_range > 0:
        logger.warning(
            f"[event_study] {out_of_range} markets have ρ̂_m outside [0,1] "
            "before clipping — check DiD estimates for these markets."
        )
    df["rho_hat"] = df["rho_hat"].clip(0.0, 1.0)

    # ── c₀_m = DiD_delta (equilibrium hiding cost = observed hiding premium) ──
    df["c0_hat"] = df["DiD_delta"].clip(lower=0.0)

    n_identified = df["rho_hat"].notna().sum()
    logger.info(
        f"[event_study] ρ̂_m identified for {n_identified}/{n_matched} markets  "
        f"mean={df['rho_hat'].mean():.3f}  std={df['rho_hat'].std():.3f}  "
        f"[{df['rho_hat'].min():.3f}, {df['rho_hat'].max():.3f}]"
    )
    logger.info(
        f"[event_study] ĉ₀_m: mean={df['c0_hat'].mean():.4f}  "
        f"std={df['c0_hat'].std():.4f}  "
        f"[{df['c0_hat'].min():.4f}, {df['c0_hat'].max():.4f}]"
    )

    return EventStudyParams(
        rho_m   = df["rho_hat"].rename("rho_m"),
        c0_m    = df["c0_hat"].rename("c0_m"),
        beta1_m = df["DiD_beta1"].rename("beta1_m"),
        e_star  = df["e_star"].rename("e_star"),
        details = df,
    )


# ---------------------------------------------------------------------------
# Section D — Aggregate event study time series (for figures)
# ---------------------------------------------------------------------------

def aggregate_event_study(
    index_df    : pd.DataFrame,
    window_months: int = 36,
) -> pd.DataFrame:
    """
    Compute the aggregate event study coefficients relative to the reform date.

    For each relative month k (from -window_months to +window_months), compute
    the cross-market mean of the log price gaps, normalised so that the last
    pre-reform month (k = -1) equals zero.

    Returns a DataFrame with columns:
        k (relative month), epc_premium, epc_se, epc_ci95,
        nondiscl_premium, nondiscl_se, nondiscl_ci95, n_markets, date
    Suitable for plotting event study figures.
    """
    wide = index_df.pivot_table(
        index=["market_id", "date"],
        columns="epc_cat",
        values="log_index",
    ).reset_index()
    wide.columns.name = None
    wide["beta1_t"] = wide["ABC"]         - wide["EFG"]
    wide["delta_t"] = wide["undisclosed"] - wide["EFG"]

    # Relative month to reform
    wide["k"] = (
        (wide["date"].dt.year  - REFORM_DATE.year) * 12
        + (wide["date"].dt.month - REFORM_DATE.month)
    )
    wide = wide[wide["k"].between(-window_months, window_months)]

    # Normalise: subtract k=-1 value per market
    base = (
        wide[wide["k"] == -1]
        .set_index("market_id")[["beta1_t","delta_t"]]
        .rename(columns={"beta1_t":"b1_base","delta_t":"d_base"})
    )
    wide = wide.join(base, on="market_id")
    wide["beta1_norm"] = wide["beta1_t"] - wide["b1_base"]
    wide["delta_norm"] = wide["delta_t"] - wide["d_base"]

    ts = (
        wide.groupby("k")
        .agg(
            epc_premium      = ("beta1_norm", "mean"),
            epc_se           = ("beta1_norm", "sem"),
            nondiscl_premium = ("delta_norm", "mean"),
            nondiscl_se      = ("delta_norm", "sem"),
            n_markets        = ("market_id",  "nunique"),
        )
        .reset_index()
    )
    ts["date"] = REFORM_DATE + pd.to_timedelta(ts["k"] * 30, unit="D")
    # 95% CI half-widths
    ts["epc_ci95"]      = 1.96 * ts["epc_se"]
    ts["nondiscl_ci95"] = 1.96 * ts["nondiscl_se"]
    return ts