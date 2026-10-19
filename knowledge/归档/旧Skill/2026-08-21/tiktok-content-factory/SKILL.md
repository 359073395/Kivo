---
name: tiktok-content-factory
description: 学习 TikTok 爆款内容的结构并原创生成印度尼西亚市场带货文案、Seedance 九宫格执行表、数字人口播执行表及所需产品图、九宫格图和数字人图。Use when the user asks to learn viral copy, generate Indonesian TikTok Shop scripts, prepare Seedance or HeyGen execution materials, create product-preserving commerce images, or resume such a content-preparation task from a local task folder.
---

# TikTok Content Factory

## 核心约束

- 只把本 Skill 当作流程说明和轻量工具包。
- 禁止把任何真实任务图片、Excel、视频、字幕、manifest、日志或聊天记录写入本 Skill 目录。
- 把全部输入副本、生成产物和任务状态写入用户本次指定的任务目录。
- 不依赖聊天历史续跑；以任务目录中的 `ACTIVE_TASK.json`、表格和文件为准。
- 缺少产品原图时暂停对应 SKU，列出缺失项并要求用户补充，不猜测产品外观。
- 已指定目标店铺时，缺少该店铺 SKU 的商品标题或产品描述就暂停对应项目，不用其他店铺资料代替。
- 本 Skill 只准备内容和素材，不自动提交 HeyGen 或 Seedance 视频生成。

## 开始前必须读取

按需读取以下轻量参考，不要一次加载无关内容：

- 内容生产步骤：[references/workflow.md](references/workflow.md)
- 官方规则门禁与自动更新：[references/policy-gate.md](references/policy-gate.md)
- 表格、目录和 manifest 字段：[references/schemas.md](references/schemas.md)

如果本机存在项目知识库，同时检索：

- `D:\codex项目\knowledge_base\00_INDEX.md`
- `D:\codex项目\knowledge_base\tag_dictionary.md`
- `D:\codex项目\knowledge_base\04_short_video_content\`
- `D:\codex项目\knowledge_base\06_tools_and_workflows\`
- `D:\codex项目\tiktok_copy_knowledge_base\`

使用 `rg` 搜索当前 SKU、商品类目、文案、九宫格、数字人、Seedance、HeyGen 和最新规则。旧聊天或旧规则与知识库最新决策冲突时，以最新决策和官方来源为准。

## 解析输出位置

按以下优先级确定 `output_root`：

1. 用户本次明确指定的目录。
2. `%USERPROFILE%\.codex\tiktok-video-workflow\config.json` 中的 `output_root`。
3. Windows 默认 `D:\TikTok视频生产\`。
4. 没有 D 盘时使用 `%USERPROFILE%\TikTok视频生产\`。

解析后先向用户明确本次保存位置。用户可以为每个任务指定不同位置；只有用户要求“以后默认使用”时才更新全局配置。

可调用：

```powershell
py -3 scripts/workspace_state.py resolve --output-root "<本次目录>"
py -3 scripts/workspace_state.py create --skill tiktok-content-factory --sku "<SKU>" --form content --output-root "<本次目录>"
py -3 scripts/workspace_state.py configure "<以后默认使用的目录>"
```

脚本只在用户输出目录创建任务文件，绝不在 Skill 目录创建任务产物。

## 续跑

- 用户给出任务目录时，先读取该目录的 `ACTIVE_TASK.json`。
- 用户未给目录时，在已解析的 `output_root` 中定位未完成任务。
- 只有一个匹配任务时可自动继续；多个匹配任务时列出路径并请用户选择。
- 已标记完成的项目不得重新生成，除非用户明确要求重做。
- 旧任务没有 manifest 时，先从现有表格和文件建立兼容 manifest，不移动、不覆盖原文件。

## 执行顺序

1. 按 `店铺名 + SKU` 盘点功效/卖点、该店标题、该店产品描述、价格、产品图和参考内容。
2. 运行官方政策与权利预检。
3. 校验总表、店铺表和产品图的 SKU 映射；冲突时暂停，不混用不同店铺资料。
4. 学习爆款的钩子、节奏、痛点、卖点顺序和 CTA，不复制受保护表达。
5. 为每个 `店铺名 + SKU` 原创生成自然口语化 Bahasa Indonesia 文案。
6. 为每条内容生成 Seedance 提示词和/或数字人口播动作提示词。
7. 对文案和图片提示词做生成中政策检查。
8. 使用图像生成/编辑能力制作并逐张质检所需图片；产品必须严格跟随原图。
9. 对文案、提示词和图片做生成后质检。
10. 只把 `generation_policy_result=passed` 的项目写入可执行表。
11. 原子更新 `ACTIVE_TASK.json`，记录数据来源、完成项、阻断项、路径和下一步。

## 交付规则

- 默认市场：TikTok Shop Indonesia。
- 默认语言：自然口语化 Bahasa Indonesia。
- Seedance 版本：9:16、15 秒、少字幕或无字幕，九宫格按从左到右、从上到下执行。
- 数字人口播版本：稳定口播、小幅动作、产品标签朝向镜头，不制作产品使用 B-roll。
- 所有对外文案和画面禁止出现 SKU 或内部文件名。
- 结果必须包含可直接交给后续视频 Skill 的本地绝对路径。
- 向用户汇报输出目录、成功数量、阻断数量、缺失素材和下一步调用的 Skill。

## 完成条件

只有同时满足以下条件才把内容准备任务标记为 `completed`：

- 必需产品图齐全且通过外观质检。
- 文案、提示词和图片通过政策与事实检查。
- 执行表已写入用户指定目录并可读取。
- 所有表格中的本地路径存在。
- `ACTIVE_TASK.json` 已保存且能够在新对话恢复。
