---
name: potato-illustrations
description: 当用户想用 Ian 风格的中文正文配图方式，为文章、帖子、工作流、方法论、结构图、观点图生成插图，但主角要换成用户自己的土豆崽 IP，而不是小黑时使用。
---

# 土豆崽正文配图

## 核心定位

这套 skill 用来生成中文正文配图。

目标不是做商业插画、PPT 信息图、可爱海报，也不是做通用卡通图。
目标是把文章里的关键判断、流程、结构、状态或隐喻，转成一张：

- 白底
- 手绘
- 留白多
- 少字
- 怪诞但清爽
- 适合正文中穿插使用

的解释型配图。

默认主角不是小黑，而是你自己的 `土豆崽 IP`。

土豆崽必须参与画面的核心动作，不能只是站在旁边当装饰。

## 强制生图路线

只要这个 skill 进入“实际生成图片”的阶段，必须调用：

- `$ark-image-generation`

禁止默认改走通用 `image_gen`。
禁止静默切换成别的生图路线。

如果 Ark 因为账号、接口、模型、权限或参数问题无法生成，就明确报错，说明 Ark 当前不可用，不要假装已经生成成功。

在生图前，必须先读取：

- `$ark-image-generation`

默认读取全局 Codex skills 下的 `$ark-image-generation`。

规则：

- 如果这个 skill 可用，就必须优先使用它
- 如果这个 skill 不可用，就明确提醒用户当前缺少 Ark 生图 skill
- 只有在 Ark skill 不可用、且用户允许时，才能改走别的生图路线

## 强制角色锚点

后续所有土豆崽配图，都必须以内置在这个 skill 里的角色资料为硬锚点，而不是只靠文字描述去“理解角色”。

必读锚点：

- `assets/potato-ip/定版说明.md`
- `assets/potato-ip/images/01_角色设定主图_定版.png`
- `assets/potato-ip/images/02_平静直视.png`
- `assets/potato-ip/images/03_微坏笑.png`
- `assets/potato-ip/images/04_生气皱眉.png`
- `assets/potato-ip/images/00_土豆崽20张总览.png`

高频表情锚点：

- `assets/potato-ip/social_pack/高频精选/01_角色设定主图_定版.png`
- `assets/potato-ip/social_pack/高频精选/02_平静直视.png`
- `assets/potato-ip/social_pack/高频精选/03_微坏笑.png`
- `assets/potato-ip/social_pack/高频精选/04_生气皱眉.png`

这些不是“可选 moodboard”，而是角色一致性的硬参考。

另外，`assets/potato-ip/prompts/` 里的角色 prompt 和背景 prompt 也都是重要模板。

规则是：

- 不要求每次逐字逐句照搬这些 prompt
- 不要求每次只复刻现有动作
- 但只要你要生成新的动作、新的表情、新的场景、新的正文配图构图，就必须参考这些现有 prompt 的角色基线和表达边界

也就是说，这些资料不是“必须原样拿来用”，但它们一定是新图生成时的角色母模板。

## 先读这些文件

按任务需要读取：

- `references/style-dna.md`
- `references/potato-ip.md`
- `references/composition-patterns.md`
- `references/prompt-template.md`
- `references/qa-checklist.md`
- `references/encoding-rules.md`

`assets/examples/` 只用于低频风格校准，不能默认直接照抄构图。

`assets/potato-ip/` 是这套 skill 自带的角色资产区，后续所有角色扩展都优先参考这里。

## 工作流

### 1. 先读正文

先读用户给的文章、Markdown、Notion 页面、长文、截图文字或观点材料。

要先提炼出：

- 核心观点是什么
- 哪些段落承担认知转折
- 哪些内容适合用图解释
- 哪些地方只该保留文字

不要平均配图。
优先选择“认知锚点”去画，比如：

- 核心判断
- 输入输出闭环
- 前后对比
- 分流
- 常见坑
- 承接路径
- 状态变化

### 2. 先出配图策略

如果用户只是让你分析“哪些地方该配图”，先输出 shot list，不要直接生图。

每张图至少写清楚：

- 放在哪个段落后
- 图的主题
- 核心意念
- 结构类型
- 土豆崽在图里做什么
- 建议元素
- 建议中文标注词

默认 4-8 张。
文章短时 1-3 张。
长文也不要轻易超过 9 张。

### 3. 再生成单张图片

如果用户明确要求“生成图片 / 出图 / 做图”，就进入实际生成。

