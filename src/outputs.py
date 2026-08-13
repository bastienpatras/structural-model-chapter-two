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

# Regime → display name and color. Codebase regime names map to paper labels:
#   "full_unraveling"     ↔ Cost-Deterred Hiding (CDH)
#   "mixed_strategy"      ↔ Partial Pooling      (PP)
#   "partial_separation"  ↔ Complete Adverse Selection (CAS)
REGIME_LABELS = {
    "mixed_strategy"    : "Partial Pooling",
    "full_unraveling"   : "Cost-Deterred Hiding",
    "partial_separation": "Complete Adverse Selection",
}
REGIME_COLORS = {
    "mixed_strategy"    : "#1D3461",   # navy
    "full_unraveling"   : "#1BA3C6",   # teal
    "partial_separation": "#d01c32",   # SPred (paper red)
}
APT_COLOR = "#1D3461"   # navy
HSE_COLOR = "#d01c32"   # SPred


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
    # bootstrap_se() returns per-market dicts (rho_se, c0_se), not scalars.
    # Resolve defensively so either shape works.
    def _mean_se(key):
        if not se_dict:
            return np.nan
        v = se_dict.get(key)
        if isinstance(v, dict):
            return float(np.nanmean(list(v.values()))) if v else np.nan
        if isinstance(v, (int, float)):
            return float(v)
        return np.nan
    mean_rho_se = _mean_se("rho_se")

    rows = [
        {
            "Parameter"  : "Mean ρ̂  (buyer sensitivity)",
            "Estimate"   : f"{mean_rho:.4f}",
            "Std Dev"    : f"({std_rho:.4f})",
            "SE (boot)"  : (f"({mean_rho_se:.4f})"
                            if not np.isnan(mean_rho_se) else "n/a"),
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


def table_market_estimates(
    data_moments  : dict,
    model_moments : dict,
    msm_result    : object,
    did_estimates : object | None = None,
    save_latex    : bool = True,
) -> pd.DataFrame:
    """
    Table: Market-level structural estimates — Table 6 of the paper.

    Columns (per market):
      β̂₁_m  : DiD EPC quality premium (first-stage input)
      Δ̂_m   : DiD non-disclosure premium (first-stage input; upper bound on ĉ₀_m)
      σ̂₀_m  : hiding rate, informed low-quality sellers (active moment)
      ê*_m   : equilibrium pool quality (from σ̂₀_m via belief function)
      ρ̂_m   : estimated EPC-sensitive buyer share (from DiD, two-step)
      ĉ₀_m  : estimated hiding cost (inverted from σ̂₀_m)
      σ̂₁_m  : hiding rate, informed high-quality sellers (model validation: should ≈ 0)
      Regime : equilibrium regime
    """
    did_df = did_estimates.did if did_estimates is not None else None

    rows = []
    for m in sorted(data_moments.keys()):
        dm = data_moments[m]
        mm = model_moments.get(m)
        rows.append({
            "Market"                              : m,
            r"$\hat{\beta}_{1,m}$"               : float(did_df.loc[m, "DiD_beta1"])
                                                   if did_df is not None and m in did_df.index else np.nan,
            r"$\hat{\Delta}_m$"                  : float(did_df.loc[m, "DiD_delta"])
                                                   if did_df is not None and m in did_df.index else np.nan,
            r"$\hat{\sigma}_{0,m}$"              : dm.m4,
            r"$\hat{e}^*_m$"                     : mm.e_star if mm else np.nan,
            r"$\hat{\rho}_m$"                    : msm_result.rho_hat.get(m, np.nan),
            r"$\hat{c}_{0,m}$"                   : msm_result.c0_hat.get(m, np.nan),
            r"$\hat{\sigma}_{1,m}$"              : dm.m5,
            "Regime"                              : mm.eq_type if mm else "---",
        })

    tbl = pd.DataFrame(rows).set_index("Market")

    numeric_cols = [c for c in tbl.columns if c != "Regime"]
    summary = tbl[numeric_cols].mean().rename("Mean")
    tbl_out = pd.concat([tbl, pd.DataFrame([summary])])

    logger.info("=== Table: Market Estimates ===\n" + tbl_out.round(4).to_string())

    if save_latex:
        path = TABLES_DIR / "table_market_estimates.tex"
        tbl_out.round(4).to_latex(path, float_format="%.4f", escape=False)
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


def _market_estimates_from_grid(grid_df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse a long-format subsidy grid back to one row per market (R̄_m is
    invariant across cost-grid rows). Used by `export_market_estimates`.
    """
    if grid_df.empty:
        return grid_df.copy()
    keep = [
        "market_id",
        "R_bar_log_pts", "R_bar_eur_per_m2",
        "price_per_m2_eur", "median_area_m2", "n_listings",
        "regime", "rho_m", "c0_m", "pi_m", "theta_bar_m",
        "sigma_0_m", "e_star_m", "beta_1_m",
    ]
    available = [c for c in keep if c in grid_df.columns]
    return grid_df[available].drop_duplicates(subset=["market_id"]).reset_index(drop=True)


def export_market_estimates(
    grid_df        : pd.DataFrame,
    summary_df     : pd.DataFrame,
    output_dir     : str | Path,
    budget_df      : pd.DataFrame | None = None,
    centroids_df   : pd.DataFrame | None = None,
) -> None:
    """
    Persist per-market calibrated parameters and the subsidy grid as CSVs.

    Output files (under `output_dir`):
      - market_estimates.csv  (one row per market)
      - subsidy_grid.csv      (long format, one row per market × cost_per_m2)
      - subsidy_summary.csv   (per cost-scheme aggregates incl. regime breakdown)
      - budget_grid.csv       (weighted total per cost-scheme, if budget_df given)
      - market_centroids.csv  (if centroids_df given)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    me_path = output_dir / "market_estimates.csv"
    _market_estimates_from_grid(grid_df).to_csv(me_path, index=False)
    logger.info(f"  → wrote {me_path}  (N={len(_market_estimates_from_grid(grid_df))})")

    sg_path = output_dir / "subsidy_grid.csv"
    grid_df.to_csv(sg_path, index=False)
    logger.info(f"  → wrote {sg_path}  (rows={len(grid_df)})")

    ss_path = output_dir / "subsidy_summary.csv"
    summary_df.to_csv(ss_path, index=False)
    logger.info(f"  → wrote {ss_path}  (rows={len(summary_df)})")

    if budget_df is not None:
        bg_path = output_dir / "budget_grid.csv"
        budget_df.to_csv(bg_path, index=False)
        logger.info(f"  → wrote {bg_path}")

    if centroids_df is not None:
        cc_path = output_dir / "market_centroids.csv"
        centroids_df.to_csv(cc_path)
        logger.info(f"  → wrote {cc_path}")


# ---------------------------------------------------------------------------
# Section J — Renovation subsidy figures and tables
# ---------------------------------------------------------------------------

def _filter_canonical(grid_df: pd.DataFrame, cost_per_m2: float) -> pd.DataFrame:
    """Pick the grid row with `cost_per_m2` closest to the requested value."""
    if grid_df.empty:
        return grid_df
    available = grid_df["cost_per_m2"].unique()
    pick      = float(min(available, key=lambda x: abs(x - cost_per_m2)))
    return grid_df[grid_df["cost_per_m2"] == pick].copy()


def figure_renovation_threshold_distribution(
    grid_apt : pd.DataFrame | None,
    grid_hse : pd.DataFrame | None,
    save     : bool = True,
) -> go.Figure | None:
    """
    Histogram of the renovation threshold R̄_m across markets, by property type.
    Bars coloured by equilibrium regime (PP / CDH / CAS).
    """
    parts = []
    if grid_apt is not None and not grid_apt.empty:
        parts.append(("Apartments", _market_estimates_from_grid(grid_apt)))
    if grid_hse is not None and not grid_hse.empty:
        parts.append(("Houses", _market_estimates_from_grid(grid_hse)))

    if not parts:
        return None

    fig = make_subplots(rows=1, cols=len(parts),
                        subplot_titles=[p[0] for p in parts],
                        shared_yaxes=False)

    for col, (label, df) in enumerate(parts, start=1):
        for reg, sub in df.groupby("regime"):
            fig.add_trace(
                go.Histogram(
                    x         = sub["R_bar_eur_per_m2"],
                    name      = REGIME_LABELS.get(reg, reg),
                    marker    = dict(color=REGIME_COLORS.get(reg, "#888"),
                                      line=dict(color="white", width=0.5)),
                    opacity   = 0.85,
                    nbinsx    = 20,
                    legendgroup = reg,
                    showlegend  = (col == 1),
                ),
                row=1, col=col,
            )
        fig.update_xaxes(title_text="R̄_m (€/m² equivalent)", row=1, col=col)
        fig.update_yaxes(title_text="# markets" if col == 1 else "", row=1, col=col)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="stack",
        width=1100, height=460,
        legend=dict(orientation="h", y=-0.18),
    )

    if save:
        path = FIGURES_DIR / "figure_renovation_threshold.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")
    return fig


def figure_subsidy_grid(
    grid_apt : pd.DataFrame | None,
    grid_hse : pd.DataFrame | None,
    save     : bool = True,
) -> go.Figure | None:
    """
    Small-multiples histogram of S*_m across markets, in €/m².
    Rows: property type. Columns: cost_per_m2 grid values (ascending).
    Vertical line at S*=0 marks markets that need no subsidy.
    """
    panels = []
    if grid_apt is not None and not grid_apt.empty:
        panels.append(("Apartments", APT_COLOR, grid_apt))
    if grid_hse is not None and not grid_hse.empty:
        panels.append(("Houses",     HSE_COLOR, grid_hse))

    if not panels:
        return None

    cost_values = sorted({
        float(c) for _, _, g in panels for c in g["cost_per_m2"].unique()
    })
    n_rows = len(panels)
    n_cols = len(cost_values)

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[f"R̂ = {c:.0f} €/m²" for c in cost_values] * 1,
        row_titles=[p[0] for p in panels],
        shared_xaxes="columns", shared_yaxes=False,
        horizontal_spacing=0.04, vertical_spacing=0.13,
    )

    for r, (label, color, grid) in enumerate(panels, start=1):
        for c, ch in enumerate(cost_values, start=1):
            sub = grid[np.isclose(grid["cost_per_m2"], ch)]
            if sub.empty:
                continue
            fig.add_trace(
                go.Histogram(
                    x       = sub["S_star_eur_per_m2"],
                    marker  = dict(color=color, line=dict(color="white", width=0.4)),
                    opacity = 0.85,
                    nbinsx  = 18,
                    showlegend = False,
                ),
                row=r, col=c,
            )
            fig.add_vline(x=0, line=dict(color="black", dash="dot", width=1),
                          row=r, col=c)
            fig.update_xaxes(title_text="S*_m (€/m²)" if r == n_rows else "",
                             row=r, col=c)
            if c == 1:
                fig.update_yaxes(title_text="# markets", row=r, col=c)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        width=240*n_cols + 80, height=320*n_rows + 90,
        title=dict(text="Minimum incentive-compatible subsidy S*_m across markets (€/m²), by renovation cost scheme",
                   x=0.02, xanchor="left"),
    )

    if save:
        path = FIGURES_DIR / "figure_subsidy_grid.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")
    return fig


