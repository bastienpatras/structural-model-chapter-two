# Finding: σ₁* = 0 is imposed by the code, and the registry rejects it

Found 2026-08-12 while preparing §4.5. **Blocks the §4 consolidation** — §4.5 was to lead with
this result, and the result does not hold.

## 1. σ̂₁ = 0 is a tautology, not a test

`src/data_prep.py:190-194`:

```python
# Strategic hiders (d=0, K=1) have theta=0 by revealed preference:
# the model predicts σ₁*=0 (high-quality informed sellers always disclose,
# Corollary (cor:hq_disclose)), so any informed non-discloser must be low quality.
mask_hiders = (df["d"] == 0) & (df["K"] == 1)
df.loc[mask_hiders, "theta"] = 0
```

`compute_market_stats` then computes `sigma_1_hat` as the share of `(K=1, θ=1)` listings with
`d=0`. Since every `(K=1, d=0)` listing has just had θ forced to 0, that set is empty by
construction and `sigma_1_hat ≡ 0` for every market, always. The comment in the code even names
the corollary as the justification — the model's prediction is used to construct the variable
that is then said to confirm it.

**This is circular, and I previously mis-advised on it.** I described σ̂₁ = 0 as "an overidentifying
restriction, not used in estimation, that the data could have rejected" and recommended promoting it
to lead the findings as the paper's specification test. That was wrong. It is an imposed assumption
and cannot be violated. Retracted.

Note also that σ̂₁ is never reported anywhere — not in `results/*/results.txt`, not in the Results
section. Every mention of σ₁ in the paper is theoretical (the corollary, the belief function, the
proofs).

## 2. The test *can* be run, and it rejects the corollary

The registry records the actual score for every `K=1` listing, including hiders —
`ademe_epc_score` is populated for 431,662 of 431,662 apartment `K=1` listings. So the hiding rate
by true quality is directly measurable, without the imposed θ.

**P(withhold | informed), by registry quality:**

| | θ=1 iff A–C | | θ=1 iff A–D | |
|---|---|---|---|---|
| | σ̂₁ (high) | σ̂₀ (low) | σ̂₁ (high) | σ̂₀ (low) |
| Apartments | **6.46%** | 7.02% | **6.21%** | 7.88% |
| Houses | **2.82%** | 2.67% | **2.51%** | 3.02% |

The model predicts σ₁ = 0 and σ₀ > 0. Instead σ̂₁ ≈ σ̂₀ at both thresholds and in both segments —
for houses at the A–C threshold, high-quality informed sellers withhold *slightly more often* than
low-quality ones (ratio 1.05).

Equivalently, the registry-score distribution of strategic hiders is nearly identical to that of
verified disclosers: 24.3% A–C among apartment hiders against 26.0% among apartment disclosers;
27.7% against 26.6% for houses.

## 3. Why this matters more than the section restructuring

**Among informed sellers, the decision to omit the EPC is essentially uncorrelated with quality.**
That is not a peripheral failure — ĉ₀ is recovered from σ̂₀ by inverting the seller's indifference
condition, and that inversion interprets σ̂₀ as the rate at which informed sellers *strategically
conceal unfavourable information*. If withholding is quality-independent, σ̂₀ is not measuring
strategic concealment, and ĉ₀ is not a concealment cost.

The most plausible benign reading points the same way: a hiding rate that is flat in quality is
exactly what **incomplete or careless listings** would produce. On that reading the `(K=1, d=0)`
group is dominated by listing incompleteness rather than deliberate concealment, and the ~6.5%/2.8%
rate is a measure of data-entry behaviour rather than of a strategic margin.

Two secondary consequences:

- **The θ imposition biases σ̂₀ upward.** Forcing all 29,676 apartment hiders into the low-quality
  group inflates both the numerator and the denominator of σ̂₀ relative to the registry-based
  measure (roughly 9.1% versus a true 7.0% at the A–C threshold, pooled).
- **`\hat\sigma_{1,m}` is computed and stored but never reported**, so nothing in the paper would
  have surfaced the problem.

## 3b. Pipeline comparison on the estimation sample (added after the fix)

`merge_datasets` now takes `hider_theta ∈ {"registry", "impose_zero"}`, defaulting to
`"registry"`. Both modes were run through the full pipeline on the apartment config, writing to
`results/_sigma1test_impose_zero/` and `results/_sigma1test_registry/`. Legacy mode reproduces the
published numbers exactly, which validates the switch. Market means over the 2022–2024 estimation
sample, i.e. computed exactly as the paper computes σ̂₀:

| | `impose_zero` (legacy) | `registry` (fixed) | change |
|---|---|---|---|
| σ̂₀ mean | 0.0766 | **0.0510** | −33% |
| σ̂₁ mean | 0.0000 (imposed) | **0.0654** | — |
| **σ̂₁/σ̂₀** | 0.000 | **1.282** | corollary rejected |
| θ̄ mean | 0.265 | 0.284 | +7% |
| ê\* mean | 0.2522 | 0.2733 | +8% |
| **ρ̂ mean** | 0.9500 | **0.9500** | unchanged |
| **ĉ₀ mean** | 0.0162 | **0.0175** | +8% |
| Full-unravelling markets | 2 (5.0%) | 2 (5.0%) | unchanged |

**The quantitative results survive; the mechanism story does not.**

- **ρ̂ is completely unaffected** — identical to four decimals, still clipped at 1 in the same
  markets. Expected: ρ̂ comes from the DiD on the price-index panel, which never touches θ.
