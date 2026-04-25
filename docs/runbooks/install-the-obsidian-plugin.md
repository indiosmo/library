# Install the video-timestamps plugin

`plugins/video-timestamps/` is a small Obsidian plugin maintained
alongside the catalog. It scans note bodies for timestamp text (such
as `12:34` or `1:02:33`) and turns them into click-to-seek links for
the video named in the note's `file:` frontmatter. Without it,
timestamps are just plain text.

Nothing else installs the plugin automatically. Run the install script
once after cloning, and again whenever the plugin source changes.

## Procedure

1. From the repo root, run `plugins/video-timestamps/install.sh`. The
   script copies the plugin files into
   `catalog/.obsidian/plugins/video-timestamps/`. It refuses to run if
   `catalog/.obsidian/` is missing.
2. In Obsidian, open the vault at `catalog/`, then go to Settings →
   Community plugins and enable "Video Timestamps". If Restricted Mode
   is on, turn it off first.
3. Open a video note that contains a timestamp in its body and click
   the timestamp. The linked video should seek to that position.

## Updating

When the plugin source changes (`main.js`, `manifest.json`, or
`styles.css`), re-run the install script. Reload the vault in
Obsidian (Ctrl/Cmd+R, or restart the app) to pick up the new files.

## Files

- `plugins/video-timestamps/install.sh` — copies plugin files into the
  vault. Takes an optional vault path argument; defaults to
  `<repo>/catalog`.
- `plugins/video-timestamps/{main.js,manifest.json,styles.css}` —
  plugin source.
- `catalog/.obsidian/plugins/video-timestamps/` — install destination
  inside the vault.
