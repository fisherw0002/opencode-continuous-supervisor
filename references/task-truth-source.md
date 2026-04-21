# Task Truth Source Notes

## What is used
The current scaffold queries:

```bash
openclaw tasks list --status running --json
```

It extracts:
- running task count
- stale running task count
- a small list of stale running tasks

## Why this is only best-effort
OpenClaw tasks are a runtime ledger, but they may include:
- unrelated ACP tasks from other workflows
- stale tasks that still show `running`
- requester sessions outside the current project

Therefore task truth is useful, but should not be the **only** stop/continue signal.

## Recommended use
Treat task truth as one input among three:
1. session truth (`acpx opencode status`)
2. history/stream freshness
3. acceptance truth (`accepted: true/false`)

## Meaningful derived signals
- `runningCount`
- `staleRunningCount`
- `staleRunning[*].ageSeconds`

If stale running ACP tasks accumulate, that is a signal the system may be leaking work or not closing detached runs correctly.
