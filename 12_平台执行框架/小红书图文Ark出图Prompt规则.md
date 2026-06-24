# 小红书图文 Ark 出图 Prompt 规则

## 适用范围

用于本工作区的小红书图文卡片出图，默认配合 `ark-image-generation` 使用。

目标不是生成“长得像 PPT 的信息卡”，而是生成更像小红书爆款知识卡的底图或成图基础。

## 总原则

1. 一页只讲一个中心判断。
2. 首图优先抓人，不优先解释。
3. 中间页优先做结构、误区、步骤、对比。
4. 同一篇里风格可以统一，但不同主题要有明显区分。
5. Prompt 重点描述视觉主体、情绪、版式气质，不要把整页文案都塞进模型。

## 推荐 Prompt 结构

每一页 prompt 默认按这 6 段组织：

1. 内容类型
   - `Chinese Xiaohongshu knowledge-card illustration`
   - `Chinese social-media editorial infographic`

2. 页面目的
   - 首图 / 误区页 / 流程页 / 收口页

3. 视觉主体
   - 标签块
   - 清晰图标
   - 路径箭头
   - 对比物
   - 轻手写感元素

4. 风格气质
   - 高信息密度
   - 清晰排版感
   - 强对比
   - 收藏感
   - 轻 editorial 感

5. 色彩和版式
   - 浅底
   - 2 到 3 个强调色
   - 垂直画幅
   - 单一焦点

6. 限制项
   - `no watermark`
   - `no photo-real portrait`
   - `no messy tiny text`
   - `no UI screenshot`

## 页面类型规则

### 1. 首图

- 目标：先让人停下。
- Prompt 重点：
  - 一个强判断
  - 一个强主体
  - 夸张但清晰
  - 不要解释过多

### 2. 误区页

- 目标：让读者快速对号入座。
- Prompt 重点：
  - 混乱 vs 清晰
  - 错误动作 vs 正确路径
  - 警示色少量点缀

### 3. 流程页

- 目标：让读者一眼看懂顺序。
- Prompt 重点：
  - 清晰路径
  - 分步标签
  - 箭头或层级
  - 不要做成复杂流程图

### 4. 结论页

- 目标：收口观点并强化记忆点。
- Prompt 重点：
  - 一句大判断
  - 少量辅助符号
  - 空间更干净

## 风格族规则

### blueprint

- 适合：流程、结构、路径类主题
- 特征：浅蓝底、蓝色主强调、清晰模块、轻科技感

### warm-notes

- 适合：经验、误区、判断类主题
- 特征：米白底、橙红强调、便利贴和手写标签感

### newsroom

- 适合：问题、冲突、反常识类主题
- 特征：白底或灰白底、红黑高对比、标题冲击强

## 禁止方向

- 纯米色大留白信息卡
- 大段密集小字
- 一张图里出现太多独立主题
- 过强海报感，缺少“知识卡”可读性
- 把整篇正文直接写进 prompt

## 推荐负面限制词

可复用一组负面限制：

`no watermark, no logo, no UI screenshot, no realistic app interface, no dense tiny text, no blurry details, no messy collage, no stock photo look`

## 本工作区的出图习惯

1. 先在 `配图方案.md` 定每页信息结构。
2. 再写 `ark_prompts.json`，逐页固化 prompt。
3. 真正调用 Ark 时，只生成本地图片，不连平台编辑器。
4. 如果 Agent Plan key 可用但模型 id 未确认：
   - 记录阻塞状态
   - 保留 prompt
   - 不伪造生成成功

