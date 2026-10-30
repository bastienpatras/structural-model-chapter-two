# Approval sheet: X-marker

Riskiest first. Decide each unit: accept / reject / edit. Nothing is applied before a decision.

## X-marker:04-attention-draft:L41-42 (lines 41-42): REVIEW-FLAGS
- words 136 -> 135; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: quantifier:only 1->0; G5 flags: new words: premise
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 % [AUTHOR REWRITE] mechanism paragraphs
-What these amendments share is that the buyer facing a silent listing still thinks about its energy performance; she only reasons about it imperfectly. A large body of evidence suggests that consumers often do not think about costs that are not put in front of them, and that when they do not, they act as if those costs were small rather than average. Buyers under-react to sales taxes that are not included in posted prices \citep{chetty_salience_2009}, to road tolls collected electronically \citep{finkelstein_eztax_2009} and to shrouded shipping fees \citep{brown_shrouded_2010}. Energy operating costs are a documented instance in durable-goods markets \citep[e.g.,][]{allcott_consumers_2011, sallee_rational_2014, allcott_evaluating_2015}. Models of focusing, salience and sparsity formalise the same idea, that the attributes a choice set makes salient receive more weight than those it leaves in the background \citep[e.g.,][]{koszegi_model_2013, bordalo_salience_2013, gabaix_sparsity_2014}. In financial markets, limited attention changes how disclosed and undisclosed information is priced \citep[e.g.,][]{hirshleifer_limited_2003, dellavigna_investor_2009}.
+These amendments share the premise that the buyer facing a silent listing still thinks about its energy performance but reasons about it imperfectly. A large body of evidence suggests that consumers often do not think about costs that are not put in front of them, and that when they do not, they act as if those costs were small rather than average. Buyers under-react to sales taxes that are not included in posted prices \citep{chetty_salience_2009}, to road tolls collected electronically \citep{finkelstein_eztax_2009} and to shrouded shipping fees \citep{brown_shrouded_2010}. Energy operating costs are a documented instance in durable-goods markets \citep[e.g.,][]{allcott_consumers_2011, sallee_rational_2014, allcott_evaluating_2015}. Models of focusing, salience and sparsity formalise the same idea, that the attributes a choice set makes salient receive more weight than those it leaves in the background \citep[e.g.,][]{koszegi_model_2013, bordalo_salience_2013, gabaix_sparsity_2014}. In financial markets, limited attention changes how disclosed and undisclosed information is priced \citep[e.g.,][]{hirshleifer_limited_2003, dellavigna_investor_2009}.
```

## X-marker:01-introduction-draft:L188-205 (lines 188-205): REVIEW-FLAGS
- words 251 -> 230; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 3->2; hedge:about 2->1; number_word:one 5->4; G5 flags: sentences 11->10; new words: offer, state
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -6,6 +6,5 @@
 renovate and publish a good one, earning the quality premium, or stay silent and earn the
 non-disclosure premium instead, so the premium to opacity looks like an opportunity cost of
-renovation that raises the private hurdle above engineering cost. In equilibrium it does not, except in the corner where every informed low-quality seller hides. This has an unexpected policy
-implication. Because the equilibrium absorbs enforcement through the fraction of sellers who
+renovation that raises the private hurdle above engineering cost. In equilibrium it does not, except in the corner where every informed low-quality seller hides. Because the equilibrium absorbs enforcement through the fraction of sellers who
 conceal, the renovation threshold depends only on the price gap between disclosed quality
 levels and is independent of enforcement intensity. Renovation subsidies, enforcement against
@@ -14,5 +13,4 @@
 \citet{gillingham_palmer_2014}. The result holds outside the corner in which every informed low-quality seller hides, and with one concealment cost per market. % [AUTHOR REWRITE] The extension of Section~\ref{ss:attention} brings the inattention
 diagnosis inside the disclosure game: buyers who attend less to energy when no rating is shown let
-silence earn a premium that no belief about quality can produce. We do not claim to have estimated the one true model of housing
-disclosure; we propose one way of reading these data through a workhorse framework, and we are
-explicit throughout about which parameters are point-identified and which are bounded.
+silence earn a premium that no belief about quality can produce. We offer one reading of these data through a workhorse framework of housing
+disclosure, and state throughout which parameters are point-identified and which are bounded.
```

