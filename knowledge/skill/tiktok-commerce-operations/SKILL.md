---
name: tiktok-commerce-operations
description: Operate the user's TikTok Shop Indonesia commerce system across product selection, SKU truth, weekly Dianxiaomi exports, pricing, Flash Deal, Feishu dispatch, listing optimization, review attribution, version comparisons, paid-traffic diagnostics, and multi-store audits. Use when the user mentions 电商运营总控、打品、跟品、整体运营规划、选品、SKU、店小秘周更、Flash Deal、定价、飞书派工、商品链接、Listing、商品卡、产品图、上架、评价归因、链接改版复测、店铺产品库、投流、千川、GMV Max、ECPM、广告消耗、ROI、空烧或跑飞.
---

# TikTok Commerce Operations

Treat this as one SKU-centered operating system. Do not make the user choose among the four legacy Skills.

Before applying a remembered rule, read `vault_root/资产/规则/规则权威与变更协议.md` and `vault_root/资产/规则/活动规则总表.md`. Old conversations, archived Skills and module history are evidence only.

Read `vault_root/资产/规则/蒸馏知识自动调用与Skill同步协议.md` for every run. After selecting a mode, read `references/distilled-method-routing.md` and automatically apply only the active methods whose triggers match; the user does not need to name the method. Candidate and `needs_reconfirm` content keeps its restricted status.

## Resolve the vault and work roots

1. Resolve `vault_root` from the nearest `knowledge-base.json` marker above the task/input path, then this loaded Skill's resolved target path, then `KNOWLEDGE_BASE_ROOT`, and finally `D:\Knowledge` only when its marker exists. Do not treat an external working directory as evidence that the vault is unavailable.
2. Read `vault_root/辅助/配置/machine-paths.local.json` when it exists.
3. Keep rules, distilled knowledge and final summaries in `vault_root`.
4. Keep source workbooks, downloads, generated uploads, browser files, databases and task logs in the configured external local work root.
5. Never invent a path when a required machine path is blank; complete all path-independent work, then report the smallest missing setting.

## Route by requested outcome

| User intent | Mode | Module to read |
|---|---|---|
| 电商运营总控、打品/跟品、跨渠道周期规划 | `campaign_planning` | `references/product-campaign-planning.md` |
| 找产品、判断能不能卖、市场机会、测试池 | `selection` | `modules/selection-engine/RUNBOOK.md` |
| 店小秘每周更新、同步在线产品表 | `weekly_sync` | `modules/weekly-product-sync/RUNBOOK.md` |
| SKU 定价、清仓下架、活动价、Flash Deal | `pricing_campaign` | `modules/sku-feishu/RUNBOOK.md` |
| 飞书 SKU 总控、派工、预购、下架、恢复正常 | `sku_dispatch` | `modules/sku-feishu/RUNBOOK.md` |
| 商品链接、标题、详情、关键词、商品卡、主图 | `listing` | `modules/listing-optimization/RUNBOOK.md` |
| 商品评价归因、跨文案图片视频资料一致性、链接改版复测 | `listing` | `references/commerce-quality-tools.md`（按实际输入选择检查/评价/复测，不新增前置） |
| 投流、千川、GMV Max、ECPM、广告消耗、空烧、跑飞、ROI/投产诊断 | `paid_traffic_diagnosis` | `modules/paid-traffic-diagnosis/RUNBOOK.md` |
| 从周更一直做到活动表或派工 | `weekly_end_to_end` | weekly sync then SKU/Feishu module |

For overall commerce planning, enter `campaign_planning` first, recover any existing SKU/store plan, and read COM-014 plus [the campaign planning runbook](references/product-campaign-planning.md). Route its concrete actions to the existing modes and content/creator Skills. Pure factual queries and already-planned local execution do not restart strategy.

If one request spans modes, run them in dependency order: `selection -> SKU facts/pricing -> listing/content facts -> paid traffic diagnosis -> weekly sync -> campaign/dispatch`. Do not mix their evidence or completion criteria. `千川` is a paid-traffic term, not a separate Skill or business system.

## Shared source-of-truth rules