- **ĉ₀ moves 8%**, from 0.0162 to 0.0175, and moves *up*. σ̂₀ falls by a third, but ĉ₀ = ρ̂·β̂₁·ê\*(σ̂₀)
  and ê\* rises (mostly because θ̄ rises once hiders' true quality is counted), so the two effects
  partly offset. With ρ̂ clipped at 1 in 38 of 40 markets, ĉ₀ is close to β̂₁·ê\* and inherits ê\*'s
  movement.
- **σ̂₁ = 0.065 exceeds σ̂₀ = 0.051.** On the paper's own sample and estimator, high-quality informed
  sellers withhold *28% more often* than low-quality ones. This is a sharper rejection than the
  pooled full-sample calculation in §2 above (which gave a ratio of 0.92), and it settles the
  sample-definition caveat: the direction is not an artefact of pooling or of including 2021H2.

So the numbers in the paper are robust to the fix. What is not robust is the claim that σ̂₀ measures
strategic concealment of unfavourable information.

## 3c. Hiding is U-shaped in quality, minimised at D

P(withhold | informed), by registry grade, full listing sample:

| | A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|---|
| Apartments | **9.52%** | 6.53% | 6.43% | **6.01%** | 6.81% | 8.62% | **11.17%** |
| Houses | **4.43%** | 3.11% | 2.65% | **2.25%** | 2.52% | 3.28% | **4.62%** |

Minimum at D, rising toward both tails, replicated independently in both segments. The model
predicts monotone decreasing. The G tail is consistent with strategic concealment; **the A tail is
not** — an A-rated seller has nothing to conceal. Not a small-sample artefact: A apartments give
9.52% ± 1.7pp against C's 6.43% ± 0.08pp.

This also explains why σ̂₁ > σ̂₀ once θ is measured: the A/B grades, which sit inside θ=1, carry the
highest hiding rates in the upper half.

**A usable implication.** If A-rated sellers cannot be concealing bad news, their rate is a
benchmark for *non-strategic* non-disclosure — incompleteness, atypical sale channels, off-plan
sales where the certificate is not yet final. Netting it out leaves a strategic component at G of
roughly 11.2 − 9.5 ≈ 1.7pp for apartments rather than 11.2pp. That is a candidate identification
strategy for the strategic margin, and it would shrink it substantially.

## 4. Extension (per the author: treat as an extension, not a baseline change)

**Correction to my earlier suggestion.** I proposed the $\alpha_k < \beta_k$ distrust-discount case
as the route out. It is the wrong extension for this fact: a discount on unverified quality makes
non-disclosure *less* attractive, which reinforces σ₁\* = 0 rather than relaxing it. The paper's own
text confirms the direction — under $\alpha_k < \beta_k$ "the non-disclosure premium would be
smaller for any given pool composition".

Two extensions that do fit the U-shape:

1. **A non-strategic disclosure-cost channel varying with property atypicality.** The only candidate
   that explains *both* tails. Operationally: an additive hazard of non-disclosure independent of θ,
   which the A-rated benchmark above identifies, on top of the strategic margin. Recommended as the
   primary extension.
2. **Ordered rather than binary θ.** Almost all θ=1 hiders are C-rated (22.3 of 24.3pp), and a
   C-rated seller just above the threshold may rationally prefer the pool's expected quality — which
   a binary θ cannot represent. Preserves the strategic mechanism and localises the failure to the
   discretisation, but does **not** explain the A tail. Best used as a threshold robustness check.

## 4b. A possible route out, which the model already contains

The corollary is not free-standing: it "follows directly from Proposition~\ref{prop:premium}(i)",
and the model's own text notes that the second hiding-cost component $c_1$ becomes binding only
when $\alpha_k < \beta_k$ — the *distrust discount* case. The assumptions table lists
$\alpha_k = \beta_k$ as a **strong** maintained assumption.

So the rejection may be read as evidence against the $\alpha_k = \beta_k$ benchmark rather than
against the model as a whole. Under $\alpha_k < \beta_k$, high-quality informed sellers can
rationally withhold, and the machinery ($c_1$) is already written down. That is a substantive
modelling decision, not something to paper over.

## 5. What I recommend, in order

1. **Decide what `d=0` among informed sellers means.** Strategic concealment, listing
   incompleteness, or a mixture? This determines whether ĉ₀ is interpretable as a concealment cost.
   Nothing downstream can be settled first.
2. **Stop imposing θ = 0 on hiders.** Use the registry score, which is observed for 100% of them.
   Then σ̂₀ and σ̂₁ are both measured rather than one being assumed, and σ̂₁ = 0 becomes a genuine
   testable restriction.
3. **Report σ̂₁.** Whatever the resolution, a quantity the model predicts to be zero should appear
   in the results table.
4. **Consider the $\alpha_k < \beta_k$ extension** if the strategic reading is to be retained.
5. Only then resume the §4 consolidation, since §4.5's lead result depends on the outcome.

## Caveats on this finding

- Threshold sensitivity was checked at A–C and A–D; the rejection holds at both, and is stronger at
  A–D for apartments.
- `ademe_epc_score` is populated for every `K=1` listing and is the registry value, not the
  displayed score — for `d=0` listings there is no displayed score, so it cannot be a copy.
- These are pooled rates over the full listing sample, not market means over the 2022–2024
  estimation sample. The market-level numbers will differ somewhat; the near-equality of σ̂₁ and σ̂₀
  is large enough that it is very unlikely to be a sample-definition artefact, but it should be
  recomputed on the estimation sample before anything is written.
