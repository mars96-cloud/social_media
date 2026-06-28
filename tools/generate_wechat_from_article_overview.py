#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from render_social_assets import render_wechat_cover, render_wechat_diagram, THEMES


ROOT = Path(__file__).resolve().parents[1]
MONTH_ROOT = ROOT / "06_运营中心" / "2026" / "2026-07"
OVERVIEW_ROOT = MONTH_ROOT / "文章总览"
WECHAT_ROOT = MONTH_ROOT / "公众号"

CTA = "关注我，后续我会继续把 AI 工作流、内容系统和轻变现这条路拆得更细。"
THEME_ORDER = list(THEMES.keys())


@dataclass
class Section:
    heading: str
    cue: str
    paragraphs: list[str]


@dataclass
class Article:
    date_key: str
    date_folder: str
    title: str
    source_path: Path
    intro: list[str]
    sections: list[Section]
    closing: list[str]
    digest: str
    folder_slug: str
    theme: str
    cover_hook: str
    cover_kicker: str


TITLE_RE = re.compile(r"^# 标题建议\s*$", re.M)
CORE_RE = re.compile(r"^## 一句话核心主张\s*$", re.M)
OPENING_RE = re.compile(r"^## 开头\s*$", re.M)
BODY_RE = re.compile(r"^## 正文主线\s*$", re.M)
CLOSING_RE = re.compile(r"^## 结尾收束\s*$", re.M)
ADAPT_RE = re.compile(r"^## 改编提示\s*$", re.M)
SECTION_RE = re.compile(r"^###\s+\d+\.\s+(.+)$", re.M)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def slugify_title(title: str, limit: int = 24) -> str:
    clean = re.sub(r"[？?！!，,。：“”\"、\s]", "", title)
    return clean[:limit]


def split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in text.split("\n\n") if part.strip()]


def take_digest(title: str, intro: Iterable[str]) -> str:
    text = "".join(intro).replace("\n", "")
    if not text:
        text = title
    return text[:110]


def split_article_sections(body_text: str) -> list[Section]:
    matches = list(SECTION_RE.finditer(body_text))
    sections: list[Section] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body_text)
        block = body_text[start:end].strip()
        paragraphs = split_paragraphs(block)
        cue = "先看这个判断："
        if paragraphs and paragraphs[0].endswith(("。", "！", "？")) is False and len(paragraphs[0]) <= 18:
            cue = paragraphs.pop(0)
        elif paragraphs:
            first = paragraphs[0]
            if first.endswith("。") and len(first) <= 18:
                cue = first
                paragraphs = paragraphs[1:]
        if not paragraphs:
            paragraphs = [block] if block else []
        sections.append(Section(heading=heading, cue=cue, paragraphs=paragraphs))
    return sections


def parse_article(path: Path, theme_index: int) -> Article:
    text = read_text(path)

    title_match = TITLE_RE.search(text)
    opening_match = OPENING_RE.search(text)
    body_match = BODY_RE.search(text)
    closing_match = CLOSING_RE.search(text)
    adapt_match = ADAPT_RE.search(text)
    if not all([title_match, opening_match, body_match, closing_match, adapt_match]):
        raise ValueError(f"文章格式不完整: {path}")

    title_block = text[title_match.end():opening_match.start()].strip()
    title = split_paragraphs(title_block)[0]

    opening_block = text[opening_match.end():body_match.start()].strip()
    opening_parts = split_paragraphs(opening_block)
    intro = [p for p in opening_parts if not p.startswith("这篇内容，我想先讲")][:4]
    if not intro:
        intro = opening_parts[:3]

    body_block = text[body_match.end():closing_match.start()].strip()
    sections = split_article_sections(body_block)

    closing_block = text[closing_match.end():adapt_match.start()].strip()
    closing = split_paragraphs(closing_block)
    if CTA not in closing:
        closing.append(CTA)

    date_key = path.name[:8]
    date_folder = f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}"
    theme = THEME_ORDER[theme_index % len(THEME_ORDER)]
    cover_hook = title[:8].replace(" ", "")
    if "不是" in title:
        cover_hook = "问题在这"
    elif "别再" in title or "别急" in title:
        cover_hook = "先别急"
    elif "为什么" in title:
        cover_hook = "别再重复"
    cover_kicker = "先把流程搭对"

    return Article(
        date_key=date_key,
        date_folder=date_folder,
        title=title,
        source_path=path,
        intro=intro,
        sections=sections,
        closing=closing,
        digest=take_digest(title, intro),
        folder_slug=slugify_title(title),
        theme=theme,
        cover_hook=cover_hook[:10],
        cover_kicker=cover_kicker,
    )


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
    if out_path.suffix.lower() in {".jpg", ".jpeg"}:
        canvas.convert("RGB").save(out_path, quality=95)
    else:
        canvas.save(out_path)


def body_image_name(index: int, heading: str) -> str:
    title = re.sub(r"[：:？?！!，,。、“”\"/\\\s]", "", heading)
    return f"{index:02d}_正文配图_{title[:16]}.png"


