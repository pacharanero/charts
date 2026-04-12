#!/usr/bin/env python3
"""Migrate MBCS v0.2 charts to v0.3 conventions.

v0.2: section labels and directions all live in **[BRACKETS]**.
v0.3: sections are ### headings, chords are plain [Am], directions are **BOLD**.

Transformations, in order:
1. A line consisting only of **[SECTION LABEL]** (optionally followed by a
   parenthetical) → ### SECTION LABEL.
2. Inline **[DIRECTION]** tokens (STOP, DEAD STOP, BVs, simile, etc.) →
   **DIRECTION**.
3. Remaining **[X]** tokens are treated as chords (or note runs) and the bold
   markup is stripped, leaving [X] in place.

Usage:
    scripts/migrate-v02-to-v03.py charts/Africa.md [more files...]
    scripts/migrate-v02-to-v03.py charts/              # whole directory
    scripts/migrate-v02-to-v03.py --dry-run charts/

Idempotent: running on an already-migrated file is a no-op.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECTION_PREFIXES = (
    "INTRO", "VERSE", "PRE-CHORUS", "CHORUS", "BRIDGE", "MIDDLE",
    "INTERLUDE", "SOLO", "GUITAR SOLO", "PIANO SOLO", "BASS SOLO",
    "HARMONICA SOLO", "DRUM SOLO", "BREAK", "OUTRO", "CODA", "VAMP",
    "TAG", "REFRAIN", "HOOK", "LINK", "RIFF", "ENDING", "INSTRUMENTAL",
)

DIRECTION_TOKENS = {
    "STOP", "DEAD STOP", "DROP", "BUILD", "ACAPELLA", "A CAPPELLA",
    "BVs", "BV", "simile", "SIMILE", "RIT", "ACCEL",
}
DIRECTION_TOKENS_CI = {d.lower() for d in DIRECTION_TOKENS}

SECTION_LINE_RE = re.compile(
    r'^(\s*)\*\*\[([^\]]+)\]\*\*(\s*\([^)]*\))?\s*$'
)
INLINE_BOLD_BRACKET_RE = re.compile(r'\*\*\[([^\]]+)\]\*\*')


def is_section_label(content: str) -> bool:
    c = content.strip().upper()
    for pref in SECTION_PREFIXES:
        if c == pref or c.startswith(pref + " ") or c.startswith(pref + "-"):
            return True
    return False


def is_direction(content: str) -> bool:
    return content.strip().lower() in DIRECTION_TOKENS_CI


def convert_line(line: str) -> str:
    # Preserve trailing whitespace (two-space line breaks)
    stripped = line.rstrip('\n')
    trailing_nl = line[len(stripped):]

    m = SECTION_LINE_RE.match(stripped)
    if m:
        indent, content, suffix = m.group(1), m.group(2).strip(), (m.group(3) or '').strip()
        if is_section_label(content):
            heading = f"{indent}### {content.upper()}"
            if suffix:
                heading += f" {suffix}"
            return heading + trailing_nl

    def repl(match: re.Match) -> str:
        inner = match.group(1).strip()
        if is_direction(inner):
            return f"**{inner}**"
        return f"[{inner}]"

    return INLINE_BOLD_BRACKET_RE.sub(repl, stripped) + trailing_nl


def migrate_file(path: Path, *, dry_run: bool = False) -> bool:
    original = path.read_text(encoding='utf-8')
    new_lines = [convert_line(line) for line in original.splitlines(keepends=True)]
    new_text = ''.join(new_lines)
    if new_text == original:
        return False
    if not dry_run:
        path.write_text(new_text, encoding='utf-8')
    return True


def iter_targets(paths: list[Path]) -> list[Path]:
    out = []
    for p in paths:
        if p.is_dir():
            out.extend(sorted(p.rglob('*.md')))
        else:
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    changed = 0
    unchanged = 0
    for target in iter_targets(args.paths):
        if migrate_file(target, dry_run=args.dry_run):
            print(f"{'would update' if args.dry_run else 'updated'}: {target}")
            changed += 1
        else:
            unchanged += 1
    print(f"\n{changed} file(s) changed, {unchanged} unchanged.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
