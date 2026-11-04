"""Figure 7: timing of the disclosure game under limited buyer attention.

Draws a horizontal timeline of the model's stages:

    0   Nature draws K ~ pi (informed) and theta ~ thetabar (quality), independently
    1   Informed seller observes theta; uninformed seller does not
    2-3 Seller chooses (d, p^list) simultaneously (the strategic moment)
    4   Buyer arrives, sees (d, p^list, X); EPC-sensitive w.p. rho
    4b  Sensitive buyer attends w.p. omega_d (the attention step, teal), with a
        two-branch fork: attentive -> subtracts zeta_theta (rated) or the
        expected cost of the silent pool (silent); inattentive -> zeta^def
    5   Buys or not: trade at p^trans or the listing expires

The figure is purely conceptual: it contains no estimated numbers.

Target: paper, full text width (\\includegraphics[width=\\textwidth]) in
paper-real-estate/sections/04-structural-draft.tex (fig:timing).

Output: paper-real-estate/fig/visuals/model_dynamics.png (300 dpi, 6.5 in wide).

Usage:
    python scripts/make_model_timing_figure.py
"""

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper-real-estate" / "fig" / "visuals" / "model_dynamics.png"

# ---------------------------------------------------------------- style ----
SPRED = "#d01c32"
PINK_BG = "#fbeef0"      # strategic-moment box (SPred tint)
PINK_EDGE = "#ec8f9b"
BBLUE = "#9BC1BC"        # attention step
TEAL_BG = "#eef5f4"      # BBLUE tint
TEAL_DARK = "#4f8a83"    # BBLUE family, dark enough for text and thin rules
INK = "#2b2b2b"
ARROW = "#bdbdbd"

try:
    fm.findfont("Fira Sans", fallback_to_default=False)
    SANS = "Fira Sans"
except ValueError:
    print("Fira Sans not found; falling back to DejaVu Sans "
          "(install: brew install --cask font-fira-sans).")
    SANS = "DejaVu Sans"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [SANS, "DejaVu Sans"],
    "font.size": 8,
    "mathtext.fontset": "custom",
    "mathtext.rm": SANS,
    "mathtext.it": f"{SANS}:italic",
    "mathtext.bf": f"{SANS}:bold",
    "mathtext.fallback": "stixsans",
    "text.color": INK,
    "savefig.dpi": 300,
    "savefig.transparent": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

FS_BODY = 8.0    # stage descriptions
FS_SMALL = 7.5   # fork branches
FS_NODE = 10.0   # numbers inside circles

# --------------------------------------------------------------- layout ----
# The axes span the whole figure and data coordinates equal inches, so every
# size below is the physical size in the paper (included at \textwidth = 6.5 in).
W, H = 6.5, 2.25                  # 2.9 : 1
Y_LINE = 0.80                     # timeline height
R = 0.16                          # node radius
LG = 0.155                        # line pitch (centre to centre) at 8 pt
PAD = 0.13                        # node edge to nearest text line centre

X = {"0": 0.50, "1": 1.55, "2-3": 2.62, "4": 3.70, "4b": 4.62, "5": 5.98}


def lines_at(ax, x, y_first, lines, step, fs=FS_BODY, ha="center", color=INK):
    """Write lines one by one at a fixed pitch so mixed text/math rows stay even.

    y_first is the centre of the first line; step < 0 stacks downward.
    """
    for i, line in enumerate(lines):
        ax.text(x, y_first + i * step, line, ha=ha, va="center_baseline",
                fontsize=fs, color=color)


def node(ax, x, label, dashed=False):
    """Draw one stage circle with its number; dashed teal for the attention step."""
    if dashed:
        ax.add_patch(Circle((x, Y_LINE), R, facecolor=TEAL_BG, edgecolor=TEAL_DARK,
                            linewidth=1.3, linestyle=(0, (3, 1.6)), zorder=3))
        txt_color = TEAL_DARK
    else:
        ax.add_patch(Circle((x, Y_LINE), R, facecolor=SPRED, edgecolor="none", zorder=3))
        txt_color = "white"
    ax.text(x, Y_LINE, label, ha="center", va="center", fontsize=FS_NODE,
            fontweight="bold", color=txt_color, zorder=4)


