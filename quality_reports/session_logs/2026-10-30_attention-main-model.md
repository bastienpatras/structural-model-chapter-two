# 2026-10-30: attention as main model (branch sections-4-5)

Goal: promote the limited-attention model (§4.6) to the main model; core = psi=1 benchmark. Plan: quality_reports/plans/2026-10-30_attention-as-main-model.md (APPROVED; auto mode; humanizer re-run after each writing step, advisory only).

## Phase 1 (hiding cost c0) done
- Micro-theorist audit: algebra treats c0 identically in both models; the break is interpretation (buyer-side detection channels) and two estimands (core c0 = b1*e*, attention c0 = Delta).
- 04-structural-draft.tex: c0 defined as r + qF, q set by enforcement, negotiation/fall-through moved to Gamma, c1 defined net of the premium already in b, "paid at listing" wording.
- 04-attention-draft.tex: assumption that c0, c1 do not depend on (rho, omega, C^def), Fix B excluded and signed; welfare paragraph names c0 = Delta-hat; "paper's measure" now c0 = Delta-hat with psi=1 value alongside.
- Check: attCzeroFit = attDthree (8.5 / 3.9), so the "hiding-rate" and "premium" readings coincide numerically.
- Humanizer pass on the new passages: no change worth applying.
- Compile clean (latexmk, no undefined refs).

## Open
- main.tex:72 still says "the model of Sections ... is the case psi=1" (Phase 6).
- Phases 2-6 pending.

## Phases 2-3 (done, each step compiled clean, 81 pages, 0 undefined refs)
- Merged 04-attention-draft.tex into 04-structural-draft.tex (git rm of the former). Order in section 4: Motivation (+ "Silence Priced Above a Verified Efficient Rating") / Setup / Buyer Attention to Silence / Equilibrium with Limited Attention / The Full-Attention Benchmark / Identification (+ att identification) / Estimates (+ att estimates). All labels kept; sec:equilibrium now sits on the benchmark subsection. main.tex input line removed.
- "extension" wording replaced in the model section; "model of Section equilibrium" -> "benchmark of Section equilibrium".
- A-attention proof of prop:att_equilibrium Step 2 now self-contained (no delegation to prop:equilibrium); resolved the [CHECK] ledger note about sigma_1>0 in CDH.
- A-robustness: remark that appendix statements hold with rho -> rho*omega_1 and c0 = Delta under attention.
- Left as is: lem:profit label placement (unreferenced, cosmetic); linear-pricing approximation is already stated in main text and A-attention (app:att_exact, conjecture).
- Stale to revisit: motivation sentence "we maintain rho-hat = 1 for those markets and treat c0 as upper bound" predates the anchored rho (T=10).
- Humanizer re-run (inline) on the new prose: nothing to change.

## Phase 4-6 + micro-theorist cross-check round 1 (all steps compiled: 81 pages, 0 undefined refs)
- Macros: added attRhoMeanApt/House to scripts/compute_attention.py; regenerated (diff vs previous macros = only the 2 new lines, values 49.5 / 45.8). Hard-coded rho, c0, sigma0 in prose (intro, section 4 prose, conclusion) replaced by macros; tables and pi-hat / 6.9 / 3.4 still hard-coded.
- Front matter: abstract (attention-first, psi macros, D91, keyword), intro P8-P9 and contribution wording, section 2 (second margin of assumption d), section 3 (fifth requirement), policy heading/opening, conclusion (three departures).
- Cross-check round 1 (micro-theorist): applied the verified items.
  - prop:pi was wrong (claimed pi pushes PP into unraveling; Delta(thetabar) is pi-free). Statement, proof and following text corrected.
  - Prop equilibrium(iii) sigma0* in [0,1].
  - c0 consistency: removed "prolonged negotiation" and "reputational concerns" from c0; labelled the estimator c0 = b*e* as the full-attention reading.
  - A-robustness remark limited to what holds under attention.
  - Resolved open ledger ISSUES 1,3,4,5,6,7 in A-attention.tex (weak/strict inequalities, C^def <= 0 for psi=1, psi>0 for pi derivative, C^def bound, rho_m reading); removed those [CHECK] blocks. Other [CHECK] blocks (ISSUE T1,T3,I7,A2, ...) left open.
  - Added converse (0,0) is an equilibrium to the Step 2 proof.
  - "model above"/"core model"/"as before" dangling wording reworded; forward refs to eq:belief_simplified, eq:Phi left as is.
