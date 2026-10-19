---
name: avatar-broll-video-producer
description: 按 SKU 建立可交接素材包：用 GPT 图像生成模型根据产品使用场景生成手持真实产品的数字人图，等待用户放入最终语音，调用 HeyGen 以该图片和音频生成对口型底片，再按文案结构、B-roll 文件夹和 Excel 时间线调用 ChatCut 完成竖屏混剪。Use when the user asks for a per-SKU avatar lip-sync package, product-holding presenter image, user-supplied voice workflow, HeyGen image lip-sync, B-roll search plan, ChatCut assembly, or a Seedance-independent mixed-video workflow.
---

# Avatar B-roll Video Producer

## 核心定位

- 把“SKU 素材包准备”“HeyGen 对口型底片”和“ChatCut 插入画面混剪”拆成三个阶段。
- 保留 `heygen-video-producer` 作为纯数字人口播模式；本 Skill 只处理 `presenter_broll_mix`。
- GPT 图像生成模型负责根据 SKU 使用场景生成手持真实产品的数字人图片。
- 用户负责提供已经确认的最终语音文件；本 Skill 不替用户生成或改写语音。
- HeyGen 只用锁定人物图和用户语音生成稳定、完整、可剪辑的对口型底片，不在 HeyGen 内自由生成商品场景或 B-roll。
- ChatCut 按 Excel 时间线覆盖痛点、产品、使用场景、证明或 CTA 画面，口播音频始终连续。
- 不依赖 Seedance；插入画面可来自用户授权素材、合规库存素材、真实产品图或图像生成。

## 核心约束

- Skill 目录只保存流程和轻量参考，真实图片、音频、Excel、视频、manifest、日志和下载缓存只能写入用户本次任务目录。
- 临时任务数据不得写入 `D:\BaiduSyncdisk` 等同步盘；同步盘默认只保存本 Skill 和知识库更新。
- 默认市场 TikTok Shop Indonesia，画幅 9:16，口播 Bahasa Indonesia。
- 用户提供对标爆款时，必须做结构复刻或高度近似改写；对齐时长、段落、句数、钩子、信息密度、卖点顺序、情绪曲线、CTA 和镜头功能，但不得逐句照抄。
- 先确定最终音频，再生成对口型底片；音频锁定后不得静默改文案、语速或停顿。
- 数字人、人脸、声音、产品图和外部素材必须有必要权利与同意；不得克隆未经授权的真人声音或肖像。
- 产品包装、标签、Logo、形态、颜色和使用动作必须与真实 SKU 一致。
- 人物图必须由 GPT 图像生成模型创建，并使用真实产品图作为参考；嘴部无遮挡，产品正面可见，手指和持握自然。
- 用户语音是唯一音频主轨；缺少用户音频时停在 `awaiting_user_audio`，不得调用 HeyGen。
- ChatCut 是默认且指定的终剪后端；工具未安装或未连接时停在 `chatcut_unavailable`，未经用户同意不得静默切换后端。
- 不制作虚假病灶、伪造前后对比、虚构评价、认证、价格、功效或促销。
- 保留平台水印、AI 标记与发布披露字段。

## 开始前读取

- Excel、目录与状态字段：[references/schemas.md](references/schemas.md)
- 镜头拆分、图片和搜索词规则：[references/visual-plan.md](references/visual-plan.md)
- HeyGen 底片与音频主轨：[references/heygen-base-video.md](references/heygen-base-video.md)
- ChatCut 时间线执行：[references/chatcut-editing.md](references/chatcut-editing.md)
- 成片校验：[references/composition-validation.md](references/composition-validation.md)

需要生成或编辑实际图片时，同时使用 `imagegen`。需要创建或修改 Excel 时，同时使用 `spreadsheets:Spreadsheets`。外部 HeyGen 创建动作只能通过已登录的 HeyGen MCP OAuth。终剪只调用已安装、已连接的 ChatCut 工具。

## 输入门禁

每条任务至少确认：

- 稳定 `task_id`、店铺名、SKU、产品标题与已核验卖点。
- 印尼语发布稿与中文逐句对照。
- 产品白底图/透明图；数字人图由 GPT 图像生成模型在本任务中创建。
- 目标输出目录与目标时长。
- `generation_policy_result=passed`。
- `rights_confirmed=true`、`consent_confirmed=true`。

