"""
viz/charts.py
=============
Publication-ready Plotly figure factories for the disclosure model.

All functions return a ``go.Figure`` using the "disclosure" template.
Saving to file (HTML / PDF) is the caller's responsibility.

Import this module *after* importing ``src.viz`` (or ``src.viz.theme``) so that
the "disclosure" template is registered before any figure is constructed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import TYPE_CHECKING

from .theme import (
    PALETTE, COLOR_SEQ, GROUP_COLORS, GROUP_LABELS,
    EQ_COLORS, EQ_LABELS, FONT,
)

if TYPE_CHECKING:
    from ..model import ValuationParams

_T = "disclosure"  # template shorthand


def _hex_to_rgba(hex_color: str, alpha: float = 0.18) -> str:
    """Convert #RRGGBB to rgba(r,g,b,alpha) — Plotly fillcolor doesn't accept 8-digit hex."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ref_line(fig, value: float, color: str = PALETTE["smoke"],
              dash: str = "dash", row=None, col=None, annotation: str | None = None):
    """Add a horizontal reference line to a subplot."""
    kwargs = dict(y0=value, y1=value, x0=0, x1=1, xref="paper",
                  yref="y" if row is None else f"y{row if row == 1 else row}",
                  line=dict(color=color, dash=dash, width=1.5))
    if row:
        kwargs["yref"] = f"y{'' if row == 1 else row}"
        kwargs["row"] = row
        kwargs["col"] = col
    fig.add_hline(**{k: v for k, v in kwargs.items() if k not in ("row", "col")},
                  row=row, col=col)
    if annotation:
        fig.add_annotation(
            x=1.01, xref="paper",
            y=value, yref="y" if row is None else f"y{'' if row == 1 else row}",
            text=annotation, showarrow=False,
            font=dict(size=10, color=color), xanchor="left",
            row=row, col=col,
        )


# ---------------------------------------------------------------------------
# 1. Data overview
# ---------------------------------------------------------------------------

