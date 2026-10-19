# Campaign Brief 与达人数据结构

## Campaign Brief（建联前必须确认）

1. 产品名称、品类、目标市场和语言。
2. 一句话核心价值。
3. 三个核心卖点，以及每个卖点可引用的证据。
4. 目标消费者、生活阶段和主要使用场景。
5. 售价、折扣、佣金、样品政策、现金预算与交付要求。
6. 建议内容方向和可提供的图片、视频、脚本或卖点资料。
7. 素材使用权、广告授权或 Spark Ads 支持范围。
8. 已批准宣称与禁用宣称。
9. 联系人、回复时区和商务确认流程。

任何未确认的佣金、现金、免费样品、发货范围、交付物、授权或产品功效都必须保持 `unknown`，生成的话术标为待确认。

## 达人输入字段

| 字段 | 要求 | 处理规则 |
|---|---|---|
| `creator_handle` / `creator_url` | 至少一个 | 达人唯一标识；标准 TikTok 主页链接可安全提取 handle，两者都缺失才排除 |
| `nickname` | 可选 | 仅用于称呼，不据此推断内容 |
| `country` / `language` | 必填 | 与目标市场或语言不符时硬筛排除 |
| `followers` | 必填 | 整数；不单独决定优先级 |
| `recent_views` | 建议 | 使用 `|` 分隔最近多条播放量；脚本取中位数 |
| `engagement_rate_pct` | 建议 | 统一为百分数，如 `4.2` 表示 4.2% |
| `content_category` | 必填 | 明显无关时排除；不明确时待人工复核 |
| `audience_profile` | 有则填写 | 未知写 `unknown`，不得猜测 |
| `commerce_metrics` | 有则填写 | 仅记录有授权来源的数据；缺失不能推断成交能力 |
| `contact_channel` | 建议 | 没有公开/授权联系方式时进入人工队列 |
| `sample_contact_status` | 建议 | 使用固定状态，避免自由文本混乱 |
| `notes` | 可选 | 记录人工观察，不写无证据的个人判断 |
| `creator_type` | 建议 | `emerging_potential`、`stable_publisher`、`high_quality_content`、`live`、`high_volume` |
| `recent_content_observation` | 建议 | 能在首条邀约中引用的真实内容观察 |
| `personalization_verified` | 建议 | 观察是否已人工核验；未核验不能作为确定事实 |

后台导出如包含以下字段，可直接保留，不需要 ScoreHub：

- `authorized_gmv`、`units_sold`：有授权且口径明确的 GMV/销量；
- `avg_shoppable_video_views`、`video_engagement_rate_pct`：平均带货视频播放与互动；
- `audience_female_pct`、`audience_top_age_range`：粉丝性别与主要年龄段；
- `category_gmv_distribution`：成交类目或 GMV 分布。

这些聚合数据只能作为事实证据，不能替代最近 10–20 条内容和评论的人工复核。

## 硬筛与预算字段

- `content_category_relevance`：`relevant`、`adjacent`、`unrelated`、`unknown`。
- `days_since_last_post`：距最近发布的天数。
- `risk_level`：`low`、`medium`、`high`、`unknown`。
- `do_not_contact`：明确拒绝或勿扰时为 `true`。
- `commission_pct`、`estimated_cash_fee`：只用于与 Campaign 的硬预算比较。

## 人工评分字段

评分必须基于可追溯证据填写。缺失分项留空或写 `unknown`，不要填 0。

- 人群匹配 30：`audience_country_language_score`（0–8）、`audience_core_profile_score`（0–8）、`audience_interest_category_score`（0–8）、`audience_use_case_score`（0–6）。
- 内容能力 25：`content_hook_score`、`content_demo_score`、`content_expression_score`、`content_production_score`、`content_stability_score`（各 0–5）。
- 带货效率 25：`commerce_view_fit_score`（0–6）、`commerce_purchase_intent_score`（0–5）、`commerce_content_ratio_score`（0–4）、`commerce_explanation_cta_score`（0–5）、`commerce_data_score`（0–5）。
- 合作可执行性 20：`cooperation_contact_score`、`cooperation_budget_score`、`cooperation_history_score`、`cooperation_schedule_logistics_score`（各 0–5）。
- 风险扣分：`risk_deduction`（0–20）。

## 证据与人工复核字段

- `reviewed_video_count`：建议 10–20；少于 10 时内容稳定性仅作初步判断。
- `reviewed_video_urls`：实际查看的视频链接，以 `|` 分隔。
- `hook_evidence`、`demo_evidence`、`expression_evidence`、`production_evidence`、`stability_evidence`：五项内容评分的可追溯依据。
- `purchase_intent_comment_evidence`：代表性价格、规格、使用或购买问题；不以纯表情互动代替。
- `commerce_content_ratio_evidence`、`commerce_explanation_cta_evidence`：商品内容比例及痛点/演示/CTA 依据。
- `risk_review_evidence`：风险核查与扣分证据。

- `data_facts`：来自导出数据或明确记录的事实。
- `content_inference`：基于公开视频内容形成、但仍需复核的判断。
- `manual_verification`：缺失数据和需人工确认事项。
- `evidence_sources`：URL、后台导出名、日期或团队记录。
- `risk_points`：风险事实与扣分理由。
- `recommended_strategy_override`：人工明确指定的合作策略，可覆盖类型映射。

## 清洗规则

- 按 `creator_url` 或规范化后的 `creator_handle` 去重。
- 自动识别 CSV/TSV/XLSX 的数据工作表、表头行和常见中英文列名；映射结果单独留档。
- 国家、语言、百分比和布尔值统一格式。
- 粉丝、播放等数字支持 `K/M/B` 缩写。
- `recent_views` 使用中位数，避免单条爆款抬高判断。
- 缺失值统一输出为 `unknown`；未知不等于 0。
- 国家、语言、粉丝或类目缺失时进入“待补数”，不因缺失自动淘汰；已知且与硬条件冲突才排除。
- 先输出数据质量报告，再评分；硬筛排除项不进入评分排名。
