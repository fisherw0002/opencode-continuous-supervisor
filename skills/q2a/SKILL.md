---
name: q2a
description: Generate and edit images plus generate videos through the user's Qwen2API deployment. Use when the user asks to 生图, 生成图片, 出图, 改图, 修图, 图片编辑, 生视频, 生成视频, 图生视频, or explicitly mentions Qwen2API / q2a / qwen 图视频. Prefer this skill when built-in image/video tools are incompatible with the user's Qwen2API bridge and you need the native Qwen2API endpoints.
---

# q2a

Use Qwen2API native endpoints, but prefer first-class OpenClaw media tools when they can return real media attachments cleanly.

## Quick path

### Images: prefer real image attachments

For **text-to-image** and **image edit**, prefer the first-class `image_generate` tool so the user receives a real image attachment instead of a bare link.

- Text-to-image model: `openai/Qwen3.6-Plus-image`
- Image-edit model: `openai/Qwen3.6-Plus-image-edit`

Only fall back to the script when the media tool path is unavailable or broken.

Script fallback commands:
- `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py image --prompt '<prompt>' --size 1024x1536`
- `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py edit --prompt '<prompt>' --image '/abs/path/to/image.png' --size 1024x1536`

### Videos

For videos, use the native q2a script when reliability matters, especially for image-to-video:
- `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py video --prompt '<prompt>' --size 1024x1792`
- `python3 /root/.openclaw/workspace/skills/q2a/scripts/q2a_generate.py video --prompt '<prompt>' --image '/abs/path/to/image.png' --size 1024x1792`

The script prints JSON.

- For image generation / edit fallback, read `data[0].url` or `data[0].b64_json`.
- For image-to-video, read top-level `url`.
- For text-to-video, read the returned JSON `data[0].url`.

## Defaults

- Base URL: `http://38.14.196.84:3000/v1`
- Image model: `Qwen3.6-Plus-image`
- Image edit model: `Qwen3.6-Plus-image-edit`
- Video model: `Qwen3.6-Plus-video`
- Override with env vars if needed:
  - `Q2A_BASE_URL`
  - `Q2A_API_KEY`
  - `Q2A_IMAGE_MODEL`
  - `Q2A_IMAGE_EDIT_MODEL`
  - `Q2A_VIDEO_MODEL`

## Prompting guidance

- Keep prompts concrete.
- For video, prefer short, stable motion descriptions.
- For image-to-video, explicitly say:
  - keep framing stable
  - only slight breathing / blinking / tiny head movement
  - no camera motion unless the user asks for it
- For image edit, describe only the intended change and keep the rest preserved.

## Delivery rule

- **Default user preference:** for images, send a real image message/attachment, not a bare link.
- Therefore, for image generation and image edit, prefer `image_generate` with the q2a-backed OpenAI-compatible model refs so the channel receives an actual image artifact.
- Only send a raw URL when there is no working attachment-capable path.
- For video, prefer a true video attachment path when available; otherwise send the q2a result URL as a fallback and explain briefly.
- Do not choose a bare-link reply for images when a real image attachment path works.
