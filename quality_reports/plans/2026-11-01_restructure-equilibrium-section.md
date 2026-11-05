# Plan: restructure Section 4.3 "Equilibrium with Limited Attention"

Status: DRAFT, awaiting approval. Branch `sections-4-5`. Nothing edited yet.
Inputs: Explore inventory (labels, citations, pointers, symbols, empirical material), micro-theorist assessment (ordering, transitions, appendix moves, soundness, proposal), and a drafting pass applying the narrativize rules and the humanizer checklist. Same procedure as the 4.2 restructure (`2026-11-01_restructure-4-2-4-3.md`).

## Context

`\subsection{Equilibrium with Limited Attention}` (label `ss:att_equilibrium`, `sections/04-structural-draft.tex`, ~lines 330-514, ~2,800 words) was moved and edited in pieces. Section 4.2 now ends by asking where the hiding rates settle. The section answers that, but the results are stacked without interpretation, the key reading arrives after a table, about 20 percent of the text is estimation that cites later sections, and several statements need fixing. Goal: the reader is led through who hides first, where hiding settles, and what silence then sells for; the core keeps the intuition and the main results; empirical readings and long discussions move to Section 4.5 or to the appendix.

## Assessment (what is wrong)

**Ordering.**
- Current: gains -> incentives -> high-quality disclosure -> regimes -> payoffs and ordering -> empirical reading -> band -> comparative statics -> high-quality empirics -> welfare. Natural: gains -> regimes -> band -> payoffs -> ordering -> comparative statics -> welfare.
- "Band" is used (l.424) before Cor att_band defines it (l.482). psi-bar is used in cost units in Prop att_incentives(iii) (l.351), defined inside Prop att_seller_types (l.433), reused by Cor att_ordering. e^def has no displayed definition in 4.3. The core silently needs e(sigma_0), Phi and Cor hq_disclose from Appendix E.
- Forward references to 4.4/4.5: `prop:att_identification`, `ss:att_estimates`, `ss:att_identification` (l.478, 489, 508, 513).

**Seams.**
- The opening (l.328 -> 333) restates the incentive conditions a third time (4.2 closes with them, then eq:gains, then Prop att_incentives(i)-(ii)).
- Prop att_equilibrium has no intuition before it (l.369 is pure definition). The premium = c_0 reading is at l.415, after the table. l.478 opens "The proposition..." right after a corollary. l.491 is a bare connector. l.508 opens weakly.
- Results stack without interpretation: Cor att_hq -> Prop att_equilibrium -> table, and Prop att_seller_types -> table -> Cor att_ordering.

**Empirical material inside theory (~550 words, ~20 percent, ~30 macros).** l.478 (effective-belief ratios, psi-hat vs thresholds, market counts, orderings), l.489 (band fit and shares in band), l.506 second half (registry sigma_1 vs sigma_0, apartment excess, house loss), last sentence of l.513 (lambda-hat). Appendix A-attention:400 points back at the l.489 band paragraph ("Section 4.3"), so the appendix depends on empirical text in the core.

**Soundness items to fix on the way.**
1. The band sentence (l.480) is inconsistent. Bounds are psi times the benchmark bound plus (1-psi)*b*e^def; width is psi*b*(thetabar - e(1)); it narrows with psi and is not a shift.
2. Prop att_equilibrium(ii) omits the unstable interior sigma_1 equilibrium; state "at least two equilibria" when both corner conditions hold.
3. Props att_incentives(iii) and att_cs are conditioned on an endogenous object (zeta^def < zeta-bar^sil); give the primitive sufficient condition zeta^def below the prior-mean cost (e* <= thetabar).
4. "At or above an A rating" (l.358) overstates: the model predicts only above zeta_1 (needs psi*zeta-bar^sil <= zeta_A at zeta^def = 0).
5. "First ordering in every apartment market" (l.478) is not verified market by market; psi-bar depends on eta_m and e_m(1). A negative Delta* cannot arise in any regime when zeta^def <= zeta_0, not only in Partial Pooling.
6. d sigma_0*/d pi < 0 is strict only when e* < thetabar. "Lowers the gain from hiding" is true only at a fixed pool: in Partial Pooling the premium stays c_0 and only sigma_0* moves.
7. The registry shows sigma_1 close to sigma_0; this is evidence against the sigma_1 = 0 prediction and not a test of it (ties to `FINDING-sigma1.md`). State it plainly; non-strategic silence is a rescue.
8. Welfare (l.513): "paid by inattentive buyers" assumes who transacts, which price = mean valuation does not give. Rated listings also carry a mark-up rho(1-omega_1)(zeta_theta - zeta^def); the part specific to silence comes from omega_1 - omega_0.
9. "One substitution extends the analysis" (l.343) holds only for sigma_1 = 0. Cor att_ordering's benchmark sentence needs pi < 1 (else e(1) = 0).

