---
name: g2a-media
description: Generate images via the user’s G2A OpenAI-compatible API (g2a.fisht.cc.cd). Use when the user explicitly wants G2A for image generation, asks to test G2A image capability, or wants /p-style G2A pictures. This skill no longer provides video generation because the current g2a service does not expose a usable video model.
---

# G2A Media

Use the bundled script to call G2A image generation directly.

## Current behavior

- G2A currently points to `https://g2a.fisht.cc.cd/v1`.
- The script auto-detects the default image model from `/v1/models` instead of assuming the old `g2` model names.
- Preferred image models, in order:
  - `grok-imagine-image-lite`
  - `grok-imagine-image`
  - `grok-imagine-1.0`
- If no matching image model exists in `/v1/models`, fail with an explicit `NO_G2A_IMAGE_MODEL_AVAILABLE` message.
- The current g2a service does **not** expose a usable video model, so do not use this skill for video.

## Path

- image: `/root/.openclaw/workspace/skills/g2a-media/scripts/g2a_image.py`

## Image

Run:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-media/scripts/g2a_image.py`

Optional env:

- `G2A_BASE_URL` default `https://g2a.fisht.cc.cd/v1`
- `G2A_SIZE` default `1024x1024`
- `G2A_IMAGE_MODEL` optional explicit override; otherwise auto-detected from `/v1/models`

## Delivery

- Prefer sending a real image attachment back to the user.
- If the script returns a local file path, attach that file in the same turn.
- If generation fails, report the actual upstream error body rather than only the outer HTTP status.
