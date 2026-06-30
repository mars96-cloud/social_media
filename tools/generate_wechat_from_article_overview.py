#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MONTH_ROOT = ROOT / "06_运营中心" / "2026" / "2026-07"
OVERVIEW_ROOT = MONTH_ROOT / "文章总览"
WECHAT_ROOT = MONTH_ROOT / "公众号"
MANIFEST_PATH = MONTH_ROOT / "wechat_gen_manifest_202607.json"

CTA = "关注我，后续我会继续把 AI 工作流、内容系统和轻变现这条路拆得更细。"
THEME = "potato-wechat"
DATE_RE = re.compile(r"^2026-07-\d{2}$")

TITLE_RE = re.compile(r"^# 标题建议\s*$", re.M)
OPENING_RE = re.compile(r"^## 开头\s*$", re.M)
BODY_RE = re.compile(r"^## 正文主线\s*$", re.M)
CLOSING_RE = re.compile(r"^## 结尾收束\s*$", re.M)
ADAPT_RE = re.compile(r"^## 改编提示\s*$", re.M)
SECTION_RE = re.compile(r"^###\s+\d+\.\s+(.+)$", re.M)
AUX_HEADING_RE = re.compile(r"^##\s+.+$", re.M)


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
    cover_title: str
    cover_subtitle: str
    cover_reason: str
    cover_visual: str
    cover_emotion: str
    cover_action: str
    cover_props: str
    cover_composition: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in text.split("\n\n") if part.strip()]


def normalize_inline_text(text: str) -> str:
    cleaned = text.replace("\r", " ").replace("\n", " ")
    cleaned = re.sub(r"`+", "", cleaned)
    cleaned = re.sub(r"#+\s*", "", cleaned)
    cleaned = re.sub(r"【[^】]*】", "", cleaned)
    cleaned = re.sub(r"\[[^\]]*\]\([^)]+\)", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def strip_prompt_noise(text: str) -> str:
    cleaned = normalize_inline_text(text)
    cleaned = re.split(r"\s##\s+", cleaned)[0]
    cleaned = re.sub(r"(关键案例或场景位|关键转折句|可复用金句|改编提示|写作说明|选题结论).*", "", cleaned)
    cleaned = cleaned.strip("：:;；，,。. ")
    return cleaned


def clean_title_for_slug(title: str, limit: int = 24) -> str:
    clean = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", title)
    return clean[:limit] or "未命名文章"


def clean_image_fragment(text: str, limit: int = 22) -> str:
    clean = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text)
    return clean[:limit] or "正文配图"


def build_digest(title: str, intro: Iterable[str]) -> str:
    merged = "".join(intro).replace("\n", "")
    return (merged or title)[:110]


def choose_cover_title(title: str) -> str:
    compact = re.sub(r"[，。！？、；：“”《》\s]", "", title)
    if "不是" in title and "而是" in title:
        left, right = title.split("而是", 1)
        left = left.split("不是", 1)[-1]
        candidate = f"别先{left[:8]} 先{right[:8]}"
        return candidate[:16]
    if "为什么" in title:
        candidate = title.replace("为什么", "").replace("？", "").replace("?", "")
        return candidate[:14] or compact[:14]
    return compact[:14]


def choose_cover_subtitle(title: str, sections: list[Section]) -> str:
    if sections:
        primary = sections[0].heading
        if len(primary) <= 18:
            return primary
    if "系统" in title:
        return "先把系统搭起来"
    if "工作流" in title:
        return "先把工作流跑顺"
    return "先把判断和动作理顺"


def infer_cover_visual(title: str, sections: list[Section]) -> str:
    if "选题" in title:
        return "土豆崽站在选题池前，把一堆零散纸条整理成清晰标签墙"
    if "工作流" in title:
        return "土豆崽一手按住失控机器，一手把散乱步骤拉回主轨道"
    if "内容" in title:
        return "土豆崽把零散内容卡片拼成一条能反复跑的生产线"
    return "土豆崽把混乱信息重新整理成能看懂的结构路径"


def infer_cover_reason(title: str) -> str:
    if "不是" in title:
        return "封面需要先把反常识判断打出来，让读者一眼感到顺序被纠正了。"
    if "为什么" in title:
        return "封面要把“问题根源”直接戳出来，读者缩略图下也能看懂冲突。"
    return "封面要先给读者一个明确判断，而不是做一张空海报。"


