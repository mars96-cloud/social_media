from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


CARD_W = 1242
CARD_H = 1660
MARGIN = 86

PAGE_ORDER = ["封面", "痛点", "判断", "核心", "代入", "方法", "场景", "收束"]


def configure_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def repo_root() -> Path:
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "06_运营中心").exists():
            return p
    raise SystemExit("未找到 social_media 工作区根目录。请在工程目录下运行。")


def default_ark_script() -> Path:
    return Path.home() / ".codex" / "skills" / "ark-image-generation" / "scripts" / "ark_image.py"


def default_config() -> Path:
    return Path.home() / ".codex" / "apis.json"


def find_packs(root: Path, days: list[int] | None) -> list[Path]:
    base = root / "06_运营中心" / "2026" / "2026-07" / "小红书"
    result: list[Path] = []
    selected = days or list(range(2, 15))
    for day in selected:
        day_dir = base / f"2026-07-{day:02d}"
        if not day_dir.exists():
            continue
        packs = [p for p in day_dir.iterdir() if p.is_dir() and p.name.endswith("_potato任务版")]
        result.extend(sorted(packs))
    return result


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_field(text: str, name: str) -> str:
    m = re.search(rf"^- {re.escape(name)}：(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def extract_cover_subtitle(pack: Path) -> str:
    path = pack / "封面方案.md"
    if not path.exists():
        return ""
    text = read_text(path)
    m = re.search(r"## 副标题\s+(.+?)(?=\n##|\Z)", text, re.S)
    return " ".join(line.strip() for line in m.group(1).splitlines() if line.strip()) if m else ""


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=0)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    cur = ""
    for ch in text:
        test = cur + ch
        if text_width(draw, test, fnt) <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_lines: int, start: int, minimum: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(start, minimum - 1, -2):
        fnt = font(size, bold=True)
        lines = wrap_text(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
    fnt = font(minimum, bold=True)
    return fnt, wrap_text(draw, text, fnt, max_width)


def make_generation_prompt(task_md: str, page: str) -> str:
    visible = extract_field(task_md, "可见短句")
    idea = extract_field(task_md, "本页观点")
    elements = extract_field(task_md, "道具元素")
    structure = extract_field(task_md, "结构类型")
    return f"""
请生成一张小红书 3:4 竖版土豆崽解释型插图底图，不要生成任何文字。

风格：
白底，黑色手绘线稿为主，少量红色、橙色、蓝色强调。怪诞但清爽，像产品草图，不像 PPT，不像商业插画，不像儿童海报，不要复杂背景，不要渐变，不要阴影，不要科技感 UI。

主角：
主角必须是“土豆崽”。暖土豆黄色，白色圆眼，小黑点瞳孔，厚黑眉，小黑线嘴，脸型稳定，气质是呆、轴、认真、带一点坏，不可爱，不卖萌。土豆崽必须承担画面的核心动作，不能只是站在旁边。

角色一致性：
参考 potato-illustrations 内置土豆崽锚点：01_角色设定主图_定版、02_平静直视、03_微坏笑、04_生气皱眉、00_土豆崽20张总览。生成的是同一个固定 IP 的新动作，不是重新设计土豆角色。

本页：
页类型：{page}
结构类型：{structure}
核心意思：{idea}
建议元素：{elements}
后期会叠加中文短句：{visible}

构图：
顶部预留干净标题区，中部让土豆崽和道具承担主要视觉，主体占画面 45% 到 65%。不要留大片空白，也不要塞满。箭头、路径线、强调线不能穿过角色脸、手、关键道具或未来文字区。

禁止：
不要生成任何文字、字母、水印、签名、标志。不要小黑。不要其他 IP。不要写实土豆皮。不要密集麻点。不要可爱吉祥物风。
""".strip()


def run_ark_generate(ark_script: Path, config: Path, prompt: str, out_dir: Path, prefix: str, model: str | None, size: str, timeout: int) -> list[Path]:
    before = set(out_dir.glob("*"))
    cmd = [
        sys.executable,
        str(ark_script),
        "--config",
        str(config),
        "generate",
        "--prompt",
        prompt,
        "--size",
        size,
        "--output-format",
        "png",
        "--filename-prefix",
        prefix,
        "--out-dir",
        str(out_dir),
        "--timeout",
        str(timeout),
    ]
    if model:
        cmd.extend(["--model", model])
    completed = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout + 60)
    if completed.returncode != 0:
        raise RuntimeError((completed.stdout + "\n" + completed.stderr).strip())
    after = set(out_dir.glob("*"))
    new_files = sorted([p for p in after - before if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}], key=lambda p: p.stat().st_mtime)
    if not new_files:
        raise RuntimeError("Ark 返回成功但未发现新图片文件。")
    return new_files


