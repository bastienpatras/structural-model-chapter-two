"""Estimate the limited-attention-to-silence extension (paper Section 4.6) and export its numbers.

Every number quoted in Section 4.6 and Appendix A-ATT is computed here and written as a LaTeX
macro, so the paper never hard-codes them (single source of truth).

Inputs (all produced by the main pipeline or tracked in the repo):
  results/{apartment,house}/anchored_diagnostics.csv   market DiDs and registry moments
  data/listings_enriched_{APARTMENT,HOUSE}.parquet      registry letters (K=1) for the energy ratio
  data/index_{APARTMENT,HOUSE}.csv                      Chapter-1 group indices (levels, yearly windows)

Outputs:
  results/attention/{apartment,house}_markets.csv       per-market objects
  results/attention/summary.csv                         one row per segment x statistic
  results/attention/bootstrap_psi.csv                   bootstrap draws of the spillover estimate
  results/tables/attention_macros.tex                   \\newcommand macros used by the paper
  results/tables/table_attention_body.tex               tabular of Table tab:attention (caption and notes stay in the paper)

Aggregation rule (design item M6): the energy objects (eta, e, theta_bar, pi, e(1), kWh units) are
cross-market means weighted by the energy-efficiency premium, the weights implied by the
ratio-of-sums estimator
    1 - psi = sum_m lambda_m / sum_m x_m,   x_m = beta1_m (eta_m - e_m).
Premia, wedges and counts are simple cross-market means, as in Table tab:did_results. Under this rule
the point estimate equals the upper end of the identified interval at C^def = 0 and the fitted
premium equals the mean premium; both are identities of the aggregation (checked below as code
self-consistency, not as evidence). The informative check is market by market (share_in_band).

Values are provisional: eta uses DPE band midpoints (G = 500 kWh) and K is the current registry
match. Re-run after the certificate-date and certified-consumption re-pulls.

Usage
-----
    python scripts/compute_attention.py            # estimate and write all outputs
    python scripts/compute_attention.py --stub     # write [XX] placeholder macros only
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_prep import DPE_BAND_MIDPOINT_KWH_M2_YR, compute_energy_anchor  # noqa: E402
from src.event_study import load_price_indices  # noqa: E402

logger = logging.getLogger("compute_attention")

SEED: int = 20261008
N_BOOT: int = 4999
SEGMENTS: dict[str, str] = {"APARTMENT": "Apt", "HOUSE": "House"}
LISTING_YEARS: tuple[int, int] = (2022, 2024)          # structural sample, as in the pipeline
WINDOWS: dict[str, tuple[str, str]] = {                 # Section 4.4 windows
    "pre": ("2018-10-01", "2021-06-30"),
    "post": ("2021-07-01", "2024-07-31"),
    "Yone": ("2021-07-01", "2022-06-30"),
    "Ytwo": ("2022-07-01", "2023-06-30"),
    "Ythree": ("2023-07-01", "2024-07-31"),
}
HIGH_LETTERS: tuple[str, ...] = ("A", "B", "C", "D")    # epc_threshold 4.0 in both configs
PARITY_TOL: float = 0.006                               # log points: 2-decimal rounding of the reference values


# --------------------------------------------------------------------------------------------
# Data assembly
# --------------------------------------------------------------------------------------------
def load_registry(segment: str) -> pd.DataFrame:
    """Listings of the structural sample with registry match, one row per listing_id."""
    cols = ["listing_id", "market_id", "K", "d", "ademe_epc_score", "ademe_epc_letter", "start_date"]
    df = pd.read_parquet(ROOT / "data" / f"listings_enriched_{segment}.parquet", columns=cols)
    years = pd.to_datetime(df["start_date"]).dt.year
    df = df[years.between(*LISTING_YEARS)].drop_duplicates("listing_id")
    return df


def energy_ratio(registry: pd.DataFrame, g_midpoint: float | None = None) -> pd.DataFrame:
    """Per-market mean consumption by quality and the energy-cost ratio eta_m (eq:eta)."""
    mids = dict(DPE_BAND_MIDPOINT_KWH_M2_YR)
    if g_midpoint is not None:
        mids[7] = g_midpoint
    en = compute_energy_anchor(registry, band_midpoints=mids).reset_index()
    en["market_id"] = en["market_id"].astype(str)
    en["eta"] = en["e_bar_0_kwh"] / (en["e_bar_0_kwh"] - en["e_bar_1_kwh"])
    return en[["market_id", "e_bar_0_kwh", "e_bar_1_kwh", "eta"]]


def market_panel(segment: str, registry: pd.DataFrame) -> pd.DataFrame:
    """Estimation-sample markets with DiDs (log points), registry moments and eta_m."""
    est = pd.read_csv(ROOT / "results" / segment.lower() / "anchored_diagnostics.csv")
    est["market_id"] = est["market_id"].astype(str)
    m = est.merge(energy_ratio(registry), on="market_id", how="inner", validate="one_to_one")
    if len(m) != len(est):
        raise ValueError(f"{segment}: energy ratio missing for {len(est) - len(m)} markets")
    m["b1"] = 100.0 * m["DiD_beta1"]                    # log points
    m["dl"] = 100.0 * m["DiD_delta"]
    m["c0"] = 100.0 * m["c0_m"]
    m["e"] = m["e_star"]
    m["lam"] = m["dl"] - m["b1"] * m["e"]               # over-identifying wedge
    m["x"] = m["b1"] * (m["eta"] - m["e"])              # eq:att_lambda regressor
    m["slack"] = m["eta"] * m["b1"] - m["dl"]           # bound Delta/b <= eta
    th, pi = m["theta_bar_hat"], m["pi_hat"]
    m["e_one"] = (1 - pi) * th / (1 - pi * th)          # e(sigma0 = 1)
    m["share_uninf"] = (1 - pi) / (pi * (1 - th) * m["sigma_0_hat"] + (1 - pi))
    return m


def window_gaps(segment: str, markets: pd.Index) -> dict[str, pd.DataFrame]:
    """Mean level gaps B (A-D minus E-G) and D (silent minus E-G), log points, by window."""
    idx = load_price_indices(str(ROOT / "data" / f"index_{segment}.csv"), high_group="ABCD")
    idx = idx[idx["market_id"].astype(str).isin(markets)]
    w = idx.pivot_table(index=["market_id", "date"], columns="epc_cat", values="log_index").reset_index()
    w["market_id"] = w["market_id"].astype(str)
    w["B"] = 100.0 * (w["ABC"] - w["EFG"])
    w["D"] = 100.0 * (w["undisclosed"] - w["EFG"])
    return {k: w[(w["date"] >= a) & (w["date"] <= b)].groupby("market_id")[["B", "D"]].mean()
            for k, (a, b) in WINDOWS.items()}


# --------------------------------------------------------------------------------------------
# Estimators
# --------------------------------------------------------------------------------------------
def psi_rom(lam: pd.Series, x: pd.Series) -> float:
    """Ratio-of-means estimator: 1 - psi = sum lambda / sum x."""
    return 1.0 - lam.sum() / x.sum()


def psi_ols(lam: pd.Series, x: pd.Series, const: bool = False) -> tuple[float, float, float, float]:
    """Regression of lambda on x (through the origin unless const). Returns psi, se, intercept, se."""
    X = sm.add_constant(x.rename("x")) if const else x.rename("x").to_frame()
    r = sm.OLS(lam, X).fit(cov_type="HC1")
    icpt = (r.params["const"], r.bse["const"]) if const else (np.nan, np.nan)
    return 1.0 - r.params["x"], r.bse["x"], icpt[0], icpt[1]


def bootstrap_rom(lam: np.ndarray, x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Market bootstrap of the ratio-of-means estimator."""
    n = len(lam)
    draws = rng.integers(0, n, size=(N_BOOT, n))
    return 1.0 - lam[draws].sum(axis=1) / x[draws].sum(axis=1)


def wmean(v: pd.Series, w: pd.Series) -> float:
    """Premium-weighted mean (the aggregation rule)."""
    return float((v * w).sum() / w.sum())


