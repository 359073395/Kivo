# Conversation Context

## Durable Objective

The user runs TikTok e-commerce across multiple seller entities and wants a standalone product-selection Agent, not a weekly-plan generator. The system must work with or without an owned SKU library.

The approved formula is:

`platform data + owned historical/inventory/profit data + rule scoring + memory review = automated selection decision`

Owned business data enters through a dedicated data-import layer and is retained in a SKU asset library. Market-only selection can start from a region, category, keyword or efficacy direction.

## System Direction

The system was inspired by an engineering-oriented multi-Agent selection workflow:

- separate program execution from AI judgment;
- Hub, Eagle Eye and Furnace agents have independent roles;
- use a persistent state machine and locks instead of direct Agent conversation;
- apply five-layer quick screening before full data injection;
- cross-check mathematical and business/LLM scores;
- retain only decision-useful recent memory;
- feed test and advertising results back into the next decision;
- propose learned rule changes and require human approval.

The local application is under `apps/tiktok-selection-system`. It provides data import, SKU assets, market evidence, LinkFox tasks, scoring, VCP memory, test feedback, reports and production deployment files.

## Business Sources

Current authoritative product data is the final enriched Y-warehouse workbook. It contains exact SKU-level prices and bilingual product information; new-product status is matched by exact SKU against the `7.8 印尼所有产品及定价` source.

Store availability must be judged at `store + exact SKU` grain. A master SKU row does not prove a store has a live product link.

The five original creator-flow stores are:

- ZivaCosme-ID
- Nectar Beauty
- Sugar Spice
- ALAMI LAB
- Second-Skin

External-store tests are separate from the creator-account flow.

## Stable SKU Rules

Known hard or strong exclusions:

- SADOER CASTOR OIL
- EE 10 Seconds
- GLUTA WHITENING
- 24HR SETTING
- OUHOE Yellow Oil
- HUNMUI Lip
- products containing Vaseline or 凡士林

`Morning Cherry Toothpaste` was replaced by `Seawater Nasal Spray`.

Scar-sheet mappings:

- Scar Sheet03 = EELHOE
- Scar Sheet04 = West Month
- Scar Sheet05 = Taerikpru
- Scar Sheet06 = Vibrum

`HK Active Oil` and `AHA` may be evaluated when current evidence supports them.

Do not repeat creator-account tested SKUs in external-store tests. The conversation explicitly applied that rule to:

- Dragon Blood
- Seawater Nasal Spray
- Sulfur XUERMI
- 563-Gloow&be Sunscreen
- KOJIC FACE WASH

Scar Sheet05 had no completed creator video at the time of the operational plan and could not be scheduled as already-produced content.

## Test Logic

The user values breadth of SKU discovery over repeatedly testing the same high-volume item. For external stores, the established rhythm was:

- one SKU per store for two consecutive days;
- five different script directions per day;
- ten videos per store-SKU block;
- use pain point, price/COD, real experience, competitor/market validation and comment/scene angles;
- day two changes hooks, scenes or benefits;
- evaluate the store-SKU combination, script, account and natural/advertising traffic separately.

Only generate a formal plan when market evidence, exact store listing, inventory, profit and other required readiness fields are valid.

## External Integrations

- LinkFox/FastMoss is the primary market-sales/GMV/growth source.
- TikTok Business MCP is for authorized owned advertising/account data, not whole-market research.
- Multiple seller entities require separate valid authorization or an approved ISV path.
- Feishu, TikTok, LinkFox and LLM credentials are intentionally not portable in this backup and must be reauthorized.

## Thread Identity

- Original Codex task ID: `019e9c3f-dd93-7c33-a742-4efd201fc882`
- Original task title: `筛选主推SKU`
- Portable Skill name: `xuanpin`

