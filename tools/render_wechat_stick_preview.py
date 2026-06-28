from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1200
HEIGHT = 900

BG = "#FBFBF8"
INK = "#111111"
SUB = "#4B4B4B"
RED = "#FF6B57"
RED_SOFT = "#FFE7E2"
BLUE = "#4A7CFF"
BLUE_SOFT = "#E8F0FF"
GREEN = "#28A86B"
GREEN_SOFT = "#E5F8EE"
YELLOW = "#FFD84D"
YELLOW_SOFT = "#FFF4C6"
GRAY = "#E7E7E0"
WHITE = "#FFFFFF"

FONT_REG = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"

ROOT = Path("C:/Users/Administrator/Desktop/codex_project/social_media")


def cn_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size=size)


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def rr(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str = INK, width: int = 4, radius: int = 26) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def tw(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        if current and tw(draw, test, font) > max_width:
            lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)
    return lines or [text]


def fit_text(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], start: int, min_size: int = 20, bold: bool = False, gap: int = 8) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    x1, y1, x2, y2 = box
    for size in range(start, min_size - 1, -2):
        fnt = cn_font(size, bold=bold)
        lines = wrap(draw, text, fnt, x2 - x1)
        line_h = size + gap
        if len(lines) * line_h <= y2 - y1:
            return fnt, lines, line_h
    fnt = cn_font(min_size, bold=bold)
    lines = wrap(draw, text, fnt, x2 - x1)
    return fnt, lines, min_size + gap


def draw_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    start: int,
    *,
    bold: bool = False,
    fill: str = INK,
    align: str = "left",
    valign: str = "center",
    gap: int = 8,
    min_size: int = 20,
) -> None:
    x1, y1, x2, y2 = box
    fnt, lines, line_h = fit_text(draw, text, box, start, min_size=min_size, bold=bold, gap=gap)
    total_h = len(lines) * line_h
    if valign == "top":
        y = y1
    elif valign == "bottom":
        y = y2 - total_h
    else:
        y = y1 + max(0, (y2 - y1 - total_h) // 2)
    for line in lines:
        width = tw(draw, line, fnt)
        if align == "center":
            x = x1 + (x2 - x1 - width) // 2
        elif align == "right":
            x = x2 - width
        else:
            x = x1
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h


def chip(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill: str, text_fill: str = WHITE) -> None:
    rr(draw, box, fill, outline=fill, width=1, radius=24)
    draw_text(draw, box, text, 24, bold=True, align="center", fill=text_fill, gap=4, min_size=18)


def icon_coin(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, text: str) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW, outline=INK, width=4)
    draw_text(draw, (cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10), text, 34, bold=True, align="center")


