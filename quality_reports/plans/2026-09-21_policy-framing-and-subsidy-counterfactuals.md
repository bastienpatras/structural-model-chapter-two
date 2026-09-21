---
status: DRAFT
branch: review
---

# Lead with policy results earlier + subsidy counterfactuals on π and ρ

## Context

Raised by Bastien on 2026-09-21, on the `review` branch, as "comments I have in my mind" for a
future session — not to be implemented now. Two ideas:

1. The abstract and introduction should signal the policy contribution earlier, not just at the
   end.
2. Run counterfactual subsidy exercises that set $\pi=1$ or $\rho=1$ (or double them) and report
   how the subsidy need changes, to argue that the other policy instruments (audit-infrastructure
   investment, disclosure salience) make mandatory disclosure more efficient and reduce reliance
   on subsidies.

Claude's assessment, given directly before this plan was written: idea 1 is a good, low-risk
framing change. Idea 2's premise is only half right, and getting the mechanism straight *before*
running anything is the point of this plan — see "The key analytical fact" below.

## Part A — Lead with policy results earlier

**Current state.** The policy-extension result is the last sentence of the abstract
(`main.tex`'s `\abs{}` block) and paragraph 12.5 (added 2026-09-21, positioned after the
energy-efficiency-gap contribution paragraph, near the end of the funnel) in
`sections/01-introduction-draft.tex`.

**Recommended approach: a light-touch early hook, not a restructure.** Keep the full policy
treatment exactly where it is (¶12.5, and §5 in `main.tex`); add:
- One clause early in the abstract (candidate location: right after the "puzzle resolves"
  sentence, or folded into the closing sentence which already exists but currently reads as an
  afterthought) that names the policy stakes up front.
- One sentence in the introduction's opening 1-2 paragraphs (¶1 or ¶2) flagging that the puzzle
  has direct implications for renovation-subsidy design, without pre-empting ¶12.5's full
  treatment.

**Why light-touch, not a full restructure:** the paper's core contribution for its target
journals (JF/JFE/RFS-style real-estate/finance, per `CLAUDE.md`) is the identification result,
not the policy extension. Over-indexing the opening on policy risks reading as scope creep to a
referee expecting a structural-identification paper. Confirm this balance with Bastien before
drafting exact sentences — this is a judgment call on emphasis, not a factual question with one
right answer.

**Open question for next session:** exact placement and wording of both additions; whether the
existing abstract closing sentence should be rewritten in place or a new sentence added earlier.

## Part B — Subsidy counterfactuals on π and ρ

### The key analytical fact (already proven in the paper, not new work)

`Proposition~\ref{prop:subsidy}` (main.tex, §5.4, "Subsidy comparative statics by regime") gives,
in the empirically-dominant Partial Pooling regime:

$$\frac{\partial S^*}{\partial c_0} = 0, \qquad \frac{\partial S^*}{\partial \pi} = 0, \qquad \frac{\partial S^*}{\partial \rho} \leq 0.$$

This means the two counterfactuals Bastien proposed are **not symmetric**:

- **$\rho\to1$ (or $\rho_m$ raised by some amount, capped at 1)**: genuinely reduces the
  per-seller minimum incentive-compatible subsidy $S^*_m$, because raising $\rho$ raises the
  verified-quality premium $\bar R_m$ that closes the $\hat R(X)-\bar R_m$ gap on its own. This
  counterfactual will show what Bastien's intuition expects: lower $S^*_m$, lower aggregate
  programme cost.
- **$\pi\to1$ (or $\pi_m$ raised)**: has **zero** effect on the per-seller subsidy in PP. Its
  entire effect runs through the **extensive margin** — the renovation-flow equation
  (`Eq.~\ref{eq:renovation_flow}` in §5.4: $\text{Renovation flow} = \pi\cdot(1-\bar\theta)\cdot
  F_R(\bar R(\rho,X)+S)$). Raising $\pi$ expands the *population* of sellers the mechanism
  reaches — currently-uninformed low-quality sellers (who today are entirely outside the
  subsidy-eligible accounting, since only informed sellers face the modelled renovation
  decision) become informed and therefore newly eligible. **A naive aggregate-€ figure under
  $\pi=1$ could rise, not fall**, because more properties enter the accounting for the first
  time, even though each one's required subsidy is unchanged. Framing this as "reduces the
  subsidy bill" would be wrong; the correct framing is closer to "expands how many properties
  the programme reaches for the same per-unit ask" or "improves cost-effectiveness per property
  addressed."

