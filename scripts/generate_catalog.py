#!/usr/bin/env python3
"""Generate Obsidian catalog markdown stubs from yt-dlp info.json files.

Scans a media directory for *.info.json files and writes a corresponding
markdown file in the catalog directory if one does not already exist.
Existing catalog files are never overwritten, so manual notes and tags are
preserved across re-runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INFO_SUFFIX = ".info.json"
DESCRIPTION_SUFFIX = ".description"
VIDEO_EXTENSIONS = ("webm", "mp4", "mkv", "mov", "m4a", "mp3", "opus")
DESCRIPTION_HEADING = "## Description"
AUTO_SUMMARY_HEADING = "## Auto Summary"
CHAPTERS_HEADING = "## Chapters"
RESERVED_CATALOG_DIRS = {"media", ".obsidian", ".trash"}


def find_video_filename(media_dir: Path, basename: str) -> str | None:
    for extension in VIDEO_EXTENSIONS:
        candidate = media_dir / f"{basename}.{extension}"
        if candidate.exists():
            return candidate.name
    return None


def read_description(media_dir: Path, basename: str) -> str:
    description_path = media_dir / f"{basename}{DESCRIPTION_SUFFIX}"
    if not description_path.exists():
        return ""
    return description_path.read_text(encoding="utf-8").strip()


def render_markdown(info: dict, video_filename: str, description: str) -> str:
    frontmatter = ["---"]
    source_url = info.get("webpage_url") or info.get("original_url") or ""
    if source_url:
        frontmatter.append(f"source: {source_url}")
    frontmatter.append(f'media: "[[{video_filename}]]"')
    frontmatter.append("tags: []")
    frontmatter.append("---")

    body = [""]
    if description:
        body.extend([DESCRIPTION_HEADING, "", description, ""])

    return "\n".join(frontmatter + body) + "\n"


def add_description_to_existing(catalog_path: Path, description: str) -> bool:
    if not description:
        return False
    text = catalog_path.read_text(encoding="utf-8")
    if DESCRIPTION_HEADING in text:
        return False

    section = f"{DESCRIPTION_HEADING}\n\n{description}\n\n"
    for heading in (AUTO_SUMMARY_HEADING, CHAPTERS_HEADING):
        index = text.find(heading)
        if index != -1:
            new_text = text[:index] + section + text[index:]
            catalog_path.write_text(new_text, encoding="utf-8")
            return True

    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    catalog_path.write_text(text + section, encoding="utf-8")
    return True


def find_existing_catalog_file(catalog_dir: Path, basename: str) -> Path | None:
    target_name = f"{basename}.md"
    for candidate in catalog_dir.rglob(target_name):
        relative_parents = candidate.relative_to(catalog_dir).parts[:-1]
        if any(
            part.startswith(".") or part in RESERVED_CATALOG_DIRS
            for part in relative_parents
        ):
            continue
        if candidate.name == target_name:
            return candidate
    return None


def process_info_file(info_path: Path, catalog_dir: Path) -> tuple[bool, str]:
    basename = info_path.name[: -len(INFO_SUFFIX)]
    description = read_description(info_path.parent, basename)

    existing = find_existing_catalog_file(catalog_dir, basename)
    if existing is not None:
        relative = existing.relative_to(catalog_dir).as_posix()
        if add_description_to_existing(existing, description):
            return True, f"added description: {relative}"
        return False, f"skip (exists): {relative}"

    with info_path.open("r", encoding="utf-8") as fh:
        info = json.load(fh)

    video_filename = find_video_filename(info_path.parent, basename)
    if video_filename is None:
        extension = info.get("ext") or "webm"
        video_filename = f"{basename}.{extension}"

    catalog_path = catalog_dir / f"{basename}.md"
    catalog_path.write_text(
        render_markdown(info, video_filename, description), encoding="utf-8"
    )
    return True, f"wrote:  {catalog_path.name}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--media-dir",
        default="catalog/media",
        help="Directory containing yt-dlp output (default: catalog/media)",
    )
    parser.add_argument(
        "--catalog-dir",
        default="catalog",
        help="Directory for Obsidian markdown files (default: catalog)",
    )
    args = parser.parse_args()

    media_dir = Path(args.media_dir)
    catalog_dir = Path(args.catalog_dir)

    if not media_dir.is_dir():
        print(f"error: media directory not found: {media_dir}", file=sys.stderr)
        return 1
    catalog_dir.mkdir(parents=True, exist_ok=True)

    info_files = sorted(media_dir.glob(f"*{INFO_SUFFIX}"))
    if not info_files:
        print("no info.json files found")
        return 0

    exit_code = 0
    for info_path in info_files:
        try:
            _, message = process_info_file(info_path, catalog_dir)
            print(message)
        except Exception as exc:
            print(f"error: {info_path.name}: {exc}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
