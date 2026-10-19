import json
import os
import subprocess
import sys
import time
from pathlib import Path
from shutil import which


TOKEN = os.environ["SPREADSHEET_TOKEN"]
DATA = Path(os.environ["PAYLOAD_JSON"])


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


def col_letter(n: int) -> str:
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def run_cli(args):
    proc = subprocess.run(
        [*CLI_PREFIX, *args],
        cwd=os.getcwd(),
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


def create_sheet(title: str, index: int) -> str:
    existing = os.environ.get("EXISTING_SHEETS_JSON")
    if existing:
        existing_map = json.loads(existing)
        if title in existing_map:
            return existing_map[title]
    res = run_cli(
        [
            "sheets",
            "+create-sheet",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--title",
            title,
            "--index",
            str(index),
        ]
    )
    data = res.get("data", {})
    # CLI/API shapes can differ slightly; find the first sheet_id-looking value.
    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "sheet_id" and isinstance(v, str):
                    return v
                found = walk(v)
                if found:
                    return found
        if isinstance(obj, list):
            for item in obj:
                found = walk(item)
                if found:
                    return found
        return None

    sid = walk(data)
    if not sid:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        raise SystemExit(f"Cannot find sheet_id for {title}")
    return sid


def write_rows(sheet_id: str, rows, start_row=1, chunk_size=20):
    if not rows:
        return
    width = max(len(r) for r in rows)
    for i in range(0, len(rows), chunk_size):
        chunk = [r + [""] * (width - len(r)) for r in rows[i : i + chunk_size]]
        r1 = start_row + i
        r2 = r1 + len(chunk) - 1
        c2 = col_letter(width)
        run_cli(
            [
                "sheets",
                "+write",
                "--as",
                "user",
                "--spreadsheet-token",
                TOKEN,
                "--range",
                f"{sheet_id}!A{r1}:{c2}{r2}",
                "--values",
                json.dumps(chunk, ensure_ascii=True),
            ]
        )
        time.sleep(0.2)


def style_header(sheet_id: str, width: int):
    run_cli(
        [
            "sheets",
            "+set-style",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{sheet_id}!A1:{col_letter(width)}1",
            "--style",
            json.dumps(
                {
                    "font": {"bold": True, "foreColor": "#FFFFFF"},
                    "backColor": "#1F4E78",
                    "hAlign": 1,
                    "vAlign": 1,
                },
                ensure_ascii=True,
            ),
        ]
    )


def set_dropdown(sheet_id: str, cell_range: str, options, colors=None):
    args = [
        "sheets",
        "+set-dropdown",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{sheet_id}!{cell_range}",
        "--condition-values",
        json.dumps(options, ensure_ascii=True),
    ]
    if colors:
        args.extend(["--highlight", "--colors", json.dumps(colors, ensure_ascii=True)])
    run_cli(args)


payload = json.loads(DATA.read_text(encoding="utf-8"))

info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
existing_sheet_info = info.get("data", {}).get("sheets", {}).get("sheets", [])
existing_title_to_id = {
    s["title"]: s["sheet_id"]
    for s in existing_sheet_info
    if "title" in s and "sheet_id" in s
}
row_counts_by_id = {
    s["sheet_id"]: s.get("grid_properties", {}).get("row_count", 200)
    for s in existing_sheet_info
    if "sheet_id" in s
}
os.environ["EXISTING_SHEETS_JSON"] = json.dumps(existing_title_to_id, ensure_ascii=False)


def ensure_rows(sheet_id: str, needed_rows: int):
    current = row_counts_by_id.get(sheet_id, 200)
    if needed_rows > current:
        run_cli(
            [
                "sheets",
                "+add-dimension",
                "--as",
                "user",
                "--spreadsheet-token",
                TOKEN,
                "--sheet-id",
                sheet_id,
                "--dimension",
                "ROWS",
                "--length",
                str(needed_rows - current),
            ]
        )
        row_counts_by_id[sheet_id] = needed_rows

sheets = []
index = 6
for title in ["派工使用说明", "SKU状态总控", "员工执行清单"]:
    sid = create_sheet(title, index)
    sheets.append((title, sid))
    index += 1

store_ids = {}
for store in payload["stores"]:
    title = f"店铺-{store}"[:100]
    sid = create_sheet(title, index)
    store_ids[store] = sid
    index += 1

sheet_ids = dict(sheets)

write_rows(sheet_ids["派工使用说明"], [["项目", "说明"], *payload["guide"]])
style_header(sheet_ids["派工使用说明"], 2)

ensure_rows(sheet_ids["SKU状态总控"], max(1000, len(payload["status_control"])))
write_rows(sheet_ids["SKU状态总控"], payload["status_control"])
style_header(sheet_ids["SKU状态总控"], 6)
set_dropdown(
    sheet_ids["SKU状态总控"],
    "B2:B1000",
    ["正常", "下架", "开预购", "关预购", "待确认"],
    ["#A9D18E", "#F4CCCC", "#FCE4D6", "#D9EAD3", "#E7E6E6"],
)

ensure_rows(sheet_ids["员工执行清单"], max(3000, len(payload["dispatch"])))
write_rows(sheet_ids["员工执行清单"], payload["dispatch"])
style_header(sheet_ids["员工执行清单"], 7)
set_dropdown(
    sheet_ids["员工执行清单"],
    "C2:C3000",
    ["正常", "下架", "开预购", "关预购", "待确认"],
    ["#A9D18E", "#F4CCCC", "#FCE4D6", "#D9EAD3", "#E7E6E6"],
)
set_dropdown(sheet_ids["员工执行清单"], "E2:E3000", ["未处理", "已完成", "有问题"], ["#FCE4D6", "#A9D18E", "#E7E6E6"])

for store, rows in payload["store_sheets"].items():
    sid = store_ids[store]
    ensure_rows(sid, max(1000, len(rows)))
    write_rows(sid, rows)
    style_header(sid, 5)
    set_dropdown(sid, "B2:B1000", ["正常", "下架", "开预购", "关预购", "待确认"], ["#A9D18E", "#F4CCCC", "#FCE4D6", "#D9EAD3", "#E7E6E6"])
    set_dropdown(sid, "C2:C1000", ["未处理", "已完成", "有问题"], ["#FCE4D6", "#A9D18E", "#E7E6E6"])

out = {
    "created": [{"title": title, "sheet_id": sid} for title, sid in sheets],
    "store_sheets": [{"store": store, "sheet_id": sid} for store, sid in store_ids.items()],
}
print(json.dumps(out, ensure_ascii=False, indent=2))
