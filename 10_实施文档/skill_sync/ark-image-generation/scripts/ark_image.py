#!/usr/bin/env python3
"""Generate images with Volcengine Ark direct-image or Agent Plan routes."""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_ENDPOINT = "/images/generations"
DEFAULT_MODEL = "doubao-seedream-3-0-t2i-250415"
DEFAULT_SIZE = "1024x1024"
DEFAULT_CONFIG = str(Path.home() / ".codex" / "apis.json")
DEFAULT_POLL_INTERVAL = 3.0
DEFAULT_POLL_TIMEOUT = 300.0


def configure_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate images with Volcengine Ark Seedream or Agent Plan."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Ark API base URL.")
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help="Image generation endpoint path or full URL.",
    )
    parser.add_argument(
        "--api-key-env",
        default=None,
        help="Environment variable containing the API key. Defaults to ARK_API_KEY, then AGENT_API_KEY.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Optional JSON config file. Defaults to ~/.codex/apis.json when it exists.",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    probe = subparsers.add_parser("probe", help="Probe whether the configured key supports direct image or Agent Plan routes.")
    probe.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds.")
    probe.add_argument("--check-direct", action="store_true", help="Also probe the direct image endpoint.")

    generate = subparsers.add_parser("generate", help="Create an image generation request.")
    generate.add_argument("--prompt", required=True, help="Text prompt for image generation.")
    generate.add_argument("--model", default=DEFAULT_MODEL, help="Direct image model or deployed endpoint id.")
    generate.add_argument("--plan-model", help="Agent Plan-compatible image model id.")
    generate.add_argument("--size", default=DEFAULT_SIZE, help="Image size, for example 1024x1024.")
    generate.add_argument(
        "--response-format",
        default="url",
        choices=["url", "b64_json"],
        help="Requested response format when supported by the provider.",
    )
    generate.add_argument("--seed", type=int, help="Optional deterministic seed.")
    generate.add_argument("--guidance-scale", type=float, help="Optional guidance scale.")
    generate.add_argument(
        "--watermark",
        choices=["true", "false"],
        help="Optional provider watermark flag.",
    )
    generate.add_argument(
        "--extra-json",
        help="JSON object merged into the request body for provider-specific options.",
    )
    generate.add_argument("--out-dir", type=Path, default=Path("output"), help="Output directory.")
    generate.add_argument("--filename-prefix", default="ark-image", help="Saved file prefix.")
    generate.add_argument("--timeout", type=float, default=120.0, help="HTTP timeout in seconds.")
    generate.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL, help="Polling interval in seconds for plan tasks.")
    generate.add_argument("--poll-timeout", type=float, default=DEFAULT_POLL_TIMEOUT, help="Polling timeout in seconds for plan tasks.")
    generate.add_argument("--dry-run", action="store_true", help="Print request without network.")
    return parser


def load_config(path):
    if not path:
        return None
    config_path = Path(path)
    if not config_path.exists():
        return None
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Config file is not valid JSON: {config_path}: {exc}") from exc


def iter_pairs(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key), item
            yield from iter_pairs(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_pairs(item)


def find_config_value(config, names, contains=None):
    if config is None:
        return None
    normalized = {name.lower() for name in names}
    contains = [item.lower() for item in (contains or [])]
    for key, value in iter_pairs(config):
        if not isinstance(value, str) or not value.strip():
            continue
        lower_key = key.lower()
        lower_value = value.lower()
        if lower_key in normalized:
            return value
        if any(marker in lower_key for marker in contains):
            return value
        if any(marker in lower_value for marker in contains):
            return value
    return None


def resolve_api_key(api_key_env):
    names = [api_key_env] if api_key_env else ["ARK_API_KEY", "AGENT_API_KEY"]
    for name in names:
        if not name:
            continue
        value = os.environ.get(name)
        if value:
            return name, value
    raise SystemExit(
        "No Ark API key found. Set ARK_API_KEY, or pass --api-key-env AGENT_API_KEY "
        "if you use the same Agent Plan key as ark-video-generation."
    )


def resolve_api_key_with_config(api_key_env, config):
    if config is not None and api_key_env is None:
        key = find_config_value(
            config,
            names=["key", "api_key", "ark_api_key", "agent_api_key", "token"],
            contains=["api_key", "ark_key", "agent_key", "token"],
        )
        if key:
            return "config", key
    try:
        return resolve_api_key(api_key_env)
    except SystemExit:
        key = find_config_value(
            config,
            names=["key", "api_key", "ark_api_key", "agent_api_key", "token"],
            contains=["api_key", "ark_key", "agent_key", "token"],
        )
        if key:
            return "config", key
        raise


def resolve_base_url_from_config(config):
    return find_config_value(
        config,
        names=["ark_url", "ark-url", "base_url", "base-url"],
        contains=["/api/plan/v3", "/api/v3"],
    )


def detect_mode(base_url):
    lower = base_url.lower()
    if "/api/plan/v3" in lower:
        return "agent-plan"
    return "direct-image"


def build_url(base_url, endpoint):
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    return base_url.rstrip("/") + "/" + endpoint.lstrip("/")


def parse_extra_json(raw):
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--extra-json is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("--extra-json must be a JSON object.")
    return value


def build_direct_body(args):
    body = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "response_format": args.response_format,
    }
    if args.seed is not None:
        body["seed"] = args.seed
    if args.guidance_scale is not None:
        body["guidance_scale"] = args.guidance_scale
    if args.watermark is not None:
        body["watermark"] = args.watermark == "true"
    body.update(parse_extra_json(args.extra_json))
    return body


