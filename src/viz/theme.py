"""
viz/theme.py
============
Design system for the disclosure model figures.

A single Plotly template "disclosure" is registered globally on import.
All chart functions in charts.py reference it via template="disclosure".

Palette
-------
A modern academic palette: deep navy as primary, bright teal as secondary,
warm amber and coral as warm accents, violet and sage for additional traces.
Designed to read well both on screen (HTML) and in greyscale (PDF).
"""

import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

PALETTE: dict[str, str] = {
    "navy":   "#1D3461",   # deep cobalt blue  — primary text, axes
    "teal":   "#1BA3C6",   # bright teal       — secondary, truthful disclosure
    "amber":  "#F7B731",   # golden amber      — accent warm, mixed strategy
    "coral":  "#FF6348",   # vivid coral       — strategic hiding, partial sep.
    "violet": "#6C5CE7",   # muted violet      — unverified disclosers, additional traces
    "sage":   "#6AB187",   # muted sage green  — uninformed sellers, full unraveling
    "smoke":  "#94A3B8",   # cool grey         — neutral, background bars
    "crimson":"#C0392B",   # deep crimson      — error / warning markers
}

# Ordered trace colour sequence
COLOR_SEQ: list[str] = [
    PALETTE["navy"],
    PALETTE["teal"],
    PALETTE["amber"],
    PALETTE["coral"],
    PALETTE["violet"],
    PALETTE["sage"],
]

# Colours for the four listing groups
GROUP_COLORS: dict[str, str] = {
    "truthful_disclosure": PALETTE["teal"],
    "strategic_hiding":    PALETTE["coral"],
    "uninformed":          PALETTE["smoke"],
    "unverified_disclosers": PALETTE["violet"],
}

# Group display labels (for legends / axis ticks)
GROUP_LABELS: dict[str, str] = {
    "truthful_disclosure":   "Verified disclosers",
    "strategic_hiding":      "Strategic hiders",
    "uninformed":            "Uninformed sellers",
    "unverified_disclosers": "Unverified disclosers",
}

# Colours for the three equilibrium regimes
EQ_COLORS: dict[str, str] = {
    "full_unraveling":    PALETTE["sage"],
    "mixed_strategy":     PALETTE["amber"],
    "partial_separation": PALETTE["coral"],
}

EQ_LABELS: dict[str, str] = {
    "full_unraveling":    "Full unraveling",
    "mixed_strategy":     "Mixed strategy",
    "partial_separation": "Partial separation",
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

FONT: str = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif"
FONT_SIZE     = 13
TITLE_SIZE    = 15
AXIS_SIZE     = 12
TICK_SIZE     = 11
LEGEND_SIZE   = 11
HOVER_SIZE    = 11

# ---------------------------------------------------------------------------
# Shared layout constants
# ---------------------------------------------------------------------------

GRID_COLOR   = "#EEF1F5"
LINE_COLOR   = "#CDD3DB"
BG_COLOR     = "white"

# ---------------------------------------------------------------------------
# Plotly template
# ---------------------------------------------------------------------------

_axis_defaults = dict(
    showgrid    = True,
    gridcolor   = GRID_COLOR,
    gridwidth   = 1,
    zeroline    = False,
    linecolor   = LINE_COLOR,
    linewidth   = 1,
    showline    = True,
    ticks       = "outside",
    ticklen     = 4,
    tickcolor   = LINE_COLOR,
    tickfont    = dict(size=TICK_SIZE, color=PALETTE["navy"]),
    title_font  = dict(size=AXIS_SIZE, color=PALETTE["navy"]),
    automargin  = True,
)

_tmpl = go.layout.Template()
_tmpl.layout = go.Layout(
    font        = dict(family=FONT, size=FONT_SIZE, color=PALETTE["navy"]),
    title       = dict(
        font    = dict(size=TITLE_SIZE, color=PALETTE["navy"], family=FONT),
        x       = 0.02,
        xanchor = "left",
        pad     = dict(l=0, b=10),
    ),
    paper_bgcolor = BG_COLOR,
    plot_bgcolor  = BG_COLOR,
    colorway      = COLOR_SEQ,
    xaxis         = _axis_defaults,
    yaxis         = _axis_defaults,
    legend        = dict(
        bgcolor     = "rgba(255, 255, 255, 0.92)",
        bordercolor = LINE_COLOR,
        borderwidth = 1,
        font        = dict(size=LEGEND_SIZE, color=PALETTE["navy"]),
        itemsizing  = "constant",
    ),
    margin        = dict(l=64, r=32, t=64, b=60),
    hoverlabel    = dict(
        bgcolor     = "white",
        bordercolor = PALETTE["navy"],
        font        = dict(size=HOVER_SIZE, family=FONT, color=PALETTE["navy"]),
        align       = "left",
    ),
    colorscale    = dict(
        sequential    = "Teal",
        sequentialminus = "RdBu",
        diverging     = "RdBu",
    ),
)

pio.templates["disclosure"]  = _tmpl
pio.templates.default        = "disclosure"
