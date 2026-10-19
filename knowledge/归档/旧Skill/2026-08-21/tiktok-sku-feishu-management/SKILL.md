---
name: tiktok-sku-feishu-management
description: Use when managing the user's TikTok Shop SKU source folder, multi-shop product exports, Indonesia SKU pricing, Product Discount or Flash Deal upload files, cleared/delisted SKU checks, store-specific product ID mapping, or Feishu/Lark SKU dispatch and management sheets.
---

# TikTok SKU Feishu Management

Use this skill for the user's TikTok shop SKU control workflow. The user communicates by SKU, and the Feishu spreadsheet becomes the dispatch board for shop staff.

## Portable Data Root

Resolve the data root in this order:

1. Use the `TIKTOK_SKU_ROOT` environment variable when it is set.
2. If this skill is inside `<root>/05_可移植Skill/tiktok-sku-feishu-management`, use `<root>`.
3. On the user's main computer, use `G:\TikTokSKU` when that folder exists.
4. Otherwise, ask for the copied `TikTokSKU` folder path once and use it for the task.

Expected layout under the root:

```text
01_店铺上架产品/   current store export workbooks; filename identifies the store
02_SKU定价源/      latest SKU price/reference workbooks
03_官方活动模板/   reusable official templates such as Product Discount
04_输出结果/       generated audits, pricing workbooks, conflicts, and upload files
05_可移植Skill/    portable copy of this skill
06_工作脚本/       deterministic local pricing and comparison scripts
settings.json       machine-specific paths such as the Zhanfu browser download root
```

Treat `01_店铺上架产品`, `02_SKU定价源`, and `03_官方活动模板` as read-only inputs. Write reports under `04_输出结果`. Flash Deal upload files are the exception: write them beside each store's downloaded template in the Zhanfu browser folder. Never overwrite the original `Flash Deal.xlsx`.

Source selection rules:

- Read store listings only from `01_店铺上架产品`; ignore Excel lock files beginning with `~$`.
- Read price/reference workbooks only from `02_SKU定价源`. Never use a workbook under `04_输出结果` as a future pricing source.
- Treat the all-SKU reference workbook containing the cat-shop price and clearance/delisting status as one source role, and the Y-warehouse activity-price workbook as a separate source role.
- If more than one workbook can fill the same source role, prefer the file explicitly named by the user. Otherwise use the newest modified file and report the selected filename before calculating.
- Use the store filename as the store identity unless the workbook contains an explicit, more authoritative store name.

## Zhanfu Browser Download Root

Resolve the store template root in this order:

1. Use `ZHANFU_BROWSER_ROOT` when set for the current run.
2. Read `zhanfu_browser_root` from `<root>/settings.json`.
3. On the user's main computer, use `F:\zhanfudown\zhanfubrowser` when it exists.
4. Otherwise, ask the user where Zhanfu Browser downloads each store's files, then update `<root>/settings.json` before generating uploads.

Required store layout:

```text
<zhanfu_browser_root>/<店铺名>/Flash Deal.xlsx
```

The folder name must exactly match the store export workbook filename. Generate `Flash Deal_已填写.xlsx` in the same store folder so the user can upload it directly from the Zhanfu Browser download location. Keep `Flash Deal.xlsx` untouched for regeneration and verification.

## Core Rules

- Treat `SKU` as the user-facing key.
- A SKU can exist in multiple shops. If the user only names a SKU, apply the action to all shops containing that SKU.
- If the same SKU appears multiple times in one shop, the `待处理派工` page should show only one row for that shop+SKU.
- If the user names a shop and SKU, apply only to that shop.
- `待处理派工` must be the first sheet and must show only actionable rows: `下架`, `开预购`, `关预购`, or `待确认`.
- Normal products should not appear in `待处理派工`.
- Store tabs can show all SKUs and prices for reference.
- Price columns are `上架原价`, `日常售价`, `平台活动价`.
- Price matching uses exact SKU first. If missing, parse `Npcs<base SKU>` as a bundle containing `N` units of the base SKU.
- For `Npcs` price audits, calculate the average unit price as `actual bundle total / N`, then compare that average with the base SKU unit reference price. Never classify an `Npcs` SKU only from its bundle total.
- If price lookup fails, leave price blank.
- In `待处理派工`, prices should appear only for actionable rows so the first page stays clean.

## Feishu CLI

Use `lark-cli` for online sheet work.

