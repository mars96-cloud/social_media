from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


THEMES = {
    "warm-paper": {
        "bg": "#F7F1E8",
        "panel": "#FFFDF9",
        "ink": "#20342E",
        "text": "#2E5E4E",
        "accent": "#F29F58",
        "accent_2": "#E8D7C4",
        "brand": "AI趣创社",
        "shape": "bars",
    },
    "blueprint": {
        "bg": "#EAF3FF",
        "panel": "#F8FBFF",
        "ink": "#19324D",
        "text": "#315D84",
        "accent": "#4C8DFF",
        "accent_2": "#BED6FF",
        "brand": "AI工作流实验室",
        "shape": "grid",
    },
    "newsroom": {
        "bg": "#F7F4EF",
        "panel": "#FFFDFC",
        "ink": "#2E2620",
        "text": "#5E4A3D",
        "accent": "#C75B39",
        "accent_2": "#E9C7B8",
        "brand": "AI实战笔记",
        "shape": "frame",
    },
    "mint-grid": {
        "bg": "#EEF7F2",
        "panel": "#FCFFFD",
        "ink": "#17392D",
        "text": "#2F6A55",
        "accent": "#57B58A",
        "accent_2": "#CFE8DB",
        "brand": "智能体流程手册",
        "shape": "pills",
    },
    "studio-pop": {
        "bg": "#FFF4E8",
        "panel": "#FFFDFB",
        "ink": "#3A2418",
        "text": "#6B4631",
        "accent": "#FF8A3D",
        "accent_2": "#FFD0B0",
        "brand": "AI增长工作室",
        "shape": "circles",
    },
    "slate-pro": {
        "bg": "#EEF1F5",
        "panel": "#FAFCFF",
        "ink": "#1F2937",
        "text": "#475569",
        "accent": "#0EA5A3",
        "accent_2": "#B8E6E4",
        "brand": "AI流程图谱",
        "shape": "panel",
    },
}


def get_theme(theme: str) -> dict[str, str]:
    return THEMES.get(theme, THEMES["warm-paper"])


def pick_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            candidate = current + char
            width = draw.textbbox((0, 0), candidate, font=font)[2]
            if current and width > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_height: int,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, font, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * line_height), line, font=font, fill=fill)
    return y + len(lines) * line_height


def draw_card_base(size: tuple[int, int], theme: str, background_path: Path | None = None) -> Image.Image:
    palette = get_theme(theme)
    image = Image.new("RGB", size, palette["bg"])
    if background_path and background_path.exists():
        bg = Image.open(background_path).convert("RGB").resize(size)
        image = Image.blend(bg, image, 0.72)
    return image


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def draw_cover_accents(draw: ImageDraw.ImageDraw, palette: dict[str, str]) -> None:
    shape = palette["shape"]
    if shape == "grid":
        for x in range(36, 900, 44):
            draw.line((x, 24, x, 360), fill=palette["accent_2"], width=1)
        for y in range(32, 360, 40):
            draw.line((24, y, 876, y), fill=palette["accent_2"], width=1)
    elif shape == "frame":
        draw.rectangle((34, 34, 866, 349), outline=palette["accent"], width=4)
        draw.line((70, 302, 830, 302), fill=palette["accent_2"], width=3)
    elif shape == "pills":
        for y in range(58, 330, 58):
            draw.rounded_rectangle((610, y, 820, y + 20), radius=10, fill=palette["accent_2"])
    elif shape == "circles":
        draw.ellipse((620, 62, 820, 250), fill=palette["accent_2"])
        draw.ellipse((700, 180, 850, 330), fill=palette["accent"])
    elif shape == "panel":
        draw.rounded_rectangle((612, 68, 834, 304), radius=28, outline=palette["accent"], width=6)
        draw.line((640, 104, 804, 104), fill=palette["accent_2"], width=4)
        draw.line((640, 146, 782, 146), fill=palette["accent_2"], width=4)
    else:
        draw.rectangle((610, 70, 616, 308), fill=palette["accent"])
        draw.rectangle((640, 70, 646, 250), fill=palette["accent"])


def render_wechat_cover(
    output_path: Path,
    background_path: Path,
    title: str,
    subtitle: str,
    theme: str = "warm-paper",
) -> None:
    palette = get_theme(theme)
    image = draw_card_base((900, 383), theme, background_path)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 40, 550, 340), radius=24, fill=palette["panel"])
    draw_cover_accents(draw, palette)

    brand_font = pick_font(18, bold=True)
    title_font = pick_font(34, bold=True)
    sub_font = pick_font(16)

    draw.text((68, 74), palette["brand"], font=brand_font, fill=palette["accent"])
    end_y = draw_wrapped(draw, (68, 118), title, title_font, palette["ink"], 440, 44, 3)
    draw_wrapped(draw, (70, max(end_y + 8, 248)), subtitle, sub_font, palette["ink"], 420, 24, 3)
    save(image, output_path)


