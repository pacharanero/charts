#!/usr/bin/env python3
"""Convert Google-Docs-exported MBCS charts from export-md/ into MBCS v0.3
charts ready to live in charts/.

The transforms are deterministic and idempotent. Anything the script can't
cleanly convert (chord-above-lyric layouts, bar-grid heavy charts, riff-only
files) is left in export-md/ with a reason printed in the report.

Transforms:
  1. Unescape Google-Docs markdown escapes: \\[ \\] \\# \\- \\! \\~ \\\\
  2. Strip the outer *italic* wrapping that Google Docs applies line-by-line
     when the body font is italic.
  3. First non-blank line of ***Title*** -> H1.
  4. Following *Artist* line -> H2.
  5. Standalone ***[SECTION]*** or *[SECTION]* -> ### SECTION.
  6. Mixed lines like "***[VERSE 1]** lyric..." split into a heading plus the
     remaining lyric on the next line.
  7. Inline bold chord brackets: **[Am]** -> [Am].
  8. Consecutive tab lines (prefixes e|, B|, G|, D|, A|, E|, b|) are folded
     into a fenced ```text block.
  9. Lyric lines are given a trailing two-space for Markdown line-break
     behaviour, if they don't already have one.
 10. YAML frontmatter is added / merged with: title, slug, hide: [toc],
     category: Guitar Charts. Tags are left empty for the user to fill in.

Skip heuristics (conservative; false negatives preferred over false positives):
  - More than 3 "chord-above-lyric" pairs: a line dominated by whitespace-
    separated short chord tokens immediately followed by a lyric line.
  - Bar-grid density: more than 6 lines matching `| chord | ... |`.

Usage:
  scripts/convert-exports.py                     # dry-run all .md in export-md/
  scripts/convert-exports.py --apply             # write to charts/ for real
  scripts/convert-exports.py --apply --delete    # also rm the export-md/ copy
  scripts/convert-exports.py --only "Africa.md"  # limit to specific files
  scripts/convert-exports.py --force "Bad As Me.md"  # convert even if skip-heuristic hits
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = ROOT / "export-md"
CHARTS_DIR = ROOT / "charts"

SECTION_PREFIXES = (
    "INTRO", "VERSE", "PRE-CHORUS", "CHORUS", "BRIDGE", "MIDDLE",
    "INTERLUDE", "SOLO", "GUITAR SOLO", "PIANO SOLO", "BASS SOLO",
    "HARMONICA SOLO", "DRUM SOLO", "BREAK", "OUTRO", "CODA", "VAMP",
    "TAG", "REFRAIN", "HOOK", "LINK", "RIFF", "ENDING", "INSTRUMENTAL",
    "REPRISE", "MODIFIED CHORUS",
)

DIRECTION_TOKENS = {
    "stop", "dead stop", "drop", "build", "acapella", "a cappella",
    "bvs", "bv", "simile", "rit", "accel", "phaser", "break", "hits",
}

TAB_LINE_RE = re.compile(r'^\s*[eEbBgGdDaA]\|')

BOLD_BRACKET_RE = re.compile(r'\*\*\[([^\]]+)\]\*\*')
# Standalone section-label line:
#   ***[X]***, ***[X] (stuff)***, ***[X]** (stuff)*,  *[X]*, **[X]**
SECTION_LINE_RE = re.compile(
    r'^\s*(?:\*\*\*|\*\*|\*)\s*\\?\[([^\]]+?)\\?\]'
    r'(?:\s*(?:\*\*\*|\*\*|\*))?'            # optional close of bold/italic after bracket
    r'\s*(\([^)]*\))?'                        # optional parenthetical
    r'\s*(?:\*\*\*|\*\*|\*)?\s*$'             # optional trailing emphasis close
)
# Mixed heading-then-lyric: "***[VERSE 1]** lyric..." / "*[VERSE 1]* lyric..." /
# "***[SOLO] stuff***" where 'stuff' contains inline chords / notes.
MIXED_HEADING_RE = re.compile(
    r'^\s*(?:\*\*\*|\*\*|\*)\s*\\?\[([^\]]+?)\\?\]'
    r'(?:\s*(?:\*\*|\*))?'                    # optional close of inner bold
    r'\s+(.+?)\s*(?:\*\*\*|\*\*|\*)?\s*$'
)
# Title: ***Song Title*** or ***Song Title -*** or ***Song Title (Key D)***
TITLE_RE = re.compile(r'^\s*\*\*\*([^*\[\]]+?)\\?-?\s*\*\*\*?\s*(.*?)\s*\*?\s*$')
# Artist: *Artist Name*
ARTIST_RE = re.compile(r'^\s*\*([^*\[\]]+?)\*\s*$')
# Standalone performance direction in bold italics: ***(build)*** / ***Phaser***
DIRECTION_LINE_RE = re.compile(r'^\s*\*\*\*([^*\[\]]+?)\*\*\*\s*$')
# Bracketless mixed heading: ***chorus** lyrics...*   ***Verse 1** lyrics...*
MIXED_NOBRACKET_RE = re.compile(
    r'^\s*\*\*\*([A-Za-z][\w \-]*?)\*\*\s+(.+?)\s*\*?\s*$'
)
# Image-embedded (Google Docs inlined image) — can't auto-convert
IMAGE_EMBED_RE = re.compile(r'^\s*!\[\]\[image\d+\]')


def unescape(s: str) -> str:
    """Reverse Google Docs markdown escaping."""
    for esc, raw in [
        ('\\[', '['), ('\\]', ']'), ('\\#', '#'), ('\\-', '-'),
        ('\\!', '!'), ('\\~', '~'), ('\\.', '.'), ('\\(', '('),
        ('\\)', ')'), ('\\\\', '\\'),
    ]:
        s = s.replace(esc, raw)
    return s


def strip_outer_italic(line: str) -> str:
    """If a line is wrapped in a single pair of outer * markers, strip them."""
    stripped = line.rstrip()
    trailing = line[len(stripped):]
    core = stripped.strip()
    if not core:
        return line
    # Don't touch bold/triple-star wrappers on this pass.
    if core.startswith('***') or core.startswith('**'):
        return line
    if core.startswith('*') and core.endswith('*') and len(core) >= 2:
        inner = core[1:-1]
        # Only strip if we don't unbalance bold markers.
        if inner.count('**') % 2 == 0:
            indent = stripped[:len(stripped) - len(stripped.lstrip())]
            return indent + inner + trailing
    return line


def normalise_section_name(name: str) -> str | None:
    """Return canonical ALL-CAPS section name, or None if not a recognised section."""
    c = name.strip().upper()
    # Strip common framing chars
    c = c.strip('"\u201c\u201d\'\u2018\u2019 ')
    for pref in SECTION_PREFIXES:
        if c == pref or c.startswith(pref + ' ') or c.startswith(pref + '-'):
            return c
    # Allow a minimal set of common variants
    if c in {"MODIFIED CHORUS", "FINAL CHORUS", "LAST CHORUS", "HALF CHORUS"}:
        return c
    return None


def convert_title_artist(lines: list[str]) -> tuple[str | None, str | None, int]:
    """Return (title, artist, lines_consumed)."""
    title = artist = None
    idx = 0
    # Skip leading blank lines
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx < len(lines):
        first = unescape(lines[idx]).strip()
        # Combined "***Title -** Artist*" pattern
        combined = re.match(r'^\*\*\*([^*]+?)\s*-\s*\*\*\s*([^*]+?)\s*\*\s*$', first)
        if combined:
            title = combined.group(1).strip().rstrip('-').strip()
            artist = combined.group(2).strip()
            idx += 1
            return title, artist, idx
        # Plain italic/bold-italic title: ***Title***
        m = TITLE_RE.match(first)
        if m:
            t = m.group(1).strip().rstrip('-').strip()
            extra = (m.group(2) or '').strip()
            title = f"{t} {extra}".strip() if extra else t
            idx += 1
        else:
            # Bold-only title from pandoc: **Title**
            m2 = re.match(r'^\*\*([^*\[\]]+?)\*\*\s*$', first)
            if m2:
                title = m2.group(1).strip().rstrip('-').strip()
                idx += 1
    # Skip blanks between title and artist
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx < len(lines) and title is not None:
        candidate = unescape(lines[idx]).strip()
        # Italic artist: *Artist*
        m = ARTIST_RE.match(candidate)
        if m:
            artist = m.group(1).strip()
            idx += 1
        # Bold artist: **Artist**
        elif re.match(r'^\*\*([^*\[\]]+?)\*\*\s*$', candidate):
            artist = re.match(r'^\*\*([^*\[\]]+?)\*\*\s*$', candidate).group(1).strip()
            idx += 1
        # Plain artist line (from pandoc): short, no chord brackets, no special
        # markup, starts with a capital letter.
        elif (
            candidate
            and len(candidate) < 80
            and '[' not in candidate
            and '|' not in candidate
            and not candidate.startswith('#')
            and re.match(r'^[A-Z"\'(]', candidate)
            and re.search(r'[A-Za-z]', candidate)
        ):
            artist = candidate.rstrip('.').strip()
            idx += 1
    return title, artist, idx


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s


@dataclass
class SkipReason:
    name: str
    reason: str


@dataclass
class Report:
    converted: list[str] = field(default_factory=list)
    skipped: list[SkipReason] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)


def detect_skip(lines: list[str]) -> str | None:
    """Return a skip reason string, or None to proceed."""
    # Image-only exports (Google Docs inlined PNG)
    if any(IMAGE_EMBED_RE.match(ln) for ln in lines[:5]):
        return "image-only export (chart was a PNG in Google Docs)"
    # Bar-grid density
    bar_grid_re = re.compile(r'^\s*\*?\s*\|\s*(?:[A-G][b#]?[\w/#+]*|%|\s*/\s*)[^|]*\|')
    bar_lines = sum(1 for ln in lines if bar_grid_re.match(ln))
    if bar_lines > 6:
        return f"bar-grid heavy ({bar_lines} lines)"

    # Chord-above-lyric pattern: line of only short chord tokens (tab/space
    # separated) followed by a plausible lyric line.
    chord_only_re = re.compile(
        r'^\s*\*?\s*(?:[A-G][b#]?[\w/#+]{0,8})(?:\s+[A-G][b#]?[\w/#+]{0,8}){1,}\s*\*?\s*$'
    )
    pairs = 0
    for i, ln in enumerate(lines[:-1]):
        if chord_only_re.match(ln):
            nxt = lines[i + 1].strip()
            # next line looks like a lyric (has some letters, isn't another chord line)
            if nxt and not chord_only_re.match(lines[i + 1]) and len(nxt) > 15:
                pairs += 1
    if pairs > 3:
        return f"chord-above-lyric layout ({pairs} pairs)"

    # Tab-only files (predominantly tablature, no lyrics)
    tab_lines = sum(1 for ln in lines if TAB_LINE_RE.match(ln))
    non_tab_content = sum(
        1 for ln in lines
        if ln.strip() and not TAB_LINE_RE.match(ln) and ln.strip() not in ('|', '')
    )
    if tab_lines > 6 and non_tab_content < 5:
        return f"tab-only ({tab_lines} tab lines, {non_tab_content} other)"

    # Low inline-chord density: the file has lyrics but chords aren't inline
    # in MBCS style. Common for pandoc-converted legacy Word docs where chords
    # live on separate lines above the lyrics. These need manual chord
    # placement to become MBCS-compliant.
    joined = "".join(lines)
    body_chars = len(joined.strip())
    inline_chord_brackets = len(
        re.findall(r'\w\s*\[[A-G][b#]?[^\]]*\]|\[[A-G][b#]?[^\]]*\]\s*\w', joined)
    )
    if body_chars > 400 and inline_chord_brackets < 3:
        return f"low inline-chord density ({inline_chord_brackets} inline chords)"

    return None


def fold_tab_blocks(lines: list[str]) -> list[str]:
    """Wrap runs of tab lines in ```text fences."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        if TAB_LINE_RE.match(lines[i]):
            j = i
            while j < len(lines) and (TAB_LINE_RE.match(lines[j]) or not lines[j].strip()):
                j += 1
            # Trim trailing blanks from block
            block_end = j
            while block_end > i and not lines[block_end - 1].strip():
                block_end -= 1
            out.append("```text\n")
            for k in range(i, block_end):
                out.append(lines[k].rstrip() + "\n" if not lines[k].endswith('\n') else lines[k])
            out.append("```\n")
            i = block_end
        else:
            out.append(lines[i])
            i += 1
    return out