On a new computer, install/configure `lark-cli` and authorize the Feishu account that owns or can edit the target sheet. Then check auth:

```powershell
lark-cli doctor
lark-cli auth status
```

If a command reports missing scopes, start device auth with `--no-wait --json`, send the raw verification URL to the user, and after they confirm run the returned `--device-code` command.

Bundled online scripts find `lark-cli` from `PATH`; they do not depend on a specific Windows user profile. Set `LARK_CLI` only if the CLI is installed in a nonstandard location.

Useful commands:

```powershell
lark-cli sheets +info --as user --spreadsheet-token <token>
lark-cli sheets +read --as user --spreadsheet-token <token> --range '<sheetId>!A1:J10'
lark-cli sheets +write --as user --spreadsheet-token <token> --range '<sheetId>!A1:B2' --values '[[...]]'
lark-cli drive +import --as user --type sheet --file '.\file.xlsx' --name 'TikTok SKU统一管理表'
```

When writing Chinese values or formulas from Python, pass JSON with `ensure_ascii=True` to avoid command-line encoding issues.

## Standard Workbook Shape

Maintain these sheets:

- `待处理派工`: first sheet; only pending work. Columns: `店铺`, `SKU`, `需要修改为`, `员工操作`, `完成状态`, `更新时间`, `备注`, `上架原价`, `日常售价`, `平台活动价`.
- `SKU状态总控`: one row per SKU. Columns: `SKU`, `当前变更状态`, `涉及店铺数`, `涉及店铺`, `处理说明`, `最近更新时间`.
- `员工执行清单`: one row per shop+SKU, normally all `正常`; useful for audit/reference.
- `店铺-<店铺名>`: one sheet per shop with all SKUs and price columns.
- `产品总表`, `SKU汇总`, `店铺统计`, `异常记录`: source/audit sheets.

## Official Campaign Upload Templates

Preserve official templates exactly: sheet names, headers, styles, number formats, validations, metadata, and OOXML package structure.

For Flash Deal uploads, a generic template is not valid for every store. In each store's Zhanfu Browser session, download a fresh template from the current Flash Deal page. The expected path is:

```text
<zhanfu_browser_root>/<店铺名>/Flash Deal.xlsx
```

- Match `<店铺名>` exactly to that store's export workbook filename.
- Never use another store's Flash Deal template, the generic bundled template, or a template from an older campaign without first downloading the current store template.
- Before generating a multi-store batch, require a template for every requested store. If any template is missing, stop before generating files and report all missing stores.
- Fill only `Product_id` and `Deal Price` cells in a copied workbook named `Flash Deal_已填写.xlsx` beside the original template. Do not overwrite the downloaded source template.

TikTok validates more than the visible header text. For official upload workbooks, preserve the original XLSX/OOXML package structure exactly:

- Never load and save an official upload template with `openpyxl`, LibreOffice, pandas, or another workbook rewriter. Those tools can remove `xl/sharedStrings.xml`, rewrite relationships, or change workbook metadata and cause TikTok to report `File header is incorrect` even when the visible headers match.
- Populate uploads by copying the untouched official template and directly patching only the required worksheet cells and shared-string entries inside the XLSX ZIP package.
- Keep every original ZIP entry, relationship, content type, custom metadata part, sheet name, validation, style, and header unchanged. Do not add or remove package entries.
- After generation, compare the output ZIP entry list with the official template. Only the intended worksheet XML and, when required, `xl/sharedStrings.xml` may differ.

- `product-discount.xlsx`: long-term fixed discount upload. Columns are `Product_id (wajib)`, `Diskon (wajib)`, optional promotional stock, and optional purchase limit. Write the discount as an Excel percentage value, for example `0.52` for 52% off.
- Flash Deal has no reusable generic live-upload template. Always use the freshly downloaded template for the exact store and current campaign. The offer price must be below the selling price and no higher than the lowest selling price in the prior 30 days.

Treat SKU as the warehouse and pricing key, but never upload SKU in place of `Product_id`. For every requested store:

