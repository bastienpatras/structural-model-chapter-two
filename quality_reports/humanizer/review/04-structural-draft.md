# Approval sheet: 04-structural-draft

Riskiest first. Decide each unit: accept / reject / edit. Nothing is applied before a decision.

## 04-structural-draft:L27-30 (lines 27-30): REVIEW-FLAGS
- words 46 -> 41; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 1->0; G5 flags: sentences 3->2; new words: allows
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,4 +1,3 @@
-We allow for, but do not impose, strategic concealment. Nothing in the specification requires
-informed sellers to withhold. The hiding rate is an equilibrium object, the model admits full
-unravelling as a special case, and whether concealment occurs, and how much, is what the
-estimation determines.
+The specification allows for strategic concealment and nothing in it requires informed sellers to
+withhold. The hiding rate is an equilibrium object, the model admits full unravelling as a special
+case, and the estimation determines whether concealment occurs and how much.
```

## 04-structural-draft:L32-39 (lines 32-39): REVIEW-FLAGS
- words 111 -> 103; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 5->3; new words: carries
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,7 +1,6 @@
-Two considerations motivate this structure. The first is resemblance. The facts in
+Two considerations motivate this structure. First, the facts in
 Section~\ref{sec:facts} line up with the Dye--Jung-Kwon configuration, in which a silent pool is
 overwhelmingly silent by constraint rather than by choice, a small but non-trivial mass of
-informed sellers who withhold, and a premium attached to silence rather than a penalty. The
-second is institutional. The binary quality space has an empirical anchor in the rental-ban
+informed sellers withhold, and silence carries a premium rather than a penalty. Second, the binary quality space has an empirical anchor in the rental-ban
 threshold introduced by \emph{loi Climat et R\'esilience}: dwellings rated E, F, or G face a
 progressive prohibition on new lettings, which draws a bright line between the bottom of the
```

## 04-structural-draft:L60-72 (lines 60-72): REVIEW-FLAGS
- words 180 -> 174; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:no 2->3; negation:not 4->2; hedge:about 1->0; number_word:several 0->1; G5 flags: new words: claim, leaves, make, several, things, unsettled
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,3 +1,3 @@
-Finally, we are explicit about what the model does not settle. It takes no stance on
+The model leaves several things unsettled. It takes no stance on
 \emph{why} an informed seller withholds, since deliberate concealment and an unrecorded but
 still-valid certificate are observationally similar in the listing data, and we do not
@@ -10,4 +10,3 @@
 buyer sensitivity but cannot establish how close to one it lies, and we maintain
 $\hat\rho_m = 1$ for those markets and treat $\hat c_{0,m}$ as an upper bound accordingly. We
-do not purport to estimate the one true model of housing disclosure; we propose one way of
-reading these data through a workhorse framework.
+propose one way of reading these data through a workhorse framework and make no claim to the one true model of housing disclosure.
```

## 04-structural-draft:L81-81 (lines 81-81): REVIEW-FLAGS
- words 103 -> 102; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 1->0; G5 flags: new words: deciding, pricing, rather
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-The seller simultaneously chooses a disclosure decision $d\in\{0,1\}$ and a listing price $p^{\text{list}}$. French property law requires that all mandatory diagnostic documents, including the DPE, be appended to the sales agreement at signing (loi ALUR, Article L271-4 CCH), so the disclosure decision and the listing price are set jointly at the time the property is placed on the market. This institutional timing motivates the simultaneous-choice formulation: the seller does not first decide whether to disclose and then price, but sets a complete strategy that internalizes how the disclosure decision shifts buyer beliefs and thereby affects both the probability of sale and the expected transaction price.
+The seller simultaneously chooses a disclosure decision $d\in\{0,1\}$ and a listing price $p^{\text{list}}$. French property law requires that all mandatory diagnostic documents, including the DPE, be appended to the sales agreement at signing (loi ALUR, Article L271-4 CCH), so the disclosure decision and the listing price are set jointly at the time the property is placed on the market. This institutional timing motivates the simultaneous-choice formulation: the seller sets a complete strategy that internalizes how the disclosure decision shifts buyer beliefs and thereby affects both the probability of sale and the expected transaction price, rather than first deciding whether to disclose and then pricing.
```

