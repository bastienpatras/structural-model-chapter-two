# Desk Review: `paper-real-estate/main.tex` — `/review-paper --peer TOPFIN`

**Date:** 2026-09-14 · **Novelty check:** ON · **Cross-artifact Phase 0:** NOT RUN (see note)

## Contribution statement (editor's understanding)

After France made the DPE legally opposable in July 2021, listings with *no* disclosed score
trade at a premium over listings disclosing a bad score (+6.9% apartments, +3.4% houses) — the
reverse of unraveling. The claimed resolution: the silent pool is dominated not by strategic
concealers but by sellers who genuinely hold no certificate, so silence cannot be read as bad
news. The distinctive asset is that the paper **observes seller information status directly**,
by matching SeLoger listings to the ADEME registry — the latent variable the entire Dye/Jung–Kwon
literature has had to assume. On that it estimates, market by market, a disclosure game with two
departures (uninformed share π, EPC-sensitive buyer share ρ), derives a closed form in which the
partial-pooling premium collapses to the concealment cost c₀ invariant to market composition, and
extends to endogenous renovation for a minimum incentive-compatible subsidy ranging from zero to
full renovation cost across French markets.

That is statable in one sentence, which is the desk test. **Sent out.**

## Desk-reject analysis — none of the six criteria met

- **Wrong fit** — no. Information economics + housing + structural + matched administrative
  registry is squarely TOPFIN; the profile's own Tier-1 exemplar (Bourveau, *Learning to
  Disclose*, RFS) sits on the same anchor and is cited as closest antecedent. Six-section
  architecture respected; lit positioning folded into the intro per house style.
- **No clear contribution** — no; §1 ¶11–12 state two crisply.
- **Fatal design flaw in the abstract** — no. DiD on a market-level hedonic index panel around a
  dated legal change, structural inversion layered on top. Legible and defensible at desk level.
  It has a serious *exposure* (below) but is not unidentified-on-its-face.
- **Below the bar** — no. The data asset alone clears it. Whether the *structural layer* clears
  it is the referee question, not the desk question.
- **Already done** — no. Closest cousin is an uncited entry in the author's own bib: a revision
  item, not a desk reject.
- **Reproducibility FAIL** — n/a, Phase 0 did not run.

## Cross-artifact note (for the record)

Confirmed: no detection signals per `cross-artifact-review.md`. `main.tex` `\input`s only its own
prose sections, no `\input{}` of generated tables, no `%% source:` comments, no table labels
matching `_outputs/` filenames. All numbers typed inline. `/review-python` and
`/audit-reproducibility` correctly not invoked this run.

Two consequences, passed to referees rather than resolved here:
1. **The desk had no independent check on any number in this paper.** Figures reach the
   manuscript only via `\includegraphics`; every table is hand-typed. The paper↔code graph is
   unwired at the table level.
2. **That is itself a submission-readiness finding.** Hand-typed tables whose upstream artifacts
   are `M`-modified-uncommitted right now (`results/tables/table_estimates.tex`,
   `table_market_estimates.tex`, `table_subsidy_grid.tex`) are precisely the configuration that
   produces drift — and the internal-consistency cluster below is plausibly the symptom.
   **Recommend running `/audit-reproducibility` against `results/` before the revision, and
   wiring `main.tex` to `\input{}` the generated tables so `CLAUDE.md`'s single-source-of-truth
   rule is mechanically enforced rather than hand-maintained.**

## Internal-consistency cluster (escalated, not desk-fatal)

Not normally listed at desk. These are listed because they are mechanically checkable, several
sit in the abstract/conclusion where an editor reads, and a real JF/JFE/RFS desk would return the
manuscript on item 1 alone.

1. **Corrupted sentence in the Conclusion.** `main.tex:301`: *"…5.7% of house sellers do.7% of
   house sellers do so."* A duplicated paste fragment, four lines from the end of the headline
   result.
2. **Aggregate programme cost contradicts itself.** §5.4 (`:291`) gives **€15.5bn** at the light
   benchmark (6.4 + 9.1, sums correctly). Conclusion (`:303`) gives **€14.6bn** at the same
   benchmark.
3. **Audit coverage reported three ways.** §3.2 (`:61`): 51.2% / 40.3%. Table Panel C π̂:
   **50.7% / 41.9%**. Conclusion (`:299`): **51.8% / 41.7%**. Plausibly three different objects
   (full-sample, cross-market mean, estimation-sample) but labelled identically and never
   reconciled.