def chart_data_overview(
    df: pd.DataFrame,
    market_stats: pd.DataFrame,
) -> go.Figure:
    """
    Three-panel overview:
      Left  — listing counts by group (horizontal bar)
      Centre — log-price distribution by group (box + mean marker)
      Right  — σ̂₀ across markets (scatter, sized by n_total)
    """
    groups = ["truthful_disclosure", "strategic_hiding", "uninformed", "unverified_disclosers"]
    present = [g for g in groups if g in df["group"].unique()]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Listings by group", "Log-price distribution by group", "Hiding rate σ̂₀ across markets"),
        column_widths=[0.25, 0.40, 0.35],
        horizontal_spacing=0.10,
    )

    # Panel 1 — horizontal bar of counts
    counts = df.groupby("group").size().reindex(present, fill_value=0)
    fig.add_trace(go.Bar(
        y=[GROUP_LABELS.get(g, g) for g in present],
        x=counts.values,
        orientation="h",
        marker_color=[GROUP_COLORS[g] for g in present],
        marker_line_width=0,
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
        showlegend=False,
    ), row=1, col=1)

    # Panel 2 — box plot per group
    for g in present:
        sub = df[df["group"] == g]["log_price"].dropna()
        fig.add_trace(go.Box(
            y=sub,
            name=GROUP_LABELS.get(g, g),
            marker_color=GROUP_COLORS[g],
            line_color=GROUP_COLORS[g],
            fillcolor=_hex_to_rgba(GROUP_COLORS[g], 0.18),
            boxmean="sd",
            hovertemplate="%{y:.3f}<extra>" + GROUP_LABELS.get(g, g) + "</extra>",
            showlegend=False,
        ), row=1, col=2)

    # Panel 3 — σ̂₀ scatter by market
    ms = market_stats.copy().sort_values("sigma_0_hat", ascending=False)
    fig.add_trace(go.Scatter(
        x=list(range(len(ms))),
        y=ms["sigma_0_hat"].values,
        mode="markers",
        marker=dict(
            size=ms["n_total"].values ** 0.4,
            color=ms["sigma_0_hat"].values,
            colorscale=[[0, PALETTE["teal"]], [0.5, PALETTE["amber"]], [1, PALETTE["coral"]]],
            showscale=True,
            colorbar=dict(title="σ̂₀", thickness=12, len=0.6, x=1.01),
            line=dict(width=0.5, color="white"),
        ),
        customdata=ms["n_total"].values,
        hovertemplate="Market rank %{x}<br>σ̂₀ = %{y:.3f}<br>N = %{customdata:,.0f}<extra></extra>",
        showlegend=False,
    ), row=1, col=3)

    fig.update_xaxes(title_text="Count", row=1, col=1)
    fig.update_xaxes(title_text="Market rank (by σ̂₀)", row=1, col=3)
    fig.update_yaxes(title_text="log price", row=1, col=2)
    fig.update_yaxes(title_text="σ̂₀", row=1, col=3)
    fig.update_layout(
        template=_T,
        height=420,
        title_text="Data overview",
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Hedonic regression parameters
# ---------------------------------------------------------------------------

def chart_hedonic_params(
    hedonic_params,
    market_stats: pd.DataFrame,
    true_beta1: float | None = None,
) -> go.Figure:
    """
    Two-panel horizontal dot chart of hedonic parameters.
      Left  — β̂₁_m (EPC premium per grade, sorted ascending)
      Right — σ̂_m (residual log-price std dev)
    Markets on the y-axis; vertical reference lines at pooled estimates.
    """
    markets = sorted(hedonic_params.beta_1_m.keys())
    b1_vals = [hedonic_params.beta_1_m[m] for m in markets]
    sc_vals = [hedonic_params.sigma_eps_m.get(m, hedonic_params.sigma_eps) for m in markets]

    # Sort by β̂₁_m ascending so largest is at top
    order     = np.argsort(b1_vals)
    labels    = [str(markets[i]) for i in order]
    b1_s      = [b1_vals[i]      for i in order]
    sc_s      = [sc_vals[i]      for i in order]

    # Colour dots by value: teal-to-navy gradient via normalised intensity
    b1_min, b1_max = min(b1_s), max(b1_s)
    b1_range = max(b1_max - b1_min, 1e-6)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("EPC premium β̂₁_m (log-price per grade)",
                        "Residual dispersion σ̂_m"),
        horizontal_spacing=0.14,
    )

    # --- Left panel: β̂₁_m lollipops ---
    # Stems: scatter from 0 to β̂₁_m
    for i, (lbl, val) in enumerate(zip(labels, b1_s)):
        fig.add_trace(go.Scatter(
            x=[0, val], y=[lbl, lbl],
            mode="lines",
            line=dict(color=PALETTE["smoke"], width=1.2),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)

    # Dots
    fig.add_trace(go.Scatter(
        x=b1_s, y=labels,
        mode="markers",
        marker=dict(
            size=9,
            color=b1_s,
            colorscale=[[0, PALETTE["teal"]], [1, PALETTE["navy"]]],
            cmin=b1_min, cmax=b1_max,
            line=dict(width=0),
        ),
        name="β̂₁_m",
        hovertemplate="<b>Market %{y}</b><br>β̂₁_m = %{x:.4f}<extra></extra>",
    ), row=1, col=1)

    # Pooled reference line
    fig.add_vline(
        x=hedonic_params.beta_1, line_dash="dash",
        line_color=PALETTE["navy"], line_width=1.5, row=1, col=1,
    )
    fig.add_annotation(
        x=hedonic_params.beta_1, y=1.0, yref="paper",
        text=f"pooled {hedonic_params.beta_1:.4f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
        row=1, col=1,
    )
    if true_beta1 is not None:
        fig.add_vline(
            x=true_beta1, line_dash="dot",
            line_color=PALETTE["crimson"], line_width=1.5, row=1, col=1,
        )

    # --- Right panel: σ̂_m dots ---
    sc_min, sc_max = min(sc_s), max(sc_s)
    for i, (lbl, val) in enumerate(zip(labels, sc_s)):
        fig.add_trace(go.Scatter(
            x=[0, val], y=[lbl, lbl],
            mode="lines",
            line=dict(color=PALETTE["smoke"], width=1.2),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=sc_s, y=labels,
        mode="markers",
        marker=dict(
            size=9,
            color=sc_s,
            colorscale=[[0, PALETTE["violet"]], [1, PALETTE["navy"]]],
            cmin=sc_min, cmax=sc_max,
            line=dict(width=0),
        ),
        name="σ̂_m",
        hovertemplate="<b>Market %{y}</b><br>σ̂_m = %{x:.4f}<extra></extra>",
    ), row=1, col=2)

    fig.add_vline(
        x=hedonic_params.sigma_eps, line_dash="dash",
        line_color=PALETTE["navy"], line_width=1.5, row=1, col=2,
    )
    fig.add_annotation(
        x=hedonic_params.sigma_eps, y=1.0, yref="paper",
        text=f"pooled {hedonic_params.sigma_eps:.4f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
        row=1, col=2,
    )

    n_markets = len(labels)
    fig.update_xaxes(title_text="β̂₁_m", zeroline=True, zerolinewidth=1,
                     zerolinecolor=PALETTE["smoke"], row=1, col=1)
    fig.update_xaxes(title_text="σ̂_m",  zeroline=True, zerolinewidth=1,
                     zerolinecolor=PALETTE["smoke"], row=1, col=2)
    fig.update_yaxes(tickfont=dict(size=10), row=1, col=1)
    fig.update_yaxes(tickfont=dict(size=10), showticklabels=False, row=1, col=2)

    fig.update_layout(
        template=_T,
        height=max(420, 18 * n_markets + 100),
        showlegend=False,
        title_text="Hedonic regression — market-level estimates",
        margin=dict(l=80, r=40, t=80, b=40),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Hiding premiums and direct ρ estimator
# ---------------------------------------------------------------------------

def chart_hiding_premiums(rho_direct_df: pd.DataFrame) -> go.Figure:
    """
    Two-panel horizontal dot chart:
      Left  — Hiding premium Δ̄_m, sorted ascending
      Right — Direct ρ̂_m (clipped markets highlighted in coral)
    Markets on the y-axis; both panels share the same order.
    """
    df = rho_direct_df.copy().sort_values("delta_bar", ascending=True)
    labels   = [str(m) for m in df.index]
    delta    = df["delta_bar"].values
    clip_col = "rho_hat_clipped" if "rho_hat_clipped" in df.columns else "rho_hat_direct"
    raw_col  = "rho_hat_direct"  if "rho_hat_direct"  in df.columns else clip_col
    rho      = df[clip_col].values
    clipped  = (df[raw_col] < 0) | (df[raw_col] > 1)

    n = len(labels)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Hiding premium Δ̄_m (log-price units)",
                        "EPC-sensitive buyer share ρ̂_m"),
        horizontal_spacing=0.14,
    )

    # --- Left: Δ̄_m lollipops ---
    for lbl, val in zip(labels, delta):
        fig.add_trace(go.Scatter(
            x=[0, val], y=[lbl, lbl],
            mode="lines",
            line=dict(color=PALETTE["smoke"], width=1.2),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=delta, y=labels,
        mode="markers",
        marker=dict(
            size=9,
            color=delta,
            colorscale=[[0, PALETTE["amber"]], [1, PALETTE["coral"]]],
            cmin=min(delta), cmax=max(delta),
            line=dict(width=0),
        ),
        name="Δ̄_m",
        hovertemplate="<b>Market %{y}</b><br>Δ̄_m = %{x:.4f}<extra></extra>",
    ), row=1, col=1)

    mean_delta = float(np.mean(delta))
    fig.add_vline(x=mean_delta, line_dash="dash",
                  line_color=PALETTE["navy"], line_width=1.5, row=1, col=1)
    fig.add_annotation(
        x=mean_delta, y=1.0, yref="paper",
        text=f"mean {mean_delta:.4f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
        row=1, col=1,
    )

    # --- Right: ρ̂_m lollipops (clipped = coral, normal = teal) ---
    dot_colors = [PALETTE["coral"] if c else PALETTE["teal"] for c in clipped]
    for lbl, val in zip(labels, rho):
        fig.add_trace(go.Scatter(
            x=[0, val], y=[lbl, lbl],
            mode="lines",
            line=dict(color=PALETTE["smoke"], width=1.2),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=2)

    # Normal markets
    mask_ok = ~clipped.values
    if mask_ok.any():
        fig.add_trace(go.Scatter(
            x=rho[mask_ok], y=[labels[i] for i in np.where(mask_ok)[0]],
            mode="markers",
            marker=dict(size=9, color=PALETTE["teal"], line=dict(width=0)),
            name="ρ̂_m",
            hovertemplate="<b>Market %{y}</b><br>ρ̂_m = %{x:.3f}<extra></extra>",
        ), row=1, col=2)

    # Clipped markets
    mask_cl = clipped.values
    if mask_cl.any():
        fig.add_trace(go.Scatter(
            x=rho[mask_cl], y=[labels[i] for i in np.where(mask_cl)[0]],
            mode="markers",
            marker=dict(size=9, color=PALETTE["coral"],
                        symbol="diamond", line=dict(width=0)),
            name="ρ̂_m (clipped)",
            hovertemplate="<b>Market %{y}</b><br>ρ̂_m = %{x:.3f} (clipped)<extra></extra>",
        ), row=1, col=2)

    fig.add_vline(x=0.5, line_dash="dot",
                  line_color=PALETTE["smoke"], line_width=1.2, row=1, col=2)

    fig.update_xaxes(title_text="Δ̄_m", zeroline=True, zerolinewidth=1,
                     zerolinecolor=PALETTE["smoke"], row=1, col=1)
    fig.update_xaxes(title_text="ρ̂_m", range=[-0.02, 1.08],
                     tickformat=".0%", row=1, col=2)
    fig.update_yaxes(tickfont=dict(size=10), row=1, col=1)
    fig.update_yaxes(tickfont=dict(size=10), showticklabels=False, row=1, col=2)

    fig.update_layout(
        template=_T,
        height=max(420, 18 * n + 100),
        showlegend=bool(mask_cl.any()),
        legend=dict(x=0.75, y=0.02, xanchor="left"),
        title_text="First-stage: hiding premium and direct ρ estimate",
        margin=dict(l=80, r=40, t=80, b=40),
    )
    return fig


# ---------------------------------------------------------------------------
# 4. Moment fit
# ---------------------------------------------------------------------------

def chart_moment_fit(
    data_moments: dict,
    model_moments: dict,
) -> go.Figure:
    """
    Two-panel scatter for the active MSM moments (m₃^DiD, m₄) plus one panel
    for the overidentifying restriction m₅. m₁ and m₂ are excluded — they are
    fit by construction after residualisation and carry no information on ρ or c₀.

    Each panel shows the 45° perfect-fit line. Points are coloured by |residual|.
    Markets where m₃ is NaN (no DiD coverage) are shown as hollow markers.
    """
    moment_info = [
        ("m3", "m3_model", "m₃<sup>DiD</sup>  — non-disclosure premium  Δ̂<sub>m</sub>"),
        ("m4", "m4_model", "m₄  — hiding rate  σ̂₀"),
        ("m5", "m5_model", "m₅  — σ̂₁ ≈ 0  (overid. restriction)"),
    ]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[info[2] for info in moment_info],
        horizontal_spacing=0.10,
    )

    markets = sorted(set(data_moments.keys()) & set(model_moments.keys()))

    for idx, (d_attr, m_attr, _) in enumerate(moment_info):
        col = idx + 1

        d_vals = np.array([getattr(data_moments[m], d_attr) for m in markets])
        m_vals = np.array([getattr(model_moments[m], m_attr) for m in markets])

        nan_mask = np.isnan(d_vals)
        valid    = ~nan_mask

        resids = np.where(valid, np.abs(d_vals - m_vals), 0.0)
        max_r  = resids[valid].max() if valid.any() and resids[valid].max() > 0 else 1.0

        # 45° perfect-fit line
        all_vals = np.concatenate([d_vals[valid], m_vals[valid]]) if valid.any() else np.array([0, 1])
        lo = all_vals.min() * 0.98
        hi = all_vals.max() * 1.02
        fig.add_trace(go.Scatter(
            x=[lo, hi], y=[lo, hi],
            mode="lines",
            line=dict(color=PALETTE["smoke"], dash="dash", width=1),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=col)

        # Plotted markets (valid data only)
        if valid.any():
            fig.add_trace(go.Scatter(
                x=d_vals[valid], y=m_vals[valid],
                mode="markers",
                marker=dict(
                    size=9,
                    color=resids[valid],
                    colorscale=[[0, PALETTE["teal"]], [0.5, PALETTE["amber"]], [1, PALETTE["coral"]]],
                    cmin=0, cmax=max_r,
                    line=dict(width=0.5, color="white"),
                    showscale=False,
                ),
                customdata=[str(markets[i]) for i in range(len(markets)) if valid[i]],
                hovertemplate="Market %{customdata}<br>data = %{x:.4f}<br>model = %{y:.4f}<br>|Δ| = %{marker.color:.4f}<extra></extra>",
                showlegend=False,
            ), row=1, col=col)

        # Annotate missing DiD coverage count on the m₃ panel
        if idx == 0 and nan_mask.any():
            n_missing = int(nan_mask.sum())
            fig.add_annotation(
                x=0.98, y=0.04, xref="x domain", yref="y domain",
                text=f"{n_missing} markets: no DiD",
                showarrow=False, xanchor="right",
                font=dict(size=10, color=PALETTE["smoke"]),
                row=1, col=1,
            )

        fig.update_xaxes(title_text="data", row=1, col=col)
        fig.update_yaxes(title_text="model", row=1, col=col)

    fig.update_layout(
        template=_T, height=380,
        title_text="Moment fit: data vs model  (active moments only)",
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# 5. MSM estimates by market
# ---------------------------------------------------------------------------

def chart_estimates_by_market(msm_result) -> go.Figure:
    """
    Two-panel horizontal lollipop chart of MSM estimates.
      Left  — ρ̂_m sorted ascending, coloured by equilibrium regime
      Right — ĉ₀_m (same market order), coloured by equilibrium regime
    Reference lines at cross-market means.
    """
    markets  = sorted(msm_result.rho_hat.keys(), key=lambda m: msm_result.rho_hat[m])
    rho_vals = [msm_result.rho_hat[m] for m in markets]
    c0_vals  = [msm_result.c0_hat[m]  for m in markets]
    eq_types = [msm_result.eq_types.get(m, "mixed_strategy") for m in markets]
    colors   = [EQ_COLORS.get(eq, PALETTE["smoke"]) for eq in eq_types]
    labels   = [str(m) for m in markets]
    n        = len(markets)

    rho_mean = float(np.mean(rho_vals))
    c0_mean  = float(np.mean(c0_vals))

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "ρ̂<sub>m</sub> — share of EPC-sensitive buyers",
            "ĉ₀<sub>m</sub> — hiding cost (log-price units)",
        ),
        horizontal_spacing=0.12,
    )

    # ── ρ̂ lollipops ──────────────────────────────────────────────────────────
    for i, (lbl, val) in enumerate(zip(labels, rho_vals)):
        fig.add_shape(
            type="line", x0=0, x1=val, y0=lbl, y1=lbl,
            line=dict(color=colors[i], width=1.5),
            row=1, col=1,
        )
    added_eq: set[str] = set()
    for lbl, val, eq, col in zip(labels, rho_vals, eq_types, colors):
        show = eq not in added_eq
        fig.add_trace(go.Scatter(
            x=[val], y=[lbl],
            mode="markers",
            marker=dict(color=col, size=9, line=dict(color="white", width=1)),
            name=EQ_LABELS.get(eq, eq),
            legendgroup=eq,
            showlegend=show,
            hovertemplate=f"<b>Market {lbl}</b><br>ρ̂ = {val:.3f}<br>{EQ_LABELS.get(eq, eq)}<extra></extra>",
        ), row=1, col=1)
        added_eq.add(eq)

    fig.add_vline(
        x=rho_mean, line_dash="dash",
        line_color=PALETTE["navy"], line_width=1.5, row=1, col=1,
    )
    fig.add_annotation(
        x=rho_mean, y=1.0, yref="paper",
        text=f"mean {rho_mean:.3f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
    )

    # ── ĉ₀ lollipops ─────────────────────────────────────────────────────────
    for i, (lbl, val) in enumerate(zip(labels, c0_vals)):
        fig.add_shape(
            type="line", x0=0, x1=val, y0=lbl, y1=lbl,
            line=dict(color=colors[i], width=1.5),
            row=1, col=2,
        )
    for lbl, val, eq, col in zip(labels, c0_vals, eq_types, colors):
        fig.add_trace(go.Scatter(
            x=[val], y=[lbl],
            mode="markers",
            marker=dict(color=col, size=9, line=dict(color="white", width=1)),
            name=EQ_LABELS.get(eq, eq),
            legendgroup=eq,
            showlegend=False,
            hovertemplate=f"<b>Market {lbl}</b><br>ĉ₀ = {val:.4f}<br>{EQ_LABELS.get(eq, eq)}<extra></extra>",
        ), row=1, col=2)

    fig.add_vline(
        x=c0_mean, line_dash="dash",
        line_color=PALETTE["navy"], line_width=1.5, row=1, col=2,
    )
    fig.add_annotation(
        x=c0_mean, y=1.0, yref="paper",
        xref="x2",
        text=f"mean {c0_mean:.4f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
    )

    fig.update_xaxes(title_text="ρ̂<sub>m</sub>", range=[0, 1.05], row=1, col=1)
    fig.update_xaxes(title_text="ĉ₀<sub>m</sub>", row=1, col=2)
    fig.update_yaxes(tickfont=dict(size=9), row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=2)
    fig.update_layout(
        template=_T,
        height=max(420, 18 * n + 120),
        title_text="MSM estimates by market",
        legend=dict(orientation="h", y=-0.08, x=0, font=dict(size=11)),
    )
    return fig


