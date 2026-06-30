from __future__ import annotations

import argparse
import math
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageStat


COVER_W = 1408
COVER_H = 600
SQUARE = 1080
BODY_W = 1280
BODY_H = 720
COVER_SAFETY_THRESHOLD = 0.020
BODY_SAFETY_THRESHOLD = 0.025

BODY_LAYOUTS = [
    {"name": "right_tall", "box": (0.58, 0.09, 0.93, 0.66)},
    {"name": "left_tall", "box": (0.07, 0.09, 0.42, 0.66)},
    {"name": "top_wide", "box": (0.10, 0.07, 0.90, 0.34)},
]

COVER_LAYOUTS = [
    {"name": "left_top", "box": (0.08, 0.08, 0.52, 0.44)},
    {"name": "center_top", "box": (0.19, 0.08, 0.81, 0.40)},
    {"name": "left_mid", "box": (0.07, 0.16, 0.47, 0.52)},
]


def configure_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def repo_root() -> Path:
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "06_运营中心").exists():
            return p
    raise SystemExit("未找到 social_media 根目录")


def default_ark_script() -> Path:
    return Path.home() / ".codex" / "skills" / "ark-image-generation" / "scripts" / "ark_image.py"


def default_config() -> Path | None:
    path = Path.home() / ".codex" / "apis.json"
    return path if path.exists() else None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_rgb_image(img: Image.Image, target_path: Path, quality: int = 95) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = target_path.suffix or ".png"
    temp_path = target_path.with_name(f"{target_path.stem}.__tmp__{suffix}")
    img.save(temp_path, quality=quality)
    if target_path.exists():
        try:
            target_path.unlink()
        except Exception:
            pass
    temp_path.replace(target_path)


def fit_image(img: Image.Image, target_size: tuple[int, int], centering: tuple[float, float]) -> Image.Image:
    return ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS, centering=centering)


def normalize_image(raw_image: Path, target_size: tuple[int, int], target_path: Path, centering: tuple[float, float]) -> None:
    with Image.open(raw_image) as opened:
        img = fit_image(opened.convert("RGB"), target_size, centering)
    save_rgb_image(img, target_path)


def box_from_layout(img: Image.Image, layout: dict) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = layout["box"]
    w, h = img.size
    return (int(w * x1), int(h * y1), int(w * x2), int(h * y2))


