# CLAUDE.md

Workspace operating principles. Loaded into every Claude Code session in this directory.

This file is **stable** — the things that don't change session-to-session. Current state, project status, and ongoing context live in MEMORY.md and topic files.

---

## How memory works in this workspace

You have two parallel persistence layers:

1. **CLAUDE.md (this file)** — workspace-wide rules. Read every session.
2. **`memory/` directory** — file-based memory at `~/.claude/projects/<workspace-slug>/memory/`, symlinked into this repo so it's version-controlled.

The `memory/` directory has three layers:

```
memory/
├── MEMORY.md                    ← master index. Always loaded. Keep < 200 lines.
├── CONVENTIONS.md               ← tag vocabulary + save-time rules.
├── MEMORY-gotchas-<topic>.md    ← per-stack indexes (frontend, backend, infra...).
├── feedback_<topic>.md          ← topic files: lessons, corrections, validated approaches.
├── project_<name>.md            ← per-project context.
├── reference_<thing>.md         ← pointers to external systems (dashboards, repos, docs).
├── user_<topic>.md              ← user profile facts.
└── archive/                     ← obsolete topic files. Move here, don't delete.
```

**Indexes (MEMORY.md, MEMORY-gotchas-*.md) are read-mostly.** They contain one-line pointers, not content. Keep them lean.

**Topic files are write-mostly.** Each one is a single fact, lesson, or context block, with frontmatter (`name`, `description`, `type`, `tags`).

When something is worth remembering: write a topic file AND add a one-line stub in every matching index. Never dump content directly into MEMORY.md.

---

## Memory loading rules

When you start a session in this workspace:

1. **Always-loaded:** `MEMORY.md` (it's the index, kept short on purpose).
2. **Identify the project** from the user's first substantive message. Match against MEMORY.md's *Active Projects* list.
3. **Load on demand** before responding:
   - `project_<name>.md` for the matched project
   - `MEMORY-gotchas-<stack>.md` for the project's tech stack

**Visible loading announcement (mandatory).** First line of any project-scoped response:

```
Loading memory: <comma-separated list of files Read>
```

If you say nothing, you loaded nothing — that's a bug, and the user needs to see it immediately. The `memory-load-check.py` hook backstops this: 3 soft warnings, then a hard block.

If a recalled memory conflicts with what you observe in the code now, **trust what you observe** and update the memory. Files rot; checking is cheap.

---

## Saving memory

When the user gives feedback, corrects you, or you learn a non-obvious fact about the project:

1. Write a topic file with frontmatter (see `memory/CONVENTIONS.md` for the format).
2. Add a one-line stub to each matching `MEMORY-gotchas-*.md` index.
3. If it's a new active project, add an entry to MEMORY.md's *Active Projects* section.

Tags are a **closed vocabulary**. Adding a new tag means editing `CONVENTIONS.md` first.

**What NOT to save:**
- Code patterns, architecture, file paths — `grep` answers those.
- Recent changes, who-did-what — `git log` is authoritative.
- Bug fixes — the fix is in the code; the commit message has the why.
- Anything already in this CLAUDE.md.

If a user asks you to save something you know is grep-answerable, push back: ask what was *surprising* or *non-obvious* about it. That's the part worth keeping.

---

## Active hooks in this workspace

- **`guard-scope.py`** — blocks Read/Write/Edit/Bash that target paths outside the workspace, `~/.claude`, `~/.config`, or `/tmp`. Forces explicit user permission for anything else.
- **`memory-load-check.py`** — soft-warns 3× then hard-blocks if a project name appears in the transcript but no `project_*.md` or matching gotcha bucket has been Read this session.
- **`save-session-summary.sh`** — saves the auto-compact summary to `memory/sessions/<date>.md` so context survives `/compact`.

---

## Workspace skills

Available via the Skill tool — invoke proactively when the description matches:

- **`pre-clear`** — five-step checklist before `/clear`: git status sweep, memory review, optional resume note, optional CLAUDE.md update. **Run this every time.** Without it, work and context leak between sessions.
- **`prune`** — reduce-only edits to CLAUDE.md or MEMORY.md. Removes duplication and stale content. Never restructures or rewrites — that's a separate task.
- **`commit`** — branch + remote + junk-file pre-flight before any git commit. Catches the most common git mistakes (wrong branch, wrong repo, `.DS_Store` in staging).

---

## CLAUDE.md vs MEMORY.md — what goes where

| CLAUDE.md (here) | MEMORY.md + topic files |
|---|---|
| Operating principles that don't change | User profile + standing preferences |
| The memory system itself | Project list with current status |
| Tooling rules (commit style, when to ask) | Per-project context (`project_*.md`) |
| Hook + skill inventory | Per-stack gotchas (in `MEMORY-gotchas-*.md` buckets) |

If you're tempted to add current-state info to CLAUDE.md (a deadline, a project status, an in-flight decision) — redirect it to a topic file plus a MEMORY.md index entry. CLAUDE.md must stay stable.

---

## TODO: Customize this for yourself

The sections above are universal — they describe how the substrate works. The sections below are yours to write. Delete this TODO marker once you've filled them in.

### Your role

<!-- Examples:
- Senior backend engineer, 8 years Python/Go.
- Solo founder building <X>. Need pragmatic guidance, not academic correctness.
- Architect, not implementer — explain things in plain language.
-->

### Standing preferences

<!-- Examples:
- Prefer pnpm over npm.
- Always use feature branches before opening a PR.
- EU-based / open-source tools first; proprietary US-cloud only as a last resort.
- Don't ask before reading files. Always ask before running shell commands.
-->

### Workflow rules

<!-- Examples:
- Question and clarify before acting on anything ambiguous.
- Plan before implementing — show files to touch, what each change does, side effects, risks.
- Never push to remote without explicit confirmation.
- Coach, don't dump errors — explain breakage and the fix in plain language.
-->

### Token / process rules

<!-- Examples:
- Suggest /clear when context gets heavy.
- Recommend Haiku for quick tasks, Sonnet for medium, Opus for deep reasoning.
- Batch related changes — header + footer + layout in one pass, not three prompts.
-->
