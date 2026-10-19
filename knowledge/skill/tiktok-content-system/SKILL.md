---
name: tiktok-content-system
description: Create and continue the user's TikTok Indonesia content workflow for viral-reference learning, paid-traffic creative strategy, high-fidelity original rewrites, follower-growth videos, commerce scripts, product-safe images, pure HeyGen talking-head videos, presenter B-roll videos, and ChatCut editing. Use when the user says 涨粉视频、爆款拆解、仿写、带货文案、投流素材、千川素材、广告创意、数字人口播、HeyGen、B-roll、混剪、ChatCut、完整带货视频或视频续跑.
---

# TikTok Content System

Use one content entry point and route internally. Seedance is archived and unavailable unless the user later explicitly restores it.

Before applying any remembered workflow, read `vault_root/资产/规则/规则权威与变更协议.md` and `vault_root/资产/规则/活动规则总表.md`. A directory or procedure from an old video task is not a global rule.

For every content run, also read `vault_root/资产/规则/蒸馏知识自动调用与Skill同步协议.md` and `references/distilled-method-routing.md`. Automatically use the relevant active method—such as wide-entry/narrow-landing A/B, differentiation, controlled variation volume or ethical desire hooks—when its trigger matches. Do not wait for the user to name the method, and do not force all methods into every video.

When a workflow uses test/sample approval before batch execution, read `vault_root/资产/规则/最新批量批准标准索引.md`. For the same mode and scope, the latest tested version that the user explicitly authorized for batch execution is the current standard. A newer sample without batch authorization remains candidate and never replaces it.

## 2026-10-16 下次排班参数覆盖

先恢复[十店项目](../../项目/进行中/20260927_十店单人运营周计划.md)与其[10/16来源](../../资源/来源索引/2026-10-16_上午工作实测与每店五链接目标.md)。用户一周测试反馈上午可完成统计数据和邀请达人，准确分钟未知，未证明全部回复/翻译/寄样也完成。以后新计划每天每店5条新测试链接、十店50条；沿用十店同组与每SKU首测一套，执行为每天5个不同SKU。达人配额不变，产品链接素材和视频素材分开、找视频素材与制作分别留时。50条是计划目标，非实绩或整日容量验收。下方旧10/100、10/8—17的90/900及240/120分钟仅为已发布历史依据，不再强制下一次新计划；本次不改云端旧任务或机器人。

## Resolve storage first

1. Resolve `vault_root` in this order: nearest `knowledge-base.json` above the current task/input path; nearest marker above this loaded Skill's resolved target path (including a Codex junction); `KNOWLEDGE_BASE_ROOT`; then `D:\Knowledge` only when its marker exists. A task working directory outside the vault is normal and must not be treated as “no knowledge base”.
2. Read `vault_root/辅助/配置/machine-paths.local.json`.
3. Store only rules, knowledge, summaries, manifests and final retrospectives in the vault.
4. Store source video, frames, temporary transcripts/OCR, product images, generated media, B-roll, HeyGen bases, ChatCut projects and final videos under the external local `productionWorkRoot`; store the final cleaned Markdown transcript in the vault.
5. Never put temporary production data in Baidu Sync, the Skill directory or another sync folder.

For `pure_heygen`, run `modules/pure-heygen/scripts/workspace_state.py recover` before asking for a path or creating folders. It must search active project summaries and `ACTIVE_TASK.json`, reject duplicate/near-duplicate task trees, and report whether the project already has an approved sample. Read [the validated pure-HeyGen baseline](modules/pure-heygen/references/validated-production-baseline.md) before preparing any presenter or calling HeyGen.

## Mode router

| User phrase or outcome | Mode | Required module |
|---|---|---|
| 涨粉视频、0703、静态字幕涨粉 | `follow_growth` | `modules/follow-growth/RUNBOOK.md` |
| 学爆款、拆结构、写印尼带货文案、准备素材 | `content_preparation` | `modules/content-preparation/RUNBOOK.md` |
| 千川素材、投流素材、广告创意、放量素材 | `content_preparation_paid` | `modules/content-preparation/RUNBOOK.md` + `references/distilled-method-routing.md` |
| 做数字人口播、纯数字人口播 | `pure_heygen` | `modules/pure-heygen/RUNBOOK.md` |
| 做带 B-roll 的完整带货视频、完整混剪 | `presenter_broll_mix` | `modules/presenter-broll/RUNBOOK.md` |
| 普通真人口播剪辑、口播可编辑 | `editable_aroll_chatcut` | `references/chatcut-editing-rules.md` |
| 只找对标或仿写 | `benchmark_rewrite` | `references/benchmark-rewrite.md` |

If wording is unambiguous, route automatically. Ask only when the requested output would materially change between pure HeyGen and a full B-roll mixed video.

