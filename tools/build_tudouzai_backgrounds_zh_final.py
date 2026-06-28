from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\Administrator\Desktop\codex_project\social_media")
SRC_DIR = ROOT / "13_人物形象" / "土豆崽_定版" / "backgrounds_xiaohei" / "final_notext"
OUT_DIR = ROOT / "13_人物形象" / "土豆崽_定版" / "backgrounds_xiaohei" / "final_clean_zh"
OVERVIEW = ROOT / "13_人物形象" / "土豆崽_定版" / "backgrounds_xiaohei" / "00_土豆崽小黑风背景_简体最终总览.png"
FONT = Path(r"C:\Windows\Fonts\simhei.ttf")


@dataclass
class TextItem:
    text: str
    xy: tuple[int, int]
    size: int
    color: tuple[int, int, int]


BLACK = (18, 18, 18)
RED = (232, 58, 35)
BLUE = (38, 108, 212)
ORANGE = (236, 126, 28)


TEXTS: dict[str, list[TextItem]] = {
    "01": [
        TextItem("工具太多", (340, 320), 84, RED),
        TextItem("还是乱", (460, 460), 84, RED),
        TextItem("输入", (1640, 1040), 64, BLACK),
        TextItem("流程", (2100, 1040), 64, BLACK),
        TextItem("输出", (2580, 1040), 64, BLACK),
        TextItem("先跑顺", (2180, 1260), 80, RED),
    ],
    "02": [
        TextItem("想法篮", (180, 1080), 70, BLACK),
        TextItem("提纲压", (960, 1040), 70, BLACK),
        TextItem("AI提速", (1590, 860), 74, BLUE),
        TextItem("初稿带", (1860, 1220), 70, BLACK),
        TextItem("发布章", (2480, 980), 70, BLACK),
    ],
    "03": [
        TextItem("忙乱", (400, 360), 74, RED),
        TextItem("补顺序", (1220, 340), 74, BLUE),
        TextItem("流程卡", (1240, 890), 66, RED),
        TextItem("稳定产出", (2380, 340), 74, BLUE),
    ],
    "04": [
        TextItem("公开内容", (80, 1180), 70, RED),
        TextItem("私域承接", (1050, 1180), 70, RED),
        TextItem("资料包", (1760, 1100), 70, BLUE),
        TextItem("低客单", (2260, 1100), 70, BLACK),
        TextItem("训练营", (2610, 860), 70, BLACK),
    ],
    "05": [
        TextItem("拆动作", (650, 1120), 76, RED),
        TextItem("别讲术语", (1450, 420), 76, ORANGE),
        TextItem("讲人话", (2520, 920), 76, BLUE),
    ],
}


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size)


def draw_text(draw: ImageDraw.ImageDraw, item: TextItem) -> None:
    draw.text(item.xy, item.text, font=font(item.size), fill=item.color)


def render_one(path: Path) -> Path:
    key = path.name[:2]
    image = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for item in TEXTS[key]:
        draw_text(draw, item)
    out = OUT_DIR / path.name.replace("-notext-", "-clean-zh-")
    image.save(out)
    return out


def build_overview(paths: list[Path]) -> None:
    thumb = (820, 462)
    label_font = font(24)
    cards = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail(thumb)
        card = Image.new("RGB", (thumb[0] + 40, thumb[1] + 80), "white")
        x = (card.width - image.width) // 2
        card.paste(image, (x, 20))
        d = ImageDraw.Draw(card)
        d.text((20, card.height - 42), path.name, fill=BLACK, font=label_font)
        cards.append(card)
    sheet = Image.new("RGB", (cards[0].width, len(cards) * cards[0].height), (245, 245, 245))
    for i, card in enumerate(cards):
        sheet.paste(card, (0, i * card.height))
    sheet.save(OVERVIEW)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [render_one(path) for path in sorted(SRC_DIR.glob("*.png"))]
    build_overview(outputs)
    for out in outputs:
        print(out)
    print(OVERVIEW)


if __name__ == "__main__":
    main()
