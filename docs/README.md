# docs

Operational documentation for the library. Architecture and pipeline
invariants live in `CLAUDE.md` at the repo root; this directory holds
the runbooks for routine tasks.

## Runbooks

- `runbooks/add-a-video.md` — download a video by URL and let the
  pipeline catalog and categorize it.
- `runbooks/add-a-book.md` — drop a book or article into the vault and
  stub a note (manual tags and shelf placement).
- `runbooks/sync-files-with-s3.md` — push or pull `catalog/files/`
  to/from the S3 backup.
- `runbooks/full-refresh.md` — wipe shelves and re-categorize every
  note, or re-shelve only without losing summaries.
- `runbooks/install-the-obsidian-plugin.md` — install the
  `video-timestamps` plugin into the vault.
