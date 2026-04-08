---
name: add-subtitles
description: "Use when user wants to add burned-in subtitles (napisy) to a video file or video URL. Downloads video, transcribes audio via Gemini, generates SRT, and burns subtitles with ffmpeg. Also use when user says: dodaj napisy, napisy na wideo, wpal napisy, subtitles, burn subtitles, hardcode subtitles, napisy do filmu, wgraj napisy."
---

# Add Subtitles

Burns subtitles into video files. Downloads video from URL (YouTube, Twitter/X, etc.), transcribes audio via Gemini Flash, generates SRT, and overlays subtitles using ffmpeg with `subtitles` filter.

Style: Source Code Pro font, white text on black background box (default dark). Use `--style light` for black text on white box.

## When to Use

- User wants burned-in (hardcoded) subtitles on a video
- User provides a video URL and wants a subtitled MP4
- User has a local video file and wants subtitles added

## How to Use

```bash
# URL (YouTube, Twitter/X, etc.)
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py "https://x.com/user/status/123456"

# Local video file
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py video.mp4

# Keep original language (don't translate to Polish)
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py "https://youtube.com/watch?v=abc" --lang original

# Custom output path
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py video.mp4 -o output.mp4

# Larger font
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py video.mp4 --font-size 24

# Dark style (white text on black box)
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py video.mp4 --style dark

# Only generate SRT file (no video)
python ~/.claude/skills/add-subtitles/scripts/add_subtitles.py "https://youtube.com/watch?v=abc" --srt-only
```

| Option | Flag | Default | Example |
|--------|------|---------|---------|
| Language | `--lang` | `pl` | `--lang en`, `--lang original` |
| Font size | `--font-size` | `18` | `--font-size 24` |
| Style | `--style` | `dark` | `--style light` (black on white) |
| Output path | `-o` | `~/Downloads/<title>_subtitled.mp4` | `-o result.mp4` |
| SRT only | `--srt-only` | off | `--srt-only` |

## Video Quality

Output video matches the source bitrate — the script reads the original video's bitrate via ffprobe and passes it to ffmpeg as `-b:v`. This avoids inflating or deflating file size compared to the input. If bitrate can't be detected, ffmpeg uses its default encoding.

## Requirements

- `yt-dlp` — for URL downloads (`pip install yt-dlp`)
- `ffmpeg` — with libass support (for subtitles filter)
- `google-genai` — for transcription (`pip install google-genai`)
- Font "Source Code Pro" installed on system

## Configuration

Uses the same Gemini API key as audio-transcript: `~/.claude/skills/audio-transcript/scripts/config.json` or `GEMINI_API_KEY` env var.
