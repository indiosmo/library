#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
catalog_dir="$script_dir/catalog"
files_dir="$catalog_dir/files"

usage() {
    cat <<EOF
Usage: $(basename "$0") [--full-refresh] [--agent claude|codex]

Catalog every item under catalog/files/ by running the video, document,
and categorize passes in sequence.

Options:
  --full-refresh   Delete all shelves and root markdown stubs under
                   catalog/ before cataloging. catalog/files/ is kept,
                   along with dotfile entries such as .obsidian/,
                   .claude/, and .gitignore.
  --agent NAME     Agent CLI to use for the categorize pass: claude or
                   codex (default: claude).
  -h, --help       Show this message.
EOF
}

full_refresh=false
agent=claude
while [[ $# -gt 0 ]]; do
    case $1 in
        --full-refresh)
            full_refresh=true
            shift
            ;;
        --agent)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for --agent" >&2
                usage >&2
                exit 1
            fi
            agent=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

case $agent in
    claude|codex) ;;
    *)
        echo "Invalid --agent: $agent (expected claude or codex)" >&2
        usage >&2
        exit 1
        ;;
esac

if [[ ! -d "$files_dir" ]]; then
    echo "Files directory not found: $files_dir" >&2
    exit 1
fi

run() {
    printf '+'
    printf ' %q' "$@"
    printf '\n'
    "$@"
}

if [[ "$full_refresh" == "true" ]]; then
    echo "Full refresh: clearing $catalog_dir (keeping files/ and dotfile entries)"
    for entry in "$catalog_dir"/*; do
        [[ -e "$entry" ]] || continue
        name=$(basename "$entry")
        if [[ "$name" == "files" ]]; then
            continue
        fi
        rm -rf -- "$entry"
        echo "  removed: $name"
    done
fi

run uv run python "$script_dir/scripts/catalog_videos.py" \
    --files-dir "$files_dir" --catalog-dir "$catalog_dir"

run uv run python "$script_dir/scripts/catalog_documents.py" \
    --files-dir "$files_dir" --catalog-dir "$catalog_dir"

run uv run python "$script_dir/scripts/categorize.py" \
    --files-dir "$files_dir" --catalog-dir "$catalog_dir" \
    --agent "$agent"
