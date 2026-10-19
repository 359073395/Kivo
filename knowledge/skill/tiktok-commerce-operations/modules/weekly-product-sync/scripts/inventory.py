#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xlsx_data_rows(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"损坏的 XLSX: {path}")
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship")
        }
        sheets = workbook.find(f"{{{MAIN_NS}}}sheets")
        if sheets is None or len(sheets) == 0:
            raise ValueError(f"XLSX 没有工作表: {path}")
        selected = next(
            (sheet for sheet in sheets if sheet.attrib.get("name") == "tiktok_chanpin_"),
            sheets[0],
        )
        rel_id = selected.attrib[f"{{{DOC_REL_NS}}}id"]
        target = rel_targets[rel_id].replace("\\", "/")
        if target.startswith("/"):
            sheet_path = target.lstrip("/")
        else:
            sheet_path = os.path.normpath(f"xl/{target}").replace("\\", "/")
        sheet_xml = ET.fromstring(archive.read(sheet_path))
        rows = sheet_xml.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row")
        populated = [row for row in rows if row.findall(f"{{{MAIN_NS}}}c")]
        return max(0, len(populated) - 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    mapping_path = Path(args.mapping).resolve()
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    expected_folders = [entry["folder"] for entry in mapping]
    actual_folders = sorted(item.name for item in root.iterdir() if item.is_dir())
    missing = sorted(set(expected_folders) - set(actual_folders))
    unexpected = sorted(set(actual_folders) - set(expected_folders))

    stores = []
    errors = []
    for entry in mapping:
        folder = root / entry["folder"]
        product = folder / entry["product_file"]
        flash = folder / "Flash Deal.xlsx"
        store = dict(entry)
        store.update({"folder_path": str(folder), "product_path": str(product)})
        try:
            if not folder.is_dir():
                raise FileNotFoundError(f"缺少店铺文件夹: {folder}")
            if not product.is_file():
                raise FileNotFoundError(f"缺少产品表: {product}")
            if not flash.is_file():
                raise FileNotFoundError(f"缺少 Flash Deal.xlsx: {flash}")
            store["product_rows"] = xlsx_data_rows(product)
            store["product_sha256"] = sha256_file(product)
            store["flash_sha256"] = sha256_file(flash)
            store["ok"] = True
        except Exception as exc:
            store["ok"] = False
            store["error"] = str(exc)
            errors.append(str(exc))
        stores.append(store)

    report = {
        "root": str(root),
        "expected_folder_count": len(expected_folders),
        "actual_folder_count": len(actual_folders),
        "missing_folders": missing,
        "unexpected_folders": unexpected,
        "stores": stores,
        "ok": not missing and not unexpected and not errors,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered)
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

