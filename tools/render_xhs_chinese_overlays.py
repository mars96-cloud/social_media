from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
ROOT = Path(
    r"C:\Users\Administrator\Desktop\codex_project\social_media\06_运营中心\2026\2026-07\草稿区\小红书\202607_小红书_AI科普对话选题池_stick风"
)
TMP_OUT = Path(r"C:\Users\Administrator\Desktop\codex_project\social_media\temp_render")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, min_size: int, max_lines: int = 2) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(start, min_size - 1, -2):
        font = load_font(size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = load_font(min_size)
    return font, wrap_text(draw, text, font, max_width)


def draw_round_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str = "#111111", width: int = 4, radius: int = 22) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_header(draw: ImageDraw.ImageDraw, width: int, page: dict, title: str) -> int:
    main_title = title if page["page"] == "01" else page["role"].replace("页", "")
    title_font, title_lines = fit_font(draw, main_title, width - 100, 98, 52, max_lines=1)
    y = 22
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=title_font, fill="#111111")

    subtitle = page.get("subtitle", "")
    if subtitle:
        sub_font, sub_lines = fit_font(draw, subtitle, width - 180, 24, 18, max_lines=1)
        top = y + title_font.size + 8
        sub_y = top
        for line in sub_lines:
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, sub_y), line, font=sub_font, fill="#111111")
        return top + sub_font.size + 8
    return y + title_font.size + 8


def clear_strip(draw: ImageDraw.ImageDraw, left: int, top: int, right: int, bottom: int) -> None:
    draw.rectangle((left, top, right, bottom), fill="#FFFFFF")


def estimate_header_bottom(page: dict) -> int:
    return 140 if page.get("subtitle") else 110


def find_content_bbox(image: Image.Image, threshold: int = 245) -> tuple[int, int, int, int] | None:
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    min_x, min_y = width, height
    max_x, max_y = -1, -1
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r < threshold or g < threshold or b < threshold:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
    if max_x < 0:
        return None
    return (min_x, min_y, max_x + 1, max_y + 1)


def reframe_content(image: Image.Image, header_bottom: int) -> tuple[Image.Image, tuple[int, int, int, int]]:
    width, height = image.size
    bbox = find_content_bbox(image)
    if not bbox:
        return image, (0, header_bottom, width, height)

    crop = image.crop(bbox)
    content_w = bbox[2] - bbox[0]
    content_h = bbox[3] - bbox[1]

    target_left = 0
    target_right = width
    target_top = header_bottom - 16
    target_bottom = height
    target_w = target_right - target_left
    target_h = target_bottom - target_top

    scale = min(target_w / content_w, target_h / content_h) * 1.08
    new_w = int(content_w * scale)
    new_h = int(content_h * scale)
    resized = crop.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (width, height), "white")
    paste_x = (width - new_w) // 2
    paste_y = target_top
    canvas.paste(resized, (paste_x, paste_y), resized)
    return canvas, (paste_x, paste_y, paste_x + new_w, paste_y + new_h)


def draw_cloud_bubble(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: str,
    tail_side: str,
) -> None:
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1

    circles = [
        (x1 + 4, y1 + 14, x1 + 92, y1 + 90),
        (x1 + 58, y1 + 2, x1 + 190, y1 + 92),
        (x1 + 168, y1 + 0, x1 + 320, y1 + 92),
        (x1 + 292, y1 + 4, x1 + 430, y1 + 90),
        (x1 + 392, y1 + 12, x2 - 4, y1 + 86),
        (x1 + 26, y1 + 34, x2 - 26, y2 - 6),
    ]
    for c in circles:
        draw.ellipse(c, fill=fill, outline="#111111", width=3)

    if tail_side == "left":
        tail = [
            (x1 + 26, y2 - 2, x1 + 62, y2 + 24),
            (x1 + 8, y2 + 18, x1 + 34, y2 + 42),
        ]
    else:
        tail = [
            (x2 - 62, y2 - 2, x2 - 26, y2 + 24),
            (x2 - 34, y2 + 18, x2 - 8, y2 + 42),
        ]
    for c in tail:
        draw.ellipse(c, fill=fill, outline="#111111", width=3)

    font, lines = fit_font(draw, text, w - 64, 32, 20, max_lines=2)
    total_height = len(lines) * (font.size + 4)
    y = y1 + max(16, ((h - 14) - total_height) // 2)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = x1 + (w - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font, fill="#111111")
        y += font.size + 4


def overlay_page(image_path: Path, page: dict, title: str) -> Path:
    image = Image.open(image_path).convert("RGBA")
    header_bottom = estimate_header_bottom(page)

    # Reframe the base illustration first, before any text is drawn.
    image, placed = reframe_content(image, header_bottom)
    draw = ImageDraw.Draw(image)
    width, height = image.size

    body_top = draw_header(draw, width, page, title)

    # Tighten the top whitespace with a shallower clean strip.
    clear_strip(draw, 18, body_top, width - 18, min(body_top + 4, height))

    # Cloud bubbles closer to the character heads; no role labels.
    content_left, content_top, content_right, content_bottom = placed
    bubble_w = 560
    bubble_h = 128
    is_cover = page["page"] == "01"
    left_box = (
        max(8, content_left + (10 if is_cover else -10)),
        max(body_top + 2, content_top + (0 if is_cover else 18)),
        max(8, content_left + (10 if is_cover else -10)) + bubble_w,
        max(body_top + 2, content_top + (0 if is_cover else 18)) + bubble_h,
    )
    right_box = (
        min(width - bubble_w - 8, content_right - bubble_w - (20 if is_cover else 30)),
        max(body_top + 2, content_top + (6 if is_cover else 10)),
        min(width - 8, content_right - (20 if is_cover else 30)),
        max(body_top + 2, content_top + (6 if is_cover else 10)) + bubble_h,
    )
    draw_cloud_bubble(draw, left_box, page["student"], "#E9FFF0", "left")
    draw_cloud_bubble(draw, right_box, page["teacher"], "#EAF4FF", "right")

    TMP_OUT.mkdir(parents=True, exist_ok=True)
    output = TMP_OUT / f"{page['page']}_final_cn.png"
    image.save(output)
    return output


def find_latest_image(images_dir: Path, page_no: str) -> Path:
    candidates = sorted(images_dir.glob(f"{page_no}_*.png"))
    candidates = [
        p for p in candidates
        if "中文排字" not in p.stem and "final_cn" not in p.stem
    ]
    preferred = [p for p in candidates if "无字底图" in p.stem]
    if preferred:
        return preferred[-1]
    if not candidates:
        raise FileNotFoundError(f"未找到页面图片: {images_dir} / {page_no}")
    return candidates[-1]


def render_topic(topic_dir: Path) -> list[Path]:
    metadata = json.loads((topic_dir / "metadata.json").read_text(encoding="utf-8"))
    images_dir = topic_dir / "images"
    outputs: list[Path] = []
    for page in metadata["pages"][:2]:
        source = find_latest_image(images_dir, page["page"])
        outputs.append(overlay_page(source, page, metadata["title"]))
    return outputs


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: render_xhs_chinese_overlays.py <topic_dir_name>")
        return 2
    outputs = render_topic(ROOT / sys.argv[1])
    for item in outputs:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
