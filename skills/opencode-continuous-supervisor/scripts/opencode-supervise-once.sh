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

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [session_name] [prompt_file] [state_dir]" >&2
  exit 2
fi

if [ -z "$SESSION_NAME" ]; then
  SESSION_NAME=$(python3 "$REGISTRY_PY" "$STATE_DIR" ensure "$PROJECT_DIR" | python3 -c 'import json,sys; print(json.load(sys.stdin)["entry"]["session_name"])')
else
  python3 "$REGISTRY_PY" "$STATE_DIR" set "$PROJECT_DIR" "$SESSION_NAME" >/dev/null
fi

WATCH_JSON=$(python3 "$(dirname "$0")/opencode-watchdog.py" "$PROJECT_DIR" "$SESSION_NAME" "$STATE_DIR")
ACCEPT_JSON=""
ACCEPTED="unknown"
if [ -n "$CRITERIA_FILE" ] && [ -f "$CRITERIA_FILE" ]; then
  ACCEPT_JSON=$(python3 "$ACCEPT_PY" "$PROJECT_DIR" "$CRITERIA_FILE")
  ACCEPTED=$(printf '%s' "$ACCEPT_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("accepted") else "false")')
fi

python3 - <<'PY' "$WATCH_JSON" "$ACCEPT_JSON"
import json, sys
watch = json.loads(sys.argv[1])
out = {"watchdog": watch}
if sys.argv[2]:
    out["acceptance"] = json.loads(sys.argv[2])
print(json.dumps(out, ensure_ascii=False, indent=2))
PY

DECISION=$(printf '%s' "$WATCH_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("decision","error"))')

if [ "$ACCEPTED" = "true" ]; then
  exit 0
fi

if [ "$DECISION" = "ok" ]; then
  exit 0
fi

if [ -n "$PROMPT_FILE" ] && [ -f "$PROMPT_FILE" ]; then
  PROMPT_TEXT=$(cat "$PROMPT_FILE")
else
  PROMPT_TEXT=$(cat "$DEFAULT_PROMPT_FILE")
fi

bash "$(dirname "$0")/opencode-sessionctl.sh" prompt "$PROJECT_DIR" "$PROMPT_TEXT" "$SESSION_NAME"
