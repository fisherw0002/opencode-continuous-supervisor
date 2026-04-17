# Current HidenCloud Renew Setup

## Architecture

Chosen production approach:
- updater uses current cookies to check/renew
- updater persists refreshed cookies after each run
- when cookies fail, stop and report
- user manually logs in through VNC
- cookies are reseeded from Epiphany only as recovery

Rejected as primary path:
- VNC GUI click automation
- OCR/button-coordinate automation
- relying on permanent Epiphany login as steady state

## Local project

Project directory:
- `/root/.openclaw/workspace/hidencloud-renew-local`

Important files:
- `.env.local`
- `.env.accounts.example`
- `hiden_cookies_US.json`
- `run_local_check.sh`
- `run_scheduled_check.py`
- `export_epiphany_hiden_cookie.py`
- `reseed_cookie_from_vnc.sh`
- `logs/scheduled-check.log`
- `logs/latest-summary.txt`

## Service scope

Current target service:
- `207229`

Current renewal rule already validated manually:
- renew allowed only when less than 1 day remains before expiration
- successful renew extends due date by 7 days

## Scheduling

Systemd timer/service:
- `hidencloud-renew-check.timer`
- `hidencloud-renew-check.service`

Schedule:
- daily 19:00

## Cookies

Seed source used to bootstrap current setup:
- `/root/.local/share/epiphany/cookies.sqlite`

Current intended steady-state behavior:
- `.env.local` provides initial seed cookie(s)
- updater then rolls cookie state forward via local cache
- if invalid, reseed manually from VNC login

## Multi-account plan

Reserved structure:
- `HIDEN_COOKIE`
- `HIDEN_COOKIE_2`
- `HIDEN_COOKIE_3`

Keep account expansion explicit; do not silently assume extra accounts.
