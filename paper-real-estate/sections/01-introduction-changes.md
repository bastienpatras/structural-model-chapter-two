# §1 Introduction — change log

Draft: `01-introduction-draft.tex`. Plan: `01-introduction-plan.md`.
9 paragraphs → 14. Classified by type, per the diagnostic protocol.

## Relocations — content moved, substance unchanged

| What | From | To |
|---|---|---|
| The data / vantage-point argument | old ¶6 | new ¶6, **near-verbatim** — strongest paragraph in the draft, deliberately left alone apart from removing the `$K$` notation |
| The four-groups classification | old ¶6 | new ¶6, unchanged |
| Dye / Jung–Kwon "silence is not always a choice" | old ¶3 | new ¶4, folded into assumption (a) |
| Buyer-heterogeneity argument + its three citations | old ¶4 | new ¶5 |
| Energy-label capitalisation literature | old ¶2 | new ¶13, strand 2 |
| Levitt–Syverson / Lizzeri | old ¶6 | new ¶13, strand 3 |
| Renovation opportunity-cost argument | old ¶7 | new ¶12 |
| Complementarity result + Gillingham–Palmer contrast | old ¶8 | new ¶12 |

## Reframings — same content, repositioned

1. **Assumption audit** (new ¶4). Old ¶3 and ¶4 each argued a separate departure from theory, in prose. Now enumerated (a)–(d), with three assumptions disposed of and **one** isolated. This is the structural core of the reframing.
2. **Assumption (a) recast as measurement, not assumption.** Previously the paper argued theoretically that non-disclosure need not be a choice. It now says: we do not assume this, we observe it — 48.8% of apartment sellers hold no certificate. Makes the data contribution load-bearing rather than decorative.
3. **Model introduced as permissive** (new ¶8): "allows for, but does not impose, strategic concealment."
4. **σ̂₁ = 0 promoted to lead the findings** (new ¶9), and framed as a *specification test* — model-implied, never used in estimation, could have been rejected. Per your confirmation.
5. **Old ¶5 split.** It ran ~500 words across four jobs; now ¶8 (model motivation) and ¶9 (findings).
6. **Invariance result demoted** from a headline claim to the last sentence of ¶9, where it functions as the reason identification works rather than as a standalone contribution.

## Additions — new material; please verify factual accuracy

1. **¶2, the institutional paragraph.** Assembled from §5.1/§6.1 material. Verify: that *loi Climat et Résilience* is the correct instrument, that "legally opposable" is the right characterisation, and that buyer recourse against misstatement is accurate.
2. **¶4, assumption (b).** Uses your ADEME figure, 100–250 €, described as the seller's obligation. Verify the obligation claim.
3. **¶7, the four enumerated facts.** All numbers taken from §2 of the current draft: 6.9%/3.4%; +0.002/+0.008 pre-reform; 79.8/16.7/3.5 and 90.4/8.5/1.1. Fact 4 (cross-market variation) is stated without a number — **supply one** or I will pull the range from §2.4.
4. **¶9.** "140 markets" = 40 apartment + 100 house from Table 1 Panel B. ρ̂ 95.0/71.8, ĉ₀ 1.6/1.8, uninformed shares 83/89 — all from §7.
5. **¶10, robustness.** Written from what exists in §7. **The volume-filter and linear-approximation sensitivities are asserted here — confirm they are actually reported**, or I soften the claim.
6. **¶14, generalizability.** Entirely new. The closing move — mandates preceding measurement capacity — is my framing; check you are willing to own it.

## Cuts — each justified

| Cut | Why |
|---|---|
| Roadmap paragraph (old ¶9) | Convention: this literature does not use them. Replaced by ¶14 |
| `patras_mandatory_2024` self-citation in ¶1 | The numbers are this paper's own (Table 1 Panel A). Citing Chapter 1 beside them was misleading. Cite Chapter 1 where it belongs — for the price-index construction |
| `nauleau_2014` free-riding result | Relocated to §5, where the subsidy heterogeneity is quantified. Too specific for the intro |
| "The market does not punish opacity: it rewards it" | Punchy but editorialising; the corpus keeps ¶1 flat. The same point now lands in ¶7 as a finding |

## Two corrections folded in

- **Units.** "7 percentage points" (abstract) and "7 log points" (intro) both replaced by "approximately 6.9%", matching Table 1's stated convention (`e^δ − 1`, in percent). **The abstract and conclusion still need the same fix** — not yet touched.
- **Notation.** `$K$` removed from ¶6; no notation anywhere in the draft.

## Revision 2 — author's factual corrections (2026-08-12)

