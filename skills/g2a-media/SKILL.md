---
name: g2a-media
description: Generate images or videos via the user’s G2A OpenAI-compatible API (g2.fisht.cc.cd). Use when the user explicitly wants G2A, asks to use /p or /v, or asks to test the G2A image/video capability.
---

# G2A Media

Use the bundled scripts to call G2A directly.

## Important current behavior

- G2A is a Grok2API-style gateway at `http://127.0.0.1:8011/v1`.
- Current model routing is narrow:
  - image generation requires `grok-imagine-1.0`
  - image edit should use `grok-imagine-1.0-edit`
  - video generation uses `grok-imagine-1.0-video`
- If the upstream is unhealthy, the API may return `500` while the inner error body reveals the real cause (for example upstream `403` or token/session issues).
- Always inspect and surface the actual error body before concluding the root cause.

## Paths

Use workspace-local scripts, not `/root/skills/...`:

- image: `/root/.openclaw/workspace/skills/g2a-media/scripts/g2a_image.py`
- video: `/root/.openclaw/workspace/skills/g2a-media/scripts/g2a_video.py`

## Image

Run:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-media/scripts/g2a_image.py`

Optional env:

- `G2A_BASE_URL` default `http://127.0.0.1:8011/v1`
- `G2A_SIZE` default `1024x1024`
- `G2A_IMAGE_MODEL` default `grok-imagine-1.0`

The script writes a downloaded file path to stdout.

## Video

Run:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-media/scripts/g2a_video.py`

Optional env:

- `G2A_BASE_URL` default `http://127.0.0.1:8011/v1`
- `G2A_ASPECT` default `1:1`
- `G2A_LEN` default `6`
- `G2A_RES` default `HD`
- `G2A_PRESET` default `normal`
- `G2A_VIDEO_MODEL` default `grok-imagine-1.0-video`

## Delivery

- Prefer sending real image/video attachments back to the user.
- If generation fails, report the actual upstream error body rather than only the outer HTTP status.