def print_json(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def request_json(method, url, api_key, body, timeout):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw) if raw else {}
            return {"ok": True, "status": response.status, "payload": payload}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return {"ok": False, "status": exc.code, "payload": payload}


def iter_image_items(payload):
    if not isinstance(payload, dict):
        return

    data = payload.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item

    images = payload.get("images")
    if isinstance(images, list):
        for item in images:
            if isinstance(item, dict):
                yield item
            elif isinstance(item, str):
                yield {"url": item}

    for key in ("url", "image_url", "b64_json"):
        if payload.get(key):
            yield {key: payload[key]}


def guess_suffix(url, default_suffix=".png"):
    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix
    return suffix or default_suffix


def download_url(url, destination, timeout):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=timeout) as response:
        destination.write_bytes(response.read())


def save_outputs(payload, out_dir, prefix, timeout):
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    for index, item in enumerate(iter_image_items(payload) or [], start=1):
        url = item.get("url") or item.get("image_url") or item.get("file_url")
        b64_json = item.get("b64_json")
        if url:
            target = out_dir / f"{prefix}-{timestamp}-{index}{guess_suffix(url)}"
            download_url(url, target, timeout)
            saved.append(str(target))
        elif b64_json:
            target = out_dir / f"{prefix}-{timestamp}-{index}.png"
            target.write_bytes(base64.b64decode(b64_json))
            saved.append(str(target))

    return saved


def detect_plan_model(args, config):
    if args.plan_model:
        return args.plan_model
    return find_config_value(
        config,
        names=["ark_plan_image_model", "plan_image_model", "agent_plan_image_model"],
        contains=["seedream", "image_model"],
    )


def size_to_ratio(size):
    try:
        width_text, height_text = size.lower().split("x", 1)
        width = int(width_text)
        height = int(height_text)
    except Exception:
        return None
    if width <= 0 or height <= 0:
        return None
    from math import gcd

    factor = gcd(width, height)
    return f"{width // factor}:{height // factor}"


def build_plan_body(args, plan_model):
    body = {
        "model": plan_model,
        "content": [
            {
                "type": "text",
                "text": args.prompt,
            }
        ],
    }
    if args.seed is not None:
        body["seed"] = args.seed
    if args.watermark is not None:
        body["watermark"] = args.watermark == "true"
    ratio = size_to_ratio(args.size)
    if ratio:
        body["ratio"] = ratio
    body.update(parse_extra_json(args.extra_json))
    return body


def poll_plan_task(base_url, api_key, task_id, timeout, interval):
    url = build_url(base_url, f"/contents/generations/tasks/{task_id}")
    deadline = time.time() + timeout
    while True:
        result = request_json("GET", url, api_key, None, timeout=min(30.0, timeout))
        if not result["ok"]:
            return result
        payload = result["payload"]
        status = str(payload.get("status", "")).lower()
        if status in {"succeeded", "failed", "cancelled"}:
            return result
        if time.time() >= deadline:
            return {
                "ok": False,
                "status": 408,
                "payload": {
                    "error": {
                        "code": "PollTimeout",
                        "message": f"Timed out waiting for Agent Plan task {task_id}",
                    }
                },
            }
        time.sleep(interval)


def run_probe(args):
    config = load_config(args.config)
    configured_base_url = resolve_base_url_from_config(config)
    base_url = configured_base_url or args.base_url
    mode = detect_mode(base_url)
    env_name, api_key = resolve_api_key_with_config(args.api_key_env, config)

    result = {
        "ok": True,
        "api_key_env": env_name,
        "detected_mode": mode,
        "base_url": base_url,
        "plan_tasks": None,
        "direct_image": None,
    }

    if mode == "agent-plan":
        plan_url = build_url(base_url, "/contents/generations/tasks?page_num=1&page_size=1")
        plan_result = request_json("GET", plan_url, api_key, None, args.timeout)
        result["plan_tasks"] = {
            "ok": plan_result["ok"],
            "status": plan_result["status"],
        }
        if not plan_result["ok"]:
            result["ok"] = False
            result["plan_tasks"]["error"] = plan_result["payload"]

    if args.check_direct or mode == "direct-image":
        direct_base = DEFAULT_BASE_URL if mode == "agent-plan" else base_url
        direct_url = build_url(direct_base, DEFAULT_ENDPOINT)
        body = {
            "model": DEFAULT_MODEL,
            "prompt": "probe only",
            "size": DEFAULT_SIZE,
            "response_format": "url",
        }
        direct_result = request_json("POST", direct_url, api_key, body, args.timeout)
        result["direct_image"] = {
            "ok": direct_result["ok"],
            "status": direct_result["status"],
        }
        if not direct_result["ok"]:
            result["direct_image"]["error"] = direct_result["payload"]

    print_json(result)
    return 0 if result["ok"] else 1


