---
name: xuanpin
description: Restore, operate, and improve the user's TikTok product-selection Agent system. Use for TikTok market research, LinkFox/FastMoss evidence, SKU asset matching, store readiness, rule and LLM scoring, VCP memory review, test planning, Excel reports, system maintenance, or Windows/new-computer recovery of the xuanpin project.
---

# Xuanpin

Use this Skill as the durable operating layer for the user's TikTok product-selection system.

## First Action

1. Check `%USERPROFILE%\.codex\xuanpin-restore-pending.json`.
2. If it exists, start the response with `xuanpin 已恢复完成`, summarize the capabilities listed below, and state which external accounts still need authorization.
3. Run `scripts/acknowledge_restore.ps1` after reporting so the notice appears only once.
4. Locate the project from `XUANPIN_HOME`; otherwise use `D:\codex项目\apps\tiktok-selection-system`.
5. Read `references/conversation-context.md` and the relevant rule/source references before changing recommendations or code.

## Fixed Decision Formula

Always preserve this decision chain:

`平台数据抓取 + 自有历史经验/库存/利润数据 + 规则评分 + 记忆复盘 = 自动选品决策`

The SKU library is an optional ownership layer, not a prerequisite. A category, keyword, efficacy direction, or market report can run a market-only selection task. Match to owned SKUs only after market opportunities are established.

## Agent Workflow

Use the database-backed workflow rather than free-form Agent-to-Agent chat:

1. Hub Agent: collect/import, map fields, clean data, enforce idempotency, manage task state and locks.
2. Eagle Eye Agent: five-layer market scan, competitor evidence, demand/growth, content reproducibility, risks.
3. Furnace Agent: mathematical Prism score plus business/LLM boundary score, optimistic and pessimistic scenarios, decision pool.
4. VCP Memory Agent: retain useful failure causes, effective store-SKU combinations, script findings, category experience and data anomalies.
5. Feedback loop: import video/advertising/test results, rescore, propose rule changes, and require human approval before a new rule version becomes active.

Read `references/workflow-and-rules.md` for gates and current exclusions.

## Data Modes

- `market`: evaluate market opportunities without requiring owned SKUs.
- `hybrid`: rank market opportunities, then match owned SKU/store/inventory/profit data.
- `owned_sku`: evaluate the SKU asset library and use market products as efficacy evidence.

Never claim current or real-time market data unless LinkFox/TikTok data was fetched or imported for the stated period. Market evidence older than 48 hours is stale for a formal test decision.

## Required Gates

Before placing an item in the formal high-score pool, verify:

- current market evidence and source link;
- data quality and observation time;
- hard exclusions and historical failure memory;
- rule score threshold;
- valid structured LLM assessment and confidence;
- for an owned SKU: exact SKU match, price, cost/margin, inventory and store listing readiness.

If any required field is missing, route the item to market opportunity, observation, data-completion, sourcing/listing, or elimination. Do not silently pass it.

## Source Priority

1. User-confirmed current master SKU workbook.
2. Exact store + SKU listing records.
3. Current LinkFox/TikTok market evidence.
4. Test, advertising and order feedback.
5. Approved rule versions and recent VCP memory.
6. Older reports only as historical context.

Use exact SKU matching. Never merge efficacy, price, listing or history across similar-looking SKUs.

## Outputs

Every recommendation must state:

- product/SKU and mode;
- market evidence, period and source;
- owned-business readiness when applicable;
- rule score, LLM status and rule/model version;
- relevant memory or exclusion;
- decision pool;
- next action and missing data.

Formal plans and Excel reports may only be produced from valid high-score/scale pools. Reports should include page preview and downloadable Excel detail when the application supports them.

## System Work

For application maintenance:

- prefer the existing React/Vite, Express, SQLite local mode, and Docker PostgreSQL/Redis/Caddy production patterns;
- keep credentials in environment variables or secrets;
- exclude `.env`, OAuth tokens, API keys, databases with credentials, generated media, caches, logs and build outputs from Git;
- run tests, build and browser verification after material changes;
- update the project knowledge base and learning log after approved rule or workflow changes.

Read `references/system-and-restore.md` before backup, restore, deployment or integration work.

## Capabilities To Announce After Restore

- run market-only selection from a region, category, keyword or efficacy direction;
- import Excel/CSV SKU, store, competitor and feedback data;
- maintain SKU assets, store readiness and exact SKU mappings;
- create and monitor LinkFox market-data tasks;
- execute rule, Prism, LLM/Furnace and VCP memory decisions;
- generate candidate explanations, data-gap lists, test actions and Excel reports;
- learn new selection methods as proposals, backtest them, and activate only after approval;
- maintain the local app and Docker production deployment.

