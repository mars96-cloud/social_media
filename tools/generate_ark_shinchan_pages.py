from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


API_URL = "https://ark.cn-beijing.volces.com/api/plan/v3/images/generations"
MODEL = "doubao-seedream-5.0-lite"
SIZE = "2048x2048"


def iter_pairs(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key), item
            yield from iter_pairs(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_pairs(item)


def find_api_key(config: dict) -> str:
    for key, value in iter_pairs(config):
        if isinstance(value, str) and value.strip() and any(token in key.lower() for token in ("api_key", "token", "ark_key", "agent_key", "key")):
            return value.strip()
    raise RuntimeError("No API key found in config")


def request_json(url: str, api_key: str, body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(raw) from exc


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=180) as resp:
        dest.write_bytes(resp.read())


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: generate_ark_shinchan_pages.py <config_json> <prompts_dir> <output_dir>")
        return 2

    config_path = Path(sys.argv[1])
    prompts_dir = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    config = json.loads(config_path.read_text(encoding="utf-8"))
    api_key = find_api_key(config)

    prompt_files = sorted(prompts_dir.glob("*.md"))
    if not prompt_files:
        raise RuntimeError("No prompt files found")

    for prompt_file in prompt_files:
        prompt = prompt_file.read_text(encoding="utf-8").strip()
        body = {
            "model": MODEL,
            "prompt": prompt,
            "size": SIZE,
            "output_format": "png",
            "response_format": "url",
            "watermark": False,
        }
        payload = request_json(API_URL, api_key, body)
        image_url = None
        for key in ("url", "image_url"):
            if payload.get(key):
                image_url = payload[key]
                break
        if not image_url:
            data = payload.get("data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                image_url = data[0].get("url") or data[0].get("image_url")
        if not image_url:
            raise RuntimeError(json.dumps(payload, ensure_ascii=False))

        stem = prompt_file.stem
        target = output_dir / f"{stem}.png"
        download(image_url, target)
        time.sleep(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
