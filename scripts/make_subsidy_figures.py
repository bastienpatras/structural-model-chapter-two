"""Paper-quality static matplotlib versions of the four subsidy figures.

Mirrors the Plotly counterparts in `src/outputs.py`:
  - figure_renovation_threshold_distribution
  - figure_subsidy_grid
  - figure_threshold_vs_beta1
  - figure_subsidy_regime_breakdown

Outputs PDFs to `paper/fig/visuals/`, styled to match the Metropolis-aligned
look of `scripts/make_fact5_map.py` (Fira Sans, pdf.fonttype=42, etc.) so the
figures embed cleanly in the LaTeX paper and the Beamer deck.

CLI
---
  python scripts/make_subsidy_figures.py [--out-dir paper/fig/visuals]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("/Users/bpatras/structural-model-chapter-two")
RESULTS = ROOT / "results"
DEFAULT_OUT = ROOT / "paper" / "fig" / "visuals"

# Palette ------------------------------------------------------------------
SPRED = "#d01c32"
SPRED_DARK = "#8b121f"
BBLUE = "#9BC1BC"
GREY = "#bdbdbd"
NAVY = "#1D3461"

REGIME_COLORS = {
    "mixed_strategy": NAVY,        # Partial Pooling
    "full_unraveling": BBLUE,      # Cost-Deterred Hiding
    "partial_separation": SPRED,   # Complete Adverse Selection
}
REGIME_LABELS = {
    "mixed_strategy": "Partial Pooling",
    "full_unraveling": "Cost-Deterred Hiding",
    "partial_separation": "Complete Adverse Selection",
}
REGIME_ORDER = ["mixed_strategy", "full_unraveling", "partial_separation"]

PROP_COLORS = {"apartment": NAVY, "house": SPRED}
PROP_LABELS = {"apartment": "Apartments", "house": "Houses"}

# Cost schemes (€/m²) included in the main-paper figures. The full grid in
# subsidy_grid.csv also contains 1000 €/m² for sensitivity; the paper focuses
# on these two benchmarks (light vs medium intervention).
MAIN_COSTS: list[float] = [250.0, 500.0]

# Font / rcParams ----------------------------------------------------------
try:
    found = fm.findfont("Fira Sans", fallback_to_default=False)
    if "FiraSans" not in os.path.basename(found):
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
    "axes.edgecolor": "#2b2b2b",
    "axes.labelcolor": "#2b2b2b",
    "xtick.color": "#2b2b2b",
    "ytick.color": "#2b2b2b",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "lines.linewidth": 1.6,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


# Data loaders -------------------------------------------------------------

def _load_grid(prop: str) -> pd.DataFrame:
    path = RESULTS / prop / "subsidy_grid.csv"
    return pd.read_csv(path)


def _market_estimates_from_grid(grid: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate the long-format grid to one row per market."""
    return (
        grid.sort_values(["market_id", "cost_per_m2"])
            .drop_duplicates(subset="market_id", keep="first")
            .reset_index(drop=True)
    )


def _ordered_regimes(values: pd.Series) -> list[str]:
    present = set(values.unique().tolist())
    return [r for r in REGIME_ORDER if r in present]


# Figure 1 -----------------------------------------------------------------

