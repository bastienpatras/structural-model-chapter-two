# Humanizer, advisory: appendix prose by part (2026-11-04)

Status: ADVISORY. Nothing below is applied. Method: a pattern scan of each part's prose lines (equations and comment lines excluded) for the humanizer's tells (not-X-but-Y, dashes, stock words, staged openers, one-line closers, "sayings"), then a read of the flagged lines. `--` in the scan is mostly LaTeX range notation (A--D, 2022--2024), which is correct and not a tell. Where a prose edit would paper over a substantive finding, the substantive fix comes first (see the part reports).

## P1, P2, P3, P4 (A-attention.tex)
Clean. The flagged "not only", "rather than" and "exactly" are real contrasts or precise qualifiers (L49, L64, L391, L408, L769), the dashes are ranges, and proof steps are written as plain derivations. No edits suggested.

## P5 (A-benchmark.tex, main.tex Proofs)
- A-benchmark L105 "the cleanest pool imaginable ... precisely because": inflation and an intensifier. Suggest: "even against the cleanest pool the model allows, one made up entirely of uninformed sellers drawn from the unconditional quality distribution ... through the cost c0, because uninformed sellers keep silence from ever carrying that worst-type inference."
- A-benchmark L107 "once every strategic hider has already piled in": colloquial. Suggest: "even once every strategic hider has already hidden."
- A-benchmark L111 "What makes this regime useful is that the equilibrium premium equals c0 exactly, and stays there regardless of pi or rho. That invariance is just the indifference condition doing its job.": staging plus a figure of speech. Suggest: "In this regime the equilibrium premium equals c0 exactly, whatever pi or rho. This follows from the indifference condition: the price gap between the non-disclosing pool and disclosed low quality has to equal the hiding cost, or the marginal seller would strictly prefer one action." Also the final sentence claims pi, rho and c0 "are all jointly identified" in this regime, which conflicts with the identification results (rho is not identified apart from omega1): a substantive fix first (P6 F2).
- A-benchmark L165 "pocket the full premium c0 as a pure rent": the claim is wrong in the benchmark (P5 #5), so fix before editing prose.
- main.tex L559: "silence is uninformative rather than damning" is a real contrast (keep).

## P6 (A-robustness.tex)
- L298 "One free parameter is matched to one observed moment --- the hiding rate among informed low-quality sellers, a group the registry identifies precisely --- and the match is exact.": a pair of em dashes (the file's only true dashes). Suggest: "One free parameter is matched to one observed moment, the hiding rate among informed low-quality sellers, and the match is exact." The clause "a group the registry identifies precisely" is contradicted by tab:robustness (P6 F10), so it goes.
- L300 "Buyer sensitivity emerges from the anchor as a genuine point estimate": "emerges" and "genuine" are inflation, and the claim overreaches (P6 F2). After the substantive fix: "The anchor gives a point estimate of rho omega1 in each market."
- L67 "buyer sensitivity is exactly insensitive to the sigma1 assignment": awkward and redundant. Suggest: "the anchored estimate of buyer sensitivity does not depend on the sigma1 assignment."
- L80 "the restriction ... is not satisfied exactly, but the model's predicted": a real contrast (keep).
- The nine other "rather than" hits are substantive contrasts (keep).

## P7 (main.tex L359-428)
- L411 "The key identification advantage is that we directly observe the latent variable K ... so we can separately identify the behavior of informed and uninformed sellers.": "key", a staged advantage, and an overclaim (K is a registry record, P7 #2). Suggest: "The registry match gives us K, the seller's information status, which buyers do not observe, and lets us identify the behavior of informed and uninformed sellers separately." Edit only together with the definition fix.
- L383 "key" appears in a description of the registry; fine.

## Not touched
Equations, proofs, tables, labels, macros, and every sentence not listed above. As in `.claude/rules/writing-with-ai.md`: a humanizer pass improves readability; it cannot change what a detector sees, and the prose that carries the argument stays yours to rewrite.
