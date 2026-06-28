# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\Administrator\Desktop\codex_project\social_media")
ARTICLE_DIR = ROOT / r"06_运营中心\2026\2026-07\公众号\2026-07-01\20260701_公众号_不是你不会用AI而是你没有第一条工作流"
IMAGES_DIR = ARTICLE_DIR / "images"
TMP_DIR = ROOT / "tmp_render"
TMP_DIR.mkdir(exist_ok=True)

bg_path = IMAGES_DIR / "01_公众号封面_底图.jpeg"
out_path = TMP_DIR / "wechat_cover_title_fixed_v2.png"

title_lines = [
    ("不是你不会用 AI", "main"),
    ("是你一直没有", "accent"),
    ("第一条工作流", "accent"),
]
subtitle = "别再只学工具了"

font_bold = Path(r"C:\Windows\Fonts\msyhbd.ttc")
font_regular = Path(r"C:\Windows\Fonts\msyh.ttc")

img = Image.open(bg_path).convert("RGBA")
w, h = img.size

canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(canvas)

# Strict title safe zone:
# keep away from the dense doodle area on the right and avoid oversized panel.
box_x = int(w * 0.07)
box_y = int(h * 0.07)
box_w = int(w * 0.57)
box_h = int(h * 0.30)

shadow = (0, 0, 0, 28)
panel = (255, 252, 246, 215)
main = (20, 20, 20, 255)
accent = (255, 130, 56, 255)
sub = (95, 104, 116, 255)
border = (236, 226, 212, 235)

draw.rounded_rectangle(
    [box_x + 8, box_y + 10, box_x + box_w + 8, box_y + box_h + 10],
    radius=24,
    fill=shadow,
)
draw.rounded_rectangle(
    [box_x, box_y, box_x + box_w, box_y + box_h],
    radius=24,
    fill=panel,
    outline=border,
    width=2,
)

font_main = ImageFont.truetype(str(font_bold), int(h * 0.063))
font_accent = ImageFont.truetype(str(font_bold), int(h * 0.053))
font_sub = ImageFont.truetype(str(font_regular), int(h * 0.025))

pad_x = int(box_w * 0.08)
current_y = box_y + int(box_h * 0.14)
max_text_right = box_x + box_w - pad_x

for text, style in title_lines:
    font = font_main if style == "main" else font_accent
    fill = main if style == "main" else accent
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    if box_x + pad_x + text_w > max_text_right:
        scale = (max_text_right - (box_x + pad_x)) / text_w
        resized = max(72, int(font.size * scale))
        font = ImageFont.truetype(str(font_bold), resized)
    draw.text((box_x + pad_x, current_y), text, font=font, fill=fill)
    line_box = draw.textbbox((box_x + pad_x, current_y), text, font=font)
    current_y = line_box[3] + int(h * 0.012)

current_y += int(h * 0.012)
draw.text((box_x + pad_x, current_y), subtitle, font=font_sub, fill=sub)

merged = Image.alpha_composite(img, canvas).convert("RGB")
merged.save(out_path, quality=95)
merged.save(IMAGES_DIR / "01_公众号封面_标题版.png", quality=95)

print(str(IMAGES_DIR / "01_公众号封面_标题版.png"))
