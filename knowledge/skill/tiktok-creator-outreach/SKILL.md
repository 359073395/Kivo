---
name: tiktok-creator-outreach
description: Screen and prepare outreach to TikTok Shop creators from legally exported CSV, TSV or XLSX data; normalize evidence, preserve unknowns, rank review queues, rescore after human video and comment review, and draft unsent outreach. Use when the user mentions 达人筛选、达人建联、邀约、寄样候选、达人评分、达人导表、合作私信、达人复盘或 TikTok creator outreach.
---

# TikTok Creator Outreach

Use a two-stage funnel: free authorized export plus local processing, then limited human evidence review. Do not purchase data, scrape unauthorized sources or auto-send.

Before using thresholds or remembered campaign defaults, read the vault's `资产/规则/规则权威与变更协议.md` and `资产/规则/活动规则总表.md`. An old campaign brief or chat is not approval for the current campaign.

Also read `资产/规则/蒸馏知识自动调用与Skill同步协议.md`. During human content review, automatically use only relevant active content methods (audience/offer fit, differentiation, hook-to-product continuity and ethical persuasion) from `tiktok-content-system/references/distilled-method-routing.md`; do not let those methods silently alter creator scoring weights, thresholds or outreach permissions.

## 2026-10-16 下次排班参数覆盖

先恢复[十店项目](../../项目/进行中/20260927_十店单人运营周计划.md)与其[10/16来源](../../资源/来源索引/2026-10-16_上午工作实测与每店五链接目标.md)。用户一周测试反馈上午可完成统计数据和邀请达人，准确分钟未知，未证明全部回复/翻译/寄样也完成。以后新计划每天每店5条新测试链接、十店50条；沿用十店同组与每SKU首测一套，执行为每天5个不同SKU。达人配额不变，产品链接素材和视频素材分开、找视频素材与制作分别留时。50条是计划目标，非实绩或整日容量验收。下方旧10/100、10/8—17的90/900及240/120分钟仅为已发布历史依据，不再强制下一次新计划；本次不改云端旧任务或机器人。

## Storage boundary

- Resolve the knowledge vault from the nearest `knowledge-base.json` marker above the task/input path, this loaded Skill's resolved target path, `KNOWLEDGE_BASE_ROOT`, or finally `D:\Knowledge` only when its marker exists; then read machine paths from `辅助/配置/machine-paths.local.json`.
- Keep this Skill, rules, reusable scoring knowledge and final summaries in the vault.
- Write raw exports, normalized CSVs, review queues and draft messages to the external local work root, never inside the Skill folder.
- Never store account credentials, cookies, tokens or API keys in the vault.

## Non-negotiable rules

- `unknown` is not zero. Missing evidence stays unknown; do not redistribute its weight or create a false precise score.
- Separate observed facts, inference and items requiring human review.
- Nickname, avatar, follower count or one viral video cannot prove audience fit, stability or conversion.
- Generate only `pending_review` and `NOT_SENT` drafts.
- Sending, opening a conversation, changing commission, promising a sample, accepting a quote or granting usage rights requires explicit authorization in the current task.
- Offer, claims, deliverables and usage rights must come from an approved Campaign Brief.
- A/B testing starts only after enough real outcome evidence exists; do not label arbitrary variants A/B prematurely.

## Workflow

1. Confirm Campaign Brief: product, market/language, audience, goal, commission/sample/budget, deliverables, usage rights and prohibited claims. Read `references/campaign-and-data-schema.md`.
2. Validate the original CSV/TSV/XLSX without overwriting it. Auto-detect worksheet, header row and common Chinese/English columns. Read `references/local-export-workflow.md`.
3. Normalize handles, URLs, percentages and K/M abbreviations; deduplicate and apply hard exclusions.
4. Calculate only evidence-supported dimensions from `references/scoring-model.md`; retain coverage and possible score range.
5. Size the standard and deep-review queues from the current campaign scope and review capacity. Historical ranges may be proposed as candidates, not treated as user-approved defaults.
6. Human-review the recent 10–20 videos and representative comments for hook, demonstration, expression, production, stability, purchase intent, product-content ratio, CTA and risks.
   Record whether the creator can execute the current campaign's relevant active content method; assess demonstrated evidence, not hypothetical potential.
7. Rerun with the completed evidence table. Use A/B/C/D thresholds only when the Campaign Brief or activity register approves the current scoring-model version; otherwise return evidence coverage, score range and `pending_review` without pretending the historical thresholds are user-confirmed.
8. Create unsent messages only for approved complete A/B candidates using `references/outreach-playbook.md` and `references/prohibited-claims.md`.
9. After authorized human sending, record replies, samples, published videos, clicks, orders and GMV; update model proposals only after evidence and user approval.

