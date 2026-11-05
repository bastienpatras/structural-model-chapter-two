# Plan: check the appendix and review every proof (humanizer advisory on each reviewed part)

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Copy to `quality_reports/plans/2026-11-04_appendix-proof-review.md` on approval. No commit. Review only: no proof, assumption or estimand is changed without the author.
Supersedes the abstract plan (done; the abstract in `main.tex` is final for now, shorter variants in `paper-real-estate/ABSTRACT-VARIANTS.md`).

## Context
The appendix now carries the derivations that Sections 4 and 5 point to, and it has been edited piecemeal during the restructure (limited attention is THE model; the full-attention version moved to `A-benchmark.tex`; Section 5 proofs live in `A-attention.tex`). It has not been read as a whole since. `APPENDIX-GAPS.md` (2026-08-13) says the proofs are "the part nobody will contest", but the proofs are now different proofs, and a proof written by an agent is a claim, not a theorem (`.claude/references/theory-proving.md`). Goal: find (a) wrong or incomplete proofs, (b) statements that no longer match the main-text version, (c) stale full-attention or pre-restructure language and broken cross-references, and (d) prose tells, per part.

## Inventory (about 1,700 lines)
| Part | File and lines | Content |
|---|---|---|
| P1 | `A-attention.tex` L1-255 | Cost form; proofs of lem:att_prices, prop:att_incentives, cor:att_hq, prop:att_equilibrium, prop:att_seller_types, cor:att_ordering |
| P2 | `A-attention.tex` L256-387 | Band fit, non-strategic silence, payoffs by type and regime; cor:att_band, prop:att_cs, prop:att_identification |
| P3 | `A-attention.tex` L388-485 | Exact logit pricing, effective belief, hiding costs, ratio-of-sums estimator, qualifications to the estimates |
| P4 | `A-attention.tex` L486-838 | Proofs for Section 5 (threshold, subsidy_ge, instruments, att_saving, lem:renov_behaviour), alternative readings, ceilings, numerical illustration |
| P5 | `main.tex` L430-726 and `A-benchmark.tex` (165) | Lemma belief_monotone and the full-attention-benchmark proofs; benchmark existence, uniqueness, comparative statics |
| P6 | `A-robustness.tex` (320) | Threshold x sigma_1 robustness; formal rho identification (scale non-identification, composite and c0, anchor), supply-side stability, naive ratio, FA hiding cost |
| P7 | `main.tex` L359-428 | Figures section, Data and Model Objects |

## Method per part (parallel, one fenced reviewer each)
1. **Fenced copy.** The part and what it cites go to a neutral copy outside the checkout (scratchpad, neutral filenames, no plans, no prior verdicts, no `APPENDIX-GAPS.md`), per `review-fencing.md`. Reviewer: `micro-theorist` (P1-P6); P7 goes to `structural-micro-reviewer` or `proofreader` equivalent.
2. **Own reading first.** The reviewer states what each proposition should say given the model (primitives in Section 4), then reads the proof.
3. **Proof discipline** (`theory-proving.md`): for each proof, a contract (hypotheses used, claim, regimes covered), a counterexample hunt on the statement (numerical spot check with sympy/numpy where a closed form is claimed), the "does the proof use an assumption the statement omits" check, and boundary cases (pi in {0,1}, psi in {0,1}, empty pools, regime edges, max with zero).
4. **Cross-checks** (mechanical): every `\ref`/`\eqref` target exists and says what the citing sentence claims; statement in the appendix equals the statement in the main text (Sections 4-5); notation (psi vs psi_delta, b vs beta_1 hat, zeta, R vs R-hat); stale "benchmark / full attention / classical" wording; units (log points vs fraction vs percent); macros used in the appendix exist and match `attention_macros.tex`.
5. **Findings schema.** `FINDING` objects (`orchestration-schemas.md`), validated with `scripts/validate-findings.py` (smoke-test the validator first); severities CRITICAL / MAJOR / MINOR; refute-biased verifier on every CRITICAL before it ships; `mechanical: true` only for labels, references, units, typos.
6. **Humanizer, advisory, per part.** After each part's review: a humanizer pass over that part's prose (not the equations), suggestions listed with current text and replacement, nothing applied. Reports saved to `quality_reports/humanizer/` and `quality_reports/appendix-review/` (see Outputs).

## Parallelism and cost
6 micro-theorist reviews (P1-P6) in two waves of three, 1 reviewer for P7, then 1 verifier fork per batch of CRITICAL findings, then the humanizer passes (run by me, advisory). About 8-10 agents in all; each review is about 150k tokens. A cheaper variant (reviewing P1, P4 and P6 only, the proofs the main text leans on) is in the decisions below.

## Outputs (all new files are reports, nothing in the manuscript changes)
- `quality_reports/appendix-review/2026-11-04_P1..P7.md` (one per part: contract table, findings, counterexample log).
- `quality_reports/appendix-review/2026-11-04_summary.md` (consolidated ranked findings, what needs the author, what is mechanical).
- `quality_reports/humanizer/2026-11-04_appendix-advisory.md` (per-part suggestions).
- `APPENDIX-GAPS.md` status check: which of its seven items are now stale (read-only list in the summary; the file itself is not edited).

## After the reviews (needs your yes before any edit)
Mechanical fixes (labels, references, units, typos, stale wording) can be applied in batches with a compile after each. Anything touching a proof step, an assumption, an estimand or reporting language comes back to you, as in `orchestrator-protocol.md` (fix step). Fresh re-review of every edited proof before it counts as repaired.

## Verification
`cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex` twice after any edit; zero undefined/multiply defined labels; `scripts/validate-findings.py` exit 0 on each findings file; every finding cites a rule or a failing case; numeric spot checks stored with their code in the scratchpad and quoted in the report.

## Decisions for the author
- **Scope:** all seven parts (recommended), or only the proofs the main text rests on (P1, P4, P6)?
- **"Humanizer on each review":** I read it as a humanizer pass on each reviewed part's prose. If you meant the reviews' own text, say so; the effect is smaller.
- **Fixes:** report first and bring the findings to you (recommended), or apply mechanical fixes as they come?
- **External check:** a frontier-model oracle review of P1 and P4 (`/oracle-review`, `external-oracle-process.md`) is possible but costs another round and sends the proofs outside; recommended only if a CRITICAL survives the verifier.
