from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\Administrator\Desktop\codex_project\social_media\06_运营中心\2026\2026-07\草稿区\小红书\202607_小红书_AI科普对话选题池_stick风"
)
ARK_SCRIPT = Path(r"C:\Users\Administrator\.codex\skills\ark-image-generation\scripts\ark_image.py")
CONFIG = Path.home() / ".codex" / "apis.json"


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: render_one_xhs_page.py <topic_dir> <page_no> <filename_prefix>")
        return 2

    topic_dir = ROOT / sys.argv[1]
    page_no = sys.argv[2]
    filename_prefix = sys.argv[3]
    prompt_files = sorted((topic_dir / "prompts").glob(f"{page_no}_*.md"))
    if not prompt_files:
        raise FileNotFoundError(f"missing prompt for {page_no}")
    prompt_file = prompt_files[0]
    images_dir = topic_dir / "images"
    prompt = prompt_file.read_text(encoding="utf-8")

    cmd = [
        sys.executable,
        str(ARK_SCRIPT),
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
        "--timeout",
        "240",
        "--out-dir",
        str(images_dir),
        "--filename-prefix",
        filename_prefix,
        "--prompt",
        prompt,
    ]
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
