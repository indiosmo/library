#!/usr/bin/env python3
"""Categorize catalog markdown files: shelf, tags, summary, and series membership via an agent CLI.

Scans catalog markdown files (recursively) and, for any file that does not
already contain a `## Auto Summary` section, invokes the chosen agent CLI
(`claude -p` or `codex exec`, selectable via `--agent`) with the
corresponding item's metadata and:

  - Picks a `shelf` (single-segment kebab-lowercase folder under the
    catalog root, e.g. `astronomy`, `computer-engineering`) and moves the
    note there.
  - Writes topical `tags` into the frontmatter list (only if the list is
    currently empty, so manual edits are preserved).
  - Inserts an `## Auto Summary` section that adds context beyond the
    uploader's description (the description itself lives in its own
    `## Description` section). The body may be empty when there is nothing
    meaningful to add.
  - Detects `series` membership and links the note to a dedicated series
    note (created on demand), then rebuilds each series note's `## Volumes`
    list from the union of its members.

The agent is allowed to use WebSearch and WebFetch to research the speaker,
event, or topic so the summary can include genuinely new information.

The prompt and the metadata fed to the agent depend on the note's
`type:` frontmatter:

  - `video`: yt-dlp's `<basename>.info.json` sidecar provides title,
    description, and chapters.
  - `book` / `article`: the source file in `catalog/files/` is opened and
    a text excerpt (front matter, table of contents, start of the first
    chapter) is extracted via `document_extract.extract_document_text`.

The script is idempotent: rerunning skips any file that already has an
Auto Summary section.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from catalog_common import is_reserved_dir_name, render_frontmatter
from document_extract import extract_document_text

INFO_SUFFIX = ".info.json"
AUTO_SUMMARY_HEADING = "## Auto Summary"
DESCRIPTION_HEADING = "## Description"
CHAPTERS_HEADING = "## Chapters"
VOLUMES_HEADING = "## Volumes"
DESCRIPTION_CHAR_LIMIT = 8000
SUPPORTED_AGENTS = ("claude", "codex")
CLAUDE_ALLOWED_TOOLS = "WebSearch,WebFetch"
CODEX_WEB_SEARCH_CONFIG = "tools.web_search=true"
INDEX_FILENAMES = {"index.md"}
SHELF_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*")
SERIES_TYPE = "series"
VIDEO_TYPE = "video"
DOCUMENT_TYPES = ("book", "article")
SERIES_FILENAME_FORBIDDEN = re.compile(r'[\\/:*?"<>|]+')

SHELF_GUIDANCE = """The shelf is a single folder under the catalog root, treated like a shelf in
a real library. Rules:

  - Single segment only. No slashes, no nested paths.
  - Kebab-lowercase: lowercase letters, digits, and hyphens. No spaces, no
    underscores, no capitals.
  - Use Dewey Decimal Classification (DDC) or Library of Congress
    Classification (LCC) as a reference for the item's primary discipline
    before choosing the folder name. Do not return DDC numbers or LCC call
    letters; convert the likely class/subclass into a plain subject shelf.
    Useful anchors:
      - DDC 000 / LCC Z, QA76: information, computer science, data,
        bibliography, libraries.
      - DDC 100 / LCC B: philosophy, psychology, logic, ethics.
      - DDC 200 / LCC B: religion, theology, mythology.
      - DDC 300 / LCC H-J-K-L: social sciences, economics, politics, law,
        education.
      - DDC 400 / LCC P: language and linguistics.
      - DDC 500 / LCC Q: mathematics and natural sciences.
      - DDC 600 / LCC R-S-T: medicine, agriculture, technology, engineering.
      - DDC 700 / LCC M-N: arts, music, design, recreation.
      - DDC 800 / LCC P: literature, rhetoric, criticism.
      - DDC 900 / LCC D-E-F-G: history, geography, biography, anthropology.
  - Pick a specific descriptive subject, not a broad catch-all. Good
    shelves: `astronomy`, `physics`, `computer-engineering`, `databases`,
    `cryptography`, `philosophy`, `economic-history`, `cognitive-science`,
    `linguistics`. Avoid overly broad shelves like `science`, `computer`,
    or `tech` — pick something more specific.
  - When the DDC/LCC class is broad, use the closest recognizable subclass
    as the shelf: for example `history-of-mathematics` over `mathematics`
    for a history of notation, `semiconductors` over `technology` for chip
    manufacturing, `aviation` over `transportation` for piloting, and
    `safety-science` over `engineering` for human-error systems safety.
  - If the item clearly fits one of the existing shelves listed below,
    reuse it verbatim rather than coining a near-synonym.
  - Items that span multiple subjects get one primary shelf; the other
    subjects go in `tags`. Same as a real library: one shelf location,
    multiple catalog entries via tags."""

SERIES_GUIDANCE = """A series groups multiple volumes, parts, or episodes that belong to the
same overarching work (e.g. `The Feynman Lectures on Physics`, `Cosmos`,
`The Art of Computer Programming`). Rules:

  - Only set `series` when the item is genuinely part of a multi-part work.
    A standalone lecture or one-off video is NOT a series. When in doubt,
    leave `series` null.
  - `series.name` must be the canonical title of the whole series, never
    the title of a single volume. Strip volume/part/episode suffixes.
  - If the canonical name matches one of the existing series listed below,
    reuse it VERBATIM. Do not coin near-synonyms.
  - `series.index` is the 1-based position of this item within the series
    (volume number, part number, episode number). Omit when the ordering
    is genuinely unknown.
  - `series_summary` is a short (1-3 sentence) description of the series
    as a whole. ONLY fill it when introducing a new series not already
    listed below; leave it empty when matching an existing series."""

VIDEO_SHELF_ONLY_PROMPT_TEMPLATE = """You are filing an already-summarized video for a personal research library.

