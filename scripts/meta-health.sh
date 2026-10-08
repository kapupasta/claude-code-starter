#!/usr/bin/env bash
# This file owns the health check of the memory layer and the project roster.
#
# Reports only what needs attention; condition-triggered, not a calendar nag.
# Companion to projects.sh (which audits project *freshness*).
#
# Checks:
#   [1] MEMORY.md size vs the auto-load cap (first 200 lines OR 25KB, whichever first)
#   [2] dead links in index files (MEMORY*.md, CONVENTIONS.md, principle_*.md)
#   [3] roster -> project file gaps: an arrow to a missing file, or a file with no arrow
#   [4] orphan project_*.md files the roster never mentions
#   [5] naming lint: memory topic files snake_case with a type prefix; roster names/dirs kebab-case; ASCII only
#   [6] index stubs over the one-line <=200-char rule
#
# Config: ~/.claude/hooks/starter-config.json (override with STARTER_CONFIG=<file>).
#   workspace_root  (default ~/code)
#   roster_file     (default <workspace_root>/PROJECTS.md)
#   memory_dir      (default ~/.claude/projects/<workspace slug>/memory)
#
# Usage:  bash scripts/meta-health.sh
# Exit:   number of findings (0 = clean), so a scheduler or CI wrapper can branch on it.
# Portable: bash 3.2 + system python3 (3.9-safe).

exec python3 - "$@" <<'PY'
import glob, json, os, re, sys, unicodedata

SIZE_WARN = 20000     # bytes: soft limit, fires well before the cap
SIZE_HARD = 25000     # bytes: Claude Code stops loading MEMORY.md around 25KB
LINE_WARN = 180       # lines: soft limit
LINE_HARD = 200       # lines: Claude Code loads only the first 200 lines
STUB_MAX = 200        # chars: an index stub is one line, <=200 chars (CONVENTIONS.md)
TOPIC_PREFIXES = ("project", "feedback", "reference", "infra", "user", "principle")
INDEX_FILES = re.compile(r"^(MEMORY(-[A-Za-z0-9_-]+)?|CONVENTIONS)\.md$")
TOPIC_NAME = re.compile(r"^(%s)_[a-z0-9_]+\.md$" % "|".join(TOPIC_PREFIXES))
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK = re.compile(r"\]\((?:\./)?([A-Za-z0-9_.-]+\.md)\)")
ARROW = re.compile(r"(?:→|->)\s*(project_[^\s)]+\.md)")
FIELD_SEP = re.compile(r"\s+(?:—|--)\s+")
COMMENT = re.compile(r"<!--.*?-->", re.S)
NO_DIR_WORDS = ("no folder", "no dir", "none", "-", "planned")
SECTIONS = ("Active", "Maintenance", "Archived")

nfc = lambda s: unicodedata.normalize("NFC", s)   # macOS lists filenames NFD; typed text is NFC


def load_config():
    """Read starter-config.json and resolve workspace_root, roster_file and memory_dir.

    @return dict of absolute paths
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

    def resolve(value, default):
        p = os.path.expanduser(value or default)
        return p if os.path.isabs(p) else os.path.join(ws, p)

    slug = os.path.realpath(ws).replace("/", "-")
    return {
        "workspace_root": ws,
        "roster_file": resolve(cfg.get("roster_file"), os.path.join(ws, "PROJECTS.md")),
        "memory_dir": resolve(cfg.get("memory_dir"), "~/.claude/projects/%s/memory" % slug),
    }


def read(path):
    """Return file text, or '' if missing.

    @param path file path
    """
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def roster_entries(text):
    """Return (section, name, raw_path, line) for each project bullet in the roster.

    @param text roster contents
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
        if len(parts) >= 2:
            out.append((section, parts[0].strip(), parts[1].strip().strip("`").strip(), line))
    return out


def slug_of(name):
    """project_<slug>.md for a roster name: lowercase, non-alphanumerics -> '_'.

    @param name roster entry name
    """
    return nfc("project_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") + ".md")


def check_size(memory, findings):
    """[1] MEMORY.md bytes and lines against the soft limits."""
    if not os.path.isfile(memory):
        print("[1] MEMORY.md: MISSING at %s" % memory)
        findings.append("MEMORY.md missing at %s" % memory)
        return
    size = os.path.getsize(memory)
    lines = read(memory).count("\n")
    print("[1] MEMORY.md: %d B / %d lines (warn %d B / %d lines; cap ~%d B / %d lines)"
          % (size, lines, SIZE_WARN, LINE_WARN, SIZE_HARD, LINE_HARD))
    if size > SIZE_WARN:
        findings.append("MEMORY.md is %d B, over the %d B soft limit - run a compaction pass (CONVENTIONS.md stub rule), don't raise the limit" % (size, SIZE_WARN))
    if lines > LINE_WARN:
        findings.append("MEMORY.md is %d lines, over the %d-line soft limit - run a compaction pass" % (lines, LINE_WARN))


