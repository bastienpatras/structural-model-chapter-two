from __future__ import annotations
"""
model.py
========
Part 2: Model Objects and Equilibrium Solver
---------------------------------------------
Implements the structural model of Section 3–4 of the paper.

Model primitives (all in log-price units unless noted):
  θ ∈ {0, 1}     : binary EPC quality (high / low energy efficiency)
  K ∈ {0, 1}     : information status (informed / uninformed seller)
  d ∈ {0, 1}     : disclosure decision
  π ∈ (0, 1)     : share of informed sellers
  ρ ∈ (0, 1)     : share of EPC-sensitive buyers
  c₀ ≥ 0         : hiding cost (applies to all non-disclosers, Eq. C(θ,d))
  e ∈ [0, 1]     : buyer belief about average quality among non-disclosers

Core equations implemented:
  Eq. (eq:belief_simplified) : belief function e(σ₀)
  Eq. (eq:demand)            : transaction probability Γ(p|d)
  Eq. (eq:payoff)            : seller profit Π(p; d, θ)
  FOC (Appendix, proof "Optimal price sensitivity") : optimal price
  Δ(e) (Sec. "Equilibrium Characterization") : profit gain from hiding
  Proposition (prop:equilibrium) : equilibrium existence and uniqueness
"""

import numpy as np
from scipy.special import expit as logistic_cdf  # 1/(1+exp(-x))
from scipy.optimize import brentq, minimize_scalar
from dataclasses import dataclass, field
from typing import Literal


# ---------------------------------------------------------------------------
# Section A — Demand distribution: logistic G(·)
# ---------------------------------------------------------------------------

def G(x: float | np.ndarray, scale: float = 1.0) -> float | np.ndarray:
    """
    Logistic CDF: G(x) = 1/(1 + exp(-x/scale)).

    The paper assumes G is the logistic CDF (Appendix proof "Optimal price sensitivity" and Lemma A.1).
    Scale parameter σ captures the dispersion of idiosyncratic taste shocks ε.
    With scale=1, this is the standard logistic.

    Assumption: scale is common across markets. We calibrate it from the
    variance of hedonic residuals: scale ≈ σ_OLS * sqrt(3) / π
    (probit-logit scale conversion). Default = 1.0 (normalised).
    """
    return logistic_cdf(x / scale)


def G_prime(x: float | np.ndarray, scale: float = 1.0) -> float | np.ndarray:
    """
    Logistic PDF: G'(x) = G(x)(1-G(x)) / scale.

    From the paper: G'(x) = G(x)(1-G(x)) > 0 for all x (Appendix Lemma A.1).
    """
    g = G(x, scale)
    return g * (1.0 - g) / scale


# ---------------------------------------------------------------------------
# Section B — Valuations (Eqs. 5, 6, 36; benchmark α_k = β_k)
# ---------------------------------------------------------------------------

