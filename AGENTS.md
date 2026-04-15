# Agent Instructions

This repo is a collection of guitar chord/lyric charts written in a personal markdown convention called **MBCS** (Marcus Baw Musical Charting System), published as a [Zensical](https://zensical.org/) site.

Before doing any work here, read `spec/mbcs.md` — it is the authoritative reference for the charting conventions and takes precedence over anything else.

## Repository layout

- `charts/` — the mkdocs `docs_dir`. Every chart lives here as `charts/<slug>.md`. Nothing outside `charts/` is published.
- `charts/styles/brand.css` — site styling, print rules, header layout.
- `charts/styles/transpose.js` — client-side +/- semitone transposer. It parses `[...]` and `{...}` tokens, so those delimiters are reserved for pitched content only (see `spec/mbcs.md`).
- `charts/index.md` — site homepage.
- `charts/tags.md` — tag index page. The Zensical tags index directive is not implemented yet (tracked at [zensical/backlog#38](https://github.com/zensical/backlog/issues/38)), so this page is a stub until upstream ships.
- `spec/` — living specification:
  - `mbcs.md` — charting conventions (delimiters, sections, rhythm, performance directions).
  - `conversion.md` — Google Docs → Markdown export workflow.
  - `roadmap.md` — outstanding work.
  - `spec.md` — older combined spec (superseded by `mbcs.md`).
- `scripts/` — migration helpers (e.g. `migrate-v02-to-v03.py`).
- `export-md/` — raw Google Docs exports staged for cleanup.
- `README.md` — GitHub-facing front page (the site has its own `index.md`).
- `mkdocs.yml` — site config. Note `docs_dir: charts` — any top-level doc file is NOT part of the site.

## Hard rules

1. **Single page**. Every chart fits on one A4 page at 141% print scale. Tab sections are the only accepted overflow. If you add content and it no longer fits, compress by referencing repeated sections rather than re-writing them.
2. **Delimiters are reserved.** `[...]` = chord or lowercase note-run. `{...}` = octaved/unison notes. Both are machine-parsed by `transpose.js`. Do NOT use `[...]` for section labels or performance directions — use `### SECTION` (H3, uppercase) and plain `**bold**` text respectively.
3. **One chart per file**, kebab-case slug filename, matching the song title.
4. **Frontmatter**: `title:`, optional `tags:` (see the tag taxonomy below), `hide: [toc]` on every chart.

## Tag taxonomy

Tags are restricted to genres, eras, and descriptors. Do **not** add artist names as tags — they clutter the index without adding navigational value. Use the song title heading for artist attribution instead.

Allowed tag categories (see recent history for the current set):

- Eras: `40s`, `50s`, `60s`, `70s`, `80s`, `90s`, `00s`, `10s`
- Genre: `rock`, `rockabilly`, `blues`, `jazz`, `soul`, `swing`, `folk`, `country`, `pop`, `punk`, `ska`, `motown`, `r&b`, `big-band`, `jump-blues`, `doo-wop`, `rock-and-roll`, `britpop`, `new-wave`, `psychobilly`, `swing-revival`, `neo-swing`, `vocal-jazz`, `glam-rock`, `2-tone`, `folk-rock`, `blues-rock`, `hard-rock`, `heavy-metal`, `indie`, `alternative`, `disco`, `electric-blues`, `electronic`, `synth-pop`, `southern-rock`, `heartland-rock`, `power-pop`, `pop-punk`, `comedy-rock`, `mod`, `skiffle`, `celtic`, `americana`, `british-invasion`, `singer-songwriter`, `acoustic`, `dance`, `funk`, `psychedelic`
- Descriptors: `instrumental`, `tab`, `capo`, `guitar`, `piano`, `christmas`, `comedy`, `novelty`, `soundtrack`, `modern`, `traditional`, `trad`, `disney`
- Origin/language: `scottish`, `danish`, `swiss`, `uk`, `australian-traditional`

If a genuinely new genre tag is needed for a chart, add it deliberately — not reflexively.

## Local development

```bash
mkdocs serve
```

Opens at `http://127.0.0.1:8000`. `docs_dir: charts`, so only files under `charts/` reload.

## Testing your work

Before declaring a chart done:

1. Serve the site and confirm the chart renders on one page in print preview (Chrome: Ctrl+P → "Save as PDF", A4 portrait).
2. Click the transpose +/– buttons — every chord, note-run, and `{...}` token should change. If any bracketed content doesn't transpose, you probably mis-used `[...]` for something non-pitched.
3. Check the italic toggle (`I` button in the header) leaves chord tokens upright.
4. Verify `hide: [toc]` is set so the right-hand ToC doesn't compete with the single-page layout.

## When in doubt

`spec/mbcs.md` > any existing chart > this file. Existing charts contain historical inconsistencies from the pre-v0.3 era; `mbcs.md` is the target state.
