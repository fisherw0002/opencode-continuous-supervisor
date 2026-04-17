# Maintenance Notes

## What is considered healthy

A healthy run should:
- start successfully with current cookie state
- discover the target service `207229`
- determine whether renew is currently allowed
- update local rolling cookie cache if session/cookies are refreshed
- write summary/logs after the run

## Expected normal outcomes

### Not yet due
Typical healthy output includes meaning like:
- login success
- found service `207229`
- not yet in renew window
- local cache updated

### Due and renewable
Expected behavior:
- service page accessible
- renew flow executed
- result logged
- cookie state rolled forward

## Failure classes

### Cookie/session invalid
Action:
- stop
- report clearly
- recover via manual VNC login + reseed

### Timer not firing
Action:
- inspect systemd timer/service state
- check recent logs
- confirm next trigger time

### Wrong service scope
Action:
- confirm `TARGET_SERVICE_IDS=207229` in `.env.local`
- do not broaden service scope accidentally

## Recommended admin checks

### Weekly
- inspect `latest-summary.txt`
- inspect recent lines in `scheduled-check.log`
- confirm timer still active

### After manual recovery
- rerun local check
- confirm summary reflects successful login/service discovery

## Commands

```bash
systemctl status --no-pager hidencloud-renew-check.timer hidencloud-renew-check.service
systemctl list-timers --all | grep hidencloud-renew-check
bash /root/.openclaw/workspace/hidencloud-renew-local/run_local_check.sh
tail -n 120 /root/.openclaw/workspace/hidencloud-renew-local/logs/scheduled-check.log
cat /root/.openclaw/workspace/hidencloud-renew-local/logs/latest-summary.txt
```
