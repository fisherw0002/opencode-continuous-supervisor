#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path

if len(sys.argv) < 2:
    print(json.dumps({"status": "error", "error": "usage: opencode-delivery-report.py <combined_json> [session_name]"}, ensure_ascii=False))
    sys.exit(2)

combined_path = Path(sys.argv[1])
session_name = sys.argv[2] if len(sys.argv) > 2 else ""
if not combined_path.is_file():
    print(json.dumps({"status": "error", "error": "combined json not found"}, ensure_ascii=False))
    sys.exit(2)

combined = json.loads(combined_path.read_text())
watch = combined.get("watchdog", {})
accept = combined.get("acceptance", {})
quality = combined.get("qualityGate", {})
project_dir = Path((watch.get("project_dir") or accept.get("project_dir") or ".")).resolve()
criteria = accept.get("criteria") or quality.get("criteria") or "unknown"
accepted = bool(accept.get("accepted", False))
delivery_ready = quality.get("deliveryReady", True) if quality else True

artifact_candidates = []
for rel in accept.get("expectedArtifactFiles", []) or []:
    p = (project_dir / rel).resolve()
    artifact_candidates.append({
        "path": str(p),
        "relative": rel,
        "exists": p.exists(),
        "sizeBytes": p.stat().st_size if p.exists() else None,
    })

required_files = []
for rel in accept.get("expectedRequiredFiles", []) or []:
    p = (project_dir / rel).resolve()
    required_files.append({
        "path": str(p),
        "relative": rel,
        "exists": p.exists(),
    })

command_evidence = []
for item in accept.get("commands", []) or []:
    command_evidence.append({
        "command": item.get("command"),
        "ok": item.get("ok"),
        "returncode": item.get("returncode"),
        "missingStrings": item.get("missingStrings", []),
        "outputSnippet": item.get("outputSnippet", "")[:500],
    })

history_tail = ""
if session_name:
    try:
        p = subprocess.run(
            ["bash", str(Path(__file__).with_name("opencode-sessionctl.sh")), "read", str(project_dir), "", session_name],
            capture_output=True,
            text=True,
            timeout=20,
        )
        history_tail = ((p.stdout or "") + "\n" + (p.stderr or "")).strip()[:2000]
    except Exception as e:
        history_tail = f"history-read-error: {e}"

existing_artifacts = [a for a in artifact_candidates if a["exists"]]
missing_artifacts = [a["relative"] for a in artifact_candidates if not a["exists"]]

summary_lines = []
summary_lines.append(f"project={project_dir}")
summary_lines.append(f"criteria={criteria}")
summary_lines.append(f"accepted={str(accepted).lower()}")
summary_lines.append(f"delivery_ready={str(delivery_ready).lower()}")
if existing_artifacts:
    summary_lines.append("artifacts=")
    for a in existing_artifacts:
        summary_lines.append(f"- {a['relative']} ({a['sizeBytes']} bytes)")
if command_evidence:
    summary_lines.append("checks=")
    for c in command_evidence:
        status = "ok" if c.get("ok") else "fail"
        summary_lines.append(f"- [{status}] {c.get('command')}")
if missing_artifacts:
    summary_lines.append("missing_artifacts=")
    for rel in missing_artifacts:
        summary_lines.append(f"- {rel}")

user_summary_lines = []
if accepted and delivery_ready:
    user_summary_lines.append("任务已达到验收条件，且已通过交付质量验收。")
elif accepted:
    user_summary_lines.append("任务已达到基础验收条件，但未通过交付质量验收。")
else:
    user_summary_lines.append("任务尚未达到验收条件。")
if existing_artifacts:
    user_summary_lines.append("交付物：")
    for a in existing_artifacts:
        user_summary_lines.append(f"- {a['relative']}")
if command_evidence:
    user_summary_lines.append("检查结果：")
    for c in command_evidence:
        user_summary_lines.append(f"- {'通过' if c.get('ok') else '失败'}：{c.get('command')}")

print(json.dumps({
    "status": "ok",
    "project_dir": str(project_dir),
    "criteria": criteria,
    "accepted": accepted,
    "deliveryReady": delivery_ready,
    "qualityGate": quality,
    "requiredFiles": required_files,
    "artifacts": artifact_candidates,
    "existingArtifacts": existing_artifacts,
    "missingArtifacts": missing_artifacts,
    "commandEvidence": command_evidence,
    "historyTail": history_tail,
    "summary": "\n".join(summary_lines),
    "userSummary": "\n".join(user_summary_lines),
}, ensure_ascii=False, indent=2))