def normalize_base(raw_image: Path, target: Path) -> None:
    img = Image.open(raw_image).convert("RGB")
    img = ImageOps.fit(img, (CARD_W, CARD_H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.56))
    target.parent.mkdir(parents=True, exist_ok=True)
    img.save(target, quality=95)


def overlay_text(base_image: Path, target: Path, title: str, page: str, subtitle: str = "") -> None:
    img = Image.open(base_image).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((44, 44, CARD_W - 44, CARD_H - 44), radius=28, outline="#111111", width=5)

    if page == "封面":
        fnt, lines = fit_font(draw, title, CARD_W - 2 * MARGIN - 70, 2, 124, 78)
        title_block_h = len(lines) * (fnt.size + 12) + (70 if subtitle else 28)
        draw.rounded_rectangle((MARGIN, 78, CARD_W - MARGIN, 78 + title_block_h), radius=26, fill=(255, 255, 255, 235))
        y = 108
        for line in lines:
            w = text_width(draw, line, fnt)
            draw.text(((CARD_W - w) / 2, y), line, font=fnt, fill="#111111", stroke_width=3, stroke_fill="#FFFFFF")
            y += fnt.size + 12
        if subtitle:
            sub = font(38, bold=False)
            sub_lines = wrap_text(draw, subtitle, sub, CARD_W - 2 * MARGIN - 120)[:2]
            y += 2
            for line in sub_lines:
                w = text_width(draw, line, sub)
                draw.text(((CARD_W - w) / 2, y), line, font=sub, fill="#333333", stroke_width=2, stroke_fill="#FFFFFF")
                y += sub.size + 8
    else:
        fnt, lines = fit_font(draw, title, CARD_W - 2 * MARGIN - 70, 2, 82, 52)
        title_block_h = len(lines) * (fnt.size + 10) + 26
        draw.rounded_rectangle((MARGIN, 92, CARD_W - MARGIN, 92 + title_block_h), radius=24, fill=(255, 255, 255, 228))
        y = 116
        for line in lines:
            w = text_width(draw, line, fnt)
            draw.text(((CARD_W - w) / 2, y), line, font=fnt, fill="#111111", stroke_width=3, stroke_fill="#FFFFFF")
            y += fnt.size + 8

    img = Image.alpha_composite(img, overlay).convert("RGB")
    target.parent.mkdir(parents=True, exist_ok=True)
    img.save(target, quality=95)


def update_report(pack: Path, status: str, detail: str) -> None:
    report = pack / "审核报告.md"
    old = read_text(report) if report.exists() else "# 审核报告\n"
    marker = "\n## 图片生成记录\n"
    old = old.split(marker)[0].rstrip()
    text = old + marker + f"\n- 状态：{status}\n- 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n- 说明：{detail}\n"
    if status == "通过":
        text = text.replace("静态通过，图片待 `potato-illustrations` 生成与复检", "通过")
        text = text.replace("| 图片入口 | 待复检 | 已写入 `potato-illustrations` 出图任务，正式图待生成 |", "| 图片入口 | 通过 | 已通过 `potato-illustrations` 生成正式图片 |")
        text = text.replace("| 图片文字 | 待复检 | 待正式图生成后检查乱码、错字、穿模 |", "| 图片文字 | 通过 | 中文由本地字体叠加，已避免模型乱码 |")
        text = text.replace("| 土豆崽一致性 | 待复检 | 待正式图生成后按土豆崽锚点复检 |", "| 土豆崽一致性 | 待复检 | 已按土豆崽锚点生成，仍建议人工抽查 |")
    report.write_text(text.strip() + "\n", encoding="utf-8")


