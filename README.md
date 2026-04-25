# Library

A personal media library backed by Obsidian. Videos, books, and articles
live as source files under `catalog/files/` with a markdown note per item
filed onto a topical shelf elsewhere in `catalog/`.

## Layout

- `catalog/` — Obsidian vault. Notes live on shelves directly under
  `catalog/`; the underlying media lives in `catalog/files/` and is
  gitignored. Only the markdown notes are committed.
- `scripts/` — Python pipeline that ingests blobs from `catalog/files/`,
  writes note stubs, and shells out to an agent CLI (`claude` or
  `codex`, selectable via `--agent`) to fill in summary, tags, shelf
  placement, and series membership. See `CLAUDE.md` for the pipeline
  architecture and idempotency rules.
- `docs/runbooks/` — step-by-step procedures for routine tasks.
- `plugins/video-timestamps/` — small Obsidian plugin that turns
  timestamp text in a video note into a click-to-seek link.

## Common tasks

Routine operations live as runbooks under `docs/runbooks/`: adding a
video, adding a book or article, syncing `catalog/files/` with S3,
full-refreshing the catalog, and installing the Obsidian plugin. See
`docs/README.md` for the index. The architectural notes — pipeline
shape, idempotency rules, agent contract, and series handling — live in
`CLAUDE.md`.

## Conventions

### Shelves

Each cataloged item lives on exactly one **shelf** — a single folder
directly under `catalog/`. Shelves use the same metaphor as a real
library: one shelf location per item.

- **Naming**: kebab-lowercase. Lowercase letters, digits, and hyphens
  only. No spaces, no underscores, no capitals. Examples:
  `astronomy`, `physics`, `computer-engineering`, `databases`,
  `cryptography`, `philosophy`, `economic-history`.
- **Classification reference**: use Dewey Decimal Classification (DDC)
  or Library of Congress Classification (LCC) to identify the item's
  primary discipline, then convert that class or subclass into a plain
  folder name. Do not use call numbers or class letters as shelf names.
  For example, DDC 500 / LCC Q should usually become a specific science
  shelf such as `physics`, `cell-biology`, or `history-of-mathematics`;
  DDC 600 / LCC T should become a specific technology or engineering
  shelf such as `semiconductors` or `aviation`.
- **Specificity**: pick a specific descriptive subject, not a broad
  catch-all. Avoid shelves like `science`, `computer`, or `tech` —
  prefer something more specific.
- **Depth**: shelves are flat. No nested subfolders.
- **Reuse**: when an item fits an existing shelf, use it verbatim
  rather than coining a near-synonym.

### Multi-subject items

An item that spans multiple subjects gets one primary shelf and surfaces
elsewhere through tags and Maps of Content (MOCs). Same as a real
library: one shelf location, multiple catalog entries.

### Tags

Tags are the cross-cutting catalog. Use them for facets that cut across
shelves: subjects the item touches but isn't primarily about, notable
people (`feynman`), eras (`1970s`), themes (`first-principles`),
formats (`lecture`, `documentary`), or status (`to-read`, `to-watch`).

- Lowercase, hyphenated phrases or single words.
- Flat — no nested `parent/child` tags.

### Files

Source media (videos, PDFs, EPUBs, HTML snapshots, etc.) lives in
`catalog/files/`. Catalog notes link to them via the `file:`
frontmatter field. Obsidian is configured to treat `catalog/files/` as
the attachment folder and to hide it from quick switcher and search.

### Frontmatter

Every catalog note has the same frontmatter shape:

```yaml
---
source: <url, optional>
type: video | book | article
file: "[[some-file.ext]]"
series: "[[Series Title]]"   # optional, only for items that belong to a series
series_index: 2              # optional, 1-based position within the series
tags: [tag1, tag2]
---
```

The catalog scripts (`scripts/catalog_videos.py`,
`scripts/catalog_documents.py`) write this stub. `categorize.py`
later fills `tags:` and moves the note onto the chosen shelf.

### Series

A multi-volume work or ongoing series (e.g. `The Feynman Lectures on
Physics`, `Cosmos`, a multi-part lecture course) is represented as one
**series note** plus one regular catalog entry per volume/episode.

- The series note has frontmatter `type: series` and lives on the same
  shelf as its members. Filename is the canonical series title.
- Each volume keeps its own `## Description` and `## Auto Summary`. The
  series note carries a series-level summary plus a `## Volumes` section
  that links to each member with `[[wikilinks]]`, ordered by
  `series_index`.
- Volumes link back to the series via the `series:` frontmatter field.
- `categorize.py` decides series membership during cataloging (the
  agent matches against existing series titles) and rebuilds each
  series note's `## Volumes` section from the items pointing at it.
