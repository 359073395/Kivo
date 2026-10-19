import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
from faster_whisper import WhisperModel


INPUT = Path(sys.argv[1]).expanduser().resolve()
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "medium")
LANG_SETTING = os.environ.get("WHISPER_LANG", "").strip()
LANG = None if not LANG_SETTING or LANG_SETTING.lower() == "auto" else LANG_SETTING


def find_knowledge_root():
    candidates = []
    configured = os.environ.get("KNOWLEDGE_ROOT", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())
    for start in (Path(__file__).resolve(), Path.cwd(), INPUT.parent):
        candidates.extend([start, *start.parents])
    candidates.append(Path("D:/Knowledge"))

    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "knowledge-base.json").is_file():
            return candidate
    raise RuntimeError("找不到包含 knowledge-base.json 的知识库；请设置 KNOWLEDGE_ROOT。")


def read_machine_paths(root):
    config = root / "辅助" / "配置" / "machine-paths.local.json"
    if not config.is_file():
        return {}
    try:
        return json.loads(config.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_work_dir(root, machine_paths):
    configured = os.environ.get("WHISPER_WORK_DIR", "").strip()
    if configured:
        base = Path(configured).expanduser()
    elif machine_paths.get("productionWorkRoot"):
        base = Path(machine_paths["productionWorkRoot"]).expanduser() / "video-transcript"
    else:
        base = Path(tempfile.gettempdir()) / "video-transcript"
    base = base.resolve()
    try:
        base.relative_to(root)
    except ValueError:
        pass
    else:
        raise RuntimeError("WHISPER_WORK_DIR 必须位于知识库外。")
    base.mkdir(parents=True, exist_ok=True)
    return base


def resolve_ffmpeg(machine_paths):
    configured = os.environ.get("FFMPEG_PATH", "").strip() or machine_paths.get("ffmpegPath", "")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_dir():
            candidate = candidate / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if candidate.is_file():
            return str(candidate.resolve())
    on_path = shutil.which("ffmpeg")
    return on_path or imageio_ffmpeg.get_ffmpeg_exe()


def media_kind(path):
    audio_extensions = {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma"}
    return "音频" if path.suffix.lower() in audio_extensions else "视频"


if not INPUT.is_file():
    raise FileNotFoundError(INPUT)

KNOWLEDGE_ROOT = find_knowledge_root()
MACHINE_PATHS = read_machine_paths(KNOWLEDGE_ROOT)
TMP = resolve_work_dir(KNOWLEDGE_ROOT, MACHINE_PATHS)
FFMPEG = resolve_ffmpeg(MACHINE_PATHS)
KIND = media_kind(INPUT)

print("ffmpeg:", FFMPEG, flush=True)
print("work_dir:", TMP, flush=True)

stem = INPUT.stem
wav = TMP / (stem + ".wav")

# 1) extract mono 16kHz wav (skip if already present)
if wav.exists() and wav.stat().st_size > 1_000_000:
    print("Reusing existing wav:", wav, flush=True)
else:
    cmd = [FFMPEG, "-y", "-i", str(INPUT), "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(wav)]
    print("Extracting audio...", flush=True)
    subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
    print("Audio extracted:", wav, flush=True)

# 2) load model
language_label = LANG or "auto"
print(f"Loading whisper model: {MODEL_SIZE} (lang={language_label})", flush=True)
CPU_THREADS = int(os.environ.get("WHISPER_THREADS", "8"))
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", cpu_threads=CPU_THREADS)

# 3) transcribe — original model parameters are unchanged; only language is configurable/automatic.
print("Transcribing...", flush=True)
transcribe_args = dict(
    beam_size=5,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
)
if LANG is not None:
    transcribe_args["language"] = LANG
segments, info = model.transcribe(str(wav), **transcribe_args)
print(f"Detected lang={info.language} p={info.language_probability:.2f}", flush=True)


def fmt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


rows = []
full = []
count = 0
for seg in segments:
    rows.append(
        {
            "start": seg.start,
            "end": seg.end,
            "start_fmt": fmt(seg.start),
            "end_fmt": fmt(seg.end),
            "text": seg.text.strip(),
        }
    )
    full.append(seg.text.strip())
    count += 1
    if count % 20 == 0:
        print(f"progress: {count} segments, t={fmt(seg.end)}", flush=True)

configured_out = os.environ.get("OUT_DIR", "").strip()
out_dir = Path(configured_out).expanduser().resolve() if configured_out else KNOWLEDGE_ROOT / "资源" / "raw" / "sources" / KIND
out_dir.mkdir(parents=True, exist_ok=True)
out_md = out_dir / (stem + "_transcript.md")

processed_duration = float(getattr(info, "duration", 0) or 0)
last_speech = rows[-1]["end"] if rows else 0
duration = processed_duration or last_speech
with out_md.open("w", encoding="utf-8") as f:
    f.write("# 视频逐字稿\n\n" if KIND == "视频" else "# 音频逐字稿\n\n")
    f.write(f"- **源文件**：`{INPUT.name}`\n")
    f.write(f"- **媒体类型**：{KIND}\n")
    f.write(f"- **语言**：{info.language}\n")
    f.write(f"- **语言设置**：{language_label}\n")
    f.write(f"- **识别模型**：faster-whisper `{MODEL_SIZE}`\n")
    f.write(f"- **音频时长**：{fmt(duration)}\n")
    f.write("- **处理状态**：complete（转写生成器已完整遍历）\n")
    f.write(f"- **生成时间**：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("---\n\n")
    for row in rows:
        f.write(f"**[{row['start_fmt']} - {row['end_fmt']}]**  {row['text']}\n\n")
    f.write("\n---\n\n## 纯文本（无时间戳）\n\n")
    f.write("".join(full))

print("WROTE", out_md, "segments:", len(rows), flush=True)
print("FIRST_LINES:", json.dumps(rows[:3], ensure_ascii=False)[:500], flush=True)