@dataclass
class ValuationParams:
    """
    Parameters for buyer valuation functions, estimated from hedonic regression.

    Under the benchmark assumption α_k = β_k (Sec. "Buyer Valuations and Demand"), buyers value quality
    the same way whether certified or inferred. This simplifies:
      v_1(d=1, θ) = β₀ + β₁·θ + X̄'β_X        (Sec. "Buyer Valuations and Demand", d=1 case)
      v_1(d=0, e) = β₀ + β₁·e + X̄'β_X        (Sec. "Buyer Valuations and Demand", d=0 case)
      v_0         = δ₀ + X̄'δ_X               (Sec. "Buyer Valuations and Demand")

    Estimated from:
      - β₁, β_X  : OLS hedonic on truthful disclosers (estimation appendix forthcoming)
      - β₀       : hedonic intercept (absorbed by market FE α_m)
      - v_0      : baseline "EPC-blind" valuation (see below)

    Note on v_0:
      EPC-insensitive valuation v₀(X) (Sec. 'Buyer Valuations and Demand'). We proxy v_0
      by the hedonic prediction at the "neutral" EPC quality (θ = θ̄) or,
      equivalently, by the mean log price of non-disclosers. A positive gap
      (v_1 > v_0 under disclosure) reflects the EPC-sensitive premium.

    Assumption: X̄'β_X and X̄'δ_X coincide (same controls enter both valuations).
    This is a simplification; δ and β could in principle differ.
    """
    # From hedonic regression on truthful disclosers (estimation appendix forthcoming)
    beta_0   : float = 0.0    # market-level intercept (α_m from hedonic; market-specific)
    beta_1   : float = 0.06   # EPC premium: log-price gain from θ=1 vs θ=0 when disclosed
    X_beta_X : float = 0.0    # mean controls contribution: X̄_m' · γ̂ (hedonic-predicted)

    # Insensitive buyer valuation (calibrated; see note above)
    # v_0 = β₀ + X̄'β_X by default (same as EPC-blind hedonic baseline)
    # Can be overridden with a separate regression on non-disclosers.
    v0_offset: float = 0.0    # v_0 = beta_0 + X_beta_X + v0_offset

    # Logistic demand scale (calibrated from hedonic residual variance)
    scale    : float = 1.0

    # φ(p^list) parameters — Eq. (eq:payoff), φ bullet.
    # Convention: p is log listing price; φ(p) = exp(γ₀ + γ₁·p) is the level
    # expected transaction price.  Default γ₀=0, γ₁=1 → φ = exp(p).
    # Override with a listing-to-transaction-price regression if available.
    gamma_0  : float = 0.0
    gamma_1  : float = 1.0

    @property
    def v0(self) -> float:
        """Insensitive buyer valuation (log price units)."""
        return self.beta_0 + self.X_beta_X + self.v0_offset

    def v1_disclosed(self, theta: float) -> float:
        """
        Sensitive buyer valuation under disclosure (Sec. "Buyer Valuations and Demand", d=1 case).
        v₁(d=1, θ) = β₀ + β₁·θ + X̄'β_X
        """
        return self.beta_0 + self.beta_1 * theta + self.X_beta_X

    def v1_hidden(self, e: float) -> float:
        """
        Sensitive buyer valuation under hiding, given belief e (Sec. "Buyer Valuations and Demand", d=0 case).
        v₁(d=0, e) = β₀ + β₁·e + X̄'β_X
        """
        return self.beta_0 + self.beta_1 * e + self.X_beta_X


# ---------------------------------------------------------------------------
# Section C — Demand, profit, and optimal pricing (Eqs. (eq:demand) and (eq:payoff))
# ---------------------------------------------------------------------------

def transaction_prob(
    p: float | np.ndarray,
    v1: float,
    v0: float,
    rho: float,
    scale: float = 1.0,
) -> float | np.ndarray:
    """
    Transaction probability Γ(p^list | d) — Eq. (eq:demand).

    Γ(p|d) = ρ · G(v₁(d) - p) + (1-ρ) · G(v₀ - p)

    Interpretation:
      ρ        : share of EPC-sensitive buyers (fraction who respond to disclosure)
      v₁(d)    : sensitive-buyer valuation under disclosure status d
      v₀       : insensitive-buyer valuation (disclosure-invariant)
      G(v - p) : probability that a buyer with valuation v purchases at price p

    When ρ = 0: demand is G(v₀ - p), independent of d → disclosure is irrelevant.
    When ρ = 1: demand is G(v₁(d) - p), fully responsive to disclosure.
    """
    return rho * G(v1 - p, scale) + (1.0 - rho) * G(v0 - p, scale)


def expected_trans_price(p: float, gamma_0: float = 0.0, gamma_1: float = 1.0) -> float:
    """
    Expected transaction price φ(p^list) — Eq. (eq:payoff), φ bullet.

    φ(p^list) = γ₀ + γ₁ · p^list

    Default: γ₀ = 0, γ₁ = 1 (listing price ≈ transaction price).
    Estimate from a listing-to-transaction-price regression if transaction data
    are available.
    """
    return gamma_0 + gamma_1 * p


