---
name: g2a-video
description: Generate a video via the user’s G2A OpenAI-compatible API (g2.fisht.cc.cd). Use when the user explicitly wants G2A for a video or uses /v.
---

# G2A Video

Use:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-video/scripts/g2a_video.py`

Current routing expectations:

- video generation uses `grok-imagine-1.0-video`
- requests may fail with outer `500` while the inner error body contains the real upstream cause

Prefer sending the generated video as a real attachment, not a bare link.
