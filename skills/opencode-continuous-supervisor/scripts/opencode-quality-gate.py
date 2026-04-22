#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

PROJECT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else None
CRITERIA = Path(sys.argv[2]) if len(sys.argv) > 2 else None

if not PROJECT_DIR or not PROJECT_DIR.is_dir():
    print(json.dumps({"status": "error", "error": "valid project_dir required"}, ensure_ascii=False))
    sys.exit(2)
if not CRITERIA or not CRITERIA.is_file():
    print(json.dumps({"status": "error", "error": "criteria file required"}, ensure_ascii=False))
    sys.exit(3)

criteria = json.loads(CRITERIA.read_text())
delivery = criteria.get("deliveryChecks", {}) or {}

required_artifacts = delivery.get("artifactFiles", criteria.get("artifactFiles", [])) or []
min_sizes = delivery.get("artifactMinSizeBytes", {}) or {}
text_rules = delivery.get("fileTextMustContain", []) or []
commands = delivery.get("commands", []) or []
manual_notes = delivery.get("manualReviewNotes", []) or []


def run(cmd, timeout=60):
    p = subprocess.run(cmd, cwd=str(PROJECT_DIR), shell=True, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

artifact_checks = []
artifact_ok = True
for rel in required_artifacts:
    p = PROJECT_DIR / rel
    exists = p.exists()
    size = p.stat().st_size if exists else None
    min_size = min_sizes.get(rel)
    size_ok = True if min_size is None else (exists and size is not None and size >= int(min_size))
    ok = exists and size_ok
    artifact_ok = artifact_ok and ok
    artifact_checks.append({
        "relative": rel,
        "path": str(p),
        "exists": exists,
        "sizeBytes": size,
        "minSizeBytes": min_size,
        "ok": ok,
    })

text_checks = []
text_ok = True
for item in text_rules:
    rel = item["path"]
    path = PROJECT_DIR / rel
    contains = item.get("contains", [])
    if not path.exists():
        text_checks.append({"path": rel, "ok": False, "missing": contains, "error": "missing file"})
        text_ok = False
        continue
    text = path.read_text(errors="ignore")
    missing = [s for s in contains if s not in text]
    ok = not missing
    text_ok = text_ok and ok
    text_checks.append({"path": rel, "ok": ok, "missing": missing})

command_results = []
commands_ok = True
for item in commands:
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
        "outputSnippet": hay[:1000],
    })

quality_ready = artifact_ok and text_ok and commands_ok
issues = []
for a in artifact_checks:
    if not a["ok"]:
        if not a["exists"]:
            issues.append(f"missing artifact: {a['relative']}")
        else:
            issues.append(f"artifact too small or invalid: {a['relative']} (size={a['sizeBytes']}, min={a['minSizeBytes']})")
for t in text_checks:
    if not t["ok"]:
        issues.append(f"file text check failed: {t['path']} missing={t.get('missing', [])}")
for c in command_results:
    if not c["ok"]:
        issues.append(f"quality command failed: {c['command']} missing={c.get('missingStrings', [])}")

feedback_lines = [
    "当前任务已满足基础 acceptance，但未通过交付质量验收，请按以下问题返工："
]
for i in issues:
    feedback_lines.append(f"- {i}")
if manual_notes:
    feedback_lines.append("额外人工要求：")
    for n in manual_notes:
        feedback_lines.append(f"- {n}")
feedback_lines.append("返工后重新产出交付物，并确保质量闸门通过。")

print(json.dumps({
    "status": "ok",
    "project_dir": str(PROJECT_DIR),
    "criteria": criteria.get("name", CRITERIA.name),
    "qualityChecksPresent": bool(delivery),
    "deliveryReady": quality_ready,
    "artifactChecks": artifact_checks,
    "textChecks": text_checks,
    "commandChecks": command_results,
    "issues": issues,
    "manualReviewNotes": manual_notes,
    "feedbackPrompt": "\n".join(feedback_lines),
}, ensure_ascii=False, indent=2))
