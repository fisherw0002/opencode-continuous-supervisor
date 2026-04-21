# Decision Guide

## Choose this skill when
- OpenCode can work, but stops after one run
- bot and worker both stop without auto-resume
- user wants persistent ACP without chat binding
- user mentions controller / mission control / watchdog / continue until done

## Prefer near-term design when
- current ACP non-chat-bound flow already mostly works
- only missing piece is re-activation / supervision

## Prefer long-term design when
- user wants bot personality fully separate from worker runtime
- bot should always feel like a planner/supervisor, not an ACP shell
- session orchestration complexity is acceptable

## Required truth sources
- `openclaw tasks list/show`
- ACP stream logs
- child session health/status
- explicit acceptance criteria

## Output expectation
This skill should produce:
1. one recommended architecture
2. one minimal component list
3. one activation rule set
4. one risk list
