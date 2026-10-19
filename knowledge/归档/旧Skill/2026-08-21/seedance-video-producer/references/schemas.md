# 执行表、状态机与日志

## Seedance 主操作表

标准六列：

1. `SKU`
2. `白底产品图`
3. `卖点`
4. `文案`
5. `Seedance按九宫格生成视频的提示词`
6. `九宫格图片`

目标输出路径可以来自第二个工作表 `任务状态`、本地 manifest 或任务目录配置，不强制破坏标准六列。

状态表至少包含：

- `task_id`
- `excel_row`
- `task_index`
- `目标输出路径`
- `generation_policy_result`
- `status`
- `attempt_count`
- `completed`
- `video_path`
- `duration_seconds`
- `width`
- `height`
- `validation_result`
- `error_code`
- `error_message`

## 状态机

```text
pending
→ preflight_ready
→ submitting
→ generating
→ download_pending
→ downloaded
→ validated
→ completed
```

特殊状态：

- `awaiting_batch_approval`
- `quota_blocked`
- `face_retry`
- `skipped`
- `unconfirmed_after_browser_timeout`
- `needs_user_review`

## ACTIVE_TASK.json

批次至少记录：

```json
{
  "schema_version": 1,
  "task_id": "stable-id",
  "skill": "seedance-video-producer",
  "output_root": "absolute-path",
  "task_dir": "absolute-path",
  "source_table": "absolute-path",
  "current_index": 0,
  "batch_status": "preflight",
  "daily_success_count": 0,
  "items": []
}
```

每条 item 至少记录：

- 稳定任务 ID、Excel 行号、SKU 和序号。
- 文案、完整提示词、产品图、九宫格和目标路径。
- 当前状态、尝试次数和 `face_retry_count`。
- 提交、完成、下载和校验时间。
- 视频时长、尺寸、校验与人工质检结果。
- 错误码、错误说明和浏览器未确认状态。

## 额度日志

`logs\quota_log.json` 记录：

- 每次 `10001114` 出现时间。
- 当时余额、SKU 和任务序号。
- 每日实际成功视频数量。
- 浏览器未确认状态。
- 同账号人工操作可能影响观察数量的说明。

## 原子性

所有 JSON 先写 `.tmp` 再原子替换。点击生成前先写提交意图；外部状态每次变化后立即持久化。聊天记录不得作为唯一状态。

