# HeyGen 生成协议

## 连接方式

- 只使用已连接的 HeyGen MCP OAuth。
- 授权失效时要求用户重新连接 HeyGen；不要改用 API key。
- 不读取、保存或请求 `HEYGEN_API_KEY`。
- 不使用 Video Agent 自由生成产品视频。
- 不使用 HeyGen 生成人物图或商品图。

## 每条任务

1. 确认当前没有其他任务处于 `submitting` 或 `generating`。
2. 检查图片、脚本、语言、比例、输出路径和合规状态。
3. 先写提交意图、时间和尝试次数，再调用创建工具。
4. 保存返回的请求 ID/视频 ID。
5. 只轮询该 ID；轮询本身可以安全重试。
6. 状态成功后下载一次，校验后才进入下一条。

建议状态：

```text
pending
→ preflight_ready
→ submitting
→ generating
→ download_pending
→ downloaded
→ validated_raw
→ polishing
→ validated
→ completed
```

特殊状态：

- `auth_blocked`
- `quota_blocked`
- `unconfirmed`
- `needs_user_review`
- `skipped`

## 重试

- 身份验证错误：立即暂停整个批次，要求重新连接，不重试创建。
- 支付、套餐或额度错误：记录服务消息并暂停，不更换调用路线。
- 明确的模型兼容性错误：只调整当前条，并在用户选择会改变人物/引擎时要求确认。
- 可重试网络错误：只对查询或下载重试一次。
- 创建调用返回不明确：不得重发创建；先通过远端列表、已有 ID 和本地文件核对。
- 当前条明确失败且没有远端成功记录时，最多重试当前条一次；再次失败标记 `needs_user_review` 并暂停。

## 下载命名

原始视频建议：

```text
videos\raw\<safe_sku>_<task_index:03d>_heygen.mp4
```

发布版建议：

```text
videos\polished\<safe_sku>_<task_index:03d>_polished.mp4
```

不要覆盖同名有效文件。任务目录和表格中的路径必须为绝对路径。

## 合规

- 只处理 `generation_policy_result=passed` 的输入。
- 不冒充真实第三方或公众人物。
- 保留平台水印和 AI 标记。
- 记录 `aigc_disclosure_required`、`commercial_disclosure_required` 和 `human_qc_completed`。
- 默认 `platform_scope=tiktok_only`。

