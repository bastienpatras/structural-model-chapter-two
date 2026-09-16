"""
run_threshold_robustness.py — Sweep the quality-threshold / sigma_1-treatment
robustness table (paper-real-estate/sections/A-robustness.tex, Table tab:robustness)
under the anchored rho estimator (quality_reports/plans/humble-zooming-lovelace.md).

Crosses two maintained specification choices, for both property types:
  - quality threshold: A-D vs E/F/G (epc_threshold=4.0, high_group="ABCD")
                    vs A-C vs E/F/G (epc_threshold=3.0, high_group="ABC")
  - sigma_1 treatment: "impose_zero" (revealed preference; forces sigma_1_hat=0)
                    vs "registry"    (withheld grade read from ADEME)

Mirrors run_pipeline() in run.py through the anchored msm_result -- deliberately
does NOT call produce_all_outputs/bootstrap/subsidies, since this sweep only
needs the market-level structural estimates, not figures or subsidy tables.

Usage
-----
    python scripts/run_threshold_robustness.py

Output
------
    results/_robust/threshold_sensitivity_summary.csv   (gitignored; regenerable)
    printed table matching tab:robustness's layout
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_prep   import merge_datasets, classify_listings, compute_market_stats, compute_market_levels, compute_energy_anchor
from src.hedonic     import estimate_hedonic, calibrate_demand_scale, calibrate_demand_scale_m
from src.estimation  import build_valuation_params
from src.event_study import load_price_indices, compute_did, estimate_rho_c0
from src.rho_identification import estimate_beta1_anchor, estimate_rho_c0_anchored, build_msm_result_from_anchored

BASE_CONFIGS = {
    "APARTMENT": "config_apartment.json",
    "HOUSE":     "config_house.json",
}

# (label, epc_threshold, high_group, hider_theta)
SPECS = [
    ("A-D vs E/F/G, sigma1 imposed (baseline)", 4.0, "ABCD", "impose_zero"),
    ("A-D vs E/F/G, sigma1 from registry",      4.0, "ABCD", "registry"),
    ("A-C vs E/F/G, sigma1 imposed",            3.0, "ABC",  "impose_zero"),
    ("A-C vs E/F/G, sigma1 from registry",      3.0, "ABC",  "registry"),
]

OUT_DIR = Path("results/_robust")


def run_spec(cfg: dict, epc_threshold: float, high_group: str, hider_theta: str) -> dict:
    """Trimmed pipeline: data -> market_stats -> hedonic -> DiD -> anchored msm_result.
    Mirrors run_pipeline() in run.py exactly through msm_result construction;
    skips bootstrap/subsidies/produce_all_outputs (not needed for this table)."""
    controls = cfg["controls"]

    df = pd.read_parquet(cfg["listings_path"])
    df = merge_datasets(df, ademe=None, epc_threshold=epc_threshold, hider_theta=hider_theta)
    df = classify_listings(df)
    market_stats = compute_market_stats(df, controls=controls)
    market_stats = market_stats[market_stats["estimable"]].copy()
    df_est = df[df["market_id"].isin(market_stats.index)].copy()

    hedonic_params = estimate_hedonic(df_est, controls=controls)
    scale   = calibrate_demand_scale(hedonic_params)
    scale_m = calibrate_demand_scale_m(hedonic_params)

    index_df      = load_price_indices(cfg["index_path"], high_group=high_group)
    did_estimates = compute_did(index_df, min_volume=cfg["did_min_volume"])
    did_params    = estimate_rho_c0(did_estimates, market_stats)

    did_markets = {m for m in did_params.rho_m.index if not np.isnan(did_params.rho_m[m])}
    estimable = set(market_stats.index) & did_markets
    market_stats = market_stats.loc[list(estimable)]
    df_est = df_est[df_est["market_id"].isin(estimable)].copy()

    market_params = {
        m: build_valuation_params(
            m, market_stats, hedonic_params, scale=scale, scale_m=scale_m,
            did_beta1=(float(did_params.beta1_m[m]) if m in did_params.beta1_m.index else None),
        )
        for m in estimable
    }
    market_levels = compute_market_levels(df_est)

    energy_anchor = compute_energy_anchor(df_est, epc_threshold=epc_threshold)
    beta1_anchor  = estimate_beta1_anchor(
        market_levels, energy_anchor,
        p_E=cfg["anchor_p_E"], r=cfg["anchor_r"],
        T=cfg.get("anchor_T"), kappa=cfg.get("anchor_kappa", 1.0),
    )
    anchored_result = estimate_rho_c0_anchored(did_estimates, market_stats, beta1_anchor)
    msm_result = build_msm_result_from_anchored(anchored_result, market_stats, market_params)

    return dict(market_stats=market_stats, msm_result=msm_result, hider_theta=hider_theta)


def summarize(result: dict) -> dict:
    market_stats = result["market_stats"]
    msm = result["msm_result"]
    markets = [m for m, v in msm.rho_hat.items() if not np.isnan(v)]
    sub = market_stats.loc[markets]

    rho = np.array([msm.rho_hat[m] for m in markets])
    c0  = np.array([msm.c0_hat[m] for m in markets])

    row = {
        "N": len(markets),
        "rho_hat_mean": float(np.mean(rho)) if len(rho) else np.nan,
        "c0_hat_mean":  float(np.mean(c0)) if len(c0) else np.nan,
        "sigma0_mean":  float(sub["sigma_0_hat"].mean()),
        "sigma1_mean":  (float(sub["sigma_1_hat"].mean())
                          if result["hider_theta"] == "registry" else np.nan),
        "theta_bar_mean": float(sub["theta_bar_hat"].mean()),
    }
    return row


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for ptype, config_path in BASE_CONFIGS.items():
        with open(config_path) as f:
            cfg = json.load(f)
        for label, epc_threshold, high_group, hider_theta in SPECS:
            print(f"[{ptype}] {label} ...")
            result = run_spec(cfg, epc_threshold, high_group, hider_theta)
            summary = summarize(result)
            summary.update(dict(property_type=ptype, spec=label,
                                 epc_threshold=epc_threshold, high_group=high_group,
                                 hider_theta=hider_theta))
            rows.append(summary)
            print(f"    N={summary['N']}  rho={summary['rho_hat_mean']:.4f}  "
                  f"c0={summary['c0_hat_mean']:.4f}  sigma0={summary['sigma0_mean']:.4f}  "
                  f"sigma1={summary['sigma1_mean']}  theta_bar={summary['theta_bar_mean']:.4f}")

    out_df = pd.DataFrame(rows)
    out_path = OUT_DIR / "threshold_sensitivity_summary.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved to {out_path}")
    print(out_df.to_string(index=False))


if __name__ == "__main__":
    main()