def ensure_trailing_br(line: str) -> str:
    """Add two trailing spaces before the newline if the line is plain prose
    (not a heading, not blank, not inside a code fence)."""
    if not line.endswith('\n'):
        return line
    content = line[:-1]
    stripped = content.rstrip()
    if not stripped:
        return line
    if stripped.startswith('#') or stripped.startswith('```'):
        return line
    if stripped.endswith('  '):
        return line
    # Don't double-add if line already ends with two spaces before newline
    if content.endswith('  '):
        return line
    return stripped + '  \n'


def convert_body(lines: list[str]) -> list[str]:
    """Apply the per-line cleanup transforms and return new lines."""
    out: list[str] = []
    for raw in lines:
        line = unescape(raw)

        # Standalone section label
        m = SECTION_LINE_RE.match(line)
        if m:
            sec = normalise_section_name(m.group(1))
            suffix = (m.group(2) or '').strip()
            if sec:
                heading = f"### {sec}"
                if suffix:
                    heading += f" {suffix}"
                out.append(heading + "\n")
                continue

        # Mixed heading + lyric
        m = MIXED_HEADING_RE.match(line)
        if m and normalise_section_name(m.group(1)):
            sec = normalise_section_name(m.group(1))
            rest = m.group(2).strip().strip('*').strip()
            # If the trailing text is short, chord-free, and doesn't look like a
            # lyric (no verbs / long prose), fold it into the heading.
            is_annotation = (
                rest
                and len(rest) <= 40
                and '[' not in rest
                and not re.search(r'\b(the|and|you|she|he|we|they|I|a|an|to)\b', rest, re.I)
            )
            if is_annotation:
                # Wrap in parens if not already
                if not (rest.startswith('(') and rest.endswith(')')):
                    rest = f"({rest})"
                out.append(f"### {sec} {rest}\n")
                continue
            out.append(f"### {sec}\n")
            if rest:
                rest_line = rest + "\n"
                rest_line = BOLD_BRACKET_RE.sub(r'[\1]', rest_line)
                rest_line = strip_outer_italic(rest_line)
                out.append(rest_line)
            continue

        # Bracketless mixed heading: ***chorus** lyric text*
        m = MIXED_NOBRACKET_RE.match(line)
        if m and normalise_section_name(m.group(1)):
            sec = normalise_section_name(m.group(1))
            rest = m.group(2).strip().strip('*').strip()
            is_annotation = (
                rest and len(rest) <= 40 and '[' not in rest
                and not re.search(r'\b(the|and|you|she|he|we|they|I|a|an|to)\b', rest, re.I)
            )
            if is_annotation:
                if not (rest.startswith('(') and rest.endswith(')')):
                    rest = f"({rest})"
                out.append(f"### {sec} {rest}\n")
                continue
            out.append(f"### {sec}\n")
            if rest:
                rest_line = rest + "\n"
                rest_line = BOLD_BRACKET_RE.sub(r'[\1]', rest_line)
                rest_line = strip_outer_italic(rest_line)
                out.append(rest_line)
            continue

        # Standalone direction line in bold italic: ***Phaser***, ***(build)***,
        # ***Intro***, ***Chorus*** (no brackets — promote to heading if section)
        m = DIRECTION_LINE_RE.match(line)
        if m:
            content = m.group(1).strip()
            sec = normalise_section_name(content)
            if sec:
                out.append(f"### {sec}\n")
                continue
            out.append(f"**{content}**\n")
            continue

        # Inline bold chord brackets -> plain brackets
        line = BOLD_BRACKET_RE.sub(r'[\1]', line)
        # Strip outer italic wrapping
        line = strip_outer_italic(line)
        out.append(line)
    return out


