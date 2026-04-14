from __future__ import annotations
"""
outputs.py
==========
Part 6: Tables and Figures
---------------------------
Produces publication-quality tables and figures following AER replication standards.

All output files are saved to results/tables/ and results/figures/.
LaTeX table output is compatible with the AER style.
"""

import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

logger = logging.getLogger(__name__)

RESULTS_DIR  = Path(__file__).parent.parent / "results"
TABLES_DIR   = RESULTS_DIR / "tables"
FIGURES_DIR  = RESULTS_DIR / "figures"

# Ensure output directories exist
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

PLOTLY_TEMPLATE = "simple_white"


# ---------------------------------------------------------------------------
# Section A — Descriptive statistics table (Table 1 equivalent)
# ---------------------------------------------------------------------------

def table_descriptive_stats(
    df          : pd.DataFrame,
    market_stats: pd.DataFrame,
    save_latex  : bool = True,
) -> pd.DataFrame:
    """
    Table: Summary statistics of listings by group (Table 5 of the paper).

    Rows: four listing groups (Truthful Disclosure, Strategic Hiding, Uninformed, Unverified Disclosers)
    Columns: count, share, mean log price, mean EPC quality (where observed)
    """
    rows = []
    for group_name in ["truthful_disclosure", "strategic_hiding", "uninformed", "unverified_disclosers"]:
        grp = df[df["group"] == group_name]
        rows.append({
            "Group"               : group_name.replace("_", " ").title(),
            "N"                   : len(grp),
            "Share (%)"           : 100 * len(grp) / len(df),
            "Mean log price"      : grp["log_price"].mean(),
            "Std log price"       : grp["log_price"].std(),
            "Mean θ (if observed)": grp["theta"].mean(),
            "Mean d"              : grp["d"].mean(),
            "Mean K"              : grp["K"].mean(),
        })

    tbl = pd.DataFrame(rows).set_index("Group")

    logger.info("=== Table: Descriptive Statistics by Group ===\n" + tbl.round(3).to_string())

    if save_latex:
        path = TABLES_DIR / "table_descriptive_stats.tex"
        tbl.round(3).to_latex(path, float_format="%.3f", escape=True)
        logger.info(f"  → Saved to {path}")

    return tbl


def table_market_stats(
    market_stats: pd.DataFrame,
    save_latex  : bool = True,
) -> pd.DataFrame:
    """
    Table: Market-level directly-measured parameters (directly measured market statistics, estimation appendix forthcoming).

    Rows: markets
    Columns: π̂_m, θ̂_m, σ̂_{0,m}, σ̂_{1,m}, Δ̄_m (raw premium)
    """
    cols = ["pi_hat", "theta_bar_hat", "sigma_0_hat", "sigma_1_hat", "delta_bar_raw"]
    labels = {
        "pi_hat"       : "π̂_m  (info prevalence)",
        "theta_bar_hat": "θ̂_m  (avg quality)",
        "sigma_0_hat"  : "σ̂_{0,m} (low hide rate)",
        "sigma_1_hat"  : "σ̂_{1,m} (high hide rate)",
        "delta_bar_raw": "Δ̄_m (raw premium)",
    }
    tbl = market_stats[[c for c in cols if c in market_stats.columns]].rename(columns=labels)

    logger.info("=== Table: Market-Level Statistics ===\n" + tbl.round(4).describe().to_string())

    if save_latex:
        path = TABLES_DIR / "table_market_stats.tex"
        tbl.round(4).to_latex(path, float_format="%.4f")
        logger.info(f"  → Saved to {path}")

    return tbl


# ---------------------------------------------------------------------------
# Section B — Main estimates table
# ---------------------------------------------------------------------------