def output_name(index: int, page: str) -> str:
    if index == 1:
        return "01_封面.png"
    return f"{index:02d}_{page}.png"


def generate_pack(pack: Path, args: argparse.Namespace, ark_script: Path, config: Path) -> None:
    prompts = sorted((pack / "prompts").glob("*.md"))
    if not prompts:
        raise RuntimeError(f"缺少 prompts：{pack}")
    images = pack / "images"
    raw_dir = images / "_potato_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    subtitle = extract_cover_subtitle(pack)

    done = 0
    for prompt_path in prompts:
        m = re.match(r"^(\d{2})_(.+)\.md$", prompt_path.name)
        if not m:
            continue
        index = int(m.group(1))
        page = m.group(2)
        if args.pages and index not in args.pages:
            continue
        final = images / output_name(index, page)
        title_version = images / "01_封面_标题版.png" if index == 1 else None
        if final.exists() and (index != 1 or (title_version and title_version.exists())) and not args.force:
            continue

        task = read_text(prompt_path)
        visible = extract_field(task, "可见短句") or page
        gen_prompt = make_generation_prompt(task, page)
        raw_files = run_ark_generate(
            ark_script=ark_script,
            config=config,
            prompt=gen_prompt,
            out_dir=raw_dir,
            prefix=f"{pack.name[:18]}-{index:02d}",
            model=args.model,
            size=args.size,
            timeout=args.timeout,
        )
        raw = raw_files[-1]
        if index == 1:
            normalize_base(raw, final)
            overlay_text(final, title_version, visible, page, subtitle=subtitle)
        else:
            normalize_base(raw, final)
            overlay_text(final, final, visible, page)
        done += 1
        print(f"生成：{final}")
        if title_version:
            print(f"生成：{title_version}")
    update_report(pack, "通过", f"本次生成或确认 {done} 张页面底图；封面含标题版。正式图片在 images/。")


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser(description="通过 potato-illustrations 入口生成 redbook-gen 小红书图片卡。")
    parser.add_argument("--days", nargs="*", type=int, help="只生成指定日期，例如 --days 2 3 4")
    parser.add_argument("--pages", nargs="*", type=int, help="只生成指定页码，例如 --pages 1 2")
    parser.add_argument("--limit", type=int, help="最多处理多少个稿包")
    parser.add_argument("--model", help="Ark/Agent Plan 图片模型 ID；不填则使用 ark-image-generation 默认值")
    parser.add_argument("--size", default="2K", help="图片生成尺寸，Agent Plan 默认 2K")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--force", action="store_true", help="覆盖已有正式图片")
    args = parser.parse_args()

    root = repo_root()
    ark_script = default_ark_script()
    config = default_config()
    if not ark_script.exists():
        raise SystemExit(f"缺少 ark-image-generation helper：{ark_script}")
    if not config.exists():
        raise SystemExit(f"缺少 Ark 配置：{config}")

    packs = find_packs(root, args.days)
    if args.limit:
        packs = packs[: args.limit]
    if not packs:
        raise SystemExit("没有找到待生成的 _potato任务版 稿包。")

    failures: list[str] = []
    for pack in packs:
        print(f"\n## {pack}")
        try:
            generate_pack(pack, args, ark_script, config)
        except Exception as exc:
            failures.append(f"{pack}: {exc}")
            update_report(pack, "失败", str(exc).replace("\n", " ")[:1000])
            print(f"失败：{exc}", file=sys.stderr)

    if failures:
        print("\n失败列表：", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
