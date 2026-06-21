from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont


THEMES: dict[str, dict[str, str]] = {
    "warm-paper": {
        "bg": "#F6EFE5",
        "ink": "#1C1A17",
        "muted": "#6D5B4B",
        "accent": "#F28C28",
        "accent_2": "#FFF1D8",
        "brand": "AI趣创社",
    },
    "blueprint": {
        "bg": "#E7F2FF",
        "ink": "#0E2440",
        "muted": "#4E6482",
        "accent": "#2D8CFF",
        "accent_2": "#D9ECFF",
        "brand": "AI工作流实验室",
    },
    "newsroom": {
        "bg": "#F7F1ED",
        "ink": "#201813",
        "muted": "#72554A",
        "accent": "#DD5D2A",
        "accent_2": "#FFE5D9",
        "brand": "AI实战笔记",
    },
    "mint-grid": {
        "bg": "#ECF8F1",
        "ink": "#103126",
        "muted": "#4A7262",
        "accent": "#1FA972",
        "accent_2": "#DDF7EA",
        "brand": "智能体流程手册",
    },
    "studio-pop": {
        "bg": "#FFF0E5",
        "ink": "#27150A",
        "muted": "#7B543A",
        "accent": "#FF7B3A",
        "accent_2": "#FFE0CC",
        "brand": "AI增长工作室",
    },
    "slate-pro": {
        "bg": "#EDF1F7",
        "ink": "#111827",
        "muted": "#5C677A",
        "accent": "#00A9A5",
        "accent_2": "#D8F5F4",
        "brand": "AI方法论",
    },
}


COVER_VARIANTS = (
    "burst-left",
    "spotlight-right",
    "warning-bar",
    "dark-card",
    "diagonal-pop",
)


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


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            candidate = current + char
            if current and text_width(draw, candidate, font) > max_width:
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


def draw_text_with_stroke(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    stroke_fill: str,
    stroke_width: int,
) -> None:
    draw.text(
        xy,
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def hex_with_alpha(value: str, alpha: int) -> tuple[int, int, int, int]:
    rgb = ImageColor.getrgb(value)
    return rgb[0], rgb[1], rgb[2], alpha


def draw_card_base(size: tuple[int, int], theme: str, background_path: Path | None = None) -> Image.Image:
    palette = get_theme(theme)
    image = Image.new("RGB", size, palette["bg"])
    if background_path and background_path.exists():
        bg = Image.open(background_path).convert("RGB").resize(size)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=0.5))
        image = Image.blend(bg, image, 0.34)
    return image


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def fit_hook(hook: str, max_chars: int = 10) -> str:
    hook = "".join(hook.split())
    if len(hook) <= max_chars:
        return hook
    return hook[:max_chars]


def fallback_hook_from_title(title: str) -> str:
    compact = title.replace("，", "").replace("。", "").replace("？", "").replace("！", "")
    candidates = [
        "先别急",
        "别再乱学",
        "问题在这",
        "先搭系统",
        "别做无用功",
        "这才值钱",
        "别被带偏",
    ]
    for candidate in candidates:
        if candidate in compact:
            return candidate
    for splitter in ("先", "别", "为什么", "如果", "普通人", "内容", "AI"):
        index = compact.find(splitter)
        if index >= 0:
            snippet = compact[index : index + 8]
            if 3 <= len(snippet) <= 10:
                return snippet
    return fit_hook(compact[:8], 8)


def default_cover_variant(theme: str) -> str:
    index = list(THEMES.keys()).index(theme) if theme in THEMES else 0
    return COVER_VARIANTS[index % len(COVER_VARIANTS)]


