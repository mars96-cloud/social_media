---
name: ark-image-generation
description: Use when Codex needs to generate images with Volcengine Ark Seedream, 豆包 Seedream, 火山方舟文生图, Ark image generation, or Agent Plan image tasks from text prompts, including saving generated images locally, checking request payloads, or troubleshooting Ark image API errors.
---

# Ark Image Generation

Use the bundled Python helper instead of hand-writing Ark API calls.

## Credentials

- Prefer `~/.codex/apis.json` by default when it contains Ark credentials or model settings.
- Use `ARK_API_KEY` or `AGENT_API_KEY` only as fallback.
- Never print API keys.
- If `~/.codex/apis.json` contains `ARK_url` that points to `.../api/plan/v3`, treat that as an Agent Plan route, not as direct proof that the key can call Seedream `images/generations`.
- If `~/.codex/apis.json` only has `ARK_url` plus `ARK_API_KEY`, first probe which mode it supports instead of assuming direct image generation.

## Standard workflow

1. confirm text-to-image, not video
2. load credentials from `~/.codex/apis.json`
3. run a capability probe when the route looks like Agent Plan
4. choose direct image mode or Agent Plan task mode
5. generate into the requested output folder
6. save URL outputs immediately
7. inspect JSON errors before changing model or endpoint

## Capability detection

- `ARK_url = .../api/plan/v3` means the key is very likely a plan key.
- A plan key can be real and usable even if `/api/v3/images/generations` returns `401`.
- For this workspace, treat these outcomes separately:
  - `GET /api/plan/v3/contents/generations/tasks` returns `200`:
    the key works for Agent Plan
  - `POST /api/plan/v3/contents/generations/tasks` with a guessed Seedream model returns `UnsupportedModel`:
    the key still works, but the image model id is wrong or not enabled for this package
  - `/api/v3/images/generations` returns `401`:
    do not call the key invalid; it only means direct image mode is not authorized

## Agent Plan rule

- Do not assume a direct Seedream model name will also work in Agent Plan.
- If the detected route is Agent Plan, prefer:
  - `python scripts/ark_image.py probe --config "$env:USERPROFILE\\.codex\\apis.json"`
  - then `python scripts/ark_image.py generate --config ... --plan-model <actual_plan_image_model>`
- If no confirmed plan image model is available yet, fail clearly and fall back to local rendering. Do not pretend Ark generation succeeded.

## Social-media batch rules

- Do not reuse one visual style across every article in a batch.
- Rotate visual families such as editorial, blueprint, newsroom, mint-grid, studio-pop, or slate-pro.
- When generating WeChat covers, prefer dramatic no-text backgrounds and add final hook text locally.

## WeChat cover standard

- The cover image is not the article title turned into a card.
- First derive the click reason.
- Then compress it into a short hook for local overlay.
- The Ark prompt should focus on:
  - one strong subject
  - exaggerated contrast
  - curiosity
  - clear thumbnail readability
  - no text
  - no watermark

### Forbidden prompt direction

- minimal beige editorial card
- too much empty space with no focal object
- prompt that mainly describes “clean information layout”

## Troubleshooting rule for this workspace

- If the key in `~/.codex/apis.json` returns `401` on the standard image endpoint but succeeds on `.../api/plan/v3` with a model-compatibility error, conclude that:
  - the config was read successfully
  - the key is real
  - the Agent Plan route is reachable
  - but the current image model id is not the right Agent Plan-compatible model for this account or package
- In that case, do not pretend image generation succeeded.
- Fall back to local rendering or ask for one of these:
  - a confirmed Agent Plan image model id
  - a Seedream-capable direct image key
  - a deployed direct image endpoint id

## Command examples

```powershell
python scripts/ark_image.py --config "$env:USERPROFILE\\.codex\\apis.json" probe
```

```powershell
python scripts/ark_image.py --config "$env:USERPROFILE\\.codex\\apis.json" generate --prompt "A dramatic Chinese social-media cover background, no text" --out-dir output
```

```powershell
python scripts/ark_image.py --config "$env:USERPROFILE\\.codex\\apis.json" generate --plan-model "<actual-plan-image-model>" --prompt "A creator desk with exaggerated contrast and one glowing workflow path" --size 1536x1024 --out-dir output
```