def infer_cover_emotion(title: str) -> str:
    if "为什么" in title or "问题" in title:
        return "皱眉、认真、带一点质问感"
    return "认真、克制、带一点反差感"


def infer_cover_props(title: str, sections: list[Section]) -> str:
    props: list[str] = []
    if "选题" in title:
        props.extend(["标签墙", "选题卡片", "箭头轨道"])
    if "工作流" in title:
        props.extend(["失控机器", "流程卡", "主轨道"])
    if "AI" in title:
        props.append("橙红色提示箭头")
    if not props and sections:
        props.extend(["结构图", "步骤卡片", "留白标题区"])
    return "、".join(dict.fromkeys(props))


def infer_cover_composition(title: str) -> str:
    if "选题" in title:
        return "主体偏中右，左上到中上留出标题安全区，缩略图下一眼能看懂“零散变系统”的对比。"
    return "主体放中下部，标题区位于中上或左上，画面必须有明显冲突和主次关系。"


def normalize_cue(paragraphs: list[str]) -> tuple[str, list[str]]:
    if not paragraphs:
        return "先看这个判断", []
    first = strip_prompt_noise(paragraphs[0])
    if len(first) <= 20 and not first.endswith(("。", "！", "？")):
        return first, paragraphs[1:]
    if len(first) <= 22 and first.endswith(("。", "！", "？")):
        return first.rstrip("。！？"), paragraphs[1:]
    cue = first[:18].rstrip("，。；：")
    return cue or "先看这个判断", paragraphs


def split_article_sections(body_text: str) -> list[Section]:
    matches = list(SECTION_RE.finditer(body_text))
    sections: list[Section] = []
    for idx, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        next_section_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(body_text)
        aux_matches = [m.start() for m in AUX_HEADING_RE.finditer(body_text, start, next_section_start)]
        end = aux_matches[0] if aux_matches else next_section_start
        block = body_text[start:end].strip()
        paragraphs = [strip_prompt_noise(item) for item in split_paragraphs(block)]
        paragraphs = [item for item in paragraphs if item]
        cue, remaining = normalize_cue(paragraphs)
        content = remaining or paragraphs[:]
        if not content and block:
            fallback = strip_prompt_noise(block)
            content = [fallback] if fallback else []
        sections.append(Section(heading=heading, cue=cue, paragraphs=content))
    return sections


def parse_article(path: Path) -> Article:
    text = read_text(path)
    title_match = TITLE_RE.search(text)
    opening_match = OPENING_RE.search(text)
    body_match = BODY_RE.search(text)
    closing_match = CLOSING_RE.search(text)
    adapt_match = ADAPT_RE.search(text)
    if not all([title_match, opening_match, body_match, closing_match, adapt_match]):
        raise ValueError(f"文章结构不完整: {path}")

    title_block = text[title_match.end():opening_match.start()].strip()
    title = split_paragraphs(title_block)[0]

    opening_block = text[opening_match.end():body_match.start()].strip()
    intro = [
        part for part in split_paragraphs(opening_block)
        if not part.startswith("这篇内容，我想先讲")
    ][:4]
    if not intro:
        intro = split_paragraphs(opening_block)[:3]

    body_block = text[body_match.end():closing_match.start()].strip()
    sections = split_article_sections(body_block)

    closing_block = text[closing_match.end():adapt_match.start()].strip()
    closing = split_paragraphs(closing_block)
    if CTA not in closing:
        closing.append(CTA)

    date_key = path.name[:8]
    date_folder = f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}"

    return Article(
        date_key=date_key,
        date_folder=date_folder,
        title=title,
        source_path=path,
        intro=intro,
        sections=sections,
        closing=closing,
        digest=build_digest(title, intro),
        folder_slug=clean_title_for_slug(title),
        cover_title=choose_cover_title(title),
        cover_subtitle=choose_cover_subtitle(title, sections),
        cover_reason=infer_cover_reason(title),
        cover_visual=infer_cover_visual(title, sections),
        cover_emotion=infer_cover_emotion(title),
        cover_action="一手按住混乱源头，一手把关键步骤拉回可复用主线",
        cover_props=infer_cover_props(title, sections),
        cover_composition=infer_cover_composition(title),
    )