def render_cover_background(image: Image.Image, palette: dict[str, str], variant: str) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    accent = palette["accent"]
    accent_2 = palette["accent_2"]

    if variant == "burst-left":
        draw.rounded_rectangle((24, 24, 430, height - 24), radius=34, fill=hex_with_alpha("#111111", 128))
        draw.ellipse((-110, -20, 220, 290), fill=hex_with_alpha(accent, 135))
        draw.ellipse((585, -40, 940, 240), fill=hex_with_alpha(accent_2, 120))
        draw.rectangle((620, 280, 860, 324), fill=hex_with_alpha(accent, 200))
    elif variant == "spotlight-right":
        draw.rounded_rectangle((40, 34, width - 40, height - 34), radius=30, outline=hex_with_alpha(accent, 230), width=4)
        draw.rounded_rectangle((48, 42, 430, height - 42), radius=28, fill=hex_with_alpha("#FFFFFF", 210))
        draw.ellipse((620, 45, 905, 310), fill=hex_with_alpha(accent, 108))
        draw.ellipse((688, 120, 860, 300), fill=hex_with_alpha("#FFFFFF", 95))
    elif variant == "warning-bar":
        draw.rectangle((0, 0, width, height), fill=hex_with_alpha("#101010", 75))
        draw.rounded_rectangle((30, 34, 472, height - 34), radius=28, fill=hex_with_alpha("#FFF9F2", 235))
        draw.rectangle((514, 38, 560, height - 38), fill=hex_with_alpha(accent, 245))
        draw.rectangle((596, 38, 636, 240), fill=hex_with_alpha(accent, 190))
        draw.ellipse((674, 58, 892, 274), fill=hex_with_alpha(accent_2, 122))
    elif variant == "dark-card":
        draw.rectangle((0, 0, width, height), fill=hex_with_alpha("#0C0C0C", 95))
        draw.rounded_rectangle((34, 34, width - 34, height - 34), radius=28, fill=hex_with_alpha("#121212", 80))
        draw.rounded_rectangle((56, 52, 474, height - 52), radius=28, fill=hex_with_alpha("#FFF7F0", 228))
        draw.ellipse((636, 26, 900, 286), fill=hex_with_alpha(accent, 125))
        draw.rounded_rectangle((650, 264, 856, 314), radius=18, fill=hex_with_alpha(accent_2, 185))
    else:
        draw.polygon([(0, 0), (310, 0), (0, 240)], fill=hex_with_alpha(accent, 180))
        draw.polygon([(width, 0), (width, 146), (604, 0)], fill=hex_with_alpha(accent_2, 165))
        draw.rounded_rectangle((42, 38, 462, height - 38), radius=30, fill=hex_with_alpha("#FFFFFF", 230))
        draw.polygon([(700, 70), (860, 40), (820, 214), (660, 242)], fill=hex_with_alpha(accent, 138))


