# Memory Conventions

This file owns the save-time rules: where a new memory goes, its frontmatter, the closed tag set and file naming. Read it only when **saving** a memory or **editing tags** on one. It overrides Claude Code's built-in "add a pointer to MEMORY.md" default.

## Why routing matters

Only `MEMORY.md` auto-loads each session, and only its first 200 lines OR 25KB, whichever comes first ([docs](https://code.claude.com/docs/en/memory)). There is **no** automatic recall that scans topic files by description: a topic file is invisible until something Reads it. So:

- an index line per lesson re-bloats `MEMORY.md` within weeks, and whatever falls past the cap silently stops loading;
- a stub filed in a bucket is only useful if that bucket's load trigger reliably fires *when the rule is needed*.

## Routing table — where the one-line stub goes

Write the topic file first, then route its stub. The first matching row wins.

| The memory is… | Stub goes in | Not in |
|---|---|---|
| Doesn't change any future decision | nowhere — don't save it | |
| A revision of an existing lesson (incl. a contradicting near-duplicate) | edit that file in place, mark the old claim `superseded YYYY-MM-DD` | a new file alongside |
| A case of an existing principle | one line in that `principle_*.md` hub's `## Cases` | `MEMORY.md` |
| Stack- or area-specific (carries a stack or knowledge-area tag) | EACH matching `MEMORY-gotchas-*.md` bucket | `MEMORY.md` |
| A tool / vendor eval verdict ("should we use X?") | one evals bucket (e.g. `MEMORY-evals.md`), whatever the subject | split by subject |
| An environment invariant (true on every session from the first Bash/Edit call: shell quirks, missing binaries, tool gates) | the `Environment invariants` section of the workspace `CLAUDE.md`; the bucket keeps the depth | a bucket alone — no trigger fires early enough |
| A project | an entry in the roster (`PROJECTS.md`), Active section; the detail lives in `project_<name>.md` | `MEMORY.md` |
| A new principle or a new gate | a `MEMORY.md` line — **only after the user's yes** | |

**The always-on test.** Before bucketing a cross-cutting rule, name the session type where it must fire, then confirm that session type loads the bucket. A rule about "how to open memory files" filed in a meta-work bucket never fires during project work, which is where it's needed. If no bucket loads in time, the firing part goes in an always-loaded file and the bucket keeps the reference. An area with a tag but no bucket file + trigger keeps its stubs in `MEMORY.md` rather than stranding them.

## What `MEMORY.md` holds

- **Gates** — the user's own hard lines (never-assume, ask-gates, credentials, scope, archive-don't-delete). Never merged into a hub, never reworded without the user's yes.
- **Principles** — one line per hub + at most 3 indented warning-sign sub-lines (the cues that make it fire).
- Pointers: roster, active workflow streams, user profile, standing preferences, a few universal references.

`MEMORY.md` is agent-facing. Optimise it for token cost and parsing, not for human scanning.

## Stub rule

**A stub is ONE line, ≤200 characters: the rule + a terse pointer.** The why, the war story, the example and the dates live in the topic file, never inline in an index. When `scripts/meta-health.sh` reports the index over its soft limit or a stub over 200 chars, the fix is a **compaction pass** (move detail to the topic file, keep rule + pointer) — never raising the threshold.

## Frontmatter

Every topic file starts with:

```markdown
---
name: <short identifier>
description: <one line used to judge relevance later — be specific>
type: <user | feedback | project | reference>
tags: [<tags from the closed set below>]
---
```

Body for `feedback` and `project` types:

```
<the rule or fact, stated plainly>

**Why:** <the reason — usually the concrete incident: what happened, where, with numbers>
**How to apply:** <when this kicks in, and what to do>
```

Keep the **concrete incident**. An agent-written moral is often wrong about the cause; the incident is what lets a later session check it.

## Principle hubs

`principle_<slug>.md` (`type: feedback`) — sections: **When** (the trigger), **Principle**, **Sharpest warning signs** (mirrored as sub-lines in `MEMORY.md`), **Also watch for**, `## Cases` (one line per incident, linking its topic file when there is one). A new hub is a new principle, so it needs the user's yes.

## Tag vocabulary (closed set)

Adding a tag means editing this section first. A file may carry several tags; multi-tagged files appear in several buckets on purpose.

- **Tech-stack** (example list — replace with what you actually use): `python`, `node`, `react`, `static-html`, `wp`
- **Knowledge area:** `css`, `accessibility`, `security`, `git-gh`, `claude-code`, `infra`, `gotcha`
- **Project lifecycle:** *not a tag.* It lives in the roster's sections (Active / Maintenance / Archived), the single source of truth. Moving a project between sections is a deliberate edit, confirmed with the user.

## File and folder naming

ASCII, lowercase, no spaces — everywhere. Transliterate accented letters (`ä→a`, `é→e`).

- **Topic files:** `snake_case` with a type prefix — `project_`, `feedback_`, `reference_`, `infra_`, `user_`, `principle_`. The `project_<name>.md` slug match depends on `_`.
- **Project directories:** `kebab-case`.
- **Index files** keep their uppercase names (`MEMORY.md`, `MEMORY-gotchas-*.md`, `CONVENTIONS.md`, `PROJECTS.md`) and are exempt.

Why: non-ASCII characters, spaces and capitals break filename matching (macOS stores filenames NFD, typed text is NFC) and slug derivation in hooks and scripts. `scripts/meta-health.sh` check [5] lints offenders.

## What NOT to save

These exclusions apply even if asked. If the user insists, ask what was *surprising* or *non-obvious* — that's the part worth keeping.

- Code patterns, architecture, file paths — `grep` answers those.
- Git history, who changed what — `git log` / `git blame` are authoritative.
- The fix itself — it's in the code; the commit message has the why.
- Anything already in CLAUDE.md.
- Ephemeral task state — in-progress work belongs in a todo/resume note, not memory.

## Archive, don't delete

An obsolete topic file moves to `archive/`. Remove its stubs from the indexes in the same edit.
