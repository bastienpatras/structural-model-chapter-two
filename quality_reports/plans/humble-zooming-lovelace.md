---
status: DRAFT
branch: fix/rho-identification-gmm
---

# Fix the ρ identification failure (structural non-disclosure model)

## Context

A simulated `--peer` referee report (`quality_reports/peer_review_paper-real-estate/referee_methods.md`,
Concern 1) argued that the paper's two-step estimator for buyer EPC-sensitivity ρ_m is degenerate:
the market-level ratio ρ̂_m = Δ̂_m/(β̂₁,m·ê*_m) collapses to ≈1 identically, regardless of the true
ρ_m, because ρ_m cancels between numerator and denominator under the model's own pricing equations.

I asked `micro-theorist` to formally verify this and design a fix. The derivation (full text
preserved below in Appendix D of this plan, and to be moved into `paper-real-estate` as real
appendix propositions during Phase 3) goes further than the referee: it **proves** — Proposition 1,
with a Jacobian argument — that (ρ_m, β1) are identified *only* as the product b_m ≡ ρ_m·β1, by
*any* moment implied by the model, for *any* number of markets. My original plan ("pool markets,
estimate ρ via cross-market GMM") is therefore impossible as stated: no amount of pooling escapes
an exact algebraic cancellation. A genuine fix requires an external, non-price anchor on β1.

While verifying the derivation's claims against the actual code (not just the paper's prose), I
found a second, independent, previously-unflagged bug: `run.py:126-130` calls
`build_valuation_params(m, market_stats, hedonic_params, scale=scale, scale_m=scale_m)` **without**
the `did_beta1` kwarg that `src/estimation.py:124-128` exists specifically to accept. So
`market_params[m].beta_1` — the β1 that actually feeds `estimate_msm`'s ĉ₀_m computation
(`estimation.py:353`) and, downstream, `R̄_m`/`S*_m` in the policy section — is silently the
**market-specific hedonic** (cross-sectional, post-period level) β1_m, not the **DiD** (pre/post
change) β̂1,m that Table 4 Panel A reports and that the paper's own formula (`eq:c0_estimator`,
`eq:did_beta1`) says should be used. Confirmed by reading `run.py:126-130` and
`src/estimation.py:95-141` directly (not inferred). This mixing of a DiD-based ρ̂_m with a
hedonic-level β1_m is a plausible independent contributor to the referee's Concern 8 "ĉ₀ₘ > β̂1ₘ"
arithmetic-impossibility finding, separate from the ρ-identification problem itself.

Helpfully, the derivation's own reasoning (§0.4, §3.3) says the **level/hedonic** β1_m is actually
the theoretically *correct* choice for c₀_m and R̄_m (both are level objects evaluated in the
post-reform period, at the same time as ê*_m/σ̂0_m — mixing them with a DiD *change* β1_m was
already wrong on those grounds, independent of the run.py omission). So the fix is not "restore
DiD β1 everywhere" — it's "make the hedonic-vs-DiD choice deliberate and internally consistent,
document it, and stop letting ρ̂_m (DiD-based) and c0/R̄ (hedonic-based) silently use different β1s."

**Net scope of this branch:** (0) fix the β1-mismatch bug and re-baseline what actually changes;
(1) build a genuine, non-degenerate identification strategy for ρ via an external energy-cost
anchor; (2) implement it in code as a new estimator module; (3) rewrite the paper's identification
section, Table 4, robustness appendix, and policy-section prose accordingly (the policy section's
*numbers* are proven to be unaffected — Part 3.1 of the derivation — only its ρ-language changes);
(4) re-review with the existing reviewer fleet.

## Phase 0 — Correctness baseline (do first, independent of everything else)

1. In `run.py:126-130`, add an explicit, documented choice for `did_beta1`. Given the derivation's
   level/change argument, the resolution is: **pass `did_beta1=None` explicitly with a comment**
   (i.e. formalize "hedonic level β1 is deliberately used for c0/R̄" as a decision, not an
   accident) — no functional code change, but add the comment and a one-line log statement so the
   choice is visible in `results.txt`.