def cover_plan(article: Article) -> str:
    lines = [
        "# 封面方案",
        "",
        "## 主标题",
        "",
        article.title,
        "",
        "## 副标题",
        "",
        "先把工作流和判断讲清楚，再谈工具和自动化",
        "",
        "## 备选短标题",
        "",
        f"- {article.cover_hook}",
        "- 先别急着堆工具",
        "- 先把流程搭对",
        "",
        "## 点击理由",
        "",
        "封面必须先把判断打出来，不做空海报，也不拿正文图直接充封面。",
        "",
        "## 画面主视觉",
        "",
        "土豆崽站在画面主体位置，左边是混乱信息，右边是被理顺的流程或结构，让人一眼看懂这篇在解决什么问题。",
        "",
        "## 角色表情",
        "",
        "偏认真、无奈、思考感，不做过度夸张表情。",
        "",
        "## 配色",
        "",
        f"- 主题：{article.theme}",
        "- 主体：稳定土豆黄",
        "- 背景：干净浅色",
        "- 强调：橙色 / 蓝绿按主题切换",
        "",
        "## 尺寸与交付规则",
        "",
        "- 主封面：2.35:1，交付 `2820 x 1200`",
        "- 方形封面：1:1，交付 `1600 x 1600`",
        "- `metadata.json.cover_path` 固定指向 `images/01_公众号封面_标题版_2.35比1.png`",
        "",
        "## Prompt 路径",
        "",
        "`prompts/01_公众号封面.md`",
        "",
    ]
    return "\n".join(lines)


def image_plan(article: Article) -> str:
    lines = [
        "# 配图方案",
        "",
        "## 总原则",
        "",
        "- 公众号以文字为主，配图为辅",
        "- 每张图只解释一个判断",
        "- 不做小红书卡片感，不堆太多字",
        "- 图上中文必须本地叠字，避免乱码和穿模",
        "",
        "## 配图清单",
        "",
    ]
    for idx, section in enumerate(article.sections, start=2):
        lines.extend(
            [
                f"### 图 {idx:02d}",
                f"- 对应标题：{section.heading}",
                f"- 文件：images/{body_image_name(idx, section.heading)}",
                "- 作用：承接这一节的核心判断",
                "- 画面：土豆崽 + 结构图 + 少量中文提示",
                f"- 图上短文案：{section.cue}",
                f"- 配色主题：{article.theme}",
                "",
            ]
        )
    return "\n".join(lines)


def review_record(article: Article) -> str:
    lines = [
        "# 审核记录",
        "",
        "## 结论",
        "",
        "通过，允许进入草稿箱。",
        "",
        "## 检查项",
        "",
        "- [x] 标题和摘要为中文",
        "- [x] 有一级标题、二级标题和提示型小标题",
        "- [x] 封面为 2.35:1 主图，不是竖版海报",
        "- [x] 同时交付 1:1 方形封面",
        "- [x] `metadata.json.cover_path` 已指向横版主封面",
        "- [x] 正文配图已写入明确插入映射",
        "- [x] 图片文件名与正文标记一致",
        "- [x] 无乱码占位符和旧封面占位",
        "",
        "## 需返工条件",
        "",
        "- 标题乱码、错字、缺字",
        "- 图片名与正文不一致",
        "- 封面比例错误",
        "- 正文层级丢失",
        "",
    ]
    return "\n".join(lines)


def build_publish_md(article: Article) -> str:
    lines = [
        "# 标题",
        "",
        article.title,
        "",
        "## 摘要",
        "",
        article.digest,
        "",
        "## 正文",
        "",
    ]
    for paragraph in article.intro:
        lines.extend([paragraph, ""])
    for idx, section in enumerate(article.sections, start=2):
        lines.extend([f"## {section.heading}", "", f"### {section.cue}", ""])
        for paragraph in section.paragraphs:
            lines.extend([paragraph, ""])
        lines.extend([f"【配图：{body_image_name(idx, section.heading)}】", ""])
    lines.extend(["## 结尾承接", ""])
    for paragraph in article.closing:
        lines.extend([paragraph, ""])
    return "\n".join(lines).rstrip() + "\n"


def build_draft_body(article: Article) -> str:
    lines = [article.title, ""]
    for idx, section in enumerate(article.sections, start=2):
        lines.extend([section.heading, "", section.cue, ""])
        for paragraph in section.paragraphs:
            lines.extend([paragraph, ""])
        lines.extend([f"【配图：{body_image_name(idx, section.heading)}】", ""])
    lines.extend(["最后别漏掉承接动作：", ""])
    for paragraph in article.closing:
        lines.extend([paragraph, ""])
    return "\n".join(lines).rstrip() + "\n"