def table_estimates(
    msm_result   : object,
    se_dict      : dict | None = None,
    direct_rho   : pd.DataFrame | None = None,
    save_latex   : bool = True,
) -> pd.DataFrame:
    """
    Table: Structural parameter estimates (ρ̂_m, ĉ₀) with standard errors.

    Format follows AER conventions: coefficient in row 1, SE in parentheses row 2.
    """
    rho_vals  = list(msm_result.rho_hat.values())
    mean_rho  = np.mean(rho_vals)
    std_rho   = np.std(rho_vals)
    c0_vals   = list(msm_result.c0_hat.values())
    mean_c0   = np.mean(c0_vals)
    std_c0    = np.std(c0_vals)

    mean_c0_se = (np.mean(list(se_dict["c0_se"].values()))
                  if se_dict and isinstance(se_dict.get("c0_se"), dict) else np.nan)

    rows = [
        {
            "Parameter"  : "Mean ρ̂  (buyer sensitivity)",
            "Estimate"   : f"{mean_rho:.4f}",
            "Std Dev"    : f"({std_rho:.4f})",
            "SE (boot)"  : f"({se_dict['rho_se_mean']:.4f})" if se_dict else "—",
        },
        {
            "Parameter"  : "Mean ĉ₀_m  (hiding cost)",
            "Estimate"   : f"{mean_c0:.6f}",
            "Std Dev"    : f"({std_c0:.6f})",
            "SE (boot)"  : f"({mean_c0_se:.6f})" if not np.isnan(mean_c0_se) else "—",
        },
        {
            "Parameter"  : "Q*  (objective at min.)",
            "Estimate"   : f"{msm_result.Q_star:.6f}",
            "Std Dev"    : "—",
            "SE (boot)"  : "—",
        },
        {
            "Parameter"  : "N markets",
            "Estimate"   : f"{msm_result.n_markets}",
            "Std Dev"    : "—",
            "SE (boot)"  : "—",
        },
    ]

    # Count equilibrium regimes
    eq_counts = pd.Series(list(msm_result.eq_types.values())).value_counts()
    for eq_type, count in eq_counts.items():
        rows.append({
            "Parameter" : f"  Markets in {eq_type.replace('_', ' ')}",
            "Estimate"  : f"{count}",
            "Std Dev"   : "—",
            "SE (boot)" : "—",
        })

    tbl = pd.DataFrame(rows).set_index("Parameter")

    logger.info("=== Table: Structural Estimates ===\n" + tbl.to_string())

    if save_latex:
        path = TABLES_DIR / "table_estimates.tex"
        tbl.to_latex(path, escape=True)
        logger.info(f"  → Saved to {path}")

    return tbl


def table_moment_fit(
    data_moments : dict,
    model_moments: dict,
    save_latex   : bool = True,
) -> pd.DataFrame:
    """
    Table: Data vs model-implied moments — Table 6 of the paper.

    Shows how well the model fits each moment across markets.
    """
    rows = []
    for m in sorted(data_moments.keys()):
        dm = data_moments[m]
        mm = model_moments.get(m)
        rows.append({
            "Market"    : m,
            "m₁ data"  : dm.m1,
            "m₁ model" : mm.m1_model if mm else np.nan,
            "m₁ diff"  : dm.m1 - mm.m1_model if mm else np.nan,
            "m₂ data"  : dm.m2,
            "m₂ model" : mm.m2_model if mm else np.nan,
            "m₂ diff"  : dm.m2 - mm.m2_model if mm else np.nan,
            "m₃ data"  : dm.m3,
            "m₃ model" : mm.m3_model if mm else np.nan,
            "m₃ diff"  : dm.m3 - mm.m3_model if mm else np.nan,
            "m₄ data"  : dm.m4,
            "m₄ model" : mm.m4_model if mm else np.nan,
            "m₄ diff"  : dm.m4 - mm.m4_model if mm else np.nan,
            "Eq. type"  : mm.eq_type if mm else "—",
        })

    tbl = pd.DataFrame(rows).set_index("Market")

    # Summary row
    numeric_cols = [c for c in tbl.columns if c != "Eq. type"]
    summary = tbl[numeric_cols].mean().rename("Mean")
    tbl_out = pd.concat([tbl, pd.DataFrame([summary])])

    logger.info("=== Table: Moment Fit ===\n" + tbl_out.round(4).to_string())

    if save_latex:
        path = TABLES_DIR / "table_moment_fit.tex"
        tbl_out.round(4).to_latex(path, float_format="%.4f")
        logger.info(f"  → Saved to {path}")

    return tbl_out


# ---------------------------------------------------------------------------
# Section C — Figures
# ---------------------------------------------------------------------------

