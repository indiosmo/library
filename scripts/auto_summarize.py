#!/usr/bin/env python3
"""Populate catalog markdown files with an Auto Summary section and tags via claude -p.

Scans catalog markdown files (recursively) and, for any file that does not
already contain a `## Auto Summary` section, calls `claude -p` with the
corresponding video's metadata and:

  - Inserts an `## Auto Summary` section that adds context beyond the
    uploader's description (the description itself lives in its own
    `## Description` section). The body may be empty when there is nothing
    meaningful to add.
  - Writes topical tags into the `tags:` frontmatter list (only if the list
    is currently empty, so manual edits are preserved).
  - Files the markdown into a category subfolder of the catalog root, picked
    by the agent (max depth 2, e.g. `science/astronomy`).

The agent is allowed to use WebSearch and WebFetch to research the speaker,
event, or topic so the summary can include genuinely new information.

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
from pathlib import Path

INFO_SUFFIX = ".info.json"
AUTO_SUMMARY_HEADING = "## Auto Summary"
DESCRIPTION_HEADING = "## Description"
CHAPTERS_HEADING = "## Chapters"
DESCRIPTION_CHAR_LIMIT = 8000
ALLOWED_TOOLS = "WebSearch,WebFetch"
RESERVED_CATALOG_DIRS = {"media", ".obsidian", ".trash"}
INDEX_FILENAMES = {"index.md"}
CATEGORY_SEGMENT_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*")
MAX_CATEGORY_DEPTH = 2

CATEGORY_ONLY_PROMPT_TEMPLATE = """You are filing an already-summarized video for a personal research library.

Pick the most appropriate `category` slug for this video. Use 1 segment for a
broad area or 2 segments separated by `/` for a subcategory. Maximum depth is
2. Lowercase letters, digits, and hyphens only; no spaces. Examples:
`science`, `science/astronomy`, `computer/programming`, `philosophy`. If the
video clearly fits one of the existing categories listed below, reuse it
verbatim. If it spans multiple fields, pick the predominant one. If a depth-1
category fits well and no existing depth-2 subcategory matches, use the
depth-1 form rather than inventing a new subcategory.

Existing categories in this catalog (reuse when applicable):
{existing_categories}

Respond with a single JSON object and nothing else:
{{"category": "science/astronomy"}}

Title: {title}
Source: {source}

Description (from uploader):
{description}

Chapters:
{chapters}
"""

PROMPT_TEMPLATE = """You are categorizing a video for a personal research library.

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
2. Between 3 and 7 lowercase topical `tags` identifying broad subject areas
   (examples: biology, physics, computer-science, philosophy, mathematics,
   history, neuroscience, economics). Use single words or hyphenated phrases.
   Prefer broad disciplinary tags over narrow ones.
3. A `category` slug used to file this note. Use 1 segment for a broad area
   or 2 segments separated by `/` for a subcategory. Maximum depth is 2.
   Lowercase letters, digits, and hyphens only; no spaces. Examples:
   `science`, `science/astronomy`, `science/biology`,
   `computer/programming`, `computer/databases`, `computer/ai`,
   `philosophy`, `history`. If the video clearly fits one of the existing
   categories listed below, reuse it verbatim. If a video spans multiple
   fields, pick the predominant one as the category and use `tags` for the
   others. If a depth-1 category fits well and no existing depth-2
   subcategory matches, use the depth-1 form rather than inventing a new
   subcategory.

Existing categories in this catalog (reuse when applicable):
{existing_categories}

Respond with a single JSON object and nothing else, in this exact shape:
{{"summary": "...", "tags": ["tag1", "tag2"], "category": "science/astronomy"}}

Title: {title}
Source: {source}

Description (from uploader):
{description}

Chapters:
{chapters}
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


def _prompt_fields(info: dict, existing_categories: list[str]) -> dict:
    title = info.get("title") or info.get("fulltitle") or "(unknown)"
    source = info.get("webpage_url") or info.get("original_url") or "(unknown)"
    description = (info.get("description") or "").strip() or "(none)"
    if len(description) > DESCRIPTION_CHAR_LIMIT:
        description = description[:DESCRIPTION_CHAR_LIMIT] + "\n[truncated]"
    chapters = format_chapters_for_prompt(info.get("chapters"))
    if existing_categories:
        category_list = "\n".join(f"- {category}" for category in existing_categories)
    else:
        category_list = "(none yet)"
    return {
        "title": title,
        "source": source,
        "description": description,
        "chapters": chapters,
        "existing_categories": category_list,
    }


def build_prompt(info: dict, existing_categories: list[str]) -> str:
    return PROMPT_TEMPLATE.format(**_prompt_fields(info, existing_categories))


def build_category_only_prompt(info: dict, existing_categories: list[str]) -> str:
    return CATEGORY_ONLY_PROMPT_TEMPLATE.format(
        **_prompt_fields(info, existing_categories)
    )


