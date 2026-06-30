from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


SCRIPT_PATH = Path.home() / ".codex" / "skills" / "potato-illustrations" / "scripts" / "generate_redbook_images.py"


def load_module():
    spec = importlib.util.spec_from_file_location("generate_redbook_images", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_raw(raw_dir: Path, index: int) -> Path:
    matches = sorted(raw_dir.glob(f"*-{index:02d}-*.png"), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise RuntimeError(f"Missing raw image for page {index:02d}: {raw_dir}")
    return matches[-1]


def rerender_pack(pack: Path, module) -> None:
    prompts = sorted((pack / "prompts").glob("*.md"))
    if not prompts:
        raise RuntimeError(f"Missing prompts: {pack}")

    images = pack / "images"
    raw_dir = images / "_potato_raw"
    subtitle = module.extract_cover_subtitle(pack)
    count = 0

    for prompt_path in prompts:
        match = re.match(r"^(\d{2})_(.+)\.md$", prompt_path.name)
        if not match:
            continue
        index = int(match.group(1))
        page = match.group(2)
        task = module.read_text(prompt_path)
        visible = module.extract_field(task, "可见短句") or page
        raw = find_raw(raw_dir, index)
        final = images / module.output_name(index, page)

        if index == 1:
            module.normalize_base(raw, final)
            module.overlay_text(final, images / "01_封面_标题版.png", visible, page, subtitle=subtitle)
        else:
            module.normalize_base(raw, final)
            module.overlay_text(final, final, visible, page)
        count += 1

    module.update_report(pack, "通过", f"本次复用 raw 图重新导出 {count} 张页面；已移除整边框并拉开封面主副标题间距。正式图片在 images/。")
    print(f"rerendered {count}: {pack}")


def discover_packs_from_date(root: Path, from_date: str) -> list[Path]:
    packs: list[Path] = []
    for pack in root.rglob("*potato*"):
        if not pack.is_dir():
            continue
        if not (pack / "prompts").exists():
            continue
        raw_dir = pack / "images" / "_potato_raw"
        if not raw_dir.exists() or not any(raw_dir.glob("*.png")):
            continue
        dates = [part for part in pack.parts if re.fullmatch(r"2026-07-\d{2}", part)]
        if not dates:
            continue
        if dates[-1] >= from_date:
            packs.append(pack)
    return sorted(packs, key=lambda p: str(p))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/rerender_redbook_from_raw.py <pack1> [pack2 ...]")
        return 2
    if sys.argv[1] == "--current-two":
        root = Path(__file__).resolve().parents[1]
        packs = []
        for prefix, day in (("20260712_", "2026-07-01"), ("20260711_", "2026-07-02")):
            matches = [
                p for p in root.rglob(f"{prefix}*potato*")
                if p.is_dir()
                and p.parent.name == day
                and (p / "prompts").exists()
                and (p / "images" / "_potato_raw").exists()
            ]
            if not matches:
                raise RuntimeError(f"Cannot find pack with prefix {prefix} under {day}")
            packs.append(sorted(matches, key=lambda p: len(str(p)))[0])
        module = load_module()
        for pack in packs:
            rerender_pack(pack, module)
        return 0
    if sys.argv[1] == "--from-date":
        if len(sys.argv) < 3:
            print("Usage: python tools/rerender_redbook_from_raw.py --from-date YYYY-MM-DD")
            return 2
        root = Path(__file__).resolve().parents[1]
        packs = discover_packs_from_date(root, sys.argv[2])
        module = load_module()
        print(f"found {len(packs)} packs")
        failures: list[str] = []
        for pack in packs:
            try:
                rerender_pack(pack, module)
            except Exception as exc:
                failures.append(f"{pack}: {exc}")
                print(f"failed: {pack}: {exc}", file=sys.stderr)
        if failures:
            print("failures:")
            for item in failures:
                print(f"- {item}")
            return 1
        return 0
    module = load_module()
    for raw in sys.argv[1:]:
        rerender_pack(Path(raw), module)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
