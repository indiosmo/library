"""Shared helpers for the catalog ingestion scripts."""

from __future__ import annotations

from pathlib import Path

RESERVED_CATALOG_DIRS = {"files", ".obsidian", ".trash"}


def is_reserved_dir_name(name: str) -> bool:
    return name.startswith(".") or name in RESERVED_CATALOG_DIRS


def find_existing_catalog_file(catalog_dir: Path, basename: str) -> Path | None:
    target_name = f"{basename}.md"
    for candidate in catalog_dir.rglob(target_name):
        relative_parents = candidate.relative_to(catalog_dir).parts[:-1]
        if any(is_reserved_dir_name(part) for part in relative_parents):
            continue
        if candidate.name == target_name:
            return candidate
    return None


def render_frontmatter(
    *,
    type_name: str,
    file_link: str | None = None,
    source_url: str | None = None,
) -> str:
    """Render the standard catalog frontmatter block.

    Tags are always emitted as an empty list; categorize fills them in
    later, and that step keys off the empty list to avoid clobbering manual
    edits. The `file` field is omitted for entries that aggregate other
    notes (e.g. series indexes) rather than pointing at a single source
    file.
    """
    lines = ["---"]
    if source_url:
        lines.append(f"source: {source_url}")
    lines.append(f"type: {type_name}")
    if file_link:
        lines.append(f'file: "[[{file_link}]]"')
    lines.append("tags: []")
    lines.append("---")
    return "\n".join(lines) + "\n"
