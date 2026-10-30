"""Paper-quality static figures for the limited-attention extension.

Five exhibits, all read from the CSVs written by ``scripts/compute_attention.py``
(``results/attention/``). Nothing is re-estimated here: every number printed on a
figure is read from those files.

  F1 ``fig_att_F1_fit.pdf``         observed vs predicted non-disclosure premium,
                                    core model (beta1 e*) vs extension (c0_fit)
  F2 ``fig_att_F2_ceilings.pdf``    premium vs green premium with the belief
                                    ceiling (Delta = b) and the attention ceiling
                                    (Delta = eta_bar b)
  F3 ``fig_att_F3_contrast.pdf``    forest plot: perceived cost of silence C* in
                                    kWh_ep/m2/yr and the relative-attention
                                    estimators psi_hat
  F5 ``fig_att_F5_hiding_cost.pdf`` per-market hiding cost, core vs extension
  F6 ``fig_att_F6_salience.pdf``    salience counterfactual: premium net of the
                                    attention wedge, and the hiding rate as a
                                    function of relative attention psi

Units: premia and hiding costs in log points (100 x log price differences).
Styling follows ``scripts/make_subsidy_figures.py`` / ``scripts/make_did_figures.py``
(Fira Sans with DejaVu fallback, pdf.fonttype = 42, navy = apartments,
SPred = houses). PDFs go to ``paper/fig/visuals/``; a PNG copy (dpi 200) of each
is written next to it for review.

CLI
---
  python3 scripts/make_attention_figures.py [--out-dir paper/fig/visuals]
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
ATT = ROOT / "results" / "attention"
DEFAULT_OUT = ROOT / "paper" / "fig" / "visuals"

# Palette (shared with make_subsidy_figures.py / make_did_figures.py) --------
SPRED = "#d01c32"
NAVY = "#1D3461"
BBLUE = "#9BC1BC"
INK = "#2b2b2b"
GREY = "#7f7f7f"
LIGHT_GREY = "#bdbdbd"
PALE_ROSE = "#fdecef"
PALE_GREY = "#f2f2f2"
AMBER = "#E8A020"          # flags markets above the attention ceiling

SEGMENTS = [("apartment", "Apt", "APARTMENT"), ("house", "House", "HOUSE")]
SEG_COLORS = {"apartment": NAVY, "house": SPRED}
SEG_LABELS = {"apartment": "Apartments", "house": "Houses"}
SEG_MARKERS = {"apartment": "o", "house": "^"}

CI_Z = 1.96

# Font / rcParams ------------------------------------------------------------
try:
    _found = fm.findfont("Fira Sans", fallback_to_default=False)
    if "FiraSans" not in os.path.basename(_found):
        print("[fonts] Fira Sans not found - falling back to DejaVu Sans.")
except Exception:
    print("[fonts] Fira Sans not found - falling back to DejaVu Sans "
          "(install: brew install --cask font-fira-sans).")

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

BOX = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#dddddd",
           linewidth=0.4, alpha=0.94)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load() -> dict:
    """Read every input once. Returns markets, policy, summary and salience path."""
    data = {
        "summary": pd.read_csv(ATT / "summary.csv", index_col="statistic"),
        "path": pd.read_csv(ATT / "salience_path.csv"),
        "markets": {},
        "policy": {},
    }
    for seg, _, _ in SEGMENTS:
        data["markets"][seg] = pd.read_csv(ATT / f"{seg}_markets.csv")
        data["policy"][seg] = pd.read_csv(ATT / f"{seg}_policy.csv")
    # Consistency checks against the summary (fail loudly on drift, never patch).
    s = data["summary"]
    for seg, col, _ in SEGMENTS:
        m, p = data["markets"][seg], data["policy"][seg]
        assert len(m) == len(p) == int(s.loc["n_markets", col]), f"{seg}: market count drift"
        assert int((m["slack"] < 0).sum()) == int(s.loc["n_viol", col]), f"{seg}: n_viol drift"
        assert np.isclose(p["c0_fit"].mean(), s.loc["c0_fit_mean", col]), f"{seg}: c0_fit drift"
        assert np.isclose(p["c0_core"].mean(), s.loc["c0_core_mean", col]), f"{seg}: c0_core drift"
        assert np.isclose(m["dl"].mean(), s.loc["dl", col]), f"{seg}: dl drift"
    return data


def fmt(x: float, nd: int = 1) -> str:
    """Fixed-decimal formatting that never prints a signed zero."""
    out = f"{x:.{nd}f}"
    return out[1:] if re.fullmatch(r"-0\.?0*", out) else out


def _save(fig: plt.Figure, out_dir: Path, name: str) -> Path:
    pdf = out_dir / f"{name}.pdf"
    fig.savefig(pdf)
    fig.savefig(out_dir / f"{name}.png", dpi=200)
    plt.close(fig)
    print(f"[saved] {pdf.relative_to(ROOT)} (+ .png)")
    return pdf


# ---------------------------------------------------------------------------
# F1 - fit to the non-disclosure premium, core vs extension
# ---------------------------------------------------------------------------

def make_f1(data: dict, out_dir: Path) -> Path:
    s = data["summary"]
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.3))
    for ax, (seg, col, _) in zip(axes, SEGMENTS):
        p = data["policy"][seg]
        c = SEG_COLORS[seg]
        x_core, x_ext, y = p["c0_core"], p["c0_fit"], p["dl"]

        lo = float(min(x_core.min(), x_ext.min(), y.min()))
        hi = float(max(x_core.max(), x_ext.max(), y.max()))
        pad = 0.05 * (hi - lo)
        xlo = min(0.0, float(min(x_core.min(), x_ext.min()))) - pad
        xhi = float(max(x_core.max(), x_ext.max())) + pad
        # Extra head-room below the data for the fit-statistics box, so it never
        # hides a market.
        yhi = float(y.max()) + pad
        ylo = float(y.min()) - pad - 0.30 * (yhi - float(y.min()))

        ax.axhline(0, color="#cccccc", lw=0.6, zorder=1)
        ax.axvline(0, color="#cccccc", lw=0.6, zorder=1)
        d = np.array([min(xlo, ylo), max(xhi, yhi)])
        ax.plot(d, d, color=GREY, ls="--", lw=0.9, zorder=2)
        # Same market: core -> extension prediction at the same observed premium.
        ax.hlines(y, x_core, x_ext, color=c, alpha=0.18, lw=0.6, zorder=2)
        ax.scatter(x_core, y, s=20, facecolor="white", edgecolor=c, lw=0.9,
                   marker=SEG_MARKERS[seg], zorder=3)
        ax.scatter(x_ext, y, s=20, facecolor=c, edgecolor="white", lw=0.4,
                   marker=SEG_MARKERS[seg], alpha=0.9, zorder=4)

        ax.set_xlim(xlo, xhi)
        ax.set_ylim(ylo, yhi)
        ax.set_title(f"{SEG_LABELS[seg]} (N = {int(s.loc['n_markets', col])})",
                     fontsize=10.5, color=INK)
        ax.set_xlabel(r"Predicted premium $\hat\Delta_m$ (log points)")

        txt = (f"{'':<10}mean resid.   RMSE   corr.\n"
               f"{'Core':<10}{fmt(s.loc['resid_core', col]):>11}"
               f"{fmt(s.loc['rmse_core', col]):>7}{fmt(s.loc['corr_core', col], 2):>7}\n"
               f"{'Extension':<10}{fmt(s.loc['resid_ext', col]):>11}"
               f"{fmt(s.loc['rmse_ext', col]):>7}{fmt(s.loc['corr_ext', col], 2):>7}\n"
               "(extension mean residual zero by construction)")
        ax.text(0.97, 0.025, txt, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=7.2, family="monospace", color=INK, bbox=BOX, zorder=6)

    axes[0].set_ylabel(r"Observed premium $\hat\Delta_m$ (log points)")
    handles = [
        Line2D([0], [0], marker="o", ls="none", mfc="white", mec=INK, mew=0.9, ms=5.5,
               label=r"Core model: $\hat\beta_{1}\hat e^{*}$"),
        Line2D([0], [0], marker="o", ls="none", mfc=INK, mec="white", ms=5.5,
               label=r"Extension: $\hat\beta_{1}[\hat\psi\hat e^{*}+(1-\hat\psi)\eta]$"),
        Line2D([0], [0], color=GREY, alpha=0.6, lw=0.8, label="Same market"),
        Line2D([0], [0], color=GREY, ls="--", lw=0.9, label="Observed = predicted"),
    ]
    fig.subplots_adjust(bottom=0.24, wspace=0.22)
    fig.legend(handles=handles, ncol=4, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.3)
    return _save(fig, out_dir, "fig_att_F1_fit")


# ---------------------------------------------------------------------------
# F2 - belief and attention ceilings
# ---------------------------------------------------------------------------

def make_f2(data: dict, out_dir: Path, belief_only: bool = False) -> Path:
    """Non-disclosure premium against the energy-efficiency premium, by market.

    ``belief_only=True`` writes the core-model exhibit (Figure 10, shown before the
    attention extension): the only ceiling drawn is Delta = beta1, and every element
    is labelled in words directly on the panel (no legend, no symbol ``b``).
    ``belief_only=False`` writes the full version with the attention ceilings.
    """
    s = data["summary"]
    if belief_only:
        dark_red = "#8A0020"
        fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.2))
        fig.subplots_adjust(wspace=0.22)
        for ax, (seg, col, _) in zip(axes, SEGMENTS):
            m = data["markets"][seg]
            c, mk = SEG_COLORS[seg], SEG_MARKERS[seg]
            above = (m["dl"] > m["b1"]).to_numpy()     # strictly above the core ceiling
            n_above, n_tot = int(above.sum()), len(m)
            assert n_above == int(s.loc["n_d_gt_b", col]), f"{seg}: n_d_gt_b drift"
            assert n_tot == int(s.loc["n_markets", col]), f"{seg}: n_markets drift"

            xhi = float(m["b1"].max()) * 1.06
            d_lo, d_hi = float(m["dl"].min()), float(m["dl"].max())
            yhi = d_hi + 0.06 * (d_hi - d_lo)
            ylo = d_lo - 0.22 * (d_hi - d_lo)
            xs = np.array([0.0, xhi])
            ax.set_xlim(0, xhi)
            ax.set_ylim(ylo, yhi)

            ax.fill_between(xs, xs, [yhi, yhi], color=PALE_ROSE, lw=0, zorder=0)
            ax.axhline(0, color="#cccccc", lw=0.6, zorder=1)
            ax.plot(xs, xs, color=INK, lw=1.0, zorder=2)

            # Above the ceiling: filled in the segment colour. On/below: hollow, lighter.
            ax.scatter(m.loc[~above, "b1"], m.loc[~above, "dl"], s=20, marker=mk,
                       facecolor="white", edgecolor=c, lw=0.8, alpha=0.55, zorder=3)
            ax.scatter(m.loc[above, "b1"], m.loc[above, "dl"], s=22, marker=mk,
                       facecolor=c, edgecolor="white", lw=0.4, zorder=4)

            # Region label, top-left of the rose area.
            ax.text(0.03, 0.97, "Core model cannot\nproduce a premium here",
                    transform=ax.transAxes, ha="left", va="top", fontsize=8.6,
                    color=dark_red, linespacing=1.15, zorder=6)

            # Failure count, lower-right (head-room reserved below the lowest market).
            ax.text(0.97, 0.03,
                    f"{n_above} of {n_tot} markets ({100 * n_above / n_tot:.0f}%)\n"
                    "lie above the ceiling",
                    transform=ax.transAxes, ha="right", va="bottom", fontsize=8.2,
                    color=INK, bbox=BOX, linespacing=1.2, zorder=6)

            # Ceiling label: horizontal text joined to the line by a short leader (the
            # markets leave no collision-free stretch for a rotated label). A grid
            # search over the panel picks the shortest leader whose label box and
            # leader keep clear of every market, both panel labels and the line.
            fig.canvas.draw()
            rdr = fig.canvas.get_renderer()
            pt = fig.dpi / 72.0                                   # display px per point
            p0, p1 = ax.transData.transform([(0, 0), (xhi, xhi)])
            u = (p1 - p0) / np.hypot(*(p1 - p0))
            nrm = np.array([-u[1], u[0]])                         # unit normal, above line
            pts = ax.transData.transform(m[["b1", "dl"]].to_numpy())
            r_mk = 0.5 * np.sqrt(22.0) * pt                       # marker radius
            frame = ax.get_window_extent(rdr)
            keep_out = [tx.get_window_extent(rdr).padded(3 * pt) for tx in ax.texts]

            def _seg_dist(q, a_, b_):
                v = b_ - a_
                s_ = np.clip(((q - a_) @ v) / (v @ v), 0.0, 1.0)
                return np.hypot(*(q - (a_ + s_[:, None] * v)).T)

            best = None
            for k, lab in enumerate((r"Core-model ceiling: $\hat\Delta = \hat\beta_{1}$",
                                     "Core-model ceiling:\n" r"$\hat\Delta = \hat\beta_{1}$")):
                probe = ax.text(0, 0, lab, fontsize=8.2, linespacing=1.15)
                ext = probe.get_window_extent(rdr)
                w, h = ext.width + 2 * pt, ext.height + 2 * pt
                probe.remove()
                for gx in np.linspace(frame.x0 + 2 * pt, frame.x1 - w - 2 * pt, 70):
                    for gy in np.linspace(frame.y0 + 2 * pt, frame.y1 - h - 2 * pt, 50):
                        corners = np.array([[gx, gy], [gx + w, gy], [gx, gy + h],
                                            [gx + w, gy + h]])
                        sd = (corners - p0) @ nrm
                        if not (np.all(sd > 0) or np.all(sd < 0)):
                            continue                              # box straddles the line
                        i = int(np.argmin(np.abs(sd)))
                        if not 5 * pt <= abs(sd[i]) <= 32 * pt:
                            continue                              # leader too short / long
                        if any(ko.overlaps(mpl.transforms.Bbox.from_extents(
                                gx, gy, gx + w, gy + h)) for ko in keep_out):
                            continue
                        dx = np.maximum.reduce([gx - pts[:, 0], 0 * pts[:, 0],
                                                pts[:, 0] - gx - w])
                        dy = np.maximum.reduce([gy - pts[:, 1], 0 * pts[:, 1],
                                                pts[:, 1] - gy - h])
                        if np.hypot(dx, dy).min() < r_mk + 6 * pt:
                            continue                              # box too close to a market
                        foot = corners[i] - sd[i] * nrm
                        if _seg_dist(pts, corners[i], foot).min() < r_mk + 2 * pt:
                            continue                              # leader crosses a market
                        score = abs(sd[i]) + 40 * pt * k          # strongly prefer one line
                        if best is None or score < best[0]:
                            best = (score, lab, corners, i, foot, abs(sd[i]))
            assert best is not None, f"{seg}: no clear position for the ceiling label"
            _, lab, corners, i, foot, lead = best
            inv = ax.transData.inverted()
            tx0, ty0 = inv.transform(corners[0] + pt)             # undo the 1 pt box pad
            ax.text(tx0, ty0, lab, ha="left", va="bottom", fontsize=8.2,
                    linespacing=1.15, color=INK, zorder=6)
            (lx0, ly0), (lx1, ly1) = inv.transform(np.vstack([corners[i], foot]))
            ax.plot([lx0, lx1], [ly0, ly1], color=INK, lw=0.6, zorder=5,
                    solid_capstyle="butt")
            side = "above" if ((corners[0] - p0) @ nrm) > 0 else "below"
            print(f"[F2a] {seg}: ceiling label {side} the line, leader "
                  f"{lead / pt:.0f} pt, {lab.count(chr(10)) + 1} line(s); {n_above}/{n_tot} above")

            ax.set_title(f"{SEG_LABELS[seg]} (N = {n_tot})", fontsize=10.5, color=INK)
            ax.set_xlabel(r"Energy-efficiency premium $\hat\beta_{1,m}$ (log points)")
        axes[0].set_ylabel(r"Non-disclosure premium $\hat\Delta_m$ (log points)")
        return _save(fig, out_dir, "fig_att_F2a_belief")

    # 0.2 in taller than before with the axes height held at ~2.6 in, so the extra
    # height all goes into white space between the x-axis label and the legend.
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.5))
    for ax, (seg, col, _) in zip(axes, SEGMENTS):
        m = data["markets"][seg]
        eta_bar = float(s.loc["eta_w", col])
        n_viol = int(s.loc["n_viol", col])
        n_above_belief = int(s.loc["n_d_gt_b", col])
        viol = m["slack"] < 0   # Delta_m > eta_m b_m, market-specific eta_m

        xhi = float(m["b1"].max()) * 1.06
        # Crop to the data (the attention ray may exit through the top) and leave
        # head-room below the lowest market for the count box.
        d_lo, d_hi = float(m["dl"].min()), float(m["dl"].max())
        yhi = d_hi + 0.06 * (d_hi - d_lo)
        ylo = d_lo - 0.22 * (d_hi - d_lo)
        xs = np.array([0.0, xhi])

        ax.fill_between(xs, xs, [yhi, yhi], color=PALE_ROSE, lw=0, zorder=0)
        # Range of market-specific attention ceilings eta_m b (thin fan).
        ax.fill_between(xs, m["eta"].min() * xs, m["eta"].max() * xs,
                        color=LIGHT_GREY, alpha=0.35, lw=0, zorder=1)
        ax.plot(xs, xs, color=INK, lw=1.0, zorder=2)
        ax.plot(xs, eta_bar * xs, color=INK, lw=1.0, ls=(0, (4, 2)), zorder=2)
        ax.axhline(0, color="#cccccc", lw=0.6, zorder=1)

        c = SEG_COLORS[seg]
        ax.scatter(m.loc[~viol, "b1"], m.loc[~viol, "dl"], s=20, color=c,
                   marker=SEG_MARKERS[seg], edgecolor="white", lw=0.4, alpha=0.85, zorder=3)
        ax.scatter(m.loc[viol, "b1"], m.loc[viol, "dl"], s=26, color=AMBER,
                   marker="D", edgecolor=INK, lw=0.5, zorder=4)

        # Ray labels: belief ray at the right edge (above the line, in the rose
        # region, clear of the markets below it); attention ray where it is at
        # ~80% of the frame height.
        ax.text(xhi * 0.985, xhi * 0.985 + 0.015 * (yhi - ylo), r"$\Delta = b$",
                ha="right", va="bottom", fontsize=8, color=INK)
        x_lab = min(0.70 * xhi, 0.80 * yhi / eta_bar)
        ax.text(x_lab - 0.01 * xhi, eta_bar * x_lab + 0.015 * (yhi - ylo),
                rf"$\Delta = \bar\eta\, b$  ($\bar\eta$ = {eta_bar:.2f})",
                ha="right", va="bottom", fontsize=8, color=INK)

        ax.set_xlim(0, xhi)
        ax.set_ylim(ylo, yhi)
        ax.set_title(f"{SEG_LABELS[seg]} (N = {len(m)})", fontsize=10.5, color=INK)
        ax.set_xlabel(r"Energy-efficiency premium $\hat b_m$ (log points)")
        box = (f"above belief ceiling: {n_above_belief} of {len(m)}\n"
               f"above own attention ceiling: {n_viol} of {len(m)}")
        ax.text(0.97, 0.03, box,
                transform=ax.transAxes, ha="right", va="bottom", fontsize=7.8,
                color=INK, bbox=BOX, zorder=6)

    axes[0].set_ylabel(r"Non-disclosure premium $\hat\Delta_m$ (log points)")
    handles = [
        Line2D([0], [0], color=INK, lw=1.0, label=r"Belief ceiling $\Delta = b$"),
        Line2D([0], [0], color=INK, lw=1.0, ls=(0, (4, 2)),
               label=r"Attention ceiling $\Delta = \bar\eta\,b$ (b-weighted)"),
        Patch(facecolor=LIGHT_GREY, alpha=0.5, label=r"Range of market $\eta_m b$"),
        Patch(facecolor=PALE_ROSE, edgecolor="#e6c8ce", lw=0.4,
              label="Not explainable by any belief"),
        Line2D([0], [0], marker="D", ls="none", mfc=AMBER, mec=INK, mew=0.5, ms=5,
               label=r"Market above its own ceiling ($\hat\Delta_m > \eta_m \hat b_m$)"),
    ]
    fig.subplots_adjust(bottom=0.30, wspace=0.22)
    fig.legend(handles=handles, ncol=3, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.2)
    return _save(fig, out_dir, "fig_att_F2_ceilings")


# ---------------------------------------------------------------------------
# F3 - segment contrast in physical units
# ---------------------------------------------------------------------------

def _gband_label(key: str) -> str:
    """'psi_Gfourtwenty' -> 'G-band midpoint 420 kWh' (the tag encodes the midpoint)."""
    words = {"fourtwenty": "420", "sixhundred": "600"}
    tag = key.split("_G", 1)[1]
    return f"G-band midpoint {words[tag]}"


def make_f3(data: dict, out_dir: Path) -> Path:
    s = data["summary"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.0),
                                   gridspec_kw={"width_ratios": [1.0, 1.15]})
    off = {"apartment": +0.14, "house": -0.14}

    # (a) C* in kWh_ep/m2/yr --------------------------------------------------
    rows_a = ["Perceived cost of silence $C^{*}$"]
    for seg, col, _ in SEGMENTS:
        c = SEG_COLORS[seg]
        y0 = 0 + off[seg]
        est, lo, hi = (s.loc[k, col] for k in ("c_star_kwh", "c_star_lo", "c_star_hi"))
        ax1.errorbar(est, y0, xerr=[[est - lo], [hi - est]], fmt=SEG_MARKERS[seg],
                     color=c, ms=6, capsize=3, lw=1.4, zorder=3)
        above = seg == "apartment"            # apartments label above, houses below
        ax1.text(est, y0 + (0.10 if above else -0.10), f"{est:.0f} [{lo:.0f}, {hi:.0f}]",
                 ha="center", va="bottom" if above else "top", fontsize=7.6, color=c)
        csil = s.loc["c_sil_kwh", col]
        ax1.scatter(csil, -1 + off[seg], marker=SEG_MARKERS[seg], s=34, facecolor="white",
                    edgecolor=c, lw=1.2, zorder=3)
        ax1.text(csil + 12, -1 + off[seg], f"{csil:.0f}", ha="left", va="center",
                 fontsize=7.6, color=c)
    rows_a.append(r"Rational silent-pool cost $\bar C^{\rm sil}$")
    ax1.axvline(0, color=GREY, ls="--", lw=0.8)
    ax1.set_yticks([0, -1])
    ax1.set_yticklabels(rows_a)
    ax1.set_ylim(-1.6, 0.6)
    ax1.set_xlim(-60, 310)
    ax1.grid(axis="y", visible=False)
    ax1.set_xlabel(r"kWh$_{\rm ep}$/m$^2$/yr")
    ax1.set_title("Cost of silence", fontsize=10.5, color=INK, loc="left")

    # (b) psi estimators ------------------------------------------------------
    est_rows = [
        ("Ratio of sums (95% bootstrap CI)", "psi", ("psi_lo", "psi_hi")),
        ("Regression through origin (±1.96 s.e.)", "psi_ols", "psi_ols_se"),
        ("Median of market ratios", "psi_med", None),
        ("Regression with constant", "psi_const", None),
        (_gband_label("psi_Gfourtwenty"), "psi_Gfourtwenty", None),
        (_gband_label("psi_Gsixhundred"), "psi_Gsixhundred", None),
    ]
    ax2.axvspan(0, 1, color=PALE_GREY, zorder=0, lw=0)
    ax2.text(0.5, 0.55, "admissible range [0, 1]", ha="center", va="bottom",
             fontsize=7.6, color=GREY)
    for i, (label, key, ci) in enumerate(est_rows):
        yi = -i
        for seg, col, _ in SEGMENTS:
            c = SEG_COLORS[seg]
            v = s.loc[key, col]
            if isinstance(ci, tuple):
                err = [[v - s.loc[ci[0], col]], [s.loc[ci[1], col] - v]]
            elif isinstance(ci, str):
                err = [[CI_Z * s.loc[ci, col]], [CI_Z * s.loc[ci, col]]]
            else:
                err = None
            ax2.errorbar(v, yi + off[seg], xerr=err, fmt=SEG_MARKERS[seg], color=c,
                         ms=5.5, capsize=2.5 if err else 0, lw=1.3, zorder=3,
                         mfc=c if i < 4 else "white", mec=c)
    ax2.axhline(-3.5, color="#dddddd", lw=0.6)
    ax2.set_yticks([-i for i in range(len(est_rows))])
    ax2.set_yticklabels([r[0] for r in est_rows], fontsize=8.5)
    ax2.set_ylim(-len(est_rows) + 0.4, 0.9)
    ax2.grid(axis="y", visible=False)
    ax2.set_xlabel(r"Relative attention $\hat\psi$")
    ax2.set_title(r"Relative attention $\hat\psi$", fontsize=10.5, color=INK, loc="left")

    handles = [
        Line2D([0], [0], marker="o", ls="none", color=NAVY, ms=5.5, label="Apartments"),
        Line2D([0], [0], marker="^", ls="none", color=SPRED, ms=5.5, label="Houses"),
        Line2D([0], [0], marker="o", ls="none", mfc="white", mec=INK, ms=5.5,
               label="Hollow: G-band sensitivity of the ratio of sums"),
    ]
    fig.subplots_adjust(left=0.19, bottom=0.24, wspace=0.95)
    fig.legend(handles=handles, ncol=3, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.3)
    return _save(fig, out_dir, "fig_att_F3_contrast")


# ---------------------------------------------------------------------------
# F5 - hiding cost by market, core vs extension
# ---------------------------------------------------------------------------

def make_f5(data: dict, out_dir: Path) -> Path:
    s = data["summary"]
    n = {seg: len(data["policy"][seg]) for seg, _, _ in SEGMENTS}
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.3), sharey=True,
                             gridspec_kw={"width_ratios": [n["apartment"] + 12, n["house"] + 12]})
    for ax, (seg, col, _) in zip(axes, SEGMENTS):
        p = data["policy"][seg].sort_values("c0_fit").reset_index(drop=True)
        c = SEG_COLORS[seg]
        r = np.arange(1, len(p) + 1)
        ax.scatter(r, p["c0_raw"], marker="_", s=22, color=GREY, lw=0.9, zorder=2)
        ax.vlines(r, p["c0_core"], p["c0_fit"], color=c, alpha=0.45, lw=0.9, zorder=3)
        ax.scatter(r, p["c0_core"], s=14, facecolor="white", edgecolor=c, lw=0.8,
                   marker=SEG_MARKERS[seg], zorder=4)
        ax.scatter(r, p["c0_fit"], s=14, facecolor=c, edgecolor="none",
                   marker=SEG_MARKERS[seg], zorder=5)
        m_core, m_fit = s.loc["c0_core_mean", col], s.loc["c0_fit_mean", col]
        ax.axhline(m_core, color=c, ls=":", lw=1.0, zorder=1)
        ax.axhline(m_fit, color=c, ls="--", lw=1.0, zorder=1)
        ax.axhline(0, color="#cccccc", lw=0.6, zorder=1)
        ax.text(0.03, 0.97, f"segment mean: core {fmt(m_core)} → extension {fmt(m_fit)}",
                transform=ax.transAxes, ha="left", va="top", fontsize=8, color=INK,
                bbox=BOX, zorder=6)
        ax.set_xlim(0, len(p) + 1)
        ax.set_title(f"{SEG_LABELS[seg]} (N = {len(p)})", fontsize=10.5, color=INK)
        ax.set_xlabel(r"Market rank by extension hiding cost $\hat c_{0,m}$")
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel(r"Hiding cost $\hat c_{0,m}$ (log points)")
    handles = [
        Line2D([0], [0], marker="o", ls="none", mfc="white", mec=INK, mew=0.8, ms=5,
               label=r"Core: $\hat\beta_1\hat e^{*}$"),
        Line2D([0], [0], marker="o", ls="none", mfc=INK, mec="none", ms=5,
               label=r"Extension: $\hat\beta_1[\hat\psi\hat e^{*}+(1-\hat\psi)\eta]$"),
        Line2D([0], [0], marker="_", ls="none", color=GREY, ms=8, mew=1.0,
               label=r"Observed premium $\hat\Delta_m$"),
        Line2D([0], [0], color=INK, ls=":", lw=1.0, label="Core mean"),
        Line2D([0], [0], color=INK, ls="--", lw=1.0, label="Extension mean"),
    ]
    fig.subplots_adjust(bottom=0.24, wspace=0.06)
    fig.legend(handles=handles, ncol=5, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0), fontsize=8.3)
    return _save(fig, out_dir, "fig_att_F5_hiding_cost")


# ---------------------------------------------------------------------------
# F6 - salience counterfactual
# ---------------------------------------------------------------------------

def make_f6(data: dict, out_dir: Path) -> Path:
    s, path = data["summary"], data["path"]
    fig = plt.figure(figsize=(9.5, 6.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[0.8, 1.0, 1.0], height_ratios=[1.0, 1.0],
                          hspace=0.50, wspace=0.38)
    ax_i = fig.add_subplot(gs[:, 0])
    ax_ii = fig.add_subplot(gs[0, 1:])
    ax_za = fig.add_subplot(gs[1, 1])
    ax_zh = fig.add_subplot(gs[1, 2])

    # (i) observed premium vs premium without the attention wedge -------------
    for k, (seg, col, _) in enumerate(SEGMENTS):
        c = SEG_COLORS[seg]
        obs = float(data["markets"][seg]["dl"].mean())
        lam = float(s.loc["lam", col])
        net = obs - lam
        ax_i.plot([k, k], [net, obs], color=c, lw=1.6, alpha=0.6, zorder=2)
        ax_i.annotate("", xy=(k, net), xytext=(k, obs),
                      arrowprops=dict(arrowstyle="-|>", color=c, lw=1.2), zorder=2)
        ax_i.scatter(k, obs, s=46, color=c, marker=SEG_MARKERS[seg], zorder=3)
        ax_i.scatter(k, net, s=46, facecolor="white", edgecolor=c, lw=1.2,
                     marker=SEG_MARKERS[seg], zorder=3)
        ax_i.text(k + 0.12, obs, f"{fmt(obs)}", va="center", ha="left", fontsize=8, color=c)
        ax_i.text(k + 0.12, net, f"{fmt(net)}", va="center", ha="left", fontsize=8, color=c)
        ax_i.text(k - 0.12, (obs + net) / 2, rf"$-\hat\lambda$ = {fmt(lam)}",
                  va="center", ha="right", fontsize=7.6, color=GREY)
    ax_i.set_xticks([0, 1])
    ax_i.set_xticklabels([SEG_LABELS[seg] for seg, _, _ in SEGMENTS])
    ax_i.set_xlim(-0.75, 1.6)
    ax_i.set_ylim(0, None)
    ax_i.grid(axis="x", visible=False)
    ax_i.set_ylabel(r"Mean non-disclosure premium (log points)")
    ax_i.set_title("(i) Premium at fixed hiding rates", fontsize=10, color=INK, loc="left")
    ax_i.legend(handles=[
        Line2D([0], [0], marker="o", ls="none", color=INK, ms=6, label=r"Observed $\hat\Delta$"),
        Line2D([0], [0], marker="o", ls="none", mfc="white", mec=INK, ms=6,
               label="Full salience\n" + r"$\hat\Delta-\hat\lambda$"),
    ], loc="center right", bbox_to_anchor=(1.02, 0.70), frameon=False, fontsize=7.8)

    # (ii) hiding rate vs psi, full range ---------------------------------------
    def draw(ax, seg, col, key, lo=None, hi=None, markers=False):
        d = path[path["segment"] == key]
        if lo is not None:
            d = d[(d["psi"] >= lo) & (d["psi"] <= hi)]
        c = SEG_COLORS[seg]
        ax.plot(d["psi"], 100 * d["mean_sigma0"], color=c, lw=1.4 if not markers else 0.8,
                marker="." if markers else None, ms=3.2, zorder=3,
                ls="-" if seg == "apartment" else (0, (5, 1.5)))
        psi_hat = float(s.loc["psi", col])
        ax.axvline(psi_hat, color=c, lw=0.8, ls=":", zorder=2)
        ax.scatter(psi_hat, float(s.loc["sigma0_obs_mean", col]), s=48, marker=SEG_MARKERS[seg],
                   facecolor="white", edgecolor=c, lw=1.4, zorder=5)
        return psi_hat

    for seg, col, key in SEGMENTS:
        c = SEG_COLORS[seg]
        ax_ii.axvspan(max(float(s.loc["psi_lo", col]), -0.02), min(float(s.loc["psi_hi", col]), 1.05),
                      color=c, alpha=0.07, lw=0, zorder=0)
        draw(ax_ii, seg, col, key)
    ax_ii.set_xlim(-0.02, 1.02)
    ax_ii.set_ylim(-4, 104)
    ax_ii.set_xlabel(r"Relative attention $\psi$")
    ax_ii.set_ylabel(r"Mean hiding rate $\sigma_0$ (%)")
    ax_ii.set_title(r"(ii) Hiding rate as a function of relative attention", fontsize=10,
                    color=INK, loc="left")
    ax_ii.text(0.60, 0.20, "knife-edge: single hiding cost per market",
               transform=ax_ii.transAxes, ha="center", va="center", fontsize=8.2,
               color=INK, style="italic", bbox=BOX)
    ax_ii.legend(handles=[
        Line2D([0], [0], color=NAVY, lw=1.4, label="Apartments"),
        Line2D([0], [0], color=SPRED, lw=1.4, ls=(0, (5, 1.5)), label="Houses"),
        Line2D([0], [0], color=INK, lw=0.8, ls=":", label=r"$\hat\psi$"),
        Patch(facecolor=INK, alpha=0.12, label=r"95% CI of $\hat\psi$"),
        Line2D([0], [0], marker="o", ls="none", mfc="white", mec=INK, ms=6,
               label="Observed mean hiding rate"),
    ], loc="center", frameon=False, fontsize=7.6, bbox_to_anchor=(0.60, 0.60))

    # Zoom panels: psi_hat +/- 0.05 (apartments) and the house cliff --------------
    for ax, (seg, col, key), half in ((ax_za, SEGMENTS[0], 0.05), (ax_zh, SEGMENTS[1], 0.12)):
        psi_hat = float(s.loc["psi", col])
        lo, hi = psi_hat - half, min(psi_hat + half, 1.0)
        draw(ax, seg, col, key, lo, hi, markers=True)
        ax.set_xlim(lo, hi)
        ax.set_ylim(-4, 104)
        ax.set_xlabel(r"Relative attention $\psi$")
        ax.set_title(f"Zoom: {SEG_LABELS[seg].lower()}, " + r"$\hat\psi$" + f" = {psi_hat:.2f}",
                     fontsize=9.5, color=INK, loc="left")
        ax.text(0.98, 0.95, f"observed: {fmt(float(s.loc['sigma0_obs_mean', col]))}%",
                transform=ax.transAxes, ha="right", va="top", fontsize=7.6,
                color=SEG_COLORS[seg])
    ax_za.set_ylabel(r"Mean hiding rate $\sigma_0$ (%)")
    return _save(fig, out_dir, "fig_att_F6_salience")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load()
    for make in (make_f1, make_f2, make_f3, make_f5, make_f6):
        make(data, out_dir)
    make_f2(data, out_dir, belief_only=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