- backtest.sh fails in hook-battery (17 FAIL cases on git fixtures); the same 17 fail on a clean worktree of HEAD, so pre-existing/environmental. Other gates pass.
- Round 2 cross-check dispatched.

## Cross-check round 2 (micro-theorist) applied; compile clean (81 pages, 0 undefined refs)
- Fixed pre-existing errors in core proofs (main.tex): CAS premium is the minimum not the maximum; Case-1 premium rises with rho; sec:beliefs ref -> lem:belief_monotone; "partial separation" mislabel for CAS; prop:pi interpretation (belief pinned in PP, hiding rate adjusts; needs c0>0).
- att_cs(ii) conditioned on sigma_1*=0; cor att_hq remark weak/strict; c0 headline unified (Delta-hat) in estimates and setting; "upper bound" argument limited to the psi=1 value.
- Front matter: abstract no longer says "cannot exceed", psi levels qualified by normalisation, subsidy claim marked "in the model"; intro: silent pool empties only when nearly all sellers informed and full attention, "order of magnitude" softened; section 3 fifth requirement softened.
- Open (not changed): [CHECK] blocks ISSUE T1, T3, I7, A2 and others in A-attention.tex; tab:equilibria "(0,1)" and eq:premium strict inequalities at band endpoints; main.tex:210 vs c0,m = Delta_m market by market; hiding-rate ordering sentence (S ~997, flagged by author); intro 01:209/216 subsidy-unchanged claim still states the model result without "in the model"; pi-hat 51.8/41.7 and 6.9/3.4 still hard-coded; stale "rho-hat = 1 maintained" sentence in motivation; tab:did_results hand-typed.

