---
name: pre-clear
description: "Run before /clear — checks git status, saves memories, optionally updates CLAUDE.md. Prevents losing work and context between sessions."
---

# Pre-Clear Checklist

Run this before every `/clear`. Five steps, in order.

---

## Step 1: Git Check

Run `git status` on every project directory that was touched this session. If unsure which were touched, scan the active projects listed in MEMORY.md.

For each project with uncommitted changes:
- Show the user what's uncommitted
- Ask: **"Commit before clearing?"**
- If yes: invoke the `commit` skill
- If no: warn them the changes will still be there but untracked — their call

If nothing is uncommitted: say so and move on.

---

## Step 2: Memory Review

Review the full conversation. Look for anything that should be saved to memory:

- New user preferences or feedback on how you worked
- Project status changes (started, completed, blocked, deployed)
- Decisions made that aren't obvious from the code
- Infrastructure or workflow discoveries
- Anything that would be useful context in the *next* session

Check existing memory files first — update stale entries rather than creating duplicates.

Save anything worth keeping per `memory/CONVENTIONS.md` (topic file + matching index stubs). If nothing new came up, say so.

---

## Step 3: Resume-Note Check (Conditional)

If the user runs many parallel sessions and loses track of what's unfinished where, a resume note is useful. Otherwise skip this step — most sessions wrap cleanly and don't need one.

Ask yourself:

> Is there work-in-progress that wouldn't surface on its own — something the user would forget about until it bites them?

Examples that **need a resume entry**:
- A PR is open but blocked, partially reviewed, or stacked behind something else
- A plan was started but only N of M tasks shipped (resume pointer needed)
- A debugging thread paused mid-investigation with a clear next step
- A decision was deferred to "next session" / "after X happens"
- An external dependency (DNS, client reply, deploy webhook) needs follow-up

Examples that **don't** — skip the step:
- Session wrapped cleanly, feature is live, nothing pending
- A bug fix was committed and verified
- The user explicitly closed out the work ("done", "shipped", "moving on")

If there's unfinished work, ask the user where they keep their open-loops list (a `Todo.md`, an issue tracker, a notes file). Offer to append a single bullet:

```
- [ ] <one-sentence summary> — <project path on disk> <branch if relevant>. <state: what's done, what's next>. <resume pointer: file path, PR #, plan path>. <follow-up issues if any>.
```

**Be specific.** "Continue project X" is useless six sessions from now. "3 of 30 tasks done, next is Task 4 <component>, resume prompt at `tmp/<project>-resume.md`" is what they need. Write it so cold-them can pick it up.

If there's no fitting target file, suggest creating one. If nothing fits the situation: skip without asking.

---

## Step 4: Todo Sweep (if a todo file exists)

If the user keeps a flat todo file (e.g. `Todo.md` in the workspace), tidy it so the active list stays glanceable. Skip if no such file exists.

1. Read the file. If no `## Done` section exists yet, append one at the bottom (`## Done` heading on its own line, preceded by a blank line).
2. Find all `- [x]` bullets that appear *before* the `## Done` heading.
3. Move each ticked bullet to the bottom of the `## Done` section, preserving the line verbatim — do not reformat or add dates.
4. Save the file.

**Edge cases:**
- Multi-line bullets: move the whole bullet including continuation, stopping at the next `- [` or blank line.
- No ticked items above `## Done`: no-op. Stay silent.
- If anything moved, report briefly: *"Swept N completed item(s) into ## Done."*

---

## Step 5: CLAUDE.md Check (Optional)

After saving memories, make a judgment call:

> Did this session reveal something that belongs in a **CLAUDE.md** — a workflow change, architectural decision, new convention, or constraint discovered?

If **yes**: tell the user what you think should be added and ask: **"Update CLAUDE.md too?"**

If **nothing significant**: skip this step entirely without asking.

Remember: CLAUDE.md is for stable principles, not current state. If the new info is project status or a recent decision, save it as a topic file instead.

---

## Done

Tell the user: **"All clear — safe to /clear."**
