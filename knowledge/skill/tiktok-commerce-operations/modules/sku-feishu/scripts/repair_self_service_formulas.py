import json
import os
import subprocess
import sys
from pathlib import Path
from shutil import which


TOKEN = os.environ["SPREADSHEET_TOKEN"]


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
DATA_TITLE = "DispatchData"
INPUT_ROWS = 200
FORMULA_ROWS = 300


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


info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
sheets = {sheet["title"]: sheet["sheet_id"] for sheet in info["data"]["sheets"]["sheets"]}
pending_id = sheets["\u5f85\u5904\u7406\u6d3e\u5de5"]
data_id = sheets[DATA_TITLE]

row_count = next(sheet["grid_properties"]["row_count"] for sheet in info["data"]["sheets"]["sheets"] if sheet["title"] == DATA_TITLE)
last_data_row = row_count

write_range(
    pending_id,
    "B1:B1",
    [
        [
            formula(
                f'=IF((COUNTIF(C5:C{FORMULA_ROWS + 4},"\u4e0b\u67b6")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f00\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5173\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f85\u786e\u8ba4"))=0,"0 \u6761\uff0c\u6d89\u53ca 0 \u4e2a\u5e97\u94fa",(COUNTIF(C5:C{FORMULA_ROWS + 4},"\u4e0b\u67b6")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f00\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5173\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f85\u786e\u8ba4"))&" \u6761\uff0c\u6d89\u53ca "&IFERROR(COUNTA(UNIQUE(FILTER(A5:A{FORMULA_ROWS + 4},(C5:C{FORMULA_ROWS + 4}="\u4e0b\u67b6")+(C5:C{FORMULA_ROWS + 4}="\u5f00\u9884\u8d2d")+(C5:C{FORMULA_ROWS + 4}="\u5173\u9884\u8d2d")+(C5:C{FORMULA_ROWS + 4}="\u5f85\u786e\u8ba4")))),0)&" \u4e2a\u5e97\u94fa")'
            )
        ]
    ],
)

for chunk_start in range(2, last_data_row + 1, 10):
    helper_formulas = []
    for row in range(chunk_start, min(chunk_start + 10, last_data_row + 1)):
        helper_formulas.append(
            [
                formula(
                    f'=IFERROR(COUNTIF(FILTER({INPUT_TITLE}!A$2:A${INPUT_ROWS},{INPUT_TITLE}!B$2:B${INPUT_ROWS}<>"\u6b63\u5e38",{INPUT_TITLE}!B$2:B${INPUT_ROWS}<>""),B{row})>0,FALSE)'
                ),
                formula(f'=IF(F{row},VLOOKUP(B{row},{INPUT_TITLE}!A:B,2,FALSE),"")'),
                formula(f'=IF(F{row},IFERROR(VLOOKUP(B{row},{INPUT_TITLE}!A:C,3,FALSE),""),"")'),
                formula(f'=IF(F{row},IFERROR(VLOOKUP(B{row},{INPUT_TITLE}!A:D,4,FALSE),""),"")'),
            ]
        )
    write_range(data_id, f"F{chunk_start}:I{chunk_start + len(helper_formulas) - 1}", helper_formulas)

print(json.dumps({"repaired": True, "data_rows": last_data_row - 1, "formula_rows": FORMULA_ROWS}, ensure_ascii=False))