## Unified Setup + notation (micro-theorist audit applied; compiles, 81 pages, 0 undefined refs)
- Energy-cost symbol renamed C -> zeta (zeta_0, zeta_1, zeta^def, bar zeta^sil, zeta^*, zeta^ins; script Z for the cost subtracted) across main.tex and sections/*.tex, so it no longer clashes with hiding costs c_0, c_1.
- Subsection "Buyer Attention to Silence" removed; its content merged into Setup (environment/timing with attention, hiding-cost independence assumption, bonus form -> cost form -> attention assumption -> three-segment demand, eq:demand as the omega_0=omega_1=1 case, prices and effective belief under Beliefs). Labels ss:attention and ss:att_setup now on Setup.
- Audit fixes: rho identified once (as rho*omega_1); alpha_1 defined; c0 independence stated once; forward-reference phrases; timing-figure caption says full-attention case; leftover capital C and constant K renamed; Delta(e) vs observed Delta clarified.
- Open: timing figure itself has no attention draw (caption only); hat convention beta1-hat estimates b; several [CHECK] blocks in A-attention.tex.

## Buyer valuation audit (micro-theorist + git history); compiles, 0 undefined refs
- Algebra of bonus form, cost form, three-segment demand, b = rho*omega_1*beta_1 and Delta = rho*omega_1*(zeta_0 - zeta^*) confirmed correct at alpha_1 = beta_1.
- Fixed prose: alpha_k (never defined in any commit) -> alpha_1 defined and benchmark alpha_1 = beta_1 stated as maintained; lemma cost_form now "under alpha_1 = beta_1"; the committed sentence "identified rho is a lower bound ... premium understates what a skeptical buyer would generate" was wrong (stale since the anchored estimator) and is replaced: alpha_1 < beta_1 leaves rho*omega_1 unaffected and overstates psi-hat; v_1 is the valuation of an ATTENTIVE sensitive buyer; inattentive buyer subtracts zeta^def (not "as though energy were absent"); premium derivation no longer imposes v_0 = beta_0; claim "c_1 matters once alpha<beta" replaced by c_1 matters only when silence sells above a verified efficient rating.
- Added: zeta is a first-order approximation in log price gaps; silent and rated dwellings of the same quality share the same energy cost.
- Open: Gamma(p|d) notation drops theta; hat convention (beta1-hat estimates b); FINDING-sigma1.md section 4b repeats the c_1 error.

## Bonus form removed; full-attention benchmark moved to appendix (compiles, 0 undefined refs)
- Eq. 2 (bonus-form v_1) and every mention of the bonus form / alpha_1 removed; buyer valuation stated only in cost form (gross value, energy costs zeta, definition of buyer valuation and mean valuation; v_1 kept as a shorthand). Lemma cost_form and its proof deleted. Micro-theorist check applied (level of energy cost, not of V-bar, matters; v_1 argument order).
- "The Full-Attention Benchmark" subsection moved from section 4 to sections/A-benchmark.tex (appendix E, before the Proofs appendix); labels unchanged; "Section ref{sec:equilibrium}" -> "Appendix ref{sec:equilibrium}" in main.tex and sections.
- Open: preliminary FOC lemma in the proofs appendix uses single-segment demand.

## Restructure of 4.2 (The Model) and 4.3 (Equilibrium with Limited Attention), 2026-11-01
- Plans: quality_reports/plans/2026-11-01_restructure-4-2-4-3.md and 2026-11-01_restructure-equilibrium-section.md (both approved).
- 4.2: old Setup + Payoffs merged into one section "The Model" (Players/Information/Timing; Seller's Choice; Buyers and Attention; Silent Pool; Prices and Effective Belief). phi*Gamma payoff, logit demand, cost-form construction, effective-belief derivation (s(zeta) scale), hiding-cost micro-foundation (c_0 = c^fix + qF, assum:c_indep), energy costs, independence justification, belief-monotonicity proof moved to appendix homes (app:att_exact, app:att_costform, app:att_etilde, app:hiding_costs, app:energy_costs, app:independence, Proofs). New labelled Assumptions: no_falsification, linear_pricing, c_indep. PBE sentence added (author to confirm).
- 4.3: five parts (Who Hides First / Where Hiding Settles / What Silence Sells For / Three Channels / Who Pays for Inattention). Empirical paragraphs moved to 4.5 (ordering reading, lambda-hat) and to appendix (app:att_band_fit, app:att_nonstrategic); payoff table to app:att_payoffs; new proof of Cor att_band; regime table gained a 5th column; psi-bar defined once in Prop att_incentives(iii) (eq:att_psibar).
- Soundness fixes: band width/location sentence, at least two equilibria in CAS, zeta*<zeta_1 claim, d sigma_0*/d pi <= 0 (strict iff e*<thetabar) incl. appendix proof step, welfare mark-up excess, sigma_1 registry wording, proof of (iii) belief form.
- Each restructure: fresh micro-theorist check applied, narrativize pass, advisory humanizer (suggestions listed to the author, not applied). All compiles clean (83 pages, 0 undefined, 0 multiply defined).
- Open: independent fenced read of 4.2/4.3; humanizer suggestions for 4.2 and 4.3 pending author approval; one 6pt overfull box (not the new tables).

## 2026-11-01 — Section 4.5 Estimates, no benchmark comparison
- Decision (user): drop the systematic comparison with the full-attention benchmark in 4.5. Plan: quality_reports/plans/2026-11-01_estimates-4-5-no-benchmark.md.
- Done: macros attDlSd*, attRsqExt* added (compute_attention.py); fit figure rebuilt attention-only; F3 split (F3b psi-by-estimator moved to app:att_qualifications as fig:att_psi_estimators); F5 no longer generated; 4.5 rebuilt (question-led opener, Attention to Silence, What Silence Pays, Fit and the Scale of Attention with tab:did_results); main.tex:71, 4.3 and 4.4 pointers repointed. Compile clean, 81 pages.
- Micro-theorist findings applied: b-hat = beta-hat_1 formula, zero-residual reason, c0 calibration rationale (observed premium in own band: 0% apt, 11% houses), upper-bound scope, ceiling-violation reading, house ordering split, opener test result.
- Open: [CHECK] notary source (04-structural l.600); typed 5.9/2.8 vs macros 5.8/2.7 (also tab:robustness); Intro L154-156 and main.tex L370 still present 2.4% full-attention cost as the hiding cost; kWh band-midpoint caveat in 4.4; define "attention ceiling" in 4.4; name for psi_delta; advisory narrativize/humanizer edits (14) awaiting user decision, not applied.
- 4.5 humanizer/narrativize: 13 of 14 advisory edits applied at user's request (edit 6 already covered by the c0 rewrite; edit 14 left in notes). AUTHOR REWRITE paragraphs (L588, L598, L613) not touched. c0 wording reconciled in 4.3/4.4/4.5 and A-robustness (identity in Partial Pooling; estimator = predicted premium). Compile clean, 80 pages. 4.5 procedure complete; next: Section 4 as a whole.
- Section 4 as a whole (plan 2026-11-01_section-4-as-a-whole.md): added section opening + closing bridge; rewrote abstract, Intro estimates paragraph, conclusion (one test + three magnitudes; benchmark 2.4/3.5 only as counterfactual); unified names (psi_delta/attention wedge/apartment inversion/zero-default assumption); added effective belief and attention wedge rows to tab:attention; fixed Intro L199 comment marker, 03:98/118, c0 definition wording, fig:ATT note sample, 4.1 default claim. Not applied: 12 advisory prose edits; canonical hiding-rate pair (15.2/6.8 vs 5.9/2.8 vs macros 5.8/2.7, A-attention:264 8.0/2.9); M9 (second force?), M10 (95% silent-uninformed share vs 83% tab:groups); six referee-risk points; remaining minors (omega_1 'normalisation', hat convention b vs beta_1, tab:attention psi vs psi_delta). Compile clean, 81 pages.


