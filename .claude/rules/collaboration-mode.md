# Collaboration Mode — contractor posture, onboarding cadence, visual polish

This is the standing contract for *how* work gets executed once a plan exists, on top of
`plan-first-workflow.md` (which governs *whether* to plan) and `orchestrator-protocol.md` (which
governs the review-fix runtime for substantive artifacts). Adopted 2026-09-14 at the user's
explicit request, at repo onboarding.

## Contractor mode

**Once a plan is approved (`ExitPlanMode` accepted), execute the full plan without pausing for
per-step confirmation.** Coordinate whatever the plan requires — file edits, subagent fan-outs,
verification passes — autonomously. Return to the user only for:

1. **Genuine ambiguity** the plan didn't resolve — a fork in the road it didn't anticipate.
2. **A decision that changes scope or approach** — not a decision the plan already made.
3. **Anything the System prompt's "Executing actions with care" section already requires
   surfacing** — destructive operations, hard-to-reverse changes, actions visible to others or
   affecting shared state. That guidance is not relaxed by this rule; contractor mode governs
   check-in *frequency*, not risk tolerance.

**What this is not.** Not an unattended daemon, and not a relaxation of
`orchestrator-protocol.md`'s documented non-goal ("No post-plan-approval trigger / no daemon") or
its Proportionality table. Contractor mode is same-session, user-present execution of a plan the
user just read and approved — it changes how often I interrupt, never how rigorously I verify.

**Relation to "Just Do It" mode** (`orchestrator-protocol.md`): that rule skips one fan-out
review skill's *internal* final-approval pause, triggered by "just do it"/"handle it" said
*inside* an already-invoked skill — it still runs the full fan-out → reduce → judge →
loop-until-dry. Contractor mode is the *outer* posture: once any plan is approved, don't come
back to ask "should I continue?" between ordinary steps. The two compose — a contractor-mode
session that invokes a fan-out skill still gets that skill's own full rigor; "Just Do It" just
means that skill's own approval pause is also skipped rather than adding a second pause on top
of the plan approval already given.

## Onboarding check-in cadence

For the first few sessions on this repo (rough default: ~5, or until the user signals otherwise
— "looks good, keep going," fewer corrections needed, explicit "dial it back"), check in *more*
than contractor mode alone would call for: surface interim results at natural milestones within
a plan, not only at the very end, so the user can see and correct the workflow while it is still
being calibrated to them.

Tracked with a plain native-auto-memory note (`project`-type, in this project's memory
directory), updated at the start or end of each session — not a hook or a script; a behavioral
cadence doesn't warrant harness-level automation. Once the note shows the taper condition met,
check-ins drop back to what contractor mode alone requires (ambiguity/decisions only).

## Visual polish standard

"Polished and publication-ready" is operationalized as: **figure, plot, and map generation goes
through a specialist**, not ad hoc plotting code written inline.

- Static Python figures for the paper/slides: `pyplot-specialist` agent.
- Maps (choropleth, point/bubble, flow): `cartopy-specialist` agent.
- Any other visualization surface (HTML/artifact charts, dashboards): the `dataviz` skill.

This applies to new figures and to material revisions of existing ones in `results/figures/`,
`results/tables/` (where a table's presentation is at stake, not just its numbers), and
`paper/fig/` / equivalent — not to quick diagnostic plots made for debugging that never reach a
committed artifact.

## Memory discipline — pointer, not a rebuild

The "don't make me repeat myself" mechanism already exists: `progress-reports.md` §3
(`MEMORY.md` as committed lesson memory, native auto-memory as the local staging ground,
`/promote-memory` as the deliberate promotion path) and the `[LEARN:category]` tag convention
this file's own header points to. This rule doesn't replace that system — it's one more source
feeding it: corrections to *how contractor mode, cadence, or visual routing should work in
practice* get logged as `[LEARN:workflow]` entries the same way any other correction would.

## Cross-references

- [`plan-first-workflow.md`](plan-first-workflow.md) — step 7 hands off into this rule.
- [`orchestrator-protocol.md`](orchestrator-protocol.md) — "Just Do It" mode, the Proportionality
  table, and the "No post-plan-approval trigger / no daemon" non-goal this rule does not relax.
- [`progress-reports.md`](progress-reports.md) — the memory system this rule feeds rather than
  duplicates.
- `../references/agent-fleet.md` — `pyplot-specialist` / `cartopy-specialist` are not in this
  fleet manifest (it only tracks reviewer/fixer subagents); they're referenced here as the
  visual-generation specialists this project uses.
