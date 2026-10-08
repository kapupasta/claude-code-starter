# Why each piece exists

Every mechanism in this starter was added after something went wrong without it. This file says what each one prevents, and what you risk if you leave it out. Nothing here is mandatory: delete what doesn't fit your work, but delete it knowing the trade.

Each entry has the same three parts:

- **Prevents:** the failure it stops.
- **Without it:** what you risk by removing it.
- **Turn it off:** how, if you decide to.

---

## Settings (`.claude/settings.json`)

### Bash sandbox (`sandbox`)

The sandbox is an operating-system boundary around the shell commands Claude runs (Seatbelt on macOS, bubblewrap on Linux and WSL2; native Windows has none). Inside it, a command can write only to the working directory, `$TMPDIR` and the paths you list in `allowWrite`, and it can reach only the network hosts you allow.

- **Prevents:** a command doing more than you meant it to. That covers a mistyped `rm` outside the project, a build script or package install that phones home, and a prompt injection in a web page or README that talks Claude into exfiltrating data with `curl`. Because the OS enforces the limits, Claude Code can also run sandboxed commands **without asking you each time**. So the sandbox doesn't just add safety, it also takes away a large share of permission prompts.
- **Without it:** every Bash command runs with your full user rights, and your only protection is the permission prompt (or, in auto mode, a classifier that decides for you, so no human sees the call). Auto mode without a sandbox means an unattended agent with full shell access.
- **Turn it off:** set `"enabled": false`, or delete the `sandbox` block. **Risk:** the above. If you do, at least switch `defaultMode` away from `auto`, so a human approves each command.

What each key does:

| Key | Why it's set this way |
|---|---|
| `autoAllowBashIfSandboxed: true` | The whole point: contained commands don't need a prompt. |
| `allowUnsandboxedCommands: true` | Lets Claude retry a command that fails in the sandbox **outside** it. Each retry still goes through the permission flow, and the `ask` rule on `dangerouslyDisableSandbox` makes sure you see it. Set it to `false` for a strict sandbox with no escape hatch. |
| `network.strictAllowlist: true` | An unlisted host fails at once instead of prompting. Without it, every new host is a prompt you'll learn to click through. **Only honoured from user settings**, which is where `install.sh` links this file. |
| `network.allowedDomains` | Package registries and GitHub's download hosts. `github.com` and `api.github.com` are deliberately **not** listed: anyone can receive data there (a gist, an issue), so they make a good exfiltration channel. Add the hosts your work needs. |
| `network.allowLocalBinding: true` | Dev servers and local databases need to bind to localhost. |
| `filesystem.allowWrite` | Package caches (`~/.npm` here; add `~/Library/pnpm/store` or `~/.local/share/pnpm/store` for pnpm). Without them, installs fail in confusing ways. |
| `credentials` | Commands can **read most of your machine by default**, including `~/.ssh` and cloud keys. Listing them with `"mode": "deny"` blocks reads and unsets the env vars inside the sandbox. Add every credential file and token variable you have. **Only honoured from user or managed settings.** |
| `excludedCommands` | `git fetch/push/pull` over SSH can't work sandboxed: the proxy filters HTTP(S), and SSH is raw TCP. Read-only `gh` commands are excluded because `gh` can fail TLS checks under Seatbelt. **Keep this list short.** Every entry is a command that runs with your full access. |

Gotchas that come with it (also in `CLAUDE.md`): `/tmp` isn't writable (use `$TMPDIR`), `diff <(…)` fails, DNS tools like `dig` time out and still exit 0, and an excluded command only escapes when it's **alone on the line**. `cd repo && git pull` stays sandboxed and fails like an auth error.

The sandbox covers **shell commands only**. Claude's own Read, Edit, Write, Glob and Grep tools, MCP servers and hooks run outside it. That gap is why `guard-scope.py` exists (see Hooks).

Docs: <https://code.claude.com/docs/en/sandboxing>

### Permissions

| Rule | Prevents | Without it |
|---|---|---|
| `defaultMode: "auto"` | A prompt for every routine action. A classifier approves safe actions and blocks risky ones. | You approve everything by hand, or you switch to bypass mode, which has no checks at all. Note that the classifier is **not a human checkpoint**: nothing reaches you when it approves. Keep the real safety in the sandbox and the hooks. |
| `deny: Bash(claude *)` | Claude starting another Claude Code process from inside a session, an agent spawning agents with none of the hooks watching. | A runaway or injected session can recurse. |
| `ask: Bash(dangerouslyDisableSandbox:true)` | A silent sandbox escape: every unsandboxed retry shows up as a prompt you answer. | An escaped command runs on the classifier's say-so alone. |

### Auto-mode environment (`autoMode.environment`)

The classifier decides "is this action risky?" without knowing your setup. `"$defaults"` keeps the built-in rules. Add plain-English lines that describe **your** boundary:

```json
"environment": [
  "$defaults",
  "Source control: github.com/your-org and all repos under it",
  "Trusted internal domains: staging.example.com (staging, not production)",
  "Sensitive remote targets: any live client production site, whether listed here or not"
]
```

