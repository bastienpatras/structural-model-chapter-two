# Plan: promote the limited-attention model (§4.6) to the main model

Status: APPROVED 2026-10-30 (branch `sections-4-5`).

## Context

The paper already runs on the attention model in practice. The Policy section (`main.tex:64-361`) is stated only under attention, the abstract and conclusion already mention it, and its fit is better. But §4 still leads with the core model (ψ=1), §4.6 is labelled an "extension", and the front matter (abstract, §1, §2, §3) tells the unraveling-plus-composition story and treats attention as an add-on. Two further problems came out of the micro-theorist audit: the hiding cost c₀ has two estimands (core ĉ₀ = β̂₁ê*, attention ĉ₀ = Δ̂; `04-attention:461` vs `main.tex:72`), and its interpretation (expected sanction) is not stated to be independent of buyer attention.

Goal: attention is the model; the core model is the full-attention benchmark (ψ=1), nested and proved once.

## My view (for the user)

Agree in direction, with five caveats that shape the plan:

1. **Keep the core as the ψ=1 benchmark, do not delete it.** Referees need the Grossman–Milgrom-type benchmark, and `PLAN.md` decision 2 says the structural work stays in full. Houses have ψ̂ ≈ 1, so the core model *is* the house model.
2. **"Fits the data" is partly by construction.** With C^def=0, ψ is just-identified from the same wedge λ̂ that rejected the core model in apartments. It is one free parameter per segment absorbing that wedge. The claim becomes credible only with over-identifying evidence: the 2022 energy-display rule as an attention test, the year-split of 1−ψ̂, the segment contrast (the only robust object, per `04-attention` identification section), the slack/violation counts. Lead with the contrast, not the ψ level.
3. **Fix c₀ first** (Fix A from the audit), because leading with attention puts it in the abstract.
4. **Proof gaps become front-page.** `prop:equilibrium`'s proof is delegated to by `A-attention:150`; exact-pricing orderings for the three-segment demand are conjectured, not proved (`A-attention:360-363`); `lem:profit` label sits after a `\subsection*`.
5. **Numbers are provisional** (G2 certificate dates, G3 certified consumption re-pulls) and the σ₁ finding (`FINDING-sigma1.md`) still qualifies "concealment cost". Headline numbers should not be frozen into the abstract until G2/G3.

## Decisions needed before execution (recommended default in bold)

- c₀ headline: **single estimand c₀ = Δ̂ in Partial Pooling (attention reading), with the core β̂₁ê* reported as the ψ=1 value** vs keep β̂₁ê* as headline.
- Core model in the text: **ψ=1 benchmark inside §4 (one subsection + corollaries), core proofs stay in appendix** vs move whole core to appendix.
- Title: **keep "When Silence Pays"**, add attention in abstract/keywords only.
- Pace: **model section first, then front matter, then policy/conclusion/appendix**, with a checkpoint after each (onboarding cadence).

## Phase 1 — Pin down c₀ (blocking)

- `04-structural:100-102`: define c₀ = r + q·F (regulatory/legal expected cost), q set by regulator/notary, independent of buyer type and attention; move negotiation and fall-through into Γ; fix "paid unconditionally on sale" wording; fix c₁ "forgone revenue premium" double-count against b.
- State as an assumption in the unified setup: c₀ does not depend on (ρ, ω₀, ω₁, C^def). One sentence naming the buyer-detection channel (Fix B) as excluded, signed: strengthens ∂σ₀*/∂ψ<0, leaves R̄ = b unchanged.
- Index estimates ĉ₀^{ψ=1} (= β̂₁ê*) and ĉ₀^{att} (= Δ̂); delete "paper's measure" at `04-attention:461`; align `main.tex:72`; say at `04-attention:379` which bounds the deadweight loss.
- No `agencies` language (memory: `feedback_no_agencies_in_paper`).

## Phase 2 — Restructure §4 (`04-structural-draft.tex` + `04-attention-draft.tex`)

New order, merging the two files into one `\section{Model}` (keep all existing `\label`s to avoid breaking refs; only promote heading levels):

