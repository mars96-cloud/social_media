from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(r"C:\Users\Administrator\Desktop\codex_project\social_media")
BASE = ROOT / "13_人物形象" / "土豆崽_定版"
IMAGES_DIR = BASE / "images"
BACKGROUNDS_DIR = BASE / "backgrounds"

MASTER_NAME = "01-角色设定主图-20260628-140846-1.png"


@dataclass
class FaceSpec:
    filename: str
    brow_left: tuple[int, int, int, int]
    brow_right: tuple[int, int, int, int]
    pupil_left: tuple[int, int]
    pupil_right: tuple[int, int]
    mouth: str


FACES = [
    FaceSpec("01_角色设定主图_定版.png", (840, 640, 980, 720), (1070, 720, 1220, 630), (972, 890), (1220, 890), "flat"),
    FaceSpec("02_平静直视.png", (860, 660, 1000, 740), (1060, 740, 1210, 650), (968, 890), (1216, 890), "flat"),
    FaceSpec("03_微坏笑.png", (845, 675, 1002, 738), (1072, 738, 1218, 648), (968, 886), (1210, 886), "smirk"),
    FaceSpec("04_生气皱眉.png", (830, 705, 985, 790), (1085, 790, 1235, 705), (958, 922), (1208, 922), "sad"),
    FaceSpec("05_轻微疑惑.png", (855, 680, 1000, 735), (1105, 715, 1218, 668), (955, 900), (1200, 875), "tilt_down"),
    FaceSpec("06_无语.png", (850, 680, 995, 735), (1078, 735, 1218, 680), (960, 892), (1205, 892), "tiny_flat"),
    FaceSpec("07_轻蔑.png", (840, 670, 998, 738), (1090, 722, 1220, 680), (960, 886), (1198, 900), "half_smirk"),
    FaceSpec("08_不爽.png", (835, 695, 990, 775), (1085, 775, 1230, 700), (958, 914), (1205, 918), "sad"),
    FaceSpec("09_发呆.png", (860, 680, 995, 730), (1075, 730, 1210, 680), (972, 898), (1218, 898), "dot_flat"),
    FaceSpec("10_惊讶.png", (865, 650, 1005, 710), (1065, 710, 1208, 650), (968, 886), (1215, 886), "o"),
    FaceSpec("11_抿嘴.png", (850, 670, 1000, 740), (1075, 740, 1215, 670), (970, 890), (1218, 890), "short_smile_down"),
    FaceSpec("12_侧眼看左.png", (850, 668, 1000, 735), (1070, 735, 1218, 660), (930, 896), (1168, 896), "flat"),
    FaceSpec("13_侧眼看右.png", (850, 668, 1000, 735), (1070, 735, 1218, 660), (1000, 896), (1240, 896), "flat"),
    FaceSpec("14_得意.png", (850, 680, 1005, 740), (1070, 740, 1215, 675), (970, 888), (1215, 888), "smirk"),
    FaceSpec("15_眯眼坏笑.png", (845, 695, 1002, 775), (1080, 775, 1230, 695), (968, 924), (1212, 924), "wide_smirk"),
    FaceSpec("16_压眉盯人.png", (825, 720, 985, 805), (1092, 805, 1240, 720), (958, 930), (1210, 930), "tiny_flat"),
    FaceSpec("17_委屈不服.png", (885, 712, 1000, 760), (1075, 760, 1195, 710), (968, 910), (1215, 910), "sad"),
    FaceSpec("18_困困的.png", (860, 690, 995, 740), (1078, 740, 1212, 690), (965, 918), (1210, 918), "tiny_flat"),
    FaceSpec("19_半闭眼冷脸.png", (850, 690, 1000, 748), (1075, 748, 1220, 688), (965, 918), (1210, 918), "flat"),
    FaceSpec("20_安静普通脸.png", (860, 680, 1000, 735), (1075, 735, 1215, 680), (972, 892), (1218, 892), "flat"),
]


