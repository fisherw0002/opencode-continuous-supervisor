# Minimal Components

## Component 1: Persistent Session Controller
Responsibilities:
- ensure/create persistent OpenCode session
- load/resume prior session
- send prompt / continue prompt
- cancel / close session
- persist stable identifiers

## Component 2: Session Registry
Responsibilities:
- map project/repo -> primary session
- resume before create
- reject unnecessary session fan-out

## Component 3: Supervisor / Watchdog
Responsibilities:
- inspect OpenClaw tasks
- inspect ACP child session status
- inspect stream freshness / waiting states
- decide whether to re-activate
- stop only on acceptance, not just completion

## Anti-patterns
- binding Telegram chat directly to the worker session
- using file mtimes as the main liveness signal
- considering `run completed` equal to delivery complete
- creating a new ACP run for every user nudge
