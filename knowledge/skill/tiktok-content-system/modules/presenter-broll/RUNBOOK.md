# 内部执行手册：数字人 B-roll 完整带货视频

> 本文件不是独立 Skill。只有 `tiktok-content-system` 路由到 `presenter_broll_mix` 时才读取。旧 `avatar-broll-video-producer` 与旧目录样例均不自动生效。

## 锁定定义

`核验产品事实 -> 原创文案 -> GPT 人物/场景图 -> 锁定真实产品图层 -> 用户最终语音 -> HeyGen 对口型底片 -> 授权 B-roll/产品素材 -> ChatCut 覆盖混剪 -> 校验`

- 用户最终语音是唯一主时间轴；记录哈希后不得静默剪切、重排、替换、重生成、变速或改停顿。
- AI 图像负责人物、环境、空手/持物姿势和光线。真实产品包装、Logo、文字、数量、颜色与比例必须来自锁定产品源图或确定性合成，不能交给模型重画。
- HeyGen 只生成稳定对口型底片；ChatCut 只覆盖画面，主音频连续。

## 输入门禁

- 稳定任务 ID、店铺、精确 SKU、当前产品事实和真实产品图。
- 已审核的印尼语发布稿与中文对照。
- 用户确认的最终语音、肖像/声音/素材权利和目标时长。
- 明确的外部任务目录；从 `productionWorkRoot` 解析，不能写入知识库或 Skill。

缺少产品事实、真实产品图、用户最终语音或权利确认时，停止对应阶段。

## 执行

1. 只有用户明确说“开始/初始化这个 SKU 或批次”时才建立任务包；目录名和层级由当前项目清单决定，不继承截图或旧聊天的固定编号目录。
2. 按钩子、痛点、产品、卖点/演示、证明/顾虑和 CTA 标记画面功能。
3. 先按真实卖点、目标人群和使用场景确定人物与动作，再生成无品牌重绘风险的人物/场景底图，把真实产品确定性合成到手部或场景；按 [商品人物图标准](../../references/product-presenter-image-standard.md) 检查白底图来源、透视、遮挡、接触阴影、环境光、人体工学、手指和产品边缘。
4. 图片通过后，建立执行表并回读路径、双语文案、时间线和素材状态。
5. 锁定用户语音后严格串行提交第一条 HeyGen；保存远端 ID，状态不明时只查询，不重复创建。
6. 底片下载并解码通过后，按时间线在 ChatCut 覆盖 B-roll、产品图、字幕和必要音效。
7. 校验整段音频连续、字幕安全、产品无漂移、素材权利和披露字段。

按需读取：

- [visual-plan.md](references/visual-plan.md)
- [heygen-base-video.md](references/heygen-base-video.md)
- [chatcut-editing.md](references/chatcut-editing.md)
- [composition-validation.md](references/composition-validation.md)
- [schemas.md](references/schemas.md)

## 测试与批量门禁

内容和执行表可整批准备；远程生成与混剪先完成一条样片。只有用户在看到并确认样片后明确说“开始批量”，才提交第二条。任一远端状态不明时标记 `unconfirmed` 并停止重复提交。
