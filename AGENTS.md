# Agent Instructions

This repo is a collection of guitar chord/lyric charts written in a personal markdown convention called **MBCS** (Marcus Baw Musical Charting System), published as a [Zensical](https://zensical.org/) site. It is content-first: chart readability, one-page print layout, and reliable transposition matter more than generic Markdown prettiness.

This file is the entry point for AI coding agents. Read it before changing anything.

## Read First

- [README.md](README.md) - project overview and publishing context.
- [spec/mbcs.md](spec/mbcs.md) - authoritative charting convention; this overrides existing legacy charts and this file.
- [spec/conversion.md](spec/conversion.md) - Google Docs to Markdown cleanup workflow.
- [spec/interface.md](spec/interface.md) - Zensical UI, layout, colour, and chart tool conventions.
- [spec/roadmap.md](spec/roadmap.md) - outstanding repo work.
- [~/code/house-style/AGENTS.md](~/code/house-style/AGENTS.md) - cross-repo engineering standards; follow it unless this file documents a local exception.

## Repository Layout

- `charts/` - the Zensical `docs_dir`; every published chart lives here as `charts/<slug>.md`.
- `charts/styles/brand.css` - Zensical site styling, screen/print layout, colours, and chart tool presentation.
- `charts/styles/transpose.js` - client-side chart tools: transpose, simple tab transposition, zoom, italic toggle, and print.
- `charts/index.md` - site homepage.
- `charts/tags.md` - tag index stub until Zensical implements the tags index directive.
- `spec/` - living charting and conversion specifications.
- `scripts/` - migration helpers for legacy exports.
- `export-md/` - raw Google Docs exports staged for cleanup.
- `site/` - generated output; do not edit by hand.

## Core Invariants

- Read [spec/mbcs.md](spec/mbcs.md) before editing charts. It is the source of truth.
- Every chart must fit on one A4 page at 141% print scale. Tab sections are the only accepted overflow.
- `[...]` is only for chords or lowercase note-runs. `{...}` is only for octaved/unison notes. Both are parsed by `charts/styles/transpose.js`.
- Do not use square brackets for section labels, directions, or comments. Use `### SECTION` headings and plain `**bold**` performance directions.
- One chart per file, with a kebab-case slug matching the song title.
- Every chart frontmatter must include `title:` and `hide: [toc]`. Tags are optional but must follow the taxonomy below.
- Do not hand-edit generated `site/` output.
- GitHub Actions must be pinned to full commit SHAs with trailing `# vX.Y.Z` comments, per [~/code/house-style/ci.md](~/code/house-style/ci.md).

## Chart Tags

Tags are restricted to genres, eras, descriptors, and origin/language. Do not add artist names as tags.

Allowed categories:

- Eras: `40s`, `50s`, `60s`, `70s`, `80s`, `90s`, `00s`, `10s`
- Genre: `rock`, `rockabilly`, `blues`, `jazz`, `soul`, `swing`, `folk`, `country`, `pop`, `punk`, `ska`, `motown`, `r&b`, `big-band`, `jump-blues`, `doo-wop`, `rock-and-roll`, `britpop`, `new-wave`, `psychobilly`, `swing-revival`, `neo-swing`, `vocal-jazz`, `glam-rock`, `2-tone`, `folk-rock`, `blues-rock`, `hard-rock`, `heavy-metal`, `indie`, `alternative`, `disco`, `electric-blues`, `electronic`, `synth-pop`, `southern-rock`, `heartland-rock`, `power-pop`, `pop-punk`, `comedy-rock`, `mod`, `skiffle`, `celtic`, `americana`, `british-invasion`, `singer-songwriter`, `acoustic`, `dance`, `funk`, `psychedelic`
- Descriptors: `instrumental`, `tab`, `capo`, `guitar`, `piano`, `christmas`, `comedy`, `novelty`, `soundtrack`, `modern`, `traditional`, `trad`, `disney`
- Origin/language: `scottish`, `danish`, `swiss`, `uk`, `australian-traditional`

Add a new genre tag only deliberately, not reflexively.

## Workflow

- `zensical build` - build the site.
- `s/docs` - serve the site locally with hot reload and open it in a browser.
- `zensical serve -a 127.0.0.1:8000` - serve directly, choosing another port if 8000 is already in use.

## Before Every Commit

```sh
zensical build
git diff --check
```

For chart changes, also verify:

- The chart renders on one A4 page in print preview.
- Transpose +/- changes every chord, note-run, and `{...}` token.
- The italic toggle leaves chord tokens upright.
- `hide: [toc]` is present.

## Approval Required

Ask before publishing, deleting remote branches, force-pushing, changing secrets, or taking externally visible GitHub actions. Routine local reads, formatting, and Zensical builds do not need approval.

## When In Doubt

[spec/mbcs.md](spec/mbcs.md) > existing chart precedent > this file > [~/code/house-style/AGENTS.md](~/code/house-style/AGENTS.md) > generic defaults. Existing charts contain historical inconsistencies from the pre-v0.3 era; `mbcs.md` is the target state.
