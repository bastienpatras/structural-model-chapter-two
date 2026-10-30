# Approval sheet: 04-attention-draft

Riskiest first. Decide each unit: accept / reject / edit. Nothing is applied before a decision.

## 04-attention-draft:L16-16 (lines 16-16): REVIEW-FLAGS
- words 118 -> 116; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: quantifier:only 0->1; G5 flags: new words: only
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-One answer is that buyers attend to energy when a listing puts it in front of them, and much less when it does not. We allow for this mechanism without imposing it: full attention remains a special case, and the data decide between the two. The extension changes the buyer side of the model and nothing else. It nests the model of Sections~\ref{ss:model_setup}--\ref{sec:equilibrium} as a special case and preserves its regimes. It leaves $\hat\rho_m$ unchanged as a number but reads it as effective attention to displayed ratings, and it reads the concealment cost off the non-disclosure premium rather than off $\hat\beta_{1,m}\hat e^*_m$ (Proposition~\ref{prop:att_identification}). It also turns the over-identifying wedge $\hat\lambda_m$ of Section~\ref{sec:identification} into an estimate of how much attention silent listings receive.
+One answer is that buyers attend to energy when a listing puts it in front of them, and much less when it does not. We allow for this mechanism without imposing it, so full attention remains a special case and the data decide between the two. The extension changes only the buyer side of the model. It nests the model of Sections~\ref{ss:model_setup}--\ref{sec:equilibrium} as a special case and preserves its regimes. It leaves $\hat\rho_m$ unchanged as a number but reads it as effective attention to displayed ratings, and it reads the concealment cost off the non-disclosure premium rather than off $\hat\beta_{1,m}\hat e^*_m$ (Proposition~\ref{prop:att_identification}). It turns the over-identifying wedge $\hat\lambda_m$ of Section~\ref{sec:identification} into an estimate of how much attention silent listings receive.
```

## 04-attention-draft:L21-22 (lines 21-22): REVIEW-FLAGS
- words 134 -> 131; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: modal:cannot 1->2; negation:not 1->0; number_word:one 1->0; G5 flags: sentences 7->5; new words: resolve
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 \paragraph{Why the model above cannot reach the apartment wedge.}
-The difficulty is not one of calibration. In the model of Section~\ref{ss:model_setup}, a buyer who sees no rating prices the listing at her belief about its quality, and a belief about a binary rating lies between the worst rating and the best. A silent listing therefore sells at most at the price of a verified efficient listing: the ratio of the non-disclosure premium to the energy-efficiency premium is the pool belief, which is bounded by $\bar\theta\le1$ (Lemma~\ref{lem:model_bounds}(i)). The same bound applies to the differences-in-differences whenever the pool belief is stable across the reform.\footnote{The ordering survives exact pricing under the monotonicity condition discussed in Appendix~\ref{app:att_exact}. The levels make the same point: silent apartments sold above verified A-to-D listings by \attLevelGapPreApt{} log points before the reform and by \attLevelGapPostApt{} after, whereas the model prices silence below verified efficiency at any date and for any belief in $[0,1]$. Under Assumption~\ref{assum:no_pre_pricing} the pre-reform gap is non-energy, and the energy component of the post-reform gap is the DiD, \attExcessApt{} log points, still positive.} The apartment wedge of \attLamApt{} log points decomposes accordingly. Of it, \attExcessApt{} points are the amount by which $\hat\Delta$ exceeds $\hat\beta_1$, a region the model cannot enter. Only the remaining \attReachApt{} points, $(1-\hat e^*)\hat\beta_1$, are within reach of any change in how buyers form beliefs about silent listings.
+Calibration cannot resolve the difficulty. In the model of Section~\ref{ss:model_setup}, a buyer who sees no rating prices the listing at her belief about its quality, and a belief about a binary rating lies between the worst rating and the best. A silent listing therefore sells at most at the price of a verified efficient listing: the ratio of the non-disclosure premium to the energy-efficiency premium is the pool belief, which is bounded by $\bar\theta\le1$ (Lemma~\ref{lem:model_bounds}(i)). The same bound applies to the differences-in-differences whenever the pool belief is stable across the reform.\footnote{The ordering survives exact pricing under the monotonicity condition discussed in Appendix~\ref{app:att_exact}. The levels make the same point: silent apartments sold above verified A-to-D listings by \attLevelGapPreApt{} log points before the reform and by \attLevelGapPostApt{} after, whereas the model prices silence below verified efficiency at any date and for any belief in $[0,1]$. Under Assumption~\ref{assum:no_pre_pricing} the pre-reform gap is non-energy, and the energy component of the post-reform gap is the DiD, \attExcessApt{} log points, still positive.} The apartment wedge of \attLamApt{} log points decomposes accordingly: \attExcessApt{} points are the amount by which $\hat\Delta$ exceeds $\hat\beta_1$, a region the model cannot enter, and only the remaining \attReachApt{} points, $(1-\hat e^*)\hat\beta_1$, are within reach of any change in how buyers form beliefs about silent listings.
```