def seller_profit(
    p: float | np.ndarray,
    v1: float,
    v0: float,
    rho: float,
    params: ValuationParams,
) -> float | np.ndarray:
    """
    Seller gross profit (before hiding cost) — Eq. (eq:payoff).

    Π(p; d, ρ) = φ(p^list) · Γ(p^list | d)

    Working convention:
      p is the log listing price (as in the hedonic regression). Revenue
      φ(p) = γ₀ + γ₁·p is linear in log price, keeping profit in log-price
      units throughout — consistent with the hedonic moments m1–m3 and the
      equilibrium condition Δ(e) = c₀.

      Under the simplified assumption γ₀=0, γ₁=1: φ(p) = p (identity).

    The hiding cost C(θ, d) is subtracted separately when comparing disclosure
    options (C(θ,d) bullet in Eq. (eq:payoff)). It is in the same log-price units as Π.
    """
    phi   = expected_trans_price(p, params.gamma_0, params.gamma_1)
    gamma = transaction_prob(p, v1, v0, rho, params.scale)
    return phi * gamma


def optimal_price(
    v1: float,
    v0: float,
    rho: float,
    params: ValuationParams,
    search_width: float = 5.0,
) -> float:
    """
    Compute the optimal listing price p* — FOC from Appendix proof "Optimal price sensitivity".

    p* = argmax_p φ(p) · Γ(p | d)

    The FOC: γ₁·Γ(p*) + (γ₀ + γ₁·p*)·Γ'(p*) = 0

    Solved numerically via bounded scalar minimisation of -Π(p).

    Parameters
    ----------
    search_width : search range ± `search_width` (in scale units) around
                   the dominant valuation. Increase if optimum not found.
    """
    v_max = max(v1, v0)
    v_min = min(v1, v0)

    # Bracket: optimal price lies between min valuation and some upper bound.
    # At p = v_max, all buyers drop out → profit ≈ 0. At p very low, revenue low.
    p_lo = v_min - search_width * params.scale
    p_hi = v_max + search_width * params.scale

    neg_profit = lambda p: -seller_profit(p, v1, v0, rho, params)
    result = minimize_scalar(neg_profit, bounds=(p_lo, p_hi), method="bounded",
                             options={"xatol": 1e-8})
    if not result.success:
        # Fallback: try a coarser grid
        p_grid = np.linspace(p_lo, p_hi, 500)
        profits = np.array([seller_profit(p, v1, v0, rho, params) for p in p_grid])
        return float(p_grid[np.argmax(profits)])
    return float(result.x)


def max_profit(
    v1: float,
    v0: float,
    rho: float,
    params: ValuationParams,
) -> float:
    """
    Maximised seller profit Π*(d, ρ) = max_p Π(p; d, ρ).

    Used to compute the profit gain from hiding Δ(e; ρ) — Sec. "Equilibrium Characterization".
    """
    p_star = optimal_price(v1, v0, rho, params)
    return float(seller_profit(p_star, v1, v0, rho, params))


# ---------------------------------------------------------------------------
# Section D — Belief function (Eq. (eq:belief_simplified))
# ---------------------------------------------------------------------------

def belief_function(
    sigma_0: float,
    pi: float,
    theta_bar: float,
) -> float:
    """
    Buyer belief about expected quality among non-disclosers — Eq. (eq:belief_simplified).

    Under the equilibrium result σ₁* = 0 (high-quality sellers always disclose,
    Corollary (cor:hq_disclose)), the belief simplifies from Eq. (eq:belief_general) to:

        e(σ₀) = (1 - π) · θ̄ / [π · (1 - θ̄) · σ₀ + (1 - π)]

    Properties:
      - e(0) = θ̄  (no strategic hiding → pool = uninformed sellers, avg quality θ̄)
      - e(1) = (1-π)θ̄ / (1 - πθ̄)  < θ̄  (all low-quality hide → pool diluted)
      - e(σ₀) strictly decreasing in σ₀ (Property 1, Sec. "Equilibrium Characterization")

    Parameters
    ----------
    sigma_0   : hiding probability of informed low-quality sellers σ₀ ∈ [0, 1]
    pi        : share of informed sellers π ∈ (0, 1)
    theta_bar : population mean quality θ̄ ∈ (0, 1)
    """
    numerator   = (1.0 - pi) * theta_bar
    denominator = pi * (1.0 - theta_bar) * sigma_0 + (1.0 - pi)
    if denominator <= 0:
        return 0.0
    return float(numerator / denominator)


