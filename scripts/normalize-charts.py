#!/usr/bin/env python3
"""Normalize filenames and YAML metadata in charts/ directory.

Changes:
1. Rename files to slug-case (lowercase, hyphens instead of spaces/special chars)
2. Remove H1 heading lines (MkDocs auto-generates from YAML title)
3. Remove YAML `slug:` field (redundant - filename IS the slug for MkDocs)
4. Keep YAML `title:` and H2 artist
5. Handle filename collisions by adding disambiguators

Usage:
    python3 scripts/normalize-charts.py          # dry-run
    python3 scripts/normalize-charts.py --apply   # actually make changes
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"

# Files to skip (special MkDocs files)
SKIP_FILES = {"index.md", "tags.md"}


def to_slug(name: str) -> str:
    """Convert a string to slug-case."""
    # Normalize unicode characters
    name = unicodedata.normalize("NFKD", name)
    # Remove various apostrophe/quote types
    name = name.replace("'", "").replace("'", "").replace("'", "").replace("'", "").replace("`", "")
    # Remove remaining non-ASCII
    name = name.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    name = name.lower()
    # Replace non-alphanumeric with hyphens
    name = re.sub(r"[^a-z0-9]+", "-", name)
    # Strip leading/trailing hyphens
    name = name.strip("-")
    # Collapse multiple hyphens
    name = re.sub(r"-{2,}", "-", name)
    return name


def normalize_text(text: str) -> str:
    """Normalize text for comparison (handle quotes, etc)."""
    text = text.lower().strip()
    text = text.replace("'", "'").replace("'", "'").replace("'", "").replace("`", "")
    return text


def extract_title_from_frontmatter(content: str) -> str | None:
    """Extract the title from YAML frontmatter."""
    # Handle double-quoted titles
    m = re.search(r'^title:\s*"([^"]+)"', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Handle single-quoted titles
    m = re.search(r"^title:\s*'([^']+)'", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Handle unquoted titles
    m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def get_disambiguator(filepath: Path) -> str | None:
    """Extract a disambiguator from the original filename."""
    stem = filepath.stem
    # Check for parenthetical suffix: "Song Name (E)" → "e"
    paren_match = re.search(r"\(([^)]+)\)\s*$", stem)
    if paren_match:
        return to_slug(paren_match.group(1))
    # Check for artist suffix: "Song Name - Artist" → "artist"
    if " - " in stem:
        suffix = stem.rsplit(" - ", 1)[1]
        return to_slug(suffix)
    return None


def process_content(content: str) -> tuple[str, list[str]]:
    """Process file content: remove slug, remove H1 if redundant."""
    actions = []

    # 1. Remove slug from frontmatter
    if re.search(r"^slug:\s*.+$", content, re.MULTILINE):
        content = re.sub(r"^slug:\s*.+\n?", "", content, count=1, flags=re.MULTILINE)
        actions.append("Removed YAML slug field")

    # 2. Remove H1 heading if it matches YAML title
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        title = extract_title_from_frontmatter(content)
        if title:
            h1_norm = normalize_text(h1_text)
            title_norm = normalize_text(title)
            if h1_norm == title_norm or h1_norm in title_norm or title_norm in h1_norm:
                content = re.sub(r"^#\s+.+\n", "", content, count=1, flags=re.MULTILINE)
                actions.append(f"Removed H1 heading: '{h1_text}'")

    return content, actions


def main():
    parser = argparse.ArgumentParser(description="Normalize chart filenames and metadata")
    parser.add_argument("--apply", action="store_true", help="Actually make changes (default: dry-run)")
    parser.add_argument("--only", type=str, help="Only process files matching this pattern")
    args = parser.parse_args()

    files = sorted(CHARTS_DIR.glob("*.md"))
    if args.only:
        pattern = re.compile(args.only, re.IGNORECASE)
        files = [f for f in files if pattern.search(f.name)]

    # Skip special files
    files = [f for f in files if f.name not in SKIP_FILES]

    # PASS 1: Read all files and determine target names
    file_plans = []  # List of (filepath, new_content, target_slug, actions)
    slug_counts: dict[str, int] = {}

    for filepath in files:
        content = filepath.read_text(encoding="utf-8")
        new_content, actions = process_content(content)

        title = extract_title_from_frontmatter(new_content)
        if title:
            target_slug = to_slug(title)
        else:
            # Fallback: use current filename stem
            target_slug = to_slug(filepath.stem)
            if not target_slug:
                target_slug = filepath.stem.lower()

        slug_counts[target_slug] = slug_counts.get(target_slug, 0) + 1
        file_plans.append((filepath, new_content, target_slug, actions))

    # PASS 2: Resolve collisions
    slug_used: dict[str, int] = {}
    total_changes = 0

    for filepath, new_content, target_slug, actions in file_plans:
        # Check if we need a disambiguator
        if slug_counts[target_slug] > 1:
            disambiguator = get_disambiguator(filepath)
            if disambiguator:
                final_slug = f"{target_slug}-{disambiguator}"
            else:
                # Use a counter-based disambiguator
                count = slug_used.get(target_slug, 0) + 1
                slug_used[target_slug] = count
                final_slug = f"{target_slug}-{count}" if count > 1 else target_slug
        else:
            final_slug = target_slug

        new_filename = f"{final_slug}.md"

        # Determine if file needs changes
        content_changed = new_content != filepath.read_text(encoding="utf-8")
        name_changed = filepath.name != new_filename

        if content_changed or name_changed:
            total_changes += 1
            change_desc = []
            if content_changed:
                change_desc.extend(actions)
            if name_changed:
                change_desc.append(f"Rename: '{filepath.name}' → '{new_filename}'")

            print(f"\n{filepath.name}:")
            for desc in change_desc:
                print(f"  - {desc}")

            # Apply changes if requested
            if args.apply:
                new_path = filepath.parent / new_filename

                # Handle edge case where target already exists with different content
                if new_path.exists() and new_path.resolve() != filepath.resolve():
                    print(f"  WARNING: Target '{new_filename}' already exists, skipping rename")
                    # Still write content changes to original file
                    if content_changed:
                        filepath.write_text(new_content, encoding="utf-8")
                else:
                    if content_changed:
                        # Write content to new path (or original if name unchanged)
                        write_path = new_path if name_changed else filepath
                        write_path.write_text(new_content, encoding="utf-8")
                    if name_changed and not new_path.exists():
                        filepath.rename(new_path)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n\n{mode}: {total_changes} files would be changed" if not args.apply else f"\n\nDONE: {total_changes} files changed")


if __name__ == "__main__":
    main()
