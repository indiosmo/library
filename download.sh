#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $(basename "$0") [--agent claude|codex] <url>" >&2
}

agent=claude
positional=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for --agent" >&2
                usage
                exit 1
            fi
            agent=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            positional+=("$@")
            break
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
        *)
            positional+=("$1")
            shift
            ;;
    esac
done

case $agent in
    claude|codex) ;;
    *)
        echo "Invalid --agent: $agent (expected claude or codex)" >&2
        usage
        exit 1
        ;;
esac

if [[ ${#positional[@]} -ne 1 ]]; then
    usage
    exit 1
fi

url=${positional[0]}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
catalog_dir="$script_dir/catalog"
output_dir="$catalog_dir/files"
env_file="$script_dir/.env"

proxy_args=()
if [[ -f "$env_file" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
fi

if [[ -n "${PROXY_URL:-}" ]]; then
    proxy_args=(--proxy "$PROXY_URL")
fi

mkdir -p "$output_dir"

downloaded_paths_file=$(mktemp)
cleanup() {
    rm -f -- "$downloaded_paths_file"
}
trap cleanup EXIT

cmd=(yt-dlp -v --write-subs --write-auto-subs --write-description --write-url --write-info-json --embed-chapters --replace-in-metadata title ":" "-" --print-to-file "after_move:%(filepath)s" "$downloaded_paths_file" -o "%(title)s.%(ext)s" "${proxy_args[@]}" -P "$output_dir" "$url")
printf '+'
printf ' %q' "${cmd[@]}"
printf '\n'
"${cmd[@]}"

downloaded_basenames=()
while IFS= read -r downloaded_path; do
    [[ -n "$downloaded_path" ]] || continue
    filename=$(basename -- "$downloaded_path")
    basename=${filename%.*}
    downloaded_basenames+=("$basename")
done < "$downloaded_paths_file"

if [[ ${#downloaded_basenames[@]} -eq 0 ]]; then
    echo "No downloaded files reported by yt-dlp; skipping catalog and categorize passes."
    exit 0
fi

basename_args=()
for basename in "${downloaded_basenames[@]}"; do
    basename_args+=(--basename "$basename")
done

generate_cmd=(uv run python "$script_dir/scripts/catalog_videos.py" --files-dir "$output_dir" --catalog-dir "$catalog_dir" "${basename_args[@]}")
printf '+'
printf ' %q' "${generate_cmd[@]}"
printf '\n'
"${generate_cmd[@]}"

categorize_cmd=(uv run python "$script_dir/scripts/categorize.py" --files-dir "$output_dir" --catalog-dir "$catalog_dir" --agent "$agent" "${basename_args[@]}")
printf '+'
printf ' %q' "${categorize_cmd[@]}"
printf '\n'
"${categorize_cmd[@]}"
