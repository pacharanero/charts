# Chart Conversion Guide

A practical runbook for migrating chord/lyric charts from their original
sources (Google Docs, legacy Word docs, PDFs) into MBCS v0.3 markdown that
lives in `charts/`. Written so another human or LLM can pick up the work
without re-deriving the decisions.

See also:

- `mbcs.md` — the chart format spec (the target)
- `spec.md` — the repo-level cleanup rules

---

## The pipeline at a glance

```
  Google Drive
       │
       ▼  rclone
  export-md/*.md          (Google Docs auto-exports to markdown)
  export-md/*.doc         (legacy Word, never migrated to Docs)
  export-md/*.docx / *.odt
  export-md/*.pdf         (text PDFs or scans)
  export-md/*.jpg         (rare — scanned image)
       │
       ├── scripts/convert-office.py   (.doc/.docx/.odt → .md)
       ├── scripts/convert-pdfs.py     (.pdf → .md via pdftotext)
       │
       ▼
  export-md/*.md          (everything normalised to .md)
       │
       ▼  scripts/convert-exports.py
  charts/*.md             (MBCS v0.3, ready for the Zensical site)
```

Each stage is idempotent. Re-running on a file that's already been converted
is a no-op unless `--overwrite` is passed.

---

## Stage 1 — Office formats → Markdown

**Script**: `scripts/convert-office.py`

Dependencies: `pandoc` (via brew), `soffice` / `libreoffice` (for the
`.doc` → `.docx` intermediate step, since pandoc doesn't read the legacy
binary `.doc` format).

```bash
scripts/convert-office.py                       # dry-run
scripts/convert-office.py --apply --delete      # convert + remove original
scripts/convert-office.py --only "Foo.doc"      # subset
```

Notes:

- Writes `Foo.md` alongside `Foo.doc` in `export-md/`. The MBCS cleanup
  (stage 3) then picks up the new `.md`.
- Pandoc output is **bold-only** (`**Title**`) not bold-italic
  (`***Title***`), because legacy Word docs usually weren't set up in the
  italic-body-font style that Google Docs migration used. Stage 3 handles
  both.
- Pandoc's `gfm+hard_line_breaks --wrap=none` is chosen so we don't reflow
  lyric lines.

---

## Stage 2 — PDFs → Markdown

**Script**: `scripts/convert-pdfs.py`

Dependencies: `pdftotext` (from poppler-utils).

```bash
scripts/convert-pdfs.py                         # dry-run
scripts/convert-pdfs.py --apply --delete
scripts/convert-pdfs.py --min-chars 50          # threshold for "scanned"
```

Notes:

- Uses `pdftotext -layout` so chord-column alignment survives.
- **Scanned / image-only PDFs are detected and skipped.** If extracted text
  is shorter than `--min-chars` (default 80), the script leaves the PDF in
  place and prints `>>`. These need manual transcription (or OCR via a tool
  like `tesseract`, if the user wants to automate later).
- Once a chart is in `.md`, stage 3 picks it up.

---

## Stage 3 — Markdown → MBCS v0.3

**Script**: `scripts/convert-exports.py`

```bash
scripts/convert-exports.py                      # dry-run, report only
scripts/convert-exports.py --apply              # write to charts/
scripts/convert-exports.py --apply --delete     # also rm the export-md source
scripts/convert-exports.py --only "Africa.md"   # single file
scripts/convert-exports.py --force "Hard.md"    # override skip heuristic
scripts/convert-exports.py --overwrite          # replace existing chart
```

What it does, in order:

1. **Unescape** Google Docs markdown escapes (`\[`, `\]`, `\#`, `\-`, `\!`,
   `\~`, `\\`, `\(`, `\)`, `\.`).
2. **Skip-detect**: files matching any of these heuristics are left in
   `export-md/` and reported:
   - Image-embedded (`![][imageN]` in the first few lines — Google Docs had
     a PNG instead of text).
   - Bar-grid heavy (>6 lines of `| chord | % | ... |` Tom Waits-style
     notation).
   - Chord-above-lyric (>3 pairs of a chord-only line followed by a lyric
     line).
   - Tab-only (>6 tab lines and <5 other content lines).
   - Low inline-chord density (body >400 chars but <3 inline `word[Chord]`
     or `[Chord]word` matches). Catches pandoc-converted legacy Word docs
     that have lyrics but no MBCS-style inline chord brackets.
3. **Title** (`# ...`) extraction. Tries in order:
   - `***Title -** Artist*` combined pattern.
   - `***Title***` or `***Title (Key)***`.
   - `**Title**` (pandoc bold-only).
4. **Artist** (`## ...`) extraction:
   - `*Artist*` italic.
   - `**Artist**` bold.
   - Plain text line, short, capitalised, no brackets or pipes — for
     pandoc output.
5. **Section labels** → H3 headings. Recognised prefixes: `INTRO`, `VERSE`,
   `PRE-CHORUS`, `CHORUS`, `BRIDGE`, `MIDDLE`, `INTERLUDE`, `SOLO`, `GUITAR
   SOLO`, `PIANO SOLO`, `BREAK`, `OUTRO`, `CODA`, `VAMP`, `TAG`, `REFRAIN`,
   `HOOK`, `LINK`, `RIFF`, `ENDING`, `INSTRUMENTAL`, `REPRISE`, `MODIFIED
   CHORUS`.
   - Standalone `***[VERSE 1]***` → `### VERSE 1`.
   - `***[VERSE 1] (BVs)***` → `### VERSE 1 (BVs)`.
   - Mixed heading+lyric `***[VERSE 1]** lyric...*` → heading on own line
     then lyric.
   - Bracketless `***Intro***` or `***chorus***` → `### INTRO` if the
     content matches a known section keyword.
   - Short trailing non-parenthetical text like `[Chorus] again` or
     `[Chorus] (x2)` is folded into the heading as `### CHORUS (again)`.
