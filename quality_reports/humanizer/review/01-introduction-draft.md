# Approval sheet: 01-introduction-draft

Riskiest first. Decide each unit: accept / reject / edit. Nothing is applied before a decision.

## 01-introduction-draft:L11-20 (lines 11-20): REVIEW-FLAGS
- words 101 -> 92; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 6->4
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,10 +1,9 @@
 % ---------- ¶1  puzzle, then the theoretical benchmark ----------
 Mandatory disclosure is the standard regulatory response to asymmetric information about
-product quality. Yet the case for mandating disclosure is contested, because theory suggests
-markets may not need it. When quality is verifiable, the unraveling result of
-\citet{grossman_informational_1981} and \citet{milgrom_good_1981} holds that sellers disclose
+product quality, yet theory suggests markets may not need it. When quality is verifiable, the
+unraveling result of \citet{grossman_informational_1981} and \citet{milgrom_good_1981} holds that sellers disclose
 voluntarily, since buyers rationally read silence as the worst possible news. All but the very
 worst sellers therefore disclose, and disclosure becomes effectively universal without a
-mandate. Whether this result describes real markets remains unsettled. It rests on strong
-assumptions, and it is difficult to test, because in most settings where quality is verifiable
+mandate. Whether this result describes real markets remains unsettled: it rests on strong
+assumptions and is difficult to test, because in most settings where quality is verifiable
 disclosure has long been compulsory.
```

## 01-introduction-draft:L22-39 (lines 22-39): REVIEW-FLAGS
- words 127 -> 119; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 0->1; G5 flags: sentences 5->6; new words: also, not
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -14,5 +14,4 @@
 it, and buyers acquired legal recourse against misstatement. The reform changed what a disclosed
 score means without changing the underlying housing stock or the legal consequences of remaining
-silent. It therefore isolates the demand-side value of the signal, and it does so in a market
-where the certificate is issued and archived by a national agency rather than by the seller or
-the listing platform.
+silent. It therefore isolates the demand-side value of the signal. The certificate is also issued
+and archived by a national agency, not by the seller or the listing platform.
```

## 01-introduction-draft:L41-50 (lines 41-50): REVIEW-FLAGS
- words 119 -> 119; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: number_word:three 0->1; G5 flags: sentences 3->7; new words: reasons, three
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,10 +1,10 @@
 % ---------- ¶3  what theory predicts here, and why this market adjudicates ----------
 Applied to this setting, unraveling makes a sharp prediction. Once the DPE is credible, sellers
-of energy-efficient properties should publish their score to separate themselves; sellers of
-mediocre properties should then publish to avoid being pooled with worse ones; and the process
+of energy-efficient properties should publish their score to separate themselves, and sellers of
+mediocre properties should then publish to avoid being pooled with worse ones. The process
 should continue until listings without a score are confined to the very bottom of the quality
 distribution, priced at or below the worst disclosed grade. French housing is a suitable
-testbed for this prediction because the disclosed attribute is a single certified index with a
-clear mapping into a running cost buyers face directly, because the certificate is verifiable
-against an independent public registry, and because a large stock of properties entered the
+testbed for this prediction for three reasons. The disclosed attribute is a single certified index with a
+clear mapping into a running cost buyers face directly. The certificate is verifiable
+against an independent public registry. And a large stock of properties entered the
 post-reform market without one.
```

## 01-introduction-draft:L52-68 (lines 52-68): REVIEW-FLAGS
- words 203 -> 201; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 7->8
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -6,5 +6,5 @@
 construction after July~2021, since the DPE is issued by a certified third-party diagnostician,
 archived in the registry of the \emph{Agence de la Transition \'Ecologique} (ADEME), and legally
-binding on the seller. Assumption~(b) is close to satisfied, because a DPE is a one-off outlay of
+binding on the seller. Assumption~(b) is close to satisfied: a DPE is a one-off outlay of
 roughly 100--250~\euro{} according to ADEME's own estimates, negligible relative to
 residential transaction values, and it is the seller's obligation rather than the buyer's.
@@ -14,4 +14,4 @@
 match at the address level, 48.8\% hold none.
 Silence in this market is therefore not always a choice, a possibility first identified by
-\citet{dye_disclosure_1985} and formalised by \citet{jung_kwon_1988}, and here it is measured
+\citet{dye_disclosure_1985} and formalised by \citet{jung_kwon_1988}. Here it is measured
 rather than inferred.
```

## 01-introduction-draft:L70-84 (lines 70-84): REVIEW-FLAGS
- words 169 -> 168; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: new words: describes, whether
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,5 +1,5 @@
 % ---------- ¶5  isolate the assumption at stake ----------
