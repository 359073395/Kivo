# LinkFox 便携运行规则

## 新电脑所需

1. 安装或恢复 LinkFox Agent 集成，或保留本 Skill 的 `scripts/linkfox.py`。
2. 在操作系统环境变量配置 `LINKFOXAGENT_API_KEY`，不要写进知识库。
3. 配置 `LINKFOX_OUTPUT_ROOT` 指向单独本地工作目录。
4. 用一个无敏感信息的小查询验证提交、进度、结果和本地文件路径。

## 任务状态

- 提交成功后立即保存 message ID、原任务和提交时间。
- `working` 只轮询；不得重复提交。
- `finished` 保存 ShareURL 和结果文件路径。
- `error/cancel/stop` 保存原因并明确是否允许修正参数后重试。
- 状态不明时标为 `unconfirmed`，先恢复 message ID 再决定。

## 主 Skill 与 LinkFox 的分工

主 Skill 提供：业务问题、产品身份、市场范围、决策门禁、最终判断。

LinkFox 提供：带时间和筛选条件的外部数据、工具结果、原始文件与可追溯链接。

LinkFox 结果不得自动升级为已批准的 SKU、功效宣称、价格、投放、建联或发布动作。