Report the active distilled methods actually used in review, plus any method rejected for product, audience, evidence or compliance mismatch.

## Local scripts

Use `scripts/creator_outreach.py validate` before `run`. All runtime outputs must be directed to a task folder below the external work root. See `references/output-schema.md` for deliverables.

## Stop conditions

Stop or downgrade the affected candidate when market/language is known to mismatch, do-not-contact is explicit, the niche is unrelated, inactivity is prolonged, brand safety is unacceptable, budget is exceeded, critical evidence is unknown or the Campaign Brief is not approved. Never turn a draft into a sent message silently.

## Commerce campaign coordination (COM-014)

For creator videos in a 打品/跟品 campaign, recover the exact SKU/store plan using [the commerce planning entry](../tiktok-commerce-operations/references/product-campaign-planning.md). Add the campaign path, selling point, audience, scene, proof, destination link and delivery/release window to the existing Campaign Brief. Select creators for their demonstrated ability to reach that audience and show that proof; coordinate with self-produced videos in the same cycle. Keep sufficient-volume criteria campaign-specific. “Link weight attracts creators” remains an unverified user hypothesis, never a reason to promise inbound creators or abandon planned outreach. Scoring weights, draft-only status and sending/sample/commission permissions remain unchanged.

## 公司手册方法补充（COM-015）

任务涉及达人证据复核、交付/授权追踪用05；真实邀约草稿默认NOT_SENT时，读取[公司手册方法入口](references/company-manual-methods.md)，按触发条件补足证据与检查。仅相容流程为active_process_only，数字、政策与算法解释仍受来源核验门；不要加载整套教材代替回答当前问题。

## 十店单人排班衔接

为用户当前十店安排达人时间或周任务时，先恢复[十店单人项目](../../项目/进行中/20260927_十店单人运营周计划.md)。达人后台是连续工作块，合并翻译、回复、合作沟通、邀请、样品与交付跟进；统计可以分字段，排班不机械拆碎。已知手动邀请耗时不包含全部沟通耗时，不恢复固定10/15分钟回复预算。每周根据成熟经营周报与实际完成/耗时重排，OUT-001权限边界不变。

## 十店当前产能安排覆盖（2026-09-30）

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 先恢复[十店最新项目](../../项目/进行中/20260927_十店单人运营周计划.md)：每日10个跨品类非相似SKU、十店同组、首轮每SKU一套链接；旧A/B三套首测前置已替代，视频产量按素材与容量规划。2026-10-08纠偏：没有用户取消5000邀约配额的证据，旧“不自动恢复5000”是AI误推；重点3店每天各200、其余7店每周各200轮邀仍须遵守，完整6工作日5000。不足周按实际工作日和7店轮邀安排说明目标，90分钟AI预算不授权缩量，不把计划量当已发送。BD在此项目明确为品牌认证，不能放进达人建联统计。达人保持连续工作块按实耗排；视频先收真实素材，优先支持有卖货信号SKU；假期仅可选轻量链接和视频素材收集。没有扩大外发/发布权限。

### 本项目最新手动日预算与视频时段（2026-10-08）

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 用户最新估计为每日链接资料240分钟、十店手动上传120分钟，两项360分钟；每日上限600分钟、每周6天、手动5店一组两组不变。24分钟/套及12分钟/SKU十店仅是平均预算反推，非逐SKU实测；旧30/20分钟单位估时归历史，不再×100或÷5。每日10不同SKU/十店100条、完整周5000邀请及既有其余预算保持。找视频素材与制作成片必须独立排时段，素材没齐先找，不将计划搜索当已有素材；具体视频分钟/条件产量沿当前项目已回读日程恢复，仅为本次预算。预算分钟算术已通过、实际耗时及SKU准备仍未确认，不以360分钟核心预算证明全天通过，不假定等待并行/素材提速、不强推ERP批量。原话与当前状态沿既有十店项目恢复。

当前范围依用户最新要求为10/8—17，10/11休息，共9工作日；90不同SKU/900计划组合不是实际量，实际未知不填0。10/12—17完整六工作日邀约5000；本周剩余三天及7店轮邀按真实完成状态和明确安排核对，不把缺失实绩当已做。该范围属于本项目此次排期，不变成其他项目或以后每周的固定九日标准。
