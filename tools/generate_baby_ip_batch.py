from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ARK = Path(r"C:\Users\Administrator\.codex\skills\ark-image-generation\scripts\ark_image.py")
CONFIG = Path.home() / ".codex" / "apis.json"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python tools/generate_baby_ip_batch.py <target-dir>")
        return 2

    target_dir = Path(sys.argv[1]).resolve()
    base_prompt = (target_dir / "prompt_base.md").read_text(encoding="utf-8")
    actions = json.loads((target_dir / "actions.json").read_text(encoding="utf-8"))
    images_dir = target_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for item in actions:
        prompt = base_prompt.replace("{ACTION_DESCRIPTION}", item["action"])
        stem = f'{item["id"]}_{item["name"]}'
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
