# TikTok SKU Feishu Workflow Reference

## Status Meanings

- `正常`: listed product is fine; do not show in pending dispatch.
- `下架`: staff must remove/offline the SKU in every listed shop.
- `开预购`: staff must set the SKU to preorder in every listed shop.
- `关预购`: stock has arrived; staff must disable preorder for the SKU in every listed shop.
- `待确认`: staff/owner must check the SKU before action.

## Dispatch Principles

- `待处理派工` is a task board, not a product database.
- Keep it short and visually obvious.
- For the current personal management sheet, routine status changes are entered in `ChangeInput` and `待处理派工` updates by formula.
- Use scripts to rebuild or repair sheets only when maintaining structure or importing new source data.
- Include prices only for pending rows.
- Leave completed tracking to the `完成状态` column.

## Price Rules

For TikTok Flash Deal and sale pricing, the current source of truth is the validated unified workbook `SKU统一定价表_价格1与价格2取低.xlsx`:

1. Default to not participating in a major campaign. Only switch when the user explicitly says the current activity participates.
2. Price 1 = cat-shop reference price from `7.21 印尼所有产品及定价.xlsx` + `min(ceil(reference price × 5%), 3000)`.
3. Price 2 = platform activity price from `Y仓 TK SHOP SKU 售价_活动价.xlsx`.
4. Final price = the lower of Price 1 and Price 2.
5. Match exact SKU first. For `Npcs<base>`, match the complete bundle SKU first; only when absent use base price × N.
6. Only user-confirmed aliases may bypass exact text equality. Missing, nonnumeric, conflicting, or product-level multi-SKU different prices block the affected Product ID.
7. The same SKU may map to several store-specific Product IDs, but a Product ID may not be reused across stores.
8. Exact user-confirmed overrides are stored in `confirmed-price-overrides.json`. Current override: `626-Expce Herbal Tea` uses Price 2 = 59,520 IDR when Price 1 is blank. Do not generalize this exception.

Columns in the user's price sheet:

| Source column | Management column |
|---|---|
| 商品 SKU | SKU |
| 上架原价 | 上架原价 |
| 日常售价 | 日常售价 |
| 平台活动价 | 平台活动价 |

Matching order:

1. Exact SKU match.
2. If no exact match and SKU matches `Npcs<base>`, use `<base>` price multiplied by `N`.
3. If still missing, leave price blank.

Examples:

- `Repairing Paint` uses `Repairing Paint` prices.
- `3pcsRepairing Paint` uses `Repairing Paint` prices multiplied by 3.
- Missing SKU means either not listed in the price sheet or not sold; leave blank unless the user says otherwise.

## Current Self-Service Layout

- `ChangeInput`: visible user input. Enter `SKU`, `修改为`, `备注`, `更新时间`.
- `待处理派工`: first sheet and automatic staff-facing output.
- `DispatchData`: hidden formula helper table; preserve its ASCII sheet name for API-written formula compatibility.

When the user enters `正常` or clears a command row, matching rows disappear from `待处理派工`.