def figure_premium_by_market(
    market_stats: pd.DataFrame,
    rho_hat     : dict | None = None,
    save        : bool = True,
) -> go.Figure:
    """
    Figure: Non-disclosure premium across markets, sorted by π̂_m.

    Key prediction (Proposition (prop:pi)): premium decreasing in π.
    Secondary pattern: premium increasing in ρ̂ (Proposition (prop:rho)).
    """
    df_plot = market_stats[["pi_hat", "delta_bar_raw"]].dropna().copy()
    df_plot = df_plot.sort_values("pi_hat")

    if rho_hat is not None:
        df_plot["rho_hat"] = df_plot.index.map(rho_hat)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Panel A: Premium vs. Information Prevalence",
                        "Panel B: Distribution of Non-Disclosure Premium"),
    )

    # Panel A: scatter premium vs π̂, coloured by ρ̂
    if "rho_hat" in df_plot.columns:
        scatter = go.Scatter(
            x=df_plot["pi_hat"],
            y=df_plot["delta_bar_raw"],
            mode="markers",
            marker=dict(
                color=df_plot["rho_hat"],
                colorscale="RdYlBu_r",
                size=8,
                line=dict(width=0.5, color="black"),
                colorbar=dict(title="ρ̂_m", x=0.44),
                showscale=True,
            ),
            hovertemplate="π̂=%{x:.3f}<br>Δ̄=%{y:.3f}<br>ρ̂=%{marker.color:.3f}<extra></extra>",
            showlegend=False,
        )
    else:
        scatter = go.Scatter(
            x=df_plot["pi_hat"],
            y=df_plot["delta_bar_raw"],
            mode="markers",
            marker=dict(color="steelblue", size=8, line=dict(width=0.5, color="black")),
            showlegend=False,
        )
    fig.add_trace(scatter, row=1, col=1)

    # LOWESS trend line
    from statsmodels.nonparametric.smoothers_lowess import lowess
    z = lowess(df_plot["delta_bar_raw"].values, df_plot["pi_hat"].values, frac=0.5)
    fig.add_trace(
        go.Scatter(
            x=z[:, 0], y=z[:, 1],
            mode="lines",
            line=dict(color="black", dash="dash", width=2),
            name="LOWESS",
        ),
        row=1, col=1,
    )
    fig.add_hline(y=0, line=dict(color="gray", dash="dot", width=1), row=1, col=1)

    # Panel B: histogram of premiums
    fig.add_trace(
        go.Histogram(
            x=df_plot["delta_bar_raw"],
            nbinsx=20,
            marker=dict(color="steelblue", line=dict(color="white", width=0.5)),
            opacity=0.85,
            name="Premium distribution",
            showlegend=False,
        ),
        row=1, col=2,
    )
    mean_prem = df_plot["delta_bar_raw"].mean()
    fig.add_vline(
        x=mean_prem, line=dict(color="black", dash="dash", width=1.5),
        annotation_text=f"Mean = {mean_prem:.3f}", annotation_position="top right",
        row=1, col=2,
    )
    fig.add_vline(
        x=0, line=dict(color="red", dash="dot", width=1.2),
        annotation_text="Zero premium",
        row=1, col=2,
    )

    fig.update_xaxes(title_text="π̂_m (share of informed sellers)", row=1, col=1)
    fig.update_yaxes(title_text="Δ̄_m (non-disclosure premium, log points)", row=1, col=1)
    fig.update_xaxes(title_text="Δ̄_m (non-disclosure premium, log points)", row=1, col=2)
    fig.update_yaxes(title_text="Number of markets", row=1, col=2)
    fig.update_layout(template=PLOTLY_TEMPLATE, width=1100, height=480)

    if save:
        path = FIGURES_DIR / "figure_premium_by_market.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")

    return fig


def figure_rho_distribution(
    rho_hat    : dict,
    market_stats: pd.DataFrame,
    save       : bool = True,
) -> go.Figure:
    """
    Figure: Distribution of ρ̂_m across markets, and scatter vs π̂_m.

    According to Proposition (prop:rho), higher ρ pushes toward partial separation.
    We expect markets with high ρ to also display large hiding premiums.
    """
    rho_series = pd.Series(rho_hat).rename("rho_hat")
    df_plot    = market_stats[["pi_hat", "theta_bar_hat"]].join(rho_series).dropna()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Panel A: Distribution of ρ̂_m",
                        "Panel B: ρ̂_m vs. π̂_m"),
    )

    # Panel A: histogram of ρ̂
    mean_rho = df_plot["rho_hat"].mean()
    fig.add_trace(
        go.Histogram(
            x=df_plot["rho_hat"],
            nbinsx=20,
            marker=dict(color="coral", line=dict(color="white", width=0.5)),
            opacity=0.85,
            showlegend=False,
        ),
        row=1, col=1,
    )
    fig.add_vline(
        x=mean_rho, line=dict(color="black", dash="dash", width=1.5),
        annotation_text=f"Mean ρ̂ = {mean_rho:.3f}", annotation_position="top right",
        row=1, col=1,
    )

    # Panel B: scatter ρ̂ vs π̂
    fig.add_trace(
        go.Scatter(
            x=df_plot["pi_hat"],
            y=df_plot["rho_hat"],
            mode="markers",
            marker=dict(color="coral", size=8, line=dict(width=0.5, color="black")),
            hovertemplate="π̂=%{x:.3f}<br>ρ̂=%{y:.3f}<extra></extra>",
            showlegend=False,
        ),
        row=1, col=2,
    )
    fig.add_annotation(
        text="Each dot = one market",
        xref="x2 domain", yref="y2 domain",
        x=0.05, y=0.95, showarrow=False,
        font=dict(size=9, color="gray"),
    )

    fig.update_xaxes(title_text="ρ̂_m (share of EPC-sensitive buyers)", row=1, col=1)
    fig.update_yaxes(title_text="Number of markets", row=1, col=1)
    fig.update_xaxes(title_text="π̂_m (share of informed sellers)", row=1, col=2)
    fig.update_yaxes(title_text="ρ̂_m (share of EPC-sensitive buyers)", row=1, col=2)
    fig.update_layout(template=PLOTLY_TEMPLATE, width=1100, height=480)

    if save:
        path = FIGURES_DIR / "figure_rho_distribution.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")

    return fig


