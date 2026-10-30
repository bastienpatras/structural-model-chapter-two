"""Paper-quality static figures for Section 5 (policy extension under limited attention).

Seven exhibits, all read from the CSVs written by ``scripts/compute_attention.py``
(``results/attention/``). Nothing is re-estimated here: every number drawn or printed
on a figure is read from those files.

  fig_att_policy_rbar_dist          market renovation threshold R_bar = b (EUR/m2), with the
                                    benchmark renovation costs and the old core-solver R_bar
  fig_att_policy_takeup             share of markets (unweighted) where a uniform subsidy S
                                    covers the market minimum S*, against S, by benchmark R_hat
  fig_att_policy_salience           2x2: hiding rate and mean R_bar along the attention path
                                    (psi), dominant-regime bands behind, estimate psi_hat marked
  fig_att_policy_bound              apartments: R_bar at the maintained reading vs the
                                    full-attention bound (rho = 1), market by market
  fig_att_policy_regimes            regime shares and mean hiding rate by scenario
  fig_att_policy_sgrid              distribution of the market minimum subsidy S* (attention)
  fig_att_policy_rbar_core_vs_att   old core-solver R_bar against the attention R_bar = b

Units: b, c0 and R_bar are stored in log points; R_bar in EUR/m2 is R_bar / 100 x price.
Style, palette and helpers are imported from ``scripts/make_attention_figures.py``; the
regime colours follow ``scripts/make_subsidy_figures.py::REGIME_COLORS`` (navy = Partial
Pooling, teal = Cost-Deterred Hiding, SPred = Complete Adverse Selection). PDFs go to
``paper/fig/visuals/``; a PNG copy (dpi 200) of each is written next to it for review.

CLI
---
  python3 scripts/make_attention_policy_figures.py [--out-dir paper/fig/visuals]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

# make_subsidy_figures is imported first so that make_attention_figures' rcParams win.
from make_subsidy_figures import REGIME_COLORS as _SUBSIDY_REGIME_COLORS  # noqa: E402
from make_subsidy_figures import REGIME_LABELS as _SUBSIDY_REGIME_LABELS  # noqa: E402
from make_attention_figures import (  # noqa: E402
    AMBER, ATT, BBLUE, BOX, DEFAULT_OUT, GREY, INK, LIGHT_GREY, NAVY, ROOT, SEG_COLORS,
    SEG_LABELS, SEG_MARKERS, SEGMENTS, SPRED, _save, fmt, load,
)

# Regime codes written by compute_attention.py -> make_subsidy_figures' regime keys.
REGIME_KEY = {"PP": "mixed_strategy", "CD": "full_unraveling", "CAS": "partial_separation"}
REGIME_ORDER = ["PP", "CD", "CAS"]
REGIME_COLORS = {k: _SUBSIDY_REGIME_COLORS[v] for k, v in REGIME_KEY.items()}
REGIME_LABELS = {k: _SUBSIDY_REGIME_LABELS[v] for k, v in REGIME_KEY.items()}

SCENARIOS = ["base", "sal", "pi1", "hi"]
SCENARIO_LABELS = {
    "base": r"Observed attention ($\hat\psi$)",
    "sal": r"Salience ($\psi \to 1$)",
    "pi1": r"All sellers informed ($\pi \to 1$)",
    "hi": r"Full-attention bound ($\rho = 1$)",
}
EXPECTED_N = {"apartment": 45, "house": 97}
SEG_KEY = {seg: key for seg, _, key in SEGMENTS}
SEG_COL = {seg: col for seg, col, _ in SEGMENTS}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_policy_inputs() -> dict:
    """Read the shared inputs (via make_attention_figures.load) plus the Section 5 files."""
    needed = [ATT / f"{seg}_{kind}.csv" for seg, _, _ in SEGMENTS
              for kind in ("scenarios", "policy", "markets")]
    needed += [ATT / f for f in ("takeup_curve.csv", "attention_path.csv",
                                 "salience_path.csv", "summary.csv")]
    missing = [str(p.relative_to(ROOT)) for p in needed if not p.exists()]
    assert not missing, f"missing inputs: {missing}"

    data = load()                         # summary, salience path, markets, policy (+ drift checks)
    data["takeup"] = pd.read_csv(ATT / "takeup_curve.csv")
    data["apath"] = pd.read_csv(ATT / "attention_path.csv")
    data["scen"] = {}
    s = data["summary"]
    for seg, col, _ in SEGMENTS:
        sc = pd.read_csv(ATT / f"{seg}_scenarios.csv")
        pol = data["policy"][seg]
        n = EXPECTED_N[seg]
        assert len(sc) == len(pol) == n == int(s.loc["n_markets", col]), f"{seg}: expected {n} markets"
        assert (sc["market_id"].to_numpy() == pol["market_id"].to_numpy()).all(), f"{seg}: market order"
        assert np.allclose(sc["rbar_base"], sc["b1"]), f"{seg}: rbar_base != b1"
        for name in SCENARIOS:
            for c in (f"rbar_{name}", f"sigma0_{name}", f"regime_{name}"):
                assert c in sc.columns, f"{seg}: missing column {c}"
        # EUR/m2 versions of the thresholds (log points / 100 x price).
        price = sc["price_eur_m2"]
        for name in SCENARIOS:
            sc[f"rbar_{name}_eur"] = sc[f"rbar_{name}"] / 100.0 * price
        sc["rbar_core_eur"] = pol["rbar_core"].to_numpy() / 100.0 * price
        assert np.isclose(sc["rbar_base_eur"].mean(), s.loc["sc_base_rbar", col]), f"{seg}: R_bar drift"
        assert np.isclose(sc["rbar_hi_eur"].mean(), s.loc["sc_hi_rbar", col]), f"{seg}: bound drift"
        data["scen"][seg] = sc
    data["rhats"] = sorted(float(r) for r in data["takeup"]["R_hat"].unique())
    for seg in data["scen"]:
        for r in data["rhats"]:
            assert f"S_ext_{int(r)}" in data["policy"][seg].columns, f"{seg}: missing S_ext_{int(r)}"
    return data


def _seg_title(seg: str, n: int) -> str:
    return f"{SEG_LABELS[seg]} (N = {n})"


def _eur(x: float) -> str:
    return f"{x:,.0f}"


# ---------------------------------------------------------------------------
# (1) Distribution of the market threshold R_bar
# ---------------------------------------------------------------------------

def make_rbar_dist(data: dict, out_dir: Path) -> Path:
    rhats = data["rhats"]
    vals = np.concatenate([np.r_[d["rbar_base_eur"], d["rbar_core_eur"]] for d in data["scen"].values()])
    width = 25.0
    x_hi = width * np.ceil((max(vals.max(), max(rhats)) * 1.04) / width)
    bins = np.arange(0.0, x_hi + width, width)

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.9), sharey=True)
    for ax, (seg, _, _) in zip(axes, SEGMENTS):
        d = data["scen"][seg]
        c = SEG_COLORS[seg]
        ax.hist(d["rbar_base_eur"], bins=bins, color=c, alpha=0.85, edgecolor="white",
                lw=0.5, zorder=2)
        ax.hist(d["rbar_core_eur"], bins=bins, histtype="step", color=INK, lw=0.9,
                ls=(0, (3, 1.5)), alpha=0.75, zorder=3)
        for r, ls in zip(rhats, ("--", ":")):
            ax.axvline(r, color=INK, ls=ls, lw=1.1, zorder=4)
        med = float(d["rbar_base_eur"].median())
        lines = [f"median: {_eur(med)} €/m²"]
        lines += [rf"$\bar R_m \geq {r:.0f}$: {int((d['rbar_base_eur'] >= r).sum())} of {len(d)}" for r in rhats]
        ax.text(0.97, 0.96, "\n".join(lines), transform=ax.transAxes, ha="right", va="top",
                fontsize=7.8, color=INK, bbox=BOX, zorder=6, multialignment="left")
        ax.set_xlim(0, x_hi)
        ax.set_title(_seg_title(seg, len(d)), fontsize=10.5, color=INK)
        ax.set_xlabel(r"Renovation threshold $\bar R_m$ (€/m²)")
        ax.grid(axis="x", visible=False)
        ax.tick_params(labelleft=True)
    axes[0].set_ylabel("Number of markets")
    handles = [
        Patch(facecolor=NAVY, alpha=0.85, label=r"Attention model, $\bar R_m = \hat b_m$ (apartments)"),
        Patch(facecolor=SPRED, alpha=0.85, label=r"Attention model, $\bar R_m = \hat b_m$ (houses)"),
        Line2D([0], [0], color=INK, lw=0.9, ls=(0, (3, 1.5)), alpha=0.75,
               label="Core solver (previous version)"),
        Line2D([0], [0], color="none", label=" "),
    ] + [Line2D([0], [0], color=INK, ls=ls, lw=1.1,
                label=rf"Renovation cost $\hat R$ = {r:.0f} €/m²")
         for r, ls in zip(rhats, ("--", ":"))]
    fig.subplots_adjust(bottom=0.30, wspace=0.10)
    fig.legend(handles=handles, ncol=3, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.2)
    return _save(fig, out_dir, "fig_att_policy_rbar_dist")


# ---------------------------------------------------------------------------
# (2) Coverage of a uniform subsidy, counted by market
# ---------------------------------------------------------------------------

TAKEUP_LS = {0: "-", 1: (0, (4, 1.6))}        # first R_hat solid, second dashed


def _ecdf(v: np.ndarray, x_max: float) -> tuple[np.ndarray, np.ndarray]:
    """Empirical cdf of v (share in %) as a steps-post curve on [0, x_max]."""
    v = np.sort(np.asarray(v, dtype=float))
    n = v.size
    xs = np.r_[0.0, v, x_max]
    ys = np.r_[np.mean(v <= 0.0), np.arange(1, n + 1) / n, 1.0] * 100.0
    keep = xs <= x_max
    return xs[keep], ys[keep]


def make_takeup(data: dict, out_dir: Path) -> Path:
    """Share of markets whose minimum subsidy S*_m a uniform subsidy S covers, by R_hat.

    Unweighted empirical cdf of S*_m = max{R_hat - R_bar_m, 0} (attention model, EUR/m2),
    read from <segment>_scenarios.csv (S_base_<R_hat>). Counting markets rather than
    listings keeps one large market (Paris for apartments) from dominating the curve;
    its listing share is reported in the note under each panel.
    """
    s, rhats = data["summary"], data["rhats"]
    assert "top_market_share" in s.index, "summary.csv lacks the top_market_share row"
    x_max = 500.0
    assert max(rhats) <= x_max, "x-axis must reach the largest renovation benchmark"

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.9), sharey=True)
    fig.subplots_adjust(bottom=0.27, top=0.90, wspace=0.10, left=0.10, right=0.98)
    for ax, (seg, col, _) in zip(axes, SEGMENTS):
        sc = data["scen"][seg]
        c = SEG_COLORS[seg]
        n = len(sc)
        assert n == int(s.loc["n_markets", col]), f"{seg}: market count drift"
        ax.axhline(50, color=LIGHT_GREY, lw=0.7, ls=":", zorder=1)
        meds = {}
        for j, r in enumerate(rhats):
            name = f"S_base_{int(r)}"
            assert name in sc.columns, f"{seg}: missing {name}"
            v = sc[name].to_numpy()
            assert np.allclose(v, np.maximum(r - sc["rbar_base_eur"].to_numpy(), 0.0)), \
                f"{seg}: {name} != max(R_hat - R_bar, 0)"
            xs, ys = _ecdf(v, x_max)
            ax.plot(xs, ys, drawstyle="steps-post", color=c, lw=1.8, ls=TAKEUP_LS[j], zorder=3)
            med = float(np.median(v))
            meds[r] = med
            ax.plot([med, med], [0, 50], color=c, lw=0.8, alpha=0.55, zorder=2)
            ax.scatter([med], [50], s=30, marker=SEG_MARKERS[seg], color=c, edgecolor="white",
                       lw=0.6, zorder=5)
            # Direct label in an empty region next to the curve's median crossing: below-right
            # for the first benchmark (the second curve is still near zero there), above-left
            # for the second (the first curve is already at 100% there).
            lab = rf"$\hat R$ = {r:.0f} €/m²" + "\n" + rf"median $S^*_m$ = {_eur(med)} €/m²"
            if j == 0:
                ax.text(med + 9, 36, lab, ha="left", va="center", fontsize=8.2, color=c,
                        zorder=6, linespacing=1.2)
            else:
                ax.text(med - 9, 64, lab, ha="right", va="center", fontsize=8.2, color=c,
                        zorder=6, linespacing=1.2)
        ax.set_xlim(0, x_max)
        ax.set_ylim(0, 102)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.set_xlabel(r"Uniform subsidy $S$ (€/m²)")
        ax.set_title(f"{SEG_LABELS[seg]} (N = {n} markets)", fontsize=10.5, color=INK)
        r0 = rhats[0]
        n0 = int((sc[f"S_base_{int(r0)}"] <= 0).sum())
        top = float(s.loc["top_market_share", col])
        note = (rf"$S^*_m = 0$ at $\hat R$ = {r0:.0f}: {n0} of {n} markets ({100 * n0 / n:.0f}%)"
                + "\n" + f"Largest market: {top:.0f}% of informed low-quality listings")
        ax.text(0.0, -0.25, note, transform=ax.transAxes, ha="left", va="top",
                fontsize=7.8, color=GREY, linespacing=1.3)
    axes[0].set_ylabel("Share of markets where the\nsubsidy covers the minimum")
    return _save(fig, out_dir, "fig_att_policy_takeup")


# ---------------------------------------------------------------------------
# (3) Salience: who hides, not who renovates
# ---------------------------------------------------------------------------

REGIME_ALPHA = {"CAS": 0.18, "PP": 0.18, "CD": 0.32}   # teal is pale: raised to stay visible


def _regime_spans(d: pd.DataFrame) -> list[tuple[float, float, str]]:
    """Contiguous psi intervals labelled by the dominant regime on the attention grid.

    Each grid point owns the half-way interval to its neighbours; neighbours with the
    same dominant regime are merged.
    """
    psi = d["psi"].to_numpy()
    shares = np.column_stack([d[f"share_{r.lower()}"].to_numpy() for r in REGIME_ORDER])
    dom = [REGIME_ORDER[i] for i in shares.argmax(axis=1)]
    edges = np.r_[psi[0], 0.5 * (psi[1:] + psi[:-1]), psi[-1]]
    spans = []
    for i, r in enumerate(dom):
        if spans and spans[-1][2] == r:
            spans[-1] = (spans[-1][0], edges[i + 1], r)
        else:
            spans.append((edges[i], edges[i + 1], r))
    return spans


def make_salience(data: dict, out_dir: Path) -> Path:
    """2x2 small multiples along relative attention psi, c0 held fixed.

    Top row: mean hiding rate (salience_path.csv, psi step 0.001, so the cliff is not drawn
    as a chord). Bottom row: mean renovation threshold R_bar in EUR/m2 (attention_path.csv,
    psi step 0.01). Background bands: dominant regime at each psi (attention_path.csv). The
    two files are checked to agree on their shared grid points; the values at psi_hat are
    read from summary.csv and checked against the paths.
    """
    s, path, fine = data["summary"], data["apath"], data["path"]
    rb_top = 25.0 * np.ceil(float(path["mean_rbar_eur"].max()) * 1.15 / 25.0)

    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.6), sharex=True, sharey="row")
    fig.subplots_adjust(bottom=0.17, top=0.93, hspace=0.12, wspace=0.08, left=0.10, right=0.98)
    for k, (seg, col, key) in enumerate(SEGMENTS):
        d = path[path["segment"] == key].sort_values("psi")
        f = fine[fine["segment"] == key].sort_values("psi")
        chk = pd.merge(d.assign(p=d["psi"].round(6)), f.assign(p=f["psi"].round(6)),
                       on="p", suffixes=("", "_fine"))
        assert len(chk) == len(d), f"{seg}: attention and salience paths do not share the grid"
        assert np.allclose(chk["mean_sigma0"], chk["mean_sigma0_fine"]), f"{seg}: path drift"
        assert np.allclose(d[[f"share_{r.lower()}" for r in REGIME_ORDER]].sum(axis=1), 1.0), \
            f"{seg}: regime shares do not sum to one"

        c = SEG_COLORS[seg]
        n = int(s.loc["n_markets", col])
        psi_hat = float(s.loc["psi", col])
        sig_hat = float(s.loc["sigma0_obs_mean", col])          # observed mean hiding (%)
        rb_hat = float(s.loc["sc_base_rbar", col])              # mean R_bar at psi_hat (EUR/m2)
        # The paths must pass through the estimate (linear interpolation tolerance).
        assert abs(100 * np.interp(psi_hat, f["psi"], f["mean_sigma0"]) - sig_hat) < 1.0, \
            f"{seg}: hiding path does not pass through the observed hiding rate at psi_hat"
        assert abs(np.interp(psi_hat, d["psi"], d["mean_rbar_eur"]) - rb_hat) < 1.0, \
            f"{seg}: threshold path does not pass through mean R_bar at psi_hat"

        top, bot = axes[0, k], axes[1, k]
        spans = _regime_spans(d)
        for ax in (top, bot):
            for lo, hi, r in spans:
                ax.axvspan(lo, hi, color=REGIME_COLORS[r], alpha=REGIME_ALPHA[r], lw=0, zorder=0)
            ax.axvline(psi_hat, color=INK, lw=0.9, ls=":", zorder=4)
            ax.grid(axis="x", visible=False)

        top.plot(f["psi"], 100 * f["mean_sigma0"], color=c, lw=1.8, zorder=3)
        bot.plot(d["psi"], d["mean_rbar_eur"], color=c, lw=1.8, zorder=3)
        top.scatter([psi_hat], [sig_hat], s=40, marker=SEG_MARKERS[seg], facecolor="white",
                    edgecolor=c, lw=1.4, zorder=5)
        bot.scatter([psi_hat], [rb_hat], s=40, marker=SEG_MARKERS[seg], facecolor="white",
                    edgecolor=c, lw=1.4, zorder=5)

        # Labels sit on the open side of the estimate line.
        right = psi_hat < 0.5
        dx = 0.025 if right else -0.025
        ha = "left" if right else "right"
        bot.text(psi_hat + dx, 0.06 * rb_top, rf"estimate $\hat\psi$ = {psi_hat:.2f}", ha=ha,
                 va="bottom", fontsize=8.2, color=INK, zorder=6)
        top.text(psi_hat + dx, sig_hat + 6, f"hiding {fmt(sig_hat)}%", ha=ha, va="bottom",
                 fontsize=8.2, color=c, zorder=6)
        bot.text(psi_hat + dx, rb_hat + 0.05 * rb_top, f"threshold {_eur(rb_hat)} €/m²", ha=ha,
                 va="bottom", fontsize=8.2, color=c, zorder=6)

        top.set_title(f"{SEG_LABELS[seg]} (N = {n})", fontsize=10.5, color=INK)
        top.set_ylim(-3, 103)
        top.set_yticks([0, 25, 50, 75, 100])
        bot.set_ylim(0, rb_top)
        bot.set_xlim(0, 1)
        bot.set_xlabel(r"Relative attention to silent listings $\psi$")
    axes[0, 0].set_ylabel("Hiding rate (%)")
    axes[1, 0].set_ylabel("Renovation threshold (€/m²)")

    handles = [Patch(facecolor=REGIME_COLORS[r], alpha=REGIME_ALPHA[r], edgecolor=LIGHT_GREY,
                     lw=0.4, label=REGIME_LABELS[r])
               for r in ("CAS", "PP", "CD")]
    fig.legend(handles=handles, ncol=3, frameon=False, loc="lower center",
               bbox_to_anchor=(0.54, 0.0), fontsize=8.3, title="Dominant regime",
               title_fontsize=8.3)
    return _save(fig, out_dir, "fig_att_policy_salience")


# ---------------------------------------------------------------------------
# (4) Full-attention bound, apartments
# ---------------------------------------------------------------------------

def make_bound(data: dict, out_dir: Path) -> Path:
    seg = "apartment"
    rhats = data["rhats"]
    d = data["scen"][seg].sort_values("rbar_base_eur").reset_index(drop=True)
    n = len(d)
    y = np.arange(n)
    cas = (d["regime_hi"] == "CAS").to_numpy()
    c = SEG_COLORS[seg]

    fig, ax = plt.subplots(figsize=(8.0, 7.6))
    x_hi = 25.0 * np.ceil(max(d["rbar_hi_eur"].max(), max(rhats)) * 1.06 / 25.0)
    for r, ls in zip(rhats, ("--", ":")):
        ax.axvline(r, color=INK, ls=ls, lw=1.0, zorder=1)
    ax.hlines(y, d["rbar_base_eur"], d["rbar_hi_eur"], color=c, alpha=0.45, lw=1.2, zorder=2)
    ax.scatter(d["rbar_base_eur"], y, s=24, marker="o", facecolor="white", edgecolor=c,
               lw=1.0, zorder=3)
    ax.scatter(d.loc[~cas, "rbar_hi_eur"], y[~cas], s=24, marker="o", color=c,
               edgecolor="white", lw=0.4, zorder=4)
    ax.scatter(d.loc[cas, "rbar_hi_eur"], y[cas], s=34, marker="D", color=AMBER,
               edgecolor=INK, lw=0.5, zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels(d["market_id"].astype(str), fontsize=6.4)
    ax.set_ylim(-0.8, n - 0.2)
    ax.set_xlim(0, x_hi)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(r"Renovation threshold $\bar R_m$ (€/m²)")
    ax.set_ylabel(r"Market identifier (sorted by $\hat b_m$ in €/m²)")
    ax.set_title(_seg_title(seg, n), fontsize=10.5, color=INK)

    lines = [rf"mean $\bar R_m$: {_eur(d['rbar_base_eur'].mean())} → {_eur(d['rbar_hi_eur'].mean())} €/m²"]
    for r in rhats:
        lines.append(rf"$\bar R_m \geq {r:.0f}$: {int((d['rbar_base_eur'] >= r).sum())} → "
                     f"{int((d['rbar_hi_eur'] >= r).sum())} of {n}")
    lines.append(f"Complete Adverse Selection under the bound: {int(cas.sum())}")
    ax.text(0.98, 0.02, "\n".join(lines), transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=INK, bbox=BOX, zorder=6, multialignment="left")

    handles = [
        Line2D([0], [0], marker="o", ls="none", mfc="white", mec=c, mew=1.0, ms=5.5,
               label=r"Maintained reading, $\bar R_m = \hat b_m$"),
        Line2D([0], [0], marker="o", ls="none", mfc=c, mec="white", ms=5.5,
               label=r"Full-attention bound ($\rho = 1$): an upper bound, not an estimate"),
        Line2D([0], [0], marker="D", ls="none", mfc=AMBER, mec=INK, mew=0.5, ms=5.5,
               label="Bound lands in Complete Adverse Selection"),
    ] + [Line2D([0], [0], color=INK, ls=ls, lw=1.0, label=rf"$\hat R$ = {r:.0f} €/m²")
         for r, ls in zip(rhats, ("--", ":"))]
    fig.subplots_adjust(bottom=0.155)
    fig.legend(handles=handles, ncol=2, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.3)
    return _save(fig, out_dir, "fig_att_policy_bound")


# ---------------------------------------------------------------------------
# (5) Regime shares by scenario
# ---------------------------------------------------------------------------

def make_regimes(data: dict, out_dir: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.7), sharey=True)
    ypos = np.arange(len(SCENARIOS))[::-1]
    for ax, (seg, col, _) in zip(axes, SEGMENTS):
        d = data["scen"][seg]
        n = len(d)
        for yv, name in zip(ypos, SCENARIOS):
            left = 0.0
            for r in REGIME_ORDER:
                share = 100.0 * float((d[f"regime_{name}"] == r).mean())
                if share <= 0:
                    continue
                hatch = "////" if (seg == "house" and name == "hi" and r == "CAS") else None
                ax.barh(yv, share, left=left, height=0.62, color=REGIME_COLORS[r],
                        edgecolor="white", lw=0.6, hatch=hatch, zorder=2)
                if share >= 12:
                    ax.text(left + share / 2, yv, f"{share:.0f}%", ha="center", va="center",
                            fontsize=7.6, color="white" if r != "CD" else INK, zorder=4,
                            bbox=(dict(boxstyle="round,pad=0.15", fc=REGIME_COLORS[r], ec="none")
                                  if hatch else None))
                left += share
            sig = 100.0 * float(d[f"sigma0_{name}"].mean())
            assert np.isclose(sig, s_val := float(data["summary"].loc[f"sc_{name}_sigma", col])), \
                f"{seg}/{name}: hiding-rate drift ({sig} vs {s_val})"
            ax.text(102, yv, f"{fmt(sig)}%", ha="left", va="center", fontsize=8.2, color=INK)
        ax.text(102, len(SCENARIOS) - 0.55, "mean\nhiding rate", ha="left", va="bottom",
                fontsize=7.4, color=GREY, linespacing=0.95)
        if seg == "house":
            ax.text(100, ypos[SCENARIOS.index("hi")] - 0.36,
                    "hatched: artefact of a single hiding cost per market",
                    ha="right", va="top", fontsize=7.4, color=INK, style="italic")
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.set_xlabel("Share of markets")
        ax.set_title(_seg_title(seg, n), fontsize=10.5, color=INK, pad=8)
        ax.grid(axis="y", visible=False)
        ax.set_ylim(-0.75, len(SCENARIOS) - 0.1)
    axes[0].set_yticks(ypos)
    axes[0].set_yticklabels([SCENARIO_LABELS[k] for k in SCENARIOS])
    handles = [Patch(facecolor=REGIME_COLORS[r], label=REGIME_LABELS[r]) for r in REGIME_ORDER]
    handles.append(Patch(facecolor=REGIME_COLORS["CAS"], edgecolor="white", hatch="////",
                         label="Artefact of a single hiding cost"))
    fig.subplots_adjust(bottom=0.25, wspace=0.20, right=0.93)
    fig.legend(handles=handles, ncol=4, frameon=False, loc="lower center",
               bbox_to_anchor=(0.52, 0.0), fontsize=8.2)
    return _save(fig, out_dir, "fig_att_policy_regimes")


# ---------------------------------------------------------------------------
# (6) Distribution of the minimum subsidy S* (attention)
# ---------------------------------------------------------------------------

def make_sgrid(data: dict, out_dir: Path) -> Path:
    rhats = data["rhats"]
    col_ranges = {}
    for r in rhats:
        v = np.concatenate([data["policy"][seg][f"S_ext_{int(r)}"].to_numpy() for seg, _, _ in SEGMENTS])
        lo, hi = float(v.min()), float(v.max())
        pad = 0.04 * (hi - lo if hi > lo else 1.0)
        col_ranges[r] = (lo - pad, hi + pad)

    fig, axes = plt.subplots(2, len(rhats), figsize=(8.0, 5.0), sharex="col")
    for i, (seg, _, _) in enumerate(SEGMENTS):
        pol = data["policy"][seg]
        for j, r in enumerate(rhats):
            ax = axes[i, j]
            v = pol[f"S_ext_{int(r)}"].to_numpy()
            lo, hi = col_ranges[r]
            ax.hist(v, bins=np.linspace(lo, hi, 19), color=SEG_COLORS[seg], edgecolor="white",
                    lw=0.4, alpha=0.9, zorder=2)
            pos = v[v > 0]
            med = float(np.median(pos)) if pos.size else float(np.median(v))
            ax.axvline(med, color=INK, ls="--", lw=1.0, zorder=5)
            ax.set_ylim(0, ax.get_ylim()[1] * 1.30)
            # Box hugs the median line on its wider side, above the bars.
            frac = (med - lo) / (hi - lo)
            left_side = frac > 0.5
            ax.text(frac - 0.02 if left_side else frac + 0.02, 0.96,
                    rf"median ($S^*_m > 0$): {_eur(med)} €/m²" + "\n"
                    + rf"$S^*_m = 0$: {int((v <= 0).sum())} of {len(v)}",
                    transform=ax.transAxes, ha="right" if left_side else "left",
                    va="top", fontsize=7.6, color=INK, bbox=BOX, zorder=6, multialignment="left")
            ax.set_xlim(lo, hi)
            ax.grid(axis="x", visible=False)
            if i == 0:
                ax.set_title(rf"Renovation cost $\hat R$ = {r:.0f} €/m²", fontsize=10.5, color=INK)
            if i == len(SEGMENTS) - 1:
                ax.set_xlabel(r"Minimum subsidy $S^*_m$ (€/m²)")
            if j == 0:
                ax.set_ylabel(f"{SEG_LABELS[seg]}\nnumber of markets")
    handles = [Line2D([0], [0], color=INK, ls="--", lw=1.0,
                      label=r"Median minimum subsidy (markets with $S^*_m > 0$)")]
    fig.subplots_adjust(hspace=0.28, wspace=0.22, bottom=0.15)
    fig.legend(handles=handles, ncol=1, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.3)
    return _save(fig, out_dir, "fig_att_policy_sgrid")


# ---------------------------------------------------------------------------
# (7) Core-solver R_bar vs attention R_bar
# ---------------------------------------------------------------------------

def make_core_vs_att(data: dict, out_dir: Path) -> Path:
    allv = np.concatenate([np.r_[d["rbar_base_eur"], d["rbar_core_eur"]] for d in data["scen"].values()])
    hi = 25.0 * np.ceil(allv.max() * 1.05 / 25.0)
    lo = min(0.0, float(allv.min()))
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.4))
    for ax, (seg, col, _) in zip(axes, SEGMENTS):
        d = data["scen"][seg]
        c = SEG_COLORS[seg]
        ax.plot([lo, hi], [lo, hi], color=GREY, ls="--", lw=0.9, zorder=1)
        ax.scatter(d["rbar_base_eur"], d["rbar_core_eur"], s=22, color=c, marker=SEG_MARKERS[seg],
                   edgecolor="white", lw=0.4, alpha=0.9, zorder=3)
        gap = d["rbar_base_eur"] - d["rbar_core_eur"]
        gap_lp = data["policy"][seg]["rbar_ext"] - data["policy"][seg]["rbar_core"]
        assert np.isclose(gap_lp.mean(), data["summary"].loc["rbar_gap_mean", col]), f"{seg}: gap drift"
        txt = (rf"mean $\bar R_m$ (€/m²): attention {_eur(d['rbar_base_eur'].mean())}, "
               f"core {_eur(d['rbar_core_eur'].mean())}\n"
               f"gap, attention − core (€/m²):\nmean {fmt(gap.mean())}, max {fmt(gap.max())}; "
               f"mean {fmt(gap_lp.mean(), 2)} log points\n"
               f"core below attention: {int((gap > 0).sum())} of {len(d)}")
        ax.text(0.03, 0.97, txt, transform=ax.transAxes, ha="left", va="top", fontsize=7.6,
                color=INK, bbox=BOX, zorder=6, multialignment="left")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(_seg_title(seg, len(d)), fontsize=10.5, color=INK)
        ax.set_xlabel(r"Attention model $\bar R_m = \hat b_m$ (€/m²)")
    axes[0].set_ylabel(r"Core solver $\bar R_m$ (€/m²)")
    handles = [
        Line2D([0], [0], marker="o", ls="none", color=NAVY, ms=5.5, label="Apartments"),
        Line2D([0], [0], marker="^", ls="none", color=SPRED, ms=5.5, label="Houses"),
        Line2D([0], [0], color=GREY, ls="--", lw=0.9, label="45° line"),
    ]
    fig.subplots_adjust(bottom=0.20, wspace=0.25)
    fig.legend(handles=handles, ncol=3, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.3)
    return _save(fig, out_dir, "fig_att_policy_rbar_core_vs_att")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    out_dir: Path = args.out_dir if args.out_dir.is_absolute() else (ROOT / args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_policy_inputs()
    for make in (make_rbar_dist, make_takeup, make_salience, make_bound, make_regimes,
                 make_sgrid, make_core_vs_att):
        make(data, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
