#!/usr/bin/env python3
import hashlib, json, os, re, sys
from pathlib import Path

STATE_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home()/".openclaw"/"workspace"/"state"/"opencode-supervisor"
ACTION = sys.argv[2] if len(sys.argv) > 2 else None
PROJECT_DIR = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None
SESSION_NAME = sys.argv[4] if len(sys.argv) > 4 else None

STATE_DIR.mkdir(parents=True, exist_ok=True)
REG = STATE_DIR / "session-registry.json"

def load():
    if REG.exists():
        try:
            return json.loads(REG.read_text())
        except Exception:
            return {"projects": {}}
    return {"projects": {}}

def save(d):
    REG.write_text(json.dumps(d, ensure_ascii=False, indent=2))

def default_name(project_dir: Path):
    base = project_dir.name or "repo"
    slug = re.sub(r'[^a-zA-Z0-9-]+', '-', base).strip('-').lower() or 'repo'
    digest = hashlib.sha1(str(project_dir).encode()).hexdigest()[:8]
    return f"oc-opencode-{slug}-{digest}"

if ACTION not in {"get","set","ensure","list"}:
    print(json.dumps({"status":"error","error":"usage: registry.py [state_dir] <get|set|ensure|list> [project_dir] [session_name]"}))
    sys.exit(2)

reg = load()
projects = reg.setdefault("projects", {})

if ACTION == "list":
    print(json.dumps(reg, ensure_ascii=False, indent=2))
    sys.exit(0)

if not PROJECT_DIR:
    print(json.dumps({"status":"error","error":"project_dir required"}))
    sys.exit(3)

key = str(PROJECT_DIR)
entry = projects.get(key)

if ACTION == "get":
    print(json.dumps({"status":"ok","project_dir":key,"entry":entry}, ensure_ascii=False, indent=2))
elif ACTION == "set":
    if not SESSION_NAME:
        print(json.dumps({"status":"error","error":"session_name required for set"}))
        sys.exit(4)
    projects[key] = {"session_name": SESSION_NAME}
    save(reg)
    print(json.dumps({"status":"ok","project_dir":key,"entry":projects[key]}, ensure_ascii=False, indent=2))
elif ACTION == "ensure":
    if not entry:
        projects[key] = {"session_name": SESSION_NAME or default_name(PROJECT_DIR)}
        save(reg)
    print(json.dumps({"status":"ok","project_dir":key,"entry":projects[key]}, ensure_ascii=False, indent=2))
