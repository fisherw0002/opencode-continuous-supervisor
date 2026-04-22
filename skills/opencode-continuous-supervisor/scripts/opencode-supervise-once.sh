#!/bin/bash
# opencode-supervise-once.sh
# Runs one cycle: watchdog + acceptance check + unified decide → action
# Outputs: combined JSON + "decider: {...}" line + "[supervise-once] action=X reason=Y"
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
DELIVERY_PY="$(dirname "$0")/opencode-delivery-report.py"
TMPDIR="${TMPDIR:-/tmp}"
WATCH_FILE=$(mktemp "$TMPDIR/opencode-watch-XXXXXX.json")
ACCEPT_FILE=$(mktemp "$TMPDIR/opencode-accept-XXXXXX.json")
COMBINED_FILE=$(mktemp "$TMPDIR/opencode-combined-XXXXXX.json")
DECISION_FILE=$(mktemp "$TMPDIR/opencode-decision-XXXXXX.json")
DELIVERY_FILE=$(mktemp "$TMPDIR/opencode-delivery-XXXXXX.json")

cleanup() { rm -f "$WATCH_FILE" "$ACCEPT_FILE" "$COMBINED_FILE" "$DECISION_FILE" "$DELIVERY_FILE" 2>/dev/null; }
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

# Merge watch + accept into combined file
MERGE_SCRIPT=$(mktemp "$TMPDIR/merge-XXXXXX.py")
cat > "$MERGE_SCRIPT" <<'INNERPY'
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
open(sys.argv[3], "w").write(json.dumps(out, ensure_ascii=False, indent=2))
INNERPY
python3 "$MERGE_SCRIPT" "$WATCH_FILE" "$ACCEPT_FILE" "$COMBINED_FILE"
rm -f "$MERGE_SCRIPT"

# Print combined JSON to stdout (for callers that want it)
cat "$COMBINED_FILE"
printf '\n'

# Run unified decider → write to decision file
python3 "$DECIDE_PY" "$COMBINED_FILE" > "$DECISION_FILE"
DECISION=$(cat "$DECISION_FILE")

# Echo decider as a separate parseable line
echo "decider: $DECISION"

# Extract action + reason
ACTION=$(python3 -c "import json; print(json.load(open('$DECISION_FILE')).get('action','error'))")
REASON=$(python3 -c "import json; print(json.load(open('$DECISION_FILE')).get('reason',''))")

echo "[supervise-once] action=$ACTION reason=$REASON"

# Build delivery report on stop so callers can proactively report back to the user.
if [ "$ACTION" = "stop" ]; then
  python3 "$DELIVERY_PY" "$COMBINED_FILE" "$SESSION_NAME" > "$DELIVERY_FILE"
  DELIVERY_COMPACT=$(python3 -c "import json; print(json.dumps(json.load(open('$DELIVERY_FILE')), ensure_ascii=False))")
  echo "delivery: $DELIVERY_COMPACT"
  echo "[supervise-once] action=stop; delivery report generated; no prompt sent"
  exit 0
fi

# If wait, do NOT send a prompt; just exit
if [ "$ACTION" = "wait" ]; then
  echo "[supervise-once] action=wait; no prompt sent"
  exit 0
fi

# Determine prompt text
if [ -n "$PROMPT_FILE" ] && [ -f "$PROMPT_FILE" ]; then
  PROMPT_TEXT=$(cat "$PROMPT_FILE")
else
  PROMPT_TEXT=$(cat "$DEFAULT_PROMPT_FILE")
fi

bash "$(dirname "$0")/opencode-sessionctl.sh" prompt "$PROJECT_DIR" "$PROMPT_TEXT" "$SESSION_NAME"