# --------------------------------------------------------------------------------------------
# Per-segment estimation
# --------------------------------------------------------------------------------------------
def estimate_segment(segment: str, rng: np.random.Generator) -> tuple[dict, pd.DataFrame, np.ndarray]:
    registry = load_registry(segment)
    m = market_panel(segment, registry)
    n = len(m)
    w = m["b1"]                                         # aggregation weights
    s: dict[str, float] = {"n_markets": n}

    # Paper parity (Table tab:did_results)
    s.update(b1=m["b1"].mean(), dl=m["dl"].mean(), lam=m["lam"].mean(), c0_base=m["c0"].mean())
    s["lam_t"] = m["lam"].mean() / (m["lam"].std(ddof=1) / np.sqrt(n))

    # Aggregates under the single rule
    r = m["dl"].sum() / m["b1"].sum()
    eta_w, e_w = wmean(m["eta"], w), wmean(m["e"], w)
    unit_w = wmean(m["e_bar_0_kwh"] - m["e_bar_1_kwh"], w)          # kWh per unit of the quality scale
    psi = psi_rom(m["lam"], m["x"])
    if not np.isclose(psi, 1.0 - (r - e_w) / (eta_w - e_w)):
        raise AssertionError("ratio-of-means estimate does not match the weighted-aggregate form")
    s.update(ratio=r, eta_w=eta_w, eta_mean=m["eta"].mean(), e_w=e_w, psi=psi)
    s["c_star_kwh"] = (eta_w - r) * unit_w                         # perceived cost of silence
    s["c_sil_kwh"] = (eta_w - e_w) * unit_w                        # rational cost of the silent pool
    s["interval_hi"] = s["c_star_kwh"] / s["c_sil_kwh"]            # psi at C^def = 0
    if not np.isclose(s["interval_hi"], psi):                      # code self-consistency (identity)
        raise AssertionError("identified-interval upper end differs from the point estimate")

    boot = bootstrap_rom(m["lam"].to_numpy(), m["x"].to_numpy(), rng)
    draws = rng.integers(0, n, size=(N_BOOT, n))                   # perceived cost of silence, kWh
    bw = m["b1"].to_numpy()[draws]
    r_b = m["dl"].to_numpy()[draws].sum(1) / bw.sum(1)
    eta_b = (m["eta"].to_numpy()[draws] * bw).sum(1) / bw.sum(1)
    unit_b = ((m["e_bar_0_kwh"] - m["e_bar_1_kwh"]).to_numpy()[draws] * bw).sum(1) / bw.sum(1)
    cstar_b = (eta_b - r_b) * unit_b
    s["c_star_se"] = cstar_b.std(ddof=1)
    s["c_star_lo"], s["c_star_hi"] = np.percentile(cstar_b, [2.5, 97.5])
    s["psi_se"] = boot.std(ddof=1)
    s["psi_lo"], s["psi_hi"] = np.percentile(boot, [2.5, 97.5])
    s["t_full"] = (1.0 - psi) / s["psi_se"]

    s["psi_ols"], s["psi_ols_se"], _, _ = psi_ols(m["lam"], m["x"])
    s["psi_const"], _, s["icpt"], s["icpt_se"] = psi_ols(m["lam"], m["x"], const=True)
    s["psi_med"] = float(np.median(1.0 - m["lam"] / m["x"]))

    # Bound Delta/b <= eta, market by market
    s["slack"] = m["slack"].mean()
    s["slack_t"] = m["slack"].mean() / (m["slack"].std(ddof=1) / np.sqrt(n))
    viol = m["slack"] < 0
    s["n_viol"] = int(viol.sum())
    top = m["b1"] >= m["b1"].quantile(2 / 3)
    s["share_viol_top"] = 100.0 * float(viol[top].mean())
    bottom = m["b1"] <= m["b1"].quantile(1 / 3)
    s["share_viol_bottom"] = 100.0 * float(viol[bottom].mean())
    s["n_d_gt_b"] = int((m["dl"] > m["b1"]).sum())

    # Partial Pooling band at the aggregate (Corollary cor:att_band); design item M6(b)
    b_bar = m["b1"].mean()
    th_w, e1_w = wmean(m["theta_bar_hat"], w), wmean(m["e_one"], w)
    # Where silence sits among ratings (Proposition att_seller_types): threshold psi_bar(e) = (e_def - 1) / (e_def - e), C_def = 0
    psi_bar = lambda e: (eta_w - 1.0) / (eta_w - e)
    s["psi_bar_e"], s["psi_bar_one"], s["psi_bar_theta"] = psi_bar(e_w), psi_bar(e1_w), psi_bar(th_w)
    s["n_between"] = int(((m["dl"] > 0) & (m["dl"] <= m["b1"])).sum())          # silent between a bad and a good rating
    s["band_lo"] = b_bar * (psi * e1_w + (1 - psi) * eta_w)
    s["band_hi"] = b_bar * (psi * th_w + (1 - psi) * eta_w)
    s["band_width"] = s["band_hi"] - s["band_lo"]
    s["band_width_base"] = b_bar * (th_w - e1_w)
    s["fitted_premium"] = b_bar * (psi * e_w + (1 - psi) * eta_w)
    if not s["band_lo"] - 1e-9 <= s["fitted_premium"] <= s["band_hi"] + 1e-9:   # identity of aggregation
        raise AssertionError("fitted premium outside the Partial Pooling band")
    # Informative version: market by market, with the common psi
    lo_m = m["b1"] * (psi * m["e_one"] + (1 - psi) * m["eta"])
    hi_m = m["b1"] * (psi * m["theta_bar_hat"] + (1 - psi) * m["eta"])
    s["share_in_band"] = 100.0 * float(((m["dl"] >= lo_m) & (m["dl"] <= hi_m)).mean())

    # Decomposition of the wedge and the belief-channel bound (Section 4.6.1)
    s["excess"] = (m["dl"] - m["b1"]).mean()
    s["reach"] = ((1 - m["e"]) * m["b1"]).mean()
    s["share_uninf"] = 100.0 * m["share_uninf"].mean()
    s["cursed"] = (m["b1"] * (m["theta_bar_hat"] - m["e"])).mean()

    # Sensitivity of psi to the registry belief and to eta (at the aggregate)
    s["sens_e"] = (eta_w - r) / (eta_w - e_w) ** 2
    s["sens_eta"] = (r - e_w) / (eta_w - e_w) ** 2

    # Hiding by grade in the registry (A-D vs E-G)
    k1 = registry[(registry["K"] == 1) & registry["market_id"].astype(str).isin(m["market_id"])]
    hi = k1["ademe_epc_letter"].isin(HIGH_LETTERS)
    s["sigma_one"] = 100.0 * float((k1.loc[hi, "d"] == 0).mean())
    s["sigma_zero"] = 100.0 * float((k1.loc[~hi, "d"] == 0).mean())

    # Policy objects
    s["salience"] = s["dl"] - (m["b1"] * m["e"]).mean()           # = mean lambda
    s["enforce_sil"] = psi * b_bar * (th_w - e_w)
    s["high_loss"] = (m["b1"] - m["dl"]).mean()

    # Levels and yearly windows from the index panel
    g = window_gaps(segment, pd.Index(m["market_id"]))
    pre, post = g["pre"], g["post"]
    did = (post - pre).reindex(m["market_id"])
    if not (np.allclose(did["B"].to_numpy(), m["b1"].to_numpy(), atol=1e-6)
            and np.allclose(did["D"].to_numpy(), m["dl"].to_numpy(), atol=1e-6)):
        raise AssertionError("index-panel DiD does not reproduce DiD_beta1 / DiD_delta")
    s["level_gap_pre"] = (pre["D"] - pre["B"]).mean()
    s["level_gap_post"] = (post["D"] - post["B"]).mean()
    mi = m.set_index("market_id")
    lev = post.reindex(mi.index)
    s["psi_lev_rom"] = 1.0 - (lev["D"].mean() / lev["B"].mean() - mi["e"].mean()) / (mi["eta"].mean() - mi["e"].mean())
    slope = sm.OLS(lev["D"], sm.add_constant(lev["B"])).fit().params["B"]
    s["psi_lev_slope"] = (mi["eta"].mean() - slope) / (mi["eta"].mean() - mi["e"].mean())
    for k in ("Yone", "Ytwo", "Ythree"):
        b1k = (g[k]["B"] - pre["B"]).reindex(mi.index)
        dlk = (g[k]["D"] - pre["D"]).reindex(mi.index)
        s[f"one_minus_psi_{k}"] = 1.0 - psi_rom(dlk - b1k * mi["e"], b1k * (mi["eta"] - mi["e"]))

    # Sensitivity to the open-ended G band
    for gmid, tag in ((420.0, "Gfourtwenty"), (600.0, "Gsixhundred")):
        alt = m.drop(columns=["eta", "e_bar_0_kwh", "e_bar_1_kwh"]).merge(
            energy_ratio(registry, gmid), on="market_id", how="inner", validate="one_to_one")
        x_alt = alt["b1"] * (alt["eta"] - alt["e"])
        s[f"psi_{tag}"] = psi_rom(alt["lam"], x_alt)
        s[f"n_viol_{tag}"] = int(((alt["eta"] * alt["b1"] - alt["dl"]) < 0).sum())

    # Parity with the paper (Table tab:did_results)
    paper = {"APARTMENT": (4.06, 8.53, 6.12, 2.41), "HOUSE": (5.82, 3.89, 0.44, 3.45)}[segment]
    got = (s["b1"], s["dl"], s["lam"], s["c0_base"])
    t_paper = {"APARTMENT": 6.78, "HOUSE": 1.10}[segment]
    if not np.isclose(s["lam_t"], t_paper, atol=0.006):
        raise AssertionError(f"{segment}: wedge t-statistic {s['lam_t']:.3f} differs from the paper's {t_paper}")
    if not np.allclose(got, paper, atol=PARITY_TOL):
        raise AssertionError(f"{segment}: parity with tab:did_results failed: {got} vs {paper}")
    return s, m, boot


