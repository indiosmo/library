# video-timestamps

Small Obsidian plugin that turns timestamp text in a note (such as
`12:34` or `1:02:33`) into a click-to-seek link for the video named in
the note's `file:` frontmatter. Designed for the catalog's video
notes, where each note links to a single source file under
`catalog/files/`.

## Install

    plugins/video-timestamps/install.sh

The script copies the plugin files into
`catalog/.obsidian/plugins/video-timestamps/` and prints the manual
step to enable the plugin in Obsidian.

See `docs/runbooks/install-the-obsidian-plugin.md` for the full
procedure, including how the plugin integrates with note frontmatter
and how to update it after changes.

## Source layout

- `main.js` — plugin code.
- `manifest.json` — Obsidian plugin manifest.
- `styles.css` — styles for the rendered timestamp links.
- `install.sh` — installer; takes an optional vault path argument
  (defaults to `<repo>/catalog`).
