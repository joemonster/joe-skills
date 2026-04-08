#!/usr/bin/env python3
"""
Add burned-in subtitles to videos.
Downloads video from URL, transcribes audio via Gemini Flash directly to SRT format,
and burns subtitles with ffmpeg subtitles filter.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"
CONFIG_PATHS = [
    Path(__file__).resolve().parent.parent.parent / "audio-transcript" / "scripts" / "config.json",
    Path.home() / ".claude" / "skills" / "audio-transcript" / "scripts" / "config.json",
]
URL_PATTERN = re.compile(r'^https?://')

PRICE_INPUT_AUDIO_PER_1M = 1.00
PRICE_OUTPUT_PER_1M = 3.00


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    for path in CONFIG_PATHS:
        if path.exists():
            with open(path) as f:
                key = json.load(f).get("gemini_api_key")
                if key:
                    return key
    print("ERROR: No Gemini API key. Set GEMINI_API_KEY or add to config.json", file=sys.stderr)
    sys.exit(1)


def download_video(url: str, output_dir: str) -> tuple[str, str]:
    """Download video from URL using yt-dlp. Returns (filepath, title)."""
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

    print(f"Downloading video from: {url}")
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
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

    video_files = list(Path(output_dir).glob("*.mp4"))
    if not video_files:
        video_files = [f for f in Path(output_dir).iterdir() if f.is_file()]
        if not video_files:
            print("ERROR: No video file downloaded.", file=sys.stderr)
            sys.exit(1)

    filepath = str(video_files[0])

    title_cmd = ["yt-dlp", "--get-title", "--no-playlist", url]
    title_result = subprocess.run(title_cmd, capture_output=True, text=True)
    title = title_result.stdout.strip() if title_result.returncode == 0 else video_files[0].stem
    title = re.sub(r'[<>:"/\\|?*]', '_', title)[:80]

    size_mb = Path(filepath).stat().st_size / (1024 * 1024)
    print(f"Downloaded: {Path(filepath).name} ({size_mb:.1f} MB)")
    return filepath, title


def extract_audio(video_path: str, output_dir: str) -> str:
    """Extract audio from video as mp3."""
    audio_path = os.path.join(output_dir, "audio.mp3")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", "-q:a", "5",
        audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Audio extraction failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Extracted audio: {Path(audio_path).stat().st_size / (1024*1024):.1f} MB")
    return audio_path


def generate_srt(audio_path: str, api_key: str, lang: str) -> str:
    """Transcribe audio directly to SRT format using Gemini Flash."""
    from google import genai

    filepath = Path(audio_path)
    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"Uploading {filepath.name} ({size_mb:.1f} MB)...")

    client = genai.Client(api_key=api_key)
    uploaded = client.files.upload(file=str(filepath))
    print("Upload complete. Generating subtitles...")

    if lang and lang.lower() == "original":
        lang_instruction = "Use the original language of the audio."
    elif lang:
        lang_instruction = f"Translate and write subtitles in {lang}."
    else:
        lang_instruction = "Translate and write subtitles in Polish (pl)."

    prompt = f"""Generate SRT subtitles for this audio recording.

{lang_instruction}

STRICT RULES:
- Output ONLY valid SRT format. No introduction, no commentary.
- Each subtitle must be MAX 2 lines, MAX 42 characters per line.
- Each subtitle should last 1-5 seconds (match actual speech timing).
- Break text at natural phrase boundaries (commas, conjunctions, pauses).
- Timestamps must be precise to when words are actually spoken.
- Use format:
  1
  00:00:01,000 --> 00:00:03,500
  First line of subtitle
  Second line if needed

  2
  00:00:03,800 --> 00:00:06,200
  Next subtitle segment

- Do NOT merge long speech into single subtitles.
- Do NOT include speaker labels (A:, B:, Speaker:).
- Start with subtitle number 1. Output nothing else."""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt, uploaded],
    )

    # Print usage
    if response.usage_metadata:
        um = response.usage_metadata
        input_tokens = um.prompt_token_count or 0
        output_tokens = um.candidates_token_count or 0
        cost_input = (input_tokens / 1_000_000) * PRICE_INPUT_AUDIO_PER_1M
        cost_output = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_1M
        cost_total = cost_input + cost_output
        print(f"Tokens: {input_tokens:,} in / {output_tokens:,} out — ${cost_total:.4f} (~{cost_total * 4:.2f} PLN)")

    srt = response.text.strip()
    # Strip markdown code fences if present
    if srt.startswith("```"):
        srt = re.sub(r'^```\w*\n?', '', srt)
        srt = re.sub(r'\n?```$', '', srt)

    return srt.strip()


STYLES = {
    "light": {
        "PrimaryColour": "&H00000000",   # black text
        "OutlineColour": "&H00FFFFFF",   # white border
        "BackColour": "&H00FFFFFF",      # white box
    },
    "dark": {
        "PrimaryColour": "&H00FFFFFF",   # white text
        "OutlineColour": "&H00000000",   # black border
        "BackColour": "&H00000000",      # black box
    },
}


def get_video_bitrate(video_path: str) -> int | None:
    """Get video stream bitrate in bits/s using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=bit_rate", "-of", "csv=p=0", video_path],
            capture_output=True, text=True
        )
        br = result.stdout.strip()
        return int(br) if br and br != "N/A" else None
    except Exception:
        return None


