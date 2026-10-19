# 知识库索引

机器可读来源清单：`source-manifest.json`。

其他 AI 的使用与校验：`runtime-and-colleague-testing.md`。

## 来源优先级

1. 用户在当前任务中明确确认的事实与最新文件。
2. `product/Y仓全部SKU产品资料与促销总表_20260808.xlsx` 中的精确 SKU 数据。
3. 本轮实时获取且带链接、观察时间的 TikTok/LinkFox/FastMoss/店铺证据。
4. `operations/Tiktok从入门到精通.docx` 及其检索版 Markdown。
5. `selection/` 中的选品规则快照与历史记忆。
6. `viral-library/` 中的历史爆款结构和文案经验。

相同层级冲突时，选择日期更近、粒度更精确、证据更直接的一项；保留冲突，不静默合并。

## 产品知识

- 原件：`product/Y仓全部SKU产品资料与促销总表_20260808.xlsx`
- 可检索索引：`product/product_catalog.jsonl`
- 索引统计：`product/product_catalog_summary.json`
- SKU 数：571 个精确且唯一的 SKU。
- 图片：`assets/product-thumbnails/` 共 571 张；原 Excel 也保留嵌入缩略图。
- 数据快照：2026-08-08。上架原价、日常售价、活动价、COD、上架状态会变化；三种价格口径不得互相替代。
- 已知问题：描述字段中的字符串 `37` 是占位；JSONL 已转为空值，原 Excel 保持不动。

先用精确 SKU 在 JSONL 搜索。需要查看原始证据、工作表结构或嵌入图时再打开 XLSX。

## TikTok 运营知识

- 原件：`operations/Tiktok从入门到精通.docx`
- 全文检索版：`operations/tiktok-operations-extracted.md`
- 检索导航：`operations/operations-retrieval-guide.md`
- 提取校验：`operations/operations_extraction_summary.json`

此文档适合学习兴趣电商、流量/转化指标、内容、达人、广告和运营 SOP。其中播放量、完播、CTR、CVR、ROI 等数字是教程口径或经验阈值；用于当前判断前必须与账号、地区、类目和平台现状交叉验证。

## 选品逻辑

- 主规则：`selection/selection-logic.md`
- 规则已从历史 xuanpin 资料中提炼为便携快照；未携带含旧电脑绝对路径、旧店铺/账号状态的原始备份，避免被其他 AI 误当现状。

正式链路：平台数据 + 自有历史/库存/利润 + 规则评分 + 记忆复盘。支持市场、混合、自有 SKU 三种模式。

## 爆款文库

- `viral-library/01_tiktok_foundation_rules.md`
- `viral-library/02_indonesia_copy_generation_playbook.md`
- `viral-library/03_viral_copy_patterns_from_batch_20260610.md`
- `viral-library/viral_reference_database.md`

这些文件保存可复用的 Hook、结构、印尼口语、类目模式与风险。它们不是可直接复制的原文库，也不替代当前对标检索。

## 动态规则

政策和平台功能会变化。使用 `policy-and-rights.md` 作为门禁，并在每个新批次记录官方核对日期；距上次核对超过 7 天、用户要求“最新”，或平台出现新提示时重新核对官方页面。
