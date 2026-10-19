---
name: ip-commerce-decision-system
description: Apply the user's already-distilled decision system to personal IP, short-video commerce and TikTok Shop choices. Use for 个人IP定位、账号规划、内容矩阵、带货策略、商业路径、短视频复盘 or decisions based on accumulated experience; use knowledge-distillation for learning courses, books, videos or building new Skills.
---

# IP Commerce Decision System

This Skill is not merely a knowledge lookup. It defines what to do when a situation occurs, which experience applies, how to execute, how to judge, how to check and when to stop.

## Resolve the knowledge base

Find `vault_root` from the nearest `knowledge-base.json` marker above the task/input path, this loaded Skill's resolved target path, `KNOWLEDGE_BASE_ROOT`, or finally `D:\Knowledge` only when its marker exists. Execution guidance stays under this Skill's `references/`; knowledge assets live under `vault_root/资产/个人IP/`. Do not use stale absolute paths from an old computer, and do not assume an external working directory means the vault is absent.

Read:

- `../../资产/规则/规则权威与变更协议.md` and `../../资产/规则/活动规则总表.md` before treating remembered methods as rules.
- `../../资产/规则/蒸馏知识自动调用与Skill同步协议.md` and `../../资产/规则/七个主Skill自动运营总图.md` so applicable approved knowledge is used without waiting for the user to name it.
- `../../资产/方法论/知识库思考框架与运行流程.md` for the portable end-to-end startup, reasoning, action-feedback, writeback and stop process.
- `references/decision-protocol.md` for every decision task.
- `references/deep-reasoning-protocol.md` when the decision is non-routine, high-impact, novel, repeatedly failing or built on doubtful assumptions.
- `references/knowledge-paths.md` to route evidence.
- `../../资产/个人IP/方法卡/published-method-cards.md` for reviewed proprietary methods when relevant.

## Choose the decision domain

- `personal_ip`: the primary asset is a person, identity, expertise, trust, audience or long-term conversion.
- `commerce_video`: the primary asset is a product, demand, product card, shop, live room or transaction path.
- `combined`: an expert/founder/creator account must also sell products or services.

Do not organize the answer by course name unless source tracing is requested.

## Decision loop

1. Recover the latest action, real result, anomaly, user correction and project state. Feedback is the first input of the next cycle, not a final review stage.
2. Define the current decision unit: object, objective, owner, market/stage, time horizon and irreversible risks. Separate facts, constraints, conditional patterns, assumptions, conflicts and unknowns.
3. Route the problem before reasoning: pure fact → direct answer with source level; pure execution → verified RUNBOOK plus hard gates; judgment/choice → both fixed filters and the objective compact/deep qualification gate; value/emotion/ethics → the user's terminal values; mixed tasks → separate facts, terminal values and implementation means. If a reasonable value-order change flips the ranking, ask the user for that value choice.
4. Retrieve only applicable active/reviewed methods and current evidence; rank by authority, recency, specificity and proof. Candidate material may suggest a probe but cannot silently drive the decision.
5. For every judgment, internally form the Mao filter (`contradiction stage`, `main contradiction`, `pace`) and the first-principles filter in parallel. The latter keeps exactly three checkpoints: a no-proper-noun equation, the `leverage variable` and `boundary constant`, and at least two hidden assumptions labeled only `可承受风险` or `致命风险`. Each field must observably change, confirm or reject a prediction/action, or prevent an error; otherwise record `no_material_effect` and recheck routing/problem definition. Do not skip `IP-004` or invent a coupling. In ordinary replies, translate only useful results into natural rationale; expose the bounded audit record only when explicitly requested.
6. Let the current main contradiction and the action outline co-emerge: every contradiction judgment must imply an action and expected signal; every proposed action must identify the contradiction, stage and structural lever it touches.
7. Use the compact path only when every qualification in `references/deep-reasoning-protocol.md` passes. Any correction, readback anomaly, disproved assumption, unexpected event, rule conflict or new irreversible/high-cost authorization immediately upgrades to the full loop.
8. Apply hard gates, then take the smallest authorized action whose feedback can discriminate among the current judgments. For irreversible/no-feedback decisions, do not force a pilot: audit load-bearing assumptions, run counterexamples/worst cases, preserve options, predeclare veto/delay signals and leave the final commitment to the user.
9. As soon as feedback appears, update stage, structure, load-bearing assumptions, main contradiction and next action together. Stop, continue, upgrade, downgrade or change direction according to predeclared signals.
10. Check factual, strategic, commercial, compliance and operational consistency throughout the loop, not only at delivery.
11. Write back each cycle as prediction → action → feedback → what changed → next probe. Emit only observable rule-effect signals, never hidden reasoning. Propose—never silently activate beyond the user's confirmed scope—rule changes.

## Default delivery

For personal IP, cover positioning, target user, trust assets, commercial path, content matrix, topic sequence, scripts, filming/editing, conversion and review.

For commerce video, cover demand, purchase situation, selling reasons, trust proof, content matrix, visual demonstration, product-card/live/private-domain handoff and CTR/CVR/GMV review.

Every recommendation must include:

- current facts and unknowns;
- applicable experience and why it applies;
- action sequence and owner;
- measurable judgment signals;
- risks, stop conditions and what would change the decision.

The normal user-facing answer must not display framework/course names, filter headings, or the fixed internal checklist. It should state the recommended action and explain why it is appropriate now, including only the relevant evidence, causal reason, material assumptions/risks, verification signal and stop/change condition. Reveal the internal framework only when the user explicitly requests a framework view, source trace or audit record.

## Learning and rule updates

Route new books, courses, videos, PDFs and personal-skill extraction to `knowledge-distillation`. New material is evidence, not an active rule. Preserve sources, conflicts and scope; update an active method only after review, validation and rule-register update.

When the user explicitly confirms that a distilled, bounded method should be used automatically, treat that confirmation as authorization to connect the method to the relevant existing Skill after conflict checks; it is not authorization to activate every source claim.
