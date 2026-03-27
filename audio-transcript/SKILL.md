---
name: audio-transcript
description: "Use when user has an audio file to transcribe, wants to know what was said in a recording, needs a written version of a conversation, meeting, interview, podcast, or lecture. Triggers on any audio processing request involving mp3, m4a, wav, flac, ogg files. Also use when user says: transkrypcja, transcribe, transcript, spisz nagranie, przetwórz audio, kto co mówił, podział na głosy, rozpoznawanie mowy, speaker diarization, zrób tekst z nagrania, odsłuchaj plik."
---

# Audio Transcript (Gemini 3 Flash)

Transcribes audio files with speaker diarization and timestamps using Gemini 3 Flash.

## When to Use

- User has an audio file (mp3, m4a, wav, flac, ogg) to transcribe
- Need speaker separation (who said what)
- Need timestamps per utterance

## How to Use

```bash
python ~/.claude/skills/audio-transcript/scripts/transcribe.py "path/to/audio.mp3"

# Polish audio, 2 speakers
python ~/.claude/skills/audio-transcript/scripts/transcribe.py recording.mp3 --lang pl --speakers 2

# Custom output path
python ~/.claude/skills/audio-transcript/scripts/transcribe.py lecture.wav -o notes.txt
```

| Option | Flag | Example |
|--------|------|---------|
| Language | `--lang` | `--lang pl` |
| Speaker count | `--speakers` | `--speakers 3` |
| Custom output | `-o` | `-o result.txt` |

Shows token usage and cost after each transcription.

## Configuration

API key via `GEMINI_API_KEY` env var or `gemini_api_key` in `~/.claude/skills/joe-config.json`.