def ensure_dirs() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)


def open_master() -> Image.Image:
    return Image.open(IMAGES_DIR / MASTER_NAME).convert("RGBA")


def blank_canvas() -> Image.Image:
    image = Image.new("RGBA", (2048, 2048), (248, 247, 244, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, 2048, 70):
        draw.line((0, y, 2048, min(2048, y + 140)), fill=(251, 250, 247, 255), width=24)
    return image


def draw_body(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    # Main silhouette
    outline = [
        (600, 330),
        (470, 520),
        (430, 760),
        (430, 980),
        (460, 1240),
        (560, 1550),
        (760, 1780),
        (1030, 1870),
        (1300, 1810),
        (1510, 1620),
        (1600, 1370),
        (1610, 1100),
        (1600, 820),
        (1560, 560),
        (1450, 390),
        (1260, 285),
        (980, 250),
        (760, 265),
    ]
    draw.polygon(outline, fill=(233, 182, 96, 255))

    # Left shadow mass
    shadow = [
        (610, 340),
        (520, 520),
        (500, 760),
        (500, 1030),
        (550, 1330),
        (660, 1610),
        (810, 1810),
        (900, 1860),
        (820, 1680),
        (740, 1410),
        (700, 1100),
        (700, 820),
        (720, 600),
        (790, 410),
    ]
    draw.polygon(shadow, fill=(205, 148, 77, 255))

    # Soft center highlight
    highlight = [
        (820, 420),
        (730, 620),
        (710, 890),
        (720, 1150),
        (780, 1410),
        (920, 1670),
        (1180, 1740),
        (1370, 1620),
        (1460, 1390),
        (1490, 1100),
        (1460, 840),
        (1390, 620),
        (1260, 470),
        (1060, 395),
    ]
    draw.polygon(highlight, fill=(240, 190, 108, 255))

    # Outline on top
    draw.line(outline + [outline[0]], fill=(10, 10, 10, 255), width=18, joint="curve")


def draw_eye(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, pupil_offset: tuple[int, int]) -> None:
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill="white", outline="black", width=6)
    px = cx + pupil_offset[0]
    py = cy + pupil_offset[1]
    draw.ellipse((px - 18, py - 18, px + 18, py + 18), fill="black")


def draw_mouth(draw: ImageDraw.ImageDraw, kind: str) -> None:
    if kind == "flat":
        draw.rounded_rectangle((1030, 1030, 1195, 1044), radius=7, fill="black")
    elif kind == "tiny_flat":
        draw.rounded_rectangle((1050, 1034, 1175, 1046), radius=6, fill="black")
    elif kind == "smirk":
        draw.arc((960, 945, 1250, 1115), start=20, end=150, fill="black", width=8)
    elif kind == "half_smirk":
        draw.arc((1005, 965, 1235, 1098), start=35, end=125, fill="black", width=8)
    elif kind == "wide_smirk":
        draw.arc((930, 950, 1265, 1115), start=18, end=158, fill="black", width=10)
    elif kind == "sad":
        draw.arc((995, 1010, 1230, 1135), start=200, end=340, fill="black", width=9)
    elif kind == "tilt_down":
        draw.line((1050, 1030, 1180, 1060), fill="black", width=8)
    elif kind == "dot_flat":
        draw.rounded_rectangle((1080, 1033, 1160, 1044), radius=5, fill="black")
    elif kind == "short_smile_down":
        draw.arc((1015, 990, 1210, 1080), start=22, end=145, fill="black", width=8)
    elif kind == "o":
        draw.ellipse((1080, 1005, 1155, 1080), outline="black", width=8)


def render_face(spec: FaceSpec) -> Path:
    image = blank_canvas()
    draw_body(image)
    draw = ImageDraw.Draw(image)

    draw.line(spec.brow_left, fill="black", width=38, joint="curve")
    draw.line(spec.brow_right, fill="black", width=38, joint="curve")
    draw_eye(draw, (972, 886), 78, (spec.pupil_left[0] - 972, spec.pupil_left[1] - 886))
    draw_eye(draw, (1218, 886), 78, (spec.pupil_right[0] - 1218, spec.pupil_right[1] - 886))
    draw_mouth(draw, spec.mouth)

    out = IMAGES_DIR / spec.filename
    image.save(out)
    return out


def soft_background(size: tuple[int, int], left_clear: bool = True) -> Image.Image:
    bg = Image.new("RGB", size, (250, 245, 236))
    draw = ImageDraw.Draw(bg)
    w, h = size
    for i in range(0, h, 60):
        draw.line((0, i, w, i + 120), fill=(255, 249, 241), width=24)
    if left_clear:
        draw.rounded_rectangle((0, 0, w * 0.33, h), radius=0, fill=(252, 248, 241))
    return bg.filter(ImageFilter.GaussianBlur(1.2))


def paste_mascot(bg: Image.Image, face_path: Path, box: tuple[int, int, int, int]) -> None:
    face = Image.open(face_path).convert("RGBA")
    face.thumbnail((box[2] - box[0], box[3] - box[1]))
    x = box[0] + ((box[2] - box[0]) - face.width) // 2
    y = box[1] + ((box[3] - box[1]) - face.height) // 2
    bg.paste(face, (x, y), face)


def draw_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], icon: str) -> None:
    draw.rounded_rectangle(rect, radius=22, fill=(247, 228, 198), outline=(208, 177, 125), width=3)
    x1, y1, x2, y2 = rect
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    if icon == "check":
        draw.rectangle((cx - 30, cy - 22, cx + 14, cy + 18), outline=(145, 95, 45), width=5)
        draw.line((cx - 18, cy, cx - 3, cy + 14), fill=(145, 95, 45), width=5)
        draw.line((cx - 3, cy + 14, cx + 24, cy - 14), fill=(145, 95, 45), width=5)
    elif icon == "circle":
        draw.arc((cx - 30, cy - 30, cx + 30, cy + 30), start=20, end=335, fill=(145, 95, 45), width=6)
    elif icon == "tick":
        draw.line((cx - 26, cy + 4, cx - 6, cy + 24), fill=(145, 95, 45), width=7)
        draw.line((cx - 6, cy + 24, cx + 34, cy - 16), fill=(145, 95, 45), width=7)


