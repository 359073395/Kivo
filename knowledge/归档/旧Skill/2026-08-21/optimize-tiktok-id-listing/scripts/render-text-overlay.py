#!/usr/bin/env python3
"""Render exact text overlays onto an accepted product-image base using Pillow."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - environment dependent
    raise SystemExit("Pillow is required. Install it with: python -m pip install pillow") from exc


FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]


def find_font(requested: str | None) -> Path:
    if requested:
        path = Path(os.path.expandvars(os.path.expanduser(requested)))
        if path.exists():
            return path
        raise FileNotFoundError(f"Font not found: {path}")
    for path in FONT_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No supported font found; pass an existing font path in the overlay spec")


def rgba(value: str | None, default: str) -> tuple[int, int, int, int]:
    return ImageColor.getcolor(value or default, "RGBA")


def resolve_box(box: list[float | int], width: int, height: int) -> tuple[int, int, int, int]:
    if len(box) != 4:
        raise ValueError("Each overlay box must contain [x, y, width, height]")
    if all(0 <= float(item) <= 1 for item in box):
        x, y, w, h = box
        return round(float(x) * width), round(float(y) * height), round(float(w) * width), round(float(h) * height)
    x, y, w, h = (round(float(item)) for item in box)
    return x, y, w, h


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke_width: int) -> int:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    return bbox[2] - bbox[0]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    stroke_width: int,
) -> str:
    wrapped_lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        words = paragraph.split()
        if not words:
            wrapped_lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if text_width(draw, candidate, font, stroke_width) <= max_width:
                current = candidate
            else:
                wrapped_lines.append(current)
                current = word
        wrapped_lines.append(current)
    return "\n".join(wrapped_lines)


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    start_size: int,
    min_size: int,
    max_width: int,
    max_height: int,
    spacing: int,
    stroke_width: int,
) -> tuple[ImageFont.FreeTypeFont, str, tuple[int, int, int, int]]:
    for size in range(start_size, min_size - 1, -1):
        font = ImageFont.truetype(str(font_path), size=size)
        wrapped = wrap_text(draw, text, font, max_width, stroke_width)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=spacing, stroke_width=stroke_width, align="left")
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font, wrapped, bbox
    raise ValueError("Text does not fit the requested box at the minimum font size")


def render(base: Image.Image, spec: dict[str, Any]) -> Image.Image:
    canvas = base.convert("RGBA")
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas, "RGBA")
    overlays = spec.get("overlays", [])
    if not isinstance(overlays, list) or not overlays:
        raise ValueError("Spec must contain a non-empty overlays list")

    for index, overlay in enumerate(overlays, start=1):
        if not isinstance(overlay, dict):
            raise ValueError(f"Overlay {index} must be an object")
        text = str(overlay.get("text", ""))
        if not text:
            raise ValueError(f"Overlay {index} has no text")
        x, y, box_w, box_h = resolve_box(overlay.get("box", []), width, height)
        if box_w <= 0 or box_h <= 0 or x < 0 or y < 0 or x + box_w > width or y + box_h > height:
            raise ValueError(f"Overlay {index} box is outside the image")

        padding = int(overlay.get("padding", 12))
        radius = int(overlay.get("radius", 0))
        background = overlay.get("background")
        if background:
            draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=radius, fill=rgba(background, "#00000000"))

        inner_w = box_w - 2 * padding
        inner_h = box_h - 2 * padding
        if inner_w <= 0 or inner_h <= 0:
            raise ValueError(f"Overlay {index} padding leaves no text area")

        font_path = find_font(overlay.get("font"))
        font_size = int(overlay.get("font_size", max(24, round(height * 0.06))))
        min_font_size = int(overlay.get("min_font_size", 16))
        spacing = int(overlay.get("spacing", max(4, round(font_size * 0.2))))
        stroke_width = int(overlay.get("stroke_width", 0))
        font, wrapped, bbox = fit_text(
            draw,
            text,
            font_path,
            font_size,
            min_font_size,
            inner_w,
            inner_h,
            spacing,
            stroke_width,
        )

        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        align = overlay.get("align", "left")
        valign = overlay.get("valign", "top")
        if align == "center":
            tx = x + padding + (inner_w - text_w) / 2
        elif align == "right":
            tx = x + padding + inner_w - text_w
        else:
            tx = x + padding
            align = "left"
        if valign == "middle":
            ty = y + padding + (inner_h - text_h) / 2 - bbox[1]
        elif valign == "bottom":
            ty = y + padding + inner_h - text_h - bbox[1]
        else:
            ty = y + padding - bbox[1]

        draw.multiline_text(
            (tx, ty),
            wrapped,
            font=font,
            fill=rgba(overlay.get("fill"), "#FFFFFFFF"),
            spacing=spacing,
            align=align,
            stroke_width=stroke_width,
            stroke_fill=rgba(overlay.get("stroke_fill"), "#000000FF"),
        )
    return canvas


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "overlay.png"
        base = Image.new("RGB", (400, 400), "#2456A6")
        spec = {
            "overlays": [
                {
                    "text": "Ringan dan Mudah Dibawa",
                    "box": [0.08, 0.65, 0.84, 0.25],
                    "font_size": 42,
                    "min_font_size": 18,
                    "fill": "#FFFFFFFF",
                    "background": "#00000099",
                    "align": "center",
                    "valign": "middle",
                    "padding": 16,
                    "radius": 12,
                }
            ]
        }
        render(base, spec).save(output)
        assert output.exists()
        assert Image.open(output).size == (400, 400)
    print("render-text-overlay self-test: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Base image")
    parser.add_argument("--spec", type=Path, help="JSON overlay specification")
    parser.add_argument("--out", type=Path, help="Output PNG or WebP")
    parser.add_argument("--force", action="store_true", help="Allow replacing an existing output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.input or not args.spec or not args.out:
        parser.error("--input, --spec, and --out are required unless --self-test is used")
    if args.out.exists() and not args.force:
        raise SystemExit(f"Output exists: {args.out}. Use --force only when replacement is intended.")

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise SystemExit("Overlay spec must be a JSON object")
    with Image.open(args.input) as base:
        result = render(base, spec)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.out)


if __name__ == "__main__":
    main()
