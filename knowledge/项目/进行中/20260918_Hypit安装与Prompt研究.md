# Hypit 安装与 Prompt 研究

用户任务：安装 https://github.com/hypit-ai/hypit 并仔细拆解其 Prompt 如何生成。

日期：2026-09-18。状态：本地安装、文本与渲染验证、源码研究完成；云端模型未连接，业务效果未验证。

当前机器：知识库 `F:\Knowledge`，生产根 `F:\820`；恢复时先读取 `辅助/配置/machine-paths.local.json`。

- 源码：`F:\820\hypit`，0.2.5，commit `5a367dd585ddb1d68e3efeaed5599f3e1ff04d5a`。
- 实验：`F:\820\hypit-lab`；入口 `README.zh-CN.md`；启动 `start-studio.ps1`。
- 官方工具 Skill：`G:\Codex\UserData\.codex\skills\hypit`。
- Studio 当前地址：`http://localhost:4317/`，机器重启后需重新启动。
- 两个 Prompt Build：`bld_20260918T080100400Z_0864ECFA37`；视频 Build：`bld_20260918T080222593Z_39E6DFABD1`。
- 成片：`F:\820\hypit-lab\outputs\hypit-demo.mp4`；8 秒、540×960、30 fps；技术解码通过，查看过第 6 秒画面，未完成整段人工视听验收。
- 实验使用本地 endpoints，没有云端生成请求。

报告：[安装与生成机制拆解](../../资产/报告/20260918_Hypit安装与Prompt生成机制拆解.md)。
来源：[固定版本来源卡](../../资源/来源索引/2026-09-18_Hypit源码与Prompt来源卡.md)。
执行参考：[Hypit 研究恢复与边界](../../skill/tiktok-content-system/references/hypit-prompt-research.md)。

已验证：TypeScript check、29 项相关上游测试、Prompt Target 构建为 0 请求、独立导出、官方聊天示例本地渲染、Studio HTTP 200、全局命令启动器。

修正记录：初次误把 Kit import suffix 写成 speaker-v1；实际 package exports 为 speaker，template ID 才是 speaker-v1。Prompt get 输出为目录内 value.json，便利文本从 value.value 提取。

业务边界：不把官方审美和模型选择改成现行 TikTok 默认；不把本地成功升级为生成模型效果或批量生产批准。后续若要求生产，先恢复真实项目、账号和素材状态。
