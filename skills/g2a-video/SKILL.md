---
name: g2a-video
description: Generate a video via the user’s G2A OpenAI-compatible API (g2a.fisht.cc.cd). Use when the user explicitly wants G2A for a video or uses /v.
---

# G2A Video

Use:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-video/scripts/g2a_video.py`

Current behavior:

- Base URL defaults to `https://g2a.fisht.cc.cd/v1`
- API key uses `G2A_API_KEY` first, then `G2AD_API_KEY`
- Video model is auto-detected from `/v1/models`
- Preferred order:
  - `grok-imagine-video`
  - `grok-imagine-1.0-video`
- If `/v1/models` exposes no video model, fail with `NO_G2A_VIDEO_MODEL_AVAILABLE` instead of guessing.

Prefer sending the generated video as a real attachment, not a bare link.
