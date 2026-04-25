# Add a book or article

Books and articles are not fetched by tooling — drop the file into
`catalog/files/` yourself, then run the catalog pipeline. The first pass
scans for documents that do not yet have a matching markdown note and
writes a stub for each one. The note's `type` is inferred from the file
extension (book for PDF, EPUB, and similar formats; article for HTML,
Markdown, plain text). See `scripts/catalog_documents.py` for the full
extension mapping.

The categorizer then opens the source file, extracts an excerpt (title
page, table of contents, start of the first chapter) via
`scripts/document_extract.py`, and feeds it to the agent CLI together
with web-search results so it can fill in the summary, tags, shelf, and
series membership the same way it does for videos.

## Procedure

1. Copy the document into `catalog/files/`. Use a clean filename — it
   becomes the note's basename in Obsidian.
2. From the repo root, run `./catalog.sh` (or just
   `uv run python scripts/catalog_documents.py` followed by
   `uv run python scripts/categorize.py` if you only want the document
   passes). The first prints one `wrote: <basename>.md` line per new
   document; the second prints one line per categorized note.
3. Open the new note. The categorizer will have written `## Auto Summary`,
   filled `tags:`, and moved the note onto a shelf. Add a manual
   `## Description` or reading notes if you want.
4. Commit the `.md` file.

## Requirements

- PDFs use `pdfplumber` (Python, declared in `pyproject.toml`). Scanned
  PDFs fall back to OCR via `pdftoppm` (poppler-utils) plus
  `pytesseract` and the `tesseract` binary.
- EPUB and HTML excerpts go through `pandoc`.

## Re-running

Both scripts are safe to run repeatedly. `catalog_documents.py` never
overwrites an existing note. `categorize.py` skips any note that already
contains `## Auto Summary` and only fills `tags:` when the line is still
literally `tags: []`, so manual edits and shelf placement survive
re-runs. Use `categorize.py --reshelve` to re-pick a shelf for an
already-summarized note without touching its summary or tags.

## Files

- `scripts/catalog_documents.py` — scans `catalog/files/` and writes
  stubs for unmatched documents.
- `scripts/document_extract.py` — pulls an excerpt from PDF/EPUB/HTML
  for the categorizer prompt.
- `scripts/categorize.py` — drives the agent CLI to summarize, tag,
  and shelve each note.
- `catalog/files/` — document blobs (gitignored).