## X-marker:01-introduction-draft:L207-219 (lines 207-219): REVIEW-FLAGS
- words 221 -> 215; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: number_word:one 1->0; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -10,4 +10,4 @@
 \euro{}\attScCostBaseTotTwoFifty{}--\attScCostBaseTotFiveHundred{} billion a year in our listing sample at plausible renovation-cost benchmarks, for scale between \attScCostBaseTotTwoFiftyLo{} and
 \attScCostBaseTotFiveHundredHi{} percent of MaPrimeR\'enov's current annual budget. Efficient targeting requires conditioning subsidy design
-on local market composition rather than applying one national rate. Enforcement against strategic hiding and investment in audit
+on local market composition. Enforcement against strategic hiding and investment in audit
 infrastructure act on separate margins: the first changes who hides, the second who is eligible to renovate, and neither lowers the subsidy a given seller needs.
```

## X-marker:main:L274-275 (lines 274-275): REVIEW-FLAGS
- words 152 -> 151; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 1->0; quantifier:only 1->0; G5 flags: new words: besides, other, regulator
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 % [AUTHOR REWRITE] section motivation
-The subsidy is not the regulator's only instrument, and the others act on different margins of the seller's problem (Table~\ref{tab:instruments}). Enforcement against hiding raises the cost of concealment and changes who hides. Raising the share of informed sellers $\pi$ changes how many sellers can renovate at all. Two further instruments act on buyers: making silence as salient as a rating raises the attention buyers pay to a listing that shows no rating, and full attention raises the attention they pay to every listing. Three questions follow. Does each instrument move the renovation threshold $\bar R$, and with it the subsidy a seller needs? Does it change who hides? And would a simple measure such as making silence salient reduce what the state has to spend on subsidies? The next proposition answers the first two questions for each instrument, with the hiding cost held at its calibrated value, and the closing subsection returns to the third.
+The regulator has other instruments besides the subsidy, and they act on different margins of the seller's problem (Table~\ref{tab:instruments}). Enforcement against hiding raises the cost of concealment and changes who hides. Raising the share of informed sellers $\pi$ changes how many sellers can renovate at all. Two further instruments act on buyers: making silence as salient as a rating raises the attention buyers pay to a listing that shows no rating, and full attention raises the attention they pay to every listing. Three questions follow. Does each instrument move the renovation threshold $\bar R$, and with it the subsidy a seller needs? Does it change who hides? And would a simple measure such as making silence salient reduce what the state has to spend on subsidies? The next proposition answers the first two questions for each instrument, with the hiding cost held at its calibrated value, and the closing subsection returns to the third.
```

