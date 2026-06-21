from __future__ import annotations

import json
import subprocess
from pathlib import Path

from render_social_assets import render_wechat_cover


ROOT = Path(__file__).resolve().parents[1]
MONTH_DIR = ROOT / "06_运营中心" / "2026" / "2026-06"
DRAFT_DIR = MONTH_DIR / "草稿区"
ARK_SCRIPT = Path.home() / ".codex" / "skills" / "ark-image-generation" / "scripts" / "ark_image.py"


ARTICLES = [
    {
        "folder": "20260621_公众号_普通人做AI先别追新工具先搭第一条工作流",
        "title": "普通人做 AI，不要先追新工具，先搭自己的第一条工作流",
        "subtitle": "回复 流程 领取《普通人最值得先搭的 5 条 AI 工作流》清单",
        "prompt": "Minimal editorial cover background for a Chinese AI workflow article, warm off-white paper texture, deep green and muted orange palette, soft geometric path motif, workflow nodes connected by thin lines, calm professional flat illustration, clean composition, lots of negative space, no readable text, no people, no watermark.",
    },
    {
        "folder": "20260622_公众号_别再只学AI工具了普通人真正该先搭的是3条AI工作流",
        "title": "别再只学 AI 工具了，普通人真正该先搭的是 3 条 AI 工作流",
        "subtitle": "回复 流程 领取《普通人最值得先搭的 5 条 AI 工作流》清单",
        "prompt": "Minimal editorial background for a Chinese article about three AI workflows, warm beige paper texture, dark green and orange accents, three simple structured lanes or cards, abstract workflow blocks, calm professional infographic mood, clean premium design, lots of negative space, no text, no watermark.",
    },
    {
        "folder": "20260623_公众号_为什么你用了很多AI还是没有真正提效",
        "title": "为什么你用了很多 AI，还是没有真正提效",
        "subtitle": "回复 SOP 领取《AI 内容提效 SOP 检查清单》",
        "prompt": "Editorial cover background for an article about why AI did not improve efficiency, warm ivory background, deep green and muted orange, abstract clutter turning into clean flow, before-and-after composition, soft paper grain, minimal flat illustration, lots of empty space, no text, no watermark.",
    },
    {
        "folder": "20260624_公众号_内容创作者最值得先学的1条AI图文生产流程",
        "title": "内容创作者最值得先学的 1 条 AI 图文生产流程",
        "subtitle": "回复 流程 领取《AI 图文生产流程表》",
        "prompt": "Editorial background for a Chinese article about AI content creation workflow, off-white textured background, deep green and muted orange, abstract cards, image frames and content blocks flowing in sequence, clean professional flat design, gentle premium style, no text, no people, no watermark.",
    },
    {
        "folder": "20260625_公众号_做AI自媒体前先想清楚这4件事",
        "title": "做 AI 自媒体前，先想清楚这 4 件事",
        "subtitle": "回复 资料 领取《AI 自媒体起步判断清单》",
        "prompt": "Minimal editorial cover background for a Chinese self-media strategy article, warm cream background, deep green and orange, four abstract thinking cards or checkpoints, subtle decision path graphic, clean flat design, professional and calm, plenty of negative space, no text, no watermark.",
    },
    {
        "folder": "20260626_公众号_公众号小红书朋友圈哪些环节最适合交给AI",
        "title": "公众号、小红书、朋友圈，哪些环节最适合交给 AI",
        "subtitle": "回复 SOP 领取《多平台内容提效检查表》",
        "prompt": "Editorial background for a Chinese article comparing multiple content platforms, warm paper background, deep green and muted orange, three abstract platform panels connected by arrows, clean infographic aesthetic, minimal flat illustration, elegant empty space, no text, no logos, no watermark.",
    },
    {
        "folder": "20260627_公众号_普通人做AI内容最容易浪费时间的5个坑",
        "title": "普通人做 AI 内容，最容易浪费时间的 5 个坑",
        "subtitle": "回复 SOP 领取《AI 内容提效避坑清单》",
        "prompt": "Editorial background for an article about five common AI content mistakes, warm beige textured background, deep green and muted orange, five abstract caution markers or cards, clean flat infographic style, calm premium design, lots of negative space, no readable text, no watermark.",
    },
    {
        "folder": "20260628_公众号_AI写作为什么总有味儿很重问题通常不在工具",
        "title": "AI 写作为什么总有味儿很重？问题通常不在工具",
        "subtitle": "回复 SOP 领取《去机器味写作检查表》",
        "prompt": "Editorial background for a Chinese article about making AI writing sound more human, warm off-white paper texture, deep green and muted orange, abstract document cards with subtle human touch strokes, clean refined flat illustration, lots of negative space, no readable text, no watermark.",
    },
    {
        "folder": "20260629_公众号_从AI提效到AI变现普通人更现实的一条路",
        "title": "从 AI 提效到 AI 变现：普通人更现实的一条路",
        "subtitle": "回复 资料 领取《从提效到变现的 3 段路径图》",
        "prompt": "Editorial background for a Chinese article about the path from AI efficiency to monetization, warm ivory textured background, deep green and muted orange, abstract upward path with three milestone cards, clean professional flat design, premium calm style, no text, no watermark.",
    },
    {
        "folder": "20260630_公众号_最适合新手切入的3种AI轻变现方向",
        "title": "最适合新手切入的 3 种 AI 轻变现方向",
        "subtitle": "回复 资料 领取《AI 轻变现方向对照表》",
        "prompt": "Minimal editorial cover background for a Chinese article about three beginner-friendly AI monetization directions, warm cream paper texture, deep green and orange palette, three abstract lanes or stepping stones, clean infographic mood, flat elegant illustration, lots of negative space, no readable text, no watermark.",
    },
]


def run_ark(prompt: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = set(out_dir.glob("ark-cover-*.png"))
    command = [
        "python",
        str(ARK_SCRIPT),
        "--config",
        str(Path.home() / ".codex" / "apis.json"),
        "generate",
        "--prompt",
        prompt,
        "--size",
        "1024x1024",
        "--out-dir",
        str(out_dir),
        "--filename-prefix",
        "ark-cover",
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(
            "Ark generate failed\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    payload = json.loads(result.stdout)
    saved = payload.get("saved") or []
    if saved:
        return Path(saved[0])
    current = set(out_dir.glob("ark-cover-*.png"))
    created = sorted(current - existing)
    if not created:
        raise RuntimeError(f"No cover base created for {out_dir}")
    return created[0]


def main() -> int:
    outputs = []
    for spec in ARTICLES:
        article_dir = DRAFT_DIR / spec["folder"]
        image_dir = article_dir / "images"
        generated = run_ark(spec["prompt"], image_dir)
        base_path = image_dir / "wechat_cover_base.png"
        if generated.resolve() != base_path.resolve():
            if base_path.exists():
                base_path.unlink()
            generated.replace(base_path)
        render_wechat_cover(image_dir / "01_公众号封面.png", base_path, spec["title"], spec["subtitle"])
        outputs.append({"folder": spec["folder"], "base": str(base_path), "cover": str(image_dir / "01_公众号封面.png")})
    print(json.dumps(outputs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
