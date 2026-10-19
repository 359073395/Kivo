import json
import os
import subprocess
import sys
from pathlib import Path
from shutil import which


TOKEN = os.environ["SPREADSHEET_TOKEN"]
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

PENDING_TITLE = "\u5f85\u5904\u7406\u6d3e\u5de5"
STATUS_TITLE = "SKU\u72b6\u6001\u603b\u63a7"
DISPATCH_TITLE = "\u5458\u5de5\u6267\u884c\u6e05\u5355"
ACTION_STATUSES = {"\u4e0b\u67b6", "\u5f00\u9884\u8d2d", "\u5173\u9884\u8d2d", "\u5f85\u786e\u8ba4"}


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


def write_range(sheet_id, range_a1, values):
    run_cli(
        [
            "sheets",
            "+write",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{sheet_id}!{range_a1}",
            "--values",
            json.dumps(values, ensure_ascii=True),
        ]
    )


def ensure_rows(sheet_id, needed):
    info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
    for sheet in info["data"]["sheets"]["sheets"]:
        if sheet["sheet_id"] != sheet_id:
            continue
        current = sheet.get("grid_properties", {}).get("row_count", 200)
        if needed > current:
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
                    str(needed - current),
                ]
            )
        return


def instruction(status):
    if status == "\u4e0b\u67b6":
        return "\u4e0b\u67b6"
    if status == "\u5f00\u9884\u8d2d":
        return "\u8bbe\u7f6e\u4e3a\u9884\u8d2d"
    if status == "\u5173\u9884\u8d2d":
        return "\u5173\u95ed\u9884\u8d2d"
    if status == "\u5f85\u786e\u8ba4":
        return "\u786e\u8ba4\u5904\u7406\u65b9\u5f0f"
    return "\u6062\u590d\u6b63\u5e38/\u53d6\u6d88\u6807\u8bb0"


def prices_for_record(price_rows, index):
    row = price_rows[index] if index < len(price_rows) else []
    return [(row[i] if i < len(row) and row[i] is not None else "") for i in range(3)]


payload = json.loads(DATA.read_text(encoding="utf-8"))
records = sorted(payload["records"], key=lambda item: (item["store"], item["sku"], item["source_row"]))

info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
sheets = info["data"]["sheets"]["sheets"]
title_to_id = {sheet["title"]: sheet["sheet_id"] for sheet in sheets}

if PENDING_TITLE in title_to_id:
    pending_id = title_to_id[PENDING_TITLE]
else:
    res = run_cli(
        [
            "sheets",
            "+create-sheet",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--title",
            PENDING_TITLE,
            "--index",
            "0",
        ]
    )
    pending_id = None

    def walk(obj):
        global pending_id
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "sheet_id":
                    pending_id = value
                    return
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(res)
    if not pending_id:
        raise SystemExit("Cannot create pending sheet")

run_cli(
    [
        "sheets",
        "+update-sheet",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--sheet-id",
        pending_id,
        "--index",
        "0",
        "--frozen-row-count",
        "4",
        "--frozen-col-count",
        "2",
    ]
)

status_sheet = title_to_id[STATUS_TITLE]
status_data = run_cli(
    [
        "sheets",
        "+read",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{status_sheet}!A1:F1000",
    ]
)["data"]["valueRange"].get("values", [])

status_by_sku = {}
for row in status_data[1:]:
    if len(row) >= 2 and row[0] and row[1] in ACTION_STATUSES:
        status_by_sku[str(row[0])] = {
            "status": row[1],
            "note": row[4] if len(row) > 4 else "",
            "date": row[5] if len(row) > 5 else "",
        }

price_rows = run_cli(
    [
        "sheets",
        "+read",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{title_to_id[DISPATCH_TITLE]}!H2:J{len(records) + 1}",
    ]
)["data"]["valueRange"].get("values", [])

pending_rows = []
seen_store_skus = set()
for idx, record in enumerate(records):
    item = status_by_sku.get(record["sku"])
    key = (record["store"], record["sku"])
    if not item or key in seen_store_skus:
        continue
    seen_store_skus.add(key)
    pending_rows.append(
        [
            record["store"],
            record["sku"],
            item["status"],
            instruction(item["status"]),
            "\u672a\u5904\u7406",
            item["date"],
            item["note"],
            *prices_for_record(price_rows, idx),
        ]
    )

store_count = len({row[0] for row in pending_rows})
header = [
    [
        "\u5f53\u524d\u5f85\u5904\u7406\u4efb\u52a1",
        f"{len(pending_rows)} \u6761\uff0c\u6d89\u53ca {store_count} \u4e2a\u5e97\u94fa",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
    [
        "\u4f7f\u7528\u65b9\u5f0f",
        "\u5458\u5de5\u53ea\u770b\u4e0b\u9762\u5217\u8868\uff1a\u5e97\u94fa + SKU + \u9700\u8981\u4fee\u6539\u4e3a\u3002\u505a\u5b8c\u540e\u628a\u5b8c\u6210\u72b6\u6001\u6539\u6210\u5df2\u5b8c\u6210\u3002",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
    ["", "", "", "", "", "", "", "", "", ""],
]
table = [
    [
        "\u5e97\u94fa",
        "SKU",
        "\u9700\u8981\u4fee\u6539\u4e3a",
        "\u5458\u5de5\u64cd\u4f5c",
        "\u5b8c\u6210\u72b6\u6001",
        "\u66f4\u65b0\u65f6\u95f4",
        "\u5907\u6ce8",
        "\u4e0a\u67b6\u539f\u4ef7",
        "\u65e5\u5e38\u552e\u4ef7",
        "\u5e73\u53f0\u6d3b\u52a8\u4ef7",
    ],
    *pending_rows,
]

ensure_rows(pending_id, max(200, len(header) + len(table) + 20))
write_range(pending_id, "A1:J200", [[""] * 10 for _ in range(200)])
write_range(pending_id, f"A1:J{len(header) + len(table)}", header + table)

run_cli(
    [
        "sheets",
        "+set-style",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{pending_id}!A1:J1",
        "--style",
        json.dumps({"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#C65911"}, ensure_ascii=True),
    ]
)
run_cli(
    [
        "sheets",
        "+set-style",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{pending_id}!A4:J4",
        "--style",
        json.dumps({"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#1F4E78"}, ensure_ascii=True),
    ]
)
if pending_rows:
    run_cli(
        [
            "sheets",
            "+set-style",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{pending_id}!A5:J{4 + len(pending_rows)}",
            "--style",
            json.dumps({"backColor": "#FCE4D6"}, ensure_ascii=True),
        ]
    )

print(json.dumps({"pending_sheet_id": pending_id, "pending_rows": len(pending_rows), "stores": store_count}, ensure_ascii=False))
