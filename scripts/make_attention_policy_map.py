"""Bubble maps of the retrofit subsidy under limited attention (paper Section 5).

One figure per renovation-cost scheme R-hat found in the attention scenario files
(`S_base_<R>` columns, currently 250 and 500 EUR/m2). Each figure has two panels
(apartments | houses) on département boundaries in Lambert-93 (EPSG:2154), with one
bubble per market:

* colour = share of the renovation cost the regulator must cover, S*_m / R-hat,
  classified into fixed bins shared by every figure, so colours are comparable
  across R-hat;
* size   = market threshold R-bar_m in EUR/m2 (bubble AREA proportional to R-bar_m,
  one scale shared by both panels and all figures);
* markets with S*_m = 0 (R-bar_m >= R-hat: no subsidy needed) are drawn as hollow
  grey circles, still sized by R-bar_m.

Inputs
------
results/attention/{apartment,house}_scenarios.csv   written by scripts/compute_attention.py
    market_id, price_eur_m2, rbar_base (log points), S_base_<R> (EUR/m2)
data/geo/market_centroids_{apartment,house}.csv     market centroids (lat, lon), the same
                                                    files scripts/make_subsidy_map.py reads
data/geo/departements.geojson                       département boundaries

Outputs
-------
paper/fig/visuals/fig_att_policy_map_R<R>.pdf  (+ .png at 300 dpi)

Design mirrors scripts/make_subsidy_map.py (Fira Sans, warm red ramp, Lambert-93,
aspect-exact layout); that script and its figures are left untouched.

Usage
-----
    python scripts/make_attention_policy_map.py                 # every R-hat in the files
    python scripts/make_attention_policy_map.py --cost 500      # one scheme only
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import urllib.request
from pathlib import Path

import cartopy.crs as ccrs
import geopandas as gpd
import mapclassify
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.feature import ShapelyFeature
from matplotlib.lines import Line2D

log = logging.getLogger("att_policy_map")

ROOT = Path(__file__).resolve().parents[1]
ATT_DIR = ROOT / "results" / "attention"
GEO_DIR = ROOT / "data" / "geo"
GEO_CACHE = GEO_DIR / "departements.geojson"
GEO_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
    "master/departements.geojson"
)
OUT_DIR = ROOT / "paper" / "fig" / "visuals"

SEGMENTS = ("apartment", "house")
SEGMENT_LABEL = {"apartment": "Apartments", "house": "Houses"}
# Guard on the estimation sample: the merge must keep every market of the attention
# extension. A change here means compute_attention.py's sample moved; update deliberately.
EXPECTED_MARKETS = {"apartment": 45, "house": 97}

# Fixed classes for S*/R-hat, in percent, shared by every figure so colours compare
# across R-hat. S* = 0 is its own (hollow) class; the first bin is (0, 20].
PCT_BINS = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]
ZERO_TOL = 1e-9            # EUR/m2; S* at or below this counts as "no subsidy needed"

# Warm sequential ramp (light = small share, dark = large share), as in
# make_subsidy_map.py; ColorBrewer Reds-derived, monotone in lightness, so it
# survives deuteranopia/protanopia and greyscale printing.
SUBSIDY_RAMP_5 = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#8b121f"]
ZERO_EDGE = "#7f7f7f"
INK = "#2b2b2b"

# Bubble area (points^2) given to the largest R-bar in the pooled sample. Area is
# proportional to R-bar; a small floor keeps near-zero thresholds visible.
SIZE_MAX = 260.0
SIZE_FLOOR = 6.0
# Markets whose centroids are closer than CLUSTER_DEG are drawn on a circle of radius
# JITTER_DEG (~15 km) around their mean so overlapping bubbles stay readable.
CLUSTER_DEG = 0.10
JITTER_DEG = 0.15

LAMBERT93 = ccrs.LambertConformal(
    central_longitude=3.0,
    central_latitude=46.5,
    standard_parallels=(49.0, 44.0),
    false_easting=700_000.0,
    false_northing=6_600_000.0,
    globe=ccrs.Globe(ellipse="GRS80"),
)
PLATE_CARREE = ccrs.PlateCarree()
MAP_EXTENT = (-5.5, 10.0, 41.1, 51.4)   # metropolitan France incl. Corsica, lon/lat

LAYOUT_LEFT, LAYOUT_RIGHT = 0.02, 0.98
LAYOUT_WSPACE = 0.03
LEGEND_BAND_IN = 1.05      # inches reserved below the maps for the two legends
TITLE_BAND_IN = 0.62       # inches reserved above the maps for the panel titles
FIG_WIDTH_IN = 10.5

try:
    _found = fm.findfont("Fira Sans", fallback_to_default=False)
    if "FiraSans" not in os.path.basename(_found):
        raise ValueError
except ValueError:
    print("[fonts] Fira Sans not found - falling back to DejaVu Sans "
          "(install: brew install --cask font-fira-sans).")

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Fira Sans", "DejaVu Sans"],
    "mathtext.fontset": "custom",
    "mathtext.rm": "Fira Sans",
    "mathtext.it": "Fira Sans:italic",
    "mathtext.bf": "Fira Sans:bold",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_departements() -> gpd.GeoDataFrame:
    """Metropolitan département polygons in EPSG:4326 (downloaded once, then cached)."""
    if not GEO_CACHE.exists():
        GEO_CACHE.parent.mkdir(parents=True, exist_ok=True)
        log.info("downloading %s -> %s", GEO_URL, GEO_CACHE)
        with urllib.request.urlopen(GEO_URL, timeout=60) as resp:
            GEO_CACHE.write_bytes(resp.read())
    gdf = gpd.read_file(GEO_CACHE)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    gdf = gdf.to_crs("EPSG:4326")
    gdf["code"] = gdf["code"].astype(str)
    gdf = gdf.loc[~gdf["code"].str.startswith("97")].copy()
    if not gdf.geometry.is_valid.all():
        gdf["geometry"] = gdf.geometry.make_valid()
    log.info("départements: %d polygons, CRS %s (plotted in Lambert-93)", len(gdf), gdf.crs)
    return gdf


def available_costs(df: pd.DataFrame) -> list[int]:
    """R-hat values present as `S_base_<R>` columns."""
    return sorted(int(m.group(1)) for c in df.columns
                  if (m := re.fullmatch(r"S_base_(\d+)", c)))


def _jitter_overlapping(lon: np.ndarray, lat: np.ndarray, seed: int = 0,
                        cluster_deg: float = CLUSTER_DEG,
                        radius_deg: float = JITTER_DEG) -> tuple[np.ndarray, np.ndarray, int]:
    """Spread near-coincident markets on a small circle around their cluster mean.

    Markets whose centroids lie within `cluster_deg` of each other (single linkage) are
    treated as co-located: at map scale their bubbles would sit on top of each other.
    Placement is deterministic in `seed`. Returns jittered lon, lat and the number of
    markets moved.
    """
    n = len(lon)
    parent = np.arange(n)

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    dist = np.hypot(lon[:, None] - lon[None, :], lat[:, None] - lat[None, :])
    for i, j in zip(*np.where(np.triu(dist < cluster_deg, k=1))):
        parent[find(i)] = find(j)
    roots = np.array([find(i) for i in range(n)])

    rng = np.random.default_rng(seed)
    out_lon, out_lat = lon.astype(float).copy(), lat.astype(float).copy()
    moved = 0
    for r in np.unique(roots):
        idxs = np.flatnonzero(roots == r)
        if len(idxs) <= 1:
            continue
        clon, clat = lon[idxs].mean(), lat[idxs].mean()
        angles = rng.permutation(len(idxs)) * (2 * np.pi / len(idxs))
        # cos(lat) keeps the offset roughly circular on the ground.
        out_lon[idxs] = clon + radius_deg * np.cos(angles) / np.cos(np.radians(clat))
        out_lat[idxs] = clat + radius_deg * np.sin(angles)
        moved += len(idxs)
    return out_lon, out_lat, moved


def load_segment(segment: str) -> pd.DataFrame:
    """Attention scenarios merged with centroids; adds R-bar in EUR/m2 and jittered coords."""
    scen = pd.read_csv(ATT_DIR / f"{segment}_scenarios.csv", dtype={"market_id": str})
    cent = pd.read_csv(GEO_DIR / f"market_centroids_{segment}.csv", dtype={"market_id": str},
                       usecols=["market_id", "lat", "lon"])
    for name, frame in (("scenarios", scen), ("centroids", cent)):
        dup = frame["market_id"].duplicated()
        if dup.any():
            raise ValueError(f"{segment} {name}: duplicated market_id {frame.loc[dup, 'market_id'].tolist()}")

    missing = sorted(set(scen["market_id"]) - set(cent["market_id"]))
    if missing:
        log.warning("%s: %d market(s) without a centroid, dropped from the map: %s",
                    segment, len(missing), missing)
    merged = scen.merge(cent, on="market_id", how="inner", validate="one_to_one")
    if merged[["lat", "lon"]].isna().any().any():
        raise ValueError(f"{segment}: NaN centroid coordinates after merge")

    expected = EXPECTED_MARKETS[segment]
    assert len(scen) == expected, f"{segment}: {len(scen)} scenario rows, expected {expected}"
    assert len(merged) == expected, f"{segment}: merge kept {len(merged)} of {expected} markets"

    merged["rbar_eur_m2"] = merged["rbar_base"] / 100.0 * merged["price_eur_m2"]
    merged["lon_j"], merged["lat_j"], moved = _jitter_overlapping(
        merged["lon"].to_numpy(dtype=float), merged["lat"].to_numpy(dtype=float))
    log.info("%s: %d markets merged with centroids; %d near-coincident markets offset by "
             "%.2f deg for legibility", segment, len(merged), moved, JITTER_DEG)
    return merged


# ---------------------------------------------------------------------------
# Encodings
# ---------------------------------------------------------------------------

def bubble_area(rbar: np.ndarray, rbar_max: float) -> np.ndarray:
    """Marker area (pt^2) proportional to R-bar, floored so tiny thresholds stay visible."""
    return np.maximum(SIZE_MAX * np.clip(rbar, 0.0, None) / rbar_max, SIZE_FLOOR)


def _nice(x: float) -> float:
    """Round down to 1, 2, 2.5 or 5 times a power of ten."""
    mag = 10.0 ** np.floor(np.log10(x))
    return max(m for m in (1.0, 2.0, 2.5, 5.0, 10.0) if m * mag <= x) * mag


def reference_rbar(rbar_max: float) -> list[float]:
    """Three legend values for bubble size, derived from the pooled maximum."""
    top = _nice(rbar_max)
    return [float(_nice(top / 6.0)), float(_nice(top / 2.0)), float(top)]


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def _panel_aspect() -> float:
    """Height/width of MAP_EXTENT projected to Lambert-93 (mid-edges included)."""
    lon0, lon1, lat0, lat1 = MAP_EXTENT
    glon, glat = np.meshgrid(np.linspace(lon0, lon1, 25), np.linspace(lat0, lat1, 25))
    xyz = LAMBERT93.transform_points(PLATE_CARREE, glon.ravel(), glat.ravel())
    return float(np.ptp(xyz[:, 1]) / np.ptp(xyz[:, 0]))


def _figure_geometry() -> tuple[tuple[float, float], float, float]:
    """Figure size and (bottom, top) fractions that make each panel slot aspect-exact."""
    panel_w_in = FIG_WIDTH_IN * (LAYOUT_RIGHT - LAYOUT_LEFT - LAYOUT_WSPACE) / 2
    axes_h_in = panel_w_in * _panel_aspect()
    fig_h = axes_h_in + LEGEND_BAND_IN + TITLE_BAND_IN
    return (FIG_WIDTH_IN, fig_h), LEGEND_BAND_IN / fig_h, 1.0 - TITLE_BAND_IN / fig_h


def _add_scale_bar(ax: plt.Axes, length_km: float = 100.0,
                   location: tuple[float, float] = (0.06, 0.05)) -> None:
    """Scale bar in Lambert-93 metres (true to scale near the standard parallels)."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    sx, sy = x0 + location[0] * (x1 - x0), y0 + location[1] * (y1 - y0)
    bar = length_km * 1000.0
    ax.plot([sx, sx + bar], [sy, sy], color=INK, lw=2.0, solid_capstyle="butt",
            transform=ax.projection, zorder=10)
    cap = 0.012 * (y1 - y0)
    for xx in (sx, sx + bar):
        ax.plot([xx, xx], [sy - cap, sy + cap], color=INK, lw=1.0,
                transform=ax.projection, zorder=10)
    ax.text(sx + bar / 2, sy + 0.025 * (y1 - y0), f"{length_km:.0f} km", ha="center",
            va="bottom", fontsize=8, color=INK, transform=ax.projection, zorder=10)


