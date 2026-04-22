#!/bin/bash
# opencode-supervise-loop.sh
# Runs supervise-once in a loop until acceptance is met or max cycles reached.
set -euo pipefail

PROJECT_DIR="${1:-}"
SESSION_NAME="${2:-}"
PROMPT_FILE="${3:-}"
STATE_DIR="${4:-$HOME/.openclaw/workspace/state/opencode-supervisor}"
CRITERIA_FILE="${5:-}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-120}"
MAX_CYCLES="${MAX_CYCLES:-0}"
AUTO_DELIVER="${OPENCODE_AUTO_DELIVER:-0}"
ONCE_SH="$(dirname "$0")/opencode-supervise-once.sh"
SEND_SH="$(dirname "$0")/opencode-delivery-send.sh"

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [session_name] [prompt_file] [state_dir] [criteria_file]" >&2
  exit 2
fi

cycle=0
while true; do
  cycle=$((cycle+1))
  echo "[supervise-loop] cycle=$cycle project=$PROJECT_DIR"

  # Run once; capture full output
  OUT=$(bash "$ONCE_SH" "$PROJECT_DIR" "$SESSION_NAME" "$PROMPT_FILE" "$STATE_DIR" "$CRITERIA_FILE" 2>&1) || true

  # Extract action from the "decider: {...}" line that once.sh emits
  # The decider line looks like:  decider: {"action": "stop", "reason": "..."}
  # Use grep + sed in a subshell that won't kill the script on non-match
  DECIDER_LINE=$(printf '%s' "$OUT" | grep '^decider: ' | head -1 | sed 's/^decider: //' || true)
  if [ -z "$DECIDER_LINE" ]; then
    echo "[supervise-loop] WARNING: no decider line found in once.sh output; defaulting to wait"
    ACTION="wait"
  else
    ACTION=$(printf '%s' "$DECIDER_LINE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('action','error'))")
  fi

  echo "[supervise-loop] cycle=$cycle action=$ACTION"

  if [ "$ACTION" = "stop" ]; then
    DELIVERY_LINE=$(printf '%s' "$OUT" | grep '^delivery: ' | head -1 | sed 's/^delivery: //' || true)
    if [ -n "$DELIVERY_LINE" ]; then
      echo "[supervise-loop] delivery=$DELIVERY_LINE"
      if [ "$AUTO_DELIVER" = "1" ]; then
        SEND_OUT=$(bash "$SEND_SH" "$DELIVERY_LINE" 2>&1) || true
        echo "[supervise-loop] notify=$SEND_OUT"
      fi
    else
      echo "[supervise-loop] WARNING: action=stop but no delivery line found"
    fi
    echo "[supervise-loop] acceptance met or stop requested; exiting"
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

  # For revive/reprompt, once.sh already sent the prompt; sleep before next inspection
  sleep "$INTERVAL_SECONDS"
done
