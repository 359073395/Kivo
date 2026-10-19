import json
import os
import subprocess
import sys
import time
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
INPUT_TITLE = "ChangeInput"
DATA_TITLE = "DispatchData"
TEST_TITLE = "FormulaTest"

FORMULA_ROWS = int(os.environ.get("FORMULA_ROWS", "300"))
INPUT_ROWS = int(os.environ.get("INPUT_ROWS", "200"))


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


def get_info():
    return run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])


def title_to_id():
    info = get_info()
    return {sheet["title"]: sheet["sheet_id"] for sheet in info["data"]["sheets"]["sheets"]}


def create_sheet(title, index):
    run_cli(
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
    return title_to_id()[title]


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


def write_rows(sheet_id, start_row, values, chunk_size=100):
    if not values:
        return
    width = max(len(row) for row in values)
    end_col = chr(ord("A") + width - 1)
    for offset in range(0, len(values), chunk_size):
        chunk = values[offset : offset + chunk_size]
        row1 = start_row + offset
        row2 = row1 + len(chunk) - 1
        write_range(sheet_id, f"A{row1}:{end_col}{row2}", chunk)


def set_style(sheet_id, range_a1, style):
    run_cli(
        [
            "sheets",
            "+set-style",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{sheet_id}!{range_a1}",
            "--style",
            json.dumps(style, ensure_ascii=True),
        ]
    )


def set_width(sheet_id, col, width):
    run_cli(
        [
            "sheets",
            "+update-dimension",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--sheet-id",
            sheet_id,
            "--dimension",
            "COLUMNS",
            "--start-index",
            str(col),
            "--end-index",
            str(col),
            "--fixed-size",
            str(width),
        ]
    )


def update_sheet(sheet_id, **kwargs):
    args = [
        "sheets",
        "+update-sheet",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--sheet-id",
        sheet_id,
    ]
    if "index" in kwargs:
        args.extend(["--index", str(kwargs["index"])])
    if "frozen_rows" in kwargs:
        args.extend(["--frozen-row-count", str(kwargs["frozen_rows"])])
    if "frozen_cols" in kwargs:
        args.extend(["--frozen-col-count", str(kwargs["frozen_cols"])])
    if kwargs.get("hidden"):
        args.append("--hidden")
    run_cli(args)


def formula(text):
    return {"type": "formula", "text": text}


def load_records():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    return sorted(payload["records"], key=lambda item: (item["store"], item["sku"], item["source_row"]))


def read_employee_prices(records_count, employee_sheet_id):
    values = run_cli(
        [
            "sheets",
            "+read",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{employee_sheet_id}!H2:J{records_count + 1}",
            "--value-render-option",
            "FormattedValue",
        ]
    )["data"]["valueRange"].get("values", [])
    out = []
    for idx in range(records_count):
        row = values[idx] if idx < len(values) else []
        out.append([(row[i] if i < len(row) and row[i] is not None else "") for i in range(3)])
    return out


def setup():
    sheets = title_to_id()

    if TEST_TITLE in sheets:
        run_cli(
            [
                "sheets",
                "+delete-sheet",
                "--as",
                "user",
                "--spreadsheet-token",
                TOKEN,
                "--sheet-id",
                sheets[TEST_TITLE],
                "--yes",
            ]
        )
        sheets = title_to_id()

    pending_id = sheets[PENDING_TITLE]
    input_id = sheets.get(INPUT_TITLE) or create_sheet(INPUT_TITLE, 1)
    sheets = title_to_id()
    data_id = sheets.get(DATA_TITLE) or create_sheet(DATA_TITLE, 99)
    sheets = title_to_id()

    update_sheet(pending_id, index=0, frozen_rows=4, frozen_cols=2)
    update_sheet(input_id, index=1, frozen_rows=1, frozen_cols=1)
    update_sheet(data_id, hidden=True)

    input_header = [
        ["SKU", "\u4fee\u6539\u4e3a", "\u5907\u6ce8", "\u66f4\u65b0\u65f6\u95f4", "\u586b\u5199\u8bf4\u660e"],
        ["", "", "", "", "\u5728 A \u5217\u586b SKU\uff0cB \u5217\u9009\u4e0b\u67b6/\u5f00\u9884\u8d2d/\u5173\u9884\u8d2d/\u5f85\u786e\u8ba4\u3002\u6539\u56de\u6b63\u5e38\u65f6\uff0cB \u5217\u9009\u6b63\u5e38\uff0c\u9996\u9875\u4f1a\u81ea\u52a8\u6d88\u5931\u3002"],
    ]
    write_rows(input_id, 1, [[""] * 5 for _ in range(INPUT_ROWS)], chunk_size=50)
    write_range(input_id, "A1:E2", input_header)
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
    set_style(input_id, "A1:E1", {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#38761D"})
    set_style(input_id, "E2:E2", {"font": {"foreColor": "#7F6000"}, "backColor": "#FFF2CC"})
    for col, width in [(1, 270), (2, 120), (3, 280), (4, 130), (5, 620)]:
        set_width(input_id, col, width)

    records = load_records()
    employee_sheet = sheets["\u5458\u5de5\u6267\u884c\u6e05\u5355"]
    prices = read_employee_prices(len(records), employee_sheet)
    data_rows = [["\u5e97\u94fa", "SKU", "\u4e0a\u67b6\u539f\u4ef7", "\u65e5\u5e38\u552e\u4ef7", "\u5e73\u53f0\u6d3b\u52a8\u4ef7", "\u662f\u5426\u5f85\u5904\u7406", "\u4fee\u6539\u4e3a", "\u5907\u6ce8", "\u66f4\u65b0\u65f6\u95f4"]]
    seen = set()
    for record, price in zip(records, prices):
        key = (record["store"], record["sku"])
        if key in seen:
            continue
        seen.add(key)
        data_rows.append([record["store"], record["sku"], *price, "", "", "", ""])
    write_rows(data_id, 1, [[""] * 9 for _ in range(len(data_rows) + 10)], chunk_size=100)
    write_rows(data_id, 1, data_rows, chunk_size=100)
    set_style(data_id, "A1:I1", {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#666666"})

    last_data_row = len(data_rows)
    for chunk_start in range(2, last_data_row + 1, 10):
        helper_formulas = []
        for row in range(chunk_start, min(chunk_start + 10, last_data_row + 1)):
            helper_formulas.append(
                [
                    formula(f'=IFERROR(COUNTIF(FILTER({INPUT_TITLE}!A$2:A${INPUT_ROWS},{INPUT_TITLE}!B$2:B${INPUT_ROWS}<>"\u6b63\u5e38",{INPUT_TITLE}!B$2:B${INPUT_ROWS}<>""),B{row})>0,FALSE)'),
                    formula(f'=IF(F{row},VLOOKUP(B{row},{INPUT_TITLE}!A:B,2,FALSE),"")'),
                    formula(f'=IF(F{row},IFERROR(VLOOKUP(B{row},{INPUT_TITLE}!A:C,3,FALSE),""),"")'),
                    formula(f'=IF(F{row},IFERROR(VLOOKUP(B{row},{INPUT_TITLE}!A:D,4,FALSE),""),"")'),
                ]
            )
        write_range(data_id, f"F{chunk_start}:I{chunk_start + len(helper_formulas) - 1}", helper_formulas)

    base = (
        f'UNIQUE(FILTER({DATA_TITLE}!A2:I{last_data_row},{DATA_TITLE}!F2:F{last_data_row}=TRUE))'
    )

    header = [
        [
            "\u5f53\u524d\u5f85\u5904\u7406\u4efb\u52a1",
            formula(f'=IF((COUNTIF(C5:C{FORMULA_ROWS + 4},"\u4e0b\u67b6")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f00\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5173\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f85\u786e\u8ba4"))=0,"0 \u6761\uff0c\u6d89\u53ca 0 \u4e2a\u5e97\u94fa",(COUNTIF(C5:C{FORMULA_ROWS + 4},"\u4e0b\u67b6")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f00\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5173\u9884\u8d2d")+COUNTIF(C5:C{FORMULA_ROWS + 4},"\u5f85\u786e\u8ba4"))&" \u6761\uff0c\u6d89\u53ca "&IFERROR(COUNTA(UNIQUE(FILTER(A5:A{FORMULA_ROWS + 4},(C5:C{FORMULA_ROWS + 4}="\u4e0b\u67b6")+(C5:C{FORMULA_ROWS + 4}="\u5f00\u9884\u8d2d")+(C5:C{FORMULA_ROWS + 4}="\u5173\u9884\u8d2d")+(C5:C{FORMULA_ROWS + 4}="\u5f85\u786e\u8ba4")))),0)&" \u4e2a\u5e97\u94fa")'),
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
            f"\u5728 {INPUT_TITLE} \u8868\u586b SKU \u548c\u4fee\u6539\u72b6\u6001\uff1b\u8fd9\u91cc\u4f1a\u81ea\u52a8\u663e\u793a\u9700\u8981\u4fee\u6539\u7684\u5e97\u94fa\u3002\u6539\u56de\u6b63\u5e38\u540e\u4f1a\u81ea\u52a8\u6d88\u5931\u3002",
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
    ]
    write_rows(pending_id, 1, [[""] * 10 for _ in range(FORMULA_ROWS + 4)], chunk_size=50)
    write_range(pending_id, "A1:J4", header)

    for chunk_start in range(1, FORMULA_ROWS + 1, 1):
        n = chunk_start
        row = n + 4
        write_range(
            pending_id,
            f"A{row}:B{row}",
            [[formula(f"=IFERROR(INDEX({base},{n},1),\"\")"), formula(f"=IFERROR(INDEX({base},{n},2),\"\")")]],
        )
        write_range(
            pending_id,
            f"C{row}:G{row}",
            [
                [
                    formula(f"=IFERROR(INDEX({base},{n},7),\"\")"),
                    formula(f"=IF(C{row}=\"\u5f00\u9884\u8d2d\",\"\u8bbe\u7f6e\u4e3a\u9884\u8d2d\",IF(C{row}=\"\u5173\u9884\u8d2d\",\"\u5173\u95ed\u9884\u8d2d\",IF(C{row}=\"\u4e0b\u67b6\",\"\u4e0b\u67b6\",IF(C{row}=\"\u5f85\u786e\u8ba4\",\"\u786e\u8ba4\u5904\u7406\u65b9\u5f0f\",\"\"))))"),
                    formula(f"=IF(A{row}=\"\",\"\",\"\u672a\u5904\u7406\")"),
                    formula(f"=IFERROR(INDEX({base},{n},9),\"\")"),
                    formula(f"=IFERROR(INDEX({base},{n},8),\"\")"),
                ]
            ],
        )
        write_range(
            pending_id,
            f"H{row}:J{row}",
            [
                [
                    formula(f"=IFERROR(INDEX({base},{n},3),\"\")"),
                    formula(f"=IFERROR(INDEX({base},{n},4),\"\")"),
                    formula(f"=IFERROR(INDEX({base},{n},5),\"\")"),
                ]
            ],
        )

    set_style(pending_id, "A1:J1", {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#C65911"})
    set_style(pending_id, "A2:J2", {"font": {"bold": True, "foreColor": "#7F3F00"}, "backColor": "#FFF2CC"})
    set_style(pending_id, "A4:J4", {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#1F4E78"})
    for col, width in [(1, 170), (2, 250), (3, 115), (4, 160), (5, 110), (6, 120), (7, 280), (8, 105), (9, 105), (10, 115)]:
        set_width(pending_id, col, width)

    print(
        json.dumps(
            {
                "input_sheet": INPUT_TITLE,
                "data_sheet": DATA_TITLE,
                "data_rows": len(data_rows) - 1,
                "formula_rows": FORMULA_ROWS,
            },
            ensure_ascii=False,
        )
    )


setup()
time.sleep(2)