1. Match the SKU in that store's export.
2. Read `产品id` from the matched row.
3. Never reuse a product ID from another store, even for the same SKU.
4. Include every store-specific product ID associated with the requested SKU.
5. Deduplicate upload rows by store plus product ID.
6. Generate separate upload files per store unless the platform workflow explicitly supports multiple stores in one upload.
7. A product ID can contain multiple SKU variants. If those variants require different prices but the official template accepts only one product-level price, do not guess. Put the product ID in a conflict report and require a single approved product-level price before generating the upload row.
8. Exclude and report every SKU marked cleared or delisted in the reference price workbook.
9. Exclude the entire product ID from batch Flash Deal uploads when any associated SKU matches the `Npcs` quantity pattern, such as `2pcs` or `3pcs`. The spreadsheet applies one product-level price to every variation, while bundle variants require variation-level pricing. List these rows in a separate `Npcs批量排除` audit sheet; they may only be configured manually by variation in the shop backend.

### Generate non-campaign Flash Deal upload files

Use `06_工作脚本/generate_flash_deal_uploads.py` after generating the non-campaign price workbook. Set:

- `PRICE_WORKBOOK`: version B workbook containing `全部店铺SKU`.
- `SHOP_DIRECTORY`: normally `<root>/01_店铺上架产品`.
- `ZHANFU_BROWSER_ROOT`: optional run-specific override for the Zhanfu Browser download root. Normally use `<root>/settings.json`.
- `OUTPUT_DIRECTORY`: optional override. Omit it to generate `Flash Deal_已填写.xlsx` beside each store's original template.
- `AUDIT_WORKBOOK`: path for the conflict/exclusion report.
- `CURRENT_DISCOUNT_RATE`: normally `0.50` because the current store display price sells at 50%.
- `TARGET_STORES`: optional comma-separated exact store names for generating only selected stores; omit it to process every store export.

The script first checks that the configured Zhanfu Browser root exists and every requested store has its own freshly downloaded template. It then preserves that exact store template, writes `Flash Deal_已填写.xlsx` in the same store folder, stores product IDs as text, and deduplicates by store plus product ID. It excludes product IDs containing Npcs bundle variants, cleared/delisted SKUs, missing prices, conflicting SKU prices, or an offer price that is not below the current discounted selling-price/L30 reference line. Always deliver the audit workbook with the upload files.

## Common Workflows

### Build from shop XLSX files

Use when the user provides a folder of shop files where each filename is the shop name.

1. Run `scripts/extract_skus.py` with:
   - `SHOPDIR`: folder containing shop `.xlsx` files
   - `OUT_JSON`: path for extracted data
2. Run `scripts/build_feishu_sku_workbook.py` with:
   - `DATA_JSON`: extracted data
   - `OUT_XLSX`: local workbook output
3. Import the workbook with `lark-cli drive +import`.
4. Run `scripts/upload_store_views.py` to add dispatch/store sheets.

### Sync prices and reset normal state

Use when the user provides a local price workbook.

Expected price columns: `商品 SKU`, `日常售价`, `平台活动价`, `上架原价`.

Run `scripts/sync_prices_and_reset_status.py` with:

- `SPREADSHEET_TOKEN`
- `DATA_JSON`
- `PRICE_XLSX`

This sets all SKUs to `正常`, clears `待处理派工`, and fills price columns in store/reference sheets.

### Verify prices against the supplied price workbook

Run `scripts/compare_feishu_prices.py` with:

- `SPREADSHEET_TOKEN`
- `DATA_JSON`
- `PRICE_XLSX`
- optionally `REPORT_JSON`

It compares the prices in `员工执行清单` and all `店铺-<店铺名>` sheets against the local price file, applying the exact-match and `Npcs` multiplier rules. Report blank expected prices separately from actual mismatches.

### Mark SKU as pending work

Use when the user says things like:

- `Repairing Paint 预购`
- `Repairing Paint 关预购`
- `ABC123 下架`
- `XYZ888 恢复正常`

Normalize terms:

- `预购`, `开预购` -> `开预购`
- `到货`, `关预购`, `关闭预购` -> `关预购`
- `下架` -> `下架`
- `恢复正常`, `正常` -> `正常`
- unclear -> `待确认`

Run `scripts/update_sku_status.py` with:

- `SPREADSHEET_TOKEN`
- `DATA_JSON`
- `TARGET_SKU`
- `TARGET_STATUS`
- `TARGET_NOTE`
- `TARGET_DATE`

Then run `scripts/rebuild_pending_dispatch.py` so the first sheet is rebuilt. It must show one row per affected shop+SKU and include the three price columns for actionable rows.

### Optimize Feishu layout

Run `scripts/optimize_feishu_sku_sheet.py` with:

- `SPREADSHEET_TOKEN`

This freezes headers/important columns, sets readable column widths, styles the main headers, and keeps `待处理派工` as the first sheet.

