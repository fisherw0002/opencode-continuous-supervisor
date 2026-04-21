#!/bin/bash
set -euo pipefail

PROJECT_DIR="${1:-}"
SESSION_NAME="${2:-}"
PROMPT_FILE="${3:-}"
STATE_DIR="${4:-$HOME/.openclaw/workspace/state/opencode-supervisor}"
CRITERIA_FILE="${5:-}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-120}"
MAX_CYCLES="${MAX_CYCLES:-0}"
ONCE_SH="$(dirname "$0")/opencode-supervise-once.sh"

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [session_name] [prompt_file] [state_dir] [criteria_file]" >&2
  exit 2
fi

cycle=0
while true; do
  cycle=$((cycle+1))
  echo "[supervise-loop] cycle=$cycle project=$PROJECT_DIR"

  OUT=$(bash "$ONCE_SH" "$PROJECT_DIR" "$SESSION_NAME" "$PROMPT_FILE" "$STATE_DIR" "$CRITERIA_FILE")
  # Extract action from decider output
  ACTION=$(printf '%s' "$OUT" | python3 - <<'PY'
import json, sys
d = json.load(sys.stdin)
dec = d.get("decider", {})
print(dec.get("action", "unknown") if isinstance(dec, dict) else "unknown")
PY)

  if [ "$ACTION" = "stop" ]; then
    echo "[supervise-loop] action=stop; acceptance met; exiting"
    exit 0
  fi

  if [ "$MAX_CYCLES" -gt 0 ] && [ "$cycle" -ge "$MAX_CYCLES" ]; then
    echo "[supervise-loop] max cycles=$MAX_CYCLES reached; exiting"
    exit 0
  fi

  if [ "$ACTION" = "wait" ]; then
    echo "[supervise-loop] action=wait; sleeping ${INTERVAL_SECONDS}s before next cycle"
    sleep "$INTERVAL_SECONDS"
    continue
  fi

  # For revive/reprompt, the once script already sent the prompt;
  # sleep before next inspection
  sleep "$INTERVAL_SECONDS"
done