## 04-structural-draft:L108-108 (lines 108-108): REVIEW-FLAGS
- words 67 -> 62; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: number_word:two 1->0; G5 flags: sentences 4->3
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-$c_0$ serves two purposes here. It is an institutional cost of concealment, fixed within the prevailing enforcement regime, which we recover from the equilibrium price gap in Section~\ref{sec:identification}. It is also a policy object, a margin the regulator can shift through stricter enforcement, and Section~\ref{sec:policy} studies counterfactual variation in $c_0$ on that basis. Estimation reads $c_0$ off the current regime, while the policy exercise perturbs it around that same reading.
+$c_0$ is an institutional cost of concealment, fixed within the prevailing enforcement regime, which we recover from the equilibrium price gap in Section~\ref{sec:identification}. It is also a policy object, a margin the regulator can shift through stricter enforcement, and Section~\ref{sec:policy} studies counterfactual variation in $c_0$ on that basis. Estimation reads $c_0$ off the current regime, while the policy exercise perturbs it around that same reading.
```

## 04-structural-draft:L192-192 (lines 192-192): REVIEW-FLAGS
- words 65 -> 62; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: new words: drives, results
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-A seller's disclosure decision reduces to one comparison: does withholding the audit, priced off the market's pool belief $e$, fetch more than disclosing the true quality $\theta$ would? A low-quality seller ($\theta=0$) gains by pooling with uninformed sellers and capturing a share of their quality premium; a high-quality seller ($\theta=1$) loses, because pooling with low-quality hiders drags the belief $e$ below 1. That asymmetry is the source of everything that follows.
+A seller's disclosure decision reduces to one comparison: does withholding the audit, priced off the market's pool belief $e$, fetch more than disclosing the true quality $\theta$ would? A low-quality seller ($\theta=0$) gains by pooling with uninformed sellers and capturing a share of their quality premium; a high-quality seller ($\theta=1$) loses, because pooling with low-quality hiders drags the belief $e$ below 1. That asymmetry drives the results below.
```

## 04-structural-draft:L205-205 (lines 205-205): REVIEW-FLAGS
- words 116 -> 116; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: dashes --- 1->0, -- 1->0; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-Proposition~\ref{prop:premium} is the familiar adverse-selection asymmetry, worked out for this setting. A high-quality seller has nothing to gain from ambiguity. Disclosure reveals her type exactly; non-disclosure pools her with low-quality hiders, and since $e(\sigma_0^*)<1$ for any non-degenerate pool, that comparison always binds. A low-quality seller faces the opposite incentive --- concealment lets her price off $e(\sigma_0^*)$, which is strictly above her true quality of zero whenever any uninformed sellers are present, so the gain from pooling is strictly positive. The hiding cost $c_1>0$ that falls only on high-quality concealers reinforces this separation but is not what drives it under the benchmark $\alpha_k=\beta_k$: pool inference alone is enough to make high-quality sellers disclose, and $c_1$ only starts to matter once $\alpha_k<\beta_k$, the distrust-discount case.
+Proposition~\ref{prop:premium} is the familiar adverse-selection asymmetry, worked out for this setting. A high-quality seller has nothing to gain from ambiguity. Disclosure reveals her type exactly; non-disclosure pools her with low-quality hiders, and since $e(\sigma_0^*)<1$ for any non-degenerate pool, that comparison always binds. A low-quality seller faces the opposite incentive: concealment lets her price off $e(\sigma_0^*)$, which is strictly above her true quality of zero whenever any uninformed sellers are present, so the gain from pooling is strictly positive. The hiding cost $c_1>0$ that falls only on high-quality concealers reinforces this separation but is not what drives it under the benchmark $\alpha_k=\beta_k$: pool inference alone is enough to make high-quality sellers disclose, and $c_1$ only starts to matter once $\alpha_k<\beta_k$, the distrust-discount case.
```

## 04-structural-draft:L230-230 (lines 230-230): REVIEW-FLAGS
- words 62 -> 62; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: dashes --- 2->0, -- 2->0; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1 +1 @@
-$\Phi$ is strictly decreasing in $\sigma_0$ --- more concealment worsens the pool, which shrinks the gain from concealing further --- and this monotone feedback is what pins down a unique equilibrium without any need for refinements. The three regimes below follow from comparing $\Phi$ against zero at its two extremes: $\Phi(0)=\Delta(\bar{\theta})-c_0$, the net gain against the cleanest possible pool, and $\Phi(1)=\Delta(e(1))-c_0$, the net gain against the most contaminated one.
+$\Phi$ is strictly decreasing in $\sigma_0$ (more concealment worsens the pool, which shrinks the gain from concealing further), and this monotone feedback is what pins down a unique equilibrium without any need for refinements. The three regimes below follow from comparing $\Phi$ against zero at its two extremes: $\Phi(0)=\Delta(\bar{\theta})-c_0$, the net gain against the cleanest possible pool, and $\Phi(1)=\Delta(e(1))-c_0$, the net gain against the most contaminated one.
```

