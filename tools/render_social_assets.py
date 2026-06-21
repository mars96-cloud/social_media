from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


BG = "#F7F1E8"
PANEL = "#FFFDF9"
DARK = "#20342E"
GREEN = "#2E5E4E"
ORANGE = "#F29F58"
BORDER = "#E8D7C4"


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


def draw_card_base(size: tuple[int, int], background_path: Path | None = None) -> Image.Image:
    image = Image.new("RGB", size, BG)
    if background_path and background_path.exists():
        bg = Image.open(background_path).convert("RGB").resize(size)
        image = Image.blend(bg, image, 0.72)
    return image


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def render_wechat_cover(output_path: Path, background_path: Path, title: str, subtitle: str) -> None:
    image = draw_card_base((900, 383), background_path)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 40, 550, 340), radius=24, fill="#FFF8F0")
    draw.rectangle((610, 70, 616, 308), fill=ORANGE)
    draw.rectangle((640, 70, 646, 250), fill=ORANGE)

    brand_font = pick_font(18, bold=True)
    title_font = pick_font(34, bold=True)
    sub_font = pick_font(16)

    draw.text((68, 74), "AI趣创社", font=brand_font, fill=ORANGE)
    end_y = draw_wrapped(draw, (68, 118), title, title_font, DARK, 440, 44, 3)
    draw_wrapped(draw, (70, max(end_y + 8, 248)), subtitle, sub_font, DARK, 420, 24, 3)
    save(image, output_path)


def render_wechat_diagram(output_path: Path, title: str, items: Iterable[str], footer: str) -> None:
    image = Image.new("RGB", (1200, 900), "#FBF6EF")
    draw = ImageDraw.Draw(image)
    title_font = pick_font(30, bold=True)
    item_font = pick_font(20)
    footer_font = pick_font(16)

    draw.text((80, 70), title, font=title_font, fill=DARK)
    top = 180
    for item in items:
        draw.rounded_rectangle((90, top, 1110, top + 92), radius=18, fill=PANEL, outline=BORDER, width=2)
        draw.ellipse((120, top + 24, 162, top + 66), fill=ORANGE)
        draw.text((190, top + 28), item, font=item_font, fill=GREEN)
        top += 110
    draw.text((92, 820), footer, font=footer_font, fill=DARK)
    save(image, output_path)


