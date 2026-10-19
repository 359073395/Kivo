# 产品资料、交付检查与反馈补充工具

状态：`active_process_only`；用户授权给现有库补工具和模板，见[直接来源及边界](../../../资源/来源索引/2026-10-19_电商工具箱增量补充授权.md)。工具验证是本地一致性检查，不是产品真实、平台审核或转化提升证明。继承 COM-004/013/014/015/016；不新增主 Skill，不替换原工具或批准流程。

## 何时用

- 同一 SKU 准备标题、详情、图中文字或视频稿：从已有资料形成共享 `product-brief.json`，避免每个产物重新解释事实。
- 完整 Listing 交付：原 `validate_listing_delivery.py` 继续使用；本工具追加实测字符、字段/数值/单位和跨文本检查。只问比较时按需检查，不强制新建完整批次。
- 有授权导出的真实评价：分类后用 `reviews` 计数，形成可追溯修改候选。没有评价不要求补零或虚构。
- 修改旧链接/素材并复盘：用 `iterate` 保留版本、假设和同口径窗口。首测没有历史数据仍可准备和上架，不把复测记录变前置。

本周2026-10-19—24继续[先上链接测流量/成交](../../../资源/来源索引/2026-10-19_本周先上链接测流量与成交.md)；这些检查不恢复市场前置、不增加首测套数、不更改5SKU/十店50条计划。期限外按当期项目规则。

## 文件与命令

脚本：[commerce_quality.py](../scripts/commerce_quality.py)。四份可复制模板：[产品资料](../assets/commerce-quality/product-brief.json)、[评价批次](../assets/commerce-quality/review-batch.json)、[评价CSV](../assets/commerce-quality/reviews.csv)、[改版复测](../assets/commerce-quality/iteration-record.json)。

从 `machine-paths.local.json` 解析 productionWorkRoot，产物放库外原任务目录。以下 `脚本路径` 和 `任务目录` 由执行代理解析，用户不用手工填写技术表。

```text
python commerce_quality.py init <库外任务目录>
python commerce_quality.py check <product-brief.json> --listing-review <原有文案检查JSON> --out <新报告.json>
python commerce_quality.py reviews <review-batch.json> --csv <reviews.csv> --brief <product-brief.json> --out <新报告.json>
python commerce_quality.py iterate <iteration-record.json> --out <新报告.json>
```

只检查图片文字或视频稿时可省 `--listing-review`；有标题/详情且省略时报告会提醒原有检查仍需完成。初始化和报告拒绝覆盖已有文件；新版本使用原任务的版本目录。`passed=true`只表示当前检查项没有错误；仍须读取 warnings、state 和人工复核项。工具不联网、不发布、不改价、不删除链接。

## 共享产品资料：自动整理已有事实

- `identity.sku`：精确SKU；`listing_targets`按店铺保存PID，未上架用 `state=draft`、PID为空，不能因此挡资料准备；已发布才要求PID。
- `sources`：每项 `id / kind / ref / as_of`；kind 可为 product_document、product_image、measurement、user_confirmation。外部对标可保留但不能支撑本品事实。as_of用YYYY-MM-DD，ref指向实际来源，不伪造。
- `facts`：每项 `id / field / value / unit / status / source_ids`。只有 confirmed、user_confirmed且有本品来源可支撑文案；unknown、conflict保留但不能被引用为已证实事实。数字value采用无千分位、点小数的规范字符串。
- `core_selling_point`是一句有本品依据的主购买理由及 fact_ids；副卖点数量不固定，不为填满模板编造。
- `forbidden_words.reviewed=true, items=[]`表示已审查且没有本次禁词，可以通过；false才是未审查。已知风险用known_risks的hold保留。
- `real_assets`记录真实原图/素材位置、用途、来源及必要哈希供原视觉流程核查；脚本不把路径存在当作产品一致性证明。
- `deliverables`只填本次实际产物；图中文字/视频稿可供检查，但最终图片OCR、配音/成片仍走现有视觉与媒体验收，不认为稿件通过等于成片通过。
- `required_keywords`每项 `text / surface / fact_ids`，继承逐词比较与核心需求保留；不称语义覆盖为已验证热搜。
- `title_constraint`默认null：只报告实测字符数。确有当前平台依据才填max_characters、source_ref、checked_at；没有默认255、120或巴西站规则。

事实示例（仅说明格式，不是当前用户产品事实）：

