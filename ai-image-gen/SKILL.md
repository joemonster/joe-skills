---
name: ai-image-gen
description: This skill should be used when the user asks to "generate an image", "create a picture", "make an illustration", "wygeneruj obrazek", "stwórz grafikę", "zrób infografikę", or mentions AI image generation in any context.
---

# AI Image Generation Skill

Generate images via the CDN API and download them to the local machine.

## API Reference

- **Endpoint:** `POST https://my-cdn-api.literalnie.workers.dev/api/images/aigenerate`
- **Auth:** `Bearer <cdn_api_key>` (from `~/.claude/skills/joe-config.json` or `CDN_API_KEY` env var)
- **Always set** `ephemeral: true` — generated images are temporary and will be auto-deleted from the CDN.

## Models

### Default models (auto-selected)

| Model ID | Engine | Speed | Source Image | Notes |
|---|---|---|---|---|
| `nano-banana` | Gemini 2.5 Flash | ~10s | Yes | **DEFAULT** — fast, multimodal |
| `nano-banana-pro` | Gemini 3 Pro | ~28s | Yes | Best quality, use for high-quality requests |
| `flux-schnell` | Flux Schnell | ~5s | No | **SZYBKI** — fastest, cheapest, good for drafts |

### All available models

Show this list when user asks for "all models", "lista modeli", "available models".

| Model ID | Engine (Vercel slug) | Speed | Source Image | Price/img | Notes |
|---|---|---|---|---|---|
| `nano-banana` | google/gemini-2.5-flash-image | ~10s | Yes | ~$0.003 | **DEFAULT** — fast, multimodal |
| `nano-banana-pro` | google/gemini-3-pro-image | ~28s | Yes | ~$0.01 | Best quality Google, infographics |
| `imagen` | google/imagen-4.0-generate | ~10s | No | ~$0.02 | Image-only, clean output |
| `flux` | bfl/flux-2-pro | ~12s | No | ~$0.03 | Photorealism, great quality/price |
| `flux-schnell` | prodia/flux-fast-schnell | ~5s | No | ~$0.003 | Fastest, cheapest, drafts |
| `gpt-image-low` | openai/gpt-image-1.5 (low) | ~30s | No | ~$0.009 | GPT Image budget |
| `gpt-image-medium` | openai/gpt-image-1.5 (medium) | ~60s | No | ~$0.034 | GPT Image balanced |
| `gpt-image-high` | openai/gpt-image-1.5 (high) | ~90s | No | ~$0.13 | Best text rendering on images |
| `recraft` | recraft/recraft-v4 | ~45s | No | ~$0.04 | Typography, graphic design |
| `recraft-pro` | recraft/recraft-v4-pro | ~60s | No | ~$0.08 | Highest resolution Recraft |

## Aspect Ratio

Default: `4:3`. Do **not** send aspect_ratio when editing a source image (--source).

| Value | Use case |
|---|---|
| `4:3` | **DEFAULT** — standard article image |
| `16:9` | Desktop wallpaper, banner, header |
| `9:16` | Rolki, Stories, telefon (pionowy) |
| `3:4` | Pionowy, portret |
| `1:1` | Kwadrat, social media avatar |

Trigger words: "szeroki"/"wide"/"banner"/"desktop" → `16:9`, "pionowy"/"vertical"/"story"/"rolka" → `9:16`, "kwadrat"/"square" → `1:1`, "portret" → `3:4`.

## Model Selection Rules

Use `nano-banana` (default) unless any of the following apply:

- **"szybko"/"draft"/"szkic"/"quick"** → use `flux-schnell`
- **"wysoka jakość"/"high quality"/"dobry obrazek"/infographic** → use `nano-banana-pro`
- **User wants to edit/translate text on an existing image** → use `nano-banana-pro` (source image support)
- **User explicitly names a model** (e.g. "użyj recraft", "flux pro", "gpt image") → use that model

## Language

By default, any text rendered on the generated image (labels, titles, captions, infographic text, etc.) **must be in Polish**, unless the user explicitly requests another language. When writing the prompt, instruct the model accordingly — e.g. include "all text in Polish" or "napisy po polsku" in the prompt.

## Workflow

