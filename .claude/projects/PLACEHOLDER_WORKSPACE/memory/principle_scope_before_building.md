---
name: principle_scope_before_building
description: "Hub — before speccing or building, establish the consumer, what each input is for, the real cost multiple and the risk order; links every scoping lesson"
type: feedback
tags: [gotcha]
---

# Scope before building

This file owns the scoping principle and every incident filed under it.

**When:** you are about to write a spec or plan, start a build, extract a template, automate a runbook step, or design UI.

**Principle:** most rework traces back to scoping against the wrong consumer, the wrong kind of job, or content that doesn't exist. The gate *survey existing tools first* (in `MEMORY.md`) is the hard form of this hub.

**Sharpest warning signs** (mirrored in `MEMORY.md`):
- changing a live system costs a multiple of greenfield — classify the job and say the multiple at kickoff; split plans by risk, front-loading unknowns
- no UI for content or capabilities that don't exist; recommend the obvious UX instead of enumerating options
- roll a pattern out N times before extracting a template; mark deliberate corner-cuts with a ceiling AND an upgrade trigger

**Also watch for:**
- scoping before reading the consumer's own spec, or before asking who the audience is
- mixing inputs: a wireframe is for layout, an exploration is for looks, a content file is for content — keep each to its purpose
- automating one runbook step and silently dropping its follow-on bullets — encode the whole step, or print what was skipped
- picking a storage format before asking what the data is FOR ("for statistics" means a closed vocabulary, not prose)
- your own option labels drifting from the user's goal — restate the goal before designing

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — a template extracted after one run** - the second project needed half of it changed. Finish the rollout across N projects first; patterns harden through repetition (see workflow streams)
- *Add your own incidents here.*
