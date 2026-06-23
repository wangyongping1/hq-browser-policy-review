#!/usr/bin/env bash
set -euo pipefail

COMPOSE_DIR="${CHROME_COMPOSE_DIR:-/mnt/c/myfile/A-huaqing/github-code/agentos-mvp-1/apps/chrome}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d /opt/data/workspace ]; then
  echo "[1/4] Runtime"
  echo "Inside Hermes container"

  echo
  echo "[2/4] hq-browser"
  sh -lc '
if command -v hq-browser >/dev/null 2>&1; then
  command -v hq-browser
elif [ -x /opt/data/.local/bin/hq-browser ]; then
  echo /opt/data/.local/bin/hq-browser
else
  echo "hq-browser missing" >&2
  exit 1
fi
printf "CDP config: "
sed -n "1p" /opt/data/.config/hq-browser/cdp-url 2>/dev/null | sed "s/token=.*/token=<redacted>/" || true
'

  echo
  echo "[3/4] Current URL"
  sh -lc '
BROWSER="$(command -v hq-browser 2>/dev/null || echo /opt/data/.local/bin/hq-browser)"
"$BROWSER" get url || true
'
else
  cd "$COMPOSE_DIR"

  echo "[1/4] Compose services"
  docker compose ps hermes relay

  echo
  echo "[2/4] hq-browser"
  docker compose exec -T hermes sh -lc '
if command -v hq-browser >/dev/null 2>&1; then
  command -v hq-browser
elif [ -x /opt/data/.local/bin/hq-browser ]; then
  echo /opt/data/.local/bin/hq-browser
else
  echo "hq-browser missing" >&2
  exit 1
fi
printf "CDP config: "
sed -n "1p" /opt/data/.config/hq-browser/cdp-url 2>/dev/null | sed "s/token=.*/token=<redacted>/" || true
'

  echo
  echo "[3/4] Current URL"
  docker compose exec -T hermes sh -lc '
BROWSER="$(command -v hq-browser 2>/dev/null || echo /opt/data/.local/bin/hq-browser)"
"$BROWSER" get url || true
'
fi

echo
echo "[4/4] Available videos"
"$SCRIPT_DIR/list-xhs-videos.sh"
