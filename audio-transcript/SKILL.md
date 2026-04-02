---
name: audio-transcript
description: "Use when user has an audio file to transcribe, wants to know what was said in a recording, needs a written version of a conversation, meeting, interview, podcast, or lecture. Also use when user provides a URL (YouTube, Twitter/X, Vimeo, etc.) and wants a transcript — the skill downloads audio automatically. Triggers on any audio processing request involving mp3, m4a, wav, flac, ogg files or video URLs. Also use when user says: transkrypcja, transcribe, transcript, spisz nagranie, przetwórz audio, kto co mówił, podział na głosy, rozpoznawanie mowy, speaker diarization, zrób tekst z nagrania, odsłuchaj plik, transkrybuj ten film, co mówią na tym filmie."
---

# Audio Transcript (Gemini 3 Flash)

Transcribes audio files or video URLs with speaker diarization and timestamps using Gemini 3 Flash. For URLs (YouTube, Twitter/X, etc.) automatically downloads audio as mp3 via yt-dlp.

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

# Custom output path
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "https://youtube.com/watch?v=xyz" -o notes.txt
```

| Option | Flag | Example |
|--------|------|---------|
| Language | `--lang` | `--lang en` (default: pl, use `original` to keep source) |
| Speaker count | `--speakers` | `--speakers 3` |
| Custom output | `-o` | `-o result.txt` |

Output defaults to `~/Downloads/`. Temp audio files are cleaned up automatically.

## Requirements

- `yt-dlp` — for URL downloads (`pip install yt-dlp`)
- `ffmpeg` — for mp3 conversion (optional but recommended)

## Configuration

API key in `~/.claude/skills/audio-transcript/scripts/config.json` (`gemini_api_key`) or `GEMINI_API_KEY` env var.