# ---------------------------------------------------------------------------
# 6. Equilibrium objects as ρ varies
# ---------------------------------------------------------------------------

def chart_equilibrium_objects(
    market_id,
    pi: float,
    theta_bar: float,
    params,
    c0_hat: float,
    rho_hat: float | None = None,
    rho_grid: np.ndarray | None = None,
) -> go.Figure:
    """
    Four-panel chart of equilibrium objects as ρ varies in [0, 1]:
      Top-left    — equilibrium hiding rate σ₀*(ρ)
      Top-right   — equilibrium belief e*(ρ)
      Bottom-left — optimal log price under hiding p*(d=0, e*(ρ), ρ)
      Bottom-right— optimal log price under disclosure p*(d=1, θ=0, ρ)

    Vertical line marks the estimated ρ̂_m if provided.
    """
    from ..model import solve_equilibrium, optimal_price

    if rho_grid is None:
        rho_grid = np.linspace(0.01, 0.99, 120)

    sigma0_vals, e_star_vals, p_hide_vals, p_disc_vals = [], [], [], []
    for rho in rho_grid:
        eq   = solve_equilibrium(rho, c0_hat, pi, theta_bar, params)
        p_h  = optimal_price(params.v1_hidden(eq.e_star), params.v0, rho, params)
        p_d  = optimal_price(params.v1_disclosed(0.0),    params.v0, rho, params)
        sigma0_vals.append(eq.sigma_0_star)
        e_star_vals.append(eq.e_star)
        p_hide_vals.append(p_h)
        p_disc_vals.append(p_d)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Hiding rate σ₀*(ρ)", "Equilibrium belief e*(ρ)",
            "Optimal price — hiding p*(d=0)", "Optimal price — disclosure p*(d=1, θ=0)",
        ),
        vertical_spacing=0.16, horizontal_spacing=0.12,
    )

    traces = [
        (sigma0_vals, "σ₀*", PALETTE["coral"],   1, 1),
        (e_star_vals, "e*",  PALETTE["teal"],    1, 2),
        (p_hide_vals, "p*(d=0)", PALETTE["amber"],  2, 1),
        (p_disc_vals, "p*(d=1,θ=0)", PALETTE["navy"], 2, 2),
    ]

    for vals, name, color, row, col in traces:
        fig.add_trace(go.Scatter(
            x=rho_grid, y=vals, mode="lines",
            line=dict(color=color, width=2.5),
            name=name,
            hovertemplate=f"ρ = %{{x:.3f}}<br>{name} = %{{y:.4f}}<extra></extra>",
            showlegend=False,
        ), row=row, col=col)

        if rho_hat is not None:
            fig.add_vline(x=rho_hat, line_dash="dash",
                          line_color=PALETTE["smoke"], line_width=1.5,
                          row=row, col=col)
            if row == 1 and col == 1:
                fig.add_annotation(
                    x=rho_hat, y=1.05, xref=f"x", yref="paper",
                    text=f"ρ̂={rho_hat:.2f}", showarrow=False,
                    font=dict(size=10, color=PALETTE["smoke"]),
                    row=row, col=col,
                )

    for col in [1, 2]:
        fig.update_xaxes(title_text="ρ (share EPC-sensitive buyers)", row=2, col=col)
    fig.update_yaxes(title_text="σ₀*", row=1, col=1)
    fig.update_yaxes(title_text="e*", row=1, col=2)
    fig.update_yaxes(title_text="log price", row=2, col=1)
    fig.update_yaxes(title_text="log price", row=2, col=2)

    fig.update_layout(
        template=_T, height=560,
        title_text=f"Equilibrium objects — market {market_id} (c₀ = {c0_hat:.4f})",
    )
    return fig


