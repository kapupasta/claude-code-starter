# Workspace Memory

Index file. One-line pointers, not content. Keep under 200 lines.

For the system itself (how memory works, when to load, save rules), see the workspace `CLAUDE.md` and `CONVENTIONS.md`.

---

## User Profile

<!-- Facts about you that shape how Claude collaborates with you. Examples:
- Senior backend engineer, 8 years Python/Go.
- Architect, not implementer — explain things in plain language.
- Native German speaker, English for code/docs.
- Privacy-conscious — minimal personal info on public-facing sites.
-->

## Standing Preferences

<!-- Universal rules that apply to all projects. Examples:
- Always use feature branches before opening a PR.
- Prefer pnpm over npm.
- EU-based / open-source tools first; proprietary US-cloud only as last resort.
- Don't ask before reading files. Always ask before running shell commands.
-->

## Universal Workflow Rules

<!-- Guidance for how Claude should behave. Pulled out separately because these
matter enough to scan every session. Examples:
- Question and clarify before acting on anything ambiguous.
- Plan before implementing — show files, changes, side effects.
- Never push to remote without explicit confirmation.
-->

## Bucket Index

Load matching bucket when working on related tech:

<!-- Edit to match your actual stacks. Delete buckets you don't use. -->
- Web frontend → [`MEMORY-gotchas-EXAMPLE.md`](./MEMORY-gotchas-EXAMPLE.md)
<!--
- Backend / API → [`MEMORY-gotchas-backend.md`](./MEMORY-gotchas-backend.md)
- Infrastructure → [`MEMORY-gotchas-infra.md`](./MEMORY-gotchas-infra.md)
- Claude Code & Agents → [`MEMORY-gotchas-claude-code.md`](./MEMORY-gotchas-claude-code.md)
-->

## Active Projects

<!-- Format: - <name> — `<path on disk>` — <one-line status>
The memory-load-check hook parses this section to decide which project a user
message refers to, so the dash format matters. Example:
- my-app — `~/code/my-app/` — Live, occasional bug fixes
- new-thing — `~/code/new-thing/` — In development, feature branch open
-->
