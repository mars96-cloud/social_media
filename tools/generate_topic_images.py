from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ARK = Path(r"C:\Users\Administrator\.codex\skills\ark-image-generation\scripts\ark_image.py")
CONFIG = Path.home() / ".codex" / "apis.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir", required=True)
    parser.add_argument("--pages", nargs="+", required=True)
    args = parser.parse_args()

    topic_dir = Path(args.topic_dir)
    prompts_dir = topic_dir / "prompts"
    images_dir = topic_dir / "images"

    for stem in args.pages:
        prompt = (prompts_dir / f"{stem}.md").read_text(encoding="utf-8")
        cmd = [
            sys.executable,
            str(ARK),
            "--config",
            str(CONFIG),
            "generate",
            "--model",
            "doubao-seedream-5.0-lite",
            "--size",
            "2K",
            "--output-format",
            "png",
            "--response-format",
            "url",
            "--out-dir",
            str(images_dir),
            "--filename-prefix",
            stem,
            "--prompt",
            prompt,
        ]
        print(f"RUN {stem}")
        code = subprocess.run(cmd, check=False).returncode
        print(f"RC {code}")
        if code != 0:
            return code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
