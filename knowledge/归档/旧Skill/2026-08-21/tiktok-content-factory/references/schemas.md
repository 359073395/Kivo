# 目录、表格与 Manifest

## 任务目录

默认命名：

```text
<output_root>\<safe_sku>_<YYYYMMDD>_<form>\
```

同名时追加 `_02`、`_03`。建议子目录：

```text
inputs\
images\product\
images\nine_grid\
images\presenter\
tables\
logs\
ACTIVE_TASK.json
RULES_SNAPSHOT.md
```

所有路径在表格和 manifest 中保存为绝对路径。

## 文案源数据表

生成前的源数据至少包含：

1. `店铺名`
2. `SKU`
3. `店铺SKU` 或 `sku ID`
4. `产品ID`
5. `产品标题`
6. `TikTok产品描述`
7. `功效/卖点`
8. `规格/成分`
9. `日常售价`
10. `平台活动价`
11. `COD状态`
12. `产品图`
13. `数据来源文件`
14. `来源行号/记录ID`

目标店铺任务必须有店铺标题和产品描述。描述为 HTML 时先清洗为纯文本，但保留原始来源文件和行号用于追溯。

## Seedance 执行表

主操作列固定为：

1. `SKU`
2. `白底产品图`
3. `卖点`
4. `文案`
5. `Seedance按九宫格生成视频的提示词`
6. `九宫格图片`

政策、来源和状态字段可放在第二个工作表 `任务状态`，不要破坏主操作表六列顺序。状态表至少包含 `task_id`、`店铺名`、`店铺SKU`、`产品ID`、`目标输出路径`、`source_table`、`source_row`、`generation_policy_result`、`rights_confirmed`、`consent_confirmed` 和 `status`。

## 数字人口播执行表

主操作列：

1. `SKU`
2. `白底产品图`
3. `卖点`
4. `文案`
5. `视频标题`
6. `标签`
7. `数字人图片`
8. `HeyGen动作提示词`

状态表至少包含 `task_id`、`店铺名`、`店铺SKU`、`产品ID`、`目标输出路径`、`source_table`、`source_row`、`voice_language`、`aspect_ratio`、`generation_policy_result`、`rights_confirmed`、`consent_confirmed` 和 `status`。

## ACTIVE_TASK.json

最小结构：

```json
{
  "schema_version": 1,
  "task_id": "stable-id",
  "skill": "tiktok-content-factory",
  "original_sku": "SKU",
  "safe_sku": "SKU",
  "mode": "content",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "output_root": "absolute-path",
  "task_dir": "absolute-path",
  "rules_snapshot": "RULES_SNAPSHOT.md",
  "rights_confirmed": false,
  "consent_confirmed": false,
  "generation_policy_checked": false,
  "generation_policy_result": "needs_review",
  "aigc_disclosure_required": true,
  "commercial_disclosure_required": true,
  "platform_scope": "tiktok_only",
  "current_index": 0,
  "batch_status": "preflight",
  "items": []
}
```

每个 item 使用稳定 `task_id`，记录 Excel 行号、店铺名、内部 SKU、店铺 SKU、产品 ID、标题/描述来源、总表来源、功效来源、价格来源、序号、文案、提示词、素材路径、输出路径、状态、尝试次数和错误说明。

更新 manifest 时先写同目录临时文件，再原子替换正式文件。任务数据不得写入 Skill 目录。
