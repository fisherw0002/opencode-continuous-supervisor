#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/hidencloud-renew-local
./.venv/bin/python run_local_check.py