# ---------------------------------------------------------------------------
# 7. MSM objective surface
# ---------------------------------------------------------------------------

def chart_msm_surface(
    rho_grid: np.ndarray,
    c0_grid: np.ndarray,
    Q_surface: np.ndarray,
    rho_hat: float | None = None,
    c0_hat: float | None = None,
    market_id=None,
) -> go.Figure:
    """
    Contour plot of log(1 + Q(ρ, c₀)) over the (ρ, c₀) parameter space.
    Minimum is marked with a white star.
    """
    log_Q = np.log1p(Q_surface)

    fig = go.Figure()

    fig.add_trace(go.Contour(
        x=rho_grid, y=c0_grid, z=log_Q.T,
        colorscale=[
            [0.0,  "#1D3461"],
            [0.15, "#1BA3C6"],
            [0.35, "#F7B731"],
            [0.65, "#FF6348"],
            [1.0,  "#6C0023"],
        ],
        contours=dict(
            showlabels=True,
            labelfont=dict(size=9, color="white"),
        ),
        colorbar=dict(title="log(1+Q)", thickness=14),
        hovertemplate="ρ = %{x:.3f}<br>c₀ = %{y:.4f}<br>log(1+Q) = %{z:.3f}<extra></extra>",
    ))

    if rho_hat is not None and c0_hat is not None:
        fig.add_trace(go.Scatter(
            x=[rho_hat], y=[c0_hat],
            mode="markers",
            marker=dict(symbol="star", size=16, color="white",
                        line=dict(color=PALETTE["navy"], width=1.5)),
            hovertemplate=f"Optimum<br>ρ̂ = {rho_hat:.3f}<br>ĉ₀ = {c0_hat:.4f}<extra></extra>",
            showlegend=False,
        ))

    title = "MSM objective surface Q(ρ, c₀)"
    if market_id is not None:
        title += f" — market {market_id}"

    fig.update_layout(
        template=_T,
        xaxis_title="ρ (share EPC-sensitive buyers)",
        yaxis_title="c₀ (hiding cost, log-price units)",
        height=480,
        title_text=title,
    )
    return fig


