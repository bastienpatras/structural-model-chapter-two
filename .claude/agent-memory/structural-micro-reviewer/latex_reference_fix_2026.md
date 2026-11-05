---
name: latex-reference-fix-2026
description: Documents the undefined-reference fix applied to main_concise.tex on 2026-05-16: cor:rho, prop:pi, prop:c0 were missing from the main body
metadata:
  type: project
---

The appendix proofs section in `paper/main_concise.tex` had three subsection headers that referenced labels not defined anywhere in the main body:

- `\ref{cor:rho}` — referenced at lines 1226 and 1265 (post-fix line numbers shift)
- `\ref{prop:pi}` — referenced at line 1245
- `\ref{prop:c0}` — referenced at line 1268

**Why:** These were appendix-standalone proofs of supplementary results (regime-transition effects of $\rho$, $\pi$, $c_0$) that had been written without corresponding labeled environments in the main body. The existing `prop:comparative_statics` captured the signs of comparative statics but not the regime-transition content that these three proofs demonstrate.

**Fix applied (2026-05-16):** Added three new labeled environments in the main body immediately after `prop:comparative_statics` and its discussion block (around line 435 in the post-fix file):
- `\begin{corollary}[Effect of $\rho$...]\label{cor:rho}` — two parts: weakly increasing premium across regimes; partial-pooling interval expands with $\rho$
- `\begin{proposition}[Equilibrium effect of $\pi$]\label{prop:pi}` — $\pi$ increase narrows Complete Adverse Selection region
- `\begin{proposition}[Equilibrium effect of $c_0$]\label{prop:c0}` — $c_0$ increase pushes toward Cost-Deterred Hiding; reduces $\sigma_0^*$ in interior

No mathematical content of any proof was changed. The appendix proof headers were already correct and needed no editing once the main-body labels existed.

**How to apply:** If the appendix is restructured or these environments are moved, ensure the three labels (`cor:rho`, `prop:pi`, `prop:c0`) remain in the main body. The inline reference `Corollary~\ref{cor:rho}(ii)` at line 1289 (within the appendix text, between proofs) requires `cor:rho` to exist; it is not a dangling citation to a main-body result.

Related: [[project_overview]]