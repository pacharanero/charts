#!/usr/bin/env python3
"""Final cleanup: rename remaining Title Case files and handle collisions."""
import re, unicodedata
from pathlib import Path

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"

def to_slug(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.replace("'", "").replace("'", "").replace("'", "").replace("'", "").replace("`", "")
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    name = re.sub(r"-{2,}", "-", name)
    return name

def get_disambiguator(filepath: Path) -> str | None:
    stem = filepath.stem
    paren_match = re.search(r"\(([^)]+)\)\s*$", stem)
    if paren_match:
        return to_slug(paren_match.group(1))
    if " - " in stem:
        suffix = stem.rsplit(" - ", 1)[1]
        return to_slug(suffix)
    return None

files = sorted(CHARTS_DIR.glob("*.md"))
renamed = 0

for filepath in files:
    stem = filepath.stem
    expected_slug = to_slug(stem)
    if stem == expected_slug:
        continue  # Already slug-case
    
    target = CHARTS_DIR / f"{expected_slug}.md"
    if target.exists() and target.resolve() != filepath.resolve():
        # Collision - add disambiguator
        disambig = get_disambiguator(filepath)
        if disambig:
            new_name = f"{expected_slug}-{disambig}.md"
        else:
            # Find next available number
            i = 2
            while (CHARTS_DIR / f"{expected_slug}-{i}.md").exists():
                i += 1
            new_name = f"{expected_slug}-{i}.md"
        target = CHARTS_DIR / new_name
    
    if filepath.name != target.name:
        print(f"Rename: {filepath.name} → {target.name}")
        filepath.rename(target)
        renamed += 1

print(f"\nRenamed {renamed} files")