def plot_panel(ax: plt.Axes, df: pd.DataFrame, depts: gpd.GeoDataFrame, cost: int,
               cmap: mpl.colors.ListedColormap, rbar_max: float) -> int:
    """Draw one panel; returns the number of markets with S* = 0."""
    ax.set_extent(list(MAP_EXTENT), crs=PLATE_CARREE)
    ax.add_feature(ShapelyFeature(depts.geometry, PLATE_CARREE, facecolor="#f3f3f3",
                                  edgecolor="white", linewidth=0.3))

    s_star = df[f"S_base_{cost}"].to_numpy(dtype=float)
    if (s_star > cost * (1 + 1e-9)).any():
        raise ValueError(f"S_base_{cost} exceeds R-hat for some market; share would exceed 1")
    is_zero = s_star <= ZERO_TOL
    # Draw large bubbles first so small ones stay on top.
    order = np.argsort(-df["rbar_eur_m2"].to_numpy())
    d = df.iloc[order]
    s_star, is_zero = s_star[order], is_zero[order]
    area = bubble_area(d["rbar_eur_m2"].to_numpy(), rbar_max)

    if is_zero.any():
        ax.scatter(d["lon_j"].to_numpy()[is_zero], d["lat_j"].to_numpy()[is_zero],
                   s=area[is_zero], facecolor="white", edgecolor=ZERO_EDGE, linewidth=0.9,
                   linestyle=(0, (2.0, 1.2)),
                   transform=PLATE_CARREE, zorder=3)
    pos = ~is_zero
    if pos.any():
        pct = 100.0 * s_star[pos] / cost
        cls = mapclassify.UserDefined(pct, bins=PCT_BINS[1:]).yb
        ax.scatter(d["lon_j"].to_numpy()[pos], d["lat_j"].to_numpy()[pos], s=area[pos],
                   c=[cmap(int(i)) for i in cls], edgecolor=INK, linewidth=0.4, alpha=0.95,
                   transform=PLATE_CARREE, zorder=4)

    _add_scale_bar(ax)
    paris = depts.loc[depts["code"] == "75"]
    if not paris.empty:
        c = paris.geometry.iloc[0].centroid
        tr = PLATE_CARREE._as_mpl_transform(ax)
        ax.annotate("Paris", xy=(c.x, c.y), xycoords=tr, xytext=(c.x + 1.0, c.y + 0.8),
                    textcoords=tr, fontsize=8, color=INK, zorder=6,
                    arrowprops=dict(arrowstyle="-", color=INK, lw=0.4, shrinkA=0, shrinkB=0))
    ax.annotate("N", xy=(0.94, 0.94), xytext=(0.94, 0.86), xycoords="axes fraction",
                textcoords="axes fraction", ha="center", va="center", fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.6), zorder=6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return int(is_zero.sum())


