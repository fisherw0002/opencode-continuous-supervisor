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

if [ -n "$MEDIA" ] && [ -f "$MEDIA" ]; then
  CMD=(openclaw message send --media "$MEDIA" --message "$MESSAGE" --channel "$CHANNEL" --account "$ACCOUNT" --target "$TARGET")
else
  CMD=(openclaw message send --message "$MESSAGE" --channel "$CHANNEL" --account "$ACCOUNT" --target "$TARGET")
fi

"${CMD[@]}" >/tmp/opencode-delivery-send.out 2>/tmp/opencode-delivery-send.err || {
  ERR=$(tr '\n' ' ' </tmp/opencode-delivery-send.err | sed 's/"/\\"/g')
  echo "{\"status\":\"error\",\"error\":\"$ERR\"}"
  exit 4
}

python3 - <<'PY' "$TMP_JSON" "$MEDIA"
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
