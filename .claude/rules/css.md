---
paths:
  - "**/*.css"
  - "**/*.scss"
---

# CSS cardinal constraints (example — auto-loaded when a CSS file is opened)

This file owns the must-not-violate CSS rules that should be in context the moment any stylesheet is touched. Claude Code injects it automatically for files matching `paths:` above, with no judgment call involved. Depth and the incidents behind each rule live in the memory bucket (`MEMORY-gotchas-css.md`, or whatever you named it); keep the two in sync.

Rules here are cardinals only: a violation silently breaks something, and the rule needs no context to apply. Everything else belongs in the bucket. Replace these with your own.

- **No `!important`.** Restructure selectors, rework the HTML, or move the rule to a later `@layer`.
- **No opacity on text.** Opacity is for decorative layers and motion. Muted text uses a colour token (e.g. `color-mix(in oklch, var(--text), var(--surface) 40%)` or `--text-muted`); opacity muddies anti-aliasing and breaks contrast maths.
- **No unlayered CSS in your own code once you use `@layer`.** Unlayered styles beat every layered rule, so one unlayered reset silently kills layered overrides. Fix the reset (move it into `@layer reset`); don't answer it with more unlayered CSS. The exception is a platform that ships unlayered CSS you can't layer.
- **Layer order is fixed by FIRST appearance.** A later `@layer a, b, c;` can't reorder names already seen; declare the order before any stylesheet uses a layer.
- **No SCSS-style `&__child` in native CSS nesting** — it isn't valid there. Flatten to top-level selectors.
- **Hover brightens, never darkens** (darker reads as disabled), and only clickable elements get hover effects. Check the hover state still meets contrast.
- **`order:` / `row-reverse` reshuffle visuals but NOT focus or screen-reader order** (WCAG 2.4.3). Keep DOM order equal to reading order; reposition with `grid-column` / `grid-row`.