### Add self-service SKU change input

Use when the user wants to update the management sheet without asking Codex each time.

Run `scripts/setup_self_service_input.py` with:

- `SPREADSHEET_TOKEN`
- `DATA_JSON`

This creates:

- `ChangeInput`: visible input sheet. The user fills `SKU`, `修改为`, `备注`, `更新时间`.
- `DispatchData`: hidden formula helper sheet with ASCII title, because API-written formulas are more reliable with ASCII sheet references.
- `待处理派工`: formula-driven first sheet. It automatically shows shop+SKU rows when `ChangeInput!B:B` is `下架`, `开预购`, `关预购`, or `待确认`; it disappears when the status is `正常` or blank.

Self-service behavior:

- User enters `Repairing Paint` + `开预购` in `ChangeInput`.
- When stock arrives, the user enters the SKU + `关预购`; staff see `关闭预购` in the operation column.
- `待处理派工` automatically lists every shop containing that SKU and includes the three price columns.
- User changes the input status to `正常`, or clears the row, and `待处理派工` automatically clears those rows.
- The setup currently pre-fills 300 formula output rows on `待处理派工`. Extend `FORMULA_ROWS` if more simultaneous dispatch rows are needed.
- After this setup, routine status work requires no Codex or CLI action: the user edits `ChangeInput` directly in Feishu.

### Add new SKUs

When the user adds new shop SKUs, update:

- `产品总表`
- `SKU汇总`
- `SKU状态总控`
- `员工执行清单`
- the relevant `店铺-<店铺名>` sheet

Default new SKU status is `正常`. Rebuild `待处理派工`; if the new SKU is normal, it should not appear there.

## Current User Defaults

- Indonesia shop exports contain display/listing prices. Unless the user says otherwise, calculate the actual price as `display price * 50%`.
- For Indonesia price audits, compare the actual average unit price with the `猫店价格（普店+3000）` unit price. The current acceptable ceiling is `cat-shop unit price + 5000` per unit.
- The current pricing model treats the recommended final unit price as the big-campaign price at 40% of display price. Calculate display price from the full SKU bundle total as `campaign total / 0.40`, and calculate the regular flash-sale price as `display price * 0.48`.
- Treat the usual 5% creator/affiliate commission as a routine cost and the additional 5.5% campaign commission as a big-campaign cost. Use 5% for regular flash-sale net calculations and the combined 10.5% for big-campaign net calculations.
- Set the big-campaign price at 40% of display and the regular flash-sale price at 48% of the same display. This keeps the big-campaign price below the recent 30-day selling price.
- The user's recommended base unit price is the minimum net amount that must remain after the combined 10.5% big-campaign commissions. Calculate the customer-facing big-campaign unit price as `net floor / 0.895`, then derive display price at 40% and regular flash price at 48%.
- The `cat-shop price + 5000` value is a comparison warning, not a hard cap when applying it would reduce big-campaign net proceeds below the user's minimum floor. Flag overages instead of lowering the protected net price.
- Always flag SKUs whose 7.21 reference value contains `清仓` or `下架`. Do not generate a sellable target price for them; list them separately as unavailable for fulfillment.

The known personal Feishu sheet from this setup is:

```text
https://my.feishu.cn/sheets/KTCmscAsWhqUi7tci7ccNRQCnnd
```

Use this token only when the user wants to work on this exact sheet:

```text
KTCmscAsWhqUi7tci7ccNRQCnnd
```

Do not assume this token if the user provides a new Feishu link.

## Moving To A New Computer

1. Copy this skill folder into the new computer's Codex skills directory as `tiktok-sku-feishu-management`.
2. Start a new Codex session and say: `使用 tiktok-sku-feishu-management 管理我的 TikTok SKU 飞书表`.
3. For the existing online sheet, no shop XLSX files are needed for normal self-service changes; open the sheet and use `ChangeInput`.
4. When asking Codex on the new computer to change or audit the online sheet, authorize `lark-cli` with the Feishu account that owns this personal sheet.
5. For rebuilding from source files, adding bulk new shop SKUs, or re-syncing prices, provide the current shop XLSX folder and the current price workbook again.
6. Before generating campaign uploads, tell Codex the new computer's Zhanfu Browser download root. Codex must update `<root>/settings.json` and verify `<zhanfu_browser_root>/<店铺名>/Flash Deal.xlsx` paths before generation.
