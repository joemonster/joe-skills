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


URL_PATTERN = re.compile(r'^https?://')

MODELS = {
    "gemini-2.5-flash": {"audio_in": 1.00, "out": 2.50},
    "gemini-3-flash-preview": {"audio_in": 1.00, "out": 3.00},
    "gemini-3.1-flash-lite-preview": {"audio_in": 0.50, "out": 1.50},
}
DEFAULT_MODEL = "gemini-2.5-flash"

# Max audio file size for Gemini upload (URI)
MAX_UPLOAD_MB = 100
# Max audio duration in seconds (9.5h)
MAX_AUDIO_DURATION = 9.5 * 3600


def load_config():
    for p in [
        Path(__file__).parent / "config.json",
        Path.home() / ".claude" / "skills" / "audio-transcript" / "scripts" / "config.json",
    ]:
        if p.exists():
            with open(p) as f:
                return json.load(f)
    return {}


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY") or load_config().get("gemini_api_key")
    if not key:
        print("ERROR: No Gemini API key. Set GEMINI_API_KEY or add gemini_api_key to config.json", file=sys.stderr)
        sys.exit(1)
    return key


def get_audio_duration(filepath: str) -> float | None:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", filepath],
            capture_output=True, text=True
        )
        return float(result.stdout.strip()) if result.stdout.strip() else None
    except Exception:
        return None


def split_audio(filepath: str, max_chunk_mb: int = 90) -> list[str]:
    """Split large audio file into chunks small enough for Gemini upload.
    Returns list of chunk file paths."""
    size_mb = Path(filepath).stat().st_size / (1024 * 1024)
    duration = get_audio_duration(filepath)

    if size_mb <= max_chunk_mb and (duration is None or duration <= MAX_AUDIO_DURATION):
        return [filepath]

    # Calculate number of chunks needed
    n_chunks_size = max(1, int(size_mb / max_chunk_mb) + 1)
    n_chunks_dur = max(1, int(duration / MAX_AUDIO_DURATION) + 1) if duration else 1
    n_chunks = max(n_chunks_size, n_chunks_dur)
    chunk_duration = int(duration / n_chunks) + 1 if duration else 1200

    print(f"File too large ({size_mb:.0f} MB, {duration/60:.0f} min). Splitting into {n_chunks} chunks...", file=sys.stderr)

    # Overlap between chunks to avoid cutting mid-sentence
    overlap = 10  # seconds

    chunks = []
    tmp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
    for i in range(n_chunks):
        start = max(0, i * chunk_duration - (overlap if i > 0 else 0))
        chunk_path = os.path.join(tmp_dir, f"chunk_{i}.mp3")
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", filepath,
               "-t", str(chunk_duration + overlap), "-ac", "1", "-ab", "96k", "-ar", "44100",
               chunk_path]
        subprocess.run(cmd, capture_output=True)
        if Path(chunk_path).exists() and Path(chunk_path).stat().st_size > 1000:
            chunks.append(chunk_path)

    print(f"Created {len(chunks)} chunks", file=sys.stderr)
    return chunks


def _upload_and_transcribe(client, filepath: str, prompt: str, model: str,
                           max_retries: int = 3) -> tuple[str, dict]:
    """Upload file and transcribe with retry on empty response."""
    import time

    size_mb = Path(filepath).stat().st_size / (1024 * 1024)
    print(f"Uploading {Path(filepath).name} ({size_mb:.1f} MB)...")

    try:
        uploaded = client.files.upload(file=str(filepath))
    except Exception as e:
        print(f"ERROR: Upload failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Wait for processing if needed
    while hasattr(uploaded, 'state') and hasattr(uploaded.state, 'name') and uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)

    print("Transcribing...")

    pricing = MODELS.get(model, MODELS[DEFAULT_MODEL])
    text = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[prompt, uploaded],
            )
        except Exception as e:
            print(f"ERROR: Gemini API call failed: {e}", file=sys.stderr)
            sys.exit(1)

        text = response.text
        if text:
            break
        print(f"Empty response (attempt {attempt + 1}/{max_retries}), retrying...", file=sys.stderr)
        time.sleep(3)

    if not text:
        text = "[BRAK TRANSKRYPCJI DLA TEGO FRAGMENTU]"

    # Extract token usage
    usage = {}
    if response.usage_metadata:
        um = response.usage_metadata
        input_tokens = um.prompt_token_count or 0
        output_tokens = um.candidates_token_count or 0
        total_tokens = um.total_token_count or 0

        cost_input = (input_tokens / 1_000_000) * pricing["audio_in"]
        cost_output = (output_tokens / 1_000_000) * pricing["out"]
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

    return text, usage


