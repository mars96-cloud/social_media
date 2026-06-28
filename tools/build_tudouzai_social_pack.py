from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(r"C:\Users\Administrator\Desktop\codex_project\social_media")
BASE = ROOT / "13_人物形象" / "土豆崽_定版"
IMAGES = BASE / "images"
BACKGROUNDS = BASE / "backgrounds"
SOCIAL = BASE / "social_pack"


FREQUENT = [
    "01_角色设定主图_定版.png",
    "02_平静直视.png",
    "03_微坏笑.png",
    "04_生气皱眉.png",
    "06_无语.png",
    "10_惊讶.png",
    "14_得意.png",
    "16_压眉盯人.png",
]


def ensure_dirs() -> None:
    SOCIAL.mkdir(parents=True, exist_ok=True)
    (SOCIAL / "高频精选").mkdir(parents=True, exist_ok=True)
    (SOCIAL / "头像背景搭配预览").mkdir(parents=True, exist_ok=True)
    (SOCIAL / "主页头图适配版").mkdir(parents=True, exist_ok=True)


def copy_frequent() -> list[Path]:
    out = []
    for name in FREQUENT:
        src = IMAGES / name
        dst = SOCIAL / "高频精选" / name
        Image.open(src).save(dst)
        out.append(dst)
    return out


def circle_avatar(src_path: Path, size: int = 320) -> Image.Image:
    im = Image.open(src_path).convert("RGBA")
    im.thumbnail((size, size))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - im.width) // 2
    y = (size - im.height) // 2
    canvas.paste(im, (x, y), im)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    out.paste(canvas, (0, 0), mask)
    return out


def build_profile_previews() -> list[Path]:
    outputs = []
    bg_names = [
        "01_工作流主视觉_定版.png",
        "02_内容生产台_定版.png",
        "03_提效到变现路径_定版.png",
        "04_讲人话的AI教练_定版.png",
        "05_避坑与判断_定版.png",
    ]
    avatar = circle_avatar(IMAGES / "01_角色设定主图_定版.png", 360)
    for idx, bg_name in enumerate(bg_names, start=1):
        bg = Image.open(BACKGROUNDS / bg_name).convert("RGBA")
        overlay = bg.copy()
        overlay.paste(avatar, (130, 160), avatar)
        d = ImageDraw.Draw(overlay)
        d.rounded_rectangle((520, 210, 1240, 410), radius=20, fill=(255, 255, 255, 220))
        d.rounded_rectangle((520, 450, 1100, 540), radius=16, fill=(255, 255, 255, 200))
        d.text((560, 255), "土豆学AI / AI趣创社", fill=(65, 56, 45))
        d.text((560, 475), "讲人话的 AI 工作流 / 内容提效 / 轻变现", fill=(95, 83, 70))
        out = SOCIAL / "头像背景搭配预览" / f"{idx:02d}_头像背景搭配预览.png"
        overlay.save(out)
        outputs.append(out)
    return outputs


def build_header_adaptations() -> list[Path]:
    outputs = []
    sizes = [
        ("小红书主页头图.png", (1600, 640), "01_工作流主视觉_定版.png"),
        ("公众号封面横版.png", (900, 383), "04_讲人话的AI教练_定版.png"),
        ("朋友圈背景.png", (1125, 633), "03_提效到变现路径_定版.png"),
        ("视频号主页背景.png", (1920, 1080), "02_内容生产台_定版.png"),
    ]
    for name, size, bg_name in sizes:
        bg = Image.open(BACKGROUNDS / bg_name).convert("RGB")
        resized = bg.resize(size, Image.Resampling.LANCZOS)
        out = SOCIAL / "主页头图适配版" / name
        resized.save(out)
        outputs.append(out)
    return outputs


def build_sheet(paths: list[Path], out_path: Path, thumb=(420, 420), cols=2) -> None:
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
    ensure_dirs()
    frequent = copy_frequent()
    previews = build_profile_previews()
    headers = build_header_adaptations()
    build_sheet(frequent, SOCIAL / "00_高频精选总览.png", thumb=(360, 360), cols=4)
    build_sheet(previews, SOCIAL / "00_头像背景搭配总览.png", thumb=(520, 300), cols=1)
    build_sheet(headers, SOCIAL / "00_主页头图适配总览.png", thumb=(520, 300), cols=1)


if __name__ == "__main__":
    main()