def icon_robot(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int = 1) -> None:
    w = 88 * scale
    h = 72 * scale
    rr(draw, (x, y, x + w, y + h), YELLOW_SOFT, outline=INK, width=4, radius=20)
    draw.ellipse((x + 18 * scale, y + 22 * scale, x + 30 * scale, y + 34 * scale), fill=INK)
    draw.ellipse((x + 58 * scale, y + 22 * scale, x + 70 * scale, y + 34 * scale), fill=INK)
    draw.line((x + 26 * scale, y + 52 * scale, x + 62 * scale, y + 52 * scale), fill=INK, width=4)
    draw.line((x + w // 2, y - 16 * scale, x + w // 2, y), fill=INK, width=4)
    draw.ellipse((x + w // 2 - 7 * scale, y - 24 * scale, x + w // 2 + 7 * scale, y - 10 * scale), fill=RED, outline=INK, width=3)


def icon_phone(draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 90, h: int = 132) -> None:
    rr(draw, (x, y, x + w, y + h), WHITE, outline=INK, width=4, radius=18)
    draw.rectangle((x + 15, y + 20, x + w - 15, y + h - 28), fill=BLUE_SOFT, outline=INK, width=3)
    draw.line((x + 32, y + h - 14, x + w - 32, y + h - 14), fill=INK, width=4)


def icon_folders(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    rr(draw, (x + 14, y + 28, x + 128, y + 106), YELLOW_SOFT, outline=INK, width=4, radius=18)
    rr(draw, (x + 42, y, x + 156, y + 78), GREEN_SOFT, outline=INK, width=4, radius=18)
    rr(draw, (x, y + 54, x + 114, y + 132), BLUE_SOFT, outline=INK, width=4, radius=18)


def draw_person(draw: ImageDraw.ImageDraw, x: int, y: int, shirt: str, mood: str = "normal") -> None:
    draw.ellipse((x, y, x + 72, y + 72), fill=WHITE, outline=INK, width=4)
    eye_y = y + 28
    draw.ellipse((x + 20, eye_y, x + 28, eye_y + 8), fill=INK)
    draw.ellipse((x + 44, eye_y, x + 52, eye_y + 8), fill=INK)
    if mood == "worry":
        draw.arc((x + 24, y + 42, x + 50, y + 58), 200, 340, fill=INK, width=4)
        draw.line((x + 16, y + 18, x + 28, y + 14), fill=INK, width=3)
        draw.line((x + 44, y + 14, x + 56, y + 18), fill=INK, width=3)
    elif mood == "happy":
        draw.arc((x + 22, y + 38, x + 52, y + 60), 20, 160, fill=INK, width=4)
    elif mood == "shock":
        draw.ellipse((x + 30, y + 42, x + 42, y + 56), outline=INK, width=3)
        draw.line((x + 14, y + 16, x + 28, y + 10), fill=INK, width=3)
        draw.line((x + 44, y + 10, x + 58, y + 16), fill=INK, width=3)
    else:
        draw.line((x + 24, y + 50, x + 48, y + 50), fill=INK, width=4)
    rr(draw, (x + 12, y + 74, x + 60, y + 136), shirt, outline=INK, width=4, radius=18)
    draw.line((x + 36, y + 136, x + 20, y + 182), fill=INK, width=4)
    draw.line((x + 36, y + 136, x + 54, y + 182), fill=INK, width=4)
    draw.line((x + 12, y + 92, x - 10, y + 118), fill=INK, width=4)
    draw.line((x + 60, y + 92, x + 84, y + 112), fill=INK, width=4)


def draw_panel_title(draw: ImageDraw.ImageDraw, title: str, kicker: str | None = None) -> None:
    if kicker:
        chip(draw, (66, 48, 238, 98), kicker, RED)
    draw_text(draw, (70, 118, 1130, 236), title, 58, bold=True, align="center", valign="top", gap=10, min_size=34)


def draw_cover(path: Path, title: str, sub: str, hook: str, scene: str) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    rr(draw, (28, 28, WIDTH - 28, HEIGHT - 28), WHITE, outline=INK, width=5, radius=34)
    chip(draw, (74, 60, 260, 112), "公众号封面", YELLOW, INK)
    draw_text(draw, (90, 138, 1110, 248), hook, 68, bold=True, align="center", valign="top", gap=8, min_size=40)
    draw_text(draw, (120, 250, 1080, 300), sub, 24, fill=SUB, align="center", valign="top", gap=6, min_size=18)

    if scene == "pit":
        draw_person(draw, 168, 414, RED, "worry")
        draw_person(draw, 922, 378, GREEN, "happy")
        icon_robot(draw, 498, 476)
        icon_phone(draw, 304, 476)
        icon_coin(draw, 952, 554, 42, "稳")
        rr(draw, (120, 336, 432, 744), RED_SOFT, outline=INK, width=4, radius=28)
        rr(draw, (760, 336, 1080, 744), GREEN_SOFT, outline=INK, width=4, radius=28)
        chip(draw, (164, 356, 298, 406), "乱忙", RED)
        chip(draw, (806, 356, 940, 406), "稳做", GREEN)
        draw_text(draw, (146, 614, 404, 700), "反复换\n工具", 42, bold=True, align="center", gap=6, min_size=28)
        draw_text(draw, (794, 614, 1046, 700), "先定流程\n再提速", 42, bold=True, align="center", gap=6, min_size=28)
        draw.line((432, 540, 486, 540), fill=INK, width=5)
        draw.polygon([(486, 540), (466, 526), (466, 554)], fill=INK)
        draw.line((714, 540, 760, 540), fill=INK, width=5)
        draw.polygon([(714, 540), (734, 526), (734, 554)], fill=INK)
    else:
        draw_person(draw, 138, 430, RED, "shock")
        draw_person(draw, 946, 416, BLUE, "happy")
        icon_folders(draw, 460, 436)
        icon_robot(draw, 610, 476)
        rr(draw, (102, 344, 396, 748), RED_SOFT, outline=INK, width=4, radius=28)
        rr(draw, (798, 344, 1094, 748), BLUE_SOFT, outline=INK, width=4, radius=28)
        chip(draw, (142, 364, 314, 414), "外挂思路", RED)
        chip(draw, (834, 364, 1006, 414), "中台思路", BLUE)
        draw_text(draw, (130, 620, 372, 700), "没系统\n全靠补", 42, bold=True, align="center", gap=6, min_size=28)
        draw_text(draw, (824, 620, 1068, 700), "有资产\n才放大", 42, bold=True, align="center", gap=6, min_size=28)

    draw_text(draw, (94, 786, 1106, 844), title, 22, fill=SUB, align="center", gap=4, min_size=18)
    save(image, path)


def draw_compare_page(path: Path, title: str, left_title: str, right_title: str, left_points: list[str], right_points: list[str], footer: str, icon_mode: str) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    rr(draw, (28, 28, WIDTH - 28, HEIGHT - 28), WHITE, outline=INK, width=5, radius=34)
    draw_panel_title(draw, title)
    left = (64, 194, 548, 760)
    right = (652, 194, 1136, 760)
    rr(draw, left, RED_SOFT, outline=INK, width=4, radius=28)
    rr(draw, right, BLUE_SOFT, outline=INK, width=4, radius=28)
    chip(draw, (100, 214, 256, 262), left_title, RED)
    chip(draw, (690, 214, 846, 262), right_title, BLUE)
    if icon_mode == "tool":
        icon_phone(draw, 248, 288)
        icon_folders(draw, 828, 292)
    elif icon_mode == "human_ai":
        draw_person(draw, 252, 278, YELLOW, "worry")
        icon_robot(draw, 812, 316)
    else:
        draw_person(draw, 244, 282, RED, "shock")
        draw_person(draw, 832, 282, BLUE, "happy")

    y_left = 470
    for idx, point in enumerate(left_points, start=1):
        draw.ellipse((96, y_left - 4, 138, y_left + 38), fill=RED, outline=INK, width=3)
        draw_text(draw, (104, y_left + 2, 130, y_left + 32), str(idx), 22, bold=True, align="center", fill=WHITE, min_size=16)
        rr(draw, (154, y_left - 18, 504, y_left + 56), WHITE, outline=INK, width=3, radius=18)
        draw_text(draw, (178, y_left - 8, 480, y_left + 42), point, 24, bold=True, gap=4, min_size=18)
        y_left += 92

    y_right = 470
    for idx, point in enumerate(right_points, start=1):
        draw.ellipse((684, y_right - 4, 726, y_right + 38), fill=BLUE, outline=INK, width=3)
        draw_text(draw, (692, y_right + 2, 718, y_right + 32), str(idx), 22, bold=True, align="center", fill=WHITE, min_size=16)
        rr(draw, (742, y_right - 18, 1092, y_right + 56), WHITE, outline=INK, width=3, radius=18)
        draw_text(draw, (766, y_right - 8, 1068, y_right + 42), point, 24, bold=True, gap=4, min_size=18)
        y_right += 92

    rr(draw, (482, 442, 718, 506), YELLOW, outline=INK, width=4, radius=24)
    draw_text(draw, (500, 454, 700, 492), "别只看表面动作", 22, bold=True, align="center", min_size=16)
    rr(draw, (86, 794, 1114, 846), GRAY, outline=INK, width=3, radius=22)
    draw_text(draw, (110, 804, 1090, 836), footer, 18, bold=True, align="center", fill=SUB, gap=4, min_size=16)
    save(image, path)


def draw_steps_page(path: Path, title: str, steps: list[str], footer: str, icon_mode: str) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    rr(draw, (28, 28, WIDTH - 28, HEIGHT - 28), WHITE, outline=INK, width=5, radius=34)
    draw_panel_title(draw, title)

    if icon_mode == "auto":
        draw_person(draw, 82, 264, RED, "shock")
        icon_robot(draw, 1010, 294)
    elif icon_mode == "template":
        icon_folders(draw, 78, 274)
        draw_person(draw, 1014, 274, GREEN, "happy")
    elif icon_mode == "bridge":
        icon_phone(draw, 88, 274)
        icon_coin(draw, 1046, 332, 40, "接")
    else:
        draw_person(draw, 84, 270, YELLOW, "normal")
        icon_robot(draw, 1012, 300)

    boxes = [
        (176, 250, 1018, 380),
        (176, 418, 1018, 548),
        (176, 586, 1018, 716),
    ]
    fills = [YELLOW_SOFT, BLUE_SOFT, GREEN_SOFT]
    labels = ["1", "2", "3"]
    for idx, box in enumerate(boxes):
        rr(draw, box, fills[idx], outline=INK, width=4, radius=26)
        x1, y1, x2, y2 = box
        draw.ellipse((x1 + 20, y1 + 26, x1 + 82, y1 + 88), fill=WHITE, outline=INK, width=4)
        draw_text(draw, (x1 + 26, y1 + 34, x1 + 76, y1 + 80), labels[idx], 32, bold=True, align="center", min_size=20)
        rr(draw, (x1 + 106, y1 + 22, x2 - 24, y2 - 22), WHITE, outline=INK, width=3, radius=20)
        draw_text(draw, (x1 + 134, y1 + 34, x2 - 56, y2 - 34), steps[idx], 30, bold=True, gap=8, min_size=20)
        if idx < 2:
            draw.line((596, y2 + 8, 596, y2 + 32), fill=INK, width=5)
            draw.polygon([(596, y2 + 46), (584, y2 + 28), (608, y2 + 28)], fill=INK)

    rr(draw, (86, 794, 1114, 846), GRAY, outline=INK, width=3, radius=22)
    draw_text(draw, (110, 804, 1090, 836), footer, 18, bold=True, align="center", fill=SUB, gap=4, min_size=16)
    save(image, path)


@dataclass(frozen=True)
class PageSpec:
    filename: str
    mode: str
    title: str
    footer: str
    left_title: str | None = None
    right_title: str | None = None
    left_points: list[str] | None = None
    right_points: list[str] | None = None
    steps: list[str] | None = None
    icon_mode: str = "default"


@dataclass(frozen=True)
class ArticleSpec:
    folder: Path
    cover_file: str
    cover_title: str
    cover_sub: str
    cover_hook: str
    cover_scene: str
    pages: list[PageSpec]


SPECS = [
    ArticleSpec(
        folder=ROOT / "06_运营中心/2026/2026-06/草稿区/公众号/20260627_公众号_普通人做AI内容最容易浪费时间的5个坑/images",
        cover_file="01_公众号封面_stick预览.png",
        cover_title="普通人做 AI 内容，最容易浪费时间的 5 个坑",
        cover_sub="不是不会用，而是动作顺序总错。",
        cover_hook="别再白忙了",
        cover_scene="pit",
        pages=[
            PageSpec(
                filename="02_坑1只顾选工具不定流程_stick预览.png",
                mode="compare",
                title="坑1：只顾选工具，不先定流程",
                left_title="先挑工具",
                right_title="先定流程",
                left_points=["花大量时间比工具", "动作顺序还是混乱", "换完工具问题还在"],
                right_points=["先把顺序固定下来", "再看哪步需要工具", "这样换工具也不乱"],
                footer="先定流程，再考虑换不换工具。",
                icon_mode="tool",
            ),
            PageSpec(
                filename="03_坑2一上来就想全自动化_stick预览.png",
                mode="steps",
                title="坑2：一上来就想全自动化",
                steps=["先让流程手动跑顺", "再把高频重复步骤自动化", "最后再考虑整条链路联动"],
                footer="手动版都不稳，自动化只会放大混乱。",
                icon_mode="auto",
            ),
            PageSpec(
                filename="04_坑3没有判断人机分工_stick预览.png",
                mode="compare",
                title="坑3：人和 AI 分工不清",
                left_title="分工混乱",
                right_title="分工清楚",
                left_points=["判断也丢给 AI", "重复活反而自己扛", "最后又慢又空"],
                right_points=["判断留给自己", "重复动作交给 AI", "整体会又快又稳"],
                footer="AI 适合提速，不适合替你做最终判断。",
                icon_mode="human_ai",
            ),
            PageSpec(
                filename="05_坑4每次都从零开始_stick预览.png",
                mode="steps",
                title="坑4：每次都从零开始，不沉淀模板",
                steps=["把高频标题结构记下来", "把常用表达沉淀成模块", "把 CTA 和配图思路固定下来"],
                footer="模板不是偷懒，是把重复动作交给系统。",
                icon_mode="template",
            ),
            PageSpec(
                filename="06_坑5发完就结束没有承接_stick预览.png",
                mode="steps",
                title="坑5：发完就结束，没有承接动作",
                steps=["内容先带来关注", "关注后给出下一步动作", "把下一步沉淀成稳定承接"],
                footer="没有承接，曝光很难变成结果。",
                icon_mode="bridge",
            ),
        ],
    ),
    ArticleSpec(
        folder=ROOT / "06_运营中心/2026/2026-07/草稿区/20260701_公众号_别把AI当外挂普通人更该先有自己的内容中台/images",
        cover_file="01_公众号封面_stick预览.png",
        cover_title="别把 AI 当外挂，普通人更该先有自己的内容中台",
        cover_sub="AI 放大的是系统，不是零散动作。",
        cover_hook="先有中台",
        cover_scene="platform",
        pages=[
            PageSpec(
                filename="02_内容中台到底包含什么_stick预览.png",
                mode="steps",
                title="内容中台，至少要有这 3 层",
                steps=["选题池：知道接下来写什么", "素材与模板：知道拿什么写", "承接动作：知道写完带去哪里"],
                footer="没有这三层，AI 再强也只是临时救火。",
                icon_mode="template",
            ),
            PageSpec(
                filename="03_AI为什么救不了没有系统的内容人_stick预览.png",
                mode="compare",
                title="为什么 AI 救不了没有系统的内容人",
                left_title="外挂思路",
                right_title="系统思路",
                left_points=["今天卡哪补哪", "内容全靠临场发挥", "结果很难稳定复用"],
                right_points=["先有固定内容资产", "再让 AI 接重复动作", "输出会越来越稳"],
                footer="AI 能放大系统，放大不了混乱。",
                icon_mode="default",
            ),
            PageSpec(
                filename="04_普通人最小内容中台怎么搭_stick预览.png",
                mode="steps",
                title="普通人最小内容中台，先这样搭",
                steps=["先留一个持续更新的选题池", "再沉淀一套高频表达模板", "最后固定每篇内容的承接动作"],
                footer="先搭最小可用版，再慢慢扩展。",
                icon_mode="template",
            ),
            PageSpec(
                filename="05_内容中台里人和AI怎么分工_stick预览.png",
                mode="compare",
                title="内容中台里，人和 AI 怎么分工",
                left_title="你来定",
                right_title="AI 来做",
                left_points=["方向判断", "观点取舍", "最后收口"],
                right_points=["整理归纳", "扩写改写", "多平台改编"],
                footer="AI 是执行层，不是总负责人。",
                icon_mode="human_ai",
            ),
            PageSpec(
                filename="06_内容中台开始起作用的3个信号_stick预览.png",
                mode="steps",
                title="中台开始起作用，通常有这 3 个信号",
                steps=["不再频繁为写什么发愁", "同类内容越写越快", "承接动作开始稳定出现"],
                footer="这时再聊自动化，才是真的站在地基上往上搭。",
                icon_mode="bridge",
            ),
        ],
    ),
]


def render_article(spec: ArticleSpec) -> None:
    draw_cover(spec.folder / spec.cover_file, spec.cover_title, spec.cover_sub, spec.cover_hook, spec.cover_scene)
    for page in spec.pages:
        if page.mode == "compare":
            draw_compare_page(
                spec.folder / page.filename,
                page.title,
                page.left_title or "",
                page.right_title or "",
                page.left_points or [],
                page.right_points or [],
                page.footer,
                page.icon_mode,
            )
        else:
            draw_steps_page(
                spec.folder / page.filename,
                page.title,
                page.steps or [],
                page.footer,
                page.icon_mode,
            )


def main() -> int:
    for spec in SPECS:
        render_article(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
