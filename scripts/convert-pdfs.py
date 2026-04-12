#!/usr/bin/env python3
"""Convert text-based PDFs in export-md/ to markdown using pdftotext.

Scanned/image-only PDFs are detected (by extracted-text length) and left in
place for manual handling.

Usage:
  scripts/convert-pdfs.py                      # dry-run
  scripts/convert-pdfs.py --apply              # write .md alongside source
  scripts/convert-pdfs.py --apply --delete     # also delete the source PDF
  scripts/convert-pdfs.py --min-chars 100      # tweak scanned-PDF threshold
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = ROOT / "export-md"
PDFTOTEXT = shutil.which("pdftotext")


def extract_text(pdf: Path) -> tuple[str | None, str | None]:
    """Return (text, error)."""
    result = subprocess.run(
        [PDFTOTEXT, "-layout", "-nopgbrk", str(pdf), "-"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return None, result.stderr.strip() or "pdftotext failed"
    return result.stdout, None


def to_markdown(text: str) -> str:
    """Light cleanup to make extracted text more markdown-friendly."""
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.rstrip()
        # Collapse runs of more than 2 internal spaces to a tab-style gap,
        # so that chord-alignment in lead sheets is preserved somewhat.
        lines.append(stripped)
    # Collapse 3+ blank lines to 2.
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank > 2:
                continue
        else:
            blank = 0
        out.append(ln)
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--min-chars", type=int, default=80,
                    help="Extracted text shorter than this is treated as image-only (default: 80)")
    args = ap.parse_args(argv)

    if not PDFTOTEXT:
        print("ERROR: pdftotext not found", file=sys.stderr)
        return 2

    targets = sorted(EXPORT_DIR.glob("*.pdf"))
    if args.only:
        targets = [p for p in targets if any(s in p.name for s in args.only)]

    ok = scanned = fail = skipped = 0
    for pdf in targets:
        dest = EXPORT_DIR / (pdf.stem + ".md")
        if dest.exists() and not args.overwrite:
            print(f"  --  {pdf.name}  [.md already exists]")
            skipped += 1
            continue
        text, err = extract_text(pdf)
        if err or text is None:
            print(f"  !!  {pdf.name}  [{err}]")
            fail += 1
            continue
        if len(text.strip()) < args.min_chars:
            print(f"  >>  {pdf.name}  [scanned/image-only, {len(text.strip())} chars — leave for manual]")
            scanned += 1
            continue
        md = to_markdown(text)
        if args.apply:
            dest.write_text(md, encoding="utf-8")
            if args.delete:
                pdf.unlink()
            print(f"  OK  {pdf.name}  ->  {dest.name}")
        else:
            print(f"  OK  {pdf.name}  ->  {dest.name}  [dry-run]")
        ok += 1

    print(f"\n{ok} text-PDFs converted, {scanned} image-only (manual), {fail} failed, {skipped} already .md")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
