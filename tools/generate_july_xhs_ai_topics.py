from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(
    r"C:\Users\Administrator\Desktop\codex_project\social_media\06_运营中心\2026\2026-07\草稿区\小红书\202607_小红书_AI科普对话选题池_stick风"
)

TOPICS = [
    {
        "id": "01",
        "title": "什么是AI",
        "question": "AI到底是什么，它真的是在思考吗？",
        "cover_title": "AI到底是啥",
        "cover_hook": "别把AI想成电子脑",
        "ending_hook": "下一篇你想先拆算法，还是先拆大模型？",
        "summary": "AI不是会思考的电子人，更像一个吃过很多样本、很会猜下一步的超级模仿器。",
        "metaphor": "像一个刷题刷到离谱的实习生",
        "why_it_matters": "看懂AI，才不会把所有自动化都叫人工智能。",
        "pages": [
            {
                "page": "01",
                "role": "封面页",
                "goal": "先打破大众对AI的神秘滤镜，做强钩子。",
                "student": "AI是不是电子大脑？",
                "teacher": "更像超会模仿的学霸。",
                "scene": "学生抱着一个写着AI的发光机器人头，表情紧张；老师把机器人头打开，里面是海量资料、聊天气泡和训练箭头。",
                "background": "纯白底，顶部留大标题区，中间是被拆开的AI象征物。",
                "palette": "黑白主线，红色强调误解，蓝色强调正确理解，少量黄色制造冲击。",
                "icons": "robot head, stacked documents, speech bubbles, training arrows, warning sign",
                "subtitle": "不是电子脑，更像模式模仿器",
            },
            {
                "page": "02",
                "role": "误解页",
                "goal": "摆出最常见误会：AI等于会思考。",
                "student": "它回答得像人，那不就是会想吗？",
                "teacher": "像，不等于真在脑内开会。",
                "scene": "左边是学生把AI当成小脑人膜拜，右边老师指着“输入-模式-输出”的三段结构。",
                "background": "左右对比构图，左红右蓝。",
                "palette": "红蓝强对比，角色保持绿色学生、蓝色老师。",
                "icons": "brain icon, input box, pattern grid, output arrow",
                "subtitle": "像会想，不等于真在思考",
            },
            {
                "page": "03",
                "role": "拆解页",
                "goal": "给出一句极简定义。",
                "student": "那AI到底在干嘛？",
                "teacher": "它在根据学过的东西，猜你下一秒想要啥。",
                "scene": "老师拿着放大镜看大量文本、图片、语音样本，最终汇成一个输出框。",
                "background": "中轴流程图，但只保留3个大块：看数据、找规律、给答案。",
                "palette": "蓝黄为主，弱化技术压迫感。",
                "icons": "text sheet, photo icon, waveform icon, magnifier, output box",
                "subtitle": "吃过样本，再按规律给答案",
            },
            {
                "page": "04",
                "role": "比喻页",
                "goal": "用生活比喻讲透概念。",
                "student": "说人话版呢？",
                "teacher": "像把全网题库背熟的实习生，快，但不一定真懂。",
                "scene": "学生递来题目，老师身后的“AI实习生”飞快翻资料然后秒答。",
                "background": "办公室小场景，背景极简。",
                "palette": "白底，蓝绿主色，黄色用于题库和灯泡。",
                "icons": "exam paper, light bulb, speed lines, folder stack",
                "subtitle": "像背熟题库的实习生",
            },
            {
                "page": "05",
                "role": "价值页",
                "goal": "告诉用户知道这个概念有什么实际用。",
                "student": "懂这个有啥用？",
                "teacher": "至少下次别人吹AI时，你不会当场被词儿镇住。",
                "scene": "左边是被术语轰炸的学生，右边是拿着“先看是不是模式识别”小卡片的冷静学生。",
                "background": "错 vs 对的双栏结构。",
                "palette": "左红右绿，底部留CTA区。",
                "icons": "bombarding chat bubbles, checklist card, shield icon",
                "subtitle": "先判断它是不是模式识别",
            },
            {
                "page": "06",
                "role": "结尾页",
                "goal": "收束判断，拉评论互动。",
                "student": "所以AI没那么玄？",
                "teacher": "玄的是包装，不是底层逻辑。",
                "scene": "学生恍然大悟，老师把“神秘滤镜”四个字撕掉。",
                "background": "白底，底部留评论引导条。",
                "palette": "蓝绿收口，整体更轻松。",
                "icons": "broken mystery mask, check mark, comment bubble",
                "subtitle": "别先被名词气势吓住",
            },
        ],
    },
    {
        "id": "02",
        "title": "什么是算法",
        "question": "算法是不是一堆很难的数学公式？",
        "cover_title": "算法不是玄学",
        "cover_hook": "它本质就是做题步骤",
        "ending_hook": "你还想看“算法推荐你内容”这件事怎么发生的吗？",
        "summary": "算法本质上是一套解决问题的步骤，不神秘，神秘的是包装它的人。",
        "metaphor": "像菜谱和做菜顺序",
        "why_it_matters": "不懂算法，就很容易把任何系统推荐都理解成黑箱魔法。",
        "pages": [
            {
                "page": "01",
                "role": "封面页",
                "goal": "把“算法=神秘高数”这个印象打掉。",
                "student": "算法是不是数学怪兽？",
                "teacher": "很多时候它只是流程写清楚。",
                "scene": "左边是怪兽版“算法”吓学生，右边老师端着一张简化菜谱。",
                "background": "白底，上标题，下方强对比。",
                "palette": "红色怪兽，蓝色老师，黄色菜谱。",
                "icons": "monster icon, recipe card, arrow sign, alert mark",
                "subtitle": "很多算法，本质就是步骤",
            },
            {
                "page": "02",
                "role": "误解页",
                "goal": "抛出常见误会。",
                "student": "不写公式就不算算法吧？",
                "teacher": "煮泡面那套步骤，严格点写，也叫算法。",
                "scene": "学生盯着满屏公式，老师指向“烧水-下面-调味”三步。",
                "background": "公式云和三步流程并列。",
                "palette": "黑白主线，红蓝对照。",
                "icons": "formula cloud, kettle, noodle bowl, step numbers",
                "subtitle": "不是只有公式才叫算法",
            },
            {
                "page": "03",
                "role": "定义页",
                "goal": "给出最朴素定义。",
                "student": "那算法到底是什么？",
                "teacher": "就是让机器按步骤处理问题的一套规则。",
                "scene": "老师把乱糟糟的问题球塞进步骤机器，出来一个结果盒子。",
                "background": "三段流程，简洁粗线条。",
                "palette": "蓝黄主色。",
                "icons": "gear, checklist, input ball, output box",
                "subtitle": "机器按规则一步步处理问题",
            },
            {
                "page": "04",
                "role": "比喻页",
                "goal": "用做菜比喻降低门槛。",
                "student": "说白了像啥？",
                "teacher": "像菜谱。菜名是目标，步骤才是算法。",
                "scene": "厨房里学生拿着西红柿炒蛋成品，老师举菜谱对比。",
                "background": "简化厨房场景。",
                "palette": "黄红点缀，保持清爽。",
                "icons": "recipe card, tomato, egg, numbered arrows",
                "subtitle": "菜名是目标，步骤才是算法",
            },
            {
                "page": "05",
                "role": "应用页",
                "goal": "连接日常使用场景。",
                "student": "那推荐视频也靠它？",
                "teacher": "对，你每一次停留，都是在给算法喂偏好。",
                "scene": "手机屏幕不断吐出视频卡片，学生疯狂滑动，算法小齿轮在背后记录。",
                "background": "手机+齿轮大符号。",
                "palette": "蓝绿主色，红色提示“别上头”。",
                "icons": "phone screen, video cards, gear, heart, clock",
                "subtitle": "你的停留，就是给算法喂偏好",
            },
            {
                "page": "06",
                "role": "结尾页",
                "goal": "收尾并引出下一步。",
                "student": "原来算法没我想的高冷。",
                "teacher": "高冷的是名字，实际很多就是流程表。",
                "scene": "学生把“算法恐惧”垃圾桶扔掉。",
                "background": "白底+评论钩子栏。",
                "palette": "绿蓝收尾。",
                "icons": "trash bin, fear label, comment bubble, check mark",
                "subtitle": "名字吓人，底层不一定复杂",
            },
        ],
    },
    {
        "id": "03",
        "title": "算法怎么工作",
        "question": "算法是怎么一步一步算出结果的？",
        "cover_title": "算法怎么跑",
        "cover_hook": "不是啪一下就有答案",
        "ending_hook": "下篇你想看模型和算法有什么区别吗？",
        "summary": "算法工作不是一跳到答案，而是按输入、判断、处理、输出的节奏逐步推进。",
        "metaphor": "像导航在每个路口都做选择",
        "why_it_matters": "理解算法流程，才能看懂为什么同样输入会得到不同结果。",
        "pages": [
            {
                "page": "01",
                "role": "封面页",
                "goal": "强调算法是过程，不是魔术。",
                "student": "它咋一秒就出结果？",
                "teacher": "你看到的是一秒，背后是好多步。",
                "scene": "学生看着答案突然弹出，老师揭开地板，下面是一串齿轮和路口。",
                "background": "白底，中间纵向路径。",
                "palette": "黑白底，黄色路径，蓝色老师。",
                "icons": "answer pop-up, gears, crossroads sign, footsteps",
                "subtitle": "答案快，不代表过程不存在",
            },
            {
                "page": "02",
                "role": "问题页",
                "goal": "抛出核心困惑。",
                "student": "它是不是直接猜的？",
                "teacher": "不是直接瞎猜，是按规则一路筛。",
                "scene": "左边是胡乱抓答案，右边是有序分拣传送带。",
                "background": "左右错对对比。",
                "palette": "红错蓝对。",
                "icons": "random grab hand, conveyor belt, filter icon, arrow",
                "subtitle": "不是乱猜，是一路筛选",
            },
            {
                "page": "03",
                "role": "流程页",
                "goal": "画出算法四步：输入-判断-处理-输出。",
                "student": "你给我最短流程版。",
                "teacher": "先拿输入，再做判断，然后处理，最后吐结果。",
                "scene": "四个巨型模块拼成一条流水线。",
                "background": "中轴四宫格。",
                "palette": "蓝黄绿分层。",
                "icons": "input tray, decision sign, gear, output box",
                "subtitle": "输入-判断-处理-输出",
            },
            {
                "page": "04",
                "role": "比喻页",
                "goal": "用导航比喻解释多步判断。",
                "student": "生活里像啥？",
                "teacher": "像导航，每个路口都在决定左拐还是直走。",
                "scene": "学生开车，导航老师在屏幕里指路，多个岔路口亮起。",
                "background": "道路地图极简场景。",
                "palette": "蓝色道路，黄色路牌。",
                "icons": "map pin, route line, left-right sign, car icon",
                "subtitle": "每个路口都在做判断",
            },
            {
                "page": "05",
                "role": "误差页",
                "goal": "解释为什么结果不一定总完美。",
                "student": "那它怎么还会翻车？",
                "teacher": "因为前面规则、数据、判断，哪一层歪了都能带偏。",
                "scene": "路径前半段有一块歪掉的路牌，后面结果冲进坑里。",
                "background": "路径失误对结果的可视化。",
                "palette": "红色坑，蓝色主路径。",
                "icons": "tilted sign, warning triangle, pit, broken arrow",
                "subtitle": "前面一层歪，后面都可能偏",
            },
            {
                "page": "06",
                "role": "结尾页",
                "goal": "收束为一个判断。",
                "student": "懂了，算法像过程表。",
                "teacher": "对，机器不是顿悟，是流程跑完。",
                "scene": "学生拿到“流程感”钥匙。",
                "background": "白底，留评论引导。",
                "palette": "绿蓝收尾。",
                "icons": "key, checklist, comment bubble, finish flag",
                "subtitle": "不是顿悟，是流程跑完",
            },
        ],
    },
]


