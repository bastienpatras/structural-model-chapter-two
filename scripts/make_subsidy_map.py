"""Paper-quality bubble map of the minimum incentive-compatible subsidy S*_m.

Loads `results/{apartment,house}/subsidy_grid.csv` plus
`data/geo/market_centroids_{apartment,house}.csv`, picks the canonical
renovation-cost scheme (default 500 €/m²), and renders a two-panel figure
(apartments | houses) with département boundaries as background and one bubble
per market coloured by S* (in €/m²). Projection handled by **Cartopy** in
Lambert-93 (EPSG:2154); styling mirrors `make_fact5_map.py` (Fira Sans, SPred
ramp, quantile classification).

Output: `paper/fig/visuals/fig_subsidy_map.pdf`.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import geopandas as gpd
import mapclassify

import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature

ROOT = Path(__file__).resolve().parents[1]
GEO_CACHE = ROOT / "data" / "geo" / "departements.geojson"
GEO_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
    "master/departements.geojson"
)

# Sequential ramp for S* (minimum subsidy): higher contrast than the very-pale
# SPred ramp, while staying in a warm red family that reads as "more subsidy
# needed = redder". Five steps; colorblind-safe (verified with simulators).
SUBSIDY_RAMP_5 = [
    "#fee5d9",
    "#fcae91",
    "#fb6a4a",
    "#de2d26",
    "#8b121f",
]

# Lambert-93 — France's official projected CRS (RGF93 / Lambert-93, EPSG:2154).
# Parameters from EPSG: lat_0=46.5, lon_0=3, lat_1=49, lat_2=44,
# x_0=700000, y_0=6600000 on the GRS80 ellipsoid.
LAMBERT93 = ccrs.LambertConformal(
    central_longitude=3.0,
    central_latitude=46.5,
    standard_parallels=(49.0, 44.0),
    false_easting=700_000.0,
    false_northing=6_600_000.0,
    globe=ccrs.Globe(ellipse="GRS80"),
)
PLATE_CARREE = ccrs.PlateCarree()

# Map extent for metropolitan France (incl. Corsica), in lon/lat degrees.
# Module-level so the figure layout in `_render_one_map` can be sized to the
# projected aspect ratio of exactly this window — see `_panel_aspect`.
MAP_EXTENT = (-5.5, 10.0, 41.1, 51.4)

# Figure-layout fractions. The axes band is bounded by these; its height is
# then derived so that each panel's slot matches the map's own aspect, which
# is what keeps Cartopy from shrinking the panel and leaving a dead band of
# whitespace above and below it (equal-aspect GeoAxes are centred in their
# slot, so any slack shows up as blank figure).
LAYOUT_LEFT, LAYOUT_RIGHT = 0.02, 0.98
LAYOUT_TOP = 0.90          # room above the axes for the two-line panel titles
LAYOUT_WSPACE = 0.03
LEGEND_BAND_IN = 1.10      # inches reserved at the bottom for the two legends
TITLE_BAND_IN = 0.60       # inches the LAYOUT_TOP margin must cover

try:
    found = fm.findfont("Fira Sans", fallback_to_default=False)
    if "FiraSans" not in os.path.basename(found):
        print("[fonts] Fira Sans not found - falling back to DejaVu Sans.")
except Exception:
    print("[fonts] Fira Sans not found - falling back to DejaVu Sans.")

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


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_geometry() -> gpd.GeoDataFrame:
    GEO_CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not GEO_CACHE.exists():
        print(f"[geo] downloading {GEO_URL} -> {GEO_CACHE}")
        with urllib.request.urlopen(GEO_URL, timeout=60) as resp:
            GEO_CACHE.write_bytes(resp.read())
    gdf = gpd.read_file(GEO_CACHE)
    gdf["code"] = gdf["code"].astype(str)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf


def _jitter_overlapping(
    lon: np.ndarray, lat: np.ndarray, seed: int = 0, radius_deg: float = 0.18
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic radial jitter for markets that share a centroid.

    Operates in degrees (the input CRS is EPSG:4326). Markets with a unique
    coordinate are left untouched; co-located markets are spread on a small
    circle around their shared point so the bubbles remain visually
    distinguishable.
    """
    rng = np.random.default_rng(seed)
    out_lon = lon.astype(float).copy()
    out_lat = lat.astype(float).copy()
    keys = list(zip(lon.tolist(), lat.tolist()))
    seen: dict[tuple[float, float], list[int]] = {}
    for i, k in enumerate(keys):
        seen.setdefault(k, []).append(i)
    for (clon, clat), idxs in seen.items():
        if len(idxs) <= 1:
            continue
        # Place co-located markets on a small circle, deterministic in seed.
        angles = rng.permutation(len(idxs)) * (2 * np.pi / len(idxs))
        for j, i in enumerate(idxs):
            out_lon[i] = clon + radius_deg * np.cos(angles[j])
            out_lat[i] = clat + radius_deg * np.sin(angles[j]) * 0.7
    return out_lon, out_lat