def figure_threshold_vs_beta1(
    grid_apt : pd.DataFrame | None,
    grid_hse : pd.DataFrame | None,
    save     : bool = True,
) -> go.Figure | None:
    """
    Scatter R̄_m vs β̂_{1,m}, colored by regime. 45° line as reference.
    PP markets should sit close to the 45° line (verified-quality premium collapse).
    """
    parts = []
    if grid_apt is not None and not grid_apt.empty:
        parts.append(("Apartments", _market_estimates_from_grid(grid_apt)))
    if grid_hse is not None and not grid_hse.empty:
        parts.append(("Houses", _market_estimates_from_grid(grid_hse)))

    if not parts:
        return None

    fig = make_subplots(rows=1, cols=len(parts),
                        subplot_titles=[p[0] for p in parts],
                        horizontal_spacing=0.08)

    all_vals = pd.concat([p[1] for p in parts])
    lo = float(min(all_vals["R_bar_log_pts"].min(), all_vals["beta_1_m"].min(), 0.0))
    hi = float(max(all_vals["R_bar_log_pts"].max(), all_vals["beta_1_m"].max()) * 1.05)

    for col, (label, df) in enumerate(parts, start=1):
        for reg, sub in df.groupby("regime"):
            fig.add_trace(
                go.Scatter(
                    x = sub["beta_1_m"], y = sub["R_bar_log_pts"],
                    mode="markers",
                    name=REGIME_LABELS.get(reg, reg),
                    marker=dict(color=REGIME_COLORS.get(reg, "#888"),
                                size=9, line=dict(width=0.5, color="black")),
                    legendgroup=reg, showlegend=(col == 1),
                    hovertemplate=("market=%{customdata}<br>"
                                   "β̂₁=%{x:.4f}<br>R̄=%{y:.4f}<extra></extra>"),
                    customdata=sub["market_id"],
                ),
                row=1, col=col,
            )
        fig.add_trace(
            go.Scatter(x=[lo, hi], y=[lo, hi],
                       mode="lines", line=dict(color="gray", dash="dash"),
                       name="45°", showlegend=(col == 1), legendgroup="ref"),
            row=1, col=col,
        )
        fig.update_xaxes(title_text="β̂₁ (verified-quality premium)",
                         range=[lo, hi], row=1, col=col)
        fig.update_yaxes(title_text="R̄_m (renovation threshold)" if col == 1 else "",
                         range=[lo, hi], row=1, col=col)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        width=1100, height=520,
        legend=dict(orientation="h", y=-0.18),
    )

    if save:
        path = FIGURES_DIR / "figure_threshold_vs_beta1.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")
    return fig


