# Add a video

`download.sh` is a thin wrapper around yt-dlp that drops the video and its
sidecars into `catalog/files/`, generates a markdown stub, then runs the
categorizer. The categorizer picks a shelf, fills tags, writes an auto
summary, and links series membership. Blobs in `catalog/files/` are
gitignored; only the markdown note ends up in git.

Requires the project's tooling installed via `uv` (run any `uv run ...` once
to populate the venv) and an agent CLI on `PATH` for the categorizer
step — `claude` by default, or `codex` when invoked with
`./download.sh --agent codex <url>`. If the source needs a proxy, set
`PROXY_URL` in `.env`.

## Procedure

1. From the repo root, run `./download.sh <url>`.
2. Wait for the run to finish. The output ends with a `wrote:
   <shelf>/<basename>.md` line from the categorizer once the note has been
   filed.
3. Open the note in Obsidian at `catalog/<shelf>/<basename>.md`. Review
   the auto-generated tags and `## Auto Summary` section; edit anything that
   looks off.
4. Commit the new `.md` file.

## Re-running

The pipeline is idempotent. If a step fails (network blip, missing
agent binary), fix the cause and re-run `./download.sh <url>`. The wrapper
only catalogs and categorizes files reported by that yt-dlp run; use the
commands below when you need to process existing files.

To re-run only the categorizer (for example, after manually clearing the
summary section): `uv run python scripts/categorize.py --basename <basename>`.
To re-pick the shelf on already-categorized notes without touching their
summary or tags: pass `--reshelve` to the same script.

## Manual fallback

If yt-dlp cannot reach the source, download the video by other means, save
it under `catalog/files/<title>.<ext>`, and write the note by hand
following the frontmatter of an existing video note (`type: video`,
`file: "[[<title>.<ext>]]"`, etc.). The categorizer needs yt-dlp's
`.info.json` sidecar, so manually-added videos do not get an auto summary.

## Files

- `download.sh` — orchestrates download, cataloguing, and categorization
- `scripts/catalog_videos.py` — writes the markdown stub from
  `*.info.json`
- `scripts/categorize.py` — picks shelf, fills tags, writes auto summary,
  links series
- `catalog/files/` — yt-dlp output (gitignored)