2. Re-run `run.py` for both property types (`config_apartment.json`, `config_house.json`) unchanged,
   confirm outputs are byte-identical to current `results/{apartment,house}` (they should be, since
   no behavior changes — this step is a regression check that Phase 0's documentation-only change
   didn't accidentally alter anything).
3. Add one paragraph to `sections/04-structural-draft.tex` §4.3 (near `eq:c0_estimator`) stating
   explicitly that ĉ0_m and R̄_m use the **market-level hedonic (post-period, cross-sectional) β1_m**,
   not the DiD β̂1,m of Table 4 Panel A — and why (level-vs-change consistency). This alone resolves
   part of referee Concern 8 (the "ĉ0 > β1" arithmetic check was comparing ĉ0 against the wrong β1).
4. Reviewer: `python-reviewer` on the `run.py`/`estimation.py` diff (mechanical, low-risk).

## Phase 1 — Data: the energy-cost anchor (Assumption A)

Goal: a market-specific, **non-price** estimate of β1_m — the capitalized energy-cost saving a
sensitive buyer attaches to a certified-A–D vs certified-E–G dwelling — that can serve as the
external scale the derivation's Proposition 4 requires.

β1_m = κ · A_m / P_m, where A_m = (Ē0,m − Ē1,m) · p^E · a(r,T), a(r,T) = [1−(1+r)^(−T)]/r

1. **Verify (gate before any code):** does the ADEME registry source data (`ADEME/`) carry raw
   certified energy-consumption values (kWh_ep/m²/yr), not just the letter grade? DPE registries
   standardly do (`consommation_energie` field); confirm the exact column name and coverage before
   building on it.
2. If present: extend `src/data_prep.py`'s market-stats aggregation (near `compute_market_stats`)
   to compute Ē0,m, Ē1,m (mean consumption by quality band, per market, from matched ADEME
   records only — i.e., K=1 listings, so this doesn't reintroduce a price-data dependency).
3. Calibrate p^E (energy price, €/kWh), r (discount rate), T (horizon) as **national constants**
   for the first pass (not market-varying) — the derivation's own recommendation ("κ=1 in the
   baseline… report sensitivity over a grid"); local variation in β1_m already comes through
   Ē0,m−Ē1,m and P_m (already in `market_stats` via `compute_market_levels`). Source p^E from a
   public reference (e.g. CRE/INSEE average residential electricity+gas price), document the
   source and the calibration grid in the config.
4. If raw consumption values are **not** available in the current ADEME extract: fall back to
   Variant III from the derivation (subgroup normalization — ρ_m=1 imposed on an ex-ante
   rental-ban-dominated subgroup of markets, giving a √M-consistent β̂1) rather than blocking the
   whole branch on a new data acquisition. Flag this as a scope decision to confirm once step 1's
   verification result is known.

## Phase 2 — Code: the point-identified estimator

New module `src/rho_identification.py` (keeps this off to the side of the existing, still-used
`estimate_rho_c0`/`estimate_msm` rather than rewriting them in place — the old ratio-based ρ̂_m
becomes a labeled diagnostic, not the estimator):

1. `estimate_beta1_anchor(market_stats, ademe_consumption, config) -> pd.Series` — Phase 1's
   β1_m per market.
2. `estimate_rho_c0_anchored(did_estimates, market_stats, beta1_anchor) -> AnchoredResult` —
   Proposition 4: ρ_m = B_m/β1_m^anchor (point identified, testable inequality ρ_m ≤ 1 i.e.
   B_m ≤ β1_m^anchor, log and flag violations rather than silently clip), c0_m = B_m·e(σ̂0,m)
   (Proposition 2(ii) — **this replaces `eq:c0_interval` as the primary c0 estimator for both
   property types**, not just houses).
3. Diagnostics, both reported not discarded:
   - λ̂_m = Δ̂_m − B_m·ê_m (the measured wedge, Lemma 3 / §0.5) — save as a column, not silently
     absorbed.
   - Concentration statistic Λ̄' = M⁻¹Σ_m ρ̂_m(1−ρ̂_m) — gates whether a covariate index (§2.4 of
     the derivation) is reportable at all for a given property type.
   - J-test on the over-identifying restriction Δ_m = B_m·e_m (report per Corollary 1.1 — this is
     the "cross-market mean ratio ≈7.7" finding, reframed correctly as a rejected specification
     test rather than an estimation nuisance).
   - The c0-homogeneity diagnostic (§2.3): scatter ê_m vs 1/B_m across PP markets, and the
     corresponding common-c0 estimate, as a robustness cross-check.
4. Wire into `run.py`: new config key (e.g. `"rho_estimator": "anchored"` vs the legacy
   `"ratio"`), inserted after the existing `did_params = estimate_rho_c0(...)` call (`run.py:108`)
   — call the new estimator, and pass its `rho_m`/`c0_m` into `rho_init`/`c0_init_dict`
   (`run.py:132-144`) in place of `did_params.rho_m`/`did_params.c0_m`. Keep `did_params` computed
   as before (source of the diagnostics above and of B_m/Δ_m themselves) — this is an additive
   change, not a deletion of `estimate_rho_c0`.
5. `src/outputs.py`: extend `_market_estimates_from_grid`'s hardcoded `keep` list
   (`outputs.py:650-656`) to add `rho_m_anchored, lambda_m, regime_j_stat` (or similar) alongside
   existing columns, so `market_estimates.csv`/`subsidy_grid.csv` carry both the old (diagnostic)
   and new (primary) ρ̂_m without breaking existing consumers.
6. Reviewer: `python-reviewer` on the new module + `run.py`/`outputs.py` diff.

## Phase 3 — Paper

1. Add Propositions 1, 2, Lemma 3, Proposition 4 (identification) to
   `paper-real-estate/sections/A-robustness.tex` or a new appendix subsection — full text is in
   Appendix D below (this plan), lightly edited to match house style
   (`realestate-finance-writing` skill) and the paper's existing proof register
   (`main.tex:556-594` is the model to match).
2. Rewrite `sections/04-structural-draft.tex` §4.3 identification narrative:
   - **Retract** the "composition bias inflates Δ̂" explanation (`:409`, `:425`) — it contradicts
     the model's own information structure (buyers don't observe K, so there's no sub-population
     to average over within the d=0 pool). Replace with Lemma 3 / the measured wedge λ̂_m.
   - Replace `eq:rho_estimator`'s ratio with Proposition 4's anchored estimator.
   - Update Table 4 (`tab:did_results`, `04-structural-draft.tex:455-484`) with the new ρ̂_m,
     ĉ₀_m; this also resolves referee Concern 8's N-mismatch/arithmetic-impossibility findings as
     a byproduct if the underlying numbers change (verify against the new table, don't assume).
3. `A-robustness.tex`: add the J-test / concentration-statistic / λ_m-wedge robustness table.
4. Abstract + Conclusion (`main.tex`): **retract** the specific ρ̂ magnitudes ("90.9% for
   apartments, 68.1% for houses") — they described a rejected specification-test statistic, not
   buyer sensitivity. Replace with whatever Phase 1/2 actually estimate.
5. Policy section (`main.tex:190-291`): **numbers unchanged** (derivation Part 3.1 — R̄^PP_m = b_m
   = B_m directly, no ρ decomposition needed) but **prose rewritten**: `:230` and `:276` currently
   attribute climate/energy-cost exposure to ρ-targeting and price-level to a separate mechanism —
   under Assumption A this is backwards (climate/consumption-gap belongs to β1, not ρ; the correct
   targeting statement is in terms of b_m, or of ρ_m once anchored). Also verify Phase 0's finding
   doesn't move the reported €165/m² / €15.5–38.7bn aggregates before rewriting the prose around
   them.
6. Reviewer: `econ-academic-editor` for the prose pass; `realestate-finance-writing` skill for
   house style on the rewritten §4.3/§5 paragraphs.

## Phase 4 — Review

1. `structural-micro-reviewer` — full re-review of the new identification section against the new
   code, focused on whether Concerns 1/2/3/4/6/8 from the referee report are actually resolved
   (not just relabeled).
2. Re-run the `methods-referee` disposition (or `/review-paper --peer TOPFIN --r2`) against the
   revised §4.3–4.5 and Table 4 specifically, since that's the referee whose Concern 1 started this.
3. `/audit-reproducibility` on the new Table 4 numbers against `results/{apartment,house}`.

## Verification

- `run.py config_apartment.json config_house.json` completes without error under both the Phase 0
  documentation-only config and the Phase 2 `"rho_estimator": "anchored"` config.
- `market_estimates.csv`/`subsidy_grid.csv` carry the new columns without breaking
  `scripts/make_subsidy_figures.py` / `scripts/make_subsidy_map.py` (regenerate all four PDFs +
  both maps, diff against current `paper/fig/visuals/*.pdf` to confirm §5's exhibits are unchanged
  per the derivation's Part 3.1 prediction — this is the concrete test of that theoretical claim).
- `results/{apartment,house}/results.txt` and `market_estimates.csv` show the new ρ̂_m/ĉ₀_m
  alongside the old (diagnostic) ones, plus λ̂_m, Λ̄', and the J-statistic.
- LaTeX compiles (`latexmk -pdf`) with no new undefined references; Table 4 numbers cross-checked
  against `results.txt` by hand before commit (per `python-code-conventions.md`/single-source
  discipline — flagged in the prior structural-micro review as currently absent, Concern C2).

## Appendix D — micro-theorist's full derivation (for Phase 3 drafting)

Preserved verbatim from the design-phase agent run (agent id `a5b6701d606be9b3e` in this session) —
Propositions 1/2/4, Corollaries 1.1/1.2, Lemma 3, the GMM moment system §2.2, the covariate table
§2.4, and the Part 3 policy-section verification, including the Part 3.3(A)/(B)/(C) code-level
findings that motivated Phase 0 above. To be pulled into `A-robustness.tex` and
`04-structural-draft.tex` during Phase 3. If session context is lost before Phase 3 starts, either
recover the transcript or re-run the same derivation prompt against `micro-theorist` (the prompt
used is reconstructable from this plan's Context section plus the referee report) — do not
paraphrase from memory, re-derive or re-fetch the verbatim text before drafting appendix prose from
it, per this repo's own `research-agent-laws.md` (re-derive, don't re-ask from a fuzzy summary).