# ---------------------------------------------------------------------------
# 8. Belief function
# ---------------------------------------------------------------------------

def chart_belief_function(
    pi_vals: list | np.ndarray,
    theta_bar: float,
    sigma_0_star: float | None = None,
) -> go.Figure:
    """
    Belief function e(σ₀) for multiple π values.
    e(σ₀) = (1−π)θ̄ / [π(1−θ̄)σ₀ + (1−π)]

    A vertical line marks the estimated equilibrium σ₀* if provided.
    """
    from ..model import belief_function

    sigma_grid = np.linspace(0, 1, 200)

    fig = go.Figure()

    for i, pi in enumerate(pi_vals):
        beliefs = [belief_function(s, pi, theta_bar) for s in sigma_grid]
        color = COLOR_SEQ[i % len(COLOR_SEQ)]
        fig.add_trace(go.Scatter(
            x=sigma_grid, y=beliefs,
            mode="lines",
            line=dict(color=color, width=2.5),
            name=f"π = {pi:.2f}",
            hovertemplate=f"π = {pi:.2f}<br>σ₀ = %{{x:.3f}}<br>e(σ₀) = %{{y:.4f}}<extra></extra>",
        ))

    # Reference: e(0) = theta_bar for all π
    fig.add_hline(y=theta_bar, line_dash="dot", line_color=PALETTE["smoke"],
                  line_width=1.5,
                  annotation_text=f"θ̄ = {theta_bar:.2f}",
                  annotation_position="right",
                  annotation_font=dict(size=10, color=PALETTE["smoke"]))

    if sigma_0_star is not None:
        fig.add_vline(x=sigma_0_star, line_dash="dash", line_color=PALETTE["coral"],
                      line_width=1.5,
                      annotation_text=f"σ₀* = {sigma_0_star:.3f}",
                      annotation_position="top right",
                      annotation_font=dict(size=10, color=PALETTE["coral"]))

    fig.update_layout(
        template=_T,
        xaxis_title="σ₀  (hiding probability of informed low-quality sellers)",
        yaxis_title="e(σ₀)  (buyer belief about average quality in pool)",
        height=420,
        title_text="Belief function e(σ₀) — Eq. (eq:belief_simplified)",
        legend=dict(orientation="h", y=-0.2, x=0),
    )
    return fig


