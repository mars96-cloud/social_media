from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(r"C:\Users\Administrator\Desktop\codex_project\social_media")
IMG_DIR = ROOT / "13_人物形象" / "土豆崽_定版" / "backgrounds_xiaohei" / "images"


def build_sheet(paths: list[Path], out_path: Path, thumb=(700, 394), cols=1) -> None:
    cards = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail(thumb)
        canvas = Image.new("RGB", (thumb[0] + 40, thumb[1] + 80), "white")
        x = (canvas.width - im.width) // 2
        canvas.paste(im, (x, 20))
        d = ImageDraw.Draw(canvas)
        d.text((20, canvas.height - 42), p.name, fill="black")
        cards.append(canvas)
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cards[0].width, rows * cards[0].height), (245, 245, 245))
    for i, card in enumerate(cards):
        sheet.paste(card, ((i % cols) * card.width, (i // cols) * card.height))
    sheet.save(out_path)


def main() -> None:
    paths = sorted(IMG_DIR.glob("*.png"))
    build_sheet(paths, IMG_DIR.parent / "00_小黑风背景总览.png")


if __name__ == "__main__":
    main()