def load_panel(
    grid_path     : Path,
    centroids_path: Path,
    cost_per_m2   : float,
) -> pd.DataFrame | None:
    if not grid_path.exists():
        print(f"[panel] missing {grid_path}; skipping")
        return None
    if not centroids_path.exists():
        print(f"[panel] missing {centroids_path}; skipping")
        return None

    grid = pd.read_csv(grid_path)
    cent = pd.read_csv(centroids_path)

    available = grid["cost_per_m2"].unique()
    rh = float(min(available, key=lambda x: abs(x - cost_per_m2)))
    canonical = grid[grid["cost_per_m2"] == rh].copy()

    merged = canonical.merge(cent, on="market_id", how="inner",
                             suffixes=("", "_cent"))
    if merged.empty:
        return None

    # n_listings can come from either side of the merge; prefer the grid value
    # which reflects the market sample size used to compute S*.
    if "n_listings" not in merged.columns and "n_listings_cent" in merged.columns:
        merged = merged.rename(columns={"n_listings_cent": "n_listings"})

    lon, lat = _jitter_overlapping(
        merged["lon"].to_numpy(), merged["lat"].to_numpy()
    )
    merged["lon_j"] = lon
    merged["lat_j"] = lat
    return merged


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def _size_from_premium(
    premium    : np.ndarray,
    premium_lo : float,
    premium_hi : float,
    size_lo    : float = 22.0,
    size_hi    : float = 200.0,
) -> np.ndarray:
    """Linear bubble area scaling on verified-quality premium (€/m²)."""
    p = np.clip(premium.astype(float), premium_lo, premium_hi)
    denom = max(premium_hi - premium_lo, 1e-9)
    return size_lo + (size_hi - size_lo) * (p - premium_lo) / denom


def _add_scale_bar(
    ax       : plt.Axes,
    length_km: float = 100.0,
    location : tuple[float, float] = (0.08, 0.05),
) -> None:
    """
    Horizontal scale bar (in km) drawn in the axes' projection coordinates.
    Lambert-93 axis units are metres, so a 100 km bar is 100 000 units.
    """
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    span_x, span_y = x1 - x0, y1 - y0
    sx = x0 + location[0] * span_x
    sy = y0 + location[1] * span_y
    bar_m = length_km * 1000.0
    ax.plot(
        [sx, sx + bar_m], [sy, sy],
        color="#2b2b2b", linewidth=2.0, solid_capstyle="butt",
        transform=ax.projection, zorder=10,
    )
    # Small end-cap ticks
    cap = 0.012 * span_y
    for xx in (sx, sx + bar_m):
        ax.plot([xx, xx], [sy - cap, sy + cap],
                color="#2b2b2b", linewidth=1.0,
                transform=ax.projection, zorder=10)
    ax.text(
        sx + bar_m / 2.0, sy + 0.025 * span_y, f"{int(length_km)} km",
        ha="center", va="bottom", fontsize=8, color="#2b2b2b",
        transform=ax.projection, zorder=10,
    )


