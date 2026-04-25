# Full-refresh the catalog

`./catalog.sh --full-refresh` deletes every shelf and root-level
markdown stub under `catalog/`, then re-runs the entire ingest
pipeline. Useful when the categorization rules have shifted enough
that you want every note re-summarized and re-shelved from scratch.

This is destructive: any manual edits to notes (descriptions, tags,
extra body content) are lost. The blobs in `catalog/files/` and dotfile
entries (`.obsidian/`, `.gitignore`, `.claude/`, etc.) are kept; every
non-dotfile entry under `catalog/` other than `files/` is removed
before the run.

If you only want to re-pick shelves for already-summarized notes
without losing their summaries or tags, use the lighter alternative
under "Re-shelve only" below.

## Procedure

1. Commit or stash any pending changes to notes you care about. The
   refresh wipes them.
2. From the repo root, run `./catalog.sh --full-refresh`.
3. Wait for the three passes (videos, documents, categorize) to
   complete. The categorize pass calls out to the agent CLI (`claude`
   by default, or `codex` via `--agent codex`) per note, so this can
   take a while on a large library.
4. Review the diff before committing. Spot-check a handful of notes;
   if the new summaries or shelf placements look wrong, tune the
   prompts in `scripts/categorize.py` and re-run.

## Re-shelve only

To re-pick shelves without losing summaries and tags:

    uv run python scripts/categorize.py --reshelve

This walks notes that already have an `## Auto Summary`, picks a fresh
shelf based on the current shelf vocabulary, and moves them. Summary,
tags, and body are left alone.

## Files

- `catalog.sh` — orchestrates the three passes and the wipe.
- `scripts/categorize.py` — the LLM-driven shelf, tag, summary, and
  series step (also hosts the `--reshelve` mode).
