#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
files_dir="$script_dir/catalog/files"
bucket="s3://indiosmo.library"
profile="library"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <push|pull> [aws s3 sync args...]" >&2
    exit 2
fi

direction="$1"
shift

case "$direction" in
    push)
        if [[ ! -d "$files_dir" ]]; then
            echo "Files directory not found: $files_dir" >&2
            exit 1
        fi
        source="$files_dir"
        destination="$bucket"
        ;;
    pull)
        mkdir -p "$files_dir"
        source="$bucket"
        destination="$files_dir"
        ;;
    *)
        echo "Unknown direction: $direction (expected push or pull)" >&2
        exit 2
        ;;
esac

cmd=(aws --profile "$profile" s3 sync "$source" "$destination" "$@")
printf '+'
printf ' %q' "${cmd[@]}"
printf '\n'
"${cmd[@]}"