def plot_panel(
    ax          : plt.Axes,
    df          : pd.DataFrame,
    metro_gdf   : gpd.GeoDataFrame,
    cmap        : mpl.colors.ListedColormap,
    pct_bins    : list[float],
    title       : str,
    cost_per_m2 : float,
    premium_lo  : float,
    premium_hi  : float,
) -> None:
    """Render one panel onto a Cartopy GeoAxes (in Lambert-93).

    Bubble *color* encodes the minimum subsidy as a share of $\\hat R$
    (i.e., $S^*_m / \\hat R$ in %); bubble *size* encodes the market-specific
    verified-quality premium $\\bar R_m$ (€/m²). `pct_bins` is the shared
    bin sequence in % (e.g., [0, 20, 40, 60, 80, 100]).
    """

    ax.set_extent(list(MAP_EXTENT), crs=PLATE_CARREE)

    metro_4326 = metro_gdf.to_crs("EPSG:4326")
    feat = ShapelyFeature(
        metro_4326.geometry, PLATE_CARREE,
        facecolor="#f3f3f3", edgecolor="white", linewidth=0.3,
    )
    ax.add_feature(feat)

    zero = df[df["S_star_eur_per_m2"] <= 0]
    pos  = df[df["S_star_eur_per_m2"] > 0]

    if not zero.empty:
        s_zero = _size_from_premium(
            zero["R_bar_eur_per_m2"].to_numpy(), premium_lo, premium_hi
        ) * 0.55
        ax.scatter(
            zero["lon_j"].to_numpy(), zero["lat_j"].to_numpy(),
            s=s_zero, c="#bdbdbd", alpha=0.55, linewidth=0.3,
            edgecolor="white", transform=PLATE_CARREE, zorder=3,
        )

    if not pos.empty:
        pct = 100.0 * pos["S_star_eur_per_m2"].to_numpy() / float(cost_per_m2)
        # Bin pct values into pct_bins. Use UserDefined classifier on bin
        # upper edges (exclude the 0 lower bound).
        classifier = mapclassify.UserDefined(pct, bins=pct_bins[1:])
        idx = classifier.yb
        colors = [cmap(int(min(i, cmap.N - 1))) for i in idx]
        sizes = _size_from_premium(
            pos["R_bar_eur_per_m2"].to_numpy(), premium_lo, premium_hi
        )
        ax.scatter(
            pos["lon_j"].to_numpy(), pos["lat_j"].to_numpy(),
            s=sizes, c=colors, alpha=0.92,
            linewidth=0.4, edgecolor="#2b2b2b",
            transform=PLATE_CARREE, zorder=4,
        )

    _add_scale_bar(ax, length_km=100.0)

    # Paris label with thin arrow leader (in data coordinates of EPSG:4326,
    # transformed by Cartopy through `xycoords`/`textcoords`).
    paris = metro_4326.loc[metro_4326["code"] == "75"]
    if not paris.empty:
        c = paris.geometry.iloc[0].centroid
        # Convert label anchor to lat/lon and offset by ~1° east / 0.8° north.
        ax.annotate(
            "Paris",
            xy=(c.x, c.y), xycoords=PLATE_CARREE._as_mpl_transform(ax),
            xytext=(c.x + 1.0, c.y + 0.8),
            textcoords=PLATE_CARREE._as_mpl_transform(ax),
            fontsize=8, color="#2b2b2b",
            arrowprops=dict(arrowstyle="-", color="#2b2b2b", lw=0.4,
                            shrinkA=0, shrinkB=0),
            zorder=5,
        )

    # North arrow (top-right of the panel, in axes-fraction coordinates).
    ax.annotate(
        "N", xy=(0.94, 0.94), xytext=(0.94, 0.86),
        xycoords="axes fraction", textcoords="axes fraction",
        ha="center", va="center", fontsize=8, color="#2b2b2b",
        arrowprops=dict(arrowstyle="->", color="#2b2b2b", lw=0.6),
        zorder=6,
    )

    # Neat-line: subtle frame around the panel.
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.outline_patch.set_visible(False) if hasattr(ax, "outline_patch") else None
    # Title is set by the caller in `_render_one_map`.