def figure_equilibrium_phase_diagram(
    pi_grid    : np.ndarray | None = None,
    c0_hat     : float = 0.03,
    rho_vals   : list[float] | None = None,
    theta_bar  : float = 0.40,
    beta_1     : float = 0.06,
    scale      : float = 1.0,
    save       : bool = True,
) -> go.Figure:
    """
    Figure: Equilibrium phase diagram in (π, ρ) space — equilibrium table in Proposition (prop:equilibrium).

    For fixed c₀, θ̄, plots the regions of:
      - Full unraveling    (c₀ > Δ(θ̄))
      - Partial separation (c₀ < Δ(e(1)))
      - Mixed strategy     (in between)
    """
    from .model import ValuationParams, solve_equilibrium

    if pi_grid is None:
        pi_grid  = np.linspace(0.05, 0.95, 50)
    if rho_vals is None:
        rho_vals = [0.1, 0.3, 0.5, 0.7]

    eq_numeric_map = {"full_unraveling": 0, "mixed_strategy": 1, "partial_separation": 2}
    colors = px.colors.qualitative.Set1

    fig = go.Figure()

    for i, rho in enumerate(rho_vals):
        eq_types = []
        for pi in pi_grid:
            params = ValuationParams(
                beta_0=0.0, beta_1=beta_1, X_beta_X=0.0,
                v0_offset=-beta_1 * 0.5,
                scale=scale,
            )
            eq = solve_equilibrium(rho, c0_hat, pi, theta_bar, params)
            eq_types.append(eq.eq_type)

        numeric = np.array([eq_numeric_map[t] for t in eq_types], dtype=float)
        # small vertical offset by rho for legibility
        numeric_offset = numeric + rho * 0.05

        fig.add_trace(go.Scatter(
            x=pi_grid,
            y=numeric_offset,
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=2),
            name=f"ρ = {rho:.1f}",
            hovertemplate=f"ρ={rho:.1f}<br>π=%{{x:.2f}}<br>regime=%{{text}}<extra></extra>",
            text=eq_types,
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Equilibrium Regime (c₀ = {c0_hat:.3f}, θ̄ = {theta_bar})",
        xaxis_title="π (share of informed sellers)",
        yaxis=dict(
            tickvals=[0, 1, 2],
            ticktext=["Full Unraveling", "Mixed Strategy", "Partial Separation"],
        ),
        legend_title="ρ (buyer sensitivity)",
        width=750,
        height=520,
    )

    if save:
        path = FIGURES_DIR / "figure_equilibrium_phase.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")

    return fig