1. Motivation: attention-first, ψ=1 benchmark named. Source: `04-attention` Motivation (L18) + `04-structural` L12.
2. Setup: S L73-166 environment/payoffs/who-hides/belief (unchanged) + AT L49-195 attention assumption, cost form, default cost, ẽ. Single set of notation; drop "as in Section 4.1" scaffolding (`AT:52,64`).
3. Equilibrium: statements from AT (`prop:att_incentives`, `cor:att_hq`, `prop:att_equilibrium`, `prop:att_seller_types`, `cor:att_ordering`, `cor:att_band`, `prop:att_cs`) as the main results. Add **"Full-attention benchmark (ψ=1)"** corollary collecting `prop:premium`, `cor:hq_disclose`, `prop:equilibrium`, `prop:comparative_statics`, `cor:rho`, `prop:pi`, `prop:c0` (they stay labelled and proved in the appendix). Rename `att_` labels only if cheap; otherwise leave (labels are invisible).
4. Welfare: promote AT:378 paragraph + S:346 to one paragraph; resolve the unfulfilled forward promise at S:346 ("Section sec:policy" formal efficiency) — either delete or point to `rem:welfare`.
5. Identification: S L348-435 (reform, two price gaps, registry beliefs, energy anchor) + `prop:att_identification`. Re-read which of `prop:scale_nonid`/`prop:what_identified`/`prop:anchored_identification` change meaning (ρ→ρω₁; c₀ = Δ̂).
6. Estimates: `tab:did_results` panel for ψ=1 benchmark + `table_attention_body`; ψ_δ by segment, contrast, over-id checks (display rule, year-split).

Cross-file refs that must be rewritten: AT→S list (e.g. "model of Section~\ref{sec:equilibrium} (ψ=1)" at AT:340/379; "as before"); S→AT forward pointers (S:62, 433, 507, 529, 539, 545, 566-567, 592) become internal.

## Phase 3 — Proofs and appendix (careful)

| Item | Action |
|---|---|
| `prop:equilibrium` proof (`M:541`) | Rewrite self-contained for general ψ (ψ=1 corollary); `A-attention:150-154` currently delegates to it; fix wrong target `Section~\ref{sec:beliefs}` for `lem:belief_monotone`. Use micro-theorist. |
| `eq:premium_derived` / `eq:premium` proof (`M:581`) | Keep: pricing rule used by `AT:145`, `AA:74,99,363`. Currently asserted, not derived from logit demand. State or prove it. "exact-pricing solver of Section equilibrium" (`AA:646,694`, `M:240`) refers to a solver not described anywhere: describe or cut. |
| Preliminary price-sensitivity lemma + `lem:profit` (`M:445-512`) | Single-segment; does not cover the (1−ρ) segment or three-segment demand. Either re-derive for `eq:demand_att` or state as conjecture honestly. Fix `lem:profit` label placement. |
| `prop:premium`, `cor:hq_disclose` (`M:513,525`) | Keep as ψ=1 proofs; `cor:att_hq` is weaker (σ₀*<1 only) — check the U-shape/σ₁ discussion still consistent. |
| `prop:comparative_statics` (`M:616`), `cor:rho` (`M:669`) | Keep Case 3 ∂σ₀/∂π (cited by `AA:288`) and PP-band argument (cited by `AT:355`). |
| `prop:pi`, `prop:c0` (`M:688,711`) | No attention analogue for regime movement in π; re-derive for Δψ or keep as ψ=1 and say so. |
| AR `prop:scale_nonid`, `prop:what_identified`(ii), `lem:model_bounds`, `prop:anchored_identification` | Restate with ρω₁; (ii) c₀ = β₁e replaced by c₀ = Δ̂ (or both). `lem:model_bounds`(i) stays: it is the ceiling attention breaks. |
| `A-attention.tex` sections 19-304, 397-641 | Keep. Rename appendix title "extension" wording. Policy proofs unchanged. |
| Lost with ψ=1-only routes | Regime-free uniqueness in CAS (attention gives existence only), strict 0<Δ*<b ordering, π regime-move: document explicitly in the benchmark corollary. |

Run `/blast-radius` before and after: every `\ref` to a moved/renamed label.

## Phase 4 — Numbers and macros

- Core estimates (ρ̂ 49.5/45.8, ĉ₀ 2.4/3.5, σ̂₀ 15.2/6.8, π̂ 51.8/41.7) are hard-coded in abstract, intro, conclusion, `04-structural:460-585`, `A-robustness:39-94`, and `tab:did_results` is hand-typed. Generate them as macros from `scripts/compute_attention.py` (or a sibling) so there is one source.
- Macros: `attCzeroBase*` and `attCzeroCoreMean*` are duplicates; retire `attRmse/Corr/Resid{Core}`, `attRbarCore*`, `attCostCore*` only if the comparison text goes. Keep as ψ=1 benchmark values otherwise. Consider renaming the `att` prefix (372 macros; mechanical) — **list as suggestion, do not do unrequested**.
- Re-run `compute_attention.py` and `mc_attention_estimator.py` after G2/G3; do not freeze abstract numbers before then.
- Figures (route via `pyplot-specialist`): `fig_att_F2a_belief` and `fig_att_F1_fit` become the lead motivation exhibits; `equilibirum_outcomes.png` and `model_dynamics.png` have no generator and need an attention dimension, redraw.

