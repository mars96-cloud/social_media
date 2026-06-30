from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location("potato_wechat_images", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"无法加载模块: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="只生成指定公众号 prompt 的 potato 图片。")
    parser.add_argument("--pack", required=True, help="公众号稿包目录")
    parser.add_argument("--prompts", nargs="+", required=True, help="要生成的 prompt 文件名")
    parser.add_argument("--model", default="doubao-seedream-5.0-lite")
    parser.add_argument("--size", default="2K")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    module_path = Path.home() / ".codex" / "skills" / "potato-illustrations" / "scripts" / "generate_wechat_images.py"
    mod = load_module(module_path)

    pack = Path(args.pack).resolve()
    prompts_dir = pack / "prompts"
    images_dir = pack / "images"
    raw_dir = images_dir / "_potato_raw"
    images_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    ark_script = mod.default_ark_script()
    config = mod.default_config()
    if config is None:
        raise SystemExit("缺少 .codex/apis.json")

    generated: list[str] = []
    for prompt_name in args.prompts:
        prompt_path = prompts_dir / prompt_name
        if not prompt_path.exists():
            raise SystemExit(f"缺少 prompt: {prompt_path}")

        text = mod.read_text(prompt_path)
        if prompt_name.startswith("01_公众号封面"):
            title = mod.extract_field(text, "封面主标题")
            subtitle = mod.extract_field(text, "封面副标题")
            final_235 = images_dir / "01_公众号封面_标题版_2.35比1.png"
            final_11 = images_dir / "01_公众号封面_标题版_1比1.png"
            if (final_235.exists() and final_11.exists()) and not args.force:
                continue
            prompt_235 = mod.build_cover_prompt(text, "2.35:1")
            prompt_11 = mod.build_cover_prompt(text, "1:1")
            raw_235 = mod.run_ark_generate(ark_script, config, prompt_235, raw_dir, f"{pack.name[:18]}-cover235", args.model, args.size, args.timeout)
            raw_11 = mod.run_ark_generate(ark_script, config, prompt_11, raw_dir, f"{pack.name[:18]}-cover11", args.model, args.size, args.timeout)
            base_235 = images_dir / "01_公众号封面_底图_2.35比1.png"
            base_11 = images_dir / "01_公众号封面_底图_1比1.png"
            mod.normalize_image(raw_235, (mod.COVER_W, mod.COVER_H), base_235, (0.54, 0.5))
            mod.normalize_image(raw_11, (mod.SQUARE, mod.SQUARE), base_11, (0.5, 0.5))
            mod.overlay_cover(base_235, final_235, title, subtitle)
            mod.overlay_cover(base_11, final_11, title, subtitle)
            generated.extend([str(base_235.relative_to(pack)), str(base_11.relative_to(pack)), str(final_235.relative_to(pack)), str(final_11.relative_to(pack))])
            print(f"生成: {final_235}")
            print(f"生成: {final_11}")
            continue

        page_title = mod.extract_field(text, "页面标题")
        title = mod.extract_field(text, "主文案") or page_title
        bullets = [item.strip() for item in mod.extract_field(text, "核心提炼").split("｜") if item.strip()]
        summary = mod.extract_field(text, "收束句")
        file_name = mod.extract_field(text, "输出文件名")
        final = images_dir / file_name
        if final.exists() and not args.force:
            continue
        prompt = mod.build_body_prompt(text)
        raw = mod.run_ark_generate(ark_script, config, prompt, raw_dir, f"{pack.name[:18]}-{mod.slug(page_title)}", args.model, args.size, args.timeout)
        mod.normalize_image(raw, (mod.BODY_W, mod.BODY_H), final, (0.52, 0.5))
        mod.overlay_body(final, final, title, bullets, summary)
        generated.append(str(final.relative_to(pack)))
        print(f"生成: {final}")

    if generated:
        mod.update_audit(pack, "按指定 prompt 补跑正式图片并完成本地叠字。", generated)


if __name__ == "__main__":
    main()
