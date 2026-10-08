#!/usr/bin/env python3
"""This file owns the README architecture diagrams: it renders each figure as a light and a dark SVG.

Run from anywhere: `python3 docs/diagrams/build.py`. Python 3.9+, stdlib only.
GitHub shows an SVG through <img>, where currentColor has no page colour to inherit,
so every colour is baked in per theme and the README picks one with <picture>.
Colours go in style="" (not presentation attributes) so a page embedding the SVG
inline can pass CSS custom properties, e.g. {"fg": "var(--fg)"}.
"""
from pathlib import Path
from xml.sax.saxutils import escape
from typing import Dict, List, Tuple

OUT_DIR = Path(__file__).resolve().parent
FONT = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
LINE_HEIGHT = 18

THEMES: Dict[str, Dict[str, str]] = {
    "light": {"bg": "#fbf8f4", "fg": "#2b2622", "muted": "#6f665e", "box": "#f2ece4", "accent": "#b4562a"},
    "dark": {"bg": "#1f1c1a", "fg": "#ece5dd", "muted": "#a89e94", "box": "#2a2623", "accent": "#e0915f"},
}


class Svg:
    """Collects SVG elements for one figure in one theme."""

    def __init__(self, width: int, height: int, theme: Dict[str, str], label: str) -> None:
        """@param width/height: viewBox size. @param theme: colour map. @param label: aria-label claim."""
        self.w, self.h, self.t, self.label = width, height, theme, label
        self.parts: List[str] = []

    def box(self, x: int, y: int, w: int, h: int, title: str, lines: Tuple[str, ...] = (),
            accent: bool = False, dashed: bool = False, mono_title: bool = False) -> None:
        """Draw a rounded box with a bold title and muted body lines. @return None"""
        stroke = self.t["accent"] if accent else self.t["muted"]
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" stroke-width="1.5"{dash} '
            f'style="fill:{self.t["box"]};stroke:{stroke}"/>')
        family = MONO if mono_title else FONT
        colour = self.t["accent"] if accent else self.t["fg"]
        self.text(x + 14, y + 24, title, size=13, weight="600", colour=colour, family=family)
        for i, line in enumerate(lines):
            self.text(x + 14, y + 24 + LINE_HEIGHT * (i + 1), line, size=12, colour=self.t["muted"])

    def text(self, x: int, y: int, s: str, size: int = 12, weight: str = "400", colour: str = "",
             family: str = FONT, anchor: str = "start") -> None:
        """Place one line of text. @return None"""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'style="fill:{colour or self.t["fg"]}" text-anchor="{anchor}">{escape(s)}</text>')

    def arrow(self, points: List[Tuple[int, int]], label: str = "", at: Tuple[int, int] = (0, 0),
              dashed: bool = False, anchor: str = "start") -> None:
        """Draw a polyline ending in an arrowhead, with an optional label at `at`. @return None"""
        pts = " ".join(f"{x},{y}" for x, y in points)
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<polyline points="{pts}" style="fill:none;stroke:{self.t["fg"]}" stroke-width="1.4"{dash} '
            f'marker-end="url(#arrow)"/>')
        if label:
            self.text(at[0], at[1], label, size=12, colour=self.t["muted"], anchor=anchor)

    def render(self) -> str:
        """@return the complete SVG document as a string."""
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
            f'aria-label="{escape(self.label)}">'
            f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'style="fill:{self.t["fg"]}"/></marker></defs>'
            f'<rect width="{self.w}" height="{self.h}" style="fill:{self.t["bg"]}"/>')
        return head + "".join(self.parts) + "</svg>\n"