def _jitter_centroids(df: pd.DataFrame, scale: float = 0.18) -> pd.DataFrame:
    """
    Deterministic radial jitter for centroids that share coordinates (e.g.,
    multiple markets sharing a département centroid). The jitter is keyed on
    `market_id` so re-runs are reproducible.
    """
    if df.empty or "market_id" not in df.columns:
        return df
    df = df.copy()
    key = df.groupby(["lat", "lon"]).cumcount()
    n_per_cell = df.groupby(["lat", "lon"])["market_id"].transform("size")
    angle = 2 * np.pi * key / n_per_cell.clip(lower=1)
    radius = scale * np.where(n_per_cell > 1, np.sqrt(key + 1) / np.sqrt(n_per_cell), 0.0)
    df["lat"] = df["lat"] + radius * np.cos(angle)
    df["lon"] = df["lon"] + radius * np.sin(angle)
    return df


def figure_subsidy_bubble_map(
    grid_apt      : pd.DataFrame | None,
    grid_hse      : pd.DataFrame | None,
    centroids_apt : pd.DataFrame | None,
    centroids_hse : pd.DataFrame | None,
    cost_per_m2_apt : float = 500.0,
    cost_per_m2_hse : float = 500.0,
    save          : bool = True,
) -> go.Figure | None:
    """
    Two-panel bubble map of S*_m (in €/m²) at one canonical cost scheme per
    property type. `go.Scattergeo` with mercator centred on France. Bubble
    color and size encode S*_m; markets with S* = 0 are shown small in grey.
    """
    panels = []
    if grid_apt is not None and centroids_apt is not None:
        panels.append(("Apartments", grid_apt, centroids_apt, cost_per_m2_apt))
    if grid_hse is not None and centroids_hse is not None:
        panels.append(("Houses", grid_hse, centroids_hse, cost_per_m2_hse))

    if not panels:
        return None

    fig = make_subplots(
        rows=1, cols=len(panels),
        specs=[[{"type": "geo"} for _ in panels]],
        subplot_titles=[f"{name} (R̂ = {c:.0f} €/m²)" for name, _, _, c in panels],
        horizontal_spacing=0.02,
    )

    for col, (label, grid, centroids, ch) in enumerate(panels, start=1):
        canonical = _filter_canonical(grid, ch)
        merged = canonical.merge(
            centroids.reset_index(), on="market_id", how="inner",
        )
        if merged.empty:
            continue
        merged = _jitter_centroids(merged)

        s   = merged["S_star_eur_per_m2"].fillna(0.0).to_numpy()
        pos = s > 0
        size_max = max(float(s.max()), 1e-9)
        sizes = 6 + 30 * (s / size_max)

        # zero-subsidy markets: small grey dots
        if (~pos).any():
            sub = merged.loc[~pos]
            fig.add_trace(
                go.Scattergeo(
                    lon=sub["lon"], lat=sub["lat"],
                    mode="markers",
                    marker=dict(size=6, color="#bbbbbb",
                                line=dict(width=0.4, color="white"),
                                opacity=0.6),
                    name="S* = 0",
                    legendgroup="zero", showlegend=(col == 1),
                    hovertemplate=("%{customdata}<br>S*=0<extra></extra>"),
                    customdata=sub["market_id"],
                ),
                row=1, col=col,
            )

        # positive-subsidy markets: colored by S*
        if pos.any():
            sub = merged.loc[pos]
            fig.add_trace(
                go.Scattergeo(
                    lon=sub["lon"], lat=sub["lat"],
                    mode="markers",
                    marker=dict(
                        size=sizes[pos],
                        color=sub["S_star_eur_per_m2"],
                        colorscale="Reds",
                        cmin=0.0,
                        cmax=float(s.max()),
                        showscale=(col == len(panels)),
                        colorbar=dict(title="S* (€/m²)"),
                        line=dict(width=0.5, color="black"),
                        opacity=0.9,
                    ),
                    name="S* > 0",
                    legendgroup="pos", showlegend=(col == 1),
                    hovertemplate=(
                        "market=%{customdata[0]}<br>"
                        "S*=%{marker.color:.0f} €/m²<extra></extra>"
                    ),
                    customdata=sub[["market_id"]],
                ),
                row=1, col=col,
            )

        fig.update_geos(
            projection_type="mercator",
            center=dict(lat=46.5, lon=2.5),
            lonaxis=dict(range=[-5.5, 10.5]),
            lataxis=dict(range=[41.0, 51.5]),
            showcountries=True, countrycolor="#444",
            showcoastlines=False,
            showland=True, landcolor="#f5f5f5",
            row=1, col=col,
        )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        width=1200, height=620,
        title=dict(text="Spatial distribution of the minimum incentive-compatible subsidy",
                   x=0.02, xanchor="left"),
    )

    if save:
        path = FIGURES_DIR / "figure_subsidy_map.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")
    return fig


