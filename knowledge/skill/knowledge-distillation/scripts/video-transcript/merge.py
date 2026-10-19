import re
import sys
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("Usage: python merge.py <transcript.md>")

SRC = Path(sys.argv[1]).expanduser().resolve()
if not SRC.is_file():
    raise FileNotFoundError(SRC)


def to_sec(t):
    h, m, s = (int(x) for x in t.split(":"))
    return h * 3600 + m * 60 + s


def to_hms(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


raw = SRC.read_text(encoding="utf-8")
parts = raw.split("\n---\n", 1)
header = parts[0]
body = parts[1] if len(parts) > 1 else ""

pat = re.compile(r"^\*\*\s*\[([\d:]+)\s*-\s*([\d:]+)\]\*\*\s*(.*)$")
entries = []
for line in body.splitlines():
    match = pat.match(line.strip())
    if match:
        entries.append({"s": to_sec(match.group(1)), "e": to_sec(match.group(2)), "text": match.group(3).strip()})
    if line.strip().startswith("## 纯文本"):
        break

TERM = "。！？!?…"
groups = []
cur = None
for entry in entries:
    if cur is None:
        cur = {"s": entry["s"], "e": entry["e"], "text": entry["text"]}
        continue
    dur = cur["e"] - cur["s"]
    merged_len = len(cur["text"])
    ends_term = cur["text"][-1] in TERM if cur["text"] else False
    if (dur >= 18) or (ends_term and dur >= 6) or merged_len >= 90:
        groups.append(cur)
        cur = {"s": entry["s"], "e": entry["e"], "text": entry["text"]}
    else:
        cur["e"] = entry["e"]
        cur["text"] += entry["text"]
if cur:
    groups.append(cur)

out = [header, ""]
out.append(f"_（说明：原始识别为 {len(entries)} 个细粒度片段，已按语义合并为可读性更好的段落，保留每段起止时间戳。完整逐字内容未删减。）_")
out.extend(["", "---", ""])
plain = []
for group in groups:
    out.append(f"**[{to_hms(group['s'])} - {to_hms(group['e'])}]**  {group['text']}")
    out.append("")
    plain.append(group["text"])

out.extend(["", "---", "", "## 纯文本（无时间戳）", ""])
for i in range(0, len(plain), 4):
    out.append("".join(plain[i : i + 4]))
    out.append("")

SRC.write_text("\n".join(out), encoding="utf-8")
print("groups:", len(groups), "entries:", len(entries))