Pick the most appropriate `shelf` slug for this video.

{shelf_guidance}

Existing shelves in this library (reuse when applicable):
{existing_shelves}

Respond with a single JSON object and nothing else:
{{"shelf": "astronomy"}}

Title: {title}
Source: {source}

Description (from uploader):
{description}

Chapters:
{chapters}
"""

VIDEO_PROMPT_TEMPLATE = """You are categorizing a video for a personal research library.

The uploader's description is shown below. The catalog already renders it in a
separate `## Description` section, so do NOT restate or paraphrase it. Your job
is to produce an `## Auto Summary` that adds genuinely new context the
description does not cover, for example: who the speaker is, what the event or
series was, the historical or technical background, related work, or notable
points raised in the chapters that the description omits.

You may use the WebSearch and WebFetch tools to research the video, speaker,
event, or topic so the summary can include accurate additional information.

Produce:
1. A short (1-4 sentence) plain-prose `summary` of additional context beyond
   the description. If the description already covers everything important and
   you cannot find anything meaningful to add, return an empty string for
   `summary`. Do not start with "This video".
2. Between 3 and 7 lowercase topical `tags`. Tags are the cross-cutting
   catalog: subjects this item touches that aren't the primary shelf,
   notable people, eras, themes, or formats. Examples: `biology`,
   `computer-science`, `feynman`, `1970s`, `lecture`, `first-principles`,
   `documentary`. Use single words or hyphenated phrases. Keep tags flat
   (no nested `parent/child` form).
3. A `shelf` slug used to file this note.
4. Optional `series` membership: if this item is part of a multi-volume work
   or ongoing series, return `{{"name": "Canonical Series Title", "index": 2}}`
   (omit `index` when unknown). Set `series` to null for standalone items.
5. Optional `series_summary`: a 1-3 sentence description of the whole series,
   set ONLY when introducing a new series not already listed below.

{shelf_guidance}

Existing shelves in this library (reuse when applicable):
{existing_shelves}

{series_guidance}

Existing series in this library (reuse when applicable):
{existing_series}

Respond with a single JSON object and nothing else, in this exact shape:
{{"summary": "...", "tags": ["tag1", "tag2"], "shelf": "astronomy", "series": null, "series_summary": ""}}

Title: {title}
Source: {source}

Description (from uploader):
{description}

Chapters:
{chapters}
"""

DOCUMENT_PROMPT_TEMPLATE = """You are categorizing a {kind} for a personal research library.

Below is the catalog basename (which usually encodes the title, author, and
year) and an excerpt extracted from the start of the document — typically
the title page, front matter, table of contents, and the beginning of the
first chapter. Use this excerpt as ground truth for what the document is.

You MUST also use WebSearch and WebFetch to look up the canonical title,
author(s), publication context, and a synopsis. Do not rely on the basename
or filename alone for facts.