def request_path(t: Dict[str, str]) -> Svg:
    """Figure 1: what a prompt and a tool call pass through before they touch the machine."""
    s = Svg(1000, 640, t, "A prompt passes a provenance check; every tool call passes four PreToolUse hooks; "
            "file tools then run directly while Bash runs inside the OS sandbox.")
    s.box(24, 24, 110, 52, "You")
    s.box(190, 24, 250, 72, "UserPromptSubmit", ("prompt-provenance.py", "adds context, never blocks"))
    s.box(500, 24, 150, 52, "Claude")
    s.box(720, 24, 256, 72, "Loaded at session start", ("CLAUDE.md", "memory/MEMORY.md (the index)"))
    s.arrow([(134, 50), (188, 50)], "prompt", (161, 42), anchor="middle")
    s.arrow([(440, 50), (498, 50)], "+ note", (469, 42), anchor="middle")
    s.arrow([(720, 60), (652, 60)], "context", (686, 76), dashed=True, anchor="middle")

    s.arrow([(575, 76), (575, 138)], "tool call", (585, 112))
    s.box(250, 140, 500, 150, "PreToolUse hooks: any one can block (exit 2)", accent=True)
    rows = [("guard-scope.py", "path outside the workspace roots?"),
            ("memory-load-check.py", "project named, its memory not Read?"),
            ("env-guard.py", "writing a real .env file?"),
            ("guard-command-shape.py", "chained rm -rf, or a mixed excluded line?")]
    for i, (hook, check) in enumerate(rows):
        y = 140 + 58 + 24 * i
        s.text(266, y, hook, family=MONO)
        s.text(460, y, check, colour=t["muted"])

    s.arrow([(330, 290), (205, 378)], "file tool", (226, 330), anchor="end")
    s.box(40, 380, 330, 110, "Claude's own file tools",
          ("Read, Edit, Write, Glob, Grep", "run outside the sandbox, so", "the hooks are their only boundary"))
    s.arrow([(670, 290), (670, 358)], "Bash", (680, 330))
    s.box(430, 360, 540, 136, "Bash sandbox, enforced by the OS",
          ("writes: working dir + $TMPDIR + allowWrite only",
           "network: allowedDomains only (strictAllowlist)",
           "reads: ~/.ssh, cloud keys and tokens denied",
           "excludedCommands (git fetch, push, pull) run outside it,",
           "through the normal permission prompt"), accent=True, dashed=True)

    s.text(40, 556, "After the turn", size=12, weight="600", colour=t["muted"])
    s.box(40, 566, 440, 56, "Stop: md-link-check.py", ("bare .md path in the reply → one forced rewrite",))
    s.box(530, 566, 440, 56, "PostCompact: save-session-summary.sh",
          ("compaction summary → memory/sessions/<date>.md",))
    return s


def memory_layers(t: Dict[str, str]) -> Svg:
    """Figure 2: which memory file loads when, and how lessons get written back."""
    s = Svg(1000, 450, t, "Memory loads in four moments: session start, a project mention, a trigger, "
            "and pre-clear, which writes lessons back into topic files and buckets.")
    cols = [(24, "1. Session start"), (268, "2. A project is named"),
            (512, "3. A trigger fires"), (756, "4. Before /clear")]
    for x, head in cols:
        s.text(x, 36, head, size=13, weight="600", colour=t["muted"])

    s.box(24, 56, 220, 60, "CLAUDE.md", ("rules + machine invariants",), mono_title=True)
    s.box(24, 136, 220, 114, "MEMORY.md", ("index, one line per entry", "Gates: the user's hard lines",
                                            "Principles: trigger → hub", "projects → PROJECTS.md"), mono_title=True)

    s.box(268, 56, 220, 60, "PROJECTS.md", ("roster: name, path, file",), mono_title=True)
    s.box(268, 146, 220, 60, "project_<name>.md", ("status + context",), mono_title=True)
    s.box(268, 236, 220, 60, "MEMORY-gotchas-<stack>", ("one stub per lesson",), mono_title=True)
    s.box(268, 326, 220, 60, "memory-load-check.py", ("blocks the 4th call if skipped",),
          accent=True, dashed=True, mono_title=True)
    s.arrow([(244, 222), (256, 222), (256, 86), (266, 86)], dashed=True)
    s.arrow([(378, 116), (378, 144)], "match", (388, 135))
    s.arrow([(378, 206), (378, 234)], "stack", (388, 225))
    s.arrow([(378, 326), (378, 298)], "checks a Read", (388, 316), dashed=True)

    s.box(512, 56, 220, 78, "principle_<name>.md", ("rule + warning signs", "+ the cases that taught it"),
          mono_title=True)
    s.box(512, 166, 220, 78, ".claude/rules/<stack>.md", ("injected when a matching", "file is opened"),
          mono_title=True)
    s.arrow([(134, 250), (134, 420), (500, 420), (500, 95), (510, 95)], "trigger named in MEMORY.md",
            (150, 412))

    s.box(756, 56, 220, 78, "pre-clear skill", ("friction, memories,", "todos, git"))
    s.box(756, 166, 220, 60, "feedback_<topic>.md", ("one fact per file",), mono_title=True)
    s.box(756, 256, 220, 60, "archive/", ("obsolete files move here",), mono_title=True)
    s.arrow([(866, 134), (866, 164)], "saves", (876, 155))
    s.arrow([(866, 226), (866, 254)], "when obsolete", (876, 245))
    s.arrow([(756, 206), (744, 206), (744, 270), (490, 270)], "stub routed to its bucket", (616, 262),
            anchor="middle")
    return s


FIGURES = {"request-path": request_path, "memory-layers": memory_layers}


def main() -> None:
    """Write <figure>-<theme>.svg for every figure and theme. @return None"""
    for name, build in FIGURES.items():
        for theme_name, theme in THEMES.items():
            path = OUT_DIR / f"{name}-{theme_name}.svg"
            path.write_text(build(theme).render(), encoding="utf-8")
            print(f"wrote {path.name}")


if __name__ == "__main__":
    main()