`千川` is treated as paid-traffic/advertising context. Reuse transferable creative mechanisms, but never import platform-specific buttons, fixed thresholds, moderation loopholes or algorithm claims into TikTok without current verification. Route spend, ROI, ECPM and GMV Max data diagnosis to `tiktok-commerce-operations`.

## Locked production definitions

### Pure HeyGen

“做数字人口播” means a stable 9:16 HeyGen presenter video with no B-roll. Recover the current task first. If real product inputs and approved script/audio exist but the presenter is missing, automatically route through `content_preparation` to create one SKU-specific candidate, lock the real product layer and locally validate it; do not ask the user to choose this internal route. Respect the current project's existing image/video approval state, generate strictly serially, download, validate and report. Do not silently add ChatCut mixing.

### Complete B-roll commerce video

“做带 B-roll 的完整带货视频” means:

`verified product facts -> high-fidelity original script -> GPT presenter/scene plate -> locked real-product composite -> user final audio -> HeyGen lip-sync base -> authorized B-roll/product materials -> ChatCut overlay mix -> validation`

The user's final audio is the locked master timeline. Once hashed and accepted, do not cut, reorder, rewrite, replace, regenerate or time-stretch it without explicit approval. B-roll overlays may cover the presenter image while the master audio remains continuous.

## Benchmark and originality rule

- When the user provides a benchmark, default to high-fidelity structure mirroring: duration, section count, sentence count, hook location, information density, pain/selling-point order, emotion curve, CTA position and shot function.
- Reuse mechanics, not protected expression, identity, exact wording, music or footage.
- Every product claim must return to the current SKU fact card.
- Classify a reference as `skip_bgm_only` only when it contains neither intelligible speech nor meaningful on-screen sales text. Unclear audio becomes `needs_manual_audio_review`, not pure BGM.

## Shared gates

- 同一SKU的图中文字、视频稿与Listing共用资料时，按需读取[产品资料与一致性补充工具](../tiktok-commerce-operations/references/commerce-quality-tools.md)。消费原SKU事实和素材版本，追加字段/数值/单位检查；未知项不编造，不新要求市场研究、九图或多套首测。脚本核对的是文本，真实产品图、配音和成片仍按本Skill既有验收。

- Missing real product images or shop-specific product facts blocks the affected SKU.
- Rights, consent, policy and factual checks must pass before generation.
- Product shape, packaging, label, logo, capacity, count and color are invariants.
- Do not rely on an image model to redraw real packaging, label text, logo or product count. Generate the person/scene/pose, then preserve the real product as a locked source layer and reject any drift.
- For product-holding presenters, the locked real product must fully cover the generated placeholder. Preserve physically correct hand depth: thumb/foreground fingers in front, supporting fingers behind. Reject any placeholder residue, pasted-on appearance, floating, detachment, duplication or morphing.
- Assign one unique presenter identity per SKU. Keep that presenter consistent within the SKU, and never reuse the same identity or face for another SKU in the same batch.
- Derive the presenter, setting and action from verified product selling points, target audience and real use scenario. “One new person per SKU” is only an identity constraint; age, styling, room and pose still need a product-specific reason. Default to natural Indonesian daily-life realism: unretouched skin/hair, soft natural light, visible environment texture and slight lived-in imperfection, medium saturation, low contrast and ordinary phone/CCD candid rendering. Reject hyper-clean studio polish, plastic skin, strong filters and generic reused personas.
- A white/transparent product image locks product identity but does not automatically provide trustworthy scene lighting or perspective; it may be edited, rendered or AI-made. Assess the source before compositing, match the presenter/camera to its usable viewpoint, transfer only broad scene lighting, and never distort packaging or label geometry to force a fit.
- Every product interaction must be physically achievable. Inspect the shoulder/elbow/forearm/wrist/hand chain, grip support, center of mass, finger depth and contact shadows. Impossible wrist angles, isolated fingertips, penetration, floating, or pose repair by stacking masks are rejection conditions. Read [the product-presenter image standard](references/product-presenter-image-standard.md) whenever a person holds, supports, uses or displays a SKU.
- For this verified pure-HeyGen commerce workflow, use 720x1280 soft phone-camera rendering as the default visual baseline. Do not default to hyper-sharp 1080p unless the user explicitly changes the standard.
- Remote generation is serial and idempotent; an existing remote ID must be queried, not recreated.
- A presenter-image approval is valid only for the exact `SKU + final file path + SHA-256 + version` that the user reviewed. It never transfers to another SKU, an earlier draft, a later derivative, or a visually similar file. Any post-approval edit changes the hash and returns that SKU to image review.
- Before each HeyGen submission, bind that exact approved image hash to the actual remote `avatar_id`/asset ID and verify the remote thumbnail or preview shows the same presenter, product and scene. Save the remote ID and binding evidence in task state. If the backend cannot expose or verify the remote input, stop; never rely on the currently selected or previously used avatar.
- The first rendered sample must be compared against the approved image, not merely checked for internal frame stability. Presenter identity, exact SKU/product packaging and scene must match at the opening, middle and ending frames. Any wrong person, wrong SKU, old avatar, placeholder residue or product drift rejects the render and blocks the batch. Decode success and stable motion are not visual approval.
- Test the first item through download and validation before batch generation unless the user has already approved the batch in this run.
- When the user explicitly authorizes batch execution, atomically snapshot the active standard ID, method version, scope, approval time/task, approved sample/input hashes, quality gates and superseded standard. Future matching tasks use that pointer automatically; do not ask the user to restate the approved requirements.
- Never auto-publish.