- **Prevents:** blocks on routine actions against your own infrastructure, and approvals of actions against production it couldn't recognise as such.
- **Without it:** expect more false blocks on your own staging hosts, and fewer blocks on production hosts the classifier can't name.
- **Watch for:** an explicit list can **replace** a default instead of extending it. Name a few production hosts, and the ones you didn't name may lose the default "looks like prod" caution. Say "not exhaustive" in the line.

### Other settings

- `cleanupPeriodDays: 90`: keeps session transcripts for three months. `prompt-provenance.py` searches them, and so does any later "what did we decide" question.
- `autoCompactEnabled: true`: long sessions compact instead of failing. `save-session-summary.sh` keeps each summary.

---

## Hooks (`.claude/hooks/`)

Hooks are scripts Claude Code runs on events. A PreToolUse hook that exits 2, or that returns `permissionDecision: "deny"`, blocks the tool call, and Claude sees the reason. Every hook reads its paths from `starter-config.json`. A missing config never blocks a prompt: the scope guard narrows to the current folder and the rest allow.

To remove a hook, delete its entry from `settings.json`. The file can stay.

### `guard-scope.py` (PreToolUse, file tools + Bash)

- **Prevents:** Claude reading or writing outside your workspace without asking: SSH keys, other projects, another client's repo. The sandbox can't cover this, because **Claude's own Read, Edit, Write, Glob and Grep tools run outside the sandbox**. This hook is the only fence around them.
- **Without it:** any path in your home directory is one tool call away, and a prompt injection only needs to name it.
- **Know:** read-only roots (default `~/.agents`, where `npx skills add --global` installs skills) allow reads but not writes. Bash path tokens are checked after trailing punctuation (`;`, `&&`, `)`) is stripped, so `ls ~/code;` isn't a false block.

### `memory-load-check.py` (PreToolUse, Edit/Write/Bash)

- **Prevents:** Claude working on a project it was just named without loading that project's memory. The lessons are on disk, but they never reach the session that needs them.
- **Without it:** the loading rule in CLAUDE.md is a request. When the model skips it, it repeats a mistake you already corrected.
- **Know:** it counts the **Read tool** only. A memory file opened with `cat` doesn't count, which is deliberate: Read calls are visible in the transcript. Warnings 1–3 go into Claude's context, and the 4th call is denied.

### `env-guard.py` (PreToolUse, Edit/Write/Bash)

- **Prevents:** Claude writing secrets into `.env` files, including through `>` and `>>` redirects. Templates (`.env.example`, `.env.sample`) are allowed.
- **Without it:** an agent "helpfully" fills in or rewrites your secrets. `>>` onto a file with no trailing newline also silently merges two values into one line.

### `guard-command-shape.py` (PreToolUse, Bash)

Four rules, each from a real failure:

| Rule | Blocks | Because |
|---|---|---|
| A | `rm -rf` chained with anything else, or aimed at `/`, `~`, `.git` or the workspace root | When `ls` and `rm` share a call, you read the list after the delete has already run. A failed `cd` before `rm -rf` deletes in the wrong directory. Build folders (`node_modules`, `dist`, …) are exempt. |
| B | (warns) bare `git` with no repo context | In a folder of many repos, a quiet "Already up to date" can come from the wrong one. |
| C | a sandbox-excluded command (`git push`, `gh pr view`) sharing its line with anything | Only a line where every part matches `excludedCommands` leaves the sandbox. `cd x && git pull` stays sandboxed and fails like an auth error, and the next retry goes wrong. |
| D | `$TMPDIR` in an unsandboxed call | `$TMPDIR` points somewhere different inside and outside the sandbox, so files "vanish". |

- **Without it:** each of these fails once in a way that looks like something else, and you lose an hour or a directory.
- **Know:** it reads `excludedCommands` from your settings, so Rule C follows your list.

### `prompt-provenance.py` (UserPromptSubmit)

- **Prevents:** a prompt you paste in that **Claude wrote earlier** (a handoff note, a plan) being treated as your own instruction. Its guesses arrive with your authority. The hook spots text that appears in an earlier assistant turn and says so. On report-style asks it also adds a reminder to mark each claim VERIFIED (checked) or INFERRED (reasoned).
- **Without it:** an agent's assumption from yesterday becomes today's "the user said so".
- **Know:** it never blocks, and it's wrapped in `|| true`, because a failing UserPromptSubmit hook would block your prompt.

### `md-link-check.py` (Stop)

- **Prevents:** replies that mention `notes.md` as plain text you can't click. It blocks the end of the turn once and asks for a clickable link; `stop_hook_active` stops it looping.
- **Without it:** nothing breaks. This one is a convenience; drop it freely.

### `save-session-summary.sh` (PostCompact)

- **Prevents:** losing the compaction summary. It's written to `memory/sessions/<date>.md`, so you can see what a long session covered after it compacted.
- **Without it:** the summary exists only inside the session that compacted.
- **Know:** it needs `jq`, and reads the `compact_summary` field.

