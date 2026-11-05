# §3 The French Energy-Performance Disclosure Regime — diagnosis and change log

Draft: `03-setting-draft.tex` (23.6k chars). **Already wired into `main.tex`** — see wiring below.

## Diagnosis

Three problems, all structural rather than substantive:

1. **Data sat at §5, after the model and the equilibrium analysis.** The corpus places data with
   the institutional setting, before any model. A Data section appearing after the model is the
   single clearest tell that a paper was written for a different field.
2. **The institutional background was buried inside the identification section**, as the opening
   paragraph of §6.1. It is the best paragraph in the paper on what the reform actually did, and
   it was invisible to anyone reading the setting.
3. **The stylized facts stood alone as §2**, disconnected from the data that produced them, so a
   reader met the facts before knowing where they came from.

None of this is a writing problem. The material is good; it was in the wrong order.

## Structure

| New | Content | Origin |
|---|---|---|
| §3 opening | What the section does; **apartment-first framing stated explicitly** | New |
| 3.1 Institutional Background | What a DPE is, who certifies it, why the registry matters · the reform · **what the reform did *not* change** | New prose + relocated paragraph |
| 3.2 Data and Measurement | Framing · 3.2.1 Sources and Sample Construction · 3.2.2 Four-Group Classification · **measurement-validity paragraph** | New prose + relocated §5 |
| 3.3 Stylized Facts | Four facts as 3.3.1–3.3.4, figures intact | Relocated §2 |
| 3.4 What the Facts Demand of the Theory | unchanged | Relocated §2 |

Assembled **programmatically** — the institutional paragraph, both data subsections, and all four
facts were extracted and spliced rather than retyped, so no transcription error is possible. 10
figures carried across intact.

The four facts were demoted from `\subsection` to `\subsubsection` so §3 has the corpus's
three-part shape. Nothing was cut and every fact keeps its own heading and figure.

## New prose (three passages)

1. **§3 opening** — states the apartment-first decision on the record: same qualitative patterns
   in both segments, but apartments have lower audit coverage, more strategic concealment, and the
   stability across the reform that identification exploits.
2. **3.1 closing, "what the reform did not change"** — the disclosure obligation and its attached
   liability predate July 2021 (*loi ALUR*, Art. L271-4 CCH), so the cost of withholding straddles
   the reform unchanged while the value of a *disclosed* grade jumps. And the E/F/G rental ban
   gives the binary quality split a regulatory anchor rather than an arbitrary cutoff. Both claims
   are the paper's own, relocated from §6.1 and from the §4 preamble; only the framing is new.
3. **3.2 closing, measurement validity** — three properties of the match: it is administrative
   rather than self-reported, so it cannot be strategically misreported; it needs a geocoded
   address, so the matched sample is the address-locatable subset; and **it fails asymmetrically**.

## ⚠ One addition that is mine and needs verification

The asymmetric-measurement-error argument in 3.2 is **my inference, not something I found in the
paper**: a listing can fail to match a certificate that exists (a false uninformed seller), whereas
a false positive requires coincidence in address, property type, area, *and* floor simultaneously —
so false negatives should dominate, making the measured informed share a lower bound and the
measured strategic-hiding share conservative.

If that holds it is a strong paragraph, because the direction of measurement error works *against*
the paper's own finding, which is the most persuasive position to be in. **But it is a claim about
your matching algorithm and I cannot verify it from the paper.** Confirm, correct, or cut.

## Wiring already applied to `main.tex`

1. Old `\section{Setting and Stylized Facts}` block removed (16.0k chars) → replaced by the `\input`
2. Old `\section{Data}` block removed (4.3k chars); its `\label{sec:data}` **carried onto §3.2**,
   because 4 live `\ref{sec:data}` calls depend on it
3. Institutional paragraph deleted from the identification section (656 chars)
4. **Dangling reference repaired:** that section then opened "This shift is the source of
   identification…" with its antecedent gone. Now reads "The change in the legal status of the DPE
   described in Section~\ref{ss:institutions}…" and renders as "Section 3.1"

`main.tex` 160.0k → 139.1k chars. Compiles clean: 0 errors, 0 duplicate labels, 0 unresolved
references or citations.

## Section count

Was 9, went to 10 when §2 was added, now back to **9** with Data folded in. Target is 7; the §4
consolidation (Model + Equilibrium + Identification + Results → "A Structural Interpretation")
takes it to 6, and the policy section keeps it at 7 by design.

## Deferred

- The apartment-first reweighting is stated in the §3 opening but the **individual fact paragraphs
  still present both segments even-handedly.** Reordering each to lead with apartments is a
  sentence-level pass I have not done; worth doing once the v2 data questions settle, since some of
  those numbers will change anyway.
- The pre-reform level-premium sentence (v2 item 4) belongs in 3.3.1 and is not yet added.