- 产品资料跨文案/图片/视频复用、完整Listing交付、评价整理或旧链接改版复盘时，按需读取[增量工具与模板](references/commerce-quality-tools.md)。共享产品事实、字段/单位检查、评价计数与版本复测接入原流程，原`validate_listing_delivery.py`保留；本周市场前置覆盖、SKU/价格/飞书规则和外部授权不变。模板由代理从已有资料整理，产物放库外，不要求用户另填一套表；无评价/复测数据不阻断首测资料。

- 本周2026-10-19—24先上链接测流量/成交，先读[临时用户覆盖](../../资源/来源索引/2026-10-19_本周先上链接测流量与成交.md)和[十店项目](../../项目/进行中/20260927_十店单人运营周计划.md)。外部市场/LinkFox/对标销量渠道不作本周排期与资料前置；SKU创建字段或最近全公司站点API未知不单独否决。保留真实SKU/图片/价格和已知排除，库存上传前核；不把未知市场写通过、历史hold写永久禁用，线上商品仍用户手动发布。期限外恢复一般规则。

- Listing标题/详情及对标、官方稿比较，自动读取[关键词与交付检查](references/listing-keyword-delivery.md)。先逐词比对并保留有依据的核心购买需求，再处理具体无依据承诺；不能把优化写成重复的泛化清洁/护理文案。默认一份推荐，中文说明、独立印尼语标题和详情复制框。用户不必再次提醒；来源为[2026-10-13直接纠正](../../资源/来源索引/2026-10-13_标题详情关键词与交付自检纠正.md)。

- 当前十店在线产品更新后，按用户 2026-10-10 明确要求继续同步原飞书 SKU 总览/派工事实层，并保留逐店与整项完成进度。先恢复 [十店 SKU 总览与飞书任务闭环](../../项目/进行中/20261010_十店SKU总览与飞书任务闭环.md)；不复跑清空输入的一次性安装脚本，不把飞书派工维护扩展为线上店铺修改授权。

- 对标交付必须可由用户查验：触发选品/竞品/对标时，读取[2026-10-09直接纠正](../../资源/来源索引/2026-10-09_对标必须提供可查验链接.md)。每个对标名称旁直接附真实商品详情页链接，并对应自家SKU；涉及视频/渠道结论同时附原证据链接。名称、ID、截图、搜索页和本地路径不能替代商品直达链接；缺失/受限/未核验要说明，不猜造URL，不声称对标已验证。每日摘要“不发表格”不取消对标证据链接。

- Browser reading follows SYS-006: prefer the in-app browser and recover the user's already-open page. Do not interpret a runtime failure as missing login. For the current two-SKU visual selection, restore [2026-09-28 cross-check project](../../项目/进行中/20260928_两SKU可视化销量交叉选品.md): exclude health supplements for this project, require recent market and Dianxiaomi SKU sales evidence, and keep withdrawn preliminary recommendations provisional.

