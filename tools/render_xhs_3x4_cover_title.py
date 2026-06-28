from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def fit_font(draw, text, font_path, max_width, max_height, start_size, min_size=40):
    for size in range(start_size, min_size - 1, -4):
        font = ImageFont.truetype(str(font_path), size)
        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=18, stroke_width=4)
        if box[2] - box[0] <= max_width and box[3] - box[1] <= max_height:
            return font
    return ImageFont.truetype(str(font_path), min_size)


def main():
    root = Path(__file__).resolve().parents[1]
    pkg = (
        root
        / "06_运营中心"
        / "2026"
        / "2026-07"
        / "小红书"
        / "2026-07-01"
        / "20260701_小红书_不是你不会用AI而是你没有第一条工作流_3比4本地版"
    )
    src = pkg / "images" / "01_封面.png"
    dst = pkg / "images" / "01_封面_标题版.png"

    img = Image.open(src).convert("RGBA")
    draw = ImageDraw.Draw(img)

    bold = Path(r"C:\Windows\Fonts\msyhbd.ttc")
    regular = Path(r"C:\Windows\Fonts\msyh.ttc")

    title = "学了 AI\n还是没提效？"
    subtitle = "你缺第一条工作流"

    x = int(img.width * 0.08)
    y = int(img.height * 0.08)
    max_width = int(img.width * 0.84)
    max_height = int(img.height * 0.23)

    title_font = fit_font(draw, title, bold, max_width, max_height, 170, 88)
    subtitle_font = fit_font(draw, subtitle, regular, max_width, int(img.height * 0.08), 64, 42)

    accent_y = y + int(img.height * 0.105)
    draw.rounded_rectangle(
        (x - 14, accent_y - 6, x + int(img.width * 0.52), accent_y + 76),
        radius=24,
        fill=(255, 122, 34, 48),
    )

    draw.multiline_text(
        (x, y),
        title,
        font=title_font,
        fill=(18, 18, 18, 255),
        spacing=20,
        stroke_width=4,
        stroke_fill=(255, 255, 255, 255),
    )

    sub_y = int(img.height * 0.255)
    draw.multiline_text(
        (x + 4, sub_y),
        subtitle,
        font=subtitle_font,
        fill=(42, 42, 42, 255),
        spacing=8,
        stroke_width=2,
        stroke_fill=(255, 255, 255, 230),
    )

    sub_box = draw.textbbox((x + 4, sub_y), subtitle, font=subtitle_font, stroke_width=2)
    draw.line(
        (x + 8, sub_box[3] + 18, min(sub_box[2] + 28, x + int(img.width * 0.55)), sub_box[3] + 18),
        fill=(255, 122, 34, 255),
        width=8,
    )

    img.convert("RGB").save(dst, quality=95)
    print(dst)


if __name__ == "__main__":
    main()