## 04-attention-draft:L37-38 (lines 37-38): REVIEW-FLAGS
- words 220 -> 213; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 3->2; G5 flags: new words: leave, natural, open
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 \paragraph{Belief-based amendments cannot reach the wedge.}
-This rules out the amendments that come to mind first. First, buyers may draw too little inference from silence, as in cursed equilibrium and in experimental evidence on disclosure games \citep[e.g.,][]{eyster_cursed_2005, jin_is_2021, hagenbach_motivated_2025}. Any such rule replaces the Bayesian belief $e^*$ by another number between zero and one, so it stays below the ceiling. It is also quantitatively small here. Sellers without a certificate make up about \attShareUninfApt{} percent of the silent apartment pool, so the Bayesian belief already sits within a few points of the prior, and full cursedness would account for about \attCursedApt{} of the \attLamApt{} points. Second, buyers may over-react to a displayed poor rating. That lowers the price of E-to-G listings, which is the base of both gaps, and it cancels from the comparison between silent and verified efficient listings. Third, the distrust discount on inferred quality allowed in Section~\ref{ss:model_setup} ($\alpha_k<\beta_k$) moves the price of silence down, not up. Observable composition does not resolve the puzzle either, because the indices hold the hedonic reference property fixed within each market and the comparison is a difference-in-differences. What these arguments do not exclude is a change in the \emph{unobserved} composition of the silent pool, most of which consists of sellers without a certificate: if the dwellings that were silent after the reform were of better unobserved quality, the wedge would rise without any change in attention.
+This rules out the natural amendments. First, buyers may draw too little inference from silence, as in cursed equilibrium and in experimental evidence on disclosure games \citep[e.g.,][]{eyster_cursed_2005, jin_is_2021, hagenbach_motivated_2025}. Any such rule replaces the Bayesian belief $e^*$ by another number between zero and one, so it stays below the ceiling. It is also quantitatively small here. Sellers without a certificate make up about \attShareUninfApt{} percent of the silent apartment pool, so the Bayesian belief already sits within a few points of the prior, and full cursedness would account for about \attCursedApt{} of the \attLamApt{} points. Second, buyers may over-react to a displayed poor rating. That lowers the price of E-to-G listings, which is the base of both gaps, and it cancels from the comparison between silent and verified efficient listings. Third, the distrust discount on inferred quality allowed in Section~\ref{ss:model_setup} ($\alpha_k<\beta_k$) moves the price of silence down, not up. Observable composition does not resolve the puzzle either, because the indices hold the hedonic reference property fixed within each market and the comparison is a difference-in-differences. The arguments leave open a change in the \emph{unobserved} composition of the silent pool, most of which consists of sellers without a certificate: if the dwellings that were silent after the reform were of better unobserved quality, the wedge would rise without any change in attention.
```

## 04-attention-draft:L110-110 (lines 110-110): REVIEW-FLAGS
- words 188 -> 186; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: new words: amounts
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-The term follows the limited-attention literature, in which an agent who does not attend to an attribute replaces it with a default value rather than with an inference \citep{gabaix_sparsity_2014, gabaix_behavioral_2019}. The default is therefore not a belief about the dwelling's rating. It is what the buyer implicitly assumes when the question of energy never arises. Three benchmark values fix ideas. With $C^{\rm def}=0$ no energy cost is priced at all, which does not mean the buyer believes the dwelling consumes nothing, only that energy plays no part in her valuation. With $C^{\rm def}$ equal to the prior mean cost $\bar\theta C_1+(1-\bar\theta)C_0$, the inattentive buyer behaves like one who assumes an average dwelling, which is cursedness by another name. With $C^{\rm def}=\bar C^{\rm sil}$ she happens to subtract exactly what an attentive buyer would infer, and attention becomes irrelevant. The same default applies to rated and silent listings, because a buyer who does not attend to energy, by definition, does not use what the listing shows about it. Which value is relevant is an empirical question: Proposition~\ref{prop:att_incentives}(iii) shows that the extension can explain the apartment wedge only if $C^{\rm def}<C_1$, and Proposition~\ref{prop:att_identification}(iii) shows what the data can say about its level.
+The term follows the limited-attention literature, in which an agent who does not attend to an attribute replaces it with a default value rather than with an inference \citep{gabaix_sparsity_2014, gabaix_behavioral_2019}. The default is therefore not a belief about the dwelling's rating. It is what the buyer implicitly assumes when the question of energy never arises. Three benchmark values fix ideas. With $C^{\rm def}=0$ no energy cost is priced at all, which does not mean the buyer believes the dwelling consumes nothing, only that energy plays no part in her valuation. With $C^{\rm def}$ equal to the prior mean cost $\bar\theta C_1+(1-\bar\theta)C_0$, the inattentive buyer behaves like one who assumes an average dwelling, which amounts to cursedness. With $C^{\rm def}=\bar C^{\rm sil}$ she happens to subtract exactly what an attentive buyer would infer, and attention becomes irrelevant. The same default applies to rated and silent listings, because a buyer who does not attend to energy, by definition, does not use what the listing shows about it. Which value is relevant is an empirical question: Proposition~\ref{prop:att_incentives}(iii) shows that the extension can explain the apartment wedge only if $C^{\rm def}<C_1$, and Proposition~\ref{prop:att_identification}(iii) shows what the data can say about its level.
```

