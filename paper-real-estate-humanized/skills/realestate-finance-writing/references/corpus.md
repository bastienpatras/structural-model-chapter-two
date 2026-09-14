# Provenance and Confidence

Read this before treating any rule in this skill as authoritative. The rules differ in how
well grounded they are, and the difference matters.

## What was actually read

Three papers, in full text, all by Thomas Bourveau and co-authors:

| Paper | Venue | Role in the distillation |
|---|---|---|
| Bourveau, Breuer & Stoumbos, "Learning to Disclose: Disclosure Dynamics in the 1890s Streetcar Industry" (74pp) | **Review of Financial Studies** 38(9), 2025 | ★ Primary source. A *structural disclosure paper in a top finance journal*. Nearly all of `introduction.md` and `model-presentation.md` derives from it. |
| Boulland, Bourveau & Breuer, "Company Websites: A New Measure of Disclosure" | Journal of Accounting Research 64(1), 2026 | Structure cross-check; measurement-validity conventions |
| Bourveau, Kepler, She & Wang, "Firm Boundaries and Voluntary Disclosure" | The Accounting Review 99(4), 2024 | Structure cross-check; the §2 "Conceptual Underpinnings" pattern |

Section structure was verified across all three and is consistent. The six-section
architecture, the conceptual §2, the placement of data before analysis, and the §5
alternatives-and-robustness pattern all replicate.

## Confidence levels

**Well grounded — verified across the corpus:**

- Six-section architecture
- §2 as conceptual framing rather than literature review; no equations in §2
- Data placed with the institutional setting, before the analysis
- No standalone literature review; related work distributed into contribution paragraphs
- No roadmap paragraph
- §5 as alternatives + estimation choices
- The hedging asymmetry (flat on facts, hedged on mechanisms)
- Enumeration in prose; dense `e.g.` citation clusters; substantive long footnotes

**Well grounded but from a single source** — all from the RFS paper, which is the only
top-finance placement available and therefore the only direct evidence on finance conventions:

- The full introduction funnel, paragraph by paragraph
- The assumption audit (a)–(d)
- "We allow, but do not impose"
- "Does not take a stance on"
- The scope disclaimer
- The nested-model fit comparison
- Closing the introduction on generalizability

Treat these as strong but not triangulated. They come from a paper that cleared *RFS*, which
is the relevant bar, but a single observation of it.

**Provisional — general knowledge of the field, NOT yet corpus-verified:**

- Anything specific to *real-estate* outlets (*Real Estate Economics*, *JREFE*, *JUE*):
  hedonic-specification conventions, tolerance for institutional description, house-style
  norms
- Table and exhibit conventions
- Abstract conventions, including whether economic magnitudes belong in the abstract
- Internet-appendix norms
- The claim that finance conventions are *stricter* than real-estate conventions and
  therefore dominate the front matter

## The gap you should be aware of

**Bourveau's corpus is 18/19 accounting journals.** Venue tally across his published work:
JAR 4, TAR 4, RAST 4, Management Science 2, CAR 2, JAE 1, JEEA 1, **RFS 1**.

So this corpus is authoritative on *how to make a disclosure-regulation research design
credible*, and thin on *real-estate and finance venue norms specifically*. The one RFS paper
is doing a lot of work here.

Until real-estate and finance exemplars are added, apply the "provisional" rules with
judgement and say so when doing it. Do not present a provisional rule to an author as though
the corpus established it.

## Papers identified as priorities but not yet acquired

SSRN blocks automated access (403, Cloudflare, even with a browser user-agent), so these
require manual download:

- **Bourveau, Garel & Petit-Romec, "Mandatory Carbon Disclosure: Evidence from France"** —
  mandatory environmental disclosure in a French setting; the nearest neighbour to
  housing-EPC-disclosure work and a likely citation for any such paper
- Bourveau, Gao, Li & Zhou, "Comply-or-Explain Regulation and Investor Protection" (JAE 2025)
- Bourveau, Lauer & Zipperer, "Stock Market Reaction to Product-Level Carbon Estimates"
- Bourveau, De George, Ellahie & Macciocchi, ICOs (JAR 2022)
- Bourveau, Gao & Hope, Canada Business Corporations Act (CAR)

## Working access routes

| Source | Status |
|---|---|
| `thomasbourveau.github.io` | ✅ open |
| `business.columbia.edu/.../pubfiles/*.pdf` | ✅ open (static PDFs only) |
| `ora.ox.ac.uk/objects/uuid:.../files/<id>` | ✅ open |
| `business.columbia.edu` and `ora.ox.ac.uk` HTML/search | ❌ 403 |
| SSRN, all endpoints | ❌ 403 |
| Publisher sites | 🔒 paywalled |

Discovery path that works: web-search for the title to surface an openly-hosted
working-paper copy (Columbia `pubfiles`, Oxford ORA, conference sites), then `curl` it
directly.
