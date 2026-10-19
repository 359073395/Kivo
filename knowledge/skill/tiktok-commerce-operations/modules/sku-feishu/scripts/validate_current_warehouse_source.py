#!/usr/bin/env python3
"""Validate the configured warehouse source and stale-price gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_inside(root: Path, relative: str, label: str, errors: list[str]) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute():
        errors.append(f"{label} must be relative")
        return None
    resolved = (root / candidate).resolve()
    try:
        common = Path(os.path.commonpath([str(root.resolve()), str(resolved)]))
    except ValueError:
        errors.append(f"{label} is outside configured root")
        return None
    if common != root.resolve():
        errors.append(f"{label} is outside configured root")
        return None
    return resolved


def resolve_reference(
    base: Path, vault_root: Path, relative: str, label: str, errors: list[str]
) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute():
        errors.append(f"{label} must be relative")
        return None
    resolved = (base / candidate).resolve()
    try:
        common = Path(os.path.commonpath([str(vault_root.resolve()), str(resolved)]))
    except ValueError:
        errors.append(f"{label} is outside the knowledge vault")
        return None
    if common != vault_root.resolve():
        errors.append(f"{label} is outside the knowledge vault")
        return None
    return resolved


def validate(vault_root: Path, mode: str) -> tuple[dict[str, Any], int]:
    pointer_path = (
        vault_root
        / "skill"
        / "tiktok-commerce-operations"
        / "references"
        / "current-warehouse-source.json"
    )
    config_path = vault_root / "辅助" / "配置" / "machine-paths.local.json"
    errors: list[str] = []

    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8-sig"))
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "passed": False,
            "allowed": False,
            "mode": mode,
            "nextAction": "stop_invalid_current_source",
            "errors": [str(exc)],
        }
        return result, 1

    root_field = str(pointer.get("configuredRoot", ""))
    configured_value = str(config.get(root_field, "")) if root_field else ""
    if not root_field or not configured_value:
        errors.append("configured source root is missing")
        source_path = None
    else:
        source_root = Path(configured_value).resolve()
        source_path = resolve_inside(
            source_root, str(pointer.get("relativePath", "")), "relativePath", errors
        )

    expected_sha = str(pointer.get("sha256", "")).lower()
    actual_sha = None
    if source_path is not None:
        if not source_path.is_file():
            errors.append("current source workbook is missing")
        elif len(expected_sha) != 64:
            errors.append("current source SHA-256 is invalid")
        else:
            actual_sha = sha256_file(source_path)
            if actual_sha != expected_sha:
                errors.append("current source SHA-256 mismatch")

    for key in ("sourceCard", "knowledgeAsset"):
        target = resolve_reference(
            pointer_path.parent,
            vault_root,
            str(pointer.get(key, "")),
            key,
            errors,
        )
        if target is not None and not target.is_file():
            errors.append(f"{key} is missing")

    base_result: dict[str, Any] = {
        "passed": not errors,
        "allowed": False,
        "mode": mode,
        "sourceDate": pointer.get("sourceDate"),
        "sourcePath": str(source_path) if source_path is not None else None,
        "sourceHashVerified": bool(actual_sha and actual_sha == expected_sha),
        "derivedStatus": pointer.get("derivedUnifiedPrices", {}).get("status"),
        "errors": errors,
    }
    if errors:
        base_result["nextAction"] = "stop_invalid_current_source"
        return base_result, 1

    if mode == "source-read":
        base_result.update(allowed=True, nextAction="read_current_source")
        return base_result, 0

    if mode == "derive-prices":
        base_result.update(allowed=True, nextAction="rebuild_unified_prices")
        return base_result, 0

    derived = pointer.get("derivedUnifiedPrices", {})
    if derived.get("status") != "current_for_source":
        base_result.update(
            allowed=False,
            nextAction="stop_stale_unified_price_rebuild_required",
        )
        return base_result, 2

    derived_path = resolve_inside(
        Path(configured_value).resolve(),
        str(derived.get("relativePath", "")),
        "derivedUnifiedPrices.relativePath",
        errors,
    )
    if derived.get("sourceSha256") != expected_sha:
        errors.append("derived prices do not reference the current source hash")
    pricing_rule_id = pointer.get("pricingRule", {}).get("id")
    if pricing_rule_id and derived.get("pricingRule") != pricing_rule_id:
        errors.append("derived prices do not reference the current pricing rule")
    price2_hash = derived.get("price2Sha256")
    if price2_hash:
        price2_path = resolve_inside(
            Path(configured_value).resolve(),
            str(pointer.get("price2", {}).get("relativePath", "")),
            "price2.relativePath", errors,
        )
        if price2_path is None or not price2_path.is_file():
            errors.append("Y warehouse source workbook is missing")
        elif sha256_file(price2_path) != price2_hash:
            errors.append("Y warehouse source hash differs from derived prices")
    if derived_path is None or not derived_path.is_file():
        errors.append("derived unified price workbook is missing")
    expected_derived_sha = str(derived.get("sha256", "")).lower()
    if derived_path is not None and derived_path.is_file():
        if len(expected_derived_sha) != 64:
            errors.append("derived unified price SHA-256 is invalid")
        elif sha256_file(derived_path) != expected_derived_sha:
            errors.append("derived unified price SHA-256 mismatch")

    base_result["errors"] = errors
    base_result["passed"] = not errors
    base_result["allowed"] = not errors
    base_result["nextAction"] = (
        "write_flash_from_current_unified_prices"
        if not errors
        else "stop_invalid_current_unified_prices"
    )
    return base_result, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", type=Path)
    parser.add_argument(
        "--mode",
        choices=("source-read", "derive-prices", "flash-write"),
        default="source-read",
    )
    args = parser.parse_args()
    vault_root = args.vault_root or Path(__file__).resolve().parents[5]
    result, exit_code = validate(vault_root.resolve(), args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