## 04-attention-draft:L225-225 (lines 225-225): REVIEW-FLAGS
- words 159 -> 158; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 5->6; new words: amounts
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-Inattention that is the same for rated and silent listings is equivalent to having fewer EPC-sensitive buyers: it scales both premia together and leaves the model of Section~\ref{sec:equilibrium} intact (part iv). Differential attention matters only if the default is optimistic (part iii); a buyer who, without thinking about energy, implicitly assumes an average dwelling is a cursed buyer by another name and stays below the ceiling.\footnote{If the default equals the prior mean cost $\bar\theta C_1+(1-\bar\theta)C_0$, it is at least $C_1$, and silence never outprices a verified efficient rating. If it equals the rational cost of the silent pool, attention is irrelevant. The evidence on shrouded costs cited above finds under-weighting toward zero rather than toward the mean, which supports an optimistic default. Housing-specific evidence on this point does not yet exist, and it is the assumption on which the extension most depends.} And the high-quality seller loses her automatic preference for disclosure once silence outprices a verified efficient rating, so that only the hiding cost stops her from hiding (part ii). Applied to the seven letters instead of the two quality levels, Lemma~\ref{lem:att_prices} also predicts where silence sits among ratings: the gap between a rated listing and a silent one should be linear in the letter's energy cost and cross zero at $C^*$. The model of Section~\ref{sec:equilibrium} places that crossing between D and E; limited attention with an optimistic default places it at or above A.
+Inattention that is the same for rated and silent listings amounts to having fewer EPC-sensitive buyers. It scales both premia together and leaves the model of Section~\ref{sec:equilibrium} intact (part iv). Differential attention matters only if the default is optimistic (part iii); a buyer who, without thinking about energy, implicitly assumes an average dwelling is a cursed buyer by another name and stays below the ceiling.\footnote{If the default equals the prior mean cost $\bar\theta C_1+(1-\bar\theta)C_0$, it is at least $C_1$, and silence never outprices a verified efficient rating. If it equals the rational cost of the silent pool, attention is irrelevant. The evidence on shrouded costs cited above finds under-weighting toward zero rather than toward the mean, which supports an optimistic default. Housing-specific evidence on this point does not yet exist, and it is the assumption on which the extension most depends.} And the high-quality seller loses her automatic preference for disclosure once silence outprices a verified efficient rating, so that only the hiding cost stops her from hiding (part ii). Applied to the seven letters instead of the two quality levels, Lemma~\ref{lem:att_prices} also predicts where silence sits among ratings: the gap between a rated listing and a silent one should be linear in the letter's energy cost and cross zero at $C^*$. The model of Section~\ref{sec:equilibrium} places that crossing between D and E; limited attention with an optimistic default places it at or above A.
```

## 04-attention-draft:L375-376 (lines 375-376): REVIEW-FLAGS
- words 133 -> 130; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 5->6; new words: enters
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 \paragraph{High-quality hiding and non-strategic silence.}
-Proposition~\ref{prop:att_incentives}(ii) and Corollary~\ref{cor:att_hq} say when high-quality sellers may hide: only if silence sells above a verified efficient rating. The registry shows similar hiding rates for the two grades, \attSigmaOneApt{} against \attSigmaZeroApt{} percent in apartments and \attSigmaOneHouse{} against \attSigmaZeroHouse{} percent in houses. In apartments silence pays a high-quality seller \attExcessApt{} log points more than her rating, yet she displays, because in Partial Pooling her slack is $b+c_1$ (Proposition~\ref{prop:att_seller_types}). The pattern in the registry is not evidence for strategic hiding by high-quality sellers: house sellers of high quality stay silent although silence costs them about \attHighLossHouse{} log points relative to their rating, so some silence is not strategic at all, for instance listings whose certificate is still pending. The same non-strategic silence is in the hiding rate of low-quality sellers, so the interior hiding rates we use may overstate strategic hiding.
+Proposition~\ref{prop:att_incentives}(ii) and Corollary~\ref{cor:att_hq} say when high-quality sellers may hide: only if silence sells above a verified efficient rating. The registry shows similar hiding rates for the two grades, \attSigmaOneApt{} against \attSigmaZeroApt{} percent in apartments and \attSigmaOneHouse{} against \attSigmaZeroHouse{} percent in houses. In apartments silence pays a high-quality seller \attExcessApt{} log points more than her rating, yet she displays, because in Partial Pooling her slack is $b+c_1$ (Proposition~\ref{prop:att_seller_types}). The registry pattern is not evidence for strategic hiding by high-quality sellers. House sellers of high quality stay silent although silence costs them about \attHighLossHouse{} log points relative to their rating, so some silence is not strategic at all, for instance listings whose certificate is still pending. The same non-strategic silence enters the hiding rate of low-quality sellers, so the interior hiding rates we use may overstate strategic hiding.
```

