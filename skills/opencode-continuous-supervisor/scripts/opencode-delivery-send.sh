#!/bin/bash
# Send delivery summary / artifact via openclaw message send.
set -euo pipefail

DELIVERY_JSON="${1:-}"
CHANNEL="${OPENCODE_DELIVERY_CHANNEL:-telegram}"
ACCOUNT="${OPENCODE_DELIVERY_ACCOUNT:-}"
TARGET="${OPENCODE_DELIVERY_TARGET:-}"

if [ -z "$DELIVERY_JSON" ]; then
  echo '{"status":"error","error":"delivery json argument required"}'
  exit 2
fi
if [ -z "$ACCOUNT" ] || [ -z "$TARGET" ]; then
  echo '{"status":"error","error":"OPENCODE_DELIVERY_ACCOUNT and OPENCODE_DELIVERY_TARGET are required"}'
  exit 3
fi

TMP_JSON=$(mktemp)
cleanup() { rm -f "$TMP_JSON" 2>/dev/null; }
trap cleanup EXIT
printf '%s' "$DELIVERY_JSON" > "$TMP_JSON"

MESSAGE=$(python3 - <<'PY' "$TMP_JSON"
import json,sys
p=sys.argv[1]
d=json.load(open(p))
print(d.get('userSummary') or d.get('summary') or '任务已完成。')
PY
)

MEDIA=$(python3 - <<'PY' "$TMP_JSON"
import json,sys
p=sys.argv[1]
d=json.load(open(p))
arts=d.get('existingArtifacts') or []
print(arts[0]['path'] if arts else '')
PY
)

ALLOWED_MEDIA_DIRS=(
  "/root/.openclaw/media/outbound"
  "/root/.openclaw/media/inbound"
  "/root/.openclaw/media/tool-image-generation"
)

is_path_allowed() {
  local path="$1"
  for dir in "${ALLOWED_MEDIA_DIRS[@]}"; do
    if [[ "$path" == "$dir"* ]]; then
      return 0
    fi
  done
  return 1
}

ensure_media_in_allowed_dir() {
  local media_path="$1"
  if [ -z "$media_path" ] || [ ! -f "$media_path" ]; then
    echo "$media_path"
    return
  fi
  if is_path_allowed "$media_path"; then
    echo "$media_path"
    return
  fi
  local filename=$(basename "$media_path")
  local dest="/root/.openclaw/media/outbound/$filename"
  cp "$media_path" "$dest"
  echo "$dest"
}
MEDIA_PATH=$(ensure_media_in_allowed_dir "$MEDIA")

if [ -n "$MEDIA_PATH" ] && [ -f "$MEDIA_PATH" ]; then
  CMD=(openclaw message send --media "$MEDIA_PATH" --message "$MESSAGE" --channel "$CHANNEL" --account "$ACCOUNT" --target "$TARGET")
else
  CMD=(openclaw message send --message "$MESSAGE" --channel "$CHANNEL" --account "$ACCOUNT" --target "$TARGET")
fi

"${CMD[@]}" >/tmp/opencode-delivery-send.out 2>/tmp/opencode-delivery-send.err || {
  ERR=$(tr '\n' ' ' </tmp/opencode-delivery-send.err | sed 's/"/\\"/g')
  echo "{\"status\":\"error\",\"error\":\"$ERR\"}"
  exit 4
}

python3 - <<'PY' "$TMP_JSON" "$MEDIA_PATH"
import json,sys
p=sys.argv[1]
media=sys.argv[2]
d=json.load(open(p))
print(json.dumps({
  'status':'ok',
  'sentMedia': bool(media),
  'mediaPath': media or None,
  'criteria': d.get('criteria'),
  'accepted': d.get('accepted'),
  'deliveryReady': d.get('deliveryReady'),
}, ensure_ascii=False))
PY
