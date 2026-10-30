# Playground notes: the non-disclosure premium & EPC predictability

*2026-10-05 · branch `review` · plan: `quality_reports/plans/harmonic-munching-lecun.md`.*
*Produced with two `micro-theorist` agents (Task 1 and Task 2 run separately), then assembled and spot-checked. No paper or model code was edited.*

---

## Read this first

**Task 1, in five lines**

1. **Why the current model can't generate the premium.** It prices a silent listing at $\rho\beta_1 e$ with $e\in[0,1]$, so a silent listing can never sit above a disclosed A–D listing (Props. 1–2; this also holds under exact logit pricing).
   - In the apartment index, silent listings sit **+7.0 log points above A–D post-reform**, in 93% of markets.
   - The binding constraint is $D\le B$, not $\lambda=0$ (§1.1).
2. **Your correlated-quality fix, $\mathrm{Cov}(\xi,\theta)$ alone, is neutral for the wedge.**
   - With no selection on $\xi$ beyond $\theta$: $\Delta=eB$, hence $\lambda=0$, for *any* correlation.
   - The Haussmann sign ($\mu<0$) even works *against* the premium (Cor. 3a).
   - Exploratory regressions find no silent premium in pre-1915 stock.
3. **Belief-based anchoring (cursed/naive buyers, motivated skepticism, salience of a bad letter) is capped.** At most 1.65 of the 6.1-point wedge; the cursed case gives ≈0.13. The reason: the silent pool is ~94% *uninformed* sellers, so the Bayesian belief is already close to the prior (Props. 4–5).
4. **What can work: unobserved quality correlated with information status $K$** (κ, Cor. 3b). In exploratory listing regressions, uninformed silent apartments trade **+18.7** above E–G within neighbourhood×vintage cells. The premium is concentrated in **missing-vintage and post-2004** listings, and is ≈+1 in known pre-2004 stock. Informed hiders price near their *true* registry grade (transparency ω≈0.58).
5. **Recommendation.**
   - First test whether the apartment DiD is a *composition* effect (new-build/incomplete listings in the "no letter" category, test R4).
   - Then add κ and ω (both point-identified).
   - Keep χ/salience as *bounded* robustness.
   - Keep shrouded energy-cost levels ($m_0$) as the only behavioural channel that can reach the magnitude. It is a secondary hypothesis with a Jan-2022 timing test.

**Update after Bastien's follow-up: the attention mechanism, Part II (§A).** Silence is priced against a *default* energy cost, not a belief. This breaks the cap iff the default is optimistic. Relative attention to silence is $a\approx0$ for apartments and $\approx1$ for houses [E]. It is identified by the pass-through of the silent pool's registry-measured cost into the silent price.

**Part VI, policy section re-done under limited attention (computations and figures, 2026-10-09).** Fit improves in level, not in cross-section; thresholds and subsidies barely change; salience is a knife-edge. See VI.2 to VI.4.

**Part V, policy under limited attention (re-derivation, 2026-10-08).** The §5.6 text in the paper is largely wrong; see V.0 for the verdict, V.6 for the claim-by-claim audit and V.8 for replacement statements and decisions. Paper not yet changed.

**Part IV, the attention extension written as paper text (full-model version).** This is a draft of §4.6 "Limited Attention to Silence" at the depth of §4.2–4.3: setup, equilibrium, comparative statics, welfare, identification, estimates and policy, plus Appendix A-ATT with proofs. Bracketed numbers are provisional until gate checks G1–G3 are run.

**Part III, the attention extension (read this one).** This is the complete, pedagogical write-up of the attention extension: model, propositions with proofs, levels vs DiD, estimation recipe, results, policy, gate checks and draft LaTeX. Where it differs from Part II (§A), Part III wins; its §0.4 lists every revision.

**Task 2, in three lines**

1. **Design.**
   - Nested buyer-visible feature sets (F0–F4).
   - Binary logit for θ (the model's object) + ordered logit (main for letters) + MNL + GBM (upper bound).
   - Folds grouped by building, plus a temporal split.
   - Metrics: information gain, AUC, $R^2_\theta$, calibration and decision metrics.
2. **Selection fix.** Train θ̄(X) on **all registry-matched listings (K=1, any d)**, not just disclosers. Evaluate on the **28,220 / 7,257 informed hiders**, whose registry letter is known. The calibration intercept there estimates $\log(\sigma_1/\sigma_0)\mid X$.
3. **Link to Task 1.** θ̄(X) is exactly the anchor in the cursed belief (E3), and it fixes the θ-mix needed to identify κ. If $\sigma_1=\sigma_0$, then χ is **not identified**.

**Spot-checks I ran on the agents' numbers** (all reproduce):
- Index DiDs (Task 1's `levels.py`): apartments 4.06/8.53 (45 mkts) and 1.69/6.92 (81 mkts); houses 5.82/3.89 and 5.07/3.41. These match Table 4 and the 6.9/3.4 headline.
- Task 2's sample counts, duplicate `listing_id` rows, and 74.0%/91.2% letter agreement.
- **Not** independently re-run: Task 1's listing-level FE regressions (`reg.py`, `reg2.py`). Treat the **[E]** numbers as exploratory until they are rebuilt in the pipeline.

**Coverage checklist (your brief → section)**

| Brief item | Section |
|---|---|
| T1.1 Why the model can't produce the premium | §1.1 (Props. 1–2, identity 1.2) |
| T1.2 Correlated ξ: sign/size, plausibility, green-premium distortion | §1.2 (Prop. 3, Cor. 3a–3d, exploratory table) |
| T1.3 Behavioural alternatives + literature | §1.3 (i)–(vi), refs §1.7 |
| T1.4 Recommendation + discriminating tests | §1.4 (table, R1–R8), §1.5 |
| T1.5 Minimal equation changes + identification | §1.6 (E1–E8, identification map) |
| T2 Sample / features | §0, §2.1.2–2.1.3 |
| T2 Models | §2.1.4 |
| T2 Metrics + CV | §2.1.5–2.1.7 |
| T2 Caveats: selection, non-disclosers, use as a model moment | §2.2 |
| T2 Draft appendix + table + figures | §2.3 |
| Open questions | end of file |

**Labels:**
- **[D]** derived
- **[A]** assumption
- **[C]** conjecture
- **[E]** exploratory number, not paper-grade
- **[CHECK]** unverified fact or citation

---

## Task 1: Why silence beats a bad letter, and what that requires of the model

*Working note on the apartment non-disclosure premium for "When Silence Pays". It answers the faculty "anchoring" suggestion and Bastien's correlated-quality suggestion. No repo file was edited. All computations ran from the scratchpad (scripts listed in §0.3).*

**Status labels used throughout.**
- **[D]** derived here, with the proof or the sympy check given.
- **[A]** maintained assumption.
- **[C]** conjecture or speculation.
- **[E]** exploratory number computed for this note from repo data. It is not a paper number. Re-run it in the pipeline before quoting it.
- **[CHECK]** a citation or institutional fact I could not fully verify.

---

### 0. Summary, sources, notation

#### 0.1 Summary

1. **The binding restriction is "silent is priced no higher than verified-high", and the test is not $\lambda$.** In the current model, any mechanism that works through beliefs about $\theta\in\{0,1\}$ or through the price of the disclosed-low listing gives a level silent–low gap no larger than the high–low gap. This holds market by market and period by period, in both the linear and the exact logit pricing model. On the apartment estimation sample, the within-market level gaps from the index panel violate it in **93% of markets post-reform**. The silent group sits **+7.0 log points above disclosed A–D**, and the violation is already present pre-reform (+2.6) [E].
2. **Behavioural belief channels are quantitatively capped.** Any belief rule that keeps $\tilde e\in[0,1]$ (cursed, naive mixture à la Hagenbach–Koessler, motivated beliefs à la Hagenbach–Saucet, Jin–Luca–Martin-style under-skepticism), plus any extra penalty on a displayed *bad* letter (the literal "anchoring" story), can produce at most $\hat\lambda\le(1-\hat e^*)\hat\beta_1=1.65$ of the 6.1-point wedge (27%). Reversion to the prior, which is the cursed/naive case, gives at most $\hat\beta_1(\bar\theta-\hat e^*)\approx0.13$, because the silent pool is 94% uninformed. Bayesian and naive beliefs therefore nearly coincide.
3. **Correlation between unobserved quality and $\theta$ is neutral for the wedge.** If $\xi$ is correlated with $\theta$ but there is no selection on $\xi$ given $\theta$, then $\Delta=e\cdot B$ exactly for any correlation, so $\lambda=0$. The Haussmann sign, $\mathrm{Cov}(\xi,\theta)<0$, lowers both gaps proportionally. Pre-1915 apartments show **no** silent premium within neighbourhood × vintage cells [E].
4. **What can work is selection on $\xi$ through information status $K$.** The wedge equals $\lambda=\kappa\cdot\Pr(K=0\mid d=0)+\dots$. In the 2022–24 listing cross-section [E], uninformed silent apartments ($K=0$) trade **+18.7** above disclosed E–G within neighbourhood × vintage cells. Informed hiders ($K=1$) trade near their *true registry grade*. Buyers cannot see $K$, so this 17-point gap between two kinds of silent listing cannot come from buyer beliefs. The premium sits entirely in listings with **missing construction year (+22.3)** or **post-2004 vintage (+18.8)**. With known pre-2004 vintage it is **+1.2**, inside the Bayesian hull.
5. **Recommendation.** Before adding any behavioural layer, establish whether $\hat\Delta$ is a composition effect of the "no letter" category (new-build or off-plan programmes, incomplete listings). If it is, the minimal fix is a $K$-dependent unobserved-quality shifter $\kappa$, plus a partial-transparency parameter $\omega$ for informed hiders. Both are point-identified from data already in the repo. The only behavioural channel that can reach the magnitude is **shrouded energy *cost levels*** (inattention to costs that are not displayed, with the € cost display mandatory from 1 Jan 2022). It is identified only with an exclusion restriction, and the vintage split contradicts it as a uniform mechanism. Treat it as a secondary hypothesis with a sharp timing test.

#### 0.2 What I read (file:line)

- **Model** (`paper-real-estate/sections/04-structural-draft.tex`):
  - buyers observe $(d,p,X)$, not $K$: :86
  - valuations, the $\alpha_k=\beta_k$ benchmark and demand: :114–126
  - $K\perp\theta$: :136–138
  - beliefs: :172–176, :216–221
  - $\Phi$ and $\Delta(e)=\rho\beta_1e$: :225–229
  - regime premia: :265–278
  - registry belief $\hat e^*$: :391–396
  - anchored estimator: :418–424
  - over-identifying wedge: :428
  - Table 4: :450–462
  - candidate explanations: :555–589
- **Price derivation** (`paper-real-estate/main.tex`): $p_0^*-p_1^*=\rho\beta_1 e$ at :485–487. It normalises $v_0=\beta_0$, i.e. $\delta=\beta$. Lemma A.1 is at :396.
- **Code:**
  - `src/model.py`: valuations :117–130; demand :136; seller profit :173–198, which uses $\phi(p)=\gamma_0+\gamma_1 p$ with $p$ the **log** price; linear hiding gain :342; structural gain :345–371, whose docstring says $e^{p}\Gamma(p)$, see the Aside in §1.1.
  - `src/event_study.py:252–253,269–270`: the paper's $\hat\beta_1,\hat\Delta$ are post-minus-pre means of within-market **index** gaps, A–D versus E–G and "Missing" versus E–G.
  - `src/rho_identification.py:71–150` (anchor) and `src/data_prep.py:428–490` (consumption gap from registry letters of $K=1$ listings).
  - `config_apartment.json:28` and `config_house.json:26` still set `"hider_theta": "impose_zero"`. The $\sigma_1$ circularity flagged in `FINDING-sigma1.md` is therefore still active in the published configuration.
- **Notes:**
  - `paper-real-estate/FINDING-sigma1.md`: $\hat\sigma_1\approx\hat\sigma_0$; hiding is U-shaped and lowest at D.
  - `V2-QUEUE.md`: $K=0$ means "no post-July-2021 registry certificate". 32% of apartment listings are disclosed with no match.
  - `DIAGNOSIS.md`.
  - `03-setting-draft.tex:129`: the national level figure has Non-disclosed > A/B/C > E/F/G.
- **Literature PDFs** (both read):
  - Hagenbach & Saucet (ReStud 2025): §1–2.3, motivated-belief model; beliefs constrained to be *consistent with the message*.
  - Hagenbach & Koessler (RED 2017): §1–4; naive receiver plays $E(t)$ after no disclosure; Prop. 1 thresholds.
- **Web:** NBER w35625 and Ginger Jin's research page, both fetched (§1.3 and §1.7).

#### 0.3 Scratchpad scripts (all read-only on the repo)

`levels.py` and `levels2.py` (index level gaps), `reg.py` and `reg2.py` (listing-level FE regressions), `energy.py` (consumption levels, registry hider grades), and `checks.py`, `checks2.py`, `checks3.py` (sympy and numerical checks). All live in the same scratchpad directory as this file.

#### 0.4 Notation

Disclosure groups:
- $H$: disclosed A–D.
- $L$: disclosed E–G.
- $N$: no letter, $d=0$.

For market $m$ and month $t$, $\bar p_{g,mt}$ is the log hedonic reference price per m² (Chapter-1 index). Define the level gaps
$$B_{mt}\equiv\bar p_{H,mt}-\bar p_{L,mt},\qquad D_{mt}\equiv\bar p_{N,mt}-\bar p_{L,mt}. \tag{0.1}$$
The paper's estimands are DiDs of period means:
$$\hat\beta_{1,m}=\bar B_{m}^{\rm post}-\bar B_m^{\rm pre},\qquad \hat\Delta_m=\bar D_m^{\rm post}-\bar D_m^{\rm pre}.\tag{0.2}$$
These come from `event_study.py:269–270`. They are **not** the listing-level hedonic coefficient of `src/hedonic.py`, which is a cross-sectional object used for scale calibration and starting values.

Further notation:
- $e\equiv\Pr(\theta=1\mid d=0)$ is the Bayesian pool belief. $\tilde e$ is the belief buyers actually price.
- $\lambda\equiv\Delta-eB$ is the paper's over-identifying wedge (04:428).
- $\xi$ is unobserved (to the econometrician) quality, priced by all buyers.

---

### 1.1 Diagnosis: why the current model cannot generate the premium

#### Proposition 1 (convex-hull bound, linear pricing) [D]

**Assumptions.**
- (A1) **Price = expected valuation (main.tex:485).** $p_g=\beta_0+X'\beta+\rho\beta_1\tilde\theta_g$, where $\tilde\theta_g$ is EPC-sensitive buyers' expected $\theta$ for a group-$g$ listing at reference $X$.
- (A2) **Bayes, with no falsification (04:83).** $\tilde\theta_H=1$, $\tilde\theta_L=0$, $\tilde\theta_N=e\in[0,1]$.
- (A3) **No unobserved quality.** The index's reference price conditions on everything that is priced except $\theta$.

**Statement.** In every market-period,
$$D_{mt}=e_{mt}B_{mt},\qquad 0\le D_{mt}\le B_{mt}. \tag{1.1}$$

**Proof.** We have $B=\rho\beta_1(1-0)$ and $D=\rho\beta_1(e-0)$, and $e\in[0,1]$ because it is a conditional probability. Sympy confirms $1-e=\frac{(1-\bar\theta)(1-\pi+\pi\sigma_0)}{H}\ge0$, where $H$ is the silent mass. $\square$

**Corollary 1 (estimand mapping) [D].** Average (0.2) over months.
1. If the pool belief is stable across the reform ($e_{\rm pre}=e_{\rm post}=e$), then $\hat\Delta=e\hat\beta_1\le\hat\beta_1$. Stability is what the paper's "flat undisclosed share" argument invokes (V2-QUEUE item 5).
2. Without stability, $\hat\Delta-\hat\beta_1=(1-e_{\rm pre})B_{\rm pre}-(1-e_{\rm post})B_{\rm post}$. This can be positive only if the silent-versus-high gap *shrank*.
3. In all cases $\hat\Delta=D_{\rm post}-D_{\rm pre}\le B_{\rm post}$, using $D_{\rm pre}\ge0$.

Inequality 3 needs no assumption on $\rho_{\rm pre}$, on $e_t$, or on regime changes. It is the robust test.

**Consistency remark [D].** Under the paper's maintained assumptions, $c_0$ is invariant across the reform (04:361) and both periods are in Partial Pooling. Equation (04:265–278) then gives $D_{\rm pre}=D_{\rm post}=c_0$, so $\hat\Delta=0$. The over-identifying test $\hat\lambda=\hat\Delta-\hat\beta_1\hat e^*$ reads a DiD as if it were a post-reform level. That is legitimate only if the pre-period premium was negligible: $\rho_{\rm pre}\approx0$, Cost-Deterred regime with $D_{\rm pre}=\rho_{\rm pre}\beta_1\bar\theta\approx0$. The data in Table 1 contradict this for apartments ($D_{\rm pre}=4.5$). This should be stated in §4.4.

#### Proposition 2 (exact logit pricing) [D]

**Setup.** Demand is
$$\Gamma(p;v_1)=\rho G\!\big(\tfrac{v_1-p}{\varsigma}\big)+(1-\rho)G\!\big(\tfrac{v_0-p}{\varsigma}\big),$$
with $G$ logistic, and the seller solves $P^*(v_1)=\arg\max_p \phi(p)\Gamma(p;v_1)$ for any increasing $\phi$. This covers both the code's $\phi(p)=p$ and the docstring's $e^{p}$.

**Statement.**
- (a) $\Pi^*(v_1)$ is nondecreasing in $v_1$.
- (b) Suppose $\rho G_1^2+(1-\rho)G_0(2G_1-G_0)\ge0$ at the relevant prices, where $G_j\equiv G((v_j-p)/\varsigma)$. This holds in particular whenever $v_1\ge v_0$, which is true for every $d$ under the paper's normalisation $v_0=\beta_0$ (main.tex:485). Then $P^*$ is nondecreasing in $v_1$. Hence
$$P^*(v_1(e))\le P^*(v_1(1)),\qquad P^*(v_1(e))-P^*(v_1(0))\le P^*(v_1(1))-P^*(v_1(0)),$$
i.e. $0\le D\le B$ holds exactly, not just to first order.

**Proof.**
- (a) Envelope theorem: $\partial\Gamma/\partial v_1=\rho g_1/\varsigma\ge0$.
- (b) $\log\Pi=\log\phi(p)+\log\Gamma(p;v_1)$, and only the second term has a cross-partial. Using $g=G(1-G)$ and $g'=g(1-2G)$:
$$\frac{\partial^2\log\Gamma}{\partial p\,\partial v_1}=\frac{\rho g_1}{\varsigma^2\Gamma^2}\Big[\rho G_1^2+(1-\rho)G_0(2G_1-G_0)\Big].$$
  When this is nonnegative, $\log\Pi$ has increasing differences, and Topkis / Milgrom–Shannon gives monotone $P^*$. If $v_1\ge v_0$ then $G_1\ge G_0$, so $2G_1-G_0\ge G_1>0$. $\square$

**Numerical check [D].** Global grid search over $\rho\in[.05,.95]$, $\varsigma\in\{.1,.3,.6,1\}$, $v_0,v_1\in[8.2,8.6]$:
- With $\phi=p$: no decreasing step in 960 cases, and pass-through $dP^*/dv_1\in[0,0.99]$.
- With $\phi=e^p$: 5 of 960 steps decrease, all with $\varsigma=0.1$, $v_0-v_1\ge0.3$ and $\rho\le0.25$. These are segment-switching cases where the seller abandons the sensitive segment, and they lie outside the paper's $v_1\ge v_0$ region.

Monotonicity alone delivers $D\le B$. The stronger claim $D\le\rho\beta_1$ additionally needs pass-through $\le1$. That holds on the grid for $\phi=p$ but is not proven in general.

**Aside, not fixed.** `model.py:173–198` implements $\phi(p)=\gamma_0+\gamma_1p$ with $p$ in **log** units, so revenue is linear in *log* price. The docstring at :345–360 and the paper's payoff (04:100–104) describe something else. The robustness variant therefore does not compute what its docstring says.

#### Confronting Proposition 1 with the data [E]

The table below gives within-market level gaps from `data/index_*.csv`, using the paper's A–D grouping, 20-transaction volume filter and pre/post windows (`levels.py`). It reproduces Table 4 Panel A exactly: 4.06/8.53 and 5.82/3.89.

| | $B_{\rm pre}$ | $B_{\rm post}$ | $D_{\rm pre}$ | $D_{\rm post}$ | $D-B$ pre / post | share of mkts with $D_{\rm post}>B_{\rm post}$ |
|---|---|---|---|---|---|---|
| Apartments, est. sample (45) | 1.97 | 6.03 | 4.54 | **13.06** | +2.56 / **+7.03** | **93%** |
| Apartments, all (81) | 0.68 | 2.37 | 10.11 | 17.03 | +9.42 / +14.65 | 90% |
| Houses, est. sample (97) | 7.48 | 13.30 | 3.88 | 7.77 | −3.60 / −5.53 | 34% |

Splitting the high group shows **silent apartments sit above A/B/C, not only above D.** In levels, A/B/C − E/F/G is 6.95 → 11.62, D − E/F/G is −1.36 → +1.45, and silent − E/F/G is 4.54 → 13.06. In DiD terms, silent gained 3.9 log points on A/B/C and 5.7 on D.

**Reading the table.**
- Apartments violate (1.1) in levels, both before and after the reform.
- The DiD test $\hat\Delta=8.53>B_{\rm post}=6.03$ violates Corollary 1(3) even under the most favourable $D_{\rm pre}=0$.
- Houses sit inside the hull. Their price-implied level belief is $D/B=0.58$ post, against $\hat e^*=0.60$, which is remarkably close.

#### The key identity [D]

Both gaps are measured against the same base $L$, so
$$\Delta-B=\bar p_N-\bar p_H,\qquad \lambda=(\Delta-B)+(1-e)B. \tag{1.2}$$

**Anything that moves only the disclosed-low price cancels from $\Delta-B$.** This includes salience of a bad letter, *passoire* stigma, the rental ban, and investor exit. Such a mechanism can raise $\lambda$ at most through the $(1-e)B$ term.

On the apartment estimation sample, $\hat\lambda=6.1$ decomposes as:
- $\hat\Delta-\hat\beta_1=4.47$, which requires **silent to beat verified A–D**;
- $(1-\hat e^*)\hat\beta_1=1.65$, which is reachable by belief or low-letter channels.

#### What breaks the bound [D]

$D>B$ requires the priced value of a silent listing to exceed the priced value of the average A–D listing. With $\tilde\theta_N\le1$, this needs one of the following:
1. **A price-relevant component of silent listings outside the hull spanned by disclosed listings.** That is unobserved quality with $E[\xi\mid N]>E[\xi\mid H]$ conditional on $X$, or a change in it across the reform for the DiD.
2. **Displayed *high* letters priced below their fundamental relative to silence.** Examples are A–D letters read as bad, or displayed € costs that are fully weighted while undisplayed costs are neglected (§1.3 (iv)).
3. **A non-buyer channel in the outcome.** These are *listing* prices, so seller-side over-listing by silent sellers would show up here (§1.3 (vi)).

Non-Bayesian beliefs about the binary $\theta$ are *not* sufficient on their own. This is the same logic as Hagenbach–Saucet's constraint that beliefs remain consistent with the message: silence has support $\{0,1\}$, so $\tilde e\le1$.

---

### 1.2 Correlated unobserved quality

#### Setup [A]

Add $\xi$ to both buyer types' valuations. It is observed by buyers, not by the econometrician, and is priced one-for-one:
$$v_1=\beta_0+\beta_1\tilde\theta+X'\beta+\xi,\qquad v_0=\beta_0+X'\beta+\xi.$$
Group mean prices then pick up $E[\xi\mid g,X]$.

Write $\bar\xi_{K\theta d}\equiv E[\xi\mid K,\theta,d,X]$. The cell masses are those of Table 1 of the paper (04:154–159). Define:
- disclosed-group means $\bar\xi^D_\theta\equiv\bar\xi_{1\theta1}$;
- the silent-pool mean $\bar\xi^N\equiv E[\xi\mid d=0,X]$;
- the correlation $\mu\equiv E[\xi\mid\theta=1,X]-E[\xi\mid\theta=0,X]$.

#### Proposition 3 (premium decomposition) [D]

Under (A1)–(A2) plus $\xi$:
$$B=\rho\beta_1+(\bar\xi^D_1-\bar\xi^D_0),\qquad \Delta=\rho\beta_1e+(\bar\xi^N-\bar\xi^D_0), \tag{1.3}$$
$$\boxed{\lambda=\Delta-eB=\tau\equiv\bar\xi^N-\big[e\,\bar\xi^D_1+(1-e)\,\bar\xi^D_0\big]},\qquad \Delta-B=-\rho\beta_1(1-e)+(\bar\xi^N-\bar\xi^D_1). \tag{1.4}$$

**Interpretation.** The over-identifying wedge is *exactly* the excess unobserved quality of the silent pool over a $\theta$-matched synthetic pool of disclosers. Under Bayesian beliefs, $\hat\lambda$ is a pure selection-on-unobservables statistic.

**Proof.** Substitute group means. Sympy (`checks.py`) verifies (1.4) symbolically over all eight $(K,\theta,d)$ cells. $\square$

#### Corollary 3a (correlation alone is neutral) [D]

If there is no selection on $\xi$ beyond $\theta$, i.e. $E[\xi\mid K,\theta,d,X]=E[\xi\mid\theta,X]$, then
$$\bar\xi^N-\bar\xi_0=e\,\mu,\qquad \Delta=e(\rho\beta_1+\mu)=e\,B,\qquad \lambda=0\ \text{for every }\mu. \tag{1.5}$$

**The sign the prompt asked for.** Haussmann means $\mu<0$: bad EPC goes with high $\xi$. The hidden pool contains more $\theta=1$ units than the disclosed-low pool, so $E[\xi\mid N]<E[\xi\mid L]$. This **works against** the premium. It also lowers $B$ by exactly the same factor, so the *ratio* $\Delta/B=e$ is unchanged.

**Required $\mu$.**
- Matching $\hat\Delta=8.53$ and $\hat\beta_1=4.06$ jointly needs $\Delta/B=2.10$, but (1.5) pins $\Delta/B=\hat e^*=0.59$. **No $\mu$ of either sign solves it.**
- Matching $\hat\Delta$ alone, holding $\rho\beta_1=\hat\rho\beta_1^{\rm anchor}\approx4.45$, needs $\mu=\hat\Delta/\hat e^*-4.45\approx+9.9$. A *positive* correlation of about 10 log points would then push $B$ to about 14.4, against the observed 4.06. Contradiction.

**Distortion of the green premium [D].**
- **Cross-sectional hedonic** (`hedonic.py`, disclosers): $\hat\beta_1^{xs}\to\rho\beta_1+\mu_X$, where $\mu_X$ is the within-$X$ correlation. Under Haussmann ($\mu_X<0$) the green premium is understated. It follows that $\hat\rho=\hat\beta_1/\beta_1^{\rm anchor}$ would be understated if built from levels.
- **Paper's DiD $\hat\beta_1$:** time-invariant $\mu$ differences out, so $\hat\rho$ is robust to it. Only a reform-dated change in $\mu$ (e.g. a change in the price of $\xi$ that is correlated with $\theta$) would contaminate $\hat\rho$.
- **Evidence consistent with $\mu<0$ in levels.** Apartment D − E/F/G is −1.36 pre-reform in the index [E]: D trades below E/F/G within market. Read as $\theta$-pricing this is impossible. It is natural if E/F/G is old central stock and D is post-war blocks.

#### Corollary 3b (selection through information status, $\kappa$) [D]

Let the uninformed pool carry a shift: $\bar\xi_{0\theta0}=E[\xi\mid\theta]+\kappa$. Then
$$\lambda=\kappa\cdot\Pr(K=0\mid d=0)=\kappa\,\frac{1-\pi}{\pi\bar\theta\sigma_1+\pi(1-\bar\theta)\sigma_0+(1-\pi)}. \tag{1.6}$$
At the apartment means ($\pi=.507$, $\bar\theta=.625$, $\sigma_0=.152$, $\sigma_1=0$), $\Pr(K=0\mid d=0)=0.945$. Matching $\hat\lambda=6.1$ needs $\Delta\kappa\approx6.5$ log points across the reform.

#### Corollary 3c (selection on $\xi$ among informed hiders, $\eta$) [D]

Suppose informed low types with high $\xi$ hide: $\bar\xi_{100}=\bar\xi_0+\eta$, with disclosers adjusting so that $E[\xi\mid K=1,\theta=0]$ is unchanged. Then $\lambda=\eta\cdot\Pr(K=1,\theta=0\mid d=0)/(1-\sigma_0)$, which is $0.065\,\eta$. Matching 6.1 needs $\eta\approx93$ log points. **Not plausible.** Strategic hiders are 5.5% of the silent pool, so who hides among informed sellers cannot move the pool price. Only the composition of the uninformed pool can.

#### Corollary 3d (the DiD caveat) [D]

Any time-invariant $\tau$ cancels from $\hat\Delta$ and $\hat\beta_1$. Under Bayesian beliefs, $\hat\lambda=\Delta\tau$ (plus $B\,\Delta e$ terms). The level violation, present pre- and post-reform, is explained by a static $\kappa$. The **DiD** wedge, however, needs the uninformed pool's relative unobserved quality, or its price, to rise at July 2021.

Reform-linked candidates [C]:
1. **New-build and off-plan listings migrating into the "no letter" category.** These would move from showing their RT2012 letter (A/B) to "non communiqué" or "en cours" during the method change. That raises $D$ *and* removes high-$\xi$ units from $H$, lowering $B$, which is exactly the apartment pattern. Houses are less exposed because new-build houses trade mostly via construction contracts rather than portal listings.
2. **The ADEME new-build DPE sits in a separate dataset from existing dwellings** [CHECK which dataset the match uses, `ADEME/enrich_listings.py`]. If only existing-dwelling records are matched, new builds are $K=0$ by construction.
3. **Post-COVID repricing of attributes that the silent group over-represents.** Flat 33-month pre-trends (04:365) argue against a slow trend but cannot rule out a break.

#### Exploratory evidence on $\kappa$ versus Haussmann [E]

Specification: listing-level log price per m², 2022–24, apartments ($N=767{,}232$). Regressors are group dummies against disclosed E–G, with FE as indicated, log size, rooms, floor, elevator and cellar. SEs are clustered by market (`reg.py`, `reg2.py`).

| Spec | $H$ (A–D) | $N,K{=}0$ | $N,K{=}1,\theta^{\rm reg}{=}1$ | $N,K{=}1,\theta^{\rm reg}{=}0$ |
|---|---|---|---|---|
| market + quarter FE | −8.70 (5.89) | 7.38 (7.04) | 0.45 (2.08) | 15.08 (2.02) |
| + vintage FE + X | −0.43 (2.39) | 12.03 (4.63) | 3.56 (0.78) | 10.53 (0.92) |
| neighbourhood + vintage FE + X | 4.88 (0.90) | **18.66 (2.12)** | 3.74 (0.72) | **0.89 (0.60)** |
| neighbourhood × vintage FE + X | 4.74 (0.91) | 16.91 (2.37) | 3.60 (0.83) | 0.91 (0.66) |
| *by vintage, nbhd×vintage FE:* | | | | |
| known vintage 1800–2003 | 3.63 (0.81) | **1.20 (0.40)** | 4.02 (0.64) | 1.46 (0.21) |
| 1800–1914 (Haussmann) | 5.21 (1.34) | **−0.63 (0.74)** | 3.08 (0.89) | 0.93 (0.25) |
| 1946–1974 | 3.82 (0.98) | 2.47 (0.58) | 4.36 (0.75) | 3.15 (0.37) |
| vintage missing (40% of sample) | 6.71 (1.05) | **22.31 (2.40)** | 4.68 (1.26) | 0.76 (1.35) |
| 2004+ | 7.20 (1.43) | **18.80 (3.43)** | 6.12 (1.54) | 10.85 (3.75) |

Composition notes:
- 72.7% of $N,K{=}0$ listings have missing vintage and 13.8% are 2004+. The comparable shares for $H$ are 32.7% and 21.0%.
- $N,K{=}0$ apartments are *less* city-centre than $L$ (35% vs 53%), so the premium is not city-centre location.

**Three implications.**
1. **Haussmann does not generate a silent premium.** Within pre-1915 neighbourhood × vintage cells, uninformed silent apartments trade at E/F/G level.
2. **The silent premium is a $K=0$ phenomenon concentrated in missing-vintage and new stock.** Buyers do not observe $K$ (04:86), so within $X$ the $K{=}0$ versus $K{=}1$ silent gap of about 15–17 points is $\xi$ (or listing type), not beliefs.
3. **Informed hiders are priced close to their true, hidden grade.** The neighbourhood row identifies a "transparency" weight
$$\omega=\frac{\delta_{N,K1,\theta=1}-\delta_{N,K1,\theta=0}}{\delta_H}=\frac{3.74-0.89}{4.88}=0.58.$$
   The implied pool price is $0.89/(1-\omega)=2.14$, i.e. a priced belief of $2.14/4.88=0.44$, **inside the hull** and near $\hat e^*$. The implied cross-sectional $\kappa$ is $18.66-2.14=16.5$.

Caveats on these numbers:
- They are cross-sectional listing prices, not the paper's index DiD.
- 627 markets are used, not the 45 in the estimation sample.
- In the 2004+ subsample the E/F/G base is only 2.4% of listings.
- They must be replicated in the pipeline before use.

**Houses, same specification.**
- $H=+12.4$; $N,K{=}0=-5.0$ (1.3), i.e. *below* E/F/G; informed hiders at $+14.4$ for true-high and $-0.5$ for true-low.
- Houses again show $\omega\approx1$, and the uninformed pool is *negatively* selected.

**Verdict on Bastien's proposal.**
- Correlation $\mathrm{Cov}(\xi,\theta\mid X)$ alone cannot produce the wedge (Corollary 3a).
- The Haussmann sign is wrong, and empirically absent within cells.
- The part of the idea that works is **unobserved quality correlated with information status $K$** (Corollary 3b). It requires relaxing $K\perp\theta$ (04:136–138) to "$K\perp\theta\mid X$ but $K\not\perp\xi$".

---

### 1.3 Behavioural alternatives, formalised

Throughout, letters are taken at face value unless a salience term is added, and $B$, $\Delta$, $\lambda$ are as in (0.1)–(1.2).

#### (i) Cursed / naive buyers, including the Hagenbach–Koessler mixture

**Belief rule [A].**
$$\tilde e=(1-\chi)\,e(\sigma_0,\sigma_1)+\chi\,\bar\theta(X),\qquad\chi\in[0,1]. \tag{1.7}$$
- $\chi$ is the Eyster–Rabin cursedness parameter.
- Equivalently, in the Hagenbach–Koessler (2017) structure, a share $\chi$ of sensitive buyers is naive and takes "no disclosure" as uninformative, playing the prior mean $E(t)$ (their eq. 4). The sophisticated share best-responds.
- With $\bar\theta(X)$ the $X$-conditional prior, this is the faculty's "don't infer the worst, anchor on other signals". **Task 2's predicted $\hat P(\theta=1\mid X)$ is the natural empirical $\bar\theta(X)$.**

**Proposition 4 (belief channels are capped) [D].** For any belief rule with $\tilde e\in[0,1]$, priced as in (A1):
$$\Delta-B=-\rho\beta_1(1-\tilde e)\le0,\qquad \lambda=\rho\beta_1(\tilde e-e)\le(1-e)\,B. \tag{1.8}$$
Under (1.7) in particular, $\lambda=\chi\rho\beta_1(\bar\theta(X)-e)$.

**Numbers.**
- Full cursedness ($\chi=1$, $\bar\theta(X)=\bar\theta$) gives $\lambda\le\hat\beta_1(\hat{\bar\theta}-\hat e^*)\approx4.06\times0.032\approx0.13$, i.e. 2% of 6.1.
- Motivated or optimistic beliefs ($\tilde e\to1$) give at most 1.65.
- Under the registry-based $\sigma_1\approx\sigma_0$ (FINDING-sigma1), $e^*=\bar\theta$ *exactly*, and the cursed channel has literally zero bite.

**Why this matters for the paper [D].** In a Dye pool that is 94% uninformed, the Bayesian already reads silence as nearly uninformative. "Insufficient skepticism" therefore cannot be the explanation, however strong the experimental evidence for it (Jin, Luca & Martin 2021; Brown, Camerer & Lovallo 2012). Under-skepticism matters when silence would be damning, i.e. when $e$ is far below the prior. Here it is not.

**Equilibrium feedback.** With cursed buyers, the informed-low hiding gain is $\rho\beta_1\tilde e$. In Partial Pooling the indifference condition still pins $\Delta=c_0$, and $\sigma_0^*$ rises (Hagenbach–Koessler Prop. 1: the threshold is increasing in the naive share $\lambda_R$). The correct cost inversion becomes $\hat c_0=\hat\beta_1\tilde e$, so the paper's $\hat\lambda$ fails by $\hat\beta_1(\tilde e-\hat e^*)$, which is the same bound.

**Prediction for hiding.** More hiding by low types, and $\sigma_0>\sigma_1=0$, with the gap growing in $\chi$. FINDING-sigma1 ($\hat\sigma_1\approx\hat\sigma_0$, U-shaped) does **not** fit.

#### (ii) Motivated skepticism (Hagenbach & Saucet 2025)

**Adaptation [A].** A buyer who has fallen for a flat holds anticipatory utility in its quality. Following their §2.3, after silence she picks
$$\tilde e=\arg\max_{x\in[0,1]}\ -(x-e)^2+\alpha x\quad\Rightarrow\quad\tilde e=\min\{1,\,e+\alpha/2\}.$$
Concluding "it is a *passoire*" is *self-threatening*, the case in which they find skepticism significantly lower (Low_Loaded versus Low_Neutral). Their beliefs stay *consistent with the message*: support within $m$, and for silence $m=\{0,1\}$.

**Implication [D].** This is covered by Proposition 4, so $\lambda\le1.65$ and $D\le B$.

**Distinctive predictions [C].**
- Stronger in owner-occupier segments than investor segments.
- Stronger where search is long and costly (tight markets), since that is where ego or anticipatory investment is high.
- Absent for EPC-insensitive buyers.

#### (iii) Salience / anchoring on displayed letters (the faculty mechanism, literal version)

**Valuation [A].** Displayed letters are perceived with distortions:
- low letters at $0-s$, with $s\ge0$ (anchoring on the bad letter: penalty beyond fundamental, à la Bordalo–Gennaioli–Shleifer salience);
- high letters at $1-s_H$, with $s_H\ge0$ for mediocre C/D read as bad (coarse thinking, Mullainathan–Schwartzstein–Shleifer 2008).
- Silence is valued at $\tilde e$.

**Proposition 5 [D]** (sympy-verified, `checks2.py`):
$$\lambda=\rho\beta_1\big[(\tilde e-e)+s(1-e)+s_He\big],\qquad \Delta-B=\rho\beta_1(\tilde e-1+s_H). \tag{1.9}$$
- **Low-letter anchoring alone ($s_H=0$) never produces $\Delta>B$.** It raises $\lambda$ by $\rho\beta_1s(1-e)$. Since $B=\rho\beta_1(1+s)\ge\rho\beta_1s$, the cap $\lambda\le(1-e)B=1.65$ still binds.
- Reaching $\Delta-B=4.47$ needs $s_H>1-\tilde e+4.47/(\rho\beta_1)$. With $\rho\beta_1\approx4$, that is $s_H\approx1.5$: displayed A–D letters penalised by 1.5 times the full quality gap.
- The index shows silent beating **A/B/C** by 3.9 DiD points. Calling A/B "mediocre" is not credible. **Rejected as the main channel.**

**Side effect [D].** $B=\rho\beta_1(1+s-s_H)$, so the anchored $\hat\rho=B/\beta_1^{\rm anchor}=\rho(1+s-s_H)$ is biased whenever letters carry salience.

#### (iv) Shrouded energy *costs* (the version of "anchor on other signals" that can work)

**Primitives [A].** Capitalised energy cost is $\mathcal E_\theta$ (per € of price), with $\mathcal E_0>\mathcal E_1>0$. EPC-sensitive buyers subtract the *displayed* cost fully. When nothing is displayed they subtract only $m_0\,\mathbb E[\mathcal E\mid d=0]$, with $m_0\in[0,1]$ the attention weight on non-displayed costs. This is a Gabaix (2019) sparsity default, with Chetty–Looney–Kroft (2009) and Brown–Hossain–Morgan (2010) as the empirical analogues, and close to Enke's (2020) "what you see is all there is". Let $\mathcal E^e\equiv\hat e\,\mathcal E_1+(1-\hat e)\mathcal E_0$.

**Proposition 6 [D]** (sympy, `checks.py`):
$$B=\rho(\mathcal E_0-\mathcal E_1),\qquad \Delta=\rho(\mathcal E_0-m_0\mathcal E^e),\qquad \frac{\Delta}{B}=\frac{\mathcal E_0-m_0\mathcal E^e}{\mathcal E_0-\mathcal E_1}, \tag{1.10}$$
$$\Delta>B\iff m_0<\mathcal E_1/\mathcal E^e .$$
Silence beats verified-high because the A–D listing *shows* a positive cost and the silent one shows none. The relevant attribute is the cost **level**, not the letter **rank**.

**Calibration [E].**
- Using the anchor's own band midpoints (`data_prep.py:417–425`) and registry letters of $K=1$ listings, market means are $\bar E_1=185$ and $\bar E_0=327$ kWh$_{ep}$/m²/yr for apartments. The full-neglect ratio is $\mathcal E_0/(\mathcal E_0-\mathcal E_1)=2.31$, against the observed $\hat\Delta/\hat\beta_1=2.10$.
- Implied attention is **$m_0=0.12$ for apartments and $m_0=0.95$ for houses** (houses: $\bar E_1=178$, $\bar E_0=339$, ratio 0.67).
- The fit is suspiciously good on one moment. Note $\hat\rho$ is unaffected if displayed costs are capitalised at weight 1 (B is still $\rho\times$ anchor).

**Institutional hook.** Since **1 January 2022**, French sale listings must state the "montant estimé des dépenses annuelles d'énergie pour un usage standard", and F/G listings must carry "logement à consommation énergétique excessive" (ANIL summary; fines up to €3,000 or €15,000). This is a dated shock to the salience of displayed costs that is *separate* from July 2021.

**What contradicts it [E].**
- Within known-vintage stock, uninformed silent apartments trade at only +1.2. (1.10) with $m_0=0.12$ predicts roughly $\hat\rho(\mathcal E_0-m_0\mathcal E^e)\approx8$ there too.
- The premium is concentrated in missing-vintage and new stock, which is not a buyer-attention margin.

**Equilibrium prediction.** The hiding gain for type $\theta$ is $\rho(\mathcal E_\theta-m_0\mathcal E^e)$, which is positive for *both* types when $m_0$ is small. So $\sigma_1>0$ is predicted. That is consistent with FINDING-sigma1, but the predicted hiding rates are large and decreasing in $\theta$. The observed informed hiding is low, flat-to-U-shaped, and priced near the true grade ($\omega\approx0.58$), which points to small hiding gains.

#### (v) Mixture of sophisticated and naive sensitive buyers

Split $\rho=\rho_S+\rho_N$. Then $B=\rho\beta_1$, $\Delta=\beta_1(\rho_Se+\rho_N\tilde e)$, and $\lambda=\rho_N\beta_1(\tilde e-e)$. This is the same cap as Proposition 4.

$\rho_N/\rho$ is identified from the cross-market slope of $\hat\lambda_m$ on $\hat\beta_{1,m}(\bar\theta_m-\hat e^*_m)$. It is **weakly identified**: the regressor has mean about 0.13 and little spread.

#### (vi) Not in the brief, but must be flagged: seller-side list pricing [C]

The outcome is the **list** price, which comes from listings rather than transactions. Uninformed sellers ($K=0$) include private sellers, estates and new-build promoters, and may post aspirational asking prices (Genesove & Mayer 2001 loss-aversion anchoring). Separately, price may itself be read as a quality signal when no letter is shown (Bagwell & Riordan 1991).

Discriminating predictions: for silent listings,
- longer time-on-market;
- more price cuts;
- a lower list-to-sale ratio.

None of these is predicted by buyer-side channels, which raise demand at the higher price.

#### Relation to the paper's current candidate explanations (04:555–589)

- **Registry-match noise "attenuates $\hat\beta_{1,m}$" (04:556–564).** This does not apply. $\hat\beta_1$ is built from **displayed**-letter index groups (`event_study.py:252`), which carry no registry-match error. Noise enters $\hat e^*$, $\hat\pi$ and $\hat\sigma_0$ instead.
- **"Coarseness / substitute signals" (04:564–571)** is case (i) with $\bar\theta(X)$. It is capped by Proposition 4 and cannot generate $D>B$.
- **"Risk premium on silent listings" (04:575–580)** has the wrong sign: it lowers silent prices.
- **"Thin buyer bargaining position" (04:580–585)** is a seller-side term in the spirit of (vi).

---

### 1.4 Discriminating predictions

Rows are the mechanisms:
- **A**: $\mathrm{Cov}(\xi,\theta\mid X)$ only.
- **B**: $\xi$-selection via $K$, $\kappa$ (uninformed or new-build composition).
- **C**: $\xi$-selection among informed hiders, $\eta$.
- **D**: cursed/naive, $\chi$.
- **E**: motivated beliefs.
- **F**: displayed-letter salience, $s$ and $s_H$.
- **G**: shrouded energy cost, $m_0$.
- **H**: seller-side over-listing.

| Prediction | A | B ($\kappa$) | C ($\eta$) | D ($\chi$) | E | F ($s,s_H$) | G ($m_0$) | H |
|---|---|---|---|---|---|---|---|---|
| Can give $\Delta>B$? | No | **Yes** | Yes (implausible size) | No | No | Only if $s_H$ large | **Yes** | Yes |
| Cap on $\lambda$ | 0 | none | none | $B(\bar\theta-e)\approx0.13$ | $(1-e)B=1.65$ | $(1-e)B$ if $s_H=0$ | none | none |
| $K{=}0$ vs $K{=}1$ silent gap given $X$ (R1) | 0 | **large, = $\kappa$** | negative | 0 | 0 | 0 | 0, or $>0$ if $K{=}1$ grades leak | $>0$ if $K{=}0$ sellers over-list |
| Loading of hidden registry grade, $\omega$ (R2) | $\mu/\delta_H$ (any sign) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Price-implied belief vs registry-Bayes $E[\theta\mid d{=}0,X]$ (R3) | equal | equal, once $\kappa$ is removed | equal | above, by $\chi(\bar\theta(X)-e)$ | above | above (via $s$) | n/a (cost units) | n/a |
| Pre-1915 vs post-1975 | $\Delta,B$ scale together | where the $K{=}0$ pool differs in $\xi$ | — | small everywhere | — | larger where E–G is common | larger where $\mathcal E_0$ is high (old stock) | — |
| Missing-vintage / new-build listings | — | **premium concentrated here** | — | no | no | no | no | possibly |
| Tight vs slack markets (cateaav2020, zones tendues) | — | where new-build share is high | — | — | larger where tight (long search) | — | larger where heating costs are high | larger where slack |
| Apartments vs houses | same | apartments (new-build programmes) | — | both | owner-occupier heavy | both | where $m_0$ is low | — |
| Timing | — | at the composition break | — | at July 2021 | — | at Jan 2022 and Jan 2023 F/G mentions | **at Jan 2022** (€ display) | — |
| Cross-market slope of $\hat\lambda_m$ on $\Pr(K{=}0\mid d{=}0)_m$ | 0 | **+** | − | ∝ $(\bar\theta-e)$ | — | — | — | — |
| Hiding pattern $\sigma_\theta$ | — | unaffected | low types with high $\xi$ hide | $\sigma_0\uparrow$, $\sigma_1=0$ | $\sigma_0\uparrow$ | $\sigma_0\uparrow$ | both $\uparrow$, $\sigma_0>\sigma_1$ | — |
| Time-on-market, price cuts | — | normal | — | normal | normal | normal | normal | **longer / more** |
| Effect of $\pi_m$ on the premium | none | via the pool weight $(1-\pi)/H$ | — | — | — | — | — | — |

**Key point: the registry lets you compute the rational belief.** $E[\theta\mid d=0,K=1,X]$ is directly observed for informed hiders (`ademe_epc_score`). The $K=0$ part needs $E[\theta\mid K=0,X]$. That is $\bar\theta$ under $K\perp\theta$, or **Task 2's $\hat P(\theta\mid X)$** under the weaker $K\perp\theta\mid X$.

Pooled registry values are $\Pr(\theta=1\mid K=1,d=0)=0.50$ against $0.57$ for disclosers [E]. Hiders are only mildly negatively selected on grade.

#### Concrete regressions and moments

- **R1 (K-gap; separates beliefs from $\xi$).**
  $$\log p_i=\alpha_{n(i)\times v(i)}+\gamma_{q(i)}+X_i'\gamma+\delta_H H_i+\delta_{0}N_iK^0_i+\delta_{1\theta}N_iK^1_i\mathbf 1[\theta^{\rm reg}_i=\theta]+\varepsilon_i,$$
  with neighbourhood × vintage FE.
  - Buyer-side channels imply $\delta_0=\delta_{\rm pool}$.
  - The difference identifies $\kappa$.
  - Report by vintage, by missing-field count, and with listings flagged as new or programme-type removed. Use SeLoger "neuf" flags if the feed has them [CHECK].

- **R2 (transparency $\omega$).** Using R1 coefficients,
  $$\hat\omega=(\delta_{11}-\delta_{10})/\delta_H,\qquad \hat\delta_{\rm pool}=\delta_{10}/(1-\hat\omega).$$
  - **Benchmark:** compare $\hat\omega$ with the discrimination slope $E[\hat P(\theta{=}1\mid X)\mid\theta{=}1,N,K^1]-E[\hat P\mid\theta{=}0,N,K^1]$ from Task 2.
  - If Task 2's slope is far below 0.58, buyers learn $\theta$ beyond $X$. Plausible routes are visits and the DPE being available on request [CHECK legal basis], which makes informed silence largely cheap talk.

- **R3 (belief test).** The price-implied belief $\hat e^{\rm price}=\hat\delta_{\rm pool}/\delta_H$, compared with $E[\theta\mid d=0,X]$ built from registry $K=1$ hiders plus $\hat P(\theta\mid X)$ for $K=0$. Then
  $$\hat\chi=(\hat e^{\rm price}-e^{\rm Bayes})/(\bar\theta(X)-e^{\rm Bayes}).$$
  Report it with an explicit weak-identification warning, since the denominator is about 0.03.

- **R4 (DiD composition).** Rebuild the Chapter-1 index (a) excluding missing-vintage and 2004+ listings, and (b) excluding new-build or programme listings. Re-estimate $\hat\Delta_m$ and $\hat\beta_{1,m}$. Tabulate the vintage composition of each EPC group by month around July 2021.
  - **If $\hat\Delta$ collapses toward $\hat e^*\hat\beta_1$, the apartment wedge is composition, not mechanism.**

- **R5 (cross-market).** Regress
  $$\hat\lambda_m=a+b_1\widehat{\Pr}(K{=}0\mid d{=}0)_m\cdot\text{newshare}_m+b_2\hat\beta_{1,m}(\hat{\bar\theta}_m-\hat e^*_m)+b_3\hat\beta_{1,m}\tfrac{\bar E_{0m}}{\bar E_{0m}-\bar E_{1m}}+\text{controls},$$
  with heating-degree-days as a shifter of $\mathcal E_0$ that is excluded from $\kappa$.

- **R6 (timing).** Monthly event study of $D_t-B_t$ (silent minus verified-high) with breaks at 2021-07, 2022-01, 2023-01 and 2024-07. The last is the small-surface relabelling (arrêté of 25 March 2024, in force 1 July 2024), which moves about 140k sub-40 m² units out of F/G without changing consumption. It is a clean test of letter salience.

- **R7 (letter RD).** If the ADEME continuous consumption (kWh$_{ep}$/m²) can be pulled for $K=1$ listings, run an RD at band thresholds. The price jump at the letter cutoff, net of the kWh slope, identifies letter salience $s$ separately from cost capitalisation (Lacetera, Pope & Sydnor 2012 logic).

- **R8 (seller side).** If start and end dates or price revisions exist in the SeLoger feed, compare time-on-market and price cuts by group.

---

### 1.5 Recommendation

**Do first, before any model change: R1, R2 and R4.** The numbers in §1.2 [E] suggest strongly that the apartment wedge comes from the composition of the "no letter, no registry" pool: missing-vintage and new stock, with unobserved quality far above the hull. Buyer beliefs do not appear to be the source.
- **If R4 confirms this,** the honest fix is a *sample definition*: exclude new-build or programme listings from the index. Add one structural term, $\kappa$, for whatever composition remains. That fix does not need a new behavioural mechanism, and it keeps the paper's Dye–Jung–Kwon interpretation intact for existing stock. The houses already fit (λ̂ ≈ 0; $D/B\approx\hat e^*$).

**Model extension to adopt in any case** (§1.6): $\kappa$ (uninformed-pool unobserved quality) plus $\omega$ (partial transparency of informed hiders).
- Both are point-identified from cross-sectional moments the repo already has.
- Both are consistent with FINDING-sigma1. With $\omega$ near 0.6–1, informed hiding gains are small, so the hiding rate need not be decreasing in $\theta$.
- Correlation $\mu$ can be added for honesty about the level green premium, but it is neutral for $\lambda$.

**Behavioural layer.** Keep the faculty's anchoring idea only in a form that can matter.
- Belief distortions ($\chi$, motivated beliefs) and bad-letter anchoring ($s$) should appear as **bounded robustness**: Propositions 4–5 put them at ≤ 27% of the wedge, and the cursed case at ≈ 2%.
- That bound is itself a useful and citable result for the paper. In a Dye market dominated by uninformed sellers, receiver naivety is nearly irrelevant.
- **Shrouded energy costs ($m_0$)** are the only behavioural channel that can match the magnitude. Keep them as a *secondary* hypothesis, tested by the January 2022 timing (R6) and the heating-cost heterogeneity (R5).

**What each option cannot do.**
- **$\kappa$** explains levels without help. For the DiD it needs a reform-dated composition change, which is open until R4 is run. It also leaves the "why does silence earn a premium" headline as partly a statement about *what* is silent, not *why* sellers stay silent. That reframes the paper's opening puzzle (03:129) and must be said explicitly.
- **$\omega$** lowers the implied concealment cost: $\hat c_0=(1-\hat\omega)\hat\beta_1\tilde e$, from 2.4 to roughly 1.0. This feeds into the subsidy counterfactuals (§5).
- **$\chi$ / motivated beliefs** cannot produce $D>B$.
- **$s$** biases $\hat\rho$ and cannot produce $D>B$.
- **$m_0$** is not separately identified from $\kappa$ without an exclusion restriction, and the vintage split already contradicts it as a uniform mechanism.

---

### 1.6 Minimal changes to the equations

All numbering below is local to this note. The paper's notation is retained: $\theta\in\{0,1\}$, $K$, $d$, $\pi$, $\bar\theta$, $\sigma_\theta$, $\rho$, $\beta_1$, $c_0$, $e(\sigma_0,\sigma_1)$.

**Valuations (replaces 04:114–121).**
$$v_1(\theta,d;X,\xi)=\beta_0+\beta_1\,\tilde\theta(d)+X'\beta+\xi,\qquad v_0(X,\xi)=\beta_0+X'\beta+\xi. \tag{E1}$$

**Unobserved quality, relaxing Assumption 1 (04:136).**
$$\xi=\kappa\,(1-K)+\mu\,\theta+\nu,\qquad E[\nu\mid K,\theta,d,X]=0,\qquad K\perp\theta\mid X. \tag{E2}$$
The restriction "no selection on $\nu$ into $d$ among informed sellers" ($\eta=0$) is maintained and testable via R1.

**Priced belief after silence.**
$$\tilde\theta(0)=\tilde e\equiv(1-\chi)\,e(\sigma_0,\sigma_1)+\chi\,\bar\theta(X),\qquad \bar\theta(X)\equiv\Pr(\theta=1\mid X)\ \text{(Task 2)}. \tag{E3}$$
Set $\chi=0$ in the baseline and report the bound.

**Partial transparency for informed hiders** (the grade leaks before the price is set, with probability $\omega$).
$$\tilde\theta(0\mid K=1,\theta)=(1-\omega)\,\tilde e+\omega\,\theta. \tag{E4}$$

**Group prices**, relative to disclosed-low at the reference $X$, using main.tex:485 pricing:
$$\begin{aligned}
p_H-p_L&=\rho\beta_1+\mu,\\
p_{N,K=0}-p_L&=\rho\beta_1\tilde e+\mu\bar\theta(X)+\kappa,\\
p_{N,K=1,\theta}-p_L&=\rho\beta_1[(1-\omega)\tilde e+\omega\theta]+\mu\theta.
\end{aligned}\tag{E5}$$

**Wedge** (sympy-verified, `checks3.py`):
$$\lambda=\Pr(K{=}0\mid d{=}0)\,\kappa+\rho\beta_1(\tilde e-e)-\rho\beta_1\omega\sum_{\theta}\Pr(K{=}1,\theta\mid d{=}0)(\tilde e-\theta), \tag{E6}$$
and $\mu$ drops out.

**Indifference with transparency** (replaces (04:227)).
$$\Phi(\sigma_0)=(1-\omega)\rho\beta_1\tilde e(\sigma_0)-c_0=0\ \Rightarrow\ \hat c_0=(1-\hat\omega)\,\hat\beta_1\,\hat{\tilde e}. \tag{E7}$$

**Optional behavioural term (shrouded cost).** Replace $\rho\beta_1\tilde\theta$ by $-\rho\,[\,\mathcal E_\theta\ \text{if }d=1;\ m_0\mathcal E^e\ \text{if }d=0\,]$:
$$\Delta/B=(\mathcal E_0-m_0\mathcal E^e)/(\mathcal E_0-\mathcal E_1). \tag{E8}$$

#### Identification map

| Parameter | Moment | Variation | Key assumption | Status |
|---|---|---|---|---|
| $\omega$ | $(\delta_{N,K1,\theta=1}-\delta_{N,K1,\theta=0})/\delta_H$ (R2) | hidden registry grade of informed hiders within $X$ cells | $\eta=0$; registry grade is the true $\theta$ | point (≈0.58 [E]) |
| $\tilde e$ (priced pool belief) | $\delta_{N,K1,\theta=0}/[(1-\omega)\delta_H]$ | same | (E4); no $\kappa$ for $K=1$ | point (≈0.44 [E]) |
| $\kappa$ | $\delta_{N,K0}-\rho\beta_1\tilde e-\mu\bar\theta(X)$ (R1) | $K=0$ vs $K=1$ silent within $X$ | buyers do not observe $K$ (04:86); $K\perp\theta\mid X$, so Task 2's $\hat P(\theta\mid X)$ fixes the $\theta$-mix | point (≈16.5 cross-section [E]); its DiD change is a separate object (R4) |
| $\chi$ | $(\hat e^{\rm price}-e^{\rm Bayes})/(\bar\theta(X)-e^{\rm Bayes})$ (R3) | registry Bayes belief vs priced belief | $\kappa$ removed first | **weak**: denominator ≈ 0.03; report a bound |
| $\rho$ | $\hat\beta_1^{DiD}/\beta_1^{\rm anchor}$ (unchanged) | reform × market | time-invariant $\mu$ (cancels in the DiD); $s=s_H=0$ | point; biased by $(1+s-s_H)$ if letters carry salience |
| $\mu$ | $B^{\rm level}_{\rm post}-\hat\rho\,\beta_1^{\rm anchor}$; or within-unit re-certification after renovation (repeat listings) | levels vs anchor | $\rho_{\rm pre}\approx0$ | **not** separately identified from $\rho$ in a pure cross-section; neutral for $\lambda$ |
| $s$ | price discontinuity at letter thresholds net of the kWh slope (R7); July-2024 small-surface relabelling (R6) | continuous registry consumption; regulatory relabelling | continuity of $\xi$ at thresholds | point if continuous kWh are obtained; otherwise confounded with $\rho$ |
| $m_0$ | $\hat\Delta_m/\hat\beta_{1,m}$ vs $\bar E_{0m}/(\bar E_{0m}-\bar E_{1m})$ (R5); Jan-2022 break (R6) | cross-market heating-cost levels; timing | $\kappa_m\perp\bar E_{0m}$ (exclusion) | weak; **not** separable from $\kappa$ without the exclusion |
| $c_0$ | (E7) | $\hat\sigma_0$, registry | Partial Pooling; registry $\theta$ for hiders (set `hider_theta: registry`) | point; level falls by the factor $(1-\hat\omega)$ |

#### Which parameters are jointly identified

- $(\omega,\tilde e,\kappa)$ are jointly identified from the cross-section once Task 2's $\hat P(\theta\mid X)$ is available.
- $(\rho,s)$ are not separately identified from $B$ and the anchor alone; they need R7 or R6.
- $(\kappa,m_0)$ need an exclusion restriction.
- $\chi$ is weakly identified because the silent pool is nearly uninformed.

**Interaction with the anchor.** $\hat\rho$ survives the $\kappa$/$\omega$ extension unchanged, since both enter $\Delta$ and not $B$. It also survives time-invariant $\mu$. It does not survive letter salience. In (E8) it survives only if displayed costs are capitalised at weight 1.

---

### 1.7 References

Entries I could not fully verify are flagged [CHECK]. Everything else was confirmed from the PDF or a web source, or is a standard reference whose bibliographic details I am confident of.

- Bagwell, K. and M. Riordan (1991). "High and Declining Prices Signal Product Quality." *American Economic Review* 81(1): 224–239.
- Bederson, B., G. Z. Jin, P. Leslie, A. Quinn and B. Zou (2018). "Incomplete Disclosure: Evidence of Signaling and Countersignaling." *AEJ: Microeconomics* 10(1): 41–66. *(Relevant to the A-tail of hiding: high types not disclosing.)*
- Bordalo, P., N. Gennaioli and A. Shleifer (2013). "Salience and Consumer Choice." *Journal of Political Economy* 121(5): 803–843.
- Brounen, D. and N. Kok (2011). "On the Economics of Energy Labels in the Housing Market." *JEEM* 62(2): 166–179.
- Brown, A. L., C. F. Camerer and D. Lovallo (2012). "To Review or Not to Review? Limited Strategic Thinking at the Movie Box Office." *AEJ: Microeconomics* 4(2): 1–26.
- Brown, J., T. Hossain and J. Morgan (2010). "Shrouded Attributes and Information Suppression: Evidence from the Field." *QJE* 125(2): 859–876.
- Chen, M. H. and G. Z. Jin (2026). "When Public Signals Backfire: Strategic Disclosure and Information Crowd-Out." NBER WP 35625 (August 2026).
  - Fetched. A public signal correlated with the sender's private information reshapes the reading of silence: receivers' estimates move toward the public signal after non-disclosure.
  - **Directly relevant.** It is the equilibrium version of "buyers anchor on other signals ($X$, photos) when no letter is shown". It predicts *less* disclosure when the public signal is favourable.
  - Testable here: hiding should rise with Task 2's $\hat P(\theta\mid X)$ among informed sellers. This fits the A-tail.
- Chetty, R., A. Looney and K. Kroft (2009). "Salience and Taxation: Theory and Evidence." *AER* 99(4): 1145–1177.
- Dranove, D. and G. Z. Jin (2010). "Quality Disclosure and Certification: Theory and Practice." *JEL* 48(4): 935–963.
- Dye, R. A. (1985). "Disclosure of Nonproprietary Information." *Journal of Accounting Research* 23(1): 123–145.
- Enke, B. (2020). "What You See Is All There Is." *QJE* 135(3): 1363–1398.
- Eyster, E. and M. Rabin (2005). "Cursed Equilibrium." *Econometrica* 73(5): 1623–1672.
- Feltovich, N., R. Harbaugh and T. To (2002). "Too Cool for School? Signalling and Countersignalling." *RAND Journal of Economics* 33(4): 630–649.
- Frondel, M., A. Gerster and C. Vance (2020). "The Power of Mandatory Quality Disclosure: Evidence from the German Housing Market." *JAERE* 7(1): 181–208.
- Fuerst, F., P. McAllister, A. Nanda and P. Wyatt (2015). "Does Energy Efficiency Matter to Home-Buyers? An Investigation of EPC Ratings and Transaction Prices in England." *Energy Economics* 48: 145–156.
- Gabaix, X. (2019). "Behavioral Inattention." In *Handbook of Behavioral Economics* Vol. 2, 261–343. Elsevier.
- Gabaix, X. and D. Laibson (2006). "Shrouded Attributes, Consumer Myopia, and Information Suppression in Competitive Markets." *QJE* 121(2): 505–540.
- Genesove, D. and C. Mayer (2001). "Loss Aversion and Seller Behavior: Evidence from the Housing Market." *QJE* 116(4): 1233–1260.
- Grossman, S. J. (1981). "The Informational Role of Warranties and Private Disclosure about Product Quality." *Journal of Law and Economics* 24(3): 461–483.
- Hagenbach, J. and F. Koessler (2017). "Simple versus Rich Language in Disclosure Games." *Review of Economic Design* 21(3): 163–175. doi:10.1007/s10058-017-0203-y.
- Hagenbach, J. and C. Saucet (2025). "Motivated Skepticism." *Review of Economic Studies* 92(3): 1882–1919. doi:10.1093/restud/rdae058.
- Jehiel, P. (2005). "Analogy-Based Expectation Equilibrium." *JET* 123(2): 81–104.
- Jin, G. Z., M. Luca and D. Martin (2021). "Is No News (Perceived as) Bad News? An Experimental Investigation of Information Disclosure." *AEJ: Microeconomics* 13(2): 141–173. *(Verified on gingerjin.com.)* Also by the same team: "Complex Disclosure," *Management Science* 68(5): 3236–3261 (2022); Chen and Jin, "Voluntary Report of Standardized Test Scores: An Experimental Study," NBER WP 33660 (2025).
- Jung, W.-O. and Y. K. Kwon (1988). "Disclosure When the Market Is Unsure of Information Endowment of Managers." *Journal of Accounting Research* 26(1): 146–153.
- Kőszegi, B. and A. Szeidl (2013). "A Model of Focusing in Economic Choice." *QJE* 128(1): 53–104.
- Lacetera, N., D. G. Pope and J. R. Sydnor (2012). "Heuristic Thinking and Limited Attention in the Car Market." *AER* 102(5): 2206–2236.
- Mathios, A. D. (2000). "The Impact of Mandatory Disclosure Laws on Product Choices: An Analysis of the Salad Dressing Market." *JLE* 43(2): 651–678.
- Milgrom, P. (1981). "Good News and Bad News: Representation Theorems and Applications." *Bell Journal of Economics* 12(2): 380–391.
- Milgrom, P. and C. Shannon (1994). "Monotone Comparative Statics." *Econometrica* 62(1): 157–180.
- Mullainathan, S., J. Schwartzstein and A. Shleifer (2008). "Coarse Thinking and Persuasion." *QJE* 123(2): 577–619.
- Myers, E., S. L. Puller and J. West (2022). "Mandatory Energy Efficiency Disclosure in Housing Markets." *AEJ: Economic Policy* 14(4): 453–487.

**Institutional facts.**
- Advertising obligations from 1 Jan 2022 (estimated annual energy expenditure; "logement à consommation énergétique excessive" for F/G): ANIL summary at anil.org/aj-dpe-mentions-obligatoires-annonces-baux-immobiliers/.
- Arrêté of 25 March 2024 on DPE thresholds for dwellings ≤ 40 m², in force 1 July 2024.
- Whether the DPE must be made available to prospective buyers before the *promesse*: [CHECK].

**Not cited, by design.** I did not find a German or other EPC paper documenting a *premium* for non-disclosure, and I do not claim one exists. Frondel et al. (2020) study the voluntary-to-mandatory shift. I have not verified their specific findings on non-disclosing listings [CHECK before citing for that point].

---

## Task 2: Can buyers infer the EPC from the listing? (design note)

**Status.** This is a design exercise. Nothing in the repo was edited and no estimation was run. Section 0 reports read-only descriptive checks I computed on 2026-10-05 from `data/listings_enriched_{APARTMENT,HOUSE}.parquet` and `data/listings_{...}.parquet`, restricted to the 2022–24 structural sample (`start_date` year in 2022–24). They are diagnostics for building the design. None of them is a paper-grade number.

**Notation** (same as §4 of the paper). $\theta\in\{0,1\}$ is binarised quality, with $\theta=1$ for A–D (`epc_threshold: 4.0` in both configs). $Y\in\{1,\dots,7\}$ is the letter, with A$=1$ and G$=7$. $K$ is information status, $d$ is disclosure, and $X$ is the buyer-visible listing content. $\bar\theta(X)\equiv\Pr(\theta=1\mid X)$ is the population prior conditional on observables. $\sigma_\theta(X)\equiv\Pr(d=0\mid K=1,\theta,X)$. $\pi(X)\equiv\Pr(K=1\mid X)$.

---

### 0. Data facts, checked against code and files

#### 0.1 Columns

**Buyer-visible columns in `listings_enriched_*`:**
- `log_price` (log €/m², asking price).
- `size_m2`.
- `rooms`, binned `room_count_{0..4,5up,NA}`.
- `floor`, binned, apartments only. Houses are 100% `floor_NA`.
- `floor_num`.
- `elevator`, which is 0 for every house.
- `cellar`.
- `bathrooms`, binned.
- `parking_count`. This is **100% missing for apartments** and 87% missing for houses, so drop it.
- `built_year`, **binned** by `process_built_year` (`data/collect_listings.py:259`) into `1799`, `1800_1914`, `1915_1945`, `1946_1974`, `1975_1990`, `1991_2003`, `2004`, `built_year_NA`. **`built_year_NA` covers 40.3% of apartments and 31.4% of houses.** `bathrooms_NA` covers 41% / 33%.
- Location ids: `region_id`, `subregion_id`, `dept`, `city_id`, `borough_id`, `neighborhood_id`, `market_id`, `cateaav2020_label`, `distance`. `neighborhood_id` is missing for 5.7% of apartments and 47.7% of houses. The 2022–24 apartment sample has 623 markets, 5,402 cities and 8,039 neighbourhoods. The house sample has 674 markets, 20,000 cities and 8,705 neighbourhoods.
- `start_date`.

**Label columns:**
- `d`.
- `EPC`, which equals `"Missing"` iff `d=0`.
- `epc_score`, which is NaN iff `d=0`.
- `K`.
- `ademe_epc_letter` and `ademe_epc_score`, populated for every $K=1$ row, hiders included.
- `match_score`.

**Raw `listings_*` only:** `address_id`, which is non-missing for every 2022–24 row, plus `street_id`, `cog` and `item_type`. These join to the enriched file on `listing_id`, and 100% of enriched ids are found in the raw file.

**In the source SQL (`collect_listings.py:84-117`) but not saved locally:**
- `energy_source_electric`: heating energy, binary electric/non-electric.
- `consoenergie` and `emissionges`.
- `client_type`, i.e. `is_offerer_individual` (private seller vs. agency).
- `realtor_ref` (`client_id`).
- `iris_id` and `block_id`.
- Continuous `build_year`. It is binned before saving.

**Not in the SQL at all:** heating *system* (individual vs. collective, heat pump, gas boiler), description text, and photo URLs. Getting any of these needs a new SeLoger extract against different tables or columns. **[Bastien: confirm which `listing_seloger.aggregate` columns hold description and heating.]**

**Leakage.** `consoenergie` (kWh/m²/yr of primary energy) and `emissionges` (kgCO₂/m²/yr) **are** the inputs to the letter. Under the 2021 method the letter is the worse of the two band classifications ("double seuil"). They must never enter $X$. There is a second, sharper issue to check first. If these fields are non-null on `d=0` listings, the letter is literally on the page for those listings and the definition of $d$ must be revisited (§5, Q1).

#### 0.2 Sample sizes, 2022–24

| | Apartments | Houses |
|---|---|---|
| All listings | 767,232 | 632,575 |
| $d=1$ (letter displayed) | 618,985 | 575,825 |
| $d=1,K=1$ | 392,342 | 262,660 |
| $d=1,K=1$, listing letter $=$ registry letter | 290,248 | 239,544 |
| $K=1$ (registry letter known, any $d$) | 420,562 | 269,917 |
| $K=1,d=0$ (informed hiders) | 28,220 | 7,257 |
| $K=0,d=0$ (uninformed) | 120,027 | 49,493 |

#### 0.3 Label distribution and the naive benchmarks it implies

Listing letters among disclosers:
- **Apartments:** A 2.2, B 5.2, C 20.8, D 34.0, E 24.0, F 8.6, G 5.1 (%).
- **Houses:** A 2.4, B 4.5, C 21.7, D 33.5, E 24.4, F 8.5, G 5.0 (%).

So $\Pr(\theta=1\mid d=1)\approx 0.62$ in both segments.

**Unconditional entropy:**
- 7-class: $H(Y)=1.64$ nats (2.36 bits).
- Binary: $H(\theta)=0.66$ nats (0.96 bits).

**Majority-class benchmarks:**
- "Always D" gets 34% exact accuracy.
- "Always D" gets **79% within-one accuracy**, because C, D and E cover 79% of mass. Within-one accuracy is therefore uninformative unless it is reported next to this benchmark.
- "Always $\theta=1$" gets 62% accuracy.

**Registry letters among $K=1$ apartments:** A 0.3, B 1.8, C 23.7, D 34.2, E 24.6, F 9.7, G 5.8. A is much rarer in the registry (0.3%) than among listing letters (2.2%).

**Hiders ($K=1,d=0$):** their registry distribution is shifted toward F/G (apartments 21.4% vs. 15.5% for all $K=1$; houses 21.8% vs. 15.5%). The shift is modest and consistent with `FINDING-sigma1.md`.

#### 0.4 Label noise: listing letter vs. registry letter among $d=1,K=1$

| | Exact | Within one | Same $\theta$ (A–D cut) | Listing better | Listing worse |
|---|---|---|---|---|---|
| Apartments | 74.0% | 94.1% | 88.9% | 12.8% | 13.2% |
| Houses | 91.2% | 98.5% | 96.9% | 6.2% | 2.6% |

**Apartments.** Agreement rises with `match_score`: 82.8% above the median vs. 65.0% below. It is low for units under 40 m² (61.9% vs. 78.1%), and disagreement is **symmetric**. That pattern looks like **matching error** (the wrong unit in a multi-unit building) rather than strategic misreporting. Small units may also be affected by the July 2024 small-surface threshold revision **[CHECK date and scope]**.

**Houses.** Disagreement is **asymmetric** toward better listing letters (6.2% vs. 2.6%). Two explanations fit: post-renovation re-certification, or mild inflation. Either one is a caveat for the No-Falsification assumption, but not for this appendix.

#### 0.5 Duplicates and relistings

**Duplicate `listing_id` rows.** The enriched apartment file has 843,621 rows but 834,026 unique `listing_id`s. Houses have 687,878 rows and 658,990 unique ids. The multiplicity reaches 36, and 36–39% of the duplicated ids carry different prices. The pattern looks like price-revision rows that the ADEME merge then fanned out further. The raw file already has some of these duplicates (837,173 rows, 834,026 unique for apartments). **This is outside this appendix's scope, but it touches the paper's $N$. Flag it (§5, Q2).**

**Repeated properties.** Using (`address_id`, rounded `size_m2`, `floor_num`) as the property key, 48% of apartment listings and 46% of house listings share a key with another listing. That share mixes relistings, multi-agency listings and identical units in the same building. Among $d=1$ keys, 2.6% (apartments) and 1.3% (houses) display more than one distinct letter.

---

### 2.1 Design

#### 2.1.1 Object of interest and why it matters for the model

The disclosure game has bite only if the letter cannot be read off the listing. To state this formally, let buyers condition on $X$. Under $K\perp\theta\mid X$ and Corollary 1 ($\sigma_1=0$), the belief about a silent listing is

$$
e(X)\;=\;\Pr(\theta=1\mid d=0,X)\;=\;\frac{(1-\pi(X))\,\bar\theta(X)}{\pi(X)\,(1-\bar\theta(X))\,\sigma_0(X)+(1-\pi(X))}. \tag{A.1}
$$

If $\bar\theta(X)\in\{0,1\}$ almost surely, then $e(X)=\bar\theta(X)$ for every $\sigma_0$. Silence then carries no information beyond $X$, the hiding gain $\rho\beta_1 e(X)$ is zero for every low type, and $\sigma_0$ has no economic content.

The game is non-trivial only on the set of listings where $\bar\theta(X)$ is interior. A natural scalar summary of "how much is left for strategic inference" is the residual variance share

$$
1-R^2_\theta\;\equiv\;\frac{\mathbb{E}\big[\bar\theta(X)(1-\bar\theta(X))\big]}{\bar\theta(1-\bar\theta)},\qquad R^2_\theta=\frac{\operatorname{Var}(\bar\theta(X))}{\operatorname{Var}(\theta)}, \tag{A.2}
$$

which uses the decomposition $\operatorname{Var}(\theta)=\operatorname{Var}(\bar\theta(X))+\mathbb{E}[\bar\theta(X)(1-\bar\theta(X))]$. For a calibrated predictor, $R^2_\theta$ equals the Brier skill score.

**The binary $\theta$ is the key object.** The 7-class problem is reported because readers will think in letters, and because the rental-ban thresholds (G 2025, F 2028, E 2034) make some letter boundaries economically relevant in their own right.

#### 2.1.2 Samples

All samples use the 2022–24 structural window and run separately for apartments and houses.

| Label | Definition | Role |
|---|---|---|
| **S1** (discloser sample) | $d=1$, valid listing letter | Main training sample. Closest to "what the market reveals." Contains $d=1,K=0$ listings whose letter may be a pre-reform certificate (§2.2.4). |
| **S2** (truthful) | $d=1$, $K=1$, listing letter $=$ registry letter | Clean labels under the post-July-2021 method. **Preferred main sample.** |
| **S2′** | S2 with `match_score` ≥ median | Tightest label quality. Robustness. |
| **S3** (informed, pre-selection) | $K=1$, label $=$ registry letter, **any $d$** | Training sample that is not selected on disclosure (§2.2.1). |
| **H** (hiders) | $K=1$, $d=0$, label $=$ registry letter | **Evaluation only.** Measures how a classifier trained on S2/S3 performs on the listings buyers actually have to infer. |
| **U** (uninformed) | $K=0$, $d=0$ | No label. Prediction only: the distribution of $\hat{\bar\theta}(X)$ in the silent pool. |

**De-duplication, in two steps:**
1. One row per `listing_id`. Keep the earliest `start_date`, and the first price observation at that date.
2. One row per property. The property key is (`address_id`, `round(size_m2)`, `floor_num`, `rooms`), and within each key I keep the first listing in the window.

**Robustness to de-duplication.** Instead of dropping repeats, keep all listings and **group cross-validation folds by `address_id`**, so that no building appears in both train and test (§2.1.5). Grouping by building is needed in any case. Collective-heating buildings can carry unit DPEs generated from building-level data **[CHECK regulatory detail]**, and same-building units share envelope and heating. Leaving building-mates in both folds would overstate predictability.

#### 2.1.3 Nested feature sets

The feature sets are cumulative. Each one is a buyer-visible set; only re-pull status differs.

| Set | Contents | Available now? |
|---|---|---|
| **F0** | Built period only (`built_year` bins incl. NA) | yes |
| **F1** (hedonic structure) | F0 + `log(size_m2)` (spline) + `rooms` + `bathrooms` + `cellar` + (apartments) `floor` bin, `floor_num`, `elevator`. Missing-indicator categories kept, because missingness is visible to the buyer. | yes |
| **F2** (+ location) | F1 + location. **F2a**: `market_id` FE. **F2b**: + `city_id`. **F2c**: + `neighborhood_id` (+ `iris_id` if re-pulled). Also `cateaav2020_label`, `distance`, and listing quarter. | yes, except `iris_id` |
| **F3** (+ price) | F2 + log asking price per m², demeaned within market×quarter | yes |
| **F4** (+ re-pull) | F2 (or F3) + continuous build year binned at thermal-regulation dates (RT 1974/1988/2000/2005/2012; bins ≤1948, 1949–74, 1975–88, 1989–2000, 2001–05, 2006–12, ≥2013) + `energy_source_electric` + heating system (individual/collective; gas/electric/heat pump/wood/district) + `client_type` + agency FE (`realtor_ref`) + text features | needs re-pull |

**Location fixed effects with a classifier.** One-hot $\sim$8k neighbourhood dummies are feasible in a penalised logit, but they make ordered logit and gradient boosting awkward. The alternative is **out-of-fold target encoding**: the empirical-Bayes-shrunk share of $\theta=1$ (or the mean letter) by location, computed only on the training fold. Shrinkage is $\tilde m_\ell=(n_\ell\bar y_\ell+\kappa\bar y)/(n_\ell+\kappa)$, with $\kappa$ tuned in the inner CV. This mirrors a buyer's "local knowledge" of the letter distribution.

**Text features (F4).** Two complementary representations:
- **Dictionary indicators.** `rénové|rénovation`, `refait à neuf`, `double vitrage`, `simple vitrage`, `pompe à chaleur|PAC`, `chauffage collectif`, `chauffage individuel`, `chaudière gaz|condensation`, `radiateurs électriques|convecteurs`, `isolation (extérieure|des combles)`, `poêle|insert`, `haussmannien`, `pierre de taille`, `ancien`, `neuf|VEFA|BBC|RT 2012|RE 2020`, `travaux à prévoir|à rafraîchir|à rénover`, `plein sud|traversant`, `dernier étage`, `menuiseries PVC|alu`, `volets roulants`.
- **TF-IDF** on uni- and bi-grams (min_df ~ 50), passed through an L1-penalised logit or as sparse input to the GBM.

**Mandatory scrub before featurisation.** Remove any mention of the DPE itself: regex on `DPE`, `classe (énergie|énergétique)`, `étiquette`, `bilan énergétique`, single letters A–G adjacent to those tokens, `kWh`, `kgCO2`, `GES`, and numeric energy values. French listings frequently restate the letter in the text, and some text is boilerplate that marks the certificate as missing ("DPE vierge", "DPE en cours"). Scrub such boilerplate too, and report it separately as a candidate $d$-misclassification diagnostic.

**Price (F3) in and out.** The asking price is buyer-visible (the model's buyer observes $(d,p^{\text{list}},X)$), so it belongs in $X$. It is also endogenous to the label:
- For disclosers, $p^{\text{list}}$ capitalises $\beta_1\theta$, so price "reveals" a letter that is already on the page.
- In the model's equilibrium, the price of a silent listing is set at the pooled valuation and does **not** vary with $\theta$ given $X$. All silent sellers with the same $X$ post the same price: deviation would reveal type, and uninformed sellers of both types are informationally identical.

So report F2 and F3 side by side. The **difference** $\Delta_{\text{F3}-\text{F2}}$ evaluated on sample **H** (hiders) is a direct test of price pooling. The model predicts that adding price raises AUC on S2 but not on H. One caveat applies: price also loads on unobserved condition (photos), which correlates with $\theta$, so a non-zero $\Delta$ on H is not by itself a rejection. Compare it to $\Delta$ on S2.

#### 2.1.4 Models

**M-bin (headline): binary logit for $\theta$.**
$$\Pr(\theta=1\mid X)=\Lambda(X'\gamma)$$
with an L2 penalty when the specification is high-dimensional. This is the model's object $\bar\theta(X)$.

**M-ord: ordered (cumulative) logit for $Y$.**
$$\Pr(Y\le k\mid X)=\Lambda(\tau_k-X'\beta),\qquad k=1,\dots,6.$$
- **Proportional-odds check.** In the style of Brant (1990), fit the six binary logits $\mathbf 1[Y\le k]$ and test $H_0:\beta_1=\dots=\beta_6$ by Wald, using the stacked sandwich covariance.
- With $N\sim 3$–$6\times10^5$ the test will reject mechanically. Report an *economic* version alongside it: the out-of-sample log-loss gain of the generalised (non-proportional) ordered logit, or of a partial-proportional-odds logit relaxing only built period and heating, over M-ord.
- A cumulative logit with a single index will struggle to fit the letter distribution's U-shaped features (rare A/B, fat G among pre-1948 stock). The generalised ordered logit is the natural fix.

**M-mnl: multinomial logit.** Unrestricted. It is the benchmark for M-ord's restriction.

**M-gbm: gradient boosting, multiclass and binary.** LightGBM (or sklearn `HistGradientBoostingClassifier`). This is the **upper bound on predictability** from a given $X$, because it captures interactions such as period × floor × elevator × location.

The binary model and the multiclass-implied $\hat\Pr(\theta=1\mid X)=\sum_{k\le4}\hat p_k(X)$ should agree. Report both. A large disagreement signals miscalibration.

#### 2.1.5 Cross-validation

**CV1, main: 5-fold `GroupKFold` grouped by `address_id` (building).** Location effects are learned from *other buildings* in the same neighbourhood. That is the "buyer who knows the local stock" thought experiment, and it blocks within-building and relisting leakage.

**CV2, transportability: `GroupKFold` grouped by `market_id`.** Run it on F0/F1 only, plus `dept`-level effects. It answers how much is learnable from structure alone without local knowledge. Under market grouping, F2 location effects are unseen by construction, so do not run F2 in CV2.

**CV3, temporal.**
- Train on 2022 and test on 2023–24.
- Also train on 2022–23 and test on 2024.
- For apartments, exclude units under 40 m² from the cross-July-2024 test, or split at 2024-07-01, because of the small-surface threshold revision **[CHECK]**.
- Use price demeaned within market × quarter so that nominal drift is not learned.

**Nested CV for M-gbm.** Within each outer training fold, run a 3-fold inner `GroupKFold` (same grouping) and random or Bayesian search over:
- `num_leaves` ∈ [15, 255]
- `min_child_samples` ∈ [50, 2000]
- `learning_rate` ∈ [0.02, 0.1]
- `feature_fraction` ∈ [0.5, 1]
- `lambda_l2`

Use early stopping on inner validation log-loss. Penalty strength for the logits is tuned the same way. The target-encoding shrinkage $\kappa$ is tuned in the inner loop and computed out of fold.

#### 2.1.6 Metrics

Notation: $i$ indexes test observations ($n$ of them), $\hat p_{ik}=\hat\Pr(Y_i=k\mid X_i)$, $\hat y_i=\arg\max_k\hat p_{ik}$, $\hat q_i=\hat\Pr(\theta_i=1\mid X_i)$, and $\hat p^0_k$ is the training-fold unconditional share (or market-level share for benchmark B1).

**Accuracy and within-one accuracy**
- $\mathrm{Acc}=\frac1n\sum_i\mathbf 1[\hat y_i=Y_i]$.
- $\mathrm{Acc}_{\pm1}=\frac1n\sum_i\mathbf 1[|\hat y_i-Y_i|\le1]$. Always print the "always D" value (≈0.79) next to it.
- Balanced accuracy, i.e. mean per-class recall, as a supplement for the rare A/B/G classes.

**Confusion matrix**, row-normalised: $C_{jk}=\Pr(\hat y=k\mid Y=j)$.

**Multiclass log-loss** (cross-entropy):
$$\mathrm{LL}=-\frac1n\sum_i\log\hat p_{i,Y_i}.$$
Binary version: $-\frac1n\sum_i[\theta_i\log\hat q_i+(1-\theta_i)\log(1-\hat q_i)]$.

**Brier score**
- Multiclass: $\frac1n\sum_i\sum_k(\hat p_{ik}-\mathbf 1[Y_i=k])^2$.
- Binary: $\frac1n\sum_i(\hat q_i-\theta_i)^2$.
- **Brier skill score:** $\mathrm{BSS}=1-\mathrm{Brier}/\mathrm{Brier}_0$, which estimates $R^2_\theta$ in (A.2).

**AUC** for $\theta$: $\Pr(\hat q_i>\hat q_j\mid\theta_i=1,\theta_j=0)$.

**Normalised information gain** (out-of-sample McFadden pseudo-$R^2$):
$$\mathrm{IG}=1-\frac{\mathrm{LL}_{\text{model}}}{\mathrm{LL}_0},\qquad \mathrm{LL}_0=-\frac1n\sum_i\log\hat p^0_{Y_i}\approx H(Y).$$

Cross-entropy is a strictly proper score, and for any predictor $\mathbb{E}[\mathrm{LL}]\ge H(Y\mid X)$. So, asymptotically, $\mathrm{IG}\le I(Y;X)/H(Y)$: **out-of-sample IG is a lower bound on the share of letter uncertainty that $X$ resolves**, and the GBM gives the tightest one. Also report the model-implied conditional entropy $\bar H=\frac1n\sum_i H(\hat p_i)$ with $H(p)=-\sum_k p_k\log p_k$, and the ratio $1-\bar H/H(Y)$. For a calibrated model $\bar H\approx\mathrm{LL}$, so a gap flags over- or under-confidence.

**Calibration**
- Reliability diagram over 10–20 bins of $\hat q$.
- $\mathrm{ECE}=\sum_b\frac{n_b}{n}|\bar\theta_b-\bar q_b|$.
- Calibration-in-the-large and calibration slope, from $\operatorname{logit}\Pr(\theta=1)=a+b\operatorname{logit}\hat q$. The intercept $a$ on sample H is economically meaningful (§2.2.1).

**Decision-relevant metrics**
- Share of listings with $\max_k\hat p_{ik}>0.5$ and $>0.8$ ("the letter is effectively known").
- For $\theta$: share with $\hat q_i\notin[0.2,0.8]$.
- Mean posterior SD $\frac1n\sum_i\sqrt{\hat q_i(1-\hat q_i)}$ against the unconditional $\sqrt{\bar\theta(1-\bar\theta)}\approx0.485$.
- **Model-linked:** the distribution of $\hat q$ among true $\theta=0$ listings (the informed low types), because a low type's hiding gain is $\rho\beta_1e(X)\le\rho\beta_1\bar\theta(X)$.

**Inference.** Use a fold-level standard error, or a cluster bootstrap by `address_id` over the out-of-fold predictions (B = 200).

#### 2.1.7 Benchmarks

- **B0:** national training-fold shares.
- **B1: market-level shares $\hat{\bar\theta}_m$.** This is exactly the scalar prior the structural model currently uses. **The headline contrast is best model vs. B1.** It measures how much listing-level conditioning adds to what the model already assumes buyers know.
- **B2:** built period only (F0, logit).
- **B3:** built period × market (cell shares, shrunk).

---

### 2.2 Caveats and the link to the structural model

#### 2.2.1 Selection on disclosure, and how the registry solves it

A classifier trained on disclosers estimates $\Pr(\theta\mid X,d=1)$, not the buyer-relevant prior $\bar\theta(X)$. Under the model (No Falsification, $K\perp\theta\mid X$), Bayes' rule gives three relations in odds form, with $\mathrm{odds}(q)\equiv q/(1-q)$:

$$
\mathrm{odds}\,\Pr(\theta=1\mid X,d=1)=\mathrm{odds}\,\bar\theta(X)\cdot\frac{1-\sigma_1(X)}{1-\sigma_0(X)}, \tag{A.3}
$$
$$
\mathrm{odds}\,\Pr(\theta=1\mid X,K=1,d=0)=\mathrm{odds}\,\bar\theta(X)\cdot\frac{\sigma_1(X)}{\sigma_0(X)}, \tag{A.4}
$$
$$
\Pr(\theta=1\mid X,K=1)=\bar\theta(X). \tag{A.5}
$$

**Implications:**

1. **Hiding rates that do not vary with $X$ distort only the intercept.** If $\sigma_0,\sigma_1$ are constant within the estimation unit, the discloser-trained logit index equals the true index plus the constant $\log\frac{1-\sigma_1}{1-\sigma_0}$. Ranking metrics (AUC, the confusion pattern up to a threshold shift) are unaffected, and only calibration moves. With $\hat\sigma_0\approx0.08$ and $\hat\sigma_1\approx0.06$ (FINDING-sigma1, apartments, A–D cut), the shift is $\approx0.02$ in log-odds, which is negligible. If hiding rates depend on $X$, the distortion is $X$-dependent and the discloser classifier is biased in shape.
2. **Train on S3, not S1.** By (A.5), the registry sample $K=1$ (all $d$) identifies $\bar\theta(X)$ directly, **provided $K\perp\theta\mid X$**. $K$ is selected on certification timing and on address-match success, not on disclosure. The match uses `address_id`, area and floor (`ADEME/match_improved.py`), so $K$ depends on $X$ (geocoding precision, building size). That makes $K\perp\theta\mid X$ more credible than the unconditional $K\perp\theta$ of Assumption 1. Neither statement implies the other, so state the conditional one explicitly.
3. **The hider evaluation is an $X$-conditional test of Corollary 1.** Apply the S3-trained model to sample H. The fitted calibration intercept $a_H$ from $\operatorname{logit}\Pr(\theta=1)=a+\operatorname{logit}\hat q$ estimates $\log(\sigma_1/\sigma_0)$ by (A.4), averaged over the hider distribution of $X$.
   - The model predicts $a_H\to-\infty$ (all hiders are low).
   - FINDING-sigma1's unconditional ratio $\hat\sigma_1/\hat\sigma_0\approx0.79$ (apartments, A–D) suggests $a_H\approx-0.24$.
   - Running this conditional on $X$ removes the compositional confound in the unconditional comparison: hiders may simply be concentrated in locations or periods with worse stock.
   - Estimating $a_H(\hat q)$ by bins of $\hat q$ traces how $\sigma_1/\sigma_0$ varies with the prior.
4. **IPW alternative.** If S1 is used, reweight disclosers by $1/\widehat\Pr(d=1\mid X,K=1,\theta)$, estimated on S3. This needs $\theta$, so in practice it collapses to training on S3. Report the IPW-S1 model only as a consistency check.

**The consequence for Task 1 needs flagging now.** If $\sigma_1(X)=\sigma_0(X)$, then (A.1), generalised to $\sigma_1>0$, gives

$$e(X)=\frac{\pi\bar\theta\sigma+(1-\pi)\bar\theta}{\pi\sigma+(1-\pi)}=\bar\theta(X).$$

The Bayesian belief equals the prior. **The Bayesian belief and the cursed (anchor) belief then coincide, and the cursedness weight $\chi$ is not identified.** Identification of $\chi$ requires $\sigma_1(X)\neq\sigma_0(X)$ on a set of positive measure, and the hider evaluation in item 3 measures exactly that.

#### 2.2.2 Using $\hat{\bar\theta}(X)$ as a model object

**Buyer's prior.** A rational-expectations buyer who conditions on $X$ uses $\bar\theta(X)$ as the prior. The silent-listing belief becomes (A.1). The scalar model is the special case $\bar\theta(X)=\bar\theta_m$, $\pi(X)=\pi_m$. Treat $\hat{\bar\theta}(X)$ as a sufficient statistic for what $X$ tells the buyer about $\theta$. That is exact when the buyer's prior is $\Pr(\theta\mid X)$ and $X$ enters valuations separately through $\sum_n\beta_nX_n$.

**What changes in equilibrium.** If buyers condition on $X$, each $X$-cell is its own disclosure game. Hold $(c_0,\rho,\beta_1,\pi)$ fixed at market level and let $\kappa\equiv c_0/(\rho\beta_1)\in(0,1)$. Applying Proposition 2 cell by cell gives:

$$
\sigma_0^*(X)=\begin{cases}
0 & \bar\theta(X)\le\kappa \quad\text{(cost-deterred)}\\[2pt]
\dfrac{(1-\pi)\,(\bar\theta(X)/\kappa-1)}{\pi\,(1-\bar\theta(X))} & \kappa<\bar\theta(X)<\bar\theta^{\dagger}\quad\text{(partial pooling)}\\[6pt]
1 & \bar\theta(X)\ge\bar\theta^{\dagger}\equiv\dfrac{\kappa}{1-\pi(1-\kappa)} \quad\text{(complete adverse selection)}
\end{cases} \tag{A.6}
$$

**Derived properties.** On the interior branch,
$$\partial\sigma_0^*/\partial\bar\theta=(1-\pi)(1/\kappa-1)/[\pi(1-\bar\theta)^2]>0,$$
because $\kappa<1$ whenever the interior is non-empty. Therefore:
- $\sigma_0^*(X)$ is weakly increasing in $\bar\theta(X)$.
- The premium of silent listings over disclosed-$\theta{=}0$ listings is $\rho\beta_1\bar\theta(X)$ (rising), then flat at $c_0$, then $\rho\beta_1(1-\pi)\bar\theta(X)/(1-\pi\bar\theta(X))$ (rising).

These follow algebraically from Proposition 2 applied per cell. The conjecture is that market-level $c_0$ is the right primitive, i.e. that the hiding cost does not vary with $X$.

**Moments this creates.** In order of how cheap they are and how safe to use:

1. **$R^2_\theta$ within market** (A.2), i.e. $\operatorname{Var}(\hat{\bar\theta}(X)\mid m)/[\bar\theta_m(1-\bar\theta_m)]$. If it is small, the scalar-prior model loses little. If it is large, the scalar $\hat c_{0,m}$ is a mixture over regimes. By the law of iterated expectations the *average* silent premium is still $\rho\beta_1\mathbb{E}[e(X)\mid d=0,m]$, but the inversion premium $=c_0$ holds only on the interior cells. **Diagnostic, report first.**
2. **Hiding-rate gradient.** On S3, estimate $\Pr(d=0\mid K=1,\theta=0,\hat{\bar\theta}(X)\text{ bin})$. (A.6) predicts a weakly increasing gradient and a zero region below $\kappa$. **Overidentifying test**, using the registry.
3. **Premium profile.** Plot the hedonic price of silent minus disclosed-low listings, by $\hat{\bar\theta}(X)$ bin within market. Bayesian buyers in partial pooling predict a flat segment at $c_0$. **Overidentifying test.**
4. **Hiding-free mass.** The share of informed-low mass with $\hat{\bar\theta}(X)<\hat\kappa_m=\hat c_{0,m}/(\hat\rho_m\hat\beta_{1,m})$: listings for which concealment cannot pay at the estimated primitives.

**Recommendation.** Report moment 1 in this appendix. Present moments 2–3 as tests in a follow-up (V2-QUEUE) rather than as estimating moments in the JMP. Turning them into estimating moments changes the equilibrium object from a market scalar to a cell-level fixed point.

**Measurement.** $\hat{\bar\theta}(X)$ is an estimate of the econometrician's prior, not the buyer's. Using it as a regressor attenuates the gradients in moments 2–3 toward zero (generated-regressor and measurement-error problem). Use out-of-fold predictions and bootstrap the two stages jointly.

#### 2.2.3 Econometrician's $X_E$ vs. buyer's $X_B$

The predictability measured here is bounded on both sides, and the two bounds point in opposite directions.

- **$X_B\supset X_E$, so predictability here is a lower bound on what buyers can know.** Buyers see photos (windows, radiators, façade, condition), full text, the visit, and possibly, after learning the address, the **public ADEME registry**. That last channel is part of $c_0$ in the paper's own interpretation; it is not part of the prior. By the data-processing inequality, $I(\theta;X_E)\le I(\theta;X_B)$.
- **Processing limits, so predictability here is an upper bound on what buyers do with $X_E$.** The classifier learns from roughly $3\times10^5$ labelled listings, neighbourhood-level stock composition and high-order interactions. A buyer has neither the data nor the computation.

The appendix's claim should therefore be stated narrowly. *"The structured content of a listing, even with location and price, leaves [XX]% of the binary uncertainty unresolved, so the letter cannot be read off the page; residual uncertainty from photos and visits is not measured."*

F4's text dictionary partially proxies the photo channel (renovation and glazing keywords). An image model trained on listing photos is the natural extension and requires photo URLs (§5).

**Link to Task 1 (anchoring, cursed buyers).** In a cursed-belief model,
$$e_\chi(X)=(1-\chi)\,e_{\text{Bayes}}(X)+\chi\,\bar\theta(X).$$
The anchor is exactly $\bar\theta(X)$, so this exercise supplies the anchor listing by listing. A naïve buyer might instead anchor on the observed *discloser* distribution $\Pr(\theta\mid X,d=1)$. By (A.3) the two candidate anchors differ by the odds factor $(1-\sigma_1)/(1-\sigma_0)\approx1$, so in these data they are empirically indistinguishable, which is good news for Task 1's robustness. Separately, $\chi$ is identified only where $\sigma_1\neq\sigma_0$ (§2.2.1).

#### 2.2.4 Other caveats

- **Label noise.** Listing and registry letters disagree on 26% (apartments) and 9% (houses) of $d=1,K=1$ listings, mostly by one letter (§0.4). Train on S2 and S2′, and evaluate on both clean and noisy labels. Label noise caps attainable accuracy, but it is not a structural ceiling: noise driven by matching error (the wrong unit in the same building) is itself partly predictable from building features. Hider labels (sample H) cannot be cross-checked, so their noise is inherited from the match. Restrict H to `match_score` ≥ median as a robustness check.
- **2021 methodology break.** The opposable DPE (3CL-2021) from July 2021 changed the letter mapping, including the double threshold and the primary-energy factor for electricity. Letters issued under the old method are not comparable.
  - Pre-reform certificates stayed legally valid for a time: those issued 2013–17 until end-2022, and those issued 2018–June 2021 until end-2024 **[CHECK against §3.1 of the paper]**.
  - So some $d=1,K=0$ listing letters in 2022–24 are old-method letters. This is the reason S2/S3, not S1, should be the main sample.
  - Also check for transitional corrections to the method in autumn 2021 **[CHECK]**. They mostly predate the 2022–24 window.
- **July 2024 small-surface revision.** The thresholds for units under 40 m² changed, so letters may differ between registry and listing **[CHECK]**. 22% of apartments are under 40 m². Agreement is 62% for these units vs. 78% for the rest.
- **Building-level DPEs and collective heating.** These produce strong within-building correlation. Group CV by `address_id` (§2.1.5). This is also why `heating: collectif` (F4) is likely highly predictive.
- **Class imbalance.** A/B make up roughly 2–7% and G roughly 5%. Do not re-weight for probability estimation, because that miscalibrates. Report balanced accuracy and per-class recall as supplements. The binary $\theta$ is roughly balanced (62/38).
- **Missingness is strategic and visible.** `built_year_NA` (40% of apartments) is buyer-visible and may correlate with $d$. That is fine for $X$, but report predictive performance separately for listings with and without built year.
- **Duplicates** (§0.5). De-duplicate before anything else.

---

### 2.3 Draft appendix (LaTeX-ready)

Conventions: natbib, `\toprule\toprule` (house style in `A-robustness.tex`), `\small`, notes in `\footnotesize\textit{Notes:}`, and `[XX]` placeholders. Keys present in `paper/DPE_library.bib`: `milgrom_good_1981`, `grossman_informational_1981`, `dye_disclosure_1985`, `jung_kwon_1988`, `brounen_kok_2011`, `fuerst_energy_2016`, `myers_mandatory_2022`. Keys marked **[CHECK]** below are placeholders that are not in the bib and must be verified before use.

```latex
% =====================================================================
% APPENDIX -- Can buyers infer the EPC from the listing?
% Referenced from §4.1 (Setup: buyers observe (d, p^list, X), not theta).
% =====================================================================

\section{Can Buyers Infer the EPC from the Listing?}
\label{app:epc_inference}

The disclosure game in Section~\ref{ss:model_setup} presumes that a buyer facing a silent
listing does not already know its energy performance. If the letter could be read off the
listing's other content (its construction period, floor, heating, location, or price),
silence would carry no information beyond what the buyer already sees, the hiding gain of a
low-quality seller would vanish, and the unraveling logic of
\citet{grossman_informational_1981} and \citet{milgrom_good_1981}, as well as its
partial-unraveling refinements \citep{dye_disclosure_1985, jung_kwon_1988}, would have no
bite. This appendix measures how much of the EPC is recoverable from what a listing shows.

\paragraph{Design.}
We train classifiers on listings whose letter is known and ask how well they predict it out
of sample. The labelled sample consists of disclosed listings from 2022--2024 whose displayed
letter coincides with the ADEME-registry letter ($N=[XX]$ apartments, $[XX]$ houses), which
removes label noise and pre-reform certificates.\footnote{We keep one listing per property,
defined by address, surface, and floor. Listing and registry letters coincide for
$[74.0]\%$ of matched apartment disclosures and $[91.2]\%$ of house disclosures.} Predictors
are nested: (F1) structural attributes (surface, rooms, bathrooms, floor, elevator, cellar,
construction period); (F2) adds location at the neighbourhood level; (F3) adds the asking
price per square metre, demeaned within market and quarter; and (F4) adds heating type and
keyword indicators from the listing description, with every mention of the certificate itself
removed. We estimate a binary logit for $\theta$ (A--D versus E--G), the object the model
uses, and an ordered logit, a multinomial logit, and gradient-boosted trees
\citep{ke_lightgbm_2017} [CHECK] for the seven letters. Boosted trees serve as an upper
bound on what these predictors can deliver. Folds are grouped by building, so that relistings
and units sharing a building-level certificate never straddle training and test data, and a
temporal split (train 2022, test 2023--2024) guards against drift. Benchmarks are the
market-level share $\bar\theta_m$, which is the prior the structural model assigns buyers,
and construction period alone.

We measure predictability with the out-of-sample information gain
$\mathrm{IG}=1-\mathrm{LL}_{\text{model}}/\mathrm{LL}_0$, the share of the unconditional
entropy of the letter that the predictors resolve. Because cross-entropy is a proper scoring
rule \citep{gneiting_raftery_2007} [CHECK], $\mathrm{IG}$ is a lower bound on the mutual
information share $I(Y;X)/H(Y)$. For the binary quality we also report the AUC and the
explained-variance share
$R^2_\theta=\operatorname{Var}(\bar\theta(X))/\operatorname{Var}(\theta)$, where
$\bar\theta(X)\equiv\Pr(\theta=1\mid X)$.

\paragraph{Results.}
Table~\ref{tab:epc_inference} reports the results. Structural attributes alone resolve
$[XX]\%$ of the letter's entropy, and location raises this to $[XX]\%$. The most flexible
model, with price, reaches $[XX]\%$ exact accuracy against $[34]\%$ for always predicting the
modal letter D. For the binary quality the AUC is $[XX]$, but the predicted probability lies
outside $[0.2,0.8]$ for only $[XX]\%$ of listings, and the mean posterior standard deviation
of $\theta$ is $[XX]$, against an unconditional $[0.49]$. Errors are concentrated on adjacent
letters, mainly D versus E (Table~\ref{tab:epc_confusion}), which is precisely the boundary
that defines $\theta$. Relative to the market-level prior, listing-level conditioning raises
$R^2_\theta$ by $[XX]$ points.

\paragraph{Selection and the informed non-disclosers.}
A classifier trained on disclosers estimates $\Pr(\theta\mid X,d=1)$ rather than the buyer's
prior $\bar\theta(X)$. Under the model the two differ only by the odds factor
$(1-\sigma_1)/(1-\sigma_0)$, which shifts the intercept but leaves the ranking of listings
unchanged. The registry allows a direct check. Re-training on all registry-matched listings,
disclosed or not, which by Assumption~\ref{ass:independence} applied conditionally on $X$
recovers $\bar\theta(X)$, changes the AUC by $[XX]$. Evaluated on informed non-disclosers,
whose certified letter we observe, the classifier's calibration intercept is $[XX]$; by
Bayes' rule this estimates $\log(\sigma_1/\sigma_0)$ conditional on observables. Adding the
asking price raises the AUC by $[XX]$ among disclosers but by only $[XX]$ among informed
non-disclosers, consistent with silent listings pooling on price as the model requires.

\paragraph{Interpretation.}
The letter is not recoverable from a listing's structured content: even the most flexible
model leaves $[XX]\%$ of the binary uncertainty unresolved, and the inference a buyer must
draw from silence is therefore not redundant. Two qualifications bound this statement. Our
predictors omit photographs and visits, so buyers may know more than we measure; but our
classifiers also exploit a volume of local data no individual buyer processes, so buyers who
reason from observables alone are likely to know less. Our conclusion is narrow: in these
data, the listing itself does not reveal the letter.

\begin{table}[htbp]
\centering
\caption{Out-of-sample predictability of the EPC from listing content}
\label{tab:epc_inference}
\small\renewcommand{\arraystretch}{1.15}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}ll*{5}{c}@{}}
\toprule\toprule
\textbf{Model} & \textbf{Predictors} & \textbf{Accuracy} & \textbf{Within one} &
\textbf{Log-loss} & \textbf{Info.\ gain} & \textbf{AUC($\theta$)} \\
\midrule
\multicolumn{7}{l}{\textit{Panel A: Apartments} ($N=[XX]$)} \\[2pt]
Modal letter (D)        & --        & [0.34] & [0.79] & [1.64] & 0      & 0.50 \\
Market share $\bar\theta_m$ & Market & [XX] & [XX] & [XX] & [XX] & [XX] \\
Logit / ordered logit   & Period    & [XX] & [XX] & [XX] & [XX] & [XX] \\
Ordered logit           & F1        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Ordered logit           & F2        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Multinomial logit       & F2        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Boosted trees           & F2        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Boosted trees           & F3        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Boosted trees           & F4        & [XX] & [XX] & [XX] & [XX] & [XX] \\
\midrule
\multicolumn{7}{l}{\textit{Panel B: Houses} ($N=[XX]$)} \\[2pt]
Modal letter (D)        & --        & [0.34] & [0.80] & [1.63] & 0      & 0.50 \\
Market share $\bar\theta_m$ & Market & [XX] & [XX] & [XX] & [XX] & [XX] \\
Logit / ordered logit   & Period    & [XX] & [XX] & [XX] & [XX] & [XX] \\
Ordered logit           & F1        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Ordered logit           & F2        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Multinomial logit       & F2        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Boosted trees           & F2        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Boosted trees           & F3        & [XX] & [XX] & [XX] & [XX] & [XX] \\
Boosted trees           & F4        & [XX] & [XX] & [XX] & [XX] & [XX] \\
\bottomrule\bottomrule
\end{tabular*}

\vspace{0.5em}
\raggedright
\footnotesize
\textit{Notes:} Out-of-sample metrics from five folds grouped by building; listings from
2022--2024 with displayed letter equal to the ADEME-registry letter, one listing per
property. Accuracy and within-one accuracy refer to the seven letters A--G; log-loss is the
multiclass cross-entropy in nats; information gain is $1-\mathrm{LL}/\mathrm{LL}_0$ with
$\mathrm{LL}_0$ the cross-entropy of training-fold national shares. AUC($\theta$) is for
A--D versus E--G, from the binary logit (logit rows) or from summed class probabilities
(other rows). F1: surface, rooms, bathrooms, floor, elevator, cellar, construction period.
F2: F1 plus neighbourhood (out-of-fold, shrunk target encoding) and listing quarter. F3: F2
plus log asking price per m$^2$ demeaned within market and quarter. F4: F2 plus heating type
and description keywords, certificate mentions removed. Boosted-tree hyperparameters are
chosen by nested cross-validation.
\end{table}

\begin{table}[htbp]
\centering
\caption{Confusion matrix, best specification (row-normalised, \%)}
\label{tab:epc_confusion}
\small\renewcommand{\arraystretch}{1.15}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l*{7}{c}c@{}}
\toprule\toprule
& \multicolumn{7}{c}{\textbf{Predicted letter}} & \\
\cmidrule(lr){2-8}
\textbf{True letter} & A & B & C & D & E & F & G & \textbf{Share} \\
\midrule
A & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
B & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
C & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
D & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
E & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
F & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
G & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] & [XX] \\
\bottomrule\bottomrule
\end{tabular*}

\vspace{0.5em}
\raggedright
\footnotesize
\textit{Notes:} Apartments, boosted trees with predictors F3, out-of-fold predictions. Each
row gives the distribution of the predicted (modal) letter for listings with the given true
letter; rows sum to 100. The binary quality cut lies between D and E. The final column gives each letter's share of the sample.
\end{table}
```

**Figure suggestions** (route through `pyplot-specialist` per `collaboration-mode.md`):
1. **Confusion heatmap**, row-normalised, apartments | houses, with a line at the D/E boundary. This can replace `tab:epc_confusion` in the main appendix and leave the table for a supplement.
2. **Distribution of $\hat{\bar\theta}(X)$ for true $\theta=1$ vs. $\theta=0$.** Overlaid densities, with the market-level $\bar\theta_m$ marked, and the band $\hat\kappa_m$ from (A.6) shaded if available. This is the figure that "shows" that the letter is not on the page.
3. **Information gain across nested feature sets** (B1 → F0 → F1 → F2 → F3 → F4), grouped bars by model, with bootstrap CIs.
4. **Reliability diagram** for $\theta$ under three training regimes (S2-trained on S2, S3-trained on S3, S3-trained on H). The vertical offset on H is $\hat a_H\approx\log(\hat\sigma_1/\hat\sigma_0)$.
5. **Disclosers vs. informed hiders.** ROC curves on S2 vs. H, for F2 and F3. The F3−F2 gap visualises the price-pooling test.

#### Implementation sketch (plan for a future `scripts/epc_predictability.py`; not created)

```python
# --- data ---------------------------------------------------------------
cols = [...buyer-visible..., "d","EPC","K","ademe_epc_letter","match_score","listing_id","start_date"]
df = read_parquet(f"data/listings_enriched_{seg}.parquet", columns=cols)
df = df.query("2022 <= start_date.dt.year <= 2024")
df = df.sort_values("start_date").drop_duplicates("listing_id")          # §0.5 fan-out
df = df.merge(read_parquet(raw, columns=["listing_id","address_id"]).drop_duplicates("listing_id"))
df["prop_key"] = hash(address_id, round(size_m2), floor_num, rooms)
df = df.drop_duplicates("prop_key")                                       # or keep + group CV
L = {"A":1,...,"G":7}
S2 = df.query("d==1 & K==1 & EPC==ademe_epc_letter"); y7 = S2.EPC.map(L); th = (y7<=4)
S3 = df.query("K==1");  y7_S3 = S3.ademe_epc_letter.map(L)
H  = df.query("K==1 & d==0")

# --- features -----------------------------------------------------------
F1 = onehot(built_year, rooms, bathrooms, floor, cellar, elevator) + spline(log size_m2)
F2 = F1 + OOF_TargetEncoder(neighborhood_id, city_id, market_id; smooth=kappa) + quarter
F3 = F2 + (log_price - mean_by(market_id, quarter))
# F4 after re-pull: + heating, energy_source_electric, client_type, realtor TE, text TF-IDF (scrubbed)

# --- CV -----------------------------------------------------------------
outer = GroupKFold(5).split(X, groups=address_id)                 # CV1
# CV2: GroupKFold by market_id on F0/F1; CV3: year-based split
for tr, te in outer:
    # binary logit:   LogisticRegression(penalty="l2", C tuned in inner GroupKFold(3))
    # ordered logit:  statsmodels OrderedModel(y7, X_dense, distr="logit") on F1 + market TE
    #                 (or mord.LogisticAT on sparse X); generalized ordered = 6 binary logits
    # multinomial:    LogisticRegression(multi_class="multinomial")
    # GBM:            lightgbm.LGBMClassifier(objective="multiclass"/"binary"),
    #                 inner GroupKFold(3) + Optuna/RandomSearch, early stopping on logloss
    store out-of-fold p_hat (7-class) and q_hat (binary)

# --- metrics ------------------------------------------------------------
acc, acc_pm1, bal_acc, confusion(normalize="true"), log_loss, brier, roc_auc,
IG = 1 - LL/LL0, Hbar = mean(entropy(p_hat)), BSS, ECE, calib (a,b) via logit(theta) ~ a + b logit(q_hat),
share(max p_hat > .5/.8), share(q_hat outside [.2,.8]), mean sqrt(q(1-q))
cluster bootstrap over address_id (B=200) on OOF predictions

# --- selection / model link --------------------------------------------
fit on S3 -> predict H: a_H = intercept of logit(theta) ~ offset(logit q_hat)   # log(s1/s0)
a_H by q_hat deciles; DeltaAUC(F3-F2) on S2 vs H
R2_theta within market = Var(q_hat | m) / [thbar_m (1-thbar_m)]
P(d=0 | K=1, theta=0, q_hat bin)   # hiding-rate gradient, eq. (A.6)
```

**Practical notes:**
- `statsmodels.OrderedModel` with thousands of dummies is slow. Use target encoding or market FE only for M-ord, and leave high-dimensional location to the GBM and the penalised logits.
- LightGBM's native categorical handling on `neighborhood_id` overfits. Prefer out-of-fold target encoding.
- Memory: S2 has about 290k apartment rows × fewer than 100 dense columns, which is trivial. TF-IDF stays sparse.

---


---

## Task 1, Part II: The attention mechanism (rewritten 2026-10-05)

> **Superseded by Part III** for the model and the estimates. The level calibration in A.0/A.6 is withdrawn (Part III §5.6). Sections A.12–A.15 (cross-check, agency data, friction, old certificates) remain the record of how we got there.

*This part replaces the first sketch of the attention story. It takes as given Bastien's point that the hedonic indices already control for composition. Algebra is sympy-checked. Calibrations use the index gaps reproduced in §1.1 [E]. Labels as above: [D] derived, [A] assumption, [C] conjecture, [E] exploratory.*

### A.0 Summary

1. **The mechanism.** Energy costs enter a buyer's valuation only when the listing puts them in front of her. A displayed label of any grade does that, and since 1 January 2022 so does the euro estimate of the annual bill that accompanies it. When nothing is displayed, an inattentive buyer does not form a belief about energy at all. She falls back on a default, and the natural default for a cost nobody mentioned is "nothing out of the ordinary".
2. **Why it breaks the model's ceiling.** Belief-based channels cannot price silence above a verified A–D listing. They only move the buyer's belief inside $[C_1, C_0]$ (§1.1, §1.3). Attention replaces the belief with a *default*. If the default is more optimistic than the average A–D cost, silence beats A–D (Proposition A2). Inattention alone is not enough: a default equal to the prior mean reproduces the cap (Corollary A2).
3. **It nests the current model.** Full attention ($\alpha_0=\alpha_1=1$) returns $D=e\,B$ exactly (Proposition A1).
4. **The calibration** [E] (ratio of market means; the market-level regression in A.12 gives $a_{\rm apt}=0.21$ (se 0.11), $a_{\rm house}=0.96$ (se 0.04)). The data identify a single ratio, $a=\alpha_0/\alpha_1$: how much attention silent listings receive relative to displayed ones.
   - **Apartments:** $a\approx0.00$ before the reform and $\approx0.08$ after. Silence is priced almost exactly as if energy did not exist.
   - **Houses:** $a\approx1$ in every period, i.e. fully attentive, which is the current model.
   - The current model fits houses and fails apartments, and attention explains why in one parameter.
5. **Seller side.** If silence pays for every grade, hiding stops being a Milgrom–Dye choice by low types. It becomes a compliance decision. This predicts $\sigma_1>0$ and $\sigma_0-\sigma_1$ proportional to the green premium. It explains the FINDING-sigma1 pattern ($\hat\sigma_1\approx\hat\sigma_0$) that the current model cannot.
6. **Identification.** $\rho\alpha_1$ comes from the green premium and the anchor (the paper's $\hat\rho$, reinterpreted). The perceived cost of silence $C^*$ comes from the premium. $a$ comes from the **pass-through of the silent pool's true composition into the silent price**, which the registry lets us compute. The inattentive default $C^D$ comes from the level. A falsifiable bound follows: $D/B\le C_0/(C_0-C_1)$ market by market.

---

### A.1 Intuition: inattention versus naive inference

The faculty's phrasing was that buyers who see a bad letter anchor on it, and buyers who see nothing anchor on other signals (location, photos, price). There are two ways to formalise "anchor on other signals". They have opposite implications.

| | Naive / cursed inference (§1.3 (i)–(ii)) | Inattention (this part) |
|---|---|---|
| Does the buyer think about energy when no label is shown? | Yes | No |
| What replaces the missing label? | A belief about the letter, e.g. the prior $\bar\theta(X)$ instead of the Bayesian $e$ | A *default cost*, whatever the buyer implicitly assumes when the topic never comes up |
| Range of the silent valuation | Between the worst and the best letter | Unrestricted: the default can be better than any certified letter |
| Can silence beat verified A–D? | No (Proposition 4) | Yes, iff the default is optimistic enough (Proposition A2) |

The key distinction is between *how* buyers infer and *whether* they think about the attribute at all. The second is the standard object in the salience and shrouded-attribute literature:
- consumers under-weight costs that are not posted (Chetty, Looney & Kroft 2009; Finkelstein 2009);
- consumers under-weight costs that are shrouded (Gabaix & Laibson 2006; Brown, Hossain & Morgan 2010);
- consumers under-weight costs that are not in focus (Kőszegi & Szeidl 2013; Bordalo, Gennaioli & Shleifer 2013).

In each case the bias is *toward zero*, not toward the mean.

**Housing-specific reasons the default may be near zero for apartments.**
- **Bundled costs.** Under collective heating, energy is paid through co-ownership charges. The buyer budgets "price + charges" and never sees energy as a separate line.
- **Mental accounting.** Buyers coming from renting often had heating included, or paid small bills in small units.
- **Decision speed.** In tight urban markets, visits are short and decisions fast.

None of these is proven [C]. They are why the parameter is plausible, not evidence that it is right.

---

### A.2 Primitives

The paper's structure is kept: $K$, $d$, $\pi$, $\bar\theta$, $\sigma_\theta$, No Falsification, and $K\perp\theta$. Three objects change.

**[A-1] Energy enters as a cost.** A property of quality $\theta\in\{0,1\}$ carries a capitalised energy cost $C_\theta$ (log-price points), with $C_0>C_1>0$. With letters, $C_k$ is increasing from A to G. The anchor already builds this object: $C_\theta\propto\bar E_\theta\,p^E a(r,T)/P_m$ (`rho_identification.py`; `data_prep.py:417–425`). The binary $\beta_1$ of the paper is $C_0-C_1$.

**[A-2] Buyers.** A share $1-\rho$ is EPC-insensitive and values the property at $V(X)+\xi$ regardless of $d$. A share $\rho$ is sensitive. A sensitive buyer is *attentive* to energy with a probability that depends on what the listing shows:
$$\Pr(\text{attentive}\mid d=1)=\alpha_1,\qquad \Pr(\text{attentive}\mid d=0)=\alpha_0,\qquad 0\le\alpha_0\le\alpha_1\le1.$$
- An attentive buyer subtracts the rational expected cost: $C_\theta$ if a label is displayed, $\bar C^N\equiv E[C\mid d=0]$ otherwise.
- An inattentive buyer subtracts a default $C^D\ge0$.

**[A-3] Display triggers attention.** The restriction $\alpha_0\le\alpha_1$ says a displayed label weakly raises attention. That is the content of the July 2021 opposability, the January 2022 € display, and the "consommation excessive" mention for F/G.

**[A-4] Pricing.** The paper's linear pricing rule is kept (main.tex:485): the price equals the buyer-share-weighted mean valuation. A.5 shows the ordering results survive the exact logit-demand model.

*(Removed at Bastien's request, 2026-10-09: dispersed hiding costs are no longer part of the analysis.)*

**[A-6] Unobserved quality.** $E[\xi\mid K,\theta,d,X]=E[\xi\mid X]$. Bastien's indices control composition, so $\xi$ is set aside here. A.9 says what would bring it back.

**Equivalent representative-buyer form.** Under linear pricing, a population in which a share $\alpha_0$ is attentive is observationally equivalent at the mean price to a single buyer who puts weight $m=\alpha_0$ on $\bar C^N$ and $1-m$ on $C^D$. This is Gabaix's (2014, 2019) sparsity weight. The two forms differ only in the *shape* of demand under logit (A.5). The notation below uses shares.

---

### A.3 Prices

**Lemma A0 (perceived deduction) [D].** The mean cost subtracted by a sensitive buyer is
$$\mathcal D(d{=}1,\theta)=\alpha_1C_\theta+(1-\alpha_1)C^D,\qquad \mathcal D(d{=}0)=\alpha_0\bar C^N+(1-\alpha_0)C^D,$$
and prices at reference $X$ are $p=V(X)-\rho\,\mathcal D$.

**Gaps relative to disclosed-low** (the paper's estimands $B$ and $D$, eq. 0.1):
$$B\equiv p_H-p_L=\rho\,\alpha_1\,(C_0-C_1), \tag{A.1}$$
$$D\equiv p_N-p_L=\rho\big[\alpha_1(C_0-C^D)-\alpha_0(\bar C^N-C^D)\big], \tag{A.2}$$
$$\bar C^N=e\,C_1+(1-e)\,C_0,\qquad e=\frac{\pi\bar\theta\sigma_1+(1-\pi)\bar\theta}{\pi\bar\theta\sigma_1+\pi(1-\bar\theta)\sigma_0+(1-\pi)}. \tag{A.3}$$
(Sympy: `B = α₁ρ(C₀−C₁)`; `D` as stated.)

**Proposition A1 (nesting) [D].** If $\alpha_0=\alpha_1=1$, then $D=e\,B$. This is the paper's model, including its cap $D\le B$.

*Proof.* With $\alpha_0=\alpha_1=1$, (A.2) gives $D=\rho(C_0-\bar C^N)$. By (A.3), $C_0-\bar C^N=e(C_0-C_1)$, so $D=e\rho(C_0-C_1)=eB$. Sympy confirms $D-eB=0$. $\square$

**The perceived cost of silence.** Write $a\equiv\alpha_0/\alpha_1\in[0,1]$, the *relative attention to silence*, and define
$$C^*\equiv C^D+a\,(\bar C^N-C^D). \tag{A.4}$$
$C^*$ is the cost the market behaves as if a silent listing carries, in units of displayed costs. Then
$$p_k-p_N=-\rho\alpha_1\,(C_k-C^*)\quad\text{for every displayed letter }k, \tag{A.5}$$
$$\frac{D}{B}=\frac{C_0-C^*}{C_0-C_1}. \tag{A.6}$$
(Sympy confirms (A.5) as an identity.) Silence is priced like a displayed letter with cost $C^*$.
- Under full attention, $C^*=\bar C^N$, which lies between the A–D and E–G costs.
- Under full inattention, $C^*=C^D$.

**Proposition A2 (when silence beats verified A–D) [D].**
$$p_N>p_H\iff C^*<C_1\iff a<\frac{C_1-C^D}{\bar C^N-C^D}. \tag{A.7}$$

*Proof.* From (A.5) with $k=$ A–D: $p_H-p_N=-\rho\alpha_1(C_1-C^*)$. The second equivalence substitutes (A.4), using $\bar C^N>C^D$. $\square$

**Corollary A2 (the default must be optimistic) [D].** A necessary condition for $p_N>p_H$ is $C^D<C_1$: the inattentive default must be better than the *average certified A–D cost*. In particular:
- **Default = prior mean** ($C^D=\bar C\equiv\bar\theta C_1+(1-\bar\theta)C_0\ge C_1$). Then $p_N\le p_H$ for every $a$. Inattention with a mean default is cursedness again, and Proposition 4 applies.
- **Default = zero** ("out of sight, out of mind"). Then $p_N>p_H$ iff $a<C_1/\bar C^N$. At the apartment means this threshold is $185/243=0.76$ [E].

This corollary is the honest statement of the assumption the mechanism needs. The *existence* of inattention does not deliver the premium; the *optimism of the default* does. The shrouded-cost evidence cited in A.1 supports a near-zero default: under-weighting toward zero, not toward the average. Housing-specific evidence would make the case stronger, and the test is A.7(c).

**Corollary A3 (a falsifiable upper bound) [D].** If $C^D\ge0$, then
$$\frac{D}{B}\le\frac{C_0}{C_0-C_1}, \tag{A.8}$$
with equality iff $a=0$ and $C^D=0$. At the anchor's band midpoints this bound is **2.30 for apartments** and **2.11 for houses** [E]. A market with $D/B$ well above its bound would reject attention with a non-negative default. It would point back to $\xi$ or to seller-side pricing.

---

### A.4 Sellers (removed)

*(Removed at Bastien's request, 2026-10-09: dispersed hiding costs are no longer part of the analysis.)*

### A.5 Robustness to exact logit pricing [D]

Under the exact demand $\Gamma(p)=\rho G((v_1-p)/\varsigma)+(1-\rho)G((v_0-p)/\varsigma)$, §1.1 Proposition 2 shows the optimal price $P^*$ is nondecreasing in the sensitive buyers' mean valuation $v_1$. The sufficient condition is $\rho G_1^2+(1-\rho)G_0(2G_1-G_0)\ge0$. In cost form $v_1=V-\mathcal D\le v_0=V$. That condition holds whenever $G_0\le2G_1$, i.e. whenever the deduction $\rho\mathcal D$ is small relative to the taste-shock scale $\varsigma$. With deductions of a few log points this should hold, but it must be checked at the estimated $\hat\varsigma$.

Given monotonicity, **every ordering result above (A2, A3, A8) holds exactly.** Only the magnitudes in (A.5)–(A.6) scale by the pass-through $dP^*/dv_1\in[0,1]$.

**Where the two attention forms differ.** With attention *shares*, a silent listing faces three segments: insensitive, sensitive-inattentive and sensitive-attentive. A seller may price to the inattentive segment and accept losing attentive buyers. That makes silent listings' time-on-market longer *and* their price higher. With a representative *weight* $m$, there is no such trade-off. Time-on-market for silent listings, holding price, therefore distinguishes the two [C].

---

### A.6 The reform: what changed, and what the data say [E]

Let attention vary by period, $\alpha_{1}^t$ and $\alpha_0^t$ for $t\in\{\text{pre},\text{post}\}$, with $C_\theta$, $C^D$ and $\bar C^N$ stable. Assume, as the paper does, that the undisclosed share is flat. Then, in levels and in the paper's DiD:
$$\frac{D^t}{B^t}=\frac{C_0-C^{*t}}{C_0-C_1},\qquad \frac{\hat\Delta}{\hat\beta_1}=\frac{(C_0-C^D)-\dfrac{\Delta\alpha_0}{\Delta\alpha_1}(\bar C^N-C^D)}{C_0-C_1}. \tag{A.12}$$
(Sympy confirms the DiD expression.)
- The level ratio identifies relative attention $a^t$ in each period.
- The DiD ratio identifies the **spillover of the reform's attention shock to silent listings**, $\Delta\alpha_0/\Delta\alpha_1$.

**Calibration with $C^D=0$.** Index gaps from §1.1; $C_\theta$ from the anchor's band midpoints, apartments $C_1:C_0=185:327$, houses $178:339$; $e$ = 0.59 / 0.60.

| | $B$ | $D$ | $D/B$ | bound (A.8) | implied $a$ | $C^*$ (kWh-equiv.) |
|---|---|---|---|---|---|---|
| Apartments, pre | 1.97 | 4.54 | 2.30 | 2.30 | **0.00** | ≈ 0 |
| Apartments, post | 6.03 | 13.06 | 2.17 | 2.30 | **0.08** | 19 |
| Apartments, DiD | 4.06 | 8.53 | 2.10 | 2.30 | **0.12** (spillover) | — |
| Houses, pre | 7.48 | 3.88 | 0.52 | 2.11 | **1.05** | 255 |
| Houses, post | 13.30 | 7.77 | 0.58 | 2.11 | **1.01** | 245 |
| Houses, DiD | 5.82 | 3.89 | 0.67 | 2.11 | **0.95** (spillover) | — |

**Reading.**
1. **Apartments sit essentially on the bound.** Silent apartments are priced as if they carried *no* energy cost, before and after the reform. The reform tripled the penalty attached to displayed labels ($B$: 1.97 → 6.03). That penalty applies to displayed A–D as well as E–G, so silence gained on both. This is why $p_N-p_H$ rose from +2.6 to +7.0, a pattern no belief model can produce.
2. **Houses are fully attentive.** $a\approx1$ in every period means house buyers price silence at the rational pool cost. The paper's current model is the right model for houses, consistent with $\hat\lambda\approx0$ there.
3. **One parameter, $a$, reconciles both markets.** It needs no extra unobserved-quality term.

**Caveats on the calibration.**
- $C_\theta$ uses letter band midpoints. The paper text says "certified consumption" (open question 14).
- $C^D=0$ is imposed. A positive default lowers the implied $a$, and apartments are already at $a\approx0$; $D/B$ above the bound would need $C^D<0$.
- Cost is assumed proportional to kWh. The ratio is unit-free, so the level of $p^E$ does not matter, but its *shape* across letters does.
- These are market-average ratios of means. A market-by-market version (A.7 (b)) is the real test.

---

### A.7 Identification

| Object | Moment | Source of variation | Maintained assumption | Status |
|---|---|---|---|---|
| $\rho\,\Delta\alpha_1$ | $\hat\beta_1/\beta_1^{\rm anchor}$ (the paper's $\hat\rho$) | reform × market DiD | $C_0-C_1$ correctly measured by the anchor | point. **Reinterpretation:** because $\hat\beta_1$ is a DiD, $\hat\rho=\rho(\alpha_1^{\rm post}-\alpha_1^{\rm pre})$, the reform-induced *increase* in attention to displayed labels (corrected in A.12) |
| $C^*$ | $D/B$ via (A.6); or the zero-crossing of (A.5) | letter-level index gaps | linear pricing / monotone pass-through | point |
| $a$ | **pass-through**: $\partial C^*/\partial\bar C^N=a$ | cross-market / cross-period variation in the silent pool's true expected cost $\bar C^N_m$, computed from the registry ($\pi_m$, $\bar\theta_m$, $\sigma_{\theta m}$, hiders' registry letters) | attention and default do not covary with $\bar C^N_m$ | point if $\bar C^N_m$ varies enough |
| $C^D$ | intercept: $C^*-a\bar C^N$ | — | given $a$ | point |
| $F$ | $\sigma_0=F(D)$, $\sigma_1=F(D-B)$; more points from letters, $\sigma_k=F(\rho\alpha_1(C_k-C^*))$ | grades within market; across markets | $c_i\perp\theta$ | nonparametric at the observed points |
| $\alpha_1$ separately from $\rho$ | change in $B$ at **Jan 2022** (€ display) with $\rho$ fixed | timing | $\rho$ does not jump at Jan 2022 | ratio $\alpha_1^{2022+}/\alpha_1^{\text{H2 2021}}$ only |

**The pass-through argument.** It is the identification idea that distinguishes attention from everything else:
- A fully attentive market ($a=1$) must lower the price of silence one-for-one with how bad the silent pool actually is.
- An inattentive market ($a=0$) prices silence the same whatever the pool contains.

The registry makes the pool's true cost observable. That is unusual: in most disclosure settings the econometrician cannot compute $E[\text{quality}\mid\text{silence}]$. Concretely, estimate
$$\widehat{C^*_m}=C_{0m}-\frac{D_m}{B_m}(C_{0m}-C_{1m}),\qquad \widehat{C^*_m}=C^D+a\,\bar C^N_m+\text{controls}+u_m.$$
Use the slope $a$, separately for apartments and houses. Prediction: $a_{\rm apt}\approx0$ and $a_{\rm house}\approx1$.

**Consequences for the paper's estimators.**
- $\hat\rho$: unchanged as a number, reinterpreted as $\rho(\alpha_1^{\rm post}-\alpha_1^{\rm pre})$. *(Corrected; the first draft said $\rho\alpha_1$.)*
- $\hat c_0$: **changes for apartments.** *(Corrected; the first draft said it was unchanged.)* See A.12.
- The over-identifying wedge $\hat\lambda=\hat\Delta-\hat\beta_1\hat e^*$ is *replaced* by a test of full attention. In levels, $\lambda=\rho\alpha_1(1-a)(\bar C^N-C^D)$, zero iff $a=1$. In the paper's DiD, $\hat\lambda=\rho(\Delta\alpha_1-\Delta\alpha_0)(\bar C^N-C^D)$, zero iff the reform raised attention to silent and displayed listings equally *(corrected; see A.12)*. So the apartment $\hat\lambda=6.1$ ($t=6.8$) **is** the rejection of full attention, and the house $\hat\lambda=0.4$ is its non-rejection.

---

### A.8 Testable predictions and how they separate attention from the alternatives

| # | Test | Attention ($a<1$, $C^D<C_1$) | Belief channels (§1.3) | Unobserved quality $\kappa$ (§1.2) | Seller-side over-listing (§1.3 (vi)) |
|---|---|---|---|---|---|
| T1 | **Letter-level gaps to silence** (A.5): regress $p_k-p_N$ on $C_k$ | linear; slope $-\rho\alpha_1$; zero-crossing at $C^*$ (≈ 0–30 kWh in apartments, i.e. **silence beats every letter**) | crossing at $\bar C^N\approx243$, between D and E | linear in $C_k$, intercept shifted by $\kappa$ | no prediction for slope |
| T2 | **Pass-through** $a$ (A.7) | ≈ 0 for apartments | 1 (Bayes); $(1-\chi)$ (cursed) | 1 | — |
| T3 | **Bound** $D_m/B_m\le C_{0m}/(C_{0m}-C_{1m})$ by market | holds | holds (≤ 1) | can be violated | can be violated |
| T4 | **Jan 2022 break** in $p_N-p_H$ | jump (€ display raises $\alpha_1$, silence unchanged) | none | none | none |
| T5 | **July 2024 small-surface relabelling** (letters improve, consumption unchanged) | relabelled units gain relative to silence, in proportion to the drop in *displayed* cost | gain via rank only | none | none |
| T6 | **Collective vs individual heating** (needs re-pull) | lower $a$ and higher premium under collective heating | — | — | — |
| T7 | **Informed hiders vs uninformed silent**, same $X$ | **same price** (buyers see silence, not $K$) | same price | different ($\kappa$) | different if $K=0$ sellers over-list |
| T8 | **Hiding by grade** | $\sigma_1>0$; $\sigma_k$ increasing in $C_k$; $\sigma_0-\sigma_1\approx fB$ | $\sigma_1=0$ | — | — |
| T9 | **Transaction vs asking prices; time-on-market** | premium survives to transactions; with attention shares, silent listings may also sell more slowly (A.5) | survives | survives | premium vanishes at transaction; longer TOM; more price cuts |
| T10 | **Market tension** | larger premium where decisions are fast (zones tendues) [C] | — | — | larger in slack markets |

T1, T2 and T3 use only data Bastien already has: the letter-level hedonic indices and registry-based $\bar C^N_m$. T7 is the one result in the current exploratory evidence that runs against all buyer-side stories (A.9).

---

### A.9 Threats and what would falsify the mechanism

1. **The $K$ split (T7).** The exploratory listing regressions of §1.2 found that, within neighbourhood × vintage cells, uninformed silent apartments priced far above informed hiders. These were cross-sectional, not Bastien's indices, and not re-run by me. Buyers cannot see $K$, so attention, like every buyer-side mechanism, predicts equal prices. *Check: split the "Missing" index by $K$.* If the series coincide, attention stands alone. If they diverge, something buyers see but the hedonic controls miss differs between the two groups. Examples: photos, listing completeness, agency vs private seller. That needs a term next to $a$, not instead of it.
2. **The default.** Everything rests on $C^D<C_1$ (Corollary A2). If buyers who don't think about energy implicitly assume an *average* flat, the mechanism collapses to cursedness. Evidence for a low default would come from:
   - T1 (silence beating A/B as well);
   - T6 (bundled energy costs);
   - the shrouded-cost literature.
3. **Asking prices.** If the indices are built on asking prices, seller-side over-listing produces the same level pattern. T9 separates them.
4. **The bound (T3).** A market with $D/B$ well above $C_0/(C_0-C_1)$ rejects attention with a non-negative default.
5. **Cost measurement.** $C_\theta$ from band midpoints compresses variation within letters. Registry kWh (open question 10) would sharpen T1 and the bound.

---

### A.10 What this does to the paper [C]

- **Framing.** "Silence pays" becomes a statement about *attention to disclosed information*: mandatory disclosure works only when the disclosed number is attended to, and in apartments silence is not even read as a signal. That fits the title better than strategic concealment by low types alone. It also gives a clean apartment/house contrast with one parameter.
- **Model.**
  - Replace $\beta_1\tilde\theta$ by $-\mathcal D(d,\theta)$ (Lemma A0).
  - Add $a$ (by property type, possibly by market) and $C^D$.
  - The current model is the case $a=1$, so houses keep their current estimates.
- **Estimation.** See A.12. $\hat\rho$ keeps its value with a new interpretation. $\hat c_0$ changes for apartments. $\hat\lambda$ becomes the moment that identifies $a$. The equilibrium solver and the subsidy threshold code must be rewritten.
- **Policy** (interacts with the 2026-09-21 policy-first plan).
  - Under attention, the binding lever is **enforcement of display** plus **salience** (the € bill).
  - A retrofit subsidy does not raise the sale price of a property its owner will not disclose. In apartments, the private return to renovation at sale is $\rho\alpha_1(C_0-C_1)$ only for sellers who disclose.
  - Inattentive buyers of silent units overpay by $\rho(1-\alpha_0)(\bar C^N-C^D)$ relative to an attentive buyer. That is a consumer-protection quantity the paper can compute.

---

### A.11 Literature to position against

- **Salience of non-posted or shrouded costs.** Chetty, Looney & Kroft (2009); Finkelstein (2009); Gabaix & Laibson (2006); Ellison (2005); Brown, Hossain & Morgan (2010).
- **Models of attention.**
  - Sparsity: Gabaix (2014, 2019).
  - Focusing and salience: Kőszegi & Szeidl (2013); Bordalo, Gennaioli & Shleifer (2013).
  - "What you see is all there is": Enke (2020).
  - Rational inattention: Sims (2003); Matějka & McKay (2015). Rational inattention gives a micro-foundation for $\alpha_0<\alpha_1$, since processing a missing field is costlier than reading a displayed one.
- **Disclosure to inattentive receivers.** Hirshleifer & Teoh (2003), closest in spirit: limited attention changes how disclosed versus undisclosed information is priced. Fishman & Hagerty (2003): mandatory vs voluntary disclosure with informed and uninformed customers. DellaVigna & Pollet (2009): attention to disclosed news. Jin, Luca & Martin (2021) and Hagenbach & Saucet (2025) are the inference-side counterpart; A.1 is the place to explain why this paper is different.
- **Energy-cost inattention.** Allcott (2011); Allcott & Greenstone (2012); Sallee (2014); Allcott & Taubinsky (2015); Houde (2018). Myers, Puller & West (2022) for housing EPCs.
- **Limited attention in durable-goods prices.** Lacetera, Pope & Sydnor (2012); Busse et al. (2013).
- **Information avoidance**, if the motivated version is wanted. Golman, Hagmann & Loewenstein (2017).

All references in A.11 were verified against Crossref on 2026-10-05: 16 of 16 match (see the end of the file).

---

### A.12 Cross-check against the estimation code, and what changes in estimation (2026-10-05)

**What was checked.**
- The paper's estimators (04:410–430) and their code: `src/rho_identification.py` (anchor, $\hat\rho$, $\hat c_0$, $\hat\lambda$); `src/data_prep.py:417–490` (energy anchor); `src/estimation.py:353` and `src/model.py:508` (equilibrium solver, renovation threshold).
- Ran two scripts on the **existing market-level estimates** (`results/*/anchored_diagnostics.csv`, 45 / 97 markets), with per-market $\bar E_\theta$ recomputed via the pipeline's own `compute_energy_anchor` (2022–24, $K=1$, registry letters):
  - `scratchpad/attention_check.py`
  - `scratchpad/attention_bound.py`
- Nothing in the repo was modified.

#### A.12.1 Corrections to Part II

1. **$\hat\rho$ is a DiD object.** $\hat\beta_1$ is a post-minus-pre difference, so $\hat\rho=\hat\beta_1/\beta_1^{\rm anchor}$ estimates $\rho(\alpha_1^{\rm post}-\alpha_1^{\rm pre})$: the reform-induced *increase* in effective attention to displayed labels, not $\rho\alpha_1$. This fits the paper's own narrative (04:349: the reform changed "how much a disclosed rating matters to the buyer"). Attention names exactly what moved.
2. **$\hat c_0$ does not stay the same.** The first draft said it was unchanged, which was wrong.
   - The paper computes $\hat c_0=\hat\beta_1\hat e^*$ because, under full attention, the low type's hiding gain is $\rho\beta_1e$.
   - Under attention, the gain is the observed silent-minus-bad gap itself, so the marginal hider's cost is $\hat\Delta$. That is the shortcut the paper explicitly rejects at 04:428 *because* it imposes full attention; under attention it is the correct inversion.
3. **$\hat\lambda$ in DiD form** equals $\rho(\Delta\alpha_1-\Delta\alpha_0)(\bar C^N-C^D)$. It tests whether the reform raised attention to silent listings as much as to displayed ones. It is not a test of $a=1$ in levels.
4. **"Sharp calibration" was too strong.** Estimated by market (below), $a_{\rm apt}=0.21\pm0.11$, not 0.00–0.12.
5. **The apartment bound binds.** On average the apartment markets sit *on* the bound $D/B\le C_0/(C_0-C_1)$. That leaves no room for a positive default $C^D$, and some individual markets violate it (A.12.2).

#### A.12.2 Results on the estimated markets [E]

The pass-through regression with $C^D=0$, from (A.6) with $\bar C^N=eC_1+(1-e)C_0$, is
$$\hat\Delta_m=(1-a)\,\hat\beta_{1,m}R_{0m}+a\,\hat\beta_{1,m}\hat e^*_m+u_m,\qquad R_{0m}\equiv\frac{\bar E_{0m}}{\bar E_{0m}-\bar E_{1m}}.$$
- The current model is $a=1$.
- Pure inattention is $a=0$.
- The two coefficients should sum to one.

| | Apartments (45) | Houses (97) |
|---|---|---|
| Mean $\bar E_1$ / $\bar E_0$ (kWh, band midpoints) | 185 / 327 | 178 / 339 |
| Bound $R_0$ (mean) | 2.31 | 2.11 |
| Unrestricted: coef. on $\hat\beta_1R_0$ / on $\hat\beta_1\hat e^*$ | 0.66 (0.40) / 0.76 (1.57) | 0.03 (0.12) / 1.02 (0.40) |
| Sum $=1$? | 1.41, $p=0.73$ | 1.04, $p=0.88$ |
| **Restricted $a$** (one parameter) | **0.21** ($1-a$: 0.79, se 0.11) | **0.96** ($1-a$: 0.04, se 0.04) |
| Current model $a=1$ | rejected ($t\approx7$) | not rejected |
| Mean slack in the attention bound, $R_0\hat\beta_1-\hat\Delta$ (log pts) | **0.92** ($t=1.0$) | 8.38 ($t=13.0$) |
| Markets violating the attention bound | 21/45 | 8/97 |
| …of which: low / mid / high $\hat\beta_1$ tercile | 67% / 33% / 40% | 22% / 3% / 0% |
| Markets violating the current model ($D/B>1$) | 37/45 | 33/97 |

**Reading.**
- **Houses.** The current model is the attention model with $a\approx1$. Nothing changes.
- **Apartments.** Full attention is decisively rejected, and attention to silence is low ($a\approx0.2$).
  - The unrestricted coefficients are imprecise, because both regressors scale with $\hat\beta_1$. The restricted one-parameter form is the one to use.
  - The apartments sit on the attention bound on average. The mechanism can fit them only with $C^D\approx0$, so any optimism less extreme than "energy costs nothing" is rejected.
  - Violations concentrate where $\hat\beta_1$ is small, where $D/B$ is noisy. But 40% of high-$\hat\beta_1$ markets still exceed the bound. **Attention is the main story, but probably not the whole story in every apartment market.** The residual is where $\xi$, seller-side listing behaviour, or measurement of $C_\theta$ come back in.
- **$R_0$ depends on energy costs.** It depends on how $C_\theta$ is measured, and the G band uses a 500 kWh **placeholder** midpoint (`data_prep.py:409–419`). From pooled registry shares, moving the G midpoint from 420 to 600 kWh moves the apartment bound from about 2.24 to 2.06 [E]. Since apartments sit on the bound, that matters for the violation count. Certified kWh (the paper text says "certified consumption"; the code uses midpoints, open question 14) should be used before this test is reported.

#### A.12.3 What changes in each estimated object

| Object | Current estimator | Under attention | Apartments | Houses |
|---|---|---|---|---|
| $\hat\rho_m$ | $\hat\beta_1/\beta_1^{\rm anchor}$ | same number; $=\rho\,\Delta\alpha_1$ (reform-driven attention to displayed labels) | 0.495 (unchanged) | 0.458 (unchanged) |
| $\hat e^*_m$ | registry, $\sigma_1=0$ imposed | registry, **with $\hat\sigma_1>0$** (attention predicts $\sigma_1>0$). It enters prices only with weight $a$. | small effect ($a\approx0.2$) | matters ($a\approx1$); use registry $\sigma_1$ (FINDING-sigma1) |
| $\hat c_{0,m}$ (marginal hider) | $\hat\beta_1\hat e^*$ | $\hat\Delta_m$ (DiD), or the post-reform level $D^{\rm post}$ if the pre-period gap is treated as attention rather than nuisance | **2.4 → 8.5** (DiD) or **13.1** (level) | 3.5 → 3.9 (DiD) |
| Hiding-cost distribution | single $c_0$ | $F$, with $F(\hat\Delta)=\hat\sigma_0$ and $F(\hat\Delta-\hat\beta_1)=\hat\sigma_1$ | two points: F(8.5), F(4.5) | F(3.9) only (high types gain $<0$) |
| $\hat\lambda_m$ | over-id test | **estimating moment** for $a$: $\hat\lambda=(1-a)\hat\beta_1(R_0-\hat e^*)$ under $C^D=0$ | $a=0.21$ | $a=0.96$ |
| New: $a$, $C^D$ | — | $a$ by property type (or market); $C^D$ normalised to 0. It is not separately identified with these moments: the bound binds for apartments | | |
| Regime classification | belief-feedback fixed point | weak feedback (scaled by $\alpha_0$), so "Partial Pooling" loses its mechanism in apartments. Hiding is governed by $F$. | regimes need redefining | unchanged |

**Plausibility flag on $\hat c_0$.**
- 8.5–13.1 log points is about 9–14% of the price. That is an order of magnitude above the statutory fines for missing DPE information in ads [CHECK amounts].
- If the attention model is right, informed low-type apartment sellers who disclose (≈85%) face non-monetary barriers to hiding worth over 9% of price. The most plausible candidate is agencies refusing to list without the DPE, i.e. hiding is mostly *unavailable* rather than costly.
- This is a substantive reinterpretation of $c_0$. It is also the current model's weak spot in reverse: its $\hat c_0=2.4$ is plausible, but its price of silence is not.

#### A.12.4 Counterfactuals (renovation threshold, `src/model.py:508`)

The code computes $\bar R=\Pi^*(d{=}1,\theta{=}1)-\Pi^*(d{=}0)+c_0$.

**Marginal seller.** Under linear pricing, $\bar R$ equals $B$ in **both** models: $(B-eB)+eB$ in the current model, and $(B-D)+D$ under attention. *The headline minimum subsidy is robust* to the mechanism, to first order.

**What changes.**
- **(b) Renovated sellers who then hide.** A renovated seller with $c_i<D-B$ hides after renovating and captures **no** sale-price return. Under attention, renovation is capitalised only for sellers who disclose. This links the subsidy directly to **enforcement of display**.
- **(c) The code must be rewritten, not just re-fed.** `solve_equilibrium` and `renovation_threshold` call `params.v1_hidden(e_star)`, i.e. they hard-code full attention. Feeding them the attention-model $\hat c_0$ would mix two models.

#### A.12.5 Decisions for Bastien

1. **DiD or level for the hiding gain.** Under attention, the pre-reform gap (silence already beat A–D in apartments) is part of the mechanism, not a nuisance, so the post-reform level ($D=13.1$) is arguably the right hiding gain. The paper's c₀-invariance argument (04:349) favours the DiD (8.5).
2. **Energy-cost measurement.** Use certified kWh instead of midpoints (and the G placeholder) before reporting the bound test.
3. **Scope.** Should the attention extension be the main specification for apartments, with houses as the $a=1$ case? Or should it be a section that "explains $\hat\lambda$", leaving the current estimates as the baseline?

---

### A.13 All listings are agency listings: implications (Bastien, 2026-10-05)

1. **The "hiding is unavailable because agencies refuse to list" reading of $\hat c_0$ (A.12.3) is wrong.** Every silent listing in the data is an agency listing.
2. **Delegated disclosure explains the size of $\hat c_0$ instead** [C]. The agency executes the display decision. It bears the expected fine and reputational cost $k$, but captures only its commission share $\tau$ of the price gain. In seller price units, the hiding cost is therefore $c_0\approx k/\tau$.
   - Illustration: $k=$ €1,000 and $\tau=5\%$ give ≈ €20,000, about 8% of a €250k flat. That is the order of the attention-model $\hat c_0$ (8.5–13.1 log points).
   - Commission rates and fine amounts are [CHECK].
   - Prediction: hiding rates vary by agency, and fall where enforcement (DGCCRF controls) is stronger.
3. **[Superseded by A.14.]** **$K=0$ is unlikely to mean "uninformed".** Agencies must hold a DPE to market a sale. $K=0$ most plausibly means a pre-July-2021 certificate or a failed registry match. This undermines the Dye reading of the silent pool (94% "uninformed" sellers):
   - **Current model:** if most silent listings are informed hiders with old certificates, the rational $e$ is lower, the predicted premium shrinks, and the apartment rejection gets worse.
   - **Attention model:** the silent price depends on $e$ only with weight $a\approx0.2$. It is robust to this reinterpretation.
4. **Alternatives.**
   - **Ruled out:** aspirational pricing by private (FSBO) sellers.
   - **Added: agency overpricing to win mandates** (Levitt & Syverson 2008, *REStat*; Rutherford, Springer & Yavas 2005, *JFE*) [CHECK]. If the agencies that omit the DPE also inflate asking prices, the silent premium appears without buyer attention. Distinguish with time-on-market and price cuts.
5. **New first-priority test: agency fixed effects.** `realtor_ref` is in the source SQL (`data/collect_listings.py:98–105`) but not in the saved files. Re-pull it and compare silent with A–D listings *within agency*, with the index's hedonic controls.
   - If the premium survives, it is buyer-side (attention).
   - If it vanishes, it is agency composition (an agency-level $\xi$, or agency pricing behaviour).

   This test comes before T4 (the Jan 2022 break), T1 (letter-level gaps) and T7 (the $K$ split).

---

### A.14 Certification friction as the source of uninformedness (Bastien, 2026-10-05)

**Bastien's argument.** $K=0$ is genuine uninformedness at the listing date. Certification is scarce, and diagnosticians were in short supply after the 2021 method change. The certificate arrives eventually, but the agency lists without waiting for it. This **supersedes A.13 point 3**: under this story, $K=0$ does not have to mean an old certificate or a failed match, and the Dye pool survives. It is also consistent with V2-QUEUE: the unmatched share falls from 62.5% to 18.4% over the period as supply catches up.

**1. The current $K$ does not measure "informed at listing" [D, from code].**
- `ADEME/match_improved.py:125–143` gives a certificate dated *after* the listing a date score of 0.
- But the date carries weight 0.2 (`:220–223`), and matches are accepted from 0.3 (`enrich_listings.py:175`).
- So a listing can be $K=1$ on a certificate that **did not exist when it was listed**.

Under the friction story, those listings are uninformed at listing but coded as **informed hiders**. Consequences:
- $\hat\pi$ is overstated.
- $\hat\sigma_0$ and $\hat\sigma_1$ include non-strategic "certificate pending" listings.
- That alone could produce FINDING-sigma1's $\hat\sigma_1\approx\hat\sigma_0$ and the grade-flat hiding pattern. **This is an alternative to attention's explanation of $\sigma_1\approx\sigma_0$ (A.4), so that fact no longer favours attention.**

*Fix:* save `date_reception_dpe` in the enrichment output and split $K$ three ways:
- $K^{\rm pre}$: certificate dated before the listing (informed);
- $K^{\rm pend}$: certificate dated after the listing start (uninformed at listing, certificate pending);
- $K=0$: never matched.

Then $\hat\pi$, $\hat\sigma_\theta$ and $\hat e^*$ should be recomputed on $K^{\rm pre}$. The distribution of time to certificate for $K^{\rm pend}$ is a direct measure of the friction. Bastien's story predicts it is longest in 2021H2–2022.

**2. Friction and attention are complements, not substitutes.**
- **Friction** explains *who* is silent: the size of $1-\pi$ and why silence was weakly informative.
- It cannot, by itself, price silence above A–D. The cap $D\le B$ (Proposition 1) holds for any $\pi$.
- **Attention** (or $\xi$) is still needed for $\hat\Delta>\hat\beta_1$.

The two combine naturally. A buyer who knows that many sellers are "waiting for the DPE" has an additional reason not to read silence as bad news.

**3. Dynamic prediction (the friction easing over time).**
- As $\pi$ rises and the pending listings leave the silent pool, the pool becomes more strategic. $e$ falls and $\bar C^N$ rises.
- **Belief model:** $\Delta=\rho\beta_1e$ falls relative to $\beta_1$, and $\lambda=0$ throughout.
- **Attention with friction:** $\lambda=\rho\alpha_1(1-a)(\bar C^N-C^D)$ **rises** as the pool worsens, because the price of silence does not follow.

The cumulative-window table (`quality_reports/diagnostics/rho-anchor-dynamics/post_window_trajectory.csv`) shows:
- Apartments: $\hat\lambda$ 3.9 → 5.5 → 6.0 (windows ending July 2022 / 2023 / 2024).
- Houses: $\hat\lambda$ 1.1 → 0.6 → 0.4.

That direction matches attention + friction. **Caveat:** these are cumulative windows, and $\hat\beta_1$ grows at the same time, so the rise in $\hat\lambda$ is not yet separated from the rise in $\hat\beta_1$. A year-specific version with year-specific $\hat\pi_t$ and $\hat e^*_t$ is needed.

**4. The first post-reform year does not fit either model [E, needs checking].**
- In the July-2022 window, the apartment mean $\hat\Delta=3.1$ while mean $\hat\beta_1=0.2$. That ratio far exceeds the attention bound ($\approx2.3$) as well as the belief-model bound (1).
- These means are over all 83 DiD markets, including those with $\hat\beta_1\le0$, so the ratio is unreliable as computed. **It should be recomputed on the estimation-sample markets.**
- If it survives, one candidate is the friction story itself acting on *unobservables*. During the shortage, the silent pool changed from mostly properties nobody had certified (often neglected stock) to ordinary properties waiting for their DPE. Hedonic indices hold observables fixed, but not this change in the silent pool's unobserved quality.
- That would be a reform-dated $\Delta\kappa$ (Cor. 3d) driven by friction. It is testable with $K^{\rm pend}$: the silent premium should be carried by pending listings in 2021H2–2022.

**5. Within-listing switches.**
- 79 apartment and 312 house listing_ids switch $d$ across rows; 45 and 135 of them also change price.
- Under the friction story these should be $d:0\to1$ (the certificate arrives during the listing). Attention predicts the price does **not** rise when an A–D label appears.
- Row timestamps are needed to order the rows; the saved files only carry `start_date`. The sample is small, but it is the only within-property comparison available.

---

### A.15 Truthful disclosure and old certificates (Bastien, 2026-10-05)

**Maintained assumption.** Disclosure is truthful (No Falsification). Pre-July-2021 certificates remained legally valid during the transition: 2013–17 certificates until end-2022, and 2018–June 2021 certificates until end-2024 [CHECK]. A listing can therefore truthfully display an **old-method** letter.

**1. $K$ captures only new certificates.** "Informed" should mean *holds any valid certificate*. The registry contains post-July-2021 certificates only, so $K=0$ mixes two groups:
- **(a) Truly uninformed sellers** (friction, A.14).
- **(b) Holders of a valid old certificate.**
  - Their disclosures ($d=1$, $K=0$) are truthful old-method letters. These are 226,643 of 767,232 apartment listings (29.5%), and 36.6% of disclosers.
  - Their silences ($d=0$, $K=0$) are **informed hiders coded as uninformed**.

Combined with A.14, $\hat\pi$ has two biases of opposite sign:
- *up*: pending certificates coded $K=1$;
- *down*: old-certificate holders coded $K=0$.

Sizing the first needs `date_reception_dpe`. Sizing the second needs the $d=1,K=0$ share and its age profile.

**2. The labelling method changed on the reform date.**
- **The groups change composition.** Disclosed A–D and E–G mix old- and new-method letters after July 2021, and contain only old-method letters before. The DiD $\hat\beta_1$ therefore combines opposability with a method-driven reclassification of who is in A–D versus E–G. The reclassification depends on true consumption, which the hedonic controls do not absorb.
- **The anchor and $\hat\beta_1$ measure different objects.** The anchor uses new-method (registry) consumption; $\hat\beta_1$ prices displayed letters of both vintages.
- **Letter disagreement is not lying.** Truthful old letters also account for part of the listing-vs-registry disagreement (Task 2 §0.4), e.g. the asymmetric house pattern.

**3. Test of the opposability channel (post-period cross-section, no DiD needed).** Compare:
- the green premium on **new-method** letters ($d=1$, $K=1$, listing letter = registry letter);
- the green premium on **old-method** letters ($d=1$, $K=0$).

Opposability predicts the first is larger. Under attention, a smaller $\alpha_1$ for old letters predicts the same direction. Equal premiums would undercut the paper's demand-side reform channel.

**4. Test of the friction story at certificate expiry.**
- At 1 Jan 2023 (expiry of 2013–17 certificates), holders become uninformed until they re-certify. Predictions: a jump in the silent share, and in certificates dated after the listing ($K^{\rm pend}$, A.14).
- A second, smaller break should appear at end-2024.

---

## Part III. The attention extension (full write-up, 2026-10-05)

*Title: "Limited attention to silence: a theory extension for When Silence Pays". Written by the micro-theorist agent; reviewed in the main session: 34/34 sympy checks re-run OK, ratio-of-means estimates independently recomputed (apartments $a_\Delta=0.13$, bootstrap 95% CI $[-0.14,0.37]$; houses $0.95$, $[0.85,1.04]$).*

*Working document, 2026-10-05, branch `review`. Nothing in the repository was edited. All computations are read-only scripts in this scratchpad (listed in §12). This document supersedes "Task 1, Part II" of `playground/notes.md` (§A.0–A.11) as the clean statement of the attention extension. It is consistent with the corrections in §A.12–A.15; where it revises an earlier number or claim, §0.4 says so explicitly.*

**Status labels.**
- **[D]** derived here; proof given in full, and every identity is checked in `ext_sympy.py` (34 checks, all OK; labels match the equation numbers here).
- **[A]** maintained assumption.
- **[C]** conjecture, interpretation or institutional claim not yet verified.
- **[E]** exploratory number computed in this session from repo data; not paper-grade until rebuilt in the pipeline.
- **[CHECK]** fact or citation to verify before it enters the paper.

---

### 0. Reader's guide

#### 0.1 What the extension does, in five sentences

1. The paper's model prices a silent listing at $\rho\beta_1 e$ with $e\in[0,1]$, so a silent listing can never sell above a verified A–D listing; in apartments it does, by about 7 log points in levels and 4.5 in the reform DiD, which is why the over-identifying wedge $\hat\lambda=6.1$ is rejected.
2. The extension keeps every piece of the paper's disclosure game and changes one thing on the buyer side: an EPC-sensitive buyer attends to energy with a probability that depends on whether a label is displayed ($\alpha_1$) or not ($\alpha_0\le\alpha_1$), and an inattentive buyer subtracts a *default* energy cost $C^D$, not a belief.
3. With $a\equiv\alpha_0/\alpha_1=1$ the extension is exactly the paper's model; with $a<1$ and an optimistic default, silence can beat a verified A–D listing, and the paper's rejected restriction $\hat\lambda=0$ becomes the moment that estimates $a$: $\hat\lambda=(1-a_\Delta)\,\hat\beta_1\,(R_0-\hat e^*)$, with $R_0=\bar E_0/(\bar E_0-\bar E_1)$ read off the registry.
4. On the estimation sample this gives relative attention to silence of about 0.1–0.2 in apartments and about 0.95 in houses (under the normalisation $C^D=0$), so one parameter reconciles the two segments; houses stay at the current model.
5. The headline renovation subsidy for the marginal seller is unchanged ($\bar R=B$ in both models), but the extension changes who renovates, what concealment costs ($\hat c_0$ rises from 2.4 to roughly 8 log points in apartments), and which policies work (display enforcement and salience, rather than hiding costs alone).

#### 0.2 Notation

Every symbol is defined again where it first appears. "Log points" means $100\times$ log-price differences, the unit of the paper's Table 4.

| Symbol | Meaning | Paper equivalent | Units |
|---|---|---|---|
| $\theta\in\{0,1\}$ | energy quality; $\theta=1$ iff letter A–D | same | — |
| $k\in\{A,\dots,G\}$ | DPE letter | `epc_score` 1–7 | — |
| $K\in\{0,1\}$ | seller holds a valid certificate at listing | same | — |
| $d\in\{0,1\}$ | a letter is displayed in the listing | same | — |
| $\pi$ | $\Pr(K=1)$ | same | share |
| $\bar\theta$ | $\Pr(\theta=1)$ | same | share |
| $\sigma_\theta$ | $\Pr(d=0\mid K=1,\theta)$, hiding rate | same | share |
| $e$ | $\Pr(\theta=1\mid d=0)$, Bayesian belief about the silent pool | $e(\sigma_0,\sigma_1)$, eq. `eq:belief_general` | share |
| $\rho$ | share of EPC-sensitive buyers | same | share |
| $V(X)$ | valuation of a property gross of energy cost | $\beta_0+X'\beta$ plus a constant (§1.3) | log price |
| $C_\theta$, $C_k$ | capitalised energy cost of quality $\theta$ / letter $k$ | $\beta_1=C_0-C_1$ | log points |
| $\bar E_\theta$ | mean certified primary-energy consumption of quality $\theta$ | anchor input | kWh$_{ep}$/m²/yr |
| $\alpha_1,\alpha_0$ | probability a sensitive buyer attends to energy, label displayed / not displayed | implicitly $\alpha_1=\alpha_0=1$ | prob. |
| $a\equiv\alpha_0/\alpha_1$ | relative attention to silence | implicitly 1 | ratio |
| $C^D$ | cost subtracted by an inattentive sensitive buyer (the "default") | none (hidden normalisation) | log points |
| $\bar C^N$ | $E[C\mid d=0]=eC_1+(1-e)C_0$, rational cost of the silent pool | $\beta_1(1-e)$ up to a constant | log points |
| $C^*$ | $C^D+a(\bar C^N-C^D)$, perceived cost of silence | $\bar C^N$ | log points |
| $\tilde e$ | $(C_0-C^*)/(C_0-C_1)$, "effective belief" priced into silence | $e$ | can exceed 1 |
| $R_0$ | $C_0/(C_0-C_1)=\bar E_0/(\bar E_0-\bar E_1)$ | none | ratio |
| $r_D$ | $C^D/(C_0-C_1)$ | none | ratio |
| $p_H,p_L,p_N$ | log price of displayed A–D, displayed E–G, silent listing at reference $X$ | index levels | log price |
| $B\equiv p_H-p_L$, $D\equiv p_N-p_L$ | level green premium; level silence premium | $\beta_{1,m,t}$, $\Delta_{m,t}$ | log points |
| $\hat\beta_1,\hat\Delta$ | post-minus-pre DiD of $B$, $D$ | same | log points |
| $\hat\lambda$ | $\hat\Delta-\hat\beta_1\hat e^*$ | same (over-ID wedge) | log points |
| $\omega_j^t\equiv\rho^t\alpha_j^t$ | effective attention mass, display state $j$, period $t$ | — | share |
| $a_\Delta\equiv\Delta\omega_0/\Delta\omega_1$ | spillover of the reform's attention shock to silence | — | ratio |
| $C^*_\Delta$ | $C^D+a_\Delta(\bar C^N-C^D)$, the DiD analogue of $C^*$ | — | log points or kWh |
| $G_\theta$ | gross gain from hiding for an informed seller of type $\theta$ | $\Delta(e)$ for $\theta=0$ | log points |
| $c_0$ | hiding (non-compliance) cost, single value (main text) | same | log points |
| $F,f$ | distribution / density of hiding costs (appendix) | — | — |
| $k$, $\tau$, $P$ | agency's expected sanction (€), commission share, price (€) | — | €, share, € |
| $\bar R$ | renovation threshold | eq. `eq:threshold` | log points |

#### 0.3 What changes and what stays, relative to the paper's §4

| Element of §4 | Status in the extension |
|---|---|
| Seller types $(K,\theta)$, $\pi$, $\bar\theta$, $K\perp\theta$ | **stays** |
| No Falsification, truthful disclosure | **stays** (and is extended to valid old-method letters, §2) |
| Belief function $e(\sigma_0,\sigma_1)$ | **stays**, but enters prices only with weight $a$ |
| Buyer valuation $v_1=\beta_0+\beta_1E[\theta\mid d]+X'\beta$ | **replaced** by the cost form with display-triggered attention (E.1)–(E.3); identical when $a=1$ |
| $\Delta(e)=\rho\beta_1e$, silent premium in $[0,B]$ | **replaced** by $D=B\,\tilde e$ with $\tilde e\in[0,R_0]$ |
| Corollary `cor:hq_disclose` ($\sigma_1^*=0$) | **stays** with a single $c_0$ whenever $\sigma_0^*<1$ |
| Three regimes (Cost-Deterred, Partial Pooling, CAS) | **stay**; the Partial Pooling band shrinks by the factor $a$ |
| $\hat\rho=\hat\beta_1/\beta_1^{\rm anchor}$ | **same number**, reinterpreted as $\Delta(\rho\alpha_1)$ |
| $\hat c_0=\hat\beta_1\hat e^*$ | **replaced** by the fitted silence premium, $\approx\hat\Delta$ |
| $\hat\lambda$ as over-ID test | **becomes the estimating moment for $a_\Delta$**; the new tests are the bound, the intercept, cross-market homogeneity |
| Renovation threshold $\bar R^{PP}=B$ | **stays** for the marginal seller; inframarginal and hide-after-renovate sellers change |
| `src/model.py` solver | must be **rewritten** (it hard-codes $a=1$ via `v1_hidden(e_star)`) |

#### 0.4 What this document revises relative to `playground/notes.md` Part II

1. **Nesting is $a=1$, not $\alpha_0=\alpha_1=1$.** Any common attention level $\alpha_0=\alpha_1$, and any default $C^D$, returns $D=eB$ (sympy). Part II stated the special case.
2. **Levels do not robustly identify $a$** (new, §5.6). The level calibration in A.0/A.6 ($a\approx0.00$ pre, 0.08 post) is a ratio of cross-market means. The cross-market slope of $D$ on $B$ in levels implies $a\approx0.8$ instead, with an imprecise positive intercept. The two can be reconciled only by a level nuisance term, so the A.0/A.6 level numbers are withdrawn. The DiD estimate of A.12 ($a=0.21$) stands, relabelled $a_\Delta$.
3. **The house result "$a\approx1$" holds only under $C^D=0$.** What houses identify is that silence is priced at the rational pool cost ($C^*_\Delta=231$ vs $\bar C^N=243$ kWh). That is equally consistent with any $a$ if the default is close to the pool mean (§6.8).
4. **The first-post-year anomaly (A.14.4) does not survive on the estimation sample.** On the 45 apartment markets, the July 2021–June 2022 window gives $\hat\beta_1=1.99$, $\hat\Delta=4.33$, ratio 2.18, inside the attention bound (2.31). The 0.2/3.1 figures were averages over 83 markets including those with $\hat\beta_1\le0$ (§7.3).
5. **Flat hiding by grade is not evidence for attention, and houses show why.** In houses the DiD hiding gain of a high type is negative ($\hat\Delta-\hat\beta_1=-1.93$), so attention predicts $\sigma_1=0$; the registry nonetheless shows $\hat\sigma_1=2.5\%$ vs $\hat\sigma_0=3.0\%$. Non-strategic silence (pending certificates, incomplete listings) therefore exists, and it can produce the same flat pattern in apartments (§4.5).
6. **New estimator recommendation.** The through-origin OLS of A.12 is biased toward $a=1$ when $\hat\beta_1$ is noisy, because the same E–G index enters both sides; the ratio-of-means estimator is not (Monte Carlo, §6.4). It gives $a_\Delta=0.13$ (apartments), 0.95 (houses).
7. **A normalisation-free object exists.** The salience counterfactual "silent listings get the same reform-induced attention as displayed ones" lowers the silent DiD premium by exactly $\hat\lambda$, whatever $C^D$ is (§8.4).
8. **G-band sensitivity recomputed with market means.** $R_0$ is 2.38 / 2.31 / 2.24 for a G midpoint of 420 / 500 / 600 kWh; A.12's 2.24→2.06 used pooled registry shares. Both show the same direction.

---

### 1. Motivation and intuition

#### 1.1 The cap in the current model

Fix a market and a period, and a reference property $X$. The paper prices a listing at the buyer-share-weighted mean valuation (main.tex:485):
$$p=\underbrace{(1-\rho)\,v_0}_{\text{insensitive}}+\underbrace{\rho\,v_1}_{\text{sensitive}},\qquad v_0=\beta_0+X'\beta,\qquad v_1=\beta_0+\beta_1\,E[\theta\mid\text{listing}]+X'\beta .$$
For the three listing groups, $E[\theta\mid\cdot]$ is 1 for a displayed A–D, 0 for a displayed E–G, and $e$ for a silent listing. So
$$p_H=\beta_0+X'\beta+\rho\beta_1,\qquad p_L=\beta_0+X'\beta,\qquad p_N=\beta_0+X'\beta+\rho\beta_1e .$$
Subtracting $p_L$:
$$B=p_H-p_L=\rho\beta_1,\qquad D=p_N-p_L=\rho\beta_1 e=e\,B .$$
Because $e$ is a probability, $0\le e\le1$, hence $0\le D\le B$. **A silent listing can never sell above a verified A–D listing.** This holds in every market and period, and the notes (Prop. 2) show it survives exact logit pricing.

**What the data say [E].** On the 45 apartment markets, the level gaps average $B=6.03$ and $D=13.06$ post-reform ($D>B$ in 93% of markets), and $B=1.97$, $D=4.54$ pre-reform ($D>B$ in 84%). The DiDs are $\hat\beta_1=4.06<\hat\Delta=8.53$. Houses respect the cap: $B=13.30$, $D=7.77$ post, $\hat\beta_1=5.82>\hat\Delta=3.89$.

**What this does to $\hat\lambda$.** The paper's wedge is $\hat\lambda=\hat\Delta-\hat\beta_1\hat e^*$. Write it as
$$\hat\lambda=\underbrace{(\hat\Delta-\hat\beta_1)}_{4.47\ \text{(apts)}}+\underbrace{(1-\hat e^*)\hat\beta_1}_{1.65}.$$
The second piece is what any story that keeps $D\le B$ can reach. The first piece, 73% of the wedge, requires silence to beat verified A–D. So the rejection is not about beliefs being slightly off; it is about a ceiling the model cannot cross.

#### 1.2 Why belief-based fixes cannot break the cap

Any mechanism that only changes *what buyers believe about $\theta$ after silence* replaces $e$ by some $\tilde e$. Cursed buyers (Eyster–Rabin), naive buyers who play the prior after "no disclosure" (Hagenbach–Koessler 2017), motivated skepticism (Hagenbach–Saucet 2025), under-skepticism (Jin–Luca–Martin 2021): all of them pick $\tilde e$ inside the support of what silence could hide, which is $\{0,1\}$. So $\tilde e\in[0,1]$ and $D=\tilde e B\le B$ again. The notes' Proposition 4 bounds the whole class at $\hat\lambda\le(1-\hat e^*)\hat\beta_1=1.65$, and the cursed case at 0.13, because a silent pool that is 94% uninformed already makes the Bayesian belief almost equal to the prior.

The same argument kills "anchoring on the bad letter" (an extra penalty on displayed E–G): it moves $p_L$, and $p_L$ cancels from $D-B=p_N-p_H$.

To get $D>B$, something must make the silent listing look *better than the average verified A–D listing*. A belief about a binary $\theta$ cannot do that. A different object has to replace the belief.

#### 1.3 Bonus form versus cost form: the paper's model is a cost model with a hidden normalisation

The paper writes energy as a **bonus** for quality: $v_1=\beta_0+\beta_1\theta+X'\beta$. Rewrite it as a **cost**. Let $C_1<C_0$ be the capitalised energy costs of an A–D and an E–G dwelling, and let $\bar V\equiv\beta_0+X'\beta+C_0$. Then
$$\bar V-C_\theta=\beta_0+X'\beta+(C_0-C_\theta)=\beta_0+X'\beta+\beta_1\theta\quad\text{with}\quad\beta_1\equiv C_0-C_1. \tag{1.1}$$
So the paper's sensitive buyer is a buyer who subtracts the energy cost she expects: $C_\theta$ when a letter is shown, and $E[C\mid d=0]=eC_1+(1-e)C_0$ after silence, which gives $\bar V-E[C\mid d=0]=\beta_0+X'\beta+\beta_1e$. The two forms are the same model.

Now look at the insensitive buyer, $v_0=\beta_0+X'\beta=\bar V-C_0$. In cost form she **subtracts $C_0$, the worst cost, whatever the listing shows.** That is a normalisation: because she subtracts the same amount from every listing, the amount cancels from every price gap, and the paper is right that it does not matter.

**The normalisation stops being innocuous as soon as "not thinking about energy" depends on what the listing shows.** If a buyer ignores energy only when no label is displayed, what she subtracts when she ignores it no longer cancels: it is compared with what she subtracts when a label is displayed. That amount is a primitive. We call it the default, $C^D$. The bonus form hides it by fixing it implicitly at $C_0$ (insensitive buyers) or by never letting attention depend on display (sensitive buyers). The extension makes it explicit.

#### 1.4 "Not thinking about energy" is not "believing the average"

Two buyers see a silent listing.

- **The cursed buyer** thinks about energy. She asks "what letter is this flat likely to have?", answers "probably the average one", and subtracts the prior mean cost $\bar C=\bar\theta C_1+(1-\bar\theta)C_0$. Her deduction lies between $C_1$ and $C_0$. Silence cannot beat A–D for her.
- **The inattentive buyer** does not think about energy. Nothing on the page prompts the question, so the energy bill never enters her comparison of this flat with others. She subtracts whatever she implicitly assumes when the topic never comes up. If that is "nothing special", the deduction is near zero, and silence beats every displayed letter.

The salience literature measures the second kind of behaviour and finds the bias goes **toward zero, not toward the mean**: consumers under-react to sales taxes that are not in the posted price (Chetty, Looney & Kroft 2009), to tolls they do not see (Finkelstein 2009), and to shrouded shipping costs (Brown, Hossain & Morgan 2010). Nobody in those studies "believes the average tax". They act as if the tax were smaller than it is.

**What this buys and what it costs.** It buys a mechanism that can cross the cap, with one parameter. It costs an assumption the data cannot fully check: the default must be optimistic, below the average verified A–D cost (Corollary E2a). Inattention alone is not enough; a default equal to the prior mean is cursedness again and reproduces the cap.

#### 1.5 Where this sits relative to the two suggestions on the table

- **The faculty suggestion** ("buyers who see a bad letter anchor on it; buyers who see nothing anchor on other signals") has two readings. Read as a belief rule, it is §1.2 and is capped. Read as focus ("a displayed letter puts energy in the comparison; with no letter, the comparison runs on location, size, photos"), it is exactly display-triggered attention, Kőszegi–Szeidl (2013) style. The extension formalises the second reading.
- **Bastien's question "is the buyer attentive or not?"** is the parameter $a=\alpha_0/\alpha_1$: how much attention a silent listing gets relative to a displayed one. Houses look attentive ($a\approx1$); apartments do not ($a\approx0.1$–$0.2$), under the normalisation discussed in §6.8.

#### 1.6 Why the extension is an extension, not a new baseline

The current model fits houses ($\hat\lambda=0.4$, $t=1.1$). It also carries the paper's identification of $\rho$ and $c_0$, its regimes and its subsidy result. The extension nests it at $a=1$, so the natural structure is: baseline = the paper's model (full attention); extension = one parameter that explains why apartments reject the baseline. Houses then serve as the in-sample check that the extension collapses to the baseline where the baseline fits.

---

### 2. Primitives

The extension keeps the paper's environment (§4.1 of the draft): a seller with observables $X$ and quality $\theta\in\{0,1\}$; information status $K$ with $\Pr(K=1)=\pi$; $\Pr(\theta=1)=\bar\theta$; buyers observe $(d,p,X)$ but not $K$. The **equilibrium concept** is the paper's: a perfect Bayesian equilibrium in which sellers (through their agency) choose $d$ optimally given prices, prices equal the buyer-share-weighted mean valuation, and attentive buyers' beliefs after silence are derived from the sellers' strategies by Bayes' rule. Inattentive buyers form no belief; their behaviour is a primitive (the default). This is a "behavioural PBE" in the sense of Gabaix (2019): rational agents best-respond to a population whose attention is exogenous.

Timing: (1) nature draws $(\theta,K)$ and the agency's sanction exposure; (2) the agency lists the property and chooses $d$ (only if $K=1$); (3) a buyer arrives, is sensitive with probability $\rho$, and if sensitive attends to energy with probability $\alpha_d$; (4) the price is the mean valuation (A8 below).

**Belief and the silent pool (from the paper).** With $\sigma_\theta\equiv\Pr(d=0\mid K=1,\theta)$, Bayes' rule over the four seller types gives the paper's `eq:belief_general`,
$$e(\sigma_0,\sigma_1)=\Pr(\theta=1\mid d=0)=\frac{\pi\bar\theta\sigma_1+(1-\pi)\bar\theta}{\pi\bar\theta\sigma_1+\pi(1-\bar\theta)\sigma_0+(1-\pi)}, \tag{E.4}$$
and the rational expected energy cost of a silent listing is
$$\bar C^N\equiv E[C\mid d=0]=e\,C_1+(1-e)\,C_0=C_0-e\,(C_0-C_1). \tag{E.5}$$

Each assumption is stated, interpreted, and then: what it rules out, what supports it, how it could fail.

---

**Assumption E-A1 (energy enters as a cost) [A].** A dwelling of quality $\theta$ carries a capitalised energy cost $C_\theta$, in log-price points, with $C_0>C_1\ge0$. With letters, $C_k$ is increasing from A to G. Costs are proportional to certified consumption:
$$C_\theta=\kappa_m\,\bar E_\theta,\qquad \kappa_m\equiv\frac{p^E\,\mathcal A(r,T)}{P_m}\times100, \tag{2.1}$$
where $\bar E_\theta$ is mean primary-energy consumption (kWh$_{ep}$/m²/yr), $p^E$ the energy price, $\mathcal A(r,T)=(1-(1+r)^{-T})/r$ the annuity factor, and $P_m$ the local price per m².

- *Interpretation.* $C_\theta$ is what the paper's anchor already builds (`src/rho_identification.py:71–150`, `src/data_prep.py:428–490`): $\beta_1^{\rm anchor}=\kappa_m(\bar E_0-\bar E_1)=C_0-C_1$. The paper's $\beta_1$ is the cost gap; the extension also uses the cost **level** $C_0$.
- *What it buys.* Every ratio we need is unit-free: $R_0\equiv C_0/(C_0-C_1)=\bar E_0/(\bar E_0-\bar E_1)$ does not depend on $p^E$, $r$, $T$ or $P_m$.
- *What it rules out.* A non-energy component of the letter that is not proportional to kWh: e.g., the rental-ban exposure of E–G under *loi Climat*, or a pure "stigma" of a bad letter. Such a component raises $C_0-C_1$ without raising $C_0$ proportionally, which lowers the true $R_0$ (adding the same amount to numerator and denominator of a ratio above 1 lowers it).
- *Evidence.* Cost capitalisation of energy is the premise of the energy-efficiency-gap literature (Allcott & Greenstone 2012); the paper's anchor already assumes it for $C_0-C_1$.
- *How it could fail.* If the rental ban is a large part of the E–G discount, $R_0$ is overstated, the attention bound (E.13) is too generous, and bound violations are understated. That is a reason to test the bound with certified kWh *and* with a rental-ban term (investor share) before trusting it.

---

**Assumption E-A2 (buyer types) [A].** A share $\rho$ of buyers is EPC-sensitive and a share $1-\rho$ is insensitive. An insensitive buyer values every listing at $V(X)-C^{\rm ins}$ for a constant $C^{\rm ins}$ (in the paper, $C^{\rm ins}=C_0$; the value is irrelevant because it cancels from every gap). Unobserved quality $\xi$ is common to both types and is absorbed by the hedonic index (A8).

- *Interpretation.* Same as the paper. $\rho$ is "who could care"; attention (A3) is "who does care about this listing".
- *Rules out.* Heterogeneous cost capitalisation within the sensitive group beyond the attention split.
- *Could fail.* If insensitive buyers' default depended on display, they would add a term with the same structure as A3; the model would then identify $\rho\alpha$ jointly anyway.

---

**Assumption E-A3 (display-triggered attention) [A].** A sensitive buyer attends to energy with probability
$$\Pr(\text{attentive}\mid d=1)=\alpha_1,\qquad \Pr(\text{attentive}\mid d=0)=\alpha_0,\qquad 0\le\alpha_0\le\alpha_1\le1. \tag{E.2}$$
Define $a\equiv\alpha_0/\alpha_1\in[0,1]$, the attention a silent listing receives relative to a displayed one.

- *Interpretation.* A displayed letter (and, since 1 January 2022, the displayed euro estimate of the annual energy bill, plus the "consommation énergétique excessive" mention for F/G [CHECK]) puts energy into the buyer's comparison. A missing letter does not. This is focusing (Kőszegi–Szeidl 2013), "what you see is all there is" (Enke 2020), and the shrouded-attribute logic (Gabaix–Laibson 2006).
- *Equivalent representative form.* Under linear pricing, a population in which a share $\alpha_0$ attends is equivalent, at the mean price, to one buyer putting weight $\alpha_0$ on the rational cost and $1-\alpha_0$ on the default: Gabaix's (2014) sparsity weight. The two forms differ in the *shape* of demand under logit pricing (§3.6), not in mean prices.
- *Rules out.* Silence drawing **more** attention than a label (e.g., buyers who become suspicious and investigate). That would be $\alpha_0>\alpha_1$, i.e., $a>1$, and it is testable: it implies $D<eB$, below the paper's prediction.
- *Evidence.* Under-reaction to non-posted costs is the robust finding of the salience literature; energy-cost inattention specifically is documented by Allcott (2011), Allcott & Taubinsky (2015), Sallee (2014) and Houde (2018) for durables. Rational inattention (Sims 2003; Matějka–McKay 2015) gives a micro-foundation: processing a missing field is costlier than reading a displayed one.
- *Could fail.* If buyers routinely request the DPE at the visit [CHECK legal basis], attention to silence is high by construction and $a$ should be near 1. That is what houses look like.

---

**Assumption E-A4 (inattentive default) [A].** An inattentive sensitive buyer subtracts a default $C^D\ge0$, the same for displayed and silent listings. In estimation we normalise $C^D=0$ (§6.8 explains why it is a normalisation and what it costs).

- *Interpretation.* $C^D$ is what the buyer implicitly assumes when energy never comes up: "a normal flat, nothing to worry about". $C^D=0$ means "no energy cost is priced at all"; it does not mean the buyer believes the dwelling consumes nothing.
- *Why the same $C^D$ for both states.* An inattentive buyer is, by definition, not using what the listing shows about energy; letting her default depend on $d$ would reintroduce attention through the back door.
- *Rules out.* A default below zero (energy as a perceived *gain*). $C^D<0$ would let $D/B$ exceed $R_0$ and is not economically meaningful.
- *Evidence.* The shrouded-cost evidence (§1.4) supports a default near zero. There is no housing-specific evidence yet [C]. Candidate reasons for apartments: energy bundled into co-ownership charges under collective heating; buyers coming from rentals with heating included; short visits in tight markets [C].
- *Could fail.* If the default is near the prior mean, attention cannot produce $D>B$ (Corollary E2a) and the apartment wedge must come from elsewhere ($\xi$, agency pricing).

---

**Assumption E-A5 (truthful disclosure, including old certificates) [A].** A displayed letter is the dwelling's true letter under a valid certificate. Pre-July-2021 certificates remained valid during the transition (2013–17 certificates until end-2022, 2018–June 2021 until end-2024 [CHECK]), so some displayed letters are truthful old-method letters.

- *Interpretation.* This is the paper's No Falsification, plus Bastien's point that old letters are not lies.
- *Consequence for measurement.* The registry contains only post-July-2021 certificates. Holders of valid old certificates are coded $K=0$. Their disclosures ($d=1,K=0$; 29.5% of apartment listings per notes A.15, not re-run) are truthful; their silences are informed hiders coded as uninformed.
- *Rules out.* Strategic misreporting. Listing-vs-registry letter disagreement (26% of matched apartment disclosures, notes Task 2 §0.4) is attributed to old-method letters and match noise, not lies.

---

**Assumption E-A6 (uninformedness is certification friction) [A].** $K=0$ means the seller has no valid certificate at the listing date: the certificate is pending (diagnosticians were scarce after the 2021 method change) or was never commissioned. The agency lists anyway. $K\perp\theta$ as in the paper.

- *Interpretation.* Bastien's friction story (notes A.14). The unmatched share falls from 62.5% to 18.4% over the period as supply catches up (V2-QUEUE, not re-run).
- *Measurement consequence [D, from code].* The registry match accepts certificates dated *after* the listing (date weight 0.2, accept threshold 0.3; `ADEME/match_improved.py:125–143,220–262`, `ADEME/enrich_listings.py:175`). Under the friction story such listings are uninformed at listing but coded $K=1$, and if silent they are coded as informed hiders. Together with A5's old-certificate holders, $\hat\pi$ carries two biases of opposite sign, and $\hat\sigma_\theta$ includes non-strategic "pending" silence.
- *Role in the extension.* These are measurement issues for the baseline objects $\hat\pi$, $\hat\sigma_\theta$, $\hat e^*$. They are **not** part of the attention mechanism. §6, step 2, shows how much they move the extension's estimates (very little in apartments, more in houses).

---

**Assumption E-A7 (delegated disclosure, single hiding cost) [A]/[C].** Every listing in the data is an agency listing (Bastien). The agency executes $d$. If it hides an available certificate, it bears an expected sanction and reputational cost $k$ (€) and receives a commission share $\tau$ of the price. The seller may bear an additional cost $c^s$ (liability at sale). In seller-price units (log points) the hiding cost is
$$c_0=\frac{100\,k}{\tau P}+c^s. \tag{2.2}$$
The main text uses a single $c_0$ per market. The appendix (§4.7) replaces it by a distribution $F$.

- *Interpretation.* Hiding is cheap in euros but expensive in log points because the decision-maker keeps only $\tau$ of the gain. Illustration [C, amounts CHECK]: $k=€1{,}000$, $\tau=5\%$, $P=€250{,}000$ give $c_0=100\times1000/(0.05\times250000)=8$ log points.
- *Rules out.* Side payments from seller to agency for hiding.
- *Could fail.* If agencies inflate asking prices on silent listings to win mandates (Levitt & Syverson 2008; Rutherford, Springer & Yavas 2005 [CHECK]), the silent premium is a seller-side listing artefact, not buyer attention. The within-agency test (§9, G1) separates them.

---

**Assumption E-A8 (linear pricing, composition-controlled indices) [A].** The log price of a listing at the reference $X$ is the buyer-share-weighted mean valuation (main.tex:485). The Chapter-1 hedonic indices hold $X$ fixed within market, so group gaps contain no observable composition (Bastien). Unobserved quality $\xi$ satisfies $E[\xi\mid K,\theta,d,X]=E[\xi\mid X]$.

- *What it buys.* Closed forms. Notes Prop. 2 shows every *ordering* result survives exact logit pricing (§3.6).
- *What it does not settle.* Whether the **levels** of the group indices are evaluated at a common reference $X$ across EPC groups (needed for level gaps to be composition-free; DiDs only need the reference to be fixed over time within a group). §5.6 shows level gaps behave very differently from DiDs, so this is a gate item (§9, G7) [CHECK].

---

### 3. Prices

#### 3.1 The perceived deduction

**Lemma E1 (perceived deduction and prices) [D].** Under E-A1–E-A4 and E-A8, the mean energy cost subtracted by sensitive buyers is
$$\bar{\mathcal D}(k)=\alpha_1C_k+(1-\alpha_1)C^D\ \ \text{(letter $k$ displayed)},\qquad \bar{\mathcal D}(N)=\alpha_0\bar C^N+(1-\alpha_0)C^D\ \ \text{(silent)}, \tag{E.6}$$
where $\bar C^N\equiv E[C\mid d=0]=eC_1+(1-e)C_0$ (E.5), and every price at the reference $X$ is $p=\Lambda(X)-\rho\,\bar{\mathcal D}$, with $\Lambda(X)\equiv V(X)-(1-\rho)C^{\rm ins}$ common to all listings.

*Proof.* A sensitive buyer's valuation is
$$u=V(X)-\mathcal D,\qquad \mathcal D=\begin{cases}C_k&\text{attentive, letter $k$ shown}\\ \bar C^N&\text{attentive, silent}\\ C^D&\text{inattentive.}\end{cases} \tag{E.1, E.3}$$
The attentive buyer after silence uses the rational expectation of cost given silence. In the binary model the silent pool has a share $e$ of $\theta=1$ (E.4, the paper's `eq:belief_general`), so $E[C\mid d=0]=eC_1+(1-e)C_0=\bar C^N$. Averaging over attention with (E.2): if a letter is shown, $E[\mathcal D\mid\text{sensitive}]=\alpha_1C_k+(1-\alpha_1)C^D$; if not, $\alpha_0\bar C^N+(1-\alpha_0)C^D$. The insensitive buyer values every listing at $V(X)-C^{\rm ins}$. The mean valuation is $(1-\rho)(V-C^{\rm ins})+\rho(V-\bar{\mathcal D})=V-(1-\rho)C^{\rm ins}-\rho\bar{\mathcal D}$. $\square$

Note that **$e$ enters only through $\bar C^N$, and $\bar C^N$ enters only with weight $\alpha_0$.** That single fact drives most of what follows.

#### 3.2 The two estimands

Take differences against displayed E–G ($k=L$, cost $C_0$). For displayed A–D ($k=H$, cost $C_1$):
$$B=p_H-p_L=-\rho[\alpha_1C_1+(1-\alpha_1)C^D]+\rho[\alpha_1C_0+(1-\alpha_1)C^D]=\rho\alpha_1(C_0-C_1). \tag{E.7}$$
The default cancels because both listings are displayed: inattentive buyers subtract $C^D$ from both.

For silence:
$$D=p_N-p_L=-\rho[\alpha_0\bar C^N+(1-\alpha_0)C^D]+\rho[\alpha_1C_0+(1-\alpha_1)C^D].$$
Collect the $C^D$ terms: $-\rho(1-\alpha_0)C^D+\rho(1-\alpha_1)C^D=\rho(\alpha_0-\alpha_1)C^D$. So
$$D=\rho\big[\alpha_1C_0-\alpha_0\bar C^N+(\alpha_0-\alpha_1)C^D\big]=\rho\big[\alpha_1(C_0-C^D)-\alpha_0(\bar C^N-C^D)\big]. \tag{E.8}$$
The default no longer cancels, because a silent listing gets attention $\alpha_0$ while a displayed one gets $\alpha_1$.

#### 3.3 The perceived cost of silence and the "effective belief"

Divide (E.8) by $\rho\alpha_1$ and use $a=\alpha_0/\alpha_1$:
$$\frac{D}{\rho\alpha_1}=(C_0-C^D)-a(\bar C^N-C^D)=C_0-\underbrace{\big[C^D+a(\bar C^N-C^D)\big]}_{\equiv\,C^*}. \tag{E.9}$$
$C^*$ is **the cost the market behaves as if a silent listing carries, in the same units as a displayed cost.** It is a weighted average of the default (weight $1-a$) and the rational pool cost (weight $a$). Two limits: full relative attention ($a=1$) gives $C^*=\bar C^N$; none ($a=0$) gives $C^*=C^D$.

Two immediate consequences.

**(i) Silence is priced like a displayed letter with cost $C^*$.** For any displayed letter $k$, by (E.6) and the definition of $C^*$:
$$p_k-p_N=-\rho[\alpha_1C_k+(1-\alpha_1)C^D]+\rho[\alpha_0\bar C^N+(1-\alpha_0)C^D]=-\rho\alpha_1\big(C_k-C^*\big). \tag{E.10}$$
(Expand the right-hand side with $C^*=C^D+a(\bar C^N-C^D)$ and $\alpha_0=a\alpha_1$; sympy confirms the identity.) Plotting $p_k-p_N$ against $C_k$ letter by letter gives a straight line with slope $-\rho\alpha_1$ crossing zero at $C_k=C^*$.

**(ii) The silence-to-green ratio.** Divide (E.9) by (E.7):
$$\frac{D}{B}=\frac{C_0-C^*}{C_0-C_1}\equiv\tilde e. \tag{E.11}$$
In the paper $D/B=e$. In the extension, **the paper's formulas all hold with $e$ replaced by the "effective belief" $\tilde e$.** Expanding $C^*$ and using $\bar C^N=C_0-e(C_0-C_1)$ (so $\bar C^N/(C_0-C_1)=R_0-e$):
$$\tilde e=R_0-\frac{C^D}{C_0-C_1}-a\Big(R_0-e-\frac{C^D}{C_0-C_1}\Big)=a\,e+(1-a)\,(R_0-r_D),\qquad r_D\equiv\frac{C^D}{C_0-C_1}. \tag{E.11'}$$
With $C^D=0$: **$\tilde e=a\,e+(1-a)R_0$, a weighted average of the Bayesian belief $e\in[0,1]$ and the number $R_0>1$**, which is the "effective belief" of a buyer who prices no energy cost at all. Because $R_0>1$, $\tilde e$ can exceed 1, and that is precisely what lets $D$ exceed $B$.

#### 3.4 Nesting, when silence beats A–D, and the bound

**Proposition E1 (nesting) [D].** If $\alpha_0=\alpha_1$ (i.e., $a=1$), then $D=e\,B$ for every attention level $\alpha_1\in(0,1]$ and every default $C^D$. The paper's model is the special case $\alpha_0=\alpha_1=1$.

*Proof.* With $a=1$, (E.11') gives $\tilde e=e$, so $D=\tilde eB=eB$. Directly: (E.8) with $\alpha_0=\alpha_1$ is $\rho\alpha_1[(C_0-C^D)-(\bar C^N-C^D)]=\rho\alpha_1(C_0-\bar C^N)=\rho\alpha_1e(C_0-C_1)=eB$, using $C_0-\bar C^N=e(C_0-C_1)$. $\square$

*What it means.* Inattention that is the same for displayed and silent listings is observationally equivalent to a smaller $\rho$: it scales $B$ and $D$ together. Only *differential* attention matters. Houses could be "inattentive" in levels and still be the paper's model.

**Proposition E2 (when silence beats verified A–D) [D].** Assume $\bar C^N>C^D$. Then
$$p_N>p_H\iff C^*<C_1\iff a<\frac{C_1-C^D}{\bar C^N-C^D}. \tag{E.12}$$

*Proof.* By (E.10) with $k=H$ ($C_k=C_1$): $p_H-p_N=-\rho\alpha_1(C_1-C^*)$, so $p_N>p_H$ iff $C^*<C_1$ (given $\rho\alpha_1>0$). Substitute $C^*$: $C^D+a(\bar C^N-C^D)<C_1\iff a(\bar C^N-C^D)<C_1-C^D\iff a<(C_1-C^D)/(\bar C^N-C^D)$, dividing by $\bar C^N-C^D>0$. $\square$

**Corollary E2a (the default must be optimistic) [D].** A necessary condition for $p_N>p_H$ is $C^D<C_1$.
- If the default equals the prior mean, $C^D=\bar C=\bar\theta C_1+(1-\bar\theta)C_0\ge C_1$, then $p_N\le p_H$ for every $a$: inattention with a mean default is cursedness again.
- If the default equals the rational pool cost, $C^D=\bar C^N$, then $C^*=\bar C^N$ for every $a$: attention does not matter at all.
- If $C^D=0$, silence beats A–D iff $a<C_1/\bar C^N$.

*Proof.* $C^*$ is a convex combination of $C^D$ and $\bar C^N$, and $\bar C^N\ge C_1$ (since $e\le1$). If $C^D\ge C_1$, both endpoints are $\ge C_1$, so $C^*\ge C_1$ and (E.12) fails. The three bullets substitute the stated $C^D$. $\square$

*What it means.* The existence of inattention does not deliver the premium. The optimism of the default does. That is the assumption a referee will push on, and the honest statement of it is this corollary.

**Corollary E2b (falsifiable upper bound) [D].** If $C^D\ge0$ and $a\in[0,1]$, then
$$\frac{D}{B}\le R_0\equiv\frac{C_0}{C_0-C_1}=\frac{\bar E_0}{\bar E_0-\bar E_1}, \tag{E.13}$$
with equality iff $C^*=0$, i.e., iff $C^D=0$ and $a=0$.

*Proof.* From (E.11), $D/B=R_0-C^*/(C_0-C_1)$. $C^*$ is a convex combination of $C^D\ge0$ and $\bar C^N\ge C_1\ge0$, so $C^*\ge0$, and $D/B\le R_0$. Equality iff $C^*=0$, which for $\bar C^N>0$ requires both $C^D=0$ and $a=0$. $\square$

*What it means.* The extension can push silence above A–D, but not without limit: at most to the point where silent listings are priced as if they carried no energy cost. A market with $D/B$ well above $R_0$ rejects attention with a non-negative default and points back to unobserved quality or seller-side pricing.

#### 3.5 What happens to the paper's wedge

In levels, define $\lambda^{\rm lev}\equiv D-eB$ (the paper's wedge, at the true $e$). From (E.11'):
$$\lambda^{\rm lev}=B(\tilde e-e)=(1-a)\,B\,(R_0-e-r_D)=\rho(\alpha_1-\alpha_0)(\bar C^N-C^D). \tag{E.14}$$
(The last form: $B(R_0-e-r_D)=\rho\alpha_1(\bar C^N-C^D)$; multiply by $1-a$.) **$\lambda=0$ iff $a=1$ (or $C^D=\bar C^N$).** So the paper's over-identifying restriction is, in the extension, the hypothesis of equal attention to silent and displayed listings. Its rejection in apartments is a rejection of that hypothesis, not of the disclosure game. §5 does the same algebra for the DiD, which is what the paper actually estimates.

#### 3.6 Robustness to exact logit pricing (summary)

Under the paper's exact demand $\Gamma(p)=\rho G((v_1-p)/\varsigma)+(1-\rho)G((v_0-p)/\varsigma)$, the notes (Prop. 2) show the optimal price is nondecreasing in the sensitive buyers' mean valuation $v_1$ when $\rho G_1^2+(1-\rho)G_0(2G_1-G_0)\ge0$ ($G_j$ the logistic CDF at buyer type $j$'s surplus). Every *ordering* result here (E2, E2a, E2b) uses only that monotonicity, so it holds exactly; magnitudes in (E.7)–(E.11) scale by pass-through $dP^*/dv_1\in[0,1]$. Two caveats. (a) In cost form $v_1\le v_0$ is possible, so the sufficient condition must be checked at the estimated $\hat\varsigma$ [to do]. (b) With attention *shares* rather than a representative weight, a silent listing faces three buyer segments, and a seller may price to the inattentive segment and accept a lower sale probability; that predicts longer time-on-market for silent listings at a higher price [C]. This is the one place where the share and weight forms differ.

#### 3.7 Worked example (apartments, estimation-sample means) [E]

Inputs (§12): $\bar E_1=185$, $\bar E_0=327$ kWh/m²/yr (band midpoints, $K=1$ registry letters, 2022–24); $\hat e^*=0.593$; DiD gaps $\hat\beta_1=4.06$, $\hat\Delta=8.53$; anchor $C_0-C_1\approx9.0$ log points (mean).

1. **Rational pool cost.** $\bar C^N=e\bar E_1+(1-e)\bar E_0=0.593\times185+0.407\times327=109.7+133.1=243$ kWh. In log points, $\bar C^N=(R_0-e)(C_0-C_1)\approx(2.30-0.593)\times9.0\approx15.4$.
2. **Bound.** $R_0=327/(327-185)=327/142=2.30$ (at means; the mean of market ratios is 2.31).
3. **Threshold for silence to beat A–D with $C^D=0$.** $C_1/\bar C^N=185/243=0.76$. Any relative attention below 0.76 puts silence above A–D.
4. **Observed ratio.** $\hat\Delta/\hat\beta_1=8.53/4.06=2.10$, below the bound 2.30 but far above the paper's prediction $\hat e^*=0.593$.
5. **Perceived cost of silence (DiD).** From (E.11), $C^*=C_0-(D/B)(C_0-C_1)=327-2.10\times142=327-298=28$ kWh. Silent apartments are priced as if they consumed 28 kWh$_{ep}$/m²/yr: better than the A band (≤70, midpoint 35).
6. **Relative attention with $C^D=0$.** $a=C^*/\bar C^N=28/243=0.12$. (The regression in §7 gives 0.13–0.21 depending on the estimator.)
7. **Letter line.** With $C^*\approx28$ kWh, (E.10) predicts that every displayed letter, including A (35 kWh), sells at or below silence. Under the paper's model the crossing would be at $\bar C^N=243$ kWh, between D (215.5) and E (290.5). This is a sharp test with letter-level indices (§9, G8).

Houses, same steps: $\bar C^N=0.595\times178+0.405\times339=243$ kWh; $R_0=2.10$; $\hat\Delta/\hat\beta_1=0.67$; $C^*=339-0.67\times161=231$ kWh, almost exactly $\bar C^N$. Silence is priced at the rational pool cost.

---

### 4. Sellers, the agency, and equilibrium

#### 4.1 Hiding gains

An informed seller of type $\theta$ compares the silent price with the price of her own displayed letter. By (E.10), with $C_k=C_\theta$:
$$G_\theta\equiv p_N-p_\theta=\rho\alpha_1\,(C_\theta-C^*),\qquad G_0-G_1=\rho\alpha_1(C_0-C_1)=B. \tag{E.15}$$
Note $G_0=p_N-p_L=D$: **the low type's gain from hiding is the observed silence premium, in any model with linear pricing.** The paper's $\hat c_0=\hat\beta_1\hat e^*$ is not a measurement of that gain; it is the full-attention *prediction* of it.

Two cases:
- **Paper ($a=1$, $C^*=\bar C^N$, between $C_1$ and $C_0$):** $G_1=-(1-e)B<0<G_0=eB$. Only low types can gain. This is the Milgrom–Dye logic behind Corollary `cor:hq_disclose`.
- **Extension with $C^*<C_1$:** $G_1>0$ as well. **Every type gains from silence**; what stops sellers from hiding is the cost of hiding.

Numbers [E]. Apartments, DiD units: $G_0=\hat\Delta=8.53$, $G_1=\hat\Delta-\hat\beta_1=4.47$ (positive in 82% of markets). Under the paper's model they would be $\hat\beta_1\hat e^*=2.4$ and $-(1-\hat e^*)\hat\beta_1=-1.65$. Houses: $G_0=3.89$, $G_1=-1.93$; the high type loses from silence, as in the paper.

#### 4.2 The agency's decision

All listings are agency listings, and the agency executes the display. Let the agency's expected cost of hiding an available certificate be $k$ euros (expected fine times detection probability, plus reputational and legal exposure), and its revenue be a share $\tau$ of the price $P$. Ignoring the second-order effect of $d$ on the sale probability, the agency hides iff its commission gain exceeds $k$:
$$\tau P\,\frac{G_\theta}{100}\ \ge\ k\iff G_\theta\ \ge\ \frac{100\,k}{\tau P}. \tag{E.16}$$
If the seller also bears $c^s$ (in log points) and the agency internalises it (for repeat business), the threshold is $c_0=100k/(\tau P)+c^s$, which is (2.2). Two features matter for the paper.
1. **Small euro sanctions, large log-point costs.** Because the agency keeps only $\tau$ of the price gain, a sanction of about €1,000 is worth 8 log points of the seller's price at $\tau=5\%$, $P=€250$k [C, amounts CHECK].
2. **$c_0$ falls with the price level.** In log points, $c_0\propto1/P_m$, so hiding should be more frequent in expensive markets, holding enforcement fixed [C, testable with $\hat\sigma_{0,m}$ and $P_m$].

#### 4.3 Disclosure with a single hiding cost (main text)

Let $c_0\ge0$ be common to all informed sellers in a market, and keep the paper's extra cost $c_1\ge0$ for high types who hide. An informed type-$\theta$ seller hides iff $G_\theta>c_0+\theta c_1$ (ties broken by mixing).

**Lemma E3 (high types still disclose unless every low type hides) [D].** In any equilibrium with $\sigma_0^*<1$, $\sigma_1^*=0$.

*Proof.* $\sigma_0^*<1$ requires that some low type weakly prefers disclosure: $G_0\le c_0$. Then $G_1=G_0-B<G_0\le c_0\le c_0+c_1$ because $B>0$. So the high type strictly prefers to disclose. $\square$

*What it means.* The paper's Corollary survives, but for a different reason. In the paper, high types disclose because silence loses them money. In the extension, silence can pay them too ($G_1>0$), but it always pays them $B$ less than it pays low types, and with a common cost the low type is always the first to want to hide. In Complete Adverse Selection ($\sigma_0^*=1$), $\sigma_1^*>0$ is possible iff $G_1>c_0+c_1$.

#### 4.4 Equilibrium regimes with a single cost

With $\sigma_1=0$, the belief is the paper's (`eq:belief_simplified`), $e(\sigma_0)=(1-\pi)\bar\theta/[\pi(1-\bar\theta)\sigma_0+(1-\pi)]$, and the low type's gain depends on $\sigma_0$ only through $\bar C^N$:
$$G_0(\sigma_0)=\rho\alpha_1(C_0-C^D)-\rho\alpha_0\big(\bar C^N(\sigma_0)-C^D\big),\qquad \bar C^N(\sigma_0)=C_0-e(\sigma_0)(C_0-C_1). \tag{E.17}$$
Differentiate: $G_0'(\sigma_0)=-\rho\alpha_0\,\partial\bar C^N/\partial\sigma_0=\rho\alpha_0(C_0-C_1)\,e'(\sigma_0)$. Since $e'(\sigma_0)<0$ (paper's Lemma `lem:belief_monotone`), $G_0$ is **weakly decreasing, and strictly decreasing iff $\alpha_0>0$.** The feedback "more hiding worsens the pool, which shrinks the gain" is the paper's, multiplied by $\alpha_0$.

**Proposition E3 (regimes) [D].** Let $G_0(0)$ and $G_0(1)$ be the gains at $\sigma_0=0$ ($e=\bar\theta$) and $\sigma_0=1$ ($e=e(1)=(1-\pi)\bar\theta/(1-\pi\bar\theta)$).
1. **Cost-Deterred Hiding** if $c_0>G_0(0)$: $\sigma_0^*=0$, $e^*=\bar\theta$, $D=G_0(0)$.
2. **Complete Adverse Selection** if $c_0<G_0(1)$: $\sigma_0^*=1$, $e^*=e(1)$ (and $\sigma_1^*>0$ if $G_1>c_0+c_1$).
3. **Partial Pooling** if $G_0(1)\le c_0\le G_0(0)$: $\sigma_0^*$ solves $G_0(\sigma_0^*)=c_0$, so **$D=c_0$, exactly as in the paper.** If $\alpha_0>0$ the solution is unique. If $\alpha_0=0$, $G_0$ is constant, Partial Pooling requires $c_0=G_0$ exactly, and then every $\sigma_0\in[0,1]$ is an equilibrium.

The width of the Partial Pooling band is
$$G_0(0)-G_0(1)=\rho\alpha_0(C_0-C_1)\big(\bar\theta-e(1)\big)=a\,B\,\big(\bar\theta-e(1)\big). \tag{E.18}$$

*Proof.* (1)–(2): with $G_0$ weakly decreasing, $c_0>G_0(0)$ implies $G_0(\sigma_0)<c_0$ for all $\sigma_0$, so no low type hides; symmetric for (2). (3): $G_0$ is continuous, so by the intermediate value theorem there is $\sigma_0^*\in[0,1]$ with $G_0(\sigma_0^*)=c_0$; strict monotonicity gives uniqueness when $\alpha_0>0$. In Partial Pooling, $D=G_0(\sigma_0^*)=c_0$ by (E.15). (E.18): $\bar C^N(1)-\bar C^N(0)=(C_0-C_1)(\bar\theta-e(1))$; multiply by $\rho\alpha_0=a\rho\alpha_1$ and use $B=\rho\alpha_1(C_0-C_1)$. Sympy confirms. $\square$

**What survives and what changes.**
- "The non-disclosure premium is a revealed hiding cost" ($D=c_0$ in Partial Pooling) **survives unchanged.** It is a statement about the marginal seller, not about buyers.
- The **width** of the Partial Pooling band shrinks by the factor $a$. Numbers [E, mixing level $B$ with DiD $a$, so indicative only]: apartments $a B(\bar\theta-e(1))\approx0.21\times6.03\times0.174=0.22$ log points (paper's model: $6.03\times0.174=1.05$); houses $0.96\times13.30\times0.134=1.71$.
- **Consequence.** In apartments a single $c_0$ would have to fall in a window of about 0.2 log points for the market to show interior hiding; we report this as a limitation of the single-cost specification.

#### 4.5 Non-strategic silence

Attention allows $\sigma_1>0$ only when silence sells above a verified efficient rating ($G_1>0$). The registry shows similar hiding rates for the two grades, and house sellers of high quality stay silent although silence costs them about two log points, so some silence is not strategic (listings with a pending certificate, for instance). The flat pattern is therefore not evidence for attention.

#### 4.6 What $c_0$ becomes, and why it is large

The marginal informed low type hides iff $G_0\ge c_0$, and in Partial Pooling (or at the margin of $F$) $c_0=G_0=D$. So under the extension the right inversion is the silence premium itself:
- **DiD reading** (pre-reform gaps treated as nuisance, as the paper does): $\hat c_0=\hat\Delta=8.5$ log points in apartments, or the model-fitted value $\hat\beta_1[R_0-\hat a(R_0-\hat e^*)]=8.0$ (§6, step 6).
- **Level reading:** $\hat c_0=D^{\rm post}=13.1$.

The paper explicitly rejects $\hat c_0=\hat\Delta$ (04:428) because, under full attention, it would impose the restriction $\hat\Delta=\hat\beta_1\hat e^*$ that $\hat\lambda$ tests. Under the extension that restriction is no longer part of the model ($a$ is estimated from it), so the shortcut becomes the correct inversion.

**Plausibility.** 8 log points is about 8% of price, an order of magnitude above statutory fines in euros if the seller bore them. Under delegated disclosure (E.16) it corresponds to an agency-level expected cost of about €1,000 per hidden listing at $\tau=5\%$, $P=€250$k, or about €500 at $\tau=2.5\%$ [C]. Houses: $\hat c_0$ moves from 3.5 to 3.8–3.9.

#### 4.7 (removed)

*(Removed at Bastien's request, 2026-10-09: dispersed hiding costs are no longer part of the analysis.)*

### 5. The reform in the extension: levels versus DiD

This is the part that most needs care, because the paper's estimands are **DiDs**, while the intuition of §3 is about **levels**. The same algebra identifies different attention objects in the two cases.

#### 5.1 Setup

Two periods, $t\in\{\text{pre},\text{post}\}$ (October 2018–June 2021, July 2021–July 2024). Let attention and sensitivity vary by period, and work with the **effective attention mass**
$$\omega_j^t\equiv\rho^t\alpha_j^t,\qquad j\in\{1\ \text{(display)},\,0\ \text{(silent)}\}.$$
$\rho$ and $\alpha$ only ever appear multiplied, so nothing is lost; relative attention in period $t$ is $a^t=\omega_0^t/\omega_1^t=\alpha_0^t/\alpha_1^t$. Maintain [A]: $C_0$, $C_1$, $C^D$ stable across the reform, and (for now) **$e$ stable**, so $\bar C^N$ is stable. Applying (E.7)–(E.8) period by period:
$$B^t=\omega_1^t(C_0-C_1),\qquad D^t=\omega_1^t(C_0-C^D)-\omega_0^t(\bar C^N-C^D). \tag{E.21}$$

#### 5.2 Levels identify $a^t$

Dividing, exactly as in (E.11'):
$$\frac{D^t}{B^t}=R_0-a^t(R_0-e)-(1-a^t)\,r_D. \tag{5.1}$$
With $C^D=0$, $a^t=(R_0-D^t/B^t)/(R_0-e)$. So **levels identify relative attention in each period**: how much a silent listing is scrutinised relative to a displayed one, at that time.

#### 5.3 DiDs identify the spillover $a_\Delta$

The paper's estimands are post-minus-pre differences. From (E.21):
$$\hat\beta_1=B^{\rm post}-B^{\rm pre}=\Delta\omega_1\,(C_0-C_1), \tag{E.22}$$
$$\hat\Delta=D^{\rm post}-D^{\rm pre}=\Delta\omega_1(C_0-C^D)-\Delta\omega_0(\bar C^N-C^D),$$
where $\Delta\omega_j\equiv\omega_j^{\rm post}-\omega_j^{\rm pre}$. Divide the second by the first, and define the **spillover**
$$a_\Delta\equiv\frac{\Delta\omega_0}{\Delta\omega_1}=\frac{\text{reform-induced increase in attention to silent listings}}{\text{reform-induced increase in attention to displayed labels}}.$$
Then, step by step: $\hat\Delta/\hat\beta_1=(C_0-C^D)/(C_0-C_1)-a_\Delta(\bar C^N-C^D)/(C_0-C_1)$; use $(C_0-C^D)/(C_0-C_1)=R_0-r_D$ and $(\bar C^N-C^D)/(C_0-C_1)=R_0-e-r_D$:
$$\frac{\hat\Delta}{\hat\beta_1}=R_0-a_\Delta(R_0-e)-(1-a_\Delta)\,r_D. \tag{E.23}$$
This is (5.1) with $a^t$ replaced by $a_\Delta$. With $C^D=0$, multiply by $\hat\beta_1$ and subtract $\hat\beta_1e$:
$$\hat\Delta=(1-a_\Delta)\,\hat\beta_1R_0+a_\Delta\,\hat\beta_1e,\qquad \boxed{\hat\lambda\equiv\hat\Delta-\hat\beta_1e=(1-a_\Delta)\,\hat\beta_1\,(R_0-e)=(\Delta\omega_1-\Delta\omega_0)\,\bar C^N.} \tag{E.24}$$
(Last equality: $\hat\beta_1(R_0-e)=\Delta\omega_1(C_0-C_1)(R_0-e)=\Delta\omega_1\bar C^N$.) For general $C^D$: $\hat\lambda=(1-a_\Delta)\hat\beta_1(R_0-e-r_D)$. All verified in sympy.

**Reading (E.24).** The reform raised the weight on energy by $\Delta\omega_1$ for displayed listings and by $\Delta\omega_0$ for silent ones. Had silent listings received the same increase, their price relative to displayed E–G would have changed by the paper's $\hat\beta_1e$. They received less, and the shortfall, priced at the rational silent-pool cost $\bar C^N$, is exactly $\hat\lambda$. **The paper's over-identifying wedge is the part of the reform's price effect that silence escaped.**

#### 5.4 How $a_\Delta$ relates to $a$, and what each means

Substitute $\omega_0^t=a^t\omega_1^t$ into the definition:
$$a_\Delta=\frac{a^{\rm post}\omega_1^{\rm post}-a^{\rm pre}\omega_1^{\rm pre}}{\omega_1^{\rm post}-\omega_1^{\rm pre}}=a^{\rm post}+\big(a^{\rm post}-a^{\rm pre}\big)\frac{\omega_1^{\rm pre}}{\Delta\omega_1}. \tag{E.25}$$
(Add and subtract $a^{\rm post}\omega_1^{\rm pre}$ in the numerator.) Three consequences.

1. **If relative attention is stable ($a^{\rm pre}=a^{\rm post}=a$), then $a_\Delta=a$.** The DiD and level objects coincide.
2. **If the pre-period price gaps were not driven by energy attention ($\omega_1^{\rm pre}=0$, hence $\omega_0^{\rm pre}=0$ because $\alpha_0\le\alpha_1$), then $a_\Delta=a^{\rm post}$ exactly.** Call this **reading R1**. It is the paper's own reading: pre-reform gaps are treated as nuisance that the DiD removes, and $\hat\rho$ measures post-reform sensitivity.
3. **Otherwise (reading R2: pre-period gaps are partly economic), $a_\Delta$ is a "marginal" relative attention.** If relative attention to silence rose with the reform, $a_\Delta>a^{\rm post}$; if it fell, $a_\Delta<a^{\rm post}$. The weight $\omega_1^{\rm pre}/\Delta\omega_1$ equals $B^{\rm pre}/\hat\beta_1$ if levels are clean: 0.49 for apartments, 1.29 for houses [E]. Example: apartments with $a^{\rm pre}=0$, $a^{\rm post}=0.15$ give $a_\Delta=0.15+0.15\times0.49=0.22$.

**What the two objects mean economically.**
- $a^t$ (levels): *at a point in time, how much is a silent listing scrutinised relative to a displayed one?*
- $a_\Delta$ (DiD): *when the reform made energy matter more, did that new attention reach listings that showed nothing?*
- **Houses ($a_\Delta\approx0.95$):** the reform raised attention to energy for every house listing, displayed or not. Energy became something house buyers ask about. A silent house was priced against the (rational) cost of the silent pool.
- **Apartments ($a_\Delta\approx0.1$–$0.2$):** the reform raised attention to *displayed* labels only. The label became something apartment buyers read, not something they ask for. The silent apartment's price did not absorb the energy information that the reform made salient elsewhere.

**An additional assumption hides in "$a_\Delta\in[0,1]$".** The primitive $\alpha_0^t\le\alpha_1^t$ holds period by period, but it does not restrict $\Delta\alpha_0/\Delta\alpha_1$. Reading $a_\Delta\in[0,1]$ requires [A] that the reform did not lower attention to silence ($\Delta\omega_0\ge0$) and did not raise it more than attention to displays ($\Delta\omega_0\le\Delta\omega_1$). Both are natural for a reform that changed the legal status of displayed labels.

#### 5.5 The role of "$e$ stable across the reform"

Drop stability: let the pool belief be $e^{\rm pre}$ before and $e^{\rm post}$ after, and keep $C^D=0$. The silent term becomes $\omega_0^{\rm post}\bar C^N_{\rm post}-\omega_0^{\rm pre}\bar C^N_{\rm pre}$. Add and subtract $\omega_0^{\rm pre}\bar C^N_{\rm post}$, and use $\bar C^N_{\rm post}-\bar C^N_{\rm pre}=-(e^{\rm post}-e^{\rm pre})(C_0-C_1)$:
$$\hat\lambda\equiv\hat\Delta-\hat\beta_1e^{\rm post}=(\Delta\omega_1-\Delta\omega_0)\,\bar C^N_{\rm post}+\omega_0^{\rm pre}\,(e^{\rm post}-e^{\rm pre})\,(C_0-C_1). \tag{E.26}$$
The estimator $1-\hat a_\Delta=\hat\lambda/[\hat\beta_1(R_0-e^{\rm post})]$ therefore has bias
$$\big(1-\hat a_\Delta\big)-\big(1-a_\Delta\big)=\frac{\omega_0^{\rm pre}}{\Delta\omega_1}\cdot\frac{e^{\rm post}-e^{\rm pre}}{R_0-e^{\rm post}}. \tag{E.27}$$
(Sympy-verified.) Reading it:
- **Direction.** If the silent pool *improved* across the reform ($e^{\rm post}>e^{\rm pre}$), part of the rise in the silent premium is the pool getting better; the estimator mistakes it for inattention and **understates $a_\Delta$**. If the pool worsened, it overstates $a_\Delta$.
- **Under reading R1 the bias is zero** ($\omega_0^{\rm pre}=0$): only the post-period belief matters, and $\hat e^*$ is measured on 2022–24 listings, i.e., in the post period.
- **Magnitude under R2 [E].** $\omega_0^{\rm pre}/\Delta\omega_1=a^{\rm pre}\,B^{\rm pre}/\hat\beta_1$. Apartments: $a^{\rm pre}\times0.49/1.71=0.28\,a^{\rm pre}$ per unit of $\Delta e$, so at most 0.03 for $|\Delta e|\le0.1$. Houses: $a^{\rm pre}\times1.29/1.52=0.85\,a^{\rm pre}$ per unit, so about 0.04 for $|\Delta e|=0.05$.

**What moves $e$, and in which direction [C].** (i) The diagnostician shortage of 2021H2–2022 added "pending" ordinary dwellings to the silent pool. A more uninformed pool moves $e$ toward $\bar\theta$, i.e., up, since $e<\bar\theta$ when low types hide more. As supply caught up, $e$ fell back. (ii) The 1 January 2023 expiry of 2013–17 certificates [CHECK] turned some informed sellers into uninformed ones until re-certification: $e$ up. (iii) The pre-reform silent pool is not observed at all (the registry starts in July 2021). Net sign: unknown. Net size: small in apartments under any reading, because $\omega_0$ is small. That is the general pattern of this extension: **where attention to silence is low, the composition of the silent pool barely matters for prices.**

#### 5.6 The pre-period fact, and why levels cannot pin down $a$

**The fact [E].** In apartments, $B^{\rm pre}=1.97<D^{\rm pre}=4.54$ on average, and $D>B$ in 84% of markets before the reform (93% after). Silence already beat verified A–D before opposability. Under reading R2 this says the mechanism predates the reform, and the reform amplified it by raising attention to displayed labels: silence gained on A–D as well as on E–G ($D-B$ rose from +2.6 to +7.0). Under reading R1 the pre-period gap is nuisance.

**Can levels tell R1 from R2, and estimate $a^t$? No, not robustly [E, new].** Under (5.1) with $C^D=0$ and a common $a^t$ across markets, the level gaps should be proportional across markets, $D^t_m=[R_{0m}-a^t(R_{0m}-e_m)]\,B^t_m$, with no intercept. Two estimators of $a^t$ should then agree:

| Apartments, 45 markets | pre | post |
|---|---|---|
| Ratio of means: $(\bar R_0-\bar D/\bar B)/(\bar R_0-\bar e)$ | $a\approx0.01$ | $a\approx0.09$ |
| Through-origin regression of $D-eB$ on $B(R_0-e)$ | $a=0.83$ (se of $1-a$: 0.07) | $a=0.80$ (0.08) |
| $D_m=k+s\,B_m$ (HC1) | $k=2.7$ (4.7), $s=0.93$ (0.10) | $k=7.5$ (4.7), $s=0.92$ (0.11) |
| Cross-market s.d. of $B_m$ / $D_m$ | 28.9 / 41.7 | 29.2 / 43.1 |

They do not agree. Across markets, $D$ moves about one-for-one with $B$ ($s\approx0.93$, which under (5.1) means $a\approx(2.31-0.93)/1.72=0.80$), and the high average ratio $\bar D/\bar B\approx2.3$ comes from a positive intercept, a silent level premium not proportional to the green premium. The level gaps also vary across markets by about 30–40 log points around means of 2–13, far more than any energy channel can produce. Houses show the mirror image: the level slope of $D$ on $B$ is 0.28 (pre) and 0.23 (post), and the through-origin estimate of $a$ exceeds 1.

**Conclusion.** Level gaps contain a large market-specific component unrelated to energy attention: group-specific reference properties, or unobserved quality differences between groups that the hedonic controls hold fixed over time but not across groups. The DiD removes it; levels do not. So:
- **Estimate $a_\Delta$ from the DiDs** (§6). In the DiD, the intercept is small and insignificant (apartments 2.8, se 1.85; houses 0.3, se 0.8), and the two estimators agree within sampling error.
- **Use levels only for sign facts** ("silence above A–D in most apartment markets, before and after the reform"), not for magnitudes of $a^t$. This withdraws the level calibration in notes A.0/A.6.
- **Whether level gaps are comparable at all** depends on how the Chapter-1 index sets the reference property across EPC groups (§9, G7).

#### 5.7 The trajectory: year-specific windows on the estimation sample [E]

Post windows split by reform year; pre window unchanged; $\hat e^*$ and $R_0$ held at their pooled 2022–24 values; 45 / 97 markets.

| Window | Apts $\hat\beta_1$ | Apts $\hat\Delta$ | Apts $\hat\lambda$ ($t$) | Apts $1-\hat a_\Delta$ (se) | Houses $\hat\beta_1$ | Houses $\hat\Delta$ | Houses $\hat\lambda$ ($t$) | Houses $1-\hat a_\Delta$ (se) |
|---|---|---|---|---|---|---|---|---|
| Y1: Jul 2021–Jun 2022 | 1.99 | 4.33 | 3.13 (4.15) | 0.53 (0.17) | 3.79 | 3.13 | 0.88 (2.54) | 0.11 (0.05) |
| Y2: Jul 2022–Jun 2023 | 4.43 | 9.86 | 7.24 (7.66) | 0.76 (0.12) | 5.92 | 3.77 | 0.23 (0.50) | 0.01 (0.05) |
| Y3: Jul 2023–Jul 2024 | 5.62 | 11.14 | 7.81 (6.46) | 0.72 (0.10) | 7.59 | 4.70 | 0.22 (0.34) | 0.03 (0.05) |
| Full post | 4.06 | 8.53 | 6.12 (6.78) | 0.79 (0.11) | 5.82 | 3.89 | 0.44 (1.10) | 0.04 (0.04) |

In Y1, $\hat\beta_1>0$ in only 37 of 45 apartment markets and 87 of 97 house markets.

**Reading.**
1. $\hat\beta_1$ rises every year in both segments: progressive capitalisation of displayed labels ($\Delta\omega_1$ growing).
2. In apartments, $\hat\Delta$ rises in step and $\hat\lambda$ with it. $\hat\lambda$ is proportional to $\hat\beta_1$ by (E.24), so its rise is not by itself evidence of anything; the scale-free object is $1-\hat a_\Delta$, which rises from 0.53 in Y1 to about 0.75 in Y2–Y3 and is flat afterwards. Attention to silence kept up with attention to labels in the first year more than later, but the Y1 estimate is noisy.
3. In houses, $1-\hat a_\Delta$ falls from 0.11 to about 0.02: attention to silence caught up with attention to labels.
4. The first-year "anomaly" of notes A.14.4 ($\hat\Delta=3.1$ vs $\hat\beta_1=0.2$) was an artefact of averaging over 83 markets, including those where $\hat\beta_1\le0$. On the estimation sample, Y1 sits inside the attention bound: $\hat\Delta/\hat\beta_1=2.18<\bar R_0=2.31$.
5. The friction story predicts the silent pool improved in 2021H2–2022 (more pending ordinary dwellings), which by (E.27), and by using the pooled 2022–24 $\hat e^*$ for Y1, would make the estimator *understate* $a_\Delta$ in Y1. Correcting for it would raise the Y1 estimate further, so friction-driven pool changes do not explain the time pattern away. Year-specific $\hat e^*_t$ and $\hat\pi_t$ are needed before reading more into it.

---

### 6. Identification and estimation: a recipe

Everything below can be implemented with files and functions already in the repo, except where a re-pull is flagged. Market index $m$; property types estimated separately.

#### 6.0 Inputs

| Object | File / function | Columns |
|---|---|---|
| Group price indices | `data/index_{APARTMENT,HOUSE}.csv` via `src/event_study.load_price_indices(path, high_group="ABCD")` | `date`, `EPC`, `cluster_id`→`market_id`, `prices` (level, €/m²; `log_index=log(prices)`), `volume` |
| Market DiDs | `src/event_study.compute_did(idx, min_volume=20)` | `DiD_beta1`, `DiD_delta`, `beta1_pre/post`, `delta_pre/post` |
| Listings + registry | `data/listings_enriched_{TYPE}.parquet` | `market_id`, `d`, `K`, `ademe_epc_score`, `match_score`, `start_date`, `EPC` (listing letter) |
| Supply moments | `src/data_prep.compute_market_stats` → `results/<type>/anchored_diagnostics.csv` | `pi_hat`, `theta_bar_hat`, `sigma_0_hat`, `e_star`, `beta1_anchor`, `rho_m`, `c0_m`, `lambda_m` |
| Energy levels | `src/data_prep.compute_energy_anchor(df)` on 2022–24 listings | `e_bar_0_kwh`, `e_bar_1_kwh` (band midpoints, $K=1$, pooled $d$) |
| **Re-pull needed** | `data/collect_listings.py`, `ADEME/enrich_listings.py` | `date_reception_dpe` (certificate date), certified kWh$_{ep}$/m² per matched certificate, `realtor_ref` |

#### 6.1 Step 1: $\hat\beta_{1,m}$ and $\hat\Delta_m$, unchanged

Exactly as now (pre October 2018–June 2021, post July 2021–July 2024, volume filter 20). Nothing in the extension changes these.

#### 6.2 Step 2: $\hat e^*_m$, and how its measurement problems feed through

As now, eq. `eq:estar`, but note three things.
1. **Timing of $K$.** Listings matched to certificates dated after the listing are coded $K=1$ (A.14). Under the friction story they were uninformed at listing. Fix: split $K$ into $K^{\rm pre}$ (certificate dated before listing), $K^{\rm pend}$ (after), $K=0$ (never matched); recompute $\hat\pi_m,\hat\sigma_{\theta,m},\hat e^*_m$ treating $K^{\rm pend}$ as uninformed.
2. **Old certificates.** Silent holders of valid pre-2021 certificates are informed hiders coded $K=0$ (A.15). They bias $\hat\pi$ down and push $\hat e^*$ toward $\bar\theta$.
3. **$\sigma_1$.** The configs still impose `hider_theta: "impose_zero"`. Under the extension $\sigma_1>0$ is allowed; use registry $\theta$ for hiders (`hider_theta: registry`).

**How much does it matter for the extension? [D]** With $C^D=0$, (E.23) gives the market-level estimator
$$\hat a_\Delta=\frac{R_0-r}{R_0-\hat e^*},\qquad r\equiv\hat\Delta/\hat\beta_1, \tag{E.28}$$
and differentiating,
$$\frac{\partial\hat a_\Delta}{\partial\hat e^*}=\frac{R_0-r}{(R_0-\hat e^*)^2},\qquad \frac{\partial\hat a_\Delta}{\partial R_0}=\frac{r-\hat e^*}{(R_0-\hat e^*)^2}.$$
At the means [E]: apartments $\partial\hat a/\partial\hat e^*=0.07$ and $\partial\hat a/\partial R_0=0.51$; houses $0.63$ and $0.03$.

So **in apartments, an error of 0.1 in $\hat e^*$ moves $\hat a_\Delta$ by 0.007**: the extension's apartment estimate is almost immune to the $K$-timing and old-certificate problems. The reason is economic, not numerical: when attention to silence is low, the composition of the silent pool barely enters prices, so mismeasuring it barely matters. In houses the sensitivity is high (0.06 per 0.1), as in the paper's model, and the $K$ split matters. Conversely, apartments are sensitive to $R_0$ (0.05 per 0.1), which is why Step 3 matters.

The same logic applies to $\hat\pi$ and $\hat\sigma$: they enter the extension's prices only through $\hat e^*$. Where they matter directly is in the hiding side: $F$ is read from $\hat\sigma_\theta$ (§4.7), and non-strategic silence $\nu$ (eq. 4.1) contaminates it.

#### 6.3 Step 3: $R_{0,m}$

$$R_{0,m}=\frac{\bar E_{0,m}}{\bar E_{0,m}-\bar E_{1,m}},$$
from `compute_energy_anchor`. **Preferred: certified kWh$_{ep}$/m² of the matched certificate**, averaged by $\theta$ within market (the paper's text already describes the anchor this way, but the code uses band midpoints; notes open question 14). Two reasons. (a) Midpoints compress within-band variation. (b) The G band is open-ended and uses a 500 kWh placeholder (`src/data_prep.py:424`). [E] On the 45 apartment markets, setting G to 420 / 500 / 600 kWh gives mean $R_0$ = 2.38 / 2.31 / 2.24, $\hat a_\Delta$ = 0.24 / 0.21 / 0.17, and bound violations 20 / 21 / 23 of 45. Houses: $R_0$ = 2.19 / 2.11 / 2.03, $\hat a_\Delta=0.96$ throughout. (Notes A.12 report 2.24→2.06 for 420→600, using pooled registry shares rather than market means; the direction is the same.)

#### 6.4 Step 4: estimate $a_\Delta$

**The estimating equation.** From (E.24), market by market,
$$\hat\lambda_m=(1-a_\Delta)\,x_m+u_m,\qquad x_m\equiv\hat\beta_{1,m}\big(R_{0,m}-\hat e^*_m\big),\qquad \hat\lambda_m=\hat\Delta_m-\hat\beta_{1,m}\hat e^*_m, \tag{E.29}$$
where $u_m$ collects sampling noise in the index DiDs and cross-market heterogeneity in $a_\Delta$. **No constant**: the model says $\hat\lambda=0$ when $\hat\beta_1=0$.

Three estimators, in increasing order of what they ask of the data.

1. **Through-origin OLS** (notes A.12): $1-\hat a_\Delta=\sum_mx_m\hat\lambda_m/\sum_mx_m^2$. Weights markets by $x_m^2$, i.e., by $\hat\beta_{1,m}^2$.
2. **Ratio of means:** $1-\hat a_\Delta=\sum_m\hat\lambda_m/\sum_mx_m$. Weights by $x_m$.
3. **Market-level minimum distance:** $\hat a_{\Delta,m}=1-\hat\lambda_m/x_m$ per market, combined with inverse-variance weights $w_m=1/\widehat{\rm Var}(\hat a_{\Delta,m})$ from a delta method on $(\hat\beta_{1,m},\hat\Delta_m)$. This needs market-level sampling variances and the covariance of $\hat\beta_{1,m}$ and $\hat\Delta_m$, which share the E–G index (positive covariance). It also delivers the homogeneity test $\sum_mw_m(\hat a_{\Delta,m}-\hat a_\Delta)^2\sim\chi^2_{M-1}$. Not yet implementable: per-market standard errors of the index DiDs are not stored.

**Why the choice matters: noise in $\hat\beta_1$ appears on both sides [D].** Write $\hat\beta_1=\beta_1+u$ and $\hat\Delta=\Delta+v$, where $u=u_H-u_L$, $v=u_N-u_L$ are index noises of the three groups (independent, variances $s_H^2,s_L^2,s_N^2$). Then $y=\hat\lambda=\lambda+v-e\,u$ and $x=(\beta_1+u)(R_0-e)$. Because both $u$ and $v$ contain $-u_L$, the noises in $y$ and $x$ are correlated: ${\rm Cov}(u,\,v-eu)=s_L^2-e(s_H^2+s_L^2)$. For through-origin OLS across many markets,
$$\operatorname{plim}\big(1-\hat a_\Delta^{OLS}\big)=(1-a_\Delta)\frac{E\beta_1^2}{E\beta_1^2+s_H^2+s_L^2}+\frac{s_L^2-e(s_H^2+s_L^2)}{(R_0-e)\,(E\beta_1^2+s_H^2+s_L^2)}. \tag{E.30}$$
The first term attenuates $1-a$ toward 0; the second is negative whenever $e>s_L^2/(s_H^2+s_L^2)$ (e.g., $e>1/2$ with equal variances, and $\hat e^*\approx0.59$). Both push **$\hat a_\Delta^{OLS}$ toward 1**, i.e., toward the paper's model. For the ratio of means, numerator and denominator are sums of terms whose noise has mean zero, so $\operatorname{plim}(1-\hat a_\Delta^{\rm ROM})=1-a_\Delta$: no attenuation, no correlation bias. A Monte Carlo (`ext_mc.py`; 45 markets, true $a=0.15$, $E\beta_1=4$, noise s.d. 1–3 per group) gives mean $\hat a^{OLS}=0.29$–$0.36$, matching (E.30), against mean $\hat a^{\rm ROM}=0.14$–$0.15$.

*Recommendation.* Report the **ratio of means** as the main estimate, through-origin OLS as a conservative (pro-full-attention) bound, and the median of market ratios as a robustness check.

**Inference.**
- Markets as independent units: HC1 for OLS; nonparametric bootstrap over markets (4,999 draws) for both estimators. Reported in §7.
- Generated regressors: $\hat e^*_m$ and $R_{0,m}$ come from registry samples that are large (hundreds of thousands of $K=1$ listings), so their sampling error is second order. To include it, bootstrap listings within market for $\hat e^*_m,R_{0,m}$ inside each market draw; this does not require rebuilding the index.
- Spatial dependence: neighbouring markets share shocks. Cluster the bootstrap by `dept` [C].
- **Selection on $\hat\beta_1>0$.** The 45/97 markets were selected on $\hat\beta_{1,m}>0$ (and on the anchor). Selecting on a noisy regressor that shares noise with the outcome biases OLS. The extension's estimator does not need the anchor or $\hat\beta_1>0$: the ratio of means is defined with negative $\hat\beta_1$ too. Re-estimate on all 81 / 114 volume-filtered markets with registry coverage as a robustness check.

#### 6.5 Step 5: reinterpret $\hat\rho$

From (E.22), if the anchor measures the true cost gap ($\beta_1^{\rm anchor}=C_0-C_1$),
$$\hat\rho=\frac{\hat\beta_1}{\beta_1^{\rm anchor}}=\Delta\omega_1=\Delta(\rho\,\alpha_1).$$
**Same number (0.495 apartments, 0.458 houses), new meaning:** the reform-induced increase in the effective mass of buyers who price a *displayed* label. Under reading R1 it is $\rho\alpha_1^{\rm post}$, the post-reform mass. The paper's narrative (04:349, the reform changed "how much a disclosed rating matters to the buyer") fits this exactly. The testable inequality $\hat\rho\le1$ survives as $\Delta\omega_1\le1$. $\rho$ and $\alpha_1$ are not separately identified; their ratio across a dated salience shock (1 January 2022 € display) would be, if $\rho$ does not jump on that date.

#### 6.6 Step 6: $\hat c_0$

Three candidates, with the argument for each.
1. **Raw DiD premium**, $\hat c_{0,m}=\hat\Delta_m$ (8.53 / 3.89). Argument: in Partial Pooling the marginal low type's gain is the silent premium itself (§4.6), in any model.
2. **Model-fitted premium**, $\hat c_{0,m}=\hat\beta_{1,m}\big[R_{0,m}-\hat a_\Delta(R_{0,m}-\hat e^*_m)\big]$ (7.97 / 3.82 with the OLS $\hat a_\Delta$). Argument: it uses the common $\hat a_\Delta$, so market-level noise in $\hat\Delta_m$ is not loaded one-for-one into $\hat c_{0,m}$; it nests the paper's $\hat\beta_1\hat e^*$ at $\hat a_\Delta=1$. **Recommended.**
3. **Post-reform level**, $\hat c_0=D^{\rm post}$ (13.06 / 7.77). Argument: under reading R2 the pre-period gap is part of the mechanism, and the marginal hider's cost is the level. Against: §5.6 shows levels carry a large non-energy component.

**DiD or level.** The case for the DiD is the paper's own identification logic plus §5.6: levels are contaminated, DiDs are not. But be clear about what the DiD reading assumes. With a single $c_0$ invariant across the reform (the paper's 04:349 argument) and Partial Pooling in both periods, $D^{\rm pre}=D^{\rm post}=c_0$ and $\hat\Delta=0$, in **both** models (notes §1.1, Consistency remark). A positive $\hat\Delta$ is coherent only if (a) the pre-period was not in Partial Pooling (for instance $\omega^{\rm pre}\approx0$, reading R1, with pre gaps as nuisance), or (b) $c_0$ moved, Under (a), $\hat c_0=\hat\Delta$ is the post-reform cost. State (a) as the maintained reading.

#### 6.7 Step 7: tests

| Test | Statistic | Model prediction | Result [E] |
|---|---|---|---|
| T-bound | $\hat\Delta_m/\hat\beta_{1,m}\le R_{0,m}$ by market; mean slack $R_0\hat\beta_1-\hat\Delta\ge0$ | holds | apts: mean slack 0.92 ($t=1.0$), 21/45 violate; houses: 8.38 ($t=13$), 8/97 |
| Full attention, houses | $H_0:1-a_\Delta=0$ | not rejected | $0.042/0.040$: $t=1.05$ |
| Full attention, apartments | $H_0:1-a_\Delta=0$ | rejected | OLS $t=7.2$; ROM $0.87/0.126$: $t=6.9$ |
| No attention, apartments | $H_0:a_\Delta=0$ | — | OLS $(0.79-1)/0.11=-1.9$; ROM $-1.0$: not rejected |
| Same $a$ in both segments | $H_0:a^{\rm apt}=a^{\rm house}$ | rejected | OLS difference 0.75, se 0.117, $t=6.4$ |
| Zero intercept | constant in (E.29) | 0 | apts 2.78 (1.85); houses 0.28 (0.79) |
| Sum restriction | coefficients on $\hat\beta_1R_0$ and $\hat\beta_1e$ sum to 1 | 1 | apts 1.41 ($p=0.73$); houses 1.04 ($p=0.88$) |
| Homogeneity of $a$ | $\chi^2_{M-1}$ (needs market s.e.) | — | not yet computable; market $\hat a_{\Delta,m}$: apts median 0.03, IQR $[-0.27,0.58]$ |
| Pass-through | silent price response to a dated shift in pool composition (Jan 2023 expiry) | $\propto a$ | to do (§9, G5) |

The bound violations should be judged against sampling noise: with per-market s.e., count markets where $\hat\Delta_m/\hat\beta_{1,m}$ exceeds $R_{0,m}$ significantly. Violations concentrate where $\hat\beta_1$ is small (67% / 33% / 40% by $\hat\beta_1$ tercile in apartments), but 40% of high-$\hat\beta_1$ apartment markets still violate.

#### 6.8 What is point-identified, normalised, set-identified

**The object the data pin down is $C^*_\Delta$, not $(a_\Delta,C^D)$.** By (E.23), $\hat\Delta/\hat\beta_1=(C_0-C^*_\Delta)/(C_0-C_1)$ with $C^*_\Delta\equiv C^D+a_\Delta(\bar C^N-C^D)$. One ratio per market identifies one number per market: the perceived cost of silence, in kWh units ($C^*_\Delta=\bar E_0-(\hat\Delta/\hat\beta_1)(\bar E_0-\bar E_1)$). Any pair $(a_\Delta,C^D)$ with the same $C^*_\Delta$ fits the same data.

**Why $C^D$ is not separately identified with these moments.** $C^*_\Delta$ is a convex combination of $C^D$ and $\bar C^N$. Raising the default and lowering relative attention can keep it fixed. Across markets, $\hat\Delta_m=(1-a)\hat\beta_{1,m}R_{0,m}+a\,\hat\beta_{1,m}e_m-(1-a)r_D\hat\beta_{1,m}$ would separate them through variation in $R_{0,m}$ and $e_m$ holding $\hat\beta_{1,m}$ fixed. But the three regressors are nearly collinear (correlations 0.99 and 0.94), because $R_0$ and $e$ vary little across markets (s.d. 0.16 and 0.09 in apartments; $\bar C^N$ s.d. 18.5 kWh). The unrestricted three-regressor fit returns $-2.26$ (s.e. 3.98) on the $\hat\beta_{1,m}$ term, whose coefficient is $-(1-a)r_D$: uninformative.

**Identified set [D, E].** Under $C^D\ge0$ and $a_\Delta\in[0,1]$: $C^*_\Delta$ lies between $C^D$ and $\bar C^N$, so
$$C^D\in[0,\,C^*_\Delta],\qquad a_\Delta=\frac{C^*_\Delta-C^D}{\bar C^N-C^D}\in\Big[0,\ \frac{C^*_\Delta}{\bar C^N}\Big].$$
**The normalisation $C^D=0$ gives the upper end of attention to silence.** Any positive default implies even less attention.
- Apartments: $C^*_\Delta=28$ kWh (ratio of means), $\bar C^N=243$: $a_\Delta\in[0,0.12]$, $C^D\in[0,28]$ kWh.
- Houses: $C^*_\Delta=231$ kWh: $a_\Delta\in[0,0.95]$, $C^D\in[0,231]$ kWh. **Houses do not identify full attention**; they identify that silence is priced at roughly the rational pool cost, which is equally consistent with "attentive" and with "inattentive, default near the pool mean". The paper's model is the observationally equivalent description, which is all the extension needs from houses.

**What extra moment would separate $a$ from $C^D$.** A shift in the silent pool's true cost $\bar C^N$ that does not shift attention or the default: the pass-through $\partial C^*/\partial\bar C^N=a$. Candidates: (i) the 1 January 2023 expiry of 2013–17 certificates, which moves the pool's composition on a known date (§9, G5); (ii) the friction easing over 2022–24, with year-specific $\hat e^*_t$; (iii) cross-market variation in $\bar C^N$, which is too small here. **Letter-level indices do not separate them**: (E.10) pins the zero-crossing at $C^*$, the same object, more precisely; they test linearity and the location of $C^*$.

**Summary table.**

| Object | Status | Moment | Key assumption |
|---|---|---|---|
| $\Delta\omega_1=\Delta(\rho\alpha_1)$ | point | $\hat\beta_1/\beta_1^{\rm anchor}$ | anchor = true cost gap |
| $\rho$ vs $\alpha_1$ | not separately | — | — |
| $C^*_\Delta$ (kWh) | point | $\hat\Delta/\hat\beta_1$, $\bar E_\theta$ | linear pricing, stable $e$ (or R1) |
| $a_\Delta$ | point **given** $C^D=0$; else set $[0,C^*_\Delta/\bar C^N]$ | (E.29) | $C^D\ge0$, $a_\Delta\in[0,1]$ |
| $C^D$ | normalised to 0; set $[0,C^*_\Delta]$ | — | — |
| $a^t$ (levels) | not robustly identified | level ratios | level gaps composition-free (fails, §5.6) |
| $c_0$ | point (marginal hider) | $\hat\Delta$ or fitted | Partial Pooling post; reading R1 |
| $F$ | two to seven points | $\hat\sigma_k$ at gains $G_k$ | non-strategic $\nu$ known (needs $K$ split) |
| Salience counterfactual | point, normalisation-free | $\hat\lambda$ | holding $e$, hiding fixed (§8.4) |

---

### 7. Results [E]

All numbers re-run in this session from the repo's data and results files (§12). Estimation sample: the paper's 45 apartment and 97 house markets. Log points.

#### 7.1 Main table

| | Apartments (45) | Houses (97) |
|---|---|---|
| $\hat\beta_1$ / $\hat\Delta$ (DiD, means) | 4.06 / 8.53 | 5.82 / 3.89 |
| $\hat e^*$ | 0.593 | 0.595 |
| $\bar E_1$ / $\bar E_0$ (kWh$_{ep}$/m²/yr, midpoints) | 185 / 327 | 178 / 339 |
| $R_0$ (mean of markets) | 2.31 | 2.11 |
| $\hat\Delta/\hat\beta_1$ (ratio of means) | 2.10 | 0.67 |
| Paper's cap violated ($\hat\Delta_m/\hat\beta_{1,m}>1$) | 37/45 | 33/97 |
| $\bar C^N$ / $C^*_\Delta$ (kWh) | 243 / 28 | 243 / 231 |
| $\hat\lambda$ ($t$) | 6.12 (6.78) | 0.44 (1.10) |
| $\hat a_\Delta$, ratio of means (bootstrap s.e.; 95% CI) | **0.13** (0.13; $[-0.12,0.37]$) | **0.95** (0.05; $[0.86,1.04]$) |
| $\hat a_\Delta$, through-origin OLS (HC1 s.e.) | 0.21 (0.11) | 0.96 (0.04) |
| $\hat a_\Delta$, median of market ratios | 0.03 | 0.96 |
| $\hat a_\Delta$, OLS with intercept | 0.53 (0.24); intercept 2.78 (1.85) | 0.98 (0.08); intercept 0.28 (0.79) |
| Unrestricted: coef. on $\hat\beta_1R_0$ / $\hat\beta_1\hat e^*$ | 0.66 (0.40) / 0.76 (1.57) | 0.03 (0.12) / 1.02 (0.40) |
| Identified set for $a_\Delta$, $C^D\in[0,C^*_\Delta]$ | $[0,\,0.12]$ | $[0,\,0.95]$ |
| Bound slack $R_0\hat\beta_1-\hat\Delta$ (mean, $t$) | 0.92 (1.0) | 8.38 (13.0) |
| Bound violations; by $\hat\beta_1$ tercile | 21/45; 67% / 33% / 40% | 8/97; 22% / 3% / 0% |
| Market $\hat a_{\Delta,m}$: median, IQR | 0.03, $[-0.27,0.58]$ | 0.96, $[0.63,1.27]$ |
| $\hat\rho$ (unchanged number; $=\Delta(\rho\alpha_1)$) | 0.495 | 0.458 |
| $\hat c_0$: paper / fitted / $\hat\Delta$ / level $D^{\rm post}$ | 2.41 / 7.97 / 8.53 / 13.06 | 3.45 / 3.82 / 3.89 / 7.77 |
| High type's hiding gain $G_1=\hat\Delta-\hat\beta_1$ | 4.47 ($>0$ in 82% of mkts) | $-1.93$ |
| $R_0$ with G midpoint 420 / 500 / 600 | 2.38 / 2.31 / 2.24 | 2.19 / 2.11 / 2.03 |
| $\hat a_\Delta$ (OLS) with G 420 / 500 / 600 | 0.24 / 0.21 / 0.17 | 0.96 throughout |

#### 7.2 Honest reading

**What supports the extension.**
1. **One parameter separates the segments.** Every estimator puts apartment attention to silence well below 1 (full attention rejected at $t\approx7$) and house attention near 1 (not rejected). The difference between segments is $t=6.4$.
2. **Apartments respect the extension's bound on average while violating the paper's cap.** 37 of 45 apartment markets have $\hat\Delta_m/\hat\beta_{1,m}>1$, which the paper's model forbids; on average they sit inside $R_0$ (slack 0.92, $t=1.0$).
3. **The model's restrictions hold where they can be tested.** The coefficients on $\hat\beta_1R_0$ and $\hat\beta_1\hat e^*$ sum to one in both segments ($p=0.73$, $0.88$), and the intercept the model excludes is not significant.
4. **The apartment estimate does not depend on the registry belief.** $\partial\hat a_\Delta/\partial\hat e^*=0.07$, so the $K$-timing and old-certificate problems cannot move it materially.
5. **The first-year anomaly of notes A.14.4 disappears on the estimation sample** (§5.7).

**What is fragile.**
1. **The bound binds.** Apartments sit essentially on the bound: $C^*_\Delta=28$ kWh. The extension fits apartments only with a default close to "no energy cost". A default of 30 kWh (about the A-band midpoint) would already require negative attention to silence at the average ratio; it is not statistically rejected (the bound slack has $t=1.0$), but there is essentially no room for a less extreme default. This is a strong assumption with no direct housing evidence yet.
2. **Almost half the apartment markets violate the bound** (21/45), and the violations are not confined to noisy low-$\hat\beta_1$ markets: 40% of high-$\hat\beta_1$ markets violate. Attention is the main story on average but cannot be the whole story everywhere; the residual is where unobserved quality, agency pricing, or cost measurement come back in.
3. **The point estimate depends on the estimator.** 0.03 (median), 0.13 (ratio of means), 0.21 (OLS), 0.53 (OLS with intercept). What is robust is "well below 1 in apartments, near 1 in houses". The level is not.
4. **$R_0$ is measured with band midpoints and a placeholder G value.** Because apartments sit on the bound, the G choice moves violations from 20 to 23 and $\hat a_\Delta$ from 0.24 to 0.17. Certified kWh is needed before the bound test is reported.
5. **Levels do not cooperate** (§5.6). The extension is identified from DiDs only, and the "silence already beat A–D before the reform" fact cannot be turned into a level estimate of $a$.
6. **Market heterogeneity is large.** Market-level $\hat a_{\Delta,m}$ has an IQR of $[-0.27,0.58]$ in apartments. Without per-market standard errors we cannot say how much is noise.
7. **The trajectory evidence is weak.** $\hat\lambda$ rises with $\hat\beta_1$ by construction; the scale-free $1-\hat a_\Delta$ moves only between Y1 and Y2.
8. **$e$ may have moved across the reform** (friction, expiry). The bias formula (E.27) shows this is small in apartments under any reading and zero under reading R1.
9. **Not yet separated from competing stories**: agency overpricing of silent listings, a reform-dated change in the unobserved quality of the silent pool, and non-energy costs of bad letters (rental ban). The gate in §9 is designed for exactly these.

#### 7.3 The first-post-year check

Notes A.14.4 reported, for the window ending July 2022, mean $\hat\Delta=3.1$ against $\hat\beta_1=0.2$ (`post_window_trajectory.csv`). Those means are over all 83 DiD markets, including the many with $\hat\beta_1\le0$ in that window. On the estimation sample (45 markets), the July 2021–June 2022 window gives $\hat\beta_1=1.99$, $\hat\Delta=4.33$, ratio 2.18, below the mean bound 2.31; $\hat\lambda=3.13$ ($t=4.15$); $1-\hat a_\Delta=0.53$ (0.17). Houses: 3.79, 3.13, $\hat\lambda=0.88$ ($t=2.54$). The anomaly does not survive. Caveat: 8 of the 45 apartment markets still have $\hat\beta_1\le0$ in Y1.

---

### 8. Counterfactuals and policy

#### 8.1 The renovation threshold, in both models

The paper defines (main.tex, eq. `eq:threshold`)
$$\bar R\equiv\Pi(d=1,\theta=1)-\Pi(d=0)+c_0,$$
the most an informed low type would pay to renovate and disclose rather than hide. Lemma `lem:threshold_regimes` uses the Partial Pooling indifference $\Pi(d=0)-c_0=\Pi(d=1,\theta=0)$ to get $\bar R^{PP}=\Pi(1,1)-\Pi(1,0)$. That step uses only indifference, so **it holds in the extension too, for any pricing rule.** Under linear pricing, $\Pi$ is the price, and the threshold can be written out in both models.

*Paper ($a=1$).* $p_H-p_N=B-D=B-eB=(1-e)B$, and in Partial Pooling $c_0=D=eB$. So
$$\bar R=(1-e)B+eB=B.$$
*Extension.* $p_H-p_N=B-D$ and $c_0=D$ (§4.4). So
$$\bar R=(B-D)+D=B. \tag{E.31}$$
**The headline minimum subsidy for the marginal seller is unchanged.** The *decomposition* is very different. Apartments, DiD units [E]: in the paper, $\bar R=1.65$ (market premium of verified-high over silence) $+\ 2.41$ (hiding cost avoided) $=4.06$. In the extension, $\bar R=-4.47$ (verifying high quality *loses* 4.47 relative to silence) $+\ 8.53$ (hiding cost avoided) $=4.06$. In the extension the whole private return to renovating comes from no longer having to pay to hide.

Under the exact logit pricing in `src/model.py`, $\Pi(1,1)-\Pi(1,0)$ depends on where displayed valuations sit relative to insensitive ones, which the extension changes through $\alpha_1$ and $C^D$. So "unchanged" is exact under linear pricing and first-order otherwise.

#### 8.2 (removed)

*(Removed at Bastien's request, 2026-10-09: dispersed hiding costs are no longer part of the analysis.)*

#### 8.3 Enforcement counterfactual: forcing informed sellers to display

Set $\sigma_0=\sigma_1=0$ (enforcement makes hiding prohibitively costly; $\pi$ unchanged).
1. **Displayed prices** do not change: $B$ depends only on $\rho\alpha_1$.
2. **The silent pool** becomes purely uninformed, so $e\to\bar\theta$ (by $K\perp\theta$) and $\bar C^N$ falls by $(\bar\theta-e)(C_0-C_1)$. The silent price rises by
$$\rho\alpha_0(\bar\theta-e)(C_0-C_1)=a\,B\,(\bar\theta-e). \tag{E.33}$$
DiD units [E]: apartments $0.21\times4.06\times(0.625-0.593)=0.03$; houses $0.96\times5.82\times0.010=0.06$. Negligible in both, because the silent pool is already mostly uninformed. (Paper's model in apartments: 0.13.)
3. **Former hiders** ($\pi(1-\bar\theta)\sigma_0$ of listings; the paper reports 3.5% of apartment and 1.1% of house listings) now disclose E–G and lose $G_0=D$ each, saving their hiding cost; the buyers of those units pay $D$ less. Under the extension that transfer is $\hat\Delta\approx8.5$ per unit (DiD), against $\hat\beta_1\hat e^*=2.4$ in the paper: enforcement is worth about 3.5 times more per hidden apartment to buyers.
4. **Renovation:** with hiding off the table, every informed low type faces $\bar R=B$, and the hide-after-renovate leak of §8.2 closes.

#### 8.4 Salience counterfactual: making silence as salient as a label

Raise attention to silence until the reform's attention shock reaches silent listings as fully as displayed ones: $a_\Delta\to1$. By (E.23), at $a_\Delta=1$ the $r_D$ term drops out and $\hat\Delta^{\rm cf}=\hat\beta_1e$, **whatever $C^D$ is**. So
$$\hat\Delta^{\rm cf}-\hat\Delta=-\hat\lambda. \tag{E.34}$$
**This counterfactual is identified without the normalisation**: $-6.1$ log points on the silent DiD premium in apartments, $-0.4$ in houses, holding $e$ and hiding fixed. Second-round effects: $G_0$ falls by $\hat\lambda$, so $\sigma_0$ falls, the pool improves and $e$ rises slightly, which raises the silent price by $\rho\alpha_0(C_0-C_1)\Delta e$; small.

**The silence mark-up borne by buyers.** In levels, a silent listing sells above what a fully attentive market would pay by
$$p_N-(\Lambda-\rho\bar C^N)=\rho(1-\alpha_0)(\bar C^N-C^D). \tag{E.35}$$
Its level needs $\rho$ and $\alpha_0$ separately, which are not identified. Under reading R1 and full attention to displayed labels ($\alpha_1=1$), its post-reform value is $\omega_1(1-a)\bar C^N=(1-a)\hat\beta_1(R_0-e)=\hat\lambda$: about 6 log points per silent apartment sale [E, conditional on those two assumptions].

**Instruments [C].** (i) A mandatory, prominently placed "DPE: non communiqué" field, so that silence is displayed rather than absent (raises $\alpha_0$). (ii) Platform defaults: whether SeLoger's DPE filter excludes listings without a DPE (notes, open question (d)). (iii) A regulatory default class for silent listings (e.g., "treated as G"), which sets $C^D$ high and makes silence unprofitable for every informed type. Its cost falls on genuinely uninformed sellers waiting for a certificate, who would then delay listing; with certification friction (A6) that is a real trade-off.

#### 8.5 Code: what must change before any counterfactual is computed

`src/model.py` hard-codes full attention:
- `ValuationParams.v1_hidden(e)` (`src/model.py:124`) returns $\beta_0+\beta_1e+X'\beta$;
- the hiding gain $\Delta(e)=\rho\beta_1e$ (`src/model.py:501`);
- `solve_equilibrium` (`:390`) and `renovation_threshold` (`:531`) call `v1_hidden(eq.e_star)`.

The minimal change is to replace $e$ by the effective belief $\tilde e=a\,e+(1-a)(R_0-r_D)$ (E.11') wherever silent valuations are computed, allow $\tilde e>1$ (anything that clips beliefs to $[0,1]$ must not apply to $\tilde e$), carry $a$ and $R_{0,m}$ per market, scale the belief feedback in `solve_equilibrium` by $a$, and allow $\sigma_1>0$. Feeding the extension's $\hat c_0$ into the current solver would mix two models. (Not done; repo untouched.)

---

### 9. Gate: checks before the extension goes into the paper

Ordered by how decisive and how cheap. For each: what to run, what would support the extension, what would kill it.

| # | Check | What to run | Supports the extension | Kills it (or forces a different term) |
|---|---|---|---|---|
| **G1** | **Within-agency comparison** | Re-pull `realtor_ref` (in the source SQL, `data/collect_listings.py:98–105`, not in saved files). Listing-level regression of log price on group dummies with agency × market × month FE and the index's hedonic controls; also its reform DiD. | The silent-minus-A–D gap and its DiD survive within agency (say, at least half the index value). | The gap vanishes within agency: the premium is agency composition (an agency-level $\xi$) or agency pricing (overpricing to win mandates). Attention is then not needed. |
| **G2** | **$K$ split by certificate date, and old certificates** | Save `date_reception_dpe`; code $K^{\rm pre}$ / $K^{\rm pend}$ / never matched. Recompute $\hat\pi,\hat\sigma_\theta,\hat e^*$ treating $K^{\rm pend}$ as uninformed; estimate $\nu$ (eq. 4.1); size the $d=1,K=0$ old-certificate group by certificate age if available. | Apartment $\hat a_\Delta$ moves by less than about 0.01 (predicted by $\partial\hat a/\partial\hat e^*=0.07$). Silent listings with $K^{\rm pend}$ price like other silent listings given $X$ (buyers cannot see $K$). Net of $\nu$, $\sigma_1>0$ in apartments and $\approx0$ in houses. | The silent premium is carried by $K^{\rm pend}$ listings: selection on unobserved quality through $K$ (notes §1.2, $\kappa$), not attention. |
| **G3** | **Certified kWh for $R_0$** | Re-pull certified kWh$_{ep}$/m² for matched certificates; recompute $\bar E_\theta$, $R_{0,m}$, the bound test with per-market s.e., and $\hat a_\Delta$. | Mean slack stays $\ge0$; significant violations are few and concentrated in low-$\hat\beta_1$ markets; $\hat a_\Delta$ stable. | Mean $\hat\Delta/\hat\beta_1$ significantly above mean $R_0$: attention with a non-negative default is rejected for apartments. |
| **G4** | **New- vs old-method green premium (opposability)** | Post-period cross-section: A–D vs E–G premium among $d=1,K=1$ with listing letter = registry letter (new method) versus $d=1,K=0$ (old method). | New-method premium larger: displayed, opposable labels draw more attention; consistent with $\hat\rho=\Delta(\rho\alpha_1)$. | Equal premiums: the reform's price effect is not about attention to displayed, opposable labels; the reinterpretation of $\hat\rho$ (and the paper's demand-side channel) is in question. Caveat: $K=0$ disclosers also include failed matches of new certificates. |
| **G5** | **1 January 2023 expiry break** [CHECK date] | Monthly event study around 2023-01 of: silent share, $K^{\rm pend}$ share, $p_N-p_H$, and $\hat e^*_t$. | Silent share and $K^{\rm pend}$ jump (friction); in apartments $p_N-p_H$ does **not** move with the pool's composition (pass-through $\approx a\approx0$); in houses it moves in proportion to $\Delta\bar C^N$. This is the moment that separates $a$ from $C^D$ (§6.8). | Apartment silent prices move one-for-one with the pool's composition: attention to silence is high, and the premium must come from elsewhere. |
| **G6** | **First-year window on the estimation sample** | Done (§7.3). Remaining: year-specific $\hat e^*_t,\hat\pi_t,R_{0,t}$. | Done: the A.14.4 anomaly does not survive. | — |
| **G7** | **Level comparability of the indices** | Check in the Chapter-1 index code whether each EPC group's index is evaluated at a common reference $X$ within market. | Common reference: the level nuisance of §5.6 is unobserved quality between groups; the DiD-based extension is unaffected. | No common reference: the level facts ("silence above A–D before the reform", 03:129) include observable composition. The extension survives (it uses DiDs); the introduction's level narrative must be reworded. |
| **G8** | **Letter-level gaps to silence** | Indices by letter (at least ABC / D / E / FG); regress the DiD of $p_k-p_N$ on $C_k$ (E.10). | Linear, slope $-\rho\alpha_1$, zero-crossing near $C^*_\Delta\approx28$ kWh: silence above every letter, including A/B/C. | Crossing near $\bar C^N\approx243$ kWh (between D and E): belief model. Strong non-linearity at letter thresholds: letter salience (notes §1.3 (iii)), which also biases $\hat\rho$. |
| **G9** | **Asking vs transaction prices; time on market** | Match to DVF transactions or use listing end dates and price revisions. | Premium survives in transaction prices; (with attention *shares*) silent listings may sell more slowly at a higher price (§3.6). | Premium vanishes at transaction, with more price cuts on silent listings: seller-side (agency) list pricing. |
| **G10** | **1 January 2022 € display** | Event study of $B$ and $p_N-p_H$ around 2022-01. | $B$ jumps ($\alpha_1$ up), and $p_N-p_H$ rises with it (silence gains on displays). | No change in either: the displayed euro bill does not move attention, weakening the display-triggered mechanism. |

**Decision rule.** Put the extension in the paper as the explanation of the apartment wedge if G1, G2 and G3 support it. If G1 kills it, the apartment wedge is agency composition or pricing, and the paper should say so instead. If G2 kills it, the right extension is the $\kappa$ term of notes §1.2–1.6 (selection on unobserved quality through $K$), not attention. G4–G10 sharpen the interpretation but do not decide inclusion.

---

### 10. Draft LaTeX for the paper

> **DRAFT. Do not paste before the gate checks G1–G3.** Numbers marked `[XX]` must be recomputed after G2 (certificate timing) and G3 (certified kWh). Keys marked `% [CHECK: not in DPE_library.bib]` must be added and verified. Notation follows `sections/04-structural-draft.tex`. Environments follow the file (`assumption`, `proposition`, `corollary`, `lemma`). Prose is a first draft for Bastien to rewrite, not text to ship.

#### 10.1 Main-text subsection

```latex
\subsection{Limited Attention to Silence}
\label{ss:attention}

The apartment wedge has a specific shape. It is not that silent listings sell
slightly above what the registry-measured pool would justify. In 37 of 45 apartment
markets the reform raised the price of silence, relative to an E--G rating, by more than
it raised the price of a verified A--D rating, $\hat\Delta_m>\hat\beta_{1,m}$; and in
levels, silent apartments sell above verified A--D ones in [XX] of 45 markets. % [42/45 before gate G7]
No belief about a binary $\theta$ can produce that, because a belief lies between the
worst and the best rating. This subsection shows that one change on the buyer side,
attention to energy that depends on whether a rating is displayed, does produce it,
nests the model above, and turns the over-identifying wedge into an estimate.

\paragraph{Energy as a displayed cost.}
Write the energy component of a dwelling's value as a capitalised cost $C_\theta$,
with $C_0>C_1\ge0$ and $\beta_1=C_0-C_1$; the valuation in
Section~\ref{ss:model_setup} is the special case in which an EPC-sensitive buyer always
subtracts her expected cost. Instead, let a sensitive buyer attend to energy with
probability $\alpha_1$ when a rating is displayed and $\alpha_0$ when none is.

\begin{assumption}[Display-triggered attention]\label{ass:attention}
$0\le\alpha_0\le\alpha_1\le1$. An attentive buyer subtracts $C_\theta$ after disclosure
and $\bar C^N\equiv e\,C_1+(1-e)\,C_0$ after silence. An inattentive buyer subtracts a
default $C^D\ge0$, normalised to zero in estimation.
\end{assumption}

\noindent The assumption follows the evidence that costs which are not displayed are
under-weighted, toward zero rather than toward their mean
\citep{chetty_salience_2009,finkelstein_ez_2009,brown_shrouded_2010}, % [CHECK: not in DPE_library.bib]
and that consumers under-weight energy costs specifically
\citep{allcott_is_2012,houde_consumers_2014}. % [CHECK: houde key is the 2014 WP; published RAND JE 2018]
Write $a\equiv\alpha_0/\alpha_1$ for the attention a silent listing receives relative to
a displayed one, and $C^*\equiv C^D+a(\bar C^N-C^D)$ for the cost buyers act as if a
silent listing carries. Prices then satisfy
\begin{equation}
  B\equiv p_H-p_L=\rho\alpha_1(C_0-C_1),\qquad
  D\equiv p_N-p_L=\rho\alpha_1(C_0-C^*),
  \label{eq:att_prices}
\end{equation}
so that every displayed rating $k$ sits at $p_k-p_N=-\rho\alpha_1(C_k-C^*)$.

\begin{proposition}[Silence above verified efficiency]\label{prop:att_silence}
\begin{enumerate}[label=(\roman*)]
  \item If $a=1$, then $D=e\,B$ for any $\alpha_1$ and $C^D$: the model of
        Section~\ref{sec:equilibrium}.
  \item $p_N>p_H$ if and only if $a<(C_1-C^D)/(\bar C^N-C^D)$. A necessary condition is
        $C^D<C_1$: the default must be below the average certified A--D cost.
  \item $D/B\le R_0\equiv C_0/(C_0-C_1)$, with equality iff $a=0$ and $C^D=0$.
\end{enumerate}
\end{proposition}

\noindent\textit{Proof.} See Appendix~\ref{app:attention}. $\Box$

\noindent Part~(ii) states what the mechanism requires. Inattention alone is not
enough; a buyer who ignores energy but implicitly assumes an average dwelling behaves
like a cursed buyer and cannot price silence above a verified rating. The default must
be optimistic. Part~(iii) gives the price of that requirement: silence can be priced as
if it carried no energy cost, but not better, so the ratio of the two premiums is bounded
by a number the registry measures, $R_{0,m}=\bar E_{0,m}/(\bar E_{0,m}-\bar E_{1,m})$.

\paragraph{The reform.}
Our estimands are differences across July~2021. Let the effective attention mass
$\omega_j=\rho\alpha_j$ change with the reform, and hold costs and the pool belief fixed.
Then $\hat\beta_{1,m}=\Delta\omega_1(C_0-C_1)$, so the anchored $\hat\rho_m$ measures the
reform-induced increase in attention to \emph{displayed} ratings, and
\begin{equation}
  \hat\lambda_m\;=\;\hat\Delta_m-\hat\beta_{1,m}\hat e^*_m
  \;=\;(1-a_\Delta)\,\hat\beta_{1,m}\,\big(R_{0,m}-\hat e^*_m\big),
  \qquad a_\Delta\equiv\frac{\Delta\omega_0}{\Delta\omega_1}.
  \label{eq:att_lambda}
\end{equation}
The wedge is the part of the reform's price effect that silent listings escaped:
had the new attention reached them as fully as displayed ratings, $\hat\lambda_m$ would
be zero. $a_\Delta$ equals relative attention $a$ when $a$ is stable across the reform,
or when ratings were not priced before it.

\paragraph{Estimates.}
Estimating~\eqref{eq:att_lambda} across markets by the ratio of means gives
$\hat a_\Delta=[XX]$ for apartments (bootstrap s.e.\ [XX]) and $[XX]$ for houses ([XX]).
Full attention to silence is rejected for apartments ($t=[XX]$) and not for houses
($t=[XX]$). The silent apartment is priced as if it consumed $[XX]$~kWh per square metre
per year, better than the A~band, while the silent house is priced at $[XX]$~kWh, close
to the $[XX]$~kWh the registry assigns to the silent pool. On average, apartment markets
satisfy the bound of Proposition~\ref{prop:att_silence}(iii) (mean slack $[XX]$ log
points), but $[XX]$ of 45 markets exceed it, which attention alone cannot explain.
Because the bound binds, the normalisation $C^D=0$ is not innocuous: the data identify
the perceived cost of silence, and a positive default would imply even less attention
than reported.

\paragraph{What changes, and what does not.}
Three objects keep their values. The anchored $\hat\rho_m$ is unchanged as a number.
The marginal informed seller's renovation threshold remains the verified-quality premium,
$\bar R=B$, because the hiding cost and the silence premium still cancel at the margin
(Lemma~\ref{lem:threshold_regimes}). Houses, where $\hat a_\Delta$ is close to one, keep
every estimate of Section~\ref{sec:results}. Two objects change for apartments. The
concealment cost becomes the fitted silence premium, $[XX]$ log points rather than
$[XX]$, which under delegated disclosure is the agency's expected sanction divided by
its commission share. And the private return to renovation at sale accrues only to
sellers who disclose, so display enforcement and renovation subsidies are complements.
```

#### 10.2 Appendix block

```latex
\section{Limited Attention to Silence: Proofs}
\label{app:attention}

\paragraph{Prices.}
A sensitive buyer's valuation is $V(X)-\mathcal{D}$, with $\mathcal{D}=C_k$ if she is
attentive and rating $k$ is displayed, $\mathcal{D}=\bar C^N=eC_1+(1-e)C_0$ if she is
attentive and the listing is silent, and $\mathcal{D}=C^D$ if she is inattentive. An
insensitive buyer values every listing at $V(X)-C^{\mathrm{ins}}$. With prices equal to
the share-weighted mean valuation,
\[
  p_k=\Lambda-\rho\big[\alpha_1C_k+(1-\alpha_1)C^D\big],\qquad
  p_N=\Lambda-\rho\big[\alpha_0\bar C^N+(1-\alpha_0)C^D\big],
\]
with $\Lambda=V(X)-(1-\rho)C^{\mathrm{ins}}$. Hence $B=\rho\alpha_1(C_0-C_1)$ and
$D=\rho[\alpha_1(C_0-C^D)-\alpha_0(\bar C^N-C^D)]=\rho\alpha_1(C_0-C^*)$ with
$C^*=C^D+a(\bar C^N-C^D)$, and $p_k-p_N=-\rho\alpha_1(C_k-C^*)$.

\begin{proof}[Proof of Proposition~\ref{prop:att_silence}]
(i) If $a=1$, $C^*=\bar C^N$ and $D=\rho\alpha_1(C_0-\bar C^N)=\rho\alpha_1e(C_0-C_1)=eB$.
(ii) $p_N-p_H=\rho\alpha_1(C_1-C^*)>0$ iff $C^*<C_1$ iff
$a(\bar C^N-C^D)<C_1-C^D$. Since $C^*$ is a convex combination of $C^D$ and
$\bar C^N\ge C_1$, $C^*<C_1$ requires $C^D<C_1$.
(iii) $D/B=(C_0-C^*)/(C_0-C_1)=R_0-C^*/(C_0-C_1)$, and $C^*\ge0$ when $C^D\ge0$.
Equality requires $C^*=0$, i.e.\ $C^D=0$ and $a=0$.
\end{proof}

\begin{lemma}[The wedge under the reform]\label{lem:att_did}
Let $\omega_j^t=\rho^t\alpha_j^t$ for $t\in\{\mathrm{pre},\mathrm{post}\}$, with $C_0$,
$C_1$, $C^D$ and $e$ fixed. Then $\hat\beta_1=\Delta\omega_1(C_0-C_1)$ and
\[
  \frac{\hat\Delta}{\hat\beta_1}=R_0-a_\Delta(R_0-e)-(1-a_\Delta)\frac{C^D}{C_0-C_1},
  \qquad a_\Delta=\frac{\Delta\omega_0}{\Delta\omega_1}
  =a^{\mathrm{post}}+\big(a^{\mathrm{post}}-a^{\mathrm{pre}}\big)
   \frac{\omega_1^{\mathrm{pre}}}{\Delta\omega_1}.
\]
With $C^D=0$, $\hat\Delta-\hat\beta_1e=(1-a_\Delta)\hat\beta_1(R_0-e)
=(\Delta\omega_1-\Delta\omega_0)\bar C^N$. If instead $e$ changes from
$e^{\mathrm{pre}}$ to $e^{\mathrm{post}}$, the wedge gains the term
$\omega_0^{\mathrm{pre}}(e^{\mathrm{post}}-e^{\mathrm{pre}})(C_0-C_1)$.
\end{lemma}

\begin{proof}
Difference $B^t=\omega_1^t(C_0-C_1)$ and
$D^t=\omega_1^t(C_0-C^D)-\omega_0^t(\bar C^N-C^D)$ across periods and divide; use
$(\bar C^N-C^D)/(C_0-C_1)=R_0-e-C^D/(C_0-C_1)$. The expression for $a_\Delta$ follows
from $\omega_0^t=a^t\omega_1^t$ by adding and subtracting $a^{\mathrm{post}}
\omega_1^{\mathrm{pre}}$. For changing $e$, add and subtract
$\omega_0^{\mathrm{pre}}\bar C^N_{\mathrm{post}}$ and use
$\bar C^N_{\mathrm{post}}-\bar C^N_{\mathrm{pre}}=-(e^{\mathrm{post}}-e^{\mathrm{pre}})(C_0-C_1)$.
\end{proof}

\begin{proposition}[Equilibrium with a common hiding cost]\label{prop:att_regimes}
With a common cost $c_0$, the gain from hiding of an informed low-quality seller,
$G_0(\sigma_0)=\rho\alpha_1(C_0-C^D)-\rho\alpha_0(\bar C^N(\sigma_0)-C^D)$, is weakly
decreasing in $\sigma_0$, strictly if $\alpha_0>0$. The regimes of
Proposition~\ref{prop:equilibrium} obtain with $\Delta(e)$ replaced by $G_0$; in
Partial Pooling $D=c_0$; the Partial Pooling interval has width
$a\,B\,(\bar\theta-e(1))$; and $\sigma_1^*=0$ whenever $\sigma_0^*<1$.
\end{proposition}

\begin{proof}
$\partial G_0/\partial\sigma_0=\rho\alpha_0(C_0-C_1)\,\partial e/\partial\sigma_0\le0$ by
Lemma~\ref{lem:belief_monotone}. The regimes follow as in the proof of
Proposition~\ref{prop:equilibrium}. In Partial Pooling, $D=p_N-p_L=G_0(\sigma_0^*)=c_0$.
The width is $G_0(0)-G_0(1)=\rho\alpha_0(C_0-C_1)(\bar\theta-e(1))=aB(\bar\theta-e(1))$.
If $\sigma_0^*<1$ then $G_0\le c_0$, and $G_1=G_0-B<c_0\le c_0+c_1$.
\end{proof}

```

---

### 11. Literature map

Only references verified earlier (notes §1.7 and the A.11 Crossref check), plus two flagged [CHECK]. "Key" is the `paper/DPE_library.bib` key where one exists; everything else must be added. For each: what it gives this extension, and how the extension differs.

**Salience of non-displayed and shrouded costs** (the evidence behind E-A3/E-A4)
- **Chetty, Looney & Kroft (2009, AER).** Demand under-reacts to sales taxes not included in posted prices. *Gives:* the template "a cost that is not displayed is under-weighted toward zero, not toward its mean" (§1.4). *Differs:* here whether the cost is displayed is a strategic choice of the seller, so attention interacts with the disclosure game.
- **Finkelstein (2009, QJE).** Electronic toll collection lowers the salience of tolls and raises toll rates. *Gives:* salience depends on the display technology, as the 2021 reform and the 2022 € display change $\alpha_1$. *Differs:* we identify relative attention across display states within a market, not a level.
- **Gabaix & Laibson (2006, QJE).** Firms may not unshroud add-on prices when some consumers are myopic. *Gives:* the equilibrium logic for why silence persists when buyers do not price it. *Differs:* disclosure is mandatory here and non-compliance is costly; shrouding is the absence of a mandated label.
- **Ellison (2005, QJE).** Add-on pricing when consumers ignore add-ons. *Gives:* the welfare reading of a price component buyers do not consider. *Differs:* same as above.
- **Brown, Hossain & Morgan (2010, QJE).** Shrouded shipping fees on eBay raise revenue. *Gives:* field evidence that buyers under-weight a hidden cost, the closest analogue to $C^D\approx0$. *Differs:* stakes are large in housing, and the hidden attribute's true distribution is observed through the registry.

**Models of attention** (the micro-foundations)
- **Gabaix (2014, QJE; 2019, Handbook of Behavioral Economics).** Sparsity: attention weight $m$ and a default value. *Gives:* the representative form ($m=\alpha_0$) and the name and role of $C^D$. *Differs:* we estimate a *relative* weight from a reform DiD, with an external cost anchor pinning the scale.
- **Kőszegi & Szeidl (2013, QJE).** Focusing on attributes that vary in the choice set. *Gives:* why a displayed letter raises attention to energy ($\alpha_1>\alpha_0$). *Differs:* variation in focus is created by a seller's disclosure decision.
- **Bordalo, Gennaioli & Shleifer (2013, JPE).** Salience distorts weights toward salient attributes. *Gives:* the "anchoring on a bad letter" reading, which the notes show is capped because it moves $p_L$ only. *Differs:* our mechanism is about the absent attribute, not the salient one.
- **Enke (2020, QJE).** "What you see is all there is": neglect of unseen information. *Gives:* the psychological basis for treating absence as "nothing to worry about". *Differs:* Enke's agents neglect unseen signals in belief formation; ours drop the cost dimension, so the deduction is a default, not a belief.
- **Sims (2003, JME); Matějka & McKay (2015, AER).** Rational inattention, and its logit representation. *Gives:* a foundation for $\alpha_0<\alpha_1$ (processing a missing field is costlier) and a link to the logit pricing in `src/model.py`. *Differs:* we do not derive $\alpha$ from information costs.

**Disclosure with inattentive or naive receivers**
- **Hirshleifer & Teoh (2003, JAE).** Limited attention changes how disclosed versus undisclosed information is priced, and firms choose presentation. *Gives:* the closest conceptual precedent. *Differs:* a mandated label, delegated disclosure, and a registry that measures the hidden quality, which makes relative attention estimable.
- **Fishman & Hagerty (2003, JLEO)** (key `fishman_mandatory_2003`). Mandatory versus voluntary disclosure when some customers cannot interpret disclosures. *Gives:* the case that mandates help only if buyers use the information. *Differs:* our buyers can read labels; they fail to price their absence.
- **DellaVigna & Pollet (2009, JF).** Investors under-react to earnings news released on Fridays. *Gives:* evidence that attention to disclosed information varies with context. *Differs:* attention here varies with whether anything is disclosed.
- **Jin, Luca & Martin (2021, AEJ: Micro).** Receivers are insufficiently skeptical of non-disclosure. *Gives:* the inference-side alternative. *Differs:* any belief-based under-skepticism is capped at $D\le B$ (notes Prop. 4) and is nearly irrelevant in a mostly uninformed pool.
- **Hagenbach & Saucet (2025, REStud).** Motivated skepticism, with beliefs constrained to be consistent with the message. *Gives:* a second inference-side alternative. *Differs:* capped by the same argument.
- **Hagenbach & Koessler (2017, RED).** Naive receivers play the prior after non-disclosure. *Gives:* the cursed benchmark (default = prior mean), which Corollary E2a shows cannot produce the premium.

**Energy-cost inattention and EPCs**
- **Allcott (2011, AER P&P)** [CHECK: confirm which Allcott 2011 was verified]. Consumers misperceive energy costs. *Gives:* direct evidence that energy costs are mis-weighted. *Differs:* durables, no strategic disclosure.
- **Allcott & Greenstone (2012, JEP)** (key `allcott_is_2012`). The energy-efficiency gap and inattention as one source. *Gives:* the framework the paper's anchor already uses (truncated horizon). *Differs:* we separate attention to displayed and undisplayed costs.
- **Sallee (2014)** [CHECK venue: J. Law & Econ.]. Rational inattention to energy efficiency when the stakes are small relative to processing costs. *Gives:* why attention to an absent label could be low. *Differs:* housing stakes are large; the inattention we find is state-contingent.
- **Allcott & Taubinsky (2015, AER).** Information and attention in the lightbulb market. *Gives:* evidence that information provision moves willingness to pay for efficiency, modestly. *Differs:* we study the *absence* of information.
- **Houde (2018, RAND)** (bib has the working-paper version, key `houde_consumers_2014`; update to the published title). Consumers respond to the Energy Star label, some ignoring energy costs. *Gives:* the closest analogue to display-triggered attention: a label as an attention device. *Differs:* letters rather than a binary label, and strategic non-display.
- **Myers, Puller & West (2022, AEJ: Policy)** (key `myers_mandatory_2022`). Mandatory disclosure raises the capitalisation of efficiency in Austin housing. *Gives:* evidence that display raises $\alpha_1$. *Differs:* no registry of non-disclosers' true quality, so silence cannot be priced against its rational value.

**Disclosure theory the extension nests**
- **Dye (1985, JAR)** (`dye_disclosure_1985`); **Jung & Kwon (1988, JAR)** (`jung_kwon_1988`). Uninformed senders keep silence partially informative. *Gives:* the paper's pool structure, unchanged. *Differs:* the pool's composition matters for prices only with weight $a$.
- **Milgrom (1981, Bell)** (`milgrom_good_1981`); **Grossman (1981, JLE)** (`grossman_informational_1981`). Unraveling. *Gives:* the benchmark. *Differs:* the force of unraveling (the belief penalty on silence) is scaled by $a$, which is why it is weak in apartments.

**Agency incentives (competing explanation and the delegated-disclosure reading)**
- **Levitt & Syverson (2008, REStat)** (key `levitt_syverson_2008` is in the bib; brief marked it [CHECK]). Agents' incentives distort sale outcomes. *Gives:* the basis for $c_0\approx k/\tau$, and the alternative that agencies overprice silent listings. *Differs:* we model the disclosure margin, not the sale-timing margin.
- **Rutherford, Springer & Yavas (2005, JFE)** [CHECK]. Principal-agent conflicts in residential brokerage. *Gives:* same. Not in the bib.

---

### 12. Glossary of every number used

"Verified" = recomputed in this session by the named script, run from the repo root, read-only. "Read" = taken from a file, not recomputed.

| Number(s) | Meaning | Source | Verified? |
|---|---|---|---|
| 45 / 97 | estimation-sample markets (apts / houses) | `results/<type>/anchored_diagnostics.csv` | verified |
| 4.06 / 8.53; 5.82 / 3.89 | mean $\hat\beta_1$ / $\hat\Delta$ | `attention_check.py`, `levels.py`, `ext_checks.py` (matches file to $10^{-16}$) | verified |
| 1.69 / 6.92; 5.07 / 3.41 | same, all 81 / 114 volume-filtered markets | `levels.py` | verified |
| 0.593 / 0.595 | mean $\hat e^*$ | `attention_check.py` | verified |
| 185 / 327; 178 / 339 | mean $\bar E_1$ / $\bar E_0$ (kWh, midpoints, $K=1$, 2022–24) | `compute_energy_anchor` via `attention_check.py` | verified |
| 2.31 / 2.11 | mean $R_0$ (2.30 / 2.10 at means) | `attention_check.py`, `ext_checks.py` | verified |
| 243 / 243 | $\bar C^N$ at means (kWh) | `ext_checks.py` | verified |
| 0.761 / 0.731 | $C_1/\bar C^N$ (threshold for $D>B$ with $C^D=0$) | `ext_checks.py` | verified |
| 28 / 231 | $C^*_\Delta$ (kWh), ratio of means; per-market medians 8 / 233 | `ext_checks3.py` | verified |
| 2.10 / 0.67 | $\hat\Delta/\hat\beta_1$ (ratio of means) | `ext_checks3.py` | verified |
| 6.12 ($t$ 6.78) / 0.44 ($t$ 1.10) | $\hat\lambda$ | `attention_bound.py`, `ext_checks.py` | verified |
| 0.495 / 0.458 | mean $\hat\rho$ (ratio of means 0.451 / 0.446) | `attention_check.py`, `ext_checks3.py` | verified |
| 2.41 / 3.45 | paper's $\hat c_0=\hat\beta_1\hat e^*$ | `ext_checks3.py` | verified |
| 7.97 / 3.82 | fitted $\hat c_0$ (extension, OLS $\hat a$) | `ext_checks3.py` | verified |
| 0.507, 0.625, 0.152 / 0.419, 0.605, 0.068 | $\hat\pi$, $\hat{\bar\theta}$, $\hat\sigma_0$ | `ext_checks.py` (means of the diagnostics file) | verified |
| 0.790 (0.110) → 0.21; 0.042 (0.040) → 0.96 | through-origin OLS $1-\hat a_\Delta$ (HC1) | `attention_check.py`, `ext_checks.py` | verified |
| boot s.e. 0.109 / 0.040; CI [0.571, 1.000] / [−0.035, 0.123] | bootstrap for OLS $1-\hat a$ (4,999 draws, seed 12345) | `ext_checks.py` | verified |
| 0.870 (0.126) → 0.13; 0.050 (0.046) → 0.95 | ratio-of-means $1-\hat a_\Delta$; CIs [0.627, 1.121] / [−0.038, 0.142] | `ext_checks.py` | verified |
| 0.97 → 0.03; 0.04 → 0.96 | median market ratio | `ext_checks.py` | verified |
| market $\hat a_m$: 0.03, IQR [−0.27, 0.58]; 0.96, [0.63, 1.27] | market-level spillover estimates | `ext_checks.py` | verified |
| 0.47 (0.24), intercept 2.78 (1.85); 0.02 (0.08), 0.28 (0.79) | $1-\hat a_\Delta$ with intercept | `ext_checks2.py` | verified |
| 0.66 (0.40) / 0.76 (1.57), sum 1.41 $p$=0.73; 0.03 (0.12) / 1.02 (0.40), 1.04 $p$=0.88 | unrestricted regression | `attention_check.py` | verified |
| 0.92 ($t$ 1.01), median 0.37; 8.38 ($t$ 12.99) | bound slack | `attention_bound.py` | verified |
| 21/45 (67/33/40%); 8/97 (22/3/0%) | bound violations, by $\hat\beta_1$ tercile | `attention_check.py`, `attention_bound.py` | verified |
| 37/45; 33/97 | $\hat\Delta_m/\hat\beta_{1,m}>1$ | `attention_check.py` | verified |
| 82%; 4.47 / −1.93 | share with $\hat\Delta>\hat\beta_1$; mean $\hat\Delta-\hat\beta_1$ | `ext_checks3.py` | verified |
| 2.38/2.31/2.24, $\hat a$ 0.24/0.21/0.17, viol. 20/21/23; 2.19/2.11/2.03, 0.96, 8/8/10 | G midpoint 420/500/600 | `ext_checks.py` | verified |
| 2.24 → 2.06 | G 420→600, pooled registry shares | notes A.12 | read, not re-run |
| 1.97 / 4.54, 6.03 / 13.06; 7.48 / 3.88, 13.30 / 7.77 | level $B$/$D$ pre / post | `levels.py`, `ext_checks.py` | verified |
| 84% / 93%; 40% / 34% | share of markets with $D>B$ pre / post | `ext_checks.py` | verified |
| $a$ ratio-of-means 0.01 / 0.09; regression 0.83 / 0.80 | level-based $a$ (apartments) pre / post | `ext_checks.py` | verified |
| slope 0.93 (0.10), intercept 2.70 (4.66) pre; 0.92 (0.11), 7.52 (4.68) post | level $D=k+sB$, apartments | `ext_checks2.py` | verified |
| s.d. 28.9 / 41.7 (pre), 29.2 / 43.1 (post) | cross-market s.d. of level $B$, $D$ (apts) | `ext_checks2.py` | verified |
| 0.28 (0.19) / 0.23 (0.18); $a$ 1.20 / 1.16 | houses level slope; level regression $a$ | `ext_checks.py`, `ext_checks2.py` | verified |
| Y1/Y2/Y3 table (§5.7) | year-specific DiDs, estimation sample | `ext_checks.py` | verified |
| 0.22 / 3.08 (83 mkts) | first-window means, all DiD markets | `quality_reports/diagnostics/rho-anchor-dynamics/post_window_trajectory.csv` | read |
| 3.9 / 5.5 / 6.0; 1.1 / 0.6 / 0.4 | cumulative-window $\hat\lambda$ (anchored markets) | same csv | read |
| 0.989, 0.940; s.d. $R_0$ 0.16, $e$ 0.09, $\bar C^N$ 18.5 kWh (apts; houses 0.13, 0.10, 26.5) | collinearity in the $C^D$-free regression | `ext_checks3.py` | verified |
| −2.26 (3.98) | coefficient on $\hat\beta_1$ (= $-(1-a)r_D$) | `ext_checks3.py` | verified |
| 0.072 / 0.510; 0.628 / 0.032 | $\partial\hat a/\partial\hat e^*$, $\partial\hat a/\partial R_0$ at means | `ext_checks3.py` | verified |
| 8.99 / 13.05 | mean anchor $\beta_1^{\rm anchor}$ (log points) | `ext_checks3.py` | verified |
| 0.489 / 0.296; $e(1)$ 0.451 / 0.471 | $\pi\bar\theta(1-\bar\theta)/(1-\pi)^2$; worst-pool belief | `ext_checks3.py` | verified |
| 0.22, 1.05, 1.71 | Partial Pooling band widths (indicative) | hand computation from verified inputs | derived |
| $\bar f<0.81$ / $<0.13$; calibrated 0.012 / 0.009 | contraction condition (E.20) | hand computation from verified inputs | derived |
| 0.29–0.36 vs 0.14–0.15 (true 0.15) | Monte Carlo mean $\hat a$ OLS vs ratio of means | `ext_mc.py` | verified |
| 6.21% / 7.88%; 2.51% / 3.02% | registry $\hat\sigma_1$ / $\hat\sigma_0$, pooled, A–D | `paper-real-estate/FINDING-sigma1.md` | read, not re-run |
| 29.5% | apartment listings with $d=1,K=0$ | notes A.15 | read, not re-run |
| 62.5% → 18.4% | unmatched share over the period | notes A.14 (V2-QUEUE) | read, not re-run |
| 3.5% / 1.1% | strategic hiders as share of listings | paper 04 (Estimates) | read |
| €1,000, 5%, €250k → 8 log points | delegated-disclosure illustration | assumption | [C, CHECK] |

#### 12.1 Scripts (all in this scratchpad; read-only on the repo; run from the repo root)

- `attention_check.py`, `attention_bound.py`, `levels.py`: pre-existing (notes Part II), re-run unchanged.
- `ext_checks.py`: year-specific windows, level vs DiD estimators, ratio of means, bootstrap, G sensitivity.
- `ext_checks2.py`: level and DiD regressions with intercept; cross-market pass-through attempt.
- `ext_checks3.py`: dispersion of $R_0$, $e$, $\bar C^N$; $C^*_\Delta$; sensitivities; fitted $\hat c_0$; $C^D$-free regression.
- `ext_sympy.py`: 34 symbolic checks; labels match equation numbers in this document.
- `ext_mc.py`: Monte Carlo for estimator bias (E.30).

#### 12.2 What this document did not do

- It did not edit any repository file, run the pipeline, or rebuild the index.
- It did not run the gate checks G1–G5, G7–G10 (they need re-pulls or new index builds).
- It did not compute per-market standard errors of $\hat\beta_{1,m},\hat\Delta_m$, so the homogeneity test and significance-based bound counts are not available.
- It did not check the logit sufficient condition at the estimated $\hat\varsigma$ (§3.6).
- Institutional facts (DPE validity windows, 2022 advertising obligations, fine amounts, commission rates, expiry dates) remain [CHECK].


---

## Part IV. The attention extension, written for the paper (full-model draft, 2026-10-05)

> **Preface (not paper text).**
>
> **Where it goes.** A new subsection, §4.6, placed after "Structural Estimates and Economic Interpretation". Its internal structure mirrors §4.2–§4.3 (Setup → Equilibrium → Comparative statics → Welfare), followed by the reform, identification, estimates and policy.
>
> **What it replaces.** The two paragraphs of `04-structural-draft.tex` (≈ lines 555–589) listing four candidate explanations of the apartment wedge. Proofs go to a new Appendix A-ATT.
>
> **Status of the numbers.** Numbers in **[brackets]** are provisional values from Part III §7 [E]. They must be recomputed after gate checks G1–G3, and nothing here should be pasted before those are run.
>
> **Numbering.** Proposition, lemma, equation and table numbers are placeholders.
>
> **Verification.**
> - New algebra: 16 sympy checks, all OK (`scratchpad/full_model_sympy.py`).
> - Earlier identities: 34 checks, all OK (`ext_sympy.py`).
>
> **Notation map to Part III** (renamed to avoid clashes with the paper):
>
> | Part III | Here |
> |---|---|
> | $\alpha_1,\alpha_0$ | $\omega_1,\omega_0$ |
> | $a$, $a_\Delta$ | $\psi$, $\psi_\delta$ |
> | $R_0$ | $\eta$ |
> | $C^D$, $r_D$ | $C^{\rm def}$; $r_D$ replaced by $e^{\rm def}=\eta-r_D$ |
> | $\bar C^N$ | $\bar C^{\rm sil}$ |
>
> **Superseded by the paper (2026-10-08).** The extension now lives in `paper-real-estate/sections/04-attention-draft.tex` (§4.6) and `sections/A-attention.tex` (Appendix). Those files carry the structural-micro-reviewer fixes, which are not back-ported here:
> - **Wording:** the identification and "single parameter" claims are softened, and the alternatives are retitled as belief-based amendments only.
> - **Footnote:** the ceiling footnote's sign is corrected.
> - **Estimator:** the selection caveat is added.
> - **Monte Carlo:** recalibrated to the data.
> - **Market-by-market band coverage:** 0% of apartment markets and 11% of house markets fall inside their own band.
> - **Contrast:** the segment contrast is restated on C\*.
>
> All numbers come from `scripts/compute_attention.py` and `scripts/mc_attention_estimator.py`.
>
> **Corrections applied 2026-10-08 (integration plan, Phase 1).** These are the design-file items:
> - **M1/D6:** Prop 10 states the no-pre-reform-energy-pricing assumption.
> - **M2:** Complete Adverse Selection may have multiple equilibria (Prop 7(ii), Cor 3 and the proof).
> - **M3:** c₁ entered the former Prop 9 (dispersed hiding costs), since dropped.
> - **M4:** the exact-logit claim is downgraded to a conjecture.
> - **M5:** Prop 6(iv) is restated net of costs.
> - **M7:** the welfare reference price includes C^ins.
> - **N2:** r^def is removed in favour of e^def.
>
> M6 (aggregation of the bracketed numbers) is handled by `scripts/compute_attention.py`. Checks: `scratchpad/phase1_checks.py`.
>
> **Voice.** Per `writing-with-ai.md`, rewrite the load-bearing sentences yourself: the opening, the mechanism paragraphs, and the interpretation of the estimates.

---

### 4.6 Limited Attention to Silence

The estimates in Section 4.5 leave one result unexplained, and its shape is specific enough to point toward a mechanism. In apartment markets the reform raised the price of a listing that shows no rating, relative to one rated E to G, by more than it raised the price of a verified A-to-D listing. We call a listing that shows no rating *silent*; it is a non-disclosing listing ($d=0$) in the notation of Section 4.2. Averaged over the 45 apartment markets the two shifts are 8.5 and 4.1 log points, and the first exceeds the second in 37 of them. In house markets the order is reversed on average, 3.9 against 5.8. This subsection asks what would have to be true of buyers for silence to be worth more than a verified efficient rating.

We allow, but do not impose, one answer: buyers attend to energy when a listing puts it in front of them, and much less when it does not. The extension changes the buyer side of the model and nothing else. It nests the model of Sections 4.2–4.3 as a special case, preserves its regimes, and leaves the identification of $\rho_m$ untouched. It also turns the over-identifying wedge $\hat\lambda_m$ into an estimate of how much attention silent listings receive.

#### 4.6.1 Motivation

**Why the model above cannot reach the apartment wedge.** The difficulty is not one of calibration. In the model of Section 4.2, a buyer who sees no rating prices the listing at her belief about its quality, and a belief about a binary rating lies between the worst rating and the best. A silent listing can therefore sell at most at the price of a verified efficient listing. In levels the non-disclosure premium cannot exceed the energy-efficiency premium. Under any pool belief that is stable across the reform, the same holds for the differences-in-differences: $\hat\Delta_m\le\hat\beta_{1,m}$.[^cap]

The apartment wedge of 6.1 log points decomposes accordingly. Of it, 4.5 points are the amount by which $\hat\Delta$ exceeds $\hat\beta_1$, a region the model cannot enter. Only the remaining 1.6 points, $(1-\hat e^*)\hat\beta_1$, are within reach of any change in how buyers form beliefs about silent listings.

**Alternatives ruled out.** This rules out the amendments that come to mind first.

First, buyers may draw too little inference from silence, as in cursed equilibrium and in experimental evidence on disclosure games (e.g., Eyster and Rabin, 2005; Jin, Luca and Martin, 2021; Hagenbach and Saucet, 2025). Any such rule replaces the Bayesian belief $e^*$ by another number between zero and one, so it stays below the ceiling. It is also quantitatively small here. Sellers without a certificate make up about 94 percent of the silent apartment pool, so the Bayesian belief already sits within a few points of the prior, and full cursedness would account for about 0.1 of the 6.1 points.

Second, buyers may over-react to a displayed poor rating. That lowers the price of E-to-G listings, which is the base of both gaps, and it cancels from the comparison between silent and verified efficient listings.

Third, the distrust discount on inferred quality allowed in Section 4.2 ($\alpha_k<\beta_k$) moves the price of silence down, not up.

Observable composition does not resolve the puzzle either, because the indices hold the hedonic reference property fixed within each market and the comparison is a difference-in-differences.[^comp]

**Attention.** What these amendments share is that the buyer facing a silent listing still thinks about its energy performance; she only reasons about it imperfectly. A large body of evidence suggests that consumers often do not think about costs that are not put in front of them, and that when they do not, they act as if those costs were small rather than average. Buyers under-react to sales taxes that are not included in posted prices (Chetty, Looney and Kroft, 2009), to road tolls collected electronically (Finkelstein, 2009) and to shrouded shipping fees (Brown, Hossain and Morgan, 2010). Energy operating costs are a documented instance in durable-goods markets (e.g., Allcott, 2011; Sallee, 2014; Allcott and Taubinsky, 2015). Models of focusing, salience and sparsity formalise the same idea: the attributes a choice set makes salient receive more weight than those it leaves in the background (e.g., Kőszegi and Szeidl, 2013; Bordalo, Gennaioli and Shleifer, 2013; Gabaix, 2014). In financial markets, limited attention changes how disclosed and undisclosed information is priced (e.g., Hirshleifer and Teoh, 2003; DellaVigna and Pollet, 2009).

**Why apartment buyers in particular.** Three features of the French setting make this behaviour plausible for apartment buyers.

First, a listing that discloses shows the rating as a coloured label and, from January 2022, an estimate of the annual energy bill in euros. Disclosure itself therefore puts energy into the buyer's comparison of dwellings.[^ads] A listing that shows nothing does not.

Second, heating in many apartment buildings is collective and paid through service charges. Apartment buyers are therefore likely to see energy as part of a monthly charge rather than as an attribute of the dwelling.

Third, dwellings are routinely put on the market before their certificate is available [Author: document in Section 3]. A missing rating is therefore common and unremarkable rather than conspicuous.

**The mechanism in three steps.** Suppose first that buyers attend to energy as often for a silent listing as for a rated one. They then price silence at the expected cost of the silent pool, and the model is exactly the one estimated above. Suppose next that they attend half as often. Half of them still price silence at the expected cost of the pool, while the other half price it at whatever they implicitly assume when energy never comes up. If that default is "nothing out of the ordinary", the silent listing gains on every rated listing, efficient ones included. Suppose finally that buyers never attend to energy on a silent listing. It is then priced as if it carried the default cost, which can lie below the cost of an A-rated dwelling, and silence beats every rating.

#### 4.6.2 Setup

We embed display-dependent attention in the buyer side of Section 4.2. This lets us read the over-identifying wedge as a measure of the attention silent listings receive, while the identification of $\rho_m$ and of the concealment cost keeps the routes described in Section 4.4. Everything not stated below is as in Section 4.2: seller types, the No Falsification assumption, Assumption 1 ($K\perp\theta$), the payoff \eqref{eq:payoff} and the demand system \eqref{eq:demand}.

##### Environment and timing

The environment is that of Section 4.2, with one addition on the buyer side. After seeing the listing, an EPC-sensitive buyer either attends to its energy performance or does not, with a probability that depends on what the listing shows.

The timing is as follows.
1. Nature draws the seller's quality $\theta$ and information status $K$, independently, with $\Pr(\theta=1)=\bar\theta$ and $\Pr(K=1)=\pi$.
2. The seller lists the property, choosing the display $d$ (only if $K=1$) and the listing price.
3. A buyer arrives. She is EPC-sensitive with probability $\rho$. If sensitive, she attends to energy with probability $\omega_d$, which depends on the display.
4. She values the property given what she attends to, and buys or not.

##### Payoffs and hiding costs

The seller's problem is \eqref{eq:payoff}, with hiding cost $C(\theta,d)=\mathbf 1[d=0](c_0+\theta c_1)$, interpreted as in Section 4.2. The extension leaves the seller side of the model unchanged. It changes only how buyers price what a listing shows, and therefore what a seller gains by showing nothing. The hiding cost keeps its role as the price of concealment that the equilibrium reveals (Proposition 7 below).

##### Buyer valuations and demand

**Why we rewrite the valuation.** Section 4.2 writes the valuation of an EPC-sensitive buyer in what we call *bonus form*. She adds $\beta_1$ times her belief that the dwelling is efficient, $v_1=\beta_0+\beta_1\,\mathbb E[\theta\mid\cdot\,]+\sum_n\beta_nX_n$. This form is natural when the question is how much a buyer believes, since for a given $X$ her belief is the only thing that varies across listings.

The form has two features that matter once the question becomes whether a buyer thinks about energy at all.
- **It records a difference, not levels.** It contains the difference in energy value between efficient and inefficient dwellings, $\beta_1$, but never the level of the energy cost of either. That level is absorbed into the intercept $\beta_0$.
- **It has no place for a buyer who forms no belief.** Every sensitive buyer enters through some number $\mathbb E[\theta\mid\cdot\,]\in[0,1]$. The most favourable valuation a silent listing can receive is therefore that of a verified efficient one.

The ceiling documented in Section 4.6.1 is thus a property of the representation as much as of the economics.

The question at the heart of this subsection is what a buyer pays for a listing whose energy performance she does not consider. Answering it requires two objects the bonus form does not contain: the level of the energy cost a buyer subtracts when she prices energy, and the amount she subtracts when she does not, which we call the default energy cost (Definition 1 below). We therefore rewrite the valuation in *cost form*. The rewriting changes nothing in the model of Section 4.2 (Lemma 6). What it changes is what the model can express.

We write the energy component of value as a capitalised cost. A dwelling of quality $\theta$ in market $m$ carries an energy cost $C_{\theta,m}$, with $C_{0,m}>C_{1,m}\ge0$, measured in the same units as the price gaps; we drop the market index when no confusion arises. We take these costs from the construction of the anchor in Assumption~\ref{assum:energy_anchor}:
$$C_{\theta,m}\;=\;\kappa\,\frac{p^E\,a(r,T)}{P_m}\;\bar E_{\theta,m},\qquad\theta\in\{0,1\}.$$
Here $\bar E_{\theta,m}$ is the mean certified primary-energy consumption, in kilowatt-hours of primary energy per square metre per year (kWh$_{\rm ep}$/m²/yr), of quality-$\theta$ dwellings among registry-matched listings in market $m$. The energy price $p^E$, the annuity factor $a(r,T)$, the local price level $P_m$ and the scale $\kappa$ are as in \eqref{eq:energy_anchor}. The anchor is the cost difference, $\beta^{\rm anchor}_{1,m}=C_{0,m}-C_{1,m}$. The extension also uses the cost *level*. Because the conversion factor $\kappa p^Ea(r,T)/P_m$ is common to both qualities, any energy cost in this subsection can equivalently be expressed in kWh$_{\rm ep}$/m²/yr, which is how Table 9 reports them. Define the *energy-cost ratio*
$$\eta_m\;\equiv\;\frac{C_{0,m}}{C_{0,m}-C_{1,m}}\;=\;\frac{\bar E_{0,m}}{\bar E_{0,m}-\bar E_{1,m}}\;>\;1,\tag{4.20}$$
which is computed from the registry alone and does not depend on the energy price, the discount rate or the horizon.

**Lemma 6 (Bonus and cost forms).** Let $\bar V(X)\equiv\beta_0+\sum_n\beta_nX_n+C_0$. The valuation of an EPC-sensitive buyer in Section 4.2 equals $\bar V(X)-C_\theta$ for a disclosed rating and $\bar V(X)-\bar C^{\rm sil}$ for a silent listing, with $\beta_1=C_0-C_1$ and
$$\bar C^{\rm sil}\;\equiv\;\mathbb E[C\mid d=0]\;=\;e\,C_1+(1-e)\,C_0,\tag{4.21}$$
the expected energy cost of the silent pool under the belief $e$ of \eqref{eq:belief_general}.

*Proof.* See Appendix A-ATT. $\Box$

**Definition 1 (Default energy cost).** The *default energy cost* $C^{\rm def}\ge0$ is the energy cost an EPC-sensitive buyer subtracts from a listing's value when she does not attend to energy. It is measured in the same units as $C_\theta$: log points of price, or equivalently kWh$_{\rm ep}$/m²/yr through the conversion factor above. The superscript stands for *default*.

The term follows the limited-attention literature, in which an agent who does not attend to an attribute replaces it with a default value rather than with an inference (e.g., Gabaix, 2014, 2019). The default is therefore not a belief about the dwelling's rating. It is what the buyer implicitly assumes when the question of energy never arises, something like "a normal dwelling, nothing to worry about".

Three benchmark values fix ideas.
- **$C^{\rm def}=0$.** No energy cost is priced at all. This does not mean the buyer believes the dwelling consumes nothing, only that energy plays no part in her valuation.
- **$C^{\rm def}$ equal to the prior mean cost, $\bar\theta C_1+(1-\bar\theta)C_0$.** The inattentive buyer behaves like one who assumes an average dwelling, which is cursedness by another name.
- **$C^{\rm def}=\bar C^{\rm sil}$.** She happens to subtract exactly what an attentive buyer would infer from silence, and attention becomes irrelevant.

The same default applies to rated and silent listings. A buyer who does not attend to energy, by definition, does not use what the listing shows about it. Which value of the default is relevant is an empirical question:
- Proposition 6(iii) below shows that the extension can explain the apartment wedge only if the default lies below the cost of an average efficient dwelling, $C^{\rm def}<C_1$.
- Proposition 10(iii) shows what the data can and cannot say about its level.

Lemma 6 makes precise the sense in which the two forms are the same model, and where they part.

**Normalisation.** Valuations enter prices only through differences across listings. Any amount a buyer subtracts from every listing alike therefore shifts all her valuations by the same constant and drops out of every price gap. The bonus form uses this normalisation twice.
- It folds the energy cost of an inefficient dwelling, $C_0$, into the intercept $\beta_0$.
- It writes the insensitive buyer's valuation as $v_0=\delta_0+\sum_n\delta_nX_n$. In cost form this amounts to subtracting the same constant from every listing, for instance $C_0$ when $\delta_0=\beta_0$.

Both choices are innocuous in Section 4.2, because each buyer treats every listing the same way: a sensitive buyer always prices energy, and an insensitive one never does.

**Why the normalisation stops being innocuous.** It fails as soon as the same buyer may price energy on one listing and not on another. A buyer who ignores energy on a silent listing but prices it on a rated one subtracts different amounts from the two. The difference involves the *level* of what she subtracts when she ignores energy, not only $\beta_1$. Formally, under Assumption 2 below, the non-disclosure premium $\Delta$ departs from the prediction of Section 4.2, $e$ times the energy-efficiency premium $\rho\,\omega_1\beta_1$, by
$$\Delta-e\,\rho\,\omega_1\beta_1\;=\;\rho\,(\omega_1-\omega_0)\,\big(\bar C^{\rm sil}-C^{\rm def}\big).$$
This departure depends on the level of the silent pool's energy cost and on the default $C^{\rm def}$. It vanishes when rated and silent listings receive the same attention ($\omega_1=\omega_0$), whatever the default. The cost form is the representation in which this object exists.

**Why the cost form is the better object.** Three properties make it the better object for the extension.
- **It nests the bonus form exactly** (Lemma 6). The extension can therefore only add to the model of Section 4.2, never contradict it where attention is uniform.
- **Its primitives are physical rather than behavioural.** $C_\theta$ is what a dwelling of quality $\theta$ costs to heat, measured from certified consumption as in the anchor, while attention and the default describe what buyers do with that cost. This separation is what lets the registry discipline the extension through $\eta$, which is computed without reference to any price.
- **It gives the default an economic meaning:** what a buyer subtracts when energy never comes up. An implicit normalisation of the bonus form becomes an assumption that can be stated, defended and tested (Proposition 6(iii)).

**Assumption 2 (Display-dependent attention).** An EPC-sensitive buyer attends to energy with probability $\omega_1$ when the listing displays a rating and with probability $\omega_0\le\omega_1$ when it does not. An attentive buyer subtracts the expected energy cost given what the listing shows: $C_\theta$ if a rating is displayed, $\bar C^{\rm sil}$ otherwise. An inattentive buyer subtracts the default energy cost $C^{\rm def}$ of Definition 1, whatever the listing shows.

We call
$$\psi\;\equiv\;\omega_0/\omega_1\;\in[0,1]$$
the *relative attention to silence*: the attention a listing without a rating receives, per unit of the attention a rated listing receives. We call $\rho\,\omega_d$ the *effective attention* to listings with display $d$: the share of all buyers who price energy when they look at such a listing. Table 7 records what each buyer subtracts.

**Table 7. Energy cost subtracted by buyer type and listing display**

| Buyer | Probability | Displayed rating $\theta$ | Silent listing |
|---|---|---|---|
| EPC-insensitive | $1-\rho$ | $C^{\rm ins}$ | $C^{\rm ins}$ |
| Sensitive, attentive | $\rho\,\omega_d$ | $C_\theta$ | $\bar C^{\rm sil}$ |
| Sensitive, inattentive | $\rho\,(1-\omega_d)$ | $C^{\rm def}$ | $C^{\rm def}$ |

*Notes:* $\omega_d=\omega_1$ for a displayed rating and $\omega_0$ for a silent listing. $C^{\rm ins}$ is the amount an EPC-insensitive buyer subtracts, defined by $\bar V(X)-C^{\rm ins}\equiv v_0(X)$ so that her valuation is the $v_0(X)$ of Section 4.2. It does not depend on the rating or on whether one is displayed, so it is the same for every listing with the same $X$ and cancels from every price gap. Its value never matters (with $\delta_0=\beta_0$ and $\delta_n=\beta_n$, $C^{\rm ins}=C_0$).

The transaction probability generalises \eqref{eq:demand} to three buyer segments:
$$\Gamma(p^{\rm list}\mid d)=\rho\Big[\omega_d\,G\big(\bar V-\mathcal C_d-p^{\rm list}\big)+(1-\omega_d)\,G\big(\bar V-C^{\rm def}-p^{\rm list}\big)\Big]+(1-\rho)\,G\big(v_0-p^{\rm list}\big),\tag{4.22}$$
where $\mathcal C_d$ is $C_\theta$ for a displayed rating and $\bar C^{\rm sil}$ for a silent listing. For the closed forms that follow we use, as in Section 4.4 and Appendix~\ref{app:proofs}, the approximation in which the equilibrium price equals the buyer-share-weighted mean valuation. All results below are stated under this linear pricing approximation, the one used to derive \eqref{eq:premium_derived}. Whether their orderings survive the exact logit demand (4.22) is discussed, not proven, in Appendix A-ATT.

Write $p^{\rm d}_\theta$ for the equilibrium log price, at the reference property $X$, of a listing that displays a rating of quality $\theta$, and $p_{\rm sil}$ for that of a silent listing. We abbreviate $p_{\rm H}\equiv p^{\rm d}_1$ (displayed A to D) and $p_{\rm L}\equiv p^{\rm d}_0$ (displayed E to G). In the notation of Section 4.3, $p_{\rm sil}-p_{\rm L}$ is the premium $p_0^*-p_1^*$.

**Lemma 7 (Prices and the perceived cost of silence).** Under Assumption 2, the energy-efficiency premium $b$ and the non-disclosure premium $\Delta$ are
$$b\;\equiv\;p_{\rm H}-p_{\rm L}\;=\;\rho\,\omega_1\,\beta_1,\qquad \beta_1=C_0-C_1,\tag{4.23}$$
$$\Delta\;\equiv\;p_{\rm sil}-p_{\rm L}\;=\;\rho\,\omega_1\,(C_0-C^*),\qquad C^*\;\equiv\;C^{\rm def}+\psi\,\big(\bar C^{\rm sil}-C^{\rm def}\big).\tag{4.24}$$
More generally, $p^{\rm d}_\theta-p_{\rm sil}=-\rho\,\omega_1\,(C_\theta-C^*)$ for $\theta\in\{0,1\}$.

*Proof.* See Appendix A-ATT. $\Box$

$C^*$ is the energy cost the market behaves as if a silent listing carries: a weighted average of the default and the rational cost of the silent pool, with weight $\psi$ on the latter. The default cancels from the energy-efficiency premium because both listings in that comparison display a rating. It does not cancel from the non-disclosure premium, because a silent listing draws attention $\omega_0$ while a rated listing draws $\omega_1$. We keep $\beta_1=C_0-C_1$ for the valuation coefficient of Section 4.2, and write $b=\rho\omega_1\beta_1$ for the energy-efficiency premium, the price gap between displayed efficient and inefficient listings. In the model of Section 4.2 ($\omega_1=1$) the premium is $\rho\beta_1$, and its reform-induced change is what $\hat\beta_1$ estimates.

##### Beliefs and the effective belief

**Who forms a belief, and about what.** Of the three buyer types in Table 7, only one forms a belief about a silent listing: the EPC-sensitive buyer who attends to energy. She asks the question of Section 4.2, namely how likely a dwelling that shows no rating is to be efficient, and answers it with Bayes' rule over the composition of the silent pool. Her belief is the one in \eqref{eq:belief_general}, unchanged:
$$e(\sigma_0,\sigma_1)\;=\;\Pr(\theta=1\mid d=0)\;=\;\frac{\pi\bar\theta\sigma_1+(1-\pi)\bar\theta}{\pi\bar\theta\sigma_1+\pi(1-\bar\theta)\sigma_0+(1-\pi)}.$$
It is the share of efficient dwellings among silent listings: a probability between zero and one.

The other two buyer types form no belief about energy.
- The insensitive buyer does not care about it.
- The inattentive sensitive buyer would care, but does not think about it on this listing and subtracts the default $C^{\rm def}$ instead (Definition 1).

The Bayesian belief therefore reaches prices only through the attentive share of sensitive buyers. That is the sense in which "silence is not read" when attention to silence is low.

**Why we need a summary number.** In Section 4.3 everything the market thinks about silence is summarised by one number, the belief $e$. The non-disclosure premium is that belief times the energy-efficiency premium, $\Delta=\rho\beta_1e$ (\eqref{eq:premium_derived}), so the ratio of the two premia *is* the belief. Under limited attention, prices aggregate a belief held by some buyers and a default used by others, and no single buyer's belief summarises them. It is still useful to have one number that plays the role $e$ played in Section 4.3, so that every formula of that section can be reused. We define it as the number that makes the formula of Section 4.3 hold.

**Definition 2 (Effective belief).** The *effective belief* $\tilde e$ is the ratio of the non-disclosure premium to the energy-efficiency premium,
$$\tilde e\;\equiv\;\frac{\Delta}{b},$$
so that $\Delta=b\,\tilde e$, just as $\Delta=\rho\beta_1e$ in Section 4.3. Equivalently, $\tilde e$ is the belief that rationalises observed prices within the model of Section 4.3. If every EPC-sensitive buyer attended to energy and held belief $\tilde e$ about every silent listing, the non-disclosure premium would be exactly $\Delta$. The model of Section 4.3 confines beliefs to $[0,1]$. An effective belief above one is therefore a direct statement that no belief, Bayesian or behavioural, can account for the premium in that model. The gap between $\tilde e$ and the registry-measured Bayesian belief $e^*$ is precisely what limited attention has to explain.

No buyer holds $\tilde e$. It is a description of prices, expressed in the units of a belief. We now compute it in four steps.

*Step 1 (from premia to costs).* By Lemma 7, $\Delta=\rho\omega_1(C_0-C^*)$ and $b=\rho\omega_1(C_0-C_1)$. The factor $\rho\omega_1$ cancels:
$$\tilde e\;=\;\frac{C_0-C^*}{C_0-C_1}.$$
This expression has a simple reading. It places the perceived cost of silence $C^*$ on a *quality scale* on which the cost of an inefficient dwelling, $C_0$, maps to 0 and the cost of an efficient dwelling, $C_1$, maps to 1. In general, any energy cost $C$ maps to the point $q(C)\equiv(C_0-C)/(C_0-C_1)$ on that scale, and $\tilde e=q(C^*)$. The lower the cost, the higher the point. A cost below $C_1$ maps above 1.

*Step 2 (split the perceived cost).* By (4.24), $C^*$ is a weighted average of the cost an attentive buyer subtracts and the cost an inattentive buyer subtracts:
$$C^*\;=\;\psi\,\bar C^{\rm sil}+(1-\psi)\,C^{\rm def}.$$
The map $q$ is linear, so it preserves weighted averages:
$$\tilde e\;=\;q(C^*)\;=\;\psi\,q\big(\bar C^{\rm sil}\big)+(1-\psi)\,q\big(C^{\rm def}\big).$$

*Step 3 (the attentive buyer's point is the Bayesian belief).* Since $\bar C^{\rm sil}=e\,C_1+(1-e)\,C_0$ by (4.21), we have $C_0-\bar C^{\rm sil}=e\,(C_0-C_1)$, and therefore
$$q\big(\bar C^{\rm sil}\big)\;=\;e.$$
Translated back onto the quality scale, the cost an attentive buyer subtracts is exactly her Bayesian belief. This is Lemma 6 read in reverse.

*Step 4 (the inattentive buyer's point).* Define the *default-implied belief*
$$e^{\rm def}\;\equiv\;q\big(C^{\rm def}\big)\;=\;\frac{C_0-C^{\rm def}}{C_0-C_1}\;=\;\eta-\frac{C^{\rm def}}{C_0-C_1},$$
where the last equality uses $\eta=C_0/(C_0-C_1)$ from (4.20); in particular $e^{\rm def}=\eta$ when $C^{\rm def}=0$. It is the point on the quality scale at which an inattentive buyer implicitly places every listing. Combining Steps 2–4:
$$\tilde e\;=\;\psi\,e+(1-\psi)\,e^{\rm def}.\tag{4.25}$$

**What (4.25) says.**
- **A weighted average of a belief and a default.** The effective belief averages the belief of buyers who think about silence and the default of those who do not. The weight on the belief is the relative attention to silence $\psi$.
- **The two pieces live on different ranges.** The Bayesian belief $e$ is a probability, so $e\le1$. The default-implied belief $e^{\rm def}$ is not a probability. It exceeds one whenever $C^{\rm def}<C_1$, that is, whenever a buyer who ignores energy implicitly assumes a lower cost than that of an average efficient dwelling. With $C^{\rm def}=0$ it equals $\eta$, about 2.3 in apartment markets. A buyer who prices no energy cost at all treats a silent listing as better than a verified efficient one, because even a verified efficient listing shows a positive cost.
- **The two limits.** With $\psi=1$, $\tilde e=e$ and the model is that of Section 4.3. With $\psi=0$, $\tilde e=e^{\rm def}$ and the composition of the silent pool plays no role in prices.
- **The ceiling.** In Section 4.3 the premium could not exceed the energy-efficiency premium because $e\le1$. Here $\tilde e>1$, and hence $\Delta>b$, is possible as soon as $\psi<1$ and $e^{\rm def}>1$. This is the formal counterpart of Section 4.6.1.

**How the effective belief responds to hiding.** In Section 4.2, when more informed low-quality sellers stay silent, the silent pool contains more inefficient dwellings, and the Bayesian belief falls (Lemma~\ref{lem:belief_monotone}). Under limited attention the same change reaches prices only through attentive buyers. Inattentive buyers keep subtracting the default whatever the pool contains, so only the first term of (4.25) moves.

**Lemma 8 (Effective-belief monotonicity).** $\tilde e(\sigma_0,\sigma_1)$ is weakly decreasing in $\sigma_0$ and weakly increasing in $\sigma_1$, strictly so if and only if $\psi>0$. Its derivatives are $\psi$ times those of $e$:
$$\frac{\partial\tilde e}{\partial\sigma_j}\;=\;\psi\,\frac{\partial e}{\partial\sigma_j},\qquad j\in\{0,1\}.$$

*Proof.* In (4.25), only $e$ depends on $(\sigma_0,\sigma_1)$, and $e^{\rm def}$ does not. Differentiate and apply Lemma~\ref{lem:belief_monotone}. $\Box$

**Why it matters for the equilibrium.** In Section 4.3 the hiding rate is pinned down by a feedback loop:
1. more concealment worsens the pool;
2. the worse pool lowers the belief;
3. the lower belief lowers the gain from further concealment.

Lemma 8 says that under limited attention this loop runs at a fraction $\psi$ of its full strength. In apartment markets, with $\psi$ around 0.13, a given increase in hiding moves the price of silence by about one eighth as much as in Section 4.3. Section 4.6.3 shows the consequences: the band of hiding costs that sustains Partial Pooling narrows by the same factor, and the composition of the silent pool matters little for prices.

#### 4.6.3 Equilibrium

##### Disclosure incentives

An informed seller compares the price of silence with the price of her own displayed rating. By Lemma 7 the gross gain from hiding for a type-$\theta$ seller is
$$g_0\;=\;b\,\tilde e,\qquad g_1\;=\;b\,(\tilde e-1),\qquad g_0-g_1=b.\tag{4.26}$$
We write $g_\theta$ for the gross gain from hiding of an informed seller of quality $\theta$, to keep $G$ for the logistic distribution in \eqref{eq:demand}. The low type's gain is the non-disclosure premium itself, $g_0=\Delta$. The model of Section 4.2 writes this gain as $\Delta(e)=\rho\beta_1e$. Under limited attention the same object becomes
$$\Delta_\psi(e)\;\equiv\;b\,\big[\psi\,e+(1-\psi)e^{\rm def}\big]\;=\;\omega_1\Big[\psi\,\Delta(e)+(1-\psi)\,\rho\beta_1e^{\rm def}\Big].\tag{4.27}$$
In the model of Section 4.3, $\omega_1=\psi=1$ and $\Delta_\psi=\Delta$. This one substitution carries the whole equilibrium analysis of Section 4.3 over to limited attention. The hiding gain is a weighted average of the gain in Section 4.3, which depends on the pool, and a gain against the default, which does not.

**Proposition 6 (Disclosure incentives under limited attention).** Under Assumption 2:
- (i) An informed seller with $\theta=0$ strictly prefers non-disclosure if and only if $\tilde e>c_0/b$.
- (ii) An informed seller with $\theta=1$ strictly prefers non-disclosure if and only if $\tilde e>1+(c_0+c_1)/b$, which requires that silence sell above a verified efficient rating.
- (iii) Silence sells above a verified efficient rating ($\tilde e>1$, i.e. $C^*<C_1$) if and only if $\psi<(C_1-C^{\rm def})/(\bar C^{\rm sil}-C^{\rm def})$. This requires $C^{\rm def}<C_1$.
- (iv) If $\psi=1$, then $\tilde e=e$ for any $\omega_1$ and $C^{\rm def}$. Conditions (i)–(ii) are then the net-of-cost comparisons that underlie Proposition~\ref{prop:equilibrium}; with $c_0=c_1=0$ they reduce to Proposition~\ref{prop:premium}.

*Proof.* See Appendix A-ATT. $\Box$

**Economic reading.**
- **Only differential attention matters.** Inattention that is the same for rated and silent listings is equivalent to having fewer EPC-sensitive buyers: it scales both premia together and leaves the model of Section 4.2 intact (part iv).
- **Differential attention matters only if the default is optimistic** (part iii). A buyer who, without thinking about energy, implicitly assumes an average dwelling is a cursed buyer by another name and stays below the ceiling.[^default]
- **The high-quality seller loses her automatic preference for disclosure** once silence outprices a verified efficient rating. What stops her from hiding is then the hiding cost alone (part ii).

**Testable implication.** Part (iii) predicts where silence sits among the ratings. Applied to the seven letters instead of the two quality levels, Lemma 7 implies that the gap between a rated listing and a silent one should be linear in the letter's energy cost and should cross zero at $C^*$. The model of Section 4.2 places that crossing between D and E. Limited attention with an optimistic default places it at or above A.

**Corollary 3 (High-quality sellers disclose outside Complete Adverse Selection).** In any equilibrium with $\sigma_0^*<1$, $\sigma_1^*=0$. In Complete Adverse Selection ($\sigma_0^*=1$), high-quality hiding is possible only if $\tilde e(1,\sigma_1)>1+(c_0+c_1)/b$ for some $\sigma_1$, which requires that silence sell above a verified efficient rating.

*Proof.* See Appendix A-ATT. $\Box$

Corollary~\ref{cor:hq_disclose} survives, but for a different reason. In Section 4.3 high-quality sellers disclose because silence costs them money. Here silence may pay them too, but it always pays them $b$ less than it pays low-quality sellers ((4.26)). With a common hiding cost, the low type is always the first to want to hide, and the high type hides only once every low type already does. With $\sigma_1^*=0$, the belief reduces to \eqref{eq:belief_simplified} and the effective belief to $\tilde e(\sigma_0)=\psi\,e(\sigma_0)+(1-\psi)e^{\rm def}$.

##### Equilibrium characterization

Define the net hiding gain under limited attention, by analogy with \eqref{eq:Phi},
$$\Phi_\psi(\sigma_0)\;\equiv\;\Delta_\psi\big(e(\sigma_0)\big)-c_0\;=\;b\Big[\psi\,\frac{(1-\pi)\bar\theta}{\pi(1-\bar\theta)\sigma_0+(1-\pi)}+(1-\psi)e^{\rm def}\Big]-c_0.\tag{4.28}$$

**Proposition 7 (Equilibrium under limited attention).** Under Assumption 2, an equilibrium exists. It is characterised as follows. Uniqueness holds in (i) and in (iii) when $\psi>0$.
- (i) If $c_0>\Delta_\psi(\bar\theta)$, the equilibrium is Cost-Deterred Hiding, with $\sigma_0^*=0$ and $e^*=\bar\theta$.
- (ii) If $c_0<\Delta_\psi(e(1))$, where $e(1)\equiv e(\sigma_0{=}1)=(1-\pi)\bar\theta/(1-\pi\bar\theta)$ is the belief when every informed low-quality seller hides, every informed low-quality seller hides, $\sigma_0^*=1$: Complete Adverse Selection. Because $\tilde e$ rises with $\sigma_1$ (Lemma 8), high-quality hiding is self-reinforcing here. Write $\bar g_1(\sigma_1)\equiv b\,[\tilde e(1,\sigma_1)-1]$ for the high type's gain. Then $\sigma_1^*=0$, with $e^*=e(1)$, is an equilibrium if and only if $\bar g_1(0)\le c_0+c_1$, and $\sigma_1^*=1$ is an equilibrium if and only if $\bar g_1(1)\ge c_0+c_1$. Both can hold at once, so equilibrium is not unique in this regime. In the model of Section 4.3 ($\psi=1$), $\bar g_1<0$, only $\sigma_1^*=0$ survives, and uniqueness is restored.
- (iii) If $\Delta_\psi(e(1))\le c_0\le\Delta_\psi(\bar\theta)$, the equilibrium is Partial Pooling.
  - If $\psi>0$, it is unique, with
$$e^*\;=\;\frac{c_0/b-(1-\psi)e^{\rm def}}{\psi},\qquad \sigma_0^*\;=\;\frac{1-\pi}{\pi(1-\bar\theta)}\Big(\frac{\bar\theta}{e^*}-1\Big).\tag{4.29}$$
  - If $\psi=0$, Partial Pooling requires $c_0=be^{\rm def}$ exactly, and then every $\sigma_0\in[0,1]$ is an equilibrium.

*Proof.* See Appendix A-ATT. $\Box$

**Table 8. Equilibrium regimes under limited attention**

| Equilibrium | Condition | $\sigma_0^*$ | Non-disclosure premium $\Delta^*$ |
|---|---|---|---|
| Cost-Deterred Hiding | $c_0>\Delta_\psi(\bar\theta)$ | 0 | $b[\psi\bar\theta+(1-\psi)e^{\rm def}]$ |
| Partial Pooling | $\Delta_\psi(e(1))\le c_0\le\Delta_\psi(\bar\theta)$ | (4.29) | $c_0$ |
| Complete Adverse Selection | $c_0<\Delta_\psi(e(1))$ | 1 | $b[\psi e(1)+(1-\psi)e^{\rm def}]$ |

*Notes:* $e(1)=(1-\pi)\bar\theta/(1-\pi\bar\theta)$. At $\psi=1$ the table reduces to Table~\ref{tab:equilibria}.

The three regimes keep their logic, and the central result of Section 4.3 survives intact. In Partial Pooling the non-disclosure premium equals the hiding cost, because the marginal hider is indifferent. That statement concerns the marginal seller, not buyers, so it holds whatever buyers attend to.

What changes is the location and the width of the band of hiding costs that sustains Partial Pooling. Both premium bounds shift up by $(1-\psi)be^{\rm def}$, the part of the gain that does not depend on the pool. The width of the band shrinks by the factor $\psi$.

**Corollary 4 (The Partial Pooling band).** The interval of hiding costs that supports Partial Pooling is
$$\big[\Delta_\psi(e(1)),\,\Delta_\psi(\bar\theta)\big],$$
of width $\psi\,b\,[\bar\theta-e(1)]$. Its width goes to zero as $\psi\to0$.

*Proof.* Direct from (4.27) and Proposition 7. $\Box$

The corollary has a sharp empirical counterpart. At the apartment means, taking the reform-period estimate $\hat\psi_\delta=[0.13]$ of Section 4.6.5 as a proxy for $\psi$ (exact if relative attention was stable across the reform; Appendix A-ATT), the band spans [8.40] to [8.49] log points, a width of [0.09]. In the model of Section 4.2 the width would be [0.71]. A single hiding cost per market would therefore have to fall inside a window of a tenth of a log point for an apartment market to show interior hiding. Yet the registry shows interior hiding rates in essentially every market. A single hiding cost per market therefore generates interior hiding only within a narrow window of costs, particularly in apartments; we do not model heterogeneity in hiding costs across sellers, and we read the band as a limitation of the single-cost specification. The mean apartment premium, [8.53], sits at the upper edge of that window. In houses ($\hat\psi_\delta=[0.95]$) the band runs from [3.22] to [3.96], is [0.74] log points wide, and contains the estimated premium of [3.89]. The single-cost model of Section 4.3 remains adequate there.

##### Comparative statics

**Proposition 8 (Comparative statics under limited attention).** Suppose $C^{\rm def}\le\bar C^{\rm sil}$.
- (i) **Partial Pooling.**
  - $\partial\sigma_0^*/\partial\psi<0$, $\partial\sigma_0^*/\partial C^{\rm def}<0$, $\partial\sigma_0^*/\partial c_0<0$, $\partial\sigma_0^*/\partial(\rho\omega_1)>0$ and $\partial\sigma_0^*/\partial\pi<0$.
  - The effect of $c_0$ on the equilibrium belief is $\partial e^*/\partial c_0=1/(\psi b)$, which grows without bound as $\psi\to0$.
- (ii) **Corners.** The premium is decreasing in $\psi$ whenever the default lies below the prior mean cost, $C^{\rm def}<\bar\theta C_1+(1-\bar\theta)C_0$. In Complete Adverse Selection, $\partial\Delta^*/\partial\pi=\psi\,b\,\partial e(1)/\partial\pi<0$: the belief channel of Proposition~\ref{prop:comparative_statics}(i), scaled by $\psi$.

*Proof.* See Appendix A-ATT. $\Box$

The comparative statics separate three channels. The *revenue channel* ($\rho\omega_1$) works as in Section 4.3. A larger effective mass of buyers who price a displayed rating raises the gain from concealment and the hiding rate.

The *belief channel* ($\pi$) keeps its sign but is scaled by $\psi$. A higher share of informed sellers makes silence more informative only to buyers who think about what silence means. Where attention to silence is low, better registry coverage barely changes the price of silence.

The *attention channel* ($\psi$, $C^{\rm def}$) is new. More attention to silence, or a less optimistic default, lowers the gain from hiding and the hiding rate. These are the margins on which a salience policy acts (Section 4.6.6).

The last statement in part (i) is the formal reason the single-cost model becomes fragile in apartments. When silence is barely read, a small change in the hiding cost produces a large swing in the hiding rate, because nothing on the buyer side pushes back.

##### High-quality hiding and non-strategic silence

Proposition 6(ii) and Corollary 3 say when high-quality sellers may hide: only if silence sells above a verified efficient rating. The registry shows similar hiding rates for the two grades, [6.3] against [8.0] percent in apartments and [2.4] against [2.9] percent in houses. That pattern is not evidence for strategic hiding by high-quality sellers: house sellers of high quality stay silent although silence costs them about [1.9] log points, so some silence is not strategic at all, for instance listings whose certificate is still pending.

##### Welfare

The welfare accounting of Section 4.3 acquires a third component. As before, the hiding cost $c_0$ is a deadweight loss to the extent it destroys real resources. To the extent it reflects the expected value of sanctions, it is in part a transfer to the state. As before, informed hiders net zero at the margin and uninformed sellers earn the non-disclosure premium as a rent.

The premium itself now contains a behavioural transfer. Relative to what a fully attentive buyer would pay, a silent listing sells at a mark-up of
$$p_{\rm sil}-\big(\bar V-(1-\rho)\,C^{\rm ins}-\rho\,\bar C^{\rm sil}\big)\;=\;\rho\,(1-\omega_0)\,\big(\bar C^{\rm sil}-C^{\rm def}\big),\tag{4.31}$$
paid by inattentive EPC-sensitive buyers to every silent seller, uninformed ones included. Unlike the allocative distortion of Section 4.3, which arises because concealed information is not transmitted, this transfer arises because transmitted absence is not read. The model identifies its level only under additional assumptions (Section 4.6.4). Under the reading that the reform's price effects capture post-reform attention, and that displayed ratings are fully attended, it equals $\hat\lambda$, about [6] log points per silent apartment sale.

#### 4.6.4 The reform and identification

The estimands of Section 4.4 are reform-induced changes, so attention enters through how the reform moved it. For any object $x$, write $\delta x\equiv x^{\rm post}-x^{\rm pre}$ for its change across the July 2021 reform, with superscripts denoting the pre- and post-reform periods of Section 4.4. In this notation $\hat\beta_{1,m}$ estimates $\delta b_m$ and $\hat\Delta_m$ estimates $\delta\Delta_m$. Let the reform raise effective attention to rated listings by $\delta(\rho\omega_1)$ and to silent listings by $\delta(\rho\omega_0)$. Define the *spillover*
$$\psi_\delta\equiv\delta(\rho\omega_0)/\delta(\rho\omega_1),$$
the share of the reform's new attention to energy that reached listings showing no rating. Hold the silent pool's composition fixed across the reform and normalise the default to zero. Equations (4.23)–(4.24) in differences then give
$$\hat\lambda_m\;\equiv\;\hat\Delta_m-\hat\beta_{1,m}\hat e^*_m\;=\;(1-\psi_\delta)\,\hat\beta_{1,m}\,\big(\eta_m-\hat e^*_m\big).\tag{4.32}$$

**Proposition 10 (Identification under limited attention).** Under Assumption 2 and the maintained assumptions of Section 4.4, including the assumption that buyers did not price energy before July 2021 (so pre-reform level gaps are non-energy and constant, and $\psi_\delta$ equals post-reform relative attention):
- (i) $\hat\rho_m=\hat\beta_{1,m}/\hat\beta^{\rm anchor}_{1,m}$ identifies $\delta(\rho\omega_1)$, the reform-induced increase in effective attention to displayed ratings.
- (ii) $\hat\Delta_m/\hat\beta_{1,m}$ identifies the reform-period perceived cost of silence, $C^*_\delta=C^{\rm def}+\psi_\delta(\bar C^{\rm sil}-C^{\rm def})$, in units of certified consumption.
- (iii) Given $C^{\rm def}=0$, (4.32) point-identifies $\psi_\delta$. Without that normalisation, $\psi_\delta$ lies in $[0,\,C^*_\delta/\bar C^{\rm sil}]$ and $C^{\rm def}$ in $[0,C^*_\delta]$.
- (iv) In Partial Pooling, the hiding cost of the informed low-quality seller equals the post-reform non-disclosure premium. Under the maintained assumption this is $\delta\Delta$, which $\hat\Delta_m$ estimates.

*Proof.* See Appendix A-ATT. $\Box$

**Economic reading.**
- **The over-identifying wedge is the part of the reform's price effect that silence escaped.** Had silent listings received the same increase in attention as rated ones, their price relative to E-to-G listings would have moved by $\hat\beta_1\hat e^*$, as Section 4.3 predicts. They received less, and the shortfall, priced at the cost of the silent pool, is $\hat\lambda$.
- **A spillover of one** means the reform made energy something buyers ask about whether or not a rating is shown. **A spillover near zero** means it made the rating something buyers read but not something they ask for.
- **Part (i)** gives the paper's demand-side reading of the reform, which changed how much a disclosed rating matters to the buyer, a precise object.
- **Part (iii)** is a statement of what the design cannot do. The two gaps pin down one number per market, the perceived cost of silence. Low attention with a modest default and slightly higher attention with an even more optimistic one fit them equally well. Normalising the default to zero delivers the largest attention compatible with the data.[^levels]

**Testable implications.**
- **The bound.** By (4.25), $\Delta/b\le\eta$ whenever $C^{\rm def}\ge0$. Since $\eta_m$ comes from the registry alone, this is a market-by-market bound on the two estimated gaps.
- **No constant.** Equation (4.32) has no constant: a market where the reform did not move the energy-efficiency premium should show no wedge.
- **Low sensitivity to the registry belief.** The registry belief $\hat e^*_m$ enters (4.32) with weight proportional to $\psi_\delta$, by Lemma 8. Where attention to silence is low, the measurement concerns about the dating of certificates in the registry have little bearing on the estimate.[^ematters]

#### 4.6.5 Estimates

Table 9 reports the estimates. We estimate $1-\psi_\delta$ as the ratio of the cross-market means of the two sides of (4.32). Unlike a regression through the origin, this estimator is free of the attenuation and correlated-noise biases that arise when $\hat\beta_{1,m}$ is noisy and shares the E-to-G index with $\hat\Delta_m$.[^estimator]

**Table 9. Relative attention to silence** [provisional]

| | Apartments | Houses |
|---|---|---|
| Markets | 45 | 97 |
| $\hat\Delta/\hat\beta_1$ (ratio of means) | [2.10] | [0.67] |
| Bound $\eta$ (mean of markets) | [2.31] | [2.11] |
| Perceived cost of silence $C^*_\delta$, kWh/m²/yr | [28] | [231] |
| Rational cost of the silent pool $\bar C^{\rm sil}$, kWh/m²/yr | [243] | [243] |
| $\hat\psi_\delta$, ratio of means (bootstrap 95% CI) | [0.13] ([−0.12, 0.37]) | [0.95] ([0.86, 1.04]) |
| $\hat\psi_\delta$, regression through the origin (HC1 s.e.) | [0.21] ([0.11]) | [0.96] ([0.04]) |
| Test of full attention, $\psi_\delta=1$ ($t$) | [6.9] | [1.0] |
| Identified interval for $\psi_\delta$, $C^{\rm def}\ge0$ | [0, 0.12] | [0, 0.95] |
| Mean slack in the bound, log points ($t$) | [0.92] ([1.0]) | [8.38] ([13.0]) |
| Implied hiding cost of the marginal hider: Section 4.4 ($\hat\beta_1\hat e^*$) / attention reading ($\delta\hat\Delta$, Prop. 10(iv)) | [2.4] / [8.5] | [3.5] / [3.9] |

*Notes:* DiD estimates on the estimation sample of Table 4. $\eta_m$ and $\bar C^{\rm sil}$ use registry letters valued at DPE band midpoints. Bootstrap over markets, 4,999 draws. The identified interval allows any default $C^{\rm def}\in[0,C^*_\delta]$. With the ratio-of-means estimate, the fitted premium $\hat\beta_{1}[\eta-\hat\psi_\delta(\eta-\hat e^*)]$ equals the mean $\hat\Delta$ by construction; it is [8.0] with the regression estimate.

**Full attention is rejected in apartments and not in houses.** The difference between the two segments is large ($t=[6.4]$). Strikingly, the perceived cost of silence in apartments is [28] kWh per square metre per year. That is below the midpoint of the A band, and an order of magnitude below the [243] kWh a fully attentive buyer would assign to the silent pool. Silent apartments are priced as though energy were not part of the transaction. In houses the perceived cost of silence is [231] kWh, within a few percent of the rational cost of the pool, which is why the model of Section 4.3 fits that segment. A single parameter thus accounts for both the rejection in apartments and the fit in houses, and it requires no change to the seller side. By Proposition 10(iii), the apartment estimate is best read as an upper bound, with identified interval [0, 0.12]. Houses establish that silence is priced at the rational cost of the pool, which is all Section 4.3 requires. They do not establish that house buyers are attentive in any absolute sense.

**What the model does not take a stance on.** The model does not take a stance on why apartment buyers fail to attend to energy when no rating is shown. It may be that energy is bundled into service charges. It may be that apartment buyers, often moving from rented housing in which heating was included, have no habit of pricing it. Or it may be that decisions in fast urban markets leave little room to ask. Irrespective of which applies, the implication for prices is the same, and so is the estimate.

**Qualifications.** Three qualifications bound these results.
- **The bound binds.** Apartment markets sit on the bound on average (slack [0.92], $t=[1.0]$). The extension accommodates them only with a default close to "no energy cost", and leaves no room for a less optimistic one.
- **Not every market fits.** [21] of the 45 apartment markets exceed the bound individually. The violations are concentrated where $\hat\beta_{1,m}$ is small and the ratio is noisy, but [40] percent of markets in the top tercile of $\hat\beta_{1,m}$ also exceed it. Limited attention is the leading force on average, but probably not the only one in every market.
- **The level of $\hat\psi_\delta$ depends on the estimator.** It ranges from [0.03] for the median of market ratios to [0.21] for the regression through the origin. What is robust across estimators is the contrast: well below one in apartments, close to one in houses.[^gband]

The trajectory of the estimate over the post-reform period is informative as well. Splitting the post window by reform year, $1-\hat\psi_\delta$ rises in apartments from [0.53] in the first year to [0.76] and [0.72] in the next two, and falls in houses from [0.11] to [0.01] and [0.03]. Over time, then, attention to silence fell behind attention to ratings in apartments, and caught up with it in houses.

#### 4.6.6 Policy implications

The extension leaves the paper's headline policy object intact and changes what surrounds it.

**The renovation threshold.** The threshold for the marginal seller in Partial Pooling equals the energy-efficiency premium in both models, $\bar R=b$ ($\rho\beta_1$ in Section 4.3), because the derivation of Section 5 uses only that seller's indifference. Its composition, however, is very different.
- In Section 4.3, an apartment seller who renovates gains [1.6] log points from the market's pricing of verified quality over silence, and [2.4] from no longer paying to hide.
- Under limited attention she *loses* [4.5] points from the market's pricing, because silence outprices a verified efficient rating, and gains [8.5] from no longer paying to hide.

The private return to renovating thus comes entirely from the concealment cost avoided.

**A salience counterfactual.** A policy that made silence as salient as a rating would extend the reform's increase in attention to silent listings, setting $\psi_\delta=1$. Examples are a mandatory "rating not provided" field, or a platform default that treats a missing rating as a rating. By (4.32), such a policy lowers the non-disclosure premium by exactly $\hat\lambda_m$, whatever the default. That is [6.1] log points in apartment markets and [0.4] in house markets. Because it does not depend on the normalisation of the default, this is the most robust number the extension produces. By Proposition 8, it also lowers hiding.

**Enforcement.** Forcing informed sellers to display would transfer the full non-disclosure premium, [8.5] log points per formerly hidden apartment, from sellers to buyers. That is about three and a half times the [2.4] points implied by Section 4.3. Its effect on the price of the remaining silent listings is negligible ([0.03] points), because attention to silence is low and the pool is already dominated by uninformed sellers.

---

### Appendix A-ATT. Limited attention to silence: proofs

**Proof of Lemma 6.** With $\bar V=\beta_0+\sum_n\beta_nX_n+C_0$ and $\beta_1=C_0-C_1$:
- For a disclosed rating: $\bar V-C_\theta=\beta_0+\sum_n\beta_nX_n+(C_0-C_\theta)=\beta_0+\beta_1\theta+\sum_n\beta_nX_n$.
- For a silent listing: $\bar V-\bar C^{\rm sil}=\beta_0+\sum_n\beta_nX_n+e(C_0-C_1)=\beta_0+\beta_1e+\sum_n\beta_nX_n$, using (4.21). $\Box$

**Proof of Lemma 7.** The proof has five steps: write each buyer's valuation, average them into a price, take differences, simplify, and read off the two premia.

*Step 1 (valuations).* Fix the reference property $X$ and write $\bar V\equiv\bar V(X)$. By Assumption 2 and Table 7, a buyer values a listing at $\bar V$ minus the energy cost she subtracts:

| Buyer | Probability | Displayed rating of quality $\theta$ | Silent listing |
|---|---|---|---|
| Insensitive | $1-\rho$ | $\bar V-C^{\rm ins}$ | $\bar V-C^{\rm ins}$ |
| Sensitive, attentive | $\rho\,\omega_d$ | $\bar V-C_\theta$ | $\bar V-\bar C^{\rm sil}$ |
| Sensitive, inattentive | $\rho\,(1-\omega_d)$ | $\bar V-C^{\rm def}$ | $\bar V-C^{\rm def}$ |

Here $C^{\rm ins}$ is the constant an insensitive buyer subtracts from every listing (Table 7), and $\omega_d=\omega_1$ for a displayed rating, $\omega_0$ for a silent listing.

*Step 2 (prices).*

*(a) The pricing rule.* We use the rule of Section 4.3, made explicit in the derivation of \eqref{eq:premium_derived}: the equilibrium price of a listing equals its expected buyer valuation. Each buyer type's valuation is weighted by the probability that a buyer of that type arrives. Formally, for a listing with display $d$,
$$p\;=\;\sum_{j}\Pr(\text{buyer of type }j\mid d)\times(\text{valuation of type }j).$$
This is the linear approximation to the logit pricing problem \eqref{eq:demand}. Appendix A-ATT ("Exact pricing") explains why the orderings survive without it.

*(b) The weights.* The three buyer types of Step 1 arrive with probabilities $1-\rho$, $\rho\,\omega_d$ and $\rho\,(1-\omega_d)$. These sum to one:
$$(1-\rho)+\rho\,\omega_d+\rho\,(1-\omega_d)=(1-\rho)+\rho=1.$$

*(c) A listing that displays a rating of quality $\theta$* ($\omega_d=\omega_1$). Multiply each valuation by its weight and expand term by term:
$$\begin{aligned}
(1-\rho)\,(\bar V-C^{\rm ins})&=(1-\rho)\,\bar V\;-\;(1-\rho)\,C^{\rm ins},\\
\rho\,\omega_1\,(\bar V-C_\theta)&=\rho\,\omega_1\,\bar V\;-\;\rho\,\omega_1\,C_\theta,\\
\rho\,(1-\omega_1)\,(\bar V-C^{\rm def})&=\rho\,(1-\omega_1)\,\bar V\;-\;\rho\,(1-\omega_1)\,C^{\rm def}.
\end{aligned}$$
Add the three lines. The $\bar V$ terms carry the weights of (b), which sum to one, so together they give $\bar V$. The cost terms remain:
$$p^{\rm d}_\theta\;=\;\bar V\;-\;(1-\rho)\,C^{\rm ins}\;-\;\rho\,\big[\omega_1\,C_\theta+(1-\omega_1)\,C^{\rm def}\big].$$

*(d) A silent listing* ($\omega_d=\omega_0$, and attentive buyers subtract $\bar C^{\rm sil}$). The same three lines are
$$\begin{aligned}
(1-\rho)\,(\bar V-C^{\rm ins})&=(1-\rho)\,\bar V\;-\;(1-\rho)\,C^{\rm ins},\\
\rho\,\omega_0\,(\bar V-\bar C^{\rm sil})&=\rho\,\omega_0\,\bar V\;-\;\rho\,\omega_0\,\bar C^{\rm sil},\\
\rho\,(1-\omega_0)\,(\bar V-C^{\rm def})&=\rho\,(1-\omega_0)\,\bar V\;-\;\rho\,(1-\omega_0)\,C^{\rm def},
\end{aligned}$$
and adding them gives
$$p_{\rm sil}\;=\;\bar V\;-\;(1-\rho)\,C^{\rm ins}\;-\;\rho\,\big[\omega_0\,\bar C^{\rm sil}+(1-\omega_0)\,C^{\rm def}\big].$$

*Reading.* Every price has three pieces:
- the common value $\bar V$;
- the insensitive buyers' constant $(1-\rho)\,C^{\rm ins}$, which is the same for every listing;
- $\rho$ times the *average energy cost subtracted by sensitive buyers*: $\omega_1C_\theta+(1-\omega_1)C^{\rm def}$ for a rated listing, and $\omega_0\bar C^{\rm sil}+(1-\omega_0)C^{\rm def}$ for a silent one.

Only the third piece differs across listings, so only it survives in price gaps (Step 3).

*(e) Consistency check with Section 4.3.* Set full attention, $\omega_1=\omega_0=1$, and the paper's normalisation $C^{\rm ins}=C_0$ (insensitive coefficients equal to sensitive ones), and recall $\bar V=\beta_0+\sum_n\beta_nX_n+C_0$ (Lemma 6).
- A disclosed low-quality listing ($\theta=0$): $p^{\rm d}_0=\bar V-(1-\rho)C_0-\rho C_0=\bar V-C_0=\beta_0+\sum_n\beta_nX_n$. This is the paper's $p_1^*$ (equal to $\beta_0$ at the paper's normalisation of $X$).
- A silent listing: $p_{\rm sil}=\bar V-(1-\rho)C_0-\rho\,\bar C^{\rm sil}=\beta_0+\sum_n\beta_nX_n+\rho\,(C_0-\bar C^{\rm sil})=\beta_0+\sum_n\beta_nX_n+\rho\,\beta_1\,e$, using $C_0-\bar C^{\rm sil}=e\,(C_0-C_1)=e\,\beta_1$. This is the paper's $p_0^*$.

Their difference is $\rho\beta_1e$, which is \eqref{eq:premium_derived}. Step 2 is therefore exactly the paper's pricing computation, with attention added to the weights.

*Step 3 (difference).* Subtracting, the common term $\bar V-(1-\rho)C^{\rm ins}$ cancels:
$$p^{\rm d}_\theta-p_{\rm sil}=-\rho\big[\omega_1C_\theta+(1-\omega_1)C^{\rm def}\big]+\rho\big[\omega_0\bar C^{\rm sil}+(1-\omega_0)C^{\rm def}\big].$$

*Step 4 (simplify).* Collect the default terms: $-\rho(1-\omega_1)C^{\rm def}+\rho(1-\omega_0)C^{\rm def}=\rho(\omega_1-\omega_0)C^{\rm def}$. So
$$p^{\rm d}_\theta-p_{\rm sil}=-\rho\,\omega_1C_\theta+\rho\,\omega_0\,\bar C^{\rm sil}+\rho(\omega_1-\omega_0)\,C^{\rm def}.$$
Substitute $\omega_0=\psi\,\omega_1$ and factor out $-\rho\,\omega_1$:
$$p^{\rm d}_\theta-p_{\rm sil}=-\rho\,\omega_1\Big[C_\theta-\psi\,\bar C^{\rm sil}-(1-\psi)\,C^{\rm def}\Big]=-\rho\,\omega_1\big(C_\theta-C^*\big),$$
because $\psi\,\bar C^{\rm sil}+(1-\psi)\,C^{\rm def}=C^{\rm def}+\psi(\bar C^{\rm sil}-C^{\rm def})=C^*$. This is the general statement of the lemma.

*Step 5 (the two premia).*
- **Energy-efficiency premium.** Apply Step 4 with $\theta=1$ and $\theta=0$ and subtract:
$$b=p_{\rm H}-p_{\rm L}=\big(p^{\rm d}_1-p_{\rm sil}\big)-\big(p^{\rm d}_0-p_{\rm sil}\big)=-\rho\omega_1(C_1-C^*)+\rho\omega_1(C_0-C^*)=\rho\,\omega_1(C_0-C_1)=\rho\,\omega_1\beta_1.$$
The silent price, and with it $C^*$, cancels. That is why the default and the attention to silence do not affect the energy-efficiency premium: (4.23).
- **Non-disclosure premium.** Apply Step 4 with $\theta=0$ and change sign:
$$\Delta=p_{\rm sil}-p_{\rm L}=-\big(p^{\rm d}_0-p_{\rm sil}\big)=\rho\,\omega_1(C_0-C^*).$$
This is (4.24). $\Box$

*Numerical illustration* [E, apartment means, energy costs in kWh-equivalent units]. Take $\rho=0.5$, $\omega_1=1$, $\omega_0=0.1$ (so $\psi=0.1$), $C_1=185$, $C_0=327$, $\bar C^{\rm sil}=243$ and $C^{\rm def}=0$.
- The perceived cost of silence is $C^*=0+0.1\times243=24.3$.
- The energy-efficiency premium is $b=0.5\times(327-185)=71$.
- The non-disclosure premium is $\Delta=0.5\times(327-24.3)=151$, about twice $b$.
- Silence sells above a displayed A-to-D rating by $p_{\rm sil}-p_{\rm H}=0.5\times(185-24.3)=80$.

With $\omega_0=\omega_1$ instead, $C^*=243$ and $\Delta=0.5\times(327-243)=42=0.59\times b$: the prediction of Section 4.3.

**Proof of Lemma 8.** Given in the main text: in (4.25) only $e$ depends on $(\sigma_0,\sigma_1)$, so $\partial\tilde e/\partial\sigma_j=\psi\,\partial e/\partial\sigma_j$, and Lemma~\ref{lem:belief_monotone} signs $\partial e/\partial\sigma_j$. $\Box$

**Proof of Proposition 6.**
- **(i)–(ii).** The low type hides iff $g_0>c_0$ and the high type iff $g_1>c_0+c_1$. Substitute (4.26).
- **(iii).** $\tilde e>1$ iff $C^*<C_1$, by (4.24) and (4.23). Substituting $C^*$ and dividing by $\bar C^{\rm sil}-C^{\rm def}>0$ gives the condition on $\psi$. $C^*$ is a convex combination of $C^{\rm def}$ and $\bar C^{\rm sil}\ge C_1$, so $C^*<C_1$ requires $C^{\rm def}<C_1$.
- **(iv).** With $\psi=1$, $\tilde e=e$ in (4.25). The disclosure comparison is then that of Proposition~\ref{prop:premium}. $\Box$

**Proof of Corollary 3.** If $\sigma_0^*<1$, some low type weakly prefers disclosure, so $g_0\le c_0$. Then $g_1=g_0-b<c_0\le c_0+c_1$, and every high type strictly prefers disclosure. If $\sigma_0^*=1$, the high type hides only if $g_1=b[\tilde e(1,\sigma_1)-1]>c_0+c_1$ at the prevailing $\sigma_1$, which requires $\tilde e>1$. $\Box$

**Proof of Proposition 7.** Whenever $\sigma_0^*<1$, $\sigma_1^*=0$ (Corollary 3), and $\Phi_\psi$ is continuous on $[0,1]$. It is strictly decreasing if $\psi>0$ (Lemma 8) and constant if $\psi=0$.
- **(i)** follows as in Proposition~\ref{prop:equilibrium}.
- **(ii)** Since $\Phi_\psi$ is decreasing, $c_0<\Delta_\psi(e(1))$ makes hiding strictly profitable for every low type at every $\sigma_0$, so $\sigma_0^*=1$. Given $\sigma_0=1$, a high type hides iff $\bar g_1(\sigma_1)>c_0+c_1$. The function $\bar g_1$ is continuous and increasing in $\sigma_1$ by Lemma 8. Hence $\sigma_1=0$ is a best response to itself iff $\bar g_1(0)\le c_0+c_1$, and $\sigma_1=1$ is a best response to itself iff $\bar g_1(1)\ge c_0+c_1$. A low type's gain exceeds a high type's by $b$, so $\sigma_0=1$ remains a best response in both cases. Existence follows because at least one of the two conditions, or an interior crossing, always holds. Uniqueness can fail: with $\pi=0.5$, $\bar\theta=0.6$, $e^{\rm def}=2.3$ and $\psi=0.5$, we get $\bar g_1(0)/b=0.364$ and $\bar g_1(1)/b=0.450$, so any $(c_0+c_1)/b$ in between supports both.
- **(iii)** follows from the intermediate value theorem, with uniqueness from strict monotonicity. Solving $\Delta_\psi(e^*)=c_0$ for $e^*$ gives the first expression in (4.29). Inverting \eqref{eq:belief_simplified} gives $\sigma_0^*$.
- **Existence when $\psi=0$.** If $\Phi_0\neq0$, it has a constant sign and one of the corners obtains. If $\Phi_0=0$, every $\sigma_0$ is a best response. $\Box$

**Proof of Proposition 8.** From (4.29):
- $\partial e^*/\partial\psi=\big[e^{\rm def}-c_0/b\big]/\psi^2$. In Partial Pooling $c_0/b=\tilde e^*=\psi e^*+(1-\psi)e^{\rm def}$, which is below $e^{\rm def}$ whenever $e^*<e^{\rm def}$. That holds when $C^{\rm def}\le\bar C^{\rm sil}$. So $\partial e^*/\partial\psi>0$.
- $\partial e^*/\partial c_0=1/(\psi b)>0$.
- $\partial e^*/\partial C^{\rm def}=(1-\psi)/[\psi(C_0-C_1)]\ge0$.
- $\partial e^*/\partial(\rho\omega_1)<0$, through $b=\rho\omega_1\beta_1$.

Since $\sigma_0^*$ is strictly decreasing in $e^*$ by (4.29), the signs of part (i) follow. The effect of $\pi$ operates only through the inversion (4.29), exactly as in Proposition~\ref{prop:comparative_statics}(ii).

For part (ii):
- The Cost-Deterred premium $b[\psi\bar\theta+(1-\psi)e^{\rm def}]$ has derivative $b[\bar\theta-e^{\rm def}]$ in $\psi$. This is negative iff $C^{\rm def}<C_0-\bar\theta(C_0-C_1)=\bar\theta C_1+(1-\bar\theta)C_0$.
- The Complete Adverse Selection premium has derivative $\psi b\,\partial e(1)/\partial\pi$ in $\pi$, with $\partial e(1)/\partial\pi=-\bar\theta(1-\bar\theta)/(1-\pi\bar\theta)^2<0$.

All derivatives are verified symbolically. $\Box$

**Proof of Proposition 10.**
- **(i)** With $\beta_1^{\rm anchor}=C_0-C_1=\beta_1$, (4.23) in differences gives $\delta b=\delta(\rho\omega_1)\,\beta_1$, which $\hat\beta_1$ estimates; dividing by the anchor gives $\delta(\rho\omega_1)$.
- **(ii)–(iii)** In differences, $\delta\Delta=\delta(\rho\omega_1)(C_0-C^{\rm def})-\delta(\rho\omega_0)(\bar C^{\rm sil}-C^{\rm def})$. Dividing by $\delta b$:
$$\delta\Delta/\delta b=e^{\rm def}-\psi_\delta\,(e^{\rm def}-e)=(C_0-C^*_\delta)/(C_0-C_1).$$
  Subtracting $e$, multiplying by $\delta b$ and replacing $\delta b$ and $\delta\Delta$ by their estimates $\hat\beta_1$ and $\hat\Delta$ gives (4.32) when $C^{\rm def}=0$. The identified set follows because $C^*_\delta$ is a convex combination of $C^{\rm def}\ge0$ and $\bar C^{\rm sil}$.
- **(iv)** In Partial Pooling the indifference of the informed low-quality seller gives $\Delta=c_0$ (Proposition 7(iii)).

**Two caveats.**
- **If the pool belief moves across the reform,** from $e^{\rm pre}$ to $e^{\rm post}$ (superscripts as in $\delta$; likewise $\omega_0^{\rm pre}$ is pre-reform attention to silent listings), the estimator of $1-\psi_\delta$ is biased by
$$\frac{\rho\omega_0^{\rm pre}}{\delta(\rho\omega_1)}\cdot\frac{e^{\rm post}-e^{\rm pre}}{\eta-e^{\rm post}}.$$
  This is zero if pre-reform attention to silence was zero.
- **Relation to post-reform attention.** $\psi_\delta$ equals post-reform relative attention if relative attention was stable, or if pre-reform gaps were not driven by attention to energy. $\Box$

**Exact pricing.** All propositions are derived under the linear pricing approximation of \eqref{eq:premium_derived}. Under the exact demand (4.22), buyers form three segments and the seller's optimal price is not a function of the mean valuation alone, so the propositions do not carry over automatically. For the two-segment demand of Section 4.2, the optimal listing price is nondecreasing in the sensitive buyers' valuation whenever the cross-partial condition of the monotone-comparative-statics argument holds. We conjecture that the orderings of Propositions 6–8 survive exact pricing at the estimated logit scale, and we have not verified this. A numerical check at the estimated scale is left for the robustness appendix. With attention *shares* rather than a representative weight, a silent listing faces three buyer segments. A seller may then price to the inattentive segment and accept a lower probability of sale, which predicts longer time on market for silent listings at higher prices.

**Estimator.** Let $\varepsilon^{\rm H}_m$, $\varepsilon^{\rm L}_m$ and $\varepsilon^{\rm sil}_m$ be the sampling errors in the reform-induced change of the A-to-D, E-to-G and silent price indices of market $m$. Assume they are independent across groups and markets, with variances $s_H^2$, $s_L^2$ and $s_{\rm sil}^2$. Then $\hat\beta_{1,m}=\delta b_m+u_m$ and $\hat\Delta_m=\delta\Delta_m+v_m$, with $u_m=\varepsilon^{\rm H}_m-\varepsilon^{\rm L}_m$ and $v_m=\varepsilon^{\rm sil}_m-\varepsilon^{\rm L}_m$. Both noise terms contain the E-to-G error $\varepsilon^{\rm L}_m$. For the regression of $\hat\lambda_m$ through the origin on $x_m\equiv\hat\beta_{1,m}(\eta_m-\hat e^*_m)$, with $E$ the expectation across markets, the probability limit of $1-\hat\psi_\delta$ is
$$(1-\psi_\delta)\frac{E(\delta b)^2}{E(\delta b)^2+s_H^2+s_L^2}+\frac{s_L^2-e(s_H^2+s_L^2)}{(\eta-e)(E(\delta b)^2+s_H^2+s_L^2)}.$$
Both terms push the estimate toward full attention. The ratio of means $\sum_m\hat\lambda_m/\sum_mx_m$ is consistent.

A Monte Carlo with 45 markets, a true $\psi_\delta$ of 0.15 and index noise of the magnitude in our data gives:
- regression through the origin: mean estimates of 0.29 to 0.36;
- ratio of means: 0.14 to 0.15.

---

[^cap]: The ordering survives the exact logit pricing of Section 4.2, because the seller's optimal price is nondecreasing in the sensitive buyers' mean valuation (Appendix A-ATT). Under a pool belief that changed across the reform, the DiD can exceed $\hat\beta_1$ only if the gap between silent and verified efficient listings narrowed. In apartments it widened, from [2.6] to [7.0] log points.

[^comp]: The indices do not hold fixed the unobserved quality of the dwellings in each group. A split of uninformed sellers by the date of their eventual certificate asks whether dwellings awaiting a certificate drive the premium. [Author: gate checks in Part III §9; report results here once run.]

[^ads]: [CHECK the exact obligations: the decree in force from 1 January 2022 requiring the estimated annual energy expenditure in sale advertisements, and the mention of excessive consumption for F and G dwellings.] The dated increase in the salience of displayed costs offers a second test. Under the extension, the gap between silent and rated listings should widen again at that date, beyond the July 2021 shift.

[^default]: If the default equals the prior mean cost $\bar\theta C_1+(1-\bar\theta)C_0$, it is at least $C_1$, and silence never outprices a verified efficient rating. If it equals the rational cost of the silent pool, attention is irrelevant. The evidence on shrouded costs cited above finds under-weighting toward zero rather than toward the mean, which supports an optimistic default. Housing-specific evidence on this point does not yet exist, and it is the assumption on which the extension most depends.

[^nonstrategic]: The registry shows similar hiding rates for the two grades. That pattern is consistent with Proposition 9(iii) but is not evidence for it. House sellers of high quality stay silent [2.5] percent of the time although silence costs them about two log points, so some silence is not strategic at all, for instance listings whose certificate is still pending. Splitting uninformed sellers by the date of their certificate measures this non-strategic component directly.

[^levels]: The same algebra in levels identifies relative attention at a point in time rather than the spillover. We do not estimate it, because across apartment markets the level gaps carry a large market-specific component that is unrelated to energy and that the differences-in-differences remove. The ratio of mean level gaps and the cross-market slope of one level gap on the other imply very different values ([0.09] and [0.80] post-reform). We therefore use levels only for signs. Silent apartment listings sell above verified efficient ones in most markets, before and after the reform.

[^ematters]: At the apartment means, an error of 0.1 in $\hat e^*$ moves $\hat\psi_\delta$ by less than 0.01. In house markets the sensitivity is about nine times larger, as in Section 4.3, and the dating of certificates matters correspondingly more there.

[^estimator]: The estimators rank by how much weight they place on markets with a large energy-efficiency premium:
    - median of market ratios: [0.03];
    - ratio of means: [0.13];
    - regression through the origin: [0.21];
    - regression with a constant, which the model excludes: [0.53], with an intercept of [2.8] (s.e. [1.9]).

[^gband]: The bound depends on how certified consumption is valued. Our $\eta_m$ values registry letters at band midpoints and the open-ended G band at 500 kWh. Valuing G at 420 or 600 kWh moves the apartment estimate of $\psi_\delta$ (regression) between [0.24] and [0.17], and the number of markets violating the bound between [20] and [23]. [Author: replace with certified consumption, gate check G3.]


---

## Exploratory check: hiding rates by letter vs Proposition 9 (2026-10-08) [E]

**What the model predicts by letter.** With a common non-strategic rate $\nu$, the observed hiding rate for registry letter $k$ is
$$\sigma_k=\nu+(1-\nu)\,F\big(\rho\omega_1(C_k-C^*)\big).$$
- $\nu$ is the non-strategic silent rate.
- The strategic part rises with the letter's energy cost wherever the gain from silence is positive.

This gives a different prediction for each segment:
- **Apartments** ($C^*\approx28$ kWh, below the A band): every letter gains from silence, so hiding should **rise from A to G, including within A–D**.
- **Houses** ($C^*\approx231$ kWh, between D at 215.5 and E at 290.5): letters A–D lose from silence, so hiding should be **flat at $\nu$ across A–D** and rise only across E–G.

**Data.** $\sigma_k=\Pr(d=0\mid K=1,\text{registry letter }k)$, 2022–24, unique `listing_id`. The "Match ≥ median" columns restrict to `match_score` at or above the median, i.e. better registry matches and hence cleaner letters.

| Letter | Apartments, all $K=1$ | Apartments, match ≥ median | Houses, all $K=1$ | Houses, match ≥ median |
|---|---|---|---|---|
| A | 9.97% (n=1,063) | 5.34% (431) | 4.47% (3,645) | 4.37% (1,694) |
| B | 6.46% (7,417) | 3.50% (2,773) | 3.10% (10,153) | 1.99% (4,732) |
| C | 6.33% (98,364) | 3.90% (54,209) | 2.66% (54,461) | 1.69% (27,521) |
| D | 5.88% (141,931) | 4.14% (75,562) | 2.26% (84,924) | 1.50% (43,628) |
| E | 6.61% (102,228) | 4.40% (49,871) | 2.52% (63,999) | 1.63% (31,848) |
| F | 8.31% (40,526) | 5.43% (15,478) | 3.26% (24,619) | 2.12% (11,727) |
| G | 10.82% (24,137) | 7.77% (9,693) | 4.63% (15,551) | 3.06% (7,637) |
| A–D pooled ($\sigma_1$) | 6.09% | 4.03% | 2.51% | 1.66% |
| E–G pooled ($\sigma_0$) | 7.63% | 5.05% | 3.01% | 1.96% |

**Gradients within A–D.** Binomial s.e.; the slope is a weighted fit over B–D, per 100 kWh.

| | C − D | B − D | Slope over B–D |
|---|---|---|---|
| Apartments, all | +0.45pp ($t$=4.5) | +0.58pp (2.0) | −0.60pp |
| Apartments, match ≥ median | **−0.24pp ($t$=−2.2)** | **−0.64pp (−1.8)** | **+0.37pp** |
| Houses, all | +0.40pp (4.6) | +0.84pp (4.7) | −0.61pp |
| Houses, match ≥ median | +0.18pp (1.9) | +0.49pp (2.3) | −0.32pp |

**Reading.**
1. **On the full sample both segments are U-shaped**, with the minimum at D and hiding falling from A to D. That contradicts the apartment prediction.
2. **On better-matched listings the two segments separate in the predicted direction.**
   - In apartments, hiding rises across the efficient letters (B 3.50 → C 3.90 → D 4.14) and keeps rising through G. High-quality sellers hide more the higher their energy cost, which is the signature of high types gaining from silence.
   - In houses, hiding stays flat to declining across B–D and rises only from E to G, consistent with no strategic hiding by high types.
   - The reversal of the apartment gradient between samples suggests that registry-match error distorts letters, and hence the gradient, in the full sample.
3. **The A tail is high in both segments and in both samples, and the model does not explain it.** An A-rated seller should hide least. The excess is presumably non-strategic, for instance new-build or nearly new dwellings. It implies that $\nu$ varies by letter, at least at A.

**Caveats.**
- The differences are a few tenths of a percentage point, with $t$ around 2.
- The median split on `match_score` is ad hoc.
- Pending-certificate listings (G2) have not been removed.
- Treat this as suggestive, not as a test.

**The right version:** split $K$ by certificate date, drop pending certificates, then estimate $\sigma_k$ by letter with market fixed effects and test $H_0$: flat over A–D, separately by segment.

**Composition of the informed hider pool** ($K=1$, $d=0$). Share of each letter among informed hiders, compared with its share among all informed sellers. 2022–24, unique `listing_id`.

| | Apts: % of hiders | % of informed | Ratio | Houses: % of hiders | % of informed | Ratio |
|---|---|---|---|---|---|---|
| A | 0.38 | 0.26 | 1.49 | 2.33 | 1.42 | 1.65 |
| B | 1.72 | 1.78 | 0.96 | 4.51 | 3.95 | 1.14 |
| C | 22.33 | 23.66 | 0.94 | 20.74 | 21.16 | 0.98 |
| D | 29.92 | 34.15 | 0.88 | 27.53 | 33.00 | 0.83 |
| E | 24.22 | 24.59 | 0.98 | 23.07 | 24.87 | 0.93 |
| F | 12.07 | 9.75 | 1.24 | 11.50 | 9.57 | 1.20 |
| G | 9.36 | 5.81 | 1.61 | 10.31 | 6.04 | 1.71 |
| **A–D** | **54.35** | 59.85 | 0.91 | **55.11** | 59.52 | 0.93 |
| **E–G** | **45.65** | 40.15 | 1.14 | **44.89** | 40.48 | 1.11 |
| N | 27,892 hiders | 415,666 informed | | 6,982 hiders | 257,352 informed | |

With `match_score` ≥ median, A–D make up 58.60% of apartment hiders (vs 63.93% of informed) and 56.23% of house hiders (vs 60.24%).

**Reading.**
- **The majority of informed hiders are high quality in both segments**, against 0% under the imposed $\sigma_1=0$.
- **The tilt toward low quality is modest** (E–G ratio 1.10–1.15). It is carried by F and G, plus an A excess.
- **The composition is nearly identical across segments**, although Proposition 9 predicts strategic high-type hiding in apartments only. This points to a large non-strategic component, which gate check G2 (certificate dates) must remove before the pool can be read as concealment, in either model.

**Same composition with D counted as low quality** (high = A–C, low = D–G):

| | Apts: % of hiders | % of informed | Ratio | Houses: % of hiders | % of informed | Ratio |
|---|---|---|---|---|---|---|
| **A–C** | 24.43 | 25.70 | 0.95 | 27.59 | 26.52 | 1.04 |
| **D–G** | 75.57 | 74.30 | 1.02 | 72.41 | 73.48 | 0.99 |
| Hiding rate $\sigma_1$(A–C) / $\sigma_0$(D–G) | 6.38% / 6.83% | | 0.93 | 2.82% / 2.67% | | 1.06 |
| Same, `match_score` ≥ median | 3.89% / 4.59% | | 0.85 | 1.86% / 1.75% | | 1.07 |

**Reading.**
- **At this cut the informed hider pool has essentially the quality mix of all informed sellers.** In houses, high-quality sellers hide slightly *more* than low-quality ones. Informed silence looks close to orthogonal to quality, which strengthens the non-strategic reading.
- **For Proposition 9 this cut is uninformative in houses.** $C^*\approx231$ kWh exceeds D's 215.5, so D-rated house sellers lose from silence and belong with the high types.
- **The threshold is a modelling choice.** The configs use A–D (`epc_threshold: 4.0`). Changing it would move $\bar\theta$, $\hat e^*$, $\bar E_\theta$ and $\eta$.

---

# Part V — Renovation Subsidies under Limited Attention to Silence: a re-derivation

*Status: working notes, 2026-10-08. Derived from the primitives of §4.1 (seller side), §4.6 (limited attention) and §5 (renovation). Every identity and sign below is checked in `scratchpad/policy_attention_sympy.py`; the OK/FAIL tally is in §V.9. Numbers in §V.7 are **provisional** (from `results/attention/summary.csv`, pending gates G2/G3).*


## V.0 What this part does, and the verdict in one page

**Question.** §5 derives a renovation threshold $\bar R$ and a minimum incentive-compatible subsidy $S^*=\max\{\hat R-\bar R,0\}$ in the full-attention model. §5.6 (`ss:att_policy`) claims that under the limited-attention extension of §4.6 (i) the threshold and the subsidy are unchanged, $\bar R=b$; (ii) subsidies and enforcement become complements; (iii) salience is an additional instrument that lowers the premium by $\hat\lambda$. The conclusion adds that "enforcement then matters inside partial pooling as well". This part re-derives everything from the primitives.

**Verdict (details and proofs below).**

1. *With a single hiding cost $c_0$*, $\bar R=b$ in Cost-Deterred Hiding **and** in Partial Pooling (whenever $\sigma_0^*<1$), whatever $\psi$. §5.6's first paragraph is correct *for that model*. But in Complete Adverse Selection the threshold is $\bar R=b-\min\{\,b\tilde e-c_0,\;b+c_1\}$, which can be close to zero or equal to $-c_1$, and it is **selection-dependent** when CAS has multiple equilibria (Proposition V.2).
2. *Dispersed hiding costs were removed at Bastien's request (2026-10-09).* The single-cost model keeps $\bar R=b$ in CD and PP, but the extension's own band result (Corollary `cor:att_band`) shows that a single cost generates interior hiding only in a narrow window, particularly in apartments. This is now reported in the paper as a limitation.
3. "Subsidies and enforcement are complements" and "enforcement matters inside partial pooling" are **not implied** by the single-cost model: the threshold is $b$ in PP whatever the hiding cost. Both claims have been removed from the paper.
4. "Renovation earns her nothing at sale" relied on renovate-then-hide, which under a single cost arises only in CAS.
5. (merged into 3.)
6. Salience: the claim that it lowers the premium by $\hat\lambda$ holding hiding fixed is an exact identity, and correct. "Offsets part of the price effect" is wrong under a single cost: inside PP the offset is **complete** ($\Delta^*=c_0$), so salience works through the hiding rate.
7. A sign the baseline does not have: in CAS and for infra-marginal hiders, $\partial\bar R/\partial(\rho\omega_1)=\beta_1(1-\tilde e)$ (partial equilibrium), which is **negative when silence outprices a verified rating**. More attention to displayed ratings then *lowers* the renovation threshold.
8. The euro figures of §5.5 remain valid ($\hat b_m=\hat\beta_{1,m}$ is the same number under both readings). "Every market is in Partial Pooling" need not carry over.

**Status conventions.** *Assumed* = a modelling choice taken from the paper or added here; *derived* = proven below; *conjectured* = not proven. Every result is stated under the linear pricing approximation of `eq:premium_derived`, which is how §4.6 states its results.

---

## V.1 Primitives and notation

Everything here is taken from §4.1 and §4.6 of the paper unless marked **[added]**.

| Symbol | Meaning |
|---|---|
| $\theta\in\{0,1\}$ | energy quality (1 = efficient, A–D); $\Pr(\theta=1)=\bar\theta$ |
| $K\in\{0,1\}$ | information status; $\Pr(K=1)=\pi$, independent of $\theta$ |
| $d\in\{0,1\}$ | display (1 = rating shown); $K=0\Rightarrow d=0$ (No Falsification) |
| $r\in\{0,1\}$ | renovation (§5): $r=1$ turns an informed $\theta=0$ seller into $\theta'=1$ at cost $\hat R$ |
| $S\ge0$ | renovation subsidy |
| $c(\theta',d)=\mathbf 1[d=0](c_0+\theta'c_1)$ | hiding cost |
| $\rho$ | share of EPC-sensitive buyers |
| $\omega_1,\ \omega_0\le\omega_1$ | probability a sensitive buyer attends to energy on a rated / silent listing |
| $\psi=\omega_0/\omega_1$ | relative attention to silence |
| $C_0>C_1\ge0$ | capitalised energy cost of an inefficient / efficient dwelling; $\beta_1=C_0-C_1$ |
| $C^{\rm def}$ | default cost subtracted by an inattentive sensitive buyer |
| $\bar C^{\rm sil}=eC_1+(1-e)C_0$ | rational expected cost of the silent pool; $e$ is the Bayesian pool belief |
| $C^*=C^{\rm def}+\psi(\bar C^{\rm sil}-C^{\rm def})$ | perceived cost of silence |
| $e^{\rm def}=(C_0-C^{\rm def})/(C_0-C_1)$ | default-implied belief ($=\eta$ when $C^{\rm def}=0$) |
| $b=\rho\omega_1\beta_1$ | energy-efficiency premium $p_{\rm H}-p_{\rm L}$ |
| $\tilde e=\psi e+(1-\psi)e^{\rm def}$ | effective belief, $\Delta=b\tilde e$ |
| $g_0=b\tilde e,\ g_1=b(\tilde e-1)$ | gross gain from silence for an informed seller of quality 0 / 1 |
| $\Delta_\psi(e)=b[\psi e+(1-\psi)e^{\rm def}]$ | low type's hiding gain as a function of the pool belief |
| $e(\sigma_0,\sigma_1)$ | Bayesian belief, `eq:belief_general`; $e(1)\equiv(1-\pi)\bar\theta/(1-\pi\bar\theta)$ |
| $\bar g_1(\sigma_1)=b[\tilde e(1,\sigma_1)-1]$ | high type's gain in CAS |
| $\hat R$ | engineering renovation cost; $\bar R$ threshold; $S^*$ minimum IC subsidy |
| $h\equiv g_0-c$ **[added]** | *net* hiding gain of a low-quality seller with hiding cost $c$ ($=\Phi_\psi$ at the equilibrium pool) |

**Maintained assumptions for this part.**

- **(PE) Partial equilibrium for the threshold** — *assumed, as in the paper.* Def. `def:minimum_subsidy` defines $S^*$ "holding equilibrium beliefs fixed": one seller's renovation decision does not move $e$, $\tilde e$ or prices. Comparative statics compare *across* equilibria (beliefs re-equilibrate when $c_0,\psi,\pi,\rho\omega_1$ move), as the paper does in Prop. `prop:subsidy`. The renovation decisions of *other* sellers are not fed back into beliefs. Remark V.4 says what changes if they are.
- **(Lin) Linear pricing** — *assumed, as in §4.6*: the price of a listing is the buyer-share-weighted mean valuation. Under (Lin), $\Pi(d,\theta)$ in §5 *is* the price, and every payoff is in log points of the reference price, the unit in which $\hat R$ and $S$ must also be expressed (euros per m² = log points × local price per m²).
- **(Ren) Renovation technology** — *assumed, from §5*: only an informed low-quality seller has a renovation decision. Renovation yields $\theta'=1$ **and a new verified certificate**, so the renovated seller is an *informed high-quality* seller: she can display the new rating or hide it. If she hides she bears $c(1,0)=c_0+c_1$. The paper's Table `tab:strategies` and the phrase "disclose a verified high score" presuppose this.
- **(Unf) Uninformed sellers are non-strategic** — *assumed, from §4.2 and made explicit here (Bastien, 2026-10-09).* Information status $K$ is a friction, not a choice: $\pi$ "is not a choice variable" and reflects forced sales (succession, liquidation, divorce), the scarcity of accredited assessors, and the time pressure sellers face. Information acquisition is **outside the disclosure game**. An uninformed seller ($K=0$) therefore has an *empty strategy set*: she cannot display (No Falsification), so she is never silent by choice, and she cannot renovate, because a renovation decision presupposes a diagnostic. She enters the model only through the composition of the silent pool, with mass $1-\pi$, and as a recipient of the non-disclosure premium. A seller who obtains a certificate before listing is, by definition, informed ($K=1$).

---

## V.2 Task A — strategy sets and payoffs for every seller type

### V.2.1 Prices

**Lemma V.1 (prices under limited attention; restates Lemma `lem:att_prices`).** Under Assumption `assum:attention` and (Lin), normalising $p_{\rm L}\equiv0$,
$$
p_{\rm L}=0,\qquad p_{\rm H}=b,\qquad p_{\rm sil}=b\,\tilde e=g_0,\qquad p_{\rm sil}-p_{\rm H}=b(\tilde e-1)=g_1 .
$$

*Proof.* From Table `tab:att_buyers` the price of a rated listing with cost $C$ is $\bar V-(1-\rho)C^{\rm ins}-\rho[\omega_1C+(1-\omega_1)C^{\rm def}]$, and the price of a silent listing is $\bar V-(1-\rho)C^{\rm ins}-\rho[\omega_0\bar C^{\rm sil}+(1-\omega_0)C^{\rm def}]$. Subtracting the $C=C_0$ price: $p_{\rm H}-p_{\rm L}=\rho\omega_1(C_0-C_1)=b$, and $p_{\rm sil}-p_{\rm L}=\rho\omega_1(C_0-C^*)=b\tilde e$, using $\omega_0=\psi\omega_1$, the definition of $C^*$ and $\tilde e=(C_0-C^*)/(C_0-C_1)$. [sympy A1–A3] $\square$

Two facts are used repeatedly:

- $\psi=1\Rightarrow\tilde e=e\le1\Rightarrow g_1\le0$: under full relative attention silence never outprices a verified efficient rating [A4].
- $\tilde e>1$ (equivalently $g_1>0$) is possible iff $\psi<1$ and $e^{\rm def}>1$, i.e. $C^{\rm def}<C_1$ (Prop. `prop:att_incentives`(iii)) [A5]. At the provisional estimates $\tilde e=2.10$ in apartments and $0.67$ in houses (§V.7).

### V.2.2 Payoffs by seller type

Payoffs are price minus hiding cost minus net renovation cost, in log points. Read $c=c_0$.

**Informed low-quality seller ($K=1,\theta=0$): four strategies.**

| # | $(r,d)$ | Buyer sees | Payoff | Using Lemma V.1 |
|---|---|---|---|---|
| 1 | $(0,1)$ disclose low | rating E–G | $p_{\rm L}$ | $0$ |
| 2 | $(0,0)$ hide | silence | $p_{\rm sil}-c$ | $g_0-c\;=\;h$ |
| 3 | $(1,1)$ renovate & disclose | rating A–D | $p_{\rm H}-(\hat R-S)$ | $b-(\hat R-S)$ |
| 4 | $(1,0)$ renovate & hide | silence | $p_{\rm sil}-c-c_1-(\hat R-S)$ | $h-c_1-(\hat R-S)$ |

Strategy 4 bears $c+c_1$, not $c$: after renovation she is a high type, and the hiding-cost function charges $c_1$ to a high type who hides. Under the full-attention model Strategy 4 is strictly dominated by Strategy 3, because $p_{\rm sil}\le p_{\rm H}$ (Cor. `cor:hq_disclose`). Under limited attention it is dominated by Strategy 3 iff $b\ge h-c_1$, i.e. iff $g_1\le c+c_1$. That is exactly the condition under which an informed *high-quality* seller with the same hiding cost discloses (Prop. `prop:att_incentives`(ii)) [B5]. So the paper's footnote to Table `tab:strategies` is right: Strategy 4 can be live only when silence outprices a verified efficient rating.

**Informed high-quality seller ($K=1,\theta=1$): two strategies, no renovation decision.**

| $(d)$ | Payoff |
|---|---|
| disclose | $p_{\rm H}=b$ |
| hide | $p_{\rm sil}-c-c_1=g_0-c-c_1$ |

She hides iff $g_1>c+c_1$.

**Uninformed seller ($K=0$): no strategy, by design.** By (Unf), her strategy set is empty, for three reasons.

1. *She cannot display.* $d=0$ by No Falsification: she cannot disclose a score she does not hold.
2. *She is never silent by choice,* so she never hides. Hiding is a decision that requires holding something to hide, and she bears no hiding cost (§4's welfare paragraph: "the uninformed seller, who bears no hiding cost, is the residual claimant").
3. *She cannot renovate.* Renovation requires an energy diagnostic before and after the works (and renovation subsidies in practice require before/after audits). Obtaining a diagnostic makes her an informed seller, and acquisition is outside the game. This matches §5: "a renovation choice $r$ that upgrades an *informed low-quality* seller's true type".

Her payoff is $p_{\rm sil}$, the same as that of an informed hider, minus nothing. She therefore appears in the policy analysis only through (i) the silent pool, whose composition determines $e$ and so $\tilde e$, and (ii) the renovation flow, from which she is excluded: the population of potential renovators is the informed low-quality mass $\pi(1-\bar\theta)$, as in §5's renovation-flow equation.

*What this assumption does not say.* It does not say uninformed sellers are irrelevant to policy. Audit-infrastructure investment raises $\pi$ (it turns uninformed sellers into informed ones), which is why §5 treats it as a separate instrument that scales how many sellers the other two instruments reach. The decision to acquire information is what the instrument changes, not a strategy the model solves for.

### V.2.3 What the strategy sets imply

The outside option of an informed low-quality seller is the better of Strategies 1 and 2,
$$
O(c)\;=\;\max\{0,\;h\},\qquad h=g_0-c,
$$
and the value of renovating, gross of its net cost, is the better of Strategies 3 and 4,
$$
V(c)\;=\;\max\{b,\;h-c_1\}.
$$
The paper's eq. `eq:threshold` takes $O=h$ (hide) and $V=b$ (display). That is valid only when $h\ge0$ **and** $h-c_1\le b$.

---

## V.3 Task B — the renovation threshold with a single hiding cost $c_0$

### V.3.1 The right definition

**Intuition.** A subsidy has to beat the seller's *best* alternative, and after renovating the seller does whatever is *best* with her new certificate. The paper's eq. `eq:threshold` fixes both choices in advance: the alternative is "hide" and the post-renovation action is "display". Under full attention the second choice is innocuous, because Cor. `cor:hq_disclose` guarantees a high type displays. Under limited attention it is not, because $p_{\rm sil}$ can exceed $p_{\rm H}$. The first choice is wrong in Cost-Deterred Hiding in *both* models, because there the alternative is "disclose low".

**Definition V.1 (renovation threshold).** For an informed low-quality seller with hiding cost $c$, the renovation threshold is the largest net renovation cost at which her best renovating strategy is weakly preferred to her best non-renovating strategy:
$$
\bar R(c)\;\equiv\;V(c)-O(c)\;=\;\max\{b,\;h-c_1\}-\max\{0,\;h\},\qquad h=g_0-c .
\tag{V.1}
$$
The minimum incentive-compatible subsidy keeps the paper's form, $S^*(c)=\max\{\hat R-\bar R(c),0\}$, and `eq:threshold` is the special case $h\ge0,\ h-c_1\le b$.

**Lemma V.2 (one formula for every case).** For $c_1\ge0$,
$$
\bar R(c)\;=\;b-\min\big\{\max\{h,0\},\;b+c_1\big\}
\;=\;\begin{cases}
b, & h\le0 \quad\text{(she would disclose low; after renovating she displays)},\\[2pt]
b-h, & 0<h\le b+c_1 \quad\text{(she would hide; after renovating she displays)},\\[2pt]
-c_1, & h>b+c_1 \quad\text{(she would hide; after renovating she still hides)}.
\end{cases}
\tag{V.2}
$$
$\bar R$ is continuous, piecewise linear and weakly decreasing in $h$, bounded between $-c_1$ and $b$.

*Proof.* Case $h\le0$: $O=0$. Since $h-c_1\le0<b$, $V=b$, so $\bar R=b$. Case $0<h\le b+c_1$: $O=h$, and $h-c_1\le b$ gives $V=b$, so $\bar R=b-h$. Case $h>b+c_1$: $O=h$ and $V=h-c_1$, so $\bar R=-c_1$. The values agree at $h=0$ (both $b$) and at $h=b+c_1$ (both $-c_1$). [sympy B1–B4] $\square$

The switch to Strategy 4 occurs at $h>b+c_1$. Since $h-b-c_1=g_1-(c+c_1)$, this is the same inequality under which an informed high type with cost $c$ hides [B5]. **A renovated seller does what an informed high-quality seller does.** That is the bridge between Corollary `cor:att_hq` and the renovation problem.

### V.3.2 The threshold in each equilibrium regime

With a single cost, $h=\Phi_\psi$ evaluated at the equilibrium pool: $h<0$ in CD, $h=0$ in PP, $h>0$ in CAS (Prop. `prop:att_equilibrium`).

**Proposition V.2 (threshold by regime, single $c_0$, limited attention).** Under (PE), (Lin), (Ren):

1. **Cost-Deterred Hiding** ($c_0>\Delta_\psi(\bar\theta)$): $\bar R^{\rm CD}=b$.
2. **Partial Pooling** ($\Delta_\psi(e(1))\le c_0\le\Delta_\psi(\bar\theta)$): $\bar R^{\rm PP}=b$, for every $\psi\in[0,1]$ and every $C^{\rm def}$ (including the $\psi=0$ continuum of equilibria).
3. **Complete Adverse Selection** ($c_0<\Delta_\psi(e(1))$), with $h^{\rm CAS}=b\tilde e(1,\sigma_1^*)-c_0>0$:
   - (a) in an equilibrium with $\sigma_1^*=0$, which exists iff $\bar g_1(0)\le c_0+c_1$:
   $$\bar R^{\rm CAS}_0\;=\;b\,[1-\tilde e(1,0)]+c_0\;=\;c_0-\bar g_1(0)\;\in\;[-c_1,\,b);$$
   - (b) in an equilibrium with $\sigma_1^*\in(0,1]$, which exists iff $\bar g_1(\sigma_1^*)\ge c_0+c_1$ (with equality if interior): $\bar R^{\rm CAS}_1=-c_1$;
   - (c) when $\bar g_1(0)\le c_0+c_1\le\bar g_1(1)$, both (a) and (b) are equilibria. The threshold then depends on equilibrium selection, and the minimum subsidy jumps by $c_0+c_1-\bar g_1(0)\ge0$ between them.
4. **Nesting.** At $\psi=1$, $\tilde e=e\le1$, so $\bar g_1<0$, only (a) survives, and $\bar R^{\rm CAS}=b[1-e(1)]+c_0>0$, which is the paper's CAS formula.

*Proof.* (1) $h=\Delta_\psi(\bar\theta)-c_0<0$, so Lemma V.2 gives $b$. (2) In PP $\Delta_\psi(e^*)=c_0$, so $h=0$ and Lemma V.2 gives $b$. Since $h-c_1=-c_1\le0<b$, the renovated seller displays [B6, E2]. If $\psi=0$, PP requires $c_0=be^{\rm def}=g_0$, so again $h=0$. (3a) Here $h=b\tilde e(1,0)-c_0$, and $h-c_1\le b\iff\bar g_1(0)\le c_0+c_1$, which is the existence condition of the $\sigma_1^*=0$ equilibrium. Then $\bar R=b-h$ [B7]. The lower bound $-c_1$ is attained when $\bar g_1(0)=c_0+c_1$. (3b) If $\sigma_1^*=1$, $\bar g_1(1)\ge c_0+c_1$ means $h-c_1\ge b$, so $\bar R=-c_1$. If $\sigma_1^*$ is interior, $\bar g_1(\sigma_1^*)=c_0+c_1$, the renovated seller is indifferent, and $\bar R=b-h=c_0-\bar g_1(\sigma_1^*)=-c_1$ [B8]. (3c) This is Prop. `prop:att_equilibrium`(ii) combined with (3a)–(3b). (4) Since $e(1)<1$ [B9], $\bar g_1(0)<0\le c_0+c_1$. $\square$

**Corollary V.1.** With a single hiding cost, $\bar R=b$ iff $\sigma_0^*<1$ (or at the PP/CAS boundary), whatever buyers attend to.

**Comparison with Lemma `lem:threshold_regimes`.**

| Paper's statement | Status under limited attention |
|---|---|
| PP: $\bar R=\Pi(1,1)-\Pi(1,0)$, invariant to $c_0,\pi$ | **Survives verbatim**, with $\Pi(1,1)-\Pi(1,0)=b=\rho\omega_1\beta_1$; also invariant to $\psi$ and $C^{\rm def}$. |
| CAS: $\bar R$ keeps form `eq:threshold`, $\partial\bar R/\partial c_0=1$ | **Survives only on branch (a)**. On branch (b) $\bar R=-c_1$, $\partial\bar R/\partial c_0=0$, and a subsidy must exceed the whole renovation cost. Under multiplicity $\bar R$ is selection-dependent. Even on branch (a), $\bar R$ can be $\le0$ when $\bar g_1(0)\in[c_0,c_0+c_1]$. |
| (silent on CD) | $\bar R^{\rm CD}=b$. `eq:threshold` would give $b[1-\tilde e(0)]+c_0>b$, the wrong object, because the outside option in CD is disclosing low. **This gap is already in the baseline**: with $\psi=1$ the correct CD threshold is $b$, not $b(1-\bar\theta)+c_0$. It is empirically moot only because no market is CD under the full-attention solver. |

**Worked example** (the multiplicity example in the proof of Prop. `prop:att_equilibrium`: $\pi=0.5$, $\bar\theta=0.6$, $e^{\rm def}=2.3$, $\psi=0.5$; take $c_1=0$, $c_0=0.4\,b$). Then $e(1)=0.4286$, $\bar g_1(0)=0.364\,b$, $\bar g_1(1)=0.450\,b$, and $c_0=0.4b<\Delta_\psi(e(1))=1.364b$, so the market is in CAS with two equilibria [B10–B15].

| | $\bar R/b$ | $S^*$ at $\hat R=b$ |
|---|---|---|
| full attention ($\psi=1$), same $\pi,\bar\theta,c_0$ | $1-e(1)+0.4=0.971$ | $0.029\,b$ |
| limited attention, $\sigma_1^*=0$ equilibrium | $0.4-0.364=0.036$ | $0.964\,b$ |
| limited attention, $\sigma_1^*=1$ equilibrium | $0$ | $b$ (= the whole cost) |

> **Remark V.2 (why $\bar R<0$ is not a typo).** In branch (a) with $\bar g_1(0)\in(c_0,c_0+c_1]$, even a free renovation is refused. Renovating forces a choice between displaying, at $b<h$, and hiding a high-quality dwelling, which costs an extra $c_1$. Both are worse than hiding a low-quality one. Whether this is economics or an artefact depends on what $c_1$ is. §4.1 motivates $c_1$ as "forgone premium", which under linear pricing is already counted in $p_{\rm H}-p_{\rm sil}$, so there is a case for $c_1=0$ (§V.8, D2). With $c_1=0$ all lower bounds become $0$.

---

## V.4 (removed)

The dispersed-hiding-cost analysis was removed at Bastien's request (2026-10-09). Part V now covers the single-cost model only.

## V.5 Task D — comparative statics of $\bar R$ and $S^*$

On the active region $\hat R>\bar R$, $\partial S^*/\partial x=-\partial\bar R/\partial x$ for any parameter $x$, so only $\bar R$ is reported. "Enforcement" is $c_0$. "Salience" is $\psi$ at fixed $\omega_1$, i.e. $\omega_0$. Varying $\rho$ or $\omega_1$ at fixed $\psi$ moves only $b=\rho\omega_1\beta_1$, so they enter through the product $\rho\omega_1$.

### V.5.1 Single hiding cost

**Proposition V.5 (single $c_0$).** Across equilibria (beliefs re-equilibrate, the regime is unchanged):

| Regime | $\partial\bar R/\partial c_0$ | $\partial\bar R/\partial\psi$ | $\partial\bar R/\partial\pi$ | $\partial\bar R/\partial(\rho\omega_1)$ | $\partial\bar R/\partial C^{\rm def}$ |
|---|---|---|---|---|---|
| CD | 0 | 0 | 0 | $\beta_1>0$ | 0 |
| PP | 0 | 0 | 0 | $\beta_1>0$ | 0 |
| CAS, $\sigma_1^*=0$ | $1$ | $b\,[e^{\rm def}-e(1)]$ | $-b\psi\,e'(1)>0$ | $\beta_1\,[1-\tilde e(1,0)]$ | $\rho\omega_1(1-\psi)>0$ |
| CAS, $\sigma_1^*>0$ | 0 | 0 | 0 | 0 | 0 |
| *Baseline CAS ($\psi=1$)* | *1* | — | *$-b\,e'(1)>0$* | *$\beta_1[1-e(1)]>0$* | — |

with $e'(1)=-\bar\theta(1-\bar\theta)/(1-\pi\bar\theta)^2<0$.

*Proof.* CD and PP: $\bar R=b=\rho\omega_1\beta_1$ (Proposition V.2). CAS(a): differentiate $\bar R=\rho\omega_1\beta_1[1-\psi e(1)-(1-\psi)e^{\rm def}]+c_0$, using $e(1)$ independent of $c_0,\psi,\rho\omega_1$ and $\partial e^{\rm def}/\partial C^{\rm def}=-1/(C_0-C_1)$ [D1–D5]. CAS(b): $\bar R=-c_1$. $\square$

Readings:

- **$\partial\bar R/\partial\psi>0$ in CAS(a)** iff $e^{\rm def}>e(1)$, which holds whenever $C^{\rm def}<\bar C^{\rm sil}$ at $\sigma_0=1$, the case the extension cares about. More salience raises the threshold, so salience and the subsidy are **substitutes** in CAS.
- **Sign flip in $\rho\omega_1$.** In CAS(a), $\partial\bar R/\partial(\rho\omega_1)=\beta_1(1-\tilde e)$ is *negative* when silence outprices a verified rating [D6]. The baseline claim $\partial\bar R/\partial\rho>0$ (Prop. `prop:subsidy`(ii)) becomes regime- *and* attention-dependent. The reason is that a larger $\rho\omega_1$ scales both $p_{\rm H}-p_{\rm L}=b$ and $p_{\rm sil}-p_{\rm L}=b\tilde e$, and the second scales faster when $\tilde e>1$.
- **The $\pi$ channel** is scaled by $\psi$, as the paper's footnote to Prop. `prop:subsidy`(ii) says, but only on branch (a). On branch (b) it is zero.
- **Regime switches.** $\bar R$ is continuous in $h$ (Lemma V.2), so moving across the CD/PP/CAS(a) boundaries changes $\bar R$ continuously. Discontinuities come only from the $\sigma_1^*$ selection in CAS.

### V.5.3 Salience and the non-disclosure premium

**Proposition V.8 (salience).** Let a policy raise $\omega_0$ to $\omega_1$ (so $\psi\to1$), holding $\omega_1$ fixed.

1. Holding $(\sigma_0,\sigma_1)$ fixed, the premium falls by exactly $b(1-\psi)(e^{\rm def}-e)=\Delta-be\equiv\lambda$, whatever $C^{\rm def}$ [E1]. Under Assumption `assum:no_pre_pricing`, $\hat\lambda_m$ estimates it.
2. Single cost, if the market stays in PP: $\Delta^*=c_0$ before and after [E2]. The hiding rate falls until the pool improvement **fully** offsets the price effect.
3. Single cost, if $c_0>b\bar\theta$ after the change: the market moves to CD, with $\Delta^*=b\bar\theta$ and $\sigma_0^*=0$.
4. On renovation: no effect on $\bar R$ in single-cost CD/PP. $\bar R$ rises in CAS(a). Salience therefore does not move the threshold outside CAS.

*Proof.* (1) $\Delta_\psi(e)-\Delta_1(e)=b(1-\psi)(e^{\rm def}-e)$, and $\Delta_\psi(e)-be=\lambda$ by definition. (2) PP solves $\Delta_\psi(e^*)=c_0$ for any $\psi$. (3) Prop. `prop:att_equilibrium`(i) at $\psi=1$. (4) Proposition V.5. $\square$

### V.5.4 What survives from the baseline (single hiding cost)

- $\bar R=b$ in Partial Pooling and Cost-Deterred Hiding, invariant to $c_0$, $\pi$, $\psi$ and $C^{\rm def}$: **survives**.
- $\partial S^*/\partial c_0=-1$ only in CAS: in CAS(a) $-1$, in CAS(b) $0$.
- $\partial\bar R/\partial\rho>0$: yes in CD/PP; in CAS(a) it has the sign of $1-\tilde e$, **negative when silence outprices a verified rating**.
- $\pi$ moves the population, not the threshold, in CD/PP; in CAS(a) the threshold effect is scaled by $\psi$.
- Subsidies, enforcement and audits act on distinct margins in CD/PP: **survives**.
- The uniform national subsidy is inefficient: **survives**.

---

## V.6 Task E — audit of §5.6 and the conclusion (single hiding cost)

Verdicts: **CORRECT**, **INCOMPLETE** (true only in a sub-case), **WRONG**. The audit of claims that relied on dispersed hiding costs was removed with that material.

| # | Claim (as drafted in §5.6 or the conclusion) | Verdict | Reason |
|---|---|---|---|
| E1 | The threshold comes from the indifference of the marginal seller between hiding and disclosing a poor rating. | **CORRECT** | — |
| E2 | Her outside option is the price of a disclosed poor rating, so renovating gains the efficiency premium whatever buyers attend to. | **CORRECT in PP and CD; INCOMPLETE** | It must also check that the renovated seller displays rather than hides, which holds in PP because $h-c_1=-c_1\le0<b$. False in CAS. |
| E3 | $\bar R=b$ in both models. | **INCOMPLETE** | True in CD and PP. In CAS, $\bar R=c_0-\bar g_1(0)$ or $-c_1$, and may depend on equilibrium selection (counterexample: $\pi=0.5$, $\bar\theta=0.6$, $e^{\rm def}=2.3$, $\psi=0.5$, $c_0=0.4b$, $c_1=0$ gives $\bar R\in\{0.036b,0\}$). |
| E4 | The magnitudes of §5.5 carry over. | **INCOMPLETE** | The euro thresholds equal $\hat b_m$ and remain valid. The statement that every market is in PP is a property of the full-attention solver and need not carry over. |
| E5 | Salience lowers the premium by $\hat\lambda$ at fixed hiding rates. | **CORRECT** | An exact identity (Proposition V.8(1)). |
| E6 | Salience lowers hiding, which "offsets part of the price effect". | **WRONG under a single cost** | Inside PP the offset is complete, $\Delta^*=c_0$ (Proposition V.8(2)). |
| E7 | "A mandatory field sets $\psi=1$". | **ASSUMED** | A behavioural hypothesis; $\psi=1$ equals $\psi_\delta=1$ only under Assumption `assum:no_pre_pricing`. |
| E8 | "Subsidies and enforced display are complements" through renovate-then-hide. | **Not derived in the single-cost model** | Renovate-then-hide requires hiders with different costs; under a single cost no one prefers it outside CAS. The claim has been removed from the paper. |
| E9 | Conclusion: "enforcement then matters inside partial pooling". | **WRONG** | With a single cost the threshold is $b$ in PP whatever the hiding cost. Removed from the paper. |
| E10 | Footnote to Table `tab:strategies`: the strategy remains dominated with a single cost outside CAS. | **CORRECT** | Outside CAS, $g_1<c_0+c_1$, so Strategy 4 is dominated. |
| E11 | Footnote to Prop. `prop:subsidy`(ii): the belief channel is scaled by $\psi$. | **CORRECT on CAS(a); INCOMPLETE** | $\partial\bar R/\partial\rho>0$ flips sign when silence outprices a verified rating (Proposition V.5). |

---

## V.7 Task F — do the §5.5 euro magnitudes survive?

### V.7.1 What the code computes

`src/estimation.py::_compute_threshold_row` calls `src/model.py::renovation_threshold(rho_m, pi_m, th_m, c0_m, pm)`. That function computes $\bar R=\Pi^*(d{=}1,\theta{=}1)-\Pi^*(d{=}0;e^*)+c_0$ by exact two-segment logit profit maximisation, at the full-attention equilibrium (`solve_equilibrium`, which hard-codes $\omega_0=\omega_1=1$), with $c_0=\hat c_{0,m}=\hat\beta_{1,m}\hat e^*_m$. Every market comes out in PP, so the result is $\approx\Pi^*(1,1)-\Pi^*(1,0)$, which under (Lin) is $\hat\rho_m\beta^{\rm anchor}_{1,m}=\hat\beta_{1,m}$.

### V.7.2 What carries over

1. **The discloser-margin threshold, $\bar R_m=\hat b_m$: valid.** Under Prop. `prop:att_identification`(i), $\hat\rho_m$ identifies $\delta(\rho\omega_1)$, so $\hat\rho_m\beta^{\rm anchor}_{1,m}=\hat\beta_{1,m}=\hat b_m$: the same number under both readings. Under (Lin) the §5.5 means and medians (€118/m² apartments, €124/m² houses), the share of markets needing support, and $S^*_m=\max\{\hat R-\hat b_m,0\}$ are unchanged *as the subsidy for disclosers and the marginal hider*.
   - *Caveat (conjectured, not checked):* under exact logit, the attention model's rated-listing demand has three segments (`eq:demand_att`). Its $\Pi(1,1)-\Pi(1,0)$ equals the code's two-segment value only if inattentive sensitive buyers value a rated listing like insensitive buyers. The gap should be second order.
2. **"Every market is in Partial Pooling": need not carry over.** Under the attention reading the single-cost $c_0$ is $\hat\Delta_m$ (Prop. `prop:att_identification`(iv)), and the premium lies inside its own Partial Pooling band in few markets (Cor. `cor:att_band`).
3. **Hiders: not covered by §5.5.** Silence outprices a verified rating ($\hat\Delta_m>\hat\beta_{1,m}$, so $g_{1,m}>0$) in **37 of 45** apartment markets and **33 of 97** house markets (`n_d_gt_b`), although the per-market ratio is noisy.

### V.7.3–V.7.4 (removed)

The numerical illustration and the recomputation list relied on dispersed hiding costs and were removed (2026-10-09).

---

## V.8 Task G — proposed replacement statements for §5.6, and decisions

### V.8.1 Proposed formal statements

**Definition 5.A (renovation threshold under limited attention).** For an informed low-quality seller with hiding cost $c$, $\bar R(c)=\max\{b,\,g_0-c-c_1\}-\max\{0,\,g_0-c\}$. $S^*(c)=\max\{\hat R-\bar R(c),0\}$.

**Lemma 5.B (threshold).** $\bar R(c)=b-\min\{\max\{g_0-c,0\},\,b+c_1\}$. A renovated seller hides her new rating iff $g_1>c+c_1$. *(Proof: Lemma V.2.)*

**Proposition 5.C (single hiding cost).** (i) If $\sigma_0^*<1$ (CD or PP), $\bar R=b=\rho\omega_1\beta_1$, independent of $c_0$, $\pi$, $\psi$ and $C^{\rm def}$. (ii) In CAS, $\bar R=c_0-\bar g_1(0)$ with $\sigma_1^*=0$, and $\bar R=-c_1$ with $\sigma_1^*>0$; when both equilibria exist, $\bar R$ depends on selection. (iii) At $\psi=1$ only the first CAS case arises. *(Proof: Proposition V.2.)*

**Proposition 5.F (salience and the premium).** Raising attention to silent listings to the level rated listings receive lowers the non-disclosure premium by $\lambda=\Delta-be$ at fixed hiding rates (estimated by $\hat\lambda_m$; provisional). Inside Partial Pooling the hiding rate falls until the premium returns to $c_0$. *(Proof: Proposition V.8.)*

### V.8.2 Decisions for Bastien

- **D2. Keep $c_1$, or set $c_1=0$?** Under linear pricing, §4.1's "forgone premium" motivation double-counts $p_{\rm H}-p_{\rm sil}$.
- **D5. Uninformed sellers.** Settled (2026-10-09): they are non-strategic by design, with an empty strategy set (assumption (Unf)). No renovation decision, no hiding, no information acquisition.
- **D6. CAS multiplicity.** A selection rule is needed for $\bar R$ in CAS if the single-cost model is used there.
- **D7. Fix the baseline CD gap** in Lemma `lem:threshold_regimes` (add $\bar R^{\rm CD}=b$) and the "disclosing low is weakly dominated" sentence in §5's opening, which is false in CD.
- **D8. Salience paragraph.** Keep the $\hat\lambda$ magnitude at fixed hiding rates and the regime-correct statement of Proposition 5.F.
- **D10. The $\rho\omega_1$ sign flip** (Proposition V.5) should be mentioned wherever $\partial\bar R/\partial\rho>0$ is used as a targeting argument.

---

## V.9 Verification report

`scratchpad/policy_attention_sympy.py`, run 2026-10-08: **59 OK, 0 FAIL.**

| Block | Checks | Content |
|---|---|---|
| A1–A5 | 5 | prices from the cost form, $b$, $\tilde e$, $g_1$, $\psi=1$ nesting, $e^{\rm def}>1\iff C^{\rm def}<C_1$ |
| B1–B15 | 15 | Lemma V.2 (random draws and each region), renovated hider ⇔ high-type hiding, PP/CAS thresholds, the worked example (0.364, 0.450, 0.036, 0.971, multiplicity) |
| C1–C4 | 4 | Proposition V.3 thresholds, marginal hider, uniform share $1-(1+c_1/b)/\tilde e$, $S_i^*$ formula |
| D1–D18 | 18 | CAS derivatives (Proposition V.5), $e'(1)$, $\partial e/\partial\pi\propto\sigma_1-\sigma_0$, signs of $e_{\sigma_j}$, GE implicit derivatives (Proposition V.6), limits $\psi\to0$ and single cost, renovation-share cross-partial |
| E1–E3 | 3 | salience identity $\lambda$, $\Delta^*=c_0$ in PP for all $\psi$, renovate-and-hide costs $c_1$ |
| F1–F11 | 14 | consistency of `summary.csv` ($\tilde e$, excess $=g_1$, salience $=\lambda$) |

Checks B1, B2–B4, C1 and C4 are randomised numerical identities (2,000–4,000 draws each), used because sympy cannot simplify nested `Max`/`Min` symbolically. The rest are exact symbolic identities or exact rational arithmetic, apart from the numerical-illustration checks.

**Not verified by sympy (pen-and-paper):** existence and uniqueness (taken from the paper's Prop. `prop:att_equilibrium`); the exact-logit caveat in §V.7.2 (conjectured).

---

## Part VI. Policy section re-done under limited attention: computations and figures (2026-10-09)

*Plan: `quality_reports/plans/harmonic-munching-lecun.md`. Code: `scripts/compute_attention.py` (policy block), `scripts/make_attention_figures.py`. Data: `results/attention/*_policy.csv`, `salience_path.csv`, `summary.csv`. Figures: `paper/fig/visuals/fig_att_F*.pdf` and `.png`. The paper is untouched. All numbers are provisional: band-midpoint energy costs and the current registry match.*

### VI.1 What was recomputed, and how

**Core model** (as in §5): hiding cost $\hat c_0=\hat\beta_1\hat e^*$; threshold $\bar R$ and subsidy $S^*$ from the exact-pricing solver, read from `results/<type>/subsidy_grid.csv`.

**Extension:** the hiding cost is the one that reproduces the *observed* hiding rate at the common $\hat\psi$, $\hat c_0^{\rm ext}=\hat\beta_1[\hat\psi\hat e^*+(1-\hat\psi)\eta]$ (the Partial Pooling condition, equation `eq:att_pp`). The threshold is $\bar R=\hat b=\hat\beta_1$ outside Complete Adverse Selection. The subsidy is $S^*=\max\{\hat R-\bar R,0\}$ with $\hat R\in\{250,500\}$ €/m², as in §5.5. The salience counterfactual solves the equilibrium at each $\psi$ with $c_0$ held at the calibrated value, $C^{\rm def}=0$ and $\sigma_1=0$.

**Checks.** The core aggregate costs reproduce §5.5: apartments €2.53bn and €11.86bn, houses €7.31bn and €21.18bn at the two benchmarks (estimation markets weighted by listings). At $\hat\psi$ the model reproduces the observed hiding rate in every market (asserted in the script).

### VI.2 Results

**Fit to the non-disclosure premium** (45 apartment / 97 house markets):

| Predicting $\hat\Delta_m$ | Mean residual | RMSE | corr(pred, obs) |
|---|---|---|---|
| Apartments, core ($\hat\beta_1\hat e^*$) | 6.1 | 8.6 | 0.40 |
| Apartments, extension | 0.0 | 5.9 | 0.43 |
| Houses, core | 0.4 | 3.9 | 0.48 |
| Houses, extension | 0.0 | 3.9 | 0.47 |

The extension removes the **level** bias in apartments (mean residual 6.1 to 0.0) and cuts the RMSE from 8.6 to 5.9. The **cross-market correlation barely moves** (0.40 to 0.43), so the extension does not explain *which* apartment markets have high premia. The zero mean residual holds by construction, because $\hat\psi$ is estimated from the same ratio. Houses are essentially unchanged.

**Hiding cost** (log points): apartments 2.4 (core) to 8.5 (extension); houses 3.5 to 3.9.

**Threshold and subsidy.** The threshold barely changes: $|\bar R^{\rm ext}-\bar R^{\rm core}|$ averages 0.12 log points in apartments and 0.18 in houses. At $\hat R=250$ the mean apartment threshold is €118/m² (core) against €122 (extension). The share of apartment markets needing a positive subsidy at $\hat R=250$ is 98% in both. Aggregate cost at the two benchmarks:

| | Core | Extension |
|---|---|---|
| Apartments, $\hat R=250$ | €2.53bn | €2.24bn |
| Apartments, $\hat R=500$ | €11.86bn | €11.57bn |
| Houses, $\hat R=250$ | €7.31bn | €7.14bn |
| Houses, $\hat R=500$ | €21.18bn | €20.98bn |

**The policy section's headline survives.** The aggregate subsidy changes by about 11% or less. What the extension changes is the hiding cost, the regime reading and the salience counterfactual.

**Salience counterfactual.** At fixed hiding rates, full salience lowers the apartment premium by $\hat\lambda=$ 6.1 log points (houses 0.4). With the equilibrium solve, the mean hiding rate falls from 15.2% to 0.0% in apartments (houses 6.8% to 0.0%), and hiding vanishes in 100% of markets. The path is a **knife-edge**: in apartments the hiding rate goes from about 100% to 0% between $\psi\approx0.12$ and $0.14$, with the observed 15.2% at $\hat\psi=$ 0.13. In houses it declines gradually over $\psi\approx0.85$ to $0.97$. A single hiding cost per market makes the Partial Pooling band about 0.09 log points wide in apartments, so the model predicts that a very small rise in attention to silence would eliminate hiding. We read this as a feature of the single-cost specification, not as a precise elasticity.

### VI.3 Figures (core set)

| # | File | Shows | Main message |
|---|---|---|---|
| F1 | `fig_att_F1_fit` | Predicted vs observed $\hat\Delta_m$, core (hollow) vs extension (filled), by segment | Level fixed; cross-market correlation barely changes |
| F2 | `fig_att_F2_ceilings` | $\hat\Delta_m$ against $\hat b_m$ with the belief ceiling $y=b$ and the attention ceiling $y=\bar\eta b$ | Silence sits above what any belief can explain and near the attention ceiling |
| F3 | `fig_att_F3_contrast` | Perceived cost of silence $C^*$ in kWh with CIs, and $\psi$ by estimator and G-band | The contrast between segments, with honest uncertainty |
| F5 | `fig_att_F5_hiding_cost` | Hiding cost by market, core vs extension | The one policy input that moves |
| F6 | `fig_att_F6_salience` | (i) premium at fixed hiding; (ii) hiding rate against $\psi$ with zooms | Salience acts through hiding; knife-edge |

Draft captions, takeaways and limitations for each figure are in the session scratchpad (`attention_figure_captions.md`).

### VI.4 Limits to state wherever these results are used

- Selection on $\hat\beta_{1,m}>0$ biases $\hat\psi$ toward 1 (Monte Carlo: 0.27 to 0.49 for a true 0.15), so the apartment $\hat\psi$ is an upper bound.
- Apartment CIs are wide: $\hat\psi$ in [-0.12, 0.37], $C^*$ in [-31, 89] kWh.
- $\psi$ is common within a segment. A per-market $\psi$ would be an identity and is outside $[0,1]$ in 26 of 45 apartment markets, so it is never plotted.
- $\bar R=b$ holds outside Complete Adverse Selection and the regime reading is aggregate only: at the common $\hat\psi$ no apartment market has its premium inside its own band.
- Uninformed sellers are non-strategic (assumption (Unf) in Part V) and enter only through the silent pool.

---

## Open questions for Bastien

**Gate for the attention extension (Part III §9).** G1 within-agency comparison (re-pull `realtor_ref`); G2 split $K$ by certificate date (`date_reception_dpe`) plus old certificates; G3 certified kWh for $R_0$. Then optionally G4 (new- vs old-method green premium), G5 (Jan 2023 expiry), G7 (whether the index levels use a common reference property across EPC groups), G8 (letter-level indices).

**Added after the attention follow-up:** (a) split the "Missing" index by $K$ (§A.6); (b) build letter-level indices for the crossing-point test (§A.4); (c) are the indices built on asking or transaction prices?; (d) does SeLoger's DPE filter include or exclude listings with no DPE?

Ordered by how much the answer changes what we do next.

### Decisions only you can make

1. **Does the headline puzzle survive a composition check (R4)?**
   - Rebuild the Chapter-1 apartment index excluding (a) missing-vintage and 2004+ listings and (b) new-build/programme listings.
   - Re-estimate $\hat\Delta_m$ and $\hat\beta_{1,m}$.
   - If $\hat\Delta$ falls toward $\hat e^*\hat\beta_1$, the "silence pays" premium in apartments is mostly *what* is silent, not *why*. The intro framing (03:129, 01-introduction) would then need to change.
   - Do you want this run next, or would you rather explore the theory first?
2. **Which extension goes into the JMP versus V2?**
   - My proposal: κ + ω in the model, with χ/salience as a bounded-robustness proposition ("receiver naivety is nearly irrelevant in a Dye pool dominated by uninformed sellers").
   - Shrouded energy costs ($m_0$) stay a secondary hypothesis.
   - θ̄(X) would be reported only as the within-market $R^2_\theta$ diagnostic in the appendix (Task 2 §2.2.2).
3. **ω changes ĉ₀.** Partial transparency of informed hiders cuts the implied concealment cost from ≈2.4 to ≈1.0 [E]. That flows into the subsidy counterfactuals (§5) and the policy-first framing in your 2026-09-21 plan. Should we accept that hit, or treat ω as robustness?
4. **Is σ₁ = 0 still imposed?** `hider_theta: "impose_zero"` is still set in both configs. Task 1 (E7) and Task 2 (§2.2.1) both need registry θ for hiders. If $\sigma_1\approx\sigma_0$ (FINDING-sigma1), the cursed parameter χ is not identified at all.

### Data questions (one query each)

5. **Is the letter on the page for some "silent" listings?** Are `consoenergie`/`emissionges` non-null on `d=0` listings in the source SeLoger table? If so, the letter is effectively visible and $d$ must be redefined. This is the first thing to check.
6. **Does the SeLoger feed flag new-build / programme / VEFA listings?** Also: does the ADEME match (`ADEME/enrich_listings.py`) use only the existing-dwelling DPE dataset? If it does, new builds are $K=0$ by construction, which would mechanically produce κ.
7. **Re-pull for Task 2's F4 set and for R5/R8:**
   - continuous `build_year` and `energy_source_electric`;
   - `client_type`, `realtor_ref`, `iris_id`;
   - heating system, description text, and (optionally) photo URLs;
   - listing end dates and price revisions, for time-on-market and price cuts.
   
   Which `listing_seloger.*` tables hold these?
8. **Duplicate `listing_id` rows.** Apartments have 843,621 rows but 834,026 ids; houses have 687,878 rows but 658,990 ids, with up to 36× repeats carrying different prices. This affects the paper's $N$ and possibly market moments. Should I open an issue per `issue-ledger.md`?
9. **Apartment label noise.** Listing and registry letters disagree on 26% of matched apartment disclosures. The disagreement is symmetric and rises as `match_score` falls. Should $K$/$\sigma$ moments be re-checked on `match_score` ≥ median?
10. **Continuous registry consumption (kWh/m²) for K=1 listings.** This would enable the letter-threshold RD (R7), which separates letter salience $s$ from cost capitalisation, and therefore protects $\hat\rho$.

### Things found in passing, for the paper (not touched)

11. **The over-identifying test reads a DiD as a level.** Under the paper's own assumptions (c₀ invariant, Partial Pooling in both periods), $D_{\rm pre}=D_{\rm post}=c_0$, so $\hat\Delta=0$. The test $\hat\lambda=\hat\Delta-\hat\beta_1\hat e^*$ is valid only if the pre-period premium is ≈0. In apartments it is 4.5 (§1.1, Consistency remark).
12. **One of the paper's candidate explanations doesn't apply.** 04:556–564 says registry-match noise attenuates $\hat\beta_1$. But $\hat\beta_1$ is built from *displayed*-letter index groups, so match noise enters $\hat e^*,\hat\pi,\hat\sigma_0$ instead. Also, the "risk premium" explanation (04:575–580) has the wrong sign.
13. **Code/docstring mismatch.** `src/model.py:173–198` uses revenue linear in **log** price, while the docstring (:345–360) and the paper (04:100–104) say otherwise. The robustness variant does not compute what it says.
14. **Anchor description.** The paper says the anchor uses certified primary-energy consumption. The code maps letters to band midpoints (`src/data_prep.py:417–425`).
15. **Institutional facts to confirm:**
    - validity windows of pre-July-2021 DPEs;
    - scope of the 25 March 2024 small-surface arrêté (in force 1 July 2024);
    - unit DPEs generated from building data under collective heating;
    - the 1 Jan 2022 advertising obligations (€ cost display; "consommation excessive" for F/G);
    - whether buyers can request the DPE before the *promesse*. This matters for ω.

---

## References: verification status

A separate `claim-verifier` agent checked every reference in this file against Crossref, RePEc or NeurIPS on 2026-10-05. That covers the 33 listed in §1.7 and the 5 methods placeholders in Task 2 (Brant 1990, McCullagh 1980, Ke et al. 2017, Gneiting & Raftery 2007, Roberts et al. 2017). **Result: 36 verified, 2 corrected, 0 not found.**

**Corrections, already applied above:**
- NBER WP 33660 is titled "Voluntary **Report** of Standardized Test Scores".
- McCullagh (1980), *JRSS-B* 42(2), runs from p. **109 to 127**, not 142. Use this if you add it to the bib.

**Also confirmed:**
- **NBER w35625** is Marty Haoyuan Chen & Ginger Zhe Jin, "When Public Signals Backfire: Strategic Disclosure and Information Crowd-Out" (Aug 2026), doi:10.3386/w35625.
- **Hagenbach & Saucet** is *REStud* 92(3).

**Still `[CHECK]`, not bibliographic:**
- institutional facts (DPE validity windows, the small-surface arrêté, collective-heating DPEs, the buyer's right to see the DPE);
- what Frondel et al. (2020) find specifically on non-disclosing listings. Don't cite them for a non-disclosure premium until you've read it.

**Attention part (A.11), second check:** all 16 references verified against Crossref: Finkelstein 2009, Ellison 2005, Gabaix 2014, Sims 2003, Matějka–McKay 2015, Sallee 2014, Allcott–Taubinsky 2015, Allcott–Greenstone 2012, Houde 2018 (use the published title), Allcott 2011, Hirshleifer–Teoh 2003, DellaVigna–Pollet 2009 (published title), Fishman–Hagerty 2003, Golman–Hagmann–Loewenstein 2017, Bernstein–Gustafson–Lewis 2019, Busse et al. 2013.

**Not yet in `paper/DPE_library.bib`:** everything except Milgrom, Grossman, Dye, Jung–Kwon, Brounen–Kok, Fuerst and Myers et al.
