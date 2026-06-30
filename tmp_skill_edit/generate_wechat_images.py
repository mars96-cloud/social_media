from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageStat


COVER_W = 1408
COVER_H = 600
SQUARE = 1080
BODY_W = 1280
BODY_H = 720
ACCENT = "#F47C20"
TEXT_MAIN = "#141414"
TEXT_SECONDARY = "#3D3D3D"
PANEL_BORDER = (255, 255, 255, 150)
BODY_SAFETY_THRESHOLD = 0.030
COVER_SAFETY_THRESHOLD = 0.025

BODY_LAYOUTS = [
    {
        "name": "right_tall",
        "box": (0.57, 0.07, 0.95, 0.68),
        "accent_side": "left",
        "prompt_hint": "画面右侧约 35% 到 40% 区域必须保留干净留白，不能放主体角色、脸、手、核心道具、箭头或大结构，留给后期中文信息面板。",
    },
    {
        "name": "left_tall",
        "box": (0.05, 0.07, 0.43, 0.68),
        "accent_side": "left",
        "prompt_hint": "画面左侧约 35% 到 40% 区域必须保留干净留白，不能放主体角色、脸、手、核心道具、箭头或大结构，留给后期中文信息面板。",
    },
    {
        "name": "top_wide",
        "box": (0.08, 0.06, 0.92, 0.34),
        "accent_side": "top",
        "prompt_hint": "画面上方约 28% 高度必须保持大块干净留白，主体放在中下部，不要让脸、手、主道具进入上方标题区。",
    },
    {
        "name": "right_compact",
        "box": (0.63, 0.10, 0.94, 0.58),
        "accent_side": "left",
        "prompt_hint": "画面右上到右中区域需要一块更紧凑的干净留白，适合较短信息面板，主体动作必须退到左侧或中下部。",
    },
    {
        "name": "left_compact",
        "box": (0.06, 0.10, 0.37, 0.58),
        "accent_side": "left",
        "prompt_hint": "画面左上到左中区域需要一块更紧凑的干净留白，适合较短信息面板，主体动作必须退到右侧或中下部。",
    },
    {
        "name": "bottom_wide",
        "box": (0.10, 0.60, 0.90, 0.88),
        "accent_side": "top",
        "prompt_hint": "画面下方约 25% 到 30% 高度必须留出干净横向留白，主体和关键道具上移，不要让主结构压进下方信息区。",
    },
]