def belief_bounds(pi: float, theta_bar: float) -> tuple[float, float]:
    """
    Boundary values of the belief function — from Eq. (eq:belief_simplified).

    e(0) = θ̄         (best-case pool: only uninformed sellers hide)
    e(1) = (1-π)θ̄ / (1 - πθ̄)   (worst-case pool: all low-quality hide too)

    Used to classify the equilibrium regime (Proposition (prop:equilibrium)).
    """
    e0 = belief_function(0.0, pi, theta_bar)   # = θ̄ (σ₀=0 boundary)
    e1 = belief_function(1.0, pi, theta_bar)   # σ₀=1 boundary
    return e0, e1


# ---------------------------------------------------------------------------
# Section E — Profit gain from hiding Δ(e; ρ) (Sec. "Equilibrium Characterization")
# ---------------------------------------------------------------------------

def profit_gain_hiding(
    e: float,
    rho: float,
    params: ValuationParams,
) -> float:
    """
    Profit gain from hiding for an informed low-quality seller — Sec. "Equilibrium Characterization".

        Δ(e; ρ) = Π*(d=0, e; ρ) - Π*(d=1, θ=0; ρ)

    Implementation (linear approximation, consistent with Lemma A.1 (Appendix)):
    ----------------------------------------------------------------
    In the model, the sensitive-buyer valuation difference is:
        v₁(d=0, e) - v₁(d=1, θ=0) = β₁ · e

    Under the benchmark α_k = β_k, this valuation difference maps approximately
    linearly to a profit difference (Lemma A.1, Appendix):
        Δ(e; ρ) ≈ ρ · β₁ · e

    This linear approximation:
      - Is consistent with the paper's identification strategy (Sec. "Equilibrium Characterization" + Lemma A.1)
      - Treats the hedonic coefficient β₁ as the structural price-quality parameter
        (under the "prices ≈ valuations" convention common in hedonic models)
      - Ensures model-implied moments are in log-price units (same as data)
      - Avoids the units/scale issue of the full nonlinear profit function

    For ρ = 0: no buyer cares about EPC → Δ = 0 → no premium (Proposition (prop:rho))
    For ρ > 0: Δ = ρ·β₁·e, increasing in both ρ and e (Propositions (prop:rho) and (prop:c0))

    Note: a "full structural" implementation using exp(p)·Γ(p) profit maximisation
    is available via `profit_gain_hiding_structural` below and can be used as a
    robustness check.
    """
    return float(rho * params.beta_1 * e)


def profit_gain_hiding_structural(
    e: float,
    rho: float,
    params: ValuationParams,
) -> float:
    """
    Full structural profit gain, normalised by exp(β₀) — Sec. "Equilibrium Characterization".

    Δ(e; ρ) = [Π*(d=0, e; ρ) - Π*(d=1, θ=0; ρ)] / exp(β₀)

    Normalising by exp(β₀) (the baseline property level from the market FE)
    keeps c₀ in the same dimensionless scale as the linear approximation ρ·β₁·e,
    so existing c₀_init values remain valid and the two versions are directly
    comparable as a robustness check.

    This is the default used in solve_equilibrium.
    """
    v1_hide       = params.v1_hidden(e)
    v1_disclose_0 = params.v1_disclosed(0.0)
    v0            = params.v0
    norm          = np.exp(params.beta_0) if params.beta_0 != 0.0 else 1.0

    pi_hide         = max_profit(v1_hide,       v0, rho, params)
    pi_disclose_low = max_profit(v1_disclose_0, v0, rho, params)

    return float((pi_hide - pi_disclose_low) / norm)