---
**Context compaction (auto) at 22:31**
Check git log and quality_reports/plans/ for current state.
- Applied the 12 advisory prose edits (section-4 opening/closer, abstract, intro test sentence, conclusion). Backup: scratchpad/pre_adv12. Compile clean.
- Table 6 (tab:attention) reworked: four panels (A prices, B attention to silence, C test and ceiling, D fit with RMSE vs SD of observed Delta-hat and R^2); psi-by-OLS and slack rows removed from the table (still in text/appendix via macros); "observed minus predicted" dropped; notes shortened. scripts/compute_attention.py table_body only; macros file identical. Plan: quality_reports/plans/2026-11-02_table6-and-section5.md.
- Section 5 mechanical fixes from micro-theorist (F1-F4, F6, F7, F9-F12, F16-F17 and partial F13/F15): regime stated as imposed by calibration with in-band 0%/11%; psi := psi-hat_delta; lower-bound/selection direction sentences; mu for cost of public funds; units in prop:att_saving; question-led openers in 5.2/5.4; tab:instruments moved to 5.6; stock-effect paragraph and eq:renovation_flow deleted. Not done: appendix moves (tab:threshold_cs, lemma statement, fig:policy_bound, exact-pricing footnote) and AUTHOR REWRITE paragraphs (5.1 opening, 5.5, 5.6, 5.7 openers) - suggestions only. Compile clean, 81 pages. Fresh check + advisory prose pass launched.
- Fresh micro-theorist check on Table 6 + Section 5 applied (F1 Remark corner condition, F2 direction of bound, F3 registry belief e* row restored to Table 6, F4 zeta^def=0 in psi row, units, notes weighting, saving-bound units 100R/P_m, symbol e*, prop:subsidy_ge F_R wording, 5.5 title, A-robustness pointer). Not applied: F10 (opening L71, author-marked), F15, F16; 12 advisory prose edits + 4 author-paragraph suggestions pending user. Compile clean, 81 pages.
- Applied the 12 advisory Section 5 prose edits (user yes) and moved tab:threshold_cs and fig:policy_bound to the appendix (app:attention). Not moved: lem:renov_behaviour statement, Remark footnote, exact-pricing footnote (inside author-marked paragraph). Author-marked 5.1/5.5/5.6/5.7 paragraphs untouched. Compile clean, 80 pages.


---
**Context compaction (auto) at 16:59**
Check git log and quality_reports/plans/ for current state.
- Applied editor suggestions to the author-marked Section 5 paragraphs at user's yes: 5.1 opening (psi-hat_delta, calibration sentences moved to a separate paragraph, 'averages'), 5.5 (dropped 'intrinsically more amenable' closer; footnote contrast), 5.6 (table carries the instrument list), 5.7 (shortened chain). Compile clean, 80 pages.


---
**Context compaction (auto) at 18:20**
Check git log and quality_reports/plans/ for current state.

