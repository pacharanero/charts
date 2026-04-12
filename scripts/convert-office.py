#!/usr/bin/env python3
"""Convert Word / ODT exports in export-md/ to markdown.

Pipeline:
  .docx, .odt              -> pandoc -> .md
  .doc  (legacy binary)    -> soffice -> .docx -> pandoc -> .md

The resulting .md lands alongside the source in export-md/ so it can then be
processed by scripts/convert-exports.py into MBCS v0.3 format.

Usage:
  scripts/convert-office.py                  # dry-run
  scripts/convert-office.py --apply          # convert and write .md files
  scripts/convert-office.py --apply --delete # also delete the original binary
  scripts/convert-office.py --only "Foo.doc" # single file
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = ROOT / "export-md"

PANDOC = shutil.which("pandoc")
SOFFICE = shutil.which("soffice") or shutil.which("libreoffice")


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def doc_to_docx(src: Path, tmpdir: Path) -> Path | None:
    """Convert legacy .doc to .docx via headless LibreOffice."""
    result = run(
        [SOFFICE, "--headless", "--convert-to", "docx", "--outdir", str(tmpdir), str(src)],
        cwd=tmpdir,
    )
    if result.returncode != 0:
        return None
    docx = tmpdir / (src.stem + ".docx")
    return docx if docx.exists() else None


def docx_to_md(src: Path, dest: Path) -> bool:
    """Convert .docx or .odt to markdown via pandoc."""
    result = run([
        PANDOC,
        "-f", "docx" if src.suffix.lower() == ".docx" else "odt",
        "-t", "gfm+hard_line_breaks",
        "--wrap=none",
        "-o", str(dest),
        str(src),
    ])
    return result.returncode == 0 and dest.exists()


def convert_one(src: Path, tmpdir: Path) -> tuple[str | None, str | None]:
    """Return (md_text, error). One of them is None."""
    ext = src.suffix.lower()
    out_md = tmpdir / (src.stem + ".md")

    if ext == ".doc":
        docx = doc_to_docx(src, tmpdir)
        if not docx:
            return None, "soffice failed to convert .doc"
        if not docx_to_md(docx, out_md):
            return None, "pandoc failed on intermediate .docx"
    elif ext in (".docx", ".odt"):
        if not docx_to_md(src, out_md):
            return None, f"pandoc failed on {ext}"
    else:
        return None, f"unsupported extension {ext}"

    try:
        return out_md.read_text(encoding="utf-8"), None
    except Exception as exc:
        return None, f"read failed: {exc}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="Write .md outputs")
    ap.add_argument("--delete", action="store_true", help="Delete the binary source after successful conversion")
    ap.add_argument("--only", action="append", default=[], help="Substring filter")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing .md in export-md/")
    args = ap.parse_args(argv)

    if not PANDOC:
        print("ERROR: pandoc not found in PATH", file=sys.stderr)
        return 2
    if not SOFFICE:
        print("WARNING: soffice/libreoffice not found; .doc files will be skipped", file=sys.stderr)

    targets: list[Path] = []
    for ext in (".doc", ".docx", ".odt"):
        targets.extend(sorted(EXPORT_DIR.glob(f"*{ext}")))
    if args.only:
        targets = [p for p in targets if any(s in p.name for s in args.only)]

    ok = fail = skipped = 0
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        for src in targets:
            dest = EXPORT_DIR / (src.stem + ".md")
            if dest.exists() and not args.overwrite:
                print(f"  --  {src.name}  [.md already exists]")
                skipped += 1
                continue
            md, err = convert_one(src, tmpdir)
            if err:
                print(f"  !!  {src.name}  [{err}]")
                fail += 1
                continue
            if args.apply:
                dest.write_text(md, encoding="utf-8")
                if args.delete:
                    src.unlink()
                print(f"  OK  {src.name}  ->  {dest.name}")
            else:
                print(f"  OK  {src.name}  ->  {dest.name}  [dry-run]")
            ok += 1

    print(f"\n{ok} converted, {fail} failed, {skipped} skipped (already have .md)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
