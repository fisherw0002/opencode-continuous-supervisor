---
name: g2a-picture
description: Generate an image via the user’s G2A OpenAI-compatible API (g2a.fisht.cc.cd). Use when the user explicitly wants G2A for an image or uses /p. This skill only supports image generation; video is not available on the current g2a service.
---

# G2A Picture

Generate an image via G2A's OpenAI-compatible API at `https://g2a.f2a.fisht.cc.cd/v1`.

## Usage

```bash
G2A_PROMPT="描述内容" python3 /root/.openclaw/workspace/skills/g2a-picture/scripts/g2a_picture.py
```

## Optional env vars

| Variable | Default | Description |
|---|---|---|
| `G2A_BASE_URL` | `https://g2a.fisht.cc.cd/v1` | API base URL |
| `G2A_API_KEY` | _(required)_ | API key |
| `G2A_SIZE` | `1024x1024` | Image size |
| `G2A_IMAGE_MODEL` | auto-detected | Override image model |

## Model detection

The script queries `/v1/models` and picks the best available image model in this order:

1. `grok-imagine-image-lite`
2. `grok-imagine-image`
3. `grok-imagine-1.0`
4. Any other model with "image" in the ID (excluding "edit" and "video")

If no image model is found, the script exits with `NO_G2A_IMAGE_MODEL_AVAILABLE`.

## Delivery

- Always attach the generated image file in the same turn as a real media attachment.
- Do not send a text-only confirmation without attaching the file.
- If generation fails, report the actual upstream error body.