# --------------------------------------------------------------------------------------------
# Policy recomputation (paper Section 5, under the limited-attention extension)
# --------------------------------------------------------------------------------------------
RENOVATION_COSTS: tuple[float, ...] = (250.0, 500.0)    # euros per m2, as in the paper's benchmarks
PSI_GRID: np.ndarray = np.linspace(0.0, 1.0, 1001)       # salience path
SAMPLE_YEARS: float = 3.5                                # n_listings counts listings from 2021-07-01 to 2024-12-31: listings per year = n / 3.5
SCENARIOS: tuple[str, ...] = ("base", "sal", "pi1", "hi")   # psi_hat, psi -> 1, pi -> 1, full attention (rho = 1 bound)
SC_STEM: dict[str, str] = {"base": "Base", "sal": "Sal", "pi1": "PiOne", "hi": "Hi"}
RC_STEM: dict[int, str] = {250: "TwoFifty", 500: "FiveHundred"}
TAKEUP_POINTS: int = 101


def sigma0_given_psi(psi: float, b: np.ndarray, c0: np.ndarray, pi: np.ndarray, th: np.ndarray,
                     eta: np.ndarray) -> np.ndarray:
    """Equilibrium hiding rate of informed low-quality sellers at relative attention psi.

    Single hiding cost c0 per market, C^def = 0 (e^def = eta), sigma_1 = 0 (Corollary att_hq outside CAS).
    Partial Pooling solves c0 = b [psi e* + (1 - psi) eta]  (eq. att_pp); Cost-Deterred Hiding has
    sigma0 = 0 and Complete Adverse Selection sigma0 = 1 (Proposition att_equilibrium).
    """
    if psi <= 0.0:
        gain_lo = b * eta                                     # Delta_0(e) = b * eta for every e
        return np.where(c0 < gain_lo, 1.0, 0.0)
    e_star = (c0 / b - (1.0 - psi) * eta) / psi
    e_one = (1.0 - pi) * th / (1.0 - pi * th)
    sigma = (1.0 - pi) / (pi * (1.0 - th)) * (th / np.clip(e_star, 1e-9, None) - 1.0)
    return np.where(e_star >= th, 0.0, np.where(e_star <= e_one, 1.0, np.clip(sigma, 0.0, 1.0)))


def policy_block(segment: str, m: pd.DataFrame, psi: float) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Per-market hiding costs, renovation thresholds and subsidies under both models, and the salience path.

    Core model: c0 = beta1 * e*, R_bar from results/<type>/subsidy_grid.csv (exact-pricing solver).
    Extension: c0 is the cost that reproduces the observed hiding rate at the common psi
    (c0 = b [psi e* + (1 - psi) eta]), and R_bar = b (log points), valid outside Complete Adverse Selection.
    """
    out = m[["market_id", "b1", "dl", "e", "eta", "theta_bar_hat", "pi_hat", "sigma_0_hat", "rho_m", "beta1_anchor"]].copy()
    out["c0_core"] = out["b1"] * out["e"]
    out["c0_fit"] = out["b1"] * (psi * out["e"] + (1 - psi) * out["eta"])
    out["c0_raw"] = out["dl"]
    grid = pd.read_csv(ROOT / "results" / segment.lower() / "subsidy_grid.csv")
    grid["market_id"] = grid["market_id"].astype(str)
    stats: dict[str, float] = {}
    rows = []
    for rc in RENOVATION_COSTS:
        g = grid[np.isclose(grid["cost_per_m2"], rc)].set_index("market_id")
        g = g.reindex(out["market_id"])
        price = g["price_per_m2_eur"].to_numpy()
        r_hat = rc / price                                    # renovation cost in log units
        rbar_core = g["R_bar_log_pts"].to_numpy()             # fractions
        rbar_ext = out["b1"].to_numpy() / 100.0
        s_core = np.maximum(r_hat - rbar_core, 0.0)
        s_ext = np.maximum(r_hat - rbar_ext, 0.0)
        units = g["median_area_m2"].to_numpy() * price
        w = g["n_listings"].to_numpy()
        tag = f"{int(rc)}"
        out[f"S_core_{tag}"] = s_core * price                 # euros per m2
        out[f"S_ext_{tag}"] = s_ext * price
        stats[f"rbar_core_eur_{tag}"] = float(np.nanmean(rbar_core * price))
        stats[f"rbar_ext_eur_{tag}"] = float(np.nanmean(rbar_ext * price))
        stats[f"share_pos_core_{tag}"] = 100.0 * float((s_core > 0).mean())
        stats[f"share_pos_ext_{tag}"] = 100.0 * float((s_ext > 0).mean())
        stats[f"cost_core_{tag}"] = float(np.nansum(w * s_core * units) / 1e9)   # billion euros, estimation markets
        stats[f"cost_ext_{tag}"] = float(np.nansum(w * s_ext * units) / 1e9)
        rows.append(tag)
    out["rbar_core"] = 100.0 * grid[np.isclose(grid["cost_per_m2"], RENOVATION_COSTS[0])].set_index(
        "market_id").reindex(out["market_id"])["R_bar_log_pts"].to_numpy()
    out["rbar_ext"] = out["b1"]
    stats["rbar_gap_mean"] = float((out["rbar_ext"] - out["rbar_core"]).abs().mean())   # log points
    stats["c0_core_mean"] = float(out["c0_core"].mean())
    stats["c0_fit_mean"] = float(out["c0_fit"].mean())

    # Salience path, per market, common psi
    b, c0 = out["b1"].to_numpy(), out["c0_fit"].to_numpy()
    pi, th, eta = out["pi_hat"].to_numpy(), out["theta_bar_hat"].to_numpy(), out["eta"].to_numpy()
    sigma_hat = sigma0_given_psi(psi, b, c0, pi, th, eta)
    if not np.allclose(sigma_hat, out["sigma_0_hat"].clip(0, 1), atol=1e-6):          # calibration identity
        raise AssertionError(f"{segment}: model at psi_hat does not reproduce the observed hiding rate")
    out["sigma0_obs"] = out["sigma_0_hat"]
    out["sigma0_full_salience"] = sigma0_given_psi(1.0, b, c0, pi, th, eta)
    out["psi_zero"] = psi * (eta - out["e"]) / (eta - th)       # attention at which hiding vanishes
    path = pd.DataFrame({"segment": segment, "psi": PSI_GRID,
                         "mean_sigma0": [float(sigma0_given_psi(x, b, c0, pi, th, eta).mean()) for x in PSI_GRID]})
    stats["sigma0_obs_mean"] = 100.0 * float(out["sigma0_obs"].mean())
    stats["sigma0_full_mean"] = 100.0 * float(out["sigma0_full_salience"].mean())
    stats["share_zero_full"] = 100.0 * float((out["sigma0_full_salience"] == 0).mean())
    stats["psi_zero_mean"] = float(out["psi_zero"].mean())
    stats["corr_core"] = float(np.corrcoef(out["c0_core"], out["dl"])[0, 1])
    stats["corr_ext"] = float(np.corrcoef(out["c0_fit"], out["dl"])[0, 1])
    stats["rmse_core"] = float(np.sqrt(((out["dl"] - out["c0_core"]) ** 2).mean()))
    stats["rmse_ext"] = float(np.sqrt(((out["dl"] - out["c0_fit"]) ** 2).mean()))
    stats["resid_core"] = float((out["dl"] - out["c0_core"]).mean())
    stats["resid_ext"] = float((out["dl"] - out["c0_fit"]).mean())
    stats["sd_resid_core"] = float((out["dl"] - out["c0_core"]).std(ddof=0))
    stats["sd_resid_ext"] = float((out["dl"] - out["c0_fit"]).std(ddof=0))
    return out, stats, path



def rbar_single_cost(b: np.ndarray, c0: np.ndarray, psi: float, pi: np.ndarray, th: np.ndarray,
                     eta: np.ndarray, c1: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Renovation threshold of an informed low-quality seller, single hiding cost, sigma_1 = 0 branch.

    R_bar = b - min{ max{Delta_psi(e(1)) - c0, 0}, b + c1 }  (Lemma V.2 evaluated at the equilibrium):
    equal to b in Cost-Deterred Hiding and Partial Pooling, and to b - (Delta_psi(e(1)) - c0) in
    Complete Adverse Selection. Returns (R_bar, flag) where flag marks markets in the CAS branch where
    high-quality hiding is also an equilibrium (threshold then depends on equilibrium selection).
    """
    e_one = (1.0 - pi) * th / (1.0 - pi * th)
    gain_cas = b * (psi * e_one + (1.0 - psi) * eta)               # Delta_psi(e(1))
    rbar = b - np.minimum(np.maximum(gain_cas - c0, 0.0), b + c1)
    g1_cas = b * (psi * e_one + (1.0 - psi) * eta - 1.0)           # high type's gain at sigma0 = 1, sigma1 = 0
    flag = (gain_cas > c0) & (g1_cas > c0 + c1)
    return rbar, flag