def body_image_name(index: int, heading: str) -> str:
    return f"{index:02d}_正文配图_{clean_image_fragment(heading, 18)}.png"


def body_prompt_filename(index: int, heading: str) -> str:
    return f"{index:02d}_正文配图_{clean_image_fragment(heading, 18)}.md"


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


def build_cover_plan(article: Article) -> str:
    lines = [
        "# 封面方案",
        "",
        "## 主标题",
        "",
        article.cover_title,
        "",
        "## 副标题",
        "",
        article.cover_subtitle,
        "",
        "## 备选短标题",
        "",
        f"- {article.cover_title}",
        f"- {article.cover_subtitle}",
        f"- {clean_title_for_slug(article.title, 12)}",
        "",
        "## 点击理由",
        "",
        article.cover_reason,
        "",
        "## 画面主视觉",
        "",
        article.cover_visual,
        "",
        "## 土豆崽表情",
        "",
        article.cover_emotion,
        "",
        "## 配色",
        "",
        "- 主题：potato-wechat",
        "- 主体：稳定土豆黄",
        "- 点缀：橙红色 / 蓝绿色少量提示",
        "- 背景：干净浅白，不要大面积色块压图",
        "",
        "## 本地叠字建议",
        "",
        "- 标题必须放在预留安全区内",
        "- 禁止压住土豆崽脸、手、关键道具和主结构路径",
        "- 标题与副标题由本地脚本叠字，不依赖模型写中文",
        "",
        "## 生成链路",
        "",
        "- 底图唯一入口：potato-illustrations",
        "- 正式链路：wechat-gen -> potato-illustrations -> ark-image-generation",
        "",
        "## Prompt 路径",
        "",
        "`prompts/01_公众号封面.md`",
        "",
    ]
    return "\n".join(lines)


def build_image_plan(article: Article) -> str:
    lines = [
        "# 配图方案",
        "",
        "## 总原则",
        "",
        "- 公众号以文字为主，配图只解释一个核心判断",
        "- 每张图都必须有土豆崽参与核心动作",
        "- 正式图片唯一生成入口是 potato-illustrations",
        "- 中文标题、要点、收束句由本地脚本叠字，不让模型直接写字",
        "",
        "## 配图清单",
        "",
    ]
    for idx, section in enumerate(article.sections, start=2):
        prompt_name = body_prompt_filename(idx, section.heading)
        image_name = body_image_name(idx, section.heading)
        lines.extend(
            [
                f"### 图 {idx:02d}",
                f"- 对应标题：{section.heading}",
                f"- 文件：images/{image_name}",
                f"- Prompt：prompts/{prompt_name}",
                f"- 作用：解释“{section.heading}”这一节的核心判断",
                f"- 图上主文案：{section.heading}",
                f"- 图上要点：{section.cue}",
                "- 审核要点：文字必须排在空白处，不能压住主体、关键道具和路径结构",
                "",
            ]
        )
    return "\n".join(lines)


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
        lines.append(f"- 三级提示 {index}：{section.cue}")
    lines.extend(
        [
            "",
            "## 配图映射",
            "",
            "### 图 01 封面",
            "- 文件：images/01_公众号封面_标题版_2.35比1.png",
            "- 用途：封面",
            "- 不进入正文",
            "",
        ]
    )
    for index, section in enumerate(article.sections, start=2):
        paragraph_pos = max(len(section.paragraphs), 1)
        lines.extend(
            [
                f"### 图 {index:02d} 正文图",
                f"- 文件：images/{body_image_name(index, section.heading)}",
                f"- 插在：{section.heading} 下，第 {paragraph_pos} 段后",
                f"- 作用：解释“{section.cue}”这个判断",
                "",
            ]
        )
    return "\n".join(lines)