def transcribe(filepath: str, api_key: str, language: str = None,
               speakers_expected: int = None, plain: bool = False,
               model: str = None) -> tuple[str, dict]:
    """Transcribe audio using Gemini Flash. Returns (text, usage_info).
    Automatically splits large files into chunks."""
    from google import genai

    model = model or DEFAULT_MODEL
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    speakers_hint = f" Expected speakers: {speakers_expected}." if speakers_expected else ""

    if language and language.lower() == "original":
        translate_instruction = "Transcribe in the original language of the audio."
    elif language:
        translate_instruction = f"Transcribe and translate the output to {language}."
    else:
        translate_instruction = "Transcribe and translate the output to Polish (pl)."

    if plain:
        prompt = f"""Transcribe the following audio recording.

{translate_instruction}

RULES:
- Output ONLY clean text divided into paragraphs.
- NO timestamps, NO speaker labels, NO diarization.
- NO introduction, NO commentary, NO summary.
- Start with the first word of the transcription. Add nothing else."""
    else:
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

    # Split large files automatically
    chunks = split_audio(str(filepath))
    is_chunked = len(chunks) > 1

    all_text = []
    total_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                   "cost_input_usd": 0, "cost_output_usd": 0, "cost_total_usd": 0, "cost_total_pln": 0}

    for i, chunk_path in enumerate(chunks):
        if is_chunked:
            print(f"\n--- Chunk {i+1}/{len(chunks)} ---", file=sys.stderr)

        text, usage = _upload_and_transcribe(client, chunk_path, prompt, model)
        all_text.append(text)

        for k in total_usage:
            total_usage[k] += usage.get(k, 0)

    # Clean up chunk temp files (but not the original)
    if is_chunked:
        for chunk_path in chunks:
            try:
                Path(chunk_path).unlink(missing_ok=True)
            except OSError:
                pass
        try:
            Path(chunks[0]).parent.rmdir()
        except OSError:
            pass

    combined = "\n\n".join(t.strip() for t in all_text if t)
    print("Done!")
    return combined, total_usage


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
    model_choices = list(MODELS.keys())
    parser = argparse.ArgumentParser(description="Transcribe audio with Gemini Flash (speaker diarization)")
    parser.add_argument("source", help="Path to audio file OR URL (YouTube, Twitter/X, etc.)")
    parser.add_argument("-o", "--output", help="Output file path (default: <input>_transcript.txt)")
    parser.add_argument("--lang", default=None, help="Output language (default: pl). Use 'original' to keep source language.")
    parser.add_argument("--speakers", type=int, default=None, help="Expected number of speakers (auto-detect if not set)")
    parser.add_argument("--plain", action="store_true", help="Plain text output: no timestamps, no speaker labels, just paragraphs")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=model_choices,
                        help=f"Gemini model (default: {DEFAULT_MODEL})")

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
        output, usage = transcribe(audio_path, api_key, args.lang, args.speakers,
                                   plain=args.plain, model=args.model)

        # Determine output path
        downloads = Path.home() / "Downloads"
        ext = ".md" if args.plain else ".txt"
        if args.output:
            output_path = Path(args.output)
        elif is_url and title:
            output_path = downloads / f"{title}_transcript{ext}"
        else:
            output_path = downloads / f"{Path(audio_path).stem}_transcript{ext}"

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
