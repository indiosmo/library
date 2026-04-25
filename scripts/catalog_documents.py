#!/usr/bin/env python3
"""Generate Obsidian catalog markdown stubs for books and articles.

Scans the files directory for document files (PDF, EPUB, HTML, Markdown,
etc.) and writes a corresponding markdown stub in the catalog directory if
one does not already exist. Existing catalog files are never overwritten,
so manual notes and tags are preserved across re-runs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from catalog_common import find_existing_catalog_file, render_frontmatter

BOOK_EXTENSIONS = {"pdf", "epub", "mobi", "azw", "azw3", "djvu"}
ARTICLE_EXTENSIONS = {"html", "htm", "mhtml", "md", "markdown", "txt"}
DOCUMENT_EXTENSIONS = BOOK_EXTENSIONS | ARTICLE_EXTENSIONS


def infer_type(extension: str) -> str:
    if extension in BOOK_EXTENSIONS:
        return "book"
    return "article"


def render_markdown(document_filename: str, document_type: str) -> str:
    return render_frontmatter(type_name=document_type, file_link=document_filename) + "\n"


def discover_documents(files_dir: Path) -> list[Path]:
    results: list[Path] = []
    for path in sorted(files_dir.iterdir()):
        if not path.is_file():
            continue
        extension = path.suffix.lower().lstrip(".")
        if extension not in DOCUMENT_EXTENSIONS:
            continue
        results.append(path)
    return results


def select_documents(files_dir: Path, basenames: list[str]) -> list[Path]:
    if not basenames:
        return discover_documents(files_dir)

    documents_by_stem = {path.stem: path for path in discover_documents(files_dir)}
    documents: list[Path] = []
    for basename in basenames:
        clean_basename = Path(basename).name
        document_path = documents_by_stem.get(clean_basename)
        if document_path is None:
            raise FileNotFoundError(f"document file not found: {clean_basename}")
        documents.append(document_path)
    return documents


def process_document(document_path: Path, catalog_dir: Path) -> tuple[bool, str]:
    basename = document_path.stem
    existing = find_existing_catalog_file(catalog_dir, basename)
    if existing is not None:
        relative = existing.relative_to(catalog_dir).as_posix()
        return False, f"skip (exists): {relative}"

    extension = document_path.suffix.lower().lstrip(".")
    document_type = infer_type(extension)
    catalog_path = catalog_dir / f"{basename}.md"
    catalog_path.write_text(
        render_markdown(document_path.name, document_type), encoding="utf-8"
    )
    return True, f"wrote:  {catalog_path.name} (type={document_type})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--files-dir",
        default="catalog/files",
        help="Directory containing document files (default: catalog/files)",
    )
    parser.add_argument(
        "--catalog-dir",
        default="catalog",
        help="Directory for Obsidian markdown files (default: catalog)",
    )
    parser.add_argument(
        "--basename",
        action="append",
        default=[],
        help=(
            "Process only this document basename, without extension. "
            "May be repeated."
        ),
    )
    args = parser.parse_args()

    files_dir = Path(args.files_dir)
    catalog_dir = Path(args.catalog_dir)

    if not files_dir.is_dir():
        print(f"error: files directory not found: {files_dir}", file=sys.stderr)
        return 1
    catalog_dir.mkdir(parents=True, exist_ok=True)

    try:
        documents = select_documents(files_dir, args.basename)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not documents:
        print("no document files found")
        return 0

    exit_code = 0
    for document_path in documents:
        try:
            _, message = process_document(document_path, catalog_dir)
            print(message)
        except Exception as exc:
            print(f"error: {document_path.name}: {exc}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
