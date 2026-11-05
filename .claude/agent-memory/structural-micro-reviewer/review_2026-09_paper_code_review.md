---
name: review_2026-09_paper_code_review
description: Full paper-code review 2026-09-14 (rev ee0e311) — status of σ1 circularity and ρ̂-boundary findings, plus new critical reproducibility gaps. Report saved to quality_reports/paper_review_structural-micro_paper-real-estate.md
type: project
---

Full review written 2026-09-14 at rev `ee0e311` (branch `paper-real-estate`). Report:
`quality_reports/paper_review_structural-micro_paper-real-estate.md`. Read that file for full
detail with line citations; this note is the durable summary for future sessions.

**σ1 circularity ([[identification_strategy]], `FINDING-sigma1.md`) — nuanced, not simply
"open" or "fixed":**
- Paper text (`sections/04-structural-draft.tex:60-72`, `sections/A-robustness.tex`) is now honest:
  explicitly states σ₁*=0 is a maintained assumption, not a tested result, and reports a registry-
  based robustness check. This is a real fix relative to the August finding.
- BUT: `config_apartment.json` / `config_house.json` both still pin `"hider_theta": "impose_zero"`
  (the circular assignment) — this is what generated the published `results/apartment`,
  `results/house` (confirmed via timestamp + σ̂₁≡0 in `results.txt`). The registry-corrected
  numbers behind `tab:robustness` live only in ad hoc, un-scripted runs
  (`results/_robust/*`, `results/_sigma1test_*`, no README, not reproducible via `run.py`).
- `src/validation.py:test_sigma1_zero`, wired into `main.py`'s `run_all_validation`, is tautological
  under the default `impose_zero` config (always 0/N rejections by construction). `main.py` is
  likely a stale/parallel entry point though (see below), so this may not be a live risk in
  practice — but it is shipped and would mislead if run.
- **Action item if resumed:** decide the baseline `hider_theta` deliberately, write a real
  `scripts/make_robustness_table.py`, and don't rely on `APPENDIX-GAPS.md`'s "IMPLEMENTED" tags
  without re-checking (see next point).

**ρ̂-boundary exposure — handled well, both in code and text.** No action needed; this is in good
shape (`04-structural-draft.tex:409,524-526`, matches `results/*/results.txt` exactly).

**`APPENDIX-GAPS.md`'s own "IMPLEMENTED" tags are stale relative to current `main.tex` (as of
ee0e311).** Items 1 (ρ̂ boundary/interior comparison table) and 2 (sample-selection/attrition
table) are marked implemented but no such tables exist anywhere in `main.tex` or its sections —
only the prose-level discussion exists. Item 3 (figure of registry coverage over time) is still
just a footnote (`sections/03-setting-draft.tex:196`), not a figure, exactly as originally
diagnosed. Don't trust these checkboxes without re-grepping the current `.tex`.

**New findings not in prior memory (2026-09-14):**
- No standard errors / bootstrap CIs anywhere for ρ̂_m, ĉ₀_m in the published paper. Both configs
  set `n_boot: 0`; no `bootstrap_draws.csv` in `results/apartment` or `results/house`. Table's
  "Std" columns are honestly-labeled cross-market dispersion, not a sampling SE — but a referee
  will still ask for one. `bootstrap_se()` in `src/estimation.py` is well-implemented (correctly
  re-draws `market_stats` per replication, not just data moments) but simply never invoked with
  `n_boot>0` for the numbers that ship.
- `main.tex`/sections never `\input{}` any table from `results/tables/*.tex` — all manuscript
  tables are hand-transcribed, contradicting `CLAUDE.md`'s own stated "single source of truth"
  policy (which figures *do* correctly follow via `\includegraphics{fig/...}`). Concrete cost of
  this: Table `tab:did_results` (`04-structural-draft.tex:455-484`) has a footnote (N=43/107) that
  contradicts its own column values (N=49/104) — drift that `\input` would have prevented.
- Two un-reconciled "non-disclosure premium" numbers in the same paper: 6.9%/3.4% (headline,
  cross-market mean of market-level DiD, Table 4 Panel A) vs 4.4%/3.7% (§2's pooled/aggregate
  hedonic-controlled DiD, `sections/03-setting-draft.tex:129`). Plausibly different estimands,
  never stated as such.
- Two divergent pipeline entry points: `main.py` (single property-type, `n_boot=500` default, no
  `hider_theta` key → falls to `impose_zero`) vs `run.py` (config-JSON-driven, what actually
  produced published results per timestamps). `CLAUDE.md` lists both without distinguishing which
  is canonical.
- `config_*.json`'s `"weighting_scheme": "optimal_gmm"` is inert — the two-step primary estimator
  (`estimate_msm(fix_rho=True)`) never touches the weighting matrix at all. Minor but worth a
  one-line config comment.

**Resolved since earlier sessions (good news, don't re-flag):**
- `cor:rho` and `prop:pi` now have economic-gloss paragraphs + testable implications
  (`04-structural-draft.tex:325-334,343-`) — matches [[latex_reference_fix_2026]] memory.
- Abstract log-points vs. percentage-points unit inconsistency (DIAGNOSIS.md) — resolved, "percent"
  used consistently now.
- The ĉ₀_m upper/lower-bound directional error flagged in [[identification_strategy]] (2026-04-22)
  — confirmed fixed, paper correctly calls it an upper bound throughout.
