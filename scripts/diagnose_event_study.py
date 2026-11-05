"""
diagnose_event_study.py
========================
Read-only diagnostic: reproduce and export the DiD event study underlying the
paper's headline non-disclosure premium (6.9% apartments / 3.4% houses),
exactly as computed by the two places in this repo that compute it, and flag
where they diverge.

Two independent computations exist in this repo for the same object
(the undisclosed-vs-energy-intensive price gap around the July 2021 reform):

  1. `src/event_study.py::compute_did()` — feeds the structural estimation
     pipeline (`main.py`/`run.py` -> `results/comparison.txt`,
     `results/tables/table_market_estimates.tex`). Uses the LOG PRICE LEVEL
     (`prices` column), per that module's own docstring, which explicitly
     warns against using `final_index` because it is a growth-rate index,
     not a level.

  2. `scripts/make_stylized_facts.py::make_fact1()` — generates the paper's
     own Fact-1 event-study figure (`fig_fact1_nondiscl_premium_eventstudy.pdf`,
     cited in `sections/03-setting-draft.tex` §3.3.1). Uses `final_index`
     (the growth-rate index, base=100 at Oct 2018), not `prices`.

This script runs BOTH, on the same underlying `data/index_*.csv` files, and
reports both alongside the manuscript's stated headline numbers, so the
divergence (if any) is visible rather than assumed.

It also reproduces the market-level structural inputs (pi_hat, theta_bar,
sigma0_hat -> e*_m) via the same `compute_market_stats` / `estimate_rho_c0`
call sequence `run.py` uses, so the beta1_m vs Delta_m*e*_m scatter (Fig 3)
uses the real e*_m, not a placeholder.

Nothing here edits `paper-real-estate/`, `src/`, or `results/`. All outputs go
to `quality_reports/diagnostics/event-study-audit/`.

Run from project root:
    python scripts/diagnose_event_study.py
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_prep import merge_datasets, classify_listings, compute_market_stats
from src.event_study import load_price_indices, compute_did, estimate_rho_c0, REFORM_DATE
OUTDIR = ROOT / "quality_reports" / "diagnostics" / "event-study-audit"
OUTDIR.mkdir(parents=True, exist_ok=True)

PROPERTY_TYPES = [
    ("APARTMENT", ROOT / "config_apartment.json"),
    ("HOUSE", ROOT / "config_house.json"),
]

# Manuscript's stated headline numbers (abstract / Table 4), for reference only.
MANUSCRIPT_HEADLINE = {
    "APARTMENT": {"delta_pct": 6.9, "beta1_pct": 1.7, "n_markets_various": "40 / 45 / 49 / 43"},
    "HOUSE": {"delta_pct": 3.4, "beta1_pct": 5.1, "n_markets_various": "100 / 97 / 104 / 107"},
}


def fact1_style_gap(index_path: Path, item_type: str) -> pd.DataFrame:
    """Replicate make_stylized_facts.py::make_fact1 exactly (final_index-based)."""
    df = pd.read_csv(index_path, parse_dates=["date"])
    df = df[df["item_type"] == item_type].copy()
    df["pv"] = df["final_index"] * df["volume"]
    grp = df.groupby(["date", "EPC"], as_index=False).agg(pv=("pv", "sum"), v=("volume", "sum"))
    grp["price"] = grp["pv"] / grp["v"]
    wide = grp.pivot(index="date", columns="EPC", values="price").sort_index()
    wide = wide.loc["2019-01-01":"2024-06-30"]
    out = pd.DataFrame(index=wide.index)
    out["nondiscl_gap_finalindex"] = np.log(wide["Missing"]) - np.log(wide["Intensive"])
    out["epc_gap_finalindex"] = np.log(wide["Efficient"]) - np.log(wide["Intensive"])
    return out


def level_style_gap(index_df: pd.DataFrame) -> pd.DataFrame:
    """Same national-aggregate object, but on `prices` (level) not `final_index`."""
    df = index_df.copy()
    df["pv"] = df["prices"] * df["volume"]
    grp = df.groupby(["date", "epc_cat"], as_index=False).agg(pv=("pv", "sum"), v=("volume", "sum"))
    grp["price"] = grp["pv"] / grp["v"]
    wide = grp.pivot(index="date", columns="epc_cat", values="price").sort_index()
    out = pd.DataFrame(index=wide.index)
    out["nondiscl_gap_prices"] = np.log(wide["undisclosed"]) - np.log(wide["EFG"])
    out["epc_gap_prices"] = np.log(wide["ABC"]) - np.log(wide["EFG"])
    return out


def pre_post(series: pd.Series) -> tuple[float, float, float]:
    pre = float(series.loc[series.index < REFORM_DATE].mean())
    post = float(series.loc[series.index >= REFORM_DATE].mean())
    return pre, post, post - pre


def run_for_property(ptype: str, config_path: Path, summary_lines: list[str]) -> None:
    cfg = json.loads(config_path.read_text())
    label = ptype.lower()
    summary_lines.append(f"\n{'=' * 70}\n{ptype}\n{'=' * 70}")

    # ---- 1. price-index panel, both computations -------------------------
    index_path = ROOT / cfg["index_path"]
    fact1_gap = fact1_style_gap(index_path, ptype)
    index_df = load_price_indices(str(index_path), high_group=cfg.get("high_group", "ABCD"))
    lvl_gap = level_style_gap(index_df)

    combined = fact1_gap.join(lvl_gap, how="outer")
    combined.to_csv(OUTDIR / f"aggregate_gap_series_{label}.csv")

    f_pre, f_post, f_did = pre_post(fact1_gap["nondiscl_gap_finalindex"])
    l_pre, l_post, l_did = pre_post(lvl_gap["nondiscl_gap_prices"])
    fb_pre, fb_post, fb_did = pre_post(fact1_gap["epc_gap_finalindex"])
    lb_pre, lb_post, lb_did = pre_post(lvl_gap["epc_gap_prices"])

    summary_lines.append(
        f"\n-- National aggregate non-disclosure gap (undisclosed - EFG), log points --\n"
        f"  make_fact1 methodology (final_index, growth rate):  pre={f_pre:+.4f}  post={f_post:+.4f}  DiD={f_did:+.4f}  ({100*(np.exp(f_did)-1):+.2f}%)\n"
        f"  event_study.py methodology (prices, level):         pre={l_pre:+.4f}  post={l_post:+.4f}  DiD={l_did:+.4f}  ({100*(np.exp(l_did)-1):+.2f}%)\n"
        f"  Manuscript states: {MANUSCRIPT_HEADLINE[ptype]['delta_pct']}%"
    )
    summary_lines.append(
        f"\n-- National aggregate EPC quality gap (ABC/D - EFG), log points --\n"
        f"  make_fact1 methodology (final_index, growth rate):  pre={fb_pre:+.4f}  post={fb_post:+.4f}  DiD={fb_did:+.4f}  ({100*(np.exp(fb_did)-1):+.2f}%)\n"
        f"  event_study.py methodology (prices, level):         pre={lb_pre:+.4f}  post={lb_post:+.4f}  DiD={lb_did:+.4f}  ({100*(np.exp(lb_did)-1):+.2f}%)\n"
        f"  Manuscript states: {MANUSCRIPT_HEADLINE[ptype]['beta1_pct']}%"
    )

    # ---- 2. market-level DiD (compute_did, exactly as main.py/run.py call it) --
    did_estimates = compute_did(index_df, min_volume=cfg["did_min_volume"])
    did_estimates.did.to_csv(OUTDIR / f"market_level_did_{label}.csv")
    did_estimates.agg_ts.to_csv(OUTDIR / f"quarterly_agg_ts_{label}.csv")

    n_markets_did = len(did_estimates.did)
    n_neg_beta1 = int((did_estimates.did["DiD_beta1"] <= 0).sum())
    summary_lines.append(
        f"\n-- Market-level DiD (compute_did, min_volume={cfg['did_min_volume']}) --\n"
        f"  N markets after volume filter: {n_markets_did}\n"
        f"  DiD_beta1: mean={did_estimates.did['DiD_beta1'].mean():.4f}  "
        f"median={did_estimates.did['DiD_beta1'].median():.4f}  "
        f"std={did_estimates.did['DiD_beta1'].std():.4f}  "
        f"N<=0: {n_neg_beta1} ({100*n_neg_beta1/n_markets_did:.0f}%)\n"
        f"  DiD_delta: mean={did_estimates.did['DiD_delta'].mean():.4f}  "
        f"median={did_estimates.did['DiD_delta'].median():.4f}  "
        f"std={did_estimates.did['DiD_delta'].std():.4f}\n"
        f"  Manuscript quotes N markets variously as: {MANUSCRIPT_HEADLINE[ptype]['n_markets_various']}"
    )

    # ---- 3. market_stats (pi_hat, theta_bar, sigma0_hat) + e*_m, rho_hat, c0_hat
    try:
        df = pd.read_parquet(ROOT / cfg["listings_path"])
        if "group" not in df.columns:
            df = merge_datasets(df, ademe=None, epc_threshold=cfg["epc_threshold"],
                                 hider_theta=cfg.get("hider_theta", "registry"))
            df = classify_listings(df)
        market_stats = compute_market_stats(df, controls=cfg["controls"])
        market_stats = market_stats[market_stats["estimable"]].copy()
        summary_lines.append(f"\n  N estimable markets (from listings, compute_market_stats): {len(market_stats)}")

        did_params = estimate_rho_c0(did_estimates, market_stats)
        details = did_params.details.copy()
        details.to_csv(OUTDIR / f"rho_c0_details_{label}.csv")

        n_valid_rho = did_params.rho_m.notna().sum()
        n_clip_1 = int((did_params.rho_m == 1.0).sum())
        n_clip_0 = int((did_params.rho_m == 0.0).sum())
        summary_lines.append(
            f"  N markets with valid rho_hat: {n_valid_rho}\n"
            f"  rho_hat clipped at 1.0: {n_clip_1} ({100*n_clip_1/max(n_valid_rho,1):.0f}%)\n"
            f"  rho_hat clipped at 0.0: {n_clip_0} ({100*n_clip_0/max(n_valid_rho,1):.0f}%)\n"
            f"  c0_hat mean: {did_params.c0_m.mean():.4f}   beta1_hat mean (structural sample): {did_params.beta1_m.mean():.4f}\n"
            f"  [c0_hat mean > beta1_hat mean]: {did_params.c0_m.mean() > did_params.beta1_m.mean()}  "
            f"(should be impossible under c0_m = rho_m*beta1_m*e*_m with rho_m,e*_m in [0,1])"
        )
    except Exception as e:
        summary_lines.append(f"\n  [skipped market_stats/rho_c0 step: {e!r}]")


def main() -> None:
    summary_lines: list[str] = [
        "Event-study diagnostic — generated by scripts/diagnose_event_study.py",
        "Compares two DiD computations already present in this repo on the same underlying data.",
    ]
    for ptype, config_path in PROPERTY_TYPES:
        run_for_property(ptype, config_path, summary_lines)

    summary_text = "\n".join(summary_lines)
    (OUTDIR / "summary.txt").write_text(summary_text + "\n")
    print(summary_text)
    print(f"\n[diagnose_event_study] CSVs + summary.txt written to {OUTDIR}")


if __name__ == "__main__":
    main()