# ---------------------------------------------------------------------------
# Section F — Equilibrium solver (Proposition (prop:equilibrium), Sec. "Equilibrium Characterization")
# ---------------------------------------------------------------------------

EQ_TYPE = Literal["full_unraveling", "partial_separation", "mixed_strategy"]


@dataclass
class EquilibriumResult:
    """Container for equilibrium solution."""
    sigma_0_star : float     # Equilibrium hiding rate σ₀* ∈ [0, 1]
    e_star       : float     # Equilibrium belief e* = E[θ | d=0]
    eq_type      : EQ_TYPE   # Equilibrium regime (Proposition (prop:equilibrium))
    delta_e0     : float     # Δ(e(0); ρ) — profit gain if σ₀=0
    delta_e1     : float     # Δ(e(1); ρ) — profit gain if σ₀=1


def solve_equilibrium(
    rho     : float,
    c0      : float,
    pi      : float,
    theta_bar: float,
    params  : ValuationParams,
    tol     : float = 1e-8,
) -> EquilibriumResult:
    """
    Solve for the unique equilibrium (σ₀*, e*) — Proposition (prop:equilibrium).

    Fixed-point problem:
      Φ(σ₀) ≡ Δ(e(σ₀); ρ) - c₀

    where:
      - e(σ₀) is the belief function (Eq. (eq:belief_simplified))
      - Δ(e; ρ) = ρ·β₁·e is the profit gain from hiding (Sec. "Equilibrium Characterization", linear approx.)

    Equilibrium type (Proposition (prop:equilibrium)):
      Full Unraveling    : c₀ > Δ(θ̄)       → σ₀* = 0,  e* = θ̄
      Partial Separation : c₀ < Δ(e(1))    → σ₀* = 1,  e* = e(1)
      Mixed Strategy     : otherwise       → σ₀* ∈ (0,1) s.t. Δ(e(σ₀*)) = c₀

    Uniqueness follows from strict monotonicity of Φ (Sec. "Equilibrium Characterization"):
      dΦ/dσ₀ = Δ'(e) · (de/dσ₀) < 0
    (Δ is increasing in e, but e is decreasing in σ₀)

    The French market operates in the Partial Separation regime (Sec. "Equilibrium Characterization").
    """
    e0, e1 = belief_bounds(pi, theta_bar)

    # Linear profit gain ρ·β₁·e — in log-price units, consistent with MSM
    # moments m1–m3 (mean log prices) and c₀ estimated from those moments.
    def _delta(e: float) -> float:
        return profit_gain_hiding(e, rho, params)

    delta_e0 = _delta(e0)
    delta_e1 = _delta(e1)

    # Classify equilibrium (Proposition (prop:equilibrium))
    if delta_e0 <= c0:
        # Full unraveling: even at best-case pool (σ₀=0), hiding not profitable
        return EquilibriumResult(
            sigma_0_star = 0.0,
            e_star       = e0,
            eq_type      = "full_unraveling",
            delta_e0     = delta_e0,
            delta_e1     = delta_e1,
        )
    elif delta_e1 >= c0:
        # Partial separation: even at worst-case pool (σ₀=1), hiding profitable
        return EquilibriumResult(
            sigma_0_star = 1.0,
            e_star       = e1,
            eq_type      = "partial_separation",
            delta_e0     = delta_e0,
            delta_e1     = delta_e1,
        )
    else:
        # Mixed strategy: unique σ₀* ∈ (0, 1) s.t. Δ(e(σ₀*)) = c₀
        sigma_0_star = brentq(
            lambda s: _delta(belief_function(s, pi, theta_bar)) - c0,
            0.0, 1.0, xtol=tol, rtol=tol,
        )
        e_star = belief_function(sigma_0_star, pi, theta_bar)
        return EquilibriumResult(
            sigma_0_star = float(sigma_0_star),
            e_star       = float(e_star),
            eq_type      = "mixed_strategy",
            delta_e0     = delta_e0,
            delta_e1     = delta_e1,
        )


