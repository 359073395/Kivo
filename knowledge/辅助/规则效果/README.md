# 规则效果信号

本目录只保存可移植的 schema、跨任务聚合结果和规则审查候选，不保存隐藏思维，也不保存每次任务的原始运行流水。

## 存储边界

- 原始信号：机器本地 `<productionWorkRoot>/rule-effects/pending/`，每条一个 JSON，避免并发追加损坏；不进入 `PORTABLE-MANIFEST.json`。
- 聚合结果：`规则效果聚合.json`，进入便携 manifest。
- 审查候选：`规则审查候选.md`，只提示需要合并/修改/替代/停用审查；不自动改变活动规则。

## 可观察效果

- `changed`：改变了动作、预测、排序或停止条件；
- `confirmed`：有事实支撑地确认原动作；
- `rejected`：否决候选动作或预测；
- `prevented_error`：阻止越权、错误批量或其他错误；
- `no_material_effect`：未改变、确认、否决或阻止任何东西。

`prevented_error` 是有效硬门禁，不得归为空转。只有同一规则在不同任务中形成持续的 `no_material_effect` 模式、且没有任何其他效果时，才进入审查候选；最终变更仍走规则权威协议和用户确认。

## 工具

- 发出信号：`辅助/维护/Write-RuleEffectSignal.ps1`
- 本地聚合/校验：`辅助/维护/Update-RuleEffectSummary.ps1`
- 每日审计先聚合，再决定是否把跨任务模式写入主日志。没有新信号时不改聚合文件，不制造版本噪音。
