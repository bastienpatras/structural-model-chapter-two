# Domain Referee Report — `/review-paper --peer TOPFIN`

**Calibrated to:** Top Finance Journal — composite (TOPFIN)
**Disposition:** SKEPTIC
**Critical peeve:** Comparability of the compared groups is asserted rather than shown — no table establishing that the units being compared are alike on pre-existing characteristics.
**Constructive peeve:** Appreciates when the paper anticipates the obvious referee objections.
**Date:** 2026-09-14
**Paper:** `paper-real-estate/main.tex` (+ `sections/01`–`04`, `sections/A-robustness.tex`)

## Executive verdict

**Score:** 68/100
**Recommendation:** Major Revision
**Headline:** The paper's headline object — a 6.9%/3.4% non-disclosure *premium* — is a difference-in-differences *change* in a price gap between two groups the paper never shows to be comparable, one of which is hit by a rental ban on the same date by the same statute; and the structural layer built on it reports a boundary-saturated parameter and a rejected corollary as if both were results.

## Dimension scores (TOPFIN weights as given)

| # | Dimension | Weight | Score | Weighted |
|---|---|---|---|---|
| 1 | Contribution & Novelty | 30% | 68/100 | 20.4 |
| 2 | Literature Positioning | 20% | 78/100 | 15.6 |
| 3 | Substantive Arguments | 20% | 52/100 | 10.4 |
| 4 | External Validity | 10% | 76/100 | 7.6 |
| 5 | Fit for TOPFIN | 20% | 70/100 | 14.0 |
| | **Composite** | | | **68.0/100** |

---

## Major concerns

### Concern 1: The compared groups are never shown to be alike, and the paper concedes they are not

**Dimension:** 3 (Substantive Arguments) · **Severity:** MAJOR

Treatment is "listings with no disclosed score"; control is "listings disclosing E/F/G." §3.3.1 states that for apartments, non-disclosers "occupy the highest price tier across the *entire* sample window," with the ordering visible in 2019, and attributes this to "the concentration of non-audited stock in high-price urban markets." That concession is doing a great deal of work and is unaccompanied by any evidence. There is no table anywhere in the manuscript comparing the two groups on area, rooms, floor, construction era, urbanicity, market composition, or listing volume in the pre-period. The claim that the hedonic indices "purge observable composition differences" is an assertion about a procedure taken from `patras_mandatory_2024`; a referee cannot check a balance claim by reading a citation.

The paper's defense is that the DiD normalization makes levels irrelevant. That defense is only as good as parallel trends, and parallel trends between two groups that differ systematically in *where they are located* and *what kind of stock they are* is precisely the assumption a reader needs help believing. Two flat pre-trend series averaging +0.002 and +0.008 log points, reported without standard errors, dispersion across markets, or a joint pre-trend test statistic, is thin support for it — especially when the paper elsewhere (§3.3.2) documents that the two segments' non-disclosure rates were themselves trending differently (houses 24.6% pre, 14.4% post; apartments 35.9% pre, 33.8% post).

**Why this matters:** If the two groups differ on a pre-existing characteristic whose price trajectory changed after 2021 — urban density, small-unit stock, investor exposure — the "premium" is a composition effect wearing an information-economics label, and the entire structural layer inverts a number that does not mean what the model says it means.

> **What would change my mind:** A pre-period balance table at the listing level comparing non-disclosers to disclosed E/F/G on the full hedonic vector plus market-level covariates (price per m², urbanicity, listing volume, share of pre-1975 stock), with normalized differences; plus the underlying event-study coefficients with market-clustered standard errors and a joint pre-trend F-test reported in the text rather than a qualitative "statistically flat."

### Concern 2: The control group is directly treated by the same statute on the same date

**Dimension:** 3 · **Severity:** MAJOR

§2 of *loi Climat et Résilience* — the same law that made the DPE opposable — imposes a phased rental prohibition on dwellings rated E, F, and G. The paper says so twice (§3.1, §4.1), and uses that threshold as the institutional anchor for its binary quality space. It then makes E/F/G listings the control group in a DiD. The most obvious alternative explanation for a widening gap between non-disclosers and E/F/G listings after July 2021 is therefore not strategic concealment at all: it is that E/F/G properties were devalued by an announced prohibition on letting them.

This objection is nowhere addressed. Concern 5 of the "competing explanation" discussion in §4.1 disposes only of a *supply-side composition* story, not of a contemporaneous *demand* shock to the control group. Note that the alternative predicts exactly the observed joint pattern the paper reads as corroborating: β̂₁ (efficient minus intensive) and Δ̂ (non-disclosed minus intensive) both jump at the same date in the same markets, because both have the same, newly penalized, denominator group.

**Why this matters:** If the rental ban explains the movement, the paper's non-disclosure premium is a mislabeled E/F/G discount, ĉ₀ is meaningless, and the policy section is computing subsidies off an artifact.

