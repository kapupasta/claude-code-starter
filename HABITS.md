# Two habits that make this work

The starter wires up a memory directory, three hooks, and a pre-clear skill — but the wiring is inert without two small disciplines. Without them, the memory dir rots, the hooks fire as noise, and you end up with a system that's harder than no system. With them, context survives between sessions and the agent gets sharper over time.

You don't need to memorise the file structure or the tag vocabulary. You need these two habits.

---

## Habit 1: announce what you load

When you start a session and it touches a project, the agent's first line should be:

```
Loading memory: MEMORY.md, project_my-app.md, MEMORY-gotchas-frontend.md
```

That's it. A simple list of which files it Read.

**Why it matters.** The whole memory system is invisible by default — files get loaded silently, or not at all. When the agent says nothing, you have no way to know whether it's working from a real understanding of the project or making it up. The announcement is your only window into that. If it forgets to announce, you've spotted the failure before it costs you anything.

**You don't have to enforce it manually.** The `memory-load-check.py` hook does the enforcement: if you mention a project but no `project_*.md` was Read, you get three soft warnings and then a hard block on the next Edit/Write/Bash. The hook exists *because* announcement is critical, not as bureaucracy. When it fires, that's the system catching a real bug.

If the agent silently skips the announcement, prompt: *"What memory did you load?"* — that recalibrates it for the rest of the session.

---

## Habit 2: run /pre-clear before /clear

Before you `/clear`, run `/pre-clear`. Always. Even when the session feels small.

The skill walks five steps: git status sweep, memory review, optional resume note, todo sweep, optional CLAUDE.md update. Most steps will be no-ops most of the time — that's fine. The ones that aren't are the ones that would have lost you something.

**Why it matters.** Sessions accrete value in two places: the working tree (uncommitted code) and the agent's understanding (un-saved feedback, decisions, project status changes). `/clear` wipes the second silently and never warns about the first. Without `/pre-clear`, every clear is a small leak. Over weeks the leaks compound: you re-explain the same preferences, re-discover the same gotchas, re-debug the same issues.

The skill's job is to ask, before you wipe: *did anything happen this session that the next session needs?* Most of the time: no. But the times it's *yes* are the times you'd otherwise pay for it twice.

---

## What to expect in the first week

The system is designed to feel mostly empty at first. That's correct.

- **Days 1–3:** MEMORY.md has your profile and prefs, and not much else. Sessions feel like normal Claude Code with extra wiring. Pre-clear will mostly say "nothing to save" — that's right.
- **Days 4–7:** The first real lessons start landing. You'll correct the agent on something, or a project decision will be worth recording, or you'll hit a gotcha that isn't obvious from the code. Save it. The bucket files start to populate.
- **Week 2–3:** Pattern recognition kicks in. The agent loads a `project_*.md` and immediately knows the constraints you'd otherwise have to repeat. The friction of saving starts paying back the friction of repeating yourself.

**Resist the urge to pre-populate.** Don't sit down and try to write all your gotchas up front — you'll write generic stuff that doesn't survive contact with reality. Save when something is actually surprising or non-obvious, in the moment, with the *why* attached. That's what makes the memory worth loading later.

**Resist the urge to disable the hooks.** When `guard-scope.py` blocks a Bash command or `memory-load-check.py` warns you, the friction is the feature. The hook is asking "are you sure?" because the action is unusual — sometimes you are sure (then approve the call or load the memory it's asking for), sometimes you're not (then you've just dodged a mistake). Disabling them removes the safety, not the cause.

---

## When the system is working

Two signals. First: pre-clear regularly surfaces something you'd have forgotten — a half-finished PR, a deferred decision, a project status change. Second: when you mention a project by name, the agent's first message names files you don't remember writing — because past-you wrote them, and now they're paying off.

If neither happens after three weeks, the system isn't matching how you work. That's worth a conversation, not a workaround.
