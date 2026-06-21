---
name: social-push
description: Use when pushing locally prepared WeChat Official Account content from workspace files into the official editor and saving it as a draft, including strict local-to-editor conversion and cover handling.
disable-model-invocation: false
allowed-tools: Bash(agent-browser:*), Bash(jq:*), Bash(osascript:*), Read
---

# Social Push

## Scope

This skill only handles WeChat Official Account draft staging from local workspace files.

It does not:

- choose topics
- write new content from scratch
- generate Xiaohongshu content
- publish live

## Input priority

When a folder is provided, read in this order:

1. `草稿箱正文.txt`
2. `发布稿.md`
3. `images/`
4. `配图方案.md`
5. `metadata.json`

## Hard rules

- Never paste raw Markdown into the editor.
- Convert local content into structured editor blocks first.
- Keep major headings and prompt-style subheadings visible inside the WeChat editor.
- Merge broken one-line fragments into natural paragraphs before insertion.
- Body images must be inserted in article order.
- Use the dedicated local cover image first: `01_公众号封面.png` or `cover_path`.
- Never lazily use the first body image as the cover.
- Only save to drafts. Do not click publish.

## WeChat cover workflow

The cover flow is fixed:

1. select cover image
2. next step
3. edit cover
4. confirm
5. save draft

For existing drafts that need visual refresh:

1. reopen the draft
2. replace the cover with the new local cover
3. verify preview changed
4. save draft again

## Success conditions

Do not treat “已保存 / 手动保存” text as the only success signal.

The draft update is considered successful only when all of these are true:

1. title is visibly written
2. body blocks are visibly inserted
3. cover preview shows the intended cover
4. the flow reached the save-draft step

## CTA rule

Default CTA for this workspace:

`关注我，后续日常推送与直播带你手把手开发自己的工作流与智能体。`

Do not rewrite this back into reply-keyword lead magnets unless the user explicitly asks.