> **What would change my mind:** Re-estimate the non-disclosure premium against a control group not subject to the letting ban — e.g. disclosed D-rated listings, or the full disclosed distribution reweighted to the non-disclosers' hedonic profile. If the premium survives against a D-only control, the rental-ban story is dead. Alternatively, exploit the phased ban's own timing (G from 2025, F from 2028) to show the gap moves with the DPE opposability date rather than with ban-phase announcements.

### Concern 3: Group membership is re-sorted by the treatment

**Dimension:** 3 · **Severity:** MAJOR

Both the treatment and control groups are defined by an endogenous seller choice that the reform itself changes. §3.2 reports that verified disclosers rose from 7.4% to roughly one half of apartment listings between 2021Q3 and 2024Q4, and that the "displays a score, no registry record" group fell from 62.5% to 18.4%. §3.3.2 reports the non-disclosure share falling from 35.9% to 28.9% (apartments) and 24.6% to 9.7% (houses). A DiD comparing group means when roughly a fifth of one group exits into the other over the post-window is comparing different populations before and after, and hedonic controls absorb only the observable part of that re-sorting — the part the model says is *not* what drives selection into silence.

The direction is not obviously favorable. If the marginal exiters from the silent pool are the best of the uninformed (those who found it cheapest to get audited), the residual silent pool worsens and the measured premium *understates*; if they are the worst, it overstates. The paper does not sign this.

**Why this matters:** The paper's own mechanism implies compositional change in the treated group is endogenous to the treatment, which is the textbook condition under which a group-level DiD is not a causal contrast.

> **What would change my mind:** A cohort-stable version of the estimate — restrict to a fixed panel of local markets and a fixed hedonic reference property, and show Δ̂ is unchanged; plus a decomposition showing how much of the post-period change in the non-disclosure index is attributable to compositional shift versus within-composition repricing (a Oaxaca- or DFL-style reweighting to the pre-period non-discloser distribution would do it).

### Concern 4: The abstract's headline number is a change, reported as a level

**Dimension:** 1, 3 · **Severity:** MAJOR

The abstract and conclusion both state that non-disclosing properties "trade at a premium of 6.9 percent above disclosed low-efficiency properties." §4.5.1 says what Δ̂ actually is: how much more non-disclosers earn "compared with the pre-reform baseline." Those are different objects, and the gap between them is exactly the pre-existing level difference Concern 1 is about. For houses the distinction is fatal to the sentence as written — §3.3.1 says house non-disclosers "begin near the bottom of the price distribution and rise toward the middle," so a house non-discloser may well still trade *below* a disclosed E/F/G listing in levels while the paper's abstract claims a 3.4% premium over it.

Relatedly, §3.3.1 reports the apartment DiD stabilizing "around +0.044" by mid-2024 while Table 4 reports Δ̂ = 6.9%. A period-mean that exceeds the terminal value of a monotonically rising event-study path needs an explanation the paper does not give.

**Why this matters:** The paper's entire framing — "we document the opposite" of unraveling — is a statement about levels. It cannot be supported by an estimate of a change without also reporting the level.

> **What would change my mind:** Report the post-reform *level* gap between non-disclosers and disclosed E/F/G, hedonic-adjusted, for both segments, with its standard error; then state the abstract's claim in whichever object it is actually true. If the level premium is negative for houses, say so.

### Concern 5: The key structural parameter is at the boundary in every apartment market, and the estimator may be an identity

**Dimension:** 1, 3 · **Severity:** MAJOR

§4.3.2 reports that ρ̂ = Δ̂/(β̂₁·ê*) exceeds unity in **all 40** apartment markets, with an unconstrained cross-market mean of **7.7**, and is then clipped to 1. The paper calls this "boundary saturation" and a "structural feature of the data." A skeptic calls it the model's one cross-equation restriction failing by nearly an order of magnitude in 100% of the lead segment. A structural model whose overidentifying content is rejected everywhere it is tested, and which is then rescued by imposing the parameter at its bound, has not been validated — and the paper nonetheless narrates ρ̂ = 90.9% in the abstract, intro, results, and conclusion as a finding ("nearly all buyers in the average market price energy performance").

There is a second, sharper possibility the paper never rules out. The model's price gap between *disclosed* high and low quality is a market-level price object and should therefore carry the same ρ weighting as the non-disclosure premium does in Table 3 (where the CDH premium is ρβ₁θ̄). But the empirical β̂₁ is defined in §4.3.3 as an observed index gap p̄ᴴ − p̄ᴸ. If that observed gap equals ρβ₁ rather than the structural β₁, then Δ̂/(β̂₁·ê*) ≡ 1 by construction, and the estimator is uninformative about ρ by algebra rather than by data limitation. That would explain the saturation perfectly, and it would mean the paper has no estimate of buyer sensitivity at all.

**Why this matters:** ρ̂ is one of two headline structural magnitudes and enters ĉ₀ multiplicatively; if it is an identity or a bound, the paper's claim to have *measured* buyer heterogeneity — the assumption it says the literature has neglected — collapses to an assumption.

