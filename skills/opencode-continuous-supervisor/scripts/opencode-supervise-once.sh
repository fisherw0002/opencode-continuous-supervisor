#!/bin/bash
set -euo pipefail

PROJECT_DIR="${1:-}"
SESSION_NAME="${2:-oc-opencode-default}"
PROMPT_FILE="${3:-}"
STATE_DIR="${4:-$HOME/.openclaw/workspace/state/opencode-supervisor}"
DEFAULT_PROMPT_FILE="$(dirname "$0")/../assets/default-continue-prompt.txt"

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [session_name] [prompt_file] [state_dir]" >&2
  exit 2
fi

WATCH_JSON=$(python3 "$(dirname "$0")/opencode-watchdog.py" "$PROJECT_DIR" "$SESSION_NAME" "$STATE_DIR")
echo "$WATCH_JSON"
DECISION=$(printf '%s' "$WATCH_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("decision","error"))')

if [ "$DECISION" = "ok" ]; then
  exit 0
fi

if [ -n "$PROMPT_FILE" ] && [ -f "$PROMPT_FILE" ]; then
  PROMPT_TEXT=$(cat "$PROMPT_FILE")
else
  PROMPT_TEXT=$(cat "$DEFAULT_PROMPT_FILE")
fi

bash "$(dirname "$0")/opencode-sessionctl.sh" prompt "$PROJECT_DIR" "$PROMPT_TEXT" "$SESSION_NAME"
