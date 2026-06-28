from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT = r"C:\Windows\Fonts\msyhbd.ttc"


def wrap_text(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        current += ch
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def load_font(font_path: str, font_size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path, font_size)


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    font_path: str,
    block: dict,
) -> None:
    x = block["x"]
    y = block["y"]
    width = block["width"]
    text = block["text"]
    font_size = block.get("font_size", 64)
    line_gap = block.get("line_gap", 16)
    max_chars = block.get("max_chars", 8)
    align = block.get("align", "center")
    text_color = block.get("text_color", "#111111")
    bg_color = block.get("bg_color")
    padding = block.get("padding", 24)
    radius = block.get("radius", 24)
    border_color = block.get("border_color")
    border_width = block.get("border_width", 2)

    font = load_font(font_path, font_size)
    lines = wrap_text(text, max_chars)
    bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in bboxes]
    heights = [box[3] - box[1] for box in bboxes]
    content_h = sum(heights) + line_gap * max(len(lines) - 1, 0)
    block_h = content_h + padding * 2

    if bg_color:
        draw.rounded_rectangle(
            (x, y, x + width, y + block_h),
            radius=radius,
            fill=bg_color,
            outline=border_color,
            width=border_width if border_color else 0,
        )

    cy = y + padding
    for line, w, h in zip(lines, widths, heights):
        if align == "left":
            tx = x + padding
        elif align == "right":
            tx = x + width - padding - w
        else:
            tx = x + (width - w) / 2
        draw.text((tx, cy), line, font=font, fill=text_color)
        cy += h + line_gap


def draw_patch(draw: ImageDraw.ImageDraw, patch: dict) -> None:
    x = patch["x"]
    y = patch["y"]
    width = patch["width"]
    height = patch["height"]
    color = patch.get("color", "#FFFFFF")
    radius = patch.get("radius", 0)
    if radius > 0:
        draw.rounded_rectangle((x, y, x + width, y + height), radius=radius, fill=color)
    else:
        draw.rectangle((x, y, x + width, y + height), fill=color)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--font", default=DEFAULT_FONT)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGBA")
    draw = ImageDraw.Draw(image)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))

    for patch in spec.get("patches", []):
        draw_patch(draw, patch)

    for block in spec.get("texts", []):
        draw_text_block(draw, args.font, block)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
