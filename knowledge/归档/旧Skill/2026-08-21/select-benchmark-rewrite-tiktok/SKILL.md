---
name: select-benchmark-rewrite-tiktok
description: 基于Y仓SKU产品知识、TikTok运营知识、选品规则和历史爆款文库，完成TikTok Shop选品判断、当前对标内容查找与证据筛选、爆款结构拆解，以及面向印尼市场的中印双语原创仿写。Use when a user asks to查SKU资料、选品、找对标、拆解爆款、仿写带货文案、生成印尼语口播，或让其他AI复用这套知识库与工作流。
---

# TikTok 选品、对标与爆款仿写

把本 Skill 当作可迁移的工作规范和只读知识包。它不依赖 Codex；任何能读取 Markdown、JSONL、XLSX/DOCX 和网页的 AI 都可以使用。

## 开始前

1. 先读 [references/knowledge-index.md](references/knowledge-index.md)，确认来源优先级、时效和已知数据问题。
2. 按任务读取对应参考，不要一次把全部大文件加载进上下文：
   - SKU/产品事实：[references/product/product-truth-rules.md](references/product/product-truth-rules.md)；精确检索 `references/product/product_catalog.jsonl`。
   - 选品：[references/selection/selection-logic.md](references/selection/selection-logic.md)。
   - 找对标：[references/benchmark/benchmark-research.md](references/benchmark/benchmark-research.md)。
   - 仿写：[references/copywriting/rewrite-playbook.md](references/copywriting/rewrite-playbook.md)。
   - 合规与权利：[references/policy-and-rights.md](references/policy-and-rights.md)。
   - 输出字段：[references/output-contract.md](references/output-contract.md)。
3. 默认按内部 SKU 工作，不按店铺拆分。只有用户明确指定店铺版本时，才读取并锁定该店铺的标题、描述、价格和链接。
4. 先声明本轮模式、数据日期和工具边界。没有实时访问能力时，不得声称已查当前市场或最新对标。

## 任务模式

- `product_lookup`：按精确 SKU 返回产品事实、促销、图片和缺失/冲突。
- `market`：只判断市场机会，不要求自有 SKU；不能直接生成发布计划。
- `hybrid`：先找市场机会，再与 Y 仓 SKU 精确匹配并判断承接能力。
- `owned_sku`：从 Y 仓 SKU 出发，用当前市场证据验证需求和内容机会。
- `benchmark_only`：只找、筛、拆对标，不做选品分池。
- `rewrite_only`：用户已给对标，直接做结构镜像和原创仿写。
- `full_pipeline`：选品 → 对标 → 拆解 → 仿写 → 合规自检。

信息不足时选择能安全完成的最窄模式，不要用猜测补齐。

## 固定工作流

### 1. 锁定目标

记录国家/语言、类目或功效方向、目标 SKU、内容形式、目标时长、是否绑定店铺、是否需要当前促销。SKU 必须精确匹配；相似名称只作为候选并要求人工确认。

### 2. 建立产品事实卡

从 `product_catalog.jsonl` 读取精确 SKU，输出规格、成分、真实卖点、使用方法、适用人群、上架原价、日常售价、活动价、折扣、COD、图片、来源、缺失字段和冲突状态。

- `37` 是源数据占位，不是产品事实。
- 商品标题/描述中的医疗化、永久、保证效果等词不自动成为可宣传卖点。
- 当前总表日期是 2026-08-08；`上架原价`、`日常售价`、`活动价` 是三个独立价格口径，禁止互相替代；用户问“现在/今天”的价格、活动或 COD 时必须重新验证。
- 有冲突的字段不得写入文案；标记 `needs_fact_confirmation`。

### 3. 完成选品门禁

按 `market`、`hybrid` 或 `owned_sku` 执行 [references/selection/selection-logic.md](references/selection/selection-logic.md)。先检查来源、时间、链接、近期销量/GMV/增长、数据可信度和硬风险，再评分和分池。