## 04-structural-draft:L50-58 (lines 50-58): CLEAN
- words 108 -> 106; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,3 +1,3 @@
-The mechanism itself is the one set out in Section~\ref{sec:unraveling}: sellers who cannot
+The mechanism is the one set out in Section~\ref{sec:unraveling}: sellers who cannot
 disclose dilute the adverse inference buyers draw from silence, which makes withholding
 attractive to informed sellers of poor quality, whose entry the buyer cannot separate from
@@ -5,5 +5,4 @@
 Figure~\ref{fig:equilibrium_outcomes}: incomplete registry coverage combined with positive
 buyer EPC-sensitivity. Even where the EPC-sensitive buyer share approaches one, as it does in
-most apartment markets after the reform, incomplete coverage alone sustains the premium, because
-so long as a non-trivial share of non-disclosers hold no certificate, buyers cannot fully
+most apartment markets after the reform, incomplete coverage alone sustains the premium: so long as a non-trivial share of non-disclosers hold no certificate, buyers cannot fully
 penalise silence. Full unravelling requires both conditions; France satisfies only one.
```

## 04-structural-draft:L15-25 (lines 15-25): UNCHANGED
- words 102 -> 102; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L41-48 (lines 41-48): UNCHANGED
- words 111 -> 111; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L79-79 (lines 79-79): UNCHANGED
- words 107 -> 107; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L83-83 (lines 83-83): UNCHANGED
- words 39 -> 39; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L85-86 (lines 85-86): UNCHANGED
- words 107 -> 107; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L88-88 (lines 88-88): UNCHANGED
- words 21 -> 21; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L99-99 (lines 99-99): UNCHANGED
- words 89 -> 89; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L99-99#fn1 (lines 99-99): UNCHANGED
- words 88 -> 88; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L104-104 (lines 104-104): UNCHANGED
- words 23 -> 23; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L106-106 (lines 106-106): UNCHANGED
- words 167 -> 167; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L112-112 (lines 112-112): UNCHANGED
- words 120 -> 120; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L114-114 (lines 114-114): UNCHANGED
- words 8 -> 8; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L121-121 (lines 121-121): UNCHANGED
- words 87 -> 87; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L126-126 (lines 126-126): UNCHANGED
- words 70 -> 70; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L130-130 (lines 130-130): UNCHANGED
- words 53 -> 53; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L134-134 (lines 134-134): UNCHANGED
- words 17 -> 17; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L140-140 (lines 140-140): UNCHANGED
- words 108 -> 108; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L142-142 (lines 142-142): UNCHANGED
- words 56 -> 56; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L164-168 (lines 164-168): UNCHANGED
- words 20 -> 20; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L172-172 (lines 172-172): UNCHANGED
- words 15 -> 15; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L178-178 (lines 178-178): UNCHANGED
- words 119 -> 119; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L214-214 (lines 214-214): UNCHANGED
- words 64 -> 64; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L216-216 (lines 216-216): UNCHANGED
- words 29 -> 29; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L221-221 (lines 221-221): UNCHANGED
- words 26 -> 26; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 04-structural-draft:L225-225 (lines 225-225): UNCHANGED
- words 29 -> 29; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n
