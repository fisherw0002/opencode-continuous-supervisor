---
name: q2a
description: Generate images and videos through the user's Qwen2API deployment. Use when the user asks to 生图, 生成图片, 出图, 改图, 生视频, 生成视频, 图生视频, or explicitly mentions Qwen2API / q2a / qwen 图视频. Prefer this skill when built-in image/video tools are incompatible with the user's Qwen2API bridge and you need the native Qwen2API endpoints.
---

# q2a

Use Qwen2API native endpoints instead of relying on OpenClaw's generic media provider wrappers.

## Quick path

- For **text-to-image**, run:
  - `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py image --prompt '<prompt>' --size 1024x1536`
- For **text-to-video**, run:
  - `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py video --prompt '<prompt>' --size 1024x1792`
- For **image-to-video**, run:
  - `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py video --prompt '<prompt>' --image '/abs/path/to/image.png' --size 1024x1792`

The script prints JSON. For images, read `data[0].url` or `data[0].b64_json`. For image-to-video, read top-level `url`.

## Defaults

- Base URL: `http://38.14.196.84:3000/v1`
- Image model: `Qwen3.6-Plus-image`
- Video model: `Qwen3.6-Plus-video`
- Override with env vars if needed:
  - `Q2A_BASE_URL`
  - `Q2A_API_KEY`
  - `Q2A_IMAGE_MODEL`
  - `Q2A_VIDEO_MODEL`

## Prompting guidance

- Keep prompts concrete.
- For video, prefer short, stable motion descriptions.
- For image-to-video, explicitly say:
  - keep framing stable
  - only slight breathing / blinking / tiny head movement
  - no camera motion unless the user asks for it

## Delivery rule

When the script returns a remote URL, reply with the media URL directly or use the proper first-class media tool only if it already supports that returned asset cleanly. Do not route the generation back through generic OpenClaw image/video wrappers once the native q2a path is chosen.