def render_xhs_card(
    output_path: Path,
    title: str,
    body_lines: list[str],
    tag_line: str,
    background_path: Path | None = None,
) -> None:
    image = draw_card_base((1242, 1660), background_path)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 70, 1172, 410), radius=32, fill="#FFF8F0")
    draw.rounded_rectangle((70, 455, 1172, 1485), radius=32, fill=PANEL)

    brand_font = pick_font(22, bold=True)
    title_font = pick_font(48, bold=True)
    body_font = pick_font(30)
    tag_font = pick_font(22, bold=True)

    draw.text((120, 112), "AI趣创社", font=brand_font, fill=ORANGE)
    draw_wrapped(draw, (118, 170), title, title_font, DARK, 900, 58, 4)

    y = 540
    for line in body_lines:
        if not line:
            y += 24
            continue
        if line.startswith("- "):
            draw.ellipse((125, y + 14, 139, y + 28), fill=ORANGE)
            y = draw_wrapped(draw, (160, y), line[2:], body_font, GREEN, 900, 42, 3) + 28
        else:
            y = draw_wrapped(draw, (120, y), line, body_font, GREEN, 960, 42, 4) + 28

    if tag_line:
        draw.rounded_rectangle((100, 1520, 600, 1590), radius=20, fill=ORANGE)
        draw.text((126, 1538), tag_line, font=tag_font, fill=PANEL)

    save(image, output_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wechat-dir", required=True)
    parser.add_argument("--xhs-dir", required=True)
    args = parser.parse_args()

    wechat_dir = Path(args.wechat_dir)
    xhs_dir = Path(args.xhs_dir)
    wechat_base = wechat_dir / "images" / "wechat_cover_base.png"
    xhs_base = xhs_dir / "images" / "xhs_cover_base.png"

    render_wechat_cover(
        wechat_dir / "images" / "01_公众号封面.png",
        wechat_base,
        "一套适合普通创作者的AI内容生产SOP",
        "从选题到发布，怎么真正跑顺",
    )

    wechat_cards = [
        ("02_为什么用了AI还是没提效.png", "为什么很多人用了 AI 还是没提效", [
            "今天写标题，明天换工具，后天又重写一遍",
            "看起来一直很忙，其实没有固定流程",
            "真正缺的不是工具，而是能反复跑起来的 SOP",
        ], "先固定步骤，再让 AI 进入步骤里承担角色。"),
        ("03_这套SOP适合哪些人.png", "这套 SOP 最适合哪类创作者", [
            "一个人同时做小红书、公众号、朋友圈等图文内容",
            "每次写内容都像临场发挥，结构和节奏不稳定",
            "想用 AI 提速，但又不想把内容写成机器味",
        ], "缺的不是更多工具，而是一条能反复跑顺的流程。"),
        ("04_AI和人分别负责什么.png", "AI 和人，分别该负责什么", [
            "AI 负责：整理、扩展、提速、改写",
            "你负责：方向、取舍、观点、结论",
            "判断不外包，内容才不会越来越像机器",
        ], "AI 是提速器，不是判断替代者。"),
        ("05_六步SOP总览.png", "基础版内容生产 SOP：6 步跑顺", [
            "1. 拆受众问题",
            "2. 扩选题角度",
            "3. 搭文章提纲",
            "4. 写初稿并补表达",
            "5. 改成平台版本",
            "6. 补承接动作后发布",
        ], "先把顺序固定，再逐步模板化。"),
        ("06_前3步先跑顺.png", "前 3 步先解决方向和结构", [
            "先拆清楚：写给谁，他们最常卡在哪",
            "围绕一个主题先铺出 5 到 10 个选题角度",
            "先定结论和提纲，再让 AI 进入写作阶段",
        ], "前 3 步做扎实，后面才不会一直返工。"),
        ("07_后3步决定能不能稳定.png", "后 3 步决定能不能长期稳定产出", [
            "初稿出来后，自己补判断，不把观点外包",
            "同一套主逻辑，再改成小红书和公众号版本",
            "发布前补 CTA，让内容进入承接和转化",
        ], "平台不同，表达不同，但底层逻辑可以共用。"),
        ("08_发布前承接动作清单.png", "发布前一定补上的 3 个承接动作", [
            "想清楚这篇内容希望读者下一步做什么",
            "在评论、私信、公众号沉淀里只选一个主 CTA",
            "检查 CTA 和正文是不是自然衔接，而不是硬塞",
        ], "没有承接动作，内容很容易变成看过就算。"),
    ]
    for filename, title, items, footer in wechat_cards:
        render_wechat_diagram(wechat_dir / "images" / filename, title, items, footer)

    xhs_cards = [
        ("01_首图.png", "内容创作者先别急着学更多 AI", [
            "先搞懂这一条图文流程。",
            "流程跑顺了，产出才会稳。",
            "",
            "- 不是工具不够",
            "- 是步骤没固定",
        ], "先搭流程", xhs_base),
        ("02_问题页.png", "为什么你学了 AI 还是不稳定", [
            "不是你不努力。",
            "而是你每天都在临场发挥。",
            "",
            "- 想选题靠现想",
            "- 写结构靠感觉",
            "- 改平台版本靠重写",
        ], "问题先看清", None),
        ("03_流程总览.png", "先看结论：这 6 步最值得先固定", [
            "- 拆痛点",
            "- 扩选题",
            "- 搭提纲",
            "- 写初稿",
            "- 改平台版",
            "- 发前检查",
        ], "6步跑顺", None),
        ("04_前三步.png", "前 2 步先解决选题和方向", [
            "1. 先拆受众痛点",
            "2. 再铺 5 到 10 个选题角度",
            "",
            "不要一上来就问 AI：",
            "“帮我写一篇。”",
        ], "先定方向", None),
        ("05_后三步.png", "第 3 步最关键：先搭提纲", [
            "先定结论。",
            "再列 3 到 5 个要点。",
            "最后才写正文。",
            "",
            "提纲稳了，全文才不会散。",
        ], "先提纲", None),
        ("06_关键提醒.png", "第 4 步和第 5 步：让 AI 提速，不替你判断", [
            "4. 初稿出来后，自己补判断",
            "5. 再改成不同平台版本",
            "",
            "- 小红书更短更快",
            "- 公众号更完整更解释",
        ], "别外包判断", None),
        ("07_CTA页.png", "第 6 步：发前一定补 CTA", [
            "发之前先想清楚：",
            "你是要收藏、评论，",
            "还是私信领资料？",
            "",
            "一篇内容只留一个主动作。",
        ], "发前检查", None),
        ("08_最关键提醒.png", "最关键的不是 AI 帮你写完", [
            "- AI 负责提速",
            "- 你负责方向",
            "- 你负责最终判断",
            "",
            "想看基础版清单，私信我 `流程`。",
        ], "私信我 流程", None),
    ]
    for filename, title, body, tag, background in xhs_cards:
        render_xhs_card(xhs_dir / "images" / filename, title, body, tag, background)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