## 04-attention-draft:L463-463 (lines 463-463): REVIEW-FLAGS
- words 84 -> 73; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 5->3; new words: whichever
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-The model does not take a stance on why apartment buyers fail to attend to energy when no rating is shown. It may be that energy is bundled into service charges. It may be that apartment buyers, often moving from rented housing in which heating was included, have no habit of pricing it. Or it may be that decisions in fast urban markets leave little room to ask. Irrespective of which applies, the implication for prices is the same, and so is the estimate.
+The model does not take a stance on why apartment buyers fail to attend to energy when no rating is shown. Energy may be bundled into service charges; apartment buyers, often moving from rented housing in which heating was included, may have no habit of pricing it; or decisions in fast urban markets may leave little room to ask. Whichever applies, the implication for prices is the same, and so is the estimate.
```

## 04-attention-draft:L44-45 (lines 44-45): CLEAN
- words 118 -> 115; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,2 +1,2 @@
 Three features of the French setting make this behaviour plausible for apartment buyers in particular. First, a listing that discloses shows the rating as a coloured label and, from January 2022, an estimate of the annual energy bill in euros, so disclosure itself puts energy into the buyer's comparison of dwellings.\footnote{Since 1 January 2022, advertisements for the sale of a dwelling must state the estimated annual energy expenditure for standard use, with the reference year of energy prices, and dwellings rated F or G must carry the mention ``logement \`a consommation \'energ\'etique excessive''. Omitting these mentions exposes the advertiser to fines under Article L126-33 of the Code de la construction et de l'habitation. % [CHECK] cite the implementing decree (D\'ecret n\textsuperscript{o} 2020-1609, 17 Dec.\ 2020) against L\'egifrance before submission.
-The obligation also gives a dated test of the mechanism: under limited attention the gap between silent and rated listings should widen again at that date.} A listing that shows nothing does not. Second, heating in many apartment buildings is collective and paid through service charges, so apartment buyers are likely to see energy as part of a monthly charge rather than as an attribute of the dwelling. Third, a missing rating is common: about \attShareUninfApt{} percent of silent apartment listings match no post-reform certificate in the registry. Silence is therefore unremarkable rather than conspicuous.
+The obligation also gives a dated test of the mechanism: under limited attention the gap between silent and rated listings should widen again at that date.} A listing that shows nothing does not. Second, heating in many apartment buildings is collective and paid through service charges, so apartment buyers are likely to see energy as part of a monthly charge rather than as an attribute of the dwelling. Third, a missing rating is common: about \attShareUninfApt{} percent of silent apartment listings match no post-reform certificate in the registry. Silence is therefore unremarkable.
```