def make_threshold_distribution(out_dir: Path) -> Path:
    grid_apt = _load_grid("apartment")
    grid_hse = _load_grid("house")
    panels = [
        ("apartment", _market_estimates_from_grid(grid_apt)),
        ("house",     _market_estimates_from_grid(grid_hse)),
    ]

    x_min = min(df["R_bar_eur_per_m2"].min() for _, df in panels)
    x_max = max(df["R_bar_eur_per_m2"].max() for _, df in panels)
    pad = 0.03 * (x_max - x_min if x_max > x_min else 1.0)
    bin_edges = np.linspace(x_min - pad, x_max + pad, 21)  # 20 bins

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.2), sharey=False)
    medians: dict[str, float] = {}

    for ax, (prop, df) in zip(axes, panels):
        regimes = _ordered_regimes(df["regime"])
        stacks = [df.loc[df["regime"] == r, "R_bar_eur_per_m2"].to_numpy()
                  for r in regimes]
        colors = [REGIME_COLORS[r] for r in regimes]
        labels = [REGIME_LABELS[r] for r in regimes]
        ax.hist(
            stacks,
            bins=bin_edges,
            stacked=True,
            color=colors,
            label=labels,
            edgecolor="white",
            linewidth=0.4,
        )

        # Median: thin vertical line; the numeric value is reported in the
        # bottom legend rather than as an in-axes annotation (avoids the
        # overlap that small panel heights produce).
        med = float(df["R_bar_eur_per_m2"].median())
        medians[prop] = med
        ax.axvline(med, color="#2b2b2b", linestyle="--", linewidth=1.0,
                   zorder=5)

        ax.set_title(PROP_LABELS[prop], fontsize=10)
        ax.set_xlabel(r"Renovation threshold $\bar R_m$ (€/m²)", fontsize=9)
        ax.tick_params(axis="both", labelsize=8.5)
        ax.set_xlim(bin_edges[0], bin_edges[-1])

        # Compact N-by-regime annotation
        n_total = len(df)
        lines = [f"N = {n_total}"]
        for r in regimes:
            lines.append(f"{REGIME_LABELS[r]}: {(df['regime'] == r).sum()}")
        ax.text(
            0.97, 0.97, "\n".join(lines),
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=7.5, color="#2b2b2b",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="#dddddd", linewidth=0.4, alpha=0.9),
        )

    axes[0].set_ylabel("Number of markets", fontsize=9)

    # Single legend below both panels. Median values reported here.
    all_regimes = _ordered_regimes(
        pd.concat([df["regime"] for _, df in panels])
    )
    handles = [mpatches.Patch(color=REGIME_COLORS[r], label=REGIME_LABELS[r])
               for r in all_regimes]
    med_label = (
        f"Median  (apt: {medians.get('apartment', float('nan')):,.0f} €/m²; "
        f"hse: {medians.get('house', float('nan')):,.0f} €/m²)"
    )
    handles.append(plt.Line2D([0], [0], color="#2b2b2b", linestyle="--",
                              linewidth=1.0, label=med_label))
    fig.subplots_adjust(bottom=0.22)
    fig.legend(handles=handles, ncol=2, frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, -0.02),
               fontsize=8.5)

    out = out_dir / "fig_subsidy_threshold_distribution.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


# Figure 2 -----------------------------------------------------------------

