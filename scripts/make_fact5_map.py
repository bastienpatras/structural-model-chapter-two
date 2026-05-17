"""Fact 5 — Non-disclosure rate by département (apartments and houses).

Parameterized over property type. Outputs to
`paper/fig/stylized_facts/{apartment,house}/fig_fact5_nondiscl_rate_map.pdf`.

Standards: Metropolis-aligned (Fira Sans), Lambert-93 (EPSG:2154), quantile
classification (k=5), viridis sequential colormap, colorblind-safe.
"""

from __future__ import annotations

import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import geopandas as gpd
import mapclassify

ROOT = Path("/Users/bpatras/structural-model-chapter-two")
GEO_CACHE = ROOT / "data" / "geo" / "departements.geojson"
GEO_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
    "master/departements.geojson"
)

SPRED = "#d01c32"
BBLUE = "#9BC1BC"   # noqa: F841

# Five-step sequential palette in the SPred family. Light at the low end,
# pure SPred mid-high, darker shade at the top. Matches the rest of the
# paper's Metropolis-aligned palette.
SPRED_RAMP_5 = [
    "#fdecef",  # very pale
    "#f1b6c0",  # pale rose
    "#e07b8a",  # rose
    "#d01c32",  # SPred
    "#8b121f",  # dark wine
]

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
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


@dataclass
class PropertyConfig:
    code: str
    folder: str
    min_listings: int


CONFIGS = [
    PropertyConfig(code="APARTMENT", folder="apartment", min_listings=200),
    PropertyConfig(code="HOUSE", folder="house", min_listings=200),
]


def load_rates(parquet_path: Path, min_listings: int) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path, columns=["dept", "d"])
    df["dept"] = df["dept"].astype(str).str.strip()
    agg = (
        df.groupby("dept")
        .agg(n_listings=("d", "size"), d_mean=("d", "mean"))
        .reset_index()
    )
    agg["nondiscl_rate"] = 1.0 - agg["d_mean"]
    kept = agg[agg["n_listings"] >= min_listings].copy()
    dropped = agg[agg["n_listings"] < min_listings].copy()
    print(
        f"[data] kept {len(kept)} départements (>= {min_listings} listings); "
        f"dropped {len(dropped)}: {sorted(dropped['dept'].tolist())}"
    )
    return kept


def load_geometry(cache: Path, url: str) -> gpd.GeoDataFrame:
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        print(f"[geo] downloading {url} -> {cache}")
        with urllib.request.urlopen(url, timeout=60) as resp:
            cache.write_bytes(resp.read())
    else:
        print(f"[geo] using cached {cache}")
    gdf = gpd.read_file(cache)
    if "code" not in gdf.columns:
        raise RuntimeError(f"GeoJSON missing 'code' column; got {list(gdf.columns)}")
    gdf["code"] = gdf["code"].astype(str)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf


def plot_choropleth(
    gdf: gpd.GeoDataFrame,
    classifier: mapclassify.MapClassifier,
    outpath: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    is_dom = gdf["code"].str.startswith("97")
    metro = gdf.loc[~is_dom].copy()

    metro.plot(ax=ax, color="#f0f0f0", edgecolor="none", linewidth=0)
    has_data = metro.dropna(subset=["nondiscl_rate"]).copy()

    cmap_discrete = mpl.colors.ListedColormap(SPRED_RAMP_5, name="spred5")
    has_data.plot(
        ax=ax,
        column="nondiscl_rate",
        cmap=cmap_discrete,
        scheme="UserDefined",
        classification_kwds={"bins": list(classifier.bins)},
        edgecolor="none",
        linewidth=0,
        legend=False,
    )

    paris = metro.loc[metro["code"] == "75"]
    if not paris.empty:
        c = paris.geometry.iloc[0].centroid
        ax.annotate(
            "Paris",
            xy=(c.x, c.y),
            xytext=(c.x + 60_000, c.y + 80_000),
            fontsize=8,
            color="#2b2b2b",
            arrowprops=dict(arrowstyle="-", color="#2b2b2b", lw=0.4, shrinkA=0, shrinkB=0),
        )

    ax.set_axis_off()
    ax.set_aspect("equal")

    # Map-style discrete legend: small colored rectangles stacked vertically,
    # left-aligned percentage labels, title above.
    bins = list(classifier.bins)
    vmin = float(has_data["nondiscl_rate"].min())
    edges = [vmin] + bins

    import matplotlib.patches as mpatches

    handles = [
        mpatches.Patch(facecolor=color, edgecolor="#2b2b2b", linewidth=0.4)
        for color in SPRED_RAMP_5
    ]
    labels = [
        f"{lo*100:.0f}% – {hi*100:.0f}%"
        for lo, hi in zip(edges[:-1], edges[1:])
    ]
    # Highest bin on top.
    handles = handles[::-1]
    labels = labels[::-1]

    legend = ax.legend(
        handles,
        labels,
        loc="center left",
        bbox_to_anchor=(0.97, 0.5),
        title="Share of listings\nwithout certified EPC",
        frameon=False,
        fontsize=9,
        title_fontsize=9,
        handlelength=1.6,
        handleheight=1.1,
        handletextpad=0.5,
        labelspacing=0.55,
        borderaxespad=0.0,
    )
    # Left-align legend title and entries.
    legend.get_title().set_horizontalalignment("left")
    try:
        legend._legend_box.align = "left"
    except Exception:
        pass

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)


def run_for_property(cfg: PropertyConfig, gdf_raw: gpd.GeoDataFrame) -> None:
    parquet = ROOT / "data" / f"listings_enriched_{cfg.code}.parquet"
    outpath = ROOT / "paper" / "fig" / "stylized_facts" / cfg.folder / "fig_fact5_nondiscl_rate_map.pdf"

    rates = load_rates(parquet, cfg.min_listings)
    gdf = gdf_raw.to_crs("EPSG:2154")
    merged = gdf.merge(rates, left_on="code", right_on="dept", how="left")

    metro_mask = ~merged["code"].str.startswith("97")
    metro_rates = merged.loc[metro_mask, "nondiscl_rate"].dropna().values
    classifier = mapclassify.Quantiles(metro_rates, k=5)
    print(f"[class/{cfg.folder}] quantile bins (k=5): {classifier.bins}")

    plot_choropleth(merged, classifier, outpath)

    s = rates.set_index("dept")["nondiscl_rate"].sort_values()
    print(f"\n=== Fact 5 / {cfg.folder} ===")
    print(f"output: {outpath}")
    print(f"n départements: {len(rates)}")
    print(f"min    : {s.min():.4f} (dept {s.idxmin()})")
    print(f"median : {s.median():.4f}")
    print(f"max    : {s.max():.4f} (dept {s.idxmax()})")
    for label, sub in [("top-3 highest", s.tail(3)[::-1]), ("bottom-3 lowest", s.head(3))]:
        print(f"\n{label}:")
        for dept, val in sub.items():
            n = int(rates.set_index("dept").loc[dept, "n_listings"])
            print(f"  dept {dept}: {val:.4f}  (n={n})")


def main() -> int:
    gdf_raw = load_geometry(GEO_CACHE, GEO_URL)
    for cfg in CONFIGS:
        run_for_property(cfg, gdf_raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
