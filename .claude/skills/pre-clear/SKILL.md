---
name: pre-clear
description: "Run before /clear — friction nominations, saves memories, appends workflow-stream notes if active, sweeps todos, optionally updates CLAUDE.md, then catches uncommitted changes. Prevents losing work, surfaces friction patterns, breaks in new workflows over iterations. Do NOT use for reducing file size or duplication (that is prune), as a standalone commit flow (that is commit), or for writing a daily work log or report."
---

# Pre-Clear Checklist

This file owns the end-of-session wrap. Run it before every `/clear`. Seven steps, in order. The git check runs LAST so it catches changes made by the todo sweep, memory writes, workflow-stream notes and any CLAUDE.md edits from this skill.

Paths below come from `~/.claude/hooks/starter-config.json`: `memory_dir` (the memory folder), `roster_file` (PROJECTS.md) and `workspace_root`. Workflow streams live in `<workspace_root>/docs/workflow-streams/`.

---

## Step 1: Memory Review

Two passes over the session, in order.

### Pass 1: Friction nominations (active hunt)

Surface 1–3 friction points from this session — actively hunt for them, don't wait for them to be obvious. These become candidates for hardened rules across sessions.

**Categories** — pick whichever fits:
- **Decision friction** — had to re-ask the user's intent N times before understanding what they wanted
- **Tool friction** — wrong tool tried repeatedly, or the right tool not invoked when it should have been
- **Memory friction** — should-have-known but didn't (memory was missing, wrong, or not loaded)
- **Verification friction** — claimed done, had to redo; an assumption that turned out wrong

**Fix ladder — run it BEFORE choosing a memory home** (see `principle_fix_the_tool_first.md`). A written rule is the weakest fix: it has to beat a habit with nothing to remind the agent at the moment it matters, and each new rule dilutes the rest. Take the highest rung that works:

1. **Remove it.** Change the environment so the mistake can't happen: a shell option, an install, a setting, an alias.
2. **Make the tool catch it.** A hook or script that corrects the mistake, or blocks with the exact fix in its message. Fixing a hook's false positive also counts.
3. **Write it down.** Only for what 1–2 can't reach: judgment calls, preferences, facts.

**The user is the gate:** a rung 1–2 fix is a *proposal* (the friction + how often it hit, the exact change, its cost), and the user decides every install, setting, hook or loosened restriction. Never apply one on your own. For friction caused by a safety fence (sandbox, scope guard, permission prompts, safety hooks), propose fixes on your side first: your command shape, the fence's error message, a false positive. Loosening a fence is the user's decision alone. **The fix must cost less than the friction** (setup + upkeep vs hits × cost per hit). A repeat despite an existing rule means the rule failed: climb the ladder, don't reword it. A landed rung 1–2 fix retires the rule it replaces and gets a check that fails on drift (e.g. a line in `scripts/meta-health.sh`).

**Template per nomination** — forced shape, because later synthesis depends on concrete context:

```
[<category>] When attempting <task> for <project>:
<what happened in 1–2 sentences with concrete numbers — "took 4 turns", "had to re-read 3 files", "asked the user X then Y then Z">
Resolution: <how fixed / abandoned / worked around>
Proposed home: <tool fix: <exact change> + drift check | revises <file> | case of principle_<slug> | bucket gotcha (<bucket>) | new principle | new gate>
```

The **Proposed home** line applies the write gate (Pass 2) up front, so the user's triage also settles *where* the lesson lands. Most lessons are a case of an existing principle — say which one.

Present nominations to the user. The user triages each:
- **pattern-worthy** → save it where its proposed home says (it then joins the normal memory flow in Pass 2)
- **one-off** → discard, don't pollute memory
- **stream-relevant** → route to Step 2 (the workflow stream notes file is the right home, not general memory)

If no notable friction came up: say so and move on. Don't invent friction to fill the slot — empty is fine.

### Pass 2: Memory sweep (passive)

Now look at the rest of the session for anything else worth saving:

- New user preferences or feedback on how you worked (not already captured by Pass 1)
- Project status changes (started, completed, blocked, deployed) → the project's `project_<name>.md`, and the roster if its lifecycle changed (ask first)
- Decisions made that aren't obvious from the code
- Infrastructure or workflow discoveries
- Anything that would be useful context in the *next* session

**Write gate — decide each save's home BEFORE writing anything.** Run every candidate (Pass 1 pattern-worthy + Pass 2 finds) through these in order; the first match wins:

1. **Doesn't change a future decision?** → don't save it. A memory earns its place only if a later session would act differently because of it.
2. **Revises an existing lesson?** → edit that file in place and mark the old claim `superseded YYYY-MM-DD`. No new file, no new index line. A near-duplicate that *contradicts* the old one is a revision, not a duplicate — never drop it and never file it alongside.
3. **A case of an existing principle?** (the `principle_*.md` hubs in the memory dir) → write the topic file if the incident has detail worth keeping, then add **one** line to that hub's `## Cases`. **No `MEMORY.md` line.**
4. **A stack- or area-specific gotcha?** → topic file + a ≤200-char stub in its `MEMORY-gotchas-*.md` bucket.
5. **A new principle or a new gate?** → propose the exact `MEMORY.md` line to the user and write it only after their yes. Gates are the user's lines: never reword an existing gate without their yes either.

Every lesson keeps its **concrete incident** (what happened, where, with numbers) in the topic file — an agent-written moral is often wrong about the cause, and the incident is what lets a later session check it.

Save what passes the gate. If nothing new came up, say so.

**Why the gate exists** (see `CONVENTIONS.md`; it overrides Claude Code's built-in "add a pointer in MEMORY.md" default): `MEMORY.md` auto-loads under a 200-line / 25KB cap. A skill that adds one index line per lesson re-bloats it every few weeks, and whatever falls past the cap silently stops loading. The index holds only Gates and one line per principle hub. **Any stub MUST be one line, ≤200 chars, rule + terse pointer — the why/war-story/example lives in the topic file, never inline.**

---

## Step 2: Workflow Stream Notes (Conditional)

Check MEMORY.md for an `## Active Workflow Streams` section. If absent or empty: skip this step silently.

If streams are listed: for each stream, check whether this session touched the project tagged as the in-progress iteration vehicle (the `Iteration N: <project-dir> — in progress` lines under the stream). If no project from this session matches: skip silently.

**If a match:**

### 2a. Append to running iteration notes

Append to `<workspace_root>/docs/workflow-streams/<stream>/iteration-<N>-notes.md` (create it if missing — **never overwrite**, always append).

If the file is being created for the first time, write this header:

```
<!-- project: <abs/path/to/project> -->
# Iteration <N> notes — <stream>

Raw observations accumulating across sessions. The synthesis subagent produces iteration-<N>.md when the iteration closes.
```

Then append the session block:

```
## Session: <YYYY-MM-DD HH:MM> · <project>

### Stream-relevant friction
<nominations from Step 1 Pass 1 tagged stream-relevant — verbatim, including the [category] header and Resolution line>

### Observations (not friction)
<decisions, dead-ends, surprising successes — anything that informs the workflow being broken in. Skip the section entirely if nothing fits.>
```

### 2b. Ask whether the iteration is complete

> "Is iteration N of \<stream\> complete?"

- **No** (default — iterations span many sessions): stop here. Notes accumulate.
- **Yes**: spawn the iteration synthesis subagent (prompt below). It produces `iteration-<N>.md` (shape: `templates/workflow-stream/iteration-N.md`). The notes file stays for audit. Update MEMORY.md: change that iteration's status from `in progress` to `complete`. If the next iteration's project is already known, ask the user and set it to `in progress`; otherwise leave it `TBD`.

### 2c. If the iteration just completed was the target one (default: the 3rd)

> "Extract the hardened pattern from all \<N\> iterations?"

If yes: spawn the hardening subagent (prompt below). It drafts `HARDENED.md`. The user reviews. On approval:
- Move the stream folder to `<workspace_root>/docs/workflow-streams/_archived/<stream>/`
- Remove the stream from MEMORY.md `## Active Workflow Streams`
- `HARDENED.md` is now the canonical reference; future memories link to it

### Iteration Synthesis Subagent Prompt

Dispatch with the `Agent` tool, `subagent_type: general-purpose`:

```
Synthesize iteration <N> of workflow stream "<stream>" into a structured writeup.

Read in order:
1. docs/workflow-streams/<stream>/goal.md — north star, what we're breaking in
2. docs/workflow-streams/<stream>/iteration-<N>-notes.md — raw notes accumulated across sessions
3. Prior iterations: iteration-1.md ... iteration-<N-1>.md (if any exist)

Produce docs/workflow-streams/<stream>/iteration-<N>.md with exactly these sections:

- **Project used as iteration vehicle:** which project this iteration ran on, and why it was chosen
- **What we applied from prior iterations:** validated practices that showed up again (one bullet each)
- **What was new this iteration:** attempts not in prior iterations or the goal
- **What worked:** validated by this iteration's outcome, with the concrete evidence
- **What broke or felt wrong:** concrete friction with examples from the notes. Cite friction notes verbatim — do not paraphrase
- **What we'd test next iteration:** specific hypotheses to probe in iteration <N+1>
- **Hardening confidence:** for each major aspect of the goal, mark CONFIRMED / REFUTED / NOT EXERCISED, with a one-line justification
- **Per-sub-dimension confidence (only if goal.md has a `## Sub-dimension ledger`):** a separate CONFIRMED / REFUTED / NOT EXERCISED call per tracked sub-dimension. Skip this section if no ledger exists.

Concrete observations beat generalizations. If the notes have 7 session entries, the writeup should reflect 7 sessions' worth of detail, not collapse it.

STOP AND REPORT after writing the file. Do not edit MEMORY.md (the parent agent handles that), do not start HARDENED.md synthesis, do not propose changes elsewhere.
```

### Hardening Subagent Prompt

Dispatch with the `Agent` tool, `subagent_type: general-purpose`. Only after the target iteration count is reached:

```
Extract the hardened workflow pattern from stream "<stream>" after <N> iterations.

Read:
1. docs/workflow-streams/<stream>/goal.md
2. iteration-1.md ... iteration-<N>.md (in order)

Produce docs/workflow-streams/<stream>/HARDENED.md with these sections:

- **Goal recap:** what we set out to harden, 1–2 sentences
- **The pattern:** concrete procedure / checklist / decision tree — the reusable thing future projects will reference. This is the load-bearing section
- **Validated across:** the <N> projects/contexts it ran in, one line each
- **Confirmed invariants:** what held in all <N> iterations
- **Known edges:** places it didn't hold or wasn't tested
- **When NOT to use:** counter-cases discovered across iterations
- **Open questions:** what these iterations couldn't answer

The output is the canonical reference. Future sessions cite this file, not the iterations.

STOP AND REPORT after writing the file. Do not propose archive moves, do not edit MEMORY.md, do not propose follow-on streams.
```

---

## Step 3: Resume-Note Check (Conditional)

Parallel sessions make it easy to lose track of what's unfinished where. After memory and stream notes are saved, decide whether this session leaves work the user needs to resume later.

> Is there work-in-progress that wouldn't surface on its own — something the user would forget about until it bites them?

Examples that **need a resume entry**:
- A PR is open but blocked, partially reviewed, or stacked behind something else
- A plan was started but only N of M tasks shipped (resume pointer needed)
- A debugging thread paused mid-investigation with a clear next step
- A decision was deferred to "next session" / "after X happens"
- An external dependency (DNS, a reply from someone, a deploy webhook) needs follow-up

Examples that **don't** — skip the step:
- The session wrapped cleanly, the feature is live, nothing pending
- A bug fix was committed and verified
- The user explicitly closed out the work ("done", "shipped", "moving on")

If there's unfinished work, tell the user what you'd write and ask where it goes (a `Todo.md` in the workspace root, an issue tracker, a notes file). Offer to append a single bullet under that project's section:

```
- [ ] <one-sentence summary> — <state: what's done, what's next>. <resume pointer: file path, PR #, plan path>.
```

**Be specific.** "Continue project X" is useless six sessions from now. "3 of 30 tasks done, next is Task 4 <component>, resume prompt at `tmp/<project>-resume.md`" is what cold-you needs.

If nothing fits: skip without asking.

---

## Step 4: Todo Sweep (if a todo file exists)

If the user keeps a flat todo file, tidy it so the active list stays glanceable. Runs every time, whether or not Step 3 added an entry. Skip if no such file exists.

1. Read the file. If no `## Done` section exists yet, append one at the bottom (`## Done` on its own line, preceded by a blank line).
2. Find all `- [x]` bullets that appear *before* the `## Done` heading.
3. Move each ticked bullet to the bottom of `## Done`, preserving the line verbatim — do not reformat or add dates (rewriting risks corrupting the completion context already inline).
4. **Remove now-empty one-off sections** (optional convention): if you group one-off items under `## <project> / <item>` headings (containing `/`), remove any such heading whose block has no `- [` lines left. Top-level project headings and `## Inbox` / `## Done` are never removed. The Step 7 git diff is the safety net.
5. Save the file.

**Edge cases:**
- Multi-line bullets: move the whole bullet including continuation lines, stopping at the next `- [` or blank line.
- Nothing ticked and nothing empty: no-op. Don't touch the file. Stay silent.
- If anything moved, report briefly: *"Swept N completed item(s) into ## Done."* (plus *"Removed N empty section(s): X, Y."* if any).

---

## Step 5: CLAUDE.md Check (Optional)

> Did this session reveal something that belongs in a **project's CLAUDE.md** — a workflow change, architectural decision, new convention, or discovered constraint?

If **yes**: tell the user what you'd add and ask: **"Update CLAUDE.md too?"** If yes, edit it concisely: capture *why* and how things connect, not what `grep` can answer. CLAUDE.md is for stable principles; project status and recent decisions go in a topic file instead.

If **nothing significant**: skip this step entirely without asking.

---

## Step 6: Domain Allowlist Sync (Optional — only if you keep a domain registry)

Skip silently unless you run Claude Code's Bash sandbox with a network allowlist AND keep a registry of the remote sites your sessions reach (e.g. a TSV of `domain  project  last_used`) from which that allowlist is derived.

1. **List this session's hosts** — live sites reached with `curl`, `wget` or a project script. If none: skip.
2. **Update the registry**: set `last_used` to today for known hosts; for a new host, propose the row and add it only after the user's yes.
3. **Dry-run your sync script** and show what would be added or pruned.
4. **Hand the apply command to the user** as a single line to run themselves. Never apply it yourself: widening your own sandbox allowlist is the user's call, and Claude Code's auto mode refuses agent self-modification of its settings anyway.

---

## Step 7: Git Check

Runs LAST so it catches changes from the sweep, memory writes, workflow-stream notes, the domain registry and any CLAUDE.md edits.

Run `git status` on every project directory touched this session, plus the repo that holds the memory dir (the starter repo, if memory is symlinked into it), the todo file's repo, and the workspace root (if workflow-stream notes were written). If unsure which projects were touched, scan the Active section of the roster.

**Clean-memory-repo trap.** If memory writes were already committed mid-session, a clean memory repo despite remembered memory edits is the NORMAL state, not a discrepancy. Confirm with `git log --since=<session start> -- <memory path>` if unsure; don't spend turns hypothesising auto-commit hooks.

For each project with uncommitted changes:
- Show the user what's uncommitted
- Ask: **"Commit before clearing?"**
- If yes: invoke the `commit` skill
- If no: warn them the changes will still be there but uncommitted — their call

If nothing is uncommitted: say so and move on.

---

## Done

Tell the user: **"All clear — safe to /clear."**

---

## Opening a Workflow Stream

Separate from the per-session flow. Run this when the user wants to systematically break in a new workflow across several projects. **Why streams exist:** a workflow designed up front and turned into a template after one run bakes in that run's accidents. Patterns harden through repetition: run it on ~3 real projects, record what held and what broke each time, and only then extract the reusable version.

1. **Pick a slug.** Kebab-case, descriptive (e.g. `content-first`, `release-checklist`).
2. **Create the folder:** `<workspace_root>/docs/workflow-streams/<slug>/`, copying `templates/workflow-stream/goal.md` from the starter repo.
3. **Fill in `goal.md`**: what we're breaking in, why now, success criteria (concrete enough to know when it's done), target iteration count (default 3), out-of-scope notes. **Get the user's sign-off on `goal.md` before iteration 1 starts.**
4. **Append to MEMORY.md** `## Active Workflow Streams` using the schema below.
5. **Tag the iteration-1 project:** in its `project_<name>.md`, note "iteration 1 of \<stream\> stream". Step 2 picks it up from then on.

### MEMORY.md schema

```
## Active Workflow Streams

- **<slug>** (<completed>/<target>): [goal](file:///abs/path/goal.md)
  - Iteration 1: <project-dir-name> — <complete | in progress | TBD>
  - Iteration 2: <project-dir-name> — <complete | in progress | TBD>
  - Iteration 3: <project-dir-name> — <complete | in progress | TBD>
```

`<project-dir-name>` MUST match `basename` of the project directory — that's what Step 2 matches against.

### Sub-dimensions (optional — decide at stream-open time)

Sometimes a stream hardens **two things in parallel**: the general workflow AND a per-context starter (per stack, per language). The parent `(N/target)` count tracks the general workflow only. If the user identifies parallel tracks, add a ledger to `goal.md`:

```
## Sub-dimension ledger

| Sub-dimension | Count | Notes |
|---|---|---|
| <name> | N/target | <which iterations covered this> |
```

The synthesis subagent then gives per-sub-dimension confidence, and the hardening subagent can distinguish "workflow confirmed" from "starter for X ready". Default is no ledger; don't force one onto a stream that hardens one thing.
