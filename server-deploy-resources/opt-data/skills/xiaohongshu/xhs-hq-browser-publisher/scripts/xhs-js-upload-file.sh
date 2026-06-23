#!/usr/bin/env bash
set -euo pipefail

COMPOSE_DIR="${CHROME_COMPOSE_DIR:-/mnt/c/myfile/A-huaqing/github-code/agentos-mvp-1/apps/chrome}"
FILE_PATH="${1:?usage: xhs-js-upload-file.sh /opt/data/workspace/image/test1.png [mime-type]}"
MIME_TYPE="${2:-}"

case "$FILE_PATH" in
  *.jpg|*.jpeg) MIME_TYPE="${MIME_TYPE:-image/jpeg}" ;;
  *.png) MIME_TYPE="${MIME_TYPE:-image/png}" ;;
  *.webp) MIME_TYPE="${MIME_TYPE:-image/webp}" ;;
  *.mp4) MIME_TYPE="${MIME_TYPE:-video/mp4}" ;;
  *.mov) MIME_TYPE="${MIME_TYPE:-video/quicktime}" ;;
  *.m4v) MIME_TYPE="${MIME_TYPE:-video/x-m4v}" ;;
  *.webm) MIME_TYPE="${MIME_TYPE:-video/webm}" ;;
  *) MIME_TYPE="${MIME_TYPE:-application/octet-stream}" ;;
esac

upload_local='
set -eu
BROWSER="$(command -v hq-browser 2>/dev/null || echo /opt/data/.local/bin/hq-browser)"
test -f "$XHS_UPLOAD_FILE"

if base64 --help 2>/dev/null | grep -q -- "-w"; then
  base64 -w 0 "$XHS_UPLOAD_FILE" > /tmp/xhs-upload.b64
else
  base64 "$XHS_UPLOAD_FILE" | tr -d "\n" > /tmp/xhs-upload.b64
fi

name="$(basename "$XHS_UPLOAD_FILE")"
cat > /tmp/xhs-upload-file.js <<EOF
(async function() {
  const b64 = "$(cat /tmp/xhs-upload.b64)";
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

"$BROWSER" eval --stdin < /tmp/xhs-upload-file.js
'

if [ -d /opt/data/workspace ]; then
  XHS_UPLOAD_FILE="$FILE_PATH" XHS_UPLOAD_MIME="$MIME_TYPE" sh -lc "$upload_local"
else
  cd "$COMPOSE_DIR"
  docker compose exec -T \
    -e XHS_UPLOAD_FILE="$FILE_PATH" \
    -e XHS_UPLOAD_MIME="$MIME_TYPE" \
    hermes sh -lc "$upload_local"
fi