GENERIC_TOPICS = [
    ("04", "什么是模型", "模型和算法到底差在哪？", "模型像学会经验的脑回路，不是单纯步骤表。", "像训练后的答题手感"),
    ("05", "什么是大模型", "为什么现在大家都在讲大模型？", "大模型是参数更多、见识更广、泛化更强的模型。", "像见过海量题型的总复习王"),
    ("06", "什么是训练", "AI训练到底在练什么？", "训练是在不断调参数，让模型少犯错。", "像老师一遍遍批改作业"),
    ("07", "什么是推理", "AI回答问题时到底在做什么？", "推理是模型用学过的能力，当场生成结果。", "像考试现场作答"),
    ("08", "什么是提示词", "提示词为什么能影响AI回答？", "提示词像你给实习生下指令，指令乱，结果就飘。", "像下任务单"),
    ("09", "什么是上下文窗口", "AI为什么聊着聊着就忘了前面？", "上下文窗口决定它一次能带多少信息进考场。", "像考试桌面能摊开的资料"),
    ("10", "什么是多模态", "AI为什么现在又能看图又能听音？", "多模态就是同一个系统能处理多种输入。", "像一个人同时会看图听话读字"),
    ("11", "什么是RAG", "RAG为什么总和知识库绑在一起？", "RAG是先查资料，再组织回答。", "像开卷答题"),
    ("12", "什么是向量数据库", "向量数据库里到底存的是什么？", "它存的是便于相似检索的向量表示。", "像按气味和感觉整理的图书馆"),
    ("13", "什么是Embedding", "Embedding为什么叫向量化？", "Embedding是把内容变成机器可比较的坐标。", "像给信息贴上空间坐标"),
    ("14", "什么是Agent", "Agent和普通聊天机器人差在哪？", "Agent不只是会说，还会拆任务、调工具、看结果。", "像会自己跑腿的执行助理"),
    ("15", "什么是智能体", "智能体为什么不只是会聊天？", "智能体强调感知、决策、行动闭环。", "像带耳朵和手脚的系统"),
    ("16", "Agent怎么工作", "Agent为什么能自己拆任务？", "Agent靠目标、计划、工具、反馈组成循环。", "像项目经理带着工具箱干活"),
    ("17", "什么是工作流", "工作流和智能体是不是一回事？", "工作流更像固定流程，智能体更像会临场判断。", "像菜单套餐和自由点单"),
    ("18", "什么是MCP", "MCP为什么突然这么火？", "MCP是让模型更标准地接外部工具和资源。", "像给AI装统一插座"),
    ("19", "什么是Tool Use", "AI调工具和直接回答有什么差别？", "Tool Use是让模型别只靠嘴，必要时真去查真去算。", "像会自己翻计算器的人"),
    ("20", "什么是Function Calling", "函数调用是不是给AI装手脚？", "Function Calling是把模型输出变成结构化动作请求。", "像让AI学会按格式派单"),
    ("21", "什么是Harness", "Harness到底是测试框架还是控制系统？", "Harness更像把模型、任务、工具和评估拴在一起的实验工位。", "像给AI搭的测试台"),
    ("22", "什么是评测", "AI评测为什么不能只看感觉？", "评测是把好坏变成可重复比较的标准。", "像考试评分表"),
    ("23", "什么是幻觉", "AI幻觉到底是胡说还是机制问题？", "幻觉是模型生成了看似合理但不真实的内容。", "像很自信但答错的同学"),
    ("24", "什么是微调", "微调是不是给模型补课？", "微调是在已有模型上做定向强化。", "像给学霸报专项班"),
    ("25", "什么是AI应用层", "真正赚钱的AI应用层到底在哪？", "应用层是把底层能力包装成用户愿意付费的产品。", "像把发动机装成能卖的车"),
]


