#!/bin/bash
set -euo pipefail

PROJECT_DIR="${1:-}"
SESSION_NAME="${2:-}"
PROMPT_FILE="${3:-}"
STATE_DIR="${4:-$HOME/.openclaw/workspace/state/opencode-supervisor}"
CRITERIA_FILE="${5:-}"
DEFAULT_PROMPT_FILE="$(dirname "$0")/../assets/default-continue-prompt.txt"
REGISTRY_PY="$(dirname "$0")/opencode-session-registry.py"
ACCEPT_PY="$(dirname "$0")/opencode-acceptance-check.py"
WATCH_PY="$(dirname "$0")/opencode-watchdog.py"
DECIDE_PY="$(dirname "$0")/opencode-unified-decider.py"
TMPDIR="${TMPDIR:-/tmp}"
WATCH_FILE=$(mktemp "$TMPDIR/opencode-watch-XXXXXX.json")
ACCEPT_FILE=$(mktemp "$TMPDIR/opencode-accept-XXXXXX.json")
COMBINED_FILE=$(mktemp "$TMPDIR/opencode-combined-XXXXXX.json")

cleanup() { rm -f "$WATCH_FILE" "$ACCEPT_FILE" "$COMBINED_FILE" 2>/dev/null; }
trap cleanup EXIT

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [session_name] [prompt_file] [state_dir] [criteria_file]" >&2
  exit 2
fi

# Resolve session name via registry
if [ -z "$SESSION_NAME" ]; then
  SESSION_NAME=$(python3 "$REGISTRY_PY" "$STATE_DIR" ensure "$PROJECT_DIR" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["entry"]["session_name"])')
else
  python3 "$REGISTRY_PY" "$STATE_DIR" set "$PROJECT_DIR" "$SESSION_NAME" >/dev/null
fi

# Run watchdog → write to watch file
python3 "$WATCH_PY" "$PROJECT_DIR" "$SESSION_NAME" "$STATE_DIR" > "$WATCH_FILE"

# Run acceptance check if criteria file provided
if [ -n "$CRITERIA_FILE" ] && [ -f "$CRITERIA_FILE" ]; then
  python3 "$ACCEPT_PY" "$PROJECT_DIR" "$CRITERIA_FILE" > "$ACCEPT_FILE"
fi

# Merge: read watch + optionally accept → combined file
python3 - <<'PY' "$WATCH_FILE" "$ACCEPT_FILE" > "$COMBINED_FILE"
import json, sys
wpath = sys.argv[1]
apath = sys.argv[2] if len(sys.argv) > 2 else None
watch = json.loads(open(wpath).read())
out = {"watchdog": watch}
if apath and open(apath).read().strip():
    try:
        out["acceptance"] = json.loads(open(apath).read())
    except Exception:
        pass
print(json.dumps(out, ensure_ascii=False, indent=2))
PY

cat "$COMBINED_FILE"

# Run unified decider
DECISION=$(python3 "$DECIDE_PY" "$COMBINED_FILE")
echo "decider: $DECISION"
ACTION=$(printf '%s' "$DECISION" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("action","error"))')
REASON=$(printf '%s' "$DECISION" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("reason",""))')

echo "[supervise-once] action=$ACTION reason=$REASON"

if [ "$ACTION" = "stop" ] || [ "$ACTION" = "wait" ]; then
  echo "[supervise-once] action=$ACTION; no prompt sent"
  exit 0
fi

# Determine prompt text
if [ -n "$PROMPT_FILE" ] && [ -f "$PROMPT_FILE" ]; then
  PROMPT_TEXT=$(cat "$PROMPT_FILE")
else
  PROMPT_TEXT=$(cat "$DEFAULT_PROMPT_FILE")
fi

bash "$(dirname "$0")/opencode-sessionctl.sh" prompt "$PROJECT_DIR" "$PROMPT_TEXT" "$SESSION_NAME"