def build_frontmatter(title: str, existing: dict | None = None) -> str:
    slug = slugify(title)
    # Minimal, consistent frontmatter
    return (
        f"---\n"
        f'slug: {slug}\n'
        f'title: "{title}"\n'
        f"tags: []\n"
        f"category: Guitar Charts\n"
        f"hide:\n"
        f"  - toc\n"
        f"---\n"
    )


def process_file(src: Path) -> tuple[str | None, str | None]:
    """Return (new_text, skip_reason). new_text is None if skipped."""
    raw = src.read_text(encoding='utf-8')
    lines = raw.splitlines(keepends=True)

    skip = detect_skip(lines)
    if skip:
        return None, skip

    # Extract title/artist from first 2 meaningful lines (pre-unescape-aware)
    title, artist, consumed = convert_title_artist(lines)
    rest = lines[consumed:]

    # Per-line cleanup
    rest = convert_body(rest)
    # Fold tab blocks
    rest = fold_tab_blocks(rest)
    # Trailing line-break spaces for lyric lines (skip heading and fenced blocks)
    out: list[str] = []
    in_fence = False
    for ln in rest:
        if ln.lstrip().startswith('```'):
            in_fence = not in_fence
            out.append(ln)
            continue
        if in_fence:
            out.append(ln)
            continue
        out.append(ensure_trailing_br(ln))
    rest = out

    if not title:
        return None, "no title detected"

    fm = build_frontmatter(title)
    body = f"\n# {title}\n"
    if artist:
        body += f"\n## {artist}\n"
    body += "\n" + "".join(rest)
    # Collapse 3+ blank lines to 2
    body = re.sub(r'\n{3,}', '\n\n', body)
    if not body.endswith('\n'):
        body += '\n'
    return fm + body, None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="Specific files to process (default: all .md in export-md/)")
    ap.add_argument("--apply", action="store_true", help="Actually write to charts/")
    ap.add_argument("--delete", action="store_true", help="Delete the export-md/ source after writing")
    ap.add_argument("--only", action="append", default=[], help="Only process files whose name contains this string")
    ap.add_argument("--force", action="append", default=[], help="Force conversion even if skip heuristic fires (match by name substring)")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing charts/<name> if present")
    args = ap.parse_args(argv)

    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        targets = sorted(EXPORT_DIR.glob("*.md"))

    if args.only:
        targets = [p for p in targets if any(sub in p.name for sub in args.only)]

    report = Report()
    for src in targets:
        force = any(sub in src.name for sub in args.force)
        try:
            new_text, skip = process_file(src)
            if skip and not force:
                report.skipped.append(SkipReason(src.name, skip))
                continue
            if new_text is None:
                # Either skipped or no title; if forced and no title, that's an error.
                report.errors.append((src.name, skip or "unknown"))
                continue
            dest = CHARTS_DIR / src.name
            if dest.exists() and not args.overwrite:
                report.skipped.append(SkipReason(src.name, f"charts/{src.name} already exists (use --overwrite)"))
                continue
            if args.apply:
                dest.write_text(new_text, encoding='utf-8')
                if args.delete:
                    src.unlink()
                report.converted.append(src.name)
            else:
                report.converted.append(src.name + "  [dry-run]")
        except Exception as exc:  # pragma: no cover
            report.errors.append((src.name, f"{type(exc).__name__}: {exc}"))

    print(f"Converted: {len(report.converted)}")
    for name in report.converted:
        print(f"  OK   {name}")
    print(f"\nSkipped: {len(report.skipped)}")
    for s in report.skipped:
        print(f"  --   {s.name}  [{s.reason}]")
    if report.errors:
        print(f"\nErrors: {len(report.errors)}")
        for name, err in report.errors:
            print(f"  !!   {name}  [{err}]")
    print(f"\n(Use --apply to write, --delete to also remove source, --overwrite to replace existing charts.)")
    return 0 if not report.errors else 1


if __name__ == "__main__":
    sys.exit(main())