## X-marker:main:L368-368 (lines 368-368): REVIEW-FLAGS
- words 179 -> 176; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 11->10; new words: makes, suffices
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-The resolution requires two departures from the classical framework, each empirically motivated and individually insufficient. First, not all sellers are informed. At listing time, only 51.8\% of apartment sellers and 41.7\% of house sellers hold a certified energy audit. When buyers observe a missing EPC score, they face genuine ambiguity. The non-disclosing seller may be concealing an unfavorable rating or may simply not know her property's energy performance. Uninformed sellers therefore provide strategic hiders with involuntary cover, preventing silence from being read as the worst possible signal. Second, not all buyers price energy performance into their offers. When the share of energy-sensitive buyers is moderate, the revenue penalty from concealment is diluted, making hiding profitable even against a skeptical pool. Neither departure alone is sufficient. Uninformed sellers keep silence ambiguous, but buyer heterogeneity ensures that exploiting this ambiguity is financially worthwhile. In apartment markets a third ingredient is needed, because no belief about silence can price a silent listing above a verified efficient one: buyers attend to energy much less when a listing shows no rating than when it shows one. % [AUTHOR REWRITE]
+The resolution requires two departures from the classical framework, each empirically motivated and individually insufficient. First, not all sellers are informed. At listing time, only 51.8\% of apartment sellers and 41.7\% of house sellers hold a certified energy audit. When buyers observe a missing EPC score, they face genuine ambiguity. The non-disclosing seller may be concealing an unfavorable rating or may simply not know her property's energy performance. Uninformed sellers therefore provide strategic hiders with involuntary cover, preventing silence from being read as the worst possible signal. Second, not all buyers price energy performance into their offers. When the share of energy-sensitive buyers is moderate, the revenue penalty from concealment is diluted, making hiding profitable even against a skeptical pool. Neither departure suffices alone: uninformed sellers keep silence ambiguous, but buyer heterogeneity makes exploiting this ambiguity financially worthwhile. In apartment markets a third ingredient is needed, because no belief about silence can price a silent listing above a verified efficient one: buyers attend to energy much less when a listing shows no rating than when it shows one. % [AUTHOR REWRITE]
```

## X-marker:main:L371-372 (lines 371-372): REVIEW-FLAGS
- words 300 -> 300; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: new words: yields
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
-These two forces generate three equilibrium regimes. In the partial-pooling equilibrium that describes the bulk of French housing markets, the fraction of informed low-quality sellers that hides adjusts endogenously until the marginal hider is exactly indifferent between concealment and disclosure. This indifference condition delivers the paper's central theoretical result. The non-disclosure premium equals exactly the concealment cost in partial pooling, invariant to the share of informed sellers and the share of energy-sensitive buyers. We identify the concealment cost directly from the disclosed-price gap and the registry-measured belief, without needing buyer energy-sensitivity to be separately estimated, and test the indifference prediction against it rather than assume it. The two segments concur less than an earlier reading of these facts suggested. Concealment costs are 2.4\% of property value for apartments and 3.5\% for houses, of the same order across two segments that differ in buyer energy-sensitivity (49.5\% for apartments, 45.8\% for houses, identified from an external energy-cost anchor rather than from the price data used to construct the premium itself); but the indifference prediction itself holds for houses and is decisively rejected for apartments, where the non-disclosure premium exceeds what the concealment cost and the registry-measured belief predict by a wide and precisely estimated margin. One attention parameter per segment, measuring how much buyers attend to energy on listings that show no rating, accounts for both the rejection in apartments and the fit in houses (Section~\ref{ss:attention}). % [AUTHOR REWRITE]
+These two forces generate three equilibrium regimes. In the partial-pooling equilibrium that describes the bulk of French housing markets, the fraction of informed low-quality sellers that hides adjusts endogenously until the marginal hider is exactly indifferent between concealment and disclosure. This indifference condition yields the paper's central theoretical result. The non-disclosure premium equals exactly the concealment cost in partial pooling, invariant to the share of informed sellers and the share of energy-sensitive buyers. We identify the concealment cost directly from the disclosed-price gap and the registry-measured belief, without needing buyer energy-sensitivity to be separately estimated, and test the indifference prediction against it rather than assume it. The two segments concur less than an earlier reading of these facts suggested. Concealment costs are 2.4\% of property value for apartments and 3.5\% for houses, of the same order across two segments that differ in buyer energy-sensitivity (49.5\% for apartments, 45.8\% for houses, identified from an external energy-cost anchor rather than from the price data used to construct the premium itself); but the indifference prediction itself holds for houses and is decisively rejected for apartments, where the non-disclosure premium exceeds what the concealment cost and the registry-measured belief predict by a wide and precisely estimated margin. One attention parameter per segment, measuring how much buyers attend to energy on listings that show no rating, accounts for both the rejection in apartments and the fit in houses (Section~\ref{ss:attention}). % [AUTHOR REWRITE]
 Strategic hiding is itself uncommon. 15.2\% of informed apartment sellers with unfavorable ratings withhold them, versus 6.8\% for houses. The non-disclosure premium survives not because strategic hiding is pervasive but because genuine uninformedness is. The uninformed seller, who pays no concealment cost yet receives the same premium as the strategic hider, is the residual claimant on the information rent; the informed hider, in the segment where the model fits, merely breaks even.
```