> **What would change my mind:** An explicit derivation showing what the observed disclosed-high-minus-disclosed-low price gap equals *in the model's own notation* (β₁, or ρβ₁, or something else), and a demonstration that ρ appears in the numerator of eq. (36) but not the denominator. If ρ does appear in both, withdraw the ρ̂ point estimates and present the paper as identifying ĉ₀ under a maintained ρ = 1 throughout. Separately: report the distribution of the unconstrained ratio, not just its mean, and state what fraction of markets are within sampling error of 1 versus grossly above it.

### Concern 6: The model's one falsifiable prediction is rejected by the paper's own appendix and reported as support

**Dimension:** 3 · **Severity:** MAJOR

Corollary 2 states σ₁* = 0 "in any equilibrium" — informed high-quality sellers never conceal. Table A.1, reading the withheld grade from the registry, gives σ̂₁ = 5.1% against σ̂₀ = 5.5% for apartments, and 2.1% against 2.2% for houses. Those are not "the model's predicted ordering holds"; those are informed high- and low-quality sellers hiding at statistically indistinguishable rates, with no standard errors reported and a gap of 0.4 and 0.1 percentage points. Under the A–C cut the ordering **reverses in both segments**. The appendix text then reads the reversal as evidence *for* the baseline threshold — which is selecting the specification on the outcome of the test it is supposed to pass.

The same table shows the concealment cost itself is not robust in level: 3.4–4.6% under one cut, 1.6–1.8% under the other, a factor of roughly 2.5 on the paper's central structural magnitude, driven entirely by an analyst choice of where to put a letter grade boundary.

**Why this matters:** The paper's claim that its estimate identifies a structural concealment cost rests on a sorting result the data do not support, and the magnitude readers will quote is a specification choice.

> **What would change my mind:** Standard errors (or a bootstrap) on σ̂₁ and σ̂₀ and an explicit test of σ₁ = 0 and of σ₁ < σ₀; a stated, pre-committed reason for the D/E cut that does not reference which cut passes the test; and either a defense of one ĉ₀ level or a consistent presentation of the range 1.6–4.6% throughout the abstract, results, conclusion, and policy section.

---

## Minor suggestions

- **Numeric integrity is poor enough to affect credibility.** Market counts are irreconcilable: §4.3.2 says 40 apartment / 100 house markets survive the volume filter; §4.4 says 45 and 97; Table 4's columns say N = 49 and 104 while its own notes say N = 43 and 107; §4.3.2 says "point identification is achieved in 8 house markets" while §4.5.2 says 22; §4.5.2 reports 3 full-unravelling apartment markets while §5 reports 2 CDH apartment markets, and 21 versus 25 for houses. The informed-share statistic appears as 51.2%/40.3% (§3.2), 50.7%/41.9% (Table 4), and 51.8%/41.7% (Conclusion). §3.2 states the market-level σ̂₀ "reported in the results" are 7.7% and 3.7%; the results table reports 14.0% and 5.7%. Programme cost is €15.5bn in §5 and €14.6bn in the Conclusion. Fix all of these before resubmission; a referee who catches four of them stops checking and starts doubting.
- The Conclusion contains a corrupted sentence: "5.7\% of house sellers do.7\% of house sellers do so."
- The €165/m² mean apartment renovation threshold implies an apartment price near €9,700/m² given β̂₁ = 1.7%; state the price base used so the reader can check the arithmetic.
- The "Disclosed, unmatched" cell (32.2% of apartment and 51.2% of house listings) is assigned to truthful disclosers by assumption. That is more than half the house sample resting on a classification rule. Report the estimates with this group dropped.
- §5's aggregate fiscal numbers (€15.5–38.7bn) are presented as "the headline fiscal fact" and then walked back to "order-of-magnitude upper bounds" in the same paragraph. Pick one register.
- Remark (welfare) is honest and belongs earlier — ideally before the maps, not after.

## Positive observations

1. **The paper anticipates several of the objections a referee would raise, and does so in the main text rather than in a buried footnote.** §3.2's discussion of the K = 0 coverage gap does the hard thing: it names the measurement failure, signs the resulting bias, and shows that the sign works *against* the paper's preferred magnitude. §4.1's closing paragraph enumerates what the model does not settle, including that σ₁ = 0 is maintained rather than tested. §4.3.1's footnote reports a failed Bartik first stage (F between 1.0 and 1.6) and explains institutionally why it failed. This is the right instinct and it earns real credit — my objections above are that in three places (the σ₁ test, the ρ̂ boundary, the abstract's framing) the anticipation stops one step short of following its own logic to the conclusion.
2. **The data asset is genuinely new and the identification advantage is correctly stated.** Observing information status K directly from an administrative registry rather than inferring it is exactly the thing the Dye/Jung-Kwon literature has never had, and the paper is precise about what the match does and does not deliver.
3. **The partial-pooling invariance result is a real theoretical payoff**, not decoration: that the premium collapses to c₀ independent of π and ρ is what makes the structural exercise more than a relabeling, and the Lemma 1 cancellation of c₀ from the renovation threshold is a genuinely non-obvious policy implication. It is worth defending properly.