COVER_LAYOUTS = [
    {
        "name": "left_top",
        "box": (0.08, 0.08, 0.56, 0.44),
        "accent_side": "top",
        "prompt_hint": "封面左上区域必须保持大块干净留白，留给后期主标题与副标题，主体冲突动作放在中部偏右。",
    },
    {
        "name": "center_top",
        "box": (0.20, 0.08, 0.80, 0.42),
        "accent_side": "top",
        "prompt_hint": "封面上方中间区域必须保持大块干净留白，留给后期主标题与副标题，主体冲突动作放在中下部。",
    },
    {
        "name": "right_top",
        "box": (0.44, 0.08, 0.92, 0.44),
        "accent_side": "top",
        "prompt_hint": "封面右上区域必须保持大块干净留白，留给后期主标题与副标题，主体冲突动作放在中部偏左。",
    },
    {
        "name": "left_mid",
        "box": (0.06, 0.18, 0.48, 0.58),
        "accent_side": "top",
        "prompt_hint": "封面左中区域必须保留一块规整的留白区，适合中等长度标题，主体动作避开左半区。",
    },
    {
        "name": "right_mid",
        "box": (0.52, 0.18, 0.94, 0.58),
        "accent_side": "top",
        "prompt_hint": "封面右中区域必须保留一块规整的留白区，适合中等长度标题，主体动作避开右半区。",
    },
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
    raise SystemExit("未找到 social_media 工作区根目录。请在工程目录下运行。")


def default_ark_script() -> Path:
    return Path.home() / ".codex" / "skills" / "ark-image-generation" / "scripts" / "ark_image.py"


def default_config() -> Path | None:
    primary = Path.home() / ".codex" / "apis.json"
    if primary.exists():
        return primary
    return None


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
    temp_path.replace(target_path)


def extract_field(text: str, name: str) -> str:
    match = re.search(rf"^- {re.escape(name)}：(.+)$", text, re.M)
    return match.group(1).strip() if match else ""


def slug(name: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "", name)
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


def parse_size(size: str) -> tuple[int, int]:
    normalized = size.strip().lower()
    if normalized == "2k":
        return 2048, 2048
    if "x" in normalized:
        w, h = normalized.split("x", 1)
        return int(w), int(h)
    raise ValueError(f"无法识别尺寸：{size}")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf" if bold else r"C:\Windows\Fonts\simsun.ttc"),
    ]
    for item in candidates:
        if item.exists():
            return ImageFont.truetype(str(item), size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=0)
    return box[2] - box[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=0)
    return box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        probe = current + ch
        if text_width(draw, probe, fnt) <= max_width or not current:
            current = probe
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_lines: int, start: int, minimum: int, bold: bool = True) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(start, minimum - 1, -2):
        fnt = font(size, bold=bold)
        lines = wrap_text(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
    fnt = font(minimum, bold=bold)
    return fnt, wrap_text(draw, text, fnt, max_width)


def multiline_height(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.ImageFont, gap: int) -> int:
    if not lines:
        return 0
    return sum(text_height(draw, line, fnt) for line in lines) + gap * (len(lines) - 1)


def candidate_score(base_rgb: Image.Image, box: tuple[int, int, int, int]) -> float:
    crop = base_rgb.crop(box)
    gray = crop.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0]
    lum_mean = ImageStat.Stat(gray).mean[0]
    rgb_stat = ImageStat.Stat(crop)
    r, g, b = rgb_stat.mean
    channel_gap = (abs(r - g) + abs(r - b) + abs(g - b)) / 3

    occupancy = 0
    strong_occupancy = 0
    pixels = crop.load()
    width, height = crop.size
    sample_step = max(1, min(width, height) // 80)
    total_samples = 0
    for y in range(0, height, sample_step):
        for x in range(0, width, sample_step):
            pr, pg, pb = pixels[x, y]
            total_samples += 1
            dist_white = math.sqrt((255 - pr) ** 2 + (255 - pg) ** 2 + (255 - pb) ** 2)
            chroma = max(pr, pg, pb) - min(pr, pg, pb)
            if dist_white > 22 or chroma > 14 or min(pr, pg, pb) < 245:
                occupancy += 1
            if dist_white > 42 or chroma > 24 or min(pr, pg, pb) < 232:
                strong_occupancy += 1
    occupancy_ratio = occupancy / max(1, total_samples)
    strong_ratio = strong_occupancy / max(1, total_samples)

    center_penalty = 0.0
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    img_cx = base_rgb.size[0] / 2
    img_cy = base_rgb.size[1] / 2
    if abs(cx - img_cx) < base_rgb.size[0] * 0.16 and abs(cy - img_cy) < base_rgb.size[1] * 0.22:
        center_penalty = 90.0

    darkness_penalty = max(0, 192 - lum_mean) * 0.8
    occupancy_penalty = occupancy_ratio * 520 + strong_ratio * 760
    color_penalty = channel_gap * 0.9
    return edge_mean + darkness_penalty + occupancy_penalty + color_penalty + center_penalty


def choose_best_box(base_rgb: Image.Image, boxes: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    ranked = sorted(((candidate_score(base_rgb, box), box) for box in boxes), key=lambda item: item[0])
    return ranked[0][1]


def box_from_layout(img: Image.Image, layout: dict) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = layout["box"]
    w, h = img.size
    return (int(w * x1), int(h * y1), int(w * x2), int(h * y2))


def occupancy_ratio(base_rgb: Image.Image, box: tuple[int, int, int, int]) -> float:
    crop = base_rgb.crop(box)
    gray = crop.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_pixels = edges.load()
    pixels = crop.load()
    width, height = crop.size
    sample_step = max(1, min(width, height) // 90)
    occupied = 0
    total = 0
    for y in range(0, height, sample_step):
        for x in range(0, width, sample_step):
            r, g, b = pixels[x, y]
            total += 1
            dist_white = math.sqrt((255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2)
            chroma = max(r, g, b) - min(r, g, b)
            edge_strength = edge_pixels[x, y]
            if (
                dist_white > 22
                or chroma > 12
                or min(r, g, b) < 246
                or edge_strength > 26
            ):
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
    prompt_builder,
    prompt_text: str,
    target_size: tuple[int, int],
    centering: tuple[float, float],
) -> tuple[Path, dict]:
    last_result = ""
    for layout in layouts:
        prompt = prompt_builder(prompt_text, layout)
        raw = run_ark_generate(ark_script, config, prompt, out_dir, f"{prefix}-{layout['name']}", model, size, timeout)
        fitted = fit_image(Image.open(raw).convert("RGB"), target_size, centering)
        occ = occupancy_ratio(fitted, box_from_layout(fitted, layout))
        last_result = f"{layout['name']}={occ:.3f}"
        if occ <= threshold:
            return raw, layout
    raise RuntimeError(f"未找到可安全叠字的 raw 图，所有布局都超出遮挡阈值。最后一次检测：{last_result}")


def draw_glass_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill_alpha: int,
    border_alpha: int,
    radius: int,
    accent_side: str | None = None,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, fill_alpha), outline=(255, 255, 255, border_alpha), width=2)
    if accent_side == "top":
        draw.rounded_rectangle((x1 + 18, y1 + 14, x1 + 190, y1 + 28), radius=7, fill=ACCENT)
    if accent_side == "left":
        draw.rounded_rectangle((x1 + 14, y1 + 18, x1 + 28, y2 - 18), radius=7, fill=ACCENT)


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
            fitted = fit_image(Image.open(raw).convert("RGB"), target_size, centering)
        except Exception:
            continue
        layout = select_layout_by_threshold(fitted, layouts, threshold)
        if layout is None:
            continue
        score = candidate_score(fitted, box_from_layout(fitted, layout))
        matched.append((score, raw, layout))
    if not matched:
        return None
    matched.sort(key=lambda item: item[0])
    _, raw, layout = matched[0]
    return raw, layout


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    box: tuple[int, int, int, int],
    fnt: ImageFont.ImageFont,
    fill: str,
    stroke_width: int,
    stroke_fill: str,
    gap: int,
) -> int:
    total_h = multiline_height(draw, lines, fnt, gap)
    y = box[1] + max(0, (box[3] - box[1] - total_h) // 2)
    for line in lines:
        tw = text_width(draw, line, fnt)
        draw.text(((box[0] + box[2] - tw) / 2, y), line, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        y += text_height(draw, line, fnt) + gap
    return y


def draw_bullets(
    draw: ImageDraw.ImageDraw,
    bullets: list[str],
    box: tuple[int, int, int, int],
    fnt: ImageFont.ImageFont,
    fill: str,
    stroke_fill: str,
) -> None:
    bullet_gap = 14
    line_gap = 8
    bullet_x = box[0] + 10
    content_x = bullet_x + 28
    y = box[1]
    for bullet in bullets:
        lines = wrap_text(draw, bullet, fnt, box[2] - content_x - 8)
        dot_y = y + max(2, text_height(draw, lines[0], fnt) // 5)
        draw.ellipse((bullet_x, dot_y + 4, bullet_x + 10, dot_y + 14), fill=ACCENT)
        for line in lines:
            draw.text((content_x, y), line, font=fnt, fill=fill, stroke_width=2, stroke_fill=stroke_fill)
            y += text_height(draw, line, fnt) + line_gap
        y += bullet_gap


def estimate_bullet_height(draw: ImageDraw.ImageDraw, bullets: list[str], fnt: ImageFont.ImageFont, width: int) -> int:
    total = 0
    for bullet in bullets:
        lines = wrap_text(draw, bullet, fnt, width)
        total += multiline_height(draw, lines, fnt, 8) + 14
    return total


def fit_body_layout(
    draw: ImageDraw.ImageDraw,
    title: str,
    bullets: list[str],
    summary: str,
    width: int,
    height: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, list[str]]:
    for title_size in range(56, 33, -2):
        title_font = font(title_size, bold=True)
        title_lines = wrap_text(draw, title, title_font, width)
        if len(title_lines) > 3:
            continue
        for bullet_size in range(28, 21, -1):
            bullet_font = font(bullet_size, bold=False)
            for summary_size in range(24, 19, -1):
                summary_font = font(summary_size, bold=False)
                summary_lines = wrap_text(draw, summary, summary_font, width - 8)[:2] if summary else []
                title_h = multiline_height(draw, title_lines, title_font, 6)
                bullet_h = estimate_bullet_height(draw, bullets, bullet_font, width - 36)
                summary_h = multiline_height(draw, summary_lines, summary_font, 4) + (28 if summary_lines else 0)
                total = title_h + 26 + bullet_h + summary_h + 38
                if total <= height:
                    return title_font, title_lines, bullet_font, summary_font, summary_lines
    title_font = font(34, bold=True)
    return title_font, wrap_text(draw, title, title_font, width)[:3], font(22, bold=False), font(19, bold=False), wrap_text(draw, summary, font(19, bold=False), width - 8)[:2] if summary else []


def build_body_prompt(task_md: str) -> str:
    return build_body_prompt_for_layout(task_md, None)


def build_body_prompt_for_layout(task_md: str, layout: dict | None) -> str:
    page_title = extract_field(task_md, "页面标题")
    visible = extract_field(task_md, "主文案")
    idea = extract_field(task_md, "核心判断")
    structure = extract_field(task_md, "结构类型")
    action = extract_field(task_md, "土豆崽动作")
    props = extract_field(task_md, "道具元素")
    notes = extract_field(task_md, "短标注")
    composition = extract_field(task_md, "构图要求")
    layout_hint = layout["prompt_hint"] if layout else "必须明显预留一块后期中文叠字安全区。"
    return f"""
请生成一张公众号正文配图底图，不要生成任何文字。

画幅要求：
16:9 横版，适合公众号正文插图，后续会在本地叠加中文标题和短标注。

风格要求：
纯白背景，黑色手绘线稿为主，少量橙色、红色、蓝色强调。整体像怪诞但清爽的产品草图，不像 PPT，不像商业插画，不像儿童插画，不要复杂背景，不要渐变，不要阴影，不要科技感 UI。

主角要求：
主角必须是土豆崽。土豆崽是暖土豆黄色，白色圆眼，小黑点瞳孔，厚黑眉，小黑线嘴，脸型稳定，气质是呆、轴、认真、带一点坏，不卖萌。土豆崽必须承担核心动作，不能站在旁边当摆设。

角色一致性要求：
请对齐 potato-illustrations 内置锚点：
- assets/potato-ip/images/01_角色设定主图_定版.png
- assets/potato-ip/images/02_平静直视.png
- assets/potato-ip/images/03_微坏笑.png
- assets/potato-ip/images/04_生气皱眉.png
- assets/potato-ip/images/00_土豆崽20张总览.png
这是一只固定角色，不是每次重新设计的新卡通。

当前图片任务：
页面标题：{page_title}
核心判断：{idea}
结构类型：{structure}
土豆崽动作：{action}
道具元素：{props}
后续本地叠字主文案：{visible}
后续本地叠字短标注：{notes}
构图要求：{composition}

构图约束：
主视觉放在画面中下部，避免遮挡后续文字区。顶部中间预留大标题安全区，整体要聚焦一个动作和一个结构。不要太空，也不要塞满，至少保留 25% 留白。允许局部道具和箭头，但不能像正式流程图。
额外安全区要求：
{layout_hint}

禁止项：
不要生成任何文字、字母、水印、logo、标题框、信息卡框、表格框、左上角标签、页码。不要出现别的 IP，不要画成软萌吉祥物，不要做旧纸质感和米色底。
""".strip()


def build_cover_prompt(task_md: str, ratio_name: str) -> str:
    return build_cover_prompt_for_layout(task_md, ratio_name, None)


def build_cover_prompt_for_layout(task_md: str, ratio_name: str, layout: dict | None) -> str:
    hook = extract_field(task_md, "封面主标题")
    kicker = extract_field(task_md, "封面副标题")
    reason = extract_field(task_md, "点击理由")
    visual = extract_field(task_md, "主视觉")
    action = extract_field(task_md, "土豆崽动作")
    props = extract_field(task_md, "道具元素")
    emotion = extract_field(task_md, "土豆崽表情")
    composition = extract_field(task_md, "构图要求")
    layout_hint = layout["prompt_hint"] if layout else "必须明显预留一块后期标题安全区。"
    return f"""
请生成一张公众号封面底图，不要生成任何文字。

画幅要求：
{ratio_name} 横版强视觉封面底图，用于公众号缩略图，需要小图可读性强。

风格要求：
纯白背景或极浅白背景，黑色手绘线稿为主，少量橙色和红色做冲击点。整体像有戏剧张力的极简怪诞草图，不像信息卡，不像 PPT，不像儿童海报，不要复杂背景，不要渐变，不要阴影。

主角要求：
主角必须是土豆崽，保持固定 IP 一致性。它要亲自制造视觉冲突，不能站在旁边。

封面信息：
封面主标题会后期本地叠加：{hook}
封面副标题会后期本地叠加：{kicker}
点击理由：{reason}
主视觉：{visual}
土豆崽动作：{action}
土豆崽表情：{emotion}
道具元素：{props}
构图要求：{composition}

构图约束：
画面中心必须有单一强主体。左中或右中形成显眼冲突物件，给后期标题预留干净安全区。缩略图一眼就能看到“别先做自动化，先把内容工作流搭起来”的张力，但不要直接写字。
额外安全区要求：
{layout_hint}

禁止项：
不要生成任何文字、字母、水印、logo、边框、信息卡、标语。不要商务照片感，不要复杂场景，不要米色，不要噪点纹理，不要可爱卖萌风。
""".strip()


def run_ark_generate(ark_script: Path, config: Path | None, prompt: str, out_dir: Path, prefix: str, model: str | None, size: str, timeout: int) -> Path:
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
    completed = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout + 60)
    if completed.returncode != 0:
        raise RuntimeError((completed.stdout + "\n" + completed.stderr).strip())
    after = set(out_dir.glob("*"))
    new_files = sorted([p for p in after - before if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}], key=lambda p: p.stat().st_mtime)
    if not new_files:
        raise RuntimeError("Ark 返回成功但未发现新图片文件。")
    return new_files[-1]


def normalize_image(raw_image: Path, target_size: tuple[int, int], target_path: Path, centering: tuple[float, float]) -> None:
    img = fit_image(Image.open(raw_image).convert("RGB"), target_size, centering)
    save_rgb_image(img, target_path, quality=95)


def fit_image(img: Image.Image, target_size: tuple[int, int], centering: tuple[float, float]) -> Image.Image:
    return ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS, centering=centering)


