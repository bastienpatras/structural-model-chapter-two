"""Figure 1: equilibrium-outcome taxonomy of the disclosure game.

Draws the 2x2 table of equilibrium outcomes by seller information (pi = 1 vs
pi < 1, columns) and buyer sensitivity to energy efficiency (rho = 0 vs rho = 1,
rows). The bottom-right "Sustained Premium" cell is split by buyer attention to
silent listings (psi = 1 vs psi < 1).

The figure is purely conceptual: it contains no estimated numbers.

Target: paper, full text width (\\includegraphics[width=\\textwidth]) in
paper-real-estate/sections/02-unraveling-draft.tex (fig:equilibrium_outcomes).

Output: paper-real-estate/fig/visuals/equilibirum_outcomes.png (300 dpi).
The misspelled filename is intentional: it is the path the .tex references.

Usage:
    python scripts/make_equilibrium_outcomes_figure.py
"""

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper-real-estate" / "fig" / "visuals" / "equilibirum_outcomes.png"

# ---------------------------------------------------------------- style ----
SPRED = "#d01c32"
INK = "#2b2b2b"          # body text and rules
INK_SOFT = "#6b6b6b"     # small notes

BLUE_BG, BLUE_TXT = "#d9e9f3", "#4a9cc0"     # "Disclosure Irrelevant"
GREEN_BG, GREEN_TXT = "#d3ecd2", "#2a9a2a"   # "Full Unraveling"
PINK_A = "#f9dde1"       # Sustained Premium, psi = 1 (and title band)
PINK_B = "#f2c4cb"       # Sustained Premium, psi < 1 (same family, deeper)

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
    "font.size": 9,
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

FS_HEAD = 8.2    # column / row headers
FS_TITLE = 8.5   # cell titles
FS_BODY = 8.0    # cell body
FS_SUBHEAD = 7.8 # sub-cell headers
FS_SUB = 7.5     # sub-cell body
FS_NOTE = 6.7    # "e.g." notes
FS_TAG = 8.0     # "GM dep. 2"

# --------------------------------------------------------------- layout ----
# Everything is laid out in inches: the axes span the whole figure and its
# data coordinates equal inches, so sizes below are physical sizes in the paper.
X0, X1, X2, X3 = 0.0, 1.62, 3.74, 6.50   # label col | pi = 1 | pi < 1
H_HEAD, H_ROW1 = 0.48, 0.58
H_BAND, H_SUB = 0.23, 0.69               # bottom row: title band + 2 sub-cells
H_ROW2 = H_BAND + 2 * H_SUB
W, H = X3, H_HEAD + H_ROW1 + H_ROW2

Y_TOP = H
Y_HEAD_BOT = H - H_HEAD
Y_ROW1_BOT = Y_HEAD_BOT - H_ROW1
Y_ROW2_BOT = Y_ROW1_BOT - H_ROW2
Y_BAND_BOT = Y_ROW1_BOT - H_BAND
Y_SPLIT = Y_BAND_BOT - H_SUB



def lines_at(ax, xc, yc, items, gap=1.38):
    """Stack text lines centred on (xc, yc).

    items: list of (text, fontsize, color, weight, style). Line pitch is
    gap x fontsize (pt), converted to inches.
    """
    pitches = [gap * fs / 72 for (_, fs, *_r) in items]
    total = sum(pitches)
    y = yc + total / 2
    arts = []
    for (txt, fs, col, wt, st), p in zip(items, pitches):
        y -= p / 2
        arts.append(ax.text(xc, y, txt, fontsize=fs, color=col, weight=wt,
                            style=st, ha="center", va="center"))
        y -= p / 2
    return arts


fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# Cell fills.
fills = [
    (X1, Y_ROW1_BOT, X2 - X1, H_ROW1, BLUE_BG),
    (X2, Y_ROW1_BOT, X3 - X2, H_ROW1, BLUE_BG),
    (X1, Y_ROW2_BOT, X2 - X1, H_ROW2, GREEN_BG),
    (X2, Y_BAND_BOT, X3 - X2, H_BAND, PINK_A),
    (X2, Y_SPLIT, X3 - X2, H_SUB, PINK_A),
    (X2, Y_ROW2_BOT, X3 - X2, H_SUB, PINK_B),
]
for x, y, w, h, c in fills:
    ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor="none", zorder=0))

# Rules: horizontal under the header and between the rows; vertical at the
# column boundaries (as in the original table).
rule = dict(color=INK, linewidth=0.8, solid_capstyle="butt", zorder=2)
ax.plot([X0 + 0.04, X3], [Y_HEAD_BOT, Y_HEAD_BOT], **rule)
ax.plot([X0 + 0.04, X3], [Y_ROW1_BOT, Y_ROW1_BOT], **rule)
ax.plot([X1, X1], [Y_ROW2_BOT, Y_TOP - 0.03], **rule)
ax.plot([X2, X2], [Y_ROW2_BOT, Y_TOP - 0.03], **rule)

# Thin white separators inside the split cell: they keep it one cell.
sep = dict(color="white", linewidth=1.2, zorder=1)
ax.plot([X2, X3], [Y_BAND_BOT, Y_BAND_BOT], **sep)
ax.plot([X2, X3], [Y_SPLIT, Y_SPLIT], **sep)

