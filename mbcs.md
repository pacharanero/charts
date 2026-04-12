# Marcus Baw Musical Charting System

*MBCS Convention Reference · v0.3 · Living document*

This is the definitive guide to the Marcus Baw Charting System (MBCS), a set of conventions for writing chord and lyric charts that are easy to read while playing.

## Purpose and Philosophy

The overriding goal of MBCS is to fit a complete song — chords, lyrics, structure, and key performance notes — onto a **single page**. This is a hard constraint, not a preference. A tab section may overflow to a second page if unavoidable, but every other element must fit on one side.

Charts were originally designed for A5 printing (lever arch folder) and have since moved to A4 at 141% print scale for better legibility in dim venues.

The defining design decision is placing chords **inline with lyrics** rather than on a separate line above them. This makes it easier to scan both simultaneously while playing, without losing your place, and makes the *timing* of chord changes against the lyric easier to judge.

### The goals of every MBCS chart

- Get the entire chords and lyrics on **one page**, as simply as possible.
- Make the timing of chord changes against the lyrics easy to judge by placing chords inline with the lyric.
- Give a clear structure to the song so verses, choruses, bridges, middle eights, stops, and changes are clear.
- Include key performance notes and directions for players, without restricting the freedom of the performer with an exact tablature or arrangement.
- Don't repeat chord changes if they are the same for subsequent verses or choruses — save space by reference.

---

## Summary of Delimiters

MBCS v0.3 reserves each delimiter for one purpose, so charts can be machine-parsed (e.g. for transposition):

| Delimiter | Meaning | Example |
| --- | --- | --- |
| `[ ]` | **Pitched content only** — chords and note runs. Transposable. | `[Am]`, `[g f# e]` |
| `{ }` | Octaved / unison notes. Transposable. | `{Eb} {F} {G}` |
| `### ` | Section label (markdown H3 heading) | `### VERSE 1` |
| `**...**` | Inline performance direction (plain bold text, no brackets) | `**STOP**`, `**BVs**` |
| `( )` | Parenthetical annotations | `(palm muted)`, `(low BVs)` |

