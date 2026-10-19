---
name: linkfox-research
description: Use LinkFox Agent as an external cross-border e-commerce research and data-tool layer for Amazon, TikTok, eBay, Walmart, Shopee, Ozon, 1688, trends, keywords, reviews, patents, sourcing and structured analysis. Use when the user asks for LinkFox、跨境数据、平台调研、竞品、关键词、评论洞察、专利、供应商、市场趋势 or evidence for another local decision Skill.
metadata: {"LinkFoxAgent":{"requires":{"env":["LINKFOXAGENT_API_KEY"]}}}
---

# LinkFox Research

本用户十店2026-10-19—24按[本周直接指令](../../资源/来源索引/2026-10-19_本周先上链接测流量与成交.md)先上链接试测：外部市场验证、LinkFox额度/结果、对标销量渠道研究不作本周排期和资料准备前置，不因积分0反复提交或阻断整周任务。只有另有具体研究请求才进入本Skill研究；已有结果照原日期/口径使用，未知不写通过。此例外不永久废除外部研究方法。

Keep LinkFox as an external evidence tool, not the owner of business decisions. The requesting local Skill defines the question and decision gate; LinkFox supplies dated evidence and artifacts.

Resolve `vault_root` from the nearest `knowledge-base.json` marker above the task/input path, this loaded Skill's resolved target path, `KNOWLEDGE_BASE_ROOT`, or finally `D:\Knowledge` only when its marker exists; then read `vault_root/资产/规则/规则权威与变更协议.md`. Old tool catalogs and old result files do not become current facts.

Read `vault_root/资产/规则/蒸馏知识自动调用与Skill同步协议.md`. When another Skill requests research, inherit its decision question and applicable active-method evidence requirements; do not make the user restate which knowledge should guide the research.

## Portability boundary

- Rules, prompt patterns, tool references and final summaries belong in `vault_root`.
- Raw LinkFox JSON/CSV, downloaded files and temporary reports belong under the external local work root.
- API keys, cookies and tokens never belong in the knowledge vault.
- On a new computer, configure `LINKFOXAGENT_API_KEY` and `LINKFOX_OUTPUT_ROOT` or reconnect an installed LinkFox integration.

Read `references/portable-runtime.md` before execution. Read only the relevant platform reference file for tool parameters.

## Capability resolution

Use this order:

1. A callable installed LinkFox integration available in the current AI host.
2. The bundled `scripts/linkfox.py` with `LINKFOXAGENT_API_KEY`.
3. If neither is available, stop and report that the external function is unavailable; still provide a precise research plan or input template.

Do not claim LinkFox data was fetched when only public web data or user files were used.

## Research contract

For this user's ecommerce benchmarks, apply the [direct 2026-10-09 requirement](../../资源/来源索引/2026-10-09_对标必须提供可查验链接.md): request and return actual product-detail URLs for every benchmark, adjacent to its name and mapped to the user's SKU. Include original video/live/data evidence URLs when supporting a channel claim. A product ID, screenshot, search page, local artifact or tool success message does not replace a direct benchmark link. Read back the returned URL and product identity; disclose missing links, access restrictions and verification time. Do not invent URLs or claim a constructed URL was verified. Missing or inaccessible evidence remains pending and cannot be presented as a verified benchmark.

1. Receive a decision question from the user or another Skill.
2. Identify the requesting Skill, decision method/ID when applicable, platform, country/site, time window, product identity, metrics, filters and desired artifact.
3. Select the smallest suitable LinkFox tools using the platform references.
4. Exclude secrets, personal data and unpublished confidential strategy from the prompt.
5. Submit once, persist message ID and task metadata to the external output root, then poll the same task rather than duplicate it.
6. Preserve source time, platform, filters, missing fields and tool limitations.
7. Return evidence, artifacts and uncertainty to the requesting Skill. Do not turn market evidence directly into an approved product, price, claim or publish action.

If the request mentions `千川`, classify it as paid-traffic/advertising evidence. Research the current named platform requested by the decision owner; never assume 千川 mechanics, fields or thresholds are current TikTok facts.

## Tool choice principles

- Current Amazon storefront order: Amazon frontend.
- Rich Amazon product and history lookup: Keepa.
- Amazon product discovery: SellerSprite.
- Long-term history and FBA breakdown: Sorftime.
- TikTok market/product/video evidence: the relevant EchoTik or FastMoss tools.
- General web and WeChat research: LinkFox web search when available.
- Aggregation: intelligent data query first; Python sandbox only for custom structured processing.
- Patent, trademark or copyright tasks require the matching legal-data tool and must not be presented as legal advice.

Tool names and counts can change. Discover the currently callable integration first; use this Skill's `references/` only as parameter guidance and the archived snapshot only as history.

## Safety and completion

External submission requires a configured credential. Any action beyond research—uploading, publishing, altering listings, sending outreach or committing money—requires separate explicit authorization. Complete only when results are saved outside the vault, source limitations are stated and a reusable summary is handed back to the relevant local decision system.