texts = []  # (artist, (xmin, ymin, xmax, ymax) of its containing cell)

# Column headers.
cx1, cx2 = (X1 + X2) / 2, (X2 + X3) / 2
yh = (Y_TOP + Y_HEAD_BOT) / 2
for a in lines_at(ax, cx1, yh, [
        (r"Fully informed sellers ($\pi = 1$)", FS_HEAD, INK, "normal", "normal"),
        ("GM dep. 2", FS_TAG, SPRED, "normal", "normal")]):
    texts.append((a, (X1, Y_HEAD_BOT, X2, Y_TOP)))
texts.append((ax.text(cx2, yh + 0.08, r"Partially informed sellers ($\pi < 1$)",
                      fontsize=FS_HEAD, weight="normal", ha="center", va="center"),
              (X2, Y_HEAD_BOT, X3, Y_TOP)))

# Row headers.
xl = X0 + 0.06
yr1 = (Y_HEAD_BOT + Y_ROW1_BOT) / 2
yr2 = (Y_ROW1_BOT + Y_ROW2_BOT) / 2
texts.append((ax.text(xl, yr1, r"Buyers do not care ($\rho = 0$)", fontsize=FS_HEAD,
                      weight="normal", ha="left", va="center"),
              (X0, Y_ROW1_BOT, X1, Y_HEAD_BOT)))
texts.append((ax.text(xl, yr2 + 0.09, r"Buyers care ($\rho = 1$)", fontsize=FS_HEAD,
                      weight="normal", ha="left", va="center"),
              (X0, Y_ROW2_BOT, X1, Y_ROW1_BOT)))
texts.append((ax.text(xl, yr2 - 0.09, "GM dep. 2", fontsize=FS_TAG, color=SPRED,
                      ha="left", va="center"),
              (X0, Y_ROW2_BOT, X1, Y_ROW1_BOT)))

# Top row: disclosure irrelevant (both columns).
for cx, (xa, xb) in ((cx1, (X1, X2)), (cx2, (X2, X3))):
    for a in lines_at(ax, cx, yr1, [
            ("Disclosure Irrelevant", FS_TITLE, BLUE_TXT, "medium", "normal"),
            ("No demand response to disclosure", FS_BODY, INK, "normal", "normal"),
            (r"Premium: $\Delta = 0$", FS_BODY, INK, "normal", "normal")]):
        texts.append((a, (xa, Y_ROW1_BOT, xb, Y_HEAD_BOT)))

# Bottom-left: full unraveling.
for a in lines_at(ax, cx1, yr2, [
        ("Full Unraveling", FS_TITLE, GREEN_TXT, "medium", "normal"),
        ("Grossman–Milgrom", FS_BODY, INK, "normal", "normal"),
        ("Silence is fully penalised", FS_BODY, INK, "normal", "normal")]):
    texts.append((a, (X1, Y_ROW2_BOT, X2, Y_ROW1_BOT)))

# Bottom-right: sustained premium, split by attention to silence (psi).
texts.append((ax.text(cx2, (Y_ROW1_BOT + Y_BAND_BOT) / 2, "Sustained Premium",
                      fontsize=FS_TITLE, color=SPRED, weight="medium",
                      ha="center", va="center"),
              (X2, Y_BAND_BOT, X3, Y_ROW1_BOT)))

subcells = [
    (Y_SPLIT, Y_BAND_BOT,
     r"Buyers attend to silence ($\psi = 1$)",
     r"Sustained premium: $0 < \Delta < b$",
     "Silence sells below a verified efficient rating",
     "e.g. houses"),
    (Y_ROW2_BOT, Y_SPLIT,
     r"Buyers attend less to silence ($\psi < 1$)",
     r"Sustained premium: $\Delta$ can exceed $b$",
     "Silence can sell above a verified efficient rating",
     "e.g. apartments"),
]
for yb, yt, head, l1, l2, note in subcells:
    ym = (yb + yt) / 2
    for a in lines_at(ax, cx2, ym, [
            (head, FS_SUBHEAD, INK, "medium", "normal"),
            (l1, FS_SUB, INK, "normal", "normal"),
            (l2, FS_SUB, INK, "normal", "normal"),
            (note, FS_NOTE, INK_SOFT, "normal", "italic")], gap=1.36):
        texts.append((a, (X2, yb, X3, yt)))

# ---------------------------------------------------- fit / overlap check ----
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
inv = ax.transData.inverted()
boxes, problems = [], []
for art, (xa, ya, xb, yb) in texts:
    bb = art.get_window_extent(renderer).transformed(inv)
    pad = 0.02
    if bb.x0 < xa + pad or bb.x1 > xb - pad or bb.y0 < ya or bb.y1 > yb:
        problems.append(f"outside its cell: {art.get_text()!r}")
    boxes.append((art, bb))
for i, (a, ba) in enumerate(boxes):
    for b, bbb in boxes[i + 1:]:
        if ba.overlaps(bbb):
            problems.append(f"overlap: {a.get_text()!r} / {b.get_text()!r}")
for p in problems:
    print("WARNING", p)

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=300, facecolor="white")
plt.close(fig)
print(f"wrote {OUT}  ({W:.2f} x {H:.2f} in at 300 dpi)")
