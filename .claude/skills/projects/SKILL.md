---
name: projects
description: "Orient in the workspace — resolve a project name to its folder, memory file, stack and current status by routing to the PROJECTS.md roster. Use when a project is mentioned and you need to know which one it is, whether it's active, what stack it runs, or which gotcha bucket applies. Do NOT use for project-specific technical detail (read that project's own CLAUDE.md), for code implementation, or for deployment troubleshooting."
---

# projects — workspace router

This file owns *how to resolve a project*, never *the project list itself*.

## The one rule

**The roster file is the single source of truth.** Its path is `roster_file` in `~/.claude/hooks/starter-config.json` (default: `PROJECTS.md` in the workspace root). Read it live. Never answer a roster question — which projects exist, what's active, what stack, what's next — from memory, from this file, or from a previous session's recollection.

> **Why this skill contains no project list:** a copy of the roster inside a skill rots silently. It keeps telling agents that a project is "awaiting setup" months after it went live, and names projects that no longer exist. A duplicated roster is worse than none, because it looks authoritative. Do not add one here.

## Procedure

1. **Read the roster** and match the user's words against it. It is grouped Active / Maintenance / Archived; each entry carries a status and a `→ project_<name>.md` pointer where a memory file exists.
2. **Read that `project_<name>.md`** from the memory dir before responding.
3. **Announce what you loaded** as the first line of your reply: `Loading memory: <files>`.
4. **Read the project's own CLAUDE.md** once you're working inside its folder — it outranks anything here.
5. **Load the matching gotcha bucket** for the project's stack (see the load table in the workspace CLAUDE.md).

If the name is ambiguous, **ask** — don't guess which project is meant.

## Freshness

The roster's lifecycle grouping is hand-maintained and drifts. `scripts/projects.sh` audits it against real git activity; `scripts/meta-health.sh` lints naming and orphaned memory files. If the roster contradicts what you can see in the repo, trust the repo and say so — don't silently reconcile.

## Confirm before acting — the user's call, not yours

- **Moving an entry between Active / Maintenance / Archived** is a deliberate lifecycle edit, never per-session churn. Ask.
- **Concluding a project is dead.** A memory file missing from the roster is not evidence of death; it is far more often a project that was never filed. Re-file it, don't archive it.

## Do NOT use this skill for

- Project-specific technical detail → that project's CLAUDE.md
- Code implementation → the project's own stack skills
- Deployment troubleshooting → your deploy/infra skills
- Saving or routing memories → `memory/CONVENTIONS.md`