def figure_subsidy_regime_breakdown(
    grid_apt : pd.DataFrame | None,
    grid_hse : pd.DataFrame | None,
    save     : bool = True,
) -> go.Figure | None:
    """
    Stacked bar: x = R̂ grid, y = count of markets with S* > 0, coloured by
    equilibrium regime, faceted by property type. Shows which regimes the
    subsidy binds in at each cost level.
    """
    panels = []
    if grid_apt is not None and not grid_apt.empty:
        panels.append(("Apartments", grid_apt))
    if grid_hse is not None and not grid_hse.empty:
        panels.append(("Houses", grid_hse))

    if not panels:
        return None

    fig = make_subplots(rows=1, cols=len(panels),
                        subplot_titles=[p[0] for p in panels],
                        shared_yaxes=False,
                        horizontal_spacing=0.10)

    for col, (label, grid) in enumerate(panels, start=1):
        positive = grid[grid["S_star_eur_per_m2"] > 0]
        counts = (
            positive.groupby(["cost_per_m2", "regime"])
            .size().unstack(fill_value=0)
            .sort_index()
        )
        for reg in counts.columns:
            fig.add_trace(
                go.Bar(
                    x=counts.index, y=counts[reg],
                    name=REGIME_LABELS.get(reg, reg),
                    marker=dict(color=REGIME_COLORS.get(reg, "#888")),
                    legendgroup=reg, showlegend=(col == 1),
                ),
                row=1, col=col,
            )
        fig.update_xaxes(title_text="R̂ (€/m²)", row=1, col=col)
        fig.update_yaxes(title_text="# markets with S* > 0" if col == 1 else "",
                         row=1, col=col)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="stack",
        width=1100, height=480,
        legend=dict(orientation="h", y=-0.18),
    )

    if save:
        path = FIGURES_DIR / "figure_subsidy_regime_breakdown.html"
        fig.write_html(str(path))
        logger.info(f"  → Saved to {path}")
    return fig


