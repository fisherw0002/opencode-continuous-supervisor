#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path

PROJECT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else None
CRITERIA = Path(sys.argv[2]) if len(sys.argv) > 2 else None

if not PROJECT_DIR or not PROJECT_DIR.is_dir():
    print(json.dumps({"status":"error","error":"valid project_dir required"}))
    sys.exit(2)
if not CRITERIA or not CRITERIA.is_file():
    print(json.dumps({"status":"error","error":"criteria file required"}))
    sys.exit(3)

criteria = json.loads(CRITERIA.read_text())

def run(cmd, timeout=60):
    p = subprocess.run(cmd, cwd=str(PROJECT_DIR), shell=True, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

missing_required = []
for rel in criteria.get("requiredFiles", []):
    if not (PROJECT_DIR / rel).exists():
        missing_required.append(rel)

missing_artifacts = []
for rel in criteria.get("artifactFiles", []):
    if not (PROJECT_DIR / rel).exists():
        missing_artifacts.append(rel)

command_results = []
commands_ok = True
for item in criteria.get("commands", []):
    cmd = item["command"]
    must = item.get("mustContain", [])
    rc, out, err = run(cmd)
    hay = (out or "") + "\n" + (err or "")
    missing = [s for s in must if s not in hay]
    ok = (rc == 0 and not missing)
    commands_ok = commands_ok and ok
    command_results.append({
        "command": cmd,
        "returncode": rc,
        "ok": ok,
        "missingStrings": missing,
        "outputSnippet": hay[:1500]
    })

text_checks = []
text_ok = True
for item in criteria.get("fileTextMustContain", []):
    path = PROJECT_DIR / item["path"]
    contains = item.get("contains", [])
    if not path.exists():
        text_checks.append({"path": item["path"], "ok": False, "missing": contains, "error": "missing file"})
        text_ok = False
        continue
    text = path.read_text(errors="ignore")
    missing = [s for s in contains if s not in text]
    ok = not missing
    text_ok = text_ok and ok
    text_checks.append({"path": item["path"], "ok": ok, "missing": missing})

accepted = (not missing_required) and (not missing_artifacts) and commands_ok and text_ok

print(json.dumps({
    "status": "ok",
    "project_dir": str(PROJECT_DIR),
    "criteria": criteria.get("name", CRITERIA.name),
    "accepted": accepted,
    "missingRequiredFiles": missing_required,
    "missingArtifacts": missing_artifacts,
    "commands": command_results,
    "textChecks": text_checks
}, ensure_ascii=False, indent=2))
