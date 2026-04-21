#!/usr/bin/env python3
import json, os, re, subprocess, sys, time
from pathlib import Path

PROJECT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else None
SESSION_NAME = sys.argv[2] if len(sys.argv) > 2 else "oc-opencode-default"
STATE_DIR = Path(sys.argv[3]) if len(sys.argv) > 3 else Path.home()/".openclaw"/"workspace"/"state"/"opencode-supervisor"
STALL_CYCLES = int(os.environ.get("OPENCODE_STALL_CYCLES", "2"))

if not PROJECT_DIR or not PROJECT_DIR.is_dir():
    print(json.dumps({"status":"error","error":"valid project_dir required"}))
    sys.exit(2)

STATE_DIR.mkdir(parents=True, exist_ok=True)
state_file = STATE_DIR / f"{SESSION_NAME}.json"


def run(cmd):
    p = subprocess.run(cmd, cwd=str(PROJECT_DIR), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

# Always ensure session exists before inspection
run(["acpx","opencode","sessions","ensure","--name",SESSION_NAME])
run(["acpx","opencode","set","-s",SESSION_NAME,"model",os.environ.get("MODEL","cpap/gpt-5.3-codex")])

rc, status_out, status_err = run(["acpx","opencode","status","-s",SESSION_NAME])
rc2, read_out, read_err = run(["acpx","opencode","sessions","read","--tail","1",SESSION_NAME])

status = "unknown"
for line in status_out.splitlines():
    if line.startswith("status:"):
        status = line.split(":",1)[1].strip()
        break

latest_ts = None
latest_line = None
for line in read_out.splitlines():
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T[^\s]+)\s+", line)
    if m:
        latest_ts = m.group(1)
        latest_line = line

prev = {}
if state_file.exists():
    try:
        prev = json.loads(state_file.read_text())
    except Exception:
        prev = {}

stale_count = int(prev.get("stale_count", 0))
if latest_ts and latest_ts == prev.get("latest_ts"):
    stale_count += 1
else:
    stale_count = 0

if status == "dead":
    decision = "revive"
    reason = "session status dead"
elif stale_count >= STALL_CYCLES:
    decision = "reprompt"
    reason = f"no new history for {stale_count} watchdog cycles"
elif latest_ts is None:
    decision = "reprompt"
    reason = "no readable session history yet"
else:
    decision = "ok"
    reason = "session appears active or has fresh history"

out = {
    "status": "ok",
    "project_dir": str(PROJECT_DIR),
    "session_name": SESSION_NAME,
    "session_status": status,
    "latest_ts": latest_ts,
    "latest_line": latest_line,
    "stale_count": stale_count,
    "decision": decision,
    "reason": reason,
}
state_file.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(json.dumps(out, ensure_ascii=False, indent=2))
