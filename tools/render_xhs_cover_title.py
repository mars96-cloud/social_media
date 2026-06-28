from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def fit_font(draw, text, font_path, max_width, start_size, min_size=40, stroke_width=0):
    for size in range(start_size, min_size - 1, -4):
        font = ImageFont.truetype(str(font_path), size)
        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=16, stroke_width=stroke_width)
        if box[2] - box[0] <= max_width:
            return font
    return ImageFont.truetype(str(font_path), min_size)


def main():
    root = Path(__file__).resolve().parents[1]
    pkg = root / "06_运营中心" / "2026" / "2026-07" / "小红书" / "2026-07-01" / "20260701_小红书_不是你不会用AI而是你没有第一条工作流"
    src = pkg / "images" / "01_封面-20260628-173830-1.png"
    dst = pkg / "images" / "01_封面_标题版.png"

    img = Image.open(src).convert("RGBA")
    draw = ImageDraw.Draw(img)

    bold = Path(r"C:\Windows\Fonts\msyhbd.ttc")
    regular = Path(r"C:\Windows\Fonts\msyh.ttc")

    title = "学了 AI\n还是没提效？"
    subtitle = "你缺的可能是\n第一条工作流"

    left_x = int(img.width * 0.075)
    title_y = int(img.height * 0.20)
    max_width = int(img.width * 0.42)

    title_font = fit_font(draw, title, bold, max_width, 164, min_size=88, stroke_width=4)
    subtitle_font = fit_font(draw, subtitle, regular, max_width, 62, min_size=40)

    # Small hand-drawn accent behind the pain word, kept away from the character.
    accent_y = title_y + 145
    draw.rounded_rectangle(
        (left_x - 18, accent_y - 8, left_x + 420, accent_y + 82),
        radius=28,
        fill=(255, 122, 34, 42),
        outline=None,
    )

    draw.multiline_text(
        (left_x, title_y),
        title,
        font=title_font,
        fill=(18, 18, 18, 255),
        spacing=22,
        stroke_width=4,
        stroke_fill=(255, 255, 255, 255),
    )

    sub_y = title_y + 440
    draw.multiline_text(
        (left_x + 8, sub_y),
        subtitle,
        font=subtitle_font,
        fill=(42, 42, 42, 255),
        spacing=12,
    )

    draw.line(
        (left_x + 4, sub_y + 180, left_x + 430, sub_y + 180),
        fill=(255, 122, 34, 255),
        width=12,
    )

    dst.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dst, quality=95)
    print(dst)


if __name__ == "__main__":
    main()
