# TikTok 合规、披露与权利门禁

官方核对日期：2026-08-12。政策会变化；新批次距此超过 7 天、用户要求最新，或平台出现新提示时重新核对。

## 官方来源

- TikTok Community Guidelines：`https://www.tiktok.com/community-guidelines`
- TikTok AIGC 帮助：`https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content`
- TikTok 商业内容披露：`https://ads.tiktok.com/help/article/about-the-commercial-content-disclosure-setting-for-advertisers`
- TikTok 创作者商业内容质量标准：`https://ads.tiktok.com/help/article/about-tiktoks-content-quality-standard-for-creator-commercial-content`
- TikTok Shop AIGC 规则示例：`https://seller-us.tiktok.com/university/essay?knowledge_id=491489038501663&lang=en`

## 必须执行

- 推广品牌、产品或服务时使用平台商业内容披露设置。
- 真实感 AI 人脸、声音、人物或场景需要按平台要求披露 AIGC；数字人、合成声音和显著 AI 编辑默认标记待披露。
- 不使用他人受版权/商标保护的内容、带水印搬运、未授权人物肖像/声音或冒充背书。
- 商业内容应真实可信，产品使用、体验、评价和演示不得伪造。
- 受管制或高风险商品先确认当地 TikTok Shop 类目与广告准入。

## 生成前

确认商品允许推广，产品事实和促销有可靠来源，用户拥有产品图、包装、参考内容、人物脸部/声音的必要权利，输入中无密码、密钥、支付信息或敏感个人资料。

## 生成中

禁止医疗/法律/金融专业建议、保证结果、虚假前后对比、虚构认证/成分/评价、欺诈促销、危险行为、冒充第三方、复制受保护表达、重画包装或规避平台审核/水印/披露。

## 生成后

逐条核对事实、外观、权利、商业披露、AIGC 披露与人工质检。至少保留：

- `rights_confirmed`
- `consent_confirmed`
- `generation_policy_checked`
- `generation_policy_result`
- `aigc_disclosure_required`
- `aigc_disclosure_confirmed`
- `commercial_disclosure_required`
- `commercial_disclosure_confirmed`
- `human_qc_completed`

只有 `generation_policy_result=passed` 的内容才可标为执行候选；生成完成不等于可以发布。
