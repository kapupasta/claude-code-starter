---
name: principle_facts_from_source
description: "Hub — before stating how a tool, vendor, version, framework or bug behaves, get it from the primary source or by driving it; links every source-of-truth lesson"
type: feedback
tags: [gotcha]
---

# Facts from source, not assumption

This file owns the source-of-truth principle and every incident filed under it.

**When:** you are about to state what a tool can or can't do, what a vendor charges or shows, which version is safe, why something broke, or why an option is closed.

**Principle:** effects you observed are facts; causes, capabilities and version claims are inferences until checked against the primary source (the installed package, the vendor's own page, the running process, the log) or by driving the tool yourself. The gates *never assume* and *docs before assuming* (in `MEMORY.md`) are the hard form of this hub.

**Sharpest warning signs** (mirrored in `MEMORY.md`):
- effect = fact, cause = inference; tag report findings VERIFIED (+evidence) / INFERRED / ASSUMED
- the vendor's own page and the installed package beat summaries, blog posts and plan text
- stuck/slow/not firing → check CPU, then trigger-vs-action, before theorising

**Also watch for:**
- the user's own observation is a primary source: what they *saw* is fact; what they say *caused* it is a hypothesis
- a failure on a deployed app: read its log before any config — config says what could happen, the log says what did
- a remembered count or a memory's rationale is a claim about the past, not an inventory — re-measure before citing it
- an upgrade target is a dependency-graph claim: check what depends on the package before naming a version
- reading only the function that handles your case — an upstream early return wins
- "my change isn't showing up": check the transport (cache headers, build output) before the payload
- a contrast between two setups is evidence only if they differ in ONE thing
- a probe that can't pass by design (read the feature's documented exceptions first)
- a denial or error that names no cause — read the actual rule before naming one
- library behaviour doesn't transfer to a wrapped config — drive the real build

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — the stored rationale was wrong** - an option was closed by citing a memory's reason; one probe showed the reason had never been verified. Verify a memory's *why* before using it to close an option
- **Example — "slow" was hung** - a process sat for minutes at 0% CPU waiting on stdin; waiting never fixes that. Check CPU past ~2 minutes
- *Add your own incidents here.*
