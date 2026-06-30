from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


SCRIPT_PATH = Path.home() / ".codex" / "skills" / "potato-illustrations" / "scripts" / "generate_redbook_images.py"
CONFIG_PATH = Path.home() / ".codex" / "apis.json"


def load_module():
    spec = importlib.util.spec_from_file_location("generate_redbook_images", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载脚本：{SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))


def prime_ark_env_from_config(config: dict) -> None:
    # Force child image-generation subprocesses to inherit the known-good
    # Agent Plan credentials from ~/.codex/apis.json instead of any stale
    # process/user environment values on this machine.
    api_key = config.get("ARK_API_KEY") or config.get("AGENT_API_KEY")
    base_url = config.get("ARK_url") or config.get("ARK_URL") or config.get("base_url")
    if api_key:
        os.environ["ARK_API_KEY"] = api_key
        os.environ["AGENT_API_KEY"] = api_key
    if base_url:
        os.environ["ARK_URL"] = base_url


def main() -> int:
    if len(sys.argv) < 2:
        print("用法：python tools/run_specific_redbook_packs.py <pack1> [pack2 ...]")
        return 2

    module = load_module()
    config_data = load_config()
    prime_ark_env_from_config(config_data)
    ark_script = module.default_ark_script()
    config_path = module.default_config()
    root = Path.cwd().resolve()

    class Args:
        model = None
        size = "2K"
        timeout = 180
        force = True
        pages = None

    failures: list[str] = []
    for raw in sys.argv[1:]:
        pack = Path(raw)
        if not pack.is_absolute():
            pack = (root / pack).resolve()
        print(f"\n## {pack}")
        try:
            module.generate_pack(pack, Args, ark_script, config_path)
        except Exception as exc:
            failures.append(f"{pack}: {exc}")
            try:
                module.update_report(pack, "失败", str(exc).replace("\n", " ")[:1000])
            except Exception:
                pass
            print(f"失败：{exc}", file=sys.stderr)

    if failures:
        print("\n失败列表：", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
