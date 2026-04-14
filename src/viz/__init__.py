"""
src/viz
=======
Publication-ready Plotly visualisation helpers for the disclosure model.

Importing this package registers the "disclosure" Plotly template globally.

Usage in notebooks:
    from src.viz import theme                   # register template (side-effect)
    from src.viz.charts import chart_moment_fit, chart_estimates_by_market, ...
    from src.viz.tables import styled_df, moment_fit_styled
"""

from . import theme   # registers pio.templates["disclosure"] on import

from .theme import PALETTE, COLOR_SEQ, GROUP_COLORS, EQ_COLORS

from .charts import (
    chart_data_overview,
    chart_hedonic_params,
    chart_hiding_premiums,
    chart_moment_fit,
    chart_estimates_by_market,
    chart_equilibrium_objects,
    chart_msm_surface,
    chart_belief_function,
    chart_market_scatter,
    chart_renovation_thresholds,
    chart_event_study_ts,
    chart_did_estimates,
)

from .tables import styled_df, moment_fit_styled

__all__ = [
    "theme",
    "PALETTE", "COLOR_SEQ", "GROUP_COLORS", "EQ_COLORS",
    "chart_data_overview",
    "chart_hedonic_params",
    "chart_hiding_premiums",
    "chart_moment_fit",
    "chart_estimates_by_market",
    "chart_equilibrium_objects",
    "chart_msm_surface",
    "chart_belief_function",
    "chart_market_scatter",
    "chart_renovation_thresholds",
    "chart_event_study_ts",
    "chart_did_estimates",
    "styled_df",
    "moment_fit_styled",
]
