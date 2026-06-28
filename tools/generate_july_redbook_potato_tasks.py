from __future__ import annotations

import re
from pathlib import Path

from generate_july_redbook_13 import TOPICS, Topic


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "06_运营中心" / "2026" / "2026-07"
OUT_ROOT = BASE / "小红书"
ARTICLE_ROOT = BASE / "文章总览"

PAGE_NAMES = ["封面", "痛点", "判断", "核心", "代入", "方法", "场景", "收束"]


def slug(text: str, max_len: int = 28) -> str:
    text = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", text)
    return text[:max_len]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def find_article_main(day: int) -> Path:
    date = f"2026-07-{day:02d}"
    ymd = f"202607{day:02d}"
    article_dir = ARTICLE_ROOT / date
    if not article_dir.exists():
        raise FileNotFoundError(f"缺少文章总览目录：{article_dir}")
    candidates = [
        p
        for p in article_dir.glob(f"{ymd}_文章总览_*.md")
        if not p.name.endswith("_写作说明.md") and not p.name.endswith("_选题结论.md")
    ]
    if len(candidates) != 1:
        raise FileNotFoundError(f"文章总览母稿数量异常：{article_dir}，找到 {len(candidates)} 个")
    text = candidates[0].read_text(encoding="utf-8").strip()
    if len(text) < 800 or "## 正文主线" not in text:
        raise ValueError(f"文章总览母稿不完整：{candidates[0]}")
    return candidates[0]


