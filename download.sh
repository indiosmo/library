#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <url>" >&2
    exit 1
fi

url=$1
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
catalog_dir="$script_dir/catalog"
output_dir="$catalog_dir/media"
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

cmd=(yt-dlp -v --write-subs --write-auto-subs --write-description --write-url --write-info-json --embed-chapters --replace-in-metadata title ":" "-" -o "%(title)s.%(ext)s" "${proxy_args[@]}" -P "$output_dir" "$url")
printf '+'
printf ' %q' "${cmd[@]}"
printf '\n'
"${cmd[@]}"

generate_cmd=(uv run python "$script_dir/scripts/generate_catalog.py" --media-dir "$output_dir" --catalog-dir "$catalog_dir")
printf '+'
printf ' %q' "${generate_cmd[@]}"
printf '\n'
"${generate_cmd[@]}"

summarize_cmd=(uv run python "$script_dir/scripts/auto_summarize.py" --media-dir "$output_dir" --catalog-dir "$catalog_dir")
printf '+'
printf ' %q' "${summarize_cmd[@]}"
printf '\n'
"${summarize_cmd[@]}"
