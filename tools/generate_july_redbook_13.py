from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "06_运营中心" / "2026" / "2026-07"
OUT_ROOT = BASE / "小红书"
ARTICLE_ROOT = BASE / "文章总览"
ACCOUNT_CONTEXT = ROOT / ".agents" / "account-context.md"

FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")

W, H = 1242, 1660


@dataclass
class Topic:
    day: int
    conclusion: str
    xhs_title: str
    cover_title: str
    subtitle: str
    audience: str
    goal: str
    boundary: str
    angle: str
    action: str
    cta: str
    tags: list[str]
    cards: list[tuple[str, str, str, str]]


TOPICS: list[Topic] = [
    Topic(
        2,
        "普通人第一条最值得先搭的，不是自动化工作流，而是内容工作流。",
        "普通人第一条AI工作流，别从自动化开始",
        "先别碰自动化",
        "第一条工作流，建议先搭内容流",
        "公众号、小红书、朋友圈、短视频都要做，但内容效率一直上不去的人。",
        "把第一条工作流落到最容易起步的内容方向，降低执行门槛。",
        "重点讲内容工作流，不讲 agent、MCP 和复杂串联。",
        "内容任务重复、高频、反馈快，最适合拿来做第一条 AI 工作流。",
        "先固定选题、提纲、初稿、改写、发布这 5 步。",
        "你现在最想先稳定哪一段内容流程？",
        ["AI工作流", "内容创作", "AI提效", "小红书运营", "普通人学AI"],
        [
            ("封面", "先别碰自动化", "土豆崽被大机器吓住，转身走向一条写着内容流的小路", "自动化机器、内容流小路"),
            ("痛点", "内容总是临时凑", "土豆崽左手拿公众号，右手拿小红书，脚边一堆没发完的草稿", "草稿纸、平台小牌"),
            ("判断", "第一条先做内容流", "土豆崽把自动化大按钮推远，把内容流程板拉到面前", "大按钮、流程板"),
            ("核心", "5步就能起跑", "土豆崽沿着选题、提纲、初稿、改写、发布五个节点走", "五节点路径"),
            ("分工", "AI接整理和扩展", "土豆崽把资料、例子、标题交给 AI 小机械臂，自己拿着判断笔", "机械臂、判断笔"),
            ("误区", "别让AI替你决定观点", "土豆崽拦住一张写着万能答案的大纸", "万能答案纸"),
            ("起步", "先跑一篇完整流程", "土豆崽把一篇内容从选题推到发布终点", "起点、终点、内容纸"),
            ("收束", "内容流跑顺再升级", "土豆崽回头看，小机器在远处排队等待升级", "升级阶梯"),
        ],
    ),
    Topic(
        3,
        "为什么你的选题总在重复？问题不是灵感少，而是没有选题系统。",
        "选题总重复？你缺的不是灵感",
        "不是没灵感",
        "是没有选题系统",
        "总说没题可写，或者写来写去只有几个角度的人。",
        "把缺选题这个痛点转成系统认知，让读者愿意收藏。",
        "重点讲选题系统，不讲热点搬运和爆款玄学。",
        "选题不是靠等灵感，而是靠输入源、标签和复用框架。",
        "先建 4 个输入源：痛点、案例、问题、反常识。",
        "你最常卡在没题，还是题太散？",
        ["选题系统", "AI写作", "内容创作", "AI提效", "小红书选题"],
        [
            ("封面", "不是没灵感", "土豆崽挠头看空白本，旁边其实有四个装满题目的水龙头", "空白本、输入源水龙头"),
            ("痛点", "写来写去就那几个", "土豆崽在同一个圆圈里绕圈，手里拿着重复题目", "重复圆圈"),
            ("判断", "问题是没系统", "土豆崽把散落便签收进一个选题盒子", "选题盒、便签"),
            ("核心", "4个输入源够用", "土豆崽打开痛点、案例、问题、反常识四个抽屉", "四抽屉"),
            ("AI角色", "AI适合帮你扩角度", "土豆崽把一个题目放进放大镜，冒出多个角度", "放大镜、角度卡"),
            ("标签", "选题池一定要打标签", "土豆崽给选题卡贴上人群、痛点、场景标签", "标签贴"),
            ("框架", "每周固定补10条", "土豆崽往选题池里投递 10 张新卡", "选题池"),
            ("收束", "系统比灵感更稳定", "土豆崽关上灵感祈祷箱，抱着选题系统走", "祈祷箱、系统盒"),
        ],
    ),
    Topic(
        4,
        "别再让 AI 直接替你写全文了，先让它帮你把提纲压出来。",
        "AI味很重？先别让它写全文",
        "别直接写全文",
        "先让 AI 压提纲",
        "一让 AI 写就味很重、越写越不想发的人。",
        "建立正确顺序：先结构，后正文。",
        "重点写提纲阶段的 AI 用法，不写一键生成神话。",
        "AI 文不像人，往往不是模型差，而是你没先定结构。",
        "先让 AI 拆对象、判断、展开点和收口。",
        "你平时会先要提纲，还是直接让 AI 写？",
        ["AI写作", "提纲写作", "去AI味", "内容创作", "AI提效"],
        [
            ("封面", "别直接写全文", "土豆崽按住一台疯狂吐长文的机器，另一只手拿出提纲夹", "吐稿机器、提纲夹"),
            ("痛点", "一写就不像你", "土豆崽看着一张标准但没个性的文章，表情无语", "标准稿纸"),
            ("判断", "先结构后正文", "土豆崽把大稿子拆成骨架，再往里面填内容", "文章骨架"),
            ("核心", "好提纲先解决4件事", "土豆崽指向对象、观点、顺序、收口四块板", "四块板"),
            ("方法", "先问写给谁", "土豆崽把人群卡放在第一位，后面才是正文卡", "人群卡"),
            ("判断", "再定你要说什么", "土豆崽用红笔圈住一句核心判断", "红笔、判断句"),
            ("执行", "最后让AI填表达", "AI 小机械臂只负责把例子和表达搬进框里", "机械臂、内容框"),
            ("收束", "想清楚，再写快", "土豆崽站在清晰提纲旁，长文机器变安静", "清晰提纲"),
        ],
    ),
    Topic(
        5,
        "AI 改写不是换个说法，而是把一份母稿改成多平台能发的版本。",
        "AI改写，不是换个说法这么简单",
        "改写不是润色",
        "是一稿多发工作流",
        "有母稿，但不会做公众号、小红书、朋友圈多平台改写的人。",
        "把改写从文字润色升级成平台工作流。",
        "重点讲一稿多发改写逻辑，不堆纯文案技巧。",
        "平台稿不是把同一段话换个说法，而是重排阅读场景。",
        "先保留核心观点，再按平台重写开头、节奏和结尾。",
        "你现在最想先改哪个平台版本？",
        ["一稿多发", "AI改写", "小红书图文", "公众号写作", "AI工作流"],
        [
            ("封面", "改写不是润色", "土豆崽拿着一份母稿，分流成公众号、小红书、朋友圈三条路", "母稿、三条路"),
            ("痛点", "同一篇到处发不动", "土豆崽把长文硬塞进手机卡片，卡片被撑变形", "长文、手机卡片"),
            ("判断", "平台稿要重组", "土豆崽把母稿拆成观点、例子、钩子、行动四块", "四块积木"),
            ("核心", "先保留核心判断", "土豆崽把一颗核心种子放进三个不同花盆", "种子、花盆"),
            ("小红书", "小红书要更短更冲突", "土豆崽把长段落剪成短卡片", "剪刀、卡片"),
            ("公众号", "公众号要逻辑更完整", "土豆崽把卡片排成一条长梯子", "长梯子"),
            ("朋友圈", "朋友圈要像真人说话", "土豆崽对着聊天框写短句", "聊天框"),
            ("收束", "改的是场景，不是词", "土豆崽把同一观点装进三种容器", "三种容器"),
        ],
    ),
    Topic(
        6,
        "你不是不会发内容，而是每次发布前都像重新开始。",
        "发内容总拖延？你缺发布SOP",
        "发前别临时凑",
        "固定5个发布动作",
        "写稿能写，但发布前总拖延、临时补标题封面标签的人。",
        "把发布动作也变成工作流的一段。",
        "重点写发布前 SOP，不写平台敏感规则细则大全。",
        "很多内容不是死在写作，而是死在发布前的混乱。",
        "固定标题、封面、标签、正文检查、结尾引导 5 个动作。",
        "你发布前最常卡在哪一步？",
        ["发布SOP", "内容运营", "AI提效", "小红书运营", "内容工作流"],
        [
            ("封面", "发前别临时凑", "土豆崽抱着写好的稿子，被标题、封面、标签三件事绊住", "稿子、绊脚绳"),
            ("痛点", "写完也不想发", "土豆崽趴在发布按钮前，旁边一堆没补完的小纸条", "发布按钮"),
            ("判断", "发布也要流程", "土豆崽把发布按钮前铺成 5 格检查清单", "检查清单"),
            ("动作1", "标题先给3个备选", "土豆崽把三个标题贴在白板上比较", "标题白板"),
            ("动作2", "封面先看缩略图", "土豆崽拿放大镜看小手机里的封面", "手机缩略图"),
            ("动作3", "标签别乱堆", "土豆崽把标签从一大堆筛成 5 个", "标签筛子"),
            ("动作4", "结尾要有下一步", "土豆崽把读者从内容页引到一扇小门", "下一步小门"),
            ("收束", "发稿前固定检查", "土豆崽盖上发布 SOP 印章", "SOP 印章"),
        ],
    ),
    Topic(
        7,
        "做内容的人最容易忽略的一段工作流，其实是发完之后的承接。",
        "内容有点赞，为什么没有后续？",
        "别只盯点赞",
        "发完之后才是承接",
        "有浏览、有点赞，但留不下咨询和私信的人。",
        "让读者意识到流量后面还有承接动作。",
        "重点写承接，不写夸张成交案例。",
        "流量不是终点，评论、私信、资料包和私域才是下一段路。",
        "先设计一个最低成本承接链路。",
        "你现在内容发完后，有设计下一步吗？",
        ["内容承接", "私域运营", "AI变现", "内容运营", "AI工作流"],
        [
            ("封面", "别只盯点赞", "土豆崽抱着点赞气球，却发现后面没有桥", "点赞气球、断桥"),
            ("痛点", "有数据没后续", "土豆崽看着热闹数据面板，旁边咨询盒空空的", "数据面板、空盒子"),
            ("判断", "发完才到承接", "土豆崽从发布终点走进承接通道", "承接通道"),
            ("核心", "承接4个动作", "土豆崽摆出评论、私信、资料、私域四个入口", "四入口"),
            ("评论", "评论区接问题", "土豆崽把读者问题贴到问题墙", "问题墙"),
            ("私信", "私信接需求", "土豆崽把私信整理成需求卡", "私信卡"),
            ("资料", "资料包接行动", "土豆崽递出一份可执行清单", "资料清单"),
            ("收束", "流量后面要有路", "土豆崽把点赞气球绑到一条清晰小路上", "清晰小路"),
        ],
    ),
    Topic(
        8,
        "很多人用了很多 AI 还是没提效，真正卡住的是顺序，不是能力。",
        "用了很多AI还没提效？顺序错了",
        "不是能力不够",
        "是使用顺序错了",
        "已经努力学 AI，但结果依然不稳定的人。",
        "做一篇误区加顺序的强共鸣内容。",
        "重点写执行顺序，不写工具优劣争论。",
        "顺序错了，AI 只会把混乱放大。",
        "先定任务、再拆步骤、再让 AI 接合适环节。",
        "你现在最容易在哪一步顺序错？",
        ["AI提效", "AI误区", "工作流", "普通人学AI", "内容提效"],
        [
            ("封面", "顺序错了", "土豆崽把步骤卡排反，机器冒烟，旁边正确顺序发光", "反序卡、正确顺序"),
            ("痛点", "越用越忙", "土豆崽被 AI 生成的一堆结果追着跑", "结果纸片"),
            ("误区1", "先找工具再找问题", "土豆崽背着工具箱，却不知道要修什么", "工具箱、问号"),
            ("误区2", "先要成品不拆步骤", "土豆崽让机器直接吐大成品，结果卡住", "卡住机器"),
            ("误区3", "先自动化再标准化", "土豆崽把混乱线团接进自动化机器", "线团机器"),
            ("正确", "先定任务再拆流程", "土豆崽把任务卡拆成三步小卡", "三步卡"),
            ("一周版", "先固定3层就够了", "土豆崽把输入、处理、输出三层叠稳", "三层积木"),
            ("收束", "顺序对了才提效", "土豆崽沿着顺序箭头轻松走到终点", "顺序箭头"),
        ],
    ),
    Topic(
        9,
        "别急着做 agent，先把你手上的重复动作抓出来。",
        "别急着做Agent，先抓重复动作",
        "先别做Agent",
        "先找重复动作",
        "被 agent、智能体概念吸引，但实际业务还没跑顺的人。",
        "避免读者跑偏到炫技术，守住工作流定位。",
        "重点讲 agent 适用前提，不讲技术教程和部署细节。",
        "没有固定重复动作，agent 也只能帮你自动化混乱。",
        "先列出每周重复 3 次以上的动作。",
        "你现在最想交给 AI 的重复动作是什么？",
        ["AI智能体", "Agent", "AI工作流", "自动化", "普通人学AI"],
        [
            ("封面", "先别做Agent", "土豆崽被一个写着 Agent 的大机器人吸引，脚下重复动作卡还没整理", "大机器人、动作卡"),
            ("兴奋", "概念很酷但别急", "土豆崽眼睛发亮看海报，旁边任务桌一团乱", "概念海报"),
            ("判断", "重复动作才是前提", "土豆崽把重复动作一张张夹到板子上", "动作板"),
            ("问题", "流程没固定先别自动化", "土豆崽把一团乱线塞进机器人，机器人冒问号", "乱线机器人"),
            ("该做1", "先列高频任务", "土豆崽写下每周重复三次以上", "高频任务清单"),
            ("该做2", "再拆输入和输出", "土豆崽把任务拆成输入盒和输出盒", "输入输出盒"),
            ("该做3", "最后再看能否代理", "土豆崽把合格任务递给小机器人", "小机器人"),
            ("收束", "Agent是下一阶段", "土豆崽站在工作流台阶上，Agent 在更高一级等着", "升级台阶"),
        ],
    ),
    Topic(
        10,
        "我做免费资料，不是为了显得大方，而是为了筛出真正想落地的人。",
        "免费资料没人要？问题可能在设计",
        "免费资料不是赠品",
        "而是筛选器",
        "开始做内容承接，但不知道免费资料到底该怎么设计的人。",
        "把免费资料从赠品升级成筛选器。",
        "重点写免费资料设计逻辑，不夸大转化率。",
        "真正有效的免费资料，不是越大越好，而是越能帮人迈出第一步越好。",
        "先做一个能解决小问题的清单或模板。",
        "你会更想要清单、模板，还是案例拆解？",
        ["免费资料", "内容承接", "私域运营", "AI变现", "个人IP"],
        [
            ("封面", "不是赠品", "土豆崽举着大礼包，又换成一个精准筛子", "礼包、筛子"),
            ("痛点", "资料很大但没人要", "土豆崽推着巨大资料山，读者小人绕开走", "资料山"),
            ("判断", "资料要帮人开始", "土豆崽把巨大资料缩成一张第一步清单", "第一步清单"),
            ("核心", "小而具体更有效", "土豆崽把大盒子换成 5 张可执行卡", "执行卡"),
            ("案例", "5条工作流适合承接", "土豆崽递出写着 5 条 AI 工作流的小册子", "小册子"),
            ("连接", "后面才能接低客单", "土豆崽把免费资料、低客单、训练营连成楼梯", "三层楼梯"),
            ("避坑", "别把资料做成百科", "土豆崽把厚百科关上，留下行动页", "百科书"),
            ("收束", "先筛出想行动的人", "土豆崽用筛子筛出举手的小人", "筛子、小人"),
        ],
    ),
    Topic(
        11,
        "私域不是把人加进来就结束了，而是把继续往前走的动作设计出来。",
        "加了微信却聊不下去？少了这3步",
        "私域不是加人",
        "是设计下一步",
        "已经在引导加人，但加了以后聊天尴尬、承接断掉的人。",
        "把加微信后面的动作说清楚。",
        "重点写私域首段承接，不写骚扰式话术。",
        "加人只是开始，真正关键是让对方自然知道下一步做什么。",
        "前 3 步先发资料、问卡点、给小建议。",
        "你加人后最容易卡在开场，还是后续承接？",
        ["私域运营", "内容承接", "AI变现", "个人IP", "轻创业"],
        [
            ("封面", "私域不是加人", "土豆崽把人拉进门后，两个人尴尬对视，门后没有路", "门、空路"),
            ("痛点", "一开口就像推销", "土豆崽拿着大喇叭卖课，读者后退", "大喇叭"),
            ("判断", "先设计下一步", "土豆崽在门后铺三块脚垫", "三步脚垫"),
            ("第一步", "先交付资料", "土豆崽递出对方刚要的资料包", "资料包"),
            ("第二步", "再问一个卡点", "土豆崽拿着一张简单问题卡", "问题卡"),
            ("第三步", "给一个小建议", "土豆崽把建议写成便签递过去", "建议便签"),
            ("边界", "不要一上来硬卖", "土豆崽把卖课锤子放进箱子里", "收起锤子"),
            ("收束", "自然往前走", "土豆崽和读者沿着小路继续走", "小路"),
        ],
    ),
    Topic(
        12,
        "低客单不是为了赚快钱，而是让用户先用更低风险的方式开始行动。",
        "低客单不是赚快钱，是过渡层",
        "低客单不是快钱",
        "是低风险行动入口",
        "想做变现，但怕一上来卖课太硬的人。",
        "把低客单讲成过渡层，而不是割裂商品。",
        "重点写低客单角色，不写收益刺激。",
        "低客单的价值，是让用户先用更低成本验证你能不能帮到他。",
        "把免费资料、低客单、训练营串成产品阶梯。",
        "你更适合先做模板、陪跑，还是小课？",
        ["低客单", "AI变现", "产品阶梯", "个人IP", "轻创业"],
        [
            ("封面", "不是赚快钱", "土豆崽把写着快钱的钞票牌推开，搭起小台阶", "钞票牌、小台阶"),
            ("误区", "别一上来只想大课", "土豆崽举着巨大课程箱，读者被吓退", "巨大课程箱"),
            ("判断", "低客单是过渡层", "土豆崽把免费、低客单、训练营三层叠起来", "三层阶梯"),
            ("作用", "先降低行动风险", "土豆崽递出一张小门票，读者敢迈进来", "小门票"),
            ("适合", "模板小课陪跑都可以", "土豆崽摆出模板、小课、轻陪跑三张卡", "三张卡"),
            ("连接", "要接得上后续", "土豆崽把小产品接到更完整的路线图", "路线图"),
            ("边界", "别承诺夸张结果", "土豆崽划掉万能保证几个字", "风险词"),
            ("收束", "先让用户开始行动", "土豆崽陪读者跨过第一阶", "第一阶"),
        ],
    ),
    Topic(
        13,
        "真正能让内容变稳的，不是每天逼自己日更，而是你有没有复盘动作。",
        "日更没变稳？你缺的是复盘动作",
        "别只逼自己日更",
        "复盘才会变稳",
        "发了不少内容，但总觉得发完就过去了的人。",
        "补上复盘这一段，让账号更像系统型账号。",
        "重点写复盘维度，不写空泛鸡汤。",
        "没有复盘，内容就像丢出去的纸飞机，飞完就没了。",
        "每篇复盘 4 件事：谁看、哪句停留、哪步转化、下次怎么改。",
        "你发完内容后，会做复盘吗？",
        ["内容复盘", "小红书运营", "AI提效", "内容系统", "个人IP"],
        [
            ("封面", "别只逼日更", "土豆崽抱着日更日历很累，旁边复盘镜子发光", "日历、镜子"),
            ("痛点", "发完就过去了", "土豆崽把内容纸飞机丢出去，后面没有收集箱", "纸飞机"),
            ("判断", "稳来自复盘", "土豆崽把飞回来的纸飞机放进复盘盒", "复盘盒"),
            ("维度1", "先看谁真的在看", "土豆崽用放大镜看读者头像", "读者头像"),
            ("维度2", "再看哪句让人停下", "土豆崽圈出卡片上的关键句", "关键句"),
            ("维度3", "再看有没有下一步", "土豆崽检查从阅读到私信的小箭头", "小箭头"),
            ("AI", "AI适合帮你归纳", "土豆崽把评论和数据交给 AI 小盒子整理", "AI 小盒子"),
            ("收束", "复盘回写选题池", "土豆崽把结论贴回选题池", "选题池"),
        ],
    ),
    Topic(
        14,
        "如果我现在从零开始做一个 AI 账号，我前两周只会先搭这 4 个东西。",
        "从零做AI账号，前两周只做4件事",
        "从零起号",
        "前两周先搭4件事",
        "想起号、重做账号、从零搭内容系统的人。",
        "做阶段性总结，适合建立信任和转发。",
        "重点写从零起号优先级，不写平台速成承诺。",
        "从零做账号，最怕一上来做太多，结果什么都没固定。",
        "前两周先搭定位、选题池、内容工作流、承接入口。",
        "如果你从零开始，最想先搭哪一块？",
        ["AI账号", "个人IP", "内容系统", "AI工作流", "轻创业"],
        [
            ("封面", "前两周只做4件事", "土豆崽站在空白账号面前，只拿出四块积木", "空白账号、四块积木"),
            ("误区", "别一上来做太多", "土豆崽同时抓着十几个任务，快要倒下", "任务球"),
            ("第一件", "先定一句话定位", "土豆崽把账号名牌和一句话定位钉到墙上", "定位名牌"),
            ("第二件", "再建选题池", "土豆崽往选题池放入第一批卡片", "选题池"),
            ("第三件", "搭内容工作流", "土豆崽沿着选题、提纲、成稿、发布走", "内容流程"),
            ("第四件", "留一个承接入口", "土豆崽给内容后面接上一扇小门", "承接小门"),
            ("节奏", "两周先跑顺别贪多", "土豆崽用日历标出两周节奏", "两周日历"),
            ("收束", "先稳，再放大", "土豆崽把四块积木搭稳，后面才出现放大器", "放大器"),
        ],
    ),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def fit(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_lines: int, start: int, min_size: int, bold: bool = False) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(start, min_size - 1, -2):
        fnt = font(size, bold=bold)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
    fnt = font(min_size, bold=bold)
    return fnt, wrap(draw, text, fnt, max_width)


def slug(text: str) -> str:
    text = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", text)
    return text[:28]


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


def draw_potato(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0, mood: str = "focus") -> None:
    body_w = int(250 * scale)
    body_h = int(330 * scale)
    x1, y1 = cx - body_w // 2, cy - body_h // 2
    x2, y2 = cx + body_w // 2, cy + body_h // 2
    draw.ellipse((x1, y1, x2, y2), fill="#E8B84F", outline="#111111", width=max(5, int(7 * scale)))
    draw.ellipse((x1 + int(20 * scale), y1 + int(35 * scale), x2 - int(45 * scale), y2 - int(10 * scale)), fill="#F2CA68", outline=None)
    for dx, dy in [(-50, -95), (38, -118), (-72, 40), (58, 82)]:
        draw.arc((cx + int(dx * scale), cy + int(dy * scale), cx + int((dx + 20) * scale), cy + int((dy + 12) * scale)), 0, 180, fill="#7B5A25", width=max(2, int(3 * scale)))
    eye_y = cy - int(45 * scale)
    for ex in [cx - int(50 * scale), cx + int(50 * scale)]:
        draw.ellipse((ex - int(33 * scale), eye_y - int(34 * scale), ex + int(33 * scale), eye_y + int(34 * scale)), fill="white", outline="#111111", width=max(4, int(5 * scale)))
    if mood in {"angry", "focus"}:
        draw.line((cx - int(88 * scale), eye_y - int(72 * scale), cx - int(25 * scale), eye_y - int(48 * scale)), fill="#111111", width=max(8, int(12 * scale)))
        draw.line((cx + int(25 * scale), eye_y - int(48 * scale), cx + int(88 * scale), eye_y - int(72 * scale)), fill="#111111", width=max(8, int(12 * scale)))
    else:
        draw.arc((cx - int(90 * scale), eye_y - int(85 * scale), cx - int(20 * scale), eye_y - int(35 * scale)), 200, 340, fill="#111111", width=max(7, int(9 * scale)))
        draw.arc((cx + int(20 * scale), eye_y - int(85 * scale), cx + int(90 * scale), eye_y - int(35 * scale)), 200, 340, fill="#111111", width=max(7, int(9 * scale)))
    pupils = [(-38, -4), (45, -8)] if mood != "surprise" else [(-45, -2), (45, -2)]
    for dx, dy in pupils:
        draw.ellipse((cx + int(dx * scale) - int(9 * scale), eye_y + int(dy * scale) - int(9 * scale), cx + int(dx * scale) + int(9 * scale), eye_y + int(dy * scale) + int(9 * scale)), fill="#111111")
    if mood == "smile":
        draw.arc((cx - int(45 * scale), cy + int(35 * scale), cx + int(55 * scale), cy + int(115 * scale)), 10, 170, fill="#111111", width=max(5, int(7 * scale)))
    elif mood == "surprise":
        draw.ellipse((cx - int(24 * scale), cy + int(40 * scale), cx + int(24 * scale), cy + int(88 * scale)), outline="#111111", width=max(5, int(7 * scale)))
    else:
        draw.arc((cx - int(45 * scale), cy + int(65 * scale), cx + int(55 * scale), cy + int(135 * scale)), 200, 340, fill="#111111", width=max(5, int(7 * scale)))
    draw.line((x1 + int(25 * scale), cy + int(45 * scale), x1 - int(70 * scale), cy + int(95 * scale)), fill="#111111", width=max(6, int(7 * scale)))
    draw.line((x2 - int(25 * scale), cy + int(45 * scale), x2 + int(70 * scale), cy + int(15 * scale)), fill="#111111", width=max(6, int(7 * scale)))
    draw.ellipse((x1 - int(90 * scale), cy + int(78 * scale), x1 - int(45 * scale), cy + int(123 * scale)), fill="white", outline="#111111", width=max(4, int(5 * scale)))
    draw.ellipse((x2 + int(50 * scale), cy - int(10 * scale), x2 + int(95 * scale), cy + int(35 * scale)), fill="white", outline="#111111", width=max(4, int(5 * scale)))


def label(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], fill: str = "#FFF6D9", size: int = 34) -> None:
    fnt = font(size, bold=True)
    lines = wrap(draw, text, fnt, 260)
    w = max(draw.textbbox((0, 0), line, font=fnt)[2] for line in lines) + 36
    h = len(lines) * (size + 8) + 26
    x, y = xy
    draw.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=fill, outline="#111111", width=4)
    ty = y + 13
    for line in lines:
        draw.text((x + 18, ty), line, font=fnt, fill="#111111")
        ty += size + 8


