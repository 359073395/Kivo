# Video / Audio → Markdown Transcript

本模块以大李公开提供的原版 `video-transcript` Skill 为基线。除用户明确指定的六项本地化修正外，保留原版的模型、参数、转写、段落合并和单文件 Markdown 交付方法，不自行改成另一套流程。

## When to use

- 用户提供视频或音频，要求逐字稿、字幕稿、transcript 或提取说话内容。
- 输出目标是 Markdown；如需 `.srt`/`.vtt`，在原写入器上另行适配。

## Environment setup (managed Python)

使用隔离 Python 环境，不污染全局 Python。运行时路径必须动态发现或来自本机配置，不复制作者电脑上的 macOS 路径。

需要的包仍与原版一致：

```text
faster-whisper
imageio-ffmpeg
```

Windows 当前实测环境使用 Python 3.11 x64 和 Microsoft Visual C++ 2015–2022 x64 Runtime；兼容锁定见 [requirements-windows.lock.txt](../scripts/video-transcript/requirements-windows.lock.txt)。本机的 CTranslate2 4.6.3/4.8.1 在载入权重时发生访问冲突，因此固定为已经通过 medium 离线推理的 4.0.0，不要自动升级。完成配置后，可用 [run-speech-transcription.ps1](../scripts/video-transcript/run-speech-transcription.ps1) 调用隔离环境；该入口只完成原版语音转写与合并，随后仍须执行画面 OCR、错字复核和完整性校验。

原版默认模型仍为 `Systran/faster-whisper-medium`，首次下载约 1.5 GB。虚拟环境、模型、WAV、抽帧和 OCR 临时文件保存在知识库外；只把最终 Markdown 写回知识库。

FFmpeg 的查找顺序：`FFMPEG_PATH` → `辅助/配置/machine-paths.local.json` 中的 `ffmpegPath` → `PATH` → `imageio-ffmpeg`。不得写死用户名、盘符或 WorkBuddy 目录。

## CRITICAL: HuggingFace download behind a proxy

当代理导致 HuggingFace/Xet 下载失败或返回 `401 Unauthorized` 时，沿用原版修复：

```text
HF_ENDPOINT=https://hf-mirror.com
HF_XET_DISABLED=1
HF_HUB_ENABLE_HF_TRANSFER=0
```

先用 `hf_hub_download(repo_id="Systran/faster-whisper-medium", filename="config.json")` 做小文件连通性检查，再下载完整模型。不要把密钥、代理凭据或模型缓存写入知识库。

## Transcribe

运行 [scripts/video-transcript/transcribe.py](../scripts/video-transcript/transcribe.py)：

```powershell
python transcribe.py "D:\外部工作目录\source.mp4"
```

原版核心参数保持不变：

- `WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=N)`；
- `beam_size=5`；
- `vad_filter=True`；
- `min_silence_duration_ms=500`；
- 默认 `medium`，默认 8 线程；
- 不向 `model.transcribe` 传 `num_workers`。

唯一语言修正：不再写死中文。默认让 Whisper 自动识别；确知语言时才设置 `WHISPER_LANG=zh`、`id`、`en` 等。实际识别语言写入最终稿。

性能判断保持原版说明：30 分钟视频在 CPU、medium int8、8线程下约需25–30分钟；`small` 通常快2–4倍，但中文准确率可能下降。除非时间紧张，逐字稿优先 `medium`。

## Keep long background runs ALIVE

沿用原版要求：长转写启动后保持同一任务存活，持续等待并查看进度，直到 Markdown 确实生成；不得启动后台进程后直接结束任务。每次等待不超过当前环境允许的单次上限。

## Post-process for readability

原始 VAD 片段通常只有1–3秒。运行 [scripts/video-transcript/merge.py](../scripts/video-transcript/merge.py)，把连续短片段合并为自然段，同时保留全部逐字内容和每段起止时间：

```powershell
python merge.py "D:\Knowledge\资源\raw\sources\视频\source_transcript.md"
```

格式保持原版：

```text
**[HH:MM:SS - HH:MM:SS]**  合并后的整段文字……
```

合并后重新生成同一文件中的“纯文本（无时间戳）”部分，不建立重复文字稿。

## Visual text / PPT / product parameters

这是对原版缺少画面信息的定向修正，不改变语音转写方法。

1. 对视频运行 [scripts/video-transcript/extract_frames.py](../scripts/video-transcript/extract_frames.py)。抽帧只写入知识库外的工作目录。
2. 用当前 AI 的图像理解/OCR能力，或本机可用 OCR 引擎，检查清单中的全部抽帧；没有 OCR 能力时停止并明确报告，不能把纯语音稿冒充完整视频稿。
3. 去重后把重要字幕、PPT标题与要点、表格、产品名称、规格、价格、界面步骤及纯画面含义写入同一个逐字稿的 `## 画面文字与视觉信息`，每条保留时间点和“原字/OCR不确定/画面描述”标记。
4. 画面没有新增信息时也记录“已检查，未发现需要补充的视觉信息”，而不是省略检查。

## Completeness, coverage, and typo checks

完成合并和画面补充后，运行 [scripts/video-transcript/verify_transcript.py](../scripts/video-transcript/verify_transcript.py)：

```powershell
python verify_transcript.py "D:\外部工作目录\source.mp4" "D:\Knowledge\资源\raw\sources\视频\source_transcript.md"
```

先做一次语境错字复核并写入同一文件的 `## 错字复核`，重点核对人名、品牌、SKU、数字、单位、价格和 OCR 与语音冲突；不确定内容保留 `[听不清]` 或 `[OCR不确定：…]`，不得猜写。然后运行脚本，自动检查源文件名、处理完成标记、时间戳顺序、起止范围、媒体时长、异常长空档、纯文本段、视觉检查记录和错字复核记录，并把结果写入同一文件的 `## 自动校验记录`。如果确有长静音或无语音片尾，再把人工确认写入 `## 覆盖率人工复核` 后重跑校验。

自动检查失败、末尾覆盖异常、关键画面未检查或错字复核未完成时，不得标记为最终稿。

## Knowledge archive

这是对原版只写用户工作区的定向修正：

- 脚本先从自身路径、当前目录或 `KNOWLEDGE_ROOT` 查找 `knowledge-base.json`，因此知识库搬家后不依赖固定 `D:\Knowledge` 盘符；仅当该标记真实存在时才回退到 `D:\Knowledge`。
- 视频最终稿自动写入 `资源/raw/sources/视频/`；音频最终稿自动写入 `资源/raw/sources/音频/`。
- 原视频、WAV、抽帧、OCR缓存和模型仍在知识库外。
- 用户显式设置 `OUT_DIR` 时允许改写最终输出目录，但蒸馏任务结束前仍需把最终清洗后的 Markdown 归档到上述知识库位置。

## Deliverable

仍只交付一个 `<stem>_transcript.md`：元数据、带时间戳段落、纯文本、画面文字与视觉信息、自动校验记录。完成后再进入原有知识蒸馏流程。
