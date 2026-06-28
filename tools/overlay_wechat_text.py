from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT = r"C:\Windows\Fonts\msyh.ttc"


def wrap_text(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        if len(current) >= max_chars:
            lines.append(current)
            current = ch
        else:
            current += ch
    if current:
        lines.append(current)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--x", type=int, default=110)
    parser.add_argument("--y", type=int, default=80)
    parser.add_argument("--font-size", type=int, default=110)
    parser.add_argument("--max-chars", type=int, default=10)
    parser.add_argument("--line-gap", type=int, default=20)
    parser.add_argument("--box-padding", type=int, default=28)
    parser.add_argument("--text-color", default="#111111")
    parser.add_argument("--bg-color", default="#FFFFFF")
    parser.add_argument("--font", default=DEFAULT_FONT)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGBA")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(args.font, args.font_size)

    lines = wrap_text(args.title, args.max_chars)
    bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in bboxes]
    heights = [box[3] - box[1] for box in bboxes]

    total_w = max(widths) + args.box_padding * 2
    total_h = sum(heights) + args.line_gap * (len(lines) - 1) + args.box_padding * 2

    x0 = args.x
    y0 = args.y
    x1 = x0 + total_w
    y1 = y0 + total_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=args.bg_color)

    cy = y0 + args.box_padding
    for line, w, h in zip(lines, widths, heights):
        tx = x0 + (total_w - w) / 2
        draw.text((tx, cy), line, font=font, fill=args.text_color)
        cy += h + args.line_gap

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
