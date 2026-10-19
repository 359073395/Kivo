#!/usr/bin/env python3
"""Build a portable JSONL product index from the authoritative XLSX."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN_NS, "r": REL_NS, "p": PKG_REL_NS}


FIELD_MAP = {
    "SKU": "sku",
    "基础SKU": "base_sku",
    "组合数量": "quantity",
    "产品名称": "product_name",
    "规格": "specification",
    "成分": "ingredients",
    "真实卖点": "selling_points",
    "使用方法": "usage",
    "适用人群": "audience",
    "商品属性/认证": "attributes_certifications",
    "Y仓备注": "warehouse_note",
    "上架原价(IDR)": "listing_original_price_idr",
    "日常售价(IDR)": "daily_price_idr",
    "活动价(IDR)": "activity_price_idr",
    "活动价/日常价": "activity_price_ratio",
    "折扣幅度": "discount_rate",
    "优惠金额(IDR)": "discount_amount_idr",
    "店小秘在线刊登价最低(IDR)": "listing_price_min_idr",
    "店小秘在线刊登价最高(IDR)": "listing_price_max_idr",
    "COD": "cod",
    "店小秘查询状态": "dianxiaomi_lookup_status",
    "在线店铺数": "online_shop_count",
    "资料完整度": "profile_completeness",
    "缺失字段": "missing_fields",
    "冲突状态": "conflict_status",
    "18店是否上架": "listed_in_18_shops",
    "参考中文名": "reference_name_cn",
    "店小秘最新更新时间": "dianxiaomi_latest_updated",
    "最佳资料来源": "best_source",
    "店小秘最新主图URL": "latest_image_url",
    "本地原图路径": "local_original_image_path",
    "图片来源": "image_source",
}

NULL_37_FIELDS = {
    "specification",
    "ingredients",
    "selling_points",
    "usage",
    "audience",
    "attributes_certifications",
}

CLAIM_RISK_PATTERNS = {
    "medical_or_treatment": re.compile(r"menyembuhkan|mengobati|obat\b|terapi|insomnia|katarak|retina|bakteri|virus|infeksi|bekas luka|keloid|scar\b|sleep aid|eye drops|tetes mata|nasal|hidung|slim(?:ming)?|weight loss|治疗|治愈|炎症|失眠|疤痕|眼药|鼻腔|减重", re.I),
    "guaranteed_or_permanent": re.compile(r"permanen|selamanya|dijamin|100\s*%|pasti|langsung\s+hilang|永久|保证|立刻见效|根治", re.I),
    "hair_growth_or_loss": re.compile(r"folikel|akar rambut|rambut rontok|pertumbuhan rambut|防脱|生发|毛囊", re.I),
    "whitening_or_body_change": re.compile(r"whitening|memutihkan|pemutih|turun\s*\d+\s*kg|美白|减重|瘦身", re.I),
    "certification_unverified": re.compile(r"BPOM|PIRT|sertifik|认证", re.I),
}


def risk_tags(values: list[object]) -> list[str]:
    combined = " | ".join(str(value or "") for value in values)
    return [name for name, pattern in CLAIM_RISK_PATTERNS.items() if pattern.search(combined)]


def column_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref).group(0)
    value = 0
    for letter in letters:
        value = value * 26 + ord(letter) - 64
    return value - 1


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")) for item in root]


def sheet_paths(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in relationships.findall(f"{{{PKG_REL_NS}}}Relationship")
    }
    result: dict[str, str] = {}
    for sheet in workbook.find(f"{{{MAIN_NS}}}sheets"):
        rel_id = sheet.attrib[f"{{{REL_NS}}}id"]
        target = targets[rel_id].lstrip("/")
        if not target.startswith("xl/"):
            target = posixpath.normpath(posixpath.join("xl", target))
        result[sheet.attrib["name"]] = target
    return result


def cell_value(cell: ET.Element, strings: list[str]):
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t"))
    value_node = cell.find(f"{{{MAIN_NS}}}v")
    if value_node is None or value_node.text is None:
        return None
    raw = value_node.text
    if cell_type == "s":
        return strings[int(raw)]
    if cell_type in {"str", "e"}:
        return raw
    if cell_type == "b":
        return raw == "1"
    try:
        number = float(raw)
        return int(number) if number.is_integer() else number
    except ValueError:
        return raw


def read_rows(archive: zipfile.ZipFile, part: str, strings: list[str]):
    root = ET.fromstring(archive.read(part))
    sheet_data = root.find(f"{{{MAIN_NS}}}sheetData")
    if sheet_data is None:
        return []
    rows = []
    for row in sheet_data.findall(f"{{{MAIN_NS}}}row"):
        values: dict[int, object] = {}
        for cell in row.findall(f"{{{MAIN_NS}}}c"):
            values[column_index(cell.attrib["r"])] = cell_value(cell, strings)
        rows.append((int(row.attrib.get("r", len(rows) + 1)), values))
    return rows


def clean_value(key: str, value):
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        if key in NULL_37_FIELDS and value == "37":
            return None
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--thumbnail-dir", type=Path)
    args = parser.parse_args()

    thumbnail_dir = args.thumbnail_dir or args.output.parents[2] / "assets" / "product-thumbnails"

    with zipfile.ZipFile(args.source) as archive:
        strings = shared_strings(archive)
        parts = sheet_paths(archive)
        rows = read_rows(archive, parts["Y仓SKU产品资料总表"], strings)

    if not rows:
        raise ValueError("The product sheet is empty")
    _, header_row = rows[0]
    headers = {index: str(value) for index, value in header_row.items() if value is not None}
    records = []
    for source_row, values in rows[1:]:
        record = {}
        for index, header in headers.items():
            key = FIELD_MAP.get(header)
            if key:
                record[key] = clean_value(key, values.get(index))
        if not record.get("sku"):
            continue
        original_path = record.get("local_original_image_path")
        if original_path:
            image_name = Path(str(original_path).replace("\\", "/")).name
            matches = sorted(thumbnail_dir.glob(f"{Path(image_name).stem}.*"))
            record["image_thumbnail"] = f"assets/product-thumbnails/{matches[0].name}" if matches else None
            record["original_image_filename"] = image_name
        else:
            record["image_thumbnail"] = None
            record["original_image_filename"] = None
        record.pop("local_original_image_path", None)
        descriptive_values = [
            record.get("product_name"),
            record.get("specification"),
            record.get("ingredients"),
            record.get("selling_points"),
            record.get("usage"),
            record.get("audience"),
            record.get("attributes_certifications"),
            record.get("warehouse_note"),
        ]
        record["claim_risk_tags"] = risk_tags(descriptive_values)
        record["fact_layers"] = {
            "snapshot_confirmed": [
                "sku", "base_sku", "quantity", "listing_original_price_idr", "daily_price_idr", "activity_price_idr",
                "activity_price_ratio", "discount_rate", "discount_amount_idr", "cod",
                "image_thumbnail", "source_workbook", "source_sheet", "source_row"
            ],
            "listing_evidence_needs_verification": [
                "product_name", "specification", "ingredients", "selling_points", "usage",
                "audience", "attributes_certifications", "dianxiaomi_lookup_status",
                "online_shop_count", "listed_in_18_shops", "latest_image_url"
            ],
            "blocked_or_unverified_claims": record["claim_risk_tags"],
        }
        record["source_workbook"] = args.source.name
        record["source_sheet"] = "Y仓SKU产品资料总表"
        record["source_row"] = source_row
        records.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    summary_path = args.summary or args.output.with_name("product_catalog_summary.json")
    summary = {
        "record_count": len(records),
        "source_workbook": args.source.name,
        "source_sheet": "Y仓SKU产品资料总表",
        "sku_unique_count": len({record["sku"] for record in records}),
        "thumbnail_reference_count": sum(bool(record.get("image_thumbnail")) for record in records),
        "notice": "The string 37 in descriptive fields is normalized to null because it is a source placeholder, not a product fact.",
        "fact_layer_notice": "Listing original price, daily price, activity price, discounts, COD and mappings are dated snapshots; descriptive listing fields remain unverified evidence and claim risks are tagged.",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