## 04-attention-draft:L21-22#fn1 (lines 21-22): UNCHANGED
- words 72 -> 72; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L24-24 (lines 24-24): UNCHANGED
- words 22 -> 22; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L26-35 (lines 26-35): UNCHANGED
- words 87 -> 87; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L44-45#fn1 (lines 44-45): UNCHANGED
- words 87 -> 87; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L47-47 (lines 47-47): UNCHANGED
- words 143 -> 143; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L52-52 (lines 52-52): UNCHANGED
- words 64 -> 64; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L54-61 (lines 54-61): UNCHANGED
- words 104 -> 104; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L63-64 (lines 63-64): UNCHANGED
- words 40 -> 40; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L66-67 (lines 66-67): UNCHANGED
- words 147 -> 147; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L69-69 (lines 69-69): UNCHANGED
- words 75 -> 75; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L74-74 (lines 74-74): UNCHANGED
- words 21 -> 21; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L91-91 (lines 91-91): UNCHANGED
- words 113 -> 113; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L117-117 (lines 117-117): UNCHANGED
- words 54 -> 54; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L134-138 (lines 134-138): UNCHANGED
- words 30 -> 30; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L140-140 (lines 140-140): UNCHANGED
- words 18 -> 18; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L145-145 (lines 145-145): UNCHANGED
- words 47 -> 47; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L147-147 (lines 147-147): UNCHANGED
- words 42 -> 42; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L161-161 (lines 161-161): UNCHANGED
- words 89 -> 89; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L163-164 (lines 163-164): UNCHANGED
- words 74 -> 74; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L166-166 (lines 166-166): UNCHANGED
- words 61 -> 61; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L173-173 (lines 173-173): UNCHANGED
- words 79 -> 79; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L175-175 (lines 175-175): UNCHANGED
- words 84 -> 84; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L185-185 (lines 185-185): UNCHANGED
- words 129 -> 129; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L192-192 (lines 192-192): UNCHANGED
- words 9 -> 9; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L194-194 (lines 194-194): UNCHANGED
- words 59 -> 59; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L199-200 (lines 199-200): UNCHANGED
- words 30 -> 30; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L205-205 (lines 205-205): UNCHANGED
- words 19 -> 19; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L210-210 (lines 210-210): UNCHANGED
- words 42 -> 42; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L225-225#fn1 (lines 225-225): UNCHANGED
- words 74 -> 74; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L234-234 (lines 234-234): UNCHANGED
- words 61 -> 61; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L236-237 (lines 236-237): UNCHANGED
- words 11 -> 11; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L242-242 (lines 242-242): UNCHANGED
- words 11 -> 11; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L276-280 (lines 276-280): UNCHANGED
- words 17 -> 17; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L332-336 (lines 332-336): UNCHANGED
- words 94 -> 94; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L348-348 (lines 348-348): UNCHANGED
- words 43 -> 43; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L355-355 (lines 355-355): UNCHANGED
- words 9 -> 9; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L357-357 (lines 357-357): UNCHANGED
- words 176 -> 176; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L359-360 (lines 359-360): UNCHANGED
- words 19 -> 19; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L373-373 (lines 373-373): UNCHANGED
- words 138 -> 138; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L378-379 (lines 378-379): UNCHANGED
- words 83 -> 83; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L384-384 (lines 384-384): UNCHANGED
- words 76 -> 76; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L389-389 (lines 389-389): UNCHANGED
- words 95 -> 95; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L408-408 (lines 408-408): UNCHANGED
- words 148 -> 148; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L408-408#fn1 (lines 408-408): UNCHANGED
- words 73 -> 73; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L410-410 (lines 410-410): UNCHANGED
- words 72 -> 72; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L410-410#fn1 (lines 410-410): UNCHANGED
- words 49 -> 49; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L415-415 (lines 415-415): UNCHANGED
- words 176 -> 176; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L415-415#fn1 (lines 415-415): UNCHANGED
- words 44 -> 44; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L424-428 (lines 424-428): UNCHANGED
- words 190 -> 190; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L431-431 (lines 431-431): UNCHANGED
- words 24 -> 24; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L433-442 (lines 433-442): UNCHANGED
- words 73 -> 73; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L450-459 (lines 450-459): UNCHANGED
- words 83 -> 83; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L461-461 (lines 461-461): UNCHANGED
- words 75 -> 75; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L465-466 (lines 465-466): UNCHANGED
- words 107 -> 107; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L465-466#fn1 (lines 465-466): UNCHANGED
- words 46 -> 46; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L468-468 (lines 468-468): UNCHANGED
- words 35 -> 35; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 04-attention-draft:L470-470 (lines 470-470): UNCHANGED
- words 8 -> 8; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n
