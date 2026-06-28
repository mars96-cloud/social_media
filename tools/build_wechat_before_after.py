from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_REG = "C:/Windows/Fonts/msyh.ttc"
INK = "#1F2A44"
SUB = "#66758F"
BG = "#F4F7FC"
PANEL = "#FFFFFF"
LINE = "#D7E2F1"

ROOT = Path(
    "C:/Users/Administrator/Desktop/codex_project/social_media/"
    "06_运营中心/2026/2026-06/草稿区/公众号"
)
OUT_DIR = ROOT / "_样张对比"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size=size)


def fit_image(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return image.resize(size)


def make_board(
    title: str,
    old_path: Path,
    new_path: Path,
    out_path: Path,
) -> None:
    width = 2200
    height = 1320
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=28, fill=BG, outline=LINE, width=3)
    draw.text((60, 54), title, font=font(50, True), fill=INK)
    draw.text((60, 124), "左：当前草稿箱旧图   右：新的漫画风信息图样张", font=font(24), fill=SUB)

    left_rect = (60, 190, 1060, 1240)
    right_rect = (1140, 190, 2140, 1240)
    draw.rounded_rectangle(left_rect, radius=24, fill=PANEL, outline=LINE, width=3)
    draw.rounded_rectangle(right_rect, radius=24, fill=PANEL, outline=LINE, width=3)
    draw.text((92, 214), "旧图", font=font(30, True), fill=INK)
    draw.text((1172, 214), "新样张", font=font(30, True), fill=INK)

    image.paste(fit_image(old_path, (940, 920)), (90, 280))
    image.paste(fit_image(new_path, (940, 920)), (1170, 280))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, format="PNG")


def main() -> int:
    make_board(
        "做AI自媒体前，先想清楚这4件事 - 封面对比",
        ROOT / "20260625_公众号_做AI自媒体前先想清楚这4件事/images/01_公众号封面.png",
        ROOT / "20260625_公众号_做AI自媒体前先想清楚这4件事/images/01_公众号封面_漫画风信息图样张.png",
        OUT_DIR / "01_做AI自媒体前先想清楚这4件事_封面对比.png",
    )
    make_board(
        "从AI提效到AI变现 - 封面对比",
        ROOT / "20260629_公众号_从AI提效到AI变现普通人更现实的一条路/images/01_公众号封面.png",
        ROOT / "20260629_公众号_从AI提效到AI变现普通人更现实的一条路/images/01_公众号封面_漫画风信息图样张.png",
        OUT_DIR / "02_从AI提效到AI变现_封面对比.png",
    )
    make_board(
        "为什么你用了很多AI还是没有真正提效 - 正文图对比",
        ROOT / "20260623_公众号_为什么你用了很多AI还是没有真正提效/images/05_第三个坑没有模板化.png",
        ROOT / "20260623_公众号_为什么你用了很多AI还是没有真正提效/images/05_第三个坑没有模板化_漫画风信息图样张.png",
        OUT_DIR / "03_为什么你用了很多AI还是没有真正提效_正文图对比.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
