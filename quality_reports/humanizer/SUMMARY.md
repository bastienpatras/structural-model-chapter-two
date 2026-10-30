# Humanizer pass: summary (2026-10-30)

Plan: `quality_reports/plans/harmonic-munching-lecun.md`. Branch `humanizer-pass`. Plugin: blader/humanizer v3.1.0,
invoked through the `humanizer:humanizer` skill by the main session and by seven section agents (Phase 2).

## Outcome

| | Count |
|---|---|
| Blocks in the inventory | 376 |
| Eligible prose units | 218 (18,757 words); 19 more blocks protected by `% [AUTHOR REWRITE]` |
| Units with a proposal | 51 (43 `REVIEW-FLAGS`, 8 `CLEAN`) |
| Units with no real tell, unchanged | 167 |
| Hard-gate failures (G1, G2, G3, G7) | 0 |
| Accepted by Bastien | 51 of 51 (all applied) |
| Rejected / edited at approval | 0 / 0 |
| Revised after the cross-check | 3 (S7b rewritten; I14 and AT-6 reverted to the baseline phrase) |
| Words in the 51 changed units | 6,804 before, 6,583 after (-3.2%), before the three cross-check revisions |

Applied per section: §1 10, §2 7, §3 8, §4 9, §4.6 8, §5 policy 5, conclusion 1, A-robustness 1, main appendix 2.
Abstract (7 units) and A-attention (28 units) came back with nothing eligible to change or no tell.

## Verification (success criteria in the plan)

- mask/unmask is the identity on the whole baseline (`selftest`: 0 round-trip failures).
- Every applied change has a ledger row with an explicit decision.
- Non-prose regions are byte-identical to the baseline: 62 changed hunks, 0 outside an accepted unit; citation, ref,
  label, macro, marker, `\emph` and number counts identical in all 8 files.
- Final compile: 0 errors, no undefined references or citations, 80 pages (baseline 80).
- Micro-theorist cross-check (`CROSSCHECK.md`): 78 edits read independently, 62 identical in meaning; the 16 others were
  verified against the source. 3 were corrected, 2 were left as the author's call (I13, S9a), the rest were kept.
- Snapshots: `baseline_2026-10-30/` (verified intact, all hashes OK) and `final_2026-10-30/` (10 files, manifest OK).

## What the plugin did, in order of frequency (from the agents' reports; the ledger does not record pattern numbers)

1. **§1 "not X but Y" contrasts** reduced to a direct statement (most frequent single change).
2. **§2 closers and fragments** deleted or folded into the sentence before (for example "The outcome is bad for both sides.").
3. **§4 staged run-ups** ("Two features … matter for what follows", "Three features stand out") removed.
4. **§8 dashes** replaced by colons or parentheses (a handful, in §4 only).
5. **§12/§13 words** such as "fundamentally", "itself", "robust" (the last one is a claim, see below).

## What went wrong or needed a human

- On technical text the plugin mostly finds nothing: 167 of 218 units (77%) had no real tell.
- Removing a staged opener can leave a dangling ordinal (§3 L219 "First," with no announcement).
- A replaced word can change a claim: "robust" to "consistent" (§1) and "the amendments that come to mind first" to
  "the natural amendments" (§4.6) were both reverted; one rewrite broke grammar and a number claim (§3 L98).
- The cross-check agents could not write report files; findings came back as text.
- My own ledger update corrupted one row by rewriting the file while reading it; repaired from the committed ledger.

## Provenance

A clean humanizer pass is a readability claim, not a provenance claim (`.claude/rules/writing-with-ai.md`). It does not
change the AI-use disclosure; see `/submission-disclosures`.

## Not done / still open

- I13 (§1 L184-186) and S9a (§3 L219) kept as accepted; the author may still want the original wording back.
- `./scripts/backtest.sh` fails exactly as on a clean clone of the previous HEAD: 1 broken link, the expired `model-versions.md` note, 12 tracked build artifacts, 17 of 234 hook-battery cases. Nothing new from this pass.
- Push to GitHub still returns 403 from this machine (inactive owner account).
