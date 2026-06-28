$ErrorActionPreference = "Stop"

$root = "C:\Users\Administrator\Desktop\codex_project\social_media"
$baseDir = Join-Path $root "06_运营中心\2026\2026-07\草稿区\公众号"
$jsonPath = Join-Path $root "tools\july_wechat_topics_202607.json"
$items = Get-Content -LiteralPath $jsonPath -Raw | ConvertFrom-Json

function Ensure-Dir([string]$Path) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Write-Utf8File([string]$Path, [string[]]$Lines) {
    [System.IO.File]::WriteAllText($Path, ($Lines -join "`r`n"), [System.Text.UTF8Encoding]::new($false))
}

foreach ($item in $items) {
    $dir = Join-Path $baseDir ("{0}_公众号_{1}" -f $item.date, $item.slug)
    $prompts = Join-Path $dir "prompts"
    $images = Join-Path $dir "images"
    Ensure-Dir $dir
    Ensure-Dir $prompts
    Ensure-Dir $images

    $body = @(
        "# $($item.title)",
        "",
        "很多人第一次看到“$($item.keyword)”这个词，第一反应不是“它到底在解决什么问题”，而是“这是不是又一个离普通人很远的 AI 术语”。",
        "",
        "这其实很正常。",
        "",
        "因为现在网上关于 AI 的内容，很多都在讲名词、讲趋势、讲工具更新，但真正能帮普通创作者、个体经营者和轻创业人群把事情做成的，往往不是这些热闹，而是把概念翻译成能落地的判断。",
        "",
        "今天这篇，我就只讲一件事：",
        "",
        "**$($item.core)。**",
        "",
        "## 一、先别急着背定义，先看它到底在解决什么",
        "",
        "如果把 $($item.keyword) 讲得尽量直白一点，它真正重要的地方不是名字，而是它在流程里扮演的作用。",
        "很多 AI 概念看起来很复杂，本质上只是把一段原本模糊的做事逻辑，变成了更清晰的动作结构。",
        "",
        "所以与其问“这个词的标准定义是什么”，不如先问：",
        "",
        "它是在帮我判断什么？",
        "它是在帮我补哪一段流程？",
        "它是在让我少踩哪一种坑？",
        "",
        "## 二、为什么大家最容易把它理解错",
        "",
        "关于 $($item.keyword)，最常见的误解通常是：",
        "",
        "**$($item.misread)**",
        "",
        "这类误解一旦形成，后面学习就会很容易跑偏。",
        "因为你会把注意力放在错误的地方。你以为自己在学 AI，实际上只是被术语牵着走。",
        "",
        "真正更稳的理解方式，是把它看成：",
        "",
        "**$($item.metaphor)。**",
        "",
        "一旦这个角度立住，很多原本看起来很技术的话，就会突然变得非常好懂。",
        "",
        "## 三、它和普通人用 AI 的关系到底在哪",
        "",
        "对“土豆学AI”这个账号最核心的人群来说，学 $($item.keyword) 并不是为了显得懂行，而是为了把 AI 从“会聊天的工具”变成“能稳定出结果的工作流”。",
        "",
        "$($item.value)",
        "",
        "这也是为什么我一直不太建议大家只追热点工具、只背新术语。",
        "因为真正拉开差距的，从来不是你知道多少个新词，而是你能不能把这些概念翻译成：",
        "",
        "1. 更清楚的任务判断",
        "2. 更少返工的流程设计",
        "3. 更稳定可复用的结果路径",
        "",
        "## 四、普通人真正更该怎么学",
        "",
        "我更建议的顺序，一直都不是“先把最难的研究明白”，而是：",
        "",
        "1. 先搞懂这个概念在解决什么问题",
        "2. 再搞懂它适合放在流程里的哪一步",
        "3. 最后再决定自己要不要继续深挖",
        "",
        "这个顺序看起来没那么炫，但非常适合普通人。",
        "因为它能让你先用起来，再逐步理解，而不是一开始就被复杂名词劝退。",
        "",
        "## 最后一句",
        "",
        "如果一个 AI 概念不能帮你更快判断任务、更稳搭流程、更少返工，那它对你现在阶段的意义就不会太大。",
        "而 $($item.keyword) 这件事，真正值得学的地方，就在这里。"
    )

    $plan = @(
        "# 配图方案",
        "",
        "## 封面",
        "- 文件：`01_公众号封面.png`",
        "- Hook：`$($item.hook)`",
        "- 画面：围绕「$($item.keyword)」做一张白底手绘封面，主角必须是固定土豆 IP，不用小黑。",
        "",
        "## 正文配图",
        "1. `02_$($item.figure2).png`",
        "2. `03_$($item.figure3).png`",
        "3. `04_$($item.figure4).png`",
        "4. `05_$($item.figure5).png`",
        "",
        "## 风格要求",
        "- 使用 `ian-xiaohei-illustrations` 的白底手绘正文图逻辑",
        "- 角色必须替换为固定土豆 IP",
        "- 统一参考头像 01 版：土黄色、黑粗眉、冷静眼神、轻微麻点、不要萌化",
        "- 每张图只讲一个判断，不做 PPT 卡片，不堆箭头，不做复杂信息图"
    )

    $metadata = [ordered]@{
        platform = "wechat"
        date = $item.date
        status = "draft_local"
        type = "image_article"
        account_name = "土豆学AI"
        title = $item.title
        topic_line = "AI科普认知"
        body_file = "发布稿.md"
        cover_hook = $item.hook
        image_files = @(
            "01_公众号封面.png",
            ("02_{0}.png" -f $item.figure2),
            ("03_{0}.png" -f $item.figure3),
            ("04_{0}.png" -f $item.figure4),
            ("05_{0}.png" -f $item.figure5)
        )
    }

    $potato = "same fixed potato IP as approved avatar version 01, warm light potato yellow, smooth potato silhouette, black thick eyebrows, calm serious eyes, subtle potato pits, clean outline, not cute mascot, not painterly, not realistic human face, consistent character across all images"

    $coverPrompt = @(
        "16:9 horizontal Chinese editorial illustration for WeChat article cover, pure white background, hand-drawn notebook sketch style, inspired by ian xiaohei illustration logic, but protagonist is $potato.",
        "Main subject is about $($item.keyword). One strong focal scene, lots of whitespace, clean black linework, small controlled orange and blue accents, no watermark, no infographic feel.",
        "Chinese handwritten annotations:",
        "- $($item.hook)",
        "- 讲人话",
        "- 能落地"
    )
    $prompt2 = @(
        "16:9 horizontal Chinese article illustration, pure white background, hand-drawn editorial sketch, protagonist is $potato.",
        "Main metaphor should explain: $($item.core)",
        "Chinese handwritten annotations:",
        "- $($item.figure2)",
        "- 先看本质"
    )
    $prompt3 = @(
        "16:9 horizontal Chinese article illustration, pure white background, hand-drawn editorial sketch, protagonist is $potato.",
        "Main metaphor should show the common misunderstanding: $($item.misread)",
        "Chinese handwritten annotations:",
        "- $($item.figure3)",
        "- 别理解偏了"
    )
    $prompt4 = @(
        "16:9 horizontal Chinese article illustration, pure white background, hand-drawn editorial sketch, protagonist is $potato.",
        "Main metaphor should visualize this life analogy: $($item.metaphor)",
        "Chinese handwritten annotations:",
        "- $($item.figure4)",
        "- 用生活比喻讲清"
    )
    $prompt5 = @(
        "16:9 horizontal Chinese article illustration, pure white background, hand-drawn editorial sketch, protagonist is $potato.",
        "Main metaphor should show what ordinary people should learn first: $($item.value)",
        "Chinese handwritten annotations:",
        "- $($item.figure5)",
        "- 先学会判断"
    )

    Write-Utf8File (Join-Path $dir "发布稿.md") $body
    Write-Utf8File (Join-Path $dir "配图方案.md") $plan
    $metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $dir "metadata.json") -Encoding utf8
    Write-Utf8File (Join-Path $prompts "01_公众号封面.md") $coverPrompt
    Write-Utf8File (Join-Path $prompts ("02_{0}.md" -f $item.figure2)) $prompt2
    Write-Utf8File (Join-Path $prompts ("03_{0}.md" -f $item.figure3)) $prompt3
    Write-Utf8File (Join-Path $prompts ("04_{0}.md" -f $item.figure4)) $prompt4
    Write-Utf8File (Join-Path $prompts ("05_{0}.md" -f $item.figure5)) $prompt5
}

Write-Output ("generated {0} wechat article packages" -f $items.Count)