def candidate_score(base_rgb: Image.Image, box: tuple[int, int, int, int]) -> float:
    crop = base_rgb.crop(box)
    gray = crop.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0]
    lum_mean = ImageStat.Stat(gray).mean[0]
    pixels = crop.load()
    width, height = crop.size
    step = max(1, min(width, height) // 90)
    occupied = 0
    total = 0
    for y in range(0, height, step):
        for x in range(0, width, step):
            r, g, b = pixels[x, y]
            total += 1
            dist_white = math.sqrt((255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2)
            chroma = max(r, g, b) - min(r, g, b)
            if dist_white > 18 or chroma > 10 or min(r, g, b) < 246:
                occupied += 1
    return edge_mean + max(0, 196 - lum_mean) * 0.7 + (occupied / max(1, total)) * 900


def occupancy_ratio(base_rgb: Image.Image, box: tuple[int, int, int, int]) -> float:
    crop = base_rgb.crop(box)
    gray = crop.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_pixels = edges.load()
    pixels = crop.load()
    width, height = crop.size
    step = max(1, min(width, height) // 90)
    occupied = 0
    total = 0
    for y in range(0, height, step):
        for x in range(0, width, step):
            r, g, b = pixels[x, y]
            total += 1
            dist_white = math.sqrt((255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2)
            chroma = max(r, g, b) - min(r, g, b)
            if dist_white > 18 or chroma > 10 or min(r, g, b) < 246 or edge_pixels[x, y] > 24:
                occupied += 1
    return occupied / max(1, total)


def select_layout_by_threshold(base_rgb: Image.Image, layouts: list[dict], threshold: float) -> dict | None:
    valid: list[tuple[float, dict]] = []
    for layout in layouts:
        box = box_from_layout(base_rgb, layout)
        occ = occupancy_ratio(base_rgb, box)
        if occ <= threshold:
            valid.append((candidate_score(base_rgb, box), layout))
    if not valid:
        return None
    valid.sort(key=lambda item: item[0])
    return valid[0][1]


def run_ark_generate(
    ark_script: Path,
    config: Path | None,
    prompt: str,
    out_dir: Path,
    prefix: str,
    model: str | None,
    size: str,
    timeout: int,
) -> Path:
    before = set(out_dir.glob("*"))
    cmd = [
        sys.executable,
        str(ark_script),
        "generate",
        "--prompt",
        prompt,
        "--size",
        size,
        "--output-format",
        "png",
        "--response-format",
        "b64_json",
        "--filename-prefix",
        prefix,
        "--out-dir",
        str(out_dir),
        "--timeout",
        str(timeout),
    ]
    if config:
        cmd[2:2] = ["--config", str(config)]
    if model:
        cmd.extend(["--model", model])
    result = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout + 60)
    if result.returncode != 0:
        raise RuntimeError((result.stdout + "\n" + result.stderr).strip())
    after = set(out_dir.glob("*"))
    new_files = sorted(
        [p for p in after - before if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}],
        key=lambda p: p.stat().st_mtime,
    )
    if not new_files:
        raise RuntimeError("Ark 未返回新图片文件")
    return new_files[-1]


def build_prompt_text(task_md: str) -> str:
    return read_text(task_md) if task_md else ""


def generate_safe_raw(
    ark_script: Path,
    config: Path | None,
    out_dir: Path,
    prefix: str,
    model: str | None,
    size: str,
    timeout: int,
    layouts: list[dict],
    threshold: float,
    prompt_text: str,
    target_size: tuple[int, int],
    centering: tuple[float, float],
) -> tuple[Path, dict]:
    last = ""
    for layout in layouts:
        raw = run_ark_generate(ark_script, config, prompt_text, out_dir, f"{prefix}-{layout['name']}", model, size, timeout)
        with Image.open(raw) as opened:
            fitted = fit_image(opened.convert("RGB"), target_size, centering)
        occ = occupancy_ratio(fitted, box_from_layout(fitted, layout))
        last = f"{layout['name']}={occ:.3f}"
        if occ <= threshold:
            return raw, layout
    raise RuntimeError(f"未找到可用无字 raw 图，最后一次检测：{last}")


def find_pack(root: Path, pack_arg: str | None, day: str | None) -> Path:
    if pack_arg:
        pack = Path(pack_arg)
        if not pack.is_absolute():
            pack = (root / pack).resolve()
        if not pack.exists():
            raise SystemExit(f"指定稿包不存在：{pack}")
        return pack
    if not day:
        raise SystemExit("请提供 --pack 或 --day")
    day_dir = root / "06_运营中心" / "2026" / "2026-07" / "公众号" / day
    packs = [p for p in day_dir.iterdir() if p.is_dir()]
    if len(packs) != 1:
        raise SystemExit(f"日期目录下稿包数量异常：{day_dir}")
    return packs[0]


def update_audit(pack: Path, detail: str, image_paths: list[str]) -> None:
    audit = pack / "审核记录.md"
    existing = read_text(audit) if audit.exists() else "# 审核记录\n"
    marker = "\n## 图片生成记录\n"
    head = existing.split(marker)[0].rstrip()
    lines = "\n".join([f"- {item}" for item in image_paths])
    content = (
        f"{head}{marker}\n"
        f"- 结论：通过\n"
        f"- 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- 说明：{detail}\n"
        f"- 正式图片：\n{lines}\n"
        f"- 来源链路：wechat-gen -> potato-illustrations -> ark-image-generation\n"
    )
    write_text(audit, content)


def find_best_existing_raw(
    raw_dir: Path,
    stem_keyword: str,
    target_size: tuple[int, int],
    centering: tuple[float, float],
    layouts: list[dict],
    threshold: float,
) -> tuple[Path, dict] | None:
    matched: list[tuple[float, Path, dict]] = []
    for raw in sorted(raw_dir.glob("*.png")):
        if stem_keyword not in raw.name:
            continue
        try:
            with Image.open(raw) as opened:
                fitted = fit_image(opened.convert("RGB"), target_size, centering)
        except Exception:
            continue
        layout = select_layout_by_threshold(fitted, layouts, threshold)
        if not layout:
            continue
        matched.append((candidate_score(fitted, box_from_layout(fitted, layout)), raw, layout))
    if not matched:
        return None
    matched.sort(key=lambda item: item[0])
    _, raw, layout = matched[0]
    return raw, layout


def slug(name: str) -> str:
    cleaned = "".join(ch for ch in name if ch.isalnum() or ("\u4e00" <= ch <= "\u9fff"))
    return cleaned[:22] or "image"


def normalize_output_filename(prompt_path: Path, file_name: str, fallback_stem: str) -> str:
    candidate = (file_name or "").strip()
    if not candidate:
        candidate = prompt_path.with_suffix(".png").name
    else:
        candidate = Path(candidate).name
        if not Path(candidate).suffix:
            candidate = f"{candidate}.png"
    normalized = Path(candidate)
    stem = normalized.stem or fallback_stem or prompt_path.stem
    suffix = normalized.suffix.lower() or ".png"
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"
    return f"{stem}{suffix}"


def generate_pack(pack: Path, args: argparse.Namespace, ark_script: Path, config: Path | None) -> None:
    prompts_dir = pack / "prompts"
    images_dir = pack / "images"
    raw_dir = images_dir / "_potato_raw"
    prompts = sorted(prompts_dir.glob("*.md"))
    if not prompts:
        raise RuntimeError(f"未找到 prompts：{prompts_dir}")
    images_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    for prompt_path in prompts:
        text = read_text(prompt_path)
        name = prompt_path.name
        if name.startswith("01_公众号封面"):
            final_235 = images_dir / "01_公众号封面_无字版_2.35比1.png"
            final_11 = images_dir / "01_公众号封面_无字版_1比1.png"
            existing_cover_235 = find_best_existing_raw(raw_dir, "cover235", (COVER_W, COVER_H), (0.54, 0.5), COVER_LAYOUTS, COVER_SAFETY_THRESHOLD)
            raw_235, _ = existing_cover_235 or generate_safe_raw(
                ark_script, config, raw_dir, f"{pack.name[:18]}-cover235", args.model, args.size, args.timeout,
                COVER_LAYOUTS, COVER_SAFETY_THRESHOLD, text, (COVER_W, COVER_H), (0.54, 0.5)
            )
            existing_cover_11 = find_best_existing_raw(raw_dir, "cover11", (SQUARE, SQUARE), (0.5, 0.5), COVER_LAYOUTS, COVER_SAFETY_THRESHOLD)
            raw_11, _ = existing_cover_11 or generate_safe_raw(
                ark_script, config, raw_dir, f"{pack.name[:18]}-cover11", args.model, args.size, args.timeout,
                COVER_LAYOUTS, COVER_SAFETY_THRESHOLD, text, (SQUARE, SQUARE), (0.5, 0.5)
            )
            normalize_image(raw_235, (COVER_W, COVER_H), final_235, (0.54, 0.5))
            normalize_image(raw_11, (SQUARE, SQUARE), final_11, (0.5, 0.5))
            generated.extend([str(final_235.relative_to(pack)), str(final_11.relative_to(pack))])
            print(f"生成：{final_235}")
            print(f"生成：{final_11}")
            continue

        page_title = ""
        for line in text.splitlines():
            if line.startswith("- 页面标题："):
                page_title = line.split("：", 1)[1].strip()
                break
        file_name = ""
        for line in text.splitlines():
            if line.startswith("- 输出文件名："):
                file_name = line.split("：", 1)[1].strip()
                break
        final = images_dir / normalize_output_filename(prompt_path, file_name, slug(page_title))
        stem_keyword = slug(page_title)
        existing_body = find_best_existing_raw(raw_dir, stem_keyword, (BODY_W, BODY_H), (0.52, 0.5), BODY_LAYOUTS, BODY_SAFETY_THRESHOLD)
        raw, _ = existing_body or generate_safe_raw(
            ark_script, config, raw_dir, f"{pack.name[:18]}-{stem_keyword}", args.model, args.size, args.timeout,
            BODY_LAYOUTS, BODY_SAFETY_THRESHOLD, text, (BODY_W, BODY_H), (0.52, 0.5)
        )
        normalize_image(raw, (BODY_W, BODY_H), final, (0.52, 0.5))
        generated.append(str(final.relative_to(pack)))
        print(f"生成：{final}")

    update_audit(pack, "公众号图片已改为纯无字 raw 图交付；封面与正文配图都不再叠加任何文字。", generated)


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser(description="公众号无字 raw 图生成器")
    parser.add_argument("--pack")
    parser.add_argument("--day")
    parser.add_argument("--model", default="doubao-seedream-5.0-lite")
    parser.add_argument("--size", default="2K")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    root = repo_root()
    ark_script = default_ark_script()
    config = default_config()
    if not ark_script.exists():
        raise SystemExit(f"缺少 ark helper: {ark_script}")
    pack = find_pack(root, args.pack, args.day)
    generate_pack(pack, args, ark_script, config)


if __name__ == "__main__":
    main()
