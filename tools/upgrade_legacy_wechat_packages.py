#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image


MAJOR_HEADING_RE = re.compile(r"^[一二三四五六七八九十]+、")
IMAGE_RE = re.compile(r"^【配图：(.+?)】$")
FIRST_COVER_RE = re.compile(r"^【配图：01_公众号封面(?:\.png)?】$")


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def fit_canvas(src_path: Path, out_path: Path, width: int, height: int) -> None:
    src = Image.open(src_path).convert("RGBA")
    bg = src.getpixel((min(15, src.width - 1), min(15, src.height - 1)))
    canvas = Image.new("RGBA", (width, height), bg)
    ratio = min(width / src.width, height / src.height)
    draw_w = round(src.width * ratio)
    draw_h = round(src.height * ratio)
    resized = src.resize((draw_w, draw_h), Image.Resampling.LANCZOS)
    draw_x = round((width - draw_w) / 2)
    draw_y = round((height - draw_h) / 2)
    canvas.paste(resized, (draw_x, draw_y), resized)
    canvas.save(out_path)


def get_digest(lines: list[str]) -> str:
    parts: list[str] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if IMAGE_RE.match(text):
            continue
        if MAJOR_HEADING_RE.match(text):
            break
        parts.append(text)
        if len("".join(parts)) >= 90:
            break
    digest = "".join(parts)[:110]
    return digest


def build_mapping(title: str, lines: list[str]) -> str:
    headings: list[str] = []
    records: list[tuple[str, str, int]] = []
    current_major = ""
    current_paragraph = 0

    for raw in lines:
        line = raw.strip()
        if not line or line == title:
            continue
        if MAJOR_HEADING_RE.match(line):
            current_major = line
            headings.append(line)
            current_paragraph = 0
            continue
        m = IMAGE_RE.match(line)
        if m:
            records.append((m.group(1), current_major, max(current_paragraph, 1)))
            continue
        current_paragraph += 1

    out: list[str] = []
    out.append("# 正文结构与配图映射")
    out.append("")
    out.append("## 文章层级")
    out.append("")
    out.append(f"- 一级标题：{title}")
    for idx, heading in enumerate(headings, start=1):
        out.append(f"- 二级标题 {idx}：{heading}")
    out.append("")
    out.append("## 配图映射")
    out.append("")
    out.append("### 图 01 封面")
    out.append("")
    out.append("- 文件：images/01_公众号封面_标题版_2.35比1.png")
    out.append("- 用途：封面")
    out.append("- 不进入正文")
    out.append("")
    for idx, (file_name, heading, paragraph) in enumerate(records, start=2):
        out.append(f"### 图 {idx} 正文图")
        out.append("")
        out.append(f"- 文件：images/{file_name}")
        out.append(f"- 插在：{heading} 下，第 {paragraph} 段后")
        out.append("- 作用：承接该节核心判断")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def upgrade_package(folder: Path) -> dict | None:
    images_dir = folder / "images"
    body_path = folder / "草稿箱正文.txt"
    meta_path = folder / "metadata.json"
    cover_old = images_dir / "01_公众号封面.png"
    if not (images_dir.exists() and body_path.exists() and meta_path.exists() and cover_old.exists()):
        return None

    lines = read_lines(body_path)
    clean_lines: list[str] = []
    removed_first_cover = False
    for line in lines:
        if not removed_first_cover and FIRST_COVER_RE.match(line.strip()):
            removed_first_cover = True
            continue
        clean_lines.append(line)
    if removed_first_cover:
        write_text(body_path, "\n".join(clean_lines).rstrip() + "\n")

    title = next((line.strip() for line in clean_lines if line.strip()), "")
    if not title:
        return None

    wide_title = images_dir / "01_公众号封面_标题版_2.35比1.png"
    square_title = images_dir / "01_公众号封面_标题版_1比1.png"
    wide_base = images_dir / "01_公众号封面_底图_2.35比1.png"
    square_base = images_dir / "01_公众号封面_底图_1比1.png"
    fit_canvas(cover_old, wide_title, 2820, 1200)
    fit_canvas(cover_old, square_title, 1600, 1600)
    wide_base.write_bytes(wide_title.read_bytes())
    square_base.write_bytes(square_title.read_bytes())

    legacy = json.loads(meta_path.read_text(encoding="utf-8"))
    body_image_paths = [
        f"images/{name}"
        for name in legacy.get("image_files", [])
        if name and not name.startswith("01_公众号封面")
    ]
    new_meta = {
        "platform": "wechat",
        "title": title,
        "digest": get_digest(clean_lines[1:]),
        "source_article": "",
        "cover_path": "images/01_公众号封面_标题版_2.35比1.png",
        "body_image_paths": body_image_paths,
        "status": "draft-ready",
        "legacy": legacy,
    }
    meta_path.write_text(json.dumps(new_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    mapping_path = folder / "正文结构与配图映射.md"
    write_text(mapping_path, build_mapping(title, clean_lines))

    return {
        "package": folder.name,
        "title": title,
        "cover": str(new_meta["cover_path"]),
        "body_image_count": len(body_image_paths),
        "removed_body_cover": removed_first_cover,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    results = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and p.name != "_样张对比"):
        result = upgrade_package(folder)
        if result:
            results.append(result)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