6. **Chord tokens**: `**[Am]**` (bold-wrapped chord) → `[Am]`.
7. **Standalone direction line**: `***Phaser***` → `**Phaser**` (unless it
   matches a section keyword, in which case it becomes a heading).
8. **Outer italic wrapping** on body lines: stripped.
9. **Tab blocks**: runs of lines starting `e|`/`B|`/`G|`/`D|`/`A|`/`E|`
   (with internal blanks allowed) are folded into a fenced ` ```text `
   block.
10. **Line breaks**: non-heading, non-fenced lines get two trailing spaces
    for Markdown `<br>` rendering.
11. **Frontmatter**: YAML front matter prepended with `slug`, `title`,
    empty `tags: []`, `category: Guitar Charts`, and `hide: [toc]` so
    Zensical doesn't render the per-page table of contents.
12. **Blank-line collapse**: 3+ consecutive blank lines → 2.

### What ends up where

A converted chart that ran through the full pipeline looks like:

```markdown
---
slug: song-name
title: "Song Name"
tags: []
category: Guitar Charts
hide:
  - toc
---

# Song Name

## Artist

### INTRO
[Am] / / / / x4  

### VERSE 1
[Am] lyric with chord [Dm] markers inline  
more lyrics  

### CHORUS
...
```

---

## Running the whole pipeline

From repo root, in order:

```bash
scripts/convert-office.py --apply --delete
scripts/convert-pdfs.py    --apply --delete
scripts/convert-exports.py --apply --delete
```

Then:

```bash
./s/up          # serve the Zensical site to spot-check the new charts
```

---

## What's expected to be left in `export-md/`

After the full pipeline, the files that remain need human attention.
Approximate breakdown from the initial run:

| Reason | Count | What to do |
| --- | ---: | --- |
| Low inline-chord density (pandoc Word docs) | ~156 | Open each, manually place `[Chord]` tokens inline with lyrics to MBCS style |
| Chord-above-lyric layout | ~40 | Same — convert tab-aligned chord rows to inline MBCS brackets |
| Scanned PDFs (image-only) | ~36 | Manual transcription, or run `tesseract` OCR first |
| No title detected (lead sheets, etc.) | ~22 | Check the first few lines; add a `***Title***` header and re-run `--only` |
| Image-only Google Docs exports | 3 | Manual re-entry from the image |
| Duplicates (already in `charts/`) | ~9 | Delete the `export-md/` copy |
| Tab-only, bar-grid-heavy | ~3 | Keep only if the song is chart-worthy; otherwise delete |

Low-density and chord-above-lyric are the biggest piles. Doing them by hand
is O(N×5 minutes). An LLM with chart context can do 5–10 at a time — **but
be mindful of Anthropic's output-side copyright filter**: writing multiple
full-song lyric outputs in one response can trip the filter. Work in small
batches (1–3 songs per response) and prefer `Edit` over `Write` for
in-place changes since Edit only transmits the diff.

---

## Patching the pipeline

If a chart pattern recurs often enough, add it to the script rather than
handling each file manually.

- New section keyword? Add it to `SECTION_PREFIXES` in
  `scripts/convert-exports.py`.
- New performance-direction token? Add it to `DIRECTION_TOKENS`.
- New skip heuristic? Extend `detect_skip` — keep heuristics conservative
  (prefer false negatives; a good chart wrongly skipped is easier to rescue
  than a bad chart wrongly promoted).

After patching, re-run `scripts/convert-exports.py` (dry-run first) and
eyeball the counts. Compare `--only` output against the raw source before
committing.

---

## Gotchas and things I learned the hard way

- **Google Docs' italic-body-font quirk.** Every body line from the Google
  Docs exports is wrapped in `*...*` because the original Doc was set in
  an italic typeface. `strip_outer_italic` reverses that safely by
  checking the inner content doesn't unbalance bold markers.
- **Escape sequences.** Google Docs escapes `[`, `]`, `#`, `-`, `!` with
  backslashes. Unescape *before* trying to match section labels, or the
  regexes miss.
- **Chord vs direction vs section.** Same-looking `[STOP]` tokens have
  different meanings depending on position and keyword set. The pipeline
  checks section prefixes first, then direction tokens, then falls through
  as chord.
- **Two trailing spaces = hard line break.** Every lyric line needs them,
  or the rendered page shows one giant paragraph. `.editorconfig`,
  `.vscode/settings.json`, and `.prettierignore` in the repo root keep
  format-on-save from silently stripping them.
- **Ambiguous "[Chorus] again".** Short trailing text after a section
  bracket is almost always an annotation (not a lyric). The script wraps
  it in parens on the heading. If a real lyric gets swallowed this way,
  it'll be obvious on visual review.
- **Copyright filter.** When working through files manually, don't write
  many full songs of lyrics in a single LLM response — the API's
  copyright guardrail can refuse the whole reply. Edit in place, or batch
  small.