- For warehouse SKU facts or pricing-source lookup, read `references/current-warehouse-source.json` and its linked knowledge asset/source card. Resolve the source workbook relative to the configured `tiktokSkuRoot`; verify its hash before deriving prices. A unified price workbook marked as needing rebuild is not a current-price source. A source-only knowledge intake does not authorize repricing Flash Deal or changing live products.
- Use exact `store + SKU` for listing identity and exact SKU for warehouse/pricing identity.
- Similar names, similar packaging and shared product IDs never authorize merging facts.
- Separate verified facts, user claims, inference, unknown and conflicts.
- `unknown` is not zero and must not pass a required gate.
- Current market, price, promotion and platform-rule claims require current authorized evidence.
- In `listing` mode, price, discount, voucher, promotion and subsidy are excluded from diagnosis, prioritization, recommendations, AI prompts and feedback evaluation. Low CTR routes to title/main-image work; low post-click CVR routes to detail, attribute, variant-clarity and trust work. Pricing and Flash Deal remain separate modes and never activate from listing metrics.
- Executor-facing workbooks must be directly forwardable: use `执行表` in the title and filename instead of role labels such as `翻译专用`; include explicit actions, execution status and raw data-return fields only, while the user and AI retain diagnosis and next-step optimization in the analysis layer.
- Any product-card data-return task must collect both Product Card report data and Product Card advertising data; never return only one group. Keep the advertising fields exactly as shown in the interface: `Pendapatan kotor`, `Impresi iklan produk`, `Jumlah klik iklan produk`, `Tingkat klik iklan produk`, and `Rasio konversi iklan`. Executors copy displayed values without calculation; blanks stay unknown and only an explicit backend zero becomes `0`.
- Product appearance, packaging, logo, variants, quantities and claims must stay faithful to source materials.
- For listing lifecycle decisions, `不通过` means platform review rejection: remove the product from the listing queue, preserve the rejection evidence, and never evade review by changing content. Zero orders alone do not establish low weight or justify deletion. Prioritize sold links, but retain unsold links with meaningful click/cart signals for observation or evidence-based testing. Check exact ID, reporting scope, complete observation window and sale availability before proposing retirement. Data anomalies require verification first. The previous zero-order blanket-deletion rule was an AI overgeneralization, explicitly corrected by the user on 2026-09-09 for Product ID 1737245549493715997. Do not present poor performance causing policy violations as a verified platform mechanism.
- If a Listing image task lacks the exact product's real source image, report the missing asset and stop that image task. Never borrow a similar SKU image, infer the product's appearance from its title, or imply that an image was produced.
- Do not upload, publish, send, alter a live listing or create a remote campaign without the user's explicit current-task authorization.

## Latest-rule overrides

These rules override conflicting legacy module text:

1. For the user's current Flash Deal workflow, edit each store's existing original `Flash Deal.xlsx` in place after validating store identity, template freshness, SKU-to-product-ID mapping and price eligibility.
2. Do not create `Flash Deal_已填写.xlsx`, a backup copy or a separate audit workbook by default. Create any of them only when the user explicitly asks.
3. Preserve the official workbook package structure. Patch only authorized cells, then reopen and verify the exact original path.
4. Never replace a store's template with another store's template. Stop the affected store on ambiguity.
5. The old hard-coded cross-task handoff ID is retired. A weekly end-to-end task continues inside the current task or records a local handoff under `项目/会话交接`.
6. Outputs must not be written into the Skill directory or a synchronized media folder.
7. Flash Deal writing must pass an OOXML structural gate before replacement: every populated row has exactly one `Product_id` cell and one `Deal Price` cell, cell references are unique, product IDs are unique, unauthorized columns are empty, and the populated-row count equals the expected eligible set. Appended rows must clone a pristine unfilled style row, never a row already containing product data.

8. User-confirmed 2026-09-22 Flash rule: skip an entire store + Product ID when it has more than one distinct exact SKU, regardless of whether final prices agree; report the skipped IDs without asking again. A single Npcs SKU remains eligible subject to pricing checks.

9. User-confirmed 2026-09-22 pricing: price1 = ceil((current warehouse column E cat-store price + 8000) * 1.05) IDR; final = min(price1, Y-warehouse activity price). This replaces the old 5% uplift capped at 3000. Rebuild and validate unified prices before writing Flash.

9.1 User-confirmed 2026-10-10 quantity rule: Npcs price = the exact base SKU's finalized unit price × N. Match the same price type; never use a standalone pack quote to override multiplication. Missing or conflicting unit price blocks that item. Read [Npcs quantity correction](../../资源/来源索引/2026-10-10_Npcs按最终单件价乘数量.md). The Flash multi-SKU skip rule remains in force.

10. User-confirmed 2026-09-22 price-risk check: before changing Flash prices, compare old/new Flash values, both pricing sources and warehouse source versions; report increase/decrease/unchanged counts and largest differences. Proactively alert on large changes or suspect unit/column interpretation and hold the affected item for the user’s decision. Formula correctness alone does not validate an anomalous source value. Do not invent a permanent user-approved percentage threshold.

Read `references/latest-rules.md` before any campaign or weekly update.

## Execution contract

For every run:

1. State the selected mode and data scope.
2. Inventory inputs without modifying them.
3. Run factual, identity, freshness and compliance gates.
4. Execute the smallest authorized change.
5. Verify with deterministic counts, exact IDs, hashes or workbook checks appropriate to the mode.
6. Report completed, skipped, blocked and unknown separately.
7. Report which distilled method IDs were applied or rejected and why.
8. Save only a reusable summary or final retrospective to the knowledge vault; return real outcomes to the method/Skill feedback loop.

