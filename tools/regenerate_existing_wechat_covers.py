from __future__ import annotations

import json
import subprocess
from pathlib import Path

from render_social_assets import render_wechat_cover


ROOT = Path(__file__).resolve().parents[1]
ARK_SCRIPT = Path.home() / ".codex" / "skills" / "ark-image-generation" / "scripts" / "ark_image.py"
APIS_CONFIG = Path.home() / ".codex" / "apis.json"


def article(
    month: str,
    folder: str,
    hook: str,
    kicker: str,
    theme: str,
    variant: str,
    prompt: str,
) -> dict[str, str]:
    return {
        "month": month,
        "folder": folder,
        "hook": hook,
        "kicker": kicker,
        "theme": theme,
        "variant": variant,
        "prompt": prompt,
    }


ARTICLES = [
    article("2026-06", "20260621_公众号_普通人做AI先别追新工具先搭第一条工作流", "先搭系统", "别先追新工具", "warm-paper", "warning-bar", "Chinese social-media cover background, exaggerated contrast between chaotic tool icons and one clear workflow path, cinematic warm paper and orange palette, strong focal object, bold light and shadow, high click-through energy, no text, no watermark."),
    article("2026-06", "20260622_公众号_别再只学AI工具了普通人真正该先搭的是3条AI工作流", "先别乱学", "真正该搭流程", "blueprint", "burst-left", "Chinese social-media cover background, three glowing workflow lanes cutting through a messy sea of floating AI app icons, bright blue tech style, dynamic perspective, punchy and dramatic, no text, no watermark."),
    article("2026-06", "20260623_公众号_为什么你用了很多AI还是没有真正提效", "提效没来", "问题不在工具", "newsroom", "dark-card", "Chinese social-media cover background, overwhelmed creator at desk with many AI windows but tangled cables and clocks, one bright efficiency path missing, cinematic newsroom mood, dramatic, no text, no watermark."),
    article("2026-06", "20260624_公众号_内容创作者最值得先学的1条AI图文生产流程", "先跑图文流", "这条最值得学", "mint-grid", "spotlight-right", "Chinese social-media cover background, creator workflow with phone screen, article card, image card connected into one clear production line, fresh mint palette, sharp focal object, high-contrast, no text, no watermark."),
    article("2026-06", "20260625_公众号_做AI自媒体前先想清楚这4件事", "先想清楚", "别急着开号", "studio-pop", "diagonal-pop", "Chinese social-media cover background, four oversized decision cards floating above a creator desk, dramatic orange highlights, suspenseful planning mood, strong composition, no text, no watermark."),
    article("2026-06", "20260626_公众号_公众号小红书朋友圈哪些环节最适合交给AI", "别全交AI", "只放大这几步", "slate-pro", "burst-left", "Chinese social-media cover background, three platform panels and several workflow steps, some glowing as delegated to AI and some locked as human judgment, sleek teal editorial style, strong visual hierarchy, no text, no watermark."),
    article("2026-06", "20260627_公众号_普通人做AI内容最容易浪费时间的5个坑", "这5个坑", "最耗时间", "warm-paper", "dark-card", "Chinese social-media cover background, five warning pits or traps on a content production path, exaggerated hazard visuals, dramatic shadows, eye-catching warm palette, no text, no watermark."),
    article("2026-06", "20260628_公众号_AI写作为什么总有味儿很重问题通常不在工具", "人味不见了", "锅不在工具", "newsroom", "warning-bar", "Chinese social-media cover background, stiff robotic manuscript versus lively handwritten notes, expressive contrast, a creator pulling one sheet away, dramatic editorial mood, no text, no watermark."),
    article("2026-06", "20260629_公众号_从AI提效到AI变现普通人更现实的一条路", "先提效再变现", "这条更现实", "studio-pop", "spotlight-right", "Chinese social-media cover background, clear rising path from laptop productivity to simple monetization milestones, one realistic path instead of luxury fantasy, bright orange pop style, no text, no watermark."),
    article("2026-06", "20260630_公众号_最适合新手切入的3种AI轻变现方向", "新手看这3种", "轻变现更现实", "blueprint", "diagonal-pop", "Chinese social-media cover background, three beginner-friendly monetization lanes with simple icons and strong perspective, bright clean blue palette, exciting but not luxury, no text, no watermark."),
    article("2026-07", "20260701_公众号_别把AI当外挂普通人更该先有自己的内容中台", "先有中台", "别把AI当外挂", "warm-paper", "warning-bar", "Chinese social-media cover background, a creator standing before a central content command center while random AI tools float outside, exaggerated contrast, warm editorial palette, strong focal subject, no text, no watermark."),
    article("2026-07", "20260702_公众号_为什么你的选题总在重复其实缺的是一套AI选题系统", "题总重复", "你缺的是系统", "blueprint", "burst-left", "Chinese social-media cover background, repeated identical topic cards spinning in chaos while one organized topic system board glows, bright blue strategic mood, curiosity-driven, no text, no watermark."),
    article("2026-07", "20260703_公众号_评论区不是反馈区而是你最便宜的需求池", "评论最值钱", "别只看点赞", "newsroom", "dark-card", "Chinese social-media cover background, comment bubbles turning into gold demand cards, creator catching them with a net, dramatic newsroom energy, no text, no watermark."),
    article("2026-07", "20260704_公众号_把AI用进客户沟通普通个体最容易忽略的3个环节", "沟通别急回", "先整理需求", "mint-grid", "spotlight-right", "Chinese social-media cover background, client chat windows, sticky notes, and a clean demand map replacing chaotic replies, fresh green palette, high-contrast and practical, no text, no watermark."),
    article("2026-07", "20260705_公众号_别急着做智能体先把这4个手动步骤跑顺", "别急做智能体", "先跑顺4步", "studio-pop", "warning-bar", "Chinese social-media cover background, four manual steps lit on a path before a giant robot gate, exaggerated suspense and orange highlights, no text, no watermark."),
    article("2026-07", "20260706_公众号_一个人做内容最该先沉淀的不是提示词而是可复用素材库", "先存素材", "不是先堆提示词", "slate-pro", "burst-left", "Chinese social-media cover background, reusable asset library shelves glowing while scattered prompt papers fly around, teal professional style, strong visual focus, no text, no watermark."),
    article("2026-07", "20260707_公众号_为什么很多人做了工作流还是不稳定问题出在复盘层", "问题在复盘", "流程不稳的根源", "newsroom", "diagonal-pop", "Chinese social-media cover background, unstable workflow machine wobbling until a review layer locks it in place, dramatic tension, editorial red-orange accents, no text, no watermark."),
    article("2026-07", "20260708_公众号_从爆款焦虑到稳定输出普通创作者更需要周更系统", "别赌爆款", "先做周更系统", "mint-grid", "spotlight-right", "Chinese social-media cover background, anxious creator surrounded by exploding trending arrows versus a calm weekly system board, fresh green style, strong emotional contrast, no text, no watermark."),
    article("2026-07", "20260709_公众号_AI不是帮你偷懒而是帮你放大判断对的人会这样用", "别拿来偷懒", "要拿来放大判断", "newsroom", "dark-card", "Chinese social-media cover background, magnifying lens amplifying a creator's judgment notes while lazy shortcuts fade away, dramatic and punchy, no text, no watermark."),
    article("2026-07", "20260710_公众号_如果你想开始做智能体先从这条半自动工作流起步", "先做半自动", "第一条就做这个", "slate-pro", "burst-left", "Chinese social-media cover background, semi-automatic workflow console with one human hand and one glowing AI assist hand, clear first-step feeling, sleek teal style, dramatic, no text, no watermark."),
]


