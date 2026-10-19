# 输出结构与状态

## 数据体检

`data_issues.csv`：`row_number`、`creator_handle`、`severity`、`field`、`issue_type`、`message`、`manual_action`。

`data_quality.json`：输入行数、有效身份数、重复/缺失身份数、各字段缺失率、格式警告、离群值和推导值。

`header_mapping.json`：输入格式、选中的工作表、表头行、源表头到规范字段的映射、未映射列和重复映射。

`normalized_creators.csv`：规范化后的本地工作副本，包含来源行/工作表与全部规范输入字段；不得覆盖原始导出。

## 评分结果

`ranked_creators.csv` 至少包含：

- 身份：rank、creator_handle、creator_url、nickname、country、language、followers；
- 分数：grade、total_score、positive_score、risk_deduction、audience_match_score、content_ability_score、commerce_efficiency_score、cooperation_score；
- 证据：data_facts、content_inference、manual_verification、evidence_sources；
- 风险与动作：missing_data、risk_points、recommended_strategy、recommendation、next_action；
- 审核：review_status，默认 `pending_review`。

评分不完整时 `total_score` 和 grade 保持“待补数”，同时输出 `known_positive_score` 与 `possible_score_range`。

## 建联草稿

`outreach_drafts.csv`：推荐合作方式及理由、TikTok 私信、邮件主题/正文、48–72 小时跟进、样品沟通、`personalization_needs_verification`、`review_status=pending_review`、`send_status=NOT_SENT`、`contact_status=pending_review`、话术版本。

## 人工复核队列

- `standard_review_queue.csv`：默认前 100 位，适合补齐基本受众、商务和已有内容证据。
- `deep_review_queue.csv`：默认前 40 位，建议按团队承接能力设为 30–50；包含最近 10–20 条视频、评论购买意向与对应评分/证据字段。

队列包括 `queue_priority`、`selection_reason`、当前评分/证据覆盖率、来源行、全部规范输入字段。深度复核表填完后可以直接作为下一次 `run` 的输入。

## Excel 工作簿

标准工作簿包含：`Summary`、`Scoring_Result`、`Standard_Review`、`Deep_Review`、`Outreach_Drafts`、`Data_Issues`、`Funnel_Tracker`、`Excluded_Creators`、`Scoring_Rules`。原始输入必须单独保留，不覆盖。

## 漏斗追踪

状态枚举：`pending_review`、`sent`、`read_no_reply`、`replied`、`pending_collaboration`、`pending_sample`、`sample_sent`、`sample_received`、`pending_content`、`content_published`、`reviewed`、`not_cooperating`、`do_not_contact`。

追踪字段：负责人、发送时间、话术版本、回复状态/耗时/态度、样品成本与物流、签收、出片时间、内容链接、素材质量、播放、互动、点击、订单、GMV、二次合作和下一步动作。