# ---------------------------------------------------------------------------
# Section G — Equilibrium non-disclosure premium (Eq. (eq:premium))
# ---------------------------------------------------------------------------

def equilibrium_premium(
    sigma_0  : float,
    pi       : float,
    theta_bar: float,
    rho      : float,
    beta_1   : float,
) -> float:
    """
    Non-disclosure premium = ρ · β₁ · e(σ₀)  for a given hiding rate σ₀.

    The three equilibrium benchmarks follow by substituting the regime-specific σ₀:

      σ₀ = 0   →  CDH upper bound:  ρβ₁θ̄               (cleanest pool, no strategic hiders)
      σ₀ = σ₀* →  PP premium:       ρβ₁e(σ₀*) = c₀     (indifference condition)
      σ₀ = 1   →  CAS lower bound:  ρβ₁(1-π)θ̄/(1-πθ̄)  (most contaminated pool)

    The strict ordering CDH > PP > CAS follows because e is strictly decreasing in σ₀
    (Lemma 3.1).  The PP premium equals c₀ by the indifference condition, invariant
    to π and ρ (Proposition (prop:equilibrium)).

    Parameters
    ----------
    sigma_0   : hiding rate of informed low-quality sellers (0 → CDH, σ₀* → PP, 1 → CAS)
    pi        : share of informed sellers
    theta_bar : population mean quality
    rho       : share of EPC-sensitive buyers
    beta_1    : structural EPC quality premium (hedonic estimate, market-specific)

    Returns
    -------
    float : log-price premium for non-disclosers vs disclosed low-quality (E/F/G) sellers
    """
    e = belief_function(sigma_0, pi, theta_bar)
    return float(rho * beta_1 * e)


# ---------------------------------------------------------------------------
# Section H — Renovation threshold (Eqs. 83, 130)
# ---------------------------------------------------------------------------

def renovation_threshold(
    rho      : float,
    pi       : float,
    theta_bar: float,
    c0       : float,
    params   : ValuationParams,
) -> float:
    """
    Maximum renovation cost below which a low-quality seller prefers to renovate
    and disclose rather than hide (Eq. (eq:threshold)).

        R̄(π, ρ, X) = Π*(d=1, θ=1) - Π*(d=0) + c₀

    Components:
      Π*(d=1, θ=1) : profit from disclosing high quality  (market premium)
      Π*(d=0)      : profit from hiding (at equilibrium belief e*)
      c₀           : hiding cost avoided by renovating and disclosing

    Policy implication: subsidise renovation by S* = max{R̂ - R̄, 0} (Eq. (eq:subsidy)).
    """
    eq = solve_equilibrium(rho, c0, pi, theta_bar, params)

    v1_high = params.v1_disclosed(1.0)   # v₁(d=1, θ=1)
    v1_hide = params.v1_hidden(eq.e_star)  # v₁(d=0, e*)
    v0      = params.v0

    pi_disclose_high = max_profit(v1_high, v0, rho, params)
    pi_hide          = max_profit(v1_hide, v0, rho, params)

    return float(pi_disclose_high - pi_hide + c0)


# ---------------------------------------------------------------------------
# Section I — Optimal subsidy (Eq. (eq:subsidy))
# ---------------------------------------------------------------------------

def optimal_subsidy(
    actual_renovation_cost: float,
    renovation_threshold  : float,
) -> float:
    """
    Minimum subsidy needed to induce renovation — Eq. (eq:subsidy).

        S*(π, ρ, X) = max{ R̂(X) - R̄(π, ρ, X), 0 }

    If the actual cost R̂ already falls below the threshold R̄, private incentives
    suffice and no subsidy is needed.
    """
    return float(max(actual_renovation_cost - renovation_threshold, 0.0))
