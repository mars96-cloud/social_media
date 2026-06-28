from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1242
HEIGHT = 1660
PANEL_GAP = 28
MARGIN = 56

PALETTE = {
    "bg": "#F6F0E4",
    "ink": "#261F1B",
    "muted": "#75655A",
    "panel": "#FFFDF8",
    "accent": "#FF8B5E",
    "accent2": "#FFD9C9",
    "mentor_body": "#E95B4E",
    "learner_body": "#F3D24B",
    "skin": "#FFF0E3",
    "bubble_mentor": "#FFF6EF",
    "bubble_learner": "#EEF8F1",
    "caption_bg": "#FFF7EE",
    "line": "#312722",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for ch in paragraph:
            candidate = current + ch
            if current and text_width(draw, candidate, fnt) > max_width:
                lines.append(current)
                current = ch
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines or [""]


def fit_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    bold: bool = True,
    line_gap: int = 8,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        fnt = font(size, bold=bold)
        lines = wrap(draw, text, fnt, max_width)
        line_height = size + line_gap
        if len(lines) * line_height <= max_height:
            return fnt, lines, line_height
    fnt = font(min_size, bold=bold)
    lines = wrap(draw, text, fnt, max_width)
    return fnt, lines, min_size + line_gap


def draw_header(draw: ImageDraw.ImageDraw, title: str, tag: str) -> None:
    draw.rounded_rectangle((MARGIN, MARGIN, WIDTH - MARGIN, 290), radius=42, fill=PALETTE["panel"])
    draw.rounded_rectangle((MARGIN + 28, MARGIN + 24, MARGIN + 172, MARGIN + 80), radius=24, fill=PALETTE["accent"])
    draw.text((MARGIN + 58, MARGIN + 38), tag, font=font(28, bold=True), fill="white")

    title_font, title_lines, line_h = fit_text_block(
        draw,
        title,
        WIDTH - MARGIN * 2 - 320,
        150,
        58,
        38,
        bold=True,
        line_gap=10,
    )
    y = MARGIN + 112
    for idx, line in enumerate(title_lines[:3]):
        draw.text((MARGIN + 32, y + idx * line_h), line, font=title_font, fill=PALETTE["ink"])

    draw.ellipse((WIDTH - 290, MARGIN + 24, WIDTH - 100, MARGIN + 234), fill=PALETTE["accent2"])
    draw.arc((WIDTH - 250, MARGIN + 74, WIDTH - 140, MARGIN + 156), 10, 170, fill=PALETTE["line"], width=5)
    draw.ellipse((WIDTH - 228, MARGIN + 108, WIDTH - 212, MARGIN + 124), fill=PALETTE["line"])
    draw.ellipse((WIDTH - 178, MARGIN + 108, WIDTH - 162, MARGIN + 124), fill=PALETTE["line"])


def character_anchor(box: tuple[int, int, int, int], role: str) -> tuple[int, int]:
    x1, y1, x2, y2 = box
    if role == "mentor":
        return x1 + 108, y1 + 214
    return x2 - 114, y2 - 138


def draw_shinchan_character(
    draw: ImageDraw.ImageDraw,
    anchor: tuple[int, int],
    role: str,
    pose: str,
    expression: str,
) -> tuple[int, int]:
    x, y = anchor
    body_color = PALETTE["mentor_body"] if role == "mentor" else PALETTE["learner_body"]
    body_w = 76
    body_h = 94

    draw.ellipse((x - 58, y - 172, x + 58, y - 70), fill=PALETTE["skin"], outline=PALETTE["line"], width=4)
    draw.line((x - 36, y - 150, x - 4, y - 154), fill=PALETTE["line"], width=7)
    draw.line((x + 4, y - 154, x + 36, y - 150), fill=PALETTE["line"], width=7)

    brow_y = y - 142
    if expression == "serious":
        draw.line((x - 30, brow_y, x - 6, brow_y - 8), fill=PALETTE["line"], width=6)
        draw.line((x + 6, brow_y - 8, x + 30, brow_y), fill=PALETTE["line"], width=6)
    elif expression == "surprised":
        draw.line((x - 30, brow_y - 8, x - 8, brow_y - 18), fill=PALETTE["line"], width=6)
        draw.line((x + 8, brow_y - 18, x + 30, brow_y - 8), fill=PALETTE["line"], width=6)
    elif expression == "thinking":
        draw.line((x - 30, brow_y - 2, x - 8, brow_y - 6), fill=PALETTE["line"], width=6)
        draw.line((x + 8, brow_y - 6, x + 30, brow_y - 2), fill=PALETTE["line"], width=6)

    eye_y = y - 126
    if expression == "thinking":
        draw.ellipse((x - 24, eye_y, x - 12, eye_y + 10), fill=PALETTE["line"])
        draw.line((x + 12, eye_y + 6, x + 28, eye_y + 6), fill=PALETTE["line"], width=4)
    else:
        draw.ellipse((x - 24, eye_y, x - 12, eye_y + 10), fill=PALETTE["line"])
        draw.ellipse((x + 12, eye_y, x + 24, eye_y + 10), fill=PALETTE["line"])

    if expression == "surprised":
        draw.ellipse((x - 10, y - 110, x + 10, y - 88), outline=PALETTE["line"], width=4)
    elif expression == "thinking":
        draw.arc((x - 22, y - 112, x + 22, y - 88), 190, 350, fill=PALETTE["line"], width=4)
    else:
        draw.arc((x - 20, y - 112, x + 20, y - 88), 10, 170, fill=PALETTE["line"], width=4)

    draw.rounded_rectangle((x - body_w // 2, y - 70, x + body_w // 2, y + body_h // 2), radius=20, fill=body_color, outline=PALETTE["line"], width=4)

    if pose == "point":
        draw.line((x + body_w // 2, y - 30, x + 86, y - 58), fill=PALETTE["line"], width=4)
        draw.line((x + 86, y - 58, x + 108, y - 60), fill=PALETTE["line"], width=4)
        draw.line((x - body_w // 2, y - 24, x - 76, y + 14), fill=PALETTE["line"], width=4)
    elif pose == "think":
        draw.line((x + body_w // 2, y - 26, x + 72, y - 4), fill=PALETTE["line"], width=4)
        draw.line((x - body_w // 2, y - 24, x - 54, y - 46), fill=PALETTE["line"], width=4)
        draw.line((x - 54, y - 46, x - 46, y - 66), fill=PALETTE["line"], width=4)
    elif pose == "excited":
        draw.line((x + body_w // 2, y - 28, x + 76, y - 70), fill=PALETTE["line"], width=4)
        draw.line((x - body_w // 2, y - 28, x - 74, y - 70), fill=PALETTE["line"], width=4)
    else:
        draw.line((x + body_w // 2, y - 28, x + 78, y - 6), fill=PALETTE["line"], width=4)
        draw.line((x - body_w // 2, y - 24, x - 76, y + 10), fill=PALETTE["line"], width=4)

    if pose == "walk":
        draw.line((x - 14, y + body_h // 2, x - 32, y + 122), fill=PALETTE["line"], width=4)
        draw.line((x + 10, y + body_h // 2, x + 40, y + 100), fill=PALETTE["line"], width=4)
    else:
        draw.line((x - 14, y + body_h // 2, x - 28, y + 112), fill=PALETTE["line"], width=4)
        draw.line((x + 14, y + body_h // 2, x + 28, y + 112), fill=PALETTE["line"], width=4)

    return x, y - 118


def draw_bubble(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    fill: str,
    tail_to: tuple[int, int],
    tail_side: str,
) -> None:
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=28, fill=fill, outline=PALETTE["line"], width=4)
    tx, ty = tail_to
    if tail_side == "left":
        base_mid_x = x1 + 42
        base1 = (base_mid_x - 10, y2 - 6)
        base2 = (base_mid_x + 14, y2 - 18)
    else:
        base_mid_x = x2 - 42
        base1 = (base_mid_x - 14, y2 - 18)
        base2 = (base_mid_x + 10, y2 - 6)
    tail_tip = (int((tx * 0.72) + (base_mid_x * 0.28)), int((ty * 0.72) + ((y2 - 10) * 0.28)))
    draw.polygon([base1, base2, tail_tip], fill=fill, outline=PALETTE["line"])

    fnt, lines, line_h = fit_text_block(draw, text, x2 - x1 - 38, y2 - y1 - 28, 30, 22, bold=True, line_gap=6)
    top = y1 + max(14, ((y2 - y1) - len(lines) * line_h) // 2 - 4)
    for idx, line in enumerate(lines):
        draw.text((x1 + 20, top + idx * line_h), line, font=fnt, fill=PALETTE["ink"])


def bubble_rect_for_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    side: str,
    top_y: int,
    width_ratio: float,
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    max_w = int((x2 - x1) * width_ratio)
    min_w = int((x2 - x1) * (width_ratio - 0.16))
    probe_font = font(30, bold=True)
    lines = wrap(draw, text, probe_font, max_w - 40)
    width = max(min_w, min(max_w, max(text_width(draw, line, probe_font) for line in lines) + 42))
    height = min(136, max(82, len(lines) * 36 + 28))
    if side == "left":
        bx1 = x1 + 18
        bx2 = bx1 + width
    else:
        bx2 = x2 - 18
        bx1 = bx2 - width
    by1 = top_y
    by2 = by1 + height
    return bx1, by1, bx2, by2


def pose_for(role: str, page_idx: int, scene_idx: int) -> str:
    mentor_poses = ["point", "excited", "think", "walk"]
    learner_poses = ["think", "walk", "excited", "default"]
    poses = mentor_poses if role == "mentor" else learner_poses
    return poses[(page_idx + scene_idx) % len(poses)]


def expression_for(role: str, page_idx: int, scene_idx: int) -> str:
    mentor_expr = ["serious", "smile", "thinking", "serious"]
    learner_expr = ["thinking", "surprised", "smile", "surprised"]
    table = mentor_expr if role == "mentor" else learner_expr
    return table[(page_idx + scene_idx) % len(table)]


def render_page(output_path: Path, page: dict, page_idx: int) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE["bg"])
    draw = ImageDraw.Draw(image)
    draw_header(draw, page["title"], page["tag"])

    panel_top = 334
    panel_h = (HEIGHT - panel_top - MARGIN - PANEL_GAP) // 2
    panel_w = (WIDTH - MARGIN * 2 - PANEL_GAP) // 2
    panels = [
        (MARGIN, panel_top, MARGIN + panel_w, panel_top + panel_h),
        (MARGIN + panel_w + PANEL_GAP, panel_top, WIDTH - MARGIN, panel_top + panel_h),
        (MARGIN, panel_top + panel_h + PANEL_GAP, MARGIN + panel_w, HEIGHT - MARGIN),
        (MARGIN + panel_w + PANEL_GAP, panel_top + panel_h + PANEL_GAP, WIDTH - MARGIN, HEIGHT - MARGIN),
    ]

    label_font = font(22, bold=True)
    caption_font = font(22)

    for idx, panel in enumerate(panels):
        px1, py1, px2, py2 = panel
        draw.rounded_rectangle(panel, radius=34, fill=PALETTE["panel"], outline=PALETTE["line"], width=4)
        draw.rounded_rectangle((px1 + 18, py1 + 16, px1 + 86, py1 + 54), radius=18, fill=PALETTE["accent2"])
        draw.text((px1 + 34, py1 + 24), f"{idx + 1}", font=label_font, fill=PALETTE["ink"])

    for scene_idx, scene in enumerate(page["scenes"][:4]):
        px1, py1, px2, py2 = panels[scene_idx]
        mentor_anchor = character_anchor(panels[scene_idx], "mentor")
        learner_anchor = character_anchor(panels[scene_idx], "learner")

        mentor_mouth = draw_shinchan_character(
            draw,
            mentor_anchor,
            "mentor",
            pose_for("mentor", page_idx, scene_idx),
            expression_for("mentor", page_idx, scene_idx),
        )
        learner_mouth = draw_shinchan_character(
            draw,
            learner_anchor,
            "learner",
            pose_for("learner", page_idx, scene_idx),
            expression_for("learner", page_idx, scene_idx),
        )

        mentor_top = py1 + 46
        learner_top = py2 - 174
        mentor_rect = bubble_rect_for_text(draw, scene["mentor"], panels[scene_idx], "right", mentor_top, 0.56)
        learner_rect = bubble_rect_for_text(draw, scene["learner"], panels[scene_idx], "left", learner_top, 0.50)

        draw_bubble(
            draw,
            mentor_rect,
            scene["mentor"],
            PALETTE["bubble_mentor"],
            mentor_mouth,
            "right",
        )
        draw_bubble(
            draw,
            learner_rect,
            scene["learner"],
            PALETTE["bubble_learner"],
            learner_mouth,
            "left",
        )

        cap_x1 = px1 + 18
        cap_x2 = px2 - 18
        cap_y1 = py2 - 54
        cap_y2 = py2 - 16
        draw.rounded_rectangle((cap_x1, cap_y1, cap_x2, cap_y2), radius=14, fill=PALETTE["caption_bg"])
        cap_font, cap_lines, cap_h = fit_text_block(draw, scene["caption"], cap_x2 - cap_x1 - 24, cap_y2 - cap_y1 - 8, 22, 18, bold=False, line_gap=4)
        cap_y = cap_y1 + ((cap_y2 - cap_y1) - len(cap_lines) * cap_h) // 2 - 1
        for idx, line in enumerate(cap_lines[:2]):
            draw.text((cap_x1 + 12, cap_y + idx * cap_h), line, font=cap_font, fill=PALETTE["muted"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    for page_idx, page in enumerate(spec["pages"]):
        render_page(Path(spec["output_dir"]) / page["file"], page, page_idx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