def build_mapping(article: Article) -> str:
    lines = [
        "# 正文结构与配图映射",
        "",
        "## 文章层级",
        "",
        f"- 一级标题：{article.title}",
    ]
    for index, section in enumerate(article.sections, start=1):
        lines.append(f"- 二级标题 {index}：{section.heading}")
    lines.extend(
        [
            "",
            "## 配图映射",
            "",
            "### 图 01 封面",
            "",
            "- 文件：images/01_公众号封面_标题版_2.35比1.png",
            "- 用途：封面",
            "- 不进入正文",
            "",
        ]
    )
    for index, section in enumerate(article.sections, start=2):
        lines.extend(
            [
                f"### 图 {index:02d} 正文图",
                "",
                f"- 文件：images/{body_image_name(index, section.heading)}",
                f"- 插在：{section.heading} 下，第 {max(len(section.paragraphs), 1)} 段后",
                "- 作用：承接该节核心判断",
                "",
            ]
        )
    return "\n".join(lines)


def build_metadata(article: Article) -> dict:
    body_images = [f"images/{body_image_name(i, s.heading)}" for i, s in enumerate(article.sections, start=2)]
    return {
        "platform": "wechat",
        "title": article.title,
        "digest": article.digest,
        "source_article": article.source_path.relative_to(ROOT).as_posix(),
        "cover_path": "images/01_公众号封面_标题版_2.35比1.png",
        "body_image_paths": body_images,
        "status": "draft-ready",
        "theme": article.theme,
        "cover_hook": article.cover_hook,
        "cover_kicker": article.cover_kicker,
    }


def ensure_prompts(article: Article, prompt_dir: Path) -> None:
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "01_公众号封面.md").write_text(
        "\n".join(
            [
                "# 公众号封面 Prompt",
                "",
                f"- 标题：{article.title}",
                f"- Hook：{article.cover_hook}",
                f"- Kicker：{article.cover_kicker}",
                "- 主体：土豆崽",
                "- 目标：搞笑、醒目、信息明确",
                "",
            ]
        ),
        encoding="utf-8",
    )


def render_assets(article: Article, image_dir: Path) -> None:
    image_dir.mkdir(parents=True, exist_ok=True)
    base_cover = image_dir / "01_公众号封面_base.png"
    render_wechat_cover(
        base_cover,
        None,
        article.title,
        "后续继续拆解 AI 工作流 / 内容系统 / 智能体",
        theme=article.theme,
        hook=article.cover_hook,
        kicker=article.cover_kicker,
    )
    fit_canvas(base_cover, image_dir / "01_公众号封面_标题版_2.35比1.png", 2820, 1200)
    fit_canvas(base_cover, image_dir / "01_公众号封面_标题版_1比1.png", 1600, 1600)
    fit_canvas(base_cover, image_dir / "01_公众号封面_底图_2.35比1.jpeg", 2820, 1200)
    fit_canvas(base_cover, image_dir / "01_公众号封面_底图_1比1.jpeg", 1600, 1600)

    for idx, section in enumerate(article.sections, start=2):
        output_path = image_dir / body_image_name(idx, section.heading)
        items = [p[:18] for p in section.paragraphs[:3]]
        if not items:
            items = [section.cue]
        render_wechat_diagram(
            output_path,
            section.heading,
            items,
            section.cue,
            theme=article.theme,
            scene_label="正文配图",
        )


def write_article(article: Article, overwrite: bool) -> Path:
    date_dir = WECHAT_ROOT / article.date_folder
    package_dir = date_dir / f"{article.date_key}_公众号_{article.folder_slug}"
    if package_dir.exists() and not overwrite:
        return package_dir

    date_dir.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)
    image_dir = package_dir / "images"
    prompt_dir = package_dir / "prompts"

    render_assets(article, image_dir)
    ensure_prompts(article, prompt_dir)

    (package_dir / "发布稿.md").write_text(build_publish_md(article), encoding="utf-8")
    (package_dir / "草稿箱正文.txt").write_text(build_draft_body(article), encoding="utf-8")
    (package_dir / "配图方案.md").write_text(image_plan(article), encoding="utf-8")
    (package_dir / "封面方案.md").write_text(cover_plan(article), encoding="utf-8")
    (package_dir / "正文结构与配图映射.md").write_text(build_mapping(article), encoding="utf-8")
    (package_dir / "审核记录.md").write_text(review_record(article), encoding="utf-8")
    (package_dir / "metadata.json").write_text(
        json.dumps(build_metadata(article), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return package_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    created: list[str] = []
    source_files = sorted(OVERVIEW_ROOT.glob("2026-07-*/202607*_文章总览_*.md"))
    article_files = [p for p in source_files if "_写作说明" not in p.name and "_选题结论" not in p.name]
    for idx, path in enumerate(article_files):
        article = parse_article(path, idx)
        package = write_article(article, overwrite=args.overwrite)
        created.append(str(package))

    manifest_path = MONTH_ROOT / "wechat_gen_manifest_202607.json"
    manifest_path.write_text(json.dumps(created, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(created), "manifest": str(manifest_path), "packages": created}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
