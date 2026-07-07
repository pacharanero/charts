# Zensical Interface Specification

This document records the UI conventions for the published Charts site. It complements `spec/mbcs.md`, which defines the chart notation itself.

The site is a **Zensical** site. Do not describe it as Material for MkDocs, even when Zensical exposes familiar class names or theme behaviours.

## Goals

- Keep the chart readable while playing: large enough for a music stand or dim room, without wasting vertical space.
- Preserve the MBCS one-page print goal. Screen controls must not affect the print stylesheet unless explicitly intended.
- Make transposition, zoom, italics, and print controls easy to find and hit.
- Keep navigation available on desktop/tablet while avoiding cramped mobile layouts.
- Use a distinct Charts colour palette rather than copying the Recipes site palette.

## Header

- The site name in the header is `charts`, not `Marcus Baw Guitar Charts`.
- Header sizing should follow the proportions of the Recipes Zensical site as a guide: larger than the stock Zensical header text, but not so large that controls become congested.
- The header should contain site/navigation controls only. Chart-specific controls should not live in the header because the header is already space-constrained.
- Header colours should maintain good contrast in both light and dark mode.
- The colour palette should be chosen deliberately. Current direction: warm walnut/parchment base with a muted teal accent and amber control highlights. Do not copy the Recipes colour palette.

## Layout

- The left navigation sidebar should be present on desktop/tablet.
- The left navigation sidebar may be hidden on narrower/mobile layouts where it competes with chart readability.
- Chart content should be horizontally balanced within its content area. Avoid asymmetric offsets caused by Zensical content/sidebar margins.
- Reduce unnecessary top whitespace so the chart starts closer to the header, but keep enough breathing room for readability.
- Tablature blocks should be centred as blocks, matching the chart's centred visual rhythm, while the monospace tab text remains left-aligned inside the block so columns line up.

## Chart Tools

Chart tools are implemented in `charts/styles/transpose.js` and styled in `charts/styles/brand.css`.

- Chart tools should appear as a floating panel, not inside the header.
- The toolbar should be non-printing.
- Controls should be large enough to tap/click comfortably and visible in both light and dark mode.
- The toolbar should initialise once per Zensical navigation event and should not duplicate itself.

### Transpose

- Transpose applies to MBCS pitched tokens:
  - chords in `[ ]`
  - lowercase note-runs in `[ ]`
  - octaved/unison notes in `{ }`
- Transpose should leave section headings, lyrics, and performance directions unchanged.
- Transpose should also attempt simple tablature transposition in recognised guitar tab code blocks by incrementing/decrementing fret numbers.
- Tablature transposition is intentionally conservative. If a down-transpose would produce a fret below `0`, the UI should show a warning that the tab needs human rearrangement instead of pretending that fret `-1` or `-2` is playable.

### Zoom

- Zoom is an on-screen readability control.
- Zoom should affect chart content size, including lyrics and headings.
- Zoom should not alter print sizing; print layout remains controlled by the print stylesheet and MBCS one-page constraints.
- Zoom state may persist locally in the browser.

### Italics

- Body text is italic by default to match the historic chart feel.
- The toolbar italic toggle should switch body text between italic and upright.
- Chord tokens should remain upright/distinct regardless of the body italic setting.

### Print

- The print button should invoke browser print.
- Printed charts should hide site chrome, navigation, and chart tools.
- Print layout should remain black-on-white, compact, and tuned for A4.

## Validation Checklist

When changing the interface:

- Check at least one normal chord chart and one chart with tablature.
- Confirm the toolbar appears once and remains usable after navigating between charts.
- Confirm transpose changes chord tokens and recognised tab fret numbers.
- Confirm negative tab transposition displays a human-rearrangement warning.
- Confirm zoom changes on-screen chart text but does not affect print CSS.
- Confirm italic toggle changes body text and leaves chord tokens readable.
- Confirm tab blocks are centred as blocks and remain internally left-aligned.
- Confirm desktop/tablet retains the left sidebar, while mobile/narrow layouts do not become cramped.
- Run `git diff --check`.
