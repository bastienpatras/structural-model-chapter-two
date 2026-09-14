**Status:** DRAFT

# Collaboration-mode workflow configuration

## Context

At the start of this working relationship on the repo, the user asked for a structured,
precise, rigorous collaboration model on top of the already-ported academic workflow
(`plan-first-workflow.md`, `orchestrator-protocol.md`, the reviewer fleet, `MEMORY.md`/`[LEARN]`
system): (1) plan-first for non-trivial tasks (already the default — `plan-first-workflow.md`),
(2) **"contractor mode"** once a plan is approved — execute autonomously, come back only for
ambiguity or a real decision, (3) **more frequent check-ins for the first few sessions**, tapering
off as the user learns how the workflow behaves, (4) publication-grade polish on every visual,
(5) a workflow that doesn't make the user repeat itself — decisions and corrections get
remembered.

The user explicitly asked to start by **adapting the workflow configuration itself**, before
touching the paper. This plan is that config pass. The humanize-and-review task on
`paper-real-estate/` is a separate, follow-on plan (see "Next step" below) — contractor mode gets
to prove itself starting there, once this lands.

**What I found on exploration:** the repo (ported 2026-09-13 from `rental-disclosure-claude`)
already has almost everything needed — it's missing one named, standing contract, not a pile of
new infrastructure:

- `orchestrator-protocol.md` already has a **"Just Do It" mode**, but it's scoped narrowly: it
  skips a fan-out review skill's *internal* final-approval pause, and is triggered by the phrase
  "just do it"/"handle it" *inside an already-invoked skill*. It explicitly is **not** a
  post-plan-approval daemon ("What is NOT automatic"). The user's ask is broader and different:
  the general posture *after any approved plan*, not specific to review skills.
- `progress-reports.md` + committed `MEMORY.md` + native auto-memory already implement
  "remember decisions, learn from corrections" — this doesn't need rebuilding, just confirming
  and tying the new preferences into it.
- `pyplot-specialist` / `cartopy-specialist` agents and the `dataviz` skill already exist for
  publication-grade visuals — the gap is a standing rule that routes figure work through them
  rather than ad hoc plotting.
- Nothing tracks "how many sessions has this user had with this workflow" — needs a lightweight
  mechanism, not a new hook.

## Approach

### 1. New rule: `.claude/rules/collaboration-mode.md`

The single place this contract lives. Contents:

- **Contractor mode.** Once a plan is approved (`ExitPlanMode` accepted), execute the full plan
  without pausing for per-step confirmation. Return to the user only for: (a) genuine ambiguity
  the plan didn't resolve, (b) a decision that changes scope or approach, (c) anything the
  System prompt's "Executing actions with care" section already requires surfacing (destructive,
  hard-to-reverse, or externally-visible actions). Explicitly same-session and user-present —
  does **not** create an unattended daemon, and does not relax `orchestrator-protocol.md`'s
  documented non-goal ("No post-plan-approval trigger / no daemon") or its Proportionality
  table. Contractor mode changes how often I check in, not how rigorously I verify.
- **Relation to "Just Do It" mode.** Cross-link both ways: "Just Do It" is the inner-loop rule
  for one fan-out skill's approval pause; contractor mode is the outer-loop rule for plan
  execution in general. They compose; neither supersedes the other.
- **Onboarding check-in cadence.** For the first few sessions (rough default: ~5, or until the
  user signals otherwise — "looks good, keep going", fewer corrections needed), check in more
  than contractor mode would otherwise call for: surface interim results at natural milestones
  within a plan, not only at the end. Track this with a plain native-auto-memory note updated
  each session (see §3) — no new hook or script; a behavioral cadence doesn't warrant one.
- **Visual polish standard.** Any figure, plot, or map generation goes through
  `pyplot-specialist` / `cartopy-specialist` (or the `dataviz` skill for non-Python/artifact
  visuals), not ad hoc plotting code — this is what "polished, publication-ready" cashes out to
  operationally.
- **Memory discipline — pointer, not a rebuild.** One paragraph pointing at
  `progress-reports.md` §3 and the `[LEARN]`/`MEMORY.md` system as the existing mechanism;
  the new preferences below feed it rather than replacing it.

### 2. Small, additive cross-links (no rewrites)

- `orchestrator-protocol.md` — one short paragraph under "Just Do It" mode pointing to the new
  rule and stating the scope distinction above.
- `plan-first-workflow.md` — one line on step 7 ("Implement via orchestrator") pointing to
  contractor mode.
- `CLAUDE.md` — one bullet under "Core Principles" linking `collaboration-mode.md`, and an
  update to the existing "Amendment note" paragraph recording this pass (it already anticipates
  exactly this).

### 3. Memory

- **Committed `MEMORY.md`:** one compact `[LEARN:workflow]`-style entry recording the four
  preferences and pointing to `collaboration-mode.md` for the full policy — this is a standing
  directive the user gave explicitly, not an organically-discovered correction, so it's written
  directly rather than routed through `/promote-memory`'s council (that ceremony is for
  auto-memory → committed promotion of *discovered* lessons).
  Consistent with `summary-parity.md`'s drift-proofing bias, keep this entry abstract (points at
  the rule file for specifics) rather than restating cadence numbers that will change.
- **Native auto-memory** (this session's private memory, not committed): a `feedback`-type
  memory with the same four preferences plus the *why* (explicit request at repo-onboarding,
  2026-09-14), and a `project`-type onboarding-status note I update each session to track
  progress toward tapering the check-in cadence.

### Explicitly out of scope for this pass

- No new hooks, scripts, or `settings.json` changes — nothing here needs harness-level
  automation; it's a behavioral/documentation contract.
- No work on the humanize/review task itself.

## Files touched

- `.claude/rules/collaboration-mode.md` (new)
- `.claude/rules/orchestrator-protocol.md` (small addition)
- `.claude/rules/plan-first-workflow.md` (small addition)
- `CLAUDE.md` (small addition + amendment note update)
- `MEMORY.md` (one new entry)
- Native auto-memory files under `~/.claude/projects/-Users-bpatras-structural-model-chapter-two/memory/` (new feedback + project entries, index update)

## Verification

- Re-read all four edited/created `.claude/`/root files together for internal consistency —
  in particular, confirm nothing contradicts the "no daemon" non-goal.
- `grep -rn "collaboration-mode" .claude/ CLAUDE.md` to confirm every cross-link resolves.
- Prose/config only — no compile or test step applies.

## Next step (separate plan, not started here)

Once this lands, enter plan mode again for the actual paper work: run `/humanize` (detect-only)
against `paper-real-estate/`, decide the new-folder scope for the humanized copy (a snapshot for
comparison vs. a compiling fork — the latter interacts with the existing `paper/` ↔
`paper-real-estate/` shared-exhibits architecture in `PLAN.md` decision 4), apply approved
rewrites, then run the reviewer fleet (`structural-micro-reviewer`, `econ-academic-editor`, and
either `/review-paper --peer` or `/seven-pass-review`). Flagging now: `journal-profiles.md` has
no JF/JFE/RFS profile yet (only econ top-5 + poli-sci), which the peer-review pipeline needs — a
question for that plan, not this one.
