"""
Price-levels figures for the mandatory EPC disclosure paper.

Two separate single-panel figures (one per property type), styled identically
to the event-study reference figure
(fig/stylized_facts/apartment/fig_fact1_nondiscl_premium_eventstudy.pdf).

Y-axis : volume-weighted national average price per m2 (EUR)
X-axis : listing month (2019-01-01 .. 2024-06-30), year ticks only
Series : 3-month centred rolling mean per EPC category.

Target medium: LaTeX full-width / Beamer full figure.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

# ---------------------------------------------------------------------------
# Metropolis-aligned rcParams (matching the event-study reference)
# ---------------------------------------------------------------------------
SPRED = "#d01c32"   # non-disclosed
BBLUE = "#9BC1BC"   # balanced
GREEN = "#2d7d46"   # efficient
GREY = "#555555"    # energy-intensive

try:
    font_manager.findfont("Fira Sans", fallback_to_default=False)
    _font = "Fira Sans"
except Exception:
    _font = "DejaVu Sans"
    print("[warn] Fira Sans not found -> falling back to DejaVu Sans. "
          "Install via 'brew install --cask font-fira-sans'.")

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [_font, "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#2b2b2b",
    "axes.labelcolor": "#2b2b2b",
    "xtick.color": "#2b2b2b",
    "ytick.color": "#2b2b2b",
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.5,
    "lines.linewidth": 1.6,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.transparent": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
DATA_DIR = Path("/Users/bpatras/structural-model-chapter-two/data")
FIG_DIR = Path("/Users/bpatras/structural-model-chapter-two/paper/fig/stylized_facts")

START = pd.Timestamp("2019-01-01")
END = pd.Timestamp("2024-06-30")
REFORM = pd.Timestamp("2021-07-01")

# (EPC value, label, color, linewidth, linestyle)
SERIES = [
    ("Missing",   "Non-disclosed",            SPRED, 2.0, "-"),
    ("Efficient", "Efficient (A/B/C)",        GREEN, 1.6, "-"),
    ("Balanced",  "Balanced (D)",             BBLUE, 1.4, "--"),
    ("Intensive", "Energy-intensive (E/F/G)", GREY,  1.4, "-."),
]

OUT = {
    "APARTMENT": FIG_DIR / "apartment" / "fig_price_levels",
    "HOUSE": FIG_DIR / "house" / "fig_price_levels",
}


def load_panel(item_type: str) -> pd.DataFrame:
    """Volume-weighted national price level per (date, EPC), 3m centred MA."""
    fname = "index_APARTMENT.csv" if item_type == "APARTMENT" else "index_HOUSE.csv"
    df = pd.read_csv(DATA_DIR / fname, parse_dates=["date"])
    df = df[df["item_type"] == item_type].copy()

    df["pv"] = df["prices"] * df["volume"]
    agg = (
        df.groupby(["date", "EPC"], as_index=False)
        .agg(pv=("pv", "sum"), vol=("volume", "sum"))
    )
    agg["price"] = agg["pv"] / agg["vol"]
    agg = agg[(agg["date"] >= START) & (agg["date"] <= END)]

    # 3-month centred rolling mean within each EPC series
    agg = agg.sort_values(["EPC", "date"])
    agg["price_smooth"] = (
        agg.groupby("EPC")["price"]
        .transform(lambda s: s.rolling(window=3, center=True, min_periods=1).mean())
    )
    return agg


def make_figure(item_type: str, agg: pd.DataFrame, slide: bool = False):
    """slide=True drops the Balanced (D) series, which blurs the slide message,
    and writes a separate *_slide file so the paper figure is unchanged."""
    fig, ax = plt.subplots(figsize=(6.5, 3.6))

    for epc, label, color, lw, ls in SERIES:
        if slide and epc == "Balanced":
            continue
        s = agg[agg["EPC"] == epc].sort_values("date")
        ax.plot(s["date"], s["price_smooth"], color=color, lw=lw, ls=ls,
                label=label, solid_capstyle="round")

    # DPE reform marker
    ax.axvline(REFORM, color="#2b2b2b", lw=0.9, ls="--")
    _, ymax = ax.get_ylim()
    ax.text(REFORM, ymax, " DPE reform", rotation=90, va="top", ha="left",
            fontsize=8, color="#2b2b2b")

    ax.set_ylabel("Price per m$^2$ (€, volume-weighted)")
    ax.set_xlabel("Listing month")
    ax.set_xlim(START, END)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.margins(x=0.01)

    ax.legend(frameon=False, loc="upper left")

    stem = OUT[item_type]
    if slide:
        stem = stem.with_name(stem.name + "_slide")
    stem.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = stem.with_suffix(".pdf")
    png_path = stem.with_suffix(".png")
    fig.savefig(pdf_path, dpi=300, bbox_inches="tight")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[saved] {pdf_path}")
    print(f"[saved] {png_path}")


def main():
    order = ["Missing", "Efficient", "Balanced", "Intensive"]
    labels = {e: l for e, l, *_ in SERIES}

    for item_type, name in (("APARTMENT", "Apartments"), ("HOUSE", "Houses")):
        agg = load_panel(item_type)
        make_figure(item_type, agg)
        make_figure(item_type, agg, slide=True)

        last_date = agg["date"].max()
        print(f"\nFinal price levels for {name} ({last_date.date()}, 3m MA):")
        snap = agg[agg["date"] == last_date].set_index("EPC")
        for epc in order:
            if epc in snap.index:
                print(f"  {labels[epc]:<26s} {snap.loc[epc, 'price_smooth']:>10,.0f} €/m2")
        print()


if __name__ == "__main__":
    main()