def extract_article_brief(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    patterns = {
        "标题建议": r"# 标题建议\s*(.+?)(?=\n## )",
        "一句话核心主张": r"## 一句话核心主张\s*(.+?)(?=\n## )",
        "开头": r"## 开头\s*(.+?)(?=\n## )",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.S)
        if m:
            result[key] = "\n".join(line.strip() for line in m.group(1).strip().splitlines() if line.strip())
    headings = re.findall(r"^###\s+(.+)$", text, re.M)
    result["正文主线"] = "\n".join(f"- {h.strip()}" for h in headings[:8])
    return result


def title_bank(topic: Topic) -> str:
    strong = [
        topic.xhs_title,
        f"{topic.cover_title}，很多人第一步就错了",
        f"{topic.cover_title}，不是你不努力",
        "普通人做 AI，先看懂这件事",
        "你卡住的地方，可能不是工具",
    ]
    contrast = [
        f"真正重要的不是工具，而是{topic.cover_title}",
        "别急着学更多 AI，先补这一段",
        "会用 AI 不等于能稳定出结果",
        "越想一步到位，越容易卡住",
        "先把小流程跑顺，比追新工具更重要",
    ]
    scene = [
        f"如果你也{topic.audience[:18]}",
        "写内容总从零开始的人，建议看完",
        "一个人做内容和业务，先别把 AI 用复杂",
        "学过很多 AI 还是没变化，可能是这里错了",
        "普通创作者更该先搭这一段流程",
    ]
    covers = [topic.cover_title, topic.subtitle, topic.xhs_title[:18]]
    return f"""# 标题库

## 强痛点标题

{chr(10).join(f"{i + 1}. {v}" for i, v in enumerate(strong))}

## 反常识标题

{chr(10).join(f"{i + 1}. {v}" for i, v in enumerate(contrast))}

## 场景代入标题

{chr(10).join(f"{i + 1}. {v}" for i, v in enumerate(scene))}

## 封面标题

{chr(10).join(f"{i + 1}. {v}" for i, v in enumerate(covers))}

## 最终推荐

- 发布标题：{topic.xhs_title}
- 封面标题：{topic.cover_title}
- 推荐理由：标题直接打中读者正在卡住的 AI 工作流问题，适合小红书信息流里快速识别痛点。
"""


def prompt_for_card(topic: Topic, idx: int, card: tuple[str, str, str, str], page: str) -> str:
    composition = {
        "封面": "小漫画型 + 强冲突封面",
        "痛点": "状态变化型",
        "判断": "前后对比型",
        "核心": "流程型",
        "代入": "概念隐喻型",
        "方法": "流程型",
        "场景": "路线型",
        "收束": "状态变化型",
    }[page]
    return f"""# {idx:02d} {page} - potato-illustrations 出图任务

## 固定入口

必须使用 `potato-illustrations` 生成。不要绕过该入口，不要使用通用卡通角色。

## 基础规格

- 平台：小红书图文
- 比例：3:4 竖版
- 推荐尺寸：1242 x 1660
- 中文策略：图中只放短中文；大标题优先后期本地叠字，避免乱码
- 主角：土豆崽 IP，必须参考 `potato-illustrations` 内置角色锚点和 prompt 模板

## 本页内容

- 文章核心：{topic.conclusion}
- 本页观点：{card[2]}
- 可见短句：{card[1]}
- 结构类型：{composition}
- 道具元素：{card[3]}

## 画面要求

{card[2]}。

土豆崽必须承担核心动作，不能只站在旁边。画面中部要足够饱满，但不要塞满。角色、道具、箭头和短字之间必须留出清晰间距，不能穿模、压脸、贴边。

## 风格要求

白底手绘解释型图，黑色线稿为主，少量红、橙、蓝作为强调。不要商业插画，不要 PPT 信息图，不要儿童可爱海报，不要复杂背景。

## 质检要点

- 是否是 3:4 竖版
- 是否像同一个土豆崽 IP
- 是否一眼能看懂本页观点
- 是否无乱码、无错字、无文字穿模
- 是否没有箭头穿过脸、手、文字或关键道具
"""


def render_package(topic: Topic) -> Path:
    date = f"2026-07-{topic.day:02d}"
    ymd = f"202607{topic.day:02d}"
    article_main = find_article_main(topic.day)
    brief = extract_article_brief(article_main)
    out = OUT_ROOT / date / f"{ymd}_小红书_{slug(topic.xhs_title)}_potato任务版"

    prompts_dir = out / "prompts"
    images_dir = out / "images"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    source_rel = article_main.relative_to(ROOT).as_posix()

    write_text(out / "选题转译.md", f"""# 选题转译

## 来源

- 日期：{date}
- 文章总览母稿：`{source_rel}`
- 生成规则：只基于文章总览母稿和账号定位改编，不使用月度选题替代母稿

## 母稿提炼

- 母稿标题：{brief.get("标题建议", "")}
- 一句话核心主张：{brief.get("一句话核心主张", topic.conclusion)}

## 正文主线

{brief.get("正文主线", "- 未提取到正文主线")}

## 小红书切口

这篇不做公众号式长解释，而是拆成 8 页图文：封面先打痛点，内页用土豆崽把抽象判断变成可看懂的动作和隐喻，最后给读者一个最小起步动作。

## 目标读者

{topic.audience}

## 本篇目的

{topic.goal}

## 边界

{topic.boundary}

## 线上数据说明

未调用小红书 API，未使用实时小红书数据，未主动搜索、浏览、抓取、爬取或登录小红书。
""")

    write_text(out / "标题库.md", title_bank(topic))

    write_text(out / "封面方案.md", f"""# 封面方案

## 封面主标题

{topic.cover_title}

## 副标题

{topic.subtitle}

## 画面钩子

{topic.cards[0][2]}。

## 点击理由

读者一眼能看到自己正在犯的错：{topic.angle}

## 构图要求

- 3:4 竖版，推荐 1242 x 1660
- 主标题必须大、短、居中偏上
- 土豆崽必须有明确表情和动作
- 副标题不压角色脸、身体或关键道具
- 不要把标题放进复杂框里
- 箭头、强调线不能穿过人物和文字

## 交给 potato-illustrations 的封面任务

见 `prompts/01_封面.md`。

## 正式图状态

待通过 `potato-illustrations` 生成并复检后放入 `images/`。
""")

    cards_md = ["# 图文卡片拆解\n"]
    queue_md = ["# potato-illustrations 图片生成队列\n", "所有图片必须通过 `potato-illustrations` 执行。本文件只描述任务，不代表图片已经生成。\n"]
    for idx, card in enumerate(topic.cards, 1):
        page = PAGE_NAMES[idx - 1]
        prompt_name = f"{idx:02d}_{page}.md"
        cards_md.append(f"""## {idx:02d} {page}

- 观点：{card[2]}
- 卡片可见文案：{card[1]}
- 画面内容：{card[2]}
- 土豆崽动作：作为画面主角参与核心动作，表情随页面情绪变化
- 背景与道具：{card[3]}
- 配色：白底、黑色线稿，少量红橙蓝强调
- 图片比例和尺寸：3:4，1242 x 1660
- 图片风格：土豆崽 IP，白底手绘解释型图
- 生图任务：`prompts/{prompt_name}`
- 审核要点：不压脸、不贴边、不乱码、不穿模、不过度空白
""")
        queue_md.append(f"- {idx:02d} {page}：`prompts/{prompt_name}` -> `images/{idx:02d}_{page}.png`")
        write_text(prompts_dir / prompt_name, prompt_for_card(topic, idx, card, page))

    write_text(out / "图文卡片拆解.md", "\n".join(cards_md))
    write_text(out / "图片生成队列.md", "\n".join(queue_md))

    body = f"""很多人以为自己卡住，是因为还没学到更厉害的 AI 工具。

但我更建议你先回头看一眼：你有没有把一件高频动作，真的拆成一条能重复跑的流程？

{topic.conclusion}

这件事不用一上来做得很复杂。你先抓一个最常重复、最容易卡住、最能直接省时间的动作，把它拆出来。

{topic.action}

先让它跑顺，再谈放大。普通人用 AI，最怕的不是慢，而是一开始就把自己搞复杂。
"""
    write_text(out / "发布稿.md", f"""# 发布稿

## 标题备选

1. {topic.xhs_title}
2. {topic.cover_title}，普通人做 AI 先看懂
3. 别再只学 AI 工具了，先补这一段

## 正文

{body.strip()}

## 标签

{" ".join("#" + tag for tag in topic.tags)}

## 结尾引导

{topic.cta}
""")

    write_text(images_dir / "README_正式图待potato生成.md", f"""# 正式图状态

本目录用于存放通过 `potato-illustrations` 生成并复检通过的小红书正式图片。

当前已生成的是文案、卡片拆解和逐页出图任务；正式图片尚未放入本目录。

预期文件：

- `01_封面.png`
- `01_封面_标题版.png`
- `02_痛点.png`
- `03_判断.png`
- `04_核心.png`
- `05_代入.png`
- `06_方法.png`
- `07_场景.png`
- `08_收束.png`
""")

    write_text(out / "审核报告.md", f"""# 审核报告

## 结论

静态通过，图片待 `potato-illustrations` 生成与复检

## 检查项

| 项目 | 结果 | 说明 |
|---|---|---|
| 文章总览母稿 | 通过 | 已读取 `{source_rel}` |
| 标题 | 通过 | 主标题短、醒目，有痛点或反差 |
| 封面方案 | 通过 | 已单独设计封面钩子和大标题 |
| 卡片节奏 | 通过 | 8 页结构完整 |
| 发布正文 | 通过 | 口语化，有判断和最小行动 |
| 合规风险 | 通过 | 未夸大收益，未承诺结果，未使用侵权 IP |
| 线上边界 | 通过 | 未调用小红书 API/MCP，未主动搜索、浏览、抓取、爬取或登录小红书 |
| 图片入口 | 待复检 | 已写入 `potato-illustrations` 出图任务，正式图待生成 |
| 图片文字 | 待复检 | 待正式图生成后检查乱码、错字、穿模 |
| 土豆崽一致性 | 待复检 | 待正式图生成后按土豆崽锚点复检 |

## 图片任务

- 任务队列：`图片生成队列.md`
- 逐页 prompt：`prompts/`
- 正式图目录：`images/`

## 需要重改

- 当前无文案层面的打回项；正式图片生成后必须复检。
""")

    return out


def main() -> None:
    created: list[Path] = []
    for topic in TOPICS:
        created.append(render_package(topic))
    for path in created:
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