## Stop conditions

Stop the affected unit rather than guess when store identity, exact SKU, product ID, current template, price source, product facts, rights, login authorization or output path is missing or conflicting. One blocked store or SKU does not justify corrupting the rest of a verified batch.

## Legacy preservation

The four original Skills exist only under `vault_root/归档/旧Skill/2026-08-21`. Active `modules/` contain non-discoverable `RUNBOOK.md` files plus scripts/references. Do not invoke legacy names or recover their frontmatter into the active tree.

## 公司手册方法补充（COM-015）

任务涉及选品/总控用01，Listing用02，投流诊断用03，周报与证据整改用06时，读取[公司手册方法入口](references/company-manual-methods.md)，按触发条件补足证据与检查。仅相容流程为active_process_only，数字、政策与算法解释仍受来源核验门；不要加载整套教材代替回答当前问题。

## 2026-10-16 下次排班参数覆盖

先恢复[十店项目](../../项目/进行中/20260927_十店单人运营周计划.md)与其[10/16来源](../../资源/来源索引/2026-10-16_上午工作实测与每店五链接目标.md)。用户一周测试反馈上午可完成统计数据和邀请达人，准确分钟未知，未证明全部回复/翻译/寄样也完成。以后新计划每天每店5条新测试链接、十店50条；沿用十店同组与每SKU首测一套，执行为每天5个不同SKU。达人配额不变，产品链接素材和视频素材分开、找视频素材与制作分别留时。50条是计划目标，非实绩或整日容量验收。下方旧10/100、10/8—17的90/900及240/120分钟仅为已发布历史依据，不再强制下一次新计划；本次不改云端旧任务或机器人。

## 十店单人周计划恢复

用户要求十店日程、每周任务、每日上架、达人时间或根据周报重排时，先读[当前十店项目](../../项目/进行中/20260927_十店单人运营周计划.md)，按active_project恢复最新纠正：达人独立后台连续处理、SKU与卖点版本资料跨店复用、成熟周报加执行实绩驱动每周重排。不要恢复旧的回复10/15分钟、素材逐店重复制作、SKU固定单店或永久重点店。具体数字仅取当前周已确认事实和清楚标注的预算；此入口不改变其他项目或外部授权。

## 十店周任务滚动维护（2026-10-08）

每次用户要求生成/重排本项目每周任务，读取[当前项目滚动清理段](../../项目/进行中/20260927_十店单人运营周计划.md)和[直接授权](../../资源/来源索引/2026-10-08_每周任务滚动清理与历史实绩保留.md)。恢复北京时间与实际计划周，先本地备份旧任务和实绩并核验，再移除执行区上一周任务；10/8本次重排清除10/8以前旧日期任务，不仅改标题或保留旧未开始任务。未完事项需明确新日期、来源和容量重排，不能无条件挂着或顺延。原始销售/巡店及其他非任务业务数据不删除，历史实绩留档供周报。同范围已有用户授权，无需重复询问；备份或保护核验失败停止清理。

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 使用`scripts/validate_weekly_task_rollover.py <库外核查JSON>`检查日期/备份/旧任务残留/数据保护、接续来源及严格数量；行为回归见`tests/test_weekly_task_rollover.py`。每天10不同SKU、十店同组、每店10/全日100计划、每SKU首测一套不缩减，当前10/8—17目标90不同SKU/900计划组合（10/11休息，9工作日；旧三日30/300仅子区间）。目标、符合证据数量、实际完成数分开；5候选不称完整计划，旧链优化/重复版本不凑新增，缺额保留未完成并继续筛选，计划量不当实绩。此入口不授权其他删除或线上商品操作。

