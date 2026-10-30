# Approval sheet: main-policy

Riskiest first. Decide each unit: accept / reject / edit. Nothing is applied before a decision.

## main:L268-269 (lines 268-269): REVIEW-FLAGS
- words 219 -> 221; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: quantifier:only 2->3; number_word:one 2->1; G5 flags: sentences 9->8; new words: gives, show
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 We aggregate over the informed low-quality listings, the only ones that can renovate: a share $\pi(1-\bar\theta)$ of listings in each market, counted over the \attSampleYears{} years of listings in the estimation markets (July 2021 to December 2024) and expressed per year.\footnote{A dwelling listed more than once in the sample is counted each time, so the figure is an upper bound on the number of dwellings. Counting every listing, as an earlier version of this section did, would multiply the bill several-fold by treating verified efficient dwellings as renovators.} The largest market accounts for \attTopMarketShareApt{} percent of the apartment base, so the apartment total reflects that market's threshold more than the typical market's. At the light benchmark the bill is \euro{}\attScBaseCostTwoFiftyApt{} billion per year for apartments and \euro{}\attScBaseCostTwoFiftyHouse{} billion for houses, \euro{}\attScCostBaseTotTwoFifty{} billion in all, which, for scale, is \attScCostBaseTotTwoFiftyLo{} to \attScCostBaseTotTwoFiftyHi{} percent of MaPrimeR\'enov's annual budget of roughly \euro{}\attBudgetLo{}--\attBudgetHi{} billion. % [CHECK] cite the budget figure (Cour des comptes or ANAH) before submission.
-At the medium benchmark it is \euro{}\attScCostBaseTotFiveHundred{} billion per year, \attScCostBaseTotFiveHundredLo{} to \attScCostBaseTotFiveHundredHi{} percent of the budget. The comparison is one of scale and not a share of the programme: the bill covers listings on one platform in the estimation markets, counted per listing, whereas the programme reaches all owners. It does not say the programme is cheap. The bill covers only the sellers who are in the model's renovation problem, and an extension that lets uninformed sellers acquire a certificate and then renovate would enlarge the eligible population. These are upper bounds on a per-listing basis and they ignore the extensive-margin participation decision. By Remark~\ref{rem:welfare} they are incentive-compatibility objects and not optimal transfers: with a shadow cost of public funds $\lambda>1$ the regulator would set the operative subsidy below $S^*_m$.
+At the medium benchmark it is \euro{}\attScCostBaseTotFiveHundred{} billion per year, \attScCostBaseTotFiveHundredLo{} to \attScCostBaseTotFiveHundredHi{} percent of the budget. The comparison gives scale only: the bill covers listings on one platform in the estimation markets, counted per listing, whereas the programme reaches all owners, so it is not a share of the programme and does not show the programme to be cheap. The bill covers only the sellers who are in the model's renovation problem, and an extension that lets uninformed sellers acquire a certificate and then renovate would enlarge the eligible population. These are upper bounds on a per-listing basis and they ignore the extensive-margin participation decision. By Remark~\ref{rem:welfare} they are incentive-compatibility objects and not optimal transfers: with a shadow cost of public funds $\lambda>1$ the regulator would set the operative subsidy below $S^*_m$.
```

## main:L322-323 (lines 322-323): REVIEW-FLAGS
- words 218 -> 217; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 2->1; G5 flags: new words: because
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 \paragraph{Full attention.}
-The full-attention result bounds how far the threshold could move if every EPC-sensitive buyer attended to energy on every listing. At the upper bound the apartment threshold rises from \euro{}\attScBaseRbarApt{} to \euro{}\attScHiRbarApt{} per m\textsuperscript{2} on average and the annual bill at the light benchmark falls from \euro{}\attScBaseCostTwoFiftyApt{} to \euro{}\attScHiCostTwoFiftyApt{} billion, and at the medium benchmark from \euro{}\attScBaseCostFiveHundredApt{} to \euro{}\attScHiCostFiveHundredApt{} billion (Figure~\ref{fig:policy_bound}). A higher rating premium also raises the gain from hiding, so \attScHiNCasApt{} of \attNMarketsApt{} apartment markets move into Complete Adverse Selection and the mean hiding rate rises to \attScHiSigmaApt{} percent. The lower bound is zero. These are bounds, not estimates: the data do not separate the share of EPC-sensitive buyers from the attention they pay to displayed ratings, and the upper bound rests on the energy-cost anchor and its ten-year horizon. In houses the same exercise moves \attScHiNCasHouse{} of \attNMarketsHouse{} markets into Complete Adverse Selection at once, with a mean hiding rate of \attScHiSigmaHouse{} percent. With one hiding cost per market every informed seller faces the same comparison, so the rise in the rating premium by a factor of about $1/\hat\rho$ pushes the gain from hiding past that cost for all of them together. With costs that differ across sellers only those whose cost lies below the new gain would start hiding. We regard the jump as a feature of the single cost and report the bound for apartments only.
+The full-attention result bounds how far the threshold could move if every EPC-sensitive buyer attended to energy on every listing. At the upper bound the apartment threshold rises from \euro{}\attScBaseRbarApt{} to \euro{}\attScHiRbarApt{} per m\textsuperscript{2} on average and the annual bill at the light benchmark falls from \euro{}\attScBaseCostTwoFiftyApt{} to \euro{}\attScHiCostTwoFiftyApt{} billion, and at the medium benchmark from \euro{}\attScBaseCostFiveHundredApt{} to \euro{}\attScHiCostFiveHundredApt{} billion (Figure~\ref{fig:policy_bound}). A higher rating premium also raises the gain from hiding, so \attScHiNCasApt{} of \attNMarketsApt{} apartment markets move into Complete Adverse Selection and the mean hiding rate rises to \attScHiSigmaApt{} percent. The lower bound is zero. These are bounds because the data do not separate the share of EPC-sensitive buyers from the attention they pay to displayed ratings, and the upper bound rests on the energy-cost anchor and its ten-year horizon. In houses the same exercise moves \attScHiNCasHouse{} of \attNMarketsHouse{} markets into Complete Adverse Selection at once, with a mean hiding rate of \attScHiSigmaHouse{} percent. With one hiding cost per market every informed seller faces the same comparison, so the rise in the rating premium by a factor of about $1/\hat\rho$ pushes the gain from hiding past that cost for all of them together. With costs that differ across sellers only those whose cost lies below the new gain would start hiding. We regard the jump as a feature of the single cost and report the bound for apartments only.
```