def attention_counterfactual(segment: str, pol: pd.DataFrame, psi: float) -> tuple[pd.DataFrame, dict]:
    """Force attention to 1 (paper Section 5.6).

    Reading (a): salience, psi -> 1 with omega_1 fixed. b is unchanged, so R_bar stays b: the gain is zero.
    Reading (b): omega_0 = omega_1 = 1. b_new = b / min(rho_hat, 1)^kappa, kappa in {0, 0.5, 1}; the data
    identify only rho_hat = rho * omega_1, so kappa = 1 (rho = 1) is the upper bound and kappa = 0 the
    maintained reading. c0 is held at its calibrated value (c0_fit).
    """
    grid = pd.read_csv(ROOT / "results" / segment.lower() / "subsidy_grid.csv")
    grid["market_id"] = grid["market_id"].astype(str)
    b, c0 = pol["b1"].to_numpy(), pol["c0_fit"].to_numpy()
    pi, th, eta = pol["pi_hat"].to_numpy(), pol["theta_bar_hat"].to_numpy(), pol["eta"].to_numpy()
    rho = np.minimum(pol["rho_m"].to_numpy(), 1.0)
    st: dict[str, float] = {}
    cf = pol[["market_id"]].copy()

    # baseline (psi_hat) and reading (a)
    rbar_base, flag_base = rbar_single_cost(b, c0, psi, pi, th, eta)
    rbar_a, flag_a = rbar_single_cost(b, c0, 1.0, pi, th, eta)
    if flag_base.any() or flag_a.any():
        raise AssertionError(f"{segment}: CAS branch with high-quality hiding; threshold depends on selection")
    if not (np.allclose(rbar_base, b) and np.allclose(rbar_a, b)):
        raise AssertionError(f"{segment}: R_bar != b in a market outside CAS at psi_hat or under salience")
    informed_low = lambda n: n * pol["pi_hat"].to_numpy() * (1.0 - pol["theta_bar_hat"].to_numpy())
    g250 = grid[np.isclose(grid["cost_per_m2"], 250.0)].set_index("market_id").reindex(pol["market_id"])
    n = g250["n_listings"].to_numpy()
    st["revealed_ratings"] = float(np.nansum(informed_low(n) * pol["sigma0_obs"].to_numpy()))
    st["informed_low_listings"] = float(np.nansum(informed_low(n)))

    for kappa, tag in ((0.0, "base"), (0.5, "mid"), (1.0, "hi")):
        b_new = b / np.minimum(np.where(rho > 0, rho, 1.0), 1.0) ** kappa
        rbar, cas_flag = rbar_single_cost(b_new, c0, 1.0, pi, th, eta)
        if cas_flag.any():                                          # high-quality hiding would make R_bar selection-dependent
            raise AssertionError(f"{segment}: reading (b) puts a market in the CAS branch with high-quality hiding")
        sig = sigma0_given_psi(1.0, b_new, c0, pi, th, eta)
        regime = np.where(c0 > b_new * th, "CD", np.where(c0 < b_new * (1 - pi) * th / (1 - pi * th), "CAS", "PP"))
        dr = rbar - b                                              # log points
        if (dr < -1e-9).any() or (dr > b_new - b + 1e-9).any():
            raise AssertionError(f"{segment}: threshold change outside [0, b_new - b]")
        if kappa == 0.0 and not np.allclose(dr, 0.0):
            raise AssertionError(f"{segment}: kappa = 0 must reproduce the extension threshold")
        # b_new equals 100 * anchor where rho_hat < 1 (checks the DiD/anchor units behind rho_m) and b where rho_hat >= 1
        cap = np.maximum(b, 100.0 * pol["beta1_anchor"].to_numpy())
        if (b_new > cap + 1e-9).any():
            raise AssertionError(f"{segment}: b_new exceeds max(b, anchor)")
        cf[f"b_{tag}"], cf[f"rbar_{tag}"], cf[f"sigma0_{tag}"], cf[f"regime_{tag}"] = b_new, rbar, sig, regime
        for rc in RENOVATION_COSTS:
            g = grid[np.isclose(grid["cost_per_m2"], rc)].set_index("market_id").reindex(pol["market_id"])
            price, area, w = g["price_per_m2_eur"].to_numpy(), g["median_area_m2"].to_numpy(), g["n_listings"].to_numpy()
            s_star = np.maximum(rc / price - rbar / 100.0, 0.0)
            cf[f"S_{tag}_{int(rc)}"] = s_star * price
            st[f"cost_{tag}_{int(rc)}"] = float(np.nansum(w * s_star * price * area) / 1e9)
            st[f"cost_inf_{tag}_{int(rc)}"] = float(np.nansum(informed_low(w) * s_star * price * area) / 1e9)
            st[f"share_pos_{tag}_{int(rc)}"] = 100.0 * float((s_star > 0).mean())
            if rc == RENOVATION_COSTS[0]:
                st[f"gain_eur_{tag}"] = float(np.nanmean((dr / 100.0) * price))
                st[f"gain_eur_lw_{tag}"] = float(np.nansum(w * (dr / 100.0) * price) / np.nansum(w))
        st[f"n_cas_{tag}"] = float((regime == "CAS").sum())
        st[f"sigma0_{tag}"] = 100.0 * float(np.mean(sig))
    st["gain_a"] = float(np.max(np.abs(rbar_a - b)))
    return cf, st



def regime_psi(b: np.ndarray, c0: np.ndarray, psi: float, pi: np.ndarray, th: np.ndarray,
               eta: np.ndarray) -> np.ndarray:
    """Regime of a market under attention psi: CD if c0 > Delta_psi(theta_bar), CAS if c0 < Delta_psi(e(1)), else PP."""
    e_one = (1.0 - pi) * th / (1.0 - pi * th)
    gain = lambda e: b * (psi * e + (1.0 - psi) * eta)
    return np.where(c0 > gain(th) + 1e-12, "CD", np.where(c0 < gain(e_one) - 1e-12, "CAS", "PP"))


def registry_hiding(segment: str, market_ids: pd.Series) -> np.ndarray:
    """Share of informed E-G listings that are not disclosed, by market, from the registry letters.

    The maintained specification (src/data_prep.py, hider_theta="impose_zero") counts every informed hider as low
    quality, so its sigma_0 also contains hiders with an A-D certificate; this is the letter-based alternative.
    """
    reg = load_registry(segment)
    reg = reg[(reg["K"] == 1) & reg["ademe_epc_letter"].notna()]
    low = reg[~reg["ademe_epc_letter"].isin(HIGH_LETTERS)]
    rate = (low["d"] == 0).groupby(low["market_id"].astype(str)).mean()
    return rate.reindex(market_ids.astype(str)).to_numpy()


def salience_saving(b: np.ndarray, lam: np.ndarray, sigma: np.ndarray, r_hat: np.ndarray, price: np.ndarray,
                    area: np.ndarray, elig: np.ndarray, cap: bool) -> np.ndarray:
    """Upper bound on the annual saving in the minimum subsidy bill from raising psi to one (euros), by market.

    With any distribution of hiding costs, a hider's rent falls by at most lambda (the fall in the price of silence);
    hiders are a share sigma of the eligible sellers, and the minimum subsidy of a seller with rent r is
    (R - b + min(r, b))^+, which rises by at most min(lambda, b, R) when the rent falls by lambda, all in log points
    of the price. With cap=True the rent that renovation destroys is capped at b (a renovated seller keeps her hiding
    cost, c1 = 0); cap=False requires the renovated seller to display (full rent). Elig is the annual number of
    eligible listings.
    """
    lam_eff = np.minimum(lam, b) if cap else lam
    per_seller = sigma * np.minimum(lam_eff, r_hat * 100.0) / 100.0
    return elig * per_seller * price * area / 1e9


