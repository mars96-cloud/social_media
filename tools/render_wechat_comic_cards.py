from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1200
HEIGHT = 900

BG = "#F4F7FC"
PAPER = "#FCFDFF"
CARD = "#FFFFFF"
INK = "#1F2A44"
SUB = "#5E6C84"
LINE = "#D7E2F1"
BLUE = "#4D8FF7"
BLUE_SOFT = "#EAF2FF"
RED = "#FF6B6B"
RED_SOFT = "#FFF1F1"
YELLOW = "#FFD45D"
YELLOW_SOFT = "#FFF7DA"
GREEN = "#28A57A"
GREEN_SOFT = "#EAF8F2"

FONT_REG = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"

ROOT = Path(
    "C:/Users/Administrator/Desktop/codex_project/social_media/"
    "06_运营中心/2026/2026-06/草稿区/公众号"
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size=size)


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def round_rect(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 3,
) -> None:
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for ch in paragraph:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=fnt)
            if current and bbox[2] - bbox[0] > max_width:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
    return lines or [text]


def fit_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    rect: tuple[int, int, int, int],
    start_size: int,
    min_size: int = 18,
    bold: bool = False,
    line_gap: int = 10,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    x1, y1, x2, y2 = rect
    for size in range(start_size, min_size - 1, -2):
        fnt = font(size, bold=bold)
        lines = wrap_text(draw, text, fnt, x2 - x1)
        line_height = size + line_gap
        if len(lines) * line_height <= y2 - y1:
            return fnt, lines, line_height
    fallback = font(min_size, bold=bold)
    lines = wrap_text(draw, text, fallback, x2 - x1)
    return fallback, lines, min_size + line_gap


def draw_text(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    start_size: int,
    *,
    bold: bool = False,
    fill: str = INK,
    align: str = "left",
    valign: str = "center",
    line_gap: int = 10,
    min_size: int = 18,
) -> None:
    x1, y1, x2, y2 = rect
    fnt, lines, line_height = fit_lines(
        draw, text, rect, start_size, min_size=min_size, bold=bold, line_gap=line_gap
    )
    total_height = len(lines) * line_height
    if valign == "top":
        y = y1
    elif valign == "bottom":
        y = y2 - total_height
    else:
        y = y1 + max(0, (y2 - y1 - total_height) // 2)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        width = bbox[2] - bbox[0]
        if align == "center":
            x = x1 + (x2 - x1 - width) // 2
        elif align == "right":
            x = x2 - width
        else:
            x = x1
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height


def draw_chip(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    fill: str,
    text_fill: str = "#FFFFFF",
) -> None:
    round_rect(draw, rect, 22, fill)
    draw_text(draw, rect, text, 22, bold=True, fill=text_fill, align="center", line_gap=6)


def draw_badge_circle(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    radius: int,
    fill: str,
    text: str,
) -> None:
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill, outline=INK, width=4)
    draw_text(
        draw,
        (cx - radius + 8, cy - radius + 8, cx + radius - 8, cy + radius - 8),
        text,
        30,
        bold=True,
        align="center",
        line_gap=4,
    )


def draw_bridge(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], text: str) -> None:
    round_rect(draw, rect, 18, BLUE)
    draw_text(draw, rect, text, 18, bold=True, fill="#FFFFFF", align="center", line_gap=4)