This is a change from earlier charts, which used `[ ]` for everything. The migration script in `scripts/` converts old-style charts; see [Migration](#migration-from-v02-charts) below.

---

## Document Header

Every chart starts with a header block:

- **Song title** uses an H1 heading (`#`).
- **Artist / composer** uses an H2 heading (`##`).

```markdown
# Song Title

## Artist / Composer
```

Where the chart is in a different key from the original recording, the key is noted in the title, e.g. `# Don't Be Cruel (D)`. Tuning variations (e.g. drop-D, DADGAD) are noted below the artist line in plain italic parentheses.

For cover versions, the artist name is sufficient. Where composer credit is relevant it may be added, e.g. `## Otis Blackwell / Elvis Presley`.

---

## Chord Notation

### Standard chords — square brackets

Chords are written in square brackets, placed inline immediately before the syllable or word where the chord change occurs.

```markdown
[Am] She's a skull and cross bone danger sign  
[Dm] Eye of the hurricane coming alive  
```

Complex chord names follow standard notation: `[C#m]`, `[Bb7]`, `[Fmaj7]`, `[G/B]`, `[Dm7b5]`, `[C(add11)]`.

### Octaved / unison notes — curly brackets

Notes played an octave apart (or as unison octaves across strings) use curly brackets:

```markdown
{Eb} {F} {G} {Eb} {F} {G}
```

### Single note runs — lowercase in square brackets

A melodic run of individual notes (not chords) is written in lowercase inside square brackets. Because the content is pitched, it transposes with the rest of the chart.

```markdown
[g f# e]    (three-note descending run)
```

### Chord voicings — fret notation

Where a specific voicing matters, it is written as a string-by-string fret sequence after the chord name. String order is low E to high E (6th string to 1st string). `x` means muted or not played.

```markdown
[Cm7]    8-x-8-8-8-8
[Dm7b5]  x-x-0-2-1-1
```

### Chord reminder block

For songs with unusual or hard-to-recall voicings, a chord reminder block appears at the end of the chart listing the shapes used:

```markdown
### Chord reminder

[Cm7+9]   x-10-8-8-8-10
[G7#5]    x-8-9-8-8-x
```

---

## Rhythm and Bar Notation

Forward slashes represent beats within a bar:

```text
/ / / /     four beats
///         three beats
```

Bar lines may be written explicitly with pipe characters for precision:

```text
| / / / / | / / / / |
```

Repeat counts follow the notation they apply to:

```markdown
### INTRO
[Am] / / / /  x4

### OUTRO
16 bars [Am]
```

Time signature and tempo may be noted at the top of a chart where helpful:

```text
FAST 4/4
SLOW 12/8
```

---

## Section Labels — markdown headings

Structural sections are written as H3 markdown headings in ALL CAPS. This replaces the earlier `**[VERSE 1]**` bracket style.

```markdown
### INTRO
### VERSE 1
### PRE-CHORUS
### CHORUS
### BRIDGE
### MIDDLE 8
### INTERLUDE
### GUITAR SOLO
### BREAK
### OUTRO
```

Section labels can carry additional instructions inline in parentheses after the heading text:

```markdown
### CHORUS (semi-stops)
### CHORUS (key change)
### VERSE 2 (band enters)
### BRIDGE (against CHORUS chords)
```

Using real headings gives us anchor links, a table of contents, and proper semantic HTML in the Zensical build — for free.

### Handling repetition

The single-page constraint means repeated sections are referenced by label only, not written out again in full. The first occurrence defines the section; subsequent occurrences just reference it:

```markdown
### VERSE 1
... full lyrics and chords ...

### CHORUS
... full lyrics and chords ...

### VERSE 2
... lyrics only, chords as VERSE 1 ...

### CHORUS

### BRIDGE

### CHORUS (x2)
```

Additional notes on a repeated section go in parentheses after the heading:

```markdown
### CHORUS (low BVs)
### CHORUS (rpt last 2 lines)
### VERSE 1 again
```

**simile** (plain bold) indicates the established chord pattern continues without writing every chord out.

---

## Performance Directions — plain bold text

Performance directions are written in plain bold, without brackets. They appear inline in a lyric line at the point they apply, or on their own line within a section.

### Stops and dynamics

- **STOP** — full band stops, silence
- **DEAD STOP** — emphatic full stop, usually with visual cue
- **DROP** — drop in dynamic or instrumentation
- **BUILD** — building intensity
- **ACAPELLA** or **A CAPPELLA** — vocals only

### Style and feel

- **simile** — continue in the same style as established
- `(palm muted)`, `(muted)` — right-hand muting technique (parenthetical)
- `(straight)`, `(swing)` — rhythmic feel (parenthetical)

### Instrument-specific notes

Specific rig or technique notes for individual players appear at the top of the chart or at the relevant section, in bold italic:

```markdown
***LIVE: Guitar 2 has Echo/Delay set to repeat after 3 quavers***  
***LIVE: Guitar 2 with medium-fast tremolo effect, clean-ish amp***  
```

---

## Backing Vocals (BVs)

Backing vocal parts are indicated several ways:

- **BVs** as inline bold text — indicates BVs enter at that point
- `(low BVs)`, `(high harmony)` as parentheticals on section headings
- Underline on a word or phrase indicates an emphasised backing vocal accent (use `<u>...</u>` in markdown)
- Specific BV lines written out below the main vocal line in parentheses where the part needs to be explicit

---

## Tab Notation

Guitar tablature for intros, solos, or signature riffs uses standard ASCII tab format with string labels (high e at top, low E at bottom), inside a fenced code block:

````markdown
```text
e|--12-10---------10--|
B|--------12-10-------|
G|--------------------|
D|--------------------|
A|--------------------|
E|--------------------|
```
````

Where only the highest strings are relevant, partial tab is acceptable.

Tab that would break the single-page rule may go on a second page — this is the one accepted exception to the single-page constraint.

---

## Markdown Formatting Summary

- **Song title**: H1 (`# Title`).
- **Artist / composer**: H2 (`## Artist`).
- **Section labels**: H3 in ALL CAPS (`### VERSE 1`).
- **Chords**: `[Am]`, `[G/B]` — no bold markup needed; the Zensical theme styles them via CSS.
- **Note runs**: lowercase in brackets, `[g f# e]`.
- **Octaved notes**: `{F}`.
- **Performance directions**: plain `**BOLD**` text — no brackets.
- **Parentheticals** (technique, arrangement notes): `(palm muted)`, `(low BVs)`.
- **Lyrics**: plain (not bold, not italic).
- **Line breaks**: two trailing spaces at the end of lyric lines for proper `<br>` rendering.
- **Vertical space**: minimal blank lines — the single-page constraint is still king.
- **Tabs**: fenced code blocks with `text` language tag.

### Legacy (v0.2) Google Docs formatting

Earlier charts were written in Google Docs and used bold italic throughout. These are being migrated; see below.

---

## Migration from v0.2 charts

Charts written under the earlier conventions used `**[VERSE 1]**` for sections and `**[STOP]**` for directions. The migration script at `scripts/migrate-v02-to-v03.py` handles the common transformations:

1. `**[SECTION LABEL]**` on its own line → `### SECTION LABEL`
2. `**[STOP]**`, `**[BVs]**`, `**[simile]**`, etc. inline → `**STOP**`, `**BVs**`, `**simile**`
3. Chord notation `[Am]`, `{Eb}`, `[g f# e]` is preserved unchanged.

Review each converted chart visually — some edge cases (unusual section names, mid-line section labels, ambiguous directives) need a human eye.

---

## Transposition

Because `[ ]` and `{ }` now contain only pitched content, charts can be transposed by a client-side script at render time. A `+/-` semitone control in the Zensical site rewrites every chord, note run, and octaved note, while leaving section headings and performance directions untouched.

See `charts/styles/transpose.js` for the implementation.

---

## Workflow: Google Docs → Markdown

Source charts live as Google Documents in the `guitar-music/a5-chord-lyric-charts` Drive folder. They were exported to Markdown using `rclone`:

```bash
rclone copy "gdrive:guitar-music/a5-chord-lyric-charts" ./export-md \
  --drive-export-formats md \
  --create-empty-src-dirs \
  --progress
```

The raw exports land in `export-md/`. Cleanup steps:

1. Strip global italicisation inherited from the Google Docs body font.
2. Apply the markdown conventions above (headings for sections, plain bold for directions, chord/note brackets preserved).
3. Run `scripts/migrate-v02-to-v03.py` on any chart already converted under the old conventions.
4. Follow MBCS conventions throughout; if something isn't covered, propose adding it to this document.
5. Move the cleaned chart into `charts/`.
6. Delete the corresponding file from `export-md/` once complete.

Existing charts in `charts/` serve as working examples of the conventions and should guide cleanup of the rest.

A [Zensical](https://zensical.org/) site is used to display the charts, following patterns from the [recipes repository](https://github.com/pacharanero/recipes).

---

## Evolving Conventions and Known Inconsistencies

MBCS is a living system. Some variation exists across charts, particularly in older documents:

- **Section label style** — older charts use `**[VERSE 1]**`; new convention is `### VERSE 1`. Migration script available.
- **Chord placement** — a small number of older charts place chords above the lyric line rather than inline. These are candidates for reformatting.
- **Artist attribution style** — varies across charts. No strict convention yet established.
- **In-chart editorial notes** — questions or uncertainties sometimes appear in parentheses, e.g. `(do we do this bit?)`. These are working notes, not performance directions, and should be distinguished clearly or removed before a chart is considered final.

> **Note:** This document should be updated as new musical situations require new conventions. When a new convention is agreed, add it here with an example.

---

*MBCS Convention Reference · Marcus Baw · `markdown-chord-lyric-charts`*
