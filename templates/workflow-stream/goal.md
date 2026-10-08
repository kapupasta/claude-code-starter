<!-- This file owns the north star of one workflow stream. Copy to <workspace_root>/docs/workflow-streams/<slug>/goal.md and fill in. -->
# Stream goal: <what we're hardening, in a few words>

**Target:** 3 iterations before extracting `HARDENED.md`.

> **Why 3, and why not template it now:** a workflow designed up front and turned into a template after one run bakes in that run's accidents — its stack, its client, its lucky breaks. Patterns harden through repetition. Run the workflow on ~3 real projects, record what held and what broke each time (the `pre-clear` skill appends notes per session and synthesises `iteration-N.md` when an iteration closes), and only then extract the reusable version. Lower the target only if iteration 2 is unambiguously clean, and say so here.

## What we're breaking in

<One paragraph: the workflow or system, its phases or steps, and what makes it different from how you work today.>

## Why now

<The gap or pain that prompted this. A concrete failure is better than a general aspiration.>

## What "hardened" looks like (success criteria)

After <N> iterations we expect to extract:

1. <A concrete artifact — a checklist, a schema, a skill, a starter repo>
2. <A discipline that held without drift across every iteration>
3. <…>

Be concrete enough that a future session can tell whether each item is done.

## Out of scope for this stream

- <Related concerns deliberately left out, and where they live instead>

## Iteration vehicles

- **Iteration 1: <project-dir-name>** — <stack / context>. <status, link to iteration-1.md when synthesised>
- **Iteration 2: TBD** — choose deliberately once iteration 1 closes: what would it test that iteration 1 didn't?
- **Iteration 3: TBD**

<!-- Optional — only if this stream hardens two tracks in parallel (e.g. the workflow + a per-stack starter). Decide at stream-open time.
## Sub-dimension ledger

| Sub-dimension | Count | Notes |
|---|---|---|
| <name> | 0/<target> | |
-->

## When the stream closes

On `HARDENED.md` approval after the target iteration count, this folder moves to `docs/workflow-streams/_archived/<slug>/` and the stream's block leaves `MEMORY.md`. `HARDENED.md` becomes the canonical reference; follow-on work (formal schemas, starters, skills) flows from it as separate projects.
