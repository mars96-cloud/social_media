import pathlib
import subprocess
import sys
import time

HELPER = r"C:\Users\Administrator\.codex\skills\ark-image-generation\scripts\ark_image.py"
CONFIG = r"C:\Users\Administrator\.codex\apis.json"
MODEL = "doubao-seedream-5.0-lite"


def sanitize_prompt(prompt: str) -> str:
    lines = prompt.splitlines()
    kept: list[str] = []
    skip_annotations = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Chinese handwritten annotations:"):
            skip_annotations = True
            continue
        if skip_annotations:
            if not stripped:
                continue
            if stripped.startswith("Strict character lock:"):
                skip_annotations = False
                kept.append(line)
            continue
        kept.append(line)

    kept.append("No visible text in image, no Chinese characters, no labels, no title, no watermark.")
    kept.append("Flat hand-drawn illustration, editorial sketch, 2D watercolor marker feel, not 3D render, not glossy mascot, not clay, not toy, not cinematic.")
    kept.append("Leave clear blank whitespace for later local Chinese overlay.")
    return "\n".join(kept)


def main(base_dir: str, names: list[str]) -> int:
    base = pathlib.Path(base_dir)
    for i, name in enumerate(names):
        prompt_path = base / "prompts" / f"{name}.md"
        out_dir = base / "images"
        prompt = sanitize_prompt(prompt_path.read_text(encoding="utf-8"))
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
            name,
        ]
        rc = subprocess.run(cmd).returncode
        print(f"{name}: rc={rc}")
        if rc != 0:
            return rc
        if i != len(names) - 1:
            time.sleep(6)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2:]))