def table_subsidy_summary(
    summary_apt : pd.DataFrame | None,
    summary_hse : pd.DataFrame | None,
    save_latex  : bool = True,
) -> str | None:
    """
    Two-panel LaTeX table summarising the subsidy grid. Rows = renovation cost
    schemes (€/m²); columns: N total, N with S* > 0, share, mean S*_eur_per_m2
    conditional on S*>0, median, p75, mean total-unit subsidy.

    Footnote: S* is the minimum incentive-compatible bound, not equilibrium
    take-up — see paper Definition `def:minimum_subsidy` and the Ramsey remark.
    """
    if summary_apt is None and summary_hse is None:
        return None

    def _panel(df: pd.DataFrame, panel_label: str) -> str:
        if df is None or df.empty:
            return ""
        d = df[df["regime"] == "all"].copy().sort_values("cost_per_m2")
        d["share_positive"] = (100 * d["share_positive"]).round(1)
        for c in ("mean_S_per_m2_positive", "median_S_per_m2", "p75_S_per_m2",
                  "mean_S_per_unit_positive"):
            d[c] = d[c].round(1)

        body = "\n".join(
            f"    {int(row.cost_per_m2)} & {int(row.N_total)} & {int(row.N_positive)} & "
            f"{row.share_positive:.1f}\\% & {row.mean_S_per_m2_positive:.0f} & "
            f"{row.median_S_per_m2:.0f} & {row.p75_S_per_m2:.0f} & "
            f"{row.mean_S_per_unit_positive:,.0f} \\\\"
            for row in d.itertuples()
        )
        return (
            f"  \\multicolumn{{8}}{{l}}{{\\textit{{Panel {panel_label}}}}} \\\\\n"
            f"  \\midrule\n{body}\n  \\midrule\n"
        )

    header = (
        "\\begin{tabular}{lccccccc}\n"
        "  \\toprule\\toprule\n"
        "  $\\hat R$ (\\euro/m\\textsuperscript{2}) & $N_{\\text{total}}$ & $N_{S>0}$ & "
        "Share $S>0$ & Mean $S^* | S>0$ (\\euro/m\\textsuperscript{2}) "
        "& Median $S^*$ (\\euro/m\\textsuperscript{2}) "
        "& P75 $S^*$ (\\euro/m\\textsuperscript{2}) "
        "& Mean $S^*$ per unit (\\euro) \\\\\n"
        "  \\midrule\n"
    )
    body = ""
    if summary_apt is not None:
        body += _panel(summary_apt, "A: Apartments")
    if summary_hse is not None:
        body += _panel(summary_hse, "B: Houses")
    footer = "  \\bottomrule\\bottomrule\n\\end{tabular}\n"
    tex = header + body + footer

    if save_latex:
        path = TABLES_DIR / "table_subsidy_grid.tex"
        path.write_text(tex)
        logger.info(f"  → Saved to {path}")

    return tex


