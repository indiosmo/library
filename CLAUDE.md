# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal media library backed by an Obsidian vault. It is two things glued
together:

1. An Obsidian vault at `catalog/` containing one markdown note per
   cataloged item, organized into single-segment subfolders called
   **shelves** (e.g. `catalog/physics/`, `catalog/philosophy/`). The
   read-side conventions (shelves, tags, series, frontmatter shape) are
   spelled out in `README.md` and are authoritative — match them when
   creating or editing notes.
2. A small Python toolchain under `scripts/` that ingests blobs from
   `catalog/files/`, writes the markdown stubs, then shells out to an
   agent CLI (`claude` or `codex`, selectable via `--agent`) to fill in
   summary, tags, shelf placement, and series membership.

`catalog/files/` is the attachment directory: videos, PDFs, EPUBs,
HTML snapshots, etc. It is fully gitignored (`catalog/files/.gitignore`
is just `*`); only the `.md` notes are committed. Obsidian is configured
to treat `files/` as its attachment folder and to hide it from quick
switcher and search (`catalog/.obsidian/app.json`).

## Pipeline

```
catalog/files/<basename>.<ext>           (blob, gitignored)
catalog/files/<basename>.info.json       (yt-dlp sidecar, videos only)
        |
        v   scripts/catalog_videos.py / scripts/catalog_documents.py
        |   (writes a stub if no .md exists with that basename anywhere
        |    under catalog/, skipping reserved dirs)
        v
catalog/<basename>.md                    (stub at catalog root)
        |
        v   scripts/categorize.py  (shells out to `claude -p` or `codex exec`)
        |   - dispatches on the stub's `type:` frontmatter
        |   - video: reads yt-dlp's <basename>.info.json
        |   - book/article: opens the linked file and pulls a text
        |     excerpt (front matter, table of contents, intro) via
        |     scripts/document_extract.py
        |   - picks a shelf and moves the file into `catalog/<shelf>/<basename>.md`
        |   - fills empty `tags: []`
        |   - inserts `## Auto Summary`
        |   - if part of a series, links it and (re)builds the series note
        v
catalog/<shelf>/<basename>.md            (final filed location)
```

`./download.sh <url>` runs yt-dlp into `catalog/files/`, then chains
`catalog_videos.py` and `categorize.py` only for the files reported by that
download. `./catalog.sh` runs
all three passes over everything currently in `catalog/files/`;
`./catalog.sh --full-refresh` first deletes every non-`files/`,
non-dotfile entry under `catalog/` and re-catalogs from scratch.

The agent CLI must be on `PATH` for `categorize.py`. Pick the backend
with `--agent claude` (default) or `--agent codex` — pass it through
`./download.sh` and `./catalog.sh` as well. The categorizer enables
web research so it can look up speakers/events/topics/books for the
auto-summary: claude gets `--allowedTools WebSearch,WebFetch`, codex
gets `-c tools.web_search=true`.

Document excerpts use `pdfplumber` (Python dep) for PDFs, with an OCR
fallback via `pdftoppm` (poppler) plus `pytesseract` and the
`tesseract` binary for scanned PDFs. EPUBs and HTML go through
`pandoc`. None of these are fatal if missing — the script just sends an
empty excerpt and lets the agent rely on web search alone.

## Common commands

```bash
# Add a video by URL (download + catalog + categorize).
./download.sh <url>
./download.sh --agent codex <url>      # use codex instead of claude

# Re-run all three catalog passes over catalog/files/.
./catalog.sh
./catalog.sh --full-refresh            # nukes shelves first, keeps catalog/files/
./catalog.sh --agent codex             # use codex for the categorize pass

# Individual passes (each is idempotent; see "Idempotency" below).
uv run python scripts/catalog_videos.py
uv run python scripts/catalog_documents.py
uv run python scripts/categorize.py
uv run python scripts/categorize.py --agent codex
uv run python scripts/categorize.py --reshelve   # only re-pick shelf for already-categorized notes

# Sync the gitignored blobs in catalog/files/ to/from S3.
./sync.sh push          # local -> s3://indiosmo.library (profile: library)
./sync.sh pull          # s3://indiosmo.library -> local