## 2026-09-30十店首轮测品覆盖

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 恢复[当前十店项目](../../项目/进行中/20260927_十店单人运营周计划.md)及[机器可读标准](references/ten-store-daily-test-standard.json)：10/8起每天从用户指定“仓库所有SKU”选10个跨品类、不相似且通过普货核查的SKU，先查第三方关键词，制作每SKU一套真实标题/主图/详情，十店上同组、每店10 SKU；每天单列BD品牌认证。旧A/B三套与每日3条不是本项目首测前置。10/1—7仅可选轻量链接和视频素材；已执行数据保留。数据、权利、库存或真实图片缺失停止对应项，不把计划100条当实绩。

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 进入批次执行准备前用 `scripts/validate_ten_store_daily_batch.py <库外批次JSON>` 检查同组10SKU、品类/用途去重、风险与证据、各店一致性和BD含义；`tests/test_ten_store_daily_batch.py`为恢复与禁止回归校验。空批次应保持阻塞，不靠占位值通过。

### 本项目最新手动日预算与视频时段（2026-10-08）

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 用户最新估计为每日链接资料240分钟、十店手动上传120分钟，两项360分钟；每日上限600分钟、每周6天、手动5店一组两组不变。24分钟/套及12分钟/SKU十店仅是平均预算反推，非逐SKU实测；旧30/20分钟单位估时归历史，不再×100或÷5。每日10不同SKU/十店100条、完整周5000邀请及既有其余预算保持。找视频素材与制作成片必须独立排时段，素材没齐先找，不将计划搜索当已有素材；具体视频分钟/条件产量沿当前项目已回读日程恢复，仅为本次预算。预算分钟算术已通过、实际耗时及SKU准备仍未确认，不以360分钟核心预算证明全天通过，不假定等待并行/素材提速、不强推ERP批量。原话与当前状态沿既有十店项目恢复。

当前范围依用户最新要求为10/8—17，10/11休息，共9工作日；90不同SKU/900计划组合不是实际量，实际未知不填0。10/12—17完整六工作日邀约5000；本周剩余三天及7店轮邀按真实完成状态和明确安排核对，不把缺失实绩当已做。该范围属于本项目此次排期，不变成其他项目或以后每周的固定九日标准。

## 当日计划的实时校时门（2026-10-08）

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 本项目排“今天”先用工具读取当前北京时间、回读真实已做，只排剩余到既定下班的可用分钟；上午已过待办移出当前执行，实绩保留。发布前与最终交付前分别再次工具校时，首槽已过则缩排或明确顺延并重新核边界，不倒填、不把空白当0、不自动叠明日或安排既定下班后加班。完整日10SKU/100目标不改，但当天目标、剩余可排量、实际、欠量分列。10/8原600分钟完整日已替换，当前19:30下班；未来10/9—17完整日不受此例外降低。恢复当前项目最新回执，不能把旧日程分钟通过当当前时刻仍可执行；只读时间校验见`scripts/validate_weekly_task_rollover.py`的`remaining_day`。

## 十店每日飞书机器人摘要（2026-10-08）

用户要求每天8:30主动通知当天任务时，恢复[项目机器人段](../../项目/进行中/20260927_十店单人运营周计划.md)与[本人周期发送和云端要求](../../资源/来源索引/2026-10-08_飞书机器人每日0830任务私聊.md)。本项目原生飞书云端DAILY已启用，Asia/Shanghai，自10/9 08:30；送达确认仍pending。不得把已启用、发送中、消息节点成功、用户收到和已读混为一谈，旧应用连接试发和本地19测试不代替当前云端工作流验收。

原Sheets347218为唯一任务权威，提醒Base为日期明确的分发副本。每次原表发布回读后同步摘要/状态并作废旧日期；用户手动只改Sheets未同步不会自动反映，必须告知。原“每次08:30立即读Sheets”是AI旧实现选择，非用户硬要求。云端查当天唯一记录，休息/缺失/重复记录明确提示，不发昨日任务，不虚构合格SKU、素材或完成量。

按日期先查日志再写发送中，防顺序重复和未知结果盲重试；不保证并发exactly-once。两条互斥消息分支各自有独立成功标记，服务可能规范化丢失共享后继，写后必须回读真实路径；结构通过仍不等于送达。已有直接授权无需再问同范围本人周期消息许可，不扩大他人/群/达人/源表写入；用户要求cloud_required，不退回本机Scheduler。生产配置/身份/回执沿productionWorkRoot/commerce-planning/feishu_daily_brief，知识库不存接收标识或凭据；下一次正式08:30核日志与本人收件。