Three errors identified by the author, all in ¶6 and ¶7. **Two of the three originate in
`paper/main_concise.tex` and were propagated by preserving ¶6 near-verbatim.** They need fixing
in the original as well as here.

| # | Error | Fix |
|---|---|---|
| 1 | "transaction records capturing actual sale prices and time-on-market, allowing us to trace the market's response from listing through closing" — **false**; transactions are not matched to listings | ¶6 rewritten: transactions enter separately, used only to estimate the listing→sale price mapping (γ₀, γ₁ in `eq:payoff`), supporting the listing price as the outcome. Time-on-market claim and "listing through closing" removed. **Also present verbatim in `paper/main_concise.tex` ¶6 and in §5.1** |
| 2 | "matching properties across all three sources" — the match is **two** sources | ¶6 now states the match is listings → ADEME registry on address/type/area/floor. **§5.1 of the original says "three sources matched at the listing level" — same error** |
| 3 | The 3.5% strategic-hider share chained onto the premium sentence, implying one sample and one source | ¶7 now separates the two samples explicitly and drops the chaining; ¶4's 48.8% scoped to address-matched listings |

Also corrected: the matched sample is the **address-geocoded subset**, not the full listing
universe. Scoping added in ¶4 and ¶6. Confirmed 48.8% is this paper's own ADEME figure
(100 − 51.2 from §5.1), so the earlier concern about it coming from Chapter 1 does not apply —
but Chapter 1 *is* the source of the price-index panel underlying facts 1 and 2, which is why
the two samples must be kept separate.

### Unresolved: the decomposition is reported three ways

| Source | Truthful | Hiders | Uninformed | Other |
|---|---|---|---|---|
| §2.3 (fact 3 figure) | 79.8% | 3.5% | 16.7% | — (sums to 100) |
| §5.2 `tab:groups` (full sample) | 49.3% | 3.5% | 44.9% | 2.3% non-certifiable |
| §5.1 text | — | — | K=0 → 48.8% | — |

Only the 3.5% is stable across all three. Table 3's implied K=1 share (52.8%) also disagrees
with §5.1's 51.2%; the house figures diverge similarly. ¶7 therefore reports **only** the stable
hider shares (3.5% / 1.1%) plus the qualitative claim that the uninformed dominate the silent
pool, with a `% FLAG` comment marking the omission. Supply the authoritative decomposition and
its sample definition and I will complete fact 3.

A related item for later: §5.2 reports the hiding rate among informed sellers as 6.9% (apartments)
/ 2.7% (houses), while Table 1 Panel C reports σ̂₀ at 7.7% / 3.7%. These may legitimately differ
(full sample vs. the 2022–2024 structural sample across 40/100 markets) — but if so the paper
should say which is which.

## Revision 3 — pre-reform interpretation and decomposition authority (2026-08-12)

### The pre-reform coefficients were misinterpreted

The original §2.1 read a **level** conclusion off **difference-in-differences** estimates:

> "Before the reform, the controlled gap fluctuates near zero in both segments (a mean of
> $+0.002$ log points for apartments and $+0.008$ for houses), consistent with buyers treating
> absent EPCs as equivalent to the worst displayed scores when the DPE carried no legal weight."

Because the estimates are normalised to a pre-reform baseline, near-zero pre-period coefficients
mean the two series **moved in parallel** — they say nothing about whether the levels were equal.
The inference that buyers treated absent EPCs as equivalent to the worst displayed score is
therefore unsupported, and it is contradicted by the paper's own Figure 1, which shows apartment
non-disclosers occupying the top price tier from 2019 onward.

The paragraph was also internally inconsistent: it stated that the controlled gap "purges
observable composition differences," then drew a level conclusion from baseline-normalised
estimates.

Rewritten in **both** `paper/main_concise.tex` and `paper-real-estate/main.tex` to say: the
pre-reform coefficients establish parallel trends, which is the identifying assumption the
design requires; the reform widens an existing level difference rather than creating one; and the
contrast with classical unraveling rests on the post-reform premium. Intro ¶7 fact 2 rewritten to
match.

**Identification note, for the §4.4 rewrite.** This distinction has a consequence worth
addressing. The structural step sets ρ̂ = Δ̂ / (β̂₁ · ê\*), where Δ̂ is the *change* in the
non-disclosure premium, and the exclusion restriction is that pre-reform ρ ≈ 0 because the DPE
was not legally opposable. Parallel pre-trends do not establish that. What would is the
pre-reform **level** of the composition-adjusted gap — if that level was already positive for
apartments net of composition, then Δ̂ identifies ρ_post − ρ_pre rather than ρ_post, and ρ̂ is
attenuated. Figure 1's apartment level premium is attributed to the concentration of non-audited
stock in high-price urban markets, i.e. to composition; the hedonic-controlled level gap would
settle the question but is not currently reported. Worth reporting.

