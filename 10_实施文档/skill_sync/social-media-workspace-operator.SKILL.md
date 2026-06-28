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

## Workspace routing rules

Use this workspace month structure as the default routing target:

`06_运营中心/<年份>/<YYYY-MM>/`

The first-level folders under each month are:

- `小红书/`
- `公众号/`
- `视频/`
- `月度选题/`
- `文章总览/`

Routing rules:

- monthly topic planning, posting calendars, topic pools, and series planning go to `月度选题/`
- mother articles, mother templates, and cross-platform source drafts go to `文章总览/`
- Xiaohongshu deliverables go to `小红书/`
- WeChat Official Account deliverables go to `公众号/`
- video scripts, storyboards, and publish-ready video project assets go to `视频/`

Compatibility rule:

- older month folders may still contain `草稿区/`, `短视频项目/`, or `已发布/`
- treat those as legacy compatibility layers
- for all new work, prefer the new month structure above unless the user explicitly asks to keep writing into the old path

## Required output

For each article or post, save to the workspace:

- `发布稿.md`
- `草稿箱正文.txt`
- `配图方案.md`
- `metadata.json`
- `images/`

When a task is cross-platform by nature, create or update a mother draft in `文章总览/` first, then derive the platform-specific package into the target platform folder.

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

### WeChat comic-infographic mode

- WeChat comic-infographic mode and Xiaohongshu comic-dialogue mode are two separate production systems in this workspace. Do not let a WeChat illustration update change the accepted Xiaohongshu comic route.
- Default split for this workspace:
  - Xiaohongshu = recurring characters + dialogue comic + `shinchan` route
  - WeChat = non-dialogue comic-infographic + locally typeset information visuals

- When the user says the current WeChat images are weak, AI-heavy, strange, or asks for a comic-skill-inspired upgrade, use comic-infographic mode.
- Comic-infographic mode is for `文字 + 配图` WeChat articles. It is not dialogue comic mode.
- The visual target is: comic-like explanation, but not speech-bubble storytelling and not copyright-character imitation.
- Do not imitate Doraemon, Shin-chan, or any other protected character directly in WeChat article illustrations unless the user explicitly accepts the legal and aesthetic risk and the output route is appropriate. Default behavior is to avoid IP imitation.
- Prefer these WeChat image structures:
  - cover with wrong-vs-right contrast
  - compare card: misconception vs correct judgment
  - three-step path card
  - phase / workflow / route breakdown
  - one-scene-one-judgment explainer
- Prefer these visual ingredients:
  - thick stable blocks
  - bold section titles
  - high-contrast labels
  - simple icon-like markers
  - bridge blocks instead of fragile connectors
  - one key judgment per image
- Avoid these failure patterns:
  - pseudo-anime character faces with wrong likeness
  - thin arrows, tiny connector lines, or delicate symbols that easily break
  - model-rendered long Chinese text as final typography
  - beige information cards with paragraph dumps
  - random sparkles, emoji noise, repeated punctuation, or decorative clutter
  - multiple visual ideas fighting in one image
- Typography rules for WeChat comic-infographic mode:
  - treat generated or illustrated layers as background only
  - final Chinese titles, chips, labels, step numbers, and summaries should be locally typeset whenever readability risk exists
  - no clipped glyphs, broken radicals, text touching borders, or compressed lines are acceptable
  - if any title, label, bridge word, or footer looks deformed, fix it locally before saving the final PNG
- Cover rules for WeChat comic-infographic mode:
  - the cover must carry a strong click reason independent from the article title
  - do not reuse the full article title as cover copy
  - the first screen should show one visual conflict clearly within mobile preview scale
  - default cover pattern for this workspace: short hook plus wrong-vs-right contrast
- Body image rules for WeChat comic-infographic mode:
  - each body image explains one judgment only
  - prefer `compare` or `steps` layouts over generic quote cards
  - if a connector is needed, use thick pill bridges or block transitions instead of arrows
  - if the image starts to feel like PPT screenshot or text poster, simplify and restage it

## Xiaohongshu rules

- Xiaohongshu stays local in this skill. Do not publish from here.
- Prefer image-led deliverables over long plain text.
- Put as much key information as possible into the image set.
- Provide title candidates, opening hook, short body text, card copy, tags, and image plan.
- Xiaohongshu and WeChat must stay on separate visual routes in this workspace. A WeChat image-style revision does not imply any change to Xiaohongshu comic-dialogue output.

### Xiaohongshu comic-dialogue mode