def handle_generate(args):
    config = load_config(args.config)
    configured_base_url = resolve_base_url_from_config(config)
    config_url = find_config_value(
        config,
        names=["seedream-url", "seedream_url", "url"],
        contains=["images/generations"],
    )
    config_model = find_config_value(
        config,
        names=["seedream-model", "seedream_model", "model", "endpoint_id"],
        contains=["seedream"],
    )
    if configured_base_url and args.base_url == DEFAULT_BASE_URL:
        args.base_url = configured_base_url
    mode = detect_mode(args.base_url)

    if config_model and args.model == DEFAULT_MODEL:
        args.model = config_model

    env_name, api_key = resolve_api_key_with_config(args.api_key_env, config)

    if mode == "agent-plan":
        plan_model = detect_plan_model(args, config)
        if not plan_model:
            print_json(
                {
                    "ok": False,
                    "status": 400,
                    "error": {
                        "code": "MissingPlanImageModel",
                        "message": "Detected an Agent Plan key from ARK_url, but no confirmed plan image model id was provided. Add --plan-model or set ARK_PLAN_IMAGE_MODEL in ~/.codex/apis.json.",
                    },
                }
            )
            return 1
        body = build_plan_body(args, plan_model)
        url = build_url(args.base_url, "/contents/generations/tasks")

        if args.dry_run:
            print_json(
                {
                    "ok": True,
                    "dry_run": True,
                    "mode": mode,
                    "url": url,
                    "headers": {
                        "Authorization": "Bearer ***",
                        "Content-Type": "application/json",
                    },
                    "body": body,
                }
            )
            return 0

        create_result = request_json("POST", url, api_key, body, args.timeout)
        if not create_result["ok"]:
            print_json({"ok": False, "status": create_result["status"], "error": create_result["payload"]})
            return 1

        payload = create_result["payload"]
        task_id = payload.get("id")
        if not task_id:
            print_json({"ok": False, "status": 502, "error": {"code": "MissingTaskId", "message": "Agent Plan create response did not include a task id."}})
            return 1

        final_result = poll_plan_task(args.base_url, api_key, task_id, args.poll_timeout, args.poll_interval)
        if not final_result["ok"]:
            print_json({"ok": False, "status": final_result["status"], "error": final_result["payload"], "task_id": task_id})
            return 1

        final_payload = final_result["payload"]
        if str(final_payload.get("status", "")).lower() != "succeeded":
            print_json({"ok": False, "status": 409, "error": final_payload.get("error"), "task_id": task_id, "response": final_payload})
            return 1

        content = final_payload.get("content") or {}
        synthesized = {}
        if isinstance(content, dict):
            for field in ("file_url", "image_url", "url"):
                if content.get(field):
                    synthesized[field] = content[field]
            if content.get("b64_json"):
                synthesized["b64_json"] = content["b64_json"]
        saved = save_outputs(synthesized, args.out_dir, args.filename_prefix, args.timeout)
        print_json(
            {
                "ok": True,
                "api_key_env": env_name,
                "mode": mode,
                "task_id": task_id,
                "response": final_payload,
                "saved": saved,
            }
        )
        if not saved:
            print("[warning] Agent Plan task succeeded but no downloadable image field was detected.", file=sys.stderr)
        return 0

    if config_url and args.endpoint == DEFAULT_ENDPOINT and args.base_url == DEFAULT_BASE_URL:
        url = config_url
    else:
        url = build_url(args.base_url, args.endpoint)
    body = build_direct_body(args)

    if args.dry_run:
        print_json(
            {
                "ok": True,
                "dry_run": True,
                "mode": mode,
                "url": url,
                "headers": {
                    "Authorization": "Bearer ***",
                    "Content-Type": "application/json",
                },
                "body": body,
            }
        )
        return 0

    result = request_json("POST", url, api_key, body, args.timeout)
    if not result["ok"]:
        print_json({"ok": False, "status": result["status"], "error": result["payload"]})
        if "/api/plan/v3/" in url and "seedream" in args.model.lower():
            print(
                "[hint] The configured key works on Agent Plan routes, but the current model is not compatible with plan/v3.",
                file=sys.stderr,
            )
        elif "/api/v3/images/generations" in url:
            print(
                "[hint] If ~/.codex/apis.json only contains an Agent Plan key or ARK_url for /api/plan/v3, that key may not be authorized for the direct Seedream image endpoint.",
                file=sys.stderr,
            )
        return 1

    payload = result["payload"]
    saved = save_outputs(payload, args.out_dir, args.filename_prefix, args.timeout)
    print_json({"ok": True, "api_key_env": env_name, "mode": mode, "response": payload, "saved": saved})
    if not saved:
        print("[warning] No image URL or b64_json output was detected.", file=sys.stderr)
    return 0


def main():
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "probe":
        return run_probe(args)
    if args.command == "generate":
        return handle_generate(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
