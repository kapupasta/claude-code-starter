---
name: commit
description: "Safe git commit with pre-flight checks — verifies branch, remote, scans for junk files, shows diff, then commits. Use whenever committing changes to any project. Do NOT use for branching strategy, remotes setup, PRs, issues, releases, repo creation, or merge-conflict resolution — those are separate git workflows."
---

# Safe Commit

This file owns the pre-commit checklist. It prevents the most common git mistakes: wrong branch, wrong repo, junk files in staging, and another session's changes riding along under your message.

## When to use

- Any time you're about to commit changes
- Especially when switching between projects (wrong-repo risk)
- Replaces ad-hoc `git add` + `git commit` sequences

## Pre-flight Checklist

Run these steps in order. Do NOT skip any step.

### 0. Load the git gotcha bucket

If the memory dir has a `MEMORY-gotchas-git.md` bucket, Read it now unless it is already in context, and apply it as a checklist through the rest of this flow.

Git rules belong in a bucket that loads on git *operations* rather than in the always-loaded index. This step is that trigger. Skip it and the bucket is stranded: nothing else reads it at the moment it applies.

### 1. Branch check

```bash
git branch --show-current
```

Show the current branch to the user. Ask: "Is this the correct branch for this commit?" and wait for confirmation, **unless both hold**, in which case show it and continue:

- the user explicitly asked to commit in this turn ("commit your changes", "commit the memory edits"), and
- the branch is the one this repo is known to commit on: its default branch as recorded in memory or the repo's CLAUDE.md, or the branch this session already committed to.

**Failure mode this still guards against:** the working directory drifts (it can persist or silently reset between calls), and the commit lands in the wrong repo or on a feature branch. If either condition is uncertain, ask. Waiting for a "yes" on a commit the user just asked for, in a repo whose identity is known, is a rubber stamp; that is why the exception exists.

### 2. Remote check

```bash
git remote get-url origin
```

Show the remote URL. Ask: "Is this the correct repo?" and wait, under the **same two conditions** as step 1. Here the known identity is the remote recorded in memory or the repo's CLAUDE.md, or the remote this session already committed to. An unfamiliar remote always gets the question.

### 3. Staged file scan

```bash
git status
```

Check staged files for junk: `.DS_Store`, `.jsonl` transcripts, editor swap files, `.env` files with real values. If found:
- Run `git reset HEAD <file>` to unstage each one
- Tell the user which files were removed from staging and why

### 4. Diff summary

```bash
git diff --cached --stat
```

Show the user what's actually being committed. If nothing is staged yet, ask what files to stage first.

**In a repo that other sessions also write to** (a shared workspace repo, a dotfiles repo, anything a parallel agent touches), **do steps 4 and 6 in ONE Bash call**: stage the exact paths, assert that the staged list equals exactly those paths, and only then commit, aborting if it doesn't match. A check made in a *separate* turn certifies a set that can change before you commit: another session stages its own files in between and they ship under your message. Single-writer repos don't need this. Either way, **read the file count `git commit` prints against what you expected**; that number is what catches it.

### 5. Commit message

Write a commit message based on the diff. **Do NOT ask the user to choose or approve it** unless they've said they want to; pick a clear one and proceed.

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

Only push if the user confirms. Run:
```bash
git push
```

## Guardrails

- NEVER run `git push --force` without explicit user instruction
- NEVER commit files containing secrets (`.env` with real values, credentials, tokens)
- NEVER skip the branch and remote checks — this is the whole point of this skill. Always RUN and SHOW them; only the *wait* for confirmation may be skipped, under the step 1 conditions
- NEVER amend a commit that is already **pushed**, or a commit **someone else** made. Amending your OWN unpushed commit to fix your own mistake is fine and preferred over a fixup commit. Check the tree is clean first: `--amend` absorbs whatever is staged
