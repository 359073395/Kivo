# Kivo · 创作工作台

Windows桌面版、本地网页版共用同一内容工作流。保留上游全部118技能、账号、画像、热点、选题、素材、内容库、日历及发布入口，增加知识检索、手动方法、反馈自学习、通用API与可升级桌面安装包。

## 安装与使用

从[最新发布页](https://github.com/359073395/Kivo/releases/latest)下载 Windows 安装包，当前版本为 `Kivo-Setup-0.3.5.exe`。首次使用请读 [新手使用指南](docs/Kivo-新手使用指南.md)，或在软件内点击“帮助 → 新手使用指南”。支持 Windows 10/11 x64，自带 Python 运行环境。首次启动会校验程序并准备本地知识，可能需要几分钟，加密目录或安全扫描会增加耗时。再次启动会复用本机数据与校验缓存。

安装包尚未使用商业代码签名证书，Windows可能显示未知发布者提示。请从本仓库发布页获取，并核对随发布提供的校验信息。桌面版已包含 FFmpeg、Node.js、Remotion、渲染浏览器和 Python 媒体依赖。平台账号需自行登录，语音识别模型按需下载，云端生图、音乐、视频等服务需配置对应供应商。

在设置中填写支持OpenAI兼容协议的Base URL、Key和模型名。完整工具流程需要模型支持 `tools` 和 `tool_calls` 字段。输入后可直接点击“保存并自测”，系统先保存再测；成功/失败原因固定显示在顶部。拉取到模型列表不等于已经保存配置，连接自测也不等于该模型已完成真实生成。

## 所有个人数据在本地

默认用户数据根为 `%APPDATA%\kivo-desktop`（保留技术目录名；桌面菜单“打开数据文件夹”可查看实际位置）：

| 内容 | 位置 |
|---|---|
| 内置知识的可编辑副本 | `knowledge-vault/` |
| 学习原文与批准方法 | `knowledge/learned/` |
| 反馈与知识索引 | `knowledge/feedback.sqlite3`、`knowledge/knowledge.sqlite3` |
| 内容、作品和会话恢复 | `platform/outputs/`；桌面浏览器历史也保存在本机用户目录 |
| 账号画像 | `platform/profiles/` |
| 大模型配置 | `model.env`，只在本机，不进入安装包或Git仓库 |
| 升级知识冲突 | `knowledge-incoming/<版本>/`，不会覆盖本地修改 |

此电脑存在正式 `F:/Knowledge` 时优先继续读取该库；换电脑没有该路径时自动使用内置本地副本。菜单可选择其他包含 `knowledge-base.json` 的目录，重开后生效。程序升级不删除个人资料、内容或知识；未修改的内置知识可更新，本地修改冲突保留两份。知识库和内容库不使用云端数据库。

使用云端API时，本次任务文本、附件和被检索的相关片段会发给您配置的模型供应商，不会自动上传整套知识库。若要求资料完全不离开电脑，请配置本机模型API；发布到社交平台仍是明确的外部动作。

## 学习闭环

手动文字资料先保存来源和原文，提炼后确认；您已确认的方法可勾选直接使用。后台反馈也可手动填报/批量JSON导入；原数据页返回有身份、有结构化数值的数据时自动摄入。按平台、账号、作品、版本及观察窗口记忆，去重、计算可计算比率、形成下一版复测假设。缺失指标不补0，错误记录可停用，不把一次结果变成全局因果规则。

自学习是可追溯经验和检索迭代，不是自动修改模型权重。平台批准层不会静默改写正式知识库活动规则。原脚本需要网页确认完整参数后执行，可能联网、调用付费服务或影响账号；不是系统沙箱。

## 升级

菜单“应用 → 检查更新”，默认从 `359073395/Kivo` 的最新GitHub Release读取 `latest.yml`。检查成功、无新版本、失败和下载完成都有提示；用户确认后才下载并重启安装，不自动打断任务。网络不能访问GitHub时会报告失败，您也可下载新版安装包覆盖安装，个人数据保留。

## 开发

核心源代码继续位于 `lingxi/`、`easel/`、`web/` 与 `skills/`，`desktop/` 为桌面壳、用户数据保护及安装构建。技术目录/环境变量保留旧名以兼容现有数据，不意味着仍依赖旧客户端。

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
npm.cmd ci --prefix web/frontend
npm.cmd run build --prefix web/frontend
npm.cmd ci --prefix desktop
.\desktop\Prepare-Python.ps1
.\desktop\Prepare-Media.ps1
node desktop/prepare.cjs
npm.cmd run build --prefix desktop
```

Kivo 保留 Easel 的全量技能与平台入口，并加入本地知识库和独立 API 引擎。代码与知识资料沿用各自来源、许可证及证据状态。
