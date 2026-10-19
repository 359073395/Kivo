#!/usr/bin/env python3
"""Normalize Indonesian TikTok Shop listing evidence into a stable JSON shape."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


PRODUCT_ALIASES = {
    "sku": ("sku", "seller_sku", "product_sku", "id", "product_id"),
    "name": ("name", "product_name", "item_name"),
    "brand": ("brand", "brand_name"),
    "category": ("category", "category_name", "category_path"),
    "title": ("title", "product_title", "listing_title"),
    "description": ("description", "product_description", "listing_description"),
    "currency": ("currency", "currency_code"),
    "price": ("price", "sale_price", "current_price"),
    "list_price": ("list_price", "original_price", "compare_at_price"),
    "promotion": ("promotion", "promo", "discount", "offer"),
    "package_contents": ("package_contents", "whats_in_box", "included_items"),
    "attributes": ("attributes", "specifications", "specs"),
    "variants": ("variants", "skus", "options"),
    "images": ("images", "image_urls", "product_images"),
    "video": ("video", "product_video", "video_url"),
}

PERFORMANCE_ALIASES = {
    "impressions": ("impressions", "exposure", "views"),
    "clicks": ("clicks", "product_clicks"),
    "ctr": ("ctr", "click_through_rate"),
    "product_page_visits": ("product_page_visits", "pdp_visits", "detail_page_views"),
    "orders": ("orders", "paid_orders"),
    "conversion_rate": ("conversion_rate", "cvr"),
    "gmv": ("gmv", "revenue", "sales_amount"),
    "refund_rate": ("refund_rate", "return_rate"),
}


def alias_candidates(containers: Iterable[dict[str, Any]], aliases: Iterable[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for container_index, container in enumerate(containers):
        for alias in aliases:
            if alias in container and container[alias] not in (None, ""):
                candidates.append({"container": container_index, "alias": alias, "value": container[alias]})
    return candidates


def unique_candidate_values(candidates: list[dict[str, Any]]) -> int:
    serialized = {json.dumps(item["value"], ensure_ascii=False, sort_keys=True, default=str) for item in candidates}
    return len(serialized)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def normalize(raw: dict[str, Any], source_label: str = "input") -> dict[str, Any]:
    product_raw = as_dict(raw.get("product"))
    containers = (product_raw, raw)
    product: dict[str, Any] = {}
    detected_conflicts: list[dict[str, Any]] = []

    for field, aliases in PRODUCT_ALIASES.items():
        candidates = alias_candidates(containers, aliases)
        if field in {"price", "list_price"}:
            candidates = [item for item in candidates if not isinstance(item["value"], dict)]
        product[field] = candidates[0]["value"] if candidates else None
        if unique_candidate_values(candidates) > 1:
            detected_conflicts.append({"field": f"product.{field}", "candidates": candidates})

    if isinstance(product["price"], dict):
        product["price"] = None
    if isinstance(product["list_price"], dict):
        product["list_price"] = None

    product["attributes"] = as_dict(product["attributes"])
    product["variants"] = as_list(product["variants"])
    product["package_contents"] = as_list(product["package_contents"])
    product["images"] = as_list(product["images"])

    price_raw = as_dict(raw.get("price"))
    currency_value = product.pop("currency", None)
    current_value = product.pop("price", None)
    list_value = product.pop("list_price", None)
    promotion_value = product.pop("promotion", None)
    price = {
        "currency": currency_value or price_raw.get("currency") or "IDR",
        "current": current_value if current_value is not None else price_raw.get("current"),
        "list": list_value if list_value is not None else price_raw.get("list"),
        "promotion": promotion_value if promotion_value is not None else price_raw.get("promotion"),
    }

    performance_raw = as_dict(raw.get("performance"))
    performance = {}
    for field, aliases in PERFORMANCE_ALIASES.items():
        candidates = alias_candidates((performance_raw, raw), aliases)
        performance[field] = candidates[0]["value"] if candidates else None
        if unique_candidate_values(candidates) > 1:
            detected_conflicts.append({"field": f"performance.{field}", "candidates": candidates})

    sources = as_list(raw.get("sources"))
    if not sources:
        sources = [{"type": "input_json", "label": source_label}]

    provenance = as_dict(raw.get("field_provenance"))
    for field, value in product.items():
        if value not in (None, "", [], {}) and f"product.{field}" not in provenance:
            provenance[f"product.{field}"] = [{"source": source_label, "verified": False}]
    for field, value in price.items():
        if value not in (None, "") and f"price.{field}" not in provenance:
            provenance[f"price.{field}"] = [{"source": source_label, "verified": False}]
    for field, value in performance.items():
        if value not in (None, "") and f"performance.{field}" not in provenance:
            provenance[f"performance.{field}"] = [{"source": source_label, "verified": False}]

    recognized = {"product", "price", "performance", "sources", "field_provenance", "conflicts", "ads", "market"}
    for aliases in PRODUCT_ALIASES.values():
        recognized.update(aliases)
    for aliases in PERFORMANCE_ALIASES.values():
        recognized.update(aliases)
    unmapped = {key: value for key, value in raw.items() if key not in recognized}

    return {
        "schema_version": "1.0",
        "market": raw.get("market") or "ID",
        "product": product,
        "price": price,
        "ads": as_list(raw.get("ads")),
        "performance": performance,
        "sources": sources,
        "field_provenance": provenance,
        "conflicts": as_list(raw.get("conflicts")) + detected_conflicts,
        "unmapped": unmapped,
    }


def self_test() -> None:
    raw = {
        "seller_sku": "SKU-1",
        "product_name": "Botol Minum",
        "listing_title": "Botol Minum 1L",
        "sale_price": 99000,
        "currency_code": "IDR",
        "specs": {"capacity": "1L"},
        "image_urls": ["a.jpg"],
        "cvr": 0.031,
    }
    result = normalize(raw, "self-test")
    assert result["market"] == "ID"
    assert result["product"]["sku"] == "SKU-1"
    assert result["product"]["attributes"]["capacity"] == "1L"
    assert result["price"]["current"] == 99000
    assert result["performance"]["conversion_rate"] == 0.031
    assert result["product"]["images"] == ["a.jpg"]

    nested = normalize(
        {
            "product": {"title": "Title A"},
            "listing_title": "Title B",
            "price": {"currency": "IDR", "current": 50000},
        },
        "self-test",
    )
    assert nested["price"]["current"] == 50000
    assert any(item["field"] == "product.title" for item in nested["conflicts"])
    print("normalize-product-data self-test: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Raw JSON input")
    parser.add_argument("--out", type=Path, help="Normalized JSON output")
    parser.add_argument("--source-label", help="Fallback provenance label")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.input or not args.out:
        parser.error("--input and --out are required unless --self-test is used")

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit("Input JSON must be an object")
    inferred_label = args.input.name
    raw_sources = as_list(raw.get("sources"))
    if raw_sources and isinstance(raw_sources[0], dict) and raw_sources[0].get("label"):
        inferred_label = str(raw_sources[0]["label"])
    result = normalize(raw, args.source_label or inferred_label)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