def make_subsidy_grid(out_dir: Path) -> Path:
    grids = {
        "apartment": _load_grid("apartment"),
        "house":     _load_grid("house"),
    }
    available = sorted({
        float(c) for g in grids.values() for c in g["cost_per_m2"].unique()
    })
    cost_values = [c for c in MAIN_COSTS if c in available] or available

    # Per-column common x-range across rows.
    col_ranges: dict[float, tuple[float, float]] = {}
    for c in cost_values:
        vals = np.concatenate([
            g.loc[np.isclose(g["cost_per_m2"], c), "S_star_eur_per_m2"].to_numpy()
            for g in grids.values()
        ])
        lo, hi = float(vals.min()), float(vals.max())
        pad = 0.04 * (hi - lo if hi > lo else 1.0)
        col_ranges[c] = (lo - pad, hi + pad)

    n_rows, n_cols = 2, len(cost_values)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(10.0, 5.2),
        sharex="col", sharey=False,
    )

    for r, prop in enumerate(["apartment", "house"]):
        grid = grids[prop]
        color = PROP_COLORS[prop]
        for c, ch in enumerate(cost_values):
            ax = axes[r, c]
            sub = grid.loc[np.isclose(grid["cost_per_m2"], ch),
                           "S_star_eur_per_m2"].to_numpy()
            lo, hi = col_ranges[ch]
            bins = np.linspace(lo, hi, 19)  # 18 bins
            ax.hist(sub, bins=bins, color=color, edgecolor="white",
                    linewidth=0.4, alpha=0.9)

            # Median of markets that need a subsidy (S* > 0) — "the median
            # subsidy required". Falls back to overall median if all are zero.
            positive = sub[sub > 0]
            med = float(np.median(positive)) if positive.size else float(np.median(sub))
            ax.axvline(med, color="#2b2b2b", linestyle="--", linewidth=1.0,
                       zorder=5)
            y_top = ax.get_ylim()[1]
            ax.text(
                med, y_top * 0.95, f"  median = {med:,.0f}",
                ha="left", va="top", fontsize=7, color="#2b2b2b",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="none", alpha=0.85),
            )

            ax.set_xlim(lo, hi)

            if r == 0:
                ax.set_title(rf"$\hat R$ = {ch:.0f} €/m²")
            if r == n_rows - 1:
                ax.set_xlabel(r"$S^*_m$ (€/m²)")
            if c == 0:
                ax.set_ylabel(f"{PROP_LABELS[prop]}\nNumber of markets")

    fig.subplots_adjust(hspace=0.28, wspace=0.22, bottom=0.16)

    # Legend at bottom: just the median line indicator (bar fills are
    # property-type-coded by row label).
    handles = [plt.Line2D([0], [0], color="#2b2b2b", linestyle="--",
                          linewidth=1.0,
                          label="Median subsidy required (markets with $S^*>0$)")]
    fig.legend(handles=handles, ncol=1, frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, -0.02))

    out = out_dir / "fig_subsidy_grid.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


# Figure 3 -----------------------------------------------------------------

def make_threshold_vs_beta1(out_dir: Path) -> Path:
    grid_apt = _load_grid("apartment")
    grid_hse = _load_grid("house")
    panels = [
        ("apartment", _market_estimates_from_grid(grid_apt)),
        ("house",     _market_estimates_from_grid(grid_hse)),
    ]

    all_vals = pd.concat([df for _, df in panels])
    lo = float(min(all_vals["R_bar_log_pts"].min(),
                   all_vals["beta_1_m"].min(), 0.0))
    hi = float(max(all_vals["R_bar_log_pts"].max(),
                   all_vals["beta_1_m"].max()) * 1.05)

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.5))

    for ax, (prop, df) in zip(axes, panels):
        # 45° reference line first (background).
        ax.plot([lo, hi], [lo, hi], color="#7f7f7f", linestyle="--",
                linewidth=0.9, zorder=1, label="45°")
        regimes = _ordered_regimes(df["regime"])
        for r in regimes:
            sub = df[df["regime"] == r]
            ax.scatter(
                sub["beta_1_m"], sub["R_bar_log_pts"],
                s=24, color=REGIME_COLORS[r], alpha=0.85,
                edgecolor="white", linewidth=0.4,
                label=REGIME_LABELS[r], zorder=2,
            )
        ax.set_title(PROP_LABELS[prop])
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(r"$\hat\beta_{1,m}$ (log price points)")

    axes[0].set_ylabel(r"$\bar R^{\mathrm{log}}_m$ (log price points)")

    # Union legend (regimes present in either panel + 45° line).
    all_regimes = _ordered_regimes(pd.concat([df["regime"] for _, df in panels]))
    handles = [mpatches.Patch(color=REGIME_COLORS[r], label=REGIME_LABELS[r])
               for r in all_regimes]
    handles.append(plt.Line2D([0], [0], color="#7f7f7f", linestyle="--",
                              linewidth=0.9, label="45° line"))
    fig.subplots_adjust(bottom=0.24)
    fig.legend(handles=handles, ncol=len(handles), frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, -0.02))

    out = out_dir / "fig_subsidy_threshold_vs_beta1.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