def render_backgrounds() -> list[Path]:
    outputs = []
    base_face = IMAGES_DIR / "01_角色设定主图_定版.png"

    bg1 = soft_background((2880, 1440), left_clear=True)
    d1 = ImageDraw.Draw(bg1)
    paste_mascot(bg1, base_face, (1550, 280, 2350, 1220))
    points = [(1100, 760), (1450, 760), (1800, 760)]
    icons = ["check", "circle", "tick"]
    for i, (x, y) in enumerate(points):
        draw_card(d1, (x - 110, y - 90, x + 110, y + 90), icons[i])
        if i < len(points) - 1:
            d1.line((x + 110, y, points[i + 1][0] - 110, y), fill=(146, 102, 58), width=10)
            d1.polygon([(points[i + 1][0] - 120, y - 16), (points[i + 1][0] - 120, y + 16), (points[i + 1][0] - 82, y)], fill=(146, 102, 58))
    out1 = BACKGROUNDS_DIR / "01_工作流主视觉_定版.png"
    bg1.save(out1)
    outputs.append(out1)

    bg2 = soft_background((2880, 1440), left_clear=True)
    d2 = ImageDraw.Draw(bg2)
    modules = [
        (1100, 360, 1380, 520),
        (1450, 360, 1730, 520),
        (1800, 360, 2080, 520),
        (1100, 620, 1380, 780),
        (1450, 620, 1730, 780),
        (1800, 620, 2080, 780),
    ]
    for i, rect in enumerate(modules):
        draw_card(d2, rect, ["check", "circle", "tick", "circle", "check", "tick"][i])
    d2.line((1240, 520, 1240, 620), fill=(149, 107, 61), width=8)
    d2.line((1590, 520, 1590, 620), fill=(149, 107, 61), width=8)
    d2.line((1940, 520, 1940, 620), fill=(149, 107, 61), width=8)
    paste_mascot(bg2, base_face, (2150, 420, 2700, 1180))
    out2 = BACKGROUNDS_DIR / "02_内容生产台_定版.png"
    bg2.save(out2)
    outputs.append(out2)

    bg3 = soft_background((2880, 1440), left_clear=True)
    d3 = ImageDraw.Draw(bg3)
    milestones = [(1180, 760), (1640, 760), (2100, 760)]
    for idx, p in enumerate(milestones):
        d3.ellipse((p[0] - 74, p[1] - 74, p[0] + 74, p[1] + 74), fill=(246, 226, 193), outline=(201, 168, 115), width=6)
        if idx < len(milestones) - 1:
            d3.line((p[0] + 74, p[1], milestones[idx + 1][0] - 74, milestones[idx + 1][1]), fill=(150, 104, 60), width=10)
            d3.polygon([(milestones[idx + 1][0] - 82, p[1] - 14), (milestones[idx + 1][0] - 82, p[1] + 14), (milestones[idx + 1][0] - 50, p[1])], fill=(150, 104, 60))
    paste_mascot(bg3, base_face, (930, 420, 1350, 1220))
    out3 = BACKGROUNDS_DIR / "03_提效到变现路径_定版.png"
    bg3.save(out3)
    outputs.append(out3)

    bg4 = soft_background((2880, 1440), left_clear=True)
    d4 = ImageDraw.Draw(bg4)
    board = (1220, 260, 2380, 1000)
    d4.rounded_rectangle(board, radius=36, fill=(250, 239, 218), outline=(206, 174, 123), width=5)
    notes = [(1300, 350, 1540, 510), (1605, 350, 1845, 510), (1910, 350, 2150, 510), (1450, 580, 1690, 740), (1760, 580, 2000, 740)]
    for i, n in enumerate(notes):
        draw_card(d4, n, ["check", "circle", "tick", "check", "tick"][i])
    paste_mascot(bg4, base_face, (2240, 760, 2700, 1320))
    out4 = BACKGROUNDS_DIR / "04_讲人话的AI教练_定版.png"
    bg4.save(out4)
    outputs.append(out4)

    bg5 = soft_background((2880, 1440), left_clear=True)
    d5 = ImageDraw.Draw(bg5)
    d5.line((1220, 900, 1620, 690), fill=(188, 144, 103), width=18)
    d5.line((1220, 900, 1620, 1080), fill=(188, 144, 103), width=18)
    d5.line((1620, 690, 2200, 620), fill=(143, 102, 58), width=18)
    d5.line((1620, 1080, 2200, 1140), fill=(214, 185, 142), width=18)
    for rect in [(1880, 520, 2090, 700), (1880, 1020, 2090, 1200)]:
        draw_card(d5, rect, "tick" if rect[1] < 800 else "circle")
    paste_mascot(bg5, base_face, (980, 520, 1380, 1220))
    out5 = BACKGROUNDS_DIR / "05_避坑与判断_定版.png"
    bg5.save(out5)
    outputs.append(out5)

    return outputs


def build_preview(paths: list[Path], out_path: Path, thumb=(620, 620), cols=2) -> None:
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
    rendered_faces = [render_face(spec) for spec in FACES]
    backgrounds = render_backgrounds()
    build_preview(rendered_faces, IMAGES_DIR / "00_土豆崽20张总览.png", thumb=(520, 520), cols=4)
    build_preview(backgrounds, BACKGROUNDS_DIR / "00_背景5张总览.png", thumb=(700, 350), cols=1)


if __name__ == "__main__":
    main()
