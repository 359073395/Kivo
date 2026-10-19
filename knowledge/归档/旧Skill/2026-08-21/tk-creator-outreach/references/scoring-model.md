# 达人评分模型（原版 PDF 对齐版 v2.0）

先硬筛，再评分。评分必须来自可追溯证据；没有证据的分项为 `unknown`，不得填 0、不得按已有项目重新分配权重。

## 总分

`总分 = 人群匹配度 + 内容能力 + 带货效率 + 合作可执行性 - 风险扣分`

正向分满分 100；风险扣分 0–20。输出同时保留各分项、证据、缺失数据、风险点和下一步动作。

## 人群匹配度：30 分

| 分项 | 上限 | 判断依据 |
|---|---:|---|
| 国家与语言匹配 | 8 | 创作者市场、主要内容语言与 Campaign 目标 |
| 核心受众匹配 | 8 | 年龄、性别、生活阶段；没有后台数据时只能写“内容受众推测，待验证” |
| 内容兴趣与产品赛道匹配 | 8 | 最近内容主题、产品赛道、受众兴趣 |
| 使用场景匹配 | 6 | 创作者真实内容场景与产品核心使用场景 |

输入字段：`audience_country_language_score` 0–8、`audience_core_profile_score` 0–8、`audience_interest_category_score` 0–8、`audience_use_case_score` 0–6。

## 内容能力：25 分

以最近 10–20 条内容为主，不用单条爆款代替稳定性判断。

| 分项 | 上限 | 判断依据 |
|---|---:|---|
| 前 3 秒 Hook | 5 | 是否快速建立问题、利益点或观看理由 |
| 产品演示 | 5 | 是否能清楚展示产品、步骤和结果 |
| 表达可信度 | 5 | 是否自然、可信、有个人特色 |
| 制作最低质量 | 5 | 画面、收音、剪辑是否满足最低要求 |
| 内容稳定性 | 5 | 最近 10–20 条是否稳定，而非只靠一条爆款 |

输入字段：`content_hook_score`、`content_demo_score`、`content_expression_score`、`content_production_score`、`content_stability_score`，均为 0–5。

同时保留 `reviewed_video_count`、`reviewed_video_urls`、`hook_evidence`、`demo_evidence`、`expression_evidence`、`production_evidence`、`stability_evidence`。填写内容分却没有对应证据时，数据体检必须发出警告；样本少于 10 条时不得把稳定性判断写成确定事实。

## 带货效率：25 分

| 分项 | 上限 | 判断依据 |
|---|---:|---|
| 近期播放与粉丝规模合理性 | 6 | 使用近期播放中位数，避免单条爆款干扰 |
| 评论购买意向 | 5 | 真实问题、价格/规格/购买意向，不以纯表情互动代替 |
| 商品内容比例 | 4 | 商品与非商品内容比例是否健康 |
| 痛点、演示与 CTA | 5 | 历史商品内容是否能解释痛点、完成演示并给出行动指引 |
| 成交/GMV/转化证据 | 5 | 仅使用合法获得且口径明确的数据；缺失时标记证据不足 |

输入字段：`commerce_view_fit_score` 0–6、`commerce_purchase_intent_score` 0–5、`commerce_content_ratio_score` 0–4、`commerce_explanation_cta_score` 0–5、`commerce_data_score` 0–5。

播放高不等于带货强。成交数据缺失时，`commerce_data_score` 必须为 `unknown`，通过小样测试继续验证。

评论购买意向、商品内容比例和痛点/演示/CTA 分数分别保留 `purchase_intent_comment_evidence`、`commerce_content_ratio_evidence`、`commerce_explanation_cta_evidence`。后台聚合数据不能自动生成这些内容分。

## 合作可执行性：20 分

| 分项 | 上限 | 判断依据 |
|---|---:|---|
| 联系渠道 | 5 | 有明确可用的联系渠道 |
| 合作方式与预算 | 5 | 寄样、纯佣、付费或混合方式是否在预算内 |
| 历史履约与沟通 | 5 | 已知的回复、履约、拒绝或勿扰状态 |
| 排期与样品地区 | 5 | 内容排期、样品可寄地区和物流可执行性 |

输入字段：`cooperation_contact_score`、`cooperation_budget_score`、`cooperation_history_score`、`cooperation_schedule_logistics_score`，均为 0–5。

## 风险扣分：0–20 分

使用 `risk_deduction` 直接记录经人工确认的总扣分，并在 `risk_points` 写明依据。风险来源包括数据异常、品牌安全、过度商业化和违规历史。没有完成风险核查时为 `unknown`，不得默认 0。

风险扣分不能替代硬筛。明显违规、明确勿扰或严重品牌安全风险应先排除。

## 缺失值与分级

- 任一评分分项或风险扣分缺少可靠依据时，保留 `unknown`，输出已知分、缺失分项与可行分数区间。
- 只有全部评分分项和风险扣分都有依据时，才输出精确总分和 A/B/C/D。
- 分层：A 80–100；B 65–79；C 50–64；D <50。
- 不完整记录标为“待补数”，不因缺数据自动淘汰。

## 校准

首次用 10 位脱敏达人测试，再扩到 50 位，最后处理大名单。每轮回填回复率、寄样转化率、出片率、GMV 和素材质量；积累一批结果后再调整权重，并记录版本、原因和测试结果。

首次导表产生的 `standard_review_queue.csv` / `deep_review_queue.csv` 仅用于安排复核顺序。该顺序不是本模型的替代分数，不得对外展示为 A/B/C/D。
