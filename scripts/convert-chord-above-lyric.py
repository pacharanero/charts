#!/usr/bin/env python3
"""Convert chord-above-lyric charts to MBCS inline-chord format.

Input files in export-md/ where each lyric line is preceded by a chord-row:

    G                  F
    The lights are on, but you're not home
    C         G
    Your mind is not your own

The column position of each chord name in the chord-row is mapped onto the
lyric line below, and the chord is inlined as [Chord] at that position.

    [G]The lights are on, [F]but you're not home
    [C]Your mind [G]is not your own

Detection heuristic: a "chord row" is a line composed almost entirely of
whitespace plus short chord-shaped tokens (root note + optional modifiers,
optional slash bass). The line immediately following, if non-empty and not
itself a chord row, is treated as its lyric.

Standalone chord rows (no lyric beneath) are emitted as `[Chord] [Chord]`
sequences on their own line, good for intros / progressions.

The output is also passed through the same cleanup regex set as
scripts/convert-exports.py before writing, so title/artist/sections/
frontmatter land in MBCS v0.3 shape.

Usage:
  scripts/convert-chord-above-lyric.py                      # dry-run all
  scripts/convert-chord-above-lyric.py --apply              # write to charts/
  scripts/convert-chord-above-lyric.py --apply --delete     # also rm source
  scripts/convert-chord-above-lyric.py --only "Foo.md"
  scripts/convert-chord-above-lyric.py --min-inline 2       # tune threshold
"""
from __future__ import annotations

import argparse
import re
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = ROOT / "export-md"
CHARTS_DIR = ROOT / "charts"

# A chord token: root (A-G) + optional accidental + optional suffix chars +
# optional slash bass.
CHORD_TOKEN_RE = re.compile(
    r'^[A-G](?:#|b)?'
    r'(?:m|M|maj|min|dim|aug|sus|add|\+|-)?'
    r'(?:\d+)?'
    r'(?:(?:[#b+\-]\d+|\(\w+\))*)'
    r'(?:/[A-G](?:#|b)?)?$'
)


def is_chord_token(tok: str) -> bool:
    return bool(CHORD_TOKEN_RE.match(tok))


def chord_tokens_with_cols(line: str) -> list[tuple[int, str]]:
    """Return a list of (column, chord) for each chord token on the line.

    A line qualifies as a chord row only if >=75% of its non-whitespace
    tokens are chord-shaped, there is at least one chord token, and the
    stripped content contains no sentence-like punctuation (.!? or trailing
    comma-lowercase)."""
    stripped = line.strip()
    if not stripped:
        return []
    # Exclude lyric-ish lines: contain typical English punctuation
    if re.search(r'[.!?]', stripped):
        return []
    tokens = re.findall(r'\S+', line)
    if not tokens:
        return []
    chord_count = sum(1 for t in tokens if is_chord_token(t))
    if chord_count == 0 or chord_count / len(tokens) < 0.75:
        return []
    # Find the column of each chord token in the original line
    out: list[tuple[int, str]] = []
    cursor = 0
    for tok in tokens:
        idx = line.find(tok, cursor)
        if idx < 0:
            continue
        if is_chord_token(tok):
            out.append((idx, tok))
        cursor = idx + len(tok)
    return out


def merge_chord_into_lyric(chord_row: str, lyric: str) -> str:
    """Insert [Chord] tokens at the column positions into the lyric."""
    chords = chord_tokens_with_cols(chord_row)
    if not chords:
        return lyric.rstrip()
    lyric_rstripped = lyric.rstrip('\n').rstrip()
    # Work from rightmost to leftmost so earlier insertions don't shift
    # the column positions of later ones.
    result = lyric_rstripped
    for col, chord in sorted(chords, key=lambda p: -p[0]):
        if col >= len(result):
            # Chord falls past the end of the lyric — append with a space
            result = result.ljust(col) + f"[{chord}]"
        else:
            # Snap to nearest word start at or before col, so chords don't
            # land mid-word. If col is inside a word, back up to the start
            # of that word; if we're between words, keep col.
            insert_at = col
            # Back up to start of the current word if we're inside one
            while insert_at > 0 and result[insert_at - 1] != ' ' and result[insert_at] != ' ':
                insert_at -= 1
            result = result[:insert_at] + f"[{chord}]" + result[insert_at:]
    return result


def standalone_chord_line(chord_row: str) -> str:
    """A chord row with no lyric beneath → print as [C] [G] [F] progression."""
    chords = chord_tokens_with_cols(chord_row)
    if not chords:
        return chord_row.rstrip()
    return " ".join(f"[{c}]" for _, c in chords)


def transform(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        chords = chord_tokens_with_cols(line)
        if chords:
            # Look ahead for a lyric line
            j = i + 1
            # Allow zero blank lines between chord row and lyric
            if j < len(lines):
                nxt = lines[j].rstrip('\n')
                nxt_chords = chord_tokens_with_cols(nxt)
                if nxt.strip() and not nxt_chords:
                    merged = merge_chord_into_lyric(line, nxt)
                    out.append(merged + "\n")
                    i = j + 1
                    continue
            # No lyric — standalone progression
            out.append(standalone_chord_line(line) + "\n")
            i += 1
        else:
            out.append(lines[i])
            i += 1
    return out


def count_inline_brackets(text: str) -> int:
    return len(re.findall(r'\[[A-G][b#]?[^\]]*\]', text))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--min-inline", type=int, default=3,
                    help="Minimum inline chord brackets produced to count as a successful conversion")
    args = ap.parse_args(argv)

    # Import convert-exports.py for the downstream MBCS cleanup
    mbcs_ns = runpy.run_path(str(ROOT / "scripts" / "convert-exports.py"), run_name="mbcs_module")

    targets = sorted(EXPORT_DIR.glob("*.md"))
    if args.only:
        targets = [p for p in targets if any(s in p.name for s in args.only)]

    converted = low_yield = skipped = errors = 0
    for src in targets:
        raw = src.read_text(encoding="utf-8")
        lines = raw.splitlines(keepends=True)

        # Pass 1: column-align chords into lyrics
        merged_lines = transform(lines)
        merged_text = "".join(merged_lines)

        # Pass 2: write merged text to a virtual file and run through MBCS cleanup
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
            tmp.write(merged_text)
            tmp_path = Path(tmp.name)
        try:
            out_text, skip_reason = mbcs_ns["process_file"](tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        if out_text is None:
            print(f"  --  {src.name}  [{skip_reason}]")
            skipped += 1
            continue

        inline = count_inline_brackets(out_text)
        if inline < args.min_inline:
            print(f"  ??  {src.name}  [yielded {inline} inline chords — likely needs manual review]")
            low_yield += 1
            continue

        dest = CHARTS_DIR / src.name
        if dest.exists() and not args.overwrite:
            print(f"  --  {src.name}  [charts/{src.name} already exists]")
            skipped += 1
            continue

        if args.apply:
            dest.write_text(out_text, encoding="utf-8")
            if args.delete:
                src.unlink()
            print(f"  OK  {src.name}  [{inline} chords inlined]")
        else:
            print(f"  OK  {src.name}  [{inline} chords inlined, dry-run]")
        converted += 1

    print(f"\n{converted} converted, {low_yield} low-yield (needs review), {skipped} skipped, {errors} errors")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
