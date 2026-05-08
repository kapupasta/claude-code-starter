# Memory Conventions

Save-time rules and tag vocabulary. Read this only when **saving** a new memory or **editing tags** on an existing one.

## Memory Saving Rules

When saving a new memory:

1. Write the topic file with frontmatter: `name`, `description`, `type`, `tags` (closed vocabulary — see below)
2. Add a one-line stub to EACH matching `MEMORY-gotchas-*.md` index (one stub per matching bucket)
3. If `type: project` AND `tags` includes `project-active`, also add an entry to MEMORY.md's *Active Projects* section
4. When marking a project released, change tags to include `project-released` and remove its entry from MEMORY.md's Active Projects list (topic file stays in flat memory dir for grep / Read)

When editing an existing topic file, verify `tags:` are still accurate; update bucket indexes if tags changed.

## Frontmatter Template

Every topic file starts with:

```markdown
---
name: <short identifier>
description: <one-line description used to decide relevance in future conversations — be specific>
type: <user | feedback | project | reference>
tags: [<comma-separated tags from the vocabulary below>]
---

<content>
```

For `feedback` and `project` types, structure the body as:

```
<the rule or fact, stated plainly>

**Why:** <reason — often a past incident, constraint, or strong preference>
**How to apply:** <when/where this guidance kicks in>
```

The *why* matters. Without it, future-you can't judge edge cases.

## Tag Vocabulary (closed set)

Adding a new tag requires updating this section first.

**Tech-stack:** <!-- Match what you actually use. Examples: `node`, `python`, `rust`, `react`, `wp`, `sveltekit` -->

**Knowledge area:** `gotcha`, `security`, `git-gh`, `claude-code`, `infra`

**Project state:** `project-active`, `project-released`, `project-archived`

**Memory type** (also in frontmatter `type`): `user`, `feedback`, `project`, `reference`

A topic file may have multiple tags. Multi-tagged files appear in multiple bucket indexes — that's intentional, not a duplication bug.

## What NOT to save

These exclusions apply even if the user asks you to save them. If the user insists, ask what was *surprising* or *non-obvious* — that's the part worth keeping.

- Code patterns, conventions, architecture, file paths — `grep` answers those.
- Git history, recent changes, who-did-what — `git log` / `git blame` are authoritative.
- Bug fix recipes — the fix is in the code; the commit message has the why.
- Anything already documented in CLAUDE.md.
- Ephemeral task details — in-progress work, temporary state, current conversation context.
