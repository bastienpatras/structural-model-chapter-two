"""Paper-quality static figures for the July 2021 DPE-disclosure event study.

Two exhibits, both built from this repository's own current pipeline:

  1. ``fig_did_event_study.pdf`` — monthly trajectories of the two log-price
     gaps that the DiD identifies, by property type:

         beta_1,m,t = log p_ABCD,m,t - log p_EFG,m,t   (disclosed quality gap)
         Delta_m,t  = log p_undisclosed,m,t - log p_EFG,m,t  (non-disclosure gap)

     Computed with the canonical methodology of ``src/event_study.py``: the
     ``prices`` column (hedonic price LEVEL, EUR/m2) of ``data/index_*.csv``,
     the ``high_group='ABCD'`` merge, and the ``compute_did`` volume filter.
     The ``final_index`` growth-rate alternative is deliberately NOT used —
     see the docstring of ``src/event_study.py``.

  2. ``fig_rho_saturation_scatter.pdf`` — market-level scatter of Delta_hat_m
     against beta_1_hat_m * e_star_hat_m with a 45-degree reference line.
     Points above the line are markets where the old ratio estimator
     rho_hat_m = Delta_hat_m / (beta_1_hat_m * e_star_hat_m) exceeded one and
     had to be clipped, i.e. where that estimator carried no information.
     Inputs are the CURRENT post-fix per-market estimates in
     ``results/{apartment,house}/anchored_diagnostics.csv``.

Styling follows ``scripts/make_subsidy_figures.py`` / ``scripts/make_fact5_map.py``
(Metropolis-aligned: Fira Sans, SPred/navy palette, pdf.fonttype=42).

CLI
---
  python scripts/make_did_figures.py [--out-dir paper/fig/visuals]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.event_study import REFORM_DATE, compute_did, load_price_indices  # noqa: E402

RESULTS = ROOT / "results"
DEFAULT_OUT = ROOT / "paper" / "fig" / "visuals"

# Palette (shared with scripts/make_subsidy_figures.py) ---------------------
SPRED = "#d01c32"
NAVY = "#1D3461"
INK = "#2b2b2b"
GREY = "#7f7f7f"
PALE_ROSE = "#fdecef"   # lightest step of the SPred ramp in make_fact5_map.py

PROP_COLORS = {"apartment": NAVY, "house": SPRED}
PROP_LABELS = {"apartment": "Apartments", "house": "Houses"}
PROP_MARKERS = {"apartment": "o", "house": "^"}

PROPERTIES: list[tuple[str, str]] = [
    ("apartment", "config_apartment.json"),
    ("house", "config_house.json"),
]

# Series styling for figure 1. Colour AND linestyle differ, so the panels stay
# readable in greyscale and for colour-vision-deficient readers.
BETA1_STYLE = dict(color=NAVY, linestyle="--", linewidth=1.6)
DELTA_STYLE = dict(color=SPRED, linestyle="-", linewidth=1.8)

CI_Z = 1.96

# Font / rcParams ----------------------------------------------------------
try:
    _found = fm.findfont("Fira Sans", fallback_to_default=False)
    if "FiraSans" not in os.path.basename(_found):
        print("[fonts] Fira Sans not found — falling back to DejaVu Sans.")
except Exception:
    print("[fonts] Fira Sans not found — falling back to DejaVu Sans.")

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Fira Sans", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "lines.linewidth": 1.6,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.transparent": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def _config(config_name: str) -> dict:
    return json.loads((ROOT / config_name).read_text())


def event_study_panel(config_name: str) -> tuple[pd.DataFrame, dict]:
    """Monthly cross-market gap trajectories for one property type.

    Uses exactly the ``src/event_study.py`` pipeline: ``load_price_indices``
    (log of the ``prices`` level, Efficient+Balanced merged into the high
    group by volume-weighted price level) and the ``compute_did`` volume
    filter, then averages the market-level monthly gaps across the surviving
    markets.

    Returns
    -------
    ts   : DataFrame indexed by month with columns
           beta1, beta1_lo, beta1_hi, delta, delta_lo, delta_hi, n_markets
    meta : dict with the market count and the headline DiD magnitudes, which
           are the pre/post contrast of the plotted series.
    """
    cfg = _config(config_name)
    index_df = load_price_indices(
        str(ROOT / cfg["index_path"]), high_group=cfg.get("high_group", "ABCD")
    )
    did = compute_did(index_df, min_volume=cfg["did_min_volume"])
    keep = set(did.did.index)

    wide = (
        index_df[index_df["market_id"].isin(keep)]
        .pivot_table(index=["market_id", "date"], columns="epc_cat", values="log_index")
        .reset_index()
    )
    wide.columns.name = None
    wide["beta1_t"] = wide["ABC"] - wide["EFG"]          # disclosed quality gap
    wide["delta_t"] = wide["undisclosed"] - wide["EFG"]  # non-disclosure gap

    # Uncertainty band: the estimand is the MOVEMENT of each gap, not its
    # level, so the band must not carry the cross-market dispersion of levels
    # (a market fixed effect that differences out). Each market's series is
    # therefore demeaned by its own pre-reform average before the standard
    # error is taken; on the balanced panel this recentres the band exactly on
    # the plotted level series.
    pre_mask = wide["date"] < REFORM_DATE
    pre_means = (
        wide[pre_mask].groupby("market_id")[["beta1_t", "delta_t"]].mean()
        .rename(columns={"beta1_t": "beta1_pre_m", "delta_t": "delta_pre_m"})
    )
    wide = wide.join(pre_means, on="market_id")
    wide["beta1_dev"] = wide["beta1_t"] - wide["beta1_pre_m"]
    wide["delta_dev"] = wide["delta_t"] - wide["delta_pre_m"]

    grp = wide.groupby("date")
    ts = pd.DataFrame({
        "beta1": grp["beta1_t"].mean(),           # skipna=True, stated explicitly below
        "delta": grp["delta_t"].mean(),
        "beta1_se": grp["beta1_dev"].sem(),
        "delta_se": grp["delta_dev"].sem(),
        "n_markets": grp["market_id"].nunique(),
    })
    for col in ("beta1", "delta"):
        ts[f"{col}_lo"] = ts[col] - CI_Z * ts[f"{col}_se"]
        ts[f"{col}_hi"] = ts[col] + CI_Z * ts[f"{col}_se"]

    meta = {
        "n_markets": len(keep),
        "did_beta1": float(did.did["DiD_beta1"].mean()),
        "did_delta": float(did.did["DiD_delta"].mean()),
        "n_months": int(ts.shape[0]),
        "date_min": ts.index.min(),
        "date_max": ts.index.max(),
        # Market-months where a category is missing, so the monthly mean is
        # taken over slightly fewer markets (reported, not silently dropped).
        "n_missing_beta1": int(wide["beta1_t"].isna().sum()),
        "n_missing_delta": int(wide["delta_t"].isna().sum()),
        "n_market_months": int(len(wide)),
    }
    return ts, meta


# ---------------------------------------------------------------------------
# Figure 1 — event-study trajectories
# ---------------------------------------------------------------------------

def make_event_study(out_dir: Path) -> tuple[Path, dict]:
    panels = {prop: event_study_panel(cfg) for prop, cfg in PROPERTIES}

    fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.6), sharex=True)

    for ax, (prop, _) in zip(axes, PROPERTIES):
        ts, meta = panels[prop]

        # Pre-reform period shaded, so the pre-trend check is the visual anchor.
        ax.axvspan(ts.index.min(), REFORM_DATE, color="#f4f4f4", zorder=0)
        ax.axhline(0.0, color=GREY, linewidth=0.8, linestyle=":", zorder=1)
        ax.axvline(REFORM_DATE, color=INK, linewidth=1.0, linestyle="--", zorder=2)

        ax.fill_between(ts.index, ts["delta_lo"], ts["delta_hi"],
                        color=SPRED, alpha=0.18, linewidth=0, zorder=2)
        ax.fill_between(ts.index, ts["beta1_lo"], ts["beta1_hi"],
                        color=NAVY, alpha=0.15, linewidth=0, zorder=2)
        ax.plot(ts.index, ts["delta"], zorder=4,
                label=r"$\Delta_{m,t}$  (undisclosed $-$ E/F/G)", **DELTA_STYLE)
        ax.plot(ts.index, ts["beta1"], zorder=3,
                label=r"$\beta_{1,m,t}$  (A–D $-$ E/F/G)", **BETA1_STYLE)

        ax.set_title(f"{PROP_LABELS[prop]}   ($N = {meta['n_markets']}$ markets)",
                     loc="left", fontsize=10.5, color=INK)
        ax.set_ylabel("Log price gap")

        ax.text(
            0.015, 0.95,
            f"Post $-$ pre:  $\\Delta$ {100 * meta['did_delta']:+.1f} log pts"
            f"   ·   $\\beta_1$ {100 * meta['did_beta1']:+.1f} log pts",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=8, color=INK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#dddddd", linewidth=0.4, alpha=0.92),
        )

    # Reform label, on the top panel only.
    top = axes[0]
    top.annotate(
        "DPE reform\n1 July 2021",
        xy=(REFORM_DATE, top.get_ylim()[1]),
        xytext=(6, -4), textcoords="offset points",
        ha="left", va="top", fontsize=8, color=INK,
    )

    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].xaxis.set_minor_locator(mdates.MonthLocator(bymonth=(1, 7)))
    # No x-axis label: the tick labels are calendar years and the series are
    # explicitly described as monthly in the legend and caption.
    t_index = panels["apartment"][0].index
    axes[-1].set_xlim(t_index.min() - pd.Timedelta(days=30),
                      t_index.max() + pd.Timedelta(days=30))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.subplots_adjust(hspace=0.22, bottom=0.14)
    fig.legend(handles=handles, labels=labels, ncol=2, frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, -0.02), fontsize=8.5)

    out = out_dir / "fig_did_event_study.pdf"
    fig.savefig(out)
    plt.close(fig)

    diag = {prop: panels[prop][1] for prop, _ in PROPERTIES}
    return out, diag


# ---------------------------------------------------------------------------
# Figure 2 — rho saturation scatter
# ---------------------------------------------------------------------------

def _anchored(prop: str) -> pd.DataFrame:
    df = pd.read_csv(RESULTS / prop / "anchored_diagnostics.csv",
                     dtype={"market_id": str})
    df["x"] = df["DiD_beta1"] * df["e_star"]   # beta_1_hat_m * e*_hat_m
    df["y"] = df["DiD_delta"]                  # Delta_hat_m
    return df


def make_rho_saturation(out_dir: Path) -> tuple[Path, dict]:
    frames = {prop: _anchored(prop) for prop, _ in PROPERTIES}
    allv = pd.concat(frames.values())

    # Both axes carry the same units and the SAME data-per-inch scale
    # (aspect="equal"), so the y = x line is drawn at a true 45 degrees. The
    # frame is cropped to the data rather than forced square: Delta_hat_m
    # ranges roughly three times as wide as beta_1_hat_m * e*_hat_m, and that
    # asymmetry is the point of the figure. Neither axis is truncated — every
    # market of both property types lies inside the frame.
    span = float(max(allv["x"].max(), allv["y"].max())
                 - min(allv["x"].min(), allv["y"].min()))
    pad = 0.06 * span
    lo = float(min(allv["x"].min(), allv["y"].min())) - pad
    x_hi = float(allv["x"].max()) + pad + 0.35 * abs(lo)
    y_hi = float(allv["y"].max()) + pad

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 4.6), sharey=True)

    diag: dict[str, dict] = {}
    for ax, (prop, _) in zip(axes, PROPERTIES):
        df = frames[prop]
        n_above = int((df["y"] > df["x"]).sum())
        diag[prop] = {"n": len(df), "n_above": n_above,
                      "share_above": n_above / len(df)}

        # Shaded region: markets where the observed premium exceeds the
        # model-predicted one (Delta_hat_m > beta_1_hat_m * e*_hat_m), i.e.
        # where the over-identifying restriction fails upward. rho_m does not
        # enter either axis.
        ax.fill_between([lo, x_hi], [lo, x_hi], [y_hi, y_hi],
                        color=PALE_ROSE, alpha=0.8, linewidth=0, zorder=0)
        ax.plot([lo, x_hi], [lo, x_hi], color=GREY, linestyle="--", linewidth=0.9,
                zorder=2, label="Observed $=$ predicted")
        ax.axhline(0.0, color="#cccccc", linewidth=0.6, zorder=1)
        ax.axvline(0.0, color="#cccccc", linewidth=0.6, zorder=1)

        ax.scatter(df["x"], df["y"], s=22, color=PROP_COLORS[prop],
                   marker=PROP_MARKERS[prop], alpha=0.85,
                   edgecolor="white", linewidth=0.4, zorder=3,
                   label=PROP_LABELS[prop])

        ax.set_xlim(lo, x_hi)
        ax.set_ylim(lo, y_hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(PROP_LABELS[prop], fontsize=10.5, color=INK)
        ax.set_xlabel(r"$\hat\beta_{1,m}\,\hat e^{*}_{m}$  (log price points)")
        ax.text(
            0.035, 0.975,
            f"$N = {len(df)}$\nabove 45°: {n_above} "
            f"({100 * n_above / len(df):.0f}%)",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=8, color=INK,
            bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                      edgecolor="#dddddd", linewidth=0.4, alpha=0.92),
        )

    axes[0].set_ylabel(r"$\hat\Delta_m$  (log price points)")

    handles = [
        plt.Line2D([0], [0], color=GREY, linestyle="--", linewidth=0.9,
                   label=r"45° line: observed $=$ predicted ($\hat\Delta_m = \hat\beta_{1,m}\hat e^{*}_m$)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=PALE_ROSE,
                      edgecolor="#e6c8ce", linewidth=0.4,
                      label=r"Silence earns more than predicted"),
    ]
    fig.subplots_adjust(bottom=0.20, wspace=0.14)
    fig.legend(handles=handles, ncol=2, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.5)

    out = out_dir / "fig_rho_saturation_scatter.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out, diag


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--quiet", action="store_true",
                        help="suppress src.event_study INFO logging")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING if args.quiet else logging.INFO,
                        format="%(message)s")

    out_dir: Path = args.out_dir
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    es_path, es_diag = make_event_study(out_dir)
    print(f"[wrote] {es_path}")
    for prop, m in es_diag.items():
        print(f"  {prop:<9} N={m['n_markets']:>3} markets  "
              f"{m['n_months']} months  "
              f"{m['date_min']:%Y-%m} → {m['date_max']:%Y-%m}  "
              f"DiD_delta={m['did_delta']:+.4f}  DiD_beta1={m['did_beta1']:+.4f}  "
              f"missing market-months: beta1={m['n_missing_beta1']}, "
              f"delta={m['n_missing_delta']} of {m['n_market_months']}")

    sc_path, sc_diag = make_rho_saturation(out_dir)
    print(f"[wrote] {sc_path}")
    for prop, m in sc_diag.items():
        print(f"  {prop:<9} N={m['n']:>3} markets  "
              f"above 45°: {m['n_above']} ({100 * m['share_above']:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
