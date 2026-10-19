import json
import os
import subprocess
import sys
import time
from pathlib import Path
from shutil import which


TOKEN = os.environ["SPREADSHEET_TOKEN"]
OUTPUT_ROWS = int(os.environ.get("FORMULA_ROWS", "300"))
INPUT_ROWS = int(os.environ.get("INPUT_ROWS", "200"))


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

INPUT_TITLE = "ChangeInput"
PENDING_TITLE = "\u5f85\u5904\u7406\u6d3e\u5de5"
ACTION_STATUSES = ["\u4e0b\u67b6", "\u5f00\u9884\u8d2d", "\u5173\u9884\u8d2d", "\u5f85\u786e\u8ba4"]


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
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def formula(text):
    return {"type": "formula", "text": text}


def write_range(sheet_id, cell_range, values):
    run_cli(
        [
            "sheets",
            "+write",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{sheet_id}!{cell_range}",
            "--values",
            json.dumps(values, ensure_ascii=True),
        ]
    )


info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
sheets = {sheet["title"]: sheet["sheet_id"] for sheet in info["data"]["sheets"]["sheets"]}
input_id = sheets[INPUT_TITLE]
pending_id = sheets[PENDING_TITLE]

pending_preview = run_cli(
    [
        "sheets",
        "+read",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{pending_id}!A1:J10",
        "--value-render-option",
        "FormattedValue",
    ]
)["data"]["valueRange"].get("values", [])
header_row = next(
    (index for index, row in enumerate(pending_preview, 1) if len(row) > 1 and row[0] == "\u5e97\u94fa" and row[1] == "SKU"),
    None,
)
if header_row is None:
    raise SystemExit("Cannot locate 待处理派工 header row.")
first_row = header_row + 1
last_row = first_row + OUTPUT_ROWS - 1

run_cli(
    [
        "sheets",
        "+set-dropdown",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--range",
        f"{input_id}!B2:B{INPUT_ROWS}",
        "--condition-values",
        json.dumps(["\u4e0b\u67b6", "\u5f00\u9884\u8d2d", "\u5173\u9884\u8d2d", "\u5f85\u786e\u8ba4", "\u6b63\u5e38"], ensure_ascii=True),
        "--colors",
        json.dumps(["#F4CCCC", "#FCE5CD", "#D9EAD3", "#FFF2CC", "#D9EAD3"], ensure_ascii=True),
        "--highlight",
    ]
)
write_range(
    input_id,
    "E2:E2",
    [["\u5728 A \u5217\u586b SKU\uff0cB \u5217\u9009\u4e0b\u67b6/\u5f00\u9884\u8d2d/\u5173\u9884\u8d2d/\u5f85\u786e\u8ba4\u3002\u6539\u56de\u6b63\u5e38\u65f6\uff0cB \u5217\u9009\u6b63\u5e38\uff0c\u9996\u9875\u4f1a\u81ea\u52a8\u6d88\u5931\u3002"]],
)

count_expr = "+".join(f'COUNTIF(C{first_row}:C{last_row},"{status}")' for status in ACTION_STATUSES)
filter_expr = "+".join(f'(C{first_row}:C{last_row}="{status}")' for status in ACTION_STATUSES)
write_range(
    pending_id,
    "B1:B1",
    [
        [
            formula(
                f'=IF(({count_expr})=0,"0 \u6761\uff0c\u6d89\u53ca 0 \u4e2a\u5e97\u94fa",({count_expr})&" \u6761\uff0c\u6d89\u53ca "&IFERROR(COUNTA(UNIQUE(FILTER(A{first_row}:A{last_row},{filter_expr}))),0)&" \u4e2a\u5e97\u94fa")'
            )
        ]
    ],
)

for start in range(first_row, last_row + 1, 20):
    formulas = []
    for row in range(start, min(start + 20, last_row + 1)):
        formulas.append(
            [
                formula(
                    f'=IF(C{row}="\u5f00\u9884\u8d2d","\u8bbe\u7f6e\u4e3a\u9884\u8d2d",IF(C{row}="\u5173\u9884\u8d2d","\u5173\u95ed\u9884\u8d2d",IF(C{row}="\u4e0b\u67b6","\u4e0b\u67b6",IF(C{row}="\u5f85\u786e\u8ba4","\u786e\u8ba4\u5904\u7406\u65b9\u5f0f",""))))'
                )
            ]
        )
    write_range(pending_id, f"D{start}:D{start + len(formulas) - 1}", formulas)

time.sleep(2)
print(json.dumps({"input_sheet": input_id, "pending_sheet": pending_id, "first_output_row": first_row, "last_output_row": last_row, "added_status": "\u5173\u9884\u8d2d"}, ensure_ascii=False))
