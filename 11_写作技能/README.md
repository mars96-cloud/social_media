# 写作技能目录

这里存放当前工作区自带的写作与调度技能。

## 当前技能

- `social-media-workspace-operator`

## 这个技能负责什么

它不是单个平台写手，而是工作区里的总控入口，统一处理：

- 先读取工作区战略资料
- 判断账号定位、人群、目标和 CTA 是否匹配
- 决定应该输出小红书、公众号还是抖音版本
- 调用平台执行框架整理格式、排版和表达
- 在需要时进入暂存、协作、发布前检查流程

## 目录建议

- `social-media-workspace-operator/SKILL.md`：主入口说明
- `social-media-workspace-operator/README.md`：技能简介与仓库说明
- `social-media-workspace-operator/安装与使用说明.md`：本地安装与使用方式
- `social-media-workspace-operator/references/`：内部规则与路由文档
- `social-media-workspace-operator/examples/`：调用示例

## 使用原则

- 工作区目录中的版本是源码主版本。
- 全局 `Codex` skill 目录中的版本是安装版本。
- 每次更新后，优先同步工作区版本，再复制到全局 skill。

如果后续新增别的平台，优先扩展 `12_平台执行框架`，然后再补这个总控 skill 的平台路由说明。