# ---------------------------------------------------------------------------
# 9. Market scatter (π̂ vs θ̄, sized by n_total)
# ---------------------------------------------------------------------------

def chart_market_scatter(market_stats: pd.DataFrame) -> go.Figure:
    """
    Scatter of π̂_m (share informed) vs θ̄_m (mean quality),
    marker size proportional to sqrt(n_total),
    colour shows disclosure rate d̄_m if available.
    """
    ms = market_stats.copy()

    color_col = "disclosure_rate" if "disclosure_rate" in ms.columns else None
    color_vals = ms[color_col].values if color_col else PALETTE["teal"]

    fig = go.Figure(go.Scatter(
        x=ms["pi_hat"].values,
        y=ms["theta_bar_hat"].values,
        mode="markers",
        marker=dict(
            size=ms["n_total"].values ** 0.4,
            color=color_vals,
            colorscale="RdBu" if color_col else None,
            showscale=bool(color_col),
            colorbar=dict(title="disclosure rate", thickness=12) if color_col else None,
            line=dict(width=0.8, color="white"),
            opacity=0.85,
        ),
        customdata=ms["n_total"].values if "n_total" in ms.columns else None,
        hovertemplate=(
            "Market %{text}<br>"
            "π̂ = %{x:.3f}<br>"
            "θ̄ = %{y:.3f}<br>"
            "N = %{customdata:,.0f}<extra></extra>"
        ),
        text=[str(m) for m in ms.index],
    ))

    fig.update_layout(
        template=_T,
        xaxis_title="π̂_m (share of informed sellers)",
        yaxis_title="θ̄_m (mean EPC quality)",
        height=440,
        title_text="Market heterogeneity: information vs quality composition",
    )
    return fig