def run_ark(prompt: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = set(out_dir.glob("ark-cover-*.png"))
    command = [
        "python",
        str(ARK_SCRIPT),
        "--config",
        str(APIS_CONFIG),
        "generate",
        "--prompt",
        prompt,
        "--size",
        "1536x1024",
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


def title_from_metadata(article_dir: Path) -> str:
    metadata_path = article_dir / "metadata.json"
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    return data["title"]


def update_metadata(article_dir: Path, spec: dict[str, str]) -> None:
    metadata_path = article_dir / "metadata.json"
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    data["theme"] = spec["theme"]
    data["cover_hook"] = spec["hook"]
    data["cover_kicker"] = spec["kicker"]
    data["cover_variant"] = spec["variant"]
    data["cover_prompt"] = spec["prompt"]
    data["cover_image"] = "01_公众号封面.png"
    metadata_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def refresh_article(spec: dict[str, str], skip_ark: bool = False) -> dict[str, str]:
    article_dir = ROOT / "06_运营中心" / "2026" / spec["month"] / "草稿区" / spec["folder"]
    image_dir = article_dir / "images"
    title = title_from_metadata(article_dir)
    base_path = image_dir / "wechat_cover_base.png"
    ark_status = "skipped"
    if not skip_ark:
        try:
            generated = run_ark(spec["prompt"], image_dir)
            if generated.resolve() != base_path.resolve():
                if base_path.exists():
                    base_path.unlink()
                generated.replace(base_path)
            ark_status = "generated"
        except Exception:
            ark_status = "fallback-existing-base" if base_path.exists() else "fallback-theme-base"
    else:
        ark_status = "fallback-existing-base" if base_path.exists() else "fallback-theme-base"

    render_wechat_cover(
        image_dir / "01_公众号封面.png",
        base_path if base_path.exists() else None,
        title,
        "关注我，后续日常推送与直播带你手把手开发自己的工作流与智能体",
        theme=spec["theme"],
        hook=spec["hook"],
        kicker=spec["kicker"],
        variant=spec["variant"],
    )
    update_metadata(article_dir, spec)
    return {
        "article_dir": str(article_dir),
        "cover": str(image_dir / "01_公众号封面.png"),
        "base": str(base_path),
        "hook": spec["hook"],
        "variant": spec["variant"],
        "ark_status": ark_status,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-ark", action="store_true")
    args = parser.parse_args()

    outputs = [refresh_article(spec, skip_ark=args.skip_ark) for spec in ARTICLES]
    print(json.dumps(outputs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
