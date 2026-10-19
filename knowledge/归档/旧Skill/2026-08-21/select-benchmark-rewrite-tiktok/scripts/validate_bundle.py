#!/usr/bin/env python3
"""Validate the portable skill's required files and knowledge indexes."""

from __future__ import annotations

import json
import hashlib
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "agents/generic-system-prompt.md",
    "references/knowledge-index.md",
    "references/source-manifest.json",
    "references/runtime-and-colleague-testing.md",
    "references/product/Y仓全部SKU产品资料与促销总表_20260808.xlsx",
    "references/product/product_catalog.jsonl",
    "references/product/product_catalog_summary.json",
    "references/operations/Tiktok从入门到精通.docx",
    "references/operations/tiktok-operations-extracted.md",
    "references/operations/operations_extraction_summary.json",
    "references/operations/operations-retrieval-guide.md",
    "references/selection/selection-logic.md",
    "references/benchmark/benchmark-research.md",
    "references/copywriting/rewrite-playbook.md",
    "references/policy-and-rights.md",
    "references/output-contract.md",
    "references/test-cases.md",
    "references/fixtures/rewrite-regression-fixture.json",
    "scripts/validate_bundle.ps1",
]

DESCRIPTIVE_FIELDS = {
    "specification", "ingredients", "selling_points", "usage", "audience", "attributes_certifications"
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        print("Missing required files:")
        print("\n".join(missing))
        raise SystemExit(1)

    catalog = ROOT / "references/product/product_catalog.jsonl"
    records = []
    with catalog.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise SystemExit(f"Invalid JSONL at line {line_number}: {error}") from error
    skus = [row.get("sku") for row in records]
    if len(records) != 571 or len(set(skus)) != 571:
        raise SystemExit(f"Expected 571 unique SKUs, got {len(records)} rows and {len(set(skus))} unique")

    required_product_keys = {"sku", "source_row", "image_thumbnail", "fact_layers", "claim_risk_tags"}
    for row in records:
        missing_keys = required_product_keys - row.keys()
        if missing_keys:
            raise SystemExit(f"Missing product keys for {row.get('sku')}: {sorted(missing_keys)}")
        if "local_original_image_path" in row:
            raise SystemExit(f"Absolute original path leaked for {row['sku']}")
        if Path(str(row["image_thumbnail"])).is_absolute():
            raise SystemExit(f"Non-portable thumbnail path for {row['sku']}")
        for field in DESCRIPTIVE_FIELDS:
            if row.get(field) == "37":
                raise SystemExit(f"Placeholder 37 remains in {field} for {row['sku']}")

    thumbnails = list((ROOT / "assets/product-thumbnails").glob("*"))
    if len(thumbnails) != 571:
        raise SystemExit(f"Expected 571 thumbnails, got {len(thumbnails)}")
    missing_thumbnails = [
        row.get("image_thumbnail")
        for row in records
        if not row.get("image_thumbnail") or not (ROOT / row["image_thumbnail"]).is_file()
    ]
    if missing_thumbnails:
        raise SystemExit(f"Missing thumbnail mappings: {missing_thumbnails[:5]}")

    sku_counts: dict[str, int] = {}
    for row in records:
        sku = str(row.get("sku") or "")
        sku_counts[sku] = sku_counts.get(sku, 0) + 1
    duplicates = [sku for sku, count in sku_counts.items() if count != 1]
    if duplicates:
        raise SystemExit(f"Duplicate SKU mappings: {duplicates[:5]}")

    referenced = {Path(row["image_thumbnail"]).name for row in records}
    actual = {path.name for path in thumbnails}
    if referenced != actual:
        raise SystemExit(f"Thumbnail mapping mismatch: missing={sorted(referenced-actual)[:5]} orphan={sorted(actual-referenced)[:5]}")
    for path in thumbnails:
        data = path.read_bytes()[:8]
        if not data or not (data.startswith(b"\xff\xd8") or data.startswith(b"\x89PNG\r\n\x1a\n")):
            raise SystemExit(f"Bad/unsupported image signature: {path.name}")

    source_manifest = json.loads((ROOT / "references/source-manifest.json").read_text(encoding="utf-8"))
    if source_manifest.get("product_knowledge", {}).get("sku_count") != 571:
        raise SystemExit("Source manifest product count does not match 571")
    source_checks = [
        ("references/product/Y仓全部SKU产品资料与促销总表_20260808.xlsx", source_manifest["product_knowledge"]["sha256"], "xl/workbook.xml"),
        ("references/operations/Tiktok从入门到精通.docx", source_manifest["operations_knowledge"]["sha256"], "word/document.xml"),
    ]
    for relative, expected, required_part in source_checks:
        path = ROOT / relative
        if sha256(path) != expected.upper():
            raise SystemExit(f"Source hash mismatch: {relative}")
        with zipfile.ZipFile(path) as archive:
            if required_part not in archive.namelist():
                raise SystemExit(f"Missing required OOXML part {required_part} in {relative}")

    qinfeiyan = [row for row in records if row["sku"] == "Qinfeiyan Shampoo"]
    if len(qinfeiyan) != 1:
        raise SystemExit("Qinfeiyan exact-match regression failed")
    q = qinfeiyan[0]
    if q.get("ingredients") is not None or q.get("usage") is not None:
        raise SystemExit("Qinfeiyan missing-field normalization failed")
    if q.get("listing_original_price_idr") != 96760 or q.get("daily_price_idr") != 48380 or q.get("activity_price_idr") != 45380:
        raise SystemExit("Qinfeiyan price regression failed")
    if "hair_growth_or_loss" not in q.get("claim_risk_tags", []):
        raise SystemExit("Qinfeiyan claim-risk regression failed")

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", skill_text):
        if not (ROOT / target).exists():
            raise SystemExit(f"Broken SKILL.md link: {target}")

    summary = json.loads((ROOT / "references/product/product_catalog_summary.json").read_text(encoding="utf-8"))
    if summary.get("record_count") != 571:
        raise SystemExit("Product summary count does not match 571")

    print("Portable bundle validation passed")
    print(f"SKUs: {len(records)}")
    print(f"Thumbnails: {len(thumbnails)}")
    print(f"Required files: {len(REQUIRED)}")


if __name__ == "__main__":
    main()
