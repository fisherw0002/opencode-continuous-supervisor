#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

TASK_STALE_THRESHOLD = int(os.environ.get("OPENCODE_TASK_STALE_THRESHOLD", "1800"))

if len(sys.argv) > 1:
    raw = Path(sys.argv[1]).read_text()
elif not sys.stdin.isatty():
    raw = sys.stdin.read()
else:
    print(json.dumps({"action":"error","reason":"no input"}))
    sys.exit(1)

data = json.loads(raw)
watch = data.get("watchdog", {})
accept = data.get("acceptance", {})
task_sum = watch.get("taskSummary") or {}

session_status = watch.get("session_status", "unknown")
lifecycle = watch.get("lifecycle", "unknown")
stale_count = watch.get("stale_count", 0)
accepted = accept.get("accepted", False) if accept else False

if accepted is True:
    action = "stop"
    reason = "acceptance criteria met; stopping supervisor"
    print(json.dumps({"action": action, "reason": reason}))
    sys.exit(0)

if session_status == "dead":
    action = "revive"
    reason = "session status dead and not yet accepted"
    print(json.dumps({"action": action, "reason": reason}))
    sys.exit(0)

if lifecycle in ("stalled", "waiting_bootstrap"):
    action = "reprompt"
    reason = f"lifecycle={lifecycle} ({stale_count} stale cycles)"
    print(json.dumps({"action": action, "reason": reason}))
    sys.exit(0)

stale_running = task_sum.get("staleRunning", [])
if stale_running:
    very_old = all(t.get("ageSeconds", 0) > TASK_STALE_THRESHOLD for t in stale_running)
    if very_old:
        action = "reprompt"
        reason = f"{len(stale_running)} stale tasks, all > {TASK_STALE_THRESHOLD}s old"
        print(json.dumps({"action": action, "reason": reason}))
        sys.exit(0)

action = "wait"
reason = f"session_status={session_status} lifecycle={lifecycle} accepted={accepted}"
print(json.dumps({"action": action, "reason": reason}))