## main:L360-360 (lines 360-360): REVIEW-FLAGS
- words 112 -> 114; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: new words: additions, narrow
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-The bound is not a point estimate, and the data do not pin the saving down further. Three things would. Hiding rates by EPC letter identify more than one point of the cost distribution: the registry shows them rising from E to G in apartments, \attHideLetterEApt{}, \attHideLetterFApt{} and \attHideLetterGApt{} percent, as a gain from hiding that rises with consumption predicts. Year-by-year hiding rates, once certificate dates are re-pulled, would exploit variation in the gain over time. A direct measure of what concealment costs sellers would give the distribution itself. Until then the finding is that, even at the bound, the saving is small against the budget, and the apartment figure rests mostly on one market.
+The bound is not a point estimate, and the data do not pin the saving down further. Three additions would narrow it. Hiding rates by EPC letter identify more than one point of the cost distribution: the registry shows them rising from E to G in apartments, \attHideLetterEApt{}, \attHideLetterFApt{} and \attHideLetterGApt{} percent, as a gain from hiding that rises with consumption predicts. Year-by-year hiding rates, once certificate dates are re-pulled, would exploit variation in the gain over time. A direct measure of what concealment costs sellers would give the distribution itself. Until then the finding is that, even at the bound, the saving is small against the budget, and the apartment figure rests mostly on one market.
```

## main:L255-255 (lines 255-255): CLEAN
- words 211 -> 210; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-No flat subsidy fits every market. Covering every apartment market at the light benchmark takes \euro{}\attBaseSMaxTwoFiftyApt{} per m\textsuperscript{2}, against a conditional median of \euro{}\attBaseSMedTwoFiftyApt{}, and for houses \euro{}\attBaseSMaxTwoFiftyHouse{} against \euro{}\attBaseSMedTwoFiftyHouse{}; at the medium benchmark the figures are \euro{}\attBaseSMaxFiveHundredApt{} against \euro{}\attBaseSMedFiveHundredApt{} and \euro{}\attBaseSMaxFiveHundredHouse{} against \euro{}\attBaseSMedFiveHundredHouse{}. A uniform national subsidy is therefore poorly targeted because the cost-sharing requirement varies across markets, although $S^*$ is an incentive-compatibility object and not a welfare optimum (Remark~\ref{rem:welfare}). Figure~\ref{fig:policy_map} maps $S^*_m/\hat R$ at the light benchmark, with bubble size encoding the local threshold $\bar R_m$. A flat per-m\textsuperscript{2} grant set at the cross-market mean would over-pay markets where the private incentive already suffices and under-pay those where the gap is largest, the first through fiscal waste and the second through forgone renovations. The dispersion is systematic: the cost-sharing ratio is low where $\bar R_m$ is high, and $\bar R_m$ is high where local prices are high and the energy-efficiency premium $\hat\beta_{1,m}$ is large. The premium reflects the capitalised value of verified quality to sensitive buyers, not a freestanding measure of how many buyers are sensitive (Appendix~\ref{app:rho_identification} shows the two are not identified apart in price data alone). An efficient programme would differentiate the subsidy along these axes and co-target audit-infrastructure investment on markets where the threshold is large but verification is scarce, since $\pi$ does not change the threshold but scales the population it applies to (Section~\ref{ss:att_policy}).
+No flat subsidy fits every market. Covering every apartment market at the light benchmark takes \euro{}\attBaseSMaxTwoFiftyApt{} per m\textsuperscript{2}, against a conditional median of \euro{}\attBaseSMedTwoFiftyApt{}, and for houses \euro{}\attBaseSMaxTwoFiftyHouse{} against \euro{}\attBaseSMedTwoFiftyHouse{}; at the medium benchmark the figures are \euro{}\attBaseSMaxFiveHundredApt{} against \euro{}\attBaseSMedFiveHundredApt{} and \euro{}\attBaseSMaxFiveHundredHouse{} against \euro{}\attBaseSMedFiveHundredHouse{}. A uniform national subsidy is therefore poorly targeted because the cost-sharing requirement varies across markets, although $S^*$ is an incentive-compatibility object and not a welfare optimum (Remark~\ref{rem:welfare}). Figure~\ref{fig:policy_map} maps $S^*_m/\hat R$ at the light benchmark, with bubble size encoding the local threshold $\bar R_m$. A flat per-m\textsuperscript{2} grant set at the cross-market mean would over-pay markets where the private incentive already suffices and under-pay those where the gap is largest, the first through fiscal waste and the second through forgone renovations. The dispersion is systematic: the cost-sharing ratio is low where $\bar R_m$ is high, and $\bar R_m$ is high where local prices are high and the energy-efficiency premium $\hat\beta_{1,m}$ is large. The premium reflects the capitalised value of verified quality to sensitive buyers and does not measure how many buyers are sensitive (Appendix~\ref{app:rho_identification} shows the two are not identified apart in price data alone). An efficient programme would differentiate the subsidy along these axes and co-target audit-infrastructure investment on markets where the threshold is large but verification is scarce, since $\pi$ does not change the threshold but scales the population it applies to (Section~\ref{ss:att_policy}).
```

