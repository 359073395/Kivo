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
  "skill": "tiktok-content-system",
  "mode": "pure_heygen",
  "output_root": "absolute-path",
  "task_dir": "absolute-path",
  "source_table": "absolute-path",
  "current_index": 0,
  "batch_status": "preflight",
  "method_id": "M-CNT-PURE-HEYGEN-001",
  "method_version": "2026-08-29",
  "sample_approval": {
    "status": "not_required_or_pending_or_approved_or_rejected",
    "approved_at": null,
    "evidence": null
  },
  "batch_approval": {
    "status": "pending_or_approved_or_revoked",
    "approved_at": null,
    "task_id": null,
    "evidence": null
  },
  "active_standard_id": null,
  "standard_history": [],
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
- `presenter_id`，同一 SKU 一致、跨 SKU 唯一
- `presenter_qc_status`
- `presenter_image_sha256`
- `presenter_approval`：至少包含 `status`、精确 `sku`、`approved_path`、`approved_version`、`approved_sha256`、`approved_at`、`evidence` 和 `scope=exact_sku_exact_file`
- `remote_input_binding`：至少包含实际 `remote_avatar_id` 或 `remote_asset_id`、`sku`、`approved_sha256`、`remote_preview_verified=true`、`preview_person_match=true`、`preview_product_match=true`、`preview_scene_match=true` 与绑定时间
- `product_source_path`
- `product_source_sha256`
- `audio_path`
- `audio_sha256`
- `method_id`
- `method_version`
- `rules_snapshot`
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
- `render_match_qc`：开头/中段/结尾相对批准图的 `presenter_match`、`exact_sku_product_match`、`package_match`、`scene_match`、`placeholder_absent` 及审核帧路径
- `error_code`
- `error_message`
- `human_qc_completed`

## 原子更新

每次外部状态变化后立即更新 manifest：

1. 写入同目录 `ACTIVE_TASK.json.tmp`。
2. 刷新并关闭文件。
3. 原子替换 `ACTIVE_TASK.json`。

聊天记录不是运行状态来源。结果表、项目摘要和 manifest 应互相对应；冲突时优先核对远端 ID、本地文件、用户批准证据和较新的状态时间，再做兼容修复。旧 manifest 缺少新增字段时可以补齐，不能因此重建任务或重复生成。

批准范围不得推断：某SKU或某样图获批，不能把其他SKU、旧文件、派生文件或相似图的 `user_approved` 自动写为 `true`。缺少精确批准字段、远端ID/预览绑定或成片对照结果时，状态最多为 `await_presenter_approval`、`bind_and_verify_exact_remote_avatar` 或 `await_render_match_qc`；不得进入 `submitted`、`completed_validated` 或发布交接。

`standard_history` 的每条记录至少包含：`standard_id`、`scope`、`method_id`、`method_version`、`status`、`batch_authorized=true`、`approved_at`、`approval_task_id`、`approved_sample_task_id`、关键输入哈希、质量门和 `supersedes`。只有批量批准记录可以成为 `active_standard_id`；样片批准或更新的候选测试不得写入活动指针。
