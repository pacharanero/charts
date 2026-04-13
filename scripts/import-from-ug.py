#!/usr/bin/env python3
"""Import a chord chart from Ultimate Guitar into MBCS v0.3 format.

Fetches the UG tab page, extracts the chord/lyric content from the embedded
JSON data, converts it to MBCS inline format (using the same column-alignment
logic as scripts/convert-chord-above-lyric.py), and writes a chart file into
charts/.

Usage:
  scripts/import-from-ug.py <URL>                          # write to charts/
  scripts/import-from-ug.py <URL> --to export-md/          # write to export-md/ instead
  scripts/import-from-ug.py <URL> --overwrite              # replace existing
  scripts/import-from-ug.py <URL> --name "My Title.md"     # override filename

Output is deliberately terse: only title, artist, and line counts print. The
lyric body is written straight to disk.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import runpy
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS_DIR = ROOT / "charts"


def fetch_url(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_ug_store(page_html: str) -> dict:
    """Ultimate Guitar embeds data in a <div class="js-store" data-content="...">
    attribute (HTML-escaped JSON)."""
    m = re.search(
        r'<div[^>]+class="js-store"[^>]+data-content="([^"]+)"',
        page_html,
    )
    if not m:
        raise RuntimeError("couldn't find js-store div — UG page format may have changed")
    raw = html.unescape(m.group(1))
    return json.loads(raw)


def extract_tab_content(store: dict) -> tuple[str, str, str]:
    """Return (title, artist, tab_content_with_ug_markers)."""
    tab = store.get("store", {}).get("page", {}).get("data", {}).get("tab", {})
    title = tab.get("song_name") or tab.get("name") or ""
    artist = tab.get("artist_name") or tab.get("artist") or ""

    tab_view = store.get("store", {}).get("page", {}).get("data", {}).get("tab_view", {})
    content = tab_view.get("wiki_tab", {}).get("content", "")
    if not content:
        raise RuntimeError("tab_view.wiki_tab.content is empty — is this a chord chart URL?")
    return title, artist, content


def ug_to_plain(content: str) -> str:
    """UG wraps chords in [ch]...[/ch] and tab sections in [tab]...[/tab]
    markers. Strip those to plain text with chord-above-lyric alignment
    preserved."""
    # Drop the [tab]/[/tab] wrappers but keep their inner content.
    content = re.sub(r'\[/?tab\]', '', content)
    # Chords stay in brackets but drop the [ch]/[/ch] wrapping: G -> G (bracket
    # added later by column alignment).
    content = re.sub(r'\[ch\]([^\[]+?)\[/ch\]', r'\1', content)
    # Strip any other UG formatting markers just in case.
    content = re.sub(r'\[/?(?:b|i|u|em)\]', '', content)
    # Normalize CRLF to LF.
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    return content


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--to", type=Path, default=CHARTS_DIR, help="Output directory (default: charts/)")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--name", help="Override the output filename (default: <title>.md)")
    args = ap.parse_args(argv)

    try:
        page = fetch_url(args.url)
        store = extract_ug_store(page)
        title, artist, raw_content = extract_tab_content(store)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    plain = ug_to_plain(raw_content)

    # Build a synthetic MBCS-input file: ***Title*** / *Artist* / body
    header = f"***{title}***\n*{artist}*\n\n"
    synthetic = header + plain

    # Run it through the column-alignment + MBCS pipeline
    align_ns = runpy.run_path(str(ROOT / "scripts" / "convert-chord-above-lyric.py"), run_name="align_module")
    mbcs_ns = runpy.run_path(str(ROOT / "scripts" / "convert-exports.py"), run_name="mbcs_module")

    # Write synthetic to a temp file, do the two passes
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(synthetic)
        tmp_path = Path(tmp.name)

    try:
        merged_lines = align_ns["transform"](tmp_path.read_text(encoding="utf-8").splitlines(keepends=True))
        tmp_path.write_text("".join(merged_lines), encoding="utf-8")
        out_text, skip = mbcs_ns["process_file"](tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    if out_text is None:
        print(f"ERROR: MBCS converter refused the result — {skip}", file=sys.stderr)
        print(f"Title: {title}\nArtist: {artist}", file=sys.stderr)
        return 2

    filename = args.name or f"{title}.md"
    args.to.mkdir(parents=True, exist_ok=True)
    dest = args.to / filename
    if dest.exists() and not args.overwrite:
        print(f"ERROR: {dest} already exists (use --overwrite)", file=sys.stderr)
        return 3
    dest.write_text(out_text, encoding="utf-8")

    inline_chords = len(re.findall(r'\[[A-G][b#]?[^\]]*\]', out_text))
    lines = sum(1 for ln in out_text.splitlines() if ln.strip())
    print(f"OK  {dest.relative_to(ROOT)}  [{inline_chords} chords, {lines} non-blank lines]")
    print(f"    title:  {title}")
    print(f"    artist: {artist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