## main:L311-312 (lines 311-312): CLEAN
- words 131 -> 129; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 \paragraph{Salience changes who hides, not who renovates.}
-A mandatory ``rating not provided'' field in advertisements, or a platform default that treats a missing rating as a rating, would raise attention to silent listings. At a fixed hiding rate the policy lowers the non-disclosure premium by $\hat\lambda_m$, by~\eqref{eq:att_lambda}: \attSalienceApt{} log points in apartments and \attSalienceHouse{} in houses. With the equilibrium response every market moves to Cost-Deterred Hiding. The mean hiding rate falls from \attSigmaObsApt{} to \attSigmaFullApt{} percent in apartments and from \attSigmaObsHouse{} to \attSigmaFullHouse{} percent in houses, and \attCfRevealedApt{} hidden unfavourable ratings of informed apartment sellers become visible, with no additional renovation (Table~\ref{tab:att_scenarios}). The threshold does not move, and neither does the subsidy bill. The apartment response is a knife-edge, because a single hiding cost makes the Partial Pooling band only \attBandWidthApt{} log points wide (Corollary~\ref{cor:att_band}), so we read it as a direction and not as an elasticity.
+A mandatory ``rating not provided'' field in advertisements, or a platform default that treats a missing rating as a rating, would raise attention to silent listings. At a fixed hiding rate the policy lowers the non-disclosure premium by $\hat\lambda_m$, by~\eqref{eq:att_lambda}: \attSalienceApt{} log points in apartments and \attSalienceHouse{} in houses. With the equilibrium response every market moves to Cost-Deterred Hiding. The mean hiding rate falls from \attSigmaObsApt{} to \attSigmaFullApt{} percent in apartments and from \attSigmaObsHouse{} to \attSigmaFullHouse{} percent in houses, and \attCfRevealedApt{} hidden unfavourable ratings of informed apartment sellers become visible, with no additional renovation (Table~\ref{tab:att_scenarios}). The threshold does not move, and neither does the subsidy bill. The apartment response is a knife-edge, because a single hiding cost makes the Partial Pooling band only \attBandWidthApt{} log points wide (Corollary~\ref{cor:att_band}), so we read it as a direction, not an elasticity.
```

## main:L106-106 (lines 106-106): UNCHANGED
- words 36 -> 36; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L126-129 (lines 126-129): UNCHANGED
- words 43 -> 43; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L147-147 (lines 147-147): UNCHANGED
- words 64 -> 64; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L158-159 (lines 158-159): UNCHANGED
- words 44 -> 44; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L163-163 (lines 163-163): UNCHANGED
- words 70 -> 70; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L200-203 (lines 200-203): UNCHANGED
- words 21 -> 21; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L209-209 (lines 209-209): UNCHANGED
- words 196 -> 196; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L211-211 (lines 211-211): UNCHANGED
- words 202 -> 202; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L216-216 (lines 216-216): UNCHANGED
- words 52 -> 52; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L232-232 (lines 232-232): UNCHANGED
- words 255 -> 255; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L242-251 (lines 242-251): UNCHANGED
- words 48 -> 48; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L253-253 (lines 253-253): UNCHANGED
- words 255 -> 255; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L253-253#fn1 (lines 253-253): UNCHANGED
- words 36 -> 36; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L257-266 (lines 257-266): UNCHANGED
- words 62 -> 62; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L268-269#fn1 (lines 268-269): UNCHANGED
- words 48 -> 48; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L296-296 (lines 296-296): UNCHANGED
- words 148 -> 148; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L305-309 (lines 305-309): UNCHANGED
- words 115 -> 115; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L314-315 (lines 314-315): UNCHANGED
- words 48 -> 48; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L320-320 (lines 320-320): UNCHANGED
- words 56 -> 56; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L325-334 (lines 325-334): UNCHANGED
- words 56 -> 56; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L336-337 (lines 336-337): UNCHANGED
- words 143 -> 143; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## main:L358-358 (lines 358-358): UNCHANGED
- words 172 -> 172; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n
