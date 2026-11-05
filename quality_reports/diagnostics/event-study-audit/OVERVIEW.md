# DiD Event-Study Overview — what "6.9%" and "3.4%" actually are

Generated 2026-09-14 from `scripts/diagnose_event_study.py` (read-only; no file in
`paper-real-estate/`, `src/`, or `results/` was touched to produce this). Full numeric output:
`summary.txt` in this folder. Figures: `figures/`.

This is a diagnostic memo for you, not paper prose — it states what the code computes and
reconciles it against every number currently in play. It does not argue that 6.9%/3.4% is right
or wrong; that's your call once you can see it.

---

## 1. What data feeds this

`data/index_APARTMENT.csv` (30,780 rows) and `data/index_HOUSE.csv` (33,601 rows) — a hedonic
price-index panel built in your prior chapter (`patras_mandatory_2024`, cited throughout the
manuscript for this). Monthly, October 2018 – July 2024, by EPC category (`Efficient` /
`Balanced` / `Intensive` / `Missing`) × market (`cluster_id`, a *zone d'emploi*). Two price
columns exist per row: `prices` (the level, €/m²) and `final_index` (a growth-rate index
normalized to 100 at October 2018 — **not** a level).

**This matters, because the repo currently computes the same object two different ways, on the
same data, and they disagree.**

## 2. Two DiD computations already exist in this repo — and they don't agree

| | `src/event_study.py::compute_did()` | `scripts/make_stylized_facts.py::make_fact1()` |
|---|---|---|
| Feeds | The actual structural pipeline: `main.py`/`run.py` → `results/comparison.txt`, `results/tables/table_market_estimates.tex` — the numbers behind the paper's structural claims | The paper's own cited Fact-1 figure (`fig_fact1_nondiscl_premium_eventstudy.pdf`, §3.3.1) |
| Variable used | `prices` (the level) | `final_index` (the growth index) |
| Per its own code | `event_study.py`'s docstring explicitly warns: *"final_index is a growth-rate index normalised to 100 at Oct-2018 base; log(final_index) measures differential appreciation, not the price level"* — i.e. the module itself says `final_index` is the wrong variable for this | Uses `final_index` anyway |

I ran both, on the same underlying files, at the **national aggregate** level (volume-weighted
average across all markets, by EPC category, by month) — see Figure 1.

**National aggregate non-disclosure premium (undisclosed − EFG), log points → %:**

| | Apartments | Houses |
|---|---|---|
| `make_fact1` methodology (`final_index`) | pre +0.21%, post +4.39%, **DiD +4.27%** | pre +0.76%, post +3.68%, **DiD +2.97%** |
| `event_study.py` methodology (`prices`) | pre +12.26%, post +18.05%, **DiD +5.96%** | pre −2.07%, post +2.84%, **DiD +4.91%** |
| **Manuscript states** | **6.9%** | **3.4%** |

**National aggregate EPC quality premium (efficient − EFG):**

| | Apartments | Houses |
|---|---|---|
| `make_fact1` methodology (`final_index`) | **DiD +4.48%** | **DiD +5.21%** |
| `event_study.py` methodology (`prices`) | **DiD +0.01%** (essentially zero) | **DiD +5.99%** |
| **Manuscript states** | **1.7%** | **5.1%** |

The apartment EPC-premium row is the sharpest divergence: the level-based national aggregate is
essentially **zero**, while the growth-index method gives 4.48% and the manuscript states 1.7%.
None of the three numbers agree with each other.

## 3. Why the market-level number is different from the national-aggregate number

The manuscript's 6.9%/3.4% is **not** the national-aggregate gap above. It is the simple,
unweighted **cross-market average** of each market's own DiD estimate. I ran
`compute_did()` exactly as `main.py`/`run.py` call it (same `min_volume=20` filter):

| | Apartments | Houses |
|---|---|---|
| Markets passing the volume filter | **81** | **114** |
| DiD_beta1 (β̂₁ₘ): mean / median | **1.69%** / 1.97% | **5.07%** / 4.74% |
| DiD_delta (Δ̂ₘ): mean / median | **6.92%** / 6.36% | **3.41%** / 3.08% |
| Markets with β̂₁ₘ ≤ 0 | 32/81 (40%) | 10/114 (9%) |

**The cross-market mean here (6.92% / 3.41%, 1.69% / 5.07%) matches the manuscript's headline
numbers almost exactly** (6.9%/3.4%, 1.7%/5.1%) — so I've faithfully reproduced the actual
pipeline, and now you know precisely what "6.9%" is: the unweighted average, across ~81
equally-weighted local markets, of each market's own pre/post price-gap change. It is not
volume-weighted (so a market with 20 transactions counts the same as one with thousands), and it
is not what the national aggregate time series in Figure 1 shows moving.

## 4. The market-count question has (at least) four different answers

| Source | Apartments | Houses |
|---|---|---|
| `results/comparison.txt` (live output) — all "estimable" markets from listings data, before any DiD filter | **302** | **564** |
| This diagnostic — markets passing `compute_did()`'s volume filter | **81** | **114** |
| This diagnostic — markets with a *valid* ρ̂ₘ (β̂₁ₘ>0 **and** matched to listings market_stats) | **45** | **97** |
| Manuscript text, at various points | 40, 49, 43 | 100, 104, 107 |

The **45 / 97** row matches two of the manuscript's own quoted numbers exactly — so that
particular pair is traceable to a real pipeline stage (DiD-valid markets after matching to the
listings sample). The **40 / 49 / 43** and **100 / 104 / 107** figures elsewhere in the text do
not correspond to any stage I can reproduce from the code as it currently stands; they may come
from a later, further-restricted MSM stage this diagnostic doesn't run (the moments-availability
intersection in `run.py`'s step [4/5]), or they may simply be stale, consistent with what both
referees flagged independently.

## 5. The ρ̂ₘ clipping, and the ĉ₀ > β̂₁ inequality — reproduced fresh, not just read off a stale table

Of the 45 apartment markets with a valid ρ̂ₘ: **40 (89%) clip at exactly 1.0**, 3 (7%) clip at
0.0 — only 2 markets land strictly between. This matches the manuscript's own reported ρ̂ mean
of 90.9% almost exactly, confirming Table 4's ρ̂ statistic really is dominated by the clip, not
by interior variation (see Figure 3). Houses: 54/97 (56%) clip at 1, 21/97 (22%) clip at 0.

For apartments, this fresh run reproduces the inequality the methods referee's algebra
predicted: **mean ĉ₀ₘ (2.27%) > mean β̂₁ₘ (1.60%)** across the 45 valid markets — which the
estimator `ĉ₀ₘ = ρ̂ₘ·β̂₁ₘ·ê*ₘ` with ρ̂ₘ, ê*ₘ ∈ [0,1] should make impossible market-by-market, and
therefore impossible in the mean. (`results/comparison.txt`'s own live numbers show the same
violation with its own values, 3.42% > 1.6% — a different pipeline stage, same violation, found
independently twice.) **Houses do not show this violation** (2.53% < 5.11%) — worth being
precise that this is an apartment-specific pattern, not a bug that hits both segments equally.

## 6. Figures

- `figures/fig1_eventstudy_{apartment,house}.pdf/png` — the national aggregate gap over time,
  both methodologies overlaid, reform date marked. This is the direct visual for "is 6.9%/3.4%
  plausible" — but per §3 above, note that what the paper actually reports is the cross-market
  average shown in Figure 2, not this national series.
- `figures/fig2_market_distributions.pdf/png` — histograms of β̂₁ₘ and Δ̂ₘ across the 81/114
  volume-filtered markets, both property types, with the manuscript's headline number marked
  against the cross-market mean.
- `figures/fig3_rho_saturation.pdf/png` — Δ̂ₘ vs. β̂₁ₘ·ê*ₘ per market, with the 45° line (where
  ρ̂ₘ = 1 exactly). Points above the line are markets where the unconstrained ratio exceeds 1
  before clipping — visually, how much of the apartment sample sits above that line is the
  picture behind "ρ̂ₘ clips at 1 in 89% of markets."

## 7. What this doesn't tell you

No standard errors, no significance test, no judgment about whether 6.9%/3.4% is "real." This
is a reconciliation of what different parts of the existing pipeline compute, on the data as it
currently sits — not a new estimate, and not a fix.
