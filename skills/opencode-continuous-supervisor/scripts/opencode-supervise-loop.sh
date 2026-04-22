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
DELIVERY_MODE="${OPENCODE_DELIVERY_MODE:-final}"
ONCE_SH="$(dirname "$0")/opencode-supervise-once.sh"
SEND_SH="$(dirname "$0")/opencode-delivery-send.sh"

derive_state_name() {
  local proj="$1"
  local sess="$2"
  local safe_proj=$(printf '%s' "$proj" | tr '/' '_' | tr -d ' ')
  local safe_sess=$(printf '%s' "$sess" | tr '/' '_' | tr -d ' ')
  echo "delivery-hash-${safe_proj:-default}${safe_sess:+-$safe_sess}"
}

get_state_file() {
  local key=$(derive_state_name "$PROJECT_DIR" "$SESSION_NAME")
  echo "$STATE_DIR/$key"
}

DELIVERY_HASH_FILE=$(get_state_file)
DELIVERY_LOCK_FILE="$STATE_DIR/delivery-lock"

acquire_lock() {
  local max_wait=30
  local waited=0
  while [ -f "$DELIVERY_LOCK_FILE" ]; do
    if [ $waited -ge $max_wait ]; then
      echo "[supervise-loop] ERROR: lock timeout, another delivery in progress"
      return 1
    fi
    sleep 1
    waited=$((waited+1))
  done
  echo $$ > "$DELIVERY_LOCK_FILE"
}

release_lock() {
  rm -f "$DELIVERY_LOCK_FILE"
}

trap release_lock EXIT

delivery_hash() {
  printf '%s' "$1" | python3 -c "import json,sys,hashlib; d=json.load(sys.stdin); h=hashlib.sha256(); key=d.get('existingArtifacts',[{}])[0].get('path','')+str(d.get('existingArtifacts',[{}])[0].get('size',0))+str(d.get('criteria',''))+(d.get('userSummary') or d.get('summary') or ''); h.update(key.encode()); print(h.hexdigest())"
}

is_delivery_duplicate() {
  local current_hash="$1"
  local last_hash=""
  if [ -f "$DELIVERY_HASH_FILE" ]; then
    last_hash=$(cat "$DELIVERY_HASH_FILE")
  fi
  if [ -n "$last_hash" ] && [ "$current_hash" = "$last_hash" ]; then
    return 0
  fi
  return 1
}

save_delivery_hash() {
  mkdir -p "$(dirname "$DELIVERY_HASH_FILE")"
  printf '%s' "$1" > "$DELIVERY_HASH_FILE"
}

wrap_message_for_mode() {
  local msg="$1"
  if [ "$DELIVERY_MODE" = "test" ]; then
    echo "[测试] $msg"
  else
    echo "$msg"
  fi
}

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [session_name] [prompt_file] [state_dir] [criteria_file]" >&2
  exit 2
fi

echo "[supervise-loop] mode=$DELIVERY_MODE project=$PROJECT_DIR session=$SESSION_NAME"

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
        if ! acquire_lock; then
          echo "[supervise-loop] delivery skipped due to lock"
        else
          CURRENT_HASH=$(delivery_hash "$DELIVERY_LINE")
          if is_delivery_duplicate "$CURRENT_HASH"; then
            echo "[supervise-loop] already delivered, skip send"
          else
            SAVE_HASH="$CURRENT_HASH"
            DELIVERY_LINE_MODED=$(wrap_message_for_mode "$DELIVERY_LINE")
            SEND_OUT=$(bash "$SEND_SH" "$DELIVERY_LINE_MODED" 2>&1) || true
            echo "[supervise-loop] notify=$SEND_OUT"
            if [ -n "$SAVE_HASH" ]; then
              save_delivery_hash "$SAVE_HASH"
            fi
          fi
        fi
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
