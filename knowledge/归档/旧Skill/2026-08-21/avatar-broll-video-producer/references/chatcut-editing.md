# ChatCut 时间线执行

## 门禁

- 只使用已安装、已启用且已完成 OAuth 的 ChatCut Codex 插件。
- 新安装或更新插件后，必须在重新启动 Codex后的新任务中执行；当前安装任务不能假设新 MCP 工具已经加载。
- 缺少 HeyGen 对口型底片、用户主音频、Excel 或必需 B-roll 时不得创建终剪项目。
- ChatCut 不可调用时标记 `chatcut_unavailable`；未经用户明确同意，不切换到本地 FFmpeg、Remotion 或其他剪辑后端。

## 输入

- `04_lipsync_heygen\..._lipsync_master.mp4`
- `03_audio_user\..._voice_master.*`，用于核对底片音轨，不在时间线上叠加第二份人声。
- `05_broll\` 中用户收集并确认可用的痛点、产品、使用、证明和生活方式素材。
- `06_excel\..._混剪执行表.xlsx`

Excel 每个镜头必须明确本地素材路径、开始/结束秒、轨道、素材入/出点、转场、字幕关键词和 `保留HeyGen原音频`。

## 时间线规则

1. 每条任务新建一个 ChatCut 项目，项目名使用 `<safe_sku>_<script_id>_<yyyymmdd>`；记录项目 ID。
2. V1 放完整 HeyGen 对口型底片，时间线从 0 秒开始，保留它的原始口播音轨。
3. V2 放全屏 B-roll，按 Excel 的语义起点覆盖画面；B-roll 自带音频默认静音。
4. V3 放真实产品白底图或产品叠加层；不得用 AI 误画产品替换真实产品图。
5. 静态图使用轻微 Ken Burns 推拉或局部移动填满时长，避免夸张运动。
6. 转场默认硬切；仅在产品亮相或语义柔和连接处使用 4–8 帧短叠化。
7. 添加 TikTok 安全区字幕与少量关键词高亮；不得遮挡人物嘴部、产品标签或平台 AI 标记。
8. 背景音乐可选，必须显著低于口播；没有合适音乐时宁可不加。

## 提交与恢复

- 创建或修改项目前先把当前条状态写为 `chatcut_submitting` 并记录提交意图。
- 保存 ChatCut 项目 ID 后进入 `chatcut_composing`；有项目 ID 时只恢复该项目，不重复创建。
- 用户替换 B-roll 或音频后建立素材版本记录，再更新现有项目。
- 每次编辑后读取 ChatCut 时间线或可视化编辑器状态，确认轨道、时长和素材确实发生变化。
- 远端结果不明确时标记 `unconfirmed`，停止重复提交。

## 导出

- 默认 1080×1920、9:16、MP4、H.264 视频和 AAC 音频。
- 草稿写入 `08_output\draft`；人工复核通过后导出到 `08_output\final`。
- 导出后使用 FFprobe/FFmpeg 做媒体校验，并把导出 ID、文件路径、时长、宽高、编解码和 QC 结果写回 Excel 与 manifest。