def render_wechat_cover(
    output_path: Path,
    background_path: Path | None,
    title: str,
    subtitle: str,
    theme: str = "warm-paper",
    hook: str | None = None,
    kicker: str | None = None,
    variant: str | None = None,
) -> None:
    palette = get_theme(theme)
    cover_hook = fit_hook(hook or fallback_hook_from_title(title))
    cover_kicker = kicker or "点开看清核心判断"
    cover_variant = variant or default_cover_variant(theme)

    image = draw_card_base((900, 383), theme, background_path)
    render_cover_background(image, palette, cover_variant)
    draw = ImageDraw.Draw(image)

    brand_font = pick_font(18, bold=True)
    tag_font = pick_font(16, bold=True)
    hook_font = pick_font(56, bold=True)
    teaser_font = pick_font(18)
    sub_font = pick_font(14)

    left_x = 68
    draw.rounded_rectangle((left_x, 60, left_x + 132, 94), radius=17, fill=palette["accent"])
    draw.text((left_x + 16, 69), palette["brand"], font=brand_font, fill="#FFFFFF")

    draw.rounded_rectangle((left_x, 110, left_x + 116, 142), radius=16, fill=palette["accent_2"])
    draw.text((left_x + 14, 118), "本期重点", font=tag_font, fill=palette["ink"])

    hook_y = 155
    hook_lines = wrap_text(draw, cover_hook, hook_font, 330)[:2]
    for idx, line in enumerate(hook_lines):
        draw_text_with_stroke(
            draw,
            (left_x, hook_y + idx * 62),
            line,
            hook_font,
            palette["ink"],
            "#FFFFFF",
            1,
        )

    teaser_y = 276 if len(hook_lines) == 1 else 320
    draw.rounded_rectangle((left_x, teaser_y - 8, left_x + 248, teaser_y + 24), radius=14, fill=hex_with_alpha("#FFFFFF", 190))
    draw.text((left_x + 12, teaser_y), cover_kicker, font=teaser_font, fill=palette["ink"])
    draw.text((left_x, 344), subtitle[:22], font=sub_font, fill=palette["muted"])

    stamp_x = 620
    draw.rounded_rectangle((stamp_x, 50, stamp_x + 172, 92), radius=20, fill=hex_with_alpha(palette["accent"], 235))
    draw.text((stamp_x + 18, 62), "继续看", font=pick_font(24, bold=True), fill="#FFFFFF")
    draw.rounded_rectangle((stamp_x, 108, 860, 148), radius=18, fill=hex_with_alpha("#FFFFFF", 170))
    draw.text((stamp_x + 18, 118), "不是复述标题，要制造好奇", font=pick_font(16, bold=True), fill=palette["ink"])

    save(image, output_path)


def draw_story_header(draw: ImageDraw.ImageDraw, palette: dict[str, str], width: int, title: str, style: str) -> None:
    draw.rounded_rectangle((54, 44, width - 54, 170), radius=28, fill=hex_with_alpha("#FFFFFF", 210))
    draw.rounded_rectangle((74, 68, 194, 106), radius=16, fill=palette["accent"])
    draw.text((90, 78), "关键拆解", font=pick_font(20, bold=True), fill="#FFFFFF")
    title_font = pick_font(36, bold=True)
    draw_wrapped(draw, (74, 118), title, title_font, palette["ink"], width - 160, 44, 2)

    if style == "scene":
        draw.ellipse((860, 46, 1140, 274), fill=hex_with_alpha(palette["accent"], 120))
        draw.ellipse((942, 110, 1108, 268), fill=hex_with_alpha("#FFFFFF", 95))
    elif style == "flow":
        for offset in range(0, 5):
            x = 842 + offset * 58
            draw.rounded_rectangle((x, 76 + offset * 10, x + 40, 176 + offset * 10), radius=20, fill=hex_with_alpha(palette["accent"], 130))
    else:
        draw.polygon([(904, 56), (1120, 98), (1060, 274), (838, 226)], fill=hex_with_alpha(palette["accent"], 135))