BASE_PROMPT = (
    "A bold original cartoon explainer illustration in a stick-figure finance-thumbnail style, "
    "white background, thick black outlines, flat bright colors, simple round-head characters, "
    "exaggerated expression, strong metaphor, clean composition, highly readable, playful but sharp, "
    "no watermark, leave space for local title overlay, do not render long Chinese text."
)


def ensure_topic(topic: dict) -> dict:
    enriched = dict(topic)
    enriched.setdefault("style", "stick-comic-skill")
    enriched.setdefault("ratio", "3:4")
    enriched.setdefault("teacher_name", "老师")
    enriched.setdefault("student_name", "学生")
    return enriched


def build_generic_pages(title: str, question: str, summary: str, metaphor: str, ending_hook: str) -> list[dict]:
    return [
        {
            "page": "01",
            "role": "封面页",
            "goal": "做出强标题和强冲突，先吸引点击。",
            "student": f"{title}很难懂吧？",
            "teacher": "没那么玄，我给你拆白。",
            "scene": f"学生被巨大的“{title}”招牌压住，老师把招牌拆成几个简单模块。",
            "background": "纯白底，顶部大标题区，中部主冲突。",
            "palette": "黑白主线，红色代表误解，蓝色代表正确理解，黄色做吸睛点。",
            "icons": "warning sign,拆解箭头, module blocks, question mark",
            "subtitle": "先别被名字吓住",
        },
        {
            "page": "02",
            "role": "提问页",
            "goal": "抛出用户最真实的问题。",
            "student": question,
            "teacher": "你不是一个人，很多人都卡在这儿。",
            "scene": "学生头上冒出大问号和错误联想图标，老师准备纠偏。",
            "background": "白底，左边误解符号，右边老师站位。",
            "palette": "红蓝对比。",
            "icons": "question mark, wrong idea bubble, alert icon",
            "subtitle": "先把最常见误解摆出来",
        },
        {
            "page": "03",
            "role": "定义页",
            "goal": "给出一句最短定义。",
            "student": "那你一句话说明白。",
            "teacher": summary,
            "scene": f"老师把“{title}”拆成3个关键块，学生在旁边记笔记。",
            "background": "中轴三段式结构。",
            "palette": "蓝黄主色，保持轻松。",
            "icons": "three blocks, note card, pointer, key symbol",
            "subtitle": "一句话先讲清它是什么",
        },
        {
            "page": "04",
            "role": "比喻页",
            "goal": "用生活比喻降低理解成本。",
            "student": "再来个说人话版。",
            "teacher": f"你就把它想成{metaphor}。",
            "scene": f"把“{title}”转成一个生活化隐喻场景，学生一下听懂。",
            "background": "极简生活场景，避免复杂背景。",
            "palette": "蓝绿加一点黄色。",
            "icons": "metaphor object, light bulb, arrow sign",
            "subtitle": "换成生活比喻就好懂了",
        },
        {
            "page": "05",
            "role": "价值页",
            "goal": "告诉用户懂这个有什么用。",
            "student": "懂它以后能干嘛？",
            "teacher": "至少能少被术语和概念牵着鼻子走。",
            "scene": "左边是被概念牵着跑，右边是拿到判断框架后的稳定状态。",
            "background": "错对双栏，底部留总结位。",
            "palette": "左红右绿，蓝色结构线。",
            "icons": "chain, shield, framework card, check mark",
            "subtitle": "知道它，才不容易被术语带偏",
        },
        {
            "page": "06",
            "role": "结尾页",
            "goal": "收束理解并引导互动。",
            "student": "行，这回我真懂了。",
            "teacher": ending_hook,
            "scene": "学生拿到一个写着“懂了”的通关卡，老师指向评论区。",
            "background": "纯白底，底部留互动条。",
            "palette": "蓝绿收尾。",
            "icons": "pass card, comment bubble, finish flag",
            "subtitle": "这回先懂个大概就够了",
        },
    ]


