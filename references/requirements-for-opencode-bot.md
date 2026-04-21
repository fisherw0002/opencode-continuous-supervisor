# Requirements Document: opencode-continuous-supervisor Skill

## Objective:
To create a robust, non-chat-bound, persistent execution loop for OpenCode/ACP tasks, ensuring continuous operation until explicit acceptance criteria are met or a maximum number of cycles is reached. This skill aims to replace ad-hoc session management with a reliable supervisory layer.

## Core Functionality:
The skill must orchestrate OpenCode sessions to perform tasks, monitor their progress, and decide whether to continue, reprompt, revive, or stop the session based on multiple truth sources.

## Key Components:
*   **Session Controller (`opencode-sessionctl.sh`):** Manages session lifecycle (ensure, prompt, status, etc.).
*   **Session Registry (`opencode-session-registry.py`):** Maps project directories to persistent session names for reuse.
*   **Watchdog (`opencode-watchdog.py`):** Monitors session health, recent history, and integrates `openclaw tasks` output for runtime liveness.
*   **Acceptance Checker (`opencode-acceptance-check.py`):** Evaluates workflow-specific criteria (files, commands, text content) to determine task completion.
*   **Unified Decider (`opencode-unified-decider.py`):** Merges signals from watchdog, acceptance, and task summary to produce a final action (`stop`, `wait`, `reprompt`, `revive`).
*   **Supervisor Once (`opencode-supervise-once.sh`):** Executes a single cycle of watchdog, acceptance check, and decision making, potentially sending a prompt.
*   **Supervisor Loop (`opencode-supervise-loop.sh`):** Repeatedly runs `supervise-once.sh` with configurable intervals and cycle limits until a `stop` action is decided or max cycles are reached.

## Decision Matrix:
The supervisor must adhere to the following logic:
*   **Acceptance Met (`accepted: true`):** Immediately `stop`.
*   **Session Dead (`session_status: dead`) AND Not Accepted:** `revive`.
*   **Lifecycle Stalled/Waiting (`lifecycle: stalled` or `waiting_bootstrap`):** `reprompt`.
*   **Stale Tasks:** If `taskSummary` indicates stale running tasks beyond `TASK_STALE_THRESHOLD`, `reprompt`.
*   **Default:** `wait` (continue observing).

## Truth Sources:
The supervisor should primarily rely on:
*   `openclaw tasks list --status running --json` for task ledger information.
*   Session status and history (`acpx opencode status`, `acpx opencode sessions read`).
*   Explicit acceptance criteria defined in JSON files.

## Key Constraints:
*   **Non-chat-bound:** Must not bind the user's chat session to the OpenCode worker.
*   **Persistence:** Prefer reusing existing sessions via the registry.
*   **Continuous Activation:** Must automatically continue or revive tasks until acceptance or max cycles.
*   **Clear Acceptance:** Must use explicit criteria to determine task completion.

## Testing Plan:
小弟 should execute the following tests using the skill's scripts:

1.  **Unit Tests:**
    *   Verify `opencode-unified-decider.py` correctly implements the decision matrix with various inputs (provided in `test_decider.py`).
    *   Test `opencode-acceptance-check.py` against different criteria files (`example-acceptance-criteria.json`, `otp-reader-helper-acceptance.json`).

2.  **Integration Tests:**
    *   Run `opencode-supervise-once.sh` with a project that meets acceptance criteria (e.g., `otp-reader-helper` with its acceptance file) to confirm it outputs `action: stop`.
    *   Run `opencode-supervise-loop.sh` with a project that meets acceptance criteria to confirm it stops appropriately.
    *   Run `opencode-supervise-loop.sh` with a project that *does not* meet acceptance criteria (or simulates failure) to confirm it continues, reprompts, or revives as per the decider's logic. Test `MAX_CYCLES` and `INTERVAL_SECONDS`.
    *   Test session registry: ensure correct session names are generated/retrieved, and reuse works.
    *   Simulate session dead states and verify `revive` action.
    *   Simulate stalled/waiting states and verify `reprompt` action.
    *   Simulate stale tasks and verify their impact on decisions.

3.  **Agent Integration:**
    *   Modify 小弟's AGENTS.md and SOUL.md to correctly dispatch long tasks to `opencode-supervise-loop.sh` or `opencode-supervise-once.sh` via the skill's path.
    *   Ensure the `tasklen:long` button correctly triggers the supervisor flow.
    *   Verify that the agent correctly interprets the supervisor's final action (`stop`, `wait`, etc.) and reports to the user.

## Modification Plan:
*   If tests reveal bugs or areas for improvement, modify the skill scripts (`.py`, `.sh`) and documentation files (`.md`, `.json`) accordingly.
*   Ensure all changes are committed to the respective Git repositories (workspace for the skill, opencode-bot/brain for agent configuration).
