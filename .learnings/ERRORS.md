# Errors

Command failures and integration errors.

---
## [ERR-20260410-001] code-server install.sh PATH

**Logged**: 2026-04-10T09:24:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
code-server install script failed because required system binaries (ldconfig/start-stop-daemon) were not in PATH.

### Details
Running `curl -fsSL https://code-server.dev/install.sh | sh` failed with:
- dpkg: warning: 'ldconfig' not found in PATH or not executable
- dpkg: warning: 'start-stop-daemon' not found in PATH or not executable
- dpkg: error: 2 expected programs not found in PATH or not executable

### Suggested Action
Retry the install with a corrected PATH that includes /usr/sbin and /sbin, or run via a login shell.

### Metadata
- Source: error
- Tags: code-server, install, PATH, dpkg
---
