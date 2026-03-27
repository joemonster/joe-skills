#!/usr/bin/env python3
"""
Instaluje joe-skills do ~/.claude/skills/.
Uruchom ponownie po git pull żeby zaktualizować.
"""

import shutil
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent
SKILLS_DIR = Path.home() / ".claude" / "skills"
CONFIG_SRC = REPO_DIR / "config.json"
CONFIG_DST = SKILLS_DIR / "joe-config.json"

SKILLS = ["audio-transcript", "web-scraper"]


def main():
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # Copy skills
    for skill in SKILLS:
        src = REPO_DIR / skill
        dst = SKILLS_DIR / skill
        if not src.exists():
            print(f"  SKIP  {skill} (not found in repo)")
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"  OK    {skill}")

    # Copy config.json -> joe-config.json (only if source exists and dest doesn't)
    if CONFIG_SRC.exists():
        if CONFIG_DST.exists():
            print(f"  SKIP  joe-config.json (already exists, not overwriting)")
        else:
            shutil.copy2(CONFIG_SRC, CONFIG_DST)
            print(f"  OK    joe-config.json")
    else:
        if not CONFIG_DST.exists():
            print(f"\n  WARNING: No config.json in repo root and no joe-config.json in skills dir.")
            print(f"           Create {CONFIG_DST} with your API keys. See config.json.example.")

    print(f"\nDone! Skills installed to {SKILLS_DIR}")


if __name__ == "__main__":
    main()