for tid, title, question, summary, metaphor in GENERIC_TOPICS:
    TOPICS.append(
        {
            "id": tid,
            "title": title,
            "question": question,
            "cover_title": title,
            "cover_hook": summary[:14],
            "ending_hook": f"还想继续拆“{title}”的进阶用法吗？",
            "summary": summary,
            "metaphor": metaphor,
            "why_it_matters": f"看懂“{title}”，后面很多AI术语都会顺下来。",
            "pages": build_generic_pages(title, question, summary, metaphor, f"还想继续拆“{title}”的进阶用法吗？"),
        }
    )


def build_analysis(topic: dict) -> str:
    return f"""# {topic['id']}_{topic['title']} 分析

## 主题定位
- 主题：{topic['title']}
- 核心问题：{topic['question']}
- 目标：让完全不懂AI的人也能在6页内看懂
- 形式：学生提问 + 老师通俗幽默回答
- 风格：{topic['style']}

## 核心判断
{topic['summary']}

## 用户为什么会点开
- 封面先解决误解
- 标题直接说人话
- 对话代替讲课，阅读负担低

## 用户为什么该看完
- 中间有生活比喻
- 每页只讲一个判断
- 结尾能自然引出下一篇

## 这篇最该避免
- 把定义写成教科书
- 一页塞太多术语
- 画面变成抽象流程图海报
"""


