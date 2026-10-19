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

T_PENDING = "\u5f85\u5904\u7406\u6d3e\u5de5"
T_STATUS = "SKU\u72b6\u6001\u603b\u63a7"
T_DISPATCH = "\u5458\u5de5\u6267\u884c\u6e05\u5355"
T_PRODUCT = "\u4ea7\u54c1\u603b\u8868"
T_SUMMARY = "SKU\u6c47\u603b"
T_EXCEPTIONS = "\u5f02\u5e38\u8bb0\u5f55"


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


def update_sheet(sheet_id, frozen_rows=1, frozen_cols=0, index=None):
    args = [
        "sheets",
        "+update-sheet",
        "--as",
        "user",
        "--spreadsheet-token",
        TOKEN,
        "--sheet-id",
        sheet_id,
        "--frozen-row-count",
        str(frozen_rows),
        "--frozen-col-count",
        str(frozen_cols),
    ]
    if index is not None:
        args.extend(["--index", str(index)])
    run_cli(args)


def set_style(sheet_id, cell_range, style):
    run_cli(
        [
            "sheets",
            "+set-style",
            "--as",
            "user",
            "--spreadsheet-token",
            TOKEN,
            "--range",
            f"{sheet_id}!{cell_range}",
            "--style",
            json.dumps(style, ensure_ascii=True),
        ]
    )


def set_widths(sheet_id, widths):
    for col, width in widths:
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


def set_height(sheet_id, row, height):
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
            "ROWS",
            "--start-index",
            str(row),
            "--end-index",
            str(row),
            "--fixed-size",
            str(height),
        ]
    )


info = run_cli(["sheets", "+info", "--as", "user", "--spreadsheet-token", TOKEN])
sheets = info["data"]["sheets"]["sheets"]
title_to_id = {s["title"]: s["sheet_id"] for s in sheets}

navy = {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#17365D"}
blue = {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#1F4E78"}
orange = {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#C65911"}
soft_note = {"font": {"bold": True, "foreColor": "#7F3F00"}, "backColor": "#FFF2CC"}
green = {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#38761D"}
gray = {"font": {"bold": True, "foreColor": "#FFFFFF"}, "backColor": "#666666"}

pending_id = title_to_id[T_PENDING]
update_sheet(pending_id, frozen_rows=4, frozen_cols=2, index=0)
set_style(pending_id, "A1:J1", orange)
set_style(pending_id, "A2:J2", soft_note)
set_style(pending_id, "A4:J4", blue)
set_height(pending_id, 1, 34)
set_height(pending_id, 2, 42)
set_height(pending_id, 4, 30)
set_widths(
    pending_id,
    [(1, 170), (2, 250), (3, 115), (4, 160), (5, 110), (6, 120), (7, 280), (8, 105), (9, 105), (10, 115)],
)

status_id = title_to_id[T_STATUS]
update_sheet(status_id, frozen_rows=1, frozen_cols=1)
set_style(status_id, "A1:F1", navy)
set_height(status_id, 1, 30)
set_widths(status_id, [(1, 260), (2, 120), (3, 100), (4, 520), (5, 260), (6, 125)])

dispatch_id = title_to_id[T_DISPATCH]
update_sheet(dispatch_id, frozen_rows=1, frozen_cols=2)
set_style(dispatch_id, "A1:J1", blue)
set_height(dispatch_id, 1, 30)
set_widths(dispatch_id, [(1, 175), (2, 255), (3, 110), (4, 190), (5, 110), (6, 145), (7, 125), (8, 105), (9, 105), (10, 115)])

for title, sheet_id in title_to_id.items():
    if title.startswith("\u5e97\u94fa-"):
        update_sheet(sheet_id, frozen_rows=1, frozen_cols=1)
        set_style(sheet_id, "A1:H1", green)
        set_height(sheet_id, 1, 30)
        set_widths(sheet_id, [(1, 270), (2, 110), (3, 125), (4, 180), (5, 125), (6, 105), (7, 105), (8, 115)])

for title in (T_PRODUCT, T_SUMMARY, T_EXCEPTIONS):
    if title not in title_to_id:
        continue
    sheet_id = title_to_id[title]
    update_sheet(sheet_id, frozen_rows=1, frozen_cols=1)
    set_style(sheet_id, "A1:K1", gray if title == T_EXCEPTIONS else navy)
    set_height(sheet_id, 1, 30)

if T_PRODUCT in title_to_id:
    set_widths(title_to_id[T_PRODUCT], [(1, 170), (2, 260), (3, 145), (4, 120), (5, 170), (6, 110), (7, 105), (8, 105), (9, 115)])
if T_SUMMARY in title_to_id:
    set_widths(title_to_id[T_SUMMARY], [(1, 260), (2, 105), (3, 520), (4, 105), (5, 105), (6, 115)])
if T_EXCEPTIONS in title_to_id:
    set_widths(title_to_id[T_EXCEPTIONS], [(1, 180), (2, 250), (3, 130), (4, 140), (5, 380)])

print(json.dumps({"optimized_sheets": len(title_to_id), "pending_sheet": pending_id}, ensure_ascii=False))
