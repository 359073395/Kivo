import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


if len(sys.argv) != 3:
    raise SystemExit("Usage: python verify_transcript.py <media> <transcript.md>")

MEDIA = Path(sys.argv[1]).expanduser().resolve()
TRANSCRIPT = Path(sys.argv[2]).expanduser().resolve()
TIMESTAMP_RE = re.compile(r"^\*\*\[([\d:]+)\s*-\s*([\d:]+)\]\*\*\s+(.+)$", re.MULTILINE)


def to_seconds(value):
    hours, minutes, seconds = (int(part) for part in value.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def media_duration(path):
    configured = os.environ.get("FFPROBE_PATH", "").strip()
    ffprobe = configured or shutil.which("ffprobe")
    if not ffprobe:
        return None
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return float(json.loads(result.stdout)["format"]["duration"])


if not MEDIA.is_file():
    raise FileNotFoundError(MEDIA)
if not TRANSCRIPT.is_file():
    raise FileNotFoundError(TRANSCRIPT)

raw = TRANSCRIPT.read_text(encoding="utf-8")
body_without_old_report = raw.split("\n## 自动校验记录", 1)[0].rstrip()
entries = [(to_seconds(a), to_seconds(b), text.strip()) for a, b, text in TIMESTAMP_RE.findall(body_without_old_report)]
duration = media_duration(MEDIA)
errors = []
warnings = []


def section_content(document, heading):
    marker = "## " + heading
    if marker not in document:
        return ""
    tail = document.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0].strip()

if f"`{MEDIA.name}`" not in raw:
    errors.append("元数据中的源文件名与输入媒体不一致")
if "**处理状态**：complete" not in raw:
    errors.append("缺少完整遍历完成标记")
if not entries:
    errors.append("没有解析到带时间戳的转写段落")
else:
    previous_end = -1
    long_gaps = []
    for start, end, _ in entries:
        if start < previous_end:
            errors.append(f"时间戳倒序或重叠：{start}s < {previous_end}s")
            break
        if end < start:
            errors.append(f"结束时间早于开始时间：{start}s–{end}s")
            break
        if previous_end >= 0 and start - previous_end >= 60:
            long_gaps.append((previous_end, start))
        previous_end = end
    coverage_review = section_content(body_without_old_report, "覆盖率人工复核")
    if long_gaps and not coverage_review:
        warnings.append("存在≥60秒无语音区间，需确认是静音还是漏转：" + ", ".join(f"{a:.0f}s–{b:.0f}s" for a, b in long_gaps[:10]))
    if duration:
        if entries[-1][1] > duration + 5:
            errors.append("最后时间戳超过媒体总时长")
        end_ratio = entries[-1][1] / duration
        if end_ratio < 0.90 and not coverage_review:
            warnings.append(f"最后语音只到媒体的 {end_ratio:.1%}；可能是片尾静音，也可能漏转，必须复核结尾")

if duration is None:
    warnings.append("未取得媒体总时长，无法自动完成末尾覆盖检查")

if "## 纯文本（无时间戳）" not in raw:
    errors.append("缺少纯文本部分")

is_video = "**媒体类型**：视频" in raw
visual_section = section_content(body_without_old_report, "画面文字与视觉信息")
if is_video and not visual_section.strip():
    errors.append("视频缺少画面文字与视觉信息检查记录")

typo_review = section_content(body_without_old_report, "错字复核")
if not typo_review:
    errors.append("缺少语境错字复核记录")

suspicious = []
for _, _, text in entries:
    if re.search(r"(.)\1{3,}", text) or "??" in text or "□□" in text:
        suspicious.append(text[:120])
if suspicious:
    warnings.append(f"发现 {len(suspicious)} 条疑似重复字/乱码，需做语境错字复核")

status = "未通过" if errors else ("需复核" if warnings else "通过")
report = [
    "## 自动校验记录",
    "",
    f"- **状态**：{status}",
    f"- **媒体总时长**：{duration:.2f} 秒" if duration is not None else "- **媒体总时长**：未取得（需人工核对）",
    f"- **时间戳段落数**：{len(entries)}",
    f"- **首末语音位置**：{entries[0][0]} 秒–{entries[-1][1]} 秒" if entries else "- **首末语音位置**：无",
    "- **错字复核重点**：人名、品牌、SKU、数字、单位、价格，以及 OCR 与语音冲突；自动规则不能替代语境复核。",
]
report.append("- **错误**：无" if not errors else "- **错误**：" + "；".join(errors))
report.append("- **警告**：无" if not warnings else "- **警告**：" + "；".join(warnings))
if suspicious:
    report.extend(["", "### 疑似错字/乱码线索", ""] + [f"- {item}" for item in suspicious[:20]])

TRANSCRIPT.write_text(body_without_old_report + "\n\n" + "\n".join(report) + "\n", encoding="utf-8")
print(json.dumps({"status": status, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
raise SystemExit(2 if errors else (3 if warnings else 0))