def build_legend(
    fig         : plt.Figure,
    pct_bins    : list[float],
    cmap        : mpl.colors.ListedColormap,
    premium_lo  : float,
    premium_hi  : float,
) -> None:
    """
    Bottom-of-figure legend with TWO components:
      (1) Discrete color bins for the minimum subsidy expressed as % of R̂
      (2) Three reference bubbles sized by the verified-quality premium R̄_m
    """
    # ── Color legend: bins as % of R̂ ─────────────────────────────────────
    # Ordered high→low so the ramp reads monotonically down each column
    # (fig.legend fills column-major), with the grey "no subsidy" class last
    # rather than heading a descending sequence it is not part of.
    color_handles = [
        mpatches.Patch(facecolor=cmap(i), edgecolor="#2b2b2b", linewidth=0.4)
        for i in range(len(pct_bins) - 1)
    ][::-1]
    color_labels = [
        f"{lo:.0f}% – {hi:.0f}%"
        for lo, hi in zip(pct_bins[:-1], pct_bins[1:])
    ][::-1]
    color_handles.append(
        mpatches.Patch(facecolor="#bdbdbd", edgecolor="#2b2b2b", linewidth=0.4)
    )
    color_labels.append(r"$S^*=0$  (no subsidy needed)")

    color_legend = fig.legend(
        color_handles, color_labels,
        title=r"Minimum subsidy $S^*_m$ as share of $\hat R$",
        loc="lower left", bbox_to_anchor=(0.03, 0.015),
        ncol=2, frameon=False, fontsize=8.5, title_fontsize=9.5,
        alignment="left",
    )
    fig.add_artist(color_legend)

    # ── Size legend: verified-quality premium R̄_m (€/m²) ─────────────────
    ref_values = np.array([premium_lo,
                           0.5 * (premium_lo + premium_hi),
                           premium_hi])
    ref_sizes = _size_from_premium(ref_values, premium_lo, premium_hi)
    size_handles = [
        plt.scatter([], [],
                    s=s, c="#444444", alpha=0.85,
                    edgecolor="#2b2b2b", linewidth=0.4)
        for s in ref_sizes
    ]
    size_labels = [f"{v:.0f} €/m²" for v in ref_values]

    size_legend = fig.legend(
        size_handles, size_labels,
        title=r"Verified-quality premium $\bar R_m$ (€/m²)",
        loc="lower right", bbox_to_anchor=(0.97, 0.015),
        ncol=3, frameon=False, fontsize=8.5, title_fontsize=9.5,
        alignment="left", borderpad=0.6, labelspacing=1.0,
        scatterpoints=1, handletextpad=0.6, columnspacing=1.2,
    )
    fig.add_artist(size_legend)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def _panel_aspect() -> float:
    """Height/width of `MAP_EXTENT` once projected into Lambert-93.

    Cartopy holds GeoAxes at equal aspect, so a slot whose aspect differs from
    this ratio gets the panel shrunk and centred inside it, and the leftover
    slack is rendered as blank figure. Deriving the layout from this number
    keeps the panels flush regardless of how `MAP_EXTENT` is later changed.
    """
    lon0, lon1, lat0, lat1 = MAP_EXTENT
    # Sample the window's edges (not just the corners): Lambert-93 is conic,
    # so the projected bounding box of the extent is set by the mid-edge
    # points, not the corner points alone.
    lons = np.linspace(lon0, lon1, 25)
    lats = np.linspace(lat0, lat1, 25)
    grid_lon, grid_lat = np.meshgrid(lons, lats)
    xyz = LAMBERT93.transform_points(
        PLATE_CARREE, grid_lon.ravel(), grid_lat.ravel()
    )
    x, y = xyz[:, 0], xyz[:, 1]
    return float((y.max() - y.min()) / (x.max() - x.min()))


def _figure_geometry(fig_width: float = 10.5) -> tuple[tuple[float, float], float]:
    """Figure size and `bottom` margin that make the axes slot aspect-exact."""
    n_panels = 2
    band_w = LAYOUT_RIGHT - LAYOUT_LEFT
    # Width available to one panel, in inches, after the inter-panel gutter.
    panel_w_in = fig_width * (band_w - LAYOUT_WSPACE * (n_panels - 1)) / n_panels
    axes_h_in = panel_w_in * _panel_aspect()
    # (LAYOUT_TOP - bottom) * H = axes_h_in and bottom * H = LEGEND_BAND_IN
    fig_height = (axes_h_in + LEGEND_BAND_IN) / LAYOUT_TOP
    # Guard: LAYOUT_TOP must actually leave room for the titles.
    if (1.0 - LAYOUT_TOP) * fig_height < TITLE_BAND_IN:
        fig_height = axes_h_in + LEGEND_BAND_IN + TITLE_BAND_IN
    bottom = LEGEND_BAND_IN / fig_height
    return (fig_width, fig_height), bottom