# Figure 4 -----------------------------------------------------------------

def make_regime_breakdown(out_dir: Path) -> Path:
    """Per cost scheme, share of markets in each category, summing to 100 %.

    Categories: Partial Pooling with S*>0, Cost-Deterred Hiding with S*>0,
    Complete Adverse Selection with S*>0, and a residual "No subsidy needed"
    bucket (markets where the threshold already exceeds R̂). All categories
    are coloured by regime; the "no subsidy" bucket is neutral grey.
    """
    grids = {
        "apartment": _load_grid("apartment"),
        "house":     _load_grid("house"),
    }
    no_sub_color = "#bdbdbd"
    no_sub_label = "No subsidy needed ($S^*=0$)"

    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.8), sharey=True)

    for ax, prop in zip(axes, ["apartment", "house"]):
        grid       = grids[prop]
        grid       = grid[grid["cost_per_m2"].isin(MAIN_COSTS)].copy()
        all_estim  = _market_estimates_from_grid(grid)
        n_total    = max(len(all_estim), 1)

        # counts[ (regime, cost) ] = # markets in `regime` with S*>0 at `cost`
        positive = grid[grid["S_star_eur_per_m2"] > 0]
        counts = (
            positive.groupby(["cost_per_m2", "regime"])
                    .size().unstack(fill_value=0)
                    .sort_index()
        )
        # No-subsidy = N_total - positive count at that cost
        n_positive_total = positive.groupby("cost_per_m2").size().sort_index()
        cost_levels = counts.index.tolist()
        x = np.arange(len(cost_levels))

        # Convert to percentages of total markets in that property type
        shares = 100.0 * counts.to_numpy(dtype=float) / float(n_total)
        no_sub = 100.0 * (n_total - n_positive_total.reindex(cost_levels)
                          .fillna(0).to_numpy()) / float(n_total)

        bottom = np.zeros(len(cost_levels))
        regimes_present = [r for r in REGIME_ORDER if r in counts.columns]
        for j, r in enumerate(regimes_present):
            vals = shares[:, list(counts.columns).index(r)]
            ax.bar(x, vals, bottom=bottom, color=REGIME_COLORS[r],
                   edgecolor="white", linewidth=0.4,
                   label=REGIME_LABELS[r] + r" — $S^*>0$", width=0.7)
            bottom += vals
        ax.bar(x, no_sub, bottom=bottom, color=no_sub_color,
               edgecolor="white", linewidth=0.4,
               label=no_sub_label, width=0.7)

        for xi in x:
            ax.text(xi, 100.5, "100%",
                    ha="center", va="bottom",
                    fontsize=7.5, color="#2b2b2b")

        ax.set_xticks(x)
        ax.set_xticklabels([f"{int(c)}" for c in cost_levels])
        ax.set_xlabel(r"$\hat R$ (€/m²)")
        ax.set_title(PROP_LABELS[prop])
        ax.set_ylim(0, 108)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.grid(axis="x", visible=False)

    axes[0].set_ylabel("Share of markets")

    # Build a single legend with regimes + no-subsidy
    all_regimes = _ordered_regimes(
        pd.concat([g["regime"] for g in grids.values()])
    )
    handles = [mpatches.Patch(color=REGIME_COLORS[r],
                              label=REGIME_LABELS[r] + r" — $S^*>0$")
               for r in all_regimes]
    handles.append(mpatches.Patch(color=no_sub_color, label=no_sub_label))
    fig.subplots_adjust(bottom=0.30)
    fig.legend(handles=handles, ncol=min(len(handles), 3), frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, -0.02))

    out = out_dir / "fig_subsidy_regime_breakdown.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


# CLI ----------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    out_dir: Path = args.out_dir
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for fn in (
        make_threshold_distribution,
        make_subsidy_grid,
        make_threshold_vs_beta1,
        make_regime_breakdown,
    ):
        path = fn(out_dir)
        print(f"[wrote] {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
