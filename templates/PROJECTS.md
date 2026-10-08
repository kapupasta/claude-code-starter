# Workspace Projects — roster & router

This file owns the list of every project in the workspace. It is the **on-demand** roster: `MEMORY.md` (always loaded) only points here. When a project is named, Claude reads this file to resolve it, then reads its detail file. Copy it to your workspace root (or wherever `roster_file` in `~/.claude/hooks/starter-config.json` points).

- **Detail per project:** `project_<name>.md` in the memory dir, where one exists, marked `→ project_<name>.md` below. That file owns the project's deep, volatile status; keep the line here short.
- **Lifecycle grouping** (Active / Maintenance / Archived) is set **by hand**, only when a project changes phase — a rare, deliberate edit confirmed with the user, never per-session churn.
- **Freshness** (is it actually still being worked on?) is **derived, not hand-maintained**: `scripts/projects.sh` reads each project's git history and flags an Active project idle for 30+ days, or a Maintenance project touched recently. It only reports; you decide.

**Line format** (the scripts parse it — keep the ` — ` separators):

```
- <name> — <path> — <status> → project_<name>.md
```

`<path>` is relative to the workspace root, absolute, or `~/…`; wrap it in backticks if you like. Write `no folder` for a project without a local directory. Leave off the `→` part if there is no memory file yet. Name and folder: ASCII, lowercase, `kebab-case`.

---

## Active

In flight: open work, a pending launch, a planned next phase, or an exploration awaiting a decision.

- example-app — `example-app/` — in development, v1 feature branch open (add the arrow once its memory file exists)

## Maintenance

Shipped / live / low-churn, no open task. Move to Active when work resumes, to Archived when fully retired.

- example-site — `example-site/` — live, occasional content updates

## Archived

Cancelled or throwaway only — killed projects, test repos. **Not** "old" or "done": project knowledge usually stays useful, so finished work goes to Maintenance and stays there. Archiving is rare.
