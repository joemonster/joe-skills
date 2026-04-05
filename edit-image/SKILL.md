---
name: edit-image
description: Use when the user wants to edit, convert, resize, crop images, check image dimensions/info, or remove watermarks. Trigger phrases include "convert to jpg/png/webp", "resize image", "crop image", "image info", "zmień format", "przeskaluj", "przytnij", "wymiary obrazka", "zrób z tego jpg", "make this a png", "remove watermark", "usuń watermark", "usuń znak wodny", or any request involving image format conversion, resizing, cropping, or watermark removal. Also trigger when user says "edit-image" directly.
---

# Edit Image

Edit images locally using Python's Pillow library and OpenCV. Handles format conversion, resize, crop, dimension info, and watermark removal.

## Setup

Before running any image operation, ensure Pillow is installed:

```bash
pip install Pillow 2>/dev/null || pip install Pillow
```

Run this silently at the start — don't ask the user. If already installed, pip will skip it.

For watermark removal, also install OpenCV (only when needed):

```bash
pip install opencv-python 2>/dev/null || pip install opencv-python
```

## Operations

### 1. Convert Format

Change image format. Supported: **JPG, PNG, GIF, WEBP**.

- JPG output uses **quality=70** by default (user can override)
- When converting to JPG, convert RGBA → RGB first (JPG doesn't support transparency)
- Output file: same name, new extension, same directory (unless user specifies otherwise)
- For batch: support glob patterns (`*.png`, `folder/*.webp`)

```python
from PIL import Image
import glob, os

files = glob.glob("pattern")  # e.g. "*.png" or single file
for f in files:
    img = Image.open(f)
    out = os.path.splitext(f)[0] + ".jpg"
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(out, quality=70)
    print(f"{f} → {out}")
```

### 2. Resize

Resize to exact dimensions or by scale.

- `800x600` → exact size (may distort if aspect ratio differs)
- `800x` or `x600` → scale preserving aspect ratio
- `50%` → scale by percentage

```python
from PIL import Image

img = Image.open("photo.jpg")
# Exact: img.resize((800, 600))
# Fit within bounds, keep aspect ratio:
# img.thumbnail((800, 600))
img_resized = img.resize((800, 600))
img_resized.save("photo_800x600.jpg", quality=70)
```

When only width or height is given, calculate the other from original aspect ratio. Use `Image.LANCZOS` for downscaling quality.

Output filename: append dimensions before extension, e.g. `photo_800x600.jpg`. Or overwrite original if user says so.

### 3. Crop

Crop to a box defined as `left,top,right,bottom` (pixels).

```python
from PIL import Image

img = Image.open("photo.jpg")
cropped = img.crop((100, 100, 500, 400))  # (left, top, right, bottom)
cropped.save("photo_cropped.jpg", quality=70)
```

Output filename: append `_cropped` before extension. Or overwrite if user requests.

### 4. Info / Dimensions

Show image metadata: dimensions, format, color mode, file size.

```python
from PIL import Image
import os

img = Image.open("photo.jpg")
size_kb = os.path.getsize("photo.jpg") / 1024
print(f"File: photo.jpg")
print(f"Dimensions: {img.width} x {img.height}")
print(f"Format: {img.format}")
print(f"Mode: {img.mode}")
print(f"File size: {size_kb:.1f} KB")
```

### 5. Remove Watermark

Remove small watermarks from images using OpenCV inpainting (TELEA algorithm). Creates a mask over the watermark area and fills it from surrounding pixels.

Requires: `opencv-python` (installed in Setup).

#### How it works

1. Calculate watermark position and size (scale proportionally if image wider than reference)
2. Create a binary mask: black everywhere, white rectangle over the watermark
3. Run `cv2.inpaint()` with TELEA algorithm
4. Save result

```python
import cv2
import numpy as np
import glob, os

# --- Config ---
PRESET = "notebooklm"  # see presets below
files = glob.glob("*.png")  # or single file
output_format = ".jpg"
jpg_quality = 70

# --- Presets ---
PRESETS = {
    "notebooklm": {
        "ref_width": 1376,      # reference image width for base measurements
        "wm_size": (97, 11),    # watermark width x height at ref_width
        "edge_margin": 10,      # px from right and bottom edge at ref_width
        "position": "bottom-right",
    },
}

preset = PRESETS[PRESET]
ref_w = preset["ref_width"]
base_wm_w, base_wm_h = preset["wm_size"]
base_edge = preset["edge_margin"]

for f in files:
    img = cv2.imread(f)
    h, w = img.shape[:2]

    # Scale watermark proportionally to image width
    scale = w / ref_w
    wm_w = int(base_wm_w * scale)
    wm_h = int(base_wm_h * scale)
    edge = int(base_edge * scale)
    pad = 2  # small padding around watermark

    # Mask position (bottom-right)
    mask = np.zeros((h, w), dtype=np.uint8)
    x1 = w - edge - wm_w - pad
    y1 = h - edge - wm_h - pad
    x2 = w - edge + pad
    y2 = h - edge + pad
    mask[y1:y2, x1:x2] = 255

    result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

    out = os.path.splitext(f)[0] + "_clean" + output_format
    if output_format == ".jpg":
        cv2.imwrite(out, result, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality])
    else:
        cv2.imwrite(out, result)
    print(f"{f} → {out}")
```

#### Watermark Presets

| Preset | Source | Size (at ref) | Position | Edge margin |
|--------|--------|---------------|----------|-------------|
| `notebooklm` | NotebookLM generated images | 97×11 px @ 1376w | bottom-right | 10 px |

To add a new preset: measure the watermark size and edge margin at a known image width, then add to PRESETS dict.

#### Tuning Parameters

| Parameter | Effect | Recommended |
|-----------|--------|-------------|
| `radius` (inpaint) | Higher = smoother but more blur | **3** for small watermarks |
| `pad` (mask padding) | Extra px around watermark | **2** for tight fit |
| `scale` | Auto-scales mask for larger images | Automatic from `ref_width` |

For complex/textured backgrounds: try `radius=5`. For clean/solid backgrounds: `radius=3` is enough.

#### Usage patterns

- Single file: `remove watermark from photo.png` (auto-detects preset if not specified)
- Batch: `remove notebooklm watermark from *.png`
- Custom position: if watermark is not in a preset, user provides size and position manually
- Output: `_clean` suffix by default, JPG 70% quality

## Defaults

| Setting | Default | Override |
|---------|---------|---------|
| JPG quality | 70 | "quality 90", "jakość 85" |
| Output location | Same directory as source | User specifies path |
| Output naming | `name_WxH.ext` or `name_cropped.ext` | User specifies |
| Overwrite original | No | "overwrite", "nadpisz" |

## Behavior

- Generate a Python script and run it via Bash. Keep scripts short and inline — no need to save script files unless the operation is complex.
- Always print what was done: input file → output file, new dimensions, file size.
- For batch operations, show a summary at the end (N files processed).
- If a file doesn't exist, report clearly and continue with remaining files.
- For GIF files: preserve animation when converting between GIF and WEBP. For resize/crop of animated GIFs, process all frames.