**Notation.** Delta means four things (premium, benchmark Delta(e), Delta_psi(e), Delta*) plus g_0 = Delta; keep Delta_psi and Delta*, drop Delta(e) from the core. e(1) collides with e(1,1) = thetabar used in the proofs (rename to \underline e). e* is both the equilibrium solution of eq:att_pp and the registry measure (eq:estar). Propositions cite only Assumption attention but also need linear_pricing (and Prop att_seller_types needs b > 0). g_0, g_1, Phi_psi are defined and then used only in the appendix.

## Proposed structure: `\subsubsection`s inside 4.3

| # | Part (descriptive heading) | Question it answers | Contents (labels kept) |
|---|---|---|---|
| 0 | Opening (2-3 sentences) | What does this section settle? | Takes over from 4.2's question; names the three questions: who hides first, where hiding settles, what silence then sells for. Cuts the third restatement of the incentive conditions. |
| 1 | Who hides first | Which informed seller gains more from silence? | `eq:gains`, `eq:Delta_psi` (second equality cut; Delta(e) leaves the core), Prop att_incentives with psi-bar defined here once, Cor att_hq. Parts (i)-(ii) demoted to the text already in 4.2; (iv) becomes a remark. |
| 2 | Where hiding settles | Where does the low type's hiding rate settle? | e(sigma_0) displayed locally; `eq:Phi_psi`; intuition sentence; Prop att_equilibrium (with fix 2, 3); interpretation "premium = c_0" directly after it; Cor att_band with its intuition and the corrected band sentence; one merged regime table (merges `tab:att_equilibria` with Panel A of `tab:att_seller_types`, now referenced in text). |
| 3 | What silence sells for | Given the regime, who gets what, and where does silence sit among ratings? | Prop att_seller_types (psi-bar part removed), Cor att_ordering as the answer to the Section 4.1 puzzle (fixes 4, 5, 9), one-sentence pointer to Section 4.5 for the estimated orderings. |
| 4 | Three channels | Which margins move the hiding rate? | Prop att_cs plus a trimmed discussion (revenue, belief, attention channels; fix 6); pointer to Section ss:att_policy; one sentence on the registry hiding rates (fix 7). |
| 5 | Who pays for inattention | Who bears the cost when buyers do not read silence? | `eq:att_markup` and welfare accounting without estimated numbers (fix 8). |
| -> | Bridge to 4.4 | What can the data recover? | One short bridge into Section 4.4 Identification. |

## Transition logic (drafted wording; the author owns the final wording of load-bearing passages, the `[AUTHOR REWRITE]` paragraphs at l.415 and l.478 in particular)

Each part opens with the question the previous part left. Drafts:
- Opening: "Section 4.2 left open where the hiding rates settle, since each informed seller's choice moves the pool belief that sets the other's gain."
- Part 2: "Because the low type drives hiding, the next question is where her hiding rate settles."
- Before Prop att_equilibrium: "When psi > 0, each additional hiding seller dilutes the silent pool with low-quality listings, which lowers the effective belief and with it the net gain from hiding. The equilibrium rate is therefore where that gain reaches zero, or a corner where it does not."
- After it: "In Partial Pooling the marginal hider is indifferent, so the non-disclosure premium equals her hiding cost, Delta* = c_0, whatever buyers attend to."
- Part 3: "At the equilibrium hiding rate, the question is what a silent listing sells for relative to a displayed rating and what each type of seller earns."
- Part 4: "Which margins move the hiding rate when the primitives change?"
- Part 5: "A last question is who bears the cost when buyers fail to read silence."
Caveats on the drafts: the drafted one-sentence replacement for the band-fit paragraph ("finds the single-cost specification generates interior hiding only within a narrow window") is not in the existing text and must be replaced by the actual claims of l.489 (shares of markets inside their own band); the bridge claim that attention parameters "enter only jointly with the hiding cost" must be checked against Prop att_identification(iv); the intuition sentence needs Phi_psi decreasing in sigma_0 for psi > 0 (true by Lemma etilde_monotone). Style rules for the full pass: no signposts that announce what follows, at most one em-dash per paragraph, few colon-elaborations, no "not X but Y".

## What moves, and where it lands

