# 输入表与 Manifest

## 数字人口播执行表

主操作表至少包含：

1. `SKU`
2. `白底产品图`
3. `卖点`
4. `文案`
5. `视频标题`
6. `标签`
7. `数字人图片`
8. `HeyGen动作提示词`

状态工作表或外部 manifest 还必须提供：

- `task_id`
- `目标输出路径`
- `voice_language`，默认 `id-ID`
- `aspect_ratio`，默认 `9:16`
- `generation_policy_result`
- `rights_confirmed`
- `consent_confirmed`
- `status`

外部 Excel 字段名称不同但语义明确时可以建立一次字段映射，并把映射记录到 manifest；不要静默猜测含义不明确的列。

## ACTIVE_TASK.json

批次字段至少包含：

```json
{
  "schema_version": 1,
  "task_id": "stable-id",
  "skill": "heygen-video-producer",
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

- `task_id`
- `excel_row`
- `sku`
- `task_index`
- `script`
- `presenter_image`
- `output_path`
- `status`
- `attempt_count`
- `remote_request_id`
- `video_id`
- `submitted_at`
- `completed_at`
- `downloaded_at`
- `duration_seconds`
- `width`
- `height`
- `validation_result`
- `error_code`
- `error_message`
- `human_qc_completed`

## 原子更新

每次外部状态变化后立即更新 manifest：

1. 写入同目录 `ACTIVE_TASK.json.tmp`。
2. 刷新并关闭文件。
3. 原子替换 `ACTIVE_TASK.json`。

聊天记录不是状态来源。结果表和 manifest 应互相对应，但冲突时优先核对远端 ID 和本地文件后再修复。

