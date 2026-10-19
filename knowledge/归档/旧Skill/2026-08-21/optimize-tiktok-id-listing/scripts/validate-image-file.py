#!/usr/bin/env python3
"""Validate technical properties of a generated or edited listing image."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment dependent
    raise SystemExit("Pillow is required. Install it with: python -m pip install pillow") from exc


def validate(
    path: Path,
    min_width: int | None = None,
    min_height: int | None = None,
    aspect: float | None = None,
    aspect_tolerance: float = 0.02,
    max_megabytes: float | None = None,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return {"path": str(path), "valid": False, "errors": ["file_not_found"], "warnings": []}

    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            mode = image.mode
            image_format = image.format
            has_alpha = "A" in image.getbands()
    except Exception as exc:
        return {"path": str(path), "valid": False, "errors": [f"unreadable_image: {exc}"], "warnings": []}

    if width <= 0 or height <= 0:
        errors.append("invalid_dimensions")
    if min_width is not None and width < min_width:
        errors.append(f"width_below_minimum:{width}<{min_width}")
    if min_height is not None and height < min_height:
        errors.append(f"height_below_minimum:{height}<{min_height}")
    actual_aspect = width / height
    if aspect is not None and abs(actual_aspect - aspect) > aspect_tolerance:
        errors.append(f"aspect_out_of_tolerance:{actual_aspect:.4f}")

    size_bytes = path.stat().st_size
    size_megabytes = size_bytes / (1024 * 1024)
    if max_megabytes is not None and size_megabytes > max_megabytes:
        errors.append(f"file_too_large:{size_megabytes:.2f}MB")
    if mode not in {"RGB", "RGBA"}:
        warnings.append(f"unusual_color_mode:{mode}")
    if image_format not in {"PNG", "JPEG", "WEBP"}:
        warnings.append(f"unusual_format:{image_format}")

    return {
        "path": str(path.resolve()),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "width": width,
        "height": height,
        "aspect_ratio": round(actual_aspect, 6),
        "mode": mode,
        "format": image_format,
        "has_alpha": has_alpha,
        "bytes": size_bytes,
        "megabytes": round(size_megabytes, 4),
        "visual_review_required": True,
        "visual_review_scope": [
            "product_shape_and_structure",
            "packaging_color_logo_and_labels",
            "model_specs_and_accessory_count",
            "indonesian_text_accuracy",
            "claim_and_offer_accuracy",
            "linked_diagnostic_issue_resolved",
        ],
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.png"
        Image.new("RGB", (100, 100), "white").save(path)
        ok = validate(path, min_width=100, min_height=100, aspect=1.0)
        assert ok["valid"]
        failed = validate(path, min_width=200)
        assert not failed["valid"]
    print("validate-image-file self-test: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path)
    parser.add_argument("--min-width", type=int)
    parser.add_argument("--min-height", type=int)
    parser.add_argument("--aspect", type=float, help="Expected width/height ratio")
    parser.add_argument("--aspect-tolerance", type=float, default=0.02)
    parser.add_argument("--max-megabytes", type=float)
    parser.add_argument("--out", type=Path, help="Optional JSON output file")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.image:
        parser.error("image is required unless --self-test is used")

    result = validate(
        args.image,
        min_width=args.min_width,
        min_height=args.min_height,
        aspect=args.aspect,
        aspect_tolerance=args.aspect_tolerance,
        max_megabytes=args.max_megabytes,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
