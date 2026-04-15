This repository contains chord and lyric charts for songs which I have collected over many years.

Originally they were in .doc format, but then I gradually converted them to Google Documents. Now I am converting them into Markdown since this is much easier to interact with and develop using LLMs.

I used rclone to export the Google Docs to Markdown format.

```
rclone copy "gdrive:guitar-music/a5-chord-lyric-charts" ./export-md \
  --drive-export-formats md \
  --create-empty-src-dirs \
  --progress
```

The exported Markdown files are in the `export-md` directory.

The next job is to clean them up according to rules we will add to this document, `spec.md`.

## RULES

- Follow the MBCS conventions in README.md. If we encounter anything not covered in the conventions, propose adding it to the conventions.

- Remove the global italicization from the body text. In the Google Docs versions I used an italic style font, but this needs to be removed for the Markdown versions.

- Once a chart has been cleaned up, add it to the `charts` directory.

- We will build a Zensical site to display the charts, this will follow patterns established in my recipes repository https://github.com/pacharanero/recipes which you can refer to.

- Charts which have been completed can be deleted from the `export-md` directory.

## Markdown Conventions

This is for elements of formatting which are specific to the Markdown versions of the charts, and not covered in the MBCS conventions in README.md.

- Song Title uses H1 markdown heading

- Artist uses H2 heading

- Section references such as **[INTRO]**, **[VERSE 1]**, **[CHORUS]** are bold and uppercase.

- Add trailing spaces (two spaces) to the end of lines to create proper line breaks in markdown rendering.

- Add trailing spaces to the end of lines where a line break is required - this is required for most lines of lyrics.

## EXAMPLES

Processed and verified charts in the folder `charts/` can be used as examples of the conventions and this can guide the cleanup of other charts.
