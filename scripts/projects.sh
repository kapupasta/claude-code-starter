#!/usr/bin/env bash
# This file owns the git-activity freshness audit of the project roster (PROJECTS.md).
#
# Lifecycle grouping (Active / Maintenance / Archived) is set by hand in the roster.
# Freshness is the drift-prone part that rots if hand-maintained, so this script derives
# it from each project directory's git log and flags mismatches:
#   - in "Active" but idle > ACTIVE_DAYS        -> consider moving to Maintenance
#   - in "Maintenance" but touched recently     -> consider moving back to Active
#   - a listed path that doesn't exist on disk  -> fix the path or the entry
# It NEVER edits the roster; it only reports. Moving an entry is the user's call.
#
# Config: ~/.claude/hooks/starter-config.json (override with STARTER_CONFIG=<file>).
#   workspace_root  base for relative roster paths           (default ~/code)
#   roster_file     the roster                               (default <workspace_root>/PROJECTS.md)
#
# Usage:  bash scripts/projects.sh [path/to/PROJECTS.md]
# Exit:   number of drift flags (0 = roster matches git activity).
# Portable: bash 3.2 + system python3 (3.9-safe); the logic runs in Python so BSD/GNU
# tool differences can't change the result.

exec python3 - "$@" <<'PY'
import json, os, re, subprocess, sys, time

ACTIVE_DAYS = 30
SECTIONS = ("Active", "Maintenance", "Archived")
NO_DIR_WORDS = ("no folder", "no dir", "none", "-", "planned")
FIELD_SEP = re.compile(r"\s+(?:—|--)\s+")   # " — " or " -- "


def load_config():
    """Read starter-config.json; return dict of resolved paths with defaults.

    @return dict with keys workspace_root, roster_file
    """
    path = os.environ.get("STARTER_CONFIG") or os.path.expanduser("~/.claude/hooks/starter-config.json")
    cfg = {}
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as fh:
                cfg = json.load(fh)
        except (ValueError, OSError) as exc:
            print("warning: could not parse %s (%s); using defaults" % (path, exc), file=sys.stderr)
    ws = os.path.abspath(os.path.expanduser(cfg.get("workspace_root") or "~/code"))
    roster = cfg.get("roster_file") or os.path.join(ws, "PROJECTS.md")
    roster = os.path.expanduser(roster)
    if not os.path.isabs(roster):
        roster = os.path.join(ws, roster)
    return {"workspace_root": ws, "roster_file": roster}


def parse_roster(text):
    """Yield (section, name, raw_path) for each project bullet in the roster.

    @param text roster file contents
    @return list of tuples
    """
    out, section = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            head = line[3:].strip()
            section = next((s for s in SECTIONS if head.startswith(s)), None)
            continue
        if section is None or not line.startswith("- ") or line.startswith("- **"):
            continue
        parts = FIELD_SEP.split(line[2:].strip())
        if len(parts) < 2:
            continue
        out.append((section, parts[0].strip(), parts[1].strip().strip("`").strip()))
    return out


def resolve_dir(raw, ws):
    """Turn a roster path field into an absolute directory, or None if it names no folder.

    @param raw path field as written in the roster
    @param ws  workspace root
    @return absolute path or None
    """
    if raw.lower().startswith(NO_DIR_WORDS):
        return None
    p = os.path.expanduser(raw)
    return p if os.path.isabs(p) else os.path.join(ws, p)


def last_commit(path):
    """Return (unix_ts, short_date) of the last commit touching path, or None.

    Scoped to the directory itself so a subdir inside a larger repo reports its own age.
    @param path project directory
    """
    try:
        res = subprocess.run(["git", "-C", path, "log", "-1", "--format=%ct %cd", "--date=short", "--", "."],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    except OSError:
        return None
    bits = res.stdout.split()
    return (int(bits[0]), bits[1]) if len(bits) == 2 else None


def main():
    cfg = load_config()
    roster = sys.argv[1] if len(sys.argv) > 1 else cfg["roster_file"]
    if not os.path.isfile(roster):
        print("roster not found: %s" % roster, file=sys.stderr)
        return 2
    with open(roster, encoding="utf-8") as fh:
        entries = parse_roster(fh.read())

    now, flags = time.time(), 0
    row = "%-28s %-12s %-6s %-12s %s"
    print(row % ("PROJECT", "LAST COMMIT", "AGE", "LIFECYCLE", "DRIFT FLAG"))
    print("-" * 84)
    for section, name, raw in entries:
        path = resolve_dir(raw, cfg["workspace_root"])
        if path is None:
            print(row % (name, "-", "-", section, "planned / no folder"))
            continue
        if not os.path.isdir(path):
            flags += 1
            print(row % (name, "-", "-", section, "MISSING DIR: %s" % raw))
            continue
        lc = last_commit(path)
        if lc is None:
            print(row % (name, "-", "-", section, "no git history"))
            continue
        age = int((now - lc[0]) // 86400)
        flag = ""
        if section == "Active" and age > ACTIVE_DAYS:
            flag = "STALE-ACTIVE: %dd idle -> Maintenance?" % age
        elif section == "Maintenance" and age <= ACTIVE_DAYS:
            flag = "REVIVED: %dd -> Active?" % age
        if flag:
            flags += 1
        print(row % (name, lc[1], "%dd" % age, section, flag))
    print()
    print("%d drift flag(s) across %d roster entries (threshold %d days)" % (flags, len(entries), ACTIVE_DAYS))
    return min(flags, 255)


sys.exit(main())
PY