## 2026-11-02 front matter vs Sections 4-5
- Plan: quality_reports/plans/2026-11-02_front-matter-vs-sections-4-5.md. Fenced micro-theorist read (neutral copy outside checkout): 1 CRITICAL, 13 MAJOR, 3 MINOR.
- Applied (unmarked or mechanical): Intro 6.9/3.4 now log points with sample; pre-trend +0.2/+0.8 and +4.4/+3.7 log points (Intro, Section 3); house uninformed 8.6%; Intro regime sentence (calibration imposes partial pooling); "empirically dominant" removed in Intro L188; Intro "second sets the level of the premium"; Conclusion K=1 shares 51.2/40.3, premium "on average across markets", L348 mechanism sentence, L351 bill/lower-bound/targeting axis.
- Bug fixed: compute_attention.py ê* row had a doubled backslash (table broke the compile); macros identical after regeneration.
- Not applied (marked [AUTHOR REWRITE], suggestions): Concl L344 rho sign, L347 "bulk of markets" and fit claim, L350 enforcement/dominant regime/salience, Intro L190-197 policy paragraph.
- Open: narrativize + humanizer pass on Intro/Conclusion; hiding-rate pair; 4.4 vs 6.9 reconciliation sentence.
- 2026-11-03: user said "apply everything". Applied the marked-line suggestions: abstract (estimator range for psi, one-hiding-cost qualifier, "poorly targeted", "certified audit on record"); Intro ¶12.5 rewritten (lower bound, bill as scale, local price levels, enforcement/audit qualifier, salience saving in euros); Conclusion L344 rho-sign, L347 imposed regime / calibrate / not rejected / fit limited, c0 numbers sentence cut, L348 registry caveat, L350 enforcement + salience wording. Compile clean, 81 pp. Pre-edit backups in scratchpad pre_fm/ (main.tex, intro, sec 3, before the 11-02 batch). Not done: narrativize + humanizer; hiding-rate pair; 4.4 vs 6.9 wording check.
- 2026-11-03: applied all 11 advisory items (I1-I5, C1-C6) from quality_reports/humanizer/2026-11-03_intro-conclusion-advisory.md; C6 as: three-departures paragraph shortened, "future work" sentence added to Conclusion policy paragraph. Backups in scratchpad pre_adv2/. Compile clean.
- 2026-11-03: abstract reworked (plan 2026-11-03_abstract-rework.md): ~330 -> ~190 words; user asked empirical results first. Order: premium + design + silence pricing, then policy result (lower bound, regime imposed, cost shares at EUR250/m2). Fenced micro-theorist check applied (reform wording "legally opposable", post-reform certificate on record, regime caveat, lower-bound direction, cost shares conditional on illustrative benchmark, targeting phrased as flat grant overpays/underpays). Backup: scratchpad pre_abs/. Open: S1 3 line 131 credits opposability to loi Climat (contradicts Intro footnote); 83/89% vs 95/98% silent-uninformed shares (Sec 3 vs Sec 4 L27); narrativize/humanizer pass pending.
- 2026-11-03 abstract v3 (plan 2026-11-03_abstract-v3-puzzle-first.md): puzzle first in plain words (no "unraveling"), bridge to renovation, two components, design, policy result led by "silence does not raise the bar for renovation". Fenced check applied: "worst news ... at or below", "informed sellers", deduct only a small fraction (not "price silence below"), "records whether seller holds post-reform certificate", lower bound exact in imposed regime, cost shares in markets needing support, "no single per-m2 grant". Body fixes: Sec 3 L131 law credit dropped, Conclusion "none suffices alone" replaced, "Efficient targeting" -> "Matching subsidies to need", Conclusion rho sentence now neutral (shrinks reward and renovation threshold). OPEN: Sec 2 L86 ("buyers who do not price weaken the penalty") and A-benchmark/Prop conflict with d sigma0*/d(rho w1)>0: direction of the rho effect on hiding needs the author's decision; Sec 3 83/89 vs Sec 4 95/98.
- 2026-11-04: humanizer suggestions for abstract v3 applied at user's 'implement' (question -> 'we ask', 'Two components explain', 'threshold' for 'bar', 'show' for 'reveal', 'exact only in'). Backup scratchpad pre_abs3/main_before_humanizer.tex.
- 2026-11-04: abstract final pass: humanizer suggestions applied (cut 'Two components solve', split 'Together they...', 'rating premium', 'misfires'); cost-share ending = version 1 (53/56% of cost, 98/90% of markets); transitions per user. Backups scratchpad pre_abs3/. Open: hedge removal (lower bound) in abstract, Keywords 'Unraveling', Sec 2 L86 rho intuition, 83/89 vs 95/98, 4.4 vs 6.9 wording.
- 2026-11-04: abstract humanizer round 3 applied (colon staging, 'cost net of the rating premium', single name 'rating premium', cost-share sentence split, 'Needs vary widely ... so a uniform subsidy misfires'). Title now 'Does Silence Pay? Mandatory Disclosure and Limited Attention in Housing Markets'. Percent (7%/3.5%) in abstract, log points elsewhere. Backup scratchpad pre_abs3/main_before_hum3.tex.
- 2026-11-04: appendix + proof review (plan 2026-11-04_appendix-proof-review.md): 7 fenced reviewers, 80 findings (1 blocker, 18 major, 42 minor, 19 nit); reports in quality_reports/appendix-review/ (P1-P7, summary, findings.json validated); humanizer advisory in quality_reports/humanizer/2026-11-04_appendix-advisory.md. CORRECTION: my 2026-11-03 Conclusion rewrite ("buyer heterogeneity makes exploiting that ambiguity financially worthwhile") carries the wrong rho sign; Section 2 L86 has it too. No manuscript edits made by the review. Awaiting author decision on fixes.
- 2026-11-04 fixes round 1 (after appendix review): rho-sign prose (Sec 2 L72-87, Conclusion L343), data appendix (listing table deleted, K/theta/rho definitions, footnote, braces), A-robustness relabelled FA benchmark cost, 14 statement-scope/proof edits, A-attention table att_seller_types e^def>1. Fenced re-review of the 20 hunks: 14 OK, 6 PROBLEM; the 4 that were my wording errors fixed (L343 'suffice', theta bullet, K for silent listings, rho note via delta(rho omega1), robustness scope, table att_seller_types, 04:431 strict). OPEN for author: Sec 2 L50-57, 72-74, 81-99 and Introduction L69-72 still say rho/(d) drives separation (conflicts with model: pi<1 alone defeats unraveling; low rho moves toward CDH); fig equilibirum_outcomes.png not inspected; P3-P6 substantive items not applied. Backups scratchpad pre_fix/. Compile clean 80 pp.
- 2026-11-04 fixes round 2: Section 2 + Introduction p5 rewritten (pi<1 defeats unraveling, rho sets the stakes; (d) wording; figure paragraph; Intro L166 'rewarded reflects the uninformed'); benchmark: Prop premium restated with hiding costs, proofs of premium/hq_disclose replaced by linear-pricing proofs (Preliminary, Lemma A.1, v_1 deleted, -101 lines), cor:rho(ii) 'shifts up and widens', cross-market prediction removed, welfare paragraph rewritten (zero-mean transfer, no allocative term), Conclusion 'residual claimant' removed, Section 4 'rent' -> premium. Fenced re-review (hunks 8 OK, 4 sibling problems) -> all fixed except: 04:304 Prop att_incentives(iv) 'with c0=c1=0 they reduce to prop:premium' (now unnecessary, harmless). Compile clean 79 pp. Backups scratchpad pre_s2/ and pre_fix/. STILL OPEN: P3 estimation claims (bound violations, selection direction, linear-pricing scope for psi inversion), P4 saving-bound object and pi->1 proof step, P6 F2/F3 identification wording, P5 remaining nits.
- 2026-11-04 fixes round 3: P3 (bound-violation reading aligned to body; linear-pricing scope incl. psi inversion with exact-logit example, either direction; selection-bias direction with condition; Step 6 identities), P4 (att_saving on average of seller-specific S_i*, uniform-subsidy caveat 'bound does not apply', siblings qualified at m.tex L335/L349/Intro; pi->1 belief now stated as assumption with general sign identities), P6 (cor ratio test hypotheses, prop anchored omega1=1 + psi=1 + PP, wording rho->rho omega1). Fenced re-review: 7 hunks, 1 major (my caveat) fixed + siblings, rest minor/nit fixed. Compile clean 80 pp. Backups scratchpad pre_r3/. NOT applied: P3 #5 (Gamma channel in c0), P4 #4-6,#8,#10-11 minors, P5 minors (04:312 citation, A-benchmark:145), P6 F8,F9,F11,F12,F13, P7 #7-9, P2 #5 (hiding-rate pair), 04:304 reduction clause, Keywords. No commit.


---
**Context compaction (auto) at 14:08**
Check git log and quality_reports/plans/ for current state.