def build_storyboard(topic: dict) -> str:
    lines = [f"# {topic['id']}_{topic['title']} 分镜", ""]
    for page in topic["pages"]:
        lines.extend(
            [
                f"## {page['page']} {page['role']}",
                f"- 页面任务：{page['goal']}",
                f"- 学生：{page['student']}",
                f"- 老师：{page['teacher']}",
                f"- 画面：{page['scene']}",
                f"- 背景：{page['background']}",
                f"- 配色：{page['palette']}",
                f"- 辅助icon：{page.get('icons', '无')}",
                f"- 短字幕：{page.get('subtitle', '无')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_characters(topic: dict) -> str:
    return f"""# 角色设定

## 学生
- 身份：普通用户 / 初学者
- 语气：疑问强，担心听不懂
- 外观：绿色上衣，圆头火柴人，表情更夸张

## 老师
- 身份：懂AI但不端着讲的人
- 语气：短句、通俗、带一点幽默
- 外观：蓝色上衣，圆头火柴人，动作更稳定

## 统一要求
- 全套只保留这两个角色
- 不能每页长得像新角色
- 背景极简，主角和符号先于细节
- 文字后期本地排，不依赖模型直接生成中文

## 本篇情绪节奏
- 开头：困惑
- 中段：拆解
- 后段：理解
- 结尾：松一口气 + 想继续看
"""


def build_publish_md(topic: dict) -> str:
    return f"""# 发布稿

## 标题候选
1. {topic['cover_title']}：{topic['summary']}
2. {topic['title']}，其实没你想得那么玄
3. {topic['title']}，我用6页给你讲人话版

## 封面钩子
{topic['cover_hook']}

## 正文短文案
很多人一听到“{topic['title']}”就自动脑补成高深黑箱，其实没必要。  
这篇我只做一件事：把它讲成人话。  

## 结尾互动
{topic['ending_hook']}

## 标签建议
#AI科普 #AI入门 #人工智能 #小白学AI #AI知识
"""


def build_draft_txt(topic: dict) -> str:
    return (
        f"{topic['title']}其实没那么玄。\n"
        f"这篇用6张图，把“{topic['question']}”拆成人话。\n"
        f"{topic['summary']}\n\n"
        f"{topic['ending_hook']}\n"
    )


def build_image_plan(topic: dict) -> str:
    lines = [
        "# 配图方案",
        "",
        f"- 风格：{topic['style']}",
        "- 比例：3:4",
        "- 文字策略：图片只留短钩子和气泡位，长中文统一后期本地排版",
        "- 统一人物：学生绿色、老师蓝色，整套保持同一脸型和线条粗细",
        "",
    ]
    for page in topic["pages"]:
        lines.extend(
            [
                f"## {page['page']} {page['role']}",
                f"- 任务：{page['goal']}",
                f"- 画面内容：{page['scene']}",
                f"- 背景：{page['background']}",
                f"- 配色：{page['palette']}",
                f"- 辅助icon：{page.get('icons', '无')}",
                f"- 短字幕：{page.get('subtitle', '无')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_metadata(topic: dict) -> dict:
    return {
        "platform": "小红书",
        "month": "2026-07",
        "series": "AI科普对话选题池",
        "style": topic["style"],
        "topic_id": topic["id"],
        "title": topic["title"],
        "question": topic["question"],
        "cover_title": topic["cover_title"],
        "cover_hook": topic["cover_hook"],
        "ending_hook": topic["ending_hook"],
        "page_count": len(topic["pages"]),
        "pages": topic["pages"],
    }


def build_prompt(topic: dict, page: dict) -> str:
    is_cover = page["page"] == "01"
    scene_type = "wrong vs right" if is_cover else "dialogue explainer"
    return (
        f"{BASE_PROMPT}\n\n"
        f"Main topic: {topic['title']}\n"
        f"Core judgment: {topic['summary']}\n"
        f"Scene type: {scene_type}\n"
        f"Character 1: confused learner in green shirt, round head stick figure, expressive eyebrows\n"
        f"Character 2: calm guide in blue shirt, round head stick figure, pointing and explaining\n"
        f"Page role: {page['role']}\n"
        f"Goal: {page['goal']}\n"
        f"Scene: {page['scene']}\n"
        f"Background: {page['background']}\n"
        f"Color palette: {page['palette']}\n"
        f"Support icons: {page.get('icons', 'simple arrows and symbols only')}\n"
        f"Subtitle intent: {page.get('subtitle', 'one short explanatory caption only')}\n"
        f"Composition: portrait 3:4, clear top title area, one central visual conflict, 2 to 4 oversized supporting icons around the main metaphor, reserve one small clean subtitle strip area under the title, minimal clutter, mobile readable\n"
        f"Text rule: do not render any readable letters, words, English, or Chinese in the image; only reserve clean empty areas for later local subtitle and speech-bubble typography\n"
    )


def write_topic(topic: dict) -> None:
    topic = ensure_topic(topic)
    topic_dir = ROOT / f"{topic['id']}_{topic['title']}"
    prompts_dir = topic_dir / "prompts"
    images_dir = topic_dir / "images"
    topic_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    (topic_dir / "analysis.md").write_text(build_analysis(topic), encoding="utf-8")
    (topic_dir / "storyboard.md").write_text(build_storyboard(topic), encoding="utf-8")
    (topic_dir / "characters.md").write_text(build_characters(topic), encoding="utf-8")
    (topic_dir / "发布稿.md").write_text(build_publish_md(topic), encoding="utf-8")
    (topic_dir / "草稿箱正文.txt").write_text(build_draft_txt(topic), encoding="utf-8")
    (topic_dir / "配图方案.md").write_text(build_image_plan(topic), encoding="utf-8")
    (topic_dir / "metadata.json").write_text(
        json.dumps(build_metadata(topic), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for page in topic["pages"]:
        (prompts_dir / f"{page['page']}_{page['role']}.md").write_text(
            build_prompt(topic, page),
            encoding="utf-8",
        )


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    overview = {
        "month": "2026-07",
        "theme": "AI科普对话选题池",
        "style": "stick-comic-skill",
        "count": len(TOPICS),
        "topics": [
            {"id": topic["id"], "title": topic["title"], "question": topic["question"]}
            for topic in TOPICS
        ],
    }
    (ROOT / "00_选题总表.json").write_text(
        json.dumps(overview, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# 2026年7月小红书 AI科普对话选题总表",
        "",
        "- 形式：学生提问 + 老师通俗幽默回答",
        "- 风格：stick-comic-skill",
        f"- 数量：{len(TOPICS)}个",
        "",
    ]
    for topic in TOPICS:
        lines.append(f"- {topic['id']}. {topic['title']}：{topic['question']}")
    (ROOT / "00_选题总表.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for topic in TOPICS:
        write_topic(topic)


if __name__ == "__main__":
    main()
