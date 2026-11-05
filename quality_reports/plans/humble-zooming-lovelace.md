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

**Revised after investigation (2026-09-14): no raw per-listing kWh data available without a live
GCS pull.** The ADEME registry is fetched from Google Cloud Storage (`ADEME/tools.py`'s
`read_csv_from_gcs`, geocoded address-level DPE data by department) and the current matching
pipeline (`ADEME/enrich_listings.py`) only retains the **letter grade** (`K`, `ademe_epc_letter`/
`ademe_epc_score`), not raw consumption values — confirmed no cached raw-consumption extract
exists locally in `data/`. A fresh GCS pull touches confidential, geocoded, address-level data
(`.claude/rules/confidential-data.md` scope) and needs its own credentials/authorization — not
attempted here. **Adopted instead: a band-midpoint anchor**, using only already-local data:

1. **Band midpoints are public, fixed, nationally-standardized** — the post-2021 French DPE
   methodology defines primary-energy consumption thresholds per letter (A ≤70, B 71–110,
   C 111–180, D 181–250, E 251–330, F 331–420, G >420 kWh_ep/m²/yr). Use documented midpoints
   (open-ended G band needs a defensible upper reference, not just a guess) as a citable, public
   calibration table — no new data acquisition, no confidentiality exposure.
2. Compute Ē0,m (weighted avg. of E/F/G midpoints) and Ē1,m (weighted avg. of A/B/C/D midpoints)
   **per market, weighted by that market's actual within-band letter distribution among ALL K=1
   listings — both disclosed (d=1) AND hidden (d=0)**, not disclosed-only (same selection-bias
   argument as before: pooling both groups is what avoids re-introducing it). First confirm the
   TRUE ADEME-matched letter (`ademe_epc_score` or equivalent, set in `src/data_prep.py`'s
   `merge_datasets`) is populated for K=1,d=0 (strategic-hiding) listings too, not only for
   disclosed ones — this is a much lighter check than the original raw-consumption-merge question,
   since it's local data already in the pipeline, not a new field.
3. Calibrate p^E (energy price, €/kWh), r (discount rate), T (horizon) as **national constants**
   for the first pass — market-level variation in β1_m now comes through each market's actual
   letter-band mix (step 2) and P_m (already in `market_stats`). Source p^E from a public
   reference (e.g. CRE/INSEE average residential electricity+gas price); document the source and
   report a calibration sensitivity grid, not a single point.

   **Status (2026-09-14), validated on real data:** p^E≈€0.21/kWh (CRE/Eurostat 2022-2024
   average, blended primary-energy-equivalent — DPE bands are kWh_ep primary energy, not billed
   kWh; a proper heating-vector-weighted conversion needs per-listing heating-type data we don't
   have, flag as a simplification), r≈3.75% (contemporary French mortgage rate). **T is the open
   item**: apartment mean ρ̂ ranges from 0.50 (T=10, 2% violate ρ≤1) down to 0.15 (perpetuity, 0%
   violate) — highly sensitive, not a nuisance parameter. Bastien is sourcing actual French
   property holding-period data (INSEE *Enquête Logement*; Notaires de France/CGEDD durée de
   détention avant revente) rather than assuming a long "efficient capitalization" horizon —
   consistent with the energy-efficiency-gap literature (Hausman 1979, Allcott & Wozny 2014)
   finding buyers empirically behave as if using shorter horizons. Full sensitivity grid and
   sourcing notes: native memory `rho_anchor_calibration.md`. **Do not lock T until that number is
   in hand** — re-run the same validation script pattern (§ this file, agent transcript
   2026-09-14) once available.