4. **Market counts drift.** §4.4 `:395` "retains 40 apartment markets and 100 house markets";
   §4.4 `:446` "45 apartment and 97 house markets"; Table `tab:did_results` column N: 49/104
   (Panel A), 45/97 (Panels B–C); that same table's *note* says "N=43 apartment … N=107 house,"
   neither of which appears in the table it annotates; §4.5 `:524` implies 42+3=45 and
   54+22+21=97; §5.4 reverts to 40/100. `scripts/check-derived-counts.py` exists and commit
   `da9f158` claims to "correct market counts" — whatever that fixed, this isn't fixed.
5. **Regime nomenclature drift.** Model defines CDH / Partial Pooling / Complete Adverse
   Selection. §4.3 `:350` and §4.5 `:524` instead say "full-unraveling markets" — not one of the
   three defined regimes. CDH is presumably meant; a referee shouldn't have to presume.
6. **Uninformed-share misuse.** §1 ¶4 (`:58`) says "48.8% hold none" — that is the K=0 share from
   `tab:groups`, i.e. no *post-2021 registry record*, which the same table's note is at pains to
   explain is **not** the share holding no certificate. ¶4 uses the coverage-gap number to
   support the genuine-ignorance claim that §3.2 `:103–118` explicitly warns against. Also ¶7
   says 8.5% uninformed for houses; `tab:groups` says 8.6%.

## Table-format deviations (TOPFIN override)

Profile requires stars at 10/5/1%, 3-decimal coefficients, SEs in parentheses, clustering in a
note.

- **No standard errors anywhere on the structural estimates.** `tab:did_results` reports
  Mean/Std/N, where "Std" is documented as the *cross-market* SD, not a standard error. No
  sampling uncertainty on ρ̂, ĉ₀, β̂₁, or Δ̂ at any level.
- **No clustering statement** in any table note in the manuscript.
- **No inference on the policy magnitudes** — the €15.5bn/€38.7bn aggregates, the 40/46/70% cost
  shares, and the "3–8× MaPrimeRénov'" multiplier (the headline fiscal facts) carry no
  uncertainty band.
- **Decimals inconsistent** — 6.9%, 3.42%, and 0.034 log points for the same class of object,
  sometimes in one paragraph (§4.5 `:526–530`).
- Stars are permitted here and simply absent — a consequence of the missing inference, not a
  separate issue.

## Novelty probes

**Caveat — nothing below is established.** Per `post-flight-verification.md`, every row is a
*novelty-probe claim requiring verification*. WebSearch can hallucinate citations and misses
paywalled/recent work. None of this is used in the desk narrative as a reason for or against
sending out.

| # | Query | Result |
|---|---|---|
| 1 | non-disclosure premium EPC France 2021 structural disclosure model housing | Only institutional/explanatory material on the DPE and the 2021 opposability reform. **No** academic paper documenting a non-disclosure *premium* in the French EPC setting or estimating a disclosure game on it. Suggestive of clear ground on the core claim. |
| 2 | structural estimation Dye model uninformed sellers matched registry energy label premium | (a) Myers/Puller/West-style work inferring seller ignorance *by simulation* — already cited (`myers_asymmetric_2020`, `myers_mandatory_2022`); strengthens the paper's "we observe, they infer" positioning. (b) "Green Lemons? Energy-Efficiency Disclosure and House Prices" — not cited, unverified. (c) **The important one:** a 2025 *Real Estate Economics* article (Lu) on energy labels and misreporting, reportedly using **French administrative data** and documenting **bunching of DPE scores below cut-offs driven by intentional misreporting**. |
| 3 | unraveling failure, non-disclosers trade at premium, uninformed sellers, 2025 | General disclosure literature (Jovanovic, Matsuno dynamic lemons, experimental unraveling, health-plan disclosure). Nothing pre-empting this paper's claim. One returned finding — tenants not rationally adjusting expectations toward information-withholding dwellings — is close enough to the mechanism to be worth locating. |

**Assessment: Clear on the core claim; one substantive citation gap that is verifiable inside the
repo.**

Probe 2(c) does **not** depend on trusting WebSearch, which is why it is stated here.
`paper/DPE_library.bib:828` already contains `@article{lu_energy_2023, title = {Energy Labels,
House Prices, and Efficiency Misreporting}` — and a grep across all of `paper-real-estate/**/*.tex`
returns **no `\cite`** to it. The entry is in the author's own bibliography and never invoked.
Same for `dranove_jin`, `jin_leslie`, `shin_burden`, `eichholtz_kok_quigley_2010`, `cassidy_how`.

