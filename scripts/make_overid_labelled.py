"""
Labelled version of the over-identification scatter (paper Figure 8) for a
backup slide: same data and styling as make_did_figures.make_rho_saturation,
plus callout labels for the markets farthest from the 45-degree line, the one
closest to it, and the largest cities.

Market names come from data/geo/market_names.csv (INSEE commune code of each
market's centre, resolved with geo.api.gouv.fr).

Output: paper/fig/visuals/fig_rho_saturation_scatter_labelled.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_did_figures import (  # noqa: E402
    DEFAULT_OUT, GREY, INK, PALE_ROSE, PROP_COLORS, PROP_LABELS, PROP_MARKERS,
    PROPERTIES, ROOT, SPRED, _anchored,
)

NAMES = pd.read_csv(ROOT / "data" / "geo" / "market_names.csv", dtype={"market_id": str})

# Which markets to label, per property type: farthest above / below the line,
# closest to it, and the largest cities (so the audience can locate them).
LABELS = {
    "apartment": {
        "far": ["Mulhouse", "Clermont-Ferrand", "Nîmes", "Le Havre", "Reims", "Brive-la-Gaillarde"],
        "close": ["Besançon"],
        "big": ["Paris", "Lyon", "Marseille", "Bordeaux", "Rennes"],
    },
    "house": {
        "far": ["Colmar", "Dunkerque", "Béthune", "Troyes", "Bergerac", "Niort"],
        "close": ["Dijon"],
        "big": ["Paris", "Lyon", "Lille", "Nantes", "Bordeaux"],
    },
}
GROUP_COLORS = {"far": SPRED, "close": "#2d7d46", "big": INK}


def _spread(y: np.ndarray, gap: float, lo: float, hi: float) -> np.ndarray:
    """Push sorted label positions apart so consecutive ones are >= gap apart."""
    out = y.copy()
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + gap)
    if out[-1] > hi:                       # shift the whole column back down
        out -= out[-1] - hi
        for i in range(len(out) - 2, -1, -1):
            out[i] = min(out[i], out[i + 1] - gap)
    return np.clip(out, lo, hi)


def make_labelled(out_dir: Path) -> Path:
    frames = {prop: _anchored(prop) for prop, _ in PROPERTIES}
    for prop, df in frames.items():
        df["mid"] = df["market_id"].str.zfill(5)
        frames[prop] = df.merge(NAMES, left_on="mid", right_on="market_id",
                                how="left", suffixes=("", "_n"))
    allv = pd.concat(frames.values())

    span = float(max(allv["x"].max(), allv["y"].max())
                 - min(allv["x"].min(), allv["y"].min()))
    pad = 0.06 * span
    lo = float(min(allv["x"].min(), allv["y"].min())) - pad
    y_hi = float(allv["y"].max()) + pad
    col_x = float(allv["x"].max()) + 0.045         # callout column
    x_hi = col_x + 0.175

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.0), sharey=True)
    for ax, (prop, _) in zip(axes, PROPERTIES):
        df = frames[prop]
        ax.fill_between([lo, x_hi], [lo, x_hi], [y_hi, y_hi],
                        color=PALE_ROSE, alpha=0.8, linewidth=0, zorder=0)
        ax.plot([lo, x_hi], [lo, x_hi], color=GREY, linestyle="--", linewidth=0.9, zorder=2)
        ax.axhline(0.0, color="#cccccc", linewidth=0.6, zorder=1)
        ax.axvline(0.0, color="#cccccc", linewidth=0.6, zorder=1)
        ax.scatter(df["x"], df["y"], s=20, color=PROP_COLORS[prop],
                   marker=PROP_MARKERS[prop], alpha=0.55,
                   edgecolor="white", linewidth=0.4, zorder=3)

        rows = []
        for group, names in LABELS[prop].items():
            for name in names:
                r = df[df["name"] == name]
                if len(r) != 1:
                    raise ValueError(f"{prop}: market {name!r} not found once")
                r = r.iloc[0]
                rows.append((float(r["y"]), float(r["x"]), name, group,
                             100 * (r["y"] - r["x"])))
        rows.sort()
        ys = _spread(np.array([r[0] for r in rows]), gap=0.021, lo=lo + 0.01, hi=y_hi - 0.01)
        for (y, x, name, group, gap), ly in zip(rows, ys):
            c = GROUP_COLORS[group]
            ax.scatter([x], [y], s=26, color=PROP_COLORS[prop], marker=PROP_MARKERS[prop],
                       edgecolor=c, linewidth=1.1, zorder=4)
            ax.plot([x, col_x - 0.004], [y, ly], color=c, linewidth=0.45, alpha=0.7, zorder=3)
            ax.text(col_x, ly, f"{name} ({gap:+.1f})", fontsize=7.6, color=c,
                    va="center", ha="left", zorder=5,
                    bbox=dict(boxstyle="square,pad=0.08", facecolor="white", edgecolor="none", alpha=0.85))

        ax.set_xlim(lo, x_hi)
        ax.set_ylim(lo, y_hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(PROP_LABELS[prop], fontsize=10.5, color=INK)
        ax.set_xlabel(r"$\hat\beta_{1,m}\,\hat e^{*}_{m}$  (log price points)")
    axes[0].set_ylabel(r"$\hat\Delta_m$  (log price points)")

    handles = [
        plt.Line2D([0], [0], color=GREY, linestyle="--", linewidth=0.9,
                   label=r"45° line: observed $=$ predicted"),
        plt.Line2D([0], [0], marker="o", linestyle="", markerfacecolor="white",
                   markeredgecolor=SPRED, markeredgewidth=1.1, color=SPRED,
                   label="far from the line"),
        plt.Line2D([0], [0], marker="o", linestyle="", markerfacecolor="white",
                   markeredgecolor=GROUP_COLORS["close"], markeredgewidth=1.1,
                   label="closest to the line"),
        plt.Line2D([0], [0], marker="o", linestyle="", markerfacecolor="white",
                   markeredgecolor=INK, markeredgewidth=1.1, label="large cities"),
    ]
    fig.subplots_adjust(bottom=0.15, wspace=0.08)
    fig.legend(handles=handles, ncol=4, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8)

    out = out_dir / "fig_rho_saturation_scatter_labelled.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(f"[wrote] {make_labelled(DEFAULT_OUT)}")
