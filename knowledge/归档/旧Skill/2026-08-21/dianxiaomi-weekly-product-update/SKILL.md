---
name: dianxiaomi-weekly-product-update
description: Update the user's weekly Dianxiaomi TikTok Shop online-product library in the existing D:\Downloads\zhanfubrowser_down\zhanfubrowser store folders. Use when asked to refresh, synchronize, export, replace, audit, or report changes for these Dianxiaomi shop product workbooks, especially the weekly recurring update. Preserve existing folders and Flash Deal.xlsx files, force 300 products per page, verify full selection, and report per-store changes.
---

# 店小秘每周在线产品库更新

## 固定范围

- 只处理 `D:\Downloads\zhanfubrowser_down\zhanfubrowser` 下已经存在且列在 `references/store-map.json` 中的店铺文件夹。
- 不创建、删除、移动或重命名店铺文件夹。
- 只覆盖映射中指定的产品表；绝不修改 `Flash Deal.xlsx`。
- 使用已登录的店小秘会话访问 `https://www.dianxiaomi.com/web/tiktokProduct/online`。
- 使用浏览器控制技能完成网页操作，使用表格技能或本技能脚本复核 `.xlsx`。

## 每次运行流程

### 1. 盘点并留存基线

1. 读取 `references/store-map.json`。
2. 运行：

   ```powershell
   python scripts/inventory.py --root "D:\Downloads\zhanfubrowser_down\zhanfubrowser" --mapping references/store-map.json --output <临时目录>\before.json
   ```

3. 若映射中的文件夹或产品表缺失、出现映射外文件夹，立即停止并报告；不要自行补建。
4. 保存每份产品表的数据行数和每份 `Flash Deal.xlsx` 的 SHA-256。

### 2. 逐店同步

按映射顺序逐店执行，严格串行：

1. 点击映射中的 `dianxiaomi_label`，等待 3 秒。
2. 验证页面确实切入该店：
   - 页面记录数是单店数量，不是“全部店铺”的数万条；
   - 产品行中出现 `「店小秘店铺名」`。
   若首次点击未生效，再点击一次并等待；仍未生效则停止该店，不能误导出全部店铺。
3. 把每页条数设为 `300条/页`，读取输入框值确认。不要依赖上次选择。
4. 点击 `同步产品` → `同步全部产品`，等待弹窗明确显示 `状态：已完成!`，记录“共同步成功 N 条数据”。
5. 关闭同步弹窗。为清除店小秘可能保留的旧勾选状态，打开新的店小秘在线产品标签页，重新选择该店。

### 3. 全量选择与导出

1. 在新标签页重新选中当前店并验证店铺身份。
2. 再次强制选择 `300条/页`，确认上下两个分页框均显示 `300条/页`。
3. 读取 `共 N 条记录` 作为在线产品数。N 不超过 300 时，当前页面应展示全部 N 条。
4. 点击表头复选框。如果页面已有历史勾选，先取消再重新全选。
5. 必须验证黄色提示为 `已选中N条数据`，与在线产品数完全一致。若不一致，刷新、新建标签页、重新选店、重新设 300 条/页后再全选；未通过校验禁止导出。
6. 点击 `导入/导出` → `按勾选导出`，等待“导出文件已经生成”。记录 `已导出：M条数据`；M 是 SKU/规格明细数，可能大于 N。
7. 读取“立即下载文件”的 HTTPS 链接，不依赖浏览器下载事件。

### 4. 原位覆盖与验证

使用映射中的原产品表路径，运行：

```powershell
python scripts/install_export.py --url <下载链接> --target <原产品表绝对路径> --root "D:\Downloads\zhanfubrowser_down\zhanfubrowser"
```

脚本只允许覆盖已存在、位于固定根目录内、且文件名不是 `Flash Deal.xlsx` 的有效 `.xlsx`。

全部店铺完成后再次运行 `inventory.py` 生成 `after.json`，并检查：

- 18 个现有文件夹仍然存在，且没有新增文件夹；
- 18 份产品表都能作为有效 XLSX 读取；
- 每份新产品表的数据行数等于该店导出弹窗的 M；
- 所有 `Flash Deal.xlsx` 的 SHA-256 与基线一致。

### 5. 交接 Flash Deal 填写

只有在 18 家产品表全部更新成功、上述复核全部通过后，使用任务消息工具通知任务 `019fcbe8-23f7-78d2-ad62-e235750eb263` 开始填写 `Flash Deal.xlsx`。

发送的消息必须包含：

- 明确说明本周 18 家在线产品库已经全部更新并复核通过；
- 产品库根目录 `D:\Downloads\zhanfubrowser_down\zhanfubrowser`；
- 要求该任务按照它自己的 `tiktok-sku-feishu-management` 技能和既有价格规则，填写 18 个现有店铺文件夹中的 `Flash Deal.xlsx`；
- 本周每家在线产品数、产品表新明细数和净变化汇总，便于它核对输入；
- 要求其完成后在自己的任务中报告填写条数、排除项和验证结果。

不要把 `Flash Deal.xlsx` 的填写工作放在本技能当前任务里执行。通知目标任务后，本技能才算完成本周交接。

若任一家产品表更新或最终复核失败，也要通知同一目标任务，但消息必须明确写明“本周产品库未完整更新，暂不要填写 Flash Deal.xlsx”，并附失败店铺与原因。不能让下游任务使用部分更新的数据。

## 汇报格式

按店铺列出：

- 在线产品数 N；
- 店小秘同步成功数；
- 旧明细数 → 新明细数；
- 净变化（新明细数减旧明细数）。

注明明细数按 SKU/规格行计算，不含表头；负数表示平台当前有效明细减少，不代表漏下载。最后汇总旧明细总数、新明细总数和净变化，并明确说明没有创建店铺文件夹、没有修改 `Flash Deal.xlsx`。

在本任务的最终汇报中同时说明：是否已成功通知任务 `019fcbe8-23f7-78d2-ad62-e235750eb263`，以及发送的是“开始填写”还是“暂缓填写”指令。

## 失败保护

- 登录失效时显示浏览器并请求用户登录，不能切换到搜索或其他来源。
- CAPTCHA 必须按浏览器控制技能要求请用户确认后再处理。
- 任一店铺未通过“店铺身份、300条/页、全选数一致、导出行数、有效XLSX”五项校验时，不覆盖该店旧表；记录失败原因并继续或安全停止。
- 网页显示的同步成功数不等同于产品表净变化；汇报两者时分开标注。