def check_dead_links(memdir, findings):
    """[2] relative .md links in index files and hubs that point at nothing."""
    files = sorted(glob.glob(os.path.join(memdir, "MEMORY*.md")) + glob.glob(os.path.join(memdir, "principle_*.md"))
                   + [os.path.join(memdir, "CONVENTIONS.md")])
    present = {nfc(os.path.basename(p)) for p in glob.glob(os.path.join(memdir, "*.md"))}
    dead = []
    for f in files:
        text = COMMENT.sub("", read(f))         # commented-out example stubs aren't links
        for target in sorted(set(LINK.findall(text))):
            if nfc(target) not in present:
                dead.append((os.path.basename(f), target))
    print("[2] dead links in index files: %d" % len(dead))
    for f, t in dead:
        findings.append("dead link in %s -> %s" % (f, t))


def check_roster_gaps(entries, project_files, findings):
    """[3] arrow -> missing file, and existing project_<slug>.md with no arrow."""
    gaps = []
    for _section, name, _raw, line in entries:
        arrows = [nfc(a) for a in ARROW.findall(line)]
        for a in arrows:
            if a not in project_files:
                gaps.append("roster entry '%s' points to %s, which doesn't exist" % (name, a))
        if not arrows and slug_of(name) in project_files:
            gaps.append("roster entry '%s' has %s but no -> arrow to it" % (name, slug_of(name)))
    print("[3] roster -> project file gaps: %d" % len(gaps))
    findings.extend(gaps)


def check_orphans(roster_text, entries, project_files, findings):
    """[4] project_*.md files the roster never mentions (by filename or by entry-name slug).

    A file whose slug matches an entry but lacks the arrow is already reported by [3].
    """
    text = nfc(roster_text)
    slugs = {slug_of(name) for _s, name, _r, _l in entries}
    orphans = sorted(f for f in project_files if f not in text and f not in slugs)
    print("[4] project files not in the roster: %d" % len(orphans))
    for f in orphans:
        findings.append("orphan %s - file it in the roster (any section); a missing entry is rarely a dead project, so confirm with the user before archiving" % f)


def check_naming(memdir, entries, ws, findings):
    """[5] ASCII/lowercase/no-space lint for memory files, roster names and project dirs."""
    bad = []
    for p in sorted(glob.glob(os.path.join(memdir, "*.md"))):
        base = nfc(os.path.basename(p))
        if INDEX_FILES.match(base):
            continue
        if not TOPIC_NAME.match(base):
            bad.append("memory file '%s' (want <%s>_snake_case.md, ASCII)" % (base, "|".join(TOPIC_PREFIXES)))
    for _section, name, raw, _line in entries:
        if not KEBAB.match(nfc(name)):
            bad.append("roster name '%s' (want kebab-case ASCII)" % name)
        if raw.lower().startswith(NO_DIR_WORDS):
            continue
        p = os.path.expanduser(raw)
        if not os.path.isabs(p):
            seg = p.strip("/").split("/")[0]       # the project's own top-level dir
        else:
            seg = os.path.basename(p.rstrip("/"))
        if seg and not KEBAB.match(nfc(seg)):
            bad.append("project dir '%s' (want kebab-case ASCII)" % seg)
    print("[5] naming offenders: %d" % len(bad))
    for b in bad:
        findings.append("naming: " + b)


def check_stub_length(memdir, findings):
    """[6] bullet lines in MEMORY.md / MEMORY-*.md longer than STUB_MAX chars."""
    long_stubs = []
    for f in sorted(glob.glob(os.path.join(memdir, "MEMORY*.md"))):
        for n, line in enumerate(COMMENT.sub("", read(f)).splitlines(), 1):
            if line.lstrip().startswith("- ") and len(line) > STUB_MAX:
                long_stubs.append("%s line %d is %d chars (max %d) - move the detail to the topic file"
                                  % (os.path.basename(f), n, len(line), STUB_MAX))
    print("[6] index stubs over %d chars: %d" % (STUB_MAX, len(long_stubs)))
    findings.extend(long_stubs)


def main():
    cfg = load_config()
    memdir, roster = cfg["memory_dir"], cfg["roster_file"]
    print("memory_dir:  %s" % memdir)
    print("roster_file: %s" % roster)
    findings = []
    if not os.path.isdir(memdir):
        print("memory dir not found - set memory_dir in starter-config.json")
        return 1
    roster_text = read(roster)
    if not roster_text:
        print("(roster not found - checks [3]-[5] see no entries)")
    entries = roster_entries(roster_text)
    project_files = {nfc(os.path.basename(p)) for p in glob.glob(os.path.join(memdir, "project_*.md"))}

    check_size(os.path.join(memdir, "MEMORY.md"), findings)
    check_dead_links(memdir, findings)
    check_roster_gaps(entries, project_files, findings)
    check_orphans(roster_text, entries, project_files, findings)
    check_naming(memdir, entries, cfg["workspace_root"], findings)
    check_stub_length(memdir, findings)

    print()
    if findings:
        print("FAIL: %d finding(s)" % len(findings))
        for f in findings:
            print("  - " + f)
    else:
        print("OK: all clean")
    return min(len(findings), 255)


sys.exit(main())
PY