def figure_subsidies(
    subsidy_df: pd.DataFrame,
    save      : bool = True,
) -> go.Figure | None:
    """
    Figure: Optimal subsidies across markets — estimation appendix forthcoming.

    Shows the distribution of S*_m and its relationship to market composition.
    According to the policy extension results, S* is decreasing in π and ρ,
    and increasing in actual renovation costs R̂.
    """
    df = subsidy_df.dropna(subset=["S_star_m"])

    if len(df) == 0:
        logger.info("[figure_subsidies] No subsidy data available (R̂_m not yet provided).")
        return None

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Panel A: Distribution of Optimal Subsidies",
                        "Panel B: Optimal Subsidy vs. π̂_m"),
    )

    # Panel A: histogram of S*
    fig.add_trace(
        go.Histogram(
            x=df["S_star_m"],
            nbinsx=20,
            marker=dict(color="seagreen", line=dict(color="white", width=0.5)),
            opacity=0.85,
            showlegend=False,
        ),
        row=1, col=1,
    )

    # Panel B: scatter S* vs π̂
    fig.add_trace(
        go.Scatter(
            x=df["pi_m"],
            y=df["S_star_m"],
            mode="markers",
            marker=dict(color="seagreen", size=8, line=dict(width=0.5, color="black")),
            hovertemplate="π̂=%{x:.3f}<br>S*=%{y:.4f}<extra></extra>",
            showlegend=False,
        ),
        row=1, col=2,
    )
    fig.add_annotation(
        text="Prediction: slope < 0",
        xref="x2 domain", yref="y2 domain",
        x=0.05, y=0.95, showarrow=False,
        font=dict(size=9, color="gray"),
    )

    fig.update_xaxes(title_text="S*_m (optimal subsidy per market)", row=1, col=1)
    fig.update_yaxes(title_text="Number of markets", row=1, col=1)
    fig.update_xaxes(title_text="π̂_m (share of informed sellers)", row=1, col=2)
    fig.update_yaxes(title_text="S*_m (optimal subsidy)", row=1, col=2)
    fig.update_layout(template=PLOTLY_TEMPLATE, width=1100, height=480)

    if save:
        path = FIGURES_DIR / "figure_subsidies.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")

    return fig


def figure_belief_function(
    pi_vals    : list[float] | None = None,
    theta_bar  : float = 0.40,
    save       : bool = True,
) -> go.Figure:
    """
    Figure: Belief function e(σ₀) for different values of π — Eq. (eq:belief_simplified).

    Illustrates how pool quality depends on the hiding rate, and how
    higher π amplifies adverse selection in the non-disclosing pool.
    """
    from .model import belief_function

    if pi_vals is None:
        pi_vals = [0.2, 0.4, 0.6, 0.8]

    sigma_grid = np.linspace(0, 1, 200)
    colors     = px.colors.qualitative.Set1

    fig = go.Figure()

    for i, pi in enumerate(pi_vals):
        beliefs = [belief_function(s, pi, theta_bar) for s in sigma_grid]
        fig.add_trace(go.Scatter(
            x=sigma_grid,
            y=beliefs,
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=2),
            name=f"π = {pi:.1f}",
            hovertemplate="σ₀=%{x:.2f}<br>e(σ₀)=%{y:.4f}<extra></extra>",
        ))

    fig.add_hline(
        y=theta_bar,
        line=dict(color="black", dash="dash", width=1),
        annotation_text=f"θ̄ = {theta_bar}",
        annotation_position="right",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Belief Function (Eq. (eq:belief_simplified)): Pool Quality vs. Hiding Rate",
        xaxis_title="σ₀ (hiding rate of informed low-quality sellers)",
        yaxis_title="e(σ₀) = E[θ | d=0] (buyer belief about pool quality)",
        yaxis=dict(range=[0, theta_bar * 1.05]),
        legend_title="π (info prevalence)",
        width=700,
        height=500,
    )

    if save:
        path = FIGURES_DIR / "figure_belief_function.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")

    return fig


def produce_all_outputs(
    df            : pd.DataFrame,
    market_stats  : pd.DataFrame,
    data_moments  : dict,
    msm_result    : object,
    hedonic_params: object,
    subsidy_df    : pd.DataFrame | None = None,
    se_dict       : dict | None = None,
) -> None:
    """
    Produce all tables and figures in one call.
    """
    logger.info("=" * 60)
    logger.info("PRODUCING TABLES AND FIGURES")
    logger.info("=" * 60)

    # Tables
    table_descriptive_stats(df, market_stats)
    table_market_stats(market_stats)
    table_estimates(msm_result, se_dict=se_dict)
    table_moment_fit(data_moments, msm_result.model_moments)

    # Figures
    figure_belief_function(theta_bar=float(market_stats["theta_bar_hat"].mean()))
    figure_premium_by_market(market_stats, rho_hat=msm_result.rho_hat)
    figure_rho_distribution(msm_result.rho_hat, market_stats)
    figure_equilibrium_phase_diagram(
        c0_hat    = float(np.mean(list(msm_result.c0_hat.values()))),
        theta_bar = float(market_stats["theta_bar_hat"].mean()),
        beta_1    = hedonic_params.beta_1,
        scale     = list(msm_result.model_moments.values())[0].e_star,  # proxy
    )
    if subsidy_df is not None:
        figure_subsidies(subsidy_df)

    logger.info(f"[outputs] All results saved to {RESULTS_DIR}")
