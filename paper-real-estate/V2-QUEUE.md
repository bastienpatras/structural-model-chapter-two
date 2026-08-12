# v2 queue

Items deferred to a second pass. Author will rerun the pipeline before these are actioned.
Nothing here blocks the section-by-section rewrite.

## Requires a pipeline rerun or author input

1. **`tab:groups` (§5.2) conflicts with the authoritative §2.3 decomposition.**
   Table: apartments 49.3 truthful / 3.5 hiders / 44.9 uninformed / 2.3 non-certifiable.
   §2.3: 79.8 / 3.5 / 16.7, summing to 100 with no fourth category.
   Table's implied K=1 share (52.8%) also disagrees with §5.1's 51.2%. House figures diverge
   similarly. Either the table is the full listing universe against §2.3's address-matched
   sample — in which case both need explicit sample labels — or it is stale.
   Table numbers deliberately left unedited; they cannot be recomputed from the paper.

2. **§5.2 informed hiding rate (6.9% apartments / 2.7% houses) vs Table 1 Panel C σ̂₀
   (7.7% / 3.7%).** Plausibly full sample vs. the 2022–2024 structural sample across 40/100
   markets — if so, label which is which.

3. **Abstract and conclusion still carry the old headline figures** (7/3, and "percentage
   points"). Both should read ≈6.9% / 3.4%, per Table 1 Panel A's stated `e^δ − 1` convention.
   Deliberately deferred: the abstract is rewritten last, from the finished introduction.

## Identification — substantive

4. **~~ρ̂ is attenuated because parallel trends do not establish ρ_pre ≈ 0.~~ Withdrawn — I was
   wrong.** §6.1 already handles this explicitly: *"The DiD does not require that buyers were
   entirely inattentive to EPC scores before July 2021; it requires only that their relative
   pricing of disclosure groups was not already trending."* It further argues the bias runs
   *upward* (both a supply-side shift and any opposability-induced change in c₀ would inflate Δ̂
   and hence ρ̂), which is why ρ̂ is presented as an upper bound. My attenuation claim contradicted
   that and does not survive.

   What remains, much smaller: the corrected §2.1 now states that apartments had a pre-reform
   *level* premium, and Figure 1 makes it visible. A reader may wonder whether that indicates
   ρ_pre > 0. One sentence in §3.3 or §4.4 attributing the level premium to composition — the
   concentration of non-audited stock in high-price urban markets, which is already the paper's
   explanation — would close the question. Worth adding; not a defect.

5. **Promote the stability-of-the-undisclosed-share identification argument.**
   The share of undisclosed listings is stable over time, especially for apartments (documented
   as a stylized fact in §2.2, "Non-Disclosure Persists Long After Mandatory Disclosure"). This
   is a genuinely clean identification argument and is currently under-used: a stable
   non-disclosure share implies the composition of the silent pool, and hence the equilibrium
   belief ê\*, does not shift across the reform. The jump in the premium therefore cannot be a
   supply-side compositional artefact and is attributable to demand-side repricing — ρ moving
   from near zero to positive. It should appear in §4.4 (identification), be previewed in the
   introduction, and be stated explicitly as the reason Δ̂ maps into ρ.
   *(Author's phrasing was "adjustment cannot come from demand but supply"; recorded here as
   supply being what stays fixed, licensing the demand-side attribution. Confirm.)*

6. **Add the two Bourveau citations** once approved: Bourveau, Breuer & Stoumbos (2025, *RFS*)
   in ¶13 strand 1; Bourveau, Garel & Petit-Romec (mandatory carbon disclosure, France) in ¶14.
   Neither is in `DPE_library.bib` yet.

## Introduction items still unverified

7. ¶2 institutional claims — that *loi Climat et Résilience* is the correct instrument, that
   "legally opposable" is right, and that buyer recourse against misstatement is accurate.
8. ¶10 asserts sensitivity to the volume filter and to the linear approximation to the profit
   gain. Confirm these are actually reported, or the claim gets softened.
9. ¶7 fact 4 (cross-market variation in the non-disclosure rate) is stated without a number.

## Standing framing decision

**This is an apartment-market story.** Houses are the secondary segment: same qualitative
patterns, weaker identification (ρ̂ interior in only 8 of 100 markets, 25 full-unraveling), and
a smaller strategic-hiding share. Write apartments first throughout and treat houses as
corroboration rather than a co-equal case.
