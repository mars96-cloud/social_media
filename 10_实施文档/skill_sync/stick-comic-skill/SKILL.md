---
name: stick-comic-skill
description: Use when creating cartoon-style educational covers, Xiaohongshu comic posts, or thumbnail-first explainer visuals that need a Sticky-Academy-like feel with simple characters, bold contrast, money or path metaphors, and high-click composition without copying the source account directly.
---

# Stick Comic Skill

## Overview

This skill creates a reusable visual system inspired by the communication style seen in Sticky-style finance explainer thumbnails: simple stick-like characters, bold contrast, strong hooks, exaggerated situations, and highly legible composition.

This skill does not copy protected characters, exact layouts, exact text, or exact thumbnails from any source account. It extracts the usable design grammar and converts it into an original workflow for local content production.

## When to Use

Use this skill when the goal is:
- a Xiaohongshu comic that must feel simple, bold, and highly clickable
- a financial, growth, money, career, or AI topic that benefits from exaggerated contrast
- a cover or slide that should feel like a YouTube-thumbnail-first explainer
- a cartoon explainer with very few characters, very clear symbolism, and low visual noise

Do not use this skill when:
- the user wants the validated `shinchan` Xiaohongshu dialogue route already used in this workspace
- the user wants a softer editorial, realistic, or painterly style
- the user wants dense text cards or information-heavy diagrams

## Core Style System

The visual target is a Sticky-like explainer grammar, not a copy.

### Non-negotiable traits

- white or near-white background
- thick black outlines
- very simple round-headed characters
- flat high-contrast color fills
- one big idea per page
- strong symbol objects: money, arrows, cages, roads, crowns, phones, charts, traps, robots, clocks
- thumbnail-like headline composition
- readable from small mobile preview size

### Character system

Default cast:
- learner: plain round-head stick person, worried or confused
- guide: slightly more confident stick person, pointing or explaining
- optional success-state version: crown, sunglasses, cash, or calm smile

Character constraints:
- no complex anatomy
- no detailed fingers
- no realistic shading
- no crowded background scenes
- faces use 2-4 emotional features only
- body pose must communicate the idea immediately

### Color system

Preferred palette:
- black outline
- white background
- green for money or gain
- red for danger, mistake, or urgency
- blue for comparison or structure
- yellow or gold for reward, status, or trap bait
- purple only as accent, not dominant base

### Composition rules

- one main character or one clear two-side comparison only
- big hook words at top or top-left
- visual story should read in under 2 seconds
- no decorative clutter
- no soft beige editorial card treatment
- background should support the idea, not compete with it

### Sticky-style metaphors to prefer

- rich vs stuck
- build vs consume
- salary vs asset
- cage vs freedom
- robot era vs human value
- fast money vs stable path
- confusion vs framework
- effort vs leverage

## Xiaohongshu Route

When used for Xiaohongshu, prefer a dialogue-comic adaptation of this style:
- keep pages simple and bold
- each page carries one judgment only
- page 01 should be a thumbnail-grade title cover
- inner pages should use 1-2 characters max
- speech should be very short
- symbols carry more meaning than long paragraphs

Recommended page order:
1. title cover page
2. mistaken belief page
3. reality check page
4. key comparison page
5. action path page
6. comment hook or CTA page

## Prompt Construction

Always build prompts from these layers:
1. topic judgment
2. emotional contrast
3. simple character state
4. symbolic object
5. composition direction
6. text handling rule

### Prompt skeleton

```text
A bold cartoon explainer image in an original stick-figure thumbnail style, white background, thick black outlines, flat bright colors, simple round-head character design, exaggerated facial expression, high-click YouTube-thumbnail composition, one big metaphor, very readable, clean negative space, no clutter, no watermark.

Topic: [core judgment]
Scene: [wrong vs right or single strong metaphor]
Character: [learner / guide / success-state]
Symbols: [money / cage / road / robot / chart / crown / phone]
Composition: [top hook area + central visual conflict + bottom reinforcement]
Text rule: leave clean space for later local typography, do not render long Chinese text inside the image.
```

## Ark Workflow

Use `ark-image-generation` for generation.

Preferred order:
1. write prompt files first
2. generate cover first
3. check whether the visual language is correct before generating the rest
4. if Ark route is blocked or model id is unavailable, still finish the local package with prompts, storyboard, and copy

## Local Typography Rules

Do not rely on generated Chinese text as final output.

- generate clean illustration space first
- add final Chinese title locally when readability matters
- avoid text touching edges
- avoid warping or broken radicals
- short phrases only on final image

### Xiaohongshu page-header rule

For Xiaohongshu final pages in this workspace:

- every publish page may add one short local Chinese header that explains the page judgment
- this header must be white background plus black text only
- do not use fragile speech-bubble tails by default for these page headers
- prefer a horizontal rounded title card placed in the upper blank area
- keep the header card away from faces, props, step numbers, or other core visual elements
- if the upper area is crowded, move the title card or expand canvas upward instead of covering the subject
- typography must be locally typeset after generation, with fixed inner padding so text never touches or breaks through the border
- when readability is weak, increase card size and font size together rather than shrinking margins too hard
- the added header is a reading aid, not the main cover title, so keep it short and stable
- if a page looks acceptable in raw art but becomes crowded after overlay, revise the local header layout instead of regenerating the illustration

## Common Mistakes

- trying to imitate the exact source account instead of the design grammar
- adding too many props in one page
- making the stick character too detailed
- using weak pale colors that kill thumbnail contrast
- writing full paragraphs on image
- making every page look identical with no emotional shift

## Deliverables

For a Xiaohongshu batch, save:
- `analysis.md`
- `storyboard.md`
- `characters.md`
- `prompts/`
- `images/`
- normal local package files required by this workspace
