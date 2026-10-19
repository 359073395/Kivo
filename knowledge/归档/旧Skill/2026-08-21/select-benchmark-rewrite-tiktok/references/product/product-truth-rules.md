# 产品事实与促销使用规则

## 检索方法

1. 只按 `sku` 精确匹配 `product_catalog.jsonl`。
2. 匹配不到时尝试大小写/首尾空格标准化，但结果必须显示原始 SKU 并要求人工确认。
3. 不按相似标题、功效或图片自动合并 SKU。
4. 组合 SKU 必须保留 `base_sku` 与 `quantity`，不能把单件与组合装价格/规格混用。

## 事实卡字段

至少读取：

- `sku`, `base_sku`, `quantity`
- `product_name`, `reference_name_cn`
- `specification`, `ingredients`, `selling_points`, `usage`, `audience`
- `attributes_certifications`, `warehouse_note`
- `listing_original_price_idr`, `daily_price_idr`, `activity_price_idr`, `discount_rate`, `discount_amount_idr`
- `cod`, `dianxiaomi_lookup_status`, `online_shop_count`, `listed_in_18_shops`
- `missing_fields`, `conflict_status`, `profile_completeness`
- `best_source`, `dianxiaomi_latest_updated`, `source_row`
- `image_thumbnail`, `latest_image_url`

## 真值边界

- 读取 `fact_layers`：`snapshot_confirmed` 只说明工作簿快照中已确认；`listing_evidence_needs_verification` 是店铺刊登证据，不等于安全宣传事实；`blocked_or_unverified_claims` 命中高风险词库，默认不得进入对外文案。
- `claim_risk_tags` 只负责拦截和提醒，不能自动证明某项宣传为假或为真；应回到包装、认证原件、当前店铺和可靠资料确认。
- `listing_original_price_idr`、`daily_price_idr` 与 `activity_price_idr` 是 2026-08-08 总表快照，不保证当前仍有效。
- `listing_original_price_idr` 是定价源中独立的“上架原价”口径；该版源表公式为“日常售价 × 2”。禁止拿 `daily_price_idr` 代替上架原价，也禁止把上架原价当日常成交价。
- 店小秘在线刊登价不是 Flash Deal 成交价。
- `cod` 只有明确导出值时才可使用；当前任务中仍需重新验证。
- `listed_in_18_shops` 只说明快照中的 18 店覆盖，不证明指定店铺此刻有可购买链接。
- `product_name`、`specification`、`ingredients`、`selling_points`、`usage`、`audience` 与认证字段均来自刊登资料/证据汇总，可能污染、串入其他描述或包含高风险宣传。未经包装/可靠资料复核，不称为“已确认事实”。
- 认证、BPOM、成分、SPF、容量等只有在同一 SKU 的包装/可靠来源一致时才可写。
- `37`、空字符串、明显乱码或与 `missing_fields` 冲突的内容视为缺失。

## 冲突处理

如果 `conflict_status` 非空：

1. 列出冲突字段。
2. 使用无冲突的共同事实继续。
3. 禁止使用有冲突的价格、规格、成分、功效或促销。
4. 状态写为 `needs_fact_confirmation`，并给出最小补充清单。

## 图片

- `image_thumbnail` 是本包内的相对路径，用于识别产品和快速测试。
- `original_image_filename` 只记录原图文件名，不含创建者电脑的绝对路径；全分辨率原图未放入本包。
- 需要抠白底或商品图编辑时，应让用户另行提供原图或把原图库作为独立附件，不从缩略图猜包装文字。

## 关键回归：Qinfeiyan Shampoo

- 快照确认：上架原价 96,760 IDR、日常价 48,380 IDR、活动价 45,380 IDR、优惠 3,000 IDR、COD 导出值明确、图片映射存在。
- 缺失：成分、使用方法。
- 冲突：标题与在线刊登价多值。
- 待确认/默认禁用：规格字段中夹带的功效描述、BPOM 号码、“永久黑发”“修复毛囊”“防脱/生发”等刊登话术。没有包装或可靠文件确认时不得作为真实卖点输出。
