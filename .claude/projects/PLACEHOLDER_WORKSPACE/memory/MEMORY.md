# Workspace Memory

This file owns the always-loaded memory index. Claude Code auto-loads only its first 200 lines OR 25KB, whichever comes first, so every entry is one line (≤200 chars): rule + pointer, never content. Save-time routing: [`CONVENTIONS.md`](./CONVENTIONS.md).

---

## Active Projects

The roster lives in `PROJECTS.md` at the workspace root (path: `roster_file` in `~/.claude/hooks/starter-config.json`). **On a project mention, Read the roster to resolve the name → `project_<name>.md`, then Read that file.** Freshness audit: `scripts/projects.sh`.

## Active Workflow Streams

Workflows harden over ~3 iterations before a template is extracted. Folder: `docs/workflow-streams/<slug>/` in the workspace root. Opened and fed by the `pre-clear` skill.

<!-- Schema (one block per stream; delete this comment when you add the first):
- **<slug>** (<completed>/<target>): [goal](file:///abs/path/docs/workflow-streams/<slug>/goal.md)
  - Iteration 1: <project-dir-name> - complete
  - Iteration 2: <project-dir-name> - in progress
  - Iteration 3: TBD
-->

## User Profile

<!-- Facts about you that shape how Claude collaborates with you. One line each. Examples:
- Architect, not developer - has the vision, needs viability checked and plain-language explanations
- Primary interface is the Claude Code CLI
- Privacy-conscious - no personal details on public-facing sites
-->

## Standing Preferences

<!-- Universal preferences that apply to every project. One line each, link a topic file if there's a why. Examples:
- Path of least friction is the #1 design rule - don't add automation that costs more than it saves
- Clarify more, in prose - ask when the possible answers diverge, stop when they don't
- Open-source / local-first tools as a tiebreaker, not a purity test
-->

## Gates
The user's lines. Never merged into a principle, never reworded without the user's yes. (Examples shipped from a real setup; keep, edit or delete.)
- **CARDINAL - never assume: fact-check or flag** - verify with a tool, doc, test or source, or label the claim a guess, even in conversation
- **CARDINAL - docs before assuming, always** - read the authoritative doc verbatim (the raw file, not a summary) before stating how a tool behaves
- **CARDINAL - never guess past an ask-gate** - publish/privacy/send/delete gates outrank a "reasonable guess"; if it isn't explicitly cleared, ask
- **CARDINAL - never circumvent a rule yourself; ask if it should be amended** - noticing friction is welcome, the line is the user's to draw
- **CARDINAL - survey existing tools before designing a new one** - search our own repos and open issues in the same pass as any vendor sweep
- **CARDINAL - `git fetch` every repo the task touches, before editing, releasing or reading-to-design** - never assume a repo has no other writers
- **Nothing is final until the user says so** - "looks good" on a proposal is a lock; silence after a question is not
- **Credentials → the user's password manager + a gitignored per-project `.env`** - the user fills it; the agent never writes, prints or exports a secret
- **Stay inside the workspace** - no reading or copying outside the allowed roots without permission
- **Archive, don't delete** - obsolete memories move to `archive/`
- **High-stakes, low-frequency steps stay manual** (migrations, DNS, certificates) - the agent walks the user through them instead of scripting them

## Principles
Each hub holds its trigger, the rule, warning signs and its cases. Open the hub when its trigger fires. A new lesson that is a case of a hub goes in the hub; this file gets a line only for a new principle or gate, after the user's yes.
- **[Prove the check](./principle_prove_the_check.md)** - before saying done/fixed/clean/passing/none: the check must be able to fail, and must test the real thing
  - a pass counts only if you've seen that check fail; a sample proves presence, never absence
  - verify by content, not count; deployed ≠ local - check the live artifact
- **[Facts from source](./principle_facts_from_source.md)** - before stating how a tool, vendor, version or bug behaves: primary source, or drive it
  - effect = fact, cause = inference; tag findings VERIFIED (+evidence) / INFERRED / ASSUMED
  - stuck/slow/not firing → check CPU, then trigger-vs-action, before theorising
- **[Ask, don't guess](./principle_ask_dont_guess.md)** - when the answer is the user's or an account owner's: ask
  - answer the literal question first; if the user has the console, have them read it
  - a blanket "go" doesn't clear your own earlier doubts; park deferred ones as an issue/todo
- **[Scope before building](./principle_scope_before_building.md)** - before a spec, plan, build, template or UI: consumer, input purpose, cost multiple, risk order
  - changing a live system costs a multiple of greenfield - say the multiple at kickoff; split plans by risk
  - roll out N times before extracting a template; mark corner-cuts with ceiling + trigger
- **[Memory & context loading](./principle_memory_loading.md)** - when a project, stack, topic or skill comes up: load its memory before acting
  - stack/topic work → Read the matching bucket, apply it as a checklist before done
  - a bucket stub ≠ the topic file; a skill can mask a bucket trigger - load it as Step 0
- **[Subagents & parallel work](./principle_subagents_parallel.md)** - when dispatching agents or sharing a working tree
  - bound each agent's files and waits; verify its output yourself, not its report
  - parallel writers in one tree collide silently - stage exact paths and check the commit's file count
- **[Fix the tool before the rule](./principle_fix_the_tool_first.md)** - when the same error/block/retry hits twice: remove it at the source → make the tool catch it → only then write a rule
  - the user is the gate for every install/setting/hook; propose your-side fixes to fences first; the fix must cost < the friction
- **[Workspace hygiene](./principle_workspace_hygiene.md)** - scratch, links and drift-prone state go where the next session expects them
  - drift-prone state belongs in a script that checks it, not in prose

## Universal Gotchas & References
Stack- and topic-specific stubs go in their `MEMORY-gotchas-*.md` bucket, not here. Only rules that fire regardless of stack, with no bucket home, get a line.
- Bucket example: [`MEMORY-gotchas-EXAMPLE.md`](./MEMORY-gotchas-EXAMPLE.md) - rename to your first real stack
<!-- Format: - [Short title](feedback_topic.md) - rule in one line -->
