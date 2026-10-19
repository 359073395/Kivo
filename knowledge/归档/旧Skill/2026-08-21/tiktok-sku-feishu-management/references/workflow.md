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
