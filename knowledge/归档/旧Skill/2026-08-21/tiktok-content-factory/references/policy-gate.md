# TikTok 官方规则门禁

## 权威来源

- TikTok Creative GenAI Terms：`https://ads.tiktok.com/i18n/official/article?aid=10021580`
- TikTok Community Guidelines Overview：`https://www.tiktok.com/safety/en/policies-and-engagement/overview`
- 本机摘要（若存在）：`D:\codex项目\knowledge_base\04_short_video_content\tiktok_official_ai_generation_and_commercial_safety_rules_20260723.md`

## 自动更新规则

每个新批次先读取本机摘要中的读取日期：

- 摘要不存在、距当前日期超过 7 天、用户要求“最新规则”，或页面/产品出现新政策提示时，重新读取两个官方页面。
- 官方内容有实质变化时，更新本机知识库笔记、索引（如需要）和 `knowledge_base\learning_log.md`。
- 无法联网时可以使用本机最近摘要，但在任务 manifest 中记录 `policy_source_status=local_cached` 和读取日期。
- 在任务目录保存本批次的 `RULES_SNAPSHOT.md`；这是任务数据，不得保存进 Skill。

## 生成前三阶段门禁

### A. 生成前

确认：

- 商品类别允许推广，受管制或高风险商品已完成适用性检查。
- 功效、成分、价格、折扣、认证和 COD 信息有可靠来源。
- 用户拥有产品图、包装、商标、参考内容、人物脸部和声音的必要权利。
- 真人脸、声音、姓名或肖像已经取得必要同意。
- 输入不含密码、密钥、支付信息、敏感个人信息或机密资料。
- 不向 TikTok GenAI 工具提交伊利诺伊州居民或身处伊利诺伊州个人的面部图像或声音记录。

未通过时标记 `blocked_before_generation` 并停止对应项目。

### B. 生成中

把以下约束写入文案和图片提示词：

- 不生成医疗、法律、金融等专业建议。
- 不生成保证结果、虚假前后对比、虚构认证/成分/评价、欺诈促销或危险行为。
- 不冒充真实第三方，不复制受保护表达。
- 不重画产品包装，不虚构标签、Logo 或文字。
- 不要求隐藏 AI 来源、移除水印、规避审核、人脸检测、额度或其他平台控制。

### C. 生成后

逐条核对：

- 事实、功效、价格、折扣、成分和认证与来源一致。
- 产品外观、包装、标签和 Logo 与原图一致。
- 没有侵权、冒充、未经许可人物、危险行为或误导性内容。
- 已保留 AIGC 标注、商业披露和人工质检字段。

只有 `generation_policy_result=passed` 才能进入可执行表。

## 发布状态字段

至少保留：

- `rights_confirmed`
- `consent_confirmed`
- `generation_policy_checked`
- `generation_policy_result`
- `generation_policy_notes`
- `aigc_disclosure_required`
- `aigc_disclosure_confirmed`
- `commercial_disclosure_required`
- `commercial_disclosure_confirmed`
- `human_qc_completed`
- `platform_scope`，默认 `tiktok_only`

在视频真正发布前必须人工确认披露与质检；内容生成完成不等于可发布。

