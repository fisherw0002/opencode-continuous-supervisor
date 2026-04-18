---
name: g2a-media
description: Generate images or videos via the user’s G2A OpenAI-compatible API (g2a.fisht.cc.cd). Use when the user explicitly wants G2A, asks to use /p or /v, or asks to test the G2A image/video capability.
---

# G2A Media

Use the bundled scripts to call G2A directly.

## Important current behavior

- G2A currently points to `https://g2a.fisht.cc.cd/v1`.
- The scripts auto-detect usable default models from `/v1/models` instead of assuming the old `g2` model names.
- Image generation prefers:
  - `grok-imagine-image-lite`
  - `grok-imagine-image`
  - `grok-imagine-1.0`
- Video generation prefers:
  - `grok-imagine-video`
  - `grok-imagine-1.0-video`
- If no matching image or video model exists in `/v1/models`, the scripts fail with an explicit `NO_G2A_*_MODEL_AVAILABLE` message.
- Always inspect and surface the actual error body before concluding the root cause.

## Paths

Use workspace-local scripts:

- image: `/root/.openclaw/workspace/skills/g2a-media/scripts/g2a_image.py`
- video: `/root/.openclaw/workspace/skills/g2a-media/scripts/g2a_video.py`

## Image

Run:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-media/scripts/g2a_image.py`

Optional env:

- `G2A_BASE_URL` default `https://g2a.fisht.cc.cd/v1`
- `G2A_SIZE` default `1024x1024`
- `G2A_IMAGE_MODEL` optional explicit override; otherwise auto-detected from `/v1/models`

The script writes a downloaded file path to stdout.

## Video

Run:

- `G2A_PROMPT="..." python3 /root/.openclaw/workspace/skills/g2a-media/scripts/g2a_video.py`

Optional env:

- `G2A_BASE_URL` default `https://g2a.fisht.cc.cd/v1`
- `G2A_ASPECT` default `1:1`
- `G2A_LEN` default `6`
- `G2A_RES` default `HD`
- `G2A_PRESET` default `normal`
- `G2A_VIDEO_MODEL` optional explicit override; otherwise auto-detected from `/v1/models`

## Delivery

- Prefer sending real image/video attachments back to the user.
- **Critical:** when a G2A script returns a local file path (for example `/root/g2a_out/p_123.jpg` or `/root/g2a_out/v_123.mp4`), immediately attach that file in the same turn by reading the file path so the channel receives actual media. Do not send a text-only placeholder like “我把文件拿到手了” without attaching the file.
- Do not rely on the user to refresh or infer that media exists; if the media was generated locally, attach it explicitly.
- If generation fails, report the actual upstream error body rather than only the outer HTTP status.
