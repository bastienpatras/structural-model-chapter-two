# Phase 4 cross-check: humanizer pass, 2026-10-30

Baseline = `baseline_2026-10-30/`. Final = `paper-real-estate/` at commit e99bcc8. Findings below are candidates that were
checked against the source text before being recorded (adjudicate-review discipline). Nothing has been reverted.

## Task 1: non-prose regions are untouched (programmatic)

Line diff of baseline against final for all 8 source files: 63 changed hunks, 0 outside the baseline line range of an
accepted unit. `git diff a97086c HEAD -- paper-real-estate` touches exactly 7 files. Counts of citations, refs, labels,
`\att…` macros, `\emph`, markers and numeric tokens are identical in every file. Compile: 0 errors, no undefined
references or citations, 80 pages.

## Tasks 2 and 3: meaning classification (two fenced readers)

Readers saw only `version_A` (baseline) and `version_B` (final): no ledger, decisions or plugin rationale. Reports were
returned as text because subagents cannot write report files.

| Reader | Files | Edits | IDENTICAL | WEAKER | STRONGER | DIFFERENT |
|---|---|---|---|---|---|---|
| 1 | main.tex, §1, §2, §3 | 51 | 37 | 12 | 0 | 2 |
| 2 | §4, §4.6, A-robustness | 27 | 25 | 1 | 1 | 0 |
| Total | | 78 | 62 | 13 | 1 | 2 |

Every ledger unit was recorded as accepted by Bastien, so none of the 16 non-identical edits was a surprise to the
approval step, but the classifications differ from "cosmetic" and are sent back for a decision.

## Reconciliation (my verification against the source)

### Act on (confirmed, recommend a change)

| id | where | what changed | verification | proposed action |
|---|---|---|---|---|
| S7b | `03-setting` L98 | "Third, and quantitatively dominant, 32.2% … display a score" became "The quantitatively dominant group is the 32.2% … display a score" | CONFIRMED. The sentence is ungrammatical (no "that"), and it now reads as a claim about the largest of the four groups. Table `tab:groups` has truthful disclosers at 47.7% of apartment listings, above 32.2%. In the baseline "dominant" meant the largest of the three shares listed in that paragraph (3.5/16.7/32.2 and 1.1/8.6/51.2). | Rewrite: "The largest of these shares is that 32.2% of apartment listings and 51.2% of house listings display a score with no matching registry record." |
| I14 | `01-intro` L232 | "documents robust premia" became "documents consistent premia" | CONFIRMED. "Robust" asserts the premia survive alternative specifications; "consistent" asserts only recurrence across studies. | Revert to "robust". |
| AT-6 | `04-attention` L38 | "the amendments that come to mind first" became "the natural amendments" | CONFIRMED. The original scoped the claim to a first-pass set. "Natural" claims the canonical set, while the same paragraph concedes that a change in unobserved composition is not ruled out. | Revert the phrase. |
| I13 | `01-intro` L184-186 | "is not a failure of the theory so much as a demonstration of how sensitive its central prediction is to an assumption that is rarely examined" became "reflects how sensitive the theory's central prediction is to an assumption that is rarely examined" | CONFIRMED. The defence of the theory is dropped and "demonstration" becomes the causal "reflects". The finding itself is unchanged. | Author's call; the original is the stronger framing for a skeptical referee. |
| S9a | `03-setting` L219 | "Two features of this decomposition are central to the analysis. First, …" became "First, …" | CONFIRMED (mild). The paragraph after the figure now opens with an ordinal and no announcement, though "Second" follows. | Optional: restore a one-clause opener. |

### Reviewed, no action needed

| id | verdict |
|---|---|
| S4-10 (`04-structural` L192) "the source of everything that follows" became "drives the results below" | WEAKER, but an improvement. The proof just above says the strict decrease in `e` in `σ₀` is what makes the equilibrium unique, so the original overclaimed. Keep. |
| M1 (`main` L255) "not a freestanding measure of how many buyers are sensitive" became "does not measure how many buyers are sensitive" | Reader called it DIFFERENT and a conflict with Prop. `scale_nonid`. OVERSTATED: the same sentence cites Appendix `rho_identification` for non-identification apart in price data, which supports B's wording. At most marginally weaker. Keep. |
| S5 (`03-setting` L45-46) dropped "rather than inventing one" | OVERSTATED as a cross-reference break. The baseline's own lead ("Two things the reform did not change") carried the same tension with "sharpened". Not introduced by this pass. Keep. |
| M4, M7a, I1, U1, U3, U10, S2, S8, S11 | Marginal WEAKER: a dropped evaluative word, intensifier, disclaimer or exclusive cleft. No claim, number or condition is lost. U10: B still says the involuntary presence of non-disclosers makes silence ambiguous, consistent with the paragraph naming insensitive buyers as the other force. M7a drops the "what sets this approach apart" distinctiveness claim; the introduction still states the contribution. Keep unless the author wants M7a back. |

### Counts and ordinals checked across all files (no break)

"three reasons" (§1, 3 delivered), "four assumptions" (§2), "Three additions" (`main` L360), "four requirements" (§3 L248),
"Two features make it unusual … the second property" (§3 L31-35), "several things" unsettled (§4, 4 items). Both
readers found no reference elsewhere in the paper to the deleted signposts.

## Decisions taken (Bastien: "implement what you suggest", 2026-10-30)

1. S7b: applied. `03-setting` L98 now reads "The largest of these shares is that 32.2% of apartment listings and 51.2% of house listings display a score with no matching registry record."
2. I14: reverted to "robust premia". AT-6: reverted to "the amendments that come to mind first".
3. I13 and S9a: kept as accepted (left to the author, not changed).
4. Everything else: kept as accepted.

After these edits: compile 0 errors, no undefined references, 80 pages; citation, ref, label, macro, marker and number
counts identical to the baseline; every changed hunk still lies inside an accepted unit. The three units' ledger rows read
`accept, revised after cross-check`.
