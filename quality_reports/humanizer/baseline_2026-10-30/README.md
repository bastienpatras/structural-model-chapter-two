# Baseline before the humanizer pass (2026-10-30)

**What this is.** A frozen copy of the paper sources as they stood on 2026-10-30, before the `humanizer` plugin
(blader/humanizer v3.1.0) was run on any section: `paper-real-estate/main.tex`, `paper-real-estate/sections/*.tex`,
and the two macro files the text reads its numbers from (`results/tables/attention_macros.tex`,
`attention_mc_macros.tex`).

**Why it exists.** The working tree had about 120 uncommitted changes on branch `review`, so `git diff HEAD` cannot
say what the humanizer changed. Every comparison in `quality_reports/humanizer/` is made against this folder.

**Contents.**
- `MANIFEST.sha256`: SHA-256 of every file here. Check with `cd baseline_2026-10-30 && shasum -a 256 -c MANIFEST.sha256`.
- `baseline_stats.json`: words per file, `\att…` macro use, and the sets of `\label`, `\cite*`, `\ref` keys per file; the compiled paper had 80 pages, 0 errors, 0 undefined references.
- `baseline_text/main.txt`: `pdftotext -layout` of that compile (the 14 MB PDF itself is not stored).

**Superseded by.** Nothing yet. If the humanizer pass is applied, the result is archived as `final_<date>/` next to this
folder and this baseline stays unchanged. It is never edited.