-The descriptiveness of unraveling in this market accordingly hinges on assumption~(d).
-Unlike disclosure costs and disclosure credibility, which a large literature has examined,
+Whether unraveling describes this market therefore hinges on assumption~(d).
+Disclosure costs and disclosure credibility have been examined in a large literature, but
 the homogeneity of buyer valuations has received little attention, even though it sets the size of
 the disclosure incentive. A seller's penalty for withholding is proportional to the share of
```

## 01-introduction-draft:L114-134 (lines 114-134): REVIEW-FLAGS
- words 229 -> 226; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 0->1; G5 flags: new words: not
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -9,6 +9,5 @@
 apartments and $+0.008$ for houses with no discernible drift, and then shift sharply upward,
 stabilising around $+0.044$ and $+0.037$ by mid-2024. For apartments the level ordering already
-favoured non-disclosers beforehand, so what the reform changes is the magnitude of the premium
-rather than its sign. Third, turning to the address-matched listing sample, non-disclosure is
+favoured non-disclosers beforehand, so the reform changes the magnitude of the premium, not its sign. Third, turning to the address-matched listing sample, non-disclosure is
 overwhelmingly involuntary. Among apartment listings 79.8\% disclose truthfully, 16.7\% are
 genuinely uninformed, and only 3.5\% hold a certificate and withhold it, with the corresponding
```

## 01-introduction-draft:L177-186 (lines 177-186): REVIEW-FLAGS
- words 122 -> 109; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 1->0; G5 flags: new words: reflects, theory's
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -6,5 +6,5 @@
 treat sellers' information as latent. By observing it directly we can decompose silence into
 inability and choice, and show that the first dominates the second by an order of magnitude
-while the second is what sustains the price premium. The finding that silence is rewarded rather
-than punished is not a failure of the theory so much as a demonstration of how sensitive its
-central prediction is to an assumption that is rarely examined.
+while the second is what sustains the price premium. That silence is rewarded rather
+than punished reflects how sensitive the theory's central prediction is to an assumption that
+is rarely examined.
```

## 01-introduction-draft:L221-238 (lines 221-238): REVIEW-FLAGS
- words 180 -> 180; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: new words: consistent
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -10,5 +10,5 @@
 disclosed and undisclosed information is priced \citep{hirshleifer_limited_2003, dellavigna_investor_2009}.
 It is closely related to the extensive evidence on the capitalisation of energy labels in
-housing, which documents robust premia for efficient properties wherever labels have been
+housing, which documents consistent premia for efficient properties wherever labels have been
 studied \citep{brounen_kok_2011, hyland_lyons_2013, fuerst_energy_2016, frondel_power_2018,
 myers_mandatory_2022}; that literature establishes that labels are priced, whereas our question
```

## 01-introduction-draft:L240-251 (lines 240-251): REVIEW-FLAGS
- words 134 -> 131; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 1->0; G5 flags: new words: beyond, extends
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -3,5 +3,5 @@
 single mandate, in one country, covering one verifiable attribute, and the low audit coverage
 that lets us separate inability from choice is itself a feature of a young disclosure regime.
-The mechanism, however, is not specific to energy labels. Wherever a disclosure mandate is
+The mechanism extends beyond energy labels. Wherever a disclosure mandate is
 introduced before the infrastructure that makes disclosure feasible is universal, a pool of
 genuinely uninformed non-disclosers will exist, and that pool will shelter strategic
```

## 01-introduction-draft:L86-112 (lines 86-112): CLEAN
- words 321 -> 320; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: unclassified (bulk accept); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -16,9 +16,9 @@
 thing buyers can never observe. Because the match requires a geocoded address, the matched
 sample is the subset of listings that can be located at the address level rather than the full
-listing universe. Within that matched sample, every listing falls into one of four groups, namely
-truthful disclosers, strategic hiders who hold a certificate and omit it, genuinely uninformed
+listing universe. Within that matched sample, every listing falls into one of four groups: truthful
+disclosers, strategic hiders who hold a certificate and omit it, genuinely uninformed
 sellers for whom no certificate exists, and a small residual displaying a score without a
 verified audit. The information structure of the disclosure game is therefore observed rather
-than inferred, a vantage point that to our knowledge is unique in this literature. Transaction
+than inferred, a vantage point that, to our knowledge, is unique in this literature. Transaction
 records enter separately and are not matched to individual listings. We use them to estimate
 the mapping from listing to realised sale price, which supports treating the listing price as
```

## 01-introduction-draft:L22-39#fn1 (lines 22-39): UNCHANGED
- words 84 -> 84; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n

## 01-introduction-draft:L136-147 (lines 136-147): UNCHANGED
- words 163 -> 163; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: pending; applied: n
