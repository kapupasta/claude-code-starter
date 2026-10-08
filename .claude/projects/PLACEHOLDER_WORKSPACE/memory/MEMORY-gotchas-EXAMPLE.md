# CSS / frontend gotchas index (example bucket)

This file owns the index of frontend lessons. Load it when doing any frontend or styling work (the workspace CLAUDE.md load table says so). Stubs link to topic files in this directory.

Multi-tagged topic files (e.g. `tags: [gotcha, css, wp]`) appear in more than one bucket — that's intentional.
> The must-not-violate subset also auto-loads via `.claude/rules/css.md` whenever a CSS file is opened. Keep the two in sync: the rule file holds the cardinals, this bucket holds the depth.

Rename this file to your real stack (e.g. `MEMORY-gotchas-css.md`, `MEMORY-gotchas-python.md`) and update the link in `MEMORY.md` and the load table in CLAUDE.md. A topic-keyed bucket (git, infra) works the same way; its trigger is the *operation*, not a file type.

**Stub format:** one line, ≤200 chars — `[Title](<topic_file>.md) — rule + the cue that makes it fire`. The why, the incident and the example live in the topic file. Group stubs under `##` headings by sub-area once you have more than ~10.

## Layering & specificity
<!-- Example stubs (create the topic files before uncommenting, or meta-health.sh reports dead links):
- [No !important](feedback_css_no_important.md) — restructure selectors or move the rule to a later `@layer` instead
- [Layer order = FIRST appearance](feedback_css_layer_order.md) — a later `@layer a, b;` can't reorder names already seen; declare order first
-->

## Browser APIs
<!--
- [Browser API "accepts" ≠ "works"](feedback_browser_compat_check.md) — isolate the browser as a variable before tuning code; check MDN compat
-->