**最新显示准则**：用户要求“当日计划的工作总结”，不是表格。08:30单条消息按工作块归纳，明确店铺、SKU/待筛状态、数量和视频重点，直接看即可执行；禁止逐时段原样搬运、发表格或靠“打开任务表”完成说明。原表仅作后台权威，消息无需链接/按钮。格式更新要回读真实云端文字，不以旧长表内容通过；启用、消息结果与收件pending仍分别保留，先恢复cloud_active_state.json。

本批10/9—17九条工作摘要已于19:13:56逐全文回读，无URL/表格/逐时段表，两个消息节点均无按钮；当前最多430字、6—7工作块只是本批结果，不升级长期数量限制。enabled保持、收件仍pending，恢复先读cloud_active_state与cloud_summary两份当前回执。

## 每次上架更新的必做收尾（COM-016，2026-10-10）

用户明确要求“以后每次更新店铺上架产品的时候都要同步一下”。对当前十店，每次实际完成已授权上架、在线商品更新或产品表刷新，都继续同步原飞书总览，不限周更、不需重复提醒。先恢复 `项目/进行中/20261010_十店SKU总览与飞书任务闭环.md`；以更新后核验的来源刷新商品、各店明细、SKU 索引/查询、派工价格参考和 Npcs 核对，标明各店真实数据日期。保留原任务、备注与完成状态，未完成任务目标变化先列差异，不把旧完成套给新链接。

**完成门槛：店铺更新＋飞书同步回读核验均通过。** 飞书失败时保留待补同步记录，报告未同步店铺及旧日期，不称整项完成。只写本地文案草稿不算实际上架；不因此建立后台定时监控或扩大线上操作授权。来源：`资源/来源索引/2026-10-10_上架产品更新必须同步飞书.md`（相对知识库根）。

## 2026-10-12 当前仓库价格源

用户指定10.12表替换9.12仓库源；以 current-warehouse-source.json 为准。887个精确SKU，96个新品均缺Y仓活动价，不能当成最终可用价；现有十店530条本地Flash价差0。详见知识库 `资源/来源索引/2026-10-12_印尼仓库SKU价格来源卡.md`。

## 2026-10-12 用户采用在线Y仓价格

价格2活动来源现为在线表 PLu3smtrShVmLItIJ6nccS0knab 的0hArmx页C列，来源指针current-warehouse-source.json已登记。每次使用前读取在线现值并核对本地快照；原Y文件留作历史，不优先使用。公式仍双源取低与Npcs单件最终价乘数量；缺价/同SKU多价阻断，不擅自选最低冲突价。626单品缺价格1例外按本次用户选择使用在线当前价格2（本次55520，旧59520仅历史）。详见知识库`资源/来源索引/2026-10-12_在线Y仓活动价作为当前价格2.md`。

## 2026-10-12 十店选品：外部市场机会与同公司竞争

本用户选品/重选时先读 [市场机会优先、同公司竞争辅助](references/market-opportunity-company-competition.md)，再走selection RUNBOOK。外部需求和可进入空间为主；公司做得越好首先提示内部竞争，不能正向抬高推荐；Kalodata同公司链接不当独立证据。用户要求重新开始时撤回旧名单，不保留旧名额；先市场再匹配货盘与排查公司竞争，详见来源和回归。

<!-- flash-guard-20261018:start -->
## 2026-10-18 十店闪购期限与风险例外

十店排班、早巡、本人提醒及Flash接续先恢复[到期防漏参考](references/flash-deal-expiry-guard.md)和[当前项目](../../项目/进行中/20260927_十店单人运营周计划.md)。按每店真实到期倒排，固定星期不能代替；当前用户单场上限72小时，提醒不代表续好，实际新期限须有完成证据。West Lip mask为user_reported_risk_hold，退出待上架派工；18日前完成保留该未上架例外，不推导数量。具体提醒时刻取本轮部署回执，不晋升永久阈值；既有价格、商品、授权及禁桌面控制边界保持。
<!-- flash-guard-20261018:end -->