def burn_subtitles(video_path: str, srt_path: str, output_path: str,
                   font_size: int = 18, style: str = "light"):
    """Burn subtitles into video using ffmpeg subtitles filter.
    Matches source video bitrate to avoid quality/size changes."""
    colors = STYLES[style]
    force_style = (
        f"FontName=Source Code Pro,"
        f"FontSize={font_size},"
        f"PrimaryColour={colors['PrimaryColour']},"
        f"OutlineColour={colors['OutlineColour']},"
        f"BackColour={colors['BackColour']},"
        f"BorderStyle=3,"              # opaque box mode
        f"Outline=5,"                  # box padding around text
        f"Shadow=0,"
        f"MarginV=30,"
        f"MarginL=20,"
        f"MarginR=20"
    )

    # Escape paths for ffmpeg filter (Windows colons, backslashes)
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    fonts_escaped = str(FONTS_DIR).replace("\\", "/").replace(":", "\\:")

    vf = f"subtitles='{srt_escaped}':fontsdir='{fonts_escaped}':force_style='{force_style}'"

    # Match source video bitrate to preserve original compression level
    bitrate = get_video_bitrate(video_path)
    video_opts = ["-b:v", str(bitrate)] if bitrate else []

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf,
        *video_opts,
        "-c:a", "copy",
        output_path,
    ]

    print("Burning subtitles...")
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        print("ERROR: ffmpeg subtitle burn failed.", file=sys.stderr)
        sys.exit(1)

    size_mb = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"Output: {output_path} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Add burned-in subtitles to video")
    parser.add_argument("source", help="Video file path or URL (YouTube, Twitter/X, etc.)")
    parser.add_argument("-o", "--output", help="Output MP4 path (default: ~/Downloads/<title>_subtitled.mp4)")
    parser.add_argument("--lang", default="pl", help="Subtitle language (default: pl, use 'original' for source)")
    parser.add_argument("--font-size", type=int, default=18, help="Font size (default: 18)")
    parser.add_argument("--style", choices=["light", "dark"], default="dark",
                        help="dark = white text on black box (default), light = black text on white box")
    parser.add_argument("--srt-only", action="store_true", help="Only generate SRT, don't burn into video")

    args = parser.parse_args()

    api_key = get_api_key()
    tmp_dir = tempfile.mkdtemp(prefix="subtitles_")
    is_url = bool(URL_PATTERN.match(args.source))

    try:
        # 1. Get video
        if is_url:
            video_path, title = download_video(args.source, tmp_dir)
        else:
            video_path = os.path.abspath(args.source)
            title = Path(video_path).stem
            if not Path(video_path).exists():
                print(f"ERROR: File not found: {video_path}", file=sys.stderr)
                sys.exit(1)

        # 2. Extract audio
        audio_path = extract_audio(video_path, tmp_dir)

        # 3. Generate SRT directly from Gemini
        srt_content = generate_srt(audio_path, api_key, args.lang)
        srt_path = os.path.join(tmp_dir, "subtitles.srt")
        Path(srt_path).write_text(srt_content, encoding="utf-8")
        entry_count = len(re.findall(r'^\d+$', srt_content, re.MULTILINE))
        print(f"Generated SRT: {entry_count} entries")

        downloads = Path.home() / "Downloads"

        if args.srt_only:
            out = Path(args.output) if args.output else downloads / f"{title}_subtitles.srt"
            out.write_text(srt_content, encoding="utf-8")
            print(f"SRT saved to: {out}")
            print(f"\n{srt_content}")
            return

        # 4. Burn subtitles
        output_path = args.output or str(downloads / f"{title}_subtitled.mp4")
        burn_subtitles(video_path, srt_path, output_path, args.font_size, args.style)
        print(f"\nDone! Video with subtitles: {output_path}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print("Cleaned up temp files.")


if __name__ == "__main__":
    main()