def build_legends(fig: plt.Figure, cmap: mpl.colors.ListedColormap, rbar_max: float) -> None:
    """Colour-class legend (bottom left) and bubble-size legend (bottom right)."""
    labels = [f"{lo:.0f}–{hi:.0f}%" if lo > 0 else f"Up to {hi:.0f}%"
              for lo, hi in zip(PCT_BINS[:-1], PCT_BINS[1:])]
    handles = [Line2D([], [], ls="", marker="o", markersize=9, markerfacecolor=cmap(i),
                      markeredgecolor=INK, markeredgewidth=0.4)
               for i in range(len(PCT_BINS) - 1)]
    handles, labels = handles[::-1], labels[::-1]           # dark (high share) first
    handles.append(plt.scatter([], [], s=81, facecolor="white", edgecolor=ZERO_EDGE,
                               linewidth=0.9, linestyle=(0, (2.0, 1.2))))
    labels.append("None needed (dashed outline)")
    leg_c = fig.legend(handles, labels,
                       title=r"Share of renovation cost the subsidy covers, $S^*/\hat{R}$",
                       loc="lower left", bbox_to_anchor=(0.03, 0.01), ncol=2,
                       frameon=False, fontsize=8.5, title_fontsize=9.5, alignment="left",
                       handletextpad=0.4, columnspacing=1.4, labelspacing=0.55)
    fig.add_artist(leg_c)

    refs = reference_rbar(rbar_max)
    size_handles = [plt.scatter([], [], s=bubble_area(np.array([v]), rbar_max)[0],
                                c="#9a9a9a", edgecolor=INK, linewidth=0.4) for v in refs]
    leg_s = fig.legend(size_handles, [f"{v:.0f} €/m²" for v in refs],
                       title=r"Market threshold $\bar{R}$ (bubble area)",
                       loc="lower right", bbox_to_anchor=(0.97, 0.035), ncol=3,
                       frameon=False, fontsize=8.5, title_fontsize=9.5, alignment="left",
                       scatterpoints=1, handletextpad=0.5, columnspacing=1.4,
                       borderpad=0.6, labelspacing=1.0)
    fig.add_artist(leg_s)


