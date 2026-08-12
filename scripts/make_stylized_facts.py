"""Produce four publication-grade Stylized Facts figures (Facts 1-4).

Parameterized over property type (APARTMENT, HOUSE). Outputs are written to
`paper/fig/stylized_facts/{apartment,house}/`.

Figures (LaTeX `\\textwidth`, Fira Sans, Metropolis palette):
  Fact 1: Non-disclosure price premium event study around the July 2021 reform.
  Fact 2: Time series of the share of listings without a certified EPC.
  Fact 3: 3-group decomposition (truthful / strategic hiding / uninformed),
          using the estimation-sample shares from results/*/results.txt.
  Fact 4: Verified ADEME energy-class composition among informed sellers,
          truthful disclosure vs. strategic hiding.

Run from project root:
    python scripts/make_stylized_facts.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

ROOT = Path("/Users/bpatras/structural-model-chapter-two")
REFORM = pd.Timestamp("2021-07-01")

SPRED = "#d01c32"
BBLUE = "#9BC1BC"

try:
    from matplotlib import font_manager

    _fira = font_manager.findfont("Fira Sans", fallback_to_default=False)
    print(f"[fonts] Fira Sans found at: {_fira}")
except Exception:
    print(
        "[fonts] WARNING: Fira Sans not found - falling back to DejaVu Sans. "
        "Install via: brew install --cask font-fira-sans"
    )

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Fira Sans", "DejaVu Sans"],
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
        "axes.prop_cycle": mpl.cycler(
            color=[SPRED, BBLUE, "#2b2b2b", "#1f78b4", "#33a02c", "#ff7f00"]
        ),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

FIGSIZE_TEXTWIDTH = (6.5, 3.6)


@dataclass
class PropertyConfig:
    code: str  # 'APARTMENT' or 'HOUSE'
    label: str  # 'apartments' or 'houses'
    folder: str  # 'apartment' or 'house'
    # Estimation-sample shares from results/{folder}/results.txt
    share_truthful: float
    share_uninformed: float
    share_hiding: float
    n_sample: int


CONFIGS = [
    PropertyConfig(
        code="APARTMENT",
        label="apartments",
        folder="apartment",
        share_truthful=0.798,
        share_uninformed=0.167,
        share_hiding=0.035,
        n_sample=834_816,
    ),
    PropertyConfig(
        code="HOUSE",
        label="houses",
        folder="house",
        share_truthful=0.904,
        share_uninformed=0.085,
        share_hiding=0.011,
        n_sample=677_011,
    ),
]


def make_fact1(cfg: PropertyConfig, outdir: Path) -> tuple[Path, float, float]:
    """Volume-weighted log price gap between non-disclosed and energy-intensive."""
    df = pd.read_csv(ROOT / "data" / f"index_{cfg.code}.csv", parse_dates=["date"])
    df = df[df["item_type"] == cfg.code].copy()

    df["pv"] = df["final_index"] * df["volume"]
    grp = df.groupby(["date", "EPC"], as_index=False).agg(
        pv=("pv", "sum"), v=("volume", "sum")
    )
    grp["price"] = grp["pv"] / grp["v"]
    wide = grp.pivot(index="date", columns="EPC", values="price").sort_index()

    wide = wide.loc["2019-01-01":"2024-06-30"]
    gap = (np.log(wide["Missing"]) - np.log(wide["Intensive"])).dropna()
    smoother = gap.rolling(window=3, center=True, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=FIGSIZE_TEXTWIDTH)
    ax.plot(gap.index, gap.values, color=SPRED, linewidth=1.4, label="Monthly gap")
    ax.plot(smoother.index, smoother.values, color=BBLUE, linewidth=2.0, label="3-month MA")
    ax.axhline(0.0, color="#7f7f7f", linewidth=0.8, linestyle=":")
    ax.axvline(REFORM, color="#2b2b2b", linewidth=0.9, linestyle="--")
    ymin, ymax = ax.get_ylim()
    ax.text(
        REFORM + pd.Timedelta(days=20),
        ymax - 0.04 * (ymax - ymin),
        "DPE reform",
        rotation=90,
        va="top",
        ha="left",
        fontsize=8,
        color="#2b2b2b",
    )
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlabel("Listing month")
    ax.set_ylabel(r"Log price gap: non-disclosed $-$ energy-intensive")
    ax.legend(loc="best", frameon=False)

    out = outdir / "fig_fact1_nondiscl_premium_eventstudy.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    pre = float(gap.loc[: REFORM - pd.Timedelta(days=1)].mean())
    post = float(gap.loc[REFORM:].mean())
    print(f"[fact1/{cfg.folder}] saved -> {out}  pre={pre:+.4f}  post={post:+.4f}")
    return out, pre, post


def make_fact2(cfg: PropertyConfig, outdir: Path) -> tuple[Path, float, float, float]:
    df = pd.read_csv(ROOT / "data" / f"index_{cfg.code}.csv", parse_dates=["date"])
    df = df[df["item_type"] == cfg.code].copy()
    vol = df.groupby(["date", "EPC"], as_index=False)["volume"].sum()
    tot = vol.groupby("date")["volume"].sum().rename("tot")
    miss = vol[vol["EPC"] == "Missing"].set_index("date")["volume"].rename("miss")
    s = pd.concat([tot, miss], axis=1).fillna(0.0)
    s["share"] = s["miss"] / s["tot"]
    s = s.sort_index()
    last12 = float(s["share"].iloc[-12:].mean())

    fig, ax = plt.subplots(figsize=FIGSIZE_TEXTWIDTH)
    ax.fill_between(s.index, 0, s["share"].values, color=BBLUE, alpha=0.25, linewidth=0)
    ax.plot(s.index, s["share"].values, color=SPRED, linewidth=1.6)
    ax.axhline(
        last12,
        color="#7f7f7f",
        linewidth=0.9,
        linestyle="--",
        label=f"Final 12-month mean = {last12:.2f}",
    )
    ax.axvline(REFORM, color="#2b2b2b", linewidth=0.9, linestyle="--")
    ymin, ymax = ax.get_ylim()
    ax.text(
        REFORM + pd.Timedelta(days=20),
        ymax - 0.04 * (ymax - ymin),
        "DPE legally opposable",
        rotation=90,
        va="top",
        ha="left",
        fontsize=8,
        color="#2b2b2b",
    )
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlabel("Listing month")
    ax.set_ylabel("Share of listings without certified EPC")
    ax.set_ylim(0, max(0.55, s["share"].max() * 1.05))
    ax.legend(loc="best", frameon=False)

    out = outdir / "fig_fact2_missing_share_timeseries.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    pre = float(s.loc[: REFORM - pd.Timedelta(days=1), "share"].mean())
    post = float(s.loc[REFORM:, "share"].mean())
    print(f"[fact2/{cfg.folder}] saved -> {out}  pre={pre:.4f}  post={post:.4f}  last12={last12:.4f}")
    return out, pre, post, last12


def make_fact3(cfg: PropertyConfig, outdir: Path) -> Path:
    """3-group decomposition using estimation-sample shares from results.txt."""
    segments = [
        # Note: share_truthful is ALL disclosers (d=1), verified and unmatched alike,
        # because classify_listings(unverified_disclosers="honest") folds (d=1, K=0)
        # into truthful_disclosure. Labelling this "K=1, d=1" would misstate it.
        ("Discloses a score (d=1)", cfg.share_truthful, BBLUE, "white"),
        ("Silent, no registry record (d=0, K=0)", cfg.share_uninformed, "#9e9e9e", "black"),
        ("Strategic hiding (d=0, K=1)", cfg.share_hiding, SPRED, "white"),
    ]

    fig, ax = plt.subplots(figsize=(6.5, 2.0))
    left = 0.0
    for label, share, color, txtcolor in segments:
        ax.barh(0, share, left=left, color=color, edgecolor="white", linewidth=0.8)
        if share > 0.06:
            ax.text(
                left + share / 2,
                0,
                f"{share*100:.1f}%",
                ha="center",
                va="center",
                color=txtcolor,
                fontsize=9,
            )
        elif share > 0.005:
            # Tiny segment (e.g., 1.1% for houses): place the label above the bar
            ax.annotate(
                f"{share*100:.1f}%",
                xy=(left + share / 2, 0.0),
                xytext=(left + share / 2, 0.45),
                ha="center",
                va="bottom",
                color=color,
                fontsize=8,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.5),
            )
        left += share

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, 0.9)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.grid(False)
    for spine in ("left", "bottom", "top", "right"):
        ax.spines[spine].set_visible(False)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="white") for _, _, c, _ in segments
    ]
    labels = [lbl for lbl, _, _, _ in segments]
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
        frameon=False,
        fontsize=8,
        handlelength=1.2,
        handletextpad=0.5,
        columnspacing=1.4,
    )

    out = outdir / "fig_fact3_three_group_decomposition.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(
        f"[fact3/{cfg.folder}] saved -> {out}  "
        f"truthful={cfg.share_truthful*100:.1f}%  "
        f"uninformed={cfg.share_uninformed*100:.1f}%  "
        f"hiding={cfg.share_hiding*100:.1f}%"
    )
    return out


def make_fact4(cfg: PropertyConfig, outdir: Path) -> tuple[Path, pd.DataFrame]:
    df = pd.read_parquet(
        ROOT / "data" / f"listings_enriched_{cfg.code}.parquet",
        columns=["K", "d", "ademe_epc_letter"],
    )
    informed = df[(df["K"] == 1) & df["ademe_epc_letter"].notna()].copy()
    classes = ["A", "B", "C", "D", "E", "F", "G"]
    truthful = informed[informed["d"] == 1]["ademe_epc_letter"].value_counts(normalize=True)
    hiding = informed[informed["d"] == 0]["ademe_epc_letter"].value_counts(normalize=True)
    truthful = truthful.reindex(classes, fill_value=0.0)
    hiding = hiding.reindex(classes, fill_value=0.0)

    fig, ax = plt.subplots(figsize=FIGSIZE_TEXTWIDTH)
    x = np.arange(len(classes))
    w = 0.4
    ax.bar(
        x - w / 2,
        truthful.values,
        width=w,
        color=BBLUE,
        edgecolor="white",
        linewidth=0.5,
        label="Truthful disclosure (d=1)",
    )
    ax.bar(
        x + w / 2,
        hiding.values,
        width=w,
        color=SPRED,
        edgecolor="white",
        linewidth=0.5,
        label="Strategic hiding (d=0)",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.set_xlabel("Verified ADEME energy class")
    ax.set_ylabel("Share within group")
    ax.legend(loc="upper left", frameon=False)
    ax.set_ylim(0, max(truthful.max(), hiding.max()) * 1.15)

    out = outdir / "fig_fact4_audit_class_by_hider_type.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    tab = pd.DataFrame({"truthful": truthful, "hiding": hiding})
    score = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
    mt = sum(tab.loc[c, "truthful"] * score[c] for c in classes)
    mh = sum(tab.loc[c, "hiding"] * score[c] for c in classes)
    print(f"[fact4/{cfg.folder}] saved -> {out}  mean_truthful={mt:.2f}  mean_hiding={mh:.2f}")
    print((tab * 100).round(2).to_string())
    return out, tab


def run_for_property(cfg: PropertyConfig) -> None:
    outdir = ROOT / "paper" / "fig" / "stylized_facts" / cfg.folder
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {cfg.code} ===")
    print(f"output dir: {outdir}")
    make_fact1(cfg, outdir)
    make_fact2(cfg, outdir)
    make_fact3(cfg, outdir)
    # Fact 4 (ADEME-class composition) was retired from the paper.


def main() -> None:
    for cfg in CONFIGS:
        run_for_property(cfg)


if __name__ == "__main__":
    main()
