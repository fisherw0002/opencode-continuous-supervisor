# Operations

## Purpose

Operate the server-local HidenCloud renew system safely and repeatedly.

## Main locations

- Project:
  - `/root/.openclaw/workspace/hidencloud-renew-local`
- Timer/service:
  - `hidencloud-renew-check.timer`
  - `hidencloud-renew-check.service`
- Logs:
  - `/root/.openclaw/workspace/hidencloud-renew-local/logs/scheduled-check.log`
  - `/root/.openclaw/workspace/hidencloud-renew-local/logs/latest-summary.txt`

## Routine checks

### Check timer status
Run:
```bash
systemctl status --no-pager hidencloud-renew-check.timer hidencloud-renew-check.service
systemctl list-timers --all | grep hidencloud-renew-check
```

### Run one check immediately
Run:
```bash
bash /root/.openclaw/workspace/hidencloud-renew-local/run_local_check.sh
```

### Read latest summary
Run:
```bash
cat /root/.openclaw/workspace/hidencloud-renew-local/logs/latest-summary.txt
```

### Read recent full log
Run:
```bash
tail -n 120 /root/.openclaw/workspace/hidencloud-renew-local/logs/scheduled-check.log
```

## Current production model

- `.env.local` is only the seed cookie source
- `hiden_cookies_US.json` is the rolling cookie cache
- scheduled runs should use current cookies first
- when cookies fail, stop and report
- recovery is manual VNC login + cookie reseed

## Service scope

Current locked service:
- `207229`

Do not broaden service scope unless explicitly requested.
