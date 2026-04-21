---
name: opencode-continuous-supervisor
description: >
  Design or implement a non-chat-bound persistent OpenCode work loop for OpenClaw bots.
  Use when a bot can start OpenCode/ACP work but it stops after one run, loses context,
  or lacks a persistent activation mechanism. Covers three core components:
  (1) persistent session controller, (2) session registry / resume policy,
  and (3) supervisor / watchdog based on ACP task and stream state.
  Trigger on requests like: "让小弟和 opencode 持续工作", "不要绑定聊天的 acp 模式",
  "做一个持续激活机制", "controller / mission control", "session 不要每轮重开", "别干一会就停".
---

# Opencode Continuous Supervisor

Use this skill when the real problem is **not** whether ACP exists, but whether OpenCode can keep working continuously **without binding the user chat** and **without dying after one run**.

## Core judgment

If the system already proves that:
- OpenCode can run through ACP, and
- the bot can still reply normally in chat,

then do **not** redesign around chat binding. The missing piece is usually a **continuous activation mechanism**.

## The 3 components to build

### 1. Persistent session controller
Borrow the control-plane idea from community `opencode-acp-control` style skills:
- create / load / prompt / cancel / close a persistent OpenCode ACP session
- persist both process/session identifiers
- treat `stopReason` as end-of-turn, **not** end-of-job

### 2. Session registry / resume policy
Borrow the reuse idea from `occ`-style controllers:
- one repo / project should prefer one main OpenCode session
- resume existing session before creating a new one
- only create a new session when no valid reusable session exists

### 3. Supervisor / watchdog
Use OpenClaw official task/session truth sources:
- `openclaw tasks show/list`
- ACP child-session status
- stream logs / last output timestamps
- waiting-for-input / stalled / terminal states

The watchdog decides whether to re-activate OpenCode.

## Do NOT rely on these as the primary truth source

Do not drive the watchdog mainly from:
- file mtimes
- whether `popup.css` changed
- whether a ZIP exists
- whether one test number still says 40/40

Those are output signals, not runtime truth.

## Recommended runtime shape

### Preferred near-term shape
- Bot may remain ACP-backed
- **No chat binding** (`thread: false`, no topic/thread/current-chat bind)
- Persistent OpenCode session behind the bot
- Separate watchdog that can continue / re-prompt / cancel / recover

### Preferred long-term shape
- Bot is a normal OpenClaw agent
- OpenCode is a background persistent worker/session
- Bot handles prompting, validation, and user-facing replies
- Watchdog continues work until acceptance criteria are met

## Minimal watchdog state machine

Track at least these states:
- `idle`
- `running`
- `waiting_input`
- `stalled`
- `needs_review`
- `accepted`
- `done`
- `failed`

## Minimal re-activation rules

- If session exists and is healthy → continue same session
- If session is `waiting_input` and work is unfinished → send next explicit prompt
- If task/session is `running` but no stream delta for N seconds → mark `stalled`
- If `stalled` and acceptance criteria not met → re-activate / steer
- If run is terminal but acceptance criteria not met → start next iteration
- Only stop when acceptance criteria are satisfied

## Acceptance criteria must be explicit

The watchdog must not stop at “run completed”.
It should stop only when the job is actually accepted, for example:
- tests passed
- required files changed
- UI matches requested structure
- artifact exists
- human-facing summary is ready

## What to borrow from community projects

### Borrow
- session lifecycle control
- session reuse / resume policy
- session identity persistence
- mission-control style orchestration thinking

### Do NOT blindly copy
- auto-install side effects (`npm install` at runtime)
- raw child_process orchestration without OpenClaw state integration
- pure poll loops with no task/session truth model
- anything that binds user chat directly to the worker session unless explicitly requested

## Included semi-executable scaffolding

This skill now includes a minimal runnable scaffold under `scripts/`:

- `scripts/opencode-sessionctl.sh`
  - ensure/status/prompt/cancel/close/history/read for a named OpenCode session
- `scripts/opencode-watchdog.py`
  - inspects session health + recent history and emits a decision JSON
- `scripts/opencode-supervise-once.sh`
  - runs watchdog once; if needed, re-prompts the same persistent session
- `assets/default-continue-prompt.txt`
  - default continue/keep-working prompt

Use these as a base, not as a finished production controller.

## Minimal usage

```bash
# 1. Ensure the persistent session exists
bash skills/opencode-continuous-supervisor/scripts/opencode-sessionctl.sh ensure /path/to/project oc-opencode-demo

# 2. Inspect health and freshness
python3 skills/opencode-continuous-supervisor/scripts/opencode-watchdog.py /path/to/project oc-opencode-demo

# 3. If needed, auto-reprompt the same session once
bash skills/opencode-continuous-supervisor/scripts/opencode-supervise-once.sh /path/to/project oc-opencode-demo
```

## Files to create when implementing further

A stronger implementation usually still needs:
- one acceptance-criteria definition per workflow family
- one registry mapping repo -> primary session
- one scheduler / recurring trigger for the watchdog
- optional notification/report layer

## If asked to implement further

When the user asks to actually build this system deeper:
1. Inspect the current bot runtime mode first
2. Verify whether chat binding is already disabled
3. Inspect task/session truth sources before proposing cron logic
4. Reuse existing persistent session if possible
5. Build watchdog around task/session state, not file mtimes
6. Keep user-facing chat separate from worker session routing unless explicitly requested
