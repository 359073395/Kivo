import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if len(sys.argv) < 2:
    raise SystemExit("Usage: python extract_frames.py <video> [output_dir] [interval_seconds]")

INPUT = Path(sys.argv[1]).expanduser().resolve()
INTERVAL = float(sys.argv[3]) if len(sys.argv) > 3 else float(os.environ.get("FRAME_INTERVAL", "15"))


def find_knowledge_root():
    configured = os.environ.get("KNOWLEDGE_ROOT", "").strip()
    candidates = [Path(configured).expanduser()] if configured else []
    for start in (Path(__file__).resolve(), Path.cwd(), INPUT.parent):
        candidates.extend([start, *start.parents])
    candidates.append(Path("D:/Knowledge"))
    for candidate in candidates:
        try:
            candidate = candidate.resolve()
        except OSError:
            continue
        if (candidate / "knowledge-base.json").is_file():
            return candidate
    return None


def read_machine_paths(root):
    if root is None:
        return {}
    config = root / "辅助" / "配置" / "machine-paths.local.json"
    try:
        return json.loads(config.read_text(encoding="utf-8-sig")) if config.is_file() else {}
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_ffmpeg(machine_paths):
    configured = os.environ.get("FFMPEG_PATH", "").strip() or machine_paths.get("ffmpegPath", "")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_dir():
            candidate = candidate / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if candidate.is_file():
            return str(candidate.resolve())
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


if not INPUT.is_file():
    raise FileNotFoundError(INPUT)

root = find_knowledge_root()
machine_paths = read_machine_paths(root)
if len(sys.argv) > 2:
    output_dir = Path(sys.argv[2]).expanduser().resolve()
elif os.environ.get("WHISPER_WORK_DIR", "").strip():
    output_dir = Path(os.environ["WHISPER_WORK_DIR"]).expanduser().resolve() / (INPUT.stem + "_frames")
elif machine_paths.get("productionWorkRoot"):
    output_dir = Path(machine_paths["productionWorkRoot"]).expanduser().resolve() / "video-transcript" / (INPUT.stem + "_frames")
else:
    output_dir = Path(tempfile.gettempdir()).resolve() / "video-transcript" / (INPUT.stem + "_frames")

if root is not None:
    try:
        output_dir.relative_to(root)
    except ValueError:
        pass
    else:
        raise RuntimeError("抽帧目录必须位于知识库外。")

output_dir.mkdir(parents=True, exist_ok=True)
ffmpeg = resolve_ffmpeg(machine_paths)

periodic_pattern = output_dir / "periodic_%06d.jpg"
periodic_cmd = [
    ffmpeg,
    "-y",
    "-i",
    str(INPUT),
    "-vf",
    f"fps=1/{INTERVAL}",
    "-q:v",
    "2",
    str(periodic_pattern),
]
subprocess.run(periodic_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

scene_pattern = output_dir / "scene_%06d.png"
scene_cmd = [
    ffmpeg,
    "-y",
    "-i",
    str(INPUT),
    "-vf",
    "select=gt(scene\\,0.35),showinfo",
    "-fps_mode",
    "vfr",
    str(scene_pattern),
]
scene_run = subprocess.run(scene_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
if scene_run.returncode != 0 and "Nothing was written into output file" not in scene_run.stderr:
    raise RuntimeError(scene_run.stderr[-2000:])

scene_times = [float(value) for value in re.findall(r"pts_time:([0-9.]+)", scene_run.stderr)]
periodic_files = sorted(output_dir.glob("periodic_*.jpg"))
scene_files = sorted(output_dir.glob("scene_*.png"))

manifest = output_dir / "frames_manifest.md"
lines = [
    "# 视频抽帧检查清单",
    "",
    f"- 源文件：`{INPUT}`",
    f"- 周期抽帧间隔：{INTERVAL:g} 秒",
    f"- 周期帧：{len(periodic_files)}",
    f"- 场景变化帧：{len(scene_files)}",
    "- 用途：OCR/图像理解检查字幕、PPT、表格、产品参数、界面步骤和纯画面信息；抽帧不是最终知识资产。",
    "",
    "## 周期帧",
    "",
]
for index, frame in enumerate(periodic_files):
    lines.append(f"- `{frame}` — 约 {index * INTERVAL:.1f}s")
lines.extend(["", "## 场景变化帧", ""])
for index, frame in enumerate(scene_files):
    timestamp = scene_times[index] if index < len(scene_times) else None
    suffix = f" — 约 {timestamp:.1f}s" if timestamp is not None else " — 时间待核对"
    lines.append(f"- `{frame}`{suffix}")
manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("WROTE", manifest)
print("periodic:", len(periodic_files), "scene:", len(scene_files))
