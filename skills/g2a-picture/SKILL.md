---
name: g2a-picture
description: Generate an image via the user’s G2A OpenAI-compatible API (g2a.fisht.cc.cd). Use when the user explicitly wants G2A for an image or uses /p. This skill only supports image generation; video is not available on the current g2a service.
---

# G2A Picture

Generate an image via G2A's OpenAI-compatible API at `https://g2a.fisht.cc.cd/v1`.

## Usage

Use the `image_generate` tool directly:

```
action: generate
prompt: <描述>
model: openai/grok-imagine-image-lite
size: 1024x1024 (or 1024x1536, 1536x1024)
aspectRatio: 1:1 (or 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9)
```

The `openai` provider is pre-configured to route to `https://g2a.fisht.cc.cd/v1` with the correct API key — no extra env vars needed.

## Model

- Primary: `openai/grok-imagine-image-lite`
- This is the only confirmed working image model on the current g2a service.

## Notes

- Do **not** use the legacy `g2a_picture.py` script for image generation; use `image_generate` tool instead.
- The script is retained only for backwards compatibility reference.
- If `image_generate` fails, fall back to running the script directly and attach the resulting file.
- Video generation is not available on the current g2a service.