Why it matters, and why it goes to the referees: the paper maintains **No Falsification** (§4.2
`:83`, restated §3.2 footnote and §4.1 `:62`) — "a score published by the owner is taken at face
value, and only omission is treated as a strategic act." That assumption does real work: it is
what classifies the 32.2% of apartment (51.2% of house) listings displaying a score with no
registry record as **truthful disclosers** — the single largest cell in `tab:groups` for houses.
A paper documenting deliberate DPE misreporting in French administrative data is the most direct
available challenge to that assumption, it is sitting in the author's own `.bib`, and it is
unengaged. **Action:** verify the reference (bib key says 2023, probe suggests 2025 *REE* — entry
may be stale), then engage it in §4.2.

Sources (novelty probes, unverified): [E2e WP044 — Mandatory Energy Efficiency Disclosure](https://e2e.uchicago.edu/pdf/workingpapers/WP044.pdf) · [Lu, *Energy labels, misreporting, and heuristic hedonic models*, Real Estate Economics 2025](https://onlinelibrary.wiley.com/doi/10.1111/1540-6229.12535) · [Green Lemons? Energy-Efficiency Disclosure and House Prices](https://www.researchgate.net/publication/319546286_Green_Lemons_Energy-Efficiency_Disclosure_and_House_Prices) · [Service-Public — diagnostic de performance énergétique](https://www.service-public.gouv.fr/particuliers/vosdroits/F16096?lang=en)

## Referee selection (Phase 1b)

Dispositions drawn from TOPFIN's referee-pool weights (CREDIBILITY 0.25 / STRUCTURAL 0.20 /
SKEPTIC 0.20 / MEASUREMENT 0.15 / POLICY 0.10 / THEORY 0.10):

- Draw 1 (full pool): **STRUCTURAL**
- Draw 2 (re-normalised over remaining 0.80): **SKEPTIC**

| Slot | Agent | Disposition | Critical peeve | Constructive peeve |
|---|---|---|---|---|
| **Referee A — domain** | `domain-referee` | **SKEPTIC** | Comparability of the compared groups is asserted rather than shown — no table establishing that the units being compared are alike on pre-existing characteristics. | Appreciates when the paper anticipates the obvious referee objections. |
| **Referee B — methods** | `methods-referee` | **STRUCTURAL** | Structural estimation: parameter plausibility check required (compare to prior literature). | Values raw-data figures before any model (scatter plots, histograms, time series) to build intuition. |

**Paper type for the methods referee:** `structural` (reduced-form DiD first stage feeding a
structural inversion — the DiD is a load-bearing input, not a separable exercise).

**TOPFIN dimension adjustments injected per referee:**
- Referee A: Contribution 30→30 · Lit positioning 25→20 · Substance 20→20 · External validity
  15→**10** · Fit 10→**20**.
- Referee B: Parameter identification 30→**35** · Estimation 20→15 · Fit/validation 15→10 ·
  Counterfactuals 15→**20**.

**Fencing note (`review-fencing.md`).** Both referees receive the manuscript only (`main.tex`,
`sections/01–04`, `A-robustness.tex`) — `FINDING-sigma1.md`, `APPENDIX-GAPS.md`, `DIAGNOSIS.md`,
`PLAN.md`, `V2-QUEUE.md` are withheld, since those are the author's own diagnosis of the paper's
weaknesses and a referee who reads them grades conformance rather than adequacy. The editor did
not read them either. If the referees independently land on the σ₁ or ρ̂-boundary exposures, that
concordance is informative; if handed the notes, it would not be.

**Send-out plan — what each referee should resolve:**
- **Domain (SKEPTIC):** is the premium real and is it the paper's claimed object? Treatment is
  "disclosed nothing," control is "disclosed E/F/G." Satisfy or reject that those sets are
  comparable rather than that the DiD normalisation papered over a level difference the paper
  itself concedes — §3.3.1 `:129`: apartment non-disclosers occupy the highest price tier *from
  2019*, well pre-reform.
- **Methods (STRUCTURAL):** does the structural layer earn its place? Specifically whether ĉ₀ is
  an estimate or an identity, given ρ̂ₘ = Δ̂ₘ/(β̂₁ₘ·ê*ₘ) and ĉ₀ₘ = ρ̂ₘ·β̂₁ₘ·ê*ₘ; and what it
  means that unconstrained ρ̂ₘ exceeds unity in **all 40** apartment markets with cross-market
  mean **≈7.7** (§4.4 `:409`) — roughly eight times outside the model's admissible range, which
  the paper attributes to composition bias and thin-cell attenuation rather than treating as a
  specification test the model fails.