正式高分结论至少需要：48 小时内市场证据、有效竞品链接、可靠数据、自有 SKU 的库存/利润/上架承接（如适用），以及可解释的规则/AI双门槛。缺项进入观察、补数据、补上架或市场机会池。

用户要求立即列出 3 款但没有实时市场数据时，只能运行内部预筛：使用 `scripts/preliminary_shortlist.py` 输出最多 3 个 `preliminary_candidate`，全部进入补数据池并写明“不代表当前推荐”。

### 4. 查找并筛选对标

使用可用浏览器、网页搜索、TikTok、Creative Center、LinkFox/FastMoss 或用户导出数据。每个目标优先收集 5–10 个候选，至少 3 个有效对标。保存链接、作者/店铺、观察时间、语言/市场、产品、价格、数据、首帧、Hook、结构、证据、CTA 和风险。

- 只看高播放不够；必须同时判断产品/痛点匹配、时效、成交关联、可复拍性和合规。
- 纯 BGM 且无销售字幕的内容标记 `skip_bgm_only`。
- 音频不清但疑似有人声时标记 `needs_manual_audio_review`。
- 无实时访问时停止在“搜索方案/待提供链接”，不能编造对标、播放量或 GMV。

### 5. 生成结构指纹

对每条有效对标记录：总时长、段落数、句数、0–3 秒钩子、痛点推进、产品出现时机、卖点顺序、证据类型、情绪曲线、CTA 位置、镜头功能和屏幕文字功能。先得到结构指纹，再写新文案。

### 6. 原创仿写

默认执行高保真结构镜像：尽量对齐总时长、段落数、句数、钩子位置、信息密度、痛点/卖点顺序、情绪曲线、CTA 位置和镜头功能。

只能复用机制，不能逐句照抄、少量换同义词、复制独特口头禅、人物身份、品牌措辞、音乐或受保护镜头。所有产品陈述必须回到当前 SKU 事实卡。默认输出自然口语化 Bahasa Indonesia 和逐段中文对照。

### 7. 三重质检

1. 事实：规格、成分、功效、上架原价、日常售价、活动价、折扣、COD、图片与来源一致。
2. 原创：不是逐句替换；独特表达和第三方身份已移除；给出 `similarity_risk`。
3. 合规：健康/美容不医疗化、不保证结果、不伪造认证/评价/促销；商业与 AIGC 披露字段齐全。

未通过则只修订失败项。需要用户确认的项目保持 `blocked` 或 `needs_review`，不伪装成完成。

## 输出要求

遵循 [references/output-contract.md](references/output-contract.md)。每次结果至少包含：

- 数据范围、观察时间和模式；
- SKU 事实卡及缺失/冲突；
- 选品证据、分池和下一步（如适用）；
- 对标清单、有效/跳过/人工复核数量；
- 结构指纹；
- 印尼语文案、中文对照、屏幕字幕和镜头功能；
- 事实来源、相似度风险、合规状态和人工确认项。

对外文案禁止出现内部 SKU、文件名或本地路径。内部工作表和审计结果可以保留 SKU 与来源。

## 工具与可移植性

- 支持网页的 AI：执行实时检索并保留链接与观察时间。
- 不支持网页的 AI：让用户提供视频链接、转录、截图或平台导出；仍可完成产品检索、历史模式匹配和仿写。
- 不支持 XLSX/DOCX 的 AI：使用已提取的 `product_catalog.jsonl` 和 `tiktok-operations-extracted.md`。
- 不自动登录账号、发布、投放、上传商品、提交视频或改写源知识文件；这些外部操作必须另获明确授权。

## 维护

- 更换产品总表后，运行 `scripts/build_product_catalog.py` 重建 JSONL。
- 更换运营 DOCX 后，运行 `scripts/extract_docx_knowledge.py` 重建 Markdown。
- 近抄回归运行 `scripts/run_fixture_tests.py`；单条检测使用 `scripts/check_rewrite_similarity.py`。
- 更新规则时保留来源日期和版本，不用新结论覆盖历史证据。
- 交付前运行 `scripts/validate_bundle.py` 和 Skill Creator 的 `quick_validate.py`。
