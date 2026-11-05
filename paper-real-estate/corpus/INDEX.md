# Reference Corpus

Two tiers, serving different purposes:

- **Tier 1 — Bourveau.** How to make a disclosure-regulation research design credible.
  His own venues are overwhelmingly accounting, so this tier teaches *design credibility
  and disclosure framing*, not venue norms.
- **Tier 2 — RE/finance exemplars.** The venue norms we are actually writing to. Pending
  venue calibration (see `../PLAN.md`, Open questions).

## Access constraints (established 2026-08-11)

| Source | Status |
|---|---|
| `thomasbourveau.github.io` | ✅ open — publication list + CV |
| `business.columbia.edu/.../pubfiles/*.pdf` | ✅ open (static PDFs only) |
| `business.columbia.edu` HTML pages | ❌ 403 Cloudflare — cannot scrape link lists |
| `ora.ox.ac.uk/objects/uuid:.../files/<id>` | ✅ open — direct file download works |
| `ora.ox.ac.uk` faceted search | ❌ 403 — cannot enumerate deposits |
| SSRN (abstract pages *and* PDFs) | ❌ 403 Cloudflare, even with browser UA |
| Publisher sites (Wiley, Springer, Elsevier, OUP, AAA) | 🔒 paywalled — need Sciences Po access |

Practical consequence: openly-hosted working-paper versions are reachable; **SSRN-only
items require manual download.** Discovery path is search-then-curl, one paper at a time.

## Tier 1 — Bourveau

### Acquired

| File | Paper | Venue |
|---|---|---|
| `bourveau/learning-to-disclose_RFS.pdf` | Learning to Disclose: Disclosure Dynamics in the 1890s Streetcar Industry (Breuer, Stoumbos) — 74pp | **RFS** 38(9), 2025 |
| `bourveau/company-websites-disclosure-measure_JAR.pdf` | Company Websites: A New Measure of Disclosure (Boulland, Breuer) | JAR 64(1), 2026 |
| `bourveau/firm-boundaries-voluntary-disclosure_TAR.pdf` | Firm Boundaries and Voluntary Disclosure (Kepler, She, Wang) | TAR 99(4), 2024 |
| `bourveau/CV_Bourveau_July2025.pdf` | CV | — |

★ **`learning-to-disclose_RFS.pdf` is the primary template.** Structural disclosure paper,
top finance placement, same Grossman/Milgrom anchor as our paper. See `../PLAN.md`.

### Priority, not yet acquired

| Paper | Venue | Why it matters | Route |
|---|---|---|---|
| Mandatory Carbon Disclosure: Evidence from France (Garel, Petit-Romec) | WP | ★ Mandatory *environmental* disclosure, *French* setting — nearest neighbour to our paper. Likely citation gap. | SSRN 4779950 (blocked) |
| Comply-or-Explain Regulation and Investor Protection (Gao, Li, Zhou) | JAE 79, 2025 | Regulatory design; disclose-or-justify mechanism | SSRN 4436460 / ScienceDirect |
| The Impact of Disclosure on Diversity: Canada Business Corporations Act (Gao, Hope) | CAR, acc. | Causal effect of a disclosure *mandate* | Wiley |
| The Role of Disclosure and Information Intermediaries in an Unregulated Capital Market: ICOs (De George, Ellahie, Macciocchi) | JAR 60(1), 2022 | Voluntary disclosure / unravelling in an unregulated market | Wiley |
| Stock Market Reaction to Product-Level Carbon Estimates (Lauer, Zipperer) | WP | Environmental information capitalised into prices | SSRN 5126184 |

### Full publication list (for reference)

Published: RAST 2017 (shareholder activism) · JAR 2018 (shareholder litigation) · JAR 2020
(cartel enforcement) · TAR 2021 (hurricanes/analysts) · JEEA 2021 (insider trading France) ·
JAR 2022 (ICOs) · Management Science 2022 (Florange Act) · RAST 2023 (public peers) · CAR
2024 (mutual fund reporting frequency) · RAST 2024 (analyst distraction) · TAR 2024 (say on
pay) · TAR 2024 (firm boundaries) · RAST 2024 (DeFi assurance) · JAR 2026 (company
websites) · **RFS 2025 (learning to disclose)** · JAE 2025 (comply-or-explain) · TAR acc.
(public company auditing) · Management Science acc. (EEO-1 diversity) · CAR acc. (Canada
disclosure/diversity).

Working: human capital disclosures · how private companies win attention · **mandatory
carbon disclosure France** · executive incentives/poaching · market-based incentives for
audit quality · **product-level carbon estimates** · voluntary revenue disclosure by US
private companies · landscape of US auditing · signalling in the OTC market · mandatory
ISSB reporting Türkiye.

Venue tally: JAR 4 · TAR 4 · RAST 4 · Management Science 2 · CAR 2 · JAE 1 · JEEA 1 ·
**RFS 1**.

## Tier 2 — RE/finance exemplars

Pending venue calibration. Target ~8, weighted toward:

- Energy-label / green-building capitalisation in housing (the direct empirical neighbours)
- Information and disclosure in real-estate markets
- Structural papers that placed in top finance, to calibrate how the model gets sold
- At least one paper with a policy/counterfactual section, to calibrate the §7 rewrite
