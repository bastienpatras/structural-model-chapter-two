"""
viz/tables.py
=============
Styled pandas display helpers for Jupyter notebooks.

All functions return a pandas Styler that renders as a clean HTML table
in a notebook cell.  The design mirrors the "disclosure" Plotly theme:
deep navy headers, clean white rows, Inter font.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .theme import PALETTE, GROUP_LABELS, EQ_LABELS

# ---------------------------------------------------------------------------
# CSS constants
# ---------------------------------------------------------------------------

_HEADER_BG   = PALETTE["navy"]
_HEADER_FG   = "white"
_ALT_ROW_BG  = "#F7F9FC"
_BORDER      = f"1px solid #DDE3EC"
_FONT        = "Inter, -apple-system, 'Segoe UI', sans-serif"
_FONT_SIZE   = "13px"
_PAD         = "6px 12px"

_BASE_STYLES = [
    {"selector": "",              "props": [("font-family", _FONT),
                                             ("font-size", _FONT_SIZE),
                                             ("border-collapse", "collapse")]},
    {"selector": "thead tr th",   "props": [("background-color", _HEADER_BG),
                                             ("color", _HEADER_FG),
                                             ("padding", _PAD),
                                             ("text-align", "left"),
                                             ("border", _BORDER),
                                             ("font-weight", "600"),
                                             ("letter-spacing", "0.02em")]},
    {"selector": "tbody tr td",   "props": [("padding", _PAD),
                                             ("border", _BORDER),
                                             ("color", PALETTE["navy"])]},
    {"selector": "tbody tr:nth-child(even) td",
                                  "props": [("background-color", _ALT_ROW_BG)]},
    {"selector": "caption",       "props": [("caption-side", "top"),
                                             ("font-weight", "600"),
                                             ("font-size", "14px"),
                                             ("color", PALETTE["navy"]),
                                             ("padding-bottom", "8px"),
                                             ("text-align", "left")]},
]


def styled_df(
    df: pd.DataFrame,
    caption: str = "",
    fmt: str | dict | None = None,
    pct_cols: list[str] | None = None,
    int_cols: list[str] | None = None,
) -> "pd.io.formats.style.Styler":
    """
    Return a styled pandas Styler ready for notebook display.

    Parameters
    ----------
    df        : DataFrame to style
    caption   : Optional table caption (rendered above the table)
    fmt       : Format string (applied to all numeric columns) or dict
                {col: fmt_str}.  Default: "{:.4f}" for floats.
    pct_cols  : Columns to format as percentages  (e.g. "39.2%")
    int_cols  : Columns to format as integers
    """
    num_cols  = df.select_dtypes(include="number").columns.tolist()

    # Build format dict
    fmt_dict: dict = {}
    if fmt is None:
        fmt_dict = {c: "{:.4f}" for c in num_cols}
    elif isinstance(fmt, str):
        fmt_dict = {c: fmt for c in num_cols}
    else:
        fmt_dict = dict(fmt)

    if pct_cols:
        fmt_dict.update({c: "{:.1%}" for c in pct_cols if c in df.columns})
    if int_cols:
        fmt_dict.update({c: "{:,.0f}" for c in int_cols if c in df.columns})

    styler = (
        df.style
          .set_table_styles(_BASE_STYLES)
          .format(fmt_dict, na_rep="—")
    )
    if caption:
        styler = styler.set_caption(caption)
    return styler


def moment_fit_styled(
    data_moments: dict,
    model_moments: dict,
) -> "pd.io.formats.style.Styler":
    """
    Build and style the moment-fit comparison table (Table 6).

    Rows = markets. For each market: data moment, model moment, difference.
    Colour-codes the difference column: green if |diff| < 0.01, red otherwise.
    """
    rows = []
    for mid, dm in sorted(data_moments.items()):
        mm = model_moments.get(mid)
        if mm is None:
            continue
        rows.append({
            "Market":       mid,
            "m₁ data":      dm.m1,   "m₁ model": mm.m1_model, "Δm₁": dm.m1 - mm.m1_model,
            "m₂ data":      dm.m2,   "m₂ model": mm.m2_model, "Δm₂": dm.m2 - mm.m2_model,
            "m₃ data":      dm.m3,   "m₃ model": mm.m3_model, "Δm₃": dm.m3 - mm.m3_model,
            "m₄ data":      dm.m4,   "m₄ model": mm.m4_model, "Δm₄": dm.m4 - mm.m4_model,
            "Eq. type":     EQ_LABELS.get(mm.eq_type, mm.eq_type),
        })

    if not rows:
        return pd.DataFrame().style

    tbl = pd.DataFrame(rows).set_index("Market")

    # Mean row
    num_cols = tbl.select_dtypes("number").columns
    mean_row = tbl[num_cols].mean().rename("Mean")
    tbl_with_mean = pd.concat([tbl, mean_row.to_frame().T.reindex(tbl.columns, axis=1)])

    diff_cols = [c for c in tbl_with_mean.columns if c.startswith("Δ")]

    def _colour_diff(val):
        if pd.isna(val):
            return ""
        return f"color: {PALETTE['sage'] if abs(val) < 0.01 else PALETTE['crimson']}"

    fmt_dict = {c: "{:.4f}" for c in tbl_with_mean.select_dtypes("number").columns}

    return (
        tbl_with_mean.style
          .set_table_styles(_BASE_STYLES)
          .format(fmt_dict, na_rep="—")
          .applymap(_colour_diff, subset=diff_cols)
          .set_caption("Moment fit: data vs model (m₁–m₄)")
    )