def _render_one_map(
    cost_per_m2 : float,
    out_path    : Path,
    metro       : gpd.GeoDataFrame,
    pct_bins    : list[float],
    premium_lo  : float,
    premium_hi  : float,
) -> None:
    apt = load_panel(
        ROOT / "results" / "apartment" / "subsidy_grid.csv",
        ROOT / "data" / "geo" / "market_centroids_apartment.csv",
        cost_per_m2,
    )
    hse = load_panel(
        ROOT / "results" / "house" / "subsidy_grid.csv",
        ROOT / "data" / "geo" / "market_centroids_house.csv",
        cost_per_m2,
    )

    cmap = mpl.colors.ListedColormap(
        SUBSIDY_RAMP_5[: len(pct_bins) - 1], name="subsidy",
    )

    figsize, bottom = _figure_geometry()
    fig, axes = plt.subplots(
        1, 2, figsize=figsize,
        subplot_kw={"projection": LAMBERT93},
    )
    fig.subplots_adjust(
        left=LAYOUT_LEFT, right=LAYOUT_RIGHT, top=LAYOUT_TOP,
        bottom=bottom, wspace=LAYOUT_WSPACE,
    )

    if apt is not None:
        plot_panel(axes[0], apt, metro, cmap, pct_bins,
                   "Apartments", cost_per_m2, premium_lo, premium_hi)
        axes[0].set_title(
            f"Apartments\n$\\hat R = {int(cost_per_m2)}$ €/m²",
            loc="left", fontsize=11, fontweight="bold", pad=8,
        )
    else:
        axes[0].set_axis_off()
        axes[0].set_title("Apartments — no data", loc="left",
                          fontsize=11, pad=8)
    if hse is not None:
        plot_panel(axes[1], hse, metro, cmap, pct_bins,
                   "Houses", cost_per_m2, premium_lo, premium_hi)
        axes[1].set_title(
            f"Houses\n$\\hat R = {int(cost_per_m2)}$ €/m²",
            loc="left", fontsize=11, fontweight="bold", pad=8,
        )
    else:
        axes[1].set_axis_off()
        axes[1].set_title("Houses — no data", loc="left", fontsize=11, pad=8)

    build_legend(fig, pct_bins, cmap, premium_lo, premium_hi)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[map] wrote {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cost-per-m2", type=float, nargs="+",
                    default=[250.0, 500.0, 1000.0],
                    help="one or more R̂ values in €/m² (default: 250 500 1000)")
    ap.add_argument(
        "--out", type=Path, default=None,
        help="output path; if omitted, auto-named per R̂ value as "
             "`paper/fig/visuals/fig_subsidy_map_R<cost>.pdf`",
    )
    args = ap.parse_args()

    metro = load_geometry()
    metro = metro.loc[~metro["code"].str.startswith("97")].copy()

    # Fixed bins in % of R̂. Shared across all rendered maps so colors are
    # directly comparable across cost schemes.
    pct_bins = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]

    # Global premium scale (over both property types and ALL requested R̂):
    # the verified-quality premium R̄_m is independent of R̂, so the same
    # bubble-size legend applies to every map in this run.
    apt_grid_path = ROOT / "results" / "apartment" / "subsidy_grid.csv"
    hse_grid_path = ROOT / "results" / "house" / "subsidy_grid.csv"
    if not apt_grid_path.exists() and not hse_grid_path.exists():
        sys.exit("error: no subsidy_grid.csv could be located; "
                 "run `python run.py config_apartment.json` first.")

    pool = []
    for p in (apt_grid_path, hse_grid_path):
        if p.exists():
            pool.append(pd.read_csv(p, usecols=["R_bar_eur_per_m2"]))
    premium_pool = pd.concat(pool)["R_bar_eur_per_m2"]
    premium_lo = float(premium_pool.min())
    premium_hi = float(premium_pool.max())

    for cost in args.cost_per_m2:
        if args.out is not None and len(args.cost_per_m2) == 1:
            out_path = args.out
        else:
            out_path = (ROOT / "paper" / "fig" / "visuals"
                        / f"fig_subsidy_map_R{int(cost)}.pdf")
        _render_one_map(cost, out_path, metro, pct_bins,
                        premium_lo, premium_hi)


if __name__ == "__main__":
    main()