def call_claude(prompt: str, claude_bin: str, timeout: int) -> str:
    result = subprocess.run(
        [claude_bin, "-p", "--allowedTools", ALLOWED_TOOLS],
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


def find_info_for_catalog(catalog_path: Path, media_dir: Path) -> Path | None:
    candidate = media_dir / f"{catalog_path.stem}{INFO_SUFFIX}"
    if candidate.exists():
        return candidate
    return None


def is_reserved_dir_name(name: str) -> bool:
    return name.startswith(".") or name in RESERVED_CATALOG_DIRS


def discover_existing_categories(catalog_dir: Path) -> list[str]:
    categories: list[str] = []
    for top in sorted(catalog_dir.iterdir()):
        if not top.is_dir() or is_reserved_dir_name(top.name):
            continue
        categories.append(top.name)
        for nested in sorted(top.iterdir()):
            if not nested.is_dir() or is_reserved_dir_name(nested.name):
                continue
            categories.append(f"{top.name}/{nested.name}")
    return categories


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


def normalize_category(raw) -> str:
    if not isinstance(raw, str):
        return ""
    cleaned = raw.strip().strip("/").lower().replace("\\", "/")
    if not cleaned:
        return ""
    segments = [seg.strip().replace(" ", "-") for seg in cleaned.split("/")]
    segments = [seg for seg in segments if seg]
    if not segments:
        return ""
    segments = segments[:MAX_CATEGORY_DEPTH]
    if not all(CATEGORY_SEGMENT_PATTERN.fullmatch(seg) for seg in segments):
        return ""
    if segments[0] in RESERVED_CATALOG_DIRS:
        return ""
    return "/".join(segments)


def move_to_category(
    catalog_path: Path, catalog_dir: Path, category: str
) -> tuple[Path, bool]:
    if not category:
        return catalog_path, False
    target_dir = catalog_dir / category
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
    media_dir: Path,
    catalog_dir: Path,
    existing_categories: list[str],
    claude_bin: str,
    timeout: int,
    recategorize: bool,
) -> str:
    text = catalog_path.read_text(encoding="utf-8")
    relative_label = catalog_path.relative_to(catalog_dir).as_posix()
    has_summary = AUTO_SUMMARY_HEADING in text

    info_path = find_info_for_catalog(catalog_path, media_dir)
    if info_path is None:
        return f"skip (no info.json): {relative_label}"

    info = load_info(info_path)

    if has_summary and not recategorize:
        return f"skip (already summarized): {relative_label}"

    if has_summary and recategorize:
        prompt = build_category_only_prompt(info, existing_categories)
        raw_response = call_claude(prompt, claude_bin, timeout)
        parsed = extract_json_object(raw_response)
        category = normalize_category(parsed.get("category"))

        final_path, moved = move_to_category(catalog_path, catalog_dir, category)
        final_label = final_path.relative_to(catalog_dir).as_posix()

        if not category:
            return f"recategorize: {final_label} (category=unset)"
        if moved:
            return f"recategorize: {final_label} (category={category}, moved)"
        return f"recategorize: {final_label} (category={category}, unchanged)"

    prompt = build_prompt(info, existing_categories)
    raw_response = call_claude(prompt, claude_bin, timeout)
    parsed = extract_json_object(raw_response)

    raw_summary = parsed.get("summary")
    summary = (raw_summary or "").strip() if isinstance(raw_summary, str) else ""
    tags = normalize_tags(parsed.get("tags"))
    category = normalize_category(parsed.get("category"))

    frontmatter, body = split_frontmatter(text)
    frontmatter, tags_updated = update_tags_in_frontmatter(frontmatter, tags)
    body = insert_auto_summary(body, summary)
    catalog_path.write_text(frontmatter + body, encoding="utf-8")

    final_path, moved = move_to_category(catalog_path, catalog_dir, category)
    final_label = final_path.relative_to(catalog_dir).as_posix()

    summary_note = "summary=empty" if not summary else "summary=written"
    tag_note = f"tags={tags}" if tags_updated else "tags=unchanged"
    if not category:
        category_note = "category=unset"
    elif moved:
        category_note = f"category={category} (moved)"
    else:
        category_note = f"category={category}"
    return f"wrote: {final_label} ({summary_note}, {tag_note}, {category_note})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media-dir", default="catalog/media")
    parser.add_argument("--catalog-dir", default="catalog")
    parser.add_argument(
        "--claude-bin",
        default="claude",
        help="Path to the claude CLI (default: claude)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Per-file claude invocation timeout in seconds (default: 180)",
    )
    parser.add_argument(
        "--recategorize",
        action="store_true",
        help=(
            "Also re-pick a category for already-summarized files and move them "
            "into the chosen subfolder. Existing summaries and tags are left "
            "unchanged."
        ),
    )
    args = parser.parse_args()

    media_dir = Path(args.media_dir)
    catalog_dir = Path(args.catalog_dir)

    if not catalog_dir.is_dir():
        print(f"error: catalog directory not found: {catalog_dir}", file=sys.stderr)
        return 1
    if not media_dir.is_dir():
        print(f"error: media directory not found: {media_dir}", file=sys.stderr)
        return 1

    claude_bin = shutil.which(args.claude_bin) or args.claude_bin
    if not Path(claude_bin).exists() and shutil.which(args.claude_bin) is None:
        print(f"error: claude CLI not found: {args.claude_bin}", file=sys.stderr)
        return 1

    catalog_files = discover_catalog_files(catalog_dir)
    if not catalog_files:
        print("no catalog markdown files found")
        return 0

    existing_categories = discover_existing_categories(catalog_dir)

    exit_code = 0
    for catalog_path in catalog_files:
        relative_label = catalog_path.relative_to(catalog_dir).as_posix()
        try:
            message = process_catalog_file(
                catalog_path,
                media_dir,
                catalog_dir,
                existing_categories,
                claude_bin,
                args.timeout,
                args.recategorize,
            )
            print(message)
            existing_categories = discover_existing_categories(catalog_dir)
        except subprocess.TimeoutExpired:
            print(f"error: timeout: {relative_label}", file=sys.stderr)
            exit_code = 1
        except Exception as exc:
            print(f"error: {relative_label}: {exc}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
