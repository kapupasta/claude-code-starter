# Claude Code Starter

A reproducible Claude Code setup with persistent memory, scoped tool access, and a pre-clear discipline. Skeleton only — no opinions about your work, just the wiring.

## What you get

- **Three-tier memory system** (index → buckets → topic files) with closed-vocabulary tags
- **Three hooks** — workspace scope guard, memory-load enforcement, session summary capture
- **Three skills** — `pre-clear` (run before `/clear`), `prune` (shrink CLAUDE.md/MEMORY.md), `commit` (git pre-flight)
- **CLAUDE.md** that explains the system, with TODO markers for your own conventions

## Install

```bash
git clone https://github.com/kapupasta/claude-code-starter ~/claude-code-starter
cd ~/claude-code-starter
./install.sh
```

(Or fork it first if you want to track your own customizations under your account.)

The installer asks for your workspace root (e.g. `~/code` or `~/projects`), renames the placeholder project dir to match, and symlinks `~/.claude/{settings.json,hooks,skills}` into this repo. Memory lives at `~/.claude/projects/<your-slug>/memory/` and is symlinked back into the repo so it gets versioned.

## After install

1. Open Claude Code inside your workspace root.
2. Edit `CLAUDE.md` — fill the **TODO: Customize** section with your role, preferences, and workflow rules.
3. Edit `memory/MEMORY.md` — add yourself to *User Profile* and *Standing Preferences*.
4. Edit `memory/CONVENTIONS.md` — set the tech-stack tags you actually use.
5. Rename `MEMORY-gotchas-EXAMPLE.md` to your first real bucket (e.g. `-frontend.md`, `-backend.md`).

That's it. Use Claude normally. Memory accretes as you give feedback. Run `/pre-clear` before every `/clear` and the system stays coherent across sessions.

## What this is *not*

- Not a workflow opinion. The starter doesn't tell you when to ask, when to commit, or what to prefer. That's CLAUDE.md's job — you write it.
- Not a plugin set. Plugins are personal; install your own via `/plugin` after setup.
- Not a productivity system. It's the substrate. The discipline is yours.

## Uninstall

```bash
rm ~/.claude/settings.json ~/.claude/hooks ~/.claude/skills
rm ~/.claude/projects/<your-slug>
```

The repo itself is untouched, so you can re-link or migrate to another machine.
