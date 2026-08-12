"""
run.py — Structural Estimation Pipeline
========================================
Mandatory Disclosure and Housing Market Dynamics
Patras, B. (Sciences Po Paris, 2024)

Usage
-----
    python run.py config_apartment.json
    python run.py config_house.json
    python run.py config_apartment.json config_house.json   # both sequentially

Output
------
    results/<property_type>/results.txt   — full printed summary (paper-ready)
    results/<property_type>/             — tables and figures
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )

# ---------------------------------------------------------------------------
# Pipeline imports
# ---------------------------------------------------------------------------

from src.data_prep   import (load_listings, merge_datasets, classify_listings,
                              compute_market_stats, compute_market_centroids,
                              compute_market_levels)
from src.hedonic     import (estimate_hedonic, compute_hiding_premium,
                              estimate_rho_direct, calibrate_demand_scale,
                              calibrate_demand_scale_m)
from src.moments     import extract_data_moments
from src.estimation  import (build_valuation_params, estimate_msm,
                              estimate_c0_bounds, compute_market_subsidies,
                              compute_subsidy_grid, aggregate_subsidy_summary,
                              aggregate_budget, bootstrap_se)
from src.model       import belief_function
from src.event_study import load_price_indices, compute_did, estimate_rho_c0
from src.outputs     import produce_all_outputs


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(cfg: dict, year: int | None = None) -> dict:
    ptype    = cfg["property_type"]
    controls = cfg["controls"]

    # ── Data ─────────────────────────────────────────────────────────────────
    year_label = f", year={year}" if year is not None else ""
    print(f"[1/5] Loading data  ({ptype}{year_label})")
    df = pd.read_parquet(cfg["listings_path"])
    if year is not None:
        df = df[df["start_date"].dt.year == year].copy()
    if "group" not in df.columns:
        df = merge_datasets(df, ademe=None, epc_threshold=cfg["epc_threshold"],
                            hider_theta=cfg.get("hider_theta", "registry"))
        df = classify_listings(df)
    market_stats = compute_market_stats(df, controls=controls)
    market_stats = market_stats[market_stats["estimable"]].copy()
    df_est       = df[df["market_id"].isin(market_stats.index)].copy()

    n_listings = len(df_est)
    n_markets  = len(market_stats)
    group_dist = df_est["group"].value_counts()

    # ── Hedonic regression ───────────────────────────────────────────────────
    print(f"[2/5] Hedonic regression  ({n_listings:,} listings, {n_markets} markets)")
    hedonic_params  = estimate_hedonic(df_est, controls=controls)
    scale           = calibrate_demand_scale(hedonic_params)
    scale_m         = calibrate_demand_scale_m(hedonic_params)
    df_hiders, market_premium = compute_hiding_premium(df_est, hedonic_params)
    rho_direct_df   = estimate_rho_direct(market_stats, market_premium, hedonic_params)

    # ── DiD event study ──────────────────────────────────────────────────────
    print(f"[3/5] DiD event study")
    did_params    = None
    did_estimates = None
    index_path    = cfg.get("index_path")
    if index_path and Path(index_path).exists():
        index_df      = load_price_indices(index_path)
        did_estimates = compute_did(index_df, min_volume=cfg["did_min_volume"])
        did_params    = estimate_rho_c0(did_estimates, market_stats)

    # ── Moments and MSM ──────────────────────────────────────────────────────
    # Restrict to markets with a valid DiD estimate (β̂₁_m > 0, ρ̂_m ∈ [0,1]).
    # Markets without a usable DiD ρ̂_m cannot be two-step identified.
    did_markets = set()
    if did_params is not None:
        did_markets = {m for m in did_params.rho_m.index if not np.isnan(did_params.rho_m[m])}

    print(f"[4/5] MSM estimation  (two-step: {'yes' if did_params is not None else 'no — fallback'}, "
          f"{len(did_markets)} DiD markets)")
    data_moments = extract_data_moments(df_est)
    estimable    = (set(market_stats.index) & set(data_moments.keys())
                    & did_markets if did_markets else set(market_stats.index) & set(data_moments.keys()))
    data_moments = {m: data_moments[m] for m in estimable}
    market_stats = market_stats.loc[list(estimable)]
    df_est       = df_est[df_est["market_id"].isin(estimable)].copy()

    market_params = {
        m: build_valuation_params(m, market_stats, hedonic_params,
                                  scale=scale, scale_m=scale_m)
        for m in estimable
    }

    rho_init     = {}
    c0_init_dict = {}
    for m in estimable:
        if did_params is not None and m in did_params.rho_m.index and not np.isnan(did_params.rho_m[m]):
            rho_init[m] = float(did_params.rho_m[m])
        elif m in rho_direct_df.index and not np.isnan(rho_direct_df.loc[m, "rho_hat_clipped"]):
            rho_init[m] = float(rho_direct_df.loc[m, "rho_hat_clipped"])
        else:
            rho_init[m] = 0.3
        c0_init_dict[m] = float(did_params.c0_m[m]) if (
            did_params is not None and m in did_params.c0_m.index
            and not np.isnan(did_params.c0_m[m])
        ) else cfg["c0_init"]

    use_twostep = did_params is not None
    msm_result  = estimate_msm(
        data_moments     = data_moments,
        market_params    = market_params,
        market_stats     = market_stats,
        weighting_scheme = cfg["weighting_scheme"],
        df               = df_est,
        rho_init         = rho_init,
        c0_init          = c0_init_dict,
        n_restarts       = cfg["n_restarts"],
        fix_rho          = use_twostep,
    )

    c0_bounds = estimate_c0_bounds(market_stats, market_params, msm_result.rho_hat)

    # ── Bootstrap (optional) ────────────────────────────────────────────────
    se_dict = None
    if cfg.get("n_boot", 0) > 0:
        print(f"[4b] Bootstrap SE  (B={cfg['n_boot']})")
        boot = bootstrap_se(
            df             = df_est,
            market_stats   = market_stats,
            hedonic_params = hedonic_params,
            market_params  = market_params,
            n_boot         = cfg["n_boot"],
            rho_hat_fixed  = msm_result.rho_hat if use_twostep else None,
        )
        se_dict = {"rho_se": boot["rho_se"], "c0_se": boot["c0_se"]}

    # ── Subsidies ───────────────────────────────────────────────────────────
    subsidy_df = compute_market_subsidies(
        market_stats      = market_stats,
        market_params     = market_params,
        rho_hat           = msm_result.rho_hat,
        c0_hat            = msm_result.c0_hat,
        actual_reno_costs = cfg.get("actual_reno_costs"),
    )

    cost_per_m2_grid       = cfg.get("cost_per_m2_grid", [250, 500, 1000])
    cost_per_m2_canonical  = float(cfg.get("cost_per_m2_canonical", 500.0))

    market_levels    = compute_market_levels(df_est)
    subsidy_grid_df  = compute_subsidy_grid(
        market_stats     = market_stats,
        market_params    = market_params,
        rho_hat          = msm_result.rho_hat,
        c0_hat           = msm_result.c0_hat,
        cost_per_m2_grid = cost_per_m2_grid,
        market_levels    = market_levels,
    )
    subsidy_summary  = aggregate_subsidy_summary(subsidy_grid_df)
    market_weights   = df_est.groupby("market_id").size()
    subsidy_budget   = aggregate_budget(subsidy_grid_df, market_weights)

    # Market centroids for the bubble map
    try:
        cache_centroids = Path("data") / "geo" / f"market_centroids_{ptype.lower()}.csv"
        centroids_df = compute_market_centroids(df_est, cache_path=cache_centroids)
    except Exception as exc:
        print(f"[centroids] failed ({exc}); skipping bubble map")
        centroids_df = None

    # ── Outputs ─────────────────────────────────────────────────────────────
    print(f"[5/5] Saving tables and figures")
    out_dir = Path(cfg.get("output_dir", f"results/{ptype.lower()}"))
    if year is not None:
        out_dir = out_dir / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)

    # If the sibling property type was already estimated, load its cached CSVs
    # so the two-panel subsidy figures can be rendered in this single pass.
    sibling_label = "HOUSE" if ptype.upper() == "APARTMENT" else "APARTMENT"
    sibling_dir   = Path("results") / sibling_label.lower()
    sib_grid      = None
    sib_summary   = None
    sib_centroids = None
    if (sibling_dir / "subsidy_grid.csv").exists():
        sib_grid = pd.read_csv(sibling_dir / "subsidy_grid.csv")
    if (sibling_dir / "subsidy_summary.csv").exists():
        sib_summary = pd.read_csv(sibling_dir / "subsidy_summary.csv")
    sib_cent_path = Path("data") / "geo" / f"market_centroids_{sibling_label.lower()}.csv"
    if sib_cent_path.exists():
        sib_centroids = pd.read_csv(sib_cent_path).set_index("market_id")
    if sib_grid is not None:
        print(f"[outputs] sibling estimates found at {sibling_dir}; two-panel figures will be rendered.")

    produce_all_outputs(
        df                = df_est,
        market_stats      = market_stats,
        data_moments      = data_moments,
        msm_result        = msm_result,
        hedonic_params    = hedonic_params,
        subsidy_df        = subsidy_df,
        se_dict           = se_dict,
        did_params        = did_params,
        did_estimates     = did_estimates,
        subsidy_grid_df   = subsidy_grid_df,
        subsidy_summary   = subsidy_summary,
        subsidy_budget    = subsidy_budget,
        centroids_df      = centroids_df,
        output_dir        = out_dir,
        sibling_grid      = sib_grid,
        sibling_centroids = sib_centroids,
        sibling_summary   = sib_summary,
        sibling_label     = sibling_label,
        self_label             = ptype.upper(),
        cost_per_m2_canonical  = cost_per_m2_canonical,
    )

    return dict(
        ptype           = ptype,
        year            = year,
        cfg             = cfg,
        df_est          = df_est,
        market_stats    = market_stats,
        group_dist      = group_dist,
        n_listings      = n_listings,
        n_markets       = n_markets,
        hedonic_params  = hedonic_params,
        did_estimates   = did_estimates,
        did_params      = did_params,
        data_moments    = data_moments,
        msm_result      = msm_result,
        c0_bounds       = c0_bounds,
        subsidy_df      = subsidy_df,
        subsidy_grid_df = subsidy_grid_df,
        subsidy_summary = subsidy_summary,
        subsidy_budget  = subsidy_budget,
        centroids_df    = centroids_df,
        se_dict         = se_dict,
    )


# ---------------------------------------------------------------------------
# Results printer
# ---------------------------------------------------------------------------

def _pct(x: float) -> str:
    return f"{100*x:.1f}%"

def _fmt(x: float, d: int = 3) -> str:
    return f"{x:.{d}f}"

def _se(val: float, se: float | None) -> str:
    if se is None or np.isnan(se):
        return f"{val:.4f}"
    return f"{val:.4f}  ({se:.4f})"


def print_results(r: dict) -> str:
    """
    Build and return the full paper-ready results string.
    Also prints to stdout.
    """
    ptype       = r["ptype"]
    ms          = r["msm_result"]
    mkt         = r["market_stats"]
    hp          = r["hedonic_params"]
    did_est     = r["did_estimates"]
    did_par     = r["did_params"]
    sub         = r["subsidy_df"]
    se          = r["se_dict"] or {}
    group_dist  = r["group_dist"]
    n_list      = r["n_listings"]

    rho_vals = np.array([v for v in ms.rho_hat.values() if not np.isnan(v)])
    c0_vals  = np.array([v for v in ms.c0_hat.values()  if not np.isnan(v)])
    rho_se   = se.get("rho_se", {})
    c0_se    = se.get("c0_se", {})

    lines = []
    W = 70

    def hdr(title: str) -> None:
        lines.append("")
        lines.append("=" * W)
        lines.append(f"  {title}")
        lines.append("=" * W)

    def sub_hdr(title: str) -> None:
        lines.append("")
        lines.append(f"  {'─' * (W-4)}")
        lines.append(f"  {title}")
        lines.append(f"  {'─' * (W-4)}")

    def row(label: str, value: str) -> None:
        lines.append(f"  {label:<42}{value}")

    # ── Header ───────────────────────────────────────────────────────────────
    hdr(f"MANDATORY DISCLOSURE AND HOUSING MARKET DYNAMICS")
    lines.append(f"  Property type  : {ptype}")
    if r.get("year"):
        lines.append(f"  Year filter    : {r['year']}")
    lines.append(f"  Estimation date: {pd.Timestamp.today().date()}")

    # ── Sample ───────────────────────────────────────────────────────────────
    sub_hdr("I. SAMPLE")
    row("Total listings (estimation sample)", f"{n_list:>12,}")
    row("Markets (estimation sample)", f"{r['n_markets']:>12,}")
    lines.append("")
    row("Group", "N          Share")
    for grp, n in group_dist.items():
        row(f"  {grp.replace('_',' ').title()}", f"{n:>9,}   {_pct(n/n_list):>6}")
    lines.append("")
    row("Mean σ̂₀ (hiding rate, informed low-qual.)", _fmt(mkt["sigma_0_hat"].mean()))
    row("Std  σ̂₀",                                   _fmt(mkt["sigma_0_hat"].std()))
    # σ̂₁ is the model's testable restriction: Corollary (cor:hq_disclose) predicts
    # σ₁* = 0. Reported explicitly so the restriction is visible rather than assumed.
    if "sigma_1_hat" in mkt.columns:
        row("Mean σ̂₁ (hiding rate, informed high-qual.)", _fmt(mkt["sigma_1_hat"].mean()))
        row("Std  σ̂₁",                                    _fmt(mkt["sigma_1_hat"].std()))
        _s1, _s0 = mkt["sigma_1_hat"].mean(), mkt["sigma_0_hat"].mean()
        row("  σ̂₁/σ̂₀  (model predicts 0)",
            _fmt(_s1 / _s0) if _s0 and not np.isnan(_s0) else "n/a")
    row("Mean π̂  (informed-seller share)",             _fmt(mkt["pi_hat"].mean()))
    row("Mean θ̄  (quality share, informed)",           _fmt(mkt["theta_bar_hat"].mean()))

    # ── Hedonic regression ───────────────────────────────────────────────────
    sub_hdr("II. HEDONIC REGRESSION  (Step 1)")
    row("β̂₁  EPC quality premium (log pts)", _fmt(hp.beta_1, 4))
    if hasattr(hp, "r2") and hp.r2 is not None:
        row("R²", _fmt(hp.r2, 3))
    if hasattr(hp, "n_obs") and hp.n_obs is not None:
        row("N (truthful disclosers)",        f"{hp.n_obs:,}")

    # ── DiD event study ──────────────────────────────────────────────────────
    sub_hdr("II. DiD EVENT STUDY  (Step 2 — identification of ρ̂_m)")
    if did_est is not None:
        did = did_est.did
        n_did    = did["DiD_beta1"].notna().sum()
        n_pos    = (did["DiD_beta1"] > 0).sum()
        beta1_m  = did["DiD_beta1"].dropna()
        delta_m  = did["DiD_delta"].dropna()
        row("Markets with DiD estimates",         f"{n_did:>12,}")
        row("Markets with β̂₁_m > 0 (usable)",    f"{n_pos:>12,}")
        lines.append("")
        row("β̂₁_m  market-level EPC premium", "")
        row("  mean  (log pts)",  _fmt(beta1_m.mean(), 4))
        row("  median",           _fmt(beta1_m.median(), 4))
        row("  std",              _fmt(beta1_m.std(), 4))
        row("  [p10, p90]",       f"[{_fmt(beta1_m.quantile(.10),4)}, {_fmt(beta1_m.quantile(.90),4)}]")
        lines.append("")
        row("Δ̂_m  non-disclosure premium (upper bound on ĉ₀_m)", "")
        row("  mean  (log pts)",  _fmt(delta_m.mean(), 4))
        row("  median",           _fmt(delta_m.median(), 4))
        row("  std",              _fmt(delta_m.std(), 4))
        row("  [p10, p90]",       f"[{_fmt(delta_m.quantile(.10),4)}, {_fmt(delta_m.quantile(.90),4)}]")
    else:
        lines.append("  DiD stage skipped (index file not found).")

    # ── Structural estimates ─────────────────────────────────────────────────
    sub_hdr("III. STRUCTURAL ESTIMATES  (Two-step: ρ̂ from DiD, ĉ₀ inverted)")
    lines.append("")
    lines.append(f"  {'Parameter':<42}{'Mean':>8}  {'Median':>8}  {'Std':>8}  {'[p10, p90]'}")
    lines.append(f"  {'─'*66}")

    def stat_row(label, vals):
        v = np.array(vals)
        lines.append(
            f"  {label:<42}"
            f"{np.mean(v):>8.4f}  "
            f"{np.median(v):>8.4f}  "
            f"{np.std(v):>8.4f}  "
            f"[{np.quantile(v,.10):.4f}, {np.quantile(v,.90):.4f}]"
        )

    stat_row("ρ̂_m  EPC-sensitive buyer share",      rho_vals)
    stat_row("ĉ₀_m  hiding cost  (log pts)",         c0_vals)
    stat_row("σ̂₀_m  equilibrium hiding rate",        mkt["sigma_0_hat"].dropna().values)
    if "sigma_1_hat" in mkt.columns:
        stat_row("σ̂₁_m  high-quality hiding (pred. 0)",
                 mkt["sigma_1_hat"].dropna().values)
    stat_row("ê*_m  equilibrium pool quality",
             [did_par.e_star[m] for m in did_par.e_star.index
              if not np.isnan(did_par.e_star[m])] if did_par is not None
             else mkt["theta_bar_hat"].dropna().values)

    if se:
        lines.append("")
        lines.append("  Bootstrap standard errors (market-level mean):")
        rho_se_vals = [v for v in rho_se.values() if v is not None and not np.isnan(v)]
        c0_se_vals  = [v for v in c0_se.values()  if v is not None and not np.isnan(v)]
        if rho_se_vals:
            row("  SE(ρ̂_m)  mean across markets", _fmt(np.mean(rho_se_vals), 4))
        if c0_se_vals:
            row("  SE(ĉ₀_m) mean across markets", _fmt(np.mean(c0_se_vals), 4))

    # ── Economic magnitudes ──────────────────────────────────────────────────
    sub_hdr("IV. ECONOMIC MAGNITUDES")
    mean_rho   = np.mean(rho_vals)
    mean_c0    = np.mean(c0_vals)
    mean_pi    = mkt["pi_hat"].mean()
    mean_tb    = mkt["theta_bar_hat"].mean()
    mean_sigma = mkt["sigma_0_hat"].mean()

    # Compute regime bounds using estimated c₀ and equilibrium belief directly.
    # Since c₀ = ρβ₁e(σ₀*) by the indifference condition, the CDH upper bound
    # and CAS lower bound are c₀ × (θ̄/e*) and c₀ × (e(1)/e*) respectively,
    # avoiding reliance on the national hedonic β̂₁ which is not market-specific.
    c0_arr, pi_arr, tb_arr, sig_arr = [], [], [], []
    for m in ms.c0_hat:
        c0_m = ms.c0_hat.get(m, np.nan)
        if np.isnan(c0_m):
            continue
        pi_m  = float(mkt.loc[m, "pi_hat"])        if m in mkt.index else np.nan
        tb_m  = float(mkt.loc[m, "theta_bar_hat"]) if m in mkt.index else np.nan
        sig_m = float(mkt.loc[m, "sigma_0_hat"])   if m in mkt.index else np.nan
        if any(np.isnan([pi_m, tb_m, sig_m])):
            continue
        c0_arr.append(c0_m); pi_arr.append(pi_m)
        tb_arr.append(tb_m); sig_arr.append(sig_m)

    if c0_arr:
        e_star_arr = [belief_function(s, p, t) for s, p, t in zip(sig_arr, pi_arr, tb_arr)]
        e1_arr     = [belief_function(1.0, p, t) for p, t in zip(pi_arr, tb_arr)]
        # CDH upper bound = ρβ₁θ̄ = c₀ × (θ̄ / e*)
        prem_cdh = float(np.mean([c * tb / es for c, tb, es
                                   in zip(c0_arr, tb_arr, e_star_arr) if es > 0]))
        # PP premium = c₀ (invariant to market composition)
        prem_pp  = float(np.mean(c0_arr))
        # CAS lower bound = ρβ₁e(1) = c₀ × (e(1) / e*)
        prem_cas = float(np.mean([c * e1 / es for c, e1, es
                                   in zip(c0_arr, e1_arr, e_star_arr) if es > 0]))
    else:
        prem_cdh = prem_pp = prem_cas = np.nan

    row("Mean ρ̂ × β̂₁  (price sensitivity, log pts)", _fmt(mean_rho * hp.beta_1, 4))
    row("Non-disclosure premium — CDH upper bound (log pts)", _fmt(prem_cdh, 4))
    row("Non-disclosure premium — Partial Pooling = ĉ₀ (log pts)", _fmt(prem_pp, 4))
    row("Non-disclosure premium — CAS lower bound (log pts)", _fmt(prem_cas, 4))
    row("Ordering check  CDH > PP > CAS",
        f"{'✓' if prem_cdh > prem_pp > prem_cas else '✗'} "
        f"({_fmt(prem_cdh,4)} > {_fmt(prem_pp,4)} > {_fmt(prem_cas,4)})")
    row("Hiding cost ĉ₀  as % of disclosed-low price", _fmt(mean_c0 * 100, 2) + "%")
    lines.append("")
    lines.append("  Interpretation: at the market mean, a low-quality informed")
    lines.append(f"  seller forgoes ~{mean_c0*100:.2f} log pts (~{mean_c0*100:.1f}% of property")
    lines.append(f"  value) to conceal her EPC score. The share of EPC-sensitive")
    lines.append(f"  buyers averages {mean_rho*100:.1f}% across markets.")

    # ── Equilibrium regimes ──────────────────────────────────────────────────
    sub_hdr("V. EQUILIBRIUM REGIME DISTRIBUTION")
    eq_counts = pd.Series(list(ms.eq_types.values())).value_counts()
    total_eq  = len(ms.eq_types)
    for regime, n in eq_counts.items():
        row(f"  {regime}", f"{n:>4}  ({_pct(n/total_eq)})")

    # ── Renovation subsidies ─────────────────────────────────────────────────
    if sub is not None and len(sub) > 0 and "S_star" in sub.columns:
        sub_hdr("VI. OPTIMAL RENOVATION SUBSIDIES  (Section 6)")
        s_vals = sub["S_star"].dropna()
        if len(s_vals) > 0:
            stat_row("S*_m  optimal subsidy  (log pts)", s_vals.values)
            row("Markets where S*_m > 0", f"{(s_vals > 0).sum():>4}  ({_pct((s_vals>0).mean())})")

    # ── Footer ───────────────────────────────────────────────────────────────
    lines.append("")
    lines.append("=" * W)
    lines.append(f"  END OF RESULTS — {ptype}")
    lines.append("=" * W)
    lines.append("")

    output = "\n".join(lines)
    print(output)
    return output


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Structural estimation pipeline — Patras (2024)"
    )
    parser.add_argument(
        "configs",
        nargs="+",
        metavar="CONFIG",
        help="Path(s) to JSON config file(s), e.g. config_apartment.json config_house.json",
    )
    parser.add_argument(
        "--year", type=int, default=None,
        help="Filter listings to a single calendar year (e.g. --year 2022). "
             "DiD estimates are unaffected (computed from the price index panel).",
    )
    args = parser.parse_args()

    all_results = {}

    for config_path in args.configs:
        with open(config_path) as f:
            cfg = json.load(f)

        ptype = cfg["property_type"]
        print(f"\n{'='*70}")
        print(f"  Running pipeline: {ptype}  (config: {config_path})")
        print(f"{'='*70}\n")

        r = run_pipeline(cfg, year=args.year)
        all_results[ptype] = r

        # Print and save results
        out_dir = Path(cfg.get("output_dir", f"results/{ptype.lower()}"))
        if args.year is not None:
            out_dir = out_dir / str(args.year)
        out_dir.mkdir(parents=True, exist_ok=True)
        txt_path = out_dir / "results.txt"

        result_str = print_results(r)
        txt_path.write_text(result_str, encoding="utf-8")
        print(f"\n  Results saved to {txt_path}")

    # If both property types ran, print a comparative summary
    if "APARTMENT" in all_results and "HOUSE" in all_results:
        _print_comparison(all_results["APARTMENT"], all_results["HOUSE"])


def _print_comparison(ra: dict, rh: dict) -> None:
    lines = []
    W = 70
    lines.append("")
    lines.append("=" * W)
    lines.append("  COMPARATIVE SUMMARY: APARTMENTS vs. HOUSES")
    lines.append("=" * W)
    lines.append("")
    lines.append(f"  {'Parameter':<38}{'APARTMENT':>12}  {'HOUSE':>12}")
    lines.append(f"  {'─'*64}")

    def cmp(label, a_val, h_val, fmt=".3f"):
        lines.append(f"  {label:<38}{a_val:>12{fmt}}  {h_val:>12{fmt}}")

    for r, tag in [(ra, "a"), (rh, "h")]:
        pass  # just reuse ra/rh below

    a_rho = np.array([v for v in ra["msm_result"].rho_hat.values() if not np.isnan(v)])
    h_rho = np.array([v for v in rh["msm_result"].rho_hat.values() if not np.isnan(v)])
    a_c0  = np.array([v for v in ra["msm_result"].c0_hat.values()  if not np.isnan(v)])
    h_c0  = np.array([v for v in rh["msm_result"].c0_hat.values()  if not np.isnan(v)])
    a_mkt = ra["market_stats"]
    h_mkt = rh["market_stats"]

    cmp("Estimation sample (listings)",  ra["n_listings"],  rh["n_listings"], ",d")
    cmp("Markets",                       ra["n_markets"],   rh["n_markets"],  "d")
    lines.append("")
    cmp("β̂₁  EPC quality premium",       ra["hedonic_params"].beta_1, rh["hedonic_params"].beta_1)
    lines.append("")
    cmp("ρ̂_m  mean",  np.mean(a_rho), np.mean(h_rho))
    cmp("ρ̂_m  median", np.median(a_rho), np.median(h_rho))
    cmp("ρ̂_m  std",    np.std(a_rho),  np.std(h_rho))
    lines.append("")
    cmp("ĉ₀_m  mean  (log pts)",  np.mean(a_c0), np.mean(h_c0), ".4f")
    cmp("ĉ₀_m  median",           np.median(a_c0), np.median(h_c0), ".4f")
    cmp("ĉ₀_m  std",              np.std(a_c0),  np.std(h_c0),  ".4f")
    lines.append("")
    cmp("σ̂₀_m  mean  (hiding rate)", a_mkt["sigma_0_hat"].mean(), h_mkt["sigma_0_hat"].mean())
    cmp("π̂_m   mean  (informed share)", a_mkt["pi_hat"].mean(), h_mkt["pi_hat"].mean())
    cmp("θ̄_m   mean  (quality share)",  a_mkt["theta_bar_hat"].mean(), h_mkt["theta_bar_hat"].mean())
    lines.append("")
    lines.append("=" * W)

    output = "\n".join(lines)
    print(output)

    # Save comparison
    Path("results").mkdir(exist_ok=True)
    comp_path = Path("results/comparison.txt")
    comp_path.write_text(output, encoding="utf-8")
    print(f"\n  Comparison saved to {comp_path}")


if __name__ == "__main__":
    main()
