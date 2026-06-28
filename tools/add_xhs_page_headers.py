from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
BASE = Path(
    r"C:\Users\Administrator\Desktop\codex_project\social_media\06_运营中心\2026\2026-06\草稿区\小红书\20260626_小红书_普通人做AI最容易掉进的3个赚钱误区_stick风漫画版"
)
IMAGES = BASE / "images"


PAGE_HEADERS = {
    "01": "普通人做AI，最容易\n掉进的3个赚钱误区",
    "02": "误区1：一上来就先盯\n快钱",
    "03": "先跑出结果，再谈\n方法和变现",
    "04": "只有流量，没有承接\n很难有结果",
    "05": "什么都想卖，最后\n什么都卖不动",
    "06": "更稳的顺序：结果 -> 方法\n-> 变现",
}


PAGE_LAYOUTS = {
    "default": {
        "bubble_box": (540, 42, 1430, 220),
        "font_start": 70,
        "font_min": 34,
        "text_pad_x": 88,
        "text_pad_y": 34,
        "radius": 72,
        "outline": 5,
        "shadow": 6,
    },
    "01": {
        "bubble_box": (500, 26, 1450, 244),
        "font_start": 74,
        "font_min": 34,
        "text_pad_x": 96,
        "text_pad_y": 34,
        "radius": 84,
        "outline": 5,
        "shadow": 6,
    },
    "02": {
        "bubble_box": (520, 36, 1395, 220),
        "font_start": 62,
        "font_min": 34,
        "text_pad_x": 88,
        "text_pad_y": 30,
        "radius": 70,
        "outline": 5,
        "shadow": 6,
    },
    "03": {
        "bubble_box": (500, 36, 1405, 220),
        "font_start": 60,
        "font_min": 32,
        "text_pad_x": 90,
        "text_pad_y": 32,
        "radius": 70,
        "outline": 5,
        "shadow": 6,
    },
    "04": {
        "bubble_box": (520, 36, 1420, 220),
        "font_start": 60,
        "font_min": 32,
        "text_pad_x": 90,
        "text_pad_y": 32,
        "radius": 70,
        "outline": 5,
        "shadow": 6,
    },
    "05": {
        "bubble_box": (500, 36, 1425, 226),
        "font_start": 60,
        "font_min": 32,
        "text_pad_x": 92,
        "text_pad_y": 34,
        "radius": 72,
        "outline": 5,
        "shadow": 6,
    },
    "06": {
        "bubble_box": (160, 18, 1120, 224),
        "font_start": 68,
        "font_min": 30,
        "text_pad_x": 98,
        "text_pad_y": 34,
        "radius": 84,
        "outline": 5,
        "shadow": 6,
    },
}


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    forced_lines = text.splitlines()
    lines: list[str] = []
    for raw_line in forced_lines:
        current = ""
        for ch in raw_line:
            candidate = current + ch
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if not current or bbox[2] - bbox[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_lines: int,
    start: int,
    min_size: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(start, min_size - 1, -2):
        font = ImageFont.truetype(str(FONT_BOLD), size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = ImageFont.truetype(str(FONT_BOLD), min_size)
    return font, wrap_text(draw, text, font, max_width)


def draw_bubble(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, outline: int, shadow: int) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(
        (x1 + shadow, y1 + shadow, x2 + shadow, y2 + shadow),
        radius=radius,
        fill="#FFFFFF",
        outline="#111111",
        width=2,
    )
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill="#FFFFFF",
        outline="#111111",
        width=outline,
    )


def add_header(image_path: Path, page_no: str, header: str) -> Path:
    image = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    layout = PAGE_LAYOUTS.get(page_no, PAGE_LAYOUTS["default"])

    bubble_box = tuple(int(v) for v in layout["bubble_box"])
    draw_bubble(
        draw,
        bubble_box,
        radius=int(layout["radius"]),
        outline=int(layout["outline"]),
        shadow=int(layout["shadow"]),
    )

    text_pad_x = int(layout["text_pad_x"])
    text_pad_y = int(layout["text_pad_y"])
    max_width = (bubble_box[2] - bubble_box[0]) - text_pad_x * 2
    font, lines = fit_font(
        draw,
        header,
        max_width=max_width,
        max_lines=2,
        start=int(layout["font_start"]),
        min_size=int(layout["font_min"]),
    )

    line_gap = max(10, font.size // 5)
    line_heights: list[int] = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    text_block_height = sum(line_heights) + line_gap * (len(lines) - 1)
    bubble_height = bubble_box[3] - bubble_box[1]
    y = bubble_box[1] + max(text_pad_y, (bubble_height - text_block_height) // 2 - 4)

    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = bubble_box[0] + ((bubble_box[2] - bubble_box[0]) - line_width) // 2
        draw.text((x, y), line, font=font, fill="#111111")
        y += line_heights[idx] + line_gap

    out = image_path.with_name(f"{page_no}_bubble.png")
    image.save(out)
    return out


def main() -> int:
    outputs: list[Path] = []
    for page_no, text in PAGE_HEADERS.items():
        matches = sorted(
            path
            for path in IMAGES.glob(f"{page_no}_*.png")
            if "_加标题" not in path.stem and not path.stem.endswith("_bubble") and path.name != f"{page_no}_bubble.png"
        )
        if not matches:
            continue
        source = matches[-1]
        outputs.append(add_header(source, page_no, text))

    for item in outputs:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
