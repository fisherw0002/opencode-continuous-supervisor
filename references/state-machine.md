# Suggested State Machine

## Runtime lifecycle states
- `active` — session healthy and history is moving
- `waiting_bootstrap` — session exists but no useful history yet
- `stalled` — no new history for N watchdog cycles
- `dead` — session process is dead

## Suggested supervisor decisions
- `ok` — do nothing
- `reprompt` — same session should receive another prompt / continue instruction
- `revive` — same logical job should be resumed by reviving/re-ensuring session first

## Acceptance note
This scaffold still does **runtime liveness**, not full delivery acceptance.
To make it production-grade, add workflow-specific acceptance criteria such as:
- tests passed
- required files changed
- artifact produced
- human review checkpoint passed
