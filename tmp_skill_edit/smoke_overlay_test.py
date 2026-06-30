from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location("wechat_overlay", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块: {module_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    module_path = Path(__file__).with_name("generate_wechat_images.py")
    mod = load_module(module_path)

    raw_dir = Path(
        r"C:\Users\adv\Desktop\codex_project\social_media\06_运营中心\2026\2026-07\公众号\2026-07-02\20260702_公众号_普通人第一条最值得先搭的不是自动化工作流而是内容工作流\images\_potato_raw"
    )
    out_dir = Path(__file__).with_name("smoke_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    raw04 = sorted(raw_dir.glob("*一条最小内容工作流先把五步跑顺*.png"))[-1]
    raw05 = sorted(raw_dir.glob("*AI适合接动作不适合替你做核心判断*.png"))[-1]
    raw06 = sorted(raw_dir.glob("*第一条工作流的目标不是炫技而是稳定复用*.png"))[-1]
    raw_cover = sorted(raw_dir.glob("*cover*.png"))[-1]

    img04 = out_dir / "04_overlay_test.png"
    img05 = out_dir / "05_overlay_test.png"
    img06 = out_dir / "06_overlay_test.png"
    cover = out_dir / "01_cover_overlay_test.png"

    mod.normalize_image(raw04, (mod.BODY_W, mod.BODY_H), img04, (0.52, 0.5))
    mod.overlay_body(img04, img04, "一条最小内容工作流，先把五步跑顺", ["选题", "提纲", "初稿", "改写", "发布"], "先跑顺五步，比收藏一堆提示词更重要。")

    mod.normalize_image(raw05, (mod.BODY_W, mod.BODY_H), img05, (0.52, 0.5))
    mod.overlay_body(img05, img05, "AI 适合接动作，不适合替你做核心判断", ["扩展整理可以给 AI", "核心判断要自己留住", "别把方向也一起外包"], "动作能交，判断别丢。")

    mod.normalize_image(raw06, (mod.BODY_W, mod.BODY_H), img06, (0.52, 0.5))
    mod.overlay_body(img06, img06, "第一条工作流的目标，不是炫技，而是稳定复用", ["别追花哨", "先能反复跑", "下周还用得上"], "能复用，才叫真正的工作流。")

    mod.normalize_image(raw_cover, (mod.COVER_W, mod.COVER_H), cover, (0.54, 0.5))
    mod.overlay_cover(cover, cover, "先别急着做自动化", "普通人更该先把内容工作流跑顺")

    print(img04)
    print(img05)
    print(img06)
    print(cover)


if __name__ == "__main__":
    main()