# ---------------------------------------------------------------------------
# 10. Renovation thresholds
# ---------------------------------------------------------------------------

def chart_renovation_thresholds(subsidy_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart of renovation threshold R̄_m per market, sorted.
    If S*_m is available (non-NaN), overlay as an additional segment.
    """
    df = subsidy_df.dropna(subset=["R_bar_m"]).sort_values("R_bar_m")
    labels = [str(m) for m in df.index]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels, x=df["R_bar_m"].values,
        orientation="h",
        marker_color=PALETTE["teal"],
        marker_line_width=0,
        name="R̄_m (renovation threshold)",
        hovertemplate="Market %{y}<br>R̄_m = %{x:.4f}<extra></extra>",
    ))

    if "S_star_m" in df.columns and df["S_star_m"].notna().any():
        fig.add_trace(go.Bar(
            y=labels, x=df["S_star_m"].fillna(0).values,
            orientation="h",
            marker_color=PALETTE["amber"],
            marker_line_width=0,
            name="S*_m (optimal subsidy)",
            hovertemplate="Market %{y}<br>S*_m = %{x:.4f}<extra></extra>",
        ))

    fig.update_layout(
        template=_T,
        xaxis_title="Renovation threshold (log-price units)",
        yaxis_title="Market",
        barmode="overlay",
        height=max(380, 22 * len(df) + 100),
        title_text="Renovation thresholds R̄_m and optimal subsidies S*_m",
        legend=dict(orientation="h", y=-0.12, x=0),
    )
    return fig


# ---------------------------------------------------------------------------
# 10. DiD event study — aggregate time series
# ---------------------------------------------------------------------------

def chart_event_study_ts(es_ts: pd.DataFrame) -> go.Figure:
    """
    Two-panel event study chart around the July 2021 DPE reform.

    Left  — EPC quality premium β₁_t = log(ABC) − log(EFG), normalised to k=-1
    Right — Non-disclosure premium Δ_t = log(Ø) − log(EFG), normalised to k=-1

    Both panels show cross-market means with 95% CI bands (1.96 × SE across
    markets). The reform date (k=0) is marked with a vertical dashed line.

    Parameters
    ----------
    es_ts : output of ``aggregate_event_study()``
        Columns: k, epc_premium, epc_ci95, nondiscl_premium, nondiscl_ci95,
                 n_markets, date
    """
    reform_k = 0

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "EPC quality premium  β̂<sub>1,t</sub>  (ABC − EFG)",
            "Non-disclosure premium  Δ̂<sub>t</sub>  (Ø − EFG)",
        ),
        horizontal_spacing=0.12,
    )

    series = [
        ("epc_premium",     "epc_ci95",     PALETTE["teal"],  "β̂₁"),
        ("nondiscl_premium","nondiscl_ci95", PALETTE["coral"], "Δ̂"),
    ]

    for col_idx, (mean_col, ci_col, color, label) in enumerate(series, start=1):
        k    = es_ts["k"].values
        mean = es_ts[mean_col].values
        ci   = es_ts[ci_col].values if ci_col in es_ts.columns else np.zeros_like(mean)
        upper = mean + ci
        lower = mean - ci

        # CI band (filled)
        fig.add_trace(go.Scatter(
            x=np.concatenate([k, k[::-1]]),
            y=np.concatenate([upper, lower[::-1]]),
            fill="toself",
            fillcolor=_hex_to_rgba(color, alpha=0.15),
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
            name=f"{label} 95% CI",
        ), row=1, col=col_idx)

        # Mean line
        fig.add_trace(go.Scatter(
            x=k,
            y=mean,
            mode="lines+markers",
            line=dict(color=color, width=2.2),
            marker=dict(size=5, color=color),
            name=label,
            legendgroup=label,
            showlegend=(col_idx == 1),
            hovertemplate=(
                "k = %{x}<br>"
                + label + " = %{y:.4f}<br>"
                + "95% CI ± " + "<extra></extra>"
            ),
        ), row=1, col=col_idx)

        # Zero baseline
        fig.add_hline(
            y=0, line_dash="dot", line_color=PALETTE["smoke"],
            line_width=1, row=1, col=col_idx,
        )
        # Reform line
        fig.add_vline(
            x=reform_k, line_dash="dash",
            line_color=PALETTE["navy"], line_width=1.5,
            row=1, col=col_idx,
        )
        fig.add_annotation(
            x=reform_k, y=1.02, yref="paper",
            xref=f"x{'' if col_idx == 1 else col_idx}",
            text="Reform (Jul 2021)",
            showarrow=False, xanchor="left", xshift=6,
            font=dict(size=10, color=PALETTE["navy"]),
        )

    fig.update_xaxes(title_text="Months relative to reform", row=1, col=1)
    fig.update_xaxes(title_text="Months relative to reform", row=1, col=2)
    fig.update_yaxes(title_text="Log-price gap (normalised)", row=1, col=1)
    fig.update_layout(
        template=_T,
        title_text="Event study: price gaps around the July 2021 DPE reform",
        height=420,
        legend=dict(orientation="h", y=-0.14, x=0),
    )
    return fig


# ---------------------------------------------------------------------------
# 11. DiD structural estimates — ρ̂_m^DiD and ĉ₀_m distributions
# ---------------------------------------------------------------------------

def chart_did_estimates(es_params) -> go.Figure:
    """
    Two-panel lollipop chart of DiD structural estimates, sorted by ρ̂_m^DiD.

    Left  — ρ̂_m^DiD ∈ [0, 1], coloured teal
    Right — ĉ₀_m (= DiD_delta, log-price units), coloured coral

    Reference lines at cross-market means. Markets where ρ̂_m is NaN (not
    identified: DiD_beta1 ≤ 0) are shown in grey on the right panel only.

    Parameters
    ----------
    es_params : EventStudyParams
        Output of ``estimate_rho_c0()``.
    """
    details = es_params.details.copy()
    details = details.sort_values("rho_hat", na_position="last")

    identified = details[details["rho_hat"].notna()]
    not_ident  = details[details["rho_hat"].isna()]

    markets_id  = [str(m) for m in identified.index]
    rho_vals    = identified["rho_hat"].tolist()
    c0_id_vals  = identified["c0_hat"].tolist()
    c0_na_vals  = not_ident["c0_hat"].tolist()
    markets_na  = [str(m) for m in not_ident.index]

    all_markets = markets_id + markets_na
    all_c0      = c0_id_vals + c0_na_vals

    rho_mean = float(np.nanmean(rho_vals)) if rho_vals else 0.0
    c0_mean  = float(np.nanmean(all_c0))   if all_c0  else 0.0

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "ρ̂<sub>m</sub><sup>DiD</sup> — share of EPC-sensitive buyers",
            "ĉ₀<sub>m</sub><sup>DiD</sup> — hiding cost (log-price units)",
        ),
        horizontal_spacing=0.12,
    )

    # ── ρ̂ lollipops (identified markets only) ────────────────────────────────
    for lbl, val in zip(markets_id, rho_vals):
        fig.add_shape(
            type="line", x0=0, x1=val, y0=lbl, y1=lbl,
            line=dict(color=PALETTE["teal"], width=1.5),
            row=1, col=1,
        )
    fig.add_trace(go.Scatter(
        x=rho_vals, y=markets_id,
        mode="markers",
        marker=dict(color=PALETTE["teal"], size=8, line=dict(color="white", width=1)),
        name="ρ̂<sup>DiD</sup>",
        hovertemplate="<b>Market %{y}</b><br>ρ̂ = %{x:.3f}<extra></extra>",
    ), row=1, col=1)
    fig.add_vline(
        x=rho_mean, line_dash="dash",
        line_color=PALETTE["navy"], line_width=1.5, row=1, col=1,
    )
    fig.add_annotation(
        x=rho_mean, y=1.0, yref="paper",
        text=f"mean {rho_mean:.3f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
    )

    # ── ĉ₀ lollipops — identified (coral) + not identified (grey) ─────────
    for lbl, val in zip(all_markets, all_c0):
        color = PALETTE["coral"] if lbl in set(markets_id) else PALETTE["smoke"]
        fig.add_shape(
            type="line", x0=0, x1=val, y0=lbl, y1=lbl,
            line=dict(color=color, width=1.5),
            row=1, col=2,
        )
    if markets_id:
        fig.add_trace(go.Scatter(
            x=c0_id_vals, y=markets_id,
            mode="markers",
            marker=dict(color=PALETTE["coral"], size=8, line=dict(color="white", width=1)),
            name="ĉ₀ (identified)",
            hovertemplate="<b>Market %{y}</b><br>ĉ₀ = %{x:.4f}<extra></extra>",
        ), row=1, col=2)
    if markets_na:
        fig.add_trace(go.Scatter(
            x=c0_na_vals, y=markets_na,
            mode="markers",
            marker=dict(color=PALETTE["smoke"], size=8, line=dict(color="white", width=1)),
            name="ĉ₀ (ρ not identified)",
            hovertemplate="<b>Market %{y}</b><br>ĉ₀ = %{x:.4f}<extra></extra>",
        ), row=1, col=2)
    fig.add_vline(
        x=c0_mean, line_dash="dash",
        line_color=PALETTE["navy"], line_width=1.5, row=1, col=2,
    )
    fig.add_annotation(
        x=c0_mean, y=1.0, yref="paper",
        xref="x2",
        text=f"mean {c0_mean:.4f}",
        showarrow=False, xanchor="left", xshift=5,
        font=dict(size=10, color=PALETTE["navy"]),
    )

    n = len(all_markets)
    fig.update_xaxes(title_text="ρ̂<sub>m</sub><sup>DiD</sup>", range=[0, 1.05], row=1, col=1)
    fig.update_xaxes(title_text="ĉ₀<sub>m</sub><sup>DiD</sup>", row=1, col=2)
    fig.update_yaxes(tickfont=dict(size=9), row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=2)
    fig.update_layout(
        template=_T,
        height=max(420, 18 * n + 120),
        title_text="DiD structural estimates by market",
        legend=dict(orientation="h", y=-0.08, x=0, font=dict(size=11)),
    )
    return fig
