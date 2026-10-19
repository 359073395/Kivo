---
name: heygen-video-producer
description: 根据本地数字人口播执行表，通过已登录的 HeyGen MCP OAuth 严格串行生成数字人口播视频，下载到用户指定目录，完成 FFprobe/FFmpeg 校验、本地后期、结果表记录和中断续跑。Use when the user asks to generate, download, polish, validate, resume, or locate HeyGen presenter videos from an Excel file, task manifest, or local task folder.
---

# HeyGen Video Producer

## 核心约束

- Skill 目录只保存流程、轻量 reference 和小脚本。
- 禁止把真实图片、Excel、视频、字幕、manifest、日志、下载缓存或聊天记录写入 Skill 目录。
- 所有任务产物和状态只写到用户本次指定的任务目录。
- 固定使用 HeyGen MCP OAuth；不读取或使用 HeyGen API key，不切换到 REST API key。
- 使用已验收的数字人图片做 image lip-sync；不使用 HeyGen 生图，不使用 Video Agent 自由生成商品视频。
- 严格串行；当前条完成、跳过或进入人工复核状态前，不提交下一条。
- 不依赖聊天历史；恢复时以本地文件和 `ACTIVE_TASK.json` 为事实来源。

## 开始前必须读取

- 生成、轮询、下载与错误处理：[references/production-protocol.md](references/production-protocol.md)
- 输入表和 manifest 结构：[references/schemas.md](references/schemas.md)
- 本地后期与视频校验：[references/validation.md](references/validation.md)

如果本机存在以下当前规则，同时读取：

- `D:\codex项目\knowledge_base\06_tools_and_workflows\tiktok_latest_rules_and_last_task_handoff_20260722.md`
- `D:\codex项目\knowledge_base\04_short_video_content\tiktok_official_ai_generation_and_commercial_safety_rules_20260723.md`
- `D:\codex项目\tiktok_copy_knowledge_base\04_ai_video_production_workflow.md`

## 定位任务与输出位置

优先使用用户本次给出的任务目录或执行表路径。没有指定时按顺序读取：

1. `%USERPROFILE%\.codex\tiktok-video-workflow\config.json`
2. `D:\TikTok视频生产\`
3. 没有 D 盘时使用 `%USERPROFILE%\TikTok视频生产\`

向用户明确本次读取位置和视频保存位置。用户可以为每个任务指定不同目录；不得把文件复制进 Skill。

可调用：

```powershell
py -3 scripts/workspace_state.py resolve --output-root "<本次目录>"
py -3 scripts/workspace_state.py locate --skill heygen-video-producer --output-root "<本次目录>"
py -3 scripts/workspace_state.py check "<任务目录>"
py -3 scripts/workspace_state.py configure "<以后默认使用的目录>"
```

只有一个未完成任务时可以自动继续；多个任务时列出路径并要求用户选择。

## 前置检查

在调用 HeyGen 前检查整张表和全部素材：

- 每行有稳定任务 ID、SKU、印尼语文案、数字人图片和目标输出路径。
- 所有本地图片路径存在且属于正确 SKU。
- 图片已经通过产品、包装、标签、Logo、人脸和手部质检。
- `generation_policy_result=passed`。
- 真人脸、声音、姓名或肖像的必要权利与同意已确认。
- 不包含密码、API key、支付信息或不必要的个人敏感资料。
- 当前条没有已有 `video_id`、已下载视频或未确认的远端提交。

缺少字段或文件时，在任何远端创建动作前停止并报告。已有 `video_id` 时只查询，不重复创建。

## 执行流程

1. 读取或建立 `ACTIVE_TASK.json`，锁定当前序号。
2. 把当前条状态原子更新为 `submitting` 并记录提交意图。
3. 通过 HeyGen MCP OAuth 上传/引用当前数字人图片。
4. 使用 image lip-sync 路线创建 9:16、印尼语数字人口播视频。
5. 保存远端请求 ID 或 `video_id` 后进入 `generating`。
6. 只轮询当前 ID，直到 `completed`、明确失败或需要用户处理。
7. 从 HeyGen 返回的正式成品地址下载到当前任务的 `videos\raw\`。
8. 校验原始视频并更新状态。
9. 按当前规则执行本地后期，输出 `videos\polished\`。
10. 再次校验，更新结果表和 manifest，然后处理下一条。

## 动作与成片要求

- 默认 9:16，语言 Indonesian。
- 只做稳定数字人口播，不插入产品使用画面或 B-roll。
- 产品标签朝向镜头并尽量保持清楚。
- 人物使用小幅点头、微笑、视线和指向动作。
- 禁止大幅挥手、转身、遮嘴、遮挡产品或改变包装。
- 不移除平台已有水印、AI 标记或其他合成内容识别信息。

## 恢复与幂等性

- `completed`、`downloaded` 或已有有效目标文件的条目不得重新提交。
- 有远端 ID 时只继续查询、下载或后期。
- 创建结果不明确时先查 manifest、远端列表、下载目录和目标文件；不要重新创建。
- 浏览器/工具/网络读取超时且远端状态未知时标记 `unconfirmed` 并暂停当前条。
- manifest 使用临时文件加原子替换更新。

## 完成汇报

汇报成功数、跳过数、失败/暂停原因、原始视频目录、发布版目录、未确认任务和结果表路径。只有人工质检与披露检查完成的条目才可标记为可发布。