## Phase 5 — Front matter (author-voice; propose drafts, user approves, per proofreading protocol and `[AUTHOR REWRITE]` tags)

- `main.tex` abstract (L42-46), keywords (L49: add limited attention / salience), JEL (L51: behavioural code), comments L22-25, title (decision).
- §1 (`01-introduction-draft.tex`): ¶1/¶3 puzzle (silence priced above a verified efficient rating, which the belief-only model cannot reach); ¶4 assumption audit (a)-(d) add attention; ¶5 reorient; ¶8 model motivation; ¶9 findings (L146-172, replace core headline with attention contrast, delete "extension"); contribution 1 and 2 (L174-200) add attention as co-equal; ¶12.5 policy; ¶13 literature strand 1; ¶14 generalizability. No roadmap paragraph, no notation in the intro (`DIAGNOSIS.md`).
- §2 (`02-unraveling`): "Two Departures" (L57-90) becomes three, or (d) is reframed; figure `fig:equilibrium_outcomes` gains attention; closing L106-113.
- §3 (`03-setting`): requirements list (L245-248) gains fifth item (silence above verified efficient), fact 1 (L128-134) check against `\attLevelGapPre/Post`; L51 display rule as attention test.
- Honour the "strictest constraint wins front matter" rule (JF/JFE/RFS), apartment-led framing (`V2-QUEUE.md`), and the 2026-09-21 policy-balance note (do not over-index on policy).

## Phase 6 — Policy, conclusion, appendix text

- `main.tex:64` rename "Policy Extension: Renovation Subsidies"; L70-74 invert nesting (attention is the model; full attention is the special case), delete "for reasons of fit"; remove or fold L240 comparison with core R̄ if the core R̄ is no longer a headline.
- Conclusion (L363-382): "two departures" becomes three; rewrite the "central theoretical result" paragraph (L371-372): premium = c₀ in Partial Pooling holds as the identity Δ* = c₀ under attention in both segments, the rejection becomes the ψ<1 finding.
- Appendix: retitle `A-attention` ("extension"); update `A-robustness:25` ("Under the limited-attention extension") and core ρ̂/ĉ₀ quoted at L39-94.
- Re-check ρ̂ boundary counts (40/42, 54/76) in `APPENDIX-GAPS.md`: stale after the anchored fix (T=10).

## Execution

User direction (2026-10-30): approved, run in auto mode, and **re-run the humanizer after every writing step** (each Phase 1, 2, 5, 6 prose edit). Per `writing-with-ai.md` the humanizer stays advisory: each suggestion is checked against the source (claim words, scope phrases, dangling connectives, per MEMORY [LEARN:review]) before it is applied, and rejected ones are logged. Defaults in "Decisions needed" are taken as bolded. Where a passage carries `[AUTHOR REWRITE]`, I draft it and keep the tag so the author can still rewrite it.

Contractor mode after approval, with a milestone check-in after Phases 1, 2-3, and 5 (onboarding cadence). Agents: `micro-theorist` for Phase 1/3 proofs, `pyplot-specialist` for figures, `econ-academic-editor` for drafting Phase 5 text (author reviews), `structural-micro-reviewer` for paper-code consistency.

Session log to `quality_reports/session_logs/` after approval and incrementally.

## Verification

1. `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex`: zero undefined references/citations, no overfull surprises; grep log for `undefined`.
2. `grep` every `\ref{...}` against `\label{...}` (script or `/blast-radius`).
3. `./scripts/backtest.sh` and `python3 scripts/check-repo-hygiene.py`.
4. `/audit-reproducibility`: every quoted number matches a macro or script output; after G2/G3 re-pull, all macros regenerated.
5. Proof check: independent `micro-theorist` read of rewritten `prop:equilibrium` proof and the benchmark corollary (ψ=1 reduces exactly to core statements), counterexample-hunt per `theory-proving.md`.
6. Fenced independent review of the final model section (`review-fencing.md`: neutral copy, prior verdicts withheld), then `/adjudicate-review` on findings. Humanizer output is advisory only and each edit is checked against source (see MEMORY [LEARN:review]).
7. Bookend: confirm the attention model leads in abstract, §1, §4, policy, conclusion, and that ψ=1 reproduces every core result.

## Suggestions (not in scope unless you ask)

- Rename the `att` macro prefix.
- Delete unused core `results/tables` and `fig_subsidy_*` artifacts.
- Heterogeneous-cost extension (`V2-QUEUE.md`).