def draw_split_cover(
    path: Path,
    title: str,
    subtitle: str,
    wrong: str,
    right: str,
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    round_rect(draw, (34, 34, WIDTH - 34, HEIGHT - 34), 30, PAPER, LINE, 4)
    draw_chip(draw, (60, 56, 292, 112), "公众号漫画风样张", BLUE)
    draw_text(draw, (74, 136, 1118, 246), title, 58, bold=True, valign="top")
    draw_text(draw, (76, 248, 980, 310), subtitle, 24, fill=SUB, valign="top")

    left = (70, 352, 562, 796)
    right_box = (638, 352, 1130, 796)
    round_rect(draw, left, 34, RED_SOFT, RED, 4)
    round_rect(draw, right_box, 34, BLUE_SOFT, BLUE, 4)

    draw_chip(draw, (102, 380, 266, 434), "常见误区", RED)
    draw_chip(draw, (670, 380, 834, 434), "更稳路径", BLUE)

    draw_badge_circle(draw, (316, 518), 66, YELLOW, "乱")
    draw_badge_circle(draw, (884, 518), 66, GREEN, "稳")

    round_rect(draw, (122, 614, 510, 742), 26, CARD, "#FFD8D8", 3)
    round_rect(draw, (690, 614, 1078, 742), 26, CARD, "#CDE0FF", 3)
    draw_text(draw, (154, 638, 478, 718), wrong, 28, bold=True, align="center", line_gap=8)
    draw_text(draw, (722, 638, 1046, 718), right, 28, bold=True, align="center", line_gap=8)

    draw_bridge(draw, (566, 494, 634, 548), "对照")
    save(image, path)


def draw_three_step(
    path: Path,
    title: str,
    steps: list[str],
    footer: str,
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    round_rect(draw, (34, 34, WIDTH - 34, HEIGHT - 34), 30, PAPER, LINE, 4)

    draw_text(draw, (76, 62, 1112, 142), title, 42, bold=True, valign="top")
    draw_chip(draw, (916, 58, 1118, 112), "路径图", YELLOW, INK)

    helpers = [
        "先把这一层跑顺，再往下接。",
        "这一层决定后面能不能稳定复用。",
        "这一层一稳，后面才会越来越轻。",
    ]
    colors = [
        (YELLOW_SOFT, "#F0CF76"),
        (BLUE_SOFT, "#C9DCFF"),
        (GREEN_SOFT, "#BEE8D7"),
    ]
    boxes = [
        (88, 186, 1112, 332),
        (88, 380, 1112, 526),
        (88, 574, 1112, 720),
    ]

    for idx, box in enumerate(boxes):
        fill, outline = colors[idx]
        x1, y1, x2, y2 = box
        round_rect(draw, box, 28, CARD, LINE, 3)
        round_rect(draw, (x1 + 18, y1 + 20, x1 + 136, y2 - 20), 24, fill, outline, 3)
        draw_text(draw, (x1 + 36, y1 + 36, x1 + 118, y2 - 36), f"{idx + 1}", 42, bold=True, align="center")
        draw_text(draw, (x1 + 170, y1 + 26, x2 - 30, y1 + 94), steps[idx], 30, bold=True, valign="top")
        draw_text(draw, (x1 + 170, y1 + 92, x2 - 36, y2 - 28), helpers[idx], 18, fill=SUB, valign="top")
        if idx < 2:
            draw_bridge(draw, (542, y2 + 12, 658, y2 + 54), "下一步")

    round_rect(draw, (88, 790, 1112, 846), 22, BLUE_SOFT, "#CDE0FF", 2)
    draw_text(draw, (120, 800, 1080, 836), footer, 20, bold=True, fill=INK, align="center", line_gap=6)
    save(image, path)


def draw_compare(
    path: Path,
    title: str,
    left_title: str,
    right_title: str,
    left_points: list[str],
    right_points: list[str],
    footer: str,
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    round_rect(draw, (34, 34, WIDTH - 34, HEIGHT - 34), 30, PAPER, LINE, 4)

    draw_text(draw, (76, 62, 1112, 140), title, 40, bold=True, valign="top")

    left = (72, 176, 560, 770)
    right_box = (640, 176, 1128, 770)
    round_rect(draw, left, 30, RED_SOFT, RED, 4)
    round_rect(draw, right_box, 30, BLUE_SOFT, BLUE, 4)
    draw_chip(draw, (104, 204, 280, 260), left_title, RED)
    draw_chip(draw, (672, 204, 848, 260), right_title, BLUE)

    for idx, point in enumerate(left_points):
        y = 326 + idx * 126
        draw_badge_circle(draw, (136, y + 18), 22, RED, f"{idx + 1}")
        round_rect(draw, (178, y - 18, 520, y + 74), 20, CARD, "#FFD7D7", 2)
        draw_text(draw, (202, y - 4, 496, y + 58), point, 24, bold=True, valign="top")

    for idx, point in enumerate(right_points):
        y = 326 + idx * 126
        draw_badge_circle(draw, (704, y + 18), 22, BLUE, f"{idx + 1}")
        round_rect(draw, (746, y - 18, 1088, y + 74), 20, CARD, "#CDE0FF", 2)
        draw_text(draw, (770, y - 4, 1064, y + 58), point, 24, bold=True, valign="top")

    draw_bridge(draw, (546, 432, 654, 486), "换法")
    round_rect(draw, (98, 802, 1102, 850), 22, CARD, LINE, 2)
    draw_text(draw, (120, 810, 1080, 842), footer, 18, bold=True, fill=SUB, align="center", line_gap=4)
    save(image, path)


@dataclass(frozen=True)
class PageSpec:
    filename: str
    title: str
    mode: str
    payload: dict


@dataclass(frozen=True)
class ArticleSpec:
    folder: str
    cover_title: str
    cover_subtitle: str
    cover_wrong: str
    cover_right: str
    pages: list[PageSpec]


SPECS = [
    ArticleSpec(
        folder="20260621_公众号_普通人做AI先别追新工具先搭第一条工作流",
        cover_title="普通人做AI，先别追新工具",
        cover_subtitle="先把第一条工作流搭起来，再谈效率放大。",
        cover_wrong="一边换工具，一边没有稳定动作顺序",
        cover_right="先搭最小工作流，再逐步提速和复用",
        pages=[
            PageSpec(
                filename="02_为什么学了很多AI还是没跑起来_漫画风信息图样张.png",
                title="为什么学了很多AI，还是没跑起来",
                mode="compare",
                payload={
                    "left_title": "常见状态",
                    "right_title": "关键变化",
                    "left_points": [
                        "学了很多工具，但没有固定动作",
                        "每次都像重新开始",
                        "看起来很忙，结果却不稳定",
                    ],
                    "right_points": [
                        "先固定一条最常用流程",
                        "先让动作顺下来",
                        "效率才有机会真正累积",
                    ],
                    "footer": "先有顺手流程，AI才会真的帮上忙。",
                },
            ),
            PageSpec(
                filename="03_第一条工作流不要从复杂开始_漫画风信息图样张.png",
                title="第一条工作流，不要从复杂开始",
                mode="steps",
                payload={
                    "steps": [
                        "先选一个高频重复任务",
                        "只保留最核心的几个环节",
                        "先跑通，再补细节和自动化",
                    ],
                    "footer": "普通人的起点应该是最小可执行版本。",
                },
            ),
            PageSpec(
                filename="04_最适合先搭的三类工作流_漫画风信息图样张.png",
                title="最适合先搭的三类工作流",
                mode="steps",
                payload={
                    "steps": [
                        "内容生产类：每天都会反复用",
                        "信息整理类：最容易减少混乱",
                        "承接转化类：最容易把曝光接住",
                    ],
                    "footer": "优先选高频、重复、可量化的任务。",
                },
            ),
            PageSpec(
                filename="05_第一条工作流的四步搭建法_漫画风信息图样张.png",
                title="第一条工作流，按这4步来搭",
                mode="steps",
                payload={
                    "steps": [
                        "先拆出完整动作顺序",
                        "再判断哪一步适合交给AI",
                        "跑通以后再固定模板",
                    ],
                    "footer": "先跑通，再优化，别反过来。",
                },
            ),
            PageSpec(
                filename="06_工作流跑完后要复盘什么_漫画风信息图样张.png",
                title="一条工作流跑完后，要复盘什么",
                mode="steps",
                payload={
                    "steps": [
                        "哪一步最耗时",
                        "哪一步最容易返工",
                        "哪一步最适合沉淀模板",
                    ],
                    "footer": "能复用，才叫真正跑起来。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260622_公众号_别再只学AI工具了普通人真正该先搭的是3条AI工作流",
        cover_title="别再只学AI工具了",
        cover_subtitle="普通人更该先搭的，是3条能复用的工作流。",
        cover_wrong="只记工具名字，却没有自己的工作路径",
        cover_right="先搭内容、整理、承接三条工作流",
        pages=[
            PageSpec(
                filename="02_为什么不该把重点只放在工具上_漫画风信息图样张.png",
                title="为什么不该把重点只放在工具上",
                mode="compare",
                payload={
                    "left_title": "只学工具",
                    "right_title": "先搭路径",
                    "left_points": [
                        "工具一直换，动作一直乱",
                        "知识越学越多，结果没跟上",
                        "很难形成自己的稳定方法",
                    ],
                    "right_points": [
                        "先固定任务路径",
                        "再选适合的工具配合",
                        "方法会越来越清楚",
                    ],
                    "footer": "先固化任务路径，再决定用哪个工具。",
                },
            ),
            PageSpec(
                filename="03_第一条先搭内容生产工作流_漫画风信息图样张.png",
                title="第一条：先搭内容生产工作流",
                mode="steps",
                payload={
                    "steps": [
                        "选题和判断先定住",
                        "再让AI参与结构、改写和提速",
                        "把输出节奏稳定下来",
                    ],
                    "footer": "高频任务最适合作为第一条流程。",
                },
            ),
            PageSpec(
                filename="04_第二条信息整理工作流_漫画风信息图样张.png",
                title="第二条：搭信息整理工作流",
                mode="steps",
                payload={
                    "steps": [
                        "收集材料不要散落",
                        "判断标准提前写清",
                        "整理结果能反复调用",
                    ],
                    "footer": "很多效率问题，源头其实是信息混乱。",
                },
            ),
            PageSpec(
                filename="05_第三条承接转化工作流_漫画风信息图样张.png",
                title="第三条：搭承接转化工作流",
                mode="steps",
                payload={
                    "steps": [
                        "内容负责吸引和筛选",
                        "承接动作负责留下联系",
                        "后续动作负责沉淀信任",
                    ],
                    "footer": "内容能不能变成结果，关键看承接。",
                },
            ),
            PageSpec(
                filename="06_哪条工作流该先开始_漫画风信息图样张.png",
                title="如果只能先搭一条，该先从哪条开始",
                mode="compare",
                payload={
                    "left_title": "不要这样选",
                    "right_title": "更稳的选法",
                    "left_points": [
                        "先选听起来最厉害的",
                        "先做最复杂的自动化",
                        "先追别人正在讲的热点工具",
                    ],
                    "right_points": [
                        "先选你每天都在做的",
                        "先选最容易复用的",
                        "先选最能立刻减负的",
                    ],
                    "footer": "先选最常用的，而不是听起来最厉害的。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260625_公众号_做AI自媒体前先想清楚这4件事",
        cover_title="做AI自媒体前，先想清楚这4件事",
        cover_subtitle="不是先开干，而是先把方向定清楚。",
        cover_wrong="一上来就开做、讲很多工具、追热点",
        cover_right="先定目的、人群、主线和承接闭环",
        pages=[
            PageSpec(
                filename="02_先想清楚你为什么做AI自媒体_漫画风信息图样张.png",
                title="你做AI自媒体，到底是为了什么",
                mode="steps",
                payload={
                    "steps": [
                        "先分清记录学习，还是长期做结果承接",
                        "目的不同，内容结构和节奏完全不同",
                        "目标先定住，后面才不容易越做越散",
                    ],
                    "footer": "目标不清，后面所有动作都会漂。",
                },
            ),
            PageSpec(
                filename="03_你准备长期服务哪类人_漫画风信息图样张.png",
                title="你准备长期服务哪类人",
                mode="compare",
                payload={
                    "left_title": "不要这样",
                    "right_title": "更稳一点",
                    "left_points": [
                        "一上来就想服务所有人",
                        "今天讲创作，明天讲副业",
                        "CTA和产品都很难稳定",
                    ],
                    "right_points": [
                        "先圈一类问题清楚的人",
                        "语言和案例会越来越准",
                        "选题和承接更容易形成闭环",
                    ],
                    "footer": "人群越清楚，账号越容易长期稳定。",
                },
            ),
            PageSpec(
                filename="04_讲工具还是讲工作流和结果_漫画风信息图样张.png",
                title="讲工具，还是讲工作流和结果",
                mode="compare",
                payload={
                    "left_title": "只讲工具",
                    "right_title": "讲路径",
                    "left_points": [
                        "工具一换，内容就容易失效",
                        "用户记住的是工具名，不是你",
                        "很难形成长期方法价值",
                    ],
                    "right_points": [
                        "讲判断、流程和结果",
                        "用户记住的是你的方法",
                        "更容易留下长期信任",
                    ],
                    "footer": "能留下来的，不是工具清单，而是方法价值。",
                },
            ),
            PageSpec(
                filename="05_最小承接闭环长什么样_漫画风信息图样张.png",
                title="最小承接闭环，先长这样",
                mode="steps",
                payload={
                    "steps": [
                        "内容带来关注或私信",
                        "私信带来资料领取或下一步动作",
                        "下一步动作再沉淀成信任和转化",
                    ],
                    "footer": "闭环不用一开始很复杂，但一定要先有。",
                },
            ),
            PageSpec(
                filename="06_想清楚这4件事会少很多弯路_漫画风信息图样张.png",
                title="想清楚这4件事，会少很多弯路",
                mode="compare",
                payload={
                    "left_title": "起步太急",
                    "right_title": "起步更稳",
                    "left_points": [
                        "看起来很忙，但一直没积累",
                        "内容主线不断切换",
                        "流量来了也接不住",
                    ],
                    "right_points": [
                        "目的、人群、主线先定清",
                        "内容会越做越聚焦",
                        "承接动作也更容易稳定",
                    ],
                    "footer": "最怕的不是起步慢，而是一开始就做偏。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260624_公众号_内容创作者最值得先学的1条AI图文生产流程",
        cover_title="内容创作者最该先学的",
        cover_subtitle="不是某个工具，而是一条能跑顺的AI图文流程。",
        cover_wrong="零散提问、零散写作、最后再拼成一篇",
        cover_right="先定顺序，再让AI在固定节点里提速",
        pages=[
            PageSpec(
                filename="02_为什么先学图文流程_漫画风信息图样张.png",
                title="为什么内容创作者应该先学图文流程",
                mode="compare",
                payload={
                    "left_title": "只学工具",
                    "right_title": "先学流程",
                    "left_points": [
                        "学会功能，不等于能稳定出稿",
                        "每篇都重新试一遍",
                        "时间大多耗在反复返工",
                    ],
                    "right_points": [
                        "先固定动作顺序",
                        "再把高频环节交给AI",
                        "流程越稳，产出越快",
                    ],
                    "footer": "高频动作，最值得先流程化。",
                },
            ),
            PageSpec(
                filename="03_图文流程六步总览_漫画风信息图样张.png",
                title="一条AI图文流程：6步总览",
                mode="steps",
                payload={
                    "steps": [
                        "先定选题、判断和结构",
                        "再推进写作、配图和校对",
                        "最后统一收口成可发布成品",
                    ],
                    "footer": "先定顺序，再去优化速度。",
                },
            ),
            PageSpec(
                filename="04_前三步决定是否跑偏_漫画风信息图样张.png",
                title="前3步决定图文会不会跑偏",
                mode="steps",
                payload={
                    "steps": [
                        "判断先不清，后面全会散",
                        "结构先不稳，写作一定慢",
                        "方向先偏掉，配图也会失焦",
                    ],
                    "footer": "方向和结构稳了，后面写作才快。",
                },
            ),
            PageSpec(
                filename="05_后3步决定能不能成品_漫画风信息图样张.png",
                title="后3步决定图文能不能变成成品",
                mode="steps",
                payload={
                    "steps": [
                        "把表达修顺，而不是只把字写满",
                        "让配图真正在解释判断",
                        "最后统一检查标题、图片和收口",
                    ],
                    "footer": "图文成品，不只是把字写完。",
                },
            ),
            PageSpec(
                filename="06_先跑顺再放大_漫画风信息图样张.png",
                title="真正开始时，先跑顺再放大",
                mode="compare",
                payload={
                    "left_title": "起手过重",
                    "right_title": "先小后大",
                    "left_points": [
                        "一开始就想做很复杂",
                        "流程没稳就想自动化",
                        "很快卡在细节里",
                    ],
                    "right_points": [
                        "先跑出最小版本",
                        "先稳定一轮完整出稿",
                        "再逐步补提效动作",
                    ],
                    "footer": "最小可执行版本，比复杂方案更重要。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260626_公众号_公众号小红书朋友圈哪些环节最适合交给AI",
        cover_title="哪些环节最适合交给AI",
        cover_subtitle="不是全交，而是把重复动作交出去。",
        cover_wrong="把方向和判断也一起外包给AI",
        cover_right="让AI做重复动作，自己守住核心判断",
        pages=[
            PageSpec(
                filename="02_AI更适合做重复动作_漫画风信息图样张.png",
                title="AI更适合做什么，不适合做什么",
                mode="compare",
                payload={
                    "left_title": "不适合",
                    "right_title": "更适合",
                    "left_points": [
                        "替你定方向",
                        "替你给最终判断",
                        "替你决定内容价值",
                    ],
                    "right_points": [
                        "重复整理",
                        "结构扩写和压缩表达",
                        "固定环节里的提速动作",
                    ],
                    "footer": "重复动作交给AI，核心判断自己守住。",
                },
            ),
            PageSpec(
                filename="03_公众号最适合交给AI的环节_漫画风信息图样张.png",
                title="公众号里，AI最适合接哪几步",
                mode="steps",
                payload={
                    "steps": [
                        "先帮你拆结构",
                        "再补表达和改写",
                        "最后配合整理文中配图重点",
                    ],
                    "footer": "公众号重逻辑，AI适合补结构和表达。",
                },
            ),
            PageSpec(
                filename="04_小红书最适合交给AI的环节_漫画风信息图样张.png",
                title="小红书里，AI最适合接哪几步",
                mode="steps",
                payload={
                    "steps": [
                        "先扩角度和钩子",
                        "再拆页和分镜",
                        "最后整理标题和卡片文案",
                    ],
                    "footer": "小红书重首屏和卡片感，拆页比长文更关键。",
                },
            ),
            PageSpec(
                filename="05_朋友圈最适合交给AI的环节_漫画风信息图样张.png",
                title="朋友圈里，AI最适合接哪几步",
                mode="steps",
                payload={
                    "steps": [
                        "先整理素材",
                        "再压缩表达",
                        "最后帮你保留轻关系感结构",
                    ],
                    "footer": "朋友圈重关系感，不适合照搬长文。",
                },
            ),
            PageSpec(
                filename="06_一套主逻辑多平台复用_漫画风信息图样张.png",
                title="真正高效的做法：一套主逻辑，多平台复用",
                mode="compare",
                payload={
                    "left_title": "直接复制",
                    "right_title": "分工复用",
                    "left_points": [
                        "同一段话到处贴",
                        "平台差异被抹平",
                        "看起来效率高，其实效果差",
                    ],
                    "right_points": [
                        "一套判断先统一",
                        "不同平台换承载方式",
                        "复用的是逻辑，不是表面格式",
                    ],
                    "footer": "复用不是复制，平台差异一定要保留。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260627_公众号_普通人做AI内容最容易浪费时间的5个坑",
        cover_title="做AI内容最浪费时间的",
        cover_subtitle="不是不会用AI，而是动作顺序总错。",
        cover_wrong="每一步都在试、换、补、返工",
        cover_right="先定流程、分工、模板和承接",
        pages=[
            PageSpec(
                filename="02_坑1只顾选工具不定流程_漫画风信息图样张.png",
                title="坑1：只顾选工具，不先定流程",
                mode="compare",
                payload={
                    "left_title": "先挑工具",
                    "right_title": "先定流程",
                    "left_points": [
                        "花大量时间对比工具",
                        "真正动作顺序还是混乱",
                        "换完工具问题依旧在",
                    ],
                    "right_points": [
                        "先把顺序固定下来",
                        "再看哪步需要工具支持",
                        "这样换工具也不会乱",
                    ],
                    "footer": "先定流程，再考虑换不换工具。",
                },
            ),
            PageSpec(
                filename="03_坑2一上来就想全自动化_漫画风信息图样张.png",
                title="坑2：一上来就想全自动化",
                mode="steps",
                payload={
                    "steps": [
                        "先让动作能执行",
                        "再让部分环节自动化",
                        "最后再考虑整体联动",
                    ],
                    "footer": "先可执行，再自动化。",
                },
            ),
            PageSpec(
                filename="04_坑3没有判断人机分工_漫画风信息图样张.png",
                title="坑3：没有判断什么该交给AI",
                mode="compare",
                payload={
                    "left_title": "分工混乱",
                    "right_title": "分工清楚",
                    "left_points": [
                        "判断也交给AI",
                        "重复动作反而自己做",
                        "最后既慢又不稳",
                    ],
                    "right_points": [
                        "判断留给自己",
                        "重复动作交给AI",
                        "整体会又快又稳",
                    ],
                    "footer": "分工清楚，才会又快又稳。",
                },
            ),
            PageSpec(
                filename="05_坑4每次都从零开始_漫画风信息图样张.png",
                title="坑4：每次都从零开始，不沉淀模板",
                mode="steps",
                payload={
                    "steps": [
                        "把高频结构写成模板",
                        "把常见判断写成清单",
                        "把重复表达写成可复用模块",
                    ],
                    "footer": "沉淀模板，后面才会越来越轻。",
                },
            ),
            PageSpec(
                filename="06_坑5发完就结束没有承接_漫画风信息图样张.png",
                title="坑5：发完就结束，没有承接动作",
                mode="steps",
                payload={
                    "steps": [
                        "内容先带来关注",
                        "关注后给出下一步动作",
                        "再让下一步沉淀成转化机会",
                    ],
                    "footer": "没有承接，时间很容易浪费在空曝光上。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260628_公众号_AI写作为什么总有味儿很重问题通常不在工具",
        cover_title="AI写作为什么总有味儿",
        cover_subtitle="问题通常不在工具，而在任务方式和最后收口。",
        cover_wrong="没有判断、没有人味、没有最后一遍人工收口",
        cover_right="先给判断，再讲问题，最后做人类收口",
        pages=[
            PageSpec(
                filename="02_味儿重很多时候不是模型不行_漫画风信息图样张.png",
                title="AI写作味儿重，很多时候不是模型不行",
                mode="compare",
                payload={
                    "left_title": "常见误判",
                    "right_title": "真正原因",
                    "left_points": [
                        "一有问题就换模型",
                        "任务本身却还是很模糊",
                        "输出自然继续发空",
                    ],
                    "right_points": [
                        "先把判断说清",
                        "先把对象和目的说清",
                        "模型才知道该往哪里写",
                    ],
                    "footer": "任务越模糊，输出越容易没味道。",
                },
            ),
            PageSpec(
                filename="03_原因1没有先给明确判断_漫画风信息图样张.png",
                title="原因1：没有先给AI一个明确判断",
                mode="steps",
                payload={
                    "steps": [
                        "先说你真正想表达什么",
                        "再说给谁看、解决什么",
                        "最后才让AI去展开表达",
                    ],
                    "footer": "先有判断，后有表达。",
                },
            ),
            PageSpec(
                filename="04_原因2写成了工具说明书_漫画风信息图样张.png",
                title="原因2：把内容写成了工具说明书",
                mode="compare",
                payload={
                    "left_title": "像说明书",
                    "right_title": "像内容",
                    "left_points": [
                        "全在讲功能和步骤",
                        "没有真实问题场景",
                        "没有鲜明结论",
                    ],
                    "right_points": [
                        "先讲读者问题",
                        "再讲判断和路径",
                        "工具只是辅助说明",
                    ],
                    "footer": "人更在意问题和结论，不只在意功能。",
                },
            ),
            PageSpec(
                filename="05_原因3没有做最后的人类收口_漫画风信息图样张.png",
                title="原因3：没有做最后的人类收口",
                mode="steps",
                payload={
                    "steps": [
                        "删掉空泛重复的话",
                        "把结论改成你自己的口气",
                        "补上真正像人说的话尾",
                    ],
                    "footer": "真正去机器味，靠最后的人类收口。",
                },
            ),
            PageSpec(
                filename="06_让AI写得更像人的3个动作_漫画风信息图样张.png",
                title="想让AI写得更像人，先改这3个动作",
                mode="steps",
                payload={
                    "steps": [
                        "先给判断",
                        "再给场景",
                        "最后人工收口",
                    ],
                    "footer": "先改任务方式，再考虑换工具。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260629_公众号_从AI提效到AI变现普通人更现实的一条路",
        cover_title="从AI提效到AI变现：普通人更现实的一条路",
        cover_subtitle="先把事情做顺，再把路径讲清。",
        cover_wrong="一开始只盯着赚钱，但自己没跑出稳定结果",
        cover_right="先提效，再整理方法，最后承接结果",
        pages=[
            PageSpec(
                filename="02_为什么别一开始只盯着AI赚钱_漫画风信息图样张.png",
                title="为什么不建议一开始只盯着AI赚钱",
                mode="compare",
                payload={
                    "left_title": "只盯赚钱",
                    "right_title": "先跑结果",
                    "left_points": [
                        "很容易停在概念层面",
                        "内容讲不深，信任感不够",
                        "后面卖什么都容易发虚",
                    ],
                    "right_points": [
                        "先用AI解决自己的高频任务",
                        "先跑出真实结果",
                        "结果本身就是后面变现的底气",
                    ],
                    "footer": "先提效，不是绕路，而是在给后面的结果打底。",
                },
            ),
            PageSpec(
                filename="03_第一阶段先把AI变成提效工具_漫画风信息图样张.png",
                title="第一阶段：先把AI变成提效工具",
                mode="steps",
                payload={
                    "steps": [
                        "内容生产、资料整理、客户沟通先跑顺",
                        "先减少返工、节省时间、提升稳定度",
                        "让真实可验证的提效结果先出来",
                    ],
                    "footer": "这一段最重要的，不是炫技，而是先跑出自己的结果。",
                },
            ),
            PageSpec(
                filename="04_第二阶段把提效整理成路径_漫画风信息图样张.png",
                title="第二阶段：把提效过程整理成路径",
                mode="steps",
                payload={
                    "steps": [
                        "不是只会用，而是能讲清楚",
                        "把流程、判断、模板整理出来",
                        "内容、资料和清单开始具备产品雏形",
                    ],
                    "footer": "会做是一回事，能讲清是下一阶段的关键。",
                },
            ),
            PageSpec(
                filename="05_第三阶段再进入变现动作_漫画风信息图样张.png",
                title="第三阶段：再进入变现动作",
                mode="steps",
                payload={
                    "steps": [
                        "先有结果",
                        "再有可讲清的方法",
                        "最后再接资料、产品和服务",
                    ],
                    "footer": "这时卖的不是概念，而是别人想借走的结果路径。",
                },
            ),
            PageSpec(
                filename="06_普通人更现实的一条路是先稳再放大_漫画风信息图样张.png",
                title="普通人更现实的一条路，是先稳再放大",
                mode="compare",
                payload={
                    "left_title": "绕过提效",
                    "right_title": "先稳再放大",
                    "left_points": [
                        "急着谈变现，讲不深",
                        "没有自己的结果支撑",
                        "后面很容易卖不动",
                    ],
                    "right_points": [
                        "先把事情做顺",
                        "再把过程讲清",
                        "最后把路径做成可分享和成交的东西",
                    ],
                    "footer": "对普通人来说，更现实的路通常不是更快，而是更稳。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260623_公众号_为什么你用了很多AI还是没有真正提效",
        cover_title="为什么你用了很多AI，还是没有真正提效",
        cover_subtitle="问题通常不在工具，而在流程和判断。",
        cover_wrong="功能越用越多，但每一步还是靠临场发挥",
        cover_right="固定顺序、保留判断、沉淀模板，效率才会稳",
        pages=[
            PageSpec(
                filename="02_不是工具不行而是路径没定_漫画风信息图样张.png",
                title="不是工具不行，而是路径没定",
                mode="compare",
                payload={
                    "left_title": "误区",
                    "right_title": "判断",
                    "left_points": [
                        "工具换了一个又一个",
                        "内容还是越做越散",
                        "只是更快地产生零散动作",
                    ],
                    "right_points": [
                        "工具只能放大已有路径",
                        "先把关键动作跑顺",
                        "再让AI去做重复加速",
                    ],
                    "footer": "AI放大的是路径，不会替你凭空生成稳定流程。",
                },
            ),
            PageSpec(
                filename="03_第一个坑每一步都临场发挥_漫画风信息图样张.png",
                title="第一个坑：每一步都临场发挥",
                mode="steps",
                payload={
                    "steps": [
                        "今天一套逻辑，明天又换一套",
                        "每次都像重新开始，当然很累",
                        "没有固定顺序，就很难真的越来越快",
                    ],
                    "footer": "不固定顺序，AI只能帮你补局部，帮不了整体。",
                },
            ),
            PageSpec(
                filename="04_第二个坑把判断外包给AI_漫画风信息图样张.png",
                title="第二个坑：把判断外包给AI",
                mode="compare",
                payload={
                    "left_title": "交给AI",
                    "right_title": "自己保留",
                    "left_points": [
                        "写给谁、结论是什么都随机生成",
                        "内容会空、散、没辨识度",
                        "最后像在拼贴表达",
                    ],
                    "right_points": [
                        "核心判断留在自己手里",
                        "把整理、改写、提速交给AI",
                        "这样才会越做越稳定",
                    ],
                    "footer": "AI可以替你整理信息，但不能替你做最终判断。",
                },
            ),
            PageSpec(
                filename="05_第三个坑没有模板化_漫画风信息图样张.png",
                title="第三个坑：没有把同类任务模板化",
                mode="steps",
                payload={
                    "steps": [
                        "提效不是只快一篇，而是后面都更快",
                        "标题、导语、正文、CTA都能逐步沉淀",
                        "没有模板，下一篇还是从零开始",
                    ],
                    "footer": "真正能积累效率的，是模板，不是一时的灵感。",
                },
            ),
            PageSpec(
                filename="06_真正提效看哪三个层面_漫画风信息图样张.png",
                title="真正提效，至少看这三个层面",
                mode="steps",
                payload={
                    "steps": [
                        "时间是不是缩短了",
                        "结果是不是更稳定了",
                        "动作是不是更容易复用了",
                    ],
                    "footer": "如果只是局部快一点，但整体仍混乱，那不算真正提效。",
                },
            ),
        ],
    ),
    ArticleSpec(
        folder="20260630_公众号_最适合新手切入的3种AI轻变现方向",
        cover_title="最适合新手切入的3种",
        cover_subtitle="轻变现的重点，不是赚得快，而是先跑起来。",
        cover_wrong="一上来就想做重产品、重服务、重交付",
        cover_right="先做轻入口，先拿到第一步结果",
        pages=[
            PageSpec(
                filename="02_轻变现的重点是先跑起来_漫画风信息图样张.png",
                title="轻变现的重点，是先跑起来",
                mode="compare",
                payload={
                    "left_title": "一开始太重",
                    "right_title": "先轻一点",
                    "left_points": [
                        "想一步做到很大",
                        "准备周期很长",
                        "容易还没开始就卡住",
                    ],
                    "right_points": [
                        "先做可快速验证的东西",
                        "先拿到第一批反馈",
                        "再逐步加深和放大",
                    ],
                    "footer": "对新手来说，先跑比先大更重要。",
                },
            ),
            PageSpec(
                filename="03_方向1卖资料模板和SOP_漫画风信息图样张.png",
                title="方向1：卖资料、模板和SOP",
                mode="steps",
                payload={
                    "steps": [
                        "把自己跑顺的方法整理出来",
                        "把重复动作做成模板",
                        "把模板打包成轻入口产品",
                    ],
                    "footer": "对内容型创作者来说，这是最顺手的入口。",
                },
            ),
            PageSpec(
                filename="04_方向2做低门槛微课或小专题_漫画风信息图样张.png",
                title="方向2：做低门槛微课或小专题",
                mode="steps",
                payload={
                    "steps": [
                        "选一个真实小问题",
                        "把解决路径讲清楚",
                        "先用小专题拿付费反馈",
                    ],
                    "footer": "先做小切口，更容易拿到第一批付费反馈。",
                },
            ),
            PageSpec(
                filename="05_方向3做轻咨询或轻陪跑_漫画风信息图样张.png",
                title="方向3：做轻咨询或轻陪跑",
                mode="steps",
                payload={
                    "steps": [
                        "先用轻服务接触真实需求",
                        "再总结高频问题和判断",
                        "后面再决定要不要产品化",
                    ],
                    "footer": "轻服务是很好的需求验证器。",
                },
            ),
            PageSpec(
                filename="06_新手最好的顺序是先轻再深再放大_漫画风信息图样张.png",
                title="新手更稳的顺序：先轻、再深、再放大",
                mode="steps",
                payload={
                    "steps": [
                        "先跑轻入口",
                        "再做更深的承接",
                        "最后再考虑放大交付",
                    ],
                    "footer": "轻变现不是小，而是更容易跑出第一步。",
                },
            ),
        ],
    ),
]


def canonical_name(sample_name: str) -> str:
    return sample_name.replace("_漫画风信息图样张", "")


def render_article(spec: ArticleSpec) -> None:
    image_dir = ROOT / spec.folder / "images"
    cover_sample = image_dir / "01_公众号封面_漫画风信息图样张.png"
    draw_split_cover(
        cover_sample,
        spec.cover_title,
        spec.cover_subtitle,
        spec.cover_wrong,
        spec.cover_right,
    )
    if cover_sample.exists():
        cover_image = Image.open(cover_sample).copy()
        save(cover_image, image_dir / "01_公众号封面.png")
    for page in spec.pages:
        output_path = image_dir / page.filename
        if page.mode == "steps":
            draw_three_step(output_path, page.title, page.payload["steps"], page.payload["footer"])
        elif page.mode == "compare":
            draw_compare(
                output_path,
                page.title,
                page.payload["left_title"],
                page.payload["right_title"],
                page.payload["left_points"],
                page.payload["right_points"],
                page.payload["footer"],
            )
        else:
            raise ValueError(f"Unsupported mode: {page.mode}")
        if output_path.exists():
            page_image = Image.open(output_path).copy()
            save(page_image, image_dir / canonical_name(page.filename))


def main() -> int:
    for spec in SPECS:
        render_article(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
