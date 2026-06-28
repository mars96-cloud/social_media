import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(r"C:\Users\Administrator\Desktop\codex_project\social_media")
BASE = ROOT / r"06_运营中心\2026\2026-07\草稿区\公众号"
HELPER = r"C:\Users\Administrator\.codex\skills\ark-image-generation\scripts\ark_image.py"
CONFIG = r"C:\Users\Administrator\.codex\apis.json"
MODEL = "doubao-seedream-5.0-lite"


def main(names: list[str]) -> int:
    for i, name in enumerate(names):
        base = BASE / name
        prompt_path = base / "prompts" / "01_公众号封面.md"
        out_dir = base / "images"
        prompt = prompt_path.read_text(encoding="utf-8")
        cmd = [
            "python",
            HELPER,
            "--config",
            CONFIG,
            "generate",
            "--model",
            MODEL,
            "--prompt",
            prompt,
            "--size",
            "2K",
            "--output-format",
            "png",
            "--out-dir",
            str(out_dir),
            "--filename-prefix",
            "01_公众号封面",
        ]
        rc = subprocess.run(cmd).returncode
        print(f"{name}: rc={rc}")
        if rc != 0:
            return rc
        if i != len(names) - 1:
            time.sleep(6)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
