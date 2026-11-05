---
name: review-python
description: Read-only Python code review protocol for analysis/estimation scripts. Checks code quality, reproducibility, domain correctness, and numerical discipline; produces a report without editing. Use when user says "review this Python script", "check the Python code", "audit the estimation code", "code review on the Python", or when a `.py` file is touched as part of a paper submission. NOT for running the code — pair with `/audit-reproducibility` for numeric verification.
argument-hint: "[filename or 'all' or a subdirectory like src/ or scripts/]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# Review Python Scripts

Run the comprehensive Python code review protocol — the Python analogue of `/review-r`.

## Steps

1. **Identify scripts to review:**
   - If `$ARGUMENTS` is a specific `.py` filename: review that file only
   - If `$ARGUMENTS` is a directory (`src/`, `scripts/`): review all `.py` files in it
   - If `$ARGUMENTS` is `all`: review all Python files in `src/`, `scripts/`, and root-level
     entry points (`main.py`, `run.py`)

2. **For each script, launch the `python-reviewer` agent** with instructions to:
   - Follow the full protocol in the agent instructions
   - Read `.claude/rules/python-code-conventions.md` for current standards
   - Save report to `quality_reports/[script_name]_python_review.md`

3. **After all reviews complete**, present a summary:
   - Total issues found per script
   - Breakdown by severity (Critical / High / Medium / Low)
   - Top 3 most critical issues

4. **IMPORTANT: Do NOT edit any Python source files.**
   Only produce reports. Fixes are applied after user review.

## When the review touches paper-code consistency

If a script implements something claimed in `paper-real-estate/`, don't stop at style/numerical
discipline — flag for the user that a `structural-micro-reviewer` pass (this project's
paper-vs-code alignment agent) may be warranted too. This skill's job is code quality; that
agent's job is "does the code actually implement what the paper claims."