def draw_soft_strip(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill_alpha: int) -> None:
    draw.rounded_rectangle(box, radius=18, fill=(255, 255, 255, fill_alpha))


def overlay_cover(base_image: Path, target_path: Path, title: str, subtitle: str, layout: dict | None = None) -> None:
    img = Image.open(base_image).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    base_rgb = img.convert("RGB")
    chosen_layout = layout or select_layout_by_threshold(base_rgb, COVER_LAYOUTS, COVER_SAFETY_THRESHOLD)
    if chosen_layout is None:
        raise RuntimeError("封面缺少安全叠字区，禁止强行叠字。")
    panel = box_from_layout(base_rgb, chosen_layout)
    draw_glass_panel(draw, panel, fill_alpha=180, border_alpha=140, radius=34, accent_side=chosen_layout["accent_side"])

    inner = (panel[0] + 34, panel[1] + 34, panel[2] - 34, panel[3] - 26)
    title_font, title_lines = fit_font(draw, title, inner[2] - inner[0], 2, 100, 58, bold=True)
    subtitle_font, subtitle_lines = fit_font(draw, subtitle, inner[2] - inner[0] - 20, 2, 34, 24, bold=False)

    title_h = multiline_height(draw, title_lines, title_font, 6)
    subtitle_h = multiline_height(draw, subtitle_lines, subtitle_font, 6)
    title_box = (inner[0], inner[1] + 10, inner[2], inner[1] + 10 + title_h + 8)
    draw_centered_lines(draw, title_lines, title_box, title_font, TEXT_MAIN, 3, "#FFFFFF", 6)

    sub_top = title_box[3] + 16
    if subtitle_lines:
        for line in subtitle_lines:
            tw = text_width(draw, line, subtitle_font)
            draw.text(((inner[0] + inner[2] - tw) / 2, sub_top), line, font=subtitle_font, fill=TEXT_SECONDARY, stroke_width=2, stroke_fill="#FFFFFF")
            sub_top += text_height(draw, line, subtitle_font) + 6

    accent_y = panel[3] - 26
    draw.rounded_rectangle((inner[0], accent_y, min(inner[0] + 260, inner[2]), accent_y + 8), radius=4, fill=ACCENT)

    merged = Image.alpha_composite(img, overlay).convert("RGB")
    save_rgb_image(merged, target_path, quality=95)


