# Marcus Baw Musical Charting System

*MBCS Convention Reference · v0.2 · Living document*

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

## Document Header

Every chart starts with a header block:

```
Song Title
Artist / Composer
```

In Markdown charts:

- **Song Title** uses an H1 heading (`#`).
- **Artist / Composer** uses an H2 heading (`##`).

Where the chart is in a different key from the original recording, the key is noted in the title, e.g. `Don't Be Cruel (D)`. Tuning variations (e.g. drop-D, DADGAD) are noted below the artist line in plain italic parentheses.

For cover versions, the artist name is sufficient. Where composer credit is relevant it may be added, e.g. `Otis Blackwell / Elvis Presley`.

---

## Chord Notation

### Standard chords — square brackets

Chords are written in square brackets, placed inline immediately before the syllable or word where the chord change occurs.

```
[Am] She's a skull and cross bone danger sign
[Dm] Eye of the hurricane coming alive
```

Complex chord names follow standard notation: `[C#m]`, `[Bb7]`, `[Fmaj7]`, `[G/B]`, `[Dm7b5]`, `[C(add11)]`.

### Octaved / unison notes — curly brackets

Notes played an octave apart (or as unison octaves across strings) use curly brackets:

```
{Eb} {F} {G} {Eb} {F} {G}
```

### Single note runs — lowercase

A melodic run of individual notes (not chords) is written in lowercase inside square brackets:

```
[g f# e]    (three-note descending run)
```

### Chord voicings — fret notation

Where a specific voicing matters, it is written as a string-by-string fret sequence after the chord name. String order is low E to high E (6th string to 1st string). `x` means muted or not played.

```
[Cm7]    8-x-8-8-8-8
[Dm7b5]  x-x-0-2-1-1
```

### Chord reminder block

For songs with unusual or hard-to-recall voicings, a chord reminder block appears at the end of the chart listing the shapes used:

```
Chord reminder
[Cm7+9]   x-10-8-8-8-10
[G7#5]    x-8-9-8-8-x
```

---

## Rhythm and Bar Notation

Forward slashes represent beats within a bar:

```
/ / / /     four beats
///         three beats
```

Bar lines may be written explicitly with pipe characters for precision:

```
| / / / / | / / / / |
```

Repeat counts follow the notation they apply to:

```
[INTRO] [Am] / / / /  x4
[Outro] 16 bars [Am]
```

Time signature and tempo may be noted at the top of a chart where helpful:

```
FAST 4/4
SLOW 12/8
```

---

## Section Labels

Structural sections are labelled in bold, inside square brackets. Preferred style is all-caps for consistency and quick visual scanning. Standard labels:

- `[INTRO]`
- `[VERSE 1]`, `[VERSE 2]` etc.
- `[PRE-CHORUS]`
- `[CHORUS]`
- `[BRIDGE]`
- `[MIDDLE 8]`
- `[INTERLUDE]`
- `[SOLO]` — with instrument noted where helpful, e.g. `[GUITAR SOLO]`, `[PIANO SOLO]`
- `[BREAK]`
- `[OUTRO]`

Section labels can carry additional instructions inline:

```
[CHORUS] (semi-stops)
[CHORUS] (key change)
[VERSE 2] (band enters)
[BRIDGE] (against CHORUS chords)
```

### Handling repetition

The single-page constraint means repeated sections are referenced by label only, not written out again in full. The first occurrence defines the section; subsequent occurrences just reference it:

```
[VERSE 1]
... full lyrics and chords ...

[CHORUS]
... full lyrics and chords ...

[VERSE 2]
... lyrics only, chords as [VERSE 1] ...

[CHORUS]

[BRIDGE]

[CHORUS]  (x2)
```

Additional notes on a repeated section go in parentheses after the label:

```
[CHORUS] (low BVs)
[CHORUS] (rpt last 2 lines)
[VERSE 1] again
```

`[simile]` indicates the established chord pattern continues without writing every chord out.

---

## Performance Directions

Performance directions appear inline in bold square brackets, either attached to a section label or placed mid-line at the point they apply.

### Stops and dynamics

- `[STOP]` — full band stops, silence
- `[DEAD STOP]` — emphatic full stop, usually with visual cue
- `[DROP]` — drop in dynamic or instrumentation
- `[BUILD]` — building intensity
- `[ACAPELLA]` or `[A CAPPELLA]` — vocals only

### Style and feel

- `[simile]` — continue in the same style as established
- `(palm muted)`, `(muted)` — right-hand muting technique
- `(straight)`, `(swing)` — rhythmic feel

### Instrument-specific notes

