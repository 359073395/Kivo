---
name: knowledge-iteration
description: "Maintain the user's portable local knowledge base: register incoming sources, update indexes and logs, run health checks, archive work, save project summaries, refresh manifests, and create local conversation handoffs when the user asks to 收入知识库、知识体检、复盘、整理归档、备份当前会话或换电脑继续. Use knowledge-distillation instead when the main task is to convert video/PDF/documents into text or distill a source or work process into reusable knowledge or Skills."
---

# Knowledge Iteration

Operate the portable local knowledge base that contains this Skill. It must not depend on Obsidian, Baidu Netdisk, or a cloud knowledge service.

## Resolve the vault

1. Find the nearest ancestor containing `knowledge-base.json` from the task/input path; otherwise inspect the resolved target path of this loaded Skill, then `KNOWLEDGE_BASE_ROOT`, and use `D:\Knowledge` only when its marker exists. A work directory outside the vault is not evidence that the vault is unavailable.
2. Read `AGENTS.md`, `首页.md`, `资产/规则/规则权威与变更协议.md`, `资产/规则/活动规则总表.md`, `辅助/规则效果/README.md`, `辅助/日志/知识库日志.md`, and `辅助/摄入队列/摄入队列.md` from that root.
3. Read `资产/规则/蒸馏知识自动调用与Skill同步协议.md` and use `资产/规则/七个主Skill自动运营总图.md` when auditing routing or completed distillations.
4. Keep every internal link relative to the vault root.
5. Read only the reference required for the selected mode.

## Choose a mode

- **Ingest / route**: register a source, check duplicates and completeness, then use `knowledge-distillation` when source conversion or distillation is required. Read [references/distillation-workflow.md](references/distillation-workflow.md).
- **Maintain**: audit duplicates, freshness, links, queues, project state, feedback, and Skill candidates. Read [references/maintenance-workflow.md](references/maintenance-workflow.md).
- **Session handoff**: when the user asks to back up/save/archive the selected Codex conversation or continue on another computer, create a local handoff under `项目/会话交接`. Read [references/session-handoff.md](references/session-handoff.md).
- **Archive**: preserve final state, reason, restart condition, and links under `归档/`; do not delete the source evidence.

## Required loop

For knowledge work, run: input → digest → output → feedback → log.

Before routing any distillation, read the vault-level authority `资产/方法论/知识蒸馏总规则.md` and the dedicated `skill/knowledge-distillation/SKILL.md`. The shorter reference in this Skill is an intake route, not a substitute for the distillation Skill.

- Check duplicates and freshness before creating a page.
- Separate facts, author views, agent inferences, conflicts, and unknowns.
- Audit unresolved conflicts before closing a distillation. If authority cannot decide a conflict that changes the conclusion or Skill route, keep it `conflict_pending_user` and require the user's decision before finalizing that part.
- Update existing authoritative knowledge before creating a near-duplicate.
- Link compiled claims to their sources or source cards.
- Return missing evidence and next questions to the queue.
- Save reusable outputs, decisions, failures, and operating experience back to the vault.
- For every completed distillation, verify that it records an existing-Skill destination and that user-confirmed/validated methods are reachable from the relevant active Skill; a knowledge asset with no execution route is incomplete unless it is deliberately reference-only.
- For user-approved or batch-validated methods, require an executable behavior regression and run it during maintenance. Structural Skill validation, JSON parsing and link checks are necessary but do not prove that a new task will recover the correct project or choose the approved route.
- For workflows with a test-to-batch gate, reconcile `资产/规则/最新批量批准标准索引.md` against project state. The latest user-authorized batch version for the same scope is active; a newer unapproved test stays candidate and must not replace it.
- Aggregate new machine-local rule-effect signals with `辅助/维护/Update-RuleEffectSummary.ps1`. Keep raw signals outside the vault; write only cross-task patterns or review candidates to portable assets. Never auto-disable a rule, and do not count `prevented_error` as no effect.
- Run `辅助/维护/Test-RuleTraceability.ps1`; missing legacy direct evidence is a visible backfill warning, while any new/modified active rule without direct evidence is an error.
- Add a concise entry to `辅助/日志/知识库日志.md`.

## Storage boundary

Save Skill, rules, knowledge, final Markdown transcripts/manuscripts, project summaries, manifests, and final retrospectives in the vault. Keep original video/audio/PDF binaries, frames, temporary transcription/OCR caches, B-roll, HeyGen base videos, ChatCut projects, final media files, and temporary downloads in the configured external local work directory. Store their paths, hashes, state summaries, and recovery conditions in the vault.

## Completion gates

- **Knowledge update**: source registered with completeness status, required final text manuscript present, duplicate/freshness check completed, at least one authoritative knowledge asset materially updated, trigger/execution/judgment/check/stop fields compiled when applicable, Skill routing/sync decision recorded, user-approved/validated methods covered by behavior regression, gaps returned, and log updated. A session handoff or an isolated summary with no deliberate execution route is not a completed distillation.
- **Session handoff**: handoff folder created, `HANDOFF.md` completed, `metadata.json` present, secrets excluded, next action and cautions recorded, and log updated.
- **Maintenance**: issues classified by evidence/impact, safe repairs separated from approval-required changes, and no substantive merge/delete performed without authorization.

Never publish, upload private knowledge, send external messages, create cloud automation, delete evidence, or perform high-impact merges without explicit user approval.