def main() -> None:
    """Build and save the timing figure."""
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # ---- arrows between consecutive nodes
    keys = list(X)
    for a, b in zip(keys[:-1], keys[1:]):
        ax.add_patch(FancyArrowPatch((X[a] + R + 0.03, Y_LINE), (X[b] - R - 0.03, Y_LINE),
                                     arrowstyle="-|>", mutation_scale=8, color=ARROW,
                                     linewidth=1.0, zorder=1))
    for k in keys:
        node(ax, X[k], k.replace("-", "–"), dashed=(k == "4b"))

    y_up0 = Y_LINE + R + PAD      # centre of the lowest line above the timeline
    y_dn0 = Y_LINE - R - PAD      # centre of the highest line below it

    # ---- stage 0 (above; listed top to bottom, so start at the top line)
    s0 = [r"$\mathbf{Nature}$ draws",
          r"$K\sim\pi$ (informed),",
          r"$\theta\sim\bar{\theta}$ (quality),",
          r"$\mathit{independently}$"]
    lines_at(ax, X["0"], y_up0 + (len(s0) - 1) * LG, s0, -LG)

    # ---- stage 1 (below)
    lines_at(ax, X["1"], y_dn0, [
        r"Informed seller",
        r"observes $\theta$",
        r"$\mathit{Uninformed}$: $\theta$ $\mathit{unknown}$",
    ], -LG)

    # ---- stage 2-3 (above, pink box + red caption)
    bx_w, bx_h = 1.36, 0.42
    bx_y = y_up0 - 0.07
    ax.add_patch(FancyBboxPatch((X["2-3"] - bx_w / 2, bx_y), bx_w, bx_h,
                                boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor=PINK_BG, edgecolor=PINK_EDGE, linewidth=0.8))
    mid = bx_y + bx_h / 2
    lines_at(ax, X["2-3"], mid + LG / 2, [
        r"$\mathbf{Seller}$ chooses $(d,\,p^{\mathrm{list}})$",
        r"$\mathit{simultaneously}$",
    ], -LG)
    ax.text(X["2-3"], bx_y + bx_h + 0.11, "The strategic moment", ha="center",
            va="center_baseline", fontsize=FS_BODY, color=SPRED, fontweight="bold")

    # ---- stage 4 (below)
    lines_at(ax, X["4"], y_dn0, [
        r"$\mathbf{Buyer}$ arrives, sees $(d,\,p^{\mathrm{list}},\,X)$",
        r"EPC-sensitive w.p. $\rho$,",
        r"insensitive w.p. $1-\rho$",
    ], -LG)

    # ---- stage 4b (above, teal box: header + two-branch fork)
    tb_x0, tb_x1 = 3.86, 6.44
    tb_y0 = y_up0 - 0.07
    tb_y1 = H - 0.05
    ax.add_patch(FancyBboxPatch((tb_x0, tb_y0), tb_x1 - tb_x0, tb_y1 - tb_y0,
                                boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor=TEAL_BG, edgecolor=BBLUE, linewidth=0.9))
    ax.plot([X["4b"], X["4b"]], [Y_LINE + R + 0.01, tb_y0], color=TEAL_DARK, lw=0.9,
            ls=(0, (2, 1.5)), zorder=2)

    cx = (tb_x0 + tb_x1) / 2
    lines_at(ax, cx, tb_y1 - 0.14, [
        r"$\mathbf{Sensitive\ buyer}$ attends w.p. $\omega_d$:",
        r"$\omega_1$ if a rating is displayed, $\omega_0\leq\omega_1$ if silent",
    ], -LG)

    # fork: root dot on the left, two branches fanning right
    fy = tb_y0 + 0.35
    dy = 0.185
    fx0 = tb_x0 + 0.13
    fx1 = fx0 + 0.26
    y_hi, y_lo = fy + dy, fy - dy
    ax.plot([fx0], [fy], marker="o", ms=3.2, color=TEAL_DARK, zorder=3)
    for yb in (y_hi, y_lo):
        ax.plot([fx0, fx1], [fy, yb], color=TEAL_DARK, lw=0.9, zorder=2)
    tx = fx1 + 0.06
    # hairline separating the attention probabilities from their consequences
    y_rule = 0.5 * ((tb_y1 - 0.14 - LG) + (fy + dy + 0.065))
    ax.plot([tb_x0 + 0.12, tb_x1 - 0.12], [y_rule, y_rule], color=BBLUE, lw=0.6)
    lines_at(ax, tx, y_hi + 0.065, [
        r"$\mathbf{attentive}$ ($\omega_d$): subtracts $\zeta_\theta$ (rated)",
        r"or expected cost of the silent pool (silent)",
    ], -0.135, fs=FS_SMALL, ha="left")
    lines_at(ax, tx, y_lo, [
        r"$\mathbf{inattentive}$ ($1-\omega_d$): subtracts default "
        r"$\zeta^{\mathrm{def}}$",
    ], -LG, fs=FS_SMALL, ha="left")

    # ---- stage 5 (below)
    lines_at(ax, X["5"], y_dn0, [
        r"$\mathbf{Buys}$ or not:",
        r"trade at $p^{\mathrm{trans}}$",
        r"or listing expires",
    ], -LG)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # No bbox_inches="tight": the canvas is exactly 6.5 in so type prints at its
    # nominal size when included at \textwidth.
    fig.savefig(OUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
