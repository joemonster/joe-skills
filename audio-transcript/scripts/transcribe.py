#!/usr/bin/env python3
"""
Audio Transcription with Speaker Diarization via Gemini Flash.
Accepts local files or URLs (YouTube, Twitter/X, etc.) — downloads audio automatically.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


# Pricing per 1M tokens (USD) for gemini-3-flash-preview
PRICE_INPUT_AUDIO_PER_1M = 1.00
PRICE_OUTPUT_PER_1M = 3.00

URL_PATTERN = re.compile(r'^https?://')


def load_config():
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY") or load_config().get("gemini_api_key")
    if not key:
        print("ERROR: No Gemini API key. Set GEMINI_API_KEY or add gemini_api_key to config.json", file=sys.stderr)
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

    speakers_hint = f" Expected speakers: {speakers_expected}." if speakers_expected else ""

    if language and language.lower() == "original":
        translate_instruction = "Transcribe in the original language of the audio."
    elif language:
        translate_instruction = f"Transcribe and translate the output to {language}."
    else:
        translate_instruction = "Transcribe and translate the output to Polish (pl)."

    prompt = f"""Transcribe the following audio recording.{speakers_hint}

{translate_instruction}

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


def download_audio(url: str) -> tuple[str, str]:
    """Download audio from URL using yt-dlp. Returns (temp_filepath, title)."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: yt-dlp not installed. Install with: pip install yt-dlp", file=sys.stderr)
        sys.exit(1)

    tmp_dir = tempfile.mkdtemp(prefix="transcript_")
    output_template = os.path.join(tmp_dir, "%(id)s.%(ext)s")

    print(f"Downloading audio from: {url}")
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "5",  # medium quality, smaller file
        "--no-playlist",
        "--no-write-thumbnail",
        "--restrict-filenames",
        "-o", output_template,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: yt-dlp failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Find the downloaded mp3
    mp3_files = list(Path(tmp_dir).glob("*.mp3"))
    if not mp3_files:
        # yt-dlp might have kept original format if ffmpeg unavailable
        all_files = list(Path(tmp_dir).iterdir())
        if all_files:
            mp3_files = all_files
        else:
            print("ERROR: No audio file downloaded.", file=sys.stderr)
            sys.exit(1)

    filepath = str(mp3_files[0])

    # Get title for output filename
    title_cmd = ["yt-dlp", "--get-title", "--no-playlist", url]
    title_result = subprocess.run(title_cmd, capture_output=True, text=True)
    title = title_result.stdout.strip() if title_result.returncode == 0 else mp3_files[0].stem
    # Sanitize title for filename
    title = re.sub(r'[<>:"/\\|?*]', '_', title)[:80]

    print(f"Downloaded: {Path(filepath).name} ({Path(filepath).stat().st_size / (1024*1024):.1f} MB)")
    return filepath, title


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with Gemini Flash (speaker diarization)")
    parser.add_argument("source", help="Path to audio file OR URL (YouTube, Twitter/X, etc.)")
    parser.add_argument("-o", "--output", help="Output file path (default: <input>_transcript.txt)")
    parser.add_argument("--lang", default=None, help="Output language (default: pl). Use 'original' to keep source language.")
    parser.add_argument("--speakers", type=int, default=None, help="Expected number of speakers (auto-detect if not set)")

    args = parser.parse_args()
    api_key = get_api_key()

    # Determine if source is URL or local file
    is_url = bool(URL_PATTERN.match(args.source))
    temp_file = None
    title = None

    if is_url:
        audio_path, title = download_audio(args.source)
        temp_file = audio_path
    else:
        audio_path = args.source

    try:
        output, usage = transcribe(audio_path, api_key, args.lang, args.speakers)

        # Determine output path
        downloads = Path.home() / "Downloads"
        if args.output:
            output_path = Path(args.output)
        elif is_url and title:
            output_path = downloads / f"{title}_transcript.txt"
        else:
            output_path = downloads / f"{Path(audio_path).stem}_transcript.txt"

        # Write output
        output_path.write_text(output, encoding="utf-8")
        print(f"Transcript saved to: {output_path}")

        # Print usage stats
        print_usage(usage)

        # Print transcript to stdout
        print("\n" + output)
    finally:
        # Clean up temp file
        if temp_file:
            try:
                Path(temp_file).unlink(missing_ok=True)
                Path(temp_file).parent.rmdir()
                print(f"Cleaned up temp audio file.")
            except OSError:
                pass


if __name__ == "__main__":
    main()