### Decomposition: §2 is authoritative (author's instruction)

Fact 3 now uses §2.3's figures: apartments 79.8% truthful / 16.7% uninformed / 3.5% hiders;
houses 90.4% / 8.5% / 1.1%. The `% FLAG` comment is removed.

**Consequential follow-up, not yet actioned:** `tab:groups` in §5.2 now conflicts with the
authoritative source and cannot simply be reworded — its numbers differ (apartments 49.3 / 3.5 /
44.9 / 2.3, and a fourth non-certifiable category that §2.3 does not have, though §2.3 sums to
100). Either the table is computed on the full listing universe while §2.3 uses the
address-matched sample — in which case both need explicit sample labels — or the table is stale
and needs regenerating. **I have not edited the table's numbers, since I cannot recompute them.**
The same applies to §5.2's prose claim that the hiding rate among informed sellers is 6.9%/2.7%,
against Table 1 Panel C's σ̂₀ of 7.7%/3.7%.

### Data-description overclaims fixed in the original paper

Both errors identified earlier now corrected in `paper/main_concise.tex` as well as the fork:

- §5.1: "three sources matched at the listing level" → two matched sources plus transaction
  records used separately for the listing-to-sale price mapping (γ₀, γ₁ in `eq:payoff`)
- §5.1: the transaction/time-on-market matching claim removed
- Original intro ¶6: the three-way enumeration collapsed to two sources, "matching properties
  across all three sources" replaced with the actual match keys, address-geocoding scope stated,
  and the transaction role described correctly

## Recommended bibliography additions

Neither is in `DPE_library.bib`; I did not insert keys that would break the build.

1. **Bourveau, Breuer & Stoumbos (2025), "Learning to Disclose," *RFS* 38(9).** Strongly recommended in ¶13 strand 1. It is the closest antecedent to this paper — a structural test of whether unraveling is descriptive — and it is the model for placing this kind of work in a finance journal. Its absence from a paper testing unraveling structurally is conspicuous.
2. **Bourveau, Garel & Petit-Romec, "Mandatory Carbon Disclosure: Evidence from France."** Mandatory environmental disclosure, French setting. Natural cite in ¶14.

Say the word and I will add both entries and wire them in.

## Suggested appendix robustness checks

You asked for suggestions. Ordered by value per unit of effort:

**Cheap, high value**

1. **ρ_m = 1 restriction as a nested benchmark.** Impose full buyer sensitivity everywhere — the classical homogeneous-buyer case — and compare implied concealment costs to the heterogeneous-ρ estimates. Reuses existing machinery. Directly quantifies what assumption (d) buys.
2. **Coverage-gap characterisation.** Compare observable characteristics of the markets dropped by the volume filter against those retained. Item 9 in your own review doc. Referees ask this reflexively of any filtered sample, and it is pure description.
3. **Pre-trend test on Δ̂ specifically.** Your assumptions table records common trends as tested for β̂₁ via event study but **untested for Δ̂** — which is the parameter that identifies ρ. This is the most exposed untested assumption in the paper. An event-study plot of Δ̂ by month would close it.

**Moderate effort, classic in Dye-type settings**

4. **Vary the quality threshold.** The A–D / E–G split at threshold 4 is a modelling choice. Re-estimate with the cut at C/D and at E/F. If ĉ₀ is stable, that is a strong result; if not, you learn where the two-quality abstraction binds.
5. **Misreporters.** The model assumes no falsification; the four-group classification identifies a rare misreporting group. Re-estimate treating misreporters as hiders, and as truthful disclosers, to bound the effect of the no-falsification assumption.
6. **Structural profit-gain function.** Replace the linear Δ(e) = ρβ₁e with `profit_gain_hiding_structural()` and compare ĉ₀. Item 11 in your review doc; the function already exists.

**Higher effort**

7. **Bootstrap the DiD first stage** to obtain SE(ρ̂) rather than treating ρ̂ as fixed. Item 10 in your review doc. Also lets you apply a confidence-interval filter to the full-unraveling classification (item 6), which currently rests on a point estimate of Δ̂ ≤ 0.
8. **Listing-to-transaction price mapping.** Your assumptions table flags γ₀ = 0, γ₁ = 1 as a moderate assumption affecting the units of ĉ₀. A regression of transaction on listing price would let you rescale, or at least bound the distortion.

Items 3 and 7 are the two a referee is most likely to demand.
