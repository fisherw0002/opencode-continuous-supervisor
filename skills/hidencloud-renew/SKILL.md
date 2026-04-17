---
name: hidencloud-renew
description: Manage HidenCloud free-service auto-renew on this server. Use when the user asks to configure, run, repair, inspect, or schedule HidenCloud renew checks; when they mention service 207229, Renew, Due date, cookie refresh, Epiphany cookies.sqlite, VNC manual relogin fallback, or daily 19:00 checks. Supports a cookie-rolling updater model: use current cookies to check/renew, persist refreshed cookies after each run, and fall back to manual VNC login + cookie reseed only when cookies become invalid.
---

# HidenCloud Renew

Use this skill for the server-local HidenCloud renew setup under:

`/root/.openclaw/workspace/hidencloud-renew-local`

## What this skill owns

- Cookie-rolling renew/check workflow
- Local HidenCloud cookie seed/reseed from Epiphany
- Service filtering for target service(s)
- Daily 19:00 timer/service management
- Logs and summary inspection
- VNC manual relogin fallback when cookies expire

## Current chosen architecture

Do **not** default to GUI clicking or OCR.

Preferred model:
1. Use current saved cookies to check/renew
2. Let the updater persist refreshed cookies after each run
3. On cookie invalidation, stop and report clearly
4. User manually relogs through VNC
5. Reseed cookies from Epiphany

## Important paths

- Project dir:
  - `/root/.openclaw/workspace/hidencloud-renew-local`
- Initial seed cookie:
  - `/root/.openclaw/workspace/hidencloud-renew-local/.env.local`
- Multi-account template:
  - `/root/.openclaw/workspace/hidencloud-renew-local/.env.accounts.example`
- Rolling cookie cache:
  - `/root/.openclaw/workspace/hidencloud-renew-local/hiden_cookies_US.json`
- Scheduled full log:
  - `/root/.openclaw/workspace/hidencloud-renew-local/logs/scheduled-check.log`
- Latest summary:
  - `/root/.openclaw/workspace/hidencloud-renew-local/logs/latest-summary.txt`
- Reseed helper:
  - `/root/.openclaw/workspace/hidencloud-renew-local/reseed_cookie_from_vnc.sh`

## Current target service

Default locked target:
- `TARGET_SERVICE_IDS=207229`

Only change this if the user explicitly asks.

## Current schedule

- Daily check at **19:00** via systemd timer
- Timer names:
  - `hidencloud-renew-check.service`
  - `hidencloud-renew-check.timer`

## What to do for common requests

### 1. “Check status / did it run?”
Run:
- `systemctl status --no-pager hidencloud-renew-check.timer hidencloud-renew-check.service`
- `systemctl list-timers --all | grep hidencloud-renew-check`
- inspect latest summary/logs

### 2. “Run one check now”
Run:
- `bash /root/.openclaw/workspace/hidencloud-renew-local/run_local_check.sh`
- or `python /root/.openclaw/workspace/hidencloud-renew-local/run_scheduled_check.py`

### 3. “Cookie expired / relogin needed”
Do **not** try to rebuild a GUI automation path first.
Preferred recovery:
1. User logs in through VNC manually
2. Run:
   - `bash /root/.openclaw/workspace/hidencloud-renew-local/reseed_cookie_from_vnc.sh`
3. Re-run a local check
4. Confirm summary/logs updated

### 4. “Add another account later”
Use `.env.accounts.example` as the pattern.
Preserve account 1 as current setup; add `HIDEN_COOKIE_2`, `HIDEN_COOKIE_3`, etc. only if requested.

### 5. “Change schedule”
Edit the systemd timer instead of inventing a second scheduler.

## When to read more

If you need implementation details, read these files directly:
- `hidencloud-renew-local/README-LOCAL.md`
- `hidencloud-renew-local/LOCAL_NOTES.md`
- `hidencloud-renew-local/run_scheduled_check.py`
- `hidencloud-renew-local/export_epiphany_hiden_cookie.py`
- `hidencloud-renew-local/main.py`

## Guardrails

- Do not revert to Epiphany/OCR/button-click automation unless the user explicitly asks
- Do not remove the service filter from `207229` unless requested
- Do not overwrite `.env.local` casually; reseed intentionally
- Treat cookie reseed as a recovery action, not the main steady-state flow