规则：

- 必须调用 `$ark-image-generation`
- 每张图单独生成
- 不要把多张图拼成一张
- 一张图只讲一个核心结构

如果任务来自 `redbook-gen` 的小红书图文卡包，优先使用本 skill 自带脚本作为入口：

```powershell
python C:\Users\Administrator\.codex\skills\potato-illustrations\scripts\generate_redbook_images.py --days 2 --model doubao-seedream-5.0-lite
```

这个脚本是 `potato-illustrations` 的执行入口，负责读取小红书稿包中的 `prompts/*.md`，按土豆崽规则生成正式图片，保存到对应稿包的 `images/`。脚本内部才会按本 skill 的强制路线调用 `$ark-image-generation`。不要在 `redbook-gen` 中直接绕过本脚本调用底层生图 helper。

小红书图片卡叠字强规则：

- 不要在左上角写“痛点”“判断”“核心”“收束”等页签。
- 不要把所有标题都放进明显黑色边框里，看起来像表格或 PPT。
- 标题应像海报标题一样直接贴在上方安全区，可以用轻微白色半透明底带提升可读性，但不要画硬边框。
- 内页只保留一条核心短句，不要给图片加栏目名。
- 如果旧图已经有页签或标题框，必须用脚本重新叠字导出版，不要继续沿用旧样式。

每次生成前，必须显式校准土豆崽一致性：

- 脸型对齐 `01_角色设定主图_定版`
- 眼睛比例对齐 `02_平静直视`
- 微坏笑气质对齐 `03_微坏笑`
- 生气和压眉状态对齐 `04_生气皱眉`
- 整体表情范围对齐 `00_土豆崽20张总览`

如果要扩展新的姿势、动作、表情、道具关系、场景关系，还必须参考：

- `assets/potato-ip/prompts/01_角色设定主图.md`
- `assets/potato-ip/prompts/02_平静直视.md`
- `assets/potato-ip/prompts/03_微坏笑.md`
- `assets/potato-ip/prompts/04_生气皱眉.md`

如果要扩展正文背景或场景感，还要参考：

- `assets/potato-ip/prompts/background_01_工作流主视觉.md`
- `assets/potato-ip/prompts/background_02_内容生产台.md`
- `assets/potato-ip/prompts/background_03_提效到变现路径.md`
- `assets/potato-ip/prompts/background_04_讲人话的AI教练.md`
- `assets/potato-ip/prompts/background_05_避坑与判断.md`

如果是一组图，这组图必须像同一只土豆崽，不能每张都长得像不同角色。

### 4. 生成后检查

生成后按下面文件检查：

- `references/qa-checklist.md`

重点检查：

- 土豆崽是不是核心动作主体
- 是否像同一个角色
- 是否太像 PPT
- 是否字太多
- 是否有明显 AI 漂移
- 是否偏离白底手绘路线

### 5. 保存交付

如果是在工作区内交付图片，按下面结构保存：

```text
assets/<article-slug>-illustrations/
```

文件名按顺序命名：

```text
01-topic-name.png
02-topic-name.png
```

不要覆盖已有成果，除非用户明确要求替换。

## 输出口径

生成前：

- 简短说明计划画几张
- 每张图负责表达什么

生成后：

- 说明生成了几张
- 每张图适合放在哪里
- 保存路径
- 哪些图最稳
- 哪些图只是备选

不要长篇解释风格理论。

## 防乱码规则

这套 skill 以后必须全部使用简体中文正文，不要夹杂英文说明段落，除非是：

- YAML `name`
- 必要的命令
- 必要的路径
- 必要的模型名

为了一劳永逸避免乱码，固定遵守以下规则：

1. 所有 `.md`、`.yaml` 文本文件统一使用 `UTF-8` 编码保存。
2. 不要通过 shell 的字符串替换去批量拼接中文正文内容。
3. 中文说明文档优先直接用文件编辑方式重写，不在终端里拼长段中文。
4. 如果已有文件出现乱码，不在原乱码文本上做局部修补，直接整文件重写为正常简体中文。
5. skill 内涉及中文路径时，优先同时保留“目录语义说明 + 真实绝对路径”，避免后续再发生路径乱码理解偏差。
6. 后续新增 reference 文件时，也必须保持 UTF-8 和简体中文，不允许再混入乱码文件。

7. 如果某个角色参考资产已经被收进 skill 内部，优先引用 skill 内部相对路径，不再依赖工作区外部目录。
