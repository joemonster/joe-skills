---
name: audio-transcript
description: "Use when user has an audio file to transcribe, wants to know what was said in a recording, needs a written version of a conversation, meeting, interview, podcast, or lecture. Also use when user provides a URL (YouTube, Twitter/X, Vimeo, etc.) and wants a transcript — the skill downloads audio automatically. Triggers on any audio processing request involving mp3, m4a, wav, flac, ogg files or video URLs. Also use when user says: transkrypcja, transcribe, transcript, spisz nagranie, przetwórz audio, kto co mówił, podział na głosy, rozpoznawanie mowy, speaker diarization, zrób tekst z nagrania, odsłuchaj plik, transkrybuj ten film, co mówią na tym filmie."
---

# Audio Transcript (Gemini Flash)

Transcribes audio files or video URLs with speaker diarization and timestamps using Gemini Flash. For URLs (YouTube, Twitter/X, etc.) automatically downloads audio as mp3 via yt-dlp. Automatically splits large files (>100 MB or >9.5h) into chunks.

## When to Use

- User has an audio file (mp3, m4a, wav, flac, ogg) to transcribe
- User provides a URL (YouTube, YT Shorts, Twitter/X, Vimeo, etc.) and wants a transcript
- Need speaker separation (who said what)
- Need timestamps per utterance

## How to Use

```bash
# Local file
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "path/to/audio.mp3"

# YouTube URL — downloads mp3 automatically
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "https://www.youtube.com/watch?v=abc123"

# Twitter/X URL
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "https://x.com/user/status/123456"

# YT Shorts
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "https://youtube.com/shorts/abc123"

# Polish audio, 2 speakers
python ~/.claude/skills/audio-transcript/scripts/transcribe.py recording.mp3 --lang pl --speakers 2

# Plain text — no timestamps, no speaker labels, just paragraphs
python ~/.claude/skills/audio-transcript/scripts/transcribe.py recording.mp3 --plain

# Cheaper model (half price on audio)
python ~/.claude/skills/audio-transcript/scripts/transcribe.py recording.mp3 --model gemini-3.1-flash-lite-preview

# Custom output path
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "https://youtube.com/watch?v=xyz" -o notes.txt
```

| Option | Flag | Default | Example |
|--------|------|---------|---------|
| Language | `--lang` | `pl` | `--lang en`, `--lang original` |
| Speaker count | `--speakers` | auto | `--speakers 3` |
| Plain text | `--plain` | off | `--plain` (no timestamps/diarization) |
| Model | `--model` | `gemini-2.5-flash` | `--model gemini-3.1-flash-lite-preview` |
| Custom output | `-o` | `~/Downloads/` | `-o result.txt` |

## Models

| Model | Audio in/1M | Output/1M | Notes |
|-------|-------------|-----------|-------|
| `gemini-2.5-flash` | $1.00 | $2.50 | **Default.** GA, reliable |
| `gemini-3-flash-preview` | $1.00 | $3.00 | Preview, newest |
| `gemini-3.1-flash-lite-preview` | $0.50 | $1.50 | **Cheapest.** Half price on audio |

## Large Files

Files over 100 MB or 9.5 hours are automatically split into chunks, transcribed separately, and merged. The script:
1. Detects file size and duration
2. Splits into chunks (~90 MB / ~20 min each) as mono 96kbps MP3
3. Uploads and transcribes each chunk with retry on empty responses
4. Merges results and cleans up temp files

For very large files (e.g. 1h+ video), consider extracting audio first as mono 96kbps MP3 to reduce upload size:
```bash
ffmpeg -i video.mp4 -vn -ac 1 -ab 96k -ar 44100 audio.mp3
```

Output defaults to `~/Downloads/`. Plain mode saves as `.md`, diarization mode as `.txt`.

## Requirements

- `yt-dlp` — for URL downloads (`pip install yt-dlp`)
- `ffmpeg` — for mp3 conversion (optional but recommended)

## Configuration

API key in `~/.claude/skills/audio-transcript/scripts/config.json` (`gemini_api_key`) or `GEMINI_API_KEY` env var.
