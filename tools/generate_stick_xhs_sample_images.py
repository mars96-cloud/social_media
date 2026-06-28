from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\Administrator\Desktop\codex_project\social_media\06_运营中心\2026\2026-07\草稿区\小红书\202607_小红书_AI科普对话选题池_stick风"
)
ARK_SCRIPT = Path(
    r"C:\Users\Administrator\.codex\skills\ark-image-generation\scripts\ark_image.py"
)
CONFIG = Path.home() / ".codex" / "apis.json"


def load_overview() -> dict:
    return json.loads((ROOT / "00_选题总表.json").read_text(encoding="utf-8"))


def iter_targets(limit: int = 3):
    overview = load_overview()
    for topic in overview["topics"][:limit]:
        topic_dir = ROOT / f"{topic['id']}_{topic['title']}"
        prompts_dir = topic_dir / "prompts"
        images_dir = topic_dir / "images"
        yield topic_dir, prompts_dir, images_dir


def generate_prompt(prompt_file: Path, images_dir: Path) -> int:
    prefix = prompt_file.stem
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
        "--out-dir",
        str(images_dir),
        "--filename-prefix",
        prefix,
        "--prompt",
        prompt_file.read_text(encoding="utf-8"),
    ]
    return subprocess.run(cmd, check=False).returncode


def main() -> int:
    for _, prompts_dir, images_dir in iter_targets(limit=3):
        for prompt_file in sorted(prompts_dir.glob("*.md"))[:2]:
            code = generate_prompt(prompt_file, images_dir)
            if code != 0:
                return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