def draw_diagram_header(draw: ImageDraw.ImageDraw, palette: dict[str, str]) -> None:
    shape = palette["shape"]
    if shape == "grid":
        draw.rounded_rectangle((70, 52, 1130, 128), radius=20, outline=palette["accent"], width=3)
    elif shape == "frame":
        draw.rectangle((76, 58, 1120, 122), outline=palette["accent"], width=4)
    elif shape == "pills":
        for x in range(80, 1120, 80):
            draw.line((x, 54, x, 122), fill=palette["accent_2"], width=2)
    elif shape == "circles":
        draw.ellipse((930, 36, 1120, 190), fill=palette["accent_2"])
    elif shape == "panel":
        draw.rounded_rectangle((76, 58, 1120, 122), radius=16, fill=palette["panel"], outline=palette["accent_2"], width=3)


def render_wechat_diagram(
    output_path: Path,
    title: str,
    items: Iterable[str],
    footer: str,
    theme: str = "warm-paper",
) -> None:
    palette = get_theme(theme)
    image = Image.new("RGB", (1200, 900), palette["bg"])
    draw = ImageDraw.Draw(image)
    title_font = pick_font(30, bold=True)
    item_font = pick_font(20)
    footer_font = pick_font(16)

    draw_diagram_header(draw, palette)
    draw.text((80, 70), title, font=title_font, fill=palette["ink"])
    top = 180
    for item in items:
        draw.rounded_rectangle((90, top, 1110, top + 92), radius=18, fill=palette["panel"], outline=palette["accent_2"], width=2)
        if palette["shape"] == "frame":
            draw.rectangle((120, top + 24, 162, top + 66), fill=palette["accent"])
        else:
            draw.ellipse((120, top + 24, 162, top + 66), fill=palette["accent"])
        draw.text((190, top + 28), item, font=item_font, fill=palette["text"])
        top += 110
    draw.text((92, 820), footer, font=footer_font, fill=palette["ink"])
    save(image, output_path)


def render_xhs_card(
    output_path: Path,
    title: str,
    body_lines: list[str],
    tag_line: str,
    background_path: Path | None = None,
    theme: str = "warm-paper",
) -> None:
    palette = get_theme(theme)
    image = draw_card_base((1242, 1660), theme, background_path)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 70, 1172, 410), radius=32, fill=palette["panel"])
    draw.rounded_rectangle((70, 455, 1172, 1485), radius=32, fill=palette["panel"])

    brand_font = pick_font(22, bold=True)
    title_font = pick_font(48, bold=True)
    body_font = pick_font(30)
    tag_font = pick_font(22, bold=True)

    draw.text((120, 112), palette["brand"], font=brand_font, fill=palette["accent"])
    draw_wrapped(draw, (118, 170), title, title_font, palette["ink"], 900, 58, 4)

    y = 540
    for line in body_lines:
        if not line:
            y += 24
            continue
        if line.startswith("- "):
            draw.ellipse((125, y + 14, 139, y + 28), fill=palette["accent"])
            y = draw_wrapped(draw, (160, y), line[2:], body_font, palette["text"], 900, 42, 3) + 28
        else:
            y = draw_wrapped(draw, (120, y), line, body_font, palette["text"], 960, 42, 4) + 28

    if tag_line:
        draw.rounded_rectangle((100, 1520, 600, 1590), radius=20, fill=palette["accent"])
        draw.text((126, 1538), tag_line, font=tag_font, fill=palette["panel"])

    save(image, output_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wechat-dir", required=True)
    parser.add_argument("--xhs-dir", required=True)
    parser.add_argument("--theme", default="warm-paper")
    args = parser.parse_args()

    wechat_dir = Path(args.wechat_dir)
    xhs_dir = Path(args.xhs_dir)
    wechat_base = wechat_dir / "images" / "wechat_cover_base.png"
    xhs_base = xhs_dir / "images" / "xhs_cover_base.png"

    render_wechat_cover(
        wechat_dir / "images" / "01_公众号封面.png",
        wechat_base,
        "一套适合普通创作者的 AI 内容生产 SOP",
        "从选题到发布，怎么真正跑顺",
        theme=args.theme,
    )

    render_xhs_card(
        xhs_dir / "images" / "01_首图.png",
        "内容创作者先别急着学更多 AI",
        ["先搞懂这一条图文流程。", "流程跑顺了，产出才会稳。", "", "- 不是工具不够", "- 是步骤没固定"],
        "先搭流程",
        xhs_base,
        theme=args.theme,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
