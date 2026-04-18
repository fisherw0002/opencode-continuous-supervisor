---
name: g2a-picture
description: Generate an image via the user’s G2A OpenAI-compatible API (g2a.fisht.cc.cd). Use when the user explicitly wants G2A for an image or uses /p.
---

# G2A Picture

Use:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-picture/scripts/g2a_picture.py`

Current behavior:

- Base URL defaults to `https://g2a.fisht.cc.cd/v1`
- API key uses `G2A_API_KEY` first, then `G2AD_API_KEY`
- Image model is auto-detected from `/v1/models`
- Preferred order:
  - `grok-imagine-image-lite`
  - `grok-imagine-image`
  - `grok-imagine-1.0`

Prefer sending the generated image as a real attachment, not a bare link. If the script returns a local file path, attach that file in the same turn instead of sending a text-only confirmation.
