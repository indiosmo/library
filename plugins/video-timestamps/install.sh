#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
project_root=$(cd -- "$script_dir/../.." &> /dev/null && pwd)
vault_dir="${1:-$project_root/catalog}"
target_dir="$vault_dir/.obsidian/plugins/video-timestamps"

if [[ ! -d "$vault_dir/.obsidian" ]]; then
    echo "Error: $vault_dir is not an Obsidian vault (.obsidian missing)" >&2
    exit 1
fi

mkdir -p "$target_dir"
cp "$script_dir/manifest.json" "$target_dir/"
cp "$script_dir/main.js" "$target_dir/"
cp "$script_dir/styles.css" "$target_dir/"

echo "Installed video-timestamps to $target_dir"
echo "In Obsidian: Settings -> Community plugins -> enable 'Video Timestamps'."
echo "If Restricted Mode is on, turn it off first."
