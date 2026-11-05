# Plan: re-derive §5 (Policy Extension) on the limited-attention model

**Status:** DRAFT, 2026-10-09, branch `review`, read-only design (micro-theorist). Repo at `561463c`.
**Checks:** `scratchpad/policy_att_sympy.py` (17 identities, all OK); numbers from
`scratchpad/policy_att_numbers.py` and `policy_att_cf2.py`, read off `results/attention/*` and
`results/<seg>/subsidy_grid.csv`. All numbers are provisional, pending gates G2 and G3.

**Standing constraints:** uninformed sellers have an empty strategy set; there is one hiding cost
c0 per market; psi is common within a segment; c1 = 0; the headline c0 is the core 2.4, while §5
uses c0^fit; agencies are never mentioned; omega_1 is only set-identified.

The full plan is in the agent's final report. This file is the plan-mode copy.

## Core results (derived)
1. R̄ = max{b,h} − max{0,h} = b − min{max{h,0}, b}, with h = Δψ(e*) − c0 and b = ρω1β1. CD and PP give R̄ = b. CAS(a) gives b(1−ẽ(1)) + c0. CAS(b) gives 0. **R̄ ≤ b in every regime**, so S* = max{R̂ − b̂, 0} is a lower bound on the IC subsidy for any hiding cost.
2. GE: inside PP, a subsidy leaves the number of hiders (1−π)(θ̄−e*)/e* and the premium (= c0) unchanged until the disclosed-low stock is used up. After that the remaining informed-low sellers all hide. Full take-up needs an extra ψb(θ̄−e*), which is at most the PP band width. That extra is 0.017 lp in apartments (0.4% of b) and 0.055 lp in houses (0.9%).
3. Instruments map onto parameters. Only S and ρω1 move R̄ in CD/PP. Salience (ψ) and enforcement (c0) move hiding only. π moves the population and the belief channel.

## Author decisions
D1 pricing (linear R̄ = b̂ vs exact solver). D2 aggregation base (all listings / (1−θ̄) / π(1−θ̄)) and annualisation. D3 include the GE proposition. D4 the c0 treatment in the ρω1 counterfactual. D5 §4.6 as an "extension" vs as the model. D6 CAS selection rule (not needed at c0^fit). D7 wording that reconciles c0 = 2.4 with c0^fit = 8.5.
