#!/bin/bash
set -euo pipefail

ACTION="${1:-}"
PROJECT_DIR="${2:-}"
PROMPT_TEXT="${3:-}"
SESSION_NAME="${4:-oc-opencode-default}"
MODEL="${MODEL:-cpap/gpt-5.3-codex}"

if [ -z "$ACTION" ] || [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 <ensure|status|prompt|cancel|close|history|read> <project_dir> [prompt_text] [session_name]" >&2
  exit 2
fi

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Project dir not found: $PROJECT_DIR" >&2
  exit 3
fi

cd "$PROJECT_DIR"

ensure_session() {
  acpx opencode sessions ensure --name "$SESSION_NAME" >/tmp/opencode-supervisor.ensure.out
  acpx opencode set -s "$SESSION_NAME" model "$MODEL" >/tmp/opencode-supervisor.model.out
}

case "$ACTION" in
  ensure)
    ensure_session
    echo "session=$SESSION_NAME cwd=$PROJECT_DIR model=$MODEL"
    ;;
  status)
    ensure_session
    acpx opencode status -s "$SESSION_NAME"
    ;;
  prompt)
    if [ -z "$PROMPT_TEXT" ]; then
      echo "prompt requires prompt_text" >&2
      exit 4
    fi
    ensure_session
    acpx opencode prompt -s "$SESSION_NAME" "$PROMPT_TEXT"
    ;;
  cancel)
    ensure_session
    acpx opencode cancel -s "$SESSION_NAME"
    ;;
  close)
    acpx opencode sessions close "$SESSION_NAME"
    ;;
  history)
    ensure_session
    acpx opencode sessions history --limit 20 "$SESSION_NAME"
    ;;
  read)
    ensure_session
    acpx opencode sessions read --tail 20 "$SESSION_NAME"
    ;;
  *)
    echo "Unknown action: $ACTION" >&2
    exit 5
    ;;
esac