## X-marker:main:L374-375 (lines 374-375): REVIEW-FLAGS
- words 273 -> 271; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 10->9; new words: respect
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
-The policy implications depart from textbook prescriptions in one consequential way. Although the renovation threshold mechanically incorporates the concealment cost, the seller's indifference condition causes that cost to cancel exactly in partial pooling. The renovation incentive reduces to the verified-quality premium, the price gap between high-quality and low-quality disclosed properties, and is invariant to both the concealment cost and the share of informed sellers. Tightening enforcement against non-disclosure therefore does not move the renovation threshold in the empirically dominant regime. The regulator faces three distinct instruments: renovation subsidies (closing the gap between the verified-quality premium and the renovation cost), enforcement against strategic hiding (relevant only outside partial pooling), and audit-infrastructure investment (scaling how many sellers the other two instruments reach, not the per-seller incentive itself). These act on distinct margins. Limited attention adds a further instrument: making silence as salient as a rating, which acts on buyers and lowers hiding without moving the renovation threshold, whereas a higher weight on displayed ratings could raise it, within a bound the data do not pin down (Section~\ref{ss:att_policy}). % [AUTHOR REWRITE]
+The policy implications depart from textbook prescriptions in one respect. Although the renovation threshold mechanically incorporates the concealment cost, the seller's indifference condition causes that cost to cancel exactly in partial pooling. The renovation incentive reduces to the verified-quality premium, the price gap between high-quality and low-quality disclosed properties, and is invariant to both the concealment cost and the share of informed sellers. Tightening enforcement against non-disclosure therefore does not move the renovation threshold in the empirically dominant regime. The regulator has three instruments that act on distinct margins: renovation subsidies (closing the gap between the verified-quality premium and the renovation cost), enforcement against strategic hiding (relevant only outside partial pooling), and audit-infrastructure investment (scaling how many sellers the other two instruments reach, not the per-seller incentive itself). Limited attention adds a further instrument: making silence as salient as a rating, which acts on buyers and lowers hiding without moving the renovation threshold, whereas a higher weight on displayed ratings could raise it, within a bound the data do not pin down (Section~\ref{ss:att_policy}). % [AUTHOR REWRITE]
  A uniform national subsidy exploits none of this structure. The minimum cost-sharing requirement varies widely, from markets where the private incentive already suffices to markets where the verified-quality premium is small, and aggregate programme costs among the sellers who can renovate run to \euro{}\attScCostBaseTotTwoFifty{} billion a year at the light renovation benchmark and \euro{}\attScCostBaseTotFiveHundred{} billion at the medium benchmark, between \attScCostBaseTotTwoFiftyLo{} and \attScCostBaseTotFiveHundredHi{} percent of the current annual budget of MaPrimeR\'enov'. Efficient targeting must condition on local market composition, directing public expenditure to markets where the private renovation gap is largest, with audit investment scaling how many sellers any subsidy reaches.
```

## X-marker:01-introduction-draft:L149-175 (lines 149-175): CLEAN
- words 342 -> 341; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -9,5 +9,5 @@
 house markets, and the cost of withholding a certificate settles at 2.4\% of property value for
 apartments and 3.5\% for houses, on the order of a third of the notary bill a French buyer
-separately pays on the same transaction. Both are economically substantial magnitudes, and of the
+separately pays on the same transaction. Both are economically substantial and of the
 same order in two segments that trade very differently. The model predicts, in the partial-pooling
 equilibrium that describes the bulk of French housing markets, that the non-disclosure premium
```

## X-marker:04-attention-draft:L282-283 (lines 282-283): CLEAN
- words 100 -> 99; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 % [AUTHOR REWRITE] lead-in to the proposition on seller types
-The three regimes keep their logic, and the central result of Section~\ref{sec:equilibrium} survives intact: in Partial Pooling the non-disclosure premium equals the hiding cost, because the marginal hider is indifferent. That statement concerns the marginal seller, not buyers, so it holds whatever buyers attend to. What limited attention changes is where silence sits among the ratings, and with it which seller gains most from silence. The next proposition derives the price of each type of listing and the payoff of each type of seller. Uninformed sellers cannot hide a rating they do not have, so they bear no hiding cost.
+The three regimes keep their logic, and the central result of Section~\ref{sec:equilibrium} survives: in Partial Pooling the non-disclosure premium equals the hiding cost, because the marginal hider is indifferent. That statement concerns the marginal seller, not buyers, so it holds whatever buyers attend to. What limited attention changes is where silence sits among the ratings, and with it which seller gains most from silence. The next proposition derives the price of each type of listing and the payoff of each type of seller. Uninformed sellers cannot hide a rating they do not have, so they bear no hiding cost.
```

## X-marker:04-attention-draft:L13-14 (lines 13-14): UNCHANGED
- words 127 -> 127; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:main:L239-240 (lines 239-240): UNCHANGED
- words 101 -> 101; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:main:L239-240#fn1 (lines 239-240): UNCHANGED
- words 51 -> 51; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:main:L342-343 (lines 342-343): UNCHANGED
- words 149 -> 149; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:04-attention-draft:L345-346 (lines 345-346): UNCHANGED
- words 333 -> 333; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:main:L377-378 (lines 377-378): UNCHANGED
- words 126 -> 126; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:04-attention-draft:L444-445 (lines 444-445): UNCHANGED
- words 193 -> 193; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## X-marker:04-attention-draft:L447-448 (lines 447-448): UNCHANGED
- words 131 -> 131; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n
