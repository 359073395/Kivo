import json
import os
import subprocess
import sys
from pathlib import Path
from shutil import which


TOKEN = os.environ["SPREADSHEET_TOKEN"]
SKU = os.environ["TARGET_SKU"]
STATUS = os.environ["TARGET_STATUS"]
NOTE = os.environ.get("TARGET_NOTE", "")
DATE = os.environ.get("TARGET_DATE", "")
DATA = Path(os.environ["DATA_JSON"])


def cli_prefix():
    direct = os.environ.get("LARK_CLI_RUNJS")
    node = os.environ.get("NODE_EXE") or which("node.exe") or which("node")
    if direct and node:
        return [node, direct]
    command = os.environ.get("LARK_CLI") or which("lark-cli.cmd") or which("lark-cli")
    if command and node:
        runjs = Path(command).resolve().parent / "node_modules" / "@larksuite" / "cli" / "scripts" / "run.js"
        if runjs.exists():
            return [node, str(runjs)]
    if command:
        return [command]
    raise SystemExit("lark-cli is not installed or is not available on PATH.")


CLI_PREFIX = cli_prefix()


def run_cli(args):
    proc = subprocess.run(
        [*CLI_PREFIX, *args],
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"Command failed: {' '.join(args)}")
    return json.loads(proc.stdout)


def write_range(range_a1, values):
    run_cli(
        [
            "sheets",
            "+write",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            range_a1,
            "--values",
            json.dumps(values, ensure_ascii=True),
        ]
    )


def instruction(status):
    if status == "下架":
        return "请到对应店铺将该 SKU 下架"
    if status == "开预购":
        return "请到对应店铺将该 SKU 设置为预购"
    if status == "关预购":
        return "请到对应店铺将该 SKU 的预购关闭"
    if status == "正常":
        return "该 SKU 恢复正常/取消标记"
    return "请先确认处理方式"


info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
sheet_ids = {s["title"]: s["sheet_id"] for s in info["data"]["sheets"]["sheets"]}

payload = json.loads(DATA.read_text(encoding="utf-8"))
records = sorted(payload["records"], key=lambda x: (x["store"], x["sku"], x["source_row"]))
matches = [(i + 2, r) for i, r in enumerate(records) if r["sku"].lower() == SKU.lower()]
stores = sorted({r["store"] for _, r in matches})

if not matches:
    raise SystemExit(f"SKU not found: {SKU}")

summary = next((s for s in payload["summary"] if s["sku"].lower() == SKU.lower()), None)
if summary:
    status_rows = sorted(payload["summary"], key=lambda x: x["sku"])
    status_row = status_rows.index(summary) + 2
    write_range(
        f"{sheet_ids['SKU状态总控']}!B{status_row}:F{status_row}",
        [[STATUS, summary["store_count"], summary["stores"], NOTE, DATE]],
    )

dispatch_sid = sheet_ids["员工执行清单"]
for row_no, _ in matches:
    write_range(f"{dispatch_sid}!C{row_no}:D{row_no}", [[STATUS, instruction(STATUS)]])
    write_range(f"{dispatch_sid}!G{row_no}:G{row_no}", [[DATE]])

for store in stores:
    title = f"店铺-{store}"[:100]
    sid = sheet_ids[title]
    store_skus = sorted([r["sku"] for r in payload["records"] if r["store"] == store])
    for idx, sku in enumerate(store_skus, 2):
        if sku.lower() == SKU.lower():
            write_range(f"{sid}!B{idx}:B{idx}", [[STATUS]])
            write_range(f"{sid}!E{idx}:E{idx}", [[DATE]])

print(json.dumps({"sku": SKU, "status": STATUS, "stores": stores, "dispatch_rows": [r for r, _ in matches]}, ensure_ascii=False))