- When the user asks for a Xiaohongshu comic, manga, dialogue comic, or wants an existing article turned into a comic conversation, use comic-dialogue mode.
- In comic-dialogue mode, prefer repurposing a validated WeChat draft or other long-form source into:
  - one core judgment per page
  - fixed recurring characters
  - short dialogue-first delivery
  - image-dominant pages with only necessary text
- Default workflow for Xiaohongshu comic-dialogue mode:
  1. keep a separate recurring-character reference page
  2. add a dedicated title cover page before any正文 page
  3. choose a suitable source topic or WeChat mother draft
  4. extract the single-sentence core judgment
  5. split it into one title cover page plus 4-6 comic pages
  6. write `analysis.md`, `storyboard.md`, `characters.md`, `prompts/`
  7. generate a `00_角色参考页`
  8. generate a `01_标题封面页`
  9. generate final page images into `images/`
  10. save the normal local post package files too: `发布稿.md`, `草稿箱正文.txt`, `配图方案.md`, `metadata.json`
- Preferred character relationship:
  - one learner / confused creator
  - one mentor / clearer operator
- Dialogue rules:
  - one round of dialogue per panel
  - keep lines short
  - let the learner ask common wrong or incomplete questions
  - let the mentor give the judgment and correction
  - avoid AI-heavy filler like stacked punctuation, repeated symbols, emoji endings, or noisy decorative marks
  - do not use `??`, `！！`, mixed emoji emphasis, or random sparkle/star symbols unless the page truly needs one small accent
  - dialogue should read like hand-set comic copy, not model-generated sticker text
- Title cover rules:
  - do not use the character reference page as the publish cover
  - always create a separate title cover page between the character reference page and the正文 pages
  - default cover structure for this workspace: title plus wrong-vs-right contrast
  - the title cover must spotlight the post theme first; characters only support the hook
  - the cover should show one obvious wrong path on one side and one clearer right path on the other side
  - keep text short and bold enough to read on Xiaohongshu mobile screens
  - cover title text is a high-risk area for glyph deformation; after image generation, locally re-check and re-typeset the final title if any character edge, radical, or punctuation looks broken
- Xiaohongshu inner-page header rules:
  - if a final Xiaohongshu page needs one extra explanatory line, add it as local post-typeset text only
  - use white background plus black text only
  - default header form for this workspace is a horizontal rounded title card, not a fragile speech bubble with a tail
  - prefer placing the title card in the upper blank area or expanded top white area instead of covering the generated art directly
  - do not place this header on top of faces, large symbols, step numbers, or other primary visual elements
  - keep clear inner padding between text and border; do not let text touch, clip, or visually crowd the frame
  - if a page needs larger text, enlarge the title card together with the font instead of squeezing text into the old box
  - if the page becomes crowded after overlay, revise the header layout locally rather than regenerating the base illustration
- Style rules:
  - if a requested comic style exists in `comic-guide`, use that style id directly
  - keep one batch visually consistent instead of rotating unrelated styles page by page
  - if Ark image generation is available, use it to generate the comic pages
  - if Ark is blocked or missing a confirmed image model, finish the local comic package anyway and mark image generation as follow-up
  - treat the generated image as the illustration layer, not the final typography source
  - for any page with long titles, vertical headings, step labels, or bottom summary questions, prefer local post-render text replacement when readability is at risk
  - if text overlaps borders, clips into bubbles, breaks Chinese glyphs, or creates obvious AI artifacts, fix it locally before calling the page done
- Validated default route for this workspace:
  - preferred comic style id: `shinchan`
  - treat `shinchan` as the default Xiaohongshu comic-dialogue style unless the user requests another style
  - before generating final pages, first generate `images/00_角色参考页.png`
  - keep the same recurring two-character relationship across the whole batch:
    - learner / confused creator
    - mentor / clearer operator
  - keep page-to-page character consistency tighter than prompt variety; do not chase unrelated scene variation
  - for this workspace, `shinchan` means the visual target should stay in the Crayon Shin-chan-like direction already accepted by the user for Xiaohongshu comic posts
  - when WeChat illustration rules are revised later, keep Xiaohongshu on this validated recurring-character comic-dialogue route unless the user explicitly asks to replace it
- File expectations for comic-dialogue mode:
  - `analysis.md`
  - `storyboard.md`
  - `characters.md`
  - `prompts/`
  - `images/00_角色参考页.png`
  - `images/01_标题封面页.png`
  - `images/02_*.png` ... final pages
  - when local text correction is applied, keep the corrected PNG as the canonical final page instead of the raw model-only version

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

