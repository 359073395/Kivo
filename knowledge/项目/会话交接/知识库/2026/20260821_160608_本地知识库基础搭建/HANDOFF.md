# 本地知识库基础搭建

## 目的与范围

把个人工作知识库固定在 `D:\Knowledge`，使 Skill、规则、知识、项目摘要、manifest 和最终复盘可以整体备份、迁移并在新的 Codex 对话继续使用。大型视频生产文件继续保存在单独的本地工作目录，不进入知识库。

## 当前进度

已完成可移植知识库基础层、五个业务工作系统重构、新电脑总手册和真正的知识蒸馏层。当前 `D:\Knowledge\skill` 共有七个活动 Skill；新增 `knowledge-distillation` 专门负责完整文字化和蒸馏，`knowledge-iteration` 负责维护、交接与迁移。飞书知识库已完成相关页面的部分读取，抖音视频仍阻断。下一步确认外部生产工作根目录、继续全量摄入飞书/抖音来源、重启 Codex 并做新对话冒烟测试。

## 已确认决定与最新规则

- `D:\Knowledge` 保存 Skill、规则、最终文字稿、知识、项目摘要、manifest 和最终复盘。
- 原视频、原音频、原 PDF/大型文档、抽帧、临时转录/OCR 缓存、B-roll、HeyGen 底片、ChatCut 工程和成片放在单独本地工作目录。
- 视频、音频、PDF、文档和网页必须先形成完整 Markdown 文字稿并写回知识库，再进入蒸馏。
- “做数字人口播”默认纯 HeyGen 模式。
- “做带 B-roll 的完整带货视频”默认使用 GPT 人物图＋用户最终语音＋HeyGen 底片＋混剪素材＋ChatCut。
- 用户最终语音是锁定主时间轴，不得在 ChatCut 中擅自剪切或重排。
- Seedance 当前不可用，归档而不删除。
- 原百度同步盘 `session-backup` 不再作为活动 Skill，改成本地 `knowledge-iteration` 会话交接。

## 关键文件与路径

- `D:\Knowledge\AGENTS.md`：任意 AI 的总入口规则。
- `D:\Knowledge\knowledge-base.json`：知识库身份标记与入口清单。
- `D:\Knowledge\PORTABLE-MANIFEST.json`：便携文件 SHA-256 清单。
- `D:\Knowledge\RESTORE-KNOWLEDGE.ps1`：新电脑恢复与 Skill 注册。
- `D:\Knowledge\skill\knowledge-distillation`：资料文字化、知识/书籍/访谈和个人技能蒸馏 Skill。
- `D:\Knowledge\skill\knowledge-iteration`：摄入登记、维护、复盘、会话交接和迁移 Skill。
- `D:\Knowledge\START-HERE.md`：新电脑恢复和整体使用手册。
- `D:\Knowledge\资产\方法论\知识蒸馏总规则.md`：全局蒸馏权威规则。
- `D:\Knowledge\资产\方法论\本次对话知识蒸馏_2026-08-21.md`：本次对话决策账本。
- `D:\Knowledge\辅助\配置\machine-paths.local.json`：当前电脑专属路径，不纳入便携清单。

大型素材工作根目录尚未确认，必须在 `machine-paths.local.json` 中填写后才能恢复相关生产任务。

## 使用的 Skill、工具与外部依赖

- 使用 `skill-creator` 规范创建 `knowledge-iteration` 和 `knowledge-distillation`。
- 使用 PowerShell 完成哈希清单、验证、恢复和 Junction 注册。
- 外部生产能力仍依赖 HeyGen、ChatCut、LinkFox、飞书、店小秘、FFmpeg 等各自的软件、插件或授权。

## 已完成验证

- PowerShell 四个脚本语法通过。
- JSON 文件解析通过。
- 便携清单跟踪 16 个基础文件时，缺失、哈希错误和未跟踪文件均为零；后续修改后应重新生成。
- 恢复脚本成功把 `knowledge-iteration` 注册到 `C:\Users\lhwha\.codex\skills`。
- 当前环境检测到 FFmpeg、FFprobe、lark-cli；未检测到 Docker。
- 会话交接生成脚本成功生成本目录。
- `knowledge-iteration` 更新后通过 Skill 校验；123 个 Markdown 本地链接无缺失。
- 资产目录已有 5 个蒸馏/复盘文件，来源索引已有 1 张本对话来源卡。
- 便携清单更新到 2447 个文件，缺失、哈希错误和未跟踪文件均为零。

## 未完成事项与下一步

1. 用户确认单独本地视频工作根目录后填写 `productionWorkRoot`。
2. 重启 Codex，在新对话分别测试七个主 Skill 的触发，确认“蒸馏”不会误路由到普通维护。
3. 重新登录/授权需要的 HeyGen、ChatCut、LinkFox、飞书、店小秘等外部后端。
4. 按实际任务结果继续补充项目摘要与最终复盘。
5. 继续逐页处理飞书 Wiki 尚未覆盖的内容，并取得抖音视频完整文件、逐字稿和画面文字；当前不得声称已完成全库学习。

## 风险、停止条件与恢复注意事项

- 复制 `D:\Knowledge` 只能搬走规则和轻量工作状态，不能搬走外部素材、软件与登录授权。
- 新电脑运行恢复脚本后要重启 Codex，并用新对话测试 Skill。
- Skill 可被新对话发现不等于外部功能已可用；插件、账号或 API 未配置时必须停止并明确报告缺项。
- 不得写入密码、Cookie、API Key、访问令牌或私人登录信息。