Specific rig or technique notes for individual players appear at the top of the chart or at the relevant section, in bold italic:

```
LIVE: Guitar 2 has Echo/Delay set to repeat after 3 quavers
LIVE: Guitar 2 with medium-fast tremolo effect, clean-ish amp
```

---

## Backing Vocals (BVs)

Backing vocal parts are indicated several ways:

- `[BVs]` inline after a chord or lyric line — indicates BVs enter here
- `(low BVs)`, `(high harmony)` as parentheticals on section labels
- Underline on a word or phrase indicates an emphasised backing vocal accent
- Specific BV lines written out below the main vocal line in parentheses where the part needs to be explicit

---

## Tab Notation

Guitar tablature for intros, solos, or signature riffs uses standard ASCII tab format with string labels (high e at top, low E at bottom), inside a fenced code block:

````
```
e|--12-10---------10--|
B|--------12-10-------|
G|--------------------|
D|--------------------|
A|--------------------|
E|--------------------|
```
````

Where only the highest strings are relevant, partial tab is acceptable:

```
e|17-|---|16-|---|
b|---|---|---|---|
```

Tab that would break the single-page rule may go on a second page — this is the one accepted exception to the single-page constraint.

---

## Markdown Formatting Conventions

These conventions apply to the Markdown versions of the charts (the `charts/` directory).

- **Song title** uses an H1 heading (`#`).
- **Artist / composer** uses an H2 heading (`##`).
- **Section labels** such as `[INTRO]`, `[VERSE 1]`, `[CHORUS]` are **bold and uppercase**, e.g. `**[VERSE 1]**`.
- **Chord names within lyrics** are bold, e.g. `**[Am]**`.
- **Performance directions** are bold.
- **Lyrics** are plain (not bold, not italicised).
- Do **not** globally italicise body text. Earlier Google Docs versions used an italic font style; this must be removed when converting to Markdown.
- Add **trailing spaces** (two spaces) to the end of lyric lines to force proper `<br>` line breaks in rendered Markdown. This is required for most lyric lines.
- Minimal use of blank lines — vertical space is precious on a single page.
- No page breaks except before an optional tab section.
- Tab blocks use fenced code blocks (triple backticks) so they render in a fixed-width font.

### Google Docs formatting conventions (legacy)

Charts in the original `a5-chord-lyric-charts` Google Docs folder follow these conventions:

- The entire chart is in a single font, typically Arial or similar sans-serif.
- Song title: bold italic, slightly larger than body text.
- Artist / composer: italic.
- Section labels: bold italic in square brackets — e.g. ***[VERSE 1]***.
- Chord names within lyrics: bold — e.g. **[Am]**.
- Performance directions: bold italic.
- Lyrics: plain (not bold).

---

## Workflow: Google Docs → Markdown

Source charts live as Google Documents in the `guitar-music/a5-chord-lyric-charts` Drive folder. They were exported to Markdown using `rclone`:

```
rclone copy "gdrive:guitar-music/a5-chord-lyric-charts" ./export-md \
  --drive-export-formats md \
  --create-empty-src-dirs \
  --progress
```

The raw exports land in `export-md/`. Cleanup steps:

1. Strip global italicisation inherited from the Google Docs body font.
2. Apply the Markdown conventions above (headings, bold section labels, trailing spaces on lyric lines, fenced tab blocks).
3. Follow MBCS conventions throughout; if something isn't covered, propose adding it to this document.
4. Move the cleaned chart into `charts/`.
5. Delete the corresponding file from `export-md/` once complete.

Existing charts in `charts/` serve as working examples of the conventions and should guide cleanup of the rest.

A Material for MkDocs site will be built to display the charts, following patterns from the [recipes repository](https://github.com/pacharanero/recipes).

---

## Evolving Conventions and Known Inconsistencies

MBCS is a living system. Some variation exists across charts, particularly in older documents:

- **Section label capitalisation** — both `[Verse 1]` and `[VERSE 1]` appear. All-caps is preferred going forward for visual clarity.
- **Chord placement** — a small number of older charts place chords above the lyric line rather than inline. These are candidates for reformatting.
- **Artist attribution style** — varies across charts. No strict convention yet established.
- **In-chart editorial notes** — questions or uncertainties sometimes appear in parentheses, e.g. `(do we do this bit?)`. These are working notes, not performance directions, and should be distinguished clearly or removed before a chart is considered final.

> **Note:** This document should be updated as new musical situations require new conventions. When a new convention is agreed, add it here with an example.

---

*MBCS Convention Reference · Marcus Baw · `markdown-chord-lyric-charts`*
