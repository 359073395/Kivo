---
name: tk-creator-outreach
description: "直接读取合法导出的 TikTok Shop 达人 CSV/XLSX，自动映射中英文表头、清洗去重、硬筛、按原版证据模型评分和分层，并生成前 30–50 位的视频/评论复核表与待人工审核邀约草稿。用于低成本达人筛选和建联准备；不依赖 ScoreHub 或外部 API，不抓取未授权数据，不自动群发。"
---

# TikTok Creator Outreach

采用“免费后台导表 + 本地处理 + 少量人工深度复核”的两阶段漏斗。默认只使用用户合法提供的 CSV/TSV/XLSX 和人工核验内容，不购买第三方达人数据，不调用外部达人 API。

## 不可破坏的边界

- `unknown` 不等于 0。缺少可靠证据的评分分项必须保持 `unknown`，不得重分配权重或生成伪精确总分。
- 数据事实、内容推测和待人工核验项必须分列；昵称、头像或单条爆款不能证明受众、内容稳定性或转化能力。
- 只生成 `pending_review` / `NOT_SENT` 草稿。任何实际发送、创建会话、寄样、修改佣金、报价、授权或对外承诺，都需要用户在当次操作前明确确认。
- Offer、产品功效、交付物和使用权只可来自已确认的 Campaign Brief。未确认时保留 `unknown` 或写“需确认”。
- 明确勿扰、市场/语言已知且不符、赛道完全无关、长期停更、明显品牌安全风险或超过硬预算的达人进入排除清单。

## 默认工作流

1. **确认 Campaign Brief**：产品、市场/语言、目标人群、活动目标、佣金/样品/预算、交付物、使用权、禁用宣称。字段见 [Campaign 与达人数据结构](references/campaign-and-data-schema.md)。
2. **直接读取后台导表**：优先使用原始 CSV/TSV/XLSX，不要求用户另存格式，不覆盖源文件。脚本自动选择工作表、检测前 30 行中的表头并映射常见中英文列名。
3. **先校验映射**：运行 `validate`，查看未映射列和数据问题。只有供应商自定义表头无法识别时才使用 `--mapping`，规则见 [本地导表工作流](references/local-export-workflow.md)。
4. **全量处理**：按 handle/URL 去重、统一数值/百分比/K/M 缩写、计算近期播放中位数、执行硬筛，并按 [原版评分模型](references/scoring-model.md) 计算已有证据。
5. **两级人工队列**：默认从全量生成约 100 人 `standard_review_queue.csv` 和约 40 人 `deep_review_queue.csv`。队列排序只决定复核先后，不等于原版最终分。
6. **只深审前 30–50 位**：人工查看最近 10–20 条视频与代表性评论，填写 Hook、产品演示、表达、制作、稳定性、购买意向、商品内容比例、CTA 和风险证据。
7. **把深审表作为新输入重跑**：只有 18 个正向分项和风险扣分全部有依据时才输出 A/B/C/D；A≥80、B=65–79、C=50–64、D<50。
8. **生成建联准备**：仅为完整 A/B 候选生成合作策略、TikTok 私信、邮件、48–72 小时跟进和样品沟通草稿。文案边界见 [建联 Playbook](references/outreach-playbook.md) 与 [禁用宣称](references/prohibited-claims.md)。
9. **人工发送与复盘**：用户批准后才可使用已授权工具发送；回填回复、寄样、出片、点击、订单和 GMV，再校准模型。

## 本地运行

使用可用的 Python 3。脚本只依赖 Python 标准库，直接支持 `.csv`、`.tsv`、`.xlsx`。

```powershell
python scripts/creator_outreach.py validate `
  --input "path/to/tiktok-creator-export.xlsx"

python scripts/creator_outreach.py run `
  --input "path/to/tiktok-creator-export.xlsx" `
  --config assets/campaign-config.example.json `
  --output-dir "outputs/tk-creator-outreach"
```

自动映射失败时才添加：

```powershell
--sheet "达人导出" --header-row 3 --mapping assets/header-mapping.example.json
```

漏斗人数可在 Campaign 配置的 `funnel` 中调整，也可临时传入 `--standard-review-limit` 和 `--deep-review-limit`。

## 输出

- `normalized_creators.csv`：自动映射后的规范字段；原始导出保持不变。
- `ranked_creators.csv`：原版四维评分、风险、证据覆盖率、可能分数区间和下一步动作。
- `standard_review_queue.csv`：默认前 100 位标准复核队列。
- `deep_review_queue.csv`：默认前 40 位的 10–20 条视频和评论证据填写表；可直接作为下一轮输入。
- `outreach_drafts.csv`：完整 A/B 候选的待审核、未发送草稿。
- `excluded_creators.csv`：重复与硬筛排除项。
- `header_mapping.json`、`data_issues.csv`、`data_quality.json`、`analysis_report.md`：映射、质量和审计记录。

详细列定义见 [输出结构](references/output-schema.md)。

## 模式选择

- 用户只有产品：先完成 Campaign Brief；不虚构达人。
- 用户给了 CSV/XLSX：直接校验、运行并报告漏斗；只有真实表头歧义才追问。
- 用户给了深度复核表：重新评分并只为完整 A/B 生成草稿。
- 用户要求 500 人处理：全量机器体检，约 80–120 人标准复核，约 30–50 人深审；不默认给 500 人逐一看视频或生成消息。
- 用户要求实际建联：先展示最终名单、Offer、首条消息和发送范围，等待明确确认；没有授权发送工具时只交付草稿。
- 更新模型：读取 [原版 PDF 对齐记录](references/source-design-notes.md)，保留版本原因、测试数据和结果。