def produce_all_outputs(
    df               : pd.DataFrame,
    market_stats     : pd.DataFrame,
    data_moments     : dict,
    msm_result       : object,
    hedonic_params   : object,
    subsidy_df       : pd.DataFrame | None = None,
    se_dict          : dict | None = None,
    did_params       : object | None = None,
    did_estimates    : object | None = None,
    subsidy_grid_df  : pd.DataFrame | None = None,
    subsidy_summary  : pd.DataFrame | None = None,
    subsidy_budget   : pd.DataFrame | None = None,
    centroids_df     : pd.DataFrame | None = None,
    output_dir       : str | Path | None = None,
    sibling_grid     : pd.DataFrame | None = None,
    sibling_centroids: pd.DataFrame | None = None,
    sibling_summary  : pd.DataFrame | None = None,
    sibling_label    : str = "HOUSE",
    self_label       : str = "APARTMENT",
    cost_per_m2_canonical : float = 500.0,
) -> None:
    """
    Produce all tables and figures in one call.

    The sibling_* arguments let a single call render the two-panel
    subsidy figures (apartments + houses side by side) when both pipelines
    have already been run. When sibling_* is None, single-panel versions are
    produced.
    """
    logger.info("=" * 60)
    logger.info("PRODUCING TABLES AND FIGURES")
    logger.info("=" * 60)

    # ---------- Tables / figures unrelated to subsidies ---------------------
    table_descriptive_stats(df, market_stats)
    table_market_stats(market_stats)
    table_estimates(msm_result, se_dict=se_dict)
    table_market_estimates(data_moments, msm_result.model_moments,
                           msm_result, did_estimates=did_estimates)

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

    # ---------- Subsidy grid: persistence ----------------------------------
    if subsidy_grid_df is not None and output_dir is not None:
        export_market_estimates(
            grid_df      = subsidy_grid_df,
            summary_df   = subsidy_summary if subsidy_summary is not None else pd.DataFrame(),
            output_dir   = output_dir,
            budget_df    = subsidy_budget,
            centroids_df = centroids_df,
        )

    # ---------- Subsidy grid: figures + table ------------------------------
    if subsidy_grid_df is not None:
        is_apt = (self_label.upper() == "APARTMENT")
        grid_apt = subsidy_grid_df if is_apt else sibling_grid
        grid_hse = subsidy_grid_df if not is_apt else sibling_grid
        cent_apt = centroids_df if is_apt else sibling_centroids
        cent_hse = centroids_df if not is_apt else sibling_centroids
        sum_apt  = subsidy_summary if is_apt else sibling_summary
        sum_hse  = subsidy_summary if not is_apt else sibling_summary

        figure_renovation_threshold_distribution(grid_apt, grid_hse)
        figure_subsidy_grid(grid_apt, grid_hse)
        figure_threshold_vs_beta1(grid_apt, grid_hse)
        figure_subsidy_regime_breakdown(grid_apt, grid_hse)
        figure_subsidy_bubble_map(
            grid_apt=grid_apt, grid_hse=grid_hse,
            centroids_apt=cent_apt, centroids_hse=cent_hse,
            cost_per_m2_apt=cost_per_m2_canonical,
            cost_per_m2_hse=cost_per_m2_canonical,
        )
        table_subsidy_summary(sum_apt, sum_hse)

    logger.info(f"[outputs] All results saved to {RESULTS_DIR}")
