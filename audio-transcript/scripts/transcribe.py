#!/usr/bin/env python3
"""
Audio Transcription with Speaker Diarization via Gemini Flash.
"""

import argparse
import json
import os
import sys
from pathlib import Path


# Pricing per 1M tokens (USD) for gemini-3-flash-preview
PRICE_INPUT_AUDIO_PER_1M = 1.00
PRICE_OUTPUT_PER_1M = 3.00


def load_config():
    """Load joe-config.json from ~/.claude/skills/."""
    config_path = Path.home() / ".claude" / "skills" / "joe-config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY") or load_config().get("gemini_api_key")
    if not key:
        print("ERROR: No Gemini API key. Set GEMINI_API_KEY env var or add gemini_api_key to ~/.claude/skills/joe-config.json", file=sys.stderr)
        sys.exit(1)
    return key


def transcribe(filepath: str, api_key: str, language: str = None,
               speakers_expected: int = None) -> tuple[str, dict]:
    """Transcribe audio using Gemini Flash. Returns (text, usage_info)."""
    from google import genai

    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"Uploading {filepath.name} ({size_mb:.1f} MB)...")

    client = genai.Client(api_key=api_key)
    try:
        uploaded = client.files.upload(file=str(filepath))
    except Exception as e:
        print(f"ERROR: Upload failed: {e}", file=sys.stderr)
        sys.exit(1)
    print("Upload complete. Transcribing...")

    lang_hint = f" Language: {language}." if language else ""
    speakers_hint = f" Expected speakers: {speakers_expected}." if speakers_expected else ""

    prompt = f"""Transcribe the following audio recording.{lang_hint}{speakers_hint}

RULES:
- Output ONLY the transcription. No introduction, no commentary, no summary.
- If there is more than 1 speaker, use diarization format:
  (HH:MM:SS) A: utterance text
  (HH:MM:SS) B: utterance text
- If there is only 1 speaker, output text with timestamps every few dozen seconds:
  (HH:MM:SS) utterance text
- Start with the first word of the transcription. Add nothing else."""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, uploaded],
        )
    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract token usage
    usage = {}
    if response.usage_metadata:
        um = response.usage_metadata
        input_tokens = um.prompt_token_count or 0
        output_tokens = um.candidates_token_count or 0
        total_tokens = um.total_token_count or 0

        cost_input = (input_tokens / 1_000_000) * PRICE_INPUT_AUDIO_PER_1M
        cost_output = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_1M
        cost_total = cost_input + cost_output

        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_input_usd": cost_input,
            "cost_output_usd": cost_output,
            "cost_total_usd": cost_total,
            "cost_total_pln": cost_total * 4.0,
        }

    print("Done!")
    return response.text, usage


def print_usage(usage: dict):
    """Print token usage and cost summary."""
    if not usage:
        return
    print(f"\n--- Zużycie ---")
    print(f"Tokeny wejściowe (audio+prompt): {usage['input_tokens']:,}")
    print(f"Tokeny wyjściowe (transkrypt):   {usage['output_tokens']:,}")
    print(f"Razem tokenów:                   {usage['total_tokens']:,}")
    print(f"Koszt: ${usage['cost_total_usd']:.4f} (~{usage['cost_total_pln']:.2f} PLN)")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with Gemini Flash (speaker diarization)")
    parser.add_argument("file", help="Path to audio file (mp3, m4a, wav, etc.)")
    parser.add_argument("-o", "--output", help="Output file path (default: <input>_transcript.txt)")
    parser.add_argument("--lang", default=None, help="Language code (e.g. pl, en, de). Auto-detect if not set.")
    parser.add_argument("--speakers", type=int, default=None, help="Expected number of speakers (auto-detect if not set)")

    args = parser.parse_args()
    api_key = get_api_key()

    output, usage = transcribe(args.file, api_key, args.lang, args.speakers)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        input_path = Path(args.file)
        output_path = input_path.parent / f"{input_path.stem}_transcript.txt"

    # Write output
    output_path.write_text(output, encoding="utf-8")
    print(f"Transcript saved to: {output_path}")

    # Print usage stats
    print_usage(usage)

    # Print transcript to stdout
    print("\n" + output)


if __name__ == "__main__":
    main()