1. Determine the model based on the user's request (see rules above).
2. Build the prompt from the user's description. Ensure any visible text on the image is in Polish (unless told otherwise).
3. Call the API using `scripts/generate.sh` (see below) or an equivalent curl command.
4. Parse the JSON response to extract `images[].url`.
5. Download each image URL to the current working directory.
6. Report the downloaded file paths to the user.

## Using the Script

The helper script at `.claude/skills/ai-image-gen/scripts/generate.sh` wraps the full flow:

```bash
# Basic generation (default model: nano-banana)
bash .claude/skills/ai-image-gen/scripts/generate.sh --prompt "a cat wearing sunglasses"

# Quick draft with flux-schnell
bash .claude/skills/ai-image-gen/scripts/generate.sh --model flux-schnell --prompt "watercolor landscape"

# Wide banner (16:9)
bash .claude/skills/ai-image-gen/scripts/generate.sh --prompt "mountain panorama" --ar 16:9

# Vertical story (9:16)
bash .claude/skills/ai-image-gen/scripts/generate.sh --prompt "portrait of a cat" --ar 9:16

# High quality with nano-banana-pro
bash .claude/skills/ai-image-gen/scripts/generate.sh --model nano-banana-pro --prompt "detailed infographic about cloud computing"

# With a local source image (multipart upload)
bash .claude/skills/ai-image-gen/scripts/generate.sh --model nano-banana-pro --prompt "translate all text to Polish" --source ./screenshot.png

# Multiple images
bash .claude/skills/ai-image-gen/scripts/generate.sh --prompt "watercolor landscape" --n 2

# Custom output directory
bash .claude/skills/ai-image-gen/scripts/generate.sh --prompt "logo design" --output-dir ./generated
```

### Script Arguments

| Arg | Required | Default | Description |
|---|---|---|---|
| `--prompt` | Yes | — | Image generation prompt |
| `--model` | No | `nano-banana` | Model ID (see table above) |
| `--source` | No | — | Path to local source image (enables multipart mode, no AR) |
| `--ar` | No | — | Aspect ratio: `4:3`, `16:9`, `9:16`, `3:4`, `1:1`. Not sent with --source |
| `--n` | No | 1 | Number of images to generate |
| `--output-dir` | No | `.` (cwd) | Directory to save downloaded images |

### Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success — images downloaded |
| 1 | API error — check response message |
| 2 | Download error — API succeeded but image download failed |

## API Request Formats

### JSON mode (no source image)

```bash
curl -s -X POST "https://my-cdn-api.literalnie.workers.dev/api/images/aigenerate" \
  -H "Authorization: Bearer $CDN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cat wearing sunglasses",
    "model": "nano-banana",
    "n": 1,
    "ephemeral": true,
    "options": {
      "aspect_ratio": "4:3"
    }
  }'
```

### Multipart mode (with local source image)

```bash
curl -s -X POST "https://my-cdn-api.literalnie.workers.dev/api/images/aigenerate" \
  -H "Authorization: Bearer $CDN_API_KEY" \
  -F "prompt=translate all text to Polish" \
  -F "model=nano-banana-pro" \
  -F "n=1" \
  -F "ephemeral=true" \
  -F "source_image=@./screenshot.png"
```

### With source image URL (JSON mode)

```bash
curl -s -X POST "https://my-cdn-api.literalnie.workers.dev/api/images/aigenerate" \
  -H "Authorization: Bearer $CDN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "translate all text to Polish",
    "model": "nano-banana-pro",
    "source_image_url": "https://example.com/image.png",
    "n": 1,
    "ephemeral": true
  }'
```

## Response Format

```json
{
  "status": "completed",
  "images": [
    {
      "url": "https://my-cdn-api.literalnie.workers.dev/ai-gen/2026-02-18/nb-87d6e5da-498.png",
      "expires_at": "2026-02-19T15:25:47.003Z"
    }
  ],
  "model_used": "google/gemini-2.5-flash-image",
  "ephemeral": true,
  "duration_ms": 11411
}
```

## Error Handling

On failure the API returns:

```json
{
  "success": false,
  "error": "Error message here",
  "code": "ERROR_CODE"
}
```

When an error occurs:
1. Show the error code and message to the user.
2. If it's a model-specific error, suggest trying a different model.
3. If it's a rate limit or timeout, wait a moment and retry once.
