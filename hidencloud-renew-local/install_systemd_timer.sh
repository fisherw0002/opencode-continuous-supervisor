#!/usr/bin/env bash
set -euo pipefail

cat > /etc/systemd/system/hidencloud-renew-check.service <<'UNIT'
[Unit]
Description=HidenCloud daily renew check
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/root/.openclaw/workspace/hidencloud-renew-local
ExecStart=/root/.openclaw/workspace/hidencloud-renew-local/.venv/bin/python /root/.openclaw/workspace/hidencloud-renew-local/run_scheduled_check.py
UNIT

cat > /etc/systemd/system/hidencloud-renew-check.timer <<'UNIT'
[Unit]
Description=Run HidenCloud renew check daily at 19:00

[Timer]
OnCalendar=*-*-* 19:00:00
Persistent=true
Unit=hidencloud-renew-check.service

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now hidencloud-renew-check.timer
systemctl status --no-pager hidencloud-renew-check.timer
systemctl list-timers --all | grep hidencloud-renew-check || true