def render_wechat_diagram(
    output_path: Path,
    title: str,
    items: Iterable[str],
    footer: str,
    theme: str = "warm-paper",
    scene_label: str | None = None,
    variant: str = "scene",
) -> None:
    palette = get_theme(theme)
    image = Image.new("RGB", (1200, 900), palette["bg"])
    draw = ImageDraw.Draw(image, "RGBA")

    draw.rounded_rectangle((28, 28, 1172, 872), radius=34, fill=hex_with_alpha("#FFFFFF", 95))
    draw_story_header(draw, palette, 1200, title, variant)

    if scene_label:
        draw.rounded_rectangle((78, 188, 266, 228), radius=18, fill=hex_with_alpha(palette["accent_2"], 235))
        draw.text((96, 199), scene_label, font=pick_font(20, bold=True), fill=palette["ink"])

    top = 270
    card_height = 108
    item_font = pick_font(27, bold=True)
    helper_font = pick_font(16)
    item_list = list(items)
    for index, item in enumerate(item_list, start=1):
        shift = 22 if index % 2 == 0 else 0
        y = top + (index - 1) * 118
        draw.rounded_rectangle((96 + shift, y, 1104 - shift, y + card_height), radius=28, fill=hex_with_alpha("#FFFFFF", 225))
        draw.rounded_rectangle((122 + shift, y + 26, 198 + shift, y + 82), radius=18, fill=hex_with_alpha(palette["accent"], 235))
        draw.text((142 + shift, y + 38), f"{index}", font=pick_font(24, bold=True), fill="#FFFFFF")
        draw.text((230 + shift, y + 26), item, font=item_font, fill=palette["ink"])
        helper = "先抓这个，再往下一步。" if index == 1 else "这是最容易被忽略的关键环节。"
        draw.text((232 + shift, y + 66), helper, font=helper_font, fill=palette["muted"])

    draw.rounded_rectangle((82, 808, 1120, 854), radius=20, fill=hex_with_alpha(palette["accent_2"], 230))
    draw.text((104, 821), footer, font=pick_font(22, bold=True), fill=palette["ink"])
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
    draw = ImageDraw.Draw(image, "RGBA")

    draw.rounded_rectangle((56, 56, 1186, 370), radius=34, fill=hex_with_alpha("#FFFFFF", 220))
    draw.rounded_rectangle((56, 408, 1186, 1536), radius=38, fill=hex_with_alpha("#FFFFFF", 205))
    draw.ellipse((850, 90, 1180, 430), fill=hex_with_alpha(palette["accent"], 115))

    draw.rounded_rectangle((90, 98, 280, 150), radius=20, fill=palette["accent"])
    draw.text((112, 112), palette["brand"], font=pick_font(24, bold=True), fill="#FFFFFF")
    draw_wrapped(draw, (98, 184), title, pick_font(54, bold=True), palette["ink"], 840, 62, 4)

    y = 488
    for line in body_lines:
        if not line:
            y += 18
            continue
        if line.startswith("- "):
            draw.rounded_rectangle((102, y + 10, 126, y + 34), radius=8, fill=palette["accent"])
            y = draw_wrapped(draw, (150, y), line[2:], pick_font(30), palette["ink"], 900, 42, 3) + 26
        else:
            y = draw_wrapped(draw, (98, y), line, pick_font(32), palette["ink"], 960, 46, 4) + 26

    if tag_line:
        draw.rounded_rectangle((86, 1566, 650, 1628), radius=26, fill=palette["accent"])
        draw.text((114, 1580), tag_line, font=pick_font(26, bold=True), fill="#FFFFFF")

    save(image, output_path)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--wechat-dir", required=True)
    parser.add_argument("--xhs-dir", required=True)
    parser.add_argument("--theme", default="warm-paper")
    args = parser.parse_args()

    wechat_dir = Path(args.wechat_dir)
    xhs_dir = Path(args.xhs_dir)

    render_wechat_cover(
        wechat_dir / "images" / "01_公众号封面.png",
        wechat_dir / "images" / "wechat_cover_base.png",
        "普通人做 AI，先别追新工具，先搭第一条工作流",
        "后续日常推送与直播，继续拆工作流与智能体",
        theme=args.theme,
        hook="先搭系统",
        kicker="别先追新工具",
    )
    render_wechat_diagram(
        wechat_dir / "images" / "02_示意图.png",
        "第一条工作流里最该先固定的动作",
        ["明确输入", "保留判断", "沉淀模板"],
        "先把关键骨架跑顺，再考虑更复杂的自动化。",
        theme=args.theme,
        scene_label="流程拆解",
    )
    render_xhs_card(
        xhs_dir / "images" / "01_首图.png",
        "普通人先别追新工具 先把自己的第一条工作流跑顺",
        ["- 先定输入", "- 再定判断", "- 最后才谈自动化"],
        "关注我，持续更新工作流",
        xhs_dir / "images" / "xhs_cover_base.png",
        theme=args.theme,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