def overlay_body(base_image: Path, target_path: Path, title: str, bullets: list[str], summary: str, layout: dict | None = None) -> None:
    img = Image.open(base_image).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    base_rgb = img.convert("RGB")
    chosen_layout = layout or select_layout_by_threshold(base_rgb, BODY_LAYOUTS, BODY_SAFETY_THRESHOLD)
    if chosen_layout is None:
        raise RuntimeError("正文图缺少安全叠字区，禁止强行叠字。")
    panel = box_from_layout(base_rgb, chosen_layout)
    draw_glass_panel(draw, panel, fill_alpha=168, border_alpha=132, radius=30, accent_side=chosen_layout["accent_side"])

    inner = (panel[0] + 34, panel[1] + 28, panel[2] - 28, panel[3] - 24)
    title_font, title_lines, bullet_font, summary_font, summary_lines = fit_body_layout(
        draw,
        title,
        bullets,
        summary,
        inner[2] - inner[0],
        inner[3] - inner[1],
    )

    title_box = (inner[0], inner[1], inner[2], inner[1] + multiline_height(draw, title_lines, title_font, 6) + 4)
    title_bottom = draw_centered_lines(draw, title_lines, title_box, title_font, TEXT_MAIN, 2, "#FFFFFF", 6)

    draw.rounded_rectangle((inner[0], title_bottom + 8, min(inner[0] + 110, inner[2]), title_bottom + 18), radius=4, fill=ACCENT)

    bullet_top = title_bottom + 30
    summary_h = multiline_height(draw, summary_lines, summary_font, 4)
    summary_box_h = summary_h + 28 if summary_lines else 0
    bullet_box = (inner[0], bullet_top, inner[2], inner[3] - summary_box_h - 18)
    draw_bullets(draw, bullets, bullet_box, bullet_font, TEXT_SECONDARY, "#FFFFFF")

    if summary_lines:
        summary_box = (inner[0], inner[3] - summary_box_h, inner[2], inner[3])
        draw.rounded_rectangle(summary_box, radius=18, fill=(255, 255, 255, 108))
        draw_centered_lines(draw, summary_lines, summary_box, summary_font, TEXT_SECONDARY, 2, "#FFFFFF", 4)

    merged = Image.alpha_composite(img, overlay).convert("RGB")
    save_rgb_image(merged, target_path, quality=95)