```json
{"id":"weight","field":"net_weight","value":"15","unit":"g","status":"confirmed","source_ids":["packaging"]}
```

## 数字及语义检查

第一次运行check会列出数字在各文本中的start/end（Python字符偏移，end不含末位）、实际数值和单位。执行代理据此生成numeric_bindings：`surface / start / end / fact_id / field / context_reviewed`，复跑验证。文案变化后重新绑定，旧位置会被拦截。

- 单位维度及换算一致才通过，例如0,015 kg与15g等值；15kg不能引用15g，15岁不能引用15g。`number_locale=id-ID`按印尼小数逗号、千分位点读取；canonical使用点小数。不能猜测两者。
- 相同数字不证明字段相同。field必须等于事实field，且执行代理逐句确认context_reviewed；数字扫描仍无法自动理解全部语义，不能伪填true。
- 不支持的数字格式、型号中数字、未知单位或单位缺省会要求复核。不得为了让检查通过编造数字事实；保留原正确表述并记录局部限制，必要时在既有语义审查中人工处理，不能宣称自动通过。
- `claim_checks`用于非数字声明：surface、quote、fact_ids、context_reviewed。必须逐项人工/代理审查成稿中的功效、年龄、安全、认证等声明；空清单不是自动证明“没有此类承诺”。
- 新工具不能替代原有核心需求、原词取舍、年龄状态、中文含义及印尼语双复制框检查。传入原检查JSON时还核对SKU和文案是否相同，避免拿旧报告给新稿背书。

## 评价转修改候选

batch identity包含store/product_id/sku；origin为own_product或competitor。同批混入其他身份、重复review_id会报错。评分缺失、非整数或超范围保持unrated；无有效评分时bad_rate为null，有评分但零差评则为0，绝不除零。

每条保留review_id、rating、text、source_ref；category由语义审查给出：

| 分类 | 路由 |
|---|---|
| misunderstanding | 核对本品事实后改清晰度 |
| usage_difficulty | 核对说明与实际用法 |
| missing_accessories | 查包装/漏配与履约，不自动靠文案解决 |
| quality / logistics | 质量/物流调查 |
| expectation_gap / other | 人工核因 |

CSV的fact_ids用分号分隔。只有本品评价、当前SKU事实引用有效，且为误解/使用困难，才标记可准备文案候选；不自动修改发布，不把“可准备”当问题已解决。对标评价只产生待验证假设。归因未知单列，所有比例明确分母；不设固定可修复率、情绪权重或自动放量条件。

## 局部改版与复测

`changes`记录surface、before_ref、after_ref、reason；另有hypothesis。无observations时state=planned_not_measured，不妨碍正常准备。

有数据时observations包含before/after，两者均有与记录完全相同的identity、start/end（YYYY-MM-DD，含首尾）、source_ref、scope、ready_for_comparison、readiness_basis及metrics。scope写实际渠道与归因口径，例如商品卡自然报表，不混商品卡广告报表。是否成熟由当次数据说明，不默认3/7/30天。

```json
{"ctr":{"kind":"rate","definition":"本口径点击/曝光","numerator":12,"denominator":1000},"orders":{"kind":"count","definition":"本口径支付订单数","value":null}}
```

率按提供的明确分子分母计算，空白/零分母保持unknown；数量对比要求窗口天数相同，指标定义与身份、渠道口径一致。只有后台百分比但无分子分母时不倒算，保留原值供人工看。不同窗口结果只描述变化，不证明因果；多项修改另提示无法归因单一项。没有数据不宣布成功，不自动调价、加预算、删零单链接；实际店铺更新后的飞书同步仍沿COM-016。

## 验证与来源

运行 `python -B -m unittest discover -s <本Skill/tests> -p test_commerce_quality.py`，并在修改连接方式时运行原 `test_listing_delivery.py`。合成数据产物留productionWorkRoot；仅检查工具行为，不证明商业效果。

设计参考：[外部项目固定版本](https://github.com/heqiangdiao-wq/AI-Cross-Border-Ecommerce-Agent-Toolkit/tree/cec98a9cab382d28dfe5b4ed0de444f33c455cb5)。本地脚本独立编写；没有复制其平台阈值、费用预设和实现。其原PDF未做完整蒸馏，范围见来源卡。新增流程经用户授权，真实SKU耗时/误报/营销效果仍待反馈。