| Item | Core keeps | Lands in |
|---|---|---|
| l.478 effective-belief ratios, psi-hat vs thresholds, market counts, orderings (~330 words, ~22 macros) | One sentence: in apartments silence sells above an efficient rating, in houses between the two (Section 4.5) | Section 4.5 `ss:att_estimates` (after the estimates it cites) |
| l.489 band fit, shares in band | One sentence with a pointer | Section 4.5, or new `A-attention.tex` subsection `app:att_band_fit`; update A-attention:400 which cites it as "Section 4.3" |
| l.506 second half: registry sigma_1 vs sigma_0, apartment excess, house loss | One sentence: evidence against sigma_1 = 0, non-strategic silence | New `A-attention.tex` subsection `app:att_nonstrategic` |
| lambda-hat number (l.513) | None | Section 4.5 |
| `tab:att_seller_types` Panel B (net payoffs) and its dense notes (~170 words) | Merged regime table keeps condition, sigma_0*, Delta*, silence-above-efficient condition | Panel B to a new `A-attention.tex` subsection `app:att_payoffs` (cited only at l.424, so safe) |
| `eq:Phi_psi` | Displayed, with the intuition sentence (used only in A-attention:131) | stays |
| Inline proof of Cor att_band (l.487) | One-line argument | New short proof subsection in `A-attention.tex` (no proof subsection exists today) |
| Prop att_incentives (iv) | A remark | stays as a remark; keeps the pointer from `A-benchmark.tex:11` working |

## Cross-references to maintain

- Labels that must survive (cited from the introduction, 4.1, policy section, appendices): `ss:att_equilibrium`, `eq:gains`, `eq:Delta_psi`, `prop:att_incentives`, `cor:att_hq`, `prop:att_equilibrium`, `eq:att_pp`, `prop:att_seller_types`, `eq:att_premium_trunc`, `eq:att_psibar`, `tab:att_seller_types`, `cor:att_ordering`, `cor:att_band`, `prop:att_cs`, `eq:att_markup`, `eq:Phi_psi`, `tab:att_equilibria` (if merged, keep one label and repoint).
- Hard-coded part numbers that break silently if items are renumbered: Prop att_incentives(iii) at l.170 and (ii) in `A-benchmark.tex:28`, (iv) at l.358. Check each and keep the numbering of parts (i)-(iv).
- psi-bar's identity is cited by Cor att_ordering's proof (`A-attention.tex:225`, "the identity in the proof of Prop att_seller_types"); if psi-bar is defined in Prop att_incentives(iii), move or restate the identity in that proof.
- Appendix E pointer (`A-benchmark.tex:11`) to att_incentives, att_equilibrium, att_ordering, att_cs stays valid.
- New labels: `app:att_band_fit`, `app:att_nonstrategic`, `app:att_payoffs`, subsection labels for the five parts.
- Add `\ref{tab:att_equilibria}` (or the merged table) to the prose.

## Execution (after approval; compile after every step)

1. Back up files to the scratchpad. Create the new appendix subsections (band fit, non-strategic silence, payoffs panel, Cor att_band proof), compile.
2. Move the empirical paragraphs to 4.5 and repoint A-attention:400. Compile.
3. Rebuild 4.3 in the new order with headings, intuition and interpretation sentences, merged regime table, soundness fixes 1-9 and the notation fixes (drop Delta(e), rename e(1), cite linear_pricing). Compile.
4. Fresh micro-theorist check of 4.3 and the appendix homes (same checklist as for 4.2); apply findings.
5. `/narrativize` on 4.3, then the humanizer in advisory mode; apply the suggestions the author approves.
6. Grep every moved or renamed label and hard-coded part number; `latexmk` twice; zero undefined and zero multiply-defined labels.
7. Update the session log; do not commit until asked.

## Verification

- `cd paper-real-estate && latexmk -pdf -interaction=nonstopmode main.tex`: no undefined references, no multiply defined labels, page count noted.
- Every label in the keep-alive list resolves; every moved result keeps its proof reachable.
- All numbers and macros unchanged; only exposition, placement and the listed corrections change.
- A reader test: each symbol is defined before use in 4.3 (re-run the first-use/definition table).
- Independent fenced read of 4.3 (neutral copy) for flow, per `review-fencing.md`.

## Decisions for the author

- Confirm five `\subsubsection`s inside 4.3 (recommended) versus a flatter section with bold-free prose transitions only.
- Confirm moving the empirical paragraphs to Section 4.5 versus new appendix subsections (plan: ratios and counts to 4.5, band fit and non-strategic silence to the appendix).
- Confirm merging the two regime tables (recommended) and sending the payoff panel to `app:att_payoffs`.
- Confirm that the drafted transition sentences are a starting point and that you rewrite the `[AUTHOR REWRITE]` paragraphs.