def find_pack(root: Path, pack_arg: str | None, day: str | None) -> Path:
    if pack_arg:
        pack = Path(pack_arg)
        if not pack.is_absolute():
            pack = (root / pack).resolve()
        if not pack.exists():
            raise SystemExit(f"指定稿包不存在：{pack}")
        return pack
    if not day:
        raise SystemExit("请提供 --pack 或 --day。")
    day_dir = root / "06_运营中心" / "2026" / "2026-07" / "公众号" / day
    if not day_dir.exists():
        raise SystemExit(f"日期目录不存在：{day_dir}")
    packs = [p for p in day_dir.iterdir() if p.is_dir()]
    if len(packs) != 1:
        raise SystemExit(f"日期目录下稿包数量异常，期望 1 个，实际 {len(packs)}：{day_dir}")
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
            title = extract_field(text, "封面主标题")
            subtitle = extract_field(text, "封面副标题")
            final_235 = images_dir / "01_公众号封面_标题版_2.35比1.png"
            final_11 = images_dir / "01_公众号封面_标题版_1比1.png"
            if final_235.exists() and final_11.exists() and not args.force:
                continue
            existing_cover_235 = find_best_existing_raw(raw_dir, "cover235", (COVER_W, COVER_H), (0.54, 0.5), COVER_LAYOUTS, COVER_SAFETY_THRESHOLD)
            if existing_cover_235:
                raw_235, layout_235 = existing_cover_235
            else:
                raw_235, layout_235 = generate_safe_raw(
                    ark_script,
                    config,
                    raw_dir,
                    f"{pack.name[:18]}-cover235",
                    args.model,
                    args.size,
                    args.timeout,
                    COVER_LAYOUTS,
                    COVER_SAFETY_THRESHOLD,
                    lambda prompt_text, layout: build_cover_prompt_for_layout(prompt_text, "2.35:1", layout),
                    text,
                    (COVER_W, COVER_H),
                    (0.54, 0.5),
                )
            existing_cover_11 = find_best_existing_raw(raw_dir, "cover11", (SQUARE, SQUARE), (0.5, 0.5), COVER_LAYOUTS, COVER_SAFETY_THRESHOLD)
            if existing_cover_11:
                raw_11, layout_11 = existing_cover_11
            else:
                raw_11, layout_11 = generate_safe_raw(
                    ark_script,
                    config,
                    raw_dir,
                    f"{pack.name[:18]}-cover11",
                    args.model,
                    args.size,
                    args.timeout,
                    COVER_LAYOUTS,
                    COVER_SAFETY_THRESHOLD,
                    lambda prompt_text, layout: build_cover_prompt_for_layout(prompt_text, "1:1", layout),
                    text,
                    (SQUARE, SQUARE),
                    (0.5, 0.5),
                )

            base_235 = images_dir / "01_公众号封面_底图_2.35比1.png"
            base_11 = images_dir / "01_公众号封面_底图_1比1.png"
            normalize_image(raw_235, (COVER_W, COVER_H), base_235, (0.54, 0.5))
            normalize_image(raw_11, (SQUARE, SQUARE), base_11, (0.5, 0.5))
            overlay_cover(base_235, final_235, title, subtitle, layout_235)
            overlay_cover(base_11, final_11, title, subtitle, layout_11)
            generated.extend([str(base_235.relative_to(pack)), str(base_11.relative_to(pack)), str(final_235.relative_to(pack)), str(final_11.relative_to(pack))])
            print(f"生成：{final_235}")
            print(f"生成：{final_11}")
            continue

        page_title = extract_field(text, "页面标题")
        title = extract_field(text, "主文案") or page_title
        bullets = [item.strip() for item in extract_field(text, "核心提炼").split("｜") if item.strip()]
        summary = extract_field(text, "收束句")
        file_name = extract_field(text, "输出文件名")
        normalized_name = normalize_output_filename(prompt_path, file_name, slug(page_title))
        final = images_dir / normalized_name
        if final.exists() and not args.force:
            continue
        stem_keyword = slug(page_title)
        existing_body = find_best_existing_raw(raw_dir, stem_keyword, (BODY_W, BODY_H), (0.52, 0.5), BODY_LAYOUTS, BODY_SAFETY_THRESHOLD)
        if existing_body:
            raw, body_layout = existing_body
        else:
            raw, body_layout = generate_safe_raw(
                ark_script,
                config,
                raw_dir,
                f"{pack.name[:18]}-{stem_keyword}",
                args.model,
                args.size,
                args.timeout,
                BODY_LAYOUTS,
                BODY_SAFETY_THRESHOLD,
                build_body_prompt_for_layout,
                text,
                (BODY_W, BODY_H),
                (0.52, 0.5),
            )
        normalize_image(raw, (BODY_W, BODY_H), final, (0.52, 0.5))
        overlay_body(final, final, title, bullets, summary, body_layout)
        generated.append(str(final.relative_to(pack)))
        print(f"生成：{final}")

    update_audit(pack, "正式图片已全部通过 potato-illustrations 生成并完成本地叠字。", generated)


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser(description="通过 potato-illustrations 入口生成公众号正式图片。")
    parser.add_argument("--pack", help="公众号稿包目录，支持绝对路径或相对 social_media 根目录")
    parser.add_argument("--day", help="只处理某一天，例如 2026-07-02")
    parser.add_argument("--model", default="doubao-seedream-5.0-lite", help="Ark/Agent Plan 图片模型 ID")
    parser.add_argument("--size", default="2K", help="生成尺寸，默认 2K")
    parser.add_argument("--timeout", type=int, default=180, help="单次生成超时秒数")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的正式成品")
    args = parser.parse_args()

    root = repo_root()
    ark_script = default_ark_script()
    config = default_config()
    if not ark_script.exists():
        raise SystemExit(f"缺少 ark-image-generation helper：{ark_script}")

    pack = find_pack(root, args.pack, args.day)
    generate_pack(pack, args, ark_script, config)


if __name__ == "__main__":
    main()
