#!/usr/bin/env bash
set -euo pipefail

scripts_dir="${1:?Usage: entrypoint.sh <scripts_dir>}"

shopt -s nullglob
scripts=("$scripts_dir"/*.ssc)
if [ ${#scripts[@]} -eq 0 ]; then
    echo "No .ssc scripts found in $scripts_dir" >&2
    exit 1
fi

for script in "${scripts[@]}"; do
    echo "Rendering $(basename "$script")..."
    xvfb-run -a --server-args="-screen 0 1280x800x24" stellarium --startup-script "$script"
done
