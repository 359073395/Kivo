---
name: seedance-video-producer
description: 使用用户已登录的 Google Chrome 操作 TikTok Symphony Image-to-Video，读取 Excel 或本地任务目录，按执行表严格串行生成 Dreamina Seedance 2.0 的 15 秒竖屏视频，下载到用户指定目录，校验、记录额度并支持中断续跑。Use when the user asks to inspect, test, batch-generate, download, validate, resume, or locate Seedance videos from product and nine-grid images.
---

# Seedance Video Producer

## 核心约束

- Skill 目录只保存流程、轻量 reference 和小脚本。
- 禁止把真实产品图、九宫格图、Excel、视频、manifest、日志、下载缓存或聊天记录写入 Skill 目录。
- 所有任务文件和运行状态只写到用户本次指定的任务目录。
- 使用用户已经登录账号的 Google Chrome，固定访问：
  `https://ads.tiktok.com/creative/creativestudio/image-to-video`
- 使用 Chrome 控制能力，不切换其他浏览器，不读取或保存密码、Cookie、验证码或登录凭证。
- 固定模型 `Dreamina Seedance 2.0`，固定时长 `15s`。
- 严格串行，任何时候只允许一条视频处于提交或生成状态。
- 默认只测试表格第一条；成功下载并校验后必须等待用户明确说“开始批量”。
- 不依赖聊天历史；恢复时以 `ACTIVE_TASK.json`、额度日志、Chrome 页面和本地文件为准。

## 开始前必须读取

- 浏览器提交、等待、下载和错误协议：[references/seedance-protocol.md](references/seedance-protocol.md)
- 输入表、状态机与日志结构：[references/schemas.md](references/schemas.md)
- 视频校验与产品质检：[references/validation.md](references/validation.md)

如果本机存在以下规则，同时读取：

- `D:\codex项目\knowledge_base\06_tools_and_workflows\tiktok_latest_rules_and_last_task_handoff_20260722.md`
- `D:\codex项目\knowledge_base\04_short_video_content\tiktok_official_ai_generation_and_commercial_safety_rules_20260723.md`

## 定位任务与保存位置

用户可以提供 Excel、本地任务目录或明确输出目录。优先级：

1. 用户本次指定的任务目录/输出位置。
2. `%USERPROFILE%\.codex\tiktok-video-workflow\config.json`。
3. `D:\TikTok视频生产\`。
4. 没有 D 盘时使用 `%USERPROFILE%\TikTok视频生产\`。

执行前明确告诉用户本次读取位置和视频保存位置。不得把文件复制到 Skill。

可调用：

```powershell
py -3 scripts/workspace_state.py resolve --output-root "<本次目录>"
py -3 scripts/workspace_state.py locate --skill seedance-video-producer --output-root "<本次目录>"
py -3 scripts/workspace_state.py check "<任务目录>"
py -3 scripts/workspace_state.py configure "<以后默认使用的目录>"
```

只有一个未完成任务时可以自动继续；多个匹配任务时必须列出路径并让用户选择。

## 全表预检

打开 Chrome 或提交任何任务前，检查整张表和全部素材。每条必须有：

- SKU。
- 产品白底图或透明图。
- 同一任务的九宫格图。
- 完整 Seedance 提示词。
- 目标输出路径（可来自表格、manifest 或任务配置）。

同时确认：

- 文件存在、可读取且 SKU 对应正确。
- `generation_policy_result=passed`。
- 产品图、商标、包装、人物和其他素材的权利/同意已确认。
- 不含密码、密钥、支付信息或不必要的敏感资料。

任何缺失都先列出，不打开生成流程、不盲目执行。

产品图不是白底/透明图时，先使用图像编辑能力制作干净版本并检查；形状、颜色、比例、包装、标签和 Logo 必须严格跟随原图。无法保持时暂停并要求用户补图。

## 提交规则

每条任务固定：

1. 第一张上传产品白底图或透明图。
2. 第二张上传同一任务九宫格图。
3. 完整粘贴该条提示词，不得截断。
4. 选择 `Dreamina Seedance 2.0`。
5. 选择 `15s`。
6. 页面有真正的视频语言选项时选择 Indonesian；不要把界面语言误认为视频语言。
7. 再次确认当前没有其他视频生成。
8. 全部正确后只点击一次生成。

提示词必须包含 TikTok Shop Indonesia、9:16、15 秒、印尼语口播、产品外观锁定、九宫格镜头顺序以及少字幕或无字幕。禁止中文、SKU、文件名、无关长文字或虚构水印；平台自动添加的水印/AIGC 标记必须保留。

## 第一条测试门禁

第一条成功、下载和校验后：

- 更新结果表和 manifest。
- 将批次状态设为 `awaiting_batch_approval`。
- 汇报测试视频路径与校验结果。
- 停止并等待用户明确说“开始批量”。

没有这句确认，不得处理第二条。

## 恢复与防重复

- 点击生成前写入提交意图、SKU、任务序号和时间。
- 页面恢复时先检查请求记录、额度、Chrome Downloads、目标文件和 manifest。
- 页面恢复后已出现新的额度限制或请求记录时，视为本周期已经尝试，不得再次点击。
- 显示生成中或 `Almost there` 时保留页面等待；未明确成功/失败前不得重复提交或进入下一条。
- 浏览器状态不明确时标记 `unconfirmed_after_browser_timeout`，不重新认领标签页、不点击生成、不处理下一条。

## 下载与完成

- 必须使用网站成品卡片自身的下载按钮。
- 禁止使用 CDN 地址或 curl 直接下载。
- 从 Chrome 默认 Downloads 识别新文件，移动并重命名到当前任务目标目录。
- 文件名必须包含 SKU 和任务序号。
- 用 FFprobe/FFmpeg 校验后才标记 `completed=true` 并处理下一条。

## 完成汇报

全部完成或按规则跳过后停止自动任务，并汇报成功数、跳过数、跳过原因、输出目录、未确认任务和观察到的每日额度情况。