缺少产品图、关键商品事实、权利确认或合规结果时，停止对应条目，不猜测或补造。

## 执行流程

1. 先按 SKU 建立任务文件夹；同一 SKU 的不同文案使用独立运行子目录，禁止覆盖旧素材。可调用 `scripts/create_sku_package.ps1 -OutputRoot <输出目录> -Sku <SKU> -ScriptId <文案编号>` 一次创建全部固定子目录、`package_manifest.json` 和 `ACTIVE_TASK.json`。
2. 把文案拆成钩子、痛点、产品亮相、卖点/演示、证据/顾虑处理和 CTA。
3. 为每段标记画面类型：`presenter`、`pain_broll`、`product_broll`、`usage_broll`、`proof_broll` 或 `cta_product`。
4. 为每个插入段生成英文搜索词、印尼语搜索词、中文释义、禁用画面和备选图片提示词。
5. 调用 GPT 图像生成模型，根据产品实际使用场景和真实产品参考图生成手持产品的数字人图片；逐项检查人物、手部、产品包装、标签、Logo、容量和嘴部无遮挡。
6. 创建单独 Excel 执行表，回读关键单元格，确认绝对路径、双语文案、镜头功能、搜索词、ChatCut 轨道与素材状态完整。
7. 等待用户把最终语音放入指定目录；验证格式、时长、清晰度和授权，记录文件哈希并锁定。不得另外生成第二份语音。
8. 通过 HeyGen MCP OAuth，以锁定人物图和用户语音生成完整对口型底片；严格串行，只提交当前条一次。
9. 下载并校验底片。等待用户把搜索到的插入视频放入对应 B-roll 子目录，并把素材状态改为 `broll_ready`。
10. 调用 ChatCut：V1 放对口型底片并保留其音频，V2/V3 按 Excel 覆盖 B-roll/产品图，添加安全区字幕、关键词高亮、必要音效和低音量背景音乐。
11. 导出后做完整解码、画面、音频、字幕、产品与披露检查，更新 Excel 与 `ACTIVE_TASK.json`。

## 目录初始化与素材交接

- 每次只为明确的 SKU 和文案编号创建一个运行目录；默认格式为 `<safe_sku>\<script_id>_<yyyymmdd>`。
- 用户只需投放三类原始素材：产品白底图放入 `01_product_white`，最终语音放入 `03_audio_user`，收集到的插入画面按用途放入 `05_broll` 的对应子目录。
- `02_presenter_gpt`、`04_lipsync_heygen`、`06_excel`、`07_chatcut` 和 `08_output` 是助手生成或写入的目录，用户无需预先准备内容。
- 初始化目录不等于授权生成。未收到用户对该 SKU 的明确“开始”指令时，只能创建空目录和清单，不得调用图像、HeyGen 或 ChatCut 生成任务。
- 不要求素材使用固定文件名；执行前扫描对应目录并把实际文件绝对路径、哈希和状态写入 Excel 与 manifest。

## 测试与批量门禁

- 内容、搜索词、图片和 Excel 可以整批准备。
- 用户语音、HeyGen 和 ChatCut 默认只测试第一条。
- 第一条完成下载、混剪和校验后，将批次状态设为 `awaiting_batch_approval`。
- 没有用户明确说“开始批量”，不得提交第二条 HeyGen 任务。
- 任何远端状态不明确时标记 `unconfirmed`，不得重复创建。

## 默认成片节奏

- 0–3 秒：数字人钩子或数字人＋产品同框。
- 痛点段：1–3 秒插入场景，口播音频继续。
- 产品与卖点段：数字人与产品特写交替。
- 使用/证明段：只展示真实可支持的动作或外观变化。
- 结尾：回到数字人或数字人＋产品完成 CTA。
- 数字人建议占 35%–55%，插入画面占 45%–65%；根据对标结构调整，不机械套比例。
- 手持产品图片进入 HeyGen 后，产品应稳定停留在胸前或身体侧前方；不要求大幅抬举、转瓶或复杂手势。

## 完成汇报

汇报任务数、GPT 人物图数量、待用户音频数、待搜索素材数、HeyGen 底片数、ChatCut 成片数、跳过/暂停原因、Excel 路径、音频目录、底片目录、成片目录和待人工复核项。只有文件校验、人工质检与披露检查完成的条目才可标记 `ready_to_publish`。