def build_review_record(article: Article) -> str:
    lines = [
        "# 审核记录",
        "",
        "## 结论",
        "",
        "静态通过，待正式出图。",
        "",
        "## 检查项",
        "",
        "| 项目 | 结果 | 说明 |",
        "|---|---|---|",
        "| 文案结构 | 通过 | 已拆成标题、摘要、正文、结尾 CTA |",
        "| 标题 | 通过 | 标题保留原判断，适合公众号 |",
        "| 封面方案 | 通过 | 已明确本地叠字和安全区要求 |",
        "| 配图方案 | 通过 | 每一节都绑定单独 prompt |",
        "| 图片来源唯一性 | 待出图 | 正式图片必须由 potato-illustrations 生成 |",
        "| 角色一致性 | 待出图 | 出图后检查土豆崽统一性 |",
        "| 草稿箱兼容性 | 通过 | 目录和映射文件齐全 |",
        "",
        "## 返工条件",
        "",
        "- 如果 images/ 中不是 potato-illustrations 正式成图，直接打回",
        "- 如果文字叠加压住主体、手、关键道具或路径结构，直接打回",
        "- 如果封面缺少 2.35:1 标题版主封面，直接打回",
        "",
    ]
    return "\n".join(lines)


def build_metadata(article: Article) -> dict:
    body_paths = [
        f"images/{body_image_name(index, section.heading)}"
        for index, section in enumerate(article.sections, start=2)
    ]
    return {
        "platform": "wechat",
        "title": article.title,
        "digest": article.digest,
        "source_article": article.source_path.relative_to(ROOT).as_posix(),
        "cover_path": "images/01_公众号封面_标题版_2.35比1.png",
        "body_image_paths": body_paths,
        "status": "draft-ready",
        "theme": THEME,
        "cover_hook": article.cover_title,
        "cover_kicker": article.cover_subtitle,
    }


def build_cover_prompt(article: Article) -> str:
    return "\n".join(
        [
            "# 公众号封面 Prompt",
            "",
            f"- 封面主标题：{article.cover_title}",
            f"- 封面副标题：{article.cover_subtitle}",
            f"- 点击理由：{article.cover_reason}",
            f"- 主视觉：{article.cover_visual}",
            f"- 土豆崽表情：{article.cover_emotion}",
            f"- 土豆崽动作：{article.cover_action}",
            f"- 道具元素：{article.cover_props}",
            f"- 构图要求：{article.cover_composition}",
            "",
        ]
    )


def section_bullets(section: Section) -> list[str]:
    bullets: list[str] = []
    seen: set[str] = set()
    for paragraph in section.paragraphs[:2]:
        normalized = strip_prompt_noise(paragraph)
        if not normalized:
            continue
        parts = re.split(r"[。！？；;]", normalized)
        for part in parts:
            snippet = strip_prompt_noise(part)
            if len(snippet) < 6:
                continue
            short = snippet[:22].rstrip("，。；：")
            key = re.sub(r"\s+", "", short)
            if key and key not in seen:
                bullets.append(short)
                seen.add(key)
            if len(bullets) >= 3:
                break
        if len(bullets) >= 3:
            break
    cue = strip_prompt_noise(section.cue)
    if cue:
        cue_key = re.sub(r"\s+", "", cue[:22])
        if cue_key not in seen:
            bullets.append(cue[:22].rstrip("，。；："))
    if not bullets:
        bullets.append("先把这件事理顺")
    return bullets[:3]


def infer_structure_type(section: Section) -> str:
    heading = section.heading
    if any(token in heading for token in ["为什么", "不是", "问题"]):
        return "认知纠偏型"
    if any(token in heading for token in ["步骤", "框架", "系统"]):
        return "结构拆解型"
    if any(token in heading for token in ["AI", "工具", "方法"]):
        return "判断对比型"
    return "核心判断型"


def infer_action(section: Section) -> str:
    heading = section.heading
    if "选题" in heading:
        return "把零散选题卡片重新分类并贴回标签墙"
    if "系统" in heading:
        return "把散乱模块重新拼回一条稳定结构"
    if "AI" in heading:
        return "站在岔路口前，把错误方向转回正轨"
    if "工作流" in heading:
        return "把散乱步骤卡拉回同一条主轨道"
    return "把混乱信息重新整理成一条能复用的路线"


def infer_props(section: Section) -> str:
    heading = section.heading
    props = ["箭头路径", "步骤卡片"]
    if "选题" in heading:
        props.append("标签墙")
    if "系统" in heading:
        props.append("结构模块")
    if "AI" in heading:
        props.append("岔路标识")
    if "工作流" in heading:
        props.append("轨道")
    return "、".join(dict.fromkeys(props))


def infer_notes(section: Section) -> str:
    return "｜".join(section_bullets(section))