**Implication for the write-up:** report the two counterfactuals with different framings. Don't
present them as two versions of the same "instrument X also reduces subsidy need" story — $\rho$
does that, $\pi$ does something different and arguably more interesting (it's the mechanism that
makes audit-infrastructure investment a genuine complement, per the "complements not
substitutes" thesis already in the paper).

### Design questions to resolve before coding (next session, not now)

1. **The $\pi$ counterfactual's population accounting.** `aggregate_budget` (in
   `src/estimation.py`, called from `run.py`) currently weights $S^*_m$ by the *observed* listing
   population (`market_weights = df_est.groupby("market_id").size()`), which reflects the
   *current* $\pi_m$. Raising $\pi_m$ to 1 requires deciding how to gross up the newly-eligible
   population, e.g. multiplying the currently-uninformed low-quality mass
   $(1-\pi_m)(1-\bar\theta_m)$ by the observed listing count and adding it to the base, applying
   the *same* $S^*_m$ (since $S^*_m$ itself is $\pi$-invariant in PP) to that expanded population.
   This is a real design decision, not a one-line parameter flip — work it out against the actual
   `compute_market_subsidies`/`compute_subsidy_grid`/`aggregate_budget` code before writing
   anything.
2. **The $\rho$ counterfactual's boundary.** $\rho_m$ is a share, capped at 1 by construction.
   "Doubling $\rho_m$" is undefined for the roughly half the sample already above 0.5 (means are
   0.495 apartments / 0.458 houses, so a meaningful share of markets sit above that). Use
   $\rho_m\to1$ (full cap) as the primary counterfactual, and/or "$\rho_m$ raised by $\Delta$
   percentage points, capped at 1" as a secondary one, rather than literal doubling.
3. **What stays fixed.** Both counterfactuals should hold $\hat\beta_{1,m}$-anchor-derived
   objects, $\hat R(X)$ benchmarks (€250/€500 per m²), and market-level $X$ fixed — only the
   named parameter moves. State this explicitly in the writeup as a partial-equilibrium
   counterfactual (it does not re-equilibrate $\hat\beta_{1,m}$ itself, which in the full model
   would also respond to a change in $\rho$ or $\pi$; flag this as a limitation, matching the
   paper's existing discipline about what the design does and doesn't deliver).
4. **A joint counterfactual** (both $\pi\to1$ and $\rho\to1$ together) is probably the most
   rhetorically useful cell in the eventual table/figure: it directly dramatizes the paper's
   "complements not substitutes" claim by showing the combined effect exceeds either alone.

### Suggested execution shape (for next session, mirrors `scripts/run_threshold_robustness.py`)

- A small script that re-runs `compute_market_subsidies`/`compute_subsidy_grid`/
  `aggregate_budget` under modified inputs (a counterfactual `rho_hat` dict capped at 1, and/or a
  counterfactual population-grossing for the $\pi$ case per design question 1), for both property
  types, at both $\hat R$ benchmarks (€250/€500), producing:
  - Per-market $S^*_m$ distribution shift (baseline vs. each counterfactual).
  - Aggregate programme cost (baseline vs. each counterfactual) — flagged with the correct
    framing per counterfactual (bill reduction for $\rho$; population reached / cost-per-property
    for $\pi$).
  - Cost-share ($S^*_m/\hat R$) distribution shift.
- Output likely lands as a new short subsection or table in §5.4/§5.5, and could double as the
  concrete illustration Part A's earlier policy hook points forward to.

## Verification (once implemented)

- Baseline reproduction check: counterfactual script's $\pi=\pi_m$, $\rho=\rho_m$ (i.e., no
  change) run must reproduce the current `results/{apartment,house}/subsidy_*.csv` and
  `aggregate_budget` numbers exactly, before trusting any counterfactual variant.
- Confirm $\partial S^*/\partial\pi=0$ holds numerically in the $\pi$ counterfactual's per-market
  $S^*_m$ column (should be unchanged from baseline; only the population/aggregate should move) —
  this is a positive-control check on the counterfactual script itself, not just a result.
- Compile-check any new paper text; independently re-verify new numbers against the script's
  output before treating them as final, per this repo's usual discipline.
