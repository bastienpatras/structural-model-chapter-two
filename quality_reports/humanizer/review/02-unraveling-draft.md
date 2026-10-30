# Approval sheet: 02-unraveling-draft

Riskiest first. Decide each unit: accept / reject / edit. Nothing is applied before a decision.

## 02-unraveling-draft:L17-23 (lines 17-23): REVIEW-FLAGS
- words 92 -> 85; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 5->4
- change type: cosmetic; decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -3,5 +3,5 @@
 what they expect to receive on average. Sellers of genuinely good products are then underpaid,
 and may withdraw from the market altogether, leaving buyers facing a pool of worse quality than
-they had hoped for \citep{akerlof_lemons_1970}. The outcome is bad for both sides. Buyers pay for
+they had hoped for \citep{akerlof_lemons_1970}. Buyers pay for
 uncertainty they would rather not bear, and the best sellers cannot capture the value of what
 they own.
```

## 02-unraveling-draft:L25-37 (lines 25-37): REVIEW-FLAGS
- words 182 -> 183; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 11->10
- change type: cosmetic; decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -5,5 +5,5 @@
 this, understand that any seller who remains silent is not of the highest quality, and revise
 downward what they will pay for silence. That revision gives the second-highest-quality seller
-the same incentive, and disclosing becomes worthwhile for them too. The argument repeats. Each
+the same incentive, and disclosing becomes worthwhile for them too. The argument repeats, and each
 round of disclosure worsens the expected quality of the remaining silent pool, which strengthens
 the incentive for the best of those who remain to separate themselves. The process continues
```

## 02-unraveling-draft:L39-48 (lines 39-48): REVIEW-FLAGS
- words 128 -> 120; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 2->1; G5 flags: sentences 6->5
- change type: content-risk (mild); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,3 +1,3 @@
-The argument is powerful but it is not free. It rests on four assumptions. First, (a)~buyers know
+The argument rests on four assumptions. First, (a)~buyers know
 that sellers possess private information about quality; if a seller may simply not know, silence
 no longer implies unwillingness to reveal. Second, (b)~disclosure is costless, or at least cheap
```

## 02-unraveling-draft:L50-55 (lines 50-55): REVIEW-FLAGS
- words 78 -> 71; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: sentences 4->3; new words: although, avoid, discloses
- change type: content-risk (mild); decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,6 +1,6 @@
-The first three assumptions have received sustained attention. The fourth has not, even though
-it governs the strength of the entire mechanism. What drives a seller to disclose is the revenue
+The first three assumptions have received sustained attention; the fourth has not, although
+it governs the strength of the entire mechanism. A seller discloses to avoid the revenue
 lost when buyers price silence pessimistically, and that loss is proportional to the share of
-buyers who care about the attribute in the first place. Whether unraveling describes any
+buyers who care about the attribute. Whether unraveling describes any
 particular market is therefore an empirical question, and answering it requires knowing which of
 these assumptions fails there.
```

## 02-unraveling-draft:L62-70 (lines 62-70): REVIEW-FLAGS
- words 112 -> 111; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 2->1; G5 flags: new words: instead
- change type: cosmetic; decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -7,3 +7,3 @@
 resulting equilibria and showed that partial pooling, in which some informed sellers of poor
 quality withhold while the uninformed are silent by necessity, is generically stable. Disclosure
-does not unravel to the bottom; it stops somewhere in the interior.
+stops somewhere in the interior instead of unraveling to the bottom.
```

## 02-unraveling-draft:L80-90 (lines 80-90): REVIEW-FLAGS
- words 158 -> 146; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: negation:not 3->2; G5 flags: sentences 9->7; new words: beyond, goes
- change type: structural; decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,3 +1,3 @@
-The two departures do not merely coexist; they compound. A larger mass of sellers who cannot
+The two departures compound. A larger mass of sellers who cannot
 disclose dilutes the adverse inference buyers draw from silence, which raises the expected quality
 of the silent pool and makes withholding more attractive to informed sellers of poor quality.
@@ -5,7 +5,7 @@
 cannot separate them from the involuntarily silent. Meanwhile, a demand side in which many buyers
 do not price the attribute weakens the penalty that would otherwise discipline them. Put together,
-the consequence is stronger than persistence of non-disclosure. Silence can command a
+the consequence goes beyond persistence of non-disclosure. Silence can command a
 \emph{premium} over the worst disclosed quality, since the silent pool contains a substantial
 mass of sellers whose silence carries no adverse information at all. The sellers who cannot
-disclose do not intend to shelter anyone. Their presence is involuntary. But it is precisely what
-makes silence ambiguous, and ambiguity is what makes concealment privately rational.
+disclose do not intend to shelter anyone, but their involuntary presence makes silence ambiguous,
+and that ambiguity makes concealment privately rational.
```

## 02-unraveling-draft:L106-114 (lines 106-114): REVIEW-FLAGS
- words 135 -> 124; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: hedge:implies 2->1; number_word:two 3->2; G5 flags: sentences 6->4
- change type: structural; decision: accept; applied: y 2026-10-30

```diff
--- before
+++ after
@@ -1,7 +1,6 @@
-Two features of this taxonomy matter for what follows. It implies that the informational content
-of silence is a market-level object rather than a universal one, so that two markets facing the
-same disclosure mandate can sit in different cells and sustain opposite price patterns. And it
-implies that the two primitives are separately movable by policy. Investment in certification
-infrastructure raises the share of sellers holding verifiable information, while the
+The taxonomy implies that the informational content of silence is a market-level object rather than a
+universal one, so two markets facing the same disclosure mandate can sit in different cells and sustain
+opposite price patterns, and that the two primitives are separately movable by policy. Investment in
+certification infrastructure raises the share of sellers holding verifiable information, while the
 share of buyers who price the attribute responds to the legal weight the certificate carries and
 to the cost of the attribute itself. Which cell a given market occupies, however, cannot be
```

## 02-unraveling-draft:L59-60 (lines 59-60): UNCHANGED
- words 27 -> 27; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 02-unraveling-draft:L72-78 (lines 72-78): UNCHANGED
- words 92 -> 92; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n

## 02-unraveling-draft:L92-97 (lines 92-97): UNCHANGED
- words 79 -> 79; gates G1/G2/G3/G7: True/True/True/True
- G4 flags: none; G5 flags: none
- change type: (unclassified); decision: n/a (unchanged); applied: n
