#!/usr/bin/env bash
set -euo pipefail

COMPOSE_DIR="${CHROME_COMPOSE_DIR:-/mnt/c/myfile/A-huaqing/github-code/agentos-mvp-1/apps/chrome}"

list_local='
set -eu
echo "Images:"
find /opt/data/workspace/image -maxdepth 2 -type f \( \
  -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \
\) -printf "%T@ %p\n" 2>/dev/null | sort -nr | cut -d" " -f2- | sed -n "1,40p" || true

echo
echo "Videos:"
find /opt/data/workspace/video /opt/data/workspace/videos -maxdepth 2 -type f \( \
  -iname "*.mp4" -o -iname "*.mov" -o -iname "*.m4v" -o -iname "*.webm" \
\) -printf "%T@ %p\n" 2>/dev/null | sort -nr | cut -d" " -f2- | sed -n "1,40p" || true
'

if [ -d /opt/data/workspace ]; then
  sh -lc "$list_local"
else
  cd "$COMPOSE_DIR"
  docker compose exec -T hermes sh -lc "$list_local"
fi