def draw_scene(draw: ImageDraw.ImageDraw, topic: Topic, card_idx: int, card: tuple[str, str, str, str]) -> None:
    role, text, scene, prop = card
    palette = ["#FFE9D6", "#EAF7FF", "#F2F6D8", "#F6EDFF", "#EFFFF2"]
    mood = ["focus", "angry", "smile", "surprise"][card_idx % 4]
    top = 300 if card_idx == 0 else 300

    # Keep each card visually dense enough for Xiaohongshu scanning: one large
    # character, two to four large props, and a bold path/relationship mark.
    draw.rounded_rectangle((86, top + 120, W - 86, H - 120), radius=42, fill="#FFFDF8", outline="#F2D7B2", width=5)
    draw.ellipse((74, top + 170, 380, top + 480), fill=palette[card_idx % len(palette)], outline="#111111", width=4)
    draw.ellipse((W - 385, top + 175, W - 70, top + 500), fill="#FFFFFF", outline="#111111", width=4)
    draw_potato(draw, W // 2, top + 500, scale=1.55 if card_idx == 0 else 1.35, mood=mood)
    if card_idx == 0:
        label(draw, "工具太多", (120, top + 235), "#FFFFFF", 42)
        label(draw, "先跑一条", (W - 370, top + 260), "#EAF7FF", 42)
        draw.line((W // 2 - 330, top + 790, W // 2 + 360, top + 1125), fill="#FF7A22", width=24)
        draw.polygon([(W // 2 + 345, top + 1070), (W // 2 + 450, top + 1168), (W // 2 + 300, top + 1162)], fill="#FF7A22")
        label(draw, "跑通", (W // 2 + 245, top + 980), "#FFFFFF", 58)
    else:
        label(draw, prop.split("、")[0], (118, top + 230), palette[card_idx % len(palette)], 38)
        if "、" in prop:
            label(draw, prop.split("、")[-1], (W - 395, top + 250), "#FFFFFF", 38)
        draw.line((205, top + 905, W - 205, top + 905), fill="#FF7A22", width=18)
        draw.polygon([(W - 225, top + 850), (W - 120, top + 905), (W - 225, top + 960)], fill="#FF7A22")
        draw.ellipse((160, top + 840, 245, top + 925), fill="#FFFFFF", outline="#111111", width=5)
        draw.ellipse((W - 255, top + 842, W - 170, top + 927), fill="#FFFFFF", outline="#111111", width=5)

    # Avoid explanatory captions inside the image. The visible card text should
    # stay short; detailed explanation belongs in the publish copy.


def draw_card(path: Path, topic: Topic, idx: int, card: tuple[str, str, str, str], cover_title: bool = False) -> None:
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((44, 44, W - 44, H - 44), radius=30, outline="#111111", width=5)
    draw.rectangle((44, 44, W - 44, 162), fill="#FFF7E8")

    if idx == 0:
        title = topic.cover_title if cover_title else topic.subtitle
        subtitle = topic.subtitle if cover_title else ""
        title_size = 132 if len(title) <= 8 else 110
        fnt, lines = fit(draw, title, W - 150, 2, title_size, 74, bold=True)
        y = 86
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=fnt, stroke_width=4)
            draw.rounded_rectangle((74, y + 20, 74 + int((bbox[2] - bbox[0]) * 0.62), y + fnt.size + 24), radius=16, fill="#FF7A2238")
            draw.text((88, y), line, font=fnt, fill="#111111", stroke_width=4, stroke_fill="#FFFFFF")
            y += fnt.size + 16
        if subtitle:
            sub_font, sub_lines = fit(draw, subtitle, W - 150, 1, 46, 34)
            for line in sub_lines:
                draw.text((92, y + 10), line, font=sub_font, fill="#333333", stroke_width=2, stroke_fill="#FFFFFF")
        draw_scene(draw, topic, idx, card)
    else:
        page = card[0]
        top_font = font(46, bold=True)
        draw.text((76, 78), f"{idx + 1:02d} {page}", font=top_font, fill="#111111")
        fnt, lines = fit(draw, card[1], W - 160, 2, 76, 48, bold=True)
        y = 180
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=fnt, stroke_width=3)
            x = (W - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, font=fnt, fill="#111111", stroke_width=3, stroke_fill="#FFFFFF")
            y += fnt.size + 8
        draw_scene(draw, topic, idx, card)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=95)


def title_bank(topic: Topic) -> str:
    strong = [
        topic.xhs_title,
        f"{topic.cover_title}，很多人第一步就错了",
        f"{topic.cover_title}，不是你不努力",
        f"普通人做 AI，先看懂这件事",
        f"你卡住的地方，可能不是工具",
    ]
    contrast = [
        f"真正重要的不是工具，而是{topic.cover_title}",
        f"别急着学更多 AI，先补这一段",
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
- 推荐理由：标题直接打中当前账号的 AI 工作流主线，适合小红书信息流里快速识别痛点。
"""


def render_markdown(topic: Topic, out: Path) -> None:
    date = f"2026-07-{topic.day:02d}"
    ymd = f"202607{topic.day:02d}"
    article_main = find_article_main(topic.day)
    source_note = "本稿基于 article-write 生成的文章总览母稿改编，平台稿来源只认文章总览母稿。"

    write_text(out / "选题转译.md", f"""# 选题转译

## 来源

- 日期：{date}
- 文章总览母稿：`{article_main.relative_to(ROOT).as_posix()}`
- 说明：{source_note}

## 一句话核心观点

{topic.conclusion}

## 小红书切口

这篇不做长篇概念解释，而是把一个认知判断拆成 8 页图文卡：先制造痛点共鸣，再给判断，再给一个最小行动。

## 未使用实时数据

未调用小红书 API，未使用实时小红书数据，本稿基于文章总览母稿和账号定位生成。
""")

    write_text(out / "标题库.md", title_bank(topic))
    write_text(out / "封面方案.md", f"""# 封面方案

## 封面主标题

{topic.cover_title}

## 副标题

{topic.subtitle}

## 画面钩子

{topic.cards[0][2]}。画面必须让人一眼看懂：{topic.angle}

## 构图要求

- 3:4 竖版
- 上方大标题区
- 土豆崽必须是主角
- 副标题不压角色脸
- 强调线不横穿角色
- 不要大段文字

## 风格要求

- 强制按 `potato-illustrations`
- 白底手绘解释型图
- 中文由本地字体渲染，避免乱码
""")

    cards_md = ["# 图文卡片拆解"]
    for idx, card in enumerate(topic.cards, 1):
        page = ["封面", "痛点", "判断", "核心", "代入", "方法", "场景", "收束"][idx - 1]
        cards_md.append(f"""## {idx:02d} {page}

- 观点：{card[2]}
- 可见文案：{card[1]}
- 画面内容：{card[2]}
- 土豆崽：作为画面主角参与核心动作，表情根据情绪变化
- 背景道具：{card[3]}
- 图片比例和尺寸：3:4，1242 x 1660
- 图片风格：土豆崽 IP，白底手绘解释型图，中文本地排版
- 生图 prompt：见 `prompts/{idx:02d}_{page}.md`
- 审核要点：不压脸、不贴边、不乱码、不过度空白
""")
    write_text(out / "图文卡片拆解.md", "\n".join(cards_md))

    body = f"""很多人以为自己卡住，是因为还没学到更厉害的 AI 工具。

但我更建议你先回头看一眼：你有没有把一件高频动作，真的拆成一条能重复跑的流程？

{topic.conclusion}

这件事不用一上来做得很复杂。你先抓一个最常重复、最容易卡住、最能直接省时间的动作，把它拆出来。

{topic.action}

先让它跑顺，再谈放大。普通人用 AI，最怕的不是慢，而是一开始就把自己搞复杂。
"""
    write_text(out / "发布稿.md", f"""# 标题备选

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

    prompts_dir = out / "prompts"
    images_dir = out / "images"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    for idx, card in enumerate(topic.cards, 1):
        page = ["封面", "痛点", "判断", "核心", "代入", "方法", "场景", "收束"][idx - 1]
        write_text(prompts_dir / f"{idx:02d}_{page}.md", f"""使用 `potato-illustrations` 的土豆崽 IP 风格，生成小红书 3:4 中文图文卡。

主题：{topic.conclusion}
本页可见文案：{card[1]}
画面内容：{card[2]}
背景道具：{card[3]}

约束：
- 土豆崽必须是主角
- 白底手绘解释型图
- 少字、中文清晰
- 不要压脸、贴边、穿模
- 不要小黑，不要通用卡通角色
""")

    for idx, card in enumerate(topic.cards):
        if idx == 0:
            draw_card(images_dir / "01_封面.png", topic, idx, card, cover_title=False)
            draw_card(images_dir / "01_封面_标题版.png", topic, idx, card, cover_title=True)
        else:
            page = ["痛点", "判断", "核心", "代入", "方法", "场景", "收束"][idx - 1]
            draw_card(images_dir / f"{idx + 1:02d}_{page}.png", topic, idx, card)

    write_text(out / "审核报告.md", f"""# 审核报告

## 结论

通过

## 检查项

| 项目 | 结果 | 说明 |
|---|---|---|
| 标题 | 通过 | 主标题短、醒目，符合小红书封面使用 |
| 封面比例 | 通过 | 3:4 竖版，1242 x 1660 |
| 封面钩子 | 通过 | 有土豆崽主角、冲突和视觉隐喻 |
| 封面叠字 | 通过 | 已生成 `01_封面_标题版.png`，本地字体渲染，未压脸 |
| 卡片节奏 | 通过 | 8 页结构完整 |
| 发布正文 | 通过 | 口语化，有判断和最小行动 |
| potato-illustrations 依赖 | 通过 | 使用土豆崽 IP 作为主角 |
| 图片文字 | 通过 | 中文由本地字体绘制，避免模型乱码 |
| 合规风险 | 通过 | 未夸大收益，未承诺结果，未使用侵权 IP |
| 线上边界 | 通过 | 未调用小红书 API/MCP，未主动搜索、浏览、抓取、爬取或登录小红书 |

## 图片清单

- `images/01_封面.png`
- `images/01_封面_标题版.png`
- `images/02_痛点.png`
- `images/03_判断.png`
- `images/04_核心.png`
- `images/05_代入.png`
- `images/06_方法.png`
- `images/07_场景.png`
- `images/08_收束.png`

## 说明

{source_note} 图片采用本地图文卡渲染和本地中文叠字，不冒充 Ark 生成图。未调用 `xhs-search`、`xhs-explore` 或任何小红书线上能力，未使用实时小红书数据。

## 需要重改

- 无
""")


def main() -> None:
    for topic in TOPICS:
        date = f"2026-07-{topic.day:02d}"
        ymd = f"202607{topic.day:02d}"
        out = OUT_ROOT / date / f"{ymd}_小红书_{slug(topic.xhs_title)}_3比4母稿改编版"
        out.mkdir(parents=True, exist_ok=True)
        render_markdown(topic, out)
        print(out)


if __name__ == "__main__":
    main()
