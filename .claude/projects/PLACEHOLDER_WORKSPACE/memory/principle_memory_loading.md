---
name: principle_memory_loading
description: "Hub — when a project, stack, topic or skill comes up, load and apply its memory before acting; links every loading/recall lesson"
type: feedback
tags: [claude-code]
---

# Memory & context loading

This file owns the memory-loading principle and every incident filed under it.

**When:** a project, stack, infra/git topic or skill enters the session — especially when a session escalates from talk to implementation, or a skill takes over the flow.

**Principle:** memory only helps if it is Read at the moment it applies and then used as a checklist. Nothing auto-recalls topic files; a bucket is invisible until something Reads it. The load table in `CLAUDE.md` is the mechanism; this hub holds the lessons about where it leaks.

**Sharpest warning signs** (mirrored in `MEMORY.md`):
- stack/topic work → Read the matching bucket, and apply it as a checklist before saying done
- a bucket stub ≠ the topic file — open the topic file before operating on the named thing
- a skill can mask a bucket trigger — the skill loads its bucket as an explicit Step 0

**Also watch for:**
- a topic-keyed bucket (git, infra) must load even when no project is named
- a session that escalates from discussion to implementation needs the buckets it skipped
- a project's own repo CLAUDE.md before the first write, not just its memory file
- a project memory file that has grown past the Read tool's page size — a partial read is page 1 only; grep by section, then archive old parts
- memory saying "do it manually / in the UI" is a constraint, not a preference — don't script around it
- running a skill means running its flow and scripts, not reading its docs
- a memory note saying "check X before continuing" is a gate: clear it when resuming, then write the answer back
- applying a change to project B that came from project A — update A's memory too

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — a rule filed in the wrong bucket recurred for months** - "open memory files with Read, not cat" sat in the meta-work bucket, but it fires during project work, which never loads that bucket. Moved the firing part to CLAUDE.md
- *Add your own incidents here.*