Produce:
1. A 2-5 sentence plain-prose `summary` covering: what the {kind} is, who
   wrote it, when it was published, and the core thesis or scope. Add
   notable context where useful (era, audience, why it matters). Do not
   start with "This {kind}".
2. Between 3 and 7 lowercase topical `tags` (subjects, eras, people,
   themes, formats). Single words or hyphenated phrases. Keep tags flat
   (no nested `parent/child` form).
3. A `shelf` slug used to file this note.
4. Optional `series` membership: if this {kind} is part of a multi-volume
   work, return `{{"name": "Canonical Series Title", "index": 2}}`. Use
   null for standalone items. Volume numbering goes in `index`; do not
   include the volume number in `name`.
5. Optional `series_summary`: a 1-3 sentence description of the whole
   series, set ONLY when introducing a new series not already listed below.

{shelf_guidance}

Existing shelves in this library (reuse when applicable):
{existing_shelves}

{series_guidance}

Existing series in this library (reuse when applicable):
{existing_series}

Respond with a single JSON object and nothing else, in this exact shape:
{{"summary": "...", "tags": ["tag1", "tag2"], "shelf": "philosophy", "series": null, "series_summary": ""}}

Title (from filename): {title}
Source file: {source}

Excerpt from the start of the {kind}:
{excerpt}
"""

DOCUMENT_SHELF_ONLY_PROMPT_TEMPLATE = """You are filing an already-summarized {kind} for a personal research library.

Pick the most appropriate `shelf` slug for this {kind}.

{shelf_guidance}

Existing shelves in this library (reuse when applicable):
{existing_shelves}

Respond with a single JSON object and nothing else:
{{"shelf": "philosophy"}}

Title (from filename): {title}
Source file: {source}

Existing summary:
{summary}

