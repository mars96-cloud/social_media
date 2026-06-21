---
name: social-media-workspace-operator
description: Use when planning, drafting, repurposing, or archiving Xiaohongshu, WeChat Official Account, or Douyin content into the local social media workspace without pushing to live platform editors.
---

# Social Media Workspace Operator

## Scope

This skill only does two things:

1. Strategy and content planning
2. Generate local deliverables inside the workspace

It does not open platform editors, upload assets to live editors, save drafts on platforms, or publish. Those actions belong to `social-push` for WeChat only.

## Required output

For each article or post, save to the workspace:

- `发布稿.md`
- `草稿箱正文.txt`
- `配图方案.md`
- `metadata.json`
- `images/`

## WeChat rules

- The article title explains the topic clearly.
- The cover does not repeat the full title.
- Always derive one click reason first, then compress it into a short cover hook.
- Default cover hook length: `4-10` Chinese characters.
- Default cover goal: eye-catching, simple, exaggerated, curiosity-driven.
- Forbidden cover pattern: beige information card plus full title text.
- Each batch must rotate multiple visual styles. Do not let all covers collapse into one template.

### WeChat in-article image rules

- Do not default to pure text cards.
- Prefer scene-like visuals, contrast, symbols, paths, role split, or error-vs-correct framing.
- Keep only a small amount of short text on the image.
- Let the article body carry the full explanation.

## Xiaohongshu rules

- Xiaohongshu stays local in this skill. Do not publish from here.
- Prefer image-led deliverables over long plain text.
- Put as much key information as possible into the image set.
- Provide title candidates, opening hook, short body text, card copy, tags, and image plan.

## CTA rule

Default CTA for this workspace:

`关注我，后续日常推送与直播带你手把手开发自己的工作流与智能体。`

Do not default to reply-keyword lead magnets such as “回复关键词领取资料”.

## Required workspace references

Read these before major generation work:

- `02_内容系统/钩子与标题.md`
- `12_平台执行框架/配图与排版规则.md`
- `12_平台执行框架/公众号执行规则.md`

## Quality bar

The output is not done unless:

- title and cover clearly do different jobs
- cover has a real click reason
- in-article images help the article think, not just decorate it
- the batch shows visible style rotation
- all files are saved locally with complete structure

## Ark image fallback rule

- If `~/.codex/apis.json` points to `.../api/plan/v3`, treat it as an Agent Plan image route first.
- A successful plan-task probe plus a failed Seedream direct call means:
  - the key is real
  - but the current plan image model id is still missing or wrong
- In that case, do not block the whole batch.
- Finish the local article package with strong local-rendered covers and keep the missing plan image model as a separate follow-up item.
