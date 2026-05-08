---
name: commit
description: "Safe git commit with pre-flight checks — verifies branch, remote, scans for junk files, shows diff, then commits. Use whenever committing changes to any project."
---

# Safe Commit

A pre-flight checklist to run before every git commit. Prevents the most common git mistakes: wrong branch, wrong repo, junk files in staging.

## When to use

- Any time you're about to commit changes
- Especially when switching between projects (wrong-repo risk)
- Replaces ad-hoc `git add` + `git commit` sequences

## Pre-flight Checklist

Run these steps in order. Do NOT skip any step.

### 1. Branch check

```bash
git branch
```

Show the current branch to the user. Ask: "Is this the correct branch for this commit?"

Wait for confirmation before continuing.

### 2. Remote check

```bash
git remote -v
```

Show the remote URL. Ask: "Is this the correct repo?"

Wait for confirmation before continuing.

### 3. Staged file scan

```bash
git status
```

Check staged files for `.DS_Store` or `.jsonl`. If found:
- Run `git reset HEAD <file>` to unstage each one
- Tell the user which files were removed from staging and why

### 4. Diff summary

```bash
git diff --cached --stat
```

Show the user what's actually being committed. If nothing is staged yet, ask what files to stage first.

### 5. Commit message

Write a commit message based on the diff. Pick a clear one and proceed straight to the commit — no need to ask the user to approve wording.

Format: plain language, present tense. Match the recent commit style in the repo (run `git log --oneline -5` if unsure). Examples:
- `Add contact form to homepage`
- `Fix sticky header on mobile`
- `Update CLAUDE.md with git safety rules`

### 6. Commit

```bash
git commit -m "<message>"
```

### 7. Push confirmation

Ask: "Push to remote now?"

Only push if user confirms. Run:
```bash
git push
```

## Guardrails

- NEVER run `git push --force` without explicit user instruction
- NEVER commit files containing secrets (.env with real values, credentials)
- NEVER skip the branch and remote checks — this is the whole point of this skill
