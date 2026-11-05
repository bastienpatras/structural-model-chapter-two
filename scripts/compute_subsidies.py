"""Recompute the renovation-subsidy figures and table from cached CSVs.

Loads per-market estimates and grid-format subsidies that were exported by the
main pipeline (`python run.py config_apartment.json` / `config_house.json`) and
regenerates all Plotly figures plus the LaTeX summary table — without rerunning
estimation or touching the parquet inputs. Useful when iterating on figure
styling, or to evaluate alternative renovation-cost schemes from the cached
market estimates.

Usage
-----
    python scripts/compute_subsidies.py                            # use defaults
    python scripts/compute_subsidies.py --cost-per-m2 750          # override canonical cost
    python scripts/compute_subsidies.py --cost-per-m2-grid 200 400 800 1200
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.outputs import (
    figure_renovation_threshold_distribution,
    figure_subsidy_grid,
    figure_threshold_vs_beta1,
    figure_subsidy_bubble_map,
    figure_subsidy_regime_breakdown,
    table_subsidy_summary,
    export_market_estimates,
)


def _load_pair(
    output_root      : Path,
    cost_per_m2_grid : list[float] | None,
) -> dict[str, dict[str, pd.DataFrame | None]]:
    """Load market_estimates / grid / summary / centroids for both property types."""
    out: dict[str, dict[str, pd.DataFrame | None]] = {}
    for ptype in ("apartment", "house"):
        ddir = output_root / ptype
        bundle: dict[str, pd.DataFrame | None] = {
            "market_estimates": None,
            "subsidy_grid"    : None,
            "subsidy_summary" : None,
            "centroids"       : None,
        }
        me = ddir / "market_estimates.csv"
        if me.exists():
            bundle["market_estimates"] = pd.read_csv(me)
        sg = ddir / "subsidy_grid.csv"
        if sg.exists():
            bundle["subsidy_grid"] = pd.read_csv(sg)
        ss = ddir / "subsidy_summary.csv"
        if ss.exists():
            bundle["subsidy_summary"] = pd.read_csv(ss)
        cc = ROOT / "data" / "geo" / f"market_centroids_{ptype}.csv"
        if cc.exists():
            bundle["centroids"] = pd.read_csv(cc).set_index("market_id")
        out[ptype] = bundle

    if cost_per_m2_grid is not None:
        for ptype, bundle in out.items():
            base = bundle["market_estimates"]
            if base is None or base.empty:
                continue
            base = base.copy()
            need = {"R_bar_log_pts", "price_per_m2_eur", "median_area_m2"}
            if not need.issubset(set(base.columns)):
                print(f"[warn] {ptype}/market_estimates.csv missing columns "
                      f"{need - set(base.columns)}; cannot override grid")
                continue
            grid = pd.DataFrame({"cost_per_m2": [float(c) for c in cost_per_m2_grid]})
            new_grid = base.merge(grid, how="cross")
            new_grid["r_hat_log_pts"]       = new_grid["cost_per_m2"] / new_grid["price_per_m2_eur"]
            new_grid["S_star_log_pts"]      = (new_grid["r_hat_log_pts"] - new_grid["R_bar_log_pts"]).clip(lower=0.0)
            new_grid["S_star_eur_per_m2"]   = new_grid["S_star_log_pts"]    * new_grid["price_per_m2_eur"]
            new_grid["S_star_eur_per_unit"] = new_grid["S_star_eur_per_m2"] * new_grid["median_area_m2"]
            cols = [
                "market_id", "cost_per_m2", "r_hat_log_pts",
                "R_bar_log_pts", "R_bar_eur_per_m2",
                "S_star_log_pts", "S_star_eur_per_m2", "S_star_eur_per_unit",
                "price_per_m2_eur", "median_area_m2", "n_listings",
                "regime", "rho_m", "c0_m", "pi_m", "theta_bar_m",
                "sigma_0_m", "e_star_m", "beta_1_m",
            ]
            bundle["subsidy_grid"] = new_grid[[c for c in cols if c in new_grid.columns]]

            from src.estimation import aggregate_subsidy_summary
            bundle["subsidy_summary"] = aggregate_subsidy_summary(bundle["subsidy_grid"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cost-per-m2", type=float, default=500.0,
                    help="canonical R̂ in €/m² for the bubble map (default 500)")
    ap.add_argument("--cost-per-m2-grid", type=float, nargs="+", default=None,
                    help="override grid in €/m²; defaults to whatever the CSV contains")
    ap.add_argument("--output-root", type=Path, default=ROOT / "results",
                    help="root of `results/{apartment,house}` directories")
    args = ap.parse_args()

    bundles = _load_pair(args.output_root, args.cost_per_m2_grid)
    apt = bundles["apartment"]
    hse = bundles["house"]

    if apt["subsidy_grid"] is None and hse["subsidy_grid"] is None:
        sys.exit("error: neither subsidy_grid.csv could be located; run "
                 "`python run.py config_apartment.json` first.")

    figure_renovation_threshold_distribution(apt["subsidy_grid"], hse["subsidy_grid"])
    figure_subsidy_grid(apt["subsidy_grid"], hse["subsidy_grid"])
    figure_threshold_vs_beta1(apt["subsidy_grid"], hse["subsidy_grid"])
    figure_subsidy_regime_breakdown(apt["subsidy_grid"], hse["subsidy_grid"])
    figure_subsidy_bubble_map(
        grid_apt        = apt["subsidy_grid"],
        grid_hse        = hse["subsidy_grid"],
        centroids_apt   = apt["centroids"],
        centroids_hse   = hse["centroids"],
        cost_per_m2_apt = args.cost_per_m2,
        cost_per_m2_hse = args.cost_per_m2,
    )
    table_subsidy_summary(apt["subsidy_summary"], hse["subsidy_summary"])

    if args.cost_per_m2_grid is not None:
        for ptype, bundle in bundles.items():
            grid = bundle["subsidy_grid"]
            summ = bundle["subsidy_summary"]
            if grid is None or summ is None:
                continue
            export_market_estimates(
                grid_df     = grid,
                summary_df  = summ,
                output_dir  = args.output_root / ptype,
                centroids_df= bundle["centroids"],
            )

    print("\nDone. HTML figures in results/figures/, table in results/tables/.")


if __name__ == "__main__":
    main()