def policy_scenarios(segment: str, pol: pd.DataFrame, cf: pd.DataFrame,
                     psi: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Section 5 scenarios under limited attention: baseline, salience (psi -> 1), pi -> 1, full-attention bound.

    Every scenario keeps c0 at its calibrated value c0_fit. The threshold is b outside Complete Adverse Selection
    (Proposition 5.1); the full-attention bound is the kappa = 1 reading of attention_counterfactual (rho = 1).
    The cost counts informed low-quality sellers pi (1 - theta_bar) of the listings, annualised over SAMPLE_YEARS;
    under pi -> 1 the eligible population is (1 - theta_bar). Returns (per-market table, take-up curves, attention path, stats).
    """
    grid = pd.read_csv(ROOT / "results" / segment.lower() / "subsidy_grid.csv")
    grid["market_id"] = grid["market_id"].astype(str)
    b, c0 = pol["b1"].to_numpy(), pol["c0_fit"].to_numpy()
    pi, th, eta = pol["pi_hat"].to_numpy(), pol["theta_bar_hat"].to_numpy(), pol["eta"].to_numpy()
    e = pol["e"].to_numpy()
    one = np.ones_like(pi)
    g250 = grid[np.isclose(grid["cost_per_m2"], 250.0)].set_index("market_id").reindex(pol["market_id"])
    price, area, n = g250["price_per_m2_eur"].to_numpy(), g250["median_area_m2"].to_numpy(), g250["n_listings"].to_numpy()

    rbar_pi1, flag_pi1 = rbar_single_cost(b, c0, psi, one, th, eta)
    if flag_pi1.any():
        raise AssertionError(f"{segment}: pi -> 1 puts a market in the CAS branch with high-quality hiding")
    sc = {                                   # rbar (log points), eligible share of listings, hiding rate, regime
        "base": (b, pi * (1 - th), pol["sigma0_obs"].to_numpy(), regime_psi(b, c0, psi, pi, th, eta)),
        "sal": (b, pi * (1 - th), pol["sigma0_full_salience"].to_numpy(), regime_psi(b, c0, 1.0, pi, th, eta)),
        "pi1": (rbar_pi1, 1 - th, sigma0_given_psi(psi, b, c0, one, th, eta),
                np.where(c0 >= b * (1.0 - psi) * eta, "CD", "CAS")),  # silent belief is 0 for any sigma0 > 0 when pi = 1; a tie has h = 0 and R_bar = b
        "hi": (cf["rbar_hi"].to_numpy(), pi * (1 - th), cf["sigma0_hi"].to_numpy(), cf["regime_hi"].to_numpy()),
    }
    if not np.allclose(sc["pi1"][0], b):
        raise AssertionError(f"{segment}: R_bar moved when pi -> 1 outside CAS")
    # The next three checks are identities of the calibration (c0_fit is built from the observed belief e), kept as guards
    # against input drift; the salience and full-attention results carry the independent content.
    if not np.all(sc["base"][3] == "PP"):
        raise AssertionError(f"{segment}: calibration should place every market in Partial Pooling at psi_hat")
    if not np.all(sc["pi1"][3] == "CD"):
        raise AssertionError(f"{segment}: pi -> 1 should move every market to Cost-Deterred Hiding")
    if not np.all(sc["sal"][3] == "CD"):
        raise AssertionError(f"{segment}: salience should move every market to Cost-Deterred Hiding")

    tab = pol[["market_id"]].copy()
    tab["price_eur_m2"], tab["area_m2"], tab["n_listings"] = price, area, n
    tab["b1"], tab["c0_fit"], tab["psi_hat"] = b, c0, psi
    st: dict[str, float] = {}
    for name, (rbar, pop, sig, reg) in sc.items():
        tab[f"rbar_{name}"], tab[f"pop_{name}"], tab[f"sigma0_{name}"], tab[f"regime_{name}"] = rbar, pop, sig, reg
        st[f"sc_{name}_rbar"] = float(np.nanmean(rbar / 100.0 * price))
        st[f"sc_{name}_sigma"] = 100.0 * float(np.mean(sig))
        for lab in ("CD", "PP", "CAS"):
            st[f"sc_{name}_n_{lab.lower()}"] = float((reg == lab).sum())
        for rc in RENOVATION_COSTS:
            gr = grid[np.isclose(grid["cost_per_m2"], rc)].set_index("market_id").reindex(pol["market_id"])
            s_star = np.maximum(rc / gr["price_per_m2_eur"].to_numpy() - rbar / 100.0, 0.0)
            tab[f"S_{name}_{int(rc)}"] = s_star * price
            st[f"sc_{name}_cost_{int(rc)}"] = float(np.nansum(n * pop * s_star * price * area) / 1e9 / SAMPLE_YEARS)
            st[f"sc_{name}_share_{int(rc)}"] = 100.0 * float((s_star > 0).mean())
    r_eur = b / 100.0 * price
    st["base_rbar_med"], st["base_rbar_min"], st["base_rbar_max"] = (float(np.nanmedian(r_eur)), float(np.nanmin(r_eur)),
                                                                     float(np.nanmax(r_eur)))
    st["base_area_med"] = float(np.nanmedian(area))
    st["n_listings_total"] = float(np.nansum(n))
    for rc in RENOVATION_COSTS:
        s_eur = tab[f"S_base_{int(rc)}"].to_numpy()
        pos = s_eur > 0
        st[f"base_smed_{int(rc)}"] = float(np.median(s_eur[pos]))
        st[f"base_smax_{int(rc)}"] = float(np.max(s_eur))          # flat subsidy that covers every market's minimum
        st[f"base_unit_{int(rc)}"] = float(np.median(s_eur[pos]) * st["base_area_med"])
        st[f"base_costshare_{int(rc)}"] = 100.0 * float(np.mean(s_eur[pos] / rc))
        st[f"base_nozero_{int(rc)}"] = 100.0 * float((~pos).mean())
    # Alternative reading: hiding cost read off each market's premium (c0 = Delta_hat_m), for the appendix
    c0_raw = pol["c0_raw"].to_numpy()
    reg_raw = regime_psi(b, c0_raw, psi, pi, th, eta)
    e_one_raw = (1.0 - pi) * th / (1.0 - pi * th)
    rb_raw, flag_raw = rbar_single_cost(b, c0_raw, psi, pi, th, eta)
    for lab in ("CD", "PP", "CAS"):
        st[f"raw_n_{lab.lower()}"] = float((reg_raw == lab).sum())
    multi = (b * (psi * e_one_raw + (1.0 - psi) * eta) > c0_raw) & (b * (psi * th + (1.0 - psi) * eta - 1.0) >= c0_raw)
    st["raw_n_flag"] = float((flag_raw | multi).sum())     # CAS markets where high-quality hiding is also an equilibrium
    st["raw_n_neg"] = float((c0_raw < 0).sum())
    st["raw_rbar_ratio"] = float(np.nanmean(rb_raw / b))
    elig = n * pi * (1 - th)
    st["top_market_share"] = 100.0 * float(np.nanmax(elig) / np.nansum(elig))   # largest market's share of eligible listings
    st["pi1_margin_pct"] = 100.0 * float(np.nanmean(b * psi * e / c0))   # slack of c0 over the default-priced silence gain, % of c0
    # Upper bound on what salience can save (Section 5.6), maintained sigma_0 and the letter-based alternative
    elig_yr = n * pi * (1 - th) / SAMPLE_YEARS
    lam_fit = (1.0 - psi) * b * (eta - e)                      # fall in the price of silence at the initial pool, log points
    lam_obs = np.maximum(pol["dl"].to_numpy() - b * e, 0.0)    # observed wedge, log points
    sig_reg = registry_hiding(segment, pol["market_id"])
    sig_reg = np.where(np.isnan(sig_reg), pol["sigma0_obs"].to_numpy(), sig_reg)
    variants = {"": (lam_fit, pol["sigma0_obs"].to_numpy(), True), "D": (lam_fit, pol["sigma0_obs"].to_numpy(), False),
                "Obs": (lam_obs, pol["sigma0_obs"].to_numpy(), True), "Reg": (lam_fit, sig_reg, True)}
    for rc in RENOVATION_COSTS:
        gr = grid[np.isclose(grid["cost_per_m2"], rc)].set_index("market_id").reindex(pol["market_id"])
        r_hat = rc / gr["price_per_m2_eur"].to_numpy()
        for tag, (lam, sg, cap) in variants.items():
            sv = salience_saving(b, lam, sg, r_hat, price, area, elig_yr, cap)
            st[f"saving{tag}_{int(rc)}"] = float(np.nansum(sv))
            if tag == "" and rc == RENOVATION_COSTS[0]:
                tab["saving_ub_250"] = sv * 1e9                  # euros per year, by market
                st["saving_top_share"] = 100.0 * float(np.nanmax(sv) / np.nansum(sv)) if np.nansum(sv) > 0 else 0.0
    reg_all = load_registry(segment)
    reg_all = reg_all[(reg_all["K"] == 1) & reg_all["market_id"].astype(str).isin(pol["market_id"].astype(str))]
    for lt in ("E", "F", "G"):
        st[f"hide_letter_{lt}"] = 100.0 * float((reg_all.loc[reg_all["ademe_epc_letter"] == lt, "d"] == 0).mean())
    st["lam_fit_mean"], st["sigma_reg_mean"] = float(np.nanmean(lam_fit)), 100.0 * float(np.nanmean(sig_reg))
    st["sc_base_pop"] = float(np.nansum(n * sc["base"][1]) / SAMPLE_YEARS)       # informed low-quality listings per year
    st["sc_pi1_pop"] = float(np.nansum(n * sc["pi1"][1]) / SAMPLE_YEARS)

    # Proposition 5.2: general-equilibrium correction and the stock of disclosed poor ratings (phase 1)
    corr = psi * b * (th - e)                                  # extra subsidy at full take-up, log points; e* = e at c0_fit
    st["ge_corr_pct_b"] = 100.0 * float(np.nanmean(corr / b))
    st["ge_corr_eur"] = float(np.nanmean(corr / 100.0 * price))
    inf_low = n * pi * (1 - th)
    st["ge_disclosed_share"] = 100.0 * float(1.0 - np.nansum(inf_low * pol["sigma0_obs"].to_numpy()) / np.nansum(inf_low))
    if (corr < -1e-9).any():
        raise AssertionError(f"{segment}: e* exceeds theta_bar in a Partial Pooling market")

    # Renovation take-up against a uniform subsidy S (share of informed low-quality listings in markets with S >= S*_m)
    core_rbar = pol["rbar_core"].to_numpy()
    rows = []
    for rc in RENOVATION_COSTS:
        gr = grid[np.isclose(grid["cost_per_m2"], rc)].set_index("market_id").reindex(pol["market_id"])
        pr = gr["price_per_m2_eur"].to_numpy()
        pop = n * pi * (1 - th)
        need = {"core": np.maximum(rc - core_rbar / 100.0 * pr, 0.0), "ext": np.maximum(rc - b / 100.0 * pr, 0.0),
                "hi": np.maximum(rc - sc["hi"][0] / 100.0 * pr, 0.0)}
        for s_eur in np.linspace(0.0, rc, TAKEUP_POINTS):
            rows.append(dict(segment=segment, R_hat=rc, S_eur=s_eur,
                             **{f"share_{k}": float(np.nansum(pop * (s_eur >= v - 1e-9)) / np.nansum(pop)) for k, v in need.items()}))
    # Threshold, hiding and regime shares along the attention path (c0 held at c0_fit)
    path = []
    for x in PSI_GRID[::10]:
        rb, _ = rbar_single_cost(b, c0, float(x), pi, th, eta)
        reg = regime_psi(b, c0, float(x), pi, th, eta)
        path.append(dict(segment=segment, psi=float(x), mean_rbar_eur=float(np.nanmean(rb / 100.0 * price)),
                         mean_sigma0=float(sigma0_given_psi(float(x), b, c0, pi, th, eta).mean()),
                         share_cd=float((reg == "CD").mean()), share_pp=float((reg == "PP").mean()),
                         share_cas=float((reg == "CAS").mean())))
    return tab, pd.DataFrame(rows), pd.DataFrame(path), st


# --------------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------------
MACROS: dict[str, tuple[str, str]] = {          # macro stem -> (summary key, format)
    "NDgtB": ("n_d_gt_b", "{:d}"), "NMarkets": ("n_markets", "{:d}"),
    "Excess": ("excess", "{:.1f}"), "Reach": ("reach", "{:.1f}"),
    "ShareUninf": ("share_uninf", "{:.0f}"), "Cursed": ("cursed", "{:.1f}"),
    "LevelGapPre": ("level_gap_pre", "{:.1f}"), "LevelGapPost": ("level_gap_post", "{:.1f}"),
    "Eta": ("eta_w", "{:.2f}"), "Ratio": ("ratio", "{:.2f}"),
    "Cstar": ("c_star_kwh", "{:.0f}"), "Csil": ("c_sil_kwh", "{:.0f}"),
    "Psi": ("psi", "{:.2f}"), "PsiLo": ("psi_lo", "{:.2f}"), "PsiHi": ("psi_hi", "{:.2f}"),
    "PsiSe": ("psi_se", "{:.2f}"), "PsiOLS": ("psi_ols", "{:.2f}"), "PsiOLSse": ("psi_ols_se", "{:.2f}"),
    "PsiMed": ("psi_med", "{:.2f}"), "PsiConst": ("psi_const", "{:.2f}"),
    "Icpt": ("icpt", "{:.1f}"), "IcptSe": ("icpt_se", "{:.1f}"),
    "Tfull": ("t_full", "{:.1f}"), "IntervalHi": ("interval_hi", "{:.2f}"),
    "Slack": ("slack", "{:.2f}"), "SlackT": ("slack_t", "{:.1f}"),
    "CstarLo": ("c_star_lo", "{:.0f}"), "CstarHi": ("c_star_hi", "{:.0f}"),
    "ShareInBand": ("share_in_band", "{:.0f}"), "ShareViolBottom": ("share_viol_bottom", "{:.0f}"),
    "NViol": ("n_viol", "{:d}"), "ShareViolTop": ("share_viol_top", "{:.0f}"),
    "Bthree": ("b1", "{:.1f}"), "Dthree": ("dl", "{:.1f}"), "Lam": ("lam", "{:.1f}"),
    "LamT": ("lam_t", "{:.2f}"), "CzeroBase": ("c0_base", "{:.1f}"),
    "BandLo": ("band_lo", "{:.2f}"), "BandHi": ("band_hi", "{:.2f}"),
    "BandWidth": ("band_width", "{:.2f}"), "BandWidthBase": ("band_width_base", "{:.2f}"),
    "FittedPremium": ("fitted_premium", "{:.2f}"),
    "SigmaOne": ("sigma_one", "{:.1f}"), "SigmaZero": ("sigma_zero", "{:.1f}"),
    "HighLoss": ("high_loss", "{:.1f}"), "Salience": ("salience", "{:.1f}"),
    "EnforceSil": ("enforce_sil", "{:.2f}"), "SensE": ("sens_e", "{:.2f}"),
    "PsiLevROM": ("psi_lev_rom", "{:.2f}"), "PsiLevSlope": ("psi_lev_slope", "{:.2f}"),
    "CzeroFit": ("c0_fit_mean", "{:.1f}"), "CzeroCoreMean": ("c0_core_mean", "{:.1f}"),
    "RmseCore": ("rmse_core", "{:.1f}"), "RmseExt": ("rmse_ext", "{:.1f}"),
    "CorrCore": ("corr_core", "{:.2f}"), "CorrExt": ("corr_ext", "{:.2f}"),
    "ResidCore": ("resid_core", "{:.1f}"), "ResidExt": ("resid_ext", "{:.1f}"),
    "RbarGap": ("rbar_gap_mean", "{:.2f}"),
    "SigmaObs": ("sigma0_obs_mean", "{:.1f}"), "SigmaFull": ("sigma0_full_mean", "{:.1f}"),
    "ShareZeroFull": ("share_zero_full", "{:.0f}"), "PsiZero": ("psi_zero_mean", "{:.2f}"),
    "SdResidCore": ("sd_resid_core", "{:.1f}"), "SdResidExt": ("sd_resid_ext", "{:.1f}"),
    "CfRevealed": ("revealed_ratings", "{:,.0f}"), "CfGainA": ("gain_a", "{:.2f}"),
    "CfGainHiEur": ("gain_eur_hi", "{:.0f}"), "CfGainHiEurLw": ("gain_eur_lw_hi", "{:.0f}"),
    "CfGainMidEur": ("gain_eur_mid", "{:.0f}"),
    "CfCostHiTwoFifty": ("cost_hi_250", "{:.2f}"), "CfCostHiFiveHundred": ("cost_hi_500", "{:.2f}"),
    "CfCostMidTwoFifty": ("cost_mid_250", "{:.2f}"), "CfCostMidFiveHundred": ("cost_mid_500", "{:.2f}"),
    "CfSharePosHiTwoFifty": ("share_pos_hi_250", "{:.0f}"), "CfNCasHi": ("n_cas_hi", "{:.0f}"),
    "CfSigmaHi": ("sigma0_hi", "{:.1f}"),
    "CostInfExtTwoFifty": ("cost_inf_base_250", "{:.2f}"), "CostInfExtFiveHundred": ("cost_inf_base_500", "{:.2f}"),
    "RbarCoreEurTwoFifty": ("rbar_core_eur_250", "{:.0f}"), "RbarExtEurTwoFifty": ("rbar_ext_eur_250", "{:.0f}"),
    "CostCoreTwoFifty": ("cost_core_250", "{:.2f}"), "CostExtTwoFifty": ("cost_ext_250", "{:.2f}"),
    "CostCoreFiveHundred": ("cost_core_500", "{:.2f}"), "CostExtFiveHundred": ("cost_ext_500", "{:.2f}"),
    "SharePosCoreTwoFifty": ("share_pos_core_250", "{:.0f}"), "SharePosExtTwoFifty": ("share_pos_ext_250", "{:.0f}"),
    "OneMinusPsiYone": ("one_minus_psi_Yone", "{:.2f}"), "OneMinusPsiYtwo": ("one_minus_psi_Ytwo", "{:.2f}"),
    "OneMinusPsiYthree": ("one_minus_psi_Ythree", "{:.2f}"),
    "PsiGfourtwenty": ("psi_Gfourtwenty", "{:.2f}"), "PsiGsixhundred": ("psi_Gsixhundred", "{:.2f}"),
    "NViolGfourtwenty": ("n_viol_Gfourtwenty", "{:d}"), "NViolGsixhundred": ("n_viol_Gsixhundred", "{:d}"),
}
for _sc in SCENARIOS:
    MACROS[f"Sc{SC_STEM[_sc]}Rbar"] = (f"sc_{_sc}_rbar", "{:.0f}")
    MACROS[f"Sc{SC_STEM[_sc]}Sigma"] = (f"sc_{_sc}_sigma", "{:.1f}")
    for _lab in ("cd", "pp", "cas"):
        MACROS[f"Sc{SC_STEM[_sc]}N{_lab.capitalize()}"] = (f"sc_{_sc}_n_{_lab}", "{:.0f}")
    for _rc, _rs in RC_STEM.items():
        MACROS[f"Sc{SC_STEM[_sc]}Cost{_rs}"] = (f"sc_{_sc}_cost_{_rc}", "{:.2f}")
        MACROS[f"Sc{SC_STEM[_sc]}Share{_rs}"] = (f"sc_{_sc}_share_{_rc}", "{:.0f}")
for _rc, _rs in RC_STEM.items():
    MACROS[f"BaseSMed{_rs}"] = (f"base_smed_{_rc}", "{:.0f}")
    MACROS[f"BaseSMax{_rs}"] = (f"base_smax_{_rc}", "{:.0f}")
    MACROS[f"BaseUnit{_rs}"] = (f"base_unit_{_rc}", "{:,.0f}")
    MACROS[f"BaseCostShare{_rs}"] = (f"base_costshare_{_rc}", "{:.0f}")
    MACROS[f"BaseNoSubsidy{_rs}"] = (f"base_nozero_{_rc}", "{:.1f}")
for _rc, _rs in RC_STEM.items():
    for _tag in ("", "D", "Obs", "Reg"):
        MACROS[f"SavingUb{_tag}{_rs}"] = (f"saving{_tag}_{_rc}", "{:.3f}")
for _lt in ("E", "F", "G"):
    MACROS[f"HideLetter{_lt}"] = (f"hide_letter_{_lt}", "{:.1f}")
MACROS.update({"SavingTopShare": ("saving_top_share", "{:.0f}"), "LamFitMean": ("lam_fit_mean", "{:.1f}"),
               "SigmaRegMean": ("sigma_reg_mean", "{:.1f}")})
MACROS["PiOneMargin"] = ("pi1_margin_pct", "{:.0f}")
MACROS.update({"PsiBar": ("psi_bar_e", "{:.2f}"), "PsiBarOne": ("psi_bar_one", "{:.2f}"),
               "PsiBarTheta": ("psi_bar_theta", "{:.2f}"), "NBetween": ("n_between", "{:d}")})
MACROS["TopMarketShare"] = ("top_market_share", "{:.0f}")
MACROS.update({"RawNCd": ("raw_n_cd", "{:.0f}"), "RawNPp": ("raw_n_pp", "{:.0f}"), "RawNCas": ("raw_n_cas", "{:.0f}"),
               "RawNFlag": ("raw_n_flag", "{:.0f}"), "RawNNeg": ("raw_n_neg", "{:.0f}"),
               "RawRbarRatio": ("raw_rbar_ratio", "{:.2f}")})
MACROS.update({"BaseRbarMed": ("base_rbar_med", "{:.0f}"), "BaseRbarMin": ("base_rbar_min", "{:.0f}"),
               "BaseRbarMax": ("base_rbar_max", "{:.0f}"), "BaseAreaMed": ("base_area_med", "{:.0f}"),
               "NListingsTotal": ("n_listings_total", "{:,.0f}")})
MACROS.update({"ScBasePop": ("sc_base_pop", "{:,.0f}"), "ScPiOnePop": ("sc_pi1_pop", "{:,.0f}"),
               "GeCorrPctB": ("ge_corr_pct_b", "{:.1f}"), "GeCorrEur": ("ge_corr_eur", "{:.1f}"),
               "GeDisclosedShare": ("ge_disclosed_share", "{:.0f}")})
BUDGET_BN: tuple[float, float] = (4.0, 5.0)              # MaPrimeRenov' annual budget, billion euros (lower, upper)
CROSS_MACROS: tuple[str, ...] = ("attDiffT", "attDiffCstarT", "attSensRatio", "attCzeroRatio", "attNBoot",
                                "attSampleYears", "attBudgetLo", "attBudgetHi",
                                *[f"attSavingUbTot{rs}{sfx}" for rs in RC_STEM.values() for sfx in ("", "Lo", "Hi")],
                                *[f"attScCostBaseTot{rs}" for rs in RC_STEM.values()],
                                *[f"attScCostBaseTot{rs}Lo" for rs in RC_STEM.values()],
                                *[f"attScCostBaseTot{rs}Hi" for rs in RC_STEM.values()])


def tex_num(text: str) -> str:
    """Typeset minus signs as a math minus in any mode (macros are used in text and math)."""
    return text.replace("-", r"\ensuremath{-}")


def macro_lines(stats: dict[str, dict] | None) -> list[str]:
    """\\newcommand lines; with stats=None every macro is a visible [XX] placeholder."""
    lines = ["% Generated by scripts/compute_attention.py -- do not edit by hand.",
             "% Values are provisional (band-midpoint energy costs; current registry match)."]
    for seg_tag in SEGMENTS.values():
        for stem, (key, fmt) in MACROS.items():
            name = f"att{stem}{seg_tag}"
            val = r"\textbf{[XX]}" if stats is None else fmt.format(
                int(stats[seg_tag][key]) if fmt == "{:d}" else stats[seg_tag][key])
            lines.append(f"\\newcommand{{\\{name}}}{{{val if stats is None else tex_num(val)}}}")
    for name in CROSS_MACROS:
        if stats is None:
            val = r"\textbf{[XX]}"
        elif name == "attDiffT":
            a, h = stats["Apt"], stats["House"]
            val = f"{(h['psi'] - a['psi']) / np.hypot(a['psi_se'], h['psi_se']):.1f}"
        elif name == "attDiffCstarT":
            a, h = stats["Apt"], stats["House"]
            val = f"{(h['c_star_kwh'] - a['c_star_kwh']) / np.hypot(a['c_star_se'], h['c_star_se']):.1f}"
        elif name == "attNBoot":
            val = f"{N_BOOT:,}"
        elif name == "attSensRatio":
            val = f"{stats['House']['sens_e'] / stats['Apt']['sens_e']:.0f}"
        elif name == "attSampleYears":
            val = f"{SAMPLE_YEARS:.1f}"
        elif name in ("attBudgetLo", "attBudgetHi"):
            val = f"{BUDGET_BN[0] if name.endswith('Lo') else BUDGET_BN[1]:.0f}"
        elif name.startswith("attSavingUbTot"):
            rc = {v: k for k, v in RC_STEM.items()}[name.removeprefix("attSavingUbTot").removesuffix("Lo").removesuffix("Hi")]
            tot = stats["Apt"][f"saving_{rc}"] + stats["House"][f"saving_{rc}"]
            val = (f"{tot:.3f}" if not name.endswith(("Lo", "Hi")) else
                   f"{100.0 * tot / (BUDGET_BN[1] if name.endswith('Lo') else BUDGET_BN[0]):.1f}")
        elif name.startswith("attScCostBaseTot"):
            rc = {v: k for k, v in RC_STEM.items()}[name.removeprefix("attScCostBaseTot").removesuffix("Lo").removesuffix("Hi")]
            tot = stats["Apt"][f"sc_base_cost_{rc}"] + stats["House"][f"sc_base_cost_{rc}"]
            val = (f"{tot:.2f}" if not name.endswith(("Lo", "Hi")) else
                   f"{100.0 * tot / (BUDGET_BN[1] if name.endswith('Lo') else BUDGET_BN[0]):.0f}")
        else:
            val = f"{stats['Apt']['dl'] / stats['Apt']['c0_base']:.1f}"
        lines.append(f"\\newcommand{{\\{name}}}{{{val}}}")
    return lines


def table_body(stats: dict[str, dict]) -> list[str]:
    """Table 7: what the data show, what each model predicts for the non-disclosure premium, attention estimates."""
    a, h = stats["Apt"], stats["House"]
    zero = lambda x: 0.0 if abs(x) < 0.05 else x                 # avoid printing a signed zero
    both = lambda lab, ka, kh, f="{:.1f}": f"{lab} & {f.format(zero(a[ka]) if f == '{:.1f}' else a[ka])} & {f.format(zero(h[kh]) if f == '{:.1f}' else h[kh])} \\\\"
    ci = lambda s: tex_num(f"{s['psi']:.2f} [{s['psi_lo']:.2f}, {s['psi_hi']:.2f}]")
    panel = lambda t: f"\\multicolumn{{3}}{{l}}{{\\textit{{{t}}}}} \\\\"
    rule = r"\cmidrule[1pt]{1-3}"
    return [
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcc@{}}",
        r"\toprule\toprule",
        f" & \\textbf{{Apartments}} ($N={a['n_markets']}$) & \\textbf{{Houses}} ($N={h['n_markets']}$) \\\\",
        r"\midrule",
        panel("A. What the data show (log points)"),
        both(r"Energy-efficiency premium $\hat\beta_1$", "b1", "b1"),
        both(r"Non-disclosure premium $\hat\Delta$", "dl", "dl"),
        both(r"Ratio $\hat\Delta/\hat\beta_1$ (at most one in the core model)", "ratio", "ratio", "{:.2f}"),
        f"Markets above the core-model ceiling $\\hat\\Delta=\\hat\\beta_1$ & {a['n_d_gt_b']} of {a['n_markets']} & {h['n_d_gt_b']} of {h['n_markets']} \\\\",
        r"\midrule",
        panel("B. Predicted non-disclosure premium (log points)"),
        both(r"Core model (full attention): $\hat\beta_1\hat e^*$", "c0_base", "c0_base"),
        f"\\quad Observed minus predicted ($t$) & {a['lam']:.1f} ({a['lam_t']:.1f}) & {zero(h['lam']):.1f} ({h['lam_t']:.1f}) \\\\",
        rule,
        r"$\triangleright$ \textbf{Limited attention: $\hat\beta_1[\hat\psi\hat e^*+(1-\hat\psi)\eta]$} & "
        + f"\\textbf{{{a['c0_fit_mean']:.1f}}} & \\textbf{{{h['c0_fit_mean']:.1f}}} \\\\",
        r" \quad \textbf{Observed minus predicted} & "
        + f"\\textbf{{{zero(a['resid_ext']):.1f}}} & \\textbf{{{zero(h['resid_ext']):.1f}}} \\\\",
        rule,
        panel("C. Attention to silence"),
        f"$\\hat\\psi_\\delta$, ratio of sums [95\\% CI] & {ci(a)} & {ci(h)} \\\\",
        f"$\\hat\\psi_\\delta$, regression through the origin (s.e.) & {a['psi_ols']:.2f} ({a['psi_ols_se']:.2f}) & {h['psi_ols']:.2f} ({h['psi_ols_se']:.2f}) \\\\",
        both(r"$t$-statistic, full attention ($\psi_\delta=1$)", "t_full", "t_full"),
        f"Identified interval for $\\psi_\\delta$ ($C^{{\\rm def}}\\ge0$) & $[0,\\,{a['interval_hi']:.2f}]$ & $[0,\\,{h['interval_hi']:.2f}]$ \\\\",
        f"Perceived cost of silence $C^*_\\delta$ (kWh$_{{\\rm ep}}$/m$^2$/yr) [95\\% CI] & "
        + tex_num(f"{a['c_star_kwh']:.0f} [{a['c_star_lo']:.0f}, {a['c_star_hi']:.0f}] & {h['c_star_kwh']:.0f} [{h['c_star_lo']:.0f}, {h['c_star_hi']:.0f}]") + " \\\\",
        both(r"Rational cost of the silent pool $\bar C^{\rm sil}$ (kWh$_{\rm ep}$/m$^2$/yr)", "c_sil_kwh", "c_sil_kwh", "{:.0f}"),
        both(r"Energy-cost ratio $\eta$ (weighted)", "eta_w", "eta_w", "{:.2f}"),
        f"Mean slack in the attention ceiling $\\eta\\hat\\beta_1-\\hat\\Delta$ ($t$) & {a['slack']:.2f} ({a['slack_t']:.1f}) & {h['slack']:.2f} ({h['slack_t']:.1f}) \\\\",
        f"Markets above their own attention ceiling & {a['n_viol']} of {a['n_markets']} & {h['n_viol']} of {h['n_markets']} \\\\",
        r"\bottomrule\bottomrule",
        r"\end{tabular*}",
    ]


def policy_table_body(stats: dict[str, dict]) -> list[str]:
    """Apartment policy table for Section 5.6: core model, extension, and the reading-(b) upper bound."""
    a = stats["Apt"]
    r = lambda label, x, y, z, f="{:.1f}": f"{label} & {f.format(x)} & {f.format(y)} & {f.format(z)} \\\\"
    return [
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lccc@{}}",
        r"\toprule\toprule",
        r" & \textbf{Core model} & \textbf{Extension} & \textbf{Full attention, upper bound} \\",
        r"\midrule",
        r("Hiding cost $\\hat c_0$ (log points)", a["c0_core_mean"], a["c0_fit_mean"], a["c0_fit_mean"]),
        r("Mean threshold $\\bar R$ (\\euro/m$^2$)", a["rbar_core_eur_250"], a["rbar_ext_eur_250"],
          a["rbar_ext_eur_250"] + a["gain_eur_hi"], "{:.0f}"),
        r("Aggregate cost, $\\hat R=250$ (\\euro bn)", a["cost_core_250"], a["cost_base_250"], a["cost_hi_250"], "{:.2f}"),
        r("Aggregate cost, $\\hat R=500$ (\\euro bn)", a["cost_core_500"], a["cost_base_500"], a["cost_hi_500"], "{:.2f}"),
        f"Hiding rate, observed (\\%) & {a['sigma0_obs_mean']:.1f} & {a['sigma0_obs_mean']:.1f} & {a['sigma0_obs_mean']:.1f} \\\\",
        f"Hiding rate with attention raised to 1 (\\%) & -- & {a['sigma0_full_mean']:.1f} & {a['sigma0_hi']:.1f} \\\\",
        r"\bottomrule\bottomrule",
        r"\end{tabular*}",
    ]


def scenario_table_body(stats: dict[str, dict]) -> list[str]:
    """Section 5.6 table: scenarios under limited attention, apartments (panel A) and houses (panel B)."""
    cols = [("base", r"$\hat\psi$ (baseline)"), ("sal", r"$\psi\to1$"), ("pi1", r"$\pi\to1$"),
            ("hi", r"Full attention (bound)")]
    lines = [r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccc@{}}", r"\toprule\toprule",
             " & " + " & ".join(f"\\textbf{{{c}}}" for _, c in cols) + r" \\"]
    for panel, tag in (("Panel A: apartments", "Apt"), ("Panel B: houses", "House")):
        st = stats[tag]
        row = lambda lab, key, f: lab + " & " + " & ".join(f.format(st[key.format(k)]) for k, _ in cols) + r" \\"
        lines += [r"\midrule", f"\\multicolumn{{5}}{{l}}{{\\textit{{{panel}}}}} \\\\",
                  row(r"Mean threshold $\bar R$ (\euro/m$^2$)", "sc_{}_rbar", "{:.0f}"),
                  row(r"Markets in Cost-Deterred Hiding", "sc_{}_n_cd", "{:.0f}"),
                  row(r"Markets in Partial Pooling", "sc_{}_n_pp", "{:.0f}"),
                  row(r"Markets in Complete Adverse Selection", "sc_{}_n_cas", "{:.0f}"),
                  row(r"Mean hiding rate (\%)", "sc_{}_sigma", "{:.1f}"),
                  row(r"Markets with $S^*>0$, $\hat R=250$ (\%)", "sc_{}_share_250", "{:.0f}"),
                  row(r"Annual cost, $\hat R=250$ (\euro bn)", "sc_{}_cost_250", "{:.2f}"),
                  row(r"Annual cost, $\hat R=500$ (\euro bn)", "sc_{}_cost_500", "{:.2f}")]
    lines += [r"\bottomrule\bottomrule", r"\end{tabular*}"]
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stub", action="store_true", help="write [XX] placeholder macros only")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("src").setLevel(logging.WARNING)

    tables = ROOT / "results" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    if args.stub:
        (tables / "attention_macros.tex").write_text("\n".join(macro_lines(None)) + "\n")
        logger.info("wrote placeholder macros")
        return

    streams = dict(zip(SEGMENTS, np.random.default_rng(SEED).spawn(len(SEGMENTS))))
    out = ROOT / "results" / "attention"
    out.mkdir(parents=True, exist_ok=True)
    stats: dict[str, dict] = {}
    boots = {}
    paths: list[pd.DataFrame] = []
    takeups: list[pd.DataFrame] = []
    apaths: list[pd.DataFrame] = []
    for segment, tag in SEGMENTS.items():
        s, m, boot = estimate_segment(segment, streams[segment])
        stats[tag] = s
        boots[tag] = boot
        m.to_csv(out / f"{segment.lower()}_markets.csv", index=False)
        pol, pstats, path = policy_block(segment, m, s["psi"])
        cf, cfstats = attention_counterfactual(segment, pol, s["psi"])
        cf.to_csv(out / f"{segment.lower()}_attention_cf.csv", index=False)
        stats[tag].update(cfstats)
        pol.to_csv(out / f"{segment.lower()}_policy.csv", index=False)
        scen, takeup, apath, scstats = policy_scenarios(segment, pol, cf, s["psi"])
        scen.to_csv(out / f"{segment.lower()}_scenarios.csv", index=False)
        takeups.append(takeup)
        apaths.append(apath)
        stats[tag].update(scstats)
        paths.append(path)
        stats[tag].update(pstats)
        logger.info("%s: psi=%.3f [%.2f, %.2f], eta=%.2f, ratio=%.2f, C*=%.0f kWh",
                    segment, s["psi"], s["psi_lo"], s["psi_hi"], s["eta_w"], s["ratio"], s["c_star_kwh"])
    pd.DataFrame(stats).rename_axis("statistic").to_csv(out / "summary.csv")
    pd.DataFrame(boots).to_csv(out / "bootstrap_psi.csv", index=False)
    pd.concat(paths).to_csv(out / "salience_path.csv", index=False)
    pd.concat(takeups).to_csv(out / "takeup_curve.csv", index=False)
    pd.concat(apaths).to_csv(out / "attention_path.csv", index=False)
    (tables / "attention_macros.tex").write_text("\n".join(macro_lines(stats)) + "\n")
    (tables / "table_attention_body.tex").write_text("\n".join(table_body(stats)) + "\n")
    (tables / "table_att_policy_body.tex").write_text("\n".join(policy_table_body(stats)) + "\n")
    (tables / "table_att_scenarios_body.tex").write_text("\n".join(scenario_table_body(stats)) + "\n")
    logger.info("wrote results/attention/ and results/tables/attention_*.tex")


if __name__ == "__main__":
    main()
