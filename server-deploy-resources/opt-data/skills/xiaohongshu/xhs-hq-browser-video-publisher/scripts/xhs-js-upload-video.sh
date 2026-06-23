#!/usr/bin/env bash
set -euo pipefail

COMPOSE_DIR="${CHROME_COMPOSE_DIR:-/mnt/c/myfile/A-huaqing/github-code/agentos-mvp-1/apps/chrome}"
VIDEO_PATH="${1:-}"

if [ -z "$VIDEO_PATH" ]; then
  if [ -d /opt/data/workspace ]; then
    VIDEO_PATH="$(
      sh -lc '
        find /opt/data/workspace/videos /opt/data/workspace/video -maxdepth 2 -type f \( \
          -iname "*.mp4" -o -iname "*.mov" -o -iname "*.m4v" -o -iname "*.webm" \
        \) -printf "%T@ %p\n" 2>/dev/null | sort -nr | cut -d" " -f2- | sed -n "1p"
      ' | tr -d "\r"
    )"
  else
    cd "$COMPOSE_DIR"
    VIDEO_PATH="$(
      docker compose exec -T hermes sh -lc '
      find /opt/data/workspace/videos /opt/data/workspace/video -maxdepth 2 -type f \( \
        -iname "*.mp4" -o -iname "*.mov" -o -iname "*.m4v" -o -iname "*.webm" \
      \) -printf "%T@ %p\n" 2>/dev/null | sort -nr | cut -d" " -f2- | sed -n "1p"
      ' | tr -d "\r"
    )"
  fi
fi

if [ -z "$VIDEO_PATH" ]; then
  echo "No video file found under /opt/data/workspace/videos or /opt/data/workspace/video" >&2
  exit 2
fi

case "$VIDEO_PATH" in
  *.mp4) MIME_TYPE="video/mp4" ;;
  *.mov) MIME_TYPE="video/quicktime" ;;
  *.m4v) MIME_TYPE="video/x-m4v" ;;
  *.webm) MIME_TYPE="video/webm" ;;
  *) MIME_TYPE="application/octet-stream" ;;
esac

upload_local='
set -eu
BROWSER="$(command -v hq-browser 2>/dev/null || echo /opt/data/.local/bin/hq-browser)"
test -f "$XHS_UPLOAD_FILE"

if base64 --help 2>/dev/null | grep -q -- "-w"; then
  base64 -w 0 "$XHS_UPLOAD_FILE" > /tmp/xhs-video-upload.b64
else
  base64 "$XHS_UPLOAD_FILE" | tr -d "\n" > /tmp/xhs-video-upload.b64
fi

name="$(basename "$XHS_UPLOAD_FILE")"
cat > /tmp/xhs-video-upload.js <<EOF
(async function() {
  const b64 = "$(cat /tmp/xhs-video-upload.b64)";
  const mime = "$XHS_UPLOAD_MIME";
  const name = "$name";
  const input = document.querySelector("input[type=file]");
  if (!input) {
    return JSON.stringify({ success: false, error: "input[type=file] not found" });
  }
  const resp = await fetch("data:" + mime + ";base64," + b64);
  const blob = await resp.blob();
  const file = new File([blob], name, { type: mime });
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new Event("change", { bubbles: true }));
  return JSON.stringify({
    success: true,
    name: file.name,
    type: file.type,
    size: file.size,
    inputAccept: input.getAttribute("accept") || ""
  });
})()
EOF

"$BROWSER" eval --stdin < /tmp/xhs-video-upload.js
'

if [ -d /opt/data/workspace ]; then
  XHS_UPLOAD_FILE="$VIDEO_PATH" XHS_UPLOAD_MIME="$MIME_TYPE" sh -lc "$upload_local"
else
  cd "$COMPOSE_DIR"
  docker compose exec -T \
    -e XHS_UPLOAD_FILE="$VIDEO_PATH" \
    -e XHS_UPLOAD_MIME="$MIME_TYPE" \
    hermes sh -lc "$upload_local"
fi