def infer_composition(section: Section) -> str:
    heading = section.heading
    if "AI" in heading:
        return "主体放中下部，左右形成明确对比，上方或侧上方留出完整信息安全区。"
    if "选题" in heading or "系统" in heading:
        return "主体偏中部，旁边要有能看懂结构变化的图形关系，留白区必须足够放信息面板。"
    return "主体放中下部，画面有清晰主次和动线，必须给后期叠字留出干净空白区。"


def build_body_prompt(article: Article, index: int, section: Section) -> str:
    bullets = section_bullets(section)
    summary = strip_prompt_noise(section.cue)
    title = strip_prompt_noise(section.heading)
    core = strip_prompt_noise(section.paragraphs[0]) if section.paragraphs else summary
    return "\n".join(
        [
            "# 正文配图 Prompt",
            "",
            f"- 页面标题：{title}",
            f"- 输出文件名：{body_image_name(index, section.heading)}",
            f"- 主文案：{title}",
            f"- 核心提炼：{'｜'.join(bullets)}",
            f"- 收束句：{summary}",
            f"- 核心判断：{core[:32]}",
            f"- 结构类型：{infer_structure_type(section)}",
            f"- 土豆崽动作：{infer_action(section)}",
            f"- 道具元素：{infer_props(section)}",
            f"- 短标注：{infer_notes(section)}",
            f"- 构图要求：{infer_composition(section)}",
            "",
        ]
    )


def write_prompts(article: Article, prompt_dir: Path) -> None:
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "01_公众号封面.md").write_text(build_cover_prompt(article), encoding="utf-8")
    for index, section in enumerate(article.sections, start=2):
        (prompt_dir / body_prompt_filename(index, section.heading)).write_text(
            build_body_prompt(article, index, section),
            encoding="utf-8",
        )


def write_article(article: Article, overwrite: bool) -> Path:
    date_dir = WECHAT_ROOT / article.date_folder
    package_dir = date_dir / f"{article.date_key}_公众号_{article.folder_slug}"
    if package_dir.exists() and not overwrite:
        return package_dir

    date_dir.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "images").mkdir(parents=True, exist_ok=True)
    write_prompts(article, package_dir / "prompts")

    (package_dir / "发布稿.md").write_text(build_publish_md(article), encoding="utf-8")
    (package_dir / "草稿箱正文.txt").write_text(build_draft_body(article), encoding="utf-8")
    (package_dir / "配图方案.md").write_text(build_image_plan(article), encoding="utf-8")
    (package_dir / "封面方案.md").write_text(build_cover_plan(article), encoding="utf-8")
    (package_dir / "正文结构与配图映射.md").write_text(build_mapping(article), encoding="utf-8")
    (package_dir / "审核记录.md").write_text(build_review_record(article), encoding="utf-8")
    (package_dir / "metadata.json").write_text(
        json.dumps(build_metadata(article), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return package_dir


def find_source_markdown(date_dir: Path) -> Path:
    candidates = sorted(
        [
            path for path in date_dir.glob("202607*_文章总览_*.md")
            if "_写作说明" not in path.name and "_选题结论" not in path.name
        ]
    )
    if len(candidates) != 1:
        raise ValueError(f"日期目录下母稿数量异常: {date_dir}")
    return candidates[0]


def iter_dates(date_from: str | None, date_to: str | None) -> list[Path]:
    date_dirs = [path for path in sorted(OVERVIEW_ROOT.iterdir()) if path.is_dir() and DATE_RE.match(path.name)]
    if date_from:
        date_dirs = [path for path in date_dirs if path.name >= date_from]
    if date_to:
        date_dirs = [path for path in date_dirs if path.name <= date_to]
    return date_dirs


def main() -> int:
    parser = argparse.ArgumentParser(description="把文章总览母稿转换为合规公众号发布包，不直接生成正式图片。")
    parser.add_argument("--date-from", help="开始日期，格式 2026-07-03")
    parser.add_argument("--date-to", help="结束日期，格式 2026-07-14")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的发布包")
    args = parser.parse_args()

    created: list[str] = []
    for date_dir in iter_dates(args.date_from, args.date_to):
        source = find_source_markdown(date_dir)
        article = parse_article(source)
        package = write_article(article, overwrite=args.overwrite)
        created.append(str(package))

    MANIFEST_PATH.write_text(json.dumps(created, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(created), "manifest": str(MANIFEST_PATH), "packages": created}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
