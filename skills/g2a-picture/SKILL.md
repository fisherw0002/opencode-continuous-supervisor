---
name: g2a-picture
description: Generate an image via the user’s G2A OpenAI-compatible API (g2.fisht.cc.cd). Use when the user explicitly wants G2A for an image or uses /p.
---

# G2A Picture

Use:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-picture/scripts/g2a_picture.py`

Current routing expectations:

- image generation requires model `grok-imagine-1.0`
- if the request fails, inspect the returned error body before concluding the cause

Prefer sending the generated image as a real attachment, not a bare link.