4. Coarseness caveat to carry into Phase 3: this loses within-band variation (e.g. a market's A–D
   mix skewed toward A vs. toward D reads the same only insofar as the letter *distribution* is
   used, but every A property gets the same midpoint regardless of true position within the band)
   — flag this explicitly as a limitation, and note the raw-microdata version (requiring GCS
   access) remains available as a future refinement if/when that access is authorized.

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
4. **Status (2026-09-14): module built and validated (`src/rho_identification.py`,
   `estimate_beta1_anchor` + `estimate_rho_c0_anchored`), full `run.py` wiring deliberately
   deferred until T is locked (see Phase 1 status note above).** Tested end-to-end on real data,
   both property types (T=10 placeholder): apartments n=49, mean ρ̂=0.498, 1 violation of ρ≤1;
   houses n=104, mean ρ̂=0.455, 6 violations; ĉ₀_m now computed correctly via Proposition 2(ii)
   for both (apartment mean 2.37%, house mean 3.39%); λ̂_m wedge and a simple one-sample-t
   diagnostic (not a full optimal-GMM J-test yet) also validated.

   **A real wiring subtlety, resolved on paper but not yet executed:** naively passing the
   anchored ρ̂_m into `run.py`'s existing `rho_init` and letting `estimate_msm(fix_rho=True)` run
   as before would silently reintroduce a ρ-dependence into ĉ₀ (`estimation.py:353` computes
   `rho_m * beta1_m * e_star`, so feeding it the anchored ρ̂_m gives
   ĉ₀ = (β̂1,m^DiD)²/β̂1,m^anchor · ê*_m — NOT Proposition 2(ii)'s B_m·ê*_m). The correct wiring
   bypasses `estimate_msm` for anchored mode entirely and constructs a compatible `MSMResult`
   directly from `AnchoredResult` (`estimation.py:262-280`: `rho_hat`, `c0_hat` are plain
   `dict[market_id, float]` — straightforward to populate from `AnchoredResult.rho_m`/`.c0_m`) —
   but `eq_types` (regime classification, feeds Table 4/figure grouping) also needs populating
   consistently via `model.solve_equilibrium`-style classification, not left empty, since
   downstream code groups by regime. **Do this wiring once T is locked, not before** — avoids
   validating throwaway plumbing against a provisional calibration.
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

## Phase 2 step 4-5 — DONE (2026-09-14)

T locked at 10 (Bastien sourced French property holding-period data; sensitivity grid to report
T=5/T=15 — not yet run). `run.py` wiring executed exactly as designed above: opt-in
`rho_estimator` config key (`"ratio"`/`"anchored"`, validated against typos so a misspelling
can't silently fall back to `"ratio"`), `anchor_p_E`/`anchor_r`/`anchor_T`/`anchor_kappa` keys.
Both `config_apartment.json`/`config_house.json` now set `rho_estimator="anchored"`,
p_E=0.21, r=0.0375, T=10 — this branch's deliverable, not merged to `paper-real-estate`.

`python-reviewer` caught 3 more issues in the wiring: a crash risk at `outputs.py:1210`
(`model_moments.values()[0]` on a possibly-empty dict) — fixed with a `belief_function`-based
fallback; unvalidated `rho_estimator` string — fixed; the "ê*_m" results.txt row silently reading
from the ratio estimator's object (wrong market set) in anchored mode — fixed. Full pipeline
re-run clean (exit 0), default "ratio" path confirmed byte-identical (up to float noise) to
pre-change output.

**Results (T=10), both property types now flowing through the full pipeline:**
- Apartments: n=45, ρ̂ mean=0.495 (1 violates ρ≤1), ĉ0 mean=2.41%, λ̂_m mean=0.061 (t=6.78 —
  strongly rejects the over-ID restriction).
- Houses: n=97, ρ̂ mean=0.458 (5 violate), ĉ0 mean=3.45%, λ̂_m mean=0.004 (t=1.10, not significant).
- Diagnostics now surfaced in `results.txt` ("III-b" section) and saved to
  `results/{apartment,house}/anchored_diagnostics.csv`, not silently discarded.

**Not yet done:** T=5/T=15 sensitivity grid; bootstrap SEs for the anchored estimator (guarded
with `NotImplementedError` if `n_boot>0` + anchored, since the existing `bootstrap_se` would
silently produce SEs inconsistent with Proposition 2(ii)); Phase 3 (paper rewrite).

## Phase 3 progress (2026-09-15)

**Step 1 done (commit `70da8de`):** formal propositions added to
`sections/A-robustness.tex` (new appendix "Identification of ρ_m: A Formal Treatment") —
Proposition (scale non-identification), Corollary (old ratio estimator = specification-test
statistic), Proposition (what's identified without an anchor), Lemma (model-implied bounds),
Assumption A, Proposition (point identification under the anchor). Written directly (the
deriving `micro-theorist` agent's transcript expired, could not resume) — flagged for a
dedicated proof-check pass before submission. Compiles cleanly, 2-pass, no undefined refs.

**Still to do:** rewrite §4.3 identification narrative (retract composition-bias story, replace
`eq:rho_estimator`, update Table 4 with anchored numbers), `A-robustness.tex`'s J-test/λ̂_m
robustness table, abstract/conclusion ρ̂ magnitude retraction, §5 policy-section prose
(targeting language currently attributes to ρ what should attribute to b_m/anchor β1),
`econ-academic-editor` + `realestate-finance-writing` pass, then Phase 4 review.

## Phase 3 — §5 policy section done (commit 6a5179d), a real bug found along the way

While refreshing §5's numbers, found and fixed a genuine bug: `compute_market_subsidies`/
`compute_subsidy_grid`/`estimate_c0_bounds` were combining the TRUE anchored `rho_hat` (~0.5)
with `market_params`'s DiD β1 for the equilibrium solve, while `c0_hat` had been computed
assuming that product equals β1,m alone (i.e. implicitly ρ=1). This gave 44/45 apartment markets
the wrong regime classification ("full_unraveling" instead of "mixed_strategy") and wrong
R̄_m/S*_m values. Fixed in `run.py` (a `rho_hat_for_thresholds={m:1.0}` substitute passed
specifically to those three functions, preserving b_m consistency; the real anchored `rho_hat`
untouched for Table 4/reporting). Verified 100% "mixed_strategy" now, consistently.

Regenerated: full pipeline, static subsidy figures, and the two choropleth maps
(`cartopy-specialist` agent — also fixed two unrelated pre-existing layout bugs in
`scripts/make_subsidy_map.py`). §5's prose rewritten with corrected numbers throughout, the
CDH-vs-PP regime narrative retired (no CDH markets survive under the anchored estimator), and
the ρ_m-vs-β1,m targeting-language conflation fixed. Conclusion's aggregate-budget citation
corrected a second time (was €11.9bn/€35.1bn from the buggy run, now €9.8bn/€33.0bn correct).

**Still open:** `A-robustness.tex`'s threshold-sensitivity table (still cites old baseline
90.9%/3.42%/14.0%) needs the whole comparison re-run under the anchored estimator; the λ̂_m/J-test/
concentration diagnostics table for the robustness appendix; `econ-academic-editor` +
`realestate-finance-writing` polish pass; Phase 4 review. Minor housekeeping noted but not done:
two stale unreferenced map PDFs, map file-size optimization (both low priority, from
cartopy-specialist's report).

## Phase 3 — narrativize pass on §4.5.2 and §5.1-5.2 (2026-09-15/16)

Ran the new `/narrativize` skill (built this session, see below) on §4.5.2 "Structural
Estimates and Economic Interpretation" and on §5.1-5.2 "Motivation"/"Extended Seller Problem".
Both independently verified (compile clean, zero stale draft-reference language, numbers
spot-checked against Table 4) and humanized (detect-only; both came back mostly clean, a few
stylistic-judgment flags, nothing auto-applied). A stale, retracted "composition bias"
paragraph was found and deleted from §4.5.2 first (substantive fix, done directly, not via the
skill). While narrativizing §5.1-5.2, `micro-theorist` sanity-checked the weak-dominance
argument and the partial-pooling cancellation claim against their appendix proofs: both check
out; found one pre-existing, non-propagating strict-vs-weak inequality slip in the (now-removed)
`eq:threshold_condition` derivation, flagged not fixed. Also fixed the pre-existing
40/100-vs-49/104 market-count inconsistency in "Two Price Gaps from the Reform" (§4.4.2): the
stated volume-filter stage was stale (40/100); `results.txt` shows the true current counts are
81/114, feeding into the already-correct 49/104 → 45/97 chain Table 4's footnote documents.

## Phase 3 — threshold-sensitivity table regenerated under the anchored estimator (2026-09-16)

Built `scripts/run_threshold_robustness.py` (a reusable sweep, mirrors `run_pipeline()` through
the anchored `msm_result` for the 4 specs × 2 property types, skipping bootstrap/subsidies/
figures). Regenerated `tab:robustness` in `A-robustness.tex` and rewrote its three interpretive
paragraphs. Key finding: $\hat\rho_m$ is now *exactly* invariant to the $\sigma_1$ assignment
(it never enters the anchored formula at all) — a cleaner version of the old "insensitive"
finding, which used to report "less than a tenth of a percentage point." Market counts (N) per
cell are unchanged from the old table, confirming only the estimator changed, not the sample.
Removed the old closing claim that "boundary saturation in $\hat\rho_m$ and the regime
classification" are unaffected by the threshold choice — both are artifacts of the retired
ratio estimator and no longer apply once $\rho$ is point-identified. Raw sweep output at
`results/_robust/threshold_sensitivity_summary.csv` (gitignored, regenerable).

**Found, not fixed (flagging for a later pass):** `sections/04-structural-draft.tex:546` cites
`Appendix~\ref{app:robustness}` for a truncated-post-reform-window robustness check (λ̂_m stable
under 1-2yr vs the full 3yr post-window), but that check was never actually written into the
appendix — it exists only as the year-by-year trajectory data from an earlier session
(`quality_reports/diagnostics/rho-anchor-dynamics/`, native memory
`rho_anchor_dynamics_table.md`). The citation is currently unbacked; either write the check into
`A-robustness.tex` from that existing data, or soften the in-text claim.

**Still open:** the λ̂_m/J-test/concentration diagnostics table for the robustness appendix
(Appendix D of this plan already specifies it; not yet built); the truncation-window citation
gap above; bootstrap SEs for the anchored estimator (still `NotImplementedError`-guarded);
`econ-academic-editor` + `realestate-finance-writing` polish pass; Phase 4 review
(`structural-micro-reviewer`, `methods-referee`/`--peer --r2`, `/audit-reproducibility` on
Table 4); two stale unreferenced map PDFs, map file-size optimization (low priority).

## Phase 5 — Bastien's introduction/abstract review comments (branch `review`, 2026-09-21)

### Context

Bastien is doing a line-by-line pass on `sections/01-introduction-draft.tex` and the abstract
(`main.tex`), on a new `review` branch cut from `fix/rho-identification-gmm`. He gave 8 numbered
comments. Several are pure questions/requests for explanation (must be answered before any text
is touched); others are direct edit requests. Investigation for the question-type comments is
done; this section is the resulting plan for what to write, per comment, for his approval.

### 1. "Doesn't the apartment wedge mean we're closer to Complete Adverse Selection? What's the
share of disclosed bad EPC ratings?" — **answer, no edit proposed**

Dispatched to `micro-theorist` with the full model apparatus. Verdict, worked through the
ordering $\rho\beta_1\bar\theta$ (CDH) $>c_0$ (PP) $>\rho\beta_1 e(1)$ (CAS) algebraically:
**it's backwards.** $\Delta(e(\sigma_0))$ is *decreasing* in the hiding rate $\sigma_0$ (more
hiding contaminates the pool, dragging inferred quality down), so a premium sitting *above* the
anchored $\hat c_{0}$ places the market on the CDH (low-hiding) side of the ordering, not the CAS
(high-hiding) side. This is independently corroborated by the raw ADEME hiding rate: only 15.2%
of informed low-quality apartment sellers hide (84.8% disclose their bad rating), which is
nowhere near CAS's $\sigma_0^*=1$. The agent also flagged that "regime classification" is the
wrong diagnostic tool here at all — $\hat c_{0,m}=\hat\beta_{1,m}\hat e^*_m$ is mechanically
confined to the PP band by the estimator's own construction (already noted in §4.5.2), so asking
whether it "falls in" CDH/PP/CAS is tautological. The informative objects are $\hat\sigma_0$
(genuine, non-tautological) and $\hat\lambda_m$ used as an over-identification test, not a
regime locator. Correct one-line characterization: apartments show genuinely low but non-zero
concealment (~15%) in which the model's PP-indifference restriction is rejected, not a market
secretly near-universal hiding.

**No text change proposed.** This is worth Bastien reading before deciding whether ¶9's framing
needs anything — the current text ("a genuine specification tension we report rather than
explain away") is already consistent with this finding (it doesn't claim a regime), so no fix is
obviously needed, but flag for his judgment.

### 2. Abstract: "...a divergence we trace to a measurable over-identifying wedge rather than
paper over" — **explanation + revision options**

Confirmed by reading the exact current text (`main.tex:40`): this is a genuine grammatical
fragment, not intentional phrasing. "Paper over" is a transitive idiom (to paper over
*something*) and its object was dropped, almost certainly during an earlier narrativize/edit
pass on this exact sentence. The intended meaning, reconstructed from context and from the
identical (complete) idea in the introduction's ¶9-10 and §4.5.2: *we don't just explain away or
smooth over the apartment/house discrepancy — we report it as a measurable, statistically
precise quantity (λ̂_m, the over-identifying wedge) instead.*

Proposed fix (pick one):
- **(a)** "...a divergence we trace to a measurable over-identifying wedge rather than paper over
  the discrepancy."  *(minimal — just restores the missing object)*
- **(b)** "...a divergence we trace to a measurable, precisely estimated over-identifying wedge,
  rather than treat it as noise."  *(names what "paper over" was gesturing at: not dismissing it
  as sampling error)*
- **(c)** Drop the "rather than paper over" clause entirely: "...a divergence we trace to a
  measurable over-identifying wedge, reported directly rather than resolved by construction."
  *(matches the phrase already used at the end of the removed ¶10, "not resolved by
  construction" — ties abstract and intro to the same framing)*

Recommendation: **(c)** — it echoes language already established elsewhere in the paper rather
than introducing a new formulation, and reads cleanest.

### 3. "'The reform changed what a disclosed score means without changing... the cost of
obtaining a certificate, or the legal consequences of remaining silent.' Is this entirely true?
Check the regulation." — **fact-checked, footnote proposed**

Researched via WebSearch (French legal/trade sources on DPE opposability and the July 2021
methodology change). Findings, sentence-clause by clause:

- **"the legal consequences of remaining silent" unchanged** — accurate. The obligation to
  furnish a DPE at sale, and liability for not doing so, predates 2021 under *loi ALUR* (Art.
  L271-4 CCH). July 2021 added *opposability of a disclosed score's content* (buyer recourse
  against misstatement) — a different thing from the penalty for providing none at all. This
  matches what §4.4.1 already says correctly.
- **Attribution is imprecise.** The intro currently attributes the July 2021 change to *loi
  Climat et Résilience*. The opposability provision's actual legal basis is **Article 179 III of
  loi n°2018-1021 du 23 novembre 2018 (loi ÉLAN)**, which amended CCH Articles L271-4 and
  L134-3-1 with a scheduled effective date of **July 1, 2021**. *Loi Climat et Résilience* was
  promulgated **August 22, 2021** — a separate, later law (rental-ban calendar, new consumption
  thresholds) that the paper already cites correctly elsewhere for the F/G rental ban. The intro
  conflates the two.
- **"the cost of obtaining a certificate" unchanged — genuinely uncertain, not clean.** The DPE
  calculation methodology was completely overhauled on the *same date*, July 1, 2021 (replacing
  the old invoices-based method with the physical-characteristics-based "3CL-2021" method),
  specifically *in order to* make the DPE reliable enough to be made opposable (Arrêté du 31 mars
  2021). Trade sources describe this as more labor-intensive for diagnosticians (longer site
  visits, more data points), which "mechanically" puts upward pressure on price — but fees are
  unregulated (each diagnostician sets their own), and no source gives a clean quantified
  before/after comparison. I can't confirm or refute "unchanged" cleanly either way.

Proposed changes:
1. Fix the attribution: replace "Under the *loi Climat et Résilience*" with something like
   "Under a 2018 reform (loi ÉLAN) that took effect on July 1, 2021" — or keep *loi Climat et
   Résilience* only for wherever the rental-ban margin is actually being invoked, and use the
   correct ÉLAN citation here.
2. Soften the audit-cost clause given the genuine uncertainty — e.g. drop "the cost of obtaining
   a certificate" from the list, or qualify it ("the nominal audit fee, which we do not track
   before/after the reform").
3. Add a footnote with the citations: *loi n°2018-1021 du 23 novembre 2018 (loi ÉLAN), art. 179
   III; Code de la construction et de l'habitation, art. L271-4, L134-3-1; Arrêté du 31 mars 2021
   relatif aux méthodes et procédures applicables au DPE.*

This is Bastien's call on exact wording; presenting the correction and footnote content for
approval rather than drafting the final sentence unilaterally, since it's a legal-citation change
he should sign off on precisely.

### 4. "'four assumptions. These are' — restructure to a colon + list" — **direct edit**

`sections/01-introduction-draft.tex:46`, current: "The unraveling prediction rests on four
assumptions. These are (a)~that buyers know sellers possess private information about quality,
(b)~that disclosure is costless, (c)~that disclosure is credible, and (d)~that buyers are
homogeneous in how much they value the disclosed attribute."

Proposed: "The unraveling prediction rests on four assumptions: (a) buyers know sellers possess
private information about quality, (b) disclosure is costless, (c) disclosure is credible, and
(d) buyers are homogeneous in how much they value the disclosed attribute." (drops the redundant
"that... that..." repetition along with the sentence break, matches this paper's established
"X: (i)/(ii)/(iii)" list convention used elsewhere in propositions/assumptions).

### 5. Add the negotiation-margin literature to ¶6 — **direct edit, citations already in the bib**

`sections/01-introduction-draft.tex:101-104`: "We use them to estimate the mapping from listing
to realised sale price, which supports treating the listing price as the relevant outcome, since
the negotiation margin in French residential sales is small and most properties transact at or
near list price." — currently uncited, but this exact claim (with the exact same three sources)
is already made and cited in §4.2.2 "Payoffs and Hiding Costs"
(`sections/04-structural-draft.tex:99`, footnote). Confirmed all three keys exist in
`DPE_library.bib`: `merlo_bargaining_2004`, `genesove_loss_2001`, `friggit_marche_2013`.

Proposed: append `\citep{merlo_bargaining_2004, genesove_loss_2001, friggit_marche_2013}` at the
end of that sentence (matching, not duplicating, the fuller footnote treatment already in
§4.2.2).

### 6. Give a sense of what ρ̂/ĉ0 mean — **my view + options**

My view: reuse the benchmark the paper has already earned rather than invent a new one. §4.5.2
(`sections/04-structural-draft.tex:495-497`) already establishes ĉ0 (2.4%/3.5%) is "of the order
of a third of the notary bill, and roughly a quarter to a third of the minimum deposit a bank
would demand" — fully derived, already defensible, no new claim needed. ρ̂ (49.5%/45.8%) is
already fairly self-interpreting as a share ("about half"), so it may not need its own benchmark.

Options for ¶9:
- **(A)** Add a compressed one-clause version of the notary/deposit comparison for ĉ0 only
  (cheapest, reuses an existing, already-verified number).
- **(B)** Compute a euro-denominated version (2.4%/3.5% of a representative apartment/house
  price) for a more concrete, less abstract feel — needs pulling median price-per-m² × median
  area from `market_estimates.csv`/`results.txt`, not yet done.
- **(C)** Benchmark ρ̂ and ĉ0 against the energy-label capitalization literature already cited in
  ¶13 (`brounen_kok_2011`, `hyland_lyons_2013`, `fuerst_energy_2016`, `frondel_power_2018`,
  `myers_mandatory_2022`) to show the magnitudes are the same order as documented elsewhere —
  ties into literature the paper already engages, reinforces "these numbers are economically
  sane."

Recommendation: **(A)**, optionally combined with **(C)** in one sentence if Bastien wants both
a concrete dollar-figure-style anchor and a literature anchor without inflating ¶9 much.

### 7. Remove ¶10 ("Our inferences survive the natural alternatives...") from the introduction
— **direct edit**

`sections/01-introduction-draft.tex:162-175`. Confirmed this is robustness/identification-defense
material (the ρ≤1 violation count, the cross-segment out-of-sample check, the sensitivity-check
list) that substantially duplicates content already in §4.4.4 and the robustness appendix — it
reads like appendix/results material, not introduction material, matching Bastien's read.

Proposed: delete the paragraph wholesale. ¶9 currently ends "...finds the structural estimates
essentially unchanged." and ¶11 begins "Our paper contributes to the literature..." — these flow
fine back-to-back with no further seam edit needed (checked by reading both neighbors).

### 8. New paragraph on the policy-extension (renovation subsidy) results — **draft for approval**

The introduction currently never mentions the renovation-subsidy extension's own findings
(uniform-subsidy inefficiency, cost-share heterogeneity, aggregate budget numbers) even though
it's roughly a third of the paper (§5) and the headline policy result. Drafted for insertion
after ¶12 (the energy-efficiency-gap contribution paragraph) or as its own ¶12.5, using numbers
already established in §5.5/Conclusion (cost-shares 54.0%/57.0%, aggregate €9.8bn/€33bn vs
MaPrimeRénov's ~€4-5bn budget, three complementary instruments):

> "The model also speaks to renovation policy. Extending the framework to an endogenous upgrade
> decision, we show the minimum subsidy needed to make renovation privately worthwhile reduces,
> in the empirically dominant partial-pooling regime, to the price gap between verified high and
> low quality alone — invariant to enforcement against hiding and to how many sellers are
> informed, which act on separate margins instead. A uniform national subsidy is accordingly
> inefficient: the required cost-share the state must cover ranges from zero to the full
> renovation cost across markets, averaging just over half in markets that need support at all,
> and aggregate programme costs at plausible renovation-cost benchmarks run to €9.8-33 billion,
> two to eight times MaPrimeRénov's current annual budget. Efficient targeting requires
> conditioning subsidy design on local market composition rather than applying one national
> rate."

Placement and exact wording are Bastien's call; presenting a full draft paragraph since comment
8 asked for one directly, not options.

### Verification (once approved and implemented)

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`, twice,
  zero undefined references (¶10's removal and the new ¶8 insertion both touch cross-references
  to `\ref{app:rho_identification}`, `\ref{app:robustness}` elsewhere in the intro — confirm none
  become orphaned).
- Independently re-verify the abstract rewrite (item 2) and the new policy paragraph (item 8)
  against the actual numbers in `results/{apartment,house}/results.txt` and §5.5 before treating
  them as final — this plan's drafted numbers are transcribed from earlier verified session work,
  not re-derived fresh.
- Grep for stale draft-reference language and em-dash/colon-tic density in any newly drafted
  prose (item 8's paragraph), per the punctuation-discipline standard now built into
  `/narrativize`.
