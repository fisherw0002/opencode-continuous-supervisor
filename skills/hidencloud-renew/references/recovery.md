# Recovery

## When to use

Use this recovery flow when the HidenCloud updater reports invalid cookies, login failure, unauthorized state, or otherwise cannot access the target service with the rolling cookie cache.

## Recovery steps

1. Start or access the existing VNC/noVNC environment on the server
2. Manually log in to HidenCloud in the server browser
3. Reseed the cookie source:

```bash
bash /root/.openclaw/workspace/hidencloud-renew-local/reseed_cookie_from_vnc.sh
```

4. Run one local check immediately:

```bash
bash /root/.openclaw/workspace/hidencloud-renew-local/run_local_check.sh
```

5. Confirm output in:
- `logs/latest-summary.txt`
- `logs/scheduled-check.log`

## Important notes

- Do not treat Epiphany login as the normal steady-state mechanism
- Use VNC login only as a recovery path when rolling cookies fail
- Keep the service filter on `207229` unless the user explicitly expands scope
