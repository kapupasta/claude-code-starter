---
name: principle_fix_the_tool_first
description: "Hub — when friction repeats (an error, a hook block, a retry loop), fix it at the source (environment, tool, hook) before writing a rule; fences are the user's call and a fix must cost less than the friction"
type: feedback
tags: [claude-code, gotcha]
---

# Fix the tool before the rule

This file owns the fix ladder (remove → tool catches → write down) and every incident filed under it.

**When:** the same error, hook block or retry hits twice in a session. Also on every pre-clear friction nomination, where it runs as the fix ladder in Step 1.

**Principle:** a written rule has to beat a habit every time, with nothing to remind the agent at the moment it matters, and every rule added makes the rest less reliable. Take the highest rung that works:

1. **Remove it.** Change the environment so the mistake can't happen: a shell option, an install, a setting, an alias.
2. **Make the tool catch it.** A hook or script that corrects the mistake, or blocks with the exact fix in its message. Fixing a hook's false positive also counts.
3. **Write it down** in memory or CLAUDE.md. Only for what 1–2 can't reach: judgment calls, preferences, facts.

**The user is the gate.** The agent spots the friction and proposes the fix; the user decides every rung 1–2 change: installing a tool, changing a setting or the shell, adding or changing a hook, loosening any restriction. The proposal names the friction (hits, cost per hit), the exact change, and what it would cost. Never apply one unilaterally, not even an obvious one.

**Two guards:**
- **Fences: fix your own side first.** Never lead with loosening a safety boundary (the sandbox, the scope guard, permission and ask gates, safety hooks). Propose a fix to your command shape, the fence's error message, or a false positive. Whether to loosen a fence is the user's decision alone; raise it, never route around it.
- **The fix must cost less than the friction.** Compare setup plus upkeep against hits × cost per hit. A new scheduled job to save one retry a month loses.

**Also:** a repeat despite an existing rule means the rule failed. Climb the ladder instead of rewording the rule. When a rung 1–2 fix lands, retire the rule it replaces and add a check that fails if the fix stops working (e.g. a line in `scripts/meta-health.sh`).

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — shell defaults caused a large share of tool failures** - CLAUDE.md already said "quote your globs" and it still hit repeatedly. Fix: set the shell option for agent sessions only, plus a health check that fails if the option disappears
- **Example — measure before fixing** - an assumed GNU-vs-BSD tool problem showed up once in a week of transcripts; the scan redirected the fix to the real top cause
- *Add your own incidents here.*