Excerpt from the start of the {kind}:
{excerpt}
"""


def load_info(info_path: Path) -> dict:
    with info_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def format_chapters_for_prompt(chapters) -> str:
    if not chapters:
        return "(none)"
    lines = []
    for chapter in chapters:
        start = chapter.get("start_time")
        if start is None:
            continue
        title = (chapter.get("title") or "").strip()
        lines.append(f"- {int(start)}s: {title}")
    return "\n".join(lines) if lines else "(none)"


def _format_existing_shelves(existing_shelves: list[str]) -> str:
    if not existing_shelves:
        return "(none yet)"
    return "\n".join(f"- {shelf}" for shelf in existing_shelves)


def _format_existing_series(series: dict) -> str:
    name = series.get("name", "")
    summary = (series.get("summary") or "").strip()
    if summary:
        return f"- {name}: {summary}"
    return f"- {name}"


def _format_existing_series_list(existing_series: list[dict] | None) -> str:
    if not existing_series:
        return "(none yet)"
    return "\n".join(_format_existing_series(series) for series in existing_series)


def _video_prompt_fields(
    info: dict,
    existing_shelves: list[str],
    existing_series: list[dict] | None = None,
) -> dict:
    title = info.get("title") or info.get("fulltitle") or "(unknown)"
    source = info.get("webpage_url") or info.get("original_url") or "(unknown)"
    description = (info.get("description") or "").strip() or "(none)"
    if len(description) > DESCRIPTION_CHAR_LIMIT:
        description = description[:DESCRIPTION_CHAR_LIMIT] + "\n[truncated]"
    chapters = format_chapters_for_prompt(info.get("chapters"))
    return {
        "title": title,
        "source": source,
        "description": description,
        "chapters": chapters,
        "existing_shelves": _format_existing_shelves(existing_shelves),
        "existing_series": _format_existing_series_list(existing_series),
        "shelf_guidance": SHELF_GUIDANCE,
        "series_guidance": SERIES_GUIDANCE,
    }


def _document_prompt_fields(
    title: str,
    source_filename: str,
    excerpt: str,
    kind: str,
    existing_shelves: list[str],
    existing_series: list[dict] | None = None,
    existing_summary: str = "",
) -> dict:
    excerpt_text = excerpt.strip() or "(no text could be extracted from the file)"
    return {
        "kind": kind,
        "title": title,
        "source": source_filename,
        "excerpt": excerpt_text,
        "summary": existing_summary.strip() or "(none)",
        "existing_shelves": _format_existing_shelves(existing_shelves),
        "existing_series": _format_existing_series_list(existing_series),
        "shelf_guidance": SHELF_GUIDANCE,
        "series_guidance": SERIES_GUIDANCE,
    }


def build_video_prompt(
    info: dict,
    existing_shelves: list[str],
    existing_series: list[dict],
) -> str:
    return VIDEO_PROMPT_TEMPLATE.format(
        **_video_prompt_fields(info, existing_shelves, existing_series)
    )


def build_video_shelf_only_prompt(info: dict, existing_shelves: list[str]) -> str:
    return VIDEO_SHELF_ONLY_PROMPT_TEMPLATE.format(
        **_video_prompt_fields(info, existing_shelves)
    )


def build_document_prompt(
    title: str,
    source_filename: str,
    excerpt: str,
    kind: str,
    existing_shelves: list[str],
    existing_series: list[dict],
) -> str:
    return DOCUMENT_PROMPT_TEMPLATE.format(
        **_document_prompt_fields(
            title=title,
            source_filename=source_filename,
            excerpt=excerpt,
            kind=kind,
            existing_shelves=existing_shelves,
            existing_series=existing_series,
        )
    )


def build_document_shelf_only_prompt(
    title: str,
    source_filename: str,
    excerpt: str,
    kind: str,
    existing_summary: str,
    existing_shelves: list[str],
) -> str:
    return DOCUMENT_SHELF_ONLY_PROMPT_TEMPLATE.format(
        **_document_prompt_fields(
            title=title,
            source_filename=source_filename,
            excerpt=excerpt,
            kind=kind,
            existing_shelves=existing_shelves,
            existing_summary=existing_summary,
        )
    )


def call_agent(prompt: str, agent: str, agent_bin: str, timeout: int) -> str:
    if agent == "claude":
        result = subprocess.run(
            [agent_bin, "-p", "--allowedTools", CLAUDE_ALLOWED_TOOLS],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude exited with code {result.returncode}: {result.stderr.strip()}"
            )
        return result.stdout.strip()

    if agent == "codex":
        with tempfile.NamedTemporaryFile(
            "r", suffix=".txt", delete=False, encoding="utf-8"
        ) as last_message_file:
            last_message_path = Path(last_message_file.name)
        try:
            result = subprocess.run(
                [
                    agent_bin,
                    "exec",
                    "--skip-git-repo-check",
                    "--color",
                    "never",
                    "-c",
                    CODEX_WEB_SEARCH_CONFIG,
                    "--output-last-message",
                    str(last_message_path),
                    "-",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"codex exited with code {result.returncode}: {result.stderr.strip()}"
                )
            return last_message_path.read_text(encoding="utf-8").strip()
        finally:
            last_message_path.unlink(missing_ok=True)

    raise ValueError(f"unsupported agent: {agent}")


def extract_json_object(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    else:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(f"no JSON object found in claude output: {text[:200]!r}")
        candidate = match.group(0)
    parsed = json.loads(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("claude returned non-object JSON")
    return parsed


def normalize_series(raw_series) -> tuple[str, int | None]:
    """Extract a (name, index) tuple from the agent's `series` field.

    Accepts either a dict ``{"name": ..., "index": ...}`` or a bare string.
    Returns ``("", None)`` when the field is missing, null, or unusable.
    """
    if raw_series is None:
        return "", None
    if isinstance(raw_series, str):
        name = raw_series.strip()
        return _sanitize_series_name(name), None
    if not isinstance(raw_series, dict):
        return "", None

    name_value = raw_series.get("name") or raw_series.get("title") or ""
    name = _sanitize_series_name(str(name_value).strip()) if name_value else ""
    if not name:
        return "", None

    index_value = raw_series.get("index")
    if index_value is None:
        index_value = raw_series.get("volume") or raw_series.get("part")
    index: int | None
    if isinstance(index_value, bool):
        index = None
    elif isinstance(index_value, int):
        index = index_value
    elif isinstance(index_value, str) and index_value.strip().isdigit():
        index = int(index_value.strip())
    else:
        index = None
    if index is not None and index <= 0:
        index = None
    return name, index


def _sanitize_series_name(name: str) -> str:
    cleaned = SERIES_FILENAME_FORBIDDEN.sub(" ", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned


def normalize_tags(raw_tags) -> list[str]:
    if not isinstance(raw_tags, list):
        return []
    cleaned = []
    seen = set()
    for tag in raw_tags:
        if not isinstance(tag, str):
            continue
        normalized = tag.strip().lower().replace(" ", "-")
        if normalized and normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[: end + len("\n---\n")], text[end + len("\n---\n") :]


def update_tags_in_frontmatter(frontmatter: str, tags: list[str]) -> tuple[str, bool]:
    if not tags:
        return frontmatter, False
    empty_pattern = re.compile(r"^tags:\s*\[\s*\]\s*$", re.MULTILINE)
    if not empty_pattern.search(frontmatter):
        return frontmatter, False
    yaml_block = "tags:\n" + "\n".join(f"  - {tag}" for tag in tags)
    return empty_pattern.sub(yaml_block, frontmatter, count=1), True


def add_series_to_frontmatter(
    frontmatter: str, series_name: str, series_index: int | None
) -> bool | tuple[str, bool]:
    """Insert `series` and optional `series_index` keys into a frontmatter block.

    Returns ``(updated_frontmatter, True)`` when fields were added, or the
    original block with ``False`` when no change was needed (e.g. the keys are
    already present, or the series name is empty).
    """
    if not series_name:
        return frontmatter, False
    if re.search(r"^series:\s*", frontmatter, re.MULTILINE):
        return frontmatter, False

    new_lines = [f'series: "[[{series_name}]]"']
    if series_index is not None:
        new_lines.append(f"series_index: {series_index}")

    lines = frontmatter.split("\n")
    for position, line in enumerate(lines):
        if line.startswith("tags:"):
            lines[position:position] = new_lines
            return "\n".join(lines), True

    for position in range(len(lines) - 1, -1, -1):
        if lines[position].strip() == "---":
            lines[position:position] = new_lines
            return "\n".join(lines), True

    return frontmatter, False


def parse_frontmatter_type(frontmatter: str) -> str:
    match = re.search(r"^type:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()


def parse_frontmatter_file_link(frontmatter: str) -> str:
    match = re.search(r'^file:\s*"\[\[(.+?)\]\]"\s*$', frontmatter, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()


def parse_frontmatter_series(frontmatter: str) -> tuple[str, int | None]:
    name_match = re.search(
        r'^series:\s*"\[\[(.+?)\]\]"\s*$', frontmatter, re.MULTILINE
    )
    if not name_match:
        return "", None
    name = name_match.group(1).strip()
    index_match = re.search(
        r"^series_index:\s*(\d+)\s*$", frontmatter, re.MULTILINE
    )
    index = int(index_match.group(1)) if index_match else None
    return name, index


def insert_auto_summary(body: str, summary: str) -> str:
    summary = summary.strip()
    section = (
        f"{AUTO_SUMMARY_HEADING}\n\n{summary}\n\n"
        if summary
        else f"{AUTO_SUMMARY_HEADING}\n\n"
    )
    insert_index = body.find(CHAPTERS_HEADING)
    if insert_index == -1:
        if not body.endswith("\n"):
            body += "\n"
        if not body.endswith("\n\n"):
            body += "\n"
        return body + section
    return body[:insert_index] + section + body[insert_index:]


def find_info_for_catalog(catalog_path: Path, files_dir: Path) -> Path | None:
    candidate = files_dir / f"{catalog_path.stem}{INFO_SUFFIX}"
    if candidate.exists():
        return candidate
    return None


def discover_existing_shelves(catalog_dir: Path) -> list[str]:
    shelves: list[str] = []
    for top in sorted(catalog_dir.iterdir()):
        if not top.is_dir() or is_reserved_dir_name(top.name):
            continue
        shelves.append(top.name)
    return shelves


def discover_catalog_files(catalog_dir: Path) -> list[Path]:
    results: list[Path] = []
    for path in sorted(catalog_dir.rglob("*.md")):
        relative_parents = path.relative_to(catalog_dir).parts[:-1]
        if any(is_reserved_dir_name(part) for part in relative_parents):
            continue
        if path.name in INDEX_FILENAMES:
            continue
        results.append(path)
    return results


def select_catalog_files(catalog_dir: Path, basenames: list[str]) -> list[Path]:
    if not basenames:
        return discover_catalog_files(catalog_dir)

    catalog_files: list[Path] = []
    for basename in basenames:
        clean_basename = Path(basename).name
        matches = [
            path
            for path in discover_catalog_files(catalog_dir)
            if path.stem == clean_basename
        ]
        if not matches:
            raise FileNotFoundError(f"catalog markdown not found: {clean_basename}")
        if len(matches) > 1:
            raise RuntimeError(f"multiple catalog markdown files found: {clean_basename}")
        catalog_files.append(matches[0])
    return catalog_files


def discover_series_notes(catalog_dir: Path) -> dict[str, dict]:
    """Map each existing series note's title to its location and summary."""
    series: dict[str, dict] = {}
    for path in discover_catalog_files(catalog_dir):
        text = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(text)
        if not re.search(r"^type:\s*series\s*$", frontmatter, re.MULTILINE):
            continue
        name = path.stem
        relative_parents = path.relative_to(catalog_dir).parts[:-1]
        shelf = relative_parents[0] if relative_parents else ""
        series[name] = {
            "name": name,
            "summary": extract_auto_summary(body),
            "path": path,
            "shelf": shelf,
        }
    return series