## Completion contract

Do not mark a video ready until the required local files exist, decode successfully, match the intended mode, preserve the product, keep audio intelligible, respect safe captions and disclose synthetic content where required. Save a task summary and final retrospective to the vault; keep media in the external work directory.

The task summary must record which active distilled method IDs were used, the tested variant, success signals, stop conditions and actual result so future runs can refine the method. A user-approved or batch-validated result must also update the corresponding behavior regression; structural validation alone is insufficient.

## Commerce campaign coordination (COM-014)

For 打品/跟品、自营视频周期规划 or creative work within an existing commerce campaign, recover the exact SKU/store plan through [the commerce planning entry](../tiktok-commerce-operations/references/product-campaign-planning.md). Map each video to its selling point, audience, scene, evidence, destination and release window. Use the shared three-set title/cover/detail matrix; video counts remain campaign-specific. For an already approved production task, continue its existing baseline and fill only the missing planning context; do not restart approvals or replace production modes. This planning rule never grants generation, publishing or spending permission.

## 公司手册方法补充（COM-015）

任务涉及对标/脚本/素材迭代用04；按卖点×人群×场景接回总控时，读取[公司手册方法入口](references/company-manual-methods.md)，按触发条件补足证据与检查。仅相容流程为active_process_only，数字、政策与算法解释仍受来源核验门；不要加载整套教材代替回答当前问题。

## 十店单人内容排期衔接

为用户当前十店编排链接资料/视频素材/制片与跨店投放计划时，先恢复[十店单人项目](../../项目/进行中/20260927_十店单人运营周计划.md)。准备量按SKU与卖点版本统计，跨店复用不重复算完整制作；逐店PID/可售核对仍独立。先安排真实素材搜索，再明确视频是已出单老品的角度扩展还是新品验证；周报与实际耗时更新下周，不沿用固定SKU单店和永久重点店。

## 十店当前产能安排覆盖（2026-09-30）

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 先恢复[十店最新项目](../../项目/进行中/20260927_十店单人运营周计划.md)：每日10个跨品类非相似SKU、十店同组、首轮每SKU一套链接；旧A/B三套首测前置已替代，视频产量按素材与容量规划。2026-10-08纠偏：没有用户取消5000邀约配额的证据，旧“不自动恢复5000”是AI误推；重点3店每天各200、其余7店每周各200轮邀仍须遵守，完整6工作日5000。不足周按实际工作日和7店轮邀安排说明目标，90分钟AI预算不授权缩量，不把计划量当已发送。BD在此项目明确为品牌认证，不能放进达人建联统计。达人保持连续工作块按实耗排；视频先收真实素材，优先支持有卖货信号SKU；假期仅可选轻量链接和视频素材收集。没有扩大外发/发布权限。

### 本项目最新手动日预算与视频时段（2026-10-08）

**历史数量适用范围：2026-10-08已发布版本；后续新计划按上方2026-10-16的5/50。** 用户最新估计为每日链接资料240分钟、十店手动上传120分钟，两项360分钟；每日上限600分钟、每周6天、手动5店一组两组不变。24分钟/套及12分钟/SKU十店仅是平均预算反推，非逐SKU实测；旧30/20分钟单位估时归历史，不再×100或÷5。每日10不同SKU/十店100条、完整周5000邀请及既有其余预算保持。找视频素材与制作成片必须独立排时段，素材没齐先找，不将计划搜索当已有素材；具体视频分钟/条件产量沿当前项目已回读日程恢复，仅为本次预算。预算分钟算术已通过、实际耗时及SKU准备仍未确认，不以360分钟核心预算证明全天通过，不假定等待并行/素材提速、不强推ERP批量。原话与当前状态沿既有十店项目恢复。

当前范围依用户最新要求为10/8—17，10/11休息，共9工作日；90不同SKU/900计划组合不是实际量，实际未知不填0。10/12—17完整六工作日邀约5000；本周剩余三天及7店轮邀按真实完成状态和明确安排核对，不把缺失实绩当已做。该范围属于本项目此次排期，不变成其他项目或以后每周的固定九日标准。