---

## Skills (`.claude/skills/`)

| Skill | Prevents | Without it |
|---|---|---|
| `pre-clear` | Losing what a session learned. `/clear` wipes context silently and never warns about uncommitted work. The skill walks through friction, memories, workflow-stream notes, todos, a CLAUDE.md check and git, in that order. | Every `/clear` is a small leak. You re-explain the same preferences and re-discover the same gotchas. |
| `commit` | Commits on the wrong branch or into the wrong repo, junk files (`.DS_Store`, logs), and another session's staged files riding along in a shared repo. | Mis-commits get found days later. |
| `prune` | "Clean up MEMORY.md" turning into a rewrite that loses your wording or a gate. It's reduce-only: remove duplication and stale lines, never restructure. | Slow bloat until lines fall past the load cap (below) and stop loading without a word. |
| `projects` | Agents answering from a remembered or copied project list. It reads `PROJECTS.md` live and never embeds it. | Stale project names, and the memory-load hook has nothing to match against. |

A skill's description says when **not** to use it ("Do NOT use for X"). That line stops a skill firing on a near-miss request.

---

## Memory (`memory/`)

### Why layers at all

Claude Code auto-loads **only `MEMORY.md`, and only its first 200 lines / 25 KB**. Nothing else is recalled unless something tells the model to open it. So the index can't hold content, and every other file needs a trigger that loads it.

| Layer | Prevents | Without it |
|---|---|---|
| `MEMORY.md` index (one line per entry) | Content crowding out the index | Past line 200, the rest doesn't load, and nothing warns you |
| Topic files (`feedback_`, `project_`, `reference_`, `user_`) | Unrelated lessons loading together | Every session pays for every lesson |
| Buckets (`MEMORY-gotchas-<stack>.md`) | Stack lessons loading on the wrong work | Your CSS lessons load during a git push, or never |
| `archive/` | Losing history when a memory goes stale | A deleted memory can't be checked when the same question comes back |

### Gates

Your hard lines, kept in their own section and never merged or reworded by an agent. The examples are real gates from the setup this came from: never assume (verify or flag a guess), docs before assuming, never circumvent a rule (ask to amend it), credentials in a password manager, archive don't delete.

- **Prevents:** a "reasonable guess" quietly overriding a rule you set, and an agent tidying your rule into something softer.
- **Without it:** your rules become suggestions over time.

### Principle hubs (`principle_*.md`)

Each principle has one trigger line in `MEMORY.md` ("before saying done…") and a hub file holding the rule, its warning signs, and a `## Cases` list of the incidents that taught it. A new lesson that's a case of an existing principle goes in the hub, not in a new index line.

- **Prevents:** the two ways lesson memory fails: one index line per lesson (the index bloats past its cap), or lessons with no trigger (they're never recalled).
- **Without it:** after a few months you have 400 lessons and no way to find the one that applies.
- **The shipped hubs** are real ones, de-personalised. Keep the ones that match how you work, then add your own cases.

### Path-scoped rules (`.claude/rules/*.md`)

A rules file with a `paths:` glob is injected **automatically** whenever Claude opens a matching file. No model judgment is involved. Use it for a file type's must-not-violate rules. Rules in `~/.claude/rules/` apply to every project, which is why the installer links them there.

- **Prevents:** critical rules depending on the model remembering to load a bucket.
- **Without it:** the cardinal CSS rule loads only if the model thinks to look.
- **Keep both:** rules hold the few always-on cardinals, buckets hold the depth. Don't thin a bucket because a rule exists.

### Project roster (`PROJECTS.md`)

One file listing every project: name, path, status, memory file. Lifecycle (Active / Maintenance / Archived) is set by hand, only when a project changes phase.

- **Prevents:** "which project is this?" guesswork, and the same project known by three names.
- **Without it:** `memory-load-check.py` and the `projects` skill have nothing to match against.

---

## Tooling (`scripts/`, `templates/`)

| Tool | Prevents | Without it |
|---|---|---|
| `scripts/meta-health.sh` | Silent memory rot: an index past its load cap, dead links, orphan files, bad filenames, stubs too long to scan. None of these has a symptom until recall fails. | You find the rot when an agent misses a lesson it "should" know. |
| `scripts/projects.sh` | The roster lying: an "Active" project untouched for months, a "Maintenance" one that's busy again. Git activity is the ground truth. | Agents trust a stale status. |
| `templates/workflow-stream/` | Extracting a template from a single run, which bakes that run's accidents into every later one. A stream runs three real iterations, with notes, before it's hardened into a template. | Premature templates you spend the next three projects fighting. |

Both scripts exit non-zero on findings, so a weekly `launchd` or `cron` job can push an alert. Schedule them, or run them inside `pre-clear`.

---

## What's deliberately not here

- **Your domain skills** (deploy, diary, design review). They're specific to your work; write them as you need them.
- **Plugins and MCP servers.** Personal; install your own with `/plugin`.
- **The content.** The original setup has hundreds of lessons. They're useless to you, and yours will be better because they come from your own mistakes.
