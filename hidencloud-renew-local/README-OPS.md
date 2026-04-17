# HidenCloud Renew Local - Ops Guide

## Purpose

This is the server-local production setup for HidenCloud free-service renew checks.

Current production model:
- use current saved cookies to check/renew
- let the updater roll cookies forward after each run
- if cookies fail, stop and report
- recover with manual VNC login + cookie reseed

## Scope

Current locked target service:
- `207229`

Do not expand scope unless explicitly requested.

## Main files

- `main.py` — upstream renew/check logic
- `.env.local` — seed cookie source and local config
- `.env.accounts.example` — multi-account template
- `hiden_cookies_US.json` — rolling cookie cache
- `run_local_check.sh` — manual check entry
- `run_scheduled_check.py` — scheduled wrapper
- `export_epiphany_hiden_cookie.py` — export seed cookie from Epiphany
- `reseed_cookie_from_vnc.sh` — recovery reseed helper
- `install_systemd_timer.sh` — timer installation helper

## Scheduling

Systemd objects:
- `hidencloud-renew-check.service`
- `hidencloud-renew-check.timer`

Current schedule:
- daily at **19:00**

Check timer:
```bash
systemctl status --no-pager hidencloud-renew-check.timer hidencloud-renew-check.service
systemctl list-timers --all | grep hidencloud-renew-check
```

## Manual operations

### Run one check now
```bash
bash /root/.openclaw/workspace/hidencloud-renew-local/run_local_check.sh
```

### Read latest summary
```bash
cat /root/.openclaw/workspace/hidencloud-renew-local/logs/latest-summary.txt
```

### Read recent full log
```bash
tail -n 120 /root/.openclaw/workspace/hidencloud-renew-local/logs/scheduled-check.log
```

## Cookie model

### Seed cookie
- stored in `.env.local`
- used to bootstrap the system

### Rolling cookie cache
- stored in `hiden_cookies_US.json`
- updater should prefer this rolling cache on later runs

### Recovery path
When cookies become invalid:
1. open VNC/noVNC
2. manually log in to HidenCloud
3. reseed:
```bash
bash /root/.openclaw/workspace/hidencloud-renew-local/reseed_cookie_from_vnc.sh
```
4. rerun a local check

## Multi-account reserve
Reserved env names:
- `HIDEN_COOKIE`
- `HIDEN_COOKIE_2`
- `HIDEN_COOKIE_3`

Add extra accounts only when explicitly needed.

## Logs

- full log:
  - `logs/scheduled-check.log`
- latest summary:
  - `logs/latest-summary.txt`

## Guardrails

- do not switch primary flow back to GUI/OCR/button-click automation
- do not remove service filter `207229` unless requested
- do not casually overwrite `.env.local`
- treat VNC login only as a recovery mechanism
