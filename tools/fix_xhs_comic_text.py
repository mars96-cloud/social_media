from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_REGULAR = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
INK = "#111111"
WHITE = "#FFFFFF"
BG = "#F8F3E6"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size=size)


def rounded_box(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    radius: int,
    fill: str = WHITE,
) -> None:
    draw.rounded_rectangle(rect, radius=radius, fill=fill)


def split_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    fnt: ImageFont.FreeTypeFont,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for ch in paragraph:
            candidate = current + ch
            bbox = draw.textbbox((0, 0), candidate, font=fnt)
            if current and (bbox[2] - bbox[0]) > max_width:
                lines.append(current)
                current = ch
            else:
                current = candidate
        lines.append(current)
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    rect: tuple[int, int, int, int],
    start_size: int,
    min_size: int,
    bold: bool = True,
    line_gap: int = 8,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    x1, y1, x2, y2 = rect
    max_width = x2 - x1
    max_height = y2 - y1
    for size in range(start_size, min_size - 1, -2):
        fnt = font(size, bold=bold)
        lines = split_lines(draw, text, max_width, fnt)
        line_height = size + line_gap
        if len(lines) * line_height <= max_height:
            return fnt, lines, line_height
    fnt = font(min_size, bold=bold)
    return fnt, split_lines(draw, text, max_width, fnt), min_size + line_gap


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    start_size: int,
    min_size: int,
    bold: bool = True,
    align: str = "center",
    line_gap: int = 8,
    fill: str = INK,
) -> None:
    fnt, lines, line_height = fit_text(draw, text, rect, start_size, min_size, bold=bold, line_gap=line_gap)
    x1, y1, x2, y2 = rect
    total_h = len(lines) * line_height
    y = y1 + max(0, (y2 - y1 - total_h) // 2)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        width = bbox[2] - bbox[0]
        if align == "left":
            x = x1
        elif align == "right":
            x = x2 - width
        else:
            x = x1 + max(0, (x2 - x1 - width) // 2)
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height


def draw_vertical_text(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    size: int,
) -> None:
    fnt = font(size, bold=True)
    x1, y1, x2, y2 = rect
    chars = list(text)
    slot = (y2 - y1) / len(chars)
    for idx, ch in enumerate(chars):
        bbox = draw.textbbox((0, 0), ch, font=fnt)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = x1 + (x2 - x1 - w) // 2
        y = int(y1 + idx * slot + (slot - h) / 2)
        draw.text((x, y), ch, font=fnt, fill=INK)


def rebuild_comment_hook(image_path: Path) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    rounded_box(draw, (70, 55, 1970, 320), radius=40, fill=BG)
    draw_text_block(
        draw,
        (180, 95, 1860, 270),
        "普通人做AI更现实的一条路",
        start_size=86,
        min_size=62,
        bold=True,
    )

    rounded_box(draw, (220, 900, 940, 1225), radius=56, fill=WHITE)
    draw_text_block(
        draw,
        (300, 950, 860, 1175),
        "阿青：\n不用追虚的！\n先从日常AI提效\n落地就好~",
        start_size=62,
        min_size=40,
        bold=True,
        line_gap=10,
    )

    rounded_box(draw, (1160, 900, 1840, 1225), radius=56, fill=WHITE)
    draw_text_block(
        draw,
        (1240, 950, 1760, 1175),
        "周周：\n没错！先做\n能用的小方法\n才靠谱",
        start_size=62,
        min_size=40,
        bold=True,
        line_gap=10,
    )

    rounded_box(draw, (175, 1450, 1870, 1930), radius=78, fill=WHITE)
    draw_text_block(
        draw,
        (300, 1545, 1745, 1835),
        "提问：你现在更卡在提效、\n整理方法，还是结果承接？",
        start_size=66,
        min_size=44,
        bold=True,
        line_gap=14,
    )

    image.save(image_path, format="PNG")


def rebuild_stage_three(image_path: Path) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    rounded_box(draw, (15, 60, 255, 1990), radius=28, fill=WHITE)
    draw_vertical_text(draw, (40, 110, 230, 1940), "第三阶段：进入更明确的结果路径", size=40)

    rounded_box(draw, (1470, 210, 1935, 585), radius=26, fill=WHITE)
    draw_text_block(
        draw,
        (1535, 285, 1870, 510),
        "先把内部流程\n跑顺提效，把事\n情做扎实！",
        start_size=48,
        min_size=34,
        bold=True,
        align="left",
        line_gap=10,
    )

    rounded_box(draw, (1340, 770, 1940, 1180), radius=26, fill=WHITE)
    draw_text_block(
        draw,
        (1410, 850, 1870, 1110),
        "等流程稳定、结果\n清晰后，整理好资料\n和专题内容！",
        start_size=48,
        min_size=34,
        bold=True,
        align="left",
        line_gap=10,
    )

    rounded_box(draw, (1370, 1430, 1945, 1845), radius=26, fill=WHITE)
    draw_text_block(
        draw,
        (1440, 1515, 1875, 1765),
        "最后对外输出整理\n好的内容，放大成\n果更顺畅！",
        start_size=48,
        min_size=34,
        bold=True,
        align="left",
        line_gap=10,
    )

    image.save(image_path, format="PNG")


def main() -> int:
    base = Path(
        "C:/Users/Administrator/Desktop/codex_project/social_media/06_运营中心/2026/2026-06/草稿区/小红书/"
        "20260624_小红书_从AI提效到AI变现普通人更现实的一条路_漫画版/images"
    )
    rebuild_comment_hook(base / "06_评论钩子.png")
    rebuild_stage_three(base / "05_第三阶段再进入变现.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