def extract_auto_summary(body: str) -> str:
    match = re.search(
        rf"^{re.escape(AUTO_SUMMARY_HEADING)}\s*\n(.*?)(?=^## |\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return ""
    return match.group(1).strip()


def ensure_series_note(
    catalog_dir: Path,
    series_name: str,
    shelf: str,
    summary: str,
    existing: dict[str, dict],
) -> tuple[Path, bool]:
    """Create the series note if missing; return (path, created)."""
    if series_name in existing:
        return existing[series_name]["path"], False

    target_dir = catalog_dir / shelf if shelf else catalog_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    series_path = target_dir / f"{series_name}.md"

    summary = (summary or "").strip()
    summary_block = (
        f"{AUTO_SUMMARY_HEADING}\n\n{summary}\n\n"
        if summary
        else f"{AUTO_SUMMARY_HEADING}\n\n"
    )
    volumes_block = f"{VOLUMES_HEADING}\n\n"
    content = (
        render_frontmatter(type_name=SERIES_TYPE)
        + "\n"
        + summary_block
        + volumes_block
    )
    series_path.write_text(content, encoding="utf-8")
    return series_path, True


def find_series_members(
    catalog_dir: Path, series_name: str
) -> list[tuple[Path, int | None]]:
    members: list[tuple[Path, int | None]] = []
    for path in discover_catalog_files(catalog_dir):
        text = path.read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(text)
        if re.search(r"^type:\s*series\s*$", frontmatter, re.MULTILINE):
            continue
        name, index = parse_frontmatter_series(frontmatter)
        if name != series_name:
            continue
        members.append((path, index))
    members.sort(
        key=lambda entry: (
            entry[1] is None,
            entry[1] if entry[1] is not None else 0,
            entry[0].stem.lower(),
        )
    )
    return members


def rebuild_volumes_section(series_path: Path, member_titles: list[str]) -> bool:
    text = series_path.read_text(encoding="utf-8")
    if member_titles:
        body = "\n".join(f"- [[{title}]]" for title in member_titles) + "\n"
    else:
        body = ""
    new_block = f"{VOLUMES_HEADING}\n\n{body}"

    pattern = re.compile(
        rf"^{re.escape(VOLUMES_HEADING)}\b.*?(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    if pattern.search(text):
        new_text = pattern.sub(new_block + "\n", text, count=1)
    else:
        if not text.endswith("\n"):
            text += "\n"
        if not text.endswith("\n\n"):
            text += "\n"
        new_text = text + new_block

    if new_text == text:
        return False
    series_path.write_text(new_text, encoding="utf-8")
    return True


def normalize_shelf(raw) -> str:
    if not isinstance(raw, str):
        return ""
    cleaned = raw.strip().strip("/").lower().replace("\\", "/")
    if not cleaned or "/" in cleaned:
        return ""
    cleaned = cleaned.replace(" ", "-")
    if not SHELF_PATTERN.fullmatch(cleaned):
        return ""
    if is_reserved_dir_name(cleaned):
        return ""
    return cleaned


def move_to_shelf(
    catalog_path: Path, catalog_dir: Path, shelf: str
) -> tuple[Path, bool]:
    if not shelf:
        return catalog_path, False
    target_dir = catalog_dir / shelf
    target = target_dir / catalog_path.name
    if target.resolve() == catalog_path.resolve():
        return catalog_path, False
    target_dir.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")
    shutil.move(str(catalog_path), str(target))
    return target, True


def process_catalog_file(
    catalog_path: Path,
    files_dir: Path,
    catalog_dir: Path,
    existing_shelves: list[str],
    existing_series: dict[str, dict],
    agent: str,
    agent_bin: str,
    timeout: int,
    reshelve: bool,
) -> str:
    text = catalog_path.read_text(encoding="utf-8")
    frontmatter_existing, body_existing = split_frontmatter(text)
    type_name = parse_frontmatter_type(frontmatter_existing)
    if type_name == SERIES_TYPE:
        return f"skip (series note): {catalog_path.relative_to(catalog_dir).as_posix()}"

    relative_label = catalog_path.relative_to(catalog_dir).as_posix()
    has_summary = AUTO_SUMMARY_HEADING in text

    if type_name == VIDEO_TYPE:
        info_path = find_info_for_catalog(catalog_path, files_dir)
        if info_path is None:
            return f"skip (no info.json): {relative_label}"
        info = load_info(info_path)
        prompt_kwargs = {"info": info}
    elif type_name in DOCUMENT_TYPES:
        file_link = parse_frontmatter_file_link(frontmatter_existing)
        if not file_link:
            return f"skip (no file link in frontmatter): {relative_label}"
        document_path = files_dir / file_link
        if not document_path.exists():
            return f"skip (source file missing: {file_link}): {relative_label}"
        excerpt = extract_document_text(document_path)
        prompt_kwargs = {
            "title": catalog_path.stem,
            "source_filename": document_path.name,
            "excerpt": excerpt,
            "kind": type_name,
        }
    else:
        return f"skip (unsupported type={type_name!r}): {relative_label}"

    if has_summary and not reshelve:
        return f"skip (already summarized): {relative_label}"

    if has_summary and reshelve:
        if type_name == VIDEO_TYPE:
            prompt = build_video_shelf_only_prompt(prompt_kwargs["info"], existing_shelves)
        else:
            existing_summary = extract_auto_summary(body_existing)
            prompt = build_document_shelf_only_prompt(
                title=prompt_kwargs["title"],
                source_filename=prompt_kwargs["source_filename"],
                excerpt=prompt_kwargs["excerpt"],
                kind=prompt_kwargs["kind"],
                existing_summary=existing_summary,
                existing_shelves=existing_shelves,
            )
        raw_response = call_agent(prompt, agent, agent_bin, timeout)
        parsed = extract_json_object(raw_response)
        shelf = normalize_shelf(parsed.get("shelf"))

        final_path, moved = move_to_shelf(catalog_path, catalog_dir, shelf)
        final_label = final_path.relative_to(catalog_dir).as_posix()

        if not shelf:
            return f"reshelve: {final_label} (shelf=unset)"
        if moved:
            return f"reshelve: {final_label} (shelf={shelf}, moved)"
        return f"reshelve: {final_label} (shelf={shelf}, unchanged)"

    if type_name == VIDEO_TYPE:
        prompt = build_video_prompt(
            prompt_kwargs["info"], existing_shelves, list(existing_series.values())
        )
    else:
        prompt = build_document_prompt(
            title=prompt_kwargs["title"],
            source_filename=prompt_kwargs["source_filename"],
            excerpt=prompt_kwargs["excerpt"],
            kind=prompt_kwargs["kind"],
            existing_shelves=existing_shelves,
            existing_series=list(existing_series.values()),
        )
    raw_response = call_agent(prompt, agent, agent_bin, timeout)
    parsed = extract_json_object(raw_response)

    raw_summary = parsed.get("summary")
    summary = (raw_summary or "").strip() if isinstance(raw_summary, str) else ""
    tags = normalize_tags(parsed.get("tags"))
    shelf = normalize_shelf(parsed.get("shelf"))
    series_name, series_index = normalize_series(parsed.get("series"))
    raw_series_summary = parsed.get("series_summary")
    series_summary = (
        raw_series_summary.strip()
        if isinstance(raw_series_summary, str)
        else ""
    )

    frontmatter, body = split_frontmatter(text)
    frontmatter, tags_updated = update_tags_in_frontmatter(frontmatter, tags)
    frontmatter, series_added = add_series_to_frontmatter(
        frontmatter, series_name, series_index
    )
    body = insert_auto_summary(body, summary)
    catalog_path.write_text(frontmatter + body, encoding="utf-8")

    final_path, moved = move_to_shelf(catalog_path, catalog_dir, shelf)
    final_label = final_path.relative_to(catalog_dir).as_posix()

    series_note: str
    if series_name:
        series_note_path, created = ensure_series_note(
            catalog_dir,
            series_name,
            shelf,
            series_summary,
            existing_series,
        )
        existing_series[series_name] = {
            "name": series_name,
            "summary": series_summary
            or existing_series.get(series_name, {}).get("summary", ""),
            "path": series_note_path,
            "shelf": shelf,
        }
        index_note = (
            f"index={series_index}" if series_index is not None else "index=?"
        )
        if created:
            series_note = f"series={series_name} ({index_note}, created)"
        elif series_added:
            series_note = f"series={series_name} ({index_note}, linked)"
        else:
            series_note = f"series={series_name} ({index_note}, unchanged)"
    else:
        series_note = "series=none"

    summary_note = "summary=empty" if not summary else "summary=written"
    tag_note = f"tags={tags}" if tags_updated else "tags=unchanged"
    if not shelf:
        shelf_note = "shelf=unset"
    elif moved:
        shelf_note = f"shelf={shelf} (moved)"
    else:
        shelf_note = f"shelf={shelf}"
    return (
        f"wrote: {final_label} "
        f"({summary_note}, {tag_note}, {shelf_note}, {series_note})"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files-dir", default="catalog/files")
    parser.add_argument("--catalog-dir", default="catalog")
    parser.add_argument(
        "--agent",
        choices=SUPPORTED_AGENTS,
        default="claude",
        help="Agent CLI to invoke for categorization (default: claude)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-file agent invocation timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--reshelve",
        action="store_true",
        help=(
            "Also re-pick a shelf for already-summarized files and move them "
            "into the chosen folder. Existing summaries and tags are left "
            "unchanged."
        ),
    )
    parser.add_argument(
        "--basename",
        action="append",
        default=[],
        help=(
            "Process only this catalog basename, without .md. May be repeated."
        ),
    )
    args = parser.parse_args()

    files_dir = Path(args.files_dir)
    catalog_dir = Path(args.catalog_dir)

    if not catalog_dir.is_dir():
        print(f"error: catalog directory not found: {catalog_dir}", file=sys.stderr)
        return 1
    if not files_dir.is_dir():
        print(f"error: files directory not found: {files_dir}", file=sys.stderr)
        return 1

    agent_bin = shutil.which(args.agent)
    if agent_bin is None:
        print(f"error: {args.agent} CLI not found on PATH", file=sys.stderr)
        return 1

    try:
        catalog_files = select_catalog_files(catalog_dir, args.basename)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not catalog_files:
        print("no catalog markdown files found")
        return 0

    existing_shelves = discover_existing_shelves(catalog_dir)
    existing_series = discover_series_notes(catalog_dir)

    exit_code = 0
    for catalog_path in catalog_files:
        relative_label = catalog_path.relative_to(catalog_dir).as_posix()
        try:
            message = process_catalog_file(
                catalog_path,
                files_dir,
                catalog_dir,
                existing_shelves,
                existing_series,
                args.agent,
                agent_bin,
                args.timeout,
                args.reshelve,
            )
            print(message)
            existing_shelves = discover_existing_shelves(catalog_dir)
        except subprocess.TimeoutExpired:
            print(f"error: timeout: {relative_label}", file=sys.stderr)
            exit_code = 1
        except Exception as exc:
            print(f"error: {relative_label}: {exc}", file=sys.stderr)
            exit_code = 1

    for series_name, series in discover_series_notes(catalog_dir).items():
        members = find_series_members(catalog_dir, series_name)
        member_titles = [path.stem for path, _ in members]
        try:
            changed = rebuild_volumes_section(series["path"], member_titles)
        except Exception as exc:
            print(f"error: series {series_name}: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        relative = series["path"].relative_to(catalog_dir).as_posix()
        if changed:
            print(f"series: {relative} (volumes={len(member_titles)})")
        else:
            print(f"series: {relative} (volumes={len(member_titles)}, unchanged)")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
