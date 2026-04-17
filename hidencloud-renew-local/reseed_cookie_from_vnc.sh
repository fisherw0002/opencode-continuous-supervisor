#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/hidencloud-renew-local
./.venv/bin/python export_epiphany_hiden_cookie.py
printf '已从 Epiphany cookies.sqlite 重新导出 HIDEN_COOKIE 到 .env.local\n'
