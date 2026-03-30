#!/usr/bin/env bash
set -euo pipefail

API_URL="https://my-cdn-api.literalnie.workers.dev/api/images/aigenerate"
CONFIG_PATH="$HOME/.claude/skills/joe-config.json"

# Read API key from joe-config.json or env
if [[ -n "${CDN_API_KEY:-}" ]]; then
  API_KEY="$CDN_API_KEY"
elif [[ -f "$CONFIG_PATH" ]]; then
  API_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_PATH')).get('cdn_api_key',''))" 2>/dev/null || echo "")
  if [[ -z "$API_KEY" ]]; then
    echo "Error: cdn_api_key not found in $CONFIG_PATH" >&2
    exit 1
  fi
else
  echo "Error: No CDN API key. Set CDN_API_KEY env var or add cdn_api_key to $CONFIG_PATH" >&2
  exit 1
fi

# Defaults
MODEL="nano-banana"
PROMPT=""
SOURCE=""
AR=""
N=1
OUTPUT_DIR="."

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)   MODEL="$2";      shift 2 ;;
    --prompt)  PROMPT="$2";     shift 2 ;;
    --source)  SOURCE="$2";     shift 2 ;;
    --ar)      AR="$2";         shift 2 ;;
    --n)       N="$2";          shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "Error: --prompt is required" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Make API call
if [[ -n "$SOURCE" ]]; then
  # Multipart mode (local source image)
  if [[ ! -f "$SOURCE" ]]; then
    echo "Error: source file not found: $SOURCE" >&2
    exit 1
  fi
  RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $API_KEY" \
    -F "prompt=$PROMPT" \
    -F "model=$MODEL" \
    -F "n=$N" \
    -F "ephemeral=true" \
    -F "source_image=@$SOURCE")
  # Note: no aspect_ratio in source image mode
else
  # JSON mode
  if [[ -n "$AR" ]]; then
    BODY=$(printf '{"prompt":"%s","model":"%s","n":%d,"ephemeral":true,"options":{"aspect_ratio":"%s"}}' \
      "$(echo "$PROMPT" | sed 's/"/\\"/g')" "$MODEL" "$N" "$AR")
  else
    BODY=$(printf '{"prompt":"%s","model":"%s","n":%d,"ephemeral":true}' \
      "$(echo "$PROMPT" | sed 's/"/\\"/g')" "$MODEL" "$N")
  fi
  RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY")
fi

# Check for API error — API returns "status":"completed" on success
STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | sed 's/"status":"//;s/"$//')
if [[ "$STATUS" != "completed" ]]; then
  ERROR_MSG=$(echo "$RESPONSE" | grep -o '"error":"[^"]*"' | head -1 | sed 's/"error":"//;s/"$//')
  ERROR_CODE=$(echo "$RESPONSE" | grep -o '"code":"[^"]*"' | head -1 | sed 's/"code":"//;s/"$//')
  echo "API Error [${ERROR_CODE:-unknown}]: ${ERROR_MSG:-unknown error}" >&2
  echo "Full response: $RESPONSE" >&2
  exit 1
fi

# Extract image URLs and download
URLS=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | sed 's/"url":"//;s/"$//')
if [[ -z "$URLS" ]]; then
  echo "Error: no image URLs in response" >&2
  echo "Full response: $RESPONSE" >&2
  exit 1
fi

DOWNLOAD_ERRORS=0
INDEX=0
while IFS= read -r URL; do
  # Extract filename from URL
  FILENAME=$(basename "$URL")
  DEST="$OUTPUT_DIR/$FILENAME"

  if curl -s -o "$DEST" "$URL"; then
    echo "$DEST"
  else
    echo "Error: failed to download $URL" >&2
    DOWNLOAD_ERRORS=$((DOWNLOAD_ERRORS + 1))
  fi
  INDEX=$((INDEX + 1))
done <<< "$URLS"

if [[ $DOWNLOAD_ERRORS -gt 0 ]]; then
  exit 2
fi

exit 0