# Install the local Obsidian plugin into the vault.
plugins/video-timestamps/install.sh
```

Python is managed via `uv` (Python >=3.13, declared in `pyproject.toml`
and `.python-version`). Just running any `uv run ...` once will
populate `.venv/`. There is no test suite, lint config, or build step.

`PROXY_URL` in `.env` (see `.env.sample`) is the only runtime config;
`download.sh` passes it to yt-dlp as `--proxy`.

## Architecture and invariants

### Where notes live, and what scripts touch

- Every catalog note has a basename matching its blob (the `<basename>` in
  `<basename>.<ext>` and `<basename>.info.json`). The cataloging scripts
  use the basename as the join key.
- The cataloging scripts walk `catalog/` recursively but **skip reserved
  directories**: anything starting with `.` (e.g. `.obsidian`,
  `.claude`, `.trash`) plus the literal `files`. This is centralized in
  `scripts/catalog_common.py:RESERVED_CATALOG_DIRS` /
  `is_reserved_dir_name`.
- `find_existing_catalog_file` (also in `catalog_common.py`) is the
  single source of truth for "does a note for this basename already
  exist anywhere under `catalog/`". Use it for any new tooling that
  needs the same lookup.

### Idempotency rules — DO NOT BREAK THESE

The whole pipeline is designed to be safe to re-run. Concretely:

- `catalog_videos.py` and `catalog_documents.py` **never overwrite**
  existing `.md` files. The only mutation they perform on an existing
  note is: if the note has no `## Description` section and the blob has
  a `.description` sidecar, they insert one above `## Auto Summary` /
  `## Chapters`. Manual edits to tags, body, and shelf placement
  survive re-runs.
- `categorize.py` skips any note that already contains
  `## Auto Summary`. It only fills `tags:` when the frontmatter line is
  literally `tags: []` (empty list) — the regex
  `r"^tags:\s*\[\s*\]\s*$"` is the gate that protects manual edits.
- The `--reshelve` flag re-picks a shelf for already-summarized notes
  but does **not** touch their summary, tags, or body.
- Any new ingestion step must preserve these properties: no overwriting
  notes, no stomping non-empty `tags:`, no rewriting `## Auto Summary`
  once present.

### Frontmatter and the agent contract

`scripts/catalog_common.py:render_frontmatter` is the single writer of
catalog frontmatter. It always emits `tags: []` so the categorizer
can later detect "untouched" tags. Keep using it rather than emitting
frontmatter inline.

`categorize.py` builds a prompt — `VIDEO_PROMPT_TEMPLATE` /
`VIDEO_SHELF_ONLY_PROMPT_TEMPLATE` for videos,
`DOCUMENT_PROMPT_TEMPLATE` / `DOCUMENT_SHELF_ONLY_PROMPT_TEMPLATE` for
books and articles — instructing the agent to return a single JSON
object with `summary`, `tags`, `shelf`, `series`, and `series_summary`.
The script then:

- normalizes the shelf via `normalize_shelf` (kebab-lowercase, single
  segment, not a reserved dir name) — invalid shelves are silently
  dropped and the note stays at the catalog root,
- normalizes tags via `normalize_tags` (lowercase, hyphenated, dedup),
- normalizes series via `normalize_series` (accepts both
  `{"name": ..., "index": ...}` and bare strings),
- uses `extract_json_object` to tolerate fenced code blocks around the
  JSON.

If you change the prompt, keep the response shape stable or update all
four normalizers in lockstep. The prompts also receive `existing_shelves`
and `existing_series` so the agent can reuse the established vocabulary
instead of coining synonyms — keep that data flowing in.

### Series notes

A series (multi-part work like `Cosmos`, `Feynman Lectures on Physics`)
is represented by a dedicated note with frontmatter `type: series`
plus one regular note per volume. `categorize.py`:

- Creates the series note via `ensure_series_note` on the same shelf as
  the volume that introduced it.
- Adds `series: "[[Series Title]]"` and optional `series_index: N` to
  each member's frontmatter (only if `series:` is not already present).
- After processing all files, calls `find_series_members` +
  `rebuild_volumes_section` to rewrite each series note's `## Volumes`
  section from the union of members currently pointing at it. The
  Volumes section is regenerated wholesale on every run, so do not put
  hand-edited content inside it — put it elsewhere in the series note.

### Obsidian vault

`catalog/.obsidian/` holds vault config; `catalog/.gitignore` excludes
`workspace.json` (committing it causes constant merge conflicts).
`plugins/video-timestamps/` is a small custom Obsidian plugin
maintained alongside the catalog; `install.sh` copies it into
`catalog/.obsidian/plugins/video-timestamps/`. It is not auto-installed
by anything else — run it once after cloning if you want timestamp
links to seek the linked video.

## Conventions

- Shelves: kebab-lowercase, single segment, specific (`databases`, not
  `tech`). Use Dewey Decimal Classification or Library of Congress
  Classification as a reference for the item's primary discipline, then
  convert that class/subclass into a plain subject folder name rather
  than a call number. Reuse existing shelves verbatim when an item fits.
  Multi-subject items get one shelf and surface elsewhere through tags.
- Tags: lowercase, hyphenated, flat (no `parent/child`). Used for
  cross-cutting facets (people, eras, formats, status).
- See `README.md` for the full rules; the prompts in
  `categorize.py` (`SHELF_GUIDANCE`, `SERIES_GUIDANCE`) repeat them
  in the form the agent sees.
- Per the user's global instructions: avoid glyphs/icons in code,
  comments, and CLI output; use explicit names (`playbook_file`, not
  `pb_file`); when refactoring, do not leave breadcrumbs about what
  the code used to do — describe present behavior or delete the
  comment.