def render(cost: int, panels: dict[str, pd.DataFrame], depts: gpd.GeoDataFrame,
           rbar_max: float, out_pdf: Path) -> dict[str, int]:
    """Render the two-panel map for one R-hat; returns S* = 0 counts per segment."""
    cmap = mpl.colors.ListedColormap(SUBSIDY_RAMP_5[: len(PCT_BINS) - 1], name="subsidy")
    figsize, bottom, top = _figure_geometry()
    fig, axes = plt.subplots(1, 2, figsize=figsize, subplot_kw={"projection": LAMBERT93})
    fig.subplots_adjust(left=LAYOUT_LEFT, right=LAYOUT_RIGHT, bottom=bottom, top=top,
                        wspace=LAYOUT_WSPACE)
    zeros: dict[str, int] = {}
    for ax, seg in zip(axes, SEGMENTS):
        df = panels[seg]
        zeros[seg] = plot_panel(ax, df, depts, cost, cmap, rbar_max)
        ax.set_title(f"{SEGMENT_LABEL[seg]} ({len(df)} markets)", loc="left",
                     fontsize=11, fontweight="bold", pad=22)
        ax.annotate(f"Renovation cost $\\hat{{R}}$ = {cost} €/m²", xy=(0, 1),
                    xycoords="axes fraction", xytext=(0, 6), textcoords="offset points",
                    ha="left", va="bottom", fontsize=9.5, color=INK)
    build_legends(fig, cmap, rbar_max)

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    fig.savefig(out_pdf.with_suffix(".png"), dpi=300)
    plt.close(fig)
    log.info("wrote %s (+ .png)", out_pdf)
    return zeros


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cost", type=int, nargs="+", default=None,
                    help="R-hat value(s) in EUR/m2; default: every S_base_<R> column present")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)      # own logger only: keeps fontTools subsetting chatter quiet

    depts = load_departements()
    panels = {seg: load_segment(seg) for seg in SEGMENTS}
    costs = sorted(set.intersection(*(set(available_costs(p)) for p in panels.values())))
    if args.cost is not None:
        unknown = set(args.cost) - set(costs)
        if unknown:
            raise SystemExit(f"no S_base column for R-hat {sorted(unknown)}; available {costs}")
        costs = sorted(args.cost)

    # R-bar does not depend on R-hat: one size scale for both panels and every figure.
    rbar_max = float(max(p["rbar_eur_m2"].max() for p in panels.values()))
    log.info("bubble area proportional to R-bar; pooled max %.1f EUR/m2 -> %.0f pt^2; "
             "legend refs %s", rbar_max, SIZE_MAX, reference_rbar(rbar_max))
    log.info("colour classes (S*/R-hat, %%): %s, plus S* = 0", PCT_BINS)

    for cost in costs:
        zeros = render(cost, panels, depts, rbar_max,
                       args.out_dir / f"fig_att_policy_map_R{cost}.pdf")
        for seg, n0 in zeros.items():
            log.info("R-hat=%d %s: %d of %d markets with S* = 0", cost, seg, n0,
                     len(panels[seg]))


if __name__ == "__main__":
    main()
